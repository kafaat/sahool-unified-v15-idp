# JWT Guards Quick Reference
# مرجع سريع لـ JWT Guards

## Python FastAPI

### Basic Usage

```python
from fastapi import Depends, FastAPI
from shared.auth import get_current_user, User

app = FastAPI()

@app.get("/profile")
async def profile(user: User = Depends(get_current_user)):
    """Protected endpoint with DB validation + caching"""
    return {"user_id": user.id, "email": user.email}
```

### With Rate Limiting

```python
from shared.auth import rate_limit_dependency

@app.post("/api/resource")
async def create(user: User = Depends(rate_limit_dependency)):
    """Protected + Rate limited (100 req/min)"""
    return {"status": "created"}
```

### Startup Configuration

```python
from shared.auth import init_user_cache, set_user_repository
from shared.auth import UserRepository, UserValidationData

@app.on_event("startup")
async def startup():
    # 1. Initialize cache
    await init_user_cache(ttl_seconds=300)

    # 2. Setup repository
    class MyRepo(UserRepository):
        async def get_user_validation_data(self, user_id):
            # Your DB query
            return UserValidationData(...)

    set_user_repository(MyRepo())
```

### Cache Management

```python
from shared.auth import get_user_cache

# Invalidate user
cache = get_user_cache()
await cache.invalidate_user(user_id)

# Clear all
await cache.clear_all()
```

---

## TypeScript NestJS

### Basic Usage

```typescript
import { Controller, Get, UseGuards } from '@nestjs/common';
import { JwtAuthGuard } from '@shared/auth/jwt.guard';
import { CurrentUser } from '@shared/auth/decorators';

@Controller('profile')
@UseGuards(JwtAuthGuard)
export class ProfileController {
  @Get()
  getProfile(@CurrentUser() user: any) {
    // Protected with DB validation + caching
    return { userId: user.id };
  }
}
```

### With Roles

```typescript
import { RolesGuard } from '@shared/auth/jwt.guard';
import { Roles } from '@shared/auth/decorators';

@UseGuards(JwtAuthGuard, RolesGuard)
@Roles('admin')
@Delete(':id')
delete(@Param('id') id: string) {
  // Admin only
}
```

### Module Setup

```typescript
import { UserValidationService } from '@shared/auth/user-validation.service';
import { IUserRepository } from '@shared/auth/user-validation.service';

@Module({
  providers: [
    JwtStrategy,
    UserValidationService,
    { provide: IUserRepository, useClass: MyUserRepository },
  ],
})
export class AuthModule {}
```

### Repository Implementation

```typescript
@Injectable()
class MyUserRepository implements IUserRepository {
  async getUserValidationData(userId: string) {
    // Your DB query
    return {
      userId,
      email: user.email,
      isActive: true,
      isVerified: true,
      roles: ['user'],
    };
  }

  async updateLastLogin(userId: string) {
    // Update DB
  }
}
```

---

## Environment Variables

```env
# Redis Cache (Optional)
REDIS_URL=redis://localhost:6379/0
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW_SECONDS=60

# JWT
JWT_SECRET_KEY=your-secret-key-min-32-chars
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

## Common Operations

### Check User Status

```python
# Python
if user.is_active and user.is_verified:
    # User is valid
    pass
```

```typescript
// TypeScript
if (userData.isActive && userData.isVerified) {
  // User is valid
}
```

### Invalidate Cache

```python
# Python - After user update
await cache.invalidate_user(user_id)
```

```typescript
// TypeScript - After user update
await this.validationService.invalidateUser(userId);
```

### Custom Rate Limit

```python
# Python
from shared.auth.dependencies import RateLimiter

custom_limiter = RateLimiter(requests=10, window_seconds=60)

@app.post("/sensitive")
async def sensitive(user: User = Depends(get_current_user)):
    if not custom_limiter.is_allowed(f"custom:{user.id}")[0]:
        raise HTTPException(429, "Too many requests")
```

---

## Logging Examples

### Python Logs

```log
# Success
INFO - User abc123 authenticated successfully (from cache)

# Failures
WARNING - Authentication failed: User abc123 is inactive
WARNING - Authentication failed: User abc123 not found
ERROR - Rate limit exceeded for user abc123
```

### TypeScript Logs

```log
# Success
[JwtAuthGuard] DEBUG - Authentication successful [GET /profile]: User abc123

# Failures
[JwtAuthGuard] WARN - Authentication failed [GET /api]: Token expired
[JwtStrategy] WARN - JWT validation failed for user abc123
```

---

## Error Handling

### Python

```python
from shared.auth.models import AuthException

try:
    user = await get_current_user(credentials)
except AuthException as e:
    # Handle auth error
    logger.error(f"Auth failed: {e.error.en}")
```

### TypeScript

```typescript
try {
  const user = await this.authService.validateUser(userId);
} catch (error) {
  if (error instanceof UnauthorizedException) {
    // Handle auth error
    this.logger.error(`Auth failed: ${error.message}`);
  }
}
```

---

## Testing

### Python Test

```python
@pytest.mark.asyncio
async def test_protected_endpoint():
    async with AsyncClient(app=app) as client:
        response = await client.get(
            "/profile",
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        assert response.status_code == 200
```

### TypeScript Test

```typescript
it('should authenticate user', async () => {
  const response = await request(app.getHttpServer())
    .get('/profile')
    .set('Authorization', `Bearer ${validToken}`)
    .expect(200);
});
```

---

## Performance

| Operation | Without Cache | With Cache | Improvement |
|-----------|--------------|------------|-------------|
| First Request | 60ms | 60ms | 0% |
| Repeated Request | 60ms | 5ms | 92% |

---

## Security Checklist

- ✅ Redis password set in production
- ✅ HTTPS enabled
- ✅ JWT secret is strong (32+ chars)
- ✅ Rate limiting enabled
- ✅ Logging monitoring configured
- ✅ Database user validation enabled
- ✅ Cache invalidation on user updates

---

## Troubleshooting

### Redis Connection Failed
```bash
# Check Redis
redis-cli ping  # Should return PONG

# Check .env
REDIS_URL=redis://localhost:6379/0
```

### User Not Found in DB
```python
# Verify repository implementation
user_data = await repository.get_user_validation_data(user_id)
assert user_data is not None
```

### Rate Limit Too Strict
```env
# Increase limits
RATE_LIMIT_REQUESTS=1000
RATE_LIMIT_WINDOW_SECONDS=60
```

---

## Best Practices

### ✅ Do
- Initialize cache on startup
- Implement user repository for DB
- Invalidate cache on user updates
- Monitor authentication logs
- Set appropriate rate limits
- Use HTTPS in production

### ❌ Don't
- Skip database validation
- Forget to invalidate cache
- Use weak JWT secrets
- Ignore rate limit violations
- Disable logging in production

---

## Quick Commands

```bash
# Install Python dependencies
pip install redis sqlalchemy

# Install TypeScript dependencies
npm install @liaoliaots/nestjs-redis ioredis

# Start Redis
redis-server

# Check Redis
redis-cli ping

# Clear Redis
redis-cli FLUSHDB
```

---

## Links

- 📖 Full Documentation: [JWT_GUARDS_ENHANCEMENT.md](./JWT_GUARDS_ENHANCEMENT.md)
- 💡 Examples: [INTEGRATION_EXAMPLES.md](./INTEGRATION_EXAMPLES.md)
- 📋 Summary: [SECURITY_ENHANCEMENTS_SUMMARY.md](./SECURITY_ENHANCEMENTS_SUMMARY.md)

---

**Version:** 1.0.0
**Updated:** 2024-12-27
**Status:** Production Ready ✅
