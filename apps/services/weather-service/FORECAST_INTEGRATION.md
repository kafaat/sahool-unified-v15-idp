# SAHOOL Weather Forecast Integration Service
# خدمة تكامل توقعات الطقس لـ SAHOOL

## Overview | نظرة عامة

The Weather Forecast Integration Service provides comprehensive agricultural weather forecasting with multi-provider support, automated alert generation, and agricultural weather indices calculation for Yemen.

توفر خدمة تكامل توقعات الطقس توقعات طقس زراعية شاملة مع دعم مزودين متعددين، وتوليد تنبيهات تلقائية، وحساب مؤشرات الطقس الزراعية لليمن.

## Features | المميزات

### 1. Multi-Provider Weather Data | بيانات الطقس من مزودين متعددين

- **Open-Meteo** (Free - مجاني): Primary provider, no API key required
- **OpenWeatherMap**: Secondary provider with API key
- **WeatherAPI**: Alternative provider with API key
- **Yemen Met Service**: Placeholder for future integration with Yemen's meteorological service

### 2. Agricultural Alerts | التنبيهات الزراعية

#### Frost Risk Detection | كشف خطر الصقيع
- **Critical**: Temperature ≤ 0°C
- **High**: Temperature ≤ 2°C
- **Medium**: Temperature ≤ 5°C

Provides recommendations for crop protection and frost mitigation.

#### Heat Wave Detection | كشف موجات الحر
- **Critical**: 3+ days with temperature ≥ 45°C
- **High**: 3+ days with temperature ≥ 42°C
- **Medium**: 3+ days with temperature ≥ 38°C

Includes irrigation and heat stress management recommendations.

#### Heavy Rain Alerts | تنبيهات الأمطار الغزيرة
- **Critical**: ≥ 50mm in 24 hours
- **High**: ≥ 30mm in 24 hours
- **Medium**: ≥ 15mm in 24 hours

Provides flood prevention and drainage recommendations.

#### Drought Conditions | ظروف الجفاف
- Detected when precipitation < 5mm over 14+ days
- Includes water conservation recommendations
- Calculates moisture deficit

### 3. Agricultural Weather Indices | المؤشرات الزراعية

#### Growing Degree Days (GDD) | أيام درجة النمو
```python
GDD = ((Tmax + Tmin) / 2) - Base Temperature (default: 10°C)
```
- Tracks crop development stages
- Helps predict harvest timing
- Customizable base temperature per crop

#### Chill Hours | ساعات البرودة
```python
Hours with temperature between 0°C and 7.2°C
```
- Essential for deciduous fruit trees
- Tracks winter chilling requirements
- Helps predict bloom timing

#### Evapotranspiration (ET0) | التبخر والنتح
```python
Calculated using Penman-Monteith or Hargreaves method
```
- Determines crop water requirements
- Helps optimize irrigation scheduling
- Calculates moisture deficit

#### Heat Stress Hours | ساعات الإجهاد الحراري
- Hours with temperature > 35°C
- Indicates crop stress periods
- Guides protective measures

## Installation | التثبيت

The forecast integration service is included in the weather-service package.

```bash
cd apps/services/weather-service
pip install -r requirements.txt
```

## Configuration | الإعدادات

### Environment Variables | متغيرات البيئة

```bash
# Provider API Keys
OPENWEATHERMAP_API_KEY=your_api_key_here
WEATHERAPI_KEY=your_api_key_here
YEMEN_MET_API_KEY=your_api_key_here  # Future

# Cache Settings
WEATHER_CACHE_ENABLED=true
WEATHER_CACHE_CURRENT_TTL=10  # minutes
WEATHER_CACHE_FORECAST_TTL=60  # minutes

# Alert Settings
WEATHER_ALERTS_ENABLED=true
WEATHER_AG_INDICES_ENABLED=true

# Alert Thresholds
FROST_CRITICAL_TEMP=0
HEAT_WAVE_CRITICAL_TEMP=45
HEAVY_RAIN_CRITICAL_MM=50

# Agricultural Indices
GDD_BASE_TEMP=10
CHILL_HOURS_THRESHOLD=7.2
```

### Configuration File | ملف الإعدادات

The service uses `/apps/services/weather-service/src/config.py` for configuration management.

```python
from config import get_config

config = get_config()
print(f"Enabled providers: {len([p for p in config.providers.values() if p.enabled])}")
```

## Usage | الاستخدام

### Basic Example | مثال أساسي

```python
import asyncio
from forecast_integration import WeatherForecastService

async def main():
    # Initialize service
    service = WeatherForecastService()

    # Fetch forecast for Sana'a, Yemen
    lat, lon = 15.3694, 44.1910
    daily, hourly, provider = await service.fetch_forecast(lat, lon, days=7)

    if daily:
        print(f"Forecast from: {provider}")
        for day in daily:
            print(f"{day.date}: {day.temp_min_c}°C - {day.temp_max_c}°C")

    # Clean up
    await service.close()

asyncio.run(main())
```

### Alert Detection | كشف التنبيهات

```python
from forecast_integration import (
    detect_frost_risk,
    detect_heat_wave,
    detect_heavy_rain,
    detect_drought_conditions
)

# Detect frost risk
frost_alerts = detect_frost_risk(daily_forecast)
for alert in frost_alerts:
    print(f"{alert.title_en} - Severity: {alert.severity.value}")
    print(f"Recommendations: {alert.recommendations_en}")

# Detect heat wave
heat_alerts = detect_heat_wave(daily_forecast)

# Detect heavy rain
rain_alerts = detect_heavy_rain(daily_forecast)

# Detect drought (with optional history)
drought_alerts = detect_drought_conditions(
    forecast=daily_forecast,
    history=historical_data  # Optional
)
```

### Agricultural Indices | المؤشرات الزراعية

```python
from forecast_integration import (
    calculate_gdd,
    calculate_chill_hours,
    calculate_evapotranspiration,
    calculate_agricultural_indices
)

# Calculate indices for a day
for day in daily_forecast:
    indices = calculate_agricultural_indices(day, hourly_forecast)

    print(f"Date: {indices.date}")
    print(f"Growing Degree Days: {indices.gdd:.1f}")
    print(f"Evapotranspiration: {indices.eto:.2f} mm")
    print(f"Heat Stress Hours: {indices.heat_stress_hours:.1f}")
    print(f"Moisture Deficit: {indices.moisture_deficit_mm:.2f} mm")
```

### Individual Index Calculations | حسابات المؤشرات الفردية

```python
# Growing Degree Days
gdd = calculate_gdd(
    tmin=20.0,
    tmax=35.0,
    base_temp=10.0,  # Optional, default: 10°C
    upper_limit=30.0  # Optional, default: 30°C
)

# Chill Hours
chill_hours = calculate_chill_hours(
    hourly_temps=[5.0, 6.5, 7.0, 8.0, 5.5],
    threshold=7.2  # Optional, default: 7.2°C
)

# Evapotranspiration
et0 = calculate_evapotranspiration(
    forecast=day_forecast,
    method="penman_monteith"  # or "hargreaves"
)
```

## API Integration | تكامل API

### Add Forecast Endpoint to Main Service | إضافة نقطة توقعات للخدمة الرئيسية

```python
# In main.py
from forecast_integration import (
    WeatherForecastService,
    detect_frost_risk,
    detect_heat_wave,
    detect_heavy_rain,
    calculate_agricultural_indices
)

@app.post("/weather/forecast/agricultural")
async def get_agricultural_forecast(req: LocationRequest, days: int = 7):
    """
    Get agricultural weather forecast with alerts and indices
    الحصول على توقعات الطقس الزراعية مع التنبيهات والمؤشرات
    """
    if not hasattr(app.state, 'forecast_service'):
        app.state.forecast_service = WeatherForecastService()

    # Fetch forecast
    daily, hourly, provider = await app.state.forecast_service.fetch_forecast(
        req.lat, req.lon, days
    )

    if not daily:
        raise ExternalServiceException.weather_service(
            details={"error": "Failed to fetch forecast"}
        )

    # Detect alerts
    alerts = []
    alerts.extend(detect_frost_risk(daily))
    alerts.extend(detect_heat_wave(daily))
    alerts.extend(detect_heavy_rain(daily))

    # Calculate indices
    indices = [
        calculate_agricultural_indices(day, hourly).to_dict()
        for day in daily
    ]

    return {
        "field_id": req.field_id,
        "location": {"lat": req.lat, "lon": req.lon},
        "provider": provider,
        "forecast": [
            {
                "date": f.date,
                "temp_max_c": f.temp_max_c,
                "temp_min_c": f.temp_min_c,
                "precipitation_mm": f.precipitation_mm,
                "condition": f.condition,
                "condition_ar": f.condition_ar,
            }
            for f in daily
        ],
        "alerts": [a.to_dict() for a in alerts],
        "agricultural_indices": indices,
        "summary": {
            "total_gdd": sum(i["gdd"] for i in indices),
            "avg_eto": sum(i["eto"] for i in indices) / len(indices),
            "total_rain": sum(f.precipitation_mm for f in daily),
        }
    }
```

## Data Models | نماذج البيانات

### AgriculturalAlert

```python
@dataclass
class AgriculturalAlert:
    alert_id: str
    alert_type: str
    category: AlertCategory
    severity: AlertSeverity
    title_en: str
    title_ar: str
    description_en: str
    description_ar: str
    start_date: str
    end_date: Optional[str]
    affected_days: int
    recommendations_en: List[str]
    recommendations_ar: List[str]
    impact_score: float  # 0-10
    confidence: float    # 0-1
```

### AgriculturalIndices

```python
@dataclass
class AgriculturalIndices:
    date: str
    gdd: float                    # Growing Degree Days
    chill_hours: float           # Chill Hours
    eto: float                   # Evapotranspiration (mm)
    heat_stress_hours: float     # Hours > 35°C
    moisture_deficit_mm: float   # ET0 - Precipitation
```

## Provider Adapters | محولات المزودين

### YemenMetAdapter (Mock)

Placeholder for future integration with Yemen's national meteorological service.

```python
from forecast_integration import YemenMetAdapter

# This is currently a mock implementation
adapter = YemenMetAdapter(api_key="future_key")
print(f"Is configured: {adapter.is_configured}")  # False (mock)
```

## Testing | الاختبار

Run the example script:

```bash
cd apps/services/weather-service/src
python forecast_example.py
```

This will demonstrate:
- Fetching forecast for Sana'a, Yemen
- Detecting agricultural alerts
- Calculating weather indices
- Generating recommendations

## File Structure | هيكل الملفات

```
apps/services/weather-service/src/
├── config.py                    # Configuration management
├── forecast_integration.py      # Main forecast service
├── forecast_example.py          # Usage example
├── providers/
│   ├── __init__.py
│   ├── multi_provider.py        # Multi-provider implementation
│   └── open_meteo.py           # Open-Meteo provider
├── main.py                      # FastAPI service
└── risks.py                     # Risk assessment functions
```

## Performance | الأداء

### Caching | التخزين المؤقت

- Current weather: 10 minutes cache
- Daily forecast: 60 minutes cache
- Hourly forecast: 30 minutes cache

### Provider Fallback | التبديل بين المزودين

The service automatically falls back to alternative providers if the primary fails:
1. Open-Meteo (free, always available)
2. OpenWeatherMap (if configured)
3. WeatherAPI (if configured)

### Rate Limiting | تحديد المعدل

Configure rate limits in config.py:
```python
ProviderConfig(
    name="OpenWeatherMap",
    rate_limit_per_day=1000,
    timeout_seconds=30,
    max_retries=3
)
```

## Best Practices | أفضل الممارسات

1. **Always close the service**: Use `await service.close()` to clean up resources
2. **Handle errors**: Providers may fail, always check if forecast data is None
3. **Cache wisely**: Use appropriate TTL values based on your needs
4. **Configure thresholds**: Adjust alert thresholds for your region and crops
5. **Monitor providers**: Check which providers are failing and why

## Troubleshooting | استكشاف الأخطاء

### No forecast data returned

```python
# Check provider configuration
from config import get_config

config = get_config()
for name, provider in config.providers.items():
    print(f"{name}: enabled={provider.enabled}, configured={provider.api_key is not None}")
```

### Alerts not generating

```python
# Check alert settings
config = get_config()
print(f"Alerts enabled: {config.enable_alerts}")
print(f"Frost threshold: {config.thresholds.frost_medium_c}°C")
```

### High API usage

```python
# Enable caching
import os
os.environ["WEATHER_CACHE_ENABLED"] = "true"
os.environ["WEATHER_CACHE_FORECAST_TTL"] = "120"  # 2 hours
```

## Future Enhancements | التحسينات المستقبلية

- [ ] Integration with Yemen Meteorological Service
- [ ] Machine learning for improved forecast accuracy
- [ ] Historical weather data analysis
- [ ] Crop-specific disease risk models
- [ ] Pest outbreak prediction
- [ ] Soil moisture integration
- [ ] Satellite imagery integration

## Support | الدعم

For issues or questions:
- GitHub Issues: [sahool-unified-v15-idp](https://github.com/kafaat/sahool-unified-v15-idp)
- Email: support@sahool.app

## License | الترخيص

Part of SAHOOL Unified Platform - Agricultural Management System for Yemen
