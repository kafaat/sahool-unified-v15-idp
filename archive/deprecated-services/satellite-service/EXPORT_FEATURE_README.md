# SAHOOL Satellite Service - Data Export Feature

## Overview

Comprehensive data export functionality has been added to the SAHOOL Satellite Service, enabling users to export satellite analysis data in multiple formats for integration with GIS systems, reporting tools, and data analysis platforms.

## What's New

### 1. Core Export Module (`src/data_exporter.py`)

A complete data export module with support for:

- **GeoJSON**: Standard geographic format for web mapping and GIS
- **CSV**: Tabular format for spreadsheets and analysis
- **JSON**: Complete structured data format
- **KML**: Google Earth and mapping applications

Key classes:

- `ExportFormat`: Enum defining supported formats
- `ExportResult`: Dataclass containing export metadata and data
- `DataExporter`: Main class with export methods for all data types

### 2. API Endpoints (added to `src/main.py`)

Four new REST API endpoints:

#### `/v1/export/analysis/{field_id}`

Export field analysis with vegetation indices, health scores, and recommendations.

- Formats: GeoJSON, CSV, JSON, KML
- Use case: Current field health status, GIS visualization

#### `/v1/export/timeseries/{field_id}`

Export time series data showing vegetation trends over time.

- Formats: CSV, JSON, GeoJSON
- Use case: Trend analysis, charting, anomaly detection

#### `/v1/export/boundaries`

Export field boundaries for multiple fields.

- Formats: GeoJSON, JSON, KML
- Use case: GIS mapping, Google Earth visualization

#### `/v1/export/report/{field_id}`

Export comprehensive reports with three report types:

- **full**: Complete analysis with all data
- **summary**: High-level health metrics
- **changes**: Change detection vs. 7 days ago
- Formats: JSON, CSV, GeoJSON
- Use case: Executive reporting, change tracking

### 3. Features

- **Streaming Responses**: Efficient handling of large files
- **Automatic Filename Generation**: Timestamped, descriptive filenames
- **Rich Metadata**: Custom headers with export info
- **Date Range Filtering**: For timeseries exports
- **Multi-field Export**: Export up to 100 fields at once
- **Flattened CSV Output**: Nested data converted to flat tables
- **Error Handling**: Comprehensive validation and error messages

## File Structure

```
satellite-service/
├── src/
│   ├── data_exporter.py          # Core export module (NEW)
│   ├── main.py                    # Updated with export endpoints
│   └── export_endpoints.py        # Reference implementation
├── test_export.py                 # Unit tests for DataExporter (NEW)
├── test_export_api.py            # Integration tests for API (NEW)
├── EXPORT_API_USAGE.md           # API documentation (NEW)
└── EXPORT_FEATURE_README.md      # This file (NEW)
```

## Quick Start

### 1. Start the Service

```bash
cd /home/user/sahool-unified-v15-idp/apps/services/satellite-service
python src/main.py
```

### 2. Test the Export Module

```bash
# Run unit tests
python test_export.py

# Run API integration tests (requires service running)
python test_export_api.py
```

### 3. Try the API

```bash
# Export field analysis as GeoJSON
curl "http://localhost:8090/v1/export/analysis/FIELD_001?lat=15.3694&lon=44.1910&format=geojson" \
  -o field_analysis.geojson

# Export timeseries as CSV
curl "http://localhost:8090/v1/export/timeseries/FIELD_001?lat=15.3694&lon=44.1910&start_date=2023-11-01&end_date=2023-12-15&format=csv" \
  -o timeseries.csv

# Export boundaries as KML for Google Earth
curl "http://localhost:8090/v1/export/boundaries?field_ids=FIELD_001,FIELD_002&format=kml" \
  -o boundaries.kml

# Export change detection report
curl "http://localhost:8090/v1/export/report/FIELD_001?lat=15.3694&lon=44.1910&report_type=changes&format=json" \
  -o changes.json
```

## Implementation Details

### DataExporter Class Methods

1. **`export_field_analysis(field_id, analysis_data, format)`**
   - Exports complete field analysis
   - Supports all formats
   - Flattens nested data for CSV

2. **`export_timeseries(field_id, timeseries_data, format)`**
   - Exports time series points
   - Creates FeatureCollection for GeoJSON
   - Optimized CSV output

3. **`export_boundaries(boundaries, format)`**
   - Exports multiple field boundaries
   - GeoJSON FeatureCollection
   - KML with polygon support

4. **`export_yield_prediction(prediction_data, format)`**
   - Exports yield predictions
   - Flattens complex prediction models

5. **`export_changes_report(changes, format)`**
   - Exports change detection results
   - Supports spatial and temporal changes

### Helper Methods

- `_to_geojson()`: Convert data to GeoJSON format
- `_to_csv()`: Convert to CSV with flattening
- `_to_kml()`: Convert to KML for Google Earth
- `_boundaries_to_kml()`: Convert multiple boundaries to KML
- `_flatten_dict()`: Recursively flatten nested dictionaries
- `_flatten_analysis_for_csv()`: Optimize analysis data for CSV
- `generate_filename()`: Generate timestamped filenames

### Filename Convention

All files follow this pattern:

```
sahool_{type}_{field_id}_{timestamp}.{extension}
```

Example:

```
sahool_field_analysis_FIELD_001_20231215_143022.geojson
```

## Testing

### Unit Tests (`test_export.py`)

Tests all DataExporter methods with sample data:

- ✓ Field analysis export (all formats)
- ✓ Time series export
- ✓ Boundaries export
- ✓ Yield prediction export
- ✓ Changes report export
- ✓ Filename generation

Run: `python test_export.py`

### Integration Tests (`test_export_api.py`)

Tests all API endpoints:

- ✓ Export analysis endpoint (all formats)
- ✓ Export timeseries endpoint
- ✓ Export boundaries endpoint
- ✓ Export report endpoint (all types)
- ✓ Error handling

Run: `python test_export_api.py` (requires service running)

## Use Cases

### 1. GIS Integration

Export field boundaries and analysis as GeoJSON/KML for QGIS, ArcGIS, or Google Earth.

### 2. Data Analysis

Export timeseries as CSV for analysis in Excel, Python (pandas), or R.

### 3. Reporting

Generate JSON or CSV reports for dashboards and executive summaries.

### 4. Change Detection

Track vegetation health changes over time with change reports.

### 5. Multi-field Analysis

Export data for multiple fields simultaneously for farm-level analysis.

## Response Headers

All export endpoints include:

- `Content-Disposition`: Suggested filename
- `X-Export-Size`: File size in bytes
- `X-Generated-At`: Generation timestamp
- `X-Data-Points`: Number of data points (timeseries)
- `X-Field-Count`: Number of fields (boundaries)
- `X-Report-Type`: Report type (report endpoint)

## Error Handling

Common errors:

- **400**: Invalid format, dates, or parameters
- **404**: Field not found
- **500**: Export processing failed

All errors return JSON with `detail` field explaining the issue.

## Performance

- **Streaming**: Large files streamed efficiently
- **Timeseries**: Weekly intervals recommended for long date ranges
- **Boundaries**: Max 100 fields per request
- **Caching**: Leverages existing Redis cache for analysis data

## Examples

See `EXPORT_API_USAGE.md` for detailed examples including:

- Python client code
- pandas DataFrame integration
- Batch export scripts
- GIS integration guides

## Dependencies

No new dependencies required. Uses standard library:

- `json`: JSON formatting
- `csv`: CSV generation
- `xml`: KML/XML generation
- `io`: String/byte stream handling
- `datetime`: Timestamp generation

## Future Enhancements

Potential additions:

- Shapefile export
- GeoTIFF export for raster data
- PDF report generation
- Compressed archive support (ZIP)
- Email export capability
- Scheduled exports
- Custom export templates

## Support

For questions or issues:

1. Check `EXPORT_API_USAGE.md` for API documentation
2. Run tests to verify functionality
3. Check logs for error details
4. Contact SAHOOL development team

## License

Part of the SAHOOL Unified Platform v15 IDP
