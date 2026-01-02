#!/usr/bin/env python3
"""
التحقق من مجمع بيانات المستشعرات
Verify Sensor Aggregator Installation

اختبار سريع للتأكد من عمل جميع المكونات
Quick test to ensure all components work correctly
"""

import sys
from datetime import datetime, timedelta, timezone


def verify_imports():
    """التحقق من الاستيراد - Verify imports"""
    print("=" * 60)
    print("التحقق من الاستيراد - Verifying imports...")
    print("=" * 60)

    try:
        from src.sensor_aggregator import SensorAggregator, create_sample_readings
        print("✓ SensorAggregator imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import SensorAggregator: {e}")
        return False

    try:
        from src.models.sensor_data import (
            SensorReading,
            AggregatedData,
            SensorHealth,
            SensorStatus,
            TimeGranularity,
            YEMEN_THRESHOLDS,
            get_threshold,
            check_value_in_range,
        )
        print("✓ All models imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import models: {e}")
        return False

    return True


def verify_basic_functionality():
    """التحقق من الوظائف الأساسية - Verify basic functionality"""
    print("\n" + "=" * 60)
    print("التحقق من الوظائف الأساسية - Verifying basic functionality...")
    print("=" * 60)

    from src.sensor_aggregator import SensorAggregator, create_sample_readings
    from src.models.sensor_data import TimeGranularity

    try:
        # 1. Create aggregator
        aggregator = SensorAggregator()
        print("✓ Created SensorAggregator instance")

        # 2. Create sample readings
        readings = create_sample_readings(
            device_id="test_device",
            field_id="test_field",
            sensor_type="air_temperature",
            count=50,
            base_value=25.0,
        )
        print(f"✓ Created {len(readings)} sample readings")

        # 3. Calculate statistics
        values = [r.value for r in readings]
        stats = aggregator.calculate_statistics(values)
        print(f"✓ Calculated statistics: mean={stats['mean']}°C")

        # 4. Detect outliers
        outliers = aggregator.detect_outliers(readings, method="zscore")
        print(f"✓ Detected outliers: {len(outliers)}")

        # 5. Check sensor health
        health = aggregator.check_sensor_status("test_device", readings)
        print(f"✓ Checked sensor health: status={health.status.value}")

        # 6. Daily summary
        daily = aggregator.daily_summary(readings)
        print(f"✓ Generated daily summary: {len(daily)} days")

        # 7. Time range aggregation
        time_range = (
            datetime.now(timezone.utc) - timedelta(hours=24),
            datetime.now(timezone.utc),
        )
        agg = aggregator.aggregate_by_field(
            "test_field", time_range, readings, TimeGranularity.DAILY
        )
        print(f"✓ Aggregated by field: {len(agg)} sensor types")

        return True

    except Exception as e:
        print(f"✗ Error during functionality test: {e}")
        import traceback

        traceback.print_exc()
        return False


def verify_yemen_thresholds():
    """التحقق من عتبات اليمن - Verify Yemen thresholds"""
    print("\n" + "=" * 60)
    print("التحقق من عتبات اليمن - Verifying Yemen thresholds...")
    print("=" * 60)

    from src.models.sensor_data import (
        YEMEN_THRESHOLDS,
        check_value_in_range,
        get_threshold,
    )

    try:
        # Check threshold definitions
        expected_sensors = [
            "soil_moisture",
            "air_temperature",
            "soil_temperature",
            "air_humidity",
            "soil_ec",
            "soil_ph",
            "rainfall",
            "wind_speed",
        ]

        for sensor_type in expected_sensors:
            threshold = get_threshold(sensor_type)
            if threshold:
                print(
                    f"✓ {sensor_type}: {threshold.min_value}-{threshold.max_value} {threshold.unit}"
                )
            else:
                print(f"✗ Missing threshold for {sensor_type}")
                return False

        # Test value checking
        is_valid, severity = check_value_in_range("air_temperature", 25.0)
        print(f"\n✓ Value check works: 25°C is valid={is_valid}, severity={severity}")

        is_valid, severity = check_value_in_range("air_temperature", 60.0)
        print(
            f"✓ Value check works: 60°C is valid={is_valid}, severity={severity} (should be critical)"
        )

        return True

    except Exception as e:
        print(f"✗ Error during threshold verification: {e}")
        import traceback

        traceback.print_exc()
        return False


def verify_data_models():
    """التحقق من نماذج البيانات - Verify data models"""
    print("\n" + "=" * 60)
    print("التحقق من نماذج البيانات - Verifying data models...")
    print("=" * 60)

    from src.models.sensor_data import (
        SensorReading,
        AggregatedData,
        SensorHealth,
        SensorStatus,
        TimeGranularity,
    )

    try:
        # Test SensorReading
        reading = SensorReading(
            device_id="test",
            field_id="test",
            sensor_type="temperature",
            value=25.0,
            unit="°C",
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        data = reading.to_dict()
        print("✓ SensorReading model works")

        # Test AggregatedData
        agg = AggregatedData(
            field_id="test",
            sensor_type="temperature",
            time_range_start=datetime.now(timezone.utc).isoformat(),
            time_range_end=datetime.now(timezone.utc).isoformat(),
            granularity=TimeGranularity.DAILY,
            mean=25.0,
            count=10,
        )
        data = agg.to_dict()
        print("✓ AggregatedData model works")

        # Test SensorHealth
        health = SensorHealth(
            device_id="test",
            field_id="test",
            sensor_type="temperature",
            status=SensorStatus.HEALTHY,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        data = health.to_dict()
        print("✓ SensorHealth model works")

        return True

    except Exception as e:
        print(f"✗ Error during model verification: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """الوظيفة الرئيسية - Main function"""
    print("\n")
    print("=" * 60)
    print("التحقق من مجمع بيانات المستشعرات - SAHOOL IoT")
    print("Sensor Aggregator Verification - SAHOOL IoT")
    print("=" * 60)

    results = []

    # Run verification tests
    results.append(("Imports", verify_imports()))
    if results[-1][1]:  # Only continue if imports work
        results.append(("Data Models", verify_data_models()))
        results.append(("Yemen Thresholds", verify_yemen_thresholds()))
        results.append(("Basic Functionality", verify_basic_functionality()))

    # Print summary
    print("\n" + "=" * 60)
    print("ملخص التحقق - Verification Summary")
    print("=" * 60)

    all_passed = True
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status} - {test_name}")
        if not passed:
            all_passed = False

    print("=" * 60)

    if all_passed:
        print("✓ جميع الاختبارات نجحت - All tests passed!")
        print("✓ Sensor Aggregator is ready to use")
        return 0
    else:
        print("✗ بعض الاختبارات فشلت - Some tests failed")
        print("✗ Please check the errors above")
        return 1


if __name__ == "__main__":
    sys.exit(main())
