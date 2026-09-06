"""Shared Anthropic client construction.

Supports two backends behind one interface:

* Standard Anthropic API  - ANTHROPIC_API_KEY only.
* Azure AI Foundry        - ANTHROPIC_API_KEY + ANTHROPIC_BASE_URL.

Foundry deployments reject some parameters that api.anthropic.com accepts
(``temperature`` is one), so request keyword arguments are built centrally here
rather than duplicated in each service.
"""

from __future__ import annotations

import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


def build_client():
    """Return an Anthropic client, or None when no key is configured."""
    key = settings.anthropic_api_key.strip()
    if not key:
        return None

    base_url = settings.anthropic_base_url.strip()
    try:
        if base_url:
            from anthropic import AnthropicFoundry

            client = AnthropicFoundry(api_key=key, base_url=base_url, timeout=90.0)
            logger.info(
                "Claude client ready via Azure AI Foundry (model=%s).",
                settings.model_name,
            )
            return client

        from anthropic import Anthropic

        client = Anthropic(api_key=key, timeout=90.0)
        logger.info("Claude client ready (model=%s).", settings.model_name)
        return client
    except Exception as exc:
        logger.warning("Could not initialise Claude client: %s", exc)
        return None


def request_kwargs(*, max_tokens: int, temperature: float | None = None) -> dict:
    """Build messages.create kwargs valid for the active backend."""
    kwargs: dict = {"model": settings.model_name, "max_tokens": max_tokens}
    # Foundry deployments raise TypeError on `temperature`; omit it there.
    if temperature is not None and not settings.use_foundry:
        kwargs["temperature"] = temperature
    return kwargs
