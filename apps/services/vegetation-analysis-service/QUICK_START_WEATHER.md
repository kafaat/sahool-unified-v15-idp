# Quick Start: Weather API
# دليل البداية السريعة: واجهة برمجة التطبيقات للطقس

## 🚀 Start the Service

```bash
cd /home/user/sahool-unified-v15-idp/apps/services/satellite-service
uvicorn src.main:app --host 0.0.0.0 --port 8090 --reload
```

Access at: http://localhost:8090

---

## 📡 Quick API Calls

### 1. Get Weather Forecast (Sanaa)
```bash
curl "http://localhost:8090/v1/weather/forecast?lat=15.3694&lon=44.1910&days=7"
```

### 2. Get Irrigation Advice (Tomato)
```bash
curl "http://localhost:8090/v1/weather/irrigation-advice?lat=15.37&lon=44.19&crop_type=TOMATO&growth_stage=mid"
```

### 3. Check Frost Risk (Highlands)
```bash
curl "http://localhost:8090/v1/weather/frost-risk?lat=15.3694&lon=44.1910&days=7"
```

### 4. Calculate GDD
```bash
curl "http://localhost:8090/v1/weather/gdd?lat=15.37&lon=44.19&start_date=2024-03-01&end_date=2024-06-30&base_temp=10"
```

### 5. Water Balance
```bash
curl "http://localhost:8090/v1/weather/water-balance?lat=15.37&lon=44.19&start_date=2024-03-01&end_date=2024-06-30&kc=1.0"
```

### 6. Historical Weather
```bash
curl "http://localhost:8090/v1/weather/historical?lat=15.37&lon=44.19&start_date=2024-01-01&end_date=2024-06-30"
```

---

## 🌍 Yemen Coordinates

| Location | Lat | Lon | Elevation | Use Case |
|----------|-----|-----|-----------|----------|
| Sanaa | 15.3694 | 44.1910 | 2,250m | Highland crops, frost |
| Aden | 12.7855 | 45.0187 | 10m | Coastal, heat |
| Hodeidah | 14.8022 | 42.9511 | 5m | Coastal, irrigation |
| Ibb | 13.9667 | 44.1667 | 2,200m | Highland, coffee |
| Taiz | 13.5795 | 44.0202 | 1,400m | Mid-elevation |
| Dhamar | 14.5439 | 44.4053 | 2,400m | Highland, frost |

---

## 🌾 Common Crops

| Crop Code | Name (EN) | Name (AR) | Kc (mid) |
|-----------|-----------|-----------|----------|
| WHEAT | Wheat | القمح | 1.15 |
| TOMATO | Tomato | طماطم | 1.15 |
| POTATO | Potato | بطاطس | 1.15 |
| COFFEE | Coffee | قهوة | 0.95 |
| SORGHUM | Sorghum | ذرة رفيعة | 1.00 |

---

## 📱 In Python Code

```python
import httpx
import asyncio

async def get_weather():
    async with httpx.AsyncClient() as client:
        # Get forecast
        response = await client.get(
            "http://localhost:8090/v1/weather/forecast",
            params={"lat": 15.3694, "lon": 44.1910, "days": 7}
        )
        forecast = response.json()

        # Get irrigation advice
        response = await client.get(
            "http://localhost:8090/v1/weather/irrigation-advice",
            params={
                "lat": 15.3694,
                "lon": 44.1910,
                "crop_type": "WHEAT",
                "growth_stage": "mid",
                "soil_moisture": 0.4
            }
        )
        advice = response.json()

        return forecast, advice

asyncio.run(get_weather())
```

---

## 🧪 Run Tests

```bash
# Full test suite
python test_weather_integration.py

# Usage examples
python examples/weather_usage_example.py
```

---

## 📚 Documentation

- API Reference: `WEATHER_API.md`
- Full Summary: `WEATHER_INTEGRATION_SUMMARY.md`
- Swagger UI: http://localhost:8090/docs
- ReDoc: http://localhost:8090/redoc

---

## 💡 Tips

1. **Free API**: No registration or API key needed
2. **Rate Limit**: 10,000 requests/day per IP
3. **Historical Data**: Available from 1940
4. **Forecast**: Up to 16 days
5. **Timezone**: All times in Asia/Aden
6. **ET0**: Included in all forecasts
7. **Bilingual**: Responses in English and Arabic

---

## ⚡ Quick Examples

### Example 1: Check if irrigation needed today
```bash
curl "http://localhost:8090/v1/weather/irrigation-advice?lat=15.37&lon=44.19&crop_type=TOMATO&growth_stage=mid&soil_moisture=0.3"
```

Look for `irrigation_needed_mm` in response.

### Example 2: Frost alert for tonight
```bash
curl "http://localhost:8090/v1/weather/frost-risk?lat=15.3694&lon=44.1910&days=1"
```

Check `risk_level`: severe, high, moderate, low, or none.

### Example 3: How much has it rained this month?
```bash
START_DATE=$(date -d "$(date +%Y-%m-01)" +%Y-%m-%d)
END_DATE=$(date +%Y-%m-%d)
curl "http://localhost:8090/v1/weather/historical?lat=15.37&lon=44.19&start_date=$START_DATE&end_date=$END_DATE"
```

Look for `total_precipitation_mm` in summary.

---

**Ready to use!** 🎉
