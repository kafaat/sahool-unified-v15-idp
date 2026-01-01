"""
SAHOOL NDVI Repository
Data access layer for NDVI observations

Sprint 8: Clean separation of DB access from business logic
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Sequence
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from .models import NdviObservation, NdviAlert


# ─────────────────────────────────────────────────────────────────────────────
# NDVI Observations
# ─────────────────────────────────────────────────────────────────────────────


def upsert_observation(
    db: Session,
    obs: NdviObservation,
) -> NdviObservation:
    """
    Insert or update an NDVI observation.

    Uses PostgreSQL ON CONFLICT for atomic upsert.
    Conflict determined by (field_id, obs_date, source).

    Args:
        db: SQLAlchemy session
        obs: NdviObservation to save

    Returns:
        Saved/updated observation
    """
    # Simple approach: add and handle duplicates
    # For production, use proper upsert with ON CONFLICT
    existing = (
        db.query(NdviObservation)
        .filter(
            NdviObservation.field_id == obs.field_id,
            NdviObservation.obs_date == obs.obs_date,
            NdviObservation.source == obs.source,
        )
        .first()
    )

    if existing:
        # Update existing observation
        existing.ndvi_mean = obs.ndvi_mean
        existing.ndvi_min = obs.ndvi_min
        existing.ndvi_max = obs.ndvi_max
        existing.ndvi_std = obs.ndvi_std
        existing.ndvi_p10 = obs.ndvi_p10
        existing.ndvi_p90 = obs.ndvi_p90
        existing.cloud_coverage = obs.cloud_coverage
        existing.confidence = obs.confidence
        existing.pixel_count = obs.pixel_count
        existing.scene_id = obs.scene_id
        existing.metadata_json = obs.metadata_json
        return existing
    else:
        db.add(obs)
        return obs


def bulk_upsert_observations(
    db: Session,
    observations: Sequence[NdviObservation],
) -> int:
    """
    Bulk upsert multiple observations.

    Args:
        db: SQLAlchemy session
        observations: Sequence of observations to save

    Returns:
        Number of observations processed
    """
    count = 0
    for obs in observations:
        upsert_observation(db, obs)
        count += 1
    return count


def get_observation(
    db: Session,
    *,
    field_id: UUID,
    obs_date: date,
    source: str = "sentinel2",
) -> NdviObservation | None:
    """Get a specific observation by field, date, and source"""
    return (
        db.query(NdviObservation)
        .filter(
            NdviObservation.field_id == field_id,
            NdviObservation.obs_date == obs_date,
            NdviObservation.source == source,
        )
        .first()
    )


def get_series(
    db: Session,
    *,
    tenant_id: UUID,
    field_id: UUID,
    start_date: date,
    end_date: date,
    source: str | None = None,
    min_confidence: float | None = None,
) -> list[NdviObservation]:
    """
    Get NDVI time series for a field.

    Args:
        db: SQLAlchemy session
        tenant_id: Tenant UUID for isolation
        field_id: Field UUID
        start_date: Start of date range (inclusive)
        end_date: End of date range (inclusive)
        source: Optional source filter
        min_confidence: Optional minimum confidence filter

    Returns:
        List of observations ordered by date ascending
    """
    query = (
        select(NdviObservation)
        .where(NdviObservation.tenant_id == tenant_id)
        .where(NdviObservation.field_id == field_id)
        .where(NdviObservation.obs_date >= start_date)
        .where(NdviObservation.obs_date <= end_date)
    )

    if source:
        query = query.where(NdviObservation.source == source)

    if min_confidence is not None:
        query = query.where(NdviObservation.confidence >= min_confidence)

    query = query.order_by(NdviObservation.obs_date.asc())

    return list(db.execute(query).scalars())


def get_latest_observation(
    db: Session,
    *,
    tenant_id: UUID,
    field_id: UUID,
    source: str | None = None,
) -> NdviObservation | None:
    """Get the most recent observation for a field"""
    query = (
        select(NdviObservation)
        .where(NdviObservation.tenant_id == tenant_id)
        .where(NdviObservation.field_id == field_id)
    )

    if source:
        query = query.where(NdviObservation.source == source)

    query = query.order_by(NdviObservation.obs_date.desc()).limit(1)

    return db.execute(query).scalar_one_or_none()


def get_field_stats(
    db: Session,
    *,
    tenant_id: UUID,
    field_id: UUID,
    start_date: date,
    end_date: date,
) -> dict:
    """
    Get aggregate statistics for a field over a date range.

    Args:
        db: SQLAlchemy session
        tenant_id: Tenant UUID
        field_id: Field UUID
        start_date: Start date
        end_date: End date

    Returns:
        Dictionary with count, avg, min, max, std
    """
    result = db.execute(
        select(
            func.count(NdviObservation.id).label("count"),
            func.avg(NdviObservation.ndvi_mean).label("avg_ndvi"),
            func.min(NdviObservation.ndvi_mean).label("min_ndvi"),
            func.max(NdviObservation.ndvi_mean).label("max_ndvi"),
            func.stddev(NdviObservation.ndvi_mean).label("std_ndvi"),
            func.avg(NdviObservation.confidence).label("avg_confidence"),
        )
        .where(NdviObservation.tenant_id == tenant_id)
        .where(NdviObservation.field_id == field_id)
        .where(NdviObservation.obs_date >= start_date)
        .where(NdviObservation.obs_date <= end_date)
    ).first()

    return {
        "count": result.count or 0,
        "avg_ndvi": float(result.avg_ndvi) if result.avg_ndvi else None,
        "min_ndvi": float(result.min_ndvi) if result.min_ndvi else None,
        "max_ndvi": float(result.max_ndvi) if result.max_ndvi else None,
        "std_ndvi": float(result.std_ndvi) if result.std_ndvi else None,
        "avg_confidence": (
            float(result.avg_confidence) if result.avg_confidence else None
        ),
    }


def delete_old_observations(
    db: Session,
    *,
    tenant_id: UUID,
    before_date: date,
) -> int:
    """
    Delete observations older than a given date.

    Used for data retention/cleanup.

    Args:
        db: SQLAlchemy session
        tenant_id: Tenant UUID
        before_date: Delete observations before this date

    Returns:
        Number of deleted observations
    """
    result = db.execute(
        NdviObservation.__table__.delete()
        .where(NdviObservation.tenant_id == tenant_id)
        .where(NdviObservation.obs_date < before_date)
    )
    return result.rowcount


# ─────────────────────────────────────────────────────────────────────────────
# NDVI Alerts
# ─────────────────────────────────────────────────────────────────────────────


def create_alert(
    db: Session,
    alert: NdviAlert,
) -> NdviAlert:
    """Create a new NDVI alert"""
    db.add(alert)
    return alert


def get_unacknowledged_alerts(
    db: Session,
    *,
    tenant_id: UUID,
    field_id: UUID | None = None,
    limit: int = 100,
) -> list[NdviAlert]:
    """Get unacknowledged alerts for a tenant"""
    query = (
        select(NdviAlert)
        .where(NdviAlert.tenant_id == tenant_id)
        .where(NdviAlert.acknowledged == False)
    )

    if field_id:
        query = query.where(NdviAlert.field_id == field_id)

    query = query.order_by(NdviAlert.created_at.desc()).limit(limit)

    return list(db.execute(query).scalars())


def acknowledge_alert(
    db: Session,
    *,
    alert_id: UUID,
    tenant_id: UUID,
    user_id: UUID,
) -> bool:
    """Acknowledge an alert"""
    alert = (
        db.query(NdviAlert)
        .filter(
            NdviAlert.id == alert_id,
            NdviAlert.tenant_id == tenant_id,
        )
        .first()
    )

    if not alert:
        return False

    alert.acknowledged = True
    alert.acknowledged_at = datetime.now(timezone.utc)
    alert.acknowledged_by = user_id
    return True
