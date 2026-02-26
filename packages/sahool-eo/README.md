# sahool-eo

Earth Observation integration package for the SAHOOL agricultural platform, built on [eo-learn](https://eo-learn.readthedocs.io/). Provides Sentinel-2, Landsat, and MODIS data fetching, S2cloudless cloud masking, 26 vegetation/spectral indices, and high-level field monitoring workflows.

## Requirements

- Python >= 3.9
- `numpy`, `scipy`, `pyyaml` (core)
- `eo-learn >= 1.4.0`, `sentinelhub >= 3.9.0` (satellite fetch)
- `s2cloudless >= 1.7.0` (cloud masking)

## Installation

```bash
# Core only (index computation without satellite fetch)
pip install sahool-eo

# With Sentinel Hub satellite fetch
pip install sahool-eo[eo]

# Full installation (all features)
pip install sahool-eo[full]
```

## Quick Start

```python
from sahool_eo import SahoolEOClient, FieldMonitoringWorkflow

client = SahoolEOClient()
workflow = FieldMonitoringWorkflow(client)
result = workflow.execute(field_id="FIELD-001", bbox=bbox)

print(result["ndvi_mean"])   # e.g. 0.68
print(result["health"])      # "healthy"
```

## Vegetation Indices (26 Total)

| Index | Class | Formula |
|-------|-------|---------|
| NDVI  | `SahoolNDVITask` | (NIR - RED) / (NIR + RED) |
| EVI   | `SahoolEVITask`  | 2.5 * (NIR - RED) / (NIR + 6*RED - 7.5*BLUE + 1) |
| LAI   | `SahoolLAITask`  | Empirical from NDVI / EVI / Red Edge |
| NDWI  | `SahoolNDWITask` | (NIR - SWIR) / (NIR + SWIR) |
| SAVI  | `SahoolSAVITask` | ((NIR - RED) / (NIR + RED + L)) * (1 + L) |
| NDMI  | `SahoolNDMITask` | (NIR - SWIR1) / (NIR + SWIR1) |
| EVI2  | `SahoolEVI2Task` | 2.5 * (NIR - RED) / (NIR + 2.4*RED + 1) |
| BSI   | `SahoolBSITask`  | Bare soil detection |
| NBR   | `SahoolNBRTask`  | Burn severity |
| CCCI  | `SahoolCCCITask` | Canopy chlorophyll content |
| MSI   | `SahoolMSITask`  | Moisture stress (inverse) |
| MNDWI | `SahoolMNDWITask`| Modified NDWI (open water) |
| ...   | Phase 1-3 chlorophyll & red-edge indices | |

### Calculate All Indices in One Pass

```python
from sahool_eo import AllIndicesTask

task = AllIndicesTask(indices=["NDVI", "EVI", "LAI", "NDWI", "BSI"])
eopatch = task.execute(eopatch)

# Access results
ndvi = eopatch.data["NDVI"]   # numpy array (T, H, W, 1)
summary = task.get_summary(eopatch)
# {"NDVI": {"min": 0.1, "max": 0.85, "mean": 0.62, "std": 0.1, "median": 0.65}}
```

## Fetch Tasks

```python
from sahool_eo import SahoolSentinelFetchTask, SahoolLandsatFetchTask

# Sentinel-2 L2A
sentinel_task = SahoolSentinelFetchTask()
eopatch = sentinel_task.execute(bbox=bbox, time_interval=("2025-01-01", "2025-02-01"))

# Landsat-8/9 (via AWS)
landsat_task = SahoolLandsatFetchTask()
```

## Cloud Masking

```python
from sahool_eo import SahoolCloudMaskTask, S2CloudlessTask

# S2cloudless probabilistic cloud mask
cloud_task = SahoolCloudMaskTask(threshold=0.4)
eopatch = cloud_task.execute(eopatch)
```

## Workflows

```python
from sahool_eo import FieldMonitoringWorkflow, TimeSeriesWorkflow, YieldPredictionWorkflow

# Time series NDVI analysis over a growing season
ts_workflow = TimeSeriesWorkflow(client)
series = ts_workflow.execute(
    field_id="FIELD-001",
    bbox=bbox,
    start_date="2025-10-01",
    end_date="2026-02-01",
)

# ML-ready feature extraction for yield prediction
yield_workflow = YieldPredictionWorkflow(client)
features = yield_workflow.execute(field_id="FIELD-001", bbox=bbox)
```

## Configuration

```bash
SENTINEL_HUB_CLIENT_ID=your_client_id
SENTINEL_HUB_CLIENT_SECRET=your_client_secret
SENTINEL_HUB_INSTANCE_ID=your_instance_id
```

## Integration with SAHOOL Platform

This package powers the `vegetation-analysis-service` (port 8090) and feeds NDVI data to the `shared/satellite/sentinel_ndvi.py` module. It is used directly in Python-based analytics pipelines and is not imported by Node.js services.
