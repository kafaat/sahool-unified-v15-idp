"""SAHOOL Observability - Prometheus Metrics & OpenTelemetry Tracing."""

from .metrics import (
    HTTP_REQUEST_DURATION,
    HTTP_REQUESTS_TOTAL,
    NATS_EVENTS_CONSUMED,
    NATS_EVENTS_PUBLISHED,
    instrument_fastapi,
    setup_tracing,
)

__all__ = [
    "HTTP_REQUEST_DURATION",
    "HTTP_REQUESTS_TOTAL",
    "NATS_EVENTS_CONSUMED",
    "NATS_EVENTS_PUBLISHED",
    "instrument_fastapi",
    "setup_tracing",
]
