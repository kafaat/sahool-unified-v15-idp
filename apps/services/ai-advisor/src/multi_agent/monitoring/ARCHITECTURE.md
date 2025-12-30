# SAHOOL Performance Monitoring System Architecture
# هندسة نظام مراقبة الأداء لسهول

## System Overview / نظرة عامة على النظام

The SAHOOL Performance Monitoring System provides comprehensive tracking and analysis of agricultural AI agent performance, feedback collection, and quality metrics.

يوفر نظام مراقبة الأداء لسهول تتبعاً وتحليلاً شاملاً لأداء الوكلاء الذكيين الزراعيين، جمع التعليقات، ومقاييس الجودة.

## Architecture Diagram / مخطط الهندسة

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SAHOOL Multi-Agent System                        │
│                    نظام سهول متعدد الوكلاء                         │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Performance Monitor                              │
│                    مراقب الأداء                                    │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │   Request    │  │   Response   │  │   Feedback   │           │
│  │   Tracking   │  │   Tracking   │  │   System     │           │
│  │ تتبع الطلبات │  │تتبع الاستجابات│  │نظام التعليقات│           │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘           │
│         │                 │                 │                      │
│         └─────────────────┴─────────────────┘                      │
│                           │                                         │
│                           ▼                                         │
│         ┌─────────────────────────────────┐                        │
│         │      Metrics Aggregation        │                        │
│         │      تجميع المقاييس            │                        │
│         └─────────────┬───────────────────┘                        │
│                       │                                             │
│         ┌─────────────┴───────────────┐                            │
│         │                             │                            │
│         ▼                             ▼                            │
│  ┌────────────┐              ┌────────────────┐                   │
│  │  In-Memory │              │   Prometheus   │                   │
│  │   Storage  │              │    Metrics     │                   │
│  │ تخزين محلي │              │ مقاييس Prometheus│                   │
│  └────────────┘              └────────────────┘                   │
└─────────────────────────────────────────────────────────────────────┘
                             │
                             ▼
        ┌────────────────────────────────────────────┐
        │           Data Consumers                   │
        │           مستهلكو البيانات                 │
        │                                            │
        │  ┌─────────────┐    ┌──────────────┐     │
        │  │   Grafana   │    │  JSON Export │     │
        │  │ Dashboards  │    │  تصدير JSON  │     │
        │  └─────────────┘    └──────────────┘     │
        │                                            │
        │  ┌─────────────┐    ┌──────────────┐     │
        │  │   Alerts &  │    │ Recommendations│    │
        │  │Notifications│    │   التوصيات    │     │
        │  └─────────────┘    └──────────────┘     │
        └────────────────────────────────────────────┘
```

## Component Breakdown / تفصيل المكونات

### 1. PerformanceMonitor / مراقب الأداء

Main orchestrator for performance tracking and metrics collection.

المنسق الرئيسي لتتبع الأداء وجمع المقاييس.

**Responsibilities / المسؤوليات:**
- Request/response tracking / تتبع الطلبات والاستجابات
- Metrics aggregation / تجميع المقاييس
- Performance calculations / حسابات الأداء
- Prometheus integration / تكامل Prometheus
- Data export / تصدير البيانات

**Key Methods / الوظائف الرئيسية:**
```python
- record_request(agent_id, request_data)
- record_response(agent_id, response_data, success, latency, ...)
- record_feedback(agent_id, request_id, feedback)
- get_metrics(agent_id)
- get_all_metrics()
- calculate_accuracy(agent_id, actual_outcomes)
- get_recommendations(agent_id)
- export_metrics(format)
```

### 2. FeedbackCollector / جامع التعليقات

Dedicated component for user feedback collection and analysis.

مكون مخصص لجمع وتحليل تعليقات المستخدمين.

**Responsibilities / المسؤوليات:**
- User feedback submission / إرسال تعليقات المستخدمين
- Actual outcome tracking / تتبع النتائج الفعلية
- Feedback analysis / تحليل التعليقات
- Improvement area identification / تحديد مجالات التحسين

**Key Methods / الوظائف الرئيسية:**
```python
- submit_feedback(request_id, rating, comments)
- submit_outcome(request_id, actual_result)
- get_feedback_summary(agent_id)
- identify_improvement_areas(agent_id)
```

### 3. AgentMetrics / مقاييس الوكيل

Dataclass for storing comprehensive agent performance metrics.

فئة بيانات لتخزين مقاييس أداء شاملة للوكيل.

**Metrics Tracked / المقاييس المتتبعة:**

#### Request Metrics / مقاييس الطلبات
- `total_requests`: Total count / إجمالي العدد
- `successful_requests`: Success count / عدد النجاحات
- `failed_requests`: Failure count / عدد الإخفاقات

#### Response Time Metrics / مقاييس وقت الاستجابة
- `avg_response_time`: Average latency / متوسط الزمن
- `p95_response_time`: 95th percentile / النسبة المئوية 95
- `p99_response_time`: 99th percentile / النسبة المئوية 99

#### Quality Metrics / مقاييس الجودة
- `avg_confidence`: Average confidence score / متوسط الثقة
- `accuracy_score`: Prediction accuracy / دقة التنبؤ
- `user_satisfaction_score`: User rating / تقييم المستخدم

#### Cost Metrics / مقاييس التكلفة
- `tokens_used`: Total tokens consumed / إجمالي الرموز
- `cost_estimate`: Estimated cost in $ / التكلفة التقديرية

## Data Flow / تدفق البيانات

### 1. Request Flow / تدفق الطلب

```
Agent Request
    │
    ▼
PerformanceMonitor.record_request()
    │
    ├─► Create RequestRecord
    ├─► Increment total_requests
    ├─► Store in _requests dict
    └─► Return request_id
```

### 2. Response Flow / تدفق الاستجابة

```
Agent Response
    │
    ▼
PerformanceMonitor.record_response()
    │
    ├─► Update RequestRecord
    ├─► Increment success/failed counters
    ├─► Update response time metrics
    ├─► Update confidence scores
    ├─► Update cost metrics
    ├─► Update Prometheus metrics
    └─► Return success status
```

### 3. Feedback Flow / تدفق التعليقات

```
User Feedback
    │
    ▼
FeedbackCollector.submit_feedback()
    │
    ├─► Create FeedbackRecord
    ├─► Update satisfaction scores
    ├─► Update Prometheus gauges
    └─► Return feedback_id
```

### 4. Accuracy Calculation Flow / تدفق حساب الدقة

```
Actual Outcomes
    │
    ▼
FeedbackCollector.submit_outcome()
    │
    ├─► Store actual result
    │
    ▼
PerformanceMonitor.calculate_accuracy()
    │
    ├─► Compare predictions vs actuals
    ├─► Calculate accuracy percentage
    ├─► Update accuracy_score
    ├─► Update Prometheus gauge
    └─► Return accuracy
```

## Storage Strategy / استراتيجية التخزين

### In-Memory Storage / التخزين في الذاكرة

The monitoring system uses efficient in-memory data structures:

يستخدم نظام المراقبة هياكل بيانات فعالة في الذاكرة:

```python
# Dictionaries for O(1) lookups / قواميس للبحث السريع
_metrics: Dict[str, AgentMetrics]           # agent_id -> metrics
_requests: Dict[str, RequestRecord]          # request_id -> record
_feedback: Dict[str, FeedbackRecord]         # feedback_id -> record

# Deques for efficient history management / طوابير للإدارة الفعالة للسجل
_request_history: Dict[str, deque]           # agent_id -> deque of request_ids

# Lists for windowed calculations / قوائم للحسابات النافذة
_response_times: List[float]                 # Recent response times
_confidence_scores: List[float]              # Recent confidence scores
_feedback_ratings: List[int]                 # Recent ratings
```

### Memory Management / إدارة الذاكرة

- **max_history**: Limits total request history (default: 1000)
  الحد الأقصى للسجل: يحد من إجمالي سجل الطلبات

- **percentile_window**: Limits data for percentile calculations (default: 100)
  نافذة النسب المئوية: يحد من البيانات لحسابات النسب المئوية

- **Automatic cleanup**: Old data automatically removed when limits reached
  التنظيف التلقائي: إزالة البيانات القديمة تلقائياً عند الوصول للحدود

## Prometheus Integration / تكامل Prometheus

### Metric Types / أنواع المقاييس

#### Counters (Monotonically Increasing) / العدادات (متزايدة دائماً)
```python
sahool_agent_requests_total{agent_id, agent_type, status}
sahool_agent_tokens_total{agent_id, agent_type}
sahool_agent_cost_dollars{agent_id, agent_type}
```

#### Gauges (Current Value) / المقاييس (القيمة الحالية)
```python
sahool_agent_confidence_score{agent_id, agent_type}
sahool_agent_accuracy_score{agent_id, agent_type}
sahool_agent_satisfaction_score{agent_id, agent_type}
```

#### Histograms (Distribution) / المدرجات التكرارية (التوزيع)
```python
sahool_agent_response_time_seconds{agent_id, agent_type}
  - Buckets: [0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0]
```

### Grafana Dashboard Example / مثال لوحة Grafana

```yaml
# Example Grafana queries / أمثلة استعلامات Grafana

# Success rate / معدل النجاح
rate(sahool_agent_requests_total{status="success"}[5m])
/ rate(sahool_agent_requests_total[5m])

# Average response time / متوسط وقت الاستجابة
rate(sahool_agent_response_time_seconds_sum[5m])
/ rate(sahool_agent_response_time_seconds_count[5m])

# P95 response time / النسبة المئوية 95 لوقت الاستجابة
histogram_quantile(0.95, sahool_agent_response_time_seconds_bucket)

# Cost per hour / التكلفة بالساعة
rate(sahool_agent_cost_dollars[1h])
```

## Performance Recommendations Engine / محرك توصيات الأداء

The system automatically analyzes metrics and provides recommendations:

يحلل النظام المقاييس تلقائياً ويوفر توصيات:

### Recommendation Areas / مجالات التوصيات

1. **Response Time** / **وقت الاستجابة**
   - Triggered when: avg_response_time > threshold
   - Severity: High if > 2x threshold

2. **Accuracy** / **الدقة**
   - Triggered when: accuracy_score < threshold
   - Severity: High (always)

3. **User Satisfaction** / **رضا المستخدم**
   - Triggered when: satisfaction_score < threshold
   - Severity: Medium

4. **Confidence** / **الثقة**
   - Triggered when: avg_confidence < 0.7
   - Severity: Low

5. **Error Rate** / **معدل الخطأ**
   - Triggered when: error_rate > 5%
   - Severity: High if > 10%, Medium otherwise

6. **Cost Efficiency** / **كفاءة التكلفة**
   - Triggered when: cost_per_request > $0.01
   - Severity: Low

### Recommendation Format / صيغة التوصية

```python
{
    'area': 'response_time',
    'area_ar': 'وقت الاستجابة',
    'severity': 'high',  # high, medium, low
    'current_value': 3.5,
    'target_value': 2.0,
    'suggestion': 'Response time (3.5s) exceeds threshold...',
    'suggestion_ar': 'وقت الاستجابة (3.5ث) يتجاوز الحد...'
}
```

## Feedback Analysis / تحليل التعليقات

### Rating Distribution / توزيع التقييمات

Tracks 1-5 star ratings:
يتتبع التقييمات من 1-5 نجوم:

```
⭐ (1): Very Poor / سيء جداً
⭐⭐ (2): Poor / سيء
⭐⭐⭐ (3): Fair / مقبول
⭐⭐⭐⭐ (4): Good / جيد
⭐⭐⭐⭐⭐ (5): Excellent / ممتاز
```

### Comment Analysis / تحليل التعليقات

Automatic theme detection using keywords:
الكشف التلقائي عن المواضيع باستخدام الكلمات المفتاحية:

```python
theme_keywords = {
    'response_time': ['slow', 'wait', 'بطيء', 'انتظار'],
    'accuracy': ['wrong', 'incorrect', 'خطأ', 'غير دقيق'],
    'clarity': ['unclear', 'confusing', 'غير واضح', 'محير'],
    'completeness': ['incomplete', 'missing', 'ناقص', 'غير كامل']
}
```

## Export Formats / صيغ التصدير

### 1. JSON Export / تصدير JSON

```json
{
  "timestamp": "2025-12-29T23:56:00Z",
  "agents": {
    "disease-expert": {
      "agent_id": "disease-expert",
      "total_requests": 100,
      "success_rate": 95.0,
      "avg_response_time": 1.5,
      "accuracy_score": 0.92,
      ...
    }
  }
}
```

### 2. Prometheus Export / تصدير Prometheus

```
# HELP sahool_agent_requests_total Total agent requests
# TYPE sahool_agent_requests_total counter
sahool_agent_requests_total{agent_id="disease-expert",status="success"} 95.0
sahool_agent_requests_total{agent_id="disease-expert",status="failure"} 5.0

# HELP sahool_agent_response_time_seconds Response time distribution
# TYPE sahool_agent_response_time_seconds histogram
sahool_agent_response_time_seconds_bucket{agent_id="disease-expert",le="1.0"} 45
sahool_agent_response_time_seconds_bucket{agent_id="disease-expert",le="2.0"} 92
...
```

## Scalability Considerations / اعتبارات قابلية التوسع

### Current Design / التصميم الحالي

- **In-memory storage**: Fast but limited by RAM
  التخزين في الذاكرة: سريع لكن محدود بالذاكرة

- **Single instance**: No distribution
  نسخة واحدة: بدون توزيع

- **Max 1000 requests/agent**: Memory bounded
  حد أقصى 1000 طلب/وكيل: محدود بالذاكرة

### Future Enhancements / التحسينات المستقبلية

1. **Redis Backend** / **خلفية Redis**
   - Distributed storage / تخزين موزع
   - Persistence / ثبات البيانات
   - Scalability / قابلية التوسع

2. **PostgreSQL Integration** / **تكامل PostgreSQL**
   - Long-term storage / تخزين طويل الأمد
   - Complex queries / استعلامات معقدة
   - Historical analysis / تحليل تاريخي

3. **Apache Kafka** / **Apache Kafka**
   - Event streaming / بث الأحداث
   - Real-time processing / معالجة في الوقت الفعلي
   - High throughput / إنتاجية عالية

## Security Considerations / اعتبارات الأمان

### Data Privacy / خصوصية البيانات

- No PII stored in metrics / لا معلومات شخصية في المقاييس
- Request data sanitization / تنقية بيانات الطلبات
- Feedback anonymization / إخفاء هوية التعليقات

### Access Control / التحكم في الوصول

- Prometheus endpoint authentication / مصادقة نقطة نهاية Prometheus
- Export permission checks / فحوصات أذونات التصدير
- Rate limiting / تحديد المعدل

## Testing Strategy / استراتيجية الاختبار

### Unit Tests / اختبارات الوحدة

```python
test_record_request()
test_record_response()
test_calculate_metrics()
test_accuracy_calculation()
test_recommendations()
```

### Integration Tests / اختبارات التكامل

```python
test_full_request_lifecycle()
test_feedback_flow()
test_prometheus_export()
test_multi_agent_monitoring()
```

### Performance Tests / اختبارات الأداء

```python
test_high_volume_requests()
test_memory_usage()
test_export_performance()
```

## Conclusion / الخلاصة

The SAHOOL Performance Monitoring System provides a comprehensive, production-ready solution for tracking and improving agricultural AI agent performance. With built-in Prometheus integration, automatic recommendations, and comprehensive feedback collection, it enables data-driven optimization of the multi-agent system.

يوفر نظام مراقبة الأداء لسهول حلاً شاملاً وجاهزاً للإنتاج لتتبع وتحسين أداء الوكلاء الذكيين الزراعيين. مع تكامل Prometheus المدمج، التوصيات التلقائية، وجمع التعليقات الشامل، فإنه يمكّن من التحسين القائم على البيانات لنظام الوكلاء المتعدد.
