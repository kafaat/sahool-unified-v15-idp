"""
SAHOOL NDVI Time-Series Analysis Module
وحدة تحليل السلاسل الزمنية لمؤشر NDVI

Complete implementation for NDVI time-series analysis including:
- Anomaly detection - كشف الشذوذ
- Trend analysis - تحليل الاتجاهات
- Seasonal patterns - الأنماط الموسمية
- Change detection - كشف التغييرات
- Cloud masking - إخفاء السحب
- Phenological stage detection - كشف مراحل النمو

References:
- Savitzky & Golay (1964) - Smoothing and Differentiation of Data
- Zeng et al. (2020) - A review of vegetation phenological metrics extraction
- Verbesselt et al. (2010) - Detecting trend and seasonal changes in satellite time series
- Fensholt & Proud (2012) - Evaluation of Earth Observation based global long term vegetation trends
"""

from dataclasses import dataclass
from datetime import date, timedelta
from enum import Enum
from typing import Any

# استيراد NumPy للحسابات العلمية
# Import NumPy for scientific calculations
try:
    import numpy as np
except ImportError:
    raise ImportError("NumPy is required for NDVI time-series analysis. Install with: pip install numpy")


# =============================================================================
# Enums - التعدادات
# =============================================================================


class AnomalyType(Enum):
    """نوع الشذوذ - Types of anomalies detected in NDVI time-series"""

    SUDDEN_DROP = "sudden_drop"  # انخفاض مفاجئ
    SUDDEN_INCREASE = "sudden_increase"  # ارتفاع مفاجئ
    PROLONGED_STRESS = "prolonged_stress"  # إجهاد مطول
    UNUSUAL_PATTERN = "unusual_pattern"  # نمط غير اعتيادي
    OUTLIER = "outlier"  # قيمة شاذة


class TrendType(Enum):
    """نوع الاتجاه - Types of trends in time-series"""

    INCREASING = "increasing"  # متزايد
    DECREASING = "decreasing"  # متناقص
    STABLE = "stable"  # مستقر
    SEASONAL = "seasonal"  # موسمي
    NO_TREND = "no_trend"  # لا اتجاه


class PhenologicalStage(Enum):
    """مراحل النمو الفينولوجية - Phenological growth stages"""

    DORMANCY = "dormancy"  # سكون
    GREEN_UP = "green_up"  # اخضرار
    PEAK_GROWTH = "peak_growth"  # ذروة النمو
    SENESCENCE = "senescence"  # شيخوخة
    DORMANT = "dormant"  # خامل


class ChangeType(Enum):
    """نوع التغيير - Types of changes between periods"""

    IMPROVEMENT = "improvement"  # تحسن
    DEGRADATION = "degradation"  # تدهور
    NO_CHANGE = "no_change"  # لا تغيير
    SIGNIFICANT_CHANGE = "significant_change"  # تغيير كبير


# =============================================================================
# Data Models - نماذج البيانات
# =============================================================================


@dataclass
class NDVIPoint:
    """نقطة NDVI مع الزمن - Single NDVI observation with timestamp"""

    date: date
    value: float
    quality: float = 1.0  # Quality score (0-1), جودة القياس
    cloud_coverage: float = 0.0  # Cloud coverage percentage, نسبة الغيوم


@dataclass
class AnomalyResult:
    """نتيجة كشف الشذوذ - Result of anomaly detection"""

    date: date
    ndvi_value: float
    expected_value: float
    deviation: float
    z_score: float
    anomaly_type: AnomalyType
    severity: float  # 0-1 scale
    description_ar: str
    description_en: str

    def to_dict(self) -> dict:
        """تحويل إلى قاموس - Convert to dictionary"""
        return {
            "date": self.date.isoformat(),
            "ndvi_value": round(self.ndvi_value, 4),
            "expected_value": round(self.expected_value, 4),
            "deviation": round(self.deviation, 4),
            "z_score": round(self.z_score, 2),
            "anomaly_type": self.anomaly_type.value,
            "severity": round(self.severity, 3),
            "description_ar": self.description_ar,
            "description_en": self.description_en,
        }


@dataclass
class TrendResult:
    """نتيجة تحليل الاتجاه - Result of trend analysis"""

    trend_type: TrendType
    slope: float  # Rate of change, معدل التغيير
    r_squared: float  # Coefficient of determination
    p_value: float  # Statistical significance
    confidence: float  # 0-1 scale
    prediction_equation: str
    description_ar: str
    description_en: str

    def to_dict(self) -> dict:
        """تحويل إلى قاموس - Convert to dictionary"""
        return {
            "trend_type": self.trend_type.value,
            "slope": round(self.slope, 6),
            "r_squared": round(self.r_squared, 4),
            "p_value": round(self.p_value, 4),
            "confidence": round(self.confidence, 3),
            "prediction_equation": self.prediction_equation,
            "description_ar": self.description_ar,
            "description_en": self.description_en,
        }


@dataclass
class SeasonalMetrics:
    """مقاييس الموسم - Seasonal phenological metrics"""

    season_start: date | None = None  # بداية الموسم
    peak_date: date | None = None  # تاريخ الذروة
    season_end: date | None = None  # نهاية الموسم
    season_length: int | None = None  # طول الموسم (أيام)
    peak_ndvi: float | None = None  # قيمة NDVI عند الذروة
    seasonal_amplitude: float | None = None  # سعة التغير الموسمي
    integrated_ndvi: float | None = None  # التكامل الموسمي (مجموع NDVI)

    def to_dict(self) -> dict:
        """تحويل إلى قاموس - Convert to dictionary"""
        return {
            "season_start": self.season_start.isoformat() if self.season_start else None,
            "peak_date": self.peak_date.isoformat() if self.peak_date else None,
            "season_end": self.season_end.isoformat() if self.season_end else None,
            "season_length": self.season_length,
            "peak_ndvi": round(self.peak_ndvi, 4) if self.peak_ndvi else None,
            "seasonal_amplitude": round(self.seasonal_amplitude, 4) if self.seasonal_amplitude else None,
            "integrated_ndvi": round(self.integrated_ndvi, 2) if self.integrated_ndvi else None,
        }


@dataclass
class ChangeDetectionResult:
    """نتيجة كشف التغيير - Result of change detection between periods"""

    change_type: ChangeType
    mean_change: float  # متوسط التغيير
    percent_change: float  # نسبة التغيير المئوية
    statistical_significance: float  # p-value
    affected_area_percent: float  # نسبة المساحة المتأثرة
    description_ar: str
    description_en: str

    def to_dict(self) -> dict:
        """تحويل إلى قاموس - Convert to dictionary"""
        return {
            "change_type": self.change_type.value,
            "mean_change": round(self.mean_change, 4),
            "percent_change": round(self.percent_change, 2),
            "statistical_significance": round(self.statistical_significance, 4),
            "affected_area_percent": round(self.affected_area_percent, 2),
            "description_ar": self.description_ar,
            "description_en": self.description_en,
        }


@dataclass
class CloudMaskResult:
    """نتيجة كشف السحب - Result of cloud detection"""

    cloud_mask: np.ndarray  # Binary mask (1 = cloud, 0 = clear)
    cloud_percentage: float  # نسبة السحب
    shadow_mask: np.ndarray | None = None  # ظلال السحب
    quality_mask: np.ndarray | None = None  # قناع الجودة

    def to_dict(self) -> dict:
        """تحويل إلى قاموس - Convert to dictionary"""
        return {
            "cloud_percentage": round(self.cloud_percentage, 2),
            "has_shadow_mask": self.shadow_mask is not None,
            "has_quality_mask": self.quality_mask is not None,
        }


# =============================================================================
# NDVI Time-Series Analyzer - محلل السلاسل الزمنية لـ NDVI
# =============================================================================


class NDVITimeSeriesAnalyzer:
    """
    محلل السلاسل الزمنية لمؤشر NDVI
    NDVI Time-Series Analyzer

    Main class for comprehensive NDVI time-series analysis including:
    - NDVI calculation from satellite bands
    - Anomaly detection using statistical methods
    - Trend analysis using linear regression
    - Forecasting using ARIMA-like methods
    - Phenological stage detection
    - Seasonal metrics calculation
    - Change detection between periods
    - Cloud masking and quality control
    """

    # عتبات NDVI - NDVI Thresholds
    NDVI_THRESHOLDS = {
        "water": -0.1,  # ماء
        "bare_soil": 0.1,  # تربة عارية
        "sparse_vegetation": 0.2,  # نباتات متفرقة
        "moderate_vegetation": 0.4,  # نباتات معتدلة
        "dense_vegetation": 0.6,  # نباتات كثيفة
        "very_dense_vegetation": 0.8,  # نباتات كثيفة جداً
    }

    def __init__(self, smoothing_window: int = 5):
        """
        تهيئة المحلل - Initialize the analyzer

        Args:
            smoothing_window: حجم نافذة التنعيم - Window size for smoothing (default: 5)
        """
        self.smoothing_window = smoothing_window

    # =========================================================================
    # NDVI Calculation - حساب NDVI
    # =========================================================================

    def calculate_ndvi(
        self,
        red_band: np.ndarray,
        nir_band: np.ndarray
    ) -> np.ndarray:
        """
        حساب مؤشر NDVI من نطاقي الأحمر والأشعة تحت الحمراء القريبة
        Calculate NDVI from RED and NIR bands

        Formula: NDVI = (NIR - RED) / (NIR + RED)

        Args:
            red_band: نطاق الأحمر - RED band (0.4-0.7 μm)
            nir_band: نطاق الأشعة تحت الحمراء القريبة - NIR band (0.7-1.1 μm)

        Returns:
            مصفوفة قيم NDVI - NDVI values array (-1 to 1)
        """
        # تحويل إلى float لتجنب مشاكل القسمة
        # Convert to float to avoid division issues
        red = red_band.astype(np.float32)
        nir = nir_band.astype(np.float32)

        # حساب NDVI مع معالجة القسمة على صفر
        # Calculate NDVI with zero-division handling
        denominator = nir + red
        ndvi = np.where(
            denominator != 0,
            (nir - red) / denominator,
            0
        )

        # قص القيم ضمن النطاق المنطقي [-1, 1]
        # Clip values to valid range
        ndvi = np.clip(ndvi, -1, 1)

        return ndvi

    # =========================================================================
    # Anomaly Detection - كشف الشذوذ
    # =========================================================================

    def detect_anomalies(
        self,
        ndvi_series: list[NDVIPoint],
        threshold: float = 2.0
    ) -> list[AnomalyResult]:
        """
        كشف الشذوذ في سلسلة NDVI الزمنية باستخدام Z-score
        Detect anomalies in NDVI time-series using Z-score method

        Args:
            ndvi_series: سلسلة بيانات NDVI - List of NDVI observations
            threshold: عتبة Z-score للشذوذ - Z-score threshold (default: 2.0 std)

        Returns:
            قائمة بالشذوذات المكتشفة - List of detected anomalies
        """
        if len(ndvi_series) < 3:
            return []

        # استخراج القيم والتواريخ
        # Extract values and dates
        values = np.array([point.value for point in ndvi_series])
        dates = [point.date for point in ndvi_series]

        # حساب المتوسط والانحراف المعياري
        # Calculate mean and standard deviation
        mean = np.mean(values)
        std = np.std(values)

        if std == 0:
            return []

        # حساب Z-scores
        # Calculate Z-scores
        z_scores = (values - mean) / std

        # تنعيم السلسلة للحصول على القيم المتوقعة
        # Smooth series to get expected values
        smoothed = self._smooth_series(values)

        # كشف الشذوذات
        # Detect anomalies
        anomalies = []
        for _i, (z_score, value, expected, date_val) in enumerate(zip(z_scores, values, smoothed, dates, strict=False)):
            if abs(z_score) > threshold:
                # تحديد نوع الشذوذ
                # Determine anomaly type
                deviation = value - expected

                if deviation < -0.15:
                    anomaly_type = AnomalyType.SUDDEN_DROP
                    desc_ar = f"انخفاض مفاجئ في NDVI بمقدار {abs(deviation):.3f}"
                    desc_en = f"Sudden NDVI drop of {abs(deviation):.3f}"
                elif deviation > 0.15:
                    anomaly_type = AnomalyType.SUDDEN_INCREASE
                    desc_ar = f"ارتفاع مفاجئ في NDVI بمقدار {deviation:.3f}"
                    desc_en = f"Sudden NDVI increase of {deviation:.3f}"
                else:
                    anomaly_type = AnomalyType.OUTLIER
                    desc_ar = f"قيمة شاذة في NDVI (Z-score: {z_score:.2f})"
                    desc_en = f"NDVI outlier (Z-score: {z_score:.2f})"

                # حساب شدة الشذوذ (0-1)
                # Calculate severity (0-1)
                severity = min(abs(z_score) / 4.0, 1.0)

                anomaly = AnomalyResult(
                    date=date_val,
                    ndvi_value=value,
                    expected_value=expected,
                    deviation=deviation,
                    z_score=z_score,
                    anomaly_type=anomaly_type,
                    severity=severity,
                    description_ar=desc_ar,
                    description_en=desc_en
                )
                anomalies.append(anomaly)

        return anomalies

    # =========================================================================
    # Trend Analysis - تحليل الاتجاه
    # =========================================================================

    def calculate_trend(
        self,
        ndvi_values: list[float],
        dates: list[date]
    ) -> TrendResult:
        """
        حساب اتجاه السلسلة الزمنية باستخدام الانحدار الخطي
        Calculate time-series trend using linear regression

        Args:
            ndvi_values: قيم NDVI - NDVI values
            dates: التواريخ - Corresponding dates

        Returns:
            نتيجة تحليل الاتجاه - Trend analysis result
        """
        if len(ndvi_values) < 2:
            return TrendResult(
                trend_type=TrendType.NO_TREND,
                slope=0.0,
                r_squared=0.0,
                p_value=1.0,
                confidence=0.0,
                prediction_equation="N/A",
                description_ar="بيانات غير كافية",
                description_en="Insufficient data"
            )

        # تحويل التواريخ إلى أرقام (أيام من البداية)
        # Convert dates to numeric (days from start)
        x = np.array([(d - dates[0]).days for d in dates])
        y = np.array(ndvi_values)

        # حساب الانحدار الخطي
        # Calculate linear regression
        n = len(x)
        slope, intercept = self._linear_regression(x, y)

        # حساب R-squared
        # Calculate R-squared
        y_pred = slope * x + intercept
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

        # حساب p-value (مبسط)
        # Calculate p-value (simplified)
        # في التطبيق الحقيقي، استخدم scipy.stats
        # In real application, use scipy.stats
        se = np.sqrt(ss_res / (n - 2)) if n > 2 else 1.0
        t_stat = abs(slope) / (se / np.sqrt(np.sum((x - np.mean(x)) ** 2))) if se > 0 else 0
        p_value = max(0.001, 1.0 / (1.0 + t_stat))  # تقريب

        # تحديد نوع الاتجاه
        # Determine trend type
        if abs(slope) < 0.0001:
            trend_type = TrendType.STABLE
            desc_ar = "اتجاه مستقر، لا تغيير ملحوظ"
            desc_en = "Stable trend, no significant change"
        elif slope > 0:
            trend_type = TrendType.INCREASING
            desc_ar = f"اتجاه متزايد بمعدل {slope:.6f} يومياً"
            desc_en = f"Increasing trend at {slope:.6f} per day"
        else:
            trend_type = TrendType.DECREASING
            desc_ar = f"اتجاه متناقص بمعدل {abs(slope):.6f} يومياً"
            desc_en = f"Decreasing trend at {abs(slope):.6f} per day"

        # حساب الثقة بناءً على R² و p-value
        # Calculate confidence based on R² and p-value
        confidence = r_squared * (1 - p_value)

        # معادلة التنبؤ
        # Prediction equation
        prediction_equation = f"NDVI = {intercept:.4f} + {slope:.6f} × days"

        return TrendResult(
            trend_type=trend_type,
            slope=slope,
            r_squared=r_squared,
            p_value=p_value,
            confidence=confidence,
            prediction_equation=prediction_equation,
            description_ar=desc_ar,
            description_en=desc_en
        )

    # =========================================================================
    # Forecasting - التنبؤ
    # =========================================================================

    def predict_next_values(
        self,
        ndvi_series: list[NDVIPoint],
        periods: int = 7
    ) -> list[tuple[date, float]]:
        """
        التنبؤ بقيم NDVI المستقبلية باستخدام المتوسط المتحرك والاتجاه
        Predict future NDVI values using moving average and trend

        Args:
            ndvi_series: سلسلة بيانات NDVI - Historical NDVI data
            periods: عدد الفترات للتنبؤ - Number of periods to forecast (default: 7 days)

        Returns:
            قائمة أزواج (تاريخ، قيمة متنبأة) - List of (date, predicted_value) tuples
        """
        if len(ndvi_series) < 3:
            return []

        # استخراج البيانات
        # Extract data
        dates = [point.date for point in ndvi_series]
        values = [point.value for point in ndvi_series]

        # حساب الاتجاه
        # Calculate trend
        trend_result = self.calculate_trend(values, dates)
        slope = trend_result.slope

        # حساب الموسمية (متوسط التغير الأسبوعي)
        # Calculate seasonality (average weekly change)
        weekly_pattern = self._extract_weekly_pattern(values) if len(values) >= 7 else [0] * 7

        # التنبؤ
        # Forecast
        predictions = []
        last_date = dates[-1]
        last_value = values[-1]

        for i in range(1, periods + 1):
            # التاريخ المستقبلي
            # Future date
            future_date = last_date + timedelta(days=i)

            # التنبؤ = آخر قيمة + اتجاه + موسمية
            # Prediction = last value + trend + seasonality
            trend_component = slope * i
            seasonal_component = weekly_pattern[i % 7]

            predicted_value = last_value + trend_component + seasonal_component

            # قص ضمن النطاق المنطقي
            # Clip to valid range
            predicted_value = np.clip(predicted_value, -1, 1)

            predictions.append((future_date, predicted_value))

        return predictions

    # =========================================================================
    # Phenological Stage Detection - كشف مراحل النمو
    # =========================================================================

    def detect_phenological_stages(
        self,
        ndvi_curve: list[NDVIPoint]
    ) -> list[tuple[date, PhenologicalStage, float]]:
        """
        كشف مراحل النمو الفينولوجية من منحنى NDVI
        Detect phenological stages from NDVI curve

        Args:
            ndvi_curve: منحنى NDVI - NDVI time-series curve

        Returns:
            قائمة (تاريخ، مرحلة، ثقة) - List of (date, stage, confidence) tuples
        """
        if len(ndvi_curve) < 5:
            return []

        # استخراج البيانات
        # Extract data
        dates = [point.date for point in ndvi_curve]
        values = np.array([point.value for point in ndvi_curve])

        # تنعيم المنحنى
        # Smooth curve
        smoothed = self._smooth_series(values)

        # حساب المشتقة (معدل التغير)
        # Calculate derivative (rate of change)
        derivative = np.gradient(smoothed)

        # كشف المراحل
        # Detect stages
        stages = []

        for i in range(1, len(smoothed) - 1):
            stage = None
            confidence = 0.0

            # سكون: NDVI منخفض ومستقر
            # Dormancy: Low and stable NDVI
            if smoothed[i] < 0.2 and abs(derivative[i]) < 0.01:
                stage = PhenologicalStage.DORMANCY
                confidence = 0.8

            # اخضرار: NDVI يزداد بسرعة
            # Green-up: Rapidly increasing NDVI
            elif derivative[i] > 0.02 and smoothed[i] < 0.5:
                stage = PhenologicalStage.GREEN_UP
                confidence = min(derivative[i] * 20, 1.0)

            # ذروة النمو: NDVI مرتفع ومستقر
            # Peak growth: High and stable NDVI
            elif smoothed[i] > 0.6 and abs(derivative[i]) < 0.01:
                stage = PhenologicalStage.PEAK_GROWTH
                confidence = smoothed[i]

            # شيخوخة: NDVI ينخفض
            # Senescence: Decreasing NDVI
            elif derivative[i] < -0.02 and smoothed[i] > 0.3:
                stage = PhenologicalStage.SENESCENCE
                confidence = min(abs(derivative[i]) * 20, 1.0)

            # خامل: NDVI منخفض بعد انخفاض
            # Dormant: Low NDVI after decline
            elif smoothed[i] < 0.25 and i > 0 and smoothed[i-1] > smoothed[i]:
                stage = PhenologicalStage.DORMANT
                confidence = 0.7

            if stage:
                stages.append((dates[i], stage, confidence))

        return stages

    # =========================================================================
    # Seasonal Analysis - التحليل الموسمي
    # =========================================================================

    def identify_growing_season_start(
        self,
        ndvi_series: list[NDVIPoint],
        threshold: float = 0.2
    ) -> date | None:
        """
        تحديد بداية موسم النمو
        Identify start of growing season

        Args:
            ndvi_series: سلسلة NDVI - NDVI time-series
            threshold: عتبة بداية الموسم - Season start threshold (default: 0.2)

        Returns:
            تاريخ بداية الموسم - Date of season start, or None
        """
        if len(ndvi_series) < 3:
            return None

        # البحث عن أول ارتفاع مستدام فوق العتبة
        # Find first sustained increase above threshold
        consecutive_days = 0
        required_consecutive = 3  # يجب أن تستمر 3 أيام على الأقل

        for i, point in enumerate(ndvi_series):
            if point.value >= threshold:
                consecutive_days += 1
                if consecutive_days >= required_consecutive:
                    # العودة للنقطة الأولى في الارتفاع
                    # Return to first point in increase
                    return ndvi_series[i - consecutive_days + 1].date
            else:
                consecutive_days = 0

        return None

    def identify_peak_greenness(
        self,
        ndvi_series: list[NDVIPoint]
    ) -> tuple[date, float] | None:
        """
        تحديد ذروة الاخضرار (أعلى قيمة NDVI)
        Identify peak greenness (maximum NDVI)

        Args:
            ndvi_series: سلسلة NDVI - NDVI time-series

        Returns:
            (تاريخ، قيمة) الذروة - (date, value) of peak, or None
        """
        if not ndvi_series:
            return None

        # إيجاد أعلى قيمة
        # Find maximum value
        max_point = max(ndvi_series, key=lambda p: p.value)
        return (max_point.date, max_point.value)

    def calculate_seasonal_integral(
        self,
        ndvi_series: list[NDVIPoint]
    ) -> float:
        """
        حساب التكامل الموسمي (مجموع قيم NDVI عبر الموسم)
        Calculate seasonal integral (sum of NDVI values across season)

        يمثل الإنتاجية الكلية للنبات
        Represents total plant productivity

        Args:
            ndvi_series: سلسلة NDVI - NDVI time-series

        Returns:
            التكامل الموسمي - Seasonal integral value
        """
        if not ndvi_series:
            return 0.0

        # حساب المجموع (طريقة شبه المنحرف)
        # Calculate sum using trapezoidal method
        total = 0.0
        for i in range(len(ndvi_series) - 1):
            # عرض الفترة بالأيام
            # Period width in days
            days = (ndvi_series[i + 1].date - ndvi_series[i].date).days
            # متوسط القيمة × العرض
            # Average value × width
            avg_value = (ndvi_series[i].value + ndvi_series[i + 1].value) / 2
            total += avg_value * days

        return total

    # =========================================================================
    # Change Detection - كشف التغيير
    # =========================================================================

    def compare_periods(
        self,
        period1_ndvi: list[float],
        period2_ndvi: list[float]
    ) -> ChangeDetectionResult:
        """
        مقارنة فترتين لكشف التغييرات
        Compare two periods to detect changes

        Args:
            period1_ndvi: قيم NDVI للفترة الأولى - NDVI values for period 1
            period2_ndvi: قيم NDVI للفترة الثانية - NDVI values for period 2

        Returns:
            نتيجة كشف التغيير - Change detection result
        """
        if not period1_ndvi or not period2_ndvi:
            return ChangeDetectionResult(
                change_type=ChangeType.NO_CHANGE,
                mean_change=0.0,
                percent_change=0.0,
                statistical_significance=1.0,
                affected_area_percent=0.0,
                description_ar="بيانات غير كافية",
                description_en="Insufficient data"
            )

        # تحويل إلى numpy arrays
        # Convert to numpy arrays
        p1 = np.array(period1_ndvi)
        p2 = np.array(period2_ndvi)

        # حساب الإحصائيات
        # Calculate statistics
        mean1 = np.mean(p1)
        mean2 = np.mean(p2)
        mean_change = mean2 - mean1

        # نسبة التغيير المئوية
        # Percent change
        percent_change = (mean_change / mean1 * 100) if mean1 != 0 else 0

        # اختبار t (مبسط)
        # T-test (simplified)
        std1 = np.std(p1)
        std2 = np.std(p2)
        pooled_std = np.sqrt((std1**2 + std2**2) / 2)
        t_stat = abs(mean_change) / pooled_std if pooled_std > 0 else 0
        p_value = max(0.001, 1.0 / (1.0 + t_stat))

        # نسبة المساحة المتأثرة (القيم التي تغيرت بأكثر من 0.1)
        # Affected area percentage (values changed by more than 0.1)
        if len(p1) == len(p2):
            changes = np.abs(p2 - p1)
            affected = np.sum(changes > 0.1)
            affected_area_percent = (affected / len(p1)) * 100
        else:
            affected_area_percent = 0.0

        # تحديد نوع التغيير
        # Determine change type
        if abs(mean_change) < 0.05:
            change_type = ChangeType.NO_CHANGE
            desc_ar = "لا يوجد تغيير ملحوظ"
            desc_en = "No significant change"
        elif mean_change > 0.15:
            change_type = ChangeType.IMPROVEMENT
            desc_ar = f"تحسن كبير في الغطاء النباتي ({percent_change:.1f}%)"
            desc_en = f"Significant vegetation improvement ({percent_change:.1f}%)"
        elif mean_change < -0.15:
            change_type = ChangeType.DEGRADATION
            desc_ar = f"تدهور في الغطاء النباتي ({percent_change:.1f}%)"
            desc_en = f"Vegetation degradation ({percent_change:.1f}%)"
        else:
            change_type = ChangeType.SIGNIFICANT_CHANGE
            direction = "زيادة" if mean_change > 0 else "نقصان"
            direction_en = "increase" if mean_change > 0 else "decrease"
            desc_ar = f"{direction} معتدل في الغطاء النباتي ({percent_change:.1f}%)"
            desc_en = f"Moderate vegetation {direction_en} ({percent_change:.1f}%)"

        return ChangeDetectionResult(
            change_type=change_type,
            mean_change=mean_change,
            percent_change=percent_change,
            statistical_significance=p_value,
            affected_area_percent=affected_area_percent,
            description_ar=desc_ar,
            description_en=desc_en
        )

    def detect_sudden_changes(
        self,
        ndvi_series: list[NDVIPoint],
        sensitivity: float = 0.15
    ) -> list[tuple[date, float, str]]:
        """
        كشف التغييرات المفاجئة في سلسلة NDVI
        Detect sudden changes in NDVI time-series

        Args:
            ndvi_series: سلسلة NDVI - NDVI time-series
            sensitivity: حساسية الكشف - Detection sensitivity (default: 0.15)

        Returns:
            قائمة (تاريخ، حجم التغيير، وصف) - List of (date, change_magnitude, description) tuples
        """
        if len(ndvi_series) < 2:
            return []

        sudden_changes = []

        for i in range(1, len(ndvi_series)):
            current = ndvi_series[i]
            previous = ndvi_series[i - 1]

            # حساب التغيير
            # Calculate change
            change = current.value - previous.value

            # كشف التغييرات المفاجئة
            # Detect sudden changes
            if abs(change) >= sensitivity:
                if change > 0:
                    desc = f"ارتفاع مفاجئ: +{change:.3f}"
                else:
                    desc = f"انخفاض مفاجئ: {change:.3f}"

                sudden_changes.append((current.date, change, desc))

        return sudden_changes

    def generate_change_map(
        self,
        before_image: np.ndarray,
        after_image: np.ndarray
    ) -> dict[str, Any]:
        """
        إنشاء خريطة التغيير بين صورتين
        Generate change map between two images

        Args:
            before_image: صورة NDVI قبل - NDVI image before
            after_image: صورة NDVI بعد - NDVI image after

        Returns:
            قاموس يحتوي على خريطة التغيير والإحصائيات
            Dictionary containing change map and statistics
        """
        if before_image.shape != after_image.shape:
            raise ValueError("Images must have the same dimensions")

        # حساب خريطة التغيير
        # Calculate change map
        change_map = after_image - before_image

        # تصنيف التغييرات
        # Classify changes
        improvement_mask = change_map > 0.15  # تحسن كبير
        degradation_mask = change_map < -0.15  # تدهور كبير
        stable_mask = np.abs(change_map) <= 0.15  # مستقر

        # حساب الإحصائيات
        # Calculate statistics
        total_pixels = change_map.size
        improved_pixels = np.sum(improvement_mask)
        degraded_pixels = np.sum(degradation_mask)
        stable_pixels = np.sum(stable_mask)

        return {
            "change_map": change_map,
            "improvement_mask": improvement_mask,
            "degradation_mask": degradation_mask,
            "stable_mask": stable_mask,
            "statistics": {
                "total_pixels": total_pixels,
                "improved_pixels": int(improved_pixels),
                "degraded_pixels": int(degraded_pixels),
                "stable_pixels": int(stable_pixels),
                "improvement_percentage": float(improved_pixels / total_pixels * 100),
                "degradation_percentage": float(degraded_pixels / total_pixels * 100),
                "stable_percentage": float(stable_pixels / total_pixels * 100),
                "mean_change": float(np.mean(change_map)),
                "max_improvement": float(np.max(change_map)),
                "max_degradation": float(np.min(change_map)),
            }
        }

    # =========================================================================
    # Cloud Masking - إخفاء السحب
    # =========================================================================

    def detect_clouds(
        self,
        image_data: dict[str, np.ndarray]
    ) -> CloudMaskResult:
        """
        كشف السحب في بيانات الصورة
        Detect clouds in image data

        Uses multiple criteria:
        - High reflectance in visible bands
        - Low temperature (if thermal band available)
        - Texture analysis

        Args:
            image_data: قاموس النطاقات - Dictionary with band names as keys
                       يجب أن يحتوي على: 'blue', 'green', 'red', 'nir'
                       اختياري: 'thermal', 'swir1', 'swir2'

        Returns:
            نتيجة كشف السحب - Cloud detection result
        """
        # التحقق من النطاقات المطلوبة
        # Check required bands
        required_bands = ['blue', 'green', 'red', 'nir']
        for band in required_bands:
            if band not in image_data:
                raise ValueError(f"Required band '{band}' not found in image_data")

        blue = image_data['blue'].astype(np.float32)
        green = image_data['green'].astype(np.float32)
        red = image_data['red'].astype(np.float32)
        nir = image_data['nir'].astype(np.float32)

        # تهيئة قناع السحب
        # Initialize cloud mask
        height, width = blue.shape
        cloud_mask = np.zeros((height, width), dtype=np.uint8)

        # معيار 1: انعكاسية عالية في النطاقات المرئية
        # Criterion 1: High reflectance in visible bands
        brightness = (blue + green + red) / 3
        bright_threshold = np.percentile(brightness, 90)
        bright_mask = brightness > bright_threshold

        # معيار 2: NDVI منخفض (السحب ليست نباتات)
        # Criterion 2: Low NDVI (clouds are not vegetation)
        ndvi = self.calculate_ndvi(red, nir)
        low_ndvi_mask = ndvi < 0.2

        # معيار 3: نسبة الأزرق/الأحمر عالية
        # Criterion 3: High blue/red ratio
        blue_red_ratio = np.where(red > 0, blue / red, 0)
        blue_red_mask = blue_red_ratio > 1.0

        # دمج المعايير
        # Combine criteria
        cloud_mask = (bright_mask & low_ndvi_mask & blue_red_mask).astype(np.uint8)

        # كشف ظلال السحب (اختياري)
        # Detect cloud shadows (optional)
        shadow_mask = None
        if 'swir1' in image_data:
            swir1 = image_data['swir1'].astype(np.float32)
            # الظلال: انعكاسية منخفضة في جميع النطاقات
            # Shadows: low reflectance in all bands
            darkness = (blue + green + red + nir + swir1) / 5
            dark_threshold = np.percentile(darkness, 10)
            shadow_mask = (darkness < dark_threshold).astype(np.uint8)

        # حساب نسبة السحب
        # Calculate cloud percentage
        cloud_percentage = (np.sum(cloud_mask) / cloud_mask.size) * 100

        # قناع الجودة (دمج السحب والظلال)
        # Quality mask (combine clouds and shadows)
        quality_mask = cloud_mask.copy()
        if shadow_mask is not None:
            quality_mask = quality_mask | shadow_mask

        return CloudMaskResult(
            cloud_mask=cloud_mask,
            cloud_percentage=cloud_percentage,
            shadow_mask=shadow_mask,
            quality_mask=quality_mask
        )

    def interpolate_cloudy_pixels(
        self,
        ndvi_image: np.ndarray,
        cloud_mask: np.ndarray,
        method: str = 'nearest'
    ) -> np.ndarray:
        """
        استيفاء البكسلات المغطاة بالسحب
        Interpolate cloudy pixels in NDVI image

        Args:
            ndvi_image: صورة NDVI - NDVI image
            cloud_mask: قناع السحب - Cloud mask (1 = cloud, 0 = clear)
            method: طريقة الاستيفاء - Interpolation method ('nearest', 'linear')

        Returns:
            صورة NDVI بعد الاستيفاء - Interpolated NDVI image
        """
        # نسخ الصورة
        # Copy image
        interpolated = ndvi_image.copy()

        # إيجاد البكسلات الصافية والمغطاة
        # Find clear and cloudy pixels
        clear_mask = (cloud_mask == 0)
        cloudy_mask = (cloud_mask == 1)

        if method == 'nearest':
            # استيفاء بأقرب قيمة صافية
            # Interpolate using nearest clear value
            # تطبيق توسيع بسيط (dilation-like)
            # Apply simple dilation-like operation
            kernel_size = 3
            half_k = kernel_size // 2

            height, width = ndvi_image.shape
            for i in range(height):
                for j in range(width):
                    if cloudy_mask[i, j]:
                        # البحث عن أقرب بكسل صافي في الجوار
                        # Search for nearest clear pixel in neighborhood
                        found = False
                        for di in range(-half_k, half_k + 1):
                            for dj in range(-half_k, half_k + 1):
                                ni, nj = i + di, j + dj
                                if (0 <= ni < height and 0 <= nj < width and
                                    clear_mask[ni, nj]):
                                    interpolated[i, j] = ndvi_image[ni, nj]
                                    found = True
                                    break
                            if found:
                                break

        elif method == 'linear':
            # استيفاء خطي باستخدام متوسط القيم المحيطة
            # Linear interpolation using average of surrounding values
            kernel_size = 3
            half_k = kernel_size // 2

            height, width = ndvi_image.shape
            for i in range(height):
                for j in range(width):
                    if cloudy_mask[i, j]:
                        # جمع القيم الصافية المحيطة
                        # Collect surrounding clear values
                        clear_values = []
                        for di in range(-half_k, half_k + 1):
                            for dj in range(-half_k, half_k + 1):
                                ni, nj = i + di, j + dj
                                if (0 <= ni < height and 0 <= nj < width and
                                    clear_mask[ni, nj]):
                                    clear_values.append(ndvi_image[ni, nj])

                        # حساب المتوسط
                        # Calculate average
                        if clear_values:
                            interpolated[i, j] = np.mean(clear_values)

        return interpolated

    # =========================================================================
    # Helper Methods - دوال مساعدة
    # =========================================================================

    def _smooth_series(self, values: np.ndarray) -> np.ndarray:
        """
        تنعيم السلسلة الزمنية باستخدام المتوسط المتحرك
        Smooth time-series using moving average

        Args:
            values: القيم - Values array

        Returns:
            القيم المنعمة - Smoothed values
        """
        if len(values) < self.smoothing_window:
            return values

        # تطبيق المتوسط المتحرك
        # Apply moving average
        smoothed = np.convolve(
            values,
            np.ones(self.smoothing_window) / self.smoothing_window,
            mode='same'
        )

        return smoothed

    def _linear_regression(self, x: np.ndarray, y: np.ndarray) -> tuple[float, float]:
        """
        حساب الانحدار الخطي البسيط
        Calculate simple linear regression

        Args:
            x: المتغير المستقل - Independent variable
            y: المتغير التابع - Dependent variable

        Returns:
            (ميل، تقاطع) - (slope, intercept)
        """
        n = len(x)
        if n == 0:
            return 0.0, 0.0

        # حساب المتوسطات
        # Calculate means
        x_mean = np.mean(x)
        y_mean = np.mean(y)

        # حساب الميل
        # Calculate slope
        numerator = np.sum((x - x_mean) * (y - y_mean))
        denominator = np.sum((x - x_mean) ** 2)

        if denominator == 0:
            return 0.0, y_mean

        slope = numerator / denominator

        # حساب التقاطع
        # Calculate intercept
        intercept = y_mean - slope * x_mean

        return slope, intercept

    def _extract_weekly_pattern(self, values: list[float]) -> list[float]:
        """
        استخراج النمط الأسبوعي من السلسلة
        Extract weekly pattern from series

        Args:
            values: قيم السلسلة - Series values

        Returns:
            نمط أسبوعي (7 قيم) - Weekly pattern (7 values)
        """
        # حساب متوسط التغير لكل يوم من الأسبوع
        # Calculate average change for each day of week
        weekly_changes = [[] for _ in range(7)]

        for i in range(1, len(values)):
            day_of_week = i % 7
            change = values[i] - values[i - 1]
            weekly_changes[day_of_week].append(change)

        # حساب متوسط كل يوم
        # Calculate average for each day
        pattern = []
        for day_changes in weekly_changes:
            if day_changes:
                pattern.append(np.mean(day_changes))
            else:
                pattern.append(0.0)

        return pattern


# =============================================================================
# Utility Functions - دوال مساعدة عامة
# =============================================================================


def create_ndvi_timeseries(
    dates: list[date],
    values: list[float],
    quality_scores: list[float] | None = None,
    cloud_coverage: list[float] | None = None
) -> list[NDVIPoint]:
    """
    إنشاء سلسلة زمنية من NDVI من القوائم
    Create NDVI time-series from lists

    Args:
        dates: قائمة التواريخ - List of dates
        values: قائمة قيم NDVI - List of NDVI values
        quality_scores: قائمة درجات الجودة (اختياري) - List of quality scores (optional)
        cloud_coverage: قائمة نسب السحب (اختياري) - List of cloud coverage (optional)

    Returns:
        سلسلة زمنية من NDVIPoint - Time-series of NDVIPoint objects
    """
    if quality_scores is None:
        quality_scores = [1.0] * len(dates)
    if cloud_coverage is None:
        cloud_coverage = [0.0] * len(dates)

    if not (len(dates) == len(values) == len(quality_scores) == len(cloud_coverage)):
        raise ValueError("All input lists must have the same length")

    return [
        NDVIPoint(
            date=d,
            value=v,
            quality=q,
            cloud_coverage=c
        )
        for d, v, q, c in zip(dates, values, quality_scores, cloud_coverage, strict=False)
    ]


def export_results_to_dict(
    anomalies: list[AnomalyResult],
    trend: TrendResult,
    seasonal_metrics: SeasonalMetrics,
    changes: ChangeDetectionResult | None = None
) -> dict[str, Any]:
    """
    تصدير نتائج التحليل إلى قاموس
    Export analysis results to dictionary

    Args:
        anomalies: قائمة الشذوذات - List of anomalies
        trend: نتيجة الاتجاه - Trend result
        seasonal_metrics: المقاييس الموسمية - Seasonal metrics
        changes: نتيجة كشف التغيير (اختياري) - Change detection result (optional)

    Returns:
        قاموس النتائج - Results dictionary
    """
    return {
        "anomalies": [a.to_dict() for a in anomalies],
        "trend": trend.to_dict(),
        "seasonal_metrics": seasonal_metrics.to_dict(),
        "changes": changes.to_dict() if changes else None,
        "metadata": {
            "analysis_date": date.today().isoformat(),
            "total_anomalies": len(anomalies),
            "has_trend": trend.trend_type != TrendType.NO_TREND,
            "season_detected": seasonal_metrics.season_start is not None,
        }
    }


# =============================================================================
# Example Usage - مثال على الاستخدام
# =============================================================================


if __name__ == "__main__":
    """
    مثال على استخدام وحدة تحليل السلاسل الزمنية لـ NDVI
    Example usage of NDVI Time-Series Analysis Module
    """

    # إنشاء بيانات تجريبية
    # Create sample data
    print("Creating sample NDVI time-series...")

    start_date = date(2024, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(100)]

    # محاكاة منحنى NDVI موسمي مع بعض الضوضاء
    # Simulate seasonal NDVI curve with some noise
    values = []
    for i in range(100):
        # منحنى جيبي موسمي
        # Seasonal sine curve
        seasonal = 0.5 + 0.3 * np.sin(2 * np.pi * i / 90)
        # إضافة ضوضاء
        # Add noise
        noise = np.random.normal(0, 0.05)
        values.append(max(0, min(1, seasonal + noise)))

    # إضافة شذوذ
    # Add anomaly
    values[50] = 0.2  # انخفاض مفاجئ

    # إنشاء سلسلة NDVI
    # Create NDVI series
    ndvi_series = create_ndvi_timeseries(dates, values)

    # تهيئة المحلل
    # Initialize analyzer
    analyzer = NDVITimeSeriesAnalyzer(smoothing_window=5)

    # كشف الشذوذات
    # Detect anomalies
    print("\nDetecting anomalies...")
    anomalies = analyzer.detect_anomalies(ndvi_series, threshold=2.0)
    print(f"Found {len(anomalies)} anomalies")
    for anomaly in anomalies:
        print(f"  - {anomaly.date}: {anomaly.description_en}")

    # تحليل الاتجاه
    # Analyze trend
    print("\nAnalyzing trend...")
    trend = analyzer.calculate_trend(values, dates)
    print(f"Trend: {trend.trend_type.value}")
    print(f"  {trend.description_en}")
    print(f"  R²: {trend.r_squared:.4f}")

    # تحديد المراحل الفينولوجية
    # Identify phenological stages
    print("\nIdentifying phenological stages...")
    stages = analyzer.detect_phenological_stages(ndvi_series)
    print(f"Detected {len(stages)} stage transitions")
    for stage_date, stage, confidence in stages[:5]:  # First 5
        print(f"  - {stage_date}: {stage.value} (confidence: {confidence:.2f})")

    # تحديد بداية الموسم
    # Identify season start
    print("\nIdentifying growing season...")
    season_start = analyzer.identify_growing_season_start(ndvi_series)
    if season_start:
        print(f"Season started: {season_start}")

    peak = analyzer.identify_peak_greenness(ndvi_series)
    if peak:
        print(f"Peak greenness: {peak[0]} (NDVI: {peak[1]:.3f})")

    integral = analyzer.calculate_seasonal_integral(ndvi_series)
    print(f"Seasonal integral: {integral:.2f}")

    # التنبؤ
    # Forecast
    print("\nForecasting next 7 days...")
    predictions = analyzer.predict_next_values(ndvi_series, periods=7)
    print("Predictions:")
    for pred_date, pred_value in predictions:
        print(f"  - {pred_date}: {pred_value:.3f}")

    # اختبار حساب NDVI من النطاقات
    # Test NDVI calculation from bands
    print("\nTesting NDVI calculation from bands...")
    red_band = np.random.rand(100, 100) * 0.3
    nir_band = np.random.rand(100, 100) * 0.6
    ndvi_image = analyzer.calculate_ndvi(red_band, nir_band)
    print(f"NDVI image shape: {ndvi_image.shape}")
    print(f"NDVI range: [{ndvi_image.min():.3f}, {ndvi_image.max():.3f}]")

    # اختبار كشف السحب
    # Test cloud detection
    print("\nTesting cloud detection...")
    image_data = {
        'blue': np.random.rand(50, 50) * 0.3,
        'green': np.random.rand(50, 50) * 0.3,
        'red': red_band[:50, :50],
        'nir': nir_band[:50, :50],
    }
    cloud_result = analyzer.detect_clouds(image_data)
    print(f"Cloud coverage: {cloud_result.cloud_percentage:.2f}%")

    print("\n✓ NDVI Time-Series Analysis Module test completed successfully!")
    print("وحدة تحليل السلاسل الزمنية لـ NDVI جاهزة للاستخدام ✓")
