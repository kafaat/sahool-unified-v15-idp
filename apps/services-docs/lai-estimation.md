# LAI Estimation Service

**Port**: 3022 | **Type**: Node.js (NestJS, TypeScript) | **Version**: 16.0.0

Leaf Area Index (LAI) estimation service based on the LAI-TransNet two-stage transfer learning framework. Provides multi-platform LAI predictions from UAV and satellite imagery with cross-scale accuracy (R² = 0.69–0.96) and vegetation index computation.

---

## Overview

`lai-estimation` implements the LAI-TransNet research framework (AI in Agriculture Journal, 2025) to estimate Leaf Area Index across multiple spatial resolutions. It fuses UAV (centimeter) and satellite (3–10 m) imagery using a two-stage transfer learning approach: first training on high-resolution UAV data, then fine-tuning with CycleGAN domain alignment for satellite imagery. The service also computes standard and advanced vegetation indices (NDVI, EVI2, GNDVI, SAVI). LAI is a critical biophysical variable for crop growth modeling, irrigation scheduling, and yield prediction.

---

## Architecture

```
NestJS Application (Port 3022)
    ├── LAIModule
    │   ├── LAIController  (estimation endpoints)
    │   └── LAIService     (CNN-TL inference, model fusion)
    └── VegetationIndicesModule
        ├── VegetationIndicesController  (index computation)
        └── VegetationIndicesService     (band math, PROSAIL integration)
    └── HealthController
    └── AuthModule (JWT Bearer via @sahool/nestjs-auth)
```

Swagger documentation is available at `/docs`. Global pipes: `ValidationPipe` (whitelist + transform). Global filters: `HttpExceptionFilter`. Global interceptors: `RequestLoggingInterceptor` with correlation IDs.

---

## API Endpoints

### Health

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Liveness and readiness probe |

### LAI Estimation

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/lai/estimate` | JWT | Estimate LAI from image data (UAV or satellite) |
| POST | `/api/v1/lai/batch` | JWT | Batch LAI estimation for multiple fields |
| GET | `/api/v1/lai/{field_id}/history` | JWT | Historical LAI time series for a field |
| GET | `/api/v1/lai/{field_id}/current` | JWT | Latest LAI estimate for a field |
| POST | `/api/v1/lai/calibrate` | JWT | Calibrate model with ground truth measurements |
| GET | `/api/v1/lai/models` | JWT | List available LAI estimation models |

### Vegetation Indices

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/indices/compute` | JWT | Compute vegetation indices from band data |
| POST | `/api/v1/indices/ndvi` | JWT | NDVI computation from Red and NIR bands |
| POST | `/api/v1/indices/evi2` | JWT | EVI2 computation (Enhanced Vegetation Index 2) |
| POST | `/api/v1/indices/gndvi` | JWT | GNDVI computation (Green NDVI) |
| POST | `/api/v1/indices/savi` | JWT | SAVI computation with soil adjustment factor |
| GET | `/api/v1/indices/{field_id}/history` | JWT | Historical vegetation index time series |

---

## Vegetation Indices

| Index | Formula | Use Case |
|-------|---------|---------|
| NDVI | (NIR - Red) / (NIR + Red) | General vegetation density |
| EVI2 | 2.5 × (NIR - Red) / (NIR + 2.4 × Red + 1) | Dense canopy (reduces saturation) |
| GNDVI | (NIR - Green) / (NIR + Green) | Nitrogen content estimation |
| SAVI | (NIR - Red) / (NIR + Red + L) × (1 + L) | Sparse vegetation (soil noise) |

---

## LAI Model Accuracy

| Platform | Method | R² | RMSE |
|----------|--------|----|------|
| UAV (5 cm) | CNN-TL Stage 1 | 0.96 | 0.15 |
| PlanetScope (3 m) | CNN-TL + CycleGAN | 0.81 | 0.42 |
| Sentinel-2 (10 m) | PROSAIL Transfer | 0.69 | 0.67 |

---

## Supported Data Sources

| Source | Resolution | Revisit | Bands Available |
|--------|-----------|---------|----------------|
| UAV Imagery | 5–50 cm | On-demand | RGB, NIR, RedEdge |
| PlanetScope | 3 m | Daily | Blue, Green, Red, NIR |
| Sentinel-2 | 10–20 m | 5 days | 12 spectral bands |
| Sentinel Hub API | Variable | Variable | All Sentinel-2 bands |

---

## Typical LAI Ranges by Crop and Stage

| Crop | Vegetative Stage | Peak LAI | Harvest |
|------|----------------|---------|---------|
| Wheat | 1.0–2.5 | 4.0–6.0 | 0.5–1.0 |
| Maize | 1.5–3.0 | 5.0–7.0 | 1.0–2.0 |
| Date Palm | 5.0–7.0 | 7.0–9.0 | 5.0–7.0 |
| Tomato | 2.0–3.5 | 4.0–5.5 | 2.0–3.0 |

---

## NATS Events

This service does not publish NATS events directly. LAI estimates are consumed synchronously by:
- `crop-growth-model` (3023) - assimilates LAI into biomass models
- `vegetation-analysis-service` (8090) - combines with NDVI for crop health
- `advisory-service` (8093) - uses LAI for fertilizer timing decisions

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `3022` | HTTP listen port |
| `ENVIRONMENT` | `development` | Deployment environment |
| `DATABASE_URL` | - | Optional PostgreSQL for result persistence |
| `CORS_ALLOWED_ORIGINS` | `https://sahool.com,http://localhost:3000` | CORS origins |
| `JWT_SECRET_KEY` | - | JWT auth (via nestjs-auth) |

---

## Dependencies

- NestJS 10.x, TypeScript 5.9.x
- `@sahool/nestjs-auth` for JWT Bearer authentication
- `@nestjs/swagger` for API documentation at `/docs`
- PROSAIL radiative transfer model library for physics-based computation

---

## Health Endpoints

```
GET /health → {"status": "ok", "service": "lai-estimation", "version": "16.0.0"}
```

---

## Related Services

- **vegetation-analysis-service** (8090) - satellite-based vegetation analysis
- **crop-growth-model** (3023) - consumes LAI for biomass modeling
- **ground-vision-service** (8182) - ground-level LAI from leaf segmentation
- **yolo26-vision-service** (8150) - aerial LAI via leaf segmentation task
