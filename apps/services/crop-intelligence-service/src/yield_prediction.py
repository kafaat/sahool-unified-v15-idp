"""
SAHOOL Yield Prediction Module
وحدة تنبؤ المحصول

Yield prediction based on vegetation indices, weather, and historical data.
Uses regression models calibrated for Yemen crops.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class CropType(str, Enum):
    """أنواع المحاصيل للتنبؤ بالمحصول"""

    WHEAT = "wheat"  # قمح
    SORGHUM = "sorghum"  # ذرة رفيعة
    MILLET = "millet"  # دخن
    TOMATO = "tomato"  # طماطم
    POTATO = "potato"  # بطاطس
    CORN = "corn"  # ذرة
    COFFEE = "coffee"  # قهوة (بن يمني)
    DATE_PALM = "date_palm"  # نخيل
    MANGO = "mango"  # مانجو
    CITRUS = "citrus"  # حمضيات
    GRAPE = "grape"  # عنب
    COTTON = "cotton"  # قطن
    QAT = "qat"  # قات
    SESAME = "sesame"  # سمسم
    ALFALFA = "alfalfa"  # برسيم


class YieldConfidence(str, Enum):
    """مستوى ثقة التنبؤ"""

    HIGH = "high"  # مرتفع (>80%)
    MEDIUM = "medium"  # متوسط (60-80%)
    LOW = "low"  # منخفض (<60%)


class YieldTrend(str, Enum):
    """اتجاه المحصول"""

    INCREASING = "increasing"  # متزايد
    STABLE = "stable"  # مستقر
    DECREASING = "decreasing"  # متناقص


# Crop yield parameters (calibrated for Yemen conditions)
CROP_PARAMETERS = {
    CropType.WHEAT: {
        "name_ar": "قمح",
        "base_yield_kg_ha": 2500,  # Average yield in Yemen
        "max_yield_kg_ha": 4500,
        "ndvi_coefficient": 8000,  # Yield response to NDVI
        "water_sensitivity": 0.8,  # Sensitivity to water stress
        "optimal_ndvi_range": (0.55, 0.75),
        "growing_days": 120,
        "price_usd_per_kg": 0.35,
    },
    CropType.SORGHUM: {
        "name_ar": "ذرة رفيعة",
        "base_yield_kg_ha": 1800,
        "max_yield_kg_ha": 3500,
        "ndvi_coefficient": 6000,
        "water_sensitivity": 0.6,  # Drought tolerant
        "optimal_ndvi_range": (0.50, 0.70),
        "growing_days": 100,
        "price_usd_per_kg": 0.30,
    },
    CropType.MILLET: {
        "name_ar": "دخن",
        "base_yield_kg_ha": 1200,
        "max_yield_kg_ha": 2500,
        "ndvi_coefficient": 5000,
        "water_sensitivity": 0.5,  # Very drought tolerant
        "optimal_ndvi_range": (0.45, 0.65),
        "growing_days": 90,
        "price_usd_per_kg": 0.28,
    },
    CropType.TOMATO: {
        "name_ar": "طماطم",
        "base_yield_kg_ha": 25000,
        "max_yield_kg_ha": 50000,
        "ndvi_coefficient": 80000,
        "water_sensitivity": 0.9,
        "optimal_ndvi_range": (0.60, 0.80),
        "growing_days": 75,
        "price_usd_per_kg": 0.40,
    },
    CropType.POTATO: {
        "name_ar": "بطاطس",
        "base_yield_kg_ha": 20000,
        "max_yield_kg_ha": 40000,
        "ndvi_coefficient": 70000,
        "water_sensitivity": 0.85,
        "optimal_ndvi_range": (0.55, 0.75),
        "growing_days": 100,
        "price_usd_per_kg": 0.25,
    },
    CropType.CORN: {
        "name_ar": "ذرة",
        "base_yield_kg_ha": 3500,
        "max_yield_kg_ha": 7000,
        "ndvi_coefficient": 12000,
        "water_sensitivity": 0.75,
        "optimal_ndvi_range": (0.60, 0.80),
        "growing_days": 110,
        "price_usd_per_kg": 0.22,
    },
    CropType.COFFEE: {
        "name_ar": "قهوة (بن يمني)",
        "base_yield_kg_ha": 800,  # Green beans
        "max_yield_kg_ha": 1500,
        "ndvi_coefficient": 2000,
        "water_sensitivity": 0.7,
        "optimal_ndvi_range": (0.50, 0.70),
        "growing_days": 365,  # Perennial
        "price_usd_per_kg": 8.00,  # Premium Yemeni coffee
    },
    CropType.DATE_PALM: {
        "name_ar": "نخيل (تمور)",
        "base_yield_kg_ha": 6000,
        "max_yield_kg_ha": 12000,
        "ndvi_coefficient": 15000,
        "water_sensitivity": 0.4,  # Drought tolerant
        "optimal_ndvi_range": (0.40, 0.60),
        "growing_days": 365,  # Perennial
        "price_usd_per_kg": 1.50,
    },
    CropType.MANGO: {
        "name_ar": "مانجو",
        "base_yield_kg_ha": 8000,
        "max_yield_kg_ha": 15000,
        "ndvi_coefficient": 20000,
        "water_sensitivity": 0.65,
        "optimal_ndvi_range": (0.55, 0.75),
        "growing_days": 365,  # Perennial
        "price_usd_per_kg": 1.20,
    },
    CropType.CITRUS: {
        "name_ar": "حمضيات",
        "base_yield_kg_ha": 15000,
        "max_yield_kg_ha": 30000,
        "ndvi_coefficient": 40000,
        "water_sensitivity": 0.75,
        "optimal_ndvi_range": (0.55, 0.75),
        "growing_days": 365,  # Perennial
        "price_usd_per_kg": 0.60,
    },
    CropType.GRAPE: {
        "name_ar": "عنب",
        "base_yield_kg_ha": 10000,
        "max_yield_kg_ha": 20000,
        "ndvi_coefficient": 30000,
        "water_sensitivity": 0.7,
        "optimal_ndvi_range": (0.50, 0.70),
        "growing_days": 180,
        "price_usd_per_kg": 1.00,
    },
    CropType.COTTON: {
        "name_ar": "قطن",
        "base_yield_kg_ha": 1500,  # Lint
        "max_yield_kg_ha": 3000,
        "ndvi_coefficient": 5000,
        "water_sensitivity": 0.8,
        "optimal_ndvi_range": (0.55, 0.75),
        "growing_days": 150,
        "price_usd_per_kg": 1.80,
    },
    CropType.QAT: {
        "name_ar": "قات",
        "base_yield_kg_ha": 4000,  # Fresh leaves
        "max_yield_kg_ha": 8000,
        "ndvi_coefficient": 10000,
        "water_sensitivity": 0.85,
        "optimal_ndvi_range": (0.60, 0.80),
        "growing_days": 365,  # Perennial
        "price_usd_per_kg": 5.00,
    },
    CropType.SESAME: {
        "name_ar": "سمسم",
        "base_yield_kg_ha": 600,
        "max_yield_kg_ha": 1200,
        "ndvi_coefficient": 2500,
        "water_sensitivity": 0.6,
        "optimal_ndvi_range": (0.45, 0.65),
        "growing_days": 100,
        "price_usd_per_kg": 2.00,
    },
    CropType.ALFALFA: {
        "name_ar": "برسيم",
        "base_yield_kg_ha": 15000,  # Dry matter per year
        "max_yield_kg_ha": 25000,
        "ndvi_coefficient": 35000,
        "water_sensitivity": 0.75,
        "optimal_ndvi_range": (0.55, 0.75),
        "growing_days": 365,  # Perennial with multiple cuts
        "price_usd_per_kg": 0.15,
    },
}


@dataclass
class YieldPrediction:
    """نتيجة تنبؤ المحصول"""

    crop_type: CropType
    predicted_yield_kg_ha: float
    predicted_yield_range: tuple[float, float]
    confidence: YieldConfidence
    confidence_percent: float
    trend: YieldTrend
    estimated_revenue_usd: float
    recommendations: list[str]
    recommendations_ar: list[str]
    limiting_factors: list[str]
    limiting_factors_ar: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "crop_type": self.crop_type.value,
            "crop_name_ar": CROP_PARAMETERS.get(self.crop_type, {}).get(
                "name_ar", self.crop_type.value
            ),
            "predicted_yield_kg_ha": round(self.predicted_yield_kg_ha),
            "predicted_yield_range": {
                "min": round(self.predicted_yield_range[0]),
                "max": round(self.predicted_yield_range[1]),
            },
            "confidence": self.confidence.value,
            "confidence_percent": round(self.confidence_percent),
            "trend": self.trend.value,
            "estimated_revenue_usd": round(self.estimated_revenue_usd, 2),
            "recommendations": self.recommendations,
            "recommendations_ar": self.recommendations_ar,
            "limiting_factors": self.limiting_factors,
            "limiting_factors_ar": self.limiting_factors_ar,
        }


def predict_yield(
    crop_type: CropType,
    ndvi: float,
    evi: float,
    ndwi: float,
    ndre: float,
    lci: float,
    savi: float,
    field_area_hectares: float = 1.0,
    growth_stage_percent: float = 50.0,
    historical_yield_kg_ha: float | None = None,
    water_stress_factor: float = 1.0,
    disease_factor: float = 1.0,
) -> YieldPrediction:
    """
    تنبؤ المحصول من المؤشرات النباتية
    Predict yield from vegetation indices

    Args:
        crop_type: Type of crop
        ndvi: Normalized Difference Vegetation Index
        evi: Enhanced Vegetation Index
        ndwi: Normalized Difference Water Index
        ndre: Normalized Difference Red Edge
        lci: Leaf Chlorophyll Index
        savi: Soil-Adjusted Vegetation Index
        field_area_hectares: Field area in hectares
        growth_stage_percent: Crop growth stage (0-100%)
        historical_yield_kg_ha: Historical average yield (optional)
        water_stress_factor: Water stress factor (0-1, 1=no stress)
        disease_factor: Disease impact factor (0-1, 1=no disease)

    Returns:
        YieldPrediction with predicted yield and recommendations
    """
    params = CROP_PARAMETERS.get(crop_type)
    if not params:
        # Use generic parameters if crop not found
        params = {
            "name_ar": crop_type.value,
            "base_yield_kg_ha": 2000,
            "max_yield_kg_ha": 4000,
            "ndvi_coefficient": 5000,
            "water_sensitivity": 0.7,
            "optimal_ndvi_range": (0.50, 0.70),
            "growing_days": 120,
            "price_usd_per_kg": 0.50,
        }

    base_yield = params["base_yield_kg_ha"]
    max_yield = params["max_yield_kg_ha"]
    ndvi_coef = params["ndvi_coefficient"]
    water_sens = params["water_sensitivity"]
    optimal_ndvi = params["optimal_ndvi_range"]
    price = params["price_usd_per_kg"]

    # Calculate NDVI-based yield estimate
    # Using logistic-like response curve
    if ndvi >= optimal_ndvi[1]:
        ndvi_factor = 1.0
    elif ndvi >= optimal_ndvi[0]:
        ndvi_factor = 0.8 + 0.2 * ((ndvi - optimal_ndvi[0]) / (optimal_ndvi[1] - optimal_ndvi[0]))
    elif ndvi >= 0.3:
        ndvi_factor = 0.4 + 0.4 * ((ndvi - 0.3) / (optimal_ndvi[0] - 0.3))
    else:
        ndvi_factor = max(0.1, ndvi * 1.5)

    # Water stress adjustment based on NDWI
    water_factor = 1.0
    if ndwi < -0.1:
        water_factor = 0.6 + 0.4 * (ndwi + 0.3) / 0.2  # Scale from -0.3 to -0.1
        water_factor = max(0.4, min(1.0, water_factor))
    water_factor *= water_stress_factor

    # Nitrogen/chlorophyll adjustment based on NDRE and LCI
    nitrogen_factor = 1.0
    if ndre < 0.22:
        nitrogen_factor = 0.7 + 0.3 * (ndre / 0.22)
    if lci < 0.20:
        nitrogen_factor *= 0.8 + 0.2 * (lci / 0.20)

    # EVI provides additional canopy density information
    evi_factor = min(1.0, evi / 0.5) if evi > 0.2 else 0.6

    # SAVI adjustment for sparse vegetation
    savi_factor = min(1.0, savi / 0.6) if savi > 0.2 else 0.7

    # Combine factors
    combined_factor = (
        ndvi_factor * 0.35
        + evi_factor * 0.20
        + water_factor * water_sens * 0.20
        + nitrogen_factor * 0.15
        + savi_factor * 0.10
    )

    # Growth stage adjustment (yield estimate improves as crop matures)
    if growth_stage_percent < 50:
        stage_uncertainty = 0.4  # High uncertainty early in season
    elif growth_stage_percent < 75:
        stage_uncertainty = 0.25
    else:
        stage_uncertainty = 0.15

    # Calculate predicted yield
    predicted_yield = base_yield + (max_yield - base_yield) * combined_factor

    # Apply disease factor
    predicted_yield *= disease_factor

    # Use historical data if available for calibration
    if historical_yield_kg_ha:
        # Blend with historical (30% weight to current prediction)
        historical_ratio = historical_yield_kg_ha / base_yield
        predicted_yield = predicted_yield * 0.7 + historical_yield_kg_ha * combined_factor * 0.3

    # Calculate confidence and range
    uncertainty_range = predicted_yield * stage_uncertainty
    yield_min = max(0, predicted_yield - uncertainty_range)
    yield_max = min(max_yield, predicted_yield + uncertainty_range)

    # Confidence based on data quality and growth stage
    data_quality = (
        (1.0 if 0.3 <= ndvi <= 0.9 else 0.7)
        * (1.0 if ndwi > -0.2 else 0.8)
        * (1.0 if ndre > 0.15 else 0.8)
    )
    confidence_pct = min(95, max(30, (1.0 - stage_uncertainty) * data_quality * 100))

    if confidence_pct >= 80:
        confidence = YieldConfidence.HIGH
    elif confidence_pct >= 60:
        confidence = YieldConfidence.MEDIUM
    else:
        confidence = YieldConfidence.LOW

    # Determine trend
    if combined_factor >= 0.8:
        trend = YieldTrend.INCREASING
    elif combined_factor >= 0.5:
        trend = YieldTrend.STABLE
    else:
        trend = YieldTrend.DECREASING

    # Calculate revenue
    total_yield_kg = predicted_yield * field_area_hectares
    revenue = total_yield_kg * price

    # Generate recommendations and limiting factors
    recommendations, recommendations_ar = _get_yield_recommendations(
        ndvi, evi, ndwi, ndre, lci, savi, water_factor, nitrogen_factor, crop_type
    )
    limiting_factors, limiting_factors_ar = _get_limiting_factors(
        ndvi, ndwi, ndre, lci, optimal_ndvi
    )

    return YieldPrediction(
        crop_type=crop_type,
        predicted_yield_kg_ha=predicted_yield,
        predicted_yield_range=(yield_min, yield_max),
        confidence=confidence,
        confidence_percent=confidence_pct,
        trend=trend,
        estimated_revenue_usd=revenue,
        recommendations=recommendations,
        recommendations_ar=recommendations_ar,
        limiting_factors=limiting_factors,
        limiting_factors_ar=limiting_factors_ar,
    )


def _get_yield_recommendations(
    ndvi: float,
    evi: float,
    ndwi: float,
    ndre: float,
    lci: float,
    savi: float,
    water_factor: float,
    nitrogen_factor: float,
    crop_type: CropType,
) -> tuple[list[str], list[str]]:
    """Generate yield improvement recommendations"""
    recommendations_en = []
    recommendations_ar = []

    if ndwi < -0.1:
        recommendations_en.append("Increase irrigation frequency to address water stress")
        recommendations_ar.append("زيادة تكرار الري لمعالجة الإجهاد المائي")

    if ndre < 0.20:
        recommendations_en.append("Apply nitrogen fertilizer to improve chlorophyll content")
        recommendations_ar.append("تطبيق سماد نيتروجيني لتحسين محتوى الكلوروفيل")

    if lci < 0.15:
        recommendations_en.append("Consider micronutrient application (Fe, Zn)")
        recommendations_ar.append("فكر في تطبيق العناصر الصغرى (حديد، زنك)")

    if ndvi < 0.5:
        recommendations_en.append("Monitor plant health - NDVI indicates reduced vigor")
        recommendations_ar.append("راقب صحة النبات - NDVI يشير لقوة منخفضة")

    if evi < 0.35:
        recommendations_en.append("Low canopy density detected - check for pest/disease issues")
        recommendations_ar.append("كثافة مظلة منخفضة - تحقق من مشاكل الآفات/الأمراض")

    if not recommendations_en:
        recommendations_en.append("Crop is developing well - maintain current management")
        recommendations_ar.append("المحصول ينمو جيداً - استمر في الإدارة الحالية")

    return recommendations_en, recommendations_ar


def _get_limiting_factors(
    ndvi: float, ndwi: float, ndre: float, lci: float, optimal_ndvi: tuple
) -> tuple[list[str], list[str]]:
    """Identify limiting factors for yield"""
    factors_en = []
    factors_ar = []

    if ndwi < -0.15:
        factors_en.append("Severe water stress")
        factors_ar.append("إجهاد مائي شديد")
    elif ndwi < -0.05:
        factors_en.append("Moderate water stress")
        factors_ar.append("إجهاد مائي معتدل")

    if ndre < 0.15:
        factors_en.append("Nitrogen deficiency")
        factors_ar.append("نقص نيتروجين")

    if lci < 0.12:
        factors_en.append("Low chlorophyll/nutrient deficiency")
        factors_ar.append("نقص كلوروفيل/عناصر غذائية")

    if ndvi < optimal_ndvi[0]:
        factors_en.append("Below optimal vegetation development")
        factors_ar.append("نمو نباتي أقل من المثالي")

    if not factors_en:
        factors_en.append("No significant limiting factors detected")
        factors_ar.append("لا توجد عوامل مقيدة ملحوظة")

    return factors_en, factors_ar


def compare_yield_potential(
    predictions: list[YieldPrediction],
) -> dict[str, Any]:
    """
    مقارنة إمكانات المحصول لعدة محاصيل
    Compare yield potential across multiple crops

    Args:
        predictions: List of yield predictions for different crops

    Returns:
        Comparison summary with rankings
    """
    if not predictions:
        return {"error": "No predictions provided"}

    # Sort by revenue
    sorted_by_revenue = sorted(predictions, key=lambda p: p.estimated_revenue_usd, reverse=True)

    # Sort by yield
    sorted_by_yield = sorted(predictions, key=lambda p: p.predicted_yield_kg_ha, reverse=True)

    # Sort by confidence
    sorted_by_confidence = sorted(predictions, key=lambda p: p.confidence_percent, reverse=True)

    return {
        "total_crops_compared": len(predictions),
        "best_by_revenue": {
            "crop": sorted_by_revenue[0].crop_type.value,
            "revenue_usd": round(sorted_by_revenue[0].estimated_revenue_usd, 2),
        },
        "best_by_yield": {
            "crop": sorted_by_yield[0].crop_type.value,
            "yield_kg_ha": round(sorted_by_yield[0].predicted_yield_kg_ha),
        },
        "most_confident": {
            "crop": sorted_by_confidence[0].crop_type.value,
            "confidence_pct": round(sorted_by_confidence[0].confidence_percent),
        },
        "rankings": {
            "by_revenue": [
                {
                    "rank": i + 1,
                    "crop": p.crop_type.value,
                    "revenue_usd": round(p.estimated_revenue_usd, 2),
                }
                for i, p in enumerate(sorted_by_revenue)
            ],
            "by_yield": [
                {
                    "rank": i + 1,
                    "crop": p.crop_type.value,
                    "yield_kg_ha": round(p.predicted_yield_kg_ha),
                }
                for i, p in enumerate(sorted_by_yield)
            ],
        },
    }


def get_crop_parameters(crop_type: CropType | None = None) -> dict[str, Any]:
    """
    الحصول على معاملات المحصول
    Get crop parameters

    Args:
        crop_type: Optional specific crop type

    Returns:
        Crop parameters dictionary
    """
    if crop_type:
        params = CROP_PARAMETERS.get(crop_type)
        if params:
            return {
                "crop_type": crop_type.value,
                **params,
            }
        return {"error": f"Unknown crop type: {crop_type}"}

    return {
        crop.value: {
            "name_ar": params["name_ar"],
            "base_yield_kg_ha": params["base_yield_kg_ha"],
            "max_yield_kg_ha": params["max_yield_kg_ha"],
            "growing_days": params["growing_days"],
            "price_usd_per_kg": params["price_usd_per_kg"],
        }
        for crop, params in CROP_PARAMETERS.items()
    }
