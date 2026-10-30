# shared/satellite

Satellite imagery integration for the SAHOOL platform using Sentinel Hub.
Provides NDVI, LAI, and other vegetation indices from free Copernicus Sentinel-2
data (10 m resolution, 5-day revisit) with bilingual health classification.
Gracefully degrades to seasonal mock data when credentials are absent, supporting
offline-first development and CI environments.

## File Structure

```
shared/satellite/
├── __init__.py          # Module exports
└── sentinel_ndvi.py     # Analyzer, data classes, evalscripts
```

## Key Components

### Data Classes

| Class | Purpose |
|-------|---------|
| `FieldBoundary` | Field definition: `field_id`, coordinate list, area in ha, CRS. Provides `to_bbox()` helper. |
| `NDVIResult` | Single analysis result: mean/min/max/std values, cloud coverage, pixel count, health status (EN + AR). Health classification is set automatically in `__post_init__`. |
| `TimeSeriesNDVI` | Ordered list of `NDVIResult` measurements with trend computation (`improving` / `stable` / `declining`). |

### VegetationIndex Enum

`NDVI`, `LAI`, `EVI`, `SAVI`, `NDWI`, `MSAVI`

### Health Status Classification (NDVI)

| NDVI Range | Status | Arabic |
|------------|--------|--------|
| >= 0.6 | healthy | صحي |
| 0.4 – 0.6 | moderate | معتدل |
| 0.2 – 0.4 | stressed | مجهد |
| < 0.2 | critical | حرج |

### SentinelNDVIAnalyzer

Main analysis class. Initialises with Sentinel Hub credentials (from arguments or
environment variables). Falls back to seasonal mock data when credentials are
absent or `sentinelhub` is not installed, making the module safe to import in
offline-first and test environments.

| Method | Purpose |
|--------|---------|
| `initialize()` | Connect to Sentinel Hub, returns `False` gracefully if unconfigured |
| `get_ndvi(field, date, max_cloud_coverage)` | Latest NDVI within 5 days of `date`, up to `max_cloud_coverage`% clouds |
| `get_time_series(field, start_date, end_date, interval_days)` | Repeated NDVI sampling over a date range |
| `get_vegetation_index(field, index_type, date)` | Any supported `VegetationIndex` |
| `analyze_crop_health(field, date)` | Combined NDVI + 30-day trend + bilingual recommendations |

The NDVI evalscript uses Sentinel-2 bands B04 (red) and B08 (NIR) with SCL-based
cloud masking. The LAI evalscript uses an empirical formula on the red-edge bands.

`TimeSeriesNDVI.trend` compares the latest value against the first to classify as
`"improving"` (delta > 0.05), `"declining"` (delta < -0.05), or `"stable"`.
`analyze_crop_health` merges the current reading with the 30-day trend to produce
bilingual recommendations (`recommendations`, `recommendations_ar`).

## Usage Example

```python
from shared.satellite import SentinelNDVIAnalyzer, FieldBoundary, VegetationIndex
from datetime import datetime, UTC

analyzer = SentinelNDVIAnalyzer()
await analyzer.initialize()

field = FieldBoundary(
    field_id="FIELD-003",
    coordinates=[(46.70, 24.70), (46.80, 24.70), (46.80, 24.80), (46.70, 24.80)],
    area_hectares=10.0,
)

# Single NDVI reading
result = await analyzer.get_ndvi(field, max_cloud_coverage=30.0)
if result:
    print(f"NDVI: {result.mean_value:.2f}")   # 0.65
    print(f"Status: {result.health_status}")  # healthy
    print(f"Arabic: {result.health_status_ar}")  # صحي

# Time series for the past 30 days
from datetime import timedelta
end = datetime.now(UTC)
start = end - timedelta(days=30)
ts = await analyzer.get_time_series(field, start, end, interval_days=5)
print(f"Trend: {ts.trend}")  # improving / stable / declining

# LAI
lai = await analyzer.get_vegetation_index(field, VegetationIndex.LAI)

# Full crop health report
report = await analyzer.analyze_crop_health(field)
print(report["health_status"])       # stressed
print(report["recommendations"])     # ['Consider additional fertilization', ...]
print(report["recommendations_ar"])  # ['فكر في تسميد إضافي', ...]
```

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `SENTINEL_HUB_CLIENT_ID` | OAuth2 client ID from sentinel-hub.com |
| `SENTINEL_HUB_CLIENT_SECRET` | OAuth2 client secret |
| `SENTINEL_HUB_INSTANCE_ID` | (Optional) Sentinel Hub instance ID |

Free registration: https://www.sentinel-hub.com/develop/api/

When credentials are not configured the analyzer silently returns mock data with
realistic seasonal variation, enabling local development without API access.
