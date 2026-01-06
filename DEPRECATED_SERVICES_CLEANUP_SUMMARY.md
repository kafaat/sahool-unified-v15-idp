# Deprecated Services Cleanup Summary

**Date**: 2026-01-06
**Author**: Claude Code Assistant
**Task**: Cleanup and proper deprecation of crop-health and ndvi-engine services

---

## Overview

This document summarizes the comprehensive cleanup and deprecation process for two AI services that have been consolidated into unified replacement services:

1. **crop-health** → **crop-intelligence-service**
2. **ndvi-engine** → **vegetation-analysis-service**

---

## Services Deprecated

### 1. crop-health Service

| Property | Value |
|----------|-------|
| **Port** | 8100 |
| **Replacement** | crop-intelligence-service (Port 8095) |
| **Deprecation Date** | 2026-01-06 |
| **Sunset Date** | 2026-06-01 |
| **Status** | DEPRECATED |

#### Features Migrated to crop-intelligence-service
- ✅ Zone-based field analysis
- ✅ Vegetation indices (NDVI, EVI, NDRE, LCI, NDWI, SAVI)
- ✅ Zone observation management
- ✅ Diagnosis engine with recommendations
- ✅ VRT (Variable Rate Technology) export
- ✅ Timeline tracking

#### Migration Path
```
OLD: POST /api/v1/fields/{field_id}/zones/{zone_id}/observations
NEW: POST /zones/{zone_id}/observations (crop-intelligence-service:8095)

OLD: GET /api/v1/fields/{field_id}/diagnosis
NEW: GET /recommendations/{field_id} (crop-intelligence-service:8095)

OLD: GET /api/v1/fields/{field_id}/vrt
NEW: POST /vrt/export (crop-intelligence-service:8095)
```

### 2. ndvi-engine Service

| Property | Value |
|----------|-------|
| **Port** | 8107 |
| **Replacement** | vegetation-analysis-service (Port 8090) |
| **Deprecation Date** | 2026-01-06 |
| **Sunset Date** | 2026-06-01 |
| **Status** | DEPRECATED |

#### Features Migrated to vegetation-analysis-service
- ✅ NDVI computation from satellite imagery
- ✅ Vegetation indices (NDVI, EVI, NDRE, NDWI, SAVI)
- ✅ Zone analysis and classification
- ✅ Anomaly detection
- ✅ Time series analysis
- ✅ Event publishing (NATS)

#### Migration Path
```
OLD: POST /ndvi/compute (ndvi-engine:8107)
NEW: GET /ndvi/{field_id} (vegetation-analysis-service:8090)

OLD: POST /ndvi/zones (ndvi-engine:8107)
NEW: GET /analysis/{field_id}/stats (vegetation-analysis-service:8090)

OLD: POST /ndvi/anomaly (ndvi-engine:8107)
NEW: GET /analysis/{field_id}/anomaly (vegetation-analysis-service:8090)
```

---

## Changes Implemented

### 1. Service Code Updates

#### crop-health Service
**File**: `/home/user/sahool-unified-v15-idp/apps/services/crop-health/src/main.py`

Changes:
- ✅ Added deprecation notice to module docstring
- ✅ Added startup deprecation warnings to lifespan function
- ✅ Updated FastAPI title to include "(DEPRECATED)"
- ✅ Added deprecation HTTP headers middleware
- ✅ Updated description with deprecation notice

Deprecation Headers Added:
```python
X-API-Deprecated: true
X-API-Deprecation-Date: 2026-01-06
X-API-Deprecation-Info: This service is deprecated. Use crop-intelligence-service instead.
X-API-Sunset: 2026-06-01
Link: <http://crop-intelligence-service:8095>; rel="successor-version"
Deprecation: true
```

#### ndvi-engine Service
**File**: `/home/user/sahool-unified-v15-idp/apps/services/ndvi-engine/src/main.py`

Changes:
- ✅ Added deprecation notice to module docstring
- ✅ Added startup deprecation warnings to lifespan function
- ✅ Updated FastAPI title to include "(DEPRECATED)"
- ✅ Added deprecation HTTP headers middleware
- ✅ Updated description with deprecation notice

Deprecation Headers Added:
```python
X-API-Deprecated: true
X-API-Deprecation-Date: 2026-01-06
X-API-Deprecation-Info: This service is deprecated. Use vegetation-analysis-service instead.
X-API-Sunset: 2026-06-01
Link: <http://vegetation-analysis-service:8090>; rel="successor-version"
Deprecation: true
```

### 2. README Updates

#### crop-health README
**File**: `/home/user/sahool-unified-v15-idp/apps/services/crop-health/README.md`

Changes:
- ✅ Enhanced deprecation notice at top
- ✅ Added deprecation date and sunset date
- ✅ Added replacement service information

#### ndvi-engine README
**File**: `/home/user/sahool-unified-v15-idp/apps/services/ndvi-engine/README.md`

Changes:
- ✅ Enhanced deprecation notice at top
- ✅ Added deprecation date and sunset date
- ✅ Added replacement service information

### 3. Docker Compose Updates

**File**: `/home/user/sahool-unified-v15-idp/docker-compose.yml`

#### crop-health Service
Changes:
- ✅ Enhanced deprecation comments with migration path
- ✅ Added Docker labels for deprecation tracking
- ✅ Added `profiles: [deprecated, legacy]` to disable by default
- ✅ Added clear dates and replacement information

Docker Labels:
```yaml
labels:
  - "com.sahool.deprecated=true"
  - "com.sahool.replacement=crop-intelligence-service"
  - "com.sahool.deprecation.reason=Consolidated into crop-intelligence-service"
  - "com.sahool.deprecation.date=2026-01-06"
  - "com.sahool.sunset.date=2026-06-01"
```

#### ndvi-engine Service
Changes:
- ✅ Enhanced deprecation comments with migration path
- ✅ Added Docker labels for deprecation tracking
- ✅ Added `profiles: [deprecated, legacy]` to disable by default
- ✅ Added clear dates and replacement information

Docker Labels:
```yaml
labels:
  - "com.sahool.deprecated=true"
  - "com.sahool.replacement=vegetation-analysis-service"
  - "com.sahool.deprecation.reason=Consolidated into vegetation-analysis-service"
  - "com.sahool.deprecation.date=2026-01-06"
  - "com.sahool.sunset.date=2026-06-01"
```

### 4. Documentation Updates

**File**: `/home/user/sahool-unified-v15-idp/apps/services/DEPRECATION_SUMMARY.md`

Changes:
- ✅ Added crop-health to deprecated services list
- ✅ Added ndvi-engine to deprecated services list
- ✅ Included feature migration details

---

## Kong API Gateway Routes

Current Kong configuration already routes deprecated service paths to replacement services:

### crop-health Routes
```yaml
# Kong routes /api/v1/crop-health to crop-intelligence-service:8095
- name: crop-health-ai
  host: crop-intelligence-upstream
  routes:
    - paths:
        - /api/v1/crop-health
```

### ndvi-engine Routes
```yaml
# Kong routes /api/v1/ndvi to ndvi-processor:8118
# Note: ndvi-processor is also deprecated, should route to vegetation-analysis-service:8090
- name: ndvi-engine
  url: http://ndvi-processor:8118
  routes:
    - paths:
        - /api/v1/ndvi
```

**⚠️ ACTION REQUIRED**: Update Kong route for ndvi-engine to point to vegetation-analysis-service:8090

---

## Service Usage

### Running WITHOUT Deprecated Services (Recommended)

```bash
# Start platform without deprecated services
docker-compose up

# This will NOT start:
# - crop-health (Port 8100)
# - ndvi-engine (Port 8107)
```

### Running WITH Deprecated Services (Backward Compatibility)

```bash
# Start platform with deprecated services
docker-compose --profile deprecated up

# This will start ALL services including:
# - crop-health (Port 8100)
# - ndvi-engine (Port 8107)
```

### Running ONLY Legacy Services

```bash
# Start only deprecated/legacy services for testing
docker-compose --profile legacy up
```

---

## Testing Deprecation Notices

### 1. Test HTTP Headers

```bash
# Test crop-health deprecation headers
curl -I http://localhost:8100/healthz | grep -i deprecat

# Expected headers:
# X-API-Deprecated: true
# X-API-Deprecation-Date: 2026-01-06
# X-API-Sunset: 2026-06-01
# Deprecation: true
```

```bash
# Test ndvi-engine deprecation headers
curl -I http://localhost:8107/healthz | grep -i deprecat

# Expected headers:
# X-API-Deprecated: true
# X-API-Deprecation-Date: 2026-01-06
# X-API-Sunset: 2026-06-01
# Deprecation: true
```

### 2. Test Startup Warnings

```bash
# Check crop-health startup logs
docker-compose logs crop-health | grep "DEPRECATION WARNING"

# Check ndvi-engine startup logs
docker-compose logs ndvi-engine | grep "DEPRECATION WARNING"
```

### 3. Test API Documentation

```bash
# Check Swagger docs include deprecation notice
curl http://localhost:8100/docs | grep DEPRECATED
curl http://localhost:8107/docs | grep DEPRECATED
```

---

## Migration Timeline

| Date | Milestone |
|------|-----------|
| **2026-01-06** | Services officially marked as DEPRECATED |
| **2026-01-06 - 2026-06-01** | Migration period (6 months) |
| **2026-03-01** | Send migration reminders to API consumers |
| **2026-05-01** | Final migration warnings |
| **2026-06-01** | Sunset date - Services may be removed |
| **2026-07-01** | Complete removal from codebase (target) |

---

## Replacement Services

### crop-intelligence-service (Port 8095)

**Status**: ACTIVE ✅
**Consolidates**:
- crop-health (Port 8100) ← DEPRECATED
- crop-health-ai (Port 8095) ← DEPRECATED
- crop-growth-model (Port 3023) ← DEPRECATED

**Features**:
- Health monitoring
- Disease diagnosis with AI
- Growth simulation
- Yield prediction
- VRT export

**Documentation**: `/home/user/sahool-unified-v15-idp/apps/services/crop-intelligence-service/README.md`

### vegetation-analysis-service (Port 8090)

**Status**: ACTIVE ✅
**Consolidates**:
- satellite-service (Port 8090) ← DEPRECATED
- ndvi-processor (Port 8118) ← DEPRECATED
- ndvi-engine (Port 8107) ← DEPRECATED
- lai-estimation (Port 3022) ← DEPRECATED

**Features**:
- Satellite imagery processing
- NDVI calculations
- Vegetation indices
- LAI estimation
- Time series analysis
- Anomaly detection

**Documentation**: `/home/user/sahool-unified-v15-idp/apps/services/vegetation-analysis-service/README.md`

---

## Benefits of Consolidation

### 1. Reduced Service Fragmentation
- **Before**: 4 crop-related services, 4 vegetation/NDVI services
- **After**: 1 crop-intelligence-service, 1 vegetation-analysis-service
- **Reduction**: 75% fewer services to maintain

### 2. Improved Maintainability
- Single codebase per domain
- Unified API interface
- Consistent error handling
- Shared dependencies

### 3. Better Resource Utilization
- Reduced memory footprint
- Fewer containers to orchestrate
- Simplified deployment
- Lower operational costs

### 4. Enhanced Developer Experience
- Clearer service boundaries
- Easier to understand system
- Reduced cognitive load
- Better documentation

---

## Action Items

### Immediate (Week 1)
- ✅ Mark services as deprecated in code
- ✅ Add deprecation HTTP headers
- ✅ Update README files
- ✅ Update docker-compose.yml with profiles
- ✅ Update documentation

### Short Term (Month 1)
- [ ] Update Kong routes to point to replacement services
- [ ] Notify API consumers about deprecation
- [ ] Add migration guide to documentation
- [ ] Create API compatibility layer if needed

### Medium Term (Months 2-4)
- [ ] Monitor deprecated service usage
- [ ] Track migration progress
- [ ] Provide migration support
- [ ] Update client libraries

### Long Term (Months 5-6)
- [ ] Final migration warnings
- [ ] Verify all consumers migrated
- [ ] Remove deprecated services from docker-compose
- [ ] Archive deprecated code

---

## References

- **Service Consolidation Map**: `/home/user/sahool-unified-v15-idp/docs/SERVICE_CONSOLIDATION_MAP.md`
- **Deprecated Services Doc**: `/home/user/sahool-unified-v15-idp/docs/DEPRECATED_SERVICES.md`
- **Deprecation Summary**: `/home/user/sahool-unified-v15-idp/apps/services/DEPRECATION_SUMMARY.md`
- **RFC 8594 - Sunset HTTP Header**: https://datatracker.ietf.org/doc/html/rfc8594
- **Deprecation HTTP Header**: https://tools.ietf.org/id/draft-dalal-deprecation-header-01.html

---

## Summary

This cleanup properly deprecates the `crop-health` and `ndvi-engine` services with:

✅ **Code-level deprecation notices** - Visible in logs and API docs
✅ **HTTP deprecation headers** - Visible to API consumers
✅ **Docker profiles** - Services disabled by default
✅ **Clear migration path** - Documented replacement services
✅ **Timeline** - 6-month migration period
✅ **Documentation** - Updated all relevant docs

The platform now has clear deprecation notices across all touchpoints, making it easy for consumers to migrate to the replacement services before the sunset date.
