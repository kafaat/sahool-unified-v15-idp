"""
Harvest Quality Grading Logic
=============================
منطق تصنيف جودة المحصول

Quality grading algorithms for grains, dates, and vegetables.
Supports moisture, protein content, sugar levels, and visual inspection.

خوارزميات تصنيف الجودة للحبوب والتمور والخضروات.
يدعم الرطوبة ومحتوى البروتين ومستويات السكر والفحص البصري.

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from .models import (
    BuyerMatch,
    BuyerRequirement,
    CropCategory,
    DateVariety,
    QualityGrade,
    QualityParameter,
    QualityStandard,
    QualityTestRecord,
    QualityTrendAnalysis,
    QualityTrendPoint,
    TestResult,
    TrendDirection,
    VegetableType,
)

# ─────────────────────────────────────────────────────────────────────────────
# Predefined Quality Standards - معايير الجودة المحددة مسبقاً
# ─────────────────────────────────────────────────────────────────────────────


def get_wheat_standard() -> QualityStandard:
    """
    Get wheat quality standard (based on SASO standards)
    الحصول على معيار جودة القمح (بناءً على معايير هيئة المواصفات السعودية)
    """
    return QualityStandard(
        id="wheat_standard_saso",
        name="Wheat Quality Standard",
        name_ar="معيار جودة القمح",
        crop_category=CropCategory.GRAIN,
        crop_type="wheat",
        crop_type_ar="قمح",
        parameters=[
            QualityParameter(
                parameter_name="moisture",
                parameter_name_ar="الرطوبة",
                unit="%",
                unit_ar="%",
                premium_min=0,
                premium_max=12.0,
                grade_a_min=12.0,
                grade_a_max=12.5,
                grade_b_min=12.5,
                grade_b_max=13.0,
                grade_c_min=13.0,
                grade_c_max=14.0,
                industrial_min=14.0,
                industrial_max=15.0,
                rejection_threshold=15.0,
                lower_is_better=True,
                weight=0.25,
                mandatory=True,
                description="Grain moisture content",
                description_ar="محتوى الرطوبة في الحبوب",
            ),
            QualityParameter(
                parameter_name="protein",
                parameter_name_ar="البروتين",
                unit="%",
                unit_ar="%",
                premium_min=14.0,
                premium_max=100,
                grade_a_min=12.5,
                grade_a_max=14.0,
                grade_b_min=11.0,
                grade_b_max=12.5,
                grade_c_min=9.5,
                grade_c_max=11.0,
                industrial_min=8.0,
                industrial_max=9.5,
                rejection_threshold=8.0,
                lower_is_better=False,
                weight=0.30,
                mandatory=True,
                description="Protein content (dry basis)",
                description_ar="محتوى البروتين (أساس جاف)",
            ),
            QualityParameter(
                parameter_name="test_weight",
                parameter_name_ar="الوزن النوعي",
                unit="kg/hl",
                unit_ar="كجم/هكتولتر",
                premium_min=80.0,
                premium_max=100,
                grade_a_min=78.0,
                grade_a_max=80.0,
                grade_b_min=76.0,
                grade_b_max=78.0,
                grade_c_min=74.0,
                grade_c_max=76.0,
                industrial_min=70.0,
                industrial_max=74.0,
                rejection_threshold=70.0,
                lower_is_better=False,
                weight=0.15,
                mandatory=True,
                description="Hectoliter weight",
                description_ar="وزن الهكتولتر",
            ),
            QualityParameter(
                parameter_name="foreign_matter",
                parameter_name_ar="الشوائب",
                unit="%",
                unit_ar="%",
                premium_min=0,
                premium_max=0.5,
                grade_a_min=0.5,
                grade_a_max=1.0,
                grade_b_min=1.0,
                grade_b_max=2.0,
                grade_c_min=2.0,
                grade_c_max=3.0,
                industrial_min=3.0,
                industrial_max=5.0,
                rejection_threshold=5.0,
                lower_is_better=True,
                weight=0.15,
                mandatory=True,
                description="Foreign material content",
                description_ar="محتوى المواد الغريبة",
            ),
            QualityParameter(
                parameter_name="damaged_kernels",
                parameter_name_ar="الحبوب التالفة",
                unit="%",
                unit_ar="%",
                premium_min=0,
                premium_max=1.0,
                grade_a_min=1.0,
                grade_a_max=2.0,
                grade_b_min=2.0,
                grade_b_max=4.0,
                grade_c_min=4.0,
                grade_c_max=6.0,
                industrial_min=6.0,
                industrial_max=10.0,
                rejection_threshold=10.0,
                lower_is_better=True,
                weight=0.15,
                mandatory=True,
                description="Damaged or sprouted kernels",
                description_ar="الحبوب التالفة أو النابتة",
            ),
        ],
        version="1.0",
        is_active=True,
        regulatory_body="SASO",
        regulatory_body_ar="هيئة المواصفات السعودية",
        standard_code="SASO 1467",
        applicable_regions=["SA", "YE"],
        description="Saudi Standard for Wheat Quality",
        description_ar="المعيار السعودي لجودة القمح",
    )


def get_barley_standard() -> QualityStandard:
    """
    Get barley quality standard
    الحصول على معيار جودة الشعير
    """
    return QualityStandard(
        id="barley_standard_saso",
        name="Barley Quality Standard",
        name_ar="معيار جودة الشعير",
        crop_category=CropCategory.GRAIN,
        crop_type="barley",
        crop_type_ar="شعير",
        parameters=[
            QualityParameter(
                parameter_name="moisture",
                parameter_name_ar="الرطوبة",
                unit="%",
                unit_ar="%",
                premium_min=0,
                premium_max=12.0,
                grade_a_min=12.0,
                grade_a_max=13.0,
                grade_b_min=13.0,
                grade_b_max=14.0,
                grade_c_min=14.0,
                grade_c_max=14.5,
                industrial_min=14.5,
                industrial_max=15.0,
                rejection_threshold=15.0,
                lower_is_better=True,
                weight=0.30,
                mandatory=True,
                description="Grain moisture content",
                description_ar="محتوى الرطوبة في الحبوب",
            ),
            QualityParameter(
                parameter_name="protein",
                parameter_name_ar="البروتين",
                unit="%",
                unit_ar="%",
                premium_min=12.0,
                premium_max=100,
                grade_a_min=10.5,
                grade_a_max=12.0,
                grade_b_min=9.0,
                grade_b_max=10.5,
                grade_c_min=7.5,
                grade_c_max=9.0,
                industrial_min=6.0,
                industrial_max=7.5,
                rejection_threshold=6.0,
                lower_is_better=False,
                weight=0.25,
                mandatory=True,
                description="Protein content",
                description_ar="محتوى البروتين",
            ),
            QualityParameter(
                parameter_name="test_weight",
                parameter_name_ar="الوزن النوعي",
                unit="kg/hl",
                unit_ar="كجم/هكتولتر",
                premium_min=68.0,
                premium_max=100,
                grade_a_min=65.0,
                grade_a_max=68.0,
                grade_b_min=62.0,
                grade_b_max=65.0,
                grade_c_min=58.0,
                grade_c_max=62.0,
                industrial_min=54.0,
                industrial_max=58.0,
                rejection_threshold=54.0,
                lower_is_better=False,
                weight=0.20,
                mandatory=True,
                description="Hectoliter weight",
                description_ar="وزن الهكتولتر",
            ),
            QualityParameter(
                parameter_name="foreign_matter",
                parameter_name_ar="الشوائب",
                unit="%",
                unit_ar="%",
                premium_min=0,
                premium_max=1.0,
                grade_a_min=1.0,
                grade_a_max=2.0,
                grade_b_min=2.0,
                grade_b_max=3.0,
                grade_c_min=3.0,
                grade_c_max=4.0,
                industrial_min=4.0,
                industrial_max=6.0,
                rejection_threshold=6.0,
                lower_is_better=True,
                weight=0.25,
                mandatory=True,
                description="Foreign material content",
                description_ar="محتوى المواد الغريبة",
            ),
        ],
        version="1.0",
        is_active=True,
        regulatory_body="SASO",
        regulatory_body_ar="هيئة المواصفات السعودية",
        standard_code="SASO 248",
        applicable_regions=["SA", "YE"],
        description="Saudi Standard for Barley Quality",
        description_ar="المعيار السعودي لجودة الشعير",
    )


def get_date_standard(variety: DateVariety = DateVariety.SUKKARI) -> QualityStandard:
    """
    Get date quality standard
    الحصول على معيار جودة التمور
    """
    return QualityStandard(
        id=f"date_standard_{variety.value}",
        name=f"Date Quality Standard - {variety.value.title()}",
        name_ar=f"معيار جودة التمور - {variety.value}",
        crop_category=CropCategory.DATE,
        crop_type="date",
        crop_type_ar="تمر",
        parameters=[
            QualityParameter(
                parameter_name="sugar_content",
                parameter_name_ar="نسبة السكر",
                unit="brix",
                unit_ar="بريكس",
                premium_min=70.0,
                premium_max=100,
                grade_a_min=65.0,
                grade_a_max=70.0,
                grade_b_min=55.0,
                grade_b_max=65.0,
                grade_c_min=45.0,
                grade_c_max=55.0,
                industrial_min=35.0,
                industrial_max=45.0,
                rejection_threshold=35.0,
                lower_is_better=False,
                weight=0.25,
                mandatory=True,
                description="Sugar content (Brix)",
                description_ar="محتوى السكر (بريكس)",
            ),
            QualityParameter(
                parameter_name="moisture",
                parameter_name_ar="الرطوبة",
                unit="%",
                unit_ar="%",
                premium_min=15.0,
                premium_max=20.0,
                grade_a_min=20.0,
                grade_a_max=23.0,
                grade_b_min=23.0,
                grade_b_max=26.0,
                grade_c_min=26.0,
                grade_c_max=30.0,
                industrial_min=30.0,
                industrial_max=35.0,
                rejection_threshold=35.0,
                lower_is_better=True,
                weight=0.20,
                mandatory=True,
                description="Moisture content (optimal for storage)",
                description_ar="محتوى الرطوبة (الأمثل للتخزين)",
            ),
            QualityParameter(
                parameter_name="size",
                parameter_name_ar="الحجم",
                unit="g",
                unit_ar="جرام",
                premium_min=15.0,
                premium_max=100,
                grade_a_min=12.0,
                grade_a_max=15.0,
                grade_b_min=9.0,
                grade_b_max=12.0,
                grade_c_min=6.0,
                grade_c_max=9.0,
                industrial_min=4.0,
                industrial_max=6.0,
                rejection_threshold=4.0,
                lower_is_better=False,
                weight=0.15,
                mandatory=True,
                description="Average fruit weight",
                description_ar="متوسط وزن الثمرة",
            ),
            QualityParameter(
                parameter_name="defects",
                parameter_name_ar="العيوب",
                unit="%",
                unit_ar="%",
                premium_min=0,
                premium_max=2.0,
                grade_a_min=2.0,
                grade_a_max=5.0,
                grade_b_min=5.0,
                grade_b_max=10.0,
                grade_c_min=10.0,
                grade_c_max=15.0,
                industrial_min=15.0,
                industrial_max=25.0,
                rejection_threshold=25.0,
                lower_is_better=True,
                weight=0.25,
                mandatory=True,
                description="Visual defects (spots, damage, insects)",
                description_ar="العيوب المرئية (بقع، تلف، حشرات)",
            ),
            QualityParameter(
                parameter_name="skin_separation",
                parameter_name_ar="انفصال القشرة",
                unit="%",
                unit_ar="%",
                premium_min=0,
                premium_max=2.0,
                grade_a_min=2.0,
                grade_a_max=5.0,
                grade_b_min=5.0,
                grade_b_max=10.0,
                grade_c_min=10.0,
                grade_c_max=15.0,
                industrial_min=15.0,
                industrial_max=20.0,
                rejection_threshold=20.0,
                lower_is_better=True,
                weight=0.15,
                mandatory=False,
                description="Skin separation percentage",
                description_ar="نسبة انفصال القشرة",
            ),
        ],
        version="1.0",
        is_active=True,
        regulatory_body="SASO",
        regulatory_body_ar="هيئة المواصفات السعودية",
        standard_code="SASO 655",
        applicable_regions=["SA", "YE"],
        description="Saudi Standard for Date Quality",
        description_ar="المعيار السعودي لجودة التمور",
    )


def get_vegetable_standard(vegetable_type: VegetableType) -> QualityStandard:
    """
    Get vegetable quality standard
    الحصول على معيار جودة الخضروات
    """
    # Common parameters for vegetables
    common_params = [
        QualityParameter(
            parameter_name="freshness",
            parameter_name_ar="النضارة",
            unit="score",
            unit_ar="درجة",
            premium_min=90.0,
            premium_max=100,
            grade_a_min=80.0,
            grade_a_max=90.0,
            grade_b_min=65.0,
            grade_b_max=80.0,
            grade_c_min=50.0,
            grade_c_max=65.0,
            industrial_min=35.0,
            industrial_max=50.0,
            rejection_threshold=35.0,
            lower_is_better=False,
            weight=0.25,
            mandatory=True,
            description="Visual freshness score (0-100)",
            description_ar="درجة النضارة البصرية (0-100)",
        ),
        QualityParameter(
            parameter_name="uniformity",
            parameter_name_ar="التجانس",
            unit="%",
            unit_ar="%",
            premium_min=95.0,
            premium_max=100,
            grade_a_min=85.0,
            grade_a_max=95.0,
            grade_b_min=70.0,
            grade_b_max=85.0,
            grade_c_min=55.0,
            grade_c_max=70.0,
            industrial_min=40.0,
            industrial_max=55.0,
            rejection_threshold=40.0,
            lower_is_better=False,
            weight=0.20,
            mandatory=True,
            description="Size and shape uniformity",
            description_ar="تجانس الحجم والشكل",
        ),
        QualityParameter(
            parameter_name="defects",
            parameter_name_ar="العيوب",
            unit="%",
            unit_ar="%",
            premium_min=0,
            premium_max=2.0,
            grade_a_min=2.0,
            grade_a_max=5.0,
            grade_b_min=5.0,
            grade_b_max=10.0,
            grade_c_min=10.0,
            grade_c_max=15.0,
            industrial_min=15.0,
            industrial_max=25.0,
            rejection_threshold=25.0,
            lower_is_better=True,
            weight=0.25,
            mandatory=True,
            description="Visual defects, blemishes, damage",
            description_ar="العيوب المرئية والخدوش والتلف",
        ),
        QualityParameter(
            parameter_name="pest_damage",
            parameter_name_ar="أضرار الآفات",
            unit="%",
            unit_ar="%",
            premium_min=0,
            premium_max=0.5,
            grade_a_min=0.5,
            grade_a_max=2.0,
            grade_b_min=2.0,
            grade_b_max=5.0,
            grade_c_min=5.0,
            grade_c_max=8.0,
            industrial_min=8.0,
            industrial_max=12.0,
            rejection_threshold=12.0,
            lower_is_better=True,
            weight=0.15,
            mandatory=True,
            description="Pest or insect damage",
            description_ar="أضرار الآفات أو الحشرات",
        ),
        QualityParameter(
            parameter_name="firmness",
            parameter_name_ar="الصلابة",
            unit="score",
            unit_ar="درجة",
            premium_min=85.0,
            premium_max=100,
            grade_a_min=70.0,
            grade_a_max=85.0,
            grade_b_min=55.0,
            grade_b_max=70.0,
            grade_c_min=40.0,
            grade_c_max=55.0,
            industrial_min=25.0,
            industrial_max=40.0,
            rejection_threshold=25.0,
            lower_is_better=False,
            weight=0.15,
            mandatory=False,
            description="Firmness/texture score",
            description_ar="درجة الصلابة/القوام",
        ),
    ]

    # Add tomato-specific parameter
    if vegetable_type == VegetableType.TOMATO:
        common_params.append(
            QualityParameter(
                parameter_name="brix",
                parameter_name_ar="بريكس",
                unit="brix",
                unit_ar="بريكس",
                premium_min=5.5,
                premium_max=100,
                grade_a_min=4.5,
                grade_a_max=5.5,
                grade_b_min=3.5,
                grade_b_max=4.5,
                grade_c_min=2.5,
                grade_c_max=3.5,
                industrial_min=2.0,
                industrial_max=2.5,
                rejection_threshold=2.0,
                lower_is_better=False,
                weight=0.15,
                mandatory=False,
                description="Sugar content (Brix)",
                description_ar="محتوى السكر (بريكس)",
            )
        )

    veg_name = vegetable_type.value.replace("_", " ").title()
    veg_name_ar = {
        VegetableType.TOMATO: "طماطم",
        VegetableType.CUCUMBER: "خيار",
        VegetableType.ONION: "بصل",
        VegetableType.POTATO: "بطاطس",
        VegetableType.CARROT: "جزر",
        VegetableType.EGGPLANT: "باذنجان",
        VegetableType.PEPPER: "فلفل",
        VegetableType.LETTUCE: "خس",
        VegetableType.ZUCCHINI: "كوسة",
        VegetableType.CABBAGE: "ملفوف",
        VegetableType.OTHER: "أخرى",
    }.get(vegetable_type, "خضروات")

    return QualityStandard(
        id=f"vegetable_standard_{vegetable_type.value}",
        name=f"Vegetable Quality Standard - {veg_name}",
        name_ar=f"معيار جودة الخضروات - {veg_name_ar}",
        crop_category=CropCategory.VEGETABLE,
        crop_type=vegetable_type.value,
        crop_type_ar=veg_name_ar,
        parameters=common_params,
        version="1.0",
        is_active=True,
        regulatory_body="SASO",
        regulatory_body_ar="هيئة المواصفات السعودية",
        standard_code="GSO 1016",
        applicable_regions=["SA", "YE"],
        description=f"GCC Standard for Fresh {veg_name} Quality",
        description_ar=f"معيار دول مجلس التعاون لجودة {veg_name_ar} الطازج",
    )


# Standard registry
QUALITY_STANDARDS: dict[str, QualityStandard] = {
    "wheat": get_wheat_standard(),
    "barley": get_barley_standard(),
    "date_sukkari": get_date_standard(DateVariety.SUKKARI),
    "date_khalas": get_date_standard(DateVariety.KHALAS),
    "date_ajwa": get_date_standard(DateVariety.AJWA),
    "tomato": get_vegetable_standard(VegetableType.TOMATO),
    "cucumber": get_vegetable_standard(VegetableType.CUCUMBER),
    "onion": get_vegetable_standard(VegetableType.ONION),
    "potato": get_vegetable_standard(VegetableType.POTATO),
}


# ─────────────────────────────────────────────────────────────────────────────
# Quality Grading Engine - محرك تصنيف الجودة
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class GradingResult:
    """Result of quality grading | نتيجة تصنيف الجودة"""

    overall_grade: QualityGrade
    grade_score: float  # 0-100 composite score
    confidence: float  # 0-1 confidence level

    # Individual parameter grades
    parameter_grades: dict[str, QualityGrade] = field(default_factory=dict)
    parameter_scores: dict[str, float] = field(default_factory=dict)

    # Limiting factor
    limiting_parameter: str = ""
    limiting_parameter_ar: str = ""

    # Summary
    passed_parameters: int = 0
    failed_parameters: int = 0
    total_parameters: int = 0

    # Grade justification
    justification: str = ""
    justification_ar: str = ""

    # Recommendations for improvement
    recommendations: list[str] = field(default_factory=list)
    recommendations_ar: list[str] = field(default_factory=list)


class QualityGradingEngine:
    """
    Engine for calculating quality grades
    محرك لحساب درجات الجودة
    """

    # Grade scores for weighted calculation
    GRADE_SCORES = {
        QualityGrade.PREMIUM: 100,
        QualityGrade.GRADE_A: 85,
        QualityGrade.GRADE_B: 70,
        QualityGrade.GRADE_C: 55,
        QualityGrade.INDUSTRIAL: 35,
        QualityGrade.REJECTED: 0,
    }

    # Arabic grade names
    GRADE_NAMES_AR = {
        QualityGrade.PREMIUM: "ممتاز",
        QualityGrade.GRADE_A: "درجة أولى",
        QualityGrade.GRADE_B: "درجة ثانية",
        QualityGrade.GRADE_C: "درجة ثالثة",
        QualityGrade.INDUSTRIAL: "صناعي",
        QualityGrade.REJECTED: "مرفوض",
    }

    def __init__(self, standard: QualityStandard | None = None):
        """Initialize grading engine with quality standard"""
        self.standard = standard

    def set_standard(self, standard: QualityStandard) -> None:
        """Set quality standard to use for grading"""
        self.standard = standard

    def get_standard_for_crop(self, crop_type: str) -> QualityStandard | None:
        """Get appropriate standard for crop type"""
        return QUALITY_STANDARDS.get(crop_type.lower())

    def calculate_grade(
        self,
        test_values: dict[str, float],
        standard: QualityStandard | None = None,
    ) -> GradingResult:
        """
        Calculate overall quality grade from test values

        Args:
            test_values: Dictionary of parameter_name -> measured_value
            standard: Quality standard to use (optional, uses engine's standard if not provided)

        Returns:
            GradingResult with overall grade and details
        """
        std = standard or self.standard
        if not std:
            raise ValueError("No quality standard provided")

        parameter_grades: dict[str, QualityGrade] = {}
        parameter_scores: dict[str, float] = {}
        weighted_sum = 0.0
        total_weight = 0.0
        passed = 0
        failed = 0
        limiting_grade = QualityGrade.PREMIUM
        limiting_param = ""
        limiting_param_ar = ""
        recommendations: list[str] = []
        recommendations_ar: list[str] = []

        for param in std.parameters:
            if param.parameter_name not in test_values:
                if param.mandatory:
                    # Missing mandatory parameter
                    parameter_grades[param.parameter_name] = QualityGrade.REJECTED
                    parameter_scores[param.parameter_name] = 0
                    failed += 1
                    recommendations.append(f"Missing required test: {param.parameter_name}")
                    recommendations_ar.append(f"اختبار مطلوب مفقود: {param.parameter_name_ar}")
                continue

            value = test_values[param.parameter_name]
            grade = param.get_grade_for_value(value)
            score = self.GRADE_SCORES[grade]

            parameter_grades[param.parameter_name] = grade
            parameter_scores[param.parameter_name] = score

            # Weighted sum
            weighted_sum += score * param.weight
            total_weight += param.weight

            # Track pass/fail
            if grade in [QualityGrade.REJECTED]:
                failed += 1
            else:
                passed += 1

            # Track limiting factor (lowest grade)
            grade_order = list(self.GRADE_SCORES.keys())
            if grade_order.index(grade) > grade_order.index(limiting_grade):
                limiting_grade = grade
                limiting_param = param.parameter_name
                limiting_param_ar = param.parameter_name_ar

            # Generate recommendations
            if grade in [QualityGrade.GRADE_C, QualityGrade.INDUSTRIAL]:
                if param.lower_is_better:
                    recommendations.append(
                        f"Reduce {param.parameter_name}: current {value}{param.unit}, "
                        f"target <{param.grade_b_max}{param.unit}"
                    )
                    recommendations_ar.append(
                        f"تقليل {param.parameter_name_ar}: الحالي {value}{param.unit_ar}، "
                        f"المستهدف <{param.grade_b_max}{param.unit_ar}"
                    )
                else:
                    recommendations.append(
                        f"Increase {param.parameter_name}: current {value}{param.unit}, "
                        f"target >{param.grade_b_min}{param.unit}"
                    )
                    recommendations_ar.append(
                        f"زيادة {param.parameter_name_ar}: الحالي {value}{param.unit_ar}، "
                        f"المستهدف >{param.grade_b_min}{param.unit_ar}"
                    )

        # Calculate composite score
        composite_score = weighted_sum / total_weight if total_weight > 0 else 0

        # Determine overall grade from composite score
        overall_grade = self._score_to_grade(composite_score)

        # But limit by the worst individual grade for mandatory parameters
        mandatory_grades = [
            parameter_grades.get(p.parameter_name, QualityGrade.PREMIUM)
            for p in std.parameters
            if p.mandatory and p.parameter_name in parameter_grades
        ]
        if mandatory_grades:
            worst_mandatory = max(mandatory_grades, key=lambda g: list(self.GRADE_SCORES.keys()).index(g))
            grade_order = list(self.GRADE_SCORES.keys())
            if grade_order.index(worst_mandatory) > grade_order.index(overall_grade):
                overall_grade = worst_mandatory

        # Calculate confidence
        confidence = self._calculate_confidence(
            total_parameters=len(std.parameters),
            tested_parameters=len(test_values),
            mandatory_tested=sum(1 for p in std.parameters if p.mandatory and p.parameter_name in test_values),
            mandatory_total=sum(1 for p in std.parameters if p.mandatory),
        )

        # Generate justification
        justification = (
            f"Grade {overall_grade.value} based on {passed} passed and {failed} failed tests. "
            f"Composite score: {composite_score:.1f}/100."
        )
        if limiting_param:
            justification += f" Limiting factor: {limiting_param}."

        justification_ar = (
            f"الدرجة {self.GRADE_NAMES_AR[overall_grade]} بناءً على {passed} اختبار ناجح و{failed} اختبار راسب. "
            f"الدرجة المركبة: {composite_score:.1f}/100."
        )
        if limiting_param_ar:
            justification_ar += f" العامل المحدد: {limiting_param_ar}."

        return GradingResult(
            overall_grade=overall_grade,
            grade_score=composite_score,
            confidence=confidence,
            parameter_grades=parameter_grades,
            parameter_scores=parameter_scores,
            limiting_parameter=limiting_param,
            limiting_parameter_ar=limiting_param_ar,
            passed_parameters=passed,
            failed_parameters=failed,
            total_parameters=len(std.parameters),
            justification=justification,
            justification_ar=justification_ar,
            recommendations=recommendations,
            recommendations_ar=recommendations_ar,
        )

    def _score_to_grade(self, score: float) -> QualityGrade:
        """Convert composite score to grade"""
        if score >= 92:
            return QualityGrade.PREMIUM
        elif score >= 77:
            return QualityGrade.GRADE_A
        elif score >= 62:
            return QualityGrade.GRADE_B
        elif score >= 45:
            return QualityGrade.GRADE_C
        elif score >= 20:
            return QualityGrade.INDUSTRIAL
        else:
            return QualityGrade.REJECTED

    def _calculate_confidence(
        self,
        total_parameters: int,
        tested_parameters: int,
        mandatory_tested: int,
        mandatory_total: int,
    ) -> float:
        """Calculate confidence in the grade"""
        if mandatory_total == 0 or total_parameters == 0:
            return 0.0

        # Mandatory coverage weight: 70%
        mandatory_coverage = mandatory_tested / mandatory_total

        # Optional coverage weight: 30%
        optional_total = total_parameters - mandatory_total
        optional_tested = tested_parameters - mandatory_tested
        optional_coverage = optional_tested / optional_total if optional_total > 0 else 1.0

        confidence = 0.7 * mandatory_coverage + 0.3 * optional_coverage
        return min(confidence, 1.0)

    def grade_test_record(self, test_record: QualityTestRecord) -> tuple[QualityTestRecord, GradingResult]:
        """
        Grade a complete test record and update it with results

        Args:
            test_record: Quality test record with test results

        Returns:
            Tuple of (updated test record, grading result)
        """
        # Determine standard from crop type
        standard = self.get_standard_for_crop(test_record.crop_type)
        if not standard:
            # Try with variety
            key = f"{test_record.crop_type}_{test_record.variety}".lower()
            standard = QUALITY_STANDARDS.get(key)

        if not standard:
            raise ValueError(f"No quality standard found for crop: {test_record.crop_type}")

        # Extract test values
        test_values: dict[str, float] = {}
        for result in test_record.test_results:
            test_values[result.parameter_name] = result.value

        # Calculate grade
        grading_result = self.calculate_grade(test_values, standard)

        # Update test record
        test_record.overall_grade = grading_result.overall_grade
        test_record.grade_score = grading_result.grade_score
        test_record.grade_confidence = grading_result.confidence
        test_record.standard_id = standard.id
        test_record.standard_name = standard.name
        test_record.standard_code = standard.standard_code
        test_record.updated_at = datetime.now(UTC)

        # Update summary metrics
        if "moisture" in test_values:
            test_record.moisture_percent = test_values["moisture"]
        if "protein" in test_values:
            test_record.protein_percent = test_values["protein"]
        if "sugar_content" in test_values or "brix" in test_values:
            test_record.sugar_brix = test_values.get("sugar_content", test_values.get("brix"))
        if "foreign_matter" in test_values:
            test_record.foreign_matter_percent = test_values["foreign_matter"]
        if "defects" in test_values:
            test_record.defect_percent = test_values["defects"]

        # Update individual test grades
        for result in test_record.test_results:
            if result.parameter_name in grading_result.parameter_grades:
                result.grade = grading_result.parameter_grades[result.parameter_name]
                result.result = (
                    TestResult.PASS
                    if result.grade not in [QualityGrade.REJECTED, QualityGrade.INDUSTRIAL]
                    else TestResult.FAIL
                )

        return test_record, grading_result


# ─────────────────────────────────────────────────────────────────────────────
# Buyer Matching - مطابقة المشترين
# ─────────────────────────────────────────────────────────────────────────────


class BuyerMatchingEngine:
    """
    Engine for matching harvest quality with buyer requirements
    محرك مطابقة جودة المحصول مع متطلبات المشترين
    """

    def __init__(self, buyer_requirements: list[BuyerRequirement] | None = None):
        """Initialize with list of buyer requirements"""
        self.requirements = buyer_requirements or []

    def add_requirement(self, requirement: BuyerRequirement) -> None:
        """Add a buyer requirement"""
        self.requirements.append(requirement)

    def find_matches(
        self,
        test_record: QualityTestRecord,
        quantity_kg: float,
        certifications: list[str] | None = None,
        min_match_score: float = 60.0,
    ) -> list[BuyerMatch]:
        """
        Find matching buyers for a harvest based on quality

        Args:
            test_record: Quality test record for the harvest
            quantity_kg: Available quantity in kg
            certifications: List of certification IDs the harvest has
            min_match_score: Minimum match score to include (0-100)

        Returns:
            List of BuyerMatch sorted by match_score descending
        """
        matches: list[BuyerMatch] = []
        certifications = certifications or []

        for req in self.requirements:
            # Skip inactive requirements
            if not req.is_valid():
                continue

            # Check crop type match
            if req.crop_type and req.crop_type.lower() != test_record.crop_type.lower():
                continue

            # Check variety if specified
            if req.acceptable_varieties and test_record.variety:
                if test_record.variety.lower() not in [v.lower() for v in req.acceptable_varieties]:
                    continue

            # Evaluate match
            match = self._evaluate_match(test_record, quantity_kg, certifications, req)

            if match.match_score >= min_match_score or match.is_eligible:
                matches.append(match)

        # Sort by match score (highest first)
        matches.sort(key=lambda m: m.match_score, reverse=True)

        return matches

    def _evaluate_match(
        self,
        test_record: QualityTestRecord,
        quantity_kg: float,
        certifications: list[str],
        requirement: BuyerRequirement,
    ) -> BuyerMatch:
        """Evaluate how well a harvest matches a buyer requirement"""
        score = 0.0
        max_score = 0.0
        unmet: list[str] = []
        unmet_ar: list[str] = []
        param_met: list[dict[str, Any]] = []

        # Check grade requirement (30 points)
        max_score += 30
        grade_met = requirement.matches_grade(test_record.overall_grade)
        if grade_met:
            score += 30
        else:
            unmet.append(f"Grade {test_record.overall_grade.value} below minimum {requirement.minimum_grade.value}")
            unmet_ar.append(
                f"الدرجة {test_record.overall_grade.value} أقل من الحد الأدنى {requirement.minimum_grade.value}"
            )

        # Check moisture (15 points)
        if requirement.max_moisture_percent is not None:
            max_score += 15
            actual_moisture = test_record.moisture_percent or 0
            if actual_moisture <= requirement.max_moisture_percent:
                score += 15
                param_met.append(
                    {
                        "parameter": "moisture",
                        "parameter_ar": "الرطوبة",
                        "required": f"<={requirement.max_moisture_percent}%",
                        "actual": f"{actual_moisture}%",
                        "met": True,
                    }
                )
            else:
                unmet.append(f"Moisture {actual_moisture}% exceeds max {requirement.max_moisture_percent}%")
                unmet_ar.append(f"الرطوبة {actual_moisture}% تتجاوز الحد الأقصى {requirement.max_moisture_percent}%")
                param_met.append(
                    {
                        "parameter": "moisture",
                        "parameter_ar": "الرطوبة",
                        "required": f"<={requirement.max_moisture_percent}%",
                        "actual": f"{actual_moisture}%",
                        "met": False,
                    }
                )

        # Check protein (15 points)
        if requirement.min_protein_percent is not None:
            max_score += 15
            actual_protein = test_record.protein_percent or 0
            if actual_protein >= requirement.min_protein_percent:
                score += 15
                param_met.append(
                    {
                        "parameter": "protein",
                        "parameter_ar": "البروتين",
                        "required": f">={requirement.min_protein_percent}%",
                        "actual": f"{actual_protein}%",
                        "met": True,
                    }
                )
            else:
                unmet.append(f"Protein {actual_protein}% below min {requirement.min_protein_percent}%")
                unmet_ar.append(f"البروتين {actual_protein}% أقل من الحد الأدنى {requirement.min_protein_percent}%")
                param_met.append(
                    {
                        "parameter": "protein",
                        "parameter_ar": "البروتين",
                        "required": f">={requirement.min_protein_percent}%",
                        "actual": f"{actual_protein}%",
                        "met": False,
                    }
                )

        # Check sugar/brix (15 points)
        if requirement.min_sugar_brix is not None:
            max_score += 15
            actual_sugar = test_record.sugar_brix or 0
            if actual_sugar >= requirement.min_sugar_brix:
                score += 15
            else:
                unmet.append(f"Sugar {actual_sugar} Brix below min {requirement.min_sugar_brix} Brix")
                unmet_ar.append(f"السكر {actual_sugar} بريكس أقل من الحد الأدنى {requirement.min_sugar_brix} بريكس")

        # Check quantity (15 points)
        max_score += 15
        quantity_met = True
        if requirement.min_quantity_kg and quantity_kg < requirement.min_quantity_kg:
            quantity_met = False
            unmet.append(f"Quantity {quantity_kg}kg below min {requirement.min_quantity_kg}kg")
            unmet_ar.append(f"الكمية {quantity_kg}كجم أقل من الحد الأدنى {requirement.min_quantity_kg}كجم")
        elif requirement.max_quantity_kg and quantity_kg > requirement.max_quantity_kg:
            quantity_met = False
            unmet.append(f"Quantity {quantity_kg}kg exceeds max {requirement.max_quantity_kg}kg")
            unmet_ar.append(f"الكمية {quantity_kg}كجم تتجاوز الحد الأقصى {requirement.max_quantity_kg}كجم")
        if quantity_met:
            score += 15

        # Check certifications (10 points)
        max_score += 10
        cert_met = True
        if requirement.required_certifications:
            missing_certs = [c for c in requirement.required_certifications if c not in certifications]
            if missing_certs:
                cert_met = False
                unmet.append(f"Missing certifications: {', '.join(missing_certs)}")
                unmet_ar.append(f"شهادات مفقودة: {', '.join(missing_certs)}")
        if cert_met:
            score += 10

        # Calculate final score
        match_score = (score / max_score * 100) if max_score > 0 else 0
        is_eligible = len(unmet) == 0

        # Calculate price
        base_price = requirement.base_price_per_kg
        adjustment_percent = 0.0
        if test_record.overall_grade == QualityGrade.PREMIUM:
            adjustment_percent = requirement.price_premium_percent
        elif test_record.overall_grade in [
            QualityGrade.GRADE_C,
            QualityGrade.INDUSTRIAL,
        ]:
            adjustment_percent = -requirement.price_discount_percent

        offered_price = base_price * (Decimal("1") + Decimal(str(adjustment_percent / 100)))
        estimated_total = offered_price * Decimal(str(quantity_kg))

        # Generate recommendation
        if is_eligible:
            recommendation = "This harvest meets all buyer requirements. Contact buyer to proceed."
            recommendation_ar = "هذا المحصول يستوفي جميع متطلبات المشتري. تواصل مع المشتري للمتابعة."
        elif match_score >= 80:
            recommendation = "Close to meeting requirements. Minor adjustments may secure the sale."
            recommendation_ar = "قريب من استيفاء المتطلبات. تعديلات طفيفة قد تضمن البيع."
        else:
            recommendation = "Does not meet buyer requirements. Consider other buyers."
            recommendation_ar = "لا يستوفي متطلبات المشتري. فكر في مشترين آخرين."

        return BuyerMatch(
            buyer_requirement_id=requirement.id,
            buyer_id=requirement.buyer_id,
            buyer_name=requirement.buyer_name,
            buyer_name_ar=requirement.buyer_name_ar,
            buyer_type=requirement.buyer_type,
            match_score=match_score,
            is_eligible=is_eligible,
            offered_price_per_kg=offered_price,
            price_adjustment_percent=adjustment_percent,
            estimated_total_value=estimated_total,
            currency=requirement.currency,
            grade_requirement_met=grade_met,
            quantity_requirement_met=quantity_met,
            certification_requirement_met=cert_met,
            parameter_requirements_met=param_met,
            unmet_requirements=unmet,
            unmet_requirements_ar=unmet_ar,
            contact_email=requirement.contact_email,
            contact_phone=requirement.contact_phone,
            recommendation=recommendation,
            recommendation_ar=recommendation_ar,
        )


# ─────────────────────────────────────────────────────────────────────────────
# Trend Analysis - تحليل الاتجاهات
# ─────────────────────────────────────────────────────────────────────────────


class QualityTrendAnalyzer:
    """
    Analyzer for quality trends over time
    محلل اتجاهات الجودة عبر الزمن
    """

    def analyze_trends(
        self,
        test_records: list[QualityTestRecord],
        min_samples: int = 3,
    ) -> QualityTrendAnalysis:
        """
        Analyze quality trends from multiple test records

        Args:
            test_records: List of quality test records
            min_samples: Minimum samples required for analysis

        Returns:
            QualityTrendAnalysis with trend information
        """
        if len(test_records) < min_samples:
            return QualityTrendAnalysis(
                sample_count=len(test_records),
                confidence_score=0.0,
                recommendations=["Insufficient data for trend analysis"],
                recommendations_ar=["بيانات غير كافية لتحليل الاتجاه"],
            )

        # Sort by date
        sorted_records = sorted(
            test_records,
            key=lambda r: r.harvest_date or datetime.min.date(),
        )

        # Extract data points
        data_points: list[QualityTrendPoint] = []
        grade_counts: dict[str, int] = {}
        moisture_values: list[float] = []
        protein_values: list[float] = []
        sugar_values: list[float] = []
        defect_values: list[float] = []
        grade_scores: list[float] = []

        for record in sorted_records:
            if record.harvest_date:
                point = QualityTrendPoint(
                    date=record.harvest_date,
                    grade=record.overall_grade,
                    grade_score=record.grade_score,
                    moisture_percent=record.moisture_percent,
                    protein_percent=record.protein_percent,
                    sugar_brix=record.sugar_brix,
                    defect_percent=record.defect_percent,
                )
                data_points.append(point)

                # Collect for statistics
                grade_counts[record.overall_grade.value] = grade_counts.get(record.overall_grade.value, 0) + 1
                grade_scores.append(record.grade_score)

                if record.moisture_percent is not None:
                    moisture_values.append(record.moisture_percent)
                if record.protein_percent is not None:
                    protein_values.append(record.protein_percent)
                if record.sugar_brix is not None:
                    sugar_values.append(record.sugar_brix)
                if record.defect_percent is not None:
                    defect_values.append(record.defect_percent)

        if not data_points:
            return QualityTrendAnalysis(sample_count=0, confidence_score=0.0)

        # Calculate statistics
        avg_score = sum(grade_scores) / len(grade_scores) if grade_scores else 0
        std_dev = self._calculate_std_dev(grade_scores)
        best_score = max(grade_scores) if grade_scores else 0
        worst_score = min(grade_scores) if grade_scores else 0

        # Determine overall trend direction
        trend_direction, trend_strength = self._calculate_trend(grade_scores)

        # Parameter-specific trends
        moisture_trend = self._calculate_trend_direction(moisture_values) if moisture_values else TrendDirection.STABLE
        protein_trend = self._calculate_trend_direction(protein_values) if protein_values else TrendDirection.STABLE
        sugar_trend = self._calculate_trend_direction(sugar_values) if sugar_values else TrendDirection.STABLE

        # Generate recommendations
        recommendations: list[str] = []
        recommendations_ar: list[str] = []

        if trend_direction == TrendDirection.DECLINING:
            recommendations.append("Quality is declining. Review production practices and input quality.")
            recommendations_ar.append("الجودة في تراجع. راجع ممارسات الإنتاج وجودة المدخلات.")

        if moisture_trend == TrendDirection.IMPROVING and moisture_values:
            recommendations.append("Moisture levels improving. Continue current drying/storage practices.")
            recommendations_ar.append("مستويات الرطوبة تتحسن. استمر في ممارسات التجفيف/التخزين الحالية.")

        # Calculate confidence
        confidence = min(len(data_points) / 10, 1.0)  # Max confidence at 10+ samples

        # Build analysis result
        first_date = data_points[0].date if data_points else None
        last_date = data_points[-1].date if data_points else None

        return QualityTrendAnalysis(
            tenant_id=sorted_records[0].tenant_id if sorted_records else "",
            farm_id=sorted_records[0].farm_id if sorted_records else "",
            field_id=sorted_records[0].field_id if sorted_records else "",
            crop_type=sorted_records[0].crop_type if sorted_records else "",
            crop_type_ar=sorted_records[0].crop_type_ar if sorted_records else "",
            period_start=first_date,
            period_end=last_date,
            data_points=data_points,
            trend_direction=trend_direction,
            trend_strength=trend_strength,
            average_grade_score=avg_score,
            grade_score_std_dev=std_dev,
            best_grade_score=best_score,
            worst_grade_score=worst_score,
            grade_distribution=grade_counts,
            moisture_trend=moisture_trend,
            protein_trend=protein_trend,
            sugar_trend=sugar_trend,
            avg_moisture_percent=(sum(moisture_values) / len(moisture_values) if moisture_values else None),
            avg_protein_percent=(sum(protein_values) / len(protein_values) if protein_values else None),
            avg_sugar_brix=(sum(sugar_values) / len(sugar_values) if sugar_values else None),
            avg_defect_percent=(sum(defect_values) / len(defect_values) if defect_values else None),
            recommendations=recommendations,
            recommendations_ar=recommendations_ar,
            sample_count=len(data_points),
            confidence_score=confidence,
        )

    def _calculate_trend(self, values: list[float]) -> tuple[TrendDirection, float]:
        """Calculate trend direction and strength from values"""
        if len(values) < 2:
            return TrendDirection.STABLE, 0.0

        # Simple linear regression slope
        n = len(values)
        x = list(range(n))
        x_mean = sum(x) / n
        y_mean = sum(values) / n

        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return TrendDirection.STABLE, 0.0

        slope = numerator / denominator

        # Calculate R-squared for trend strength
        y_pred = [y_mean + slope * (x[i] - x_mean) for i in range(n)]
        ss_res = sum((values[i] - y_pred[i]) ** 2 for i in range(n))
        ss_tot = sum((values[i] - y_mean) ** 2 for i in range(n))
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

        # Determine direction
        if abs(slope) < 0.5:  # Threshold for "stable"
            direction = TrendDirection.STABLE
        elif slope > 0:
            direction = TrendDirection.IMPROVING
        else:
            direction = TrendDirection.DECLINING

        # Check for fluctuation (high variance, low R-squared)
        if r_squared < 0.3 and self._calculate_std_dev(values) > 10:
            direction = TrendDirection.FLUCTUATING

        return direction, abs(r_squared) * 100

    def _calculate_trend_direction(self, values: list[float]) -> TrendDirection:
        """Calculate just trend direction"""
        direction, _ = self._calculate_trend(values)
        return direction

    def _calculate_std_dev(self, values: list[float]) -> float:
        """Calculate standard deviation"""
        if len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / (len(values) - 1)
        return math.sqrt(variance)
