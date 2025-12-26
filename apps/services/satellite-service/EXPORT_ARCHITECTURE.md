# SAHOOL Data Export Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     SAHOOL Satellite Service                    │
│                         with Data Export                        │
└─────────────────────────────────────────────────────────────────┘

┌─────────────┐      ┌──────────────┐      ┌────────────────┐
│   Clients   │      │  API Layer   │      │  Export Layer  │
└─────────────┘      └──────────────┘      └────────────────┘
      │                     │                      │
      │                     │                      │
      ▼                     ▼                      ▼

┌─────────────────────────────────────────────────────────────────┐
│                        Request Flow                             │
└─────────────────────────────────────────────────────────────────┘

1. Client Request
   │
   ├─► GET /v1/export/analysis/{field_id}
   ├─► GET /v1/export/timeseries/{field_id}
   ├─► GET /v1/export/boundaries
   └─► GET /v1/export/report/{field_id}
         │
         ▼
2. API Endpoint Handler
   │
   ├─► Validate parameters
   ├─► Perform analysis (if needed)
   └─► Call DataExporter
         │
         ▼
3. DataExporter
   │
   ├─► Format conversion
   │   ├─► _to_geojson()
   │   ├─► _to_csv()
   │   ├─► _to_kml()
   │   └─► JSON (native)
   │
   ├─► Data flattening (for CSV)
   │   ├─► _flatten_dict()
   │   ├─► _flatten_analysis_for_csv()
   │   └─► _flatten_prediction_for_csv()
   │
   └─► Generate ExportResult
         │
         ▼
4. StreamingResponse
   │
   ├─► Set Content-Type
   ├─► Set Content-Disposition
   ├─► Add custom headers
   └─► Stream data to client
```

## Component Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                          src/main.py                               │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │              Export API Endpoints                        │    │
│  ├──────────────────────────────────────────────────────────┤    │
│  │                                                          │    │
│  │  • export_analysis(field_id, lat, lon, format)          │    │
│  │  • export_timeseries(field_id, lat, lon, dates, format) │    │
│  │  • export_boundaries(field_ids, format)                 │    │
│  │  • export_report(field_id, lat, lon, type, format)      │    │
│  │                                                          │    │
│  └──────────────────────────────────────────────────────────┘    │
│                           │                                        │
│                           ▼                                        │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │            Helper Function                               │    │
│  ├──────────────────────────────────────────────────────────┤    │
│  │                                                          │    │
│  │  • _perform_analysis(field_id, lat, lon, date)          │    │
│  │    └─► Uses multi-provider or simulated data            │    │
│  │                                                          │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────┐
│                     src/data_exporter.py                           │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │              Data Models                                 │    │
│  ├──────────────────────────────────────────────────────────┤    │
│  │  • ExportFormat (Enum)                                   │    │
│  │  • ExportResult (Dataclass)                              │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │              DataExporter Class                          │    │
│  ├──────────────────────────────────────────────────────────┤    │
│  │                                                          │    │
│  │  Export Methods:                                         │    │
│  │  ├─► export_field_analysis()                            │    │
│  │  ├─► export_timeseries()                                │    │
│  │  ├─► export_boundaries()                                │    │
│  │  ├─► export_yield_prediction()                          │    │
│  │  └─► export_changes_report()                            │    │
│  │                                                          │    │
│  │  Conversion Methods:                                     │    │
│  │  ├─► _to_geojson()                                      │    │
│  │  ├─► _to_csv()                                          │    │
│  │  ├─► _to_kml()                                          │    │
│  │  └─► _boundaries_to_kml()                               │    │
│  │                                                          │    │
│  │  Helper Methods:                                         │    │
│  │  ├─► _flatten_dict()                                    │    │
│  │  ├─► _flatten_analysis_for_csv()                        │    │
│  │  ├─► _flatten_prediction_for_csv()                      │    │
│  │  ├─► _format_kml_description()                          │    │
│  │  └─► generate_filename()                                │    │
│  │                                                          │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagram

```
┌──────────────┐
│   Request    │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Validation  │
│  - Format    │
│  - Params    │
│  - Dates     │
└──────┬───────┘
       │
       ▼
┌──────────────────┐
│  Data Collection │ ◄──── Cache (Redis)
│  - Analysis      │
│  - Timeseries    │
│  - Boundaries    │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  DataExporter    │
│  - Select format │
│  - Transform     │
│  - Flatten       │
└──────┬───────────┘
       │
       ├─────► GeoJSON ──┐
       ├─────► CSV ──────┤
       ├─────► JSON ─────┤
       └─────► KML ──────┤
                         │
                         ▼
                  ┌──────────────┐
                  │ ExportResult │
                  │ - filename   │
                  │ - data       │
                  │ - metadata   │
                  └──────┬───────┘
                         │
                         ▼
                  ┌──────────────────┐
                  │ StreamingResponse│
                  │ - Headers        │
                  │ - Content-Type   │
                  │ - Streaming      │
                  └──────┬───────────┘
                         │
                         ▼
                  ┌──────────────┐
                  │    Client    │
                  │   (Download) │
                  └──────────────┘
```

## Format-Specific Conversion

```
┌─────────────────────────────────────────────────────────────┐
│                    Format Conversion                        │
└─────────────────────────────────────────────────────────────┘

Input Data (Dict/List)
       │
       ├─► GeoJSON
       │   └─► Feature/FeatureCollection
       │       ├─► geometry: {type, coordinates}
       │       └─► properties: {all other fields}
       │
       ├─► CSV
       │   └─► Flatten nested structures
       │       ├─► field.subfield → field_subfield
       │       ├─► lists → comma-separated strings
       │       └─► Write to StringIO with csv.DictWriter
       │
       ├─► JSON
       │   └─► json.dumps with indent=2, default=str
       │
       └─► KML
           └─► XML structure
               ├─► <kml> → <Document> → <Placemark>
               ├─► <Point> or <Polygon>
               └─► <description> with HTML table
```

## Export Endpoint Matrix

```
┌────────────────┬──────────┬──────┬──────┬──────┬──────────────────────┐
│   Endpoint     │ GeoJSON  │ CSV  │ JSON │ KML  │   Best For           │
├────────────────┼──────────┼──────┼──────┼──────┼──────────────────────┤
│ /analysis      │    ✓     │  ✓   │  ✓   │  ✓   │ Current status       │
│ /timeseries    │    ✓     │  ✓   │  ✓   │  ✗   │ Trend analysis       │
│ /boundaries    │    ✓     │  ✗   │  ✓   │  ✓   │ GIS mapping          │
│ /report        │    ✓     │  ✓   │  ✓   │  ✗   │ Comprehensive data   │
└────────────────┴──────────┴──────┴──────┴──────┴──────────────────────┘
```

## Integration Points

```
┌─────────────────────────────────────────────────────────────────┐
│                    External Integrations                        │
└─────────────────────────────────────────────────────────────────┘

DataExporter
     │
     ├─► GIS Systems
     │   ├─► QGIS (GeoJSON, KML)
     │   ├─► ArcGIS (GeoJSON)
     │   └─► Google Earth (KML)
     │
     ├─► Data Analysis
     │   ├─► Excel (CSV)
     │   ├─► Python/pandas (CSV, JSON)
     │   ├─► R (CSV)
     │   └─► Jupyter Notebooks (JSON)
     │
     ├─► Web Applications
     │   ├─► Leaflet (GeoJSON)
     │   ├─► Mapbox (GeoJSON)
     │   └─► OpenLayers (GeoJSON)
     │
     └─► Reporting Tools
         ├─► Power BI (CSV, JSON)
         ├─► Tableau (CSV)
         └─► Custom dashboards (JSON)
```

## Error Handling Flow

```
Request
   │
   ▼
Validate Format ──► Invalid ──► 400: Invalid format
   │ Valid
   ▼
Validate Params ──► Invalid ──► 400: Invalid parameters
   │ Valid
   ▼
Get Data ──────────► Error ───► 500: Data fetch failed
   │ Success
   ▼
Export Data ───────► Error ───► 500: Export failed
   │ Success
   ▼
Stream Response ───► Success ─► 200 + File
```

## Performance Characteristics

```
┌────────────────────────────────────────────────────────────┐
│                    Performance Profile                     │
└────────────────────────────────────────────────────────────┘

Format      │ Speed  │ Size   │ Compression │ Best Use
────────────┼────────┼────────┼─────────────┼─────────────────
GeoJSON     │ Fast   │ Medium │ Good        │ Web mapping
CSV         │ Fast   │ Small  │ Excellent   │ Data analysis
JSON        │ Fast   │ Medium │ Good        │ API integration
KML         │ Medium │ Large  │ Poor        │ Google Earth

Optimization Strategies:
├─► Streaming: Handle large files without memory issues
├─► Caching: Reuse analysis results from Redis
├─► Batching: Process multiple fields efficiently
└─► Flattening: Minimize nested structure overhead
```

## Security Considerations

```
┌────────────────────────────────────────────────────────────┐
│                  Security Measures                         │
└────────────────────────────────────────────────────────────┘

Input Validation
├─► Format enum validation
├─► Coordinate range checks (-90/90, -180/180)
├─► Date format validation
├─► Field count limits (max 100)
└─► Field ID sanitization

Output Safety
├─► No user-controlled XML injection
├─► Filename sanitization
├─► Content-Type headers set correctly
└─► No sensitive data exposure

Rate Limiting
└─► Consider adding rate limits for bulk exports
```

## Testing Architecture

```
┌────────────────────────────────────────────────────────────┐
│                     Test Coverage                          │
└────────────────────────────────────────────────────────────┘

test_export.py (Unit Tests)
├─► DataExporter class
│   ├─► All export methods
│   ├─► All format conversions
│   ├─► Data flattening
│   └─► Filename generation
└─► 100% method coverage

test_export_api.py (Integration Tests)
├─► All API endpoints
│   ├─► /export/analysis
│   ├─► /export/timeseries
│   ├─► /export/boundaries
│   └─► /export/report
├─► All format variations
├─► Error handling
└─► Response validation
```

## Future Enhancements

```
Potential Additions:
├─► Additional Formats
│   ├─► Shapefile (.shp)
│   ├─► GeoTIFF (raster data)
│   └─► GeoPackage (.gpkg)
│
├─► Advanced Features
│   ├─► Compressed archives (ZIP)
│   ├─► PDF report generation
│   ├─► Email delivery
│   └─► Scheduled exports
│
└─► Performance
    ├─► Async processing for large exports
    ├─► Background task queue
    └─► Export caching
```
