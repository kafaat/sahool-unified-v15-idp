"""
Machine Learning Module - Agro-Advisor
وحدة التعلم الآلي - المستشار الزراعي

Multi-criteria decision making for agricultural recommendations:
- WASPAS (Weighted Aggregated Sum Product Assessment)
- Balance yield, cost, and sustainability

Author: SAHOOL Platform Team
Updated: January 2026
"""

from .waspas import (
    WASPASRecommender,
    Criterion,
    Alternative,
    WASPASResult,
    create_waspas_report,
)

__all__ = [
    "WASPASRecommender",
    "Criterion",
    "Alternative",
    "WASPASResult",
    "create_waspas_report",
]
