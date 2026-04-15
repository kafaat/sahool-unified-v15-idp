"""Auth routes: register, login, logout, refresh, /me."""
import uuid
import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status, Cookie
from jose import JWTError
from typing import Optional

from ...core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from ...core.config import settings
from ...models.user import UserRegister, UserLogin, UserOut
from ...models.token import TokenResponse, TokenWithUser
from ..deps import get_current_user

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

_REFRESH_COOKIE = "refresh_token"
_REFRESH_MAX_AGE = settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 86400


def _set_refresh_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=_REFRESH_COOKIE,
        value=token,
        httponly=True,
        secure=False,   # set True in production behind HTTPS
        samesite="lax",
        max_age=_REFRESH_MAX_AGE,
        path="/api/v1/auth/refresh",
    )


def _clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(key=_REFRESH_COOKIE, path="/api/v1/auth/refresh")


# ── Register ──────────────────────────────────────────────────────────────────

@router.post("/register", response_model=TokenWithUser, status_code=status.HTTP_201_CREATED)
async def register(body: UserRegister, request: Request, response: Response):
    pool = request.app.state.db
    async with pool.acquire() as conn:
        existing = await conn.fetchrow("SELECT id FROM users WHERE email = $1", body.email)
        if existing:
            raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")

        user_id = await conn.fetchval(
            """
            INSERT INTO users (email, name, password_hash, is_active)
            VALUES ($1, $2, $3, TRUE)
            RETURNING id
            """,
            body.email, body.name, hash_password(body.password),
        )
        user_id = str(user_id)

        # Assign default 'user' role
        role_id = await conn.fetchval("SELECT id FROM roles WHERE name = 'user'")
        if role_id:
            await conn.execute(
                "INSERT INTO user_roles (user_id, role_id) VALUES ($1, $2) ON CONFLICT DO NOTHING",
                uuid.UUID(user_id), role_id,
            )

    access_token, _ = create_access_token(user_id, body.email, "user")
    refresh_token, jti, family_id = create_refresh_token(user_id)

    # Store refresh token
    async with pool.acquire() as conn:
        expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
            days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
        )
        await conn.execute(
            """
            INSERT INTO refresh_tokens (jti, user_id, family_id, expires_at)
            VALUES ($1, $2, $3, $4)
            """,
            uuid.UUID(jti), uuid.UUID(user_id), uuid.UUID(family_id), expires_at,
        )

    _set_refresh_cookie(response, refresh_token)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user_id,
            "email": body.email,
            "name": body.name,
            "role": "user",
            "is_active": True,
        },
    }


# ── Login ─────────────────────────────────────────────────────────────────────

@router.post("/login", response_model=TokenWithUser)
async def login(body: UserLogin, request: Request, response: Response):
    pool = request.app.state.db
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT u.id, u.email, u.name, u.password_hash, u.is_active,
                   r.name AS role
            FROM users u
            LEFT JOIN user_roles ur ON ur.user_id = u.id
            LEFT JOIN roles r ON r.id = ur.role_id
            WHERE u.email = $1
            ORDER BY CASE r.name WHEN 'admin' THEN 0 WHEN 'moderator' THEN 1 ELSE 2 END
            LIMIT 1
            """,
            body.email,
        )

    if not row or not verify_password(body.password, row["password_hash"]):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid email or password")

    if not row["is_active"]:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Account is inactive")

    user_id = str(row["id"])
    role = row["role"] or "user"

    access_token, _ = create_access_token(user_id, row["email"], role)
    refresh_token, jti, family_id = create_refresh_token(user_id)

    async with pool.acquire() as conn:
        expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
            days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
        )
        await conn.execute(
            """
            INSERT INTO refresh_tokens (jti, user_id, family_id, expires_at)
            VALUES ($1, $2, $3, $4)
            """,
            uuid.UUID(jti), uuid.UUID(user_id), uuid.UUID(family_id), expires_at,
        )

    _set_refresh_cookie(response, refresh_token)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user_id,
            "email": row["email"],
            "name": row["name"],
            "role": role,
            "is_active": row["is_active"],
        },
    }


# ── Refresh ───────────────────────────────────────────────────────────────────

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: Request,
    response: Response,
    refresh_token: Optional[str] = Cookie(default=None),
):
    if not refresh_token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "No refresh token")

    try:
        payload = decode_token(refresh_token)
    except JWTError:
        _clear_refresh_cookie(response)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid refresh token")

    if payload.get("type") != "refresh":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not a refresh token")

    jti = payload.get("jti")
    family_id = payload.get("family_id")
    user_id = payload.get("sub")

    pool = request.app.state.db
    async with pool.acquire() as conn:
        async with conn.transaction():
            row = await conn.fetchrow(
                "SELECT revoked FROM refresh_tokens WHERE jti = $1",
                uuid.UUID(jti),
            )

            if row is None:
                _clear_refresh_cookie(response)
                raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token not found")

            if row["revoked"]:
                # Theft detected — revoke entire family
                await conn.execute(
                    "UPDATE refresh_tokens SET revoked = TRUE WHERE family_id = $1",
                    uuid.UUID(family_id),
                )
                _clear_refresh_cookie(response)
                raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token reuse detected")

            # Revoke old token
            await conn.execute(
                "UPDATE refresh_tokens SET revoked = TRUE WHERE jti = $1",
                uuid.UUID(jti),
            )

            # Fetch user + role
            user_row = await conn.fetchrow(
                """
                SELECT u.email, r.name AS role
                FROM users u
                LEFT JOIN user_roles ur ON ur.user_id = u.id
                LEFT JOIN roles r ON r.id = ur.role_id
                WHERE u.id = $1
                ORDER BY CASE r.name WHEN 'admin' THEN 0 WHEN 'moderator' THEN 1 ELSE 2 END
                LIMIT 1
                """,
                uuid.UUID(user_id),
            )
            if not user_row:
                raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found")

            # Issue new refresh token in same family
            new_rt, new_jti, _ = create_refresh_token(user_id, family_id=family_id)
            expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
                days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
            )
            await conn.execute(
                """
                INSERT INTO refresh_tokens (jti, user_id, family_id, expires_at)
                VALUES ($1, $2, $3, $4)
                """,
                uuid.UUID(new_jti), uuid.UUID(user_id), uuid.UUID(family_id), expires_at,
            )

    role = user_row["role"] or "user"
    new_at, _ = create_access_token(user_id, user_row["email"], role)

    _set_refresh_cookie(response, new_rt)
    return {"access_token": new_at, "token_type": "bearer"}


# ── Logout ────────────────────────────────────────────────────────────────────

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: Request,
    response: Response,
    refresh_token: Optional[str] = Cookie(default=None),
    current_user: dict = Depends(get_current_user),
):
    if refresh_token:
        try:
            payload = decode_token(refresh_token)
            jti = payload.get("jti")
            pool = request.app.state.db
            async with pool.acquire() as conn:
                await conn.execute(
                    "UPDATE refresh_tokens SET revoked = TRUE WHERE jti = $1",
                    uuid.UUID(jti),
                )
        except (JWTError, Exception):
            pass  # best-effort revocation

    _clear_refresh_cookie(response)


# ── Me ────────────────────────────────────────────────────────────────────────

@router.get("/me")
async def me(request: Request, current_user: dict = Depends(get_current_user)):
    pool = request.app.state.db
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT u.id, u.email, u.name, u.is_active, u.created_at, r.name AS role
            FROM users u
            LEFT JOIN user_roles ur ON ur.user_id = u.id
            LEFT JOIN roles r ON r.id = ur.role_id
            WHERE u.id = $1
            ORDER BY CASE r.name WHEN 'admin' THEN 0 WHEN 'moderator' THEN 1 ELSE 2 END
            LIMIT 1
            """,
            uuid.UUID(current_user["user_id"]),
        )
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")

    return {
        "id": str(row["id"]),
        "email": row["email"],
        "name": row["name"],
        "role": row["role"] or "user",
        "is_active": row["is_active"],
        "created_at": row["created_at"].isoformat(),
    }
