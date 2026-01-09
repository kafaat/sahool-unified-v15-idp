"""
Token Revocation Middleware for FastAPI
البرمجيات الوسيطة للتحقق من إلغاء الرموز

Middleware to check token revocation status before processing requests.
"""

import logging
from collections.abc import Callable

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from .jwt import decode_token
from .token_revocation import get_revocation_store

logger = logging.getLogger(__name__)


class TokenRevocationMiddleware(BaseHTTPMiddleware):
    """
    Middleware to check if JWT tokens are revoked

    This middleware:
    1. Extracts token from request
    2. Decodes and validates token
    3. Checks revocation status in Redis
    4. Rejects request if token is revoked

    Usage:
        app.add_middleware(
            TokenRevocationMiddleware,
            exempt_paths=["/healthz", "/docs"],
        )
    """

    def __init__(
        self,
        app,
        exempt_paths: list[str] | None = None,
        check_revocation: bool = True,
    ):
        """
        Initialize middleware

        Args:
            app: FastAPI application
            exempt_paths: List of paths to exempt from revocation check
            check_revocation: Enable/disable revocation checking (useful for testing)
        """
        super().__init__(app)
        self.exempt_paths = exempt_paths or [
            "/healthz",
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
        ]
        self.check_revocation = check_revocation
        self._revocation_store = None

    async def _get_revocation_store(self):
        """Lazy initialization of revocation store"""
        if self._revocation_store is None:
            self._revocation_store = get_revocation_store()
            if not self._revocation_store._initialized:
                try:
                    await self._revocation_store.initialize()
                except Exception as e:
                    logger.error(f"Failed to initialize revocation store: {e}")
                    # Don't fail the middleware, but disable revocation checking
                    self.check_revocation = False

        return self._revocation_store

    def _is_exempt_path(self, path: str) -> bool:
        """Check if path is exempt from revocation check"""
        return any(path.startswith(exempt) for exempt in self.exempt_paths)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and check token revocation"""
        # Skip revocation check for exempt paths
        if self._is_exempt_path(request.url.path):
            return await call_next(request)

        # Skip if revocation checking is disabled
        if not self.check_revocation:
            return await call_next(request)

        # Extract token from Authorization header
        auth_header = request.headers.get("authorization")
        if not auth_header:
            # No token, let the request proceed (other middleware will handle auth)
            return await call_next(request)

        # Extract Bearer token
        token_parts = auth_header.split()
        if len(token_parts) != 2 or token_parts[0].lower() != "bearer":
            # Invalid format, let other middleware handle it
            return await call_next(request)

        token = token_parts[1]

        try:
            # Decode token to get JTI and other claims
            token_data = decode_token(token)

            if not token_data:
                # Token invalid, let other middleware handle it
                return await call_next(request)

            # Check revocation status
            revocation_store = await self._get_revocation_store()

            result = await revocation_store.is_revoked(
                jti=token_data.jti,
                user_id=token_data.user_id,
                tenant_id=token_data.tenant_id,
                family_id=token_data.family_id,
                issued_at=token_data.iat.timestamp() if token_data.iat else None,
            )

            if result.is_revoked:
                logger.warning(
                    f"Revoked token used: jti={token_data.jti[:8] if token_data.jti else 'N/A'}..., "
                    f"reason={result.reason}, user_id={token_data.user_id}"
                )

                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "error": "token_revoked",
                        "message": "This token has been revoked",
                        "reason": result.reason,
                    },
                    headers={"WWW-Authenticate": "Bearer"},
                )

        except Exception as e:
            logger.error(f"Error checking token revocation: {e}")
            # On error, allow request to proceed (fail open for availability)
            # In high-security environments, you might want to fail closed instead

        # Token is valid and not revoked, proceed with request
        return await call_next(request)


async def check_token_revocation(token: str) -> tuple[bool, str | None]:
    """
    Helper function to check if a token is revoked

    Args:
        token: JWT token to check

    Returns:
        Tuple of (is_revoked, reason)
    """
    try:
        # Decode token
        token_data = decode_token(token)

        if not token_data:
            return False, None

        # Check revocation
        revocation_store = get_revocation_store()
        if not revocation_store._initialized:
            await revocation_store.initialize()

        result = await revocation_store.is_revoked(
            jti=token_data.jti,
            user_id=token_data.user_id,
            tenant_id=token_data.tenant_id,
            family_id=token_data.family_id,
            issued_at=token_data.iat.timestamp() if token_data.iat else None,
        )

        return result.is_revoked, result.reason

    except Exception as e:
        logger.error(f"Error checking token revocation: {e}")
        return False, None
