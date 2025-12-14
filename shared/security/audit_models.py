"""
Audit Log Database Models
Tortoise ORM models for security audit trail
"""

from enum import Enum

from tortoise import fields
from tortoise.models import Model


class AuditSeverity(str, Enum):
    """Audit event severity levels"""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AuditCategory(str, Enum):
    """Audit event categories"""

    AUTH = "auth"  # Login, logout, token refresh
    ACCESS = "access"  # Resource access
    DATA = "data"  # Data changes (CRUD)
    ADMIN = "admin"  # Administrative actions
    SECURITY = "security"  # Security events
    SYSTEM = "system"  # System events


class AuditLog(Model):
    """
    Security Audit Log

    Immutable record of security-relevant events.
    Indexed for fast queries on common access patterns.
    """

    id = fields.UUIDField(pk=True)

    # Identity
    tenant_id = fields.CharField(max_length=64, index=True)
    user_id = fields.CharField(max_length=64, index=True)

    # Action
    action = fields.CharField(max_length=128, index=True)
    category = fields.CharField(max_length=32, index=True)
    severity = fields.CharField(max_length=16, default="info")

    # Resource
    resource_type = fields.CharField(max_length=64, null=True, index=True)
    resource_id = fields.CharField(max_length=128, null=True)

    # Context
    correlation_id = fields.CharField(max_length=64, null=True, index=True)
    session_id = fields.CharField(max_length=64, null=True, index=True)

    # Request info
    ip_address = fields.CharField(max_length=64, null=True)
    user_agent = fields.TextField(null=True)
    request_method = fields.CharField(max_length=16, null=True)
    request_path = fields.CharField(max_length=512, null=True)

    # Details
    details = fields.JSONField(null=True)
    old_value = fields.JSONField(null=True)  # For data changes
    new_value = fields.JSONField(null=True)  # For data changes

    # Result
    success = fields.BooleanField(default=True)
    error_code = fields.CharField(max_length=64, null=True)
    error_message = fields.TextField(null=True)

    # Timestamp
    created_at = fields.DatetimeField(auto_now_add=True, index=True)

    class Meta:
        table = "security_audit_logs"
        indexes = [
            ("tenant_id", "created_at"),
            ("user_id", "created_at"),
            ("action", "created_at"),
            ("category", "created_at"),
            ("resource_type", "resource_id"),
        ]

    def __str__(self):
        return f"AuditLog({self.action} by {self.user_id})"


class AuditLogSummary(Model):
    """
    Aggregated audit statistics per tenant/day.
    Used for dashboards and reports.
    """

    id = fields.UUIDField(pk=True)
    tenant_id = fields.CharField(max_length=64, index=True)
    date = fields.DateField(index=True)

    # Counts
    total_events = fields.IntField(default=0)
    auth_events = fields.IntField(default=0)
    access_events = fields.IntField(default=0)
    data_events = fields.IntField(default=0)
    admin_events = fields.IntField(default=0)
    security_events = fields.IntField(default=0)

    # Failures
    failed_logins = fields.IntField(default=0)
    permission_denials = fields.IntField(default=0)

    # Active users
    unique_users = fields.IntField(default=0)
    unique_ips = fields.IntField(default=0)

    class Meta:
        table = "security_audit_summaries"
        unique_together = ("tenant_id", "date")


class SessionLog(Model):
    """
    User session tracking for security monitoring.
    """

    id = fields.UUIDField(pk=True)
    tenant_id = fields.CharField(max_length=64, index=True)
    user_id = fields.CharField(max_length=64, index=True)
    session_id = fields.CharField(max_length=64, unique=True, index=True)

    # Session info
    ip_address = fields.CharField(max_length=64, null=True)
    user_agent = fields.TextField(null=True)
    device_type = fields.CharField(max_length=32, null=True)

    # Timestamps
    started_at = fields.DatetimeField(auto_now_add=True)
    last_activity_at = fields.DatetimeField(null=True)
    ended_at = fields.DatetimeField(null=True)

    # Status
    is_active = fields.BooleanField(default=True)
    end_reason = fields.CharField(max_length=32, null=True)  # logout, expired, revoked

    class Meta:
        table = "security_sessions"
        indexes = [
            ("tenant_id", "user_id"),
            ("is_active", "last_activity_at"),
        ]
