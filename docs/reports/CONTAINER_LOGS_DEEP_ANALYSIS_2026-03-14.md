# SAHOOL Container Logs Deep Analysis Report

**Date:** 2026-03-14
**Containers Analyzed:** 73 (all succeeded)
**Severity Scale:** CRITICAL > HIGH > MEDIUM > LOW

---

## Executive Summary

Deep analysis of all 73 SAHOOL containers reveals **12 critical issues**, **18 high-severity issues**, and **25+ medium/low findings** across infrastructure, microservices, and configuration layers. While all containers report as running, multiple systemic issues affect reliability, security, and data integrity.

### Issue Distribution

| Category | Critical | High | Medium | Low |
|----------|----------|------|--------|-----|
| PostgreSQL & Init Scripts | 2 | 2 | 2 | 1 |
| PgBouncer | 3 | 1 | 2 | 0 |
| Kong API Gateway | 1 | 3 | 2 | 1 |
| Redis | 1 | 2 | 2 | 1 |
| NATS | 0 | 2 | 2 | 0 |
| Vault | 2 | 0 | 0 | 1 |
| Milvus/Qdrant/etcd | 1 | 1 | 1 | 0 |
| Microservices (Python) | 2 | 5 | 6 | 2 |
| Docker Compose Config | 0 | 2 | 4 | 2 |
| **Total** | **12** | **18** | **21** | **8** |

---

## 1. Infrastructure: PostgreSQL (sahool-postgres)

### 1.1 CRITICAL: `01-research-expansion.sql` Fails on Missing `users` Table

**Log Evidence:**
```
sahool-postgres | ERROR: relation "users" does not exist
sahool-postgres | STATEMENT: CREATE TABLE IF NOT EXISTS research_sites (
    contact_person UUID REFERENCES users(id), ...
)
```

**Root Cause:** The `users` table is managed by Prisma ORM in `user-service` (NestJS). It is created only when `prisma migrate deploy` runs on service startup. However, `01-research-expansion.sql` executes during Docker init (before any NestJS service starts) and contains **11 foreign key references** to `users(id)`.

**Affected Tables (11 FK references):**

| Table | Column |
|-------|--------|
| `research_sites` | `contact_person` |
| `protocol_templates` | `created_by` |
| `sample_batches` | `created_by` |
| `sample_analysis_results` | `analyzed_by` |
| `sample_analysis_results` | `verified_by` |
| `research_data_points` | `recorded_by` |
| `experiment_locks` | `locked_by` |
| `research_reports` | `reviewed_by` |
| `research_reports` | `approved_by` |
| `research_reports` | `created_by` |
| `statistical_analyses` | `performed_by` |

**Additionally Missing Enums:** `sample_type`, `experiment_status`, `protocol_status`, `governance_level`

**Impact:** All research-related tables fail to create. `research-core` service has incomplete schema.

**Fix:** `infrastructure/core/postgres/init/01-research-expansion.sql`
- Option A (Recommended): Remove FK constraints, add via post-startup migration
- Option B: Create minimal `users` stub in `00-init-sahool.sql` with `id UUID PRIMARY KEY`

---

### 1.2 CRITICAL: `04-mlflow-db.sql` Uses psql-Only Syntax

**File:** `infrastructure/core/postgres/init/04-mlflow-db.sql` (Line 24)

```sql
SELECT 'CREATE DATABASE mlflow'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'mlflow')\gexec
```

**Root Cause:** `\gexec` is a psql meta-command, not valid SQL. Additionally, `CREATE DATABASE` cannot execute within a transaction block.

**Impact:** MLflow database creation fails silently during init. MLflow service will fail to store experiment data.

**Fix:**
```sql
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'mlflow') THEN
        PERFORM dblink_exec('dbname=postgres', 'CREATE DATABASE mlflow');
    END IF;
END $$;
```

---

### 1.3 HIGH: PgBouncer `auth_query` Schema Missing at First Boot

**Log Evidence:**
```
sahool-postgres | ERROR: schema "pgbouncer" does not exist at character 20
sahool-postgres | STATEMENT: SELECT passwd FROM pgbouncer.get_auth('sahool')
```

**Timeline:**
```
T=0.8s  PostgreSQL accepts connections (init scripts still running)
T=3.0s  PgBouncer connects, tries auth_query → FAILS
T=3.0s  PgBouncer falls back to plaintext passwords
T=18s   02-pgbouncer-user.sql creates the schema (too late)
```

**Fix:** Add readiness dependency so PgBouncer waits for all init scripts to complete.

---

### 1.4 HIGH: Missing `calibration_run` Table Query

**Log Evidence:**
```
sahool-postgres | ERROR: relation "calibration_run" does not exist
sahool-postgres | STATEMENT: SELECT id::text, tenant_id, field_id ... FROM calibration_run WHERE status = 'queued'
```

**Root Cause:** Service queries `calibration_run` before `07-calibration-tables.sql` finishes executing.

---

### 1.5 HIGH: `06-equipment-fix.sql` Type Mismatch

**File:** `infrastructure/core/postgres/init/06-equipment-fix.sql` (Line 12)

Creates `equipment_id VARCHAR(50)` but copies from `id UUID`, causing implicit type coercion. Should use `UUID` type.

---

### 1.6 MEDIUM: Unclean Shutdown / WAL Recovery

```
sahool-postgres | database system was not properly shut down; automatic recovery in progress
sahool-postgres | invalid magic number 0000 in WAL segment 000000010000000000000002
sahool-postgres | checkpoint complete: wrote 2133 buffers (13.0%)
```

**Fix:** Already addressed with `stop_grace_period: 30s` (added 2026-03-13).

---

## 2. Infrastructure: PgBouncer (sahool-pgbouncer)

### 2.1 CRITICAL: Plaintext Password Fallback

```
sahool-pgbouncer | [WARN] Using plaintext password for auth_user (SCRAM hash unavailable)
```

PgBouncer stores the plaintext password in `/etc/pgbouncer/runtime/userlist.txt` (even with `chmod 600`).

**Fix:** Ensure PgBouncer starts only after all init scripts complete, or auto-restart after init.

---

### 2.2 CRITICAL: Timestamp Overflow in Connection Ages (Unsigned Integer Underflow)

```
sahool-pgbouncer | LOG: closing because: client_idle_timeout (age=18446744073707s)
sahool-pgbouncer | LOG: closing because: server lifetime over (age=18446744073704s)
```

**Analysis:** `18446744073707 ≈ 2^64 - 5` — classic unsigned integer underflow. Connections are being terminated prematurely because PgBouncer calculates a massive positive age instead of the actual duration.

**Impact:** ~30 connections from various services terminated with incorrect age values.

**Fix:**
1. Verify Docker host time synchronization (NTP)
2. Consider upgrading PgBouncer from 1.23.1 if known bug

---

### 2.3 CRITICAL: Healthcheck Variable Scope Bug

**File:** `infrastructure/core/pgbouncer/healthcheck.sh` (Lines 202-223)

```bash
echo "$POOL_DATA" | while read -r ... do
    TOTAL_CL_ACTIVE=$((TOTAL_CL_ACTIVE + cl_active))  # Lost in subshell!
done
echo $TOTAL_CL_ACTIVE  # Always prints 0
```

**Root Cause:** The `while` loop runs in a subshell due to the pipe (`|`). All variable assignments inside are lost when the subshell exits.

**Impact:** Pool utilization metrics are always reported as 0%, making the healthcheck unreliable.

**Fix:** Use process substitution:
```bash
while read -r ... ; do
    ...
done < <(echo "$POOL_DATA")
```

---

### 2.4 HIGH: All Connections Without TLS

Every connection shows `tls=no`:
```ini
# infrastructure/core/pgbouncer/pgbouncer.ini
server_tls_sslmode = disable
client_tls_sslmode = disable
```

All database traffic is unencrypted. Acceptable for development only.

---

### 2.5 MEDIUM: Rapid Connect/Disconnect from Service 172.18.0.51

7 connections within 640ms from a single service, each immediately disconnecting. Likely health check probes or failing migration retries.

---

### 2.6 MEDIUM: Entrypoint Permission Bypass

**File:** `infrastructure/core/pgbouncer/entrypoint.sh` (Lines 19-20)

```bash
chmod 777 /etc/pgbouncer/runtime 2>/dev/null || true
```

Silent permission failures could cause runtime file generation to fail, leading to PgBouncer startup failure with no clear error.

---

## 3. Infrastructure: Kong API Gateway (sahool-kong)

### 3.1 CRITICAL: Startup Timeout Errors Across All Workers

```
[error] 1283#0: *26 [lua] worker.lua:138: communicate(): failed to connect: timeout
[error] 1282#0: *30 [lua] worker.lua:138: communicate(): failed to connect: timeout
... (12 timeout errors across 9 workers)
```

**Root Cause:** Originally 24 auto-detected workers caused contention during declarative config synchronization. Fixed by reducing to `KONG_NGINX_WORKER_PROCESSES: 4`.

**Impact:** Temporary - requests during first ~15s of startup may fail.

---

### 3.2 HIGH: Event Broker Connection Failures

```
[error] broker.lua:111: run(): failed to init socket: nginx output filter error
[error] broker.lua:208: run(): event broker failed: connection reset by peer
[error] broker.lua:184: failed to send event: broken pipe
```

10 connection errors cascading from config loading timeouts. Self-resolving after ~20s.

---

### 3.3 HIGH: Wildcard CORS Origin

**File:** `infrastructure/gateway/kong/kong.yml` (Line 28)

```yaml
origins: ["*"]  # Replace with ${KONG_CORS_ORIGINS:-*} in production
```

Template syntax is NOT implemented — `*` is hardcoded. All origins are allowed.

---

### 3.4 HIGH: Missing Redis Password in Rate Limiting

**File:** `infrastructure/gateway/kong/kong-rate-limiting-tiers.yml` (40+ occurrences)

Rate limiting plugins reference `redis_host: kong-redis` but **no `redis_password` field**. If Redis requires authentication, all rate limiting will fail silently.

---

### 3.5 MEDIUM: Exponential Backoff Sleep Flooding (200+ Log Entries Per Startup)

Each worker performs blocking sleep (0.001s → 0.5s) while waiting for config, generating excessive log noise.

---

## 4. Infrastructure: Redis (sahool-redis)

### 4.1 CRITICAL: ACL Users Commented Out

**File:** `infrastructure/redis/redis-secure.conf` (Lines 113-131)

All ACL user definitions are **commented out**:
```ini
# user sahool_app on >${REDIS_APP_PASSWORD} ~session:* ~cache:* +@read +@write...
# user kong_gateway on >${REDIS_KONG_PASSWORD} ~ratelimit:* +@read +@write...
# user sahool_readonly on >${REDIS_READONLY_PASSWORD} ~* +@read +@connection...
# user sahool_admin on >${REDIS_ADMIN_PASSWORD} ~* +@all
```

**Impact:** ACL is not enforced. Any client with `requirepass` can execute ANY command on ALL keys, defeating the purpose of access control.

---

### 4.2 HIGH: Production Config Binds to Localhost Only

**File:** `infrastructure/redis/redis-production.conf` (Line 26)

```ini
bind 127.0.0.1 ::1
```

In Docker Compose, services communicate via container names — this config prevents all container-to-container connections.

---

### 4.3 HIGH: Redis Configuration Inconsistency Across Kong

| File | Redis Host | Password |
|------|-----------|----------|
| `kong.yml` | `kong-redis` | **None** |
| `kong-v2-routes.yml` | `redis` | `${REDIS_PASSWORD}` |
| `kong-rate-limiting-tiers.yml` | `kong-redis` | **None** |

Multiple Redis hostnames used; password handling inconsistent.

---

## 5. Infrastructure: NATS (sahool-nats)

### 5.1 HIGH: Development Credentials in Plaintext

**File:** `config/nats/nats.conf` (Lines 1-17)

Credentials transmitted in plaintext without TLS. No environment check or mode switching in `docker-compose.yml`.

---

### 5.2 HIGH: No Production TLS Enforcement

**File:** `docker-compose.yml` (Lines 274-275)

```yaml
- ./config/nats/nats.conf:/etc/nats/nats.conf:ro
# No conditional for production TLS config
```

No mechanism to switch to `nats-secure.conf` for production.

---

### 5.3 MEDIUM: Cluster Configs Missing HTTP Port Binding Restriction

**Files:** `config/nats/nats-cluster-node{1,2,3}.conf`

`http_port: 8222` accepts connections on all interfaces. Should restrict to `127.0.0.1:8222`.

---

## 6. Infrastructure: Vault (sahool-vault)

### 6.1 CRITICAL: Unsubstituted cluster_addr Placeholder

**File:** `infrastructure/core/vault/vault-production.hcl` (Line 68)

```hcl
cluster_addr = "https://VAULT_NODE_IP:8201"
```

Literal `VAULT_NODE_IP` is never substituted. Vault HA clustering will fail.

---

### 6.2 CRITICAL: No Auto-Unseal Configured

**File:** `infrastructure/core/vault/vault-production.hcl` (Lines 74-102)

All three cloud-based auto-unseal methods (AWS KMS, Azure Key Vault, GCP Cloud KMS) are commented out. Vault will require **manual unsealing** on every restart.

---

## 7. Infrastructure: Milvus, Qdrant, etcd

### 7.1 CRITICAL: Milvus/etcd-auth Dependency Race Condition

**File:** `docker-compose.yml` (Lines 1087-1094)

Milvus depends on `etcd` and `minio` being healthy, but doesn't wait for `etcd-init` (authentication initializer). When etcd-auth profile is enabled, Milvus will fail with auth errors.

---

### 7.2 HIGH: Qdrant Healthcheck Only Verifies Port

```yaml
test: ["CMD-SHELL", "grep -q '18BD' /proc/net/tcp"]  # 0x18BD = 6333
```

Only checks if port 6333 is listening — doesn't verify Qdrant is actually accepting requests or serving data.

---

## 8. Microservices: Python FastAPI Services

### 8.1 CRITICAL: Missing DATABASE_URL Handling (12 Services)

**Affected Services:**
- `audit-service` (8114)
- `equipment-service` (8101)
- `field-intelligence` (8120)
- `hydrology-service` (8165)
- `leveling-optimizer-service` (8170)
- `advisory-service` (8093)
- `alert-service` (8113)
- `irrigation-smart` (8094)
- `notification-service` (8110)
- `crop-intelligence-service` (8095)
- `vegetation-analysis-service` (8090)
- `weather-service` (8092)

Services crash or fail silently if `DATABASE_URL` is not set. Lifespan context manager tries to create a database pool without proper validation.

---

### 8.2 CRITICAL: NATS Connection Failures Not Handled Downstream (14 Services)

Services log NATS connection failures as warnings but set `app.state.nc = None`. Downstream code doesn't always check before publishing:

```python
# Typical pattern - warning logged but code continues
nats_url = os.getenv("NATS_URL")
if nats_url:
    try:
        app.state.nc = await nats.connect(nats_url)
    except Exception as e:
        logger.warning(f"NATS connection failed: {e}")
        app.state.nc = None
# Later: app.state.nc.publish(...)  → AttributeError: 'NoneType' has no attribute 'publish'
```

---

### 8.3 HIGH: Connection Resource Leaks (8 Services)

**Affected Services:**
- `equipment-service` — Missing database pool close
- `notification-service` — Redis client may not close on error
- `edge-orchestrator-service` — Initializes managers before database
- `llm-orchestrator-service` — Trainer init depends on unvalidated settings
- `field-intelligence` — Rules engine initializes before DB connection validated
- `irrigation-smart` — Import nats conditionally but doesn't check before use
- `skills-service` — Missing comprehensive readiness checks
- `knowledge-graph` — Readiness depends on graph_service without health validation

---

### 8.4 HIGH: Missing /readyz Implementation (9 Services)

Only **11 of 20 analyzed services** fully implement both `/healthz` and `/readyz`. Services without proper readiness checks may be routed traffic before they're ready.

---

### 8.5 HIGH: No Connection State Tracking (16 Services)

Only 4 services track connection status (`app.state.db_connected`):
- `edge-orchestrator-service` ✓
- `field-intelligence` ✓
- `hydrology-service` ✓
- `leveling-optimizer-service` ✓

All other services lack centralized connection state tracking.

---

### 8.6 HIGH: Race Conditions in Lifespan Initialization (5 Services)

- `edge-orchestrator-service` — Initializes device_manager and ws_manager before database
- `llm-orchestrator-service` — Trainer depends on settings not fully validated
- `field-intelligence` — Rules engine initializes before DB connection validated
- `advisory-service` — Token revocation middleware optional import
- `pest-detection-service` — Vision service dependency checked during readiness, not startup

---

## 9. Cross-Service: Startup Race Condition

The root cause of multiple issues is a **startup race condition**:

```
T=0.0s   PostgreSQL starts, begins init scripts
T=0.0s   PgBouncer starts, waits for port 5432
T=0.0s   Kong starts
T=0.8s   PostgreSQL accepts connections (init scripts still running!)
T=3.0s   PgBouncer detects port → tries auth_query → FAILS → plaintext fallback
T=5.0s   Services start connecting through PgBouncer
T=5.0s   Some services query tables not yet created → ERRORS
T=10s    Kong workers loading config → TIMEOUTS between workers
T=15s    00-init-sahool.sql completes
T=16s    01-research-expansion.sql → FAILS (no users table)
T=18s    02-pgbouncer-user.sql creates pgbouncer schema (too late)
T=20s    Init scripts complete
T=25s    NestJS services start, run Prisma migrations
T=30s    user-service creates users table
T=35s    Platform stabilizes
```

**Key Problem:** PostgreSQL reports `service_healthy` (via `pg_isready`) before all init scripts finish. All services depending on `postgres: service_healthy` start too early.

---

## 10. Docker Compose: Dependency and Configuration Issues

### 10.1 HIGH: MLflow Missing Direct Postgres Dependency

MLflow depends only on `pgbouncer`, but pgbouncer can report healthy before postgres is fully initialized (race condition through transitive dependency).

### 10.2 HIGH: Irrigation-Smart Unreliable Healthcheck

Comment in docker-compose.yml: "healthcheck is unreliable - see PR #1213" — known but unresolved issue.

### 10.3 MEDIUM: Inconsistent Health Check Intervals

| Service | Interval | Start Period | Retries |
|---------|----------|-------------|---------|
| postgres | 15s | 60s | 8 |
| pgbouncer | 15s | 90s | 10 |
| redis | 30s | 30s | - |
| nats | 30s | 30s | - |
| kong | 15s | 45s | - |
| milvus | 30s | 90s | - |

No documented rationale for varying strategies.

### 10.4 MEDIUM: Services Missing Healthchecks

`ai-chat-assistant` has `depends_on` but no `healthcheck` defined.

---

## 11. Security Issues Summary

| # | Issue | Severity | Location |
|---|-------|----------|----------|
| S1 | PgBouncer plaintext password fallback | CRITICAL | pgbouncer entrypoint.sh |
| S2 | All PgBouncer connections without TLS | HIGH | pgbouncer.ini |
| S3 | Redis ACL users commented out | CRITICAL | redis-secure.conf |
| S4 | NATS credentials in plaintext (no TLS) | HIGH | nats.conf |
| S5 | Kong wildcard CORS origin (`*`) | HIGH | kong.yml |
| S6 | Kong rate limiting missing Redis password | HIGH | kong-rate-limiting-tiers.yml |
| S7 | Vault no auto-unseal (manual unsealing) | CRITICAL | vault-production.hcl |
| S8 | Kong audit endpoint uses HTTP (no TLS) | MEDIUM | kong-security.yml |
| S9 | PgBouncer admin reuses DB password | MEDIUM | entrypoint.sh |
| S10 | NATS cluster HTTP monitoring on all interfaces | MEDIUM | nats-cluster-*.conf |

---

## 12. Recommendations by Priority

### Immediate Action (Critical)

| # | Issue | Fix | File |
|---|-------|-----|------|
| C1 | `01-research-expansion.sql` fails | Remove FK constraints to `users`, add via post-migration | `infrastructure/core/postgres/init/01-research-expansion.sql` |
| C2 | `04-mlflow-db.sql` uses `\gexec` | Rewrite using `DO $$ ... EXECUTE` block | `infrastructure/core/postgres/init/04-mlflow-db.sql` |
| C3 | PgBouncer plaintext fallback | Add init-complete readiness gate | `infrastructure/core/pgbouncer/entrypoint.sh` |
| C4 | PgBouncer timestamp overflow | Verify NTP sync, consider PgBouncer upgrade | `docker-compose.yml` |
| C5 | Healthcheck variable scope bug | Use process substitution `< <(...)` | `infrastructure/core/pgbouncer/healthcheck.sh` |
| C6 | Redis ACL not enforced | Uncomment ACL user definitions | `infrastructure/redis/redis-secure.conf` |
| C7 | Vault cluster_addr placeholder | Replace with `${VAULT_NODE_IP}` or dynamic hostname | `infrastructure/core/vault/vault-production.hcl` |
| C8 | Vault no auto-unseal | Enable appropriate cloud KMS provider | `infrastructure/core/vault/vault-production.hcl` |
| C9 | Milvus/etcd-auth race | Add `etcd-init` dependency for Milvus | `docker-compose.yml` |
| C10 | 12 services crash on missing DATABASE_URL | Add environment validation before lifespan | Multiple `main.py` files |
| C11 | 14 services NoneType NATS errors | Add null-check before `nc.publish()` | Multiple `main.py` files |
| C12 | Kong worker startup timeouts | Already fixed (workers=4), monitor | `docker-compose.yml` |

### High Priority

| # | Issue | Fix |
|---|-------|-----|
| H1 | PgBouncer all connections without TLS | Enable `server_tls_sslmode = require` for production |
| H2 | Kong CORS wildcard origin | Implement env variable substitution |
| H3 | Kong rate limiting Redis password | Add `redis_password` to all rate limiting configs |
| H4 | NATS plaintext credentials | Add production TLS config switching |
| H5 | Redis production bind localhost | Change to `bind 0.0.0.0 ::` for Docker |
| H6 | Redis config inconsistency across Kong | Standardize Redis hostname and password |
| H7 | MLflow transitive dependency race | Add direct postgres health dependency |
| H8 | Irrigation-smart unreliable healthcheck | Fix per PR #1213 |
| H9 | 8 services with connection resource leaks | Add proper cleanup in lifespan shutdown |
| H10 | 9 services missing /readyz | Implement comprehensive readiness checks |
| H11 | 16 services no connection state tracking | Add `app.state.db_connected` pattern |
| H12 | 5 services lifespan race conditions | Reorder initialization sequence |
| H13 | Qdrant port-only healthcheck | Add HTTP health endpoint check |

### Medium Priority

| # | Issue | Fix |
|---|-------|-----|
| M1 | Equipment fix type mismatch | Use UUID type instead of VARCHAR(50) |
| M2 | PgBouncer entrypoint silent failures | Fail explicitly on permission errors |
| M3 | Kong sleep log flooding | Reduce log level or worker count |
| M4 | NATS cluster HTTP port exposure | Bind to localhost |
| M5 | Kong audit endpoint HTTP | Switch to HTTPS |
| M6 | PgBouncer admin password reuse | Require explicit admin password |
| M7 | Inconsistent health check intervals | Document rationale, standardize |
| M8 | ai-chat-assistant missing healthcheck | Add healthcheck |

---

## 13. Service Connection Map (from PgBouncer Logs)

| IP Address | Connections | Status |
|------------|-------------|--------|
| 172.18.0.20 | 2 | idle_timeout |
| 172.18.0.23 | 3 | idle_timeout |
| 172.18.0.33 | 2 | idle_timeout |
| 172.18.0.42 | 8 | idle_timeout (highest) |
| 172.18.0.51 | 7 | rapid reconnect (640ms) |
| 172.18.0.61 | 2 | active |
| 172.18.0.63 | 2 | active |
| 172.18.0.65 | 2 | active |
| 172.18.0.71 | 1 | active |
| *20 others* | 1-2 each | idle_timeout |

**Total unique service IPs:** 24 | **Total connections:** ~55 | **Terminated by idle_timeout (with overflow):** ~30

---

## 14. Architecture Recommendations

### 14.1 Implement Init-Complete Gate for PostgreSQL

```yaml
# docker-compose.yml
postgres:
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U sahool && test -f /tmp/init-complete"]
    interval: 15s
    timeout: 10s
    retries: 10
    start_period: 120s
```

Add `touch /tmp/init-complete` as the last line in a new `99-mark-ready.sql` init script.

### 14.2 Unified Startup Validation Framework

Create a shared startup validator for all Python services:

```python
# shared/startup.py
async def validate_startup(app: FastAPI, require_db=True, require_nats=False):
    """Validate all required connections before accepting traffic."""
    if require_db:
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            logger.error("DATABASE_URL not set")
            raise SystemExit(1)
        app.state.db_pool = await asyncpg.create_pool(db_url)
        app.state.db_connected = True

    if require_nats:
        nats_url = os.getenv("NATS_URL")
        if nats_url:
            app.state.nc = await nats.connect(nats_url)
            app.state.nats_connected = True
        else:
            app.state.nc = None
            app.state.nats_connected = False
```

### 14.3 PgBouncer Post-Init Restart

Add a post-init restart mechanism so PgBouncer re-attempts `auth_query` after init scripts complete:

```yaml
# docker-compose.yml
pgbouncer:
  depends_on:
    postgres:
      condition: service_healthy  # With init-complete gate
```

---

_Generated: 2026-03-14 | Analyst: Claude Code | Containers: 73 | Issues: 59 total (12 Critical, 18 High, 21 Medium, 8 Low)_
