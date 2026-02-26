# Audit Service | خدمة التدقيق والمراجعة

Centralized audit logging service for security compliance and operational traceability across all SAHOOL platform services.

**Port:** 8114 | **Type:** Python / FastAPI | **Version:** 16.0.0

---

## Overview

The Audit Service provides a tamper-evident, hash-chained audit trail for all security-critical and operationally significant events on the platform. It supports multi-framework compliance reporting (GDPR, SOC2, ISO27001), real-time security alerting, and structured export for external SIEM tools.

Key capabilities:
- Hash chain integrity validation for tamper detection
- Field-level change tracking (old/new value diff storage)
- Compliance report generation per regulatory framework
- Real-time security event stream (failed logins, privilege escalations)
- Bilingual audit entries (Arabic / English)

---

## Architecture

```
Audit Service (8114)
├── In-Memory Storage (CI/test mode)
├── Shared Audit Module (production)  ← shared/audit_trail/
│   └── PostgreSQL (primary persistence)
├── NATS (event subscriptions)
│   └── Subscribes to: UserAuthenticated, FieldCreated/Updated/Deleted, AlertTriggered, etc.
└── Redis (optional: rate limiting cache)
```

On startup the service attempts a PostgreSQL connection via the shared audit module. If `ENVIRONMENT=test` or `ci`, it falls back to in-memory storage so the service can run in CI without external dependencies.

---

## API Endpoints

### Health

| Method | Path | Description |
|--------|------|-------------|
| GET | `/healthz` | Kubernetes liveness probe |
| GET | `/readyz` | Kubernetes readiness probe (checks DB + NATS) |
| GET | `/health` | Combined health check with dependency status |

### Audit Logs

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/audit/logs` | Query logs with filters (user, action, category, resource, date range) |
| GET | `/api/v1/audit/logs/{log_id}` | Get a specific audit log entry |
| GET | `/api/v1/audit/users/{user_id}/trail` | Full audit trail for a user |
| GET | `/api/v1/audit/resources/{type}/{id}/trail` | Audit trail for a specific resource |

Query parameters for `/api/v1/audit/logs`: `user_id`, `action`, `category`, `resource_type`, `resource_id`, `success`, `start_date`, `end_date`, `skip`, `limit` (max 500).

### Hash Chain Integrity

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/audit/chain/validate` | Validate hash chain integrity for a date range |
| GET | `/api/v1/audit/chain/summary` | Chain coverage statistics for tenant |

### Compliance

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/audit/compliance/report` | Generate compliance report (GDPR, SOC2, ISO27001, general) |

### Statistics & Security

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/audit/stats` | Audit statistics by period (7d, 30d, 90d) |
| GET | `/api/v1/audit/security-events` | Recent security category events |
| GET | `/api/v1/audit/failed-logins` | Failed login attempts within N hours |

### Export

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/audit/export` | Export logs as JSON or CSV for a date range |

---

## NATS Events

### Publishes

| Subject | Trigger |
|---------|---------|
| `AuditLogged.v1` | New audit log entry created |
| `AuditAlertTriggered.v1` | Security alert condition met |
| `ComplianceReportGenerated.v1` | Compliance report generated |

### Subscribes

| Subject | Purpose |
|---------|---------|
| `UserAuthenticated.v1` | Log authentication events |
| `UserRegistered.v1` | Log user creation |
| `FieldCreated.v1`, `FieldUpdated.v1`, `FieldDeleted.v1` | Track field-level changes |
| `AlertTriggered.v1` | Log alert events |
| `TaskCreated.v1`, `TaskCompleted.v1` | Log task lifecycle |

---

## Authentication

All endpoints require the `X-Tenant-Id` header. Returns HTTP 400 if missing. JWT-based auth is applied by Kong at the gateway level before reaching this service.

---

## Audit Log Entry Schema

```json
{
  "id": "uuid",
  "tenant_id": "uuid",
  "user_id": "uuid",
  "action": "auth.login.success",
  "category": "security | data | system | compliance",
  "severity": "info | warning | error | critical",
  "resource_type": "field | user | task",
  "resource_id": "uuid",
  "correlation_id": "uuid",
  "ip_address": "string",
  "success": true,
  "old_value": {},
  "new_value": {},
  "entry_hash": "sha256-hex",
  "created_at": "ISO8601"
}
```

---

## Environment Variables

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `PORT` | `8114` | No | Service port |
| `HOST` | `0.0.0.0` | No | Bind address |
| `ENVIRONMENT` | `development` | No | `test`/`ci` enables in-memory fallback |
| `DATABASE_URL` | - | Yes (prod) | PostgreSQL connection string |
| `NATS_URL` | - | No | NATS server URL |
| `REDIS_URL` | - | No | Redis for caching |
| `LOG_LEVEL` | `INFO` | No | Logging verbosity |

---

## Dependencies

- **FastAPI** 0.128.5 — HTTP framework
- **asyncpg** — PostgreSQL async driver
- **nats-py** — NATS event subscription
- `shared.audit_trail` — Shared audit utilities
- `shared.errors_py` — Unified error handling and request ID middleware

---

## Related Services

- **user-service** (3025) — Produces authentication events consumed here
- **field-management-service** (3000) — Produces field lifecycle events
- **alert-service** (8113) — Alert events are logged here
- **billing-core** (8089) — Financial operations audited here
