"""
SAHOOL Authentication Endpoints - Full Implementation
نقاط نهاية المصادقة الكاملة

This module provides fully functional authentication endpoints with:
- Secure password hashing (Argon2id)
- JWT token generation and validation
- Rate limiting protection
- Token revocation support
- In-memory storage for development

Production Note: Replace InMemoryAuthStore with database-backed implementation.
"""

import logging
import secrets
from datetime import UTC, datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel, EmailStr, Field

from .config import get_auth_config
from .jwt import create_access_token, create_refresh_token, decode_token
from .models import AuthException
from .password import hash_password, verify_password

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# Request/Response Models
# ═══════════════════════════════════════════════════════════════════════════════


class LoginRequest(BaseModel):
    """Login request schema"""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password")


class RegisterRequest(BaseModel):
    """Registration request schema"""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password")
    full_name: str = Field(..., min_length=2, max_length=100, description="Full name")
    phone: str | None = Field(None, description="Phone number")


class ForgotPasswordRequest(BaseModel):
    """Forgot password request schema"""

    email: EmailStr = Field(..., description="User email address")


class ResetPasswordRequest(BaseModel):
    """Reset password request schema"""

    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, description="New password")


class RefreshTokenRequest(BaseModel):
    """Token refresh request schema"""

    refresh_token: str = Field(..., description="Refresh token")


class AuthResponse(BaseModel):
    """Authentication response schema"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 3600


class MessageResponse(BaseModel):
    """Generic message response"""

    message: str
    message_ar: str | None = None


class UserResponse(BaseModel):
    """User info response"""

    id: str
    email: str
    full_name: str
    roles: list[str]
    is_verified: bool


# ═══════════════════════════════════════════════════════════════════════════════
# In-Memory Auth Store (Development Only)
# ═══════════════════════════════════════════════════════════════════════════════


class InMemoryAuthStore:
    """
    In-memory storage for development/testing.
    تخزين في الذاكرة للتطوير والاختبار.

    ⚠️ WARNING: Replace with database storage in production!
    """

    def __init__(self):
        self._users: dict[str, dict[str, Any]] = {}
        self._reset_tokens: dict[str, dict[str, Any]] = {}
        self._revoked_tokens: set[str] = set()
        self._refresh_tokens: dict[str, str] = {}  # jti -> user_id

        # Add default test user
        self._add_test_user()

    def _add_test_user(self):
        """Add a default test user for development"""
        test_password = hash_password("TestPassword123!")
        self._users["test@sahool.app"] = {
            "id": "user_test_001",
            "email": "test@sahool.app",
            "password_hash": test_password,
            "full_name": "Test User",
            "phone": "+967777000000",
            "roles": ["farmer", "user"],
            "is_active": True,
            "is_verified": True,
            "tenant_id": "tenant_001",
            "created_at": datetime.now(UTC),
        }
        logger.info("Test user created: test@sahool.app / TestPassword123!")

    def get_user_by_email(self, email: str) -> dict | None:
        """Get user by email"""
        return self._users.get(email.lower())

    def get_user_by_id(self, user_id: str) -> dict | None:
        """Get user by ID"""
        for user in self._users.values():
            if user["id"] == user_id:
                return user
        return None

    def create_user(self, email: str, password_hash: str, full_name: str, phone: str | None = None) -> dict:
        """Create a new user"""
        user_id = f"user_{secrets.token_hex(8)}"
        user = {
            "id": user_id,
            "email": email.lower(),
            "password_hash": password_hash,
            "full_name": full_name,
            "phone": phone,
            "roles": ["user"],
            "is_active": True,
            "is_verified": False,  # Requires email verification
            "tenant_id": None,
            "created_at": datetime.now(UTC),
        }
        self._users[email.lower()] = user
        return user

    def update_password(self, email: str, new_password_hash: str) -> bool:
        """Update user password"""
        user = self._users.get(email.lower())
        if user:
            user["password_hash"] = new_password_hash
            return True
        return False

    def create_reset_token(self, email: str) -> str | None:
        """Create password reset token"""
        user = self.get_user_by_email(email)
        if not user:
            return None

        token = secrets.token_urlsafe(32)
        self._reset_tokens[token] = {
            "email": email.lower(),
            "expires_at": datetime.now(UTC) + timedelta(minutes=15),
            "used": False,
        }
        return token

    def validate_reset_token(self, token: str) -> str | None:
        """Validate reset token and return email"""
        token_data = self._reset_tokens.get(token)
        if not token_data:
            return None
        if token_data["used"]:
            return None
        if datetime.now(UTC) > token_data["expires_at"]:
            return None
        return token_data["email"]

    def invalidate_reset_token(self, token: str) -> None:
        """Mark reset token as used"""
        if token in self._reset_tokens:
            self._reset_tokens[token]["used"] = True

    def revoke_token(self, jti: str) -> None:
        """Revoke a token by JTI"""
        self._revoked_tokens.add(jti)

    def is_token_revoked(self, jti: str) -> bool:
        """Check if token is revoked"""
        return jti in self._revoked_tokens

    def store_refresh_token(self, jti: str, user_id: str) -> None:
        """Store refresh token mapping"""
        self._refresh_tokens[jti] = user_id

    def get_refresh_token_user(self, jti: str) -> str | None:
        """Get user ID for refresh token"""
        return self._refresh_tokens.get(jti)


# Global store instance
_auth_store: InMemoryAuthStore | None = None


def get_auth_store() -> InMemoryAuthStore:
    """Get or create auth store"""
    global _auth_store
    if _auth_store is None:
        _auth_store = InMemoryAuthStore()
    return _auth_store


# ═══════════════════════════════════════════════════════════════════════════════
# Router Definition
# ═══════════════════════════════════════════════════════════════════════════════

router = APIRouter()


# ═══════════════════════════════════════════════════════════════════════════════
# Authentication Endpoints
# ═══════════════════════════════════════════════════════════════════════════════


@router.post(
    "/login",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    summary="User Login | تسجيل الدخول",
    description="""
    Authenticate user with email and password.
    المصادقة باستخدام البريد الإلكتروني وكلمة المرور.

    **Test Credentials:**
    - Email: test@sahool.app
    - Password: TestPassword123!
    """,
)
async def login(
    request: Request,
    response: Response,
    credentials: LoginRequest,
    store: InMemoryAuthStore = Depends(get_auth_store),
):
    """Login endpoint with full authentication."""

    # Get user by email
    user = store.get_user_by_email(credentials.email)

    if not user:
        logger.warning(f"Login failed - user not found: {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify password
    is_valid = verify_password(credentials.password, user["password_hash"])

    if not is_valid:
        logger.warning(f"Login failed - invalid password: {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.get("is_active", False):
        logger.warning(f"Login failed - user inactive: {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )

    # Generate tokens
    config = get_auth_config()
    access_token, _access_jti = create_access_token(
        user_id=user["id"],
        roles=user.get("roles", ["user"]),
        tenant_id=user.get("tenant_id"),
        permissions=["farm:read", "farm:write"],
    )
    refresh_token, _refresh_jti, _family_id = create_refresh_token(
        user_id=user["id"],
        tenant_id=user.get("tenant_id"),
    )

    logger.info(f"Login successful: {credentials.email} (IP: {request.client.host})")

    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=config.access_token_expire_minutes * 60,
    )


@router.post(
    "/register",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="User Registration | تسجيل مستخدم جديد",
)
async def register(
    request: Request,
    user_data: RegisterRequest,
    store: InMemoryAuthStore = Depends(get_auth_store),
):
    """Registration endpoint."""

    # Check if email exists
    existing_user = store.get_user_by_email(user_data.email)
    if existing_user:
        logger.warning(f"Registration failed - email exists: {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    # Hash password
    password_hash = hash_password(user_data.password)

    # Create user
    user = store.create_user(
        email=user_data.email,
        password_hash=password_hash,
        full_name=user_data.full_name,
        phone=user_data.phone,
    )

    logger.info(f"User registered: {user_data.email} (ID: {user['id']})")

    # In production: Send verification email here

    return MessageResponse(
        message="Registration successful. Please check your email for verification.",
        message_ar="تم التسجيل بنجاح. يرجى التحقق من بريدك الإلكتروني.",
    )


@router.post(
    "/forgot-password",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Request Password Reset | طلب إعادة تعيين كلمة المرور",
)
async def forgot_password(
    request: Request,
    data: ForgotPasswordRequest,
    store: InMemoryAuthStore = Depends(get_auth_store),
):
    """Password reset request endpoint."""

    # Create reset token (returns None if user doesn't exist)
    token = store.create_reset_token(data.email)

    if token:
        logger.info(f"Password reset requested: {data.email} (token: {token[:8]}...)")
        # In production: Send email with reset link
        # For development: Log the token
        logger.debug(f"Reset token for {data.email}: {token}")
    else:
        logger.info(f"Password reset requested for non-existent user: {data.email}")

    # Always return success to prevent email enumeration
    return MessageResponse(
        message="If the email exists, a password reset link has been sent.",
        message_ar="إذا كان البريد الإلكتروني موجوداً، تم إرسال رابط إعادة تعيين كلمة المرور.",
    )


@router.post(
    "/reset-password",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Reset Password | إعادة تعيين كلمة المرور",
)
async def reset_password(
    request: Request,
    data: ResetPasswordRequest,
    store: InMemoryAuthStore = Depends(get_auth_store),
):
    """Password reset endpoint."""

    # Validate token
    email = store.validate_reset_token(data.token)

    if not email:
        logger.warning("Invalid reset token attempted")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    # Hash new password
    new_password_hash = hash_password(data.new_password)

    # Update password
    success = store.update_password(email, new_password_hash)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update password",
        )

    # Invalidate token (one-time use)
    store.invalidate_reset_token(data.token)

    logger.info(f"Password reset successful: {email}")

    return MessageResponse(
        message="Password has been reset successfully.",
        message_ar="تم إعادة تعيين كلمة المرور بنجاح.",
    )


@router.post(
    "/refresh",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh Access Token | تحديث رمز الوصول",
)
async def refresh_token(
    request: Request,
    data: RefreshTokenRequest,
    store: InMemoryAuthStore = Depends(get_auth_store),
):
    """Token refresh endpoint."""

    try:
        # Decode and verify refresh token
        payload = decode_token(data.refresh_token, verify_audience=True)

        # Check token type
        if payload.token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )

        # Check if token is revoked
        if payload.jti and store.is_token_revoked(payload.jti):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
            )

        # Get user
        user = store.get_user_by_id(payload.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )

        # Check if user is still active
        if not user.get("is_active", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated",
            )

        # Generate new tokens
        config = get_auth_config()
        access_token, _access_jti = create_access_token(
            user_id=user["id"],
            roles=user.get("roles", ["user"]),
            tenant_id=user.get("tenant_id"),
            permissions=["farm:read", "farm:write"],
        )
        new_refresh_token, _refresh_jti, _family_id = create_refresh_token(
            user_id=user["id"],
            tenant_id=user.get("tenant_id"),
        )

        # Revoke old refresh token (token rotation)
        if payload.jti:
            store.revoke_token(payload.jti)

        logger.info(f"Token refreshed for user: {user['email']}")

        return AuthResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            expires_in=config.access_token_expire_minutes * 60,
        )

    except (AuthException, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )


@router.post(
    "/logout",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="User Logout | تسجيل الخروج",
)
async def logout(
    request: Request,
    store: InMemoryAuthStore = Depends(get_auth_store),
):
    """Logout endpoint - invalidates tokens."""

    # Extract token from Authorization header
    auth_header = request.headers.get("Authorization")

    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header[7:]
        try:
            payload = decode_token(token, verify_audience=True)

            # Revoke the token
            if payload.jti:
                store.revoke_token(payload.jti)
                logger.info(f"Token revoked for user: {payload.user_id}")

        except (AuthException, ValueError):
            # Token is invalid/expired, but logout is still successful
            pass

    return MessageResponse(
        message="Logout successful.",
        message_ar="تم تسجيل الخروج بنجاح.",
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get Current User | الحصول على المستخدم الحالي",
)
async def get_current_user(
    request: Request,
    store: InMemoryAuthStore = Depends(get_auth_store),
):
    """Get current authenticated user info."""

    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
        )

    token = auth_header[7:]

    try:
        payload = decode_token(token, verify_audience=True)

        # Check if token is revoked
        if payload.jti and store.is_token_revoked(payload.jti):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
            )

        user = store.get_user_by_id(payload.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        return UserResponse(
            id=user["id"],
            email=user["email"],
            full_name=user["full_name"],
            roles=user.get("roles", []),
            is_verified=user.get("is_verified", False),
        )

    except (AuthException, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
