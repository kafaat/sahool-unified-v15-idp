#!/usr/bin/env python3
"""
Quick test script for Yield Prediction functionality
Run with: python3 test_yield_prediction.py
"""

import asyncio
from datetime import datetime, timedelta, date
from src.yield_predictor import YieldPredictor


async def test_yield_predictor():
    """Test the yield predictor with sample data"""

    print("=" * 80)
    print("SAHOOL Crop Yield Prediction Test")
    print("=" * 80)

    predictor = YieldPredictor()

    # Test data: Wheat field in Yemen highlands
    field_id = "test-field-001"
    crop_code = "WHEAT"

    # Simulated NDVI time series (10 observations over growing season)
    # Typical wheat growth: starts low, peaks mid-season, declines at harvest
    ndvi_series = [0.25, 0.35, 0.50, 0.65, 0.72, 0.75, 0.70, 0.60, 0.45, 0.30]

    # Weather data (typical Yemen highlands)
    weather_data = {
        "temp_min_series": [12, 13, 14, 15, 16, 17, 18, 18, 17, 16] * 9,  # 90 days
        "temp_max_series": [24, 25, 26, 27, 28, 29, 30, 29, 28, 27] * 9,
        "precipitation_mm": 250,  # Total rainfall in mm
        "et0_mm": 300,  # Reference evapotranspiration
    }

    # Soil moisture (0-1 scale)
    soil_moisture = 0.45  # Moderate moisture

    # Planting date (60 days ago)
    planting_date = datetime.now() - timedelta(days=60)

    print("\nInput Parameters:")
    print(f"  Field ID: {field_id}")
    print(f"  Crop: {crop_code}")
    print(f"  Planting Date: {planting_date.date()}")
    print(f"  Field Area: 1.0 ha")
    print(f"  NDVI Observations: {len(ndvi_series)}")
    print(f"  NDVI Peak: {max(ndvi_series):.2f}")
    print(f"  Precipitation: {weather_data['precipitation_mm']} mm")
    print(f"  Soil Moisture: {soil_moisture:.2f}")

    # Run prediction
    print("\n" + "-" * 80)
    print("Running Yield Prediction...")
    print("-" * 80)

    prediction = await predictor.predict_yield(
        field_id=field_id,
        crop_code=crop_code,
        ndvi_series=ndvi_series,
        weather_data=weather_data,
        soil_moisture=soil_moisture,
        planting_date=planting_date,
        field_area_ha=1.0,
    )

    # Display results
    print("\nPREDICTION RESULTS:")
    print("=" * 80)
    print(f"\nCrop: {prediction.crop_name_en} ({prediction.crop_name_ar})")
    print(f"Growth Stage: {prediction.growth_stage}")
    if prediction.days_to_harvest:
        print(f"Days to Harvest: {prediction.days_to_harvest}")

    print(f"\nYield Prediction:")
    print(f"  Predicted Yield: {prediction.predicted_yield_ton_ha:.2f} ton/ha")
    print(f"  Confidence: {prediction.confidence * 100:.1f}%")
    print(
        f"  Range: {prediction.yield_range_min:.2f} - {prediction.yield_range_max:.2f} ton/ha"
    )

    print(f"\nComparisons:")
    print(f"  vs. Regional Average: {prediction.comparison_to_average:+.1f}%")
    print(f"  vs. Base Yield: {prediction.comparison_to_base:+.1f}%")

    print(f"\nYield Factors (0-1 scale, 1=optimal):")
    for factor, value in prediction.factors.items():
        bar = "█" * int(value * 20) + "░" * (20 - int(value * 20))
        print(f"  {factor:25s}: {bar} {value:.3f}")

    print(f"\nRecommendations (Arabic):")
    for i, rec in enumerate(prediction.recommendations_ar, 1):
        print(f"  {i}. {rec}")

    print(f"\nRecommendations (English):")
    for i, rec in enumerate(prediction.recommendations_en, 1):
        print(f"  {i}. {rec}")

    print("\n" + "=" * 80)
    print("Test completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_yield_predictor())
