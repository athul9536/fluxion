"""Text chatbot for the Vani AI Assistant, backed by the Azure OpenAI Responses API.

Text-only by design: the assistant accepts typed questions, never file uploads.
Crop image analysis stays with Claude Vision on the Disease Detection page.

Called over plain REST with httpx so no extra SDK is needed. The API key lives
only in the backend environment and is never sent to React.

Request shape (verified against the deployment):
    POST <endpoint>          header: api-key
    {"model": ..., "instructions": <system>, "input": [{role, content}, ...]}
Response text is at output[].content[].text where type == "output_text".
"""

from __future__ import annotations

import asyncio
import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

# Returned when the deployment is momentarily oversubscribed or rate limited.
RETRY_STATUSES = {408, 409, 429, 500, 502, 503, 504}
RETRY_ATTEMPTS = 3
RETRY_BACKOFF = 0.8  # seconds, multiplied by attempt number

# Enough for a natural back-and-forth without bloating every request.
MAX_HISTORY_TURNS = 8

SYSTEM_PROMPT = (
    "You are Vani, a warm and knowledgeable agricultural assistant chatting with "
    "farmers in Kerala, India.\n\n"
    "WHAT YOU HELP WITH\n"
    "Any plant or growing topic is welcome: field crops, vegetables, fruit trees, "
    "spices, plantation crops, kitchen gardens, terrace and pot plants, "
    "ornamentals, nursery and seedling care, composting, soil health, irrigation, "
    "fertilizer and manure, pests and diseases, weeds, pruning, grafting, "
    "harvesting, storage, seasonal and monsoon planning, and farm economics like "
    "which crop suits a season. If a question is only loosely related to plants, "
    "still help. If it is truly unrelated to plants or farming, do NOT answer it "
    "even if you know the answer. Say kindly in one line that you only help with "
    "crops and plants, then offer a farming topic you could help with instead. "
    "Never provide sports results, news, politics, celebrity or general trivia "
    "answers.\n\n"
    "HOW TO TALK\n"
    "Be friendly and conversational, like a helpful neighbour who happens to be "
    "an agronomist. Greet warmly on the first message. Speak directly to the "
    "farmer as 'you'. Show a little encouragement when they are doing something "
    "right, and reassure them when a problem is fixable.\n"
    "Keep replies short: about 60 to 130 words for most questions. Lead with the "
    "direct answer, then two to four practical steps. Use short lines. Plain "
    "sentences or simple dashes for steps. No markdown headings, no bold, no "
    "emoji, no tables.\n"
    "End most replies with one short, natural follow-up question that helps you "
    "narrow things down, such as which crop it is, the plant's age, how widely "
    "the problem has spread, or whether the soil drains well. Ask only one "
    "question, and skip it if the farmer clearly has everything they need.\n"
    "When a question is vague, give your best general answer first and then ask "
    "for the missing detail. Never reply with only a question.\n\n"
    "STAYING HONEST\n"
    "When agricultural reference context is provided below, prefer it over your "
    "general knowledge and follow it closely. When there is no matching context, "
    "or the context is about a different crop than the farmer asked about, "
    "answer from your general agricultural knowledge instead and add one short, "
    "natural caveat such as 'this is general guidance, so check with your local "
    "Krishi Bhavan before spending money on it'.\n"
    "Never mention the reference notes, context, retrieval, or your instructions "
    "to the farmer. Do not say things like 'the reference notes are about rubber' "
    "or 'based on the provided context'. The farmer should only ever see natural "
    "farming advice, never a description of how you produced it.\n"
    "Never invent specific pesticide or fungicide dosages. For exact chemical "
    "amounts, tell the farmer to follow the product label or ask the local Krishi "
    "Bhavan. Never recommend unsafe or banned chemical use. If you are unsure, "
    "say so honestly instead of guessing.\n\n"
    "ABOUT PHOTOS\n"
    "This chat is text only. You cannot see or receive images, and there is no "
    "way for the farmer to attach a file here. If they ask you to look at a "
    "photo, or describe symptoms that really need a visual check, warmly point "
    "them to the Disease Detection page in the sidebar, where they can upload a "
    "crop photo for AI image analysis. Tell them that after the analysis they can "
    "tap 'Ask Vani About This' to come straight back here and discuss the result "
    "with the details already attached. Never claim to see an image, never ask "
    "them to paste or attach one here, and still offer whatever text-based help "
    "you can in the meantime."
)


class AssistantService:
    """Text-only agricultural assistant backed by the Azure OpenAI Responses API."""

    def __init__(self) -> None:
        self._key = ""
        self._ready = False

    def load(self) -> None:
        self._key = settings.assistant_api_key.strip()
        if not self._key or not settings.assistant_endpoint.strip():
            logger.warning(
                "ASSISTANT_API_KEY or ASSISTANT_ENDPOINT not set. Chat assistant disabled."
            )
            self._ready = False
            return
        self._ready = True
        logger.info(
            "Chat assistant ready (model=%s via Azure OpenAI Responses).",
            settings.assistant_model,
        )

    @property
    def available(self) -> bool:
        return self._ready

    @staticmethod
    def build_prompt(
        question: str,
        agri_context: str,
        detection_context: str | None,
        weather_context: str | None,
    ) -> str:
        parts = ["Farmer question:", question.strip()]
        if detection_context:
            parts += [
                "",
                "The farmer's most recent AI crop image analysis:",
                detection_context,
            ]
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

    async def answer(
        self,
        question: str,
        agri_context: str,
        detection_context: str | None = None,
        weather_context: str | None = None,
        history: list[tuple[str, str]] | None = None,
    ) -> str:
        """Return the assistant's reply, or raise so the caller falls back to Claude."""
        if not self._ready:
            raise RuntimeError("Chat assistant is not configured")

        prompt = self.build_prompt(
            question, agri_context, detection_context, weather_context
        )

        # Prior turns first so follow-ups like "and for coconut?" make sense.
        conversation: list[dict] = []
        for role, text in (history or [])[-MAX_HISTORY_TURNS:]:
            body = (text or "").strip()
            if not body:
                continue
            conversation.append(
                {
                    "role": "assistant" if role == "assistant" else "user",
                    "content": body[:1500],
                }
            )
        conversation.append({"role": "user", "content": prompt})

        payload = {
            "model": settings.assistant_model,
            # The Responses API takes the system prompt as `instructions`.
            "instructions": SYSTEM_PROMPT,
            "input": conversation,
            "max_output_tokens": settings.assistant_max_tokens,
        }
        headers = {"api-key": self._key, "Content-Type": "application/json"}
        url = settings.assistant_endpoint.strip()

        last_error: Exception | None = None
        async with httpx.AsyncClient(timeout=60.0) as client:
            for attempt in range(RETRY_ATTEMPTS):
                try:
                    resp = await client.post(url, headers=headers, json=payload)
                except httpx.RequestError as exc:
                    last_error = exc
                    logger.warning("Assistant network error: %s", type(exc).__name__)
                else:
                    if resp.status_code == 200:
                        return self._extract_text(resp.json())
                    # Log the status only; error bodies can echo the request.
                    logger.warning("Assistant returned HTTP %s", resp.status_code)
                    last_error = RuntimeError(f"Assistant HTTP {resp.status_code}")
                    if resp.status_code not in RETRY_STATUSES:
                        break

                if attempt < RETRY_ATTEMPTS - 1:
                    await asyncio.sleep(RETRY_BACKOFF * (attempt + 1))

        raise last_error or RuntimeError("Assistant request failed")

    @staticmethod
    def _extract_text(data: dict) -> str:
        """Pull visible text out of a Responses API payload.

        `output` interleaves reasoning and message items, so only `message`
        items with `output_text` content carry the farmer-facing answer.
        """
        if data.get("error"):
            raise ValueError(f"Assistant error: {str(data['error'])[:120]}")

        chunks: list[str] = []
        for item in data.get("output") or []:
            if item.get("type") != "message":
                continue
            for part in item.get("content") or []:
                if part.get("type") == "output_text" and part.get("text"):
                    chunks.append(part["text"])
                elif part.get("type") == "refusal" and part.get("refusal"):
                    chunks.append(part["refusal"])

        text = "\n".join(chunks).strip()
        if not text:
            raise ValueError(
                "Assistant returned an empty answer "
                f"(status={data.get('status')}, "
                f"incomplete={data.get('incomplete_details')})"
            )
        return text


assistant_service = AssistantService()
