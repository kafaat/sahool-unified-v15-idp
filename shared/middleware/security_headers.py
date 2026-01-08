"""
SAHOOL Security Headers Middleware
إضافة رؤوس الأمان لمنصة سهول

This middleware adds essential security headers to all HTTP responses
to protect against common web vulnerabilities.

Security Headers Implemented:
- X-Frame-Options: Prevents clickjacking attacks
- X-Content-Type-Options: Prevents MIME-type sniffing
- Referrer-Policy: Controls referrer information
- X-XSS-Protection: Legacy XSS protection (for older browsers)
- Strict-Transport-Security: Enforces HTTPS
- Content-Security-Policy: Prevents XSS and data injection attacks
- Permissions-Policy: Controls browser features

Based on GAPS_AND_RECOMMENDATIONS.md - Phase 1 (High Priority)
"""

import os
from collections.abc import Callable

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses.

    Usage:
        from shared.middleware.security_headers import SecurityHeadersMiddleware

        app = FastAPI()
        app.add_middleware(SecurityHeadersMiddleware)
    """

    def __init__(
        self,
        app,
        enable_hsts: bool = True,
        enable_csp: bool = True,
        csp_policy: str | None = None,
    ):
        """
        Initialize security headers middleware.

        Args:
            app: FastAPI application instance
            enable_hsts: Enable Strict-Transport-Security header (HTTPS only)
            enable_csp: Enable Content-Security-Policy header
            csp_policy: Custom CSP policy (uses secure default if None)
        """
        super().__init__(app)
        self.enable_hsts = enable_hsts
        self.enable_csp = enable_csp
        self.csp_policy = csp_policy or self._get_default_csp()
        self.environment = os.getenv("ENVIRONMENT", "development").lower()

    def _get_default_csp(self) -> str:
        """
        Get default Content Security Policy.

        This is a restrictive policy optimized for API services.
        For web applications serving HTML/JS, customize via CSP_POLICY env var.

        Security Note: This default policy does NOT use 'unsafe-inline' or
        'unsafe-eval' to maintain strong XSS protection. If your app requires
        inline scripts/styles, use nonces or hashes instead.
        """
        return (
            "default-src 'self'; "
            "script-src 'self'; "  # No unsafe-inline or unsafe-eval
            "style-src 'self'; "  # No unsafe-inline
            "img-src 'self' data: https:; "  # Allow images from self, data URIs, and HTTPS
            "font-src 'self' data:; "  # Allow fonts from self and data URIs
            "connect-src 'self'; "  # API calls only to same origin
            "frame-ancestors 'none'; "  # Cannot be embedded in frames
            "base-uri 'self'; "  # Restrict base tag URLs
            "form-action 'self'; "  # Forms can only submit to same origin
            "object-src 'none'; "  # Block plugins (Flash, etc.)
            "upgrade-insecure-requests"  # Upgrade HTTP to HTTPS
        )

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Add security headers to all responses.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware or route handler

        Returns:
            Response with security headers added
        """
        # Process the request and get response
        response = await call_next(request)

        # ═══════════════════════════════════════════════════════════════════
        # Essential Security Headers (Always Applied)
        # ═══════════════════════════════════════════════════════════════════

        # Prevent clickjacking attacks
        # DENY: The page cannot be displayed in a frame
        response.headers["X-Frame-Options"] = "DENY"

        # Prevent MIME-type sniffing
        # Forces browsers to respect the Content-Type header
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Control referrer information leakage
        # strict-origin-when-cross-origin: Send full URL for same-origin,
        # only origin for cross-origin HTTPS, nothing for HTTP
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Legacy XSS protection (for older browsers)
        # Modern browsers use CSP instead, but this provides defense in depth
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Remove server information disclosure
        response.headers["X-Powered-By"] = "SAHOOL"

        # ═══════════════════════════════════════════════════════════════════
        # HSTS - Enforce HTTPS (Production Only)
        # ═══════════════════════════════════════════════════════════════════

        if self.enable_hsts and self.environment == "production":
            # max-age=31536000: 1 year in seconds
            # includeSubDomains: Apply to all subdomains
            # preload: Allow inclusion in browser HSTS preload lists
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )

        # ═══════════════════════════════════════════════════════════════════
        # Content Security Policy
        # ═══════════════════════════════════════════════════════════════════

        if self.enable_csp:
            response.headers["Content-Security-Policy"] = self.csp_policy

        # ═══════════════════════════════════════════════════════════════════
        # Permissions Policy (Feature Policy)
        # ═══════════════════════════════════════════════════════════════════

        # Restrict access to browser features
        # This prevents malicious scripts from accessing sensitive features
        response.headers["Permissions-Policy"] = (
            "geolocation=(), "  # Block geolocation unless explicitly needed
            "microphone=(), "  # Block microphone access
            "camera=(), "  # Block camera access
            "payment=(), "  # Block payment APIs
            "usb=(), "  # Block USB access
            "magnetometer=(), "  # Block magnetometer
            "accelerometer=(), "  # Block accelerometer
            "gyroscope=()"  # Block gyroscope
        )

        # ═══════════════════════════════════════════════════════════════════
        # Additional Security Headers
        # ═══════════════════════════════════════════════════════════════════

        # Cross-Origin Resource Policy
        # same-origin: Only allow same-origin requests
        response.headers["Cross-Origin-Resource-Policy"] = "same-origin"

        # Cross-Origin Opener Policy
        # same-origin: Isolate browsing context
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"

        # Cross-Origin Embedder Policy
        # require-corp: Require CORP header on cross-origin resources
        response.headers["Cross-Origin-Embedder-Policy"] = "require-corp"

        return response


def setup_security_headers(
    app: FastAPI,
    enable_hsts: bool = None,
    enable_csp: bool = True,
    csp_policy: str | None = None,
) -> None:
    """
    Configure security headers middleware with sensible defaults.

    Args:
        app: FastAPI application instance
        enable_hsts: Enable HSTS header (auto-detected based on environment)
        enable_csp: Enable Content-Security-Policy header
        csp_policy: Custom CSP policy (uses secure default if None)

    Usage:
        from shared.middleware.security_headers import setup_security_headers

        app = FastAPI()
        setup_security_headers(app)

    Environment Variables:
        ENVIRONMENT: Set to 'production' to enable HSTS
        ENABLE_HSTS: Override auto-detection (true/false)
        ENABLE_CSP: Enable/disable CSP (true/false)
        CSP_POLICY: Custom CSP policy string
    """
    # Auto-detect HSTS based on environment if not specified
    if enable_hsts is None:
        enable_hsts_env = os.getenv("ENABLE_HSTS", "").lower()
        if enable_hsts_env in ("true", "1", "yes"):
            enable_hsts = True
        elif enable_hsts_env in ("false", "0", "no"):
            enable_hsts = False
        else:
            # Default: Enable in production only
            environment = os.getenv("ENVIRONMENT", "development").lower()
            enable_hsts = environment == "production"

    # Check environment variable for CSP
    enable_csp_env = os.getenv("ENABLE_CSP", "").lower()
    if enable_csp_env in ("false", "0", "no"):
        enable_csp = False

    # Get custom CSP policy from environment if provided
    csp_policy = csp_policy or os.getenv("CSP_POLICY")

    # Add the middleware
    app.add_middleware(
        SecurityHeadersMiddleware,
        enable_hsts=enable_hsts,
        enable_csp=enable_csp,
        csp_policy=csp_policy,
    )


def get_security_headers_config() -> dict:
    """
    Get security headers configuration as a dictionary.
    Useful for debugging or logging.

    Returns:
        Dictionary with current security headers configuration
    """
    environment = os.getenv("ENVIRONMENT", "development")
    enable_hsts = os.getenv("ENABLE_HSTS", "auto")
    enable_csp = os.getenv("ENABLE_CSP", "true")

    return {
        "environment": environment,
        "hsts_enabled": enable_hsts,
        "csp_enabled": enable_csp,
        "csp_policy": os.getenv("CSP_POLICY", "default"),
    }
