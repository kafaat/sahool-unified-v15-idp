# Field Boundary Detection - Quick Start Guide
# دليل البدء السريع - كشف حدود الحقول

Quick reference for using the Field Boundary Detection API.

## 🚀 Quick Start

### Start the Service

```bash
cd /home/user/sahool-unified-v15-idp/apps/services/satellite-service
python -m src.main
```

The service will start on `http://localhost:8090`

### Run Examples

```bash
python examples/boundary_detection_example.py
```

## 📍 API Endpoints

### 1. Detect Boundaries

**Endpoint:** `POST /v1/boundaries/detect`

**Simplest Request:**
```bash
curl -X POST "http://localhost:8090/v1/boundaries/detect?lat=15.5527&lon=44.2075"
```

**With All Options:**
```bash
curl -X POST "http://localhost:8090/v1/boundaries/detect?lat=15.5527&lon=44.2075&radius_m=500&date=2024-01-15"
```

**Python:**
```python
import httpx

async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8090/v1/boundaries/detect",
        params={"lat": 15.5527, "lon": 44.2075, "radius_m": 500}
    )
    boundaries = response.json()
```

**Response:**
```json
{
  "type": "FeatureCollection",
  "features": [...],
  "metadata": {
    "fields_detected": 3,
    "total_area_hectares": 12.5
  }
}
```

---

### 2. Refine Boundary

**Endpoint:** `POST /v1/boundaries/refine`

**Request:**
```bash
curl -X POST "http://localhost:8090/v1/boundaries/refine" \
  -d "coords=[[44.207, 15.552], [44.208, 15.552], [44.208, 15.553], [44.207, 15.553]]" \
  -d "buffer_m=50"
```

**Python:**
```python
coords = [[44.207, 15.552], [44.208, 15.552], [44.208, 15.553], [44.207, 15.553]]

async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8090/v1/boundaries/refine",
        params={"coords": json.dumps(coords), "buffer_m": 50}
    )
    refined = response.json()
```

**Response:**
```json
{
  "refined_boundary": {...},
  "refinement_stats": {
    "area_hectares": 2.51,
    "confidence": 0.88
  }
}
```

---

### 3. Detect Changes

**Endpoint:** `GET /v1/boundaries/{field_id}/changes`

**Request:**
```bash
curl "http://localhost:8090/v1/boundaries/field_12345/changes?since_date=2023-07-01&previous_coords=[[44.207,15.552],[44.208,15.552],[44.208,15.553],[44.207,15.553]]"
```

**Python:**
```python
previous = [[44.207, 15.552], [44.208, 15.552], [44.208, 15.553], [44.207, 15.553]]

async with httpx.AsyncClient() as client:
    response = await client.get(
        "http://localhost:8090/v1/boundaries/field_12345/changes",
        params={
            "since_date": "2023-07-01",
            "previous_coords": json.dumps(previous)
        }
    )
    changes = response.json()
```

**Response:**
```json
{
  "change_analysis": {
    "change_type": "expansion",
    "change_percent": 15.2,
    "area_change_hectares": 0.37
  },
  "interpretation": {
    "en": "Field has expanded by 15.2% (0.37 hectares)",
    "ar": "توسع الحقل بنسبة 15.2% (0.37 هكتار)"
  }
}
```

---

## 🌍 Common Locations in Yemen

```python
# Sana'a (Highland)
lat, lon = 15.5527, 44.2075

# Aden (Coastal)
lat, lon = 12.7855, 45.0187

# Taiz (Highland)
lat, lon = 13.5796, 44.0194

# Hodeidah (Coastal)
lat, lon = 14.7978, 42.9545
```

---

## 📊 Response Fields

### FieldBoundary Properties
```json
{
  "field_id": "unique identifier",
  "area_hectares": 2.47,
  "perimeter_meters": 628.5,
  "centroid": [44.207, 15.552],
  "detection_confidence": 0.85,      // 0-1 (higher is better)
  "quality_score": 0.80,             // 0-1 (shape regularity)
  "mean_ndvi": 0.65,                 // 0-1 (vegetation health)
  "method": "ndvi_edge"              // detection method used
}
```

### Change Types
- `"stable"` - No significant change (< 5%)
- `"expansion"` - Field has grown
- `"contraction"` - Field has shrunk

---

## ⚙️ Configuration

Adjust detection parameters in code:

```python
from src.field_boundary_detector import FieldBoundaryDetector

detector = FieldBoundaryDetector()

# Sensitivity
detector.ndvi_threshold = 0.25      # Lower = more sensitive
detector.edge_sensitivity = 0.15    # Lower = more edges detected

# Size filters
detector.min_area_hectares = 0.1    # Minimum field size
detector.max_area_hectares = 500.0  # Maximum field size

# Simplification
detector.simplify_tolerance = 0.00005  # Lower = more detail
```

---

## 🎯 Use Case Examples

### 1. Farmer Field Registration
```python
# Farmer provides location
boundaries = await detect_boundary(lat=15.5527, lon=44.2075)

# Show detected fields to farmer
for boundary in boundaries:
    print(f"Field: {boundary.area_hectares} hectares")

# Farmer selects their field
selected = boundaries[0]
```

### 2. Monitor Field Expansion
```python
# Check if field has expanded
change = await detect_boundary_change(
    field_id="field_123",
    previous_coords=last_year_coords,
    current_date=datetime.now()
)

if change.change_type == "expansion":
    print(f"Field expanded by {change.area_change_hectares} hectares")
```

### 3. Improve Hand-Drawn Boundary
```python
# User draws rough boundary on map
user_drawn = [[44.207, 15.552], [44.208, 15.553], ...]

# Refine to match satellite imagery
refined = await refine_boundary(coords=user_drawn)
print(f"Refined to {refined.area_hectares} hectares")
```

---

## 🧪 Testing

Run unit tests:
```bash
pytest tests/test_boundary_detector.py -v
```

Run all examples:
```bash
python examples/boundary_detection_example.py
```

---

## 🐛 Troubleshooting

### Service won't start
```bash
# Check if port 8090 is available
lsof -i :8090

# Install dependencies
pip install -r requirements.txt
```

### No boundaries detected
- Increase `radius_m` parameter
- Try different date (better weather/season)
- Lower detection thresholds
- Check if location has agricultural fields

### Low confidence scores
- Use boundary refinement
- Try different satellite imagery date
- Manually adjust boundaries

---

## 📚 Full Documentation

See [FIELD_BOUNDARY_DETECTION.md](FIELD_BOUNDARY_DETECTION.md) for complete documentation.

---

## 🔗 Related Endpoints

- `/v1/analyze` - Get NDVI and field health
- `/v1/phenology/{field_id}` - Get crop growth stage
- `/v1/soil-moisture/{field_id}` - Get soil moisture (SAR)
- `/v1/yield-prediction` - Predict crop yield

---

**Version:** 1.0.0
**Updated:** December 2025
**Part of:** SAHOOL Unified Agricultural Platform v15
