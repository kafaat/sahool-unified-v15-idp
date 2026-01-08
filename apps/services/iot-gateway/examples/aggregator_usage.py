"""
أمثلة استخدام مجمع بيانات المستشعرات
Sensor Aggregator Usage Examples

يوضح كيفية استخدام خدمة تجميع بيانات المستشعرات
Demonstrates how to use the sensor data aggregation service
"""

from datetime import UTC, datetime, timedelta

from apps.services.iot_gateway.src.models.sensor_data import (
    SensorReading,
    TimeGranularity,
)
from apps.services.iot_gateway.src.sensor_aggregator import (
    SensorAggregator,
    create_sample_readings,
)


def example_basic_statistics():
    """
    مثال: حساب الإحصائيات الأساسية
    Example: Calculate basic statistics
    """
    print("\n" + "=" * 60)
    print("مثال 1: الإحصائيات الأساسية")
    print("Example 1: Basic Statistics")
    print("=" * 60)

    aggregator = SensorAggregator()

    # إنشاء قراءات تجريبية - Create sample readings
    values = [22.5, 23.0, 24.5, 25.0, 23.5, 24.0, 26.0, 25.5, 24.5, 23.0]

    stats = aggregator.calculate_statistics(values)

    print(f"\nالقيم - Values: {values}")
    print(f"\nالمتوسط - Mean: {stats['mean']}°C")
    print(f"الوسيط - Median: {stats['median']}°C")
    print(f"الحد الأدنى - Min: {stats['min']}°C")
    print(f"الحد الأقصى - Max: {stats['max']}°C")
    print(f"الانحراف المعياري - Std Dev: {stats['std']}°C")
    print("\nالمئينات - Percentiles:")
    print(f"  P10: {stats['p10']}°C")
    print(f"  P25: {stats['p25']}°C")
    print(f"  P75: {stats['p75']}°C")
    print(f"  P90: {stats['p90']}°C")


def example_outlier_detection():
    """
    مثال: اكتشاف القيم الشاذة
    Example: Detect outliers
    """
    print("\n" + "=" * 60)
    print("مثال 2: اكتشاف القيم الشاذة")
    print("Example 2: Outlier Detection")
    print("=" * 60)

    aggregator = SensorAggregator()

    # إنشاء قراءات مع قيم شاذة - Create readings with outliers
    readings = create_sample_readings(
        device_id="sensor_temp_001",
        field_id="field_highland_01",
        sensor_type="air_temperature",
        count=20,
        base_value=25.0,
        noise=1.0,
    )

    # إضافة قيم شاذة - Add outliers
    readings.append(
        SensorReading(
            device_id="sensor_temp_001",
            field_id="field_highland_01",
            sensor_type="air_temperature",
            value=55.0,  # قيمة شاذة - outlier
            unit="°C",
            timestamp=datetime.now(UTC).isoformat(),
        )
    )

    print(f"\nعدد القراءات الإجمالي - Total readings: {len(readings)}")

    # اكتشاف باستخدام Z-Score
    print("\n--- طريقة Z-Score Method ---")
    outliers_zscore = aggregator.detect_outliers(
        readings, method="zscore", threshold=2.5
    )
    print(f"القيم الشاذة المكتشفة - Outliers detected: {len(outliers_zscore)}")
    for outlier in outliers_zscore:
        print(f"  القيمة - Value: {outlier.value}°C في - at {outlier.timestamp}")

    # اكتشاف باستخدام IQR
    print("\n--- طريقة IQR Method ---")
    outliers_iqr = aggregator.detect_outliers(readings, method="iqr", threshold=1.5)
    print(f"القيم الشاذة المكتشفة - Outliers detected: {len(outliers_iqr)}")

    # اكتشاف باستخدام عتبات اليمن
    print("\n--- عتبات اليمن - Yemen Thresholds ---")
    outliers_threshold = aggregator.detect_outliers(readings, method="threshold")
    print(f"القيم خارج النطاق - Out of range: {len(outliers_threshold)}")


def example_field_aggregation():
    """
    مثال: تجميع البيانات حسب الحقل
    Example: Aggregate data by field
    """
    print("\n" + "=" * 60)
    print("مثال 3: التجميع حسب الحقل")
    print("Example 3: Field Aggregation")
    print("=" * 60)

    aggregator = SensorAggregator()
    field_id = "field_sanaa_001"

    # إنشاء قراءات لأنواع مختلفة من المستشعرات
    # Create readings for different sensor types
    readings = []

    # درجة حرارة الهواء - Air temperature
    readings.extend(
        create_sample_readings(
            device_id="temp_001",
            field_id=field_id,
            sensor_type="air_temperature",
            count=48,
            base_value=28.0,
            noise=3.0,
        )
    )

    # رطوبة التربة - Soil moisture
    readings.extend(
        create_sample_readings(
            device_id="soil_001",
            field_id=field_id,
            sensor_type="soil_moisture",
            count=48,
            base_value=45.0,
            noise=5.0,
        )
    )

    # رطوبة الهواء - Air humidity
    readings.extend(
        create_sample_readings(
            device_id="humid_001",
            field_id=field_id,
            sensor_type="air_humidity",
            count=48,
            base_value=55.0,
            noise=8.0,
        )
    )

    # تحديد الفترة الزمنية - Define time range
    time_range = (
        datetime.now(UTC) - timedelta(hours=24),
        datetime.now(UTC),
    )

    # التجميع - Aggregate
    aggregated_data = aggregator.aggregate_by_field(
        field_id=field_id,
        time_range=time_range,
        readings=readings,
        granularity=TimeGranularity.DAILY,
    )

    print(f"\nالحقل - Field: {field_id}")
    print("الفترة الزمنية - Time range: آخر 24 ساعة - Last 24 hours")
    print(f"أنواع المستشعرات - Sensor types: {len(aggregated_data)}")

    for agg in aggregated_data:
        print(f"\n--- {agg.sensor_type} ---")
        print(f"  عدد القراءات - Count: {agg.count}")
        print(f"  المتوسط - Mean: {agg.mean}")
        print(f"  الحد الأدنى - Min: {agg.min}")
        print(f"  الحد الأقصى - Max: {agg.max}")
        print(f"  الانحراف المعياري - Std: {agg.std}")
        print(f"  جودة البيانات - Quality: {agg.data_quality_score:.1f}%")
        print(f"  القيم الشاذة - Outliers: {agg.outlier_count}")


def example_time_based_aggregation():
    """
    مثال: التجميع الزمني (ساعي، يومي، أسبوعي)
    Example: Time-based aggregation
    """
    print("\n" + "=" * 60)
    print("مثال 4: التجميع الزمني")
    print("Example 4: Time-based Aggregation")
    print("=" * 60)

    aggregator = SensorAggregator()

    # إنشاء قراءات لـ 48 ساعة - Create readings for 48 hours
    readings = create_sample_readings(
        device_id="sensor_001",
        field_id="field_001",
        sensor_type="air_temperature",
        count=192,  # 4 قراءات/ساعة × 48 ساعة
        base_value=26.0,
        noise=4.0,
    )

    # المتوسط الساعي - Hourly average
    print("\n--- المتوسط الساعي - Hourly Average ---")
    hourly_data = aggregator.hourly_average(readings)
    print(f"عدد الساعات - Hours: {len(hourly_data)}")
    for hour_key in list(hourly_data.keys())[:3]:  # عرض أول 3 ساعات
        agg = hourly_data[hour_key]
        print(f"  {hour_key}: {agg.mean}°C (n={agg.count})")

    # الملخص اليومي - Daily summary
    print("\n--- الملخص اليومي - Daily Summary ---")
    daily_data = aggregator.daily_summary(readings)
    print(f"عدد الأيام - Days: {len(daily_data)}")
    for day_key, agg in daily_data.items():
        print(f"  {day_key}:")
        print(f"    المتوسط - Mean: {agg.mean}°C")
        print(f"    النطاق - Range: {agg.min}°C - {agg.max}°C")
        print(f"    القراءات - Readings: {agg.count}")


def example_sensor_health_monitoring():
    """
    مثال: مراقبة صحة المستشعرات
    Example: Sensor health monitoring
    """
    print("\n" + "=" * 60)
    print("مثال 5: مراقبة صحة المستشعرات")
    print("Example 5: Sensor Health Monitoring")
    print("=" * 60)

    aggregator = SensorAggregator()
    device_id = "sensor_temp_highland_01"

    # مثال 1: مستشعر صحي - Healthy sensor
    print("\n--- مستشعر صحي - Healthy Sensor ---")
    healthy_readings = create_sample_readings(
        device_id=device_id,
        field_id="field_001",
        sensor_type="air_temperature",
        count=96,  # 24 ساعة من القراءات
        base_value=25.0,
        noise=2.0,
    )

    health = aggregator.check_sensor_status(device_id, healthy_readings)
    print(f"الحالة - Status: {health.status.value}")
    print(f"جودة البيانات - Quality: {health.data_quality_score:.1f}%")
    print(f"وقت التشغيل - Uptime: {health.uptime_percentage:.1f}%")
    print(f"القراءات في 24 ساعة - Readings (24h): {health.readings_count_24h}")
    print(f"القيم الشاذة - Outliers: {health.outlier_percentage:.1f}%")

    if health.recommendations_ar:
        print("\nالتوصيات - Recommendations:")
        for rec in health.recommendations_ar:
            print(f"  • {rec}")

    # مثال 2: مستشعر بقراءات قليلة - Sensor with few readings
    print("\n--- مستشعر بقراءات قليلة - Low Readings ---")
    poor_readings = create_sample_readings(
        device_id=device_id,
        field_id="field_001",
        sensor_type="air_temperature",
        count=10,  # قراءات قليلة جداً
        base_value=25.0,
    )

    health_poor = aggregator.check_sensor_status(device_id, poor_readings)
    print(f"الحالة - Status: {health_poor.status.value}")
    print(f"جودة البيانات - Quality: {health_poor.data_quality_score:.1f}%")
    print(f"وقت التشغيل - Uptime: {health_poor.uptime_percentage:.1f}%")

    if health_poor.alerts:
        print("\nالتنبيهات - Alerts:")
        for alert in health_poor.alerts:
            print(f"  ⚠️  {alert}")


def example_drift_detection():
    """
    مثال: اكتشاف انحراف المستشعر
    Example: Sensor drift detection
    """
    print("\n" + "=" * 60)
    print("مثال 6: اكتشاف انحراف المستشعر")
    print("Example 6: Sensor Drift Detection")
    print("=" * 60)

    aggregator = SensorAggregator()

    # إنشاء قراءات مع انحراف تدريجي
    # Create readings with gradual drift
    readings = []
    start_time = datetime.now(UTC) - timedelta(hours=48)

    print("\nإنشاء قراءات مع انحراف من 20°C إلى 30°C")
    print("Creating readings with drift from 20°C to 30°C")

    for i in range(100):
        # انحراف تدريجي من 20 إلى 30 - Gradual drift from 20 to 30
        value = 20.0 + (i / 100.0) * 10.0
        timestamp = start_time + timedelta(minutes=30 * i)

        reading = SensorReading(
            device_id="drifting_sensor",
            field_id="field_001",
            sensor_type="air_temperature",
            value=value,
            unit="°C",
            timestamp=timestamp.isoformat(),
        )
        readings.append(reading)

    drift_detected, drift_magnitude = aggregator.detect_sensor_drift(readings, window_size=10)

    print(f"\nالانحراف مكتشف - Drift detected: {drift_detected}")
    if drift_magnitude:
        print(f"مقدار الانحراف - Drift magnitude: {drift_magnitude:.1f}%")

    # فحص الصحة - Check health
    health = aggregator.check_sensor_status("drifting_sensor", readings)
    print(f"\nالحالة - Status: {health.status.value}")

    if health.drift_detected:
        print("\n⚠️  تحذير: انحراف مكتشف في المستشعر")
        print("⚠️  Warning: Sensor drift detected")
        print("\nالتوصيات - Recommendations:")
        for rec in health.recommendations_ar:
            print(f"  • {rec}")


def example_rainfall_cumulative():
    """
    مثال: المجموع التراكمي للأمطار
    Example: Rainfall cumulative sum
    """
    print("\n" + "=" * 60)
    print("مثال 7: المجموع التراكمي للأمطار")
    print("Example 7: Rainfall Cumulative Sum")
    print("=" * 60)

    aggregator = SensorAggregator()

    # قراءات الأمطار اليومية - Daily rainfall readings
    rainfall_data = [
        ("2024-01-01", 5.5),
        ("2024-01-02", 12.0),
        ("2024-01-03", 0.0),
        ("2024-01-04", 8.5),
        ("2024-01-05", 3.0),
        ("2024-01-06", 15.5),
        ("2024-01-07", 0.0),
    ]

    readings = []
    for date_str, value in rainfall_data:
        reading = SensorReading(
            device_id="rain_gauge_001",
            field_id="field_taiz_001",
            sensor_type="rainfall",
            value=value,
            unit="mm",
            timestamp=f"{date_str}T12:00:00Z",
        )
        readings.append(reading)

    time_range = (
        datetime.fromisoformat("2024-01-01T00:00:00Z"),
        datetime.fromisoformat("2024-01-08T00:00:00Z"),
    )

    agg = aggregator._aggregate_readings(
        field_id="field_taiz_001",
        sensor_type="rainfall",
        time_range=time_range,
        readings=readings,
        granularity=TimeGranularity.WEEKLY,
    )

    print("\nالفترة - Period: أسبوع - Week")
    print(f"القراءات - Readings: {agg.count}")
    print(f"\nالمجموع التراكمي - Cumulative Sum: {agg.cumulative_sum} mm")
    print(f"المتوسط اليومي - Daily Average: {agg.mean} mm")
    print(f"الحد الأقصى - Maximum: {agg.max} mm")
    print(f"الحد الأدنى - Minimum: {agg.min} mm")


def example_complete_workflow():
    """
    مثال: سير عمل كامل
    Example: Complete workflow
    """
    print("\n" + "=" * 60)
    print("مثال 8: سير عمل كامل")
    print("Example 8: Complete Workflow")
    print("=" * 60)

    aggregator = SensorAggregator()

    # 1. إنشاء بيانات تجريبية - Create sample data
    print("\n1. إنشاء بيانات المستشعرات - Creating sensor data...")
    readings = create_sample_readings(
        device_id="multi_sensor_001",
        field_id="demo_field",
        sensor_type="soil_moisture",
        count=96,
        base_value=55.0,
        noise=8.0,
    )
    print(f"   ✓ تم إنشاء {len(readings)} قراءة - Created {len(readings)} readings")

    # 2. حساب الإحصائيات - Calculate statistics
    print("\n2. حساب الإحصائيات - Calculating statistics...")
    values = [r.value for r in readings]
    stats = aggregator.calculate_statistics(values)
    print(f"   ✓ المتوسط: {stats['mean']}%")
    print(f"   ✓ النطاق: {stats['min']}% - {stats['max']}%")

    # 3. اكتشاف القيم الشاذة - Detect outliers
    print("\n3. اكتشاف القيم الشاذة - Detecting outliers...")
    outliers = aggregator.detect_outliers(readings, method="threshold")
    print(f"   ✓ القيم الشاذة: {len(outliers)}")

    # 4. فحص صحة المستشعر - Check sensor health
    print("\n4. فحص صحة المستشعر - Checking sensor health...")
    health = aggregator.check_sensor_status("multi_sensor_001", readings)
    print(f"   ✓ الحالة: {health.status.value}")
    print(f"   ✓ جودة البيانات: {health.data_quality_score:.1f}%")

    # 5. التجميع اليومي - Daily aggregation
    print("\n5. التجميع اليومي - Daily aggregation...")
    daily_data = aggregator.daily_summary(readings)
    print(f"   ✓ عدد الأيام: {len(daily_data)}")

    # 6. التقرير النهائي - Final report
    print("\n" + "=" * 60)
    print("التقرير النهائي - Final Report")
    print("=" * 60)
    print("المستشعر - Sensor: multi_sensor_001")
    print("النوع - Type: soil_moisture")
    print("الفترة - Period: 24 hours")
    print(f"القراءات - Readings: {len(readings)}")
    print(f"المتوسط - Average: {stats['mean']}%")
    print(f"جودة البيانات - Quality: {health.data_quality_score:.1f}%")
    print(f"الحالة - Status: {health.status.value}")


def main():
    """
    تشغيل جميع الأمثلة
    Run all examples
    """
    print("\n")
    print("=" * 60)
    print("أمثلة استخدام مجمع بيانات المستشعرات - SAHOOL IoT")
    print("Sensor Data Aggregator Usage Examples - SAHOOL IoT")
    print("=" * 60)

    example_basic_statistics()
    example_outlier_detection()
    example_field_aggregation()
    example_time_based_aggregation()
    example_sensor_health_monitoring()
    example_drift_detection()
    example_rainfall_cumulative()
    example_complete_workflow()

    print("\n" + "=" * 60)
    print("اكتملت جميع الأمثلة - All examples completed")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
