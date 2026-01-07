"""
SAHOOL Audit Service
Unified audit logging service for all domains
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from .hashchain import build_canonical_string, compute_entry_hash
from .models import AuditLog
from .redact import redact_dict

logger = logging.getLogger(__name__)


def get_last_hash(db: Session, tenant_id: UUID) -> str | None:
    """
    Get the hash of the last audit entry for a tenant.

    Args:
        db: SQLAlchemy session
        tenant_id: Tenant UUID

    Returns:
        Last entry hash or None if no entries exist
    """
    stmt = (
        select(AuditLog.entry_hash)
        .where(AuditLog.tenant_id == tenant_id)
        .order_by(AuditLog.created_at.desc())
        .limit(1)
    )
    return db.execute(stmt).scalar_one_or_none()


def write_audit_log(
    db: Session,
    *,
    tenant_id: UUID,
    actor_id: UUID | None,
    actor_type: str,
    action: str,
    resource_type: str,
    resource_id: str,
    correlation_id: UUID,
    ip: str | None = None,
    user_agent: str | None = None,
    details: dict[str, Any] | None = None,
) -> AuditLog:
    """
    Write an audit log entry with hash chain integrity.

    This is the single entry point for all audit logging in SAHOOL.
    All services should use this function to ensure consistent
    logging format and hash chain integrity.

    Args:
        db: SQLAlchemy session
        tenant_id: Tenant UUID
        actor_id: User or service ID (None for system actions)
        actor_type: Type of actor ('user', 'service', 'system')
        action: Action performed (e.g., 'field.create')
        resource_type: Type of resource (e.g., 'field')
        resource_id: ID of the affected resource
        correlation_id: Request correlation ID
        ip: Client IP address
        user_agent: Client user agent
        details: Additional details (will be redacted)

    Returns:
        Created AuditLog entry

    Example:
        ```python
        from shared.libs.audit import write_audit_log

        write_audit_log(
            db=session,
            tenant_id=tenant_id,
            actor_id=user_id,
            actor_type="user",
            action="field.create",
            resource_type="field",
            resource_id=str(field.id),
            correlation_id=correlation_id,
            ip=request.client.host,
            details={"name": field.name},
        )
        ```
    """
    # Redact sensitive data from details
    safe_details = redact_dict(details or {})
    details_json = json.dumps(safe_details, ensure_ascii=False, sort_keys=True)

    # Truncate user_agent if too long
    if user_agent and len(user_agent) > 256:
        user_agent = user_agent[:253] + "..."

    # Get previous hash for chain
    prev_hash = get_last_hash(db, tenant_id)

    # Create entry (without hash initially)
    entry = AuditLog(
        tenant_id=tenant_id,
        actor_id=actor_id,
        actor_type=actor_type,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        correlation_id=correlation_id,
        ip=ip,
        user_agent=user_agent,
        details_json=details_json,
        prev_hash=prev_hash,
        entry_hash="",  # Will be computed after flush
    )

    db.add(entry)
    db.flush()  # Ensures created_at is set

    # Compute hash with all fields including created_at
    canonical = build_canonical_string(
        tenant_id=str(entry.tenant_id),
        actor_id=str(entry.actor_id) if entry.actor_id else None,
        actor_type=entry.actor_type,
        action=entry.action,
        resource_type=entry.resource_type,
        resource_id=entry.resource_id,
        correlation_id=str(entry.correlation_id),
        details_json=entry.details_json,
        created_at_iso=entry.created_at.isoformat(),
    )
    entry.entry_hash = compute_entry_hash(
        prev_hash=entry.prev_hash, canonical=canonical
    )

    db.flush()

    logger.info(
        f"Audit: {entry.action} on {entry.resource_type}/{entry.resource_id} "
        f"by {entry.actor_type}/{entry.actor_id} "
        f"[tenant={entry.tenant_id}, corr={entry.correlation_id}]"
    )

    return entry


def query_audit_logs(
    db: Session,
    *,
    tenant_id: UUID,
    actor_id: UUID | None = None,
    resource_type: str | None = None,
    resource_id: str | None = None,
    action: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[AuditLog]:
    """
    Query audit logs with filters.

    Args:
        db: SQLAlchemy session
        tenant_id: Tenant UUID (required)
        actor_id: Filter by actor
        resource_type: Filter by resource type
        resource_id: Filter by resource ID
        action: Filter by action (supports prefix matching)
        start_date: Filter by start date
        end_date: Filter by end date
        limit: Maximum results
        offset: Pagination offset

    Returns:
        List of matching AuditLog entries
    """
    stmt = (
        select(AuditLog)
        .where(AuditLog.tenant_id == tenant_id)
        .order_by(AuditLog.created_at.desc())
    )

    if actor_id:
        stmt = stmt.where(AuditLog.actor_id == actor_id)

    if resource_type:
        stmt = stmt.where(AuditLog.resource_type == resource_type)

    if resource_id:
        stmt = stmt.where(AuditLog.resource_id == resource_id)

    if action:
        # Support prefix matching (e.g., "field." matches all field actions)
        if action.endswith("."):
            stmt = stmt.where(AuditLog.action.startswith(action))
        else:
            stmt = stmt.where(AuditLog.action == action)

    if start_date:
        stmt = stmt.where(AuditLog.created_at >= start_date)

    if end_date:
        stmt = stmt.where(AuditLog.created_at <= end_date)

    stmt = stmt.limit(limit).offset(offset)

    return list(db.execute(stmt).scalars())


def get_audit_log_by_id(
    db: Session,
    audit_id: UUID,
    tenant_id: UUID,
) -> AuditLog | None:
    """Get a specific audit log entry"""
    stmt = (
        select(AuditLog)
        .where(AuditLog.id == audit_id)
        .where(AuditLog.tenant_id == tenant_id)
    )
    return db.execute(stmt).scalar_one_or_none()


def get_resource_history(
    db: Session,
    *,
    tenant_id: UUID,
    resource_type: str,
    resource_id: str,
    limit: int = 50,
) -> list[AuditLog]:
    """
    Get the audit history for a specific resource.

    Args:
        db: SQLAlchemy session
        tenant_id: Tenant UUID
        resource_type: Type of resource
        resource_id: Resource ID
        limit: Maximum results

    Returns:
        List of audit entries for the resource
    """
    return query_audit_logs(
        db,
        tenant_id=tenant_id,
        resource_type=resource_type,
        resource_id=resource_id,
        limit=limit,
    )
