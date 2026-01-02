# API Fallback Manager - Quick Start
# البداية السريعة - مدير الاحتياطي

## 🚀 5-Minute Quick Start

### 1. Import and Use (Weather Service Example)

```python
from shared.utils.fallback_manager import get_fallback_manager

fm = get_fallback_manager()

# Your API call
def fetch_weather(location):
    return requests.get(f"https://api.weather.com/{location}").json()

# Protected with automatic fallback!
result = fm.execute_with_fallback("weather", fetch_weather, "Sanaa")
```

That's it! If the API fails, it automatically uses the weather fallback. ✅

### 2. Using Decorators

```python
from shared.utils.fallback_manager import circuit_breaker, with_fallback

def my_fallback():
    return {"status": "unavailable"}

@with_fallback(my_fallback)
@circuit_breaker(failure_threshold=5, recovery_timeout=30)
def get_data():
    return external_api_call()

# Call normally
result = get_data()
```

### 3. Check Circuit Status

```python
status = fm.get_circuit_status("weather")
print(f"State: {status['state']}")  # closed, open, or half_open
print(f"Failures: {status['failure_count']}/{status['failure_threshold']}")
```

## 📊 Pre-configured Services

Just use these service names with the global manager:

| Service | Name | Threshold | Timeout |
|---------|------|-----------|---------|
| Weather | `"weather"` | 5 | 30s |
| Satellite | `"satellite"` | 3 | 60s |
| AI | `"ai"` | 5 | 30s |
| Crop Health | `"crop_health"` | 4 | 45s |
| Irrigation | `"irrigation"` | 4 | 45s |

## 🔍 Circuit States

- **CLOSED** ✅ - Everything normal
- **OPEN** ❌ - Service failing, using fallback
- **HALF_OPEN** 🔄 - Testing if service recovered

## 📁 Files Location

```
/apps/services/shared/utils/
├── fallback_manager.py          # Main implementation
├── fallback_examples.py         # Working examples
├── README.md                    # Full documentation
├── INTEGRATION_GUIDE.md         # Integration guide
├── IMPLEMENTATION_SUMMARY.md    # Technical summary
└── tests/
    └── test_fallback_manager.py # Test suite
```

## 🧪 Run Examples

```bash
cd /home/user/sahool-unified-v15-idp/apps/services/shared/utils
python3 fallback_examples.py
```

## 📖 Next Steps

1. ✅ Read this Quick Start (you're here!)
2. 📖 Read `README.md` for detailed docs
3. 🔧 Read `INTEGRATION_GUIDE.md` for your service
4. 💻 Run `fallback_examples.py` to see it in action
5. 🧪 Run tests: `python3 -m pytest tests/ -v` (requires pytest)

## 💡 Common Patterns

### Pattern 1: Simple Fallback
```python
fm = get_fallback_manager()
result = fm.execute_with_fallback("weather", api_call)
```

### Pattern 2: Decorators
```python
@circuit_breaker(failure_threshold=5)
def my_function():
    return api_call()
```

### Pattern 3: Custom Service
```python
fm = FallbackManager()
fm.register_fallback("my_service", my_fallback_fn)
result = fm.execute_with_fallback("my_service", primary_fn)
```

## ⚙️ Configuration

```python
fm.register_fallback(
    service_name="my_service",
    fallback_fn=my_fallback,
    failure_threshold=5,    # Failures before circuit opens
    recovery_timeout=30,    # Seconds before retry
    success_threshold=3     # Successes to close circuit
)
```

## 🔧 Manual Control

```python
# Reset a circuit
fm.reset_circuit("weather")

# Get all statuses
all_statuses = fm.get_all_statuses()

# Check specific service
status = fm.get_circuit_status("weather")
```

## 🎯 Real Example

```python
from flask import Flask, jsonify
from shared.utils.fallback_manager import get_fallback_manager

app = Flask(__name__)
fm = get_fallback_manager()

@app.route('/weather/<location>')
def get_weather(location):
    def fetch():
        response = requests.get(f"{WEATHER_API}/{location}")
        response.raise_for_status()
        return response.json()

    try:
        data = fm.execute_with_fallback("weather", fetch)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 503

@app.route('/health/circuits')
def circuit_health():
    return jsonify(fm.get_all_statuses())
```

## 🐛 Troubleshooting

**Q: Fallback not being called?**
A: Ensure service is registered: `fm.register_fallback("my_service", fallback)`

**Q: Circuit stuck OPEN?**
A: Reset manually: `fm.reset_circuit("my_service")`

**Q: Too many failures?**
A: Increase threshold: `failure_threshold=10`

## 📞 Support

- 📖 Full docs: `README.md`
- 🔧 Integration: `INTEGRATION_GUIDE.md`
- 💻 Examples: `fallback_examples.py`
- 📊 Summary: `IMPLEMENTATION_SUMMARY.md`

---

**Made for SAHOOL 🌾**
**صُنع لسهول 🌾**
