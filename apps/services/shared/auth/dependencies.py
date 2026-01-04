"""
FastAPI Authentication Dependencies
اعتماديات المصادقة لـ FastAPI
"""

import logging
from typing import Optional, List, Callable

from fastapi import Depends, HTTPException, Header, Security, status
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader

from .config import get_auth_config
from .jwt import decode_token, TokenData
from .models import User, UserStatus, SYSTEM_ROLES
from .rbac import get_permission_checker

logger = logging.getLogger(__name__)

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/token",
    auto_error=False,
)

# API Key authentication
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_token_data(
    token: Optional[str] = Depends(oauth2_scheme),
) -> Optional[TokenData]:
    """
    Extract and validate token data from request
    استخراج والتحقق من بيانات الرمز من الطلب
    """
    if not token:
        return None

    try:
        return decode_token(token)
    except ValueError as e:
        logger.warning(f"Invalid token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


async def get_current_user(
    token_data: Optional[TokenData] = Depends(get_token_data),
) -> User:
    """
    Get the current authenticated user
    الحصول على المستخدم المصادق عليه حالياً

    This is a simplified version that creates a User from token data.
    In production, you would fetch the full user from database.
    """
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

    # Create user from token data
    # In production, fetch from database using token_data.user_id
    roles = []
    for role_name in token_data.roles:
        if role_name in SYSTEM_ROLES:
            roles.append(SYSTEM_ROLES[role_name])

    user = User(
        id=token_data.user_id,
        email=token_data.email or "",
        hashed_password="",  # Not needed for authenticated user
        tenant_id=token_data.tenant_id,
        roles=roles,
        status=UserStatus.ACTIVE,
    )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current user and verify they are active
    الحصول على المستخدم الحالي والتحقق من أنه نشط
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account",
        )
    return current_user


async def get_optional_user(
    token_data: Optional[TokenData] = Depends(get_token_data),
) -> Optional[User]:
    """
    Get current user if authenticated, None otherwise
    الحصول على المستخدم الحالي إذا كان مصادقاً، وإلا None
    """
    if token_data is None:
        return None

    roles = []
    for role_name in token_data.roles:
        if role_name in SYSTEM_ROLES:
            roles.append(SYSTEM_ROLES[role_name])

    return User(
        id=token_data.user_id,
        email=token_data.email or "",
        hashed_password="",
        tenant_id=token_data.tenant_id,
        roles=roles,
        status=UserStatus.ACTIVE,
    )


def require_roles(allowed_roles: List[str]) -> Callable:
    """
    Dependency factory that requires user to have at least one of the roles
    مصنع اعتماديات يتطلب أن يكون لدى المستخدم دور واحد على الأقل

    Usage:
        @app.get("/admin")
        async def admin_route(user: User = Depends(require_roles(["admin", "super_admin"]))):
            ...
    """

    async def role_checker(
        current_user: User = Depends(get_current_active_user),
    ) -> User:
        if not current_user.has_any_role(allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User does not have required role. Required: {allowed_roles}",
            )
        return current_user

    return role_checker


def require_permissions(required_permissions: List[str]) -> Callable:
    """
    Dependency factory that requires user to have all specified permissions
    مصنع اعتماديات يتطلب أن يكون لدى المستخدم جميع الصلاحيات المحددة

    Usage:
        @app.post("/farms")
        async def create_farm(user: User = Depends(require_permissions(["farm:create"]))):
            ...
    """

    async def permission_checker(
        current_user: User = Depends(get_current_active_user),
    ) -> User:
        checker = get_permission_checker()

        for permission_id in required_permissions:
            if not checker.has_permission(current_user, permission_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Missing required permission: {permission_id}",
                )

        return current_user

    return permission_checker


def require_tenant_access(tenant_id_param: str = "tenant_id") -> Callable:
    """
    Dependency factory that verifies user can access the tenant
    مصنع اعتماديات يتحقق من أن المستخدم يمكنه الوصول إلى المستأجر

    Usage:
        @app.get("/tenants/{tenant_id}/data")
        async def get_tenant_data(
            tenant_id: str,
            user: User = Depends(require_tenant_access()),
        ):
            ...
    """

    async def tenant_checker(
        current_user: User = Depends(get_current_active_user),
        **kwargs,
    ) -> User:
        tenant_id = kwargs.get(tenant_id_param)

        if tenant_id and not current_user.can_access_tenant(tenant_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User cannot access this tenant",
            )

        return current_user

    return tenant_checker


async def api_key_auth(
    api_key: Optional[str] = Security(api_key_header),
) -> str:
    """
    Validate API key for service-to-service communication
    التحقق من صحة مفتاح API للاتصال بين الخدمات

    Usage:
        @app.get("/internal/data")
        async def internal_route(api_key: str = Depends(api_key_auth)):
            ...
    """
    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
        )

    config = get_auth_config()

    if api_key not in config.api_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    return api_key


async def get_tenant_id(
    current_user: User = Depends(get_current_user),
    x_tenant_id: Optional[str] = Header(None),
) -> str:
    """
    Get tenant ID from user or header
    الحصول على معرف المستأجر من المستخدم أو العنوان

    Super admins can override tenant using X-Tenant-ID header.
    """
    # Super admin can specify tenant via header
    if current_user.has_role("super_admin") and x_tenant_id:
        return x_tenant_id

    # Otherwise use user's tenant
    if current_user.tenant_id:
        return current_user.tenant_id

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Tenant ID not available",
    )


# ============================================
# Convenience dependencies for common patterns
# اعتماديات مريحة للأنماط الشائعة
# ============================================

# Admin access (tenant_admin or super_admin)
require_admin = require_roles(["tenant_admin", "super_admin"])

# Super admin only
require_super_admin = require_roles(["super_admin"])

# Farm management access
require_farm_access = require_roles(["super_admin", "tenant_admin", "farm_manager"])

# Field operations access
require_field_access = require_roles(
    ["super_admin", "tenant_admin", "farm_manager", "field_operator"]
)

# Any authenticated user
require_authenticated = get_current_active_user
