"""GET /api/reports and /api/reports/{id} - detection history."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.detection import DetectionReport
from app.schemas.detection import ReportOut, ReportStats
from app.state import counters

router = APIRouter()


@router.get("/reports", response_model=list[ReportOut])
def list_reports(db: Session = Depends(get_db), limit: int = 50):
    stmt = (
        select(DetectionReport)
        .order_by(DetectionReport.created_at.desc(), DetectionReport.id.desc())
        .limit(min(limit, 200))
    )
    return db.scalars(stmt).all()


@router.get("/reports/stats", response_model=ReportStats)
def report_stats(db: Session = Depends(get_db)):
    reports = db.scalars(select(DetectionReport)).all()
    healthy = sum(1 for r in reports if r.severity == "Healthy")
    # "Unable to determine" analyses are neither a disease nor a clean bill.
    undetermined = sum(
        1 for r in reports if r.disease.strip().lower() == "unable to determine"
    )
    return ReportStats(
        crops_scanned=len(reports),
        diseases_detected=max(0, len(reports) - healthy - undetermined),
        healthy_plants=healthy,
        questions_asked=counters.questions_asked,
    )


@router.get("/reports/{report_id}", response_model=ReportOut)
def get_report(report_id: int, db: Session = Depends(get_db)):
    report = db.get(DetectionReport, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="We couldn't find that report.")
    return report
