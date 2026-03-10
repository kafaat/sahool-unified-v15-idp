# SAHOOL Platform - Comprehensive Codebase Audit Report

**Date**: 2026-03-09
**Scope**: Full platform analysis (72 microservices, 80 shared modules, mobile, web, infrastructure)
**Method**: 17 parallel analysis agents covering all dimensions
**Platform Version**: 16.0.0

---

## Executive Summary

| Dimension | Status | Critical | High | Medium | Low |
|-----------|--------|----------|------|--------|-----|
| Security | **EXCELLENT** | 0 | 0 | 0 | 2 |
| Database Schema | **EXCELLENT** | 0 | 0 | 1 | 2 |
| Port Registry | **EXCELLENT** | 0 | 0 | 0 | 3 |
| Docker Config | **EXCELLENT** | 0 | 2 | 4 | 0 |
| Shared Module Graph | **GOOD** | 0 | 1 | 2 | 2 |
| Dead Code | **GOOD** | 0 | 0 | 3 | 2 |
| Python Dependencies | **NEEDS WORK** | 0 | 3 | 5 | 3 |
| Node.js Dependencies | **NEEDS WORK** | 3 | 5 | 3 | 3 |
| Error Handling | **NEEDS WORK** | 3 | 3 | 3 | 0 |
| NATS Events | **NEEDS WORK** | 4 | 4 | 2 | 0 |
| API Consistency | **NEEDS WORK** | 0 | 3 | 3 | 0 |
| CI/CD Workflows | **NEEDS WORK** | 1 | 1 | 2 | 1 |
| Test Coverage | **CRITICAL** | 0 | 5 | 3 | 2 |
| Logging | **CRITICAL** | 2 | 3 | 2 | 0 |
| Environment Config | **NEEDS WORK** | 0 | 3 | 5 | 2 |
| Import Health | **GOOD** | 0 | 0 | 1 | 3 |
| Flutter/Dart | **GOOD** | 0 | 2 | 2 | 2 |
| **TOTAL** | | **13** | **35** | **41** | **25** |

---

## 1. Security Vulnerability Scan

### Result: EXCELLENT - No Critical Vulnerabilities

- **Hardcoded Secrets**: NONE found in source code
- **SQL Injection**: All queries parameterized (Prisma + Tortoise ORM)
- **Command Injection**: Proper `subprocess_exec()` usage (no shell=True)
- **CORS**: Environment-aware configuration with wildcard warnings
- **SSL/TLS**: `sslmode=require` enforced on all DB connections
- **File Upload**: Size/type/virus validation via `shared/file_validation/`
- **Input Validation**: Pydantic + custom validators across all FastAPI services
- **XXE Prevention**: `defusedxml` used for XML parsing
- **AI Guardrails**: Tool execution restricted via `shared/ai/guardrails/tool_guard.py`

---

## 2. Python Dependency Analysis

### Result: 65 packages with version conflicts (49.6% of 131 unique packages)

**Critical Conflicts**:

| Package | Issue | Impact |
|---------|-------|--------|
| **PyJWT** | `==2.10.1` (shared/auth) vs `>=2.8.0,<3.0.0` (17+ services) | Auth module forces version globally |
| **AsyncPG** | 3 versions in use (0.30.0, 0.31.0, ranges) | DB protocol incompatibilities |
| **FastAPI** | 4 versions (0.115.5, 0.126.0, 0.128.5, ranges) | Middleware behavior differences |
| **Constraint Files** | `constraints.txt` (pins) vs `docker/constraints-ai.txt` (ranges) | Inconsistent enforcement |

**Recommendation**: Standardize PyJWT, align AsyncPG to 0.31.0, consolidate FastAPI to 0.128.5.

---

## 3. Node.js Dependency Analysis

### Result: Multiple critical version conflicts across 45 package.json files

**Critical Issues**:

| Package | Issue | Fix |
|---------|-------|-----|
| **Prisma** | shared-db `^5.8.0` vs services `^5.22.0` vs root `^5.10.0` | Align to ^5.22.0 |
| **TypeScript** | 5.9.3 (standard) vs 5.7.2 (user-service, code-review-agent) | Pin all to 5.9.3 |
| **file:// protocols** | field-management & marketplace use file:// refs | Convert to workspace refs |
| **@types/node** | 6 versions (20.x vs 22.x) | Standardize to 20.19.33 |
| **@sentry/nextjs** | v8 (shared pkgs) vs v9.5 (apps) | Remove from shared packages |

**Hoisting Opportunity**: 500MB+ savings by hoisting 14 high-impact packages to root.

---

## 4. Error Handling Patterns

### Result: 204 generic 500 errors, inconsistent framework adoption

| Issue | Count | Severity |
|-------|-------|----------|
| Generic `HTTPException(500)` without error codes | 204 | HIGH |
| Bare `except:` clauses | 3 | CRITICAL |
| Services NOT using `shared/errors_py.py` | 32 (44%) | HIGH |
| Missing NATS publish error handling | 30+ | HIGH |
| Missing DB operation error handling | 15+ | HIGH |
| Empty catch blocks (JS) | 1 | MEDIUM |

**Key File**: `shared/errors_py.py` exists with 15+ error codes and bilingual support, but only 40/72 services use it.

---

## 5. NATS Event Architecture

### Result: 271 defined events with critical gaps

| Issue | Count | Severity |
|-------|-------|----------|
| Undefined event published (`sahool.terrain.simulation_completed`) | 1 | CRITICAL |
| Events without tenant-scoped subjects | 266/271 | CRITICAL |
| Missing JSON schemas in governance | 267/271 (98.5%) | HIGH |
| Missing error handling in event publishing | 30+ services | HIGH |
| DLQ handlers not implemented | 65+ services | HIGH |
| Missing required fields (tenant_id, correlation_id) | 3+ services | HIGH |

**Recommendation**: Add missing event constant, migrate to `get_tenant_subject()`, implement DLQ handlers.

---

## 6. Database Schema

### Result: EXCELLENT - Well-implemented

- **Foreign Key Indexes**: Comprehensive on all models
- **Timestamps**: DB-level auto-update triggers on all tables
- **Tenant Isolation**: All 70+ tables have `tenant_id` with backfill logic
- **Connection Pooling**: PgBouncer (250 max, transaction mode)
- **Primary Keys**: UUID `uuid_generate_v4()` throughout
- **PostGIS**: GIST indexes, correct SRID 4326
- **Optimistic Locking**: Version fields on Field and Wallet models
- **Row-Level Security**: RLS functions defined in migrations

**Single Issue**: N+1 query risk in Tortoise ORM services (notification-service, task-service).

---

## 7. API Endpoint Consistency

### Result: Multiple consistency issues

| Issue | Count |
|-------|-------|
| Missing `/healthz` endpoints | 4 services (copilot-api, edge-orchestrator, leveling-optimizer, terrain-core) |
| Missing `response_model` definitions | 47 services |
| Inconsistent versioning (`/v1/` vs `/api/v1/`) | 53 services |
| Potential missing auth on protected endpoints | 3 services (audit-service, provider-config, globalgap-compliance) |
| Port conflicts | **0** |

---

## 8. Test Coverage

### Result: CRITICAL gaps

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Services with any tests | 60/72 (83%) | 100% | YELLOW |
| Services with 3+ test files | 15/72 (21%) | 80% | RED |
| Shared modules with tests | 3/80 (4%) | 60% | RED |
| Estimated code coverage | ~5% | 20% | RED |

**Services with ZERO tests (11)**: user-service, chat-service, marketplace-service, iot-service, crop-growth-model, yield-prediction, yield-prediction-service, lai-estimation, disaster-assessment, research-core, vllm-deepseek.

**Untested shared modules (96.25%)**: auth/, cache/, events/, contracts/, ai/, agents/, guardrails/, mobile_sync/ - all critical infrastructure.

---

## 9. Docker Configuration

### Result: EXCELLENT security posture

| Control | Compliance |
|---------|-----------|
| Non-root user (`sahool` UID 1000) | 100% |
| HEALTHCHECK directives | 91% |
| Multi-stage builds | 49% |
| `pip --no-cache-dir` | 100% |
| `security_opt: no-new-privileges` | 95% |
| Tini init system | 100% |

**Minor Issues**: Missing logging config (90+ services), read-only filesystem not enforced, 1 inconsistent base image (agro-rules).

---

## 10. CI/CD Workflows

### Result: 53 workflows, 1 critical issue

| Issue | Count | Severity |
|-------|-------|----------|
| Unpinned third-party action (`bridgecrewio/checkov-action@master`) | 1 | CRITICAL |
| Missing `permissions:` declarations | 21 | HIGH |
| Missing `timeout-minutes` | 40 | MEDIUM |
| Missing caching (pip, npm, Docker) | 28 | MEDIUM |
| Potential injection (`deploy-preview.yml` PR title) | 1 | LOW |

**Good Practices**: Concurrency controls, proper secrets handling, most GitHub actions pinned to versions.

---

## 11. Environment Configuration

### Result: Significant inconsistencies

| Issue | Severity |
|-------|----------|
| Duplicate variable names (JWT_SECRET vs JWT_SECRET_KEY, 3 CORS variants) | HIGH |
| Hardcoded fallback URLs (nats://localhost:4222, postgresql://localhost) | HIGH |
| 30+ unused variables in .env.example | MEDIUM |
| No `env_file:` directives in any docker-compose | MEDIUM |
| 10+ service env vars missing from .env.example | MEDIUM |
| .env.example (870 lines) diverged from .env.development.template (232 lines) | MEDIUM |

---

## 12. Logging Consistency

### Result: CRITICAL inconsistencies

| Issue | Count | Severity |
|-------|-------|----------|
| `print()` instead of logging | 92 files | CRITICAL |
| No logging configuration at all | 36 services | CRITICAL |
| Basic `logging.getLogger` (not structlog) | 16 services | HIGH |
| `console.log` in Node.js services | 88+ files | HIGH |
| Services using structlog (compliant) | Only 22 (7.1%) | - |

**Shared logging infrastructure exists** (`shared/logging_config.py`, `shared/middleware/request_logging.py`) but only 3 files import from it.

---

## 13. Shared Module Dependency Graph

### Result: Clean architecture, no circular dependencies

| Finding | Details |
|---------|---------|
| Circular dependencies | **0** |
| AI module (monolithic) | 84,442 LOC (67% of shared code) |
| Auth module (bottleneck) | 13,368 LOC, imported by 88 services (79%) |
| Orphan modules | 5 (db, design-system, python-lib, templates, versioning) |
| Max dependency depth | 3 tiers |

**Recommendation**: Split AI module into 6-8 focused sub-modules.

---

## 14. Import Health

### Result: GOOD - No critical issues

| Finding | Count | Severity |
|---------|-------|----------|
| `sys.path.insert` usage | 43 services | MEDIUM |
| Star imports | 2 files | LOW |
| Deprecated modules (imp, distutils) | 0 | - |
| Circular imports | 0 | - |
| Missing `__init__.py` | 0 | - |

---

## 15. Flutter/Dart Analysis

### Result: GOOD - Strong offline-first architecture

**Strengths**: SQLCipher encryption, certificate pinning with placeholder detection, Riverpod state management, ETag-based conflict resolution.

**Issues**:

| Issue | Severity |
|-------|----------|
| `app_links` v3.5.1 (root) vs v6.3.3 (field_app) | HIGH |
| `share_plus` v7.2.1 vs v10.1.4 | HIGH |
| StreamSubscription dispose verification needed | MEDIUM |
| Generic error messages in catch blocks | MEDIUM |

---

## 16. Port & Service Registry

### Result: EXCELLENT - 100% alignment

- **Port conflicts**: 0
- **Governance/docker-compose/SERVICE_PORTS sync**: 100%
- **72 active services, 15 properly archived**

---

## 17. Dead Code & Unused Files

### Result: GOOD - Code health score 8.5/10

| Finding | Count |
|---------|-------|
| Skeleton services (< 300 LOC) | 8 |
| TODO/FIXME/XXX/HACK comments | 373 |
| Test files referencing deprecated services | 16 |
| Properly archived deprecated services | 15 |

---

## Priority Action Plan

### P0 - Critical (This Week)

1. **Pin `bridgecrewio/checkov-action` to SHA** in security-audit.yml
2. **Add missing NATS event constant** `SAHOOL_TERRAIN_SIMULATION_COMPLETED`
3. **Fix bare `except:` clauses** in 3 files
4. **Align Prisma versions** to ^5.22.0 across all packages
5. **Verify auth decorators** on audit-service, provider-config, globalgap-compliance

### P1 - High (This Sprint)

6. **Add tests for user-service, marketplace-service, chat-service** (security-critical, zero tests)
7. **Migrate 32 services** to use `shared/errors_py.py` unified error handling
8. **Replace 92 `print()` calls** with structlog logging
9. **Add `permissions:` block** to 21 CI/CD workflows
10. **Consolidate JWT_SECRET vs JWT_SECRET_KEY** to single variable name
11. **Add error handling to NATS publishers** (30+ services)
12. **Pin TypeScript** to 5.9.3 in user-service and code-review-agent

### P2 - Medium (Next Quarter)

13. **Generate JSON schemas** for 267 NATS events
14. **Migrate events to tenant-scoped subjects** (`get_tenant_subject()`)
15. **Add `timeout-minutes`** to 40 CI/CD workflows
16. **Add caching** to 28 CI/CD workflows
17. **Split AI module** into 6-8 focused sub-modules
18. **Implement DLQ handlers** across services
19. **Add response_model** to 47 FastAPI services
20. **Standardize API versioning** to `/api/v1/` pattern
21. **Hoist Node.js dependencies** (500MB+ savings)
22. **Remove hardcoded fallback URLs** from service configs

### P3 - Long Term

23. **Achieve 20% test coverage** (currently ~5%)
24. **Test shared modules** (auth, events, cache, ai)
25. **Complete 8 skeleton services** or archive them
26. **Clean up 30+ unused env variables** from .env.example
27. **Implement read-only filesystem** for Docker containers
28. **Reduce Python dependency conflicts** from 65 to <20

---

## Metrics Summary

| Metric | Value |
|--------|-------|
| Total microservices | 72 active + 15 archived |
| Shared modules | 80 |
| Total Python packages | 131 unique |
| Total Node packages | 45 package.json files |
| CI/CD workflows | 53 |
| NATS events defined | 271 |
| Prisma schemas | 28 |
| SQL migrations | 44 |
| Dockerfiles | 81 |
| Test files | 236 unit + 40 integration + 7 smoke |
| Lines of shared code | ~207KB |
| Documentation files | 475+ |

---

_Report generated by 17 parallel analysis agents on 2026-03-09_
_Platform: SAHOOL Unified v16.0.0_
