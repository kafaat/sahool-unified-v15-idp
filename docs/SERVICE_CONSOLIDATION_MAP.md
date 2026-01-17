# Service Consolidation Map

**خارطة توحيد الخدمات**

This document tracks the consolidation of microservices from 40+ to ~25 services.

## Consolidation Status

### ✅ Completed Consolidations

#### 1. Weather Services → `weather-service`

| Old Service      | Port      | Status        | New Service     |
| ---------------- | --------- | ------------- | --------------- |
| weather-core     | 8098/8108 | ⚠️ Deprecated | weather-service |
| weather-advanced | 8092      | ⚠️ Deprecated | weather-service |

**New Service:** `weather-service` (Port 8108)

---

#### 2. Chat Services → `chat-service`

| Old Service    | Port | Status        | New Service  |
| -------------- | ---- | ------------- | ------------ |
| chat-service   | 8114 | ✅ Primary    | chat-service |
| community-chat | 8097 | ⚠️ Deprecated | chat-service |

**New Service:** `chat-service` (Port 8114) - Already production-ready

---

#### 3. Crop Intelligence → `crop-intelligence-service`

| Old Service       | Port | Status        | New Service               |
| ----------------- | ---- | ------------- | ------------------------- |
| crop-health       | 8100 | ⚠️ Deprecated | crop-intelligence-service |
| crop-health-ai    | 8095 | ⚠️ Deprecated | crop-intelligence-service |
| crop-growth-model | 8097 | ⚠️ Deprecated | crop-intelligence-service |

**New Service:** `crop-intelligence-service` (Port 8095)

---

#### 4. Vegetation Analysis → `vegetation-analysis-service`

| Old Service       | Port | Status        | New Service                 |
| ----------------- | ---- | ------------- | --------------------------- |
| satellite-service | 8090 | ⚠️ Deprecated | vegetation-analysis-service |
| ndvi-processor    | 8101 | ⚠️ Deprecated | vegetation-analysis-service |
| ndvi-engine       | 8099 | ⚠️ Deprecated | vegetation-analysis-service |
| lai-estimation    | 8100 | ⚠️ Deprecated | vegetation-analysis-service |

**New Service:** `vegetation-analysis-service` (Port 8090)

---

#### 5. Advisory Services → `advisory-service`

| Old Service        | Port | Status        | New Service      |
| ------------------ | ---- | ------------- | ---------------- |
| agro-advisor       | 8095 | ⚠️ Deprecated | advisory-service |
| fertilizer-advisor | 8093 | ⚠️ Deprecated | advisory-service |

**New Service:** `advisory-service` (Port 8093)

> **Note:** `ai-advisor` (Port 8112) remains as separate orchestrator service

---

#### 6. Yield Services → `yield-prediction-service`

| Old Service      | Port | Status        | New Service              |
| ---------------- | ---- | ------------- | ------------------------ |
| yield-engine     | 8098 | ⚠️ Deprecated | yield-prediction-service |
| yield-prediction | 8103 | ⚠️ Deprecated | yield-prediction-service |

**New Service:** `yield-prediction-service` (Port 8103)

---

#### 7. Field Services → `field-management-service`

| Old Service   | Port | Status        | New Service              |
| ------------- | ---- | ------------- | ------------------------ |
| field-core    | 3000 | ⚠️ Deprecated | field-management-service |
| field-service | 8115 | ⚠️ Deprecated | field-management-service |
| field-ops     | 8080 | ⚠️ Deprecated | field-management-service |

**New Service:** `field-management-service` (Port 3000)

---

## Service Count Summary

| Category          | Before | After | Reduction |
| ----------------- | ------ | ----- | --------- |
| Weather           | 2      | 1     | -1        |
| Chat              | 2      | 1     | -1        |
| Crop Intelligence | 3      | 1     | -2        |
| Vegetation        | 4      | 1     | -3        |
| Advisory          | 2      | 1     | -1        |
| Yield             | 2      | 1     | -1        |
| Field             | 3      | 1     | -2        |
| **Total Reduced** | **18** | **7** | **-11**   |

## New Unified Services

| Service                       | Port | Replaces                                       | Features                                                |
| ----------------------------- | ---- | ---------------------------------------------- | ------------------------------------------------------- |
| `weather-service`             | 8108 | weather-core, weather-advanced                 | Weather data, forecasting, agricultural alerts          |
| `chat-service`                | 8114 | community-chat                                 | Real-time messaging, Socket.IO                          |
| `crop-intelligence-service`   | 8095 | crop-health, crop-health-ai, crop-growth-model | Health monitoring, disease diagnosis, growth simulation |
| `vegetation-analysis-service` | 8090 | satellite-service, ndvi-\*, lai-estimation     | Satellite imagery, vegetation indices, LAI              |
| `advisory-service`            | 8093 | agro-advisor, fertilizer-advisor               | Disease diagnosis, fertilizer planning                  |
| `yield-prediction-service`    | 8103 | yield-engine, yield-prediction                 | ML predictions, scenario analysis                       |
| `field-management-service`    | 3000 | field-core, field-service, field-ops           | Field CRUD, tasks, mobile sync                          |

## Migration Guide

### For Developers

1. **Update imports** - Change service references in your code
2. **Update URLs** - Point to new service endpoints
3. **Update docker-compose** - Use new service names
4. **Update Kong routes** - Route to new services

### For DevOps

1. **Phase 1**: Deploy new consolidated services alongside deprecated ones
2. **Phase 2**: Route traffic to new services
3. **Phase 3**: Monitor for issues
4. **Phase 4**: Remove deprecated services

## Deprecated Services Removal Timeline

| Service            | Deprecation Date | Removal Target |
| ------------------ | ---------------- | -------------- |
| weather-core       | 2024-12-28       | v17.0.0        |
| weather-advanced   | 2024-12-28       | v17.0.0        |
| community-chat     | 2024-12-28       | v17.0.0        |
| crop-health        | 2024-12-28       | v17.0.0        |
| crop-health-ai     | 2024-12-28       | v17.0.0        |
| crop-growth-model  | 2024-12-28       | v17.0.0        |
| satellite-service  | 2024-12-28       | v17.0.0        |
| ndvi-processor     | 2024-12-28       | v17.0.0        |
| ndvi-engine        | 2024-12-28       | v17.0.0        |
| lai-estimation     | 2024-12-28       | v17.0.0        |
| agro-advisor       | 2024-12-28       | v17.0.0        |
| fertilizer-advisor | 2024-12-28       | v17.0.0        |
| yield-engine       | 2024-12-28       | v17.0.0        |
| yield-prediction   | 2024-12-28       | v17.0.0        |
| field-core         | 2024-12-28       | v17.0.0        |
| field-service      | 2024-12-28       | v17.0.0        |
| field-ops          | 2024-12-28       | v17.0.0        |

## Architecture Benefits

### Before Consolidation

- 40+ microservices
- Complex service mesh
- High operational overhead
- Duplicate functionality
- Inconsistent APIs

### After Consolidation

- ~25 microservices
- Cleaner architecture
- Reduced maintenance burden
- Single source of truth
- Unified API patterns
- Faster deployments
- Easier debugging
