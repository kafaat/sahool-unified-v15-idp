"""
Service-to-Service Authentication Middleware for FastAPI
Middleware and dependencies for verifying service tokens
"""

import logging
from collections.abc import Callable

from fastapi import Depends, Header, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from .service_auth import ServiceAuthErrors, verify_service_token

logger = logging.getLogger(__name__)


class ServiceAuthMiddleware(BaseHTTPMiddleware):
    """
    Service-to-Service Authentication Middleware for FastAPI.

    This middleware validates service tokens for inter-service communication.
    It extracts the service token from X-Service-Token header and validates it.

    Example:
        ```python
        from fastapi import FastAPI
        from shared.auth.service_middleware import ServiceAuthMiddleware

        app = FastAPI()
        app.add_middleware(
            ServiceAuthMiddleware,
            current_service="farm-service",
            exclude_paths=["/health", "/docs"]
        )

        @app.get("/internal/fields")
        async def get_fields(request: Request):
            # Access the calling service name
            calling_service = request.state.calling_service
            return {"message": f"Called by {calling_service}"}
        ```
    """

    def __init__(
        self,
        app,
        current_service: str,
        exclude_paths: list[str] | None = None,
        require_service_auth: bool = False,
    ):
        """
        Initialize service authentication middleware.

        Args:
            app: FastAPI application instance
            current_service: Name of the current service
            exclude_paths: List of paths to exclude from service authentication
            require_service_auth: If True, all requests require service authentication
        """
        super().__init__(app)
        self.current_service = current_service
        self.exclude_paths = exclude_paths or [
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
        ]
        self.require_service_auth = require_service_auth

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request and validate service token.

        Args:
            request: FastAPI request object
            call_next: Next middleware or route handler

        Returns:
            Response from the route handler
        """
        # Skip authentication for excluded paths
        if self._is_excluded_path(request.url.path):
            return await call_next(request)

        # Extract service token from X-Service-Token header
        service_token = request.headers.get("X-Service-Token")

        if service_token:
            try:
                # Verify service token
                payload = verify_service_token(service_token)

                # Verify the target service matches current service
                if payload["target_service"] != self.current_service:
                    logger.warning(
                        f"Service token target mismatch: "
                        f"expected {self.current_service}, got {payload['target_service']}"
                    )
                    return JSONResponse(
                        status_code=403,
                        content={
                            "error": ServiceAuthErrors.UNAUTHORIZED_SERVICE_CALL[
                                "code"
                            ],
                            "message": ServiceAuthErrors.UNAUTHORIZED_SERVICE_CALL[
                                "en"
                            ],
                        },
                    )

                # Add calling service to request state
                request.state.calling_service = payload["service_name"]
                request.state.is_service_request = True

                logger.debug(
                    f"Service request: {payload['service_name']} -> {self.current_service}"
                )

            except Exception as e:
                logger.warning(f"Service authentication failed: {str(e)}")

                if self.require_service_auth:
                    return JSONResponse(
                        status_code=401,
                        content={
                            "error": ServiceAuthErrors.INVALID_SERVICE_TOKEN["code"],
                            "message": ServiceAuthErrors.INVALID_SERVICE_TOKEN["en"],
                        },
                    )

        elif self.require_service_auth:
            return JSONResponse(
                status_code=401,
                content={
                    "error": "missing_service_token",
                    "message": "Service authentication token is required",
                },
            )

        # Continue to next middleware or route handler
        return await call_next(request)

    def _is_excluded_path(self, path: str) -> bool:
        """Check if path is excluded from service authentication"""
        return any(path.startswith(excluded) for excluded in self.exclude_paths)


async def verify_service_request(
    request: Request,
    x_service_token: str | None = Header(None),
) -> dict:
    """
    FastAPI dependency to verify service-to-service requests.

    This dependency extracts and validates the service token from the
    X-Service-Token header. Use this for endpoints that should only be
    accessible by other services.

    Args:
        request: FastAPI request object
        x_service_token: Service token from X-Service-Token header

    Returns:
        Dictionary with service_name and target_service

    Raises:
        HTTPException: If service token is missing or invalid

    Example:
        ```python
        from fastapi import APIRouter, Depends
        from shared.auth.service_middleware import verify_service_request

        router = APIRouter()

        @router.get("/internal/data")
        async def get_internal_data(
            service_info: dict = Depends(verify_service_request)
        ):
            calling_service = service_info["service_name"]
            return {"message": f"Called by {calling_service}"}
        ```
    """
    from fastapi import HTTPException

    if not x_service_token:
        raise HTTPException(
            status_code=401,
            detail={
                "error": "missing_service_token",
                "message": "Service authentication token is required",
            },
        )

    try:
        payload = verify_service_token(x_service_token)

        # Add to request state if not already set by middleware
        if not hasattr(request.state, "calling_service"):
            request.state.calling_service = payload["service_name"]
            request.state.is_service_request = True

        return payload

    except Exception as e:
        logger.warning(f"Service token verification failed: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail={
                "error": ServiceAuthErrors.INVALID_SERVICE_TOKEN["code"],
                "message": ServiceAuthErrors.INVALID_SERVICE_TOKEN["en"],
            },
        )


def require_service_auth(allowed_services: list[str] | None = None):
    """
    FastAPI dependency factory to require service authentication.

    Creates a dependency that validates service tokens and optionally
    restricts access to specific services.

    Args:
        allowed_services: List of service names allowed to call this endpoint
                         If None, all valid services are allowed

    Returns:
        FastAPI dependency function

    Example:
        ```python
        from fastapi import APIRouter, Depends
        from shared.auth.service_middleware import require_service_auth

        router = APIRouter()

        # Only farm-service and crop-service can call this
        @router.post("/internal/process")
        async def process_data(
            service_info: dict = Depends(
                require_service_auth(["farm-service", "crop-service"])
            )
        ):
            return {"status": "processed"}
        ```
    """

    async def _verify_service(
        service_info: dict = Depends(verify_service_request),
    ) -> dict:
        from fastapi import HTTPException

        if allowed_services and service_info["service_name"] not in allowed_services:
            logger.warning(
                f"Service {service_info['service_name']} not in allowed list"
            )
            raise HTTPException(
                status_code=403,
                detail={
                    "error": ServiceAuthErrors.UNAUTHORIZED_SERVICE_CALL["code"],
                    "message": ServiceAuthErrors.UNAUTHORIZED_SERVICE_CALL["en"],
                },
            )

        return service_info

    return _verify_service


def get_calling_service(request: Request) -> str | None:
    """
    Get the name of the calling service from request state.

    Args:
        request: FastAPI request object

    Returns:
        Name of the calling service or None if not a service request

    Example:
        ```python
        from fastapi import Request

        @app.get("/endpoint")
        async def endpoint(request: Request):
            calling_service = get_calling_service(request)
            if calling_service:
                print(f"Called by service: {calling_service}")
        ```
    """
    return getattr(request.state, "calling_service", None)


def is_service_request(request: Request) -> bool:
    """
    Check if the current request is from another service.

    Args:
        request: FastAPI request object

    Returns:
        True if request is from a service, False otherwise

    Example:
        ```python
        from fastapi import Request

        @app.get("/endpoint")
        async def endpoint(request: Request):
            if is_service_request(request):
                # Handle service request differently
                pass
        ```
    """
    return getattr(request.state, "is_service_request", False)
