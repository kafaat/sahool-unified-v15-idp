"""
Authentication Models for SAHOOL Platform
==========================================
نماذج المصادقة لمنصة سهول

Shared data models for JWT authentication across all services.
Provides type-safe models for tokens, users, permissions, and errors.

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Sequence


class Permission(str, Enum):
    """Permission types for SAHOOL platform"""

    # Farm Management
    FARM_READ = "farm:read"
    FARM_WRITE = "farm:write"
    FARM_DELETE = "farm:delete"

    # Field Management
    FIELD_READ = "field:read"
    FIELD_WRITE = "field:write"
    FIELD_DELETE = "field:delete"

    # Crop Management
    CROP_READ = "crop:read"
    CROP_WRITE = "crop:write"
    CROP_DELETE = "crop:delete"

    # Weather & Climate
    WEATHER_READ = "weather:read"
    WEATHER_SUBSCRIBE = "weather:subscribe"

    # Advisory Services
    ADVISORY_READ = "advisory:read"
    ADVISORY_REQUEST = "advisory:request"

    # Analytics & Reports
    ANALYTICS_READ = "analytics:read"
    ANALYTICS_EXPORT = "analytics:export"

    # User Management
    USER_READ = "user:read"
    USER_WRITE = "user:write"
    USER_DELETE = "user:delete"

    # Admin Operations
    ADMIN_ACCESS = "admin:access"
    ADMIN_SETTINGS = "admin:settings"
    ADMIN_BILLING = "admin:billing"

    # Equipment Management
    EQUIPMENT_READ = "equipment:read"
    EQUIPMENT_WRITE = "equipment:write"
    EQUIPMENT_DELETE = "equipment:delete"

    # Precision Agriculture
    VRA_READ = "vra:read"
    VRA_WRITE = "vra:write"
    SPRAY_TIMING_READ = "spray:read"
    SPRAY_TIMING_WRITE = "spray:write"
    GDD_READ = "gdd:read"
    ROTATION_READ = "rotation:read"
    ROTATION_WRITE = "rotation:write"
    PROFITABILITY_READ = "profitability:read"


@dataclass
class TokenPayload:
    """
    JWT Token Payload model.
    نموذج حمولة رمز JWT

    Represents the decoded payload from a JWT token with role and permission
    checking capabilities.

    Attributes:
        user_id: Unique identifier for the user
        roles: List of role names assigned to the user
        exp: Token expiration timestamp
        iat: Token issued at timestamp
        tenant_id: Optional multi-tenant identifier
        jti: Token ID for revocation support
        token_type: Type of token ('access' or 'refresh')
        permissions: List of fine-grained permissions

    Example:
        >>> payload = TokenPayload(
        ...     user_id="user123",
        ...     roles=["farmer", "admin"],
        ...     exp=datetime.now() + timedelta(hours=1),
        ...     iat=datetime.now(),
        ...     permissions=["farm:read", "farm:write"]
        ... )
        >>> payload.has_role("admin")
        True
    """

    user_id: str
    roles: list[str]
    exp: datetime
    iat: datetime
    tenant_id: str | None = None
    jti: str | None = None
    token_type: str = "access"
    permissions: list[str] = field(default_factory=list)

    def has_role(self, role: str) -> bool:
        """
        Check if user has a specific role.

        Args:
            role: Role name to check

        Returns:
            True if user has the role, False otherwise
        """
        return role in self.roles

    def has_any_role(self, *roles: str) -> bool:
        """
        Check if user has any of the specified roles.

        Args:
            *roles: Variable number of role names to check

        Returns:
            True if user has at least one of the roles
        """
        return any(role in self.roles for role in roles)

    def has_all_roles(self, *roles: str) -> bool:
        """
        Check if user has all of the specified roles.

        Args:
            *roles: Variable number of role names to check

        Returns:
            True if user has all of the roles
        """
        return all(role in self.roles for role in roles)

    def has_permission(self, permission: str | Permission) -> bool:
        """
        Check if user has a specific permission.

        Args:
            permission: Permission name or Permission enum value

        Returns:
            True if user has the permission, False otherwise
        """
        perm_str = permission.value if isinstance(permission, Permission) else permission
        return perm_str in self.permissions

    def has_any_permission(self, *permissions: str | Permission) -> bool:
        """
        Check if user has any of the specified permissions.

        Args:
            *permissions: Variable number of permission names or enum values

        Returns:
            True if user has at least one of the permissions
        """
        return any(self.has_permission(p) for p in permissions)

    def is_expired(self) -> bool:
        """
        Check if the token is expired.

        Returns:
            True if token is expired, False otherwise
        """
        return datetime.now(tz=self.exp.tzinfo) > self.exp

    def to_dict(self) -> dict[str, Any]:
        """
        Convert token payload to dictionary.

        Returns:
            Dictionary representation of the token payload
        """
        return {
            "user_id": self.user_id,
            "roles": self.roles,
            "exp": self.exp.isoformat(),
            "iat": self.iat.isoformat(),
            "tenant_id": self.tenant_id,
            "jti": self.jti,
            "token_type": self.token_type,
            "permissions": self.permissions,
        }


@dataclass
class User:
    """
    User model for authentication context.
    نموذج المستخدم لسياق المصادقة

    Represents an authenticated user with their roles, permissions,
    and access rights across the SAHOOL platform.

    Attributes:
        id: Unique user identifier
        email: User's email address
        roles: List of role names assigned to the user
        farm_ids: List of farm IDs the user has access to
        tenant_id: Multi-tenant identifier
        permissions: Fine-grained permission list
        is_active: Whether the account is active
        is_verified: Whether the email is verified

    Example:
        >>> user = User(
        ...     id="user123",
        ...     email="farmer@example.com",
        ...     roles=["farmer"],
        ...     farm_ids=["farm1", "farm2"],
        ...     permissions=["farm:read", "field:write"]
        ... )
        >>> user.has_farm_access("farm1")
        True
    """

    id: str
    email: str
    roles: list[str]
    farm_ids: list[str] = field(default_factory=list)
    tenant_id: str | None = None
    permissions: list[str] = field(default_factory=list)
    is_active: bool = True
    is_verified: bool = True

    def has_role(self, role: str) -> bool:
        """
        Check if user has a specific role.

        Args:
            role: Role name to check

        Returns:
            True if user has the role
        """
        return role in self.roles

    def has_any_role(self, *roles: str) -> bool:
        """
        Check if user has any of the specified roles.

        Args:
            *roles: Variable number of role names

        Returns:
            True if user has at least one of the roles
        """
        return any(role in self.roles for role in roles)

    def has_farm_access(self, farm_id: str) -> bool:
        """
        Check if user has access to a specific farm.

        Args:
            farm_id: Farm identifier to check

        Returns:
            True if user has access to the farm
        """
        # Admins have access to all farms
        if self.has_role("admin"):
            return True
        return farm_id in self.farm_ids

    def has_permission(self, permission: str | Permission) -> bool:
        """
        Check if user has a specific permission.

        Args:
            permission: Permission name or Permission enum value

        Returns:
            True if user has the permission
        """
        perm_str = permission.value if isinstance(permission, Permission) else permission
        return perm_str in self.permissions

    def has_any_permission(self, *permissions: str | Permission) -> bool:
        """
        Check if user has any of the specified permissions.

        Args:
            *permissions: Variable number of permissions

        Returns:
            True if user has at least one of the permissions
        """
        return any(self.has_permission(p) for p in permissions)

    def can_access_resource(
        self,
        resource_type: str,
        action: str = "read",
        farm_id: str | None = None,
    ) -> bool:
        """
        Check if user can perform an action on a resource.

        Args:
            resource_type: Type of resource (farm, field, crop, etc.)
            action: Action to perform (read, write, delete)
            farm_id: Optional farm ID for farm-scoped resources

        Returns:
            True if user has access

        Example:
            >>> user.can_access_resource("field", "write", farm_id="farm1")
            True
        """
        # Check farm access if provided
        if farm_id and not self.has_farm_access(farm_id):
            return False

        # Build permission string
        permission = f"{resource_type}:{action}"
        return self.has_permission(permission)

    def to_dict(self) -> dict[str, Any]:
        """
        Convert user to dictionary.

        Returns:
            Dictionary representation of the user
        """
        return {
            "id": self.id,
            "email": self.email,
            "roles": self.roles,
            "farm_ids": self.farm_ids,
            "tenant_id": self.tenant_id,
            "permissions": self.permissions,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
        }

    def __repr__(self) -> str:
        """Return string representation of user."""
        return f"User(id={self.id!r}, email={self.email!r}, roles={self.roles!r})"


@dataclass
class AuthErrorMessage:
    """Authentication error messages in Arabic and English"""

    en: str
    ar: str
    code: str


# Error Messages
class AuthErrors:
    """Authentication error messages"""

    INVALID_TOKEN = AuthErrorMessage(
        en="Invalid authentication token",
        ar="رمز المصادقة غير صالح",
        code="invalid_token",
    )

    EXPIRED_TOKEN = AuthErrorMessage(
        en="Authentication token has expired",
        ar="انتهت صلاحية رمز المصادقة",
        code="expired_token",
    )

    MISSING_TOKEN = AuthErrorMessage(
        en="Authentication token is missing",
        ar="رمز المصادقة مفقود",
        code="missing_token",
    )

    INVALID_CREDENTIALS = AuthErrorMessage(
        en="Invalid credentials provided",
        ar="بيانات الاعتماد المقدمة غير صحيحة",
        code="invalid_credentials",
    )

    INSUFFICIENT_PERMISSIONS = AuthErrorMessage(
        en="Insufficient permissions to access this resource",
        ar="أذونات غير كافية للوصول إلى هذا المورد",
        code="insufficient_permissions",
    )

    ACCOUNT_DISABLED = AuthErrorMessage(
        en="User account has been disabled",
        ar="تم تعطيل حساب المستخدم",
        code="account_disabled",
    )

    ACCOUNT_NOT_VERIFIED = AuthErrorMessage(
        en="User account is not verified",
        ar="حساب المستخدم غير موثق",
        code="account_not_verified",
    )

    TOKEN_REVOKED = AuthErrorMessage(
        en="Authentication token has been revoked",
        ar="تم إلغاء رمز المصادقة",
        code="token_revoked",
    )

    RATE_LIMIT_EXCEEDED = AuthErrorMessage(
        en="Too many requests. Please try again later",
        ar="طلبات كثيرة جدا. الرجاء المحاولة مرة أخرى لاحقا",
        code="rate_limit_exceeded",
    )

    INVALID_ISSUER = AuthErrorMessage(
        en="Invalid token issuer", ar="مصدر الرمز غير صالح", code="invalid_issuer"
    )

    INVALID_AUDIENCE = AuthErrorMessage(
        en="Invalid token audience", ar="جمهور الرمز غير صالح", code="invalid_audience"
    )


class AuthException(Exception):
    """
    Base authentication exception for SAHOOL platform.
    استثناء المصادقة الأساسي لمنصة سهول

    Provides bilingual error messages and standardized error response
    formatting for API responses.

    Attributes:
        error: Error message object with code and bilingual messages
        status_code: HTTP status code for the response
        details: Optional additional error details

    Example:
        >>> raise AuthException(AuthErrors.INVALID_TOKEN)
        >>> raise AuthException(AuthErrors.EXPIRED_TOKEN, status_code=401)
    """

    def __init__(
        self,
        error: AuthErrorMessage,
        status_code: int = 401,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.error = error
        self.status_code = status_code
        self.details = details or {}
        super().__init__(error.en)

    def to_dict(self, lang: str = "en") -> dict[str, Any]:
        """
        Convert exception to dictionary for API response.

        Args:
            lang: Language code ('en' for English, 'ar' for Arabic)

        Returns:
            Dictionary with error code, message, and status code
        """
        message = self.error.ar if lang == "ar" else self.error.en
        result: dict[str, Any] = {
            "error": self.error.code,
            "message": message,
            "status_code": self.status_code,
        }
        if self.details:
            result["details"] = self.details
        return result

    def to_http_response(self, lang: str = "en") -> dict[str, Any]:
        """
        Convert to standardized HTTP error response format.

        Args:
            lang: Language code for the message

        Returns:
            Dictionary suitable for JSONResponse
        """
        return {
            "success": False,
            "error": self.to_dict(lang),
        }

    def __repr__(self) -> str:
        """Return detailed string representation."""
        return f"AuthException(code={self.error.code!r}, status={self.status_code})"
