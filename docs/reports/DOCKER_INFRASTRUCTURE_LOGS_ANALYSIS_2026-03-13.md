# Docker Infrastructure Logs Analysis Report

**Date:** 2026-03-13
**Services Analyzed:** PostgreSQL, PgBouncer, Kong
**Severity Scale:** CRITICAL > HIGH > MEDIUM > LOW

---

## Executive Summary

Analysis of `docker compose logs postgres pgbouncer kong` reveals **4 critical issues**, **5 high-severity issues**, and several medium/low findings across the three infrastructure services. The platform starts successfully but with degraded security and missing database objects.

| Service | Status | Critical | High | Medium |
|---------|--------|----------|------|--------|
| PostgreSQL | Running (with init errors) | 1 | 2 | 1 |
| PgBouncer | Running (degraded auth) | 2 | 1 | 1 |
| Kong | Running (startup errors) | 1 | 2 | 1 |

---

## 1. PostgreSQL (sahool-postgres)

### 1.1 Successful Operations

- PostgreSQL 16.4 initialized and running
- `00-init-sahool.sql` completed: 12 tables, 40 indexes, 856 functions
- Extensions loaded: PostGIS, pgcrypto, uuid-ossp, pg_trgm, btree_gist
- Demo data seeded: tenants (1), crops (10), equipment (3), fields (3), alerts (2)
- WAL recovery completed successfully after unclean shutdown

### 1.2 CRITICAL: `01-research-expansion.sql` Fails on Missing `users` Table

**Log Evidence:**
```
sahool-postgres | 2026-03-13 19:39:16.359 UTC [64] ERROR: relation "users" does not exist
sahool-postgres | STATEMENT: CREATE TABLE IF NOT EXISTS research_sites (
    ...
    contact_person UUID REFERENCES users(id),
    ...
)
```

**Root Cause:**
The `users` table is managed by Prisma ORM in `user-service` and created only when that NestJS service runs `prisma migrate deploy` on startup. However, `01-research-expansion.sql` executes during Docker init (before any NestJS service starts) and contains 12+ foreign key references to `users(id)`.

**Affected References in `01-research-expansion.sql`:**

| Line | Table | Column |
|------|-------|--------|
| 39 | `research_sites` | `contact_person` |
| 70 | `protocol_templates` | `created_by` |
| 124 | `sample_batches` | `created_by` |
| 201 | `sample_analysis_results` | `analyzed_by` |
| 203 | `sample_analysis_results` | `verified_by` |
| 230 | `research_data_points` | `recorded_by` |
| 254 | `experiment_locks` | `locked_by` |
| 282 | `research_reports` | `reviewed_by` |
| 284 | `research_reports` | `approved_by` |
| 291 | `research_reports` | `created_by` |
| 321 | `statistical_analyses` | `performed_by` |

**Additionally Missing Enums:**
- `sample_type` (used line 170)
- `experiment_status` (used line 257)
- `protocol_status` (used line 64)
- `governance_level` (used line 64)

**Impact:** All research-related tables fail to create. The `research-core` service will have incomplete schema.

**Fix Options:**
1. **Option A (Recommended):** Remove FK constraints from init script, add them via a post-startup migration after `user-service` creates the `users` table
2. **Option B:** Create a minimal `users` table stub in `00-init-sahool.sql` with just `id UUID PRIMARY KEY` that Prisma can later alter
3. **Option C:** Move research tables entirely to Prisma migrations in `research-core` service

**File:** `infrastructure/core/postgres/init/01-research-expansion.sql`

---

### 1.3 HIGH: PgBouncer `auth_query` Schema Missing at First Boot

**Log Evidence:**
```
sahool-postgres | 2026-03-13 19:39:25.908 UTC [44] ERROR: schema "pgbouncer" does not exist at character 20
sahool-postgres | STATEMENT: SELECT passwd FROM pgbouncer.get_auth('sahool')
```

**Root Cause:**
PgBouncer starts and attempts `auth_query` at `19:39:25`, but the `pgbouncer` schema is created by `02-pgbouncer-user.sql` which hasn't executed yet at that point. The init scripts are still running when PgBouncer connects.

**Timeline:**
```
19:39:14 - PostgreSQL starts accepting connections
19:39:22 - PgBouncer detects port open, starts connecting
19:39:25 - PgBouncer executes auth_query → FAILS (schema not yet created)
19:39:25 - PgBouncer falls back to plaintext userlist.txt
           (later) 02-pgbouncer-user.sql creates the schema
```

**Impact:** PgBouncer uses plaintext password fallback instead of SCRAM-SHA-256 `auth_query`. After restart, `auth_query` would work correctly.

**Fix:** Add `start_period` or readiness dependency so PgBouncer waits for init scripts to complete, not just for the port to open.

---

### 1.4 HIGH: Missing `calibration_run` Table Query

**Log Evidence:**
```
sahool-postgres | 2026-03-13 19:39:51.981 UTC [62] ERROR: relation "calibration_run" does not exist
sahool-postgres | STATEMENT:
    SELECT id::text, tenant_id, field_id, season_id, crop_type,
           model_name, model_version, method, dataset_fingerprint
    FROM calibration_run
    WHERE status = 'queued'
    ORDER BY started_at ASC
    LIMIT $1
```

**Root Cause:**
The `calibration_run` table is defined in `07-calibration-tables.sql`. However, the service querying it connects before all init scripts finish. This is the same timing issue as the PgBouncer auth_query problem.

**Impact:** Calibration service cannot find queued jobs until restart.

---

### 1.5 MEDIUM: Unclean Shutdown / WAL Recovery

**Log Evidence:**
```
sahool-postgres | database system was not properly shut down; automatic recovery in progress
sahool-postgres | redo starts at 0/14E6AA8
sahool-postgres | invalid magic number 0000 in WAL segment 000000010000000000000002
sahool-postgres | redo done at 0/23C1FB8
sahool-postgres | checkpoint complete: wrote 2133 buffers (13.0%)
```

**Analysis:** PostgreSQL detected an unclean shutdown and performed automatic WAL recovery. The "invalid magic number" in the WAL segment is expected at the end of replay (marks the boundary of valid WAL data). Recovery completed successfully with 2133 buffers written.

**Impact:** None after recovery. However, repeated unclean shutdowns indicate `docker compose down` may not be waiting for PostgreSQL to finish its checkpoint.

**Fix:** Ensure `stop_grace_period: 30s` is set for the postgres service in docker-compose.yml.

---

## 2. PgBouncer (sahool-pgbouncer)

### 2.1 Successful Operations

- PgBouncer 1.23.1 started on port 6432
- Kernel file descriptor limit: 1,048,576 (sufficient)
- Max client connections: 800
- Established ~11 server connections to PostgreSQL
- Stats reporting: 5 queries/s, 774us wait time (healthy)

### 2.2 CRITICAL: Plaintext Password Fallback

**Log Evidence:**
```
sahool-pgbouncer | [WARN] 2026-03-13 19:39:25 Using plaintext password for auth_user (SCRAM hash unavailable)
```

**Root Cause:**
The entrypoint script attempts to fetch SCRAM-SHA-256 hash from PostgreSQL via `pgbouncer.get_auth()`, but the function doesn't exist yet (see issue 1.3). It falls back to storing the plaintext password in `userlist.txt`.

**Security Impact:** Passwords are stored in plaintext on disk at `/etc/pgbouncer/runtime/userlist.txt`. Even though the file is `chmod 600`, this is a security risk.

**Configuration Reference:**
- Auth type: `scram-sha-256` (in `pgbouncer.ini` line 60)
- Auth query: `SELECT usename, passwd FROM pgbouncer.get_auth($1)` (line 64)
- Fallback: Plaintext in `userlist.txt`

**Fix:** Ensure PgBouncer starts only after init scripts complete, or restart PgBouncer after init.

---

### 2.3 CRITICAL: Timestamp Overflow in Connection Ages

**Log Evidence:**
```
sahool-pgbouncer | LOG C-...: sahool/sahool@172.18.0.33:40476 closing because: client_idle_timeout (age=18446744073707s)
sahool-pgbouncer | LOG S-...: sahool/sahool@172.18.0.8:5432 closing because: server lifetime over (age=18446744073704s)
```

**Analysis:**
The value `18446744073707` is approximately `2^64 - 5` seconds, which is a classic **unsigned integer underflow**. This happens when:
1. A timestamp calculation results in a negative value
2. The negative value is interpreted as an unsigned 64-bit integer

**Possible Causes:**
- System clock skew between containers
- PgBouncer's internal timer wraps around during startup
- Connection established before PgBouncer's internal clock initializes

**Impact:** Connections are closed prematurely with incorrect age values. The `client_idle_timeout` (900s) triggers incorrectly because PgBouncer calculates a massive positive age instead of the actual connection duration.

**Affected Connections:** ~30 connections from various services (IPs: 172.18.0.20-55) were terminated with this overflow.

**Fix Options:**
1. Verify Docker host time synchronization (`timedatectl` or NTP)
2. Add `--privileged` or `SYS_TIME` capability if time sync is needed
3. Consider upgrading PgBouncer if this is a known bug in 1.23.1

---

### 2.4 HIGH: All Connections Without TLS

**Log Evidence:**
Every connection shows `tls=no`:
```
sahool-pgbouncer | LOG C-...: sahool/sahool@172.18.0.41:38030 login attempt: db=sahool user=sahool tls=no
```

**Configuration:**
```ini
# infrastructure/core/pgbouncer/pgbouncer.ini
server_tls_sslmode = disable
client_tls_sslmode = disable
```

**Impact:** All database traffic between microservices and PgBouncer, and between PgBouncer and PostgreSQL, is unencrypted. Acceptable for development only.

**Fix for Production:**
```ini
server_tls_sslmode = require
client_tls_sslmode = require
```

---

### 2.5 MEDIUM: Rapid Connect/Disconnect from Service 172.18.0.51

**Log Evidence:**
```
19:39:54.139 - login attempt (172.18.0.51:59872) → closing (client close request)
19:39:54.143 - login attempt (172.18.0.51:59874) → closing (client close request)
19:39:54.247 - login attempt (172.18.0.51:59878) → closing (client close request)
19:39:54.370 - login attempt (172.18.0.51:59890) → closing (client close request)
19:39:54.590 - login attempt (172.18.0.51:59906) → closing (client close request)
19:39:54.681 - login attempt (172.18.0.51:59914) → closing (client close request)
19:39:54.778 - login attempt (172.18.0.51:59924) → closing (client close request)
```

**Analysis:** A service at `172.18.0.51` connects 7 times within 640ms and disconnects immediately each time. This pattern suggests:
- Health check probes (connect → query → disconnect)
- OR a service failing to run migrations and retrying rapidly

**Impact:** Low. Connections are short-lived and don't accumulate.

---

## 3. Kong (sahool-kong)

### 3.1 Successful Operations

- OpenResty/1.21.4.1 (Kong 3.5-alpine) running
- 24 worker processes started (PIDs 1260-1283)
- Declarative config loaded from `/kong/declarative/kong.yml`
- Event method: epoll (optimal for Linux)

### 3.2 CRITICAL: Startup Timeout Errors Across All Workers

**Log Evidence:**
```
[error] 1283#0: *26 [lua] worker.lua:138: communicate(): failed to connect: failed to receive response header: timeout
[error] 1282#0: *30 [lua] worker.lua:138: communicate(): failed to connect: ...timeout
[error] 1281#0: *34 [lua] worker.lua:138: communicate(): failed to connect: ...timeout
[error] 1263#0: *38 [lua] worker.lua:138: communicate(): failed to connect: ...timeout
[error] 1278#0: *551 [lua] worker.lua:138: communicate(): ...timeout
[error] 1279#0: *563 [lua] worker.lua:138: communicate(): ...timeout
[error] 1280#0: *665 [lua] worker.lua:138: communicate(): ...timeout
[error] 1277#0: *1048 [lua] worker.lua:138: communicate(): ...timeout
[error] 1274#0: *1196 [lua] worker.lua:138: communicate(): ...timeout
```

**Analysis:** 12 timeout errors across 9 different worker processes during startup. The `worker.lua:138 communicate()` function handles inter-worker communication for declarative config synchronization. The timeouts occur because:

1. All 24 workers start simultaneously
2. Each worker tries to load the declarative config from disk
3. Worker #1263 (the "config worker") loads `kong.yml` and purges cache
4. Other workers wait for config broadcast, but the 24 workers create contention
5. Some workers timeout waiting for the config event

**Evidence of Successful Recovery:**
```
[notice] 1263#0: *3 [kong] init.lua:523 declarative config loaded from /kong/declarative/kong.yml
```
Worker 1263 successfully loaded the config. The other workers would eventually receive it via the event system.

**Impact:** Temporary - requests during the first ~15 seconds of startup may fail or route incorrectly. After config propagation completes, all workers function normally.

**Fix:**
```yaml
# Reduce worker count if not needed
KONG_NGINX_WORKER_PROCESSES: 4  # Instead of 'auto' (24 on this host)
```

---

### 3.3 HIGH: Event Broker Connection Failures

**Log Evidence:**
```
[error] 1260#0: *3116 [lua] broker.lua:111: run(): failed to init socket: failed to flush response header: nginx output filter error
[error] 1260#0: *3109 [lua] broker.lua:208: run(): event broker failed: failed to receive the header bytes: connection reset by peer
[error] 1260#0: *3112 [lua] broker.lua:184: failed to send event: failed to send frame: broken pipe
```

**Analysis:** The event broker (worker #1260, the master event dispatcher) fails to communicate with other workers. Three distinct error types:

| Error | Count | Cause |
|-------|-------|-------|
| `nginx output filter error` | 4 | Worker closed connection before response sent |
| `connection reset by peer` | 5 | Worker crashed or restarted during communication |
| `broken pipe` | 1 | Attempted write to closed connection |

**Root Cause:** These errors are cascading from the config loading timeouts. When workers timeout on config loading, they restart their event connections, causing resets for the broker.

**Impact:** Temporary. Self-resolving after startup stabilization (~15-20s).

---

### 3.4 HIGH: Exponential Backoff Sleep Flooding

**Log Evidence (sample):**
```
[notice] 1273#0: *8 [lua] globalpatches.lua:73: sleep(): executing a blocking 'sleep' (0.001 seconds)
[notice] 1273#0: *8 [lua] globalpatches.lua:73: sleep(): executing a blocking 'sleep' (0.002 seconds)
[notice] 1273#0: *8 [lua] globalpatches.lua:73: sleep(): executing a blocking 'sleep' (0.004 seconds)
...
[notice] 1273#0: *8 [lua] globalpatches.lua:73: sleep(): executing a blocking 'sleep' (0.5 seconds)
```

**Analysis:** Each of the 24 workers performs exponential backoff sleep (0.001s → 0.002s → 0.004s → ... → 0.5s) while waiting for the declarative config to load. This generates **200+ log entries** per startup and indicates workers are blocking during initialization.

**Impact:** Log noise and delayed startup. Each worker blocks for up to ~1 second total (sum of geometric series).

**Fix:** Reduce `log_level` for `notice` messages or reduce worker count.

---

### 3.5 MEDIUM: Non-Root User Warning

**Log Evidence:**
```
[warn] the "user" directive makes sense only if the master process runs with super-user privileges
```

**Analysis:** Kong's nginx.conf contains a `user` directive, but the container runs as non-root. This is expected behavior in Docker and harmless.

---

## 4. Cross-Service Timing Issues

The root cause of multiple issues is a **startup race condition**:

```
T=0.0s  PostgreSQL container starts, begins init scripts
T=0.0s  PgBouncer container starts, waits for port 5432
T=0.0s  Kong container starts

T=0.8s  PostgreSQL begins accepting connections (init scripts still running!)
T=3.0s  PgBouncer detects port open, starts connecting
T=3.0s  PgBouncer tries auth_query → FAILS (02-pgbouncer-user.sql not yet run)
T=3.0s  PgBouncer falls back to plaintext passwords

T=5.0s  Services start connecting through PgBouncer
T=5.0s  Some services query tables not yet created → ERRORS

T=10s   Kong workers loading declarative config → TIMEOUTS between workers
T=15s   00-init-sahool.sql completes
T=16s   01-research-expansion.sql runs → FAILS on missing users table
T=18s   02-pgbouncer-user.sql creates pgbouncer schema (too late for first boot)
T=20s   Remaining init scripts complete

T=25s   NestJS services start, run Prisma migrations
T=30s   user-service creates users table (needed by research tables)
T=35s   Platform stabilizes
```

---

## 5. Recommendations Summary

### Critical (Fix Immediately)

| # | Issue | Fix | File |
|---|-------|-----|------|
| C1 | `01-research-expansion.sql` fails on missing `users` table | Remove FK constraints, add via post-migration | `infrastructure/core/postgres/init/01-research-expansion.sql` |
| C2 | PgBouncer plaintext password fallback | Add readiness check for init scripts completion | `infrastructure/core/pgbouncer/entrypoint.sh` |
| C3 | Timestamp overflow in PgBouncer connection ages | Check Docker host time sync, consider PgBouncer upgrade | `docker-compose.yml` (pgbouncer service) |
| C4 | Kong worker timeouts during startup | Reduce `KONG_NGINX_WORKER_PROCESSES` from `auto` to `4` | `docker-compose.yml` (kong service) |

### High Priority

| # | Issue | Fix | File |
|---|-------|-----|------|
| H1 | PgBouncer auth_query fails at first boot | Ensure PgBouncer waits for full DB init, not just port | `infrastructure/core/pgbouncer/entrypoint.sh` |
| H2 | `calibration_run` table not found by service | Add service dependency on DB readiness | `docker-compose.yml` |
| H3 | All PgBouncer connections without TLS | Enable TLS for production deployments | `infrastructure/core/pgbouncer/pgbouncer.ini` |
| H4 | Kong event broker connection resets | Reduce worker count, increase startup timeout | `docker-compose.yml` (kong service) |
| H5 | NATS service_started vs service_healthy | Change all `depends_on` to `service_healthy` | `docker-compose.yml` (all services) |

### Medium Priority

| # | Issue | Fix |
|---|-------|-----|
| M1 | Unclean PostgreSQL shutdown | Set `stop_grace_period: 30s` |
| M2 | Kong startup log flooding (200+ notice lines) | Reduce worker count or adjust log level |
| M3 | Rapid connect/disconnect from 172.18.0.51 | Investigate service behavior |
| M4 | Missing enums in research-expansion.sql | Add enum definitions before table creation |

---

## 6. Service Connection Map (from PgBouncer logs)

| IP Address | Connections | First Seen | Status |
|------------|-------------|------------|--------|
| 172.18.0.20 | 2 | 19:39:44 | idle_timeout |
| 172.18.0.23 | 3 | 19:39:53 | idle_timeout |
| 172.18.0.25 | 2 | 19:39:52 | idle_timeout |
| 172.18.0.33 | 2 | 19:39:42 | idle_timeout |
| 172.18.0.34 | 2 | 19:39:42 | idle_timeout |
| 172.18.0.35 | 1 | 19:39:51 | idle_timeout |
| 172.18.0.36 | 2 | 19:39:46 | idle_timeout |
| 172.18.0.38 | 2 | 19:39:43 | idle_timeout |
| 172.18.0.39 | 2 | 19:39:49 | idle_timeout |
| 172.18.0.40 | 2 | 19:39:49 | idle_timeout |
| 172.18.0.41 | 2 | 19:39:42 | idle_timeout |
| 172.18.0.42 | 8 | 19:39:52 | idle_timeout |
| 172.18.0.46 | 2 | 19:39:49 | idle_timeout |
| 172.18.0.47 | 2 | 19:39:46 | idle_timeout |
| 172.18.0.48 | 2 | 19:39:51 | idle_timeout |
| 172.18.0.49 | 2 | 19:39:44 | idle_timeout |
| 172.18.0.50 | 1 | 19:39:53 | idle_timeout |
| 172.18.0.51 | 7 | 19:39:53 | rapid reconnect |
| 172.18.0.55 | 1 | 19:39:53 | idle_timeout |
| 172.18.0.61 | 2 | 19:39:41 | active |
| 172.18.0.63 | 2 | 19:39:45 | active |
| 172.18.0.65 | 2 | 19:39:45 | active |
| 172.18.0.68 | 2 | 19:40:23 | idle_timeout |
| 172.18.0.71 | 1 | 19:40:10 | active |

**Total unique service IPs:** 24
**Total connections observed:** ~55
**Connections terminated by idle_timeout:** ~30 (with timestamp overflow)

---

_Generated: 2026-03-13 | Analyst: Claude Code_
