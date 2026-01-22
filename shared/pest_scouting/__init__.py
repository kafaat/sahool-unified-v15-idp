"""
SAHOOL Pest Scouting and Monitoring Module - وحدة مسح ورصد الآفات
==================================================================

Comprehensive pest scouting and monitoring module for the SAHOOL
National Agricultural Intelligence Platform.

Features:
- Pest/disease identification support with Middle East pest database
- Scout report management and tracking
- Threshold-based alerts with economic analysis
- Treatment recommendations (chemical, biological, cultural)
- Historical outbreak tracking and analysis

Supported Pests (Middle East focus):
- Red Palm Weevil (سوسة النخيل الحمراء)
- Dubas Bug (دوباس النخيل)
- Aphids (المن)
- Whiteflies (الذبابة البيضاء)
- Spider Mites (العنكبوت الأحمر)
- Locusts (الجراد الصحراوي)
- Date Moth (فراشة التمر)
- Tomato Leafminer (حافرة أنفاق الطماطم - Tuta absoluta)
- Thrips (التربس)
- Fruit Flies (ذباب الفاكهة)

Bilingual support: Arabic (العربية) and English

Version: 1.0.0
Author: SAHOOL Platform Team
Updated: January 2026
"""

# =============================================================================
# Models - النماذج
# =============================================================================
from .models import (
    # Enums
    PestCategory,
    PestLifeStage,
    InfestationLevel,
    AlertPriority,
    ScoutingMethod,
    TreatmentType,
    TreatmentUrgency,
    CropType,
    # Data Classes
    PestIdentification,
    ScoutObservation,
    ScoutReport,
    PestAlert,
    OutbreakRecord,
    TreatmentRecommendation,
    EconomicThreshold,
)

# =============================================================================
# Identification - التعريف
# =============================================================================
from .identification import (
    # Database
    PEST_DATABASE,
    # Lookup functions
    get_pest_by_id,
    get_pest_by_scientific_name,
    search_pests_by_name,
    get_pests_by_crop,
    get_pests_by_category,
    get_quarantine_pests,
    get_high_priority_pests,
    # Identification helpers
    identify_by_symptoms,
    identify_by_description,
    get_identification_guide,
    assess_infestation_level,
    get_similar_pests,
    # Seasonal and regional
    get_seasonal_pests,
    get_pest_risk_factors,
)

# =============================================================================
# Thresholds - العتبات
# =============================================================================
from .thresholds import (
    # Database
    THRESHOLD_DATABASE,
    # Data Classes
    ThresholdAssessment,
    # Lookup functions
    get_threshold,
    get_thresholds_for_crop,
    get_thresholds_for_pest,
    # Assessment functions
    assess_threshold,
    assess_scout_report,
    generate_threshold_alert,
    # Economic calculations
    calculate_economic_injury_level,
    calculate_gain_threshold,
    estimate_yield_loss,
    calculate_treatment_roi,
)

# =============================================================================
# Recommendations - التوصيات
# =============================================================================
from .recommendations import (
    # Data Classes
    ChemicalOption,
    BiologicalOption,
    CulturalPractice,
    # Database
    TREATMENT_PROTOCOLS,
    # Functions
    get_treatment_protocol,
    generate_treatment_recommendation,
    generate_recommendation_from_alert,
    generate_recommendations_from_report,
    # Rotation management
    get_rotation_recommendation,
    get_ipm_calendar,
)

# =============================================================================
# Module Exports - صادرات الوحدة
# =============================================================================
__all__ = [
    # === Models ===
    # Enums
    "PestCategory",
    "PestLifeStage",
    "InfestationLevel",
    "AlertPriority",
    "ScoutingMethod",
    "TreatmentType",
    "TreatmentUrgency",
    "CropType",
    # Data Classes
    "PestIdentification",
    "ScoutObservation",
    "ScoutReport",
    "PestAlert",
    "OutbreakRecord",
    "TreatmentRecommendation",
    "EconomicThreshold",
    # === Identification ===
    "PEST_DATABASE",
    "get_pest_by_id",
    "get_pest_by_scientific_name",
    "search_pests_by_name",
    "get_pests_by_crop",
    "get_pests_by_category",
    "get_quarantine_pests",
    "get_high_priority_pests",
    "identify_by_symptoms",
    "identify_by_description",
    "get_identification_guide",
    "assess_infestation_level",
    "get_similar_pests",
    "get_seasonal_pests",
    "get_pest_risk_factors",
    # === Thresholds ===
    "THRESHOLD_DATABASE",
    "ThresholdAssessment",
    "get_threshold",
    "get_thresholds_for_crop",
    "get_thresholds_for_pest",
    "assess_threshold",
    "assess_scout_report",
    "generate_threshold_alert",
    "calculate_economic_injury_level",
    "calculate_gain_threshold",
    "estimate_yield_loss",
    "calculate_treatment_roi",
    # === Recommendations ===
    "ChemicalOption",
    "BiologicalOption",
    "CulturalPractice",
    "TREATMENT_PROTOCOLS",
    "get_treatment_protocol",
    "generate_treatment_recommendation",
    "generate_recommendation_from_alert",
    "generate_recommendations_from_report",
    "get_rotation_recommendation",
    "get_ipm_calendar",
]

__version__ = "1.0.0"
