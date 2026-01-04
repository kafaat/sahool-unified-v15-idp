"""
SAHOOL Yield Ensemble Model - Usage Examples
أمثلة استخدام نموذج مجموعة التنبؤ بالإنتاج

This file demonstrates how to use the YieldEnsembleModel for yield prediction.
يوضح هذا الملف كيفية استخدام نموذج YieldEnsembleModel للتنبؤ بالإنتاج.

Usage:
  python3 yield_ensemble_example.py

Or from parent directory:
  cd /path/to/ai-agents-core/src
  python3 -m models.yield_ensemble_example
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.crop_parameters import Region, get_all_crop_ids, get_crop_parameters
from models.yield_ensemble import FieldData, YieldEnsembleModel


def example_basic_prediction():
    """
    Basic yield prediction example
    مثال أساسي للتنبؤ بالإنتاج
    """
    print("=" * 70)
    print("Example 1: Basic Yield Prediction")
    print("مثال 1: تنبؤ أساسي بالإنتاج")
    print("=" * 70)

    # Create field data - إنشاء بيانات الحقل
    field = FieldData(
        field_id="FIELD-001",
        crop_id="wheat",
        region=Region.HIGHLANDS,
        area_hectares=10.0,

        # NDVI data - بيانات NDVI
        ndvi_current=0.70,
        ndvi_peak=0.73,

        # Climate data - بيانات المناخ
        accumulated_gdd=1800,
        current_temperature=20.0,

        # Water data - بيانات المياه
        soil_moisture_current=60.0,
        total_irrigation_mm=350,
        total_rainfall_mm=150,

        # Soil data - بيانات التربة
        soil_ph=6.5,
        soil_ec=2.0,
        soil_nutrient_score=0.8,

        # Crop status - حالة المحصول
        days_since_planting=100
    )

    # Create model and predict - إنشاء النموذج والتنبؤ
    model = YieldEnsembleModel()
    prediction = model.predict(field)

    # Display results - عرض النتائج
    print(f"\nPredicted Yield: {prediction.predicted_yield_kg_per_hectare:.1f} kg/ha")
    print(f"Confidence: {prediction.confidence:.1%}")
    print(f"Total Revenue: {prediction.estimated_total_revenue:,.0f} YER")
    print(f"Days to Harvest: {prediction.days_to_harvest} days")


def example_with_historical_data():
    """
    Prediction with historical yield data
    التنبؤ مع بيانات الإنتاج التاريخية
    """
    print("\n\n" + "=" * 70)
    print("Example 2: Prediction with Historical Data")
    print("مثال 2: التنبؤ مع البيانات التاريخية")
    print("=" * 70)

    field = FieldData(
        field_id="FIELD-002",
        crop_id="tomato",
        region=Region.TIHAMA,
        area_hectares=3.0,
        ndvi_current=0.68,
        accumulated_gdd=1400,
        current_temperature=28.0,
        soil_moisture_current=55.0,
        total_irrigation_mm=500,
        total_rainfall_mm=80,
        soil_ph=6.2,
        days_since_planting=70,

        # Historical yields from past seasons - إنتاج تاريخي من المواسم السابقة
        historical_yields=[24000, 26000, 25500, 27000]
    )

    model = YieldEnsembleModel()
    prediction = model.predict(field)

    print(f"\nHistorical Yields: {field.historical_yields}")
    print(f"Predicted Yield: {prediction.predicted_yield_kg_per_hectare:,.0f} kg/ha")
    print(f"Confidence: {prediction.confidence:.1%}")

    # Show confidence metrics - عرض مقاييس الثقة
    print("\nConfidence Breakdown:")
    print(f"  Data Completeness: {prediction.confidence_metrics.data_completeness:.1%}")
    print(f"  Model Agreement: {prediction.confidence_metrics.model_agreement:.1%}")
    print(f"  Historical Accuracy: {prediction.confidence_metrics.historical_accuracy:.1%}")


def example_limiting_factors_and_recommendations():
    """
    Identify limiting factors and get recommendations
    تحديد العوامل المحددة والحصول على التوصيات
    """
    print("\n\n" + "=" * 70)
    print("Example 3: Limiting Factors and Recommendations")
    print("مثال 3: العوامل المحددة والتوصيات")
    print("=" * 70)

    # Field with multiple stress factors - حقل مع عوامل إجهاد متعددة
    field = FieldData(
        field_id="FIELD-003",
        crop_id="potato",
        region=Region.HIGHLANDS,
        area_hectares=5.0,

        # Poor NDVI indicating plant health issues
        ndvi_current=0.50,

        # Insufficient thermal time
        accumulated_gdd=900,
        current_temperature=18.0,

        # Water stress
        soil_moisture_current=30.0,
        total_irrigation_mm=200,
        total_rainfall_mm=100,

        # Soil issues
        soil_ph=5.2,  # Too acidic
        soil_ec=1.8,
        soil_nutrient_score=0.5,

        days_since_planting=70
    )

    model = YieldEnsembleModel()
    prediction = model.predict(field)

    print(f"\nPredicted Yield: {prediction.predicted_yield_kg_per_hectare:,.0f} kg/ha")
    print(f"Confidence: {prediction.confidence:.1%}")

    print(f"\nLimiting Factors ({len(prediction.limiting_factors)}):")
    for i, factor in enumerate(prediction.limiting_factors, 1):
        print(f"\n  {i}. {factor['factor_ar']} ({factor['factor']})")
        print(f"     Severity: {factor['severity']}")
        print(f"     Impact: {factor['impact_pct']:.1f}%")
        print(f"     {factor['description_ar']}")

    print(f"\nRecommendations ({len(prediction.recommendations)}):")
    for i, rec in enumerate(prediction.recommendations, 1):
        print(f"\n  {i}. [{rec['priority'].upper()}] {rec['action_ar']}")
        print(f"     {rec['details_ar']}")
        print(f"     Expected Impact: {rec['expected_impact']}")


def example_model_explanation():
    """
    Get detailed model explanation
    الحصول على شرح مفصل للنموذج
    """
    print("\n\n" + "=" * 70)
    print("Example 4: Detailed Model Explanation")
    print("مثال 4: شرح مفصل للنموذج")
    print("=" * 70)

    field = FieldData(
        field_id="FIELD-004",
        crop_id="coffee",
        region=Region.HIGHLANDS,
        area_hectares=2.0,
        ndvi_current=0.64,
        accumulated_gdd=1900,
        current_temperature=21.0,
        soil_moisture_current=65.0,
        total_irrigation_mm=900,
        total_rainfall_mm=400,
        soil_ph=6.0,
        soil_ec=0.9,
        soil_nutrient_score=0.85,
        days_since_planting=220,
        historical_yields=[780, 820, 850]
    )

    model = YieldEnsembleModel()
    prediction = model.predict(field)

    # Get feature importance - الحصول على أهمية الميزات
    print("\nFeature Importance (Model Weights):")
    importance = model.get_feature_importance()
    for feature, weight in importance.items():
        print(f"  {feature:30s}: {weight:.1%}")

    # Get detailed explanation - الحصول على شرح مفصل
    print("\nDetailed Prediction Explanation:")
    explanation = model.explain_prediction(prediction)

    print("\nSub-Model Predictions:")
    for model_name, pred_value in explanation['sub_models']['predictions'].items():
        contrib = explanation['sub_models']['contributions'][model_name]
        print(f"  {model_name:12s}: {pred_value:7.1f} kg/ha "
              f"(weight: {contrib['weight']:.1%}, "
              f"confidence: {contrib['confidence']:.1%})")

    print("\nConfidence Interval:")
    for level, value in explanation['summary'].items():
        if 'confidence' not in level.lower():
            continue
        print(f"  {level}: {value}")


def example_multi_crop_comparison():
    """
    Compare predictions across different crops
    مقارنة التنبؤات عبر محاصيل مختلفة
    """
    print("\n\n" + "=" * 70)
    print("Example 5: Multi-Crop Comparison")
    print("مثال 5: مقارنة متعددة المحاصيل")
    print("=" * 70)

    # Define common field conditions
    base_field = {
        "field_id": "MULTI-001",
        "region": Region.TIHAMA,
        "area_hectares": 1.0,
        "ndvi_current": 0.65,
        "accumulated_gdd": 1500,
        "current_temperature": 30.0,
        "soil_moisture_current": 50.0,
        "total_irrigation_mm": 400,
        "total_rainfall_mm": 100,
        "soil_ph": 7.0,
        "soil_ec": 2.0,
        "days_since_planting": 80
    }

    # Test different crops - اختبار محاصيل مختلفة
    crops_to_test = ["tomato", "cucumber", "eggplant", "pepper"]

    model = YieldEnsembleModel()
    results = []

    for crop_id in crops_to_test:
        field = FieldData(crop_id=crop_id, **base_field)
        prediction = model.predict(field)

        crop_params = get_crop_parameters(crop_id)
        results.append({
            'crop': crop_params.name_ar,
            'yield_kg_ha': prediction.predicted_yield_kg_per_hectare,
            'confidence': prediction.confidence,
            'revenue': prediction.estimated_revenue_per_ha
        })

    # Display comparison - عرض المقارنة
    print(f"\n{'Crop':<20} {'Yield (kg/ha)':>15} {'Confidence':>12} {'Revenue (YER)':>15}")
    print("-" * 70)
    for r in sorted(results, key=lambda x: x['revenue'], reverse=True):
        print(f"{r['crop']:<20} {r['yield_kg_ha']:>15,.0f} {r['confidence']:>11.1%} {r['revenue']:>15,.0f}")


def example_regional_comparison():
    """
    Compare same crop across different regions
    مقارنة نفس المحصول عبر مناطق مختلفة
    """
    print("\n\n" + "=" * 70)
    print("Example 6: Regional Comparison (Wheat)")
    print("مثال 6: مقارنة إقليمية (القمح)")
    print("=" * 70)

    base_field = {
        "field_id": "REGIONAL-001",
        "crop_id": "wheat",
        "area_hectares": 5.0,
        "ndvi_current": 0.70,
        "accumulated_gdd": 1800,
        "current_temperature": 20.0,
        "soil_moisture_current": 55.0,
        "total_irrigation_mm": 350,
        "total_rainfall_mm": 120,
        "soil_ph": 6.8,
        "soil_ec": 2.5,
        "days_since_planting": 95
    }

    regions = [Region.HIGHLANDS, Region.TIHAMA, Region.HADHRAMAUT]
    model = YieldEnsembleModel()

    print(f"\n{'Region':<20} {'Yield (kg/ha)':>15} {'Multiplier':>12} {'Total Revenue':>15}")
    print("-" * 70)

    for region in regions:
        field = FieldData(region=region, **base_field)
        prediction = model.predict(field)

        wheat_params = get_crop_parameters("wheat")
        regional_adj = wheat_params.regional_adjustments.get(region)
        multiplier = regional_adj.yield_multiplier if regional_adj else 1.0

        print(f"{region.value:<20} {prediction.predicted_yield_kg_per_hectare:>15,.0f} "
              f"{multiplier:>11.2f}x {prediction.estimated_total_revenue:>15,.0f}")


def main():
    """Run all examples - تشغيل جميع الأمثلة"""

    print("\n" + "=" * 70)
    print("SAHOOL Yield Ensemble Model - Complete Examples")
    print("نموذج مجموعة التنبؤ بالإنتاج - أمثلة كاملة")
    print("=" * 70)

    # Show available crops - عرض المحاصيل المتاحة
    print(f"\nAvailable Crops: {len(get_all_crop_ids())}")
    print(", ".join(get_all_crop_ids()))

    # Run examples - تشغيل الأمثلة
    example_basic_prediction()
    example_with_historical_data()
    example_limiting_factors_and_recommendations()
    example_model_explanation()
    example_multi_crop_comparison()
    example_regional_comparison()

    print("\n\n" + "=" * 70)
    print("All examples completed successfully!")
    print("جميع الأمثلة اكتملت بنجاح!")
    print("=" * 70)


if __name__ == "__main__":
    main()
