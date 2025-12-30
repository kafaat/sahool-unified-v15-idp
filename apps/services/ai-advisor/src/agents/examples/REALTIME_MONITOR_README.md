# Real-time Monitor Agent Documentation
# توثيق وكيل المراقبة في الوقت الفعلي

## Overview | نظرة عامة

The Real-time Monitor Agent is a specialized AI agent that continuously monitors farm conditions and triggers alerts based on sensor data, satellite imagery, and weather patterns. It uses both threshold-based and machine learning anomaly detection to identify potential issues before they become critical.

وكيل المراقبة في الوقت الفعلي هو وكيل ذكاء اصطناعي متخصص يراقب بشكل مستمر ظروف المزرعة ويطلق التنبيهات بناءً على بيانات أجهزة الاستشعار والصور الفضائية وأنماط الطقس. يستخدم كلاً من الكشف عن الشذوذات القائم على العتبات والتعلم الآلي لتحديد المشاكل المحتملة قبل أن تصبح حرجة.

## Features | الميزات

### 1. Data Sources Integration | تكامل مصادر البيانات

- **IoT Sensors**: Soil moisture, temperature, humidity
  - أجهزة استشعار IoT: رطوبة التربة، درجة الحرارة، الرطوبة

- **Satellite Imagery**: NDVI, NDWI, and other vegetation indices
  - الصور الفضائية: NDVI، NDWI، ومؤشرات الغطاء النباتي الأخرى

- **Weather Data**: Forecasts, warnings, and alerts
  - بيانات الطقس: التوقعات، التحذيرات، والتنبيهات

- **Historical Patterns**: Trend analysis and baseline comparisons
  - الأنماط التاريخية: تحليل الاتجاهات ومقارنات الأساس

### 2. Alert Types | أنواع التنبيهات

The agent can generate the following alert types:

يمكن للوكيل إنشاء أنواع التنبيهات التالية:

| Alert Type | Arabic | Description |
|------------|--------|-------------|
| DISEASE_RISK | خطر المرض | Potential disease outbreak detected |
| PEST_OUTBREAK | تفشي الآفات | Pest infestation risk identified |
| WATER_STRESS | إجهاد المياه | Insufficient soil moisture |
| NUTRIENT_DEFICIENCY | نقص المغذيات | Nutrient levels below optimal |
| WEATHER_WARNING | تحذير الطقس | Adverse weather conditions |
| HARVEST_READY | جاهز للحصاد | Crop ready for harvesting |
| FROST_ALERT | تنبيه الصقيع | Frost risk detected |
| HEAT_STRESS | إجهاد الحرارة | High temperature stress |
| FLOOD_RISK | خطر الفيضان | Flooding potential |

### 3. Alert Severity Levels | مستويات خطورة التنبيه

- **CRITICAL** (حرج): Immediate action required
- **HIGH** (عالي): Action needed within 24 hours
- **MEDIUM** (متوسط): Action needed within 2-3 days
- **LOW** (منخفض): Monitoring recommended

### 4. Anomaly Detection | كشف الشذوذات

The agent uses two approaches:

يستخدم الوكيل طريقتين:

1. **Threshold-based Detection**: Compares values against configured thresholds
   - الكشف القائم على العتبات: مقارنة القيم مع العتبات المحددة

2. **Statistical Anomaly Detection**: Uses Z-score analysis to detect unusual patterns
   - الكشف الإحصائي عن الشذوذات: استخدام تحليل Z-score لاكتشاف الأنماط غير العادية

## Installation | التثبيت

The agent is already integrated into the SAHOOL AI Advisor service. No additional installation required.

الوكيل مدمج بالفعل في خدمة المستشار الذكي SAHOOL. لا حاجة لتثبيت إضافي.

## Usage | الاستخدام

### Basic Example | مثال أساسي

```python
import asyncio
from agents.realtime_monitor_agent import (
    RealtimeMonitorAgent,
    MonitoringConfig,
    AlertType,
    AlertSeverity,
)

async def monitor_field():
    # Initialize agent | تهيئة الوكيل
    agent = RealtimeMonitorAgent()

    # Initialize NATS (optional) | تهيئة NATS (اختياري)
    await agent.initialize_nats()

    # Configure monitoring | إعدادات المراقبة
    config = MonitoringConfig(
        sensor_check_interval=300,  # 5 minutes
        soil_moisture_min=25.0,
        soil_moisture_max=75.0,
        temperature_min=12.0,
        temperature_max=32.0,
        ndvi_min_threshold=0.5,
        enable_alerts=True,
    )

    # Start monitoring | بدء المراقبة
    result = await agent.start_monitoring("field_001", config)
    print(f"Monitoring started: {result['status']}")

    # Later... stop monitoring | لاحقاً... إيقاف المراقبة
    # await agent.stop_monitoring("field_001")

asyncio.run(monitor_field())
```

### Check for Anomalies | التحقق من الشذوذات

```python
# Sensor data | بيانات أجهزة الاستشعار
sensor_data = {
    "soil_moisture": 18.5,
    "temperature": 28.3,
    "humidity": 65.0,
}

# Check anomalies | التحقق من الشذوذات
result = await agent.check_anomalies("field_001", sensor_data)

if result['has_anomalies']:
    for anomaly in result['anomalies']:
        print(f"Anomaly: {anomaly['type']}")
        print(f"Severity: {anomaly['severity'].value}")
```

### Analyze Stress Indicators | تحليل مؤشرات الإجهاد

```python
# Vegetation indices | مؤشرات الغطاء النباتي
indices = {
    "ndvi": 0.42,
    "ndwi": 0.15,
    "evi": 0.38,
}

# Analyze stress | تحليل الإجهاد
result = await agent.analyze_stress_indicators("field_001", indices)

if result['has_stress']:
    for indicator in result['stress_indicators']:
        print(f"Stress: {indicator['stress_type']}")
        print(f"Severity: {indicator['severity'].value}")
```

### Generate Alert | إنشاء تنبيه

```python
# Generate alert | إنشاء تنبيه
alert = await agent.generate_alert(
    field_id="field_001",
    alert_type=AlertType.WATER_STRESS,
    severity=AlertSeverity.HIGH,
    data={
        "soil_moisture": 18.5,
        "threshold": 25.0,
        "confidence": 0.85,
    }
)

print(f"Alert ID: {alert.alert_id}")
print(f"Message (EN): {alert.message_en}")
print(f"Message (AR): {alert.message_ar}")
print(f"Actions: {alert.recommended_actions}")
```

### Get Monitoring Status | الحصول على حالة المراقبة

```python
status = await agent.get_monitoring_status("field_001")

print(f"Status: {status['status']}")
print(f"Alerts generated: {status['alerts_generated']}")
print(f"Recent alerts: {status['recent_alerts']}")
```

### Predict Future Issues | التنبؤ بالمشاكل المستقبلية

```python
# Predict issues for next 24 hours | التنبؤ بالمشاكل للـ 24 ساعة القادمة
prediction = await agent.predict_issues("field_001", timeframe="24h")

print(f"Prediction: {prediction['prediction']}")
```

## Configuration | الإعدادات

### MonitoringConfig Parameters | معاملات إعدادات المراقبة

| Parameter | Type | Default | Description (EN/AR) |
|-----------|------|---------|---------------------|
| sensor_check_interval | int | 300 | Sensor check interval in seconds / فترة فحص أجهزة الاستشعار بالثواني |
| satellite_check_interval | int | 86400 | Satellite check interval (24h) / فترة فحص الأقمار الصناعية (24 ساعة) |
| weather_check_interval | int | 3600 | Weather check interval (1h) / فترة فحص الطقس (ساعة واحدة) |
| soil_moisture_min | float | 20.0 | Minimum soil moisture % / الحد الأدنى لرطوبة التربة % |
| soil_moisture_max | float | 80.0 | Maximum soil moisture % / الحد الأقصى لرطوبة التربة % |
| temperature_min | float | 10.0 | Minimum temperature °C / الحد الأدنى لدرجة الحرارة °C |
| temperature_max | float | 35.0 | Maximum temperature °C / الحد الأقصى لدرجة الحرارة °C |
| ndvi_min_threshold | float | 0.4 | Minimum healthy NDVI / الحد الأدنى لـ NDVI الصحي |
| ndvi_drop_threshold | float | 0.15 | Significant NDVI drop / انخفاض كبير في NDVI |
| enable_alerts | bool | True | Enable/disable alerts / تفعيل/تعطيل التنبيهات |
| alert_languages | List[str] | ["ar", "en"] | Alert languages / لغات التنبيه |

## NATS Integration | تكامل NATS

The agent uses NATS for real-time event publishing and subscribing:

يستخدم الوكيل NATS لنشر الأحداث في الوقت الفعلي والاشتراك فيها:

### Published Events | الأحداث المنشورة

1. **monitoring_started**: When monitoring begins
   - عند بدء المراقبة

2. **monitoring_stopped**: When monitoring stops
   - عند إيقاف المراقبة

3. **alert_generated**: When an alert is created
   - عند إنشاء تنبيه

### Subscribed Topics | المواضيع المشترك فيها

1. **sahool.monitoring.sensor_data**: IoT sensor data
   - بيانات أجهزة استشعار IoT

2. **sahool.monitoring.satellite_data**: Satellite imagery data
   - بيانات الصور الفضائية

3. **sahool.monitoring.weather_data**: Weather updates
   - تحديثات الطقس

## Best Practices | أفضل الممارسات

### 1. Threshold Configuration | إعداد العتبات

- Adjust thresholds based on crop type and growth stage
  - ضبط العتبات بناءً على نوع المحصول ومرحلة النمو

- Consider local climate conditions
  - مراعاة الظروف المناخية المحلية

- Review and update thresholds seasonally
  - مراجعة وتحديث العتبات موسمياً

### 2. Alert Management | إدارة التنبيهات

- Prioritize CRITICAL and HIGH severity alerts
  - إعطاء الأولوية للتنبيهات الحرجة والعالية

- Review alert history regularly
  - مراجعة سجل التنبيهات بانتظام

- Act on recommendations promptly
  - التصرف بناءً على التوصيات فوراً

### 3. Data Quality | جودة البيانات

- Ensure sensor calibration is current
  - التأكد من تحديث معايرة أجهزة الاستشعار

- Validate incoming data for accuracy
  - التحقق من دقة البيانات الواردة

- Maintain sufficient historical data for predictions
  - الحفاظ على بيانات تاريخية كافية للتنبؤات

### 4. Performance Optimization | تحسين الأداء

- Use appropriate check intervals based on crop needs
  - استخدام فترات فحص مناسبة بناءً على احتياجات المحصول

- Limit historical data storage to prevent memory issues
  - تقييد تخزين البيانات التاريخية لمنع مشاكل الذاكرة

- Monitor NATS connection health
  - مراقبة صحة اتصال NATS

## Integration with Other Agents | التكامل مع الوكلاء الآخرين

The Real-time Monitor Agent can collaborate with other specialized agents:

يمكن لوكيل المراقبة في الوقت الفعلي التعاون مع الوكلاء المتخصصين الآخرين:

- **Disease Expert**: For detailed disease diagnosis
  - خبير الأمراض: للتشخيص التفصيلي للأمراض

- **Irrigation Advisor**: For water management recommendations
  - مستشار الري: لتوصيات إدارة المياه

- **Pest Management**: For pest control strategies
  - إدارة الآفات: لاستراتيجيات مكافحة الآفات

- **Soil Science**: For nutrient management
  - علم التربة: لإدارة المغذيات

- **Emergency Response**: For critical situations
  - الاستجابة للطوارئ: للحالات الحرجة

## Troubleshooting | استكشاف الأخطاء

### Common Issues | المشاكل الشائعة

1. **NATS Connection Failed**
   - Check NATS server availability
   - Verify network connectivity
   - Review NATS configuration in settings

2. **No Anomalies Detected**
   - Verify threshold configuration
   - Ensure sufficient historical data
   - Check sensor data quality

3. **Too Many Alerts**
   - Review and adjust thresholds
   - Increase tolerance levels
   - Filter out low-priority alerts

## API Reference | مرجع API

### Methods | الطرق

#### `start_monitoring(field_id, config)`
Start monitoring a field with specified configuration.

بدء مراقبة حقل بإعدادات محددة.

**Parameters:**
- `field_id` (str): Unique field identifier
- `config` (MonitoringConfig): Monitoring configuration

**Returns:** Dict with status and session info

---

#### `stop_monitoring(field_id)`
Stop monitoring a field.

إيقاف مراقبة حقل.

**Parameters:**
- `field_id` (str): Field identifier

**Returns:** Dict with stop status

---

#### `check_anomalies(field_id, sensor_data)`
Detect anomalies in sensor data.

كشف الشذوذات في بيانات أجهزة الاستشعار.

**Parameters:**
- `field_id` (str): Field identifier
- `sensor_data` (Dict): Current sensor readings

**Returns:** Dict with anomaly detection results

---

#### `analyze_stress_indicators(field_id, indices)`
Analyze crop stress from vegetation indices.

تحليل إجهاد المحاصيل من مؤشرات الغطاء النباتي.

**Parameters:**
- `field_id` (str): Field identifier
- `indices` (Dict): Vegetation indices (NDVI, NDWI, etc.)

**Returns:** Dict with stress analysis results

---

#### `generate_alert(field_id, alert_type, severity, data)`
Generate and publish an alert.

إنشاء ونشر تنبيه.

**Parameters:**
- `field_id` (str): Field identifier
- `alert_type` (AlertType): Type of alert
- `severity` (AlertSeverity): Alert severity level
- `data` (Dict): Alert data

**Returns:** Alert object

---

#### `get_monitoring_status(field_id)`
Get current monitoring status for a field.

الحصول على حالة المراقبة الحالية لحقل.

**Parameters:**
- `field_id` (str): Field identifier

**Returns:** Dict with monitoring status

---

#### `predict_issues(field_id, timeframe)`
Predict upcoming issues based on trends.

التنبؤ بالمشاكل القادمة بناءً على الاتجاهات.

**Parameters:**
- `field_id` (str): Field identifier
- `timeframe` (str): Prediction timeframe (e.g., "24h", "48h", "7d")

**Returns:** Dict with prediction results

## Example Output | مثال على المخرجات

### Alert Object | كائن التنبيه

```json
{
  "alert_id": "field_001_water_stress_20241229120000",
  "field_id": "field_001",
  "alert_type": "water_stress",
  "severity": "high",
  "timestamp": "2024-12-29T12:00:00",
  "message_ar": "تحذير: إجهاد مائي في المحاصيل. مستوى الخطورة: high",
  "message_en": "Warning: Water stress in crops. Severity: high",
  "data": {
    "soil_moisture": 18.5,
    "threshold": 25.0,
    "confidence": 0.85
  },
  "recommended_actions": [
    "Increase irrigation frequency",
    "Check irrigation system for malfunctions",
    "Consult irrigation advisor for optimal watering schedule"
  ],
  "confidence": 0.85
}
```

## License | الترخيص

This agent is part of the SAHOOL unified platform and follows the same license terms.

هذا الوكيل جزء من منصة SAHOOL الموحدة ويتبع نفس شروط الترخيص.

## Support | الدعم

For issues or questions:
- Check the documentation
- Review example code
- Contact the SAHOOL development team

للمشاكل أو الأسئلة:
- راجع التوثيق
- راجع الكود النموذجي
- اتصل بفريق تطوير SAHOOL
