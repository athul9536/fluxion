"""detection_reports table.

Location is stored as a PostGIS geography(Point, 4326) column for spatial
queries, alongside plain latitude/longitude columns so the API stays simple.
The table itself is managed by the Supabase migrations in supabase/migrations/.
"""

from datetime import datetime, timezone

from geoalchemy2 import Geography
from sqlalchemy import JSON, Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db import POSTGIS_ENABLED, Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class DetectionReport(Base):
    __tablename__ = "detection_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    farmer_id: Mapped[str] = mapped_column(String(64), default="premium-farmer-001")

    crop: Mapped[str] = mapped_column(String(80))
    disease: Mapped[str] = mapped_column(String(120))
    confidence: Mapped[float] = mapped_column(Float)
    severity: Mapped[str] = mapped_column(String(40))
    status: Mapped[str] = mapped_column(String(40), default="Reviewed")

    # Claude Vision returns lists; stored as JSON so reports round-trip exactly.
    treatment: Mapped[list | None] = mapped_column(JSON, default=list, nullable=True)
    symptoms: Mapped[list | None] = mapped_column(JSON, default=list, nullable=True)
    prevention: Mapped[list | None] = mapped_column(JSON, default=list, nullable=True)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    needs_expert_confirmation: Mapped[bool] = mapped_column(Boolean, default=True)

    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    location_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    # Recorded only when a disease is found; stays null for healthy scans.
    pincode: Mapped[str | None] = mapped_column(String(12), nullable=True)

    image_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(255), nullable=True)

    geom: Mapped[str | None] = mapped_column(
        Geography(geometry_type="POINT", srid=4326), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )

    def set_location(self, latitude: float | None, longitude: float | None) -> None:
        self.latitude = latitude
        self.longitude = longitude
        if POSTGIS_ENABLED and latitude is not None and longitude is not None:
            self.geom = f"SRID=4326;POINT({longitude} {latitude})"
