"""
SAHOOL Shared Authentication & Authorization Layer
طبقة المصادقة والتفويض المشتركة
"""

from .config import AuthConfig
from .jwt import (
    create_access_token,
    create_refresh_token,
    verify_token,
    decode_token,
    TokenData,
)
from .dependencies import (
    get_current_user,
    get_current_active_user,
    require_roles,
    require_permissions,
    api_key_auth,
    oauth2_scheme,
)
from .models import User, Role, Permission
from .password import hash_password, verify_password
from .rbac import RBACManager, PermissionChecker

__all__ = [
    # Config
    "AuthConfig",
    # JWT
    "create_access_token",
    "create_refresh_token",
    "verify_token",
    "decode_token",
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
]
