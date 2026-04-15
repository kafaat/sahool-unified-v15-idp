# 00 · Universal Service Review Checklist

**Applies to:** every SAHOOL microservice, Node.js or Python, any pattern.
**Revision:** 1.0.0 (2026-04-13)
**Time to run:** ~15 min for a well-kept service, ~60 min for an unknown one.

This is the **mandatory baseline**. Pattern-specific templates (`01`–`07`)
add depth on top of it but never remove a row. If a row doesn't apply to a
given service, write `N/A — <one-sentence rationale>` instead of leaving
it blank.

> قائمة المراجعة الأساسية الإلزامية لأي خدمة. القوالب النوعية تضيف
> تفاصيل إضافية لكن لا تستبدل أياً من هذه البنود.

---

## How to fill the matrix

Copy the table below into an audit report or a PR description. Mark each
row with one of:

| Symbol | Meaning |
|---|---|
| ✅ | Compliant — verified by reading the code or running the command in “how to verify”. |
| ⚠️ | Partially compliant — lists what's missing in the notes column. |
| ❌ | Non-compliant — must be fixed before merge / release. |
| 🚫 | Not applicable — justify in the notes column. |

---

## Capability groups

### 1 · Bilingual identity

| # | Check | How to verify | Result | Notes |
|---|---|---|---|---|
| 1.1 | Service has an entry in `governance/services.yaml` | `grep -A5 '^  <service>:' governance/services.yaml` | | |
| 1.2 | README present with EN + AR sections: Purpose, Architecture, API, Events, Ops | `head -20 apps/services/<svc>/README.md` | | |
| 1.3 | Service linked to its pattern template in README (see `docs/service-templates/`) | `grep service-templates apps/services/<svc>/README.md` | | |
| 1.4 | Port matches `packages/shared-types/src/contracts/service-ports.ts` | compare Dockerfile EXPOSE to SERVICE_PORTS | | |

### 2 · Health & lifecycle

| # | Check | How to verify | Result | Notes |
|---|---|---|---|---|
| 2.1 | `/healthz` (liveness) returns 200 without DB | `curl /healthz` | | |
| 2.2 | `/readyz` (readiness) returns 200 only when all deps (DB, NATS, Redis) are up | inspect handler returns composite status | | |
| 2.3 | `/metrics` exposes Prometheus format when applicable | `curl /metrics \| head` | | |
| 2.4 | Graceful shutdown on `SIGTERM`: drain DB pool, drain NATS, stop accepting new requests | grep `gracefulShutdown\|lifespan\|onModuleDestroy` | | |
| 2.5 | No `process.exit()` / `os._exit()` in normal flow — only in shutdown or fatal startup | grep `process.exit\|os\._exit\|sys.exit` | | |

### 3 · Configuration & secrets

| # | Check | How to verify | Result | Notes |
|---|---|---|---|---|
| 3.1 | All config read via env vars at startup, not sprinkled per-request | grep `process.env\|os.getenv` coverage | | |
| 3.2 | No secrets committed — `.env` in `.gitignore`, `.env.example` present | `git log -p .env 2>/dev/null \| head` (should be empty) | | |
| 3.3 | Sensitive env vars documented in README with placeholder values | inspect README Ops section | | |
| 3.4 | `DATABASE_URL` and `DATABASE_URL_DIRECT` both declared (PgBouncer transaction-mode) | grep both in code + compose | | |
| 3.5 | `JWT_SECRET_KEY` validated at startup (≥32 chars, not `changeme`) | startup validator present | | |

### 4 · Database

| # | Check | How to verify | Result | Notes |
|---|---|---|---|---|
| 4.1 | Connection pool sized for the workload (min/max explicit) | inspect pool config | | |
| 4.2 | Every tenant table has `tenantId String @map("tenant_id")` + an index containing it | `./scripts/prisma-check.sh` + grep | | |
| 4.3 | All tenant queries scope by `tenantId` — no cross-tenant leaks | spot-check 3 random queries | | |
| 4.4 | Transactions used for multi-table writes | grep `$transaction\|asyncpg transaction` | | |
| 4.5 | Migrations present (`prisma migrate diff --from-empty` works) for Prisma services | `ls prisma/migrations/` | | |
| 4.6 | N+1 queries avoided (relations loaded with `include` / eager fetch) | spot-check list endpoints | | |

### 5 · NATS / event bus

| # | Check | How to verify | Result | Notes |
|---|---|---|---|---|
| 5.1 | If the service publishes events: every subject is `sahool.<domain>.<entity>.<action>` | `./scripts/check-event-subject-prefix.sh` | | |
| 5.2 | Subjects come from constants (`EventSubjects` or `shared.events.subjects`) — no raw strings in business code | grep for raw strings in events dir | | |
| 5.3 | NATS lifecycle: connect on startup, drain on shutdown | grep `initializeNatsClient\|nats.connect\|nats.drain` | | |
| 5.4 | Published events include `tenantId` + `eventId` (UUID) + `timestamp` + `version` | inspect an outgoing envelope | | |
| 5.5 | Critical writes go through the Outbox pattern (`OutboxEvent` table) | grep `OutboxEvent\|outbox_event` | | |
| 5.6 | Subscribers handle duplicates (idempotency key) and failures (DLQ) | grep `IdempotencyKey\|DLQ\|dead_letter` | | |

### 6 · Security

| # | Check | How to verify | Result | Notes |
|---|---|---|---|---|
| 6.1 | Authenticated routes require a valid JWT (shared guard / dependency) | grep `JwtAuthGuard\|get_current_user` on router files | | |
| 6.2 | Role / scope checks on mutations (RBAC) | grep `@Roles\|require_role` | | |
| 6.3 | Input validation via Zod / class-validator / Pydantic — no raw `any` on boundaries | inspect one controller file | | |
| 6.4 | Rate limiting applied globally or per-route | grep `ThrottlerGuard\|slowapi\|rate_limit` | | |
| 6.5 | SSRF guard on proxy-style endpoints (allow-listed hosts/params) | inspect fetch / httpx usage | | |
| 6.6 | Output escaping for bilingual strings — no raw HTML rendering on the backend | grep `dangerouslySetInnerHTML` (web) / direct HTML responses | | |
| 6.7 | CORS allow-list is explicit (no `*` in production) | inspect CORS config | | |
| 6.8 | Security headers present (CSP, HSTS, X-Content-Type-Options, Referrer-Policy) | `curl -I` on a GET endpoint | | |

### 7 · Observability

| # | Check | How to verify | Result | Notes |
|---|---|---|---|---|
| 7.1 | Structured JSON logs (`structlog` / `nestjs-pino`) — never `print` / `console.log` | grep `print(\|console\\.log(` | | |
| 7.2 | Correlation ID (`x-request-id`) propagated through logs + outgoing events | inspect middleware | | |
| 7.3 | OpenTelemetry traces emitted (spans cover the request lifecycle) | grep `opentelemetry\|trace.get_tracer` | | |
| 7.4 | Prometheus metrics for request rate, latency histogram, error counter | inspect `/metrics` | | |
| 7.5 | Sentry (or equivalent) captures unhandled exceptions | grep `Sentry\|captureException` | | |
| 7.6 | No PII in logs — sensitive fields (password, phone, email) redacted | grep for the mask list | | |

### 8 · Testing

| # | Check | How to verify | Result | Notes |
|---|---|---|---|---|
| 8.1 | Unit tests (`*.spec.ts` / `tests/unit/*.py`) cover happy-path + error-path of each handler | count + sample | | |
| 8.2 | Integration tests hit real DB + NATS via testcontainers or docker-compose | `ls tests/integration/` | | |
| 8.3 | Smoke test importable without env (CI fast path) | | | |
| 8.4 | Golden dataset / snapshot tests for AI services | | | |
| 8.5 | Coverage ≥ 60 % lines — trending up, not down | coverage report | | |

### 9 · Deployment & ops

| # | Check | How to verify | Result | Notes |
|---|---|---|---|---|
| 9.1 | Multi-stage Dockerfile: `base` → `builder` → `production` | `grep -c '^FROM' Dockerfile` ≥ 2 | | |
| 9.2 | Runs as non-root user (UID ≥ 1000) | `grep 'USER' Dockerfile` | | |
| 9.3 | `HEALTHCHECK` directive present | `grep HEALTHCHECK Dockerfile` | | |
| 9.4 | `.dockerignore` excludes `node_modules`, `.git`, `__pycache__`, `tests/` from build context | inspect | | |
| 9.5 | Pip / npm mirror fallback chain for offline/restricted networks | 3-tier fallback present | | |
| 9.6 | Kong route in `infrastructure/gateway/kong/kong.yml` | `grep <service> infrastructure/gateway/kong/kong.yml` | | |
| 9.7 | Kubernetes Helm chart in `helm/<service>/` with resource requests + limits | `ls helm/` | | |
| 9.8 | ArgoCD Application in `gitops/` | `grep <service> gitops/*.yaml` | | |
| 9.9 | Grafana dashboard JSON checked-in (or at least a `# TODO` pointing to the shared one) | `ls infrastructure/monitoring/grafana/dashboards/` | | |
| 9.10 | Alert rules in `infrastructure/monitoring/prometheus/rules/` | `ls` | | |

---

## Single-command audit shortcut

```bash
SERVICE=<service-name>
SVC_DIR=apps/services/$SERVICE

echo "=== $SERVICE ==="
test -f "$SVC_DIR/README.md"                        && echo "✅ README"        || echo "❌ README"
grep -q "service-templates" "$SVC_DIR/README.md"    && echo "✅ template link" || echo "❌ template link"
grep -c "^FROM" "$SVC_DIR/Dockerfile"               | awk '$1>=2 {print "✅ multi-stage Dockerfile"}'
grep -q "USER sahool\|USER 1000" "$SVC_DIR/Dockerfile" && echo "✅ non-root"    || echo "⚠️ runs as root?"
grep -q "HEALTHCHECK" "$SVC_DIR/Dockerfile"         && echo "✅ HEALTHCHECK"   || echo "❌ HEALTHCHECK"
grep -rq "/healthz\|/readyz" "$SVC_DIR"             && echo "✅ probes"        || echo "❌ probes"
grep -rq "SIGTERM\|gracefulShutdown\|lifespan"      "$SVC_DIR" && echo "✅ graceful shutdown" || echo "⚠️ graceful shutdown"

./scripts/check-event-subject-prefix.sh             && echo "✅ event subjects"
./scripts/prisma-check.sh                            && echo "✅ Prisma clean"
```

A deeper automated check is provided by `scripts/service-review.sh`
(generated from this checklist) — one-shot TODO for anyone willing to
wrap the commands above.
