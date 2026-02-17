"""
SAHOOL Field Chat Service - JWT Authentication
Provides JWT token validation for API endpoints
"""

import os

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    Validate JWT token and return user info.

    Args:
        credentials: HTTP Bearer token from Authorization header

    Returns:
        dict: Decoded JWT payload containing user information

    Raises:
        HTTPException: 401 if token is expired or invalid
    """
    token = credentials.credentials
    jwt_secret = os.getenv("JWT_SECRET_KEY")

    if not jwt_secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "configuration_error",
                "message_ar": "خطأ في تكوين المصادقة",
                "message_en": "Authentication configuration error",
            },
        )

    try:
        payload = jwt.decode(
            token,
            jwt_secret,
            algorithms=[os.getenv("JWT_ALGORITHM", "HS256")],
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "token_expired",
                "message_ar": "انتهت صلاحية الرمز المميز",
                "message_en": "Token has expired",
            },
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "invalid_token",
                "message_ar": "رمز مميز غير صالح",
                "message_en": "Invalid token",
            },
        )


def validate_websocket_token(token: str) -> dict:
    """
    Validate JWT token for WebSocket connections.

    Args:
        token: JWT token string

    Returns:
        dict: Decoded JWT payload

    Raises:
        ValueError: If token is invalid or expired
    """
    jwt_secret = os.getenv("JWT_SECRET_KEY")

    if not jwt_secret:
        raise ValueError("JWT_SECRET_KEY not configured")

    try:
        payload = jwt.decode(
            token,
            jwt_secret,
            algorithms=[os.getenv("JWT_ALGORITHM", "HS256")],
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")
