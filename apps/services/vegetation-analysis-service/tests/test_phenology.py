"""
Test Crop Phenology Detection
اختبار كشف مراحل نمو المحاصيل
"""

import sys
from pathlib import Path
from datetime import date, datetime, timedelta

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from phenology_detector import PhenologyDetector, GrowthStage


def test_wheat_phenology():
    """Test wheat phenology detection"""
    print("=" * 80)
    print("Testing Wheat Phenology Detection")
    print("=" * 80)

    detector = PhenologyDetector()

    # Simulate wheat NDVI time series over 120 days
    planting_date = date(2024, 11, 1)  # November planting (winter wheat in Yemen)
    ndvi_series = []

    # Generate realistic NDVI progression for wheat
    days = 120
    for day in range(days):
        current_date = planting_date + timedelta(days=day)

        # Simulate wheat growth curve
        if day < 10:  # Germination
            ndvi = 0.15 + (day / 10) * 0.10
        elif day < 25:  # Emergence
            ndvi = 0.25 + ((day - 10) / 15) * 0.15
        elif day < 55:  # Tillering (rapid growth)
            ndvi = 0.40 + ((day - 25) / 30) * 0.30
        elif day < 75:  # Stem elongation and booting (peak)
            ndvi = 0.70 + ((day - 55) / 20) * 0.05
        elif day < 87:  # Flowering
            ndvi = 0.75 - ((day - 75) / 12) * 0.03
        elif day < 105:  # Ripening (decline)
            ndvi = 0.72 - ((day - 87) / 18) * 0.27
        else:  # Senescence
            ndvi = 0.45 - ((day - 105) / 15) * 0.20

        ndvi_series.append(
            {
                "date": current_date.isoformat(),
                "value": round(max(0.1, min(0.85, ndvi)), 4),
            }
        )

    # Test at different points in season
    test_points = [
        (30, "Tillering stage"),
        (60, "Stem elongation"),
        (80, "Flowering"),
        (95, "Ripening"),
        (115, "Senescence"),
    ]

    for day_idx, description in test_points:
        print(f"\n--- Day {day_idx}: {description} ---")
        test_series = ndvi_series[:day_idx]

        result = detector.detect_current_stage(
            field_id="field_test_001",
            crop_type="wheat",
            ndvi_series=test_series,
            planting_date=planting_date,
        )

        print(
            f"Current Stage: {result.current_stage.label_en} ({result.current_stage.label_ar})"
        )
        print(f"Days in Stage: {result.days_in_stage}")
        print(
            f"Next Stage: {result.expected_next_stage.label_en} in {result.days_to_next_stage} days"
        )
        print(f"Season Progress: {result.season_progress_percent:.1f}%")
        print(f"NDVI: {result.ndvi_at_detection}")
        print(f"Confidence: {result.confidence:.2f}")
        print(
            f"Recommendations (AR): {result.recommendations_ar[0] if result.recommendations_ar else 'None'}"
        )


def test_timeline_generation():
    """Test phenology timeline generation"""
    print("\n" + "=" * 80)
    print("Testing Phenology Timeline Generation")
    print("=" * 80)

    detector = PhenologyDetector()

    crops_to_test = ["wheat", "sorghum", "tomato", "coffee"]

    for crop in crops_to_test:
        print(f"\n--- {crop.upper()} Timeline ---")
        planting_date = date(2024, 11, 1)

        timeline = detector.get_phenology_timeline(
            field_id="field_timeline_001", crop_type=crop, planting_date=planting_date
        )

        print(f"Planting: {timeline.planting_date}")
        print(f"Harvest: {timeline.harvest_estimate}")
        print(f"Season Length: {timeline.season_length_days} days")
        print(f"\nStages:")
        for stage in timeline.stages[:3]:  # Show first 3 stages
            print(
                f"  - {stage['stage_en']} ({stage['stage_ar']}): {stage['start_date']} to {stage['end_date']}"
            )

        if timeline.critical_periods:
            print(f"\nCritical Periods:")
            for cp in timeline.critical_periods:
                print(f"  - {cp['stage_en']}: {cp['reason_en']}")


def test_supported_crops():
    """Test listing supported crops"""
    print("\n" + "=" * 80)
    print("Supported Crops for Phenology Detection")
    print("=" * 80)

    detector = PhenologyDetector()
    crops = detector.get_supported_crops()

    print(f"\nTotal: {len(crops)} crops\n")

    # Group by category
    cereals = ["wheat", "sorghum", "millet"]
    vegetables = ["tomato", "potato", "onion"]
    legumes = ["faba_bean", "lentil"]
    cash_crops = ["coffee", "qat"]
    fruits = ["mango", "grape"]

    categories = [
        ("Cereals (الحبوب)", cereals),
        ("Vegetables (الخضروات)", vegetables),
        ("Legumes (البقوليات)", legumes),
        ("Cash Crops (المحاصيل النقدية)", cash_crops),
        ("Fruits (الفواكه)", fruits),
    ]

    for category, crop_list in categories:
        print(f"{category}:")
        for crop_info in crops:
            if crop_info["id"] in crop_list:
                print(
                    f"  - {crop_info['name_en']} ({crop_info['name_ar']}): {crop_info['season_length_days']} days"
                )
        print()


def test_recommendations():
    """Test stage-specific recommendations"""
    print("\n" + "=" * 80)
    print("Testing Stage-Specific Recommendations")
    print("=" * 80)

    detector = PhenologyDetector()

    test_cases = [
        ("wheat", GrowthStage.FLOWERING, "Critical flowering period"),
        ("tomato", GrowthStage.FRUIT_DEVELOPMENT, "Fruit development"),
        ("sorghum", GrowthStage.RIPENING, "Pre-harvest"),
    ]

    for crop_type, stage, description in test_cases:
        print(f"\n--- {crop_type.upper()} - {description} ---")
        crop_params = detector.YEMEN_CROP_SEASONS[crop_type]

        recommendations_ar, recommendations_en = detector._get_stage_recommendations(
            crop_type=crop_type,
            stage=stage,
            days_to_next=7,
            current_ndvi=0.6,
            crop_params=crop_params,
        )

        print("Recommendations (English):")
        for rec in recommendations_en[:3]:  # Show first 3
            print(f"  {rec}")

        print("\nRecommendations (Arabic):")
        for rec in recommendations_ar[:3]:
            print(f"  {rec}")


def test_sos_pos_eos_detection():
    """Test phenological event detection"""
    print("\n" + "=" * 80)
    print("Testing SOS/POS/EOS Detection")
    print("=" * 80)

    detector = PhenologyDetector()

    # Create a realistic NDVI curve
    base_date = date(2024, 11, 1)
    ndvi_series = []

    # Simulate complete season
    ndvi_curve = [
        0.12,
        0.14,
        0.16,
        0.18,
        0.21,  # Pre-SOS
        0.25,
        0.30,
        0.38,
        0.45,
        0.52,  # SOS - green-up
        0.58,
        0.63,
        0.68,
        0.71,
        0.73,  # Vegetative growth
        0.75,
        0.76,
        0.75,
        0.73,
        0.71,  # POS - peak
        0.68,
        0.64,
        0.58,
        0.52,
        0.45,  # Decline
        0.38,
        0.30,
        0.23,
        0.18,
        0.14,  # EOS - senescence
    ]

    for i, ndvi in enumerate(ndvi_curve):
        ndvi_series.append(
            {
                "date": (base_date + timedelta(days=i * 4)).isoformat(),  # Every 4 days
                "value": ndvi,
            }
        )

    result = detector.detect_current_stage(
        field_id="field_sos_test",
        crop_type="wheat",
        ndvi_series=ndvi_series,
        planting_date=base_date,
    )

    print(f"Start of Season (SOS): {result.sos_date}")
    print(f"Peak of Season (POS): {result.pos_date}")
    print(f"End of Season (EOS): {result.eos_date}")
    print(f"Estimated Harvest: {result.estimated_harvest_date}")

    if result.sos_date and result.eos_date:
        season_length = (result.eos_date - result.sos_date).days
        print(f"Detected Season Length: {season_length} days")


if __name__ == "__main__":
    print("🌱 SAHOOL Crop Phenology Detector - Test Suite")
    print("=" * 80)
    print()

    try:
        test_wheat_phenology()
        test_timeline_generation()
        test_supported_crops()
        test_recommendations()
        test_sos_pos_eos_detection()

        print("\n" + "=" * 80)
        print("✅ All tests completed successfully!")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
