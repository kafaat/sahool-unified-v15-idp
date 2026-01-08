"""
SAHOOL Yield Prediction Ensemble Model
نموذج مجموعة التنبؤ بالإنتاج - نظام صحول

Ensemble model combining multiple predictors for accurate yield estimation.
نموذج مجموعة يجمع عدة محاكيات للتنبؤ الدقيق بالإنتاج.

Sub-models:
1. NDVI-Based Predictor (وزن: 0.35) - Plant health and vigor
2. GDD-Based Predictor (وزن: 0.25) - Thermal time accumulation
3. Soil Moisture Predictor (وزن: 0.20) - Water stress analysis
4. Historical Trend Predictor (وزن: 0.20) - Past performance patterns

Author: SAHOOL Development Team
Date: 2026-01-02
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

import numpy as np

from .crop_parameters import CropParameters, Region, get_crop_parameters

# Configure logging - تكوين السجلات
logger = logging.getLogger(__name__)


class GrowthStage(Enum):
    """Crop growth stages - مراحل نمو المحصول"""

    GERMINATION = "germination"  # الإنبات
    VEGETATIVE = "vegetative"  # النمو الخضري
    FLOWERING = "flowering"  # الإزهار
    FRUIT_SET = "fruit_set"  # عقد الثمار
    MATURATION = "maturation"  # النضج
    HARVEST_READY = "harvest_ready"  # جاهز للحصاد


class LimitingFactor(Enum):
    """Factors limiting yield - العوامل المحددة للإنتاج"""

    WATER_STRESS = "water_stress"  # إجهاد مائي
    NUTRIENT_DEFICIENCY = "nutrient_deficiency"  # نقص العناصر الغذائية
    HEAT_STRESS = "heat_stress"  # إجهاد حراري
    DISEASE_PRESSURE = "disease_pressure"  # ضغط الأمراض
    POOR_PLANT_HEALTH = "poor_plant_health"  # صحة نبات منخفضة
    SOIL_SALINITY = "soil_salinity"  # ملوحة التربة
    SOIL_pH_IMBALANCE = "soil_ph_imbalance"  # اختلال pH التربة
    INADEQUATE_GDD = "inadequate_gdd"  # نقص درجات الحرارة التراكمية
    INSUFFICIENT_DATA = "insufficient_data"  # بيانات غير كافية


@dataclass
class ConfidenceMetrics:
    """
    Confidence calculation metrics
    مقاييس حساب الثقة
    """

    # Data completeness score (0-1) - درجة اكتمال البيانات
    data_completeness: float

    # Model agreement score (0-1) - درجة توافق النماذج
    model_agreement: float

    # Historical accuracy adjustment (0-1) - تعديل الدقة التاريخية
    historical_accuracy: float

    # Final confidence (0-1) - الثقة النهائية
    final_confidence: float

    # Individual model confidences - ثقة النماذج الفردية
    model_confidences: dict[str, float] = field(default_factory=dict)


@dataclass
class YieldPrediction:
    """
    Comprehensive yield prediction output
    ناتج شامل للتنبؤ بالإنتاج
    """

    # Basic prediction - التنبؤ الأساسي
    predicted_yield_kg_per_hectare: float

    # Confidence interval - فاصل الثقة
    confidence_interval: dict[str, float]  # {"low": x, "mid": y, "high": z}

    # Overall confidence (0-1) - الثقة الإجمالية
    confidence: float

    # Limiting factors - العوامل المحددة
    limiting_factors: list[dict[str, Any]]

    # Recommendations - التوصيات
    recommendations: list[dict[str, str]]

    # Additional metadata - بيانات إضافية
    crop_id: str
    region: Region
    growth_stage: GrowthStage
    days_to_harvest: int
    prediction_date: datetime = field(default_factory=datetime.now)

    # Sub-model predictions - تنبؤات النماذج الفرعية
    sub_model_predictions: dict[str, float] = field(default_factory=dict)

    # Confidence metrics - مقاييس الثقة
    confidence_metrics: ConfidenceMetrics | None = None

    # Economic projections - التوقعات الاقتصادية
    estimated_revenue_per_ha: float = 0.0
    estimated_total_revenue: float = 0.0


@dataclass
class FieldData:
    """
    Field data input for prediction
    بيانات الحقل المدخلة للتنبؤ
    """

    # Basic field information - المعلومات الأساسية للحقل
    field_id: str
    crop_id: str
    region: Region
    area_hectares: float

    # NDVI data - بيانات NDVI
    ndvi_current: float | None = None
    ndvi_peak: float | None = None
    ndvi_history: list[tuple[datetime, float]] | None = None

    # Weather/Climate data - بيانات الطقس/المناخ
    accumulated_gdd: float | None = None
    current_temperature: float | None = None
    temperature_history: list[float] | None = None

    # Soil data - بيانات التربة
    soil_moisture_current: float | None = None  # Percentage
    soil_moisture_history: list[float] | None = None
    soil_ph: float | None = None
    soil_ec: float | None = None  # dS/m
    soil_nutrient_score: float | None = None  # 0-1

    # Water/Irrigation data - بيانات المياه/الري
    total_irrigation_mm: float | None = None
    total_rainfall_mm: float | None = None

    # Crop status - حالة المحصول
    planting_date: datetime | None = None
    current_growth_stage: GrowthStage | None = None
    days_since_planting: int | None = None

    # Historical data - البيانات التاريخية
    historical_yields: list[float] | None = None  # Past yields for this field

    # Disease/Pest data - بيانات الأمراض/الآفات
    disease_severity: float | None = None  # 0-1


class NDVIBasedPredictor:
    """
    NDVI-based yield predictor - محاكي الإنتاج بناءً على NDVI
    Weight: 0.35 - الوزن: 0.35

    Uses vegetation index to estimate plant health and biomass.
    يستخدم مؤشر النباتات لتقدير صحة النبات والكتلة الحيوية.
    """

    def __init__(self, weight: float = 0.35):
        self.weight = weight
        self.name = "NDVI Model"
        self.name_ar = "نموذج NDVI"

    def predict(self, field_data: FieldData, crop_params: CropParameters) -> tuple[float, float]:
        """
        Predict yield based on NDVI
        التنبؤ بالإنتاج بناءً على NDVI

        Args:
            field_data: Field data - بيانات الحقل
            crop_params: Crop parameters - معلمات المحصول

        Returns:
            (predicted_yield, confidence) - (الإنتاج المتوقع، الثقة)
        """
        base_yield = crop_params.base_yield_kg_per_ha
        optimal_ndvi = crop_params.growth.optimal_ndvi_peak

        # Check for NDVI data availability - التحقق من توفر بيانات NDVI
        ndvi_value = field_data.ndvi_peak or field_data.ndvi_current

        if ndvi_value is None:
            logger.warning(f"No NDVI data available for {field_data.field_id}")
            return base_yield * 0.7, 0.3  # Low confidence default

        # Calculate NDVI ratio - حساب نسبة NDVI
        ndvi_ratio = min(ndvi_value / optimal_ndvi, 1.2)  # Allow 20% over-performance

        # Apply non-linear response curve - تطبيق منحنى استجابة غير خطي
        # Crops respond non-linearly to vegetation health
        if ndvi_ratio < 0.5:
            # Severe stress - إجهاد شديد
            yield_factor = 0.3 * ndvi_ratio
        elif ndvi_ratio < 0.8:
            # Moderate stress - إجهاد متوسط
            yield_factor = 0.15 + 0.65 * ndvi_ratio
        else:
            # Good to excellent condition - حالة جيدة إلى ممتازة
            yield_factor = 0.8 + 0.2 * (ndvi_ratio - 0.8) / 0.4

        predicted_yield = base_yield * yield_factor

        # Calculate confidence based on data quality - حساب الثقة بناءً على جودة البيانات
        confidence = 0.7
        if field_data.ndvi_history and len(field_data.ndvi_history) > 5:
            confidence = 0.85  # Higher confidence with historical data
        elif field_data.ndvi_peak:
            confidence = 0.75  # Peak NDVI is more reliable than current

        logger.info(
            f"NDVI predictor: {predicted_yield:.1f} kg/ha (NDVI: {ndvi_value:.2f}, confidence: {confidence:.2f})"
        )

        return predicted_yield, confidence


class GDDBasedPredictor:
    """
    Growing Degree Days (GDD) based predictor - محاكي بناءً على درجات الحرارة التراكمية
    Weight: 0.25 - الوزن: 0.25

    Uses thermal time accumulation to predict yield.
    يستخدم تراكم الوقت الحراري للتنبؤ بالإنتاج.
    """

    def __init__(self, weight: float = 0.25):
        self.weight = weight
        self.name = "GDD Model"
        self.name_ar = "نموذج درجات الحرارة التراكمية"

    def predict(self, field_data: FieldData, crop_params: CropParameters) -> tuple[float, float]:
        """
        Predict yield based on GDD accumulation
        التنبؤ بالإنتاج بناءً على تراكم GDD

        Args:
            field_data: Field data - بيانات الحقل
            crop_params: Crop parameters - معلمات المحصول

        Returns:
            (predicted_yield, confidence) - (الإنتاج المتوقع، الثقة)
        """
        base_yield = crop_params.base_yield_kg_per_ha
        required_gdd = crop_params.growth.gdd_required

        # Check for GDD data - التحقق من بيانات GDD
        accumulated_gdd = field_data.accumulated_gdd

        if accumulated_gdd is None:
            # Estimate based on days since planting - تقدير بناءً على الأيام منذ الزراعة
            if field_data.days_since_planting and field_data.current_temperature:
                base_temp = crop_params.growth.base_temp
                avg_daily_gdd = max(field_data.current_temperature - base_temp, 0)
                accumulated_gdd = avg_daily_gdd * field_data.days_since_planting
                confidence = 0.5  # Lower confidence with estimated GDD
            else:
                logger.warning(f"No GDD data available for {field_data.field_id}")
                return base_yield * 0.75, 0.4

        else:
            confidence = 0.7

        # Calculate GDD ratio - حساب نسبة GDD
        gdd_ratio = accumulated_gdd / required_gdd

        # Apply developmental response curve - تطبيق منحنى الاستجابة التنموية
        # Yield response follows sigmoid curve relative to GDD completion
        if gdd_ratio < 0.4:
            # Early stage - مرحلة مبكرة
            yield_factor = 0.3
        elif gdd_ratio < 0.7:
            # Mid-development - منتصف التطور
            yield_factor = 0.3 + 0.5 * ((gdd_ratio - 0.4) / 0.3)
        elif gdd_ratio <= 1.0:
            # Late development to optimal - التطور المتأخر إلى الأمثل
            yield_factor = 0.8 + 0.2 * ((gdd_ratio - 0.7) / 0.3)
        else:
            # Over-maturity possible - احتمال النضج الزائد
            over_maturity_penalty = min((gdd_ratio - 1.0) * 0.1, 0.15)
            yield_factor = 1.0 - over_maturity_penalty

        # Check for temperature stress - التحقق من إجهاد درجة الحرارة
        if field_data.current_temperature:
            temp = field_data.current_temperature
            optimal_min = crop_params.growth.optimal_temp_min
            optimal_max = crop_params.growth.optimal_temp_max

            if temp < optimal_min - 5 or temp > optimal_max + 5:
                yield_factor *= 0.8  # Severe temperature stress
                confidence *= 0.9
            elif temp < optimal_min or temp > optimal_max:
                yield_factor *= 0.9  # Moderate temperature stress

        predicted_yield = base_yield * yield_factor

        logger.info(
            f"GDD predictor: {predicted_yield:.1f} kg/ha (GDD: {accumulated_gdd:.0f}/{required_gdd:.0f}, confidence: {confidence:.2f})"
        )

        return predicted_yield, confidence


class SoilMoisturePredictor:
    """
    Soil moisture-based predictor - محاكي بناءً على رطوبة التربة
    Weight: 0.20 - الوزن: 0.20

    Analyzes water stress and availability.
    يحلل الإجهاد المائي وتوفر المياه.
    """

    def __init__(self, weight: float = 0.20):
        self.weight = weight
        self.name = "Soil Moisture Model"
        self.name_ar = "نموذج رطوبة التربة"

    def predict(self, field_data: FieldData, crop_params: CropParameters) -> tuple[float, float]:
        """
        Predict yield based on water availability
        التنبؤ بالإنتاج بناءً على توفر المياه

        Args:
            field_data: Field data - بيانات الحقل
            crop_params: Crop parameters - معلمات المحصول

        Returns:
            (predicted_yield, confidence) - (الإنتاج المتوقع، الثقة)
        """
        base_yield = crop_params.base_yield_kg_per_ha
        required_water_mm = crop_params.growth.water_requirement_mm

        # Calculate total water supply - حساب إجمالي إمداد المياه
        total_water = 0.0
        confidence = 0.6

        if field_data.total_irrigation_mm is not None:
            total_water += field_data.total_irrigation_mm
        if field_data.total_rainfall_mm is not None:
            total_water += field_data.total_rainfall_mm

        # If no water data, estimate from soil moisture - إذا لم توجد بيانات مياه، تقدير من رطوبة التربة
        if total_water == 0 and field_data.soil_moisture_current is not None:
            # Rough estimation - تقدير تقريبي
            soil_moisture_pct = field_data.soil_moisture_current
            if soil_moisture_pct > 60:
                water_adequacy = 1.0
            elif soil_moisture_pct > 40:
                water_adequacy = 0.8
            elif soil_moisture_pct > 20:
                water_adequacy = 0.5
            else:
                water_adequacy = 0.3
            confidence = 0.5
        elif total_water > 0:
            # Calculate water adequacy ratio - حساب نسبة كفاية المياه
            water_adequacy = total_water / required_water_mm
            confidence = 0.7
        else:
            logger.warning(f"No water data available for {field_data.field_id}")
            return base_yield * 0.7, 0.3

        # Apply water stress response curve - تطبيق منحنى استجابة الإجهاد المائي
        # Crops have critical water periods and drought tolerance varies
        drought_tolerance = crop_params.drought_tolerance

        if water_adequacy >= 0.8:
            # Adequate water - مياه كافية
            yield_factor = 0.95 + 0.05 * min(water_adequacy - 0.8, 0.4) / 0.4
        elif water_adequacy >= 0.6:
            # Mild stress - إجهاد خفيف
            stress_impact = (1 - drought_tolerance) * 0.2
            yield_factor = 0.95 - stress_impact * ((0.8 - water_adequacy) / 0.2)
        elif water_adequacy >= 0.4:
            # Moderate stress - إجهاد متوسط
            stress_impact = (1 - drought_tolerance) * 0.4
            yield_factor = 0.75 - stress_impact * ((0.6 - water_adequacy) / 0.2)
        else:
            # Severe stress - إجهاد شديد
            stress_impact = (1 - drought_tolerance) * 0.6
            yield_factor = max(0.35 - stress_impact, 0.1)

        predicted_yield = base_yield * yield_factor

        logger.info(
            f"Soil moisture predictor: {predicted_yield:.1f} kg/ha (water adequacy: {water_adequacy:.2f}, confidence: {confidence:.2f})"
        )

        return predicted_yield, confidence


class HistoricalTrendPredictor:
    """
    Historical trend-based predictor - محاكي بناءً على الاتجاهات التاريخية
    Weight: 0.20 - الوزن: 0.20

    Uses past performance to predict future yields.
    يستخدم الأداء السابق للتنبؤ بالإنتاج المستقبلي.
    """

    def __init__(self, weight: float = 0.20):
        self.weight = weight
        self.name = "Historical Trend Model"
        self.name_ar = "نموذج الاتجاه التاريخي"

    def predict(self, field_data: FieldData, crop_params: CropParameters) -> tuple[float, float]:
        """
        Predict yield based on historical trends
        التنبؤ بالإنتاج بناءً على الاتجاهات التاريخية

        Args:
            field_data: Field data - بيانات الحقل
            crop_params: Crop parameters - معلمات المحصول

        Returns:
            (predicted_yield, confidence) - (الإنتاج المتوقع، الثقة)
        """
        base_yield = crop_params.base_yield_kg_per_ha

        # Check for historical data - التحقق من البيانات التاريخية
        if not field_data.historical_yields or len(field_data.historical_yields) == 0:
            logger.warning(f"No historical data available for {field_data.field_id}")
            return base_yield, 0.4  # Return base yield with low confidence

        historical_yields = field_data.historical_yields

        # Calculate trend - حساب الاتجاه
        if len(historical_yields) >= 3:
            # Use weighted average with recent years weighted higher
            # استخدام متوسط مرجح مع وزن أعلى للسنوات الأخيرة
            weights = np.linspace(0.5, 1.5, len(historical_yields))
            weights = weights / weights.sum()
            predicted_yield = np.average(historical_yields, weights=weights)

            # Calculate trend direction - حساب اتجاه الاتجاه
            if len(historical_yields) >= 3:
                recent_avg = np.mean(historical_yields[-2:])
                older_avg = np.mean(historical_yields[:-2])

                if recent_avg > older_avg * 1.1:
                    # Improving trend - اتجاه تحسن
                    predicted_yield *= 1.05
                elif recent_avg < older_avg * 0.9:
                    # Declining trend - اتجاه تراجع
                    predicted_yield *= 0.95

            confidence = min(0.6 + 0.05 * len(historical_yields), 0.85)

        elif len(historical_yields) == 2:
            # Simple average with adjustment - متوسط بسيط مع تعديل
            predicted_yield = np.mean(historical_yields)
            confidence = 0.6

        else:
            # Single historical point - نقطة تاريخية واحدة
            predicted_yield = historical_yields[0]
            confidence = 0.5

        # Calculate variability penalty - حساب عقوبة التباين
        if len(historical_yields) >= 2:
            cv = np.std(historical_yields) / np.mean(historical_yields)  # Coefficient of variation
            if cv > 0.3:
                confidence *= 0.85  # High variability reduces confidence

        logger.info(
            f"Historical trend predictor: {predicted_yield:.1f} kg/ha (n={len(historical_yields)}, confidence: {confidence:.2f})"
        )

        return predicted_yield, confidence


class YieldEnsembleModel:
    """
    Ensemble model for yield prediction - نموذج مجموعة للتنبؤ بالإنتاج

    Combines multiple sub-models with weighted averaging for robust predictions.
    يجمع نماذج فرعية متعددة مع متوسط مرجح للتنبؤات القوية.
    """

    def __init__(
        self,
        ndvi_weight: float = 0.35,
        gdd_weight: float = 0.25,
        moisture_weight: float = 0.20,
        historical_weight: float = 0.20,
    ):
        """
        Initialize ensemble model
        تهيئة نموذج المجموعة

        Args:
            ndvi_weight: Weight for NDVI model - وزن نموذج NDVI
            gdd_weight: Weight for GDD model - وزن نموذج GDD
            moisture_weight: Weight for soil moisture model - وزن نموذج رطوبة التربة
            historical_weight: Weight for historical model - وزن النموذج التاريخي
        """
        # Normalize weights - تطبيع الأوزان
        total_weight = ndvi_weight + gdd_weight + moisture_weight + historical_weight
        self.weights = {
            "ndvi": ndvi_weight / total_weight,
            "gdd": gdd_weight / total_weight,
            "moisture": moisture_weight / total_weight,
            "historical": historical_weight / total_weight,
        }

        # Initialize sub-models - تهيئة النماذج الفرعية
        self.ndvi_predictor = NDVIBasedPredictor(weight=self.weights["ndvi"])
        self.gdd_predictor = GDDBasedPredictor(weight=self.weights["gdd"])
        self.moisture_predictor = SoilMoisturePredictor(weight=self.weights["moisture"])
        self.historical_predictor = HistoricalTrendPredictor(weight=self.weights["historical"])

        logger.info(f"YieldEnsembleModel initialized with weights: {self.weights}")

    def predict(self, field_data: FieldData) -> YieldPrediction:
        """
        Predict yield using ensemble of models
        التنبؤ بالإنتاج باستخدام مجموعة من النماذج

        Args:
            field_data: Field data input - بيانات الحقل المدخلة

        Returns:
            Comprehensive yield prediction - تنبؤ شامل بالإنتاج
        """
        # Get crop parameters - الحصول على معلمات المحصول
        crop_params = get_crop_parameters(field_data.crop_id)

        if crop_params is None:
            raise ValueError(f"Unknown crop: {field_data.crop_id}")

        logger.info(f"Predicting yield for field {field_data.field_id}, crop: {field_data.crop_id}")

        # Apply regional adjustment - تطبيق التعديل الإقليمي
        regional_adjustment = crop_params.regional_adjustments.get(field_data.region)
        if regional_adjustment:
            regional_multiplier = regional_adjustment.yield_multiplier
        else:
            regional_multiplier = 1.0
            logger.warning(f"No regional adjustment found for {field_data.region}, using 1.0")

        # Run sub-model predictions - تشغيل تنبؤات النماذج الفرعية
        predictions = {}
        confidences = {}

        # NDVI model - نموذج NDVI
        ndvi_yield, ndvi_conf = self.ndvi_predictor.predict(field_data, crop_params)
        predictions["ndvi"] = ndvi_yield
        confidences["ndvi"] = ndvi_conf

        # GDD model - نموذج GDD
        gdd_yield, gdd_conf = self.gdd_predictor.predict(field_data, crop_params)
        predictions["gdd"] = gdd_yield
        confidences["gdd"] = gdd_conf

        # Soil moisture model - نموذج رطوبة التربة
        moisture_yield, moisture_conf = self.moisture_predictor.predict(field_data, crop_params)
        predictions["moisture"] = moisture_yield
        confidences["moisture"] = moisture_conf

        # Historical model - النموذج التاريخي
        hist_yield, hist_conf = self.historical_predictor.predict(field_data, crop_params)
        predictions["historical"] = hist_yield
        confidences["historical"] = hist_conf

        # Calculate weighted ensemble prediction - حساب التنبؤ المرجح للمجموعة
        ensemble_yield = sum(
            predictions[model] * self.weights[model] * confidences[model] for model in predictions
        ) / sum(self.weights[model] * confidences[model] for model in predictions)

        # Apply regional multiplier - تطبيق المعامل الإقليمي
        ensemble_yield *= regional_multiplier

        # Apply soil quality adjustments - تطبيق تعديلات جودة التربة
        soil_factor = self._calculate_soil_factor(field_data, crop_params)
        ensemble_yield *= soil_factor

        # Apply disease impact - تطبيق تأثير الأمراض
        if field_data.disease_severity:
            disease_impact = 1.0 - (field_data.disease_severity * 0.4)  # Up to 40% yield loss
            ensemble_yield *= disease_impact

        # Calculate confidence metrics - حساب مقاييس الثقة
        confidence_metrics = self._calculate_confidence_metrics(
            field_data, predictions, confidences
        )

        # Identify limiting factors - تحديد العوامل المحددة
        limiting_factors = self._identify_limiting_factors(
            field_data, crop_params, predictions, ensemble_yield
        )

        # Generate recommendations - إنشاء التوصيات
        recommendations = self._generate_recommendations(field_data, crop_params, limiting_factors)

        # Determine growth stage - تحديد مرحلة النمو
        growth_stage = self._determine_growth_stage(field_data, crop_params)

        # Calculate days to harvest - حساب الأيام حتى الحصاد
        days_to_harvest = self._calculate_days_to_harvest(field_data, crop_params)

        # Calculate confidence interval - حساب فاصل الثقة
        confidence_interval = self._calculate_confidence_interval(
            ensemble_yield, confidence_metrics, predictions
        )

        # Calculate economic projections - حساب التوقعات الاقتصادية
        revenue_per_ha = ensemble_yield * crop_params.market_price_per_kg
        total_revenue = revenue_per_ha * field_data.area_hectares

        # Create prediction object - إنشاء كائن التنبؤ
        prediction = YieldPrediction(
            predicted_yield_kg_per_hectare=ensemble_yield,
            confidence_interval=confidence_interval,
            confidence=confidence_metrics.final_confidence,
            limiting_factors=limiting_factors,
            recommendations=recommendations,
            crop_id=field_data.crop_id,
            region=field_data.region,
            growth_stage=growth_stage,
            days_to_harvest=days_to_harvest,
            sub_model_predictions=predictions,
            confidence_metrics=confidence_metrics,
            estimated_revenue_per_ha=revenue_per_ha,
            estimated_total_revenue=total_revenue,
        )

        logger.info(
            f"Ensemble prediction complete: {ensemble_yield:.1f} kg/ha (confidence: {confidence_metrics.final_confidence:.2f})"
        )

        return prediction

    def _calculate_soil_factor(self, field_data: FieldData, crop_params: CropParameters) -> float:
        """
        Calculate soil quality adjustment factor
        حساب عامل تعديل جودة التربة
        """
        soil_factor = 1.0

        # pH adjustment - تعديل pH
        if field_data.soil_ph is not None:
            optimal_ph_min = crop_params.soil.ph_min
            optimal_ph_max = crop_params.soil.ph_max
            ph = field_data.soil_ph

            if optimal_ph_min <= ph <= optimal_ph_max:
                ph_factor = 1.0
            elif ph < optimal_ph_min:
                ph_factor = max(0.7, 1.0 - (optimal_ph_min - ph) * 0.1)
            else:
                ph_factor = max(0.7, 1.0 - (ph - optimal_ph_max) * 0.1)

            soil_factor *= ph_factor

        # EC (salinity) adjustment - تعديل EC (الملوحة)
        if field_data.soil_ec is not None:
            ec_tolerance = crop_params.soil.ec_tolerance
            ec = field_data.soil_ec

            if ec <= ec_tolerance:
                ec_factor = 1.0
            elif ec <= ec_tolerance * 1.5:
                ec_factor = 0.85
            else:
                ec_factor = max(0.5, 1.0 - (ec - ec_tolerance) * 0.1)

            soil_factor *= ec_factor

        # Nutrient score adjustment - تعديل درجة العناصر الغذائية
        if field_data.soil_nutrient_score is not None:
            soil_factor *= 0.7 + 0.3 * field_data.soil_nutrient_score

        return soil_factor

    def _calculate_confidence_metrics(
        self, field_data: FieldData, predictions: dict[str, float], confidences: dict[str, float]
    ) -> ConfidenceMetrics:
        """
        Calculate comprehensive confidence metrics
        حساب مقاييس الثقة الشاملة
        """
        # Data completeness score - درجة اكتمال البيانات
        data_completeness = self._data_completeness_score(field_data)

        # Model agreement score - درجة توافق النماذج
        model_agreement = self._model_agreement_score(predictions)

        # Historical accuracy adjustment - تعديل الدقة التاريخية
        historical_accuracy = self._historical_accuracy_adjustment(field_data)

        # Calculate final confidence - حساب الثقة النهائية
        # Weighted combination of metrics
        final_confidence = (
            0.4 * data_completeness + 0.3 * model_agreement + 0.3 * historical_accuracy
        )

        # Adjust based on individual model confidences - التعديل بناءً على ثقة النماذج الفردية
        avg_model_confidence = np.mean(list(confidences.values()))
        final_confidence = final_confidence * avg_model_confidence

        # Ensure confidence is between 0 and 1
        final_confidence = max(0.0, min(1.0, final_confidence))

        return ConfidenceMetrics(
            data_completeness=data_completeness,
            model_agreement=model_agreement,
            historical_accuracy=historical_accuracy,
            final_confidence=final_confidence,
            model_confidences=confidences,
        )

    def _data_completeness_score(self, field_data: FieldData) -> float:
        """
        Calculate data completeness score (0-1)
        حساب درجة اكتمال البيانات
        """
        # Check which data fields are available
        available_fields = 0
        total_fields = 0

        # Critical fields - الحقول الحرجة
        critical_fields = [
            field_data.ndvi_current is not None or field_data.ndvi_peak is not None,
            field_data.accumulated_gdd is not None or field_data.days_since_planting is not None,
            field_data.soil_moisture_current is not None
            or field_data.total_irrigation_mm is not None,
            field_data.planting_date is not None,
        ]
        available_fields += sum(critical_fields)
        total_fields += len(critical_fields)

        # Supplementary fields - الحقول التكميلية
        supplementary_fields = [
            field_data.soil_ph is not None,
            field_data.soil_ec is not None,
            field_data.soil_nutrient_score is not None,
            field_data.historical_yields is not None and len(field_data.historical_yields) > 0,
            field_data.ndvi_history is not None and len(field_data.ndvi_history) > 3,
        ]
        available_fields += sum(supplementary_fields) * 0.5
        total_fields += len(supplementary_fields) * 0.5

        completeness = available_fields / total_fields if total_fields > 0 else 0.5

        return completeness

    def _model_agreement_score(self, predictions: dict[str, float]) -> float:
        """
        Calculate model agreement score (0-1)
        حساب درجة توافق النماذج
        """
        if len(predictions) < 2:
            return 0.5

        values = list(predictions.values())
        mean_pred = np.mean(values)

        if mean_pred == 0:
            return 0.5

        # Calculate coefficient of variation - حساب معامل التباين
        cv = np.std(values) / mean_pred

        # Convert to agreement score (lower CV = higher agreement)
        # CV < 0.1: excellent agreement
        # CV > 0.5: poor agreement
        if cv < 0.1:
            agreement = 1.0
        elif cv < 0.2:
            agreement = 0.9
        elif cv < 0.3:
            agreement = 0.75
        elif cv < 0.5:
            agreement = 0.6
        else:
            agreement = max(0.4, 1.0 - cv)

        return agreement

    def _historical_accuracy_adjustment(self, field_data: FieldData) -> float:
        """
        Adjust confidence based on historical accuracy
        تعديل الثقة بناءً على الدقة التاريخية
        """
        # If we have historical data, we can assess past prediction accuracy
        # For now, use a heuristic based on data availability

        if field_data.historical_yields and len(field_data.historical_yields) >= 3:
            # More historical data = higher confidence in patterns
            return min(0.7 + 0.05 * len(field_data.historical_yields), 0.95)
        elif field_data.historical_yields and len(field_data.historical_yields) > 0:
            return 0.7
        else:
            return 0.6  # Default for new fields

    def _identify_limiting_factors(
        self,
        field_data: FieldData,
        crop_params: CropParameters,
        predictions: dict[str, float],
        ensemble_yield: float,
    ) -> list[dict[str, Any]]:
        """
        Identify factors limiting yield
        تحديد العوامل المحددة للإنتاج
        """
        limiting_factors = []
        base_yield = crop_params.base_yield_kg_per_ha

        # Check NDVI/plant health - التحقق من NDVI/صحة النبات
        if predictions["ndvi"] < base_yield * 0.7:
            severity = "high" if predictions["ndvi"] < base_yield * 0.5 else "medium"
            limiting_factors.append(
                {
                    "factor": LimitingFactor.POOR_PLANT_HEALTH.value,
                    "factor_ar": "صحة النبات منخفضة",
                    "severity": severity,
                    "impact_pct": ((base_yield - predictions["ndvi"]) / base_yield) * 100,
                    "description": "Vegetation index indicates poor plant vigor",
                    "description_ar": "مؤشر النباتات يشير إلى ضعف حيوية النبات",
                }
            )

        # Check water stress - التحقق من الإجهاد المائي
        if predictions["moisture"] < base_yield * 0.7:
            severity = "high" if predictions["moisture"] < base_yield * 0.5 else "medium"
            limiting_factors.append(
                {
                    "factor": LimitingFactor.WATER_STRESS.value,
                    "factor_ar": "إجهاد مائي",
                    "severity": severity,
                    "impact_pct": ((base_yield - predictions["moisture"]) / base_yield) * 100,
                    "description": "Insufficient water availability",
                    "description_ar": "عدم كفاية توفر المياه",
                }
            )

        # Check GDD/thermal stress - التحقق من GDD/الإجهاد الحراري
        if predictions["gdd"] < base_yield * 0.7:
            severity = "medium"
            limiting_factors.append(
                {
                    "factor": LimitingFactor.INADEQUATE_GDD.value,
                    "factor_ar": "نقص درجات الحرارة التراكمية",
                    "severity": severity,
                    "impact_pct": ((base_yield - predictions["gdd"]) / base_yield) * 100,
                    "description": "Suboptimal thermal time accumulation",
                    "description_ar": "تراكم وقت حراري دون المستوى الأمثل",
                }
            )

        # Check heat stress - التحقق من الإجهاد الحراري
        if field_data.current_temperature:
            temp = field_data.current_temperature
            optimal_max = crop_params.growth.optimal_temp_max

            if temp > optimal_max + 5:
                limiting_factors.append(
                    {
                        "factor": LimitingFactor.HEAT_STRESS.value,
                        "factor_ar": "إجهاد حراري",
                        "severity": "high",
                        "impact_pct": min((temp - optimal_max) * 2, 20),
                        "description": f"Temperature {temp}°C exceeds optimal range",
                        "description_ar": f"درجة الحرارة {temp}°م تتجاوز النطاق الأمثل",
                    }
                )

        # Check soil pH - التحقق من pH التربة
        if field_data.soil_ph:
            ph = field_data.soil_ph
            ph_min = crop_params.soil.ph_min
            ph_max = crop_params.soil.ph_max

            if ph < ph_min - 0.5 or ph > ph_max + 0.5:
                limiting_factors.append(
                    {
                        "factor": LimitingFactor.SOIL_pH_IMBALANCE.value,
                        "factor_ar": "اختلال pH التربة",
                        "severity": "medium",
                        "impact_pct": 15,
                        "description": f"Soil pH {ph:.1f} outside optimal range",
                        "description_ar": f"pH التربة {ph:.1f} خارج النطاق الأمثل",
                    }
                )

        # Check soil salinity - التحقق من ملوحة التربة
        if field_data.soil_ec:
            ec = field_data.soil_ec
            ec_tolerance = crop_params.soil.ec_tolerance

            if ec > ec_tolerance * 1.2:
                limiting_factors.append(
                    {
                        "factor": LimitingFactor.SOIL_SALINITY.value,
                        "factor_ar": "ملوحة التربة",
                        "severity": "high" if ec > ec_tolerance * 1.5 else "medium",
                        "impact_pct": min((ec - ec_tolerance) * 10, 30),
                        "description": f"Soil EC {ec:.1f} dS/m exceeds tolerance",
                        "description_ar": f"EC التربة {ec:.1f} dS/m يتجاوز التحمل",
                    }
                )

        # Check disease pressure - التحقق من ضغط الأمراض
        if field_data.disease_severity and field_data.disease_severity > 0.3:
            limiting_factors.append(
                {
                    "factor": LimitingFactor.DISEASE_PRESSURE.value,
                    "factor_ar": "ضغط الأمراض",
                    "severity": "high" if field_data.disease_severity > 0.6 else "medium",
                    "impact_pct": field_data.disease_severity * 40,
                    "description": "Significant disease presence detected",
                    "description_ar": "اكتشاف وجود كبير للأمراض",
                }
            )

        # Sort by impact - الترتيب حسب التأثير
        limiting_factors.sort(key=lambda x: x["impact_pct"], reverse=True)

        return limiting_factors

    def _generate_recommendations(
        self,
        field_data: FieldData,
        crop_params: CropParameters,
        limiting_factors: list[dict[str, Any]],
    ) -> list[dict[str, str]]:
        """
        Generate actionable recommendations
        إنشاء توصيات قابلة للتنفيذ
        """
        recommendations = []

        # Address limiting factors - معالجة العوامل المحددة
        for factor in limiting_factors[:3]:  # Top 3 limiting factors
            factor_type = factor["factor"]

            if factor_type == LimitingFactor.WATER_STRESS.value:
                recommendations.append(
                    {
                        "priority": "high",
                        "action": "Increase irrigation frequency",
                        "action_ar": "زيادة تكرار الري",
                        "details": f"Apply {int(crop_params.growth.water_requirement_mm * 0.1)} mm per irrigation event",
                        "details_ar": f"تطبيق {int(crop_params.growth.water_requirement_mm * 0.1)} مم لكل حدث ري",
                        "expected_impact": f"Potential yield increase: {factor['impact_pct'] * 0.6:.0f}%",
                    }
                )

            elif factor_type == LimitingFactor.POOR_PLANT_HEALTH.value:
                recommendations.append(
                    {
                        "priority": "high",
                        "action": "Apply foliar fertilizer and inspect for pests/diseases",
                        "action_ar": "تطبيق سماد ورقي وفحص الآفات/الأمراض",
                        "details": "NPK foliar spray + pest scouting",
                        "details_ar": "رش NPK الورقي + استطلاع الآفات",
                        "expected_impact": f"Potential yield increase: {factor['impact_pct'] * 0.5:.0f}%",
                    }
                )

            elif factor_type == LimitingFactor.SOIL_SALINITY.value:
                recommendations.append(
                    {
                        "priority": "medium",
                        "action": "Implement leaching irrigation",
                        "action_ar": "تنفيذ ري الغسيل",
                        "details": "Apply 15-20% extra irrigation to leach salts",
                        "details_ar": "تطبيق 15-20% ري إضافي لغسل الأملاح",
                        "expected_impact": "Gradual yield recovery over season",
                    }
                )

            elif factor_type == LimitingFactor.SOIL_pH_IMBALANCE.value:
                if field_data.soil_ph and field_data.soil_ph < crop_params.soil.ph_min:
                    recommendations.append(
                        {
                            "priority": "medium",
                            "action": "Apply lime to raise soil pH",
                            "action_ar": "تطبيق الجير لرفع pH التربة",
                            "details": f"Target pH: {crop_params.soil.ph_min:.1f}-{crop_params.soil.ph_max:.1f}",
                            "details_ar": f"pH المستهدف: {crop_params.soil.ph_min:.1f}-{crop_params.soil.ph_max:.1f}",
                            "expected_impact": "Long-term yield improvement",
                        }
                    )
                else:
                    recommendations.append(
                        {
                            "priority": "medium",
                            "action": "Apply sulfur to lower soil pH",
                            "action_ar": "تطبيق الكبريت لخفض pH التربة",
                            "details": f"Target pH: {crop_params.soil.ph_min:.1f}-{crop_params.soil.ph_max:.1f}",
                            "details_ar": f"pH المستهدف: {crop_params.soil.ph_min:.1f}-{crop_params.soil.ph_max:.1f}",
                            "expected_impact": "Long-term yield improvement",
                        }
                    )

            elif factor_type == LimitingFactor.DISEASE_PRESSURE.value:
                recommendations.append(
                    {
                        "priority": "high",
                        "action": "Apply appropriate fungicide/pesticide",
                        "action_ar": "تطبيق مبيد فطري/آفات مناسب",
                        "details": f"Treat based on identified diseases for {crop_params.name_ar}",
                        "details_ar": f"العلاج بناءً على الأمراض المحددة لـ {crop_params.name_ar}",
                        "expected_impact": f"Prevent further yield loss of {factor['impact_pct']:.0f}%",
                    }
                )

        # General recommendations - التوصيات العامة
        if not limiting_factors:
            recommendations.append(
                {
                    "priority": "low",
                    "action": "Maintain current management practices",
                    "action_ar": "الحفاظ على ممارسات الإدارة الحالية",
                    "details": "Crop is performing well, continue monitoring",
                    "details_ar": "المحصول يؤدي بشكل جيد، استمر في المراقبة",
                    "expected_impact": "Sustain current yield levels",
                }
            )

        # Harvest timing recommendation - توصية توقيت الحصاد
        days_to_harvest = self._calculate_days_to_harvest(field_data, crop_params)
        if days_to_harvest <= 14:
            recommendations.append(
                {
                    "priority": "high",
                    "action": f"Prepare for harvest in {days_to_harvest} days",
                    "action_ar": f"استعد للحصاد في غضون {days_to_harvest} يوم",
                    "details": "Arrange equipment and labor",
                    "details_ar": "ترتيب المعدات والعمالة",
                    "expected_impact": "Optimal harvest timing",
                }
            )

        return recommendations

    def _determine_growth_stage(
        self, field_data: FieldData, crop_params: CropParameters
    ) -> GrowthStage:
        """
        Determine current growth stage
        تحديد مرحلة النمو الحالية
        """
        if field_data.current_growth_stage:
            return field_data.current_growth_stage

        # Estimate based on days since planting - تقدير بناءً على الأيام منذ الزراعة
        if field_data.days_since_planting is not None:
            days = field_data.days_since_planting
            total_days = crop_params.growth.growth_days

            progress = days / total_days

            if progress < 0.15:
                return GrowthStage.GERMINATION
            elif progress < 0.4:
                return GrowthStage.VEGETATIVE
            elif progress < 0.6:
                return GrowthStage.FLOWERING
            elif progress < 0.8:
                return GrowthStage.FRUIT_SET
            elif progress < 0.95:
                return GrowthStage.MATURATION
            else:
                return GrowthStage.HARVEST_READY

        # Default to vegetative if unknown - الافتراضي إلى الخضري إذا كان غير معروف
        return GrowthStage.VEGETATIVE

    def _calculate_days_to_harvest(self, field_data: FieldData, crop_params: CropParameters) -> int:
        """
        Calculate days remaining until harvest
        حساب الأيام المتبقية حتى الحصاد
        """
        total_days = crop_params.growth.growth_days

        if field_data.days_since_planting is not None:
            days_remaining = max(0, total_days - field_data.days_since_planting)
            return days_remaining

        # Estimate based on GDD if available - تقدير بناءً على GDD إذا كان متاحًا
        if field_data.accumulated_gdd is not None:
            required_gdd = crop_params.growth.gdd_required
            gdd_remaining = max(0, required_gdd - field_data.accumulated_gdd)

            # Estimate days based on average daily GDD - تقدير الأيام بناءً على متوسط GDD اليومي
            if field_data.current_temperature:
                avg_daily_gdd = max(
                    field_data.current_temperature - crop_params.growth.base_temp, 0
                )
                if avg_daily_gdd > 0:
                    days_remaining = int(gdd_remaining / avg_daily_gdd)
                    return days_remaining

        # Default estimate - التقدير الافتراضي
        return total_days // 2

    def _calculate_confidence_interval(
        self,
        ensemble_yield: float,
        confidence_metrics: ConfidenceMetrics,
        predictions: dict[str, float],
    ) -> dict[str, float]:
        """
        Calculate confidence interval (low, mid, high)
        حساب فاصل الثقة (منخفض، متوسط، عالي)
        """
        # Calculate variance from sub-model predictions - حساب التباين من تنبؤات النماذج الفرعية
        values = list(predictions.values())
        std_dev = np.std(values)

        # Adjust interval width based on confidence - تعديل عرض الفاصل بناءً على الثقة
        confidence = confidence_metrics.final_confidence
        interval_multiplier = 2.0 - confidence  # Lower confidence = wider interval

        # Calculate interval - حساب الفاصل
        margin = std_dev * interval_multiplier

        return {
            "low": max(0, ensemble_yield - margin),
            "mid": ensemble_yield,
            "high": ensemble_yield + margin,
        }

    def get_feature_importance(self) -> dict[str, float]:
        """
        Get feature importance (model weights)
        الحصول على أهمية الميزات (أوزان النماذج)

        Returns:
            Dictionary of model weights - قاموس أوزان النماذج
        """
        return {
            "NDVI (Plant Health)": self.weights["ndvi"],
            "GDD (Thermal Time)": self.weights["gdd"],
            "Soil Moisture (Water)": self.weights["moisture"],
            "Historical Trends": self.weights["historical"],
        }

    def explain_prediction(self, prediction: YieldPrediction) -> dict[str, Any]:
        """
        Explain a prediction with detailed breakdown
        شرح التنبؤ مع تفصيل مفصل

        Args:
            prediction: Yield prediction to explain - تنبؤ الإنتاج للشرح

        Returns:
            Detailed explanation - الشرح المفصل
        """
        explanation = {
            "summary": {
                "predicted_yield_kg_ha": prediction.predicted_yield_kg_per_hectare,
                "confidence": prediction.confidence,
                "crop": prediction.crop_id,
                "region": prediction.region.value,
                "growth_stage": prediction.growth_stage.value,
            },
            "sub_models": {"contributions": {}, "predictions": prediction.sub_model_predictions},
            "confidence_breakdown": {
                "data_completeness": prediction.confidence_metrics.data_completeness,
                "model_agreement": prediction.confidence_metrics.model_agreement,
                "historical_accuracy": prediction.confidence_metrics.historical_accuracy,
                "final_confidence": prediction.confidence_metrics.final_confidence,
            },
            "limiting_factors": prediction.limiting_factors,
            "recommendations": prediction.recommendations,
            "confidence_interval": prediction.confidence_interval,
            "economic_projection": {
                "revenue_per_hectare": prediction.estimated_revenue_per_ha,
                "total_revenue": prediction.estimated_total_revenue,
            },
        }

        # Calculate each model's contribution to final prediction
        # حساب مساهمة كل نموذج في التنبؤ النهائي
        for model_name, weight in self.weights.items():
            if model_name in prediction.sub_model_predictions:
                pred_value = prediction.sub_model_predictions[model_name]
                confidence = prediction.confidence_metrics.model_confidences.get(model_name, 0.5)
                contribution = pred_value * weight * confidence
                explanation["sub_models"]["contributions"][model_name] = {
                    "weight": weight,
                    "prediction": pred_value,
                    "confidence": confidence,
                    "contribution": contribution,
                }

        return explanation
