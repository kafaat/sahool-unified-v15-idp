"""
Water Compliance Reporting Module - وحدة تقارير الامتثال المائي
================================================================

Provides regulatory compliance reporting for Saudi water regulations:
- MEWA (Ministry of Environment, Water and Agriculture) reports
- NWC (National Water Company) consumption reports
- Groundwater extraction reports
- Water quality compliance reports
- Conservation initiative tracking

Author: SAHOOL Platform Team
Version: 1.0.0
Updated: January 2026
"""

from __future__ import annotations

import calendar
import uuid
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from typing import Any

from .models import (
    AlertSeverity,
    ComplianceStatus,
    SaudiWaterStandards,
    WaterAllocation,
    WaterConsumptionRecord,
    WaterQualityClass,
    WaterQualityTest,
    WaterRight,
    WaterSource,
    WaterSourceStatus,
    WaterSourceType,
)

# =============================================================================
# Report Models - نماذج التقارير
# =============================================================================


@dataclass
class ReportPeriod:
    """Report period definition - تعريف فترة التقرير"""

    start_date: date
    end_date: date
    period_type: str = "quarterly"  # daily, weekly, monthly, quarterly, annual
    period_type_ar: str = "ربع سنوي"

    @property
    def days(self) -> int:
        """Number of days in period"""
        return (self.end_date - self.start_date).days + 1

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "period_type": self.period_type,
            "period_type_ar": self.period_type_ar,
            "days": self.days,
        }


@dataclass
class ConsumptionSummary:
    """Water consumption summary - ملخص استهلاك المياه"""

    total_m3: float = 0.0
    irrigation_m3: float = 0.0
    livestock_m3: float = 0.0
    domestic_m3: float = 0.0
    processing_m3: float = 0.0
    other_m3: float = 0.0

    avg_daily_m3: float = 0.0
    max_daily_m3: float = 0.0
    min_daily_m3: float = 0.0

    by_source: dict[str, float] = field(default_factory=dict)
    by_field: dict[str, float] = field(default_factory=dict)
    by_crop: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "total_m3": self.total_m3,
            "by_purpose": {
                "irrigation_m3": self.irrigation_m3,
                "livestock_m3": self.livestock_m3,
                "domestic_m3": self.domestic_m3,
                "processing_m3": self.processing_m3,
                "other_m3": self.other_m3,
            },
            "daily_statistics": {
                "avg_m3": self.avg_daily_m3,
                "max_m3": self.max_daily_m3,
                "min_m3": self.min_daily_m3,
            },
            "by_source": self.by_source,
            "by_field": self.by_field,
            "by_crop": self.by_crop,
        }


@dataclass
class ComplianceIssue:
    """Compliance issue record - سجل مشكلة الامتثال"""

    id: str
    issue_type: str
    issue_type_ar: str
    severity: AlertSeverity
    description_en: str
    description_ar: str
    regulation_reference: str | None = None
    regulation_reference_ar: str | None = None
    detected_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    resolved: bool = False
    resolved_at: datetime | None = None
    resolution_notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "issue_type": self.issue_type,
            "issue_type_ar": self.issue_type_ar,
            "severity": self.severity.value,
            "description_en": self.description_en,
            "description_ar": self.description_ar,
            "regulation_reference": self.regulation_reference,
            "regulation_reference_ar": self.regulation_reference_ar,
            "detected_at": self.detected_at.isoformat(),
            "resolved": self.resolved,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
        }


# =============================================================================
# MEWA Compliance Report - تقرير الامتثال لوزارة البيئة والمياه والزراعة
# =============================================================================


@dataclass
class MEWAComplianceReport:
    """
    MEWA Water Compliance Report - تقرير الامتثال المائي لوزارة البيئة والمياه والزراعة

    Required quarterly report for agricultural water users in Saudi Arabia.
    This report documents water extraction, consumption, and compliance
    with allocated water rights.
    """

    id: str
    tenant_id: str
    farm_id: str
    report_period: ReportPeriod
    generated_at: datetime

    # Farm information - معلومات المزرعة
    farm_name: str = ""
    farm_name_ar: str = ""
    farm_license_number: str = ""
    governorate: str = ""
    governorate_ar: str = ""
    region: str = ""
    region_ar: str = ""
    total_area_ha: float = 0.0

    # Water sources - مصادر المياه
    sources: list[WaterSource] = field(default_factory=list)
    total_sources: int = 0
    wells_count: int = 0
    other_sources_count: int = 0

    # Water rights and allocations - حقوق المياه والتخصيصات
    total_allocated_m3: float = 0.0
    total_allocated_m3_period: float = 0.0

    # Consumption - الاستهلاك
    consumption_summary: ConsumptionSummary = field(default_factory=ConsumptionSummary)

    # Compliance - الامتثال
    compliance_status: ComplianceStatus = ComplianceStatus.COMPLIANT
    compliance_issues: list[ComplianceIssue] = field(default_factory=list)
    allocation_utilization_percent: float = 0.0

    # Metering - القياس
    metered_sources_count: int = 0
    unmetered_sources_count: int = 0
    metering_compliance: bool = True

    # Quality - الجودة
    quality_tests_count: int = 0
    quality_compliant: bool = True
    quality_issues: list[str] = field(default_factory=list)

    # Conservation - الحفاظ على المياه
    conservation_measures: list[str] = field(default_factory=list)
    conservation_measures_ar: list[str] = field(default_factory=list)
    water_savings_m3: float = 0.0

    # Certification - التصديق
    prepared_by: str = ""
    prepared_by_title: str = ""
    certification_date: date | None = None
    digital_signature: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for submission"""
        return {
            "report_id": self.id,
            "report_type": "MEWA_QUARTERLY_COMPLIANCE",
            "report_type_ar": "تقرير الامتثال الربع سنوي لوزارة البيئة",
            "tenant_id": self.tenant_id,
            "farm_id": self.farm_id,
            "period": self.report_period.to_dict(),
            "generated_at": self.generated_at.isoformat(),
            "farm_information": {
                "name": self.farm_name,
                "name_ar": self.farm_name_ar,
                "license_number": self.farm_license_number,
                "governorate": self.governorate,
                "governorate_ar": self.governorate_ar,
                "region": self.region,
                "region_ar": self.region_ar,
                "total_area_ha": self.total_area_ha,
            },
            "water_sources": {
                "total_count": self.total_sources,
                "wells_count": self.wells_count,
                "other_sources_count": self.other_sources_count,
                "sources": [s.to_dict() for s in self.sources],
            },
            "water_allocation": {
                "total_allocated_m3": self.total_allocated_m3,
                "period_allocation_m3": self.total_allocated_m3_period,
            },
            "consumption": self.consumption_summary.to_dict(),
            "compliance": {
                "status": self.compliance_status.value,
                "allocation_utilization_percent": self.allocation_utilization_percent,
                "issues": [i.to_dict() for i in self.compliance_issues],
            },
            "metering": {
                "metered_sources": self.metered_sources_count,
                "unmetered_sources": self.unmetered_sources_count,
                "compliance": self.metering_compliance,
            },
            "water_quality": {
                "tests_count": self.quality_tests_count,
                "compliant": self.quality_compliant,
                "issues": self.quality_issues,
            },
            "conservation": {
                "measures": self.conservation_measures,
                "measures_ar": self.conservation_measures_ar,
                "water_savings_m3": self.water_savings_m3,
            },
            "certification": {
                "prepared_by": self.prepared_by,
                "title": self.prepared_by_title,
                "date": (self.certification_date.isoformat() if self.certification_date else None),
            },
        }


# =============================================================================
# Well Extraction Report - تقرير استخراج الآبار
# =============================================================================


@dataclass
class WellExtractionReport:
    """
    Well Extraction Report - تقرير استخراج البئر

    Required report for groundwater wells documenting extraction volumes
    and compliance with licensed limits.
    """

    id: str
    tenant_id: str
    well_id: str
    report_period: ReportPeriod
    generated_at: datetime

    # Well information - معلومات البئر
    well_name: str = ""
    well_name_ar: str = ""
    well_license_number: str = ""
    well_depth_m: float = 0.0
    aquifer_name: str = ""
    aquifer_name_ar: str = ""

    # Location - الموقع
    latitude: float = 0.0
    longitude: float = 0.0
    governorate: str = ""
    region: str = ""

    # Licensed extraction - الاستخراج المرخص
    licensed_extraction_m3_year: float = 0.0
    licensed_extraction_m3_day: float = 0.0

    # Actual extraction - الاستخراج الفعلي
    total_extraction_m3: float = 0.0
    avg_daily_extraction_m3: float = 0.0
    max_daily_extraction_m3: float = 0.0
    extraction_days: int = 0
    pump_hours: float = 0.0

    # Year-to-date - منذ بداية العام
    ytd_extraction_m3: float = 0.0
    ytd_remaining_m3: float = 0.0
    ytd_utilization_percent: float = 0.0

    # Water levels - مستويات المياه
    static_water_level_start_m: float | None = None
    static_water_level_end_m: float | None = None
    level_change_m: float | None = None
    avg_drawdown_m: float | None = None

    # Meter readings - قراءات العداد
    meter_reading_start: float | None = None
    meter_reading_end: float | None = None
    meter_id: str | None = None
    meter_certified: bool = True
    meter_calibration_date: date | None = None

    # Compliance - الامتثال
    compliance_status: ComplianceStatus = ComplianceStatus.COMPLIANT
    over_extraction_m3: float = 0.0
    compliance_notes: str = ""
    compliance_notes_ar: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "report_id": self.id,
            "report_type": "WELL_EXTRACTION",
            "report_type_ar": "تقرير استخراج البئر",
            "tenant_id": self.tenant_id,
            "well_id": self.well_id,
            "period": self.report_period.to_dict(),
            "generated_at": self.generated_at.isoformat(),
            "well_information": {
                "name": self.well_name,
                "name_ar": self.well_name_ar,
                "license_number": self.well_license_number,
                "depth_m": self.well_depth_m,
                "aquifer": self.aquifer_name,
                "aquifer_ar": self.aquifer_name_ar,
                "location": {
                    "latitude": self.latitude,
                    "longitude": self.longitude,
                    "governorate": self.governorate,
                    "region": self.region,
                },
            },
            "licensed_extraction": {
                "annual_m3": self.licensed_extraction_m3_year,
                "daily_m3": self.licensed_extraction_m3_day,
            },
            "actual_extraction": {
                "total_m3": self.total_extraction_m3,
                "avg_daily_m3": self.avg_daily_extraction_m3,
                "max_daily_m3": self.max_daily_extraction_m3,
                "extraction_days": self.extraction_days,
                "pump_hours": self.pump_hours,
            },
            "year_to_date": {
                "extraction_m3": self.ytd_extraction_m3,
                "remaining_m3": self.ytd_remaining_m3,
                "utilization_percent": self.ytd_utilization_percent,
            },
            "water_levels": {
                "static_start_m": self.static_water_level_start_m,
                "static_end_m": self.static_water_level_end_m,
                "level_change_m": self.level_change_m,
                "avg_drawdown_m": self.avg_drawdown_m,
            },
            "meter": {
                "id": self.meter_id,
                "reading_start": self.meter_reading_start,
                "reading_end": self.meter_reading_end,
                "certified": self.meter_certified,
                "calibration_date": (self.meter_calibration_date.isoformat() if self.meter_calibration_date else None),
            },
            "compliance": {
                "status": self.compliance_status.value,
                "over_extraction_m3": self.over_extraction_m3,
                "notes": self.compliance_notes,
                "notes_ar": self.compliance_notes_ar,
            },
        }


# =============================================================================
# Water Quality Report - تقرير جودة المياه
# =============================================================================


@dataclass
class WaterQualityReport:
    """
    Water Quality Compliance Report - تقرير الامتثال لجودة المياه

    Documents water quality testing and compliance with
    Saudi irrigation water standards.
    """

    id: str
    tenant_id: str
    farm_id: str
    report_period: ReportPeriod
    generated_at: datetime

    # Sources tested - المصادر المختبرة
    sources_tested: int = 0
    total_sources: int = 0

    # Tests conducted - الاختبارات المجراة
    tests_conducted: int = 0
    tests_passed: int = 0
    tests_failed: int = 0

    # Quality classifications - تصنيفات الجودة
    class_a_sources: int = 0
    class_b_sources: int = 0
    class_c_sources: int = 0
    class_d_sources: int = 0
    unfit_sources: int = 0

    # Test results - نتائج الاختبارات
    test_results: list[WaterQualityTest] = field(default_factory=list)

    # Key parameters summary - ملخص المعايير الرئيسية
    avg_ec_ds_m: float | None = None
    avg_tds_ppm: float | None = None
    avg_ph: float | None = None
    avg_sar: float | None = None

    # Compliance - الامتثال
    compliance_status: ComplianceStatus = ComplianceStatus.COMPLIANT
    compliance_issues: list[ComplianceIssue] = field(default_factory=list)

    # Recommendations - التوصيات
    recommendations_en: list[str] = field(default_factory=list)
    recommendations_ar: list[str] = field(default_factory=list)

    # Lab information - معلومات المختبر
    testing_lab: str = ""
    testing_lab_ar: str = ""
    lab_accreditation: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "report_id": self.id,
            "report_type": "WATER_QUALITY",
            "report_type_ar": "تقرير جودة المياه",
            "tenant_id": self.tenant_id,
            "farm_id": self.farm_id,
            "period": self.report_period.to_dict(),
            "generated_at": self.generated_at.isoformat(),
            "testing_coverage": {
                "sources_tested": self.sources_tested,
                "total_sources": self.total_sources,
                "coverage_percent": ((self.sources_tested / self.total_sources * 100) if self.total_sources > 0 else 0),
            },
            "test_summary": {
                "total_tests": self.tests_conducted,
                "passed": self.tests_passed,
                "failed": self.tests_failed,
                "pass_rate_percent": (
                    (self.tests_passed / self.tests_conducted * 100) if self.tests_conducted > 0 else 0
                ),
            },
            "quality_classification": {
                "class_a": self.class_a_sources,
                "class_b": self.class_b_sources,
                "class_c": self.class_c_sources,
                "class_d": self.class_d_sources,
                "unfit": self.unfit_sources,
            },
            "key_parameters": {
                "avg_ec_ds_m": self.avg_ec_ds_m,
                "avg_tds_ppm": self.avg_tds_ppm,
                "avg_ph": self.avg_ph,
                "avg_sar": self.avg_sar,
            },
            "compliance": {
                "status": self.compliance_status.value,
                "issues": [i.to_dict() for i in self.compliance_issues],
            },
            "recommendations": {
                "en": self.recommendations_en,
                "ar": self.recommendations_ar,
            },
            "laboratory": {
                "name": self.testing_lab,
                "name_ar": self.testing_lab_ar,
                "accreditation": self.lab_accreditation,
            },
        }


# =============================================================================
# Farm Water Summary Report - تقرير ملخص مياه المزرعة
# =============================================================================


@dataclass
class FarmWaterSummaryReport:
    """
    Farm Water Summary Report - تقرير ملخص مياه المزرعة

    Comprehensive water management summary for the farm including
    all sources, consumption, efficiency, and compliance.
    """

    id: str
    tenant_id: str
    farm_id: str
    report_period: ReportPeriod
    generated_at: datetime

    # Farm overview - نظرة عامة على المزرعة
    farm_name: str = ""
    farm_name_ar: str = ""
    total_area_ha: float = 0.0
    irrigated_area_ha: float = 0.0
    active_fields: int = 0
    crops: list[str] = field(default_factory=list)
    crops_ar: list[str] = field(default_factory=list)

    # Water sources summary - ملخص مصادر المياه
    total_sources: int = 0
    active_sources: int = 0
    total_capacity_m3: float = 0.0
    available_capacity_m3: float = 0.0

    # Water allocation - تخصيص المياه
    total_allocation_m3: float = 0.0
    used_allocation_m3: float = 0.0
    remaining_allocation_m3: float = 0.0
    allocation_utilization_percent: float = 0.0

    # Consumption summary - ملخص الاستهلاك
    consumption: ConsumptionSummary = field(default_factory=ConsumptionSummary)

    # Efficiency metrics - مقاييس الكفاءة
    avg_application_efficiency: float | None = None
    avg_distribution_uniformity: float | None = None
    water_productivity_kg_m3: float | None = None
    economic_productivity_sar_m3: float | None = None

    # Water quality - جودة المياه
    quality_tests_count: int = 0
    quality_class_distribution: dict[str, int] = field(default_factory=dict)

    # Compliance summary - ملخص الامتثال
    overall_compliance: ComplianceStatus = ComplianceStatus.COMPLIANT
    compliance_issues_count: int = 0
    critical_issues_count: int = 0

    # Trends - الاتجاهات
    consumption_trend: str = "stable"  # increasing, decreasing, stable
    consumption_trend_ar: str = "مستقر"
    consumption_change_percent: float = 0.0

    # Cost analysis - تحليل التكلفة
    total_water_cost_sar: Decimal | None = None
    total_energy_cost_sar: Decimal | None = None
    cost_per_m3_sar: Decimal | None = None

    # Recommendations - التوصيات
    recommendations_en: list[str] = field(default_factory=list)
    recommendations_ar: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "report_id": self.id,
            "report_type": "FARM_WATER_SUMMARY",
            "report_type_ar": "ملخص مياه المزرعة",
            "tenant_id": self.tenant_id,
            "farm_id": self.farm_id,
            "period": self.report_period.to_dict(),
            "generated_at": self.generated_at.isoformat(),
            "farm_overview": {
                "name": self.farm_name,
                "name_ar": self.farm_name_ar,
                "total_area_ha": self.total_area_ha,
                "irrigated_area_ha": self.irrigated_area_ha,
                "active_fields": self.active_fields,
                "crops": self.crops,
                "crops_ar": self.crops_ar,
            },
            "water_sources": {
                "total": self.total_sources,
                "active": self.active_sources,
                "total_capacity_m3": self.total_capacity_m3,
                "available_capacity_m3": self.available_capacity_m3,
            },
            "water_allocation": {
                "total_m3": self.total_allocation_m3,
                "used_m3": self.used_allocation_m3,
                "remaining_m3": self.remaining_allocation_m3,
                "utilization_percent": self.allocation_utilization_percent,
            },
            "consumption": self.consumption.to_dict(),
            "efficiency": {
                "avg_application_efficiency": self.avg_application_efficiency,
                "avg_distribution_uniformity": self.avg_distribution_uniformity,
                "water_productivity_kg_m3": self.water_productivity_kg_m3,
                "economic_productivity_sar_m3": self.economic_productivity_sar_m3,
            },
            "water_quality": {
                "tests_count": self.quality_tests_count,
                "class_distribution": self.quality_class_distribution,
            },
            "compliance": {
                "overall_status": self.overall_compliance.value,
                "issues_count": self.compliance_issues_count,
                "critical_issues": self.critical_issues_count,
            },
            "trends": {
                "consumption": self.consumption_trend,
                "consumption_ar": self.consumption_trend_ar,
                "change_percent": self.consumption_change_percent,
            },
            "costs": {
                "total_water_sar": (float(self.total_water_cost_sar) if self.total_water_cost_sar else None),
                "total_energy_sar": (float(self.total_energy_cost_sar) if self.total_energy_cost_sar else None),
                "per_m3_sar": (float(self.cost_per_m3_sar) if self.cost_per_m3_sar else None),
            },
            "recommendations": {
                "en": self.recommendations_en,
                "ar": self.recommendations_ar,
            },
        }


# =============================================================================
# Report Generator - مولد التقارير
# =============================================================================


class WaterReportGenerator:
    """
    Water Report Generator - مولد تقارير المياه

    Generates various water management reports for regulatory
    compliance and internal analysis.
    """

    def __init__(self, tenant_id: str):
        """Initialize report generator for tenant"""
        self.tenant_id = tenant_id
        self.standards = SaudiWaterStandards()

    def generate_mewa_report(
        self,
        farm_id: str,
        period: ReportPeriod,
        sources: list[WaterSource],
        water_rights: list[WaterRight],
        consumption_records: list[WaterConsumptionRecord],
        quality_tests: list[WaterQualityTest],
        farm_info: dict[str, Any] | None = None,
    ) -> MEWAComplianceReport:
        """
        Generate MEWA quarterly compliance report.
        إنشاء تقرير الامتثال الربع سنوي لوزارة البيئة
        """
        report = MEWAComplianceReport(
            id=str(uuid.uuid4()),
            tenant_id=self.tenant_id,
            farm_id=farm_id,
            report_period=period,
            generated_at=datetime.now(UTC),
        )

        # Set farm information
        if farm_info:
            report.farm_name = farm_info.get("name", "")
            report.farm_name_ar = farm_info.get("name_ar", "")
            report.farm_license_number = farm_info.get("license_number", "")
            report.governorate = farm_info.get("governorate", "")
            report.governorate_ar = farm_info.get("governorate_ar", "")
            report.region = farm_info.get("region", "")
            report.region_ar = farm_info.get("region_ar", "")
            report.total_area_ha = farm_info.get("total_area_ha", 0.0)

        # Process sources
        report.sources = sources
        report.total_sources = len(sources)
        report.wells_count = sum(
            1 for s in sources if s.source_type in (WaterSourceType.WELL, WaterSourceType.ARTESIAN_WELL)
        )
        report.other_sources_count = report.total_sources - report.wells_count

        # Metering compliance
        report.metered_sources_count = sum(1 for s in sources if s.has_meter)
        report.unmetered_sources_count = report.total_sources - report.metered_sources_count

        # Check metering compliance (wells deeper than 50m require meters)
        deep_wells_without_meters = [
            s
            for s in sources
            if s.source_type in (WaterSourceType.WELL, WaterSourceType.ARTESIAN_WELL)
            and s.well_depth_m
            and s.well_depth_m > self.standards.METER_REQUIRED_WELL_DEPTH_M
            and not s.has_meter
        ]
        report.metering_compliance = len(deep_wells_without_meters) == 0

        if not report.metering_compliance:
            report.compliance_issues.append(
                ComplianceIssue(
                    id=str(uuid.uuid4()),
                    issue_type="metering_non_compliance",
                    issue_type_ar="عدم الامتثال للقياس",
                    severity=AlertSeverity.HIGH,
                    description_en=f"{len(deep_wells_without_meters)} well(s) deeper than "
                    f"{self.standards.METER_REQUIRED_WELL_DEPTH_M}m lack required water meters",
                    description_ar=f"{len(deep_wells_without_meters)} بئر(آبار) أعمق من "
                    f"{self.standards.METER_REQUIRED_WELL_DEPTH_M}م تفتقر إلى عدادات المياه المطلوبة",
                    regulation_reference="MEWA Well Metering Regulation",
                    regulation_reference_ar="لائحة قياس الآبار لوزارة البيئة",
                )
            )

        # Process water rights
        report.total_allocated_m3 = sum(r.allocated_m3_year for r in water_rights)

        # Calculate period allocation based on period type
        period_fraction = period.days / 365
        report.total_allocated_m3_period = report.total_allocated_m3 * period_fraction

        # Process consumption
        consumption_summary = self._calculate_consumption_summary(consumption_records, period)
        report.consumption_summary = consumption_summary

        # Calculate allocation utilization
        if report.total_allocated_m3_period > 0:
            report.allocation_utilization_percent = (
                consumption_summary.total_m3 / report.total_allocated_m3_period
            ) * 100

        # Check for over-extraction
        if report.allocation_utilization_percent > 100:
            over_extraction = consumption_summary.total_m3 - report.total_allocated_m3_period
            report.compliance_issues.append(
                ComplianceIssue(
                    id=str(uuid.uuid4()),
                    issue_type="over_extraction",
                    issue_type_ar="استخراج مفرط",
                    severity=AlertSeverity.CRITICAL,
                    description_en=f"Water extraction exceeds allocation by {over_extraction:.0f} m3 "
                    f"({report.allocation_utilization_percent:.1f}% of allocation)",
                    description_ar=f"يتجاوز استخراج المياه التخصيص بمقدار {over_extraction:.0f} م3 "
                    f"({report.allocation_utilization_percent:.1f}% من التخصيص)",
                    regulation_reference="MEWA Water Allocation Regulation",
                    regulation_reference_ar="لائحة تخصيص المياه لوزارة البيئة",
                )
            )

        # Process quality tests
        report.quality_tests_count = len(quality_tests)
        if quality_tests:
            for test in quality_tests:
                if test.quality_class == WaterQualityClass.UNFIT:
                    report.quality_issues.append(f"Source {test.source_id}: Water unfit for irrigation")
                    report.quality_compliant = False

        # Set overall compliance status
        if any(i.severity == AlertSeverity.CRITICAL for i in report.compliance_issues):
            report.compliance_status = ComplianceStatus.NON_COMPLIANT
        elif report.compliance_issues:
            report.compliance_status = ComplianceStatus.WARNING
        else:
            report.compliance_status = ComplianceStatus.COMPLIANT

        return report

    def generate_well_extraction_report(
        self,
        well: WaterSource,
        period: ReportPeriod,
        consumption_records: list[WaterConsumptionRecord],
        water_right: WaterRight | None = None,
    ) -> WellExtractionReport:
        """
        Generate well extraction report.
        إنشاء تقرير استخراج البئر
        """
        report = WellExtractionReport(
            id=str(uuid.uuid4()),
            tenant_id=self.tenant_id,
            well_id=well.id,
            report_period=period,
            generated_at=datetime.now(UTC),
        )

        # Well information
        report.well_name = well.name
        report.well_name_ar = well.name_ar
        report.well_license_number = well.license_number or ""
        report.well_depth_m = well.well_depth_m or 0.0
        report.aquifer_name = well.aquifer_name or ""
        report.aquifer_name_ar = well.aquifer_name_ar or ""

        if well.location:
            report.latitude = well.location.lat
            report.longitude = well.location.lng
        report.governorate = well.governorate or ""
        report.region = well.region or ""

        # Licensed extraction
        report.licensed_extraction_m3_year = well.licensed_extraction_m3_year or 0.0
        report.licensed_extraction_m3_day = well.licensed_extraction_m3_day or 0.0

        # Calculate actual extraction from records
        well_records = [r for r in consumption_records if r.source_id == well.id]
        report.total_extraction_m3 = sum(r.volume_m3 for r in well_records)
        report.extraction_days = len(
            {r.period_start.date() if r.period_start else r.recorded_at.date() for r in well_records}
        )

        if report.extraction_days > 0:
            report.avg_daily_extraction_m3 = report.total_extraction_m3 / report.extraction_days

        # Calculate pump hours
        report.pump_hours = sum(r.duration_hours or 0 for r in well_records)

        # Daily max
        daily_totals: dict[date, float] = {}
        for r in well_records:
            day = r.period_start.date() if r.period_start else r.recorded_at.date()
            daily_totals[day] = daily_totals.get(day, 0) + r.volume_m3
        if daily_totals:
            report.max_daily_extraction_m3 = max(daily_totals.values())

        # Year-to-date
        report.ytd_extraction_m3 = well.total_extracted_m3_ytd
        if report.licensed_extraction_m3_year > 0:
            report.ytd_remaining_m3 = max(0, report.licensed_extraction_m3_year - report.ytd_extraction_m3)
            report.ytd_utilization_percent = (report.ytd_extraction_m3 / report.licensed_extraction_m3_year) * 100

        # Water levels
        report.static_water_level_start_m = well.static_water_level_m
        report.static_water_level_end_m = well.static_water_level_m  # Would need historical data
        if well.static_water_level_m and well.dynamic_water_level_m:
            report.avg_drawdown_m = well.dynamic_water_level_m - well.static_water_level_m

        # Meter information
        if well.meter:
            report.meter_id = well.meter.id
            report.meter_certified = well.meter.is_certified
            report.meter_calibration_date = (
                well.meter.last_calibrated_at.date() if well.meter.last_calibrated_at else None
            )

        # Compliance check
        if report.ytd_utilization_percent > 100:
            report.compliance_status = ComplianceStatus.NON_COMPLIANT
            report.over_extraction_m3 = report.ytd_extraction_m3 - report.licensed_extraction_m3_year
            report.compliance_notes = "Annual extraction limit exceeded"
            report.compliance_notes_ar = "تم تجاوز حد الاستخراج السنوي"
        elif report.ytd_utilization_percent > 90:
            report.compliance_status = ComplianceStatus.WARNING
            report.compliance_notes = "Approaching annual extraction limit"
            report.compliance_notes_ar = "يقترب من حد الاستخراج السنوي"
        else:
            report.compliance_status = ComplianceStatus.COMPLIANT

        return report

    def generate_quality_report(
        self,
        farm_id: str,
        period: ReportPeriod,
        sources: list[WaterSource],
        quality_tests: list[WaterQualityTest],
    ) -> WaterQualityReport:
        """
        Generate water quality compliance report.
        إنشاء تقرير الامتثال لجودة المياه
        """
        report = WaterQualityReport(
            id=str(uuid.uuid4()),
            tenant_id=self.tenant_id,
            farm_id=farm_id,
            report_period=period,
            generated_at=datetime.now(UTC),
        )

        report.total_sources = len(sources)

        # Filter tests in period
        period_tests = [t for t in quality_tests if period.start_date <= t.tested_at.date() <= period.end_date]

        report.tests_conducted = len(period_tests)
        report.sources_tested = len({t.source_id for t in period_tests})

        # Count by quality class
        class_counts = {
            WaterQualityClass.CLASS_A: 0,
            WaterQualityClass.CLASS_B: 0,
            WaterQualityClass.CLASS_C: 0,
            WaterQualityClass.CLASS_D: 0,
            WaterQualityClass.UNFIT: 0,
        }

        for test in period_tests:
            class_counts[test.quality_class] += 1
            if test.quality_class != WaterQualityClass.UNFIT:
                report.tests_passed += 1
            else:
                report.tests_failed += 1

        report.class_a_sources = class_counts[WaterQualityClass.CLASS_A]
        report.class_b_sources = class_counts[WaterQualityClass.CLASS_B]
        report.class_c_sources = class_counts[WaterQualityClass.CLASS_C]
        report.class_d_sources = class_counts[WaterQualityClass.CLASS_D]
        report.unfit_sources = class_counts[WaterQualityClass.UNFIT]

        # Calculate averages
        ec_values = [t.electrical_conductivity_ds_m for t in period_tests if t.electrical_conductivity_ds_m]
        tds_values = [t.tds_ppm for t in period_tests if t.tds_ppm]
        ph_values = [t.ph for t in period_tests if t.ph]
        sar_values = [t.sar for t in period_tests if t.sar]

        if ec_values:
            report.avg_ec_ds_m = sum(ec_values) / len(ec_values)
        if tds_values:
            report.avg_tds_ppm = sum(tds_values) / len(tds_values)
        if ph_values:
            report.avg_ph = sum(ph_values) / len(ph_values)
        if sar_values:
            report.avg_sar = sum(sar_values) / len(sar_values)

        report.test_results = period_tests

        # Check compliance
        if report.unfit_sources > 0:
            report.compliance_status = ComplianceStatus.NON_COMPLIANT
            report.compliance_issues.append(
                ComplianceIssue(
                    id=str(uuid.uuid4()),
                    issue_type="unfit_water_sources",
                    issue_type_ar="مصادر مياه غير صالحة",
                    severity=AlertSeverity.CRITICAL,
                    description_en=f"{report.unfit_sources} source(s) have water unfit for irrigation",
                    description_ar=f"{report.unfit_sources} مصدر(مصادر) لديها مياه غير صالحة للري",
                )
            )

        # Generate recommendations
        if report.avg_ec_ds_m and report.avg_ec_ds_m > self.standards.EC_CLASS_B_MAX:
            report.recommendations_en.append("Consider blending water sources or treating water to reduce salinity")
            report.recommendations_ar.append("فكر في خلط مصادر المياه أو معالجة المياه لتقليل الملوحة")

        if report.sources_tested < report.total_sources:
            report.recommendations_en.append(
                f"Test remaining {report.total_sources - report.sources_tested} "
                "water sources for comprehensive quality assessment"
            )
            report.recommendations_ar.append(
                f"اختبر المصادر المتبقية البالغ عددها {report.total_sources - report.sources_tested} لتقييم شامل للجودة"
            )

        return report

    def generate_farm_summary_report(
        self,
        farm_id: str,
        period: ReportPeriod,
        sources: list[WaterSource],
        allocations: list[WaterAllocation],
        consumption_records: list[WaterConsumptionRecord],
        quality_tests: list[WaterQualityTest],
        farm_info: dict[str, Any] | None = None,
        efficiency_metrics: dict[str, Any] | None = None,
    ) -> FarmWaterSummaryReport:
        """
        Generate comprehensive farm water summary report.
        إنشاء تقرير ملخص مياه المزرعة الشامل
        """
        report = FarmWaterSummaryReport(
            id=str(uuid.uuid4()),
            tenant_id=self.tenant_id,
            farm_id=farm_id,
            report_period=period,
            generated_at=datetime.now(UTC),
        )

        # Farm info
        if farm_info:
            report.farm_name = farm_info.get("name", "")
            report.farm_name_ar = farm_info.get("name_ar", "")
            report.total_area_ha = farm_info.get("total_area_ha", 0.0)
            report.irrigated_area_ha = farm_info.get("irrigated_area_ha", 0.0)
            report.active_fields = farm_info.get("active_fields", 0)
            report.crops = farm_info.get("crops", [])
            report.crops_ar = farm_info.get("crops_ar", [])

        # Water sources
        report.total_sources = len(sources)
        report.active_sources = sum(1 for s in sources if s.status == WaterSourceStatus.ACTIVE)
        report.total_capacity_m3 = sum(s.max_capacity_m3 or 0 for s in sources)
        report.available_capacity_m3 = sum(s.current_level_m3 or 0 for s in sources)

        # Allocations
        report.total_allocation_m3 = sum(a.allocated_m3 for a in allocations)
        report.used_allocation_m3 = sum(a.consumed_m3 for a in allocations)
        report.remaining_allocation_m3 = sum(a.remaining_m3 for a in allocations)
        if report.total_allocation_m3 > 0:
            report.allocation_utilization_percent = (report.used_allocation_m3 / report.total_allocation_m3) * 100

        # Consumption
        report.consumption = self._calculate_consumption_summary(consumption_records, period)

        # Efficiency
        if efficiency_metrics:
            report.avg_application_efficiency = efficiency_metrics.get("avg_application_efficiency")
            report.avg_distribution_uniformity = efficiency_metrics.get("avg_distribution_uniformity")
            report.water_productivity_kg_m3 = efficiency_metrics.get("water_productivity_kg_m3")
            report.economic_productivity_sar_m3 = efficiency_metrics.get("economic_productivity_sar_m3")

        # Quality
        report.quality_tests_count = len(quality_tests)
        quality_dist: dict[str, int] = {}
        for test in quality_tests:
            class_name = test.quality_class.value
            quality_dist[class_name] = quality_dist.get(class_name, 0) + 1
        report.quality_class_distribution = quality_dist

        # Compliance
        compliance_issues = []

        # Check allocation compliance
        if report.allocation_utilization_percent > 100:
            compliance_issues.append("over_allocation")
            report.critical_issues_count += 1

        # Check license validity
        expired_sources = [s for s in sources if not s.is_license_valid]
        if expired_sources:
            compliance_issues.append(f"{len(expired_sources)}_expired_licenses")
            report.critical_issues_count += len(expired_sources)

        report.compliance_issues_count = len(compliance_issues)
        if report.critical_issues_count > 0:
            report.overall_compliance = ComplianceStatus.NON_COMPLIANT
        elif compliance_issues:
            report.overall_compliance = ComplianceStatus.WARNING
        else:
            report.overall_compliance = ComplianceStatus.COMPLIANT

        # Generate recommendations
        self._generate_summary_recommendations(report)

        return report

    def _calculate_consumption_summary(
        self,
        records: list[WaterConsumptionRecord],
        period: ReportPeriod,
    ) -> ConsumptionSummary:
        """Calculate consumption summary from records"""
        summary = ConsumptionSummary()

        # Filter records in period
        period_records = [
            r for r in records if r.period_start and period.start_date <= r.period_start.date() <= period.end_date
        ]

        summary.total_m3 = sum(r.volume_m3 for r in period_records)

        # By purpose
        for r in period_records:
            if r.purpose == "irrigation":
                summary.irrigation_m3 += r.volume_m3
            elif r.purpose == "livestock":
                summary.livestock_m3 += r.volume_m3
            elif r.purpose == "domestic":
                summary.domestic_m3 += r.volume_m3
            elif r.purpose == "processing":
                summary.processing_m3 += r.volume_m3
            else:
                summary.other_m3 += r.volume_m3

        # By source
        for r in period_records:
            summary.by_source[r.source_id] = summary.by_source.get(r.source_id, 0) + r.volume_m3

        # By field
        for r in period_records:
            if r.field_id:
                summary.by_field[r.field_id] = summary.by_field.get(r.field_id, 0) + r.volume_m3

        # By crop
        for r in period_records:
            if r.crop_type:
                summary.by_crop[r.crop_type] = summary.by_crop.get(r.crop_type, 0) + r.volume_m3

        # Daily statistics
        daily_totals: dict[date, float] = {}
        for r in period_records:
            if r.period_start:
                day = r.period_start.date()
                daily_totals[day] = daily_totals.get(day, 0) + r.volume_m3

        if daily_totals:
            summary.avg_daily_m3 = sum(daily_totals.values()) / len(daily_totals)
            summary.max_daily_m3 = max(daily_totals.values())
            summary.min_daily_m3 = min(daily_totals.values())

        return summary

    def _generate_summary_recommendations(self, report: FarmWaterSummaryReport) -> None:
        """Generate recommendations for farm summary report"""
        # Efficiency recommendations
        if report.avg_application_efficiency and report.avg_application_efficiency < 75:
            report.recommendations_en.append(
                "Irrigation efficiency is below target. Consider system "
                "maintenance or upgrade to improve water use efficiency."
            )
            report.recommendations_ar.append(
                "كفاءة الري أقل من الهدف. فكر في صيانة النظام أو الترقية لتحسين كفاءة استخدام المياه."
            )

        # Allocation recommendations
        if report.allocation_utilization_percent > 90:
            report.recommendations_en.append(
                "Water allocation usage is high. Plan irrigation carefully for the remaining period."
            )
            report.recommendations_ar.append("استخدام تخصيص المياه مرتفع. خطط للري بعناية للفترة المتبقية.")

        # Quality recommendations
        if "unfit" in report.quality_class_distribution:
            unfit_count = report.quality_class_distribution.get("unfit", 0)
            if unfit_count > 0:
                report.recommendations_en.append(
                    f"Address {unfit_count} water source(s) with quality issues. "
                    "Consider treatment or alternative sources."
                )
                report.recommendations_ar.append(
                    f"عالج {unfit_count} مصدر(مصادر) مياه بها مشاكل جودة. فكر في المعالجة أو مصادر بديلة."
                )

        # Conservation recommendations
        report.recommendations_en.append(
            "Continue monitoring water usage and implement water-saving "
            "practices such as mulching and deficit irrigation where appropriate."
        )
        report.recommendations_ar.append(
            "استمر في مراقبة استخدام المياه وتنفيذ ممارسات توفير المياه مثل التغطية والري الناقص حيثما كان ذلك مناسباً."
        )


# =============================================================================
# Report Scheduler - مجدول التقارير
# =============================================================================


class WaterReportScheduler:
    """
    Water Report Scheduler - مجدول تقارير المياه

    Manages scheduled report generation for regulatory compliance.
    """

    def __init__(self, tenant_id: str):
        """Initialize scheduler"""
        self.tenant_id = tenant_id
        self.standards = SaudiWaterStandards()

    def get_next_report_due_date(
        self,
        report_type: str,
        last_report_date: date | None = None,
    ) -> date:
        """
        Get next report due date based on report type.
        الحصول على تاريخ استحقاق التقرير التالي
        """
        today = date.today()

        if report_type == "mewa_quarterly":
            # Quarterly reports due end of month after quarter
            # Q1 (Jan-Mar) due April 30, Q2 (Apr-Jun) due July 31, etc.
            quarter = (today.month - 1) // 3
            next_quarter_month = ((quarter + 1) % 4) * 3 + 4  # 4, 7, 10, 1
            year = today.year if next_quarter_month > today.month else today.year + 1
            if next_quarter_month > 12:
                next_quarter_month = 1
                year += 1
            # Last day of the due month
            if next_quarter_month in (4, 6, 9, 11):
                day = 30
            elif next_quarter_month == 2:
                day = 28
            else:
                day = 31
            return date(year, next_quarter_month, day)

        elif report_type == "well_extraction":
            # Monthly reports due 15th of following month
            next_month = today.month + 1 if today.month < 12 else 1
            year = today.year if today.month < 12 else today.year + 1
            return date(year, next_month, 15)

        elif report_type == "water_quality":
            # Bi-annual reports (every 6 months)
            if last_report_date:
                months_diff = (today.year - last_report_date.year) * 12 + (today.month - last_report_date.month)
                if months_diff < 6:
                    # Calculate next due date
                    due_month = last_report_date.month + 6
                    year = last_report_date.year
                    if due_month > 12:
                        due_month -= 12
                        year += 1
                    return date(year, due_month, min(last_report_date.day, calendar.monthrange(year, due_month)[1]))

            # Default: due in 6 months
            due_month = today.month + 6
            year = today.year
            if due_month > 12:
                due_month -= 12
                year += 1
            return date(year, due_month, min(today.day, calendar.monthrange(year, due_month)[1]))

        else:
            # Default: monthly
            next_month = today.month + 1 if today.month < 12 else 1
            year = today.year if today.month < 12 else today.year + 1
            return date(year, next_month, 1)

    def get_overdue_reports(
        self,
        farm_id: str,
        report_history: dict[str, date],
    ) -> list[dict[str, Any]]:
        """
        Check for overdue reports.
        التحقق من التقارير المتأخرة
        """
        overdue: list[dict[str, Any]] = []
        today = date.today()

        report_types = [
            ("mewa_quarterly", "MEWA Quarterly Compliance", "تقرير الامتثال الربع سنوي"),
            ("well_extraction", "Well Extraction Monthly", "تقرير استخراج الآبار الشهري"),
            ("water_quality", "Water Quality Bi-annual", "تقرير جودة المياه نصف السنوي"),
        ]

        for report_type, name_en, name_ar in report_types:
            last_date = report_history.get(report_type)
            due_date = self.get_next_report_due_date(report_type, last_date)

            if due_date < today:
                days_overdue = (today - due_date).days
                overdue.append(
                    {
                        "report_type": report_type,
                        "name_en": name_en,
                        "name_ar": name_ar,
                        "due_date": due_date.isoformat(),
                        "days_overdue": days_overdue,
                        "severity": (AlertSeverity.CRITICAL.value if days_overdue > 30 else AlertSeverity.HIGH.value),
                    }
                )

        return overdue

    def create_report_period(
        self,
        period_type: str,
        reference_date: date | None = None,
    ) -> ReportPeriod:
        """
        Create a report period based on type.
        إنشاء فترة تقرير بناءً على النوع
        """
        ref_date = reference_date or date.today()

        if period_type == "quarterly":
            # Get previous quarter
            quarter = (ref_date.month - 1) // 3
            if quarter == 0:
                start = date(ref_date.year - 1, 10, 1)
                end = date(ref_date.year - 1, 12, 31)
            else:
                start_month = (quarter - 1) * 3 + 1
                end_month = quarter * 3
                start = date(ref_date.year, start_month, 1)
                # Last day of end month
                if end_month in (4, 6, 9, 11):
                    end_day = 30
                elif end_month == 2:
                    end_day = 28
                else:
                    end_day = 31
                end = date(ref_date.year, end_month, end_day)

            return ReportPeriod(
                start_date=start,
                end_date=end,
                period_type="quarterly",
                period_type_ar="ربع سنوي",
            )

        elif period_type == "monthly":
            # Previous month
            if ref_date.month == 1:
                start = date(ref_date.year - 1, 12, 1)
                end = date(ref_date.year - 1, 12, 31)
            else:
                prev_month = ref_date.month - 1
                start = date(ref_date.year, prev_month, 1)
                if prev_month in (4, 6, 9, 11):
                    end_day = 30
                elif prev_month == 2:
                    end_day = 28
                else:
                    end_day = 31
                end = date(ref_date.year, prev_month, end_day)

            return ReportPeriod(
                start_date=start,
                end_date=end,
                period_type="monthly",
                period_type_ar="شهري",
            )

        elif period_type == "annual":
            # Previous year
            start = date(ref_date.year - 1, 1, 1)
            end = date(ref_date.year - 1, 12, 31)

            return ReportPeriod(
                start_date=start,
                end_date=end,
                period_type="annual",
                period_type_ar="سنوي",
            )

        else:
            # Default: last 30 days
            end = ref_date - timedelta(days=1)
            start = end - timedelta(days=29)

            return ReportPeriod(
                start_date=start,
                end_date=end,
                period_type="custom",
                period_type_ar="مخصص",
            )
