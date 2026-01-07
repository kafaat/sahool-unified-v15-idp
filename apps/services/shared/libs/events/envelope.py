"""
SAHOOL Event Envelope
Standard envelope for all events in the platform
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class EventEnvelope(BaseModel):
    """
    Standard event envelope that wraps all event payloads.

    All events in SAHOOL are wrapped in this envelope to ensure:
    - Consistent structure across all events
    - Traceability via correlation_id
    - Schema validation via schema_ref
    - Multi-tenancy via tenant_id
    """

    model_config = ConfigDict(extra="forbid")

    # Event identification
    event_id: UUID = Field(default_factory=uuid4, description="Unique event identifier")
    event_type: str = Field(..., description="Event type (e.g., 'field.created')")
    event_version: int = Field(default=1, ge=1, description="Event schema version")

    # Multi-tenancy and tracing
    tenant_id: UUID = Field(..., description="Tenant that owns this event")
    correlation_id: UUID = Field(..., description="Correlation ID for request tracing")

    # Timing
    occurred_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the event occurred",
    )

    # Schema validation
    schema_ref: str = Field(
        ...,
        description="Reference to schema in registry (e.g., 'events.field.created:v1')",
    )
    producer: str = Field(..., description="Service/domain that produced this event")

    # Payload
    payload: dict[str, Any] = Field(
        ..., description="Event payload matching schema_ref"
    )

    def to_json_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dictionary"""
        return {
            "event_id": str(self.event_id),
            "event_type": self.event_type,
            "event_version": self.event_version,
            "tenant_id": str(self.tenant_id),
            "correlation_id": str(self.correlation_id),
            "occurred_at": self.occurred_at.isoformat(),
            "schema_ref": self.schema_ref,
            "producer": self.producer,
            "payload": self.payload,
        }
