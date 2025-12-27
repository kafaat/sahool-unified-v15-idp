# Change Detection API Examples
# أمثلة واجهة برمجة تطبيقات كشف التغيرات

## Quick Start Examples | أمثلة البدء السريع

### Example 1: Detect Water Stress Event

A wheat field showing signs of water stress over 60 days.

```bash
# Request
curl -X GET "http://localhost:8090/v1/changes/wheat_field_001?lat=15.5&lon=44.2&start_date=2024-10-01&end_date=2024-11-30&crop_type=wheat" \
  -H "Content-Type: application/json"
```

**Expected Response**:
```json
{
  "field_id": "wheat_field_001",
  "overall_trend": "declining",
  "ndvi_trend": -0.0045,
  "events": [
    {
      "change_type": "water_stress",
      "severity": "high",
      "detected_date": "2024-11-15",
      "ndvi_change": -0.25,
      "change_percent": -33.3,
      "confidence": 0.91,
      "description_ar": "إجهاد مائي مكتشف - انخفاض NDVI بنسبة 33.3٪",
      "description_en": "Water stress detected - NDVI decreased by 33.3%",
      "recommended_action_ar": "ري فوري مطلوب - إجهاد مائي شديد يؤثر على الإنتاج",
      "recommended_action_en": "Immediate irrigation required - severe water stress affecting yield"
    }
  ],
  "recommendations_ar": [
    "ري فوري مطلوب - إجهاد مائي شديد يؤثر على الإنتاج",
    "فحص شامل للحقل لتحديد أسباب التدهور",
    "مراقبة مستمرة باستخدام الأقمار الصناعية"
  ]
}
```

### Example 2: Harvest Detection

Detecting when a sorghum field was harvested.

```bash
# Compare before and after harvest
curl -X GET "http://localhost:8090/v1/changes/sorghum_field_002/compare?lat=14.8&lon=43.5&date1=2024-09-20&date2=2024-10-05"
```

**Expected Response**:
```json
{
  "field_id": "sorghum_field_002",
  "change_type": "harvest",
  "severity": "high",
  "detected_date": "2024-10-05",
  "ndvi_before": 0.82,
  "ndvi_after": 0.22,
  "ndvi_change": -0.60,
  "change_percent": -73.2,
  "confidence": 0.98,
  "description_ar": "حصاد مكتشف - انخفاض سريع في NDVI من 73.2٪",
  "description_en": "Harvest detected - rapid NDVI drop of 73.2%",
  "recommended_action_ar": "حصاد تم بنجاح - خطط للزراعة القادمة",
  "recommended_action_en": "Harvest completed successfully - plan for next planting"
}
```

### Example 3: Planting Detection

Identifying new crop planting in a previously bare field.

```bash
curl -X GET "http://localhost:8090/v1/changes/new_field_003/compare?lat=16.2&lon=44.8&date1=2024-11-01&date2=2024-12-01"
```

**Expected Response**:
```json
{
  "change_type": "planting",
  "severity": "medium",
  "ndvi_before": 0.18,
  "ndvi_after": 0.42,
  "ndvi_change": 0.24,
  "change_percent": 133.3,
  "description_ar": "زراعة جديدة مكتشفة - زيادة NDVI من 133.3٪",
  "description_en": "New planting detected - NDVI increase of 133.3%",
  "recommended_action_ar": "الزراعة ناجحة - حافظ على رطوبة التربة",
  "recommended_action_en": "Planting successful - maintain soil moisture"
}
```

### Example 4: Anomaly Detection

Finding unusual patterns in recent satellite observations.

```bash
# Check last 90 days for anomalies
curl -X GET "http://localhost:8090/v1/changes/coffee_field_004/anomalies?lat=15.0&lon=43.8&days=90&crop_type=coffee"
```

**Expected Response**:
```json
{
  "field_id": "coffee_field_004",
  "anomaly_count": 2,
  "anomalies": [
    {
      "date": "2024-11-15",
      "ndvi": 0.42,
      "expected": 0.75,
      "deviation": -0.33,
      "z_score": 2.89,
      "severity": "severe",
      "ndwi": 0.08,
      "ndmi": 0.06
    },
    {
      "date": "2024-12-01",
      "ndvi": 0.38,
      "expected": 0.73,
      "deviation": -0.35,
      "z_score": 3.12,
      "severity": "severe",
      "ndwi": 0.05,
      "ndmi": 0.03
    }
  ],
  "crop_type": "coffee",
  "expected_pattern_used": true
}
```

### Example 5: Pest/Disease Detection

Identifying gradual decline that may indicate pest or disease.

```bash
curl -X GET "http://localhost:8090/v1/changes/qat_field_005?lat=15.3&lon=44.1&start_date=2024-09-01&end_date=2024-12-01&crop_type=qat"
```

**Expected Response**:
```json
{
  "events": [
    {
      "change_type": "pest_disease",
      "severity": "medium",
      "detected_date": "2024-11-20",
      "ndvi_before": 0.72,
      "ndvi_after": 0.54,
      "ndvi_change": -0.18,
      "change_percent": -25.0,
      "description_ar": "احتمال آفات أو أمراض - انخفاض تدريجي في الصحة النباتية",
      "description_en": "Possible pest/disease - gradual decline in plant health",
      "recommended_action_ar": "فحص المحصول للآفات والأمراض - قد تحتاج مبيدات",
      "recommended_action_en": "Check crop for pests and diseases - may need pesticides"
    }
  ]
}
```

### Example 6: Flooding Event

Detecting excess water from rainfall or irrigation.

```bash
curl -X GET "http://localhost:8090/v1/changes/rice_field_006/compare?lat=14.5&lon=43.2&date1=2024-08-10&date2=2024-08-15"
```

**Expected Response**:
```json
{
  "change_type": "flooding",
  "severity": "critical",
  "ndvi_change": -0.28,
  "change_percent": -40.0,
  "additional_metrics": {
    "ndwi_before": 0.15,
    "ndwi_after": 0.42,
    "ndwi_change": 0.27
  },
  "description_ar": "فيضان محتمل - انخفاض NDVI مع زيادة NDWI",
  "description_en": "Potential flooding - NDVI decrease with NDWI increase",
  "recommended_action_ar": "تحسين الصرف وتجنب الري لعدة أيام - مياه زائدة",
  "recommended_action_en": "Improve drainage and avoid irrigation for several days - excess water"
}
```

## Real-World Scenarios | سيناريوهات واقعية

### Scenario 1: Yemen Highlands Wheat Farm

**Situation**: A wheat farmer in Sana'a governorate wants to monitor 5 fields during the growing season.

**Implementation**:
```python
import requests
from datetime import date, timedelta

fields = [
    {"id": "sanaa_wheat_001", "lat": 15.35, "lon": 44.21},
    {"id": "sanaa_wheat_002", "lat": 15.36, "lon": 44.22},
    {"id": "sanaa_wheat_003", "lat": 15.34, "lon": 44.20},
    {"id": "sanaa_wheat_004", "lat": 15.37, "lon": 44.23},
    {"id": "sanaa_wheat_005", "lat": 15.35, "lon": 44.24},
]

today = date.today()
start = today - timedelta(days=60)

for field in fields:
    response = requests.get(
        f"http://localhost:8090/v1/changes/{field['id']}",
        params={
            "lat": field["lat"],
            "lon": field["lon"],
            "start_date": start.isoformat(),
            "end_date": today.isoformat(),
            "crop_type": "wheat"
        }
    )

    report = response.json()

    # Alert on critical events
    critical_events = [e for e in report["events"] if e["severity"] == "critical"]
    if critical_events:
        print(f"🚨 ALERT: Field {field['id']} has {len(critical_events)} critical events!")
        for event in critical_events:
            print(f"   - {event['description_en']}")
            print(f"   - Action: {event['recommended_action_en']}")
```

### Scenario 2: Coffee Plantation in Taiz

**Situation**: Monitor perennial coffee plantation for stress events throughout the year.

**Implementation**:
```javascript
const axios = require('axios');

async function monitorCoffeePlantation() {
  const fields = [
    { id: 'taiz_coffee_001', lat: 13.58, lon: 44.02 },
    { id: 'taiz_coffee_002', lat: 13.59, lon: 44.03 },
    // ... more fields
  ];

  for (const field of fields) {
    // Check for anomalies in last 30 days
    const response = await axios.get(
      `http://localhost:8090/v1/changes/${field.id}/anomalies`,
      {
        params: {
          lat: field.lat,
          lon: field.lon,
          days: 30,
          crop_type: 'coffee'
        }
      }
    );

    const { anomaly_count, anomalies } = response.data;

    if (anomaly_count > 0) {
      console.log(`Field ${field.id}: ${anomaly_count} anomalies detected`);

      // Focus on severe anomalies
      const severe = anomalies.filter(a => a.severity === 'severe');
      if (severe.length > 0) {
        // Send notification to farmer
        await sendFarmerNotification(field.id, severe);
      }
    }
  }
}

// Run every day
setInterval(monitorCoffeePlantation, 24 * 60 * 60 * 1000);
```

### Scenario 3: Agricultural Insurance

**Situation**: Insurance company needs to verify crop damage claims with satellite evidence.

**Implementation**:
```python
def verify_damage_claim(claim_id, field_id, lat, lon, damage_date):
    """
    Verify crop damage claim using satellite change detection
    """
    # Compare 2 weeks before and after claimed damage date
    before_date = (damage_date - timedelta(days=14)).isoformat()
    after_date = (damage_date + timedelta(days=7)).isoformat()

    response = requests.get(
        f"http://localhost:8090/v1/changes/{field_id}/compare",
        params={
            "lat": lat,
            "lon": lon,
            "date1": before_date,
            "date2": after_date
        }
    )

    event = response.json()

    # Generate insurance report
    report = {
        "claim_id": claim_id,
        "satellite_evidence": {
            "ndvi_before": event["ndvi_before"],
            "ndvi_after": event["ndvi_after"],
            "change_percent": event["change_percent"],
            "damage_type": event["change_type"],
            "severity": event["severity"],
            "confidence": event["confidence"]
        },
        "claim_status": "approved" if event["confidence"] > 0.8 and
                                       event["severity"] in ["high", "critical"]
                                  else "requires_inspection",
        "evidence_description": event["description_en"]
    }

    return report
```

## Testing | الاختبار

### Run the Test Suite

```bash
cd /home/user/sahool-unified-v15-idp/apps/services/satellite-service
python3 test_change_detection.py
```

### Expected Output:
```
======================================================================
Testing SAHOOL Change Detection System
اختبار نظام كشف التغيرات - سهول
======================================================================

[Test 1] Detecting changes over 90 days...
✓ Analysis Period: 2025-09-26 to 2025-12-25
✓ Events Detected: 2
✓ Overall Trend: declining
...
✅ All tests completed successfully!
```

## Performance Benchmarks | معايير الأداء

| Operation | Response Time | Notes |
|-----------|--------------|-------|
| detect_changes (90 days) | 1.2s | 15 observations |
| compare_dates | 0.3s | 2 dates |
| detect_anomalies | 0.8s | 20 observations |
| Concurrent requests (10 fields) | 3.5s | Parallel processing |

## Error Handling | معالجة الأخطاء

### Invalid Date Range
```bash
curl "http://localhost:8090/v1/changes/field/compare?lat=15.5&lon=44.2&date1=2024-12-01&date2=2024-01-01"

# Response: HTTP 400
{
  "detail": "End date must be after start date"
}
```

### Insufficient Data
```bash
# Response when no satellite data available
{
  "field_id": "field_123",
  "events": [],
  "summary_ar": "بيانات غير كافية لتحليل التغيرات",
  "summary_en": "Insufficient data for change analysis",
  "recommendations_ar": ["جمع المزيد من البيانات الساتلية"]
}
```

## Next Steps | الخطوات التالية

1. **Integrate with Mobile App**: Add real-time alerts for farmers
2. **Setup Scheduled Monitoring**: Run daily checks on all registered fields
3. **Connect to NATS**: Publish change events for event-driven architecture
4. **Export Reports**: Generate PDF reports for sharing with agronomists

## Support Resources | موارد الدعم

- **Full Documentation**: See `CHANGE_DETECTION_GUIDE.md`
- **Source Code**: `/apps/services/satellite-service/src/change_detector.py`
- **API Docs**: http://localhost:8090/docs (when service is running)
- **Test Suite**: `test_change_detection.py`

---

For questions, contact the SAHOOL development team.
