"""
SAHOOL Security Package
JWT, RBAC, Audit, and mTLS utilities for production-safe services
"""

from .audit import AuditAction, audit_log
from .deps import get_optional_principal, get_principal
from .guard import require, require_all, require_any
from .jwt import AuthError, create_token, verify_token
from .rbac import ROLE_PERMISSIONS, get_role_permissions, has_permission

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
