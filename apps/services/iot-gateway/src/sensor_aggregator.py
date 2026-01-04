"""
خدمة تجميع بيانات المستشعرات - SAHOOL IoT
Sensor Data Aggregation Service

يوفر تجميع البيانات، الإحصائيات، واكتشاف الشذوذات لقراءات المستشعرات
Provides data aggregation, statistics, and anomaly detection for sensor readings
"""

import statistics
from collections import defaultdict
from datetime import UTC, datetime, timedelta

from .models.sensor_data import (
    AggregatedData,
    SensorHealth,
    SensorReading,
    SensorStatus,
    TimeGranularity,
    check_value_in_range,
    get_threshold,
)


class SensorAggregator:
    """
    مجمع بيانات المستشعرات
    Sensor Data Aggregator

    يوفر وظائف متقدمة لتجميع وتحليل بيانات المستشعرات
    Provides advanced functionality for aggregating and analyzing sensor data
    """

    def __init__(self):
        """تهيئة المجمع - Initialize aggregator"""
        self.readings_cache: dict[str, list[SensorReading]] = {}
        self.health_cache: dict[str, SensorHealth] = {}

    def aggregate_by_field(
        self,
        field_id: str,
        time_range: tuple[datetime, datetime],
        readings: list[SensorReading],
        granularity: TimeGranularity = TimeGranularity.DAILY,
    ) -> list[AggregatedData]:
        """
        تجميع البيانات حسب الحقل
        Aggregate data by field

        Args:
            field_id: معرف الحقل - Field ID
            time_range: الفترة الزمنية (بداية، نهاية) - Time range (start, end)
            readings: قائمة القراءات - List of readings
            granularity: دقة الوقت - Time granularity

        Returns:
            قائمة البيانات المجمعة - List of aggregated data
        """
        # تصفية القراءات للحقل المطلوب - Filter readings for the field
        field_readings = [r for r in readings if r.field_id == field_id]

        # تجميع حسب نوع المستشعر - Group by sensor type
        by_type = defaultdict(list)
        for reading in field_readings:
            by_type[reading.sensor_type].append(reading)

        # حساب التجميع لكل نوع - Calculate aggregation for each type
        aggregated = []
        for sensor_type, type_readings in by_type.items():
            agg_data = self._aggregate_readings(
                field_id=field_id,
                sensor_type=sensor_type,
                time_range=time_range,
                readings=type_readings,
                granularity=granularity,
            )
            aggregated.append(agg_data)

        return aggregated

    def aggregate_by_sensor_type(
        self,
        sensor_type: str,
        time_range: tuple[datetime, datetime],
        readings: list[SensorReading],
        granularity: TimeGranularity = TimeGranularity.DAILY,
    ) -> dict[str, AggregatedData]:
        """
        تجميع البيانات حسب نوع المستشعر
        Aggregate data by sensor type

        Args:
            sensor_type: نوع المستشعر - Sensor type
            time_range: الفترة الزمنية - Time range
            readings: قائمة القراءات - List of readings
            granularity: دقة الوقت - Time granularity

        Returns:
            قاموس البيانات المجمعة حسب الحقل - Dictionary of aggregated data by field
        """
        # تصفية القراءات حسب النوع - Filter readings by type
        type_readings = [
            r for r in readings if r.sensor_type.lower() == sensor_type.lower()
        ]

        # تجميع حسب الحقل - Group by field
        by_field = defaultdict(list)
        for reading in type_readings:
            by_field[reading.field_id].append(reading)

        # حساب التجميع لكل حقل - Calculate aggregation for each field
        aggregated = {}
        for field_id, field_readings in by_field.items():
            agg_data = self._aggregate_readings(
                field_id=field_id,
                sensor_type=sensor_type,
                time_range=time_range,
                readings=field_readings,
                granularity=granularity,
            )
            aggregated[field_id] = agg_data

        return aggregated

    def _aggregate_readings(
        self,
        field_id: str,
        sensor_type: str,
        time_range: tuple[datetime, datetime],
        readings: list[SensorReading],
        granularity: TimeGranularity,
    ) -> AggregatedData:
        """
        تجميع القراءات وحساب الإحصائيات
        Aggregate readings and calculate statistics

        Returns:
            البيانات المجمعة - Aggregated data
        """
        if not readings:
            return AggregatedData(
                field_id=field_id,
                sensor_type=sensor_type,
                time_range_start=time_range[0].isoformat(),
                time_range_end=time_range[1].isoformat(),
                granularity=granularity,
                count=0,
            )

        # استخراج القيم - Extract values
        values = [r.value for r in readings]
        devices = list({r.device_id for r in readings})

        # حساب الإحصائيات - Calculate statistics
        stats = self.calculate_statistics(values)

        # اكتشاف القيم الشاذة - Detect outliers
        outliers = self.detect_outliers(readings, method="zscore")
        outlier_count = len(outliers)

        # حساب معدل التغيير - Calculate rate of change
        rate_of_change = self._calculate_rate_of_change(readings)

        # حساب المجموع التراكمي (للأمطار) - Calculate cumulative sum (for rainfall)
        cumulative_sum = None
        if sensor_type.lower() in ["rainfall", "rain", "precipitation"]:
            cumulative_sum = sum(values)

        # حساب جودة البيانات - Calculate data quality
        quality_score = self.calculate_data_quality_score(readings)

        return AggregatedData(
            field_id=field_id,
            sensor_type=sensor_type,
            time_range_start=time_range[0].isoformat(),
            time_range_end=time_range[1].isoformat(),
            granularity=granularity,
            mean=stats["mean"],
            median=stats["median"],
            min=stats["min"],
            max=stats["max"],
            std=stats["std"],
            count=len(values),
            percentile_10=stats["p10"],
            percentile_25=stats["p25"],
            percentile_75=stats["p75"],
            percentile_90=stats["p90"],
            rate_of_change=rate_of_change,
            cumulative_sum=cumulative_sum,
            data_quality_score=quality_score,
            outlier_count=outlier_count,
            devices=devices,
        )

    def calculate_statistics(self, readings: list[float]) -> dict[str, float | None]:
        """
        حساب الإحصائيات الأساسية
        Calculate basic statistics

        Args:
            readings: قائمة القيم - List of values

        Returns:
            قاموس الإحصائيات - Statistics dictionary
        """
        if not readings:
            return {
                "mean": None,
                "median": None,
                "min": None,
                "max": None,
                "std": None,
                "p10": None,
                "p25": None,
                "p75": None,
                "p90": None,
            }

        # الإحصائيات الأساسية - Basic statistics
        mean_val = statistics.mean(readings)
        median_val = statistics.median(readings)
        min_val = min(readings)
        max_val = max(readings)

        # الانحراف المعياري - Standard deviation
        std_val = statistics.stdev(readings) if len(readings) > 1 else 0.0

        # المئينات - Percentiles
        sorted_readings = sorted(readings)
        len(sorted_readings)

        p10 = self._percentile(sorted_readings, 10)
        p25 = self._percentile(sorted_readings, 25)
        p75 = self._percentile(sorted_readings, 75)
        p90 = self._percentile(sorted_readings, 90)

        return {
            "mean": round(mean_val, 2),
            "median": round(median_val, 2),
            "min": round(min_val, 2),
            "max": round(max_val, 2),
            "std": round(std_val, 2),
            "p10": round(p10, 2),
            "p25": round(p25, 2),
            "p75": round(p75, 2),
            "p90": round(p90, 2),
        }

    def _percentile(self, sorted_values: list[float], percentile: int) -> float:
        """
        حساب المئين
        Calculate percentile

        Args:
            sorted_values: القيم المرتبة - Sorted values
            percentile: المئين المطلوب (0-100) - Desired percentile (0-100)

        Returns:
            قيمة المئين - Percentile value
        """
        if not sorted_values:
            return 0.0

        k = (len(sorted_values) - 1) * percentile / 100
        f = int(k)
        c = f + 1 if f + 1 < len(sorted_values) else f
        d0 = sorted_values[f]
        d1 = sorted_values[c]
        return d0 + (d1 - d0) * (k - f)

    def detect_outliers(
        self,
        readings: list[SensorReading],
        method: str = "zscore",
        threshold: float = 3.0,
    ) -> list[SensorReading]:
        """
        اكتشاف القيم الشاذة
        Detect outliers in readings

        Args:
            readings: قائمة القراءات - List of readings
            method: الطريقة ('zscore', 'iqr', 'threshold') - Method
            threshold: العتبة - Threshold (for zscore: std deviations, for iqr: multiplier)

        Returns:
            قائمة القراءات الشاذة - List of outlier readings
        """
        if not readings or len(readings) < 3:
            return []

        values = [r.value for r in readings]

        if method == "zscore":
            return self._detect_outliers_zscore(readings, values, threshold)
        elif method == "iqr":
            return self._detect_outliers_iqr(readings, values, threshold)
        elif method == "threshold":
            return self._detect_outliers_threshold(readings)
        else:
            return self._detect_outliers_zscore(readings, values, threshold)

    def _detect_outliers_zscore(
        self, readings: list[SensorReading], values: list[float], threshold: float
    ) -> list[SensorReading]:
        """
        اكتشاف القيم الشاذة باستخدام Z-Score
        Detect outliers using Z-Score method
        """
        if len(values) < 2:
            return []

        mean = statistics.mean(values)
        std = statistics.stdev(values)

        if std == 0:
            return []

        outliers = []
        for reading in readings:
            z_score = abs((reading.value - mean) / std)
            if z_score > threshold:
                reading.is_outlier = True
                outliers.append(reading)

        return outliers

    def _detect_outliers_iqr(
        self, readings: list[SensorReading], values: list[float], multiplier: float
    ) -> list[SensorReading]:
        """
        اكتشاف القيم الشاذة باستخدام IQR (Interquartile Range)
        Detect outliers using IQR method
        """
        sorted_values = sorted(values)
        q1 = self._percentile(sorted_values, 25)
        q3 = self._percentile(sorted_values, 75)
        iqr = q3 - q1

        lower_bound = q1 - multiplier * iqr
        upper_bound = q3 + multiplier * iqr

        outliers = []
        for reading in readings:
            if reading.value < lower_bound or reading.value > upper_bound:
                reading.is_outlier = True
                outliers.append(reading)

        return outliers

    def _detect_outliers_threshold(
        self, readings: list[SensorReading]
    ) -> list[SensorReading]:
        """
        اكتشاف القيم الشاذة باستخدام عتبات اليمن
        Detect outliers using Yemen-specific thresholds
        """
        outliers = []
        for reading in readings:
            is_valid, severity = check_value_in_range(
                reading.sensor_type, reading.value
            )
            if not is_valid:
                reading.is_outlier = True
                outliers.append(reading)

        return outliers

    def _calculate_rate_of_change(self, readings: list[SensorReading]) -> float | None:
        """
        حساب معدل التغيير
        Calculate rate of change (units per hour)

        Args:
            readings: قائمة القراءات - List of readings

        Returns:
            معدل التغيير (وحدة/ساعة) - Rate of change (units/hour)
        """
        if len(readings) < 2:
            return None

        # ترتيب القراءات حسب الوقت - Sort by timestamp
        sorted_readings = sorted(
            readings, key=lambda r: datetime.fromisoformat(r.timestamp)
        )

        first = sorted_readings[0]
        last = sorted_readings[-1]

        # حساب الفرق في الوقت (بالساعات) - Calculate time difference (in hours)
        time1 = datetime.fromisoformat(first.timestamp)
        time2 = datetime.fromisoformat(last.timestamp)
        hours_diff = (time2 - time1).total_seconds() / 3600

        if hours_diff == 0:
            return None

        # حساب معدل التغيير - Calculate rate of change
        value_diff = last.value - first.value
        rate = value_diff / hours_diff

        return round(rate, 4)

    # ============ Time-based Aggregations ============

    def hourly_average(
        self, readings: list[SensorReading]
    ) -> dict[str, AggregatedData]:
        """
        المتوسط الساعي
        Calculate hourly averages

        Args:
            readings: قائمة القراءات - List of readings

        Returns:
            قاموس المتوسطات الساعية - Dictionary of hourly averages
        """
        return self._time_based_aggregation(readings, TimeGranularity.HOURLY)

    def daily_summary(self, readings: list[SensorReading]) -> dict[str, AggregatedData]:
        """
        الملخص اليومي
        Calculate daily summaries

        Args:
            readings: قائمة القراءات - List of readings

        Returns:
            قاموس الملخصات اليومية - Dictionary of daily summaries
        """
        return self._time_based_aggregation(readings, TimeGranularity.DAILY)

    def weekly_trend(self, readings: list[SensorReading]) -> dict[str, AggregatedData]:
        """
        الاتجاه الأسبوعي
        Calculate weekly trends

        Args:
            readings: قائمة القراءات - List of readings

        Returns:
            قاموس الاتجاهات الأسبوعية - Dictionary of weekly trends
        """
        return self._time_based_aggregation(readings, TimeGranularity.WEEKLY)

    def monthly_report(
        self, readings: list[SensorReading]
    ) -> dict[str, AggregatedData]:
        """
        التقرير الشهري
        Calculate monthly reports

        Args:
            readings: قائمة القراءات - List of readings

        Returns:
            قاموس التقارير الشهرية - Dictionary of monthly reports
        """
        return self._time_based_aggregation(readings, TimeGranularity.MONTHLY)

    def _time_based_aggregation(
        self, readings: list[SensorReading], granularity: TimeGranularity
    ) -> dict[str, AggregatedData]:
        """
        تجميع حسب الوقت
        Time-based aggregation helper

        Returns:
            قاموس البيانات المجمعة حسب الفترة الزمنية
            Dictionary of aggregated data by time period
        """
        if not readings:
            return {}

        # تجميع القراءات حسب الفترات الزمنية - Group readings by time periods
        time_buckets = defaultdict(list)

        for reading in readings:
            timestamp = datetime.fromisoformat(reading.timestamp)
            bucket_key = self._get_time_bucket_key(timestamp, granularity)
            time_buckets[bucket_key].append(reading)

        # حساب التجميع لكل فترة - Calculate aggregation for each period
        aggregated = {}
        for bucket_key, bucket_readings in time_buckets.items():
            # الحصول على نطاق الوقت - Get time range
            time_range = self._get_time_range_from_bucket(bucket_key, granularity)

            # افترض نفس field_id و sensor_type - Assume same field and sensor type
            field_id = bucket_readings[0].field_id
            sensor_type = bucket_readings[0].sensor_type

            agg_data = self._aggregate_readings(
                field_id=field_id,
                sensor_type=sensor_type,
                time_range=time_range,
                readings=bucket_readings,
                granularity=granularity,
            )
            aggregated[bucket_key] = agg_data

        return aggregated

    def _get_time_bucket_key(
        self, timestamp: datetime, granularity: TimeGranularity
    ) -> str:
        """
        الحصول على مفتاح الفترة الزمنية
        Get time bucket key for grouping
        """
        if granularity == TimeGranularity.HOURLY:
            return timestamp.strftime("%Y-%m-%d %H:00")
        elif granularity == TimeGranularity.DAILY:
            return timestamp.strftime("%Y-%m-%d")
        elif granularity == TimeGranularity.WEEKLY:
            # ISO week number
            year, week, _ = timestamp.isocalendar()
            return f"{year}-W{week:02d}"
        elif granularity == TimeGranularity.MONTHLY:
            return timestamp.strftime("%Y-%m")
        else:
            return timestamp.isoformat()

    def _get_time_range_from_bucket(
        self, bucket_key: str, granularity: TimeGranularity
    ) -> tuple[datetime, datetime]:
        """
        الحصول على نطاق الوقت من مفتاح الفترة
        Get time range from bucket key
        """
        if granularity == TimeGranularity.HOURLY:
            start = datetime.strptime(bucket_key, "%Y-%m-%d %H:%M")
            end = start + timedelta(hours=1)
        elif granularity == TimeGranularity.DAILY:
            start = datetime.strptime(bucket_key, "%Y-%m-%d")
            end = start + timedelta(days=1)
        elif granularity == TimeGranularity.WEEKLY:
            year, week = bucket_key.split("-W")
            start = datetime.strptime(f"{year}-W{week}-1", "%Y-W%W-%w")
            end = start + timedelta(weeks=1)
        elif granularity == TimeGranularity.MONTHLY:
            start = datetime.strptime(bucket_key, "%Y-%m")
            # نهاية الشهر - End of month
            if start.month == 12:
                end = datetime(start.year + 1, 1, 1)
            else:
                end = datetime(start.year, start.month + 1, 1)
        else:
            start = datetime.now(UTC)
            end = start

        return (start, end)

    # ============ Sensor Health Monitoring ============

    def check_sensor_status(
        self,
        device_id: str,
        readings: list[SensorReading],
        expected_interval_minutes: int = 15,
    ) -> SensorHealth:
        """
        فحص حالة المستشعر
        Check sensor health status

        Args:
            device_id: معرف الجهاز - Device ID
            readings: قراءات آخر 24 ساعة - Readings from last 24 hours
            expected_interval_minutes: الفترة المتوقعة بين القراءات (بالدقائق)
                                      Expected interval between readings (minutes)

        Returns:
            صحة المستشعر - Sensor health information
        """
        if not readings:
            return SensorHealth(
                device_id=device_id,
                field_id="unknown",
                sensor_type="unknown",
                status=SensorStatus.OFFLINE,
                timestamp=datetime.now(UTC).isoformat(),
                data_quality_score=0.0,
                alerts=["لا توجد قراءات - No readings available"],
            )

        # استخراج المعلومات الأساسية - Extract basic info
        field_id = readings[0].field_id
        sensor_type = readings[0].sensor_type

        # حساب جودة البيانات - Calculate data quality
        quality_score = self.calculate_data_quality_score(readings)

        # حساب نسبة وقت التشغيل - Calculate uptime
        expected_readings = (24 * 60) // expected_interval_minutes
        uptime_percentage = min(100.0, (len(readings) / expected_readings) * 100)

        # اكتشاف الانحراف - Detect drift
        drift_detected, drift_magnitude = self.detect_sensor_drift(readings)

        # اكتشاف القيم الشاذة - Detect outliers
        outliers = self.detect_outliers(readings, method="threshold")
        outlier_percentage = (len(outliers) / len(readings)) * 100 if readings else 0

        # تحديد الحالة - Determine status
        status = self._determine_sensor_status(
            quality_score, uptime_percentage, drift_detected, outlier_percentage
        )

        # جمع التنبيهات والتوصيات - Collect alerts and recommendations
        alerts, recommendations_ar, recommendations_en = (
            self._generate_alerts_and_recommendations(
                status,
                quality_score,
                uptime_percentage,
                drift_detected,
                outlier_percentage,
                sensor_type,
            )
        )

        # آخر قراءة ناجحة - Last successful reading
        sorted_readings = sorted(
            readings, key=lambda r: datetime.fromisoformat(r.timestamp), reverse=True
        )
        last_successful = sorted_readings[0].timestamp if sorted_readings else None

        # استخراج معلومات البطارية والإشارة - Extract battery and signal info
        battery_level = None
        signal_strength = None
        if sorted_readings and sorted_readings[0].metadata:
            battery_level = sorted_readings[0].metadata.get("battery")
            signal_strength = sorted_readings[0].metadata.get("rssi")

        return SensorHealth(
            device_id=device_id,
            field_id=field_id,
            sensor_type=sensor_type,
            status=status,
            timestamp=datetime.now(UTC).isoformat(),
            data_quality_score=round(quality_score, 2),
            uptime_percentage=round(uptime_percentage, 2),
            battery_level=battery_level,
            signal_strength=signal_strength,
            drift_detected=drift_detected,
            drift_magnitude=drift_magnitude,
            readings_count_24h=len(readings),
            expected_readings_24h=expected_readings,
            outlier_percentage=round(outlier_percentage, 2),
            last_successful_reading=last_successful,
            alerts=alerts,
            recommendations_ar=recommendations_ar,
            recommendations_en=recommendations_en,
        )

    def detect_sensor_drift(
        self, readings: list[SensorReading], window_size: int = 10
    ) -> tuple[bool, float | None]:
        """
        اكتشاف انحراف المستشعر
        Detect sensor drift (gradual degradation)

        Args:
            readings: قائمة القراءات - List of readings
            window_size: حجم النافذة للمقارنة - Window size for comparison

        Returns:
            (drift_detected, drift_magnitude)
        """
        if len(readings) < window_size * 2:
            return False, None

        # ترتيب القراءات حسب الوقت - Sort by timestamp
        sorted_readings = sorted(
            readings, key=lambda r: datetime.fromisoformat(r.timestamp)
        )

        # مقارنة النوافذ الأولى والأخيرة - Compare first and last windows
        first_window = [r.value for r in sorted_readings[:window_size]]
        last_window = [r.value for r in sorted_readings[-window_size:]]

        first_mean = statistics.mean(first_window)
        last_mean = statistics.mean(last_window)

        # حساب الانحراف النسبي - Calculate relative drift
        if first_mean == 0:
            return False, None

        drift_percentage = abs((last_mean - first_mean) / first_mean) * 100

        # عتبة الانحراف: 20% - Drift threshold: 20%
        drift_detected = drift_percentage > 20.0

        return drift_detected, round(drift_percentage, 2) if drift_detected else None

    def calculate_data_quality_score(self, readings: list[SensorReading]) -> float:
        """
        حساب نقاط جودة البيانات
        Calculate data quality score (0-100)

        العوامل:
        Factors:
        - اكتمال البيانات (50%) - Data completeness
        - دقة البيانات (30%) - Data accuracy (outliers)
        - توقيت البيانات (20%) - Data timeliness

        Args:
            readings: قائمة القراءات - List of readings

        Returns:
            نقاط الجودة (0-100) - Quality score (0-100)
        """
        if not readings:
            return 0.0

        # 1. اكتمال البيانات - Data completeness (50 points)
        # افترض قراءة كل 15 دقيقة في 24 ساعة = 96 قراءة
        # Assume reading every 15 minutes in 24 hours = 96 readings
        expected_count = 96
        completeness_score = min(50.0, (len(readings) / expected_count) * 50)

        # 2. دقة البيانات - Data accuracy (30 points)
        # على أساس نسبة القيم الشاذة - Based on outlier percentage
        outliers = self.detect_outliers(readings, method="threshold")
        outlier_ratio = len(outliers) / len(readings) if readings else 0
        accuracy_score = max(0.0, 30.0 * (1 - outlier_ratio))

        # 3. توقيت البيانات - Data timeliness (20 points)
        # على أساس حداثة آخر قراءة - Based on recency of last reading
        sorted_readings = sorted(
            readings, key=lambda r: datetime.fromisoformat(r.timestamp), reverse=True
        )
        last_reading_time = datetime.fromisoformat(sorted_readings[0].timestamp)
        now = datetime.now(UTC)

        # إذا كانت آخر قراءة أحدث من ساعة، نقاط كاملة
        # If last reading is within 1 hour, full points
        hours_since_last = (now - last_reading_time).total_seconds() / 3600
        if hours_since_last <= 1:
            timeliness_score = 20.0
        elif hours_since_last <= 6:
            timeliness_score = 15.0
        elif hours_since_last <= 24:
            timeliness_score = 10.0
        else:
            timeliness_score = 0.0

        total_score = completeness_score + accuracy_score + timeliness_score
        return min(100.0, total_score)

    def _determine_sensor_status(
        self,
        quality_score: float,
        uptime_percentage: float,
        drift_detected: bool,
        outlier_percentage: float,
    ) -> SensorStatus:
        """
        تحديد حالة المستشعر
        Determine sensor status based on metrics
        """
        # حرج - Critical
        if quality_score < 30 or uptime_percentage < 50:
            return SensorStatus.CRITICAL

        # انحراف مكتشف - Drift detected
        if drift_detected:
            return SensorStatus.DRIFT_DETECTED

        # تحذير - Warning
        if quality_score < 60 or uptime_percentage < 80 or outlier_percentage > 10:
            return SensorStatus.WARNING

        # سليم - Healthy
        return SensorStatus.HEALTHY

    def _generate_alerts_and_recommendations(
        self,
        status: SensorStatus,
        quality_score: float,
        uptime_percentage: float,
        drift_detected: bool,
        outlier_percentage: float,
        sensor_type: str,
    ) -> tuple[list[str], list[str], list[str]]:
        """
        توليد التنبيهات والتوصيات
        Generate alerts and recommendations
        """
        alerts = []
        recommendations_ar = []
        recommendations_en = []

        if status == SensorStatus.CRITICAL:
            alerts.append("حالة حرجة - Critical status")
            if quality_score < 30:
                recommendations_ar.append("جودة البيانات منخفضة جداً - تحقق من المستشعر")
                recommendations_en.append("Data quality very low - Check sensor")
            if uptime_percentage < 50:
                recommendations_ar.append(
                    "المستشعر غير متصل بشكل متكرر - تحقق من الاتصال"
                )
                recommendations_en.append(
                    "Sensor frequently offline - Check connectivity"
                )

        if drift_detected:
            alerts.append("انحراف مكتشف - Drift detected")
            recommendations_ar.append(
                "المستشعر يظهر انحرافاً تدريجياً - قد يحتاج إلى معايرة"
            )
            recommendations_en.append(
                "Sensor showing gradual drift - May need calibration"
            )

        if outlier_percentage > 10:
            alerts.append(f"نسبة عالية من القيم الشاذة: {outlier_percentage:.1f}%")
            recommendations_ar.append("قيم شاذة كثيرة - تحقق من موقع التثبيت")
            recommendations_en.append("Many outliers - Check installation location")

        if uptime_percentage < 80:
            alerts.append(f"وقت التشغيل منخفض: {uptime_percentage:.1f}%")
            recommendations_ar.append("قراءات متقطعة - تحقق من البطارية والإشارة")
            recommendations_en.append(
                "Intermittent readings - Check battery and signal"
            )

        # توصيات خاصة بنوع المستشعر - Sensor-type specific recommendations
        threshold = get_threshold(sensor_type)
        if threshold:
            recommendations_ar.append(
                f"النطاق الموصى به: {threshold.min_value}-{threshold.max_value} {threshold.unit}"
            )
            recommendations_en.append(
                f"Recommended range: {threshold.min_value}-{threshold.max_value} {threshold.unit}"
            )

        if not alerts:
            alerts.append("لا توجد تنبيهات - No alerts")
            recommendations_ar.append("المستشعر يعمل بشكل طبيعي")
            recommendations_en.append("Sensor operating normally")

        return alerts, recommendations_ar, recommendations_en


# ============ Utility Functions ============


def create_sample_readings(
    device_id: str,
    field_id: str,
    sensor_type: str,
    count: int = 96,
    base_value: float = 25.0,
    noise: float = 2.0,
) -> list[SensorReading]:
    """
    إنشاء قراءات تجريبية للاختبار
    Create sample readings for testing

    Args:
        device_id: معرف الجهاز
        field_id: معرف الحقل
        sensor_type: نوع المستشعر
        count: عدد القراءات
        base_value: القيمة الأساسية
        noise: مستوى الضوضاء

    Returns:
        قائمة القراءات التجريبية
    """
    import random

    readings = []
    start_time = datetime.now(UTC) - timedelta(hours=24)

    for i in range(count):
        timestamp = start_time + timedelta(minutes=15 * i)
        value = base_value + random.uniform(-noise, noise)

        reading = SensorReading(
            device_id=device_id,
            field_id=field_id,
            sensor_type=sensor_type,
            value=round(value, 2),
            unit="°C",
            timestamp=timestamp.isoformat(),
            metadata={
                "battery": random.randint(80, 100),
                "rssi": random.randint(-80, -50),
            },
        )
        readings.append(reading)

    return readings
