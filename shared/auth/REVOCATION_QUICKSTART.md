# Token Revocation Quick Start Guide

# دليل البدء السريع لإلغاء الرموز

Get started with token revocation in 5 minutes!

## Quick Setup

### 1. Prerequisites

```bash
# Start Redis
docker run -d --name redis -p 6379:6379 redis:7-alpine

# Install dependencies
pip install redis[asyncio]  # Python
npm install redis           # TypeScript
```

### 2. Environment Variables

Create `.env` file:

```bash
# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Token Revocation
TOKEN_REVOCATION_ENABLED=true

# JWT
JWT_SECRET=your-secret-key-at-least-32-chars
JWT_ALGORITHM=HS256
```

### 3. Python Setup (FastAPI)

```python
# main.py
from fastapi import FastAPI
from shared.auth import (
    JWTAuthMiddleware,
    TokenRevocationMiddleware,
)
from shared.auth.revocation_api import router as revocation_router

app = FastAPI()

# Add middleware (order matters!)
app.add_middleware(JWTAuthMiddleware)
app.add_middleware(TokenRevocationMiddleware)

# Include revocation endpoints
app.include_router(revocation_router)

# Your routes...
@app.get("/protected")
async def protected():
    return {"message": "Protected route"}
```

### 4. TypeScript Setup (NestJS)

```typescript
// app.module.ts
import { Module } from "@nestjs/common";
import { APP_GUARD } from "@nestjs/core";
import { JwtModule } from "@nestjs/jwt";
import { TokenRevocationModule } from "@shared/auth/token-revocation";
import { TokenRevocationGuard } from "@shared/auth/token-revocation.guard";

@Module({
  imports: [
    JwtModule.register({
      secret: process.env.JWT_SECRET,
    }),
    TokenRevocationModule,
  ],
  providers: [
    {
      provide: APP_GUARD,
      useClass: TokenRevocationGuard,
    },
  ],
})
export class AppModule {}
```

## Quick Examples

### Logout (Python)

```python
from fastapi import APIRouter, Request, Depends
from shared.auth import get_current_user, revoke_token, verify_token

router = APIRouter()

@router.post("/logout")
async def logout(request: Request, user = Depends(get_current_user)):
    # Get token
    token = request.headers["Authorization"].split(" ")[1]
    payload = verify_token(token)

    # Revoke it
    await revoke_token(jti=payload.jti, reason="user_logout")

    return {"message": "Logged out"}
```

### Logout (TypeScript)

```typescript
import { Controller, Post, Request, UseGuards } from "@nestjs/common";
import { JwtAuthGuard } from "@shared/auth/jwt.guard";
import { RedisTokenRevocationStore } from "@shared/auth/token-revocation";

@Controller("auth")
export class AuthController {
  constructor(private readonly revocationStore: RedisTokenRevocationStore) {}

  @Post("logout")
  @UseGuards(JwtAuthGuard)
  async logout(@Request() req) {
    const token = req.headers.authorization.split(" ")[1];
    const payload = this.jwtService.decode(token);

    await this.revocationStore.revokeToken(payload.jti, {
      reason: "user_logout",
    });

    return { message: "Logged out" };
  }
}
```

### Logout from All Devices (Python)

```python
from shared.auth import revoke_all_user_tokens

@router.post("/logout-all")
async def logout_all(user = Depends(get_current_user)):
    await revoke_all_user_tokens(user_id=user.id, reason="logout_all")
    return {"message": "Logged out from all devices"}
```

### Logout from All Devices (TypeScript)

```typescript
@Post('logout-all')
@UseGuards(JwtAuthGuard)
async logoutAll(@Request() req) {
  await this.revocationStore.revokeAllUserTokens(
    req.user.id,
    'logout_all',
  );

  return { message: 'Logged out from all devices' };
}
```

## Testing

### Test Redis Connection

```bash
# Python
python -c "
import asyncio
from shared.auth.token_revocation import get_revocation_store

async def test():
    store = await get_revocation_store()
    healthy = await store.health_check()
    print(f'Redis: {'✅' if healthy else '❌'}')

asyncio.run(test())
"
```

```bash
# TypeScript
node -e "
const { RedisTokenRevocationStore } = require('./shared/auth/token-revocation');

(async () => {
  const store = new RedisTokenRevocationStore();
  await store.initialize();
  const healthy = await store.healthCheck();
  console.log(\`Redis: \${healthy ? '✅' : '❌'}\`);
  await store.close();
})();
"
```

### Test Token Revocation

```bash
# 1. Login and get token
curl -X POST http://localhost:3000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}'

# 2. Access protected route (should work)
curl -X GET http://localhost:3000/protected \
  -H "Authorization: Bearer YOUR_TOKEN"

# 3. Logout (revoke token)
curl -X POST http://localhost:3000/auth/revocation/revoke-current \
  -H "Authorization: Bearer YOUR_TOKEN"

# 4. Try to access protected route again (should fail with 401)
curl -X GET http://localhost:3000/protected \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Common Use Cases

### 1. User Logout

```python
# Python
await revoke_token(jti=payload.jti, reason="user_logout")
```

```typescript
// TypeScript
await this.revocationStore.revokeToken(payload.jti, { reason: "user_logout" });
```

### 2. Password Change

```python
# Python
await revoke_all_user_tokens(user_id=user.id, reason="password_change")
```

```typescript
// TypeScript
await this.revocationStore.revokeAllUserTokens(user.id, "password_change");
```

### 3. Account Security Reset

```python
# Python
await revoke_all_user_tokens(user_id=user.id, reason="security_reset")
```

```typescript
// TypeScript
await this.revocationStore.revokeAllUserTokens(user.id, "security_reset");
```

## API Quick Reference

| Endpoint                              | Method | Description                    |
| ------------------------------------- | ------ | ------------------------------ |
| `/auth/revocation/revoke-current`     | POST   | Logout (revoke current token)  |
| `/auth/revocation/revoke-all`         | POST   | Logout from all devices        |
| `/auth/revocation/revoke`             | POST   | Revoke specific token (admin)  |
| `/auth/revocation/revoke-user-tokens` | POST   | Revoke all user tokens (admin) |
| `/auth/revocation/status/:jti`        | GET    | Check token status             |
| `/auth/revocation/stats`              | GET    | Get statistics (admin)         |
| `/auth/revocation/health`             | GET    | Health check                   |

## Troubleshooting

### Redis Connection Failed

```bash
# Check if Redis is running
docker ps | grep redis

# Test Redis
redis-cli ping
# Should respond: PONG

# Check Redis logs
docker logs redis
```

### Tokens Not Being Revoked

1. Check environment variable: `TOKEN_REVOCATION_ENABLED=true`
2. Verify Redis connection: `curl http://localhost:3000/auth/revocation/health`
3. Check middleware order: Revocation middleware should be after JWT middleware
4. Ensure tokens have `jti` claim

### Performance Issues

```bash
# Check Redis memory
redis-cli info memory

# Check number of keys
redis-cli DBSIZE

# Monitor Redis operations
redis-cli monitor
```

## Next Steps

- Read full documentation: [TOKEN_REVOCATION_README.md](./TOKEN_REVOCATION_README.md)
- See more examples: [REVOCATION_EXAMPLES.md](./REVOCATION_EXAMPLES.md)
- Configure monitoring and alerts
- Set up Redis cluster for production
- Implement audit logging

## Support

- Issues: Create a GitHub issue
- Questions: Check documentation
- Security: Contact security team

---

**Ready to go! 🚀**

For more details, see:

- [Full Documentation](./TOKEN_REVOCATION_README.md)
- [Detailed Examples](./REVOCATION_EXAMPLES.md)
- [API Reference](./revocation_api.py)
