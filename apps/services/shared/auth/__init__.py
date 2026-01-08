"""
SAHOOL Shared Authentication & Authorization Layer
طبقة المصادقة والتفويض المشتركة
"""

from .config import AuthConfig
from .dependencies import (
    api_key_auth,
    get_current_active_user,
    get_current_user,
    oauth2_scheme,
    require_permissions,
    require_roles,
)
from .jwt import (
    TokenData,
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_jti,
    verify_token,
)
from .models import Permission, Role, User
from .password import hash_password, verify_password
from .rbac import PermissionChecker, RBACManager
from .revocation_middleware import (
    TokenRevocationMiddleware,
    check_token_revocation,
)
from .token_revocation import (
    RedisTokenRevocationStore,
    RevocationCheckResult,
    RevocationInfo,
    RevocationStats,
    get_revocation_store,
)

__all__ = [
    # Config
    "AuthConfig",
    # JWT
    "create_access_token",
    "create_refresh_token",
    "verify_token",
    "decode_token",
    "generate_jti",
    "TokenData",
    # Dependencies
    "get_current_user",
    "get_current_active_user",
    "require_roles",
    "require_permissions",
    "api_key_auth",
    "oauth2_scheme",
    # Models
    "User",
    "Role",
    "Permission",
    # Password
    "hash_password",
    "verify_password",
    # RBAC
    "RBACManager",
    "PermissionChecker",
    # Token Revocation
    "RedisTokenRevocationStore",
    "RevocationInfo",
    "RevocationCheckResult",
    "RevocationStats",
    "get_revocation_store",
    "TokenRevocationMiddleware",
    "check_token_revocation",
]
