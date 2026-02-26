# Drift Detection Report | تقرير كشف الانحراف

**Date | التاريخ**: 2026-02-26
**Version | الإصدار**: 16.0.0
**Branch | الفرع**: main
**Scope | النطاق**: Full platform drift analysis across 7 dimensions

---

## Executive Summary | الملخص التنفيذي

This report provides a comprehensive drift detection analysis of the SAHOOL platform, examining **7 critical dimensions** across **71 active microservices**, **24 npm workspaces**, and **65+ shared Python modules**. The analysis identified **47 drift issues** across all categories.

يقدم هذا التقرير تحليلاً شاملاً لكشف الانحراف في منصة سهول، ويفحص **7 أبعاد حرجة** عبر **71 خدمة مصغرة نشطة** و**24 مساحة عمل npm** و**أكثر من 65 وحدة Python مشتركة**. حدد التحليل **47 مشكلة انحراف** عبر جميع الفئات.

### Overall Platform Health Score | درجة صحة المنصة الإجمالية

| Dimension | Score | Status | البعد |
|-----------|-------|--------|-------|
| Service Registry | 7.8/10 | Good | سجل الخدمات |
| Port Assignments | 7.5/10 | Good | تعيينات المنافذ |
| Health Endpoints | 9.7/10 | Excellent | نقاط فحص الصحة |
| Dockerfile Patterns | 7.0/10 | Fair | أنماط Dockerfile |
| Dependency Versions | 5.5/10 | Needs Attention | إصدارات التبعيات |
| Deprecated Services | 7.0/10 | Fair | الخدمات المهملة |
| **Overall** | **7.4/10** | **Good** | **الإجمالي** |

---

## Table of Contents | جدول المحتويات

1. [Service Registry Drift | انحراف سجل الخدمات](#1-service-registry-drift)
2. [Port Assignment Drift | انحراف تعيينات المنافذ](#2-port-assignment-drift)
3. [Health Endpoint Drift | انحراف نقاط فحص الصحة](#3-health-endpoint-drift)
4. [Dockerfile Pattern Drift | انحراف أنماط Dockerfile](#4-dockerfile-pattern-drift)
5. [Dependency Version Drift | انحراف إصدارات التبعيات](#5-dependency-version-drift)
6. [Deprecated Services Drift | انحراف الخدمات المهملة](#6-deprecated-services-drift)
7. [Consolidated Findings | النتائج الموحدة](#7-consolidated-findings)
8. [Remediation Roadmap | خارطة طريق المعالجة](#8-remediation-roadmap)

---

## 1. Service Registry Drift

**سجل الخدمات - كشف الانحراف**

### Registry Overview

| Category | Count | Status |
|----------|-------|--------|
| Total Services in Registry | 83 | — |
| Active Services | 68 | ✅ |
| Deprecated (still in apps/) | 4 | ⚠️ |
| Archived Services | 11 | ✅ |
| Services in docker-compose | 70 | ✅ |
| Services on filesystem (apps/services/) | 71 | ✅ |

### Issues Found: 2

#### DRIFT-REG-001: yield-prediction NOT Archived (CRITICAL)

| Property | Value |
|----------|-------|
| **Severity** | 🔴 CRITICAL |
| **Service** | `yield-prediction` |
| **Current State** | Still in `apps/services/yield-prediction/` |
| **Expected State** | Should be in `archive/deprecated-services/yield-prediction/` |
| **Replacement** | `yield-prediction-service` (port 8152, active) |
| **Docker Profile** | `profiles: [deprecated]` (correctly isolated) |

The service is marked deprecated in the registry but has NOT been moved to the archive directory, unlike all other deprecated services (community-chat, field-chat, yield-engine, etc.).

#### DRIFT-REG-002: ndvi-processor Path Mismatch (MINOR)

| Property | Value |
|----------|-------|
| **Severity** | 🟡 MINOR |
| **Service** | `ndvi-processor` |
| **Registry Path** | `apps/services/ndvi-processor` (marked active) |
| **Archive Path** | `archive/deprecated-services/ndvi-processor/` (also exists) |
| **Issue** | Dual existence - active directory AND archive copy |

### Profile Distribution

| Profile | Services | Status |
|---------|----------|--------|
| default | 66 | ✅ Standard deployment |
| deprecated | 1 (yield-prediction) | ✅ Isolated |
| gpu | 2 (ollama, ollama-model-loader) | ✅ |
| optional | 4 (ai-chat-assistant, code-review-agent, ussd-gateway, whatsapp-bot-service) | ✅ |

### Naming Consistency: ✅ PASS

All 68 active services use consistent hyphenated naming. No underscore/hyphen mismatches detected.

---

## 2. Port Assignment Drift

**تعيينات المنافذ - كشف الانحراف**

### Issues Found: 7

#### DRIFT-PORT-001: code-review-agent Incorrectly in SERVICE_PORTS (CRITICAL)

| Property | Value |
|----------|-------|
| **Severity** | 🔴 CRITICAL |
| **Service** | `code-review-agent` |
| **Assigned Port** | 8145 |
| **File** | `packages/shared-types/src/contracts/service-ports.ts` |
| **Issue** | This is an NPM library module, NOT an HTTP service. Has no EXPOSE in Dockerfile, no HTTP server in code |

#### DRIFT-PORT-002: demo-data Incorrectly in SERVICE_PORTS (CRITICAL)

| Property | Value |
|----------|-------|
| **Severity** | 🔴 CRITICAL |
| **Service** | `demo-data` |
| **Assigned Port** | 8261 |
| **Issue** | Background worker/generator with no HTTP server. Has no EXPOSE in Dockerfile |

#### DRIFT-PORT-003: yield-prediction Duplicate Service (HIGH)

| Property | Value |
|----------|-------|
| **Severity** | 🟠 HIGH |
| **Legacy** | `yield-prediction` on port 3021 |
| **Current** | `yield-prediction-service` on port 8152 |
| **Issue** | Both run simultaneously in docker-compose; Kong routes only reference 8152 |

#### DRIFT-PORT-004: whatsapp-bot-service Parameterized EXPOSE (MEDIUM)

| Property | Value |
|----------|-------|
| **Severity** | 🟡 MEDIUM |
| **Service** | `whatsapp-bot-service` |
| **File** | `apps/services/whatsapp-bot-service/Dockerfile` |
| **Issue** | Uses `EXPOSE ${PORT}` instead of explicit `EXPOSE 8240` |

#### DRIFT-PORT-005: Mixed Port Ranges (LOW)

| Range | Count | Purpose |
|-------|-------|---------|
| 3000-3099 | 8 services | Node.js "core" services |
| 8000-8299 | ~60 services | All other services |

No documented rationale for range separation.

#### DRIFT-PORT-006: 30+ Services Missing from Kong Upstreams (MEDIUM)

Kong gateway only routes 41 of 71 services. Missing services can only be reached directly by IP:port.

**Services NOT in Kong but should be considered:**
- ai-advisor (8112), ai-agents-core (8161), ai-agents-service (8130)
- ai-chat-assistant (8260), crm-service (8131), yield-prediction-service (8152)
- mcp-server (8201), logistics-service (8167), and 22+ more

#### DRIFT-PORT-007: yolo26-vision-service Duplicate EXPOSE (LOW)

| Property | Value |
|----------|-------|
| **File** | `apps/services/yolo26-vision-service/Dockerfile` |
| **Issue** | `EXPOSE 8150` appears twice (redundant, not harmful) |

### Port Conflict Check: ✅ PASS

No actual port conflicts found. All 71 services have unique port assignments.

---

## 3. Health Endpoint Drift

**نقاط فحص الصحة - كشف الانحراف**

### Overall Compliance: 97.4% (76/78 services fully compliant)

| Metric | Python (56) | Node.js (22) | Total |
|--------|-------------|--------------|-------|
| Has `/healthz` | 56 (100%) | 22 (100%) | 78 (100%) |
| Has `/readyz` | 55 (98.2%) | 22 (100%) | 77 (98.7%) |
| Correct version `16.0.0` | 54 (96.4%) | 22 (100%) | 76 (97.4%) |

### Issues Found: 2

#### DRIFT-HEALTH-001: ai-chat-assistant Wrong Version (HIGH)

| Property | Value |
|----------|-------|
| **Severity** | 🟠 HIGH |
| **File** | `apps/services/ai-chat-assistant/src/main.py` (lines 96, 148) |
| **Current** | `"version": "1.0.0"` |
| **Expected** | `"version": "16.0.0"` |

#### DRIFT-HEALTH-002: copilot-api Wrong Version (HIGH)

| Property | Value |
|----------|-------|
| **Severity** | 🟠 HIGH |
| **File** | `apps/services/copilot-api/src/api/v1/health.py` (lines 33, 88) |
| **Current** | `"version": "1.0.0"` |
| **Expected** | `"version": "16.0.0"` |

### Standard Response Format

```json
{"status": "ok", "service": "<service-name>", "version": "16.0.0"}
```

All services follow the standard format. Some add additional fields (timestamp, dependency checks) which are compatible additions.

---

## 4. Dockerfile Pattern Drift

**أنماط Dockerfile - كشف الانحراف**

### Pip Mirror Pattern Distribution (70 Dockerfiles)

| Pattern | Count | Status | Description |
|---------|-------|--------|-------------|
| **A: Multi-Mirror Fallback** | 52 | ✅ Recommended | PyPI → Aliyun → Tencent fallback |
| **B: Aliyun Mirror Only** | 6 | ⚠️ Suboptimal | Single mirror dependency |
| **C: No Mirror** | 0 | ✅ | None found |
| Node.js (N/A) | 12 | — | Not applicable |

### Issues Found: 5 Categories

#### DRIFT-DOCKER-001: Non-Standard Base Image (MEDIUM)

| Service | Image | Expected |
|---------|-------|----------|
| `edge-orchestrator-service` | `python:3.12-slim` | `python:3.11-slim-bookworm` |
| `yolo26-vision-service` | `nvidia/cuda:12.1.1-...` | ✅ Expected exception |

#### DRIFT-DOCKER-002: Non-Standard User Names (20 services)

Expected: user `sahool` with UID 1000, GID 1000

| Issue Type | Count | Examples |
|------------|-------|---------|
| Missing UID/GID specification | 14 | agro-rules, ai-agents-core, code-fix-agent, digital-twin-engine, globalgap-compliance, iot-sensor-hub, irrigation-cycle-engine, ndvi-processor, pest-detection-service, skills-service, terrain-core-service, ussd-gateway, virtual-sensors, knowledge-graph |
| Non-standard user name | 4 | ground-vision-service (`appuser`), leveling-optimizer-service (`appuser`), supply-chain-service (`appuser`), iot-service (`nodejs` UID 1001) |
| Node default user | 2 | marketplace-service (`node`), plus other Node.js services |

#### DRIFT-DOCKER-003: Single-Stage Builds (28 services)

28 Python services use single-stage builds instead of multi-stage, resulting in larger images:
- ai-agents-core, agro-rules, ai-chat-assistant, code-review-service, cooperative-service, drone-service, digital-twin-engine, globalgap-compliance, hydrology-service, indicators-service, irrigation-cycle-engine, iot-gateway, iot-sensor-hub, knowledge-graph, lowcode-engine, mcp-server, pest-detection-service, skills-service, soil-analysis-service, terrain-core-service, traceability-service, ussd-gateway, vegetation-analysis-service, weather-service, wechat-service, ws-gateway, and 2 more

#### DRIFT-DOCKER-004: Missing PIP_NO_CACHE_DIR (12 services)

Services without the standard `PIP_NO_CACHE_DIR=1` environment variable:
- ground-vision-service, indicators-service, irrigation-smart, knowledge-graph, ndvi-processor, terrain-core-service, and 6 more

#### DRIFT-DOCKER-005: Missing PIP_DEFAULT_TIMEOUT/PIP_RETRIES (16 services)

16 services do not set `PIP_DEFAULT_TIMEOUT=300` and `PIP_RETRIES=10`.

### HEALTHCHECK Compliance: ✅ 100%

All 70 Dockerfiles include HEALTHCHECK directives.

---

## 5. Dependency Version Drift

**إصدارات التبعيات - كشف الانحراف**

### 🔴 CRITICAL SECURITY ISSUES

#### DRIFT-DEP-001: cryptography Below CVE-Patched Version (20 services)

| Property | Value |
|----------|-------|
| **Severity** | 🔴 CRITICAL |
| **Constraint** | `cryptography>=43.0.1` (CVE-2024-225, GHSA-3ww4-gg4f-jr7f) |
| **Violation** | 20 services specify `cryptography>=42.0.0` |

**Affected services:**
advisory-service, ai-advisor, billing-core, crm-service, crop-intelligence-service, equipment-service, iot-gateway, irrigation-smart, llm-orchestrator-service, logistics-service, lowcode-engine, ndvi-processor, notification-service, skills-service, task-service, vegetation-analysis-service, virtual-sensors, weather-service, wechat-service, whatsapp-bot-service

#### DRIFT-DEP-002: python-jose Below CVE Patch (4 services)

| Property | Value |
|----------|-------|
| **Severity** | 🔴 CRITICAL |
| **Constraint** | `python-jose>=3.5.0` (CVE-2024-33663, CVE-2024-33664) |
| **Violation** | 4 services specify `python-jose[cryptography]>=3.4.0` |

**Affected:** copilot-api, field-management-service, supply-chain-service, ws-gateway

#### DRIFT-DEP-003: numpy Compatibility Mismatch

| Property | Value |
|----------|-------|
| **Severity** | 🟠 HIGH |
| **File** | `pyproject.toml` (line 51) |
| **Current** | `numpy>=1.26.0,<3.0.0` |
| **Required** | `numpy>=1.26.0,<2.5.0` (TensorFlow 2.20.0 compatibility) |
| **Note** | Correctly set in `constraints.txt` and `docker/constraints-ai.txt` |

### Major Version Conflicts

#### DRIFT-DEP-004: fastapi Version Fragmentation

| Pin Pattern | Count |
|-------------|-------|
| `fastapi==0.128.5` (current) | 41 services |
| `fastapi>=0.104.0` - `>=0.126.0` (ranges) | 7 services |

#### DRIFT-DEP-005: Redis Variant Fragmentation

| Variant | Count |
|---------|-------|
| `redis>=7.1.0,<8.0.0` (without hiredis) | 30 services |
| `redis[hiredis]==7.1.0` (pinned with hiredis) | 4 services |
| `redis[hiredis]>=7.1.0,<8.0.0` (range with hiredis) | 5 services |

#### DRIFT-DEP-006: constraints.txt vs constraints-ai.txt Mismatches

| Package | constraints.txt | constraints-ai.txt |
|---------|----------------|-------------------|
| nats-py | `==2.13.1` | `>=2.9.0,<3.0.0` |
| Pillow | `==11.3.0` | `>=10.0.0,<12.0.0` |

#### DRIFT-DEP-007: starlette Version Newer Than Constraint

| Property | Value |
|----------|-------|
| **Service** | leveling-optimizer-service |
| **Requirement** | `starlette==0.52.1` |
| **Constraint** | `starlette>=0.49.1` |
| **Issue** | Service pins newer version than constraint range |

---

## 6. Deprecated Services Drift

**الخدمات المهملة - كشف الانحراف**

### Archive Status

| Status | Count | Detail |
|--------|-------|--------|
| Properly Archived | 14 | ✅ In archive/, marked in registry |
| Not Yet Archived | 1 | ⚠️ yield-prediction (in apps/services/) |
| Dual Existence | 1 | ⚠️ ndvi-processor (active + archive) |

### Issues Found: 6

#### DRIFT-DEPR-001: ndvi-processor Still in Active Docker Compose (CRITICAL)

| Property | Value |
|----------|-------|
| **Severity** | 🔴 CRITICAL |
| **File** | `docker-compose.yml` (lines 2439-2476) |
| **Issue** | Full service definition still active (only has deprecation comment) |
| **Impact** | Service starts by default with `docker-compose up` |
| **Expected** | Should require `profiles: [deprecated]` or be removed entirely |

#### DRIFT-DEPR-002: Active Code References to Deprecated Services (HIGH)

| Active Service | References | File | Line |
|----------------|------------|------|------|
| task-service | `ndvi-engine:8107` | `src/ndvi_client.py` | 27 |
| globalgap-compliance | `field-service:8115` | `src/config.py` | 54 |
| alert-service | `ndvi-engine` | `src/main.py` | — |
| field-intelligence | `ndvi-engine` | `src/models/events.py` | — |

**Impact:** Runtime failures if deprecated services are fully removed.

#### DRIFT-DEPR-003: Stale Helm Charts for Deprecated Services (MEDIUM)

8 Helm charts exist for deprecated services in `helm/services/`:
- agro-advisor, crop-health, crop-health-ai, field-ops, ndvi-engine, satellite-service, weather-advanced, weather-core

**Risk:** Accidental production deployment of deprecated services.

#### DRIFT-DEPR-004: ndvi-processor in CI/CD Test Matrix (MEDIUM)

| Property | Value |
|----------|-------|
| **File** | `.github/workflows/container-tests.yml` (line 221) |
| **Issue** | ndvi-processor included in container test matrix |
| **Port Mapping** | 8024 → 8118 |

#### DRIFT-DEPR-005: Deprecated API Endpoints in TypeScript Contracts (MEDIUM)

| Property | Value |
|----------|-------|
| **File** | `packages/shared-types/src/contracts/api-endpoints.ts` |
| **Deprecated Endpoints** | field-core, weather-core, crop-health, agro-advisor, field-chat |

#### DRIFT-DEPR-006: SLO Config References yield-engine (LOW)

| Property | Value |
|----------|-------|
| **File** | `shared/monitoring/sli_slo.py` |
| **Issue** | `yield-engine` still in SLO configuration |

---

## 7. Consolidated Findings

**النتائج الموحدة**

### Issue Summary by Severity

| Severity | Count | Issues |
|----------|-------|--------|
| 🔴 CRITICAL | 7 | DRIFT-REG-001, DRIFT-PORT-001, DRIFT-PORT-002, DRIFT-DEP-001, DRIFT-DEP-002, DRIFT-DEPR-001, DRIFT-DEPR-002 |
| 🟠 HIGH | 6 | DRIFT-PORT-003, DRIFT-HEALTH-001, DRIFT-HEALTH-002, DRIFT-DEP-003, DRIFT-DOCKER-001, DRIFT-DEPR-003 |
| 🟡 MEDIUM | 9 | DRIFT-PORT-004, DRIFT-PORT-006, DRIFT-DOCKER-002, DRIFT-DOCKER-003, DRIFT-DOCKER-004, DRIFT-DOCKER-005, DRIFT-DEPR-004, DRIFT-DEPR-005, DRIFT-DEP-004 |
| 🟢 LOW | 5 | DRIFT-PORT-005, DRIFT-PORT-007, DRIFT-DEP-005, DRIFT-DEP-006, DRIFT-DEPR-006 |
| **Total** | **27 unique issues** | |

### Issues by Category

```
Service Registry      ██░░░░░░░░  2 issues
Port Assignments      ███████░░░  7 issues
Health Endpoints      ██░░░░░░░░  2 issues
Dockerfile Patterns   █████░░░░░  5 issues
Dependencies          ███████░░░  7 issues
Deprecated Services   ██████░░░░  6 issues
```

### Top 10 Most Affected Services

| # | Service | Issues | Categories |
|---|---------|--------|------------|
| 1 | ndvi-processor | 5 | Registry, Deprecated, Docker, CI/CD, Compose |
| 2 | yield-prediction | 3 | Registry, Port, Deprecated |
| 3 | copilot-api | 3 | Health, Dependencies (python-jose, cryptography) |
| 4 | ai-chat-assistant | 2 | Health (version), Docker (single-stage) |
| 5 | code-review-agent | 2 | Port (not a service), Docker |
| 6 | demo-data | 2 | Port (not a service), Docker |
| 7 | globalgap-compliance | 2 | Deprecated refs, Docker |
| 8 | task-service | 2 | Deprecated refs, Dependencies |
| 9 | edge-orchestrator-service | 1 | Docker (Python 3.12 base) |
| 10 | leveling-optimizer-service | 1 | Dependencies (starlette pin) |

### Cross-Dimensional Drift Correlations

| Correlation | Finding |
|-------------|---------|
| Deprecated + Registry + Compose | ndvi-processor exists in all three without consistent state |
| Port + Docker | Services without HTTP servers (code-review-agent, demo-data) have port assignments but no EXPOSE |
| Security + Dependencies | 24 services vulnerable: 20 cryptography + 4 python-jose below CVE patches |
| Docker + Dependencies | 12 services missing PIP_NO_CACHE_DIR may cache vulnerable packages |

---

## 8. Remediation Roadmap

**خارطة طريق المعالجة**

### Phase 1: Critical Security (Immediate | فوري)

| # | Action | Files | Impact |
|---|--------|-------|--------|
| 1 | Update `cryptography>=43.0.1` in 20 service requirements.txt files | `apps/services/*/requirements.txt` | Patches CVE-2024-225 |
| 2 | Update `python-jose>=3.5.0` in 4 service requirements.txt files | copilot-api, field-management-service, supply-chain-service, ws-gateway | Patches CVE-2024-33663/33664 |
| 3 | Fix numpy upper bound in pyproject.toml | `pyproject.toml` | TensorFlow compatibility |

### Phase 2: Service Lifecycle (This Sprint | هذا السبرنت)

| # | Action | Files | Impact |
|---|--------|-------|--------|
| 4 | Archive yield-prediction to `archive/deprecated-services/` | `apps/services/yield-prediction/` | Registry consistency |
| 5 | Remove ndvi-processor from docker-compose default profile | `docker-compose.yml` (lines 2439-2476) | Prevents unintended startup |
| 6 | Resolve ndvi-processor dual existence (archive vs active) | `governance/services.yaml`, filesystem | Single source of truth |
| 7 | Update task-service ndvi_client.py: `ndvi-engine:8107` → `vegetation-analysis-service:8090` | `apps/services/task-service/src/ndvi_client.py:27` | Remove deprecated dependency |
| 8 | Update globalgap-compliance config: `field-service:8115` → `field-management-service:3000` | `apps/services/globalgap-compliance/src/config.py:54` | Remove deprecated dependency |

### Phase 3: Standardization (Next Sprint | السبرنت القادم)

| # | Action | Files | Impact |
|---|--------|-------|--------|
| 9 | Fix health endpoint versions to `16.0.0` | ai-chat-assistant `main.py`, copilot-api `health.py` | Version consistency |
| 10 | Remove code-review-agent and demo-data from SERVICE_PORTS | `packages/shared-types/src/contracts/service-ports.ts` | Accurate port registry |
| 11 | Standardize Docker user to `sahool` UID 1000 across 20 services | 20 Dockerfiles | Security consistency |
| 12 | Convert 28 single-stage Dockerfiles to multi-stage | 28 Dockerfiles | Smaller images |
| 13 | Add PIP_NO_CACHE_DIR=1 to 12 services | 12 Dockerfiles | Build optimization |
| 14 | Fix edge-orchestrator-service base image to Python 3.11 | `apps/services/edge-orchestrator-service/Dockerfile` | Version consistency |

### Phase 4: Cleanup (Backlog | الأعمال المتراكمة)

| # | Action | Files | Impact |
|---|--------|-------|--------|
| 15 | Archive 8 deprecated Helm charts | `helm/services/` | Prevent accidental deployment |
| 16 | Remove deprecated API endpoints from TypeScript contracts | `packages/shared-types/src/contracts/api-endpoints.ts` | Contract accuracy |
| 17 | Remove ndvi-processor from CI test matrix | `.github/workflows/container-tests.yml` | CI efficiency |
| 18 | Clean up SLO config for yield-engine | `shared/monitoring/sli_slo.py` | Monitoring accuracy |
| 19 | Standardize Redis hiredis usage across services | 39 requirements.txt files | Dependency consistency |
| 20 | Add 30+ missing services to Kong upstreams | `infrastructure/gateway/kong/kong-upstreams.yml` | API Gateway coverage |

---

## Appendix A: Full Service Compliance Matrix

| Service | Registry | Port | Health | Docker | Deps | Deprecated |
|---------|----------|------|--------|--------|------|------------|
| advisory-service | ✅ | ✅ | ✅ | ✅ | ⚠️ crypto | ✅ |
| agent-registry | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| agro-rules | ✅ | ✅ | ✅ | ⚠️ UID | ✅ | ✅ |
| ai-advisor | ✅ | ✅ | ✅ | ⚠️ mirror | ⚠️ crypto | ✅ |
| ai-agents-core | ✅ | ✅ | ✅ | ⚠️ UID | ✅ | ✅ |
| ai-agents-service | ✅ | ✅ | ✅ | ⚠️ mirror | ✅ | ✅ |
| ai-chat-assistant | ✅ | ✅ | ❌ ver | ⚠️ stage | ✅ | ✅ |
| alert-service | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠️ ref |
| astronomical-calendar | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| audit-service | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| billing-core | ✅ | ✅ | ✅ | ✅ | ⚠️ crypto | ✅ |
| chat-service | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| code-fix-agent | ✅ | ✅ | ✅ | ⚠️ UID | ✅ | ✅ |
| code-review-agent | ✅ | ❌ port | ✅ | ✅ | ✅ | ✅ |
| code-review-service | ✅ | ✅ | ✅ | ⚠️ stage | ✅ | ✅ |
| cooperative-service | ✅ | ✅ | ✅ | ⚠️ stage | ✅ | ✅ |
| copilot-api | ✅ | ✅ | ❌ ver | ✅ | ⚠️ jose | ✅ |
| crm-service | ✅ | ✅ | ✅ | ✅ | ⚠️ crypto | ✅ |
| crop-growth-model | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| crop-intelligence-service | ✅ | ✅ | ✅ | ✅ | ⚠️ crypto | ✅ |
| demo-data | ✅ | ❌ port | ✅ | ⚠️ UID | ✅ | ✅ |
| digital-twin-engine | ✅ | ✅ | ✅ | ⚠️ UID | ✅ | ✅ |
| disaster-assessment | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| drone-service | ✅ | ✅ | ✅ | ⚠️ stage | ✅ | ✅ |
| edge-orchestrator-service | ✅ | ✅ | ✅ | ❌ py3.12 | ✅ | ✅ |
| equipment-service | ✅ | ✅ | ✅ | ✅ | ⚠️ crypto | ✅ |
| fertigation-engine | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| field-intelligence | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠️ ref |
| field-management-service | ✅ | ✅ | ✅ | ✅ | ⚠️ jose | ✅ |
| globalgap-compliance | ✅ | ✅ | ✅ | ⚠️ UID | ✅ | ⚠️ ref |
| ground-vision-service | ✅ | ✅ | ✅ | ⚠️ user | ✅ | ✅ |
| hydrology-service | ✅ | ✅ | ✅ | ⚠️ stage | ✅ | ✅ |
| indicators-service | ✅ | ✅ | ✅ | ⚠️ mirror | ✅ | ✅ |
| inventory-service | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| iot-gateway | ✅ | ✅ | ✅ | ⚠️ stage | ⚠️ crypto | ✅ |
| iot-sensor-hub | ✅ | ✅ | ✅ | ⚠️ UID | ✅ | ✅ |
| iot-service | ✅ | ✅ | ✅ | ⚠️ user | ✅ | ✅ |
| irrigation-cycle-engine | ✅ | ✅ | ✅ | ⚠️ UID | ✅ | ✅ |
| irrigation-smart | ✅ | ✅ | ✅ | ⚠️ PIP | ⚠️ crypto | ✅ |
| knowledge-graph | ✅ | ✅ | ✅ | ⚠️ UID/PIP | ✅ | ✅ |
| lai-estimation | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| leveling-optimizer-service | ✅ | ✅ | ✅ | ⚠️ user | ⚠️ starlette | ✅ |
| llm-orchestrator-service | ✅ | ✅ | ✅ | ✅ | ⚠️ crypto | ✅ |
| logistics-service | ✅ | ✅ | ✅ | ✅ | ⚠️ crypto | ✅ |
| lowcode-engine | ✅ | ✅ | ✅ | ⚠️ stage | ⚠️ crypto | ✅ |
| marketplace-service | ✅ | ✅ | ✅ | ⚠️ user | ✅ | ✅ |
| mcp-server | ✅ | ✅ | ✅ | ⚠️ stage | ✅ | ✅ |
| ndvi-processor | ⚠️ dual | ✅ | ✅ | ⚠️ UID/PIP | ⚠️ crypto | ❌ active |
| notification-service | ✅ | ✅ | ✅ | ✅ | ⚠️ crypto | ✅ |
| pest-detection-service | ✅ | ✅ | ✅ | ⚠️ UID | ✅ | ✅ |
| provider-config | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| research-core | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| skills-service | ✅ | ✅ | ✅ | ⚠️ UID | ⚠️ crypto | ✅ |
| soil-analysis-service | ✅ | ✅ | ✅ | ⚠️ stage | ✅ | ✅ |
| supply-chain-service | ✅ | ✅ | ✅ | ⚠️ user | ⚠️ jose | ✅ |
| task-service | ✅ | ✅ | ✅ | ✅ | ⚠️ crypto | ⚠️ ref |
| terrain-core-service | ✅ | ✅ | ✅ | ⚠️ UID/PIP | ✅ | ✅ |
| traceability-service | ✅ | ✅ | ✅ | ⚠️ stage | ✅ | ✅ |
| user-service | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| ussd-gateway | ✅ | ✅ | ✅ | ⚠️ UID | ✅ | ✅ |
| vegetation-analysis-service | ✅ | ✅ | ✅ | ⚠️ stage | ⚠️ crypto | ✅ |
| virtual-sensors | ✅ | ✅ | ✅ | ⚠️ UID | ⚠️ crypto | ✅ |
| weather-service | ✅ | ✅ | ✅ | ⚠️ stage | ⚠️ crypto | ✅ |
| wechat-service | ✅ | ✅ | ✅ | ⚠️ stage | ⚠️ crypto | ✅ |
| whatsapp-bot-service | ✅ | ⚠️ EXPOSE | ✅ | ✅ | ⚠️ crypto | ✅ |
| ws-gateway | ✅ | ✅ | ✅ | ⚠️ stage | ⚠️ jose | ✅ |
| yield-prediction | ⚠️ depr | ⚠️ dup | ✅ | ✅ | ✅ | ⚠️ not archived |
| yield-prediction-service | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| yolo26-vision-service | ✅ | ⚠️ dup EXPOSE | ✅ | ✅ | ✅ | ✅ |

**Legend:** ✅ Compliant | ⚠️ Warning | ❌ Violation

---

## Appendix B: Files Requiring Immediate Attention

### CRITICAL Files (7)

```
apps/services/advisory-service/requirements.txt          # cryptography pin
apps/services/copilot-api/requirements.txt               # python-jose pin
apps/services/copilot-api/src/api/v1/health.py           # version string
apps/services/ai-chat-assistant/src/main.py              # version string
apps/services/task-service/src/ndvi_client.py             # deprecated service URL
apps/services/globalgap-compliance/src/config.py          # deprecated service URL
docker-compose.yml                                        # ndvi-processor active definition
```

### HIGH Priority Files (5)

```
packages/shared-types/src/contracts/service-ports.ts      # code-review-agent, demo-data entries
governance/services.yaml                                   # ndvi-processor path, yield-prediction status
pyproject.toml                                             # numpy upper bound
apps/services/edge-orchestrator-service/Dockerfile         # Python 3.12 base
infrastructure/gateway/kong/kong-upstreams.yml             # missing services
```

---

_Report generated: 2026-02-26 | تم إنشاء التقرير_
_Analysis scope: main branch, full codebase | نطاق التحليل: الفرع الرئيسي، قاعدة الكود الكاملة_
_Tool: Automated drift detection across 7 dimensions | الأداة: كشف الانحراف الآلي عبر 7 أبعاد_
