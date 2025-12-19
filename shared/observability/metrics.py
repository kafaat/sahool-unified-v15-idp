"""
Metrics Collection for Python Services
جمع المقاييس لخدمات Python

Provides Prometheus-compatible metrics for monitoring.
"""

from typing import Optional, Callable, Any
from functools import wraps
import time
from contextlib import contextmanager

try:
    from prometheus_client import Counter, Histogram, Gauge, Info, CollectorRegistry, generate_latest
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False


class MetricsCollector:
    """
    Metrics collector for service monitoring.
    جامع المقاييس لمراقبة الخدمات.
    """

    def __init__(self, service_name: str, registry: Optional['CollectorRegistry'] = None):
        self.service_name = service_name
        self.registry = registry
        self._metrics: dict[str, Any] = {}

        if not PROMETHEUS_AVAILABLE:
            return

        # Default metrics
        self._setup_default_metrics()

    def _setup_default_metrics(self) -> None:
        """Setup default metrics for all services."""
        if not PROMETHEUS_AVAILABLE:
            return

        # Request metrics
        self._metrics['requests_total'] = Counter(
            f'{self.service_name}_requests_total',
            'Total number of requests',
            ['method', 'endpoint', 'status'],
            registry=self.registry,
        )

        self._metrics['request_duration'] = Histogram(
            f'{self.service_name}_request_duration_seconds',
            'Request duration in seconds',
            ['method', 'endpoint'],
            buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
            registry=self.registry,
        )

        # Error metrics
        self._metrics['errors_total'] = Counter(
            f'{self.service_name}_errors_total',
            'Total number of errors',
            ['type', 'severity'],
            registry=self.registry,
        )

        # Active connections/workers
        self._metrics['active_connections'] = Gauge(
            f'{self.service_name}_active_connections',
            'Number of active connections',
            registry=self.registry,
        )

        # Service info
        self._metrics['info'] = Info(
            f'{self.service_name}_info',
            'Service information',
            registry=self.registry,
        )

    def record_request(
        self,
        method: str,
        endpoint: str,
        status: int,
        duration: float,
    ) -> None:
        """
        Record a request metric.
        تسجيل مقياس طلب.
        """
        if not PROMETHEUS_AVAILABLE:
            return

        self._metrics['requests_total'].labels(
            method=method,
            endpoint=endpoint,
            status=str(status),
        ).inc()

        self._metrics['request_duration'].labels(
            method=method,
            endpoint=endpoint,
        ).observe(duration)

    def record_error(self, error_type: str, severity: str = 'error') -> None:
        """
        Record an error metric.
        تسجيل مقياس خطأ.
        """
        if not PROMETHEUS_AVAILABLE:
            return

        self._metrics['errors_total'].labels(
            type=error_type,
            severity=severity,
        ).inc()

    def set_active_connections(self, count: int) -> None:
        """
        Set active connections gauge.
        تعيين عداد الاتصالات النشطة.
        """
        if not PROMETHEUS_AVAILABLE:
            return

        self._metrics['active_connections'].set(count)

    def increment_active_connections(self) -> None:
        """Increment active connections."""
        if not PROMETHEUS_AVAILABLE:
            return
        self._metrics['active_connections'].inc()

    def decrement_active_connections(self) -> None:
        """Decrement active connections."""
        if not PROMETHEUS_AVAILABLE:
            return
        self._metrics['active_connections'].dec()

    def set_info(self, version: str, environment: str, **kwargs: str) -> None:
        """
        Set service info.
        تعيين معلومات الخدمة.
        """
        if not PROMETHEUS_AVAILABLE:
            return

        info_dict = {
            'version': version,
            'environment': environment,
            **kwargs,
        }
        self._metrics['info'].info(info_dict)

    def create_counter(
        self,
        name: str,
        description: str,
        labels: Optional[list[str]] = None,
    ) -> Optional['Counter']:
        """
        Create a custom counter.
        إنشاء عداد مخصص.
        """
        if not PROMETHEUS_AVAILABLE:
            return None

        full_name = f'{self.service_name}_{name}'
        counter = Counter(
            full_name,
            description,
            labels or [],
            registry=self.registry,
        )
        self._metrics[name] = counter
        return counter

    def create_histogram(
        self,
        name: str,
        description: str,
        labels: Optional[list[str]] = None,
        buckets: Optional[list[float]] = None,
    ) -> Optional['Histogram']:
        """
        Create a custom histogram.
        إنشاء مدرج تكراري مخصص.
        """
        if not PROMETHEUS_AVAILABLE:
            return None

        full_name = f'{self.service_name}_{name}'
        histogram = Histogram(
            full_name,
            description,
            labels or [],
            buckets=buckets or Histogram.DEFAULT_BUCKETS,
            registry=self.registry,
        )
        self._metrics[name] = histogram
        return histogram

    def create_gauge(
        self,
        name: str,
        description: str,
        labels: Optional[list[str]] = None,
    ) -> Optional['Gauge']:
        """
        Create a custom gauge.
        إنشاء مقياس مخصص.
        """
        if not PROMETHEUS_AVAILABLE:
            return None

        full_name = f'{self.service_name}_{name}'
        gauge = Gauge(
            full_name,
            description,
            labels or [],
            registry=self.registry,
        )
        self._metrics[name] = gauge
        return gauge

    @contextmanager
    def measure_time(self, metric_name: str, labels: Optional[dict[str, str]] = None):
        """
        Context manager to measure execution time.
        مدير سياق لقياس وقت التنفيذ.
        """
        start = time.perf_counter()
        try:
            yield
        finally:
            duration = time.perf_counter() - start
            if PROMETHEUS_AVAILABLE and metric_name in self._metrics:
                metric = self._metrics[metric_name]
                if labels:
                    metric.labels(**labels).observe(duration)
                else:
                    metric.observe(duration)

    def get_metrics(self) -> bytes:
        """
        Get metrics in Prometheus format.
        الحصول على المقاييس بتنسيق Prometheus.
        """
        if not PROMETHEUS_AVAILABLE:
            return b''

        return generate_latest(self.registry)


def timed(metric_name: str, labels_func: Optional[Callable[..., dict[str, str]]] = None):
    """
    Decorator to measure function execution time.
    مزخرف لقياس وقت تنفيذ الدالة.

    Example:
        @timed('process_duration', lambda field_id: {'field_id': field_id})
        def process_field(field_id: str):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            try:
                return func(*args, **kwargs)
            finally:
                duration = time.perf_counter() - start
                labels = labels_func(*args, **kwargs) if labels_func else {}
                # Log timing (metrics collector would need to be injected)
                # For now, just print in debug mode
                import os
                if os.getenv('DEBUG'):
                    print(f"[TIMING] {metric_name}: {duration:.4f}s {labels}")
        return wrapper
    return decorator


# NDVI-specific metrics
class NDVIMetrics(MetricsCollector):
    """
    NDVI-specific metrics collector.
    جامع مقاييس NDVI.
    """

    def __init__(self, registry: Optional['CollectorRegistry'] = None):
        super().__init__('ndvi_processor', registry)
        self._setup_ndvi_metrics()

    def _setup_ndvi_metrics(self) -> None:
        """Setup NDVI-specific metrics."""
        if not PROMETHEUS_AVAILABLE:
            return

        self._metrics['calculations_total'] = Counter(
            'ndvi_calculations_total',
            'Total NDVI calculations',
            ['satellite_source'],
            registry=self.registry,
        )

        self._metrics['calculation_duration'] = Histogram(
            'ndvi_calculation_duration_seconds',
            'NDVI calculation duration',
            ['field_size_category'],
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0],
            registry=self.registry,
        )

        self._metrics['ndvi_values'] = Histogram(
            'ndvi_mean_values',
            'Distribution of mean NDVI values',
            buckets=[-1.0, -0.5, 0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
            registry=self.registry,
        )

        self._metrics['anomalies_detected'] = Counter(
            'ndvi_anomalies_detected_total',
            'Total NDVI anomalies detected',
            ['anomaly_type'],
            registry=self.registry,
        )

    def record_calculation(
        self,
        satellite_source: str,
        duration: float,
        field_size_hectares: float,
        mean_ndvi: float,
    ) -> None:
        """Record an NDVI calculation."""
        if not PROMETHEUS_AVAILABLE:
            return

        self._metrics['calculations_total'].labels(
            satellite_source=satellite_source,
        ).inc()

        # Categorize field size
        if field_size_hectares < 10:
            size_category = 'small'
        elif field_size_hectares < 50:
            size_category = 'medium'
        else:
            size_category = 'large'

        self._metrics['calculation_duration'].labels(
            field_size_category=size_category,
        ).observe(duration)

        self._metrics['ndvi_values'].observe(mean_ndvi)

    def record_anomaly(self, anomaly_type: str) -> None:
        """Record an NDVI anomaly detection."""
        if not PROMETHEUS_AVAILABLE:
            return

        self._metrics['anomalies_detected'].labels(
            anomaly_type=anomaly_type,
        ).inc()
