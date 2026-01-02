"""
SAHOOL API Fallback Manager - Usage Examples
أمثلة استخدام مدير الاحتياطي لواجهات برمجة التطبيقات

Real-world examples for integrating fallback manager in SAHOOL services
أمثلة واقعية لدمج مدير الاحتياطي في خدمات سهول
"""

import time
import random
from datetime import datetime
from typing import Dict, Any, List

from fallback_manager import (
    FallbackManager,
    circuit_breaker,
    with_fallback,
    get_fallback_manager,
    ServiceFallbacks
)


# ===== مثال 1: خدمة الطقس - Example 1: Weather Service =====

print("\n" + "="*60)
print("مثال 1: خدمة الطقس مع الاحتياطي - Example 1: Weather with Fallback")
print("="*60)

def weather_api_call(location: str) -> Dict[str, Any]:
    """
    محاكاة استدعاء واجهة برمجة تطبيقات الطقس
    Simulate weather API call
    """
    # محاكاة فشل عشوائي - Simulate random failures
    if random.random() < 0.3:  # 30% فشل - 30% failure rate
        raise Exception("Weather API timeout")

    return {
        "location": location,
        "temperature": 28.5,
        "humidity": 65.0,
        "wind_speed": 12.3,
        "condition": "غائم جزئياً - Partly Cloudy",
        "timestamp": datetime.now().isoformat()
    }

# استخدام مدير الاحتياطي العام - Use global fallback manager
fm = get_fallback_manager()

print("\nاستدعاء خدمة الطقس 5 مرات - Calling weather service 5 times:")
for i in range(5):
    try:
        result = fm.execute_with_fallback(
            "weather",
            weather_api_call,
            location="صنعاء - Sana'a"
        )
        print(f"  {i+1}. ✅ نجاح - Success: {result['temperature']}°C, {result['condition']}")
    except Exception as e:
        print(f"  {i+1}. ❌ فشل - Failed: {str(e)}")

# عرض حالة الدائرة - Display circuit status
weather_status = fm.get_circuit_status("weather")
print(f"\n📊 حالة دائرة الطقس - Weather Circuit Status:")
print(f"  الحالة - State: {weather_status['state']}")
print(f"  الفشل - Failures: {weather_status['failure_count']}/{weather_status['failure_threshold']}")


# ===== مثال 2: خدمة الأقمار الصناعية - Example 2: Satellite Service =====

print("\n" + "="*60)
print("مثال 2: خدمة الأقمار الصناعية - Example 2: Satellite Service")
print("="*60)

# إنشاء مدير احتياطي مخصص - Create custom fallback manager
satellite_fm = FallbackManager()

def satellite_fallback_custom(field_id: str) -> Dict[str, Any]:
    """
    احتياطي مخصص للأقمار الصناعية
    Custom satellite fallback
    """
    return {
        "field_id": field_id,
        "ndvi": 0.65,  # قيمة افتراضية آمنة - Safe default value
        "imagery_date": "2026-01-01",
        "cloud_coverage": 0,
        "source": "cached_imagery",
        "message": "استخدام آخر صور متاحة - Using last available imagery"
    }

satellite_fm.register_fallback(
    "satellite_ndvi",
    satellite_fallback_custom,
    failure_threshold=3,
    recovery_timeout=60
)

def get_satellite_ndvi(field_id: str) -> Dict[str, Any]:
    """
    الحصول على NDVI من الأقمار الصناعية
    Get NDVI from satellite
    """
    # محاكاة فشل - Simulate failure
    if random.random() < 0.5:
        raise Exception("Satellite imagery not available")

    return {
        "field_id": field_id,
        "ndvi": random.uniform(0.3, 0.9),
        "imagery_date": datetime.now().isoformat(),
        "cloud_coverage": random.randint(0, 30),
        "source": "sentinel-2"
    }

print("\nطلب NDVI لـ 3 حقول - Request NDVI for 3 fields:")
for field_id in ["F001", "F002", "F003"]:
    result = satellite_fm.execute_with_fallback(
        "satellite_ndvi",
        get_satellite_ndvi,
        field_id=field_id
    )
    print(f"  {field_id}: NDVI={result['ndvi']:.2f}, المصدر - Source={result['source']}")


# ===== مثال 3: استخدام الديكوريتورز - Example 3: Using Decorators =====

print("\n" + "="*60)
print("مثال 3: استخدام الديكوريتورز - Example 3: Using Decorators")
print("="*60)

def ai_recommendations_fallback(field_id: str, crop_type: str) -> Dict[str, Any]:
    """
    توصيات احتياطية مبنية على القواعد
    Rule-based fallback recommendations
    """
    return {
        "field_id": field_id,
        "crop_type": crop_type,
        "recommendations": [
            {
                "type": "irrigation",
                "priority": "medium",
                "message_ar": "تحقق من مستوى رطوبة التربة",
                "message_en": "Check soil moisture level"
            },
            {
                "type": "monitoring",
                "priority": "low",
                "message_ar": "راقب نمو المحصول بانتظام",
                "message_en": "Monitor crop growth regularly"
            }
        ],
        "confidence": 0.4,
        "source": "rule_based"
    }

@with_fallback(ai_recommendations_fallback)
@circuit_breaker(failure_threshold=4, recovery_timeout=30)
def get_ai_recommendations(field_id: str, crop_type: str) -> Dict[str, Any]:
    """
    الحصول على توصيات الذكاء الاصطناعي
    Get AI recommendations
    """
    # محاكاة استدعاء AI - Simulate AI call
    if random.random() < 0.4:
        raise Exception("AI service temporarily unavailable")

    return {
        "field_id": field_id,
        "crop_type": crop_type,
        "recommendations": [
            {
                "type": "fertilizer",
                "priority": "high",
                "message_ar": f"أضف سماد نيتروجيني للـ{crop_type}",
                "message_en": f"Add nitrogen fertilizer for {crop_type}"
            }
        ],
        "confidence": 0.92,
        "source": "ai_model_v2"
    }

print("\nطلب توصيات AI لحقول مختلفة - Request AI recommendations:")
for i in range(3):
    result = get_ai_recommendations(f"F{i+1}", "قمح - Wheat")
    print(f"  الحقل - Field F{i+1}:")
    print(f"    المصدر - Source: {result['source']}")
    print(f"    الثقة - Confidence: {result['confidence']}")
    print(f"    التوصيات - Recommendations: {len(result['recommendations'])}")

# عرض حالة قاطع الدائرة - Show circuit breaker status
cb_status = get_ai_recommendations.circuit_breaker.get_status()
print(f"\n  حالة قاطع الدائرة - Circuit status: {cb_status['state']}")


# ===== مثال 4: تنسيق متعدد الخدمات - Example 4: Multi-Service Orchestration =====

print("\n" + "="*60)
print("مثال 4: تحليل شامل للحقل - Example 4: Comprehensive Field Analysis")
print("="*60)

def get_comprehensive_field_analysis(field_id: str) -> Dict[str, Any]:
    """
    تحليل شامل يجمع بيانات من خدمات متعددة
    Comprehensive analysis combining multiple services
    """
    fm = get_fallback_manager()

    analysis = {
        "field_id": field_id,
        "timestamp": datetime.now().isoformat(),
        "services_status": {}
    }

    # 1. بيانات الطقس - Weather data
    try:
        weather = fm.execute_with_fallback(
            "weather",
            lambda: weather_api_call("صنعاء")
        )
        analysis["weather"] = weather
        analysis["services_status"]["weather"] = "success"
    except Exception as e:
        analysis["services_status"]["weather"] = f"failed: {str(e)}"

    # 2. بيانات الأقمار الصناعية - Satellite data
    try:
        satellite = fm.execute_with_fallback(
            "satellite",
            lambda: {"ndvi": 0.75, "imagery_date": datetime.now().isoformat()}
        )
        analysis["satellite"] = satellite
        analysis["services_status"]["satellite"] = "success"
    except Exception as e:
        analysis["services_status"]["satellite"] = f"failed: {str(e)}"

    # 3. توصيات الذكاء الاصطناعي - AI recommendations
    try:
        ai = fm.execute_with_fallback(
            "ai",
            lambda: {"recommendations": ["Monitor irrigation"], "confidence": 0.85}
        )
        analysis["ai"] = ai
        analysis["services_status"]["ai"] = "success"
    except Exception as e:
        analysis["services_status"]["ai"] = f"failed: {str(e)}"

    return analysis

# تنفيذ التحليل الشامل - Execute comprehensive analysis
print("\nتحليل الحقل F123 - Analyzing field F123:")
field_analysis = get_comprehensive_field_analysis("F123")

print(f"  الطابع الزمني - Timestamp: {field_analysis['timestamp']}")
print(f"  حالة الخدمات - Services Status:")
for service, status in field_analysis["services_status"].items():
    icon = "✅" if status == "success" else "⚠️"
    print(f"    {icon} {service}: {status}")


# ===== مثال 5: اختبار انتقالات الحالة - Example 5: State Transitions =====

print("\n" + "="*60)
print("مثال 5: اختبار انتقالات حالة الدائرة - Example 5: Circuit State Transitions")
print("="*60)

test_fm = FallbackManager()

def test_fallback():
    return {"status": "fallback_data"}

test_fm.register_fallback(
    "test_service",
    test_fallback,
    failure_threshold=3,
    recovery_timeout=2
)

failure_count = {"count": 0}

def flaky_service():
    """خدمة غير مستقرة - Flaky service"""
    failure_count["count"] += 1

    if failure_count["count"] <= 3:
        raise Exception(f"Failure {failure_count['count']}")
    return {"status": "success", "attempt": failure_count["count"]}

print("\nاختبار تسلسل: CLOSED → OPEN → HALF_OPEN → CLOSED")
print("Testing sequence: CLOSED → OPEN → HALF_OPEN → CLOSED\n")

# محاولات تفشل (CLOSED → OPEN) - Failing attempts (CLOSED → OPEN)
for i in range(3):
    result = test_fm.execute_with_fallback("test_service", flaky_service)
    status = test_fm.get_circuit_status("test_service")
    print(f"  محاولة {i+1} - Attempt {i+1}: الحالة - State={status['state']}, الفشل - Failures={status['failure_count']}")

print(f"\n  ⏸️  الدائرة الآن مفتوحة - Circuit is now OPEN")
print(f"  ⏳ الانتظار {2} ثانية للاستعادة - Waiting 2 seconds for recovery...")
time.sleep(2.1)

# محاولة بعد الاستعادة (OPEN → HALF_OPEN → CLOSED) - Attempt after recovery
print(f"\n  🔄 محاولة بعد الاستعادة - Attempting after recovery:")
result = test_fm.execute_with_fallback("test_service", flaky_service)
status = test_fm.get_circuit_status("test_service")
print(f"  الحالة - State: {status['state']}")
print(f"  النتيجة - Result: {result}")


# ===== مثال 6: مراقبة الصحة - Example 6: Health Monitoring =====

print("\n" + "="*60)
print("مثال 6: مراقبة صحة الخدمات - Example 6: Service Health Monitoring")
print("="*60)

def generate_health_report() -> Dict[str, Any]:
    """
    توليد تقرير صحة شامل
    Generate comprehensive health report
    """
    fm = get_fallback_manager()
    all_statuses = fm.get_all_statuses()

    healthy = []
    degraded = []
    failed = []

    for service, status in all_statuses.items():
        if status['state'] == 'closed' and status['failure_count'] == 0:
            healthy.append(service)
        elif status['state'] == 'open':
            failed.append(service)
        else:
            degraded.append(service)

    overall_health = "healthy"
    if failed:
        overall_health = "critical"
    elif degraded:
        overall_health = "degraded"

    return {
        "timestamp": datetime.now().isoformat(),
        "overall_health": overall_health,
        "healthy_services": healthy,
        "degraded_services": degraded,
        "failed_services": failed,
        "total_services": len(all_statuses),
        "details": all_statuses
    }

health_report = generate_health_report()
print(f"\n📊 تقرير صحة الخدمات - Service Health Report:")
print(f"  الحالة العامة - Overall Health: {health_report['overall_health'].upper()}")
print(f"  إجمالي الخدمات - Total Services: {health_report['total_services']}")
print(f"  ✅ سليمة - Healthy: {len(health_report['healthy_services'])}")
print(f"  ⚠️  متدهورة - Degraded: {len(health_report['degraded_services'])}")
print(f"  ❌ فاشلة - Failed: {len(health_report['failed_services'])}")

if health_report['healthy_services']:
    print(f"\n  الخدمات السليمة - Healthy Services: {', '.join(health_report['healthy_services'])}")


# ===== مثال 7: إعادة تعيين يدوية - Example 7: Manual Reset =====

print("\n" + "="*60)
print("مثال 7: إعادة تعيين يدوية للدائرة - Example 7: Manual Circuit Reset")
print("="*60)

reset_fm = FallbackManager()
reset_fm.register_fallback("test_reset", lambda: {"reset": True}, failure_threshold=2)

def always_fails():
    raise Exception("Always fails")

# فتح الدائرة - Open the circuit
for i in range(2):
    try:
        reset_fm.execute_with_fallback("test_reset", always_fails)
    except:
        pass

status_before = reset_fm.get_circuit_status("test_reset")
print(f"\n  قبل إعادة التعيين - Before reset:")
print(f"    الحالة - State: {status_before['state']}")
print(f"    الفشل - Failures: {status_before['failure_count']}")

# إعادة تعيين يدوية - Manual reset
print(f"\n  🔧 إعادة تعيين الدائرة - Resetting circuit...")
reset_fm.reset_circuit("test_reset")

status_after = reset_fm.get_circuit_status("test_reset")
print(f"\n  بعد إعادة التعيين - After reset:")
print(f"    الحالة - State: {status_after['state']}")
print(f"    الفشل - Failures: {status_after['failure_count']}")


# ===== الخلاصة - Summary =====

print("\n" + "="*60)
print("✅ اكتملت جميع الأمثلة بنجاح - All Examples Completed Successfully")
print("="*60)

print("""
الميزات المثبتة - Demonstrated Features:
  ✅ قاطع الدائرة بثلاث حالات - Circuit breaker with 3 states
  ✅ التنفيذ التلقائي للاحتياطي - Automatic fallback execution
  ✅ التخزين المؤقت للنتائج - Result caching
  ✅ الديكوريتورز - Decorators
  ✅ تنسيق متعدد الخدمات - Multi-service orchestration
  ✅ انتقالات الحالة - State transitions
  ✅ مراقبة الصحة - Health monitoring
  ✅ إعادة التعيين اليدوية - Manual reset

للمزيد من المعلومات، راجع README.md
For more information, see README.md
""")
