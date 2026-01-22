"""
ML Irrigation Prediction Module
===============================
وحدة التنبؤ بالري باستخدام التعلم الآلي

A comprehensive ML-based irrigation prediction and optimization module
for the SAHOOL National Agricultural Intelligence Platform.

Features:
- Irrigation need prediction based on weather, soil, and crop data
- Water usage optimization recommendations
- Historical pattern analysis
- Anomaly detection for irrigation systems
- Bilingual support (Arabic/English)

Author: SAHOOL Platform Team
Updated: January 2026

Usage Example:
-------------
    from shared.ml_irrigation import (
        IrrigationPredictor,
        IrrigationFeatures,
        WeatherFeatures,
        SoilFeatures,
        CropFeatures,
        IrrigationType,
        predict_irrigation,
        optimize_water_usage,
        detect_irrigation_anomalies,
    )

    # Create feature objects
    weather = WeatherFeatures(
        temperature_current=28.0,
        temperature_max=35.0,
        temperature_min=22.0,
        humidity=45.0,
        precipitation_probability=10.0,
        precipitation_amount_mm=0.0,
        wind_speed=12.0,
        wind_direction=180.0,
        solar_radiation=800.0,
        cloud_cover=20.0,
        et0=5.5,
    )

    soil = SoilFeatures(
        moisture_current=35.0,
        moisture_field_capacity=45.0,
        moisture_wilting_point=15.0,
        moisture_depth_cm=30.0,
        soil_type=SoilType.LOAMY,
        infiltration_rate=15.0,
        water_holding_capacity=150.0,
        ec=1.2,
        ph=7.2,
        soil_temperature=25.0,
    )

    crop = CropFeatures(
        crop_type="wheat",
        crop_type_ar="قمح",
        growth_stage=CropStage.TILLERING,
        days_after_planting=45,
        growth_stage_days=10,
        kc=0.95,
        root_depth_cm=60.0,
        ndvi=0.72,
    )

    # Quick prediction
    prediction = predict_irrigation(weather, soil, crop)

    print(f"Irrigation needed: {prediction.irrigation_needed}")
    print(f"Amount: {prediction.recommended_amount_mm}mm")
    print(f"Urgency: {prediction.urgency.value}")
    print(f"Recommendation: {prediction.recommendation}")
    print(f"التوصية: {prediction.recommendation_ar}")

    # Water optimization
    from shared.ml_irrigation import IrrigationRecord, optimize_water_usage

    records = [...]  # Historical records
    optimization = optimize_water_usage(records, area_ha=10.5)
    print(f"Potential savings: {optimization.savings_percent}%")

    # Anomaly detection
    from shared.ml_irrigation import detect_irrigation_anomalies

    anomalies = detect_irrigation_anomalies(records, current_reading=45.0)
    for anomaly in anomalies:
        print(f"{anomaly.anomaly_type.value}: {anomaly.description}")
"""

# Version
__version__ = "1.0.0"

# Models - Data structures
from .models import (
    # Enums
    IrrigationUrgency,
    CropStage,
    SoilType,
    IrrigationType,
    AnomalyType,
    AnomalySeverity,
    PredictionConfidence,
    # Feature models
    WeatherFeatures,
    SoilFeatures,
    CropFeatures,
    IrrigationFeatures,
    # Prediction models
    IrrigationPrediction,
    WaterOptimizationResult,
    IrrigationAnomaly,
    HistoricalPattern,
    IrrigationRecord,
)

# Predictor - ML prediction logic
from .predictor import (
    IrrigationPredictor,
    PredictorConfig,
    predict_irrigation,
    get_predictor,
    # Constants
    CROP_COEFFICIENTS,
    URGENCY_MESSAGES,
)

# Optimizer - Water optimization
from .optimizer import (
    WaterOptimizer,
    OptimizerConfig,
    optimize_water_usage,
    detect_irrigation_anomalies,
    analyze_irrigation_patterns,
    get_optimizer,
    # Constants
    OPTIMAL_TIMING,
    ANOMALY_DESCRIPTIONS,
    ANOMALY_RECOMMENDATIONS,
)

# Export all public symbols
__all__ = [
    # Version
    "__version__",
    # Enums
    "IrrigationUrgency",
    "CropStage",
    "SoilType",
    "IrrigationType",
    "AnomalyType",
    "AnomalySeverity",
    "PredictionConfidence",
    # Feature models
    "WeatherFeatures",
    "SoilFeatures",
    "CropFeatures",
    "IrrigationFeatures",
    # Prediction models
    "IrrigationPrediction",
    "WaterOptimizationResult",
    "IrrigationAnomaly",
    "HistoricalPattern",
    "IrrigationRecord",
    # Predictor
    "IrrigationPredictor",
    "PredictorConfig",
    "predict_irrigation",
    "get_predictor",
    "CROP_COEFFICIENTS",
    "URGENCY_MESSAGES",
    # Optimizer
    "WaterOptimizer",
    "OptimizerConfig",
    "optimize_water_usage",
    "detect_irrigation_anomalies",
    "analyze_irrigation_patterns",
    "get_optimizer",
    "OPTIMAL_TIMING",
    "ANOMALY_DESCRIPTIONS",
    "ANOMALY_RECOMMENDATIONS",
]
