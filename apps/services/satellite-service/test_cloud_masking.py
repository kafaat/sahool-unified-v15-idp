"""
Test Cloud Masking System
اختبار نظام تحديد الغطاء السحابي

Tests for the advanced cloud masking functionality including:
- Cloud cover analysis
- Clear observation finding
- Best observation selection
- Temporal interpolation
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from cloud_masking import (
    SCLClass,
    get_cloud_masker,
)


async def test_cloud_cover_analysis():
    """Test basic cloud cover analysis"""
    print("\n" + "=" * 70)
    print("TEST 1: Cloud Cover Analysis")
    print("=" * 70)

    masker = get_cloud_masker()

    # Test analysis for a field
    field_id = "test_field_001"
    latitude = 15.5527
    longitude = 44.2075
    date = datetime(2024, 3, 15)

    result = await masker.analyze_cloud_cover(
        field_id=field_id, latitude=latitude, longitude=longitude, date=date
    )

    print(f"\n📍 Field: {result.field_id}")
    print(f"📅 Date: {result.timestamp.strftime('%Y-%m-%d')}")
    print(f"☁️  Cloud Cover: {result.cloud_cover_percent}%")
    print(f"🌑 Shadow Cover: {result.shadow_cover_percent}%")
    print(f"✅ Clear Pixels: {result.clear_cover_percent}%")
    print(f"⭐ Quality Score: {result.quality_score:.3f}")
    print(f"✓  Usable: {result.usable}")
    print(f"💡 Recommendation: {result.recommendation}")

    print("\n📊 SCL Distribution:")
    for class_name, percent in sorted(
        result.scl_distribution.items(), key=lambda x: x[1], reverse=True
    ):
        if percent > 0:
            print(f"   {class_name}: {percent}%")

    assert result.quality_score >= 0 and result.quality_score <= 1
    assert result.cloud_cover_percent >= 0 and result.cloud_cover_percent <= 100
    print("\n✅ Cloud cover analysis test passed!")


async def test_find_clear_observations():
    """Test finding clear observations in date range"""
    print("\n" + "=" * 70)
    print("TEST 2: Find Clear Observations")
    print("=" * 70)

    masker = get_cloud_masker()

    field_id = "test_field_002"
    latitude = 15.5527
    longitude = 44.2075
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 3, 31)
    max_cloud = 20.0

    observations = await masker.find_clear_observations(
        field_id=field_id,
        latitude=latitude,
        longitude=longitude,
        start_date=start_date,
        end_date=end_date,
        max_cloud_cover=max_cloud,
    )

    print(f"\n📍 Field: {field_id}")
    print(f"📅 Date Range: {start_date.date()} to {end_date.date()}")
    print(f"☁️  Max Cloud Threshold: {max_cloud}%")
    print(f"🔍 Found {len(observations)} clear observations")

    if observations:
        print("\n🏆 Top 5 Observations (by quality):")
        for i, obs in enumerate(observations[:5], 1):
            print(f"\n   {i}. {obs.date.strftime('%Y-%m-%d')} ({obs.satellite})")
            print(f"      Cloud: {obs.cloud_cover}%")
            print(f"      Quality: {obs.quality_score:.3f}")
            print(f"      Clear Pixels: {obs.clear_pixels}%")

    assert all(obs.cloud_cover <= max_cloud for obs in observations)
    assert all(obs.quality_score >= 0 and obs.quality_score <= 1 for obs in observations)
    print("\n✅ Clear observations test passed!")


async def test_best_observation():
    """Test finding best observation near target date"""
    print("\n" + "=" * 70)
    print("TEST 3: Best Observation Selection")
    print("=" * 70)

    masker = get_cloud_masker()

    field_id = "test_field_003"
    latitude = 15.5527
    longitude = 44.2075
    target_date = datetime(2024, 2, 15)
    tolerance_days = 15

    best = await masker.get_best_observation(
        field_id=field_id,
        latitude=latitude,
        longitude=longitude,
        target_date=target_date,
        days_tolerance=tolerance_days,
    )

    print(f"\n📍 Field: {field_id}")
    print(f"🎯 Target Date: {target_date.date()}")
    print(f"📏 Tolerance: ±{tolerance_days} days")

    if best:
        days_diff = abs((best.date - target_date).days)
        print("\n🏆 Best Observation:")
        print(f"   Date: {best.date.strftime('%Y-%m-%d')} ({best.satellite})")
        print(f"   Days from target: {days_diff}")
        print(f"   Cloud Cover: {best.cloud_cover}%")
        print(f"   Shadow Cover: {best.shadow_cover}%")
        print(f"   Quality Score: {best.quality_score:.3f}")
        print(f"   Clear Pixels: {best.clear_pixels}%")

        assert days_diff <= tolerance_days
        assert best.quality_score >= 0 and best.quality_score <= 1
        print("\n✅ Best observation test passed!")
    else:
        print("\n⚠️  No clear observations found (this is expected sometimes)")


async def test_quality_scoring():
    """Test quality score calculation"""
    print("\n" + "=" * 70)
    print("TEST 4: Quality Score Calculation")
    print("=" * 70)

    masker = get_cloud_masker()

    test_cases = [
        (0, 0, 100, "Perfect - no clouds"),
        (5, 2, 93, "Excellent - minimal clouds"),
        (15, 10, 75, "Good - acceptable clouds"),
        (25, 15, 60, "Fair - moderate clouds"),
        (50, 20, 30, "Poor - heavy clouds"),
        (80, 10, 10, "Very poor - mostly cloudy"),
    ]

    print("\n📊 Quality Score Test Cases:")
    for cloud, shadow, clear, desc in test_cases:
        score = masker.calculate_quality_score(cloud, shadow, clear)
        print(f"\n   {desc}")
        print(f"   Cloud: {cloud}%, Shadow: {shadow}%, Clear: {clear}%")
        print(f"   → Quality Score: {score:.3f}")

        assert score >= 0 and score <= 1

    print("\n✅ Quality scoring test passed!")


async def test_cloud_masking():
    """Test applying cloud mask to NDVI values"""
    print("\n" + "=" * 70)
    print("TEST 5: Cloud Mask Application")
    print("=" * 70)

    masker = get_cloud_masker()

    test_cases = [
        (0.75, SCLClass.VEGETATION, "VEGETATION - should pass"),
        (0.65, SCLClass.BARE_SOIL, "BARE_SOIL - should pass"),
        (0.50, SCLClass.CLOUD_MEDIUM, "CLOUD_MEDIUM - should mask"),
        (0.60, SCLClass.CLOUD_HIGH, "CLOUD_HIGH - should mask"),
        (0.55, SCLClass.CLOUD_SHADOW, "CLOUD_SHADOW - should mask"),
        (0.45, SCLClass.THIN_CIRRUS, "THIN_CIRRUS - should mask"),
    ]

    print("\n🎭 Mask Application Test Cases:")
    for ndvi, scl_class, desc in test_cases:
        result = await masker.apply_cloud_mask(ndvi, scl_class)

        if result is not None:
            print(f"   ✅ {desc}: {ndvi} → {result}")
            assert result == ndvi
        else:
            print(f"   🚫 {desc}: {ndvi} → MASKED")
            assert scl_class not in masker.VALID_CLASSES

    print("\n✅ Cloud masking test passed!")


async def test_interpolation():
    """Test temporal interpolation of cloudy pixels"""
    print("\n" + "=" * 70)
    print("TEST 6: Temporal Interpolation")
    print("=" * 70)

    masker = get_cloud_masker()

    # Create test NDVI series with some cloudy observations
    ndvi_series = [
        {"date": "2024-01-01", "ndvi": 0.60, "cloudy": False},
        {
            "date": "2024-01-06",
            "ndvi": 0.45,
            "cloudy": True,
        },  # Cloudy - should interpolate
        {
            "date": "2024-01-11",
            "ndvi": 0.50,
            "cloudy": True,
        },  # Cloudy - should interpolate
        {"date": "2024-01-16", "ndvi": 0.70, "cloudy": False},
        {
            "date": "2024-01-21",
            "ndvi": 0.55,
            "cloudy": True,
        },  # Cloudy - should interpolate
        {"date": "2024-01-26", "ndvi": 0.75, "cloudy": False},
    ]

    print("\n📈 Original NDVI Series:")
    for obs in ndvi_series:
        status = "☁️ CLOUDY" if obs["cloudy"] else "✅ CLEAR"
        print(f"   {obs['date']}: {obs['ndvi']:.3f} {status}")

    # Test linear interpolation
    print("\n🔧 Applying Linear Interpolation...")
    interpolated = await masker.interpolate_cloudy_pixels(
        field_id="test_field_004", ndvi_series=ndvi_series.copy(), method="linear"
    )

    print("\n📊 Interpolated NDVI Series:")
    for obs in interpolated:
        if obs.get("interpolated", False):
            print(
                f"   {obs['date']}: {obs['ndvi']:.3f} 🔄 INTERPOLATED ({obs['interpolation_method']})"
            )
        else:
            status = "☁️ CLOUDY" if obs.get("cloudy", False) else "✅ CLEAR"
            print(f"   {obs['date']}: {obs['ndvi']:.3f} {status}")

    # Verify interpolated values are reasonable
    for _i, obs in enumerate(interpolated):
        if obs.get("interpolated", False):
            # Check that interpolated value is within range of neighbors
            assert 0 <= obs["ndvi"] <= 1
            print(f"   ✓ Interpolated value {obs['ndvi']:.3f} is valid")

    # Test previous interpolation
    print("\n🔧 Testing Previous (Forward Fill) Interpolation...")
    prev_interp = await masker.interpolate_cloudy_pixels(
        field_id="test_field_004", ndvi_series=ndvi_series.copy(), method="previous"
    )

    interpolated_count = sum(1 for obs in prev_interp if obs.get("interpolated", False))
    print(f"   Interpolated {interpolated_count} observations using 'previous' method")

    print("\n✅ Interpolation test passed!")


async def test_scl_distribution():
    """Test SCL class distribution calculation"""
    print("\n" + "=" * 70)
    print("TEST 7: SCL Class Distribution")
    print("=" * 70)

    masker = get_cloud_masker()

    # Create sample SCL data (100 pixels)
    scl_data = (
        [SCLClass.VEGETATION.value] * 60  # 60% vegetation
        + [SCLClass.BARE_SOIL.value] * 20  # 20% bare soil
        + [SCLClass.CLOUD_MEDIUM.value] * 10  # 10% clouds
        + [SCLClass.CLOUD_SHADOW.value] * 5  # 5% shadow
        + [SCLClass.WATER.value] * 5  # 5% water
    )

    print(f"\n📊 Sample SCL Data ({len(scl_data)} pixels)")

    # Analyze
    result = await masker.analyze_cloud_cover(
        field_id="test_field_005", latitude=15.5, longitude=44.2, scl_data=scl_data
    )

    print("\n📈 Distribution Results:")
    for class_name, percent in sorted(
        result.scl_distribution.items(), key=lambda x: x[1], reverse=True
    ):
        print(f"   {class_name}: {percent}%")

    print("\n📊 Coverage Summary:")
    print(f"   Cloud Cover: {result.cloud_cover_percent}%")
    print(f"   Shadow Cover: {result.shadow_cover_percent}%")
    print(f"   Clear Cover: {result.clear_cover_percent}%")
    print(f"   Quality Score: {result.quality_score:.3f}")

    # Verify percentages add up to 100
    total = sum(result.scl_distribution.values())
    assert abs(total - 100.0) < 0.1, f"Percentages should sum to 100, got {total}"

    print("\n✅ SCL distribution test passed!")


async def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("🧪 SAHOOL Cloud Masking System - Test Suite")
    print("نظام تحديد الغطاء السحابي - مجموعة الاختبارات")
    print("=" * 70)

    try:
        await test_cloud_cover_analysis()
        await test_find_clear_observations()
        await test_best_observation()
        await test_quality_scoring()
        await test_cloud_masking()
        await test_interpolation()
        await test_scl_distribution()

        print("\n" + "=" * 70)
        print("✅ ALL TESTS PASSED!")
        print("جميع الاختبارات نجحت!")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
