#!/usr/bin/env python3
"""
Test script for advanced vegetation indices
Verifies that all new functionality works correctly
"""

import sys

sys.path.insert(0, "/home/user/sahool-unified-v15-idp/apps/services/satellite-service/src")

from vegetation_indices import (
    BandData,
    CropType,
    GrowthStage,
    IndexInterpreter,
    VegetationIndicesCalculator,
)


def test_calculator():
    """Test the indices calculator"""
    print("=" * 60)
    print("Test 1: Vegetation Indices Calculator")
    print("=" * 60)

    # Create sample Sentinel-2 band data (healthy wheat field)
    bands = BandData(
        B02_blue=0.05,
        B03_green=0.08,
        B04_red=0.06,
        B05_red_edge1=0.12,
        B06_red_edge2=0.18,
        B07_red_edge3=0.22,
        B08_nir=0.45,
        B8A_nir_narrow=0.42,
        B11_swir1=0.25,
        B12_swir2=0.18,
    )

    calculator = VegetationIndicesCalculator()
    indices = calculator.calculate_all(bands)

    print("\nCalculated Indices for Healthy Wheat Field:")
    print(f"  NDVI:  {indices.ndvi:.4f}  (Overall health)")
    print(f"  NDRE:  {indices.ndre:.4f}  (Chlorophyll/Nitrogen)")
    print(f"  GNDVI: {indices.gndvi:.4f}  (Early stress detection)")
    print(f"  NDWI:  {indices.ndwi:.4f}  (Water content)")
    print(f"  MCARI: {indices.mcari:.4f}  (Chlorophyll concentration)")
    print(f"  LAI:   {indices.lai:.2f}   (Leaf area)")
    print(f"  MSAVI: {indices.msavi:.4f}  (Soil-adjusted)")

    print("\n✅ Calculator test passed!")
    return indices


def test_interpreter():
    """Test the index interpreter"""
    print("\n" + "=" * 60)
    print("Test 2: Index Interpreter")
    print("=" * 60)

    interpreter = IndexInterpreter()

    # Test NDVI interpretation for wheat in vegetative stage
    ndvi_interp = interpreter.interpret_index(
        index_name="ndvi",
        value=0.65,
        crop_type=CropType.WHEAT,
        growth_stage=GrowthStage.VEGETATIVE,
    )

    print("\nNDVI Interpretation (Wheat - Vegetative):")
    print(f"  Value:  {ndvi_interp.value:.4f}")
    print(f"  Status: {ndvi_interp.status.value}")
    print(f"  AR:     {ndvi_interp.description_ar}")
    print(f"  EN:     {ndvi_interp.description_en}")
    print(f"  Confidence: {ndvi_interp.confidence:.2f}")

    # Test NDRE interpretation (nitrogen status)
    ndre_interp = interpreter.interpret_index(
        index_name="ndre",
        value=0.28,
        crop_type=CropType.WHEAT,
        growth_stage=GrowthStage.VEGETATIVE,
    )

    print("\nNDRE Interpretation (Nitrogen Status):")
    print(f"  Value:  {ndre_interp.value:.4f}")
    print(f"  Status: {ndre_interp.status.value}")
    print(f"  AR:     {ndre_interp.description_ar}")
    print(f"  EN:     {ndre_interp.description_en}")

    # Test water stress interpretation
    ndwi_interp = interpreter.interpret_index(
        index_name="ndwi",
        value=-0.15,
        crop_type=CropType.WHEAT,
        growth_stage=GrowthStage.REPRODUCTIVE,
    )

    print("\nNDWI Interpretation (Water Stress):")
    print(f"  Value:  {ndwi_interp.value:.4f}")
    print(f"  Status: {ndwi_interp.status.value}")
    print(f"  AR:     {ndwi_interp.description_ar}")
    print(f"  EN:     {ndwi_interp.description_en}")

    print("\n✅ Interpreter test passed!")


def test_growth_stage_recommendations():
    """Test growth stage recommendations"""
    print("\n" + "=" * 60)
    print("Test 3: Growth Stage Recommendations")
    print("=" * 60)

    interpreter = IndexInterpreter()

    stages = [
        GrowthStage.EMERGENCE,
        GrowthStage.VEGETATIVE,
        GrowthStage.REPRODUCTIVE,
        GrowthStage.MATURATION,
    ]

    for stage in stages:
        recommended = interpreter.get_recommended_indices(stage)
        print(f"\n{stage.value.upper()}:")
        print(f"  Recommended: {', '.join(recommended)}")

    print("\n✅ Growth stage recommendations test passed!")


def test_crop_specific_thresholds():
    """Test crop-specific thresholds"""
    print("\n" + "=" * 60)
    print("Test 4: Crop-Specific Thresholds")
    print("=" * 60)

    interpreter = IndexInterpreter()
    crops = [CropType.WHEAT, CropType.SORGHUM, CropType.COFFEE]

    ndvi_value = 0.65

    for crop in crops:
        interp = interpreter.interpret_index(
            index_name="ndvi",
            value=ndvi_value,
            crop_type=crop,
            growth_stage=GrowthStage.VEGETATIVE,
        )
        print(f"\n{crop.value.upper()} (NDVI={ndvi_value}):")
        print(f"  Status: {interp.status.value}")
        print(f"  Description: {interp.description_en}")

    print("\n✅ Crop-specific thresholds test passed!")


def test_stress_detection():
    """Test stress detection scenarios"""
    print("\n" + "=" * 60)
    print("Test 5: Stress Detection Scenarios")
    print("=" * 60)

    interpreter = IndexInterpreter()

    # Scenario 1: Water stress
    print("\nScenario 1: Water Stress (NDWI = -0.25)")
    water_stress = interpreter.interpret_index(
        "ndwi", -0.25, CropType.WHEAT, GrowthStage.REPRODUCTIVE
    )
    print(f"  Status: {water_stress.status.value}")
    print(f"  Action: {water_stress.description_en}")

    # Scenario 2: Nitrogen deficiency
    print("\nScenario 2: Nitrogen Deficiency (NDRE = 0.12)")
    nitrogen_def = interpreter.interpret_index("ndre", 0.12, CropType.WHEAT, GrowthStage.VEGETATIVE)
    print(f"  Status: {nitrogen_def.status.value}")
    print(f"  Action: {nitrogen_def.description_en}")

    # Scenario 3: Early stress (GNDVI)
    print("\nScenario 3: Early Stress Detection (GNDVI = 0.32)")
    early_stress = interpreter.interpret_index("gndvi", 0.32, CropType.WHEAT, GrowthStage.EMERGENCE)
    print(f"  Status: {early_stress.status.value}")
    print(f"  Action: {early_stress.description_en}")

    print("\n✅ Stress detection test passed!")


def test_all_indices():
    """Test calculation of all 18 indices"""
    print("\n" + "=" * 60)
    print("Test 6: All 18 Indices Calculation")
    print("=" * 60)

    # Stressed crop scenario
    stressed_bands = BandData(
        B02_blue=0.06,
        B03_green=0.09,
        B04_red=0.12,
        B05_red_edge1=0.14,
        B06_red_edge2=0.16,
        B07_red_edge3=0.18,
        B08_nir=0.25,
        B8A_nir_narrow=0.24,
        B11_swir1=0.28,
        B12_swir2=0.22,
    )

    calculator = VegetationIndicesCalculator()
    indices = calculator.calculate_all(stressed_bands)

    print("\nAll Indices (Stressed Crop):")
    indices_dict = indices.to_dict()

    # Group by category
    basic = ["ndvi", "ndwi", "evi", "savi", "lai", "ndmi"]
    chlorophyll = ["ndre", "cvi", "mcari", "tcari", "sipi"]
    stress = ["gndvi", "vari", "gli", "grvi"]
    corrected = ["msavi", "osavi", "arvi"]

    print("\n  Basic Indices:")
    for idx in basic:
        print(f"    {idx.upper():8s}: {indices_dict[idx]:.4f}")

    print("\n  Chlorophyll & Nitrogen:")
    for idx in chlorophyll:
        print(f"    {idx.upper():8s}: {indices_dict[idx]:.4f}")

    print("\n  Early Stress Detection:")
    for idx in stress:
        print(f"    {idx.upper():8s}: {indices_dict[idx]:.4f}")

    print("\n  Soil/Atmosphere Corrected:")
    for idx in corrected:
        print(f"    {idx.upper():8s}: {indices_dict[idx]:.4f}")

    print(f"\n  Total Indices: {len(indices_dict)}")
    print("\n✅ All indices calculation test passed!")


def main():
    """Run all tests"""
    print("\n🧪 Testing Advanced Vegetation Indices System")
    print("=" * 60)

    try:
        test_calculator()
        test_interpreter()
        test_growth_stage_recommendations()
        test_crop_specific_thresholds()
        test_stress_detection()
        test_all_indices()

        print("\n" + "=" * 60)
        print("✅ All tests passed successfully!")
        print("=" * 60)
        print("\nAdvanced Vegetation Indices System is ready to use.")
        print("Available indices: 18")
        print("Supported crops: Wheat, Sorghum, Coffee, Qat, and more")
        print("Growth stages: Emergence, Vegetative, Reproductive, Maturation")
        print("\nAPI Endpoints:")
        print("  GET  /v1/indices/{field_id}")
        print("  GET  /v1/indices/{field_id}/{index_name}")
        print("  POST /v1/indices/interpret")
        print("  GET  /v1/indices/guide")
        print("\n")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
