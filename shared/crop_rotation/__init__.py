"""
SAHOOL Crop Rotation Planning Module - وحدة تخطيط الدورة الزراعية

Comprehensive crop rotation planning and soil health management for
Middle East agricultural operations.

Features:
- Rotation planning and recommendations - تخطيط الدورة والتوصيات
- Soil health improvement tracking - تتبع تحسين صحة التربة
- Pest/disease break recommendations - توصيات كسر دورة الآفات/الأمراض
- Nutrient cycling optimization - تحسين دورة المغذيات
- Multi-year planning - التخطيط متعدد السنوات

Supported Crops (Middle East):
- Wheat (قمح)
- Barley (شعير)
- Alfalfa (برسيم)
- Clover (برسيم مصري)
- Maize (ذرة)
- Sorghum (ذرة رفيعة)
- Tomato (طماطم)
- Potato (بطاطس)
- Onion (بصل)
- Cucumber (خيار)
- Melon (بطيخ أصفر)
- Watermelon (بطيخ أحمر)
- Date Palm (نخيل)
- Cotton (قطن)
- And more...

Version: 1.0.0
Author: SAHOOL Platform Team
Updated: January 2026
"""

# =============================================================================
# Models - النماذج
# =============================================================================

from .models import (
    # Crop Information
    CropCharacteristics,
    # Enums
    CropFamily,
    # Field History
    CropHistoryRecord,
    CropType,
    FieldRotationHistory,
    MultiYearPlan,
    NutrientBalance,
    PestBreakRecommendation,
    # Pest and Disease
    PestDiseaseRisk,
    PlanStatus,
    RecommendationPriority,
    RotationBenefit,
    RotationPlan,
    # Recommendations
    RotationRecommendation,
    RotationSequence,
    # Rotation Planning
    RotationSlot,
    Season,
    SoilHealthIndicator,
    # Soil Health
    SoilHealthMeasurement,
    SoilHealthReport,
    SoilHealthTrend,
)

# =============================================================================
# Planner - المخطط
# =============================================================================
from .planner import (
    # Databases
    CROP_DATABASE,
    PEST_DISEASE_DATABASE,
    ROTATION_COMPATIBILITY,
    # Main Planner Class
    CropRotationPlanner,
    # Configuration
    RotationPlannerConfig,
    calculate_rotation_score,
    get_crop_arabic_name,
    # Helper Functions
    get_crop_characteristics,
    get_recommended_break_crops,
    get_rotation_compatibility,
)

# =============================================================================
# Soil Health - صحة التربة
# =============================================================================
from .soil_health import (
    CROP_SOIL_IMPACT,
    # Constants
    OPTIMAL_RANGES,
    # Enums
    SoilHealthRating,
    # Main Tracker Class
    SoilHealthTracker,
    # Configuration
    SoilHealthTrackerConfig,
    TrendDirection,
    # Helper Functions
    assess_soil_health_from_measurement,
    calculate_nitrogen_credit,
    get_organic_matter_trend_summary,
)

# =============================================================================
# Exports - التصديرات
# =============================================================================

__all__ = [
    # === Models ===
    # Enums
    "CropFamily",
    "CropType",
    "Season",
    "RotationBenefit",
    "SoilHealthIndicator",
    "RecommendationPriority",
    "PlanStatus",
    "SoilHealthRating",
    "TrendDirection",
    # Crop Information
    "CropCharacteristics",
    # Rotation Planning Models
    "RotationSlot",
    "RotationSequence",
    "RotationPlan",
    # Pest and Disease Models
    "PestDiseaseRisk",
    "PestBreakRecommendation",
    # Soil Health Models
    "SoilHealthMeasurement",
    "SoilHealthTrend",
    "SoilHealthReport",
    "NutrientBalance",
    # Recommendation Models
    "RotationRecommendation",
    "MultiYearPlan",
    # History Models
    "CropHistoryRecord",
    "FieldRotationHistory",
    # === Planner ===
    "RotationPlannerConfig",
    "CropRotationPlanner",
    "CROP_DATABASE",
    "PEST_DISEASE_DATABASE",
    "ROTATION_COMPATIBILITY",
    "get_crop_characteristics",
    "get_crop_arabic_name",
    "get_recommended_break_crops",
    "get_rotation_compatibility",
    "calculate_rotation_score",
    # === Soil Health ===
    "SoilHealthTrackerConfig",
    "SoilHealthTracker",
    "OPTIMAL_RANGES",
    "CROP_SOIL_IMPACT",
    "assess_soil_health_from_measurement",
    "calculate_nitrogen_credit",
    "get_organic_matter_trend_summary",
]

__version__ = "1.0.0"
