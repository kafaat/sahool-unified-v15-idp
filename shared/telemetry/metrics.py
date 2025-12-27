"""
OpenTelemetry Metrics for SAHOOL Platform
==========================================

This module provides comprehensive metrics instrumentation for all
Python-based services in the SAHOOL agricultural platform.

Features:
- OpenTelemetry metrics (counters, histograms, gauges)
- Prometheus exporter for metrics scraping
- Request count, latency, error rate metrics
- Custom business metrics (fields, satellite requests, weather queries)
- Automatic metric labeling with service names

Usage:
    from shared.telemetry.metrics import init_metrics, track_request, track_business_metric

    # Initialize at application startup
    meter_provider = init_metrics(service_name="field_core")

    # Track HTTP requests
    track_request(method="GET", endpoint="/fields", status_code=200, duration=0.123)

    # Track business metrics
    track_business_metric("fields_created", value=1, labels={"user_id": "123"})

Author: SAHOOL Platform Team
Date: 2025-12-26
"""

import logging
import os
import time
from typing import Optional, Dict, Any
from contextlib import contextmanager

from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    PeriodicExportingMetricReader,
    ConsoleMetricExporter,
)
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION, DEPLOYMENT_ENVIRONMENT
from prometheus_client import start_http_server, REGISTRY

logger = logging.getLogger(__name__)

# Global meter instance
_meter: Optional[metrics.Meter] = None
_meter_provider: Optional[MeterProvider] = None

# Metrics instruments
_request_counter: Optional[metrics.Counter] = None
_request_duration: Optional[metrics.Histogram] = None
_error_counter: Optional[metrics.Counter] = None
_business_counters: Dict[str, metrics.Counter] = {}
_business_histograms: Dict[str, metrics.Histogram] = {}
_business_gauges: Dict[str, metrics.ObservableGauge] = {}


def init_metrics(
    service_name: Optional[str] = None,
    service_version: Optional[str] = None,
    environment: Optional[str] = None,
    prometheus_port: int = 9090,
    enable_prometheus: bool = True,
    enable_console: bool = False,
) -> MeterProvider:
    """
    Initialize OpenTelemetry metrics with Prometheus exporter.

    Args:
        service_name: Name of the service (auto-detected from env if not provided)
        service_version: Version of the service
        environment: Deployment environment (development, staging, production)
        prometheus_port: Port for Prometheus metrics endpoint
        enable_prometheus: Enable Prometheus exporter
        enable_console: Enable console exporter for debugging

    Returns:
        MeterProvider instance
    """
    global _meter_provider, _meter
    global _request_counter, _request_duration, _error_counter

    # Auto-detect service name from environment
    if not service_name:
        service_name = os.getenv("OTEL_SERVICE_NAME") or os.getenv("SERVICE_NAME", "sahool-service")

    if not service_version:
        service_version = os.getenv("SERVICE_VERSION", "1.0.0")

    if not environment:
        environment = os.getenv("ENVIRONMENT", "development")

    # Create resource with service information
    resource = Resource.create({
        SERVICE_NAME: service_name,
        SERVICE_VERSION: service_version,
        DEPLOYMENT_ENVIRONMENT: environment,
        "service.namespace": "sahool",
        "service.instance.id": os.getenv("HOSTNAME", "unknown"),
    })

    # Configure metric readers
    metric_readers = []

    # Add Prometheus exporter
    if enable_prometheus or os.getenv("PROMETHEUS_METRICS_ENABLED", "true").lower() == "true":
        try:
            prometheus_reader = PrometheusMetricReader()
            metric_readers.append(prometheus_reader)

            # Start Prometheus HTTP server
            prometheus_port = int(os.getenv("PROMETHEUS_PORT", prometheus_port))
            start_http_server(port=prometheus_port, registry=REGISTRY)
            logger.info(f"Prometheus metrics endpoint started on port {prometheus_port}")
        except Exception as e:
            logger.error(f"Failed to configure Prometheus exporter: {e}")

    # Add console exporter for debugging
    if enable_console or os.getenv("OTEL_CONSOLE_EXPORT", "false").lower() == "true":
        console_reader = PeriodicExportingMetricReader(
            ConsoleMetricExporter(),
            export_interval_millis=60000,  # 1 minute
        )
        metric_readers.append(console_reader)
        logger.info("Console metrics exporter enabled")

    # Create meter provider
    _meter_provider = MeterProvider(
        resource=resource,
        metric_readers=metric_readers,
    )

    # Set global meter provider
    metrics.set_meter_provider(_meter_provider)

    # Get meter instance
    _meter = metrics.get_meter(
        name=service_name,
        version=service_version,
    )

    # Initialize standard HTTP metrics
    _request_counter = _meter.create_counter(
        name="http_requests_total",
        description="Total number of HTTP requests",
        unit="1",
    )

    _request_duration = _meter.create_histogram(
        name="http_request_duration_seconds",
        description="HTTP request duration in seconds",
        unit="s",
    )

    _error_counter = _meter.create_counter(
        name="http_errors_total",
        description="Total number of HTTP errors",
        unit="1",
    )

    logger.info(f"OpenTelemetry metrics initialized: service={service_name}, env={environment}")

    return _meter_provider


def get_meter(name: Optional[str] = None, version: Optional[str] = None) -> metrics.Meter:
    """
    Get a meter instance.

    Args:
        name: Meter name (defaults to service name)
        version: Meter version

    Returns:
        Meter instance
    """
    if not _meter_provider:
        logger.warning("Meter provider not initialized, using default")
        return metrics.get_meter(name or __name__, version=version)

    return metrics.get_meter(name or __name__, version=version)


def track_request(
    method: str,
    endpoint: str,
    status_code: int,
    duration: float,
    labels: Optional[Dict[str, str]] = None,
) -> None:
    """
    Track HTTP request metrics.

    Args:
        method: HTTP method (GET, POST, etc.)
        endpoint: API endpoint
        status_code: HTTP status code
        duration: Request duration in seconds
        labels: Additional labels
    """
    if not _request_counter or not _request_duration:
        return

    attributes = {
        "http.method": method,
        "http.endpoint": endpoint,
        "http.status_code": status_code,
    }

    if labels:
        attributes.update(labels)

    # Count request
    _request_counter.add(1, attributes=attributes)

    # Record duration
    _request_duration.record(duration, attributes=attributes)

    # Count errors (4xx, 5xx)
    if status_code >= 400 and _error_counter:
        error_type = "client_error" if status_code < 500 else "server_error"
        error_attributes = {**attributes, "error.type": error_type}
        _error_counter.add(1, attributes=error_attributes)


@contextmanager
def track_request_duration(method: str, endpoint: str, labels: Optional[Dict[str, str]] = None):
    """
    Context manager to track request duration.

    Args:
        method: HTTP method
        endpoint: API endpoint
        labels: Additional labels

    Example:
        with track_request_duration("GET", "/fields"):
            # ... process request
            pass
    """
    start_time = time.time()
    status_code = 200

    try:
        yield
    except Exception as e:
        status_code = 500
        raise
    finally:
        duration = time.time() - start_time
        track_request(method, endpoint, status_code, duration, labels)


def create_counter(
    name: str,
    description: str = "",
    unit: str = "1",
) -> metrics.Counter:
    """
    Create a custom counter metric.

    Args:
        name: Metric name
        description: Metric description
        unit: Metric unit

    Returns:
        Counter instance
    """
    meter = get_meter()
    return meter.create_counter(
        name=name,
        description=description,
        unit=unit,
    )


def create_histogram(
    name: str,
    description: str = "",
    unit: str = "1",
) -> metrics.Histogram:
    """
    Create a custom histogram metric.

    Args:
        name: Metric name
        description: Metric description
        unit: Metric unit

    Returns:
        Histogram instance
    """
    meter = get_meter()
    return meter.create_histogram(
        name=name,
        description=description,
        unit=unit,
    )


def create_up_down_counter(
    name: str,
    description: str = "",
    unit: str = "1",
) -> metrics.UpDownCounter:
    """
    Create a custom up-down counter metric (can go up and down).

    Args:
        name: Metric name
        description: Metric description
        unit: Metric unit

    Returns:
        UpDownCounter instance
    """
    meter = get_meter()
    return meter.create_up_down_counter(
        name=name,
        description=description,
        unit=unit,
    )


def track_business_metric(
    metric_name: str,
    value: float = 1,
    metric_type: str = "counter",
    labels: Optional[Dict[str, Any]] = None,
    description: str = "",
    unit: str = "1",
) -> None:
    """
    Track custom business metrics.

    Args:
        metric_name: Name of the metric
        value: Metric value
        metric_type: Type of metric (counter, histogram)
        labels: Metric labels
        description: Metric description
        unit: Metric unit

    Example:
        # Track fields created
        track_business_metric("fields_created", value=1, labels={"user_id": "123"})

        # Track satellite request latency
        track_business_metric(
            "satellite_request_duration",
            value=2.5,
            metric_type="histogram",
            labels={"provider": "sentinel"}
        )
    """
    global _business_counters, _business_histograms

    attributes = labels or {}

    if metric_type == "counter":
        if metric_name not in _business_counters:
            _business_counters[metric_name] = create_counter(
                name=metric_name,
                description=description or f"Business metric: {metric_name}",
                unit=unit,
            )
        _business_counters[metric_name].add(value, attributes=attributes)

    elif metric_type == "histogram":
        if metric_name not in _business_histograms:
            _business_histograms[metric_name] = create_histogram(
                name=metric_name,
                description=description or f"Business metric: {metric_name}",
                unit=unit,
            )
        _business_histograms[metric_name].record(value, attributes=attributes)


# Predefined business metrics for SAHOOL services
class SahoolMetrics:
    """Standard business metrics for SAHOOL platform."""

    @staticmethod
    def track_field_created(user_id: str, field_type: str = "agricultural"):
        """Track field creation."""
        track_business_metric(
            "sahool_fields_created_total",
            value=1,
            labels={"user_id": user_id, "field_type": field_type},
            description="Total number of fields created",
        )

    @staticmethod
    def track_satellite_request(provider: str, status: str, duration: float):
        """Track satellite imagery request."""
        track_business_metric(
            "sahool_satellite_requests_total",
            value=1,
            labels={"provider": provider, "status": status},
            description="Total number of satellite requests",
        )
        track_business_metric(
            "sahool_satellite_request_duration_seconds",
            value=duration,
            metric_type="histogram",
            labels={"provider": provider},
            description="Satellite request duration in seconds",
            unit="s",
        )

    @staticmethod
    def track_weather_query(provider: str, location: str, status: str):
        """Track weather data query."""
        track_business_metric(
            "sahool_weather_queries_total",
            value=1,
            labels={"provider": provider, "location": location, "status": status},
            description="Total number of weather queries",
        )

    @staticmethod
    def track_ndvi_calculation(field_id: str, duration: float):
        """Track NDVI calculation."""
        track_business_metric(
            "sahool_ndvi_calculations_total",
            value=1,
            labels={"field_id": field_id},
            description="Total number of NDVI calculations",
        )
        track_business_metric(
            "sahool_ndvi_calculation_duration_seconds",
            value=duration,
            metric_type="histogram",
            labels={"field_id": field_id},
            description="NDVI calculation duration in seconds",
            unit="s",
        )

    @staticmethod
    def track_ai_recommendation(advisor_type: str, crop_type: str, duration: float):
        """Track AI advisory recommendation."""
        track_business_metric(
            "sahool_ai_recommendations_total",
            value=1,
            labels={"advisor_type": advisor_type, "crop_type": crop_type},
            description="Total number of AI recommendations",
        )
        track_business_metric(
            "sahool_ai_recommendation_duration_seconds",
            value=duration,
            metric_type="histogram",
            labels={"advisor_type": advisor_type},
            description="AI recommendation duration in seconds",
            unit="s",
        )

    @staticmethod
    def track_iot_reading(sensor_type: str, field_id: str, value: float):
        """Track IoT sensor reading."""
        track_business_metric(
            "sahool_iot_readings_total",
            value=1,
            labels={"sensor_type": sensor_type, "field_id": field_id},
            description="Total number of IoT sensor readings",
        )

    @staticmethod
    def track_notification_sent(notification_type: str, channel: str, status: str):
        """Track notification delivery."""
        track_business_metric(
            "sahool_notifications_sent_total",
            value=1,
            labels={
                "notification_type": notification_type,
                "channel": channel,
                "status": status,
            },
            description="Total number of notifications sent",
        )

    @staticmethod
    def track_irrigation_event(field_id: str, event_type: str, water_amount: float):
        """Track irrigation event."""
        track_business_metric(
            "sahool_irrigation_events_total",
            value=1,
            labels={"field_id": field_id, "event_type": event_type},
            description="Total number of irrigation events",
        )
        track_business_metric(
            "sahool_irrigation_water_liters",
            value=water_amount,
            metric_type="histogram",
            labels={"field_id": field_id},
            description="Irrigation water amount in liters",
            unit="L",
        )

    @staticmethod
    def track_crop_health_analysis(crop_type: str, health_score: float, duration: float):
        """Track crop health analysis."""
        track_business_metric(
            "sahool_crop_health_analyses_total",
            value=1,
            labels={"crop_type": crop_type},
            description="Total number of crop health analyses",
        )
        track_business_metric(
            "sahool_crop_health_score",
            value=health_score,
            metric_type="histogram",
            labels={"crop_type": crop_type},
            description="Crop health score (0-100)",
            unit="score",
        )

    @staticmethod
    def track_yield_prediction(crop_type: str, predicted_yield: float, duration: float):
        """Track yield prediction."""
        track_business_metric(
            "sahool_yield_predictions_total",
            value=1,
            labels={"crop_type": crop_type},
            description="Total number of yield predictions",
        )
        track_business_metric(
            "sahool_predicted_yield_kg",
            value=predicted_yield,
            metric_type="histogram",
            labels={"crop_type": crop_type},
            description="Predicted yield in kilograms",
            unit="kg",
        )

    @staticmethod
    def track_marketplace_transaction(transaction_type: str, amount: float, status: str):
        """Track marketplace transaction."""
        track_business_metric(
            "sahool_marketplace_transactions_total",
            value=1,
            labels={"transaction_type": transaction_type, "status": status},
            description="Total number of marketplace transactions",
        )
        track_business_metric(
            "sahool_marketplace_revenue",
            value=amount,
            metric_type="histogram",
            labels={"transaction_type": transaction_type},
            description="Marketplace transaction revenue",
            unit="currency",
        )


__all__ = [
    "init_metrics",
    "get_meter",
    "track_request",
    "track_request_duration",
    "create_counter",
    "create_histogram",
    "create_up_down_counter",
    "track_business_metric",
    "SahoolMetrics",
]
