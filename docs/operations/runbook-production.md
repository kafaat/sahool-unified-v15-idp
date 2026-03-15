# SAHOOL Operational Runbook (Production)

> **Version**: 1.0.0
> **Platform**: SAHOOL v16.0.0
> **Last Updated**: 2026-02-23
> **Owner**: KAFAAT — Platform Engineering
> **Scope**: Event-Driven Architecture (NATS JetStream + Outbox + PostgreSQL + K8s)

---

## 0. Purpose

This runbook defines:

- How to **detect** incidents (alerts, dashboards, symptoms)
- How to **diagnose** rapidly (commands, queries, log patterns)
- How to **remediate** (step-by-step procedures)
- When to **escalate** (severity matrix, response windows)
- How to **verify recovery** (exit criteria, post-incident checks)

### Applicable Services

| Layer | Services |
|-------|----------|
| **Acquisition** | `weather-service`, `iot-service`, `iot-gateway`, `virtual-sensors`, `edge-orchestrator-service` |
| **Intelligence** | `crop-intelligence-service`, `vegetation-analysis-service`, `indicators-service`, `yolo26-vision-service`, `terrain-core-service` |
| **Decision** | `advisory-service`, `irrigation-smart`, `crop-growth-model`, `yield-prediction-service`, `hydrology-service`, `leveling-optimizer-service` |
| **Business** | `notification-service`, `marketplace-service`, `billing-core`, `chat-service`, `task-service`, `equipment-service`, `ws-gateway` |

### JetStream Streams (12 Pre-Defined)

| Stream | Subjects | Retention |
|--------|----------|-----------|
| `SAHOOL_FIELD` | `sahool.field.>`, `sahool.satellite.>` | 30 days |
| `SAHOOL_WEATHER` | `sahool.weather.>` | 7 days |
| `SAHOOL_INTELLIGENCE` | `sahool.calibration.>`, `sahool.irrigation.>`, `sahool.health.>`, `sahool.recommendation.>` | 30 days |
| `SAHOOL_VISION` | `sahool.vision.>` | 14 days |
| `SAHOOL_TERRAIN` | `sahool.terrain.>` | 30 days |
| `SAHOOL_EDGE` | `sahool.edge.>` | 14 days |
| `SAHOOL_BUSINESS` | `sahool.billing.>`, `sahool.notification.>`, `sahool.task.>`, etc. | 90 days |
| `SAHOOL_AGENT` | `sahool.agent.>` | 14 days |
| `SAHOOL_IOT` | `sahool.iot.>` | 14 days |
| `SAHOOL_SYSTEM` | `sahool.system.>`, `sahool.user.>` | 30 days |
| `SAHOOL_TENANT` | `sahool.tenant.>` | 30 days |
| `SAHOOL_DLQ` | `sahool.dlq.>` | 30 days |

> Streams defined in `shared/events/streams.py`. Each stream: `max_messages=1,000,000`, `max_bytes=5GB`, `storage=file`, `dedup_window=120s`.

---

## 1. Severity Levels

| Level | Definition | Response Window | Action |
|-------|-----------|-----------------|--------|
| **P0** | Total system outage or data loss | Immediate | Rollback + incident bridge |
| **P1** | Recommendations, calibration, or billing impacted | 15 minutes | Investigate and remediate |
| **P2** | Latency degradation or non-critical feature failure | Same day | Fix within working hours |
| **P3** | Non-impacting error or cosmetic issue | Scheduled | Fix in next sprint |

---

## 2. Incident: DLQ Growth

### Symptoms

- Alert: `DLQMessageCountHigh` (threshold: 100 messages — `shared/events/dlq_config.py`)
- Increasing messages in `SAHOOL_DLQ` stream
- Repeated subject pattern in DLQ (e.g., `sahool.dlq.calibration.run.failed.v1`)
- Dashboard: DLQ message count graph trending upward

### Diagnosis

**Step 1** — Inspect DLQ stream info:

```bash
nats stream info SAHOOL_DLQ
```

**Step 2** — Read sample message from DLQ:

```bash
nats consumer next SAHOOL_DLQ <consumer-name>
```

**Step 3** — Use the DLQ management API:

```bash
# Get DLQ statistics (messages by subject, error type, service)
curl http://localhost:8150/dlq/stats

# List DLQ messages with pagination
curl "http://localhost:8150/dlq/messages?limit=10&offset=0"

# Get specific message details
curl http://localhost:8150/dlq/messages/<msg_id>
```

**Step 4** — Examine message metadata fields:

| Field | What to Check |
|-------|---------------|
| `original_subject` | Which event failed? |
| `correlation_id` | Trace the full request chain |
| `retry_count` | Should be 3 (max retries from `DLQ_MAX_RETRIES`) |
| `failure_reason` | Root cause string |
| `error_type` | `ValidationError` = non-retriable, `TimeoutError` = retriable |
| `consumer_service` | Which service failed to process? |
| `retry_timestamps` | Backoff pattern: 1s → 2s → 4s |
| `retry_errors` | Error history per attempt |

### Remediation

| Root Cause | Action |
|------------|--------|
| `ValidationError` / `ValueError` / `KeyError` / `TypeError` | Fix source data or publisher schema. These are **non-retriable** — they went directly to DLQ. |
| `TimeoutError` / `ConnectionError` | Check downstream DB or service health. These retried 3 times with exponential backoff before DLQ. |
| Schema mismatch (`X-Schema-Version` header) | Check for version drift between publisher and consumer. Verify `BaseEvent.version` field. |
| DB lock / high CPU | See [Incident: DB High CPU](#6-incident-db-high-cpu--lock-contention) |

### Do NOT

- Do NOT replay all DLQ messages at once — this can cause event storms
- Do NOT delete DLQ messages without analysis
- Do NOT disable DLQ (`DLQ_ENABLED=false`) as a workaround

### After Fix

```bash
# Replay specific messages only (by sequence number)
curl -X POST http://localhost:8150/dlq/replay/<sequence_number>

# Or bulk replay (with caution, specific sequences only)
curl -X POST http://localhost:8150/dlq/replay/bulk \
  -H "Content-Type: application/json" \
  -d '{"sequences": [1, 2, 3]}'

# Archive old DLQ messages
curl -X POST http://localhost:8150/dlq/archive
```

- Monitor consumer lag for 10 minutes after replay
- Verify no new DLQ entries for the same subject

---

## 3. Incident: Consumer Lag

### Symptoms

- JetStream consumer lag is high (increasing `num_ack_pending`)
- Dashboard not updating with fresh data
- Recommendations are delayed
- Alert: `JetStreamLag` (from `infrastructure/monitoring/prometheus/rules/nats-alerts.yml`)

### Diagnosis

```bash
# Check specific consumer info
nats consumer info SAHOOL_INTELLIGENCE decision-consumer

# Check all consumers for a stream
nats consumer ls SAHOOL_INTELLIGENCE
```

**Key metrics to inspect**:

| Metric | Healthy | Concerning |
|--------|---------|------------|
| `num_ack_pending` | < 100 | > 1,000 |
| `num_redelivered` | 0 | Increasing |
| `num_waiting` | > 0 | 0 (no workers pulling) |

### Remediation

1. **Check consumer pod resource usage**:

   ```bash
   kubectl top pods -l app=crop-intelligence-service
   ```

2. **Check DB latency** (slow queries block event processing):

   ```bash
   kubectl exec -it postgres-0 -- psql -U sahool -c \
     "SELECT pid, now() - query_start AS duration, query FROM pg_stat_activity WHERE state = 'active' ORDER BY duration DESC LIMIT 5;"
   ```

3. **Restart stuck consumer** (if `num_waiting=0` and pod is running):

   ```bash
   kubectl delete pod <consumer-pod-name>
   ```

4. **Scale horizontally** (manual HPA override):

   ```bash
   kubectl scale deployment crop-intelligence-service --replicas=4
   ```

   > HPA is configured for 14 services with scale-up: 100% per 15s or +2 pods per 60s, scale-down: -10% per 60s with 5-min stabilization. See `helm/charts/*/templates/hpa.yaml`.

5. **Check `max_concurrent_messages`** setting (default: 10 in `SubscriberConfig`):

   If processing is CPU-bound, reduce concurrency to prevent overload.

---

## 4. Incident: Duplicate Recommendation Suspected

### Symptoms

- Farmer receives the same irrigation or fertilizer recommendation twice
- Duplicate entries in database recommendation tables
- Duplicate notification delivery

### Diagnosis

**Step 1** — Check `processed_events` table:

```sql
-- PK is (tenant_id, event_id) — dedup guard
SELECT * FROM processed_events
WHERE correlation_id = '<correlation_id>';

-- Check for multiple entries with same correlation
SELECT tenant_id, event_id, subject, service, status, processed_at
FROM processed_events
WHERE correlation_id = '<correlation_id>'
ORDER BY processed_at;
```

**Step 2** — Check in-memory dedup (LRU cache, 50K entries in `EventSubscriber`):

```bash
# Check subscriber dedup stats in service logs
kubectl logs <pod> | grep "Duplicate event_id skipped"
# Or check dedup hit count
kubectl logs <pod> | grep "dedup_hit_count"
```

**Step 3** — Check outbox replay:

```sql
-- Check if outbox event was published more than once
SELECT id, subject, status, retry_count, created_at, sent_at
FROM outbox_events
WHERE correlation_id = '<correlation_id>';
```

**Step 4** — Check NATS dedup window:

> Streams have `dedup_window=120s`. If the same `event_id` is published within 120s, NATS deduplicates it. Beyond 120s, the consumer-side `processed_events` table is the guard.

### Remediation

| Root Cause | Action |
|------------|--------|
| `processed_events` PK not enforced | Verify `PRIMARY KEY (tenant_id, event_id)` exists |
| In-memory LRU evicted (cache full) | Check `_dedup_max_size=50000` — increase if needed |
| ACK sent before DB commit | **Critical bug** — ACK must happen AFTER successful DB write. Check `auto_ack` setting in `Subscription`. |
| Outbox relay published twice | Check `_SQL_MARK_SENT` is atomic — verify `sent_at IS NULL` guard |
| NATS dedup window expired | Events published >120s apart with same ID. Increase `dedup_window` or rely on `processed_events`. |

---

## 5. Incident: Outbox Backlog

### Symptoms

- `outbox_events` table growing rapidly (status=`pending`)
- Downstream services not receiving events
- Stale data in dashboards

### Diagnosis

```sql
-- Count pending outbox events
SELECT COUNT(*) FROM outbox_events WHERE status = 'pending';

-- Check oldest pending event
SELECT id, subject, created_at, retry_count, last_error
FROM outbox_events
WHERE status = 'pending'
ORDER BY created_at ASC
LIMIT 10;

-- Check failed outbox events
SELECT subject, COUNT(*), MAX(retry_count), MAX(last_error)
FROM outbox_events
WHERE status = 'failed'
GROUP BY subject;
```

### Remediation

1. **Check NATS availability**:

   ```bash
   nats server ping
   nats server info
   ```

2. **Check OutboxRelay status** in service logs:

   ```bash
   kubectl logs <pod> | grep "outbox_relay"
   # Look for: outbox_relay_started, outbox_relay_batch, outbox_relay_error
   ```

3. **Verify OutboxRelay is running** (background task in service lifespan):

   > OutboxRelay: `poll_interval=1.0s`, `batch_size=50`. Defined in `shared/events/outbox.py`.

4. **Scale outbox relay** if NATS is healthy but backlog persists:

   ```bash
   kubectl scale deployment <service-with-outbox> --replicas=3
   ```

5. **Run cleanup** for old sent events (24h TTL):

   ```sql
   -- Check sent events that should be cleaned
   SELECT COUNT(*) FROM outbox_events
   WHERE status = 'sent' AND sent_at < NOW() - INTERVAL '24 hours';
   ```

### Escalation

- **P1** if `pending` backlog > 50,000
- **P0** if NATS is completely unreachable

---

## 6. Incident: DB High CPU / Lock Contention

### Symptoms

- PostgreSQL CPU > 80%
- Slow queries across services
- Connection timeouts (PgBouncer: max 250 connections, transaction mode)
- Alert: `PostgresCPUHigh`

### Diagnosis

```sql
-- Active queries and their duration
SELECT pid, now() - query_start AS duration, state, query
FROM pg_stat_activity
WHERE state != 'idle'
ORDER BY duration DESC
LIMIT 20;

-- Lock waits
SELECT blocked.pid AS blocked_pid,
       blocked.query AS blocked_query,
       blocking.pid AS blocking_pid,
       blocking.query AS blocking_query
FROM pg_stat_activity blocked
JOIN pg_locks bl ON bl.pid = blocked.pid
JOIN pg_locks bk ON bk.locktype = bl.locktype
  AND bk.relation = bl.relation
  AND bk.pid != bl.pid
JOIN pg_stat_activity blocking ON blocking.pid = bk.pid
WHERE NOT bl.granted;

-- Table bloat / missing indexes
SELECT schemaname, tablename, n_tup_ins, n_tup_upd, n_tup_del,
       n_live_tup, n_dead_tup, last_vacuum, last_autovacuum
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC
LIMIT 10;
```

### Remediation

| Root Cause | Action |
|------------|--------|
| Long-running query | `SELECT pg_cancel_backend(<pid>);` (safe) or `pg_terminate_backend(<pid>)` (force) |
| Missing index | Add index — check `processed_events`, `outbox_events` indexes exist |
| `processed_events` table bloat | Run `VACUUM ANALYZE processed_events;` — TTL cleanup should run every 7 days |
| `outbox_events` table bloat | Run `VACUUM ANALYZE outbox_events;` — sent events should be cleaned after 24h |
| High connection count | Check PgBouncer stats: `SHOW POOLS;` and `SHOW CLIENTS;` |
| Batch size too large | Reduce `batch_size` in OutboxRelay (default: 50) or consumer processing |

### Vertical Scaling (Emergency)

```bash
# Increase DB resources
kubectl edit statefulset postgres
# Adjust resources.limits.cpu and resources.limits.memory
```

---

## 7. Incident: Event Storm

### Symptoms

- Sudden spike in publish rate on specific subjects
- Outbox backlog growing
- Consumer lag increasing across streams
- NATS: high message rate in `nats server info`

### Diagnosis

```bash
# Check NATS server stats
nats server info

# Check stream message rates
nats stream info SAHOOL_INTELLIGENCE
nats stream info SAHOOL_FIELD

# Identify high-volume subjects
nats stream subjects SAHOOL_INTELLIGENCE
```

- Check producer service logs for correlation_id patterns (is one request generating many events?)
- Check if a batch operation or bulk import is running

### Remediation

1. **Apply rate limiting** at API gateway (Kong):

   > Rate limit tiers defined in `shared/middleware/rate_limit.py`:
   > - Starter: 30 req/min, 500/hour
   > - Professional: 60 req/min, 2000/hour
   > - Enterprise: 120 req/min, 5000/hour
   > - Internal: 1000 req/min, 50000/hour

2. **Throttle specific subject** at publisher level:

   Temporarily reduce batch sizes or add delays in the producing service.

3. **Scale consumers horizontally**:

   ```bash
   kubectl scale deployment advisory-service --replicas=6
   kubectl scale deployment crop-intelligence-service --replicas=4
   ```

4. **Check circuit breakers**:

   > Pre-configured breakers in `shared/ai/circuit_breaker.py`:
   > - `ollama`: 3 failures, 30s timeout
   > - `anthropic`: 5 failures, 60s timeout
   > - `openai`: 5 failures, 60s timeout

---

## 8. Correlation Debugging Procedure

### Objective

Trace the full journey of an irrigation recommendation from HTTP request through event chain to notification delivery.

### Steps

**Step 1** — Get `correlation_id` from the initial HTTP request log:

```bash
# Search service logs for the correlation ID
kubectl logs -l app=advisory-service | grep "correlation_id=<XYZ>"
```

> Correlation ID is generated by `shared/middleware/request_logging.py` from `X-Correlation-ID` or `X-Request-ID` header, or auto-generated as UUID.

**Step 2** — Search across all services in the chain:

```bash
# Search each service in the event chain
for svc in advisory-service irrigation-smart crop-intelligence-service notification-service; do
  echo "=== $svc ==="
  kubectl logs -l app=$svc | grep "<correlation_id>"
done
```

**Step 3** — Verify the event chain:

| Header | Purpose |
|--------|---------|
| `X-Correlation-ID` | Same across entire request chain |
| `X-Causation-ID` | Points to the upstream `event_id` that caused this event |
| `X-Event-ID` | Unique ID of this specific event |
| `X-Tenant-ID` | Tenant scope (from JWT `tid` claim) |
| `X-Schema-Version` | Event schema version for compatibility |
| `traceparent` | W3C OpenTelemetry trace format: `00-{trace_id}-{span_id}-01` |

**BaseEvent fields** (from `shared/events/contracts.py`):

> Every event carries: `event_id`, `correlation_id`, `causation_id`, `trace_id`, `span_id`, `version`, `source_service`, `tenant_id_header`.

**Step 4** — Verify:

- No missing hop in the causation chain (`causation_id` must point to parent `event_id`)
- No broken `traceparent` (OpenTelemetry)
- `processed_events` table has entries for each service in the chain
- No DLQ entries for this correlation_id

```sql
SELECT * FROM processed_events
WHERE correlation_id = '<XYZ>'
ORDER BY processed_at;
```

---

## 9. Pod Crash During Processing

### Symptoms

- Pod restart count increasing (`kubectl get pods` → RESTARTS column)
- NATS `num_redelivered` count increasing
- Possible duplicate processing

### Diagnosis

```bash
# Check pod restart reason
kubectl describe pod <pod-name> | grep -A 5 "Last State"

# Check if OOMKilled
kubectl get pod <pod-name> -o jsonpath='{.status.containerStatuses[0].lastState.terminated.reason}'
```

**Key questions**:

1. Did ACK happen before crash? → If yes, message is lost (violates at-least-once)
2. Did `processed_events` record the event? → If yes, replay is safe (dedup will skip)
3. Is the event in DLQ? → If yes, retry logic detected the failure

### Remediation

**Usually no intervention needed.** The system recovers automatically:

1. NATS redelivers the message (since ACK was not sent)
2. Consumer processes the message again
3. `processed_events` table prevents duplicate side effects (PK: `tenant_id, event_id`)
4. In-memory LRU dedup (50K cache) provides fast-path dedup

**If duplication occurred** (ACK before commit — a bug):

- Review `auto_ack` setting in the `Subscription` config
- Ensure ACK happens AFTER successful DB commit
- Check idempotency layer in `shared/events/subscriber.py`

---

## 10. Emergency Rollback Procedure

### Trigger

A new deployment caused failures (errors, DLQ growth, wrong recommendations).

### Steps

**Step 1** — Rollback the deployment:

```bash
kubectl rollout undo deployment/<service-name>
```

**Step 2** — Verify consumers reconnected:

```bash
nats consumer info <stream> <consumer-name>
# Check: num_waiting > 0 (workers are pulling)
```

**Step 3** — Check consumer lag:

```bash
nats consumer info <stream> <consumer-name>
# Check: num_ack_pending is decreasing
```

**Step 4** — Monitor DLQ for 15 minutes:

```bash
watch -n 10 'nats stream info SAHOOL_DLQ'
```

**Step 5** — Verify no new failures:

```bash
# Check error rate in Prometheus
# Alert: error rate < 1% for 15 minutes
kubectl logs -l app=<service-name> --tail=100 | grep -i error
```

---

## 11. Health Check Routine (Daily)

Run this checklist daily (or automate with `make health`):

| Check | Target | Command |
|-------|--------|---------|
| DLQ count | = 0 (or near zero) | `nats stream info SAHOOL_DLQ` |
| Outbox pending | < 100 | `SELECT COUNT(*) FROM outbox_events WHERE status='pending';` |
| No redeliver spike | `num_redelivered` stable | `nats consumer info <stream> <consumer>` |
| DB CPU | < 70% | Grafana: Infrastructure Overview dashboard |
| HPA stable | No flapping | `kubectl get hpa` |
| Error rate | < 1% per service | Grafana: Service Overview dashboard |
| All health endpoints | 200 OK | `make health` or `for port in 8090 8091 8092 8093 8094 8095; do curl -sf http://localhost:$port/healthz; done` |

### Automated Health Endpoints

All services expose (per `shared/monitoring/health_enhanced.py`):

| Endpoint | Purpose | K8s Probe |
|----------|---------|-----------|
| `GET /healthz` | Liveness (is the process alive?) | `livenessProbe` |
| `GET /readyz` | Readiness (can it handle traffic?) | `readinessProbe` |
| `GET /health` | Comprehensive status (dependencies, metrics) | Manual check |
| `GET /metrics` | Prometheus metrics | Prometheus scrape |

---

## 12. Weekly Review

| Task | Purpose |
|------|---------|
| Check stream retention | Ensure no streams approaching `max_messages` (1M) or `max_bytes` (5GB) |
| Check `processed_events` growth | Run TTL cleanup if table > 1M rows (7-day retention) |
| Archive old correlation logs | Reduce log storage costs |
| Review slow queries | `pg_stat_statements` — optimize top 5 slow queries |
| Review retry patterns | Check `retry_count` distribution in `outbox_events` and DLQ |
| Check circuit breaker states | Ensure no breakers are stuck in OPEN state |
| Verify backup health | WAL archiving, PITR readiness (see `docs/disaster-recovery/`) |

---

## 13. Escalation Matrix

| Severity | Response | Who | Channel |
|----------|----------|-----|---------|
| **P0** | Immediate rollback + incident bridge | On-call engineer + Team Lead | War room / incident channel |
| **P1** | Investigate within 15 min | On-call engineer | Alert channel |
| **P2** | Fix within same business day | Assigned engineer | Team channel |
| **P3** | Schedule in next sprint | Product team | Backlog |

### Escalation Triggers

| Condition | Severity |
|-----------|----------|
| All pods down for a service | P0 |
| Data loss confirmed | P0 |
| DLQ > 1000 messages in 1 hour | P1 |
| Outbox backlog > 50,000 | P1 |
| Consumer lag > 10,000 and growing | P1 |
| DB CPU > 90% for 10 minutes | P1 |
| NATS connection lost | P1 |
| Single service error rate > 5% | P2 |
| Latency p99 > 5s | P2 |

---

## 14. Golden Rules

> These rules are absolute. Violating them can cause data loss, duplicate side effects, or cascading failures.

| # | Rule | Reason |
|---|------|--------|
| 1 | **Never replay all DLQ messages at once** | Causes event storms; replay selectively after root cause fix |
| 2 | **Never delete `processed_events` data** | Removes idempotency guard; duplicates will occur on replay |
| 3 | **Never disable idempotency temporarily** | Even "just for testing" can cause production duplicates |
| 4 | **Never ACK before DB commit** | Message is lost if pod crashes between ACK and commit |
| 5 | **Never publish events outside outbox transaction** | Breaks exactly-once guarantee; event may publish without business write |
| 6 | **Never force-delete NATS streams** | Use retention policies; force-delete loses unprocessed messages |
| 7 | **Never bypass rate limiting for debugging** | Use internal tier (1000 req/min) instead of disabling |

---

## 15. Exit Criteria (Incident Resolved)

An incident is considered **resolved** when ALL of the following hold for **30 minutes**:

- [ ] DLQ message count is stable (no new messages)
- [ ] No new error logs for the affected service
- [ ] Consumer lag is at normal levels (`num_ack_pending` < 100)
- [ ] DB CPU is stable (< 70%)
- [ ] No duplicate side effects detected
- [ ] Outbox `pending` count < 100
- [ ] Health endpoints return 200 for all affected services
- [ ] HPA is not flapping (replicas stable)

---

## 16. Platform Maturity Assessment

If the patterns described in this runbook are fully implemented and operational:

- **Outbox pattern** ensures exactly-once event delivery (no lost events)
- **DLQ with retry** handles transient failures automatically (3 retries, exponential backoff)
- **Processed events table** prevents duplicate processing on replay
- **In-memory LRU dedup** (50K cache) provides fast-path deduplication
- **W3C correlation tracing** enables full request chain debugging
- **Circuit breakers** prevent cascading failures to external services
- **HPA** scales services automatically under load

The platform is at a **Production-Mature** level, resilient against:

- Pod restarts and crashes
- Transient network failures and retries
- Message duplication and replay
- Partial failures across the event chain
- External service outages (circuit breaker protection)

---

## Appendix A: Key File References

| Component | File Path |
|-----------|-----------|
| DLQ Configuration | `shared/events/dlq_config.py` |
| DLQ Service API | `shared/events/dlq_service.py` |
| DLQ Handler (retry + move) | `shared/events/subscriber_dlq.py` |
| DLQ Monitoring | `shared/events/dlq_monitoring.py` |
| Outbox Pattern | `shared/events/outbox.py` |
| Outbox Models (SQLAlchemy) | `shared/libs/outbox/models.py` |
| Event Publisher (trace headers) | `shared/events/publisher.py` |
| Event Subscriber (dedup) | `shared/events/subscriber.py` |
| Event Contracts (BaseEvent) | `shared/events/contracts.py` |
| Subject Constants | `shared/events/subjects.py` |
| Stream Definitions | `shared/events/streams.py` |
| Correlation ID Middleware | `shared/middleware/request_logging.py` |
| Circuit Breaker | `shared/ai/circuit_breaker.py` |
| Rate Limiting | `shared/middleware/rate_limit.py` |
| Health Check (Enhanced) | `shared/monitoring/health_enhanced.py` |
| Prometheus Metrics | `shared/monitoring/metrics.py` |
| NATS Server Config | `config/nats/nats.conf` |
| Prometheus Alert Rules | `infrastructure/monitoring/prometheus/rules/` |
| Grafana Dashboards | `infrastructure/grafana/dashboards/` |
| DLQ Docker Compose | `docker/docker-compose.dlq.yml` |

## Appendix B: Environment Variables (Event Infrastructure)

```bash
# NATS
NATS_URL=nats://nats:4222
JETSTREAM_DOMAIN=sahool
SERVICE_NAME=<service-name>

# DLQ
DLQ_ENABLED=true
DLQ_MAX_RETRIES=3
DLQ_INITIAL_DELAY=1.0
DLQ_MAX_DELAY=60.0
DLQ_BACKOFF_MULTIPLIER=2.0
DLQ_STREAM_NAME=SAHOOL_DLQ
DLQ_MAX_AGE_DAYS=30
DLQ_MAX_MESSAGES=100000
DLQ_ALERT_ENABLED=true
DLQ_ALERT_THRESHOLD=100
DLQ_ALERT_CHECK_INTERVAL=300

# Database (outbox + processed_events)
DATABASE_URL=postgresql://user:pass@pgbouncer:6432/sahool?sslmode=require

# Monitoring
ENVIRONMENT=production
LOG_LEVEL=INFO
```

## Appendix C: Quick Command Reference

```bash
# === NATS ===
nats stream ls                                  # List all streams
nats stream info SAHOOL_DLQ                     # DLQ stream status
nats stream info SAHOOL_INTELLIGENCE            # Intelligence stream status
nats consumer ls SAHOOL_INTELLIGENCE            # List consumers
nats consumer info SAHOOL_INTELLIGENCE <name>   # Consumer lag details
nats server info                                # NATS server health

# === Database ===
SELECT COUNT(*) FROM outbox_events WHERE status='pending';    # Outbox backlog
SELECT COUNT(*) FROM processed_events;                        # Dedup table size
SELECT * FROM pg_stat_activity WHERE state='active';          # Active queries
VACUUM ANALYZE outbox_events;                                 # Cleanup bloat
VACUUM ANALYZE processed_events;                              # Cleanup bloat

# === Kubernetes ===
kubectl get pods -l app=<service>               # Pod status
kubectl top pods -l app=<service>               # Resource usage
kubectl logs -l app=<service> --tail=100        # Recent logs
kubectl rollout undo deployment/<service>       # Emergency rollback
kubectl scale deployment/<service> --replicas=N # Manual scale
kubectl get hpa                                 # Autoscaler status

# === DLQ Management API ===
curl http://localhost:8150/dlq/stats            # DLQ statistics
curl http://localhost:8150/dlq/messages         # List DLQ messages
curl -X POST http://localhost:8150/dlq/replay/<seq>  # Replay one message

# === Health ===
make health                                     # Check all services
make status                                     # Service status & URLs
```
