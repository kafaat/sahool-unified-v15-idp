"""
SAHOOL Satellite Service - Agricultural Change Detection System
نظام كشف التغيرات الزراعية

Detects significant changes in agricultural fields from satellite time series:
- Vegetation changes (growth, decline, stress)
- Water stress and flooding
- Harvest and planting detection
- Crop damage events
- Land clearing

References:
- "Agricultural Change Detection Using Satellite Time Series" (2023)
- "NDVI-based Crop Monitoring and Anomaly Detection" (2022)
- "Remote Sensing for Precision Agriculture" (FAO 2021)
"""

from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple
from datetime import datetime, date, timedelta
from enum import Enum
import math
import logging
import statistics

logger = logging.getLogger(__name__)


# =============================================================================
# Enums
# =============================================================================

class ChangeType(Enum):
    """Types of agricultural changes that can be detected"""
    VEGETATION_INCREASE = "vegetation_increase"      # النمو النباتي
    VEGETATION_DECREASE = "vegetation_decrease"      # التدهور النباتي
    WATER_STRESS = "water_stress"                    # الإجهاد المائي
    FLOODING = "flooding"                            # الفيضان
    HARVEST = "harvest"                              # الحصاد
    PLANTING = "planting"                            # الزراعة
    LAND_CLEARING = "land_clearing"                  # تجريف الأرض
    CROP_DAMAGE = "crop_damage"                      # تلف المحصول
    DROUGHT_STRESS = "drought_stress"                # إجهاد الجفاف
    PEST_DISEASE = "pest_disease"                    # الآفات والأمراض
    NO_CHANGE = "no_change"                          # لا تغيير


class SeverityLevel(str, Enum):
    """Severity levels for detected changes"""
    LOW = "low"                    # منخفض
    MEDIUM = "medium"              # متوسط
    HIGH = "high"                  # مرتفع
    CRITICAL = "critical"          # حرج


class TrendDirection(str, Enum):
    """Overall trend direction"""
    IMPROVING = "improving"        # تحسن
    STABLE = "stable"             # مستقر
    DECLINING = "declining"        # تدهور


# =============================================================================
# Data Models
# =============================================================================

@dataclass
class ChangeEvent:
    """A single detected change event"""
    field_id: str
    change_type: ChangeType
    severity: SeverityLevel
    detected_date: date
    location: Dict[str, float]  # {lat, lon, affected_area_ha}
    ndvi_before: float
    ndvi_after: float
    ndvi_change: float
    change_percent: float
    confidence: float  # 0.0 to 1.0
    description_ar: str
    description_en: str
    recommended_action_ar: str
    recommended_action_en: str
    additional_metrics: Dict[str, float] = None  # Optional NDWI, NDMI, etc.

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        result = asdict(self)
        result['change_type'] = self.change_type.value
        result['severity'] = self.severity.value
        result['detected_date'] = self.detected_date.isoformat()
        return result


@dataclass
class ChangeReport:
    """Comprehensive change detection report for a field"""
    field_id: str
    analysis_period: Dict[str, str]  # {start_date, end_date}
    events: List[ChangeEvent]
    overall_trend: TrendDirection
    ndvi_trend: float  # Slope of NDVI over time (positive = improving)
    anomaly_count: int
    severity_summary: Dict[str, int]  # Count by severity level
    change_type_summary: Dict[str, int]  # Count by change type
    summary_ar: str
    summary_en: str
    recommendations_ar: List[str]
    recommendations_en: List[str]

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        result = {
            'field_id': self.field_id,
            'analysis_period': self.analysis_period,
            'events': [event.to_dict() for event in self.events],
            'overall_trend': self.overall_trend.value,
            'ndvi_trend': self.ndvi_trend,
            'anomaly_count': self.anomaly_count,
            'severity_summary': self.severity_summary,
            'change_type_summary': self.change_type_summary,
            'summary_ar': self.summary_ar,
            'summary_en': self.summary_en,
            'recommendations_ar': self.recommendations_ar,
            'recommendations_en': self.recommendations_en,
        }
        return result


@dataclass
class NDVIDataPoint:
    """Single NDVI time series data point"""
    date: date
    ndvi: float
    ndwi: Optional[float] = None
    ndmi: Optional[float] = None
    cloud_cover: float = 0.0


# =============================================================================
# Change Detection Algorithm
# =============================================================================

class ChangeDetector:
    """
    Detect significant changes in agricultural fields from satellite time series.
    كشف التغييرات المهمة في الحقول الزراعية من السلاسل الزمنية للأقمار الصناعية
    """

    # Thresholds for change detection
    THRESHOLDS = {
        "significant_change": 0.10,      # NDVI change > 10%
        "major_change": 0.20,            # NDVI change > 20%
        "critical_change": 0.30,         # NDVI change > 30%
        "rapid_change_days": 14,         # Change within 2 weeks
        "seasonal_adjustment": True,     # Account for normal seasonal variation
        "min_ndvi_for_vegetation": 0.15, # Minimum NDVI to consider as vegetation
        "max_cloud_cover": 30.0,         # Maximum cloud cover to use data point
    }

    # Z-score thresholds for anomaly detection
    ANOMALY_THRESHOLDS = {
        "mild": 1.5,      # 1.5 standard deviations
        "moderate": 2.0,  # 2.0 standard deviations
        "severe": 2.5,    # 2.5 standard deviations
    }

    # Crop-specific seasonal patterns (simplified sine wave approximation)
    SEASONAL_PATTERNS = {
        "wheat": {
            "planting_month": 11,  # November
            "harvest_month": 5,    # May
            "peak_ndvi": 0.75,
            "base_ndvi": 0.20,
        },
        "sorghum": {
            "planting_month": 6,   # June
            "harvest_month": 10,   # October
            "peak_ndvi": 0.80,
            "base_ndvi": 0.25,
        },
        "coffee": {
            "planting_month": None,  # Perennial
            "harvest_month": None,
            "peak_ndvi": 0.85,
            "base_ndvi": 0.65,
        },
        "qat": {
            "planting_month": None,  # Perennial
            "harvest_month": None,
            "peak_ndvi": 0.80,
            "base_ndvi": 0.60,
        },
    }

    async def detect_changes(
        self,
        field_id: str,
        latitude: float,
        longitude: float,
        start_date: date,
        end_date: date,
        crop_type: Optional[str] = None,
        ndvi_timeseries: Optional[List[NDVIDataPoint]] = None,
    ) -> ChangeReport:
        """
        Detect all significant changes in the time period.

        Algorithm:
        1. Fetch or use provided NDVI time series for the period
        2. Calculate expected seasonal pattern (if crop known)
        3. Identify anomalies (deviations from expected)
        4. Classify each anomaly by type
        5. Generate report with recommendations

        Args:
            field_id: Unique field identifier
            latitude: Field latitude
            longitude: Field longitude
            start_date: Start of analysis period
            end_date: End of analysis period
            crop_type: Type of crop (e.g., "wheat", "sorghum")
            ndvi_timeseries: Optional pre-fetched NDVI time series

        Returns:
            ChangeReport with all detected changes and recommendations
        """
        logger.info(f"Detecting changes for field {field_id} from {start_date} to {end_date}")

        # If no time series provided, would fetch from satellite service
        # For now, we'll work with provided data or return mock
        if not ndvi_timeseries:
            # In real implementation, fetch from satellite service
            logger.warning("No NDVI time series provided - returning empty report")
            return self._create_empty_report(field_id, start_date, end_date)

        # Filter out cloudy observations
        clean_data = [
            point for point in ndvi_timeseries
            if point.cloud_cover <= self.THRESHOLDS["max_cloud_cover"]
        ]

        if len(clean_data) < 3:
            logger.warning(f"Insufficient clean data points ({len(clean_data)}) for field {field_id}")
            return self._create_empty_report(field_id, start_date, end_date)

        # Calculate expected pattern if crop type is known
        expected_pattern = None
        if crop_type and crop_type.lower() in self.SEASONAL_PATTERNS:
            expected_pattern = self._calculate_expected_pattern(
                clean_data, crop_type.lower()
            )

        # Detect anomalies
        anomalies = await self.detect_anomalies(clean_data, expected_pattern)

        # Calculate overall trend
        ndvi_trend = self._calculate_trend([p.ndvi for p in clean_data])
        overall_trend = self._determine_overall_trend(ndvi_trend, anomalies)

        # Classify changes and create events
        events = []
        for anomaly in anomalies:
            event = self._create_change_event(
                field_id=field_id,
                latitude=latitude,
                longitude=longitude,
                anomaly=anomaly,
                crop_type=crop_type,
                clean_data=clean_data,
            )
            if event:
                events.append(event)

        # Generate summary statistics
        severity_summary = self._count_by_severity(events)
        change_type_summary = self._count_by_change_type(events)

        # Generate summary text
        summary_ar, summary_en = self._generate_summary(
            events, ndvi_trend, overall_trend, start_date, end_date
        )

        # Generate recommendations
        recommendations_ar, recommendations_en = self._generate_recommendations(
            events, overall_trend, crop_type
        )

        return ChangeReport(
            field_id=field_id,
            analysis_period={
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
            events=events,
            overall_trend=overall_trend,
            ndvi_trend=ndvi_trend,
            anomaly_count=len(anomalies),
            severity_summary=severity_summary,
            change_type_summary=change_type_summary,
            summary_ar=summary_ar,
            summary_en=summary_en,
            recommendations_ar=recommendations_ar,
            recommendations_en=recommendations_en,
        )

    async def compare_dates(
        self,
        field_id: str,
        latitude: float,
        longitude: float,
        date1: date,
        date2: date,
        ndvi1: float,
        ndvi2: float,
        ndwi1: Optional[float] = None,
        ndwi2: Optional[float] = None,
    ) -> ChangeEvent:
        """
        Compare two specific dates and identify change.

        Args:
            field_id: Unique field identifier
            latitude: Field latitude
            longitude: Field longitude
            date1: First date (earlier)
            date2: Second date (later)
            ndvi1: NDVI value on date1
            ndvi2: NDVI value on date2
            ndwi1: Optional NDWI value on date1
            ndwi2: Optional NDWI value on date2

        Returns:
            ChangeEvent describing the change
        """
        logger.info(f"Comparing dates {date1} and {date2} for field {field_id}")

        # Calculate change metrics
        ndvi_change = ndvi2 - ndvi1
        change_percent = (ndvi_change / ndvi1 * 100) if ndvi1 != 0 else 0
        days_between = (date2 - date1).days

        # Determine season for context
        season = self._get_season(date2)

        # Classify the change
        change_type = self.classify_change(
            ndvi_before=ndvi1,
            ndvi_after=ndvi2,
            days_between=days_between,
            season=season,
            ndwi_before=ndwi1,
            ndwi_after=ndwi2,
        )

        # Determine severity
        severity = self._determine_severity(abs(change_percent), days_between)

        # Calculate confidence based on magnitude and time span
        confidence = self._calculate_confidence(
            change_percent=abs(change_percent),
            days_between=days_between,
        )

        # Generate descriptions and recommendations
        desc_ar, desc_en = self._generate_change_description(
            change_type, ndvi_change, change_percent, date1, date2
        )
        rec_ar, rec_en = self.generate_recommendation(
            change_type, severity, None
        )

        # Additional metrics
        additional_metrics = {}
        if ndwi1 is not None and ndwi2 is not None:
            additional_metrics["ndwi_before"] = ndwi1
            additional_metrics["ndwi_after"] = ndwi2
            additional_metrics["ndwi_change"] = ndwi2 - ndwi1

        return ChangeEvent(
            field_id=field_id,
            change_type=change_type,
            severity=severity,
            detected_date=date2,
            location={
                "lat": latitude,
                "lon": longitude,
                "affected_area_ha": 1.0,  # Single point, assume 1 hectare
            },
            ndvi_before=ndvi1,
            ndvi_after=ndvi2,
            ndvi_change=ndvi_change,
            change_percent=change_percent,
            confidence=confidence,
            description_ar=desc_ar,
            description_en=desc_en,
            recommended_action_ar=rec_ar,
            recommended_action_en=rec_en,
            additional_metrics=additional_metrics,
        )

    async def detect_anomalies(
        self,
        ndvi_series: List[NDVIDataPoint],
        expected_pattern: Optional[List[float]] = None
    ) -> List[Dict]:
        """
        Detect anomalies in NDVI time series.
        Uses Z-score or deviation from expected pattern.

        Args:
            ndvi_series: List of NDVI data points
            expected_pattern: Optional expected NDVI values for each point

        Returns:
            List of anomaly dictionaries with index, value, z_score, deviation
        """
        if len(ndvi_series) < 3:
            return []

        anomalies = []
        ndvi_values = [p.ndvi for p in ndvi_series]

        if expected_pattern and len(expected_pattern) == len(ndvi_values):
            # Deviation-based anomaly detection
            deviations = [
                actual - expected
                for actual, expected in zip(ndvi_values, expected_pattern)
            ]

            # Calculate statistics on deviations
            mean_dev = statistics.mean(deviations)
            std_dev = statistics.stdev(deviations) if len(deviations) > 1 else 0.01

            for i, (point, deviation) in enumerate(zip(ndvi_series, deviations)):
                z_score = abs((deviation - mean_dev) / std_dev) if std_dev > 0 else 0

                if z_score >= self.ANOMALY_THRESHOLDS["mild"]:
                    anomalies.append({
                        "index": i,
                        "date": point.date,
                        "ndvi": point.ndvi,
                        "expected": expected_pattern[i],
                        "deviation": deviation,
                        "z_score": z_score,
                        "ndwi": point.ndwi,
                        "ndmi": point.ndmi,
                    })
        else:
            # Z-score based anomaly detection (no expected pattern)
            mean_ndvi = statistics.mean(ndvi_values)
            std_ndvi = statistics.stdev(ndvi_values) if len(ndvi_values) > 1 else 0.01

            for i, point in enumerate(ndvi_series):
                z_score = abs((point.ndvi - mean_ndvi) / std_ndvi) if std_ndvi > 0 else 0

                if z_score >= self.ANOMALY_THRESHOLDS["mild"]:
                    anomalies.append({
                        "index": i,
                        "date": point.date,
                        "ndvi": point.ndvi,
                        "expected": mean_ndvi,
                        "deviation": point.ndvi - mean_ndvi,
                        "z_score": z_score,
                        "ndwi": point.ndwi,
                        "ndmi": point.ndmi,
                    })

        logger.info(f"Detected {len(anomalies)} anomalies in time series")
        return anomalies

    def classify_change(
        self,
        ndvi_before: float,
        ndvi_after: float,
        days_between: int,
        season: str,
        ndwi_before: Optional[float] = None,
        ndwi_after: Optional[float] = None,
    ) -> ChangeType:
        """
        Classify the type of change based on NDVI pattern.

        Classification logic:
        - Harvest: Rapid NDVI drop (>0.3) from high NDVI (>0.5)
        - Planting: NDVI rise from bare soil (<0.2) to vegetation (>0.3)
        - Water stress: NDVI drop + NDWI drop
        - Flooding: NDVI drop + NDWI increase
        - Land clearing: Very rapid drop to near zero
        - Crop damage: Moderate rapid drop
        - Vegetation increase/decrease: General trends

        Args:
            ndvi_before: NDVI value at earlier date
            ndvi_after: NDVI value at later date
            days_between: Number of days between measurements
            season: Season name ("winter", "spring", "summer", "fall")
            ndwi_before: Optional NDWI before
            ndwi_after: Optional NDWI after

        Returns:
            ChangeType enum value
        """
        ndvi_change = ndvi_after - ndvi_before
        change_rate = abs(ndvi_change) / max(days_between, 1)  # Change per day

        # No significant change
        if abs(ndvi_change) < self.THRESHOLDS["significant_change"]:
            return ChangeType.NO_CHANGE

        # Water-related changes (if NDWI available)
        if ndwi_before is not None and ndwi_after is not None:
            ndwi_change = ndwi_after - ndwi_before

            # Flooding: NDVI drop + NDWI increase
            if ndvi_change < -0.15 and ndwi_change > 0.15:
                return ChangeType.FLOODING

            # Water stress: NDVI drop + NDWI drop
            if ndvi_change < -0.15 and ndwi_change < -0.15:
                if abs(ndvi_change) > 0.25:
                    return ChangeType.DROUGHT_STRESS
                return ChangeType.WATER_STRESS

        # Harvest detection
        if (ndvi_before > 0.5 and
            ndvi_after < 0.3 and
            ndvi_change < -0.3 and
            days_between <= 30):
            return ChangeType.HARVEST

        # Planting detection
        if (ndvi_before < 0.25 and
            ndvi_after > 0.35 and
            ndvi_change > 0.2 and
            days_between <= 45):
            return ChangeType.PLANTING

        # Land clearing (very rapid drop to near zero)
        if (ndvi_before > 0.3 and
            ndvi_after < 0.15 and
            change_rate > 0.015):  # >1.5% per day
            return ChangeType.LAND_CLEARING

        # Crop damage (moderate rapid decrease)
        if (ndvi_change < -0.2 and
            days_between <= self.THRESHOLDS["rapid_change_days"] and
            ndvi_before > 0.3):
            return ChangeType.CROP_DAMAGE

        # Pest/disease (gradual decrease from healthy state)
        if (ndvi_change < -0.15 and
            days_between > 14 and
            ndvi_before > 0.5):
            return ChangeType.PEST_DISEASE

        # General vegetation changes
        if ndvi_change > 0:
            return ChangeType.VEGETATION_INCREASE
        else:
            return ChangeType.VEGETATION_DECREASE

    def generate_recommendation(
        self,
        change_type: ChangeType,
        severity: SeverityLevel,
        crop_type: Optional[str]
    ) -> Tuple[str, str]:
        """
        Generate actionable recommendation in Arabic and English.

        Args:
            change_type: Type of detected change
            severity: Severity level of the change
            crop_type: Type of crop (optional)

        Returns:
            Tuple of (arabic_recommendation, english_recommendation)
        """
        recommendations = {
            ChangeType.VEGETATION_INCREASE: (
                "استمر في نفس نظام الري والتسميد - المحصول ينمو بشكل جيد",
                "Continue current irrigation and fertilization - crop is growing well"
            ),
            ChangeType.VEGETATION_DECREASE: (
                "تحقق من الري والتسميد - قد يحتاج المحصول لعناية إضافية",
                "Check irrigation and fertilization - crop may need additional care"
            ),
            ChangeType.WATER_STRESS: {
                SeverityLevel.LOW: (
                    "راقب الري - علامات مبكرة لإجهاد مائي",
                    "Monitor irrigation - early signs of water stress"
                ),
                SeverityLevel.MEDIUM: (
                    "زد كمية الري بنسبة 20-30٪ - إجهاد مائي واضح",
                    "Increase irrigation by 20-30% - clear water stress"
                ),
                SeverityLevel.HIGH: (
                    "ري فوري مطلوب - إجهاد مائي شديد يؤثر على الإنتاج",
                    "Immediate irrigation required - severe water stress affecting yield"
                ),
                SeverityLevel.CRITICAL: (
                    "ري عاجل وفير - خطر فقدان المحصول",
                    "Urgent heavy irrigation - risk of crop failure"
                ),
            },
            ChangeType.DROUGHT_STRESS: (
                "ري عاجل وفحص نظام الري - جفاف شديد",
                "Urgent irrigation and check irrigation system - severe drought"
            ),
            ChangeType.FLOODING: (
                "تحسين الصرف وتجنب الري لعدة أيام - مياه زائدة",
                "Improve drainage and avoid irrigation for several days - excess water"
            ),
            ChangeType.HARVEST: (
                "حصاد تم بنجاح - خطط للزراعة القادمة",
                "Harvest completed successfully - plan for next planting"
            ),
            ChangeType.PLANTING: (
                "الزراعة ناجحة - حافظ على رطوبة التربة",
                "Planting successful - maintain soil moisture"
            ),
            ChangeType.LAND_CLEARING: (
                "تم اكتشاف تجريف - تحقق من حالة الحقل",
                "Land clearing detected - verify field status"
            ),
            ChangeType.CROP_DAMAGE: (
                "فحص الحقل فوراً - احتمال تلف من آفات أو طقس",
                "Inspect field immediately - possible pest or weather damage"
            ),
            ChangeType.PEST_DISEASE: (
                "فحص المحصول للآفات والأمراض - قد تحتاج مبيدات",
                "Check crop for pests and diseases - may need pesticides"
            ),
            ChangeType.NO_CHANGE: (
                "الحقل مستقر - استمر في الممارسات الحالية",
                "Field is stable - continue current practices"
            ),
        }

        rec = recommendations.get(change_type)

        # Handle severity-based recommendations
        if isinstance(rec, dict):
            rec = rec.get(severity, rec.get(SeverityLevel.MEDIUM))

        if rec:
            return rec
        else:
            return (
                "مراقبة مستمرة موصى بها",
                "Continued monitoring recommended"
            )

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _create_empty_report(
        self, field_id: str, start_date: date, end_date: date
    ) -> ChangeReport:
        """Create an empty report when insufficient data"""
        return ChangeReport(
            field_id=field_id,
            analysis_period={
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
            events=[],
            overall_trend=TrendDirection.STABLE,
            ndvi_trend=0.0,
            anomaly_count=0,
            severity_summary={},
            change_type_summary={},
            summary_ar="بيانات غير كافية لتحليل التغيرات",
            summary_en="Insufficient data for change analysis",
            recommendations_ar=["جمع المزيد من البيانات الساتلية"],
            recommendations_en=["Collect more satellite data"],
        )

    def _calculate_expected_pattern(
        self, data_points: List[NDVIDataPoint], crop_type: str
    ) -> List[float]:
        """Calculate expected seasonal NDVI pattern for a crop"""
        pattern_info = self.SEASONAL_PATTERNS.get(crop_type, {})

        if not pattern_info:
            return None

        expected = []
        for point in data_points:
            # Simple sinusoidal pattern based on day of year
            day_of_year = point.date.timetuple().tm_yday

            # Perennial crops have stable high NDVI
            if pattern_info["planting_month"] is None:
                expected_ndvi = pattern_info["base_ndvi"] + 0.1 * math.sin(
                    2 * math.pi * day_of_year / 365
                )
            else:
                # Annual crops have clear planting-harvest cycle
                planting_day = pattern_info["planting_month"] * 30
                cycle_day = (day_of_year - planting_day) % 365

                # Peak at middle of season
                peak_day = 120  # ~4 months after planting
                if cycle_day < peak_day:
                    progress = cycle_day / peak_day
                    expected_ndvi = (
                        pattern_info["base_ndvi"] +
                        (pattern_info["peak_ndvi"] - pattern_info["base_ndvi"]) *
                        math.sin(math.pi / 2 * progress)
                    )
                else:
                    decline = (cycle_day - peak_day) / (240 - peak_day)
                    expected_ndvi = (
                        pattern_info["peak_ndvi"] -
                        (pattern_info["peak_ndvi"] - pattern_info["base_ndvi"]) *
                        min(decline, 1.0)
                    )

            expected.append(round(expected_ndvi, 3))

        return expected

    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate linear trend (slope) of values"""
        if len(values) < 2:
            return 0.0

        n = len(values)
        x = list(range(n))

        # Linear regression: y = mx + b
        sum_x = sum(x)
        sum_y = sum(values)
        sum_xy = sum(xi * yi for xi, yi in zip(x, values))
        sum_x2 = sum(xi ** 2 for xi in x)

        denominator = n * sum_x2 - sum_x ** 2
        if denominator == 0:
            return 0.0

        slope = (n * sum_xy - sum_x * sum_y) / denominator
        return round(slope, 6)

    def _determine_overall_trend(
        self, ndvi_trend: float, anomalies: List[Dict]
    ) -> TrendDirection:
        """Determine overall trend direction"""
        # Count negative vs positive anomalies
        negative_anomalies = sum(
            1 for a in anomalies if a.get("deviation", 0) < 0
        )
        positive_anomalies = len(anomalies) - negative_anomalies

        # If trend is strongly positive and few negative anomalies
        if ndvi_trend > 0.001 and negative_anomalies <= positive_anomalies:
            return TrendDirection.IMPROVING

        # If trend is strongly negative and many negative anomalies
        if ndvi_trend < -0.001 and negative_anomalies > positive_anomalies:
            return TrendDirection.DECLINING

        # Otherwise stable
        return TrendDirection.STABLE

    def _create_change_event(
        self,
        field_id: str,
        latitude: float,
        longitude: float,
        anomaly: Dict,
        crop_type: Optional[str],
        clean_data: List[NDVIDataPoint],
    ) -> Optional[ChangeEvent]:
        """Create a ChangeEvent from an anomaly"""
        index = anomaly["index"]

        # Need at least one previous point to compare
        if index == 0:
            return None

        # Get before and after values
        point_after = clean_data[index]
        point_before = clean_data[index - 1]

        ndvi_change = point_after.ndvi - point_before.ndvi
        change_percent = (
            (ndvi_change / point_before.ndvi * 100)
            if point_before.ndvi != 0 else 0
        )
        days_between = (point_after.date - point_before.date).days

        # Skip if change is too small
        if abs(ndvi_change) < self.THRESHOLDS["significant_change"]:
            return None

        # Classify change
        season = self._get_season(point_after.date)
        change_type = self.classify_change(
            ndvi_before=point_before.ndvi,
            ndvi_after=point_after.ndvi,
            days_between=days_between,
            season=season,
            ndwi_before=point_before.ndwi,
            ndwi_after=point_after.ndwi,
        )

        # Determine severity
        severity = self._determine_severity(abs(change_percent), days_between)

        # Calculate confidence from z-score
        z_score = anomaly.get("z_score", 0)
        confidence = min(0.5 + (z_score / 5.0), 0.99)  # Higher z-score = higher confidence

        # Generate descriptions
        desc_ar, desc_en = self._generate_change_description(
            change_type, ndvi_change, change_percent,
            point_before.date, point_after.date
        )

        # Generate recommendations
        rec_ar, rec_en = self.generate_recommendation(
            change_type, severity, crop_type
        )

        # Additional metrics
        additional_metrics = {
            "z_score": z_score,
            "deviation": anomaly.get("deviation", 0),
        }
        if point_after.ndwi is not None:
            additional_metrics["ndwi"] = point_after.ndwi
        if point_after.ndmi is not None:
            additional_metrics["ndmi"] = point_after.ndmi

        return ChangeEvent(
            field_id=field_id,
            change_type=change_type,
            severity=severity,
            detected_date=point_after.date,
            location={
                "lat": latitude,
                "lon": longitude,
                "affected_area_ha": 1.0,
            },
            ndvi_before=point_before.ndvi,
            ndvi_after=point_after.ndvi,
            ndvi_change=ndvi_change,
            change_percent=change_percent,
            confidence=confidence,
            description_ar=desc_ar,
            description_en=desc_en,
            recommended_action_ar=rec_ar,
            recommended_action_en=rec_en,
            additional_metrics=additional_metrics,
        )

    def _determine_severity(
        self, change_percent: float, days_between: int
    ) -> SeverityLevel:
        """Determine severity level based on change magnitude and speed"""
        # Rapid changes are more severe
        daily_change = change_percent / max(days_between, 1)

        if change_percent > 30 or daily_change > 2.0:
            return SeverityLevel.CRITICAL
        elif change_percent > 20 or daily_change > 1.0:
            return SeverityLevel.HIGH
        elif change_percent > 10 or daily_change > 0.5:
            return SeverityLevel.MEDIUM
        else:
            return SeverityLevel.LOW

    def _calculate_confidence(
        self, change_percent: float, days_between: int
    ) -> float:
        """Calculate confidence based on change magnitude and time span"""
        # Higher confidence for larger changes over appropriate time spans
        magnitude_factor = min(abs(change_percent) / 30.0, 1.0)

        # Optimal time span is 7-30 days
        if 7 <= days_between <= 30:
            time_factor = 1.0
        elif days_between < 7:
            time_factor = 0.7  # Too quick, might be noise
        else:
            time_factor = 0.8  # Longer span, more uncertainty

        confidence = 0.5 + (magnitude_factor * time_factor * 0.45)
        return round(min(confidence, 0.95), 2)

    def _get_season(self, d: date) -> str:
        """Get season name for a date"""
        month = d.month
        if month in [12, 1, 2]:
            return "winter"
        elif month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        else:
            return "fall"

    def _generate_change_description(
        self,
        change_type: ChangeType,
        ndvi_change: float,
        change_percent: float,
        date1: date,
        date2: date,
    ) -> Tuple[str, str]:
        """Generate human-readable description of the change"""
        days = (date2 - date1).days

        descriptions = {
            ChangeType.VEGETATION_INCREASE: (
                f"زيادة في الغطاء النباتي بنسبة {abs(change_percent):.1f}٪ خلال {days} يوم",
                f"Vegetation cover increased by {abs(change_percent):.1f}% over {days} days"
            ),
            ChangeType.VEGETATION_DECREASE: (
                f"انخفاض في الغطاء النباتي بنسبة {abs(change_percent):.1f}٪ خلال {days} يوم",
                f"Vegetation cover decreased by {abs(change_percent):.1f}% over {days} days"
            ),
            ChangeType.WATER_STRESS: (
                f"إجهاد مائي مكتشف - انخفاض NDVI بنسبة {abs(change_percent):.1f}٪",
                f"Water stress detected - NDVI decreased by {abs(change_percent):.1f}%"
            ),
            ChangeType.DROUGHT_STRESS: (
                f"إجهاد جفاف شديد - انخفاض حاد في NDVI وNDWI",
                f"Severe drought stress - sharp decline in NDVI and NDWI"
            ),
            ChangeType.FLOODING: (
                f"فيضان محتمل - انخفاض NDVI مع زيادة NDWI",
                f"Potential flooding - NDVI decrease with NDWI increase"
            ),
            ChangeType.HARVEST: (
                f"حصاد مكتشف - انخفاض سريع في NDVI من {abs(change_percent):.1f}٪",
                f"Harvest detected - rapid NDVI drop of {abs(change_percent):.1f}%"
            ),
            ChangeType.PLANTING: (
                f"زراعة جديدة مكتشفة - زيادة NDVI من {abs(change_percent):.1f}٪",
                f"New planting detected - NDVI increase of {abs(change_percent):.1f}%"
            ),
            ChangeType.LAND_CLEARING: (
                f"تجريف أرض محتمل - انخفاض سريع جداً في NDVI",
                f"Potential land clearing - very rapid NDVI decrease"
            ),
            ChangeType.CROP_DAMAGE: (
                f"تلف محتمل في المحصول - انخفاض سريع بنسبة {abs(change_percent):.1f}٪",
                f"Potential crop damage - rapid decrease of {abs(change_percent):.1f}%"
            ),
            ChangeType.PEST_DISEASE: (
                f"احتمال آفات أو أمراض - انخفاض تدريجي في الصحة النباتية",
                f"Possible pest/disease - gradual decline in plant health"
            ),
            ChangeType.NO_CHANGE: (
                "لا توجد تغييرات كبيرة مكتشفة",
                "No significant changes detected"
            ),
        }

        return descriptions.get(change_type, (
            f"تغيير بنسبة {change_percent:.1f}٪ في NDVI",
            f"Change of {change_percent:.1f}% in NDVI"
        ))

    def _count_by_severity(self, events: List[ChangeEvent]) -> Dict[str, int]:
        """Count events by severity level"""
        counts = {
            SeverityLevel.LOW.value: 0,
            SeverityLevel.MEDIUM.value: 0,
            SeverityLevel.HIGH.value: 0,
            SeverityLevel.CRITICAL.value: 0,
        }
        for event in events:
            counts[event.severity.value] = counts.get(event.severity.value, 0) + 1
        return counts

    def _count_by_change_type(self, events: List[ChangeEvent]) -> Dict[str, int]:
        """Count events by change type"""
        counts = {}
        for event in events:
            key = event.change_type.value
            counts[key] = counts.get(key, 0) + 1
        return counts

    def _generate_summary(
        self,
        events: List[ChangeEvent],
        ndvi_trend: float,
        overall_trend: TrendDirection,
        start_date: date,
        end_date: date,
    ) -> Tuple[str, str]:
        """Generate summary text for the report"""
        days = (end_date - start_date).days

        if not events:
            return (
                f"لم يتم اكتشاف تغييرات كبيرة خلال {days} يوم. الحقل مستقر.",
                f"No significant changes detected over {days} days. Field is stable."
            )

        # Trend description
        trend_ar = {
            TrendDirection.IMPROVING: "تحسن",
            TrendDirection.STABLE: "مستقر",
            TrendDirection.DECLINING: "تدهور",
        }[overall_trend]

        trend_en = overall_trend.value

        # Count critical events
        critical_count = sum(
            1 for e in events if e.severity == SeverityLevel.CRITICAL
        )
        high_count = sum(
            1 for e in events if e.severity == SeverityLevel.HIGH
        )

        summary_ar = (
            f"تم اكتشاف {len(events)} تغيير خلال {days} يوم. "
            f"الاتجاه العام: {trend_ar}. "
        )
        summary_en = (
            f"Detected {len(events)} changes over {days} days. "
            f"Overall trend: {trend_en}. "
        )

        if critical_count > 0:
            summary_ar += f"تنبيه: {critical_count} حدث حرج يتطلب اهتمام فوري. "
            summary_en += f"Alert: {critical_count} critical event(s) requiring immediate attention. "
        elif high_count > 0:
            summary_ar += f"{high_count} حدث عالي الخطورة. "
            summary_en += f"{high_count} high-severity event(s). "

        return (summary_ar, summary_en)

    def _generate_recommendations(
        self,
        events: List[ChangeEvent],
        overall_trend: TrendDirection,
        crop_type: Optional[str],
    ) -> Tuple[List[str], List[str]]:
        """Generate list of recommendations"""
        recommendations_ar = []
        recommendations_en = []

        if not events:
            return (
                ["استمر في المراقبة المنتظمة للحقل"],
                ["Continue regular field monitoring"]
            )

        # Get unique change types
        change_types = list(set(e.change_type for e in events))

        # Priority recommendations based on severity
        critical_events = [e for e in events if e.severity == SeverityLevel.CRITICAL]
        high_events = [e for e in events if e.severity == SeverityLevel.HIGH]

        # Add critical recommendations first
        for event in critical_events[:2]:  # Max 2 critical
            recommendations_ar.append(event.recommended_action_ar)
            recommendations_en.append(event.recommended_action_en)

        # Add high-severity recommendations
        for event in high_events[:2]:  # Max 2 high
            if event.recommended_action_ar not in recommendations_ar:
                recommendations_ar.append(event.recommended_action_ar)
                recommendations_en.append(event.recommended_action_en)

        # Add general recommendations based on trend
        if overall_trend == TrendDirection.DECLINING:
            recommendations_ar.append(
                "فحص شامل للحقل لتحديد أسباب التدهور"
            )
            recommendations_en.append(
                "Comprehensive field inspection to identify causes of decline"
            )

        # Always add monitoring recommendation
        recommendations_ar.append("مراقبة مستمرة باستخدام الأقمار الصناعية")
        recommendations_en.append("Continuous monitoring using satellite imagery")

        return (recommendations_ar, recommendations_en)
