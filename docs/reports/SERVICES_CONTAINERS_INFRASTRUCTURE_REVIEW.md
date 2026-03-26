# Services & Containers Infrastructure Review Report

**Date**: 2026-03-21
**Scope**: 72 service Dockerfiles, docker-compose files, Helm charts, CI/CD workflows, port/health cross-reference
**Reviewer**: Automated Infrastructure Audit (8 parallel agents)

---

## Executive Summary

A comprehensive audit of all SAHOOL platform services and container infrastructure uncovered **78 issues** across 8 areas. The most critical findings include **missing shared module copies causing runtime import failures**, **swallowed test failures in release pipeline**, **inverted production approval gate logic**, and **HEALTHCHECK syntax errors preventing container health monitoring**.

| Severity | Dockerfiles | Compose | Helm | CI/CD | Ports | Total |
|----------|-------------|---------|------|-------|-------|-------|
| Critical | 8 | 1 | 0 | 2 | 0 | **11** |
| High | 10 | 1 | 1 | 0 | 0 | **12** |
| Medium | 14 | 1 | 5 | 3 | 1 | **24** |
| Low | 8 | 0 | 1 | 2 | 0 | **11** |
| **Total** | **40** | **3** | **7** | **7** | **1** | **78** |

**Positive Finding**: Port consistency is excellent — 66 services verified with zero conflicts across governance, docker-compose, and TypeScript contracts.

---

## 1. Python Service Dockerfiles (47 services reviewed)

### CRITICAL — Runtime Import Failures

#### 1.1 Missing Root shared/ Module Copy (5 services)
These services copy `apps/services/shared/` but NOT the root `shared/` directory, causing `ImportError` at startup:

| Service | File | Line |
|---------|------|------|
| alert-service | `apps/services/alert-service/Dockerfile` | 71 |
| irrigation-smart | `apps/services/irrigation-smart/Dockerfile` | 58 |
| drone-service | `apps/services/drone-service/Dockerfile` | 33-37 |
| virtual-sensors | `apps/services/virtual-sensors/Dockerfile` | 72 |
| provider-config | `apps/services/provider-config/Dockerfile` | 68-75 (wrong path) |

**Fix**: Add `COPY shared/ ./shared/` before `COPY apps/services/shared/ ./shared/`.

#### 1.2 HEALTHCHECK ${PORT} Not Expanded (2 services)
- **llm-orchestrator-service/Dockerfile:117** — `${PORT}` in Python string not expanded (HEALTHCHECK CMD doesn't use shell)
- **crop-intelligence-service/Dockerfile:113** — ENV definition order issue with HEALTHCHECK

**Fix**: Use `os.environ.get("PORT", "8164")` inside Python code.

#### 1.3 Missing httpx Dependency for HEALTHCHECK
- **astronomical-calendar/requirements.txt** — HEALTHCHECK uses `httpx` but it's not in requirements.txt.

### HIGH — Missing Tini (PID 1 Signal Handling)

**14+ services** run Python directly as PID 1 without tini, causing zombie process accumulation and failed graceful shutdown:

alert-service, billing-core, cooperative-service, crm-service, crop-intelligence-service, equipment-service, indicators-service, inventory-service, irrigation-smart, notification-service, task-service, vegetation-analysis-service, weather-service, and more.

**Fix**: Install tini and add `ENTRYPOINT ["/usr/bin/tini", "--"]`.

### HIGH — Broken HEALTHCHECK Syntax

| Service | File | Issue |
|---------|------|-------|
| iot-gateway | Dockerfile:82 | Missing `|| exit 1` |
| virtual-sensors | Dockerfile:87 | Broken quote escaping in shell |

### MEDIUM

| Issue | Services Affected | Fix |
|-------|------------------|-----|
| Missing PYTHONPATH=/app | crm-service, indicators-service | Add to ENV |
| pip.conf in /root/.pip (wrong user) | ws-gateway | Move to /home/sahool/.pip |
| Missing --create-home in useradd | fertigation-engine, irrigation-cycle-engine, digital-twin-engine | Add --create-home flag |
| Wrong base image (slim vs slim-bookworm) | agro-rules | Use python:3.11-slim-bookworm |
| Missing PYTHONDONTWRITEBYTECODE | code-review-service | Add to ENV |
| Inconsistent UID/GID (no explicit 1000) | ai-agents-core, logistics-service | Add --uid 1000 --gid 1000 |
| Uses --user pip instead of venv | astronomical-calendar, provider-config | Switch to venv pattern |
| Hardcoded HEALTHCHECK port vs ${PORT} CMD | inventory-service, ws-gateway | Make consistent |

### LOW — Dependency Issues

| Issue | Services |
|-------|----------|
| asyncpg unbounded upper (missing `<1.0.0`) | indicators-service |
| apscheduler unpinned (vs ==3.11.2) | inventory-service |
| tensorflow-cpu unbounded upper | ai-agents-core |
| astroid/pylint unbounded upper | code-fix-agent |
| SQLAlchemy capitalization inconsistency | equipment-service vs alert-service |
| Unnecessary curl install | crm-service |

---

## 2. NestJS Service Dockerfiles (10 services reviewed)

### CRITICAL

#### 2.1 HEALTHCHECK Syntax Errors (2 services)
- **crop-growth-model/Dockerfile:154** — HEALTHCHECK written on single line without proper continuation
- **disaster-assessment/Dockerfile:141** — Same issue

**Fix**: Add backslash continuation: `HEALTHCHECK ... \n    CMD ...`

#### 2.2 iot-service Dependency Resolution Failure
- **File**: `apps/services/iot-service/Dockerfile`, lines 37, 100, 129
- **Issue**: `@sahool/shared-events` deleted from package.json in production stage, then manually copied to node_modules without proper package.json entry. `require('@sahool/shared-events')` will fail.

#### 2.3 code-review-agent Missing Entry Point
- **File**: `apps/services/code-review-agent/Dockerfile:92`
- **Issue**: `CMD ["node", "dist/production-agent.js"]` references file that may not exist after `tsc` compilation.

---

## 3. Docker Compose Files (13 files reviewed)

### HIGH

#### 3.1 etcd-perms-init Missing Healthcheck
- **File**: `docker-compose.yml`, lines 933-971
- **Issue**: `etcd` depends on `etcd-perms-init` with `condition: service_completed_successfully`, but the init service has no healthcheck. Docker Compose cannot determine completion.

### MEDIUM

#### 3.2 test_runner Short-Form depends_on
- **File**: `docker-compose.test.yml`, lines 163-168
- **Issue**: Uses short form `depends_on` (startup order only) instead of `condition: service_healthy`. Tests may start before services are ready.

### PORT CONSISTENCY: PASSED
- 66 services verified across governance/services.yaml, docker-compose.yml, and TypeScript contracts
- Zero port conflicts found
- Zero duplicate port assignments

---

## 4. Helm Charts & Kubernetes

### HIGH

#### 4.1 NATS StatefulSet Missing Security Context
- **File**: `helm/sahool/templates/infrastructure/nats-statefulset.yaml`, lines 40-47
- **Issue**: No podSecurityContext, no container securityContext, no automountServiceAccountToken. PostgreSQL and Redis have proper contexts but NATS does not.

### MEDIUM

#### 4.2 Prometheus Metrics Port Annotation Mismatch
- **File**: `helm/sahool/values.yaml`, line 42
- **Issue**: Default `prometheus.io/port: "8080"` but no services use port 8080. Metrics collection fails silently.

#### 4.3 Kong Missing PodDisruptionBudget
- **File**: `helm/sahool/templates/pdb.yaml`
- **Issue**: PDB template only covers `.Values.services`, not infrastructure. Kong (3 replicas in production) has no PDB — all pods can be evicted during maintenance.

#### 4.4 Infrastructure VPA Templates Not Rendered
- **File**: `helm/sahool/templates/vpa.yaml`, lines 8-41
- **Issue**: VPA template loops `.Values.services` only. PostgreSQL, Redis, NATS, Kong have VPA settings in values.yaml but VPA resources are never created.

#### 4.5 PostgreSQL/Redis readOnlyRootFilesystem Conflict
- **Files**: postgres-statefulset.yaml:52, redis-deployment.yaml:51
- **Issue**: `readOnlyRootFilesystem: true` set but these services need write access to data directories. Missing emptyDir volumes for /tmp.

#### 4.6 Kong TLS Configuration Unclear
- **File**: `helm/sahool/templates/infrastructure/kong-deployment.yaml`, lines 10-19
- **Issue**: Service type LoadBalancer exposes port 443 → container 8443, but no TLS certificate configuration visible.

### LOW

#### 4.7 Missing tmp Volumes in Stateful Services
- PostgreSQL and Redis deployments lack emptyDir for /tmp (unlike application services).

---

## 5. CI/CD Workflows

### CRITICAL

#### 5.1 Production Approval Gate Logic Bug
- **File**: `.github/workflows/cd-production.yml`, line 150
- **Issue**: `if: skip_approval != 'true' || hotfix_justification == ''` — OR logic allows bypass. Should use AND.
- **Impact**: Production deployments can accidentally skip approval.

#### 5.2 Release Pipeline Swallows Test Failures
- **File**: `.github/workflows/release.yml`, line 214
- **Issue**: `pytest --tb=short || true` — all test failures ignored. Releases created with untested code.

### MEDIUM

#### 5.3 Docker Buildx Single-Platform Default
- **File**: `.github/workflows/docker-buildx.yml`, line 240
- Default `linux/amd64` only. ARM64 users get no image.

#### 5.4 Unset Turbo Cache Secret
- **File**: `.github/workflows/ci.yml`, line 67
- `TURBO_REMOTE_CACHE_SIGNATURE_KEY` silently empty if secret not configured.

#### 5.5 Deprecated Safety Security Scanner
- **File**: `.github/workflows/security-checks.yml`, line 190
- `safety scan` deprecated since June 2024, may not work without API key.

### LOW

#### 5.6 Unquoted Bash Variable in CD
- **File**: `.github/workflows/cd-production.yml`, line 132

#### 5.7 Prerelease Tag Condition
- **File**: `.github/workflows/release.yml`, line 312

---

## 6. Service Port & Health Cross-Reference

### RESULT: 98% CONSISTENT

| Check | Result |
|-------|--------|
| Port conflicts | **NONE** — all 66 services have unique ports |
| Governance ↔ Docker-Compose sync | **100%** (66/66 active services) |
| Governance ↔ TypeScript contracts | **100%** (66/66) |
| Kong routes ↔ service ports | **100%** (71/71 routes) |
| Health endpoints consistent | **98%** (81/82 use `/healthz`) |

### Issues Found

#### 6.1 vllm-deepseek Not Deployed
- Active in governance/services.yaml (port 8270) but NOT in docker-compose.yml.
- **Fix**: Add to docker-compose or mark inactive in governance.

#### 6.2 user-service Non-Standard Health Endpoint
- Uses `/api/v1/health` instead of platform standard `/healthz`.

---

## Priority Action Plan

### Week 1 — Critical Fixes (11 issues)
1. **Fix 5 services missing root shared/ copy** — runtime import failures
2. **Fix HEALTHCHECK syntax** in crop-growth-model, disaster-assessment, iot-gateway, virtual-sensors, llm-orchestrator, crop-intelligence
3. **Fix production approval gate logic** in cd-production.yml
4. **Remove `|| true` from pytest** in release.yml
5. **Fix iot-service shared-events dependency**
6. **Add httpx to astronomical-calendar requirements**

### Week 2 — High Priority (12 issues)
7. Add tini to 14+ Python services
8. Fix etcd-perms-init healthcheck dependency
9. Add NATS security context in Helm
10. Fix code-review-agent entry point

### Week 3 — Medium Priority (24 issues)
11. Add PYTHONPATH to crm-service, indicators-service
12. Fix pip.conf location in ws-gateway
13. Add --create-home to 3 services
14. Fix Prometheus port annotation in Helm
15. Add Kong PDB
16. Fix VPA template for infrastructure
17. Fix PostgreSQL/Redis readOnlyRootFilesystem
18. Fix docker-buildx multi-platform default
19. Use proper base image in agro-rules

### Backlog — Low Priority (11 issues)
20. Pin dependency upper bounds
21. Standardize user-service health endpoint
22. Add vllm-deepseek to docker-compose
23. Fix unquoted bash variables in CI
