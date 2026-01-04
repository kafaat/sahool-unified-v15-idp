"""
SAHOOL - Rate Limiter Usage Examples
أمثلة استخدام حد المعدل

This file demonstrates how to use the advanced rate limiting middleware
in SAHOOL applications.

يوضح هذا الملف كيفية استخدام ميدلوير حد المعدل المتقدم
في تطبيقات SAHOOL.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from apps.kernel.common.middleware import (
    ENDPOINT_CONFIGS,
    EndpointConfig,
    get_rate_limit_stats,
    rate_limit,
    setup_rate_limiting,
)

# ═══════════════════════════════════════════════════════════════════════════════
# مثال 1: الإعداد الأساسي
# Example 1: Basic Setup
# ═══════════════════════════════════════════════════════════════════════════════

app = FastAPI(title="SAHOOL API with Rate Limiting")

# إعداد حد المعدل مع Redis
# Setup rate limiting with Redis
limiter = setup_rate_limiting(
    app,
    redis_url="redis://localhost:6379/0",
    exclude_paths=["/healthz", "/metrics", "/docs"],
)


# ═══════════════════════════════════════════════════════════════════════════════
# مثال 2: استخدام الديكوريتر لحد معدل مخصص
# Example 2: Using Decorator for Custom Rate Limit
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/api/v1/heavy-processing")
@rate_limit(requests=5, period=60, strategy="token_bucket", burst=2)
async def heavy_processing(request: Request):
    """
    نقطة نهاية للمعالجة الثقيلة مع حد معدل منخفض
    Heavy processing endpoint with low rate limit.

    Rate Limit: 5 requests/minute with 2 burst requests
    Strategy: Token Bucket (allows burst)
    """
    return {
        "status": "processing",
        "message": "تم بدء المعالجة الثقيلة - Heavy processing started"
    }


@app.get("/api/v1/quick-query")
@rate_limit(requests=100, period=60, strategy="fixed_window")
async def quick_query(request: Request):
    """
    نقطة نهاية للاستعلامات السريعة مع حد معدل عالي
    Quick query endpoint with high rate limit.

    Rate Limit: 100 requests/minute
    Strategy: Fixed Window (fast and simple)
    """
    return {
        "status": "success",
        "data": "نتيجة الاستعلام السريع - Quick query result"
    }


# ═══════════════════════════════════════════════════════════════════════════════
# مثال 3: تكوين مخصص لكل نقطة نهاية
# Example 3: Custom Endpoint Configuration
# ═══════════════════════════════════════════════════════════════════════════════

# إضافة تكوينات مخصصة إلى نقاط نهاية محددة
# Add custom configurations to specific endpoints
ENDPOINT_CONFIGS["/api/v1/satellite-analysis"] = EndpointConfig(
    requests=3,
    period=60,
    burst=1,
    strategy="sliding_window"
)

ENDPOINT_CONFIGS["/api/v1/crop-recommendations"] = EndpointConfig(
    requests=20,
    period=60,
    burst=5,
    strategy="token_bucket"
)


@app.get("/api/v1/satellite-analysis")
async def satellite_analysis(request: Request):
    """
    تحليل صور الأقمار الصناعية - معالجة ثقيلة جدًا
    Satellite image analysis - very heavy processing.

    Rate Limit: 3 requests/minute (configured in ENDPOINT_CONFIGS)
    Strategy: Sliding Window (accurate rate limiting)
    """
    return {
        "status": "analyzing",
        "message": "جاري تحليل صور الأقمار الصناعية - Analyzing satellite imagery"
    }


# ═══════════════════════════════════════════════════════════════════════════════
# مثال 4: الاستخدام اليدوي لحد المعدل
# Example 4: Manual Rate Limit Usage
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/v1/manual-check")
async def manual_rate_limit_check(request: Request):
    """
    مثال على التحقق اليدوي من حد المعدل
    Example of manual rate limit checking.
    """
    from apps.kernel.common.middleware import ClientIdentifier

    # الحصول على معرف العميل
    # Get client identifier
    client_id = ClientIdentifier.get_client_id(request)

    # التحقق من حد المعدل يدويًا
    # Check rate limit manually
    allowed, remaining, reset = await limiter.check_rate_limit(
        client_id=client_id,
        endpoint="/api/v1/manual-check"
    )

    if not allowed:
        return JSONResponse(
            status_code=429,
            content={
                "error": "rate_limit_exceeded",
                "message": "تم تجاوز حد المعدل - Rate limit exceeded",
                "retry_after": reset,
            },
            headers={
                "Retry-After": str(reset),
                "X-RateLimit-Remaining": "0",
            }
        )

    return {
        "status": "success",
        "rate_limit": {
            "remaining": remaining,
            "reset_in": reset,
        }
    }


# ═══════════════════════════════════════════════════════════════════════════════
# مثال 5: الحصول على إحصائيات حد المعدل
# Example 5: Get Rate Limit Statistics
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/api/v1/rate-limit-stats")
async def get_my_rate_limit_stats(request: Request):
    """
    الحصول على إحصائيات حد المعدل للعميل الحالي
    Get rate limit statistics for current client.
    """
    from apps.kernel.common.middleware import ClientIdentifier

    client_id = ClientIdentifier.get_client_id(request)
    stats = await get_rate_limit_stats(limiter, client_id)

    return {
        "status": "success",
        "stats": stats
    }


# ═══════════════════════════════════════════════════════════════════════════════
# مثال 6: إعادة تعيين حدود المعدل (للإدارة)
# Example 6: Reset Rate Limits (for administration)
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/v1/admin/reset-rate-limit")
async def reset_client_rate_limit(
    client_id: str,
    endpoint: str = None,
    # admin_token: str = Depends(verify_admin_token)  # يجب إضافة المصادقة - Should add authentication
):
    """
    إعادة تعيين حدود المعدل لعميل معين (للإداريين فقط)
    Reset rate limits for a specific client (admin only).

    Args:
        client_id: معرف العميل - Client identifier
        endpoint: نقطة نهاية محددة (اختياري) - Specific endpoint (optional)
    """
    success = await limiter.reset_limits(
        client_id=client_id,
        endpoint=endpoint
    )

    if success:
        return {
            "status": "success",
            "message": f"تم إعادة تعيين حدود المعدل - Rate limits reset for {client_id}"
        }
    else:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "فشل إعادة تعيين حدود المعدل - Failed to reset rate limits"
            }
        )


# ═══════════════════════════════════════════════════════════════════════════════
# مثال 7: تحديد هوية العميل المخصص
# Example 7: Custom Client Identification
# ═══════════════════════════════════════════════════════════════════════════════

def custom_client_identifier(request: Request) -> str:
    """
    دالة مخصصة لتحديد هوية العميل
    Custom function for client identification.

    يمكنك تخصيص كيفية تحديد العملاء بناءً على احتياجاتك
    You can customize how clients are identified based on your needs.
    """
    # مثال: استخدام معرف المنظمة من الرأس
    # Example: Use organization ID from header
    org_id = request.headers.get("X-Organization-ID")
    if org_id:
        return f"org:{org_id}"

    # الرجوع إلى الطريقة الافتراضية
    # Fallback to default method
    from apps.kernel.common.middleware import ClientIdentifier
    return ClientIdentifier.get_client_id(request)


# استخدام المعرف المخصص
# Use custom identifier
# limiter_custom = setup_rate_limiting(
#     app,
#     identifier_func=custom_client_identifier
# )


# ═══════════════════════════════════════════════════════════════════════════════
# مثال 8: نقاط نهاية محمية بمستويات مختلفة
# Example 8: Protected Endpoints with Different Levels
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/api/v1/analyze")
async def analyze_field(request: Request):
    """
    تحليل الحقل - 10 طلبات/دقيقة
    Field analysis - 10 req/min (configured in ENDPOINT_CONFIGS)
    """
    return {"status": "analyzing", "message": "جاري تحليل الحقل - Analyzing field"}


@app.get("/api/v1/field-health")
async def field_health(request: Request):
    """
    صحة الحقل - 30 طلب/دقيقة
    Field health - 30 req/min (configured in ENDPOINT_CONFIGS)
    """
    return {"status": "healthy", "message": "الحقل بصحة جيدة - Field is healthy"}


@app.get("/api/v1/weather")
async def weather_data(request: Request):
    """
    بيانات الطقس - 60 طلب/دقيقة
    Weather data - 60 req/min (configured in ENDPOINT_CONFIGS)
    """
    return {"temperature": 25, "humidity": 60, "message": "بيانات الطقس - Weather data"}


@app.get("/api/v1/sensors")
async def sensor_data(request: Request):
    """
    بيانات المستشعرات - 100 طلب/دقيقة
    Sensor data - 100 req/min (configured in ENDPOINT_CONFIGS)
    """
    return {"sensors": [], "message": "بيانات المستشعرات - Sensor data"}


@app.get("/healthz")
async def health_check():
    """
    فحص الصحة - غير محدود
    Health check - unlimited (excluded from rate limiting)
    """
    return {"status": "healthy"}


# ═══════════════════════════════════════════════════════════════════════════════
# مثال 9: معالجة أخطاء حد المعدل المخصصة
# Example 9: Custom Rate Limit Error Handling
# ═══════════════════════════════════════════════════════════════════════════════

@app.exception_handler(429)
async def rate_limit_handler(request: Request, exc):
    """
    معالج مخصص لأخطاء حد المعدل
    Custom handler for rate limit errors.
    """
    return JSONResponse(
        status_code=429,
        content={
            "error": "too_many_requests",
            "message_ar": "عدد كبير جدًا من الطلبات. يرجى المحاولة لاحقًا.",
            "message_en": "Too many requests. Please try again later.",
            "documentation": "https://docs.sahool.ai/api/rate-limits",
        },
        headers={
            "Retry-After": str(getattr(exc, "retry_after", 60)),
        }
    )


# ═══════════════════════════════════════════════════════════════════════════════
# مثال 10: اختبار استراتيجيات مختلفة
# Example 10: Testing Different Strategies
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/api/v1/test/fixed-window")
@rate_limit(requests=10, period=60, strategy="fixed_window")
async def test_fixed_window(request: Request):
    """اختبار استراتيجية النافذة الثابتة - Test Fixed Window Strategy"""
    return {"strategy": "fixed_window", "message": "Simple and fast"}


@app.get("/api/v1/test/sliding-window")
@rate_limit(requests=10, period=60, strategy="sliding_window")
async def test_sliding_window(request: Request):
    """اختبار استراتيجية النافذة المنزلقة - Test Sliding Window Strategy"""
    return {"strategy": "sliding_window", "message": "Accurate and fair"}


@app.get("/api/v1/test/token-bucket")
@rate_limit(requests=10, period=60, strategy="token_bucket", burst=5)
async def test_token_bucket(request: Request):
    """اختبار استراتيجية دلو الرموز - Test Token Bucket Strategy"""
    return {"strategy": "token_bucket", "message": "Smooth with burst support"}


# ═══════════════════════════════════════════════════════════════════════════════
# تشغيل التطبيق
# Run Application
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

"""
مثال على الاستخدام من سطر الأوامر:
Command line usage example:

# تشغيل التطبيق - Run the application
python example_usage.py

# اختبار نقطة نهاية - Test an endpoint
curl http://localhost:8000/api/v1/weather

# التحقق من الرؤوس - Check headers
curl -I http://localhost:8000/api/v1/weather

# اختبار حد المعدل - Test rate limit
for i in {1..70}; do curl http://localhost:8000/api/v1/weather; done

# الحصول على الإحصائيات - Get statistics
curl http://localhost:8000/api/v1/rate-limit-stats

# إعادة تعيين الحدود (للإدارة) - Reset limits (admin)
curl -X POST "http://localhost:8000/api/v1/admin/reset-rate-limit?client_id=ip:127.0.0.1"

===================================
استراتيجيات حد المعدل المتاحة:
Available Rate Limit Strategies:
===================================

1. Fixed Window (النافذة الثابتة):
   - الأسرع والأبسط - Fastest and simplest
   - مناسب للحدود العالية - Good for high limits
   - يمكن أن يسمح بضعف الطلبات عند حدود النافذة
   - Can allow 2x requests at window boundaries

2. Sliding Window (النافذة المنزلقة):
   - الأكثر دقة - Most accurate
   - عادل لجميع المستخدمين - Fair for all users
   - استخدام أعلى للذاكرة - Higher memory usage
   - الأفضل للحدود المتوسطة - Best for medium limits

3. Token Bucket (دلو الرموز):
   - يسمح بالطلبات المتتالية - Allows burst requests
   - سلس ومرن - Smooth and flexible
   - الأفضل للحدود المنخفضة مع الطلبات المتتالية
   - Best for low limits with burst support

===================================
تعريف العميل:
Client Identification:
===================================

الأولوية (Priority):
1. API Key (من الرأس X-API-Key) - From X-API-Key header
2. User ID (من المصادقة) - From authentication
3. IP Address (احتياطي) - Fallback

===================================
رؤوس HTTP:
HTTP Headers:
===================================

Response Headers:
- X-RateLimit-Limit: الحد الأقصى للطلبات - Maximum requests
- X-RateLimit-Remaining: الطلبات المتبقية - Remaining requests
- X-RateLimit-Reset: الوقت حتى إعادة التعيين (ثواني) - Time to reset (seconds)
- X-RateLimit-Client-ID: معرف العميل - Client identifier
- Retry-After: وقت إعادة المحاولة (عند التجاوز) - Retry time (when exceeded)

Request Headers:
- X-API-Key: مفتاح API للتعريف - API key for identification
- X-Forwarded-For: عنوان IP الحقيقي - Real IP address
- X-Organization-ID: معرف المنظمة (مخصص) - Organization ID (custom)
"""
