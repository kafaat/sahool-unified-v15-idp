"""
API Versioning Middleware for SAHOOL Platform
نظام إصدارات API لمنصة سهول

Provides URL-based API versioning with backward compatibility support.
Supports versions: v1, v2 (future), etc.

Usage:
    from shared.middleware.api_versioning import (
        APIVersionMiddleware,
        VersionedRouter,
        APIVersion,
    )

    # Add middleware to FastAPI app
    app.add_middleware(APIVersionMiddleware)

    # Create versioned router
    router = VersionedRouter(version=APIVersion.V1, prefix="/fields")
"""

import logging
import re
from collections.abc import Callable
from enum import Enum

from fastapi import APIRouter, HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# API Version Definitions
# ═══════════════════════════════════════════════════════════════════════════════


class APIVersion(str, Enum):
    """Supported API versions"""

    V1 = "v1"
    V2 = "v2"  # Future version placeholder

    @classmethod
    def latest(cls) -> "APIVersion":
        """Get the latest stable version"""
        return cls.V1

    @classmethod
    def all_versions(cls) -> list[str]:
        """Get all supported version strings"""
        return [v.value for v in cls]

    @classmethod
    def is_valid(cls, version: str) -> bool:
        """Check if version string is valid"""
        return version.lower() in cls.all_versions()


# Current supported versions
SUPPORTED_VERSIONS = [APIVersion.V1]
DEFAULT_VERSION = APIVersion.V1
DEPRECATED_VERSIONS: list[APIVersion] = []  # Versions scheduled for removal


# ═══════════════════════════════════════════════════════════════════════════════
# Version Parsing
# ═══════════════════════════════════════════════════════════════════════════════

# Pattern to match /api/v1/, /api/v2/, etc.
VERSION_PATTERN = re.compile(r"^/api/(v\d+)(/.*)?$", re.IGNORECASE)

# Pattern for unversioned API paths
UNVERSIONED_API_PATTERN = re.compile(r"^/api(/.*)?$", re.IGNORECASE)


def extract_api_version(path: str) -> tuple[APIVersion | None, str]:
    """
    Extract API version from path and return normalized path.

    Args:
        path: Request path (e.g., "/api/v1/fields")

    Returns:
        Tuple of (version, remaining_path)
        - version: APIVersion if found, None otherwise
        - remaining_path: Path without version prefix

    Examples:
        "/api/v1/fields" -> (APIVersion.V1, "/api/fields")
        "/api/fields" -> (None, "/api/fields")
        "/health" -> (None, "/health")
    """
    match = VERSION_PATTERN.match(path)
    if match:
        version_str = match.group(1).lower()
        remaining = match.group(2) or ""
        if APIVersion.is_valid(version_str):
            return APIVersion(version_str), f"/api{remaining}"
    return None, path


# ═══════════════════════════════════════════════════════════════════════════════
# Versioning Middleware
# ═══════════════════════════════════════════════════════════════════════════════


class APIVersionMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle API versioning.

    Features:
    - Extracts version from URL (/api/v1/...)
    - Sets version in request state
    - Adds deprecation warnings for old versions
    - Supports unversioned endpoints (health, docs)

    Usage:
        app.add_middleware(APIVersionMiddleware)
    """

    # Paths that don't require versioning
    EXCLUDED_PATHS = {
        "/",
        "/health",
        "/ready",
        "/metrics",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/favicon.ico",
    }

    async def dispatch(self, request: Request, call_next: Callable):
        path = request.url.path

        # Skip versioning for excluded paths
        if self._is_excluded_path(path):
            return await call_next(request)

        # Extract version from path
        version, normalized_path = extract_api_version(path)

        # If it's an API path without version, default to latest
        if version is None and UNVERSIONED_API_PATTERN.match(path):
            version = DEFAULT_VERSION
            logger.debug(f"Unversioned API request to {path}, defaulting to {version.value}")

        # Store version in request state for downstream use
        request.state.api_version = version

        # Add deprecation warning header if using deprecated version
        response = await call_next(request)

        if version in DEPRECATED_VERSIONS:
            response.headers["X-API-Deprecated"] = "true"
            response.headers["X-API-Deprecation-Info"] = (
                f"API version {version.value} is deprecated. "
                f"Please upgrade to {DEFAULT_VERSION.value}"
            )
            logger.warning(f"Deprecated API version {version.value} used: {path}")

        # Add version info to response headers
        if version:
            response.headers["X-API-Version"] = version.value

        return response

    def _is_excluded_path(self, path: str) -> bool:
        """Check if path should be excluded from versioning"""
        # Exact match
        if path in self.EXCLUDED_PATHS:
            return True
        # Prefix match for docs
        return bool(path.startswith("/docs") or path.startswith("/redoc"))


# ═══════════════════════════════════════════════════════════════════════════════
# Versioned Router
# ═══════════════════════════════════════════════════════════════════════════════


class VersionedRouter(APIRouter):
    """
    APIRouter with built-in version prefix.

    Creates routes under /api/v{N}/prefix pattern.

    Usage:
        router = VersionedRouter(
            version=APIVersion.V1,
            prefix="/fields",
            tags=["Fields"]
        )

        @router.get("/")
        async def list_fields():
            ...
        # Creates: GET /api/v1/fields/
    """

    def __init__(
        self,
        version: APIVersion = DEFAULT_VERSION,
        prefix: str = "",
        *args,
        **kwargs,
    ):
        # Build versioned prefix: /api/v1/prefix
        versioned_prefix = f"/api/{version.value}{prefix}"

        # Add version tag if not specified
        tags = kwargs.get("tags", [])
        if not tags:
            kwargs["tags"] = [f"API {version.value.upper()}"]

        super().__init__(prefix=versioned_prefix, *args, **kwargs)
        self.api_version = version


def create_versioned_routers(
    prefix: str,
    versions: list[APIVersion] | None = None,
    **kwargs,
) -> dict[APIVersion, VersionedRouter]:
    """
    Create routers for multiple API versions.

    Args:
        prefix: Base path prefix (e.g., "/fields")
        versions: List of versions to support (default: SUPPORTED_VERSIONS)
        **kwargs: Additional router arguments

    Returns:
        Dictionary mapping version to router

    Example:
        routers = create_versioned_routers("/fields", tags=["Fields"])
        v1_router = routers[APIVersion.V1]
    """
    if versions is None:
        versions = SUPPORTED_VERSIONS

    return {v: VersionedRouter(version=v, prefix=prefix, **kwargs) for v in versions}


# ═══════════════════════════════════════════════════════════════════════════════
# Version Dependency
# ═══════════════════════════════════════════════════════════════════════════════


def get_api_version(request: Request) -> APIVersion:
    """
    FastAPI dependency to get current API version.

    Usage:
        @router.get("/fields")
        async def list_fields(version: APIVersion = Depends(get_api_version)):
            if version == APIVersion.V1:
                return v1_response
            return v2_response
    """
    return getattr(request.state, "api_version", DEFAULT_VERSION) or DEFAULT_VERSION


def require_version(
    min_version: APIVersion | None = None,
    max_version: APIVersion | None = None,
) -> Callable:
    """
    Create dependency that requires specific API version range.

    Args:
        min_version: Minimum required version (inclusive)
        max_version: Maximum allowed version (inclusive)

    Usage:
        @router.get(
            "/new-feature",
            dependencies=[Depends(require_version(min_version=APIVersion.V2))]
        )
        async def new_feature():
            ...
    """

    async def version_check(request: Request) -> APIVersion:
        version = get_api_version(request)

        if min_version and version.value < min_version.value:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "version_too_low",
                    "message_en": f"This endpoint requires API version {min_version.value} or higher",
                    "message_ar": f"هذا الطريق يتطلب إصدار API {min_version.value} أو أعلى",
                    "current_version": version.value,
                    "minimum_version": min_version.value,
                },
            )

        if max_version and version.value > max_version.value:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "version_too_high",
                    "message_en": f"This endpoint is not available in API version {version.value}",
                    "message_ar": f"هذا الطريق غير متاح في إصدار API {version.value}",
                    "current_version": version.value,
                    "maximum_version": max_version.value,
                },
            )

        return version

    return version_check


# ═══════════════════════════════════════════════════════════════════════════════
# Version Info Endpoint
# ═══════════════════════════════════════════════════════════════════════════════


def get_version_info() -> dict:
    """
    Get API version information for documentation.

    Returns:
        Dictionary with version details
    """
    return {
        "supported_versions": [v.value for v in SUPPORTED_VERSIONS],
        "default_version": DEFAULT_VERSION.value,
        "latest_version": APIVersion.latest().value,
        "deprecated_versions": [v.value for v in DEPRECATED_VERSIONS],
        "version_format": "/api/v{N}/...",
        "examples": {
            "v1_fields": "/api/v1/fields",
            "v1_farms": "/api/v1/farms",
            "unversioned": "/api/fields (defaults to latest)",
        },
    }


# Version info router (unversioned, for documentation)
version_router = APIRouter(prefix="/api", tags=["API Info"])


@version_router.get("/versions", summary="Get API version information")
async def api_versions():
    """
    Get information about supported API versions.

    Returns list of supported versions, default version, and deprecation info.
    """
    return get_version_info()


@version_router.get("/v1", summary="API v1 root")
async def api_v1_root():
    """API v1 root endpoint"""
    return {
        "version": "v1",
        "status": "stable",
        "documentation": "/docs",
        "message_en": "Welcome to SAHOOL API v1",
        "message_ar": "مرحبا بك في API سهول الإصدار الأول",
    }
