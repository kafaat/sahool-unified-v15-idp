"""
Base Event Classes
==================

Provides the foundational event structure for all SAHOOL domain events.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4


@dataclass
class EventMetadata:
    """Metadata attached to every event"""

    correlation_id: UUID
    causation_id: UUID | None = None
    user_id: UUID | None = None
    trace_id: str | None = None
    span_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "correlation_id": str(self.correlation_id),
            "causation_id": str(self.causation_id) if self.causation_id else None,
            "user_id": str(self.user_id) if self.user_id else None,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
        }


@dataclass
class EventSource:
    """Source information for the event producer"""

    service: str
    version: str
    instance_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "service": self.service,
            "version": self.version,
            "instance_id": self.instance_id,
        }


@dataclass
class BaseEvent:
    """
    Base class for all SAHOOL domain events.

    All events must inherit from this class and define:
    - EVENT_TYPE: str (e.g., "field.created")
    - EVENT_VERSION: str (e.g., "1.0.0")
    - SCHEMA_PATH: str (path to JSON schema)
    """

    EVENT_TYPE: str = ""
    EVENT_VERSION: str = "1.0.0"
    SCHEMA_PATH: str = ""

    # Required fields
    tenant_id: UUID

    # Auto-generated fields
    event_id: UUID = field(default_factory=uuid4)
    timestamp: datetime = field(default_factory=datetime.utcnow)

    # Optional metadata
    metadata: EventMetadata | None = None
    source: EventSource | None = None

    def __post_init__(self):
        if not self.metadata:
            self.metadata = EventMetadata(correlation_id=uuid4())

    @property
    def event_type(self) -> str:
        return self.EVENT_TYPE

    @property
    def event_version(self) -> str:
        return self.EVENT_VERSION

    def to_dict(self) -> dict[str, Any]:
        """Convert event to dictionary for serialization"""
        return {
            "event_id": str(self.event_id),
            "event_type": self.event_type,
            "event_version": self.event_version,
            "timestamp": self.timestamp.isoformat(),
            "tenant_id": str(self.tenant_id),
            "correlation_id": (
                str(self.metadata.correlation_id) if self.metadata else None
            ),
            "source": self.source.to_dict() if self.source else None,
            "metadata": self.metadata.to_dict() if self.metadata else None,
            "payload": self._payload_to_dict(),
        }

    def _payload_to_dict(self) -> dict[str, Any]:
        """Override in subclasses to define payload serialization"""
        raise NotImplementedError("Subclasses must implement _payload_to_dict")

    def to_json(self) -> str:
        """Serialize event to JSON string"""
        return json.dumps(self.to_dict(), default=str)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BaseEvent":
        """Deserialize event from dictionary"""
        raise NotImplementedError("Subclasses must implement from_dict")

    @classmethod
    def from_json(cls, json_str: str) -> "BaseEvent":
        """Deserialize event from JSON string"""
        return cls.from_dict(json.loads(json_str))

    def validate(self) -> bool:
        """Validate event against its JSON schema"""
        # TODO: Implement JSON schema validation
        return True

    def __str__(self) -> str:
        return f"{self.event_type}(id={self.event_id}, tenant={self.tenant_id})"
