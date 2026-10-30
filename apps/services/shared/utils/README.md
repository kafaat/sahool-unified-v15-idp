# SAHOOL API Fallback Manager with Circuit Breaker

# مدير الاحتياطي لواجهات برمجة التطبيقات مع نمط قاطع الدائرة

A robust fallback mechanism for API calls with circuit breaker pattern to prevent cascading failures and improve system resilience.

آلية احتياطية قوية لاستدعاءات واجهة برمجة التطبيقات مع نمط قاطع الدائرة لمنع الفشل المتتالي وتحسين مرونة النظام.

## Features / الميزات

### Circuit Breaker Pattern / نمط قاطع الدائرة

- ✅ **Three States**: CLOSED, OPEN, HALF_OPEN
- ✅ **Configurable Thresholds**: Customize failure/success thresholds
- ✅ **Automatic Recovery**: Auto-transition to testing mode after timeout
- ✅ **Thread-Safe**: Safe for concurrent operations

### Fallback Management / إدارة الاحتياطي

- ✅ **Service Registration**: Register fallback functions per service
- ✅ **Automatic Caching**: Cache successful responses
- ✅ **Multi-Level Fallback**: Primary → Fallback → Cache
- ✅ **Status Monitoring**: Real-time circuit status tracking

### Built-in Service Fallbacks / احتياطيات الخدمات المدمجة

- 🌤️ **Weather Service**: Returns cached or default weather data
- 🛰️ **Satellite Service**: Returns cached imagery or unavailable status
- 🤖 **AI Service**: Returns rule-based recommendations
- 🌱 **Crop Health Service**: Returns default health status
- 💧 **Irrigation Service**: Returns conservative irrigation recommendations

## Installation / التثبيت

```python
# Import the module
from shared.utils.fallback_manager import (
    FallbackManager,
    CircuitBreaker,
    circuit_breaker,
    with_fallback,
    get_fallback_manager,
)
```

## Quick Start / البداية السريعة

### Using Global Fallback Manager / استخدام مدير الاحتياطي العام

```python
from shared.utils.fallback_manager import get_fallback_manager

# Get global instance / الحصول على النسخة العامة
fm = get_fallback_manager()


# Execute with fallback / تنفيذ مع احتياطي
def get_weather_from_api():
    # Call external weather API
    response = requests.get("https://api.weather.com/data")
    return response.json()


# Automatically uses weather_fallback on failure
result = fm.execute_with_fallback("weather", get_weather_from_api)
```

### Creating Custom Fallback Manager / إنشاء مدير احتياطي مخصص

```python
from shared.utils.fallback_manager import FallbackManager

# Create manager / إنشاء المدير
fm = FallbackManager()


# Define fallback function / تعريف دالة احتياطية
def my_service_fallback(*args, **kwargs):
    return {"status": "fallback", "data": "Default data", "source": "fallback"}


# Register service / تسجيل الخدمة
fm.register_fallback(
    service_name="my_service",
    fallback_fn=my_service_fallback,
    failure_threshold=5,  # 5 failures before opening circuit
    recovery_timeout=30,  # 30 seconds before retry
    success_threshold=3,  # 3 successes to close circuit
)


# Execute / تنفيذ
def primary_function():
    # Your primary logic here
    return call_external_api()


result = fm.execute_with_fallback("my_service", primary_function)
```

## Using Decorators / استخدام الديكوريتورز

### Circuit Breaker Decorator / ديكوريتور قاطع الدائرة

```python
from shared.utils.fallback_manager import circuit_breaker


@circuit_breaker(failure_threshold=5, recovery_timeout=30)
def call_satellite_api():
    """
    Automatically protected by circuit breaker
    محمي تلقائياً بقاطع الدائرة
    """
    response = requests.get("https://api.satellite.com/imagery")
    return response.json()


# Call normally / استدعاء عادي
try:
    data = call_satellite_api()
except Exception as e:
    print(f"Circuit is open or call failed: {e}")

# Access circuit breaker / الوصول إلى قاطع الدائرة
status = call_satellite_api.circuit_breaker.get_status()
print(f"Circuit State: {status['state']}")
```

### Fallback Decorator / ديكوريتور الاحتياطي

```python
from shared.utils.fallback_manager import with_fallback


def fallback_crop_data():
    return {"crop": "unknown", "health": 50.0, "source": "fallback"}


@with_fallback(fallback_crop_data)
def get_crop_health(field_id):
    """
    Falls back to fallback_crop_data on failure
    يستخدم fallback_crop_data عند الفشل
    """
    response = requests.get(f"https://api.crop-health.com/field/{field_id}")
    return response.json()


# Automatically uses fallback on error
data = get_crop_health("field_123")
```

### Combining Decorators / دمج الديكوريتورز

```python
from shared.utils.fallback_manager import circuit_breaker, with_fallback


def ai_fallback():
    return {"recommendations": [], "source": "fallback"}


@with_fallback(ai_fallback)
@circuit_breaker(failure_threshold=5, recovery_timeout=60)
def get_ai_recommendations(field_id):
    """
    Protected by both circuit breaker and fallback
    محمي بقاطع الدائرة والاحتياطي معاً
    """
    response = requests.post("https://api.ai-advisor.com/recommend", json={"field_id": field_id})
    return response.json()


# Fully protected call
recommendations = get_ai_recommendations("field_123")
```

## Circuit Breaker States / حالات قاطع الدائرة

### CLOSED (مغلق)

- Normal operation / العمليات الطبيعية
- All requests are allowed / جميع الطلبات مسموحة
- Counts failures / يحسب الفشل

### OPEN (مفتوح)

- Circuit is broken / الدائرة معطلة
- All requests fail immediately / جميع الطلبات تفشل فوراً
- Waits for recovery timeout / ينتظر مهلة الاستعادة

### HALF_OPEN (نصف مفتوح)

- Testing mode / وضع الاختبار
- Limited requests allowed / طلبات محدودة مسموحة
- Transitions to CLOSED on success / ينتقل إلى مغلق عند النجاح
- Transitions to OPEN on failure / ينتقل إلى مفتوح عند الفشل

## State Transition Flow / تدفق انتقال الحالات

```
CLOSED ──(5 failures)──> OPEN ──(30 seconds)──> HALF_OPEN
   ↑                                                 │
   │                                                 │
   └────────────(3 successes)────────────────────────┘

HALF_OPEN ──(1 failure)──> OPEN
```

## Monitoring Circuit Status / مراقبة حالة الدائرة

```python
from shared.utils.fallback_manager import get_fallback_manager

fm = get_fallback_manager()

# Get status for specific service / الحصول على حالة خدمة معينة
weather_status = fm.get_circuit_status("weather")
print(f"""
State: {weather_status["state"]}
Failures: {weather_status["failure_count"]}/{weather_status["failure_threshold"]}
Successes: {weather_status["success_count"]}/{weather_status["success_threshold"]}
Time until retry: {weather_status["time_until_retry"]} seconds
""")

# Get all statuses / الحصول على جميع الحالات
all_statuses = fm.get_all_statuses()
for service, status in all_statuses.items():
    print(f"{service}: {status['state']}")
```

## Manual Circuit Reset / إعادة تعيين الدائرة يدوياً

```python
from shared.utils.fallback_manager import get_fallback_manager

fm = get_fallback_manager()

# Reset specific circuit / إعادة تعيين دائرة معينة
fm.reset_circuit("weather")

# Or reset from decorator / أو إعادة التعيين من الديكوريتور
call_satellite_api.circuit_breaker.reset()
```

## Advanced Usage Examples / أمثلة الاستخدام المتقدم

### Custom Service with Caching / خدمة مخصصة مع التخزين المؤقت

```python
from shared.utils.fallback_manager import FallbackManager
import requests

fm = FallbackManager()


def ndvi_fallback(field_id):
    """Returns cached NDVI or default value"""
    return {"ndvi": 0.5, "field_id": field_id, "source": "fallback", "message": "Using default NDVI value"}


fm.register_fallback("ndvi", ndvi_fallback, failure_threshold=3)


def get_ndvi(field_id):
    """Primary NDVI calculation"""
    response = requests.get(f"https://api.satellite.com/ndvi/{field_id}")
    if response.status_code != 200:
        raise Exception("NDVI API failed")
    return response.json()


# First call - success, result is cached
ndvi_data = fm.execute_with_fallback("ndvi", get_ndvi, field_id="F123")

# If next calls fail and fallback fails, uses cached result
ndvi_data = fm.execute_with_fallback("ndvi", get_ndvi, field_id="F123")
```

### Multi-Service Orchestration / تنسيق متعدد الخدمات

```python
from shared.utils.fallback_manager import get_fallback_manager

fm = get_fallback_manager()


def get_field_analysis(field_id):
    """
    Combines multiple services with individual circuit breakers
    يدمج خدمات متعددة مع قواطع دائرة فردية
    """
    results = {}

    # Weather data with fallback
    results["weather"] = fm.execute_with_fallback("weather", lambda: get_weather_api(field_id))

    # Satellite data with fallback
    results["satellite"] = fm.execute_with_fallback("satellite", lambda: get_satellite_api(field_id))

    # AI recommendations with fallback
    results["ai"] = fm.execute_with_fallback("ai", lambda: get_ai_recommendations_api(field_id))

    return results


# Even if some services fail, you get partial results
analysis = get_field_analysis("field_123")
```

### Health Check Endpoint / نقطة فحص الصحة

```python
from flask import Flask, jsonify
from shared.utils.fallback_manager import get_fallback_manager

app = Flask(__name__)
fm = get_fallback_manager()


@app.route("/health/circuits")
def circuit_health():
    """
    Returns circuit breaker status for all services
    يرجع حالة قواطع الدائرة لجميع الخدمات
    """
    all_statuses = fm.get_all_statuses()

    healthy_services = [name for name, status in all_statuses.items() if status["state"] == "closed"]

    degraded_services = [name for name, status in all_statuses.items() if status["state"] in ["open", "half_open"]]

    return jsonify(
        {
            "status": "healthy" if not degraded_services else "degraded",
            "healthy_services": healthy_services,
            "degraded_services": degraded_services,
            "details": all_statuses,
        }
    )
```

## Configuration Guide / دليل التكوين

### Choosing Thresholds / اختيار العتبات

**failure_threshold** (عتبة الفشل):

- **Low (3-5)**: For critical services that should fail fast
- **Medium (5-10)**: For standard services
- **High (10+)**: For services with expected intermittent failures

**recovery_timeout** (مهلة الاستعادة):

- **Short (10-30s)**: For services that recover quickly
- **Medium (30-60s)**: Standard recovery time
- **Long (60-300s)**: For services with slow recovery

**success_threshold** (عتبة النجاح):

- **Low (2-3)**: Quick recovery verification
- **Medium (3-5)**: Standard verification
- **High (5+)**: Conservative recovery verification

### Example Configurations / أمثلة التكوين

```python
# Critical service - fail fast / خدمة حرجة - فشل سريع
fm.register_fallback("payment_gateway", payment_fallback, failure_threshold=3, recovery_timeout=60, success_threshold=5)

# Standard service / خدمة عادية
fm.register_fallback("weather", weather_fallback, failure_threshold=5, recovery_timeout=30, success_threshold=3)

# Flaky service / خدمة غير مستقرة
fm.register_fallback(
    "external_sensor", sensor_fallback, failure_threshold=10, recovery_timeout=120, success_threshold=3
)
```

## Testing / الاختبار

Run the test suite:

```bash
cd /home/user/sahool-unified-v15-idp/apps/services/shared/utils
python3 -m pytest tests/test_fallback_manager.py -v
```

## Best Practices / أفضل الممارسات

1. **Always register fallbacks** for critical services
   سجل دائماً احتياطيات للخدمات الحرجة

2. **Use appropriate thresholds** based on service characteristics
   استخدم عتبات مناسبة بناءً على خصائص الخدمة

3. **Monitor circuit status** in production
   راقب حالة الدائرة في الإنتاج

4. **Implement meaningful fallbacks** rather than just returning None
   نفذ احتياطيات ذات معنى بدلاً من إرجاع None فقط

5. **Log all circuit transitions** for debugging
   سجل جميع انتقالات الدائرة للتصحيح

6. **Test fallback paths** regularly
   اختبر مسارات الاحتياطي بانتظام

7. **Cache successful responses** for critical data
   خزن الاستجابات الناجحة للبيانات الحرجة

8. **Use global manager** for consistent behavior
   استخدم المدير العام للسلوك المتسق

## Performance Considerations / اعتبارات الأداء

- Circuit breaker operations are **thread-safe** using locks
- Caching is enabled by default with **5-minute TTL**
- Minimal overhead when circuit is CLOSED
- No external dependencies required

## Architecture / البنية

```
FallbackManager
├── Circuit Breakers (per service)
│   ├── State Management (CLOSED/OPEN/HALF_OPEN)
│   ├── Failure Counting
│   └── Recovery Timer
├── Fallback Functions (per service)
├── Cache Layer (with TTL)
└── Thread Safety (Locks)
```

## API Reference / مرجع واجهة برمجة التطبيقات

### FallbackManager

#### `register_fallback(service_name, fallback_fn, failure_threshold=5, recovery_timeout=30, success_threshold=3)`

Register a fallback function for a service.

#### `execute_with_fallback(service_name, primary_fn, *args, **kwargs)`

Execute function with fallback protection.

#### `get_circuit_status(service_name)`

Get current circuit breaker status.

#### `reset_circuit(service_name)`

Manually reset circuit breaker.

#### `get_all_statuses()`

Get status of all circuit breakers.

### CircuitBreaker

#### `call(func, *args, **kwargs)`

Execute function with circuit breaker protection.

#### `reset()`

Manually reset the circuit.

#### `get_status()`

Get current status.

### Decorators

#### `@circuit_breaker(failure_threshold, recovery_timeout, success_threshold)`

Protect function with circuit breaker.

#### `@with_fallback(fallback_fn)`

Provide fallback function for failures.

## Troubleshooting / استكشاف الأخطاء

### Circuit stuck in OPEN state

- Check if recovery_timeout is too long
- Verify the service is actually available
- Manually reset: `fm.reset_circuit(service_name)`

### Fallback not being called

- Ensure fallback is registered: `fm.register_fallback(...)`
- Check circuit is not in OPEN state before registration
- Verify primary function is actually failing

### Cache not working

- Check cache TTL (default 5 minutes)
- Ensure successful call was made first
- Verify service name matches

## License / الترخيص

Part of SAHOOL Unified Agricultural Platform
جزء من منصة سهول الزراعية الموحدة

## Support / الدعم

For issues and questions:

- GitHub Issues: [sahool-unified-v15-idp]
- Email: support@sahool.com

---

Made with ❤️ for Yemeni Farmers
صُنع بـ ❤️ للمزارعين اليمنيين
