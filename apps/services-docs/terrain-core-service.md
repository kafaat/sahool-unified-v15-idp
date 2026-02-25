# Terrain Core Service

**Type:** Python / FastAPI
**Port:** 8185
**Version:** 16.0.0
**Layer:** Intelligence (Event Architecture)

## Overview

The Terrain Core Service performs comprehensive terrain analysis for agricultural land assessment using Digital Elevation Model (DEM) data. It produces slope, aspect, flow direction, flow accumulation, Topographic Wetness Index (TWI), curvature, and contour outputs from multiple satellite DEM sources. Results drive irrigation method selection, drainage design, field leveling planning, and precision agriculture zone mapping.

Note: The service README lists port 8160 but the CLAUDE.md service registry and governance/services.yaml record port 8185 as the canonical port.

## Architecture

```
FastAPI Application (port 8185)
├── DEM Ingest Module (Copernicus, SRTM, ALOS, local GeoTIFF)
├── Terrain Processing Engine
│   ├── GDAL >= 3.6 (geospatial I/O and reprojection)
│   ├── rasterio >= 1.3 (raster read/write)
│   └── richdem >= 2.3 (terrain algorithms: D8, D-Infinity, MFD)
├── Irrigation Suitability Classifier
└── Cache Layer (Redis TTL 3600 s, S3/MinIO for DEM tiles)
    ↓
PostgreSQL with PostGIS (analysis result persistence)
    ↓
NATS (terrain analysis completion events)
```

Analysis outputs are projected to EPSG:32637 (UTM 37N) by default, covering the primary operational area of the platform.

## DEM Data Sources

| Source | Resolution | Coverage |
|--------|------------|----------|
| Copernicus DEM GLO-30 | 30 m | Global (ESA) |
| Copernicus DEM GLO-90 | 90 m | Global (ESA) |
| NASA SRTM | 30 m / 90 m | Global |
| ALOS PALSAR | 12.5 m | Asia/Pacific (JAXA) |
| Local upload | User-defined | Custom GeoTIFF |

## API Endpoints

### Health
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/healthz` | GET | Kubernetes liveness probe |
| `/readyz` | GET | Kubernetes readiness probe |
| `/metrics` | GET | Prometheus metrics |

### Terrain Analysis
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/terrain/analyze` | POST | Full terrain analysis (all indicators) |
| `/api/v1/terrain/slope` | POST | Slope analysis only (degrees or percent) |
| `/api/v1/terrain/aspect` | POST | Aspect analysis (8 cardinal directions) |
| `/api/v1/terrain/flow` | POST | Flow direction and flow accumulation |
| `/api/v1/terrain/twi` | POST | Topographic Wetness Index |
| `/api/v1/terrain/curvature` | POST | Plan and profile curvature |
| `/api/v1/terrain/contours` | POST | Contour line generation |

### DEM Management
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/dem/sources` | GET | List available DEM sources |
| `/api/v1/dem/upload` | POST | Upload custom GeoTIFF DEM |
| `/api/v1/dem/fetch` | POST | Fetch DEM for a bounding box |
| `/api/v1/dem/metadata/{field_id}` | GET | DEM metadata for a field |

### Irrigation Suitability
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/terrain/irrigation-zones` | POST | Generate irrigation suitability zones |
| `/api/v1/terrain/recommendations` | GET | Terrain-based irrigation recommendations |

## Terrain Indicators

| Indicator | Description | Agricultural Use |
|-----------|-------------|-----------------|
| Slope | Surface inclination (degrees or %) | Irrigation method selection |
| Aspect | Slope direction (8 classes) | Sun exposure, crop placement |
| Flow Direction | D8 / D-Infinity / MFD flow path | Drainage design |
| Flow Accumulation | Upstream contributing area | Stream network delineation |
| TWI | Topographic Wetness Index | Soil moisture prediction |
| Plan Curvature | Horizontal curvature | Erosion risk assessment |
| Profile Curvature | Vertical curvature | Water flow acceleration |
| Contours | Elevation contour lines | Field visualization and leveling |

## Slope Classification

| Category | Slope | Recommendation |
|----------|-------|----------------|
| Flat | 0–2% | Surface / flood irrigation |
| Gentle | 2–5% | Sprinkler / drip irrigation |
| Moderate | 5–10% | Drip irrigation preferred |
| Steep | 10–20% | Drip only, terracing needed |
| Very Steep | >20% | Not suitable for irrigation |

## NATS Events

### Publishes
| Event | Trigger |
|-------|---------|
| `TerrainAnalysisCompleted.v1` | Full analysis finished |
| `SlopeAnalysisCompleted.v1` | Slope analysis finished |
| `TWICalculated.v1` | TWI calculation finished |
| `ContoursGenerated.v1` | Contour lines generated |

### Consumes
| Event | Action |
|-------|--------|
| `FieldBoundaryCreated.v1` | Process terrain for new field |
| `FieldBoundaryUpdated.v1` | Re-process terrain on boundary change |
| `DEMUpdated.v1` | Re-analyze with new DEM data |

## Environment Variables

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `PORT` | `8185` | No | Service port |
| `DATABASE_URL` | — | Yes | PostgreSQL (PostGIS) connection |
| `REDIS_URL` | — | Yes | Redis for result caching |
| `NATS_URL` | — | Yes | NATS server |
| `DEFAULT_DEM_SOURCE` | `copernicus` | No | Default DEM source |
| `DEFAULT_RESOLUTION_M` | `30.0` | No | Output resolution in meters |
| `MAX_PROCESSING_AREA_KM2` | `1000.0` | No | Maximum analysis area |
| `DEFAULT_CRS` | `EPSG:32637` | No | Default coordinate reference system |
| `RESAMPLING_METHOD` | `bilinear` | No | Raster resampling algorithm |
| `CONTOUR_INTERVAL_M` | `5.0` | No | Default contour interval |
| `FLOW_THRESHOLD` | `100` | No | Flow accumulation for stream detection |
| `TEMP_DIR` | `/tmp/terrain` | No | Working directory for processing |
| `DEM_CACHE_DIR` | `/tmp/terrain/dem_cache` | No | DEM tile cache directory |
| `MAX_UPLOAD_SIZE_MB` | `500` | No | Max GeoTIFF upload size |
| `S3_BUCKET` | — | No | S3/MinIO bucket for DEM storage |
| `AWS_REGION` | `me-south-1` | No | AWS region |
| `CACHE_TTL_SECONDS` | `3600` | No | Redis cache TTL |

## Dependencies

| Package | Purpose |
|---------|---------|
| GDAL >= 3.6 | Geospatial data processing and reprojection |
| rasterio >= 1.3 | Raster I/O |
| richdem >= 2.3 | Terrain analysis algorithms (D8, D-Inf, MFD) |
| shapely >= 2.0 | Geometric operations |
| pyproj >= 3.6 | Coordinate transformations |
| numpy >= 1.24 | Numerical computing |
| FastAPI >= 0.128.5 | Web framework |

System requirements: GDAL binaries, PROJ library, GEOS library.

## Health Endpoints

```
GET /healthz  → {"status": "ok", "service": "terrain-core-service"}
GET /readyz   → {"status": "ok", "database": true, "nats": true}
GET /metrics  → Prometheus: analysis_duration_seconds, dem_fetch_total, cache_hits
```

## Admin Integration Notes

- Terrain analysis is automatically triggered on `FieldBoundaryCreated.v1` events — no manual invocation needed for new fields.
- The admin portal's field detail view can display slope classification maps and TWI overlays sourced from this service.
- Use `/api/v1/terrain/irrigation-zones` to generate zone-level irrigation method recommendations for display in the precision agriculture module.
- The hydrology-service (port 8165) depends on this service for DEM data and TWI inputs; ensure terrain-core-service starts before hydrology-service in Docker Compose.
- For large fields (>100 ha) at 30 m resolution, analysis may take 2–5 minutes; implement async polling in the admin portal using the `TerrainAnalysisCompleted.v1` NATS event.
