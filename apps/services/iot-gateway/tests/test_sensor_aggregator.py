"""
اختبارات مجمع بيانات المستشعرات
Tests for Sensor Data Aggregator
"""

import unittest
from datetime import UTC, datetime, timedelta

from apps.services.iot_gateway.src.models.sensor_data import (
    SensorReading,
    SensorStatus,
    TimeGranularity,
)
from apps.services.iot_gateway.src.sensor_aggregator import (
    SensorAggregator,
    create_sample_readings,
)


class TestSensorAggregator(unittest.TestCase):
    """اختبارات المجمع - Aggregator tests"""

    def setUp(self):
        """إعداد الاختبارات - Test setup"""
        self.aggregator = SensorAggregator()
        self.device_id = "device_001"
        self.field_id = "field_123"
        self.sensor_type = "air_temperature"

    def test_calculate_statistics(self):
        """اختبار حساب الإحصائيات - Test statistics calculation"""
        values = [20.0, 22.0, 25.0, 24.0, 23.0, 21.0, 26.0, 28.0, 27.0, 25.0]
        stats = self.aggregator.calculate_statistics(values)

        # التحقق من وجود جميع الإحصائيات - Verify all statistics exist
        self.assertIsNotNone(stats["mean"])
        self.assertIsNotNone(stats["median"])
        self.assertIsNotNone(stats["min"])
        self.assertIsNotNone(stats["max"])
        self.assertIsNotNone(stats["std"])
        self.assertIsNotNone(stats["p10"])
        self.assertIsNotNone(stats["p25"])
        self.assertIsNotNone(stats["p75"])
        self.assertIsNotNone(stats["p90"])

        # التحقق من القيم - Verify values
        self.assertEqual(stats["min"], 20.0)
        self.assertEqual(stats["max"], 28.0)
        self.assertAlmostEqual(stats["mean"], 24.1, places=1)

    def test_detect_outliers_zscore(self):
        """اختبار اكتشاف القيم الشاذة (Z-Score)"""
        # إنشاء قراءات تجريبية مع قيمة شاذة
        # Create sample readings with an outlier
        readings = create_sample_readings(
            self.device_id, self.field_id, self.sensor_type, count=10, base_value=25.0
        )

        # إضافة قيمة شاذة - Add outlier
        outlier = SensorReading(
            device_id=self.device_id,
            field_id=self.field_id,
            sensor_type=self.sensor_type,
            value=100.0,  # قيمة شاذة واضحة
            unit="°C",
            timestamp=datetime.now(UTC).isoformat(),
        )
        readings.append(outlier)

        outliers = self.aggregator.detect_outliers(readings, method="zscore", threshold=2.0)

        # يجب أن يكتشف على الأقل قيمة شاذة واحدة
        # Should detect at least one outlier
        self.assertGreater(len(outliers), 0)
        self.assertTrue(any(r.value == 100.0 for r in outliers))

    def test_detect_outliers_threshold(self):
        """اختبار اكتشاف القيم الشاذة (عتبات اليمن)"""
        # إنشاء قراءة خارج النطاق المقبول
        # Create reading outside acceptable range
        readings = [
            SensorReading(
                device_id=self.device_id,
                field_id=self.field_id,
                sensor_type="air_temperature",
                value=60.0,  # أعلى من الحد الأقصى (45°C)
                unit="°C",
                timestamp=datetime.now(UTC).isoformat(),
            ),
            SensorReading(
                device_id=self.device_id,
                field_id=self.field_id,
                sensor_type="air_temperature",
                value=25.0,  # قيمة طبيعية
                unit="°C",
                timestamp=datetime.now(UTC).isoformat(),
            ),
        ]

        outliers = self.aggregator.detect_outliers(readings, method="threshold")

        # يجب أن يكتشف القيمة 60.0 كقيمة شاذة
        # Should detect 60.0 as outlier
        self.assertEqual(len(outliers), 1)
        self.assertEqual(outliers[0].value, 60.0)

    def test_aggregate_by_field(self):
        """اختبار التجميع حسب الحقل"""
        # إنشاء قراءات متعددة
        readings = create_sample_readings(
            self.device_id, self.field_id, "air_temperature", count=24
        )
        readings.extend(
            create_sample_readings(
                self.device_id, self.field_id, "air_humidity", count=24, base_value=60.0
            )
        )

        time_range = (
            datetime.now(UTC) - timedelta(hours=24),
            datetime.now(UTC),
        )

        aggregated = self.aggregator.aggregate_by_field(
            self.field_id, time_range, readings, TimeGranularity.DAILY
        )

        # يجب أن يكون هناك نوعان من المستشعرات
        # Should have two sensor types
        self.assertEqual(len(aggregated), 2)

        sensor_types = {agg.sensor_type for agg in aggregated}
        self.assertIn("air_temperature", sensor_types)
        self.assertIn("air_humidity", sensor_types)

    def test_aggregate_by_sensor_type(self):
        """اختبار التجميع حسب نوع المستشعر"""
        # إنشاء قراءات لحقول مختلفة
        readings = create_sample_readings(
            "device_001", "field_001", "soil_moisture", count=24
        )
        readings.extend(
            create_sample_readings(
                "device_002", "field_002", "soil_moisture", count=24
            )
        )

        time_range = (
            datetime.now(UTC) - timedelta(hours=24),
            datetime.now(UTC),
        )

        aggregated = self.aggregator.aggregate_by_sensor_type(
            "soil_moisture", time_range, readings, TimeGranularity.DAILY
        )

        # يجب أن يكون هناك حقلان
        # Should have two fields
        self.assertEqual(len(aggregated), 2)
        self.assertIn("field_001", aggregated)
        self.assertIn("field_002", aggregated)

    def test_hourly_average(self):
        """اختبار المتوسط الساعي"""
        # إنشاء قراءات لـ 24 ساعة (كل 15 دقيقة)
        # Create readings for 24 hours (every 15 minutes)
        readings = create_sample_readings(
            self.device_id, self.field_id, self.sensor_type, count=96
        )

        hourly_data = self.aggregator.hourly_average(readings)

        # يجب أن يكون هناك 24 ساعة
        # Should have 24 hours
        self.assertGreater(len(hourly_data), 0)
        self.assertLessEqual(len(hourly_data), 24)

    def test_daily_summary(self):
        """اختبار الملخص اليومي"""
        # إنشاء قراءات لعدة أيام
        readings = create_sample_readings(
            self.device_id, self.field_id, self.sensor_type, count=96
        )

        daily_data = self.aggregator.daily_summary(readings)

        # يجب أن يكون هناك يوم واحد على الأقل
        # Should have at least one day
        self.assertGreater(len(daily_data), 0)

    def test_check_sensor_status_healthy(self):
        """اختبار فحص حالة المستشعر (سليم)"""
        # إنشاء قراءات صحيحة
        readings = create_sample_readings(
            self.device_id, self.field_id, "air_temperature", count=96, base_value=25.0, noise=1.0
        )

        health = self.aggregator.check_sensor_status(self.device_id, readings)

        # التحقق من الحالة - Verify status
        self.assertEqual(health.device_id, self.device_id)
        self.assertGreater(health.data_quality_score, 70)
        self.assertGreater(health.uptime_percentage, 90)
        self.assertIn(health.status, [SensorStatus.HEALTHY, SensorStatus.WARNING])

    def test_check_sensor_status_offline(self):
        """اختبار فحص حالة المستشعر (غير متصل)"""
        # لا توجد قراءات - No readings
        health = self.aggregator.check_sensor_status(self.device_id, [])

        # التحقق من الحالة - Verify status
        self.assertEqual(health.status, SensorStatus.OFFLINE)
        self.assertEqual(health.data_quality_score, 0.0)

    def test_detect_sensor_drift(self):
        """اختبار اكتشاف الانحراف"""
        # إنشاء قراءات مع انحراف تدريجي
        # Create readings with gradual drift
        readings = []
        start_time = datetime.now(UTC) - timedelta(hours=24)

        for i in range(50):
            # زيادة تدريجية من 20 إلى 30
            # Gradual increase from 20 to 30
            value = 20.0 + (i / 50.0) * 10.0
            timestamp = start_time + timedelta(minutes=30 * i)

            reading = SensorReading(
                device_id=self.device_id,
                field_id=self.field_id,
                sensor_type=self.sensor_type,
                value=value,
                unit="°C",
                timestamp=timestamp.isoformat(),
            )
            readings.append(reading)

        drift_detected, drift_magnitude = self.aggregator.detect_sensor_drift(readings, window_size=10)

        # يجب اكتشاف الانحراف - Should detect drift
        self.assertTrue(drift_detected)
        self.assertIsNotNone(drift_magnitude)
        self.assertGreater(drift_magnitude, 20.0)

    def test_calculate_data_quality_score(self):
        """اختبار حساب نقاط جودة البيانات"""
        # قراءات عالية الجودة - High quality readings
        good_readings = create_sample_readings(
            self.device_id, self.field_id, self.sensor_type, count=96, base_value=25.0, noise=0.5
        )

        good_score = self.aggregator.calculate_data_quality_score(good_readings)

        # يجب أن يكون النقاط عالي - Should have high score
        self.assertGreater(good_score, 70)

        # قراءات قليلة - Few readings
        poor_readings = create_sample_readings(
            self.device_id, self.field_id, self.sensor_type, count=10, base_value=25.0
        )

        poor_score = self.aggregator.calculate_data_quality_score(poor_readings)

        # يجب أن يكون النقاط منخفض - Should have lower score
        self.assertLess(poor_score, good_score)

    def test_rate_of_change(self):
        """اختبار حساب معدل التغيير"""
        # إنشاء قراءات بمعدل تغيير ثابت
        # Create readings with constant rate of change
        readings = []
        start_time = datetime.now(UTC) - timedelta(hours=10)

        for i in range(10):
            # زيادة 1 درجة كل ساعة - Increase 1 degree per hour
            value = 20.0 + i
            timestamp = start_time + timedelta(hours=i)

            reading = SensorReading(
                device_id=self.device_id,
                field_id=self.field_id,
                sensor_type=self.sensor_type,
                value=value,
                unit="°C",
                timestamp=timestamp.isoformat(),
            )
            readings.append(reading)

        rate = self.aggregator._calculate_rate_of_change(readings)

        # معدل التغيير يجب أن يكون تقريباً 1 درجة/ساعة
        # Rate of change should be approximately 1 degree/hour
        self.assertIsNotNone(rate)
        self.assertAlmostEqual(rate, 1.0, places=1)

    def test_cumulative_sum_for_rainfall(self):
        """اختبار المجموع التراكمي للأمطار"""
        # إنشاء قراءات أمطار
        # Create rainfall readings
        rainfall_values = [2.5, 1.0, 3.5, 0.5, 4.0]
        readings = []

        for i, value in enumerate(rainfall_values):
            reading = SensorReading(
                device_id=self.device_id,
                field_id=self.field_id,
                sensor_type="rainfall",
                value=value,
                unit="mm",
                timestamp=(datetime.now(UTC) + timedelta(hours=i)).isoformat(),
            )
            readings.append(reading)

        time_range = (
            datetime.now(UTC) - timedelta(hours=1),
            datetime.now(UTC) + timedelta(hours=10),
        )

        aggregated = self.aggregator._aggregate_readings(
            self.field_id,
            "rainfall",
            time_range,
            readings,
            TimeGranularity.DAILY,
        )

        # المجموع التراكمي يجب أن يساوي مجموع القيم
        # Cumulative sum should equal sum of values
        self.assertIsNotNone(aggregated.cumulative_sum)
        self.assertAlmostEqual(aggregated.cumulative_sum, sum(rainfall_values), places=1)


class TestSensorReadingModel(unittest.TestCase):
    """اختبار نموذج القراءة"""

    def test_sensor_reading_creation(self):
        """اختبار إنشاء قراءة مستشعر"""
        reading = SensorReading(
            device_id="test_device",
            field_id="test_field",
            sensor_type="temperature",
            value=25.5,
            unit="°C",
            timestamp=datetime.now(UTC).isoformat(),
        )

        self.assertEqual(reading.device_id, "test_device")
        self.assertEqual(reading.value, 25.5)
        self.assertFalse(reading.is_outlier)

    def test_sensor_reading_to_dict(self):
        """اختبار تحويل القراءة إلى قاموس"""
        reading = SensorReading(
            device_id="test_device",
            field_id="test_field",
            sensor_type="temperature",
            value=25.5,
            unit="°C",
            timestamp=datetime.now(UTC).isoformat(),
            metadata={"battery": 95},
        )

        data = reading.to_dict()

        self.assertIn("device_id", data)
        self.assertIn("value", data)
        self.assertIn("metadata", data)
        self.assertEqual(data["metadata"]["battery"], 95)


if __name__ == "__main__":
    unittest.main()
