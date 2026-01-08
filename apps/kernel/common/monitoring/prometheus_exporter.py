"""
SAHOOL Prometheus Metrics Exporter
مُصدّر مقاييس بروميثيوس لسهول

Exports performance metrics in Prometheus format with proper labels and types.
Integrates with PerformanceMonitor to provide real-time metrics.
"""

import logging
import time
from datetime import datetime

try:
    from prometheus_client import (
        REGISTRY,
        CollectorRegistry,
        Counter,
        Gauge,
        Histogram,
        Info,
        generate_latest,
    )

    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    logging.warning("prometheus_client not installed. Install with: pip install prometheus-client")

from .performance_monitor import get_monitor

logger = logging.getLogger(__name__)


class PrometheusExporter:
    """
    مُصدّر مقاييس بروميثيوس
    Prometheus metrics exporter for SAHOOL

    Exports metrics in Prometheus format with Arabic descriptions.
    Includes:
    - HTTP request metrics (counters, histograms)
    - Database query metrics
    - External API metrics
    - System resource metrics
    - Custom business metrics
    """

    def __init__(
        self,
        service_name: str = "sahool",
        namespace: str = "sahool",
        registry: CollectorRegistry | None = None,
    ):
        """
        Initialize Prometheus exporter

        Args:
            service_name: Service name for labels
            namespace: Metric namespace prefix
            registry: Custom registry (default: global REGISTRY)
        """
        if not PROMETHEUS_AVAILABLE:
            raise ImportError(
                "prometheus_client is required. Install with: pip install prometheus-client"
            )

        self.service_name = service_name
        self.namespace = namespace
        self.registry = registry or REGISTRY
        self.monitor = get_monitor()

        # Initialize metrics
        self._init_metrics()

        logger.info(f"Prometheus exporter initialized for service: {service_name}")

    def _init_metrics(self):
        """تهيئة جميع مقاييس بروميثيوس - Initialize all Prometheus metrics"""

        # Service info - معلومات الخدمة
        self.service_info = Info(
            f"{self.namespace}_service",
            "SAHOOL service information - معلومات خدمة سهول",
            registry=self.registry,
        )
        self.service_info.info(
            {
                "service": self.service_name,
                "version": "1.0.0",
                "platform": "SAHOOL Agricultural Platform",
            }
        )

        # HTTP Request Metrics - مقاييس طلبات HTTP
        self.http_requests_total = Counter(
            f"{self.namespace}_http_requests_total",
            "Total HTTP requests - إجمالي طلبات HTTP",
            ["service", "method", "endpoint", "status"],
            registry=self.registry,
        )

        self.http_request_duration_seconds = Histogram(
            f"{self.namespace}_http_request_duration_seconds",
            "HTTP request latency in seconds - زمن استجابة طلبات HTTP بالثواني",
            ["service", "method", "endpoint"],
            buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
            registry=self.registry,
        )

        self.http_requests_active = Gauge(
            f"{self.namespace}_http_requests_active",
            "Currently active HTTP requests - طلبات HTTP النشطة حالياً",
            ["service"],
            registry=self.registry,
        )

        self.http_errors_total = Counter(
            f"{self.namespace}_http_errors_total",
            "Total HTTP errors - إجمالي أخطاء HTTP",
            ["service", "status_category"],
            registry=self.registry,
        )

        # Database Metrics - مقاييس قاعدة البيانات
        self.db_queries_total = Counter(
            f"{self.namespace}_db_queries_total",
            "Total database queries - إجمالي استعلامات قاعدة البيانات",
            ["service", "query_type", "table"],
            registry=self.registry,
        )

        self.db_query_duration_seconds = Histogram(
            f"{self.namespace}_db_query_duration_seconds",
            "Database query latency in seconds - زمن استعلامات قاعدة البيانات بالثواني",
            ["service", "query_type", "table"],
            buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5],
            registry=self.registry,
        )

        self.db_query_errors_total = Counter(
            f"{self.namespace}_db_query_errors_total",
            "Total database query errors - إجمالي أخطاء استعلامات قاعدة البيانات",
            ["service", "query_type"],
            registry=self.registry,
        )

        # External API Metrics - مقاييس الخدمات الخارجية
        self.external_api_calls_total = Counter(
            f"{self.namespace}_external_api_calls_total",
            "Total external API calls - إجمالي استدعاءات الخدمات الخارجية",
            ["service", "target", "success"],
            registry=self.registry,
        )

        self.external_api_duration_seconds = Histogram(
            f"{self.namespace}_external_api_duration_seconds",
            "External API call latency - زمن استدعاءات الخدمات الخارجية",
            ["service", "target"],
            buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
            registry=self.registry,
        )

        # System Resource Metrics - مقاييس موارد النظام
        self.system_memory_usage_ratio = Gauge(
            f"{self.namespace}_system_memory_usage_ratio",
            "System memory usage ratio - نسبة استخدام ذاكرة النظام",
            ["service"],
            registry=self.registry,
        )

        self.system_cpu_usage_ratio = Gauge(
            f"{self.namespace}_system_cpu_usage_ratio",
            "System CPU usage ratio - نسبة استخدام معالج النظام",
            ["service"],
            registry=self.registry,
        )

        # Alert Metrics - مقاييس التنبيهات
        self.alerts_total = Counter(
            f"{self.namespace}_alerts_total",
            "Total performance alerts - إجمالي تنبيهات الأداء",
            ["service", "alert_type", "severity"],
            registry=self.registry,
        )

        self.alerts_active = Gauge(
            f"{self.namespace}_alerts_active",
            "Currently active alerts - التنبيهات النشطة حالياً",
            ["service", "severity"],
            registry=self.registry,
        )

        # Uptime - وقت التشغيل
        self.uptime_seconds = Gauge(
            f"{self.namespace}_uptime_seconds",
            "Service uptime in seconds - وقت تشغيل الخدمة بالثواني",
            ["service"],
            registry=self.registry,
        )

    def record_http_request(self, method: str, endpoint: str, status: int, duration_seconds: float):
        """
        تسجيل طلب HTTP في بروميثيوس
        Record HTTP request in Prometheus

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            status: HTTP status code
            duration_seconds: Request duration in seconds
        """
        # Record in performance monitor
        self.monitor.track_request(endpoint, duration_seconds * 1000, status, method)

        # Update Prometheus metrics
        self.http_requests_total.labels(
            service=self.service_name, method=method, endpoint=endpoint, status=str(status)
        ).inc()

        self.http_request_duration_seconds.labels(
            service=self.service_name, method=method, endpoint=endpoint
        ).observe(duration_seconds)

        # Track errors
        if status >= 400:
            status_category = "4xx" if status < 500 else "5xx"
            self.http_errors_total.labels(
                service=self.service_name, status_category=status_category
            ).inc()

    def record_db_query(
        self, query_type: str, duration_seconds: float, table: str = "unknown", success: bool = True
    ):
        """
        تسجيل استعلام قاعدة البيانات
        Record database query

        Args:
            query_type: Query type (SELECT, INSERT, etc.)
            duration_seconds: Query duration in seconds
            table: Table name
            success: Whether query succeeded
        """
        # Record in performance monitor
        self.monitor.track_db_query(query_type, duration_seconds * 1000, success, table)

        # Update Prometheus metrics
        self.db_queries_total.labels(
            service=self.service_name, query_type=query_type, table=table
        ).inc()

        self.db_query_duration_seconds.labels(
            service=self.service_name, query_type=query_type, table=table
        ).observe(duration_seconds)

        if not success:
            self.db_query_errors_total.labels(
                service=self.service_name, query_type=query_type
            ).inc()

    def record_external_api_call(
        self, target: str, duration_seconds: float, success: bool, endpoint: str | None = None
    ):
        """
        تسجيل استدعاء خدمة خارجية
        Record external API call

        Args:
            target: Target service name
            duration_seconds: Call duration in seconds
            success: Whether call succeeded
            endpoint: Specific endpoint (optional)
        """
        # Record in performance monitor
        self.monitor.track_external_api(target, duration_seconds * 1000, success, endpoint)

        # Update Prometheus metrics
        self.external_api_calls_total.labels(
            service=self.service_name, target=target, success=str(success)
        ).inc()

        self.external_api_duration_seconds.labels(service=self.service_name, target=target).observe(
            duration_seconds
        )

    def update_system_metrics(self):
        """
        تحديث مقاييس موارد النظام
        Update system resource metrics
        """
        # Record in performance monitor (this also gets current metrics)
        self.monitor.record_system_metrics()

        # Get latest metrics and update Prometheus
        summary = self.monitor.get_metrics_summary(period="1m")

        if "system" in summary:
            system = summary["system"]

            # Memory
            if "memory" in system and "current_percent" in system["memory"]:
                memory_ratio = system["memory"]["current_percent"] / 100.0
                self.system_memory_usage_ratio.labels(service=self.service_name).set(memory_ratio)

            # CPU
            if "cpu" in system and "current_percent" in system["cpu"]:
                cpu_ratio = system["cpu"]["current_percent"] / 100.0
                self.system_cpu_usage_ratio.labels(service=self.service_name).set(cpu_ratio)

    def update_alert_metrics(self):
        """
        تحديث مقاييس التنبيهات
        Update alert metrics
        """
        alerts = self.monitor.active_alerts

        # Count alerts by severity
        warning_count = sum(1 for a in alerts if a.severity == "warning")
        critical_count = sum(1 for a in alerts if a.severity == "critical")

        self.alerts_active.labels(service=self.service_name, severity="warning").set(warning_count)

        self.alerts_active.labels(service=self.service_name, severity="critical").set(
            critical_count
        )

        # Increment total alerts counter
        for alert in alerts:
            self.alerts_total.labels(
                service=self.service_name, alert_type=alert.alert_type, severity=alert.severity
            ).inc()

    def update_uptime(self):
        """
        تحديث وقت التشغيل
        Update service uptime
        """
        uptime = (datetime.now() - self.monitor.start_time).total_seconds()
        self.uptime_seconds.labels(service=self.service_name).set(uptime)

    def export_metrics(self) -> bytes:
        """
        تصدير المقاييس بصيغة بروميثيوس
        Export metrics in Prometheus format

        Returns:
            Prometheus-formatted metrics as bytes
        """
        # Update dynamic metrics before export
        self.update_system_metrics()
        self.update_uptime()
        self.update_alert_metrics()

        return generate_latest(self.registry)

    def get_metrics_text(self) -> str:
        """
        الحصول على المقاييس كنص
        Get metrics as text

        Returns:
            Prometheus-formatted metrics as string
        """
        return self.export_metrics().decode("utf-8")


# Global exporter instance - النسخة العامة للمُصدّر
_exporter: PrometheusExporter | None = None


def get_exporter(service_name: str = "sahool") -> PrometheusExporter:
    """
    الحصول على أو إنشاء مثيل المُصدّر العام
    Get or create the global exporter instance

    Args:
        service_name: Name of the service

    Returns:
        PrometheusExporter instance
    """
    global _exporter
    if _exporter is None:
        _exporter = PrometheusExporter(service_name=service_name)
    return _exporter


def setup_prometheus_endpoint(app, service_name: str = "sahool"):
    """
    إعداد نقطة نهاية /metrics لـ FastAPI
    Setup /metrics endpoint for FastAPI

    Args:
        app: FastAPI application instance
        service_name: Name of the service
    """
    try:
        from fastapi import Response
        from fastapi.responses import PlainTextResponse
    except ImportError:
        logger.error("FastAPI not installed, cannot setup endpoint")
        return

    exporter = get_exporter(service_name)

    @app.get("/metrics", response_class=PlainTextResponse)
    async def metrics_endpoint():
        """
        Prometheus metrics endpoint
        نقطة نهاية مقاييس بروميثيوس
        """
        return exporter.get_metrics_text()

    @app.middleware("http")
    async def prometheus_middleware(request, call_next):
        """
        Middleware to automatically track HTTP requests
        وسيط لتتبع طلبات HTTP تلقائياً
        """
        # Skip metrics endpoint to avoid recursion
        if request.url.path == "/metrics":
            return await call_next(request)

        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time

        # Record metrics
        exporter.record_http_request(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code,
            duration_seconds=duration,
        )

        return response

    logger.info(f"Prometheus endpoint /metrics configured for {service_name}")


def track_db_operation(query_type: str, table: str = "unknown"):
    """
    ديكوراتور لتتبع عمليات قاعدة البيانات
    Decorator to track database operations

    Args:
        query_type: Type of query (SELECT, INSERT, etc.)
        table: Table name

    Example:
        @track_db_operation("SELECT", "users")
        async def get_user(user_id: int):
            ...
    """

    def decorator(func):
        async def wrapper(*args, **kwargs):
            exporter = get_exporter()
            start_time = time.time()
            success = True

            try:
                result = await func(*args, **kwargs)
                return result
            except Exception:
                success = False
                raise
            finally:
                duration = time.time() - start_time
                exporter.record_db_query(query_type, duration, table, success)

        return wrapper

    return decorator


def track_external_api(target: str, endpoint: str | None = None):
    """
    ديكوراتور لتتبع استدعاءات الخدمات الخارجية
    Decorator to track external API calls

    Args:
        target: Target service name
        endpoint: Specific endpoint (optional)

    Example:
        @track_external_api("weather_api", "/forecast")
        async def get_weather(location: str):
            ...
    """

    def decorator(func):
        async def wrapper(*args, **kwargs):
            exporter = get_exporter()
            start_time = time.time()
            success = True

            try:
                result = await func(*args, **kwargs)
                return result
            except Exception:
                success = False
                raise
            finally:
                duration = time.time() - start_time
                exporter.record_external_api_call(target, duration, success, endpoint)

        return wrapper

    return decorator
