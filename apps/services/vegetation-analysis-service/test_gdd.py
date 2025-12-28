#!/usr/bin/env python3
"""
Quick test script for GDD tracker functionality.
Tests the core GDD calculation methods and crop data.
"""

import sys
sys.path.insert(0, 'src')

from src.gdd_tracker import GDDTracker, GDDMethod

def test_gdd_calculations():
    """Test GDD calculation methods"""
    tracker = GDDTracker()

    print("Testing GDD Calculation Methods")
    print("=" * 60)

    # Test case: Tmax=25°C, Tmin=15°C, Base=10°C
    temp_max = 25.0
    temp_min = 15.0
    base_temp = 10.0
    upper_temp = 30.0

    print(f"\nTest Case:")
    print(f"  Tmax: {temp_max}°C")
    print(f"  Tmin: {temp_min}°C")
    print(f"  Base: {base_temp}°C")
    print(f"  Upper: {upper_temp}°C")
    print()

    # Simple method
    gdd_simple = tracker.calculate_daily_gdd(
        temp_min, temp_max, base_temp, method="simple"
    )
    print(f"Simple Method: {gdd_simple:.1f} GDD")
    print(f"  Formula: ((25 + 15) / 2) - 10 = 10.0")

    # Modified method
    gdd_modified = tracker.calculate_daily_gdd(
        temp_min, temp_max, base_temp, upper_temp, method="modified"
    )
    print(f"Modified Method: {gdd_modified:.1f} GDD")

    # Sine method
    gdd_sine = tracker.calculate_daily_gdd(
        temp_min, temp_max, base_temp, upper_temp, method="sine"
    )
    print(f"Sine Method: {gdd_sine:.1f} GDD")

    print("\n" + "=" * 60)

    # Test edge cases
    print("\nEdge Cases:")

    # Both temps below base
    gdd_cold = tracker.calculate_daily_gdd(5, 8, 10, method="simple")
    print(f"  Cold day (Tmax=8, Tmin=5, Base=10): {gdd_cold:.1f} GDD")

    # Very hot day
    gdd_hot = tracker.calculate_daily_gdd(30, 40, 10, 35, method="modified")
    print(f"  Hot day (Tmax=40, Tmin=30, Base=10, Upper=35): {gdd_hot:.1f} GDD")

    print()


def test_crop_data():
    """Test crop GDD requirements data"""
    tracker = GDDTracker()

    print("Testing Crop GDD Requirements")
    print("=" * 60)

    # Get all crops
    crops = tracker.get_all_crops()

    print(f"\nTotal Crops Supported: {len(crops)}")
    print()

    # Show first 10 crops
    print("Sample Crops:")
    for crop in crops[:10]:
        print(f"  {crop['crop_code']:15} | {crop['crop_name_en']:20} | {crop['crop_name_ar']:15} | Base: {crop['base_temp_c']:4.1f}°C | Total: {crop['total_gdd_required']:5.0f} GDD")

    print()

    # Test specific crop - WHEAT
    print("Detailed Wheat Requirements:")
    print("-" * 60)

    wheat_params = tracker.CROP_GDD_REQUIREMENTS["WHEAT"]
    print(f"Crop: {wheat_params['name_en']} ({wheat_params['name_ar']})")
    print(f"Total GDD Required: {wheat_params['total']}")
    print(f"\nGrowth Stages:")

    for i, stage in enumerate(wheat_params['stages'], 1):
        print(f"  {i}. {stage['name_en']:20} ({stage['name_ar']:20}) - {stage['gdd']:5.0f} GDD")

    print()


def test_growth_stages():
    """Test growth stage determination"""
    tracker = GDDTracker()

    print("Testing Growth Stage Determination")
    print("=" * 60)

    crop = "WHEAT"
    test_gdds = [0, 150, 500, 1100, 1500, 2000, 2500]

    print(f"\nCrop: {crop}")
    print(f"GDD → Stage\n")

    for gdd in test_gdds:
        current_en, current_ar, next_en, next_ar, gdd_to_next = tracker.get_current_stage(crop, gdd)
        print(f"  {gdd:5.0f} GDD → {current_en:20} ({current_ar:20}) | Next: {next_en:20} in {gdd_to_next:5.1f} GDD")

    print()


def test_all_crops_valid():
    """Verify all crops have valid data"""
    tracker = GDDTracker()

    print("Validating All Crop Data")
    print("=" * 60)

    errors = []

    for crop_code in tracker.CROP_GDD_REQUIREMENTS.keys():
        try:
            # Check base temp exists
            if crop_code not in tracker.CROP_BASE_TEMPS:
                errors.append(f"{crop_code}: Missing base temperature")
                continue

            # Check requirements
            req = tracker.CROP_GDD_REQUIREMENTS[crop_code]

            # Validate stages
            if not req.get('stages'):
                errors.append(f"{crop_code}: No stages defined")

            # Check stage GDDs are increasing
            prev_gdd = 0
            for stage in req['stages']:
                if stage['gdd'] <= prev_gdd:
                    errors.append(f"{crop_code}: Stage GDDs not increasing")
                prev_gdd = stage['gdd']

            # Check total GDD
            if req['total'] <= 0:
                errors.append(f"{crop_code}: Invalid total GDD")

            # Check last stage matches total
            last_stage_gdd = req['stages'][-1]['gdd'] if req['stages'] else 0
            if last_stage_gdd != req['total']:
                errors.append(f"{crop_code}: Last stage GDD ({last_stage_gdd}) != total ({req['total']})")

        except Exception as e:
            errors.append(f"{crop_code}: {str(e)}")

    if errors:
        print("\nERRORS FOUND:")
        for error in errors:
            print(f"  ❌ {error}")
    else:
        print("\n✅ All crop data is valid!")
        print(f"   {len(tracker.CROP_GDD_REQUIREMENTS)} crops validated successfully")

    print()


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("GDD TRACKER TEST SUITE")
    print("=" * 60 + "\n")

    try:
        test_gdd_calculations()
        test_crop_data()
        test_growth_stages()
        test_all_crops_valid()

        print("=" * 60)
        print("✅ All tests completed successfully!")
        print("=" * 60 + "\n")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
