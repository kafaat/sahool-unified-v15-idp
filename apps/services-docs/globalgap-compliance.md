# GlobalGAP Compliance Service

**Port**: 8128 | **Type**: Python (FastAPI) | **Version**: 16.0.0

GlobalGAP IFA v6 compliance management service. Tracks farm compliance status, manages IFA v6 checklists, prepares audit reports, records non-conformities, and manages GGN certificates for certified farms.

---

## Overview

`globalgap-compliance` implements the GlobalGAP Integrated Farm Assurance (IFA) version 6 standard for the SAHOOL platform. It provides a full compliance lifecycle: initial assessment using IFA v6 control points, non-conformity tracking with corrective actions, audit report generation, and GGN certificate issuance and renewal. The service publishes compliance state-change events to NATS for downstream notification and reporting. Storage is in-memory for development; production deployments should connect to PostgreSQL.

---

## Architecture

```
FastAPI Application
    ├── ComplianceService  (record management, trend analysis)
    ├── AuditService       (report preparation and storage)
    ├── NatsPublisher      (event publishing)
    └── Middleware
        ├── CORS
        ├── X-Tenant-Id header validation
        └── Unified exception handling
```

Authentication is via `X-Tenant-Id` header (required on all endpoints). The service uses in-memory dictionaries for storage in the current implementation; database persistence via asyncpg is planned for production.

---

## API Endpoints

### Health

| Method | Path | Description |
|--------|------|-------------|
| GET | `/healthz` | Liveness probe |
| GET | `/health/live` | Kubernetes liveness alias |
| GET | `/readyz` | Readiness probe (NATS connectivity) |
| GET | `/health/ready` | Kubernetes readiness alias |
| GET | `/health` | Full dependency status (storage, NATS, record counts) |

### Compliance Records

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/farms/{farm_id}/compliance` | Tenant | Current compliance status |
| POST | `/farms/{farm_id}/compliance` | Tenant | Create or update compliance record |
| GET | `/farms/{farm_id}/compliance/trends` | Tenant | Compliance trends (1–24 months) |

### Checklists (IFA v6 Control Points)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/checklists` | Tenant | Available checklists (filter: `ifa_version`, `checklist_type`) |
| GET | `/checklists/{id}/items` | Tenant | Control points (filter: `category`, `compliance_level`) |
| POST | `/farms/{farm_id}/assessments` | Tenant | Record a control point assessment |
| GET | `/farms/{farm_id}/assessments` | Tenant | All assessments for a farm |

### Audits

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/audits` | Tenant | Create an audit report |
| GET | `/audits/{audit_id}` | Tenant | Get audit report by ID |
| GET | `/farms/{farm_id}/audits` | Tenant | Audit history for a farm |

### Non-Conformities

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/farms/{farm_id}/non-conformities` | Tenant | List non-conformities (filter: `severity`, `resolved`) |
| POST | `/non-conformities` | Tenant | Record a new non-conformity |

### GGN Certificates

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/farms/{farm_id}/certificates` | Tenant | List GGN certificates |
| POST | `/certificates` | Tenant | Issue a new GGN certificate |
| GET | `/certificates/{certificate_id}` | Tenant | Get certificate by ID |

---

## NATS Events Published

| Subject | Trigger |
|---------|---------|
| `sahool.globalgap.compliance_updated` | Compliance record created or updated |
| `sahool.globalgap.audit_completed` | Audit report finalized |
| `sahool.globalgap.non_conformity_created` | New non-conformity recorded |
| `sahool.globalgap.certificate_created` | GGN certificate issued |

---

## IFA v6 Compliance Levels

| Level | Code | Description |
|-------|------|-------------|
| Major Must | `MM` | Mandatory; zero tolerance - non-compliance = suspension |
| Minor Must | `Mm` | Required; < 5% non-compliance allowed |
| Recommended | `Rec` | Best practice; no minimum compliance threshold |

---

## Compliance Status Values

| Status | Description |
|--------|-------------|
| `not_assessed` | No assessment performed |
| `compliant` | All control points meet requirements |
| `minor_non_compliant` | Minor non-conformities present |
| `major_non_compliant` | Major non-conformities require immediate action |
| `suspended` | Certification suspended |

---

## Severity Levels

| Severity | Response Time |
|----------|--------------|
| `critical` | Immediate action required |
| `major` | Corrective action within 28 days |
| `minor` | Corrective action at next audit |

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8128` | HTTP listen port |
| `ENVIRONMENT` | `development` | Deployment environment |
| `NATS_URL` | `nats://localhost:4222` | NATS server URL |
| `DATABASE_URL` | - | PostgreSQL (future production use) |
| `CORS_ORIGINS` | `http://localhost:3000,...` | Allowed CORS origins |
| `LOG_LEVEL` | `INFO` | Logging verbosity |

---

## Dependencies

- `fastapi` + `pydantic` v2 for API and validation
- `structlog` for structured JSON logging
- `nats-py` for NATS event publishing
- `shared.errors_py` for request-ID middleware and exception handling
- Local `services/compliance_service.py`, `services/audit_service.py`
- Local `models/certificate.py`, `models/checklist.py`, `models/compliance.py`

---

## Health Endpoints

```
GET /healthz      → {"status": "alive", "service": "globalgap-compliance-service"}
GET /readyz       → {"status": "ready", "database": false, "nats": true|false}
GET /health       → {"status": "healthy", "dependencies": {"storage": "in_memory", "nats": "connected|disconnected"}}
```

---

## Related Services

- **farm-documents** (`shared/farm_documents/`) - document compliance records
- **audit-service** (8114) - platform-wide audit log
- **advisory-service** (8093) - PHI and pesticide compliance advisory
