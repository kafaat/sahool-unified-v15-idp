"""
SAHOOL Authentication Endpoints Example
مثال على نقاط المصادقة

This example demonstrates how to implement authentication endpoints with
strict rate limiting to prevent brute-force attacks.

Usage:
    Include this in your FastAPI application:

    from fastapi import FastAPI
    from apps.services.shared.auth.auth_endpoints_example import router

    app = FastAPI()
    app.include_router(router, prefix="/api/v1/auth", tags=["Authentication"])
"""

import logging
import secrets
import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel, EmailStr, Field

from ..middleware.rate_limiter import get_rate_limit_headers
from .jwt import TokenData, create_access_token, create_refresh_token, decode_token
from .password import hash_password, verify_password
from .rate_limiting import AuthRateLimiter, get_auth_rate_limiter

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
    summary="User Login",
    description="""
    Authenticate user with email and password.

    **Rate Limit: 5 requests per minute per IP + username**

    Security Features:
    - Strict rate limiting to prevent brute force attacks
    - Failed login attempts are logged
    - Account lockout after multiple failed attempts (implement in service)

    Headers:
    - X-RateLimit-Limit: Maximum requests allowed
    - X-RateLimit-Remaining: Remaining requests in current window
    - X-RateLimit-Reset: Seconds until rate limit resets
    """,
    responses={
        200: {
            "description": "Login successful",
            "headers": {
                "X-RateLimit-Limit": {
                    "description": "Request limit",
                    "schema": {"type": "integer"},
                },
                "X-RateLimit-Remaining": {
                    "description": "Requests remaining",
                    "schema": {"type": "integer"},
                },
                "X-RateLimit-Reset": {
                    "description": "Seconds until reset",
                    "schema": {"type": "integer"},
                },
            },
        },
        401: {"description": "Invalid credentials"},
        429: {
            "description": "Rate limit exceeded - Too many login attempts",
            "content": {
                "application/json": {
                    "example": {
                        "error": "rate_limit_exceeded",
                        "message": "Too many login attempts. Please try again later.",
                        "retry_after": 45,
                    }
                }
            },
        },
    },
)
async def login(
    request: Request,
    response: Response,
    credentials: LoginRequest,
    limiter: AuthRateLimiter = Depends(get_auth_rate_limiter),
):
    """Login endpoint with strict rate limiting (5 req/min)."""

    # Check rate limit - raises HTTPException if exceeded
    allowed, remaining, limit, reset = await limiter.check_login_limit(request, credentials.email)

    # Add rate limit headers to response
    for header, value in get_rate_limit_headers(remaining, limit, reset).items():
        response.headers[header] = value

    # Log login attempt for security monitoring
    logger.info(
        "Login attempt - Email: %s, IP: %s, Remaining: %d/%d",
        str(credentials.email).replace("\n", " ").replace("\r", " "),
        str(request.client.host).replace("\n", " ").replace("\r", " "),
        remaining,
        limit,
    )

    # --- Authentication Logic ---
    # In production: user = await db.users.find_one({"email": credentials.email})
    # For this example, we simulate a database lookup:
    user = _mock_user_lookup(credentials.email)

    if user is None:
        # User not found - use generic error to prevent email enumeration
        logger.warning(
            "Failed login attempt (user not found) - Email: %s, IP: %s",
            str(credentials.email).replace("\n", " ").replace("\r", " "),
            str(request.client.host).replace("\n", " ").replace("\r", " "),
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Verify password against stored hash
    if not verify_password(credentials.password, user["password_hash"]):
        logger.warning(
            "Failed login attempt (wrong password) - Email: %s, IP: %s",
            str(credentials.email).replace("\n", " ").replace("\r", " "),
            str(request.client.host).replace("\n", " ").replace("\r", " "),
        )
        # In production: increment failed login counter for account lockout
        # await db.users.update_one(
        #     {"email": credentials.email},
        #     {"$inc": {"failed_login_attempts": 1}, "$set": {"last_failed_login": datetime.now(UTC)}}
        # )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # In production: reset failed login counter on success
    # await db.users.update_one(
    #     {"email": credentials.email},
    #     {"$set": {"failed_login_attempts": 0, "last_login": datetime.now(UTC)}}
    # )

    # Generate JWT tokens with JTI for revocation tracking
    access_token, access_jti = create_access_token(
        user_id=user["id"],
        email=user["email"],
        tenant_id=user.get("tenant_id"),
        roles=user.get("roles", []),
    )
    refresh_token_str, refresh_jti, family_id = create_refresh_token(
        user_id=user["id"],
        tenant_id=user.get("tenant_id"),
    )

    logger.info(
        "Login successful - User: %s, IP: %s",
        user["id"],
        str(request.client.host).replace("\n", " ").replace("\r", " "),
    )

    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token_str,
        expires_in=3600,
    )


@router.post(
    "/register",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="User Registration",
    description="""
    Create a new user account.

    **Rate Limit: 10 requests per minute per IP**

    Security Features:
    - Moderate rate limiting to prevent spam registrations
    - Email validation
    - Password strength requirements
    - Email verification (implement in service)
    """,
    responses={
        201: {"description": "Registration successful"},
        400: {"description": "Invalid registration data"},
        409: {"description": "Email already exists"},
        429: {"description": "Rate limit exceeded"},
    },
)
async def register(
    request: Request,
    response: Response,
    user_data: RegisterRequest,
    limiter: AuthRateLimiter = Depends(get_auth_rate_limiter),
):
    """Registration endpoint with moderate rate limiting (10 req/min)."""

    # Check rate limit
    allowed, remaining, limit, reset = await limiter.check_registration_limit(request, user_data.email)

    # Add rate limit headers
    for header, value in get_rate_limit_headers(remaining, limit, reset).items():
        response.headers[header] = value

    logger.info(
        "Registration attempt - Email: %s, IP: %s",
        str(user_data.email).replace("\n", " ").replace("\r", " "),
        str(request.client.host).replace("\n", " ").replace("\r", " "),
    )

    # --- Registration Logic ---

    # Step 1: Check if email already exists
    # In production: existing = await db.users.find_one({"email": user_data.email})
    existing = _mock_user_lookup(user_data.email)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )

    # Step 2: Hash the password securely (bcrypt with fallback to PBKDF2)
    password_hash = hash_password(user_data.password)

    # Step 3: Create user record
    new_user = {
        "id": str(uuid.uuid4()),
        "email": user_data.email,
        "full_name": user_data.full_name,
        "phone": user_data.phone,
        "password_hash": password_hash,
        "is_active": False,  # Inactive until email verified
        "is_verified": False,
        "created_at": datetime.now(UTC).isoformat(),
        "roles": ["farmer"],  # Default role
    }

    # In production: await db.users.insert_one(new_user)
    logger.info("User created - ID: %s", new_user["id"])

    # Step 4: Generate email verification token
    _verification_token = secrets.token_urlsafe(32)
    # In production: store token with expiry and send verification email
    # await db.email_verifications.insert_one({
    #     "user_id": new_user["id"],
    #     "token": _verification_token,
    #     "expires_at": datetime.now(UTC) + timedelta(hours=24),
    # })
    # await email_service.send_verification(user_data.email, _verification_token)

    logger.info("Verification email queued - User: %s", new_user["id"])

    return MessageResponse(message="Registration successful. Please check your email for verification.")


@router.post(
    "/forgot-password",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Request Password Reset",
    description="""
    Request a password reset email.

    **Rate Limit: 3 requests per minute per IP + email**

    Security Features:
    - Very strict rate limiting to prevent abuse
    - Generic response to prevent email enumeration
    - Token expiration (15 minutes)
    - One-time use tokens
    """,
    responses={
        200: {"description": "Request processed (always returns success)"},
        429: {"description": "Rate limit exceeded"},
    },
)
async def forgot_password(
    request: Request,
    response: Response,
    data: ForgotPasswordRequest,
    limiter: AuthRateLimiter = Depends(get_auth_rate_limiter),
):
    """Password reset request endpoint with very strict rate limiting (3 req/min)."""

    # Check rate limit
    allowed, remaining, limit, reset = await limiter.check_password_reset_limit(request, data.email)

    # Add rate limit headers
    for header, value in get_rate_limit_headers(remaining, limit, reset).items():
        response.headers[header] = value

    logger.info(
        "Password reset request - Email: %s, IP: %s",
        str(data.email).replace("\n", " ").replace("\r", " "),
        str(request.client.host).replace("\n", " ").replace("\r", " "),
    )

    # --- Password Reset Request Logic ---
    # Always return success to prevent email enumeration, regardless of whether
    # the user exists. All real work happens inside the conditional block.

    # In production: user = await db.users.find_one({"email": data.email})
    user = _mock_user_lookup(data.email)

    if user is not None:
        # Step 1: Generate a cryptographically secure one-time-use reset token
        _reset_token = secrets.token_urlsafe(32)

        # Step 2: Store the token with a 15-minute expiry
        # In production:
        # await db.password_resets.delete_many({"user_id": user["id"]})  # Invalidate old tokens
        # await db.password_resets.insert_one({
        #     "user_id": user["id"],
        #     "token_hash": hash_password(_reset_token),  # Store hashed, not plaintext
        #     "expires_at": datetime.now(UTC) + timedelta(minutes=15),
        #     "used": False,
        # })
        logger.info("Password reset token generated - User: %s", user["id"])

        # Step 3: Send reset email with link containing the plaintext token
        # In production: await email_service.send_password_reset(
        #     email=data.email,
        #     reset_link=f"https://app.sahool.io/reset-password?token={_reset_token}"
        # )
        logger.info("Password reset email queued - User: %s", user["id"])
    else:
        # Log for monitoring but do not reveal to the caller
        logger.info("Password reset requested for non-existent email")

    # Always return success to prevent email enumeration
    return MessageResponse(message="If the email exists, a password reset link has been sent.")


@router.post(
    "/reset-password",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Reset Password",
    description="""
    Reset password using the token from email.

    **Rate Limit: 5 requests per minute per IP**

    Security Features:
    - Token validation and expiration check
    - One-time use tokens
    - Password strength validation
    """,
    responses={
        200: {"description": "Password reset successful"},
        400: {"description": "Invalid or expired token"},
        429: {"description": "Rate limit exceeded"},
    },
)
async def reset_password(
    request: Request,
    response: Response,
    data: ResetPasswordRequest,
    limiter: AuthRateLimiter = Depends(get_auth_rate_limiter),
):
    """Password reset endpoint with rate limiting (5 req/min)."""

    # For reset, we use registration limit config (similar strictness)
    allowed, remaining, limit, reset = await limiter.check_registration_limit(request)

    # Add rate limit headers
    for header, value in get_rate_limit_headers(remaining, limit, reset).items():
        response.headers[header] = value

    logger.info(
        "Password reset attempt - IP: %s",
        str(request.client.host).replace("\n", " ").replace("\r", " "),
    )

    # --- Password Reset Confirmation Logic ---

    # Step 1: Look up the reset token record
    # In production: Find all unexpired, unused tokens and verify the hash
    # reset_record = await db.password_resets.find_one({
    #     "used": False,
    #     "expires_at": {"$gt": datetime.now(UTC)},
    # })
    # Then compare: verify_password(data.token, reset_record["token_hash"])
    #
    # For this example, simulate a lookup:
    reset_record = _mock_reset_token_lookup(data.token)

    if reset_record is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired password reset token",
        )

    # Step 2: Check token expiration
    if reset_record["expires_at"] < datetime.now(UTC):
        logger.warning("Expired reset token used - User: %s", reset_record["user_id"])
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired password reset token",
        )

    # Step 3: Hash the new password
    _new_password_hash = hash_password(data.new_password)

    # Step 4: Update the user's password in the database
    # In production:
    # await db.users.update_one(
    #     {"id": reset_record["user_id"]},
    #     {"$set": {"password_hash": _new_password_hash, "updated_at": datetime.now(UTC)}}
    # )
    logger.info("Password updated - User: %s", reset_record["user_id"])

    # Step 5: Mark the reset token as used (one-time use)
    # In production:
    # await db.password_resets.update_one(
    #     {"_id": reset_record["_id"]},
    #     {"$set": {"used": True, "used_at": datetime.now(UTC)}}
    # )

    # Step 6: Optionally revoke all existing sessions for security
    # In production:
    # await revocation_store.revoke_all_user_tokens(reset_record["user_id"])
    logger.info("All existing sessions invalidated after password reset - User: %s", reset_record["user_id"])

    return MessageResponse(message="Password has been reset successfully")


@router.post(
    "/refresh",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh Access Token",
    description="""
    Get a new access token using a refresh token.

    **Rate Limit: 10 requests per minute per IP**

    Security Features:
    - Refresh token validation
    - Token rotation (issue new refresh token)
    - Revocation check
    """,
    responses={
        200: {"description": "Token refreshed successfully"},
        401: {"description": "Invalid or expired refresh token"},
        429: {"description": "Rate limit exceeded"},
    },
)
async def refresh_token(
    request: Request,
    response: Response,
    data: RefreshTokenRequest,
    limiter: AuthRateLimiter = Depends(get_auth_rate_limiter),
):
    """Token refresh endpoint with moderate rate limiting (10 req/min)."""

    # --- Token Refresh Logic ---

    # Step 1: Decode the refresh token to extract user_id and validate signature/expiry
    try:
        token_data: TokenData = decode_token(data.refresh_token)
    except Exception as e:
        logger.warning("Invalid refresh token presented - IP: %s, Error: %s", request.client.host, str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    # Step 2: Verify it is actually a refresh token (not an access token)
    if token_data.token_type != "refresh":
        logger.warning("Non-refresh token used for refresh - User: %s", token_data.user_id)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    user_id = token_data.user_id

    # Apply rate limiting using the extracted user_id
    allowed, remaining, limit, reset = await limiter.check_token_refresh_limit(request, user_id)

    # Add rate limit headers
    for header, value in get_rate_limit_headers(remaining, limit, reset).items():
        response.headers[header] = value

    logger.info(
        "Token refresh - User: %s, IP: %s",
        user_id,
        str(request.client.host).replace("\n", " ").replace("\r", " "),
    )

    # Step 3: Check if token has been revoked
    # In production: check against revocation store (Redis-backed)
    # revocation_store = get_revocation_store()
    # if await revocation_store.is_token_revoked(token_data.jti):
    #     # Possible token theft - revoke entire token family
    #     if token_data.family_id:
    #         await revocation_store.revoke_token_family(token_data.family_id)
    #     logger.warning("Revoked refresh token reuse detected - User: %s, family: %s", user_id, token_data.family_id)
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has been revoked")

    # Step 4: Verify user still exists and is active
    # In production: user = await db.users.find_one({"id": user_id, "is_active": True})
    # if user is None:
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User account is inactive")

    # Step 5: Rotate tokens - issue new access + refresh tokens, revoke the old refresh token
    # Revoke the old refresh token (one-time use / rotation)
    # In production: await revocation_store.revoke_token(token_data.jti)

    new_access_token, access_jti = create_access_token(
        user_id=user_id,
        email=token_data.email,
        tenant_id=token_data.tenant_id,
        roles=token_data.roles,
    )
    new_refresh_token, refresh_jti, family_id = create_refresh_token(
        user_id=user_id,
        tenant_id=token_data.tenant_id,
        family_id=token_data.family_id,  # Preserve token family for rotation tracking
    )

    logger.info("Tokens refreshed - User: %s, new_access_jti: %s", user_id, access_jti[:8])

    return AuthResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        expires_in=3600,
    )


@router.post(
    "/logout",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="User Logout",
    description="""
    Logout user and invalidate tokens.

    **No rate limiting** - Logout is not security-sensitive.
    """,
    responses={
        200: {"description": "Logout successful"},
    },
)
async def logout(request: Request, data: RefreshTokenRequest | None = None):
    """Logout endpoint - no rate limiting needed."""

    # --- Logout Logic ---

    # Step 1: Extract the access token from the Authorization header
    auth_header = request.headers.get("Authorization", "")
    access_token = None
    access_token_data = None

    if auth_header.startswith("Bearer "):
        access_token = auth_header[len("Bearer "):]
        try:
            access_token_data = decode_token(access_token)
        except Exception:
            # If access token is invalid/expired, continue with logout anyway
            # The user may be logging out with an expired access token
            logger.info("Logout with invalid/expired access token - IP: %s", request.client.host)

    user_id = access_token_data.user_id if access_token_data else "unknown"

    # Step 2: Revoke the access token by adding its JTI to the blacklist
    # In production (Redis-backed revocation store):
    # revocation_store = get_revocation_store()
    # if access_token_data and access_token_data.jti:
    #     remaining_ttl = (access_token_data.exp - datetime.now(UTC)).total_seconds()
    #     if remaining_ttl > 0:
    #         await revocation_store.revoke_token(
    #             jti=access_token_data.jti,
    #             ttl=int(remaining_ttl),  # Auto-expire from blacklist when token would expire
    #         )

    # Step 3: Revoke the refresh token (and optionally the entire token family)
    if data and data.refresh_token:
        try:
            refresh_token_data = decode_token(data.refresh_token)
            # In production: revoke the refresh token and its family
            # await revocation_store.revoke_token(refresh_token_data.jti)
            # if refresh_token_data.family_id:
            #     await revocation_store.revoke_token_family(refresh_token_data.family_id)
            logger.info(
                "Refresh token revoked on logout - User: %s, family: %s",
                user_id,
                getattr(refresh_token_data, "family_id", None),
            )
        except Exception:
            # If refresh token is already invalid, that's fine for logout
            logger.info("Logout with invalid refresh token - User: %s", user_id)

    # Step 4: Optionally clear server-side session data
    # In production:
    # await db.sessions.delete_many({"user_id": user_id})
    # await cache.delete(f"session:{user_id}")

    logger.info("User logout successful - User: %s, IP: %s", user_id, request.client.host)

    return MessageResponse(message="Logout successful")


# ═══════════════════════════════════════════════════════════════════════════════
# Mock Helpers (Example Only)
# ═══════════════════════════════════════════════════════════════════════════════
# In a production service, these would be replaced by actual database queries
# (e.g., using asyncpg, Tortoise ORM, or Prisma).

# In-memory mock store for demonstration purposes
_MOCK_USERS: dict[str, dict] = {
    "farmer@example.com": {
        "id": "usr_01HZEXAMPLE000000000000001",
        "email": "farmer@example.com",
        "full_name": "Ahmed Al-Rashid",
        "password_hash": hash_password("SecurePass123!"),
        "is_active": True,
        "is_verified": True,
        "roles": ["farmer"],
        "tenant_id": "tenant_001",
        "created_at": "2025-01-01T00:00:00Z",
    },
}

_MOCK_RESET_TOKENS: dict[str, dict] = {}


def _mock_user_lookup(email: str) -> dict | None:
    """
    Simulate a database user lookup by email.

    In production, replace with:
        user = await db.users.find_one({"email": email, "is_active": True})

    Returns:
        User dict if found, None otherwise.
    """
    return _MOCK_USERS.get(email)


def _mock_reset_token_lookup(token: str) -> dict | None:
    """
    Simulate a database lookup for a password reset token.

    In production, replace with:
        records = await db.password_resets.find({"used": False, "expires_at": {"$gt": now}})
        for record in records:
            if verify_password(token, record["token_hash"]):
                return record

    Note: In production, tokens are stored as hashes (not plaintext) and
    verified using constant-time comparison via verify_password().

    Returns:
        Reset token record dict if found and valid, None otherwise.
    """
    record = _MOCK_RESET_TOKENS.get(token)
    if record is not None and not record.get("used", False):
        return record
    return None
