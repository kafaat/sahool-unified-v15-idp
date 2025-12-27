# Token Revocation System
# نظام إلغاء الرموز

A comprehensive Redis-based token revocation system for SAHOOL platform with support for both Python (FastAPI) and TypeScript (NestJS).

## Overview | نظرة عامة

This token revocation system provides a robust, distributed solution for invalidating JWT tokens before their natural expiration. It uses Redis as a backend for fast, distributed token blacklisting with automatic TTL (Time-To-Live) management.

### Key Features | الميزات الرئيسية

✅ **Redis-Based Storage**: High-performance, distributed token revocation
✅ **Multiple Revocation Strategies**:
   - Individual token revocation (by JTI)
   - User-level revocation (all user tokens)
   - Tenant-level revocation (all tenant tokens)
✅ **Automatic TTL Management**: Tokens auto-expire from blacklist
✅ **Dual Language Support**: Python and TypeScript implementations
✅ **Fail-Safe Design**: Graceful degradation on Redis errors
✅ **REST API Endpoints**: Complete API for token management
✅ **Middleware Integration**: Automatic revocation checking
✅ **Audit Logging**: Track all revocation activities
✅ **Health Monitoring**: Built-in health checks

## Architecture | البنية المعمارية

```
┌─────────────────────────────────────────────────────────┐
│                    Client Application                    │
└─────────────────────┬───────────────────────────────────┘
                      │
                      │ JWT Token
                      ▼
┌─────────────────────────────────────────────────────────┐
│              Authentication Middleware                   │
│  (JWTAuthMiddleware / JwtAuthGuard)                     │
└─────────────────────┬───────────────────────────────────┘
                      │
                      │ Verify Token
                      ▼
┌─────────────────────────────────────────────────────────┐
│           Token Revocation Middleware/Guard             │
│  (TokenRevocationMiddleware / TokenRevocationGuard)     │
└─────────────────────┬───────────────────────────────────┘
                      │
                      │ Check Revocation
                      ▼
┌─────────────────────────────────────────────────────────┐
│          Redis Token Revocation Store                   │
│  (RedisTokenRevocationStore)                            │
└─────────────────────┬───────────────────────────────────┘
                      │
                      │ Redis Operations
                      ▼
┌─────────────────────────────────────────────────────────┐
│                    Redis Server                          │
│  Keys: revoked:token:*, revoked:user:*,                 │
│        revoked:tenant:*                                 │
└─────────────────────────────────────────────────────────┘
```

## Components | المكونات

### Python Components

1. **`token_revocation.py`**: Core revocation store implementation
2. **`revocation_middleware.py`**: FastAPI middleware for checking revoked tokens
3. **`revocation_api.py`**: REST API endpoints for token management

### TypeScript Components

1. **`token-revocation.ts`**: Core revocation store implementation (NestJS)
2. **`token-revocation.guard.ts`**: NestJS guard for checking revoked tokens
3. **`revocation.controller.ts`**: REST API endpoints for token management

## Installation | التثبيت

### Prerequisites | المتطلبات الأساسية

- Redis 6.0 or higher
- Python 3.9+ (for Python implementation)
- Node.js 16+ (for TypeScript implementation)

### Python Dependencies

```bash
pip install redis[asyncio]
```

### TypeScript Dependencies

```bash
npm install redis @nestjs/jwt
```

### Redis Setup

```bash
# Using Docker
docker run -d \
  --name redis \
  -p 6379:6379 \
  redis:7-alpine

# Or with password
docker run -d \
  --name redis \
  -p 6379:6379 \
  redis:7-alpine \
  redis-server --requirepass your_password
```

## Configuration | الإعدادات

### Environment Variables

```bash
# Redis Configuration
REDIS_URL=redis://localhost:6379/0
# Or individual settings
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=your_password  # Optional

# Token Revocation
TOKEN_REVOCATION_ENABLED=true

# JWT Configuration
JWT_SECRET=your_secret_key_here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
JWT_ISSUER=sahool-platform
JWT_AUDIENCE=sahool-api
```

## Usage | الاستخدام

### Python (FastAPI)

#### 1. Setup Application

```python
from fastapi import FastAPI
from shared.auth.middleware import JWTAuthMiddleware
from shared.auth.revocation_middleware import TokenRevocationMiddleware
from shared.auth.revocation_api import router as revocation_router

app = FastAPI()

# Add middleware (order matters!)
app.add_middleware(JWTAuthMiddleware)
app.add_middleware(TokenRevocationMiddleware)

# Include revocation API
app.include_router(revocation_router)
```

#### 2. Revoke Token on Logout

```python
from shared.auth.token_revocation import revoke_token

@app.post("/logout")
async def logout(request: Request):
    token = extract_token(request)
    payload = verify_token(token)

    await revoke_token(
        jti=payload.jti,
        expires_in=3600,
        reason="user_logout"
    )

    return {"message": "Logged out successfully"}
```

#### 3. Revoke All User Tokens

```python
from shared.auth.token_revocation import revoke_all_user_tokens

@app.post("/change-password")
async def change_password(user_id: str):
    # Update password...

    # Revoke all existing tokens
    await revoke_all_user_tokens(
        user_id=user_id,
        reason="password_change"
    )

    return {"message": "Password changed"}
```

### TypeScript (NestJS)

#### 1. Setup Application

```typescript
// app.module.ts
import { Module } from '@nestjs/common';
import { APP_GUARD } from '@nestjs/core';
import { TokenRevocationModule } from '@shared/auth/token-revocation';
import { TokenRevocationGuard } from '@shared/auth/token-revocation.guard';
import { RevocationController } from '@shared/auth/revocation.controller';

@Module({
  imports: [TokenRevocationModule],
  controllers: [RevocationController],
  providers: [
    {
      provide: APP_GUARD,
      useClass: TokenRevocationGuard,
    },
  ],
})
export class AppModule {}
```

#### 2. Revoke Token on Logout

```typescript
import { RedisTokenRevocationStore } from '@shared/auth/token-revocation';

@Controller('auth')
export class AuthController {
  constructor(
    private readonly revocationStore: RedisTokenRevocationStore,
  ) {}

  @Post('logout')
  async logout(@Request() req) {
    const payload = this.extractPayload(req);

    await this.revocationStore.revokeToken(payload.jti, {
      expiresIn: 3600,
      reason: 'user_logout',
    });

    return { message: 'Logged out successfully' };
  }
}
```

#### 3. Skip Revocation Check

```typescript
import { SkipRevocationCheck } from '@shared/auth/token-revocation.guard';

@Controller('public')
export class PublicController {
  @Get('data')
  @SkipRevocationCheck()
  async getPublicData() {
    return { data: 'public' };
  }
}
```

## API Endpoints | نقاط نهاية API

All endpoints are prefixed with `/auth/revocation`

### 1. POST `/revoke-current`
Revoke the current token (logout)

**Request Headers:**
```
Authorization: Bearer YOUR_JWT_TOKEN
```

**Response:**
```json
{
  "success": true,
  "message": "Successfully logged out",
  "revokedCount": 1
}
```

### 2. POST `/revoke-all`
Revoke all tokens for current user (logout from all devices)

**Request Headers:**
```
Authorization: Bearer YOUR_JWT_TOKEN
```

**Response:**
```json
{
  "success": true,
  "message": "All your tokens have been revoked. Logged out from all devices."
}
```

### 3. POST `/revoke`
Revoke a specific token by JTI

**Request Headers:**
```
Authorization: Bearer YOUR_JWT_TOKEN
```

**Request Body:**
```json
{
  "jti": "550e8400-e29b-41d4-a716-446655440000",
  "reason": "suspicious_activity"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Token revoked successfully",
  "revokedCount": 1
}
```

### 4. POST `/revoke-user-tokens`
Revoke all tokens for a specific user (Admin only)

**Request Headers:**
```
Authorization: Bearer YOUR_JWT_TOKEN
```

**Request Body:**
```json
{
  "userId": "user-123",
  "reason": "account_compromised"
}
```

**Response:**
```json
{
  "success": true,
  "message": "All tokens revoked for user user-123"
}
```

### 5. POST `/revoke-tenant-tokens`
Revoke all tokens for a tenant (Admin only)

**Request Headers:**
```
Authorization: Bearer YOUR_JWT_TOKEN
```

**Request Body:**
```json
{
  "tenantId": "tenant-456",
  "reason": "security_breach"
}
```

**Response:**
```json
{
  "success": true,
  "message": "All tokens revoked for tenant tenant-456"
}
```

### 6. GET `/status/:jti`
Check if a token is revoked

**Request Headers:**
```
Authorization: Bearer YOUR_JWT_TOKEN
```

**Response:**
```json
{
  "isRevoked": true,
  "reason": "user_logout",
  "revokedAt": 1640000000.0
}
```

### 7. GET `/stats`
Get revocation statistics (Admin only)

**Request Headers:**
```
Authorization: Bearer YOUR_JWT_TOKEN
```

**Response:**
```json
{
  "initialized": true,
  "revokedTokens": 42,
  "revokedUsers": 10,
  "revokedTenants": 2,
  "redisUrl": "localhost:6379/0"
}
```

### 8. GET `/health`
Check service health

**Response:**
```json
{
  "status": "healthy",
  "service": "token_revocation",
  "redis": "connected"
}
```

## Revocation Strategies | استراتيجيات الإلغاء

### 1. Token-Level Revocation (JTI)
Revoke individual tokens by their JWT ID.

**Use Cases:**
- User logout from current device
- Suspicious activity on specific session
- Token refresh invalidation

**Redis Key Pattern:** `revoked:token:{jti}`
**TTL:** Token expiration time

### 2. User-Level Revocation
Revoke all tokens for a specific user.

**Use Cases:**
- Password change
- Account security reset
- Logout from all devices
- Account permissions change

**Redis Key Pattern:** `revoked:user:{user_id}`
**TTL:** 30 days

### 3. Tenant-Level Revocation
Revoke all tokens for all users in a tenant.

**Use Cases:**
- Security breach
- Tenant suspension
- Major configuration changes
- Compliance requirements

**Redis Key Pattern:** `revoked:tenant:{tenant_id}`
**TTL:** 30 days

## Performance Considerations | اعتبارات الأداء

### Latency
- Token revocation check: ~1-2ms (Redis in-memory)
- Token revocation operation: ~2-3ms

### Scalability
- Redis can handle 100,000+ ops/sec
- Use Redis Cluster for high-traffic applications
- Connection pooling is automatic

### Memory Usage
- Each revoked token: ~200 bytes
- Automatic cleanup via TTL
- No memory leaks

## Security Best Practices | أفضل ممارسات الأمان

1. **Always Use HTTPS**: Protect tokens in transit
2. **Set Appropriate TTL**: Match token expiration times
3. **Rate Limit Revocation**: Prevent abuse of revocation endpoints
4. **Audit Logging**: Track all revocation events
5. **Secure Redis**: Use password and network isolation
6. **Fail Open**: Allow access on Redis errors (configurable)
7. **Admin-Only Operations**: Restrict tenant/user revocations to admins

## Monitoring | المراقبة

### Health Checks

```python
# Python
from shared.auth.token_revocation import get_revocation_store

store = await get_revocation_store()
is_healthy = await store.health_check()
```

```typescript
// TypeScript
const isHealthy = await this.revocationStore.healthCheck();
```

### Statistics

```python
# Python
stats = await store.get_stats()
print(f"Revoked tokens: {stats['revoked_tokens']}")
```

```typescript
// TypeScript
const stats = await this.revocationStore.getStats();
console.log(`Revoked tokens: ${stats.revokedTokens}`);
```

### Metrics to Monitor

- Redis connection health
- Number of revoked tokens
- Revocation operation latency
- Redis memory usage
- Failed revocation attempts

## Troubleshooting | استكشاف الأخطاء

### Redis Connection Failed

```bash
# Check Redis is running
docker ps | grep redis

# Test connection
redis-cli ping

# Check logs
docker logs redis-container
```

### Tokens Not Being Revoked

1. Check if revocation is enabled: `TOKEN_REVOCATION_ENABLED=true`
2. Verify Redis connection: Use health check endpoint
3. Check middleware order: Revocation after authentication
4. Verify JTI is present in tokens

### Performance Issues

1. Check Redis memory: `redis-cli info memory`
2. Monitor Redis latency: `redis-cli --latency`
3. Review connection pool settings
4. Consider Redis Cluster for scaling

## Testing | الاختبار

### Unit Tests

```python
# Python
import pytest
from shared.auth.token_revocation import RedisTokenRevocationStore

@pytest.mark.asyncio
async def test_token_revocation():
    store = RedisTokenRevocationStore()
    await store.initialize()

    # Revoke token
    success = await store.revoke_token("test-jti", expires_in=60)
    assert success

    # Check revocation
    is_revoked = await store.is_token_revoked("test-jti")
    assert is_revoked

    await store.close()
```

```typescript
// TypeScript
describe('RedisTokenRevocationStore', () => {
  it('should revoke token', async () => {
    const store = new RedisTokenRevocationStore();
    await store.initialize();

    const success = await store.revokeToken('test-jti', {
      expiresIn: 60,
    });
    expect(success).toBe(true);

    const isRevoked = await store.isTokenRevoked('test-jti');
    expect(isRevoked).toBe(true);

    await store.close();
  });
});
```

### Integration Tests

Test the full flow:
1. Login → Get token
2. Make authenticated request → Success
3. Logout → Token revoked
4. Make authenticated request → Unauthorized

## Migration Guide | دليل الترحيل

### From In-Memory to Redis

```python
# Before (in-memory)
from shared.security.token_revocation import TokenRevocationService
service = TokenRevocationService()

# After (Redis)
from shared.auth.token_revocation import get_revocation_store
store = await get_revocation_store()
```

The API is compatible, so most code should work without changes.

## FAQ | الأسئلة الشائعة

### Q: What happens if Redis is down?
A: By default, the system "fails open" - requests are allowed. You can configure "fail closed" behavior with `fail_open=False`.

### Q: How long are revocations stored?
A: Token revocations are stored until token expiration. User/tenant revocations are stored for 30 days.

### Q: Can I use a different Redis database?
A: Yes, set `REDIS_DB` environment variable.

### Q: Does this work with refresh tokens?
A: Yes, refresh tokens also have JTI and can be revoked.

### Q: What's the performance impact?
A: Minimal (~1-2ms per request). Redis operations are very fast.

### Q: Can I revoke tokens retrospectively?
A: Yes, user-level and tenant-level revocations affect all tokens issued before revocation time.

## Support | الدعم

For issues, questions, or contributions:
- GitHub Issues: [Create an issue](#)
- Documentation: See [REVOCATION_EXAMPLES.md](./REVOCATION_EXAMPLES.md)
- Security Issues: Contact security team directly

## License | الترخيص

Copyright © 2024 SAHOOL Platform
All rights reserved.

---

**Version:** 1.0.0
**Last Updated:** 2024-12-27
**Maintainer:** SAHOOL Platform Team
