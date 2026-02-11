"""
SAHOOL Soil Testing and Analysis Module - وحدة تحليل واختبار التربة

Comprehensive soil testing and analysis for agricultural operations including:
- Soil test result recording - تسجيل نتائج تحليل التربة
- Nutrient level interpretation - تفسير مستويات العناصر الغذائية
- Amendment recommendations - توصيات التعديل والتسميد
- Historical trend tracking - تتبع الاتجاهات التاريخية
- Lab integration support - دعم التكامل مع المختبرات

Features:
- Support for NPK, pH, EC, organic matter, micronutrients
- Bilingual Arabic/English content
- Local Middle East soil type classifications
- Crop-specific interpretations and recommendations
- Multi-year trend analysis with management insights

Usage:
    from shared.soil_testing import (
        SoilTestResult,
        SoilTestInterpreter,
        SoilAmendmentRecommender,
        SoilTrendAnalyzer,
    )

    # Create a soil test result
    soil_test = SoilTestResult(
        id="test_001",
        tenant_id="tenant_001",
        field_id="field_001",
        sample_id="sample_001",
        sample_date=datetime.now(),
        macronutrients=MacronutrientResults(
            nitrogen_nitrate_ppm=25,
            phosphorus_ppm=15,
            potassium_ppm=180,
        ),
        soil_properties=SoilProperties(
            ph=7.8,
            ec_ds_m=2.5,
            organic_matter_percent=1.5,
        ),
    )

    # Interpret results
    interpreter = SoilTestInterpreter()
    report = interpreter.interpret(soil_test, crop="wheat")
    print(report.summary_ar)

    # Generate amendment recommendations
    recommender = SoilAmendmentRecommender()
    plan = recommender.generate_plan(soil_test, crop="wheat")
    print(plan.summary_ar)

    # Analyze trends over multiple tests
    analyzer = SoilTrendAnalyzer()
    trend_report = analyzer.analyze_trends(field_id, tenant_id, soil_tests_list)
    print(trend_report.summary_ar)

Version: 1.0.0
Author: SAHOOL Platform Team
"""

# Models - Data structures
# Interpreter - Result interpretation
from .interpreter import (
    CROP_SENSITIVITY,
    # Thresholds data
    NUTRIENT_THRESHOLDS,
    SOIL_PROPERTY_THRESHOLDS,
    # Configuration
    InterpretationConfig,
    # Main interpreter
    SoilTestInterpreter,
    get_ec_status,
    get_nutrient_status,
    get_ph_status,
    # Convenience functions
    interpret_soil_test,
)
from .models import (
    AmendmentPlan,
    # Recommendations
    AmendmentRecommendation,
    ExtractionMethod,
    HeavyMetals,
    InterpretationReport,
    LabInfo,
    LabStatus,
    # Result components
    MacronutrientResults,
    MicronutrientResults,
    # Interpretation
    NutrientInterpretation,
    # Enums
    NutrientStatus,
    NutrientTrend,
    # Sample and Lab
    SampleLocation,
    SampleType,
    SoilProperties,
    # Main soil test
    SoilTestResult,
    SoilTexture,
    SoilTextureClass,
    SoilType,
    # Trends
    TrendDataPoint,
    TrendReport,
)

# Recommendations - Amendment recommendations
from .recommendations import (
    CROP_REQUIREMENTS,
    # Product data
    FERTILIZER_PRODUCTS,
    # Configuration
    RecommendationConfig,
    # Main recommender
    SoilAmendmentRecommender,
    calculate_fertilizer_rate,
    # Convenience functions
    generate_amendment_plan,
    get_available_products,
    get_crop_requirements,
)

# Trends - Historical analysis
from .trends import (
    # Main analyzer
    SoilTrendAnalyzer,
    # Configuration
    TrendAnalysisConfig,
    # Convenience functions
    analyze_soil_trends,
    compare_soil_periods,
    get_nutrient_trend,
)

__version__ = "1.0.0"

__all__ = [
    # Version
    "__version__",
    # ===== Enums =====
    "NutrientStatus",
    "SoilTextureClass",
    "SoilType",
    "SampleType",
    "LabStatus",
    "ExtractionMethod",
    # ===== Sample and Lab Models =====
    "SampleLocation",
    "LabInfo",
    # ===== Result Component Models =====
    "MacronutrientResults",
    "MicronutrientResults",
    "SoilProperties",
    "SoilTexture",
    "HeavyMetals",
    # ===== Main Soil Test Model =====
    "SoilTestResult",
    # ===== Interpretation Models =====
    "NutrientInterpretation",
    "InterpretationReport",
    # ===== Recommendation Models =====
    "AmendmentRecommendation",
    "AmendmentPlan",
    # ===== Trend Models =====
    "TrendDataPoint",
    "NutrientTrend",
    "TrendReport",
    # ===== Interpreter =====
    "InterpretationConfig",
    "SoilTestInterpreter",
    "interpret_soil_test",
    "get_nutrient_status",
    "get_ph_status",
    "get_ec_status",
    "NUTRIENT_THRESHOLDS",
    "SOIL_PROPERTY_THRESHOLDS",
    "CROP_SENSITIVITY",
    # ===== Recommendations =====
    "RecommendationConfig",
    "SoilAmendmentRecommender",
    "generate_amendment_plan",
    "get_available_products",
    "get_crop_requirements",
    "calculate_fertilizer_rate",
    "FERTILIZER_PRODUCTS",
    "CROP_REQUIREMENTS",
    # ===== Trends =====
    "TrendAnalysisConfig",
    "SoilTrendAnalyzer",
    "analyze_soil_trends",
    "get_nutrient_trend",
    "compare_soil_periods",
]
