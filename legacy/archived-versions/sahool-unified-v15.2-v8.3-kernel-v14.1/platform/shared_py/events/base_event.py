"""SAHOOL Event Base v15.2

Standard event envelope:
- event_id, event_type, tenant_id, timestamp
- correlation_id (required)
- trace context (if available)
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from opentelemetry import trace


class EventTypes:
    # NOTE: subjects are strings (NATS subjects) used consistently in services
    IMAGE_ANALYZE_REQUESTED = "internal.image.analyze"
    IMAGE_ANALYZED = "internal.image.analyzed"
    DISEASE_RISK_ASSESSED = "decision.disease.risk_assessed"


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def get_current_trace_context() -> Dict[str, Optional[str]]:
    """Extract trace context from OpenTelemetry, if any."""
    current_span = trace.get_current_span()
    if not current_span or not current_span.is_recording():
        return {"trace_id": None, "span_id": None}

    ctx = current_span.get_span_context()
    return {
        "trace_id": format(ctx.trace_id, "032x") if ctx.trace_id else None,
        "span_id": format(ctx.span_id, "016x") if ctx.span_id else None,
    }


def create_event(
    event_type: str,
    payload: Dict[str, Any],
    tenant_id: str = "default",
    correlation_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Create standardized event with trace context."""
    trace_ctx = get_current_trace_context()

    return {
        "event_id": str(uuid.uuid4()),
        "event_type": event_type,
        "tenant_id": tenant_id,
        "timestamp": _utc_iso(),
        "correlation_id": correlation_id or str(uuid.uuid4()),
        "trace": {"trace_id": trace_ctx["trace_id"], "span_id": trace_ctx["span_id"]},
        "payload": payload,
        "schema_version": "v15.2",
    }
