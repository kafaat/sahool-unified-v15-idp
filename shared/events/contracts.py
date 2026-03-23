"""
SAHOOL Event Contracts
======================
عقود الأحداث - نماذج Pydantic لجميع أحداث NATS في منصة سهول

Comprehensive Pydantic models for all NATS events across the SAHOOL platform.
These contracts ensure type safety, validation, and consistency across services.

Usage:
    from shared.events.contracts import FieldCreatedEvent, WeatherAlertEvent

    event = FieldCreatedEvent(
        field_id="uuid",
        farm_id="uuid",
        name="Field 1",
        geometry_wkt="POLYGON(...)",
        area_hectares=10.5
    )
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from uuid import UUID, uuid4

import structlog
from pydantic import BaseModel, ConfigDict, Field

# ─────────────────────────────────────────────────────────────────────────────
# Event Payload Validation - التحقق من صحة حمولة الأحداث
# ─────────────────────────────────────────────────────────────────────────────

_logger = structlog.get_logger(__name__) if "structlog" in dir() else logging.getLogger(__name__)

# Required base fields for all SAHOOL events published over NATS.
# الحقول الأساسية المطلوبة لجميع أحداث سهول المنشورة عبر NATS.
REQUIRED_EVENT_FIELDS: frozenset[str] = frozenset(
    {
        "event_id",
        "timestamp",
        "tenant_id",
        "source_service",
    }
)


def validate_event_payload(subject: str, payload: dict, *, strict: bool = False) -> bool:
    """Validate event payload has required base fields.

    All SAHOOL events must include: event_id, timestamp, tenant_id, source_service.

    التحقق من أن حمولة الحدث تحتوي على الحقول الأساسية المطلوبة.

    Args:
        subject: NATS subject the event is published to (e.g. "sahool.field.created").
        payload: Event payload as a dictionary.
        strict: If True, raise ValueError on missing fields instead of just logging.

    Returns:
        True if all required fields are present, False otherwise.

    Raises:
        ValueError: If strict=True and required fields are missing.
    """
    missing = REQUIRED_EVENT_FIELDS - set(payload.keys())

    # Also check for None/empty tenant_id
    if "tenant_id" in payload and not payload["tenant_id"]:
        missing = missing | {"tenant_id"}

    if missing:
        msg = f"Event on '{subject}' missing required fields: {sorted(missing)}"
        _logger.warning("event_missing_required_fields", subject=subject, missing=sorted(missing))
        if strict:
            raise ValueError(msg)
        return False
    return True


# ─────────────────────────────────────────────────────────────────────────────
# Base Event Model - النموذج الأساسي للأحداث
# ─────────────────────────────────────────────────────────────────────────────


class BaseEvent(BaseModel):
    """
    Base class for all SAHOOL events with common metadata.
    النموذج الأساسي لجميع الأحداث مع البيانات الوصفية المشتركة

    Canonical event envelope — all other BaseEvent definitions should
    import from this module.  Fields added 2026-02-23 for Architecture
    Conformance: causation_id, trace_id, span_id.
    """

    event_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique event identifier")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Event timestamp")
    version: str = Field(default="1.0", description="Event schema version")
    source_service: str | None = Field(None, description="Service that emitted the event")
    tenant_id: str | None = Field(
        None,
        description="Tenant ID for multi-tenant event routing and NATS header propagation.",
    )
    correlation_id: str | None = Field(None, description="Correlation ID for tracing across services")
    causation_id: str | None = Field(
        None,
        description="Event ID of the upstream event that caused this event (event chain linking)",
    )
    trace_id: str | None = Field(None, description="OpenTelemetry trace ID (W3C hex)")
    span_id: str | None = Field(None, description="OpenTelemetry span ID (W3C hex)")

    @property
    def event_type(self) -> str:
        """Return the event type name (class name)"""
        return self.__class__.__name__

    model_config = ConfigDict(populate_by_name=True)


# ─────────────────────────────────────────────────────────────────────────────
# Field Events - أحداث الحقول
# ─────────────────────────────────────────────────────────────────────────────


class FieldCreatedEvent(BaseEvent):
    """
    Event emitted when a new field is created.
    حدث يُطلق عند إنشاء حقل جديد
    """

    field_id: UUID = Field(..., description="Unique field identifier")
    farm_id: UUID = Field(..., description="Parent farm identifier")
    tenant_id: UUID = Field(..., description="Tenant/organization identifier")
    name: str = Field(..., min_length=1, max_length=120, description="Field name")
    name_ar: str | None = Field(None, max_length=120, description="Arabic field name")
    geometry_wkt: str = Field(..., min_length=10, description="Field geometry in WKT format")
    area_hectares: float | None = Field(None, ge=0, description="Field area in hectares")
    soil_type: str | None = Field(None, description="Soil type")
    irrigation_type: str | None = Field(None, description="Irrigation type")
    created_by: UUID | None = Field(None, description="User who created the field")


class FieldUpdatedEvent(BaseEvent):
    """
    Event emitted when a field is updated.
    حدث يُطلق عند تحديث حقل
    """

    field_id: UUID = Field(..., description="Field identifier")
    name: str | None = Field(None, max_length=120, description="Updated field name")
    name_ar: str | None = Field(None, max_length=120, description="Updated Arabic name")
    geometry_wkt: str | None = Field(None, description="Updated geometry")
    area_hectares: float | None = Field(None, ge=0, description="Updated area")
    soil_type: str | None = Field(None, description="Updated soil type")
    irrigation_type: str | None = Field(None, description="Updated irrigation type")
    ndvi_value: float | None = Field(None, ge=-1, le=1, description="Latest NDVI value")
    updated_by: UUID | None = Field(None, description="User who updated the field")


class FieldDeletedEvent(BaseEvent):
    """
    Event emitted when a field is deleted.
    حدث يُطلق عند حذف حقل
    """

    field_id: UUID = Field(..., description="Deleted field identifier")
    farm_id: UUID = Field(..., description="Parent farm identifier")
    tenant_id: UUID = Field(..., description="Tenant identifier")
    deleted_by: UUID | None = Field(None, description="User who deleted the field")
    reason: str | None = Field(None, description="Deletion reason")


# ─────────────────────────────────────────────────────────────────────────────
# Weather Events - أحداث الطقس
# ─────────────────────────────────────────────────────────────────────────────


class WeatherForecastEvent(BaseEvent):
    """
    Event emitted when weather forecast is updated.
    حدث يُطلق عند تحديث توقعات الطقس
    """

    field_id: UUID | None = Field(None, description="Related field (if applicable)")
    location_lat: float = Field(..., ge=-90, le=90, description="Latitude")
    location_lon: float = Field(..., ge=-180, le=180, description="Longitude")
    forecast_date: datetime = Field(..., description="Forecast date/time")
    temperature: float | None = Field(None, description="Temperature in Celsius")
    humidity: float | None = Field(None, ge=0, le=100, description="Humidity percentage")
    wind_speed: float | None = Field(None, ge=0, description="Wind speed in km/h")
    precipitation: float | None = Field(None, ge=0, description="Precipitation in mm")
    conditions: str | None = Field(None, description="Weather conditions description")
    provider: str | None = Field(None, description="Weather data provider")


class WeatherAlertEvent(BaseEvent):
    """
    Event emitted for weather alerts and warnings.
    حدث يُطلق للتحذيرات والتنبيهات الجوية
    """

    alert_id: UUID = Field(default_factory=uuid4, description="Alert identifier")
    tenant_id: UUID = Field(..., description="Affected tenant")
    field_ids: list[UUID] = Field(default_factory=list, description="Affected fields")
    alert_type: str = Field(
        ...,
        pattern="^(frost|heatwave|storm|heavy_rain|drought|wind)$",
        description="Alert type",
    )
    severity: str = Field(..., pattern="^(info|warning|critical)$", description="Alert severity")
    title: str = Field(..., description="Alert title")
    title_ar: str | None = Field(None, description="Arabic alert title")
    message: str = Field(..., description="Alert message")
    message_ar: str | None = Field(None, description="Arabic alert message")
    start_time: datetime = Field(..., description="Alert start time")
    end_time: datetime | None = Field(None, description="Alert end time")
    affected_area_radius_km: float | None = Field(None, ge=0, description="Affected area radius")


# ─────────────────────────────────────────────────────────────────────────────
# Satellite Events - أحداث الأقمار الصناعية
# ─────────────────────────────────────────────────────────────────────────────


class SatelliteDataReadyEvent(BaseEvent):
    """
    Event emitted when satellite imagery is processed and ready.
    حدث يُطلق عند معالجة صور الأقمار الصناعية وجاهزيتها
    """

    field_id: UUID = Field(..., description="Field identifier")
    tenant_id: UUID = Field(..., description="Tenant identifier")
    satellite_source: str = Field(..., description="Satellite source (e.g., Sentinel-2, Landsat)")
    capture_date: datetime = Field(..., description="Image capture date")
    processing_date: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Processing date")
    cloud_coverage: float | None = Field(None, ge=0, le=100, description="Cloud coverage percentage")

    # Vegetation indices
    ndvi_mean: float | None = Field(None, ge=-1, le=1, description="Mean NDVI value")
    ndvi_min: float | None = Field(None, ge=-1, le=1, description="Minimum NDVI value")
    ndvi_max: float | None = Field(None, ge=-1, le=1, description="Maximum NDVI value")
    evi_mean: float | None = Field(None, description="Mean EVI value")
    ndwi_mean: float | None = Field(None, ge=-1, le=1, description="Mean NDWI value")

    # Data URLs
    image_url: str | None = Field(None, description="Processed image URL")
    thumbnail_url: str | None = Field(None, description="Thumbnail URL")
    data_url: str | None = Field(None, description="Raw data URL")

    # Metadata
    resolution_meters: float | None = Field(None, ge=0, description="Image resolution")
    bands: list[str] | None = Field(default_factory=list, description="Available spectral bands")


class SatelliteAnomalyEvent(BaseEvent):
    """
    Event emitted when satellite analysis detects anomalies.
    حدث يُطلق عند اكتشاف شذوذات في التحليل الفضائي
    """

    anomaly_id: UUID = Field(default_factory=uuid4, description="Anomaly identifier")
    field_id: UUID = Field(..., description="Affected field")
    tenant_id: UUID = Field(..., description="Tenant identifier")
    anomaly_type: str = Field(
        ...,
        pattern="^(ndvi_drop|vegetation_loss|water_stress|disease_pattern|growth_delay)$",
        description="Anomaly type",
    )
    severity: str = Field(..., pattern="^(low|medium|high|critical)$", description="Anomaly severity")
    confidence_score: float = Field(..., ge=0, le=1, description="Detection confidence")
    affected_area_hectares: float | None = Field(None, ge=0, description="Affected area size")
    affected_area_percentage: float | None = Field(None, ge=0, le=100, description="Percentage of field affected")
    detection_date: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Detection date")

    # Comparison values
    current_value: float | None = Field(None, description="Current index value")
    baseline_value: float | None = Field(None, description="Baseline/expected value")
    deviation: float | None = Field(None, description="Deviation from baseline")

    # Location
    centroid_lat: float | None = Field(None, ge=-90, le=90, description="Anomaly centroid latitude")
    centroid_lon: float | None = Field(None, ge=-180, le=180, description="Anomaly centroid longitude")
    geometry_wkt: str | None = Field(None, description="Affected area geometry")

    # Recommendations
    recommended_action: str | None = Field(None, description="Recommended action")
    recommended_action_ar: str | None = Field(None, description="Arabic recommended action")


# ─────────────────────────────────────────────────────────────────────────────
# Health Events - أحداث الصحة النباتية
# ─────────────────────────────────────────────────────────────────────────────


class DiseaseDetectedEvent(BaseEvent):
    """
    Event emitted when crop disease is detected.
    حدث يُطلق عند اكتشاف مرض نباتي
    """

    detection_id: UUID = Field(default_factory=uuid4, description="Detection identifier")
    field_id: UUID = Field(..., description="Affected field")
    tenant_id: UUID = Field(..., description="Tenant identifier")
    crop_type: str | None = Field(None, description="Affected crop type")

    disease_name: str = Field(..., description="Disease name")
    disease_name_ar: str | None = Field(None, description="Arabic disease name")
    disease_category: str | None = Field(None, description="Disease category (fungal, bacterial, viral, pest)")

    confidence_score: float = Field(..., ge=0, le=1, description="Detection confidence")
    severity: str = Field(..., pattern="^(low|medium|high|critical)$", description="Disease severity")

    # Detection details
    detection_method: str | None = Field(None, description="Detection method (AI, manual, sensor)")
    affected_area_hectares: float | None = Field(None, ge=0, description="Affected area")
    symptoms_observed: list[str] | None = Field(default_factory=list, description="Observed symptoms")

    # Images
    image_urls: list[str] | None = Field(default_factory=list, description="Disease image URLs")

    # Recommendations
    treatment_recommendation: str | None = Field(None, description="Treatment recommendation")
    treatment_recommendation_ar: str | None = Field(None, description="Arabic treatment")
    urgency_level: str | None = Field(None, description="Treatment urgency")
    estimated_yield_impact: float | None = Field(None, ge=0, le=100, description="Est. yield impact %")


class CropStressEvent(BaseEvent):
    """
    Event emitted when crop stress is detected (water, nutrient, heat, etc.).
    حدث يُطلق عند اكتشاف إجهاد نباتي
    """

    stress_id: UUID = Field(default_factory=uuid4, description="Stress event identifier")
    field_id: UUID = Field(..., description="Affected field")
    tenant_id: UUID = Field(..., description="Tenant identifier")

    stress_type: str = Field(
        ...,
        pattern="^(water|nutrient|heat|cold|salinity|compaction)$",
        description="Stress type",
    )
    severity: str = Field(..., pattern="^(low|medium|high|critical)$", description="Stress severity")
    confidence_score: float = Field(..., ge=0, le=1, description="Detection confidence")

    # Indicators
    ndvi_value: float | None = Field(None, ge=-1, le=1, description="NDVI value")
    ndwi_value: float | None = Field(None, ge=-1, le=1, description="NDWI value (water stress)")
    temperature_value: float | None = Field(None, description="Temperature reading")
    soil_moisture_value: float | None = Field(None, ge=0, le=100, description="Soil moisture %")

    affected_area_hectares: float | None = Field(None, ge=0, description="Affected area")
    detection_date: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Detection date")

    # Recommendations
    action_required: str | None = Field(None, description="Required action")
    action_required_ar: str | None = Field(None, description="Arabic action required")
    time_sensitivity: str | None = Field(None, description="Time sensitivity (immediate, soon, monitor)")


# ─────────────────────────────────────────────────────────────────────────────
# Inventory Events - أحداث المخزون
# ─────────────────────────────────────────────────────────────────────────────


class LowStockEvent(BaseEvent):
    """
    Event emitted when inventory stock levels are low.
    حدث يُطلق عند انخفاض مستويات المخزون
    """

    alert_id: UUID = Field(default_factory=uuid4, description="Alert identifier")
    tenant_id: UUID = Field(..., description="Tenant identifier")
    warehouse_id: UUID | None = Field(None, description="Warehouse identifier")

    product_id: UUID = Field(..., description="Product identifier")
    product_name: str = Field(..., description="Product name")
    product_name_ar: str | None = Field(None, description="Arabic product name")
    product_category: str | None = Field(None, description="Product category")
    sku: str | None = Field(None, description="Product SKU")

    current_quantity: float = Field(..., ge=0, description="Current stock quantity")
    unit_of_measure: str = Field(..., description="Unit of measure (kg, L, units)")
    threshold_quantity: float = Field(..., ge=0, description="Low stock threshold")
    reorder_quantity: float | None = Field(None, ge=0, description="Recommended reorder quantity")

    severity: str = Field(..., pattern="^(low|medium|high|critical)$", description="Alert severity")

    # Supplier info
    preferred_supplier_id: UUID | None = Field(None, description="Preferred supplier")
    estimated_restock_days: int | None = Field(None, ge=0, description="Days to restock")

    # Cost estimation
    estimated_cost: float | None = Field(None, ge=0, description="Estimated reorder cost")
    currency: str | None = Field(default="SAR", description="Currency code")


class BatchExpiredEvent(BaseEvent):
    """
    Event emitted when product batch expires or is about to expire.
    حدث يُطلق عند انتهاء صلاحية دفعة منتج أو قرب انتهائها
    """

    alert_id: UUID = Field(default_factory=uuid4, description="Alert identifier")
    tenant_id: UUID = Field(..., description="Tenant identifier")
    warehouse_id: UUID | None = Field(None, description="Warehouse identifier")

    batch_id: UUID = Field(..., description="Batch identifier")
    batch_number: str = Field(..., description="Batch number")
    product_id: UUID = Field(..., description="Product identifier")
    product_name: str = Field(..., description="Product name")
    product_name_ar: str | None = Field(None, description="Arabic product name")

    expiry_date: datetime = Field(..., description="Batch expiry date")
    quantity: float = Field(..., ge=0, description="Batch quantity")
    unit_of_measure: str = Field(..., description="Unit of measure")

    status: str = Field(..., pattern="^(expiring_soon|expired|critical)$", description="Expiry status")
    days_until_expiry: int = Field(..., description="Days until expiry (negative if expired)")

    value_at_risk: float | None = Field(None, ge=0, description="Value of at-risk inventory")
    currency: str | None = Field(default="SAR", description="Currency code")

    # Recommendations
    recommended_action: str | None = Field(None, description="Recommended action")
    recommended_action_ar: str | None = Field(None, description="Arabic recommended action")


# ─────────────────────────────────────────────────────────────────────────────
# Billing Events - أحداث الفواتير والاشتراكات
# ─────────────────────────────────────────────────────────────────────────────


class SubscriptionCreatedEvent(BaseEvent):
    """
    Event emitted when a new subscription is created.
    حدث يُطلق عند إنشاء اشتراك جديد
    """

    subscription_id: UUID = Field(..., description="Subscription identifier")
    tenant_id: UUID = Field(..., description="Tenant identifier")
    user_id: UUID = Field(..., description="User who created subscription")

    plan_id: str = Field(..., description="Subscription plan ID")
    plan_name: str = Field(..., description="Plan name")
    plan_tier: str = Field(..., pattern="^(free|basic|professional|enterprise)$", description="Plan tier")

    billing_cycle: str = Field(..., pattern="^(monthly|quarterly|annual)$", description="Billing cycle")

    start_date: datetime = Field(..., description="Subscription start date")
    end_date: datetime | None = Field(None, description="Subscription end date")
    trial_end_date: datetime | None = Field(None, description="Trial period end date")

    # Pricing
    price_amount: float = Field(..., ge=0, description="Subscription price")
    currency: str = Field(default="SAR", description="Currency code")

    # Limits and features
    max_fields: int | None = Field(None, ge=0, description="Maximum fields allowed")
    max_area_hectares: float | None = Field(None, ge=0, description="Maximum area allowed")
    features_enabled: list[str] | None = Field(default_factory=list, description="Enabled features")

    auto_renew: bool = Field(default=True, description="Auto-renewal enabled")
    payment_method_id: str | None = Field(None, description="Payment method identifier")


class PaymentCompletedEvent(BaseEvent):
    """
    Event emitted when a payment is successfully completed.
    حدث يُطلق عند إتمام دفعة بنجاح
    """

    payment_id: UUID = Field(..., description="Payment identifier")
    subscription_id: UUID | None = Field(None, description="Related subscription")
    invoice_id: UUID | None = Field(None, description="Related invoice")
    tenant_id: UUID = Field(..., description="Tenant identifier")

    amount: float = Field(..., ge=0, description="Payment amount")
    currency: str = Field(default="SAR", description="Currency code")

    payment_method: str = Field(
        ...,
        pattern="^(credit_card|debit_card|bank_transfer|wallet|apple_pay|stc_pay|mada)$",
        description="Payment method",
    )
    payment_provider: str | None = Field(None, description="Payment provider (Stripe, Tap, etc.)")

    transaction_id: str = Field(..., description="Payment gateway transaction ID")
    payment_date: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Payment date")

    # Payment details
    description: str | None = Field(None, description="Payment description")
    description_ar: str | None = Field(None, description="Arabic payment description")

    # Tax and fees
    subtotal: float | None = Field(None, ge=0, description="Subtotal before tax")
    tax_amount: float | None = Field(None, ge=0, description="Tax amount (VAT)")
    tax_percentage: float | None = Field(None, ge=0, le=100, description="Tax percentage")

    # Receipt
    receipt_url: str | None = Field(None, description="Payment receipt URL")
    invoice_url: str | None = Field(None, description="Invoice URL")


class SubscriptionRenewedEvent(BaseEvent):
    """
    Event emitted when a subscription is renewed.
    حدث يُطلق عند تجديد اشتراك
    """

    subscription_id: UUID = Field(..., description="Subscription identifier")
    tenant_id: UUID = Field(..., description="Tenant identifier")
    renewal_date: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Renewal date")
    previous_end_date: datetime = Field(..., description="Previous end date")
    new_end_date: datetime = Field(..., description="New end date")
    payment_id: UUID | None = Field(None, description="Related payment")
    amount_charged: float = Field(..., ge=0, description="Amount charged for renewal")
    currency: str = Field(default="SAR", description="Currency code")


class PaymentFailedEvent(BaseEvent):
    """
    Event emitted when a payment fails.
    حدث يُطلق عند فشل عملية دفع
    """

    payment_id: UUID = Field(..., description="Failed payment identifier")
    subscription_id: UUID | None = Field(None, description="Related subscription")
    tenant_id: UUID = Field(..., description="Tenant identifier")

    amount: float = Field(..., ge=0, description="Payment amount")
    currency: str = Field(default="SAR", description="Currency code")

    failure_reason: str = Field(..., description="Failure reason code")
    failure_message: str | None = Field(None, description="Failure message")
    failure_message_ar: str | None = Field(None, description="Arabic failure message")

    payment_method: str | None = Field(None, description="Payment method used")
    retry_count: int = Field(default=0, ge=0, description="Number of retry attempts")
    next_retry_date: datetime | None = Field(None, description="Next automatic retry date")


# ─────────────────────────────────────────────────────────────────────────────
# AI Agent Events - أحداث الوكلاء الذكية
# ─────────────────────────────────────────────────────────────────────────────


class AgentExecutionStartedEvent(BaseEvent):
    """
    Event emitted when an AI agent starts execution.
    حدث يُطلق عند بدء تنفيذ وكيل ذكي
    """

    execution_id: str = Field(..., description="Execution identifier")
    agent_type: str = Field(..., description="Type of agent (farm_advisor, research, planner)")
    tenant_id: str = Field(..., description="Tenant identifier")
    task: str = Field(..., description="Task description")
    mode: str = Field(default="hybrid", description="Execution mode (plan, execute, hybrid)")
    field_id: str | None = Field(None, description="Target field ID if applicable")
    farm_id: str | None = Field(None, description="Target farm ID if applicable")


class AgentExecutionCompletedEvent(BaseEvent):
    """
    Event emitted when an AI agent completes execution successfully.
    حدث يُطلق عند إكمال تنفيذ وكيل ذكي بنجاح
    """

    execution_id: str = Field(..., description="Execution identifier")
    agent_type: str = Field(..., description="Type of agent")
    tenant_id: str = Field(..., description="Tenant identifier")
    status: str = Field(default="completed", description="Completion status")
    total_steps: int = Field(default=0, ge=0, description="Total steps executed")
    duration_ms: int = Field(default=0, ge=0, description="Total duration in milliseconds")
    result_summary: str | None = Field(None, description="Summary of execution result")
    result_summary_ar: str | None = Field(None, description="Arabic summary")


class AgentExecutionFailedEvent(BaseEvent):
    """
    Event emitted when an AI agent execution fails.
    حدث يُطلق عند فشل تنفيذ وكيل ذكي
    """

    execution_id: str = Field(..., description="Execution identifier")
    agent_type: str = Field(..., description="Type of agent")
    tenant_id: str = Field(..., description="Tenant identifier")
    error_type: str = Field(..., description="Error type/code")
    error_message: str = Field(..., description="Error message")
    error_message_ar: str | None = Field(None, description="Arabic error message")
    failed_at_step: int | None = Field(None, description="Step number where failure occurred")
    duration_ms: int = Field(default=0, ge=0, description="Duration before failure")


class AgentStepCompletedEvent(BaseEvent):
    """
    Event emitted when an AI agent completes a step.
    حدث يُطلق عند إكمال وكيل ذكي لخطوة
    """

    execution_id: str = Field(..., description="Execution identifier")
    step_number: int = Field(..., ge=1, description="Step number")
    action: str = Field(..., description="Action taken")
    action_ar: str | None = Field(None, description="Arabic action description")
    tool_used: str | None = Field(None, description="Tool used in this step")
    duration_ms: int = Field(default=0, ge=0, description="Step duration")
    success: bool = Field(default=True, description="Whether step succeeded")


# ─────────────────────────────────────────────────────────────────────────────
# CRM Events - أحداث إدارة علاقات المزارعين
# ─────────────────────────────────────────────────────────────────────────────


class FarmerCreatedEvent(BaseEvent):
    """
    Event emitted when a new farmer is created in CRM.
    حدث يُطلق عند إنشاء مزارع جديد
    """

    farmer_id: str = Field(..., description="Farmer identifier")
    tenant_id: str = Field(..., description="Tenant identifier")
    name: str = Field(..., description="Farmer name")
    name_ar: str | None = Field(None, description="Arabic name")
    phone_last4: str | None = Field(None, description="Last 4 digits of phone (masked for privacy)")
    status: str = Field(default="lead", description="Initial status")
    farm_size_hectares: float | None = Field(None, ge=0, description="Farm size")
    primary_crops: list[str] = Field(default_factory=list, description="Primary crops")


class FarmerUpdatedEvent(BaseEvent):
    """
    Event emitted when a farmer profile is updated.
    حدث يُطلق عند تحديث ملف مزارع
    """

    farmer_id: str = Field(..., description="Farmer identifier")
    tenant_id: str = Field(..., description="Tenant identifier")
    updated_fields: list[str] = Field(..., description="List of updated fields")
    new_status: str | None = Field(None, description="New status if changed")


class FarmerStatusChangedEvent(BaseEvent):
    """
    Event emitted when a farmer's status changes.
    حدث يُطلق عند تغيير حالة مزارع
    """

    farmer_id: str = Field(..., description="Farmer identifier")
    tenant_id: str = Field(..., description="Tenant identifier")
    old_status: str = Field(..., description="Previous status")
    new_status: str = Field(..., description="New status")
    reason: str | None = Field(None, description="Reason for status change")


class HarvestDealCreatedEvent(BaseEvent):
    """
    Event emitted when a new harvest deal is created.
    حدث يُطلق عند إنشاء صفقة حصاد جديدة
    """

    deal_id: str = Field(..., description="Deal identifier")
    farmer_id: str = Field(..., description="Farmer identifier")
    tenant_id: str = Field(..., description="Tenant identifier")
    crop_type: str = Field(..., description="Crop type")
    crop_type_ar: str | None = Field(None, description="Arabic crop type")
    expected_quantity_tons: float = Field(..., gt=0, description="Expected quantity")
    expected_harvest_date: str = Field(..., description="Expected harvest date (ISO)")
    price_per_ton: float | None = Field(None, gt=0, description="Price per ton")


class HarvestDealStageChangedEvent(BaseEvent):
    """
    Event emitted when a harvest deal stage changes.
    حدث يُطلق عند تغيير مرحلة صفقة الحصاد
    """

    deal_id: str = Field(..., description="Deal identifier")
    farmer_id: str = Field(..., description="Farmer identifier")
    tenant_id: str = Field(..., description="Tenant identifier")
    old_stage: str = Field(..., description="Previous stage")
    new_stage: str = Field(..., description="New stage")
    total_value: float | None = Field(None, description="Total deal value")


class InteractionLoggedEvent(BaseEvent):
    """
    Event emitted when an interaction with a farmer is logged.
    حدث يُطلق عند تسجيل تفاعل مع مزارع
    """

    interaction_id: str = Field(..., description="Interaction identifier")
    farmer_id: str = Field(..., description="Farmer identifier")
    tenant_id: str = Field(..., description="Tenant identifier")
    interaction_type: str = Field(..., description="Type (call, visit, whatsapp, sms, email)")
    subject: str = Field(..., description="Interaction subject")
    outcome: str | None = Field(None, description="Interaction outcome")
    follow_up_required: bool = Field(default=False, description="Follow-up needed")


# ─────────────────────────────────────────────────────────────────────────────
# Low-Code Events - أحداث محرك التطوير منخفض الكود
# ─────────────────────────────────────────────────────────────────────────────


class PageCreatedEvent(BaseEvent):
    """
    Event emitted when a new page is created.
    حدث يُطلق عند إنشاء صفحة جديدة
    """

    page_id: str = Field(..., description="Page identifier")
    tenant_id: str = Field(..., description="Tenant identifier")
    name: str = Field(..., description="Page name")
    name_ar: str | None = Field(None, description="Arabic name")
    route: str = Field(..., description="Page route")
    blocks_count: int = Field(default=0, ge=0, description="Number of blocks")
    data_model_id: str | None = Field(None, description="Associated data model")


class PagePublishedEvent(BaseEvent):
    """
    Event emitted when a page is published.
    حدث يُطلق عند نشر صفحة
    """

    page_id: str = Field(..., description="Page identifier")
    tenant_id: str = Field(..., description="Tenant identifier")
    name: str = Field(..., description="Page name")
    route: str = Field(..., description="Published route")
    page_version: int = Field(default=1, ge=1, description="Published page version number")


class DataModelCreatedEvent(BaseEvent):
    """
    Event emitted when a data model is created.
    حدث يُطلق عند إنشاء نموذج بيانات
    """

    model_id: str = Field(..., description="Data model identifier")
    tenant_id: str = Field(..., description="Tenant identifier")
    name: str = Field(..., description="Model name")
    name_ar: str | None = Field(None, description="Arabic name")
    fields_count: int = Field(default=0, ge=0, description="Number of fields")


class WorkflowExecutedEvent(BaseEvent):
    """
    Event emitted when a workflow is executed.
    حدث يُطلق عند تنفيذ سير عمل
    """

    workflow_id: str = Field(..., description="Workflow identifier")
    page_id: str | None = Field(None, description="Associated page")
    tenant_id: str = Field(..., description="Tenant identifier")
    trigger: str = Field(..., description="Workflow trigger")
    status: str = Field(default="completed", description="Execution status")
    duration_ms: int = Field(default=0, ge=0, description="Execution duration")


# ─────────────────────────────────────────────────────────────────────────────
# WeChat Events - أحداث ويتشات
# ─────────────────────────────────────────────────────────────────────────────


class WeChatMessageReceivedEvent(BaseEvent):
    """
    Event emitted when a WeChat message is received.
    حدث يُطلق عند استلام رسالة ويتشات
    """

    message_id: str = Field(..., description="WeChat message identifier")
    tenant_id: str = Field(..., description="Tenant identifier")
    from_user_id: str = Field(..., description="Sender WeChat user ID")
    from_user_name: str | None = Field(None, description="Sender display name")
    to_user_id: str = Field(..., description="Recipient WeChat user ID")
    message_type: str = Field(
        ...,
        pattern="^(text|image|voice|video|location|link|event)$",
        description="Message type",
    )
    content: str | None = Field(None, description="Message content (for text messages)")
    media_id: str | None = Field(None, description="Media ID (for media messages)")
    location_lat: float | None = Field(None, ge=-90, le=90, description="Location latitude")
    location_lon: float | None = Field(None, ge=-180, le=180, description="Location longitude")
    received_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Message received time")


class WeChatMessageSentEvent(BaseEvent):
    """
    Event emitted when a WeChat message is sent.
    حدث يُطلق عند إرسال رسالة ويتشات
    """

    message_id: str = Field(..., description="WeChat message identifier")
    tenant_id: str = Field(..., description="Tenant identifier")
    to_user_id: str = Field(..., description="Recipient WeChat user ID")
    to_user_name: str | None = Field(None, description="Recipient display name")
    message_type: str = Field(
        ...,
        pattern="^(text|image|voice|video|news|template)$",
        description="Message type",
    )
    content: str | None = Field(None, description="Message content")
    template_id: str | None = Field(None, description="Template ID for template messages")
    status: str = Field(default="sent", description="Send status (sent, delivered, failed)")
    sent_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Message sent time")
    error_message: str | None = Field(None, description="Error message if failed")


class WeChatContactAddedEvent(BaseEvent):
    """
    Event emitted when a new WeChat contact is added.
    حدث يُطلق عند إضافة جهة اتصال ويتشات جديدة
    """

    contact_id: str = Field(..., description="Internal contact identifier")
    tenant_id: str = Field(..., description="Tenant identifier")
    wechat_user_id: str = Field(..., description="WeChat user ID")
    nickname: str | None = Field(None, description="WeChat nickname")
    avatar_url: str | None = Field(None, description="Profile avatar URL")
    gender: str | None = Field(None, pattern="^(male|female|unknown)$", description="Gender")
    city: str | None = Field(None, description="City")
    province: str | None = Field(None, description="Province")
    country: str | None = Field(None, description="Country")
    language: str | None = Field(None, description="Language preference")
    farmer_id: str | None = Field(None, description="Linked farmer ID in CRM")
    subscribed_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Subscription time")


class WeChatMomentPublishedEvent(BaseEvent):
    """
    Event emitted when a WeChat Moment is published.
    حدث يُطلق عند نشر لحظة ويتشات
    """

    moment_id: str = Field(..., description="Moment identifier")
    tenant_id: str = Field(..., description="Tenant identifier")
    content: str = Field(..., description="Moment text content")
    content_ar: str | None = Field(None, description="Arabic content")
    media_urls: list[str] = Field(default_factory=list, description="Attached media URLs")
    media_type: str | None = Field(None, pattern="^(image|video|link)$", description="Media type")
    link_url: str | None = Field(None, description="External link URL")
    link_title: str | None = Field(None, description="Link title")
    visibility: str = Field(default="public", description="Visibility (public, contacts, private)")
    published_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Publish time")
    target_audience: list[str] = Field(default_factory=list, description="Target audience tags")


class WeChatChatSummarizedEvent(BaseEvent):
    """
    Event emitted when a WeChat chat conversation is summarized.
    حدث يُطلق عند تلخيص محادثة ويتشات
    """

    summary_id: str = Field(..., description="Summary identifier")
    tenant_id: str = Field(..., description="Tenant identifier")
    contact_id: str = Field(..., description="Contact identifier")
    farmer_id: str | None = Field(None, description="Linked farmer ID")
    conversation_start: datetime = Field(..., description="Conversation start time")
    conversation_end: datetime = Field(..., description="Conversation end time")
    message_count: int = Field(..., ge=1, description="Number of messages summarized")
    summary: str = Field(..., description="AI-generated summary in English")
    summary_ar: str | None = Field(None, description="AI-generated summary in Arabic")
    key_topics: list[str] = Field(default_factory=list, description="Key topics discussed")
    sentiment: str | None = Field(
        None,
        pattern="^(positive|neutral|negative|mixed)$",
        description="Overall conversation sentiment",
    )
    action_items: list[str] = Field(default_factory=list, description="Extracted action items")
    follow_up_required: bool = Field(default=False, description="Follow-up needed")
    follow_up_date: datetime | None = Field(None, description="Suggested follow-up date")


# ─────────────────────────────────────────────────────────────────────────────
# Exports
# ─────────────────────────────────────────────────────────────────────────────

__all__ = [
    # Base
    "BaseEvent",
    # Field events
    "FieldCreatedEvent",
    "FieldUpdatedEvent",
    "FieldDeletedEvent",
    # Weather events
    "WeatherForecastEvent",
    "WeatherAlertEvent",
    # Satellite events
    "SatelliteDataReadyEvent",
    "SatelliteAnomalyEvent",
    # Health events
    "DiseaseDetectedEvent",
    "CropStressEvent",
    # Inventory events
    "LowStockEvent",
    "BatchExpiredEvent",
    # Billing events
    "SubscriptionCreatedEvent",
    "PaymentCompletedEvent",
    "SubscriptionRenewedEvent",
    "PaymentFailedEvent",
    # AI Agent events
    "AgentExecutionStartedEvent",
    "AgentExecutionCompletedEvent",
    "AgentExecutionFailedEvent",
    "AgentStepCompletedEvent",
    # CRM events
    "FarmerCreatedEvent",
    "FarmerUpdatedEvent",
    "FarmerStatusChangedEvent",
    "HarvestDealCreatedEvent",
    "HarvestDealStageChangedEvent",
    "InteractionLoggedEvent",
    # Low-Code events
    "PageCreatedEvent",
    "PagePublishedEvent",
    "DataModelCreatedEvent",
    "WorkflowExecutedEvent",
    # WeChat events
    "WeChatMessageReceivedEvent",
    "WeChatMessageSentEvent",
    "WeChatContactAddedEvent",
    "WeChatMomentPublishedEvent",
    "WeChatChatSummarizedEvent",
    # Validation utilities
    "validate_event_payload",
    "REQUIRED_EVENT_FIELDS",
]
