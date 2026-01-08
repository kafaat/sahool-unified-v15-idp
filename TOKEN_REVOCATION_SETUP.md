# Token Revocation Setup Guide

Quick setup guide for implementing token revocation on logout for SAHOOL platform.

## Prerequisites

1. Redis server running
2. Node.js and npm installed
3. PostgreSQL database configured

## Setup Steps

### 1. Install Dependencies

```bash
cd apps/services/user-service
npm install uuid @types/uuid
```

### 2. Configure Environment Variables

Create or update `.env` file in `apps/services/user-service/`:

```bash
# Copy example file
cp .env.example .env

# Edit the file with your settings
nano .env
```

**Minimum required configuration:**

```env
# Database
DATABASE_URL="postgresql://user:password@localhost:5432/sahool_users"

# JWT
JWT_SECRET_KEY="your-super-secret-jwt-key-at-least-32-characters-long"
JWT_ALGORITHM="HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES="30"
JWT_REFRESH_TOKEN_EXPIRE_DAYS="7"

# Redis
REDIS_URL="redis://localhost:6379"

# Token Revocation
TOKEN_REVOCATION_ENABLED="true"
```

### 3. Start Redis

**Using Docker:**
```bash
docker run --name sahool-redis -p 6379:6379 -d redis:alpine
```

**Using local Redis:**
```bash
redis-server
```

**Verify Redis is running:**
```bash
redis-cli ping
# Should return: PONG
```

### 4. Build and Start User Service

```bash
cd apps/services/user-service

# Install dependencies
npm install

# Run database migrations (if needed)
npx prisma migrate dev

# Start the service
npm run start:dev
```

### 5. Verify Implementation

**Test the API:**

```bash
# 1. Login
curl -X POST http://localhost:3020/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@sahool.com",
    "password": "TestPassword123!"
  }'

# Copy the access_token from response

# 2. Access protected endpoint
curl -X GET http://localhost:3020/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Should return user info

# 3. Logout (revoke token)
curl -X POST http://localhost:3020/api/v1/auth/logout \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Should return: {"success": true, "message": "Logged out successfully"}

# 4. Try using the same token again
curl -X GET http://localhost:3020/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Should return 401 Unauthorized with "token_revoked" error
```

**Check Redis:**

```bash
# Connect to Redis CLI
redis-cli

# List all revoked tokens
KEYS revoked:token:*

# Check a specific token (use one of the keys from above)
GET revoked:token:<jti>

# Output should show:
# {"revokedAt":1234567890,"reason":"user_logout","userId":"..."}

# Check TTL (Time To Live)
TTL revoked:token:<jti>

# Should show seconds until expiration
```

### 6. Configure Other Services (Optional)

To enable token revocation in other services (e.g., marketplace-service, iot-service):

**Update the service's `app.module.ts`:**

```typescript
import { Module } from '@nestjs/common';
import { APP_GUARD } from '@nestjs/core';
import { JwtModule } from '@nestjs/jwt';
import { TokenRevocationGuard } from '@sahool/nestjs-auth/guards/token-revocation.guard';
import { RedisTokenRevocationStore } from '@sahool/nestjs-auth/services/token-revocation';
import { JWTConfig } from '@sahool/nestjs-auth/config/jwt.config';

@Module({
  imports: [
    JwtModule.register({
      secret: JWTConfig.getVerificationKey(),
    }),
    // ... other modules
  ],
  providers: [
    // Global token revocation guard
    {
      provide: APP_GUARD,
      useClass: TokenRevocationGuard,
    },
    // Token revocation store
    {
      provide: RedisTokenRevocationStore,
      useFactory: () => {
        const redisUrl =
          process.env.REDIS_URL ||
          `redis://${process.env.REDIS_HOST || 'localhost'}:${process.env.REDIS_PORT || 6379}`;
        return new RedisTokenRevocationStore(redisUrl);
      },
    },
    // ... other providers
  ],
})
export class AppModule {}
```

**Add Redis config to service's `.env`:**

```env
REDIS_URL="redis://localhost:6379"
TOKEN_REVOCATION_ENABLED="true"
```

### 7. Update Frontend Environment

For admin and web apps, add backend URL:

**`apps/admin/.env.local`:**
```env
USER_SERVICE_URL="http://localhost:3020"
```

**`apps/web/.env.local`:**
```env
USER_SERVICE_URL="http://localhost:3020"
```

## Verification Checklist

- [ ] Redis is running and accessible
- [ ] User service starts without errors
- [ ] Login endpoint returns tokens with JTI
- [ ] Protected endpoints work with valid token
- [ ] Logout successfully revokes token
- [ ] Revoked token cannot access protected endpoints
- [ ] Token appears in Redis with correct TTL
- [ ] Health check endpoint returns healthy status
- [ ] Frontend logout calls backend revocation

## Troubleshooting

### Redis Connection Error

**Error:** `Failed to initialize Redis: connect ECONNREFUSED`

**Solution:**
1. Ensure Redis is running: `redis-cli ping`
2. Check Redis connection string in `.env`
3. Verify firewall allows connection to Redis port

### JWT Secret Not Configured

**Error:** `JWT_SECRET must be at least 32 characters in production`

**Solution:**
Generate a secure secret:
```bash
# Generate random secret
node -e "console.log(require('crypto').randomBytes(32).toString('base64'))"

# Add to .env
JWT_SECRET_KEY="<generated_secret>"
```

### Token Missing JTI

**Error:** `Token does not have JTI claim`

**Solution:**
Ensure you're using the new auth service for login. Old tokens won't have JTI.
1. Use POST `/api/v1/auth/login` endpoint
2. Verify token payload includes `jti` field

### Module Import Errors

**Error:** `Cannot find module '@sahool/nestjs-auth'`

**Solution:**
```bash
# Install the package
cd packages/nestjs-auth
npm install
npm run build

# Link it (if needed)
npm link

# In the service directory
npm link @sahool/nestjs-auth
```

## Production Deployment

### Redis Configuration

**High Availability Setup:**
```env
# Redis Sentinel or Cluster
REDIS_URL="redis://sentinel1:26379,sentinel2:26379,sentinel3:26379"

# With password
REDIS_URL="redis://:password@host:6379"

# Redis Cluster
REDIS_CLUSTER_NODES="host1:6379,host2:6379,host3:6379"
```

### Security Checklist

- [ ] Use strong JWT secret (minimum 32 characters)
- [ ] Enable Redis password authentication
- [ ] Use TLS for Redis connections in production
- [ ] Set appropriate token expiration times
- [ ] Monitor Redis memory usage
- [ ] Set up Redis persistence (AOF or RDB)
- [ ] Configure Redis maxmemory policy
- [ ] Enable rate limiting on auth endpoints
- [ ] Set up monitoring and alerts

### Performance Optimization

```env
# Increase token expiration to reduce revocation checks
JWT_ACCESS_TOKEN_EXPIRE_MINUTES="60"

# Use Redis connection pooling
REDIS_MAX_CONNECTIONS="50"
REDIS_MIN_CONNECTIONS="10"

# Enable Redis persistence
REDIS_SAVE="900 1 300 10 60 10000"
```

## Monitoring

### Health Checks

```bash
# Service health
curl http://localhost:3020/api/v1/health

# Token revocation health
curl http://localhost:3020/api/v1/auth/revocation/health

# Redis health
redis-cli ping
```

### Metrics to Monitor

1. **Redis Metrics:**
   - Memory usage
   - Key count (revoked tokens)
   - Hit/miss ratio
   - Connection count

2. **Application Metrics:**
   - Login success/failure rate
   - Logout success rate
   - Token revocation rate
   - Revoked token access attempts

3. **Performance Metrics:**
   - Token validation latency
   - Redis operation latency
   - Authentication endpoint response time

### Logging

Check logs for:
```bash
# Token revocations
grep "Token revoked" /var/log/user-service.log

# Revoked token access attempts
grep "Revoked token access attempt" /var/log/user-service.log

# Redis connection issues
grep "Redis error" /var/log/user-service.log
```

## Next Steps

1. Test the implementation thoroughly
2. Set up monitoring and alerts
3. Document API for frontend team
4. Deploy to staging environment
5. Perform load testing
6. Deploy to production
7. Monitor for issues

## Support

For issues or questions:
1. Check logs: `docker logs sahool-user-service`
2. Check Redis: `redis-cli` and use `KEYS *` to inspect
3. Review documentation: `TOKEN_REVOCATION_IMPLEMENTATION.md`
4. Contact platform team

## Summary

Your token revocation system is now set up! Users can:
- ✅ Login and receive tokens with unique JTI
- ✅ Access protected resources with valid tokens
- ✅ Logout and immediately revoke tokens
- ✅ Be blocked from using revoked tokens
- ✅ Logout from all devices

The system automatically manages token lifecycle with Redis TTL.
