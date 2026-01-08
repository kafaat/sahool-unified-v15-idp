"""
Token Revocation Usage Examples for FastAPI
أمثلة استخدام إلغاء الرموز لـ FastAPI

Complete working examples showing how to implement token revocation
in your authentication endpoints.
"""

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel

from .dependencies import get_current_user, get_token_data
from .jwt import TokenData, create_access_token, create_refresh_token, decode_token
from .models import User
from .token_revocation import get_revocation_store

# Create router for auth endpoints
router = APIRouter(prefix="/auth", tags=["Authentication"])


# ============================================
# Request/Response Models
# ============================================


class LoginRequest(BaseModel):
    """Login request"""

    email: str
    password: str


class LoginResponse(BaseModel):
    """Login response with tokens"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 1800  # 30 minutes


class RefreshRequest(BaseModel):
    """Refresh token request"""

    refresh_token: str


class LogoutResponse(BaseModel):
    """Logout response"""

    message: str
    revoked: bool


# ============================================
# Authentication Endpoints with Revocation
# ============================================


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Login and issue tokens with JTI tracking

    This endpoint:
    1. Validates user credentials
    2. Issues access and refresh tokens with JTI
    3. Returns tokens to client

    In production, you should:
    - Verify password hash
    - Check user status (active, suspended)
    - Rate limit login attempts
    - Log login events
    """
    # TODO: Replace with actual user authentication
    # For example purposes, we skip actual password verification
    user_id = "user_123"
    email = request.email
    tenant_id = "tenant_456"
    roles = ["farmer"]

    # Create access token with JTI
    access_token, access_jti = create_access_token(
        user_id=user_id,
        email=email,
        tenant_id=tenant_id,
        roles=roles,
        expires_delta=timedelta(minutes=30),
    )

    # Create refresh token with JTI and family ID
    refresh_token, refresh_jti, family_id = create_refresh_token(
        user_id=user_id,
        tenant_id=tenant_id,
        expires_delta=timedelta(days=7),
    )

    # Optional: Store token metadata in database for audit trail
    # await store_token_metadata(
    #     user_id=user_id,
    #     access_jti=access_jti,
    #     refresh_jti=refresh_jti,
    #     family_id=family_id,
    # )

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=1800,
    )


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user)],
    token_data: Annotated[TokenData, Depends(get_token_data)],
):
    """
    Logout and revoke the current access token

    This endpoint:
    1. Gets the current token's JTI
    2. Adds it to the revocation list
    3. Token becomes invalid immediately

    Best practice: Also revoke the associated refresh token if available
    """
    revocation_store = get_revocation_store()

    # Ensure store is initialized
    if not revocation_store._initialized:
        await revocation_store.initialize()

    revoked = False

    # Revoke the current access token
    if token_data.jti:
        revoked = await revocation_store.revoke_token(
            jti=token_data.jti,
            expires_in=1800,  # Longer than token lifetime
            reason="user_logout",
            user_id=current_user.id,
            tenant_id=current_user.tenant_id,
        )

    return LogoutResponse(
        message="Logged out successfully" if revoked else "Logout processed",
        revoked=revoked,
    )


@router.post("/refresh", response_model=LoginResponse)
async def refresh_token_endpoint(request: Request, body: RefreshRequest):
    """
    Refresh access token using refresh token

    This implements secure refresh token rotation:
    1. Validates the refresh token
    2. Checks if token/family is revoked
    3. Revokes the old refresh token
    4. Issues new access and refresh tokens
    5. Keeps the same token family for tracking

    If token reuse is detected:
    - Revokes entire token family
    - Forces user to re-authenticate
    """
    revocation_store = get_revocation_store()

    if not revocation_store._initialized:
        await revocation_store.initialize()

    try:
        # Decode and validate refresh token
        token_data = decode_token(body.refresh_token)

        if token_data.token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token type. Expected refresh token.",
            )

        # Check if token is revoked
        result = await revocation_store.is_revoked(
            jti=token_data.jti,
            family_id=token_data.family_id,
            user_id=token_data.user_id,
            issued_at=token_data.iat.timestamp() if token_data.iat else None,
        )

        if result.is_revoked:
            # Token was already used! This is a security issue.
            # Revoke the entire token family to invalidate all related tokens
            if token_data.family_id:
                await revocation_store.revoke_token_family(
                    family_id=token_data.family_id,
                    reason="token_reuse_detected",
                )

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked. Possible security issue detected.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Revoke the old refresh token (it's now been used)
        if token_data.jti:
            await revocation_store.revoke_token(
                jti=token_data.jti,
                expires_in=86400 * 7,  # 7 days
                reason="refresh_rotation",
                user_id=token_data.user_id,
            )

        # Issue new tokens with the same family_id
        new_access_token, access_jti = create_access_token(
            user_id=token_data.user_id,
            email=token_data.email,
            tenant_id=token_data.tenant_id,
            roles=token_data.roles,
            permissions=token_data.permissions,
            expires_delta=timedelta(minutes=30),
        )

        new_refresh_token, refresh_jti, family_id = create_refresh_token(
            user_id=token_data.user_id,
            tenant_id=token_data.tenant_id,
            family_id=token_data.family_id,  # Keep same family for rotation tracking
            expires_delta=timedelta(days=7),
        )

        return LoginResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=1800,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


@router.post("/revoke-all")
async def revoke_all_user_tokens(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Revoke all tokens for the current user

    Use cases:
    - User changed password
    - User wants to logout from all devices
    - Security incident response

    This revokes all tokens issued before the current timestamp,
    forcing re-authentication on all devices.
    """
    revocation_store = get_revocation_store()

    if not revocation_store._initialized:
        await revocation_store.initialize()

    success = await revocation_store.revoke_all_user_tokens(
        user_id=current_user.id,
        reason="user_requested_revoke_all",
    )

    return {
        "message": "All tokens revoked successfully",
        "user_id": current_user.id,
        "success": success,
    }


# ============================================
# Admin Endpoints
# ============================================


@router.post("/admin/users/{user_id}/revoke-tokens")
async def admin_revoke_user_tokens(
    request: Request,
    user_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Admin endpoint to revoke all tokens for a specific user

    Requires admin role.

    Use cases:
    - Account suspension
    - Security incident
    - Force password reset
    """
    # Check if current user has admin role
    if not current_user.has_any_role(["admin", "super_admin"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    revocation_store = get_revocation_store()

    if not revocation_store._initialized:
        await revocation_store.initialize()

    success = await revocation_store.revoke_all_user_tokens(
        user_id=user_id,
        reason="admin_revocation",
    )

    return {
        "message": f"All tokens revoked for user {user_id}",
        "target_user_id": user_id,
        "revoked_by": current_user.id,
        "success": success,
    }


@router.post("/admin/tenants/{tenant_id}/revoke-tokens")
async def admin_revoke_tenant_tokens(
    request: Request,
    tenant_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Admin endpoint to revoke all tokens for a tenant

    Requires super_admin role.

    Use cases:
    - Tenant suspension
    - Plan downgrade/expiration
    - Security incident
    """
    # Check if current user has super_admin role
    if not current_user.has_role("super_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required",
        )

    revocation_store = get_revocation_store()

    if not revocation_store._initialized:
        await revocation_store.initialize()

    success = await revocation_store.revoke_all_tenant_tokens(
        tenant_id=tenant_id,
        reason="admin_revocation",
    )

    return {
        "message": f"All tokens revoked for tenant {tenant_id}",
        "target_tenant_id": tenant_id,
        "revoked_by": current_user.id,
        "success": success,
    }


@router.get("/admin/revocation/stats")
async def get_revocation_stats(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Get token revocation statistics

    Requires admin role.
    """
    if not current_user.has_any_role(["admin", "super_admin"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    revocation_store = get_revocation_store()

    if not revocation_store._initialized:
        await revocation_store.initialize()

    stats = await revocation_store.get_stats()

    return {
        "initialized": stats.initialized,
        "revoked_tokens": stats.revoked_tokens,
        "revoked_users": stats.revoked_users,
        "revoked_tenants": stats.revoked_tenants,
        "redis_url": stats.redis_url,
    }


@router.get("/admin/revocation/health")
async def check_revocation_health(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Check revocation store health

    Requires admin role.
    """
    if not current_user.has_any_role(["admin", "super_admin"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    revocation_store = get_revocation_store()

    is_healthy = await revocation_store.health_check()

    return {
        "healthy": is_healthy,
        "initialized": revocation_store._initialized,
        "service": "token_revocation",
    }


# ============================================
# Usage in your main.py
# ============================================

"""
To use these endpoints in your FastAPI application:

from fastapi import FastAPI
from auth.token_revocation_example import router as auth_router

app = FastAPI()

# Include the auth router
app.include_router(auth_router)

# Or with a different prefix
app.include_router(auth_router, prefix="/api/v1")
"""
