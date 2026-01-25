# Crop Phenology Detection - كشف مراحل نمو المحاصيل

## Overview | نظرة عامة

The SAHOOL Satellite Service now includes advanced crop phenology detection capabilities. Using NDVI time series from satellite imagery, the system can automatically detect crop growth stages based on the BBCH scale and provide stage-specific recommendations for farmers.

يتضمن نظام SAHOOL للأقمار الصناعية الآن قدرات متقدمة لكشف مراحل نمو المحاصيل. باستخدام بيانات NDVI من صور الأقمار الصناعية، يمكن للنظام اكتشاف مراحل نمو المحاصيل تلقائياً بناءً على مقياس BBCH وتقديم توصيات خاصة بكل مرحلة للمزارعين.

## Features | المميزات

### 1. Automatic Growth Stage Detection

- **SOS Detection**: Start of Season - beginning of green-up
- **POS Detection**: Peak of Season - maximum vegetation
- **EOS Detection**: End of Season - senescence begins
- **BBCH Mapping**: Maps to standardized BBCH growth stages

### 2. Yemen Crop Coverage

The system supports **12 major Yemen crops** across 5 categories:

#### Cereals (الحبوب)

- **Wheat (قمح)**: 120 days
- **Sorghum (ذرة رفيعة)**: 110 days
- **Millet (دخن)**: 90 days

#### Vegetables (الخضروات)

- **Tomato (طماطم)**: 105 days
- **Potato (بطاطس)**: 100 days
- **Onion (بصل)**: 120 days

#### Legumes (البقوليات)

- **Faba Bean (فول)**: 130 days
- **Lentil (عدس)**: 110 days

#### Cash Crops (المحاصيل النقدية)

- **Coffee (بن)**: 365 days (perennial)
- **Qat (قات)**: 90 days (leaf harvest cycle)

#### Fruits (الفواكه)

- **Mango (مانجو)**: 180 days
- **Grape (عنب)**: 150 days

### 3. Stage-Specific Recommendations

For each growth stage, the system provides:

- **Irrigation guidance**: When and how much to water
- **Fertilization timing**: NPK requirements by stage
- **Pest monitoring**: Stage-sensitive pest alerts
- **Critical period warnings**: Flowering, fruit set, etc.
- **Harvest preparation**: Pre-harvest planning

### 4. ActionTemplate Integration

Phenology detection automatically generates ActionTemplate tasks for mobile app:

- Stage-specific task cards
- Urgency levels based on critical periods
- Offline-executable instructions
- NATS event publishing for real-time notifications

## API Endpoints

### 1. Detect Current Growth Stage

```http
GET /v1/phenology/{field_id}?crop_type=wheat&lat=15.3694&lon=44.1910&planting_date=2024-11-01&days=60
```

**Response:**

```json
{
  "field_id": "field_001",
  "crop_type": "wheat",
  "current_stage": {
    "id": "flowering",
    "name_ar": "إزهار",
    "name_en": "Flowering",
    "days_in_stage": 8,
    "stage_start_date": "2024-12-20"
  },
  "next_stage": {
    "id": "fruit_dev",
    "name_ar": "تطور الثمار",
    "name_en": "Fruit Development",
    "days_to_next_stage": 4
  },
  "season_progress": {
    "percent": 65.5,
    "sos_date": "2024-11-15",
    "pos_date": "2024-12-25",
    "eos_date": null,
    "estimated_harvest_date": "2025-02-28"
  },
  "ndvi_at_detection": 0.72,
  "confidence": 0.89,
  "recommendations_ar": [
    "🌱 المحصول (قمح) في مرحلة إزهار",
    "💐 مرحلة حرجة - تجنب الإجهاد المائي",
    "🐝 تأكد من وجود الملقحات إن أمكن",
    "⚠️ فترة حرجة: حساس للإجهاد المائي"
  ],
  "recommendations_en": [
    "🌱 Crop (wheat) is in Flowering stage",
    "💐 Critical period - avoid water stress",
    "🐝 Ensure pollinators presence if applicable",
    "⚠️ Critical period: Sensitive to water stress"
  ]
}
```

### 2. Get Phenology Timeline (Planning)

```http
GET /v1/phenology/{field_id}/timeline?crop_type=wheat&planting_date=2024-11-01
```

**Response:**

```json
{
  "field_id": "field_001",
  "crop_type": "wheat",
  "planting_date": "2024-11-01",
  "harvest_estimate": "2025-03-01",
  "season_length_days": 120,
  "stages": [
    {
      "stage": "germination",
      "stage_ar": "إنبات",
      "stage_en": "Germination",
      "start_date": "2024-11-01",
      "end_date": "2024-11-11",
      "duration_days": 10,
      "ndvi_range": { "min": 0.15, "max": 0.25 }
    },
    {
      "stage": "emergence",
      "stage_ar": "بزوغ",
      "stage_en": "Emergence",
      "start_date": "2024-11-11",
      "end_date": "2024-11-26",
      "duration_days": 15,
      "ndvi_range": { "min": 0.25, "max": 0.35 }
    }
  ],
  "critical_periods": [
    {
      "stage": "tillering",
      "stage_ar": "التفريع",
      "stage_en": "Tillering",
      "start_date": "2024-11-26",
      "end_date": "2024-12-26",
      "reason_ar": "فترة حرجة للتسميد",
      "reason_en": "Critical fertilization period"
    }
  ]
}
```

### 3. Get Stage Recommendations

```http
GET /v1/phenology/recommendations/wheat/flowering
```

**Response:**

```json
{
  "crop_type": "wheat",
  "crop_name_ar": "قمح",
  "stage": {
    "id": "flowering",
    "name_ar": "إزهار",
    "name_en": "Flowering"
  },
  "recommendations_ar": [
    "🌱 المحصول (قمح) في مرحلة إزهار",
    "💐 مرحلة حرجة - تجنب الإجهاد المائي",
    "🐝 تأكد من وجود الملقحات إن أمكن"
  ],
  "recommendations_en": [
    "🌱 Crop (wheat) is in Flowering stage",
    "💐 Critical period - avoid water stress",
    "🐝 Ensure pollinators presence if applicable"
  ]
}
```

### 4. List Supported Crops

```http
GET /v1/phenology/crops
```

**Response:**

```json
{
  "crops": [
    {
      "id": "wheat",
      "name_ar": "قمح",
      "name_en": "Wheat",
      "season_length_days": 120
    },
    ...
  ],
  "total": 12
}
```

### 5. Detect with ActionTemplate

```http
POST /v1/phenology/{field_id}/analyze-with-action
```

**Request Body:**

```json
{
  "field_id": "field_001",
  "farmer_id": "farmer_123",
  "tenant_id": "tenant_abc",
  "crop_type": "wheat",
  "latitude": 15.3694,
  "longitude": 44.191,
  "planting_date": "2024-11-01",
  "days": 60,
  "publish_event": true
}
```

**Response:**

```json
{
  "phenology": {
    "field_id": "field_001",
    "crop_type": "wheat",
    "current_stage": {
      "id": "flowering",
      "name_ar": "إزهار",
      "name_en": "Flowering"
    },
    "days_in_stage": 8,
    "season_progress_percent": 65.5,
    "confidence": 0.89,
    "recommendations_ar": [...],
    "recommendations_en": [...]
  },
  "action_template": {
    "action_id": "act_uuid",
    "action_type": "monitoring",
    "title_ar": "مراقبة دقيقة - مرحلة الإزهار الحرجة",
    "title_en": "Close Monitoring - Critical Flowering Stage",
    "urgency": "medium",
    "confidence": 0.89,
    "estimated_duration_minutes": 45,
    "offline_executable": true
  },
  "task_card": {
    "id": "act_uuid",
    "type": "monitoring",
    "title_ar": "مراقبة دقيقة - مرحلة الإزهار الحرجة",
    "urgency": {
      "level": "medium",
      "color": "#EAB308"
    },
    "crop_type": "wheat",
    "current_stage": "إزهار",
    "season_progress": 65.5
  },
  "nats_published": true
}
```

## Algorithm Details

### Phenological Metrics

The detector uses three key phenological metrics:

1. **SOS (Start of Season)**
   - NDVI crosses emergence threshold (0.20) with sustained increase
   - Indicates beginning of active growth

2. **POS (Peak of Season)**
   - Maximum NDVI in time series
   - Typically occurs during stem elongation/flowering

3. **EOS (End of Season)**
   - NDVI drops below harvest threshold (0.25) after POS
   - Indicates crop senescence

### NDVI Thresholds

```python
NDVI_THRESHOLDS = {
    "bare_soil": 0.10,        # Bare soil baseline
    "emergence": 0.20,        # Green-up begins (SOS)
    "active_growth": 0.35,    # Active vegetative growth
    "peak": 0.65,             # Maximum greenness (POS)
    "senescence_start": 0.45, # Decline begins
    "harvest_ready": 0.25,    # Ready for harvest (EOS)
}
```

### Stage Determination

The algorithm:

1. Smooths NDVI time series (moving average)
2. Detects SOS, POS, EOS dates
3. Calculates days since SOS
4. Maps to crop-specific growth stages based on:
   - Days since SOS
   - Current NDVI value
   - Expected stage durations for crop type

### Confidence Calculation

Confidence is based on:

- **NDVI consistency** (60%): How well current NDVI matches expected range
- **Observation count** (40%): More observations = higher confidence

## Crop-Specific Parameters

Each crop has calibrated parameters:

```python
"wheat": {
    "name_ar": "قمح",
    "season_length_days": 120,
    "stages": {
        "germination": {"duration_days": 10, "ndvi_start": 0.15, "ndvi_end": 0.25},
        "emergence": {"duration_days": 15, "ndvi_start": 0.25, "ndvi_end": 0.35},
        "tillering": {"duration_days": 30, "ndvi_start": 0.35, "ndvi_end": 0.55},
        # ... more stages
    },
    "critical_periods": [
        {"stage": "tillering", "reason_ar": "فترة حرجة للتسميد"},
        {"stage": "flowering", "reason_ar": "حساس للإجهاد المائي"}
    ]
}
```

## Testing

Run the test suite:

```bash
cd apps/services/satellite-service
python3 tests/test_phenology.py
```

## Integration Examples

### Example 1: Wheat Field Monitoring

```python
# Farmer plants wheat on Nov 1
# System monitors NDVI every 5 days via Sentinel-2
# At day 60 (late December):

GET /v1/phenology/field_123?crop_type=wheat&lat=15.37&lon=44.19&planting_date=2024-11-01&days=60

# Response: "Tillering stage - Apply nitrogen fertilizer"
# Mobile app shows: Task card with urgency=medium
```

### Example 2: Pre-Season Planning

```python
# Farmer wants to plan irrigation schedule for tomato

GET /v1/phenology/field_456/timeline?crop_type=tomato&planting_date=2024-12-01

# Response: Complete timeline with all stages and critical periods
# Farmer can plan resources and labor accordingly
```

### Example 3: Critical Period Alert

```python
# System detects wheat entering flowering stage
# Critical period flagged in crop parameters
# Automatic ActionTemplate generated with urgency=high
# NATS event published → Mobile push notification
# Task: "Close monitoring required - sensitive to water stress"
```

## References

- **BBCH Scale**: Meier, U. (2001). Growth stages of mono-and dicotyledonous plants. Federal Biological Research Centre for Agriculture and Forestry.
- **Phenology Metrics**: Reed et al. (1994). Measuring phenological variability from satellite imagery. Journal of Vegetation Science.
- **NDVI Applications**: Bolton & Friedl (2013). Forecasting crop yield using remotely sensed vegetation indices. Remote Sensing of Environment.
- **Yemen Agriculture**: Ministry of Agriculture and Irrigation, Republic of Yemen

## Future Enhancements

1. **Multi-year Learning**: Adjust thresholds based on historical performance
2. **Weather Integration**: Factor in temperature, rainfall for better predictions
3. **Variety-Specific**: Different parameters for crop varieties
4. **Spatial Variation**: Within-field phenology heterogeneity
5. **Real Sentinel Data**: Integration with actual Sentinel-2 imagery (currently simulated)

## Support

For questions or issues:

- GitHub Issues: [sahool-unified-v15-idp](https://github.com/yourusername/sahool-unified-v15-idp)
- Email: support@sahool.example.com
