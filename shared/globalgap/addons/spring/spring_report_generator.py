"""
SPRING Report Generator
مولد تقارير SPRING

Generate bilingual (Arabic/English) SPRING compliance reports with water balance calculations,
efficiency recommendations, and PDF-ready formatting.

إنشاء تقارير امتثال SPRING ثنائية اللغة (عربي/إنجليزي) مع حسابات توازن المياه،
وتوصيات الكفاءة، والتنسيق الجاهز لـ PDF.
"""

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, Field

from .spring_checklist import (
    SPRING_CATEGORIES,
    calculate_spring_compliance,
)
from .water_metrics import (
    IrrigationEfficiency,
    RainfallHarvesting,
    WaterEfficiencyScore,
    WaterQualityTest,
    WaterSource,
    WaterUsageMetric,
    classify_water_efficiency,
)

# ==================== Water Balance Models ====================


class WaterBalanceCalculation(BaseModel):
    """
    Water balance calculation for a reporting period
    حساب توازن المياه لفترة التقرير
    """

    period_start: date = Field(
        ..., description="Period start date / تاريخ بداية الفترة"
    )
    period_end: date = Field(..., description="Period end date / تاريخ نهاية الفترة")
    farm_id: str = Field(..., description="Farm identifier / معرف المزرعة")

    # Inputs (المدخلات)
    irrigation_water_m3: float = Field(
        ..., ge=0, description="Irrigation water (m³) / مياه الري"
    )
    rainfall_m3: float = Field(0, ge=0, description="Rainfall (m³) / الأمطار")
    recycled_water_m3: float = Field(
        0, ge=0, description="Recycled water (m³) / المياه المعاد تدويرها"
    )
    total_input_m3: float = Field(
        ..., ge=0, description="Total input (m³) / المدخلات الكلية"
    )

    # Outputs (المخرجات)
    crop_evapotranspiration_m3: float = Field(
        ..., ge=0, description="Crop ET (m³) / التبخر النتح للمحصول"
    )
    runoff_m3: float = Field(
        0, ge=0, description="Surface runoff (m³) / الجريان السطحي"
    )
    deep_percolation_m3: float = Field(
        0, ge=0, description="Deep percolation (m³) / الترشح العميق"
    )
    evaporation_m3: float = Field(
        0, ge=0, description="Direct evaporation (m³) / التبخر المباشر"
    )
    total_output_m3: float = Field(
        ..., ge=0, description="Total output (m³) / المخرجات الكلية"
    )

    # Balance (التوازن)
    storage_change_m3: float = Field(
        ..., description="Storage change (m³) / تغيير التخزين"
    )
    balance_error_percent: float = Field(
        0, ge=0, description="Balance error (%) / خطأ التوازن"
    )

    # Efficiency (الكفاءة)
    beneficial_use_efficiency_percent: float = Field(
        ..., ge=0, le=100, description="Beneficial use (%) / الاستخدام المفيد"
    )
    water_productivity_kg_per_m3: float | None = Field(
        None, description="Water productivity (kg/m³) / إنتاجية المياه"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "period_start": "2024-10-01",
                "period_end": "2024-12-31",
                "farm_id": "FARM-YE-001",
                "irrigation_water_m3": 14500,
                "rainfall_m3": 450,
                "recycled_water_m3": 50,
                "total_input_m3": 15000,
                "crop_evapotranspiration_m3": 12500,
                "runoff_m3": 300,
                "deep_percolation_m3": 1800,
                "evaporation_m3": 400,
                "total_output_m3": 15000,
                "storage_change_m3": 0,
                "balance_error_percent": 0.5,
                "beneficial_use_efficiency_percent": 83.3,
                "water_productivity_kg_per_m3": 6.8,
            }
        }


class SpringReportSection(BaseModel):
    """
    Report section
    قسم التقرير
    """

    section_id: str = Field(..., description="Section identifier / معرف القسم")
    title_en: str = Field(..., description="Section title (English) / عنوان القسم")
    title_ar: str = Field(..., description="Section title (Arabic) / عنوان القسم")
    content_en: str = Field(..., description="Section content (English) / محتوى القسم")
    content_ar: str = Field(..., description="Section content (Arabic) / محتوى القسم")
    order: int = Field(..., description="Display order / ترتيب العرض")
    subsections: list["SpringReportSection"] = Field(
        default_factory=list, description="Subsections / الأقسام الفرعية"
    )


class SpringReport(BaseModel):
    """
    Complete SPRING compliance report
    تقرير امتثال SPRING الكامل
    """

    report_id: str = Field(..., description="Report identifier / معرف التقرير")
    generated_date: datetime = Field(
        default_factory=datetime.utcnow, description="Generation date / تاريخ الإنشاء"
    )
    report_period_start: date = Field(..., description="Period start / بداية الفترة")
    report_period_end: date = Field(..., description="Period end / نهاية الفترة")

    farm_id: str = Field(..., description="Farm identifier / معرف المزرعة")
    farm_name_en: str = Field(..., description="Farm name (English) / اسم المزرعة")
    farm_name_ar: str = Field(..., description="Farm name (Arabic) / اسم المزرعة")

    # Executive Summary
    executive_summary_en: str = Field(
        ..., description="Executive summary (EN) / الملخص التنفيذي"
    )
    executive_summary_ar: str = Field(
        ..., description="Executive summary (AR) / الملخص التنفيذي"
    )

    # Water Balance
    water_balance: WaterBalanceCalculation = Field(
        ..., description="Water balance / توازن المياه"
    )

    # Efficiency Score
    efficiency_score: WaterEfficiencyScore = Field(
        ..., description="Efficiency score / درجة الكفاءة"
    )

    # Compliance Assessment
    compliance_summary: dict[str, Any] = Field(
        ..., description="Compliance summary / ملخص الامتثال"
    )

    # Sections
    sections: list[SpringReportSection] = Field(
        default_factory=list, description="Report sections / أقسام التقرير"
    )

    # Recommendations
    recommendations_en: list[str] = Field(
        default_factory=list, description="Recommendations (EN) / التوصيات"
    )
    recommendations_ar: list[str] = Field(
        default_factory=list, description="Recommendations (AR) / التوصيات"
    )

    # Yemen-specific insights
    yemen_context_notes_en: str | None = Field(
        None, description="Yemen context (EN) / السياق اليمني"
    )
    yemen_context_notes_ar: str | None = Field(
        None, description="Yemen context (AR) / السياق اليمني"
    )

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
        }


# ==================== Report Generator Class ====================


class SpringReportGenerator:
    """
    Generate comprehensive SPRING compliance reports
    إنشاء تقارير امتثال SPRING الشاملة
    """

    def __init__(self, farm_id: str, farm_name_en: str, farm_name_ar: str):
        """
        Initialize report generator

        Args:
            farm_id: Farm identifier
            farm_name_en: Farm name in English
            farm_name_ar: Farm name in Arabic
        """
        self.farm_id = farm_id
        self.farm_name_en = farm_name_en
        self.farm_name_ar = farm_name_ar

    def generate_report(
        self,
        period_start: date,
        period_end: date,
        water_balance: WaterBalanceCalculation,
        efficiency_score: WaterEfficiencyScore,
        compliant_items: list[str],
        water_sources: list[WaterSource],
        usage_records: list[WaterUsageMetric],
        quality_tests: list[WaterQualityTest],
        efficiency_records: list[IrrigationEfficiency],
        rainfall_records: list[RainfallHarvesting] | None = None,
        include_yemen_context: bool = True,
    ) -> SpringReport:
        """
        Generate complete SPRING report
        إنشاء تقرير SPRING كامل

        Args:
            period_start: Reporting period start date
            period_end: Reporting period end date
            water_balance: Water balance calculation
            efficiency_score: Overall efficiency score
            compliant_items: List of compliant checklist item IDs
            water_sources: List of water sources
            usage_records: Water usage records
            quality_tests: Water quality test results
            efficiency_records: Irrigation efficiency records
            rainfall_records: Rainfall harvesting records (optional)
            include_yemen_context: Include Yemen-specific context

        Returns:
            Complete SPRING report
        """
        # Calculate compliance
        compliance_summary = calculate_spring_compliance(compliant_items)

        # Generate executive summary
        exec_summary_en, exec_summary_ar = self._generate_executive_summary(
            compliance_summary, efficiency_score, water_balance
        )

        # Generate report sections
        sections = self._generate_report_sections(
            water_sources,
            usage_records,
            quality_tests,
            efficiency_records,
            rainfall_records,
            compliance_summary,
        )

        # Generate recommendations
        recommendations_en, recommendations_ar = self._generate_recommendations(
            efficiency_score, compliance_summary, water_balance
        )

        # Generate Yemen context
        yemen_notes_en, yemen_notes_ar = None, None
        if include_yemen_context:
            yemen_notes_en, yemen_notes_ar = self._generate_yemen_context(
                water_balance, efficiency_score, usage_records
            )

        # Create report
        report = SpringReport(
            report_id=f"SPRING-{self.farm_id}-{period_end.strftime('%Y%m%d')}",
            report_period_start=period_start,
            report_period_end=period_end,
            farm_id=self.farm_id,
            farm_name_en=self.farm_name_en,
            farm_name_ar=self.farm_name_ar,
            executive_summary_en=exec_summary_en,
            executive_summary_ar=exec_summary_ar,
            water_balance=water_balance,
            efficiency_score=efficiency_score,
            compliance_summary=compliance_summary,
            sections=sections,
            recommendations_en=recommendations_en,
            recommendations_ar=recommendations_ar,
            yemen_context_notes_en=yemen_notes_en,
            yemen_context_notes_ar=yemen_notes_ar,
        )

        return report

    def _generate_executive_summary(
        self,
        compliance: dict[str, Any],
        efficiency: WaterEfficiencyScore,
        balance: WaterBalanceCalculation,
    ) -> tuple[str, str]:
        """Generate executive summary in both languages"""

        compliance_pct = compliance["overall_compliance_percentage"]
        efficiency_pct = efficiency.average_application_efficiency
        water_use = balance.total_input_m3

        summary_en = f"""
This SPRING compliance report covers the period from {balance.period_start} to {balance.period_end}
for {self.farm_name_en}.

Overall SPRING Compliance: {compliance_pct}% ({compliance['compliant_items']}/{compliance['total_items']} items)
Average Irrigation Efficiency: {efficiency_pct}%
Total Water Use: {water_use:,.0f} m³
Beneficial Use Efficiency: {balance.beneficial_use_efficiency_percent}%

The farm demonstrates {"excellent" if compliance_pct >= 90 else "good" if compliance_pct >= 75 else "acceptable"}
compliance with SPRING requirements. Key strengths include {efficiency.drip_irrigation_percentage}% drip irrigation
coverage and {efficiency.soil_moisture_monitoring_coverage}% soil moisture sensor coverage.
        """.strip()

        summary_ar = f"""
يغطي تقرير امتثال SPRING هذا الفترة من {balance.period_start} إلى {balance.period_end}
لـ {self.farm_name_ar}.

الامتثال الإجمالي لـ SPRING: {compliance_pct}% ({compliance['compliant_items']}/{compliance['total_items']} عنصر)
متوسط كفاءة الري: {efficiency_pct}%
إجمالي استخدام المياه: {water_use:,.0f} متر مكعب
كفاءة الاستخدام المفيد: {balance.beneficial_use_efficiency_percent}%

تُظهر المزرعة امتثالاً {"ممتاز" if compliance_pct >= 90 else "جيد" if compliance_pct >= 75 else "مقبول"}
لمتطلبات SPRING. تشمل نقاط القوة الرئيسية تغطية الري بالتنقيط بنسبة {efficiency.drip_irrigation_percentage}%
وتغطية أجهزة استشعار رطوبة التربة بنسبة {efficiency.soil_moisture_monitoring_coverage}%.
        """.strip()

        return summary_en, summary_ar

    def _generate_report_sections(
        self,
        water_sources: list[WaterSource],
        usage_records: list[WaterUsageMetric],
        quality_tests: list[WaterQualityTest],
        efficiency_records: list[IrrigationEfficiency],
        rainfall_records: list[RainfallHarvesting] | None,
        compliance: dict[str, Any],
    ) -> list[SpringReportSection]:
        """Generate detailed report sections"""

        sections = []

        # Section 1: Water Sources
        sources_content_en = self._format_water_sources_section(water_sources, "en")
        sources_content_ar = self._format_water_sources_section(water_sources, "ar")

        sections.append(
            SpringReportSection(
                section_id="water_sources",
                title_en="Water Sources Assessment",
                title_ar="تقييم مصادر المياه",
                content_en=sources_content_en,
                content_ar=sources_content_ar,
                order=1,
            )
        )

        # Section 2: Water Usage
        usage_content_en = self._format_water_usage_section(usage_records, "en")
        usage_content_ar = self._format_water_usage_section(usage_records, "ar")

        sections.append(
            SpringReportSection(
                section_id="water_usage",
                title_en="Water Usage Analysis",
                title_ar="تحليل استخدام المياه",
                content_en=usage_content_en,
                content_ar=usage_content_ar,
                order=2,
            )
        )

        # Section 3: Water Quality
        quality_content_en = self._format_water_quality_section(quality_tests, "en")
        quality_content_ar = self._format_water_quality_section(quality_tests, "ar")

        sections.append(
            SpringReportSection(
                section_id="water_quality",
                title_en="Water Quality Monitoring",
                title_ar="مراقبة جودة المياه",
                content_en=quality_content_en,
                content_ar=quality_content_ar,
                order=3,
            )
        )

        # Section 4: Irrigation Efficiency
        efficiency_content_en = self._format_efficiency_section(
            efficiency_records, "en"
        )
        efficiency_content_ar = self._format_efficiency_section(
            efficiency_records, "ar"
        )

        sections.append(
            SpringReportSection(
                section_id="irrigation_efficiency",
                title_en="Irrigation Efficiency",
                title_ar="كفاءة الري",
                content_en=efficiency_content_en,
                content_ar=efficiency_content_ar,
                order=4,
            )
        )

        # Section 5: Rainwater Harvesting (if applicable)
        if rainfall_records:
            rainfall_content_en = self._format_rainfall_section(rainfall_records, "en")
            rainfall_content_ar = self._format_rainfall_section(rainfall_records, "ar")

            sections.append(
                SpringReportSection(
                    section_id="rainwater_harvesting",
                    title_en="Rainwater Harvesting",
                    title_ar="حصاد مياه الأمطار",
                    content_en=rainfall_content_en,
                    content_ar=rainfall_content_ar,
                    order=5,
                )
            )

        # Section 6: Compliance Summary
        compliance_content_en = self._format_compliance_section(compliance, "en")
        compliance_content_ar = self._format_compliance_section(compliance, "ar")

        sections.append(
            SpringReportSection(
                section_id="compliance_summary",
                title_en="SPRING Compliance Summary",
                title_ar="ملخص امتثال SPRING",
                content_en=compliance_content_en,
                content_ar=compliance_content_ar,
                order=6,
            )
        )

        return sections

    def _format_water_sources_section(
        self, sources: list[WaterSource], lang: str
    ) -> str:
        """Format water sources section"""
        if lang == "en":
            content = f"Total Water Sources: {len(sources)}\n\n"
            for source in sources:
                content += f"- {source.name_en} ({source.source_type.value})\n"
                if source.legal_permit_number:
                    content += f"  Permit: {source.legal_permit_number}\n"
                if source.capacity_cubic_meters:
                    content += f"  Capacity: {source.capacity_cubic_meters:,.0f} m³\n"
                content += "\n"
        else:
            content = f"إجمالي مصادر المياه: {len(sources)}\n\n"
            for source in sources:
                content += f"- {source.name_ar} ({source.source_type.value})\n"
                if source.legal_permit_number:
                    content += f"  التصريح: {source.legal_permit_number}\n"
                if source.capacity_cubic_meters:
                    content += (
                        f"  السعة: {source.capacity_cubic_meters:,.0f} متر مكعب\n"
                    )
                content += "\n"

        return content

    def _format_water_usage_section(
        self, usage: list[WaterUsageMetric], lang: str
    ) -> str:
        """Format water usage section"""
        total_usage = sum(u.volume_cubic_meters for u in usage)
        total_area = sum(
            u.crop_area_hectares or 0 for u in usage if u.crop_area_hectares
        )

        if lang == "en":
            content = f"Total Water Usage: {total_usage:,.0f} m³\n"
            content += f"Total Irrigated Area: {total_area:.2f} hectares\n"
            if total_area > 0:
                content += f"Average Water Use: {total_usage/total_area:,.0f} m³/ha\n"
            content += f"\nTotal Usage Records: {len(usage)}\n"
        else:
            content = f"إجمالي استخدام المياه: {total_usage:,.0f} متر مكعب\n"
            content += f"المساحة المروية الكلية: {total_area:.2f} هكتار\n"
            if total_area > 0:
                content += f"متوسط استخدام المياه: {total_usage/total_area:,.0f} متر مكعب/هكتار\n"
            content += f"\nإجمالي سجلات الاستخدام: {len(usage)}\n"

        return content

    def _format_water_quality_section(
        self, tests: list[WaterQualityTest], lang: str
    ) -> str:
        """Format water quality section"""
        passing_tests = sum(1 for t in tests if t.meets_irrigation_standards)

        if lang == "en":
            content = f"Total Quality Tests: {len(tests)}\n"
            content += f"Tests Meeting Standards: {passing_tests}/{len(tests)}\n"
            content += (
                f"Compliance Rate: {(passing_tests/len(tests)*100):.1f}%\n"
                if len(tests) > 0
                else ""
            )
        else:
            content = f"إجمالي اختبارات الجودة: {len(tests)}\n"
            content += f"الاختبارات المطابقة للمعايير: {passing_tests}/{len(tests)}\n"
            content += (
                f"معدل الامتثال: {(passing_tests/len(tests)*100):.1f}%\n"
                if len(tests) > 0
                else ""
            )

        return content

    def _format_efficiency_section(
        self, records: list[IrrigationEfficiency], lang: str
    ) -> str:
        """Format efficiency section"""
        if not records:
            return (
                "No efficiency records available"
                if lang == "en"
                else "لا توجد سجلات كفاءة متاحة"
            )

        avg_efficiency = sum(r.application_efficiency_percent for r in records) / len(
            records
        )

        if lang == "en":
            content = f"Average Application Efficiency: {avg_efficiency:.1f}%\n"
            content += f"Efficiency Assessments: {len(records)}\n"
            level_en, _ = classify_water_efficiency(avg_efficiency)
            content += f"Performance Level: {level_en}\n"
        else:
            content = f"متوسط كفاءة التطبيق: {avg_efficiency:.1f}%\n"
            content += f"تقييمات الكفاءة: {len(records)}\n"
            _, level_ar = classify_water_efficiency(avg_efficiency)
            content += f"مستوى الأداء: {level_ar}\n"

        return content

    def _format_rainfall_section(
        self, records: list[RainfallHarvesting], lang: str
    ) -> str:
        """Format rainfall harvesting section"""
        total_collected = sum(r.collected_volume_m3 for r in records)

        if lang == "en":
            content = f"Total Rainwater Collected: {total_collected:,.0f} m³\n"
            content += f"Collection Events: {len(records)}\n"
        else:
            content = f"إجمالي مياه الأمطار المجمعة: {total_collected:,.0f} متر مكعب\n"
            content += f"أحداث التجميع: {len(records)}\n"

        return content

    def _format_compliance_section(self, compliance: dict[str, Any], lang: str) -> str:
        """Format compliance summary section"""
        if lang == "en":
            content = f"Overall Compliance: {compliance['overall_compliance_percentage']:.1f}%\n"
            content += f"Compliant Items: {compliance['compliant_items']}\n"
            content += f"Non-Compliant Items: {compliance['non_compliant_items']}\n\n"
            content += "Category Compliance:\n"
            for category, pct in compliance["category_compliance"].items():
                cat_info = SPRING_CATEGORIES.get(category, {})
                content += f"- {cat_info.get('name_en', category)}: {pct:.1f}%\n"
        else:
            content = f"الامتثال الإجمالي: {compliance['overall_compliance_percentage']:.1f}%\n"
            content += f"العناصر المطابقة: {compliance['compliant_items']}\n"
            content += f"العناصر غير المطابقة: {compliance['non_compliant_items']}\n\n"
            content += "امتثال الفئات:\n"
            for category, pct in compliance["category_compliance"].items():
                cat_info = SPRING_CATEGORIES.get(category, {})
                content += f"- {cat_info.get('name_ar', category)}: {pct:.1f}%\n"

        return content

    def _generate_recommendations(
        self,
        efficiency: WaterEfficiencyScore,
        compliance: dict[str, Any],
        balance: WaterBalanceCalculation,
    ) -> tuple[list[str], list[str]]:
        """Generate recommendations based on assessment"""

        recommendations_en = []
        recommendations_ar = []

        # Drip irrigation recommendation
        if efficiency.drip_irrigation_percentage < 70:
            recommendations_en.append(
                f"Increase drip irrigation coverage from {efficiency.drip_irrigation_percentage}% to at least 70% for high-value crops."
            )
            recommendations_ar.append(
                f"زيادة تغطية الري بالتنقيط من {efficiency.drip_irrigation_percentage}% إلى 70% على الأقل للمحاصيل ذات القيمة العالية."
            )

        # Soil moisture monitoring
        if efficiency.soil_moisture_monitoring_coverage < 50:
            recommendations_en.append(
                "Install soil moisture sensors to improve irrigation scheduling and reduce water waste."
            )
            recommendations_ar.append(
                "تركيب أجهزة استشعار رطوبة التربة لتحسين جدولة الري وتقليل هدر المياه."
            )

        # Rainwater harvesting
        if efficiency.rainwater_percentage < 5:
            recommendations_en.append(
                "Implement or expand rainwater harvesting systems to supplement irrigation water."
            )
            recommendations_ar.append(
                "تنفيذ أو توسيع أنظمة حصاد مياه الأمطار لتكملة مياه الري."
            )

        # Water quality testing
        if efficiency.water_quality_tests_conducted < 4:
            recommendations_en.append(
                "Increase water quality testing frequency to quarterly (minimum 4 tests per year)."
            )
            recommendations_ar.append(
                "زيادة تكرار اختبارات جودة المياه إلى فصلياً (4 اختبارات على الأقل سنوياً)."
            )

        # Efficiency improvement
        if efficiency.average_application_efficiency < 75:
            recommendations_en.append(
                "Improve irrigation system maintenance and uniformity to achieve >75% application efficiency."
            )
            recommendations_ar.append(
                "تحسين صيانة نظام الري والتوحيد لتحقيق كفاءة تطبيق >75%."
            )

        # Legal compliance
        if efficiency.sources_with_legal_permits < efficiency.total_water_sources:
            recommendations_en.append(
                "Obtain legal water extraction permits for all water sources."
            )
            recommendations_ar.append(
                "الحصول على تصاريح استخراج المياه القانونية لجميع مصادر المياه."
            )

        # Deep percolation
        if balance.deep_percolation_m3 / balance.total_input_m3 > 0.15:
            recommendations_en.append(
                "Reduce deep percolation losses by improving irrigation scheduling and system design."
            )
            recommendations_ar.append(
                "تقليل خسائر الترشح العميق من خلال تحسين جدولة الري وتصميم النظام."
            )

        return recommendations_en, recommendations_ar

    def _generate_yemen_context(
        self,
        balance: WaterBalanceCalculation,
        efficiency: WaterEfficiencyScore,
        usage_records: list[WaterUsageMetric],
    ) -> tuple[str, str]:
        """Generate Yemen-specific context and insights"""

        context_en = f"""
YEMEN WATER SCARCITY CONTEXT:

Yemen faces severe water scarcity with groundwater levels declining 6-7 meters annually in major agricultural
basins like Sana'a. This farm's water management practices are critical for sustainable agriculture.

Farm Performance in Yemen Context:
- Water use per hectare: {efficiency.water_use_per_hectare_m3:.0f} m³/ha
- Irrigation efficiency: {efficiency.average_application_efficiency:.1f}%
- Drip irrigation coverage: {efficiency.drip_irrigation_percentage:.1f}%

Qat vs. Food Crops Consideration:
Food crop production (vegetables, fruits, grains) is prioritized over qat cultivation for water sustainability.
This farm's focus on food production contributes to national food security while conserving water resources.

Recommendations for Yemen Context:
- Continue groundwater monitoring to track aquifer depletion rates
- Maximize drip irrigation adoption to reduce water consumption
- Explore rainwater harvesting during monsoon season (April-September)
- Consider deficit irrigation strategies during water stress periods
- Participate in community water management initiatives
        """.strip()

        context_ar = f"""
سياق ندرة المياه في اليمن:

يواجه اليمن ندرة شديدة في المياه مع انخفاض مستويات المياه الجوفية 6-7 أمتار سنوياً في أحواض
زراعية رئيسية مثل صنعاء. ممارسات إدارة المياه في هذه المزرعة حاسمة للزراعة المستدامة.

أداء المزرعة في السياق اليمني:
- استخدام المياه لكل هكتار: {efficiency.water_use_per_hectare_m3:.0f} متر مكعب/هكتار
- كفاءة الري: {efficiency.average_application_efficiency:.1f}%
- تغطية الري بالتنقيط: {efficiency.drip_irrigation_percentage:.1f}%

اعتبارات القات مقابل محاصيل الغذاء:
يتم إعطاء الأولوية لإنتاج المحاصيل الغذائية (الخضروات، الفواكه، الحبوب) على زراعة القات
لاستدامة المياه. تركيز هذه المزرعة على إنتاج الغذاء يساهم في الأمن الغذائي الوطني مع الحفاظ
على موارد المياه.

توصيات للسياق اليمني:
- الاستمرار في مراقبة المياه الجوفية لتتبع معدلات استنزاف طبقة المياه الجوفية
- تعظيم اعتماد الري بالتنقيط لتقليل استهلاك المياه
- استكشاف حصاد مياه الأمطار خلال موسم الرياح الموسمية (أبريل-سبتمبر)
- النظر في استراتيجيات الري الناقص خلال فترات الإجهاد المائي
- المشاركة في مبادرات إدارة المياه المجتمعية
        """.strip()

        return context_en, context_ar


# ==================== Helper Functions ====================


def generate_spring_report(
    farm_id: str,
    farm_name_en: str,
    farm_name_ar: str,
    period_start: date,
    period_end: date,
    water_balance: WaterBalanceCalculation,
    efficiency_score: WaterEfficiencyScore,
    compliant_items: list[str],
    water_sources: list[WaterSource],
    usage_records: list[WaterUsageMetric],
    quality_tests: list[WaterQualityTest],
    efficiency_records: list[IrrigationEfficiency],
    rainfall_records: list[RainfallHarvesting] | None = None,
    include_yemen_context: bool = True,
) -> SpringReport:
    """
    Convenience function to generate SPRING report
    وظيفة ملائمة لإنشاء تقرير SPRING

    Args:
        farm_id: Farm identifier
        farm_name_en: Farm name (English)
        farm_name_ar: Farm name (Arabic)
        period_start: Report period start
        period_end: Report period end
        water_balance: Water balance calculation
        efficiency_score: Efficiency score
        compliant_items: List of compliant item IDs
        water_sources: Water sources list
        usage_records: Usage records
        quality_tests: Quality test results
        efficiency_records: Efficiency records
        rainfall_records: Rainfall harvesting records (optional)
        include_yemen_context: Include Yemen context

    Returns:
        SPRING compliance report
    """
    generator = SpringReportGenerator(farm_id, farm_name_en, farm_name_ar)

    return generator.generate_report(
        period_start=period_start,
        period_end=period_end,
        water_balance=water_balance,
        efficiency_score=efficiency_score,
        compliant_items=compliant_items,
        water_sources=water_sources,
        usage_records=usage_records,
        quality_tests=quality_tests,
        efficiency_records=efficiency_records,
        rainfall_records=rainfall_records,
        include_yemen_context=include_yemen_context,
    )


def export_report_to_text(report: SpringReport, language: str = "both") -> str:
    """
    Export report to plain text format
    تصدير التقرير إلى تنسيق نص عادي

    Args:
        report: SPRING report
        language: "en", "ar", or "both"

    Returns:
        Text formatted report
    """
    output = []

    def add_section(title: str, content: str):
        output.append(f"\n{'=' * 80}")
        output.append(title)
        output.append("=" * 80)
        output.append(content)

    if language in ["en", "both"]:
        add_section(
            "SPRING COMPLIANCE REPORT",
            f"""
Farm: {report.farm_name_en}
Report Period: {report.report_period_start} to {report.report_period_end}
Generated: {report.generated_date.strftime('%Y-%m-%d %H:%M')}
        """,
        )

        add_section("EXECUTIVE SUMMARY", report.executive_summary_en)

        for section in sorted(report.sections, key=lambda s: s.order):
            add_section(section.title_en, section.content_en)

        if report.recommendations_en:
            add_section(
                "RECOMMENDATIONS",
                "\n".join(f"• {r}" for r in report.recommendations_en),
            )

        if report.yemen_context_notes_en:
            add_section("YEMEN CONTEXT", report.yemen_context_notes_en)

    if language in ["ar", "both"]:
        if language == "both":
            output.append("\n\n" + "=" * 80)
            output.append("النسخة العربية / ARABIC VERSION")
            output.append("=" * 80)

        add_section(
            "تقرير امتثال SPRING",
            f"""
المزرعة: {report.farm_name_ar}
فترة التقرير: {report.report_period_start} إلى {report.report_period_end}
تاريخ الإنشاء: {report.generated_date.strftime('%Y-%m-%d %H:%M')}
        """,
        )

        add_section("الملخص التنفيذي", report.executive_summary_ar)

        for section in sorted(report.sections, key=lambda s: s.order):
            add_section(section.title_ar, section.content_ar)

        if report.recommendations_ar:
            add_section(
                "التوصيات", "\n".join(f"• {r}" for r in report.recommendations_ar)
            )

        if report.yemen_context_notes_ar:
            add_section("السياق اليمني", report.yemen_context_notes_ar)

    return "\n".join(output)
