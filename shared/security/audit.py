"""
Audit Logging Service
Database + Event logging for security audit trail

Features:
- Field-level change tracking
- Hash chain integrity validation
- Compliance reporting
- Fallback logging for failures
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from uuid import uuid4

from .audit_models import AuditCategory, AuditLog, AuditSeverity

logger = logging.getLogger(__name__)

# Configuration for hash chain
ENABLE_HASH_CHAIN = True
HASH_ALGORITHM = "sha256"


# ─────────────────────────────────────────────────────────────────────────────
# Audit Action Constants
# ─────────────────────────────────────────────────────────────────────────────


class AuditAction(StrEnum):
    """Standard audit actions"""

    # Auth
    LOGIN_SUCCESS = "auth.login.success"
    LOGIN_FAILED = "auth.login.failed"
    LOGOUT = "auth.logout"
    TOKEN_REFRESH = "auth.token.refresh"
    TOKEN_REVOKED = "auth.token.revoked"
    PASSWORD_CHANGED = "auth.password.changed"
    PASSWORD_RESET = "auth.password.reset"

    # Access
    RESOURCE_ACCESSED = "access.resource.accessed"
    PERMISSION_DENIED = "access.permission.denied"
    TENANT_SWITCHED = "access.tenant.switched"

    # Data - Tasks
    TASK_CREATED = "data.task.created"
    TASK_UPDATED = "data.task.updated"
    TASK_DELETED = "data.task.deleted"
    TASK_ASSIGNED = "data.task.assigned"
    TASK_COMPLETED = "data.task.completed"

    # Data - Fields
    FIELD_CREATED = "data.field.created"
    FIELD_UPDATED = "data.field.updated"
    FIELD_DELETED = "data.field.deleted"

    # Data - IoT
    DEVICE_REGISTERED = "data.device.registered"
    DEVICE_UPDATED = "data.device.updated"
    DEVICE_REMOVED = "data.device.removed"

    # Admin
    USER_CREATED = "admin.user.created"
    USER_UPDATED = "admin.user.updated"
    USER_DELETED = "admin.user.deleted"
    USER_ROLE_CHANGED = "admin.user.role_changed"
    TENANT_CREATED = "admin.tenant.created"
    TENANT_UPDATED = "admin.tenant.updated"

    # Security
    SUSPICIOUS_ACTIVITY = "security.suspicious_activity"
    RATE_LIMIT_EXCEEDED = "security.rate_limit_exceeded"
    INVALID_TOKEN = "security.invalid_token"
    BRUTE_FORCE_DETECTED = "security.brute_force_detected"


# ─────────────────────────────────────────────────────────────────────────────
# Audit Logger
# ─────────────────────────────────────────────────────────────────────────────


async def audit_log(
    *,
    tenant_id: str,
    user_id: str,
    action: str,
    resource_type: str | None = None,
    resource_id: str | None = None,
    category: str = AuditCategory.ACCESS,
    severity: str = AuditSeverity.INFO,
    correlation_id: str | None = None,
    session_id: str | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
    request_method: str | None = None,
    request_path: str | None = None,
    details: dict | None = None,
    old_value: dict | None = None,
    new_value: dict | None = None,
    success: bool = True,
    error_code: str | None = None,
    error_message: str | None = None,
) -> AuditLog:
    """
    Create an audit log entry.

    Usage:
        await audit_log(
            tenant_id=principal["tid"],
            user_id=principal["sub"],
            action=AuditAction.TASK_COMPLETED,
            resource_type="task",
            resource_id=task_id,
            category=AuditCategory.DATA,
        )
    """
    log_entry = await AuditLog.create(
        id=uuid4(),
        tenant_id=tenant_id,
        user_id=user_id,
        action=action,
        category=category,
        severity=severity,
        resource_type=resource_type,
        resource_id=resource_id,
        correlation_id=correlation_id,
        session_id=session_id,
        ip_address=ip_address,
        user_agent=user_agent,
        request_method=request_method,
        request_path=request_path,
        details=details,
        old_value=old_value,
        new_value=new_value,
        success=success,
        error_code=error_code,
        error_message=error_message,
    )

    # Also log to application logger for immediate visibility
    log_level = logging.WARNING if not success else logging.INFO
    logger.log(
        log_level,
        f"AUDIT: {action} | tenant={tenant_id} user={user_id} resource={resource_type}:{resource_id} success={success}",
    )

    return log_entry


# ─────────────────────────────────────────────────────────────────────────────
# Convenience Functions
# ─────────────────────────────────────────────────────────────────────────────


async def audit_auth(
    tenant_id: str,
    user_id: str,
    action: str,
    success: bool = True,
    ip_address: str | None = None,
    user_agent: str | None = None,
    details: dict | None = None,
    error_message: str | None = None,
) -> AuditLog:
    """Log authentication events"""
    return await audit_log(
        tenant_id=tenant_id,
        user_id=user_id,
        action=action,
        category=AuditCategory.AUTH,
        severity=AuditSeverity.WARNING if not success else AuditSeverity.INFO,
        ip_address=ip_address,
        user_agent=user_agent,
        details=details,
        success=success,
        error_message=error_message,
    )


async def audit_data_change(
    tenant_id: str,
    user_id: str,
    action: str,
    resource_type: str,
    resource_id: str,
    old_value: dict | None = None,
    new_value: dict | None = None,
    correlation_id: str | None = None,
) -> AuditLog:
    """Log data change events with before/after values"""
    return await audit_log(
        tenant_id=tenant_id,
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        category=AuditCategory.DATA,
        old_value=old_value,
        new_value=new_value,
        correlation_id=correlation_id,
    )


async def audit_admin_action(
    tenant_id: str,
    user_id: str,
    action: str,
    target_user_id: str | None = None,
    details: dict | None = None,
    correlation_id: str | None = None,
) -> AuditLog:
    """Log administrative actions"""
    return await audit_log(
        tenant_id=tenant_id,
        user_id=user_id,
        action=action,
        category=AuditCategory.ADMIN,
        severity=AuditSeverity.WARNING,
        resource_type="user" if target_user_id else None,
        resource_id=target_user_id,
        details=details,
        correlation_id=correlation_id,
    )


async def audit_security_event(
    tenant_id: str,
    user_id: str,
    action: str,
    ip_address: str | None = None,
    details: dict | None = None,
) -> AuditLog:
    """Log security-related events"""
    return await audit_log(
        tenant_id=tenant_id,
        user_id=user_id,
        action=action,
        category=AuditCategory.SECURITY,
        severity=AuditSeverity.WARNING,
        ip_address=ip_address,
        details=details,
        success=False,
    )


async def audit_permission_denied(
    tenant_id: str,
    user_id: str,
    permission: str,
    resource_type: str | None = None,
    resource_id: str | None = None,
    ip_address: str | None = None,
) -> AuditLog:
    """Log permission denial events"""
    return await audit_log(
        tenant_id=tenant_id,
        user_id=user_id,
        action=AuditAction.PERMISSION_DENIED,
        category=AuditCategory.ACCESS,
        severity=AuditSeverity.WARNING,
        resource_type=resource_type,
        resource_id=resource_id,
        ip_address=ip_address,
        details={"required_permission": permission},
        success=False,
        error_code="forbidden",
    )


# ─────────────────────────────────────────────────────────────────────────────
# Query Helpers
# ─────────────────────────────────────────────────────────────────────────────


async def get_user_audit_trail(
    tenant_id: str,
    user_id: str,
    limit: int = 100,
    category: str | None = None,
) -> list[AuditLog]:
    """Get audit logs for a specific user"""
    query = AuditLog.filter(tenant_id=tenant_id, user_id=user_id)
    if category:
        query = query.filter(category=category)
    return await query.order_by("-created_at").limit(limit)


async def get_resource_audit_trail(
    tenant_id: str,
    resource_type: str,
    resource_id: str,
    limit: int = 100,
) -> list[AuditLog]:
    """Get audit logs for a specific resource"""
    return (
        await AuditLog.filter(
            tenant_id=tenant_id,
            resource_type=resource_type,
            resource_id=resource_id,
        )
        .order_by("-created_at")
        .limit(limit)
    )


async def get_security_events(
    tenant_id: str,
    limit: int = 100,
) -> list[AuditLog]:
    """Get recent security events"""
    return (
        await AuditLog.filter(
            tenant_id=tenant_id,
            category=AuditCategory.SECURITY,
        )
        .order_by("-created_at")
        .limit(limit)
    )


async def get_failed_logins(
    tenant_id: str,
    hours: int = 24,
    limit: int = 100,
) -> list[AuditLog]:
    """Get failed login attempts"""
    cutoff = datetime.now(UTC) - timedelta(hours=hours)

    return (
        await AuditLog.filter(
            tenant_id=tenant_id,
            action=AuditAction.LOGIN_FAILED,
            created_at__gte=cutoff,
        )
        .order_by("-created_at")
        .limit(limit)
    )


# ─────────────────────────────────────────────────────────────────────────────
# Hash Chain Functions
# ─────────────────────────────────────────────────────────────────────────────


def compute_entry_hash(
    tenant_id: str,
    user_id: str,
    action: str,
    resource_type: str | None,
    resource_id: str | None,
    details: dict | None,
    prev_hash: str | None,
    timestamp: datetime,
) -> str:
    """
    Compute SHA-256 hash for an audit entry.

    Creates a deterministic hash from the entry's key fields
    to enable chain integrity verification.
    """
    # Build canonical string for hashing
    canonical_parts = [
        tenant_id,
        user_id,
        action,
        resource_type or "null",
        resource_id or "null",
        json.dumps(details or {}, sort_keys=True),
        prev_hash or "null",
        timestamp.isoformat() if timestamp else "null",
    ]
    canonical_string = "|".join(canonical_parts)

    # Compute SHA-256 hash
    return hashlib.sha256(canonical_string.encode("utf-8")).hexdigest()


async def get_last_entry_hash(tenant_id: str) -> str | None:
    """Get the hash of the most recent audit entry for a tenant."""
    last_entry = await AuditLog.filter(tenant_id=tenant_id).order_by("-created_at").first()
    return last_entry.entry_hash if last_entry else None


@dataclass
class HashChainValidationResult:
    """Result of hash chain validation."""

    valid: bool
    total_entries: int
    validated_entries: int
    invalid_entries: list[str]
    errors: list[str]

    def to_dict(self) -> dict:
        return {
            "valid": self.valid,
            "total_entries": self.total_entries,
            "validated_entries": self.validated_entries,
            "invalid_entries": self.invalid_entries,
            "errors": self.errors,
        }


async def validate_hash_chain(
    tenant_id: str,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> HashChainValidationResult:
    """
    Validate the hash chain integrity for a tenant's audit logs.

    Returns a validation result indicating whether the chain is intact
    and listing any tampered or missing entries.

    Args:
        tenant_id: The tenant to validate
        start_date: Optional start date filter
        end_date: Optional end date filter

    Returns:
        HashChainValidationResult with validation details
    """
    query = AuditLog.filter(tenant_id=tenant_id)

    if start_date:
        query = query.filter(created_at__gte=start_date)
    if end_date:
        query = query.filter(created_at__lte=end_date)

    entries = await query.order_by("created_at").all()

    result = HashChainValidationResult(
        valid=True,
        total_entries=len(entries),
        validated_entries=0,
        invalid_entries=[],
        errors=[],
    )

    if not entries:
        return result

    expected_prev_hash: str | None = None

    for entry in entries:
        # Skip entries without hash chain (legacy entries)
        if not entry.entry_hash:
            result.errors.append(f"Entry {entry.id}: Missing entry_hash (legacy entry)")
            continue

        # Verify prev_hash matches expected
        if entry.prev_hash != expected_prev_hash:
            result.valid = False
            result.invalid_entries.append(str(entry.id))
            result.errors.append(
                f"Entry {entry.id}: prev_hash mismatch. Expected '{expected_prev_hash}', got '{entry.prev_hash}'"
            )

        # Recompute and verify entry hash
        computed_hash = compute_entry_hash(
            tenant_id=entry.tenant_id,
            user_id=entry.user_id,
            action=entry.action,
            resource_type=entry.resource_type,
            resource_id=entry.resource_id,
            details=entry.details,
            prev_hash=entry.prev_hash,
            timestamp=entry.created_at,
        )

        if entry.entry_hash != computed_hash:
            result.valid = False
            result.invalid_entries.append(str(entry.id))
            result.errors.append(
                f"Entry {entry.id}: Hash mismatch. Stored '{entry.entry_hash}', computed '{computed_hash}'"
            )
        else:
            result.validated_entries += 1

        # Update expected prev_hash for next entry
        expected_prev_hash = entry.entry_hash

    return result


async def get_audit_chain_summary(tenant_id: str) -> dict:
    """
    Get a summary of the audit chain status for a tenant.

    Returns metrics about the chain including total entries,
    chain coverage, and last validation timestamp.
    """
    total_entries = await AuditLog.filter(tenant_id=tenant_id).count()
    entries_with_hash = await AuditLog.filter(
        tenant_id=tenant_id,
        entry_hash__not_isnull=True,
    ).count()

    first_entry = await AuditLog.filter(tenant_id=tenant_id).order_by("created_at").first()
    last_entry = await AuditLog.filter(tenant_id=tenant_id).order_by("-created_at").first()

    return {
        "tenant_id": tenant_id,
        "total_entries": total_entries,
        "entries_with_hash": entries_with_hash,
        "chain_coverage_percent": ((entries_with_hash / total_entries * 100) if total_entries > 0 else 0),
        "first_entry_date": first_entry.created_at.isoformat() if first_entry else None,
        "last_entry_date": last_entry.created_at.isoformat() if last_entry else None,
        "last_entry_hash": last_entry.entry_hash if last_entry else None,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Compliance Reporting
# ─────────────────────────────────────────────────────────────────────────────


async def get_compliance_report(
    tenant_id: str,
    start_date: datetime,
    end_date: datetime,
    framework: str = "general",
) -> dict:
    """
    Generate a compliance report for a tenant within a date range.

    Args:
        tenant_id: The tenant to report on
        start_date: Start of reporting period
        end_date: End of reporting period
        framework: Compliance framework (general, GDPR, SOC2, ISO27001)

    Returns:
        Compliance report dictionary
    """
    entries: list[AuditLog] = await AuditLog.filter(
        tenant_id=tenant_id,
        created_at__gte=start_date,
        created_at__lte=end_date,
    ).all()

    # Count by category - iterate over enum members explicitly
    category_counts: dict[str, int] = {}
    for cat in list(AuditCategory):
        category_counts[cat.value] = sum(1 for e in entries if e.category == cat.value)

    # Count by severity - iterate over enum members explicitly
    severity_counts: dict[str, int] = {}
    for sev in list(AuditSeverity):
        severity_counts[sev.value] = sum(1 for e in entries if e.severity == sev.value)

    # Failed events
    failed_events = [e for e in entries if not e.success]

    # Security events
    security_events = [e for e in entries if e.category == AuditCategory.SECURITY.value]

    # Unique users
    unique_users = len({e.user_id for e in entries})

    # Chain validation
    chain_validation = await validate_hash_chain(tenant_id, start_date, end_date)

    report = {
        "tenant_id": tenant_id,
        "report_generated": datetime.now(UTC).isoformat(),
        "period": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat(),
        },
        "framework": framework,
        "summary": {
            "total_events": len(entries),
            "failed_events": len(failed_events),
            "security_events": len(security_events),
            "unique_users": unique_users,
        },
        "by_category": category_counts,
        "by_severity": severity_counts,
        "chain_integrity": {
            "valid": chain_validation.valid,
            "validated_entries": chain_validation.validated_entries,
            "issues": len(chain_validation.errors),
        },
    }

    # Add framework-specific sections
    if framework == "GDPR":
        report["gdpr"] = await _get_gdpr_metrics(entries)
    elif framework == "SOC2":
        report["soc2"] = await _get_soc2_metrics(entries)
    elif framework == "ISO27001":
        report["iso27001"] = await _get_iso27001_metrics(entries)

    return report


async def _get_gdpr_metrics(entries: list[AuditLog]) -> dict:
    """Get GDPR-specific compliance metrics."""
    return {
        "data_access_events": sum(
            1 for e in entries if e.category == AuditCategory.DATA.value and "access" in e.action.lower()
        ),
        "data_export_events": sum(1 for e in entries if "export" in e.action.lower()),
        "data_deletion_events": sum(1 for e in entries if "delete" in e.action.lower()),
        "consent_events": sum(1 for e in entries if "consent" in e.action.lower()),
    }


async def _get_soc2_metrics(entries: list[AuditLog]) -> dict:
    """Get SOC 2-specific compliance metrics."""
    return {
        "access_control_events": sum(1 for e in entries if e.category == AuditCategory.ACCESS.value),
        "authentication_events": sum(1 for e in entries if e.category == AuditCategory.AUTH.value),
        "failed_access_attempts": sum(1 for e in entries if e.category == AuditCategory.ACCESS.value and not e.success),
        "admin_actions": sum(1 for e in entries if e.category == AuditCategory.ADMIN.value),
    }


async def _get_iso27001_metrics(entries: list[AuditLog]) -> dict:
    """Get ISO 27001-specific compliance metrics."""
    return {
        "security_incidents": sum(
            1
            for e in entries
            if e.category == AuditCategory.SECURITY.value
            and e.severity in [AuditSeverity.ERROR.value, AuditSeverity.CRITICAL.value]
        ),
        "access_reviews_completed": sum(1 for e in entries if "review" in e.action.lower()),
        "policy_violations": sum(1 for e in entries if "violation" in e.action.lower()),
        "configuration_changes": sum(
            1 for e in entries if e.category == AuditCategory.ADMIN.value and "config" in e.action.lower()
        ),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Export Functions
# ─────────────────────────────────────────────────────────────────────────────


async def export_audit_logs(
    tenant_id: str,
    start_date: datetime,
    end_date: datetime,
    format: str = "json",
) -> str | bytes:
    """
    Export audit logs in the specified format.

    Args:
        tenant_id: The tenant to export
        start_date: Start of export period
        end_date: End of export period
        format: Export format (json, csv)

    Returns:
        Exported data as string or bytes
    """
    entries = (
        await AuditLog.filter(
            tenant_id=tenant_id,
            created_at__gte=start_date,
            created_at__lte=end_date,
        )
        .order_by("created_at")
        .all()
    )

    if format == "json":
        return json.dumps(
            [
                {
                    "id": str(e.id),
                    "tenant_id": e.tenant_id,
                    "user_id": e.user_id,
                    "action": e.action,
                    "category": e.category,
                    "severity": e.severity,
                    "resource_type": e.resource_type,
                    "resource_id": e.resource_id,
                    "details": e.details,
                    "success": e.success,
                    "error_code": e.error_code,
                    "error_message": e.error_message,
                    "ip_address": e.ip_address,
                    "created_at": e.created_at.isoformat(),
                    "entry_hash": e.entry_hash,
                }
                for e in entries
            ],
            indent=2,
        )
    elif format == "csv":
        import csv
        import io

        output = io.StringIO()
        # nosemgrep: use-defusedcsv -- all values are internal audit record fields (ids, ISO timestamps, enum values), not user-authored formula content
        writer = csv.writer(output)
        writer.writerow(
            [
                "id",
                "tenant_id",
                "user_id",
                "action",
                "category",
                "severity",
                "resource_type",
                "resource_id",
                "success",
                "ip_address",
                "created_at",
                "entry_hash",
            ]
        )
        for e in entries:
            writer.writerow(
                [
                    str(e.id),
                    e.tenant_id,
                    e.user_id,
                    e.action,
                    e.category,
                    e.severity,
                    e.resource_type,
                    e.resource_id,
                    e.success,
                    e.ip_address,
                    e.created_at.isoformat(),
                    e.entry_hash,
                ]
            )
        return output.getvalue()
    else:
        raise ValueError(f"Unsupported export format: {format}")
