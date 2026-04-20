"""
Authentication API Routes for SAHOOL Platform
مسارات واجهة برمجة التطبيقات للمصادقة

FastAPI routes for authentication:
- Login with 2FA support
- Token refresh
- Current user info
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from .jwt_handler import create_access_token, verify_token
from .models import AuthErrors, AuthException
from .twofa_service import get_twofa_service

logger = logging.getLogger(__name__)

# Router setup
router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"],
)


# ══════════════════════════════════════════════════════════════════════════════
# Request/Response Models
# ══════════════════════════════════════════════════════════════════════════════


class LoginRequest(BaseModel):
    """Login request payload"""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password", min_length=6)
    totp_code: str | None = Field(None, description="6-digit TOTP code if 2FA is enabled")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "admin@sahool.io",
                "password": "SecurePassword123",
                "totp_code": "123456",
            }
        }
    )


class LoginResponse(BaseModel):
    """Login response"""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    user: dict = Field(..., description="User information")
    requires_2fa: bool = Field(default=False, description="Whether 2FA is required")
    temp_token: str | None = Field(None, description="Temporary token for 2FA verification")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "user": {
                    "id": "user-123",
                    "email": "admin@sahool.io",
                    "name": "Admin User",
                    "role": "admin",
                },
                "requires_2fa": False,
            }
        }
    )


class TwoFALoginRequest(BaseModel):
    """2FA login request payload"""

    temp_token: str = Field(..., description="Temporary token from initial login")
    totp_code: str = Field(..., description="6-digit TOTP code or backup code")

    model_config = ConfigDict(json_schema_extra={"example": {"temp_token": "temp_token_here", "totp_code": "123456"}})


class RefreshTokenRequest(BaseModel):
    """Token refresh request"""

    refresh_token: str = Field(..., description="Refresh token")

    model_config = ConfigDict(json_schema_extra={"example": {"refresh_token": "refresh_token_here"}})


# ══════════════════════════════════════════════════════════════════════════════
# Dependency for User Service
# ══════════════════════════════════════════════════════════════════════════════

# NOTE: This should be injected by your application
_user_service = None


def get_user_service():
    """Get user service instance (should be overridden by application)"""
    if _user_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="User service not configured",
        )
    return _user_service


def set_user_service(service):
    """Set user service instance"""
    global _user_service
    _user_service = service


# ══════════════════════════════════════════════════════════════════════════════
# Helper Functions
# ══════════════════════════════════════════════════════════════════════════════


def create_temp_token(user_id: str, email: str) -> str:
    """Create a signed temporary token for 2FA verification (valid for 5 minutes).

    SECURITY: Uses JWT with HMAC signature instead of plain base64 to prevent
    token forgery and 2FA bypass attacks.
    """
    return create_access_token(
        user_id=user_id,
        roles=[],
        expires_delta=timedelta(minutes=5),
        extra_claims={"temp": True, "email": email},
    )


def verify_temp_token(temp_token: str) -> dict | None:
    """Verify and decode temporary token using JWT signature verification.

    SECURITY: Validates the 'temp' claim to prevent regular access tokens
    from being used to bypass 2FA challenges.
    """
    try:
        # First verify signature and standard claims via verify_token
        payload = verify_token(temp_token)

        if not hasattr(payload, "user_id") or not payload.user_id:
            return None

        # SECURITY: Decode raw JWT with full signature verification to
        # access the 'temp' extra claim not in the TokenPayload model.
        import jwt as pyjwt

        from .config import config
        from .jwt_handler import ALLOWED_ALGORITHMS

        raw_payload = pyjwt.decode(
            temp_token,
            config.get_verification_key(),
            algorithms=ALLOWED_ALGORITHMS,
            audience=config.JWT_AUDIENCE,
            issuer=config.JWT_ISSUER,
        )

        if not raw_payload.get("temp"):
            logger.warning(
                "Temp token verification failed: missing 'temp' claim",
                extra={"user_id": payload.user_id},
            )
            return None

        email = raw_payload.get("email")
        if not email:
            logger.warning(
                "Temp token missing 'email' claim",
                extra={"user_id": payload.user_id},
            )
            return None

        return {
            "user_id": payload.user_id,
            "email": email,
            "temp": True,
        }
    except AuthException:
        return None
    except Exception as e:
        logger.error(f"Error verifying temp token: {type(e).__name__}", exc_info=True)
        return None


# ══════════════════════════════════════════════════════════════════════════════
# API Endpoints
# ══════════════════════════════════════════════════════════════════════════════


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Login with email and password.

    Flow:
    1. Verify email and password
    2. If 2FA is enabled and no TOTP code provided:
       - Return temp_token and requires_2fa=True
       - Client should call /login/2fa with TOTP code
    3. If 2FA is enabled and TOTP code provided:
       - Verify TOTP code
       - Return access token
    4. If 2FA is not enabled:
       - Return access token
    """
    try:
        user_service = get_user_service()

        # Verify password
        user = user_service.verify_user_password(request.email, request.password)
        if not user:
            logger.warning(f"Failed login attempt for email: {request.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=AuthErrors.INVALID_CREDENTIALS.en,
            )

        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=AuthErrors.ACCOUNT_DISABLED.en,
            )

        # Check if user is verified
        if not user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=AuthErrors.ACCOUNT_NOT_VERIFIED.en,
            )

        # Check if 2FA is enabled
        if user.twofa_enabled:
            # If TOTP code is provided, verify it
            if request.totp_code:
                twofa_service = get_twofa_service()

                # Try TOTP verification
                is_valid_totp = twofa_service.verify_totp(user.twofa_secret, request.totp_code)

                # Try backup code if TOTP fails
                is_valid_backup = False
                used_backup_hash = None
                if not is_valid_totp and user.twofa_backup_codes:
                    is_valid_backup, used_backup_hash, _remaining = twofa_service.verify_backup_code(
                        request.totp_code, user.twofa_backup_codes
                    )

                if not is_valid_totp and not is_valid_backup:
                    logger.warning(f"Invalid 2FA code for user {user.id}")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid two-factor authentication code",
                    )

                # Remove used backup code
                if is_valid_backup and used_backup_hash:
                    user_service.remove_backup_code(user.id, used_backup_hash)
                    logger.info(f"Backup code used for user {user.id}")

                # Continue to create access token
            else:
                # Return temp token and require 2FA
                temp_token = create_temp_token(user.id, user.email)

                return LoginResponse(
                    access_token="",
                    token_type="bearer",
                    user={
                        "id": user.id,
                        "email": user.email,
                        "name": user.profile.name,
                        "role": user.roles[0] if user.roles else "viewer",
                    },
                    requires_2fa=True,
                    temp_token=temp_token,
                )

        # Create access token
        access_token = create_access_token(
            user_id=user.id,
            roles=user.roles,
            tenant_id=user.tenant_id,
            permissions=[],  # Add permissions as needed
        )

        # Update last login
        user_service.update_last_login(user.id)

        logger.info(f"User {user.id} logged in successfully")

        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user={
                "id": user.id,
                "email": user.email,
                "name": user.profile.name,
                "name_ar": user.profile.name_ar,
                "role": user.roles[0] if user.roles else "viewer",
                "tenant_id": user.tenant_id,
            },
            requires_2fa=False,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during login",
        )


@router.post("/login/2fa", response_model=LoginResponse)
async def login_with_2fa(request: TwoFALoginRequest):
    """
    Complete login with 2FA verification.

    This endpoint is called after initial login when 2FA is required.
    """
    try:
        # Verify temp token
        payload = verify_temp_token(request.temp_token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired temporary token",
            )

        user_service = get_user_service()
        twofa_service = get_twofa_service()

        # Get user
        user = user_service.get_user(payload["user_id"])
        if not user or not user.twofa_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Two-factor authentication is not enabled",
            )

        # Verify TOTP code
        is_valid_totp = twofa_service.verify_totp(user.twofa_secret, request.totp_code)

        # Try backup code if TOTP fails
        is_valid_backup = False
        used_backup_hash = None
        if not is_valid_totp and user.twofa_backup_codes:
            is_valid_backup, used_backup_hash, _remaining = twofa_service.verify_backup_code(
                request.totp_code, user.twofa_backup_codes
            )

        if not is_valid_totp and not is_valid_backup:
            logger.warning(f"Invalid 2FA code for user {user.id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid two-factor authentication code",
            )

        # Remove used backup code
        if is_valid_backup and used_backup_hash:
            user_service.remove_backup_code(user.id, used_backup_hash)
            logger.info(f"Backup code used for user {user.id}")

        # Create access token
        access_token = create_access_token(
            user_id=user.id,
            roles=user.roles,
            tenant_id=user.tenant_id,
            permissions=[],  # Add permissions as needed
        )

        # Update last login
        user_service.update_last_login(user.id)

        logger.info(f"User {user.id} completed 2FA login successfully")

        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user={
                "id": user.id,
                "email": user.email,
                "name": user.profile.name,
                "name_ar": user.profile.name_ar,
                "role": user.roles[0] if user.roles else "viewer",
                "tenant_id": user.tenant_id,
            },
            requires_2fa=False,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"2FA login error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during 2FA verification",
        )


@router.get("/me")
async def get_current_user_info(user_id: str):
    """
    Get current user information.

    Note: This should use the get_current_user dependency in production
    """
    try:
        user_service = get_user_service()
        user = user_service.get_user(user_id)

        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        return {
            "success": True,
            "data": {
                "id": user.id,
                "email": user.email,
                "name": user.profile.name,
                "name_ar": user.profile.name_ar,
                "role": user.roles[0] if user.roles else "viewer",
                "tenant_id": user.tenant_id,
                "twofa_enabled": user.twofa_enabled,
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user information",
        )
