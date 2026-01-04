"""
📈 SAHOOL Yield Prediction Workflow
سير عمل توقع المحصول

This workflow provides yield prediction pipeline:
1. Collect historical vegetation indices
2. Analyze growth patterns
3. Apply yield prediction model
4. Generate predictions with confidence

Corresponds to Event Chain 4 in SAHOOL architecture:
crop-growth-model → yield-engine → marketplace-service
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Optional

import numpy as np

logger = logging.getLogger(__name__)


# =============================================================================
# Crop Growth Stages
# =============================================================================


class CropGrowthStage:
    """Crop growth stage definitions"""

    GERMINATION = "germination"
    VEGETATIVE = "vegetative"
    FLOWERING = "flowering"
    FRUIT_DEVELOPMENT = "fruit_development"
    MATURITY = "maturity"
    HARVEST = "harvest"


# Typical NDVI ranges for growth stages
GROWTH_STAGE_NDVI = {
    CropGrowthStage.GERMINATION: (0.1, 0.25),
    CropGrowthStage.VEGETATIVE: (0.25, 0.5),
    CropGrowthStage.FLOWERING: (0.5, 0.7),
    CropGrowthStage.FRUIT_DEVELOPMENT: (0.6, 0.8),
    CropGrowthStage.MATURITY: (0.4, 0.6),
    CropGrowthStage.HARVEST: (0.2, 0.4),
}


# =============================================================================
# Yield Prediction Workflow
# =============================================================================


class YieldPredictionWorkflow:
    """
    Yield prediction workflow using vegetation indices

    This workflow uses historical NDVI/EVI data to estimate
    crop yield based on empirical relationships and growth patterns.

    Yield estimation methods:
    1. NDVI Integration: Cumulative NDVI over growing season
    2. Peak NDVI: Maximum NDVI during critical growth period
    3. LAI-based: Using Leaf Area Index for biomass estimation

    Example:
        workflow = YieldPredictionWorkflow()
        result = workflow.execute(
            field_id="field_001",
            crop_type="wheat",
            historical_data=ndvi_timeseries,
            planting_date="2024-01-15"
        )
        print(f"Predicted yield: {result['predicted_yield_kg_ha']} kg/ha")
    """

    def __init__(
        self,
        method: str = "integrated",  # "integrated", "peak", "lai"
        crop_coefficients: Optional[dict[str, dict]] = None,
    ):
        """
        Initialize yield prediction workflow

        Args:
            method: Yield estimation method
            crop_coefficients: Crop-specific yield coefficients
        """
        self.method = method

        # Default crop yield coefficients (kg/ha per NDVI unit)
        self.crop_coefficients = crop_coefficients or {
            "wheat": {"a": 8500, "b": 0.65, "base_yield": 2000},
            "barley": {"a": 7000, "b": 0.60, "base_yield": 1800},
            "tomato": {"a": 45000, "b": 0.70, "base_yield": 15000},
            "coffee": {"a": 3500, "b": 0.55, "base_yield": 800},
            "banana": {"a": 35000, "b": 0.72, "base_yield": 12000},
            "maize": {"a": 12000, "b": 0.68, "base_yield": 3000},
            "sorghum": {"a": 5500, "b": 0.58, "base_yield": 1500},
            "millet": {"a": 4000, "b": 0.55, "base_yield": 1000},
            "qat": {"a": 8000, "b": 0.60, "base_yield": 2500},  # Yemen-specific
            "date_palm": {"a": 15000, "b": 0.50, "base_yield": 5000},
        }

    def execute(
        self,
        field_id: str,
        tenant_id: str,
        crop_type: str,
        historical_data: list[dict[str, Any]],
        planting_date: str,
        area_hectares: float = 1.0,
        current_growth_day: Optional[int] = None,
    ) -> dict[str, Any]:
        """
        Execute yield prediction workflow

        Args:
            field_id: Field identifier
            tenant_id: Tenant identifier
            crop_type: Type of crop
            historical_data: List of {date, ndvi, evi, lai} observations
            planting_date: Planting date (YYYY-MM-DD)
            area_hectares: Field area in hectares
            current_growth_day: Days since planting (None = calculate)

        Returns:
            Yield prediction results
        """
        logger.info(f"Starting yield prediction for {field_id}")

        result = {
            "field_id": field_id,
            "tenant_id": tenant_id,
            "crop_type": crop_type,
            "area_hectares": area_hectares,
            "execution_timestamp": datetime.utcnow().isoformat(),
            "method": self.method,
        }

        try:
            # Extract NDVI time series
            ndvi_series = self._extract_ndvi_series(historical_data)

            if len(ndvi_series) < 3:
                result["status"] = "insufficient_data"
                result["error"] = "Need at least 3 observations for prediction"
                return result

            # Determine growth stage
            current_ndvi = ndvi_series[-1]["value"]
            growth_stage = self._determine_growth_stage(current_ndvi)
            result["current_growth_stage"] = growth_stage

            # Calculate growth day if not provided
            if current_growth_day is None:
                planting = datetime.strptime(planting_date, "%Y-%m-%d")
                current_growth_day = (datetime.now() - planting).days
            result["growth_day"] = current_growth_day

            # Get crop coefficients
            coeffs = self.crop_coefficients.get(
                crop_type.lower(),
                self.crop_coefficients.get("wheat"),  # Default to wheat
            )

            # Calculate yield based on method
            if self.method == "integrated":
                predicted_yield = self._integrated_ndvi_yield(ndvi_series, coeffs)
            elif self.method == "peak":
                predicted_yield = self._peak_ndvi_yield(ndvi_series, coeffs)
            elif self.method == "lai":
                lai_series = self._extract_lai_series(historical_data)
                predicted_yield = self._lai_based_yield(lai_series, coeffs)
            else:
                predicted_yield = self._integrated_ndvi_yield(ndvi_series, coeffs)

            # Apply area
            total_yield = predicted_yield * area_hectares

            # Calculate confidence
            confidence = self._calculate_confidence(ndvi_series, growth_stage)

            # Generate prediction ranges
            yield_min = predicted_yield * (1 - 0.15)  # -15%
            yield_max = predicted_yield * (1 + 0.15)  # +15%

            result.update(
                {
                    "status": "success",
                    "predicted_yield_kg_ha": round(predicted_yield, 0),
                    "total_yield_kg": round(total_yield, 0),
                    "yield_range": {
                        "min_kg_ha": round(yield_min, 0),
                        "max_kg_ha": round(yield_max, 0),
                    },
                    "confidence_score": round(confidence, 2),
                    "growth_metrics": {
                        "current_ndvi": round(current_ndvi, 3),
                        "peak_ndvi": round(max(d["value"] for d in ndvi_series), 3),
                        "integrated_ndvi": round(
                            sum(d["value"] for d in ndvi_series), 3
                        ),
                        "observations_count": len(ndvi_series),
                    },
                }
            )

            # Generate YieldPredicted event
            result["event"] = self._create_yield_event(result)

            logger.info(f"Yield prediction completed: {predicted_yield} kg/ha")
            return result

        except Exception as e:
            logger.error(f"Yield prediction failed: {e}")
            result["status"] = "error"
            result["error"] = str(e)
            return result

    def _extract_ndvi_series(self, historical_data: list[dict]) -> list[dict]:
        """Extract NDVI time series from historical data"""
        series = []
        for obs in historical_data:
            if "ndvi" in obs and obs["ndvi"] is not None:
                series.append(
                    {
                        "date": obs.get("date", ""),
                        "value": float(obs["ndvi"]),
                    }
                )
        return sorted(series, key=lambda x: x["date"])

    def _extract_lai_series(self, historical_data: list[dict]) -> list[dict]:
        """Extract LAI time series from historical data"""
        series = []
        for obs in historical_data:
            if "lai" in obs and obs["lai"] is not None:
                series.append(
                    {
                        "date": obs.get("date", ""),
                        "value": float(obs["lai"]),
                    }
                )
        return sorted(series, key=lambda x: x["date"])

    def _determine_growth_stage(self, current_ndvi: float) -> str:
        """Determine crop growth stage from NDVI"""
        for stage, (min_ndvi, max_ndvi) in GROWTH_STAGE_NDVI.items():
            if min_ndvi <= current_ndvi <= max_ndvi:
                return stage

        if current_ndvi > 0.7:
            return CropGrowthStage.FRUIT_DEVELOPMENT
        elif current_ndvi < 0.1:
            return CropGrowthStage.GERMINATION
        else:
            return CropGrowthStage.VEGETATIVE

    def _integrated_ndvi_yield(self, ndvi_series: list[dict], coeffs: dict) -> float:
        """
        Calculate yield from integrated NDVI

        Uses cumulative NDVI as proxy for total biomass production.
        """
        # Calculate integrated NDVI (sum of all observations)
        integrated = sum(d["value"] for d in ndvi_series)

        # Normalize by observation count
        mean_ndvi = integrated / len(ndvi_series)

        # Apply yield model: Y = a * NDVI^b + base
        yield_estimate = coeffs["a"] * (mean_ndvi ** coeffs["b"]) + coeffs["base_yield"]

        return max(0, yield_estimate)

    def _peak_ndvi_yield(self, ndvi_series: list[dict], coeffs: dict) -> float:
        """
        Calculate yield from peak NDVI

        Peak NDVI correlates with maximum vegetation development.
        """
        peak_ndvi = max(d["value"] for d in ndvi_series)

        # Apply yield model with peak NDVI
        yield_estimate = coeffs["a"] * (peak_ndvi ** coeffs["b"]) + coeffs["base_yield"]

        return max(0, yield_estimate)

    def _lai_based_yield(self, lai_series: list[dict], coeffs: dict) -> float:
        """
        Calculate yield from LAI

        LAI provides direct estimate of photosynthetic capacity.
        """
        if not lai_series:
            return coeffs["base_yield"]

        max_lai = max(d["value"] for d in lai_series)

        # LAI-based yield model (different coefficients)
        # Higher LAI generally means more biomass
        yield_estimate = (max_lai / 5.0) * coeffs["a"] + coeffs["base_yield"]

        return max(0, yield_estimate)

    def _calculate_confidence(
        self, ndvi_series: list[dict], growth_stage: str
    ) -> float:
        """Calculate prediction confidence score"""
        confidence = 0.5  # Base confidence

        # More observations = higher confidence
        obs_count = len(ndvi_series)
        if obs_count >= 10:
            confidence += 0.2
        elif obs_count >= 5:
            confidence += 0.1

        # Later growth stage = higher confidence
        stage_confidence = {
            CropGrowthStage.GERMINATION: -0.1,
            CropGrowthStage.VEGETATIVE: 0.0,
            CropGrowthStage.FLOWERING: 0.1,
            CropGrowthStage.FRUIT_DEVELOPMENT: 0.15,
            CropGrowthStage.MATURITY: 0.2,
            CropGrowthStage.HARVEST: 0.15,
        }
        confidence += stage_confidence.get(growth_stage, 0)

        # Consistent NDVI pattern = higher confidence
        values = [d["value"] for d in ndvi_series]
        std_dev = np.std(values) if len(values) > 1 else 0.5
        if std_dev < 0.1:
            confidence += 0.1
        elif std_dev > 0.3:
            confidence -= 0.1

        return min(0.95, max(0.3, confidence))

    def _create_yield_event(self, result: dict) -> dict[str, Any]:
        """Create YieldPredicted.v1 event"""
        import uuid

        return {
            "event_id": str(uuid.uuid4()),
            "event_type": "YieldPredicted",
            "event_version": 1,
            "tenant_id": result["tenant_id"],
            "timestamp": datetime.utcnow().isoformat(),
            "source": "yield-prediction-workflow",
            "payload": {
                "field_id": result["field_id"],
                "crop_type": result["crop_type"],
                "prediction_date": datetime.utcnow().date().isoformat(),
                "predicted_yield_kg_ha": result.get("predicted_yield_kg_ha", 0),
                "confidence_score": result.get("confidence_score", 0),
                "prediction_method": result["method"],
                "growth_stage": result.get("current_growth_stage", "unknown"),
            },
        }


# =============================================================================
# Growth Stage Estimation
# =============================================================================


class GrowthStageEstimator:
    """
    Estimate crop growth stage from vegetation indices

    Uses NDVI trajectory analysis to determine current growth stage
    and estimate days to next stage.
    """

    def __init__(self, crop_type: str = "wheat"):
        """
        Initialize growth stage estimator

        Args:
            crop_type: Type of crop for stage duration calibration
        """
        self.crop_type = crop_type

        # Typical stage durations (days) - Yemen climate
        self.stage_durations = {
            "wheat": {
                CropGrowthStage.GERMINATION: 15,
                CropGrowthStage.VEGETATIVE: 30,
                CropGrowthStage.FLOWERING: 20,
                CropGrowthStage.FRUIT_DEVELOPMENT: 25,
                CropGrowthStage.MATURITY: 20,
            },
            "tomato": {
                CropGrowthStage.GERMINATION: 10,
                CropGrowthStage.VEGETATIVE: 25,
                CropGrowthStage.FLOWERING: 15,
                CropGrowthStage.FRUIT_DEVELOPMENT: 40,
                CropGrowthStage.MATURITY: 15,
            },
        }

    def estimate(self, ndvi_series: list[dict], planting_date: str) -> dict[str, Any]:
        """
        Estimate current growth stage and progression

        Args:
            ndvi_series: NDVI time series
            planting_date: Planting date (YYYY-MM-DD)

        Returns:
            Growth stage estimation results
        """
        if not ndvi_series:
            return {"status": "no_data"}

        current_ndvi = ndvi_series[-1]["value"]
        planting = datetime.strptime(planting_date, "%Y-%m-%d")
        days_since_planting = (datetime.now() - planting).days

        # Determine stage from NDVI
        current_stage = self._ndvi_to_stage(current_ndvi)

        # Calculate NDVI trend
        if len(ndvi_series) >= 2:
            trend = ndvi_series[-1]["value"] - ndvi_series[-2]["value"]
        else:
            trend = 0

        # Estimate days to next stage
        durations = self.stage_durations.get(
            self.crop_type, self.stage_durations["wheat"]
        )
        stage_duration = durations.get(current_stage, 20)

        return {
            "current_stage": current_stage,
            "days_since_planting": days_since_planting,
            "current_ndvi": round(current_ndvi, 3),
            "ndvi_trend": (
                "increasing"
                if trend > 0.02
                else "decreasing" if trend < -0.02 else "stable"
            ),
            "estimated_stage_duration": stage_duration,
            "estimated_harvest_date": self._estimate_harvest_date(
                planting_date, current_stage, durations
            ),
        }

    def _ndvi_to_stage(self, ndvi: float) -> str:
        """Convert NDVI to growth stage"""
        for stage, (min_v, max_v) in GROWTH_STAGE_NDVI.items():
            if min_v <= ndvi <= max_v:
                return stage
        return CropGrowthStage.VEGETATIVE

    def _estimate_harvest_date(
        self, planting_date: str, current_stage: str, durations: dict
    ) -> str:
        """Estimate harvest date based on remaining stages"""
        planting = datetime.strptime(planting_date, "%Y-%m-%d")

        # Sum remaining stage durations
        stages = list(GROWTH_STAGE_NDVI.keys())
        current_idx = stages.index(current_stage) if current_stage in stages else 0

        remaining_days = sum(durations.get(stage, 20) for stage in stages[current_idx:])

        harvest_date = planting + timedelta(days=remaining_days)
        return harvest_date.date().isoformat()
