# SAHOOL Platform - Rate Limiting Documentation

# توثيق تحديد المعدل - منصة سهول

**Version:** v16.0.0  
**Last Updated:** 2026-01-05  
**Status:** Production Ready ✅

---

## 📋 Overview | نظرة عامة

SAHOOL platform implements a comprehensive rate limiting system to protect APIs from abuse and ensure fair resource allocation.

تنفذ منصة سهول نظام شامل لتحديد المعدل لحماية واجهات برمجة التطبيقات من الإساءة وضمان التوزيع العادل للموارد.

### Features | الميزات

- ✅ **Redis-backed** - Distributed rate limiting across multiple servers
- ✅ **In-memory fallback** - Works without Redis in development
- ✅ **Multiple tiers** - Free, Basic, Pro, Enterprise, Internal
- ✅ **Flexible algorithms** - Token Bucket + Sliding Window
- ✅ **Per-endpoint customization** - Different limits for different APIs
- ✅ **Real-time monitoring** - Track usage via headers and metrics
- ✅ **Graceful degradation** - Continues working if Redis fails

---

## 🎯 Rate Limit Tiers | مستويات تحديد المعدل

### Tier Comparison | مقارنة المستويات

| Tier           | RPM (Requests/Min) | RPH (Requests/Hour) | Burst | Use Case                      |
| -------------- | ------------------ | ------------------- | ----- | ----------------------------- |
| **Free**       | 30                 | 500                 | 5     | Public API, Testing           |
| **Basic**      | 60                 | 2,000               | 10    | Small farms, Individual users |
| **Pro**        | 120                | 5,000               | 20    | Medium farms, Business users  |
| **Enterprise** | 500                | 20,000              | 50    | Large operations, Partners    |
| **Internal**   | 1,000              | 50,000              | 100   | Service-to-service calls      |

**RPM:** Requests per minute (طلبات في الدقيقة)  
**RPH:** Requests per hour (طلبات في الساعة)  
**Burst:** Temporary spike allowance (السماح بالارتفاع المؤقت)

---

## ⚙️ Configuration | التكوين

### Environment Variables | المتغيرات البيئية

```bash
# Enable/Disable Rate Limiting
RATE_LIMIT_ENABLED=true

# Redis Configuration (Required for production)
REDIS_URL="redis://:password@redis:6379/0"
REDIS_RATE_LIMIT_DB=1  # Separate DB for rate limiting

# Free Tier Limits
RATE_LIMIT_FREE_RPM=30
RATE_LIMIT_FREE_RPH=500
RATE_LIMIT_FREE_BURST=5

# Basic Tier Limits
RATE_LIMIT_BASIC_RPM=60
RATE_LIMIT_BASIC_RPH=2000
RATE_LIMIT_BASIC_BURST=10

# Pro Tier Limits
RATE_LIMIT_PRO_RPM=120
RATE_LIMIT_PRO_RPH=5000
RATE_LIMIT_PRO_BURST=20

# Enterprise Tier Limits
RATE_LIMIT_ENTERPRISE_RPM=500
RATE_LIMIT_ENTERPRISE_RPH=20000
RATE_LIMIT_ENTERPRISE_BURST=50

# Internal Service Limits
RATE_LIMIT_INTERNAL_RPM=1000
RATE_LIMIT_INTERNAL_RPH=50000
RATE_LIMIT_INTERNAL_BURST=100

# Rate Limit Response Headers
RATE_LIMIT_HEADERS_ENABLED=true

# Ban on Excessive Violations
RATE_LIMIT_BAN_ENABLED=true
RATE_LIMIT_BAN_THRESHOLD=10  # violations before ban (adjustable based on tier)
RATE_LIMIT_BAN_DURATION=3600  # ban duration in seconds (1 hour)

# Note: Ban threshold of 10 is conservative to avoid false positives from legitimate
# traffic spikes or network issues. For stricter control, reduce to 5-7 violations.
# Consider implementing tier-based thresholds (e.g., Free: 5, Pro: 15).
```

---

## 🚀 Usage Examples | أمثلة الاستخدام

### 1. Apply to All Routes | تطبيق على جميع المسارات

```python
from fastapi import FastAPI
from shared.middleware.rate_limiter import RateLimitMiddleware

app = FastAPI(title="SAHOOL Field Service")

# Add rate limiting middleware
app.add_middleware(
    RateLimitMiddleware,
    tier="basic",  # Default tier for all routes
    redis_url=settings.REDIS_URL
)
```

### 2. Per-Endpoint Rate Limiting | تحديد المعدل لكل نقطة نهاية

```python
from fastapi import APIRouter, Depends
from shared.middleware.rate_limiter import rate_limit

router = APIRouter()

# Public endpoint - Free tier
@router.get("/public/fields")
@rate_limit(tier="free")
async def list_public_fields():
    """List fields - Free tier (30 req/min)"""
    return {"fields": []}

# Authenticated endpoint - Basic tier
@router.get("/fields")
@rate_limit(tier="basic")
async def list_fields(user: User = Depends(get_current_user)):
    """List user's fields - Basic tier (60 req/min)"""
    return {"fields": user.fields}

# Premium feature - Pro tier
@router.get("/fields/analytics")
@rate_limit(tier="pro")
async def get_field_analytics(user: User = Depends(get_current_user)):
    """Advanced analytics - Pro tier (120 req/min)"""
    return {"analytics": {}}

# Internal API - Internal tier
@router.get("/internal/sync")
@rate_limit(tier="internal")
async def internal_sync(api_key: str = Depends(verify_internal_key)):
    """Internal sync endpoint - Internal tier (1000 req/min)"""
    return {"status": "synced"}
```

### 3. Custom Rate Limits | حدود مخصصة

```python
from shared.middleware.rate_limiter import rate_limit, RateLimitConfig

# Custom rate limit for expensive operation
@router.post("/fields/{field_id}/analyze")
@rate_limit(
    config=RateLimitConfig(
        requests_per_minute=10,
        requests_per_hour=100,
        burst_size=2
    )
)
async def analyze_field(field_id: str):
    """Expensive AI analysis - Custom limits (10 req/min)"""
    return await run_ai_analysis(field_id)

# Different limits for different HTTP methods
@router.get("/inventory")
@rate_limit(tier="basic")  # 60 req/min for GET
async def list_inventory():
    return {"items": []}

@router.post("/inventory")
@rate_limit(tier="pro")  # 120 req/min for POST
async def create_inventory_item(item: InventoryItem):
    return {"id": "new-item-id"}
```

### 4. User-Based Rate Limiting | تحديد المعدل حسب المستخدم

```python
from shared.middleware.rate_limiter import rate_limit_by_user

@router.get("/profile")
@rate_limit_by_user(tier_field="subscription_tier")
async def get_profile(user: User = Depends(get_current_user)):
    """
    Rate limit based on user's subscription tier.
    Free users: 30 req/min
    Basic users: 60 req/min
    Pro users: 120 req/min
    """
    return user.profile
```

### 5. IP-Based Rate Limiting | تحديد المعدل حسب IP

```python
from shared.middleware.rate_limiter import rate_limit_by_ip

# Protect login endpoint from brute force
@router.post("/auth/login")
@rate_limit_by_ip(
    config=RateLimitConfig(
        requests_per_minute=5,
        requests_per_hour=20,
        burst_size=1
    )
)
async def login(credentials: LoginRequest):
    """Login - 5 attempts per minute per IP"""
    return await authenticate(credentials)
```

---

## 📊 Response Headers | رؤوس الاستجابة

When rate limiting is enabled, the following headers are included in responses:

عند تفعيل تحديد المعدل، يتم تضمين الرؤوس التالية في الاستجابات:

```http
X-RateLimit-Limit: 60          # Max requests per window
X-RateLimit-Remaining: 45      # Remaining requests
X-RateLimit-Reset: 1609459200  # Unix timestamp when limit resets
X-RateLimit-Tier: basic        # Current tier
Retry-After: 30                # Seconds to wait (only when rate limited)
```

### Example Response | مثال على الاستجابة

```bash
# Successful request
curl -i https://api.sahool.com/fields

HTTP/1.1 200 OK
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 1704492000
X-RateLimit-Tier: basic
Content-Type: application/json

{"fields": [...]}
```

```bash
# Rate limited request
curl -i https://api.sahool.com/fields

HTTP/1.1 429 Too Many Requests
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1704492060
X-RateLimit-Tier: basic
Retry-After: 60
Content-Type: application/json

{
  "error": "rate_limit_exceeded",
  "message": "Too many requests. Please try again later.",
  "retry_after": 60
}
```

---

## 🔍 Monitoring & Metrics | المراقبة والمقاييس

### Prometheus Metrics | مقاييس Prometheus

```promql
# Total requests by tier
rate_limit_requests_total{tier="basic"}

# Rate limit violations
rate_limit_violations_total{tier="basic"}

# Current rate limit usage
rate_limit_current_usage{tier="basic"}

# Redis connection status
rate_limit_redis_connected
```

### Logging | السجلات

```python
# Rate limit violation logs
{
  "level": "warning",
  "message": "Rate limit exceeded",
  "user_id": "user-123",
  "ip": "192.168.1.100",
  "tier": "basic",
  "endpoint": "/fields",
  "limit": 60,
  "current": 61,
  "timestamp": "2026-01-05T21:00:00Z"
}

# Ban event logs
{
  "level": "error",
  "message": "User banned for excessive violations",
  "user_id": "user-456",
  "violations": 12,
  "ban_duration": 3600,
  "timestamp": "2026-01-05T21:05:00Z"
}
```

---

## 🛡️ Security Features | ميزات الأمان

### 1. Automatic IP Banning | الحظر التلقائي لعنوان IP

Users who exceed rate limits excessively can be automatically banned:

```python
# Configuration
RATE_LIMIT_BAN_ENABLED=true
RATE_LIMIT_BAN_THRESHOLD=10  # 10 violations within window
RATE_LIMIT_BAN_DURATION=3600  # 1 hour ban

# Programmatic ban
from shared.middleware.rate_limiter import ban_ip, unban_ip

# Ban an IP
ban_ip("192.168.1.100", duration=3600, reason="abuse")

# Unban an IP
unban_ip("192.168.1.100")

# Check if IP is banned
is_banned = await check_ip_banned("192.168.1.100")
```

### 2. Whitelist / Blacklist | القائمة البيضاء / السوداء

```python
from shared.middleware.rate_limiter import (
    add_to_whitelist,
    add_to_blacklist,
    remove_from_whitelist,
    remove_from_blacklist
)

# Whitelist an IP (bypass rate limits)
add_to_whitelist("192.168.1.50", reason="trusted_partner")

# Blacklist an IP (always deny)
add_to_blacklist("192.168.1.100", reason="malicious_activity")

# Remove from lists
remove_from_whitelist("192.168.1.50")
remove_from_blacklist("192.168.1.100")
```

### 3. Burst Protection | حماية من الانفجار

```python
# Token bucket algorithm with burst protection
# Allows temporary spikes but prevents sustained abuse

# Example: Basic tier allows burst of 10 requests
# - User can send 10 requests instantly
# - Then limited to 1 request per second (60/min)
# - Bucket refills at 1 token/second
```

---

## 🔧 Advanced Configuration | التكوين المتقدم

### Custom Rate Limit Strategy | استراتيجية مخصصة

```python
from shared.middleware.rate_limiter import RateLimiter, RateLimitStrategy

class CustomRateLimitStrategy(RateLimitStrategy):
    """Custom strategy: Different limits for weekdays vs weekends"""

    async def get_limit(self, user, request):
        from datetime import datetime

        is_weekend = datetime.now().weekday() >= 5

        if is_weekend:
            # Double limits on weekends
            return user.tier.rpm * 2, user.tier.rph * 2
        else:
            return user.tier.rpm, user.tier.rph

# Use custom strategy
limiter = RateLimiter(strategy=CustomRateLimitStrategy())
```

### Dynamic Rate Limits | حدود ديناميكية

```python
from shared.middleware.rate_limiter import dynamic_rate_limit

@router.get("/fields")
@dynamic_rate_limit(
    calculate_limit=lambda user: (
        user.subscription_tier.rpm,
        user.subscription_tier.rph
    )
)
async def list_fields(user: User = Depends(get_current_user)):
    """Rate limit based on user's subscription tier"""
    return {"fields": user.fields}
```

---

## 🧪 Testing | الاختبار

### Unit Tests | اختبارات الوحدة

```python
import pytest
from shared.middleware.rate_limiter import RateLimiter, RateLimitConfig

@pytest.mark.asyncio
async def test_rate_limit_enforcement():
    limiter = RateLimiter(
        config=RateLimitConfig(
            requests_per_minute=5,
            requests_per_hour=100,
            burst_size=2
        )
    )

    # First 7 requests should pass (5 + 2 burst)
    for i in range(7):
        assert await limiter.check("test-user") == True

    # 8th request should be rate limited
    assert await limiter.check("test-user") == False

@pytest.mark.asyncio
async def test_rate_limit_reset():
    limiter = RateLimiter(redis_url="redis://localhost")

    # Consume all requests
    for i in range(60):
        await limiter.check("test-user")

    # Should be rate limited
    assert await limiter.check("test-user") == False

    # Wait for reset
    await asyncio.sleep(61)

    # Should work again
    assert await limiter.check("test-user") == True
```

### Integration Tests | اختبارات التكامل

```python
from fastapi.testclient import TestClient

def test_rate_limit_headers(client: TestClient):
    # First request
    response = client.get("/fields")
    assert response.status_code == 200
    assert "X-RateLimit-Limit" in response.headers
    assert "X-RateLimit-Remaining" in response.headers
    assert int(response.headers["X-RateLimit-Remaining"]) == 59

def test_rate_limit_exceeded(client: TestClient):
    # Exhaust rate limit
    for i in range(60):
        client.get("/fields")

    # Next request should be rate limited
    response = client.get("/fields")
    assert response.status_code == 429
    assert "Retry-After" in response.headers
    assert response.json()["error"] == "rate_limit_exceeded"
```

---

## 🚨 Troubleshooting | حل المشاكل

### Common Issues | المشاكل الشائعة

#### 1. Rate Limits Not Working

```bash
# Check if Redis is running
redis-cli ping

# Check rate limit configuration
echo $RATE_LIMIT_ENABLED

# Check logs
docker logs field-service | grep rate_limit
```

#### 2. Too Strict Limits

```bash
# Increase limits temporarily
export RATE_LIMIT_BASIC_RPM=120

# Or upgrade user tier
UPDATE users SET subscription_tier = 'pro' WHERE id = 'user-123';
```

#### 3. Redis Connection Issues

```python
# Fallback to in-memory rate limiting
RATE_LIMIT_FALLBACK_TO_MEMORY=true

# Or check Redis connection
import redis
r = redis.from_url(os.getenv("REDIS_URL"))
r.ping()  # Should return True
```

---

## 📚 API Reference | مرجع API

### RateLimiter Class

```python
class RateLimiter:
    """Main rate limiter class"""

    def __init__(
        self,
        redis_url: str = None,
        config: RateLimitConfig = None,
        strategy: RateLimitStrategy = None
    ):
        """Initialize rate limiter"""

    async def check(
        self,
        key: str,
        cost: int = 1
    ) -> bool:
        """Check if request should be allowed"""

    async def get_usage(self, key: str) -> Dict:
        """Get current usage statistics"""

    async def reset(self, key: str):
        """Reset rate limit for key"""
```

### Decorators

```python
@rate_limit(tier: str = "basic")
@rate_limit_by_user(tier_field: str = "subscription_tier")
@rate_limit_by_ip(config: RateLimitConfig = None)
@dynamic_rate_limit(calculate_limit: Callable)
```

---

## 🔄 Migration from Old System | الترحيل من النظام القديم

If you're migrating from an older rate limiting implementation:

```python
# Old code
from old_rate_limiter import rate_limit as old_rate_limit

@old_rate_limit(max_requests=60, window=60)
async def my_endpoint():
    pass

# New code
from shared.middleware.rate_limiter import rate_limit

@rate_limit(tier="basic")  # 60 req/min
async def my_endpoint():
    pass
```

---

## 📖 References | المراجع

- [GAPS_AND_RECOMMENDATIONS.md](../GAPS_AND_RECOMMENDATIONS.md) - Original recommendations
- [Security Headers](../shared/middleware/security_headers.py) - Security middleware
- [Production Deployment](./PRODUCTION_DEPLOYMENT.md) - Deployment guide
- [Rate Limiting Guide](../shared/middleware/RATE_LIMITING_GUIDE.md) - Original guide
- [OWASP Rate Limiting](https://owasp.org/www-community/controls/Blocking_Brute_Force_Attacks)

---

**Author:** GitHub Copilot Agent  
**Version:** v1.0  
**Last Updated:** 2026-01-05
