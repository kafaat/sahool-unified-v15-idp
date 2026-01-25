# Deprecated Services Report | تقرير الخدمات المهملة

**Platform:** SAHOOL - National Agricultural Intelligence Platform
**Report Date:** 2026-01-25
**Version:** 16.0.0

---

## Executive Summary | الملخص التنفيذي

This report documents all deprecated services in the SAHOOL platform, their replacement services, migration status, and sunset dates.

يوثق هذا التقرير جميع الخدمات المهملة في منصة سهول، والخدمات البديلة لها، وحالة الترحيل، وتواريخ الإيقاف.

### Key Statistics | الإحصائيات الرئيسية

| Metric | Value |
|--------|-------|
| **Total Deprecated Services** | 14 |
| **Archived Services** | 10 |
| **Pending Removal** | 4 |
| **Sunset Date (API v1)** | 2026-06-30 |
| **Services with Active Routes** | 6 (legacy paths) |

---

## Deprecated Services List | قائمة الخدمات المهملة

### Category 1: Satellite & Vegetation Analysis | تحليل الأقمار الصناعية والغطاء النباتي

#### 1. satellite-service → vegetation-analysis-service

| Field | Value |
|-------|-------|
| **Name (AR)** | خدمة الأقمار الصناعية |
| **Original Port** | 9190 |
| **Replacement** | vegetation-analysis-service |
| **Replacement Port** | 8090 |
| **Status** | Archived |
| **Deprecation Date** | 2026-01-11 |
| **Archive Date** | 2026-01-25 |
| **Kong Legacy Route** | `/api/v1/satellite-legacy` |

**Features Migrated:**
- Satellite scene ingestion (SatelliteSceneIngested.v1)
- Raster tile processing (RasterTileReady.v1)
- Index tile computation (IndexTileReady.v1)
- Field indicators calculation (FieldIndicatorsComputed.v1)

**Migration Action:**
```bash
# Old
curl http://satellite-service:9190/api/v1/scenes
# New
curl http://vegetation-analysis-service:8090/api/v1/vegetation/scenes
```

---

#### 2. ndvi-engine → vegetation-analysis-service

| Field | Value |
|-------|-------|
| **Name (AR)** | محرك NDVI |
| **Original Port** | 8097 |
| **Replacement** | vegetation-analysis-service |
| **Replacement Port** | 8090 |
| **Status** | Deprecated (Active) |
| **Deprecation Date** | 2026-01-06 |
| **Sunset Date** | 2026-06-01 |

**Features Migrated:**
- NDVI computation from coordinates
- Sentinel-2 data processing
- Zone analysis and segmentation
- Anomaly detection
- Multiple vegetation indices (EVI, NDRE, NDWI, SAVI)

**Migration Action:**
```bash
# Old
curl -X POST http://ndvi-engine:8097/compute
# New
curl -X POST http://vegetation-analysis-service:8090/api/v1/ndvi/compute
```

---

#### 3. ndvi-processor → vegetation-analysis-service

| Field | Value |
|-------|-------|
| **Name (AR)** | معالج NDVI |
| **Original Port** | 8118 |
| **Replacement** | vegetation-analysis-service |
| **Replacement Port** | 8090 |
| **Status** | Deprecated |

**Features Migrated:**
- Batch NDVI processing
- Time-series analysis
- Historical data aggregation

---

#### 4. lai-estimation → vegetation-analysis-service

| Field | Value |
|-------|-------|
| **Name (AR)** | تقدير مؤشر مساحة الورقة |
| **Original Port** | 8099 (README) / 3022 (Kong) |
| **Replacement** | vegetation-analysis-service |
| **Replacement Port** | 8090 |
| **Status** | Deprecated |
| **Kong Legacy Route** | `/lai-legacy` |

**Features Migrated:**
- LAI estimation from satellite imagery
- Multi-model support (empirical, physical, ML)
- Field measurements calibration
- LAI-NDVI relationship analysis

---

### Category 2: Weather Services | خدمات الطقس

#### 5. weather-advanced → weather-service

| Field | Value |
|-------|-------|
| **Name (AR)** | خدمة الطقس المتقدمة |
| **Original Port** | 9092 |
| **Replacement** | weather-service |
| **Replacement Port** | 8092 |
| **Status** | Archived |
| **Deprecation Date** | 2026-01-11 |
| **Archive Date** | 2026-01-25 |
| **Kong Legacy Route** | `/api/v1/weather-advanced` |

**Features Migrated:**
- Weather observation (WeatherObserved.v1)
- Weather forecasting (WeatherForecastReady.v1)
- Weather alerts (WeatherAlertIssued.v1)

**External APIs:**
- OpenWeatherMap
- WeatherAPI

---

#### 6. weather-core → weather-service

| Field | Value |
|-------|-------|
| **Name (AR)** | نواة الطقس |
| **Original Port** | 8108 |
| **Replacement** | weather-service |
| **Replacement Port** | 8092 |
| **Status** | Deprecated |

---

### Category 3: Crop Intelligence | الذكاء المحصولي

#### 7. crop-health-ai → crop-intelligence-service

| Field | Value |
|-------|-------|
| **Name (AR)** | سهول فيجن - كشف الأمراض |
| **Original Port** | 9095 |
| **Replacement** | crop-intelligence-service |
| **Replacement Port** | 8095 |
| **Status** | Archived |
| **Deprecation Date** | 2026-01-11 |
| **Archive Date** | 2026-01-25 |
| **Kong Legacy Route** | `/api/v1/crop-health-ai` |

**Features Migrated:**
- Crop health assessment (CropHealthAssessed.v1)
- Crop stress detection (CropStressDetected.v1)
- AI-based disease detection

---

#### 8. crop-health → crop-intelligence-service

| Field | Value |
|-------|-------|
| **Name (AR)** | صحة المحاصيل |
| **Original Port** | 8100 |
| **Replacement** | crop-intelligence-service |
| **Replacement Port** | 8095 |
| **Status** | Archived |
| **Archive Date** | 2026-01-25 |

**Features Migrated:**
- Zone-based health monitoring
- Vegetation indices (NDVI, EVI, NDRE, LCI, NDWI, SAVI)
- VRT export

---

### Category 4: Advisory Services | خدمات الاستشارات

#### 9. fertilizer-advisor → advisory-service

| Field | Value |
|-------|-------|
| **Name (AR)** | مستشار التسميد |
| **Original Port** | 9093 |
| **Replacement** | advisory-service |
| **Replacement Port** | 8093 |
| **Status** | Archived |
| **Deprecation Date** | 2026-01-11 |
| **Archive Date** | 2026-01-25 |
| **Kong Legacy Route** | `/api/v1/fertilizer-advisor` |

**Features Migrated:**
- Fertilizer plan proposals (FertilizerPlanProposed.v1)
- Growth stage-based recommendations
- Soil fertility evaluation

---

#### 10. agro-advisor → advisory-service

| Field | Value |
|-------|-------|
| **Name (AR)** | المستشار الزراعي |
| **Original Port** | 8095 |
| **Replacement** | advisory-service |
| **Replacement Port** | 8093 |
| **Status** | Deprecated |
| **Deprecation Date** | 2025-01-06 |
| **Removal Target** | v17.0.0 |

**Features Migrated:**
- Disease diagnosis → `/disease/*`
- Nutrient assessment → `/nutrient/*`
- Fertilizer planning → `/fertilizer/*`
- Crop information → `/crops/*`

**Migration Action:**
```bash
# Old
curl http://agro-advisor:8105/disease/assess
# New
curl http://advisory-service:8093/disease/assess
```

---

### Category 5: Field Management | إدارة الحقول

#### 11. field-core → field-management-service

| Field | Value |
|-------|-------|
| **Name (AR)** | نواة الحقول |
| **Original Port** | 3005 |
| **Replacement** | field-management-service |
| **Replacement Port** | 3000 |
| **Status** | Archived |
| **Deprecation Date** | 2026-01-01 |
| **Archive Date** | 2026-01-25 |

**Features Migrated:**
- Field creation (FieldCreated.v1)
- Field updates (FieldUpdated.v1)

---

#### 12. field-ops → field-management-service

| Field | Value |
|-------|-------|
| **Name (AR)** | عمليات الحقول |
| **Original Port** | 8155 |
| **Replacement** | field-management-service |
| **Replacement Port** | 3000 |
| **Status** | Archived |
| **Deprecation Date** | 2026-01-01 |
| **Archive Date** | 2026-01-25 |
| **Kong Legacy Route** | `/field-ops-legacy` |

**Features Migrated:**
- Field operation logging (FieldOperationLogged.v1)

---

#### 13. field-service → field-management-service

| Field | Value |
|-------|-------|
| **Name (AR)** | خدمة الحقول |
| **Original Port** | 8156 |
| **Replacement** | field-management-service |
| **Replacement Port** | 3000 |
| **Status** | Archived |
| **Deprecation Date** | 2026-01-01 |
| **Archive Date** | 2026-01-25 |

**Features Migrated:**
- Field data synchronization (FieldDataSynced.v1)

---

### Category 6: Yield & Growth Models | نماذج الإنتاجية والنمو

#### 14. yield-prediction → yield-prediction-service

| Field | Value |
|-------|-------|
| **Name (AR)** | توقع الإنتاجية |
| **Original Port** | 3021 / 8103 |
| **Replacement** | yield-prediction-service |
| **Replacement Port** | 8103 |
| **Status** | Deprecated |
| **Kong Legacy Route** | `/yield-legacy` |

**Features:**
- Single field prediction
- Regional forecasting
- Historical comparison
- Yield optimization recommendations

---

#### 15. yield-engine → yield-prediction-service

| Field | Value |
|-------|-------|
| **Name (AR)** | محرك التنبؤ بالإنتاجية |
| **Original Port** | 8098 |
| **Replacement** | yield-prediction-service |
| **Status** | Deprecated |

---

#### 16. crop-growth-model (Legacy)

| Field | Value |
|-------|-------|
| **Original Port** | 3023 |
| **Status** | Deprecated |
| **Kong Legacy Route** | `/crop-growth-legacy` |

---

## API v1 Deprecation | إهمال API v1

All API v1 routes are deprecated with the following schedule:

| Stage | Date | Action |
|-------|------|--------|
| Deprecation Announced | 2026-01-01 | Headers added |
| Reduced Rate Limits | 2026-03-01 | 50/min max |
| Warning Period | 2026-04-01 | Aggressive warnings |
| **Sunset Date** | **2026-06-30** | **Routes removed** |

### HTTP Deprecation Headers

All deprecated endpoints return these headers:

```http
X-API-Deprecated: true
X-API-Deprecation-Date: 2026-01-01
X-API-Deprecation-Info: This service is deprecated. Use <replacement> instead.
X-API-Sunset: 2026-06-30
X-API-Version: 1
Link: <http://replacement:port>; rel="successor-version"
Warning: 299 - "API version 1 is deprecated and will be removed on 2026-06-30"
Deprecation: true
```

---

## Kong Gateway Legacy Routes | مسارات Kong القديمة

The following legacy routes are still accessible but should not be used:

| Legacy Route | Deprecated Service | Replacement Route |
|--------------|-------------------|-------------------|
| `/api/v1/satellite-legacy` | satellite-service | `/api/v1/vegetation` |
| `/api/v1/weather-advanced` | weather-advanced | `/api/v1/weather` |
| `/api/v1/crop-health-ai` | crop-health-ai | `/api/v1/crop-intelligence` |
| `/api/v1/fertilizer-advisor` | fertilizer-advisor | `/api/v1/advisory` |
| `/yield-legacy` | yield-prediction | `/api/v1/yield` |
| `/lai-legacy` | lai-estimation | `/api/v1/vegetation/lai` |
| `/crop-growth-legacy` | crop-growth-model | `/api/v1/crop-growth` |
| `/field-ops-legacy` | field-ops | `/api/v1/fields` |

---

## Migration Checklist | قائمة التحقق من الترحيل

### For API Consumers | لمستهلكي API

- [ ] Update service URLs to replacement services
- [ ] Update API paths from v1 to v2 where applicable
- [ ] Monitor for deprecation headers in responses
- [ ] Test with new endpoints before sunset date
- [ ] Update client libraries and SDKs

### For Service Operators | لمشغلي الخدمات

- [ ] Monitor usage of deprecated services via logs/metrics
- [ ] Notify stakeholders about deprecation timeline
- [ ] Archive deprecated service directories to `archive/deprecated-services/`
- [ ] Remove deprecated services from docker-compose profiles
- [ ] Update Kong routes after sunset date
- [ ] Clean up database schemas for archived services

---

## Archived Services Location | موقع الخدمات المؤرشفة

All archived services have been moved to:
```
archive/deprecated-services/
├── satellite-service/
├── weather-advanced/
├── crop-health-ai/
├── crop-health/
├── fertilizer-advisor/
├── field-core/
├── field-ops/
└── field-service/
```

---

## Monitoring Deprecated Services | مراقبة الخدمات المهملة

### Check Deprecation Warnings

```bash
# Check startup logs for deprecation warnings
docker-compose logs 2>&1 | grep "DEPRECATION WARNING"

# Check specific service
docker-compose logs weather-advanced | grep "DEPRECATION"
docker-compose logs crop-health-ai | grep "DEPRECATION"
docker-compose logs satellite-service | grep "DEPRECATION"
```

### Check HTTP Headers

```bash
# Verify deprecation headers are present
curl -I http://localhost:8092/healthz | grep -i deprecat
curl -I http://localhost:8095/healthz | grep -i deprecat
curl -I http://localhost:8090/healthz | grep -i deprecat
```

### Prometheus Metrics

Query deprecated service usage:
```promql
# Count requests to deprecated services
sum(rate(http_requests_total{service=~"satellite-service|weather-advanced|crop-health-ai"}[5m]))

# Alert if deprecated services still receiving traffic
sum(rate(http_requests_total{deprecated="true"}[1h])) > 0
```

---

## Timeline Summary | ملخص الجدول الزمني

```
2025-01-01  ─┬─ Deprecation announced for initial services
             │
2026-01-01  ─┼─ API v1 deprecation headers added
             │  Field services marked deprecated
             │
2026-01-06  ─┼─ NDVI engine, crop-health deprecated
             │
2026-01-11  ─┼─ Satellite, weather-advanced, crop-health-ai,
             │  fertilizer-advisor deprecated
             │
2026-01-25  ─┼─ Services archived (current)
             │
2026-03-01  ─┼─ Reduced rate limits for v1 (50/min)
             │
2026-06-01  ─┼─ Sunset date for some services
             │
2026-06-30  ─┴─ API v1 sunset - routes removed
```

---

## Contact & Support | الاتصال والدعم

For migration assistance:
- **Documentation:** `docs/`
- **Service Registry:** `governance/services.yaml`
- **API Mapping:** `docs/kong-backend-services-api-mapping.md`

---

**Report Generated:** 2026-01-25
**Author:** Claude Code
**Status:** Complete
