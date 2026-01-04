# SAHOOL AI Explainability Module
# وحدة تفسير الذكاء الاصطناعي

from .explainer import build_explanation, compute_confidence_breakdown
from .models import ConfidenceBreakdown, EvidenceItem, Explanation

__all__ = [
    "ConfidenceBreakdown",
    "EvidenceItem",
    "Explanation",
    "build_explanation",
    "compute_confidence_breakdown",
]
