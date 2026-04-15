"""
Pydantic response models for traceability-service - نماذج استجابة Pydantic
camelCase serialization via Field aliases for API consumers (TypeScript/Flutter clients).
"""

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

# ─────────────────────────────────────────────────────────────────────────────
# Enums
# ─────────────────────────────────────────────────────────────────────────────


class BatchStatus(StrEnum):
    """Produce batch lifecycle status - حالة دورة حياة الدفعة.

    Must stay in sync with the `valid_batch_status` CHECK constraint in
    migrations/001_create_traceability_tables.sql.
    """

    CREATED = "created"
    HARVESTED = "harvested"
    IN_PROCESSING = "in_processing"
    IN_STORAGE = "in_storage"
    IN_TRANSIT = "in_transit"
    AT_RETAIL = "at_retail"
    SOLD = "sold"
    EXPIRED = "expired"
    SPLIT = "split"
    RECALLED = "recalled"


class EventType(StrEnum):
    """Supply chain event types - أنواع أحداث سلسلة التوريد."""

    HARVEST = "harvest"
    PROCESSING = "processing"
    STORAGE = "storage"
    TRANSPORT = "transport"
    RETAIL = "retail"
    CONSUMER_SCAN = "consumer_scan"
    QUALITY_CHECK = "quality_check"
    CERTIFICATION = "certification"
    RECALL = "recall"


# ─────────────────────────────────────────────────────────────────────────────
# Base config for camelCase serialization
# ─────────────────────────────────────────────────────────────────────────────


def _to_camel(snake: str) -> str:
    parts = snake.split("_")
    return parts[0] + "".join(p.title() for p in parts[1:])


class CamelModel(BaseModel):
    """Base model that serializes snake_case fields as camelCase.

    Accepts both snake_case (from DB rows) and camelCase (from API clients)
    on input; always emits camelCase on output.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=_to_camel,
        from_attributes=True,
        use_enum_values=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Response models (camelCase wire format)
# ─────────────────────────────────────────────────────────────────────────────


class BatchResponse(CamelModel):
    """Produce batch response - نموذج استجابة الدفعة."""

    id: str
    tenant_id: str
    farm_id: str
    field_id: str
    batch_code: str
    product_name_en: str
    product_name_ar: str
    variety: str | None = None
    quantity: float
    unit: str = "kg"
    quality_grade: str | None = "A"
    status: BatchStatus = BatchStatus.CREATED
    version: int = 1
    created_at: datetime | None = None
    updated_at: datetime | None = None


class BatchListResponse(CamelModel):
    batches: list[BatchResponse]
    count: int


class SupplyChainEventResponse(CamelModel):
    """Supply chain event response - نموذج استجابة الحدث."""

    id: str
    batch_id: str
    event_type: EventType
    timestamp: datetime | None = None
    location: str | None = None
    location_ar: str | None = None
    crop_type: str | None = None
    harvest_method: str | None = None
    quality_grade: str | None = None
    facility_name: str | None = None
    process_type: str | None = None
    temperature_c: float | None = None
    humidity_percent: float | None = None
    origin: str | None = None
    destination: str | None = None
    transport_mode: str | None = None
    vehicle_id: str | None = None
    notes: str | None = None
    notes_ar: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime | None = None


class BatchEventListResponse(CamelModel):
    batch_id: str
    events: list[SupplyChainEventResponse]
    count: int


class EventRecordedResponse(CamelModel):
    status: str = "recorded"
    event: SupplyChainEventResponse


class BatchSplitResponse(CamelModel):
    parent_batch_id: str
    remaining_quantity: float
    child_batches: list[BatchResponse]


class AffectedChildBatch(CamelModel):
    id: str
    batch_code: str
    status: str


class RecallResponse(CamelModel):
    status: str = "recalled"
    batch_id: str
    batch_code: str
    reason_en: str
    reason_ar: str
    severity: str
    affected_children: list[AffectedChildBatch]
    recall_event: SupplyChainEventResponse
    recalled_at: datetime


class JourneyStep(CamelModel):
    event_type: str
    timestamp: datetime | None = None
    location: str | None = None
    crop_type: str | None = None
    quality_grade: str | None = None
    facility: str | None = None
    process_type: str | None = None
    temperature_c: float | None = None
    origin: str | None = None
    destination: str | None = None
    mode: str | None = None


class CertificationInfo(CamelModel):
    id: str
    batch_id: str
    certification_type: str
    certificate_number: str | None = None
    issuing_body: str | None = None
    valid_from: datetime | None = None
    valid_until: datetime | None = None
    status: str


class ProductJourneyResponse(CamelModel):
    batch_code: str
    product_name_en: str
    product_name_ar: str
    farm_id: str
    status: str
    quality_grade: str | None = None
    journey: list[JourneyStep]
    certifications: list[dict[str, Any]]


class BatchCodeResponse(CamelModel):
    batch_code: str


class BatchCodeVerifyResponse(CamelModel):
    code: str
    valid: bool
    exists: bool


class QRCodeResponse(CamelModel):
    batch_id: str
    batch_code: str
    qr_data: str
    format: str


class CarbonFootprintResponse(CamelModel):
    batch_id: str
    carbon_footprint_kg_co2: float | None = None
    message: str | None = None
