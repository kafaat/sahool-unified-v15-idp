# SAHOOL Satellite Service - Data Export API

## Overview

The SAHOOL Satellite Service now includes comprehensive data export functionality, allowing you to export satellite analysis data in multiple formats for integration with GIS systems, reporting tools, and data analysis platforms.

## Supported Formats

- **GeoJSON** (`geojson`): Standard geographic data format, ideal for web mapping and GIS
- **CSV** (`csv`): Tabular format for spreadsheets and data analysis
- **JSON** (`json`): Complete structured data format
- **KML** (`kml`): Google Earth and mapping applications

## API Endpoints

### 1. Export Field Analysis

Export comprehensive field analysis including vegetation indices, health scores, and recommendations.

**Endpoint:** `GET /v1/export/analysis/{field_id}`

**Parameters:**
- `field_id` (path): Field identifier
- `lat` (query, required): Latitude (-90 to 90)
- `lon` (query, required): Longitude (-180 to 180)
- `format` (query, optional): Export format - `geojson`, `csv`, `json`, `kml` (default: `geojson`)

**Example Request:**
```bash
curl "http://localhost:8090/v1/export/analysis/FIELD_001?lat=15.3694&lon=44.1910&format=geojson" \
  -o field_analysis.geojson
```

**Response:**
- Stream download with appropriate Content-Type
- Headers include:
  - `Content-Disposition`: attachment filename
  - `X-Export-Size`: file size in bytes
  - `X-Generated-At`: timestamp

**Use Cases:**
- Export current field health status
- Generate reports for stakeholders
- Import into GIS systems for visualization
- Archive historical analysis data

---

### 2. Export Time Series

Export vegetation index trends over time (NDVI, EVI, etc.).

**Endpoint:** `GET /v1/export/timeseries/{field_id}`

**Parameters:**
- `field_id` (path): Field identifier
- `lat` (query, required): Latitude
- `lon` (query, required): Longitude
- `start_date` (query, required): Start date (YYYY-MM-DD)
- `end_date` (query, required): End date (YYYY-MM-DD)
- `format` (query, optional): `csv`, `json`, `geojson` (default: `csv`)

**Example Request:**
```bash
curl "http://localhost:8090/v1/export/timeseries/FIELD_001?lat=15.3694&lon=44.1910&start_date=2023-11-01&end_date=2023-12-15&format=csv" \
  -o timeseries.csv
```

**CSV Output Example:**
```csv
date,latitude,longitude,ndvi,ndwi,evi,health_score,health_status,cloud_cover
2023-11-01,15.3694,44.1910,0.65,0.40,0.58,75.0,good,8.5
2023-11-08,15.3694,44.1910,0.70,0.42,0.63,80.0,excellent,5.2
2023-11-15,15.3694,44.1910,0.75,0.45,0.68,85.0,excellent,3.1
```

**Use Cases:**
- Track vegetation health trends
- Analyze seasonal patterns
- Create charts and graphs
- Detect anomalies over time

---

### 3. Export Field Boundaries

Export field boundaries for multiple fields in GIS-compatible formats.

**Endpoint:** `GET /v1/export/boundaries`

**Parameters:**
- `field_ids` (query, required): Comma-separated field IDs (max 100)
- `format` (query, optional): `geojson`, `json`, `kml` (default: `geojson`)

**Example Request:**
```bash
curl "http://localhost:8090/v1/export/boundaries?field_ids=FIELD_001,FIELD_002,FIELD_003&format=geojson" \
  -o boundaries.geojson
```

**GeoJSON Output Example:**
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[44.0, 15.0], [44.01, 15.0], ...]]
      },
      "properties": {
        "field_id": "FIELD_001",
        "name": "Main Wheat Field",
        "area_hectares": 5.2
      }
    }
  ]
}
```

**Use Cases:**
- Import field boundaries into GIS software
- Visualize fields in Google Earth (KML)
- Create farm maps
- Share field locations with teams

---

### 4. Export Comprehensive Report

Export detailed field reports with various report types.

**Endpoint:** `GET /v1/export/report/{field_id}`

**Parameters:**
- `field_id` (path): Field identifier
- `lat` (query, required): Latitude
- `lon` (query, required): Longitude
- `report_type` (query, optional): `full`, `summary`, `changes` (default: `full`)
- `format` (query, optional): `json`, `csv`, `geojson` (default: `json`)

**Report Types:**
- **full**: Complete analysis with all indices and recommendations
- **summary**: High-level health metrics only
- **changes**: Change detection comparing current vs. 7 days ago

**Example Request (Full Report):**
```bash
curl "http://localhost:8090/v1/export/report/FIELD_001?lat=15.3694&lon=44.1910&report_type=full&format=json" \
  -o full_report.json
```

**Example Request (Changes Report):**
```bash
curl "http://localhost:8090/v1/export/report/FIELD_001?lat=15.3694&lon=44.1910&report_type=changes&format=csv" \
  -o changes_report.csv
```

**Use Cases:**
- Generate weekly/monthly reports
- Track changes and trends
- Share analysis with agronomists
- Create executive summaries

---

## Python Client Examples

### Export Field Analysis

```python
import requests

def export_field_analysis(field_id, lat, lon, format='geojson'):
    """Export field analysis to file"""
    url = f"http://localhost:8090/v1/export/analysis/{field_id}"
    params = {
        'lat': lat,
        'lon': lon,
        'format': format
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        # Get filename from header
        filename = response.headers.get('Content-Disposition', '').split('filename=')[1].strip('"')

        # Save to file
        with open(filename, 'wb') as f:
            f.write(response.content)

        print(f"Exported: {filename}")
        print(f"Size: {response.headers.get('X-Export-Size')} bytes")
        return filename
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

# Usage
export_field_analysis("FIELD_001", 15.3694, 44.1910, format='geojson')
```

### Export Time Series to Pandas DataFrame

```python
import requests
import pandas as pd
from io import StringIO

def export_timeseries_to_dataframe(field_id, lat, lon, start_date, end_date):
    """Export timeseries and load into pandas DataFrame"""
    url = f"http://localhost:8090/v1/export/timeseries/{field_id}"
    params = {
        'lat': lat,
        'lon': lon,
        'start_date': start_date,
        'end_date': end_date,
        'format': 'csv'
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        # Load CSV into DataFrame
        df = pd.read_csv(StringIO(response.text))
        df['date'] = pd.to_datetime(df['date'])
        return df
    else:
        print(f"Error: {response.status_code}")
        return None

# Usage
df = export_timeseries_to_dataframe(
    "FIELD_001",
    15.3694,
    44.1910,
    "2023-11-01",
    "2023-12-15"
)

# Analyze trends
print(df.describe())
print(df[['date', 'ndvi', 'health_score']].head())

# Plot
import matplotlib.pyplot as plt
df.plot(x='date', y='ndvi', title='NDVI Over Time')
plt.show()
```

### Batch Export Multiple Fields

```python
import requests
import concurrent.futures

def export_field(field_data):
    """Export single field analysis"""
    field_id, lat, lon = field_data
    url = f"http://localhost:8090/v1/export/analysis/{field_id}"
    params = {'lat': lat, 'lon': lon, 'format': 'geojson'}

    response = requests.get(url, params=params)
    if response.status_code == 200:
        filename = f"{field_id}_analysis.geojson"
        with open(filename, 'wb') as f:
            f.write(response.content)
        return field_id, True
    return field_id, False

# List of fields to export
fields = [
    ("FIELD_001", 15.3694, 44.1910),
    ("FIELD_002", 15.3695, 44.1915),
    ("FIELD_003", 15.3696, 44.1920),
]

# Export in parallel
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    results = executor.map(export_field, fields)

for field_id, success in results:
    print(f"{field_id}: {'✓' if success else '✗'}")
```

---

## Integration Examples

### QGIS Integration

1. Export field boundaries as GeoJSON:
```bash
curl "http://localhost:8090/v1/export/boundaries?field_ids=FIELD_001,FIELD_002&format=geojson" -o fields.geojson
```

2. In QGIS:
   - Layer → Add Layer → Add Vector Layer
   - Select the exported GeoJSON file
   - Style and analyze as needed

### Google Earth Integration

1. Export as KML:
```bash
curl "http://localhost:8090/v1/export/analysis/FIELD_001?lat=15.3694&lon=44.1910&format=kml" -o field.kml
```

2. Open the KML file in Google Earth to visualize field location and analysis data

### Excel/Spreadsheet Analysis

1. Export timeseries as CSV:
```bash
curl "http://localhost:8090/v1/export/timeseries/FIELD_001?lat=15.3694&lon=44.1910&start_date=2023-11-01&end_date=2023-12-15&format=csv" -o timeseries.csv
```

2. Open in Excel and create charts, pivot tables, etc.

---

## Response Headers

All export endpoints include these custom headers:

- **Content-Disposition**: `attachment; filename="sahool_..."` - suggested filename
- **X-Export-Size**: File size in bytes
- **X-Generated-At**: ISO 8601 timestamp of generation
- **X-Data-Points** (timeseries): Number of data points
- **X-Field-Count** (boundaries): Number of fields
- **X-Report-Type** (report): Type of report generated

---

## Error Handling

### Common Error Codes

- **400 Bad Request**: Invalid parameters (format, dates, coordinates)
- **404 Not Found**: Field not found
- **500 Internal Server Error**: Export processing failed

### Example Error Response

```json
{
  "detail": "Invalid format 'xyz'. Supported: geojson, csv, json, kml"
}
```

---

## Performance Considerations

1. **Time Series**: Long date ranges generate more data points. Use weekly intervals for better performance.
2. **Boundaries**: Maximum 100 fields per export request.
3. **Large Exports**: Use streaming to handle large files efficiently.

---

## File Naming Convention

All exported files follow this pattern:
```
sahool_{type}_{field_id}_{timestamp}.{extension}
```

Examples:
- `sahool_field_analysis_FIELD_001_20231215_143022.geojson`
- `sahool_timeseries_FIELD_002_20231215_143045.csv`
- `sahool_boundaries_multi_20231215_143100.kml`

---

## Next Steps

1. Test the endpoints with your data
2. Integrate with your GIS or analysis tools
3. Automate exports for regular reporting
4. Build dashboards using the exported data

For questions or issues, contact the SAHOOL development team.
