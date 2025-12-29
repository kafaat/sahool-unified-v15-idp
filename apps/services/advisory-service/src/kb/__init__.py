"""
SAHOOL Agro Advisor - Knowledge Base
Agricultural knowledge for Yemen context

قاعدة المعرفة الزراعية - مستشار ساحول
المعرفة الزراعية لسياق اليمن
"""

from .diseases import DISEASES, get_disease, get_diseases_by_crop, search_diseases
from .fertilizers import (
    FERTILIZERS,
    calculate_dose,
    get_fertilizer,
    get_fertilizers_by_type,
    get_fertilizers_for_nutrient,
)
from .nutrients import (
    NUTRIENT_DEFICIENCIES,
    diagnose_from_ndvi,
    get_deficiency,
    get_deficiency_by_nutrient,
)
from .ecological import (
    ECOLOGICAL_PRINCIPLES,
    ECOLOGICAL_PRACTICES,
    COMPANION_PLANTING,
    get_principle,
    get_principles_by_category,
    get_practice,
    get_practices_by_category,
    get_companions,
    search_practices,
    get_globalgap_practices,
    calculate_transition_timeline,
)
from .pitfalls import (
    PITFALLS,
    get_pitfall,
    get_pitfalls_by_category,
    get_pitfalls_by_severity,
    search_pitfalls,
    diagnose_pitfalls,
    get_recovery_plan,
    calculate_risk_score,
)

__all__ = [
    # Diseases
    "DISEASES",
    "get_disease",
    "get_diseases_by_crop",
    "search_diseases",
    # Nutrients
    "NUTRIENT_DEFICIENCIES",
    "get_deficiency",
    "get_deficiency_by_nutrient",
    "diagnose_from_ndvi",
    # Fertilizers
    "FERTILIZERS",
    "get_fertilizer",
    "get_fertilizers_by_type",
    "get_fertilizers_for_nutrient",
    "calculate_dose",
    # Ecological Agriculture (الزراعة الإيكولوجية)
    "ECOLOGICAL_PRINCIPLES",
    "ECOLOGICAL_PRACTICES",
    "COMPANION_PLANTING",
    "get_principle",
    "get_principles_by_category",
    "get_practice",
    "get_practices_by_category",
    "get_companions",
    "search_practices",
    "get_globalgap_practices",
    "calculate_transition_timeline",
    # Pitfalls (المزالق الزراعية)
    "PITFALLS",
    "get_pitfall",
    "get_pitfalls_by_category",
    "get_pitfalls_by_severity",
    "search_pitfalls",
    "diagnose_pitfalls",
    "get_recovery_plan",
    "calculate_risk_score",
]
