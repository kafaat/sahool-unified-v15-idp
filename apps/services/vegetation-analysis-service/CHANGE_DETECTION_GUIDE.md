# SAHOOL Change Detection System

# نظام كشف التغيرات الزراعية - سهول

## Overview | نظرة عامة

The Change Detection System analyzes satellite time series data to automatically identify significant changes in agricultural fields, helping farmers respond quickly to crop stress, damage, or optimal growth conditions.

يحلل نظام كشف التغيرات بيانات السلاسل الزمنية للأقمار الصناعية لتحديد التغييرات المهمة في الحقول الزراعية تلقائياً، مما يساعد المزارعين على الاستجابة بسرعة لإجهاد المحاصيل أو الأضرار أو ظروف النمو المثلى.

## Features | الميزات

### 1. Change Types Detected | أنواع التغييرات المكتشفة

- **Vegetation Growth** (النمو النباتي): Healthy crop development
- **Vegetation Decline** (التدهور النباتي): Reduced crop vigor
- **Water Stress** (الإجهاد المائي): Insufficient irrigation detected
- **Drought Stress** (إجهاد الجفاف): Severe water deficiency
- **Flooding** (الفيضان): Excess water accumulation
- **Harvest Detection** (كشف الحصاد): Automatic harvest event detection
- **Planting Detection** (كشف الزراعة): New crop planting identification
- **Crop Damage** (تلف المحصول): Pest, disease, or weather damage
- **Land Clearing** (تجريف الأرض): Field preparation or deforestation

### 2. Severity Levels | مستويات الخطورة

- **Low** (منخفض): Minor changes, monitor only
- **Medium** (متوسط): Moderate changes, consider action
- **High** (مرتفع): Significant changes, action recommended
- **Critical** (حرج): Severe changes, immediate action required

### 3. Analysis Capabilities | قدرات التحليل

- Time series anomaly detection (كشف الشذوذ في السلاسل الزمنية)
- Trend analysis (تحليل الاتجاهات)
- Seasonal pattern recognition (التعرف على الأنماط الموسمية)
- Crop-specific thresholds (عتبات خاصة بالمحصول)
- Bilingual recommendations (توصيات ثنائية اللغة)

## API Endpoints | نقاط النهاية

### 1. Comprehensive Change Detection

**Endpoint**: `GET /v1/changes/{field_id}`

Analyzes a time period to detect all significant changes.

**Parameters**:

- `field_id` (required): Field identifier
- `lat` (required): Field latitude (-90 to 90)
- `lon` (required): Field longitude (-180 to 180)
- `start_date` (required): Start date (YYYY-MM-DD)
- `end_date` (required): End date (YYYY-MM-DD)
- `crop_type` (optional): Crop type (wheat, sorghum, coffee, qat, etc.)

**Example Request**:

```bash
curl "http://localhost:8090/v1/changes/field_123?lat=15.5&lon=44.2&start_date=2024-01-01&end_date=2024-03-31&crop_type=wheat"
```

**Example Response**:

```json
{
  "field_id": "field_123",
  "analysis_period": {
    "start_date": "2024-01-01",
    "end_date": "2024-03-31"
  },
  "events": [
    {
      "field_id": "field_123",
      "change_type": "water_stress",
      "severity": "high",
      "detected_date": "2024-02-15",
      "location": {
        "lat": 15.5,
        "lon": 44.2,
        "affected_area_ha": 1.0
      },
      "ndvi_before": 0.75,
      "ndvi_after": 0.52,
      "ndvi_change": -0.23,
      "change_percent": -30.7,
      "confidence": 0.89,
      "description_ar": "إجهاد مائي مكتشف - انخفاض NDVI بنسبة 30.7٪",
      "description_en": "Water stress detected - NDVI decreased by 30.7%",
      "recommended_action_ar": "زد كمية الري بنسبة 20-30٪ - إجهاد مائي واضح",
      "recommended_action_en": "Increase irrigation by 20-30% - clear water stress",
      "additional_metrics": {
        "ndwi": 0.05,
        "z_score": 2.35
      }
    }
  ],
  "overall_trend": "declining",
  "ndvi_trend": -0.0023,
  "anomaly_count": 3,
  "severity_summary": {
    "low": 1,
    "medium": 0,
    "high": 2,
    "critical": 0
  },
  "change_type_summary": {
    "water_stress": 2,
    "vegetation_decrease": 1
  },
  "summary_ar": "تم اكتشاف 3 تغيير خلال 90 يوم. الاتجاه العام: تدهور. 2 حدث عالي الخطورة.",
  "summary_en": "Detected 3 changes over 90 days. Overall trend: declining. 2 high-severity event(s).",
  "recommendations_ar": [
    "زد كمية الري بنسبة 20-30٪ - إجهاد مائي واضح",
    "فحص شامل للحقل لتحديد أسباب التدهور",
    "مراقبة مستمرة باستخدام الأقمار الصناعية"
  ],
  "recommendations_en": [
    "Increase irrigation by 20-30% - clear water stress",
    "Comprehensive field inspection to identify causes of decline",
    "Continuous monitoring using satellite imagery"
  ]
}
```

### 2. Compare Two Dates

**Endpoint**: `GET /v1/changes/{field_id}/compare`

Compares two specific dates for before/after analysis.

**Parameters**:

- `field_id` (required): Field identifier
- `lat` (required): Field latitude
- `lon` (required): Field longitude
- `date1` (required): First date (YYYY-MM-DD)
- `date2` (required): Second date (YYYY-MM-DD)

**Example Request**:

```bash
curl "http://localhost:8090/v1/changes/field_123/compare?lat=15.5&lon=44.2&date1=2024-01-01&date2=2024-02-01"
```

**Example Response**:

```json
{
  "field_id": "field_123",
  "change_type": "harvest",
  "severity": "high",
  "detected_date": "2024-02-01",
  "location": {
    "lat": 15.5,
    "lon": 44.2,
    "affected_area_ha": 1.0
  },
  "ndvi_before": 0.78,
  "ndvi_after": 0.25,
  "ndvi_change": -0.53,
  "change_percent": -67.9,
  "confidence": 0.95,
  "description_ar": "حصاد مكتشف - انخفاض سريع في NDVI من 67.9٪",
  "description_en": "Harvest detected - rapid NDVI drop of 67.9%",
  "recommended_action_ar": "حصاد تم بنجاح - خطط للزراعة القادمة",
  "recommended_action_en": "Harvest completed successfully - plan for next planting"
}
```

### 3. Detect Anomalies

**Endpoint**: `GET /v1/changes/{field_id}/anomalies`

Identifies unusual NDVI values that deviate from expected patterns.

**Parameters**:

- `field_id` (required): Field identifier
- `lat` (required): Field latitude
- `lon` (required): Field longitude
- `days` (optional): Analysis period in days (default: 90, max: 365)
- `crop_type` (optional): Crop type for expected pattern

**Example Request**:

```bash
curl "http://localhost:8090/v1/changes/field_123/anomalies?lat=15.5&lon=44.2&days=90&crop_type=wheat"
```

**Example Response**:

```json
{
  "field_id": "field_123",
  "analysis_period": {
    "start_date": "2024-09-26",
    "end_date": "2024-12-25"
  },
  "anomaly_count": 2,
  "anomalies": [
    {
      "date": "2024-11-15",
      "ndvi": 0.35,
      "expected": 0.68,
      "deviation": -0.33,
      "z_score": 2.45,
      "severity": "moderate",
      "ndwi": 0.12,
      "ndmi": 0.1
    }
  ],
  "crop_type": "wheat",
  "expected_pattern_used": true
}
```

## Algorithm Details | تفاصيل الخوارزمية

### Change Detection Process

1. **Data Collection**: Fetch NDVI time series from satellite observations
2. **Quality Filtering**: Remove cloudy observations (>30% cloud cover)
3. **Seasonal Pattern Calculation**: Compute expected NDVI based on crop type
4. **Anomaly Detection**: Identify deviations using Z-score analysis
5. **Change Classification**: Categorize anomalies by type (harvest, stress, etc.)
6. **Severity Assessment**: Determine urgency based on magnitude and speed
7. **Trend Analysis**: Calculate overall field health trajectory
8. **Recommendation Generation**: Provide actionable advice in Arabic & English

### Detection Thresholds

```python
THRESHOLDS = {
    "significant_change": 0.10,      # 10% NDVI change
    "major_change": 0.20,            # 20% NDVI change
    "critical_change": 0.30,         # 30% NDVI change
    "rapid_change_days": 14,         # Change within 2 weeks
}

ANOMALY_THRESHOLDS = {
    "mild": 1.5,                     # 1.5 standard deviations
    "moderate": 2.0,                 # 2.0 standard deviations
    "severe": 2.5,                   # 2.5 standard deviations
}
```

### Classification Logic

**Harvest Detection**:

- NDVI before > 0.5 (healthy crop)
- NDVI after < 0.3 (bare soil)
- Change > -0.3
- Within 30 days

**Planting Detection**:

- NDVI before < 0.25 (bare soil)
- NDVI after > 0.35 (vegetation)
- Change > +0.2
- Within 45 days

**Water Stress**:

- NDVI decline
- NDWI decline (simultaneous)
- Moderate change rate

**Flooding**:

- NDVI decline
- NDWI increase (water accumulation)
- Rapid change

## Crop-Specific Patterns | الأنماط الخاصة بالمحاصيل

### Wheat (القمح)

- Planting: November
- Peak NDVI: ~0.75
- Harvest: May

### Sorghum (الذرة الرفيعة)

- Planting: June
- Peak NDVI: ~0.80
- Harvest: October

### Coffee (البن)

- Perennial crop
- Peak NDVI: ~0.85
- Base NDVI: ~0.65

### Qat (القات)

- Perennial crop
- Peak NDVI: ~0.80
- Base NDVI: ~0.60

## Use Cases | حالات الاستخدام

### 1. Early Warning System

Monitor fields continuously and receive alerts when stress is detected early, allowing preventive action.

### 2. Harvest Planning

Automatically detect when crops are harvested and plan next planting cycle.

### 3. Irrigation Management

Identify water stress events and optimize irrigation schedules.

### 4. Insurance Claims

Document crop damage events with satellite evidence for insurance verification.

### 5. Yield Prediction

Use change patterns to improve yield forecasting accuracy.

### 6. Farm Management

Track multiple fields and prioritize attention based on severity.

## Integration Examples | أمثلة التكامل

### Python Client

```python
import requests
from datetime import date, timedelta

# Detect changes over last 90 days
today = date.today()
start = today - timedelta(days=90)

response = requests.get(
    "http://localhost:8090/v1/changes/my_field",
    params={
        "lat": 15.5,
        "lon": 44.2,
        "start_date": start.isoformat(),
        "end_date": today.isoformat(),
        "crop_type": "wheat"
    }
)

report = response.json()
print(f"Detected {len(report['events'])} changes")
print(f"Overall trend: {report['overall_trend']}")

# Print critical events
for event in report['events']:
    if event['severity'] == 'critical':
        print(f"⚠️ {event['description_en']}")
        print(f"   {event['recommended_action_en']}")
```

### JavaScript/Node.js Client

```javascript
const axios = require("axios");

async function detectChanges(fieldId, lat, lon, startDate, endDate) {
  try {
    const response = await axios.get(
      `http://localhost:8090/v1/changes/${fieldId}`,
      {
        params: {
          lat,
          lon,
          start_date: startDate,
          end_date: endDate,
          crop_type: "wheat",
        },
      },
    );

    const report = response.data;
    console.log(`Trend: ${report.overall_trend}`);
    console.log(`Events: ${report.events.length}`);

    // Display recommendations
    report.recommendations_en.forEach((rec) => {
      console.log(`📋 ${rec}`);
    });

    return report;
  } catch (error) {
    console.error("Change detection failed:", error.message);
  }
}
```

### Mobile App Integration

```kotlin
// Android Kotlin example
suspend fun detectChanges(
    fieldId: String,
    lat: Double,
    lon: Double,
    startDate: String,
    endDate: String
): ChangeReport = withContext(Dispatchers.IO) {
    val response = apiService.detectChanges(
        fieldId = fieldId,
        lat = lat,
        lon = lon,
        startDate = startDate,
        endDate = endDate,
        cropType = "wheat"
    )

    // Show notification for critical events
    response.events
        .filter { it.severity == "critical" }
        .forEach { event ->
            showNotification(
                title = "تنبيه حرج - Critical Alert",
                message = event.description_ar
            )
        }

    response
}
```

## Performance Considerations | اعتبارات الأداء

- **Response Time**: Typically 1-3 seconds for 90-day analysis
- **Data Points**: Processes up to 50 observations efficiently
- **Concurrent Requests**: Supports multiple fields simultaneously
- **Caching**: Results cached for 1 hour by default

## Limitations | القيود

1. **Cloud Cover**: Requires at least 3 clear observations for reliable analysis
2. **Temporal Resolution**: Sentinel-2 revisit time is 5-10 days
3. **Spatial Resolution**: 10-20m depending on satellite band
4. **Crop Knowledge**: Better results when crop type is specified

## Future Enhancements | التحسينات المستقبلية

- [ ] SAR integration for all-weather monitoring
- [ ] Machine learning for improved classification
- [ ] Multi-field batch analysis
- [ ] Real-time alert subscriptions via NATS
- [ ] Export to GeoJSON/Shapefile
- [ ] Historical baseline comparison
- [ ] Mobile push notifications

## Support | الدعم

For questions or issues, contact the SAHOOL development team:

- Email: support@sahool.ye
- Documentation: https://docs.sahool.ye
- GitHub: https://github.com/sahool/satellite-service

---

**Version**: 1.0.0
**Last Updated**: December 2024
**License**: Proprietary - SAHOOL Agriculture Platform
