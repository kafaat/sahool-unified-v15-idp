"""
Token Revocation API Endpoints
نقاط نهاية API لإلغاء الرموز

Provides REST API endpoints for token revocation operations.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field

from .dependencies import get_current_user
from .jwt_handler import verify_token
from .models import User
from .token_revocation import get_revocation_store

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Request/Response Models
# ─────────────────────────────────────────────────────────────────────────────


class RevokeTokenRequest(BaseModel):
    """Request to revoke a single token"""

    jti: str = Field(..., description="JWT ID to revoke")
    reason: str | None = Field("manual", description="Reason for revocation")

    class Config:
        json_schema_extra = {
            "example": {
                "jti": "550e8400-e29b-41d4-a716-446655440000",
                "reason": "user_logout",
            }
        }


class RevokeUserTokensRequest(BaseModel):
    """Request to revoke all tokens for a user"""

    user_id: str = Field(..., description="User ID")
    reason: str | None = Field("manual", description="Reason for revocation")

    class Config:
        json_schema_extra = {"example": {"user_id": "user-123", "reason": "password_change"}}


class RevokeTenantTokensRequest(BaseModel):
    """Request to revoke all tokens for a tenant"""

    tenant_id: str = Field(..., description="Tenant ID")
    reason: str | None = Field("security", description="Reason for revocation")

    class Config:
        json_schema_extra = {"example": {"tenant_id": "tenant-456", "reason": "security_breach"}}


class RevocationResponse(BaseModel):
    """Response for revocation operations"""

    success: bool = Field(..., description="Whether operation succeeded")
    message: str = Field(..., description="Response message")
    revoked_count: int | None = Field(None, description="Number of tokens revoked")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Token revoked successfully",
                "revoked_count": 1,
            }
        }


class TokenStatusResponse(BaseModel):
    """Response for token status check"""

    is_revoked: bool = Field(..., description="Whether token is revoked")
    reason: str | None = Field(None, description="Revocation reason")
    revoked_at: float | None = Field(None, description="When token was revoked")

    class Config:
        json_schema_extra = {
            "example": {
                "is_revoked": True,
                "reason": "user_logout",
                "revoked_at": 1640000000.0,
            }
        }


class RevocationStatsResponse(BaseModel):
    """Response for revocation statistics"""

    initialized: bool = Field(..., description="Store initialization status")
    revoked_tokens: int = Field(..., description="Number of revoked tokens")
    revoked_users: int = Field(..., description="Number of users with revoked tokens")
    revoked_tenants: int = Field(..., description="Number of tenants with revoked tokens")
    redis_url: str | None = Field(None, description="Redis connection URL (masked)")

    class Config:
        json_schema_extra = {
            "example": {
                "initialized": True,
                "revoked_tokens": 42,
                "revoked_users": 10,
                "revoked_tenants": 2,
                "redis_url": "localhost:6379/0",
            }
        }


# ─────────────────────────────────────────────────────────────────────────────
# API Router
# ─────────────────────────────────────────────────────────────────────────────

router = APIRouter(
    prefix="/auth/revocation",
    tags=["Token Revocation"],
)


@router.post(
    "/revoke",
    response_model=RevocationResponse,
    status_code=status.HTTP_200_OK,
    summary="Revoke a single token",
    description="Revoke a specific token by its JTI (JWT ID)",
)
async def revoke_token_endpoint(
    request: RevokeTokenRequest,
    current_user: User = Depends(get_current_user),
) -> RevocationResponse:
    """
    Revoke a single token by JTI.
    إلغاء رمز واحد بواسطة JTI.

    This endpoint requires authentication. Users can only revoke their own tokens
    unless they have admin privileges.
    """
    try:
        store = await get_revocation_store()

        success = await store.revoke_token(
            jti=request.jti,
            reason=request.reason,
            user_id=current_user.id,
        )

        if success:
            return RevocationResponse(
                success=True,
                message="Token revoked successfully",
                revoked_count=1,
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to revoke token",
            )

    except Exception as e:
        logger.error(f"Error revoking token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to revoke token: {str(e)}",
        )


@router.post(
    "/revoke-current",
    response_model=RevocationResponse,
    status_code=status.HTTP_200_OK,
    summary="Revoke current token",
    description="Revoke the currently authenticated token (logout)",
)
async def revoke_current_token(
    request: Request,
    current_user: User = Depends(get_current_user),
) -> RevocationResponse:
    """
    Revoke the current token (logout).
    إلغاء الرمز الحالي (تسجيل الخروج).

    This endpoint revokes the token used to authenticate this request.
    """
    try:
        # Extract token from request
        authorization = request.headers.get("Authorization")
        if not authorization:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No token provided")

        # Extract JTI from token
        token = authorization.split(" ")[1]
        payload = verify_token(token)

        if not payload.jti:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token does not have JTI claim",
            )

        # Revoke token
        store = await get_revocation_store()
        success = await store.revoke_token(
            jti=payload.jti,
            reason="user_logout",
            user_id=current_user.id,
        )

        if success:
            return RevocationResponse(
                success=True,
                message="Successfully logged out",
                revoked_count=1,
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to logout",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error revoking current token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to logout: {str(e)}",
        )


@router.post(
    "/revoke-user-tokens",
    response_model=RevocationResponse,
    status_code=status.HTTP_200_OK,
    summary="Revoke all user tokens",
    description="Revoke all tokens for a specific user",
)
async def revoke_user_tokens_endpoint(
    request: RevokeUserTokensRequest,
    current_user: User = Depends(get_current_user),
) -> RevocationResponse:
    """
    Revoke all tokens for a user.
    إلغاء جميع رموز المستخدم.

    Users can only revoke their own tokens. Admins can revoke any user's tokens.
    """
    # Check authorization
    is_admin = "admin" in current_user.roles or "superadmin" in current_user.roles

    if request.user_id != current_user.id and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only revoke your own tokens",
        )

    try:
        store = await get_revocation_store()

        success = await store.revoke_all_user_tokens(
            user_id=request.user_id,
            reason=request.reason,
        )

        if success:
            return RevocationResponse(
                success=True,
                message=f"All tokens revoked for user {request.user_id}",
                revoked_count=None,  # Unknown count
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to revoke user tokens",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error revoking user tokens: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to revoke user tokens: {str(e)}",
        )


@router.post(
    "/revoke-all",
    response_model=RevocationResponse,
    status_code=status.HTTP_200_OK,
    summary="Revoke all current user's tokens",
    description="Revoke all tokens for the currently authenticated user",
)
async def revoke_all_current_user_tokens(
    current_user: User = Depends(get_current_user),
    reason: str = "user_logout_all",
) -> RevocationResponse:
    """
    Revoke all tokens for the current user.
    إلغاء جميع رموز المستخدم الحالي.

    This logs the user out from all devices.
    """
    try:
        store = await get_revocation_store()

        success = await store.revoke_all_user_tokens(
            user_id=current_user.id,
            reason=reason,
        )

        if success:
            return RevocationResponse(
                success=True,
                message="All your tokens have been revoked. Logged out from all devices.",
                revoked_count=None,
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to revoke all tokens",
            )

    except Exception as e:
        logger.error(f"Error revoking all user tokens: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to revoke all tokens: {str(e)}",
        )


@router.post(
    "/revoke-tenant-tokens",
    response_model=RevocationResponse,
    status_code=status.HTTP_200_OK,
    summary="Revoke all tenant tokens (Admin only)",
    description="Revoke all tokens for a specific tenant (requires admin privileges)",
)
async def revoke_tenant_tokens_endpoint(
    request: RevokeTenantTokensRequest,
    current_user: User = Depends(get_current_user),
) -> RevocationResponse:
    """
    Revoke all tokens for a tenant.
    إلغاء جميع رموز المستأجر.

    This endpoint requires admin or superadmin role.
    Use with caution - affects all users in the tenant.
    """
    # Check admin authorization
    is_admin = "admin" in current_user.roles or "superadmin" in current_user.roles

    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required"
        )

    try:
        store = await get_revocation_store()

        success = await store.revoke_all_tenant_tokens(
            tenant_id=request.tenant_id,
            reason=request.reason,
        )

        if success:
            return RevocationResponse(
                success=True,
                message=f"All tokens revoked for tenant {request.tenant_id}",
                revoked_count=None,
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to revoke tenant tokens",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error revoking tenant tokens: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to revoke tenant tokens: {str(e)}",
        )


@router.get(
    "/status/{jti}",
    response_model=TokenStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Check token status",
    description="Check if a specific token is revoked",
)
async def check_token_status(
    jti: str,
    current_user: User = Depends(get_current_user),
) -> TokenStatusResponse:
    """
    Check if a token is revoked.
    التحقق من إلغاء الرمز.

    Returns revocation status and details.
    """
    try:
        store = await get_revocation_store()

        # Check if token is revoked
        is_revoked = await store.is_token_revoked(jti)

        # Get revocation info if revoked
        info = None
        if is_revoked:
            info = await store.get_revocation_info(jti)

        return TokenStatusResponse(
            is_revoked=is_revoked,
            reason=info.get("reason") if info else None,
            revoked_at=info.get("revoked_at") if info else None,
        )

    except Exception as e:
        logger.error(f"Error checking token status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check token status: {str(e)}",
        )


@router.get(
    "/stats",
    response_model=RevocationStatsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get revocation statistics (Admin only)",
    description="Get statistics about revoked tokens",
)
async def get_revocation_stats(
    current_user: User = Depends(get_current_user),
) -> RevocationStatsResponse:
    """
    Get revocation statistics.
    الحصول على إحصائيات الإلغاء.

    This endpoint requires admin or superadmin role.
    """
    # Check admin authorization
    is_admin = "admin" in current_user.roles or "superadmin" in current_user.roles

    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required"
        )

    try:
        store = await get_revocation_store()
        stats = await store.get_stats()

        return RevocationStatsResponse(**stats)

    except Exception as e:
        logger.error(f"Error getting revocation stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get revocation stats: {str(e)}",
        )


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description="Check if token revocation service is healthy",
)
async def health_check() -> dict:
    """
    Check token revocation service health.
    التحقق من صحة خدمة إلغاء الرموز.

    Returns health status of the Redis connection.
    """
    try:
        store = await get_revocation_store()
        is_healthy = await store.health_check()

        if is_healthy:
            return {
                "status": "healthy",
                "service": "token_revocation",
                "redis": "connected",
            }
        else:
            return {
                "status": "unhealthy",
                "service": "token_revocation",
                "redis": "disconnected",
            }

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "service": "token_revocation", "error": str(e)}


# Export router for inclusion in main app
__all__ = ["router"]
