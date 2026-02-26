# shared/ml_irrigation

ML Irrigation Prediction Module | وحدة التنبؤ بالري باستخدام التعلم الآلي

A machine learning-based irrigation decision engine for the SAHOOL platform. Combines agronomic rule-based calculations with optional sklearn-compatible ML models in an ensemble approach. Outputs bilingual (Arabic/English) irrigation recommendations with confidence scoring, optimal timing, and contributing factor explanations.

## File Structure

```
shared/ml_irrigation/
├── __init__.py     # Module exports and comprehensive usage documentation
├── models.py       # Feature models (WeatherFeatures, SoilFeatures, CropFeatures) and prediction models
├── predictor.py    # IrrigationPredictor: rule-based, ML, and ensemble prediction engine
└── optimizer.py    # WaterOptimizer: usage optimization, anomaly detection, pattern analysis
```

## Key Components

### Feature Models (`models.py`)

Three feature classes capture all inputs required for prediction:

| Class | Key Fields |
|-------|-----------|
| `WeatherFeatures` | temperature_current/max/min, humidity, precipitation_probability/amount, wind_speed/direction, solar_radiation, cloud_cover, et0 |
| `SoilFeatures` | moisture_current/field_capacity/wilting_point/depth_cm, soil_type, infiltration_rate, water_holding_capacity, ec, ph, soil_temperature |
| `CropFeatures` | crop_type, crop_type_ar, growth_stage, days_after_planting, kc, root_depth_cm, ndvi, area_ha |

`IrrigationFeatures` combines all three plus `irrigation_type` and `system_efficiency`.

Prediction output model `IrrigationPrediction` contains: `irrigation_needed`, `recommended_amount_mm`, `recommended_amount_liters`, `urgency`, `optimal_time`, `confidence`, `confidence_level`, `recommendation`, `recommendation_ar`, `reasoning`, `reasoning_ar`, `factors`.

Enums:
- `IrrigationUrgency`: CRITICAL / HIGH / MEDIUM / LOW / NONE
- `CropStage`: GERMINATION / SEEDLING / VEGETATIVE / TILLERING / FLOWERING / GRAIN_FILL / MATURITY / HARVEST
- `SoilType`: SANDY / LOAMY / CLAY / SILTY / SANDY_LOAM / CLAY_LOAM / SILT_LOAM
- `IrrigationType`: DRIP / SPRINKLER / FLOOD / CENTER_PIVOT / FURROW / SUBSURFACE
- `AnomalyType`: OVER_IRRIGATION / UNDER_IRRIGATION / SENSOR_DRIFT / SYSTEM_LEAK / UNUSUAL_PATTERN / SCHEDULING_ERROR
- `PredictionConfidence`: VERY_HIGH / HIGH / MEDIUM / LOW / VERY_LOW

### Irrigation Predictor (`predictor.py`)

`IrrigationPredictor` implements a three-path prediction pipeline:

1. **Rule-based path**: Uses FAO-56 crop coefficients (Kc), soil depletion fraction, crop-stage depletion allowances, effective rainfall (USDA SCS method), and system efficiency to calculate irrigation need and amount.

2. **ML model path** (optional): Accepts any sklearn-compatible model implementing `predict()` and `predict_proba()`. Converts features to a numeric vector via `IrrigationFeatures.to_feature_vector()`.

3. **Ensemble combination**: Weighted blend (configurable `rule_weight` / `model_weight`) of both paths.

Post-processing: historical record adjustment (effectiveness-rated), bilingual recommendation generation, and contributing factor extraction.

`CROP_COEFFICIENTS` table covers wheat, barley, tomato, date palm, and a default fallback - all by growth stage.

`PredictorConfig` key settings:
- `moisture_critical_threshold`: 25% (triggers CRITICAL urgency)
- `moisture_low_threshold`: 40% (triggers MEDIUM)
- `rain_probability_threshold`: 60% (delay recommendation)
- `depletion_allowances`: per-stage allowable depletion fractions
- `irrigation_efficiencies`: drip 0.90, sprinkler 0.75, flood 0.50, center_pivot 0.85, furrow 0.55, subsurface 0.95

### Water Optimizer (`optimizer.py`)

`WaterOptimizer` analyzes historical `IrrigationRecord` lists to find savings and flag anomalies.

- `optimize_water_usage(records, area_ha)` -> `WaterOptimizationResult` with savings_percent, recommendations
- `detect_irrigation_anomalies(records, current_reading)` -> list of `IrrigationAnomaly`
- `analyze_irrigation_patterns(records)` -> list of `HistoricalPattern`

`OPTIMAL_TIMING` dict maps irrigation types to best-practice hours (e.g., drip at 05:00, sprinkler at 06:00, flood at 04:00).

## Usage Example

```python
from datetime import datetime, UTC
from shared.ml_irrigation import (
    IrrigationPredictor,
    IrrigationFeatures,
    WeatherFeatures,
    SoilFeatures,
    CropFeatures,
    IrrigationType,
    CropStage,
    SoilType,
    predict_irrigation,
    optimize_water_usage,
    detect_irrigation_anomalies,
    IrrigationRecord,
)

# Build feature objects
weather = WeatherFeatures(
    temperature_current=30.0,
    temperature_max=38.0,
    temperature_min=22.0,
    humidity=38.0,
    precipitation_probability=5.0,
    precipitation_amount_mm=0.0,
    wind_speed=14.0,
    wind_direction=180.0,
    solar_radiation=850.0,
    cloud_cover=10.0,
    et0=6.2,
)

soil = SoilFeatures(
    moisture_current=28.0,           # Below low threshold (40%)
    moisture_field_capacity=45.0,
    moisture_wilting_point=15.0,
    moisture_depth_cm=30.0,
    soil_type=SoilType.LOAMY,
    infiltration_rate=15.0,
    water_holding_capacity=150.0,
    ec=1.1,
    ph=7.3,
    soil_temperature=28.0,
    timestamp=datetime.now(UTC),
)

crop = CropFeatures(
    crop_type="wheat",
    crop_type_ar="قمح",
    growth_stage=CropStage.FLOWERING,  # Critical stage - lower depletion allowance (0.35)
    days_after_planting=85,
    growth_stage_days=8,
    kc=1.15,                          # Wheat flowering Kc
    root_depth_cm=80.0,
    ndvi=0.68,
    area_ha=5.5,
)

# Quick single-call prediction
prediction = predict_irrigation(
    weather=weather,
    soil=soil,
    crop=crop,
    irrigation_type=IrrigationType.DRIP,
    system_efficiency=0.90,
)

print(f"Irrigation needed: {prediction.irrigation_needed}")
print(f"Amount: {prediction.recommended_amount_mm}mm ({prediction.recommended_amount_liters:.0f}L)")
print(f"Urgency: {prediction.urgency.value}")
print(f"Confidence: {prediction.confidence:.0%} ({prediction.confidence_level.value})")
print(f"Optimal time: {prediction.optimal_time.strftime('%H:%M')}")
print(f"Recommendation: {prediction.recommendation}")
print(f"التوصية: {prediction.recommendation_ar}")
print(f"Reasoning: {prediction.reasoning}")

# Contributing factors
for factor in prediction.factors:
    print(f"  {factor['name']}: {factor['value']} (impact: {factor['impact']})")

# Water usage optimization from historical records
records = [
    IrrigationRecord(
        record_id="REC-001",
        field_id="FIELD-003",
        irrigation_date=datetime.now(UTC),
        amount_mm=35.0,
        duration_hours=4.0,
        irrigation_type=IrrigationType.DRIP,
        effectiveness_rating=4.2,
    ),
]
result = optimize_water_usage(records, area_ha=5.5)
print(f"Potential savings: {result.savings_percent:.1f}%")

# Anomaly detection
anomalies = detect_irrigation_anomalies(records, current_reading=28.0)
for a in anomalies:
    print(f"{a.anomaly_type.value}: {a.description}")
```

## Version

1.0.0 | Author: SAHOOL Platform Team | Updated: January 2026
