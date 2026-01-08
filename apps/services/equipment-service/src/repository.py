"""
SAHOOL Equipment Service - Repository Layer
Data access layer for equipment, maintenance records, and alerts

نطبق مبدأ فصل المسؤوليات: منطق الوصول للبيانات منفصل عن منطق العمل
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .db_models import Equipment, MaintenanceAlert, MaintenanceRecord

# ═══════════════════════════════════════════════════════════════════════════════
# Equipment Repository
# ═══════════════════════════════════════════════════════════════════════════════


def create_equipment(db: Session, equipment: Equipment) -> Equipment:
    """
    Create a new equipment record.

    Args:
        db: SQLAlchemy session
        equipment: Equipment object to create

    Returns:
        Created equipment
    """
    db.add(equipment)
    db.flush()  # Get the ID without committing
    return equipment


def get_equipment(
    db: Session,
    *,
    equipment_id: str,
    tenant_id: str | None = None,
) -> Equipment | None:
    """
    Get a specific equipment by ID.

    Args:
        db: SQLAlchemy session
        equipment_id: Equipment identifier
        tenant_id: Optional tenant ID for isolation

    Returns:
        Equipment or None if not found
    """
    query = select(Equipment).where(Equipment.equipment_id == equipment_id)

    if tenant_id:
        query = query.where(Equipment.tenant_id == tenant_id)

    return db.execute(query).scalar_one_or_none()


def get_equipment_by_qr(
    db: Session,
    *,
    qr_code: str,
    tenant_id: str | None = None,
) -> Equipment | None:
    """
    Get equipment by QR code.

    Args:
        db: SQLAlchemy session
        qr_code: QR code
        tenant_id: Optional tenant ID for isolation

    Returns:
        Equipment or None if not found
    """
    query = select(Equipment).where(Equipment.qr_code == qr_code)

    if tenant_id:
        query = query.where(Equipment.tenant_id == tenant_id)

    return db.execute(query).scalar_one_or_none()


def list_equipment(
    db: Session,
    *,
    tenant_id: str,
    equipment_type: str | None = None,
    status: str | None = None,
    field_id: str | None = None,
    skip: int = 0,
    limit: int = 50,
) -> tuple[list[Equipment], int]:
    """
    List equipment with filtering and pagination.

    Args:
        db: SQLAlchemy session
        tenant_id: Tenant ID
        equipment_type: Optional equipment type filter
        status: Optional status filter
        field_id: Optional field ID filter
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return

    Returns:
        Tuple of (list of equipment, total count)
    """
    # Build base query
    query = select(Equipment).where(Equipment.tenant_id == tenant_id)

    if equipment_type:
        query = query.where(Equipment.equipment_type == equipment_type)

    if status:
        query = query.where(Equipment.status == status)

    if field_id:
        query = query.where(Equipment.field_id == field_id)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = db.execute(count_query).scalar() or 0

    # Apply pagination and ordering
    query = query.order_by(Equipment.name).offset(skip).limit(limit)

    equipment_list = list(db.execute(query).scalars())

    return equipment_list, total


def update_equipment(
    db: Session,
    *,
    equipment_id: str,
    tenant_id: str,
    **updates,
) -> Equipment | None:
    """
    Update equipment fields.

    Args:
        db: SQLAlchemy session
        equipment_id: Equipment identifier
        tenant_id: Tenant ID for isolation
        **updates: Fields to update

    Returns:
        Updated equipment or None if not found
    """
    equipment = (
        db.query(Equipment)
        .filter(
            Equipment.equipment_id == equipment_id,
            Equipment.tenant_id == tenant_id,
        )
        .first()
    )

    if not equipment:
        return None

    for key, value in updates.items():
        if hasattr(equipment, key) and value is not None:
            setattr(equipment, key, value)

    equipment.updated_at = datetime.utcnow()

    return equipment


def delete_equipment(db: Session, equipment_id: str, tenant_id: str) -> bool:
    """
    Delete an equipment record.

    Args:
        db: SQLAlchemy session
        equipment_id: Equipment identifier
        tenant_id: Tenant ID for isolation

    Returns:
        True if deleted, False if not found
    """
    equipment = (
        db.query(Equipment)
        .filter(
            Equipment.equipment_id == equipment_id,
            Equipment.tenant_id == tenant_id,
        )
        .first()
    )

    if not equipment:
        return False

    db.delete(equipment)
    return True


def get_equipment_stats(
    db: Session,
    *,
    tenant_id: str,
) -> dict:
    """
    Get equipment statistics for a tenant.

    Args:
        db: SQLAlchemy session
        tenant_id: Tenant ID

    Returns:
        Dictionary with statistics
    """
    equipment_list = db.query(Equipment).filter(Equipment.tenant_id == tenant_id).all()

    by_type = {}
    by_status = {}

    for eq in equipment_list:
        by_type[eq.equipment_type] = by_type.get(eq.equipment_type, 0) + 1
        by_status[eq.status] = by_status.get(eq.status, 0) + 1

    return {
        "total": len(equipment_list),
        "by_type": by_type,
        "by_status": by_status,
        "operational": by_status.get("operational", 0),
        "maintenance": by_status.get("maintenance", 0) + by_status.get("repair", 0),
        "inactive": by_status.get("inactive", 0),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Maintenance Records Repository
# ═══════════════════════════════════════════════════════════════════════════════


def create_maintenance_record(db: Session, record: MaintenanceRecord) -> MaintenanceRecord:
    """
    Create a new maintenance record.

    Args:
        db: SQLAlchemy session
        record: MaintenanceRecord object to create

    Returns:
        Created maintenance record
    """
    db.add(record)
    db.flush()
    return record


def get_maintenance_history(
    db: Session,
    *,
    equipment_id: str,
    limit: int = 20,
) -> list[MaintenanceRecord]:
    """
    Get maintenance history for equipment.

    Args:
        db: SQLAlchemy session
        equipment_id: Equipment identifier
        limit: Maximum number of records to return

    Returns:
        List of maintenance records
    """
    query = (
        select(MaintenanceRecord)
        .where(MaintenanceRecord.equipment_id == equipment_id)
        .order_by(MaintenanceRecord.performed_at.desc())
        .limit(limit)
    )

    return list(db.execute(query).scalars())


# ═══════════════════════════════════════════════════════════════════════════════
# Maintenance Alerts Repository
# ═══════════════════════════════════════════════════════════════════════════════


def create_maintenance_alert(db: Session, alert: MaintenanceAlert) -> MaintenanceAlert:
    """
    Create a new maintenance alert.

    Args:
        db: SQLAlchemy session
        alert: MaintenanceAlert object to create

    Returns:
        Created maintenance alert
    """
    db.add(alert)
    db.flush()
    return alert


def get_maintenance_alerts(
    db: Session,
    *,
    tenant_id: str,
    priority: str | None = None,
    overdue_only: bool = False,
) -> list[MaintenanceAlert]:
    """
    Get maintenance alerts with filtering.

    Args:
        db: SQLAlchemy session
        tenant_id: Tenant ID
        priority: Optional priority filter
        overdue_only: If True, return only overdue alerts

    Returns:
        List of maintenance alerts
    """
    # Get equipment IDs for this tenant
    equipment_ids = db.query(Equipment.equipment_id).filter(Equipment.tenant_id == tenant_id).all()
    equipment_id_list = [eq[0] for eq in equipment_ids]

    if not equipment_id_list:
        return []

    query = select(MaintenanceAlert).where(MaintenanceAlert.equipment_id.in_(equipment_id_list))

    if priority:
        query = query.where(MaintenanceAlert.priority == priority)

    if overdue_only:
        query = query.where(MaintenanceAlert.is_overdue == True)

    # Sort by priority and overdue status
    query = query.order_by(
        MaintenanceAlert.is_overdue.desc(),
        MaintenanceAlert.priority.desc(),
    )

    return list(db.execute(query).scalars())


def delete_maintenance_alert(db: Session, alert_id: str) -> bool:
    """
    Delete a maintenance alert.

    Args:
        db: SQLAlchemy session
        alert_id: Alert identifier

    Returns:
        True if deleted, False if not found
    """
    alert = db.query(MaintenanceAlert).filter(MaintenanceAlert.alert_id == alert_id).first()

    if not alert:
        return False

    db.delete(alert)
    return True
