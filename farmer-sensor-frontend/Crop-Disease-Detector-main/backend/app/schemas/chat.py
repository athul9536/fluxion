from pydantic import BaseModel, Field


class DetectionContext(BaseModel):
    """Detection context forwarded from the dashboard's 'Ask Vani about this result'."""

    crop: str | None = None
    disease: str | None = None
    confidence: float | None = None
    severity: str | None = None
    symptoms: list[str] = []
    treatment: list[str] = []
    explanation: str | None = None
    image_url: str | None = None


class ChatContext(BaseModel):
    detection: DetectionContext | None = None
    latitude: float | None = None
    longitude: float | None = None
    include_weather: bool = True


class ChatTurn(BaseModel):
    """One earlier turn, so the assistant can hold a real conversation."""

    role: str = "user"  # "user" | "assistant"
    text: str = ""


class ChatRequest(BaseModel):
    message: str = Field(default="", max_length=2000)
    # Optional base64 image (data URL or bare base64) for in-chat diagnosis.
    image: str | None = None
    # Accepted at the top level as well as inside `context` for convenience.
    detection_context: DetectionContext | None = None
    context: ChatContext | None = None
    # Recent turns, oldest first. Trimmed server-side.
    history: list[ChatTurn] = []


class ChatResponse(BaseModel):
    response: str
    sources: list[str] = []
    used_weather: bool = False
    used_image: bool = False
    model_source: str = "claude"
