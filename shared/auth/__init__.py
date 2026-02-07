"""
SAHOOL Platform Authentication Module
Shared JWT authentication and authorization for Python (FastAPI) services

Enhanced with:
- Database user validation
- Redis caching for performance
- User status checks (active, verified, deleted, suspended)
- Failed authentication logging
- Improved rate limiting
- Refresh Token Rotation with theft detection
- Token fingerprinting and binding
- Comprehensive session management
- Enhanced RBAC with hierarchical permissions
- Security audit logging
- Enhanced 2FA with rate limiting
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
from .revocation_middleware import (
    RevocationCheckDependency,
    TokenRevocationMiddleware,
)
from .service_auth import (
    ALLOWED_SERVICES,
    SERVICE_COMMUNICATION_MATRIX,
    ServiceCallAuditLog,
    ServiceCallRateLimiter,
    ServiceToken,
    ServiceTokenRevocationStore,
    check_service_call_rate_limit,
    create_service_token,
    get_allowed_targets,
    get_audit_log,
    get_rate_limiter,
    get_revocation_store,
    get_service_audit_logs,
    get_service_call_stats,
    is_service_authorized,
    is_service_token_revoked,
    log_service_call,
    revoke_service_token,
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
    is_token_revoked,
    revoke_all_user_tokens,
    revoke_token,
)
from .user_cache import (
    UserCache,
    close_user_cache,
    get_user_cache,
    init_user_cache,
)
from .user_repository import (
    InMemoryUserRepository,
    UserRepository,
    UserValidationData,
    get_user_repository,
    set_user_repository,
)

# Security Enhancements (New)
from .security_enhancements import (
    TokenFingerprint,
    TokenFamily,
    TokenFamilyStatus,
    RefreshTokenRotationManager,
    PasswordPepper,
    get_rotation_manager,
    get_password_pepper,
    create_fingerprint_hash,
    generate_secure_jti,
    generate_family_id,
    generate_secure_token,
    constant_time_compare,
)

# Session Management (New)
from .session_manager import (
    SessionInfo,
    SessionStatus,
    SessionManager,
    SessionSecurityChecker,
    get_session_manager,
    generate_session_id,
)

# Security Audit Logging (New)
from .security_audit import (
    SecurityEvent,
    SecurityEventType,
    SecurityEventSeverity,
    SecurityAuditLogger,
    get_security_audit_logger,
    audit_login_success,
    audit_login_failed,
    check_brute_force,
)

# Enhanced 2FA (New)
from .twofa_enhanced import (
    TwoFAMethod,
    TwoFAStatus,
    TwoFAConfig,
    EnhancedTwoFactorAuth,
    get_enhanced_2fa,
)

# Enhanced RBAC (New)
from .rbac_enhanced import (
    SystemRole,
    PermissionAction,
    ResourceType,
    AccessContext,
    AccessDecision,
    RBACManager,
    get_rbac_manager,
    require_permission,
    ROLE_HIERARCHY,
    DEFAULT_ROLE_PERMISSIONS,
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
    "ServiceTokenRevocationStore",
    "ServiceCallAuditLog",
    "ServiceCallRateLimiter",
    "create_service_token",
    "verify_service_token",
    "is_service_authorized",
    "get_allowed_targets",
    "ALLOWED_SERVICES",
    "SERVICE_COMMUNICATION_MATRIX",
    # Service Token Revocation
    "revoke_service_token",
    "is_service_token_revoked",
    "get_revocation_store",
    # Service Call Audit Logging
    "get_audit_log",
    "log_service_call",
    "get_service_audit_logs",
    # Service Call Rate Limiting
    "get_rate_limiter",
    "check_service_call_rate_limit",
    "get_service_call_stats",
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
    # Security Enhancements (New)
    "TokenFingerprint",
    "TokenFamily",
    "TokenFamilyStatus",
    "RefreshTokenRotationManager",
    "PasswordPepper",
    "get_rotation_manager",
    "get_password_pepper",
    "create_fingerprint_hash",
    "generate_secure_jti",
    "generate_family_id",
    "generate_secure_token",
    "constant_time_compare",
    # Session Management (New)
    "SessionInfo",
    "SessionStatus",
    "SessionManager",
    "SessionSecurityChecker",
    "get_session_manager",
    "generate_session_id",
    # Security Audit Logging (New)
    "SecurityEvent",
    "SecurityEventType",
    "SecurityEventSeverity",
    "SecurityAuditLogger",
    "get_security_audit_logger",
    "audit_login_success",
    "audit_login_failed",
    "check_brute_force",
    # Enhanced 2FA (New)
    "TwoFAMethod",
    "TwoFAStatus",
    "TwoFAConfig",
    "EnhancedTwoFactorAuth",
    "get_enhanced_2fa",
    # Enhanced RBAC (New)
    "SystemRole",
    "PermissionAction",
    "ResourceType",
    "AccessContext",
    "AccessDecision",
    "RBACManager",
    "get_rbac_manager",
    "require_permission",
    "ROLE_HIERARCHY",
    "DEFAULT_ROLE_PERMISSIONS",
]
