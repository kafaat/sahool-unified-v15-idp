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
from .service_auth import (
    ALLOWED_SERVICES,
    SERVICE_COMMUNICATION_MATRIX,
    ServiceToken,
    create_service_token,
    get_allowed_targets,
    is_service_authorized,
    verify_service_token,
)
from .service_middleware import (
    ServiceAuthMiddleware,
    get_calling_service,
    is_service_request,
    require_service_auth,
    verify_service_request,
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
    # Service-to-Service Authentication
    "ServiceToken",
    "create_service_token",
    "verify_service_token",
    "is_service_authorized",
    "get_allowed_targets",
    "ALLOWED_SERVICES",
    "SERVICE_COMMUNICATION_MATRIX",
    # Service Authentication Middleware
    "ServiceAuthMiddleware",
    "verify_service_request",
    "require_service_auth",
    "get_calling_service",
    "is_service_request",
]
