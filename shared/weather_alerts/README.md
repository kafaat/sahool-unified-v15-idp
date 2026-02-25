# shared/weather_alerts

Weather Alerts Module | وحدة تنبيهات الطقس

Agricultural weather monitoring for the SAHOOL platform. Generates crop-specific severe weather alerts, identifies optimal pesticide spray windows, produces irrigation scheduling recommendations, and pinpoints harvest timing based on multi-day forecasts. All output is bilingual (Arabic/English).

## File Structure

```
shared/weather_alerts/
├── __init__.py       # Module exports and extensive usage documentation
├── models.py         # Data models, enums, and crop-specific thresholds
├── alerts.py         # WeatherAlertGenerator: alert, irrigation schedule, harvest window logic
└── spray_window.py   # SprayWindowCalculator: hourly spray window scoring and inversion detection
```

## Key Components

### Data Models (`models.py`)

| Model | Purpose |
|-------|---------|
| `WeatherForecast` | Single forecast period (temperature min/max, humidity, wind, precipitation, UV) |
| `WeatherAlert` | Triggered alert with severity, type, bilingual title/description, and action list |
| `AlertThresholds` | Configurable per-crop thresholds for frost, heat, wind, and hail |
| `SprayWindow` | Scored hourly spray opportunity (0-100) with overall condition enum |
| `IrrigationSchedule` | Irrigation recommendation (proceed / delay / skip) with bilingual reason |
| `HarvestWindow` | Harvest condition assessment with optimal date and bilingual recommendation |

Enums:
- `AlertSeverity`: CRITICAL / HIGH / MEDIUM / LOW / INFO
- `AlertType`: FROST / HEAT / WIND / HAIL / HEAVY_RAIN / DROUGHT / HUMIDITY / TEMPERATURE_INVERSION
- `CropType`: WHEAT / BARLEY / DATE_PALM / TOMATO / CUCUMBER / CITRUS / GRAPES / VEGETABLES / GENERAL
- `SprayCondition`: EXCELLENT / GOOD / FAIR / POOR / UNSUITABLE
- `HarvestCondition`: EXCELLENT / GOOD / ACCEPTABLE / POOR / UNSUITABLE / DELAY_RECOMMENDED
- `IrrigationRecommendation`: PROCEED / DELAY / SKIP / REDUCE / INCREASE

Constants `CROP_FROST_THRESHOLDS` and `CROP_HEAT_THRESHOLDS` provide per-crop temperature danger levels.

### Alert Generator (`alerts.py`)

`WeatherAlertGenerator` scans forecast lists for threshold violations and generates prioritized alerts. Also produces irrigation schedules and harvest windows.

`AlertGeneratorConfig` controls enabling/disabling individual alert types.

Standalone convenience function: `generate_weather_alerts(forecasts, crop_type, field_id)`.

### Spray Window Calculator (`spray_window.py`)

`SprayWindowCalculator` scores each hourly forecast on a 0-100 scale using wind speed, temperature, humidity, and Delta-T (wet-bulb depression). Also detects temperature inversion periods during which drift risk is extreme.

`SprayWindowConfig` allows custom thresholds for wind, temperature, and humidity limits.

Standalone functions:
- `find_spray_windows(hourly_forecasts, min_duration_hours)` - finds contiguous acceptable windows
- `get_best_spray_time(hourly_forecasts)` - returns the single best hour
- `detect_inversions(hourly_forecasts)` - returns list of (start, end) inversion periods

## Usage Example

```python
from datetime import date, datetime
from shared.weather_alerts import (
    WeatherAlertGenerator,
    WeatherForecast,
    CropType,
    SprayWindowCalculator,
    generate_weather_alerts,
    find_spray_windows,
    detect_inversions,
)

# Build forecast objects
forecasts = [
    WeatherForecast(
        forecast_date=date.today(),
        temperature_min=-2.0,
        temperature_max=14.0,
        humidity=78.0,
        wind_speed=8.0,
        precipitation_probability=5.0,
    ),
    WeatherForecast(
        forecast_date=date.today(),
        temperature_min=5.0,
        temperature_max=28.0,
        humidity=42.0,
        wind_speed=22.0,          # High wind
        precipitation_probability=0.0,
    ),
]

# Generate crop-specific alerts
alerts = generate_weather_alerts(
    forecasts=forecasts,
    crop_type=CropType.WHEAT,
    field_id="FIELD-001",
)
for alert in alerts:
    print(f"{alert.get_priority_icon()} [{alert.severity.value}] {alert.title}")
    print(f"   {alert.title_ar}")
    for action in alert.recommended_actions:
        print(f"   - {action}")

# Irrigation scheduling
generator = WeatherAlertGenerator()
schedule = generator.generate_irrigation_schedule(
    forecasts=forecasts,
    field_id="FIELD-001",
    crop_type=CropType.WHEAT,
    soil_moisture_current=32.0,
    planned_irrigation_mm=25.0,
)
print(f"Recommendation: {schedule.recommendation.value}")
print(f"Reason (AR): {schedule.reason_ar}")

# Harvest window assessment
harvest = generator.generate_harvest_window(
    forecasts=forecasts,
    field_id="FIELD-001",
    crop_type=CropType.WHEAT,
)
print(f"Condition: {harvest.overall_condition.value}")
print(f"Optimal date: {harvest.optimal_date}")

# Spray window optimization (hourly forecasts)
hourly = [...]  # List of hourly WeatherForecast objects
windows = find_spray_windows(hourly, min_duration_hours=2.0)
for w in windows:
    print(f"Window: {w.start_time} to {w.end_time} | Score: {w.score}/100 | {w.overall_condition.value}")
    print(f"Drift risk: {w.drift_risk}")

# Temperature inversion detection
inversions = detect_inversions(hourly)
for start, end in inversions:
    print(f"Do NOT spray {start} - {end} (inversion period)")
```

## Alert Priority Icons

| Severity | Icon |
|----------|------|
| CRITICAL | [!!!] |
| HIGH | [!!] |
| MEDIUM | [!] |
| LOW / INFO | [.] |

## Version

16.0.0 | Author: SAHOOL Platform Team | Updated: January 2026
