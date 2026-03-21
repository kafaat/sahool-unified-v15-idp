"""
FastAPI Authentication Dependencies for SAHOOL Platform
Dependency injection for authentication and authorization
"""

import logging
import time
from collections import defaultdict
from collections.abc import Callable

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .config import config
from .jwt_handler import verify_token
from .models import AuthErrors, AuthException, User
from .token_revocation import is_token_revoked
from .user_cache import get_user_cache
from .user_repository import get_user_repository

# Logger setup
logger = logging.getLogger(__name__)

# OAuth2 scheme for token extraction
oauth2_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(oauth2_scheme),
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

        # Check token revocation before any other validation
        if config.TOKEN_REVOCATION_ENABLED:
            try:
                revoked, reason = await is_token_revoked(
                    jti=payload.jti,
                    user_id=user_id,
                    tenant_id=payload.tenant_id,
                    issued_at=payload.iat.timestamp() if payload.iat else None,
                )
                if revoked:
                    logger.warning(
                        f"Authentication failed: Token revoked for user {user_id}, reason={reason}"
                    )
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail=AuthErrors.TOKEN_REVOKED.en,
                        headers={"WWW-Authenticate": "Bearer"},
                    )
            except HTTPException:
                raise
            except Exception as e:
                # Fail closed: reject token if revocation store is unavailable
                logger.error(f"SECURITY: Token revocation check failed, failing closed: {e}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=AuthErrors.TOKEN_REVOKED.en,
                    headers={"WWW-Authenticate": "Bearer"},
                )

        # Check cache first for user status
        cache = get_user_cache()
        cached_user = None

        if cache:
            cached_user = await cache.get_user_status(user_id)

            if cached_user:
                # Validate cached user status — check ALL denial conditions.
                # Security: defaults are fail-closed (False/True) so that a
                # missing key rejects rather than admits the user.
                if cached_user.get("is_deleted", False):
                    logger.warning(f"Authentication failed: User {user_id} is deleted (cached)")
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=AuthErrors.ACCOUNT_DISABLED.en,
                    )

                if cached_user.get("is_suspended", False):
                    logger.warning(f"Authentication failed: User {user_id} is suspended (cached)")
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=AuthErrors.ACCOUNT_DISABLED.en,
                    )

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

                # Create User object from cache — use fail-closed defaults
                user = User(
                    id=user_id,
                    email=cached_user.get("email", ""),
                    roles=cached_user.get("roles", payload.roles),
                    tenant_id=cached_user.get("tenant_id", payload.tenant_id),
                    permissions=payload.permissions,
                    is_active=cached_user.get("is_active", False),
                    is_verified=cached_user.get("is_verified", False),
                )

                logger.debug(f"User {user_id} authenticated successfully (from cache)")

                if request:
                    request.state.user = user
                    request.state.token_payload = payload

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

            # Update cache — include all status fields so cached path
            # can perform the same denial checks as the DB path.
            if cache:
                cache_kwargs = {
                    "user_id": user_id,
                    "is_active": user_data.is_active,
                    "is_verified": user_data.is_verified,
                    "roles": user_data.roles,
                    "email": user_data.email,
                    "tenant_id": user_data.tenant_id,
                }
                # Pass is_deleted/is_suspended if the cache accepts them
                if hasattr(user_data, "is_deleted"):
                    cache_kwargs["is_deleted"] = user_data.is_deleted
                if hasattr(user_data, "is_suspended"):
                    cache_kwargs["is_suspended"] = user_data.is_suspended
                try:
                    await cache.set_user_status(**cache_kwargs)
                except TypeError:
                    # Older cache implementation may not accept new fields;
                    # fall back to the original signature.
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

        # Store user and token payload in request state
        if request:
            request.state.user = user
            request.state.token_payload = payload

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


async def require_2fa_verified(
    request: Request,
    user: User = Depends(get_current_user),
) -> User:
    """
    Dependency that enforces 2FA verification.

    Use on sensitive endpoints that require completed 2FA.
    Checks the JWT claim 'twofa_verified' to ensure the user
    has passed 2FA during the current session.

    Args:
        request: FastAPI request object (injected automatically)
        user: Authenticated user from get_current_user

    Returns:
        User object if 2FA is verified

    Raises:
        HTTPException 403: If 2FA is required but not verified

    Example:
        ```python
        @app.post("/admin/danger")
        async def danger(user: User = Depends(require_2fa_verified)):
            ...
        ```
    """
    # Fail-closed: if token_payload is missing from request state,
    # we cannot verify 2FA status. get_current_user always sets it
    # when request is available, so this should not happen in practice.
    if not hasattr(request.state, "token_payload"):
        logger.warning("require_2fa_verified: token_payload missing from request state")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Two-factor authentication is required for this operation",
        )

    payload = request.state.token_payload
    if getattr(payload, "twofa_required", False) and not getattr(payload, "twofa_verified", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Two-factor authentication is required for this operation",
        )
    return user


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


def enforce_tenant(user: User, requested_tenant_id: str | None = None) -> str:
    """
    Enforce tenant isolation by validating the user's tenant access.

    Returns the validated tenant_id to use for database queries.
    If requested_tenant_id is provided, validates that the user has access.
    Otherwise, returns the user's own tenant_id.

    Args:
        user: Authenticated user from get_current_user
        requested_tenant_id: Optional tenant_id from request path/body

    Returns:
        str: The validated tenant_id

    Raises:
        HTTPException 400: If no tenant_id is available
        HTTPException 403: If user doesn't have access to requested tenant

    Example:
        ```python
        @app.get("/fields")
        async def list_fields(user: User = Depends(get_current_user)):
            tenant_id = enforce_tenant(user)
            return await db.query("SELECT * FROM fields WHERE tenant_id = $1", tenant_id)
        ```
    """
    user_tenant = user.tenant_id

    if not user_tenant and not requested_tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tenant context is required but not available",
        )

    if requested_tenant_id:
        # Only super_admin can access other tenants (cross-tenant access).
        # Regular admin is scoped to their own tenant.
        # الأمان: فقط المشرف الأعلى يمكنه الوصول عبر المستأجرين
        if "super_admin" in (user.roles or []):
            return requested_tenant_id
        # Non-super_admin users must match their own tenant
        if user_tenant and user_tenant != requested_tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: tenant mismatch",
            )
        return requested_tenant_id

    # At this point: no requested_tenant_id, and user_tenant is set
    # (the case where both are empty raises HTTPException above)
    assert user_tenant is not None  # guaranteed by the guard above
    return user_tenant


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

    async def farm_access_checker(request: Request, user: User = Depends(get_current_active_user)) -> User:
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
        self.storage[key] = [timestamp for timestamp in self.storage[key] if timestamp > window_start]

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
        logger.error(f"Rate limit exceeded for user {user.id} (total violations: {violation_count})")
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


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(oauth2_scheme),
) -> User | None:
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

        # Check token revocation for optional auth too
        if config.TOKEN_REVOCATION_ENABLED:
            try:
                revoked, _reason = await is_token_revoked(
                    jti=payload.jti,
                    user_id=payload.user_id,
                    tenant_id=payload.tenant_id,
                    issued_at=payload.iat.timestamp() if payload.iat else None,
                )
                if revoked:
                    logger.debug(f"Optional auth: token revoked for user {payload.user_id}")
                    return None
            except Exception:
                # Fail closed for optional auth: treat as unauthenticated
                return None

        return User(
            id=payload.user_id,
            email="",
            roles=payload.roles,
            tenant_id=payload.tenant_id,
            permissions=payload.permissions,
        )
    except AuthException as e:
        logger.debug(f"Optional auth failed: {e.error.code}")
        return None
    except Exception as e:
        logger.warning(f"Unexpected error in optional auth: {type(e).__name__}: {e}")
        return None
