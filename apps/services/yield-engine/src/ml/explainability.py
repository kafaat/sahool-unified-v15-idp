"""
SHAP Explainability Module
===========================
وحدة التفسير باستخدام SHAP

Implements SHAP (SHapley Additive exPlanations) for model
interpretability and feature contribution analysis.

Based on: Lundberg & Lee (2017) - "A Unified Approach to
Interpreting Model Predictions"

Features:
    - Feature contribution analysis
    - Individual prediction explanations
    - Global feature importance
    - Visualization support
    - Bilingual explanations (Arabic/English)

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
class FeatureContribution:
    """Contribution of a single feature to prediction."""

    feature_name: str
    feature_name_ar: str
    feature_value: float
    contribution: float  # SHAP value
    contribution_percent: float
    direction: str  # "positive" or "negative"


@dataclass
class ExplanationResult:
    """SHAP explanation for a prediction."""

    prediction_value: float
    base_value: float  # Expected value
    feature_contributions: list[FeatureContribution]
    top_positive_features: list[str]
    top_negative_features: list[str]
    explanation_text: str
    explanation_text_ar: str


class SHAPExplainer:
    """
    SHAP Explainer for Yield Prediction Models
    
    Provides interpretable explanations of model predictions
    using Shapley values from game theory.
    
    Example:
        explainer = SHAPExplainer(model)
        explainer.fit(X_train)
        explanation = explainer.explain(X_test[0], feature_names)
    """

    def __init__(self, model: Any, model_type: str = "tree"):
        """
        Initialize SHAP explainer.
        
        Args:
            model: Trained model (sklearn, xgboost, etc.)
            model_type: Type of model ("tree", "linear", "deep")
        """
        self.model = model
        self.model_type = model_type
        self.explainer = None
        self.expected_value = 0.0

    def fit(self, X_background: np.ndarray, max_samples: int = 100):
        """
        Fit SHAP explainer on background data.
        
        Args:
            X_background: Background dataset for SHAP
            max_samples: Maximum samples to use for background
        """
        # Sample background data if too large
        if len(X_background) > max_samples:
            indices = np.random.choice(len(X_background), max_samples, replace=False)
            X_background = X_background[indices]
        
        try:
            import shap
            
            # Create appropriate explainer based on model type
            if self.model_type == "tree":
                self.explainer = shap.TreeExplainer(self.model)
            elif self.model_type == "linear":
                self.explainer = shap.LinearExplainer(self.model, X_background)
            else:
                # Fallback to KernelExplainer (model-agnostic but slower)
                self.explainer = shap.KernelExplainer(
                    self.model.predict, X_background
                )
            
            # Calculate expected value
            shap_values = self.explainer.shap_values(X_background)
            if isinstance(shap_values, list):
                shap_values = shap_values[0]
            
            self.expected_value = float(np.mean(self.model.predict(X_background)))
            
            logger.info(f"SHAP explainer fitted with {len(X_background)} background samples")
            
        except ImportError:
            logger.warning("SHAP library not available, using fallback explainer")
            self.explainer = None
            self.expected_value = float(np.mean(self.model.predict(X_background)))

    def explain(
        self,
        X: np.ndarray,
        feature_names: list[str],
        feature_names_ar: list[str] | None = None,
    ) -> ExplanationResult:
        """
        Explain a single prediction.
        
        Args:
            X: Feature vector (1D array)
            feature_names: List of feature names
            feature_names_ar: List of Arabic feature names
            
        Returns:
            ExplanationResult with SHAP values and interpretation
        """
        if feature_names_ar is None:
            feature_names_ar = feature_names
        
        # Ensure X is 2D
        if X.ndim == 1:
            X = X.reshape(1, -1)
        
        # Get prediction
        prediction = float(self.model.predict(X)[0])
        
        # Calculate SHAP values
        if self.explainer is not None:
            try:
                shap_values = self.explainer.shap_values(X)
                
                if isinstance(shap_values, list):
                    shap_values = shap_values[0]
                
                if shap_values.ndim > 1:
                    shap_values = shap_values[0]
                
            except Exception as e:
                logger.warning(f"SHAP calculation failed: {e}, using fallback")
                shap_values = self._fallback_explanation(X[0], prediction)
        else:
            shap_values = self._fallback_explanation(X[0], prediction)
        
        # Create feature contributions
        contributions = []
        total_abs_contribution = np.sum(np.abs(shap_values))
        
        for i, (shap_value, feat_value) in enumerate(zip(shap_values, X[0])):
            contribution_percent = (
                abs(shap_value) / total_abs_contribution * 100
                if total_abs_contribution > 0
                else 0
            )
            
            contributions.append(
                FeatureContribution(
                    feature_name=feature_names[i],
                    feature_name_ar=feature_names_ar[i],
                    feature_value=float(feat_value),
                    contribution=float(shap_value),
                    contribution_percent=contribution_percent,
                    direction="positive" if shap_value > 0 else "negative",
                )
            )
        
        # Sort by absolute contribution
        contributions.sort(key=lambda x: abs(x.contribution), reverse=True)
        
        # Get top features
        top_positive = [
            c.feature_name for c in contributions
            if c.direction == "positive"
        ][:3]
        
        top_negative = [
            c.feature_name for c in contributions
            if c.direction == "negative"
        ][:3]
        
        # Generate explanation text
        explanation_en = self._generate_explanation_text(
            contributions, prediction, self.expected_value, lang="en"
        )
        explanation_ar = self._generate_explanation_text(
            contributions, prediction, self.expected_value, lang="ar"
        )
        
        return ExplanationResult(
            prediction_value=prediction,
            base_value=self.expected_value,
            feature_contributions=contributions,
            top_positive_features=top_positive,
            top_negative_features=top_negative,
            explanation_text=explanation_en,
            explanation_text_ar=explanation_ar,
        )

    def _fallback_explanation(
        self, X: np.ndarray, prediction: float
    ) -> np.ndarray:
        """
        Fallback explanation when SHAP is not available.
        
        Uses simple feature correlation with prediction deviation.
        """
        # Normalize features
        X_norm = (X - np.mean(X)) / (np.std(X) + 1e-10)
        
        # Contribution proportional to normalized value
        deviation = prediction - self.expected_value
        contributions = X_norm * (deviation / len(X))
        
        return contributions

    def _generate_explanation_text(
        self,
        contributions: list[FeatureContribution],
        prediction: float,
        base_value: float,
        lang: str = "en",
    ) -> str:
        """Generate human-readable explanation."""
        top_3 = contributions[:3]
        
        if lang == "ar":
            text = f"التوقع: {prediction:.2f} طن/هكتار (القيمة الأساسية: {base_value:.2f})\n\n"
            text += "أهم العوامل المؤثرة:\n"
            
            for i, contrib in enumerate(top_3, 1):
                direction = "زيادة" if contrib.direction == "positive" else "تقليل"
                text += f"{i}. {contrib.feature_name_ar}: {direction} بمقدار {abs(contrib.contribution):.2f} "
                text += f"({contrib.contribution_percent:.1f}%)\n"
        else:
            text = f"Prediction: {prediction:.2f} t/ha (base: {base_value:.2f})\n\n"
            text += "Top Contributing Factors:\n"
            
            for i, contrib in enumerate(top_3, 1):
                direction = "increases" if contrib.direction == "positive" else "decreases"
                text += f"{i}. {contrib.feature_name}: {direction} yield by {abs(contrib.contribution):.2f} "
                text += f"({contrib.contribution_percent:.1f}%)\n"
        
        return text


def create_explanation_report(explanation: ExplanationResult) -> dict[str, Any]:
    """
    Create comprehensive explanation report.
    
    Args:
        explanation: SHAP explanation result
        
    Returns:
        Dictionary with formatted report
    """
    report = {
        "prediction": {
            "value": explanation.prediction_value,
            "base_value": explanation.base_value,
            "deviation": explanation.prediction_value - explanation.base_value,
        },
        "top_features": {
            "positive": explanation.top_positive_features,
            "negative": explanation.top_negative_features,
        },
        "contributions": [
            {
                "feature": c.feature_name,
                "feature_ar": c.feature_name_ar,
                "value": c.feature_value,
                "contribution": c.contribution,
                "contribution_percent": c.contribution_percent,
                "direction": c.direction,
            }
            for c in explanation.feature_contributions
        ],
        "explanation": {
            "english": explanation.explanation_text,
            "arabic": explanation.explanation_text_ar,
        },
    }
    
    return report
