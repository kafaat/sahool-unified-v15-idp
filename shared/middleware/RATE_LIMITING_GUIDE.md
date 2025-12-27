# دليل تحديد المعدل (Rate Limiting Guide)

## نظرة عامة

توفر منصة سهول نظام تحديد معدل متقدم مع الميزات التالية:

- ✅ **دعم Redis** - توزيع عدادات المعدل عبر عدة خوادم
- ✅ **احتياطي ذاكري** - يعمل بدون Redis في بيئة التطوير
- ✅ **مستويات متعددة** - Free, Standard, Premium, Internal
- ✅ **حماية من الاختراق** - Token Bucket + Sliding Window
- ✅ **سهل الاستخدام** - Decorators جاهزة للاستخدام
- ✅ **قابل للتخصيص** - إعدادات مرنة لكل endpoint

---

## المحتويات

1. [التثبيت](#التثبيت)
2. [الاستخدام الأساسي](#الاستخدام-الأساسي)
3. [الإعدادات](#الإعدادات)
4. [Decorators المتاحة](#decorators-المتاحة)
5. [أمثلة متقدمة](#أمثلة-متقدمة)
6. [استكشاف الأخطاء](#استكشاف-الأخطاء)

---

## التثبيت

### 1. تفعيل Redis (اختياري ولكن موصى به)

```bash
# في ملف .env
REDIS_URL=redis://:your_password@redis:6379/0
RATE_LIMIT_ENABLED=true
```

### 2. تكوين المستويات

```bash
# Free Tier
RATE_LIMIT_FREE_RPM=30
RATE_LIMIT_FREE_RPH=500
RATE_LIMIT_FREE_BURST=5

# Standard Tier
RATE_LIMIT_STANDARD_RPM=60
RATE_LIMIT_STANDARD_RPH=2000
RATE_LIMIT_STANDARD_BURST=10

# Premium Tier
RATE_LIMIT_PREMIUM_RPM=120
RATE_LIMIT_PREMIUM_RPH=5000
RATE_LIMIT_PREMIUM_BURST=20

# Internal Services
RATE_LIMIT_INTERNAL_RPM=1000
RATE_LIMIT_INTERNAL_RPH=50000
RATE_LIMIT_INTERNAL_BURST=100
```

---

## الاستخدام الأساسي

### 1. استخدام Middleware عام

```python
from fastapi import FastAPI
from shared.middleware import rate_limit_middleware

app = FastAPI()

# إضافة middleware لجميع المسارات
app.middleware("http")(rate_limit_middleware)
```

### 2. استخدام Middleware من shared.auth

```python
from fastapi import FastAPI
from shared.auth.middleware import RateLimitMiddleware

app = FastAPI()

# تخصيص الإعدادات
app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=100,
    requests_per_hour=2000,
    burst_limit=20,
    exclude_paths=["/health", "/docs"],
    redis_url="redis://localhost:6379/0"
)
```

---

## Decorators المتاحة

### 1. `@rate_limit()` - تحديد معدل مخصص

```python
from fastapi import FastAPI, Request
from shared.middleware import rate_limit

app = FastAPI()

@app.get("/expensive-endpoint")
@rate_limit(requests_per_minute=10, requests_per_hour=100, burst_limit=2)
async def expensive_endpoint(request: Request):
    """Endpoint مكلف يحتاج حماية إضافية"""
    return {"message": "This is an expensive operation"}
```

### 2. `@rate_limit_by_user()` - تحديد بناءً على المستخدم

```python
from shared.middleware import rate_limit_by_user

@app.get("/user-data")
@rate_limit_by_user(requests_per_minute=30, requests_per_hour=500)
async def get_user_data(request: Request):
    """يتطلب مصادقة - يحدد المعدل بناءً على user_id"""
    user = request.state.user
    return {"user_id": user.id, "data": "..."}
```

### 3. `@rate_limit_by_api_key()` - تحديد بناءً على API Key

```python
from shared.middleware import rate_limit_by_api_key

@app.get("/api/data")
@rate_limit_by_api_key(
    requests_per_minute=100,
    requests_per_hour=5000,
    header_name="X-API-Key"
)
async def api_endpoint(request: Request):
    """API endpoint - يحدد بناءً على API key"""
    return {"data": "API response"}
```

### 4. `@rate_limit_by_tenant()` - تحديد بناءً على Tenant

```python
from shared.middleware import rate_limit_by_tenant

@app.get("/tenant/data")
@rate_limit_by_tenant(requests_per_minute=200, requests_per_hour=10000)
async def tenant_endpoint(request: Request):
    """Multi-tenant endpoint"""
    tenant_id = request.state.tenant_id
    return {"tenant_id": tenant_id, "data": "..."}
```

---

## أمثلة متقدمة

### 1. Custom Key Function

```python
from shared.middleware import rate_limit

def custom_rate_limit_key(request: Request) -> str:
    """دالة مخصصة لاستخراج مفتاح التحديد"""
    # استخدام organization_id من header
    org_id = request.headers.get("X-Organization-ID", "default")
    return f"org:{org_id}"

@app.get("/org/data")
@rate_limit(
    requests_per_minute=50,
    key_func=custom_rate_limit_key
)
async def org_endpoint(request: Request):
    return {"data": "Organization data"}
```

### 2. مستويات متعددة لنفس التطبيق

```python
from fastapi import FastAPI, Request, HTTPException
from shared.middleware import RateLimitMiddleware
from shared.auth.middleware import JWTAuthMiddleware

app = FastAPI()

# 1. JWT Authentication
app.add_middleware(JWTAuthMiddleware)

# 2. Rate Limiting
app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=60,
    requests_per_hour=2000,
    burst_limit=10,
)

# Endpoints مع تحديدات مختلفة
@app.get("/public")
async def public_endpoint():
    """Endpoint عام - يستخدم الإعدادات الافتراضية"""
    return {"message": "Public data"}

@app.get("/premium-feature")
@rate_limit(requests_per_minute=200)
async def premium_feature(request: Request):
    """ميزة premium - حدود أعلى"""
    return {"message": "Premium feature"}

@app.get("/limited-resource")
@rate_limit(requests_per_minute=5, burst_limit=1)
async def limited_resource(request: Request):
    """مورد محدود جداً"""
    return {"message": "Limited resource"}
```

### 3. استخدام RateLimiter مباشرة

```python
from shared.middleware import RateLimiter, RateLimitConfig, TierConfig

# إنشاء rate limiter مخصص
custom_limiter = RateLimiter(
    tier_config=TierConfig(
        free=RateLimitConfig(requests_per_minute=10, burst_limit=2),
        premium=RateLimitConfig(requests_per_minute=100, burst_limit=20),
    )
)

@app.get("/custom-endpoint")
async def custom_endpoint(request: Request):
    # فحص يدوي
    allowed, headers = custom_limiter.check_rate_limit(request)

    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded",
            headers=headers
        )

    return {"message": "Success"}
```

### 4. معالجة Rate Limit Headers

```python
from fastapi import Response

@app.get("/monitored-endpoint")
@rate_limit(requests_per_minute=50)
async def monitored_endpoint(request: Request, response: Response):
    """Endpoint يعرض معلومات التحديد"""

    # Headers تضاف تلقائياً:
    # X-RateLimit-Limit: 50
    # X-RateLimit-Remaining: 45
    # X-RateLimit-Reset: 1234567890

    return {
        "message": "Check response headers for rate limit info",
        "headers": dict(response.headers)
    }
```

---

## الإعدادات

### Environment Variables

| المتغير | الوصف | القيمة الافتراضية |
|---------|--------|------------------|
| `RATE_LIMIT_ENABLED` | تفعيل/تعطيل التحديد | `true` |
| `REDIS_URL` | رابط Redis | - |
| `RATE_LIMIT_FREE_RPM` | طلبات Free/دقيقة | `30` |
| `RATE_LIMIT_FREE_RPH` | طلبات Free/ساعة | `500` |
| `RATE_LIMIT_FREE_BURST` | Burst limit Free | `5` |
| `RATE_LIMIT_STANDARD_RPM` | طلبات Standard/دقيقة | `60` |
| `RATE_LIMIT_STANDARD_RPH` | طلبات Standard/ساعة | `2000` |
| `RATE_LIMIT_STANDARD_BURST` | Burst limit Standard | `10` |
| `RATE_LIMIT_PREMIUM_RPM` | طلبات Premium/دقيقة | `120` |
| `RATE_LIMIT_PREMIUM_RPH` | طلبات Premium/ساعة | `5000` |
| `RATE_LIMIT_PREMIUM_BURST` | Burst limit Premium | `20` |
| `RATE_LIMIT_INTERNAL_RPM` | طلبات Internal/دقيقة | `1000` |
| `RATE_LIMIT_INTERNAL_RPH` | طلبات Internal/ساعة | `50000` |
| `RATE_LIMIT_INTERNAL_BURST` | Burst limit Internal | `100` |

### RateLimitConfig Options

```python
from shared.middleware import RateLimitConfig

config = RateLimitConfig(
    requests_per_minute=60,   # الحد الأقصى للطلبات في الدقيقة
    requests_per_hour=2000,    # الحد الأقصى للطلبات في الساعة
    burst_limit=10,            # حماية من الاختراق السريع
)
```

---

## Response Headers

عند تجاوز الحد:

```
HTTP/1.1 429 Too Many Requests
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1234567890
Retry-After: 60

{
  "error": "rate_limit_exceeded",
  "error_ar": "تم تجاوز حد الطلبات",
  "message": "Too many requests. Please try again later.",
  "message_ar": "طلبات كثيرة جداً. يرجى المحاولة لاحقاً.",
  "retry_after": 60
}
```

---

## استكشاف الأخطاء

### 1. Rate Limiting لا يعمل

```python
# تأكد من تفعيل rate limiting
import os
print(os.getenv("RATE_LIMIT_ENABLED"))  # يجب أن يكون "true"

# تأكد من إضافة middleware
from shared.auth.config import config
print(config.RATE_LIMIT_ENABLED)  # يجب أن يكون True
```

### 2. Redis غير متصل

```bash
# فحص اتصال Redis
redis-cli ping
# يجب أن يرجع: PONG

# فحص من Python
import redis
r = redis.from_url(os.getenv("REDIS_URL"))
print(r.ping())  # يجب أن يرجع: True
```

### 3. معرفة السبب في تجاوز الحد

```python
# تفعيل logging
import logging
logging.basicConfig(level=logging.DEBUG)

# سيظهر في logs:
# WARNING: Rate limit exceeded for user:123
# INFO: Rate limiter connected to Redis successfully
```

### 4. إعادة ضبط العدادات يدوياً (Redis)

```bash
# حذف جميع مفاتيح rate limiting
redis-cli --scan --pattern "ratelimit:*" | xargs redis-cli del

# حذف لمستخدم معين
redis-cli del "ratelimit:user:123:minute"
redis-cli del "ratelimit:user:123:hour"
redis-cli del "ratelimit:user:123:burst"
```

---

## الخوارزميات المستخدمة

### 1. Token Bucket (للحماية من Burst)

```
- كل مستخدم لديه bucket من tokens
- كل طلب يستهلك token واحد
- Tokens تُعاد ملئها بمعدل ثابت
- إذا لم يكن هناك tokens متاحة، الطلب يُرفض
```

### 2. Sliding Window (لتحديد الطلبات)

```
- تتبع طوابع زمنية لكل طلب
- حساب عدد الطلبات في آخر 60 ثانية/3600 ثانية
- إزالة الطلبات القديمة تلقائياً
- دقة عالية في التحديد
```

---

## Best Practices

### 1. استخدم Redis في Production

```python
# في بيئة production
REDIS_URL=redis://:password@redis-cluster:6379/0
RATE_LIMIT_ENABLED=true
```

### 2. حدود مناسبة للموارد

```python
# موارد مكلفة = حدود أقل
@rate_limit(requests_per_minute=5)
async def expensive_ai_processing():
    pass

# موارد خفيفة = حدود أعلى
@rate_limit(requests_per_minute=100)
async def get_cached_data():
    pass
```

### 3. مراقبة Rate Limiting

```python
# أضف metrics
from prometheus_client import Counter

rate_limit_exceeded_counter = Counter(
    'rate_limit_exceeded_total',
    'Total rate limit exceeded events',
    ['endpoint', 'tier']
)

# في middleware
if is_limited:
    rate_limit_exceeded_counter.labels(
        endpoint=request.url.path,
        tier=tier
    ).inc()
```

### 4. معالجة Errors بشكل صحيح

```python
from fastapi import Request, HTTPException

@app.exception_handler(HTTPException)
async def rate_limit_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == 429:
        return JSONResponse(
            status_code=429,
            content={
                "error": "rate_limit_exceeded",
                "error_ar": "تم تجاوز حد الطلبات",
                "message": "Too many requests",
                "message_ar": "طلبات كثيرة جداً",
                "retry_after": exc.headers.get("Retry-After", 60),
                "support": "contact@sahool.com"
            },
            headers=exc.headers
        )
    return exc
```

---

## أمثلة Integration

### مع FastAPI Dependency Injection

```python
from fastapi import Depends, Request
from shared.middleware import RateLimiter, RateLimitConfig

async def check_rate_limit(request: Request):
    """Dependency للتحقق من rate limit"""
    limiter = RateLimiter()
    allowed, headers = limiter.check_rate_limit(request)

    if not allowed:
        raise HTTPException(status_code=429, headers=headers)

    return True

@app.get("/protected")
async def protected_route(
    request: Request,
    _: bool = Depends(check_rate_limit)
):
    return {"message": "Protected data"}
```

### مع Background Tasks

```python
from fastapi import BackgroundTasks

@app.post("/process")
@rate_limit(requests_per_minute=10)
async def process_data(
    request: Request,
    background_tasks: BackgroundTasks
):
    """معالجة في الخلفية - rate limit على الطلب فقط"""

    def heavy_processing():
        # لا يؤثر على rate limiting
        import time
        time.sleep(10)

    background_tasks.add_task(heavy_processing)
    return {"status": "processing"}
```

---

## الخلاصة

نظام تحديد المعدل في سهول يوفر:

✅ حماية من الاستخدام المفرط والهجمات
✅ مرونة في التكوين لكل endpoint
✅ دعم موزع عبر Redis
✅ سهولة في الاستخدام عبر Decorators
✅ توافق مع بيئات مختلفة (development/production)

للمزيد من المعلومات، راجع:
- [shared/middleware/rate_limit.py](./rate_limit.py)
- [shared/auth/middleware.py](../auth/middleware.py)
- [.env.example](../../.env.example)

---

## الدعم

إذا واجهت أي مشاكل:
1. تحقق من [استكشاف الأخطاء](#استكشاف-الأخطاء)
2. راجع logs التطبيق
3. تأكد من تكوين Redis بشكل صحيح
4. تواصل مع فريق التطوير

**تم التحديث:** 2025-12-27
**الإصدار:** 1.0.0
