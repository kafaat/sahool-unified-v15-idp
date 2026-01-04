"""
FastAPI Security Dependencies
Authentication and authorization dependencies for route handlers
"""

import logging
from typing import Annotated

from fastapi import Depends, Header, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .jwt import AuthError, verify_token

logger = logging.getLogger(__name__)

# HTTP Bearer scheme for OpenAPI docs
bearer_scheme = HTTPBearer(auto_error=False)


# ─────────────────────────────────────────────────────────────────────────────
# Principal Dependencies
# ─────────────────────────────────────────────────────────────────────────────


async def get_principal(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    """
    Extract and verify the authenticated principal from JWT.

    Usage:
        @app.get("/protected")
        async def protected_route(principal: dict = Depends(get_principal)):
            user_id = principal["sub"]
            tenant_id = principal["tid"]
            ...

    Raises:
        HTTPException 401 if token is missing or invalid
    """
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail={
                "error": "missing_token",
                "message_ar": "رمز المصادقة مفقود",
                "message_en": "Authentication token is required",
            },
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = verify_token(credentials.credentials)

        # Attach to request state for audit logging
        request.state.principal = payload
        request.state.user_id = payload.get("sub")
        request.state.tenant_id = payload.get("tid")

        return payload

    except AuthError as e:
        logger.warning(f"Authentication failed: {e.message}")
        raise HTTPException(
            status_code=401,
            detail={
                "error": e.code,
                "message_ar": "رمز المصادقة غير صالح",
                "message_en": e.message,
            },
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_optional_principal(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict | None:
    """
    Extract principal if present, but don't require it.

    Useful for endpoints that behave differently for authenticated vs anonymous users.
    """
    if credentials is None:
        return None

    try:
        payload = verify_token(credentials.credentials)
        request.state.principal = payload
        request.state.user_id = payload.get("sub")
        request.state.tenant_id = payload.get("tid")
        return payload
    except AuthError:
        return None


# ─────────────────────────────────────────────────────────────────────────────
# Tenant Dependencies
# ─────────────────────────────────────────────────────────────────────────────


async def get_tenant_id(principal: dict = Depends(get_principal)) -> str:
    """
    Extract tenant ID from authenticated principal.

    Usage:
        @app.get("/tenant-resource")
        async def get_resource(tenant_id: str = Depends(get_tenant_id)):
            ...
    """
    return principal.get("tid", "")


async def get_user_id(principal: dict = Depends(get_principal)) -> str:
    """
    Extract user ID from authenticated principal.
    """
    return principal.get("sub", "")


# ─────────────────────────────────────────────────────────────────────────────
# Header-based Tenant (for service-to-service)
# ─────────────────────────────────────────────────────────────────────────────


async def get_tenant_from_header(
    x_tenant_id: str = Header(None, alias="X-Tenant-ID"),
    principal: dict | None = Depends(get_optional_principal),
) -> str:
    """
    Get tenant ID from either JWT or X-Tenant-ID header.
    JWT takes precedence.
    """
    if principal:
        return principal.get("tid", "")
    if x_tenant_id:
        return x_tenant_id
    raise HTTPException(
        status_code=400,
        detail={
            "error": "missing_tenant",
            "message_ar": "معرف المستأجر مطلوب",
            "message_en": "Tenant ID is required",
        },
    )


# ─────────────────────────────────────────────────────────────────────────────
# API Key Authentication (for external integrations)
# ─────────────────────────────────────────────────────────────────────────────


async def get_api_key(
    x_api_key: str = Header(None, alias="X-API-Key"),
) -> str | None:
    """
    Extract API key from header for external integrations.
    Validation should be done by the service.
    """
    return x_api_key


async def require_api_key(
    api_key: str = Depends(get_api_key),
) -> str:
    """
    Require API key to be present.
    """
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail={
                "error": "missing_api_key",
                "message_ar": "مفتاح API مطلوب",
                "message_en": "API key is required",
            },
        )
    return api_key


# ─────────────────────────────────────────────────────────────────────────────
# Type Aliases
# ─────────────────────────────────────────────────────────────────────────────

Principal = Annotated[dict, Depends(get_principal)]
OptionalPrincipal = Annotated[dict | None, Depends(get_optional_principal)]
TenantID = Annotated[str, Depends(get_tenant_id)]
UserID = Annotated[str, Depends(get_user_id)]
