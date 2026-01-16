# Rate Limiting Configuration Across SAHOOL Services

## Overview

This document provides a comprehensive overview of rate limiting implementation across all critical Python services in the SAHOOL platform. Rate limiting is implemented using Redis-backed distributed rate limiting with in-memory fallback for development.

## Rate Limit Tiers

The platform uses the following rate limit tiers defined in `/apps/services/shared/middleware/rate_limiter.py`:

### Tier Configuration

| Tier          | Requests/Min | Requests/Hour | Burst Limit | Use Case                                  |
| ------------- | ------------ | ------------- | ----------- | ----------------------------------------- |
| **FREE**      | 30           | 500           | 5           | Free tier users                           |
| **STANDARD**  | 60           | 2,000         | 10          | Standard API endpoints                    |
| **PREMIUM**   | 120          | 5,000         | 20          | Premium users / High-volume endpoints     |
| **INTERNAL**  | 1,000        | 50,000        | 100         | Internal service-to-service communication |
| **UNLIMITED** | ∞            | ∞             | ∞           | No rate limiting (disabled)               |

### Environment Variables

Rate limits can be configured via environment variables:

```bash
# FREE Tier
RATE_LIMIT_FREE_RPM=30
RATE_LIMIT_FREE_RPH=500
RATE_LIMIT_FREE_BURST=5

# STANDARD Tier
RATE_LIMIT_STANDARD_RPM=60
RATE_LIMIT_STANDARD_RPH=2000
RATE_LIMIT_STANDARD_BURST=10

# PREMIUM Tier
RATE_LIMIT_PREMIUM_RPM=120
RATE_LIMIT_PREMIUM_RPH=5000
RATE_LIMIT_PREMIUM_BURST=20

# INTERNAL Tier
RATE_LIMIT_INTERNAL_RPM=1000
RATE_LIMIT_INTERNAL_RPH=50000
RATE_LIMIT_INTERNAL_BURST=100

# Redis Configuration
REDIS_URL=redis://redis:6379/0
```

## Services with Rate Limiting

### 1. **billing-core** ✅

**Port:** 8089
**Rate Limiting:** Enabled
**Configuration:**

- Uses Redis-backed rate limiting when REDIS_URL is available
- Excludes webhook endpoints from rate limiting:
  - `/healthz`
  - `/v1/webhooks/stripe`
  - `/v1/webhooks/tharwatt`
- **Tier Strategy:** Default tier function (IP-based, checks internal service header)

**Rationale:**

- Payment endpoints need protection against abuse
- Webhooks excluded to prevent payment processing delays

---

### 2. **ai-advisor** ✅

**Port:** 8115
**Rate Limiting:** Enabled
**Configuration:**

- Uses shared rate_limit_middleware with custom rate_limiter
- Excludes health and monitoring endpoints:
  - `/healthz`
  - `/docs`
  - `/redoc`
  - `/openapi.json`
- **Tier Strategy:** Default (checks X-Internal-Service header, X-Rate-Limit-Tier header)

**Rationale:**

- AI advisory endpoints are compute-intensive and costly
- Need to prevent abuse and control LLM costs
- Monitoring endpoints excluded for operational visibility

---

### 3. **ai-agents-core** ✅ **(Newly Added)**

**Port:** 8120
**Rate Limiting:** Enabled
**Configuration:**

- Custom tier function based on endpoint type:
  - `/api/v1/analyze`: STANDARD tier (60/min) - Full field analysis is resource-intensive
  - `/api/v1/edge/*`: PREMIUM tier (120/min) - Edge endpoints need higher throughput
  - Other endpoints: STANDARD tier (60/min)
  - Internal services: INTERNAL tier (1000/min)
- Excluded paths:
  - `/healthz`
  - `/api/v1/system/status`

**Rationale:**

- Multi-agent AI analysis is extremely resource-intensive
- Different endpoints have different resource requirements
- Edge endpoints (mobile, IoT) need higher limits for real-time operations
- Analysis endpoints need stricter limits to prevent system overload

---

### 4. **iot-gateway** ✅ **(Newly Added)**

**Port:** 8106
**Rate Limiting:** Enabled
**Configuration:**

- Custom tier function based on endpoint type:
  - `/sensor/reading`: STANDARD tier (60/min) - Single sensor readings
  - `/sensor/batch`: PREMIUM tier (120/min) - Batch uploads need higher limits
  - `/device/*`: PREMIUM tier (120/min) - Device management operations
  - Internal services: INTERNAL tier (1000/min)
- Excluded paths:
  - `/healthz`
  - `/health`
  - `/stats`

**Rationale:**

- IoT endpoints are vulnerable to sensor data flooding attacks
- Batch endpoints need higher limits for efficient data ingestion
- Device registration and management need protection
- Health endpoints excluded for monitoring

---

### 5. **field-management-service** ✅

**Port:** 8083
**Rate Limiting:** Enabled
**Configuration:**

- Uses default rate limiting configuration
- Standard middleware setup

**Rationale:**

- Field data management needs protection against bulk operations
- Prevents accidental or malicious mass field creation/updates

---

### 6. **inventory-service** ✅

**Port:** 8084
**Rate Limiting:** Enabled
**Configuration:**

- Uses default rate limiting configuration
- Standard middleware setup

**Rationale:**

- Inventory operations need protection against mass updates
- Prevents inventory manipulation attacks

---

### 7. **notification-service** ✅

**Port:** 8085
**Rate Limiting:** Enabled
**Configuration:**

- Uses default rate limiting configuration
- Standard middleware setup

**Rationale:**

- Critical to prevent notification spam
- Protects against mass notification abuse
- Prevents email/SMS quota exhaustion

---

### 8. **satellite-service** ✅

**Port:** 8086
**Rate Limiting:** Enabled
**Configuration:**

- Uses default rate limiting configuration
- Standard middleware setup

**Rationale:**

- Satellite data analysis is expensive (external API costs)
- Need to prevent excessive satellite API calls
- Protects third-party API quota

---

## Services Without Rate Limiting

### Services Not Requiring Rate Limiting

The following services do not exist as Python services or are not user-facing:

- **user-service**: No Python implementation (handled by auth service)
- **marketplace-service**: Does not exist

## Rate Limiting Headers

All rate-limited responses include the following headers:

```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 42
X-RateLimit-Reset: 45
```

When rate limit is exceeded, the service returns:

```http
HTTP/1.1 429 Too Many Requests
Content-Type: application/json

{
  "error": "rate_limit_exceeded",
  "message": "Too many requests. Please slow down.",
  "retry_after": 45
}
```

## Architecture

### Redis-Backed Distributed Rate Limiting

- **Production:** Uses Redis for distributed rate limiting across multiple service instances
- **Development:** Falls back to in-memory rate limiting when Redis is unavailable
- **Algorithm:** Sliding window with sorted sets for accurate rate limiting

### Key Features

1. **Automatic Header Injection:** Rate limit information in every response
2. **Multiple Tiers:** FREE, STANDARD, PREMIUM, INTERNAL, UNLIMITED
3. **Configurable:** Via environment variables
4. **Failsafe:** Graceful fallback to in-memory limiter
5. **Tenant-Aware:** Can be configured per tenant/user
6. **IP-Based:** Default key based on client IP (X-Forwarded-For aware)

## Security Considerations

### Internal Service Authentication

Services can bypass rate limiting by including the header:

```http
X-Internal-Service: true
```

**⚠️ Security Note:** This header should only be set by authenticated internal services. API Gateway must strip this header from external requests.

### Rate Limit Tier Header

Clients can request a specific tier (if authorized):

```http
X-Rate-Limit-Tier: premium
```

**⚠️ Security Note:** Tier selection should be validated against user's subscription level. Unauthorized tier requests should be rejected or downgraded.

## Monitoring and Alerts

### Key Metrics to Monitor

1. **Rate Limit Hit Rate:** % of requests hitting rate limits
2. **Tier Distribution:** Distribution of requests across tiers
3. **Redis Health:** Redis connection status and latency
4. **Fallback Usage:** How often in-memory fallback is used

### Recommended Alerts

```yaml
- alert: HighRateLimitHitRate
  condition: rate_limit_exceeded_total > 100/min
  severity: warning
  description: "High rate of requests hitting rate limits"

- alert: RedisRateLimiterDown
  condition: redis_rate_limiter_available == 0
  severity: critical
  description: "Redis rate limiter unavailable, using in-memory fallback"

- alert: SuspiciousRateLimitPattern
  condition: rate_limit_exceeded_per_ip > 1000/hour
  severity: warning
  description: "Possible DDoS or scraping attack detected"
```

## Testing Rate Limits

### Test with curl

```bash
# Test standard endpoint
for i in {1..70}; do
  curl -s -o /dev/null -w "%{http_code}\n" \
    http://localhost:8120/api/v1/analyze \
    -H "Content-Type: application/json" \
    -d '{"field_id":"test","crop_type":"wheat"}'
done

# First 60 should return 200, next 10 should return 429
```

### Test with Python

```python
import requests
import time

endpoint = "http://localhost:8120/api/v1/analyze"
headers = {"Content-Type": "application/json"}
data = {"field_id": "test", "crop_type": "wheat"}

for i in range(70):
    response = requests.post(endpoint, json=data, headers=headers)
    print(f"Request {i+1}: {response.status_code}")

    if response.status_code == 429:
        retry_after = response.headers.get("X-RateLimit-Reset")
        print(f"Rate limited! Retry after {retry_after} seconds")
        break

    time.sleep(0.1)
```

## Best Practices

### For Service Developers

1. **Always use `setup_rate_limiting()`** when creating new services
2. **Exclude health endpoints** from rate limiting
3. **Configure appropriate tiers** based on endpoint resource requirements
4. **Use Redis in production** for distributed rate limiting
5. **Log rate limit events** for monitoring and debugging
6. **Test rate limiting** before deploying to production

### For API Consumers

1. **Respect rate limit headers** in responses
2. **Implement exponential backoff** when rate limited
3. **Use batch endpoints** when available
4. **Cache responses** to reduce API calls
5. **Request higher tier** if needed for your use case

## Troubleshooting

### Rate Limiting Not Working

1. Check if Redis is running: `redis-cli ping`
2. Verify REDIS_URL environment variable
3. Check service logs for rate limiting initialization
4. Verify middleware order (rate limiting should be last)

### False Positives

1. Check if IP is being correctly extracted (X-Forwarded-For)
2. Verify tier configuration
3. Check if internal service header is being stripped by gateway
4. Review Redis key TTLs

### Performance Issues

1. Monitor Redis latency
2. Check if too many keys in Redis (cleanup old entries)
3. Consider increasing rate limits for legitimate high-volume users
4. Review tier assignments

## Future Enhancements

1. **Per-User Rate Limiting:** Track limits per authenticated user instead of IP
2. **Dynamic Tier Adjustment:** Automatically adjust tiers based on subscription
3. **Burst Protection:** Enhanced burst detection and prevention
4. **Geographic Rate Limiting:** Different limits based on geographic region
5. **Cost-Based Limiting:** Rate limits based on operation cost (LLM tokens, compute)
6. **Adaptive Limits:** Machine learning-based adaptive rate limiting

## Related Documentation

- [Middleware Architecture](/docs/middleware-architecture.md)
- [Security Best Practices](/docs/security-best-practices.md)
- [API Gateway Configuration](/docs/api-gateway-configuration.md)
- [Redis Setup Guide](/docs/redis-setup.md)

---

**Last Updated:** 2026-01-08
**Maintainer:** Platform Security Team
**Status:** Production Ready ✅
