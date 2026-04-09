"""Shared FastAPI dependencies: auth extraction, RBAC guards."""
from fastapi import Depends, HTTPException, Request, status, Cookie
from jose import JWTError
from typing import Optional

from ..core.security import decode_token


def _extract_bearer(request: Request) -> Optional[str]:
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return auth[7:]
    return None


async def get_current_user(
    request: Request,
    db_pool=None,  # injected via app.state in middleware
) -> dict:
    token = _extract_bearer(request)
    if not token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing access token")
    try:
        payload = decode_token(token)
    except JWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token")

    if payload.get("type") != "access":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not an access token")

    return {
        "user_id": payload["sub"],
        "email": payload.get("email"),
        "role": payload.get("role", "user"),
        "jti": payload.get("jti"),
    }


def require_role(*roles: str):
    """Dependency factory: raises 403 if user role not in allowed roles."""
    async def _dep(current_user: dict = Depends(get_current_user)) -> dict:
        if current_user["role"] not in roles:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                f"Required role(s): {', '.join(roles)}",
            )
        return current_user
    return _dep
