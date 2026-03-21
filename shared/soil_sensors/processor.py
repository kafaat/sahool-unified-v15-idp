"""
Sensor Data Processor - معالج بيانات المجسات
Data aggregation, anomaly detection, and field interpolation
"""

from __future__ import annotations

import math
import uuid
from collections import defaultdict
from datetime import UTC, datetime, timedelta

from .models import (
    AlertSeverity,
    FieldMoistureMap,
    SensorAggregation,
    SensorAlert,
    SensorReading,
    SensorType,
    SoilSensor,
)


class SensorDataProcessor:
    """
    Process sensor readings for a field
    معالج قراءات المجسات للحقل
    """

    def __init__(self, field_id: str, tenant_id: str):
        self.field_id = field_id
        self.tenant_id = tenant_id
        self._readings: dict[str, list[SensorReading]] = defaultdict(list)
        self._sensors: dict[str, SoilSensor] = {}
        self._max_readings = 1000  # Per sensor

    def register_sensor(self, sensor: SoilSensor):
        """Register sensor for processing"""
        self._sensors[sensor.id] = sensor

    def add_reading(self, reading: SensorReading) -> list[SensorAlert]:
        """
        Add reading and check for alerts
        إضافة قراءة والتحقق من التنبيهات
        """
        alerts = []

        # Validate reading
        if not reading.is_valid:
            return alerts

        # Apply calibration if available
        sensor = self._sensors.get(reading.sensor_id)
        if sensor and sensor.calibration:
            reading.value = sensor.calibration.apply_calibration(reading.value)

        # Store reading
        self._readings[reading.sensor_id].append(reading)

        # Trim old readings
        if len(self._readings[reading.sensor_id]) > self._max_readings:
            self._readings[reading.sensor_id] = self._readings[reading.sensor_id][-self._max_readings :]

        # Check thresholds
        if sensor:
            threshold_alert = self._check_thresholds(reading, sensor)
            if threshold_alert:
                alerts.append(threshold_alert)

        # Check for anomalies
        anomaly_alert = self._check_anomaly(reading)
        if anomaly_alert:
            alerts.append(anomaly_alert)

        return alerts

    def _check_thresholds(self, reading: SensorReading, sensor: SoilSensor) -> SensorAlert | None:
        """Check if reading exceeds thresholds"""
        value = reading.value

        # Critical thresholds
        if sensor.critical_min is not None and value < sensor.critical_min:
            return self._create_threshold_alert(
                reading,
                sensor,
                "critical_low",
                f"Critical low: {value:.1f}% (min: {sensor.critical_min}%)",
                AlertSeverity.CRITICAL,
            )

        if sensor.critical_max is not None and value > sensor.critical_max:
            return self._create_threshold_alert(
                reading,
                sensor,
                "critical_high",
                f"Critical high: {value:.1f}% (max: {sensor.critical_max}%)",
                AlertSeverity.CRITICAL,
            )

        # Warning thresholds
        if sensor.min_threshold is not None and value < sensor.min_threshold:
            return self._create_threshold_alert(
                reading,
                sensor,
                "low_moisture",
                f"Low moisture: {value:.1f}% (threshold: {sensor.min_threshold}%)",
                AlertSeverity.HIGH,
            )

        if sensor.max_threshold is not None and value > sensor.max_threshold:
            return self._create_threshold_alert(
                reading,
                sensor,
                "high_moisture",
                f"High moisture: {value:.1f}% (threshold: {sensor.max_threshold}%)",
                AlertSeverity.MEDIUM,
            )

        return None

    def _create_threshold_alert(
        self,
        reading: SensorReading,
        sensor: SoilSensor,
        alert_type: str,
        message: str,
        severity: AlertSeverity,
    ) -> SensorAlert:
        """Create threshold alert"""
        alert_messages = {
            "critical_low": {
                "title_en": "🚨 Critical Low Soil Moisture",
                "title_ar": "🚨 رطوبة تربة حرجة منخفضة",
                "message_ar": f"رطوبة حرجة منخفضة: {reading.value:.1f}% في {sensor.name_ar}",
            },
            "critical_high": {
                "title_en": "🚨 Critical High Soil Moisture",
                "title_ar": "🚨 رطوبة تربة حرجة مرتفعة",
                "message_ar": f"رطوبة حرجة مرتفعة: {reading.value:.1f}% في {sensor.name_ar}",
            },
            "low_moisture": {
                "title_en": "⚠️ Low Soil Moisture",
                "title_ar": "⚠️ رطوبة تربة منخفضة",
                "message_ar": f"رطوبة منخفضة: {reading.value:.1f}% في {sensor.name_ar} - يحتاج ري",
            },
            "high_moisture": {
                "title_en": "💧 High Soil Moisture",
                "title_ar": "💧 رطوبة تربة مرتفعة",
                "message_ar": f"رطوبة مرتفعة: {reading.value:.1f}% في {sensor.name_ar} - تأجيل الري",
            },
        }

        msgs = alert_messages.get(alert_type, {})

        return SensorAlert(
            alert_id=f"sensor_{uuid.uuid4().hex[:8]}",
            sensor_id=sensor.id,
            field_id=self.field_id,
            tenant_id=self.tenant_id,
            timestamp=reading.timestamp,
            alert_type=alert_type,
            severity=severity,
            reading_value=reading.value,
            reading_unit=reading.unit,
            threshold_value=sensor.min_threshold if "low" in alert_type else sensor.max_threshold,
            title_en=msgs.get("title_en", "Sensor Alert"),
            title_ar=msgs.get("title_ar", "تنبيه مجس"),
            message_en=message,
            message_ar=msgs.get("message_ar", message),
        )

    def _check_anomaly(self, reading: SensorReading) -> SensorAlert | None:
        """
        Check for anomalous reading using statistical analysis
        التحقق من القراءة الشاذة باستخدام التحليل الإحصائي
        """
        sensor_readings = self._readings.get(reading.sensor_id, [])

        if len(sensor_readings) < 10:
            return None  # Not enough data

        # Get recent readings (last 24 hours)
        cutoff = datetime.now(UTC) - timedelta(hours=24)
        recent = [r for r in sensor_readings if r.timestamp > cutoff]

        if len(recent) < 5:
            return None

        # Calculate statistics
        values = [r.value for r in recent[:-1]]  # Exclude current reading
        avg = sum(values) / len(values)
        variance = sum((v - avg) ** 2 for v in values) / len(values)
        std = math.sqrt(variance) if variance > 0 else 0.1

        # Check if current reading is anomalous (> 3 std deviations)
        z_score = abs(reading.value - avg) / std if std > 0 else 0

        if z_score > 3:
            self._sensors.get(reading.sensor_id)
            return SensorAlert(
                alert_id=f"anomaly_{uuid.uuid4().hex[:8]}",
                sensor_id=reading.sensor_id,
                field_id=self.field_id,
                tenant_id=self.tenant_id,
                timestamp=reading.timestamp,
                alert_type="anomaly_detected",
                severity=AlertSeverity.MEDIUM,
                reading_value=reading.value,
                reading_unit=reading.unit,
                title_en="⚠️ Unusual Sensor Reading",
                title_ar="⚠️ قراءة مجس غير عادية",
                message_en=f"Unusual reading: {reading.value:.1f}% (expected: {avg:.1f}% ± {std:.1f}%)",
                message_ar=f"قراءة غير عادية: {reading.value:.1f}% (المتوقع: {avg:.1f}% ± {std:.1f}%)",
            )

        return None

    def get_latest_readings(self, sensor_id: str | None = None) -> dict[str, SensorReading]:
        """Get latest reading from each sensor"""
        result = {}

        sensors = [sensor_id] if sensor_id else self._readings.keys()

        for sid in sensors:
            readings = self._readings.get(sid, [])
            if readings:
                result[sid] = readings[-1]

        return result

    def get_aggregation(self, sensor_id: str, period_hours: int = 24) -> SensorAggregation | None:
        """
        Get aggregated readings for time period
        الحصول على القراءات المجمعة لفترة زمنية
        """
        readings = self._readings.get(sensor_id, [])
        if not readings:
            return None

        cutoff = datetime.now(UTC) - timedelta(hours=period_hours)
        period_readings = [r for r in readings if r.timestamp > cutoff]

        if not period_readings:
            return None

        values = [r.value for r in period_readings if r.is_valid]
        valid_count = len(values)
        invalid_count = len(period_readings) - valid_count

        if not values:
            return None

        avg_val = sum(values) / len(values)
        min_val = min(values)
        max_val = max(values)
        variance = sum((v - avg_val) ** 2 for v in values) / len(values)
        std_val = math.sqrt(variance)

        # Calculate trend
        if len(values) >= 2:
            first_half = values[: len(values) // 2]
            second_half = values[len(values) // 2 :]
            first_avg = sum(first_half) / len(first_half)
            second_avg = sum(second_half) / len(second_half)

            diff = second_avg - first_avg
            trend_rate = diff / period_hours

            if diff > std_val:
                trend = "increasing"
            elif diff < -std_val:
                trend = "decreasing"
            else:
                trend = "stable"
        else:
            trend = "stable"
            trend_rate = 0.0

        sensor = self._sensors.get(sensor_id)

        return SensorAggregation(
            sensor_id=sensor_id,
            field_id=self.field_id,
            period_start=period_readings[0].timestamp,
            period_end=period_readings[-1].timestamp,
            reading_type=sensor.sensor_type if sensor else SensorType.MOISTURE,
            count=len(period_readings),
            avg_value=avg_val,
            min_value=min_val,
            max_value=max_val,
            std_value=std_val,
            trend=trend,
            trend_rate=trend_rate,
            valid_readings=valid_count,
            invalid_readings=invalid_count,
        )


def aggregate_readings(readings: list[SensorReading], interval_minutes: int = 60) -> list[SensorAggregation]:
    """
    Aggregate readings into time intervals
    تجميع القراءات في فترات زمنية
    """
    if not readings:
        return []

    # Group by interval
    intervals: dict[datetime, list[SensorReading]] = defaultdict(list)

    for reading in readings:
        # Round to interval
        interval_start = reading.timestamp.replace(
            minute=(reading.timestamp.minute // interval_minutes) * interval_minutes,
            second=0,
            microsecond=0,
        )
        intervals[interval_start].append(reading)

    # Aggregate each interval
    aggregations = []
    for interval_start, interval_readings in sorted(intervals.items()):
        values = [r.value for r in interval_readings if r.is_valid]
        if not values:
            continue

        avg_val = sum(values) / len(values)
        min_val = min(values)
        max_val = max(values)
        variance = sum((v - avg_val) ** 2 for v in values) / len(values)

        aggregations.append(
            SensorAggregation(
                sensor_id=interval_readings[0].sensor_id,
                field_id="",  # Set by caller
                period_start=interval_start,
                period_end=interval_start + timedelta(minutes=interval_minutes),
                reading_type=interval_readings[0].reading_type,
                count=len(interval_readings),
                avg_value=avg_val,
                min_value=min_val,
                max_value=max_val,
                std_value=math.sqrt(variance),
                valid_readings=len(values),
                invalid_readings=len(interval_readings) - len(values),
            )
        )

    return aggregations


def detect_anomalies(readings: list[SensorReading], threshold_std: float = 3.0) -> list[SensorReading]:
    """
    Detect anomalous readings using statistical analysis
    اكتشاف القراءات الشاذة باستخدام التحليل الإحصائي
    """
    if len(readings) < 10:
        return []

    values = [r.value for r in readings if r.is_valid]
    if len(values) < 10:
        return []

    avg = sum(values) / len(values)
    variance = sum((v - avg) ** 2 for v in values) / len(values)
    std = math.sqrt(variance)

    if std < 0.1:
        std = 0.1  # Prevent division by zero

    anomalies = []
    for reading in readings:
        if reading.is_valid:
            z_score = abs(reading.value - avg) / std
            if z_score > threshold_std:
                anomalies.append(reading)

    return anomalies


def interpolate_field_moisture(
    sensors: list[SoilSensor],
    readings: dict[str, SensorReading],
    field_bounds: tuple[float, float, float, float],  # min_lat, max_lat, min_lng, max_lng
    resolution_m: float = 10.0,
) -> FieldMoistureMap:
    """
    Interpolate soil moisture across field using IDW
    استيفاء رطوبة التربة عبر الحقل باستخدام IDW

    Uses Inverse Distance Weighting interpolation
    """
    min_lat, max_lat, min_lng, max_lng = field_bounds

    # Approximate grid size
    lat_range = max_lat - min_lat
    lng_range = max_lng - min_lng

    # Approximate meters per degree at this latitude
    meters_per_degree_lat = 111320
    meters_per_degree_lng = 111320 * math.cos(math.radians((min_lat + max_lat) / 2))

    # Grid dimensions
    n_rows = max(1, int((lat_range * meters_per_degree_lat) / resolution_m))
    n_cols = max(1, int((lng_range * meters_per_degree_lng) / resolution_m))

    # Limit grid size
    n_rows = min(n_rows, 100)
    n_cols = min(n_cols, 100)

    # Get sensor points with readings
    points = []
    for sensor in sensors:
        if sensor.id in readings and readings[sensor.id].is_valid:
            points.append(
                {
                    "lat": sensor.lat,
                    "lng": sensor.lng,
                    "value": readings[sensor.id].value,
                }
            )

    if not points:
        return FieldMoistureMap(
            field_id="",
            timestamp=datetime.now(UTC),
            grid_resolution_m=resolution_m,
            min_lat=min_lat,
            max_lat=max_lat,
            min_lng=min_lng,
            max_lng=max_lng,
            moisture_grid=[],
            sensor_count=0,
        )

    # IDW interpolation
    moisture_grid = []
    all_values = []

    for row in range(n_rows):
        grid_row = []
        lat = min_lat + (row + 0.5) * lat_range / n_rows

        for col in range(n_cols):
            lng = min_lng + (col + 0.5) * lng_range / n_cols

            # Calculate IDW value
            weighted_sum = 0.0
            weight_total = 0.0

            for point in points:
                dist = math.sqrt(
                    ((lat - point["lat"]) * meters_per_degree_lat) ** 2
                    + ((lng - point["lng"]) * meters_per_degree_lng) ** 2
                )

                if dist < 1:
                    dist = 1  # Prevent division by zero

                weight = 1.0 / (dist**2)  # IDW power = 2
                weighted_sum += point["value"] * weight
                weight_total += weight

            value = weighted_sum / weight_total if weight_total > 0 else 0
            grid_row.append(value)
            all_values.append(value)

        moisture_grid.append(grid_row)

    # Calculate statistics
    avg_moisture = sum(all_values) / len(all_values) if all_values else 0
    min_moisture = min(all_values) if all_values else 0
    max_moisture = max(all_values) if all_values else 0
    variance = sum((v - avg_moisture) ** 2 for v in all_values) / len(all_values) if all_values else 0
    std_moisture = math.sqrt(variance)

    # Find dry and wet zones
    dry_zones = []
    wet_zones = []

    dry_threshold = 30  # %
    wet_threshold = 70  # %

    for row in range(n_rows):
        lat = min_lat + (row + 0.5) * lat_range / n_rows
        for col in range(n_cols):
            lng = min_lng + (col + 0.5) * lng_range / n_cols
            value = moisture_grid[row][col]

            if value < dry_threshold:
                dry_zones.append({"lat": lat, "lng": lng, "moisture": value})
            elif value > wet_threshold:
                wet_zones.append({"lat": lat, "lng": lng, "moisture": value})

    return FieldMoistureMap(
        field_id="",  # Set by caller
        timestamp=datetime.now(UTC),
        grid_resolution_m=resolution_m,
        min_lat=min_lat,
        max_lat=max_lat,
        min_lng=min_lng,
        max_lng=max_lng,
        moisture_grid=moisture_grid,
        avg_moisture=avg_moisture,
        min_moisture=min_moisture,
        max_moisture=max_moisture,
        std_moisture=std_moisture,
        sensor_count=len(points),
        interpolation_method="idw",
        dry_zones=dry_zones[:10],  # Limit to top 10
        wet_zones=wet_zones[:10],
    )


def generate_moisture_alert(
    field_id: str,
    tenant_id: str,
    moisture_map: FieldMoistureMap,
) -> SensorAlert | None:
    """
    Generate field-level moisture alert based on interpolated map
    إنشاء تنبيه رطوبة على مستوى الحقل بناءً على الخريطة المستوفاة
    """
    if not moisture_map.moisture_grid:
        return None

    avg = moisture_map.avg_moisture

    # Critical dry
    if avg < 25:
        return SensorAlert(
            alert_id=f"field_moisture_{uuid.uuid4().hex[:8]}",
            sensor_id="field_aggregate",
            field_id=field_id,
            tenant_id=tenant_id,
            timestamp=moisture_map.timestamp,
            alert_type="field_dry_critical",
            severity=AlertSeverity.CRITICAL,
            reading_value=avg,
            reading_unit="%",
            title_en="🚨 Critical: Field Needs Irrigation",
            title_ar="🚨 حرج: الحقل يحتاج ري فوري",
            message_en=f"Average soil moisture is critically low at {avg:.1f}%. "
            f"Immediate irrigation recommended. {len(moisture_map.dry_zones)} dry zones detected.",
            message_ar=f"متوسط رطوبة التربة حرج عند {avg:.1f}%. "
            f"يُنصح بالري الفوري. تم اكتشاف {len(moisture_map.dry_zones)} مناطق جافة.",
        )

    # Warning dry
    if avg < 35:
        return SensorAlert(
            alert_id=f"field_moisture_{uuid.uuid4().hex[:8]}",
            sensor_id="field_aggregate",
            field_id=field_id,
            tenant_id=tenant_id,
            timestamp=moisture_map.timestamp,
            alert_type="field_dry_warning",
            severity=AlertSeverity.HIGH,
            reading_value=avg,
            reading_unit="%",
            title_en="⚠️ Low Soil Moisture - Plan Irrigation",
            title_ar="⚠️ رطوبة تربة منخفضة - خطط للري",
            message_en=f"Average soil moisture is low at {avg:.1f}%. Plan irrigation within 24-48 hours.",
            message_ar=f"متوسط رطوبة التربة منخفض عند {avg:.1f}%. خطط للري خلال 24-48 ساعة.",
        )

    # Waterlogged warning
    if avg > 80:
        return SensorAlert(
            alert_id=f"field_moisture_{uuid.uuid4().hex[:8]}",
            sensor_id="field_aggregate",
            field_id=field_id,
            tenant_id=tenant_id,
            timestamp=moisture_map.timestamp,
            alert_type="field_waterlogged",
            severity=AlertSeverity.MEDIUM,
            reading_value=avg,
            reading_unit="%",
            title_en="💧 High Soil Moisture - Skip Irrigation",
            title_ar="💧 رطوبة تربة مرتفعة - تخطي الري",
            message_en=f"Average soil moisture is high at {avg:.1f}%. "
            f"Skip next irrigation cycle. {len(moisture_map.wet_zones)} waterlogged zones.",
            message_ar=f"متوسط رطوبة التربة مرتفع عند {avg:.1f}%. "
            f"تخطي دورة الري التالية. {len(moisture_map.wet_zones)} مناطق مشبعة.",
        )

    return None
