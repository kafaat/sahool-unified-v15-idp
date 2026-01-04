"""
SAHOOL Alert Service - Repository Layer
Data access layer for alerts and alert rules

نطبق مبدأ فصل المسؤوليات: منطق الوصول للبيانات منفصل عن منطق العمل
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from .db_models import Alert, AlertRule

# ═══════════════════════════════════════════════════════════════════════════════
# Alerts Repository
# ═══════════════════════════════════════════════════════════════════════════════


def create_alert(db: Session, alert: Alert) -> Alert:
    """
    Create a new alert.

    Args:
        db: SQLAlchemy session
        alert: Alert object to create

    Returns:
        Created alert
    """
    db.add(alert)
    db.flush()  # Get the ID without committing
    return alert


def get_alert(
    db: Session,
    *,
    alert_id: UUID,
    tenant_id: UUID | None = None,
) -> Alert | None:
    """
    Get a specific alert by ID.

    Args:
        db: SQLAlchemy session
        alert_id: Alert UUID
        tenant_id: Optional tenant UUID for isolation

    Returns:
        Alert or None if not found
    """
    query = select(Alert).where(Alert.id == alert_id)

    if tenant_id:
        query = query.where(Alert.tenant_id == tenant_id)

    return db.execute(query).scalar_one_or_none()


def get_alerts_by_field(
    db: Session,
    *,
    field_id: str,
    tenant_id: UUID | None = None,
    status: str | None = None,
    alert_type: str | None = None,
    severity: str | None = None,
    skip: int = 0,
    limit: int = 50,
) -> tuple[list[Alert], int]:
    """
    Get alerts for a specific field with filtering.

    Args:
        db: SQLAlchemy session
        field_id: Field identifier
        tenant_id: Optional tenant UUID for isolation
        status: Optional status filter
        alert_type: Optional type filter
        severity: Optional severity filter
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return

    Returns:
        Tuple of (list of alerts, total count)
    """
    # Build base query
    query = select(Alert).where(Alert.field_id == field_id)

    if tenant_id:
        query = query.where(Alert.tenant_id == tenant_id)

    if status:
        query = query.where(Alert.status == status)

    if alert_type:
        query = query.where(Alert.type == alert_type)

    if severity:
        query = query.where(Alert.severity == severity)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = db.execute(count_query).scalar() or 0

    # Apply pagination and ordering
    query = query.order_by(Alert.created_at.desc()).offset(skip).limit(limit)

    alerts = list(db.execute(query).scalars())

    return alerts, total


def get_alerts_by_tenant(
    db: Session,
    *,
    tenant_id: UUID,
    status: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[Alert]:
    """
    Get alerts for a tenant with optional filters.

    Args:
        db: SQLAlchemy session
        tenant_id: Tenant UUID
        status: Optional status filter
        start_date: Optional start date filter
        end_date: Optional end date filter
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of alerts
    """
    query = select(Alert).where(Alert.tenant_id == tenant_id)

    if status:
        query = query.where(Alert.status == status)

    if start_date:
        query = query.where(Alert.created_at >= start_date)

    if end_date:
        query = query.where(Alert.created_at <= end_date)

    query = query.order_by(Alert.created_at.desc()).offset(skip).limit(limit)

    return list(db.execute(query).scalars())


def update_alert_status(
    db: Session,
    *,
    alert_id: UUID,
    status: str,
    user_id: str | None = None,
    note: str | None = None,
) -> Alert | None:
    """
    Update alert status with tracking.

    Args:
        db: SQLAlchemy session
        alert_id: Alert UUID
        status: New status
        user_id: Optional user identifier
        note: Optional note

    Returns:
        Updated alert or None if not found
    """
    alert = db.query(Alert).filter(Alert.id == alert_id).first()

    if not alert:
        return None

    alert.status = status
    now = datetime.now(UTC)

    if status == "acknowledged":
        alert.acknowledged_at = now
        alert.acknowledged_by = user_id
    elif status == "dismissed":
        alert.dismissed_at = now
        alert.dismissed_by = user_id
    elif status == "resolved":
        alert.resolved_at = now
        alert.resolved_by = user_id
        if note:
            alert.resolution_note = note

    return alert


def get_active_alerts(
    db: Session,
    *,
    tenant_id: UUID | None = None,
    field_id: str | None = None,
) -> list[Alert]:
    """
    Get all active (non-expired, non-resolved) alerts.

    Args:
        db: SQLAlchemy session
        tenant_id: Optional tenant filter
        field_id: Optional field filter

    Returns:
        List of active alerts
    """
    now = datetime.now(UTC)

    query = (
        select(Alert)
        .where(Alert.status.in_(["active", "acknowledged"]))
        .where(or_(Alert.expires_at.is_(None), Alert.expires_at > now))
    )

    if tenant_id:
        query = query.where(Alert.tenant_id == tenant_id)

    if field_id:
        query = query.where(Alert.field_id == field_id)

    query = query.order_by(Alert.severity.desc(), Alert.created_at.desc())

    return list(db.execute(query).scalars())


def delete_alert(db: Session, alert_id: UUID) -> bool:
    """
    Delete an alert.

    Args:
        db: SQLAlchemy session
        alert_id: Alert UUID

    Returns:
        True if deleted, False if not found
    """
    alert = db.query(Alert).filter(Alert.id == alert_id).first()

    if not alert:
        return False

    db.delete(alert)
    return True


def get_alert_statistics(
    db: Session,
    *,
    tenant_id: UUID | None = None,
    field_id: str | None = None,
    days: int = 30,
) -> dict:
    """
    Get alert statistics for a period.

    Args:
        db: SQLAlchemy session
        tenant_id: Optional tenant filter
        field_id: Optional field filter
        days: Number of days to look back

    Returns:
        Dictionary with statistics
    """
    cutoff = datetime.now(UTC) - timedelta(days=days)

    query = select(Alert).where(Alert.created_at >= cutoff)

    if tenant_id:
        query = query.where(Alert.tenant_id == tenant_id)

    if field_id:
        query = query.where(Alert.field_id == field_id)

    alerts = list(db.execute(query).scalars())

    total = len(alerts)
    active = len([a for a in alerts if a.status == "active"])

    by_type = {}
    by_severity = {}
    by_status = {}

    for alert in alerts:
        by_type[alert.type] = by_type.get(alert.type, 0) + 1
        by_severity[alert.severity] = by_severity.get(alert.severity, 0) + 1
        by_status[alert.status] = by_status.get(alert.status, 0) + 1

    # Calculate resolution times
    resolution_times = []
    for alert in alerts:
        if alert.resolved_at and alert.created_at:
            delta = alert.resolved_at - alert.created_at
            hours = delta.total_seconds() / 3600
            resolution_times.append(hours)

    avg_resolution = (
        sum(resolution_times) / len(resolution_times) if resolution_times else None
    )

    return {
        "total_alerts": total,
        "active_alerts": active,
        "by_type": by_type,
        "by_severity": by_severity,
        "by_status": by_status,
        "acknowledged_count": by_status.get("acknowledged", 0),
        "resolved_count": by_status.get("resolved", 0),
        "average_resolution_hours": (
            round(avg_resolution, 2) if avg_resolution else None
        ),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Alert Rules Repository
# ═══════════════════════════════════════════════════════════════════════════════


def create_alert_rule(db: Session, rule: AlertRule) -> AlertRule:
    """
    Create a new alert rule.

    Args:
        db: SQLAlchemy session
        rule: AlertRule object to create

    Returns:
        Created alert rule
    """
    db.add(rule)
    db.flush()
    return rule


def get_alert_rule(
    db: Session,
    *,
    rule_id: UUID,
    tenant_id: UUID | None = None,
) -> AlertRule | None:
    """
    Get a specific alert rule by ID.

    Args:
        db: SQLAlchemy session
        rule_id: Rule UUID
        tenant_id: Optional tenant UUID for isolation

    Returns:
        AlertRule or None if not found
    """
    query = select(AlertRule).where(AlertRule.id == rule_id)

    if tenant_id:
        query = query.where(AlertRule.tenant_id == tenant_id)

    return db.execute(query).scalar_one_or_none()


def get_alert_rules_by_field(
    db: Session,
    *,
    field_id: str,
    tenant_id: UUID | None = None,
    enabled_only: bool = False,
) -> list[AlertRule]:
    """
    Get alert rules for a specific field.

    Args:
        db: SQLAlchemy session
        field_id: Field identifier
        tenant_id: Optional tenant UUID for isolation
        enabled_only: If True, return only enabled rules

    Returns:
        List of alert rules
    """
    query = select(AlertRule).where(AlertRule.field_id == field_id)

    if tenant_id:
        query = query.where(AlertRule.tenant_id == tenant_id)

    if enabled_only:
        query = query.where(AlertRule.enabled is True)

    query = query.order_by(AlertRule.created_at.desc())

    return list(db.execute(query).scalars())


def get_enabled_rules(db: Session, tenant_id: UUID | None = None) -> list[AlertRule]:
    """
    Get all enabled alert rules.

    Args:
        db: SQLAlchemy session
        tenant_id: Optional tenant filter

    Returns:
        List of enabled alert rules
    """
    query = select(AlertRule).where(AlertRule.enabled is True)

    if tenant_id:
        query = query.where(AlertRule.tenant_id == tenant_id)

    return list(db.execute(query).scalars())


def update_alert_rule(
    db: Session,
    *,
    rule_id: UUID,
    **updates,
) -> AlertRule | None:
    """
    Update an alert rule.

    Args:
        db: SQLAlchemy session
        rule_id: Rule UUID
        **updates: Fields to update

    Returns:
        Updated rule or None if not found
    """
    rule = db.query(AlertRule).filter(AlertRule.id == rule_id).first()

    if not rule:
        return None

    for key, value in updates.items():
        if hasattr(rule, key):
            setattr(rule, key, value)

    rule.updated_at = datetime.now(UTC)

    return rule


def delete_alert_rule(db: Session, rule_id: UUID) -> bool:
    """
    Delete an alert rule.

    Args:
        db: SQLAlchemy session
        rule_id: Rule UUID

    Returns:
        True if deleted, False if not found
    """
    rule = db.query(AlertRule).filter(AlertRule.id == rule_id).first()

    if not rule:
        return False

    db.delete(rule)
    return True


def mark_rule_triggered(db: Session, rule_id: UUID) -> AlertRule | None:
    """
    Mark a rule as triggered (update last_triggered_at).

    Args:
        db: SQLAlchemy session
        rule_id: Rule UUID

    Returns:
        Updated rule or None if not found
    """
    rule = db.query(AlertRule).filter(AlertRule.id == rule_id).first()

    if not rule:
        return None

    rule.last_triggered_at = datetime.now(UTC)

    return rule


def get_rules_ready_to_trigger(
    db: Session,
    *,
    tenant_id: UUID | None = None,
) -> list[AlertRule]:
    """
    Get enabled rules that are ready to trigger (past cooldown period).

    Args:
        db: SQLAlchemy session
        tenant_id: Optional tenant filter

    Returns:
        List of rules ready to trigger
    """
    now = datetime.now(UTC)

    query = select(AlertRule).where(AlertRule.enabled is True)

    if tenant_id:
        query = query.where(AlertRule.tenant_id == tenant_id)

    rules = list(db.execute(query).scalars())

    # Filter by cooldown
    ready_rules = []
    for rule in rules:
        if rule.last_triggered_at is None:
            ready_rules.append(rule)
        else:
            cooldown_delta = timedelta(hours=rule.cooldown_hours)
            if rule.last_triggered_at + cooldown_delta <= now:
                ready_rules.append(rule)

    return ready_rules
