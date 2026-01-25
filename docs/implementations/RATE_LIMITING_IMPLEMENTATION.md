# SAHOOL Platform - Rate Limiting Implementation

## Overview

This document describes the comprehensive rate limiting implementation across the SAHOOL platform to prevent brute-force attacks, API abuse, and ensure fair resource usage.

## Security Objectives

- **Prevent Brute Force Attacks**: Limit authentication attempts to prevent password guessing
- **Prevent Credential Stuffing**: Rate limit login endpoints to prevent automated credential testing
- **Prevent Account Enumeration**: Limit password reset requests to prevent email discovery
- **Prevent API Abuse**: Ensure fair usage of API resources
- **Protect Infrastructure**: Prevent DDoS attacks and resource exhaustion

## Implementation Layers

The rate limiting is implemented at three layers:

### 1. Kong Gateway Layer (Entry Point)

### 2. Application Layer (NestJS Services)

### 3. Application Layer (FastAPI Services)

---

## 1. Kong Gateway Rate Limiting

Kong Gateway provides the first line of defense with Redis-backed distributed rate limiting.

### Configuration Location

```
/home/user/sahool-unified-v15-idp/infrastructure/gateway/kong/kong.yml
```

### Authentication Endpoints

#### Login Endpoint

- **Path**: `/api/v1/auth/login`
- **Rate Limit**: 5 requests/minute, 20 requests/hour
- **Policy**: Redis-backed
- **Headers**: `X-RateLimit-Limit: 5`

```yaml
- name: auth-login-route
  paths:
    - /api/v1/auth/login
  plugins:
    - name: rate-limiting
      config:
        minute: 5
        hour: 20
        policy: redis
```

#### Password Reset Endpoint

- **Path**: `/api/v1/auth/password-reset`, `/api/v1/auth/forgot-password`
- **Rate Limit**: 3 requests/minute, 10 requests/hour
- **Policy**: Redis-backed
- **Headers**: `X-RateLimit-Limit: 3`

```yaml
- name: auth-password-reset-route
  paths:
    - /api/v1/auth/password-reset
    - /api/v1/auth/forgot-password
  plugins:
    - name: rate-limiting
      config:
        minute: 3
        hour: 10
```

#### Registration Endpoint

- **Path**: `/api/v1/auth/register`, `/api/v1/auth/signup`
- **Rate Limit**: 10 requests/minute, 50 requests/hour
- **Policy**: Redis-backed
- **Headers**: `X-RateLimit-Limit: 10`

```yaml
- name: auth-register-route
  paths:
    - /api/v1/auth/register
    - /api/v1/auth/signup
  plugins:
    - name: rate-limiting
      config:
        minute: 10
        hour: 50
```

#### Token Refresh Endpoint

- **Path**: `/api/v1/auth/refresh`
- **Rate Limit**: 10 requests/minute, 100 requests/hour
- **Policy**: Redis-backed

### General API Endpoints

#### Standard Tier (Starter Users)

- **Rate Limit**: 100 requests/minute, 5000 requests/hour
- **Services**: Field management, Weather, Calendar, Notifications

#### Professional Tier

- **Rate Limit**: 1000 requests/minute, 50000 requests/hour
- **Services**: Satellite, NDVI, Crop Health AI, Irrigation, Yield Engine

#### Enterprise Tier

- **Rate Limit**: 10000 requests/minute, 500000 requests/hour
- **Services**: AI Advisor, IoT Gateway, Research, Marketplace

#### Admin Endpoints

- **Path**: `/api/v1/admin/*`
- **Rate Limit**: 50 requests/minute, 2000 requests/hour
- **Additional Security**: IP restriction to private networks

---

## 2. NestJS Services Rate Limiting

All NestJS services use `@nestjs/throttler` for application-level rate limiting.

### Installation

The throttler is already installed in all NestJS services:

```json
{
  "dependencies": {
    "@nestjs/throttler": "^6.2.1"
  }
}
```

### Global Configuration

Each NestJS service has throttler configured in `app.module.ts`:

```typescript
import { ThrottlerModule, ThrottlerGuard } from "@nestjs/throttler";
import { APP_GUARD } from "@nestjs/core";

@Module({
  imports: [
    ThrottlerModule.forRoot([
      {
        name: "short",
        ttl: 1000, // 1 second
        limit: 10, // 10 requests per second
      },
      {
        name: "medium",
        ttl: 60000, // 1 minute
        limit: 100, // 100 requests per minute
      },
      {
        name: "long",
        ttl: 3600000, // 1 hour
        limit: 1000, // 1000 requests per hour
      },
    ]),
  ],
  providers: [
    {
      provide: APP_GUARD,
      useClass: ThrottlerGuard,
    },
  ],
})
export class AppModule {}
```

### Per-Endpoint Configuration

Use the `@Throttle()` decorator for specific rate limits:

```typescript
import { Throttle } from "@nestjs/throttler";

@Controller("auth")
export class AuthController {
  // Login - 5 requests per minute
  @Post("login")
  @Throttle({ default: { limit: 5, ttl: 60000 } })
  async login(@Body() loginDto: LoginDto) {
    // ...
  }

  // Registration - 10 requests per minute
  @Post("register")
  @Throttle({ default: { limit: 10, ttl: 60000 } })
  async register(@Body() registerDto: RegisterDto) {
    // ...
  }

  // Password reset - 3 requests per minute
  @Post("forgot-password")
  @Throttle({ default: { limit: 3, ttl: 60000 } })
  async forgotPassword(@Body() dto: ForgotPasswordDto) {
    // ...
  }

  // Skip rate limiting for specific endpoints
  @Post("logout")
  @SkipThrottle()
  async logout() {
    // ...
  }
}
```

### Example Implementation

See: `/home/user/sahool-unified-v15-idp/apps/services/shared/auth/auth.controller.example.ts`

### Services with Throttler

- ✅ `marketplace-service` (Port 3010)
- ✅ `iot-service` (Port 8117)
- ✅ `chat-service` (Port 8114)
- ✅ `research-core` (Port 3015)
- ✅ `disaster-assessment` (Port 3020)

---

## 3. FastAPI Services Rate Limiting

FastAPI services use the custom `RateLimiter` middleware with Redis backend.

### Middleware Location

```
/home/user/sahool-unified-v15-idp/apps/services/shared/middleware/rate_limiter.py
```

### Global Rate Limiting Setup

Add to your FastAPI application:

```python
from fastapi import FastAPI
from apps.services.shared.middleware import setup_rate_limiting

app = FastAPI()

# Setup rate limiting middleware
limiter = setup_rate_limiting(
    app,
    use_redis=True,
    redis_url="redis://:password@redis:6379/0",
)
```

### Authentication-Specific Rate Limiting

Use the specialized `AuthRateLimiter` for authentication endpoints:

#### Configuration Location

```
/home/user/sahool-unified-v15-idp/apps/services/shared/auth/rate_limiting.py
```

#### Rate Limit Configurations

```python
from apps.services.shared.auth.rate_limiting import AUTH_RATE_CONFIGS

# Login: 5 req/min, 20 req/hour
AUTH_RATE_CONFIGS.LOGIN

# Password Reset: 3 req/min, 10 req/hour
AUTH_RATE_CONFIGS.PASSWORD_RESET

# Registration: 10 req/min, 50 req/hour
AUTH_RATE_CONFIGS.REGISTRATION

# Token Refresh: 10 req/min, 100 req/hour
AUTH_RATE_CONFIGS.TOKEN_REFRESH
```

#### Usage in Endpoints

```python
from fastapi import APIRouter, Depends, Request, Response
from apps.services.shared.auth.rate_limiting import get_auth_rate_limiter, AuthRateLimiter
from apps.services.shared.middleware.rate_limiter import get_rate_limit_headers

router = APIRouter()

@router.post("/login")
async def login(
    request: Request,
    response: Response,
    credentials: LoginRequest,
    limiter: AuthRateLimiter = Depends(get_auth_rate_limiter),
):
    # Check rate limit (raises HTTPException if exceeded)
    allowed, remaining, limit, reset = await limiter.check_login_limit(
        request, credentials.email
    )

    # Add rate limit headers
    for header, value in get_rate_limit_headers(remaining, limit, reset).items():
        response.headers[header] = value

    # Your authentication logic here
    ...
```

### Example Implementation

See: `/home/user/sahool-unified-v15-idp/apps/services/shared/auth/auth_endpoints_example.py`

### Features

- **Redis-backed**: Distributed rate limiting across multiple instances
- **Automatic Headers**: Adds `X-RateLimit-*` headers to responses
- **Fallback**: In-memory rate limiting if Redis is unavailable
- **Configurable Tiers**: Free, Standard, Premium, Internal, Unlimited
- **Path Exclusions**: Health checks and metrics excluded by default

---

## Rate Limit Headers

All rate-limited endpoints return the following headers:

### Header Definitions

| Header                  | Description                                        | Example |
| ----------------------- | -------------------------------------------------- | ------- |
| `X-RateLimit-Limit`     | Maximum requests allowed in the current window     | `5`     |
| `X-RateLimit-Remaining` | Number of requests remaining in the current window | `3`     |
| `X-RateLimit-Reset`     | Seconds until the rate limit window resets         | `45`    |

### Example Response

```http
HTTP/1.1 200 OK
X-RateLimit-Limit: 5
X-RateLimit-Remaining: 3
X-RateLimit-Reset: 45
Content-Type: application/json

{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

### Rate Limit Exceeded Response

```http
HTTP/1.1 429 Too Many Requests
X-RateLimit-Limit: 5
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 45
Retry-After: 45
Content-Type: application/json

{
  "error": "rate_limit_exceeded",
  "message": "Too many login attempts. Please try again later.",
  "retry_after": 45
}
```

---

## Rate Limiting Strategy Summary

### Authentication Endpoints

| Endpoint       | Rate Limit  | Window   | Policy        |
| -------------- | ----------- | -------- | ------------- |
| Login          | 5 requests  | 1 minute | IP + Username |
| Password Reset | 3 requests  | 1 minute | IP + Email    |
| Registration   | 10 requests | 1 minute | IP + Email    |
| Token Refresh  | 10 requests | 1 minute | IP + User ID  |
| Logout         | Unlimited   | -        | No limit      |

### API Endpoints by Tier

| Tier         | Rate Limit             | Services           |
| ------------ | ---------------------- | ------------------ |
| Starter      | 100/min, 5000/hour     | Basic services     |
| Professional | 1000/min, 50000/hour   | Advanced analytics |
| Enterprise   | 10000/min, 500000/hour | AI, IoT, Research  |
| Admin        | 50/min, 2000/hour      | Admin dashboard    |

---

## Security Best Practices

### 1. Use IP + Identifier for Rate Limiting

- Login: Use IP + username/email combination
- Password Reset: Use IP + email
- Registration: Use IP + email
- This prevents attackers from bypassing limits by trying different accounts

### 2. Return Generic Error Messages

- Don't reveal whether an account exists
- Always return success for password reset, even if email doesn't exist
- Prevents account enumeration attacks

### 3. Log Failed Attempts

- Log all failed authentication attempts
- Include IP address, timestamp, and attempted credential
- Monitor for patterns indicating attacks

### 4. Implement Account Lockout

- Lock account after N failed login attempts (e.g., 10)
- Require manual unlock or time-based unlock
- Send notification to user about lockout

### 5. Use Redis for Distributed Systems

- Ensure rate limits work across multiple service instances
- Configure Redis password and secure connection
- Use separate Redis database for rate limiting (database 1)

### 6. Monitor Rate Limit Violations

- Set up alerts for repeated rate limit violations
- Track patterns of abuse
- Implement IP blocking for persistent violators

---

## Testing Rate Limiting

### Testing Kong Gateway Limits

```bash
# Test login rate limit (should fail after 5 requests)
for i in {1..10}; do
  curl -X POST http://localhost:8000/api/v1/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"test@example.com","password":"password123"}' \
    -v
  sleep 1
done
```

### Testing NestJS Service Limits

```bash
# Test with direct service connection (bypass Kong)
for i in {1..10}; do
  curl -X POST http://localhost:3010/api/v1/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"test@example.com","password":"password123"}' \
    -v
  sleep 1
done
```

### Verify Headers

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}' \
  -i | grep "X-RateLimit"
```

Expected output:

```
X-RateLimit-Limit: 5
X-RateLimit-Remaining: 4
X-RateLimit-Reset: 60
```

---

## Deployment Considerations

### Environment Variables

Ensure these environment variables are set:

```bash
# Redis connection for rate limiting
REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
REDIS_PASSWORD=<secure-password>

# Rate limit configurations (optional - has defaults)
RATE_LIMIT_FREE_RPM=30
RATE_LIMIT_STANDARD_RPM=60
RATE_LIMIT_PREMIUM_RPM=120
RATE_LIMIT_INTERNAL_RPM=1000
```

### Docker Compose Configuration

The Redis service is already configured in `docker-compose.yml`:

```yaml
redis:
  image: redis:7-alpine
  command:
    [
      "redis-server",
      "--requirepass",
      "${REDIS_PASSWORD}",
      "--maxmemory",
      "512mb",
      "--maxmemory-policy",
      "allkeys-lru",
    ]
  ports:
    - "127.0.0.1:6379:6379"
```

### Kong Configuration

Kong uses Redis for distributed rate limiting:

```yaml
environment:
  KONG_PLUGINS: "bundled,prometheus"
  REDIS_PASSWORD: ${REDIS_PASSWORD}
```

---

## Monitoring and Alerts

### Metrics to Monitor

1. **Rate Limit Violations**: Track 429 responses
2. **Authentication Failures**: Track 401 responses
3. **Suspicious Patterns**: Multiple IPs trying same username
4. **Account Lockouts**: Track locked accounts

### Prometheus Metrics

Kong exposes Prometheus metrics at `/metrics`:

```
kong_http_status{code="429"} - Rate limit exceeded count
kong_bandwidth - Request/response sizes
kong_latency - Request processing time
```

### Log Monitoring

Monitor logs for:

- `Rate limit exceeded` messages
- `Failed login attempt` messages
- Repeated attempts from same IP
- Attempts on non-existent accounts

---

## Troubleshooting

### Issue: Rate limits not working

**Check:**

1. Redis connection: `redis-cli -a $REDIS_PASSWORD ping`
2. Kong configuration reload: `docker-compose restart kong`
3. Service restart: `docker-compose restart <service-name>`

### Issue: Rate limits too strict

**Solution:**

1. Adjust limits in Kong config: `infrastructure/gateway/kong/kong.yml`
2. Update NestJS throttler config in `app.module.ts`
3. Modify FastAPI rate limit configs in `rate_limiting.py`
4. Reload configuration

### Issue: Headers not appearing

**Check:**

1. Kong response-transformer plugin configured
2. NestJS throttler guard enabled
3. FastAPI middleware properly added

---

## Files Modified/Created

### Modified Files

1. `/home/user/sahool-unified-v15-idp/infrastructure/gateway/kong/kong.yml`
   - Added authentication endpoints with rate limiting
   - Updated admin endpoint rate limits

### Created Files

1. `/home/user/sahool-unified-v15-idp/apps/services/shared/auth/rate_limiting.py`
   - Authentication-specific rate limiting for FastAPI

2. `/home/user/sahool-unified-v15-idp/apps/services/shared/auth/auth_endpoints_example.py`
   - Example FastAPI authentication endpoints with rate limiting

3. `/home/user/sahool-unified-v15-idp/apps/services/shared/auth/auth.controller.example.ts`
   - Example NestJS authentication controller with throttling

4. `/home/user/sahool-unified-v15-idp/RATE_LIMITING_IMPLEMENTATION.md`
   - This documentation file

### Existing Files (No Changes Needed)

1. `/home/user/sahool-unified-v15-idp/apps/services/shared/middleware/rate_limiter.py`
   - Already has comprehensive rate limiting middleware

2. All NestJS services already have `@nestjs/throttler` installed and configured

---

## Next Steps

1. **Test the implementation**:

   ```bash
   # Start the services
   docker-compose up -d

   # Test rate limits
   bash /home/user/sahool-unified-v15-idp/scripts/test_rate_limits.sh
   ```

2. **Implement authentication services** using the examples provided

3. **Monitor rate limit violations** and adjust limits as needed

4. **Set up alerts** for suspicious activity patterns

5. **Document API rate limits** in API documentation

---

## References

- [Kong Rate Limiting Plugin](https://docs.konghq.com/hub/kong-inc/rate-limiting/)
- [NestJS Throttler](https://docs.nestjs.com/security/rate-limiting)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [OWASP Brute Force Prevention](https://owasp.org/www-community/controls/Blocking_Brute_Force_Attacks)

---

## Support

For questions or issues with rate limiting implementation:

- Check logs: `docker-compose logs kong` or `docker-compose logs <service-name>`
- Review Redis: `docker-compose exec redis redis-cli -a $REDIS_PASSWORD`
- Test endpoint: Use curl with `-v` flag to see headers

---

**Last Updated**: 2026-01-01
**Version**: 16.0.0
**Status**: ✅ Production Ready
