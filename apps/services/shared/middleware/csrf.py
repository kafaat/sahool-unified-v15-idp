"""
SAHOOL CSRF Protection Middleware
حماية من هجمات CSRF (Cross-Site Request Forgery)

Provides CSRF token generation and validation for state-changing operations.
يوفر توليد والتحقق من رموز CSRF للعمليات التي تغير الحالة.
"""

import hashlib
import hmac
import logging
import secrets
import time
from typing import Callable, Optional, Set, List
from urllib.parse import urlparse

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.datastructures import MutableHeaders

logger = logging.getLogger(__name__)


class CSRFConfig:
    """
    Configuration for CSRF protection.
    إعدادات حماية CSRF.
    """

    def __init__(
        self,
        secret_key: Optional[str] = None,
        token_name: str = "csrf_token",
        header_name: str = "X-CSRF-Token",
        cookie_name: str = "csrf_token",
        cookie_path: str = "/",
        cookie_domain: Optional[str] = None,
        cookie_secure: bool = True,
        cookie_httponly: bool = True,
        cookie_samesite: str = "strict",
        cookie_max_age: int = 3600,  # 1 hour
        safe_methods: Set[str] = None,
        exclude_paths: List[str] = None,
        require_referer_check: bool = True,
        trusted_origins: List[str] = None,
    ):
        """
        Initialize CSRF configuration.

        Args:
            secret_key: Secret key for HMAC signing (generated if not provided)
            token_name: Name of the token in request body/form
            header_name: Name of the CSRF header
            cookie_name: Name of the CSRF cookie
            cookie_path: Cookie path
            cookie_domain: Cookie domain (None for current domain)
            cookie_secure: Use Secure flag (HTTPS only)
            cookie_httponly: Use HttpOnly flag
            cookie_samesite: SameSite attribute (strict, lax, none)
            cookie_max_age: Cookie max age in seconds
            safe_methods: HTTP methods that don't require CSRF protection
            exclude_paths: Paths to exclude from CSRF protection
            require_referer_check: Check Referer header for additional security
            trusted_origins: List of trusted origins for CORS scenarios
        """
        self.secret_key = secret_key or secrets.token_hex(32)
        self.token_name = token_name
        self.header_name = header_name
        self.cookie_name = cookie_name
        self.cookie_path = cookie_path
        self.cookie_domain = cookie_domain
        self.cookie_secure = cookie_secure
        self.cookie_httponly = cookie_httponly
        self.cookie_samesite = cookie_samesite
        self.cookie_max_age = cookie_max_age
        self.safe_methods = safe_methods or {"GET", "HEAD", "OPTIONS", "TRACE"}
        self.exclude_paths = exclude_paths or [
            "/health",
            "/healthz",
            "/readyz",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/metrics",
        ]
        self.require_referer_check = require_referer_check
        self.trusted_origins = trusted_origins or []


class CSRFProtection(BaseHTTPMiddleware):
    """
    CSRF Protection Middleware for FastAPI.

    This middleware implements Double Submit Cookie pattern with HMAC signing:
    1. Generates a CSRF token on first request
    2. Sets the token in a secure cookie
    3. Expects the token in a header for state-changing requests
    4. Validates token matches and signature is valid
    5. Excludes API endpoints using Bearer token authentication

    Example:
        ```python
        from fastapi import FastAPI
        from apps.services.shared.middleware.csrf import CSRFProtection, CSRFConfig

        app = FastAPI()

        csrf_config = CSRFConfig(
            secret_key="your-secret-key",
            cookie_secure=True,
            exclude_paths=["/api/v1/webhook"]
        )

        app.add_middleware(CSRFProtection, config=csrf_config)

        @app.get("/form")
        async def get_form(request: Request):
            # CSRF token available in cookie
            return {"message": "Token set in cookie"}

        @app.post("/submit")
        async def submit_form(request: Request):
            # CSRF token will be validated automatically
            return {"message": "Success"}
        ```
    """

    def __init__(
        self,
        app,
        config: Optional[CSRFConfig] = None,
    ):
        """
        Initialize CSRF protection middleware.

        Args:
            app: FastAPI application instance
            config: CSRF configuration (uses defaults if not provided)
        """
        super().__init__(app)
        self.config = config or CSRFConfig()
        logger.info(
            f"CSRF Protection initialized: cookie={self.config.cookie_name}, "
            f"header={self.config.header_name}, secure={self.config.cookie_secure}"
        )

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        """
        Process the request and apply CSRF protection.

        Args:
            request: FastAPI request object
            call_next: Next middleware or route handler

        Returns:
            Response with CSRF cookie set (if needed) or error response
        """
        # Skip CSRF protection for excluded paths
        if self._is_excluded_path(request.url.path):
            return await call_next(request)

        # Skip CSRF for API requests with Bearer token authentication
        if self._has_bearer_token(request):
            logger.debug(f"Skipping CSRF check for Bearer token auth: {request.url.path}")
            return await call_next(request)

        # Safe methods don't require CSRF validation
        if request.method in self.config.safe_methods:
            response = await call_next(request)
            # Set CSRF cookie on safe requests if not present
            if not request.cookies.get(self.config.cookie_name):
                self._set_csrf_cookie(response, request)
            return response

        # Validate CSRF token for state-changing operations
        is_valid, error_message = self._validate_csrf_token(request)

        if not is_valid:
            logger.warning(
                f"CSRF validation failed: {error_message}",
                extra={
                    "path": request.url.path,
                    "method": request.method,
                    "client": request.client.host if request.client else "unknown",
                },
            )
            return JSONResponse(
                status_code=403,
                content={
                    "success": False,
                    "error": {
                        "code": "CSRF_VALIDATION_FAILED",
                        "message": "CSRF token validation failed",
                        "message_ar": "فشل التحقق من رمز CSRF",
                        "details": {"reason": error_message},
                    },
                },
            )

        # Token is valid, proceed with request
        response = await call_next(request)

        # Refresh CSRF cookie on successful requests
        self._set_csrf_cookie(response, request)

        return response

    def _is_excluded_path(self, path: str) -> bool:
        """
        Check if path is excluded from CSRF protection.

        Args:
            path: Request path

        Returns:
            True if path is excluded
        """
        return any(path.startswith(excluded) for excluded in self.config.exclude_paths)

    def _has_bearer_token(self, request: Request) -> bool:
        """
        Check if request has Bearer token authentication.

        CSRF protection is primarily for cookie-based authentication.
        API requests using Bearer tokens are exempt from CSRF checks.

        Args:
            request: FastAPI request object

        Returns:
            True if request has Bearer token
        """
        authorization = request.headers.get("Authorization", "")
        return authorization.lower().startswith("bearer ")

    def _generate_csrf_token(self, timestamp: Optional[int] = None) -> str:
        """
        Generate a CSRF token using HMAC with timestamp.

        Token format: {random_value}.{timestamp}.{hmac_signature}

        Args:
            timestamp: Unix timestamp (current time if not provided)

        Returns:
            CSRF token string
        """
        if timestamp is None:
            timestamp = int(time.time())

        # Generate random value
        random_value = secrets.token_urlsafe(32)

        # Create message to sign
        message = f"{random_value}.{timestamp}"

        # Generate HMAC signature
        signature = hmac.new(
            self.config.secret_key.encode(),
            message.encode(),
            hashlib.sha256,
        ).hexdigest()

        # Return complete token
        return f"{random_value}.{timestamp}.{signature}"

    def _verify_csrf_token(self, token: str) -> tuple[bool, Optional[str]]:
        """
        Verify CSRF token signature and expiration.

        Args:
            token: CSRF token to verify

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Parse token
            parts = token.split(".")
            if len(parts) != 3:
                return False, "Invalid token format"

            random_value, timestamp_str, provided_signature = parts

            # Verify timestamp
            try:
                timestamp = int(timestamp_str)
            except ValueError:
                return False, "Invalid timestamp"

            # Check token expiration
            current_time = int(time.time())
            if current_time - timestamp > self.config.cookie_max_age:
                return False, "Token expired"

            # Recreate message and verify signature
            message = f"{random_value}.{timestamp}"
            expected_signature = hmac.new(
                self.config.secret_key.encode(),
                message.encode(),
                hashlib.sha256,
            ).hexdigest()

            # Use constant-time comparison to prevent timing attacks
            if not hmac.compare_digest(expected_signature, provided_signature):
                return False, "Invalid token signature"

            return True, None

        except Exception as e:
            logger.error(f"Error verifying CSRF token: {e}", exc_info=True)
            return False, "Token verification error"

    def _validate_csrf_token(self, request: Request) -> tuple[bool, Optional[str]]:
        """
        Validate CSRF token from request.

        Implements Double Submit Cookie pattern:
        1. Token must be present in cookie
        2. Token must be present in header or form data
        3. Both tokens must match
        4. Token signature must be valid
        5. Token must not be expired

        Args:
            request: FastAPI request object

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Get token from cookie
        cookie_token = request.cookies.get(self.config.cookie_name)
        if not cookie_token:
            return False, "CSRF cookie not found"

        # Get token from header (preferred) or form data
        header_token = request.headers.get(self.config.header_name)

        if not header_token:
            # Try to get from form data (for form submissions)
            # Note: This requires the request body to be read, which is handled by FastAPI
            return False, f"CSRF token not found in {self.config.header_name} header"

        # Verify tokens match (constant-time comparison)
        if not hmac.compare_digest(cookie_token, header_token):
            return False, "CSRF token mismatch between cookie and header"

        # Verify token signature and expiration
        is_valid, error = self._verify_csrf_token(cookie_token)
        if not is_valid:
            return False, error

        # Additional referer check if enabled
        if self.config.require_referer_check:
            is_valid, error = self._check_referer(request)
            if not is_valid:
                return False, error

        return True, None

    def _check_referer(self, request: Request) -> tuple[bool, Optional[str]]:
        """
        Check Referer header for additional CSRF protection.

        Args:
            request: FastAPI request object

        Returns:
            Tuple of (is_valid, error_message)
        """
        referer = request.headers.get("Referer")
        if not referer:
            # Some browsers/clients don't send Referer
            # Allow if Origin header is present instead
            origin = request.headers.get("Origin")
            if not origin:
                logger.debug("No Referer or Origin header present")
                # Don't fail if both are missing - rely on token validation
                return True, None
            referer = origin

        try:
            referer_url = urlparse(referer)
            request_host = request.headers.get("Host", "")

            # Check if referer matches current host
            if referer_url.netloc == request_host:
                return True, None

            # Check if referer is in trusted origins
            if referer_url.netloc in self.config.trusted_origins:
                return True, None

            # Check if origin matches any trusted origin
            for origin in self.config.trusted_origins:
                if referer.startswith(origin):
                    return True, None

            logger.warning(
                f"Referer validation failed: {referer_url.netloc} != {request_host}",
                extra={"referer": referer, "host": request_host},
            )
            return False, "Referer validation failed"

        except Exception as e:
            logger.error(f"Error checking referer: {e}")
            return False, "Invalid Referer header"

    def _set_csrf_cookie(self, response: Response, request: Request) -> None:
        """
        Set CSRF token cookie in response.

        Args:
            response: Response object
            request: Request object (used to check if cookie already exists)
        """
        # Check if cookie already exists and is valid
        existing_token = request.cookies.get(self.config.cookie_name)
        if existing_token:
            is_valid, _ = self._verify_csrf_token(existing_token)
            if is_valid:
                # Existing token is still valid, no need to set new one
                return

        # Generate new token
        token = self._generate_csrf_token()

        # Build cookie attributes
        samesite = self.config.cookie_samesite.lower()
        if samesite not in ("strict", "lax", "none"):
            samesite = "strict"

        # Set cookie in response
        response.set_cookie(
            key=self.config.cookie_name,
            value=token,
            max_age=self.config.cookie_max_age,
            path=self.config.cookie_path,
            domain=self.config.cookie_domain,
            secure=self.config.cookie_secure,
            httponly=self.config.cookie_httponly,
            samesite=samesite,
        )

        logger.debug(
            f"CSRF cookie set: {self.config.cookie_name} "
            f"(secure={self.config.cookie_secure}, httponly={self.config.cookie_httponly}, "
            f"samesite={samesite})"
        )


def get_csrf_token(request: Request, cookie_name: str = "csrf_token") -> Optional[str]:
    """
    Helper function to get CSRF token from request cookies.

    Usage in route handlers:
        ```python
        from apps.services.shared.middleware.csrf import get_csrf_token

        @app.get("/form")
        async def get_form(request: Request):
            csrf_token = get_csrf_token(request)
            return {"csrf_token": csrf_token}
        ```

    Args:
        request: FastAPI request object
        cookie_name: Name of the CSRF cookie

    Returns:
        CSRF token string or None if not found
    """
    return request.cookies.get(cookie_name)


# Export main classes and functions
__all__ = [
    "CSRFConfig",
    "CSRFProtection",
    "get_csrf_token",
]
