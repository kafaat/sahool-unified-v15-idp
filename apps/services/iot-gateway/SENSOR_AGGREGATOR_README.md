# Sensor Data Aggregation Service - SAHOOL IoT
# خدمة تجميع بيانات المستشعرات - صحول

## Overview | نظرة عامة

A comprehensive sensor data aggregation and analytics service for SAHOOL IoT Gateway. Provides advanced statistical analysis, anomaly detection, and sensor health monitoring tailored for Yemen's agricultural climate.

خدمة شاملة لتجميع وتحليل بيانات المستشعرات لبوابة صحول للإنترنت. توفر تحليلات إحصائية متقدمة، واكتشاف الشذوذات، ومراقبة صحة المستشعرات مصممة خصيصاً لمناخ اليمن الزراعي.

## Features | الميزات

### 1. Statistical Aggregation | التجميع الإحصائي
- **Basic Statistics** | الإحصائيات الأساسية
  - Mean (متوسط), Median (وسيط), Min (أدنى), Max (أقصى)
  - Standard Deviation (الانحراف المعياري)

- **Percentiles** | المئينات
  - 10th, 25th, 75th, 90th percentiles
  - Quartile analysis (تحليل الأرباع)

- **Advanced Metrics** | المقاييس المتقدمة
  - Rate of Change (معدل التغيير) - units per hour
  - Cumulative Sum (المجموع التراكمي) - for rainfall data

### 2. Time-based Aggregations | التجميع الزمني

- **Hourly Average** (متوسط ساعي) - 1-hour intervals
- **Daily Summary** (ملخص يومي) - Daily statistics
- **Weekly Trend** (اتجاه أسبوعي) - Weekly patterns
- **Monthly Report** (تقرير شهري) - Monthly analytics

### 3. Outlier Detection | اكتشاف القيم الشاذة

Three methods for anomaly detection:

1. **Z-Score Method** (طريقة Z-Score)
   - Statistical outlier detection
   - Configurable threshold (default: 3 standard deviations)

2. **IQR Method** (طريقة IQR)
   - Interquartile Range detection
   - Robust to extreme values

3. **Threshold Method** (طريقة العتبات)
   - Yemen-specific climate thresholds
   - Optimized for local agricultural conditions

### 4. Sensor Health Monitoring | مراقبة صحة المستشعرات

- **Status Monitoring** | مراقبة الحالة
  - Healthy (سليم), Warning (تحذير), Critical (حرج), Offline (غير متصل)

- **Quality Metrics** | مقاييس الجودة
  - Data Quality Score (0-100) (نقاط جودة البيانات)
  - Uptime Percentage (نسبة وقت التشغيل)
  - Outlier Percentage (نسبة القيم الشاذة)

- **Drift Detection** | اكتشاف الانحراف
  - Gradual sensor degradation detection
  - Calibration recommendations

- **Arabic Recommendations** | التوصيات بالعربية
  - Context-aware alerts
  - Actionable recommendations

## Yemen Climate Thresholds | عتبات مناخ اليمن

Optimized alert thresholds for Yemen's agricultural conditions:

| Sensor Type | Min | Max | Unit | Critical Min | Critical Max |
|-------------|-----|-----|------|--------------|--------------|
| **Soil Moisture** (رطوبة التربة) | 20% | 80% | % | 10% | 90% |
| **Air Temperature** (درجة حرارة الهواء) | 5°C | 45°C | °C | 0°C | 50°C |
| **Soil Temperature** (درجة حرارة التربة) | 10°C | 35°C | °C | 5°C | 40°C |
| **Air Humidity** (رطوبة الهواء) | 10% | 95% | % | 5% | 98% |
| **Soil EC** (الملوحة) | 0 | 4 | dS/m | 0 | 6 |
| **Soil pH** (حموضة التربة) | 5.5 | 8.5 | - | 4.5 | 9.5 |
| **Rainfall** (الأمطار) | 0 | 100 | mm/day | 0 | 200 |
| **Wind Speed** (سرعة الرياح) | 0 | 15 | m/s | 0 | 25 |

## Installation | التثبيت

The sensor aggregator is part of the IoT Gateway service. No additional installation required.

```python
from apps.services.iot_gateway.src.sensor_aggregator import SensorAggregator
from apps.services.iot_gateway.src.models.sensor_data import SensorReading, TimeGranularity
```

## Usage Examples | أمثلة الاستخدام

### Example 1: Basic Statistics | الإحصائيات الأساسية

```python
from sensor_aggregator import SensorAggregator

aggregator = SensorAggregator()

# Sample temperature values
values = [22.5, 23.0, 24.5, 25.0, 23.5, 24.0, 26.0, 25.5]

stats = aggregator.calculate_statistics(values)

print(f"Mean: {stats['mean']}°C")
print(f"Median: {stats['median']}°C")
print(f"Min: {stats['min']}°C")
print(f"Max: {stats['max']}°C")
print(f"Std Dev: {stats['std']}°C")
```

### Example 2: Outlier Detection | اكتشاف القيم الشاذة

```python
from sensor_aggregator import SensorAggregator, create_sample_readings

aggregator = SensorAggregator()

# Create sample readings
readings = create_sample_readings(
    device_id="sensor_001",
    field_id="field_001",
    sensor_type="air_temperature",
    count=50,
    base_value=25.0
)

# Detect outliers using Z-Score method
outliers = aggregator.detect_outliers(readings, method="zscore", threshold=2.5)
print(f"Outliers detected: {len(outliers)}")

# Detect using Yemen thresholds
outliers_threshold = aggregator.detect_outliers(readings, method="threshold")
print(f"Out of range: {len(outliers_threshold)}")
```

### Example 3: Field Aggregation | التجميع حسب الحقل

```python
from datetime import datetime, timedelta, timezone
from sensor_aggregator import SensorAggregator
from models.sensor_data import TimeGranularity

aggregator = SensorAggregator()

# Define time range
time_range = (
    datetime.now(timezone.utc) - timedelta(hours=24),
    datetime.now(timezone.utc)
)

# Aggregate by field
aggregated = aggregator.aggregate_by_field(
    field_id="field_highland_001",
    time_range=time_range,
    readings=readings,
    granularity=TimeGranularity.DAILY
)

for agg in aggregated:
    print(f"{agg.sensor_type}:")
    print(f"  Mean: {agg.mean}")
    print(f"  Count: {agg.count}")
    print(f"  Quality: {agg.data_quality_score}%")
```

### Example 4: Sensor Health Check | فحص صحة المستشعر

```python
aggregator = SensorAggregator()

# Check sensor health (last 24 hours of readings)
health = aggregator.check_sensor_status(
    device_id="sensor_temp_001",
    readings=readings,
    expected_interval_minutes=15
)

print(f"Status: {health.status.value}")
print(f"Quality Score: {health.data_quality_score}%")
print(f"Uptime: {health.uptime_percentage}%")
print(f"Drift Detected: {health.drift_detected}")

# Arabic recommendations
for rec in health.recommendations_ar:
    print(f"• {rec}")
```

### Example 5: Time-based Aggregation | التجميع الزمني

```python
aggregator = SensorAggregator()

# Hourly average
hourly = aggregator.hourly_average(readings)

# Daily summary
daily = aggregator.daily_summary(readings)

# Weekly trend
weekly = aggregator.weekly_trend(readings)

# Monthly report
monthly = aggregator.monthly_report(readings)

for day_key, agg in daily.items():
    print(f"{day_key}: {agg.mean}°C (n={agg.count})")
```

### Example 6: Rainfall Cumulative Sum | المجموع التراكمي للأمطار

```python
from models.sensor_data import SensorReading

# Create rainfall readings
rainfall_readings = [
    SensorReading(
        device_id="rain_gauge_001",
        field_id="field_taiz_001",
        sensor_type="rainfall",
        value=5.5,
        unit="mm",
        timestamp="2024-01-01T12:00:00Z"
    ),
    # ... more readings
]

time_range = (start_date, end_date)

agg = aggregator._aggregate_readings(
    field_id="field_taiz_001",
    sensor_type="rainfall",
    time_range=time_range,
    readings=rainfall_readings,
    granularity=TimeGranularity.WEEKLY
)

print(f"Weekly Rainfall: {agg.cumulative_sum} mm")
print(f"Daily Average: {agg.mean} mm")
```

## Data Models | نماذج البيانات

### SensorReading

```python
@dataclass
class SensorReading:
    device_id: str           # معرف الجهاز
    field_id: str            # معرف الحقل
    sensor_type: str         # نوع المستشعر
    value: float             # القيمة
    unit: str                # الوحدة
    timestamp: str           # وقت القراءة
    metadata: Optional[Dict] # بيانات إضافية
    quality_score: Optional[float]  # نقاط الجودة (0-100)
    is_outlier: bool = False        # هل هي قيمة شاذة
```

### AggregatedData

```python
@dataclass
class AggregatedData:
    field_id: str
    sensor_type: str
    time_range_start: str
    time_range_end: str
    granularity: TimeGranularity

    # Statistics
    mean: Optional[float]
    median: Optional[float]
    min: Optional[float]
    max: Optional[float]
    std: Optional[float]
    count: int

    # Percentiles
    percentile_10: Optional[float]
    percentile_25: Optional[float]
    percentile_75: Optional[float]
    percentile_90: Optional[float]

    # Advanced metrics
    rate_of_change: Optional[float]
    cumulative_sum: Optional[float]

    # Quality
    data_quality_score: Optional[float]
    outlier_count: int
```

### SensorHealth

```python
@dataclass
class SensorHealth:
    device_id: str
    field_id: str
    sensor_type: str
    status: SensorStatus  # HEALTHY, WARNING, CRITICAL, OFFLINE
    timestamp: str

    # Metrics
    data_quality_score: float        # 0-100
    uptime_percentage: float         # 0-100
    battery_level: Optional[float]   # 0-100
    signal_strength: Optional[float] # dBm

    # Issues
    drift_detected: bool
    drift_magnitude: Optional[float]
    outlier_percentage: float

    # Recommendations
    alerts: List[str]
    recommendations_ar: List[str]  # Arabic recommendations
    recommendations_en: List[str]  # English recommendations
```

## API Methods | طرق الواجهة

### Aggregation Methods | طرق التجميع

```python
# Aggregate by field
aggregate_by_field(field_id, time_range, readings, granularity)

# Aggregate by sensor type
aggregate_by_sensor_type(sensor_type, time_range, readings, granularity)

# Calculate statistics
calculate_statistics(readings)

# Detect outliers
detect_outliers(readings, method='zscore', threshold=3.0)
```

### Time-based Aggregations | التجميع الزمني

```python
# Hourly average
hourly_average(readings)

# Daily summary
daily_summary(readings)

# Weekly trend
weekly_trend(readings)

# Monthly report
monthly_report(readings)
```

### Health Monitoring | مراقبة الصحة

```python
# Check sensor status
check_sensor_status(device_id, readings, expected_interval_minutes=15)

# Detect sensor drift
detect_sensor_drift(readings, window_size=10)

# Calculate data quality score
calculate_data_quality_score(readings)
```

## Running Examples | تشغيل الأمثلة

Run the comprehensive usage examples:

```bash
cd /home/user/sahool-unified-v15-idp
python -m apps.services.iot_gateway.examples.aggregator_usage
```

## Running Tests | تشغيل الاختبارات

```bash
cd /home/user/sahool-unified-v15-idp
python -m pytest apps/services/iot-gateway/tests/test_sensor_aggregator.py -v
```

## File Structure | هيكل الملفات

```
apps/services/iot-gateway/
├── src/
│   ├── sensor_aggregator.py          # Main aggregator implementation
│   ├── models/
│   │   ├── __init__.py
│   │   └── sensor_data.py            # Data models and thresholds
│   ├── mqtt_client.py                # MQTT client
│   ├── normalizer.py                 # Data normalization
│   └── main.py                       # Gateway service
├── tests/
│   ├── test_sensor_aggregator.py     # Aggregator tests
│   └── test_health.py                # Health check tests
├── examples/
│   └── aggregator_usage.py           # Usage examples
└── SENSOR_AGGREGATOR_README.md       # This file
```

## Integration with IoT Gateway | التكامل مع بوابة الإنترنت

The sensor aggregator can be integrated into the IoT Gateway's main service:

```python
from sensor_aggregator import SensorAggregator
from models.sensor_data import SensorReading

# Initialize aggregator
aggregator = SensorAggregator()

# Process incoming MQTT data
async def handle_mqtt_message(msg: MqttMessage):
    # Normalize reading
    reading = normalize(msg.payload, msg.topic)

    # Store reading (add to database or cache)
    # ...

    # Periodically aggregate and analyze
    # Can be triggered by:
    # - Scheduled job (every hour/day)
    # - API endpoint request
    # - Event-driven (after N readings)
```

## Performance Considerations | اعتبارات الأداء

- **Memory**: Uses in-memory caching for recent readings
- **Computation**: O(n log n) for most statistical operations
- **Scalability**: Designed for thousands of readings per aggregation
- **Optimization**: Percentile calculations use efficient algorithms

## Future Enhancements | التحسينات المستقبلية

- [ ] Machine learning-based anomaly detection
- [ ] Predictive sensor failure analysis
- [ ] Real-time streaming aggregation
- [ ] Multi-field comparative analysis
- [ ] Advanced visualization exports
- [ ] Database persistence layer
- [ ] API endpoints for aggregation service

## Support | الدعم

For issues or questions:
- Create an issue in the repository
- Contact: support@sahool.io
- Documentation: https://docs.sahool.io

## License | الترخيص

Part of SAHOOL Unified Platform v15
Copyright © 2024 SAHOOL

---

**SAHOOL IoT** - Empowering Yemeni Agriculture with Smart Technology
**صحول للإنترنت** - تمكين الزراعة اليمنية بالتكنولوجيا الذكية
