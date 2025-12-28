# SAHOOL Data Export - Quick Reference

## Quick Start

```bash
# Start the service
python src/main.py

# Run tests
python test_export.py
```

## API Endpoints

### 1. Export Analysis
```bash
GET /v1/export/analysis/{field_id}?lat={lat}&lon={lon}&format={format}
```
**Formats:** geojson, csv, json, kml

**Example:**
```bash
curl "http://localhost:8090/v1/export/analysis/FIELD_001?lat=15.3694&lon=44.1910&format=geojson" -o analysis.geojson
```

---

### 2. Export Timeseries
```bash
GET /v1/export/timeseries/{field_id}?lat={lat}&lon={lon}&start_date={date}&end_date={date}&format={format}
```
**Formats:** csv, json, geojson

**Example:**
```bash
curl "http://localhost:8090/v1/export/timeseries/FIELD_001?lat=15.3694&lon=44.1910&start_date=2023-11-01&end_date=2023-12-15&format=csv" -o timeseries.csv
```

---

### 3. Export Boundaries
```bash
GET /v1/export/boundaries?field_ids={ids}&format={format}
```
**Formats:** geojson, json, kml

**Example:**
```bash
curl "http://localhost:8090/v1/export/boundaries?field_ids=FIELD_001,FIELD_002&format=kml" -o boundaries.kml
```

---

### 4. Export Report
```bash
GET /v1/export/report/{field_id}?lat={lat}&lon={lon}&report_type={type}&format={format}
```
**Report Types:** full, summary, changes
**Formats:** json, csv, geojson

**Example:**
```bash
curl "http://localhost:8090/v1/export/report/FIELD_001?lat=15.3694&lon=44.1910&report_type=changes&format=json" -o report.json
```

---

## Python Usage

```python
import requests

# Export analysis
response = requests.get(
    "http://localhost:8090/v1/export/analysis/FIELD_001",
    params={"lat": 15.3694, "lon": 44.1910, "format": "geojson"}
)

# Save to file
with open("analysis.geojson", "wb") as f:
    f.write(response.content)

# Load to pandas
import pandas as pd
from io import StringIO

response = requests.get(
    "http://localhost:8090/v1/export/timeseries/FIELD_001",
    params={
        "lat": 15.3694,
        "lon": 44.1910,
        "start_date": "2023-11-01",
        "end_date": "2023-12-15",
        "format": "csv"
    }
)

df = pd.read_csv(StringIO(response.text))
```

---

## Format Guide

| Format  | Best For              | File Size | Use Case                    |
|---------|----------------------|-----------|----------------------------|
| GeoJSON | Web mapping, GIS     | Medium    | Leaflet, QGIS              |
| CSV     | Data analysis        | Small     | Excel, pandas, R           |
| JSON    | API integration      | Medium    | Dashboards, apps           |
| KML     | Google Earth         | Large     | Visualization              |

---

## Response Headers

All exports include:
- `Content-Disposition`: Filename
- `X-Export-Size`: File size (bytes)
- `X-Generated-At`: Timestamp
- `X-Data-Points`: Count (timeseries)
- `X-Field-Count`: Count (boundaries)
- `X-Report-Type`: Type (report)

---

## Error Codes

- **400**: Invalid format/parameters
- **404**: Field not found
- **500**: Export failed

---

## File Naming

Pattern: `sahool_{type}_{field_id}_{timestamp}.{ext}`

Example: `sahool_field_analysis_FIELD_001_20231215_143022.geojson`

---

## Integration

### QGIS
1. Export as GeoJSON
2. Layer → Add Vector Layer → Select file

### Google Earth
1. Export as KML
2. File → Open → Select KML

### Excel
1. Export as CSV
2. Open in Excel

### Python/pandas
```python
df = pd.read_csv("timeseries.csv")
df.plot(x='date', y='ndvi')
```

---

## Limits

- Boundaries: Max 100 fields
- Timeseries: Max 365 days
- All: Streaming prevents memory issues

---

## Documentation

- **EXPORT_API_USAGE.md** - Full API docs
- **EXPORT_FEATURE_README.md** - Feature overview
- **EXPORT_ARCHITECTURE.md** - System design
- **IMPLEMENTATION_SUMMARY.txt** - Complete summary

---

## Testing

```bash
# Unit tests
python test_export.py

# Integration tests (requires service running)
python test_export_api.py
```

---

## Support

For issues or questions, see full documentation in `EXPORT_API_USAGE.md`
