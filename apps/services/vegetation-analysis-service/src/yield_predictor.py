"""
SAHOOL Crop Yield Prediction Model
نموذج التنبؤ بإنتاجية المحاصيل

ML-based yield prediction using:
- Satellite vegetation indices (NDVI, EVI, LAI)
- Growing Degree Days (GDD)
- Water balance model
- Soil moisture from SAR
- Historical yield data

Based on FAO methodology and Yemen-specific calibration.
"""

import math

# Import shared crop catalog
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


# Define CropInfo first as fallback
@dataclass
class CropInfo:
    code: str = ""
    name_en: str = ""
    name_ar: str = ""
    base_yield_ton_ha: float = 0.0


SHARED_PATH = Path(__file__).parent.parent.parent / "shared"
if str(SHARED_PATH) not in sys.path:
    sys.path.insert(0, str(SHARED_PATH))
try:
    from crops import ALL_CROPS, CropInfo, get_crop
except ImportError:
    # Fallback for standalone testing
    ALL_CROPS = {}

    def get_crop(code: str):
        return None


@dataclass
class YieldPrediction:
    """Yield prediction result with confidence and recommendations"""

    field_id: str
    crop_code: str
    crop_name_ar: str
    crop_name_en: str
    predicted_yield_ton_ha: float
    yield_range_min: float
    yield_range_max: float
    confidence: float  # 0-1
    factors: dict[str, float]  # contribution of each factor (0-1)
    comparison_to_average: float  # % above/below regional average
    comparison_to_base: float  # % above/below crop base yield
    recommendations_ar: list[str]
    recommendations_en: list[str]
    prediction_date: datetime
    growth_stage: str  # current growth stage
    days_to_harvest: int | None


class YieldPredictor:
    """
    ML-based crop yield prediction using satellite indices and weather data.

    Model ensemble:
    1. NDVI-based regression (40% weight)
    2. Growing Degree Days model (30% weight)
    3. Water balance model (20% weight)
    4. Soil moisture model (10% weight)

    Yemen-specific calibration factors from FAO and local research.
    """

    # Regional average yields for Yemen (ton/ha) - from FAO statistics
    YEMEN_AVERAGE_YIELDS = {
        "WHEAT": 1.8,
        "SORGHUM": 1.2,
        "MILLET": 0.8,
        "CORN": 2.5,
        "BARLEY": 1.5,
        "COFFEE": 0.6,
        "DATE_PALM": 5.0,
        "TOMATO": 25.0,
        "POTATO": 15.0,
        "ONION": 12.0,
        "GRAPE": 8.0,
        "MANGO": 6.0,
        "BANANA": 20.0,
        "ALFALFA": 18.0,
        "SESAME": 0.5,
        "QAT": 3.0,
        "FABA_BEAN": 1.8,
        "CUCUMBER": 28.0,
        "EGGPLANT": 22.0,
        "WATERMELON": 25.0,
    }

    # NDVI-to-Yield sensitivity coefficients (crop-specific)
    # Based on research: Yield = base_yield * (1 + k * (NDVI_integral - NDVI_baseline))
    NDVI_YIELD_COEFFICIENTS = {
        "WHEAT": {"k": 2.5, "baseline_integral": 45.0, "peak_min": 0.65},
        "BARLEY": {"k": 2.3, "baseline_integral": 40.0, "peak_min": 0.60},
        "CORN": {"k": 3.0, "baseline_integral": 50.0, "peak_min": 0.70},
        "SORGHUM": {"k": 2.2, "baseline_integral": 42.0, "peak_min": 0.60},
        "MILLET": {"k": 2.0, "baseline_integral": 38.0, "peak_min": 0.55},
        "RICE": {"k": 2.8, "baseline_integral": 55.0, "peak_min": 0.75},
        "TOMATO": {"k": 3.5, "baseline_integral": 52.0, "peak_min": 0.75},
        "POTATO": {"k": 3.2, "baseline_integral": 48.0, "peak_min": 0.70},
        "ONION": {"k": 2.8, "baseline_integral": 50.0, "peak_min": 0.65},
        "COFFEE": {"k": 1.8, "baseline_integral": 60.0, "peak_min": 0.70},
        "DATE_PALM": {"k": 2.0, "baseline_integral": 65.0, "peak_min": 0.60},
        "BANANA": {"k": 3.0, "baseline_integral": 70.0, "peak_min": 0.80},
        "GRAPE": {"k": 2.5, "baseline_integral": 55.0, "peak_min": 0.65},
        "MANGO": {"k": 2.3, "baseline_integral": 58.0, "peak_min": 0.70},
        "QAT": {"k": 2.0, "baseline_integral": 75.0, "peak_min": 0.75},
        # Default for other crops
        "DEFAULT": {"k": 2.5, "baseline_integral": 45.0, "peak_min": 0.65},
    }

    # GDD requirements for optimal yield (base temp 10°C)
    GDD_REQUIREMENTS = {
        "WHEAT": {"optimal": 2000, "min": 1500, "max": 2500},
        "BARLEY": {"optimal": 1600, "min": 1200, "max": 2000},
        "CORN": {"optimal": 2700, "min": 2200, "max": 3200},
        "SORGHUM": {"optimal": 2400, "min": 2000, "max": 2800},
        "MILLET": {"optimal": 1800, "min": 1500, "max": 2200},
        "RICE": {"optimal": 3000, "min": 2500, "max": 3500},
        "TOMATO": {"optimal": 2200, "min": 1800, "max": 2600},
        "POTATO": {"optimal": 1800, "min": 1400, "max": 2200},
        "COFFEE": {"optimal": 1500, "min": 1200, "max": 1800},
        # Default
        "DEFAULT": {"optimal": 2000, "min": 1500, "max": 2500},
    }

    # Water stress impact coefficients (Ky - FAO)
    # Yield reduction factor per unit of water stress
    WATER_STRESS_KY = {
        "WHEAT": 1.05,
        "BARLEY": 1.0,
        "CORN": 1.25,
        "SORGHUM": 0.9,
        "MILLET": 0.8,
        "RICE": 1.2,
        "TOMATO": 1.05,
        "POTATO": 1.1,
        "ONION": 1.1,
        "COFFEE": 1.0,
        "DATE_PALM": 0.9,
        "BANANA": 1.2,
        "DEFAULT": 1.0,
    }

    async def predict_yield(
        self,
        field_id: str,
        crop_code: str,
        ndvi_series: list[float],
        weather_data: dict,
        soil_moisture: float | None = None,
        planting_date: datetime | None = None,
        field_area_ha: float = 1.0,
    ) -> YieldPrediction:
        """
        Predict crop yield using ensemble of models.

        Args:
            field_id: Field identifier
            crop_code: Crop code from SAHOOL catalog (e.g., "WHEAT", "TOMATO")
            ndvi_series: Time series of NDVI values (bi-weekly or monthly)
            weather_data: {
                "temp_min_series": [float],  # Daily min temps (°C)
                "temp_max_series": [float],  # Daily max temps (°C)
                "precipitation_mm": float,    # Total precipitation
                "et0_mm": Optional[float],    # Reference evapotranspiration
            }
            soil_moisture: Current soil moisture (0-1)
            planting_date: Date of planting
            field_area_ha: Field area in hectares

        Returns:
            YieldPrediction with predicted yield and recommendations
        """
        # Get crop info from catalog
        crop_info = get_crop(crop_code)
        if not crop_info:
            # Fallback to default
            crop_name_en = crop_code.replace("_", " ").title()
            crop_name_ar = crop_code
            base_yield = 2.0
            kc_mid = 1.0
        else:
            crop_name_en = crop_info.name_en
            crop_name_ar = crop_info.name_ar
            base_yield = crop_info.base_yield_ton_ha
            kc_mid = crop_info.kc_mid or 1.0

        # Calculate NDVI features
        ndvi_peak = max(ndvi_series) if ndvi_series else 0.5
        sum(ndvi_series) / len(ndvi_series) if ndvi_series else 0.5
        ndvi_integral = self.calculate_ndvi_integral(ndvi_series)

        # Calculate GDD
        gdd = self.calculate_gdd(
            weather_data.get("temp_min_series", []),
            weather_data.get("temp_max_series", []),
        )

        # Calculate water stress
        precipitation = weather_data.get("precipitation_mm", 0)
        et0 = weather_data.get("et0_mm", precipitation * 1.2)  # Estimate if not provided
        water_stress_factor = self.calculate_water_stress(
            precipitation=precipitation,
            et0=et0,
            kc=kc_mid,
            soil_moisture=soil_moisture,
        )

        # Determine growth stage
        growth_stage, days_to_harvest = self.estimate_growth_stage(
            planting_date=planting_date,
            gdd_accumulated=gdd,
            crop_code=crop_code,
            crop_info=crop_info,
        )

        # Model 1: NDVI-based yield prediction (40% weight)
        ndvi_yield = self.predict_from_ndvi(
            crop_code=crop_code,
            base_yield=base_yield,
            ndvi_peak=ndvi_peak,
            ndvi_integral=ndvi_integral,
        )

        # Model 2: GDD-based yield prediction (30% weight)
        gdd_yield = self.predict_from_gdd(
            crop_code=crop_code,
            base_yield=base_yield,
            gdd_accumulated=gdd,
        )

        # Model 3: Water balance yield prediction (20% weight)
        water_yield = base_yield * water_stress_factor

        # Model 4: Soil moisture yield prediction (10% weight)
        soil_yield = self.predict_from_soil_moisture(
            base_yield=base_yield,
            soil_moisture=soil_moisture,
        )

        # Ensemble prediction (weighted average)
        predicted_yield = (
            0.40 * ndvi_yield + 0.30 * gdd_yield + 0.20 * water_yield + 0.10 * soil_yield
        )

        # Calculate confidence based on data quality and consistency
        confidence = self.calculate_confidence(
            ndvi_series=ndvi_series,
            ndvi_peak=ndvi_peak,
            gdd=gdd,
            water_stress_factor=water_stress_factor,
            model_variance=[ndvi_yield, gdd_yield, water_yield, soil_yield],
        )

        # Calculate yield range (uncertainty)
        uncertainty = (1 - confidence) * 0.3  # Max 30% uncertainty
        yield_range_min = predicted_yield * (1 - uncertainty)
        yield_range_max = predicted_yield * (1 + uncertainty)

        # Calculate comparisons
        regional_avg = self.YEMEN_AVERAGE_YIELDS.get(crop_code, base_yield * 0.7)
        comparison_to_average = ((predicted_yield - regional_avg) / regional_avg) * 100
        comparison_to_base = ((predicted_yield - base_yield) / base_yield) * 100

        # Get factor contributions (normalized to 0-1)
        factors = self.get_yield_factors(
            ndvi_peak=ndvi_peak,
            ndvi_integral=ndvi_integral,
            gdd=gdd,
            precipitation=precipitation,
            water_stress_factor=water_stress_factor,
            soil_moisture=soil_moisture or 0.5,
            crop_code=crop_code,
        )

        # Generate recommendations
        recommendations_ar, recommendations_en = self.generate_recommendations(
            crop_code=crop_code,
            crop_name_ar=crop_name_ar,
            crop_name_en=crop_name_en,
            ndvi_peak=ndvi_peak,
            water_stress_factor=water_stress_factor,
            soil_moisture=soil_moisture,
            gdd=gdd,
            growth_stage=growth_stage,
            predicted_yield=predicted_yield,
            base_yield=base_yield,
            factors=factors,
        )

        return YieldPrediction(
            field_id=field_id,
            crop_code=crop_code,
            crop_name_ar=crop_name_ar,
            crop_name_en=crop_name_en,
            predicted_yield_ton_ha=round(predicted_yield, 2),
            yield_range_min=round(yield_range_min, 2),
            yield_range_max=round(yield_range_max, 2),
            confidence=round(confidence, 3),
            factors=factors,
            comparison_to_average=round(comparison_to_average, 1),
            comparison_to_base=round(comparison_to_base, 1),
            recommendations_ar=recommendations_ar,
            recommendations_en=recommendations_en,
            prediction_date=datetime.utcnow(),
            growth_stage=growth_stage,
            days_to_harvest=days_to_harvest,
        )

    def calculate_ndvi_integral(self, ndvi_series: list[float]) -> float:
        """
        Calculate cumulative NDVI (area under curve).
        Represents total photosynthetic activity over the season.
        """
        if not ndvi_series or len(ndvi_series) < 2:
            return 0.0

        # Trapezoidal integration
        integral = 0.0
        for i in range(len(ndvi_series) - 1):
            integral += (ndvi_series[i] + ndvi_series[i + 1]) / 2

        return round(integral, 2)

    def calculate_gdd(
        self,
        temp_min_series: list[float],
        temp_max_series: list[float],
        base_temp: float = 10.0,
    ) -> float:
        """
        Calculate Growing Degree Days (GDD).
        GDD = Σ((Tmax + Tmin)/2 - Tbase) for all days where avg temp > base temp
        """
        if not temp_min_series or not temp_max_series:
            return 0.0

        gdd = 0.0
        n = min(len(temp_min_series), len(temp_max_series))

        for i in range(n):
            avg_temp = (temp_max_series[i] + temp_min_series[i]) / 2
            if avg_temp > base_temp:
                gdd += avg_temp - base_temp

        return round(gdd, 1)

    def calculate_water_stress(
        self,
        precipitation: float,
        et0: float,
        kc: float,
        soil_moisture: float | None,
    ) -> float:
        """
        Calculate water stress factor (0-1, where 1 = no stress).
        Uses FAO-56 methodology.
        """
        # Calculate crop water requirement (ETc = ET0 * Kc)
        etc = et0 * kc

        # Water deficit
        water_deficit = max(0, etc - precipitation)

        # Relative water deficit (0-1)
        relative_deficit = min(1.0, water_deficit / etc) if etc > 0 else 0.0

        # Adjust with soil moisture if available
        if soil_moisture is not None:
            # Soil moisture below 0.4 indicates stress
            sm_factor = min(1.0, soil_moisture / 0.4) if soil_moisture < 0.4 else 1.0
            relative_deficit = (relative_deficit + (1 - sm_factor)) / 2

        # Water stress factor (1 = no stress, 0 = severe stress)
        stress_factor = 1 - relative_deficit

        return max(0.0, min(1.0, stress_factor))

    def predict_from_ndvi(
        self,
        crop_code: str,
        base_yield: float,
        ndvi_peak: float,
        ndvi_integral: float,
    ) -> float:
        """
        Predict yield from NDVI using empirical relationship.
        Yield = base_yield * (1 + k * (NDVI_integral - baseline))
        """
        coeffs = self.NDVI_YIELD_COEFFICIENTS.get(
            crop_code, self.NDVI_YIELD_COEFFICIENTS["DEFAULT"]
        )

        k = coeffs["k"]
        baseline = coeffs["baseline_integral"]
        peak_min = coeffs["peak_min"]

        # NDVI integral factor
        integral_factor = 1 + (k * (ndvi_integral - baseline) / baseline)
        integral_factor = max(0.3, min(2.0, integral_factor))  # Limit to 30-200%

        # Peak NDVI factor (penalty if too low)
        peak_factor = ndvi_peak / peak_min if ndvi_peak < peak_min else 1.0

        predicted_yield = base_yield * integral_factor * peak_factor

        return max(0.0, predicted_yield)

    def predict_from_gdd(
        self,
        crop_code: str,
        base_yield: float,
        gdd_accumulated: float,
    ) -> float:
        """
        Predict yield from GDD using response curve.
        Yield increases with GDD up to optimal, then decreases.
        """
        gdd_req = self.GDD_REQUIREMENTS.get(crop_code, self.GDD_REQUIREMENTS["DEFAULT"])

        optimal = gdd_req["optimal"]
        min_gdd = gdd_req["min"]
        max_gdd = gdd_req["max"]

        if gdd_accumulated < min_gdd:
            # Below minimum: linear reduction
            gdd_factor = gdd_accumulated / min_gdd
        elif gdd_accumulated <= optimal:
            # Below optimal: linear increase
            gdd_factor = 0.7 + 0.3 * ((gdd_accumulated - min_gdd) / (optimal - min_gdd))
        elif gdd_accumulated <= max_gdd:
            # Above optimal: slight decrease
            gdd_factor = 1.0 - 0.2 * ((gdd_accumulated - optimal) / (max_gdd - optimal))
        else:
            # Excessive heat: penalty
            excess = (gdd_accumulated - max_gdd) / max_gdd
            gdd_factor = 0.8 * math.exp(-excess)

        gdd_factor = max(0.2, min(1.0, gdd_factor))

        return base_yield * gdd_factor

    def predict_from_soil_moisture(
        self,
        base_yield: float,
        soil_moisture: float | None,
    ) -> float:
        """
        Predict yield from soil moisture.
        Optimal: 0.4-0.6, Stress below 0.3, excess above 0.7
        """
        if soil_moisture is None:
            return base_yield  # Assume optimal

        if 0.4 <= soil_moisture <= 0.6:
            sm_factor = 1.0  # Optimal
        elif soil_moisture < 0.4:
            sm_factor = max(0.4, soil_moisture / 0.4)  # Drought stress
        else:  # > 0.6
            sm_factor = max(0.7, 1.0 - 0.3 * ((soil_moisture - 0.6) / 0.4))  # Waterlogging

        return base_yield * sm_factor

    def estimate_growth_stage(
        self,
        planting_date: datetime | None,
        gdd_accumulated: float,
        crop_code: str,
        crop_info: CropInfo | None,
    ) -> tuple[str, int | None]:
        """
        Estimate current growth stage and days to harvest.
        """
        if not planting_date:
            return "unknown", None

        days_since_planting = (datetime.utcnow() - planting_date).days
        season_days = crop_info.growing_season_days if crop_info else 120

        # Estimate based on days
        progress = days_since_planting / season_days

        if progress < 0.1:
            stage = "germination"
        elif progress < 0.3:
            stage = "vegetative"
        elif progress < 0.5:
            stage = "flowering"
        elif progress < 0.8:
            stage = "fruiting"
        elif progress < 1.0:
            stage = "ripening"
        else:
            stage = "harvest_ready"

        days_to_harvest = max(0, season_days - days_since_planting)

        return stage, days_to_harvest

    def calculate_confidence(
        self,
        ndvi_series: list[float],
        ndvi_peak: float,
        gdd: float,
        water_stress_factor: float,
        model_variance: list[float],
    ) -> float:
        """
        Calculate prediction confidence (0-1) based on data quality and model agreement.
        """
        confidence = 1.0

        # Factor 1: NDVI data quality (30%)
        if not ndvi_series or len(ndvi_series) < 3:
            confidence *= 0.6
        elif len(ndvi_series) < 5:
            confidence *= 0.8

        # Factor 2: NDVI peak quality (20%)
        if ndvi_peak < 0.3:
            confidence *= 0.5
        elif ndvi_peak < 0.5:
            confidence *= 0.7

        # Factor 3: Model agreement (30%)
        if model_variance:
            mean_yield = sum(model_variance) / len(model_variance)
            if mean_yield > 0:
                variance = sum((y - mean_yield) ** 2 for y in model_variance) / len(model_variance)
                cv = (variance**0.5) / mean_yield  # Coefficient of variation
                agreement_factor = max(0.5, 1 - cv)
                confidence *= agreement_factor

        # Factor 4: Water stress severity (20%)
        if water_stress_factor < 0.5:
            confidence *= 0.8  # High stress reduces confidence

        return max(0.3, min(1.0, confidence))

    def get_yield_factors(
        self,
        ndvi_peak: float,
        ndvi_integral: float,
        gdd: float,
        precipitation: float,
        water_stress_factor: float,
        soil_moisture: float,
        crop_code: str,
    ) -> dict[str, float]:
        """
        Return contribution of each factor to yield (normalized 0-1).
        """
        # Normalize each factor to 0-1 scale
        factors = {
            "vegetation_health": min(1.0, ndvi_peak / 0.8),  # 0.8 = excellent
            "biomass_accumulation": min(1.0, ndvi_integral / 60.0),  # 60 = high productivity
            "thermal_time": self._normalize_gdd(gdd, crop_code),
            "water_availability": water_stress_factor,
            "soil_moisture": min(1.0, soil_moisture / 0.6),  # 0.6 = optimal
        }

        # Round to 3 decimals
        return {k: round(v, 3) for k, v in factors.items()}

    def _normalize_gdd(self, gdd: float, crop_code: str) -> float:
        """Normalize GDD to 0-1 scale based on crop requirements."""
        gdd_req = self.GDD_REQUIREMENTS.get(crop_code, self.GDD_REQUIREMENTS["DEFAULT"])
        optimal = gdd_req["optimal"]

        # 1.0 at optimal, decreases away from optimal
        if gdd <= 0:
            return 0.0
        elif gdd <= optimal:
            return min(1.0, gdd / optimal)
        else:
            return max(0.5, 1.0 - 0.5 * ((gdd - optimal) / optimal))

    def generate_recommendations(
        self,
        crop_code: str,
        crop_name_ar: str,
        crop_name_en: str,
        ndvi_peak: float,
        water_stress_factor: float,
        soil_moisture: float | None,
        gdd: float,
        growth_stage: str,
        predicted_yield: float,
        base_yield: float,
        factors: dict[str, float],
    ) -> tuple[list[str], list[str]]:
        """
        Generate actionable recommendations based on prediction factors.
        """
        recommendations_ar = []
        recommendations_en = []

        # Water management
        if water_stress_factor < 0.6:
            recommendations_ar.append(
                f"🌊 إجهاد مائي مكتشف - زيادة الري بنسبة {int((1 - water_stress_factor) * 100)}% لتحسين الإنتاجية"
            )
            recommendations_en.append(
                f"🌊 Water stress detected - increase irrigation by {int((1 - water_stress_factor) * 100)}% to improve yield"
            )
        elif soil_moisture and soil_moisture > 0.7:
            recommendations_ar.append("⚠️ رطوبة التربة عالية - تقليل الري لتجنب تشبع الجذور")
            recommendations_en.append(
                "⚠️ High soil moisture - reduce irrigation to avoid root waterlogging"
            )

        # Vegetation health
        if ndvi_peak < 0.5:
            recommendations_ar.append(
                f"🌱 صحة النباتات ضعيفة (NDVI: {ndvi_peak:.2f}) - تطبيق سماد نيتروجيني فوري"
            )
            recommendations_en.append(
                f"🌱 Poor vegetation health (NDVI: {ndvi_peak:.2f}) - apply nitrogen fertilizer immediately"
            )
        elif ndvi_peak < 0.65:
            recommendations_ar.append("🌿 صحة النباتات متوسطة - تحسين التسميد الورقي")
            recommendations_en.append("🌿 Moderate vegetation - improve foliar fertilization")

        # Yield potential
        yield_ratio = predicted_yield / base_yield
        if yield_ratio < 0.7:
            recommendations_ar.append(
                f"📉 الإنتاجية المتوقعة منخفضة ({int(yield_ratio * 100)}% من الإمكانية) - تكثيف الإدارة"
            )
            recommendations_en.append(
                f"📉 Low yield potential ({int(yield_ratio * 100)}% of capacity) - intensify management"
            )
        elif yield_ratio > 1.2:
            recommendations_ar.append(
                f"✨ أداء ممتاز! الإنتاجية المتوقعة {int(yield_ratio * 100)}% من الطاقة القاعدية"
            )
            recommendations_en.append(
                f"✨ Excellent performance! Predicted yield is {int(yield_ratio * 100)}% of base capacity"
            )

        # Growth stage specific
        if growth_stage == "flowering":
            recommendations_ar.append("🌸 مرحلة التزهير - تجنب إجهاد الماء وتطبيق البوتاسيوم")
            recommendations_en.append("🌸 Flowering stage - avoid water stress and apply potassium")
        elif growth_stage == "fruiting":
            recommendations_ar.append("🍅 مرحلة الإثمار - الحفاظ على رطوبة ثابتة وحماية من الآفات")
            recommendations_en.append(
                "🍅 Fruiting stage - maintain consistent moisture and protect from pests"
            )
        elif growth_stage == "ripening":
            recommendations_ar.append("🌾 مرحلة النضج - تقليل الري تدريجياً والاستعداد للحصاد")
            recommendations_en.append(
                "🌾 Ripening stage - gradually reduce irrigation and prepare for harvest"
            )

        # Critical factors
        critical_factors = [k for k, v in factors.items() if v < 0.5]
        if critical_factors:
            factor_names_ar = {
                "vegetation_health": "صحة النباتات",
                "biomass_accumulation": "تراكم الكتلة الحيوية",
                "thermal_time": "الوقت الحراري",
                "water_availability": "توفر المياه",
                "soil_moisture": "رطوبة التربة",
            }
            factor_names_en = {
                "vegetation_health": "vegetation health",
                "biomass_accumulation": "biomass accumulation",
                "thermal_time": "thermal time",
                "water_availability": "water availability",
                "soil_moisture": "soil moisture",
            }

            critical_ar = ", ".join([factor_names_ar.get(f, f) for f in critical_factors])
            critical_en = ", ".join([factor_names_en.get(f, f) for f in critical_factors])

            recommendations_ar.append(f"⚠️ عوامل حرجة تحتاج تحسين: {critical_ar}")
            recommendations_en.append(f"⚠️ Critical factors needing improvement: {critical_en}")

        # If no issues
        if not recommendations_ar:
            recommendations_ar.append(
                f"✅ {crop_name_ar} في حالة جيدة - استمر في الممارسات الحالية"
            )
            recommendations_en.append(
                f"✅ {crop_name_en} is in good condition - continue current practices"
            )

        return recommendations_ar, recommendations_en
