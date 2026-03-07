"""
Traceability Models - Farm-to-Table Tracking
نماذج التتبع - من المزرعة إلى المائدة

Data models for produce batch tracking, supply chain events,
certifications, and consumer-facing product journey display.

نماذج البيانات لتتبع دفعات المنتجات، أحداث سلسلة التوريد،
الشهادات، وعرض رحلة المنتج للمستهلك.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import uuid4

# ─────────────────────────────────────────────────────────────────────────────
# Enums - التعدادات
# ─────────────────────────────────────────────────────────────────────────────


class EventType(StrEnum):
    """Supply chain event types - أنواع أحداث سلسلة التوريد"""

    HARVEST = "harvest"  # الحصاد
    PROCESSING = "processing"  # المعالجة
    STORAGE = "storage"  # التخزين
    TRANSPORT = "transport"  # النقل
    RETAIL = "retail"  # البيع بالتجزئة
    CONSUMER_SCAN = "consumer_scan"  # مسح المستهلك


class BatchStatus(StrEnum):
    """Batch lifecycle status - حالة دورة حياة الدفعة"""

    CREATED = "created"  # تم الإنشاء
    HARVESTED = "harvested"  # تم الحصاد
    IN_PROCESSING = "in_processing"  # قيد المعالجة
    IN_STORAGE = "in_storage"  # في التخزين
    IN_TRANSIT = "in_transit"  # في النقل
    AT_RETAIL = "at_retail"  # في المتجر
    SOLD = "sold"  # تم البيع
    EXPIRED = "expired"  # منتهي الصلاحية
    RECALLED = "recalled"  # تم استرجاعه


class CertificationType(StrEnum):
    """Types of certifications - أنواع الشهادات"""

    GLOBALGAP = "globalgap"  # GlobalGAP
    ORGANIC = "organic"  # عضوي
    HALAL = "halal"  # حلال
    SASO = "saso"  # هيئة المواصفات السعودية
    SFDA = "sfda"  # الهيئة العامة للغذاء والدواء
    ISO_22000 = "iso_22000"  # ISO 22000
    HACCP = "haccp"  # HACCP
    FAIR_TRADE = "fair_trade"  # التجارة العادلة
    LOCAL_GAP = "local_gap"  # الممارسات الزراعية المحلية


class QualityGrade(StrEnum):
    """Product quality grades - درجات جودة المنتج"""

    PREMIUM = "premium"  # ممتاز
    GRADE_A = "grade_a"  # درجة أ
    GRADE_B = "grade_b"  # درجة ب
    GRADE_C = "grade_c"  # درجة ج
    REJECTED = "rejected"  # مرفوض


class StorageCondition(StrEnum):
    """Storage condition types - أنواع ظروف التخزين"""

    AMBIENT = "ambient"  # درجة حرارة الغرفة
    CHILLED = "chilled"  # مبرد (0-4 درجة)
    FROZEN = "frozen"  # مجمد
    CONTROLLED_ATMOSPHERE = "controlled_atmosphere"  # جو متحكم به
    HUMIDITY_CONTROLLED = "humidity_controlled"  # رطوبة متحكم بها


class TransportMode(StrEnum):
    """Transport mode types - أنواع وسائل النقل"""

    TRUCK_REFRIGERATED = "truck_refrigerated"  # شاحنة مبردة
    TRUCK_AMBIENT = "truck_ambient"  # شاحنة عادية
    AIR_FREIGHT = "air_freight"  # شحن جوي
    SEA_FREIGHT = "sea_freight"  # شحن بحري
    RAIL = "rail"  # سكك حديدية
    LOCAL_DELIVERY = "local_delivery"  # توصيل محلي


# ─────────────────────────────────────────────────────────────────────────────
# Location Models - نماذج الموقع
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class GeoLocation:
    """Geographic location - الموقع الجغرافي"""

    latitude: float
    longitude: float
    altitude_m: float | None = None
    accuracy_m: float | None = None


@dataclass
class Address:
    """Physical address - العنوان الفعلي"""

    address_line1_en: str
    address_line1_ar: str
    city_en: str
    city_ar: str
    region_en: str
    region_ar: str
    country_code: str  # ISO 3166-1 alpha-2
    postal_code: str | None = None
    address_line2_en: str | None = None
    address_line2_ar: str | None = None


# ─────────────────────────────────────────────────────────────────────────────
# Actor Models - نماذج الجهات الفاعلة
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class Producer:
    """Farm/Producer information - معلومات المزرعة/المنتج"""

    id: str
    name_en: str
    name_ar: str
    farm_name_en: str
    farm_name_ar: str
    registration_number: str  # رقم التسجيل
    address: Address
    location: GeoLocation | None = None
    contact_phone: str | None = None
    contact_email: str | None = None
    certifications: list[str] = field(default_factory=list)  # Certification IDs


@dataclass
class ProcessingFacility:
    """Processing/Packing facility - مرفق المعالجة/التعبئة"""

    id: str
    name_en: str
    name_ar: str
    facility_type_en: str  # e.g., "Packing House", "Processing Plant"
    facility_type_ar: str
    registration_number: str
    address: Address
    location: GeoLocation | None = None
    certifications: list[str] = field(default_factory=list)


@dataclass
class Transporter:
    """Transport company - شركة النقل"""

    id: str
    company_name_en: str
    company_name_ar: str
    vehicle_id: str
    driver_name: str | None = None
    license_number: str | None = None


@dataclass
class Retailer:
    """Retail outlet - منفذ البيع بالتجزئة"""

    id: str
    name_en: str
    name_ar: str
    store_type_en: str  # e.g., "Supermarket", "Farmers Market"
    store_type_ar: str
    address: Address
    location: GeoLocation | None = None


# ─────────────────────────────────────────────────────────────────────────────
# Certification Models - نماذج الشهادات
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class Certification:
    """Certification record - سجل الشهادة"""

    id: str
    certification_type: CertificationType
    certificate_number: str

    # Names
    name_en: str  # e.g., "GlobalGAP IFA v6"
    name_ar: str

    # Issuing body
    issuing_body_en: str
    issuing_body_ar: str

    # Validity
    issue_date: datetime
    expiry_date: datetime

    # Scope
    scope_en: str  # What is certified
    scope_ar: str

    # Status
    is_valid: bool = True

    # Verification
    verification_url: str | None = None  # URL to verify certificate
    certificate_document_url: str | None = None

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def is_currently_valid(self) -> bool:
        """Check if certification is currently valid"""
        return self.is_valid and datetime.now(UTC) < self.expiry_date


@dataclass
class ComplianceRecord:
    """Compliance/inspection record - سجل الامتثال/التفتيش"""

    id: str
    certification_id: str
    inspection_date: datetime
    inspector_name: str

    # Results
    is_compliant: bool
    score: float | None = None  # Percentage or points

    # Details
    findings_en: str | None = None
    findings_ar: str | None = None

    # Corrective actions
    corrective_actions_en: list[str] = field(default_factory=list)
    corrective_actions_ar: list[str] = field(default_factory=list)

    # Documents
    report_url: str | None = None


# ─────────────────────────────────────────────────────────────────────────────
# Batch Models - نماذج الدفعات
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class ProduceBatch:
    """
    Produce batch for tracking - دفعة المنتج للتتبع

    Represents a batch of agricultural produce from harvest to consumer.
    يمثل دفعة من المنتجات الزراعية من الحصاد إلى المستهلك.
    """

    id: str = field(default_factory=lambda: str(uuid4()))
    batch_code: str = ""  # Human-readable batch code (e.g., "WH-2025-001")

    # Tenant and farm
    tenant_id: str = ""
    farm_id: str = ""
    field_id: str = ""

    # Product info
    product_name_en: str = ""
    product_name_ar: str = ""
    variety_en: str = ""
    variety_ar: str = ""

    # Quantity
    quantity: float = 0.0
    quantity_unit: str = "kg"  # kg, ton, crate, box

    # Quality
    quality_grade: QualityGrade = QualityGrade.GRADE_A

    # Status
    status: BatchStatus = BatchStatus.CREATED

    # Dates
    harvest_date: datetime | None = None
    pack_date: datetime | None = None
    expiry_date: datetime | None = None

    # Producer
    producer_id: str | None = None

    # Certifications associated with this batch
    certification_ids: list[str] = field(default_factory=list)

    # QR code
    qr_code_url: str | None = None
    qr_code_data: str | None = None

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    # Custom attributes
    attributes: dict = field(default_factory=dict)


@dataclass
class BatchSplit:
    """Record of batch splitting - سجل تقسيم الدفعة"""

    id: str
    parent_batch_id: str
    child_batch_ids: list[str]
    split_date: datetime
    reason_en: str
    reason_ar: str
    performed_by: str  # User ID


@dataclass
class BatchMerge:
    """Record of batch merging - سجل دمج الدفعات"""

    id: str
    source_batch_ids: list[str]
    target_batch_id: str
    merge_date: datetime
    reason_en: str
    reason_ar: str
    performed_by: str  # User ID


# ─────────────────────────────────────────────────────────────────────────────
# Supply Chain Event Models - نماذج أحداث سلسلة التوريد
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class SupplyChainEvent:
    """
    Base supply chain event - حدث سلسلة التوريد الأساسي

    Records a single event in the product's journey from farm to consumer.
    يسجل حدثاً واحداً في رحلة المنتج من المزرعة إلى المستهلك.
    """

    id: str = field(default_factory=lambda: str(uuid4()))
    batch_id: str = ""
    event_type: EventType = EventType.HARVEST

    # Timestamp
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    # Location
    location: GeoLocation | None = None
    location_name_en: str = ""
    location_name_ar: str = ""

    # Actor (who performed the event)
    actor_id: str = ""  # Producer, Facility, Transporter, or Retailer ID
    actor_type: str = ""  # "producer", "facility", "transporter", "retailer"
    actor_name_en: str = ""
    actor_name_ar: str = ""

    # Description
    description_en: str = ""
    description_ar: str = ""

    # Evidence
    photos: list[str] = field(default_factory=list)  # Photo URLs
    documents: list[str] = field(default_factory=list)  # Document URLs

    # Verification
    verified: bool = False
    verified_by: str | None = None
    verification_timestamp: datetime | None = None

    # Digital signature (for authenticity)
    signature: str | None = None

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class HarvestEvent(SupplyChainEvent):
    """Harvest event details - تفاصيل حدث الحصاد"""

    # Override defaults
    event_type: EventType = field(default=EventType.HARVEST)

    # Harvest-specific fields
    field_id: str = ""
    field_name_en: str = ""
    field_name_ar: str = ""

    # Crop details
    crop_type: str = ""
    variety: str = ""

    # Harvest details
    harvest_method_en: str = ""  # e.g., "Manual", "Mechanical"
    harvest_method_ar: str = ""

    # Weather at harvest
    temperature_c: float | None = None
    humidity_percent: float | None = None

    # Quality at harvest
    quality_notes_en: str = ""
    quality_notes_ar: str = ""


@dataclass
class ProcessingEvent(SupplyChainEvent):
    """Processing/Packing event details - تفاصيل حدث المعالجة/التعبئة"""

    event_type: EventType = field(default=EventType.PROCESSING)

    # Facility
    facility_id: str = ""
    facility_name_en: str = ""
    facility_name_ar: str = ""

    # Processing type
    processing_type_en: str = ""  # e.g., "Washing", "Grading", "Packing"
    processing_type_ar: str = ""

    # Input/Output
    input_quantity: float = 0.0
    output_quantity: float = 0.0
    quantity_unit: str = "kg"
    loss_percentage: float = 0.0

    # Quality control
    quality_check_passed: bool = True
    quality_grade: QualityGrade | None = None
    quality_notes_en: str = ""
    quality_notes_ar: str = ""


@dataclass
class StorageEvent(SupplyChainEvent):
    """Storage event details - تفاصيل حدث التخزين"""

    event_type: EventType = field(default=EventType.STORAGE)

    # Storage facility
    facility_id: str = ""
    facility_name_en: str = ""
    facility_name_ar: str = ""
    storage_unit_id: str = ""  # e.g., "Cold Room 3"

    # Storage conditions
    storage_condition: StorageCondition = StorageCondition.CHILLED
    target_temperature_c: float | None = None
    actual_temperature_c: float | None = None
    target_humidity_percent: float | None = None
    actual_humidity_percent: float | None = None

    # Duration
    storage_start: datetime = field(default_factory=lambda: datetime.now(UTC))
    storage_end: datetime | None = None

    # Notes
    condition_notes_en: str = ""
    condition_notes_ar: str = ""


@dataclass
class TransportEvent(SupplyChainEvent):
    """Transport event details - تفاصيل حدث النقل"""

    event_type: EventType = field(default=EventType.TRANSPORT)

    # Transporter
    transporter_id: str = ""
    transporter_name_en: str = ""
    transporter_name_ar: str = ""
    vehicle_id: str = ""

    # Route
    origin_en: str = ""
    origin_ar: str = ""
    origin_location: GeoLocation | None = None
    destination_en: str = ""
    destination_ar: str = ""
    destination_location: GeoLocation | None = None

    # Transport mode
    transport_mode: TransportMode = TransportMode.TRUCK_REFRIGERATED

    # Temperature control
    target_temperature_c: float | None = None
    min_recorded_temperature_c: float | None = None
    max_recorded_temperature_c: float | None = None

    # Timing
    departure_time: datetime | None = None
    arrival_time: datetime | None = None

    # Distance
    distance_km: float | None = None


@dataclass
class RetailEvent(SupplyChainEvent):
    """Retail arrival/display event - حدث الوصول/العرض في التجزئة"""

    event_type: EventType = field(default=EventType.RETAIL)

    # Retailer
    retailer_id: str = ""
    retailer_name_en: str = ""
    retailer_name_ar: str = ""
    store_location_en: str = ""
    store_location_ar: str = ""

    # Receiving
    received_quantity: float = 0.0
    quantity_unit: str = "kg"

    # Quality check at receipt
    quality_check_passed: bool = True
    temperature_at_receipt_c: float | None = None

    # Display
    display_location_en: str = ""  # e.g., "Produce Aisle", "Cold Section"
    display_location_ar: str = ""

    # Pricing
    unit_price: float | None = None
    currency: str = "SAR"


@dataclass
class ConsumerScanEvent(SupplyChainEvent):
    """Consumer QR scan event - حدث مسح المستهلك للرمز"""

    event_type: EventType = field(default=EventType.CONSUMER_SCAN)

    # Scan info
    scan_location: GeoLocation | None = None
    device_type: str = ""  # "mobile", "tablet", "kiosk"

    # Session (anonymous tracking)
    session_id: str = ""

    # Consumer feedback (optional)
    rating: int | None = None  # 1-5
    feedback_en: str | None = None
    feedback_ar: str | None = None


# ─────────────────────────────────────────────────────────────────────────────
# Consumer-Facing Models - نماذج واجهة المستهلك
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class ProductJourneyStep:
    """Single step in product journey display - خطوة واحدة في عرض رحلة المنتج"""

    step_number: int
    event_type: EventType

    # Display info
    title_en: str
    title_ar: str
    description_en: str
    description_ar: str

    # Location
    location_en: str
    location_ar: str

    # Date
    date: datetime

    # Icon/image
    icon: str = ""  # Icon name or URL
    image_url: str | None = None

    # Verification badge
    verified: bool = False


@dataclass
class ProductJourney:
    """
    Complete product journey for consumer display
    رحلة المنتج الكاملة لعرض المستهلك
    """

    batch_id: str
    batch_code: str

    # Product info
    product_name_en: str
    product_name_ar: str
    variety_en: str
    variety_ar: str

    # Producer info
    producer_name_en: str
    producer_name_ar: str
    farm_name_en: str
    farm_name_ar: str
    farm_location_en: str
    farm_location_ar: str

    # Quality
    quality_grade: QualityGrade

    # Dates
    harvest_date: datetime
    pack_date: datetime | None = None
    expiry_date: datetime | None = None

    # Journey steps
    steps: list[ProductJourneyStep] = field(default_factory=list)

    # Certifications
    certifications: list[Certification] = field(default_factory=list)

    # Freshness
    days_since_harvest: int = 0
    freshness_score: int = 100  # 0-100

    # Sustainability metrics
    transport_distance_km: float = 0.0
    carbon_footprint_kg: float | None = None

    # Total journey time
    journey_duration_hours: float = 0.0


@dataclass
class QRCodeData:
    """Data encoded in QR code - البيانات المشفرة في رمز QR"""

    batch_id: str
    batch_code: str
    product_name_en: str
    product_name_ar: str
    producer_name_en: str
    producer_name_ar: str
    harvest_date: str  # ISO format
    verification_url: str  # URL to full journey

    # Compact format for QR
    def to_compact_string(self) -> str:
        """Generate compact string for QR encoding"""
        return f"SAHOOL|{self.batch_code}|{self.product_name_en}|{self.harvest_date}|{self.verification_url}"


# ─────────────────────────────────────────────────────────────────────────────
# Summary/Report Models - نماذج الملخصات/التقارير
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class BatchTraceReport:
    """
    Complete batch trace report - تقرير تتبع الدفعة الكامل

    Comprehensive report of a batch's journey through the supply chain.
    تقرير شامل لرحلة الدفعة عبر سلسلة التوريد.
    """

    batch: ProduceBatch
    producer: Producer | None = None
    events: list[SupplyChainEvent] = field(default_factory=list)
    certifications: list[Certification] = field(default_factory=list)

    # Summary stats
    total_journey_hours: float = 0.0
    total_distance_km: float = 0.0
    number_of_handlers: int = 0

    # Temperature tracking
    min_temperature_c: float | None = None
    max_temperature_c: float | None = None
    temperature_excursions: int = 0  # Number of times out of spec

    # Quality
    quality_checks_passed: int = 0
    quality_checks_failed: int = 0

    # Compliance
    all_certifications_valid: bool = True
    compliance_issues: list[str] = field(default_factory=list)

    # Generated
    generated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    generated_by: str = ""
