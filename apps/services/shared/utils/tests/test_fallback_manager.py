"""
SAHOOL API Fallback Manager Tests
اختبارات مدير الاحتياطي لواجهات برمجة التطبيقات

Comprehensive tests for Circuit Breaker pattern and Fallback Manager
اختبارات شاملة لنمط قاطع الدائرة ومدير الاحتياطي
"""

import pytest
import time
from unittest.mock import Mock, patch
from datetime import datetime

import sys
import os

# إضافة المسار للوحدة - Add module path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fallback_manager import (
    CircuitBreaker,
    CircuitState,
    FallbackManager,
    ServiceFallbacks,
    circuit_breaker,
    with_fallback,
    get_fallback_manager
)


# ===== اختبارات قاطع الدائرة - Circuit Breaker Tests =====

class TestCircuitBreaker:
    """
    اختبارات قاطع الدائرة
    Circuit Breaker Tests
    """

    def test_circuit_breaker_initialization(self):
        """
        اختبار: تهيئة قاطع الدائرة
        Test: Circuit breaker initialization
        """
        cb = CircuitBreaker(failure_threshold=5, recovery_timeout=30, success_threshold=3)

        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0
        assert cb.success_count == 0
        assert cb.failure_threshold == 5
        assert cb.recovery_timeout == 30
        assert cb.success_threshold == 3

    def test_circuit_breaker_successful_call(self):
        """
        اختبار: استدعاء ناجح
        Test: Successful call
        """
        cb = CircuitBreaker()

        def successful_func():
            return "نجاح - success"

        result, success = cb.call(successful_func)

        assert result == "نجاح - success"
        assert success is True
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0

    def test_circuit_opens_after_threshold_failures(self):
        """
        اختبار: فتح الدائرة بعد تجاوز عتبة الفشل
        Test: Circuit opens after threshold failures
        """
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=30)

        def failing_func():
            raise Exception("فشل - failure")

        # محاولة 3 مرات - Try 3 times
        for i in range(3):
            with pytest.raises(Exception):
                cb.call(failing_func)

        # التحقق من فتح الدائرة - Verify circuit is open
        assert cb.state == CircuitState.OPEN
        assert cb.failure_count == 3

        # المحاولة الرابعة يجب أن تفشل بسبب فتح الدائرة
        # Fourth attempt should fail due to open circuit
        with pytest.raises(Exception, match="Circuit breaker is OPEN"):
            cb.call(failing_func)

    def test_circuit_transitions_to_half_open_after_timeout(self):
        """
        اختبار: انتقال الدائرة إلى نصف مفتوح بعد انتهاء المهلة
        Test: Circuit transitions to half-open after timeout
        """
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=1)

        def failing_func():
            raise Exception("فشل - failure")

        # فتح الدائرة - Open circuit
        for i in range(2):
            with pytest.raises(Exception):
                cb.call(failing_func)

        assert cb.state == CircuitState.OPEN

        # الانتظار لانتهاء المهلة - Wait for timeout
        time.sleep(1.1)

        # المحاولة التالية يجب أن تنقل إلى نصف مفتوح
        # Next attempt should transition to half-open
        def successful_func():
            return "نجاح - success"

        # يجب أن ينتقل إلى نصف مفتوح - Should transition to half-open
        # ولكن سينجح - But will succeed
        result, success = cb.call(successful_func)

        assert cb.state == CircuitState.HALF_OPEN
        assert result == "نجاح - success"

    def test_circuit_closes_after_success_threshold(self):
        """
        اختبار: إغلاق الدائرة بعد تحقيق عتبة النجاح
        Test: Circuit closes after success threshold
        """
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=1, success_threshold=2)

        def failing_func():
            raise Exception("فشل - failure")

        def successful_func():
            return "نجاح - success"

        # فتح الدائرة - Open circuit
        for i in range(2):
            with pytest.raises(Exception):
                cb.call(failing_func)

        assert cb.state == CircuitState.OPEN

        # الانتظار - Wait
        time.sleep(1.1)

        # نجاح مرتين للإغلاق - Two successes to close
        cb.call(successful_func)
        assert cb.state == CircuitState.HALF_OPEN

        cb.call(successful_func)
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0
        assert cb.success_count == 0

    def test_circuit_reopens_on_failure_in_half_open(self):
        """
        اختبار: إعادة فتح الدائرة عند الفشل في وضع نصف مفتوح
        Test: Circuit reopens on failure in half-open state
        """
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=1)

        def failing_func():
            raise Exception("فشل - failure")

        def successful_func():
            return "نجاح - success"

        # فتح الدائرة - Open circuit
        for i in range(2):
            with pytest.raises(Exception):
                cb.call(failing_func)

        assert cb.state == CircuitState.OPEN

        # الانتظار - Wait
        time.sleep(1.1)

        # الانتقال إلى نصف مفتوح بنجاح - Transition to half-open with success
        cb.call(successful_func)
        assert cb.state == CircuitState.HALF_OPEN

        # الفشل في نصف مفتوح يجب أن يعيد فتح الدائرة
        # Failure in half-open should reopen circuit
        with pytest.raises(Exception):
            cb.call(failing_func)

        assert cb.state == CircuitState.OPEN

    def test_manual_reset(self):
        """
        اختبار: إعادة التعيين اليدوية
        Test: Manual reset
        """
        cb = CircuitBreaker(failure_threshold=2)

        def failing_func():
            raise Exception("فشل - failure")

        # فتح الدائرة - Open circuit
        for i in range(2):
            with pytest.raises(Exception):
                cb.call(failing_func)

        assert cb.state == CircuitState.OPEN

        # إعادة تعيين يدوية - Manual reset
        cb.reset()

        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0
        assert cb.success_count == 0

    def test_get_status(self):
        """
        اختبار: الحصول على الحالة
        Test: Get status
        """
        cb = CircuitBreaker(failure_threshold=5, recovery_timeout=30)

        status = cb.get_status()

        assert status["state"] == "closed"
        assert status["failure_count"] == 0
        assert status["success_count"] == 0
        assert status["failure_threshold"] == 5
        assert status["recovery_timeout"] == 30


# ===== اختبارات مدير الاحتياطي - Fallback Manager Tests =====

class TestFallbackManager:
    """
    اختبارات مدير الاحتياطي
    Fallback Manager Tests
    """

    def test_fallback_manager_initialization(self):
        """
        اختبار: تهيئة مدير الاحتياطي
        Test: Fallback manager initialization
        """
        fm = FallbackManager()

        assert len(fm._fallbacks) == 0
        assert len(fm._circuit_breakers) == 0

    def test_register_fallback(self):
        """
        اختبار: تسجيل دالة احتياطية
        Test: Register fallback function
        """
        fm = FallbackManager()

        def my_fallback():
            return "احتياطي - fallback"

        fm.register_fallback("test_service", my_fallback)

        assert "test_service" in fm._fallbacks
        assert "test_service" in fm._circuit_breakers

    def test_execute_with_fallback_success(self):
        """
        اختبار: تنفيذ ناجح دون احتياطي
        Test: Successful execution without fallback
        """
        fm = FallbackManager()

        def my_fallback():
            return "احتياطي - fallback"

        def primary_func():
            return "أساسي - primary"

        fm.register_fallback("test_service", my_fallback)

        result = fm.execute_with_fallback("test_service", primary_func)

        assert result == "أساسي - primary"

    def test_execute_with_fallback_uses_fallback_on_failure(self):
        """
        اختبار: استخدام الاحتياطي عند فشل الدالة الأساسية
        Test: Uses fallback on primary failure
        """
        fm = FallbackManager()

        def my_fallback():
            return "احتياطي - fallback"

        def failing_func():
            raise Exception("فشل - failure")

        fm.register_fallback("test_service", my_fallback, failure_threshold=1)

        result = fm.execute_with_fallback("test_service", failing_func)

        assert result == "احتياطي - fallback"

    def test_execute_with_fallback_uses_cache(self):
        """
        اختبار: استخدام الذاكرة المؤقتة عند فشل الاحتياطي
        Test: Uses cache when fallback fails
        """
        fm = FallbackManager()

        call_count = {"count": 0}

        def failing_fallback():
            raise Exception("فشل الاحتياطي - fallback failure")

        def primary_func():
            call_count["count"] += 1
            if call_count["count"] == 1:
                return "نتيجة مخزنة - cached result"
            raise Exception("فشل - failure")

        fm.register_fallback("test_service", failing_fallback, failure_threshold=1)

        # النجاح الأول يخزن النتيجة - First success caches result
        result1 = fm.execute_with_fallback("test_service", primary_func)
        assert result1 == "نتيجة مخزنة - cached result"

        # الفشل الثاني يستخدم المخزن - Second failure uses cache
        result2 = fm.execute_with_fallback("test_service", primary_func)
        assert result2 == "نتيجة مخزنة - cached result"

    def test_get_circuit_status(self):
        """
        اختبار: الحصول على حالة قاطع الدائرة
        Test: Get circuit status
        """
        fm = FallbackManager()

        def my_fallback():
            return "احتياطي"

        fm.register_fallback("test_service", my_fallback)

        status = fm.get_circuit_status("test_service")

        assert status is not None
        assert status["state"] == "closed"

    def test_reset_circuit(self):
        """
        اختبار: إعادة تعيين قاطع الدائرة
        Test: Reset circuit
        """
        fm = FallbackManager()

        def my_fallback():
            return "احتياطي"

        def failing_func():
            raise Exception("فشل")

        fm.register_fallback("test_service", my_fallback, failure_threshold=2)

        # فتح الدائرة - Open circuit
        for i in range(2):
            fm.execute_with_fallback("test_service", failing_func)

        status = fm.get_circuit_status("test_service")
        assert status["state"] == "open"

        # إعادة تعيين - Reset
        fm.reset_circuit("test_service")

        status = fm.get_circuit_status("test_service")
        assert status["state"] == "closed"

    def test_get_all_statuses(self):
        """
        اختبار: الحصول على جميع الحالات
        Test: Get all statuses
        """
        fm = FallbackManager()

        def fallback1():
            return "1"

        def fallback2():
            return "2"

        fm.register_fallback("service1", fallback1)
        fm.register_fallback("service2", fallback2)

        all_statuses = fm.get_all_statuses()

        assert len(all_statuses) == 2
        assert "service1" in all_statuses
        assert "service2" in all_statuses


# ===== اختبارات الديكوريتورز - Decorator Tests =====

class TestDecorators:
    """
    اختبارات الديكوريتورز
    Decorator Tests
    """

    def test_circuit_breaker_decorator_success(self):
        """
        اختبار: ديكوريتور قاطع الدائرة مع نجاح
        Test: Circuit breaker decorator with success
        """
        @circuit_breaker(failure_threshold=3)
        def successful_func():
            return "نجاح - success"

        result = successful_func()
        assert result == "نجاح - success"

    def test_circuit_breaker_decorator_failure(self):
        """
        اختبار: ديكوريتور قاطع الدائرة مع فشل
        Test: Circuit breaker decorator with failure
        """
        @circuit_breaker(failure_threshold=2)
        def failing_func():
            raise Exception("فشل - failure")

        # محاولتان تفشلان - Two failures
        for i in range(2):
            with pytest.raises(Exception):
                failing_func()

        # المحاولة الثالثة - دائرة مفتوحة - Third attempt - circuit open
        with pytest.raises(Exception, match="Circuit breaker is OPEN"):
            failing_func()

    def test_circuit_breaker_decorator_has_circuit_breaker_attribute(self):
        """
        اختبار: الديكوريتور يحتوي على خاصية قاطع الدائرة
        Test: Decorator has circuit_breaker attribute
        """
        @circuit_breaker(failure_threshold=3)
        def test_func():
            return "test"

        assert hasattr(test_func, 'circuit_breaker')
        assert isinstance(test_func.circuit_breaker, CircuitBreaker)

    def test_with_fallback_decorator_success(self):
        """
        اختبار: ديكوريتور الاحتياطي مع نجاح
        Test: Fallback decorator with success
        """
        def fallback_func():
            return "احتياطي - fallback"

        @with_fallback(fallback_func)
        def successful_func():
            return "نجاح - success"

        result = successful_func()
        assert result == "نجاح - success"

    def test_with_fallback_decorator_uses_fallback(self):
        """
        اختبار: ديكوريتور الاحتياطي يستخدم الاحتياطي عند الفشل
        Test: Fallback decorator uses fallback on failure
        """
        def fallback_func():
            return "احتياطي - fallback"

        @with_fallback(fallback_func)
        def failing_func():
            raise Exception("فشل - failure")

        result = failing_func()
        assert result == "احتياطي - fallback"

    def test_with_fallback_decorator_raises_on_both_failures(self):
        """
        اختبار: ديكوريتور الاحتياطي يرفع استثناء عند فشل الاثنين
        Test: Fallback decorator raises when both fail
        """
        def failing_fallback():
            raise Exception("فشل الاحتياطي - fallback failure")

        @with_fallback(failing_fallback)
        def failing_func():
            raise Exception("فشل أساسي - primary failure")

        with pytest.raises(Exception, match="فشل أساسي"):
            failing_func()


# ===== اختبارات الاحتياطيات الخاصة بالخدمات - Service Fallbacks Tests =====

class TestServiceFallbacks:
    """
    اختبارات الاحتياطيات الخاصة بالخدمات
    Service-Specific Fallbacks Tests
    """

    def test_weather_fallback(self):
        """
        اختبار: احتياطي خدمة الطقس
        Test: Weather service fallback
        """
        result = ServiceFallbacks.weather_fallback()

        assert "temperature" in result
        assert "humidity" in result
        assert "condition" in result
        assert result["source"] == "fallback"
        assert "timestamp" in result

    def test_satellite_fallback(self):
        """
        اختبار: احتياطي خدمة الأقمار الصناعية
        Test: Satellite service fallback
        """
        result = ServiceFallbacks.satellite_fallback()

        assert result["imagery_available"] is False
        assert result["ndvi"] is None
        assert result["source"] == "fallback"
        assert "timestamp" in result

    def test_ai_fallback(self):
        """
        اختبار: احتياطي خدمة الذكاء الاصطناعي
        Test: AI service fallback
        """
        result = ServiceFallbacks.ai_fallback()

        assert "recommendations" in result
        assert isinstance(result["recommendations"], list)
        assert len(result["recommendations"]) > 0
        assert result["source"] == "fallback_rules"
        assert result["confidence"] == 0.3

    def test_crop_health_fallback(self):
        """
        اختبار: احتياطي خدمة صحة المحاصيل
        Test: Crop health service fallback
        """
        result = ServiceFallbacks.crop_health_fallback()

        assert result["health_status"] == "unknown"
        assert result["health_score"] == 50.0
        assert result["source"] == "fallback"
        assert "timestamp" in result

    def test_irrigation_fallback(self):
        """
        اختبار: احتياطي خدمة الري
        Test: Irrigation service fallback
        """
        result = ServiceFallbacks.irrigation_fallback()

        assert result["irrigation_needed"] is None
        assert result["water_amount"] == 0.0
        assert result["source"] == "fallback"
        assert "timestamp" in result


# ===== اختبارات التكامل - Integration Tests =====

class TestIntegration:
    """
    اختبارات التكامل
    Integration Tests
    """

    def test_full_workflow_with_recovery(self):
        """
        اختبار: سير العمل الكامل مع الاستعادة
        Test: Full workflow with recovery
        """
        fm = FallbackManager()

        call_count = {"count": 0}

        def my_fallback():
            return "احتياطي - fallback"

        def flaky_func():
            call_count["count"] += 1
            # فشل 3 مرات ثم نجاح - Fail 3 times then succeed
            if call_count["count"] <= 3:
                raise Exception("فشل - failure")
            return "نجاح - success"

        fm.register_fallback("test_service", my_fallback, failure_threshold=3, recovery_timeout=1)

        # 3 فشل - 3 failures
        for i in range(3):
            result = fm.execute_with_fallback("test_service", flaky_func)
            assert result == "احتياطي - fallback"

        # التحقق من فتح الدائرة - Verify circuit is open
        status = fm.get_circuit_status("test_service")
        assert status["state"] == "open"

        # الانتظار للاستعادة - Wait for recovery
        time.sleep(1.1)

        # النجاح الآن - Should succeed now
        result = fm.execute_with_fallback("test_service", flaky_func)
        assert result == "نجاح - success"

    def test_multiple_services_independence(self):
        """
        اختبار: استقلالية الخدمات المتعددة
        Test: Multiple services independence
        """
        fm = FallbackManager()

        def fallback1():
            return "احتياطي1"

        def fallback2():
            return "احتياطي2"

        def failing_func():
            raise Exception("فشل")

        def successful_func():
            return "نجاح"

        fm.register_fallback("service1", fallback1, failure_threshold=2)
        fm.register_fallback("service2", fallback2, failure_threshold=2)

        # فشل service1 - Fail service1
        for i in range(2):
            fm.execute_with_fallback("service1", failing_func)

        # service2 يجب أن يعمل - service2 should work
        result = fm.execute_with_fallback("service2", successful_func)
        assert result == "نجاح"

        # التحقق من الحالات - Check statuses
        status1 = fm.get_circuit_status("service1")
        status2 = fm.get_circuit_status("service2")

        assert status1["state"] == "open"
        assert status2["state"] == "closed"

    def test_global_fallback_manager(self):
        """
        اختبار: مدير الاحتياطي العام
        Test: Global fallback manager
        """
        fm = get_fallback_manager()

        assert fm is not None
        assert isinstance(fm, FallbackManager)

        # التحقق من الاحتياطيات المسجلة مسبقاً - Check pre-registered fallbacks
        assert "weather" in fm._fallbacks
        assert "satellite" in fm._fallbacks
        assert "ai" in fm._fallbacks


# ===== اختبارات الأداء - Performance Tests =====

class TestPerformance:
    """
    اختبارات الأداء
    Performance Tests
    """

    def test_cache_expiration(self):
        """
        اختبار: انتهاء صلاحية التخزين المؤقت
        Test: Cache expiration
        """
        fm = FallbackManager()
        fm._cache_ttl = 1  # ثانية واحدة - 1 second

        def my_fallback():
            return "احتياطي"

        def primary_func():
            return "أساسي"

        fm.register_fallback("test_service", my_fallback)

        # تخزين النتيجة - Cache result
        result1 = fm.execute_with_fallback("test_service", primary_func)
        assert result1 == "أساسي"

        # الحصول من الذاكرة المؤقتة - Get from cache
        cached = fm._get_cached_result("test_service")
        assert cached == "أساسي"

        # الانتظار لانتهاء الصلاحية - Wait for expiration
        time.sleep(1.1)

        # يجب أن تكون انتهت الصلاحية - Should be expired
        cached = fm._get_cached_result("test_service")
        assert cached is None

    def test_thread_safety(self):
        """
        اختبار: الأمان في بيئة متعددة الخيوط
        Test: Thread safety
        """
        import threading

        fm = FallbackManager()

        def my_fallback():
            return "احتياطي"

        def primary_func():
            time.sleep(0.01)
            return "نجاح"

        fm.register_fallback("test_service", my_fallback)

        results = []

        def worker():
            result = fm.execute_with_fallback("test_service", primary_func)
            results.append(result)

        # إنشاء 10 خيوط - Create 10 threads
        threads = [threading.Thread(target=worker) for _ in range(10)]

        # بدء الخيوط - Start threads
        for t in threads:
            t.start()

        # انتظار الانتهاء - Wait for completion
        for t in threads:
            t.join()

        # التحقق من النتائج - Verify results
        assert len(results) == 10
        assert all(r == "نجاح" for r in results)


# ===== نقطة الدخول للاختبارات - Test Entry Point =====

if __name__ == "__main__":
    # تشغيل الاختبارات - Run tests
    pytest.main([__file__, "-v", "--tb=short"])
