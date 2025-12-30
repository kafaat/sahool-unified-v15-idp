# API Summary - SAHOOL Performance Monitoring
# ملخص واجهة البرمجة - نظام مراقبة الأداء لسهول

## Classes Overview / نظرة عامة على الفئات

### 1. AgentMetrics (Dataclass)

**Purpose:** Store comprehensive agent performance metrics
**الهدف:** تخزين مقاييس أداء شاملة للوكيل

**Attributes:**
```python
agent_id: str                      # Agent identifier / معرف الوكيل
agent_type: str                    # Agent type / نوع الوكيل
total_requests: int                # Total requests / إجمالي الطلبات
successful_requests: int           # Successful requests / الطلبات الناجحة
failed_requests: int               # Failed requests / الطلبات الفاشلة
avg_response_time: float           # Average response time (seconds)
p95_response_time: float           # 95th percentile response time
p99_response_time: float           # 99th percentile response time
avg_confidence: float              # Average confidence (0.0-1.0)
accuracy_score: float              # Accuracy score (0.0-1.0)
user_satisfaction_score: float     # User satisfaction (0.0-5.0)
tokens_used: int                   # Total tokens used
cost_estimate: float               # Estimated cost ($)
last_updated: datetime             # Last update timestamp
created_at: datetime               # Creation timestamp
```

**Methods:**
```python
success_rate() -> float            # Calculate success rate percentage
error_rate() -> float              # Calculate error rate percentage
cost_per_request() -> float        # Calculate average cost per request
to_dict() -> Dict[str, Any]        # Convert to dictionary
from_dict(data) -> AgentMetrics    # Create from dictionary
```

---

### 2. PerformanceMonitor (Main Class)

**Purpose:** Real-time performance monitoring and metrics collection
**الهدف:** مراقبة الأداء وجمع المقاييس في الوقت الفعلي

**Constructor:**
```python
PerformanceMonitor(
    max_history: int = 1000,           # Max request history
    percentile_window: int = 100,      # Percentile calculation window
    enable_prometheus: bool = True     # Enable Prometheus metrics
)
```

**Core Methods:**

#### Request/Response Tracking

```python
async record_request(
    agent_id: str,
    request_data: Dict[str, Any],
    request_id: Optional[str] = None
) -> str
"""
Record a new agent request
تسجيل طلب وكيل جديد

Args:
    agent_id: Agent identifier
    request_data: Request payload
    request_id: Optional custom request ID

Returns:
    Request ID
"""

async record_response(
    agent_id: str,
    response_data: Dict[str, Any],
    success: bool,
    latency: float,
    request_id: Optional[str] = None,
    confidence: float = 0.0,
    tokens_used: int = 0,
    error: Optional[str] = None
) -> bool
"""
Record agent response
تسجيل استجابة الوكيل

Args:
    agent_id: Agent identifier
    response_data: Response payload
    success: Whether request succeeded
    latency: Response time in seconds
    confidence: Confidence score (0.0-1.0)
    tokens_used: Number of tokens consumed
    error: Error message if failed

Returns:
    True if successful
"""
```

#### Feedback Management

```python
async record_feedback(
    agent_id: str,
    request_id: str,
    feedback: Dict[str, Any],
    feedback_id: Optional[str] = None
) -> str
"""
Record user feedback for a request
تسجيل تعليقات المستخدم لطلب

Args:
    agent_id: Agent identifier
    request_id: Associated request ID
    feedback: Feedback data (rating, comments, etc.)
    feedback_id: Optional custom feedback ID

Returns:
    Feedback ID
"""
```

#### Metrics Retrieval

```python
async get_metrics(agent_id: str) -> Optional[AgentMetrics]
"""
Get performance metrics for a specific agent
الحصول على مقاييس الأداء لوكيل محدد

Args:
    agent_id: Agent identifier

Returns:
    Agent metrics or None
"""

async get_all_metrics() -> Dict[str, AgentMetrics]
"""
Get performance metrics for all agents
الحصول على مقاييس الأداء لجميع الوكلاء

Returns:
    Dictionary of agent_id to metrics
"""
```

#### Accuracy & Recommendations

```python
async calculate_accuracy(
    agent_id: str,
    actual_outcomes: List[Tuple[str, Any]]
) -> float
"""
Calculate agent accuracy based on actual outcomes
حساب دقة الوكيل بناءً على النتائج الفعلية

Args:
    agent_id: Agent identifier
    actual_outcomes: List of (request_id, actual_result) tuples

Returns:
    Accuracy score (0.0-1.0)
"""

async get_recommendations(
    agent_id: str,
    threshold_response_time: float = 5.0,
    threshold_accuracy: float = 0.8,
    threshold_satisfaction: float = 4.0
) -> List[Dict[str, Any]]
"""
Get performance improvement recommendations
الحصول على توصيات تحسين الأداء

Args:
    agent_id: Agent identifier
    threshold_response_time: Max acceptable response time
    threshold_accuracy: Min acceptable accuracy
    threshold_satisfaction: Min acceptable satisfaction

Returns:
    List of recommendations with severity and suggestions
"""
```

#### Export

```python
async export_metrics(format: str = "json") -> str
"""
Export metrics in specified format
تصدير المقاييس بالصيغة المحددة

Args:
    format: Export format ("json" or "prometheus")

Returns:
    Formatted metrics string
"""
```

---

### 3. FeedbackCollector (Feedback Management)

**Purpose:** User feedback collection and analysis
**الهدف:** جمع وتحليل تعليقات المستخدمين

**Constructor:**
```python
FeedbackCollector(performance_monitor: PerformanceMonitor)
```

**Methods:**

```python
async submit_feedback(
    request_id: str,
    rating: int,
    comments: str = "",
    agent_id: Optional[str] = None
) -> str
"""
Submit user feedback for a request
إرسال تعليقات المستخدم لطلب

Args:
    request_id: Request identifier
    rating: Rating 1-5
    comments: Text comments
    agent_id: Optional agent ID (auto-detected if not provided)

Returns:
    Feedback ID
"""

async submit_outcome(
    request_id: str,
    actual_result: Any,
    agent_id: Optional[str] = None
) -> bool
"""
Submit actual outcome for accuracy tracking
إرسال النتيجة الفعلية لتتبع الدقة

Args:
    request_id: Request identifier
    actual_result: The actual outcome
    agent_id: Optional agent ID

Returns:
    True if recorded
"""

async get_feedback_summary(
    agent_id: str,
    time_window: Optional[timedelta] = None
) -> Dict[str, Any]
"""
Get feedback summary for an agent
الحصول على ملخص التعليقات لوكيل

Args:
    agent_id: Agent identifier
    time_window: Optional time window for feedback

Returns:
    Feedback summary with ratings, distribution, comments
"""

async identify_improvement_areas(agent_id: str) -> List[Dict[str, Any]]
"""
Identify areas for improvement based on feedback
تحديد مجالات التحسين بناءً على التعليقات

Args:
    agent_id: Agent identifier

Returns:
    List of improvement areas with mentions, priority, suggestions
"""
```

---

## Enums / التعدادات

### MetricType
```python
class MetricType(str, Enum):
    COUNTER = "counter"        # Monotonically increasing counter
    GAUGE = "gauge"            # Current value that can go up/down
    HISTOGRAM = "histogram"    # Distribution of values
```

### FeedbackRating
```python
class FeedbackRating(int, Enum):
    VERY_POOR = 1     # سيء جداً
    POOR = 2          # سيء
    FAIR = 3          # مقبول
    GOOD = 4          # جيد
    EXCELLENT = 5     # ممتاز
```

### ImprovementArea
```python
class ImprovementArea(str, Enum):
    RESPONSE_TIME = "response_time"              # وقت الاستجابة
    ACCURACY = "accuracy"                        # الدقة
    CONFIDENCE = "confidence"                    # الثقة
    USER_SATISFACTION = "user_satisfaction"      # رضا المستخدم
    COST_EFFICIENCY = "cost_efficiency"          # كفاءة التكلفة
    ERROR_RATE = "error_rate"                    # معدل الخطأ
```

---

## Data Models / نماذج البيانات

### RequestRecord
```python
@dataclass
class RequestRecord:
    request_id: str                         # Unique request ID
    agent_id: str                           # Agent ID
    timestamp: datetime                     # Request timestamp
    request_data: Dict[str, Any]            # Request payload
    response_data: Optional[Dict[str, Any]] # Response payload
    success: bool                           # Success status
    latency: float                          # Response time (seconds)
    confidence: float                       # Confidence score
    tokens_used: int                        # Tokens used
    error: Optional[str]                    # Error message
```

### FeedbackRecord
```python
@dataclass
class FeedbackRecord:
    feedback_id: str              # Unique feedback ID
    request_id: str               # Associated request ID
    agent_id: str                 # Agent ID
    rating: FeedbackRating        # Rating (1-5)
    comments: str                 # Text comments
    actual_outcome: Optional[Any] # Actual outcome for accuracy
    timestamp: datetime           # Feedback timestamp
```

---

## Prometheus Metrics / مقاييس Prometheus

### Counters
```
sahool_agent_requests_total{agent_id, agent_type, status}
sahool_agent_tokens_total{agent_id, agent_type}
sahool_agent_cost_dollars{agent_id, agent_type}
```

### Gauges
```
sahool_agent_confidence_score{agent_id, agent_type}
sahool_agent_accuracy_score{agent_id, agent_type}
sahool_agent_satisfaction_score{agent_id, agent_type}
```

### Histograms
```
sahool_agent_response_time_seconds{agent_id, agent_type}
  Buckets: [0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0]
```

---

## Quick Usage Example / مثال استخدام سريع

```python
import asyncio
from multi_agent.monitoring import PerformanceMonitor, FeedbackCollector

async def main():
    # Initialize
    monitor = PerformanceMonitor()
    collector = FeedbackCollector(monitor)

    # Track request
    request_id = await monitor.record_request(
        agent_id="disease-expert",
        request_data={"query": "diagnose wheat rust"}
    )

    # Record response
    await monitor.record_response(
        agent_id="disease-expert",
        response_data={"diagnosis": "yellow_rust"},
        success=True,
        latency=1.5,
        confidence=0.92,
        tokens_used=150
    )

    # Collect feedback
    await collector.submit_feedback(
        request_id=request_id,
        rating=5,
        comments="Excellent!"
    )

    # Get metrics
    metrics = await monitor.get_metrics("disease-expert")
    print(f"Success rate: {metrics.success_rate():.2f}%")

asyncio.run(main())
```

---

## File Locations / مواقع الملفات

```
/home/user/sahool-unified-v15-idp/apps/services/ai-advisor/src/multi_agent/monitoring/
├── performance_monitor.py    # Core implementation
├── __init__.py               # Module exports
├── example_usage.py          # Comprehensive examples
├── requirements.txt          # Dependencies
├── README.md                 # Full documentation
├── ARCHITECTURE.md           # System architecture
├── QUICKSTART.md             # Quick start guide
└── API_SUMMARY.md            # This file
```

---

For complete documentation, see README.md
للوثائق الكاملة، راجع README.md
