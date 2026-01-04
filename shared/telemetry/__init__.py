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

from .logging import (
    get_logger,
    log_exception,
    setup_logging,
)
from .metrics import (
    SahoolMetrics,
    get_meter,
    init_metrics,
    track_business_metric,
    track_request,
)
from .tracing import (
    get_current_span_id,
    get_current_trace_id,
    get_tracer,
    init_tracer,
    instrument_all,
    trace_method,
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
