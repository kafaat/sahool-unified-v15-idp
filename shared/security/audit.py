"""
Audit Logging Service
Database + Event logging for security audit trail
"""

import logging
from datetime import UTC, datetime
from enum import Enum
from uuid import uuid4

from .audit_models import AuditCategory, AuditLog, AuditSeverity

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Audit Action Constants
# ─────────────────────────────────────────────────────────────────────────────


class AuditAction(str, Enum):
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
        f"AUDIT: {action} | tenant={tenant_id} user={user_id} "
        f"resource={resource_type}:{resource_id} success={success}",
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
    from datetime import timedelta

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
