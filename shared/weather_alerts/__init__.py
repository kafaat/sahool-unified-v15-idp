"""
Weather Alerts Module
=====================
وحدة تنبيهات الطقس

Enhanced weather alerts for agricultural operations including:
- Severe weather alerts (frost, heat, wind, hail)
- Spray window optimization
- Irrigation scheduling based on forecast
- Harvest timing recommendations

Features:
- Temperature inversion detection
- Wind speed thresholds and drift risk
- Humidity considerations
- Bilingual Arabic/English alerts

Author: SAHOOL Platform Team
Updated: January 2026

Usage Examples:
--------------

1. Generate weather alerts from forecasts:

    from shared.weather_alerts import (
        WeatherAlertGenerator,
        WeatherForecast,
        CropType,
        generate_weather_alerts,
    )

    # Create forecasts
    forecast = WeatherForecast(
        forecast_date=date.today(),
        temperature_min=-2.0,
        temperature_max=15.0,
        humidity=75.0,
        wind_speed=20.0,
        precipitation_probability=10.0,
    )

    # Generate alerts
    alerts = generate_weather_alerts(
        forecasts=[forecast],
        crop_type=CropType.WHEAT,
        field_id="FIELD-001",
    )

    for alert in alerts:
        print(f"{alert.get_priority_icon()} {alert.title}")
        print(f"   {alert.title_ar}")
        for action in alert.recommended_actions:
            print(f"   - {action}")

2. Find spray windows:

    from shared.weather_alerts import (
        SprayWindowCalculator,
        WeatherForecast,
        find_spray_windows,
    )

    # With hourly forecasts
    hourly_forecasts = [...]  # List of hourly WeatherForecast objects

    windows = find_spray_windows(
        hourly_forecasts=hourly_forecasts,
        min_duration_hours=2.0,
    )

    for window in windows:
        print(f"Window: {window.start_time} - {window.end_time}")
        print(f"Score: {window.score}/100")
        print(f"Condition: {window.overall_condition.value}")
        print(f"Drift Risk: {window.drift_risk} / {window.drift_risk_ar}")

3. Generate irrigation schedule:

    from shared.weather_alerts import (
        WeatherAlertGenerator,
        CropType,
    )

    generator = WeatherAlertGenerator()
    schedule = generator.generate_irrigation_schedule(
        forecasts=forecasts,
        field_id="FIELD-001",
        crop_type=CropType.WHEAT,
        soil_moisture_current=35.0,
        planned_irrigation_mm=25.0,
    )

    print(f"Recommendation: {schedule.recommendation.value}")
    print(f"Reason: {schedule.reason}")
    print(f"Reason (AR): {schedule.reason_ar}")

4. Get harvest window recommendations:

    generator = WeatherAlertGenerator()
    harvest = generator.generate_harvest_window(
        forecasts=forecasts,
        field_id="FIELD-001",
        crop_type=CropType.WHEAT,
    )

    print(f"Condition: {harvest.overall_condition.value}")
    print(f"Optimal Date: {harvest.optimal_date}")
    print(f"Recommendation: {harvest.recommendation}")
    print(f"Recommendation (AR): {harvest.recommendation_ar}")

5. Detect temperature inversions:

    from shared.weather_alerts import detect_inversions

    inversion_periods = detect_inversions(hourly_forecasts)
    for start, end in inversion_periods:
        print(f"Inversion: {start} - {end}")
        print("  DO NOT spray during this period!")
"""

# Models
from .models import (
    # Enums
    AlertSeverity,
    AlertType,
    CropType,
    HarvestCondition,
    IrrigationRecommendation,
    SprayCondition,
    # Data classes
    AlertThresholds,
    HarvestWindow,
    IrrigationSchedule,
    SprayWindow,
    WeatherAlert,
    WeatherForecast,
    # Crop-specific thresholds
    CROP_FROST_THRESHOLDS,
    CROP_HEAT_THRESHOLDS,
)

# Alert generation
from .alerts import (
    AlertGeneratorConfig,
    WeatherAlertGenerator,
    generate_weather_alerts,
)

# Spray window optimization
from .spray_window import (
    SprayWindowCalculator,
    SprayWindowConfig,
    detect_inversions,
    find_spray_windows,
    get_best_spray_time,
)

__all__ = [
    # Enums
    "AlertSeverity",
    "AlertType",
    "CropType",
    "HarvestCondition",
    "IrrigationRecommendation",
    "SprayCondition",
    # Data classes
    "AlertThresholds",
    "HarvestWindow",
    "IrrigationSchedule",
    "SprayWindow",
    "WeatherAlert",
    "WeatherForecast",
    # Crop-specific thresholds
    "CROP_FROST_THRESHOLDS",
    "CROP_HEAT_THRESHOLDS",
    # Alert generation
    "AlertGeneratorConfig",
    "WeatherAlertGenerator",
    "generate_weather_alerts",
    # Spray window
    "SprayWindowCalculator",
    "SprayWindowConfig",
    "detect_inversions",
    "find_spray_windows",
    "get_best_spray_time",
]

__version__ = "16.0.0"
