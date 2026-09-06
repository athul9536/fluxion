from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """All runtime configuration comes from the environment / .env file."""

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Supabase Postgres connection string (Project Settings > Database).
    # Prefer the pooler host for IPv4-friendly connectivity.
    database_url: str = ""

    anthropic_api_key: str = ""
    # Single source of truth for the model name. All current Claude models
    # support vision, so one setting covers both chat and image analysis.
    anthropic_model: str = "claude-opus-5"
    # Legacy alias: earlier .env files used CLAUDE_MODEL.
    claude_model: str = ""

    # Set to an Azure AI Foundry endpoint to route through Foundry instead of
    # api.anthropic.com. Leave empty to use the standard Anthropic API.
    anthropic_base_url: str = ""

    # Longest edge sent to Claude. Large photos are downscaled first to cut
    # upload size and token cost without losing lesion detail.
    vision_max_edge: int = 1568

    @property
    def model_name(self) -> str:
        """Resolved Claude model, preferring ANTHROPIC_MODEL."""
        return (self.anthropic_model or self.claude_model or "claude-opus-5").strip()

    @property
    def use_foundry(self) -> bool:
        """True when requests should go through Azure AI Foundry."""
        return bool(self.anthropic_base_url.strip())

    # The chat assistant handles text-only questions. Claude keeps image
    # analysis. ASSISTANT_PROVIDER decides which answers chat; the other stays
    # available as an automatic fallback.
    # Azure OpenAI Responses API deployment for the text-only chat assistant.
    assistant_api_key: str = ""
    assistant_endpoint: str = ""
    assistant_model: str = "gpt-5.4"
    assistant_max_tokens: int = 900
    assistant_provider: str = "azure-openai"  # "azure-openai" | "claude"

    openweather_api_key: str = ""

    default_latitude: float = 9.4981
    default_longitude: float = 76.3388
    default_location_name: str = "Alappuzha, Kerala"

    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    max_upload_bytes: int = 8 * 1024 * 1024  # 8 MB

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def upload_dir(self) -> Path:
        path = BASE_DIR / "storage" / "uploads"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def knowledge_dir(self) -> Path:
        return BASE_DIR / "app" / "data"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
