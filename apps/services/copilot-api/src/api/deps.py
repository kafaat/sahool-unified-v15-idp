"""
Authentication dependencies for copilot-api - تبعيات المصادقة للمستشار الذكي
"""

import os
from datetime import UTC, datetime

import jwt
import structlog
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

logger = structlog.get_logger()

security = HTTPBearer(auto_error=False)

# Security: JWT_SECRET_KEY must be set via environment variable
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not JWT_SECRET_KEY:
    logger.warning("jwt_secret_missing", msg="JWT_SECRET_KEY not set - authentication will fail")
    JWT_SECRET_KEY = ""  # Will cause decode to fail, preventing auth bypass
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ALLOWED_ALGORITHMS = ["HS256", "HS384", "HS512"]


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> dict:
    """
    Validate JWT token and return user payload.
    التحقق من رمز JWT وإرجاع بيانات المستخدم.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Authentication required", "error_ar": "المصادقة مطلوبة"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    try:
        # Validate algorithm against whitelist to prevent algorithm confusion attacks
        if JWT_ALGORITHM not in ALLOWED_ALGORITHMS:
            raise jwt.InvalidTokenError(f"Algorithm {JWT_ALGORITHM} not allowed")

        payload = jwt.decode(
            token, JWT_SECRET_KEY, algorithms=ALLOWED_ALGORITHMS,
            options={"require": ["exp", "sub"]}
        )

        user_id = payload.get("sub") or payload.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error": "Invalid token payload", "error_ar": "محتوى الرمز غير صالح"},
            )

        return {
            "user_id": user_id,
            "tenant_id": payload.get("tid") or payload.get("tenant_id"),
            "role": payload.get("role", "user"),
            "email": payload.get("email"),
        }

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Token expired", "error_ar": "انتهت صلاحية الرمز"},
        )
    except jwt.InvalidTokenError as e:
        logger.warning("invalid_jwt_token", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Invalid token", "error_ar": "رمز غير صالح"},
        )


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> dict | None:
    """
    Optional auth - returns None if no token provided.
    مصادقة اختيارية - تُرجع None إذا لم يتم توفير رمز.

    Security: If a token IS provided but is invalid/expired, we log a warning
    and return None rather than silently ignoring the failure.
    """
    if not credentials:
        return None
    try:
        return await get_current_user(credentials)
    except HTTPException as e:
        logger.warning(
            "optional_auth_token_rejected",
            status_code=e.status_code,
            detail=e.detail,
            msg="Token provided but failed validation - treating as unauthenticated",
        )
        return None
