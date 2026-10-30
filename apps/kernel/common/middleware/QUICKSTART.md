# SAHOOL Rate Limiter - Quick Start Guide

# دليل البدء السريع لحد معدل الطلبات

Get started with SAHOOL's advanced rate limiting in 5 minutes!

ابدأ مع حد معدل الطلبات المتقدم لسهول في 5 دقائق!

## Prerequisites | المتطلبات

```bash
# 1. Start Redis (Docker)
docker run -d --name redis -p 6379:6379 redis:7-alpine

# 2. Install dependencies
pip install fastapi redis uvicorn
```

## Step 1: Basic Setup | الخطوة 1: الإعداد الأساسي

Create a simple FastAPI application with rate limiting:

أنشئ تطبيق FastAPI بسيط مع حد المعدل:

```python
# app.py
from fastapi import FastAPI, Request
from apps.kernel.common.middleware import setup_rate_limiting

# Create app
app = FastAPI(title="My SAHOOL Service")

# Setup rate limiting (one line!)
limiter = setup_rate_limiting(app)


# Your endpoints
@app.get("/api/data")
async def get_data():
    return {"data": "some data"}


@app.get("/healthz")
async def health():
    return {"status": "healthy"}  # Unlimited (excluded by default)
```

Run it:

```bash
uvicorn app:app --reload
```

## Step 2: Test It | الخطوة 2: اختبره

```bash
# Make requests
for i in {1..70}; do
  curl -i http://localhost:8000/api/data
done

# You'll see rate limit headers:
# X-RateLimit-Limit: 60
# X-RateLimit-Remaining: 45
# X-RateLimit-Reset: 30

# After 60 requests in 1 minute, you'll get:
# HTTP/1.1 429 Too Many Requests
```

## Step 3: Custom Limits | الخطوة 3: حدود مخصصة

Use the `@rate_limit` decorator for custom endpoint limits:

استخدم ديكوريتر `@rate_limit` لحدود مخصصة لنقاط النهاية:

```python
from apps.kernel.common.middleware import rate_limit


@app.post("/api/heavy-task")
@rate_limit(requests=5, period=60, strategy="token_bucket", burst=2)
async def heavy_task(request: Request):
    # Only 5 requests/minute with 2 burst
    return {"status": "processing"}


@app.get("/api/quick-query")
@rate_limit(requests=100, period=60, strategy="fixed_window")
async def quick_query(request: Request):
    # 100 requests/minute
    return {"result": "data"}
```

## Step 4: Choose Your Strategy | الخطوة 4: اختر استراتيجيتك

### Fixed Window (النافذة الثابتة)

**Best for**: High-frequency endpoints

```python
@rate_limit(requests=100, period=60, strategy="fixed_window")
```

### Sliding Window (النافذة المنزلقة) - **DEFAULT**

**Best for**: Most use cases

```python
@rate_limit(requests=60, period=60, strategy="sliding_window")
```

### Token Bucket (دلو الرموز)

**Best for**: Bursty traffic

```python
@rate_limit(requests=10, period=60, strategy="token_bucket", burst=5)
```

## Step 5: Client Identification | الخطوة 5: تحديد هوية العميل

Clients are automatically identified by (in order):

يتم تحديد هوية العملاء تلقائيًا بـ (بالترتيب):

1. **API Key** - Send `X-API-Key` header
2. **User ID** - From authentication
3. **IP Address** - Fallback

```bash
# With API Key
curl -H "X-API-Key: your-api-key" http://localhost:8000/api/data

# Without API Key (uses IP)
curl http://localhost:8000/api/data
```

## Step 6: Monitor & Manage | الخطوة 6: راقب وأدر

### Get Statistics

```python
from apps.kernel.common.middleware import get_rate_limit_stats, ClientIdentifier


@app.get("/api/my-stats")
async def my_stats(request: Request):
    client_id = ClientIdentifier.get_client_id(request)
    stats = await get_rate_limit_stats(limiter, client_id)
    return stats
```

### Reset Limits (Admin)

```python
@app.post("/admin/reset-limits")
async def reset_limits(client_id: str):
    await limiter.reset_limits(client_id)
    return {"status": "reset"}
```

## Common Patterns | الأنماط الشائعة

### Pattern 1: Different Limits for Different Endpoints

```python
from apps.kernel.common.middleware import ENDPOINT_CONFIGS, EndpointConfig

# Heavy processing
ENDPOINT_CONFIGS["/api/v1/analyze"] = EndpointConfig(requests=10, period=60, strategy="token_bucket", burst=2)

# Standard queries
ENDPOINT_CONFIGS["/api/v1/data"] = EndpointConfig(requests=60, period=60, strategy="sliding_window")

# High-frequency sensor data
ENDPOINT_CONFIGS["/api/v1/sensors"] = EndpointConfig(requests=100, period=60, strategy="fixed_window")
```

### Pattern 2: Organization-Based Rate Limiting

```python
def org_based_identifier(request: Request) -> str:
    org_id = request.headers.get("X-Organization-ID")
    if org_id:
        return f"org:{org_id}"

    from apps.kernel.common.middleware import ClientIdentifier

    return ClientIdentifier.get_client_id(request)


# Setup with custom identifier
limiter = setup_rate_limiting(app, identifier_func=org_based_identifier)
```

### Pattern 3: Manual Rate Limit Checks

```python
@app.post("/api/conditional")
async def conditional_endpoint(request: Request, action: str):
    client_id = ClientIdentifier.get_client_id(request)

    # Different limits based on action
    if action == "expensive":
        allowed, remaining, reset = await limiter.check_rate_limit(
            client_id=client_id,
            endpoint="/api/v1/analyze",  # Uses analyze limits
        )
    else:
        allowed, remaining, reset = await limiter.check_rate_limit(
            client_id=client_id,
            endpoint="/api/v1/data",  # Uses data limits
        )

    if not allowed:
        raise HTTPException(status_code=429, detail=f"Rate limit exceeded. Retry after {reset} seconds")

    return {"action": action, "remaining": remaining}
```

## Environment Variables | متغيرات البيئة

```bash
# .env
REDIS_URL=redis://localhost:6379/0
```

## Troubleshooting | استكشاف الأخطاء

### Issue: Rate limiting not working

```python
# Check Redis connection
import redis.asyncio as redis

client = redis.from_url("redis://localhost:6379/0")
await client.ping()  # Should return True
```

### Issue: All requests are rate limited

```python
# Check your limits are reasonable
ENDPOINT_CONFIGS["/api/endpoint"] = EndpointConfig(
    requests=60,  # Not 6!
    period=60,
)
```

### Issue: Need to clear limits for testing

```python
# Reset all limits for a client
await limiter.reset_limits("ip:127.0.0.1")

# Or use Redis CLI
redis-cli --scan --pattern "ratelimit:*" | xargs redis-cli del
```

## Next Steps | الخطوات التالية

- Read the [full README](README.md) for advanced features
- Check [example_usage.py](example_usage.py) for more examples
- Run [test_rate_limiter.py](test_rate_limiter.py) for testing
- Deploy to production with Redis cluster

## Production Checklist | قائمة التحقق للإنتاج

- [ ] Redis is running and accessible
- [ ] Redis has persistence enabled
- [ ] Rate limits are configured appropriately
- [ ] Health check endpoints are excluded
- [ ] Monitoring is set up for rate limit events
- [ ] Error messages are clear and helpful
- [ ] API documentation includes rate limit info
- [ ] Load testing completed successfully

## Complete Example | مثال كامل

```python
# production_app.py
from fastapi import FastAPI, Request, HTTPException
from apps.kernel.common.middleware import (
    setup_rate_limiting,
    rate_limit,
    ENDPOINT_CONFIGS,
    EndpointConfig,
)

# Create app
app = FastAPI(title="SAHOOL Agricultural Platform", version="1.0.0")

# Configure endpoint-specific limits
ENDPOINT_CONFIGS["/api/v1/satellite-analysis"] = EndpointConfig(requests=3, period=60, strategy="sliding_window")

ENDPOINT_CONFIGS["/api/v1/weather"] = EndpointConfig(requests=60, period=60, strategy="sliding_window")

ENDPOINT_CONFIGS["/api/v1/sensors"] = EndpointConfig(requests=100, period=60, strategy="fixed_window")

# Setup rate limiting
limiter = setup_rate_limiting(
    app, redis_url="redis://redis:6379/0", exclude_paths=["/healthz", "/readyz", "/metrics", "/docs"]
)


# Endpoints
@app.get("/api/v1/weather")
async def get_weather(location: str):
    """60 requests/min - configured in ENDPOINT_CONFIGS"""
    return {"temperature": 25, "location": location}


@app.get("/api/v1/sensors")
async def get_sensors():
    """100 requests/min - configured in ENDPOINT_CONFIGS"""
    return {"sensors": []}


@app.post("/api/v1/satellite-analysis")
async def analyze_satellite(field_id: str):
    """3 requests/min - configured in ENDPOINT_CONFIGS"""
    return {"status": "analyzing", "field_id": field_id}


@app.post("/api/v1/custom-heavy")
@rate_limit(requests=5, period=60, strategy="token_bucket", burst=2)
async def custom_heavy(request: Request):
    """5 requests/min with 2 burst - uses decorator"""
    return {"status": "processing"}


@app.get("/healthz")
async def health():
    """Unlimited - excluded from rate limiting"""
    return {"status": "healthy"}


# Run: uvicorn production_app:app --host 0.0.0.0 --port 8000
```

That's it! You're now using advanced rate limiting in your SAHOOL service! 🚀

هذا كل شيء! أنت الآن تستخدم حد معدل متقدم في خدمة سهول الخاصة بك! 🚀

---

**Need Help?** | **تحتاج مساعدة؟**

- Read the [README](README.md)
- Check [example_usage.py](example_usage.py)
- Review [test_rate_limiter.py](test_rate_limiter.py)
