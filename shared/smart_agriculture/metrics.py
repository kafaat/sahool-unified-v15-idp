"""
Smart Agriculture Operational Metrics | مقاييس عمليات الزراعة الذكية

Tracks and reports key operational metrics for smart agriculture systems
including management efficiency, labor optimization, and AI performance.

يتتبع ويقدم تقارير عن المقاييس التشغيلية الرئيسية لأنظمة الزراعة الذكية
بما في ذلك كفاءة الإدارة، تحسين العمالة، وأداء الذكاء الاصطناعي.

Key Metrics:
- Management radius: 10 acres -> 100+ acres per person
  نطاق الإدارة: 10 فدان -> 100+ فدان للشخص
- Labor cost reduction: 50-60%
  تخفيض تكلفة العمالة: 50-60%
- Failure response time: 24h -> 2h
  وقت الاستجابة للأعطال: 24 ساعة -> 2 ساعة
- Pest detection accuracy: 97.5%
  دقة اكتشاف الآفات: 97.5%
- Early detection: 3-5 days before manual
  الاكتشاف المبكر: 3-5 أيام قبل اليدوي
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


class MetricCategory(Enum):
    """
    Categories of operational metrics.
    فئات المقاييس التشغيلية.
    """

    EFFICIENCY = "efficiency"
    LABOR = "labor"
    RESPONSE = "response"
    AI_PERFORMANCE = "ai_performance"
    COST = "cost"
    QUALITY = "quality"


@dataclass
class MetricValue:
    """
    Individual metric value with context.
    قيمة مقياس فردي مع السياق.

    Attributes:
        name: Metric name | اسم المقياس
        name_ar: Arabic name | الاسم بالعربية
        value: Current value | القيمة الحالية
        unit: Measurement unit | وحدة القياس
        baseline: Traditional/baseline value | القيمة الأساسية/التقليدية
        improvement: Improvement percentage | نسبة التحسن
        category: Metric category | فئة المقياس
    """

    name: str
    name_ar: str
    value: float
    unit: str
    baseline: float
    improvement: float
    category: MetricCategory

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "name_ar": self.name_ar,
            "value": self.value,
            "unit": self.unit,
            "baseline": self.baseline,
            "improvement_pct": self.improvement,
            "category": self.category.value,
        }


@dataclass
class EfficiencyMetrics:
    """
    Management efficiency metrics.
    مقاييس كفاءة الإدارة.

    Attributes:
        management_radius_before: Acres per person before smart ag | الفدان/شخص قبل
        management_radius_after: Acres per person with smart ag | الفدان/شخص بعد
        improvement_factor: Improvement multiplier | معامل التحسن
    """

    management_radius_before: float = 10.0  # acres per person
    management_radius_after: float = 100.0  # acres per person
    improvement_factor: float = 10.0

    @property
    def improvement_percentage(self) -> float:
        """Calculate improvement percentage."""
        if self.management_radius_before > 0:
            return (self.management_radius_after - self.management_radius_before) / self.management_radius_before * 100
        return 0.0


@dataclass
class LaborMetrics:
    """
    Labor efficiency metrics.
    مقاييس كفاءة العمالة.

    Attributes:
        cost_reduction_min: Minimum labor cost reduction (%) | الحد الأدنى لتخفيض التكلفة
        cost_reduction_max: Maximum labor cost reduction (%) | الحد الأقصى لتخفيض التكلفة
        hours_saved_per_hectare: Labor hours saved per hectare | ساعات العمل الموفرة/هكتار
    """

    cost_reduction_min: float = 50.0
    cost_reduction_max: float = 60.0
    hours_saved_per_hectare: float = 15.0

    @property
    def average_reduction(self) -> float:
        """Get average cost reduction."""
        return (self.cost_reduction_min + self.cost_reduction_max) / 2


@dataclass
class ResponseMetrics:
    """
    Response time metrics.
    مقاييس وقت الاستجابة.

    Attributes:
        response_time_before: Response time before (hours) | وقت الاستجابة قبل
        response_time_after: Response time with smart ag (hours) | وقت الاستجابة بعد
    """

    response_time_before: float = 24.0  # hours
    response_time_after: float = 2.0  # hours

    @property
    def improvement_percentage(self) -> float:
        """Calculate response time improvement."""
        if self.response_time_before > 0:
            return (self.response_time_before - self.response_time_after) / self.response_time_before * 100
        return 0.0


@dataclass
class AIPerformanceMetrics:
    """
    AI system performance metrics.
    مقاييس أداء نظام الذكاء الاصطناعي.

    Attributes:
        pest_detection_accuracy: Pest detection accuracy (%) | دقة اكتشاف الآفات
        early_detection_days: Days of early detection vs manual | أيام الاكتشاف المبكر
        false_positive_rate: False positive rate (%) | معدل الإيجابية الخاطئة
        model_confidence: Average model confidence (%) | متوسط ثقة النموذج
    """

    pest_detection_accuracy: float = 97.5
    early_detection_days_min: float = 3.0
    early_detection_days_max: float = 5.0
    false_positive_rate: float = 2.5
    model_confidence: float = 95.0

    @property
    def early_detection_average(self) -> float:
        """Get average early detection days."""
        return (self.early_detection_days_min + self.early_detection_days_max) / 2


@dataclass
class CostMetrics:
    """
    Cost-related metrics.
    المقاييس المتعلقة بالتكلفة.

    Attributes:
        fertilizer_cost_reduction: Fertilizer cost reduction (yuan) | تخفيض تكلفة الأسمدة
        water_cost_reduction: Water cost reduction (yuan) | تخفيض تكلفة المياه
        energy_cost_reduction: Energy cost reduction (yuan) | تخفيض تكلفة الطاقة
        yield_value_increase: Yield value increase (yuan) | زيادة قيمة المحصول
    """

    fertilizer_cost_reduction: float = 200.0  # yuan per cycle
    water_cost_reduction: float = 150.0
    energy_cost_reduction: float = 100.0
    yield_value_increase: float = 500.0

    @property
    def total_savings(self) -> float:
        """Calculate total cost savings."""
        return self.fertilizer_cost_reduction + self.water_cost_reduction + self.energy_cost_reduction

    @property
    def net_benefit(self) -> float:
        """Calculate net benefit including yield increase."""
        return self.total_savings + self.yield_value_increase


@dataclass
class QualityMetrics:
    """
    Product quality metrics.
    مقاييس جودة المنتج.

    Attributes:
        grade_a_percentage: Percentage of Grade A produce (%) | نسبة المنتج من الدرجة أ
        rejection_rate: Product rejection rate (%) | معدل رفض المنتج
        shelf_life_improvement: Shelf life improvement (days) | تحسن مدة الصلاحية
    """

    grade_a_percentage: float = 85.0
    rejection_rate: float = 3.0
    shelf_life_improvement: float = 2.0


class OperationalMetrics:
    """
    Smart Agriculture Operational Metrics Tracker.
    متتبع مقاييس عمليات الزراعة الذكية.

    Tracks and reports key operational metrics for smart agriculture
    implementations with bilingual support.

    يتتبع ويقدم تقارير عن المقاييس التشغيلية الرئيسية
    لتطبيقات الزراعة الذكية مع دعم ثنائي اللغة.

    Key documented metrics:
    - Management radius: 10 acres -> 100+ acres per person
    - Labor cost reduction: 50-60%
    - Failure response time: 24h -> 2h
    - Pest detection accuracy: 97.5%
    - Early detection: 3-5 days before manual

    Example usage:
        metrics = OperationalMetrics()
        report = metrics.get_full_report()
        summary = metrics.get_summary_report(language="ar")
    """

    def __init__(self):
        """
        Initialize the operational metrics tracker.
        تهيئة متتبع المقاييس التشغيلية.
        """
        self.efficiency = EfficiencyMetrics()
        self.labor = LaborMetrics()
        self.response = ResponseMetrics()
        self.ai_performance = AIPerformanceMetrics()
        self.cost = CostMetrics()
        self.quality = QualityMetrics()

        self._tracking_start = datetime.now()
        self._custom_metrics: dict[str, MetricValue] = {}
        self._history: list[dict[str, Any]] = []

    @property
    def management_radius(self) -> tuple[float, float]:
        """
        Get management radius improvement.
        الحصول على تحسن نطاق الإدارة.

        Returns:
            tuple: (before, after) in acres per person
            10 acres -> 100+ acres per person
        """
        return (
            self.efficiency.management_radius_before,
            self.efficiency.management_radius_after,
        )

    @property
    def labor_cost_reduction(self) -> tuple[float, float]:
        """
        Get labor cost reduction range.
        الحصول على نطاق تخفيض تكلفة العمالة.

        Returns:
            tuple: (min, max) percentage
            50-60% reduction
        """
        return (
            self.labor.cost_reduction_min,
            self.labor.cost_reduction_max,
        )

    @property
    def failure_response_time(self) -> tuple[float, float]:
        """
        Get failure response time improvement.
        الحصول على تحسن وقت الاستجابة للأعطال.

        Returns:
            tuple: (before, after) in hours
            24h -> 2h
        """
        return (
            self.response.response_time_before,
            self.response.response_time_after,
        )

    @property
    def pest_detection_accuracy(self) -> float:
        """
        Get pest detection accuracy.
        الحصول على دقة اكتشاف الآفات.

        Returns:
            float: Accuracy percentage (97.5%)
        """
        return self.ai_performance.pest_detection_accuracy

    @property
    def early_detection_days(self) -> tuple[float, float]:
        """
        Get early detection days range.
        الحصول على نطاق أيام الاكتشاف المبكر.

        Returns:
            tuple: (min, max) days before manual detection
            3-5 days before manual
        """
        return (
            self.ai_performance.early_detection_days_min,
            self.ai_performance.early_detection_days_max,
        )

    def add_custom_metric(
        self,
        name: str,
        name_ar: str,
        value: float,
        unit: str,
        baseline: float,
        category: MetricCategory = MetricCategory.EFFICIENCY,
    ) -> None:
        """
        Add a custom metric.
        إضافة مقياس مخصص.

        Args:
            name: Metric name in English
            name_ar: Metric name in Arabic
            value: Current metric value
            unit: Measurement unit
            baseline: Baseline/traditional value
            category: Metric category
        """
        improvement = 0.0
        if baseline > 0 and value != baseline:
            improvement = abs((value - baseline) / baseline * 100)

        self._custom_metrics[name] = MetricValue(
            name=name,
            name_ar=name_ar,
            value=value,
            unit=unit,
            baseline=baseline,
            improvement=improvement,
            category=category,
        )

    def record_observation(
        self,
        metric_name: str,
        value: float,
        notes: str = "",
    ) -> None:
        """
        Record a metric observation for historical tracking.
        تسجيل ملاحظة مقياس للتتبع التاريخي.

        Args:
            metric_name: Name of the metric
            value: Observed value
            notes: Optional notes
        """
        self._history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "metric": metric_name,
                "value": value,
                "notes": notes,
            }
        )

    def get_metric_values(self) -> list[MetricValue]:
        """
        Get all metric values as MetricValue objects.
        الحصول على جميع قيم المقاييس ككائنات MetricValue.

        Returns:
            list: List of all metrics
        """
        metrics = [
            MetricValue(
                name="Management Radius",
                name_ar="نطاق الإدارة",
                value=self.efficiency.management_radius_after,
                unit="acres/person",
                baseline=self.efficiency.management_radius_before,
                improvement=self.efficiency.improvement_percentage,
                category=MetricCategory.EFFICIENCY,
            ),
            MetricValue(
                name="Labor Cost Reduction",
                name_ar="تخفيض تكلفة العمالة",
                value=self.labor.average_reduction,
                unit="%",
                baseline=0,
                improvement=self.labor.average_reduction,
                category=MetricCategory.LABOR,
            ),
            MetricValue(
                name="Response Time",
                name_ar="وقت الاستجابة",
                value=self.response.response_time_after,
                unit="hours",
                baseline=self.response.response_time_before,
                improvement=self.response.improvement_percentage,
                category=MetricCategory.RESPONSE,
            ),
            MetricValue(
                name="Pest Detection Accuracy",
                name_ar="دقة اكتشاف الآفات",
                value=self.ai_performance.pest_detection_accuracy,
                unit="%",
                baseline=80.0,  # Estimated manual accuracy
                improvement=17.5,
                category=MetricCategory.AI_PERFORMANCE,
            ),
            MetricValue(
                name="Early Detection",
                name_ar="الاكتشاف المبكر",
                value=self.ai_performance.early_detection_average,
                unit="days",
                baseline=0,
                improvement=100,  # 100% improvement as manual has 0 days early
                category=MetricCategory.AI_PERFORMANCE,
            ),
            MetricValue(
                name="Total Cost Savings",
                name_ar="إجمالي توفير التكلفة",
                value=self.cost.total_savings,
                unit="yuan",
                baseline=0,
                improvement=100,
                category=MetricCategory.COST,
            ),
            MetricValue(
                name="Grade A Produce",
                name_ar="المنتج من الدرجة أ",
                value=self.quality.grade_a_percentage,
                unit="%",
                baseline=70.0,
                improvement=21.4,
                category=MetricCategory.QUALITY,
            ),
        ]

        # Add custom metrics
        metrics.extend(self._custom_metrics.values())

        return metrics

    def get_full_report(self) -> dict[str, Any]:
        """
        Get comprehensive metrics report.
        الحصول على تقرير المقاييس الشامل.

        Returns:
            dict: Full metrics report
        """
        return {
            "efficiency": {
                "management_radius_before": self.efficiency.management_radius_before,
                "management_radius_after": self.efficiency.management_radius_after,
                "improvement_factor": self.efficiency.improvement_factor,
                "improvement_percentage": self.efficiency.improvement_percentage,
            },
            "labor": {
                "cost_reduction_min": self.labor.cost_reduction_min,
                "cost_reduction_max": self.labor.cost_reduction_max,
                "hours_saved_per_hectare": self.labor.hours_saved_per_hectare,
            },
            "response": {
                "time_before_hours": self.response.response_time_before,
                "time_after_hours": self.response.response_time_after,
                "improvement_percentage": self.response.improvement_percentage,
            },
            "ai_performance": {
                "pest_detection_accuracy": self.ai_performance.pest_detection_accuracy,
                "early_detection_days_min": self.ai_performance.early_detection_days_min,
                "early_detection_days_max": self.ai_performance.early_detection_days_max,
                "false_positive_rate": self.ai_performance.false_positive_rate,
                "model_confidence": self.ai_performance.model_confidence,
            },
            "cost": {
                "fertilizer_savings_yuan": self.cost.fertilizer_cost_reduction,
                "water_savings_yuan": self.cost.water_cost_reduction,
                "energy_savings_yuan": self.cost.energy_cost_reduction,
                "yield_increase_yuan": self.cost.yield_value_increase,
                "total_savings_yuan": self.cost.total_savings,
                "net_benefit_yuan": self.cost.net_benefit,
            },
            "quality": {
                "grade_a_percentage": self.quality.grade_a_percentage,
                "rejection_rate": self.quality.rejection_rate,
                "shelf_life_improvement_days": self.quality.shelf_life_improvement,
            },
            "custom_metrics": {name: metric.to_dict() for name, metric in self._custom_metrics.items()},
            "tracking_since": self._tracking_start.isoformat(),
            "observation_count": len(self._history),
        }

    def get_summary_report(self, language: str = "en") -> str:
        """
        Get formatted summary report.
        الحصول على تقرير ملخص منسق.

        Args:
            language: Output language ('en' or 'ar')

        Returns:
            str: Formatted summary
        """
        if language == "ar":
            return self._get_summary_ar()
        return self._get_summary_en()

    def _get_summary_en(self) -> str:
        """Generate English summary."""
        return f"""
Smart Agriculture Operational Metrics Report
=============================================

EFFICIENCY IMPROVEMENTS
-----------------------
Management Radius: {self.efficiency.management_radius_before} -> {self.efficiency.management_radius_after}+ acres/person
Improvement Factor: {self.efficiency.improvement_factor}x

LABOR OPTIMIZATION
------------------
Cost Reduction: {self.labor.cost_reduction_min}-{self.labor.cost_reduction_max}%
Hours Saved: {self.labor.hours_saved_per_hectare} hours/hectare

RESPONSE TIME
-------------
Before: {self.response.response_time_before}h
After: {self.response.response_time_after}h
Improvement: {self.response.improvement_percentage:.1f}%

AI PERFORMANCE
--------------
Pest Detection Accuracy: {self.ai_performance.pest_detection_accuracy}%
Early Detection: {self.ai_performance.early_detection_days_min}-{self.ai_performance.early_detection_days_max} days before manual
False Positive Rate: {self.ai_performance.false_positive_rate}%
Model Confidence: {self.ai_performance.model_confidence}%

COST SAVINGS (per cycle)
------------------------
Fertilizer: {self.cost.fertilizer_cost_reduction} yuan
Water: {self.cost.water_cost_reduction} yuan
Energy: {self.cost.energy_cost_reduction} yuan
Yield Increase: {self.cost.yield_value_increase} yuan
Total Benefit: {self.cost.net_benefit} yuan

QUALITY
-------
Grade A Produce: {self.quality.grade_a_percentage}%
Rejection Rate: {self.quality.rejection_rate}%
Shelf Life Improvement: +{self.quality.shelf_life_improvement} days
"""

    def _get_summary_ar(self) -> str:
        """Generate Arabic summary."""
        return f"""
تقرير مقاييس عمليات الزراعة الذكية
=============================================

تحسينات الكفاءة
-----------------------
نطاق الإدارة: {self.efficiency.management_radius_before} -> {self.efficiency.management_radius_after}+ فدان/شخص
معامل التحسن: {self.efficiency.improvement_factor}x

تحسين العمالة
------------------
تخفيض التكلفة: {self.labor.cost_reduction_min}-{self.labor.cost_reduction_max}%
الساعات الموفرة: {self.labor.hours_saved_per_hectare} ساعة/هكتار

وقت الاستجابة
-------------
قبل: {self.response.response_time_before} ساعة
بعد: {self.response.response_time_after} ساعة
التحسن: {self.response.improvement_percentage:.1f}%

أداء الذكاء الاصطناعي
--------------
دقة اكتشاف الآفات: {self.ai_performance.pest_detection_accuracy}%
الاكتشاف المبكر: {self.ai_performance.early_detection_days_min}-{self.ai_performance.early_detection_days_max} أيام قبل الطريقة اليدوية
معدل الإيجابية الخاطئة: {self.ai_performance.false_positive_rate}%
ثقة النموذج: {self.ai_performance.model_confidence}%

توفير التكاليف (لكل دورة)
------------------------
الأسمدة: {self.cost.fertilizer_cost_reduction} يوان
المياه: {self.cost.water_cost_reduction} يوان
الطاقة: {self.cost.energy_cost_reduction} يوان
زيادة المحصول: {self.cost.yield_value_increase} يوان
إجمالي الفائدة: {self.cost.net_benefit} يوان

الجودة
-------
المنتج من الدرجة أ: {self.quality.grade_a_percentage}%
معدل الرفض: {self.quality.rejection_rate}%
تحسن مدة الصلاحية: +{self.quality.shelf_life_improvement} أيام
"""

    def get_kpi_dashboard(self) -> dict[str, Any]:
        """
        Get KPI data formatted for dashboard display.
        الحصول على بيانات مؤشرات الأداء الرئيسية للعرض في لوحة القيادة.

        Returns:
            dict: Dashboard-ready KPI data
        """
        return {
            "kpis": [
                {
                    "id": "management_radius",
                    "title": "Management Radius",
                    "title_ar": "نطاق الإدارة",
                    "value": f"{self.efficiency.management_radius_after}+",
                    "unit": "acres/person",
                    "trend": "up",
                    "change": f"+{self.efficiency.improvement_factor}x",
                },
                {
                    "id": "labor_reduction",
                    "title": "Labor Cost Reduction",
                    "title_ar": "تخفيض تكلفة العمالة",
                    "value": f"{self.labor.average_reduction:.0f}",
                    "unit": "%",
                    "trend": "up",
                    "change": f"{self.labor.cost_reduction_min}-{self.labor.cost_reduction_max}%",
                },
                {
                    "id": "response_time",
                    "title": "Response Time",
                    "title_ar": "وقت الاستجابة",
                    "value": f"{self.response.response_time_after:.0f}",
                    "unit": "hours",
                    "trend": "down",
                    "change": f"-{self.response.improvement_percentage:.0f}%",
                },
                {
                    "id": "pest_accuracy",
                    "title": "Pest Detection",
                    "title_ar": "اكتشاف الآفات",
                    "value": f"{self.ai_performance.pest_detection_accuracy}",
                    "unit": "%",
                    "trend": "up",
                    "change": "+17.5%",
                },
                {
                    "id": "early_detection",
                    "title": "Early Detection",
                    "title_ar": "الاكتشاف المبكر",
                    "value": f"{self.ai_performance.early_detection_average:.0f}",
                    "unit": "days",
                    "trend": "up",
                    "change": "before manual",
                },
                {
                    "id": "cost_savings",
                    "title": "Total Savings",
                    "title_ar": "إجمالي التوفير",
                    "value": f"{self.cost.net_benefit:.0f}",
                    "unit": "yuan",
                    "trend": "up",
                    "change": "per cycle",
                },
            ],
            "updated_at": datetime.now().isoformat(),
        }

    def calculate_annual_impact(
        self,
        area_hectares: float,
        cycles_per_year: int = 2,
    ) -> dict[str, Any]:
        """
        Calculate annual impact for a given farm.
        حساب التأثير السنوي لمزرعة معينة.

        Args:
            area_hectares: Farm area in hectares
            cycles_per_year: Number of crop cycles per year

        Returns:
            dict: Annual impact metrics
        """
        area_acres = area_hectares * 2.471  # Convert to acres

        # Labor savings
        traditional_workers = area_acres / self.efficiency.management_radius_before
        smart_workers = area_acres / self.efficiency.management_radius_after
        workers_saved = traditional_workers - smart_workers

        # Cost savings (annual)
        annual_savings = self.cost.net_benefit * cycles_per_year * area_hectares

        # Time savings
        hours_saved = self.labor.hours_saved_per_hectare * area_hectares * cycles_per_year

        return {
            "farm_area_hectares": area_hectares,
            "cycles_per_year": cycles_per_year,
            "workers_saved": round(workers_saved, 1),
            "labor_hours_saved": round(hours_saved, 0),
            "annual_savings_yuan": round(annual_savings, 0),
            "response_time_improvement_hours": (self.response.response_time_before - self.response.response_time_after),
            "early_warning_days": self.ai_performance.early_detection_average,
        }

    def export_metrics(self, format: str = "json") -> str:
        """
        Export metrics in specified format.
        تصدير المقاييس بالتنسيق المحدد.

        Args:
            format: Export format ('json', 'csv', or 'markdown')

        Returns:
            str: Exported metrics data
        """
        import json as json_module

        if format == "json":
            return json_module.dumps(self.get_full_report(), indent=2)

        elif format == "csv":
            metrics = self.get_metric_values()
            lines = ["name,name_ar,value,unit,baseline,improvement,category"]
            for m in metrics:
                lines.append(f"{m.name},{m.name_ar},{m.value},{m.unit},{m.baseline},{m.improvement},{m.category.value}")
            return "\n".join(lines)

        elif format == "markdown":
            metrics = self.get_metric_values()
            lines = [
                "| Metric | Value | Unit | Improvement |",
                "|--------|-------|------|-------------|",
            ]
            for m in metrics:
                lines.append(f"| {m.name} | {m.value} | {m.unit} | {m.improvement:.1f}% |")
            return "\n".join(lines)

        return self.get_summary_report()
