"""
Evaluation Scoring Service
خدمة تقييم الأداء

Tracks prediction quality, confidence calibration, and model drift detection.

Features:
- Prediction confidence scoring
- Actual outcome recording
- Accuracy metrics calculation
- Model drift detection
- Confidence calibration analysis
- Performance benchmarking per disease/crop
"""

import logging
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

import numpy as np

logger = logging.getLogger("sahool-vision")


@dataclass
class PredictionScore:
    """Score for a single prediction"""

    diagnosis_id: str
    predicted_disease: str
    predicted_confidence: float
    actual_disease: str | None = None
    timestamp: datetime = None
    field_id: str | None = None
    correct: bool | None = None
    confidence_error: float | None = None


@dataclass
class AccuracyMetrics:
    """Accuracy metrics for a prediction set"""

    total_predictions: int
    correct_predictions: int
    accuracy: float
    high_confidence_accuracy: float  # Accuracy for conf > 0.7
    medium_confidence_accuracy: float  # Accuracy for 0.5-0.7
    low_confidence_accuracy: float  # Accuracy for conf < 0.5
    confidence_mean: float
    confidence_std: float
    calibration_score: float  # How well confidence matches accuracy


@dataclass
class ModelDriftIndicators:
    """Indicators of model performance drift"""

    accuracy_7day: float
    accuracy_30day: float
    accuracy_change_percent: float
    confidence_trend: str  # increasing, decreasing, stable
    false_positive_rate: float
    false_negative_rate: float
    drift_detected: bool
    drift_severity: str  # none, mild, moderate, severe


class EvaluationScorer:
    """
    Track prediction quality and model performance

    This service maintains statistics on prediction accuracy and helps
    detect when the model's performance is degrading (drift detection).
    """

    def __init__(self, lookback_days: int = 90):
        self.lookback_days = lookback_days

        # Store all prediction scores
        self.prediction_scores: list[PredictionScore] = []

        # Cache for metrics (invalidated when new scores added)
        self.metrics_cache: dict[str, AccuracyMetrics] = {}
        self.per_disease_cache: dict[str, dict[str, Any]] = {}
        self.per_crop_cache: dict[str, dict[str, Any]] = {}

        logger.info(f"📊 Evaluation Scorer initialized (lookback: {lookback_days} days)")

    def score_prediction(
        self,
        diagnosis_id: str,
        predicted_disease: str,
        predicted_confidence: float,
        field_id: str | None = None,
    ) -> PredictionScore:
        """
        Record a prediction for later evaluation

        Args:
            diagnosis_id: Unique diagnosis ID
            predicted_disease: Predicted disease ID
            predicted_confidence: Confidence score (0-1)
            field_id: Associated field ID

        Returns:
            PredictionScore object
        """
        score = PredictionScore(
            diagnosis_id=diagnosis_id,
            predicted_disease=predicted_disease,
            predicted_confidence=predicted_confidence,
            timestamp=datetime.utcnow(),
            field_id=field_id,
        )

        self.prediction_scores.append(score)

        # Invalidate cache
        self.metrics_cache.clear()
        self.per_disease_cache.clear()
        self.per_crop_cache.clear()

        logger.info(
            f"📌 Prediction scored: {diagnosis_id} "
            f"→ {predicted_disease} ({predicted_confidence:.1%})"
        )

        return score

    def record_outcome(
        self,
        diagnosis_id: str,
        actual_disease: str,
        notes: str | None = None,
    ) -> bool:
        """
        Record the actual outcome of a diagnosis

        This allows calculation of accuracy metrics.

        Args:
            diagnosis_id: Diagnosis ID to update
            actual_disease: Actual disease (from expert review, etc)
            notes: Optional notes on the outcome

        Returns:
            True if outcome recorded, False if diagnosis not found
        """
        for score in self.prediction_scores:
            if score.diagnosis_id == diagnosis_id:
                score.actual_disease = actual_disease
                score.correct = score.predicted_disease == actual_disease
                score.confidence_error = abs(
                    score.predicted_confidence
                    - (1.0 if score.correct else 0.0)
                )

                # Invalidate cache
                self.metrics_cache.clear()
                self.per_disease_cache.clear()
                self.per_crop_cache.clear()

                status = "✅ CORRECT" if score.correct else "❌ INCORRECT"
                logger.info(
                    f"📊 Outcome recorded: {diagnosis_id} "
                    f"({score.predicted_disease} → {actual_disease}) {status}"
                )

                return True

        logger.warning(f"⚠️  Could not find diagnosis {diagnosis_id} to record outcome")
        return False

    def get_accuracy_metrics(self, days_back: int | None = None) -> AccuracyMetrics:
        """
        Calculate accuracy metrics for evaluated predictions

        Args:
            days_back: Only include predictions from last N days

        Returns:
            AccuracyMetrics object
        """
        cache_key = f"overall_{days_back}"
        if cache_key in self.metrics_cache:
            return self.metrics_cache[cache_key]

        # Filter predictions
        scores = self._filter_evaluated_scores(days_back)

        if not scores:
            return AccuracyMetrics(
                total_predictions=0,
                correct_predictions=0,
                accuracy=0.0,
                high_confidence_accuracy=0.0,
                medium_confidence_accuracy=0.0,
                low_confidence_accuracy=0.0,
                confidence_mean=0.0,
                confidence_std=0.0,
                calibration_score=0.0,
            )

        # Basic accuracy
        total = len(scores)
        correct = sum(1 for s in scores if s.correct)
        accuracy = correct / total if total > 0 else 0.0

        # Accuracy by confidence level
        high_conf = [s for s in scores if s.predicted_confidence > 0.7]
        medium_conf = [s for s in scores if 0.5 <= s.predicted_confidence <= 0.7]
        low_conf = [s for s in scores if s.predicted_confidence < 0.5]

        high_conf_acc = sum(1 for s in high_conf if s.correct) / len(high_conf) if high_conf else 0.0
        medium_conf_acc = (
            sum(1 for s in medium_conf if s.correct) / len(medium_conf)
            if medium_conf
            else 0.0
        )
        low_conf_acc = sum(1 for s in low_conf if s.correct) / len(low_conf) if low_conf else 0.0

        # Confidence calibration
        confidences = np.array([s.predicted_confidence for s in scores])
        conf_mean = float(np.mean(confidences))
        conf_std = float(np.std(confidences))

        # Calibration: how well does confidence match actual accuracy?
        # Perfect calibration: predicted_confidence == observed_accuracy
        # Split into bins and compare
        calibration_score = self._calculate_calibration_score(scores)

        metrics = AccuracyMetrics(
            total_predictions=total,
            correct_predictions=correct,
            accuracy=accuracy,
            high_confidence_accuracy=high_conf_acc,
            medium_confidence_accuracy=medium_conf_acc,
            low_confidence_accuracy=low_conf_acc,
            confidence_mean=conf_mean,
            confidence_std=conf_std,
            calibration_score=calibration_score,
        )

        # Cache result
        self.metrics_cache[cache_key] = metrics
        return metrics

    def get_per_disease_metrics(self, days_back: int | None = None) -> dict[str, dict]:
        """
        Get accuracy metrics broken down by disease

        Args:
            days_back: Only include predictions from last N days

        Returns:
            Dict of {disease_id: metrics_dict}
        """
        cache_key = f"disease_{days_back}"
        if cache_key in self.per_disease_cache:
            return self.per_disease_cache[cache_key]

        scores = self._filter_evaluated_scores(days_back)
        disease_groups = defaultdict(list)

        for score in scores:
            disease_groups[score.predicted_disease].append(score)

        metrics = {}
        for disease_id, disease_scores in disease_groups.items():
            total = len(disease_scores)
            correct = sum(1 for s in disease_scores if s.correct)
            accuracy = correct / total if total > 0 else 0.0

            confidences = [s.predicted_confidence for s in disease_scores]

            metrics[disease_id] = {
                "samples": total,
                "correct": correct,
                "accuracy": accuracy,
                "avg_confidence": np.mean(confidences),
                "std_confidence": np.std(confidences),
                "false_positive_rate": self._calculate_fpr_for_disease(
                    disease_id, disease_scores
                ),
            }

        self.per_disease_cache[cache_key] = metrics
        return metrics

    def get_per_crop_metrics(self, days_back: int | None = None) -> dict[str, dict]:
        """
        Get accuracy metrics broken down by crop type

        Args:
            days_back: Only include predictions from last N days

        Returns:
            Dict of {crop_id: metrics_dict}
        """
        cache_key = f"crop_{days_back}"
        if cache_key in self.per_crop_cache:
            return self.per_crop_cache[cache_key]

        # Note: This requires crop_id to be tracked with predictions
        # For now, return empty dict - implement when crop tracking added
        return {}

    def detect_model_drift(self, days_back: int = 7) -> ModelDriftIndicators:
        """
        Detect if model performance is drifting

        Compares recent performance (7 days) with historical (30 days)

        Args:
            days_back: Days to use for recent comparison

        Returns:
            ModelDriftIndicators
        """
        # Recent metrics
        recent_metrics = self.get_accuracy_metrics(days_back=days_back)

        # Historical metrics
        historical_metrics = self.get_accuracy_metrics(days_back=30)

        # Calculate change
        if historical_metrics.total_predictions == 0:
            return ModelDriftIndicators(
                accuracy_7day=recent_metrics.accuracy,
                accuracy_30day=0.0,
                accuracy_change_percent=0.0,
                confidence_trend="unknown",
                false_positive_rate=0.0,
                false_negative_rate=0.0,
                drift_detected=False,
                drift_severity="none",
            )

        accuracy_change = (
            (recent_metrics.accuracy - historical_metrics.accuracy)
            / historical_metrics.accuracy
            * 100
        )

        # Detect confidence trend
        recent_scores = self._filter_evaluated_scores(days_back=days_back)
        older_scores = self._filter_evaluated_scores(
            days_back=30, start_days_back=days_back
        )

        recent_conf = (
            np.mean([s.predicted_confidence for s in recent_scores])
            if recent_scores
            else 0.5
        )
        older_conf = (
            np.mean([s.predicted_confidence for s in older_scores])
            if older_scores
            else 0.5
        )

        if recent_conf > older_conf + 0.05:
            conf_trend = "increasing"
        elif recent_conf < older_conf - 0.05:
            conf_trend = "decreasing"
        else:
            conf_trend = "stable"

        # Calculate error rates
        fpr = self._calculate_overall_fpr(recent_scores)
        fnr = self._calculate_overall_fnr(recent_scores)

        # Determine drift severity
        if accuracy_change < -10:
            drift_detected = True
            severity = "severe"
        elif accuracy_change < -5:
            drift_detected = True
            severity = "moderate"
        elif accuracy_change < -2:
            drift_detected = True
            severity = "mild"
        else:
            drift_detected = False
            severity = "none"

        indicators = ModelDriftIndicators(
            accuracy_7day=recent_metrics.accuracy,
            accuracy_30day=historical_metrics.accuracy,
            accuracy_change_percent=accuracy_change,
            confidence_trend=conf_trend,
            false_positive_rate=fpr,
            false_negative_rate=fnr,
            drift_detected=drift_detected,
            drift_severity=severity,
        )

        if drift_detected:
            logger.warning(
                f"⚠️  Model drift detected ({severity}): "
                f"Accuracy changed {accuracy_change:+.1f}%"
            )

        return indicators

    def get_evaluation_report(self, days_back: int = 30) -> dict[str, Any]:
        """
        Generate comprehensive evaluation report

        Args:
            days_back: Report period in days

        Returns:
            Comprehensive evaluation report
        """
        overall_metrics = self.get_accuracy_metrics(days_back=days_back)
        disease_metrics = self.get_per_disease_metrics(days_back=days_back)
        drift = self.detect_model_drift(days_back=7)

        # Top performing diseases
        top_diseases = sorted(
            disease_metrics.items(),
            key=lambda x: x[1]["accuracy"],
            reverse=True,
        )[:5]

        # Worst performing diseases
        worst_diseases = sorted(
            disease_metrics.items(),
            key=lambda x: x[1]["accuracy"],
        )[:5]

        report = {
            "report_period_days": days_back,
            "generated_at": datetime.utcnow().isoformat(),
            "overall_metrics": {
                "total_evaluated": overall_metrics.total_predictions,
                "accuracy": f"{overall_metrics.accuracy:.1%}",
                "correct_predictions": overall_metrics.correct_predictions,
                "high_conf_accuracy": f"{overall_metrics.high_confidence_accuracy:.1%}",
                "medium_conf_accuracy": f"{overall_metrics.medium_confidence_accuracy:.1%}",
                "low_conf_accuracy": f"{overall_metrics.low_confidence_accuracy:.1%}",
                "confidence_calibration": f"{overall_metrics.calibration_score:.2f}",
            },
            "per_disease_performance": {
                "top_5": [
                    {
                        "disease": disease,
                        "accuracy": f"{metrics['accuracy']:.1%}",
                        "samples": metrics["samples"],
                    }
                    for disease, metrics in top_diseases
                ],
                "worst_5": [
                    {
                        "disease": disease,
                        "accuracy": f"{metrics['accuracy']:.1%}",
                        "samples": metrics["samples"],
                    }
                    for disease, metrics in worst_diseases
                ],
                "total_diseases_evaluated": len(disease_metrics),
            },
            "model_drift_indicators": {
                "7day_accuracy": f"{drift.accuracy_7day:.1%}",
                "30day_accuracy": f"{drift.accuracy_30day:.1%}",
                "accuracy_change": f"{drift.accuracy_change_percent:+.1f}%",
                "confidence_trend": drift.confidence_trend,
                "false_positive_rate": f"{drift.false_positive_rate:.1%}",
                "false_negative_rate": f"{drift.false_negative_rate:.1%}",
                "drift_detected": drift.drift_detected,
                "drift_severity": drift.drift_severity,
            },
            "recommendations": self._generate_recommendations(
                overall_metrics, drift, disease_metrics
            ),
        }

        return report

    def _filter_evaluated_scores(
        self,
        days_back: int | None = None,
        start_days_back: int | None = None,
    ) -> list[PredictionScore]:
        """
        Filter prediction scores by date and evaluation status

        Args:
            days_back: Include predictions from last N days
            start_days_back: Start from N days back (for ranges)

        Returns:
            List of evaluated scores
        """
        now = datetime.utcnow()
        scores = []

        for score in self.prediction_scores:
            # Must have outcome recorded
            if score.actual_disease is None:
                continue

            # Check date range
            if score.timestamp is None:
                continue

            if days_back:
                cutoff = now - timedelta(days=days_back)
                if score.timestamp < cutoff:
                    continue

            if start_days_back:
                start = now - timedelta(days=start_days_back)
                if score.timestamp > start:
                    continue

            scores.append(score)

        return scores

    def _calculate_calibration_score(self, scores: list[PredictionScore]) -> float:
        """
        Calculate how well confidence matches observed accuracy

        Range: 0-1, where 1 = perfectly calibrated

        Uses Expected Calibration Error (ECE) metric
        """
        if not scores:
            return 0.0

        # Bin predictions by confidence
        bins = [(0.0, 0.1), (0.1, 0.2), (0.2, 0.3), (0.3, 0.4), (0.4, 0.5),
                (0.5, 0.6), (0.6, 0.7), (0.7, 0.8), (0.8, 0.9), (0.9, 1.0)]

        ece = 0.0
        total = len(scores)

        for bin_min, bin_max in bins:
            bin_scores = [
                s for s in scores
                if bin_min <= s.predicted_confidence < bin_max
            ]

            if bin_scores:
                bin_accuracy = sum(1 for s in bin_scores if s.correct) / len(
                    bin_scores
                )
                bin_confidence = np.mean(
                    [s.predicted_confidence for s in bin_scores]
                )
                bin_size = len(bin_scores) / total

                ece += abs(bin_accuracy - bin_confidence) * bin_size

        # Convert to 0-1 score (1 = perfect)
        calibration = 1.0 - ece
        return max(0.0, min(1.0, calibration))

    def _calculate_fpr_for_disease(
        self,
        disease_id: str,
        scores: list[PredictionScore],
    ) -> float:
        """False positive rate for a disease"""
        fp = sum(
            1 for s in scores
            if s.predicted_disease == disease_id and s.actual_disease != disease_id
        )
        neg = sum(1 for s in scores if s.actual_disease != disease_id)
        return fp / neg if neg > 0 else 0.0

    def _calculate_overall_fpr(self, scores: list[PredictionScore]) -> float:
        """Overall false positive rate"""
        fp = sum(
            1 for s in scores
            if s.predicted_disease != "healthy" and s.actual_disease == "healthy"
        )
        return fp / len(scores) if scores else 0.0

    def _calculate_overall_fnr(self, scores: list[PredictionScore]) -> float:
        """Overall false negative rate"""
        fn = sum(
            1 for s in scores
            if s.predicted_disease == "healthy"
            and s.actual_disease != "healthy"
        )
        diseased = sum(1 for s in scores if s.actual_disease != "healthy")
        return fn / diseased if diseased > 0 else 0.0

    def _generate_recommendations(
        self,
        metrics: AccuracyMetrics,
        drift: ModelDriftIndicators,
        disease_metrics: dict,
    ) -> list[str]:
        """Generate recommendations based on evaluation"""
        recommendations = []

        if metrics.accuracy < 0.7:
            recommendations.append(
                "Overall accuracy below 70%. Consider model retraining."
            )

        if drift.drift_detected:
            recommendations.append(
                f"Model drift detected ({drift.drift_severity}). Monitor performance closely."
            )

        if metrics.calibration_score < 0.5:
            recommendations.append(
                "Confidence calibration poor. Model may be over/under-confident."
            )

        if metrics.high_confidence_accuracy < 0.5:
            recommendations.append("High-confidence predictions are often wrong. Reduce confidence thresholds or retrain.")

        if disease_metrics:
            worst = min(disease_metrics.items(), key=lambda x: x[1]["accuracy"])
            if worst[1]["accuracy"] < 0.5 and worst[1]["samples"] > 10:
                recommendations.append(
                    f"Poor accuracy on {worst[0]}. Consider additional training data."
                )

        if not recommendations:
            recommendations.append("Model performance is healthy. No action needed.")

        return recommendations

    def get_statistics_summary(self) -> dict[str, Any]:
        """Get summary statistics of all recorded predictions"""
        return {
            "total_predictions": len(self.prediction_scores),
            "evaluated_predictions": len(self._filter_evaluated_scores()),
            "unevaluated_predictions": (
                len(self.prediction_scores)
                - len(self._filter_evaluated_scores())
            ),
            "evaluation_rate": (
                len(self._filter_evaluated_scores()) / len(self.prediction_scores)
                if self.prediction_scores
                else 0.0
            ),
            "timestamp": datetime.utcnow().isoformat(),
        }


# Singleton instance
evaluation_scorer = EvaluationScorer(lookback_days=90)
