# SAHOOL Multi-Agent Performance Monitoring System
# نظام مراقبة الأداء للوكلاء المتعدد لسهول

A comprehensive performance monitoring and feedback system for agricultural AI agents in the SAHOOL platform.

نظام شامل لمراقبة الأداء والتعليقات للوكلاء الذكيين الزراعيين في منصة سهول.

## Features / الميزات

### Core Features / الميزات الأساسية

- **Real-time Performance Tracking** / **تتبع الأداء في الوقت الفعلي**
  - Request and response monitoring / مراقبة الطلبات والاستجابات
  - Success/failure rate tracking / تتبع معدلات النجاح والفشل
  - Response time metrics (avg, P95, P99) / مقاييس وقت الاستجابة

- **Quality Metrics** / **مقاييس الجودة**
  - Confidence score tracking / تتبع درجة الثقة
  - Accuracy calculation / حساب الدقة
  - User satisfaction monitoring / مراقبة رضا المستخدم

- **Cost Management** / **إدارة التكلفة**
  - Token usage tracking / تتبع استخدام الرموز
  - Cost estimation / تقدير التكلفة
  - Cost per request analysis / تحليل التكلفة لكل طلب

- **Feedback System** / **نظام التعليقات**
  - User feedback collection / جمع تعليقات المستخدمين
  - Rating system (1-5 stars) / نظام التقييم (1-5 نجوم)
  - Actual outcome tracking / تتبع النتائج الفعلية

- **Performance Recommendations** / **توصيات الأداء**
  - Automated improvement suggestions / اقتراحات تحسين تلقائية
  - Problem area identification / تحديد مجالات المشاكل
  - Threshold-based alerts / تنبيهات قائمة على الحدود

- **Prometheus Integration** / **تكامل Prometheus**
  - Metrics export for Grafana / تصدير المقاييس لـ Grafana
  - Counter, Gauge, and Histogram metrics / مقاييس العداد والمقياس والمدرج التكراري
  - Standard Prometheus format / صيغة Prometheus القياسية

## Installation / التثبيت

### Requirements / المتطلبات

```bash
# Core dependencies / الحزم الأساسية
pip install structlog

# Optional: Prometheus support / اختياري: دعم Prometheus
pip install prometheus-client
```

### Quick Start / البدء السريع

```python
from multi_agent.monitoring import PerformanceMonitor, FeedbackCollector

# Initialize monitor
monitor = PerformanceMonitor(
    max_history=1000,
    enable_prometheus=True
)

# Start monitoring
request_id = await monitor.record_request(
    agent_id="disease-expert",
    request_data={"query": "diagnose wheat disease"}
)

await monitor.record_response(
    agent_id="disease-expert",
    response_data={"diagnosis": "yellow rust"},
    success=True,
    latency=1.5,
    confidence=0.92,
    tokens_used=150
)
```

## Usage Examples / أمثلة الاستخدام

### Example 1: Basic Performance Monitoring / مثال 1: مراقبة الأداء الأساسية

```python
import asyncio
from multi_agent.monitoring import PerformanceMonitor

async def monitor_agent():
    monitor = PerformanceMonitor()

    # Record request
    request_id = await monitor.record_request(
        agent_id="disease-expert",
        request_data={
            "query": "Diagnose wheat rust",
            "language": "ar"
        }
    )

    # Process request (your agent logic here)
    # ...

    # Record response
    await monitor.record_response(
        agent_id="disease-expert",
        response_data={
            "diagnosis": "yellow_rust",
            "confidence": 0.92
        },
        success=True,
        latency=1.5,
        confidence=0.92,
        tokens_used=150
    )

    # Get metrics
    metrics = await monitor.get_metrics("disease-expert")
    print(f"Success rate: {metrics.success_rate():.2f}%")
    print(f"Avg response time: {metrics.avg_response_time:.2f}s")
    print(f"Cost per request: ${metrics.cost_per_request():.4f}")

asyncio.run(monitor_agent())
```

### Example 2: Feedback Collection / مثال 2: جمع التعليقات

```python
from multi_agent.monitoring import PerformanceMonitor, FeedbackCollector

async def collect_feedback():
    monitor = PerformanceMonitor()
    collector = FeedbackCollector(monitor)

    # After agent responds...
    request_id = "req_123"

    # User provides feedback
    await collector.submit_feedback(
        request_id=request_id,
        rating=5,
        comments="Excellent diagnosis! Very accurate and helpful."
    )

    # Later, submit actual outcome for accuracy tracking
    await collector.submit_outcome(
        request_id=request_id,
        actual_result="yellow_rust_confirmed"
    )

    # Get feedback summary
    summary = await collector.get_feedback_summary("disease-expert")
    print(f"Average rating: {summary['average_rating']:.2f}/5.0")
    print(f"Total feedback: {summary['total_feedback']}")

asyncio.run(collect_feedback())
```

### Example 3: Performance Recommendations / مثال 3: توصيات الأداء

```python
async def get_recommendations():
    monitor = PerformanceMonitor()

    # After some monitoring...
    recommendations = await monitor.get_recommendations(
        agent_id="disease-expert",
        threshold_response_time=2.0,
        threshold_accuracy=0.9,
        threshold_satisfaction=4.5
    )

    for rec in recommendations:
        print(f"Area: {rec['area']}")
        print(f"Suggestion: {rec['suggestion']}")
        print(f"Severity: {rec['severity']}")
        print()

asyncio.run(get_recommendations())
```

### Example 4: Multi-Agent Monitoring / مثال 4: مراقبة الوكلاء المتعددين

```python
async def monitor_multiple_agents():
    monitor = PerformanceMonitor()

    agents = [
        "disease-expert",
        "irrigation-advisor",
        "fertilizer-expert"
    ]

    # Monitor all agents
    for agent_id in agents:
        # ... record requests and responses
        pass

    # Get all metrics
    all_metrics = await monitor.get_all_metrics()

    for agent_id, metrics in all_metrics.items():
        print(f"\n{agent_id}:")
        print(f"  Requests: {metrics.total_requests}")
        print(f"  Success rate: {metrics.success_rate():.2f}%")
        print(f"  Avg response time: {metrics.avg_response_time:.2f}s")

asyncio.run(monitor_multiple_agents())
```

### Example 5: Prometheus Export / مثال 5: تصدير Prometheus

```python
async def export_prometheus():
    monitor = PerformanceMonitor(enable_prometheus=True)

    # After monitoring...

    # Export for Prometheus/Grafana
    prometheus_metrics = await monitor.export_metrics(format="prometheus")

    # Serve via HTTP endpoint (example with Flask)
    from flask import Flask, Response

    app = Flask(__name__)

    @app.route('/metrics')
    async def metrics():
        metrics_data = await monitor.export_metrics(format="prometheus")
        return Response(metrics_data, mimetype='text/plain')

    app.run(port=9090)
```

## API Reference / مرجع واجهة البرمجة

### PerformanceMonitor

#### Constructor / المُنشئ

```python
PerformanceMonitor(
    max_history: int = 1000,           # Maximum request history
    percentile_window: int = 100,      # Window for percentile calculations
    enable_prometheus: bool = True     # Enable Prometheus metrics
)
```

#### Methods / الوظائف

##### `async record_request(agent_id, request_data, request_id=None) -> str`
Record a new agent request / تسجيل طلب وكيل جديد

**Parameters:**
- `agent_id`: Agent identifier / معرف الوكيل
- `request_data`: Request payload / بيانات الطلب
- `request_id`: Optional custom request ID / معرف طلب مخصص اختياري

**Returns:** Request ID / معرف الطلب

##### `async record_response(agent_id, response_data, success, latency, **kwargs) -> bool`
Record agent response / تسجيل استجابة الوكيل

**Parameters:**
- `agent_id`: Agent identifier / معرف الوكيل
- `response_data`: Response payload / بيانات الاستجابة
- `success`: Whether request succeeded / نجح الطلب أم لا
- `latency`: Response time in seconds / وقت الاستجابة بالثواني
- `confidence`: Confidence score 0.0-1.0 / درجة الثقة
- `tokens_used`: Number of tokens consumed / عدد الرموز المستخدمة
- `error`: Error message if failed / رسالة الخطأ إن فشل

**Returns:** True if successful / صحيح إذا نجح

##### `async record_feedback(agent_id, request_id, feedback, feedback_id=None) -> str`
Record user feedback / تسجيل تعليقات المستخدم

**Parameters:**
- `agent_id`: Agent identifier / معرف الوكيل
- `request_id`: Associated request ID / معرف الطلب المرتبط
- `feedback`: Feedback data dict / قاموس بيانات التعليقات
- `feedback_id`: Optional custom feedback ID / معرف تعليق مخصص اختياري

**Returns:** Feedback ID / معرف التعليق

##### `async get_metrics(agent_id) -> Optional[AgentMetrics]`
Get performance metrics for a specific agent / الحصول على مقاييس الأداء لوكيل محدد

##### `async get_all_metrics() -> Dict[str, AgentMetrics]`
Get performance metrics for all agents / الحصول على مقاييس الأداء لجميع الوكلاء

##### `async calculate_accuracy(agent_id, actual_outcomes) -> float`
Calculate agent accuracy based on actual outcomes / حساب دقة الوكيل بناءً على النتائج الفعلية

##### `async get_recommendations(agent_id, **thresholds) -> List[Dict]`
Get performance improvement recommendations / الحصول على توصيات تحسين الأداء

##### `async export_metrics(format="json") -> str`
Export metrics in specified format / تصدير المقاييس بالصيغة المحددة

**Formats:**
- `"json"`: JSON format / صيغة JSON
- `"prometheus"`: Prometheus format / صيغة Prometheus

### FeedbackCollector

#### Constructor / المُنشئ

```python
FeedbackCollector(performance_monitor: PerformanceMonitor)
```

#### Methods / الوظائف

##### `async submit_feedback(request_id, rating, comments="", agent_id=None) -> str`
Submit user feedback / إرسال تعليقات المستخدم

**Parameters:**
- `request_id`: Request identifier / معرف الطلب
- `rating`: Rating 1-5 / التقييم من 1 إلى 5
- `comments`: Text comments / تعليقات نصية
- `agent_id`: Optional agent ID / معرف الوكيل (اختياري)

##### `async submit_outcome(request_id, actual_result, agent_id=None) -> bool`
Submit actual outcome for accuracy tracking / إرسال النتيجة الفعلية لتتبع الدقة

##### `async get_feedback_summary(agent_id, time_window=None) -> Dict`
Get feedback summary for an agent / الحصول على ملخص التعليقات لوكيل

##### `async identify_improvement_areas(agent_id) -> List[Dict]`
Identify areas for improvement based on feedback / تحديد مجالات التحسين بناءً على التعليقات

### AgentMetrics

Dataclass containing all agent performance metrics / فئة بيانات تحتوي على جميع مقاييس أداء الوكيل

**Attributes:**
- `agent_id`: Agent identifier / معرف الوكيل
- `agent_type`: Agent type / نوع الوكيل
- `total_requests`: Total number of requests / إجمالي الطلبات
- `successful_requests`: Successful requests / الطلبات الناجحة
- `failed_requests`: Failed requests / الطلبات الفاشلة
- `avg_response_time`: Average response time / متوسط وقت الاستجابة
- `p95_response_time`: 95th percentile / النسبة المئوية 95
- `p99_response_time`: 99th percentile / النسبة المئوية 99
- `avg_confidence`: Average confidence / متوسط الثقة
- `accuracy_score`: Accuracy score / درجة الدقة
- `user_satisfaction_score`: User satisfaction / رضا المستخدم
- `tokens_used`: Total tokens used / إجمالي الرموز المستخدمة
- `cost_estimate`: Estimated cost / تقدير التكلفة

**Methods:**
- `success_rate()`: Calculate success rate / حساب معدل النجاح
- `error_rate()`: Calculate error rate / حساب معدل الخطأ
- `cost_per_request()`: Calculate cost per request / حساب التكلفة لكل طلب
- `to_dict()`: Convert to dictionary / تحويل إلى قاموس

## Prometheus Metrics / مقاييس Prometheus

When Prometheus integration is enabled, the following metrics are exposed:

عند تفعيل تكامل Prometheus، يتم توفير المقاييس التالية:

### Counters / العدادات

- `sahool_agent_requests_total{agent_id, agent_type, status}`
  - Total number of agent requests / إجمالي طلبات الوكيل

- `sahool_agent_tokens_total{agent_id, agent_type}`
  - Total tokens used by agent / إجمالي الرموز المستخدمة

- `sahool_agent_cost_dollars{agent_id, agent_type}`
  - Total cost in dollars / إجمالي التكلفة بالدولار

### Gauges / المقاييس

- `sahool_agent_confidence_score{agent_id, agent_type}`
  - Agent confidence score / درجة ثقة الوكيل

- `sahool_agent_accuracy_score{agent_id, agent_type}`
  - Agent accuracy score / درجة دقة الوكيل

- `sahool_agent_satisfaction_score{agent_id, agent_type}`
  - User satisfaction score / درجة رضا المستخدم

### Histograms / المدرجات التكرارية

- `sahool_agent_response_time_seconds{agent_id, agent_type}`
  - Agent response time distribution / توزيع وقت استجابة الوكيل
  - Buckets: [0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0]

## Best Practices / أفضل الممارسات

### 1. Consistent Request Tracking / تتبع الطلبات المتسق

Always record both request and response for complete tracking:

سجل دائماً كلاً من الطلب والاستجابة للتتبع الكامل:

```python
# Good ✅
request_id = await monitor.record_request(agent_id, data)
# ... process ...
await monitor.record_response(agent_id, response, success, latency)

# Bad ❌
# Only recording response without request
await monitor.record_response(agent_id, response, success, latency)
```

### 2. Provide Meaningful Request Data / توفير بيانات طلب ذات معنى

Include relevant context in request data:

قم بتضمين السياق ذي الصلة في بيانات الطلب:

```python
request_data = {
    "agent_type": "disease_diagnosis",
    "query": "diagnose wheat disease",
    "language": "ar",
    "user_id": "farmer_123",
    "farm_location": "Riyadh"
}
```

### 3. Track Confidence Scores / تتبع درجات الثقة

Always provide confidence scores when available:

قدم دائماً درجات الثقة عند توفرها:

```python
await monitor.record_response(
    agent_id=agent_id,
    response_data=response,
    success=True,
    latency=latency,
    confidence=0.92,  # Always include confidence
    tokens_used=tokens
)
```

### 4. Collect User Feedback / جمع تعليقات المستخدمين

Actively encourage and collect user feedback:

شجع وأجمع تعليقات المستخدمين بنشاط:

```python
# After showing response to user
feedback_id = await collector.submit_feedback(
    request_id=request_id,
    rating=user_rating,
    comments=user_comments
)
```

### 5. Monitor and Act on Recommendations / راقب وتصرف بناءً على التوصيات

Regularly check and act on performance recommendations:

تحقق بانتظام من توصيات الأداء وتصرف بناءً عليها:

```python
# Daily/weekly monitoring
recommendations = await monitor.get_recommendations(agent_id)
for rec in recommendations:
    if rec['severity'] == 'high':
        # Take immediate action
        alert_team(rec)
```

### 6. Export Metrics for Visualization / تصدير المقاييس للتصور

Use Prometheus and Grafana for visualization:

استخدم Prometheus و Grafana للتصور:

```python
# Setup Prometheus endpoint
@app.route('/metrics')
async def metrics():
    return await monitor.export_metrics(format="prometheus")
```

## Integration with SAHOOL Multi-Agent System / التكامل مع نظام سهول متعدد الوكلاء

This monitoring system integrates seamlessly with other SAHOOL components:

يتكامل نظام المراقبة هذا بسلاسة مع مكونات سهول الأخرى:

```python
from multi_agent.orchestration import MasterAdvisor
from multi_agent.monitoring import PerformanceMonitor

# Initialize
monitor = PerformanceMonitor()
advisor = MasterAdvisor(performance_monitor=monitor)

# Monitoring is automatic
response = await advisor.process_query(query)
metrics = await monitor.get_metrics(advisor.agent_id)
```

## Testing / الاختبار

Run the example usage file to test the monitoring system:

قم بتشغيل ملف مثال الاستخدام لاختبار نظام المراقبة:

```bash
cd /home/user/sahool-unified-v15-idp/apps/services/ai-advisor/src/multi_agent/monitoring
python example_usage.py
```

## Troubleshooting / استكشاف الأخطاء وإصلاحها

### Prometheus not available / Prometheus غير متوفر

```python
from multi_agent.monitoring import PROMETHEUS_AVAILABLE

if not PROMETHEUS_AVAILABLE:
    print("Install prometheus_client: pip install prometheus-client")
```

### High memory usage / استخدام ذاكرة مرتفع

Reduce `max_history` and `percentile_window`:

قلل `max_history` و `percentile_window`:

```python
monitor = PerformanceMonitor(
    max_history=500,  # Reduced from 1000
    percentile_window=50  # Reduced from 100
)
```

## License / الترخيص

Part of the SAHOOL Agricultural AI Platform

جزء من منصة سهول للذكاء الاصطناعي الزراعي

## Support / الدعم

For questions and support:
للأسئلة والدعم:

- GitHub Issues: [sahool-unified-v15-idp](https://github.com/sahool/sahool-unified-v15-idp)
- Email: support@sahool.ai
