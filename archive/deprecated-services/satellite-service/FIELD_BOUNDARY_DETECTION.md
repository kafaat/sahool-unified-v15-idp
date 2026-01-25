# Field Boundary Detection

# كشف حدود الحقول من الأقمار الصناعية

Automatic field boundary detection from satellite imagery using NDVI-based edge detection.

## Overview

The Field Boundary Detection system automatically identifies agricultural field boundaries from satellite imagery using advanced image processing techniques. It provides three main capabilities:

1. **Automatic Detection** - Find all fields in an area
2. **Boundary Refinement** - Improve rough boundaries
3. **Change Detection** - Track boundary changes over time

## Features

### 1. NDVI-Based Edge Detection

- Uses NDVI (Normalized Difference Vegetation Index) to identify vegetated areas
- Applies gradient analysis to detect field edges
- Traces contours to extract polygon boundaries
- Filters by minimum/maximum area and shape quality

### 2. Geometric Calculations

- **Area Calculation**: Shoelace formula with latitude correction
- **Perimeter Calculation**: Haversine distance for accurate geographic measurements
- **Centroid**: Geometric center of field
- **Quality Scoring**: Based on shape regularity and detection confidence

### 3. Boundary Simplification

- Douglas-Peucker algorithm to reduce polygon complexity
- Maintains shape accuracy while reducing point count
- Configurable tolerance for different use cases

### 4. Change Detection

- Compare historical boundaries with current imagery
- Detect field expansion, contraction, or stability
- Calculate boundary shift distance and affected areas

## API Endpoints

### 1. Detect Boundaries

```http
POST /v1/boundaries/detect
```

Automatically detect field boundaries around a point.

**Parameters:**

- `lat` (required): Latitude of center point
- `lon` (required): Longitude of center point
- `radius_m` (optional): Search radius in meters (default: 500)
- `date` (optional): Date for imagery (ISO format)

**Example Request:**

```bash
curl -X POST "http://localhost:8090/v1/boundaries/detect?lat=15.5527&lon=44.2075&radius_m=500&date=2024-01-15"
```

**Example Response:**

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Polygon",
        "coordinates": [
          [
            [44.206, 15.551],
            [44.208, 15.551],
            [44.208, 15.553],
            [44.206, 15.553]
          ]
        ]
      },
      "properties": {
        "field_id": "field_15552700_44207500_0",
        "area_hectares": 2.47,
        "perimeter_meters": 628.5,
        "centroid": [44.207, 15.552],
        "detection_confidence": 0.85,
        "method": "ndvi_edge",
        "mean_ndvi": 0.65,
        "quality_score": 0.8
      }
    }
  ],
  "metadata": {
    "center": { "lat": 15.5527, "lon": 44.2075 },
    "radius_meters": 500,
    "detection_date": "2024-01-15T00:00:00",
    "fields_detected": 3,
    "total_area_hectares": 12.5,
    "method": "ndvi_edge_detection"
  }
}
```

### 2. Refine Boundary

```http
POST /v1/boundaries/refine
```

Refine a rough boundary by snapping to NDVI edges.

**Parameters:**

- `coords` (required): Initial boundary coordinates as JSON array `[[lon, lat], ...]`
- `buffer_m` (optional): Refinement buffer in meters (default: 50)

**Example Request:**

```bash
curl -X POST "http://localhost:8090/v1/boundaries/refine" \
  -d "coords=[[44.207, 15.552], [44.208, 15.552], [44.208, 15.553], [44.207, 15.553]]" \
  -d "buffer_m=50"
```

**Example Response:**

```json
{
  "refined_boundary": {
    "type": "Feature",
    "geometry": {
      "type": "Polygon",
      "coordinates": [
        [
          [44.207, 15.552],
          [44.2081, 15.5521],
          [44.208, 15.5531],
          [44.2069, 15.553]
        ]
      ]
    },
    "properties": {
      "field_id": "field_refined_15552700_44207500",
      "area_hectares": 2.51,
      "perimeter_meters": 635.2,
      "centroid": [44.2075, 15.5526],
      "detection_confidence": 0.88,
      "method": "refined",
      "quality_score": 0.85
    }
  },
  "refinement_stats": {
    "initial_points": 4,
    "refined_points": 4,
    "area_hectares": 2.51,
    "perimeter_meters": 635.2,
    "confidence": 0.88,
    "quality_score": 0.85
  }
}
```

### 3. Detect Boundary Changes

```http
GET /v1/boundaries/{field_id}/changes
```

Detect changes in field boundary over time.

**Parameters:**

- `field_id` (required): Field identifier
- `since_date` (required): Compare to this date (ISO format)
- `previous_coords` (required): Previous boundary coordinates as JSON array

**Example Request:**

```bash
curl "http://localhost:8090/v1/boundaries/field_12345/changes?since_date=2023-07-01&previous_coords=[[44.207,15.552],[44.208,15.552],[44.208,15.553],[44.207,15.553]]"
```

**Example Response:**

```json
{
  "field_id": "field_12345",
  "change_analysis": {
    "change_type": "expansion",
    "change_percent": 15.2,
    "previous_area_hectares": 2.47,
    "current_area_hectares": 2.84,
    "area_change_hectares": 0.37,
    "boundary_shift_meters": 12.5,
    "confidence": 0.82
  },
  "affected_area": {
    "type": "MultiPoint",
    "coordinates": [
      [44.208, 15.553],
      [44.209, 15.553]
    ]
  },
  "interpretation": {
    "en": "Field has expanded by 15.2% (0.37 hectares)",
    "ar": "توسع الحقل بنسبة 15.2% (0.37 هكتار)"
  },
  "detection_date": "2024-01-15T00:00:00"
}
```

## Algorithm Details

### Detection Process

1. **Data Acquisition**
   - Fetch high-resolution NDVI imagery for the area
   - Resolution: 10m (Sentinel-2) or better
   - Cloud masking applied automatically

2. **Preprocessing**
   - Apply NDVI threshold (default: 0.25) to identify vegetated areas
   - Remove noise and small artifacts
   - Fill gaps in vegetated regions

3. **Edge Detection**
   - Calculate NDVI gradients using Sobel-like operators
   - Apply edge sensitivity threshold (default: 0.15)
   - Generate edge pixel map

4. **Contour Tracing**
   - Trace contours along edge pixels
   - Convert pixel coordinates to geographic coordinates (WGS84)
   - Close polygons and validate topology

5. **Filtering & Validation**
   - Filter by area (0.1 - 500 hectares)
   - Calculate quality metrics
   - Rank by detection confidence

6. **Simplification**
   - Apply Douglas-Peucker algorithm
   - Default tolerance: ~5 meters
   - Preserve shape while reducing complexity

### Geometric Calculations

#### Area (Shoelace Formula with Latitude Correction)

```python
# Meters per degree at latitude
lat_to_meters = 111,320 m
lon_to_meters = 111,320 * cos(latitude) m

# Convert to planar coordinates
coords_meters = [(lon * lon_to_meters, lat * lat_to_meters) for lon, lat in coords]

# Shoelace formula
area_m² = 0.5 * |Σ(x_i * y_(i+1) - x_(i+1) * y_i)|

# Convert to hectares
area_hectares = area_m² / 10,000
```

#### Perimeter (Haversine Distance)

```python
# For each pair of consecutive points
d = 2 * R * arcsin(√(sin²(Δlat/2) + cos(lat1) * cos(lat2) * sin²(Δlon/2)))

perimeter = Σ(distances)
```

Where R = 6,371,000 meters (Earth's radius)

#### Confidence Score

Based on:

- **Shape regularity** (isoperimetric quotient): 40%
- **Edge clarity** (NDVI gradient strength): 30%
- **Area appropriateness** (agricultural field size): 30%

```python
# Isoperimetric quotient (circle = 1.0)
quotient = 4π * area / perimeter²

# Confidence score
confidence = 0.4 * shape_score + 0.3 * edge_score + 0.3 * size_score
```

## Configuration

Default parameters can be adjusted:

```python
detector = FieldBoundaryDetector()

# Detection thresholds
detector.ndvi_threshold = 0.25      # Minimum NDVI for cultivated land
detector.edge_sensitivity = 0.15    # NDVI gradient threshold

# Area filters
detector.min_area_hectares = 0.1    # Minimum field size (1,000 m²)
detector.max_area_hectares = 500.0  # Maximum field size

# Simplification
detector.simplify_tolerance = 0.00005  # ~5m at equator

# Change detection
detector.stable_threshold = 0.05    # ±5% is considered stable
```

## Use Cases

### 1. Farmer Field Registration

Automatically detect and register farmer fields without manual digitization:

```python
# Farmer provides approximate location
boundaries = await detector.detect_boundary(
    latitude=15.5527,
    longitude=44.2075,
    radius_meters=500
)

# System presents detected boundaries for confirmation
# Farmer selects their field(s)
```

### 2. Field Monitoring

Track changes in field boundaries over growing seasons:

```python
# Detect changes from last season
change = await detector.detect_boundary_change(
    field_id="field_12345",
    previous_coords=last_season_coords,
    current_date=datetime.now()
)

if change.change_type == "expansion":
    # Field expanded - possible land clearing
    # Send notification or alert
elif change.change_type == "contraction":
    # Field contracted - possible abandonment or erosion
    # Flag for investigation
```

### 3. Cadastral Mapping

Generate agricultural cadastre from satellite imagery:

```python
# Scan large area in grid
for lat, lon in grid_points:
    boundaries = await detector.detect_boundary(
        latitude=lat,
        longitude=lon,
        radius_meters=1000
    )
    # Store boundaries in database
    # Build regional field map
```

### 4. Precision Agriculture

Define management zones within fields:

```python
# Refine farmer-drawn boundary
refined = await detector.refine_boundary(
    initial_coords=farmer_drawn_coords,
    buffer_meters=50
)

# Use refined boundary for:
# - Variable rate application
# - Yield zone mapping
# - Irrigation planning
```

## Integration Examples

### Python Integration

```python
from satellite_service.field_boundary_detector import FieldBoundaryDetector

# Initialize detector
detector = FieldBoundaryDetector()

# Detect boundaries
boundaries = await detector.detect_boundary(
    latitude=15.5527,
    longitude=44.2075,
    radius_meters=500
)

# Export as GeoJSON
for boundary in boundaries:
    geojson = boundary.to_geojson()
    print(f"Field {geojson['properties']['field_id']}: "
          f"{geojson['properties']['area_hectares']} hectares")
```

### JavaScript/TypeScript Integration

```typescript
// Call API endpoint
const response = await fetch(
  "http://localhost:8090/v1/boundaries/detect?" +
    new URLSearchParams({
      lat: "15.5527",
      lon: "44.2075",
      radius_m: "500",
    }),
  { method: "POST" },
);

const data = await response.json();

// Display on map (Leaflet example)
const geoJsonLayer = L.geoJSON(data, {
  onEachFeature: (feature, layer) => {
    const props = feature.properties;
    layer.bindPopup(`
      <b>Field ${props.field_id}</b><br>
      Area: ${props.area_hectares} ha<br>
      Confidence: ${props.detection_confidence}
    `);
  },
}).addTo(map);
```

## Performance

### Detection Speed

- **Small area** (< 1 km²): ~2-5 seconds
- **Medium area** (1-10 km²): ~5-15 seconds
- **Large area** (> 10 km²): ~15-30 seconds

_Times vary based on satellite data availability and processing complexity_

### Accuracy

- **Position accuracy**: ±10-20 meters (limited by satellite resolution)
- **Area accuracy**: ±5-10% (depending on field size and shape)
- **Detection rate**: ~85-95% (varies by crop type and season)

### Limitations

1. **Cloud cover**: Detection fails when cloud coverage > 30%
2. **Small fields**: Fields < 0.1 hectares may not be detected
3. **Irregular shapes**: Very irregular fields may have lower confidence
4. **Bare soil**: Non-vegetated fields require different detection methods
5. **Mixed vegetation**: Tree-crop systems may need manual adjustment

## Troubleshooting

### No Boundaries Detected

**Possible causes:**

- No agricultural fields in search area
- Cloud coverage too high
- Fields too small (< 0.1 hectares)
- Season with no active vegetation

**Solutions:**

- Increase search radius
- Try different date (different season)
- Lower `ndvi_threshold` parameter
- Use manual boundary refinement instead

### Low Confidence Scores

**Possible causes:**

- Irregular field shapes
- Mixed vegetation (trees + crops)
- Edge degradation or overlap with natural vegetation
- Partial cloud coverage

**Solutions:**

- Use boundary refinement to improve accuracy
- Manually adjust boundaries
- Try different date with clearer imagery

### Boundary Shift in Change Detection

**Possible causes:**

- Different satellite sensors/resolutions
- Seasonal vegetation changes
- Actual boundary changes (intended)

**Solutions:**

- Use same satellite source for comparison
- Account for seasonal variations
- Set higher `stable_threshold` for tolerance

## Future Enhancements

Planned features for future versions:

1. **Multi-spectral segmentation** - Use all bands, not just NDVI
2. **Machine learning boundaries** - Train CNN for better accuracy
3. **Temporal smoothing** - Use time series to reduce noise
4. **Crop type integration** - Different thresholds per crop
5. **Terrain correction** - Account for slopes and elevation
6. **Automated validation** - Compare with ground truth data
7. **Batch processing** - Process large regions efficiently
8. **Mobile app integration** - Field verification on smartphones

## References

### Scientific Literature

1. Watkins, B. & van Niekerk, A. (2019). "A comparison of object-based image analysis approaches for field boundary delineation using multi-temporal Sentinel-2 imagery." _Computers and Electronics in Agriculture_, 158, 294-302.

2. Graesser, J. & Ramankutty, N. (2017). "Detection of cropland field parcels from Landsat imagery." _Remote Sensing of Environment_, 201, 165-180.

3. Persello, C. et al. (2019). "Delineation of agricultural fields in smallholder farms from satellite images using fully convolutional networks and combinatorial grouping." _Remote Sensing of Environment_, 231, 111253.

### Technical Resources

- [Sentinel-2 User Guide](https://sentinel.esa.int/web/sentinel/user-guides/sentinel-2-msi)
- [Douglas-Peucker Algorithm](https://en.wikipedia.org/wiki/Ramer%E2%80%93Douglas%E2%80%93Peucker_algorithm)
- [Haversine Formula](https://en.wikipedia.org/wiki/Haversine_formula)
- [Shoelace Formula](https://en.wikipedia.org/wiki/Shoelace_formula)

## License

Part of the SAHOOL Unified Agricultural Platform v15
Copyright © 2025

---

**Support:** For questions or issues, contact the SAHOOL development team.

**Documentation Version:** 1.0.0
**Last Updated:** December 2025
