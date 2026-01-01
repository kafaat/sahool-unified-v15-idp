"""
Two-Factor Authentication API Routes for SAHOOL Platform
مسارات واجهة برمجة التطبيقات للمصادقة الثنائية

FastAPI routes for 2FA management:
- Setup 2FA
- Verify and enable 2FA
- Disable 2FA
- Generate backup codes
"""

import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from .dependencies import get_current_active_user
from .models import AuthErrors, User
from .twofa_service import get_twofa_service

logger = logging.getLogger(__name__)

# Router setup
router = APIRouter(
    prefix="/admin/2fa",
    tags=["2FA Management"],
)


# ══════════════════════════════════════════════════════════════════════════════
# Request/Response Models
# ══════════════════════════════════════════════════════════════════════════════


class TwoFASetupResponse(BaseModel):
    """Response for 2FA setup initiation"""

    secret: str = Field(..., description="TOTP secret (base32 encoded)")
    qr_code: str = Field(..., description="QR code as base64 data URI")
    manual_entry_key: str = Field(..., description="Secret for manual entry")
    issuer: str = Field(..., description="Issuer name")
    account_name: str = Field(..., description="Account name (email)")

    class Config:
        json_schema_extra = {
            "example": {
                "secret": "JBSWY3DPEHPK3PXP",
                "qr_code": "data:image/png;base64,iVBORw0KG...",
                "manual_entry_key": "JBSWY3DPEHPK3PXP",
                "issuer": "SAHOOL Agricultural Platform",
                "account_name": "admin@sahool.io"
            }
        }


class TwoFAVerifyRequest(BaseModel):
    """Request for 2FA verification"""

    token: str = Field(..., description="6-digit TOTP code", min_length=6, max_length=6)

    class Config:
        json_schema_extra = {
            "example": {
                "token": "123456"
            }
        }


class TwoFAVerifyResponse(BaseModel):
    """Response for 2FA verification"""

    success: bool = Field(..., description="Whether 2FA was enabled successfully")
    backup_codes: list[str] = Field(..., description="Backup codes for account recovery")
    message: str = Field(..., description="Success message")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "backup_codes": ["ABCD-EFGH", "IJKL-MNOP"],
                "message": "Two-factor authentication enabled successfully"
            }
        }


class TwoFADisableRequest(BaseModel):
    """Request for disabling 2FA"""

    token: str = Field(..., description="6-digit TOTP code or backup code")

    class Config:
        json_schema_extra = {
            "example": {
                "token": "123456"
            }
        }


class TwoFAStatusResponse(BaseModel):
    """Response for 2FA status"""

    enabled: bool = Field(..., description="Whether 2FA is enabled")
    backup_codes_remaining: int = Field(..., description="Number of unused backup codes")

    class Config:
        json_schema_extra = {
            "example": {
                "enabled": True,
                "backup_codes_remaining": 8
            }
        }


class BackupCodesResponse(BaseModel):
    """Response for backup codes generation"""

    backup_codes: list[str] = Field(..., description="New backup codes")
    message: str = Field(..., description="Warning message")

    class Config:
        json_schema_extra = {
            "example": {
                "backup_codes": ["ABCD-EFGH", "IJKL-MNOP"],
                "message": "Previous backup codes have been invalidated"
            }
        }


# ══════════════════════════════════════════════════════════════════════════════
# Dependency for User Service
# ══════════════════════════════════════════════════════════════════════════════

# NOTE: This should be injected by your application
# For now, we'll use a placeholder that should be overridden
_user_service = None


def get_user_service():
    """Get user service instance (should be overridden by application)"""
    if _user_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="User service not configured"
        )
    return _user_service


def set_user_service(service):
    """Set user service instance"""
    global _user_service
    _user_service = service


# ══════════════════════════════════════════════════════════════════════════════
# API Endpoints
# ══════════════════════════════════════════════════════════════════════════════


@router.post("/setup", response_model=TwoFASetupResponse)
async def setup_twofa(
    user: User = Depends(get_current_active_user),
):
    """
    Initiate 2FA setup for admin user.

    Steps:
    1. Generate a new TOTP secret
    2. Generate QR code for authenticator app
    3. Return secret and QR code

    Note: 2FA is not enabled until verified via /verify endpoint
    """
    # Check if user is admin
    if not user.has_role("admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can set up 2FA"
        )

    try:
        twofa_service = get_twofa_service()
        user_service = get_user_service()

        # Generate new secret
        secret = twofa_service.generate_secret()

        # Generate QR code
        qr_code = twofa_service.generate_qr_code(secret, user.email)

        # Store secret temporarily (not enabled yet)
        # This will be stored in the user record
        await user_service.update_twofa_secret(user.id, secret)

        logger.info(f"2FA setup initiated for user {user.id}")

        return TwoFASetupResponse(
            secret=secret,
            qr_code=qr_code,
            manual_entry_key=secret,
            issuer=twofa_service.issuer,
            account_name=user.email
        )

    except Exception as e:
        logger.error(f"Error setting up 2FA for user {user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to set up two-factor authentication"
        )


@router.post("/verify", response_model=TwoFAVerifyResponse)
async def verify_and_enable_twofa(
    request: TwoFAVerifyRequest,
    user: User = Depends(get_current_active_user),
):
    """
    Verify TOTP code and enable 2FA.

    Steps:
    1. Verify the TOTP code against stored secret
    2. Generate backup codes
    3. Enable 2FA for the user
    4. Return backup codes

    Note: Backup codes should be saved securely by the user
    """
    # Check if user is admin
    if not user.has_role("admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can enable 2FA"
        )

    try:
        twofa_service = get_twofa_service()
        user_service = get_user_service()

        # Get user's 2FA secret
        user_data = await user_service.get_user(user.id)
        if not user_data or not user_data.twofa_secret:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="2FA setup not initiated. Please call /setup first"
            )

        # Verify TOTP token
        is_valid = twofa_service.verify_totp(user_data.twofa_secret, request.token)
        if not is_valid:
            logger.warning(f"Invalid TOTP token provided by user {user.id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification code"
            )

        # Generate backup codes
        backup_codes = twofa_service.generate_backup_codes()

        # Hash backup codes for storage
        hashed_codes = [twofa_service.hash_backup_code(code) for code in backup_codes]

        # Enable 2FA and store backup codes
        await user_service.enable_twofa(user.id, hashed_codes)

        logger.info(f"2FA enabled successfully for user {user.id}")

        return TwoFAVerifyResponse(
            success=True,
            backup_codes=backup_codes,
            message="Two-factor authentication enabled successfully. Save your backup codes in a secure location."
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error enabling 2FA for user {user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to enable two-factor authentication"
        )


@router.post("/disable")
async def disable_twofa(
    request: TwoFADisableRequest,
    user: User = Depends(get_current_active_user),
):
    """
    Disable 2FA for user account.

    Requires current TOTP code or backup code for verification.
    """
    # Check if user is admin
    if not user.has_role("admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can disable 2FA"
        )

    try:
        twofa_service = get_twofa_service()
        user_service = get_user_service()

        # Get user's 2FA data
        user_data = await user_service.get_user(user.id)
        if not user_data or not user_data.twofa_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Two-factor authentication is not enabled"
            )

        # Try to verify as TOTP token first
        is_valid_totp = twofa_service.verify_totp(user_data.twofa_secret, request.token)

        # If not valid TOTP, try as backup code
        is_valid_backup = False
        if not is_valid_totp and user_data.twofa_backup_codes:
            is_valid_backup, _ = twofa_service.verify_backup_code(
                request.token,
                user_data.twofa_backup_codes
            )

        if not is_valid_totp and not is_valid_backup:
            logger.warning(f"Invalid code provided for 2FA disable by user {user.id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification code"
            )

        # Disable 2FA
        await user_service.disable_twofa(user.id)

        logger.info(f"2FA disabled for user {user.id}")

        return {
            "success": True,
            "message": "Two-factor authentication has been disabled"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error disabling 2FA for user {user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to disable two-factor authentication"
        )


@router.get("/status", response_model=TwoFAStatusResponse)
async def get_twofa_status(
    user: User = Depends(get_current_active_user),
):
    """
    Get current 2FA status for user.
    """
    # Check if user is admin
    if not user.has_role("admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can access 2FA status"
        )

    try:
        user_service = get_user_service()
        user_data = await user_service.get_user(user.id)

        backup_codes_remaining = 0
        if user_data and user_data.twofa_backup_codes:
            backup_codes_remaining = len(user_data.twofa_backup_codes)

        return TwoFAStatusResponse(
            enabled=user_data.twofa_enabled if user_data else False,
            backup_codes_remaining=backup_codes_remaining
        )

    except Exception as e:
        logger.error(f"Error getting 2FA status for user {user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get two-factor authentication status"
        )


@router.post("/backup-codes", response_model=BackupCodesResponse)
async def regenerate_backup_codes(
    request: TwoFAVerifyRequest,
    user: User = Depends(get_current_active_user),
):
    """
    Generate new backup codes.

    Requires current TOTP code for verification.
    Note: This invalidates all previous backup codes.
    """
    # Check if user is admin
    if not user.has_role("admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can regenerate backup codes"
        )

    try:
        twofa_service = get_twofa_service()
        user_service = get_user_service()

        # Get user's 2FA data
        user_data = await user_service.get_user(user.id)
        if not user_data or not user_data.twofa_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Two-factor authentication is not enabled"
            )

        # Verify TOTP token
        is_valid = twofa_service.verify_totp(user_data.twofa_secret, request.token)
        if not is_valid:
            logger.warning(f"Invalid TOTP token for backup code regeneration by user {user.id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification code"
            )

        # Generate new backup codes
        backup_codes = twofa_service.generate_backup_codes()

        # Hash backup codes for storage
        hashed_codes = [twofa_service.hash_backup_code(code) for code in backup_codes]

        # Update backup codes
        await user_service.update_backup_codes(user.id, hashed_codes)

        logger.info(f"Backup codes regenerated for user {user.id}")

        return BackupCodesResponse(
            backup_codes=backup_codes,
            message="Previous backup codes have been invalidated. Save these new codes in a secure location."
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error regenerating backup codes for user {user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to regenerate backup codes"
        )
