# Context Compression Skill

## Description

This skill enables efficient compression of agricultural context data for SAHOOL operations. It reduces token usage while preserving critical information for crop advisory, field operations, and farm management decisions. Essential for offline-first environments with limited bandwidth and for optimizing LLM context windows in agricultural AI systems.

## Instructions

### Compression Principles

1. **Preserve Critical Data**: Never compress safety-critical agricultural information
2. **Maintain Bilingual Keys**: Keep both Arabic and English identifiers for key terms
3. **Use Domain Abbreviations**: Apply standard agricultural abbreviations
4. **Structured Summaries**: Convert verbose data to structured formats
5. **Temporal Relevance**: Prioritize recent data over historical

### Standard Agricultural Abbreviations

| Full Term | Abbreviation | Arabic | المختصر |
|-----------|--------------|--------|---------|
| Hectare | ha | هكتار | هـ |
| Normalized Difference Vegetation Index | NDVI | مؤشر الغطاء النباتي | م.غ.ن |
| Leaf Area Index | LAI | مؤشر مساحة الورق | م.م.و |
| Evapotranspiration | ET | التبخر-النتح | ت.ن |
| Parts Per Million | ppm | جزء في المليون | ج.م |
| Kilogram per Hectare | kg/ha | كغ/هكتار | كغ/هـ |
| Cubic Meter | m³ | متر مكعب | م³ |
| Electrical Conductivity | EC | التوصيل الكهربائي | ت.ك |
| Soil Moisture | SM | رطوبة التربة | ر.ت |
| Days After Planting | DAP | أيام بعد الزراعة | أ.ب.ز |

### Compression Levels

#### Level 1: Light Compression (80% retention)
- Remove redundant descriptions
- Apply standard abbreviations
- Keep all numerical data

#### Level 2: Medium Compression (50% retention)
- Summarize repeated patterns
- Aggregate time-series data
- Remove non-essential metadata

#### Level 3: Heavy Compression (25% retention)
- Extract key metrics only
- Single-line summaries
- Critical alerts only

### Field Data Compression Template

**Original (verbose):**
```
Field FIELD-003 located in the northern section of Al-Rashid Farm is currently
cultivating winter wheat variety Sakha 95. The field covers an area of 8.5
hectares and uses center pivot irrigation. The soil type is clay loam with a
pH of 7.2. Current NDVI reading is 0.72 indicating healthy vegetation. The
crop was planted on November 15, 2024 and is currently in the tillering stage.
```

**Level 1 Compressed:**
```
FIELD-003 | North | Al-Rashid
Crop: Winter wheat (Sakha 95) | 8.5ha | Center pivot
Soil: Clay loam, pH 7.2 | NDVI: 0.72
Planted: 2024-11-15 | Stage: Tillering
```

**Level 2 Compressed:**
```
F003: Wheat-Sakha95 | 8.5ha | NDVI:0.72 | Tillering | pH:7.2
```

**Level 3 Compressed:**
```
F003:Wht|8.5ha|N0.72|Till
```

### Time-Series Data Compression

**Original:**
```
NDVI readings for FIELD-003:
- 2024-12-01: 0.45
- 2024-12-08: 0.52
- 2024-12-15: 0.58
- 2024-12-22: 0.63
- 2024-12-29: 0.68
- 2025-01-05: 0.70
- 2025-01-12: 0.72
```

**Compressed (trend summary):**
```
F003 NDVI: 0.45→0.72 (Dec-Jan) +60% | Trend: ↑ steady
```

### Advisory Compression Template

**Original:**
```
Based on the current soil moisture readings of 35% and the weather forecast
showing no rain expected in the next 72 hours, combined with the high
evapotranspiration rate of 6.2mm per day, we recommend scheduling irrigation
within the next 24 hours. Apply approximately 450 cubic meters per hectare
using drip irrigation to bring soil moisture back to field capacity.
```

**Compressed:**
```
⚠️ IRRIGATE 24h | SM:35% | ET:6.2mm/d | No rain 72h
Rx: 450m³/ha drip → field capacity
```

### Multi-Field Summary Compression

**Original (multiple fields):**
```
Field 001: Wheat, 5.2ha, NDVI 0.68, healthy, tillering stage
Field 002: Barley, 3.8ha, NDVI 0.65, healthy, heading stage
Field 003: Wheat, 8.5ha, NDVI 0.72, healthy, tillering stage
Field 004: Date palm, 450 trees, healthy, dormant
Field 005: Fallow, 2.1ha, preparing for tomato
```

**Compressed (table format):**
```
| ID | Crop | Area | NDVI | Status |
|----|------|------|------|--------|
| 01 | Wht  | 5.2  | .68  | Till   |
| 02 | Bar  | 3.8  | .65  | Head   |
| 03 | Wht  | 8.5  | .72  | Till   |
| 04 | Palm | 450t | -    | Dorm   |
| 05 | -    | 2.1  | -    | Prep   |
```

### Alert Priority Encoding

Encode alert priority in compressed format:

```
[!!!] Critical - immediate action required | حرج
[!!]  Warning - action within 24-48h | تحذير
[!]   Info - monitor situation | معلومات
[.]   Normal - no action needed | عادي
```

**Example:**
```
[!!!] F003: Aphid >30/tiller | Spray NOW
[!!]  F001: SM 32% | Irrigate 48h
[!]   F002: Heading stage | Monitor
[.]   F004: Palm healthy | Routine
```

### Sensor Data Compression

**Original:**
```json
{
  "sensor_id": "SMS-003-A",
  "field_id": "FIELD-003",
  "timestamp": "2025-01-13T08:30:00Z",
  "soil_moisture_10cm": 42.5,
  "soil_moisture_30cm": 48.2,
  "soil_moisture_60cm": 55.1,
  "soil_temperature_10cm": 12.3,
  "electrical_conductivity": 1.8,
  "battery_level": 87
}
```

**Compressed:**
```
SMS-003-A@0830: SM[42/48/55] T:12.3 EC:1.8 Batt:87%
```

### Bilingual Compression Keys

Maintain bilingual reference in compressed outputs:

```
Crops: Wht=قمح | Bar=شعير | Tom=طماطم | Cuc=خيار | Palm=نخيل
Status: Act=نشط | Harv=محصود | Fal=بور | Plan=مخطط
Alerts: Crit=حرج | Warn=تحذير | Info=معلومات | OK=عادي
```

## Examples

### Example 1: Compress Daily Farm Report

**Input:**
```
Daily Farm Report - Al-Rashid Farm - January 13, 2025

Weather Summary:
Today's weather was partly cloudy with a high temperature of 18°C and a low
of 8°C. Relative humidity averaged 65%. Wind was from the northwest at
12 km/h. No precipitation recorded. Tomorrow's forecast shows similar
conditions with slightly warmer temperatures.

Field Status:
Field 001 (North Wheat): The wheat crop is progressing well through the
tillering stage. NDVI reading of 0.68 indicates good canopy development.
Soil moisture at 45% is adequate. No pest or disease issues observed.

Field 003 (East Wheat): Concern noted - NDVI dropped from 0.75 to 0.72
over the past week. Visual inspection revealed some yellowing in the
eastern corner. Soil test showed nitrogen deficiency (N: 18ppm vs
recommended 25ppm). Recommend nitrogen application of 46 kg/ha urea.

Field 004 (Date Palm Grove): All 450 trees inspected. 3 trees showing
signs of red palm weevil damage in Block B. Treatment initiated with
injection method. Remaining trees healthy.

Irrigation Summary:
Total water used today: 2,450 m³
Field 001: 580 m³ (center pivot)
Field 003: 720 m³ (center pivot)
Field 004: 1,150 m³ (drip system)
Water source (Well-001): Operating normally, 78% capacity
```

**Output (Level 2 Compression):**
```
=== Al-Rashid Farm | 2025-01-13 ===

WEATHER: 8-18°C | RH:65% | Wind:NW@12km/h | No rain
Tomorrow: Similar, warmer

FIELDS:
| ID  | Crop | NDVI | SM  | Status          |
|-----|------|------|-----|-----------------|
| F01 | Wht  | .68  | 45% | OK-Tillering    |
| F03 | Wht  | .72↓ | -   | [!!]N-deficient |
| F04 | Palm | -    | -   | [!]3 RPW trees  |

ALERTS:
[!!] F03: N:18ppm<25 | Rx: Urea 46kg/ha
[!]  F04: RPW Block-B | Treatment active

WATER: 2,450m³ total
F01:580 | F03:720 | F04:1150 | Well:78%cap
```

### Example 2: Compress Crop Advisory Response

**Input:**
```
Crop Advisory Response for Farmer Ahmed - Field FIELD-003

Based on the comprehensive analysis of your wheat field, including satellite
imagery, soil sensor data, weather forecasts, and historical yield data,
we provide the following recommendations:

Irrigation Management:
Your current soil moisture level of 38% is approaching the stress threshold
for wheat at the tillering stage. Given the forecast of no rain for the next
5 days and daily evapotranspiration rates of 5.8mm, we strongly recommend
irrigating within the next 24 hours. Apply 500 cubic meters per hectare to
bring moisture to field capacity (approximately 55%). Schedule the next
irrigation in 7 days, adjusting based on actual weather conditions.

Fertilizer Application:
Nitrogen levels are below optimal at 18 parts per million. For wheat at
tillering stage, the target should be 25-30 ppm. We recommend applying 46
kilograms per hectare of urea (46% N) as a top dressing. Apply early morning
when dew is present for better absorption. Do not apply if rain is expected
within 24 hours to prevent runoff.

Pest Monitoring:
No significant pest pressure detected currently. However, given reports of
aphid outbreaks in neighboring farms, we recommend daily scouting of your
field borders. Economic threshold for aphids in wheat is 25 aphids per
tiller. If exceeded, contact advisory for spray recommendations.

Growth Stage Assessment:
Your wheat is at Zadoks growth stage 25 (main shoot and 5 tillers). This is
consistent with the planting date and accumulated growing degree days.
Expected heading date: March 10-15, 2025. Harvest window: May 15-25, 2025.

العربية:
استناداً إلى تحليل شامل لحقل القمح الخاص بك، نوصي بالري خلال 24 ساعة وإضافة
اليوريا بمعدل 46 كغ/هكتار. راقب حشرة المن يومياً.
```

**Output (Level 2 Compression):**
```
=== ADVISORY: F003 Wheat | Ahmed ===

[!!] IRRIGATE <24h
SM:38%→55% | ET:5.8mm/d | No rain 5d
Rx: 500m³/ha | Next: +7d

[!!] FERTILIZE (N-deficient)
N:18ppm<25 | Stage:Tillering
Rx: Urea 46kg/ha | AM w/dew | Skip if rain<24h

[!] PEST WATCH
Aphid risk (neighbors) | Scout borders daily
Threshold: 25/tiller → spray alert

GROWTH: Zadoks-25 (5 tillers)
Heading: Mar 10-15 | Harvest: May 15-25

---
ري خلال 24س | يوريا 46كغ/هـ | مراقبة المن
```

### Example 3: Compress Sensor Array Data

**Input:**
```json
{
  "farm_id": "FARM-001",
  "timestamp": "2025-01-13T14:00:00Z",
  "sensors": [
    {
      "id": "SMS-001-A",
      "field": "FIELD-001",
      "type": "soil_moisture",
      "readings": {
        "depth_10cm": 44.2,
        "depth_30cm": 48.5,
        "depth_60cm": 52.1
      },
      "temperature": 14.2,
      "ec": 1.6,
      "battery": 92
    },
    {
      "id": "SMS-001-B",
      "field": "FIELD-001",
      "type": "soil_moisture",
      "readings": {
        "depth_10cm": 42.8,
        "depth_30cm": 47.2,
        "depth_60cm": 51.8
      },
      "temperature": 14.0,
      "ec": 1.7,
      "battery": 88
    },
    {
      "id": "SMS-003-A",
      "field": "FIELD-003",
      "type": "soil_moisture",
      "readings": {
        "depth_10cm": 36.5,
        "depth_30cm": 41.2,
        "depth_60cm": 48.9
      },
      "temperature": 13.8,
      "ec": 1.9,
      "battery": 85
    },
    {
      "id": "WS-001",
      "type": "weather_station",
      "readings": {
        "temperature": 17.2,
        "humidity": 58,
        "wind_speed": 14.2,
        "wind_direction": "NW",
        "solar_radiation": 420,
        "rain_today": 0
      },
      "battery": 95
    },
    {
      "id": "FM-001",
      "type": "flow_meter",
      "readings": {
        "flow_rate": 125.5,
        "total_today": 1850,
        "pressure": 3.2
      }
    }
  ]
}
```

**Output (Compressed):**
```
FARM-001 @ 14:00 | 2025-01-13

SOIL MOISTURE (avg by field):
F01: SM[43/48/52] T:14.1 EC:1.65 | OK
F03: SM[37/41/49] T:13.8 EC:1.9  | [!]Low

WEATHER (WS-001):
17.2°C | RH:58% | NW@14km/h | SR:420 | Rain:0

WATER (FM-001):
125.5L/min | Today:1850m³ | P:3.2bar

BATTERY: All>85% OK
```

### Example 4: Decompress for Full Context

When context needs expansion, provide decompression mapping:

**Compressed Input:**
```
[!!!] F003:Wht|N0.72↓|SM37|N:18<25|Aphid-risk
Rx: Irr500m³+Urea46kg|Scout daily
```

**Decompressed Output:**
```
CRITICAL ALERT - Field 003 (Wheat)
تنبيه حرج - الحقل 003 (قمح)

Issues Detected:
1. NDVI declining: 0.72 (decreasing trend) - vegetation stress
2. Soil moisture low: 37% (below 40% threshold)
3. Nitrogen deficient: 18ppm (target: 25ppm minimum)
4. Aphid risk: neighboring fields reporting infestations

Recommended Actions:
1. IRRIGATE: Apply 500 cubic meters per hectare immediately
2. FERTILIZE: Apply 46 kg/ha urea after irrigation
3. MONITOR: Daily field scouting for aphid presence

الإجراءات الموصى بها:
1. الري: 500 متر مكعب/هكتار فوراً
2. التسميد: 46 كغ/هكتار يوريا بعد الري
3. المراقبة: فحص يومي للحقل للكشف عن المن
```
