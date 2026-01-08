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

from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

# ─────────────────────────────────────────────────────────────────────────────
# Base Event Model - النموذج الأساسي للأحداث
# ─────────────────────────────────────────────────────────────────────────────


class BaseEvent(BaseModel):
    """
    Base class for all SAHOOL events with common metadata.
    النموذج الأساسي لجميع الأحداث مع البيانات الوصفية المشتركة
    """

    event_id: str = Field(
        default_factory=lambda: str(uuid4()), description="Unique event identifier"
    )
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Event timestamp")
    version: str = Field(default="1.0", description="Event schema version")
    source_service: str | None = Field(None, description="Service that emitted the event")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }
        populate_by_name = True


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
    processing_date: datetime = Field(
        default_factory=datetime.utcnow, description="Processing date"
    )
    cloud_coverage: float | None = Field(
        None, ge=0, le=100, description="Cloud coverage percentage"
    )

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
    severity: str = Field(
        ..., pattern="^(low|medium|high|critical)$", description="Anomaly severity"
    )
    confidence_score: float = Field(..., ge=0, le=1, description="Detection confidence")
    affected_area_hectares: float | None = Field(None, ge=0, description="Affected area size")
    affected_area_percentage: float | None = Field(
        None, ge=0, le=100, description="Percentage of field affected"
    )
    detection_date: datetime = Field(default_factory=datetime.utcnow, description="Detection date")

    # Comparison values
    current_value: float | None = Field(None, description="Current index value")
    baseline_value: float | None = Field(None, description="Baseline/expected value")
    deviation: float | None = Field(None, description="Deviation from baseline")

    # Location
    centroid_lat: float | None = Field(None, ge=-90, le=90, description="Anomaly centroid latitude")
    centroid_lon: float | None = Field(
        None, ge=-180, le=180, description="Anomaly centroid longitude"
    )
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
    disease_category: str | None = Field(
        None, description="Disease category (fungal, bacterial, viral, pest)"
    )

    confidence_score: float = Field(..., ge=0, le=1, description="Detection confidence")
    severity: str = Field(
        ..., pattern="^(low|medium|high|critical)$", description="Disease severity"
    )

    # Detection details
    detection_method: str | None = Field(None, description="Detection method (AI, manual, sensor)")
    affected_area_hectares: float | None = Field(None, ge=0, description="Affected area")
    symptoms_observed: list[str] | None = Field(
        default_factory=list, description="Observed symptoms"
    )

    # Images
    image_urls: list[str] | None = Field(default_factory=list, description="Disease image URLs")

    # Recommendations
    treatment_recommendation: str | None = Field(None, description="Treatment recommendation")
    treatment_recommendation_ar: str | None = Field(None, description="Arabic treatment")
    urgency_level: str | None = Field(None, description="Treatment urgency")
    estimated_yield_impact: float | None = Field(
        None, ge=0, le=100, description="Est. yield impact %"
    )


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
    severity: str = Field(
        ..., pattern="^(low|medium|high|critical)$", description="Stress severity"
    )
    confidence_score: float = Field(..., ge=0, le=1, description="Detection confidence")

    # Indicators
    ndvi_value: float | None = Field(None, ge=-1, le=1, description="NDVI value")
    ndwi_value: float | None = Field(None, ge=-1, le=1, description="NDWI value (water stress)")
    temperature_value: float | None = Field(None, description="Temperature reading")
    soil_moisture_value: float | None = Field(None, ge=0, le=100, description="Soil moisture %")

    affected_area_hectares: float | None = Field(None, ge=0, description="Affected area")
    detection_date: datetime = Field(default_factory=datetime.utcnow, description="Detection date")

    # Recommendations
    action_required: str | None = Field(None, description="Required action")
    action_required_ar: str | None = Field(None, description="Arabic action required")
    time_sensitivity: str | None = Field(
        None, description="Time sensitivity (immediate, soon, monitor)"
    )


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

    status: str = Field(
        ..., pattern="^(expiring_soon|expired|critical)$", description="Expiry status"
    )
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
    plan_tier: str = Field(
        ..., pattern="^(free|basic|professional|enterprise)$", description="Plan tier"
    )

    billing_cycle: str = Field(
        ..., pattern="^(monthly|quarterly|annual)$", description="Billing cycle"
    )

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
    payment_date: datetime = Field(default_factory=datetime.utcnow, description="Payment date")

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
    renewal_date: datetime = Field(default_factory=datetime.utcnow, description="Renewal date")
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
]
