"""SAHOOL Observability - Prometheus Metrics & OpenTelemetry Tracing."""

from . import metrics as _metrics

instrument_fastapi = _metrics.instrument_fastapi
setup_tracing = _metrics.setup_tracing

__all__ = [
    "instrument_fastapi",
    "setup_tracing",
]

if hasattr(_metrics, "HTTP_REQUEST_DURATION"):
    HTTP_REQUEST_DURATION = _metrics.HTTP_REQUEST_DURATION
    __all__.append("HTTP_REQUEST_DURATION")

if hasattr(_metrics, "HTTP_REQUESTS_TOTAL"):
    HTTP_REQUESTS_TOTAL = _metrics.HTTP_REQUESTS_TOTAL
    __all__.append("HTTP_REQUESTS_TOTAL")

if hasattr(_metrics, "NATS_EVENTS_CONSUMED"):
    NATS_EVENTS_CONSUMED = _metrics.NATS_EVENTS_CONSUMED
    __all__.append("NATS_EVENTS_CONSUMED")

if hasattr(_metrics, "NATS_EVENTS_PUBLISHED"):
    NATS_EVENTS_PUBLISHED = _metrics.NATS_EVENTS_PUBLISHED
    __all__.append("NATS_EVENTS_PUBLISHED")
