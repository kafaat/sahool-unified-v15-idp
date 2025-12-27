"""
SAHOOL Platform Authentication Module
Shared JWT authentication and authorization for Python (FastAPI) services
"""

from .config import JWTConfig, config
from .dependencies import (
    get_current_active_user,
    get_current_user,
    get_optional_user,
    rate_limit_dependency,
    require_farm_access,
    require_permissions,
    require_roles,
)
from .jwt_handler import (
    create_access_token,
    create_refresh_token,
    create_token_pair,
    decode_token,
    refresh_access_token,
    verify_token,
)
from .middleware import (
    JWTAuthMiddleware,
    RateLimitMiddleware,
    SecurityHeadersMiddleware,
    TenantContextMiddleware,
)
from .models import (
    AuthErrorMessage,
    AuthErrors,
    AuthException,
    Permission,
    TokenPayload,
    User,
)

__all__ = [
    # Configuration
    "JWTConfig",
    "config",
    # JWT Handler
    "create_access_token",
    "create_refresh_token",
    "create_token_pair",
    "verify_token",
    "decode_token",
    "refresh_access_token",
    # Dependencies
    "get_current_user",
    "get_current_active_user",
    "get_optional_user",
    "require_roles",
    "require_permissions",
    "require_farm_access",
    "rate_limit_dependency",
    # Middleware
    "JWTAuthMiddleware",
    "TenantContextMiddleware",
    "RateLimitMiddleware",
    "SecurityHeadersMiddleware",
    # Models
    "User",
    "TokenPayload",
    "Permission",
    "AuthException",
    "AuthErrors",
    "AuthErrorMessage",
]
