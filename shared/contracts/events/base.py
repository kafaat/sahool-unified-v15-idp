"""
Base Event Classes
==================

Provides the foundational event structure for all SAHOOL domain events.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, ClassVar
from uuid import UUID, uuid4

import jsonschema
from jsonschema import ValidationError

# Schema directory relative to this file
_SCHEMA_DIR = Path(__file__).parent.parent / "schemas"

# Cache for loaded schemas
_schema_cache: dict[str, dict] = {}


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

    # Class-level constants (override in subclasses)
    EVENT_TYPE: ClassVar[str] = ""
    EVENT_VERSION: ClassVar[str] = "1.0.0"
    SCHEMA_PATH: ClassVar[str] = ""

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
            "correlation_id": (str(self.metadata.correlation_id) if self.metadata else None),
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
        """
        Validate event against its JSON schema.

        Returns:
            bool: True if validation passes

        Raises:
            ValidationError: If the event data does not conform to the schema
            FileNotFoundError: If the schema file cannot be found
        """
        if not self.SCHEMA_PATH:
            # No schema defined, skip validation
            return True

        schema = self._load_schema(self.SCHEMA_PATH)
        event_data = self.to_dict()

        # Create a registry with local schemas for $ref resolution
        from referencing import Registry, Resource

        registry = Registry()

        # Load all local schemas to resolve $ref references
        for schema_file in _SCHEMA_DIR.glob("*.json"):
            local_schema = self._load_schema(schema_file.name)
            schema_id = local_schema.get("$id", f"file://{schema_file}")
            # Also register by filename for relative refs
            resource = Resource.from_contents(local_schema)
            registry = registry.with_resource(schema_id, resource)
            registry = registry.with_resource(schema_file.name, resource)

        validator = jsonschema.Draft7Validator(schema, registry=registry)
        validator.validate(event_data)
        return True

    @staticmethod
    def _load_schema(schema_path: str) -> dict[str, Any]:
        """
        Load and cache a JSON schema from the schemas directory.

        Args:
            schema_path: Relative path to the schema file

        Returns:
            dict: The loaded JSON schema

        Raises:
            FileNotFoundError: If the schema file doesn't exist
        """
        if schema_path in _schema_cache:
            return _schema_cache[schema_path]

        full_path = _SCHEMA_DIR / schema_path
        if not full_path.exists():
            raise FileNotFoundError(f"Schema file not found: {full_path}")

        with open(full_path, encoding="utf-8") as f:
            schema = json.load(f)

        _schema_cache[schema_path] = schema
        return schema

    def __str__(self) -> str:
        return f"{self.event_type}(id={self.event_id}, tenant={self.tenant_id})"
