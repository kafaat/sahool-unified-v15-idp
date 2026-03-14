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

.. note:: Tracing Module Overlap
   This package (``shared.telemetry``) and ``shared.observability`` both provide
   distributed tracing, metrics collection, and structured logging. The two
   packages evolved independently and have significant overlap:

   - **shared.telemetry** (this package): Uses direct OpenTelemetry SDK imports.
     All submodules require ``opentelemetry-*`` packages to be installed.
     Best suited for services that already have the full OTel SDK in their
     requirements and need low-level OTel control (custom samplers, baggage, etc.).

   - **shared.observability**: Wraps OpenTelemetry behind ``try/except`` guards
     so it degrades gracefully when OTel packages are absent. Also includes
     additional features: sensitive-data masking in logs, agent/cost metrics,
     FastAPI middleware, and health check utilities.

   **Preferred module for new services**: ``shared.observability``
   It is the more defensive and feature-complete option. Services that need the
   full OTel SDK surface can import ``shared.telemetry`` as a supplement.

   A future consolidation effort may unify these into a single package.
   See: docs/adr/ for related Architecture Decision Records.
"""

try:
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
except ImportError:
    # opentelemetry packages not installed — degrade gracefully.
    # Services that need telemetry should use shared.observability instead.
    pass

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
