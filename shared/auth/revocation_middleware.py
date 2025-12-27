"""
Token Revocation Middleware for FastAPI
Middleware للتحقق من الرموز الملغاة

Checks if tokens are revoked before allowing access to protected routes.
"""

import logging
from typing import Callable, Optional

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from .config import config
from .jwt_handler import verify_token
from .models import AuthErrors, AuthException
from .token_revocation import get_revocation_store

logger = logging.getLogger(__name__)


class TokenRevocationMiddleware(BaseHTTPMiddleware):
    """
    Middleware to check if tokens are revoked.
    وسيط للتحقق من إلغاء الرموز.

    This middleware should be added after JWTAuthMiddleware to check
    if authenticated tokens have been revoked.

    Example:
        ```python
        from fastapi import FastAPI
        from shared.auth.middleware import JWTAuthMiddleware
        from shared.auth.revocation_middleware import TokenRevocationMiddleware

        app = FastAPI()
        app.add_middleware(JWTAuthMiddleware)
        app.add_middleware(TokenRevocationMiddleware)

        @app.get("/protected")
        async def protected_route(request: Request):
            user = request.state.user
            return {"user_id": user.id}
        ```
    """

    def __init__(
        self,
        app,
        exclude_paths: Optional[list[str]] = None,
        fail_open: bool = True,
    ):
        """
        Initialize token revocation middleware.

        Args:
            app: FastAPI application instance
            exclude_paths: List of paths to exclude from revocation check
            fail_open: If True, allow access on Redis errors (default: True)
        """
        super().__init__(app)
        self.exclude_paths = exclude_paths or [
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/auth/login",
            "/auth/register",
            "/auth/refresh",
        ]
        self.fail_open = fail_open

    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        """
        Check if token is revoked before allowing access.

        Args:
            request: FastAPI request object
            call_next: Next middleware or route handler

        Returns:
            Response from the route handler or revocation error
        """
        # Skip for excluded paths
        if self._is_excluded_path(request.url.path):
            return await call_next(request)

        # Only check if user is authenticated
        if not hasattr(request.state, "user") or not request.state.user:
            return await call_next(request)

        # Skip if revocation is disabled
        if not config.TOKEN_REVOCATION_ENABLED:
            return await call_next(request)

        try:
            # Extract token and verify it
            token = self._extract_token(request)
            if not token:
                return await call_next(request)

            # Verify token to get claims
            payload = verify_token(token)

            # Get revocation store
            store = await get_revocation_store()

            # Check if token is revoked
            is_revoked, reason = await store.is_revoked(
                jti=payload.jti,
                user_id=payload.user_id,
                tenant_id=payload.tenant_id,
                issued_at=payload.iat.timestamp(),
            )

            if is_revoked:
                logger.warning(
                    f"Revoked token access attempt: "
                    f"user={payload.user_id}, reason={reason}"
                )

                return JSONResponse(
                    status_code=401,
                    content={
                        "error": AuthErrors.TOKEN_REVOKED.code,
                        "message": AuthErrors.TOKEN_REVOKED.en,
                        "reason": reason,
                    }
                )

        except AuthException as e:
            # Token is invalid - let JWTAuthMiddleware handle it
            logger.debug(f"Invalid token in revocation check: {e.error.code}")

        except Exception as e:
            logger.error(f"Error checking token revocation: {e}")

            # Fail open: allow access on errors if configured
            if not self.fail_open:
                return JSONResponse(
                    status_code=503,
                    content={
                        "error": "service_unavailable",
                        "message": "Token revocation service unavailable",
                    }
                )

        # Continue to next middleware or route handler
        return await call_next(request)

    def _is_excluded_path(self, path: str) -> bool:
        """Check if path is excluded from revocation check"""
        return any(path.startswith(excluded) for excluded in self.exclude_paths)

    def _extract_token(self, request: Request) -> Optional[str]:
        """
        Extract JWT token from Authorization header.

        Args:
            request: FastAPI request object

        Returns:
            JWT token string or None if not found
        """
        authorization = request.headers.get(config.TOKEN_HEADER)

        if not authorization:
            return None

        try:
            scheme, token = authorization.split()

            if scheme.lower() != config.TOKEN_PREFIX.lower():
                return None

            return token

        except ValueError:
            return None


class RevocationCheckDependency:
    """
    FastAPI dependency for checking token revocation.
    تبعية FastAPI للتحقق من إلغاء الرمز.

    Use this as a route dependency to check token revocation.

    Example:
        ```python
        from fastapi import Depends, APIRouter
        from shared.auth.revocation_middleware import RevocationCheckDependency

        router = APIRouter()
        revocation_check = RevocationCheckDependency()

        @router.get("/protected", dependencies=[Depends(revocation_check)])
        async def protected_route():
            return {"status": "ok"}
        ```
    """

    def __init__(self, fail_open: bool = True):
        """
        Initialize revocation check dependency.

        Args:
            fail_open: If True, allow access on Redis errors
        """
        self.fail_open = fail_open

    async def __call__(self, request: Request) -> None:
        """
        Check if token is revoked.

        Args:
            request: FastAPI request object

        Raises:
            HTTPException: If token is revoked
        """
        from fastapi import HTTPException

        # Only check if user is authenticated
        if not hasattr(request.state, "user") or not request.state.user:
            return

        # Skip if revocation is disabled
        if not config.TOKEN_REVOCATION_ENABLED:
            return

        try:
            # Get token from request
            token = self._extract_token(request)
            if not token:
                return

            # Verify token to get claims
            payload = verify_token(token)

            # Get revocation store
            store = await get_revocation_store()

            # Check if token is revoked
            is_revoked, reason = await store.is_revoked(
                jti=payload.jti,
                user_id=payload.user_id,
                tenant_id=payload.tenant_id,
                issued_at=payload.iat.timestamp(),
            )

            if is_revoked:
                logger.warning(
                    f"Revoked token access attempt: "
                    f"user={payload.user_id}, reason={reason}"
                )

                raise HTTPException(
                    status_code=401,
                    detail={
                        "error": AuthErrors.TOKEN_REVOKED.code,
                        "message": AuthErrors.TOKEN_REVOKED.en,
                        "reason": reason,
                    }
                )

        except HTTPException:
            raise

        except AuthException as e:
            # Token is invalid
            raise HTTPException(
                status_code=401,
                detail={
                    "error": e.error.code,
                    "message": e.error.en,
                }
            )

        except Exception as e:
            logger.error(f"Error checking token revocation: {e}")

            # Fail open: allow access on errors if configured
            if not self.fail_open:
                raise HTTPException(
                    status_code=503,
                    detail={
                        "error": "service_unavailable",
                        "message": "Token revocation service unavailable",
                    }
                )

    def _extract_token(self, request: Request) -> Optional[str]:
        """Extract JWT token from Authorization header"""
        authorization = request.headers.get(config.TOKEN_HEADER)

        if not authorization:
            return None

        try:
            scheme, token = authorization.split()

            if scheme.lower() != config.TOKEN_PREFIX.lower():
                return None

            return token

        except ValueError:
            return None
