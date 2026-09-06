"""Seed a couple of demo reports so My Reports is never empty on first run."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.core.config import settings
from app.db import SessionLocal
from app.models.detection import DetectionReport

logger = logging.getLogger(__name__)

DEMO = [
    {
        "crop": "Coconut",
        "disease": "Leaf Rot",
        "confidence": 0.88,
        "severity": "Moderate",
        "symptoms": [
            "Blackened, shredded tips on the younger fronds",
            "Rotting tissue spreading inward from the leaflet edges",
        ],
        "treatment": [
            "Cut away and destroy the severely rotted portions of the young fronds.",
            "Improve drainage around the basin so water does not stand near the bole.",
            "Restore nutrition with organic manure and a balanced dose including potassium.",
        ],
        "prevention": [
            "Keep basins mulched and well drained through the monsoon.",
            "Inspect the crown monthly during and after heavy rain.",
        ],
        "explanation": "Symptoms match coconut leaf rot, which is common on palms weakened by root wilt during prolonged wet weather.",
        "days_ago": 6,
    },
    {
        "crop": "Turmeric",
        "disease": "Leaf Spot",
        "confidence": 0.81,
        "severity": "Mild",
        "symptoms": [
            "Small brown spots with pale centres scattered on the leaves",
        ],
        "treatment": [
            "Remove the worst affected leaves and destroy them away from the beds.",
            "Keep the beds mulched and the drainage channels clear.",
        ],
        "prevention": [
            "Plant on raised beds with free drainage.",
            "Maintain the potassium dose at earthing up.",
        ],
        "explanation": "Early leaf spot. Spread is limited so far, so cultural control should be enough.",
        "days_ago": 12,
    },
    {
        "crop": "Rice",
        "disease": "Healthy",
        "confidence": 0.92,
        "severity": "Healthy",
        "symptoms": ["Uniform green leaves with no lesions visible"],
        "treatment": ["No treatment needed. Continue your normal schedule."],
        "prevention": [
            "Scout the field weekly during humid weather.",
            "Avoid excess nitrogen, which invites blast and hoppers.",
        ],
        "explanation": "No disease signs found in this photo.",
        "days_ago": 20,
    },
]


def seed_demo_reports() -> None:
    db = SessionLocal()
    try:
        if db.scalar(select(DetectionReport.id).limit(1)):
            return
        now = datetime.now(timezone.utc)
        for item in DEMO:
            report = DetectionReport(
                crop=item["crop"],
                disease=item["disease"],
                confidence=item["confidence"],
                severity=item["severity"],
                symptoms=item["symptoms"],
                treatment=item["treatment"],
                prevention=item["prevention"],
                explanation=item["explanation"],
                needs_expert_confirmation=item["severity"] != "Healthy",
                status="Healthy" if item["severity"] == "Healthy" else "Action needed",
                location_name=settings.default_location_name,
                created_at=now - timedelta(days=item["days_ago"]),
            )
            report.set_location(settings.default_latitude, settings.default_longitude)
            db.add(report)
        db.commit()
        logger.info("Seeded %d demo detection reports.", len(DEMO))
    except Exception as exc:
        db.rollback()
        logger.warning("Could not seed demo reports: %s", exc)
    finally:
        db.close()
