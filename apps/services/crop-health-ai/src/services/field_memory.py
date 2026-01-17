"""
Field Memory Service
خدمة ذاكرة الحقل

Maintains persistent memory of disease patterns per field
for contextual disease prediction and historical tracking.

Features:
- Per-field disease history tracking
- Temporal pattern analysis
- Field health scoring
- Seasonal disease prediction
- Disease frequency analysis
"""

import logging
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

logger = logging.getLogger("sahool-vision")


@dataclass
class FieldDiagnosisRecord:
    """Single diagnosis record for a field"""

    diagnosis_id: str
    disease_id: str
    disease_name_ar: str
    confidence: float
    severity: str
    timestamp: datetime
    affected_area_percent: float
    treated: bool = False


@dataclass
class FieldHealthMetrics:
    """Calculated metrics for field health"""

    field_id: str
    total_diagnoses: int
    healthy_diagnoses: int
    infected_diagnoses: int
    health_score: float  # 0-1, higher is healthier
    infection_trend: str  # 'improving', 'stable', 'worsening'
    dominant_disease: str | None
    disease_variety: int
    avg_confidence: float
    last_updated: datetime


@dataclass
class DiseasePattern:
    """Pattern of disease occurrence"""

    disease_id: str
    disease_name_ar: str
    occurrence_count: int
    avg_confidence: float
    severity_levels: dict[str, int]  # {severity: count}
    last_occurred: datetime
    days_between_occurrences: list[int]
    avg_severity: str


class FieldMemory:
    """
    Memory store for field-specific disease patterns

    This service maintains historical records per field, enabling
    contextual diagnosis and pattern recognition.
    """

    def __init__(self, max_records_per_field: int = 100):
        # Store last N diagnoses per field
        self.max_records = max_records_per_field

        # {field_id: deque of FieldDiagnosisRecord}
        self.field_histories: dict[str, deque] = defaultdict(
            lambda: deque(maxlen=max_records_per_field)
        )

        # Cache for metrics
        self.field_metrics_cache: dict[str, FieldHealthMetrics] = {}
        self.patterns_cache: dict[str, dict[str, DiseasePattern]] = {}

        logger.info(f"🧠 Field Memory initialized (max {max_records_per_field} records per field)")

    def record_diagnosis(
        self,
        field_id: str,
        diagnosis_id: str,
        disease_id: str,
        disease_name_ar: str,
        confidence: float,
        severity: str,
        affected_area_percent: float,
    ) -> FieldDiagnosisRecord:
        """
        Record a new diagnosis in field memory

        Args:
            field_id: Unique field identifier
            diagnosis_id: Diagnosis ID
            disease_id: Disease identifier
            disease_name_ar: Arabic disease name
            confidence: Prediction confidence (0-1)
            severity: Disease severity level
            affected_area_percent: Affected area percentage

        Returns:
            FieldDiagnosisRecord created
        """
        record = FieldDiagnosisRecord(
            diagnosis_id=diagnosis_id,
            disease_id=disease_id,
            disease_name_ar=disease_name_ar,
            confidence=confidence,
            severity=severity,
            timestamp=datetime.utcnow(),
            affected_area_percent=affected_area_percent,
        )

        self.field_histories[field_id].append(record)

        # Invalidate cache
        self.field_metrics_cache.pop(field_id, None)
        self.patterns_cache.pop(field_id, None)

        logger.info(
            f"📝 Field {field_id}: Recorded {disease_id} "
            f"(confidence: {confidence:.1%}, severity: {severity})"
        )

        return record

    def get_field_history(
        self,
        field_id: str,
        limit: int | None = None,
        days_back: int | None = None,
    ) -> list[FieldDiagnosisRecord]:
        """
        Get diagnosis history for a field

        Args:
            field_id: Field identifier
            limit: Max records to return
            days_back: Only return records from last N days

        Returns:
            List of FieldDiagnosisRecord
        """
        history = list(self.field_histories[field_id])

        # Filter by date if specified
        if days_back:
            cutoff_date = datetime.utcnow() - timedelta(days=days_back)
            history = [r for r in history if r.timestamp >= cutoff_date]

        # Apply limit (most recent first)
        if limit:
            history = history[-limit:]

        return list(reversed(history))  # Most recent first

    def get_disease_patterns(self, field_id: str) -> dict[str, DiseasePattern]:
        """
        Analyze disease patterns for a field

        Args:
            field_id: Field identifier

        Returns:
            Dict of {disease_id: DiseasePattern}
        """
        # Check cache
        if field_id in self.patterns_cache:
            return self.patterns_cache[field_id]

        patterns = {}
        history = list(self.field_histories[field_id])

        if not history:
            return patterns

        # Group by disease
        disease_records = defaultdict(list)
        for record in history:
            if record.disease_id != "healthy":
                disease_records[record.disease_id].append(record)

        # Analyze each disease
        for disease_id, records in disease_records.items():
            # Calculate metrics
            timestamps = [r.timestamp for r in records]
            confidences = [r.confidence for r in records]
            severities = [r.severity for r in records]

            # Days between occurrences
            days_between = []
            for i in range(1, len(timestamps)):
                delta = (timestamps[i - 1] - timestamps[i]).days
                if delta > 0:
                    days_between.append(delta)

            # Severity distribution
            severity_dist = {}
            for severity in severities:
                severity_dist[severity] = severity_dist.get(severity, 0) + 1

            # Most common severity
            avg_severity = max(severity_dist.keys(), key=lambda k: severity_dist[k])

            pattern = DiseasePattern(
                disease_id=disease_id,
                disease_name_ar=records[0].disease_name_ar,
                occurrence_count=len(records),
                avg_confidence=sum(confidences) / len(confidences),
                severity_levels=severity_dist,
                last_occurred=max(timestamps),
                days_between_occurrences=days_between,
                avg_severity=avg_severity,
            )

            patterns[disease_id] = pattern

        # Cache result
        self.patterns_cache[field_id] = patterns

        logger.info(
            f"🔍 Field {field_id}: Analyzed {len(patterns)} disease patterns "
            f"from {len(history)} diagnoses"
        )

        return patterns

    def calculate_field_metrics(self, field_id: str) -> FieldHealthMetrics:
        """
        Calculate comprehensive health metrics for a field

        Args:
            field_id: Field identifier

        Returns:
            FieldHealthMetrics with computed values
        """
        # Check cache
        if field_id in self.field_metrics_cache:
            return self.field_metrics_cache[field_id]

        history = list(self.field_histories[field_id])

        if not history:
            # Default metrics for new field
            metrics = FieldHealthMetrics(
                field_id=field_id,
                total_diagnoses=0,
                healthy_diagnoses=0,
                infected_diagnoses=0,
                health_score=1.0,  # Assume healthy
                infection_trend="unknown",
                dominant_disease=None,
                disease_variety=0,
                avg_confidence=0.0,
                last_updated=datetime.utcnow(),
            )
            self.field_metrics_cache[field_id] = metrics
            return metrics

        # Count diagnoses
        total = len(history)
        healthy = sum(1 for r in history if r.disease_id == "healthy")
        infected = total - healthy

        # Health score (ratio of healthy diagnoses)
        health_score = healthy / total if total > 0 else 1.0

        # Infection trend (compare first half vs second half)
        mid = total // 2
        first_half_healthy = sum(
            1 for r in history[-mid:] if r.disease_id == "healthy"
        )
        second_half_healthy = sum(
            1 for r in history[:mid] if r.disease_id == "healthy"
        )
        first_ratio = first_half_healthy / mid if mid > 0 else 0
        second_ratio = second_half_healthy / mid if mid > 0 else 0

        if second_ratio > first_ratio + 0.1:
            trend = "improving"
        elif second_ratio < first_ratio - 0.1:
            trend = "worsening"
        else:
            trend = "stable"

        # Dominant disease
        patterns = self.get_disease_patterns(field_id)
        dominant = None
        if patterns:
            dominant = max(patterns.items(), key=lambda x: x[1].occurrence_count)[0]

        # Average confidence
        confidences = [r.confidence for r in history]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        metrics = FieldHealthMetrics(
            field_id=field_id,
            total_diagnoses=total,
            healthy_diagnoses=healthy,
            infected_diagnoses=infected,
            health_score=health_score,
            infection_trend=trend,
            dominant_disease=dominant,
            disease_variety=len(patterns),
            avg_confidence=avg_confidence,
            last_updated=datetime.utcnow(),
        )

        # Cache result
        self.field_metrics_cache[field_id] = metrics

        return metrics

    def predict_disease_likelihood(
        self,
        field_id: str,
        disease_id: str,
        days_ahead: int = 7,
    ) -> dict[str, Any]:
        """
        Predict likelihood of disease recurrence based on patterns

        Args:
            field_id: Field identifier
            disease_id: Disease to predict
            days_ahead: How many days ahead to predict

        Returns:
            Dict with likelihood score and reasoning
        """
        patterns = self.get_disease_patterns(field_id)

        if disease_id not in patterns:
            return {
                "disease_id": disease_id,
                "likelihood": 0.0,
                "reasoning": "Disease not found in field history",
                "confidence": "low",
            }

        pattern = patterns[disease_id]

        # Calculate likelihood based on:
        # 1. Recurrence frequency
        # 2. Time since last occurrence
        # 3. Severity trend

        # Average days between occurrences
        if pattern.days_between_occurrences:
            avg_days_between = sum(pattern.days_between_occurrences) / len(
                pattern.days_between_occurrences
            )
        else:
            avg_days_between = 30  # Default assumption

        # Days since last occurrence
        last_occurrence = pattern.last_occurred
        days_since = (datetime.utcnow() - last_occurrence).days

        # Likelihood is higher if:
        # - Time since last = ~expected interval
        # - High historical confidence
        # - Disease previously appeared multiple times

        # Normalize likelihood (0-1)
        if avg_days_between > 0:
            # Peak at expected interval
            interval_ratio = days_since / avg_days_between
            if 0.5 < interval_ratio < 2.0:
                likelihood = 0.7 * min(interval_ratio, 2 - interval_ratio)
            else:
                likelihood = 0.0
        else:
            likelihood = 0.5

        # Boost likelihood based on historical confidence
        likelihood *= pattern.avg_confidence

        # Boost if multiple occurrences
        if pattern.occurrence_count >= 3:
            likelihood = min(likelihood * 1.2, 1.0)

        return {
            "disease_id": disease_id,
            "disease_name_ar": pattern.disease_name_ar,
            "likelihood": min(likelihood, 1.0),
            "confidence": "high" if pattern.occurrence_count >= 3 else "medium",
            "reasoning": (
                f"Based on {pattern.occurrence_count} occurrences, "
                f"typically {avg_days_between:.0f} days apart"
            ),
            "days_since_last": days_since,
            "avg_interval_days": avg_days_between,
            "predicted_days_ahead": days_ahead,
        }

    def get_field_risk_assessment(self, field_id: str) -> dict[str, Any]:
        """
        Comprehensive risk assessment for field

        Args:
            field_id: Field identifier

        Returns:
            Risk assessment with overall score and disease-specific risks
        """
        metrics = self.calculate_field_metrics(field_id)
        patterns = self.get_disease_patterns(field_id)

        # Calculate overall risk (inverse of health score)
        overall_risk = 1.0 - metrics.health_score

        # Boost risk if worsening trend
        if metrics.infection_trend == "worsening":
            overall_risk = min(overall_risk * 1.3, 1.0)
        elif metrics.infection_trend == "improving":
            overall_risk = max(overall_risk * 0.7, 0.0)

        # Disease-specific risks
        disease_risks = []
        for disease_id, pattern in patterns.items():
            prediction = self.predict_disease_likelihood(field_id, disease_id, days_ahead=7)
            disease_risks.append(
                {
                    "disease_id": disease_id,
                    "disease_name_ar": pattern.disease_name_ar,
                    "risk_score": prediction["likelihood"],
                    "occurrences": pattern.occurrence_count,
                    "severity": pattern.avg_severity,
                }
            )

        # Sort by risk
        disease_risks.sort(key=lambda x: x["risk_score"], reverse=True)

        return {
            "field_id": field_id,
            "overall_risk_score": overall_risk,
            "risk_level": (
                "critical"
                if overall_risk > 0.7
                else "high"
                if overall_risk > 0.5
                else "medium"
                if overall_risk > 0.3
                else "low"
            ),
            "health_trend": metrics.infection_trend,
            "field_health_score": metrics.health_score,
            "disease_variety": metrics.disease_variety,
            "top_threats": disease_risks[:5],
            "last_updated": metrics.last_updated.isoformat(),
        }

    def mark_diagnosis_treated(self, field_id: str, diagnosis_id: str) -> bool:
        """
        Mark a diagnosis as treated (for tracking intervention success)

        Args:
            field_id: Field identifier
            diagnosis_id: Diagnosis to mark as treated

        Returns:
            True if marked, False if not found
        """
        for record in self.field_histories[field_id]:
            if record.diagnosis_id == diagnosis_id:
                record.treated = True
                # Invalidate cache
                self.field_metrics_cache.pop(field_id, None)
                logger.info(f"✅ Marked {diagnosis_id} as treated in field {field_id}")
                return True
        return False

    def get_treatment_effectiveness(self, field_id: str) -> dict[str, Any]:
        """
        Calculate treatment effectiveness for field

        Args:
            field_id: Field identifier

        Returns:
            Treatment effectiveness metrics
        """
        history = list(self.field_histories[field_id])

        if not history:
            return {
                "field_id": field_id,
                "treatments_applied": 0,
                "effectiveness_rate": 0.0,
                "avg_recovery_days": 0,
            }

        # Find treated diagnoses followed by healthy diagnoses
        treated_diagnoses = [r for r in history if r.treated]
        successful_treatments = 0
        recovery_times = []

        for treated in treated_diagnoses:
            # Find next diagnosis
            treated_idx = history.index(treated)
            if treated_idx > 0:
                next_diagnosis = history[treated_idx - 1]
                if next_diagnosis.disease_id == "healthy":
                    successful_treatments += 1
                    recovery_days = (next_diagnosis.timestamp - treated.timestamp).days
                    recovery_times.append(recovery_days)

        effectiveness_rate = (
            successful_treatments / len(treated_diagnoses)
            if treated_diagnoses
            else 0.0
        )
        avg_recovery = (
            sum(recovery_times) / len(recovery_times) if recovery_times else 0
        )

        return {
            "field_id": field_id,
            "treatments_applied": len(treated_diagnoses),
            "successful_treatments": successful_treatments,
            "effectiveness_rate": effectiveness_rate,
            "avg_recovery_days": avg_recovery,
            "total_diagnoses": len(history),
        }

    def clear_field_history(self, field_id: str) -> bool:
        """Clear all history for a field (use with caution)"""
        if field_id in self.field_histories:
            self.field_histories[field_id].clear()
            self.field_metrics_cache.pop(field_id, None)
            self.patterns_cache.pop(field_id, None)
            logger.warning(f"⚠️  Cleared all history for field {field_id}")
            return True
        return False

    def get_all_fields_summary(self) -> dict[str, Any]:
        """Get summary statistics across all fields"""
        all_metrics = [
            self.calculate_field_metrics(field_id) for field_id in self.field_histories
        ]

        if not all_metrics:
            return {
                "total_fields": 0,
                "total_diagnoses": 0,
                "avg_health_score": 0.0,
            }

        total_diagnoses = sum(m.total_diagnoses for m in all_metrics)
        avg_health = sum(m.health_score for m in all_metrics) / len(all_metrics)

        return {
            "total_fields": len(all_metrics),
            "total_diagnoses": total_diagnoses,
            "avg_health_score": avg_health,
            "fields_at_risk": sum(1 for m in all_metrics if m.health_score < 0.5),
            "timestamp": datetime.utcnow().isoformat(),
        }


# Singleton instance
field_memory = FieldMemory(max_records_per_field=100)
