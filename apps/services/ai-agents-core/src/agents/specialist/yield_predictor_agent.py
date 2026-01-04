"""
SAHOOL Yield Predictor Agent
وكيل توقع الإنتاج

Specialized agent for:
- Crop yield prediction
- Production optimization
- Harvest timing
- Economic analysis

Uses ensemble of prediction models (NDVI, GDD, Water Balance, Soil).
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from ..base_agent import (
    AgentAction,
    AgentContext,
    AgentLayer,
    AgentPercept,
    AgentType,
    BaseAgent,
)

logger = logging.getLogger(__name__)


@dataclass
class YieldPrediction:
    """توقع الإنتاج"""

    crop_type: str
    predicted_yield_tons: float
    yield_per_hectare: float
    confidence: float
    yield_range: tuple  # (min, max)
    harvest_date: datetime
    days_to_harvest: int
    growth_stage: str
    limiting_factors: list[str]
    recommendations: list[str]


class YieldPredictorAgent(BaseAgent):
    """
    وكيل توقع الإنتاج
    Yield Predictor Agent using ensemble models
    """

    # Yemen crop base yields (tons/hectare)
    BASE_YIELDS = {
        "wheat": 2.5,
        "barley": 2.2,
        "corn": 4.0,
        "sorghum": 2.0,
        "millet": 1.5,
        "rice": 3.5,
        "tomato": 25.0,
        "potato": 15.0,
        "onion": 12.0,
        "cucumber": 28.0,
        "pepper": 15.0,
        "eggplant": 20.0,
        "date_palm": 5.0,
        "mango": 6.0,
        "banana": 20.0,
        "grape": 8.0,
        "coffee": 0.8,
        "alfalfa": 18.0,
    }

    # Crop growth parameters
    CROP_PARAMS = {
        "wheat": {
            "gdd_required": 2000,
            "optimal_ndvi_peak": 0.75,
            "water_requirement_mm": 450,
            "growth_days": 120,
        },
        "tomato": {
            "gdd_required": 1500,
            "optimal_ndvi_peak": 0.70,
            "water_requirement_mm": 600,
            "growth_days": 90,
        },
        "corn": {
            "gdd_required": 2500,
            "optimal_ndvi_peak": 0.80,
            "water_requirement_mm": 550,
            "growth_days": 100,
        },
        "date_palm": {
            "gdd_required": 3500,
            "optimal_ndvi_peak": 0.60,
            "water_requirement_mm": 1500,
            "growth_days": 180,
        },
        "coffee": {
            "gdd_required": 2000,
            "optimal_ndvi_peak": 0.65,
            "water_requirement_mm": 1200,
            "growth_days": 270,
        },
    }

    # Model weights for ensemble
    MODEL_WEIGHTS = {
        "ndvi_model": 0.40,
        "gdd_model": 0.30,
        "water_model": 0.20,
        "soil_model": 0.10,
    }

    def __init__(self, agent_id: str = "yield_predictor_001"):
        super().__init__(
            agent_id=agent_id,
            name="Yield Predictor Agent",
            name_ar="وكيل توقع الإنتاج",
            agent_type=AgentType.UTILITY_BASED,
            layer=AgentLayer.SPECIALIST,
            description="Expert agent for crop yield prediction and optimization",
            description_ar="وكيل خبير لتوقع إنتاج المحاصيل وتحسينها",
        )

        # Prediction history for learning
        self.prediction_history: list[dict[str, Any]] = []

        # Set utility function
        self.set_utility_function(self._recommendation_utility)

    def _recommendation_utility(
        self, action: AgentAction, context: AgentContext
    ) -> float:
        """دالة المنفعة لتقييم التوصيات"""
        if action.action_type not in ["yield_optimization", "harvest_timing"]:
            return 0.0

        # Higher utility for higher confidence and yield improvement
        confidence = action.confidence
        yield_impact = action.parameters.get("yield_impact", 0)

        return confidence * 0.6 + (yield_impact / 100) * 0.4

    async def perceive(self, percept: AgentPercept) -> None:
        """استقبال البيانات للتوقع"""
        if percept.percept_type == "ndvi_data":
            self.state.beliefs["ndvi_history"] = percept.data

        elif percept.percept_type == "weather_data":
            self.state.beliefs["weather"] = percept.data

        elif percept.percept_type == "soil_data":
            self.state.beliefs["soil"] = percept.data

        elif percept.percept_type == "irrigation_data":
            self.state.beliefs["irrigation"] = percept.data

        elif percept.percept_type == "crop_info":
            self.state.beliefs["crop"] = percept.data

        # Update context
        if not self.context:
            self.context = AgentContext()
        self.context.metadata["yield_beliefs"] = self.state.beliefs

    async def think(self) -> AgentAction | None:
        """حساب التوقع واتخاذ القرار"""
        crop_info = self.state.beliefs.get("crop", {})
        crop_type = crop_info.get("type", "wheat")

        # Run ensemble prediction
        prediction = await self._predict_yield(crop_type)

        if not prediction:
            return AgentAction(
                action_type="insufficient_data",
                parameters={"reason": "البيانات غير كافية للتوقع"},
                confidence=0.5,
                priority=3,
                reasoning="لا توجد بيانات كافية لإجراء توقع دقيق",
                source_agent=self.agent_id,
            )

        # Generate recommendations
        recommendations = await self._generate_recommendations(prediction)

        # Select best action
        if recommendations:
            best_action = self.select_best_action(recommendations, self.context)
            best_action.parameters["prediction"] = {
                "yield_tons": prediction.predicted_yield_tons,
                "yield_per_ha": prediction.yield_per_hectare,
                "confidence": prediction.confidence,
                "harvest_date": prediction.harvest_date.isoformat(),
                "days_to_harvest": prediction.days_to_harvest,
                "growth_stage": prediction.growth_stage,
            }
            return best_action

        # Default: return prediction only
        return AgentAction(
            action_type="yield_prediction",
            parameters={"prediction": prediction.__dict__, "crop_type": crop_type},
            confidence=prediction.confidence,
            priority=2,
            reasoning=f"توقع إنتاج {crop_type}: {prediction.yield_per_hectare:.1f} طن/هكتار",
            source_agent=self.agent_id,
        )

    async def _predict_yield(self, crop_type: str) -> YieldPrediction | None:
        """التوقع باستخدام نماذج متعددة"""
        if crop_type not in self.BASE_YIELDS:
            return None

        base_yield = self.BASE_YIELDS[crop_type]
        params = self.CROP_PARAMS.get(crop_type, self.CROP_PARAMS["wheat"])

        # Model 1: NDVI-based
        ndvi_yield = await self._ndvi_model(base_yield, params)

        # Model 2: GDD-based
        gdd_yield = await self._gdd_model(base_yield, params)

        # Model 3: Water balance
        water_yield = await self._water_model(base_yield, params)

        # Model 4: Soil quality
        soil_yield = await self._soil_model(base_yield)

        # Ensemble prediction
        ensemble_yield = (
            self.MODEL_WEIGHTS["ndvi_model"] * ndvi_yield["yield"]
            + self.MODEL_WEIGHTS["gdd_model"] * gdd_yield["yield"]
            + self.MODEL_WEIGHTS["water_model"] * water_yield["yield"]
            + self.MODEL_WEIGHTS["soil_model"] * soil_yield["yield"]
        )

        # Calculate confidence
        confidences = [
            ndvi_yield["confidence"],
            gdd_yield["confidence"],
            water_yield["confidence"],
            soil_yield["confidence"],
        ]
        avg_confidence = sum(confidences) / len(confidences)

        # Variance penalty
        variance = sum((c - avg_confidence) ** 2 for c in confidences) / len(
            confidences
        )
        final_confidence = avg_confidence * (1 - variance)

        # Identify limiting factors
        limiting_factors = []
        if ndvi_yield["yield"] < base_yield * 0.7:
            limiting_factors.append("صحة النبات منخفضة")
        if water_yield["yield"] < base_yield * 0.7:
            limiting_factors.append("إجهاد مائي")
        if gdd_yield["yield"] < base_yield * 0.7:
            limiting_factors.append("ظروف حرارية غير مثالية")
        if soil_yield["yield"] < base_yield * 0.7:
            limiting_factors.append("جودة التربة منخفضة")

        # Estimate harvest date
        growth_progress = self.state.beliefs.get("crop", {}).get("growth_progress", 0.5)
        days_remaining = int(params["growth_days"] * (1 - growth_progress))
        harvest_date = datetime.now() + timedelta(days=days_remaining)

        # Growth stage
        if growth_progress < 0.2:
            growth_stage = "إنبات"
        elif growth_progress < 0.4:
            growth_stage = "نمو خضري"
        elif growth_progress < 0.6:
            growth_stage = "إزهار"
        elif growth_progress < 0.8:
            growth_stage = "إثمار"
        else:
            growth_stage = "نضج"

        field_area = self.state.beliefs.get("crop", {}).get("area_hectares", 1)

        return YieldPrediction(
            crop_type=crop_type,
            predicted_yield_tons=ensemble_yield * field_area,
            yield_per_hectare=ensemble_yield,
            confidence=final_confidence,
            yield_range=(ensemble_yield * 0.85, ensemble_yield * 1.15),
            harvest_date=harvest_date,
            days_to_harvest=days_remaining,
            growth_stage=growth_stage,
            limiting_factors=limiting_factors,
            recommendations=[],
        )

    async def _ndvi_model(self, base_yield: float, params: dict) -> dict[str, float]:
        """نموذج NDVI"""
        ndvi_data = self.state.beliefs.get("ndvi_history", {})
        peak_ndvi = ndvi_data.get("peak", 0.5)
        optimal_peak = params["optimal_ndvi_peak"]

        ratio = min(peak_ndvi / optimal_peak, 1.0)
        yield_estimate = base_yield * ratio

        confidence = 0.7 if ndvi_data else 0.3

        return {"yield": yield_estimate, "confidence": confidence}

    async def _gdd_model(self, base_yield: float, params: dict) -> dict[str, float]:
        """نموذج درجات الحرارة التراكمية"""
        weather = self.state.beliefs.get("weather", {})
        accumulated_gdd = weather.get("accumulated_gdd", params["gdd_required"] * 0.5)
        required_gdd = params["gdd_required"]

        ratio = min(accumulated_gdd / required_gdd, 1.0)

        # Quadratic response
        yield_estimate = base_yield * (2 * ratio - ratio**2)

        confidence = 0.6 if weather else 0.3

        return {"yield": yield_estimate, "confidence": confidence}

    async def _water_model(self, base_yield: float, params: dict) -> dict[str, float]:
        """نموذج توازن المياه"""
        irrigation = self.state.beliefs.get("irrigation", {})
        weather = self.state.beliefs.get("weather", {})

        water_applied = irrigation.get("total_mm", 0)
        rainfall = weather.get("total_rainfall_mm", 0)
        total_water = water_applied + rainfall

        requirement = params["water_requirement_mm"]

        if total_water < requirement * 0.6:
            stress_factor = total_water / (requirement * 0.6)
        else:
            stress_factor = 1.0

        yield_estimate = base_yield * stress_factor

        confidence = 0.65 if irrigation or weather else 0.3

        return {"yield": yield_estimate, "confidence": confidence}

    async def _soil_model(self, base_yield: float) -> dict[str, float]:
        """نموذج جودة التربة"""
        soil = self.state.beliefs.get("soil", {})

        # Default factors
        ph_factor = 1.0
        ec_factor = 1.0
        nutrient_factor = 1.0

        if soil:
            ph = soil.get("ph", 7.0)
            ph_factor = 1.0 if 6.0 <= ph <= 7.5 else 0.8

            ec = soil.get("ec", 1.5)
            if ec < 2.5:
                ec_factor = 1.0
            elif ec < 4.0:
                ec_factor = 0.8
            else:
                ec_factor = 0.5

            nutrients = soil.get("nutrient_score", 0.8)
            nutrient_factor = nutrients

        overall_factor = (ph_factor + ec_factor + nutrient_factor) / 3
        yield_estimate = base_yield * overall_factor

        confidence = 0.6 if soil else 0.4

        return {"yield": yield_estimate, "confidence": confidence}

    async def _generate_recommendations(
        self, prediction: YieldPrediction
    ) -> list[AgentAction]:
        """توليد التوصيات"""
        actions = []

        # Yield optimization recommendations
        for factor in prediction.limiting_factors:
            if "مائي" in factor:
                actions.append(
                    AgentAction(
                        action_type="yield_optimization",
                        parameters={
                            "factor": "irrigation",
                            "recommendation_ar": "زيادة معدل الري",
                            "yield_impact": 15,
                        },
                        confidence=0.8,
                        priority=2,
                        reasoning="تحسين الإنتاج عبر زيادة الري",
                    )
                )
            elif "تربة" in factor:
                actions.append(
                    AgentAction(
                        action_type="yield_optimization",
                        parameters={
                            "factor": "fertilization",
                            "recommendation_ar": "إضافة سماد عضوي",
                            "yield_impact": 10,
                        },
                        confidence=0.75,
                        priority=3,
                        reasoning="تحسين جودة التربة",
                    )
                )

        # Harvest timing
        if prediction.days_to_harvest <= 14:
            actions.append(
                AgentAction(
                    action_type="harvest_timing",
                    parameters={
                        "days_to_harvest": prediction.days_to_harvest,
                        "optimal_date": prediction.harvest_date.isoformat(),
                        "recommendation_ar": "استعد للحصاد",
                    },
                    confidence=0.85,
                    priority=1,
                    reasoning=f"موعد الحصاد خلال {prediction.days_to_harvest} يوم",
                )
            )

        return actions

    async def act(self, action: AgentAction) -> dict[str, Any]:
        """تنفيذ التوصية"""
        result = {
            "action_type": action.action_type,
            "executed_at": datetime.now().isoformat(),
            "success": True,
        }

        if action.action_type == "yield_prediction":
            result["prediction"] = action.parameters.get("prediction")

        elif action.action_type == "yield_optimization":
            result["recommendation"] = {
                "factor": action.parameters.get("factor"),
                "action_ar": action.parameters.get("recommendation_ar"),
                "expected_yield_increase": f"{action.parameters.get('yield_impact', 0)}%",
            }

        elif action.action_type == "harvest_timing":
            result["harvest_plan"] = {
                "days_remaining": action.parameters.get("days_to_harvest"),
                "optimal_date": action.parameters.get("optimal_date"),
                "recommendation_ar": action.parameters.get("recommendation_ar"),
            }

        # Store for learning
        self.prediction_history.append(
            {
                "action": action.action_type,
                "prediction": action.parameters.get("prediction"),
                "timestamp": datetime.now().isoformat(),
            }
        )

        return result
