# SAHOOL Traceability Service

## خدمة التتبع - من المزرعة إلى المائدة

Farm-to-table supply chain traceability service with QR codes, blockchain anchoring, and consumer product journey.

خدمة تتبع سلسلة التوريد من المزرعة إلى المائدة مع رموز QR والتثبيت على البلوكتشين ورحلة المنتج للمستهلك.

---

## Features | الميزات

- **Batch Management** | إدارة الدفعات
  - Produce batch creation and tracking
  - Unique batch codes with checksum validation
  - Batch splits and merges
  - Complete batch history

- **Supply Chain Events** | أحداث سلسلة التوريد
  - Harvest recording with field data
  - Processing facility tracking
  - Storage conditions monitoring
  - Transportation tracking
  - Retail point of sale

- **QR Code Generation** | إنشاء رموز QR
  - Multiple QR formats (PNG, SVG, PDF)
  - Various sizes (Small, Medium, Large, XLarge)
  - Label generation with batch info
  - Bilingual labels (Arabic/English)

- **Consumer Journey** | رحلة المستهلك
  - Public product journey display
  - Certification verification
  - Quality grade information
  - Carbon footprint calculation

- **Certifications & Compliance** | الشهادات والامتثال
  - GlobalGAP certification tracking
  - Organic certification
  - SASO standards compliance
  - ISO certifications

---

## API Endpoints | نقاط النهاية

### Health Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/healthz` | GET | Kubernetes liveness probe |
| `/readyz` | GET | Kubernetes readiness probe |
| `/health` | GET | Comprehensive health check with dependencies |
| `/metrics` | GET | Prometheus metrics |

### Batches

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/traceability/batches` | GET | List produce batches (optional tenant_id, farm_id filters) |
| `/api/v1/traceability/batches` | POST | Create new batch with auto-generated batch code |
| `/api/v1/traceability/batches/{batch_id}` | GET | Get batch details |
| `/api/v1/traceability/batches/{batch_id}` | PUT | Update batch details (product name, quantity, status) |
| `/api/v1/traceability/batches/{batch_id}/split` | POST | Split batch into sub-batches |
| `/api/v1/traceability/batches/generate-code` | POST | Generate batch code (product_code, year, sequence) |
| `/api/v1/traceability/batches/verify-code/{code}` | GET | Verify batch code format and existence |

### Supply Chain Events

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/traceability/batches/{batch_id}/events` | GET | List all events for a batch |
| `/api/v1/traceability/batches/{batch_id}/events/harvest` | POST | Record harvest event |
| `/api/v1/traceability/batches/{batch_id}/events/processing` | POST | Record processing event |
| `/api/v1/traceability/batches/{batch_id}/events/storage` | POST | Record storage event |
| `/api/v1/traceability/batches/{batch_id}/events/transport` | POST | Record transport event |

### QR Codes

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/traceability/batches/{batch_id}/qr` | GET | Get QR code for batch |

### Consumer Journey & Carbon

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/traceability/journey/{batch_code}` | GET | Get consumer-facing product journey |
| `/api/v1/traceability/carbon/{batch_id}` | GET | Estimate carbon footprint from transport events |

### Recall Management (GS1 EPCIS Compliant)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/traceability/batches/{batch_id}/recall` | POST | Initiate product recall with forward trace |

### Planned Endpoints (Not Yet Implemented)

- **Batch Merge**: Merge multiple batches into one
- **Retail Events**: Record retail/point-of-sale events
- **Consumer Features**: Consumer scan recording, certification display
- **Certifications**: Full certification CRUD and batch attachment
- **Reports**: Trace reports, supply chain reports, compliance reports

---

## NATS Events | الأحداث

All events use centralized constants from `shared.events.subjects`.

### Produces

| Event | NATS Subject | Description |
|-------|-------------|-------------|
| `BatchCreated.v1` | `sahool.traceability.batch_created` | New produce batch created |
| `BatchSplit.v1` | `sahool.traceability.batch_split` | Batch split into sub-batches |
| `BatchRecalled.v1` | `sahool.traceability.batch_recalled` | Product recall initiated |
| `HarvestRecorded.v1` | `sahool.traceability.harvest_recorded` | Harvest event recorded |
| `ProcessingRecorded.v1` | `sahool.traceability.processing_recorded` | Processing event recorded |
| `StorageRecorded.v1` | `sahool.traceability.storage_recorded` | Storage event recorded |
| `TransportRecorded.v1` | `sahool.traceability.transport_recorded` | Transport event recorded |
| `NotificationSend.v1` | `sahool.notification.send` | Critical recall notifications |

### Consumes

| Event | Description |
|-------|-------------|
| `FieldCreated.v1` | Field data for producer tracking |
| `HarvestCompleted.v1` | Harvest task completion |

---

## Environment Variables | متغيرات البيئة

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `PORT` | Service port | `8123` | No |
| `HOST` | Bind address | `0.0.0.0` | No |
| `ENVIRONMENT` | Environment (development/staging/production) | `development` | No |
| `DATABASE_URL` | PostgreSQL connection string | - | Yes |
| `REDIS_URL` | Redis connection string | - | Yes |
| `NATS_URL` | NATS server URL | - | Yes |
| `QR_BASE_URL` | Base URL for QR code links | - | No |
| `BLOCKCHAIN_ENABLED` | Enable blockchain anchoring | `false` | No |
| `BLOCKCHAIN_RPC_URL` | Blockchain RPC endpoint | - | No |
| `LOG_LEVEL` | Logging level | `INFO` | No |

---

## Port

**8123**

---

## Quick Start | البداية السريعة

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the service
uvicorn src.main:app --host 0.0.0.0 --port 8123 --reload
```

### Docker

```bash
# Build image
docker build -t sahool/traceability-service .

# Run container
docker run -p 8123:8123 \
  -e DATABASE_URL=postgresql://user:pass@localhost:5432/sahool \
  -e REDIS_URL=redis://localhost:6379 \
  -e NATS_URL=nats://localhost:4222 \
  sahool/traceability-service
```

---

## Kubernetes Deployment | نشر Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: traceability-service
  namespace: sahool
  labels:
    app: traceability-service
    tier: business
spec:
  replicas: 2
  selector:
    matchLabels:
      app: traceability-service
  template:
    metadata:
      labels:
        app: traceability-service
    spec:
      containers:
        - name: traceability-service
          image: sahool/traceability-service:latest
          ports:
            - containerPort: 8123
          env:
            - name: PORT
              value: "8123"
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: sahool-secrets
                  key: database-url
            - name: REDIS_URL
              valueFrom:
                secretKeyRef:
                  name: sahool-secrets
                  key: redis-url
            - name: NATS_URL
              valueFrom:
                configMapKeyRef:
                  name: sahool-config
                  key: nats-url
            - name: QR_BASE_URL
              value: "https://trace.sahool.app"
          livenessProbe:
            httpGet:
              path: /healthz
              port: 8123
            initialDelaySeconds: 10
            periodSeconds: 15
          readinessProbe:
            httpGet:
              path: /readyz
              port: 8123
            initialDelaySeconds: 5
            periodSeconds: 10
          resources:
            requests:
              cpu: "200m"
              memory: "256Mi"
            limits:
              cpu: "500m"
              memory: "512Mi"
---
apiVersion: v1
kind: Service
metadata:
  name: traceability-service
  namespace: sahool
spec:
  selector:
    app: traceability-service
  ports:
    - port: 8123
      targetPort: 8123
  type: ClusterIP
```

---

## Consumer Journey Example | مثال رحلة المستهلك

When a consumer scans the QR code on a product, they see:

```json
{
  "product": {
    "name_en": "Organic Tomatoes",
    "name_ar": "طماطم عضوية",
    "batch_code": "TM-25-001",
    "grade": "A"
  },
  "producer": {
    "name": "Al-Falah Farm",
    "location": "Riyadh, Saudi Arabia",
    "certifications": ["GlobalGAP", "Organic"]
  },
  "journey": [
    {
      "event": "Harvested",
      "date": "2025-01-15",
      "location": "Field A, Al-Falah Farm"
    },
    {
      "event": "Quality Checked",
      "date": "2025-01-15",
      "grade": "A"
    },
    {
      "event": "Packed",
      "date": "2025-01-16",
      "facility": "Al-Falah Packing House"
    },
    {
      "event": "Shipped",
      "date": "2025-01-17",
      "destination": "Retail Distribution Center"
    }
  ],
  "carbon_footprint": {
    "total_kg_co2": 0.45,
    "per_kg": 0.09
  }
}
```

---

## Testing | الاختبار

```bash
# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test
pytest tests/test_qr_generator.py -v
```

---

## Dependencies | التبعيات

This service uses the shared traceability module:

```python
from shared.traceability import (
    SupplyChainTracker,
    QRCodeGenerator,
    generate_batch_code,
    calculate_carbon_footprint,
)
from shared.traceability.models import TransportMode
```

---

## License | الترخيص

Proprietary - KAFAAT

---

**Version**: 16.0.0
**Last Updated**: March 2026
