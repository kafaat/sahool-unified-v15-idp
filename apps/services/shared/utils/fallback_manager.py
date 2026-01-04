"""
SAHOOL API Fallback Manager with Circuit Breaker Pattern
مدير الاحتياطي لواجهات برمجة التطبيقات مع نمط قاطع الدائرة

This module provides a robust fallback mechanism for API calls with circuit breaker pattern
to prevent cascading failures and improve system resilience.

يوفر هذا الوحدة آلية احتياطية قوية لاستدعاءات واجهة برمجة التطبيقات مع نمط قاطع الدائرة
لمنع الفشل المتتالي وتحسين مرونة النظام.
"""

import json
import logging
import time
from collections.abc import Callable
from datetime import datetime
from enum import Enum
from functools import wraps
from threading import Lock
from typing import Any

# إعداد السجلات
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """
    حالات قاطع الدائرة
    Circuit Breaker States

    CLOSED: النظام يعمل بشكل طبيعي - Normal operation
    OPEN: النظام معطل مؤقتاً - System temporarily disabled
    HALF_OPEN: النظام في وضع الاختبار - System in testing mode
    """
    CLOSED = "closed"  # يسمح بجميع الطلبات - Allows all requests
    OPEN = "open"  # يرفض جميع الطلبات - Rejects all requests
    HALF_OPEN = "half_open"  # يسمح ببعض الطلبات للاختبار - Allows limited requests for testing


class CircuitBreaker:
    """
    قاطع الدائرة - Circuit Breaker Implementation

    يراقب الفشل ويفتح الدائرة عند تجاوز عتبة الفشل
    Monitors failures and opens circuit when failure threshold is exceeded

    Attributes:
        failure_threshold (int): عدد الفشل المسموح قبل فتح الدائرة - Number of failures before opening circuit
        recovery_timeout (int): وقت الانتظار بالثواني قبل محاولة الاستعادة - Wait time in seconds before recovery attempt
        success_threshold (int): عدد النجاحات المطلوبة لإغلاق الدائرة - Number of successes needed to close circuit
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 30,
        success_threshold: int = 3
    ):
        """
        تهيئة قاطع الدائرة
        Initialize Circuit Breaker

        Args:
            failure_threshold: عدد الفشل المسموح - Number of allowed failures
            recovery_timeout: مهلة الاستعادة بالثواني - Recovery timeout in seconds
            success_threshold: عدد النجاحات للإغلاق - Number of successes to close
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold

        # حالة الدائرة - Circuit state
        self.state = CircuitState.CLOSED

        # العدادات - Counters
        self.failure_count = 0
        self.success_count = 0

        # الأوقات - Timestamps
        self.last_failure_time: float | None = None
        self.opened_at: float | None = None

        # القفل للأمان في بيئة متعددة الخيوط - Thread safety lock
        self._lock = Lock()

        logger.info(
            f"تم إنشاء قاطع دائرة - Circuit Breaker created: "
            f"failure_threshold={failure_threshold}, "
            f"recovery_timeout={recovery_timeout}, "
            f"success_threshold={success_threshold}"
        )

    def call(self, func: Callable, *args, **kwargs) -> tuple[Any, bool]:
        """
        تنفيذ الدالة مع حماية قاطع الدائرة
        Execute function with circuit breaker protection

        Args:
            func: الدالة المراد تنفيذها - Function to execute
            *args: معاملات الدالة - Function arguments
            **kwargs: معاملات الدالة المسماة - Function keyword arguments

        Returns:
            Tuple[Any, bool]: نتيجة الدالة وحالة النجاح - Function result and success status

        Raises:
            Exception: إذا كانت الدائرة مفتوحة - If circuit is open
        """
        with self._lock:
            # التحقق من حالة الدائرة - Check circuit state
            if self.state == CircuitState.OPEN:
                # التحقق من إمكانية الانتقال إلى نصف مفتوح - Check if can transition to half-open
                if self._should_attempt_reset():
                    self._transition_to_half_open()
                else:
                    logger.warning(
                        f"الدائرة مفتوحة - Circuit is OPEN. "
                        f"وقت الانتظار المتبقي: {self._time_until_retry():.1f}s"
                    )
                    raise Exception("Circuit breaker is OPEN")

        # محاولة تنفيذ الدالة - Attempt to execute function
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result, True
        except Exception as e:
            self._on_failure()
            logger.error(f"فشل تنفيذ الدالة - Function execution failed: {str(e)}")
            raise

    def _on_success(self):
        """
        معالجة النجاح - Handle successful execution
        """
        with self._lock:
            self.failure_count = 0

            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                logger.info(
                    f"نجاح في وضع نصف مفتوح - Success in HALF_OPEN: "
                    f"{self.success_count}/{self.success_threshold}"
                )

                # إغلاق الدائرة إذا تم تحقيق العتبة - Close circuit if threshold met
                if self.success_count >= self.success_threshold:
                    self._transition_to_closed()

    def _on_failure(self):
        """
        معالجة الفشل - Handle failed execution
        """
        with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.time()

            logger.warning(
                f"فشل مسجل - Failure recorded: "
                f"{self.failure_count}/{self.failure_threshold}"
            )

            # فتح الدائرة إذا تم تجاوز العتبة - Open circuit if threshold exceeded
            if self.failure_count >= self.failure_threshold:
                self._transition_to_open()

            # إعادة تعيين عداد النجاح في وضع نصف مفتوح - Reset success count in half-open
            if self.state == CircuitState.HALF_OPEN:
                self.success_count = 0
                self._transition_to_open()

    def _transition_to_open(self):
        """
        الانتقال إلى حالة مفتوح - Transition to OPEN state
        """
        self.state = CircuitState.OPEN
        self.opened_at = time.time()
        self.success_count = 0
        logger.error(
            f"⚠️ الدائرة مفتوحة الآن - Circuit is now OPEN. "
            f"فشل {self.failure_count} مرات"
        )

    def _transition_to_half_open(self):
        """
        الانتقال إلى حالة نصف مفتوح - Transition to HALF_OPEN state
        """
        self.state = CircuitState.HALF_OPEN
        self.success_count = 0
        logger.info("🔄 الدائرة في وضع نصف مفتوح - Circuit is now HALF_OPEN")

    def _transition_to_closed(self):
        """
        الانتقال إلى حالة مغلق - Transition to CLOSED state
        """
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.opened_at = None
        logger.info("✅ الدائرة مغلقة - Circuit is now CLOSED")

    def _should_attempt_reset(self) -> bool:
        """
        التحقق من إمكانية محاولة إعادة التعيين
        Check if should attempt reset

        Returns:
            bool: True إذا انتهت مهلة الاستعادة - True if recovery timeout has elapsed
        """
        if self.opened_at is None:
            return False

        elapsed = time.time() - self.opened_at
        return elapsed >= self.recovery_timeout

    def _time_until_retry(self) -> float:
        """
        حساب الوقت المتبقي حتى إعادة المحاولة
        Calculate time remaining until retry

        Returns:
            float: الثواني المتبقية - Seconds remaining
        """
        if self.opened_at is None:
            return 0.0

        elapsed = time.time() - self.opened_at
        return max(0.0, self.recovery_timeout - elapsed)

    def reset(self):
        """
        إعادة تعيين قاطع الدائرة يدوياً
        Manually reset circuit breaker
        """
        with self._lock:
            self._transition_to_closed()
            logger.info("🔧 تم إعادة تعيين الدائرة يدوياً - Circuit manually reset")

    def get_status(self) -> dict[str, Any]:
        """
        الحصول على حالة قاطع الدائرة
        Get circuit breaker status

        Returns:
            Dict: معلومات الحالة - Status information
        """
        with self._lock:
            return {
                "state": self.state.value,
                "failure_count": self.failure_count,
                "success_count": self.success_count,
                "failure_threshold": self.failure_threshold,
                "success_threshold": self.success_threshold,
                "recovery_timeout": self.recovery_timeout,
                "time_until_retry": self._time_until_retry() if self.state == CircuitState.OPEN else 0,
                "last_failure_time": datetime.fromtimestamp(self.last_failure_time).isoformat()
                    if self.last_failure_time else None
            }


class FallbackManager:
    """
    مدير الاحتياطي - Fallback Manager

    يدير الدوال الاحتياطية لخدمات مختلفة مع حماية قاطع الدائرة
    Manages fallback functions for different services with circuit breaker protection
    """

    def __init__(self):
        """
        تهيئة مدير الاحتياطي
        Initialize Fallback Manager
        """
        # خريطة الدوال الاحتياطية - Fallback functions map
        self._fallbacks: dict[str, Callable] = {}

        # خريطة قواطع الدائرة - Circuit breakers map
        self._circuit_breakers: dict[str, CircuitBreaker] = {}

        # ذاكرة التخزين المؤقت - Cache storage
        self._cache: dict[str, tuple[Any, float]] = {}

        # مدة التخزين المؤقت (5 دقائق) - Cache duration (5 minutes)
        self._cache_ttl = 300

        # القفل - Thread lock
        self._lock = Lock()

        logger.info("✨ تم تهيئة مدير الاحتياطي - Fallback Manager initialized")

    def register_fallback(
        self,
        service_name: str,
        fallback_fn: Callable,
        failure_threshold: int = 5,
        recovery_timeout: int = 30,
        success_threshold: int = 3
    ):
        """
        تسجيل دالة احتياطية لخدمة
        Register a fallback function for a service

        Args:
            service_name: اسم الخدمة - Service name
            fallback_fn: الدالة الاحتياطية - Fallback function
            failure_threshold: عتبة الفشل - Failure threshold
            recovery_timeout: مهلة الاستعادة - Recovery timeout
            success_threshold: عتبة النجاح - Success threshold
        """
        with self._lock:
            self._fallbacks[service_name] = fallback_fn
            self._circuit_breakers[service_name] = CircuitBreaker(
                failure_threshold=failure_threshold,
                recovery_timeout=recovery_timeout,
                success_threshold=success_threshold
            )
            logger.info(f"✅ تم تسجيل احتياطي للخدمة - Registered fallback for: {service_name}")

    def execute_with_fallback(
        self,
        service_name: str,
        primary_fn: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        تنفيذ دالة مع احتياطي
        Execute function with fallback

        Args:
            service_name: اسم الخدمة - Service name
            primary_fn: الدالة الأساسية - Primary function
            *args: معاملات الدالة - Function arguments
            **kwargs: معاملات مسماة - Keyword arguments

        Returns:
            Any: نتيجة الدالة الأساسية أو الاحتياطية - Result from primary or fallback
        """
        # التحقق من وجود قاطع دائرة - Check if circuit breaker exists
        if service_name not in self._circuit_breakers:
            logger.warning(
                f"⚠️ لا يوجد قاطع دائرة للخدمة - No circuit breaker for: {service_name}. "
                f"تنفيذ مباشر - Executing directly."
            )
            return primary_fn(*args, **kwargs)

        circuit_breaker = self._circuit_breakers[service_name]

        try:
            # محاولة تنفيذ الدالة الأساسية - Try primary function
            result, success = circuit_breaker.call(primary_fn, *args, **kwargs)

            # تخزين النتيجة في الذاكرة المؤقتة - Cache the result
            self._cache_result(service_name, result)

            return result

        except Exception as e:
            logger.warning(
                f"⚠️ فشل الدالة الأساسية للخدمة {service_name}: {str(e)}"
            )

            # محاولة استخدام الدالة الاحتياطية - Try fallback function
            if service_name in self._fallbacks:
                logger.info(f"🔄 استخدام الدالة الاحتياطية - Using fallback for: {service_name}")
                try:
                    fallback_fn = self._fallbacks[service_name]
                    result = fallback_fn(*args, **kwargs)
                    return result
                except Exception as fallback_error:
                    logger.error(
                        f"❌ فشل الاحتياطي أيضاً - Fallback also failed: {str(fallback_error)}"
                    )

            # محاولة استخدام النتيجة المخزنة - Try cached result
            cached_result = self._get_cached_result(service_name)
            if cached_result is not None:
                logger.info(f"💾 استخدام النتيجة المخزنة - Using cached result for: {service_name}")
                return cached_result

            # إذا فشل كل شيء - If everything fails
            raise Exception(
                f"كل المحاولات فشلت للخدمة {service_name} - "
                f"All attempts failed for service {service_name}"
            )

    def _cache_result(self, service_name: str, result: Any):
        """
        تخزين النتيجة في الذاكرة المؤقتة
        Cache the result

        Args:
            service_name: اسم الخدمة - Service name
            result: النتيجة للتخزين - Result to cache
        """
        with self._lock:
            self._cache[service_name] = (result, time.time())

    def _get_cached_result(self, service_name: str) -> Any | None:
        """
        الحصول على النتيجة المخزنة
        Get cached result

        Args:
            service_name: اسم الخدمة - Service name

        Returns:
            Optional[Any]: النتيجة المخزنة إن وجدت - Cached result if available
        """
        with self._lock:
            if service_name not in self._cache:
                return None

            result, timestamp = self._cache[service_name]

            # التحقق من صلاحية التخزين - Check cache validity
            if time.time() - timestamp > self._cache_ttl:
                del self._cache[service_name]
                return None

            return result

    def get_circuit_status(self, service_name: str) -> dict[str, Any] | None:
        """
        الحصول على حالة قاطع الدائرة لخدمة
        Get circuit breaker status for a service

        Args:
            service_name: اسم الخدمة - Service name

        Returns:
            Optional[Dict]: حالة قاطع الدائرة - Circuit breaker status
        """
        if service_name not in self._circuit_breakers:
            return None

        return self._circuit_breakers[service_name].get_status()

    def reset_circuit(self, service_name: str):
        """
        إعادة تعيين قاطع الدائرة لخدمة
        Reset circuit breaker for a service

        Args:
            service_name: اسم الخدمة - Service name
        """
        if service_name in self._circuit_breakers:
            self._circuit_breakers[service_name].reset()
            logger.info(f"🔧 تم إعادة تعيين قاطع الدائرة - Circuit reset for: {service_name}")

    def get_all_statuses(self) -> dict[str, dict[str, Any]]:
        """
        الحصول على حالة جميع قواطع الدائرة
        Get status of all circuit breakers

        Returns:
            Dict: حالات جميع القواطع - All circuit breaker statuses
        """
        return {
            service: self.get_circuit_status(service)
            for service in self._circuit_breakers
        }


# ===== الديكوريتورز - Decorators =====

def circuit_breaker(
    failure_threshold: int = 5,
    recovery_timeout: int = 30,
    success_threshold: int = 3
):
    """
    ديكوريتور قاطع الدائرة
    Circuit Breaker Decorator

    يحمي الدالة بقاطع دائرة
    Protects function with a circuit breaker

    Args:
        failure_threshold: عتبة الفشل - Failure threshold
        recovery_timeout: مهلة الاستعادة - Recovery timeout
        success_threshold: عتبة النجاح - Success threshold

    Example:
        @circuit_breaker(failure_threshold=3, recovery_timeout=60)
        def call_external_api():
            # استدعاء واجهة برمجة تطبيقات خارجية
            pass
    """
    def decorator(func: Callable) -> Callable:
        cb = CircuitBreaker(
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout,
            success_threshold=success_threshold
        )

        @wraps(func)
        def wrapper(*args, **kwargs):
            result, _ = cb.call(func, *args, **kwargs)
            return result

        # إضافة خاصية للوصول إلى قاطع الدائرة - Add property to access circuit breaker
        wrapper.circuit_breaker = cb

        return wrapper

    return decorator


def with_fallback(fallback_fn: Callable):
    """
    ديكوريتور الدالة الاحتياطية
    Fallback Function Decorator

    يوفر دالة احتياطية في حالة فشل الدالة الأساسية
    Provides a fallback function if primary function fails

    Args:
        fallback_fn: الدالة الاحتياطية - Fallback function

    Example:
        def fallback_weather():
            return {"temp": 25, "condition": "unknown"}

        @with_fallback(fallback_weather)
        def get_weather():
            # الحصول على الطقس من واجهة برمجة تطبيقات
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.warning(
                    f"⚠️ فشل {func.__name__}، استخدام الاحتياطي - "
                    f"{func.__name__} failed, using fallback: {str(e)}"
                )
                try:
                    return fallback_fn(*args, **kwargs)
                except Exception as fallback_error:
                    logger.error(
                        f"❌ فشل الاحتياطي أيضاً - Fallback also failed: {str(fallback_error)}"
                    )
                    raise e

        return wrapper

    return decorator


# ===== احتياطيات خاصة بالخدمات - Service-Specific Fallbacks =====

class ServiceFallbacks:
    """
    دوال احتياطية خاصة بخدمات SAHOOL
    Service-specific fallback functions for SAHOOL
    """

    @staticmethod
    def weather_fallback(*args, **kwargs) -> dict[str, Any]:
        """
        احتياطي لخدمة الطقس
        Weather service fallback

        يرجع بيانات طقس افتراضية أو مخزنة
        Returns default or cached weather data
        """
        logger.info("🌤️ استخدام احتياطي الطقس - Using weather fallback")

        # يمكن تحسين هذا ليستخدم آخر بيانات معروفة
        # This can be enhanced to use last known data
        return {
            "temperature": 25.0,
            "humidity": 60.0,
            "condition": "غير معروف - Unknown",
            "wind_speed": 0.0,
            "precipitation": 0.0,
            "source": "fallback",
            "message": "بيانات افتراضية - استخدم بحذر - Default data - Use with caution",
            "timestamp": datetime.now().isoformat()
        }

    @staticmethod
    def satellite_fallback(*args, **kwargs) -> dict[str, Any]:
        """
        احتياطي لخدمة الأقمار الصناعية
        Satellite service fallback

        يرجع صور مخزنة أو حالة غير متاحة
        Returns cached imagery or unavailable status
        """
        logger.info("🛰️ استخدام احتياطي الأقمار الصناعية - Using satellite fallback")

        return {
            "imagery_available": False,
            "ndvi": None,
            "last_update": None,
            "source": "fallback",
            "message": "صور الأقمار الصناعية غير متوفرة حالياً - Satellite imagery currently unavailable",
            "timestamp": datetime.now().isoformat()
        }

    @staticmethod
    def ai_fallback(*args, **kwargs) -> dict[str, Any]:
        """
        احتياطي لخدمة الذكاء الاصطناعي
        AI service fallback

        يرجع توصيات مبنية على القواعد
        Returns rule-based recommendations
        """
        logger.info("🤖 استخدام احتياطي الذكاء الاصطناعي - Using AI fallback")

        # توصيات عامة مبنية على القواعد
        # General rule-based recommendations
        return {
            "recommendations": [
                {
                    "type": "general",
                    "priority": "medium",
                    "message_ar": "تابع مراقبة المحاصيل بانتظام",
                    "message_en": "Continue monitoring crops regularly"
                },
                {
                    "type": "general",
                    "priority": "low",
                    "message_ar": "تحقق من نظام الري",
                    "message_en": "Check irrigation system"
                }
            ],
            "confidence": 0.3,
            "source": "fallback_rules",
            "message": "توصيات عامة - مطلوب تحليل متقدم - General recommendations - Advanced analysis required",
            "timestamp": datetime.now().isoformat()
        }

    @staticmethod
    def crop_health_fallback(*args, **kwargs) -> dict[str, Any]:
        """
        احتياطي لخدمة صحة المحاصيل
        Crop health service fallback
        """
        logger.info("🌱 استخدام احتياطي صحة المحاصيل - Using crop health fallback")

        return {
            "health_status": "unknown",
            "health_score": 50.0,
            "issues": [],
            "source": "fallback",
            "message": "حالة صحة المحصول غير معروفة - يرجى الفحص اليدوي - Crop health unknown - Manual inspection required",
            "timestamp": datetime.now().isoformat()
        }

    @staticmethod
    def irrigation_fallback(*args, **kwargs) -> dict[str, Any]:
        """
        احتياطي لخدمة الري
        Irrigation service fallback
        """
        logger.info("💧 استخدام احتياطي الري - Using irrigation fallback")

        return {
            "irrigation_needed": None,
            "water_amount": 0.0,
            "schedule": None,
            "source": "fallback",
            "message": "توصيات الري غير متوفرة - استخدم الخبرة المحلية - Irrigation recommendations unavailable - Use local expertise",
            "timestamp": datetime.now().isoformat()
        }


# ===== نسخة عامة من مدير الاحتياطي - Global Fallback Manager Instance =====

# إنشاء نسخة عامة للاستخدام المباشر
# Create global instance for direct use
global_fallback_manager = FallbackManager()

# تسجيل الاحتياطيات الافتراضية - Register default fallbacks
global_fallback_manager.register_fallback(
    "weather",
    ServiceFallbacks.weather_fallback,
    failure_threshold=5,
    recovery_timeout=30
)

global_fallback_manager.register_fallback(
    "satellite",
    ServiceFallbacks.satellite_fallback,
    failure_threshold=3,
    recovery_timeout=60
)

global_fallback_manager.register_fallback(
    "ai",
    ServiceFallbacks.ai_fallback,
    failure_threshold=5,
    recovery_timeout=30
)

global_fallback_manager.register_fallback(
    "crop_health",
    ServiceFallbacks.crop_health_fallback,
    failure_threshold=4,
    recovery_timeout=45
)

global_fallback_manager.register_fallback(
    "irrigation",
    ServiceFallbacks.irrigation_fallback,
    failure_threshold=4,
    recovery_timeout=45
)

logger.info("✅ تم تسجيل جميع الاحتياطيات الافتراضية - All default fallbacks registered")


# ===== دوال مساعدة - Helper Functions =====

def get_fallback_manager() -> FallbackManager:
    """
    الحصول على نسخة مدير الاحتياطي العامة
    Get global fallback manager instance

    Returns:
        FallbackManager: مدير الاحتياطي - Fallback manager instance
    """
    return global_fallback_manager


if __name__ == "__main__":
    # مثال على الاستخدام - Usage example
    print("🔧 مثال على استخدام مدير الاحتياطي - Fallback Manager Usage Example")

    # إنشاء مدير احتياطي - Create fallback manager
    fm = FallbackManager()

    # تعريف دالة احتياطية - Define fallback function
    def my_fallback(*args, **kwargs):
        return {"status": "fallback", "data": "بيانات احتياطية"}

    # تسجيل الخدمة - Register service
    fm.register_fallback("test_service", my_fallback, failure_threshold=3)

    # دالة أساسية تفشل - Primary function that fails
    def failing_function():
        raise Exception("فشل متعمد - Intentional failure")

    # تنفيذ مع الاحتياطي - Execute with fallback
    try:
        result = fm.execute_with_fallback("test_service", failing_function)
        print(f"✅ النتيجة: {result}")
    except Exception as e:
        print(f"❌ خطأ: {e}")

    # عرض الحالة - Display status
    status = fm.get_circuit_status("test_service")
    print(f"📊 حالة الدائرة: {json.dumps(status, indent=2, ensure_ascii=False)}")
