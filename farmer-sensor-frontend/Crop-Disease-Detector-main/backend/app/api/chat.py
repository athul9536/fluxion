"""POST /api/chat - RAG + Claude agricultural assistant, with optional vision.

The backend decides which of three shapes a request is:
  1. text-only question
  2. image diagnosis (an image is attached)
  3. follow-up about an existing diagnosis (detection context attached)
"""

from __future__ import annotations

import base64
import binascii
import logging
import re

from fastapi import APIRouter

from app.core.config import settings
from app.core.errors import EmptyMessageError, InvalidImageError
from app.schemas.chat import ChatRequest, ChatResponse, DetectionContext
from app.services.assistant_service import assistant_service
from app.services.claude_service import claude_service
from app.services.rag_service import rag_service
from app.services.vision_service import vision_service
from app.services.weather_service import weather_service
from app.state import counters

logger = logging.getLogger(__name__)
router = APIRouter()

DATA_URL = re.compile(r"^data:(image/[a-z+]+);base64,", re.IGNORECASE)


def _decode_image(value: str) -> bytes:
    """Accept a data URL or bare base64 string."""
    payload = DATA_URL.sub("", value.strip())
    try:
        return base64.b64decode(payload, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise InvalidImageError(
            "We couldn't read that image. Please attach a JPEG, PNG or WebP photo."
        ) from exc


def _detection_context(detection: DetectionContext | None) -> str | None:
    if detection is None:
        return None
    lines: list[str] = []
    if detection.crop:
        lines.append(f"Crop: {detection.crop}")
    if detection.disease:
        lines.append(f"Detected disease: {detection.disease}")
    if detection.confidence is not None:
        lines.append(f"AI confidence estimate: {round(detection.confidence * 100)}%")
    if detection.severity:
        lines.append(f"Severity: {detection.severity}")
    if detection.symptoms:
        lines.append("Symptoms observed: " + "; ".join(detection.symptoms))
    if detection.treatment:
        lines.append("Treatment already shown to the farmer: " + "; ".join(detection.treatment))
    if detection.explanation:
        lines.append(f"Analysis notes: {detection.explanation}")
    return "\n".join(lines) or None


@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest):
    message = (payload.message or "").strip()
    if not message:
        raise EmptyMessageError

    ctx = payload.context
    detection = payload.detection_context or (ctx.detection if ctx else None)

    # Request type 2: an image is attached, so use Claude's vision path.
    image_parts = None
    if payload.image:
        raw = _decode_image(payload.image)
        image_parts = vision_service.prepare_image(raw)

    hints = []
    if detection:
        hints = [h for h in (detection.crop, detection.disease) if h]

    chunks = rag_service.retrieve(message, hints=hints)
    agri_context = rag_service.format_context(chunks)

    weather_context = None
    used_weather = False
    if ctx is None or ctx.include_weather:
        try:
            lat = ctx.latitude if ctx else None
            lon = ctx.longitude if ctx else None
            weather_context = weather_service.as_context(
                await weather_service.current(lat, lon)
            )
            used_weather = True
        except Exception as exc:  # weather is never allowed to break chat
            logger.warning("Skipping weather context: %s", exc)

    detection_text = _detection_context(detection)

    # The chat assistant answers text-only questions. An attached image always
    # goes to Claude, since the assistant is wired up here for text chat only.
    prefer_assistant = (
        image_parts is None
        and settings.assistant_provider.strip().lower() != "claude"
        and assistant_service.available
    )

    answer = None
    source = None
    if prefer_assistant:
        try:
            answer = await assistant_service.answer(
                question=message,
                agri_context=agri_context,
                detection_context=detection_text,
                weather_context=weather_context,
                history=[(t.role, t.text) for t in payload.history],
            )
            source = "azure-openai"
        except Exception as exc:
            logger.warning("Chat assistant failed, falling back to Claude: %s", exc)

    if answer is None:
        answer, source = claude_service.answer(
            question=message,
            agri_context=agri_context,
            detection_context=detection_text,
            weather_context=weather_context,
            image=image_parts,
            history=[(t.role, t.text) for t in payload.history],
        )
    counters.questions_asked += 1

    return ChatResponse(
        response=answer,
        sources=[f"{c.crop} - {c.title}" for c in chunks],
        used_weather=used_weather,
        used_image=image_parts is not None,
        model_source=source,
    )
