"""
SAHOOL Agro Advisor - Knowledge Base
Agricultural knowledge for Yemen context
"""

from .diseases import DISEASES, get_disease, get_diseases_by_crop, search_diseases
from .nutrients import (
    NUTRIENT_DEFICIENCIES,
    get_deficiency,
    get_deficiency_by_nutrient,
    diagnose_from_ndvi,
)
from .fertilizers import (
    FERTILIZERS,
    get_fertilizer,
    get_fertilizers_by_type,
    get_fertilizers_for_nutrient,
    calculate_dose,
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
]
