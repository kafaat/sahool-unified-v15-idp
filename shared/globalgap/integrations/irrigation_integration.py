"""
GlobalGAP Irrigation Integration
تكامل الري مع GlobalGAP

Integrates irrigation-smart service with GlobalGAP compliance requirements.
Maps irrigation data to SPRING water management requirements and generates
water usage reports for audits.

يربط خدمة الري الذكي مع متطلبات الامتثال لـ GlobalGAP.
يربط بيانات الري بمتطلبات إدارة المياه SPRING ويولد
تقارير استخدام المياه للتدقيق.

Usage:
    from shared.globalgap.integrations.irrigation_integration import (
        IrrigationIntegration,
        WaterUsageReport,
        SPRINGCompliance
    )

    integration = IrrigationIntegration()
    await integration.connect()

    # Record irrigation event for GlobalGAP
    await integration.record_irrigation_event(
        farm_id=uuid4(),
        field_id=uuid4(),
        water_volume_m3=150.0,
        water_source="well",
        irrigation_method="drip"
    )

    # Generate water usage report
    report = await integration.generate_water_usage_report(
        farm_id=uuid4(),
        start_date=date(2024, 1, 1),
        end_date=date(2024, 12, 31)
    )
"""

from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
from enum import Enum

from pydantic import BaseModel, Field

from shared.events.publisher import EventPublisher
from .events import (
    WaterUsageRecordedEvent,
    GlobalGAPSubjects,
    ComplianceUpdatedEvent
)


# ─────────────────────────────────────────────────────────────────────────────
# Enums and Constants
# ─────────────────────────────────────────────────────────────────────────────

class WaterSource(str, Enum):
    """
    Water source types
    أنواع مصادر المياه
    """
    WELL = "WELL"  # بئر
    RIVER = "RIVER"  # نهر
    LAKE = "LAKE"  # بحيرة
    MUNICIPAL = "MUNICIPAL"  # بلدية
    RAINWATER = "RAINWATER"  # مياه الأمطار
    RECYCLED = "RECYCLED"  # مياه معاد تدويرها
    CANAL = "CANAL"  # قناة
    RESERVOIR = "RESERVOIR"  # خزان


class IrrigationMethod(str, Enum):
    """
    Irrigation methods
    طرق الري
    """
    DRIP = "DRIP"  # الري بالتنقيط
    SPRINKLER = "SPRINKLER"  # الري بالرش
    SURFACE = "SURFACE"  # الري السطحي
    FLOOD = "FLOOD"  # الري بالغمر
    SUBSURFACE = "SUBSURFACE"  # الري تحت السطحي
    CENTER_PIVOT = "CENTER_PIVOT"  # الري المحوري
    MICRO_SPRINKLER = "MICRO_SPRINKLER"  # الرش الصغير


class WaterQualityStatus(str, Enum):
    """
    Water quality test status
    حالة اختبار جودة المياه
    """
    TESTED_COMPLIANT = "TESTED_COMPLIANT"  # تم الاختبار ومطابق
    TESTED_NON_COMPLIANT = "TESTED_NON_COMPLIANT"  # تم الاختبار وغير مطابق
    NOT_TESTED = "NOT_TESTED"  # لم يتم الاختبار
    PENDING = "PENDING"  # قيد الانتظار


# ─────────────────────────────────────────────────────────────────────────────
# Data Models
# ─────────────────────────────────────────────────────────────────────────────

class WaterUsageRecord(BaseModel):
    """
    Water usage record for GlobalGAP compliance
    سجل استخدام المياه للامتثال لـ GlobalGAP
    """

    id: str = Field(default_factory=lambda: str(uuid4()), description="Record ID")
    farm_id: UUID = Field(..., description="Farm ID")
    field_id: Optional[UUID] = Field(None, description="Field ID")
    tenant_id: UUID = Field(..., description="Tenant ID")

    # Water usage
    water_volume_m3: float = Field(..., ge=0, description="Water volume in cubic meters")
    water_source: WaterSource = Field(..., description="Water source")
    water_source_name: Optional[str] = Field(None, description="Specific water source name")

    # Quality
    water_quality_status: WaterQualityStatus = Field(..., description="Water quality test status")
    water_quality_test_date: Optional[date] = Field(None, description="Last water quality test date")
    water_quality_certificate_url: Optional[str] = Field(None, description="Water quality certificate URL")

    # Period
    recording_date: date = Field(..., description="Recording date")
    usage_period_start: Optional[date] = Field(None, description="Usage period start")
    usage_period_end: Optional[date] = Field(None, description="Usage period end")

    # Irrigation details
    irrigation_method: Optional[IrrigationMethod] = Field(None, description="Irrigation method used")
    irrigation_duration_hours: Optional[float] = Field(None, ge=0, description="Irrigation duration")
    irrigation_efficiency: Optional[float] = Field(None, ge=0, le=100, description="Irrigation efficiency %")

    # Compliance fields
    water_rights_documented: bool = Field(default=False, description="Water rights documented")
    water_rights_document_url: Optional[str] = Field(None, description="Water rights document URL")
    spring_compliant: bool = Field(..., description="SPRING water requirement compliance")

    # Metadata
    recorded_by: Optional[UUID] = Field(None, description="User who recorded")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }


class WaterUsageReport(BaseModel):
    """
    Water usage report for GlobalGAP audits
    تقرير استخدام المياه لتدقيق GlobalGAP
    """

    report_id: str = Field(default_factory=lambda: str(uuid4()), description="Report ID")
    farm_id: UUID = Field(..., description="Farm ID")
    tenant_id: UUID = Field(..., description="Tenant ID")
    ggn: Optional[str] = Field(None, description="GlobalGAP Number")

    # Reporting period
    report_start_date: date = Field(..., description="Report period start")
    report_end_date: date = Field(..., description="Report period end")

    # Summary statistics
    total_water_volume_m3: float = Field(..., ge=0, description="Total water volume in m³")
    total_irrigated_area_ha: float = Field(..., ge=0, description="Total irrigated area in hectares")
    average_water_per_ha: float = Field(..., ge=0, description="Average water per hectare (m³/ha)")

    # Water sources breakdown
    water_by_source: Dict[str, float] = Field(
        default_factory=dict,
        description="Water volume by source (e.g., {'WELL': 1000.0, 'MUNICIPAL': 500.0})"
    )

    # Irrigation methods breakdown
    water_by_irrigation_method: Dict[str, float] = Field(
        default_factory=dict,
        description="Water volume by irrigation method"
    )

    # Compliance metrics
    total_records: int = Field(..., ge=0, description="Total water usage records")
    records_with_quality_tests: int = Field(..., ge=0, description="Records with water quality tests")
    quality_test_compliance_rate: float = Field(..., ge=0, le=100, description="Quality test compliance %")

    records_with_water_rights: int = Field(..., ge=0, description="Records with documented water rights")
    water_rights_compliance_rate: float = Field(..., ge=0, le=100, description="Water rights compliance %")

    spring_compliant_records: int = Field(..., ge=0, description="SPRING compliant records")
    spring_compliance_rate: float = Field(..., ge=0, le=100, description="SPRING compliance %")

    # Overall compliance
    overall_compliance_score: float = Field(..., ge=0, le=100, description="Overall water management compliance %")
    is_compliant: bool = Field(..., description="Meets GlobalGAP water management requirements")

    # Issues and recommendations
    non_compliant_sources: List[str] = Field(
        default_factory=list,
        description="Water sources without quality tests"
    )
    missing_water_rights: List[str] = Field(
        default_factory=list,
        description="Sources missing water rights documentation"
    )

    recommendations_en: List[str] = Field(default_factory=list, description="Recommendations in English")
    recommendations_ar: List[str] = Field(default_factory=list, description="Recommendations in Arabic")

    # Report metadata
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    generated_by: Optional[UUID] = Field(None, description="User who generated report")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }


class SPRINGCompliance(BaseModel):
    """
    SPRING (Sustainable Program for Irrigation and Groundwater Use) compliance status
    حالة الامتثال لبرنامج SPRING
    """

    farm_id: UUID = Field(..., description="Farm ID")
    compliance_period_start: date = Field(..., description="Compliance period start")
    compliance_period_end: date = Field(..., description="Compliance period end")

    # SPRING requirements
    water_management_plan_exists: bool = Field(..., description="Water management plan documented")
    water_management_plan_url: Optional[str] = Field(None, description="Water management plan URL")

    irrigation_system_efficiency: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="Irrigation system efficiency %"
    )
    target_efficiency: float = Field(default=75.0, ge=0, le=100, description="Target efficiency %")

    # Water monitoring
    water_usage_monitored: bool = Field(..., description="Water usage systematically monitored")
    monitoring_frequency_days: Optional[int] = Field(None, ge=1, description="Monitoring frequency in days")

    # Quality testing
    water_quality_tested_annually: bool = Field(..., description="Water quality tested at least annually")
    last_quality_test_date: Optional[date] = Field(None, description="Last quality test date")
    days_since_last_test: Optional[int] = Field(None, description="Days since last quality test")

    # Legal compliance
    water_rights_authorized: bool = Field(..., description="Legal water rights/authorization")
    water_usage_within_limits: bool = Field(..., description="Water usage within authorized limits")

    # Overall compliance
    is_spring_compliant: bool = Field(..., description="Overall SPRING compliance")
    compliance_score: float = Field(..., ge=0, le=100, description="SPRING compliance score %")

    # Issues
    non_compliance_issues_en: List[str] = Field(
        default_factory=list,
        description="Non-compliance issues (English)"
    )
    non_compliance_issues_ar: List[str] = Field(
        default_factory=list,
        description="Non-compliance issues (Arabic)"
    )

    assessed_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }


# ─────────────────────────────────────────────────────────────────────────────
# Integration Class
# ─────────────────────────────────────────────────────────────────────────────

class IrrigationIntegration:
    """
    Integration between irrigation-smart service and GlobalGAP compliance
    التكامل بين خدمة الري الذكي والامتثال لـ GlobalGAP

    Responsibilities:
    - Map irrigation events to GlobalGAP water usage records
    - Track water source compliance
    - Generate water usage reports for audits
    - Monitor SPRING water management compliance
    - Emit NATS events for water usage tracking
    """

    def __init__(self, publisher: Optional[EventPublisher] = None):
        """
        Initialize irrigation integration

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
            self.publisher = EventPublisher(service_name="globalgap-irrigation-integration")

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
    # Record Water Usage
    # ─────────────────────────────────────────────────────────────────────────

    async def record_irrigation_event(
        self,
        farm_id: UUID,
        tenant_id: UUID,
        water_volume_m3: float,
        water_source: WaterSource,
        field_id: Optional[UUID] = None,
        irrigation_method: Optional[IrrigationMethod] = None,
        water_quality_status: WaterQualityStatus = WaterQualityStatus.NOT_TESTED,
        water_quality_test_date: Optional[date] = None,
        water_rights_documented: bool = False,
        irrigation_duration_hours: Optional[float] = None,
        irrigation_efficiency: Optional[float] = None,
        recording_date: Optional[date] = None,
        recorded_by: Optional[UUID] = None,
    ) -> WaterUsageRecord:
        """
        Record irrigation event for GlobalGAP compliance tracking
        تسجيل حدث الري لتتبع الامتثال لـ GlobalGAP

        Args:
            farm_id: Farm ID
            tenant_id: Tenant ID
            water_volume_m3: Water volume in cubic meters
            water_source: Water source type
            field_id: Field ID (optional)
            irrigation_method: Irrigation method used
            water_quality_status: Water quality test status
            water_quality_test_date: Date of last water quality test
            water_rights_documented: Whether water rights are documented
            irrigation_duration_hours: Duration of irrigation
            irrigation_efficiency: Irrigation efficiency percentage
            recording_date: Date of record (defaults to today)
            recorded_by: User ID who recorded

        Returns:
            WaterUsageRecord instance
        """
        # Determine SPRING compliance
        spring_compliant = self._check_spring_compliance(
            water_quality_status=water_quality_status,
            water_quality_test_date=water_quality_test_date,
            water_rights_documented=water_rights_documented
        )

        # Create water usage record
        record = WaterUsageRecord(
            farm_id=farm_id,
            tenant_id=tenant_id,
            field_id=field_id,
            water_volume_m3=water_volume_m3,
            water_source=water_source,
            water_quality_status=water_quality_status,
            water_quality_test_date=water_quality_test_date,
            recording_date=recording_date or date.today(),
            irrigation_method=irrigation_method,
            irrigation_duration_hours=irrigation_duration_hours,
            irrigation_efficiency=irrigation_efficiency,
            water_rights_documented=water_rights_documented,
            spring_compliant=spring_compliant,
            recorded_by=recorded_by,
        )

        # Emit NATS event
        if self._connected:
            event = WaterUsageRecordedEvent(
                farm_id=farm_id,
                tenant_id=tenant_id,
                field_id=field_id,
                water_volume_m3=water_volume_m3,
                water_source=water_source.value,
                water_quality_tested=(water_quality_status == WaterQualityStatus.TESTED_COMPLIANT),
                recording_date=record.recording_date,
                irrigation_method=irrigation_method.value if irrigation_method else None,
                irrigation_efficiency=irrigation_efficiency,
                spring_water_requirement_met=spring_compliant,
                water_rights_documented=water_rights_documented,
                recorded_by=recorded_by,
            )

            await self.publisher.publish_event(
                GlobalGAPSubjects.WATER_USAGE_RECORDED,
                event
            )

        return record

    def _check_spring_compliance(
        self,
        water_quality_status: WaterQualityStatus,
        water_quality_test_date: Optional[date],
        water_rights_documented: bool
    ) -> bool:
        """
        Check if water usage meets SPRING requirements
        التحقق من استيفاء استخدام المياه لمتطلبات SPRING

        SPRING requires:
        - Water quality tested and compliant
        - Water quality test within last 12 months
        - Water rights documented

        Returns:
            True if SPRING compliant
        """
        # Water quality must be tested and compliant
        if water_quality_status != WaterQualityStatus.TESTED_COMPLIANT:
            return False

        # Water quality test must be recent (within 12 months)
        if water_quality_test_date:
            days_since_test = (date.today() - water_quality_test_date).days
            if days_since_test > 365:
                return False
        else:
            return False

        # Water rights must be documented
        if not water_rights_documented:
            return False

        return True

    # ─────────────────────────────────────────────────────────────────────────
    # Generate Reports
    # ─────────────────────────────────────────────────────────────────────────

    async def generate_water_usage_report(
        self,
        farm_id: UUID,
        tenant_id: UUID,
        start_date: date,
        end_date: date,
        records: List[WaterUsageRecord],
        ggn: Optional[str] = None,
        total_irrigated_area_ha: float = 0.0,
        generated_by: Optional[UUID] = None,
    ) -> WaterUsageReport:
        """
        Generate water usage report for GlobalGAP audit
        إنشاء تقرير استخدام المياه لتدقيق GlobalGAP

        Args:
            farm_id: Farm ID
            tenant_id: Tenant ID
            start_date: Report period start
            end_date: Report period end
            records: List of water usage records
            ggn: GlobalGAP Number
            total_irrigated_area_ha: Total irrigated area in hectares
            generated_by: User ID who generated report

        Returns:
            WaterUsageReport instance
        """
        # Calculate summary statistics
        total_water = sum(r.water_volume_m3 for r in records)
        avg_water_per_ha = total_water / total_irrigated_area_ha if total_irrigated_area_ha > 0 else 0.0

        # Water by source
        water_by_source: Dict[str, float] = {}
        for record in records:
            source = record.water_source.value if isinstance(record.water_source, WaterSource) else record.water_source
            water_by_source[source] = water_by_source.get(source, 0.0) + record.water_volume_m3

        # Water by irrigation method
        water_by_method: Dict[str, float] = {}
        for record in records:
            if record.irrigation_method:
                method = record.irrigation_method.value if isinstance(record.irrigation_method, IrrigationMethod) else record.irrigation_method
                water_by_method[method] = water_by_method.get(method, 0.0) + record.water_volume_m3

        # Compliance metrics
        total_records = len(records)
        records_with_quality_tests = sum(
            1 for r in records if r.water_quality_status == WaterQualityStatus.TESTED_COMPLIANT
        )
        records_with_water_rights = sum(1 for r in records if r.water_rights_documented)
        spring_compliant_records = sum(1 for r in records if r.spring_compliant)

        quality_test_rate = (records_with_quality_tests / total_records * 100) if total_records > 0 else 0.0
        water_rights_rate = (records_with_water_rights / total_records * 100) if total_records > 0 else 0.0
        spring_rate = (spring_compliant_records / total_records * 100) if total_records > 0 else 0.0

        # Overall compliance score (weighted average)
        overall_compliance = (quality_test_rate * 0.4 + water_rights_rate * 0.3 + spring_rate * 0.3)
        is_compliant = overall_compliance >= 95.0  # GlobalGAP requires 95%+ for Major Must

        # Identify issues
        non_compliant_sources = [
            source for source, _ in water_by_source.items()
            if not any(
                r.water_source.value == source and r.water_quality_status == WaterQualityStatus.TESTED_COMPLIANT
                for r in records
            )
        ]

        missing_water_rights = [
            source for source, _ in water_by_source.items()
            if not any(
                r.water_source.value == source and r.water_rights_documented
                for r in records
            )
        ]

        # Generate recommendations
        recommendations_en = []
        recommendations_ar = []

        if quality_test_rate < 100:
            recommendations_en.append(
                f"Test water quality for all sources. Current: {quality_test_rate:.1f}%"
            )
            recommendations_ar.append(
                f"اختبار جودة المياه لجميع المصادر. الحالي: {quality_test_rate:.1f}%"
            )

        if water_rights_rate < 100:
            recommendations_en.append(
                f"Document water rights for all sources. Current: {water_rights_rate:.1f}%"
            )
            recommendations_ar.append(
                f"توثيق حقوق المياه لجميع المصادر. الحالي: {water_rights_rate:.1f}%"
            )

        if spring_rate < 100:
            recommendations_en.append(
                f"Ensure SPRING compliance for all water usage. Current: {spring_rate:.1f}%"
            )
            recommendations_ar.append(
                f"ضمان الامتثال لـ SPRING لجميع استخدامات المياه. الحالي: {spring_rate:.1f}%"
            )

        # Create report
        report = WaterUsageReport(
            farm_id=farm_id,
            tenant_id=tenant_id,
            ggn=ggn,
            report_start_date=start_date,
            report_end_date=end_date,
            total_water_volume_m3=total_water,
            total_irrigated_area_ha=total_irrigated_area_ha,
            average_water_per_ha=avg_water_per_ha,
            water_by_source=water_by_source,
            water_by_irrigation_method=water_by_method,
            total_records=total_records,
            records_with_quality_tests=records_with_quality_tests,
            quality_test_compliance_rate=quality_test_rate,
            records_with_water_rights=records_with_water_rights,
            water_rights_compliance_rate=water_rights_rate,
            spring_compliant_records=spring_compliant_records,
            spring_compliance_rate=spring_rate,
            overall_compliance_score=overall_compliance,
            is_compliant=is_compliant,
            non_compliant_sources=non_compliant_sources,
            missing_water_rights=missing_water_rights,
            recommendations_en=recommendations_en,
            recommendations_ar=recommendations_ar,
            generated_by=generated_by,
        )

        return report

    # ─────────────────────────────────────────────────────────────────────────
    # SPRING Compliance Assessment
    # ─────────────────────────────────────────────────────────────────────────

    async def assess_spring_compliance(
        self,
        farm_id: UUID,
        water_management_plan_exists: bool,
        irrigation_system_efficiency: Optional[float],
        water_usage_monitored: bool,
        monitoring_frequency_days: Optional[int],
        water_quality_tested_annually: bool,
        last_quality_test_date: Optional[date],
        water_rights_authorized: bool,
        water_usage_within_limits: bool,
        compliance_period_start: date,
        compliance_period_end: date,
    ) -> SPRINGCompliance:
        """
        Assess SPRING (Sustainable Program for Irrigation and Groundwater Use) compliance
        تقييم الامتثال لبرنامج SPRING

        Args:
            farm_id: Farm ID
            water_management_plan_exists: Water management plan documented
            irrigation_system_efficiency: Current irrigation efficiency %
            water_usage_monitored: Water usage systematically monitored
            monitoring_frequency_days: Monitoring frequency
            water_quality_tested_annually: Annual water quality testing
            last_quality_test_date: Last quality test date
            water_rights_authorized: Legal water rights/authorization
            water_usage_within_limits: Usage within authorized limits
            compliance_period_start: Assessment period start
            compliance_period_end: Assessment period end

        Returns:
            SPRINGCompliance instance
        """
        issues_en = []
        issues_ar = []
        compliance_points = 0
        total_points = 7

        # Check each requirement
        if water_management_plan_exists:
            compliance_points += 1
        else:
            issues_en.append("Water management plan not documented")
            issues_ar.append("خطة إدارة المياه غير موثقة")

        if irrigation_system_efficiency and irrigation_system_efficiency >= 75.0:
            compliance_points += 1
        else:
            issues_en.append("Irrigation efficiency below 75% target")
            issues_ar.append("كفاءة الري أقل من الهدف 75%")

        if water_usage_monitored:
            compliance_points += 1
        else:
            issues_en.append("Water usage not systematically monitored")
            issues_ar.append("استخدام المياه غير مراقب بشكل منهجي")

        if water_quality_tested_annually:
            compliance_points += 1
        else:
            issues_en.append("Water quality not tested annually")
            issues_ar.append("جودة المياه لم يتم اختبارها سنويًا")

        if water_rights_authorized:
            compliance_points += 1
        else:
            issues_en.append("Water rights not authorized/documented")
            issues_ar.append("حقوق المياه غير مصرح بها/موثقة")

        if water_usage_within_limits:
            compliance_points += 1
        else:
            issues_en.append("Water usage exceeds authorized limits")
            issues_ar.append("استخدام المياه يتجاوز الحدود المصرح بها")

        # Check last quality test date
        days_since_test = None
        if last_quality_test_date:
            days_since_test = (date.today() - last_quality_test_date).days
            if days_since_test <= 365:
                compliance_points += 1
            else:
                issues_en.append(f"Water quality test overdue ({days_since_test} days since last test)")
                issues_ar.append(f"اختبار جودة المياه متأخر ({days_since_test} يوم منذ آخر اختبار)")
        else:
            issues_en.append("No water quality test date recorded")
            issues_ar.append("لا يوجد تاريخ اختبار جودة المياه مسجل")

        # Calculate compliance score
        compliance_score = (compliance_points / total_points) * 100
        is_spring_compliant = compliance_score >= 100.0  # All requirements must be met

        return SPRINGCompliance(
            farm_id=farm_id,
            compliance_period_start=compliance_period_start,
            compliance_period_end=compliance_period_end,
            water_management_plan_exists=water_management_plan_exists,
            irrigation_system_efficiency=irrigation_system_efficiency,
            water_usage_monitored=water_usage_monitored,
            monitoring_frequency_days=monitoring_frequency_days,
            water_quality_tested_annually=water_quality_tested_annually,
            last_quality_test_date=last_quality_test_date,
            days_since_last_test=days_since_test,
            water_rights_authorized=water_rights_authorized,
            water_usage_within_limits=water_usage_within_limits,
            is_spring_compliant=is_spring_compliant,
            compliance_score=compliance_score,
            non_compliance_issues_en=issues_en,
            non_compliance_issues_ar=issues_ar,
        )

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
    "WaterSource",
    "IrrigationMethod",
    "WaterQualityStatus",

    # Models
    "WaterUsageRecord",
    "WaterUsageReport",
    "SPRINGCompliance",

    # Integration
    "IrrigationIntegration",
]
