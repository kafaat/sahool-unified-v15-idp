"""
SAHOOL Event Models
===================
Pydantic models matching the JSON schemas in shared/contracts/events/
These models ensure type safety and validation for event-driven communication.

Usage:
    from shared.events.models import FieldCreatedEvent, FieldUpdatedEvent

    event = FieldCreatedEvent(
        field_id="uuid",
        farm_id="uuid",
        name="Field 1",
        geometry_wkt="POLYGON(...)",
        created_at=datetime.utcnow()
    )
    await nats.publish("field.created", event.model_dump_json())
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ─────────────────────────────────────────────────────────────────────────────
# Base Event Model
# ─────────────────────────────────────────────────────────────────────────────


class BaseEvent(BaseModel):
    """Base class for all SAHOOL events with common metadata."""

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }


# ─────────────────────────────────────────────────────────────────────────────
# Field Events
# ─────────────────────────────────────────────────────────────────────────────


class FieldCreatedEvent(BaseEvent):
    """Event emitted when a new field is created."""

    field_id: UUID
    farm_id: UUID
    name: str = Field(..., min_length=1, max_length=120)
    name_ar: Optional[str] = Field(None, max_length=120)
    geometry_wkt: str = Field(..., min_length=10)
    area_hectares: Optional[float] = Field(None, ge=0)
    soil_type: Optional[str] = None
    irrigation_type: Optional[str] = None
    created_at: datetime


class FieldUpdatedEvent(BaseEvent):
    """Event emitted when a field is updated."""

    field_id: UUID
    name: Optional[str] = Field(None, max_length=120)
    name_ar: Optional[str] = Field(None, max_length=120)
    geometry_wkt: Optional[str] = None
    area_hectares: Optional[float] = Field(None, ge=0)
    soil_type: Optional[str] = None
    irrigation_type: Optional[str] = None
    ndvi_value: Optional[float] = Field(None, ge=-1, le=1)
    updated_at: datetime


# ─────────────────────────────────────────────────────────────────────────────
# Farm Events
# ─────────────────────────────────────────────────────────────────────────────


class FarmCreatedEvent(BaseEvent):
    """Event emitted when a new farm is created."""

    farm_id: UUID
    tenant_id: UUID
    name: str = Field(..., min_length=1, max_length=120)
    name_ar: Optional[str] = Field(None, max_length=120)
    location_lat: float = Field(..., ge=-90, le=90)
    location_lon: float = Field(..., ge=-180, le=180)
    total_area_hectares: Optional[float] = Field(None, ge=0)
    created_at: datetime


# ─────────────────────────────────────────────────────────────────────────────
# Crop Events
# ─────────────────────────────────────────────────────────────────────────────


class CropPlantedEvent(BaseEvent):
    """Event emitted when a crop is planted in a field."""

    field_id: UUID
    crop_type: str = Field(..., min_length=1, max_length=100)
    variety: Optional[str] = Field(None, max_length=100)
    planting_date: datetime
    expected_harvest_date: Optional[datetime] = None
    area_hectares: Optional[float] = Field(None, ge=0)


# ─────────────────────────────────────────────────────────────────────────────
# Task Events
# ─────────────────────────────────────────────────────────────────────────────


class TaskCreatedEvent(BaseEvent):
    """Event emitted when a new task is created."""

    task_id: UUID
    field_id: Optional[UUID] = None
    tenant_id: UUID
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    priority: str = Field(..., pattern="^(low|medium|high|urgent)$")
    due_date: Optional[datetime] = None
    assigned_to: Optional[UUID] = None
    created_at: datetime


class TaskCompletedEvent(BaseEvent):
    """Event emitted when a task is completed."""

    task_id: UUID
    completed_by: UUID
    completed_at: datetime
    evidence_notes: Optional[str] = None


# ─────────────────────────────────────────────────────────────────────────────
# Advisor Events
# ─────────────────────────────────────────────────────────────────────────────


class AdvisorRecommendationEvent(BaseEvent):
    """Event emitted when the advisor generates a recommendation."""

    recommendation_id: UUID
    field_id: UUID
    tenant_id: UUID
    recommendation_type: str = Field(
        ..., pattern="^(irrigation|fertilizer|pest|harvest)$"
    )
    title: str
    title_ar: Optional[str] = None
    description: str
    description_ar: Optional[str] = None
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
    field_id: Optional[UUID] = None
    alert_type: str = Field(..., pattern="^(weather|pest|disease|irrigation|system)$")
    severity: str = Field(..., pattern="^(info|warning|critical)$")
    title: str
    title_ar: Optional[str] = None
    message: str
    message_ar: Optional[str] = None
    created_at: datetime
