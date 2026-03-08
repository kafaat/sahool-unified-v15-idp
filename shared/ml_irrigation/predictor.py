"""
ML Irrigation Predictor
=======================
نظام التنبؤ بالري باستخدام التعلم الآلي

Machine learning-based irrigation need prediction including:
- Multi-factor irrigation need assessment
- Timing optimization
- Confidence scoring
- Bilingual recommendations (Arabic/English)

Supports both rule-based and ML model predictions with
ensemble methods for improved accuracy.

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any, Protocol

from .models import (
    CropFeatures,
    CropStage,
    IrrigationFeatures,
    IrrigationPrediction,
    IrrigationRecord,
    IrrigationType,
    IrrigationUrgency,
    PredictionConfidence,
    SoilFeatures,
    WeatherFeatures,
)

logger = logging.getLogger(__name__)


class MLModel(Protocol):
    """Protocol for ML models (sklearn-compatible interface)"""

    def predict(self, X: list[list[float]]) -> list[float]:
        """Predict irrigation amount"""
        ...

    def predict_proba(self, X: list[list[float]]) -> list[list[float]]:
        """Predict probabilities for classification"""
        ...


@dataclass
class PredictorConfig:
    """
    Configuration for irrigation predictor
    إعدادات نظام التنبؤ بالري
    """

    # Thresholds
    moisture_critical_threshold: float = 25.0  # % - Critical moisture level
    moisture_low_threshold: float = 40.0  # % - Low moisture trigger
    moisture_optimal_threshold: float = 60.0  # % - Optimal moisture level

    # Depletion allowances by crop stage
    depletion_allowances: dict[str, float] = field(
        default_factory=lambda: {
            "germination": 0.25,
            "seedling": 0.30,
            "vegetative": 0.40,
            "tillering": 0.45,
            "flowering": 0.35,
            "grain_fill": 0.40,
            "maturity": 0.55,
            "harvest": 0.60,
        }
    )

    # Weather adjustments
    rain_probability_threshold: float = 60.0  # % - Delay irrigation if rain likely
    high_temp_threshold: float = 35.0  # Celsius - Increase water need
    high_wind_threshold: float = 25.0  # km/h - Avoid sprinkler irrigation

    # System efficiencies
    irrigation_efficiencies: dict[str, float] = field(
        default_factory=lambda: {
            "drip": 0.90,
            "sprinkler": 0.75,
            "flood": 0.50,
            "center_pivot": 0.85,
            "furrow": 0.55,
            "subsurface": 0.95,
        }
    )

    # Prediction settings
    default_confidence: float = 0.75
    min_irrigation_amount_mm: float = 5.0  # Minimum practical amount
    max_irrigation_amount_mm: float = 100.0  # Maximum single application

    # Model settings
    use_ml_model: bool = False
    model_weight: float = 0.6  # Weight for ML model vs rule-based
    rule_weight: float = 0.4


# Crop coefficient data by growth stage
CROP_COEFFICIENTS: dict[str, dict[str, float]] = {
    "wheat": {
        "germination": 0.35,
        "seedling": 0.45,
        "vegetative": 0.75,
        "tillering": 0.95,
        "flowering": 1.15,
        "grain_fill": 1.05,
        "maturity": 0.65,
        "harvest": 0.35,
    },
    "barley": {
        "germination": 0.30,
        "seedling": 0.40,
        "vegetative": 0.70,
        "tillering": 0.90,
        "flowering": 1.10,
        "grain_fill": 1.00,
        "maturity": 0.60,
        "harvest": 0.30,
    },
    "tomato": {
        "germination": 0.40,
        "seedling": 0.50,
        "vegetative": 0.80,
        "flowering": 1.10,
        "grain_fill": 1.05,
        "maturity": 0.80,
        "harvest": 0.60,
    },
    "date_palm": {
        "germination": 0.90,
        "vegetative": 0.95,
        "flowering": 1.00,
        "grain_fill": 0.95,
        "maturity": 0.90,
    },
    "default": {
        "germination": 0.35,
        "seedling": 0.50,
        "vegetative": 0.80,
        "tillering": 0.90,
        "flowering": 1.10,
        "grain_fill": 1.00,
        "maturity": 0.70,
        "harvest": 0.40,
    },
}

# Bilingual urgency messages
URGENCY_MESSAGES = {
    IrrigationUrgency.CRITICAL: {
        "en": "CRITICAL: Irrigate immediately to prevent crop damage",
        "ar": "حرج: قم بالري فوراً لمنع ضرر المحصول",
    },
    IrrigationUrgency.HIGH: {
        "en": "HIGH: Irrigation needed within 6 hours",
        "ar": "عالي: الري مطلوب خلال 6 ساعات",
    },
    IrrigationUrgency.MEDIUM: {
        "en": "MEDIUM: Schedule irrigation within 24 hours",
        "ar": "متوسط: جدول الري خلال 24 ساعة",
    },
    IrrigationUrgency.LOW: {
        "en": "LOW: Irrigation can be scheduled within 2-3 days",
        "ar": "منخفض: يمكن جدولة الري خلال 2-3 أيام",
    },
    IrrigationUrgency.NONE: {
        "en": "No irrigation needed at this time",
        "ar": "لا حاجة للري في الوقت الحالي",
    },
}


class IrrigationPredictor:
    """
    ML-based irrigation prediction engine
    محرك التنبؤ بالري باستخدام التعلم الآلي

    Combines rule-based agronomic calculations with ML models
    for accurate irrigation need prediction.

    Features:
    - Multi-factor analysis (weather, soil, crop)
    - Confidence scoring
    - Optimal timing recommendations
    - Bilingual output (Arabic/English)
    - Support for custom ML models

    Usage:
        predictor = IrrigationPredictor()

        # Create features
        features = IrrigationFeatures(
            weather=weather_data,
            soil=soil_data,
            crop=crop_data,
            irrigation_type=IrrigationType.DRIP,
            system_efficiency=0.90,
        )

        # Get prediction
        prediction = predictor.predict(features)

        print(f"Irrigation needed: {prediction.irrigation_needed}")
        print(f"Amount: {prediction.recommended_amount_mm}mm")
        print(f"Urgency: {prediction.urgency.value}")
    """

    def __init__(
        self,
        config: PredictorConfig | None = None,
        ml_model: MLModel | None = None,
    ):
        """
        Initialize the irrigation predictor

        Args:
            config: Predictor configuration
            ml_model: Optional sklearn-compatible ML model
        """
        self.config = config or PredictorConfig()
        self.ml_model = ml_model

    def predict(
        self,
        features: IrrigationFeatures,
        historical_records: list[IrrigationRecord] | None = None,
    ) -> IrrigationPrediction:
        """
        Predict irrigation needs based on input features
        التنبؤ باحتياجات الري بناءً على الميزات المدخلة

        Args:
            features: Combined irrigation features
            historical_records: Optional historical irrigation records

        Returns:
            IrrigationPrediction with recommendations
        """
        # Calculate rule-based prediction
        rule_prediction = self._rule_based_prediction(features)

        # Calculate ML prediction if model available
        ml_prediction = None
        if self.ml_model and self.config.use_ml_model:
            ml_prediction = self._ml_prediction(features)

        # Combine predictions
        final_prediction = self._combine_predictions(
            rule_prediction,
            ml_prediction,
            features,
        )

        # Adjust for historical patterns if available
        if historical_records:
            final_prediction = self._adjust_for_history(
                final_prediction,
                historical_records,
                features,
            )

        # Generate recommendation text
        final_prediction = self._generate_recommendations(final_prediction, features)

        return final_prediction

    def _rule_based_prediction(
        self,
        features: IrrigationFeatures,
    ) -> IrrigationPrediction:
        """
        Calculate irrigation need using agronomic rules
        حساب احتياج الري باستخدام القواعد الزراعية
        """
        # Get crop coefficient
        kc = self._get_crop_coefficient(
            features.crop.crop_type,
            features.crop.growth_stage,
        )

        # Calculate crop water requirement (ETc)
        etc = features.weather.et0 * kc

        # Calculate soil moisture deficit
        soil = features.soil
        depletion = soil.depletion_fraction

        # Get allowable depletion for crop stage
        allowable_depletion = self.config.depletion_allowances.get(
            features.crop.growth_stage.value,
            0.45,
        )

        # Determine if irrigation needed
        irrigation_needed = depletion >= allowable_depletion

        # Calculate irrigation amount
        if irrigation_needed:
            # Calculate net irrigation requirement
            root_zone_depth_m = features.crop.root_depth_cm / 100
            deficit_mm = (
                soil.moisture_deficit * root_zone_depth_m * 10  # Convert to mm
            )

            # Account for effective rainfall
            effective_rain = self._calculate_effective_rain(features.weather)
            deficit_mm = max(0, deficit_mm - effective_rain)

            # Adjust for system efficiency
            efficiency = self.config.irrigation_efficiencies.get(
                features.irrigation_type.value,
                features.system_efficiency,
            )
            gross_amount = deficit_mm / efficiency if efficiency > 0 else deficit_mm

            # Apply limits
            recommended_amount = max(
                self.config.min_irrigation_amount_mm,
                min(gross_amount, self.config.max_irrigation_amount_mm),
            )
        else:
            recommended_amount = 0.0

        # Determine urgency
        urgency = self._determine_urgency(
            features.soil,
            features.weather,
            features.crop,
            depletion,
        )

        # Calculate confidence
        confidence = self._calculate_confidence(features)

        # Determine optimal timing
        optimal_time = self._determine_optimal_timing(features)

        return IrrigationPrediction(
            request_id=features.request_id,
            irrigation_needed=irrigation_needed,
            recommended_amount_mm=round(recommended_amount, 1),
            urgency=urgency,
            optimal_time=optimal_time,
            confidence=confidence,
            confidence_level=self._confidence_to_level(confidence),
            model_name="rule_based",
            model_version="1.0.0",
            factors=self._extract_factors(features, etc, depletion),
        )

    def _ml_prediction(
        self,
        features: IrrigationFeatures,
    ) -> IrrigationPrediction | None:
        """
        Calculate irrigation need using ML model
        حساب احتياج الري باستخدام نموذج التعلم الآلي
        """
        if not self.ml_model:
            return None

        try:
            # Convert features to vector
            X = [features.to_feature_vector()]

            # Get prediction
            prediction = self.ml_model.predict(X)[0]

            # Get probability if available
            try:
                proba = self.ml_model.predict_proba(X)[0]
                confidence = max(proba)
            except (AttributeError, NotImplementedError):
                confidence = self.config.default_confidence

            # Interpret prediction
            irrigation_needed = prediction > self.config.min_irrigation_amount_mm
            recommended_amount = max(0, min(prediction, self.config.max_irrigation_amount_mm))

            return IrrigationPrediction(
                request_id=features.request_id,
                irrigation_needed=irrigation_needed,
                recommended_amount_mm=round(recommended_amount, 1),
                urgency=self._amount_to_urgency(recommended_amount),
                confidence=confidence,
                confidence_level=self._confidence_to_level(confidence),
                model_name="ml_model",
                model_version="1.0.0",
            )

        except Exception as e:
            logger.warning(f"ML prediction failed: {e}")
            return None

    def _combine_predictions(
        self,
        rule_pred: IrrigationPrediction,
        ml_pred: IrrigationPrediction | None,
        features: IrrigationFeatures,
    ) -> IrrigationPrediction:
        """Combine rule-based and ML predictions"""
        if ml_pred is None:
            return rule_pred

        # Weighted average of amounts
        combined_amount = (
            self.config.rule_weight * rule_pred.recommended_amount_mm
            + self.config.model_weight * ml_pred.recommended_amount_mm
        )

        # Use higher confidence prediction for binary decision
        if ml_pred.confidence > rule_pred.confidence:
            irrigation_needed = ml_pred.irrigation_needed
            urgency = ml_pred.urgency
        else:
            irrigation_needed = rule_pred.irrigation_needed
            urgency = rule_pred.urgency

        # Average confidence
        combined_confidence = (
            self.config.rule_weight * rule_pred.confidence + self.config.model_weight * ml_pred.confidence
        )

        return IrrigationPrediction(
            request_id=features.request_id,
            irrigation_needed=irrigation_needed,
            recommended_amount_mm=round(combined_amount, 1),
            urgency=urgency,
            optimal_time=rule_pred.optimal_time,
            confidence=combined_confidence,
            confidence_level=self._confidence_to_level(combined_confidence),
            model_name="ensemble",
            model_version="1.0.0",
            factors=rule_pred.factors,
        )

    def _adjust_for_history(
        self,
        prediction: IrrigationPrediction,
        records: list[IrrigationRecord],
        features: IrrigationFeatures,
    ) -> IrrigationPrediction:
        """Adjust prediction based on historical patterns"""
        if not records:
            return prediction

        # Calculate historical average amount
        recent_records = [r for r in records if r.irrigation_date > datetime.now(UTC) - timedelta(days=30)]

        if not recent_records:
            return prediction

        avg_amount = sum(r.amount_mm for r in recent_records) / len(recent_records)
        avg_effectiveness = sum(r.effectiveness_rating for r in recent_records if r.effectiveness_rating)
        if avg_effectiveness:
            avg_effectiveness /= len([r for r in recent_records if r.effectiveness_rating])

        # Adjust amount based on historical effectiveness
        if avg_effectiveness and avg_effectiveness < 3.5:
            # Historical irrigations were less effective, increase amount
            adjustment = 1.0 + (3.5 - avg_effectiveness) * 0.1
            prediction.recommended_amount_mm = round(prediction.recommended_amount_mm * adjustment, 1)
        elif avg_effectiveness and avg_effectiveness > 4.5:
            # Historical irrigations were very effective, slight decrease
            prediction.recommended_amount_mm = round(prediction.recommended_amount_mm * 0.95, 1)

        # Increase confidence if historical pattern matches prediction
        if abs(prediction.recommended_amount_mm - avg_amount) < avg_amount * 0.2:
            prediction.confidence = min(0.95, prediction.confidence + 0.1)
            prediction.confidence_level = self._confidence_to_level(prediction.confidence)

        return prediction

    def _generate_recommendations(
        self,
        prediction: IrrigationPrediction,
        features: IrrigationFeatures,
    ) -> IrrigationPrediction:
        """Generate bilingual recommendation text"""
        # Base recommendation from urgency
        urgency_msg = URGENCY_MESSAGES[prediction.urgency]
        prediction.recommendation = urgency_msg["en"]
        prediction.recommendation_ar = urgency_msg["ar"]

        # Build detailed reasoning
        reasoning_en = []
        reasoning_ar = []

        # Soil moisture status
        moisture = features.soil.moisture_current
        if moisture < self.config.moisture_critical_threshold:
            reasoning_en.append(f"Soil moisture critically low at {moisture:.1f}%")
            reasoning_ar.append(f"رطوبة التربة منخفضة بشكل حرج عند {moisture:.1f}%")
        elif moisture < self.config.moisture_low_threshold:
            reasoning_en.append(f"Soil moisture below optimal at {moisture:.1f}%")
            reasoning_ar.append(f"رطوبة التربة دون المستوى الأمثل عند {moisture:.1f}%")

        # Weather considerations
        if features.weather.precipitation_probability > self.config.rain_probability_threshold:
            reasoning_en.append(
                f"Rain expected ({features.weather.precipitation_probability:.0f}% probability), "
                "consider delaying irrigation"
            )
            reasoning_ar.append(
                f"أمطار متوقعة (احتمال {features.weather.precipitation_probability:.0f}%)، يُنصح بتأخير الري"
            )

        if features.weather.temperature_max > self.config.high_temp_threshold:
            reasoning_en.append(f"High temperature ({features.weather.temperature_max:.1f}C) increases water demand")
            reasoning_ar.append(f"درجة حرارة مرتفعة ({features.weather.temperature_max:.1f}م) تزيد الطلب على المياه")

        # Crop stage consideration
        stage = features.crop.growth_stage
        stage_ar = {
            CropStage.GERMINATION: "الإنبات",
            CropStage.SEEDLING: "الشتلة",
            CropStage.VEGETATIVE: "النمو الخضري",
            CropStage.TILLERING: "التفريع",
            CropStage.FLOWERING: "الإزهار",
            CropStage.GRAIN_FILL: "امتلاء الحبوب",
            CropStage.MATURITY: "النضج",
            CropStage.HARVEST: "الحصاد",
        }
        reasoning_en.append(f"Crop is in {stage.value} stage with specific water needs")
        reasoning_ar.append(f"المحصول في مرحلة {stage_ar.get(stage, stage.value)} مع احتياجات مائية محددة")

        # Amount recommendation
        if prediction.irrigation_needed:
            area_ha = features.crop.area_ha
            if area_ha:
                volume_m3 = prediction.recommended_amount_mm * area_ha * 10
                prediction.recommended_amount_liters = volume_m3 * 1000
                reasoning_en.append(
                    f"Recommended: {prediction.recommended_amount_mm}mm ({volume_m3:.1f}m3 for {area_ha:.2f}ha)"
                )
                reasoning_ar.append(
                    f"التوصية: {prediction.recommended_amount_mm}مم ({volume_m3:.1f}م3 لـ {area_ha:.2f}هـ)"
                )
            else:
                reasoning_en.append(f"Recommended: {prediction.recommended_amount_mm}mm irrigation")
                reasoning_ar.append(f"التوصية: {prediction.recommended_amount_mm}مم من الري")

        # Optimal timing
        if prediction.optimal_time:
            time_str = prediction.optimal_time.strftime("%H:%M")
            reasoning_en.append(f"Best time: around {time_str} (low evaporation)")
            reasoning_ar.append(f"أفضل وقت: حوالي {time_str} (تبخر منخفض)")

        prediction.reasoning = " | ".join(reasoning_en)
        prediction.reasoning_ar = " | ".join(reasoning_ar)

        return prediction

    def _get_crop_coefficient(
        self,
        crop_type: str,
        growth_stage: CropStage,
    ) -> float:
        """Get crop coefficient (Kc) for crop type and stage"""
        crop_type_lower = crop_type.lower()
        stage_value = growth_stage.value

        # Get crop-specific coefficients or default
        crop_coeffs = CROP_COEFFICIENTS.get(
            crop_type_lower,
            CROP_COEFFICIENTS["default"],
        )

        return crop_coeffs.get(stage_value, 0.8)

    def _calculate_effective_rain(self, weather: WeatherFeatures) -> float:
        """Calculate effective rainfall (usable by crop)"""
        if weather.precipitation_probability < 30:
            return 0.0

        # Effective rainfall formula (USDA SCS method simplified)
        expected_rain = weather.precipitation_amount_mm * (weather.precipitation_probability / 100)

        if expected_rain <= 0:
            return 0.0

        # Effective rainfall is typically 70-80% of actual rainfall
        effective = expected_rain * 0.75

        # Reduce for high-intensity expected rainfall
        if expected_rain > 25:
            effective = expected_rain * 0.60

        return effective

    def _determine_urgency(
        self,
        soil: SoilFeatures,
        weather: WeatherFeatures,
        crop: CropFeatures,
        depletion: float,
    ) -> IrrigationUrgency:
        """Determine irrigation urgency level"""
        # Critical moisture level
        if soil.moisture_current < self.config.moisture_critical_threshold:
            return IrrigationUrgency.CRITICAL

        # High stress during sensitive stages
        sensitive_stages = {CropStage.FLOWERING, CropStage.GRAIN_FILL}
        if crop.growth_stage in sensitive_stages and depletion > 0.5:
            return IrrigationUrgency.HIGH

        # High temperature stress
        if weather.temperature_max > self.config.high_temp_threshold and depletion > 0.4:
            return IrrigationUrgency.HIGH

        # Low moisture
        if soil.moisture_current < self.config.moisture_low_threshold:
            return IrrigationUrgency.MEDIUM

        # Moderate depletion
        if depletion > 0.4:
            return IrrigationUrgency.LOW

        # No immediate need
        return IrrigationUrgency.NONE

    def _calculate_confidence(self, features: IrrigationFeatures) -> float:
        """Calculate prediction confidence based on data quality"""
        confidence = self.config.default_confidence

        # Increase confidence for recent sensor data
        data_age_hours = (datetime.now(UTC) - features.soil.timestamp).total_seconds() / 3600

        if data_age_hours < 1:
            confidence += 0.10
        elif data_age_hours < 6:
            confidence += 0.05
        elif data_age_hours > 24:
            confidence -= 0.10

        # Increase confidence if NDVI available
        if features.crop.ndvi is not None:
            confidence += 0.05

        # Decrease confidence for uncertain weather
        if features.weather.precipitation_probability > 40:
            confidence -= 0.05

        # Clamp to valid range
        return max(0.3, min(0.95, confidence))

    def _confidence_to_level(self, confidence: float) -> PredictionConfidence:
        """Convert confidence score to level"""
        if confidence >= 0.90:
            return PredictionConfidence.VERY_HIGH
        elif confidence >= 0.75:
            return PredictionConfidence.HIGH
        elif confidence >= 0.60:
            return PredictionConfidence.MEDIUM
        elif confidence >= 0.40:
            return PredictionConfidence.LOW
        else:
            return PredictionConfidence.VERY_LOW

    def _amount_to_urgency(self, amount_mm: float) -> IrrigationUrgency:
        """Convert irrigation amount to urgency level"""
        if amount_mm >= 50:
            return IrrigationUrgency.CRITICAL
        elif amount_mm >= 30:
            return IrrigationUrgency.HIGH
        elif amount_mm >= 15:
            return IrrigationUrgency.MEDIUM
        elif amount_mm >= 5:
            return IrrigationUrgency.LOW
        else:
            return IrrigationUrgency.NONE

    def _determine_optimal_timing(
        self,
        features: IrrigationFeatures,
    ) -> datetime:
        """Determine optimal irrigation timing"""
        now = datetime.now(UTC)

        # Prefer early morning (4-7 AM) for low evaporation
        target_hour = 5

        # Adjust for high wind (avoid sprinkler in wind)
        if (
            features.irrigation_type == IrrigationType.SPRINKLER
            and features.weather.wind_speed > self.config.high_wind_threshold
        ):
            # Move to evening when wind typically drops
            target_hour = 18

        # Set optimal time to next occurrence of target hour
        optimal = now.replace(hour=target_hour, minute=0, second=0, microsecond=0)
        if optimal <= now:
            optimal += timedelta(days=1)

        return optimal

    def _extract_factors(
        self,
        features: IrrigationFeatures,
        etc: float,
        depletion: float,
    ) -> list[dict[str, Any]]:
        """Extract contributing factors for explanation"""
        factors = []

        # Soil moisture factor
        moisture_impact = "high" if features.soil.moisture_current < 35 else "medium"
        factors.append(
            {
                "name": "Soil Moisture",
                "name_ar": "رطوبة التربة",
                "value": f"{features.soil.moisture_current:.1f}%",
                "impact": moisture_impact,
                "weight": 0.35,
            }
        )

        # ET factor
        factors.append(
            {
                "name": "Crop Water Demand (ETc)",
                "name_ar": "الطلب المائي للمحصول",
                "value": f"{etc:.1f} mm/day",
                "impact": "high" if etc > 5 else "medium",
                "weight": 0.25,
            }
        )

        # Depletion factor
        factors.append(
            {
                "name": "Soil Depletion",
                "name_ar": "استنزاف التربة",
                "value": f"{depletion * 100:.0f}%",
                "impact": "high" if depletion > 0.5 else "medium",
                "weight": 0.20,
            }
        )

        # Weather factor
        rain_factor = "low" if features.weather.precipitation_probability > 50 else "medium"
        factors.append(
            {
                "name": "Weather Conditions",
                "name_ar": "الظروف الجوية",
                "value": f"Rain: {features.weather.precipitation_probability:.0f}%",
                "impact": rain_factor,
                "weight": 0.20,
            }
        )

        return factors


def predict_irrigation(
    weather: WeatherFeatures,
    soil: SoilFeatures,
    crop: CropFeatures,
    irrigation_type: IrrigationType = IrrigationType.DRIP,
    system_efficiency: float = 0.85,
    config: PredictorConfig | None = None,
) -> IrrigationPrediction:
    """
    Convenience function for quick irrigation prediction
    دالة مساعدة للتنبؤ السريع بالري

    Args:
        weather: Weather features
        soil: Soil features
        crop: Crop features
        irrigation_type: Type of irrigation system
        system_efficiency: Irrigation system efficiency (0-1)
        config: Optional predictor configuration

    Returns:
        IrrigationPrediction with recommendations

    Example:
        prediction = predict_irrigation(
            weather=WeatherFeatures(...),
            soil=SoilFeatures(...),
            crop=CropFeatures(...),
        )
        print(f"Need: {prediction.irrigation_needed}")
        print(f"Amount: {prediction.recommended_amount_mm}mm")
    """
    features = IrrigationFeatures(
        weather=weather,
        soil=soil,
        crop=crop,
        irrigation_type=irrigation_type,
        system_efficiency=system_efficiency,
    )

    predictor = IrrigationPredictor(config=config)
    return predictor.predict(features)


# Singleton predictor instance
_default_predictor: IrrigationPredictor | None = None


def get_predictor(config: PredictorConfig | None = None) -> IrrigationPredictor:
    """Get or create the default predictor instance"""
    global _default_predictor
    if _default_predictor is None or config is not None:
        _default_predictor = IrrigationPredictor(config=config)
    return _default_predictor
