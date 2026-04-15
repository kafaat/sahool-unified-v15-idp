"""User self-service routes: profile update, change-password, forgot/reset password."""
import uuid
import hashlib
import secrets
import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status

from ...core.security import hash_password, verify_password
from ...models.user import UserUpdate, ChangePassword, ForgotPassword, ResetPassword
from ..deps import get_current_user

router = APIRouter(prefix="/api/v1/users", tags=["users"])

_RESET_TOKEN_TTL_MINUTES = 30


# ── Profile update ────────────────────────────────────────────────────────────

@router.patch("/me")
async def update_profile(
    body: UserUpdate,
    request: Request,
    current_user: dict = Depends(get_current_user),
):
    pool = request.app.state.db
    updates = body.model_dump(exclude_none=True)
    if not updates:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "No fields to update")

    # Check email uniqueness if changing email
    if "email" in updates:
        async with pool.acquire() as conn:
            existing = await conn.fetchrow(
                "SELECT id FROM users WHERE email = $1 AND id != $2",
                updates["email"], uuid.UUID(current_user["user_id"]),
            )
        if existing:
            raise HTTPException(status.HTTP_409_CONFLICT, "Email already in use")

    set_clauses = ", ".join(f"{k} = ${i+2}" for i, k in enumerate(updates))
    values = list(updates.values())

    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            f"""
            UPDATE users SET {set_clauses}, updated_at = NOW()
            WHERE id = $1
            RETURNING id, email, name, is_active, created_at
            """,
            uuid.UUID(current_user["user_id"]), *values,
        )
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")

    return {
        "id": str(row["id"]),
        "email": row["email"],
        "name": row["name"],
        "role": current_user["role"],
        "is_active": row["is_active"],
        "created_at": row["created_at"].isoformat(),
    }


# ── Change password ───────────────────────────────────────────────────────────

@router.post("/me/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    body: ChangePassword,
    request: Request,
    current_user: dict = Depends(get_current_user),
):
    pool = request.app.state.db
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT password_hash FROM users WHERE id = $1",
            uuid.UUID(current_user["user_id"]),
        )
    if not row or not verify_password(body.current_password, row["password_hash"]):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Current password is incorrect")

    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE users SET password_hash = $1, updated_at = NOW() WHERE id = $2",
            hash_password(body.new_password), uuid.UUID(current_user["user_id"]),
        )


# ── Forgot password ───────────────────────────────────────────────────────────

@router.post("/forgot-password")
async def forgot_password(body: ForgotPassword, request: Request):
    pool = request.app.state.db
    async with pool.acquire() as conn:
        user = await conn.fetchrow("SELECT id FROM users WHERE email = $1", body.email)

    # Always return 200 to prevent user enumeration
    if not user:
        return {"message": "If that email exists, a reset token was generated"}

    raw_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
        minutes=_RESET_TOKEN_TTL_MINUTES
    )

    async with pool.acquire() as conn:
        # Invalidate existing tokens for this user
        await conn.execute(
            "UPDATE password_reset_tokens SET used = TRUE WHERE user_id = $1 AND used = FALSE",
            user["id"],
        )
        await conn.execute(
            """
            INSERT INTO password_reset_tokens (user_id, token_hash, expires_at)
            VALUES ($1, $2, $3)
            """,
            user["id"], token_hash, expires_at,
        )

    # In production: send email with raw_token.
    # In development: return the token directly for testing.
    return {
        "message": "Reset token generated",
        "reset_token": raw_token,  # remove this line in production
        "expires_in_minutes": _RESET_TOKEN_TTL_MINUTES,
    }


# ── Reset password ────────────────────────────────────────────────────────────

@router.post("/reset-password", status_code=status.HTTP_204_NO_CONTENT)
async def reset_password(body: ResetPassword, request: Request):
    token_hash = hashlib.sha256(body.token.encode()).hexdigest()
    now = datetime.datetime.now(datetime.timezone.utc)

    pool = request.app.state.db
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT id, user_id FROM password_reset_tokens
            WHERE token_hash = $1 AND used = FALSE AND expires_at > $2
            """,
            token_hash, now,
        )
    if not row:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid or expired reset token")

    async with pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute(
                "UPDATE password_reset_tokens SET used = TRUE WHERE id = $1",
                row["id"],
            )
            await conn.execute(
                "UPDATE users SET password_hash = $1, updated_at = NOW() WHERE id = $2",
                hash_password(body.new_password), row["user_id"],
            )
            # Revoke all refresh tokens for security
            await conn.execute(
                "UPDATE refresh_tokens SET revoked = TRUE WHERE user_id = $1",
                row["user_id"],
            )
