"""
SAHOOL Kernel - Advanced API Rate Limiting Middleware
ميدلوير التحكم المتقدم في معدل طلبات API

Provides multiple rate limiting strategies with Redis-backed distributed storage:
- FixedWindowLimiter: Simple time window counter
- SlidingWindowLimiter: Accurate sliding window algorithm
- TokenBucketLimiter: Smooth rate limiting with burst handling

Features:
- Per-endpoint rate limit configuration
- Multiple client identification methods (API Key, IP, User ID)
- Distributed rate limiting with Redis
- FastAPI middleware integration
- Decorator pattern for custom endpoints
- Standard rate limit headers (X-RateLimit-*)

Version: 2.0.0
Created: 2026
"""

import hashlib
import logging
import os
import time
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from functools import wraps
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# تكوين حدود المعدل لكل نقطة نهاية
# Endpoint Rate Limit Configuration
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class EndpointConfig:
    """
    تكوين حد المعدل لنقطة نهاية واحدة
    Rate limit configuration for a single endpoint.

    Attributes:
        requests: عدد الطلبات المسموح بها - Number of allowed requests
        period: فترة الحد بالثواني - Limit period in seconds
        burst: الحد الأقصى للطلبات المتتالية - Maximum burst requests
        strategy: استراتيجية الحد - Limiting strategy to use
    """
    requests: int
    period: int  # بالثواني - in seconds
    burst: int | None = None
    strategy: str = "sliding_window"  # fixed_window, sliding_window, token_bucket


# تكوينات افتراضية لنقاط النهاية المختلفة
# Default configurations for different endpoints
ENDPOINT_CONFIGS: dict[str, EndpointConfig] = {
    "/api/v1/analyze": EndpointConfig(
        requests=10,
        period=60,  # 10 طلبات/دقيقة للمعالجة الثقيلة - 10 req/min for heavy processing
        burst=2,
        strategy="token_bucket"
    ),
    "/api/v1/field-health": EndpointConfig(
        requests=30,
        period=60,  # 30 طلب/دقيقة - 30 req/min
        burst=5,
        strategy="sliding_window"
    ),
    "/api/v1/weather": EndpointConfig(
        requests=60,
        period=60,  # 60 طلب/دقيقة - 60 req/min
        burst=10,
        strategy="sliding_window"
    ),
    "/api/v1/sensors": EndpointConfig(
        requests=100,
        period=60,  # 100 طلب/دقيقة - 100 req/min
        burst=20,
        strategy="fixed_window"
    ),
    "/healthz": EndpointConfig(
        requests=0,  # غير محدود - unlimited
        period=0,
        strategy="fixed_window"
    ),
}


# ═══════════════════════════════════════════════════════════════════════════════
# واجهة استراتيجية حد المعدل الأساسية
# Base Rate Limit Strategy Interface
# ═══════════════════════════════════════════════════════════════════════════════


class RateLimitStrategy(ABC):
    """
    واجهة أساسية لاستراتيجيات حد المعدل المختلفة
    Base interface for different rate limiting strategies.
    """

    def __init__(self, redis_client=None):
        """
        تهيئة الاستراتيجية
        Initialize the strategy.

        Args:
            redis_client: عميل Redis للتخزين الموزع - Redis client for distributed storage
        """
        self.redis = redis_client

    @abstractmethod
    async def check_rate_limit(
        self,
        client_id: str,
        endpoint: str,
        config: EndpointConfig
    ) -> tuple[bool, int, int]:
        """
        التحقق من حد المعدل
        Check if request is within rate limits.

        Args:
            client_id: معرف العميل - Client identifier
            endpoint: نقطة النهاية - API endpoint
            config: تكوين حد المعدل - Rate limit configuration

        Returns:
            Tuple: (allowed, remaining_requests, reset_time_seconds)
        """
        pass

    @abstractmethod
    async def reset_limits(self, client_id: str, endpoint: str) -> bool:
        """
        إعادة تعيين حدود المعدل للعميل
        Reset rate limits for a client.

        Args:
            client_id: معرف العميل - Client identifier
            endpoint: نقطة النهاية - API endpoint

        Returns:
            bool: True if reset successful
        """
        pass


# ═══════════════════════════════════════════════════════════════════════════════
# استراتيجية النافذة الثابتة
# Fixed Window Strategy
# ═══════════════════════════════════════════════════════════════════════════════


class FixedWindowLimiter(RateLimitStrategy):
    """
    استراتيجية النافذة الثابتة - بسيطة وسريعة
    Fixed Window Strategy - Simple and fast.

    يقسم الوقت إلى نوافذ ثابتة ويحسب الطلبات في كل نافذة
    Divides time into fixed windows and counts requests per window.

    مزايا: بسيط، استخدام منخفض للذاكرة
    Pros: Simple, low memory usage

    عيوب: يمكن أن يسمح بضعف الطلبات عند حدود النافذة
    Cons: Can allow 2x requests at window boundaries
    """

    async def check_rate_limit(
        self,
        client_id: str,
        endpoint: str,
        config: EndpointConfig
    ) -> tuple[bool, int, int]:
        """التحقق من حد المعدل باستخدام نافذة ثابتة"""
        # إذا كان الحد صفر، السماح بجميع الطلبات
        # If limit is zero, allow all requests
        if config.requests == 0:
            return True, -1, 0

        now = time.time()
        # حساب بداية النافذة الحالية
        # Calculate current window start
        window_start = int(now / config.period) * config.period
        window_key = f"ratelimit:fixed:{client_id}:{endpoint}:{window_start}"

        if not self.redis:
            # الرجوع إلى الذاكرة إذا لم يكن Redis متاحًا
            # Fallback to in-memory if Redis not available
            return True, config.requests, config.period

        try:
            # زيادة العداد بشكل ذري
            # Increment counter atomically
            pipe = self.redis.pipeline()
            pipe.incr(window_key)
            pipe.expire(window_key, config.period * 2)  # احتفظ بنافذتين - Keep 2 windows
            results = await pipe.execute()

            current_count = results[0]
            remaining = max(0, config.requests - current_count)
            reset_time = int(window_start + config.period - now)

            # التحقق مما إذا كان الحد قد تم تجاوزه
            # Check if limit exceeded
            allowed = current_count <= config.requests

            if not allowed:
                logger.warning(
                    f"حد المعدل تم تجاوزه - Rate limit exceeded: "
                    f"client={client_id}, endpoint={endpoint}, "
                    f"count={current_count}/{config.requests}"
                )

            return allowed, remaining, reset_time

        except Exception as e:
            logger.error(f"خطأ في التحقق من حد المعدل - Rate limit check error: {e}")
            # السماح بالطلب عند الفشل - Allow request on failure
            return True, config.requests, config.period

    async def reset_limits(self, client_id: str, endpoint: str) -> bool:
        """إعادة تعيين حدود المعدل"""
        if not self.redis:
            return False

        try:
            # حذف جميع مفاتيح النوافذ لهذا العميل والنقطة النهائية
            # Delete all window keys for this client and endpoint
            pattern = f"ratelimit:fixed:{client_id}:{endpoint}:*"
            cursor = 0
            deleted = 0

            while True:
                cursor, keys = await self.redis.scan(cursor, match=pattern, count=100)
                if keys:
                    deleted += await self.redis.delete(*keys)
                if cursor == 0:
                    break

            logger.info(
                f"إعادة تعيين حدود المعدل - Rate limits reset: "
                f"client={client_id}, endpoint={endpoint}, keys_deleted={deleted}"
            )
            return True

        except Exception as e:
            logger.error(f"خطأ في إعادة تعيين الحدود - Reset error: {e}")
            return False


# ═══════════════════════════════════════════════════════════════════════════════
# استراتيجية النافذة المنزلقة
# Sliding Window Strategy
# ═══════════════════════════════════════════════════════════════════════════════


class SlidingWindowLimiter(RateLimitStrategy):
    """
    استراتيجية النافذة المنزلقة - دقيقة وعادلة
    Sliding Window Strategy - Accurate and fair.

    تستخدم مجموعات Redis المرتبة لتتبع جميع الطلبات مع الطوابع الزمنية
    Uses Redis sorted sets to track all requests with timestamps.

    مزايا: دقيق جدًا، عادل، لا توجد مشاكل في حدود النوافذ
    Pros: Very accurate, fair, no window boundary issues

    عيوب: استخدام أعلى للذاكرة، أداء أبطأ قليلاً
    Cons: Higher memory usage, slightly slower
    """

    async def check_rate_limit(
        self,
        client_id: str,
        endpoint: str,
        config: EndpointConfig
    ) -> tuple[bool, int, int]:
        """التحقق من حد المعدل باستخدام نافذة منزلقة"""
        # إذا كان الحد صفر، السماح بجميع الطلبات
        if config.requests == 0:
            return True, -1, 0

        now = time.time()
        window_start = now - config.period
        key = f"ratelimit:sliding:{client_id}:{endpoint}"

        if not self.redis:
            return True, config.requests, config.period

        try:
            pipe = self.redis.pipeline()

            # إزالة الطلبات القديمة خارج النافذة
            # Remove old requests outside the window
            pipe.zremrangebyscore(key, 0, window_start)

            # حساب الطلبات الحالية في النافذة
            # Count current requests in window
            pipe.zcard(key)

            # إضافة الطلب الحالي
            # Add current request
            request_id = f"{now}:{hashlib.md5(str(now).encode()).hexdigest()[:8]}"
            pipe.zadd(key, {request_id: now})

            # تعيين انتهاء الصلاحية
            # Set expiry
            pipe.expire(key, config.period * 2)

            results = await pipe.execute()
            current_count = results[1]

            remaining = max(0, config.requests - current_count - 1)
            reset_time = config.period

            # التحقق مما إذا كان الحد قد تم تجاوزه
            allowed = current_count < config.requests

            if not allowed:
                # إزالة الطلب الذي أضفناه للتو
                # Remove the request we just added
                await self.redis.zrem(key, request_id)
                logger.warning(
                    f"حد المعدل تم تجاوزه - Rate limit exceeded: "
                    f"client={client_id}, endpoint={endpoint}, "
                    f"count={current_count}/{config.requests}"
                )

            return allowed, remaining, reset_time

        except Exception as e:
            logger.error(f"خطأ في التحقق من حد المعدل - Rate limit check error: {e}")
            return True, config.requests, config.period

    async def reset_limits(self, client_id: str, endpoint: str) -> bool:
        """إعادة تعيين حدود المعدل"""
        if not self.redis:
            return False

        try:
            key = f"ratelimit:sliding:{client_id}:{endpoint}"
            deleted = await self.redis.delete(key)

            logger.info(
                f"إعادة تعيين حدود المعدل - Rate limits reset: "
                f"client={client_id}, endpoint={endpoint}, deleted={deleted}"
            )
            return True

        except Exception as e:
            logger.error(f"خطأ في إعادة تعيين الحدود - Reset error: {e}")
            return False


# ═══════════════════════════════════════════════════════════════════════════════
# استراتيجية دلو الرموز
# Token Bucket Strategy
# ═══════════════════════════════════════════════════════════════════════════════


class TokenBucketLimiter(RateLimitStrategy):
    """
    استراتيجية دلو الرموز - سلس ومرن
    Token Bucket Strategy - Smooth and flexible.

    يملأ الدلو بالرموز بمعدل ثابت، يستهلك كل طلب رمزًا واحدًا
    Fills bucket with tokens at a constant rate, each request consumes one token.

    مزايا: يسمح بالطلبات المتتالية، سلس، مرن
    Pros: Allows burst requests, smooth, flexible

    عيوب: أكثر تعقيدًا في التنفيذ
    Cons: More complex to implement
    """

    async def check_rate_limit(
        self,
        client_id: str,
        endpoint: str,
        config: EndpointConfig
    ) -> tuple[bool, int, int]:
        """التحقق من حد المعدل باستخدام دلو الرموز"""
        # إذا كان الحد صفر، السماح بجميع الطلبات
        if config.requests == 0:
            return True, -1, 0

        now = time.time()
        key = f"ratelimit:bucket:{client_id}:{endpoint}"

        # حساب معدل ملء الرموز (رموز في الثانية)
        # Calculate token refill rate (tokens per second)
        refill_rate = config.requests / config.period

        # الحد الأقصى للرموز (سعة الدلو)
        # Maximum tokens (bucket capacity)
        max_tokens = config.burst or config.requests

        if not self.redis:
            return True, config.requests, config.period

        try:
            # الحصول على حالة الدلو الحالية
            # Get current bucket state
            pipe = self.redis.pipeline()
            pipe.hgetall(key)
            results = await pipe.execute()
            bucket = results[0] or {}

            # استخراج القيم الحالية
            # Extract current values
            last_update = float(bucket.get('last_update', now))
            tokens = float(bucket.get('tokens', max_tokens))

            # حساب الرموز الجديدة المضافة منذ آخر تحديث
            # Calculate new tokens added since last update
            time_passed = now - last_update
            new_tokens = time_passed * refill_rate
            tokens = min(max_tokens, tokens + new_tokens)

            # التحقق مما إذا كان لدينا رمز متاح
            # Check if we have a token available
            allowed = tokens >= 1.0

            if allowed:
                # استهلاك رمز واحد
                # Consume one token
                tokens -= 1.0
            else:
                logger.warning(
                    f"حد المعدل تم تجاوزه - Rate limit exceeded: "
                    f"client={client_id}, endpoint={endpoint}, "
                    f"tokens={tokens:.2f}/{max_tokens}"
                )

            # تحديث حالة الدلو
            # Update bucket state
            pipe = self.redis.pipeline()
            pipe.hset(key, mapping={
                'tokens': str(tokens),
                'last_update': str(now)
            })
            pipe.expire(key, config.period * 2)
            await pipe.execute()

            # حساب وقت إعادة التعيين (الوقت حتى يصبح لدينا رمز واحد)
            # Calculate reset time (time until we have one token)
            reset_time = int((1.0 - tokens) / refill_rate) + 1 if tokens < 1.0 else 0

            remaining = int(tokens)

            return allowed, remaining, reset_time

        except Exception as e:
            logger.error(f"خطأ في التحقق من حد المعدل - Rate limit check error: {e}")
            return True, config.requests, config.period

    async def reset_limits(self, client_id: str, endpoint: str) -> bool:
        """إعادة تعيين حدود المعدل"""
        if not self.redis:
            return False

        try:
            key = f"ratelimit:bucket:{client_id}:{endpoint}"
            deleted = await self.redis.delete(key)

            logger.info(
                f"إعادة تعيين حدود المعدل - Rate limits reset: "
                f"client={client_id}, endpoint={endpoint}, deleted={deleted}"
            )
            return True

        except Exception as e:
            logger.error(f"خطأ في إعادة تعيين الحدود - Reset error: {e}")
            return False


# ═══════════════════════════════════════════════════════════════════════════════
# مدير حد المعدل الرئيسي
# Main Rate Limiter Manager
# ═══════════════════════════════════════════════════════════════════════════════


class RateLimiter:
    """
    مدير حد المعدل الرئيسي مع دعم لاستراتيجيات متعددة
    Main rate limiter manager with support for multiple strategies.

    Usage:
        limiter = RateLimiter()
        await limiter.initialize()

        allowed, remaining, reset = await limiter.check_rate_limit(
            client_id="user:123",
            endpoint="/api/v1/weather"
        )
    """

    def __init__(self, redis_url: str | None = None):
        """
        تهيئة مدير حد المعدل
        Initialize rate limiter manager.

        Args:
            redis_url: عنوان URL لـ Redis - Redis connection URL
        """
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.redis = None
        self._initialized = False

        # تهيئة الاستراتيجيات
        # Initialize strategies
        self.strategies: dict[str, RateLimitStrategy] = {}

    async def initialize(self):
        """
        تهيئة اتصال Redis والاستراتيجيات
        Initialize Redis connection and strategies.
        """
        if self._initialized:
            return

        try:
            from redis.asyncio import from_url as redis_from_url

            self.redis = redis_from_url(
                self.redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
            )

            # اختبار الاتصال
            # Test connection
            await self.redis.ping()
            logger.info(f"✓ Redis متصل للحد من المعدل - Redis connected for rate limiting: {self.redis_url}")

        except Exception as e:
            logger.warning(
                f"⚠ Redis غير متاح، حد المعدل معطل - "
                f"Redis not available, rate limiting disabled: {e}"
            )
            self.redis = None

        # إنشاء مثيلات الاستراتيجيات
        # Create strategy instances
        self.strategies = {
            "fixed_window": FixedWindowLimiter(self.redis),
            "sliding_window": SlidingWindowLimiter(self.redis),
            "token_bucket": TokenBucketLimiter(self.redis),
        }

        self._initialized = True

    def _get_endpoint_config(self, endpoint: str) -> EndpointConfig:
        """
        الحصول على تكوين نقطة النهاية
        Get endpoint configuration.

        Args:
            endpoint: مسار نقطة النهاية - Endpoint path

        Returns:
            تكوين نقطة النهاية - Endpoint configuration
        """
        # البحث عن تطابق دقيق
        # Look for exact match
        if endpoint in ENDPOINT_CONFIGS:
            return ENDPOINT_CONFIGS[endpoint]

        # البحث عن تطابق البادئة
        # Look for prefix match
        for pattern, config in ENDPOINT_CONFIGS.items():
            if endpoint.startswith(pattern):
                return config

        # تكوين افتراضي: 60 طلب/دقيقة
        # Default config: 60 req/min
        return EndpointConfig(
            requests=60,
            period=60,
            burst=10,
            strategy="sliding_window"
        )

    async def check_rate_limit(
        self,
        client_id: str,
        endpoint: str,
    ) -> tuple[bool, int, int]:
        """
        التحقق من حد المعدل لعميل ونقطة نهاية
        Check rate limit for a client and endpoint.

        Args:
            client_id: معرف العميل - Client identifier
            endpoint: نقطة النهاية - API endpoint

        Returns:
            Tuple: (allowed, remaining_requests, reset_time_seconds)
        """
        if not self._initialized:
            await self.initialize()

        # الحصول على تكوين نقطة النهاية
        # Get endpoint configuration
        config = self._get_endpoint_config(endpoint)

        # إذا كان الحد صفر، السماح بجميع الطلبات
        # If limit is zero, allow all requests
        if config.requests == 0:
            return True, -1, 0

        # الحصول على الاستراتيجية
        # Get strategy
        strategy = self.strategies.get(
            config.strategy,
            self.strategies["sliding_window"]
        )

        return await strategy.check_rate_limit(client_id, endpoint, config)

    async def get_remaining_requests(
        self,
        client_id: str,
        endpoint: str,
    ) -> int:
        """
        الحصول على عدد الطلبات المتبقية
        Get remaining requests for a client and endpoint.

        Args:
            client_id: معرف العميل - Client identifier
            endpoint: نقطة النهاية - API endpoint

        Returns:
            عدد الطلبات المتبقية - Number of remaining requests
        """
        allowed, remaining, reset = await self.check_rate_limit(client_id, endpoint)
        # إذا تم رفض الطلب، إضافة واحد مرة أخرى لأننا لم نستهلكه فعليًا
        # If request was denied, add one back since we didn't actually consume it
        if not allowed:
            remaining = 0
        return remaining

    async def reset_limits(self, client_id: str, endpoint: str | None = None) -> bool:
        """
        إعادة تعيين حدود المعدل لعميل
        Reset rate limits for a client.

        Args:
            client_id: معرف العميل - Client identifier
            endpoint: نقطة نهاية محددة (اختياري) - Specific endpoint (optional)

        Returns:
            bool: True if reset successful
        """
        if not self._initialized:
            await self.initialize()

        if endpoint:
            # إعادة تعيين نقطة نهاية محددة
            # Reset specific endpoint
            config = self._get_endpoint_config(endpoint)
            strategy = self.strategies.get(
                config.strategy,
                self.strategies["sliding_window"]
            )
            return await strategy.reset_limits(client_id, endpoint)
        else:
            # إعادة تعيين جميع النقاط النهائية
            # Reset all endpoints
            success = True
            for _strategy_name, strategy in self.strategies.items():
                try:
                    # إعادة تعيين جميع المفاتيح لهذا العميل
                    # Reset all keys for this client
                    if self.redis:
                        pattern = f"ratelimit:*:{client_id}:*"
                        cursor = 0
                        while True:
                            cursor, keys = await self.redis.scan(cursor, match=pattern, count=100)
                            if keys:
                                await self.redis.delete(*keys)
                            if cursor == 0:
                                break
                except Exception as e:
                    logger.error(f"خطأ في إعادة التعيين - Reset error: {e}")
                    success = False

            logger.info(
                f"إعادة تعيين جميع حدود المعدل - All rate limits reset: "
                f"client={client_id}"
            )
            return success


# ═══════════════════════════════════════════════════════════════════════════════
# تعريف العميل
# Client Identification
# ═══════════════════════════════════════════════════════════════════════════════


class ClientIdentifier:
    """
    تحديد هوية العميل من الطلب
    Identify client from request using multiple methods.

    الأولوية: مفتاح API > معرف المستخدم > عنوان IP
    Priority: API Key > User ID > IP Address
    """

    @staticmethod
    def get_client_id(request: Request) -> str:
        """
        استخراج معرف العميل من الطلب
        Extract client identifier from request.

        Args:
            request: طلب FastAPI - FastAPI request

        Returns:
            معرف العميل - Client identifier
        """
        # 1. محاولة الحصول على مفتاح API من الرأس
        # 1. Try to get API key from header
        api_key = request.headers.get("X-API-Key")
        if api_key:
            # تجزئة مفتاح API للأمان
            # Hash API key for security
            api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()[:16]
            return f"apikey:{api_key_hash}"

        # 2. محاولة الحصول على معرف المستخدم من المصادقة
        # 2. Try to get user ID from authentication
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            return f"user:{user_id}"

        # 3. الرجوع إلى عنوان IP
        # 3. Fallback to IP address
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            ip = forwarded.split(",")[0].strip()
        else:
            ip = request.client.host if request.client else "unknown"

        return f"ip:{ip}"

    @staticmethod
    def get_identification_method(client_id: str) -> str:
        """
        الحصول على طريقة التعريف المستخدمة
        Get identification method used.

        Args:
            client_id: معرف العميل - Client identifier

        Returns:
            طريقة التعريف - Identification method
        """
        if client_id.startswith("apikey:"):
            return "api_key"
        elif client_id.startswith("user:"):
            return "user_id"
        else:
            return "ip_address"


# ═══════════════════════════════════════════════════════════════════════════════
# ميدلوير FastAPI
# FastAPI Middleware
# ═══════════════════════════════════════════════════════════════════════════════


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    ميدلوير FastAPI للحد من المعدل التلقائي
    FastAPI middleware for automatic rate limiting.

    Usage:
        app = FastAPI()
        limiter = RateLimiter()
        app.add_middleware(
            RateLimitMiddleware,
            limiter=limiter,
            exclude_paths=["/healthz", "/metrics"]
        )
    """

    def __init__(
        self,
        app,
        limiter: RateLimiter,
        exclude_paths: list[str] | None = None,
        identifier_func: Callable[[Request], str] | None = None,
    ):
        """
        تهيئة الميدلوير
        Initialize middleware.

        Args:
            app: تطبيق FastAPI - FastAPI application
            limiter: مثيل RateLimiter - RateLimiter instance
            exclude_paths: مسارات مستثناة - Paths to exclude
            identifier_func: دالة مخصصة لتحديد هوية العميل - Custom client identification function
        """
        super().__init__(app)
        self.limiter = limiter
        self.exclude_paths = exclude_paths or ["/healthz", "/readyz", "/livez", "/metrics", "/docs", "/openapi.json"]
        self.identifier_func = identifier_func or ClientIdentifier.get_client_id

    async def dispatch(self, request: Request, call_next):
        """
        معالجة الطلب من خلال حد المعدل
        Process request through rate limiter.
        """
        # تخطي المسارات المستثناة
        # Skip excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)

        # الحصول على معرف العميل
        # Get client identifier
        client_id = self.identifier_func(request)
        endpoint = request.url.path

        # التحقق من حد المعدل
        # Check rate limit
        allowed, remaining, reset = await self.limiter.check_rate_limit(
            client_id=client_id,
            endpoint=endpoint
        )

        # إعداد رؤوس حد المعدل
        # Prepare rate limit headers
        headers = {
            "X-RateLimit-Limit": str(self.limiter._get_endpoint_config(endpoint).requests),
            "X-RateLimit-Remaining": str(max(0, remaining)),
            "X-RateLimit-Reset": str(reset),
            "X-RateLimit-Client-ID": client_id,
        }

        # إذا تم تجاوز الحد، إرجاع خطأ 429
        # If limit exceeded, return 429 error
        if not allowed:
            headers["Retry-After"] = str(reset)
            return JSONResponse(
                status_code=429,
                content={
                    "error": "rate_limit_exceeded",
                    "message": "تم تجاوز حد المعدل. يرجى المحاولة لاحقًا - Rate limit exceeded. Please try again later.",
                    "retry_after": reset,
                    "limit": self.limiter._get_endpoint_config(endpoint).requests,
                    "period": self.limiter._get_endpoint_config(endpoint).period,
                },
                headers=headers,
            )

        # معالجة الطلب وإضافة رؤوس حد المعدل
        # Process request and add rate limit headers
        response = await call_next(request)

        for header, value in headers.items():
            response.headers[header] = value

        return response


# ═══════════════════════════════════════════════════════════════════════════════
# ديكوريتر حد المعدل
# Rate Limit Decorator
# ═══════════════════════════════════════════════════════════════════════════════


def rate_limit(
    requests: int,
    period: int,
    strategy: str = "sliding_window",
    burst: int | None = None,
):
    """
    ديكوريتر لتطبيق حد معدل مخصص على نقطة نهاية
    Decorator to apply custom rate limit to an endpoint.

    Usage:
        @app.get("/api/v1/custom")
        @rate_limit(requests=10, period=60, strategy="token_bucket")
        async def custom_endpoint(request: Request):
            return {"status": "ok"}

    Args:
        requests: عدد الطلبات المسموح بها - Number of allowed requests
        period: الفترة بالثواني - Period in seconds
        strategy: استراتيجية الحد - Limiting strategy
        burst: الحد الأقصى للطلبات المتتالية - Maximum burst requests
    """
    def decorator(func: Callable):
        # تسجيل التكوين المخصص
        # Register custom configuration
        endpoint_path = f"/{func.__name__}"
        ENDPOINT_CONFIGS[endpoint_path] = EndpointConfig(
            requests=requests,
            period=period,
            burst=burst,
            strategy=strategy,
        )

        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            # الحصول على معرف العميل
            # Get client identifier
            client_id = ClientIdentifier.get_client_id(request)

            # إنشاء مثيل limiter إذا لم يكن موجودًا
            # Create limiter instance if not exists
            if not hasattr(wrapper, "_limiter"):
                wrapper._limiter = RateLimiter()
                await wrapper._limiter.initialize()

            # التحقق من حد المعدل
            # Check rate limit
            allowed, remaining, reset = await wrapper._limiter.check_rate_limit(
                client_id=client_id,
                endpoint=endpoint_path
            )

            if not allowed:
                raise HTTPException(
                    status_code=429,
                    detail={
                        "error": "rate_limit_exceeded",
                        "message": "تم تجاوز حد المعدل - Rate limit exceeded",
                        "retry_after": reset,
                    },
                    headers={
                        "Retry-After": str(reset),
                        "X-RateLimit-Limit": str(requests),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(reset),
                    }
                )

            # تنفيذ الدالة
            # Execute function
            return await func(request, *args, **kwargs)

        return wrapper

    return decorator


# ═══════════════════════════════════════════════════════════════════════════════
# دوال مساعدة
# Helper Functions
# ═══════════════════════════════════════════════════════════════════════════════


def setup_rate_limiting(
    app: FastAPI,
    redis_url: str | None = None,
    exclude_paths: list[str] | None = None,
    identifier_func: Callable[[Request], str] | None = None,
) -> RateLimiter:
    """
    إعداد حد المعدل لتطبيق FastAPI
    Set up rate limiting for a FastAPI application.

    Args:
        app: تطبيق FastAPI - FastAPI application
        redis_url: عنوان URL لـ Redis - Redis connection URL
        exclude_paths: مسارات مستثناة - Paths to exclude
        identifier_func: دالة مخصصة لتحديد هوية العميل - Custom client identification function

    Returns:
        مثيل RateLimiter - RateLimiter instance

    Usage:
        from apps.kernel.common.middleware import setup_rate_limiting

        app = FastAPI()
        limiter = setup_rate_limiting(app)
    """
    limiter = RateLimiter(redis_url=redis_url)

    @app.on_event("startup")
    async def initialize_rate_limiter():
        await limiter.initialize()
        logger.info("✓ حد المعدل تم تهيئته - Rate limiting initialized")

    app.add_middleware(
        RateLimitMiddleware,
        limiter=limiter,
        exclude_paths=exclude_paths,
        identifier_func=identifier_func,
    )

    return limiter


async def get_rate_limit_stats(limiter: RateLimiter, client_id: str) -> dict[str, Any]:
    """
    الحصول على إحصائيات حد المعدل لعميل
    Get rate limit statistics for a client.

    Args:
        limiter: مثيل RateLimiter - RateLimiter instance
        client_id: معرف العميل - Client identifier

    Returns:
        إحصائيات حد المعدل - Rate limit statistics
    """
    stats = {
        "client_id": client_id,
        "identification_method": ClientIdentifier.get_identification_method(client_id),
        "endpoints": {}
    }

    for endpoint, config in ENDPOINT_CONFIGS.items():
        remaining = await limiter.get_remaining_requests(client_id, endpoint)
        stats["endpoints"][endpoint] = {
            "limit": config.requests,
            "period": config.period,
            "remaining": remaining,
            "strategy": config.strategy,
        }

    return stats
