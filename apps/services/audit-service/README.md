# SAHOOL Audit Service

خدمة التدقيق والمراجعة المركزية

Centralized audit logging service for security compliance and operational traceability.

## Features

- **Hash Chain Integrity** - سلسلة التجزئة للتحقق من السلامة
- **Field-Level Tracking** - تتبع التغييرات على مستوى الحقل
- **Compliance Reporting** - تقارير الامتثال (GDPR, SOC2, ISO27001)
- **Real-time Security Alerts** - تنبيهات الأمان في الوقت الفعلي
- **Fallback Logging** - التسجيل الاحتياطي للأعطال

## API Endpoints

### Health
- `GET /health` - Health check with dependencies
- `GET /healthz` - Kubernetes liveness probe
- `GET /readyz` - Kubernetes readiness probe

### Audit Logs
- `GET /api/v1/audit/logs` - Query audit logs with filters
- `GET /api/v1/audit/logs/{log_id}` - Get specific audit log
- `GET /api/v1/audit/users/{user_id}/trail` - User audit trail
- `GET /api/v1/audit/resources/{type}/{id}/trail` - Resource audit trail

### Hash Chain
- `GET /api/v1/audit/chain/validate` - Validate hash chain integrity
- `GET /api/v1/audit/chain/summary` - Chain summary for tenant

### Compliance
- `GET /api/v1/audit/compliance/report` - Generate compliance report

### Statistics
- `GET /api/v1/audit/stats` - Audit statistics
- `GET /api/v1/audit/security-events` - Recent security events
- `GET /api/v1/audit/failed-logins` - Failed login attempts

### Export
- `GET /api/v1/audit/export` - Export audit logs (JSON/CSV)

## Events

### Produces
- `AuditLogged.v1` - When audit log is created
- `AuditAlertTriggered.v1` - When security alert is triggered
- `ComplianceReportGenerated.v1` - When compliance report is generated

### Consumes
- `UserAuthenticated.v1`
- `UserRegistered.v1`
- `FieldCreated.v1`, `FieldUpdated.v1`, `FieldDeleted.v1`
- `AlertTriggered.v1`
- `TaskCreated.v1`, `TaskCompleted.v1`

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Service port | `8114` |
| `ENVIRONMENT` | Environment name | `development` |
| `DATABASE_URL` | PostgreSQL connection string | - |
| `NATS_URL` | NATS server URL | - |
| `REDIS_URL` | Redis connection string | - |

## Development

```bash
# Run locally
uvicorn src.main:app --host 0.0.0.0 --port 8114 --reload

# Run tests
pytest tests/ -v

# Build Docker image
docker build -t sahool-audit-service .
```

## Port

**8114**
