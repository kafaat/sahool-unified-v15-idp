# Spray Time Advisor - مستشار وقت الرش

OneSoil-style spray time recommendations for SAHOOL agricultural platform.

## Overview

The Spray Time Advisor helps farmers determine the optimal time to apply pesticides, herbicides, fungicides, and other agricultural sprays based on real-time weather conditions. This feature is critical for:

- **Maximizing efficacy**: Applying products at the right conditions ensures better results
- **Minimizing waste**: Avoiding adverse conditions reduces product loss
- **Environmental protection**: Preventing drift and runoff
- **Economic efficiency**: Getting the most value from expensive inputs
- **Safety**: Reducing operator exposure and crop damage

## Features

✅ **7-Day Spray Forecast** - Identify optimal spray windows for the week ahead
✅ **Best Time Finder** - Find the single best spray opportunity in next N days
✅ **Time Evaluation** - Check if a specific planned time is suitable
✅ **Product-Specific** - Tailored recommendations for herbicides, insecticides, fungicides, etc.
✅ **Risk Assessment** - Identify specific risks (drift, wash-off, evaporation, phytotoxicity)
✅ **Bilingual Support** - Recommendations in both Arabic and English
✅ **Yemen-Optimized** - Regional considerations for highlands, coastal, and mid-elevation areas
✅ **Delta-T Calculation** - Wet bulb depression for optimal spray conditions

## Weather Parameters Monitored

### Temperature (درجة الحرارة)
- **Ideal Range**: 10-30°C (varies by product)
- **Too Low (<10°C)**: Reduced product efficacy
- **Too High (>30°C)**: Risk of phytotoxicity (plant damage)

### Humidity (الرطوبة)
- **Ideal Range**: 40-80%
- **Too Low (<40%)**: Rapid evaporation, poor absorption
- **Too High (>80%)**: Slow drying, disease spread (for fungicides)

### Wind Speed (سرعة الرياح)
- **Ideal**: < 15 km/h (general), < 10 km/h (insecticides)
- **High Wind**: Risk of spray drift to non-target areas
- **Too Calm**: Droplets may settle unevenly

### Rain Probability (احتمال المطر)
- **Ideal**: < 20%
- **Critical Factor**: Need 4-6 hours rain-free after application
- **High Probability**: Product may wash off before absorption

### Delta-T (Wet Bulb Depression)
- **Ideal Range**: 2-8°C
- **< 2°C**: Temperature inversion risk (droplets suspended)
- **> 8°C**: Rapid evaporation

## Product-Specific Requirements

### Herbicide (مبيد أعشاب)
```
Temperature: 15-28°C (higher temp for absorption)
Humidity: > 50%
Rain-free period: 6 hours after application
Wind: < 15 km/h
```
**Why**: Herbicides need time to be absorbed through leaf cuticles. Warmer temperatures and moderate humidity improve absorption.

### Insecticide (مبيد حشري)
```
Temperature: 12-28°C
Humidity: 40-80%
Wind: < 10 km/h (critical - prevents drift)
Best time: Early morning or dusk when insects are active
```
**Why**: Insecticides work on contact. Lower wind prevents drift, and cooler times increase insect activity.

### Fungicide (مبيد فطري)
```
Temperature: 10-25°C
Humidity: < 70% (lower humidity preferred)
Wind: < 12 km/h
```
**Why**: High humidity can promote fungal spore spread. Apply before disease pressure builds.

### Foliar Fertilizer (سماد ورقي)
```
Temperature: 10-28°C
Humidity: > 60% (higher humidity improves absorption)
Wind: < 15 km/h
```
**Why**: Nutrients are absorbed through leaf stomata. Higher humidity keeps stomata open longer.

### Growth Regulator (منظم نمو)
```
Temperature: 15-25°C (moderate conditions)
Humidity: > 50%
Wind: < 12 km/h
```
**Why**: Growth regulators are sensitive to environmental stress. Moderate conditions ensure predictable results.

## API Endpoints

### 1. Get Spray Forecast
**Endpoint**: `GET /v1/spray/forecast`

Get 7-day spray forecast with optimal windows.

**Parameters**:
- `lat` (required): Latitude (-90 to 90)
- `lon` (required): Longitude (-180 to 180)
- `days` (optional): Forecast days (1-16, default: 7)
- `product_type` (optional): Product type (herbicide, insecticide, fungicide, foliar_fertilizer, growth_regulator)

**Example**:
```bash
curl "http://localhost:8090/v1/spray/forecast?lat=15.3694&lon=44.1910&days=7&product_type=herbicide"
```

**Response**:
```json
{
  "location": {"lat": 15.3694, "lon": 44.1910},
  "forecast_days": 7,
  "product_type": "herbicide",
  "forecast": [
    {
      "date": "2024-12-25",
      "overall_condition": "good",
      "best_window": {
        "start_time": "2024-12-25T07:00:00",
        "end_time": "2024-12-25T11:00:00",
        "duration_hours": 4,
        "condition": "good",
        "score": 78.5,
        "weather": {
          "temperature_c": 22.5,
          "humidity_percent": 65.0,
          "wind_speed_kmh": 8.2,
          "precipitation_probability": 10.0
        },
        "risks": ["low_humidity"],
        "recommendations_ar": [...],
        "recommendations_en": [...]
      },
      "all_windows": [...],
      "hours_suitable": 6.5,
      "daily_summary": {
        "sunrise": "2024-12-25T06:00:00",
        "sunset": "2024-12-25T18:00:00",
        "temp_min_c": 12.5,
        "temp_max_c": 28.3,
        "rain_probability": 15.0,
        "wind_max_kmh": 12.5
      }
    }
  ],
  "summary": {
    "total_suitable_hours": 38.5,
    "days_with_good_conditions": 5,
    "best_day": "2024-12-26"
  }
}
```

### 2. Find Best Spray Time
**Endpoint**: `GET /v1/spray/best-time`

Find the single best spray window in next N days.

**Parameters**:
- `lat` (required): Latitude
- `lon` (required): Longitude
- `product_type` (required): Product type
- `within_days` (optional): Search period (1-7, default: 3)

**Example**:
```bash
curl "http://localhost:8090/v1/spray/best-time?lat=15.3694&lon=44.1910&product_type=insecticide&within_days=3"
```

### 3. Evaluate Specific Time
**Endpoint**: `POST /v1/spray/evaluate`

Check if a specific time is suitable for spraying.

**Parameters**:
- `lat` (required): Latitude
- `lon` (required): Longitude
- `target_datetime` (required): Target time (ISO 8601 format)
- `product_type` (optional): Product type

**Example**:
```bash
curl -X POST "http://localhost:8090/v1/spray/evaluate?lat=15.3694&lon=44.1910&target_datetime=2024-12-26T09:00:00&product_type=herbicide"
```

### 4. Get Spray Conditions Info
**Endpoint**: `GET /v1/spray/conditions`

Get reference information about spray conditions, risks, and guidelines.

**Example**:
```bash
curl "http://localhost:8090/v1/spray/conditions"
```

## Spray Condition Levels

| Score | Condition | Meaning | Action |
|-------|-----------|---------|--------|
| 85-100 | **Excellent** 🟢 | Perfect conditions | Proceed with confidence |
| 70-84 | **Good** 🟢 | Safe to spray | Proceed normally |
| 50-69 | **Marginal** 🟡 | Some risks present | Exercise caution |
| 30-49 | **Poor** 🟠 | Not recommended | Consider postponing |
| 0-29 | **Dangerous** 🔴 | Hazardous conditions | Do NOT spray |

## Risk Factors

### Spray Drift (انجراف الرذاذ)
**Cause**: Wind speed > 15 km/h
**Impact**: Product drifts to non-target areas (crops, homes, water bodies)
**Mitigation**: Reduce spray pressure, use larger nozzles, or postpone

### Wash-Off (الغسل)
**Cause**: Rain probability > 20%
**Impact**: Product washed off before absorption
**Mitigation**: Wait for 4-6 hours rain-free forecast after spraying

### Evaporation (التبخر)
**Cause**: Low humidity + high temperature
**Impact**: Droplets evaporate before reaching target
**Mitigation**: Spray during cooler times (early morning/evening)

### Poor Absorption (امتصاص ضعيف)
**Cause**: Low humidity (< 40%)
**Impact**: Reduced uptake through leaf surfaces
**Mitigation**: Add surfactant, spray when humidity higher

### Phytotoxicity (السمية النباتية)
**Cause**: Temperature > 30°C
**Impact**: Chemical + heat stress damages plants
**Mitigation**: Spray during cooler hours, consider reducing dosage

### Reduced Efficacy (فعالية منخفضة)
**Cause**: Temperature < 10°C
**Impact**: Chemical reactions slow, insects less active
**Mitigation**: Wait for warmer conditions

### Temperature Inversion (الانعكاس الحراري)
**Cause**: Delta-T < 2°C
**Impact**: Droplets suspended in air layer, drift risk
**Mitigation**: Wait for atmospheric mixing (usually mid-morning)

## Yemen Regional Considerations

### Highlands (صنعاء، إب، ذمار)
**Elevation**: > 1,500m
**Challenges**:
- Cold morning temperatures
- Frost risk in winter (Dec-Feb)
- Strong afternoon winds

**Best Spray Times**:
- Mid-day (10 AM - 3 PM) when temperatures are optimal
- Avoid early morning (too cold)
- Watch for frost in winter months

### Coastal Areas (الحديدة، عدن، المكلا)
**Elevation**: 0-100m
**Challenges**:
- High humidity (often > 80%)
- Coastal winds (especially afternoon)
- Very high summer temperatures

**Best Spray Times**:
- Early morning (6-9 AM) before humidity rises
- Evening (4-6 PM) after peak heat
- Avoid midday in summer

### Mid-Elevation (تعز، ريمة)
**Elevation**: 500-1,500m
**Challenges**:
- Variable mountain winds
- Moderate conditions year-round

**Best Spray Times**:
- Morning (7-11 AM)
- Generally favorable conditions
- Monitor mountain winds

## Usage Examples

### Python Example

```python
import asyncio
from src.spray_advisor import SprayAdvisor, SprayProduct

async def main():
    advisor = SprayAdvisor()

    # Get 7-day forecast for herbicide
    forecast = await advisor.get_spray_forecast(
        latitude=15.3694,  # Sanaa
        longitude=44.1910,
        days=7,
        product_type=SprayProduct.HERBICIDE
    )

    # Find best spray time
    best_window = await advisor.get_best_spray_time(
        latitude=15.3694,
        longitude=44.1910,
        product_type=SprayProduct.INSECTICIDE,
        within_days=3
    )

    if best_window:
        print(f"Best time: {best_window.start_time}")
        print(f"Score: {best_window.score}/100")
        print(f"Condition: {best_window.condition.value}")

    await advisor.close()

asyncio.run(main())
```

### cURL Examples

```bash
# Get weekly forecast for Sanaa wheat farm
curl "http://localhost:8090/v1/spray/forecast?lat=15.3694&lon=44.1910&days=7&product_type=herbicide"

# Find best time for insecticide in Hodeidah
curl "http://localhost:8090/v1/spray/best-time?lat=14.8022&lon=42.9511&product_type=insecticide&within_days=3"

# Check if tomorrow 9 AM is good for fungicide in Taiz
curl -X POST "http://localhost:8090/v1/spray/evaluate?lat=13.5795&lon=44.0202&target_datetime=2024-12-26T09:00:00&product_type=fungicide"

# Get spray guidelines
curl "http://localhost:8090/v1/spray/conditions"
```

## Testing

Run the comprehensive test suite:

```bash
cd apps/services/satellite-service
python test_spray_advisor.py
```

Run usage examples (requires running service):

```bash
# Start service
python -m uvicorn src.main:app --port 8090

# In another terminal
python examples/spray_advisor_usage.py
```

## Data Source

Weather data from **Open-Meteo** free API:
- Hourly forecasts up to 16 days ahead
- Temperature, humidity, wind speed, precipitation probability
- No API key required
- Rate limit: 10,000 requests/day per IP

**API Documentation**: https://open-meteo.com/en/docs

## Safety Reminders

⚠️ **Always**:
- Wear personal protective equipment (PPE): gloves, goggles, mask
- Read product label and follow manufacturer instructions
- Keep spray records (date, time, product, conditions)
- Avoid spraying near homes, schools, and water bodies
- Clean equipment thoroughly after use
- Dispose of containers properly
- Check local regulations and spray buffer zones

⚠️ **Never**:
- Spray in high wind conditions (drift risk)
- Spray before rain (wash-off risk)
- Spray during extreme heat (phytotoxicity risk)
- Spray without proper protective equipment
- Mix incompatible products

## Integration with SAHOOL Platform

The Spray Advisor integrates with:

- **Field Management**: Spray recommendations per field
- **Crop Calendar**: Optimal spray timing for growth stages
- **Weather Service**: Real-time and forecast data
- **Task Management**: Schedule spray operations
- **Mobile App**: Push notifications for optimal spray windows
- **Record Keeping**: Log spray applications with conditions

## Future Enhancements

Planned features:
- [ ] Soil moisture integration for better timing
- [ ] Historical spray efficacy tracking
- [ ] Machine learning for location-specific optimization
- [ ] Integration with equipment (spray rate, nozzle selection)
- [ ] Resistance management (rotation recommendations)
- [ ] Buffer zone calculations
- [ ] Spray calendar generation
- [ ] SMS/WhatsApp notifications for optimal windows

## References

- FAO Guidelines on Pesticide Application: http://www.fao.org/agriculture/crops/thematic-sitemap/theme/pests/jmpr/en/
- Spray Application Manual: https://grains.org.au/resources-and-publications/resources/spray-application-manual
- OneSoil Spray Time Feature: https://onesoil.ai/en/blog/spray-time
- Delta-T Guide: https://www.dpi.nsw.gov.au/agriculture/farm-management/weather/delta-t

## License

Part of the SAHOOL Unified Platform v15 - Open Source Agricultural Platform for Yemen

---

**Created by**: SAHOOL Development Team
**Last Updated**: 2024-12-25
**Version**: 1.0.0
