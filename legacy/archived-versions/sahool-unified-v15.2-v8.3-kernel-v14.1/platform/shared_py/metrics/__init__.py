from __future__ import annotations

from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

EVENTS_PUBLISHED = Counter(
    "sahool_events_published_total",
    "Total events published",
    ["service", "event_type", "tenant_id"],
)

EVENTS_CONSUMED = Counter(
    "sahool_events_consumed_total",
    "Total events consumed",
    ["service", "event_type", "tenant_id"],
)


def init_service_info(service_name: str, version: str, layer: str) -> None:
    # placeholder hook for future gauges/labels
    return


def get_metrics() -> bytes:
    return generate_latest()


def get_metrics_content_type() -> str:
    return CONTENT_TYPE_LATEST
