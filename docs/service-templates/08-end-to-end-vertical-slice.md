# 08 · End-to-End Vertical-Slice Review

**Applies to:** any user-facing feature / endpoint.
**Companion to:** patterns 01–07 (which review services in isolation).
**Goal:** trace a single request from the user's device to the
database and back, catching drift at every hop.

> قالب المراجعة الرأسية الشاملة: تتبّع الطلب من واجهة المستخدم عبر
> البوابة والوسيط حتى الخدمة الخلفية وقاعدة البيانات.

Use this template **after** the per-pattern review — Pattern 01 tells
you whether `field-management-service` is healthy in isolation; this
template tells you whether the **Fields page** actually works end to
end.

---

## The SAHOOL request stack (reference)

```
┌─────────────────────────────────────────────────────────────────┐
│ 1 · CLIENT                                                      │
│     Web (Next.js 15)  ·  Admin (Next.js)  ·  Mobile (Flutter)   │
│       │                                                          │
│       │  HTTPS (TLS 1.3)                                         │
│       ▼                                                          │
│ 2 · EDGE / CDN                                                  │
│     Cloudflare or AWS CloudFront · WAF · DDoS                   │
│       │                                                          │
│       ▼                                                          │
│ 3 · WEB FRONTEND (Next.js on standalone)                        │
│     a. Middleware  — middleware.ts                              │
│        · i18n detection                                          │
│        · CSRF double-submit                                      │
│        · Auth gate (reads httpOnly access_token cookie)          │
│        · Security headers (CSP / HSTS / Referrer-Policy)         │
│     b. Next.js rewrite  — next.config.js                         │
│        · /api/v1/*  →  $API_GATEWAY_URL (Kong) /api/v1/*         │
│     c. Internal proxy route  — apps/web/src/app/api/<name>/     │
│        · Extracts tenant_id from JWT                             │
│        · Rate-limit (Redis)                                      │
│        · Allow-lists query params (SSRF guard)                   │
│        · Forwards with `Authorization: Bearer <access_token>`    │
│       │                                                          │
│       ▼                                                          │
│ 4 · API GATEWAY (Kong 3.x)                                      │
│     · JWT verification plugin                                    │
│     · Rate-limit per tier (starter / pro / enterprise / …)       │
│     · CORS                                                       │
│     · Request-id propagation (`X-Request-Id`)                    │
│     · Routes `/api/v1/<domain>/*`  →  service upstream           │
│       │                                                          │
│       ▼                                                          │
│ 5 · BACKEND SERVICE (NestJS or FastAPI, patterns 01–07)         │
│     · Guards / dependencies                                      │
│       - JwtAuthGuard (redundant w/ Kong but defence-in-depth)    │
│       - TenantGuard (stamps `tenantId` onto request)             │
│       - RolesGuard (RBAC)                                        │
│       - ThrottlerGuard / slowapi (burst protection)              │
│     · Validation pipe (class-validator / Pydantic)               │
│     · Controller / route handler                                 │
│     · Service / domain logic                                     │
│       │                                                          │
│       ├─ Reads/Writes Postgres via Prisma / asyncpg              │
│       ├─ Emits events to NATS (`sahool.<domain>.<action>`)       │
│       ├─ Publishes metrics to Prometheus                         │
│       └─ Emits OTel spans to Jaeger                              │
│       │                                                          │
│       ▼                                                          │
│ 6 · DATA LAYER                                                  │
│     · PgBouncer (transaction-mode pool)                          │
│         - `DATABASE_URL` (pooled)                                │
│         - `DATABASE_URL_DIRECT` (for migrations)                 │
│     · PostgreSQL 16 + PostGIS 3.4                                │
│     · Redis (cache / rate-limit / sessions)                      │
│     · MinIO (S3-compatible) for large objects                    │
│     · Vector DB (Qdrant) for AI services                         │
│                                                                  │
│ CROSS-CUTTING (spans every layer)                               │
│   - Logs: structlog / pino → Loki                                │
│   - Traces: OpenTelemetry → Jaeger                               │
│   - Metrics: Prometheus → Grafana                                │
│   - Errors: Sentry                                               │
│   - Feature flags: GrowthBook                                    │
│   - Secrets: HashiCorp Vault                                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## Review steps — do them in order

Pick one representative feature (e.g. **"create a field"**, **"get
weather forecast"**, **"send chat message"**) and follow the request
through each layer below. Mark every row ✅ / ⚠️ / ❌ / 🚫 exactly like
the universal checklist.

### 1 · Client (Web / Admin / Mobile)

| # | Check | How to verify |
|---|---|---|
| 1.1 | Page uses a feature hook (React Query / Riverpod) — not raw fetch | inspect `apps/web/src/features/<domain>/hooks/*` |
| 1.2 | Hook calls `createApiClient()` / unified-client — not hard-coded fetch | `grep createApiClient` |
| 1.3 | Endpoint comes from `@sahool/shared-types/contracts` constants — not string literal | `grep <DOMAIN>_ENDPOINTS` |
| 1.4 | Loading + error states rendered (no blank screens on slow networks) | visual inspection |
| 1.5 | Bilingual text (EN/AR) for every label, error, toast | `grep 'ar:' features/<domain>/api.ts` |
| 1.6 | No PII in URL query params | inspect request in DevTools |
| 1.7 | Errors surface to Sentry via the shim | `grep sentryShim` |

### 2 · Edge / CDN

| # | Check | How to verify |
|---|---|---|
| 2.1 | HTTPS only — HSTS preloaded for main hostnames | `curl -I https://<host>` |
| 2.2 | Static assets have far-future `Cache-Control` with content hashing | `curl -I /_next/static/...` |
| 2.3 | HTML responses have `Cache-Control: no-store` (prevents stale-SW bug, see §SW audit) | `curl -I /dashboard` |
| 2.4 | WAF rules blocking common payloads (SQLi, path traversal) | WAF dashboard |
| 2.5 | DDoS protection engaged in production | cloud console |

### 3 · Web Frontend — middleware + proxy routes

| # | Check | How to verify |
|---|---|---|
| 3.1 | `middleware.ts` runs on every request: i18n, CSRF, security headers | `apps/web/src/middleware.ts` |
| 3.2 | Protected routes redirect to `/login` when cookie missing | clear cookies, visit `/dashboard` |
| 3.3 | `next.config.js` rewrite targets `$API_GATEWAY_URL` (Kong) — not a direct service URL | `apps/web/next.config.js` |
| 3.4 | Any `/api/<name>/route.ts` proxy extracts `tenant_id` from JWT — never trusts the body | pick 3 routes and inspect |
| 3.5 | Proxy routes rate-limited per IP + per tenant | `grep isRateLimited` |
| 3.6 | Proxy routes allow-list query params (SSRF defence) | `grep allowedParams` |
| 3.7 | Service Worker (`public/sw.js`) does not pre-cache HTML (see §SW audit) | inspect `STATIC_ASSETS` array |
| 3.8 | `/sw-kill.html` present as recovery escape | `ls apps/web/public/sw-kill*` |

### 4 · API Gateway (Kong)

| # | Check | How to verify |
|---|---|---|
| 4.1 | Service is declared in `infrastructure/gateway/kong/kong.yml` | `grep <service>` |
| 4.2 | JWT plugin enabled (verifies signature + expiration) | plugin listed per route |
| 4.3 | Rate-limit plugin maps to the correct tier | plugin config |
| 4.4 | CORS plugin allow-lists expected origins only | plugin config |
| 4.5 | Upstream health-check points at `/healthz` | upstream block |
| 4.6 | `X-Request-Id` header propagated to upstreams | inspect `headers_to_propagate` |

### 5 · Backend service — controller + service

| # | Check | How to verify |
|---|---|---|
| 5.1 | Route registered at the same path as `<DOMAIN>_ENDPOINTS.<X>` | diff contracts vs router |
| 5.2 | Controller delegates to a service method — no DB calls in controllers | inspect |
| 5.3 | Service method receives `tenantId` as a typed parameter — never reads it from body | inspect signature |
| 5.4 | DTO validated (class-validator / Pydantic) — reject unknown fields | grep `whitelist: true` / `extra="forbid"` |
| 5.5 | Mutations wrapped in a single transaction (DB writes + outbox insert) | grep `$transaction` / `async with conn.transaction()` |
| 5.6 | Domain event emitted after commit with `sahool.*` subject | see NATS audit |
| 5.7 | Errors mapped to the unified envelope `{ success, error, error_ar, code, requestId }` | inspect exception filter |
| 5.8 | Audit log written for mutating actions (see `audit-service`) | grep `auditLog` |

### 6 · Data layer

| # | Check | How to verify |
|---|---|---|
| 6.1 | Connection goes through PgBouncer (`DATABASE_URL` includes `:6432`) | `echo $DATABASE_URL` |
| 6.2 | Migrations use `DATABASE_URL_DIRECT` (:5432, bypasses pooler) | inspect CI step |
| 6.3 | Query uses parameterized SQL — NEVER string concat | grep `f"` near `execute(` |
| 6.4 | Every `SELECT` scopes by `tenantId` | review |
| 6.5 | Geometry columns have GIST indexes | `\d+ <table>` |
| 6.6 | Cache-aside / read-through Redis wrapper on hot reads | grep `@Cache` / `cache.get` |
| 6.7 | Large binaries go to MinIO — not bytea columns | |

### 7 · Cross-cutting (same for every layer)

| # | Check | How to verify |
|---|---|---|
| 7.1 | `x-request-id` set at the CDN/edge and propagated all the way to Postgres `application_name` | follow the header through logs |
| 7.2 | OTel span covers the request from client to DB query | Jaeger trace view |
| 7.3 | Error logged to Sentry with breadcrumbs — no silent `.catch(() => {})` | grep swallowed catches |
| 7.4 | Request + response visible in Prometheus histograms (`http_request_duration_seconds`) | `curl /metrics` |
| 7.5 | Feature flag gate at the controller for WIP endpoints | grep `growthbook` |
| 7.6 | No PII in logs at any layer | grep for the mask list |

---

## Per-pattern E2E trace examples

### A. Fields page (Pattern 01 · NestJS)

```
Web   GET /fields                                   apps/web/src/app/(dashboard)/fields/page.tsx
  → useFields()                                     apps/web/src/features/fields/hooks/useFields.ts
  → createApiClient().get(FIELD_ENDPOINTS.LIST)     apps/web/src/features/fields/api.ts
  → fetch /api/v1/fields                            (browser, same-origin)
  → Next.js rewrite → $API_GATEWAY_URL/api/v1/fields
Kong  JWT verify + rate-limit + /healthz upstream check
  → http://field-management-service:3000/api/v1/fields
Service JwtAuthGuard → TenantGuard → FieldsController.list()
  → FieldsService.findAll(tenantId, paginationParams)
  → Prisma: SELECT from fields WHERE tenantId = $1 ...
DB    PgBouncer → PostgreSQL (reads via `idx_fields_tenant_*`)
Reply unified `{success, data, meta}` envelope back through the same path
```

### B. Send chat message (Pattern 01 · NestJS + Pattern 06 bridge)

```
Web   Socket.IO 'send_message' event                apps/web/src/features/chat/…
Kong  (for HTTP-initiated auth handshake only; WS lives on ws-gateway after upgrade)
Service ChatGateway.handleSendMessage
  → ChatService.sendMessage(dto, tenantId)
  → Prisma $transaction {
      create Message + updateMany Conversation + updateMany Participant
    }
  → ChatEventsService.publishMessageSent(…)
      emits sahool.chat.message.sent
DB    Postgres commit inside transaction
NATS  Subscribers: notification-service (push), audit-service (log)
Web   Socket.IO broadcast back to conversation room
```

### C. Weather forecast (Pattern 02 · FastAPI)

```
Web   GET /weather                                  apps/web/src/app/(dashboard)/weather/page.tsx
  → useWeatherForecast(locationId)
  → createApiClient().get(WEATHER_ENDPOINTS.FORECAST_BY_LOCATION)
Kong  /api/v1/weather/forecast/{id} → weather-service:8092
Service FastAPI router → Pydantic validation → WeatherService.forecast()
  → Redis cache GET (6 h TTL) → HIT, return
  → (on MISS) Fetch Open-Meteo/OpenWeather with circuit breaker
  → Write Redis cache → publish sahool.weather.forecast.issued
DB    n/a (stateless for this endpoint; forecasts persisted only when pushed)
```

### D. Vision inference (Pattern 04 · GPU)

```
Mobile  POST /api/v1/vision/detect/pest [image/*]
Kong    JWT + rate-limit (Enterprise tier: 120 req/min)
Service yolo26-vision-service:8150
  → guard: content-type + size ≤ MAX_UPLOAD_SIZE_MB
  → ModelManager.get('pest', variant='m') (LRU cache)
  → inference (FP16, <500 ms P95 on RTX 3090)
  → post-process → NMS → severity + recommendations (bilingual)
  → if critical: publish sahool.vision.critical.alert
Reply `{detections: [...], model: 'm', inference_ms: 42}`
```

---

## Red flags — stop the review and escalate

Any ONE of the following should block the release:

- ❌ Tenant ID read from request body anywhere in the trace
- ❌ SQL built by string concatenation
- ❌ `process.env.NEXT_PUBLIC_*` carrying a secret
- ❌ A proxy route that forwards `Authorization` without re-validating JWT
  (Kong should do this too, but defence-in-depth is required)
- ❌ Event subject missing the `sahool.` prefix (caught by
  `scripts/check-event-subject-prefix.sh`)
- ❌ Long-lived admin bearer token in a mobile build
- ❌ `Cache-Control: public` on a tenant-scoped response
- ❌ `catch (e) {}` that swallows a domain-level error without logging
  + Sentry capture + metric increment

---

## Deliverable — the audit report

For each feature you review, attach a table like:

| Layer | Check | Result | Notes |
|---|---|---|---|
| Client | 1.3 endpoint via contracts | ✅ | uses `FIELD_ENDPOINTS.LIST` |
| Edge | 2.3 no-store on HTML | ⚠️ | missing on `/dashboard` |
| Middleware | 3.7 SW not pre-caching HTML | ✅ | fixed 2026-04-13 (commit 1fcb0e75) |
| Kong | 4.5 health-check upstream | ✅ | |
| Service | 5.5 transactional | ✅ | `$transaction` in `ChatService.sendMessage` |
| Service | 5.6 event emitted | ✅ | `sahool.chat.message.sent` |
| DB | 6.4 tenant-scoped | ✅ | `WHERE tenantId = $1` in every query |
| Cross-cutting | 7.1 request-id propagated | ⚠️ | missing in Kong `headers_to_propagate` |

File it in the feature's PR or a dated report in `docs/audits/`.
