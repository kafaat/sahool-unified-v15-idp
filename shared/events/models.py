"""
SAHOOL Event Models (Legacy)
============================
Legacy event models — new code should use shared.events.contracts instead.

These models are kept for backward compatibility.  The local BaseEvent now
inherits from contracts.BaseEvent so that all legacy events carry the full
event envelope (event_id, timestamp, correlation_id, trace_id, etc.).

Usage:
    from shared.events.models import FieldCreatedEvent, FieldUpdatedEvent

    event = FieldCreatedEvent(
        field_id="uuid",
        farm_id="uuid",
        name="Field 1",
        geometry_wkt="POLYGON(...)",
        created_at=datetime.now(timezone.utc)
    )
    await nats.publish("field.created", event.model_dump_json())
"""

from __future__ import annotations

import warnings
from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field

from .contracts import BaseEvent as _ContractsBaseEvent

# ─────────────────────────────────────────────────────────────────────────────
# Event Enums
# ─────────────────────────────────────────────────────────────────────────────


class EventPriority(StrEnum):
    """Event priority levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EventStatus(StrEnum):
    """Event processing status"""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class EventMetadataDTO(BaseModel):
    """
    Lenient event metadata for deserialization (all fields optional, str types).
    For strict event creation, use shared.contracts.events.base.EventMetadata.
    بيانات وصفية مرنة للأحداث (جميع الحقول اختيارية)
    """

    correlation_id: str | None = None
    causation_id: str | None = None
    user_id: str | None = None
    trace_id: str | None = None
    span_id: str | None = None


# Backward-compatible alias
EventMetadata = EventMetadataDTO


# ─────────────────────────────────────────────────────────────────────────────
# Base Event Model — now delegates to contracts.BaseEvent
# ─────────────────────────────────────────────────────────────────────────────


class BaseEvent(_ContractsBaseEvent):
    """
    Legacy base event — inherits the canonical envelope from contracts.BaseEvent.

    All legacy event models (FieldCreatedEvent, TaskCreatedEvent, etc.) now
    carry event_id, timestamp, correlation_id, causation_id, trace_id, span_id
    automatically.

    .. deprecated::
        Use ``shared.events.contracts.BaseEvent`` directly for new events.
    """


# ─────────────────────────────────────────────────────────────────────────────
# Field Events
# ─────────────────────────────────────────────────────────────────────────────


class FieldCreatedEvent(BaseEvent):
    """Event emitted when a new field is created."""

    field_id: UUID
    farm_id: UUID
    name: str = Field(..., min_length=1, max_length=120)
    name_ar: str | None = Field(None, max_length=120)
    geometry_wkt: str = Field(..., min_length=10)
    area_hectares: float | None = Field(None, ge=0)
    soil_type: str | None = None
    irrigation_type: str | None = None
    created_at: datetime


class FieldUpdatedEvent(BaseEvent):
    """Event emitted when a field is updated."""

    field_id: UUID
    name: str | None = Field(None, max_length=120)
    name_ar: str | None = Field(None, max_length=120)
    geometry_wkt: str | None = None
    area_hectares: float | None = Field(None, ge=0)
    soil_type: str | None = None
    irrigation_type: str | None = None
    ndvi_value: float | None = Field(None, ge=-1, le=1)
    updated_at: datetime


# ─────────────────────────────────────────────────────────────────────────────
# Farm Events
# ─────────────────────────────────────────────────────────────────────────────


class FarmCreatedEvent(BaseEvent):
    """Event emitted when a new farm is created."""

    farm_id: UUID
    tenant_id: UUID
    name: str = Field(..., min_length=1, max_length=120)
    name_ar: str | None = Field(None, max_length=120)
    location_lat: float = Field(..., ge=-90, le=90)
    location_lon: float = Field(..., ge=-180, le=180)
    total_area_hectares: float | None = Field(None, ge=0)
    created_at: datetime


# ─────────────────────────────────────────────────────────────────────────────
# Crop Events
# ─────────────────────────────────────────────────────────────────────────────


class CropPlantedEvent(BaseEvent):
    """Event emitted when a crop is planted in a field."""

    field_id: UUID
    crop_type: str = Field(..., min_length=1, max_length=100)
    variety: str | None = Field(None, max_length=100)
    planting_date: datetime
    expected_harvest_date: datetime | None = None
    area_hectares: float | None = Field(None, ge=0)


# ─────────────────────────────────────────────────────────────────────────────
# Task Events
# ─────────────────────────────────────────────────────────────────────────────


class TaskCreatedEvent(BaseEvent):
    """Event emitted when a new task is created."""

    task_id: UUID
    field_id: UUID | None = None
    tenant_id: UUID
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    priority: str = Field(..., pattern="^(low|medium|high|urgent)$")
    due_date: datetime | None = None
    assigned_to: UUID | None = None
    created_at: datetime


class TaskCompletedEvent(BaseEvent):
    """Event emitted when a task is completed."""

    task_id: UUID
    completed_by: UUID
    completed_at: datetime
    evidence_notes: str | None = None


# ─────────────────────────────────────────────────────────────────────────────
# Advisor Events
# ─────────────────────────────────────────────────────────────────────────────


class AdvisorRecommendationEvent(BaseEvent):
    """Event emitted when the advisor generates a recommendation."""

    recommendation_id: UUID
    field_id: UUID
    tenant_id: UUID
    recommendation_type: str = Field(..., pattern="^(irrigation|fertilizer|pest|harvest)$")
    title: str
    title_ar: str | None = None
    description: str
    description_ar: str | None = None
    priority: str = Field(..., pattern="^(low|medium|high|critical)$")
    confidence_score: float = Field(..., ge=0, le=1)
    created_at: datetime


# ─────────────────────────────────────────────────────────────────────────────
# Alert Events
# ─────────────────────────────────────────────────────────────────────────────


class AlertCreatedEvent(BaseEvent):
    """Event emitted when an alert is created."""

    alert_id: UUID
    tenant_id: UUID
    field_id: UUID | None = None
    alert_type: str = Field(..., pattern="^(weather|pest|disease|irrigation|system)$")
    severity: str = Field(..., pattern="^(info|warning|critical)$")
    title: str
    title_ar: str | None = None
    message: str
    message_ar: str | None = None
    created_at: datetime
