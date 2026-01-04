"""
GlobalGAP Field Operations Integration
تكامل عمليات الحقل مع GlobalGAP

Integrates field-ops service with GlobalGAP traceability and harvest tracking requirements.
Generates traceability records, tracks harvest batches, and maps activities to compliance requirements.

يربط خدمة عمليات الحقل مع متطلبات التتبع وتتبع الحصاد في GlobalGAP.
ينشئ سجلات التتبع، ويتتبع دفعات الحصاد، ويربط الأنشطة بمتطلبات الامتثال.

Usage:
    from shared.globalgap.integrations.field_ops_integration import (
        FieldOpsIntegration,
        TraceabilityRecord,
        HarvestBatch
    )

    integration = FieldOpsIntegration()
    await integration.connect()

    # Create traceability record
    record = await integration.create_traceability_record(
        farm_id=uuid4(),
        field_id=uuid4(),
        batch_number="BATCH-2024-001",
        harvest_date=date.today(),
        product_name_en="Tomato",
        quantity_kg=1000.0
    )

    # Track harvest batch
    batch = await integration.track_harvest_batch(
        farm_id=uuid4(),
        field_id=uuid4(),
        batch_number="BATCH-2024-001",
        harvest_date=date.today()
    )
"""

from datetime import date, datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from shared.events.publisher import EventPublisher

from .events import (
    GlobalGAPSubjects,
    TraceabilityRecordCreatedEvent,
)

# ─────────────────────────────────────────────────────────────────────────────
# Enums and Constants
# ─────────────────────────────────────────────────────────────────────────────


class ActivityType(str, Enum):
    """
    Field operation activity types
    أنواع أنشطة عمليات الحقل
    """

    PLANTING = "PLANTING"  # الزراعة
    IRRIGATION = "IRRIGATION"  # الري
    FERTILIZATION = "FERTILIZATION"  # التسميد
    PEST_CONTROL = "PEST_CONTROL"  # مكافحة الآفات
    WEEDING = "WEEDING"  # إزالة الأعشاب
    PRUNING = "PRUNING"  # التقليم
    THINNING = "THINNING"  # الترقيق
    HARVEST = "HARVEST"  # الحصاد
    POST_HARVEST = "POST_HARVEST"  # ما بعد الحصاد
    SOIL_PREPARATION = "SOIL_PREPARATION"  # إعداد التربة
    MONITORING = "MONITORING"  # المراقبة


class HarvestMethod(str, Enum):
    """
    Harvest methods
    طرق الحصاد
    """

    MANUAL = "MANUAL"  # يدوي
    MECHANICAL = "MECHANICAL"  # ميكانيكي
    SEMI_MECHANICAL = "SEMI_MECHANICAL"  # شبه ميكانيكي


class PackagingType(str, Enum):
    """
    Packaging types
    أنواع التعبئة
    """

    BULK = "BULK"  # سائب
    CRATE = "CRATE"  # صندوق
    BOX = "BOX"  # علبة
    BAG = "BAG"  # كيس
    PALLET = "PALLET"  # منصة نقالة
    CONTAINER = "CONTAINER"  # حاوية


# ─────────────────────────────────────────────────────────────────────────────
# Data Models
# ─────────────────────────────────────────────────────────────────────────────


class FieldActivity(BaseModel):
    """
    Field activity record for compliance tracking
    سجل نشاط الحقل لتتبع الامتثال
    """

    id: str = Field(default_factory=lambda: str(uuid4()), description="Activity ID")
    farm_id: UUID = Field(..., description="Farm ID")
    field_id: UUID | None = Field(None, description="Field ID")
    tenant_id: UUID = Field(..., description="Tenant ID")

    # Activity details
    activity_type: ActivityType = Field(..., description="Activity type")
    activity_date: date = Field(..., description="Activity date")
    activity_description_en: str = Field(
        ..., description="Activity description (English)"
    )
    activity_description_ar: str | None = Field(
        None, description="Activity description (Arabic)"
    )

    # Worker information
    worker_name: str | None = Field(None, description="Worker/operator name")
    worker_id: str | None = Field(None, description="Worker ID number")
    workers_count: int | None = Field(None, ge=1, description="Number of workers")

    # Time tracking
    start_time: datetime | None = Field(None, description="Activity start time")
    end_time: datetime | None = Field(None, description="Activity end time")
    duration_hours: float | None = Field(
        None, ge=0, description="Activity duration in hours"
    )

    # Area covered
    area_covered_ha: float | None = Field(
        None, ge=0, description="Area covered in hectares"
    )

    # Equipment used
    equipment_used: list[str] | None = Field(
        default_factory=list, description="Equipment used"
    )

    # Inputs used (fertilizers, pesticides, etc.)
    inputs_used: list[dict[str, Any]] | None = Field(
        default_factory=list, description="Inputs used (product name, quantity, etc.)"
    )

    # Weather conditions
    weather_conditions: str | None = Field(None, description="Weather conditions")
    temperature_celsius: float | None = Field(
        None, description="Temperature in Celsius"
    )

    # GlobalGAP compliance mapping
    related_control_points: list[str] = Field(
        default_factory=list,
        description="Related GlobalGAP control points (e.g., ['AF.1.1.1', 'AF.2.3.4'])",
    )

    # Evidence
    photos: list[str] = Field(default_factory=list, description="Photo URLs")
    documents: list[str] = Field(default_factory=list, description="Document URLs")

    # Metadata
    recorded_by: UUID | None = Field(None, description="User who recorded")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }


class HarvestBatch(BaseModel):
    """
    Harvest batch tracking record
    سجل تتبع دفعة الحصاد
    """

    id: str = Field(default_factory=lambda: str(uuid4()), description="Batch ID")
    batch_number: str = Field(..., description="Batch/lot number")

    farm_id: UUID = Field(..., description="Farm ID")
    field_id: UUID | None = Field(None, description="Field ID")
    tenant_id: UUID = Field(..., description="Tenant ID")

    # Product information
    product_name_en: str = Field(..., description="Product name (English)")
    product_name_ar: str | None = Field(None, description="Product name (Arabic)")
    product_variety: str | None = Field(None, description="Product variety")
    crop_type: str = Field(..., description="Crop type")

    # Harvest details
    harvest_date: date = Field(..., description="Harvest date")
    harvest_method: HarvestMethod = Field(..., description="Harvest method")

    # Quantities
    quantity_kg: float = Field(..., ge=0, description="Quantity in kilograms")
    quantity_units: int | None = Field(
        None, ge=0, description="Quantity in units (boxes, crates, etc.)"
    )
    packaging_type: PackagingType | None = Field(None, description="Packaging type")

    # Quality
    quality_grade: str | None = Field(
        None, description="Quality grade (A, B, C, etc.)"
    )
    quality_notes_en: str | None = Field(None, description="Quality notes (English)")
    quality_notes_ar: str | None = Field(None, description="Quality notes (Arabic)")

    # Traceability
    ggn: str | None = Field(None, description="GlobalGAP Number")
    planting_date: date | None = Field(None, description="Planting date")
    days_to_harvest: int | None = Field(
        None, ge=0, description="Days from planting to harvest"
    )

    # Growing period activities (counts)
    irrigation_records_count: int = Field(
        default=0, ge=0, description="Number of irrigation records"
    )
    fertilizer_records_count: int = Field(
        default=0, ge=0, description="Number of fertilizer applications"
    )
    pest_control_records_count: int = Field(
        default=0, ge=0, description="Number of pest control activities"
    )
    other_activities_count: int = Field(
        default=0, ge=0, description="Number of other activities"
    )

    # Withdrawal periods compliance
    last_pesticide_application_date: date | None = Field(
        None, description="Last pesticide application date"
    )
    withdrawal_period_days: int | None = Field(
        None, ge=0, description="Required withdrawal period"
    )
    days_since_last_pesticide: int | None = Field(
        None, description="Days since last pesticide"
    )
    withdrawal_period_respected: bool = Field(
        default=True, description="Withdrawal period respected"
    )

    # Storage and handling
    storage_location: str | None = Field(None, description="Storage location")
    storage_temperature_celsius: float | None = Field(
        None, description="Storage temperature"
    )
    cold_chain_maintained: bool = Field(
        default=True, description="Cold chain maintained (if required)"
    )

    # Destination
    destination: str | None = Field(
        None, description="Destination (customer, market, etc.)"
    )
    dispatch_date: date | None = Field(None, description="Dispatch date")

    # Metadata
    harvested_by: str | None = Field(None, description="Person/crew who harvested")
    recorded_by: UUID | None = Field(None, description="User who recorded")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }


class TraceabilityRecord(BaseModel):
    """
    Complete traceability record from farm to fork
    سجل تتبع كامل من المزرعة إلى المائدة
    """

    record_id: str = Field(
        default_factory=lambda: str(uuid4()), description="Traceability record ID"
    )
    batch_id: str = Field(..., description="Related harvest batch ID")
    batch_number: str = Field(..., description="Batch/lot number")

    farm_id: UUID = Field(..., description="Farm ID")
    field_id: UUID | None = Field(None, description="Field ID")
    tenant_id: UUID = Field(..., description="Tenant ID")

    # Product identification
    product_name_en: str = Field(..., description="Product name (English)")
    product_name_ar: str | None = Field(None, description="Product name (Arabic)")
    product_variety: str | None = Field(None, description="Product variety")

    # Farm information
    ggn: str = Field(..., description="GlobalGAP Number")
    farm_name_en: str | None = Field(None, description="Farm name (English)")
    farm_name_ar: str | None = Field(None, description="Farm name (Arabic)")

    # Growing period
    planting_date: date = Field(..., description="Planting date")
    harvest_date: date = Field(..., description="Harvest date")
    growing_days: int = Field(..., ge=0, description="Growing period in days")

    # Quantity
    quantity_kg: float = Field(..., ge=0, description="Quantity in kg")

    # Activity traceability
    linked_activities: list[str] = Field(
        default_factory=list, description="Linked activity IDs"
    )

    irrigation_records_linked: int = Field(
        default=0, ge=0, description="Linked irrigation records"
    )
    fertilizer_records_linked: int = Field(
        default=0, ge=0, description="Linked fertilizer records"
    )
    pest_control_records_linked: int = Field(
        default=0, ge=0, description="Linked pest control records"
    )
    harvest_records_linked: int = Field(
        default=0, ge=0, description="Linked harvest records"
    )

    # Input traceability
    fertilizers_used: list[dict[str, Any]] = Field(
        default_factory=list,
        description="List of fertilizers used with dates and quantities",
    )
    pesticides_used: list[dict[str, Any]] = Field(
        default_factory=list,
        description="List of pesticides used with dates and quantities",
    )

    # Compliance indicators
    full_traceability: bool = Field(
        ..., description="Complete farm-to-fork traceability"
    )
    all_inputs_documented: bool = Field(..., description="All inputs documented")
    withdrawal_periods_respected: bool = Field(
        default=True, description="All withdrawal periods respected"
    )
    globalgap_compliant: bool = Field(
        ..., description="Meets GlobalGAP traceability requirements"
    )

    # Issues
    traceability_gaps_en: list[str] = Field(
        default_factory=list, description="Identified traceability gaps (English)"
    )
    traceability_gaps_ar: list[str] = Field(
        default_factory=list, description="Identified traceability gaps (Arabic)"
    )

    # QR code / barcode
    qr_code_url: str | None = Field(None, description="QR code image URL")
    barcode: str | None = Field(None, description="Barcode/UPC")

    # Record metadata
    created_by: UUID | None = Field(None, description="User who created record")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }


class ActivityComplianceMapping(BaseModel):
    """
    Mapping of field activities to GlobalGAP control points
    ربط أنشطة الحقل بنقاط التحكم في GlobalGAP
    """

    activity_type: ActivityType = Field(..., description="Activity type")
    activity_name_en: str = Field(..., description="Activity name (English)")
    activity_name_ar: str = Field(..., description="Activity name (Arabic)")

    # Related GlobalGAP control points
    related_control_points: list[str] = Field(
        default_factory=list, description="Related control point IDs"
    )

    # Required documentation
    required_records_en: list[str] = Field(
        default_factory=list, description="Required records (English)"
    )
    required_records_ar: list[str] = Field(
        default_factory=list, description="Required records (Arabic)"
    )

    # Evidence requirements
    photos_required: bool = Field(default=False, description="Photos required")
    documents_required: bool = Field(default=False, description="Documents required")
    worker_training_required: bool = Field(
        default=False, description="Worker training required"
    )

    class Config:
        use_enum_values = True


# ─────────────────────────────────────────────────────────────────────────────
# Integration Class
# ─────────────────────────────────────────────────────────────────────────────


class FieldOpsIntegration:
    """
    Integration between field-ops service and GlobalGAP traceability compliance
    التكامل بين خدمة عمليات الحقل والامتثال لتتبع GlobalGAP

    Responsibilities:
    - Generate traceability records for harvest batches
    - Track all field activities for compliance
    - Map activities to GlobalGAP control points
    - Ensure complete farm-to-fork traceability
    - Monitor withdrawal period compliance
    - Emit NATS events for traceability
    """

    def __init__(self, publisher: EventPublisher | None = None):
        """
        Initialize field operations integration

        Args:
            publisher: Event publisher instance (will create if not provided)
        """
        self.publisher = publisher
        self._connected = False

        # Activity to control point mappings
        self._activity_mappings = self._initialize_activity_mappings()

    def _initialize_activity_mappings(
        self,
    ) -> dict[ActivityType, ActivityComplianceMapping]:
        """Initialize activity to compliance mappings"""
        return {
            ActivityType.PLANTING: ActivityComplianceMapping(
                activity_type=ActivityType.PLANTING,
                activity_name_en="Planting",
                activity_name_ar="الزراعة",
                related_control_points=["AF.1.1.1", "AF.1.2.1"],
                required_records_en=[
                    "Planting date",
                    "Seed variety",
                    "Planting density",
                ],
                required_records_ar=["تاريخ الزراعة", "صنف البذور", "كثافة الزراعة"],
                documents_required=True,
            ),
            ActivityType.IRRIGATION: ActivityComplianceMapping(
                activity_type=ActivityType.IRRIGATION,
                activity_name_en="Irrigation",
                activity_name_ar="الري",
                related_control_points=["AF.3.1.1", "AF.3.2.1", "ENV.3.1.1"],
                required_records_en=[
                    "Water volume",
                    "Water source",
                    "Irrigation method",
                ],
                required_records_ar=["حجم المياه", "مصدر المياه", "طريقة الري"],
                documents_required=True,
            ),
            ActivityType.FERTILIZATION: ActivityComplianceMapping(
                activity_type=ActivityType.FERTILIZATION,
                activity_name_en="Fertilization",
                activity_name_ar="التسميد",
                related_control_points=["AF.4.1.1", "AF.4.2.1", "AF.4.3.1"],
                required_records_en=["Fertilizer type", "Quantity", "Application date"],
                required_records_ar=["نوع السماد", "الكمية", "تاريخ التطبيق"],
                documents_required=True,
            ),
            ActivityType.PEST_CONTROL: ActivityComplianceMapping(
                activity_type=ActivityType.PEST_CONTROL,
                activity_name_en="Pest Control",
                activity_name_ar="مكافحة الآفات",
                related_control_points=["AF.5.1.1", "AF.5.2.1", "AF.5.3.1"],
                required_records_en=[
                    "Pest identification",
                    "Treatment method",
                    "PPP details",
                ],
                required_records_ar=["تحديد الآفة", "طريقة العلاج", "تفاصيل PPP"],
                documents_required=True,
                worker_training_required=True,
            ),
            ActivityType.HARVEST: ActivityComplianceMapping(
                activity_type=ActivityType.HARVEST,
                activity_name_en="Harvest",
                activity_name_ar="الحصاد",
                related_control_points=["AF.9.1.1", "AF.9.2.1", "FV.5.1.1"],
                required_records_en=["Harvest date", "Quantity", "Quality grade"],
                required_records_ar=["تاريخ الحصاد", "الكمية", "درجة الجودة"],
                documents_required=True,
            ),
        }

    async def connect(self) -> bool:
        """
        Connect to NATS for event publishing
        الاتصال بـ NATS لنشر الأحداث

        Returns:
            True if connected successfully
        """
        if self.publisher is None:
            self.publisher = EventPublisher(
                service_name="globalgap-field-ops-integration"
            )

        if not self.publisher.is_connected:
            self._connected = await self.publisher.connect()
        else:
            self._connected = True

        return self._connected

    async def close(self):
        """Close NATS connection"""
        if self.publisher:
            await self.publisher.close()
        self._connected = False

    # ─────────────────────────────────────────────────────────────────────────
    # Field Activity Tracking
    # ─────────────────────────────────────────────────────────────────────────

    async def record_field_activity(
        self,
        farm_id: UUID,
        tenant_id: UUID,
        activity_type: ActivityType,
        activity_description_en: str,
        activity_date: date | None = None,
        field_id: UUID | None = None,
        activity_description_ar: str | None = None,
        worker_name: str | None = None,
        area_covered_ha: float | None = None,
        inputs_used: list[dict[str, Any]] | None = None,
        recorded_by: UUID | None = None,
    ) -> FieldActivity:
        """
        Record field activity for compliance tracking
        تسجيل نشاط الحقل لتتبع الامتثال

        Args:
            farm_id: Farm ID
            tenant_id: Tenant ID
            activity_type: Activity type
            activity_description_en: Activity description (English)
            activity_date: Activity date (defaults to today)
            field_id: Field ID (optional)
            activity_description_ar: Activity description (Arabic)
            worker_name: Worker/operator name
            area_covered_ha: Area covered in hectares
            inputs_used: Inputs used
            recorded_by: User ID who recorded

        Returns:
            FieldActivity instance
        """
        # Get compliance mapping for this activity
        mapping = self._activity_mappings.get(activity_type)
        related_control_points = mapping.related_control_points if mapping else []

        activity = FieldActivity(
            farm_id=farm_id,
            tenant_id=tenant_id,
            field_id=field_id,
            activity_type=activity_type,
            activity_date=activity_date or date.today(),
            activity_description_en=activity_description_en,
            activity_description_ar=activity_description_ar,
            worker_name=worker_name,
            area_covered_ha=area_covered_ha,
            inputs_used=inputs_used or [],
            related_control_points=related_control_points,
            recorded_by=recorded_by,
        )

        return activity

    # ─────────────────────────────────────────────────────────────────────────
    # Harvest Batch Tracking
    # ─────────────────────────────────────────────────────────────────────────

    async def track_harvest_batch(
        self,
        farm_id: UUID,
        tenant_id: UUID,
        batch_number: str,
        product_name_en: str,
        crop_type: str,
        harvest_date: date,
        quantity_kg: float,
        harvest_method: HarvestMethod,
        field_id: UUID | None = None,
        product_name_ar: str | None = None,
        product_variety: str | None = None,
        ggn: str | None = None,
        planting_date: date | None = None,
        last_pesticide_application_date: date | None = None,
        withdrawal_period_days: int | None = None,
        recorded_by: UUID | None = None,
    ) -> HarvestBatch:
        """
        Track harvest batch for traceability
        تتبع دفعة الحصاد للتتبع

        Args:
            farm_id: Farm ID
            tenant_id: Tenant ID
            batch_number: Batch/lot number
            product_name_en: Product name (English)
            crop_type: Crop type
            harvest_date: Harvest date
            quantity_kg: Quantity in kg
            harvest_method: Harvest method
            field_id: Field ID (optional)
            product_name_ar: Product name (Arabic)
            product_variety: Product variety
            ggn: GlobalGAP Number
            planting_date: Planting date
            last_pesticide_application_date: Last pesticide application date
            withdrawal_period_days: Required withdrawal period
            recorded_by: User ID who recorded

        Returns:
            HarvestBatch instance
        """
        # Calculate days to harvest
        days_to_harvest = None
        if planting_date:
            days_to_harvest = (harvest_date - planting_date).days

        # Check withdrawal period compliance
        days_since_pesticide = None
        withdrawal_period_respected = True

        if last_pesticide_application_date and withdrawal_period_days is not None:
            days_since_pesticide = (harvest_date - last_pesticide_application_date).days
            withdrawal_period_respected = days_since_pesticide >= withdrawal_period_days

        batch = HarvestBatch(
            batch_number=batch_number,
            farm_id=farm_id,
            tenant_id=tenant_id,
            field_id=field_id,
            product_name_en=product_name_en,
            product_name_ar=product_name_ar,
            product_variety=product_variety,
            crop_type=crop_type,
            harvest_date=harvest_date,
            harvest_method=harvest_method,
            quantity_kg=quantity_kg,
            ggn=ggn,
            planting_date=planting_date,
            days_to_harvest=days_to_harvest,
            last_pesticide_application_date=last_pesticide_application_date,
            withdrawal_period_days=withdrawal_period_days,
            days_since_last_pesticide=days_since_pesticide,
            withdrawal_period_respected=withdrawal_period_respected,
            recorded_by=recorded_by,
        )

        return batch

    # ─────────────────────────────────────────────────────────────────────────
    # Traceability Record Generation
    # ─────────────────────────────────────────────────────────────────────────

    async def create_traceability_record(
        self,
        farm_id: UUID,
        tenant_id: UUID,
        batch_id: str,
        batch_number: str,
        product_name_en: str,
        ggn: str,
        planting_date: date,
        harvest_date: date,
        quantity_kg: float,
        field_id: UUID | None = None,
        product_name_ar: str | None = None,
        product_variety: str | None = None,
        farm_name_en: str | None = None,
        farm_name_ar: str | None = None,
        irrigation_records_count: int = 0,
        fertilizer_records_count: int = 0,
        pest_control_records_count: int = 0,
        harvest_records_count: int = 0,
        fertilizers_used: list[dict[str, Any]] | None = None,
        pesticides_used: list[dict[str, Any]] | None = None,
        created_by: UUID | None = None,
    ) -> TraceabilityRecord:
        """
        Create complete traceability record for harvest batch
        إنشاء سجل تتبع كامل لدفعة الحصاد

        Args:
            farm_id: Farm ID
            tenant_id: Tenant ID
            batch_id: Harvest batch ID
            batch_number: Batch/lot number
            product_name_en: Product name (English)
            ggn: GlobalGAP Number
            planting_date: Planting date
            harvest_date: Harvest date
            quantity_kg: Quantity in kg
            field_id: Field ID (optional)
            product_name_ar: Product name (Arabic)
            product_variety: Product variety
            farm_name_en: Farm name (English)
            farm_name_ar: Farm name (Arabic)
            irrigation_records_count: Number of irrigation records
            fertilizer_records_count: Number of fertilizer records
            pest_control_records_count: Number of pest control records
            harvest_records_count: Number of harvest records
            fertilizers_used: List of fertilizers used
            pesticides_used: List of pesticides used
            created_by: User ID who created record

        Returns:
            TraceabilityRecord instance
        """
        # Calculate growing period
        growing_days = (harvest_date - planting_date).days

        # Assess traceability completeness
        full_traceability = (
            irrigation_records_count > 0
            and fertilizer_records_count > 0
            and harvest_records_count > 0
        )

        all_inputs_documented = (
            fertilizers_used is not None and len(fertilizers_used) > 0
        )

        # Check for traceability gaps
        gaps_en = []
        gaps_ar = []

        if irrigation_records_count == 0:
            gaps_en.append("No irrigation records linked")
            gaps_ar.append("لا توجد سجلات ري مرتبطة")

        if fertilizer_records_count == 0:
            gaps_en.append("No fertilizer records linked")
            gaps_ar.append("لا توجد سجلات أسمدة مرتبطة")

        if pest_control_records_count == 0:
            gaps_en.append("No pest control records linked")
            gaps_ar.append("لا توجد سجلات مكافحة آفات مرتبطة")

        if not fertilizers_used or len(fertilizers_used) == 0:
            gaps_en.append("Fertilizer inputs not documented")
            gaps_ar.append("مدخلات الأسمدة غير موثقة")

        # GlobalGAP compliance
        globalgap_compliant = full_traceability and all_inputs_documented

        record = TraceabilityRecord(
            batch_id=batch_id,
            batch_number=batch_number,
            farm_id=farm_id,
            tenant_id=tenant_id,
            field_id=field_id,
            product_name_en=product_name_en,
            product_name_ar=product_name_ar,
            product_variety=product_variety,
            ggn=ggn,
            farm_name_en=farm_name_en,
            farm_name_ar=farm_name_ar,
            planting_date=planting_date,
            harvest_date=harvest_date,
            growing_days=growing_days,
            quantity_kg=quantity_kg,
            irrigation_records_linked=irrigation_records_count,
            fertilizer_records_linked=fertilizer_records_count,
            pest_control_records_linked=pest_control_records_count,
            harvest_records_linked=harvest_records_count,
            fertilizers_used=fertilizers_used or [],
            pesticides_used=pesticides_used or [],
            full_traceability=full_traceability,
            all_inputs_documented=all_inputs_documented,
            globalgap_compliant=globalgap_compliant,
            traceability_gaps_en=gaps_en,
            traceability_gaps_ar=gaps_ar,
            created_by=created_by,
        )

        # Emit NATS event
        if self._connected:
            event = TraceabilityRecordCreatedEvent(
                farm_id=farm_id,
                tenant_id=tenant_id,
                field_id=field_id,
                batch_number=batch_number,
                harvest_date=harvest_date,
                product_name_en=product_name_en,
                product_name_ar=product_name_ar,
                product_variety=product_variety,
                quantity_kg=quantity_kg,
                ggn=ggn,
                planting_date=planting_date,
                irrigation_records_linked=irrigation_records_count,
                fertilizer_records_linked=fertilizer_records_count,
                pest_control_records_linked=pest_control_records_count,
                harvest_records_linked=harvest_records_count,
                full_traceability=full_traceability,
                withdrawal_period_respected=True,  # Would come from harvest batch
                created_by=created_by,
            )

            await self.publisher.publish_event(
                GlobalGAPSubjects.TRACEABILITY_RECORD_CREATED, event
            )

        return record

    # ─────────────────────────────────────────────────────────────────────────
    # Activity Compliance Mapping
    # ─────────────────────────────────────────────────────────────────────────

    def get_activity_compliance_mapping(
        self, activity_type: ActivityType
    ) -> ActivityComplianceMapping | None:
        """
        Get compliance mapping for an activity type
        الحصول على ربط الامتثال لنوع النشاط

        Args:
            activity_type: Activity type

        Returns:
            ActivityComplianceMapping or None
        """
        return self._activity_mappings.get(activity_type)

    def get_all_activity_mappings(
        self,
    ) -> dict[ActivityType, ActivityComplianceMapping]:
        """
        Get all activity to compliance mappings
        الحصول على جميع روابط الأنشطة بالامتثال

        Returns:
            Dictionary of activity mappings
        """
        return self._activity_mappings

    # ─────────────────────────────────────────────────────────────────────────
    # Context Manager Support
    # ─────────────────────────────────────────────────────────────────────────

    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()


# ─────────────────────────────────────────────────────────────────────────────
# Exports
# ─────────────────────────────────────────────────────────────────────────────

__all__ = [
    # Enums
    "ActivityType",
    "HarvestMethod",
    "PackagingType",
    # Models
    "FieldActivity",
    "HarvestBatch",
    "TraceabilityRecord",
    "ActivityComplianceMapping",
    # Integration
    "FieldOpsIntegration",
]
