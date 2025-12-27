# Token Revocation Examples
# أمثلة على إلغاء الرموز

This document provides practical examples of using the token revocation system.

## Table of Contents
1. [Python Examples](#python-examples)
2. [TypeScript/NestJS Examples](#typescriptnestjs-examples)
3. [API Usage Examples](#api-usage-examples)
4. [Common Scenarios](#common-scenarios)

---

## Python Examples

### 1. Setup in FastAPI Application

```python
from fastapi import FastAPI
from shared.auth.middleware import JWTAuthMiddleware
from shared.auth.revocation_middleware import TokenRevocationMiddleware
from shared.auth.revocation_api import router as revocation_router

app = FastAPI(title="SAHOOL API")

# Add authentication middleware
app.add_middleware(JWTAuthMiddleware, require_auth=False)

# Add token revocation middleware
app.add_middleware(TokenRevocationMiddleware, fail_open=True)

# Include revocation API endpoints
app.include_router(revocation_router)
```

### 2. Revoke Token on Logout

```python
from fastapi import APIRouter, Depends
from shared.auth.dependencies import get_current_user
from shared.auth.token_revocation import revoke_token
from shared.auth.jwt_handler import verify_token

router = APIRouter()

@router.post("/auth/logout")
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    # Extract token
    token = request.headers.get("Authorization").split(" ")[1]
    payload = verify_token(token)

    # Revoke the token
    await revoke_token(
        jti=payload.jti,
        expires_in=3600,  # 1 hour
        reason="user_logout",
        user_id=current_user.id
    )

    return {"message": "Successfully logged out"}
```

### 3. Revoke All User Tokens (Password Change)

```python
from shared.auth.token_revocation import revoke_all_user_tokens

@router.post("/auth/change-password")
async def change_password(
    old_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user),
):
    # Verify old password
    if not verify_password(old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid password")

    # Update password in database
    await update_user_password(current_user.id, new_password)

    # Revoke all existing tokens
    await revoke_all_user_tokens(
        user_id=current_user.id,
        reason="password_change"
    )

    return {"message": "Password changed. Please login again."}
```

### 4. Manual Token Revocation Check

```python
from shared.auth.token_revocation import get_revocation_store

async def check_token_manually(jti: str, user_id: str, issued_at: float):
    store = await get_revocation_store()

    is_revoked, reason = await store.is_revoked(
        jti=jti,
        user_id=user_id,
        issued_at=issued_at
    )

    if is_revoked:
        print(f"Token is revoked: {reason}")
        return False

    return True
```

### 5. Using Revocation Dependency

```python
from fastapi import Depends
from shared.auth.revocation_middleware import RevocationCheckDependency

revocation_check = RevocationCheckDependency(fail_open=True)

@router.get("/protected", dependencies=[Depends(revocation_check)])
async def protected_route(current_user: User = Depends(get_current_user)):
    return {"user_id": current_user.id}
```

---

## TypeScript/NestJS Examples

### 1. Setup in NestJS Application

```typescript
// app.module.ts
import { Module } from '@nestjs/common';
import { APP_GUARD } from '@nestjs/core';
import { JwtModule } from '@nestjs/jwt';
import { TokenRevocationModule } from '@shared/auth/token-revocation';
import { TokenRevocationGuard } from '@shared/auth/token-revocation.guard';
import { RevocationController } from '@shared/auth/revocation.controller';
import { JWTConfig } from '@shared/auth/config';

@Module({
  imports: [
    // JWT Module
    JwtModule.register({
      secret: JWTConfig.SECRET,
      signOptions: JWTConfig.getJwtOptions().signOptions,
    }),

    // Token Revocation Module
    TokenRevocationModule,
  ],
  controllers: [RevocationController],
  providers: [
    // Global guard for token revocation
    {
      provide: APP_GUARD,
      useClass: TokenRevocationGuard,
    },
  ],
})
export class AppModule {}
```

### 2. Revoke Token on Logout

```typescript
// auth.controller.ts
import { Controller, Post, Request, UseGuards } from '@nestjs/common';
import { JwtAuthGuard } from '@shared/auth/jwt.guard';
import { RedisTokenRevocationStore } from '@shared/auth/token-revocation';
import { JwtService } from '@nestjs/jwt';

@Controller('auth')
export class AuthController {
  constructor(
    private readonly revocationStore: RedisTokenRevocationStore,
    private readonly jwtService: JwtService,
  ) {}

  @Post('logout')
  @UseGuards(JwtAuthGuard)
  async logout(@Request() req) {
    // Extract token
    const token = req.headers.authorization.split(' ')[1];
    const payload = this.jwtService.decode(token);

    // Revoke the token
    await this.revocationStore.revokeToken(payload.jti, {
      expiresIn: 3600, // 1 hour
      reason: 'user_logout',
      userId: req.user.id,
    });

    return { message: 'Successfully logged out' };
  }
}
```

### 3. Revoke All User Tokens (Password Change)

```typescript
@Post('change-password')
@UseGuards(JwtAuthGuard)
async changePassword(
  @Body() dto: ChangePasswordDto,
  @Request() req,
) {
  const user = req.user;

  // Verify old password
  const isValid = await this.authService.verifyPassword(
    dto.oldPassword,
    user.hashedPassword,
  );

  if (!isValid) {
    throw new UnauthorizedException('Invalid password');
  }

  // Update password
  await this.authService.updatePassword(user.id, dto.newPassword);

  // Revoke all existing tokens
  await this.revocationStore.revokeAllUserTokens(
    user.id,
    'password_change',
  );

  return { message: 'Password changed. Please login again.' };
}
```

### 4. Skip Revocation Check for Specific Route

```typescript
import { Controller, Get } from '@nestjs/common';
import { SkipRevocationCheck } from '@shared/auth/token-revocation.guard';

@Controller('public')
export class PublicController {
  @Get('data')
  @SkipRevocationCheck()
  async getPublicData() {
    return { data: 'This route skips revocation check' };
  }
}
```

### 5. Manual Token Revocation Check

```typescript
async function checkTokenManually(
  jti: string,
  userId: string,
  issuedAt: number,
): Promise<boolean> {
  const store = new RedisTokenRevocationStore();
  await store.initialize();

  const result = await store.isRevoked({
    jti,
    userId,
    issuedAt,
  });

  if (result.isRevoked) {
    console.log(`Token is revoked: ${result.reason}`);
    return false;
  }

  return true;
}
```

### 6. Using Interceptor Instead of Guard

```typescript
// app.module.ts
import { APP_INTERCEPTOR } from '@nestjs/core';
import { TokenRevocationInterceptor } from '@shared/auth/token-revocation.guard';

@Module({
  providers: [
    {
      provide: APP_INTERCEPTOR,
      useClass: TokenRevocationInterceptor,
    },
  ],
})
export class AppModule {}
```

---

## API Usage Examples

### 1. Logout (Revoke Current Token)

```bash
# Logout current user
curl -X POST http://localhost:3000/auth/revocation/revoke-current \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

Response:
```json
{
  "success": true,
  "message": "Successfully logged out",
  "revokedCount": 1
}
```

### 2. Logout from All Devices

```bash
# Revoke all tokens for current user
curl -X POST http://localhost:3000/auth/revocation/revoke-all \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

Response:
```json
{
  "success": true,
  "message": "All your tokens have been revoked. Logged out from all devices."
}
```

### 3. Revoke Specific Token (Admin)

```bash
# Revoke a specific token by JTI
curl -X POST http://localhost:3000/auth/revocation/revoke \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "jti": "550e8400-e29b-41d4-a716-446655440000",
    "reason": "suspicious_activity"
  }'
```

### 4. Revoke All User Tokens (Admin)

```bash
# Revoke all tokens for a specific user
curl -X POST http://localhost:3000/auth/revocation/revoke-user-tokens \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "user-123",
    "reason": "account_compromised"
  }'
```

### 5. Check Token Status

```bash
# Check if a token is revoked
curl -X GET http://localhost:3000/auth/revocation/status/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

Response:
```json
{
  "isRevoked": true,
  "reason": "user_logout",
  "revokedAt": 1640000000.0
}
```

### 6. Get Revocation Statistics (Admin)

```bash
# Get statistics
curl -X GET http://localhost:3000/auth/revocation/stats \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

Response:
```json
{
  "initialized": true,
  "revokedTokens": 42,
  "revokedUsers": 10,
  "revokedTenants": 2,
  "redisUrl": "localhost:6379/0"
}
```

### 7. Health Check

```bash
# Check service health
curl -X GET http://localhost:3000/auth/revocation/health
```

Response:
```json
{
  "status": "healthy",
  "service": "token_revocation",
  "redis": "connected"
}
```

---

## Common Scenarios

### Scenario 1: User Logout
User clicks logout button → Revoke current token → User redirected to login

```python
# Python
await revoke_token(jti=payload.jti, reason="user_logout")
```

```typescript
// TypeScript
await this.revocationStore.revokeToken(payload.jti, { reason: 'user_logout' });
```

### Scenario 2: Password Change
User changes password → Revoke all user tokens → User must login again

```python
# Python
await revoke_all_user_tokens(user_id=user.id, reason="password_change")
```

```typescript
// TypeScript
await this.revocationStore.revokeAllUserTokens(user.id, 'password_change');
```

### Scenario 3: Suspicious Activity
Admin detects suspicious activity → Revoke all user tokens → Investigate

```python
# Python
await revoke_all_user_tokens(user_id=suspicious_user_id, reason="suspicious_activity")
```

```typescript
// TypeScript
await this.revocationStore.revokeAllUserTokens(suspiciousUserId, 'suspicious_activity');
```

### Scenario 4: Account Deactivation
Admin deactivates account → Revoke all user tokens → User cannot access

```python
# Python
await revoke_all_user_tokens(user_id=user_id, reason="account_deactivated")
```

```typescript
// TypeScript
await this.revocationStore.revokeAllUserTokens(userId, 'account_deactivated');
```

### Scenario 5: Security Breach
Security breach detected → Revoke all tenant tokens → All users must re-login

```python
# Python (Admin only)
from shared.auth.token_revocation import get_revocation_store
store = await get_revocation_store()
await store.revoke_all_tenant_tokens(tenant_id=tenant_id, reason="security_breach")
```

```typescript
// TypeScript (Admin only)
await this.revocationStore.revokeAllTenantTokens(tenantId, 'security_breach');
```

---

## Environment Variables

Make sure to set these environment variables:

```bash
# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=your_redis_password  # Optional

# Or use Redis URL
REDIS_URL=redis://:password@localhost:6379/0

# Token Revocation
TOKEN_REVOCATION_ENABLED=true

# JWT Configuration
JWT_SECRET=your_secret_key_here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
```

---

## Testing

### Test Redis Connection

```python
# Python
from shared.auth.token_revocation import get_revocation_store

async def test_redis():
    store = await get_revocation_store()
    is_healthy = await store.health_check()
    print(f"Redis is {'healthy' if is_healthy else 'unhealthy'}")
```

```typescript
// TypeScript
const store = new RedisTokenRevocationStore();
await store.initialize();
const isHealthy = await store.healthCheck();
console.log(`Redis is ${isHealthy ? 'healthy' : 'unhealthy'}`);
```

### Test Token Revocation

```python
# Python
import time

async def test_token_revocation():
    store = await get_revocation_store()

    # Revoke a token
    jti = "test-token-123"
    await store.revoke_token(jti, expires_in=60, reason="test")

    # Check if revoked
    is_revoked = await store.is_token_revoked(jti)
    print(f"Token revoked: {is_revoked}")  # True

    # Wait for expiry (in production, this would be automatic)
    # time.sleep(61)

    # Check again (should be False after TTL expires)
    # is_revoked = await store.is_token_revoked(jti)
    # print(f"Token revoked after TTL: {is_revoked}")  # False
```

---

## Best Practices

1. **Always set appropriate TTL**: Set `expires_in` to match token expiration time
2. **Use specific reasons**: Provide clear reasons for revocation for audit trails
3. **Fail open on Redis errors**: Don't block users if Redis is temporarily unavailable
4. **Monitor revocation stats**: Regularly check statistics to detect anomalies
5. **Clean up old revocations**: Redis TTL automatically handles this
6. **Use user-level revocation**: For password changes and security events
7. **Use tenant-level revocation**: Only for critical security incidents
8. **Test thoroughly**: Test revocation in development before production

---

## Troubleshooting

### Issue: Redis Connection Failed

```bash
# Check Redis is running
redis-cli ping

# Check Redis logs
docker logs redis-container
```

### Issue: Tokens Not Being Revoked

```python
# Check if revocation is enabled
from shared.auth.config import config
print(f"Revocation enabled: {config.TOKEN_REVOCATION_ENABLED}")

# Check Redis health
store = await get_revocation_store()
is_healthy = await store.health_check()
print(f"Redis healthy: {is_healthy}")
```

### Issue: Performance Issues

```bash
# Check Redis memory usage
redis-cli info memory

# Check number of revoked tokens
redis-cli DBSIZE

# Clear old revocations (if needed)
redis-cli KEYS "revoked:*" | xargs redis-cli DEL
```

---

## Security Considerations

1. **Rate Limiting**: Implement rate limiting on revocation endpoints
2. **Authorization**: Ensure only authorized users can revoke tokens
3. **Audit Logging**: Log all revocation actions for security audits
4. **Encrypted Communication**: Use TLS for Redis connections in production
5. **Password Protection**: Always use Redis password in production
6. **Network Security**: Restrict Redis access to application servers only

---

## Performance Optimization

1. **Use Redis Cluster**: For high-traffic applications
2. **Connection Pooling**: Reuse Redis connections
3. **Batch Operations**: Batch multiple revocations when possible
4. **Monitor Latency**: Track Redis response times
5. **Set Appropriate TTL**: Avoid storing revocations longer than needed
6. **Use Pipeline**: For multiple Redis operations

---

For more information, see:
- [Token Revocation README](./README.md)
- [JWT Handler Documentation](./jwt_handler.py)
- [Redis Documentation](https://redis.io/documentation)
