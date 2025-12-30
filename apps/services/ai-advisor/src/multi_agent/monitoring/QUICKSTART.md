# Quick Start Guide - SAHOOL Performance Monitoring
# دليل البدء السريع - نظام مراقبة الأداء لسهول

Get started with the SAHOOL Performance Monitoring System in 5 minutes!

ابدأ مع نظام مراقبة الأداء لسهول في 5 دقائق!

## Installation / التثبيت

### Step 1: Install Dependencies / الخطوة 1: تثبيت المكتبات

```bash
cd /home/user/sahool-unified-v15-idp/apps/services/ai-advisor/src/multi_agent/monitoring

# Install required packages
pip install -r requirements.txt

# Or install individually
pip install structlog prometheus-client
```

### Step 2: Verify Installation / الخطوة 2: التحقق من التثبيت

```python
from multi_agent.monitoring import PerformanceMonitor, FeedbackCollector
print("✅ Installation successful!")
```

## Basic Usage / الاستخدام الأساسي

### Minimal Example (30 seconds) / مثال بسيط (30 ثانية)

```python
import asyncio
from multi_agent.monitoring import PerformanceMonitor

async def quick_start():
    # 1. Create monitor
    monitor = PerformanceMonitor()

    # 2. Track a request
    request_id = await monitor.record_request(
        agent_id="my-agent",
        request_data={"query": "test"}
    )

    # 3. Record response
    await monitor.record_response(
        agent_id="my-agent",
        response_data={"result": "success"},
        success=True,
        latency=1.5
    )

    # 4. Get metrics
    metrics = await monitor.get_metrics("my-agent")
    print(f"Total requests: {metrics.total_requests}")
    print(f"Success rate: {metrics.success_rate():.2f}%")

asyncio.run(quick_start())
```

## Common Use Cases / حالات الاستخدام الشائعة

### Use Case 1: Monitor Agent Performance / مراقبة أداء الوكيل

```python
import asyncio
from multi_agent.monitoring import PerformanceMonitor

async def monitor_my_agent():
    monitor = PerformanceMonitor()

    # Your agent processes a request
    request_id = await monitor.record_request(
        agent_id="disease-expert",
        request_data={
            "query": "Diagnose wheat rust",
            "user_id": "farmer_123"
        }
    )

    # Agent processes...
    # (your agent logic here)

    # Record the response
    await monitor.record_response(
        agent_id="disease-expert",
        response_data={
            "diagnosis": "yellow_rust",
            "confidence": 0.92
        },
        success=True,
        latency=2.1,
        confidence=0.92,
        tokens_used=150
    )

    # Check performance
    metrics = await monitor.get_metrics("disease-expert")
    print(f"📊 Agent Metrics:")
    print(f"  Requests: {metrics.total_requests}")
    print(f"  Success Rate: {metrics.success_rate():.2f}%")
    print(f"  Avg Response Time: {metrics.avg_response_time:.2f}s")
    print(f"  Avg Confidence: {metrics.avg_confidence:.2%}")
    print(f"  Cost: ${metrics.cost_estimate:.4f}")

asyncio.run(monitor_my_agent())
```

### Use Case 2: Collect User Feedback / جمع تعليقات المستخدمين

```python
import asyncio
from multi_agent.monitoring import PerformanceMonitor, FeedbackCollector

async def collect_user_feedback():
    monitor = PerformanceMonitor()
    collector = FeedbackCollector(monitor)

    # After agent responds to user...
    request_id = "req_123"  # From previous request

    # User provides feedback
    feedback_id = await collector.submit_feedback(
        request_id=request_id,
        rating=5,  # 1-5 stars
        comments="Excellent diagnosis! Very helpful.",
        agent_id="disease-expert"
    )

    # Get feedback summary
    summary = await collector.get_feedback_summary("disease-expert")
    print(f"💬 Feedback Summary:")
    print(f"  Total Feedback: {summary['total_feedback']}")
    print(f"  Average Rating: {summary['average_rating']:.2f}/5.0")

asyncio.run(collect_user_feedback())
```

### Use Case 3: Get Improvement Recommendations / الحصول على توصيات التحسين

```python
import asyncio
from multi_agent.monitoring import PerformanceMonitor

async def get_improvement_tips():
    monitor = PerformanceMonitor()

    # After monitoring for a while...
    recommendations = await monitor.get_recommendations(
        agent_id="disease-expert",
        threshold_response_time=2.0,
        threshold_accuracy=0.9
    )

    print(f"💡 Improvement Recommendations:")
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. {rec['area'].upper()}")
        print(f"   Severity: {rec['severity']}")
        print(f"   Current: {rec.get('current_value', 'N/A')}")
        print(f"   Target: {rec.get('target_value', 'N/A')}")
        print(f"   Suggestion: {rec['suggestion']}")

asyncio.run(get_improvement_tips())
```

### Use Case 4: Export Metrics / تصدير المقاييس

```python
import asyncio
from multi_agent.monitoring import PerformanceMonitor

async def export_performance_data():
    monitor = PerformanceMonitor(enable_prometheus=True)

    # After monitoring...

    # Export as JSON
    json_data = await monitor.export_metrics(format="json")
    print("📄 JSON Export:")
    print(json_data[:200] + "...")

    # Export for Prometheus/Grafana
    prometheus_data = await monitor.export_metrics(format="prometheus")
    print("\n📊 Prometheus Export:")
    print(prometheus_data[:200] + "...")

asyncio.run(export_performance_data())
```

## Integration with Your Agent / التكامل مع وكيلك

### Option 1: Decorator Pattern / نمط المُزخرف

```python
import asyncio
from functools import wraps
from multi_agent.monitoring import PerformanceMonitor

monitor = PerformanceMonitor()

def track_performance(agent_id: str):
    """Decorator to automatically track agent performance"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Record request
            request_data = {"args": str(args), "kwargs": str(kwargs)}
            request_id = await monitor.record_request(agent_id, request_data)

            # Execute function
            import time
            start = time.time()
            try:
                result = await func(*args, **kwargs)
                latency = time.time() - start

                # Record success
                await monitor.record_response(
                    agent_id=agent_id,
                    response_data={"result": str(result)},
                    success=True,
                    latency=latency
                )
                return result
            except Exception as e:
                latency = time.time() - start

                # Record failure
                await monitor.record_response(
                    agent_id=agent_id,
                    response_data={},
                    success=False,
                    latency=latency,
                    error=str(e)
                )
                raise

        return wrapper
    return decorator

# Use the decorator
@track_performance("my-agent")
async def my_agent_function(query: str):
    # Your agent logic
    await asyncio.sleep(1)  # Simulate processing
    return f"Processed: {query}"

# Call your function
asyncio.run(my_agent_function("test query"))
```

### Option 2: Context Manager Pattern / نمط مدير السياق

```python
import asyncio
from contextlib import asynccontextmanager
from multi_agent.monitoring import PerformanceMonitor
import time

monitor = PerformanceMonitor()

@asynccontextmanager
async def track_agent_request(agent_id: str, request_data: dict):
    """Context manager for tracking agent requests"""
    request_id = await monitor.record_request(agent_id, request_data)
    start_time = time.time()

    try:
        yield request_id
        # Success case
        latency = time.time() - start_time
        await monitor.record_response(
            agent_id=agent_id,
            response_data={"status": "success"},
            success=True,
            latency=latency
        )
    except Exception as e:
        # Failure case
        latency = time.time() - start_time
        await monitor.record_response(
            agent_id=agent_id,
            response_data={},
            success=False,
            latency=latency,
            error=str(e)
        )
        raise

# Use the context manager
async def my_agent_with_tracking():
    async with track_agent_request("my-agent", {"query": "test"}) as request_id:
        # Your agent logic
        await asyncio.sleep(1)
        result = "Success"
    return result

asyncio.run(my_agent_with_tracking())
```

## Running the Examples / تشغيل الأمثلة

### Run All Examples / تشغيل جميع الأمثلة

```bash
cd /home/user/sahool-unified-v15-idp/apps/services/ai-advisor/src/multi_agent/monitoring

python example_usage.py
```

This will run 6 comprehensive examples demonstrating all features!

سيتم تشغيل 6 أمثلة شاملة توضح جميع الميزات!

## Configuration / الإعدادات

### Basic Configuration / الإعدادات الأساسية

```python
monitor = PerformanceMonitor(
    max_history=1000,          # Max requests to keep in memory
    percentile_window=100,     # Window for percentile calculations
    enable_prometheus=True     # Enable Prometheus metrics
)
```

### Advanced Configuration / الإعدادات المتقدمة

```python
# For high-volume systems
monitor = PerformanceMonitor(
    max_history=5000,          # More history
    percentile_window=500,     # Larger window for accuracy
    enable_prometheus=True
)

# For memory-constrained systems
monitor = PerformanceMonitor(
    max_history=500,           # Less history
    percentile_window=50,      # Smaller window
    enable_prometheus=False    # Disable Prometheus
)
```

## Prometheus Setup / إعداد Prometheus

### Step 1: Create Metrics Endpoint / إنشاء نقطة نهاية المقاييس

```python
from flask import Flask, Response
from multi_agent.monitoring import PerformanceMonitor

app = Flask(__name__)
monitor = PerformanceMonitor(enable_prometheus=True)

@app.route('/metrics')
async def metrics():
    prometheus_data = await monitor.export_metrics(format="prometheus")
    return Response(prometheus_data, mimetype='text/plain')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9090)
```

### Step 2: Configure Prometheus / إعداد Prometheus

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'sahool-agents'
    static_configs:
      - targets: ['localhost:9090']
```

### Step 3: Start Prometheus / تشغيل Prometheus

```bash
prometheus --config.file=prometheus.yml
```

### Step 4: Access Metrics / الوصول إلى المقاييس

- Prometheus UI: http://localhost:9090
- Metrics endpoint: http://localhost:9090/metrics

## Next Steps / الخطوات التالية

1. **Read the full documentation** / **اقرأ الوثائق الكاملة**
   - README.md for detailed API reference
   - ARCHITECTURE.md for system design

2. **Run the examples** / **شغّل الأمثلة**
   - `python example_usage.py`

3. **Integrate with your agents** / **دمج مع وكلائك**
   - Use decorator or context manager patterns
   - Start collecting metrics

4. **Setup monitoring** / **إعداد المراقبة**
   - Configure Prometheus
   - Create Grafana dashboards
   - Set up alerts

5. **Analyze and improve** / **حلل وحسّن**
   - Review metrics regularly
   - Act on recommendations
   - Collect user feedback

## Common Issues / المشاكل الشائعة

### Issue 1: Import Error / خطأ الاستيراد

```python
# Error: ModuleNotFoundError: No module named 'structlog'
# Solution:
pip install structlog
```

### Issue 2: Prometheus Not Available / Prometheus غير متوفر

```python
from multi_agent.monitoring import PROMETHEUS_AVAILABLE

if not PROMETHEUS_AVAILABLE:
    print("Install: pip install prometheus-client")
```

### Issue 3: Memory Usage / استخدام الذاكرة

```python
# Reduce max_history if memory is a concern
monitor = PerformanceMonitor(max_history=500)
```

## Support / الدعم

Need help? / تحتاج مساعدة؟

- Check README.md for full documentation
- Review example_usage.py for code samples
- Read ARCHITECTURE.md for system design

## Summary / الملخص

You've learned how to:
- Install and configure the monitoring system
- Track agent requests and responses
- Collect user feedback
- Get performance recommendations
- Export metrics to Prometheus

Start monitoring your SAHOOL agents today!

تعلمت كيفية:
- تثبيت وإعداد نظام المراقبة
- تتبع طلبات واستجابات الوكلاء
- جمع تعليقات المستخدمين
- الحصول على توصيات الأداء
- تصدير المقاييس إلى Prometheus

ابدأ مراقبة وكلاء سهول اليوم!
