"""
SAHOOL Performance Monitoring Service
خدمة مراقبة أداء سهول

Provides comprehensive performance monitoring including:
- Request tracking and latency monitoring
- Database query performance
- External API monitoring
- System resource usage
- Alerting thresholds
"""

import logging
import statistics
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from threading import Lock
from typing import Any, Literal

import psutil

logger = logging.getLogger(__name__)


@dataclass
class MetricPoint:
    """
    نقطة بيانات مقياس واحدة
    Single metric data point
    """
    timestamp: datetime
    value: float
    labels: dict[str, str] = field(default_factory=dict)


@dataclass
class PerformanceAlert:
    """
    تنبيه أداء
    Performance alert
    """
    alert_type: str
    severity: Literal["warning", "critical"]
    message: str
    message_ar: str
    timestamp: datetime
    value: float
    threshold: float


class CircularBuffer:
    """
    مخزن مؤقت دائري محدود الحجم لتخزين المقاييس
    Size-limited circular buffer for storing metrics
    """

    def __init__(self, max_size: int = 10000):
        self.max_size = max_size
        self.data: deque = deque(maxlen=max_size)
        self._lock = Lock()

    def append(self, item: MetricPoint):
        """إضافة عنصر إلى المخزن المؤقت"""
        with self._lock:
            self.data.append(item)

    def get_range(self, start_time: datetime, end_time: datetime | None = None) -> list[MetricPoint]:
        """الحصول على البيانات في نطاق زمني محدد"""
        if end_time is None:
            end_time = datetime.now()

        with self._lock:
            return [
                point for point in self.data
                if start_time <= point.timestamp <= end_time
            ]

    def get_recent(self, count: int) -> list[MetricPoint]:
        """الحصول على آخر N نقطة"""
        with self._lock:
            return list(self.data)[-count:]

    def clear(self):
        """مسح المخزن المؤقت"""
        with self._lock:
            self.data.clear()


class PerformanceMonitor:
    """
    مراقب أداء شامل لمنصة سهول
    Comprehensive performance monitor for SAHOOL platform

    Features:
    - Request latency tracking (p50, p95, p99)
    - Request throughput monitoring
    - Error rate tracking
    - Database query performance
    - External API latency
    - System resource monitoring
    - Automatic alerting
    """

    # Alert thresholds - عتبات التنبيه
    THRESHOLDS = {
        "response_time_warning": 1.0,  # 1 second
        "response_time_critical": 2.0,  # 2 seconds
        "error_rate_warning": 0.03,  # 3%
        "error_rate_critical": 0.05,  # 5%
        "memory_warning": 0.70,  # 70%
        "memory_critical": 0.80,  # 80%
        "cpu_warning": 0.70,  # 70%
        "cpu_critical": 0.85,  # 85%
        "db_query_warning": 0.5,  # 500ms
        "db_query_critical": 1.0,  # 1 second
    }

    def __init__(self, buffer_size: int = 10000, retention_period_hours: int = 24):
        """
        Initialize performance monitor

        Args:
            buffer_size: Maximum number of metrics to keep in memory
            retention_period_hours: How long to keep metrics (hours)
        """
        self._lock = Lock()
        self.retention_period = timedelta(hours=retention_period_hours)

        # Request metrics - مقاييس الطلبات
        self.request_latencies: dict[str, CircularBuffer] = defaultdict(
            lambda: CircularBuffer(buffer_size)
        )
        self.request_counts: dict[str, int] = defaultdict(int)
        self.error_counts: dict[str, dict[str, int]] = defaultdict(
            lambda: {"4xx": 0, "5xx": 0}
        )

        # Database metrics - مقاييس قاعدة البيانات
        self.db_query_times: dict[str, CircularBuffer] = defaultdict(
            lambda: CircularBuffer(buffer_size)
        )

        # External API metrics - مقاييس الخدمات الخارجية
        self.external_api_latencies: dict[str, CircularBuffer] = defaultdict(
            lambda: CircularBuffer(buffer_size)
        )
        self.external_api_success: dict[str, int] = defaultdict(int)
        self.external_api_failures: dict[str, int] = defaultdict(int)

        # System metrics - مقاييس النظام
        self.memory_usage: CircularBuffer = CircularBuffer(buffer_size)
        self.cpu_usage: CircularBuffer = CircularBuffer(buffer_size)

        # Alerts - التنبيهات
        self.active_alerts: list[PerformanceAlert] = []

        # Start time for uptime tracking
        self.start_time = datetime.now()

        logger.info("Performance monitor initialized - تم تهيئة مراقب الأداء")

    def track_request(
        self,
        endpoint: str,
        duration_ms: float,
        status: int,
        method: str = "GET"
    ):
        """
        تتبع طلب HTTP
        Track an HTTP request

        Args:
            endpoint: API endpoint path
            duration_ms: Request duration in milliseconds
            status: HTTP status code
            method: HTTP method (GET, POST, etc.)
        """
        with self._lock:
            # Record latency
            key = f"{method}:{endpoint}"
            point = MetricPoint(
                timestamp=datetime.now(),
                value=duration_ms,
                labels={"endpoint": endpoint, "method": method, "status": str(status)}
            )
            self.request_latencies[key].append(point)

            # Update counters
            self.request_counts[key] += 1

            # Track errors
            if 400 <= status < 500:
                self.error_counts[key]["4xx"] += 1
            elif status >= 500:
                self.error_counts[key]["5xx"] += 1

            # Check for alerts
            self._check_response_time_alert(endpoint, duration_ms)
            self._check_error_rate_alert(key)

        logger.debug(f"Tracked request: {method} {endpoint} - {duration_ms}ms - {status}")

    def track_db_query(
        self,
        query_type: str,
        duration_ms: float,
        success: bool = True,
        table: str | None = None
    ):
        """
        تتبع استعلام قاعدة البيانات
        Track a database query

        Args:
            query_type: Type of query (SELECT, INSERT, UPDATE, DELETE)
            duration_ms: Query duration in milliseconds
            success: Whether query succeeded
            table: Table name (optional)
        """
        with self._lock:
            key = query_type
            if table:
                key = f"{query_type}:{table}"

            point = MetricPoint(
                timestamp=datetime.now(),
                value=duration_ms,
                labels={
                    "query_type": query_type,
                    "success": str(success),
                    "table": table or "unknown"
                }
            )
            self.db_query_times[key].append(point)

            # Check for slow query alerts
            self._check_db_query_alert(key, duration_ms)

        logger.debug(f"Tracked DB query: {key} - {duration_ms}ms - success={success}")

    def track_external_api(
        self,
        service: str,
        duration_ms: float,
        success: bool,
        endpoint: str | None = None
    ):
        """
        تتبع استدعاء خدمة خارجية
        Track an external API call

        Args:
            service: Service name
            duration_ms: Call duration in milliseconds
            success: Whether the call succeeded
            endpoint: Specific endpoint (optional)
        """
        with self._lock:
            key = service
            if endpoint:
                key = f"{service}:{endpoint}"

            point = MetricPoint(
                timestamp=datetime.now(),
                value=duration_ms,
                labels={
                    "service": service,
                    "success": str(success),
                    "endpoint": endpoint or "unknown"
                }
            )
            self.external_api_latencies[key].append(point)

            # Update success/failure counters
            if success:
                self.external_api_success[key] += 1
            else:
                self.external_api_failures[key] += 1

        logger.debug(f"Tracked external API: {key} - {duration_ms}ms - success={success}")

    def record_system_metrics(self):
        """
        تسجيل مقاييس النظام (الذاكرة، المعالج)
        Record system metrics (memory, CPU)
        """
        try:
            # Memory usage
            memory = psutil.virtual_memory()
            memory_point = MetricPoint(
                timestamp=datetime.now(),
                value=memory.percent / 100.0,  # Convert to ratio
                labels={"type": "memory"}
            )
            self.memory_usage.append(memory_point)

            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_point = MetricPoint(
                timestamp=datetime.now(),
                value=cpu_percent / 100.0,  # Convert to ratio
                labels={"type": "cpu"}
            )
            self.cpu_usage.append(cpu_point)

            # Check for resource alerts
            self._check_memory_alert(memory.percent / 100.0)
            self._check_cpu_alert(cpu_percent / 100.0)

            logger.debug(f"System metrics: Memory={memory.percent:.1f}%, CPU={cpu_percent:.1f}%")
        except Exception as e:
            logger.error(f"Error recording system metrics: {e}")

    def get_metrics_summary(
        self,
        period: str = "1h",
        endpoint: str | None = None
    ) -> dict[str, Any]:
        """
        الحصول على ملخص المقاييس لفترة زمنية محددة
        Get metrics summary for a specific time period

        Args:
            period: Time period (e.g., '1h', '5m', '24h')
            endpoint: Specific endpoint to filter (optional)

        Returns:
            Dictionary with metrics summary
        """
        # Parse period
        period_delta = self._parse_period(period)
        start_time = datetime.now() - period_delta

        with self._lock:
            summary = {
                "period": period,
                "start_time": start_time.isoformat(),
                "end_time": datetime.now().isoformat(),
                "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
                "requests": self._get_request_summary(start_time, endpoint),
                "database": self._get_database_summary(start_time),
                "external_apis": self._get_external_api_summary(start_time),
                "system": self._get_system_summary(start_time),
                "alerts": [
                    {
                        "type": alert.alert_type,
                        "severity": alert.severity,
                        "message": alert.message,
                        "message_ar": alert.message_ar,
                        "timestamp": alert.timestamp.isoformat(),
                        "value": alert.value,
                        "threshold": alert.threshold
                    }
                    for alert in self.active_alerts
                ]
            }

        return summary

    def _get_request_summary(
        self,
        start_time: datetime,
        endpoint_filter: str | None = None
    ) -> dict[str, Any]:
        """Get summary of HTTP request metrics"""
        all_latencies = []
        total_requests = 0
        total_errors_4xx = 0
        total_errors_5xx = 0

        for key, buffer in self.request_latencies.items():
            if endpoint_filter and endpoint_filter not in key:
                continue

            points = buffer.get_range(start_time)
            if points:
                all_latencies.extend([p.value for p in points])

            if key in self.request_counts:
                total_requests += self.request_counts[key]

            if key in self.error_counts:
                total_errors_4xx += self.error_counts[key]["4xx"]
                total_errors_5xx += self.error_counts[key]["5xx"]

        # Calculate percentiles
        p50 = p95 = p99 = 0.0
        if all_latencies:
            all_latencies.sort()
            p50 = statistics.median(all_latencies)
            p95 = self._percentile(all_latencies, 0.95)
            p99 = self._percentile(all_latencies, 0.99)

        # Calculate throughput and error rate
        period_seconds = (datetime.now() - start_time).total_seconds()
        throughput = total_requests / period_seconds if period_seconds > 0 else 0
        error_rate = (total_errors_4xx + total_errors_5xx) / total_requests if total_requests > 0 else 0

        return {
            "total_requests": total_requests,
            "throughput_per_second": round(throughput, 2),
            "latency": {
                "p50_ms": round(p50, 2),
                "p95_ms": round(p95, 2),
                "p99_ms": round(p99, 2),
                "avg_ms": round(statistics.mean(all_latencies), 2) if all_latencies else 0,
            },
            "errors": {
                "4xx": total_errors_4xx,
                "5xx": total_errors_5xx,
                "total": total_errors_4xx + total_errors_5xx,
                "error_rate_percent": round(error_rate * 100, 2)
            }
        }

    def _get_database_summary(self, start_time: datetime) -> dict[str, Any]:
        """Get summary of database query metrics"""
        all_query_times = []
        query_counts = {}

        for key, buffer in self.db_query_times.items():
            points = buffer.get_range(start_time)
            if points:
                all_query_times.extend([p.value for p in points])
                query_type = key.split(":")[0]
                query_counts[query_type] = query_counts.get(query_type, 0) + len(points)

        p50 = p95 = p99 = 0.0
        if all_query_times:
            all_query_times.sort()
            p50 = statistics.median(all_query_times)
            p95 = self._percentile(all_query_times, 0.95)
            p99 = self._percentile(all_query_times, 0.99)

        return {
            "total_queries": len(all_query_times),
            "query_times": {
                "p50_ms": round(p50, 2),
                "p95_ms": round(p95, 2),
                "p99_ms": round(p99, 2),
                "avg_ms": round(statistics.mean(all_query_times), 2) if all_query_times else 0,
            },
            "by_type": query_counts
        }

    def _get_external_api_summary(self, start_time: datetime) -> dict[str, Any]:
        """Get summary of external API call metrics"""
        all_latencies = []
        total_success = sum(self.external_api_success.values())
        total_failures = sum(self.external_api_failures.values())

        for _key, buffer in self.external_api_latencies.items():
            points = buffer.get_range(start_time)
            if points:
                all_latencies.extend([p.value for p in points])

        p50 = p95 = p99 = 0.0
        if all_latencies:
            all_latencies.sort()
            p50 = statistics.median(all_latencies)
            p95 = self._percentile(all_latencies, 0.95)
            p99 = self._percentile(all_latencies, 0.99)

        total_calls = total_success + total_failures
        success_rate = (total_success / total_calls * 100) if total_calls > 0 else 0

        return {
            "total_calls": total_calls,
            "success": total_success,
            "failures": total_failures,
            "success_rate_percent": round(success_rate, 2),
            "latency": {
                "p50_ms": round(p50, 2),
                "p95_ms": round(p95, 2),
                "p99_ms": round(p99, 2),
                "avg_ms": round(statistics.mean(all_latencies), 2) if all_latencies else 0,
            }
        }

    def _get_system_summary(self, start_time: datetime) -> dict[str, Any]:
        """Get summary of system resource metrics"""
        memory_points = self.memory_usage.get_range(start_time)
        cpu_points = self.cpu_usage.get_range(start_time)

        memory_values = [p.value for p in memory_points]
        cpu_values = [p.value for p in cpu_points]

        return {
            "memory": {
                "current_percent": round(memory_values[-1] * 100, 2) if memory_values else 0,
                "avg_percent": round(statistics.mean(memory_values) * 100, 2) if memory_values else 0,
                "max_percent": round(max(memory_values) * 100, 2) if memory_values else 0,
            },
            "cpu": {
                "current_percent": round(cpu_values[-1] * 100, 2) if cpu_values else 0,
                "avg_percent": round(statistics.mean(cpu_values) * 100, 2) if cpu_values else 0,
                "max_percent": round(max(cpu_values) * 100, 2) if cpu_values else 0,
            }
        }

    def _check_response_time_alert(self, endpoint: str, duration_ms: float):
        """Check if response time exceeds thresholds"""
        duration_s = duration_ms / 1000.0

        if duration_s >= self.THRESHOLDS["response_time_critical"]:
            alert = PerformanceAlert(
                alert_type="response_time",
                severity="critical",
                message=f"Critical: Response time {duration_s:.2f}s exceeds threshold for {endpoint}",
                message_ar=f"حرج: زمن الاستجابة {duration_s:.2f}ث يتجاوز الحد المسموح لـ {endpoint}",
                timestamp=datetime.now(),
                value=duration_s,
                threshold=self.THRESHOLDS["response_time_critical"]
            )
            self._add_alert(alert)
        elif duration_s >= self.THRESHOLDS["response_time_warning"]:
            alert = PerformanceAlert(
                alert_type="response_time",
                severity="warning",
                message=f"Warning: Response time {duration_s:.2f}s approaching threshold for {endpoint}",
                message_ar=f"تحذير: زمن الاستجابة {duration_s:.2f}ث يقترب من الحد المسموح لـ {endpoint}",
                timestamp=datetime.now(),
                value=duration_s,
                threshold=self.THRESHOLDS["response_time_warning"]
            )
            self._add_alert(alert)

    def _check_error_rate_alert(self, key: str):
        """Check if error rate exceeds thresholds"""
        total_requests = self.request_counts.get(key, 0)
        if total_requests < 10:  # Need minimum requests for meaningful rate
            return

        total_errors = self.error_counts[key]["4xx"] + self.error_counts[key]["5xx"]
        error_rate = total_errors / total_requests

        if error_rate >= self.THRESHOLDS["error_rate_critical"]:
            alert = PerformanceAlert(
                alert_type="error_rate",
                severity="critical",
                message=f"Critical: Error rate {error_rate*100:.1f}% exceeds threshold for {key}",
                message_ar=f"حرج: معدل الأخطاء {error_rate*100:.1f}% يتجاوز الحد المسموح لـ {key}",
                timestamp=datetime.now(),
                value=error_rate,
                threshold=self.THRESHOLDS["error_rate_critical"]
            )
            self._add_alert(alert)
        elif error_rate >= self.THRESHOLDS["error_rate_warning"]:
            alert = PerformanceAlert(
                alert_type="error_rate",
                severity="warning",
                message=f"Warning: Error rate {error_rate*100:.1f}% approaching threshold for {key}",
                message_ar=f"تحذير: معدل الأخطاء {error_rate*100:.1f}% يقترب من الحد المسموح لـ {key}",
                timestamp=datetime.now(),
                value=error_rate,
                threshold=self.THRESHOLDS["error_rate_warning"]
            )
            self._add_alert(alert)

    def _check_db_query_alert(self, key: str, duration_ms: float):
        """Check if database query time exceeds thresholds"""
        duration_s = duration_ms / 1000.0

        if duration_s >= self.THRESHOLDS["db_query_critical"]:
            alert = PerformanceAlert(
                alert_type="slow_query",
                severity="critical",
                message=f"Critical: DB query {key} took {duration_s:.2f}s",
                message_ar=f"حرج: استعلام قاعدة البيانات {key} استغرق {duration_s:.2f}ث",
                timestamp=datetime.now(),
                value=duration_s,
                threshold=self.THRESHOLDS["db_query_critical"]
            )
            self._add_alert(alert)
        elif duration_s >= self.THRESHOLDS["db_query_warning"]:
            alert = PerformanceAlert(
                alert_type="slow_query",
                severity="warning",
                message=f"Warning: DB query {key} took {duration_s:.2f}s",
                message_ar=f"تحذير: استعلام قاعدة البيانات {key} استغرق {duration_s:.2f}ث",
                timestamp=datetime.now(),
                value=duration_s,
                threshold=self.THRESHOLDS["db_query_warning"]
            )
            self._add_alert(alert)

    def _check_memory_alert(self, memory_ratio: float):
        """Check if memory usage exceeds thresholds"""
        if memory_ratio >= self.THRESHOLDS["memory_critical"]:
            alert = PerformanceAlert(
                alert_type="memory_usage",
                severity="critical",
                message=f"Critical: Memory usage {memory_ratio*100:.1f}% exceeds threshold",
                message_ar=f"حرج: استخدام الذاكرة {memory_ratio*100:.1f}% يتجاوز الحد المسموح",
                timestamp=datetime.now(),
                value=memory_ratio,
                threshold=self.THRESHOLDS["memory_critical"]
            )
            self._add_alert(alert)
        elif memory_ratio >= self.THRESHOLDS["memory_warning"]:
            alert = PerformanceAlert(
                alert_type="memory_usage",
                severity="warning",
                message=f"Warning: Memory usage {memory_ratio*100:.1f}% approaching threshold",
                message_ar=f"تحذير: استخدام الذاكرة {memory_ratio*100:.1f}% يقترب من الحد المسموح",
                timestamp=datetime.now(),
                value=memory_ratio,
                threshold=self.THRESHOLDS["memory_warning"]
            )
            self._add_alert(alert)

    def _check_cpu_alert(self, cpu_ratio: float):
        """Check if CPU usage exceeds thresholds"""
        if cpu_ratio >= self.THRESHOLDS["cpu_critical"]:
            alert = PerformanceAlert(
                alert_type="cpu_usage",
                severity="critical",
                message=f"Critical: CPU usage {cpu_ratio*100:.1f}% exceeds threshold",
                message_ar=f"حرج: استخدام المعالج {cpu_ratio*100:.1f}% يتجاوز الحد المسموح",
                timestamp=datetime.now(),
                value=cpu_ratio,
                threshold=self.THRESHOLDS["cpu_critical"]
            )
            self._add_alert(alert)
        elif cpu_ratio >= self.THRESHOLDS["cpu_warning"]:
            alert = PerformanceAlert(
                alert_type="cpu_usage",
                severity="warning",
                message=f"Warning: CPU usage {cpu_ratio*100:.1f}% approaching threshold",
                message_ar=f"تحذير: استخدام المعالج {cpu_ratio*100:.1f}% يقترب من الحد المسموح",
                timestamp=datetime.now(),
                value=cpu_ratio,
                threshold=self.THRESHOLDS["cpu_warning"]
            )
            self._add_alert(alert)

    def _add_alert(self, alert: PerformanceAlert):
        """Add alert and limit to most recent 100"""
        self.active_alerts.append(alert)
        if len(self.active_alerts) > 100:
            self.active_alerts = self.active_alerts[-100:]
        logger.warning(f"Performance alert: {alert.message}")

    def clear_alerts(self):
        """مسح جميع التنبيهات النشطة - Clear all active alerts"""
        with self._lock:
            self.active_alerts.clear()

    @staticmethod
    def _percentile(data: list[float], percentile: float) -> float:
        """Calculate percentile from sorted data"""
        if not data:
            return 0.0
        k = (len(data) - 1) * percentile
        f = int(k)
        c = k - f
        if f + 1 < len(data):
            return data[f] + c * (data[f + 1] - data[f])
        return data[f]

    @staticmethod
    def _parse_period(period: str) -> timedelta:
        """Parse period string like '1h', '5m', '24h' to timedelta"""
        if not period:
            return timedelta(hours=1)

        unit = period[-1].lower()
        try:
            value = int(period[:-1])
        except ValueError:
            return timedelta(hours=1)

        if unit == 'h':
            return timedelta(hours=value)
        elif unit == 'm':
            return timedelta(minutes=value)
        elif unit == 's':
            return timedelta(seconds=value)
        elif unit == 'd':
            return timedelta(days=value)
        else:
            return timedelta(hours=1)


# Global instance - النسخة العامة
_monitor: PerformanceMonitor | None = None


def get_monitor() -> PerformanceMonitor:
    """
    الحصول على أو إنشاء مثيل مراقب الأداء العام
    Get or create the global performance monitor instance
    """
    global _monitor
    if _monitor is None:
        _monitor = PerformanceMonitor()
    return _monitor
