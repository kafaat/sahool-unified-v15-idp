# Fallback Manager Integration Guide for SAHOOL Services

# دليل دمج مدير الاحتياطي لخدمات سهول

Quick guide for integrating the Fallback Manager into existing SAHOOL microservices.

دليل سريع لدمج مدير الاحتياطي في خدمات سهول الصغرى الموجودة.

## Quick Integration Steps / خطوات الدمج السريعة

### 1. Import the Module / استيراد الوحدة

Add to your service's main file:

```python
from shared.utils.fallback_manager import (
    get_fallback_manager,
    circuit_breaker,
    with_fallback
)
```

### 2. Choose Integration Pattern / اختيار نمط الدمج

You have three options:

#### Option A: Use Global Manager (Recommended) / استخدام المدير العام (موصى به)

Best for: Weather, Satellite, AI, Crop Health, Irrigation services

```python
from shared.utils.fallback_manager import get_fallback_manager

fm = get_fallback_manager()

# Already configured fallbacks for common services!
# احتياطيات مُكونة مسبقاً للخدمات الشائعة!

@app.route('/api/weather/<location>')
def get_weather(location):
    def primary_weather_call():
        return call_external_weather_api(location)

    # Automatically uses weather_fallback on failure
    result = fm.execute_with_fallback("weather", primary_weather_call)
    return jsonify(result)
```

#### Option B: Use Decorators / استخدام الديكوريتورز

Best for: Individual functions that need protection

```python
from shared.utils.fallback_manager import circuit_breaker, with_fallback

def my_fallback():
    return {"status": "unavailable", "data": None}

@with_fallback(my_fallback)
@circuit_breaker(failure_threshold=5, recovery_timeout=30)
def get_satellite_imagery(field_id):
    response = requests.get(f"{SATELLITE_API}/imagery/{field_id}")
    return response.json()
```

#### Option C: Create Custom Manager / إنشاء مدير مخصص

Best for: Services with unique requirements

```python
from shared.utils.fallback_manager import FallbackManager

# Create service-specific manager
my_fm = FallbackManager()

# Register custom fallback
my_fm.register_fallback(
    "my_service",
    my_custom_fallback,
    failure_threshold=3,
    recovery_timeout=60
)
```

## Service-Specific Integration Examples / أمثلة دمج خاصة بالخدمات

### Weather Service Integration / دمج خدمة الطقس

**File**: `apps/services/weather-service/app/main.py`

```python
from flask import Flask, jsonify
from shared.utils.fallback_manager import get_fallback_manager
import requests

app = Flask(__name__)
fm = get_fallback_manager()

@app.route('/api/weather/<location>')
def get_weather(location):
    """
    Weather endpoint with automatic fallback
    نقطة نهاية الطقس مع احتياطي تلقائي
    """
    def fetch_weather():
        response = requests.get(
            f"https://api.openweathermap.org/data/2.5/weather",
            params={"q": location, "appid": API_KEY}
        )
        response.raise_for_status()
        return response.json()

    try:
        # Uses weather_fallback if API fails
        data = fm.execute_with_fallback("weather", fetch_weather)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 503

@app.route('/health/circuit')
def circuit_status():
    """Health check endpoint for circuit breaker"""
    status = fm.get_circuit_status("weather")
    return jsonify(status)
```

### Satellite Service Integration / دمج خدمة الأقمار الصناعية

**File**: `apps/services/satellite-service/app/main.py`

```python
from shared.utils.fallback_manager import get_fallback_manager
import requests

fm = get_fallback_manager()

class SatelliteService:
    def get_ndvi(self, field_id: str):
        """
        Get NDVI with fallback protection
        الحصول على NDVI مع حماية احتياطية
        """
        def fetch_ndvi():
            response = requests.get(f"{SATELLITE_API}/ndvi/{field_id}")
            response.raise_for_status()
            return response.json()

        # Uses satellite_fallback on failure
        return fm.execute_with_fallback("satellite", fetch_ndvi)

    def get_circuit_health(self):
        """Check if satellite service circuit is healthy"""
        status = fm.get_circuit_status("satellite")
        return status['state'] == 'closed'
```

### AI Advisor Service Integration / دمج خدمة مستشار الذكاء الاصطناعي

**File**: `apps/services/ai-advisor/app/main.py`

```python
from shared.utils.fallback_manager import get_fallback_manager
import requests

fm = get_fallback_manager()

class AIAdvisorService:
    def get_recommendations(self, field_id: str, crop_type: str):
        """
        Get AI recommendations with rule-based fallback
        الحصول على توصيات AI مع احتياطي قائم على القواعد
        """
        def fetch_ai_recommendations():
            response = requests.post(
                f"{AI_API}/recommendations",
                json={"field_id": field_id, "crop_type": crop_type}
            )
            response.raise_for_status()
            return response.json()

        # Uses ai_fallback (rule-based) on failure
        return fm.execute_with_fallback("ai", fetch_ai_recommendations)
```

### Crop Health Service Integration / دمج خدمة صحة المحاصيل

**File**: `apps/services/crop-health/app/main.py`

```python
from shared.utils.fallback_manager import get_fallback_manager, circuit_breaker

fm = get_fallback_manager()

@circuit_breaker(failure_threshold=5, recovery_timeout=45)
def analyze_crop_health(field_id: str):
    """
    Analyze crop health with circuit breaker
    تحليل صحة المحصول مع قاطع الدائرة
    """
    # Complex analysis that might fail
    ndvi_data = get_ndvi_analysis(field_id)
    weather_data = get_weather_analysis(field_id)

    # Combine and analyze
    health_score = calculate_health_score(ndvi_data, weather_data)
    return {
        "field_id": field_id,
        "health_score": health_score,
        "status": "healthy" if health_score > 70 else "needs_attention"
    }

# Access circuit breaker status
def get_analysis_circuit_status():
    return analyze_crop_health.circuit_breaker.get_status()
```

### Custom Service with Custom Fallback / خدمة مخصصة مع احتياطي مخصص

**File**: `apps/services/my-service/app/main.py`

```python
from shared.utils.fallback_manager import FallbackManager

# Create service-specific manager
fm = FallbackManager()

# Define custom fallback
def my_custom_fallback(param1, param2):
    """Return safe default values"""
    return {
        "param1": param1,
        "param2": param2,
        "result": "default_value",
        "source": "fallback",
        "confidence": 0.0
    }

# Register the fallback
fm.register_fallback(
    "my_service",
    my_custom_fallback,
    failure_threshold=3,
    recovery_timeout=30
)

# Use it
def process_request(param1, param2):
    def primary_processing():
        # Your complex logic here
        return complex_api_call(param1, param2)

    return fm.execute_with_fallback(
        "my_service",
        primary_processing,
        param1,
        param2
    )
```

## Health Check Integration / دمج فحص الصحة

Add circuit breaker health checks to your service:

```python
from flask import Flask, jsonify
from shared.utils.fallback_manager import get_fallback_manager

app = Flask(__name__)
fm = get_fallback_manager()

@app.route('/health')
def health_check():
    """
    Standard health check with circuit breaker status
    فحص الصحة القياسي مع حالة قاطع الدائرة
    """
    all_statuses = fm.get_all_statuses()

    degraded_circuits = [
        name for name, status in all_statuses.items()
        if status['state'] != 'closed'
    ]

    return jsonify({
        "status": "degraded" if degraded_circuits else "healthy",
        "circuits": all_statuses,
        "degraded": degraded_circuits
    }), 200 if not degraded_circuits else 503

@app.route('/admin/circuits/reset/<service_name>', methods=['POST'])
def reset_circuit(service_name):
    """
    Admin endpoint to manually reset a circuit
    نقطة نهاية الإدارة لإعادة تعيين الدائرة يدوياً
    """
    fm.reset_circuit(service_name)
    return jsonify({
        "message": f"Circuit {service_name} reset successfully"
    })
```

## Docker Compose Integration / دمج Docker Compose

Add environment variables for circuit breaker configuration:

```yaml
services:
  weather-service:
    environment:
      - CIRCUIT_BREAKER_ENABLED=true
      - WEATHER_FAILURE_THRESHOLD=5
      - WEATHER_RECOVERY_TIMEOUT=30
```

Then in your service:

```python
import os

# Configure based on environment
CIRCUIT_ENABLED = os.getenv('CIRCUIT_BREAKER_ENABLED', 'true') == 'true'
FAILURE_THRESHOLD = int(os.getenv('WEATHER_FAILURE_THRESHOLD', '5'))
RECOVERY_TIMEOUT = int(os.getenv('WEATHER_RECOVERY_TIMEOUT', '30'))

if CIRCUIT_ENABLED:
    fm.register_fallback(
        "weather",
        weather_fallback,
        failure_threshold=FAILURE_THRESHOLD,
        recovery_timeout=RECOVERY_TIMEOUT
    )
```

## Monitoring and Logging / المراقبة والتسجيل

The fallback manager logs important events automatically:

- `INFO`: Circuit breaker state transitions
- `WARNING`: Failures and fallback usage
- `ERROR`: Critical failures and circuit opening

Example log output:

```
INFO:fallback_manager:✅ تم تسجيل احتياطي للخدمة - Registered fallback for: weather
WARNING:fallback_manager:فشل مسجل - Failure recorded: 3/5
ERROR:fallback_manager:⚠️ الدائرة مفتوحة الآن - Circuit is now OPEN. فشل 5 مرات
INFO:fallback_manager:🔄 الدائرة في وضع نصف مفتوح - Circuit is now HALF_OPEN
INFO:fallback_manager:✅ الدائرة مغلقة - Circuit is now CLOSED
```

## Testing Your Integration / اختبار التكامل

Create tests to verify fallback behavior:

```python
import pytest
from unittest.mock import patch

def test_weather_with_fallback(app):
    """Test weather service uses fallback on API failure"""

    with patch('requests.get') as mock_get:
        # Simulate API failure
        mock_get.side_effect = Exception("API timeout")

        response = app.get('/api/weather/Sanaa')

        # Should return fallback data, not error
        assert response.status_code == 200
        data = response.json()
        assert data['source'] == 'fallback'

def test_circuit_opens_after_failures(app):
    """Test circuit opens after threshold failures"""

    with patch('requests.get') as mock_get:
        mock_get.side_effect = Exception("API timeout")

        # Trigger 5 failures
        for _ in range(5):
            app.get('/api/weather/Sanaa')

        # Check circuit is open
        status = app.get('/health/circuit').json()
        assert status['state'] == 'open'
```

## Best Practices / أفضل الممارسات

### 1. Use Global Manager for Standard Services / استخدم المدير العام للخدمات القياسية

```python
# ✅ Good - Uses pre-configured fallback
fm = get_fallback_manager()
fm.execute_with_fallback("weather", fetch_weather)

# ❌ Avoid - Reinventing the wheel
fm = FallbackManager()
fm.register_fallback("weather", my_weather_fallback)
```

### 2. Always Provide Meaningful Fallbacks / وفر دائماً احتياطيات ذات معنى

```python
# ✅ Good - Meaningful fallback
def weather_fallback():
    return {
        "temperature": 25.0,
        "condition": "unknown",
        "source": "fallback",
        "message": "Using default data - Check manually"
    }

# ❌ Avoid - Useless fallback
def weather_fallback():
    return None
```

### 3. Configure Thresholds Based on Service Characteristics

```python
# ✅ Good - Critical service, fail fast
fm.register_fallback("payment", payment_fallback,
                     failure_threshold=3, recovery_timeout=60)

# ✅ Good - Non-critical service, more tolerant
fm.register_fallback("analytics", analytics_fallback,
                     failure_threshold=10, recovery_timeout=30)
```

### 4. Monitor Circuit Status in Production

```python
# ✅ Good - Regular monitoring
@app.route('/metrics')
def metrics():
    statuses = fm.get_all_statuses()
    open_circuits = [k for k, v in statuses.items() if v['state'] == 'open']

    # Alert if circuits are open
    if open_circuits:
        logger.warning(f"Open circuits: {open_circuits}")

    return jsonify(statuses)
```

### 5. Test Fallback Paths Regularly

```python
# ✅ Good - Test fallback paths
def test_fallback_path():
    """Ensure fallback returns valid data"""
    result = weather_fallback()
    assert 'temperature' in result
    assert 'condition' in result
```

## Troubleshooting Common Issues / حل المشكلات الشائعة

### Issue: Fallback not being called / المشكلة: لا يتم استدعاء الاحتياطي

**Solution**: Ensure fallback is registered before use

```python
# Register before using
fm.register_fallback("my_service", my_fallback)

# Then use
fm.execute_with_fallback("my_service", primary_fn)
```

### Issue: Circuit stuck in OPEN / المشكلة: الدائرة عالقة في OPEN

**Solution**: Check recovery_timeout or manually reset

```python
# Option 1: Wait for timeout
time.sleep(recovery_timeout)

# Option 2: Manual reset
fm.reset_circuit("service_name")
```

### Issue: Too many failures / المشكلة: فشل كثير جداً

**Solution**: Adjust failure_threshold

```python
# Increase threshold for flaky services
fm.register_fallback("flaky_service", fallback,
                     failure_threshold=10)  # Was 5
```

## Performance Considerations / اعتبارات الأداء

- Circuit breaker adds **minimal overhead** (~0.1ms per call)
- Thread-safe operations use locks (may block briefly)
- Caching reduces load on fallback functions
- Default cache TTL is 5 minutes

## Migration Guide / دليل الانتقال

### Migrating Existing Try-Catch Blocks / نقل كتل Try-Catch الموجودة

**Before**:

```python
def get_weather(location):
    try:
        return call_weather_api(location)
    except Exception:
        return {"temperature": 25, "condition": "unknown"}
```

**After**:

```python
from shared.utils.fallback_manager import get_fallback_manager

fm = get_fallback_manager()

def get_weather(location):
    return fm.execute_with_fallback(
        "weather",
        lambda: call_weather_api(location)
    )
```

Benefits:

- ✅ Automatic circuit breaking
- ✅ State tracking
- ✅ Logging
- ✅ Metrics

## Support / الدعم

Questions? Issues?

- Check README.md for detailed documentation
- See fallback_examples.py for working examples
- Run tests: `pytest tests/test_fallback_manager.py -v`

---

**Happy Coding! 🚀**
**برمجة سعيدة! 🚀**
