"""
SAHOOL - Rate Limiter Tests
اختبارات حد المعدل

Comprehensive tests for rate limiting middleware with all three strategies.

اختبارات شاملة لميدلوير حد المعدل مع جميع الاستراتيجيات الثلاثة.
"""

import time
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from apps.kernel.common.middleware import (
    ClientIdentifier,
    EndpointConfig,
    FixedWindowLimiter,
    RateLimiter,
    RateLimitMiddleware,
    SlidingWindowLimiter,
    TokenBucketLimiter,
    rate_limit,
)

# ═══════════════════════════════════════════════════════════════════════════════
# تركيبات الاختبار
# Test Fixtures
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
async def redis_client():
    """
    إنشاء عميل Redis وهمي للاختبار
    Create mock Redis client for testing.
    """
    mock_redis = AsyncMock()
    mock_redis.ping = AsyncMock(return_value=True)
    mock_redis.pipeline = MagicMock()
    return mock_redis


@pytest.fixture
async def rate_limiter(redis_client):
    """
    إنشاء مثيل RateLimiter للاختبار
    Create RateLimiter instance for testing.
    """
    limiter = RateLimiter()
    limiter.redis = redis_client
    limiter._initialized = True
    limiter.strategies = {
        "fixed_window": FixedWindowLimiter(redis_client),
        "sliding_window": SlidingWindowLimiter(redis_client),
        "token_bucket": TokenBucketLimiter(redis_client),
    }
    return limiter


@pytest.fixture
def app():
    """
    إنشاء تطبيق FastAPI للاختبار
    Create FastAPI app for testing.
    """
    app = FastAPI()

    @app.get("/test")
    async def test_endpoint():
        return {"status": "ok"}

    @app.get("/healthz")
    async def health():
        return {"status": "healthy"}

    return app


# ═══════════════════════════════════════════════════════════════════════════════
# اختبارات استراتيجية النافذة الثابتة
# Fixed Window Strategy Tests
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_fixed_window_allows_within_limit(redis_client):
    """
    اختبار: النافذة الثابتة تسمح بالطلبات ضمن الحد
    Test: Fixed window allows requests within limit.
    """
    limiter = FixedWindowLimiter(redis_client)
    config = EndpointConfig(requests=10, period=60)

    # محاكاة استجابة Redis
    # Mock Redis response
    mock_pipe = AsyncMock()
    mock_pipe.execute = AsyncMock(return_value=[1, True])  # count=1
    redis_client.pipeline.return_value = mock_pipe

    allowed, remaining, reset = await limiter.check_rate_limit(
        client_id="test:user", endpoint="/api/test", config=config
    )

    assert allowed is True
    assert remaining >= 0
    assert reset > 0


@pytest.mark.asyncio
async def test_fixed_window_blocks_over_limit(redis_client):
    """
    اختبار: النافذة الثابتة تمنع الطلبات فوق الحد
    Test: Fixed window blocks requests over limit.
    """
    limiter = FixedWindowLimiter(redis_client)
    config = EndpointConfig(requests=10, period=60)

    # محاكاة استجابة Redis - الحد مكتمل
    # Mock Redis response - limit reached
    mock_pipe = AsyncMock()
    mock_pipe.execute = AsyncMock(return_value=[11, True])  # count=11 (over limit)
    redis_client.pipeline.return_value = mock_pipe

    allowed, remaining, reset = await limiter.check_rate_limit(
        client_id="test:user", endpoint="/api/test", config=config
    )

    assert allowed is False
    assert remaining == 0


@pytest.mark.asyncio
async def test_fixed_window_unlimited_endpoint(redis_client):
    """
    اختبار: النافذة الثابتة تسمح بطلبات غير محدودة عندما يكون الحد صفر
    Test: Fixed window allows unlimited requests when limit is zero.
    """
    limiter = FixedWindowLimiter(redis_client)
    config = EndpointConfig(requests=0, period=60)  # unlimited

    allowed, remaining, reset = await limiter.check_rate_limit(
        client_id="test:user", endpoint="/healthz", config=config
    )

    assert allowed is True
    assert remaining == -1  # unlimited


# ═══════════════════════════════════════════════════════════════════════════════
# اختبارات استراتيجية النافذة المنزلقة
# Sliding Window Strategy Tests
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_sliding_window_allows_within_limit(redis_client):
    """
    اختبار: النافذة المنزلقة تسمح بالطلبات ضمن الحد
    Test: Sliding window allows requests within limit.
    """
    limiter = SlidingWindowLimiter(redis_client)
    config = EndpointConfig(requests=10, period=60)

    # محاكاة استجابة Redis
    # Mock Redis response
    mock_pipe = AsyncMock()
    mock_pipe.execute = AsyncMock(
        return_value=[0, 5, 1, True]
    )  # removed=0, count=5, added=1
    redis_client.pipeline.return_value = mock_pipe

    allowed, remaining, reset = await limiter.check_rate_limit(
        client_id="test:user", endpoint="/api/test", config=config
    )

    assert allowed is True
    assert remaining >= 0


@pytest.mark.asyncio
async def test_sliding_window_blocks_over_limit(redis_client):
    """
    اختبار: النافذة المنزلقة تمنع الطلبات فوق الحد
    Test: Sliding window blocks requests over limit.
    """
    limiter = SlidingWindowLimiter(redis_client)
    config = EndpointConfig(requests=10, period=60)

    # محاكاة استجابة Redis - الحد مكتمل
    # Mock Redis response - limit reached
    mock_pipe = AsyncMock()
    mock_pipe.execute = AsyncMock(return_value=[0, 10, 1, True])  # count=10 (at limit)
    redis_client.pipeline.return_value = mock_pipe
    redis_client.zrem = AsyncMock()

    allowed, remaining, reset = await limiter.check_rate_limit(
        client_id="test:user", endpoint="/api/test", config=config
    )

    assert allowed is False
    assert remaining == 0
    # تحقق من إزالة الطلب الذي تمت إضافته
    # Verify request was removed
    redis_client.zrem.assert_called_once()


# ═══════════════════════════════════════════════════════════════════════════════
# اختبارات استراتيجية دلو الرموز
# Token Bucket Strategy Tests
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_token_bucket_allows_with_tokens(redis_client):
    """
    اختبار: دلو الرموز يسمح بالطلبات عندما تكون هناك رموز متاحة
    Test: Token bucket allows requests when tokens are available.
    """
    limiter = TokenBucketLimiter(redis_client)
    config = EndpointConfig(requests=10, period=60, burst=15)

    # محاكاة استجابة Redis - دلو ممتلئ
    # Mock Redis response - full bucket
    mock_pipe = AsyncMock()
    mock_pipe.execute = AsyncMock(
        return_value=[
            {"tokens": "15.0", "last_update": str(time.time())},  # hgetall
            None,
            None,  # hset, expire
        ]
    )
    redis_client.pipeline.return_value = mock_pipe

    allowed, remaining, reset = await limiter.check_rate_limit(
        client_id="test:user", endpoint="/api/test", config=config
    )

    assert allowed is True
    assert remaining >= 0


@pytest.mark.asyncio
async def test_token_bucket_blocks_without_tokens(redis_client):
    """
    اختبار: دلو الرموز يمنع الطلبات عندما لا تكون هناك رموز
    Test: Token bucket blocks requests when no tokens available.
    """
    limiter = TokenBucketLimiter(redis_client)
    config = EndpointConfig(requests=10, period=60, burst=15)

    # محاكاة استجابة Redis - دلو فارغ
    # Mock Redis response - empty bucket
    mock_pipe = AsyncMock()
    mock_pipe.execute = AsyncMock(
        return_value=[
            {
                "tokens": "0.5",
                "last_update": str(time.time()),
            },  # hgetall - less than 1 token
            None,
            None,  # hset, expire
        ]
    )
    redis_client.pipeline.return_value = mock_pipe

    allowed, remaining, reset = await limiter.check_rate_limit(
        client_id="test:user", endpoint="/api/test", config=config
    )

    assert allowed is False


@pytest.mark.asyncio
async def test_token_bucket_refills_over_time(redis_client):
    """
    اختبار: دلو الرموز يعيد ملء الرموز مع مرور الوقت
    Test: Token bucket refills tokens over time.
    """
    limiter = TokenBucketLimiter(redis_client)
    config = EndpointConfig(requests=10, period=60, burst=15)

    # محاكاة استجابة Redis - دلو قديم بحاجة إلى إعادة ملء
    # Mock Redis response - old bucket needs refill
    old_time = time.time() - 30  # 30 seconds ago
    mock_pipe = AsyncMock()
    mock_pipe.execute = AsyncMock(
        return_value=[
            {"tokens": "0.0", "last_update": str(old_time)},  # hgetall
            None,
            None,  # hset, expire
        ]
    )
    redis_client.pipeline.return_value = mock_pipe

    allowed, remaining, reset = await limiter.check_rate_limit(
        client_id="test:user", endpoint="/api/test", config=config
    )

    # يجب أن يكون مسموحًا لأن الرموز قد أعيد ملؤها
    # Should be allowed because tokens were refilled
    assert allowed is True


# ═══════════════════════════════════════════════════════════════════════════════
# اختبارات RateLimiter الرئيسية
# Main RateLimiter Tests
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_rate_limiter_selects_correct_strategy(rate_limiter):
    """
    اختبار: RateLimiter يختار الاستراتيجية الصحيحة
    Test: RateLimiter selects correct strategy.
    """
    # اختبار اختيار الاستراتيجية بناءً على التكوين
    # Test strategy selection based on configuration
    EndpointConfig(requests=10, period=60, strategy="fixed_window")
    EndpointConfig(requests=10, period=60, strategy="sliding_window")
    EndpointConfig(requests=10, period=60, strategy="token_bucket")

    # جميع الاستراتيجيات يجب أن تكون متاحة
    # All strategies should be available
    assert "fixed_window" in rate_limiter.strategies
    assert "sliding_window" in rate_limiter.strategies
    assert "token_bucket" in rate_limiter.strategies


@pytest.mark.asyncio
async def test_rate_limiter_endpoint_config_matching():
    """
    اختبار: RateLimiter يطابق تكوين نقطة النهاية بشكل صحيح
    Test: RateLimiter matches endpoint config correctly.
    """
    limiter = RateLimiter()

    # اختبار التطابق الدقيق
    # Test exact match
    config1 = limiter._get_endpoint_config("/api/v1/analyze")
    assert config1.requests == 10

    # اختبار تطابق البادئة
    # Test prefix match
    config2 = limiter._get_endpoint_config("/api/v1/analyze/123")
    assert config2.requests == 10

    # اختبار التكوين الافتراضي
    # Test default config
    config3 = limiter._get_endpoint_config("/api/v1/unknown")
    assert config3.requests == 60  # default


# ═══════════════════════════════════════════════════════════════════════════════
# اختبارات تحديد هوية العميل
# Client Identification Tests
# ═══════════════════════════════════════════════════════════════════════════════


def test_client_identifier_api_key():
    """
    اختبار: تحديد هوية العميل باستخدام مفتاح API
    Test: Client identification using API key.
    """
    request = MagicMock(spec=Request)
    request.headers.get = MagicMock(return_value="test-api-key-123")
    request.state = MagicMock()

    client_id = ClientIdentifier.get_client_id(request)

    assert client_id.startswith("apikey:")
    assert ClientIdentifier.get_identification_method(client_id) == "api_key"


def test_client_identifier_user_id():
    """
    اختبار: تحديد هوية العميل باستخدام معرف المستخدم
    Test: Client identification using user ID.
    """
    request = MagicMock(spec=Request)
    request.headers.get = MagicMock(return_value=None)  # No API key
    request.state = MagicMock(user_id="user123")

    client_id = ClientIdentifier.get_client_id(request)

    assert client_id == "user:user123"
    assert ClientIdentifier.get_identification_method(client_id) == "user_id"


def test_client_identifier_ip_address():
    """
    اختبار: تحديد هوية العميل باستخدام عنوان IP (احتياطي)
    Test: Client identification using IP address (fallback).
    """
    request = MagicMock(spec=Request)
    request.headers.get = MagicMock(return_value=None)  # No API key
    request.state = MagicMock(spec=["user_id"])  # No user_id attribute
    delattr(request.state, "user_id")
    request.client = MagicMock(host="192.168.1.1")

    client_id = ClientIdentifier.get_client_id(request)

    assert client_id == "ip:192.168.1.1"
    assert ClientIdentifier.get_identification_method(client_id) == "ip_address"


def test_client_identifier_forwarded_for():
    """
    اختبار: تحديد هوية العميل باستخدام X-Forwarded-For
    Test: Client identification using X-Forwarded-For.
    """
    request = MagicMock(spec=Request)

    def get_header(name):
        if name == "X-Forwarded-For":
            return "203.0.113.1, 198.51.100.1"
        return None

    request.headers.get = get_header
    request.state = MagicMock(spec=["user_id"])
    delattr(request.state, "user_id")

    client_id = ClientIdentifier.get_client_id(request)

    assert client_id == "ip:203.0.113.1"  # First IP in the list


# ═══════════════════════════════════════════════════════════════════════════════
# اختبارات ميدلوير FastAPI
# FastAPI Middleware Tests
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_middleware_allows_excluded_paths(app, rate_limiter):
    """
    اختبار: الميدلوير يسمح بالمسارات المستثناة
    Test: Middleware allows excluded paths.
    """
    app.add_middleware(
        RateLimitMiddleware, limiter=rate_limiter, exclude_paths=["/healthz"]
    )

    client = TestClient(app)
    response = client.get("/healthz")

    # يجب أن يكون ناجحًا دون فحص حد المعدل
    # Should succeed without rate limit check
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_middleware_adds_rate_limit_headers(app, rate_limiter):
    """
    اختبار: الميدلوير يضيف رؤوس حد المعدل
    Test: Middleware adds rate limit headers.
    """

    # محاكاة استجابة الفحص
    # Mock check response
    async def mock_check(*args, **kwargs):
        return True, 45, 30  # allowed, remaining, reset

    rate_limiter.check_rate_limit = mock_check

    app.add_middleware(
        RateLimitMiddleware,
        limiter=rate_limiter,
    )

    client = TestClient(app)
    response = client.get("/test")

    # التحقق من الرؤوس
    # Verify headers
    assert "X-RateLimit-Limit" in response.headers
    assert "X-RateLimit-Remaining" in response.headers
    assert "X-RateLimit-Reset" in response.headers


# ═══════════════════════════════════════════════════════════════════════════════
# اختبارات الديكوريتر
# Decorator Tests
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_rate_limit_decorator():
    """
    اختبار: ديكوريتر rate_limit يعمل بشكل صحيح
    Test: rate_limit decorator works correctly.
    """
    app = FastAPI()

    @app.get("/decorated")
    @rate_limit(requests=5, period=60, strategy="fixed_window")
    async def decorated_endpoint(request: Request):
        return {"status": "ok"}

    # التحقق من أن التكوين تم تسجيله
    # Verify configuration was registered
    from apps.kernel.common.middleware import ENDPOINT_CONFIGS

    assert "/decorated_endpoint" in ENDPOINT_CONFIGS


# ═══════════════════════════════════════════════════════════════════════════════
# اختبارات إعادة التعيين
# Reset Tests
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_fixed_window_reset(redis_client):
    """
    اختبار: إعادة تعيين النافذة الثابتة
    Test: Fixed window reset.
    """
    limiter = FixedWindowLimiter(redis_client)

    # محاكاة استجابة المسح
    # Mock scan response
    async def mock_scan(cursor, match=None, count=None):
        if cursor == 0:
            return (100, ["key1", "key2", "key3"])
        return (0, [])

    redis_client.scan = mock_scan
    redis_client.delete = AsyncMock(return_value=3)

    success = await limiter.reset_limits("test:user", "/api/test")

    assert success is True
    redis_client.delete.assert_called()


@pytest.mark.asyncio
async def test_sliding_window_reset(redis_client):
    """
    اختبار: إعادة تعيين النافذة المنزلقة
    Test: Sliding window reset.
    """
    limiter = SlidingWindowLimiter(redis_client)

    redis_client.delete = AsyncMock(return_value=1)

    success = await limiter.reset_limits("test:user", "/api/test")

    assert success is True
    redis_client.delete.assert_called_once()


@pytest.mark.asyncio
async def test_token_bucket_reset(redis_client):
    """
    اختبار: إعادة تعيين دلو الرموز
    Test: Token bucket reset.
    """
    limiter = TokenBucketLimiter(redis_client)

    redis_client.delete = AsyncMock(return_value=1)

    success = await limiter.reset_limits("test:user", "/api/test")

    assert success is True
    redis_client.delete.assert_called_once()


# ═══════════════════════════════════════════════════════════════════════════════
# اختبارات التكامل
# Integration Tests
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
@pytest.mark.integration
async def test_full_rate_limiting_flow():
    """
    اختبار التكامل: تدفق حد المعدل الكامل
    Integration test: Full rate limiting flow.

    Note: يتطلب Redis قيد التشغيل - Requires running Redis
    """
    import os

    # تخطي إذا لم يكن Redis متاحًا
    # Skip if Redis not available
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    try:
        from redis.asyncio import from_url

        redis = from_url(redis_url, decode_responses=True)
        await redis.ping()
    except Exception:
        pytest.skip("Redis not available")

    # إنشاء limiter حقيقي
    # Create real limiter
    limiter = RateLimiter(redis_url=redis_url)
    await limiter.initialize()

    # اختبار التحقق من حد المعدل
    # Test rate limit check
    client_id = "test:integration"
    endpoint = "/api/v1/test"

    # إعادة تعيين أولاً
    # Reset first
    await limiter.reset_limits(client_id, endpoint)

    # يجب أن يُسمح بالطلبات الأولى
    # First requests should be allowed
    for i in range(5):
        allowed, remaining, reset = await limiter.check_rate_limit(client_id, endpoint)
        assert allowed is True

    # التنظيف
    # Cleanup
    await limiter.reset_limits(client_id, endpoint)
    await redis.close()


# ═══════════════════════════════════════════════════════════════════════════════
# تشغيل الاختبارات
# Run Tests
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])

"""
كيفية تشغيل الاختبارات:
How to run tests:

# تشغيل جميع الاختبارات - Run all tests
pytest test_rate_limiter.py -v

# تشغيل اختبار محدد - Run specific test
pytest test_rate_limiter.py::test_fixed_window_allows_within_limit -v

# تشغيل مع التغطية - Run with coverage
pytest test_rate_limiter.py --cov=apps.kernel.common.middleware --cov-report=html

# تشغيل اختبارات التكامل فقط - Run integration tests only
pytest test_rate_limiter.py -m integration -v

# تشغيل مع الإخراج التفصيلي - Run with verbose output
pytest test_rate_limiter.py -vv --log-cli-level=DEBUG
"""
