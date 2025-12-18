"""
SAHOOL Security Package
JWT, RBAC, Audit, and mTLS utilities for production-safe services
"""

from .deps import get_optional_principal, get_principal
from .guard import require, require_all, require_any
from .jwt import AuthError, create_token, verify_token
from .rbac import ROLE_PERMISSIONS, get_role_permissions, has_permission

# Lazy imports for audit module (requires tortoise-orm)
# Import these explicitly when needed: from shared.security.audit import audit_log, AuditAction


def __getattr__(name: str):
    """Lazy loading for audit module to avoid tortoise dependency at import time"""
    if name in ("audit_log", "AuditAction"):
        from .audit import AuditAction, audit_log

        globals()["audit_log"] = audit_log
        globals()["AuditAction"] = AuditAction
        return globals()[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__version__ = "15.3.3"

__all__ = [
    # JWT
    "verify_token",
    "create_token",
    "AuthError",
    # Dependencies
    "get_principal",
    "get_optional_principal",
    # RBAC
    "has_permission",
    "get_role_permissions",
    "ROLE_PERMISSIONS",
    # Guard
    "require",
    "require_any",
    "require_all",
    # Audit (lazy loaded)
    "audit_log",
    "AuditAction",
]
