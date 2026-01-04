"""
Field Domain Events
===================

Events related to field management operations.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID

from .base import BaseEvent


@dataclass
class FieldCreatedEvent(BaseEvent):
    """Event emitted when a new field is registered"""

    EVENT_TYPE = "field.created"
    EVENT_VERSION = "1.0.0"
    SCHEMA_PATH = "field.created.v1.json"

    # Required payload fields
    field_id: UUID = None
    name: str = ""
    geometry: dict[str, Any] = field(default_factory=dict)
    area_hectares: float = 0.0

    # Optional payload fields
    soil_type: str | None = None
    irrigation_type: str | None = None
    owner_id: UUID | None = None
    location: dict[str, str] | None = None

    def _payload_to_dict(self) -> dict[str, Any]:
        payload = {
            "field_id": str(self.field_id),
            "tenant_id": str(self.tenant_id),
            "name": self.name,
            "geometry": self.geometry,
            "area_hectares": self.area_hectares,
        }

        if self.soil_type:
            payload["soil_type"] = self.soil_type
        if self.irrigation_type:
            payload["irrigation_type"] = self.irrigation_type
        if self.owner_id:
            payload["owner_id"] = str(self.owner_id)
        if self.location:
            payload["location"] = self.location

        return payload

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FieldCreatedEvent":
        payload = data.get("payload", {})
        return cls(
            event_id=UUID(data["event_id"]),
            tenant_id=UUID(data["tenant_id"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            field_id=UUID(payload["field_id"]),
            name=payload["name"],
            geometry=payload["geometry"],
            area_hectares=payload["area_hectares"],
            soil_type=payload.get("soil_type"),
            irrigation_type=payload.get("irrigation_type"),
            owner_id=UUID(payload["owner_id"]) if payload.get("owner_id") else None,
            location=payload.get("location"),
        )


@dataclass
class FieldUpdatedEvent(BaseEvent):
    """Event emitted when field information is updated"""

    EVENT_TYPE = "field.updated"
    EVENT_VERSION = "1.0.0"
    SCHEMA_PATH = "field.updated.v1.json"

    # Required payload fields
    field_id: UUID = None
    updated_fields: list[str] = field(default_factory=list)
    changes: dict[str, Any] = field(default_factory=dict)

    # Optional
    updated_by: UUID | None = None

    def _payload_to_dict(self) -> dict[str, Any]:
        payload = {
            "field_id": str(self.field_id),
            "updated_fields": self.updated_fields,
            "changes": self.changes,
            "updated_at": self.timestamp.isoformat(),
        }

        if self.updated_by:
            payload["updated_by"] = str(self.updated_by)

        return payload


@dataclass
class FieldBoundaryChangedEvent(BaseEvent):
    """Event emitted when field boundary geometry changes"""

    EVENT_TYPE = "field.boundary_changed"
    EVENT_VERSION = "1.0.0"
    SCHEMA_PATH = "field.boundary_changed.v1.json"

    field_id: UUID = None
    old_geometry: dict[str, Any] = field(default_factory=dict)
    new_geometry: dict[str, Any] = field(default_factory=dict)
    area_change_hectares: float = 0.0

    def _payload_to_dict(self) -> dict[str, Any]:
        return {
            "field_id": str(self.field_id),
            "old_geometry": self.old_geometry,
            "new_geometry": self.new_geometry,
            "area_change_hectares": self.area_change_hectares,
        }
