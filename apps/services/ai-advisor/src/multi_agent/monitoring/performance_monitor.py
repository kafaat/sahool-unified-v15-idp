"""
SAHOOL Multi-Agent Performance Monitoring and Feedback System
نظام مراقبة الأداء والتعليقات للوكلاء المتعدد لسهول

Comprehensive performance tracking, metrics collection, and feedback management
for agricultural AI agents with Prometheus integration.

تتبع شامل للأداء، جمع المقاييس، وإدارة التعليقات للوكلاء الذكيين الزراعيين
مع تكامل Prometheus.

Features / الميزات:
- Real-time performance metrics / مقاييس الأداء في الوقت الفعلي
- Request/response tracking / تتبع الطلبات والاستجابات
- User feedback collection / جمع تعليقات المستخدمين
- Accuracy calculation / حساب الدقة
- Performance recommendations / توصيات الأداء
- Prometheus metrics export / تصدير مقاييس Prometheus
- Multi-format export (JSON, Prometheus) / تصدير متعدد الصيغ
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import json
import asyncio
import statistics
import structlog
from collections import defaultdict, deque

# Prometheus imports (optional - gracefully degrade if not available)
try:
    from prometheus_client import Counter, Gauge, Histogram, CollectorRegistry, generate_latest
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    # Create dummy classes for type hints
    class Counter: pass
    class Gauge: pass
    class Histogram: pass
    class CollectorRegistry: pass

logger = structlog.get_logger()


# ═══════════════════════════════════════════════════════════════════════════════
# Enums / التعدادات
# ═══════════════════════════════════════════════════════════════════════════════

class MetricType(str, Enum):
    """
    Metric types for monitoring
    أنواع المقاييس للمراقبة
    """
    COUNTER = "counter"  # عداد - Monotonically increasing counter
    GAUGE = "gauge"  # مقياس - Current value that can go up/down
    HISTOGRAM = "histogram"  # مدرج تكراري - Distribution of values


class FeedbackRating(int, Enum):
    """
    User feedback rating scale
    مقياس تقييم تعليقات المستخدم
    """
    VERY_POOR = 1  # سيء جداً
    POOR = 2  # سيء
    FAIR = 3  # مقبول
    GOOD = 4  # جيد
    EXCELLENT = 5  # ممتاز


class ImprovementArea(str, Enum):
    """
    Areas for agent improvement
    مجالات تحسين الوكيل
    """
    RESPONSE_TIME = "response_time"  # وقت الاستجابة
    ACCURACY = "accuracy"  # الدقة
    CONFIDENCE = "confidence"  # الثقة
    USER_SATISFACTION = "user_satisfaction"  # رضا المستخدم
    COST_EFFICIENCY = "cost_efficiency"  # كفاءة التكلفة
    ERROR_RATE = "error_rate"  # معدل الخطأ


# ═══════════════════════════════════════════════════════════════════════════════
# Data Models / نماذج البيانات
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class AgentMetrics:
    """
    Comprehensive agent performance metrics
    مقاييس أداء شاملة للوكيل

    Tracks all performance indicators for an agent including requests,
    response times, accuracy, user satisfaction, and costs.

    يتتبع جميع مؤشرات الأداء للوكيل بما في ذلك الطلبات،
    أوقات الاستجابة، الدقة، رضا المستخدم، والتكاليف.
    """
    # Identity / الهوية
    agent_id: str  # معرف الوكيل الفريد
    agent_type: str  # نوع الوكيل (مثال: disease_expert, irrigation_advisor)

    # Request Statistics / إحصائيات الطلبات
    total_requests: int = 0  # إجمالي الطلبات
    successful_requests: int = 0  # الطلبات الناجحة
    failed_requests: int = 0  # الطلبات الفاشلة

    # Response Time Metrics / مقاييس وقت الاستجابة
    avg_response_time: float = 0.0  # متوسط وقت الاستجابة (ثواني)
    p95_response_time: float = 0.0  # النسبة المئوية 95 لوقت الاستجابة
    p99_response_time: float = 0.0  # النسبة المئوية 99 لوقت الاستجابة

    # Quality Metrics / مقاييس الجودة
    avg_confidence: float = 0.0  # متوسط الثقة (0.0-1.0)
    accuracy_score: float = 0.0  # درجة الدقة (0.0-1.0)
    user_satisfaction_score: float = 0.0  # درجة رضا المستخدم (0.0-5.0)

    # Cost Metrics / مقاييس التكلفة
    tokens_used: int = 0  # إجمالي الرموز المستخدمة
    cost_estimate: float = 0.0  # تقدير التكلفة (بالدولار)

    # Timestamps / الطوابع الزمنية
    last_updated: datetime = field(default_factory=datetime.utcnow)  # آخر تحديث
    created_at: datetime = field(default_factory=datetime.utcnow)  # تاريخ الإنشاء

    # Internal tracking (not serialized)
    _response_times: List[float] = field(default_factory=list, repr=False)  # أوقات الاستجابة
    _confidence_scores: List[float] = field(default_factory=list, repr=False)  # درجات الثقة
    _feedback_ratings: List[int] = field(default_factory=list, repr=False)  # تقييمات التعليقات

    def success_rate(self) -> float:
        """
        Calculate success rate
        حساب معدل النجاح
        """
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100

    def error_rate(self) -> float:
        """
        Calculate error rate
        حساب معدل الخطأ
        """
        if self.total_requests == 0:
            return 0.0
        return (self.failed_requests / self.total_requests) * 100

    def cost_per_request(self) -> float:
        """
        Calculate average cost per request
        حساب متوسط التكلفة لكل طلب
        """
        if self.total_requests == 0:
            return 0.0
        return self.cost_estimate / self.total_requests

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for serialization
        تحويل إلى قاموس للتسلسل
        """
        data = asdict(self)
        # Remove internal tracking fields
        data.pop('_response_times', None)
        data.pop('_confidence_scores', None)
        data.pop('_feedback_ratings', None)
        # Convert datetime to ISO format
        data['last_updated'] = self.last_updated.isoformat()
        data['created_at'] = self.created_at.isoformat()
        # Add computed metrics
        data['success_rate'] = self.success_rate()
        data['error_rate'] = self.error_rate()
        data['cost_per_request'] = self.cost_per_request()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentMetrics':
        """
        Create from dictionary
        إنشاء من قاموس
        """
        # Remove computed fields
        data.pop('success_rate', None)
        data.pop('error_rate', None)
        data.pop('cost_per_request', None)

        # Convert ISO datetime strings back to datetime objects
        if 'last_updated' in data and isinstance(data['last_updated'], str):
            data['last_updated'] = datetime.fromisoformat(data['last_updated'])
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])

        return cls(**data)


@dataclass
class RequestRecord:
    """
    Individual request tracking record
    سجل تتبع الطلب الفردي
    """
    request_id: str  # معرف الطلب الفريد
    agent_id: str  # معرف الوكيل
    timestamp: datetime = field(default_factory=datetime.utcnow)  # وقت الطلب
    request_data: Dict[str, Any] = field(default_factory=dict)  # بيانات الطلب
    response_data: Optional[Dict[str, Any]] = None  # بيانات الاستجابة
    success: bool = False  # نجح الطلب؟
    latency: float = 0.0  # زمن الاستجابة (ثواني)
    confidence: float = 0.0  # درجة الثقة
    tokens_used: int = 0  # الرموز المستخدمة
    error: Optional[str] = None  # رسالة الخطأ (إن وجدت)


@dataclass
class FeedbackRecord:
    """
    User feedback record
    سجل تعليقات المستخدم
    """
    feedback_id: str  # معرف التعليق الفريد
    request_id: str  # معرف الطلب المرتبط
    agent_id: str  # معرف الوكيل
    rating: FeedbackRating  # التقييم (1-5)
    comments: str = ""  # تعليقات نصية
    actual_outcome: Optional[Any] = None  # النتيجة الفعلية (للدقة)
    timestamp: datetime = field(default_factory=datetime.utcnow)  # وقت التعليق


# ═══════════════════════════════════════════════════════════════════════════════
# Performance Monitor / مراقب الأداء
# ═══════════════════════════════════════════════════════════════════════════════

class PerformanceMonitor:
    """
    Real-time performance monitoring for multi-agent system
    مراقبة الأداء في الوقت الفعلي لنظام الوكلاء المتعدد

    Tracks and analyzes performance metrics for all agents in the system,
    providing insights, recommendations, and exportable metrics.

    يتتبع ويحلل مقاييس الأداء لجميع الوكلاء في النظام،
    مع توفير رؤى وتوصيات ومقاييس قابلة للتصدير.

    Features:
    - Request/response tracking / تتبع الطلبات والاستجابات
    - Real-time metrics calculation / حساب المقاييس في الوقت الفعلي
    - Performance recommendations / توصيات الأداء
    - Multi-format export / تصدير متعدد الصيغ
    - Prometheus integration / تكامل Prometheus

    Example / مثال:
        ```python
        # Initialize monitor
        monitor = PerformanceMonitor()

        # Record a request
        await monitor.record_request(
            agent_id="disease-expert",
            request_data={"query": "wheat rust diagnosis"}
        )

        # Record response
        await monitor.record_response(
            agent_id="disease-expert",
            response_data={"diagnosis": "yellow rust"},
            success=True,
            latency=1.5
        )

        # Get metrics
        metrics = await monitor.get_metrics("disease-expert")
        print(f"Success rate: {metrics.success_rate():.2f}%")

        # Export to Prometheus
        prom_metrics = await monitor.export_metrics(format="prometheus")
        ```
    """

    def __init__(
        self,
        max_history: int = 1000,
        percentile_window: int = 100,
        enable_prometheus: bool = True,
    ):
        """
        Initialize performance monitor
        تهيئة مراقب الأداء

        Args:
            max_history: Maximum request history to keep / الحد الأقصى لسجل الطلبات
            percentile_window: Window for percentile calculations / نافذة حساب النسب المئوية
            enable_prometheus: Enable Prometheus metrics / تفعيل مقاييس Prometheus
        """
        self.max_history = max_history
        self.percentile_window = percentile_window
        self.enable_prometheus = enable_prometheus and PROMETHEUS_AVAILABLE

        # Storage
        self._metrics: Dict[str, AgentMetrics] = {}  # agent_id -> metrics
        self._requests: Dict[str, RequestRecord] = {}  # request_id -> record
        self._request_history: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=max_history)
        )  # agent_id -> deque of request_ids

        # Feedback storage
        self._feedback: Dict[str, FeedbackRecord] = {}  # feedback_id -> record
        self._request_feedback: Dict[str, List[str]] = defaultdict(list)  # request_id -> feedback_ids

        # Logger
        self._logger = logger.bind(component="performance_monitor")

        # Prometheus setup
        if self.enable_prometheus:
            self._setup_prometheus()
        else:
            self._logger.warning("prometheus_disabled", reason="prometheus_client not available")

    def _setup_prometheus(self):
        """
        Setup Prometheus metrics
        إعداد مقاييس Prometheus
        """
        if not PROMETHEUS_AVAILABLE:
            return

        # Create custom registry
        self.registry = CollectorRegistry()

        # Request counters
        self.request_counter = Counter(
            'sahool_agent_requests_total',
            'Total number of agent requests / إجمالي طلبات الوكيل',
            ['agent_id', 'agent_type', 'status'],
            registry=self.registry
        )

        # Response time histogram
        self.response_time_histogram = Histogram(
            'sahool_agent_response_time_seconds',
            'Agent response time in seconds / وقت استجابة الوكيل بالثواني',
            ['agent_id', 'agent_type'],
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0],
            registry=self.registry
        )

        # Confidence gauge
        self.confidence_gauge = Gauge(
            'sahool_agent_confidence_score',
            'Agent confidence score / درجة ثقة الوكيل',
            ['agent_id', 'agent_type'],
            registry=self.registry
        )

        # Accuracy gauge
        self.accuracy_gauge = Gauge(
            'sahool_agent_accuracy_score',
            'Agent accuracy score / درجة دقة الوكيل',
            ['agent_id', 'agent_type'],
            registry=self.registry
        )

        # User satisfaction gauge
        self.satisfaction_gauge = Gauge(
            'sahool_agent_satisfaction_score',
            'User satisfaction score / درجة رضا المستخدم',
            ['agent_id', 'agent_type'],
            registry=self.registry
        )

        # Token usage counter
        self.tokens_counter = Counter(
            'sahool_agent_tokens_total',
            'Total tokens used by agent / إجمالي الرموز المستخدمة',
            ['agent_id', 'agent_type'],
            registry=self.registry
        )

        # Cost counter
        self.cost_counter = Counter(
            'sahool_agent_cost_dollars',
            'Total cost in dollars / إجمالي التكلفة بالدولار',
            ['agent_id', 'agent_type'],
            registry=self.registry
        )

        self._logger.info("prometheus_initialized")

    # ─── Request Tracking ─────────────────────────────────────────────────

    async def record_request(
        self,
        agent_id: str,
        request_data: Dict[str, Any],
        request_id: Optional[str] = None,
    ) -> str:
        """
        Record a new agent request
        تسجيل طلب وكيل جديد

        Args:
            agent_id: Agent identifier / معرف الوكيل
            request_data: Request payload / بيانات الطلب
            request_id: Optional custom request ID / معرف طلب مخصص اختياري

        Returns:
            Request ID / معرف الطلب
        """
        # Generate request ID if not provided
        if not request_id:
            request_id = f"{agent_id}_{datetime.utcnow().timestamp()}"

        # Create request record
        record = RequestRecord(
            request_id=request_id,
            agent_id=agent_id,
            request_data=request_data,
        )

        # Store record
        self._requests[request_id] = record
        self._request_history[agent_id].append(request_id)

        # Initialize metrics if needed
        if agent_id not in self._metrics:
            self._metrics[agent_id] = AgentMetrics(
                agent_id=agent_id,
                agent_type=request_data.get('agent_type', 'unknown')
            )

        # Update total requests
        self._metrics[agent_id].total_requests += 1

        self._logger.info(
            "request_recorded",
            agent_id=agent_id,
            request_id=request_id
        )

        return request_id

    async def record_response(
        self,
        agent_id: str,
        response_data: Dict[str, Any],
        success: bool,
        latency: float,
        request_id: Optional[str] = None,
        confidence: float = 0.0,
        tokens_used: int = 0,
        error: Optional[str] = None,
    ) -> bool:
        """
        Record agent response
        تسجيل استجابة الوكيل

        Args:
            agent_id: Agent identifier / معرف الوكيل
            response_data: Response payload / بيانات الاستجابة
            success: Whether request succeeded / نجح الطلب أم لا
            latency: Response time in seconds / وقت الاستجابة بالثواني
            request_id: Associated request ID / معرف الطلب المرتبط
            confidence: Confidence score 0.0-1.0 / درجة الثقة
            tokens_used: Number of tokens consumed / عدد الرموز المستخدمة
            error: Error message if failed / رسالة الخطأ إن فشل

        Returns:
            True if recorded successfully / صحيح إذا تم التسجيل بنجاح
        """
        # Find or create request record
        if request_id and request_id in self._requests:
            record = self._requests[request_id]
        else:
            # Create new record if request_id not found
            record = RequestRecord(
                request_id=request_id or f"{agent_id}_response_{datetime.utcnow().timestamp()}",
                agent_id=agent_id,
            )
            self._requests[record.request_id] = record

        # Update record
        record.response_data = response_data
        record.success = success
        record.latency = latency
        record.confidence = confidence
        record.tokens_used = tokens_used
        record.error = error

        # Update metrics
        metrics = self._metrics.get(agent_id)
        if not metrics:
            metrics = AgentMetrics(
                agent_id=agent_id,
                agent_type=response_data.get('agent_type', 'unknown')
            )
            self._metrics[agent_id] = metrics

        # Update counters
        if success:
            metrics.successful_requests += 1
        else:
            metrics.failed_requests += 1

        # Update response times
        metrics._response_times.append(latency)
        if len(metrics._response_times) > self.percentile_window:
            metrics._response_times = metrics._response_times[-self.percentile_window:]

        # Calculate response time metrics
        metrics.avg_response_time = statistics.mean(metrics._response_times)
        if len(metrics._response_times) >= 2:
            sorted_times = sorted(metrics._response_times)
            p95_idx = int(len(sorted_times) * 0.95)
            p99_idx = int(len(sorted_times) * 0.99)
            metrics.p95_response_time = sorted_times[p95_idx]
            metrics.p99_response_time = sorted_times[p99_idx]

        # Update confidence
        if confidence > 0:
            metrics._confidence_scores.append(confidence)
            if len(metrics._confidence_scores) > self.percentile_window:
                metrics._confidence_scores = metrics._confidence_scores[-self.percentile_window:]
            metrics.avg_confidence = statistics.mean(metrics._confidence_scores)

        # Update cost metrics
        metrics.tokens_used += tokens_used
        # Estimate cost (example: $0.003 per 1K tokens for Claude)
        metrics.cost_estimate += (tokens_used / 1000) * 0.003

        # Update timestamp
        metrics.last_updated = datetime.utcnow()

        # Update Prometheus metrics
        if self.enable_prometheus:
            status = "success" if success else "failure"
            self.request_counter.labels(
                agent_id=agent_id,
                agent_type=metrics.agent_type,
                status=status
            ).inc()

            self.response_time_histogram.labels(
                agent_id=agent_id,
                agent_type=metrics.agent_type
            ).observe(latency)

            if confidence > 0:
                self.confidence_gauge.labels(
                    agent_id=agent_id,
                    agent_type=metrics.agent_type
                ).set(confidence)

            if tokens_used > 0:
                self.tokens_counter.labels(
                    agent_id=agent_id,
                    agent_type=metrics.agent_type
                ).inc(tokens_used)

                cost_delta = (tokens_used / 1000) * 0.003
                self.cost_counter.labels(
                    agent_id=agent_id,
                    agent_type=metrics.agent_type
                ).inc(cost_delta)

        self._logger.info(
            "response_recorded",
            agent_id=agent_id,
            request_id=record.request_id,
            success=success,
            latency=latency
        )

        return True

    # ─── Feedback Management ──────────────────────────────────────────────

    async def record_feedback(
        self,
        agent_id: str,
        request_id: str,
        feedback: Dict[str, Any],
        feedback_id: Optional[str] = None,
    ) -> str:
        """
        Record user feedback for a request
        تسجيل تعليقات المستخدم لطلب

        Args:
            agent_id: Agent identifier / معرف الوكيل
            request_id: Associated request ID / معرف الطلب المرتبط
            feedback: Feedback data including rating and comments / بيانات التعليقات
            feedback_id: Optional custom feedback ID / معرف تعليق مخصص اختياري

        Returns:
            Feedback ID / معرف التعليق
        """
        # Generate feedback ID if not provided
        if not feedback_id:
            feedback_id = f"fb_{request_id}_{datetime.utcnow().timestamp()}"

        # Extract rating
        rating_value = feedback.get('rating', 3)
        if isinstance(rating_value, int):
            rating = FeedbackRating(rating_value)
        else:
            rating = FeedbackRating.FAIR

        # Create feedback record
        record = FeedbackRecord(
            feedback_id=feedback_id,
            request_id=request_id,
            agent_id=agent_id,
            rating=rating,
            comments=feedback.get('comments', ''),
            actual_outcome=feedback.get('actual_outcome'),
        )

        # Store record
        self._feedback[feedback_id] = record
        self._request_feedback[request_id].append(feedback_id)

        # Update metrics
        metrics = self._metrics.get(agent_id)
        if metrics:
            metrics._feedback_ratings.append(rating.value)
            if len(metrics._feedback_ratings) > self.percentile_window:
                metrics._feedback_ratings = metrics._feedback_ratings[-self.percentile_window:]

            # Calculate average satisfaction
            if metrics._feedback_ratings:
                metrics.user_satisfaction_score = statistics.mean(metrics._feedback_ratings)

            # Update Prometheus
            if self.enable_prometheus:
                self.satisfaction_gauge.labels(
                    agent_id=agent_id,
                    agent_type=metrics.agent_type
                ).set(metrics.user_satisfaction_score)

        self._logger.info(
            "feedback_recorded",
            agent_id=agent_id,
            request_id=request_id,
            feedback_id=feedback_id,
            rating=rating.value
        )

        return feedback_id

    # ─── Metrics Retrieval ────────────────────────────────────────────────

    async def get_metrics(self, agent_id: str) -> Optional[AgentMetrics]:
        """
        Get performance metrics for a specific agent
        الحصول على مقاييس الأداء لوكيل محدد

        Args:
            agent_id: Agent identifier / معرف الوكيل

        Returns:
            Agent metrics or None / مقاييس الوكيل أو لا شيء
        """
        return self._metrics.get(agent_id)

    async def get_all_metrics(self) -> Dict[str, AgentMetrics]:
        """
        Get performance metrics for all agents
        الحصول على مقاييس الأداء لجميع الوكلاء

        Returns:
            Dictionary of agent_id to metrics / قاموس معرف الوكيل إلى المقاييس
        """
        return self._metrics.copy()

    # ─── Accuracy Calculation ─────────────────────────────────────────────

    async def calculate_accuracy(
        self,
        agent_id: str,
        actual_outcomes: List[Tuple[str, Any]],  # (request_id, actual_result)
    ) -> float:
        """
        Calculate agent accuracy based on actual outcomes
        حساب دقة الوكيل بناءً على النتائج الفعلية

        Args:
            agent_id: Agent identifier / معرف الوكيل
            actual_outcomes: List of (request_id, actual_result) tuples / قائمة النتائج الفعلية

        Returns:
            Accuracy score 0.0-1.0 / درجة الدقة
        """
        metrics = self._metrics.get(agent_id)
        if not metrics:
            return 0.0

        correct_predictions = 0
        total_predictions = 0

        for request_id, actual_result in actual_outcomes:
            request = self._requests.get(request_id)
            if not request or not request.response_data:
                continue

            # Extract prediction from response
            predicted_result = request.response_data.get('prediction')
            if predicted_result is None:
                continue

            total_predictions += 1

            # Compare prediction with actual (simple equality for now)
            if predicted_result == actual_result:
                correct_predictions += 1

        # Calculate accuracy
        if total_predictions > 0:
            accuracy = correct_predictions / total_predictions
            metrics.accuracy_score = accuracy
            metrics.last_updated = datetime.utcnow()

            # Update Prometheus
            if self.enable_prometheus:
                self.accuracy_gauge.labels(
                    agent_id=agent_id,
                    agent_type=metrics.agent_type
                ).set(accuracy)

            self._logger.info(
                "accuracy_calculated",
                agent_id=agent_id,
                accuracy=accuracy,
                correct=correct_predictions,
                total=total_predictions
            )

            return accuracy

        return 0.0

    # ─── Recommendations ──────────────────────────────────────────────────

    async def get_recommendations(
        self,
        agent_id: str,
        threshold_response_time: float = 5.0,
        threshold_accuracy: float = 0.8,
        threshold_satisfaction: float = 4.0,
    ) -> List[Dict[str, Any]]:
        """
        Get performance improvement recommendations
        الحصول على توصيات تحسين الأداء

        Args:
            agent_id: Agent identifier / معرف الوكيل
            threshold_response_time: Max acceptable response time / الحد الأقصى لوقت الاستجابة
            threshold_accuracy: Min acceptable accuracy / الحد الأدنى للدقة
            threshold_satisfaction: Min acceptable satisfaction / الحد الأدنى للرضا

        Returns:
            List of recommendations / قائمة التوصيات
        """
        metrics = await self.get_metrics(agent_id)
        if not metrics:
            return []

        recommendations = []

        # Response time check
        if metrics.avg_response_time > threshold_response_time:
            recommendations.append({
                'area': ImprovementArea.RESPONSE_TIME.value,
                'area_ar': 'وقت الاستجابة',
                'severity': 'high' if metrics.avg_response_time > threshold_response_time * 2 else 'medium',
                'current_value': metrics.avg_response_time,
                'target_value': threshold_response_time,
                'suggestion': f'Response time ({metrics.avg_response_time:.2f}s) exceeds threshold ({threshold_response_time}s). Consider optimization.',
                'suggestion_ar': f'وقت الاستجابة ({metrics.avg_response_time:.2f}ث) يتجاوز الحد المسموح ({threshold_response_time}ث). يُنصح بالتحسين.',
            })

        # Accuracy check
        if metrics.accuracy_score > 0 and metrics.accuracy_score < threshold_accuracy:
            recommendations.append({
                'area': ImprovementArea.ACCURACY.value,
                'area_ar': 'الدقة',
                'severity': 'high',
                'current_value': metrics.accuracy_score,
                'target_value': threshold_accuracy,
                'suggestion': f'Accuracy ({metrics.accuracy_score:.2%}) is below threshold ({threshold_accuracy:.2%}). Review model and prompts.',
                'suggestion_ar': f'الدقة ({metrics.accuracy_score:.2%}) أقل من الحد المطلوب ({threshold_accuracy:.2%}). راجع النموذج والمطالبات.',
            })

        # User satisfaction check
        if metrics.user_satisfaction_score > 0 and metrics.user_satisfaction_score < threshold_satisfaction:
            recommendations.append({
                'area': ImprovementArea.USER_SATISFACTION.value,
                'area_ar': 'رضا المستخدم',
                'severity': 'medium',
                'current_value': metrics.user_satisfaction_score,
                'target_value': threshold_satisfaction,
                'suggestion': f'User satisfaction ({metrics.user_satisfaction_score:.2f}/5.0) is below threshold. Analyze feedback comments.',
                'suggestion_ar': f'رضا المستخدم ({metrics.user_satisfaction_score:.2f}/5.0) أقل من الحد المطلوب. حلل تعليقات المستخدمين.',
            })

        # Confidence check
        if metrics.avg_confidence > 0 and metrics.avg_confidence < 0.7:
            recommendations.append({
                'area': ImprovementArea.CONFIDENCE.value,
                'area_ar': 'الثقة',
                'severity': 'low',
                'current_value': metrics.avg_confidence,
                'target_value': 0.8,
                'suggestion': f'Low confidence ({metrics.avg_confidence:.2%}). Consider model fine-tuning or additional context.',
                'suggestion_ar': f'ثقة منخفضة ({metrics.avg_confidence:.2%}). يُنصح بضبط دقيق للنموذج أو إضافة سياق.',
            })

        # Error rate check
        error_rate = metrics.error_rate()
        if error_rate > 5.0:  # More than 5% error rate
            recommendations.append({
                'area': ImprovementArea.ERROR_RATE.value,
                'area_ar': 'معدل الخطأ',
                'severity': 'high' if error_rate > 10.0 else 'medium',
                'current_value': error_rate,
                'target_value': 5.0,
                'suggestion': f'Error rate ({error_rate:.2f}%) is high. Review error logs and input validation.',
                'suggestion_ar': f'معدل الخطأ ({error_rate:.2f}%) مرتفع. راجع سجلات الأخطاء والتحقق من المدخلات.',
            })

        # Cost efficiency check
        cost_per_request = metrics.cost_per_request()
        if cost_per_request > 0.01:  # More than $0.01 per request
            recommendations.append({
                'area': ImprovementArea.COST_EFFICIENCY.value,
                'area_ar': 'كفاءة التكلفة',
                'severity': 'low',
                'current_value': cost_per_request,
                'target_value': 0.01,
                'suggestion': f'Cost per request (${cost_per_request:.4f}) is high. Consider token optimization.',
                'suggestion_ar': f'تكلفة كل طلب (${cost_per_request:.4f}) مرتفعة. يُنصح بتحسين استخدام الرموز.',
            })

        self._logger.info(
            "recommendations_generated",
            agent_id=agent_id,
            count=len(recommendations)
        )

        return recommendations

    # ─── Export ───────────────────────────────────────────────────────────

    async def export_metrics(self, format: str = "json") -> str:
        """
        Export metrics in specified format
        تصدير المقاييس بالصيغة المحددة

        Args:
            format: Export format ("json" or "prometheus") / صيغة التصدير

        Returns:
            Formatted metrics string / نص المقاييس المنسق
        """
        if format.lower() == "json":
            # Export as JSON
            export_data = {
                'timestamp': datetime.utcnow().isoformat(),
                'agents': {
                    agent_id: metrics.to_dict()
                    for agent_id, metrics in self._metrics.items()
                }
            }
            return json.dumps(export_data, ensure_ascii=False, indent=2)

        elif format.lower() == "prometheus":
            # Export Prometheus metrics
            if not self.enable_prometheus:
                raise ValueError("Prometheus not enabled")

            return generate_latest(self.registry).decode('utf-8')

        else:
            raise ValueError(f"Unsupported export format: {format}")


# ═══════════════════════════════════════════════════════════════════════════════
# Feedback Collector / جامع التعليقات
# ═══════════════════════════════════════════════════════════════════════════════

class FeedbackCollector:
    """
    User feedback collection and analysis
    جمع وتحليل تعليقات المستخدمين

    Collects and analyzes user feedback to improve agent performance,
    identify issues, and track satisfaction trends.

    يجمع ويحلل تعليقات المستخدمين لتحسين أداء الوكيل،
    تحديد المشاكل، وتتبع اتجاهات الرضا.

    Example / مثال:
        ```python
        # Initialize collector
        collector = FeedbackCollector(performance_monitor)

        # Submit user feedback
        await collector.submit_feedback(
            request_id="req_123",
            rating=5,
            comments="Excellent diagnosis and treatment plan"
        )

        # Submit actual outcome
        await collector.submit_outcome(
            request_id="req_123",
            actual_result="yellow_rust_confirmed"
        )

        # Get feedback summary
        summary = await collector.get_feedback_summary("disease-expert")

        # Identify improvement areas
        areas = await collector.identify_improvement_areas("disease-expert")
        ```
    """

    def __init__(self, performance_monitor: PerformanceMonitor):
        """
        Initialize feedback collector
        تهيئة جامع التعليقات

        Args:
            performance_monitor: Associated performance monitor / مراقب الأداء المرتبط
        """
        self.monitor = performance_monitor
        self._logger = logger.bind(component="feedback_collector")

    # ─── Feedback Submission ──────────────────────────────────────────────

    async def submit_feedback(
        self,
        request_id: str,
        rating: int,
        comments: str = "",
        agent_id: Optional[str] = None,
    ) -> str:
        """
        Submit user feedback for a request
        إرسال تعليقات المستخدم لطلب

        Args:
            request_id: Request identifier / معرف الطلب
            rating: Rating 1-5 / التقييم من 1 إلى 5
            comments: Text comments / تعليقات نصية
            agent_id: Optional agent ID (auto-detected if not provided) / معرف الوكيل

        Returns:
            Feedback ID / معرف التعليق
        """
        # Find agent_id if not provided
        if not agent_id:
            request = self.monitor._requests.get(request_id)
            if request:
                agent_id = request.agent_id
            else:
                raise ValueError(f"Request {request_id} not found and agent_id not provided")

        # Validate rating
        if rating < 1 or rating > 5:
            raise ValueError(f"Rating must be between 1 and 5, got {rating}")

        # Record feedback
        feedback_id = await self.monitor.record_feedback(
            agent_id=agent_id,
            request_id=request_id,
            feedback={
                'rating': rating,
                'comments': comments,
            }
        )

        self._logger.info(
            "feedback_submitted",
            request_id=request_id,
            agent_id=agent_id,
            rating=rating
        )

        return feedback_id

    async def submit_outcome(
        self,
        request_id: str,
        actual_result: Any,
        agent_id: Optional[str] = None,
    ) -> bool:
        """
        Submit actual outcome for accuracy tracking
        إرسال النتيجة الفعلية لتتبع الدقة

        Args:
            request_id: Request identifier / معرف الطلب
            actual_result: The actual outcome / النتيجة الفعلية
            agent_id: Optional agent ID / معرف الوكيل

        Returns:
            True if recorded / صحيح إذا تم التسجيل
        """
        # Find agent_id if not provided
        if not agent_id:
            request = self.monitor._requests.get(request_id)
            if request:
                agent_id = request.agent_id
            else:
                raise ValueError(f"Request {request_id} not found and agent_id not provided")

        # Record outcome
        feedback_id = await self.monitor.record_feedback(
            agent_id=agent_id,
            request_id=request_id,
            feedback={
                'actual_outcome': actual_result,
                'rating': 3,  # Neutral rating for outcome submission
            }
        )

        # Recalculate accuracy
        await self.monitor.calculate_accuracy(
            agent_id=agent_id,
            actual_outcomes=[(request_id, actual_result)]
        )

        self._logger.info(
            "outcome_submitted",
            request_id=request_id,
            agent_id=agent_id
        )

        return True

    # ─── Feedback Analysis ────────────────────────────────────────────────

    async def get_feedback_summary(
        self,
        agent_id: str,
        time_window: Optional[timedelta] = None,
    ) -> Dict[str, Any]:
        """
        Get feedback summary for an agent
        الحصول على ملخص التعليقات لوكيل

        Args:
            agent_id: Agent identifier / معرف الوكيل
            time_window: Optional time window for feedback / نافذة زمنية اختيارية

        Returns:
            Feedback summary / ملخص التعليقات
        """
        # Get all feedback for agent
        agent_feedback = [
            fb for fb in self.monitor._feedback.values()
            if fb.agent_id == agent_id
        ]

        # Filter by time window
        if time_window:
            cutoff = datetime.utcnow() - time_window
            agent_feedback = [
                fb for fb in agent_feedback
                if fb.timestamp >= cutoff
            ]

        if not agent_feedback:
            return {
                'agent_id': agent_id,
                'total_feedback': 0,
                'average_rating': 0.0,
                'rating_distribution': {},
                'recent_comments': [],
            }

        # Calculate statistics
        ratings = [fb.rating.value for fb in agent_feedback]
        avg_rating = statistics.mean(ratings)

        # Rating distribution
        rating_dist = {i: ratings.count(i) for i in range(1, 6)}

        # Get recent comments (last 10)
        recent_feedback = sorted(agent_feedback, key=lambda x: x.timestamp, reverse=True)[:10]
        recent_comments = [
            {
                'rating': fb.rating.value,
                'comments': fb.comments,
                'timestamp': fb.timestamp.isoformat(),
            }
            for fb in recent_feedback
            if fb.comments
        ]

        summary = {
            'agent_id': agent_id,
            'total_feedback': len(agent_feedback),
            'average_rating': round(avg_rating, 2),
            'rating_distribution': rating_dist,
            'recent_comments': recent_comments,
        }

        self._logger.info(
            "feedback_summary_generated",
            agent_id=agent_id,
            total=len(agent_feedback),
            avg_rating=avg_rating
        )

        return summary

    async def identify_improvement_areas(
        self,
        agent_id: str,
    ) -> List[Dict[str, Any]]:
        """
        Identify areas for improvement based on feedback
        تحديد مجالات التحسين بناءً على التعليقات

        Args:
            agent_id: Agent identifier / معرف الوكيل

        Returns:
            List of improvement areas with details / قائمة مجالات التحسين
        """
        # Get feedback summary
        summary = await self.get_feedback_summary(agent_id)

        # Get performance recommendations
        recommendations = await self.monitor.get_recommendations(agent_id)

        # Analyze comments for common themes
        agent_feedback = [
            fb for fb in self.monitor._feedback.values()
            if fb.agent_id == agent_id and fb.comments
        ]

        # Keywords for different improvement areas
        theme_keywords = {
            'response_time': ['slow', 'takes too long', 'wait', 'delayed', 'بطيء', 'انتظار'],
            'accuracy': ['wrong', 'incorrect', 'inaccurate', 'mistake', 'خطأ', 'غير دقيق'],
            'clarity': ['unclear', 'confusing', 'hard to understand', 'غير واضح', 'محير'],
            'completeness': ['incomplete', 'missing', 'not enough', 'ناقص', 'غير كامل'],
        }

        # Count theme occurrences
        theme_counts = defaultdict(int)
        for fb in agent_feedback:
            comments_lower = fb.comments.lower()
            for theme, keywords in theme_keywords.items():
                if any(keyword in comments_lower for keyword in keywords):
                    theme_counts[theme] += 1

        # Build improvement areas
        improvement_areas = []

        # Add theme-based improvements
        for theme, count in sorted(theme_counts.items(), key=lambda x: x[1], reverse=True):
            if count >= 2:  # At least 2 mentions
                improvement_areas.append({
                    'area': theme,
                    'mentions': count,
                    'source': 'user_feedback',
                    'priority': 'high' if count >= 5 else 'medium',
                })

        # Add performance-based improvements
        for rec in recommendations:
            improvement_areas.append({
                'area': rec['area'],
                'severity': rec['severity'],
                'source': 'performance_metrics',
                'current_value': rec['current_value'],
                'target_value': rec['target_value'],
                'suggestion': rec['suggestion'],
            })

        self._logger.info(
            "improvement_areas_identified",
            agent_id=agent_id,
            count=len(improvement_areas)
        )

        return improvement_areas
