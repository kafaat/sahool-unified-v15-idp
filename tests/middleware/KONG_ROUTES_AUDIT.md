# Kong Routes Configuration Audit Report

**Generated**: 2026-01-06
**Configuration Files Audited**:

- `/home/user/sahool-unified-v15-idp/infrastructure/gateway/kong/kong.yml` (Canonical)
- `/home/user/sahool-unified-v15-idp/infra/kong/kong.yml` (Mirror)
- `/home/user/sahool-unified-v15-idp/infrastructure/gateway/kong-ha/kong/declarative/kong.yml` (HA Config)

---

## Executive Summary

### Total Configuration

- **Upstreams Defined**: 15
- **Services Configured**: 37
- **Routes Defined**: 37
- **Actual Services in apps/services/**: 54 directories
- **Missing Routes**: 17 services
- **Deprecated Services with Routes**: 9
- **Duplicate Route Paths**: 3 conflicts identified

### Health Status

- ✅ All configured routes have proper path definitions
- ✅ All configured routes have methods specified or defaulted
- ✅ All configured routes use `strip_path: false` (consistent)
- ⚠️ No regex priority settings found (may need for advanced routing)
- ⚠️ Multiple services missing from Kong configuration
- ⚠️ Deprecated services still have active routes

---

## 1. Upstreams Analysis

### Configured Upstreams (15)

| Upstream Name                 | Target                      | Port | Health Check Path | Status        |
| ----------------------------- | --------------------------- | ---- | ----------------- | ------------- |
| field-management-upstream     | field-management-service    | 3000 | /healthz          | ✅ Active     |
| weather-service-upstream      | weather-service             | 8092 | /healthz          | ✅ Active     |
| vegetation-analysis-upstream  | vegetation-analysis-service | 8090 | /healthz          | ✅ Active     |
| ai-advisor-upstream           | ai-advisor                  | 8112 | /healthz          | ✅ Active     |
| crop-intelligence-upstream    | crop-intelligence-service   | 8095 | /healthz          | ✅ Active     |
| advisory-service-upstream     | advisory-service            | 8093 | /healthz          | ✅ Active     |
| iot-gateway-upstream          | iot-gateway                 | 8106 | /healthz          | ⚠️ Deprecated |
| iot-service-upstream          | iot-service                 | 8117 | /healthz          | ✅ Active     |
| virtual-sensors-upstream      | virtual-sensors             | 8119 | /healthz          | ✅ Active     |
| marketplace-service-upstream  | marketplace-service         | 3010 | /healthz          | ✅ Active     |
| billing-core-upstream         | billing-core                | 8089 | /healthz          | ✅ Active     |
| notification-service-upstream | notification-service        | 8110 | /healthz          | ✅ Active     |
| research-core-upstream        | research-core               | 3015 | /healthz          | ✅ Active     |
| disaster-assessment-upstream  | disaster-assessment         | 3020 | /healthz          | ✅ Active     |
| field-intelligence-upstream   | field-intelligence          | 8120 | /healthz          | ✅ Active     |
| mcp-server-upstream           | mcp-server                  | 8200 | /health           | ✅ Active     |
| code-review-upstream          | code-review-service         | 8096 | /health           | ✅ Active     |

### Issues Found:

1. ❌ **iot-gateway-upstream** - Points to deprecated service (port 8106)
2. ⚠️ **Inconsistent Health Paths**: Most use `/healthz`, but mcp-server and code-review use `/health`

---

## 2. Services and Routes Analysis

### 2.1 Starter Package Services (5 services)

#### ✅ field-core

- **Service Name**: field-core
- **Upstream**: field-management-upstream → field-management-service:3000
- **Route Name**: field-core-route
- **Paths**:
  - `/api/v1/fields`
  - `/api/v1/field-core`
- **Methods**: GET, POST, PUT, PATCH, DELETE
- **Strip Path**: false ✅
- **Timeouts**: connect=5s, write=60s, read=60s
- **Retries**: 3
- **Plugins**: JWT, ACL (starter/professional/enterprise), Rate Limiting (100/min, 5000/hour), Correlation ID, Request Size (10MB)
- **Status**: ✅ Properly configured

#### ✅ weather-service

- **Service Name**: weather-service
- **Upstream**: weather-service-upstream → weather-service:8092
- **Route Name**: weather-service-route
- **Paths**: `/api/v1/weather`
- **Methods**: GET, POST
- **Strip Path**: false ✅
- **Retries**: 3
- **Plugins**: JWT, ACL (starter/professional/enterprise), Rate Limiting (100/min), Response Transformer
- **Status**: ✅ Properly configured

#### ✅ astronomical-calendar

- **Service Name**: astronomical-calendar
- **URL**: http://astronomical-calendar:8111 (Direct URL, no upstream)
- **Route Name**: astronomical-calendar-route
- **Paths**:
  - `/api/v1/astronomical`
  - `/api/v1/calendar`
- **Methods**: Not specified (defaults to all)
- **Strip Path**: false ✅
- **Plugins**: JWT, ACL (starter/professional/enterprise), Rate Limiting (100/min)
- **Status**: ✅ Properly configured

#### ✅ advisory-service

- **Service Name**: advisory-service
- **URL**: http://advisory-service:8093
- **Route Name**: advisory-route
- **Paths**:
  - `/api/v1/advice`
  - `/api/v1/advisory`
  - `/api/v1/agro-advisor` (Legacy path for backwards compatibility)
- **Methods**: Not specified (defaults to all)
- **Strip Path**: false ✅
- **Plugins**: JWT, ACL (starter/professional/enterprise), Rate Limiting (100/min)
- **Notes**: Consolidates deprecated agro-advisor and fertilizer-advisor
- **Status**: ✅ Properly configured with legacy support

#### ✅ notification-service

- **Service Name**: notification-service
- **URL**: http://notification-service:8110
- **Route Name**: notification-route
- **Paths**: `/api/v1/notifications`
- **Methods**: Not specified (defaults to all)
- **Strip Path**: false ✅
- **Plugins**: JWT, ACL (starter/professional/enterprise), Rate Limiting (100/min)
- **Status**: ✅ Properly configured

---

### 2.2 Professional Package Services (11 services)

#### ✅ satellite-service

- **Service Name**: satellite-service
- **Upstream**: vegetation-analysis-upstream → vegetation-analysis-service:8090
- **Route Name**: satellite-route
- **Paths**: `/api/v1/satellite`
- **Methods**: Not specified
- **Strip Path**: false ✅
- **Timeouts**: connect=10s, write=120s, read=120s
- **Retries**: 3
- **Plugins**: JWT, ACL (professional/enterprise), Rate Limiting (1000/min, 50000/hour), Request Size (50MB)
- **Status**: ✅ Properly configured

#### ✅ ndvi-engine

- **Service Name**: ndvi-engine
- **URL**: http://ndvi-processor:8118
- **Route Name**: ndvi-route
- **Paths**: `/api/v1/ndvi`
- **Methods**: Not specified
- **Strip Path**: false ✅
- **Plugins**: JWT, ACL (professional/enterprise), Rate Limiting (1000/min)
- **Status**: ✅ Properly configured

#### ✅ crop-health-ai

- **Service Name**: crop-health-ai
- **Upstream**: crop-intelligence-upstream → crop-intelligence-service:8095
- **Route Name**: crop-health-route
- **Paths**: `/api/v1/crop-health`
- **Methods**: Not specified
- **Strip Path**: false ✅
- **Timeouts**: connect=10s, write=120s, read=120s
- **Plugins**: JWT, ACL (professional/enterprise), Rate Limiting (1000/min), Request Size (25MB)
- **Status**: ✅ Properly configured

#### ✅ irrigation-smart

- **Service Name**: irrigation-smart
- **URL**: http://irrigation-smart:8094
- **Route Name**: irrigation-route
- **Paths**: `/api/v1/irrigation`
- **Methods**: Not specified
- **Strip Path**: false ✅
- **Plugins**: JWT, ACL (professional/enterprise), Rate Limiting (1000/min)
- **Status**: ✅ Properly configured

#### ✅ virtual-sensors

- **Service Name**: virtual-sensors
- **Upstream**: virtual-sensors-upstream → virtual-sensors:8119
- **Route Name**: virtual-sensors-route
- **Paths**: `/api/v1/sensors/virtual`
- **Methods**: Not specified
- **Strip Path**: false ✅
- **Plugins**: JWT, ACL (professional/enterprise), Rate Limiting (1000/min)
- **Status**: ✅ Properly configured

#### ✅ yield-engine

- **Service Name**: yield-engine
- **URL**: http://yield-prediction-service:8098
- **Route Name**: yield-engine-route
- **Paths**: `/api/v1/yield`
- **Methods**: Not specified
- **Strip Path**: false ✅
- **Plugins**: JWT, ACL (professional/enterprise), Rate Limiting (1000/min)
- **Status**: ✅ Properly configured

#### ⚠️ fertilizer-advisor

- **Service Name**: fertilizer-advisor
- **Upstream**: advisory-service-upstream → advisory-service:8093
- **Route Name**: fertilizer-route
- **Paths**: `/api/v1/fertilizer`
- **Methods**: Not specified
- **Strip Path**: false ✅
- **Plugins**: JWT, ACL (professional/enterprise), Rate Limiting (1000/min)
- **Status**: ⚠️ Routes to advisory-service (consolidated service)
- **Note**: Service directory still exists at `apps/services/fertilizer-advisor`

#### ✅ inventory-service

- **Service Name**: inventory-service
- **URL**: http://inventory-service:8116
- **Route Name**: inventory-route
- **Paths**: `/api/v1/inventory`
- **Methods**: Not specified
- **Strip Path**: false ✅
- **Plugins**: JWT, ACL (professional/enterprise), Rate Limiting (1000/min)
- **Status**: ✅ Properly configured

#### ✅ field-intelligence

- **Service Name**: field-intelligence
- **URL**: http://field-intelligence:8120
- **Route Name**: field-intelligence-route
- **Paths**:
  - `/api/v1/field-intelligence`
  - `/api/v1/intelligence`
- **Methods**: Not specified
- **Strip Path**: false ✅
- **Plugins**: JWT, ACL (professional/enterprise), Rate Limiting (1000/min)
- **Status**: ✅ Properly configured

#### ✅ equipment-service

- **Service Name**: equipment-service
- **URL**: http://equipment-service:8101
- **Route Name**: equipment-route
- **Paths**: `/api/v1/equipment`
- **Methods**: Not specified
- **Strip Path**: false ✅
- **Plugins**: JWT, ACL (professional/enterprise), Rate Limiting (1000/min)
- **Status**: ⚠️ Service marked as deprecated in service-registry.yaml

#### ✅ weather-advanced

- **Service Name**: weather-advanced
- **URL**: http://weather-service:8092
- **Route Name**: weather-advanced-route
- **Paths**: `/api/v1/weather/advanced`
- **Methods**: Not specified
- **Strip Path**: false ✅
- **Plugins**: JWT, ACL (professional/enterprise), Rate Limiting (1000/min)
- **Status**: ✅ Consolidated into weather-service

---

### 2.3 Enterprise Package Services (9 services)

#### ✅ ai-advisor

- **Service Name**: ai-advisor
- **Upstream**: ai-advisor-upstream → ai-advisor:8112
- **Route Name**: ai-advisor-route
- **Paths**: `/api/v1/ai-advisor`
- **Methods**: Not specified
- **Strip Path**: false ✅
- **Timeouts**: connect=15s, write=180s, read=180s
- **Plugins**: JWT, ACL (enterprise/research), Rate Limiting (10000/min, 500000/hour), Request Size (50MB)
- **Status**: ✅ Properly configured

#### ⚠️ iot-gateway

- **Service Name**: iot-gateway
- **Upstream**: iot-gateway-upstream → iot-gateway:8106
- **Route Name**: iot-gateway-route
- **Paths**:
  - `/api/v1/iot`
  - `/api/v1/agro-rules`
- **Methods**: Not specified
- **Strip Path**: false ✅
- **Plugins**: JWT, ACL (enterprise), Rate Limiting (10000/min), IP Restriction (internal only)
- **Status**: ⚠️ Service marked as deprecated in service-registry.yaml

#### ✅ research-core

- **Service Name**: research-core
- **URL**: http://research-core:3015
- **Route Name**: research-route
- **Paths**: `/api/v1/research`
- **Methods**: Not specified
- **Strip Path**: false ✅
- **Plugins**: JWT, ACL (enterprise/research), Rate Limiting (10000/min), IP Restriction (internal only)
- **Status**: ✅ Properly configured

#### ✅ marketplace-service

- **Service Name**: marketplace-service
- **URL**: http://marketplace-service:3010
- **Route Name**: marketplace-route
- **Paths**: `/api/v1/marketplace`
- **Methods**: Not specified
- **Strip Path**: false ✅
- **Plugins**: JWT, ACL (enterprise), Rate Limiting (10000/min), IP Restriction (internal only)
- **Status**: ✅ Properly configured

#### ✅ billing-core

- **Service Name**: billing-core
- **URL**: http://billing-core:8089
- **Route Name**: billing-route
- **Paths**: `/api/v1/billing`
- **Methods**: Not specified
- **Strip Path**: false ✅
- **Plugins**: JWT, ACL (starter/professional/enterprise), Rate Limiting (1000/min), IP Restriction (internal only)
- **Status**: ✅ Properly configured

#### ✅ disaster-assessment

- **Service Name**: disaster-assessment
- **URL**: http://disaster-assessment:3020
- **Route Name**: disaster-route
- **Paths**:
  - `/api/v1/disaster`
  - `/api/v1/disasters`
- **Methods**: Not specified
- **Strip Path**: false ✅
- **Plugins**: JWT, ACL (enterprise/research), Rate Limiting (10000/min), IP Restriction (internal only)
- **Status**: ✅ Properly configured

#### ✅ crop-growth-model

- **Service Name**: crop-growth-model
- **URL**: http://crop-growth-model:3023
- **Route Name**: crop-model-route
- **Paths**: `/api/v1/crop-model`
- **Methods**: Not specified
- **Strip Path**: false ✅
- **Timeouts**: connect=15s, write=180s, read=180s
- **Plugins**: JWT, ACL (enterprise/research), Rate Limiting (10000/min)
- **Status**: ✅ Properly configured

#### ✅ lai-estimation

- **Service Name**: lai-estimation
- **URL**: http://lai-estimation:3022
- **Route Name**: lai-route
- **Paths**: `/api/v1/lai`
- **Methods**: Not specified
- **Strip Path**: false ✅
- **Plugins**: JWT, ACL (enterprise/research), Rate Limiting (10000/min)
- **Status**: ✅ Properly configured

#### ✅ yield-prediction

- **Service Name**: yield-prediction
- **URL**: http://yield-prediction:3021
- **Route Name**: yield-prediction-route
- **Paths**: `/api/v1/yield-prediction`
- **Methods**: Not specified
- **Strip Path**: false ✅
- **Plugins**: JWT, ACL (enterprise/research), Rate Limiting (10000/min)
- **Status**: ✅ Properly configured

---

### 2.4 Shared Services (12 services)

#### ⚠️ field-ops

- **Service Name**: field-ops
- **URL**: http://field-management-service:3000
- **Route Name**: field-ops-route
- **Paths**: `/api/v1/field-ops`
- **Methods**: Not specified
- **Strip Path**: false ✅
- **Plugins**: JWT, ACL (all users), Rate Limiting (1000/min)
- **Status**: ⚠️ Service marked as deprecated, routes to field-management-service

#### ✅ ws-gateway

- **Service Name**: ws-gateway
- **URL**: http://ws-gateway:8081
- **Route Name**: ws-gateway-route
- **Paths**: `/api/v1/ws`
- **Methods**: Not specified
- **Strip Path**: false ✅
- **Protocols**: http, https
- **Plugins**: JWT, ACL (all users), Rate Limiting (5000/min)
- **Status**: ✅ Properly configured

#### ✅ indicators-service

- **Service Name**: indicators-service
- **URL**: http://indicators-service:8091
- **Route Name**: indicators-route
- **Paths**: `/api/v1/indicators`
- **Methods**: Not specified
- **Strip Path**: false ✅
- **Plugins**: JWT, ACL (professional/enterprise/research), Rate Limiting (1000/min)
- **Status**: ✅ Properly configured

#### ✅ community-chat

- **Service Name**: community-chat
- **URL**: http://community-chat:8097
- **Route Name**: community-chat-route
- **Paths**: `/api/v1/community/chat`
- **Methods**: Not specified
- **Strip Path**: false ✅
- **Plugins**: JWT, ACL (all users), Rate Limiting (2000/min)
- **Status**: ✅ Properly configured

#### ⚠️ field-chat

- **Service Name**: field-chat
- **URL**: http://field-chat:8099
- **Route Name**: field-chat-route
- **Paths**:
  - `/api/v1/field/chat`
  - `/api/v1/field-chat`
- **Methods**: Not specified
- **Strip Path**: false ✅
- **Plugins**: JWT, ACL (all users), Rate Limiting (2000/min)
- **Status**: ⚠️ Service marked as deprecated, replacement is community-chat

#### ⚠️ task-service

- **Service Name**: task-service
- **URL**: http://task-service:8103
- **Route Name**: task-route
- **Paths**: `/api/v1/tasks`
- **Methods**: Not specified
- **Strip Path**: false ✅
- **Plugins**: JWT, ACL (all users), Rate Limiting (1000/min)
- **Status**: ⚠️ Service marked as deprecated, merged into field-service

#### ⚠️ provider-config

- **Service Name**: provider-config
- **URL**: http://provider-config:8104
- **Route Name**: provider-config-route
- **Paths**: `/api/v1/providers`
- **Methods**: Not specified
- **Strip Path**: false ✅
- **Plugins**: JWT, ACL (professional/enterprise), Rate Limiting (500/min)
- **Status**: ⚠️ Service marked as deprecated, merged into billing-core

#### ✅ alert-service

- **Service Name**: alert-service
- **URL**: http://alert-service:8113
- **Route Name**: alert-route
- **Paths**: `/api/v1/alerts`
- **Methods**: Not specified
- **Strip Path**: false ✅
- **Plugins**: JWT, ACL (all users), Rate Limiting (1000/min)
- **Status**: ✅ Properly configured

#### ✅ chat-service

- **Service Name**: chat-service
- **URL**: http://chat-service:8114
- **Route Name**: chat-service-route
- **Paths**: `/api/v1/chat`
- **Methods**: Not specified
- **Strip Path**: false ✅
- **Plugins**: JWT, ACL (all users), Rate Limiting (2000/min)
- **Status**: ✅ Properly configured

#### ⚠️ field-service

- **Service Name**: field-service
- **URL**: http://field-management-service:3000
- **Route Name**: field-service-route
- **Paths**: `/api/v1/field-service`
- **Methods**: Not specified
- **Strip Path**: false ✅
- **Plugins**: JWT, ACL (all users), Rate Limiting (1000/min)
- **Status**: ⚠️ Service directory exists but may be consolidated

#### ✅ iot-service

- **Service Name**: iot-service
- **Upstream**: iot-service-upstream → iot-service:8117
- **Route Name**: iot-service-route
- **Paths**: `/api/v1/iot-service`
- **Methods**: Not specified
- **Strip Path**: false ✅
- **Plugins**: JWT, ACL (enterprise), Rate Limiting (10000/min)
- **Status**: ✅ Properly configured

#### ✅ ndvi-processor

- **Service Name**: ndvi-processor
- **URL**: http://ndvi-processor:8118
- **Route Name**: ndvi-processor-route
- **Paths**: `/api/v1/ndvi-processor`
- **Methods**: Not specified
- **Strip Path**: false ✅
- **Plugins**: JWT, ACL (professional/enterprise), Rate Limiting (1000/min)
- **Status**: ✅ Properly configured

#### ✅ mcp-server

- **Service Name**: mcp-server
- **Upstream**: mcp-server-upstream → mcp-server:8200
- **Route Name**: mcp-server-route
- **Paths**: `/api/v1/mcp`
- **Methods**: Not specified
- **Strip Path**: false ✅
- **Plugins**: JWT, ACL (professional/enterprise/research), Rate Limiting (1000/min, 50000/hour)
- **Status**: ✅ Properly configured

#### ✅ code-review-service

- **Service Name**: code-review-service
- **Upstream**: code-review-upstream → code-review-service:8096
- **Route Name**: code-review-route
- **Paths**: `/api/v1/code-review`
- **Methods**: Not specified
- **Strip Path**: false ✅
- **Plugins**: JWT, ACL (enterprise/research), Rate Limiting (500/min, 10000/hour)
- **Status**: ✅ Properly configured

---

### 2.5 Health Check Service

#### ✅ health-check

- **Service Name**: health-check
- **URL**: http://kong:8000
- **Route Name**: health-route
- **Paths**:
  - `/health`
  - `/ping`
- **Methods**: GET
- **Strip Path**: false ✅
- **Plugins**: Request Termination (200 OK)
- **Status**: ✅ Properly configured

---

## 3. Missing Routes

### Services Without Kong Routes (17 services)

| Service Name             | Directory Exists | Port (from service-registry) | Reason                                           |
| ------------------------ | ---------------- | ---------------------------- | ------------------------------------------------ |
| user-service             | ✅               | N/A                          | Missing - Critical service                       |
| agent-registry           | ✅               | N/A                          | Missing - Support service                        |
| ai-agents-core           | ✅               | N/A                          | Missing - Core AI service                        |
| globalgap-compliance     | ✅               | N/A                          | Missing - Compliance service                     |
| yield-prediction-service | ✅               | 8098                         | Has `yield-engine` route but not direct route    |
| crop-health              | ✅               | N/A                          | Deprecated, replaced by crop-health-ai           |
| agro-rules               | ✅               | N/A                          | Deprecated, NATS worker                          |
| agro-advisor             | ✅               | 8105                         | Deprecated, has legacy route in advisory-service |
| weather-core             | ✅               | 8108                         | Deprecated, replaced by weather-advanced         |
| ndvi-engine (directory)  | ✅               | 8107                         | Deprecated, has route as ndvi-processor          |
| field-core (directory)   | ✅               | 3000                         | Has route but directory separate                 |
| shared                   | ✅               | N/A                          | Not a service, shared libraries                  |
| demo-data                | ✅               | N/A                          | Utility service, not API service                 |

### Critical Missing Services

#### 🔴 user-service

- **Status**: Active service directory exists
- **Impact**: HIGH - Authentication and user management
- **Recommendation**: Add Kong route immediately
- **Suggested Configuration**:
  ```yaml
  - name: user-service
    url: http://user-service:8100
    routes:
      - name: user-route
        paths:
          - /api/v1/users
          - /api/v1/auth
        strip_path: false
    plugins:
      - name: rate-limiting
        config:
          minute: 2000
      - name: cors
  ```

#### 🟡 globalgap-compliance

- **Status**: Active service directory exists
- **Impact**: MEDIUM - Compliance tracking
- **Recommendation**: Add Kong route if service is active
- **Suggested Path**: `/api/v1/compliance` or `/api/v1/globalgap`

#### 🟡 ai-agents-core

- **Status**: Active service directory exists
- **Impact**: MEDIUM - AI agent orchestration
- **Recommendation**: Add Kong route or clarify if internal-only service

---

## 4. Duplicate and Conflicting Routes

### Path Conflicts

#### ⚠️ Conflict 1: NDVI Endpoints

- **Path**: `/api/v1/ndvi`
- **Service 1**: ndvi-engine → http://ndvi-processor:8118
- **Service 2**: satellite-service route includes ndvi in HA config
- **Resolution**: Main config uses separate routes, HA config combines them
- **Status**: Potential conflict in HA setup

#### ⚠️ Conflict 2: Field Management Services

- **Services pointing to same backend**:
  - field-core → field-management-service:3000 (`/api/v1/fields`, `/api/v1/field-core`)
  - field-ops → field-management-service:3000 (`/api/v1/field-ops`)
  - field-service → field-management-service:3000 (`/api/v1/field-service`)
- **Status**: Multiple routes to same service - acceptable for migration but creates confusion
- **Recommendation**: Consolidate to single service name after deprecation period

#### ⚠️ Conflict 3: Yield Services

- **Path Similarity**: `/api/v1/yield` vs `/api/v1/yield-prediction`
- **Service 1**: yield-engine → yield-prediction-service:8098 (`/api/v1/yield`)
- **Service 2**: yield-prediction → yield-prediction:3021 (`/api/v1/yield-prediction`)
- **Status**: Different services, different paths - OK but may confuse users
- **Recommendation**: Document the difference clearly

---

## 5. Route Naming Convention Analysis

### Naming Pattern Analysis

✅ **Consistent Patterns**:

- Service names use kebab-case: `field-management`, `weather-service`, `satellite-service`
- Route names follow pattern: `{service}-route` (e.g., `field-core-route`, `weather-route`)
- Path prefixes consistent: All use `/api/v1/` prefix

✅ **Good Practices**:

- strip_path consistently set to `false` across all routes
- All routes use proper HTTP methods or default to all
- Timeout values appropriate for service type (longer for AI/computation services)

⚠️ **Inconsistencies**:

1. **Health Check Paths**: Most services use `/healthz` but mcp-server and code-review use `/health`
2. **Service Definition**: Mix of `url:` (direct) and `host:` (upstream) - both work but inconsistent
3. **Method Specification**: Some routes specify methods explicitly, others rely on defaults

---

## 6. Deprecated Service Routes

### Services with Active Routes but Marked Deprecated

| Service Name               | Route Path                             | Replacement Service | Deprecation Date | Removal Date | Risk                        |
| -------------------------- | -------------------------------------- | ------------------- | ---------------- | ------------ | --------------------------- |
| iot-gateway                | /api/v1/iot, /api/v1/agro-rules        | iot-service         | 2025-12          | 2026-03      | 🔴 HIGH                     |
| field-ops                  | /api/v1/field-ops                      | field-service       | 2025-12          | 2026-03      | 🟡 MEDIUM                   |
| field-chat                 | /api/v1/field/chat, /api/v1/field-chat | community-chat      | 2025-12          | 2026-03      | 🟡 MEDIUM                   |
| equipment-service          | /api/v1/equipment                      | field-service       | 2025-12          | 2026-03      | 🟡 MEDIUM                   |
| task-service               | /api/v1/tasks                          | field-service       | 2025-12          | 2026-03      | 🟡 MEDIUM                   |
| provider-config            | /api/v1/providers                      | billing-core        | 2025-12          | 2026-03      | 🟡 MEDIUM                   |
| agro-advisor (legacy path) | /api/v1/agro-advisor                   | advisory-service    | 2025-12          | 2026-03      | 🟢 LOW (has migration path) |
| weather-advanced           | /api/v1/weather/advanced               | weather-service     | 2025-12          | 2026-03      | 🟢 LOW (consolidated)       |
| fertilizer-advisor         | /api/v1/fertilizer                     | advisory-service    | 2025-12          | 2026-03      | 🟢 LOW (has migration)      |

### Recommendations for Deprecated Routes

1. **Immediate Actions** (Before 2026-03):
   - Add deprecation headers to responses from deprecated routes
   - Update API documentation to highlight deprecations
   - Add logging for deprecated route usage to track adoption

2. **Migration Headers** (Add to deprecated route plugins):

   ```yaml
   - name: response-transformer
     config:
       add:
         headers:
           - "X-API-Deprecated: true"
           - "X-API-Sunset: 2026-03-01"
           - "X-API-Replacement: /api/v1/{new-path}"
           - 'Link: </api/v1/{new-path}>; rel="successor-version"'
   ```

3. **Monitoring**:
   - Track usage metrics for all deprecated routes
   - Alert when usage doesn't decrease month-over-month
   - Prepare migration guides for remaining clients

---

## 7. Plugin Configuration Analysis

### Rate Limiting Tiers

| Tier         | Services    | Rate (per minute) | Rate (per hour)           | Redis Configured |
| ------------ | ----------- | ----------------- | ------------------------- | ---------------- |
| Starter      | 5 services  | 100               | 5,000 (field-core only)   | ✅ Yes           |
| Professional | 11 services | 1,000             | N/A (most)                | ✅ Yes           |
| Enterprise   | 9 services  | 10,000            | 500,000 (ai-advisor only) | ✅ Yes           |
| Special      | code-review | 500               | 10,000                    | ✅ Yes           |

### Security Plugins

✅ **All routes have**:

- JWT authentication
- ACL (role-based access)
- Rate limiting with Redis backend
- Fault-tolerant Redis connection

✅ **Enhanced security routes**:

- **IP Restriction** (internal only):
  - iot-gateway
  - research-core
  - marketplace-service
  - billing-core
  - disaster-assessment
- **Request Size Limiting**:
  - field-core (10MB)
  - satellite-service (50MB)
  - crop-health-ai (25MB)
  - ai-advisor (50MB)

### Global Plugins

✅ **Active Global Plugins**:

1. **CORS** - Properly configured with allowed origins
2. **File Logging** - /var/log/kong/access.log
3. **Prometheus** - Metrics collection enabled
4. **Response Transformer** - Security headers (CSP, HSTS, X-Frame-Options, etc.)
5. **Correlation ID** - Request tracing (X-Request-ID)

---

## 8. Configuration File Discrepancies

### Main Configuration vs HA Configuration

| Aspect             | Main Config  | HA Config       | Status                |
| ------------------ | ------------ | --------------- | --------------------- |
| Format Version     | 3.0          | 3.0             | ✅ Match              |
| Total Services     | 37           | 8               | ⚠️ Different          |
| Upstreams          | 15 upstreams | 0 (direct URLs) | ⚠️ Different          |
| Rate Limit Backend | Redis        | Local           | 🔴 Incompatible       |
| Authentication     | JWT + ACL    | None configured | 🔴 Security Gap       |
| Health Checks      | Detailed     | Basic           | ⚠️ Less comprehensive |

### Issues Found

1. **🔴 CRITICAL**: HA configuration missing JWT authentication
2. **🔴 CRITICAL**: HA configuration uses local rate limiting (not shared across instances)
3. **⚠️ WARNING**: HA configuration only has 8 services vs 37 in main config
4. **⚠️ WARNING**: Port numbers differ between main and HA configs for same services

### Recommendation

- HA configuration appears to be for a different deployment scenario (possibly testing/development)
- Should either be updated to match main config or clearly labeled as legacy/alternative config
- **DO NOT use HA config in production without adding authentication and shared rate limiting**

---

## 9. Port Number Analysis

### Port Assignments

| Port | Service                     | Status        | Notes                               |
| ---- | --------------------------- | ------------- | ----------------------------------- |
| 3000 | field-management-service    | ✅ Active     | Multiple routes point here          |
| 3010 | marketplace-service         | ✅ Active     |                                     |
| 3015 | research-core               | ✅ Active     |                                     |
| 3020 | disaster-assessment         | ✅ Active     |                                     |
| 3021 | yield-prediction            | ✅ Active     |                                     |
| 3022 | lai-estimation              | ✅ Active     |                                     |
| 3023 | crop-growth-model           | ✅ Active     |                                     |
| 8081 | ws-gateway                  | ✅ Active     | Changed from 8089 to avoid conflict |
| 8089 | billing-core                | ✅ Active     |                                     |
| 8090 | vegetation-analysis-service | ✅ Active     |                                     |
| 8091 | indicators-service          | ✅ Active     |                                     |
| 8092 | weather-service             | ✅ Active     |                                     |
| 8093 | advisory-service            | ✅ Active     |                                     |
| 8094 | irrigation-smart            | ✅ Active     |                                     |
| 8095 | crop-intelligence-service   | ✅ Active     |                                     |
| 8096 | code-review-service         | ✅ Active     |                                     |
| 8097 | community-chat              | ✅ Active     |                                     |
| 8098 | yield-prediction-service    | ✅ Active     |                                     |
| 8099 | field-chat                  | ⚠️ Deprecated |                                     |
| 8101 | equipment-service           | ⚠️ Deprecated |                                     |
| 8103 | task-service                | ⚠️ Deprecated |                                     |
| 8104 | provider-config             | ⚠️ Deprecated |                                     |
| 8105 | agro-advisor                | ⚠️ Deprecated |                                     |
| 8106 | iot-gateway                 | ⚠️ Deprecated |                                     |
| 8110 | notification-service        | ✅ Active     |                                     |
| 8111 | astronomical-calendar       | ✅ Active     |                                     |
| 8112 | ai-advisor                  | ✅ Active     |                                     |
| 8113 | alert-service               | ✅ Active     |                                     |
| 8114 | chat-service                | ✅ Active     |                                     |
| 8116 | inventory-service           | ✅ Active     |                                     |
| 8117 | iot-service                 | ✅ Active     |                                     |
| 8118 | ndvi-processor              | ✅ Active     |                                     |
| 8119 | virtual-sensors             | ✅ Active     |                                     |
| 8120 | field-intelligence          | ✅ Active     |                                     |
| 8200 | mcp-server                  | ✅ Active     |                                     |

### Port Conflicts

- ✅ No port conflicts detected
- ⚠️ Port 8089 conflict resolved (ws-gateway moved to 8081)

---

## 10. Regex Priority Analysis

### Current State

- ❌ **No regex priorities configured** - All routes rely on exact path matching
- ✅ All paths are non-overlapping, so priority is not critical
- ⚠️ Some services have multiple paths which could benefit from priority ordering

### Routes That Could Benefit from Regex Priority

1. **field-core-route**:
   - `/api/v1/fields` (more specific)
   - `/api/v1/field-core` (less specific)
   - Recommended priority: Should prioritize longer/more specific paths first

2. **advisory-route**:
   - `/api/v1/advice`
   - `/api/v1/advisory`
   - `/api/v1/agro-advisor` (legacy)
   - Recommended priority: Order by specificity

3. **field-intelligence-route**:
   - `/api/v1/field-intelligence` (more specific)
   - `/api/v1/intelligence` (less specific)
   - Recommended: Priority on more specific path

### Recommendation

- Current configuration is safe without regex priority since paths don't overlap
- Consider adding `regex_priority` if you plan to add wildcard or regex routes in future
- Document route matching order in API documentation

---

## 11. Best Practices Compliance

### ✅ Following Best Practices

1. **Strip Path Configuration**: All routes consistently use `strip_path: false`
2. **Timeout Configuration**: Appropriate timeouts for service types
3. **Retry Logic**: Services have retry counts (2-3 retries)
4. **Health Checks**: All upstreams have active health checks configured
5. **Rate Limiting**: Tier-based rate limiting implemented
6. **Authentication**: JWT on all routes except health check
7. **Authorization**: ACL plugin ensures role-based access
8. **Monitoring**: Prometheus plugin enabled globally
9. **Tracing**: Correlation ID for request tracking
10. **Security Headers**: CSP, HSTS, X-Frame-Options configured globally

### ⚠️ Areas for Improvement

1. **Method Specification**: Many routes don't specify allowed HTTP methods
   - Recommendation: Explicitly define methods for all routes

2. **Request Size Limits**: Only 4 services have request size limits
   - Recommendation: Add appropriate limits to all routes

3. **Response Transformation**: Only 2 services use response transformation
   - Recommendation: Standardize response headers across all services

4. **Circuit Breaker**: Not configured on any routes
   - Recommendation: Add circuit breaker plugin for external dependencies

5. **Caching**: No caching plugins configured
   - Recommendation: Add proxy-cache for GET requests on read-heavy services

6. **Request/Response Validation**: No schema validation configured
   - Recommendation: Consider adding request-validator plugin for critical services

---

## 12. Recommendations

### Immediate Actions (Priority 1 - Critical)

1. **Add user-service route** - Critical missing service for authentication
2. **Update HA configuration** - Add JWT and shared Redis rate limiting
3. **Add deprecation headers** - Inform clients about deprecated routes
4. **Remove iot-gateway upstream** - Service is deprecated, cleanup configuration

### Short-term Actions (Priority 2 - High)

1. **Consolidate field management routes** - Reduce confusion with multiple routes to same backend
2. **Add HTTP method specifications** - Improve security and clarity
3. **Implement request size limits** - Protect against large payload attacks
4. **Add circuit breaker plugin** - Improve resilience for AI and external services
5. **Document missing services** - Clarify which services in apps/services are not API services

### Medium-term Actions (Priority 3 - Medium)

1. **Implement caching strategy** - Add proxy-cache for appropriate routes
2. **Add request validation** - Validate request schemas for critical endpoints
3. **Standardize health check paths** - All services should use either /health or /healthz
4. **Review and optimize timeouts** - Based on actual service performance metrics
5. **Implement service mesh** - Consider Kong Service Mesh for advanced features

### Long-term Actions (Priority 4 - Low)

1. **Implement API versioning strategy** - Prepare for v2 API paths
2. **Add GraphQL gateway** - For complex query requirements
3. **Implement rate limiting per endpoint** - More granular control than service-level
4. **Add WAF plugin** - Web Application Firewall for advanced threat protection

---

## 13. Configuration Quality Score

### Overall Score: 7.5/10

**Breakdown**:

- ✅ **Route Configuration**: 9/10 - Well structured, consistent
- ✅ **Security**: 8/10 - Good JWT/ACL, missing some request validation
- ✅ **Performance**: 7/10 - Good timeouts/retries, missing caching
- ⚠️ **Completeness**: 6/10 - Missing critical services (user-service)
- ⚠️ **Maintainability**: 7/10 - Deprecated routes need cleanup
- ✅ **Monitoring**: 9/10 - Excellent observability setup
- ⚠️ **HA Readiness**: 5/10 - HA config needs significant work
- ✅ **Documentation**: 8/10 - Well commented configuration files

### Key Strengths

1. Comprehensive rate limiting with Redis backend
2. Excellent security baseline (JWT, ACL, IP restrictions)
3. Good timeout and retry configurations
4. Strong observability (Prometheus, correlation IDs, logging)
5. Consistent naming conventions

### Key Weaknesses

1. Missing critical service routes (user-service)
2. HA configuration significantly behind main config
3. No caching strategy implemented
4. Deprecated services still have active routes
5. No circuit breaker for resilience

---

## 14. Summary

This Kong configuration represents a **well-architected API gateway** for a complex microservices platform with **37 services** configured across **starter, professional, and enterprise** tiers. The configuration demonstrates strong security practices with JWT authentication, role-based access control, and tier-based rate limiting.

**Critical items requiring immediate attention**:

1. Add user-service route (authentication is critical)
2. Update HA configuration security
3. Plan deprecation migration for 9 deprecated routes

**Overall assessment**: The configuration is production-ready for the main deployment but requires attention to missing services and deprecated route cleanup before the March 2026 deprecation deadline.

---

**Report Generated**: 2026-01-06
**Audited By**: Kong Configuration Audit Tool
**Configuration Version**: 15.5.0
