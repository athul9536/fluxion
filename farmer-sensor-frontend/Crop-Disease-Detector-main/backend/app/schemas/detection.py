from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class Location(BaseModel):
    latitude: float | None = None
    longitude: float | None = None
    name: str | None = None


SEVERITIES = {"Healthy", "Mild", "Moderate", "Severe", "Unknown"}


class VisionAnalysis(BaseModel):
    """Structured crop analysis returned by Claude Vision."""

    crop: str = "Unknown"
    disease: str = "Unable to determine"
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    severity: str = "Unknown"
    symptoms: list[str] = []
    treatment: list[str] = []
    prevention: list[str] = []
    explanation: str = ""
    needs_expert_confirmation: bool = True


class DetectionResponse(VisionAnalysis):
    """API response for POST /api/detect."""

    id: int | None = None
    # Echoed back only when it was saved (i.e. a disease was detected).
    pincode: str | None = None
    location: Location = Location()
    image_url: str | None = None
    created_at: datetime | None = None
    saved: bool = True
    note: str | None = None

    @property
    def healthy(self) -> bool:
        return self.severity == "Healthy"


class ReportOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    crop: str
    disease: str
    confidence: float
    severity: str
    treatment: list[str] = []
    symptoms: list[str] = []
    prevention: list[str] = []
    explanation: str | None = None
    needs_expert_confirmation: bool = True
    status: str
    location_name: str | None = None
    pincode: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    image_url: str | None = None
    created_at: datetime


class ReportStats(BaseModel):
    crops_scanned: int = 0
    diseases_detected: int = 0
    healthy_plants: int = 0
    questions_asked: int = 0
