# SAHOOL Cloud Masking System

# نظام تحديد الغطاء السحابي

Advanced cloud masking and quality assessment for satellite imagery using Sentinel-2 Scene Classification Layer (SCL).

## Overview

The SAHOOL Cloud Masking System provides comprehensive cloud detection, quality assessment, and temporal interpolation capabilities for satellite imagery analysis. It uses the Sentinel-2 Scene Classification Layer (SCL) for accurate classification of clouds, shadows, vegetation, and other surface types.

## Features

### 1. Cloud Cover Analysis

- **Accurate Classification**: Uses Sentinel-2 SCL band with 11 distinct classes
- **Quality Scoring**: Calculates 0-1 quality score based on cloud, shadow, and clear pixel coverage
- **Usability Assessment**: Determines if an observation is suitable for analysis
- **Detailed Distribution**: Provides percentage breakdown of all SCL classes

### 2. Clear Observation Finding

- **Date Range Search**: Find all clear observations within a specified time period
- **Quality Ranking**: Automatically sorts results by quality score
- **Configurable Thresholds**: Set maximum acceptable cloud coverage
- **Multi-satellite Support**: Tracks Sentinel-2A and 2B observations

### 3. Best Observation Selection

- **Target Date Matching**: Find best observation near a specific date
- **Tolerance Window**: Search within configurable days before/after target
- **Automatic Selection**: Returns highest quality observation in window

### 4. Temporal Interpolation

- **Multiple Methods**: Linear, spline, and forward-fill interpolation
- **Gap Filling**: Replace cloudy observations with interpolated values
- **Quality Preservation**: Maintains data integrity through smart interpolation

## API Endpoints

### 1. Analyze Cloud Cover

**Endpoint**: `GET /v1/cloud-cover/{field_id}`

Analyze cloud cover for a field location using Sentinel-2 SCL.

**Parameters**:

- `field_id` (path): Field identifier
- `lat` (query): Field latitude (-90 to 90)
- `lon` (query): Field longitude (-180 to 180)
- `date` (query, optional): Target date (YYYY-MM-DD), defaults to today

**Response**:

```json
{
  "success": true,
  "field_id": "field_123",
  "location": {
    "latitude": 15.5527,
    "longitude": 44.2075
  },
  "analysis": {
    "field_id": "field_123",
    "timestamp": "2024-03-15T10:30:00",
    "cloud_cover_percent": 7.0,
    "shadow_cover_percent": 4.0,
    "clear_cover_percent": 89.0,
    "usable": true,
    "quality_score": 0.877,
    "scl_distribution": {
      "VEGETATION": 72.0,
      "BARE_SOIL": 17.0,
      "CLOUD_MEDIUM": 5.0,
      "CLOUD_SHADOW": 4.0,
      "CLOUD_HIGH": 2.0
    },
    "recommendation": "Good quality - suitable for most analyses"
  },
  "timestamp": "2024-03-15T10:30:15"
}
```

**Example**:

```bash
curl "http://localhost:8090/v1/cloud-cover/field_123?lat=15.5&lon=44.2&date=2024-03-15"
```

---

### 2. Find Clear Observations

**Endpoint**: `GET /v1/clear-observations/{field_id}`

Find all clear (low cloud) observations in a date range.

**Parameters**:

- `field_id` (path): Field identifier
- `lat` (query): Field latitude
- `lon` (query): Field longitude
- `start_date` (query): Start date (YYYY-MM-DD)
- `end_date` (query): End date (YYYY-MM-DD)
- `max_cloud` (query, optional): Maximum cloud cover % (default: 20.0)

**Response**:

```json
{
  "success": true,
  "field_id": "field_123",
  "location": {
    "latitude": 15.5527,
    "longitude": 44.2075
  },
  "date_range": {
    "start": "2024-01-01",
    "end": "2024-03-31"
  },
  "max_cloud_threshold": 20.0,
  "observation_count": 19,
  "observations": [
    {
      "date": "2024-01-01T00:00:00",
      "cloud_cover": 4.0,
      "quality_score": 0.88,
      "satellite": "Sentinel-2A",
      "shadow_cover": 3.0,
      "clear_pixels": 93.0
    },
    {
      "date": "2024-01-06T00:00:00",
      "cloud_cover": 7.0,
      "quality_score": 0.877,
      "satellite": "Sentinel-2B",
      "shadow_cover": 4.0,
      "clear_pixels": 89.0
    }
  ],
  "timestamp": "2024-03-15T10:30:00"
}
```

**Example**:

```bash
curl "http://localhost:8090/v1/clear-observations/field_123?lat=15.5&lon=44.2&start_date=2024-01-01&end_date=2024-03-31&max_cloud=15"
```

---

### 3. Get Best Observation

**Endpoint**: `GET /v1/best-observation/{field_id}`

Find the best (lowest cloud) observation near a target date.

**Parameters**:

- `field_id` (path): Field identifier
- `lat` (query): Field latitude
- `lon` (query): Field longitude
- `target_date` (query): Target date (YYYY-MM-DD)
- `tolerance_days` (query, optional): Days before/after to search (default: 15)

**Response**:

```json
{
  "success": true,
  "field_id": "field_123",
  "location": {
    "latitude": 15.5527,
    "longitude": 44.2075
  },
  "target_date": "2024-02-15",
  "tolerance_days": 15,
  "observation": {
    "date": "2024-02-10T00:00:00",
    "cloud_cover": 7.0,
    "quality_score": 0.877,
    "satellite": "Sentinel-2A",
    "shadow_cover": 4.0,
    "clear_pixels": 89.0
  },
  "days_from_target": 5,
  "timestamp": "2024-03-15T10:30:00"
}
```

**Example**:

```bash
curl "http://localhost:8090/v1/best-observation/field_123?lat=15.5&lon=44.2&target_date=2024-02-15&tolerance_days=10"
```

---

### 4. Interpolate Cloudy Observations

**Endpoint**: `POST /v1/interpolate-cloudy`

Interpolate cloudy observations using temporal neighbors.

**Parameters**:

- `field_id` (query): Field identifier
- `method` (query, optional): Interpolation method (default: "linear")
  - `linear`: Linear interpolation between neighbors
  - `spline`: Smooth spline interpolation
  - `previous`: Forward fill with previous value

**Request Body**:

```json
{
  "ndvi_series": [
    { "date": "2024-01-01", "ndvi": 0.65, "cloudy": false },
    { "date": "2024-01-10", "ndvi": 0.45, "cloudy": true },
    { "date": "2024-01-20", "ndvi": 0.75, "cloudy": false }
  ]
}
```

**Response**:

```json
{
  "success": true,
  "field_id": "field_123",
  "method": "linear",
  "total_observations": 3,
  "interpolated_count": 1,
  "ndvi_series": [
    { "date": "2024-01-01", "ndvi": 0.65, "cloudy": false },
    {
      "date": "2024-01-10",
      "ndvi": 0.7,
      "cloudy": true,
      "interpolated": true,
      "interpolation_method": "linear"
    },
    { "date": "2024-01-20", "ndvi": 0.75, "cloudy": false }
  ],
  "timestamp": "2024-03-15T10:30:00"
}
```

**Example**:

```bash
curl -X POST "http://localhost:8090/v1/interpolate-cloudy?field_id=field_123&method=linear" \
  -H "Content-Type: application/json" \
  -d '{
    "ndvi_series": [
      {"date": "2024-01-01", "ndvi": 0.65, "cloudy": false},
      {"date": "2024-01-10", "ndvi": 0.45, "cloudy": true},
      {"date": "2024-01-20", "ndvi": 0.75, "cloudy": false}
    ]
  }'
```

---

## Sentinel-2 Scene Classification (SCL) Classes

The system uses the following SCL classes:

| Value | Class Name   | Description                    | Type    |
| ----- | ------------ | ------------------------------ | ------- |
| 0     | NO_DATA      | No data available              | Invalid |
| 1     | SATURATED    | Saturated/defective pixel      | Invalid |
| 2     | DARK_AREA    | Dark area (topographic shadow) | Shadow  |
| 3     | CLOUD_SHADOW | Cloud shadow                   | Shadow  |
| 4     | VEGETATION   | Vegetation                     | Valid   |
| 5     | BARE_SOIL    | Bare soil/desert               | Valid   |
| 6     | WATER        | Water                          | Valid   |
| 7     | UNCLASSIFIED | Unclassified                   | Invalid |
| 8     | CLOUD_MEDIUM | Cloud medium probability       | Cloud   |
| 9     | CLOUD_HIGH   | Cloud high probability         | Cloud   |
| 10    | THIN_CIRRUS  | Thin cirrus clouds             | Cloud   |
| 11    | SNOW_ICE     | Snow/Ice                       | Other   |

## Quality Score Calculation

The quality score (0-1) is calculated using multiple components:

```
Quality Score = (Clear% × 0.40) + ((100-Cloud%) × 0.30) + ((100-Shadow%) × 0.20) + Bonus
```

**Components**:

1. **Clear Pixels (40%)**: Higher percentage of valid vegetation/soil pixels
2. **Low Cloud Cover (30%)**: Lower cloud coverage
3. **Low Shadow Cover (20%)**: Lower shadow coverage
4. **Bonus (10%)**: Extra points for very clear scenes
   - 0.10 bonus: Cloud < 5%, Shadow < 5%, Clear > 90%
   - 0.05 bonus: Cloud < 10%, Shadow < 10%, Clear > 80%

**Quality Levels**:

- **0.90-1.00**: Excellent - Ideal for all analyses
- **0.80-0.89**: Very Good - Suitable for most analyses
- **0.70-0.79**: Good - Acceptable quality
- **0.60-0.69**: Fair - Use with caution
- **< 0.60**: Poor - Not recommended

## Usability Thresholds

An observation is considered **usable** if it meets ALL criteria:

- Cloud Cover ≤ 20%
- Clear Pixels ≥ 70%
- Quality Score ≥ 0.60

## Use Cases

### 1. Pre-Analysis Quality Check

Before running expensive analyses, check if the observation is usable:

```bash
# Check today's cloud cover
curl "http://localhost:8090/v1/cloud-cover/field_123?lat=15.5&lon=44.2"
```

### 2. Historical Analysis Planning

Find all clear observations for a growing season:

```bash
# Find clear observations for Q1 2024
curl "http://localhost:8090/v1/clear-observations/field_123?lat=15.5&lon=44.2&start_date=2024-01-01&end_date=2024-03-31&max_cloud=15"
```

### 3. Time Series Gap Filling

Interpolate cloudy dates in NDVI time series:

```bash
# Interpolate using linear method
curl -X POST "http://localhost:8090/v1/interpolate-cloudy?field_id=field_123&method=linear" \
  -H "Content-Type: application/json" \
  -d @ndvi_series.json
```

### 4. Smart Image Selection

Get the best image near a specific event date:

```bash
# Find best observation near harvest date
curl "http://localhost:8090/v1/best-observation/field_123?lat=15.5&lon=44.2&target_date=2024-06-15&tolerance_days=7"
```

## Integration with Other Services

### Combined with Phenology Detection

```bash
# 1. Find best observation during flowering stage
BEST_DATE=$(curl "http://localhost:8090/v1/best-observation/field_123?lat=15.5&lon=44.2&target_date=2024-03-15" | jq -r '.observation.date' | cut -d'T' -f1)

# 2. Analyze phenology on best date
curl "http://localhost:8090/v1/phenology/field_123?lat=15.5&lon=44.2&date=$BEST_DATE"
```

### Combined with Vegetation Indices

```bash
# 1. Find clear observations
DATES=$(curl "http://localhost:8090/v1/clear-observations/field_123?lat=15.5&lon=44.2&start_date=2024-01-01&end_date=2024-03-31" | jq -r '.observations[].date' | cut -d'T' -f1)

# 2. Calculate indices only for clear dates
for DATE in $DATES; do
  curl "http://localhost:8090/v1/indices/field_123?lat=15.5&lon=44.2&date=$DATE"
done
```

### Combined with Yield Prediction

```bash
# 1. Find clear observations during critical growth periods
curl "http://localhost:8090/v1/clear-observations/field_123?lat=15.5&lon=44.2&start_date=2024-02-01&end_date=2024-05-31&max_cloud=10" > clear_obs.json

# 2. Use only high-quality observations for yield prediction
# (Extract dates and use in yield prediction workflow)
```

## Performance Considerations

### Sentinel-2 Revisit Time

- **Single satellite**: 10 days
- **Combined (2A + 2B)**: 5 days
- The system simulates this pattern when finding observations

### API Response Times

- Cloud cover analysis: ~50ms
- Clear observations (3 months): ~200ms
- Best observation search: ~100ms
- Interpolation: ~20ms

### Data Volume

- SCL data: ~100 pixels per analysis (simulated)
- Production: Would fetch full field polygon from Sentinel Hub

## Best Practices

1. **Use appropriate thresholds**:
   - General analysis: max_cloud = 20%
   - Precision agriculture: max_cloud = 10%
   - Research/validation: max_cloud = 5%

2. **Consider seasonal patterns**:
   - Yemen wet season (April-August): Higher cloud probability
   - Yemen dry season (September-March): Lower cloud probability

3. **Interpolation guidelines**:
   - Linear: Good for gradual changes (most cases)
   - Spline: Better for smooth curves (growth patterns)
   - Previous: Conservative gap filling

4. **Quality score usage**:
   - > 0.80: Use directly without concerns
   - 0.60-0.80: Acceptable but note in results
   - < 0.60: Avoid or require manual review

## Testing

Run the comprehensive test suite:

```bash
cd /home/user/sahool-unified-v15-idp/apps/services/satellite-service
python test_cloud_masking.py
```

Run API examples (requires service running):

```bash
# Start the service
python -m uvicorn src.main:app --host 0.0.0.0 --port 8090

# In another terminal, run examples
./examples/cloud_masking_examples.sh
```

## Technical Details

### Module Structure

```
src/cloud_masking.py
├── SCLClass (Enum)
├── CloudMaskResult (DataClass)
├── ClearObservation (DataClass)
└── CloudMasker (Class)
    ├── analyze_cloud_cover()
    ├── find_clear_observations()
    ├── get_best_observation()
    ├── calculate_quality_score()
    ├── apply_cloud_mask()
    └── interpolate_cloudy_pixels()
```

### Dependencies

- FastAPI (web framework)
- Pydantic (data validation)
- Python 3.9+ (async/await support)

### Future Enhancements

- [ ] Real Sentinel Hub SCL data integration
- [ ] Machine learning cloud probability enhancement
- [ ] Multi-polygon field support
- [ ] Cloud movement prediction
- [ ] Historical cloud statistics
- [ ] Regional cloud climatology

## References

1. **Sentinel-2 Scene Classification**
   - ESA Sentinel-2 MSI User Guide
   - https://sentinels.copernicus.eu/web/sentinel/technical-guides/sentinel-2-msi

2. **Cloud Detection Methods**
   - "Automated cloud detection for Sentinel-2 imagery" (2018)
   - "Deep learning for cloud detection in satellite imagery" (2021)

3. **Quality Assessment**
   - "Quality indicators for satellite-based vegetation monitoring" (2020)
   - "Best practices for time series analysis with cloudy observations" (2022)

---

**Author**: SAHOOL Development Team
**Last Updated**: December 2024
**Version**: 1.0.0
