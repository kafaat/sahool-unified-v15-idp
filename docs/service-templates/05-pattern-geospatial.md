# 05 · Geospatial / PostGIS Compute Template

**Gold standard:** `apps/services/hydrology-service/`
**Related:** `terrain-core-service`, `leveling-optimizer-service`,
`field-management-service` (partially).
**Use when:** the service processes rasters (DEM, NDVI tiles), vectors
(field boundaries, watersheds), or runs heavy PostGIS queries.

> قالب خدمات المعالجة الجغرافية — رموز رقمية للارتفاع، تحليل المياه،
> استعلامات PostGIS الثقيلة.

---

## Why `hydrology-service`?

- Real raster pipeline: DEM → fill sinks → flow direction →
  accumulation → watershed delineation.
- GDAL + rasterio + shapely + pyproj stack handled cleanly in the
  Dockerfile (large native deps).
- PostGIS extension declared in the Prisma schema (example of raster
  + vector in one service).
- NATS events (`sahool.hydrology.analysis.completed`) follow the
  platform convention.

---

## Delta from Pattern 02 / 03

Geospatial services are a Pattern 02 (CRUD with DB) or Pattern 03
(stateless compute) with the following specializations.

### 1 · Dockerfile — native GIS dependencies

```dockerfile
FROM python:3.11-slim-bookworm AS base
RUN apt-get update && apt-get install -y --no-install-recommends \
      gdal-bin libgdal-dev \
      libgeos-dev libproj-dev \
      libspatialindex-dev \
      build-essential \
 && rm -rf /var/lib/apt/lists/*

ENV GDAL_CONFIG=/usr/bin/gdal-config \
    CPLUS_INCLUDE_PATH=/usr/include/gdal \
    C_INCLUDE_PATH=/usr/include/gdal
```

Rasterio and Fiona MUST be installed from wheels tied to the GDAL
version in the base image — pin versions aggressively:

```
GDAL==3.6.*
rasterio==1.3.*
Fiona==1.9.*
shapely==2.0.*
pyproj==3.6.*
geopandas==0.14.*
```

### 2 · PostGIS in Prisma schema

```prisma
datasource db {
  provider   = "postgresql"
  url        = env("DATABASE_URL")
  directUrl  = env("DATABASE_URL_DIRECT")
  extensions = [postgis]
}

generator client {
  provider        = "prisma-client-js"
  previewFeatures = ["postgisExtensions"]
}
```

Raster columns are still mapped via raw SQL until Prisma gets native
support — keep the raw-SQL helpers in a dedicated `geospatial.ts` /
`geospatial.py` module, never scattered across domain code.

### 3 · Spatial indexes

Every geometry column **must** have a GIST index:

```sql
CREATE INDEX idx_fields_boundary_gist
  ON fields USING GIST (boundary);
```

Verify via `\d+ <table>` or the Prisma migration SQL.

### 4 · Tile caching

Expose map tiles via a dedicated `/tiles/{z}/{x}/{y}.png` or
`.mvt` endpoint. Always cache them — regenerating tiles on every
request is fatal:

- CDN cache for public tiles (public NDVI, public DEM).
- Redis / MinIO cache for tenant-private tiles, keyed by
  `(tenant_id, layer_id, z, x, y)`.

### 5 · Long-running jobs

Some operations (basin delineation on a 50-km² DEM) take minutes.
**Don't run them inline.** The pattern:

1. `POST /api/v1/hydrology/basin-delineation` returns `202 Accepted`
   with a `jobId`.
2. The service enqueues a job (NATS or arq/Celery).
3. A worker (separate process) executes the job.
4. On completion it publishes `sahool.hydrology.basin.completed`
   with the `jobId` + S3/MinIO URL of the result.
5. Client polls `GET /api/v1/hydrology/jobs/{id}` or subscribes to the
   event via the WebSocket gateway.

### 6 · Coordinate reference systems (CRS)

- **Input**: accept WGS84 (EPSG:4326) for user data.
- **Compute**: reproject to an equal-area / equal-distance CRS
  appropriate for the region (UTM for Yemen: EPSG:32638 / 32639).
- **Store**: whatever your PostGIS schema dictates — be consistent
  within one table.
- **Output**: return the CRS the user provided.

Never silently change CRS — every DTO that carries a geometry must
name its CRS explicitly.

### 7 · Memory budget

Raster operations go OOM fast. Hard rules:

- Process rasters in **windows** (rasterio `block_windows`), never
  whole rasters into RAM.
- Budget: `MAX_RASTER_SIZE_MB=512` env — reject requests above it
  with `E4002` (bilingual).
- K8s pod memory request ≥ 2× `MAX_RASTER_SIZE_MB` + 1 GB overhead.

### 8 · Events

Typical subjects:

```
sahool.terrain.dem.processed
sahool.terrain.slope.analyzed
sahool.hydrology.drainage.analyzed
sahool.hydrology.watershed.delineated
sahool.hydrology.flow.computed
sahool.leveling.plan.generated
sahool.leveling.cutfill.computed
```

### 9 · Testing

- **Golden raster** test fixtures in `tests/fixtures/golden-rasters/`
  — a 200×200 DEM with known outputs for every algorithm.
- Integration tests run GDAL inside the test container (`apt-get
  install -y gdal-bin` in the CI matrix).
- Memory/time budget assertions: any algorithm that exceeds 10 s or
  1 GB on a 1 km² DEM fails the test.

### 10 · Observability

Emit Prometheus histograms per algorithm:

```python
hist_inference_seconds = Histogram(
    "hydrology_inference_seconds",
    "Algorithm runtime",
    ["algorithm"],
    buckets=(0.1, 0.5, 1.0, 5.0, 10.0, 30.0, 60.0, 300.0),
)
```

---

## Coverage matrix

| Service | PostGIS declared | GIST indexes | Async jobs | CRS explicit | Memory budget | Last audit |
|---|---|---|---|---|---|---|
| hydrology-service | ✅ gold | ✅ | ✅ | ✅ | ✅ | 2026-03 |
| terrain-core-service | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| leveling-optimizer-service | — (compute) | — | ✅ | ✅ | ✅ | — |
| field-management-service | ✅ | ✅ | — | ✅ | — | 2026-04 |
| disaster-assessment | ✅ | ⚠️ | — | — | — | — |
