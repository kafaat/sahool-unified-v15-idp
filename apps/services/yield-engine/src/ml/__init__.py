"""
Machine Learning Module - Yield Engine
وحدة التعلم الآلي - محرك الإنتاجية

Advanced ML capabilities for yield prediction:
- Feature selection (Boruta)
- Hyperparameter optimization (SBO)
- Model explainability (SHAP)

Author: SAHOOL Platform Team
Updated: January 2026
"""

from .feature_selection import BorutaFeatureSelector, FeatureImportance, BorutaResult
from .optimization import SatinBowerbirdOptimizer, OptimizationResult
from .explainability import SHAPExplainer, ExplanationResult

__all__ = [
    "BorutaFeatureSelector",
    "FeatureImportance",
    "BorutaResult",
    "SatinBowerbirdOptimizer",
    "OptimizationResult",
    "SHAPExplainer",
    "ExplanationResult",
]
