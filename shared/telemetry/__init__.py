"""
SAHOOL Platform - OpenTelemetry Distributed Tracing & Metrics
==============================================================

This package provides comprehensive observability instrumentation for the SAHOOL
agricultural platform, including distributed tracing, metrics, and structured logging.

Modules:
    tracing: OpenTelemetry distributed tracing
    metrics: Prometheus metrics and OpenTelemetry meters
    logging: Structured JSON logging with trace correlation

Author: SAHOOL Platform Team
Date: 2025-12-26
"""

from .tracing import (
    init_tracer,
    get_tracer,
    instrument_all,
    trace_method,
    get_current_trace_id,
    get_current_span_id,
)

from .metrics import (
    init_metrics,
    get_meter,
    track_request,
    track_business_metric,
    SahoolMetrics,
)

from .logging import (
    setup_logging,
    get_logger,
    log_exception,
)

__version__ = "1.0.0"

__all__ = [
    # Tracing
    "init_tracer",
    "get_tracer",
    "instrument_all",
    "trace_method",
    "get_current_trace_id",
    "get_current_span_id",
    # Metrics
    "init_metrics",
    "get_meter",
    "track_request",
    "track_business_metric",
    "SahoolMetrics",
    # Logging
    "setup_logging",
    "get_logger",
    "log_exception",
]
