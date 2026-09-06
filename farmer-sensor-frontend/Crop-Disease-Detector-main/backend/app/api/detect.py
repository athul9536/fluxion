"""POST /api/detect - crop disease analysis via Claude Vision.

React uploads multipart/form-data here; the Anthropic API key stays on the
backend and is never sent to the browser.
"""

from __future__ import annotations

import logging
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db import get_db
from app.models.detection import DetectionReport
from app.schemas.detection import DetectionResponse
from app.services.vision_service import vision_service

logger = logging.getLogger(__name__)
router = APIRouter()

SUFFIX_BY_MEDIA = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}


def _clean_pincode(value: str | None) -> str | None:
    """Keep digits only and accept a plausible 6-digit Indian pincode.

    Anything else is dropped rather than stored, since a malformed code is worse
    than none for grouping outbreaks by area.
    """
    if not value:
        return None
    digits = "".join(ch for ch in value if ch.isdigit())
    return digits if len(digits) == 6 else None


def _save_image(raw: bytes, filename: str) -> tuple[str, str]:
    suffix = Path(filename or "").suffix.lower()
    if suffix not in {".jpg", ".jpeg", ".png", ".webp"}:
        suffix = ".jpg"
    name = f"{uuid.uuid4().hex}{suffix}"
    path = settings.upload_dir / name
    path.write_bytes(raw)
    return str(path), f"/media/{name}"


@router.post("/detect", response_model=DetectionResponse)
async def detect(
    db: Session = Depends(get_db),
    image: UploadFile = File(...),
    latitude: float | None = Form(default=None),
    longitude: float | None = Form(default=None),
    location_name: str | None = Form(default=None),
    pincode: str | None = Form(default=None),
):
    raw = await image.read()

    # Validation (type, size, decodability) lives in the vision service so the
    # same rules apply to the chatbot's image path.
    analysis = vision_service.analyze(raw)

    image_path, image_url = _save_image(raw, image.filename or "crop.jpg")

    lat = latitude if latitude is not None else settings.default_latitude
    lon = longitude if longitude is not None else settings.default_longitude
    place = location_name or settings.default_location_name

    undetermined = analysis.disease.strip().lower() == "unable to determine"
    if analysis.severity == "Healthy":
        status = "Healthy"
    elif undetermined:
        status = "Needs a clearer photo"
    else:
        status = "Action needed"

    # Pincode is stored only for confirmed disease findings, so the table can be
    # grouped by area for outbreak tracking. Healthy and undetermined scans
    # deliberately leave it null.
    diseased = not undetermined and analysis.severity != "Healthy"
    saved_pincode = _clean_pincode(pincode) if diseased else None

    report = DetectionReport(
        crop=analysis.crop,
        disease=analysis.disease,
        confidence=analysis.confidence,
        severity=analysis.severity,
        treatment=analysis.treatment,
        symptoms=analysis.symptoms,
        prevention=analysis.prevention,
        explanation=analysis.explanation,
        needs_expert_confirmation=analysis.needs_expert_confirmation,
        status=status,
        location_name=place,
        pincode=saved_pincode,
        image_path=image_path,
        image_url=image_url,
    )
    report.set_location(lat, lon)

    saved = True
    note = None
    try:
        db.add(report)
        db.commit()
        db.refresh(report)
    except Exception as exc:  # analysis is still useful without persistence
        saved = False
        note = "We couldn't save this analysis to your reports, but the result is ready."
        logger.exception("Could not save detection report: %s", exc)
        # The connection may already be dead (e.g. the Supabase pooler dropped
        # it), in which case rollback raises too. Never let cleanup turn a
        # usable analysis into a 500.
        try:
            db.rollback()
        except Exception:
            logger.warning("Rollback failed after a failed commit; connection likely closed.")

    report_id = None
    created_at = None
    if saved:
        try:
            report_id = report.id
            created_at = report.created_at
        except Exception:
            logger.warning("Could not read saved report identity; returning result only.")

    return DetectionResponse(
        **analysis.model_dump(),
        id=report_id,
        pincode=saved_pincode,
        location={"latitude": lat, "longitude": lon, "name": place},
        image_url=image_url,
        created_at=created_at,
        saved=saved,
        note=note,
    )
