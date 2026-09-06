"""Crop disease analysis using Claude's native vision capability.

The API key never leaves the backend: React uploads an image to FastAPI, FastAPI
base64-encodes it and calls the Anthropic Messages API, then returns structured
JSON to React.
"""

from __future__ import annotations

import base64
import io
import json
import logging
import re

from PIL import Image, UnidentifiedImageError

from app.core.config import settings
from app.core.errors import (
    DetectionFailedError,
    ImageTooLargeError,
    InvalidImageError,
    VisionUnavailableError,
)
from app.schemas.detection import SEVERITIES, VisionAnalysis
from app.services.claude_client import build_client, request_kwargs

logger = logging.getLogger(__name__)

# Claude accepts these image media types.
SUPPORTED_MEDIA = {
    "JPEG": "image/jpeg",
    "PNG": "image/png",
    "WEBP": "image/webp",
}

SYSTEM_PROMPT = (
    "You are Vani, an agricultural crop disease assistant helping farmers in "
    "Kerala, India. Analyze the uploaded crop image carefully. Your task is to "
    "identify visible signs of crop disease.\n\n"
    "Return ONLY valid JSON using this exact structure, with no markdown fences "
    "and no commentary:\n"
    "{\n"
    '  "crop": "string",\n'
    '  "disease": "string",\n'
    '  "confidence": 0,\n'
    '  "severity": "Healthy | Mild | Moderate | Severe | Unknown",\n'
    '  "symptoms": ["string"],\n'
    '  "treatment": ["string"],\n'
    '  "prevention": ["string"],\n'
    '  "explanation": "string",\n'
    '  "needs_expert_confirmation": true\n'
    "}\n\n"
    "Rules:\n"
    "- Do not invent a disease when the image is unclear.\n"
    '- If the image is insufficient for diagnosis, set "disease" to "Unable to '
    'determine" and explain why in "explanation".\n'
    "- If the image does not show a plant or crop at all, say so plainly in the "
    'explanation and use "Unable to determine".\n'
    "- Confidence must be a number between 0 and 1. Treat it as an AI estimate, "
    "not a scientifically validated probability.\n"
    '- "crop" must be ONLY the common crop name, at most three words (for '
    'example "Rice", "Coconut", "Apple"). Put any reasoning or botanical '
    'names in "explanation", never in "crop". Use "Unknown" if unsure.\n'
    '- "disease" must be a short condition name, at most six words. Put '
    "alternatives and caveats in the explanation.\n"
    "- Describe visible symptoms you can actually see in the image.\n"
    "- Give practical treatment guidance a smallholder farmer can act on.\n"
    "- Do not invent pesticide dosages. Do not recommend unsafe chemical use. "
    "For exact doses, tell the farmer to confirm with the product label or the "
    "local Krishi Bhavan.\n"
    "- If specific treatment information is unavailable, say so.\n"
    "- If multiple diseases are plausible, name the most likely one and explain "
    "the alternatives in the explanation.\n"
    "- Always set needs_expert_confirmation appropriately.\n"
    "- Never claim certainty from an image alone.\n"
    "- Keep each list item short and plain: one practical action per item."
)

USER_PROMPT = (
    "Analyze this crop photo and return the JSON described in your instructions."
)


def _clamp_confidence(value) -> float:
    try:
        conf = float(value)
    except (TypeError, ValueError):
        return 0.0
    if conf > 1:  # a model may answer 94 instead of 0.94
        conf = conf / 100
    return max(0.0, min(1.0, round(conf, 4)))


def _short_label(value, fallback: str, max_words: int, max_chars: int) -> str:
    """Keep crop/disease names short enough for the result card.

    The model occasionally answers with reasoning ("Apple - likely, based on
    leaf venation"). Anything after a dash, comma, bracket or colon is dropped;
    the full reasoning stays available in `explanation`.
    """
    text = str(value or "").strip()
    if not text:
        return fallback
    text = re.split(r"\s*[\(\[:;]|\s+[-\u2013\u2014]\s+|,", text, maxsplit=1)[0].strip()
    text = text.strip(" .-")
    if not text:
        return fallback
    words = text.split()
    if len(words) > max_words:
        text = " ".join(words[:max_words])
    if len(text) > max_chars:
        text = text[:max_chars].rstrip(" .-")
    return text or fallback


def _as_list(value) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value.strip()] if value.strip() else []
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    return []


def _extract_json(text: str) -> dict:
    """Parse the model's reply, tolerating markdown fences or stray prose."""
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
    raise ValueError("Claude did not return parseable JSON")


class VisionService:
    """Claude Vision crop analysis. Client is created once at startup."""

    def __init__(self) -> None:
        self._client = None

    def load(self) -> None:
        if not settings.anthropic_api_key.strip():
            logger.warning(
                "ANTHROPIC_API_KEY not set. Image analysis will be unavailable."
            )
            return
        self._client = build_client()

    @property
    def available(self) -> bool:
        return self._client is not None

    def prepare_image(self, raw: bytes) -> tuple[str, str]:
        """Validate, downscale if needed, and base64-encode. Returns (b64, media_type)."""
        if not raw:
            raise InvalidImageError("The uploaded file was empty. Please try again.")
        if len(raw) > settings.max_upload_bytes:
            raise ImageTooLargeError

        try:
            image = Image.open(io.BytesIO(raw))
            image.verify()
            image = Image.open(io.BytesIO(raw))
            source_format = (image.format or "").upper()
        except (UnidentifiedImageError, OSError, ValueError) as exc:
            raise InvalidImageError from exc

        if source_format not in SUPPORTED_MEDIA:
            raise InvalidImageError(
                "Only JPEG, PNG and WebP photos are supported. Please upload one of these."
            )

        longest = max(image.size)
        needs_resize = longest > settings.vision_max_edge
        if not needs_resize and source_format in SUPPORTED_MEDIA:
            return base64.b64encode(raw).decode("ascii"), SUPPORTED_MEDIA[source_format]

        # Downscale large photos: keeps upload size and token cost sane.
        scale = settings.vision_max_edge / longest
        new_size = (max(1, int(image.width * scale)), max(1, int(image.height * scale)))
        resized = image.convert("RGB").resize(new_size, Image.LANCZOS)
        buf = io.BytesIO()
        resized.save(buf, "JPEG", quality=88, optimize=True)
        logger.info("Resized image from %s to %s for Claude.", image.size, new_size)
        return base64.b64encode(buf.getvalue()).decode("ascii"), "image/jpeg"

    @staticmethod
    def image_block(b64: str, media_type: str) -> dict:
        """Anthropic image content block."""
        return {
            "type": "image",
            "source": {"type": "base64", "media_type": media_type, "data": b64},
        }

    def analyze(self, raw: bytes) -> VisionAnalysis:
        """Send the crop photo to Claude and return structured analysis."""
        b64, media_type = self.prepare_image(raw)

        if self._client is None:
            raise VisionUnavailableError

        try:
            message = self._client.messages.create(
                **request_kwargs(max_tokens=1500, temperature=0.2),
                system=SYSTEM_PROMPT,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            self.image_block(b64, media_type),
                            {"type": "text", "text": USER_PROMPT},
                        ],
                    }
                ],
            )
            text = "".join(
                b.text for b in message.content if getattr(b, "type", "") == "text"
            )
        except Exception as exc:
            logger.warning("Claude Vision request failed: %s", exc)
            raise DetectionFailedError from exc

        try:
            payload = _extract_json(text)
        except ValueError as exc:
            logger.warning("Unparseable vision response: %s", text[:300])
            raise DetectionFailedError from exc

        severity = str(payload.get("severity", "Unknown")).strip().title()
        if severity not in SEVERITIES:
            severity = "Unknown"

        return VisionAnalysis(
            crop=_short_label(payload.get("crop"), "Unknown", max_words=3, max_chars=40),
            disease=_short_label(
                payload.get("disease"), "Unable to determine", max_words=6, max_chars=80
            ),
            confidence=_clamp_confidence(payload.get("confidence")),
            severity=severity,
            symptoms=_as_list(payload.get("symptoms")),
            treatment=_as_list(payload.get("treatment")),
            prevention=_as_list(payload.get("prevention")),
            explanation=str(payload.get("explanation") or "").strip(),
            needs_expert_confirmation=bool(
                payload.get("needs_expert_confirmation", True)
            ),
        )


vision_service = VisionService()
