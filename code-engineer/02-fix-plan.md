# 02-fix-plan.md — SAHOOL Platform Fix Plan

**Timestamp:** 2026-01-09T00:00:00Z
**Analysis:** Static Configuration Review
**Docker Status:** Not available in this environment

---

## Executive Summary

This fix plan addresses configuration issues identified through static analysis of the SAHOOL v16.0.0 platform. The fixes are ordered by priority and dependency chain.

---

## Pre-Requisite Fixes (Before Stack Start)

### Fix 0: Create Environment File

**Priority:** CRITICAL
**Impact:** Stack cannot start without this

**Symptom:**

- docker-compose uses `${VAR:?error message}` syntax
- Missing .env file causes immediate failure

**Evidence:**

```yaml
POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?POSTGRES_PASSWORD is required}
REDIS_PASSWORD: ${REDIS_PASSWORD:?REDIS_PASSWORD is required}
```

**Root Cause:**

- .env file does not exist (only .env.example template)

**Proposed Change:**

```bash
cd /home/user/sahool-unified-v15-idp
cp .env.example .env
# Edit .env with secure values
```

**Validation:**

```bash
# Verify all required vars are set
grep -E "^[A-Z].*=" .env | wc -l
```

**Risk Level:** Low
**Rollback:** Delete .env file

---

## Fix Order (Container by Container)

### Fix 1: PostgreSQL (postgres)

**Service:** postgres
**Priority:** CRITICAL (First in dependency chain)

**Symptom:**

- First service to start
- All other services depend on it

**Evidence:**

- depends_on chains start here
- Health check: `pg_isready -U sahool`

**Proposed Changes:**

1. Ensure POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB in .env
2. Verify init scripts exist in `infrastructure/core/postgres/init/`

**Validation:**

```bash
docker compose up -d postgres
docker compose ps postgres
docker compose logs postgres | tail -20
```

**Risk Level:** Low
**Rollback:** `docker compose down postgres`

---

### Fix 2: PgBouncer (pgbouncer)

**Service:** pgbouncer
**Priority:** HIGH (Connection pooler for all services)

**Symptom:**

- Authentication issues noted in comments
- Services may fail to connect

**Evidence:**

```yaml
# Line 96-98 in docker-compose.yml
# Health check - temporarily using a simple port check since authentication is failing
# TODO: Fix password authentication
```

**Root Cause:**

- PgBouncer auth_type configuration mismatch
- Password hash format may not match

**Proposed Changes:**

1. Verify pgbouncer.ini auth_type matches POSTGRES credentials
2. Check userlist.txt format

**Files to Review:**

- `infrastructure/core/pgbouncer/pgbouncer.ini`
- `infrastructure/core/pgbouncer/userlist.txt`

**Validation:**

```bash
docker compose up -d pgbouncer
docker compose exec pgbouncer pgbouncer -R
docker compose logs pgbouncer | tail -20
```

**Risk Level:** Medium
**Rollback:** Restart postgres and pgbouncer

---

### Fix 3: Redis (redis)

**Service:** redis
**Priority:** HIGH (Session & cache)

**Symptom:**

- Redis requires password authentication
- ACL configuration for multi-user access

**Evidence:**

```yaml
command:
  [
    "redis-server",
    "/usr/local/etc/redis/redis.conf",
    "--requirepass",
    "${REDIS_PASSWORD:?...}",
  ]
```

**Config File Status:** EXISTS

- `infrastructure/redis/redis-secure.conf` ✓

**Proposed Changes:**

1. Ensure REDIS_PASSWORD in .env
2. Optionally set ACL passwords for enhanced security

**Validation:**

```bash
docker compose up -d redis
docker compose exec redis redis-cli -a $REDIS_PASSWORD ping
```

**Risk Level:** Low
**Rollback:** `docker compose restart redis`

---

### Fix 4: NATS (nats)

**Service:** nats
**Priority:** HIGH (Message queue)

**Symptom:**

- Requires 10 authentication environment variables
- JetStream encryption key required

**Evidence:**

```yaml
NATS_USER: ${NATS_USER:?NATS_USER is required}
NATS_PASSWORD: ${NATS_PASSWORD:?NATS_PASSWORD is required}
# ... 8 more required vars
NATS_JETSTREAM_KEY: ${NATS_JETSTREAM_KEY:?NATS_JETSTREAM_KEY is required}
```

**Config File Status:** EXISTS

- `config/nats/nats.conf` ✓
- `config/nats/nats-secure.conf` ✓

**Proposed Changes:**

1. Set all 10 NATS environment variables in .env
2. Generate NATS_JETSTREAM_KEY (AES-256 key)

**Validation:**

```bash
docker compose up -d nats
curl http://localhost:8222/healthz
docker compose logs nats | tail -20
```

**Risk Level:** Medium
**Rollback:** `docker compose restart nats`

---

### Fix 5: MQTT Broker (mqtt)

**Service:** mqtt
**Priority:** MEDIUM (IoT communication)

**Symptom:**

- Password file generated dynamically at startup

**Evidence:**

```yaml
command: /bin/sh -c "mosquitto_passwd -b -c /mosquitto/config/passwd ..."
```

**Config File Status:** UNKNOWN

- `infrastructure/core/mqtt/mosquitto.conf` - need to verify

**Proposed Changes:**

1. Verify mosquitto.conf exists
2. Set MQTT_USER and MQTT_PASSWORD in .env

**Validation:**

```bash
docker compose up -d mqtt
docker compose logs mqtt | tail -20
```

**Risk Level:** Low
**Rollback:** `docker compose restart mqtt`

---

### Fix 6: TLS Certificates

**Priority:** LOW (Development can use non-TLS)

**Symptom:**

- TLS required for production
- Certificate directory exists but empty

**Evidence:**

- `config/certs/` contains only generation script
- No actual .crt, .key files

**Proposed Changes:**
For Development (non-TLS):

- No changes needed, use nats.conf (not nats-secure.conf)

For Production:

```bash
cd config/certs
./generate-internal-tls.sh
```

**Validation:**

```bash
ls -la config/certs/*.crt
ls -la config/certs/*.key
```

**Risk Level:** Low (dev), Medium (prod)
**Rollback:** Delete generated certificates

---

### Fix 7: Kong API Gateway

**Priority:** HIGH (API routing)

**Symptom:**

- Kong uses separate compose file
- Requires its own PostgreSQL database

**Evidence:**

- `infrastructure/gateway/kong/docker-compose.yml`
- Uses kong-database service

**Proposed Changes:**

1. Set KONG_PG_PASSWORD in .env
2. Run Kong migrations before gateway

**Validation:**

```bash
cd infrastructure/gateway/kong
docker compose up -d
curl http://localhost:8001/status
```

**Risk Level:** Medium
**Rollback:** `docker compose down` in kong directory

---

## Application Services (Bulk Fix)

### Fix 8: All Application Services

**Priority:** MEDIUM (After infrastructure stable)

**Symptom:**

- Services depend on infrastructure
- May have missing env vars

**Proposed Changes:**

1. Ensure DATABASE_URL points to pgbouncer:6432
2. Set service-specific environment variables
3. Start services in batches

**Validation:**

```bash
# Start core services first
docker compose up -d field-management-service marketplace-service

# Check health
curl http://localhost:3000/health
```

**Risk Level:** Low
**Rollback:** `docker compose down <service>`

---

## Summary Checklist

### Before Starting Stack:

- [ ] Create .env from .env.example
- [ ] Set all POSTGRES\_\* variables
- [ ] Set REDIS_PASSWORD
- [ ] Set all NATS\_\* variables (10 total)
- [ ] Set JWT_SECRET_KEY
- [ ] Verify config files exist

### Infrastructure Startup Order:

1. [ ] postgres
2. [ ] pgbouncer (wait for postgres healthy)
3. [ ] redis
4. [ ] nats
5. [ ] mqtt
6. [ ] qdrant

### Application Startup:

7. [ ] kong
8. [ ] core services (field-management, marketplace)
9. [ ] remaining services

### Validation:

- [ ] All containers running
- [ ] Health checks passing
- [ ] API endpoints responding

---

_Fix Plan generated by Code Engineer Agent_
_SAHOOL v16.0.0 - Configuration Fix Plan_
