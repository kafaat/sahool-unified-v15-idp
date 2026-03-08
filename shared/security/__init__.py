"""
SAHOOL Security Package
JWT, RBAC, Audit, Token Revocation, and Policy Engine utilities
"""

from .audit import AuditAction, audit_log
from .jwt import AuthError, create_token, verify_token
from .policy_engine import (
    PolicyContext,
    PolicyDecision,
    PolicyEngine,
    PolicyResult,
    can_access,
    evaluate_policy,
    get_policy_engine,
)
from .rbac import ROLE_PERMISSIONS, get_role_permissions, has_permission
from .token_revocation import (
    TokenRevocationService,
    get_revocation_service,
    is_token_revoked,
    revoke_token,
    revoke_user_tokens,
)


def __getattr__(name: str):
    """Lazy import for FastAPI-dependent modules (deps, guard)."""
    _deps_attrs = {"get_principal", "get_optional_principal"}
    _guard_attrs = {"require", "require_any", "require_all"}

    if name in _deps_attrs:
        from . import deps

        return getattr(deps, name)
    if name in _guard_attrs:
        from . import guard

        return getattr(guard, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


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
