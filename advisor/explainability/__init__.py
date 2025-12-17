# SAHOOL AI Explainability Module
# وحدة تفسير الذكاء الاصطناعي

from .models import ConfidenceBreakdown, EvidenceItem, Explanation
from .explainer import build_explanation, compute_confidence_breakdown

__all__ = [
    "ConfidenceBreakdown",
    "EvidenceItem",
    "Explanation",
    "build_explanation",
    "compute_confidence_breakdown",
]
