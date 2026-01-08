# Token Revocation Guide for Python FastAPI Services
# دليل إلغاء الرموز لخدمات Python FastAPI

This guide explains how to use the token revocation system in SAHOOL Python FastAPI services.

## Overview

The token revocation system provides:
- **JTI (JWT ID) tracking** - Revoke individual tokens
- **Token family tracking** - Revoke related tokens (refresh token rotation)
- **User-level revocation** - Revoke all tokens for a user
- **Tenant-level revocation** - Revoke all tokens for a tenant
- **Redis-backed storage** - Fast, distributed revocation checks

## Architecture

The system consists of three main components:

1. **RedisTokenRevocationStore** (`token_revocation.py`) - Core revocation logic
2. **TokenRevocationMiddleware** (`revocation_middleware.py`) - FastAPI middleware
3. **JWT enhancements** (`jwt.py`) - JTI generation and token family support

## Setup

### 1. Install Dependencies

Add to your service's `requirements.txt`:
```
redis[hiredis]==5.2.1
```

### 2. Environment Variables

Configure Redis connection:
```bash
# Full URL (recommended)
REDIS_URL=redis://localhost:6379/0

# Or individual components
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=your_password_here  # Optional
```

### 3. Initialize in Your Service

Add to your FastAPI application's `main.py`:

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

# Import token revocation
try:
    from auth.token_revocation import get_revocation_store
    from auth.revocation_middleware import TokenRevocationMiddleware
    REVOCATION_AVAILABLE = True
except ImportError:
    REVOCATION_AVAILABLE = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    if REVOCATION_AVAILABLE:
        try:
            revocation_store = get_revocation_store()
            await revocation_store.initialize()
            app.state.revocation_store = revocation_store
            print("✅ Token revocation store initialized")
        except Exception as e:
            print(f"⚠️ Token revocation failed: {e}")

    yield

    # Shutdown
    if getattr(app.state, "revocation_store", None):
        await app.state.revocation_store.close()


app = FastAPI(lifespan=lifespan)

# Add revocation middleware
if REVOCATION_AVAILABLE:
    app.add_middleware(
        TokenRevocationMiddleware,
        exempt_paths=["/healthz", "/docs", "/redoc", "/openapi.json"],
    )
```

## Usage Examples

### 1. Creating Tokens with JTI

The JWT functions now return tuples with JTI for tracking:

```python
from auth.jwt import create_access_token, create_refresh_token

# Create access token
token, jti = create_access_token(
    user_id="user123",
    email="user@example.com",
    tenant_id="tenant456",
    roles=["farmer"],
)

# Create refresh token
refresh_token, refresh_jti, family_id = create_refresh_token(
    user_id="user123",
    tenant_id="tenant456",
)

# Store JTI for later revocation
# You might want to store these in your database
```

### 2. Revoking Individual Tokens

```python
from fastapi import Request

@app.post("/auth/logout")
async def logout(request: Request, token_data: TokenData = Depends(get_token_data)):
    """Logout and revoke the current token"""

    revocation_store = request.app.state.revocation_store

    # Revoke the current access token
    if token_data.jti:
        success = await revocation_store.revoke_token(
            jti=token_data.jti,
            expires_in=1800,  # Keep revocation for 30 minutes (longer than token TTL)
            reason="user_logout",
            user_id=token_data.user_id,
            tenant_id=token_data.tenant_id,
        )

    return {"message": "Logged out successfully"}
```

### 3. Revoking All User Tokens

Useful for:
- Password changes
- Security incidents
- Account suspension

```python
@app.post("/admin/users/{user_id}/revoke-tokens")
async def revoke_user_tokens(
    request: Request,
    user_id: str,
    current_user: User = Depends(require_admin),
):
    """Revoke all tokens for a user (admin only)"""

    revocation_store = request.app.state.revocation_store

    success = await revocation_store.revoke_all_user_tokens(
        user_id=user_id,
        reason="admin_revocation",
    )

    return {
        "message": f"All tokens revoked for user {user_id}",
        "success": success,
    }
```

### 4. Revoking Tenant Tokens

Useful for:
- Tenant suspension
- Plan downgrades
- Security lockouts

```python
@app.post("/admin/tenants/{tenant_id}/revoke-tokens")
async def revoke_tenant_tokens(
    request: Request,
    tenant_id: str,
    current_user: User = Depends(require_super_admin),
):
    """Revoke all tokens for a tenant (super admin only)"""

    revocation_store = request.app.state.revocation_store

    success = await revocation_store.revoke_all_tenant_tokens(
        tenant_id=tenant_id,
        reason="tenant_suspended",
    )

    return {
        "message": f"All tokens revoked for tenant {tenant_id}",
        "success": success,
    }
```

### 5. Refresh Token Rotation

Implement secure refresh token rotation:

```python
@app.post("/auth/refresh")
async def refresh_token(
    request: Request,
    refresh_token: str,
):
    """Exchange refresh token for new access token"""

    try:
        # Decode refresh token
        token_data = decode_token(refresh_token)

        if token_data.token_type != "refresh":
            raise HTTPException(400, "Invalid token type")

        revocation_store = request.app.state.revocation_store

        # Check if token or family is revoked
        result = await revocation_store.is_revoked(
            jti=token_data.jti,
            family_id=token_data.family_id,
            user_id=token_data.user_id,
            issued_at=token_data.iat.timestamp(),
        )

        if result.is_revoked:
            # Possible token reuse attack!
            # Revoke the entire token family
            if token_data.family_id:
                await revocation_store.revoke_token_family(
                    family_id=token_data.family_id,
                    reason="possible_token_reuse",
                )

            raise HTTPException(401, "Token has been revoked")

        # Revoke the old refresh token
        if token_data.jti:
            await revocation_store.revoke_token(
                jti=token_data.jti,
                expires_in=86400 * 7,  # 7 days
                reason="refresh_rotation",
            )

        # Issue new tokens with same family_id
        new_access_token, access_jti = create_access_token(
            user_id=token_data.user_id,
            tenant_id=token_data.tenant_id,
        )

        new_refresh_token, refresh_jti, family_id = create_refresh_token(
            user_id=token_data.user_id,
            tenant_id=token_data.tenant_id,
            family_id=token_data.family_id,  # Keep same family
        )

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
        }

    except ValueError as e:
        raise HTTPException(401, str(e))
```

### 6. Manual Revocation Check

If you need to check revocation status manually:

```python
from auth.revocation_middleware import check_token_revocation

@app.get("/internal/check-token")
async def check_token(token: str):
    """Internal endpoint to check if a token is revoked"""

    is_revoked, reason = await check_token_revocation(token)

    return {
        "is_revoked": is_revoked,
        "reason": reason,
    }
```

### 7. Health Check

Add revocation store health check to your service:

```python
@app.get("/healthz")
async def health_check(request: Request):
    """Service health check including revocation store"""

    health = {
        "service": "ok",
        "revocation_store": "unknown",
    }

    if revocation_store := getattr(request.app.state, "revocation_store", None):
        if await revocation_store.health_check():
            health["revocation_store"] = "ok"
        else:
            health["revocation_store"] = "degraded"

    return health
```

### 8. Statistics and Monitoring

Get revocation statistics:

```python
@app.get("/admin/revocation/stats")
async def get_revocation_stats(
    request: Request,
    current_user: User = Depends(require_admin),
):
    """Get token revocation statistics"""

    revocation_store = request.app.state.revocation_store
    stats = await revocation_store.get_stats()

    return {
        "initialized": stats.initialized,
        "revoked_tokens": stats.revoked_tokens,
        "revoked_users": stats.revoked_users,
        "revoked_tenants": stats.revoked_tenants,
        "redis_url": stats.redis_url,
    }
```

## Redis Key Structure

The system uses the following Redis key prefixes:

- `revoked:token:{jti}` - Individual token revocations
- `revoked:user:{user_id}` - User-level revocations
- `revoked:tenant:{tenant_id}` - Tenant-level revocations
- `revoked:family:{family_id}` - Token family revocations

All keys have TTL (Time To Live) to automatically expire and clean up.

## Security Best Practices

1. **Always use JTI** - Every token should have a unique JTI for tracking
2. **Set appropriate TTLs** - Revocation TTL should be longer than token lifetime
3. **Implement refresh token rotation** - Prevent token reuse attacks
4. **Monitor for suspicious patterns** - Track revocation reasons
5. **Use token families** - Detect and prevent token theft
6. **Fail open on Redis errors** - Maintain availability over perfect security

## Performance Considerations

- **Redis is fast** - Revocation checks add minimal latency (~1-2ms)
- **Connection pooling** - Redis client maintains connection pool
- **Async operations** - All operations are non-blocking
- **TTL for cleanup** - Expired revocations are automatically cleaned up

## Troubleshooting

### Redis Connection Failed

If Redis is unavailable, the service will:
1. Log a warning
2. Continue running without revocation checks
3. Accept all tokens (fail open)

This ensures service availability even if Redis is down.

### High Memory Usage

If Redis memory grows too large:
1. Check TTL settings - ensure keys expire
2. Monitor revocation patterns
3. Consider Redis maxmemory policies
4. Use Redis persistence if needed

### Token Still Valid After Revocation

Common causes:
1. Token cached in client
2. Revocation propagation delay
3. Wrong JTI used
4. Redis connection issue

Check:
- Token JTI matches revocation JTI
- Redis connection is healthy
- Middleware is properly configured

## Migration from Existing Systems

If you have existing tokens without JTI:

1. **Gradual migration** - New tokens get JTI, old tokens expire naturally
2. **User-level revocation** - Use user/tenant revocation for old tokens
3. **Force re-login** - Optionally force all users to re-authenticate

## Examples in Existing Services

See these files for reference:
- `/apps/services/advisory-service/src/main.py` - Advisory service integration
- `/apps/services/ai-advisor/src/main.py` - AI advisor integration
- `/apps/services/shared/auth/token_revocation.py` - Core implementation
- `/apps/services/shared/auth/revocation_middleware.py` - Middleware implementation

## Related Documentation

- NestJS implementation: `/apps/services/user-service/src/utils/token-revocation.ts`
- JWT configuration: `/apps/services/shared/auth/jwt.py`
- Authentication guide: `/apps/services/shared/auth/README.md`
