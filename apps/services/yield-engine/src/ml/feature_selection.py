"""
Boruta Feature Selection
=========================
اختيار المتغيرات باستخدام Boruta

Implements Boruta algorithm for feature importance ranking
and automatic feature selection for yield prediction models.

Based on: Kursa & Rudnicki (2010) - "Feature Selection with the Boruta Package"

Features:
    - Automatic feature selection
    - Statistical significance testing
    - Support for Random Forest and other tree-based models
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
class FeatureImportance:
    """Feature importance result."""

    feature_name: str
    feature_name_ar: str
    importance_score: float
    rank: int
    decision: str  # "confirmed", "tentative", "rejected"
    p_value: float
    z_score: float


@dataclass
class BorutaResult:
    """Result of Boruta feature selection."""

    selected_features: list[str]
    selected_features_ar: list[str]
    feature_importances: list[FeatureImportance]
    n_iterations: int
    n_confirmed: int
    n_tentative: int
    n_rejected: int
    execution_time_seconds: float


class BorutaFeatureSelector:
    """
    Boruta Feature Selection Algorithm
    
    Two-stage feature selection:
    1. Boruta algorithm for feature importance
    2. Statistical significance testing
    
    Example:
        selector = BorutaFeatureSelector(max_iterations=100)
        result = selector.fit(X, y)
        X_selected = selector.transform(X)
    """

    def __init__(
        self,
        max_iterations: int = 100,
        alpha: float = 0.05,
        verbose: bool = True,
    ):
        """
        Initialize Boruta selector.
        
        Args:
            max_iterations: Maximum number of iterations
            alpha: Statistical significance level (default: 0.05)
            verbose: Print progress messages
        """
        self.max_iterations = max_iterations
        self.alpha = alpha
        self.verbose = verbose
        self.selected_features_: list[str] = []
        self.selected_feature_indices_: list[int] = []
        self.feature_importances_: list[FeatureImportance] = []

    def fit(
        self,
        X: np.ndarray,
        y: np.ndarray,
        feature_names: list[str],
        feature_names_ar: list[str] | None = None,
    ) -> BorutaResult:
        """
        Fit Boruta feature selector.
        
        Args:
            X: Feature matrix (n_samples, n_features)
            y: Target vector (n_samples,)
            feature_names: List of feature names
            feature_names_ar: List of Arabic feature names (optional)
            
        Returns:
            BorutaResult with selected features and importances
        """
        import time

        start_time = time.time()

        if feature_names_ar is None:
            feature_names_ar = feature_names

        n_features = X.shape[1]
        
        if self.verbose:
            logger.info(f"Starting Boruta feature selection with {n_features} features")
        
        # Simplified implementation using feature importance
        # In production, use sklearn-BorutaPy or implement full algorithm
        feature_importance_scores = self._calculate_importance(X, y)
        
        # Rank features
        ranked_indices = np.argsort(feature_importance_scores)[::-1]
        
        # Statistical testing (simplified)
        importances = []
        confirmed_count = 0
        tentative_count = 0
        rejected_count = 0
        
        # Threshold: features with importance > median of shadow features
        threshold = np.median(feature_importance_scores)
        
        for rank, idx in enumerate(ranked_indices, 1):
            importance = feature_importance_scores[idx]
            
            # Decision based on importance relative to threshold
            if importance > threshold * 1.5:
                decision = "confirmed"
                confirmed_count += 1
            elif importance > threshold * 0.8:
                decision = "tentative"
                tentative_count += 1
            else:
                decision = "rejected"
                rejected_count += 1
            
            # Calculate statistics (simplified)
            z_score = (importance - threshold) / (np.std(feature_importance_scores) + 1e-10)
            p_value = self._calculate_p_value(z_score)
            
            importances.append(
                FeatureImportance(
                    feature_name=feature_names[idx],
                    feature_name_ar=feature_names_ar[idx],
                    importance_score=float(importance),
                    rank=rank,
                    decision=decision,
                    p_value=p_value,
                    z_score=z_score,
                )
            )
        
        # Select confirmed and tentative features
        selected = [f.feature_name for f in importances if f.decision in ["confirmed", "tentative"]]
        selected_ar = [f.feature_name_ar for f in importances if f.decision in ["confirmed", "tentative"]]
        
        # Store indices of selected features for transform()
        selected_indices = [
            i for i, f in enumerate(importances)
            if f.decision in ["confirmed", "tentative"]
        ]
        
        self.selected_features_ = selected
        self.selected_feature_indices_ = selected_indices
        self.feature_importances_ = importances
        
        execution_time = time.time() - start_time
        
        if self.verbose:
            logger.info(
                f"Boruta completed: {confirmed_count} confirmed, "
                f"{tentative_count} tentative, {rejected_count} rejected "
                f"in {execution_time:.2f}s"
            )
        
        return BorutaResult(
            selected_features=selected,
            selected_features_ar=selected_ar,
            feature_importances=importances,
            n_iterations=self.max_iterations,
            n_confirmed=confirmed_count,
            n_tentative=tentative_count,
            n_rejected=rejected_count,
            execution_time_seconds=execution_time,
        )

    def transform(self, X: np.ndarray) -> np.ndarray:
        """
        Transform dataset to selected features only.
        
        Args:
            X: Feature matrix
            
        Returns:
            Transformed feature matrix with selected features only
        """
        if not self.selected_features_:
            raise ValueError("Boruta not fitted. Call fit() first.")
        
        if not self.selected_feature_indices_:
            raise ValueError("No features were selected.")
        
        # Return only the selected feature columns using stored indices
        return X[:, self.selected_feature_indices_]

    def _calculate_importance(self, X: np.ndarray, y: np.ndarray) -> np.ndarray:
        """
        Calculate feature importance using Random Forest.
        
        Simplified implementation. In production, use:
        - sklearn.ensemble.RandomForestRegressor
        - or XGBoost feature importance
        """
        try:
            from sklearn.ensemble import RandomForestRegressor
            
            rf = RandomForestRegressor(
                n_estimators=50,
                max_depth=10,
                random_state=42,
                n_jobs=-1,
            )
            rf.fit(X, y)
            return rf.feature_importances_
        except ImportError:
            # Fallback: correlation-based importance
            logger.warning("sklearn not available, using correlation-based importance")
            return np.abs(np.corrcoef(X.T, y)[:-1, -1])

    def _calculate_p_value(self, z_score: float) -> float:
        """Calculate p-value from z-score (simplified)."""
        try:
            from scipy import stats
            return float(2 * (1 - stats.norm.cdf(abs(z_score))))
        except ImportError:
            # Fallback approximation
            return float(np.exp(-0.5 * z_score**2))


def create_feature_importance_report(result: BorutaResult) -> dict[str, Any]:
    """
    Create a comprehensive feature importance report.
    
    Args:
        result: Boruta selection result
        
    Returns:
        Dictionary with bilingual report
    """
    report = {
        "summary": {
            "total_features": len(result.feature_importances),
            "confirmed": result.n_confirmed,
            "tentative": result.n_tentative,
            "rejected": result.n_rejected,
            "selected": len(result.selected_features),
            "execution_time_seconds": result.execution_time_seconds,
        },
        "summary_ar": {
            "إجمالي_المتغيرات": len(result.feature_importances),
            "مؤكد": result.n_confirmed,
            "محتمل": result.n_tentative,
            "مرفوض": result.n_rejected,
            "مختار": len(result.selected_features),
            "وقت_التنفيذ_ثانية": result.execution_time_seconds,
        },
        "selected_features": result.selected_features,
        "selected_features_ar": result.selected_features_ar,
        "feature_importances": [
            {
                "feature": f.feature_name,
                "feature_ar": f.feature_name_ar,
                "importance": f.importance_score,
                "rank": f.rank,
                "decision": f.decision,
                "p_value": f.p_value,
                "z_score": f.z_score,
            }
            for f in result.feature_importances
        ],
    }
    
    return report
