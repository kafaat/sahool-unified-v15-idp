# SAHOOL Weather API Integration

# تكامل واجهة برمجة التطبيقات للطقس

## Overview

Complete weather integration using **Open-Meteo free API** for crop modeling, irrigation scheduling, and agricultural decision support in Yemen.

## Features

✅ **7-Day Weather Forecast** with ET0 (evapotranspiration)
✅ **Historical Weather Data** back to 1940
✅ **Growing Degree Days (GDD)** calculation for phenology tracking
✅ **Water Balance Analysis** (Precipitation vs ET0 × Kc)
✅ **Irrigation Recommendations** based on crop type and growth stage
✅ **Frost Risk Assessment** for Yemen highlands

### Yemen-Specific Features

- **Timezone**: Asia/Aden
- **Highland Frost Monitoring**: Sanaa, Ibb, Dhamar
- **Coastal Heat Stress**: Hodeidah, Aden
- **Seasonal Patterns**: Summer rains, winter cold

---

## API Endpoints

### 1. Weather Forecast

```http
GET /v1/weather/forecast?lat=15.3694&lon=44.1910&days=7
```

**Parameters:**

- `lat` (required): Latitude (-90 to 90)
- `lon` (required): Longitude (-180 to 180)
- `days` (optional): Forecast days (1-16, default: 7)

**Response:**

```json
{
  "location": { "lat": 15.3694, "lon": 44.191 },
  "generated_at": "2024-12-25T10:30:00",
  "forecast_days": 7,
  "daily": [
    {
      "timestamp": "2024-12-26T00:00:00",
      "temperature_c": 18.5,
      "temperature_min_c": 12.0,
      "temperature_max_c": 25.0,
      "precipitation_mm": 0.0,
      "et0_mm": 4.5
    }
  ]
}
```

**Use Cases:**

- Irrigation planning
- Harvest scheduling
- Frost protection
- Water requirement estimation

---

### 2. Historical Weather

```http
GET /v1/weather/historical?lat=15.3694&lon=44.1910&start_date=2024-01-01&end_date=2024-06-30
```

**Parameters:**

- `lat` (required): Latitude
- `lon` (required): Longitude
- `start_date` (required): Start date (YYYY-MM-DD)
- `end_date` (required): End date (YYYY-MM-DD)

**Limits:**

- Historical data: 1940 to ~7 days ago
- Maximum: 365 days per request

**Response:**

```json
{
  "location": {"lat": 15.3694, "lon": 44.1910},
  "start_date": "2024-01-01",
  "end_date": "2024-06-30",
  "days": 182,
  "summary": {
    "avg_temp_c": 20.5,
    "min_temp_c": 8.0,
    "max_temp_c": 32.0,
    "total_precipitation_mm": 150.5,
    "total_et0_mm": 820.0,
    "gdd_base_10": 1850.5
  },
  "daily": [...]
}
```

**Use Cases:**

- Analyze past growing seasons
- Calibrate yield prediction models
- Climate pattern analysis
- Historical comparisons

---

### 3. Growing Degree Days (GDD)

```http
GET /v1/weather/gdd?lat=15.3694&lon=44.1910&start_date=2024-03-01&end_date=2024-06-30&base_temp=10
```

**Parameters:**

- `lat` (required): Latitude
- `lon` (required): Longitude
- `start_date` (required): Start date
- `end_date` (required): End date
- `base_temp` (optional): Base temperature (°C, default: 10)

**GDD Formula:**

```
GDD = Σ(max(0, (Tmax + Tmin)/2 - Tbase))
```

**Base Temperatures:**

- Most crops: 10°C (default)
- Warm-season (corn, tomato): 10-12°C
- Cool-season (wheat, barley): 5-8°C
- Tropical (mango, banana): 12-15°C

**Response:**

```json
{
  "location": { "lat": 15.3694, "lon": 44.191 },
  "period": {
    "start_date": "2024-03-01",
    "end_date": "2024-06-30",
    "days": 122
  },
  "base_temperature_c": 10,
  "gdd_accumulated": 1850.5,
  "gdd_per_day": 15.17
}
```

**Use Cases:**

- Predict flowering/harvest dates
- Track crop development stages
- Compare seasons
- Schedule field operations

---

### 4. Water Balance

```http
GET /v1/weather/water-balance?lat=15.3694&lon=44.1910&start_date=2024-03-01&end_date=2024-06-30&kc=1.0
```

**Parameters:**

- `lat` (required): Latitude
- `lon` (required): Longitude
- `start_date` (required): Start date
- `end_date` (required): End date
- `kc` (optional): Crop coefficient (0.4-1.3, default: 1.0)

**Crop Coefficients (Kc):**

| Crop Type      | Initial | Mid-Season | Late    |
| -------------- | ------- | ---------- | ------- |
| Wheat, Barley  | 0.3-0.5 | 1.0-1.15   | 0.3-0.5 |
| Tomato, Potato | 0.4-0.6 | 1.05-1.25  | 0.7-0.9 |
| Fruit Trees    | 0.8-1.1 | 0.8-1.1    | 0.8-1.1 |

**Response:**

```json
{
  "location": {"lat": 15.3694, "lon": 44.1910},
  "period": {"start_date": "2024-03-01", "end_date": "2024-06-30", "days": 122},
  "kc": 1.0,
  "summary": {
    "total_precipitation_mm": 150.5,
    "total_etc_mm": 820.0,
    "total_balance_mm": -669.5,
    "status": "deficit",
    "status_ar": "عجز مائي"
  },
  "daily_balance": [...]
}
```

**Water Balance Status:**

- **Surplus** (> +50mm): Reduce irrigation
- **Balanced** (-50 to +50mm): Optimal
- **Deficit** (< -50mm): Increase irrigation

---

### 5. Irrigation Recommendation

```http
GET /v1/weather/irrigation-advice?lat=15.3694&lon=44.1910&crop_type=WHEAT&growth_stage=mid&soil_moisture=0.4
```

**Parameters:**

- `lat` (required): Latitude
- `lon` (required): Longitude
- `crop_type` (required): Crop code (e.g., WHEAT, TOMATO, POTATO)
- `growth_stage` (required): Growth stage (initial, development, mid, late, harvest)
- `soil_moisture` (optional): Current soil moisture (0-1)
- `field_id` (optional): Field identifier

**Growth Stages:**

- `initial`: Germination/establishment (Kc ~0.5)
- `development`: Vegetative growth (Kc ~0.7)
- `mid`: Flowering/peak growth (Kc ~1.0-1.2)
- `late`: Ripening/maturation (Kc ~0.8)
- `harvest`: Pre-harvest (Kc ~0.6)

**Response:**

```json
{
  "field_id": null,
  "crop_type": "WHEAT",
  "crop_name_ar": "القمح",
  "crop_name_en": "Wheat",
  "growth_stage": "mid",
  "recommendation_date": "2024-12-25T10:30:00",
  "water_requirement_mm": 42.5,
  "precipitation_forecast_mm": 5.0,
  "irrigation_needed_mm": 37.5,
  "irrigation_frequency_days": 3,
  "recommendation_ar": "ري معتدل مطلوب كل 3 أيام. مرحلة حرجة - حافظ على رطوبة ثابتة.",
  "recommendation_en": "Moderate irrigation needed every 3 days. Critical stage - maintain consistent moisture.",
  "confidence": 0.85
}
```

**Yemen Crops:**

- WHEAT, BARLEY, SORGHUM, MILLET
- TOMATO, POTATO, ONION, CUCUMBER
- COFFEE, DATE_PALM, MANGO, BANANA
- QAT, SESAME, FABA_BEAN

---

### 6. Frost Risk Assessment

```http
GET /v1/weather/frost-risk?lat=15.3694&lon=44.1910&days=7
```

**Parameters:**

- `lat` (required): Latitude
- `lon` (required): Longitude
- `days` (optional): Forecast days (1-16, default: 7)

**Frost Risk Levels:**

- **Severe** (< -2°C, 95%+ probability): Immediate protection needed
- **High** (-2°C to 0°C, 70-95% probability): Protect sensitive crops
- **Moderate** (0°C to 2°C, 40-70% probability): Monitor and prepare
- **Low** (2°C to 5°C, 10-40% probability): Watch forecasts
- **None** (> 5°C, <10% probability): No action needed

**Response:**

```json
{
  "location": { "lat": 15.3694, "lon": 44.191 },
  "forecast_days": 7,
  "max_risk_level": "moderate",
  "frost_risks": [
    {
      "date": "2024-12-26",
      "min_temp_c": 3.5,
      "frost_probability": 0.25,
      "risk_level": "low",
      "recommendation_ar": "خطر صقيع منخفض - راقب التوقعات",
      "recommendation_en": "Low frost risk - monitor forecasts"
    }
  ],
  "summary": {
    "days_with_frost_risk": 2,
    "days_with_high_risk": 0,
    "min_temperature_c": 1.5
  }
}
```

**Yemen Highland Locations (Frost-Prone):**

- Sanaa (1,900m): lat=15.3694, lon=44.1910
- Ibb (2,200m): lat=13.9667, lon=44.1667
- Dhamar (2,400m): lat=14.5439, lon=44.4053
- Taiz (1,400m): lat=13.5795, lon=44.0202

**Frost Protection Methods:**

- Cover crops with plastic sheets or blankets
- Use smoke/heating for orchards
- Irrigate before frost (wet soil holds heat)
- Avoid low-lying areas (cold air pools)

---

## Testing

### Run Test Suite

```bash
cd /home/user/sahool-unified-v15-idp/apps/services/satellite-service
python test_weather_integration.py
```

**Tests Include:**

1. Weather Forecast (Sanaa)
2. Historical Weather (Aden)
3. Growing Degree Days (Ibb)
4. Water Balance (Taiz)
5. Irrigation Recommendation (Hodeidah)
6. Frost Risk Assessment (Sanaa)

### Manual API Testing

Start the satellite service:

```bash
cd /home/user/sahool-unified-v15-idp/apps/services/satellite-service
uvicorn src.main:app --host 0.0.0.0 --port 8090 --reload
```

Test endpoints:

```bash
# Weather forecast for Sanaa
curl "http://localhost:8090/v1/weather/forecast?lat=15.3694&lon=44.1910&days=7"

# Historical weather
curl "http://localhost:8090/v1/weather/historical?lat=15.3694&lon=44.1910&start_date=2024-01-01&end_date=2024-06-30"

# Growing Degree Days
curl "http://localhost:8090/v1/weather/gdd?lat=15.3694&lon=44.1910&start_date=2024-03-01&end_date=2024-06-30&base_temp=10"

# Water balance
curl "http://localhost:8090/v1/weather/water-balance?lat=15.3694&lon=44.1910&start_date=2024-03-01&end_date=2024-06-30&kc=1.0"

# Irrigation advice
curl "http://localhost:8090/v1/weather/irrigation-advice?lat=15.3694&lon=44.1910&crop_type=WHEAT&growth_stage=mid&soil_moisture=0.4"

# Frost risk
curl "http://localhost:8090/v1/weather/frost-risk?lat=15.3694&lon=44.1910&days=7"
```

---

## Implementation Details

### Files Created

1. **`src/weather_integration.py`** (700+ lines)
   - `WeatherIntegration` class with Open-Meteo API client
   - `WeatherData`, `WeatherForecast`, `HistoricalWeather` data models
   - `IrrigationRecommendation`, `FrostRisk` specialized models
   - Full implementation of all weather methods

2. **`src/weather_endpoints.py`** (350+ lines)
   - FastAPI endpoint registration function
   - All 6 weather endpoints with validation
   - Comprehensive documentation in English and Arabic

3. **`test_weather_integration.py`** (400+ lines)
   - Complete test suite for all features
   - Yemen-specific test locations
   - Error handling and reporting

4. **`WEATHER_API.md`** (this file)
   - Complete API documentation
   - Usage examples
   - Testing guide

### Integration with main.py

```python
# Added imports
from .weather_integration import (
    WeatherIntegration,
    WeatherForecast,
    HistoricalWeather,
    FrostRisk,
    IrrigationRecommendation,
    get_weather_service,
)

# Registered weather endpoints
from .weather_endpoints import register_weather_endpoints
register_weather_endpoints(app)
```

---

## Open-Meteo API

### Features

- ✅ **Free** - No API key required
- ✅ **Rate Limit**: 10,000 requests/day per IP
- ✅ **Coverage**: Global, including Yemen
- ✅ **Historical**: Data back to 1940
- ✅ **Forecast**: Up to 16 days
- ✅ **ET0**: FAO-56 reference evapotranspiration
- ✅ **No Authentication**: No signup needed

### Data Sources

- NOAA GFS (forecast)
- ERA5 (historical)
- Multiple weather models

### Documentation

- Website: https://open-meteo.com
- API Docs: https://open-meteo.com/en/docs
- Archive API: https://open-meteo.com/en/docs/historical-weather-api

---

## Integration with Yield Prediction

The weather integration is designed to work seamlessly with the existing yield prediction system:

```python
# In yield_predictor.py
from .weather_integration import get_weather_service

# Get weather data for yield prediction
weather_service = get_weather_service()
forecast = await weather_service.get_forecast(lat, lon, days=7)

# Use ET0 for water stress calculation
et0_mm = sum(day.et0_mm for day in forecast.daily if day.et0_mm)

# Get GDD for phenology tracking
gdd = await weather_service.get_growing_degree_days(
    lat, lon, planting_date, datetime.now().date()
)
```

---

## Yemen Locations Reference

### Major Cities

| City     | Elevation | Latitude | Longitude | Climate              |
| -------- | --------- | -------- | --------- | -------------------- |
| Sanaa    | 2,250m    | 15.3694  | 44.1910   | Highland, frost risk |
| Aden     | 10m       | 12.7855  | 45.0187   | Coastal, hot         |
| Taiz     | 1,400m    | 13.5795  | 44.0202   | Mid-elevation        |
| Hodeidah | 5m        | 14.8022  | 42.9511   | Coastal, very hot    |
| Ibb      | 2,200m    | 13.9667  | 44.1667   | Highland, frost risk |
| Dhamar   | 2,400m    | 14.5439  | 44.4053   | Highland, high frost |
| Hajjah   | 1,800m    | 15.6944  | 43.6031   | Highland             |

### Climate Zones

1. **Highland** (>1,500m): Sanaa, Ibb, Dhamar
   - Cool winters with frost risk
   - Moderate summers
   - Spring/summer rains

2. **Coastal** (<100m): Aden, Hodeidah
   - Hot year-round
   - High humidity
   - Little rainfall

3. **Mid-Elevation** (500-1,500m): Taiz
   - Moderate temperatures
   - Seasonal variation
   - Good agricultural potential

---

## Future Enhancements

- [ ] Soil temperature integration
- [ ] Wind damage risk assessment
- [ ] Heat stress alerts
- [ ] Precipitation intensity analysis
- [ ] Multi-location batch requests
- [ ] Caching for frequently requested data
- [ ] Integration with satellite soil moisture

---

## License

This weather integration uses the **Open-Meteo free API** under their [CC BY 4.0 license](https://open-meteo.com/en/terms).

Attribution: Weather data by [Open-Meteo.com](https://open-meteo.com/)

---

## Support

For issues or questions:

- Check Open-Meteo documentation: https://open-meteo.com/en/docs
- Review test suite: `test_weather_integration.py`
- Check endpoint documentation: `/docs` (FastAPI auto-generated)

---

**Last Updated**: December 2024
**API Version**: 1.0
**Service**: SAHOOL Satellite Service v15.7+
