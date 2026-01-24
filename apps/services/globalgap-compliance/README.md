# GlobalGAP Compliance Service | خدمة الامتثال لـ GlobalGAP

> Farm certification compliance tracking for GlobalGAP IFA v6 standards

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](package.json)
[![Python](https://img.shields.io/badge/python-3.11-green.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.0+-red.svg)](https://fastapi.tiangolo.com)

## Overview | نظرة عامة

The GlobalGAP Compliance Service manages certification compliance tracking for farms following GlobalGAP IFA v6 standards. It provides comprehensive tools for audit management, checklist assessments, and certificate lifecycle tracking.

خدمة الامتثال لـ GlobalGAP تدير تتبع الامتثال للشهادات للمزارع وفقاً لمعايير GlobalGAP IFA v6. توفر أدوات شاملة لإدارة التدقيق وتقييمات قوائم الفحص وتتبع دورة حياة الشهادات.

## Features | الميزات

- **Compliance Tracking**: Real-time compliance status calculation
- **Checklist Management**: Full GlobalGAP IFA v6 checklist support (AF & CB)
- **Audit Management**: Internal, external, and certification audits
- **Non-Conformity Tracking**: Severity-based categorization with corrective actions
- **Certificate Management**: GGN lifecycle tracking with expiry alerts
- **Multi-Tenant Support**: Tenant isolation via X-Tenant-Id header
- **Bilingual Support**: Arabic and English throughout
- **Event-Driven**: NATS event publishing for integrations

## Directory Structure | هيكل المجلدات

```
globalgap-compliance/
├── Dockerfile
├── requirements.txt
├── src/
│   ├── main.py                  # FastAPI entry point
│   ├── config.py                # Settings and configuration
│   ├── database.py              # Database connection & repositories
│   ├── models/
│   │   ├── certificate.py       # GGN certificate models
│   │   ├── checklist.py         # Checklist and assessment models
│   │   └── compliance.py        # Compliance record and audit models
│   ├── repositories/
│   │   └── compliance_repository.py
│   ├── services/
│   │   ├── audit_service.py     # Audit preparation logic
│   │   ├── checklist_service.py # Checklist management
│   │   └── compliance_service.py
│   └── events/
│       └── nats_publisher.py    # NATS event publishing
├── migrations/
│   ├── 001_initial_schema.sql
│   └── 002_add_indexes.sql
└── examples/
    └── database_usage.py
```

## API Endpoints | نقاط النهاية

### Health Check | فحص الصحة

| Endpoint | Method | Purpose | الوصف |
|----------|--------|---------|-------|
| `/health` | GET | Full health check with dependencies | فحص شامل مع التبعيات |
| `/healthz` | GET | Kubernetes liveness probe | فحص الحياة |
| `/health/live` | GET | Alias for liveness | فحص الحياة (بديل) |
| `/readyz` | GET | Kubernetes readiness probe | فحص الجاهزية |
| `/health/ready` | GET | Alias for readiness | فحص الجاهزية (بديل) |

**GET /health**
```json
{
    "status": "healthy",
    "service": "globalgap-compliance",
    "version": "1.0.0",
    "timestamp": "2026-01-24T10:30:00Z",
    "dependencies": {
        "storage": "in_memory",
        "storage_records": 42,
        "nats": "connected"
    }
}
```

**GET /healthz**
```json
{
    "status": "alive",
    "service": "globalgap-compliance",
    "timestamp": "2026-01-24T10:30:00Z"
}
```

**GET /readyz**
```json
{
    "status": "ready",
    "service": "globalgap-compliance",
    "database": false,
    "nats": true
}
```

### Compliance | الامتثال

| Endpoint | Method | Purpose | الوصف |
|----------|--------|---------|-------|
| `/farms/{farm_id}/compliance` | GET | Get compliance status | حالة الامتثال |
| `/farms/{farm_id}/compliance` | POST | Create/update compliance | إنشاء/تحديث |
| `/farms/{farm_id}/compliance/trends` | GET | Compliance trends | اتجاهات الامتثال |

**GET /farms/{farm_id}/compliance**

Headers: `X-Tenant-Id: tenant_001`

Response:
```json
{
    "id": "comp_001",
    "farm_id": "farm_001",
    "tenant_id": "tenant_001",
    "overall_status": "partially_compliant",
    "compliance_percentage": 92.5,
    "total_control_points": 250,
    "compliant_points": 231,
    "non_compliant_points": 19,
    "major_must_fails": 0,
    "minor_must_fails": 12,
    "ifa_version": "6.0",
    "assessment_date": "2026-01-15T10:00:00Z"
}
```

### Checklists | قوائم الفحص

| Endpoint | Method | Purpose | الوصف |
|----------|--------|---------|-------|
| `/checklists` | GET | List available checklists | قوائم الفحص المتاحة |
| `/checklists/{id}/items` | GET | Get checklist items | عناصر قائمة الفحص |
| `/farms/{farm_id}/assessments` | GET | Farm assessments | تقييمات المزرعة |
| `/farms/{farm_id}/assessments` | POST | Create assessment | إنشاء تقييم |

### Audits | التدقيق

| Endpoint | Method | Purpose | الوصف |
|----------|--------|---------|-------|
| `/audits` | POST | Create audit report | إنشاء تقرير تدقيق |
| `/audits/{audit_id}` | GET | Get audit result | نتيجة التدقيق |
| `/farms/{farm_id}/audits` | GET | Farm audit history | سجل تدقيق المزرعة |

**POST /audits**

Query: `?farm_id=farm_001&audit_type=internal&auditor_name=Ahmed`

Response:
```json
{
    "id": "audit_001",
    "farm_id": "farm_001",
    "audit_type": "internal",
    "auditor_name": "Ahmed",
    "audit_date": "2026-01-24T10:00:00Z",
    "audit_status": "conditional",
    "overall_score": 87.5,
    "total_findings": 15,
    "critical_findings": 0,
    "major_findings": 3,
    "minor_findings": 12,
    "executive_summary_ar": "التدقيق يظهر امتثال جيد مع بعض الملاحظات",
    "executive_summary_en": "Audit shows good compliance with some observations",
    "recommendations": ["Address water storage issues", "Update pest records"],
    "follow_up_required": true,
    "follow_up_deadline": "2026-02-24T10:00:00Z"
}
```

### Non-Conformities | عدم المطابقة

| Endpoint | Method | Purpose | الوصف |
|----------|--------|---------|-------|
| `/farms/{farm_id}/non-conformities` | GET | List non-conformities | قائمة عدم المطابقة |
| `/non-conformities` | POST | Create non-conformity | إنشاء عدم مطابقة |

### Certificates | الشهادات

| Endpoint | Method | Purpose | الوصف |
|----------|--------|---------|-------|
| `/farms/{farm_id}/certificates` | GET | Farm certificates | شهادات المزرعة |
| `/certificates` | POST | Create certificate | إنشاء شهادة |
| `/certificates/{id}` | GET | Get certificate | تفاصيل الشهادة |

## Data Models | نماذج البيانات

### Compliance Status | حالة الامتثال
```python
COMPLIANT = "compliant"
NON_COMPLIANT = "non_compliant"
PARTIALLY_COMPLIANT = "partially_compliant"
PENDING_REVIEW = "pending_review"
NOT_ASSESSED = "not_assessed"
```

### Severity Levels | مستويات الخطورة
```python
CRITICAL = "critical"    # Immediate action required
MAJOR = "major"          # Major Must failure
MINOR = "minor"          # Minor Must failure
OBSERVATION = "observation"  # Recommendation
```

### Compliance Levels | مستويات الامتثال
```python
MAJOR_MUST = "major_must"      # 100% required - No certification if failed
MINOR_MUST = "minor_must"      # 95% required
RECOMMENDATION = "recommendation"  # Best practice
```

### Certificate Status | حالة الشهادة
```python
ACTIVE = "active"
EXPIRED = "expired"
SUSPENDED = "suspended"
WITHDRAWN = "withdrawn"
PENDING_APPROVAL = "pending_approval"
RENEWAL_REQUIRED = "renewal_required"
```

## Database Schema | مخطط قاعدة البيانات

### Tables | الجداول

| Table | Purpose | الوصف |
|-------|---------|-------|
| `globalgap_registrations` | Farm GGN registrations | تسجيلات المزارع |
| `compliance_records` | Audit results & scores | نتائج التدقيق |
| `checklist_responses` | Individual item responses | استجابات العناصر |
| `non_conformances` | Non-conformities & actions | عدم المطابقة |

## Events | الأحداث

Events are published to NATS for integration with other services.

| Event | Subject | Trigger |
|-------|---------|---------|
| Compliance Updated | `compliance.updated` | Compliance record changed |
| Audit Completed | `compliance.audit.completed` | Audit report generated |
| Non-Conformity Created | `compliance.non_conformity.created` | New NC recorded |
| Non-Conformity Resolved | `compliance.non_conformity.resolved` | NC resolved |
| Certificate Created | `compliance.certificate.created` | New certificate |
| Certificate Renewed | `compliance.certificate.renewed` | Certificate renewed |
| Certificate Expired | `compliance.certificate.expired` | Certificate expired |

## Configuration | الإعدادات

### Environment Variables | متغيرات البيئة

```bash
# Service
SERVICE_NAME=globalgap-compliance
SERVICE_VERSION=1.0.0
SERVICE_PORT=8120
LOG_LEVEL=INFO

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@postgres:5432/sahool_compliance
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20

# NATS
NATS_URL=nats://nats:4222
NATS_SUBJECT_PREFIX=sahool.compliance

# GlobalGAP
IFA_VERSION=6.0
GGN_CHECK_INTERVAL=86400
AUDIT_RETENTION_DAYS=1825
CERTIFICATE_RENEWAL_WARNING_DAYS=90

# Features
ENABLE_AUTO_CHECKLIST_GENERATION=true
CHECKLIST_LANGUAGE=ar
ENABLE_CACHE=true
CACHE_TTL=3600
```

## Development | التطوير

### Prerequisites | المتطلبات

- Python 3.11+
- PostgreSQL 16+
- NATS Server (optional)

### Installation | التثبيت

```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
psql $DATABASE_URL -f migrations/001_initial_schema.sql
psql $DATABASE_URL -f migrations/002_add_indexes.sql

# Run locally
uvicorn src.main:app --host 0.0.0.0 --port 8120 --reload
```

### Docker

```bash
# Build
docker build -t sahool/globalgap-compliance:latest .

# Run
docker run -p 8123:8123 \
  -e DATABASE_URL="postgresql+asyncpg://..." \
  -e NATS_URL="nats://nats:4222" \
  sahool/globalgap-compliance:latest
```

## Kubernetes Deployment | النشر على Kubernetes

```yaml
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: globalgap-compliance
    image: sahool/globalgap-compliance:latest
    ports:
    - containerPort: 8123
    livenessProbe:
      httpGet:
        path: /health/live
        port: 8123
      initialDelaySeconds: 15
      periodSeconds: 30
    readinessProbe:
      httpGet:
        path: /health/ready
        port: 8123
      initialDelaySeconds: 10
      periodSeconds: 10
    env:
    - name: DATABASE_URL
      valueFrom:
        secretKeyRef:
          name: db-credentials
          key: url
```

## GlobalGAP IFA v6 Categories | فئات GlobalGAP

### All Farm Base (AF) | قاعدة كل المزارع

| Category | Code | الوصف |
|----------|------|-------|
| Site Management | AF.1 | إدارة الموقع |
| Soil Management | AF.2 | إدارة التربة |
| Fertilizer Use | AF.3 | استخدام الأسمدة |
| Irrigation | AF.4 | الري |
| Crop Protection | AF.5 | حماية المحاصيل |
| Harvest | AF.6 | الحصاد |
| Produce Handling | AF.7 | معالجة المنتجات |
| Waste & Pollution | AF.8 | النفايات والتلوث |
| Worker Health & Safety | AF.9 | صحة وسلامة العمال |
| Environment | AF.10 | البيئة |

### Crops Base (CB) | قاعدة المحاصيل

| Category | Code | الوصف |
|----------|------|-------|
| Propagation Material | CB.1 | مواد الإكثار |
| Site History | CB.2 | تاريخ الموقع |

## Compliance Rules | قواعد الامتثال

- **Major Must**: 100% compliance required for certification
- **Minor Must**: Minimum 95% compliance required
- **Recommendations**: Best practices, not mandatory

## Related Services | الخدمات المرتبطة

- **field-management-service**: Farm and field data
- **notification-service**: Certificate expiry alerts
- **audit-service**: Audit logging

## License | الترخيص

Proprietary - KAFAAT © 2026

---

**Version**: 1.0.0
**Port**: 8120 (dev) / 8123 (docker)
**Last Updated**: January 2026
