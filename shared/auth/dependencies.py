"""
FastAPI Authentication Dependencies for SAHOOL Platform
Dependency injection for authentication and authorization
"""

import logging
import time
from collections import defaultdict
from functools import wraps
from typing import Callable, Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .config import config
from .jwt_handler import verify_token
from .models import AuthErrors, AuthException, User
from .user_cache import get_user_cache
from .user_repository import get_user_repository

# Logger setup
logger = logging.getLogger(__name__)

# OAuth2 scheme for token extraction
oauth2_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(oauth2_scheme),
    request: Request = None,
) -> User:
    """
    Get the current authenticated user from the JWT token.

    This dependency:
    1. Extracts and verifies the JWT token
    2. Checks cache for user status (if Redis available)
    3. Validates user exists in database
    4. Validates user status (active, verified, not deleted/suspended)
    5. Logs failed authentication attempts

    Args:
        credentials: HTTP Authorization credentials (Bearer token)
        request: FastAPI request object

    Returns:
        User object with authenticated user information

    Raises:
        HTTPException: If token is missing, invalid, or expired

    Example:
        ```python
        @app.get("/profile")
        async def get_profile(user: User = Depends(get_current_user)):
            return {"user_id": user.id, "email": user.email}
        ```
    """
    if not credentials:
        logger.warning("Authentication failed: Missing token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=AuthErrors.MISSING_TOKEN.en,
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        token = credentials.credentials
        payload = verify_token(token)
        user_id = payload.user_id

        # Check cache first for user status
        cache = get_user_cache()
        cached_user = None

        if cache:
            cached_user = await cache.get_user_status(user_id)

            if cached_user:
                # Validate cached user status
                if not cached_user.get("is_active", False):
                    logger.warning(f"Authentication failed: User {user_id} is inactive (cached)")
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=AuthErrors.ACCOUNT_DISABLED.en,
                    )

                if not cached_user.get("is_verified", False):
                    logger.warning(f"Authentication failed: User {user_id} is not verified (cached)")
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=AuthErrors.ACCOUNT_NOT_VERIFIED.en,
                    )

                # Create User object from cache
                user = User(
                    id=user_id,
                    email=cached_user.get("email", ""),
                    roles=cached_user.get("roles", payload.roles),
                    tenant_id=cached_user.get("tenant_id", payload.tenant_id),
                    permissions=payload.permissions,
                    is_active=cached_user.get("is_active", True),
                    is_verified=cached_user.get("is_verified", True),
                )

                logger.debug(f"User {user_id} authenticated successfully (from cache)")

                if request:
                    request.state.user = user

                return user

        # Cache miss or no cache - check database
        repository = get_user_repository()

        if repository:
            user_data = await repository.get_user_validation_data(user_id)

            if not user_data:
                logger.warning(f"Authentication failed: User {user_id} not found in database")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=AuthErrors.INVALID_TOKEN.en,
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # Check if user is deleted
            if user_data.is_deleted:
                logger.warning(f"Authentication failed: User {user_id} is deleted")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=AuthErrors.ACCOUNT_DISABLED.en,
                )

            # Check if user is suspended
            if user_data.is_suspended:
                logger.warning(f"Authentication failed: User {user_id} is suspended")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=AuthErrors.ACCOUNT_DISABLED.en,
                )

            # Check if user is active
            if not user_data.is_active:
                logger.warning(f"Authentication failed: User {user_id} is inactive")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=AuthErrors.ACCOUNT_DISABLED.en,
                )

            # Check if user is verified
            if not user_data.is_verified:
                logger.warning(f"Authentication failed: User {user_id} is not verified")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=AuthErrors.ACCOUNT_NOT_VERIFIED.en,
                )

            # Update cache
            if cache:
                await cache.set_user_status(
                    user_id=user_id,
                    is_active=user_data.is_active,
                    is_verified=user_data.is_verified,
                    roles=user_data.roles,
                    email=user_data.email,
                    tenant_id=user_data.tenant_id,
                )

            # Create User object from database
            user = User(
                id=user_id,
                email=user_data.email,
                roles=user_data.roles,
                tenant_id=user_data.tenant_id,
                permissions=payload.permissions,
                is_active=user_data.is_active,
                is_verified=user_data.is_verified,
            )

            logger.info(f"User {user_id} authenticated successfully (from database)")

        else:
            # No database available - create user from token only
            logger.warning("No user repository available - using token data only")
            user = User(
                id=user_id,
                email="",
                roles=payload.roles,
                tenant_id=payload.tenant_id,
                permissions=payload.permissions,
            )

            logger.info(f"User {user_id} authenticated successfully (token only)")

        # Store user in request state
        if request:
            request.state.user = user

        return user

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except AuthException as e:
        logger.warning(f"Authentication failed: {e.error.en}")
        raise HTTPException(
            status_code=e.status_code,
            detail=e.error.en,
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Authentication error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=AuthErrors.INVALID_TOKEN.en,
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_active_user(
    user: User = Depends(get_current_user),
) -> User:
    """
    Get the current active user.

    This dependency ensures the user account is active.

    Args:
        user: User object from get_current_user dependency

    Returns:
        User object if account is active

    Raises:
        HTTPException: If account is disabled

    Example:
        ```python
        @app.get("/dashboard")
        async def dashboard(user: User = Depends(get_current_active_user)):
            return {"message": f"Welcome {user.email}"}
        ```
    """
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=AuthErrors.ACCOUNT_DISABLED.en,
        )

    return user


def require_roles(*required_roles: str) -> Callable:
    """
    Decorator/dependency to require specific roles.

    Args:
        *required_roles: One or more role names required

    Returns:
        Dependency function that checks user roles

    Raises:
        HTTPException: If user doesn't have required roles

    Example:
        ```python
        @app.post("/admin/settings")
        async def update_settings(
            user: User = Depends(require_roles("admin"))
        ):
            return {"message": "Settings updated"}

        # Or with multiple roles (user needs at least one)
        @app.get("/reports")
        async def get_reports(
            user: User = Depends(require_roles("admin", "manager"))
        ):
            return {"reports": [...]}
        ```
    """
    async def role_checker(user: User = Depends(get_current_active_user)) -> User:
        if not user.has_any_role(*required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=AuthErrors.INSUFFICIENT_PERMISSIONS.en,
            )
        return user

    return role_checker


def require_permissions(*required_permissions: str) -> Callable:
    """
    Decorator/dependency to require specific permissions.

    Args:
        *required_permissions: One or more permission names required

    Returns:
        Dependency function that checks user permissions

    Raises:
        HTTPException: If user doesn't have required permissions

    Example:
        ```python
        @app.delete("/farms/{farm_id}")
        async def delete_farm(
            farm_id: str,
            user: User = Depends(require_permissions("farm:delete"))
        ):
            return {"message": "Farm deleted"}
        ```
    """
    async def permission_checker(user: User = Depends(get_current_active_user)) -> User:
        if not any(user.has_permission(perm) for perm in required_permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=AuthErrors.INSUFFICIENT_PERMISSIONS.en,
            )
        return user

    return permission_checker


def require_farm_access(farm_id_param: str = "farm_id") -> Callable:
    """
    Decorator/dependency to require access to a specific farm.

    Args:
        farm_id_param: Name of the path parameter containing farm_id

    Returns:
        Dependency function that checks farm access

    Raises:
        HTTPException: If user doesn't have access to the farm

    Example:
        ```python
        @app.get("/farms/{farm_id}/fields")
        async def get_farm_fields(
            farm_id: str,
            user: User = Depends(require_farm_access())
        ):
            return {"fields": [...]}
        ```
    """
    async def farm_access_checker(
        request: Request,
        user: User = Depends(get_current_active_user)
    ) -> User:
        farm_id = request.path_params.get(farm_id_param)

        if not farm_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing {farm_id_param} parameter",
            )

        # Admin users have access to all farms
        if user.has_role("admin"):
            return user

        if not user.has_farm_access(farm_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=AuthErrors.INSUFFICIENT_PERMISSIONS.en,
            )

        return user

    return farm_access_checker


# Rate Limiting Implementation
class RateLimiter:
    """
    In-memory rate limiter with logging.
    محدد المعدل في الذاكرة مع التسجيل.
    """

    def __init__(
        self,
        requests: int = 100,
        window_seconds: int = 60,
    ):
        self.requests = requests
        self.window_seconds = window_seconds
        self.storage: dict = defaultdict(list)
        self.violation_count: dict = defaultdict(int)

    def is_allowed(self, key: str) -> tuple[bool, int]:
        """
        Check if request is allowed.

        Args:
            key: Rate limit key (usually user ID or IP)

        Returns:
            Tuple of (is_allowed, remaining_requests)
        """
        now = time.time()
        window_start = now - self.window_seconds

        # Clean old requests
        self.storage[key] = [
            timestamp for timestamp in self.storage[key]
            if timestamp > window_start
        ]

        current_count = len(self.storage[key])
        remaining = max(0, self.requests - current_count)

        # Check limit
        if current_count >= self.requests:
            self.violation_count[key] += 1
            logger.warning(
                f"Rate limit exceeded for {key}: "
                f"{current_count}/{self.requests} requests in {self.window_seconds}s "
                f"(violation #{self.violation_count[key]})"
            )
            return False, 0

        # Add current request
        self.storage[key].append(now)
        return True, remaining - 1

    def get_violation_count(self, key: str) -> int:
        """Get number of rate limit violations for a key"""
        return self.violation_count.get(key, 0)

    def reset_violations(self, key: str) -> None:
        """Reset violation count for a key"""
        if key in self.violation_count:
            del self.violation_count[key]


# Global rate limiter instance
_rate_limiter = RateLimiter(
    requests=config.RATE_LIMIT_REQUESTS,
    window_seconds=config.RATE_LIMIT_WINDOW_SECONDS,
)


async def rate_limit_dependency(
    request: Request,
    user: User = Depends(get_current_user),
) -> User:
    """
    Rate limiting dependency based on user ID.

    Args:
        request: FastAPI request object
        user: Authenticated user

    Returns:
        User object if rate limit not exceeded

    Raises:
        HTTPException: If rate limit exceeded

    Example:
        ```python
        @app.post("/api/heavy-operation")
        async def heavy_operation(
            user: User = Depends(rate_limit_dependency)
        ):
            return {"message": "Operation completed"}
        ```
    """
    if not config.RATE_LIMIT_ENABLED:
        return user

    key = f"rate_limit:{user.id}"
    allowed, remaining = _rate_limiter.is_allowed(key)

    if not allowed:
        violation_count = _rate_limiter.get_violation_count(key)
        logger.error(
            f"Rate limit exceeded for user {user.id} "
            f"(total violations: {violation_count})"
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=AuthErrors.RATE_LIMIT_EXCEEDED.en,
            headers={
                "X-RateLimit-Limit": str(_rate_limiter.requests),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(int(time.time() + _rate_limiter.window_seconds)),
            },
        )

    # Add rate limit headers to response
    if request:
        request.state.rate_limit_remaining = remaining

    logger.debug(f"Rate limit check passed for user {user.id} ({remaining} remaining)")

    return user


def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(oauth2_scheme),
) -> Optional[User]:
    """
    Get the current user if authenticated, otherwise None.

    This is useful for endpoints that work differently for authenticated vs unauthenticated users.

    Args:
        credentials: HTTP Authorization credentials (Bearer token)

    Returns:
        User object if authenticated, None otherwise

    Example:
        ```python
        @app.get("/content")
        async def get_content(user: Optional[User] = Depends(get_optional_user)):
            if user:
                return {"content": "premium content", "user": user.email}
            else:
                return {"content": "public content"}
        ```
    """
    if not credentials:
        return None

    try:
        token = credentials.credentials
        payload = verify_token(token)

        return User(
            id=payload.user_id,
            email="",
            roles=payload.roles,
            tenant_id=payload.tenant_id,
            permissions=payload.permissions,
        )
    except:
        return None
