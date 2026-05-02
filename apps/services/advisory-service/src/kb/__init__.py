"""
SAHOOL Agro Advisor - Knowledge Base
Agricultural knowledge for Yemen context
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

# AI-advisor v2 knowledge sources (optional — depend on httpx / qdrant-client).
# Import errors are tolerated so unit tests for the rule-based KB can run
# without the heavier dependencies installed.
try:
    from .knowledge_graph_client import KnowledgeGraphClient
except ImportError:  # pragma: no cover
    KnowledgeGraphClient = None  # type: ignore[assignment,misc]

try:
    from .crag_knowledge_base import CragKnowledgeBase
except ImportError:  # pragma: no cover
    CragKnowledgeBase = None  # type: ignore[assignment,misc]

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
    # AI advisor v2
    "KnowledgeGraphClient",
    "CragKnowledgeBase",
]
