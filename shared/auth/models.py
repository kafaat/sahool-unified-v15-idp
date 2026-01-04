"""
Authentication Models for SAHOOL Platform
Shared data models for JWT authentication across all services
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


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
    """JWT Token Payload"""

    user_id: str
    roles: list[str]
    exp: datetime
    iat: datetime
    tenant_id: str | None = None
    jti: str | None = None  # Token ID for revocation
    token_type: str = "access"  # access or refresh
    permissions: list[str] = field(default_factory=list)

    def has_role(self, role: str) -> bool:
        """Check if user has a specific role"""
        return role in self.roles

    def has_any_role(self, *roles: str) -> bool:
        """Check if user has any of the specified roles"""
        return any(role in self.roles for role in roles)

    def has_all_roles(self, *roles: str) -> bool:
        """Check if user has all of the specified roles"""
        return all(role in self.roles for role in roles)

    def has_permission(self, permission: str) -> bool:
        """Check if user has a specific permission"""
        return permission in self.permissions


@dataclass
class User:
    """User model for authentication context"""

    id: str
    email: str
    roles: list[str]
    farm_ids: list[str] = field(default_factory=list)
    tenant_id: str | None = None
    permissions: list[str] = field(default_factory=list)
    is_active: bool = True
    is_verified: bool = True

    def has_role(self, role: str) -> bool:
        """Check if user has a specific role"""
        return role in self.roles

    def has_farm_access(self, farm_id: str) -> bool:
        """Check if user has access to a specific farm"""
        return farm_id in self.farm_ids

    def has_permission(self, permission: str) -> bool:
        """Check if user has a specific permission"""
        return permission in self.permissions


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
    """Base authentication exception"""

    def __init__(self, error: AuthErrorMessage, status_code: int = 401):
        self.error = error
        self.status_code = status_code
        super().__init__(error.en)

    def to_dict(self, lang: str = "en") -> dict:
        """Convert to dictionary for API response"""
        message = self.error.ar if lang == "ar" else self.error.en
        return {
            "error": self.error.code,
            "message": message,
            "status_code": self.status_code,
        }
