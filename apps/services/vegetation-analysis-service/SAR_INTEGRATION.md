# Sentinel-1 SAR Integration for Soil Moisture Estimation
# تكامل SAR سنتينل-1 لتقدير رطوبة التربة

## Overview

The SAHOOL Satellite Service now includes **Sentinel-1 SAR (Synthetic Aperture Radar)** integration for soil moisture estimation. This enhancement enables cloud-independent monitoring of soil water content using radar backscatter data.

### Key Features

- **☁️ Cloud-independent monitoring**: Works in all weather conditions
- **💧 Soil moisture estimation**: Estimates both percentage (0-100%) and volumetric water content (m³/m³)
- **🌾 Irrigation event detection**: Identifies sudden moisture increases from irrigation or rainfall
- **📊 Time series analysis**: Tracks soil moisture changes over time
- **🇾🇪 Yemen-calibrated**: Optimized for Yemeni agricultural soils (arid/semi-arid)

## Technical Details

### SAR Soil Moisture Algorithm

Uses an empirical Water Cloud Model calibrated for Yemen:

```
SM = A + B × log₁₀(VV/VH) + C × θ
```

**Calibration Parameters:**
- **A = 15.0**: Baseline moisture (%)
- **B = 8.5**: Sensitivity to backscatter ratio
- **C = -0.3**: Incidence angle correction

**Soil Properties (Yemen agricultural soils):**
- Porosity: 0.45 (sandy-loam)
- Field Capacity: 0.35 m³/m³
- Wilting Point: 0.15 m³/m³

### Data Sources

1. **Primary**: Copernicus STAC API (Sentinel-1)
   - Free access to Sentinel-1 C-SAR data
   - VV and VH polarization
   - 6-day revisit time
   - URL: https://catalogue.dataspace.copernicus.eu/stac

2. **Fallback**: Simulated data
   - Season-aware generation
   - Region-specific calibration
   - Always available

## API Endpoints

### 1. Get Soil Moisture

**Endpoint**: `GET /v1/soil-moisture/{field_id}`

**Parameters**:
- `field_id` (path): Field identifier
- `lat` (query): Field latitude (-90 to 90)
- `lon` (query): Field longitude (-180 to 180)
- `date` (query, optional): Target date (YYYY-MM-DD), defaults to today

**Example Request**:
```bash
curl "http://localhost:8090/v1/soil-moisture/field_001?lat=15.3694&lon=44.1910"
```

**Example Response**:
```json
{
  "field_id": "field_001",
  "timestamp": "2025-12-25T10:30:00",
  "soil_moisture": {
    "percent": 24.5,
    "volumetric_water_content": 0.1102,
    "status": "Optimal - Good for Growth",
    "status_ar": "مثالي - جيد للنمو"
  },
  "sar_data": {
    "vv_backscatter_db": -11.2,
    "vh_backscatter_db": -19.8,
    "incidence_angle_deg": 35.4,
    "data_source": "sentinel-1"
  },
  "confidence": 0.92,
  "recommendation_ar": "مستوى الرطوبة مناسب - استمر في جدول الري الحالي",
  "recommendation_en": "Moisture level adequate - continue current schedule"
}
```

### 2. Detect Irrigation Events

**Endpoint**: `GET /v1/irrigation-events/{field_id}`

**Parameters**:
- `field_id` (path): Field identifier
- `days` (query): Days to look back (7-90, default: 30)

**Example Request**:
```bash
curl "http://localhost:8090/v1/irrigation-events/field_001?days=30"
```

**Example Response**:
```json
{
  "field_id": "field_001",
  "period_days": 30,
  "events_detected": 2,
  "events": [
    {
      "detected_date": "2025-12-20T06:00:00",
      "moisture_change": {
        "before_percent": 18.5,
        "after_percent": 35.2,
        "increase_percent": 16.7
      },
      "estimated_water_mm": 50.1,
      "confidence": 0.88,
      "detection_method": "sar_moisture_spike"
    },
    {
      "detected_date": "2025-12-10T07:30:00",
      "moisture_change": {
        "before_percent": 22.3,
        "after_percent": 40.1,
        "increase_percent": 17.8
      },
      "estimated_water_mm": 53.4,
      "confidence": 0.91,
      "detection_method": "sar_moisture_spike"
    }
  ],
  "summary": {
    "total_water_applied_mm": 103.5,
    "average_application_mm": 51.8
  }
}
```

### 3. Get SAR Time Series

**Endpoint**: `GET /v1/sar-timeseries/{field_id}`

**Parameters**:
- `field_id` (path): Field identifier
- `start_date` (query): Start date (YYYY-MM-DD)
- `end_date` (query): End date (YYYY-MM-DD)
- `lat` (query, optional): Field latitude
- `lon` (query, optional): Field longitude

**Example Request**:
```bash
curl "http://localhost:8090/v1/sar-timeseries/field_001?start_date=2025-11-01&end_date=2025-12-25&lat=15.3694&lon=44.1910"
```

**Example Response**:
```json
{
  "field_id": "field_001",
  "start_date": "2025-11-01",
  "end_date": "2025-12-25",
  "data_points_count": 10,
  "timeseries": [
    {
      "acquisition_date": "2025-11-01T05:30:00",
      "scene_id": "S1_20251101_A",
      "orbit_direction": "ASCENDING",
      "backscatter": {
        "vv_db": -12.5,
        "vh_db": -20.1,
        "vv_vh_ratio": 4.79
      },
      "incidence_angle_deg": 33.2,
      "soil_moisture_percent": 22.8
    }
  ],
  "statistics": {
    "average_moisture_percent": 24.3,
    "min_moisture_percent": 18.5,
    "max_moisture_percent": 35.2,
    "moisture_range_percent": 16.7,
    "trend": "increasing"
  }
}
```

## Soil Moisture Interpretation

The system provides automated interpretation of soil moisture levels:

| Range (% of field capacity) | Status | Status (Arabic) | Action |
|------------------------------|--------|-----------------|--------|
| < Wilting Point (0.15) | Critical - Wilting Point | حرج - نقطة الذبول | Urgent irrigation required |
| 0.15 - 0.26 | Low - Water Stress | منخفض - إجهاد مائي | Irrigation needed soon |
| 0.26 - 0.35 | Optimal - Good for Growth | مثالي - جيد للنمو | Continue current schedule |
| > 0.35 | High - Near Saturation | مرتفع - قرب التشبع | Avoid over-irrigation |

## Integration with Mobile App

The SAR soil moisture data integrates seamlessly with the SAHOOL mobile app:

### Action Templates

When critical soil moisture is detected, the service can generate action templates:

```python
# Example: Generate irrigation action from low soil moisture
if soil_moisture.soil_moisture_percent < 20:
    action = {
        "action_type": "irrigation",
        "title_ar": "ري عاجل مطلوب - رطوبة منخفضة",
        "title_en": "Urgent Irrigation - Low Moisture",
        "urgency": "high",
        "data": {
            "current_moisture": soil_moisture.soil_moisture_percent,
            "recommended_water_mm": 40.0
        }
    }
```

### NATS Event Publishing

Real-time soil moisture alerts can be published via NATS:

```python
# Published on soil moisture check
await publish_analysis_completed_sync(
    event_type="sar.soil_moisture_critical",
    field_id=field_id,
    data={
        "moisture_percent": 15.2,
        "status": "critical",
        "recommendation": "immediate_irrigation"
    },
    priority="high"
)
```

## Usage Examples

### Python SDK Example

```python
import httpx
import asyncio

async def monitor_soil_moisture(field_id: str, lat: float, lon: float):
    async with httpx.AsyncClient() as client:
        # Get current soil moisture
        response = await client.get(
            f"http://localhost:8090/v1/soil-moisture/{field_id}",
            params={"lat": lat, "lon": lon}
        )
        data = response.json()

        print(f"Field {field_id}:")
        print(f"  Soil Moisture: {data['soil_moisture']['percent']}%")
        print(f"  Status: {data['soil_moisture']['status']}")
        print(f"  Recommendation: {data['recommendation_en']}")

        # Check for recent irrigation events
        response = await client.get(
            f"http://localhost:8090/v1/irrigation-events/{field_id}",
            params={"days": 14}
        )
        events = response.json()

        print(f"\n  Recent irrigation events: {events['events_detected']}")
        for event in events['events']:
            print(f"    - {event['detected_date']}: {event['estimated_water_mm']}mm")

# Run for Sana'a region field
asyncio.run(monitor_soil_moisture("field_sana_001", 15.3694, 44.1910))
```

### JavaScript/React Example

```javascript
// Fetch soil moisture for a field
async function getSoilMoisture(fieldId, lat, lon) {
  const response = await fetch(
    `http://localhost:8090/v1/soil-moisture/${fieldId}?lat=${lat}&lon=${lon}`
  );
  const data = await response.json();

  return {
    moisture: data.soil_moisture.percent,
    status: data.soil_moisture.status,
    statusAr: data.soil_moisture.status_ar,
    recommendation: data.recommendation_en,
    recommendationAr: data.recommendation_ar,
    confidence: data.confidence
  };
}

// Component usage
function SoilMoistureCard({ fieldId, coordinates }) {
  const [moisture, setMoisture] = useState(null);

  useEffect(() => {
    getSoilMoisture(fieldId, coordinates.lat, coordinates.lon)
      .then(setMoisture);
  }, [fieldId]);

  return (
    <div className="card">
      <h3>Soil Moisture | رطوبة التربة</h3>
      <div className="moisture-level">{moisture?.moisture}%</div>
      <div className="status">{moisture?.statusAr}</div>
      <div className="recommendation">{moisture?.recommendationAr}</div>
    </div>
  );
}
```

## Benefits Over Optical Satellite Data

| Feature | Sentinel-1 SAR | Sentinel-2 Optical |
|---------|----------------|-------------------|
| **Cloud coverage** | ✅ Works through clouds | ❌ Requires clear skies |
| **Day/night** | ✅ Day and night | ☀️ Daytime only |
| **Soil moisture** | ✅ Direct measurement | ⚠️ Indirect (NDWI) |
| **Vegetation health** | ⚠️ Limited | ✅ Excellent (NDVI) |
| **Resolution** | 10-20m | 10m |
| **Revisit time** | 6 days | 5 days |

**Recommendation**: Use **both** SAR and optical data for comprehensive field monitoring:
- **SAR**: Soil moisture, irrigation monitoring
- **Optical**: Vegetation health, crop growth stages

## Limitations

1. **Accuracy factors**:
   - Surface roughness affects backscatter
   - Vegetation cover reduces soil signal
   - Topography influences incidence angle

2. **Calibration**:
   - Current calibration optimized for Yemen
   - May need adjustment for other regions
   - Field validation recommended

3. **Temporal resolution**:
   - 6-day revisit time
   - May miss short irrigation events
   - Combine with weather data for better accuracy

## Future Enhancements

- [ ] Integration with ground-based soil moisture sensors for validation
- [ ] Machine learning models for improved accuracy
- [ ] Crop-specific calibration (wheat, sorghum, coffee, etc.)
- [ ] Combination with weather forecasts for irrigation scheduling
- [ ] Sub-field moisture variability mapping
- [ ] Real-time alerts via mobile push notifications

## References

- Sentinel-1 Mission: https://sentinels.copernicus.eu/web/sentinel/missions/sentinel-1
- SAR Handbook: https://servirglobal.net/Global/Articles/Article/2674/sar-handbook-comprehensive-methodologies-for-forest-monitoring-and-biomass-estimation
- Water Cloud Model: Attema & Ulaby (1978)
- Copernicus Data Space: https://dataspace.copernicus.eu/

## Support

For questions or issues with the SAR integration:
- Check service health: `GET /healthz`
- View available providers: `GET /v1/providers`
- Review logs for error messages

---

**Version**: 15.7.0
**Last Updated**: December 2025
**License**: Part of SAHOOL Unified Platform
