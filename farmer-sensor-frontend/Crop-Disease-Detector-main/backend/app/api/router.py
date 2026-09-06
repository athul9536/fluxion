from fastapi import APIRouter

from app.api import chat, detect, reports, weather
from app.core.config import settings
from app.services.assistant_service import assistant_service
from app.services.claude_service import claude_service
from app.services.vision_service import vision_service

api_router = APIRouter(prefix="/api")
api_router.include_router(detect.router, tags=["detection"])
api_router.include_router(chat.router, tags=["assistant"])
api_router.include_router(reports.router, tags=["reports"])
api_router.include_router(weather.router, tags=["weather"])


@api_router.get("/health", tags=["health"])
def health():
    prefer_assistant = (
        settings.assistant_provider.strip().lower() != "claude"
        and assistant_service.available
    )
    if prefer_assistant:
        assistant = "azure-openai"
    elif claude_service.available:
        assistant = "claude"
    else:
        assistant = "local-context"

    return {
        "status": "ok",
        "detector": "claude-vision" if vision_service.available else "unconfigured",
        "assistant": assistant,
        "assistant_model": (
            settings.assistant_model if prefer_assistant else settings.model_name
        ),
        "vision_model": settings.model_name,
    }
