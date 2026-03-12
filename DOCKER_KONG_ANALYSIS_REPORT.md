# SAHOOL v16.0.0 Docker & Kong Analysis Report

**Generated:** 2026-02-02
**Analyst:** Claude (Senior SRE / Full-Stack Architect)
**Platform:** SAHOOL National Agricultural Intelligence Platform

---

## Executive Summary

This report provides a comprehensive analysis of the SAHOOL platform's Docker infrastructure and Kong API Gateway configuration. Critical issues have been identified including **port conflicts**, **Kong configuration mismatches**, and **runtime errors** that require immediate attention.

### Key Findings
- **2 Critical Port Conflicts** in docker-compose.yml
- **11 Kong Port Mismatches** between kong.yaml and docker-compose.yml
- **4 Runtime Errors** identified in api.logs
- **10 Deprecated Services** identified with migration paths
- **62 Active Services** + Infrastructure

---

## 1. System Topology Map

### 1.1 Infrastructure Services (14)

| Service | Port | Health Status | Notes |
|---------|------|---------------|-------|
| postgres | 5432 | Healthy | PostGIS 16-3.4 |
| pgbouncer | 6432 | Healthy | Connection pooler (250 max connections) |
| redis | 6379 | Healthy | Redis 7.4-alpine |
| vault | 8200 | Healthy | HashiCorp Vault 1.17 |
| nats | 4222 | Healthy | NATS 2.10.24 with JetStream |
| nats-prometheus-exporter | 7777 | Healthy | Metrics exporter |
| mlflow | 5000 | Warning | pip install errors |
| mqtt | 1883 | Healthy | Eclipse Mosquitto 2 |
| qdrant | 6333 | Healthy | Qdrant v1.7.4 |
| etcd | 2379 | Healthy | etcd v3.5.5 |
| minio | 9000 | Healthy | MinIO object storage |
| milvus | 19530 | Healthy | Milvus v2.5.27 |
| kong | 8000 | Healthy | Kong 3.4 (DB-less mode) |
| ollama | 11434 | GPU Profile | Requires NVIDIA runtime |

### 1.2 Node.js Services (12)

| Service | Port | Status | Replacement |
|---------|------|--------|-------------|
| field-management-service | 3000 | Active | - |
| marketplace-service | 3010 | Active | - |
| research-core | 3015 | Active | - |
| disaster-assessment | 3020 | Warning | Prisma errors |
| user-service | 3025 | Active | - |
| chat-service | 8114 | Active | - |
| iot-service | 8117 | Active | - |
| ground-vision-service | 8182 | Active | Requires GPU |
| yield-prediction | 3021 | **DEPRECATED** | yield-prediction-service |
| lai-estimation | 3022 | **DEPRECATED** | vegetation-analysis-service |
| crop-growth-model | 3023 | **DEPRECATED** | crop-intelligence-service |
| community-chat | 8097 | **DEPRECATED** | chat-service |

### 1.3 Python Services (48)

| Service | Port | Status | Notes |
|---------|------|--------|-------|
| ws-gateway | 8081 | Active | WebSocket gateway |
| billing-core | 8089 | Active | - |
| vegetation-analysis-service | 8090 | Active | Unified satellite/vegetation |
| indicators-service | 8091 | Active | - |
| weather-service | 8092 | Active | Unified weather |
| advisory-service | 8093 | Active | Unified advisory |
| irrigation-smart | 8094 | Active | - |
| crop-intelligence-service | 8095 | Active | Unified crop analysis |
| field-chat | 8099 | Warning | DB scheme error |
| equipment-service | 8101 | Warning | Migration error |
| task-service | 8103 | Active | - |
| provider-config | 8104 | Active | - |
| iot-gateway | 8106 | Active | - |
| notification-service | 8110 | Active | - |
| astronomical-calendar | 8111 | Active | - |
| ai-advisor | 8112 | Active | - |
| alert-service | 8113 | Active | - |
| inventory-service | 8116 | Active | - |
| ndvi-processor | 8118 | **DEPRECATED** | vegetation-analysis-service |
| virtual-sensors | 8119 | Active | - |
| **field-intelligence** | **8120** | **CONFLICT** | Port shared with globalgap |
| skills-service | 8121 | Active | - |
| audit-service | 8122 | Active | - |
| traceability-service | 8123 | Active | - |
| soil-analysis-service | 8124 | Active | - |
| pest-detection-service | 8125 | Active | - |
| drone-service | 8126 | Active | - |
| cooperative-service | 8127 | Active | - |
| ai-agents-service | 8130 | Active | - |
| crm-service | 8131 | Active | - |
| lowcode-engine | 8132 | Active | - |
| wechat-service | 8133 | Active | - |
| yolo26-vision-service | 8150 | Active | Requires GPU |
| yield-prediction-service | 8152 | Active | - |
| agent-registry | 8160 | Active | - |
| ai-agents-core | 8161 | Active | - |
| code-fix-agent | 8162 | Active | - |
| copilot-api | 8163 | Active | - |
| llm-orchestrator-service | 8164 | Active | - |
| **knowledge-graph** | **8165** | **CONFLICT** | Port shared with hydrology |
| supply-chain-service | 8166 | Active | - |
| logistics-service | 8167 | Active | - |
| leveling-optimizer-service | 8170 | Active | - |
| terrain-core-service | 8185 | Active | - |
| edge-orchestrator-service | 8180 | Active | - |
| mcp-server | 8201 | Active | - |
| **hydrology-service** | **8165** | **CONFLICT** | Port shared with knowledge-graph |
| **globalgap-compliance** | **8120** | **CONFLICT** | Port shared with field-intelligence |

### 1.4 Deprecated Services (Profile Required)

| Service | Port | Profile | Replacement |
|---------|------|---------|-------------|
| field-ops | 8080 | deprecated | field-management-service |
| agro-advisor | 8105 | deprecated, legacy | advisory-service |
| ndvi-engine | 8107 | deprecated, legacy | vegetation-analysis-service |
| weather-core | 8108 | deprecated, legacy | weather-service |
| crop-health | 8100 | deprecated, legacy | crop-intelligence-service |

---

## 2. Critical Issues

### 2.1 Port Conflicts in docker-compose.yml

**CRITICAL: Two pairs of services are configured to use the same ports!**

#### Conflict 1: Port 8165
```
hydrology-service:    PORT=8165  (line 3999)
knowledge-graph:      PORT=8165  (line 3430)
```

**Fix Required:** Change knowledge-graph to port 8140

#### Conflict 2: Port 8120
```
field-intelligence:      PORT=8120  (line 2539)
globalgap-compliance:    PORT=8120  (line 3570)
```

**Fix Required:** Change globalgap-compliance to port 8168

### 2.2 Kong Configuration Port Mismatches

The following services have incorrect ports in kong.yaml:

| Service | Kong Port | Docker Port | Fix |
|---------|-----------|-------------|-----|
| audit-service | 8114 | 8122 | Change to 8122 |
| agent-registry | 8185 | 8160 | Change to 8160 |
| ai-agents-core | 8122 | 8161 | Change to 8161 |
| knowledge-graph | 8140 | 8165 → 8140 | Keep 8140 (docker needs fix) |
| globalgap-compliance | 8123 | 8120 → 8168 | Change to 8168 |
| copilot-api | 8210 | 8163 | Change to 8163 |
| llm-orchestrator-service | 8220 | 8164 | Change to 8164 |
| supply-chain-service | 8230 | 8166 | Change to 8166 |
| traceability-service | 8156 | 8123 | Change to 8123 |
| logistics-service | 8162 | 8167 | Change to 8167 |
| code-fix-agent | 8161 | 8162 | Change to 8162 |

### 2.3 Runtime Errors from api.logs

#### Error 1: field-chat Database Scheme
```
sahool-field-chat | Database connection failed (running without DB): Unknown DB scheme: postgresql+asyncpg
```
**Cause:** field-chat uses `postgresql+asyncpg://` scheme but the service may not support asyncpg.
**Status:** Service running without database (degraded mode)

#### Error 2: disaster-assessment Prisma Migration
```
sahool-disaster-assessment | Error: P3005
sahool-disaster-assessment | Migration failed, continuing anyway...
```
**Cause:** Prisma migration issue, possibly schema mismatch.
**Status:** Service running but may have data integrity issues.

#### Error 3: equipment-service Migration
```
sahool-equipment-service | Migration check failed (non-fatal): foreign key constraint "equipment_maintenance_equipment_id_fkey" cannot be implemented
```
**Cause:** Foreign key constraint issue during migration.
**Status:** Service running with potential constraint violations.

#### Error 4: mlflow pip Install
```
sahool-mlflow | WARNING: Retrying after connection broken: Failed to establish a new connection
```
**Cause:** Network connectivity during pip install of psycopg2-binary.
**Status:** Service may have delayed startup but should recover.

---

## 3. Dependency Analysis

### 3.1 Correct Dependencies (Verified)

All services properly depend on infrastructure with `service_healthy` conditions:
- pgbouncer depends on postgres
- All application services depend on pgbouncer (not postgres directly)
- Services requiring NATS have nats dependency
- Services requiring Redis have redis dependency

### 3.2 Dependency Chain Issues

1. **user-service** depends on `notification-service` - creates circular startup dependency risk
2. **ai-advisor** depends on 5 services - long dependency chain may cause timeout

---

## 4. Recommended Fixes

### 4.1 Docker Compose Fixes

#### Fix 1: Resolve Port 8165 Conflict
Change knowledge-graph to port 8140:

```yaml
# knowledge-graph service (around line 3430)
knowledge-graph:
  environment:
    - PORT=8140  # Changed from 8165
  ports:
    - "8140:8140"  # Changed from 8165:8165
```

#### Fix 2: Resolve Port 8120 Conflict
Change globalgap-compliance to port 8168:

```yaml
# globalgap-compliance service (around line 3570)
globalgap-compliance:
  environment:
    - PORT=8168  # Changed from 8120
  ports:
    - "8168:8168"  # Changed from 8120:8120
```

#### Fix 3: Increase start_period for Heavy Services
For services with ML models or heavy initialization:

```yaml
# terrain-core-service (already has 90s - good)
# milvus (already has 90s - good)
# iot-gateway (already has 90s - good)
```

### 4.2 Kong Configuration Fixes

See Section 5 for complete kong.yaml corrections.

---

## 5. Kong Configuration Corrections

The following service port mappings need to be corrected in `infrastructure/gateway/kong/kong.yml`:

### Services Requiring Port Fixes:

```yaml
# audit-service - Line ~598
- name: audit-service
  host: audit-service
  port: 8122  # Fixed from 8114

# agent-registry - Line ~686
- name: agent-registry
  host: agent-registry
  port: 8160  # Fixed from 8185

# ai-agents-core - Line ~697
- name: ai-agents-core
  host: ai-agents-core
  port: 8161  # Fixed from 8122

# knowledge-graph - Line ~708
- name: knowledge-graph
  host: knowledge-graph
  port: 8140  # Matches docker-compose fix

# globalgap-compliance - Line ~653
- name: globalgap-compliance
  host: globalgap-compliance
  port: 8168  # Matches docker-compose fix

# copilot-api - Line ~824
- name: copilot-api
  host: copilot-api
  port: 8163  # Fixed from 8210

# llm-orchestrator-service - Line ~846
- name: llm-orchestrator-service
  host: llm-orchestrator-service
  port: 8164  # Fixed from 8220

# supply-chain-service - Line ~913
- name: supply-chain-service
  host: supply-chain-service
  port: 8166  # Fixed from 8230

# traceability-service - Line ~932
- name: traceability-service
  host: traceability-service
  port: 8123  # Fixed from 8156

# logistics-service - Line ~664
- name: logistics-service
  host: logistics-service
  port: 8167  # Fixed from 8162

# code-fix-agent - Line ~802
- name: code-fix-agent
  host: code-fix-agent
  port: 8162  # Fixed from 8161
```

---

## 6. GPU Services Considerations

The following services require NVIDIA GPU runtime:

| Service | Profile | Fallback |
|---------|---------|----------|
| ollama | gpu | Not available without GPU |
| ollama-model-loader | gpu | N/A (loader only) |
| code-review-service | gpu | Not available without GPU |
| yolo26-vision-service | (none) | Will fail without GPU |
| ground-vision-service | (none) | Will fail without GPU |

**Recommendation:** Add proper error handling for GPU services when GPU is not available, or add them to the `gpu` profile.

---

## 7. Network Configuration

### 7.1 Network Status
- All services correctly use `sahool-network` (bridge driver)
- Kong uses Docker internal DNS resolver (127.0.0.11)
- DNS cache TTL set to 300s for stability

### 7.2 Port Binding Security
- Infrastructure ports (5432, 6379, 4222, etc.) bound to 127.0.0.1 only
- Kong proxy port (8000) exposed externally
- Kong admin port (8001) bound to 127.0.0.1 only

---

## 8. Action Items

### Immediate (P0)
1. [ ] Fix port 8165 conflict (knowledge-graph → 8140)
2. [ ] Fix port 8120 conflict (globalgap-compliance → 8168)
3. [ ] Update kong.yaml with corrected ports (11 services)

### High Priority (P1)
4. [ ] Investigate field-chat database scheme issue
5. [ ] Resolve disaster-assessment Prisma migration
6. [ ] Fix equipment-service foreign key constraint

### Medium Priority (P2)
7. [ ] Add GPU services to `gpu` profile
8. [ ] Review ai-advisor dependency chain (5 services)
9. [ ] Consider removing deprecated services from non-profile builds

### Low Priority (P3)
10. [ ] Update mlflow startup to handle network delays
11. [ ] Add health endpoint monitoring dashboard
12. [ ] Document service deprecation timeline

---

## Appendix A: Complete Port Mapping

| Port | Service | Type |
|------|---------|------|
| 3000 | field-management-service | Node.js |
| 3010 | marketplace-service | Node.js |
| 3015 | research-core | Node.js |
| 3020 | disaster-assessment | Node.js |
| 3021 | yield-prediction (deprecated) | Node.js |
| 3022 | lai-estimation (deprecated) | Node.js |
| 3023 | crop-growth-model (deprecated) | Node.js |
| 3025 | user-service | Node.js |
| 4222 | nats | Infrastructure |
| 5000 | mlflow | Infrastructure |
| 5432 | postgres | Infrastructure |
| 6333 | qdrant | Infrastructure |
| 6379 | redis | Infrastructure |
| 6432 | pgbouncer | Infrastructure |
| 7777 | nats-prometheus-exporter | Infrastructure |
| 8000 | kong | API Gateway |
| 8080 | field-ops (deprecated) | Python |
| 8081 | ws-gateway | Python |
| 8089 | billing-core | Python |
| 8090 | vegetation-analysis-service | Python |
| 8091 | indicators-service | Python |
| 8092 | weather-service | Python |
| 8093 | advisory-service | Python |
| 8094 | irrigation-smart | Python |
| 8095 | crop-intelligence-service | Python |
| 8097 | community-chat (deprecated) | Node.js |
| 8099 | field-chat | Python |
| 8100 | crop-health (deprecated) | Python |
| 8101 | equipment-service | Python |
| 8102 | code-review-service | Python |
| 8103 | task-service | Python |
| 8104 | provider-config | Python |
| 8105 | agro-advisor (deprecated) | Python |
| 8106 | iot-gateway | Python |
| 8107 | ndvi-engine (deprecated) | Python |
| 8108 | weather-core (deprecated) | Python |
| 8110 | notification-service | Python |
| 8111 | astronomical-calendar | Python |
| 8112 | ai-advisor | Python |
| 8113 | alert-service | Python |
| 8114 | chat-service | Node.js |
| 8116 | inventory-service | Python |
| 8117 | iot-service | Node.js |
| 8118 | ndvi-processor | Python |
| 8119 | virtual-sensors | Python |
| 8120 | field-intelligence | Python |
| 8121 | skills-service | Python |
| 8122 | audit-service | Python |
| 8123 | traceability-service | Python |
| 8124 | soil-analysis-service | Python |
| 8125 | pest-detection-service | Python |
| 8126 | drone-service | Python |
| 8127 | cooperative-service | Python |
| 8130 | ai-agents-service | Python |
| 8131 | crm-service | Python |
| 8132 | lowcode-engine | Python |
| 8133 | wechat-service | Python |
| 8140 | knowledge-graph (FIXED) | Python |
| 8150 | yolo26-vision-service | Python |
| 8152 | yield-prediction-service | Python |
| 8160 | agent-registry | Python |
| 8161 | ai-agents-core | Python |
| 8162 | code-fix-agent | Python |
| 8163 | copilot-api | Python |
| 8164 | llm-orchestrator-service | Python |
| 8165 | hydrology-service | Python |
| 8166 | supply-chain-service | Python |
| 8167 | logistics-service | Python |
| 8168 | globalgap-compliance (FIXED) | Python |
| 8170 | leveling-optimizer-service | Python |
| 8182 | ground-vision-service | Python |
| 8185 | terrain-core-service | Python |
| 8190 | edge-orchestrator-service | Python |
| 8200 | vault | Infrastructure |
| 8201 | mcp-server | Python |
| 9000 | minio | Infrastructure |
| 11434 | ollama | Infrastructure |
| 19530 | milvus | Infrastructure |

---

*Report generated by Claude Senior SRE Analysis*
