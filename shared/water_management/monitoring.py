"""
Water Monitoring Module - وحدة مراقبة المياه
=============================================

Provides water level and quality monitoring functionality:
- Real-time water level tracking
- Quality parameter monitoring
- Alert generation for thresholds
- Trend analysis

Integrates with IoT sensors and NATS event system.

Author: SAHOOL Platform Team
Version: 1.0.0
Updated: January 2026
"""

from __future__ import annotations

import statistics
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any

from .models import (
    AlertSeverity,
    ComplianceStatus,
    SaudiWaterStandards,
    WaterAlert,
    WaterQualityClass,
    WaterQualityParameter,
    WaterQualityTest,
    WaterSource,
    WaterSourceType,
)

# =============================================================================
# Water Level Monitoring - مراقبة مستوى المياه
# =============================================================================


@dataclass
class WaterLevelReading:
    """
    Single water level reading - قراءة مستوى مياه واحدة
    """

    id: str
    source_id: str
    tenant_id: str
    timestamp: datetime

    # Level measurement
    level_m3: float | None = None  # Volume in tank/reservoir
    level_percent: float | None = None  # Percentage of capacity
    depth_m: float | None = None  # Water depth for wells

    # For wells
    static_level_m: float | None = None  # مستوى المياه الساكنة
    dynamic_level_m: float | None = None  # مستوى المياه أثناء الضخ
    drawdown_m: float | None = None  # انخفاض المستوى

    # Sensor info
    sensor_id: str | None = None
    reading_quality: float = 1.0  # 0-1 quality score
    is_valid: bool = True

    # Battery/signal for remote sensors
    battery_percent: float | None = None
    signal_strength: int | None = None  # RSSI

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "source_id": self.source_id,
            "tenant_id": self.tenant_id,
            "timestamp": self.timestamp.isoformat(),
            "level": {
                "volume_m3": self.level_m3,
                "percent": self.level_percent,
                "depth_m": self.depth_m,
            },
            "well_levels": {
                "static_m": self.static_level_m,
                "dynamic_m": self.dynamic_level_m,
                "drawdown_m": self.drawdown_m,
            },
            "sensor": {
                "id": self.sensor_id,
                "quality": self.reading_quality,
                "is_valid": self.is_valid,
                "battery_percent": self.battery_percent,
            },
        }


@dataclass
class WaterLevelTrend:
    """
    Water level trend analysis - تحليل اتجاه مستوى المياه
    """

    source_id: str
    period_start: datetime
    period_end: datetime

    # Readings in period
    reading_count: int = 0
    valid_readings: int = 0

    # Level statistics
    avg_level_m3: float | None = None
    min_level_m3: float | None = None
    max_level_m3: float | None = None
    std_level_m3: float | None = None

    avg_level_percent: float | None = None
    min_level_percent: float | None = None
    max_level_percent: float | None = None

    # Trend analysis
    trend: str = "stable"  # increasing, decreasing, stable, fluctuating
    trend_ar: str = "مستقر"
    change_rate_m3_day: float | None = None  # Change per day
    change_rate_percent_day: float | None = None

    # Projections
    days_until_empty: float | None = None  # At current depletion rate
    days_until_full: float | None = None  # At current fill rate
    projected_level_7d_m3: float | None = None

    # Anomalies detected
    anomalies_detected: int = 0
    anomaly_details: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "source_id": self.source_id,
            "period": {
                "start": self.period_start.isoformat(),
                "end": self.period_end.isoformat(),
            },
            "readings": {
                "count": self.reading_count,
                "valid": self.valid_readings,
            },
            "statistics": {
                "avg_m3": self.avg_level_m3,
                "min_m3": self.min_level_m3,
                "max_m3": self.max_level_m3,
                "std_m3": self.std_level_m3,
                "avg_percent": self.avg_level_percent,
            },
            "trend": {
                "direction": self.trend,
                "direction_ar": self.trend_ar,
                "change_rate_m3_day": self.change_rate_m3_day,
                "change_rate_percent_day": self.change_rate_percent_day,
            },
            "projections": {
                "days_until_empty": self.days_until_empty,
                "days_until_full": self.days_until_full,
                "projected_level_7d_m3": self.projected_level_7d_m3,
            },
            "anomalies": {
                "count": self.anomalies_detected,
                "details": self.anomaly_details,
            },
        }


class WaterLevelMonitor:
    """
    Water level monitoring service - خدمة مراقبة مستوى المياه

    Monitors water levels in sources (wells, tanks, reservoirs)
    and generates alerts when thresholds are exceeded.
    """

    # Alert thresholds (percentage of capacity)
    CRITICAL_LOW_PERCENT = 10.0
    WARNING_LOW_PERCENT = 25.0
    NORMAL_MIN_PERCENT = 30.0
    WARNING_HIGH_PERCENT = 90.0
    CRITICAL_HIGH_PERCENT = 95.0

    # Well drawdown thresholds (meters)
    DRAWDOWN_WARNING_M = 5.0
    DRAWDOWN_CRITICAL_M = 10.0

    def __init__(self, tenant_id: str):
        """Initialize monitor for tenant"""
        self.tenant_id = tenant_id
        self._readings_cache: dict[str, list[WaterLevelReading]] = {}

    def record_reading(
        self,
        source: WaterSource,
        level_m3: float | None = None,
        level_percent: float | None = None,
        depth_m: float | None = None,
        static_level_m: float | None = None,
        dynamic_level_m: float | None = None,
        sensor_id: str | None = None,
    ) -> WaterLevelReading:
        """
        Record a new water level reading.
        تسجيل قراءة مستوى مياه جديدة
        """
        # Calculate level_percent if not provided
        if level_percent is None and level_m3 is not None and source.max_capacity_m3:
            level_percent = (level_m3 / source.max_capacity_m3) * 100

        # Calculate drawdown for wells
        drawdown_m = None
        if static_level_m is not None and dynamic_level_m is not None:
            drawdown_m = dynamic_level_m - static_level_m

        reading = WaterLevelReading(
            id=str(uuid.uuid4()),
            source_id=source.id,
            tenant_id=self.tenant_id,
            timestamp=datetime.now(UTC),
            level_m3=level_m3,
            level_percent=level_percent,
            depth_m=depth_m,
            static_level_m=static_level_m,
            dynamic_level_m=dynamic_level_m,
            drawdown_m=drawdown_m,
            sensor_id=sensor_id,
        )

        # Cache reading
        if source.id not in self._readings_cache:
            self._readings_cache[source.id] = []
        self._readings_cache[source.id].append(reading)

        # Keep only last 1000 readings per source
        if len(self._readings_cache[source.id]) > 1000:
            self._readings_cache[source.id] = self._readings_cache[source.id][-1000:]

        return reading

    def check_alerts(self, source: WaterSource, reading: WaterLevelReading) -> list[WaterAlert]:
        """
        Check reading against thresholds and generate alerts.
        فحص القراءة مقابل العتبات وإنشاء التنبيهات
        """
        alerts: list[WaterAlert] = []

        # Check tank/reservoir levels
        if reading.level_percent is not None:
            # Critical low level
            if reading.level_percent <= self.CRITICAL_LOW_PERCENT:
                alerts.append(
                    self._create_alert(
                        source=source,
                        alert_type="critical_low_level",
                        severity=AlertSeverity.CRITICAL,
                        title_en="Critical Low Water Level",
                        title_ar="مستوى مياه منخفض حرج",
                        message_en=f"Water level at {reading.level_percent:.1f}% - immediate action required",
                        message_ar=f"مستوى المياه عند {reading.level_percent:.1f}% - يتطلب إجراء فوري",
                        triggered_value=reading.level_percent,
                        threshold_value=self.CRITICAL_LOW_PERCENT,
                        unit="%",
                        recommended_action_en="Reduce water usage immediately and arrange for water delivery",
                        recommended_action_ar="قلل استخدام المياه فوراً ورتب لتوصيل المياه",
                    )
                )
            # Warning low level
            elif reading.level_percent <= self.WARNING_LOW_PERCENT:
                alerts.append(
                    self._create_alert(
                        source=source,
                        alert_type="low_level_warning",
                        severity=AlertSeverity.HIGH,
                        title_en="Low Water Level Warning",
                        title_ar="تحذير انخفاض مستوى المياه",
                        message_en=f"Water level at {reading.level_percent:.1f}% - plan for replenishment",
                        message_ar=f"مستوى المياه عند {reading.level_percent:.1f}% - خطط للتجديد",
                        triggered_value=reading.level_percent,
                        threshold_value=self.WARNING_LOW_PERCENT,
                        unit="%",
                        recommended_action_en="Schedule water replenishment within the next 2-3 days",
                        recommended_action_ar="جدول تجديد المياه خلال يومين إلى ثلاثة أيام",
                    )
                )
            # Warning high level (overflow risk)
            elif reading.level_percent >= self.CRITICAL_HIGH_PERCENT:
                alerts.append(
                    self._create_alert(
                        source=source,
                        alert_type="critical_high_level",
                        severity=AlertSeverity.HIGH,
                        title_en="Critical High Water Level - Overflow Risk",
                        title_ar="مستوى مياه مرتفع حرج - خطر فيضان",
                        message_en=f"Water level at {reading.level_percent:.1f}% - risk of overflow",
                        message_ar=f"مستوى المياه عند {reading.level_percent:.1f}% - خطر فيضان",
                        triggered_value=reading.level_percent,
                        threshold_value=self.CRITICAL_HIGH_PERCENT,
                        unit="%",
                        recommended_action_en="Stop inflow and increase water usage or drainage",
                        recommended_action_ar="أوقف التدفق وزد استخدام المياه أو التصريف",
                    )
                )

        # Check well drawdown
        if reading.drawdown_m is not None:
            if reading.drawdown_m >= self.DRAWDOWN_CRITICAL_M:
                alerts.append(
                    self._create_alert(
                        source=source,
                        alert_type="critical_drawdown",
                        severity=AlertSeverity.CRITICAL,
                        title_en="Critical Well Drawdown",
                        title_ar="انخفاض حرج في مستوى البئر",
                        message_en=f"Well drawdown at {reading.drawdown_m:.1f}m - reduce pumping immediately",
                        message_ar=f"انخفاض البئر عند {reading.drawdown_m:.1f}م - قلل الضخ فوراً",
                        triggered_value=reading.drawdown_m,
                        threshold_value=self.DRAWDOWN_CRITICAL_M,
                        unit="m",
                        recommended_action_en="Reduce pump rate or allow well to recover",
                        recommended_action_ar="قلل معدل الضخ أو اسمح للبئر بالتعافي",
                    )
                )
            elif reading.drawdown_m >= self.DRAWDOWN_WARNING_M:
                alerts.append(
                    self._create_alert(
                        source=source,
                        alert_type="drawdown_warning",
                        severity=AlertSeverity.MEDIUM,
                        title_en="Well Drawdown Warning",
                        title_ar="تحذير انخفاض مستوى البئر",
                        message_en=f"Well drawdown at {reading.drawdown_m:.1f}m - monitor closely",
                        message_ar=f"انخفاض البئر عند {reading.drawdown_m:.1f}م - راقب عن كثب",
                        triggered_value=reading.drawdown_m,
                        threshold_value=self.DRAWDOWN_WARNING_M,
                        unit="m",
                        recommended_action_en="Consider reducing pump operating hours",
                        recommended_action_ar="فكر في تقليل ساعات تشغيل المضخة",
                    )
                )

        return alerts

    def analyze_trend(
        self,
        source_id: str,
        hours: int = 168,  # 7 days default
    ) -> WaterLevelTrend:
        """
        Analyze water level trend over specified period.
        تحليل اتجاه مستوى المياه خلال الفترة المحددة
        """
        now = datetime.now(UTC)
        period_start = now - timedelta(hours=hours)

        readings = self._readings_cache.get(source_id, [])
        period_readings = [r for r in readings if r.timestamp >= period_start and r.is_valid]

        trend = WaterLevelTrend(
            source_id=source_id,
            period_start=period_start,
            period_end=now,
            reading_count=len(period_readings),
            valid_readings=len(period_readings),
        )

        if not period_readings:
            return trend

        # Calculate statistics
        levels_m3 = [r.level_m3 for r in period_readings if r.level_m3 is not None]
        levels_percent = [r.level_percent for r in period_readings if r.level_percent is not None]

        if levels_m3:
            trend.avg_level_m3 = statistics.mean(levels_m3)
            trend.min_level_m3 = min(levels_m3)
            trend.max_level_m3 = max(levels_m3)
            if len(levels_m3) > 1:
                trend.std_level_m3 = statistics.stdev(levels_m3)

        if levels_percent:
            trend.avg_level_percent = statistics.mean(levels_percent)
            trend.min_level_percent = min(levels_percent)
            trend.max_level_percent = max(levels_percent)

        # Calculate trend direction
        if len(period_readings) >= 2:
            first_reading = period_readings[0]
            last_reading = period_readings[-1]

            if first_reading.level_m3 is not None and last_reading.level_m3 is not None:
                change = last_reading.level_m3 - first_reading.level_m3
                time_diff_days = (last_reading.timestamp - first_reading.timestamp).total_seconds() / 86400

                if time_diff_days > 0:
                    trend.change_rate_m3_day = change / time_diff_days

                    # Determine trend direction
                    if abs(change) < 0.5:  # Less than 0.5 m3 change
                        trend.trend = "stable"
                        trend.trend_ar = "مستقر"
                    elif change > 0:
                        trend.trend = "increasing"
                        trend.trend_ar = "متزايد"
                    else:
                        trend.trend = "decreasing"
                        trend.trend_ar = "متناقص"

                    # Calculate days until empty/full
                    if trend.change_rate_m3_day and trend.change_rate_m3_day < 0:
                        if last_reading.level_m3:
                            trend.days_until_empty = abs(last_reading.level_m3 / trend.change_rate_m3_day)

        return trend

    def _create_alert(
        self,
        source: WaterSource,
        alert_type: str,
        severity: AlertSeverity,
        title_en: str,
        title_ar: str,
        message_en: str,
        message_ar: str,
        triggered_value: float,
        threshold_value: float,
        unit: str,
        recommended_action_en: str,
        recommended_action_ar: str,
    ) -> WaterAlert:
        """Create a water alert"""
        return WaterAlert(
            id=str(uuid.uuid4()),
            tenant_id=self.tenant_id,
            farm_id=source.farm_id,
            source_id=source.id,
            alert_type=alert_type,
            severity=severity,
            title_en=title_en,
            title_ar=title_ar,
            message_en=message_en,
            message_ar=message_ar,
            triggered_value=triggered_value,
            threshold_value=threshold_value,
            unit=unit,
            recommended_action_en=recommended_action_en,
            recommended_action_ar=recommended_action_ar,
        )


# =============================================================================
# Water Quality Monitoring - مراقبة جودة المياه
# =============================================================================


class WaterQualityMonitor:
    """
    Water quality monitoring service - خدمة مراقبة جودة المياه

    Monitors water quality parameters and generates alerts
    based on Saudi standards for irrigation water.
    """

    def __init__(self, tenant_id: str):
        """Initialize monitor for tenant"""
        self.tenant_id = tenant_id
        self.standards = SaudiWaterStandards()
        self._test_history: dict[str, list[WaterQualityTest]] = {}

    def evaluate_quality(self, test: WaterQualityTest) -> tuple[WaterQualityClass, list[WaterQualityParameter]]:
        """
        Evaluate water quality and return classification and issues.
        تقييم جودة المياه وإرجاع التصنيف والمشاكل
        """
        issues: list[WaterQualityParameter] = []
        quality_class = WaterQualityClass.CLASS_B  # Default

        # Evaluate EC
        if test.electrical_conductivity_ds_m is not None:
            ec = test.electrical_conductivity_ds_m
            param = WaterQualityParameter(
                parameter="EC",
                parameter_ar="الموصلية الكهربائية",
                value=ec,
                unit="dS/m",
                max_acceptable=self.standards.EC_CLASS_B_MAX,
                is_within_limits=ec <= self.standards.EC_CLASS_B_MAX,
            )
            if not param.is_within_limits:
                issues.append(param)

            # Update class based on EC
            if ec <= self.standards.EC_CLASS_A_MAX:
                quality_class = WaterQualityClass.CLASS_A
            elif ec <= self.standards.EC_CLASS_B_MAX:
                quality_class = WaterQualityClass.CLASS_B
            elif ec <= self.standards.EC_CLASS_C_MAX:
                quality_class = WaterQualityClass.CLASS_C
            elif ec <= self.standards.EC_CLASS_D_MAX:
                quality_class = WaterQualityClass.CLASS_D
            else:
                quality_class = WaterQualityClass.UNFIT

        # Evaluate pH
        if test.ph is not None:
            ph = test.ph
            is_within = self.standards.PH_MIN <= ph <= self.standards.PH_MAX
            param = WaterQualityParameter(
                parameter="pH",
                parameter_ar="درجة الحموضة",
                value=ph,
                unit="",
                min_acceptable=self.standards.PH_MIN,
                max_acceptable=self.standards.PH_MAX,
                is_within_limits=is_within,
            )
            if not is_within:
                issues.append(param)

        # Evaluate SAR
        if test.sar is not None:
            sar = test.sar
            sar_limit = self.standards.SAR_LOAM_MAX  # Default to loam
            param = WaterQualityParameter(
                parameter="SAR",
                parameter_ar="نسبة امتصاص الصوديوم",
                value=sar,
                unit="",
                max_acceptable=sar_limit,
                is_within_limits=sar <= sar_limit,
            )
            if not param.is_within_limits:
                issues.append(param)

        # Evaluate Boron
        if test.boron_ppm is not None:
            boron = test.boron_ppm
            boron_limit = self.standards.BORON_MODERATE_MAX
            param = WaterQualityParameter(
                parameter="Boron",
                parameter_ar="البورون",
                value=boron,
                unit="ppm",
                max_acceptable=boron_limit,
                is_within_limits=boron <= boron_limit,
            )
            if not param.is_within_limits:
                issues.append(param)

        # Evaluate Chloride for sensitive crops
        if test.chloride_ppm is not None:
            chloride = test.chloride_ppm
            chloride_limit = 350  # ppm for sensitive crops
            param = WaterQualityParameter(
                parameter="Chloride",
                parameter_ar="الكلوريد",
                value=chloride,
                unit="ppm",
                max_acceptable=chloride_limit,
                is_within_limits=chloride <= chloride_limit,
            )
            if not param.is_within_limits:
                issues.append(param)

        # Evaluate Sodium
        if test.sodium_ppm is not None:
            sodium = test.sodium_ppm
            sodium_limit = 200  # ppm
            param = WaterQualityParameter(
                parameter="Sodium",
                parameter_ar="الصوديوم",
                value=sodium,
                unit="ppm",
                max_acceptable=sodium_limit,
                is_within_limits=sodium <= sodium_limit,
            )
            if not param.is_within_limits:
                issues.append(param)

        # Evaluate Nitrate
        if test.nitrate_ppm is not None:
            nitrate = test.nitrate_ppm
            nitrate_limit = 50  # ppm for irrigation
            param = WaterQualityParameter(
                parameter="Nitrate",
                parameter_ar="النترات",
                value=nitrate,
                unit="ppm",
                max_acceptable=nitrate_limit,
                is_within_limits=nitrate <= nitrate_limit,
            )
            if not param.is_within_limits:
                issues.append(param)

        return quality_class, issues

    def check_quality_alerts(self, source: WaterSource, test: WaterQualityTest) -> list[WaterAlert]:
        """
        Check quality test results and generate alerts.
        فحص نتائج اختبار الجودة وإنشاء التنبيهات
        """
        alerts: list[WaterAlert] = []
        quality_class, issues = self.evaluate_quality(test)

        # Update test classification
        test.quality_class = quality_class

        # Alert if water is unfit
        if quality_class == WaterQualityClass.UNFIT:
            alerts.append(
                WaterAlert(
                    id=str(uuid.uuid4()),
                    tenant_id=self.tenant_id,
                    farm_id=source.farm_id,
                    source_id=source.id,
                    alert_type="water_unfit",
                    severity=AlertSeverity.CRITICAL,
                    title_en="Water Unfit for Irrigation",
                    title_ar="مياه غير صالحة للري",
                    message_en="Water quality test indicates water is unfit for any agricultural use",
                    message_ar="يشير اختبار جودة المياه إلى أن المياه غير صالحة لأي استخدام زراعي",
                    recommended_action_en="Stop using this water source. Consult water treatment specialist",
                    recommended_action_ar="توقف عن استخدام مصدر المياه هذا. استشر متخصص معالجة المياه",
                )
            )

        # Alert for specific parameter issues
        for issue in issues:
            severity = AlertSeverity.HIGH if issue.parameter in ("EC", "SAR") else AlertSeverity.MEDIUM

            alerts.append(
                WaterAlert(
                    id=str(uuid.uuid4()),
                    tenant_id=self.tenant_id,
                    farm_id=source.farm_id,
                    source_id=source.id,
                    alert_type=f"quality_issue_{issue.parameter.lower()}",
                    severity=severity,
                    title_en=f"Water Quality Issue: {issue.parameter}",
                    title_ar=f"مشكلة جودة المياه: {issue.parameter_ar}",
                    message_en=f"{issue.parameter} level ({issue.value} {issue.unit}) "
                    f"exceeds acceptable limit ({issue.max_acceptable} {issue.unit})",
                    message_ar=f"مستوى {issue.parameter_ar} ({issue.value} {issue.unit}) "
                    f"يتجاوز الحد المقبول ({issue.max_acceptable} {issue.unit})",
                    triggered_value=issue.value,
                    threshold_value=issue.max_acceptable or 0,
                    unit=issue.unit,
                    recommended_action_en=self._get_parameter_recommendation_en(issue.parameter),
                    recommended_action_ar=self._get_parameter_recommendation_ar(issue.parameter),
                )
            )

        return alerts

    def get_suitable_crops(self, quality_class: WaterQualityClass) -> tuple[list[str], list[str]]:
        """
        Get suitable and unsuitable crops based on water quality.
        الحصول على المحاصيل المناسبة وغير المناسبة بناءً على جودة المياه
        """
        # Suitable crops by water quality class (English, Arabic)
        suitable_by_class = {
            WaterQualityClass.CLASS_A: (
                ["All crops", "Vegetables", "Fruits", "Cereals"],
                ["جميع المحاصيل", "الخضروات", "الفواكه", "الحبوب"],
            ),
            WaterQualityClass.CLASS_B: (
                ["Date palm", "Wheat", "Barley", "Alfalfa", "Most vegetables"],
                ["النخيل", "القمح", "الشعير", "البرسيم", "معظم الخضروات"],
            ),
            WaterQualityClass.CLASS_C: (
                ["Date palm", "Barley", "Cotton", "Sugar beet"],
                ["النخيل", "الشعير", "القطن", "بنجر السكر"],
            ),
            WaterQualityClass.CLASS_D: (
                ["Salt-tolerant crops only", "Date palm", "Barley"],
                ["المحاصيل المتحملة للملوحة فقط", "النخيل", "الشعير"],
            ),
            WaterQualityClass.UNFIT: (
                [],
                [],
            ),
        }

        unsuitable_by_class = {
            WaterQualityClass.CLASS_A: ([], []),
            WaterQualityClass.CLASS_B: (
                ["Sensitive citrus", "Strawberry"],
                ["الحمضيات الحساسة", "الفراولة"],
            ),
            WaterQualityClass.CLASS_C: (
                ["Most vegetables", "Citrus", "Stone fruits"],
                ["معظم الخضروات", "الحمضيات", "الفواكه ذات النواة"],
            ),
            WaterQualityClass.CLASS_D: (
                ["Vegetables", "Fruits", "Sensitive crops"],
                ["الخضروات", "الفواكه", "المحاصيل الحساسة"],
            ),
            WaterQualityClass.UNFIT: (
                ["All crops"],
                ["جميع المحاصيل"],
            ),
        }

        suitable = suitable_by_class.get(quality_class, ([], []))
        unsuitable = unsuitable_by_class.get(quality_class, ([], []))

        return suitable[0], unsuitable[0]  # Return English lists

    def analyze_quality_trend(self, source_id: str, months: int = 12) -> dict[str, Any]:
        """
        Analyze water quality trend over specified period.
        تحليل اتجاه جودة المياه خلال الفترة المحددة
        """
        tests = self._test_history.get(source_id, [])
        cutoff = datetime.now(UTC) - timedelta(days=months * 30)
        period_tests = [t for t in tests if t.tested_at >= cutoff]

        if not period_tests:
            return {
                "source_id": source_id,
                "period_months": months,
                "test_count": 0,
                "trend": "insufficient_data",
                "trend_ar": "بيانات غير كافية",
            }

        # Sort by date
        period_tests.sort(key=lambda t: t.tested_at)

        # Track key parameters
        ec_values = [t.electrical_conductivity_ds_m for t in period_tests if t.electrical_conductivity_ds_m]
        tds_values = [t.tds_ppm for t in period_tests if t.tds_ppm]
        ph_values = [t.ph for t in period_tests if t.ph]

        result = {
            "source_id": source_id,
            "period_months": months,
            "test_count": len(period_tests),
            "parameters": {},
        }

        if ec_values:
            ec_trend = "stable"
            if len(ec_values) >= 2:
                change = ec_values[-1] - ec_values[0]
                if change > 0.5:
                    ec_trend = "increasing"
                elif change < -0.5:
                    ec_trend = "improving"

            result["parameters"]["ec"] = {
                "current": ec_values[-1],
                "avg": statistics.mean(ec_values),
                "min": min(ec_values),
                "max": max(ec_values),
                "trend": ec_trend,
            }

        if tds_values:
            result["parameters"]["tds"] = {
                "current": tds_values[-1],
                "avg": statistics.mean(tds_values),
                "min": min(tds_values),
                "max": max(tds_values),
            }

        if ph_values:
            result["parameters"]["ph"] = {
                "current": ph_values[-1],
                "avg": statistics.mean(ph_values),
                "min": min(ph_values),
                "max": max(ph_values),
            }

        return result

    def _get_parameter_recommendation_en(self, parameter: str) -> str:
        """Get recommendation for parameter issue (English)"""
        recommendations = {
            "EC": "Consider blending with lower-salinity water or use salt-tolerant crops",
            "SAR": "Apply gypsum to improve soil structure and reduce sodium hazard",
            "Boron": "Use boron-tolerant crops or blend with low-boron water",
            "Chloride": "Avoid foliar irrigation and use chloride-tolerant crops",
            "Sodium": "Improve drainage and apply calcium amendments",
            "pH": "Consult water treatment specialist for pH adjustment",
            "Nitrate": "Monitor crop nitrogen needs to avoid over-fertilization",
        }
        return recommendations.get(parameter, "Consult water quality specialist")

    def _get_parameter_recommendation_ar(self, parameter: str) -> str:
        """Get recommendation for parameter issue (Arabic)"""
        recommendations = {
            "EC": "فكر في خلط المياه مع مياه أقل ملوحة أو استخدم محاصيل متحملة للملوحة",
            "SAR": "أضف الجبس لتحسين بنية التربة وتقليل خطر الصوديوم",
            "Boron": "استخدم محاصيل متحملة للبورون أو اخلط مع مياه منخفضة البورون",
            "Chloride": "تجنب الري الورقي واستخدم محاصيل متحملة للكلوريد",
            "Sodium": "حسّن الصرف وأضف تعديلات الكالسيوم",
            "pH": "استشر متخصص معالجة المياه لضبط درجة الحموضة",
            "Nitrate": "راقب احتياجات المحصول من النيتروجين لتجنب الإفراط في التسميد",
        }
        return recommendations.get(parameter, "استشر متخصص جودة المياه")


# =============================================================================
# Groundwater Monitoring - مراقبة المياه الجوفية
# =============================================================================


@dataclass
class AquiferStatus:
    """
    Aquifer status assessment - تقييم حالة طبقة المياه الجوفية
    """

    aquifer_name: str
    aquifer_name_ar: str
    region: str
    assessment_date: datetime

    # Wells monitored
    well_count: int = 0
    active_wells: int = 0

    # Water levels
    avg_static_level_m: float | None = None
    avg_dynamic_level_m: float | None = None
    avg_drawdown_m: float | None = None

    # Trends
    level_change_m_year: float | None = None
    level_trend: str = "stable"  # declining, stable, recovering
    level_trend_ar: str = "مستقر"

    # Extraction vs recharge
    estimated_extraction_m3_year: float | None = None
    estimated_recharge_m3_year: float | None = None
    sustainability_index: float | None = None  # extraction/recharge

    # Status
    status: str = "sustainable"  # sustainable, stressed, critical
    status_ar: str = "مستدام"

    # Recommendations
    recommendations_en: list[str] = field(default_factory=list)
    recommendations_ar: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "aquifer": {
                "name": self.aquifer_name,
                "name_ar": self.aquifer_name_ar,
                "region": self.region,
            },
            "assessment_date": self.assessment_date.isoformat(),
            "wells": {
                "total": self.well_count,
                "active": self.active_wells,
            },
            "water_levels": {
                "avg_static_m": self.avg_static_level_m,
                "avg_dynamic_m": self.avg_dynamic_level_m,
                "avg_drawdown_m": self.avg_drawdown_m,
            },
            "trends": {
                "level_change_m_year": self.level_change_m_year,
                "direction": self.level_trend,
                "direction_ar": self.level_trend_ar,
            },
            "sustainability": {
                "extraction_m3_year": self.estimated_extraction_m3_year,
                "recharge_m3_year": self.estimated_recharge_m3_year,
                "index": self.sustainability_index,
            },
            "status": self.status,
            "status_ar": self.status_ar,
            "recommendations": {
                "en": self.recommendations_en,
                "ar": self.recommendations_ar,
            },
        }


class GroundwaterMonitor:
    """
    Groundwater monitoring service - خدمة مراقبة المياه الجوفية

    Monitors groundwater levels and sustainability for wells.
    """

    def __init__(self, tenant_id: str):
        """Initialize monitor"""
        self.tenant_id = tenant_id
        self.standards = SaudiWaterStandards()

    def assess_well_sustainability(
        self,
        well: WaterSource,
        extraction_m3_year: float,
        level_change_m_year: float | None = None,
    ) -> dict[str, Any]:
        """
        Assess sustainability of well extraction.
        تقييم استدامة استخراج البئر
        """
        if well.source_type not in (
            WaterSourceType.WELL,
            WaterSourceType.ARTESIAN_WELL,
        ):
            return {"error": "Not a well source"}

        # Get regional limit
        region = well.region or "central"
        extraction_limit = self.standards.get_extraction_limit(region)

        # Calculate sustainability metrics
        utilization = (extraction_m3_year / extraction_limit) * 100

        status = "sustainable"
        status_ar = "مستدام"
        recommendations_en = []
        recommendations_ar = []

        if utilization > 100:
            status = "over_extraction"
            status_ar = "استخراج مفرط"
            recommendations_en.append(f"Reduce extraction by {utilization - 100:.0f}% to comply with regional limits")
            recommendations_ar.append(f"قلل الاستخراج بنسبة {utilization - 100:.0f}% للامتثال للحدود الإقليمية")
        elif utilization > 80:
            status = "high_utilization"
            status_ar = "استخدام عالي"
            recommendations_en.append("Monitor extraction closely and plan for efficiency improvements")
            recommendations_ar.append("راقب الاستخراج عن كثب وخطط لتحسينات الكفاءة")

        if level_change_m_year is not None and level_change_m_year < -0.5:
            recommendations_en.append(
                f"Water table declining at {abs(level_change_m_year):.1f}m/year. Consider reducing pumping"
            )
            recommendations_ar.append(
                f"منسوب المياه ينخفض بمعدل {abs(level_change_m_year):.1f}م/سنة. فكر في تقليل الضخ"
            )

        return {
            "well_id": well.id,
            "region": region,
            "extraction_m3_year": extraction_m3_year,
            "extraction_limit_m3_year": extraction_limit,
            "utilization_percent": utilization,
            "level_change_m_year": level_change_m_year,
            "status": status,
            "status_ar": status_ar,
            "recommendations_en": recommendations_en,
            "recommendations_ar": recommendations_ar,
        }

    def check_license_compliance(self, source: WaterSource) -> ComplianceStatus:
        """
        Check if source is compliant with license requirements.
        التحقق من امتثال المصدر لمتطلبات الترخيص
        """
        issues = []

        # Check license validity
        if not source.is_license_valid:
            issues.append("expired_license")

        # Check extraction vs allocation
        if source.licensed_extraction_m3_year and source.total_extracted_m3_ytd > source.licensed_extraction_m3_year:
            issues.append("exceeded_allocation")

        # Check meter requirement
        if (
            source.source_type in (WaterSourceType.WELL, WaterSourceType.ARTESIAN_WELL)
            and source.well_depth_m
            and source.well_depth_m > self.standards.METER_REQUIRED_WELL_DEPTH_M
            and not source.has_meter
        ):
            issues.append("meter_required")

        if not issues:
            return ComplianceStatus.COMPLIANT
        elif "exceeded_allocation" in issues or "expired_license" in issues:
            return ComplianceStatus.NON_COMPLIANT
        else:
            return ComplianceStatus.WARNING
