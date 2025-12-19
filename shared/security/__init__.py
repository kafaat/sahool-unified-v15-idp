"""
SAHOOL Security Package
JWT, RBAC, Audit, Token Revocation, and Policy Engine utilities
"""

from .audit import AuditAction, audit_log
from .deps import get_optional_principal, get_principal
from .guard import require, require_all, require_any
from .jwt import AuthError, create_token, verify_token
from .rbac import ROLE_PERMISSIONS, get_role_permissions, has_permission
from .token_revocation import (
    TokenRevocationService,
    get_revocation_service,
    revoke_token,
    revoke_user_tokens,
    is_token_revoked,
)
from .policy_engine import (
    PolicyEngine,
    PolicyContext,
    PolicyResult,
    PolicyDecision,
    get_policy_engine,
    evaluate_policy,
    can_access,
)

__version__ = "15.4.0"

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
    # Token Revocation
    "TokenRevocationService",
    "get_revocation_service",
    "revoke_token",
    "revoke_user_tokens",
    "is_token_revoked",
    # Policy Engine
    "PolicyEngine",
    "PolicyContext",
    "PolicyResult",
    "PolicyDecision",
    "get_policy_engine",
    "evaluate_policy",
    "can_access",
]
