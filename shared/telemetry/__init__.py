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

_TELEMETRY_AVAILABLE = False

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

    _TELEMETRY_AVAILABLE = True
except ModuleNotFoundError:
    # opentelemetry packages not installed — provide explicit stubs that
    # raise a clear error when called, rather than failing silently.

    def _not_available(*args, **kwargs):  # noqa: ANN002, ANN003, ANN201
        raise ModuleNotFoundError(
            "opentelemetry packages are not installed. "
            "Install them or use shared.observability (which degrades gracefully)."
        )

    get_logger = _not_available
    log_exception = _not_available
    setup_logging = _not_available
    SahoolMetrics = _not_available  # type: ignore[assignment,misc]
    get_meter = _not_available
    init_metrics = _not_available
    track_business_metric = _not_available
    track_request = _not_available
    get_current_span_id = _not_available
    get_current_trace_id = _not_available
    get_tracer = _not_available
    init_tracer = _not_available
    instrument_all = _not_available
    trace_method = _not_available

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
