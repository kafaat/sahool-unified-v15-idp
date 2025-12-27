"""
SAHOOL Platform Authentication Module
Shared JWT authentication and authorization for Python (FastAPI) services

Enhanced with:
- Database user validation
- Redis caching for performance
- User status checks (active, verified, deleted, suspended)
- Failed authentication logging
- Improved rate limiting
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
from .user_cache import (
    UserCache,
    get_user_cache,
    init_user_cache,
    close_user_cache,
)
from .user_repository import (
    UserRepository,
    UserValidationData,
    InMemoryUserRepository,
    get_user_repository,
    set_user_repository,
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
from .token_revocation import (
    RedisTokenRevocationStore,
    get_revocation_store,
    revoke_token,
    revoke_all_user_tokens,
    is_token_revoked,
)
from .revocation_middleware import (
    TokenRevocationMiddleware,
    RevocationCheckDependency,
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
    # User Cache
    "UserCache",
    "get_user_cache",
    "init_user_cache",
    "close_user_cache",
    # User Repository
    "UserRepository",
    "UserValidationData",
    "InMemoryUserRepository",
    "get_user_repository",
    "set_user_repository",
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
    # Token Revocation
    "RedisTokenRevocationStore",
    "get_revocation_store",
    "revoke_token",
    "revoke_all_user_tokens",
    "is_token_revoked",
    "TokenRevocationMiddleware",
    "RevocationCheckDependency",
]
