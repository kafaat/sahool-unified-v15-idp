# Container Audit Fix Summary - March 2026
# ملخص إصلاحات تدقيق الحاويات - مارس 2026

**Date**: 2026-03-15
**Branch**: `claude/fix-sahool-containers-Uhcvw`
**Base Commit**: `5021e59`

---

## Overview | نظرة عامة

Audited 73 containers across the SAHOOL platform. Identified and fixed issues spanning container crashes (P0), security gaps, infrastructure misconfigurations, degraded services, and build failures. All fixes were validated with 425 smoke tests passing and 8772 unit tests passing.

---

## Fix Summary Table | جدول ملخص الإصلاحات

| # | Issue | Category | Files Changed | Status |
|---|-------|----------|---------------|--------|
| 1 | knowledge-graph crash: bad `cors_config` import, missing `shared/` in Docker | Crash (P0) | `knowledge-graph/Dockerfile`, `knowledge-graph/src/main.py` | Fixed |
| 2 | copilot-api crash: missing `apps/services/shared` overlay in Docker | Crash (P0) | `copilot-api/Dockerfile` | Fixed |
| 3 | pest-detection-service crash: missing `apps/services/shared` overlay in Docker | Crash (P0) | `pest-detection-service/Dockerfile` | Fixed |
| 4 | NATS plaintext passwords in config | Security | `config/nats/nats.conf`, `config/nats/nats-secure.conf` | Fixed |
| 5 | etcd missing TLS and auth | Security | `docker-compose.tls.yml`, `infrastructure/core/etcd/init-auth.sh` | Fixed |
| 6 | PgBouncer no TLS support | Security | `infrastructure/core/pgbouncer/pgbouncer.ini` | Fixed |
| 7 | Weak default passwords in `.env` templates | Security | `.env.development.template`, `.env.example` | Fixed |
| 8 | 7 services missing bcrypt/pyotp/qrcode deps | Security | 7 `requirements.txt` files | Fixed |
| 9 | MQTT inefficient healthcheck (`pub` instead of `sub`) | Infrastructure | `infrastructure/core/mqtt/mosquitto.conf` | Fixed |
| 10 | MinIO outdated image | Infrastructure | `docker-compose.yml` | Fixed |
| 11 | Milvus clock drift (missing SYS_TIME cap, etcd TLS) | Infrastructure | `config/milvus/milvus.yaml`, `docker-compose.yml` | Fixed |
| 12 | No Prometheus rules for service restarts | Infrastructure | `infrastructure/monitoring/prometheus/rules/service-restarts.yml` | Fixed |
| 13 | advisory-service Redis pointing to localhost | Degraded | `docker-compose.yml` | Fixed |
| 14 | agent-registry Redis only enabled in production | Degraded | `agent-registry/src/config.py`, `agent-registry/src/main.py` | Fixed |
| 15 | billing-core TOCTOU race condition | Degraded | `billing-core/src/repository.py` | Fixed |
| 16 | crop-intelligence SahoolException import error | Degraded | `crop-intelligence-service/src/main.py` | Fixed |
| 17 | LLM orchestrator missing transformers/crewai deps | Degraded | `llm-orchestrator-service/requirements.txt` | Fixed |
| 18 | Rollup platform mismatch (win32 in Linux lockfile) | Build | `package-lock.json` | Fixed |
| 19 | NumPy 2.x ABI mismatch with torch/transformers | Build | `constraints.txt`, `docker/constraints-ai.txt` | Fixed |
| 20 | Prisma v7 auto-upgrade risk (drops url/directUrl) | Build | 4 NestJS `package.json` files | Fixed |

---

## Details by Category | التفاصيل حسب الفئة

### 1. Container Crashes (P0) | أعطال الحاويات

Three services failed to start entirely:

- **knowledge-graph**: The `cors_config` import referenced a non-existent path. Fixed the import and added `COPY shared/ /app/shared/` to the Dockerfile so the shared Python library is available at runtime.
- **copilot-api**: Missing the `apps/services/shared` overlay directory. Added `COPY` directive to Dockerfile.
- **pest-detection-service**: Same missing overlay issue as copilot-api. Added `COPY` directive.

### 2. Security | الأمان

- **NATS bcrypt passwords**: Replaced plaintext `$NATS_ADMIN_PASSWORD` env-var references in `nats.conf` with pre-hashed bcrypt (`$2b$`) values. Added `nats-secure.conf` with hardened settings. Updated unit test assertions to accept bcrypt hashes.
- **etcd TLS**: Enabled `--auto-tls` and `--peer-auto-tls` in `docker-compose.tls.yml`. Added `init-auth.sh` for JWT auth token bootstrapping. Added `SYS_TIME` capability for WSL2/container clock drift.
- **PgBouncer TLS**: Set `server_tls_sslmode = prefer` and `client_tls_sslmode = allow` in `pgbouncer.ini` with an upgrade ladder path documented in comments.
- **Weak passwords**: Strengthened all default dev passwords in `.env.development.template` and `.env.example` (e.g., `sahool_dev_2026!secure` instead of `password`).
- **Missing auth deps**: Added `bcrypt`, `pyotp`, and `qrcode[pil]` to 7 services that import `shared/auth/` but lacked the transitive dependencies: advisory-service, ai-agents-service, logistics-service, crm-service, lowcode-engine, notification-service, iot-gateway.

### 3. Infrastructure | البنية التحتية

- **MQTT healthcheck**: Changed from `mosquitto_pub` (creates connection + publishes) to `mosquitto_sub -W 1` (lightweight subscribe with 1s timeout) in `mosquitto.conf`.
- **MinIO update**: Bumped image to `minio/minio:RELEASE.2025-03-12T18-04-18Z` in `docker-compose.yml`. Added parity/erasure-coding warnings.
- **Milvus clock drift**: Added `config/milvus/milvus.yaml` with etcd TLS endpoint configuration. Added `SYS_TIME` capability to the Milvus container for clock synchronization.
- **Prometheus restart alerts**: Created `service-restarts.yml` with alert rules for container restart monitoring across all 73 services. Includes rules for high restart rates, CrashLoopBackOff, and OOM kills.
- **Monitoring compose**: Added restart rules volume mount to `docker-compose.monitoring.yml`.

### 4. Degraded Services | خدمات متدهورة

- **advisory-service Redis**: Environment variable pointed to `localhost` instead of Docker service name `redis`. Fixed in `docker-compose.yml`.
- **agent-registry Redis**: Redis was gated behind `ENVIRONMENT == "production"`, so dev/staging environments had no caching. Refactored `config.py` to support `REDIS_URL` env var and enable Redis in all environments. Added URL parsing for backward compatibility with host/port/password config.
- **billing-core race condition**: Replaced a SELECT-then-INSERT (TOCTOU race) pattern with PostgreSQL `INSERT ... ON CONFLICT DO UPDATE` for idempotent plan creation in `repository.py`.
- **crop-intelligence**: Fixed `SahoolException` import path to use correct shared module.
- **LLM orchestrator**: Added missing `transformers`, `crewai`, `crewai-tools`, and `langchain-community` to `requirements.txt`.
- **notification-service**: Fixed queue processor import and added credential setup docs.
- **Other config fixes**: Corrected `edge-orchestrator-service`, `whatsapp-bot-service`, `task-service`, and `vegetation-analysis-service` Redis/config references.

### 5. Build Fixes | إصلاحات البناء

- **Rollup platform mismatch**: `package-lock.json` was generated on Windows/WSL2, embedding `@rollup/rollup-win32-x64-msvc` as a resolved optional dependency. Regenerated on Linux to resolve `@rollup/rollup-linux-x64-gnu` instead.
- **NumPy 2.x ABI break**: AI services using torch/transformers compiled against NumPy 1.x would crash with NumPy 2.x installed. Pinned `numpy<2.0.0` in `constraints.txt` and `docker/constraints-ai.txt`.
- **Prisma v7 prevention**: Pinned `prisma` and `@prisma/client` to `~5.22.0` (patch-only range) in 4 NestJS services (chat-service, marketplace-service, iot-service, disaster-assessment) to prevent accidental upgrade to Prisma v7 which removes `url`/`directUrl` from schema.

---

## Verification | التحقق

| Test Suite | Result |
|------------|--------|
| Smoke tests (import verification) | 425 passed |
| Unit tests | 8772 passed |
| NATS config tests | Updated and passing |

---

## Commits | الالتزامات

| Hash | Message |
|------|---------|
| `9f339d4` | fix: resolve container crashes, security gaps, and dependency issues |
| `38a5420` | fix(web): regenerate package-lock.json for Linux platform |
| `601ad0c` | fix: complete remaining container audit findings - security, TLS, infra, and service fixes |
| `44f3659` | fix: agent-registry Redis config and billing-core race condition |
| `fddc931` | test: update NATS config test to accept bcrypt password hashes |

---

## Files Changed | الملفات المتغيرة

44 files across 5 commits. Key areas:

- `apps/services/` - 22 service files (Dockerfiles, requirements, source)
- `config/` - NATS, Milvus configuration
- `infrastructure/` - etcd, MQTT, PgBouncer, Prometheus
- `docker-compose*.yml` - Compose stack updates
- `constraints.txt` - Python dependency pins
- `package-lock.json` - Node.js lockfile regeneration
- `.env.*` - Environment template hardening

---

_Generated: 2026-03-15_
