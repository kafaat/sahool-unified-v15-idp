"""
Harvest Quality Tracking Module
===============================
وحدة تتبع جودة المحصول

Comprehensive quality tracking for agricultural produce including:
- Quality grading standards for grains, dates, and vegetables
- Quality test recording and certification
- Grade-based pricing calculations
- Quality trend analysis
- Buyer requirements matching

تتبع شامل للجودة للمنتجات الزراعية يتضمن:
- معايير تصنيف الجودة للحبوب والتمور والخضروات
- تسجيل اختبارات الجودة والشهادات
- حسابات التسعير المبنية على الدرجة
- تحليل اتجاهات الجودة
- مطابقة متطلبات المشترين

Usage Example:
--------------

```python
from shared.harvest_quality import (
    # Models
    QualityGrade,
    QualityStandard,
    QualityTestRecord,
    QualityTestResult,
    BuyerRequirement,
    GradePriceMatrix,

    # Grading
    QualityGradingEngine,
    BuyerMatchingEngine,
    QualityTrendAnalyzer,
    QUALITY_STANDARDS,

    # Pricing
    QualityPricingEngine,
    PricingConfig,
    PRICE_MATRICES,
    calculate_quick_price,
    get_grade_price_breakdown,
)

# Grade a wheat sample
engine = QualityGradingEngine()
engine.set_standard(QUALITY_STANDARDS["wheat"])

result = engine.calculate_grade({
    "moisture": 12.5,
    "protein": 13.0,
    "test_weight": 79.0,
    "foreign_matter": 0.8,
    "damaged_kernels": 1.5,
})

print(f"Grade: {result.overall_grade.value}")
print(f"Score: {result.grade_score:.1f}/100")

# Calculate price
pricing_engine = QualityPricingEngine()
price_calc = pricing_engine.calculate_price(
    grade=result.overall_grade,
    quantity=1000,  # kg
    test_values={"moisture": 12.5, "protein": 13.0},
    price_matrix=PRICE_MATRICES["wheat"],
)

print(f"Total price: {price_calc.final_price} {price_calc.currency.value}")
```

Author: SAHOOL Platform Team
Version: 1.0.0
Updated: January 2026
"""

# Models
# Grading
from .grading import (
    # Standard registry
    QUALITY_STANDARDS,
    # Buyer matching
    BuyerMatchingEngine,
    GradingResult,
    # Grading engine
    QualityGradingEngine,
    # Trend analysis
    QualityTrendAnalyzer,
    get_barley_standard,
    get_date_standard,
    get_vegetable_standard,
    # Standard getters
    get_wheat_standard,
)
from .models import (
    BuyerMatch,
    # Buyer Requirements
    BuyerRequirement,
    BuyerType,
    # Enums
    CropCategory,
    Currency,
    DateStage,
    DateVariety,
    # Pricing
    GradePriceMatrix,
    GrainType,
    PriceCalculation,
    PriceUnit,
    # Errors
    QualityError,
    QualityErrors,
    QualityException,
    QualityGrade,
    # Quality Standards
    QualityParameter,
    QualityStandard,
    QualityTestRecord,
    # Test Records
    QualityTestResult,
    QualityTrendAnalysis,
    # Trend Analysis
    QualityTrendPoint,
    TestResult,
    TestStatus,
    TestType,
    TrendDirection,
    VegetableType,
)

# Pricing
from .pricing import (
    DATE_ADJUSTMENT_RULES,
    GRAIN_ADJUSTMENT_RULES,
    # Price matrix registry
    PRICE_MATRICES,
    # Adjustment rules
    PriceAdjustmentRule,
    PricingConfig,
    # Pricing engine
    QualityPricingEngine,
    # Utility functions
    calculate_quick_price,
    estimate_value_improvement,
    get_barley_price_matrix,
    get_date_price_matrix,
    get_grade_price_breakdown,
    get_vegetable_price_matrix,
    # Price matrix getters
    get_wheat_price_matrix,
)

__all__ = [
    # ─── Enums ────────────────────────────────────────────────────────────
    "CropCategory",
    "QualityGrade",
    "GrainType",
    "DateVariety",
    "DateStage",
    "VegetableType",
    "TestType",
    "TestStatus",
    "TestResult",
    "BuyerType",
    "TrendDirection",
    "Currency",
    "PriceUnit",
    # ─── Quality Standards ────────────────────────────────────────────────
    "QualityParameter",
    "QualityStandard",
    "QUALITY_STANDARDS",
    "get_wheat_standard",
    "get_barley_standard",
    "get_date_standard",
    "get_vegetable_standard",
    # ─── Test Records ─────────────────────────────────────────────────────
    "QualityTestResult",
    "QualityTestRecord",
    # ─── Grading ──────────────────────────────────────────────────────────
    "QualityGradingEngine",
    "GradingResult",
    # ─── Buyer Requirements ───────────────────────────────────────────────
    "BuyerRequirement",
    "BuyerMatch",
    "BuyerMatchingEngine",
    # ─── Trend Analysis ───────────────────────────────────────────────────
    "QualityTrendPoint",
    "QualityTrendAnalysis",
    "QualityTrendAnalyzer",
    # ─── Pricing ──────────────────────────────────────────────────────────
    "GradePriceMatrix",
    "PriceCalculation",
    "QualityPricingEngine",
    "PricingConfig",
    "PriceAdjustmentRule",
    "GRAIN_ADJUSTMENT_RULES",
    "DATE_ADJUSTMENT_RULES",
    "PRICE_MATRICES",
    "get_wheat_price_matrix",
    "get_barley_price_matrix",
    "get_date_price_matrix",
    "get_vegetable_price_matrix",
    "calculate_quick_price",
    "get_grade_price_breakdown",
    "estimate_value_improvement",
    # ─── Errors ───────────────────────────────────────────────────────────
    "QualityError",
    "QualityErrors",
    "QualityException",
]

__version__ = "1.0.0"
