"""
SAHOOL Security Package
JWT, RBAC, Audit, and mTLS utilities for production-safe services
"""

from .jwt import verify_token, create_token, AuthError
from .deps import get_principal, get_optional_principal
from .rbac import has_permission, get_role_permissions, ROLE_PERMISSIONS
from .guard import require, require_any, require_all
from .audit import audit_log, AuditAction

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
    # Audit
    "audit_log",
    "AuditAction",
]
