"""
WASPAS Multi-Criteria Decision Making
======================================
تحليل القرارات متعددة المعايير باستخدام WASPAS

Implements WASPAS (Weighted Aggregated Sum Product Assessment)
for multi-objective optimization in agricultural recommendations.

Based on: Zavadskas et al. (2012) - "Optimization of Weighted Aggregated
Sum Product Assessment"

Features:
    - Multi-criteria decision analysis
    - Balance between yield, cost, and sustainability
    - Weighted aggregation of objectives
    - Bilingual output (Arabic/English)

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class Criterion:
    """Single decision criterion."""

    name: str
    name_ar: str
    weight: float  # 0-1, sum of all weights should be 1
    is_benefit: bool  # True for maximize, False for minimize
    unit: str
    unit_ar: str


@dataclass
class Alternative:
    """Decision alternative (e.g., fertilizer recommendation)."""

    id: str
    name: str
    name_ar: str
    description: str
    description_ar: str
    criteria_values: dict[str, float]  # criterion_name -> value


@dataclass
class WASPASResult:
    """WASPAS analysis result."""

    ranked_alternatives: list[tuple[str, float]]  # (alternative_id, score)
    best_alternative_id: str
    scores: dict[str, float]  # alternative_id -> score
    wsm_scores: dict[str, float]  # Weighted Sum Model scores
    wpm_scores: dict[str, float]  # Weighted Product Model scores
    lambda_param: float
    explanation: str
    explanation_ar: str


class WASPASRecommender:
    """
    WASPAS Multi-Criteria Decision Making
    
    Combines two approaches:
    1. WSM (Weighted Sum Model) - additive aggregation
    2. WPM (Weighted Product Model) - multiplicative aggregation
    
    Final score: Q = λ * WSM + (1-λ) * WPM
    
    Example:
        criteria = [
            Criterion("yield", "الإنتاجية", 0.4, True, "t/ha", "طن/هكتار"),
            Criterion("cost", "التكلفة", 0.3, False, "SAR", "ريال"),
            Criterion("sustainability", "الاستدامة", 0.3, True, "score", "درجة"),
        ]
        
        alternatives = [
            Alternative("alt1", "Urea", "يوريا", ..., {"yield": 4.5, "cost": 500, "sustainability": 0.7}),
            Alternative("alt2", "Organic", "عضوي", ..., {"yield": 4.2, "cost": 800, "sustainability": 0.95}),
        ]
        
        waspas = WASPASRecommender(criteria)
        result = waspas.evaluate(alternatives)
    """

    def __init__(
        self,
        criteria: list[Criterion],
        lambda_param: float = 0.5,
        verbose: bool = True,
    ):
        """
        Initialize WASPAS recommender.
        
        Args:
            criteria: List of decision criteria
            lambda_param: Balance between WSM and WPM (0-1, default 0.5)
            verbose: Print progress messages
        """
        self.criteria = criteria
        self.lambda_param = lambda_param
        self.verbose = verbose
        
        # Validate weights sum to 1
        total_weight = sum(c.weight for c in criteria)
        if not np.isclose(total_weight, 1.0):
            logger.warning(f"Criteria weights sum to {total_weight}, normalizing...")
            for c in self.criteria:
                c.weight /= total_weight

    def evaluate(self, alternatives: list[Alternative]) -> WASPASResult:
        """
        Evaluate alternatives using WASPAS.
        
        Args:
            alternatives: List of decision alternatives
            
        Returns:
            WASPASResult with ranked alternatives
        """
        if self.verbose:
            logger.info(f"WASPAS evaluation: {len(alternatives)} alternatives, {len(self.criteria)} criteria")
        
        # Step 1: Build decision matrix
        matrix = self._build_decision_matrix(alternatives)
        
        # Step 2: Normalize decision matrix
        normalized_matrix = self._normalize_matrix(matrix)
        
        # Step 3: Calculate WSM scores
        wsm_scores = self._calculate_wsm(normalized_matrix)
        
        # Step 4: Calculate WPM scores
        wpm_scores = self._calculate_wpm(normalized_matrix)
        
        # Step 5: Calculate final WASPAS scores
        waspas_scores = {}
        for alt_id in wsm_scores:
            waspas_scores[alt_id] = (
                self.lambda_param * wsm_scores[alt_id] +
                (1 - self.lambda_param) * wpm_scores[alt_id]
            )
        
        # Step 6: Rank alternatives
        ranked = sorted(waspas_scores.items(), key=lambda x: x[1], reverse=True)
        best_id = ranked[0][0]
        
        # Step 7: Generate explanation
        explanation_en = self._generate_explanation(ranked, alternatives, lang="en")
        explanation_ar = self._generate_explanation(ranked, alternatives, lang="ar")
        
        if self.verbose:
            logger.info(f"Best alternative: {best_id} (score: {ranked[0][1]:.4f})")
        
        return WASPASResult(
            ranked_alternatives=ranked,
            best_alternative_id=best_id,
            scores=waspas_scores,
            wsm_scores=wsm_scores,
            wpm_scores=wpm_scores,
            lambda_param=self.lambda_param,
            explanation=explanation_en,
            explanation_ar=explanation_ar,
        )

    def _build_decision_matrix(
        self, alternatives: list[Alternative]
    ) -> dict[str, dict[str, float]]:
        """Build decision matrix from alternatives."""
        matrix = {}
        
        for alt in alternatives:
            matrix[alt.id] = {}
            for criterion in self.criteria:
                if criterion.name not in alt.criteria_values:
                    raise ValueError(
                        f"Alternative {alt.id} missing value for criterion {criterion.name}"
                    )
                matrix[alt.id][criterion.name] = alt.criteria_values[criterion.name]
        
        return matrix

    def _normalize_matrix(
        self, matrix: dict[str, dict[str, float]]
    ) -> dict[str, dict[str, float]]:
        """
        Normalize decision matrix.
        
        For benefit criteria (maximize): x_ij / max(x_j)
        For cost criteria (minimize): min(x_j) / x_ij
        """
        normalized = {}
        
        # Find max and min for each criterion
        criterion_values = {c.name: [] for c in self.criteria}
        for alt_values in matrix.values():
            for crit_name, value in alt_values.items():
                criterion_values[crit_name].append(value)
        
        criterion_max = {name: max(values) for name, values in criterion_values.items()}
        criterion_min = {name: min(values) for name, values in criterion_values.items()}
        
        # Normalize
        for alt_id, alt_values in matrix.items():
            normalized[alt_id] = {}
            
            for criterion in self.criteria:
                value = alt_values[criterion.name]
                
                if criterion.is_benefit:
                    # Benefit criterion: higher is better
                    normalized[alt_id][criterion.name] = (
                        value / criterion_max[criterion.name]
                        if criterion_max[criterion.name] > 0
                        else 0
                    )
                else:
                    # Cost criterion: lower is better
                    normalized[alt_id][criterion.name] = (
                        criterion_min[criterion.name] / value
                        if value > 0
                        else 1
                    )
        
        return normalized

    def _calculate_wsm(
        self, normalized_matrix: dict[str, dict[str, float]]
    ) -> dict[str, float]:
        """Calculate Weighted Sum Model scores."""
        wsm_scores = {}
        
        for alt_id, alt_values in normalized_matrix.items():
            score = 0.0
            for criterion in self.criteria:
                score += criterion.weight * alt_values[criterion.name]
            wsm_scores[alt_id] = score
        
        return wsm_scores

    def _calculate_wpm(
        self, normalized_matrix: dict[str, dict[str, float]]
    ) -> dict[str, float]:
        """Calculate Weighted Product Model scores."""
        wpm_scores = {}
        
        for alt_id, alt_values in normalized_matrix.items():
            score = 1.0
            for criterion in self.criteria:
                # Avoid zero/negative values in product
                value = max(alt_values[criterion.name], 1e-10)
                score *= value ** criterion.weight
            wpm_scores[alt_id] = score
        
        return wpm_scores

    def _generate_explanation(
        self,
        ranked: list[tuple[str, float]],
        alternatives: list[Alternative],
        lang: str = "en",
    ) -> str:
        """Generate human-readable explanation."""
        alt_map = {alt.id: alt for alt in alternatives}
        
        top_3 = ranked[:min(3, len(ranked))]
        
        if lang == "ar":
            text = "نتائج التحليل متعدد المعايير (WASPAS):\n\n"
            text += "أفضل 3 بدائل:\n"
            
            for i, (alt_id, score) in enumerate(top_3, 1):
                alt = alt_map[alt_id]
                text += f"{i}. {alt.name_ar} - النتيجة: {score:.3f}\n"
                text += f"   {alt.description_ar}\n\n"
            
            text += "\nالمعايير المستخدمة:\n"
            for criterion in self.criteria:
                text += f"- {criterion.name_ar}: وزن {criterion.weight:.0%}\n"
        else:
            text = "WASPAS Multi-Criteria Analysis Results:\n\n"
            text += "Top 3 Alternatives:\n"
            
            for i, (alt_id, score) in enumerate(top_3, 1):
                alt = alt_map[alt_id]
                text += f"{i}. {alt.name} - Score: {score:.3f}\n"
                text += f"   {alt.description}\n\n"
            
            text += "\nCriteria Used:\n"
            for criterion in self.criteria:
                text += f"- {criterion.name}: {criterion.weight:.0%} weight\n"
        
        return text


def create_waspas_report(
    result: WASPASResult, alternatives: list[Alternative]
) -> dict[str, Any]:
    """
    Create comprehensive WASPAS report.
    
    Args:
        result: WASPAS analysis result
        alternatives: List of evaluated alternatives
        
    Returns:
        Dictionary with formatted report
    """
    alt_map = {alt.id: alt for alt in alternatives}
    
    report = {
        "best_alternative": {
            "id": result.best_alternative_id,
            "name": alt_map[result.best_alternative_id].name,
            "name_ar": alt_map[result.best_alternative_id].name_ar,
            "score": result.scores[result.best_alternative_id],
        },
        "ranking": [
            {
                "rank": i,
                "id": alt_id,
                "name": alt_map[alt_id].name,
                "name_ar": alt_map[alt_id].name_ar,
                "score": score,
                "wsm_score": result.wsm_scores[alt_id],
                "wpm_score": result.wpm_scores[alt_id],
            }
            for i, (alt_id, score) in enumerate(result.ranked_alternatives, 1)
        ],
        "parameters": {
            "lambda": result.lambda_param,
            "n_alternatives": len(alternatives),
        },
        "explanation": {
            "english": result.explanation,
            "arabic": result.explanation_ar,
        },
    }
    
    return report
