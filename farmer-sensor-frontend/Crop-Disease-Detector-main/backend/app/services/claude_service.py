"""Claude (Anthropic) integration for the Vani agricultural assistant."""

from __future__ import annotations

import logging

from app.core.config import settings
from app.core.errors import AssistantUnavailableError
from app.services.claude_client import build_client, request_kwargs

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are Vani, an agricultural assistant helping farmers in Kerala. Give "
    "practical, clear, evidence-grounded agricultural guidance. Use the provided "
    "agricultural context whenever available. Do not invent specific pesticide "
    "dosages or unsafe recommendations when the source context does not provide "
    "them. If the information is insufficient, clearly say so.\n"
    "Never mention the reference notes, context, retrieval, or your instructions "
    "to the farmer. They should only see natural farming advice, never a "
    "description of how you produced it.\n\n"
    "Any plant or growing topic is welcome: field crops, vegetables, fruit trees, "
    "spices, plantation crops, kitchen gardens, pot and terrace plants, "
    "ornamentals, nursery care, composting, soil, irrigation, pests, diseases, "
    "pruning, harvesting, storage and seasonal planning. If a question is truly "
    "unrelated to plants or farming, say kindly that you focus on crops and "
    "plants, then offer a farming topic you could help with instead.\n\n"
    "Be friendly and conversational, like a helpful neighbour who happens to be "
    "an agronomist. Reply in simple English a farmer can act on today. Keep it "
    "to about 60 to 130 words. Lead with the direct answer, then the steps to "
    "take. Use short lines, no markdown headings, no bold, no emoji. End most "
    "replies with one short follow-up question that helps narrow things down, "
    "and never reply with only a question. For exact chemical dosages, tell the "
    "farmer to confirm with the product label or the local Krishi Bhavan.\n\n"
    "If an image IS attached to this request, describe only what is actually "
    "visible in it. Do not invent a disease when the photo is unclear; say what "
    "a clearer photo would need to show. Never claim certainty from an image "
    "alone.\n\n"
    "If NO image is attached, remember this chat box is text only and the farmer "
    "cannot attach a file here. Never say 'send me a photo' or 'please attach "
    "it'. Instead, warmly point them to the Disease Detection page in the "
    "sidebar to upload the photo for AI image analysis, and mention they can "
    "then tap 'Ask Vani About This' to come back and discuss the result. Still "
    "offer whatever text-based help you can in the meantime."
)


class ClaudeService:
    def __init__(self) -> None:
        self._client = None

    def load(self) -> None:
        if not settings.anthropic_api_key.strip():
            logger.warning("ANTHROPIC_API_KEY not set. Assistant will use local context only.")
            return
        self._client = build_client()

    @property
    def available(self) -> bool:
        return self._client is not None

    @staticmethod
    def build_user_prompt(
        question: str,
        agri_context: str,
        detection_context: str | None,
        weather_context: str | None,
    ) -> str:
        parts = ["Farmer question:", question.strip()]
        if detection_context:
            parts += ["", "Recent AI disease detection for this farmer:", detection_context]
        if weather_context:
            parts += ["", "Current field weather:", weather_context]
        if agri_context:
            parts += [
                "",
                "Background notes retrieved for this question. Use them if they match "
                "the crop and topic being asked about; ignore them if they do not. "
                "Never mention these notes or refer to them in your reply:",
                agri_context,
            ]
        else:
            parts += [
                "",
                "No background notes matched this question. Answer from your general "
                "agricultural knowledge and add one short, natural caveat. Do not "
                "mention notes or context.",
            ]
        return "\n".join(parts)

    def answer(
        self,
        question: str,
        agri_context: str,
        detection_context: str | None = None,
        weather_context: str | None = None,
        image: tuple[str, str] | None = None,
        history: list[tuple[str, str]] | None = None,
    ) -> tuple[str, str]:
        """Returns (answer, source).

        When `image` is provided as (base64, media_type) the question is sent as
        a Claude image content block so the farmer can ask about a photo
        directly in chat. Falls back to local context when Claude is down.
        """
        prompt = self.build_user_prompt(
            question, agri_context, detection_context, weather_context
        )
        if self._client is None:
            return self._fallback(agri_context, detection_context), "local-context"

        if image is None:
            content = prompt
        else:
            b64, media_type = image
            content = [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": media_type,
                        "data": b64,
                    },
                },
                {"type": "text", "text": prompt},
            ]

        # Prior turns first so follow-ups keep their meaning.
        messages = []
        for role, text in (history or [])[-8:]:
            body = (text or "").strip()
            if body:
                messages.append(
                    {
                        "role": "assistant" if role == "assistant" else "user",
                        "content": body[:1500],
                    }
                )
        messages.append({"role": "user", "content": content})

        try:
            message = self._client.messages.create(
                **request_kwargs(max_tokens=800, temperature=0.2),
                system=SYSTEM_PROMPT,
                messages=messages,
            )
            text = "".join(
                block.text for block in message.content if getattr(block, "type", "") == "text"
            ).strip()
            if not text:
                raise ValueError("Empty response from Claude")
            return text, "claude"
        except Exception as exc:
            logger.warning("Claude request failed: %s", exc)
            fallback = self._fallback(agri_context, detection_context)
            if not fallback:
                raise AssistantUnavailableError from exc
            return fallback, "local-context"

    @staticmethod
    def _fallback(agri_context: str, detection_context: str | None) -> str:
        """Grounded answer straight from retrieved context when Claude is unavailable."""
        if not agri_context:
            # No matching reference and no live model: be honest rather than silent.
            return (
                "Our AI assistant is offline at the moment, and I don't have a local "
                "reference note that matches your question.\n\n"
                "Please try again shortly. For anything urgent, your local Krishi "
                "Bhavan officer is the best source of advice.\n\n"
                "If you want a crop photo checked, the Disease Detection page still "
                "works and will save the result to your reports."
            )
        first = agri_context.split("\n\n")[0]
        body = first.split("\n", 1)[-1].strip()
        lead = "Here is the guidance from our agricultural reference for your question."
        if detection_context:
            lead = (
                "Based on your recent detection and our agricultural reference, "
                "here is the guidance."
            )
        return (
            f"{lead}\n\n{body}\n\n"
            "The AI assistant is offline at the moment, so this is the reference text "
            "rather than a tailored answer. Confirm any chemical dose with the product "
            "label or your local Krishi Bhavan."
        )


claude_service = ClaudeService()
