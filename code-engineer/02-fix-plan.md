# SAHOOL Platform - Fix Plan

**Generated:** 2026-01-08T21:10:00Z
**Engineer:** Code Engineer Agent
**Total Fixes:** 8 critical + 4 recommended

---

## Fix Order Strategy

Fixes are ordered by:
1. **Dependency chain** - Infrastructure before services
2. **Impact scope** - Wider impact fixes first
3. **Risk level** - Lower risk fixes first

```
Fix 1: .env file → Unblocks ALL services
Fix 2: PgBouncer → Enables database
Fix 3: Certificates directories → Enables volume mounts
Fix 4: .env.example missing vars → Prevents future errors
Fix 5: Kong port mismatch → Fixes code-review route
Fix 6: Kong non-existent services → Prevents healthcheck failures
Fix 7: Ollama optional profile → Allows GPU-less deployment
Fix 8: Health check alignment → Improves monitoring
```

---

## Fix 1: Create .env File from Template

### Service
**Target:** Environment Configuration
**Symptom:** `error: POSTGRES_PASSWORD is required` (and 25+ similar errors)
**Evidence:** `.env` file does not exist; `.env.example` exists with template values
**Root Cause:** No environment file created for deployment

### Proposed Changes

**File:** `.env` (new file)

**Action:** Copy `.env.example` to `.env` with development-safe placeholder values

```bash
cp .env.example .env
# Then edit .env with development values
```

**Required Substitutions for Development:**

| Variable | Example Value |
|----------|---------------|
| POSTGRES_PASSWORD | dev_postgres_password_123 |
| REDIS_PASSWORD | dev_redis_password_123 |
| JWT_SECRET_KEY | dev_jwt_secret_key_at_least_32_chars_long |
| NATS_USER | sahool_app |
| NATS_PASSWORD | dev_nats_password_123 |
| NATS_ADMIN_USER | nats_admin |
| NATS_ADMIN_PASSWORD | dev_nats_admin_password_123 |
| NATS_MONITOR_USER | nats_monitor |
| NATS_MONITOR_PASSWORD | dev_nats_monitor_password_123 |
| NATS_CLUSTER_USER | nats_cluster |
| NATS_CLUSTER_PASSWORD | dev_nats_cluster_password_123 |
| NATS_SYSTEM_USER | nats_system |
| NATS_SYSTEM_PASSWORD | dev_nats_system_password_123 |
| NATS_JETSTREAM_KEY | dev_jetstream_encryption_key_32chr |
| ETCD_ROOT_USERNAME | root |
| ETCD_ROOT_PASSWORD | dev_etcd_password_123 |
| MINIO_ROOT_USER | sahool_minio_admin_dev |
| MINIO_ROOT_PASSWORD | dev_minio_password_secure_123 |
| STARTER_JWT_SECRET | dev_starter_jwt_secret_32_chars_min |
| PROFESSIONAL_JWT_SECRET | dev_professional_jwt_secret_32_chr |
| ENTERPRISE_JWT_SECRET | dev_enterprise_jwt_secret_32_chars |
| RESEARCH_JWT_SECRET | dev_research_jwt_secret_32_chars_x |
| ADMIN_JWT_SECRET | dev_admin_jwt_secret_32_characters |

### Validation Steps
```bash
docker compose config  # Should not show any errors
```

### Risk Level
**LOW** - Creates new file, does not modify existing

### Rollback Plan
```bash
rm .env
```

---

## Fix 2: Fix PgBouncer Hardcoded Password

### Service
**Target:** pgbouncer
**Symptom:** FATAL: password authentication failed
**Evidence:** `infrastructure/core/pgbouncer/pgbouncer.ini:8` contains hardcoded password
**Root Cause:** Password hardcoded instead of environment variable placeholder

### Proposed Changes

**File:** `infrastructure/core/pgbouncer/pgbouncer.ini`

**Before:**
```ini
sahool = host=postgres port=5432 dbname=sahool user=sahool password=change_this_secure_password_in_production
```

**After:**
```ini
; Password is injected via DB_PASSWORD environment variable by edoburu/pgbouncer image
; Do not specify password here - it will be added automatically
sahool = host=postgres port=5432 dbname=sahool
```

**Also update line 14:**
```ini
; Use wildcard for dynamic databases
* = host=postgres port=5432
```

### Validation Steps
```bash
docker compose up -d pgbouncer
docker compose logs pgbouncer | grep -i "error\|fail"
docker compose exec pgbouncer psql -h localhost -p 6432 -U sahool -d sahool -c "SELECT 1"
```

### Risk Level
**LOW** - Configuration change, easily reversible

### Rollback Plan
```bash
git checkout infrastructure/core/pgbouncer/pgbouncer.ini
```

---

## Fix 3: Create Required Directories for Volume Mounts

### Service
**Target:** minio, multiple TLS-enabled services
**Symptom:** Container fails to start due to missing mount path
**Evidence:** `secrets/minio-certs/production/certs` directory does not exist
**Root Cause:** Required directories not created

### Proposed Changes

**Action:** Create empty directories with placeholder files

```bash
# MinIO certs directory
mkdir -p secrets/minio-certs/production/certs
touch secrets/minio-certs/production/certs/.gitkeep

# TLS certs directory (already partially exists)
mkdir -p config/certs
touch config/certs/.gitkeep

# Kong SSL directory
mkdir -p infrastructure/gateway/kong/ssl
touch infrastructure/gateway/kong/ssl/.gitkeep
```

**Add .gitignore entries:**
```
# Secrets - never commit actual certificates
secrets/minio-certs/production/certs/*.crt
secrets/minio-certs/production/certs/*.key
secrets/minio-certs/production/certs/*.pem
config/certs/*.crt
config/certs/*.key
config/certs/*.pem
```

### Validation Steps
```bash
ls -la secrets/minio-certs/production/certs/
ls -la config/certs/
docker compose config | grep -A2 "minio-certs"
```

### Risk Level
**LOW** - Creates empty directories only

### Rollback Plan
```bash
rm -rf secrets/minio-certs
```

---

## Fix 4: Add Missing Environment Variables to .env.example

### Service
**Target:** Environment template
**Symptom:** docker-compose.yml requires variables not in .env.example
**Evidence:** NATS_SYSTEM_USER, NATS_SYSTEM_PASSWORD, NATS_JETSTREAM_KEY missing
**Root Cause:** .env.example not synchronized with docker-compose.yml

### Proposed Changes

**File:** `.env.example`

**Add after line 127 (NATS_CLUSTER_PASSWORD):**
```bash
# NATS System Account (for internal monitoring)
NATS_SYSTEM_USER=nats_system
NATS_SYSTEM_PASSWORD=change_this_secure_nats_system_password_32_chars

# NATS JetStream Encryption Key (AES-256)
# Generate with: openssl rand -hex 32
NATS_JETSTREAM_KEY=change_this_jetstream_encryption_key_64_hex_chars
```

### Validation Steps
```bash
grep -E "NATS_SYSTEM|NATS_JETSTREAM" .env.example
docker compose config 2>&1 | grep -i "nats"
```

### Risk Level
**LOW** - Updates template file only

### Rollback Plan
```bash
git checkout .env.example
```

---

## Fix 5: Fix Kong code-review-service Port

### Service
**Target:** kong (API Gateway)
**Symptom:** /api/v1/code-review returns 502 Bad Gateway
**Evidence:** Kong upstream targets port 8096, service runs on 8102
**Root Cause:** Kong config has wrong port number

### Proposed Changes

**File:** `infrastructure/gateway/kong/kong.yml`

**Before (line 462):**
```yaml
- name: code-review-upstream
  targets:
    - target: code-review-service:8096
```

**After:**
```yaml
- name: code-review-upstream
  targets:
    - target: code-review-service:8102
```

**Also update health check path (line 467):**
```yaml
healthchecks:
  active:
    http_path: /health  # Matches docker-compose healthcheck
```

### Validation Steps
```bash
docker compose restart kong
curl -f http://localhost:8000/api/v1/code-review/health || echo "Still failing"
docker compose logs kong | grep code-review
```

### Risk Level
**LOW** - Configuration change

### Rollback Plan
```bash
git checkout infrastructure/gateway/kong/kong.yml
docker compose restart kong
```

---

## Fix 6: Comment Out Non-Existent Kong Upstreams/Services

### Service
**Target:** kong (API Gateway)
**Symptom:** DNS resolution failures, healthcheck timeouts
**Evidence:** 16 services defined in Kong but not in docker-compose.yml
**Root Cause:** Kong config includes services not yet implemented

### Proposed Changes

**File:** `infrastructure/gateway/kong/kong.yml`

**Action:** Comment out upstreams and services for non-existent services:

Services to comment out:
- user-service-upstream (lines 489-514)
- agent-registry-upstream (lines 516-541)
- ai-agents-core-upstream (lines 543-568)
- globalgap-compliance-upstream (lines 570-595)
- analytics-service-upstream (lines 597-622)
- reporting-service-upstream (lines 624-649)
- integration-service-upstream (lines 651-676)
- audit-service-upstream (lines 678-703)
- export-service-upstream (lines 705-730)
- import-service-upstream (lines 732-757)
- admin-dashboard-upstream (lines 759-784)
- monitoring-service-upstream (lines 786-811)
- logging-service-upstream (lines 813-838)
- tracing-service-upstream (lines 840-865)
- cache-service-upstream (lines 867-892)
- search-service-upstream (lines 894-919)

And corresponding services section entries (lines 2308-2972)

**Alternative:** Set these upstreams to a placeholder target that returns 503

### Validation Steps
```bash
docker compose exec kong kong config parse /kong/declarative/kong.yml
docker compose restart kong
docker compose logs kong | grep -i "error\|warn"
```

### Risk Level
**MEDIUM** - Large configuration change, but easily reversible

### Rollback Plan
```bash
git checkout infrastructure/gateway/kong/kong.yml
docker compose restart kong
```

---

## Fix 7: Make Ollama Optional with Profile

### Service
**Target:** ollama, ollama-model-loader, code-review-service
**Symptom:** Services fail on non-GPU systems
**Evidence:** `driver: nvidia` device requirement
**Root Cause:** GPU is required but not available in all environments

### Proposed Changes

**File:** `docker-compose.yml`

**Add profile to ollama service (around line 374):**
```yaml
ollama:
  profiles:
    - gpu
    - ai
  image: ollama/ollama:0.5.4
  # ... rest of config
```

**Add profile to ollama-model-loader (around line 422):**
```yaml
ollama-model-loader:
  profiles:
    - gpu
    - ai
  image: curlimages/curl:8.11.1
  # ... rest of config
```

**Make code-review-service ollama dependency optional (around line 473):**
```yaml
code-review-service:
  # ... existing config
  depends_on:
    ollama:
      condition: service_healthy
      required: false  # Make optional
```

Or add profile:
```yaml
code-review-service:
  profiles:
    - gpu
    - ai
```

### Validation Steps
```bash
# Without GPU services:
docker compose up -d

# With GPU services:
docker compose --profile gpu up -d
```

### Risk Level
**MEDIUM** - Changes service availability behavior

### Rollback Plan
```bash
git checkout docker-compose.yml
```

---

## Fix 8: Align Health Check Paths

### Service
**Target:** Multiple services
**Symptom:** Kong healthchecks may fail despite healthy services
**Evidence:** Kong uses `/healthz`, some services use `/health`
**Root Cause:** Inconsistent health endpoint naming

### Proposed Changes

**File:** `infrastructure/gateway/kong/kong.yml`

**Update healthcheck paths to match actual service endpoints:**

| Upstream | Current Path | Correct Path |
|----------|--------------|--------------|
| iot-gateway-upstream | /healthz | /health |
| marketplace-service-upstream | /healthz | /api/v1/healthz |
| mcp-server-upstream | /health | /health (OK) |
| code-review-upstream | /health | /health (OK) |

### Validation Steps
```bash
# Test each service health endpoint
curl http://localhost:8106/health  # iot-gateway
curl http://localhost:3010/api/v1/healthz  # marketplace
```

### Risk Level
**LOW** - Configuration only

### Rollback Plan
```bash
git checkout infrastructure/gateway/kong/kong.yml
```

---

## Implementation Order Summary

| Order | Fix | Time Est. | Dependencies |
|-------|-----|-----------|--------------|
| 1 | Create .env | 5 min | None |
| 2 | Fix PgBouncer | 2 min | None |
| 3 | Create directories | 2 min | None |
| 4 | Update .env.example | 2 min | None |
| 5 | Fix Kong port | 2 min | Fix 1 |
| 6 | Comment Kong services | 10 min | Fix 5 |
| 7 | Make Ollama optional | 5 min | None |
| 8 | Align health paths | 5 min | Fix 5 |

**Total estimated time:** ~35 minutes

---

## Post-Fix Validation Checklist

- [ ] `docker compose config` runs without errors
- [ ] `docker compose up -d postgres` starts successfully
- [ ] `docker compose up -d pgbouncer` connects to postgres
- [ ] `docker compose up -d redis` starts with authentication
- [ ] `docker compose up -d nats` starts with authentication
- [ ] `docker compose up -d kong` loads declarative config
- [ ] `docker compose ps` shows all expected services healthy
- [ ] `curl http://localhost:8000/health` returns 200
