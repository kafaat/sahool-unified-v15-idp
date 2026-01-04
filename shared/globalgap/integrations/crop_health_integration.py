"""
GlobalGAP Crop Health Integration
تكامل صحة المحاصيل مع GlobalGAP

Integrates crop-health-ai service with GlobalGAP IPM (Integrated Pest Management) requirements.
Maps pest and disease detection to IPM documentation and tracks chemical PPP usage.

يربط خدمة الذكاء الاصطناعي لصحة المحاصيل مع متطلبات الإدارة المتكاملة للآفات.
يربط اكتشاف الآفات والأمراض بتوثيق IPM ويتتبع استخدام المبيدات الكيميائية.

Usage:
    from shared.globalgap.integrations.crop_health_integration import (
        CropHealthIntegration,
        IPMReport,
        PPPApplicationRecord
    )

    integration = CropHealthIntegration()
    await integration.connect()

    # Record pest detection for IPM
    await integration.record_pest_detection(
        farm_id=uuid4(),
        field_id=uuid4(),
        pest_name_en="Aphid",
        pest_name_ar="المن",
        severity="medium"
    )

    # Record chemical treatment
    await integration.record_ppp_application(
        farm_id=uuid4(),
        field_id=uuid4(),
        ppp_name="Imidacloprid",
        active_ingredient="Imidacloprid",
        dosage_per_ha=0.5
    )

    # Generate IPM report
    report = await integration.generate_ipm_report(
        farm_id=uuid4(),
        start_date=date(2024, 1, 1),
        end_date=date(2024, 12, 31)
    )
"""

from datetime import date, datetime, timedelta
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from shared.events.publisher import EventPublisher

from .events import (
    GlobalGAPSubjects,
    IPMActivityRecordedEvent,
)

# ─────────────────────────────────────────────────────────────────────────────
# Enums and Constants
# ─────────────────────────────────────────────────────────────────────────────


class PestCategory(str, Enum):
    """
    Pest/disease categories
    فئات الآفات والأمراض
    """

    INSECT = "INSECT"  # حشرة
    FUNGAL = "FUNGAL"  # فطري
    BACTERIAL = "BACTERIAL"  # بكتيري
    VIRAL = "VIRAL"  # فيروسي
    WEED = "WEED"  # حشائش
    NEMATODE = "NEMATODE"  # نيماتودا
    MITE = "MITE"  # عث
    RODENT = "RODENT"  # قوارض


class IPMActivityType(str, Enum):
    """
    IPM activity types
    أنواع أنشطة الإدارة المتكاملة للآفات
    """

    MONITORING = "MONITORING"  # المراقبة
    PREVENTION = "PREVENTION"  # الوقاية
    CONTROL = "CONTROL"  # السيطرة
    TREATMENT = "TREATMENT"  # العلاج
    BIOLOGICAL_CONTROL = "BIOLOGICAL_CONTROL"  # المكافحة الحيوية
    CULTURAL_CONTROL = "CULTURAL_CONTROL"  # المكافحة الثقافية
    MECHANICAL_CONTROL = "MECHANICAL_CONTROL"  # المكافحة الميكانيكية
    CHEMICAL_CONTROL = "CHEMICAL_CONTROL"  # المكافحة الكيميائية


class DetectionMethod(str, Enum):
    """
    Detection methods
    طرق الكشف
    """

    AI_DETECTION = "AI_DETECTION"  # الكشف بالذكاء الاصطناعي
    MANUAL_INSPECTION = "MANUAL_INSPECTION"  # الفحص اليدوي
    TRAP_MONITORING = "TRAP_MONITORING"  # مراقبة المصائد
    SENSOR_ALERT = "SENSOR_ALERT"  # تنبيه المستشعر
    SATELLITE_IMAGERY = "SATELLITE_IMAGERY"  # صور الأقمار الصناعية
    SCOUTING = "SCOUTING"  # المسح


class SeverityLevel(str, Enum):
    """
    Severity levels
    مستويات الخطورة
    """

    LOW = "low"  # منخفض
    MEDIUM = "medium"  # متوسط
    HIGH = "high"  # عالي
    CRITICAL = "critical"  # حرج


class PPPType(str, Enum):
    """
    Plant Protection Product types
    أنواع منتجات وقاية النباتات
    """

    INSECTICIDE = "INSECTICIDE"  # مبيد حشري
    FUNGICIDE = "FUNGICIDE"  # مبيد فطري
    HERBICIDE = "HERBICIDE"  # مبيد أعشاب
    BACTERICIDE = "BACTERICIDE"  # مبيد بكتيري
    NEMATICIDE = "NEMATICIDE"  # مبيد نيماتودا
    ACARICIDE = "ACARICIDE"  # مبيد عث
    RODENTICIDE = "RODENTICIDE"  # مبيد قوارض
    BIOCONTROL_AGENT = "BIOCONTROL_AGENT"  # عامل مكافحة حيوية


# ─────────────────────────────────────────────────────────────────────────────
# Data Models
# ─────────────────────────────────────────────────────────────────────────────


class PestDetectionRecord(BaseModel):
    """
    Pest or disease detection record
    سجل اكتشاف آفة أو مرض
    """

    id: str = Field(default_factory=lambda: str(uuid4()), description="Record ID")
    farm_id: UUID = Field(..., description="Farm ID")
    field_id: UUID | None = Field(None, description="Field ID")
    tenant_id: UUID = Field(..., description="Tenant ID")

    # Detection details
    detection_date: date = Field(..., description="Detection date")
    detection_method: DetectionMethod = Field(..., description="Detection method")

    # Pest/Disease information
    pest_or_disease_name_en: str = Field(..., description="Pest/disease name (English)")
    pest_or_disease_name_ar: str | None = Field(
        None, description="Pest/disease name (Arabic)"
    )
    pest_category: PestCategory = Field(..., description="Pest/disease category")

    scientific_name: str | None = Field(None, description="Scientific name")

    # Severity
    severity_level: SeverityLevel = Field(..., description="Severity level")
    confidence_score: float | None = Field(
        None, ge=0, le=1, description="AI detection confidence"
    )

    # Affected area
    affected_area_ha: float | None = Field(
        None, ge=0, description="Affected area in hectares"
    )
    affected_area_percentage: float | None = Field(
        None, ge=0, le=100, description="% of field affected"
    )

    # Symptoms and evidence
    symptoms_observed: list[str] = Field(
        default_factory=list, description="Observed symptoms"
    )
    image_urls: list[str] = Field(
        default_factory=list, description="Detection image URLs"
    )

    # Monitoring
    monitoring_frequency_days: int | None = Field(
        None, ge=1, description="Monitoring frequency"
    )

    # Metadata
    detected_by: UUID | None = Field(None, description="User who detected")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }


class PPPApplicationRecord(BaseModel):
    """
    Plant Protection Product (PPP) application record
    سجل تطبيق منتج وقاية النباتات
    """

    id: str = Field(default_factory=lambda: str(uuid4()), description="Record ID")
    farm_id: UUID = Field(..., description="Farm ID")
    field_id: UUID | None = Field(None, description="Field ID")
    tenant_id: UUID = Field(..., description="Tenant ID")

    # Application details
    application_date: date = Field(..., description="Application date")
    pest_detection_id: str | None = Field(
        None, description="Related pest detection record ID"
    )

    # Product information
    ppp_name: str = Field(..., description="PPP product name")
    ppp_type: PPPType = Field(..., description="PPP type")
    active_ingredient: str = Field(..., description="Active ingredient")
    active_ingredient_concentration: str | None = Field(
        None, description="Concentration (e.g., 25% EC)"
    )

    # Dosage
    dosage_per_ha: float = Field(..., ge=0, description="Dosage per hectare")
    dosage_unit: str = Field(..., description="Dosage unit (L, kg, g)")
    total_quantity_applied: float | None = Field(
        None, ge=0, description="Total quantity applied"
    )
    area_treated_ha: float | None = Field(
        None, ge=0, description="Area treated in hectares"
    )

    # Application method
    application_method: str = Field(
        ..., description="Application method (spray, granular, etc.)"
    )
    application_equipment: str | None = Field(None, description="Equipment used")

    # Compliance
    ppp_globalgap_approved: bool = Field(
        ..., description="Product is GlobalGAP approved"
    )
    ppp_registration_number: str | None = Field(
        None, description="Product registration number"
    )

    mrl_compliant: bool = Field(
        default=True, description="MRL (Maximum Residue Level) compliant"
    )
    withdrawal_period_days: int | None = Field(
        None, ge=0, description="Withdrawal period in days"
    )
    safe_harvest_date: date | None = Field(
        None, description="Safe harvest date (after withdrawal)"
    )

    # Justification (IPM requirement)
    pest_or_disease_name: str = Field(..., description="Target pest/disease")
    justification_en: str = Field(
        ..., description="Application justification (English)"
    )
    justification_ar: str | None = Field(
        None, description="Application justification (Arabic)"
    )

    threshold_exceeded: bool = Field(..., description="Economic threshold exceeded")
    alternative_methods_tried: bool = Field(
        default=False, description="Non-chemical methods tried first"
    )

    # Weather conditions
    weather_conditions: str | None = Field(
        None, description="Weather conditions during application"
    )
    wind_speed_kmh: float | None = Field(
        None, ge=0, description="Wind speed during application"
    )

    # Operator
    operator_name: str | None = Field(None, description="Operator name")
    operator_certified: bool = Field(
        default=False, description="Operator certified for PPP application"
    )

    # Evidence
    application_record_url: str | None = Field(
        None, description="Application record document URL"
    )
    product_label_url: str | None = Field(None, description="Product label URL")

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


class IPMReport(BaseModel):
    """
    Integrated Pest Management (IPM) report for GlobalGAP audit
    تقرير الإدارة المتكاملة للآفات لتدقيق GlobalGAP
    """

    report_id: str = Field(
        default_factory=lambda: str(uuid4()), description="Report ID"
    )
    farm_id: UUID = Field(..., description="Farm ID")
    tenant_id: UUID = Field(..., description="Tenant ID")
    ggn: str | None = Field(None, description="GlobalGAP Number")

    # Reporting period
    report_start_date: date = Field(..., description="Report period start")
    report_end_date: date = Field(..., description="Report period end")

    # Detection summary
    total_detections: int = Field(
        ..., ge=0, description="Total pest/disease detections"
    )
    detections_by_category: dict[str, int] = Field(
        default_factory=dict,
        description="Detections by category (e.g., {'INSECT': 10, 'FUNGAL': 5})",
    )
    detections_by_severity: dict[str, int] = Field(
        default_factory=dict, description="Detections by severity level"
    )

    # Monitoring
    monitoring_frequency_avg_days: float | None = Field(
        None, description="Average monitoring frequency"
    )
    systematic_monitoring_in_place: bool = Field(
        ..., description="Systematic monitoring program in place"
    )

    # IPM activities
    total_ipm_activities: int = Field(..., ge=0, description="Total IPM activities")
    prevention_activities: int = Field(
        default=0, ge=0, description="Prevention activities"
    )
    monitoring_activities: int = Field(
        default=0, ge=0, description="Monitoring activities"
    )
    biological_control_activities: int = Field(
        default=0, ge=0, description="Biological control activities"
    )
    cultural_control_activities: int = Field(
        default=0, ge=0, description="Cultural control activities"
    )
    chemical_control_activities: int = Field(
        default=0, ge=0, description="Chemical control activities"
    )

    # PPP usage
    total_ppp_applications: int = Field(..., ge=0, description="Total PPP applications")
    ppp_applications_justified: int = Field(
        ..., ge=0, description="Justified PPP applications"
    )
    ppp_justification_rate: float = Field(
        ..., ge=0, le=100, description="PPP justification rate %"
    )

    approved_ppp_usage: int = Field(
        ..., ge=0, description="GlobalGAP approved PPP usage"
    )
    ppp_approval_rate: float = Field(
        ..., ge=0, le=100, description="PPP approval rate %"
    )

    mrl_compliant_applications: int = Field(
        ..., ge=0, description="MRL compliant applications"
    )
    mrl_compliance_rate: float = Field(
        ..., ge=0, le=100, description="MRL compliance rate %"
    )

    # Chemical usage breakdown
    total_active_ingredients_used: int = Field(
        ..., ge=0, description="Number of different active ingredients"
    )
    active_ingredients_list: list[str] = Field(
        default_factory=list, description="List of active ingredients"
    )

    # IPM principles compliance
    economic_thresholds_used: bool = Field(
        ..., description="Economic thresholds used for decisions"
    )
    preventive_measures_priority: bool = Field(
        ..., description="Preventive measures prioritized"
    )
    non_chemical_methods_first: bool = Field(
        ..., description="Non-chemical methods tried first"
    )
    chemical_last_resort: bool = Field(..., description="Chemicals used as last resort")

    # Overall compliance
    overall_ipm_compliance_score: float = Field(
        ..., ge=0, le=100, description="Overall IPM compliance %"
    )
    is_ipm_compliant: bool = Field(..., description="Meets GlobalGAP IPM requirements")

    # Issues and recommendations
    compliance_issues_en: list[str] = Field(
        default_factory=list, description="Compliance issues (English)"
    )
    compliance_issues_ar: list[str] = Field(
        default_factory=list, description="Compliance issues (Arabic)"
    )

    recommendations_en: list[str] = Field(
        default_factory=list, description="Recommendations (English)"
    )
    recommendations_ar: list[str] = Field(
        default_factory=list, description="Recommendations (Arabic)"
    )

    # Report metadata
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    generated_by: UUID | None = Field(None, description="User who generated report")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }


# ─────────────────────────────────────────────────────────────────────────────
# Integration Class
# ─────────────────────────────────────────────────────────────────────────────


class CropHealthIntegration:
    """
    Integration between crop-health-ai service and GlobalGAP IPM compliance
    التكامل بين خدمة الذكاء الاصطناعي لصحة المحاصيل والامتثال لـ IPM

    Responsibilities:
    - Map pest/disease detection to IPM documentation
    - Track chemical PPP (Plant Protection Product) usage
    - Generate IPM reports for audits
    - Monitor MRL (Maximum Residue Level) compliance
    - Emit NATS events for IPM activities
    """

    def __init__(self, publisher: EventPublisher | None = None):
        """
        Initialize crop health integration

        Args:
            publisher: Event publisher instance (will create if not provided)
        """
        self.publisher = publisher
        self._connected = False

    async def connect(self) -> bool:
        """
        Connect to NATS for event publishing
        الاتصال بـ NATS لنشر الأحداث

        Returns:
            True if connected successfully
        """
        if self.publisher is None:
            self.publisher = EventPublisher(
                service_name="globalgap-crop-health-integration"
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
    # Pest/Disease Detection
    # ─────────────────────────────────────────────────────────────────────────

    async def record_pest_detection(
        self,
        farm_id: UUID,
        tenant_id: UUID,
        pest_or_disease_name_en: str,
        pest_category: PestCategory,
        severity_level: SeverityLevel,
        detection_method: DetectionMethod,
        field_id: UUID | None = None,
        pest_or_disease_name_ar: str | None = None,
        detection_date: date | None = None,
        confidence_score: float | None = None,
        affected_area_ha: float | None = None,
        symptoms_observed: list[str] | None = None,
        image_urls: list[str] | None = None,
        detected_by: UUID | None = None,
    ) -> PestDetectionRecord:
        """
        Record pest or disease detection for IPM tracking
        تسجيل اكتشاف آفة أو مرض لتتبع IPM

        Args:
            farm_id: Farm ID
            tenant_id: Tenant ID
            pest_or_disease_name_en: Pest/disease name (English)
            pest_category: Pest/disease category
            severity_level: Severity level
            detection_method: Detection method used
            field_id: Field ID (optional)
            pest_or_disease_name_ar: Pest/disease name (Arabic)
            detection_date: Detection date (defaults to today)
            confidence_score: AI detection confidence
            affected_area_ha: Affected area in hectares
            symptoms_observed: List of observed symptoms
            image_urls: Detection image URLs
            detected_by: User ID who detected

        Returns:
            PestDetectionRecord instance
        """
        record = PestDetectionRecord(
            farm_id=farm_id,
            tenant_id=tenant_id,
            field_id=field_id,
            detection_date=detection_date or date.today(),
            detection_method=detection_method,
            pest_or_disease_name_en=pest_or_disease_name_en,
            pest_or_disease_name_ar=pest_or_disease_name_ar,
            pest_category=pest_category,
            severity_level=severity_level,
            confidence_score=confidence_score,
            affected_area_ha=affected_area_ha,
            symptoms_observed=symptoms_observed or [],
            image_urls=image_urls or [],
            detected_by=detected_by,
        )

        # Emit NATS event
        if self._connected:
            event = IPMActivityRecordedEvent(
                farm_id=farm_id,
                tenant_id=tenant_id,
                field_id=field_id,
                activity_date=record.detection_date,
                activity_type="MONITORING",
                pest_or_disease_name_en=pest_or_disease_name_en,
                pest_or_disease_name_ar=pest_or_disease_name_ar,
                pest_category=pest_category.value,
                detection_method=detection_method.value,
                severity_level=severity_level.value,
                treatment_applied=False,
                justification_en=f"Detected {pest_or_disease_name_en} via {detection_method.value}",
                justification_ar=pest_or_disease_name_ar,
                recorded_by=detected_by,
            )

            await self.publisher.publish_event(
                GlobalGAPSubjects.IPM_ACTIVITY_RECORDED, event
            )

        return record

    # ─────────────────────────────────────────────────────────────────────────
    # PPP Application
    # ─────────────────────────────────────────────────────────────────────────

    async def record_ppp_application(
        self,
        farm_id: UUID,
        tenant_id: UUID,
        ppp_name: str,
        ppp_type: PPPType,
        active_ingredient: str,
        dosage_per_ha: float,
        dosage_unit: str,
        application_method: str,
        pest_or_disease_name: str,
        justification_en: str,
        threshold_exceeded: bool,
        ppp_globalgap_approved: bool,
        field_id: UUID | None = None,
        application_date: date | None = None,
        pest_detection_id: str | None = None,
        justification_ar: str | None = None,
        area_treated_ha: float | None = None,
        withdrawal_period_days: int | None = None,
        alternative_methods_tried: bool = False,
        mrl_compliant: bool = True,
        operator_certified: bool = False,
        recorded_by: UUID | None = None,
    ) -> PPPApplicationRecord:
        """
        Record Plant Protection Product (PPP) application
        تسجيل تطبيق منتج وقاية النباتات

        Args:
            farm_id: Farm ID
            tenant_id: Tenant ID
            ppp_name: PPP product name
            ppp_type: PPP type
            active_ingredient: Active ingredient
            dosage_per_ha: Dosage per hectare
            dosage_unit: Dosage unit
            application_method: Application method
            pest_or_disease_name: Target pest/disease
            justification_en: Application justification (English)
            threshold_exceeded: Economic threshold exceeded
            ppp_globalgap_approved: Product is GlobalGAP approved
            field_id: Field ID (optional)
            application_date: Application date (defaults to today)
            pest_detection_id: Related pest detection record ID
            justification_ar: Application justification (Arabic)
            area_treated_ha: Area treated in hectares
            withdrawal_period_days: Withdrawal period in days
            alternative_methods_tried: Non-chemical methods tried first
            mrl_compliant: MRL compliant
            operator_certified: Operator certified
            recorded_by: User ID who recorded

        Returns:
            PPPApplicationRecord instance
        """
        app_date = application_date or date.today()

        # Calculate safe harvest date
        safe_harvest_date = None
        if withdrawal_period_days is not None:
            safe_harvest_date = app_date + timedelta(days=withdrawal_period_days)

        record = PPPApplicationRecord(
            farm_id=farm_id,
            tenant_id=tenant_id,
            field_id=field_id,
            application_date=app_date,
            pest_detection_id=pest_detection_id,
            ppp_name=ppp_name,
            ppp_type=ppp_type,
            active_ingredient=active_ingredient,
            dosage_per_ha=dosage_per_ha,
            dosage_unit=dosage_unit,
            area_treated_ha=area_treated_ha,
            application_method=application_method,
            ppp_globalgap_approved=ppp_globalgap_approved,
            mrl_compliant=mrl_compliant,
            withdrawal_period_days=withdrawal_period_days,
            safe_harvest_date=safe_harvest_date,
            pest_or_disease_name=pest_or_disease_name,
            justification_en=justification_en,
            justification_ar=justification_ar,
            threshold_exceeded=threshold_exceeded,
            alternative_methods_tried=alternative_methods_tried,
            operator_certified=operator_certified,
            recorded_by=recorded_by,
        )

        # Emit NATS event
        if self._connected:
            event = IPMActivityRecordedEvent(
                farm_id=farm_id,
                tenant_id=tenant_id,
                field_id=field_id,
                activity_date=app_date,
                activity_type="TREATMENT",
                pest_or_disease_name_en=pest_or_disease_name,
                pest_or_disease_name_ar=justification_ar,
                detection_method="MANUAL_INSPECTION",
                severity_level="medium",
                treatment_applied=True,
                ppp_product_name=ppp_name,
                ppp_active_ingredient=active_ingredient,
                ppp_dosage=f"{dosage_per_ha} {dosage_unit}/ha",
                ppp_compliant=ppp_globalgap_approved and mrl_compliant,
                justification_en=justification_en,
                justification_ar=justification_ar,
                recorded_by=recorded_by,
            )

            await self.publisher.publish_event(
                GlobalGAPSubjects.IPM_ACTIVITY_RECORDED, event
            )

        return record

    # ─────────────────────────────────────────────────────────────────────────
    # Generate IPM Report
    # ─────────────────────────────────────────────────────────────────────────

    async def generate_ipm_report(
        self,
        farm_id: UUID,
        tenant_id: UUID,
        start_date: date,
        end_date: date,
        detections: list[PestDetectionRecord],
        ppp_applications: list[PPPApplicationRecord],
        ggn: str | None = None,
        generated_by: UUID | None = None,
    ) -> IPMReport:
        """
        Generate IPM report for GlobalGAP audit
        إنشاء تقرير IPM لتدقيق GlobalGAP

        Args:
            farm_id: Farm ID
            tenant_id: Tenant ID
            start_date: Report period start
            end_date: Report period end
            detections: List of pest detection records
            ppp_applications: List of PPP application records
            ggn: GlobalGAP Number
            generated_by: User ID who generated report

        Returns:
            IPMReport instance
        """
        # Detection statistics
        total_detections = len(detections)

        detections_by_category: dict[str, int] = {}
        for detection in detections:
            cat = (
                detection.pest_category.value
                if isinstance(detection.pest_category, PestCategory)
                else detection.pest_category
            )
            detections_by_category[cat] = detections_by_category.get(cat, 0) + 1

        detections_by_severity: dict[str, int] = {}
        for detection in detections:
            sev = (
                detection.severity_level.value
                if isinstance(detection.severity_level, SeverityLevel)
                else detection.severity_level
            )
            detections_by_severity[sev] = detections_by_severity.get(sev, 0) + 1

        # PPP statistics
        total_ppp = len(ppp_applications)
        justified_ppp = sum(1 for app in ppp_applications if app.threshold_exceeded)
        approved_ppp = sum(1 for app in ppp_applications if app.ppp_globalgap_approved)
        mrl_compliant_ppp = sum(1 for app in ppp_applications if app.mrl_compliant)

        ppp_justification_rate = (
            (justified_ppp / total_ppp * 100) if total_ppp > 0 else 100.0
        )
        ppp_approval_rate = (approved_ppp / total_ppp * 100) if total_ppp > 0 else 100.0
        mrl_compliance_rate = (
            (mrl_compliant_ppp / total_ppp * 100) if total_ppp > 0 else 100.0
        )

        # Active ingredients
        active_ingredients = list(
            {app.active_ingredient for app in ppp_applications}
        )
        total_active_ingredients = len(active_ingredients)

        # IPM activity counts
        monitoring_activities = total_detections
        chemical_control_activities = total_ppp

        # IPM principles compliance
        economic_thresholds_used = justified_ppp == total_ppp if total_ppp > 0 else True
        chemical_last_resort = (
            sum(1 for app in ppp_applications if app.alternative_methods_tried)
            >= (total_ppp * 0.8)
            if total_ppp > 0
            else True
        )

        # Overall compliance score (weighted)
        compliance_score = (
            ppp_justification_rate * 0.3
            + ppp_approval_rate * 0.3
            + mrl_compliance_rate * 0.4
        )
        is_compliant = (
            compliance_score >= 95.0
        )  # GlobalGAP requires 95%+ for Major Must

        # Issues and recommendations
        issues_en = []
        issues_ar = []
        recommendations_en = []
        recommendations_ar = []

        if ppp_justification_rate < 100:
            issues_en.append(
                f"Not all PPP applications justified (Current: {ppp_justification_rate:.1f}%)"
            )
            issues_ar.append(
                f"ليست جميع تطبيقات PPP مبررة (الحالي: {ppp_justification_rate:.1f}%)"
            )
            recommendations_en.append(
                "Ensure all PPP applications are based on economic thresholds"
            )
            recommendations_ar.append(
                "تأكد من أن جميع تطبيقات PPP تستند إلى عتبات اقتصادية"
            )

        if ppp_approval_rate < 100:
            issues_en.append(
                f"Unapproved PPP products used (Current: {ppp_approval_rate:.1f}%)"
            )
            issues_ar.append(
                f"استخدام منتجات PPP غير معتمدة (الحالي: {ppp_approval_rate:.1f}%)"
            )
            recommendations_en.append("Use only GlobalGAP approved PPP products")
            recommendations_ar.append("استخدم فقط منتجات PPP المعتمدة من GlobalGAP")

        if mrl_compliance_rate < 100:
            issues_en.append(
                f"MRL non-compliance detected (Current: {mrl_compliance_rate:.1f}%)"
            )
            issues_ar.append(
                f"عدم الامتثال لـ MRL (الحالي: {mrl_compliance_rate:.1f}%)"
            )
            recommendations_en.append(
                "Ensure all PPP applications comply with MRL limits"
            )
            recommendations_ar.append("تأكد من امتثال جميع تطبيقات PPP لحدود MRL")

        if not chemical_last_resort:
            recommendations_en.append(
                "Try non-chemical IPM methods before resorting to pesticides"
            )
            recommendations_ar.append(
                "جرب طرق IPM غير الكيميائية قبل اللجوء إلى المبيدات"
            )

        # Create report
        report = IPMReport(
            farm_id=farm_id,
            tenant_id=tenant_id,
            ggn=ggn,
            report_start_date=start_date,
            report_end_date=end_date,
            total_detections=total_detections,
            detections_by_category=detections_by_category,
            detections_by_severity=detections_by_severity,
            systematic_monitoring_in_place=total_detections > 0,
            total_ipm_activities=monitoring_activities + chemical_control_activities,
            monitoring_activities=monitoring_activities,
            chemical_control_activities=chemical_control_activities,
            total_ppp_applications=total_ppp,
            ppp_applications_justified=justified_ppp,
            ppp_justification_rate=ppp_justification_rate,
            approved_ppp_usage=approved_ppp,
            ppp_approval_rate=ppp_approval_rate,
            mrl_compliant_applications=mrl_compliant_ppp,
            mrl_compliance_rate=mrl_compliance_rate,
            total_active_ingredients_used=total_active_ingredients,
            active_ingredients_list=active_ingredients,
            economic_thresholds_used=economic_thresholds_used,
            preventive_measures_priority=True,  # Would need to track prevention activities
            non_chemical_methods_first=chemical_last_resort,
            chemical_last_resort=chemical_last_resort,
            overall_ipm_compliance_score=compliance_score,
            is_ipm_compliant=is_compliant,
            compliance_issues_en=issues_en,
            compliance_issues_ar=issues_ar,
            recommendations_en=recommendations_en,
            recommendations_ar=recommendations_ar,
            generated_by=generated_by,
        )

        return report

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
    "PestCategory",
    "IPMActivityType",
    "DetectionMethod",
    "SeverityLevel",
    "PPPType",
    # Models
    "PestDetectionRecord",
    "PPPApplicationRecord",
    "IPMReport",
    # Integration
    "CropHealthIntegration",
]
