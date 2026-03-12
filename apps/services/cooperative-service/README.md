# SAHOOL Cooperative Service

## خدمة التعاونيات الزراعية

Agricultural cooperatives management service for resource pooling, group purchasing, and revenue sharing.

خدمة إدارة التعاونيات الزراعية لتجميع الموارد والشراء الجماعي وتوزيع الإيرادات.

---

## Features | الميزات

- **Cooperative Management** | إدارة التعاونيات
  - Create and manage cooperatives with hierarchical structure
  - Member lifecycle management
  - Role-based access (Admin, Manager, Member)
  - Multi-tenant support

- **Resource Pooling** | تجميع الموارد
  - Shared equipment management (tractors, harvesters)
  - Storage facility scheduling
  - Transportation resources
  - Booking and scheduling system
  - Priority-based allocation

- **Group Purchasing** | الشراء الجماعي
  - Bulk purchase orders
  - Member order aggregation
  - Supplier management
  - Price negotiation tracking
  - Order fulfillment tracking

- **Revenue Sharing** | توزيع الإيرادات
  - Multiple sharing methods (Equal, Contribution, Production, Land Area, Weighted, Hybrid)
  - Financial period management
  - Transaction tracking
  - Payment distribution
  - Reporting and analytics

### Revenue Sharing Methods | طرق توزيع الإيرادات

| Method | Description | Description (AR) |
|--------|-------------|------------------|
| `EQUAL` | Equal distribution among all members | توزيع متساوي بين الأعضاء |
| `CONTRIBUTION` | Based on share/capital contribution | بناء على المساهمة المالية |
| `PRODUCTION` | Based on production volume | بناء على كمية الإنتاج |
| `LAND_AREA` | Based on contributed land area | بناء على مساحة الأرض |
| `WEIGHTED` | Custom weights per member | أوزان مخصصة لكل عضو |
| `HYBRID` | Combination of multiple methods | مزيج من عدة طرق |

---

## API Endpoints | نقاط النهاية

### Health Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/healthz` | GET | Kubernetes liveness probe |
| `/readyz` | GET | Kubernetes readiness probe |
| `/health` | GET | Comprehensive health check with dependencies |
| `/metrics` | GET | Prometheus metrics |

### Cooperatives

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/cooperatives` | GET | List cooperatives |
| `/api/v1/cooperatives` | POST | Create cooperative |
| `/api/v1/cooperatives/{coop_id}` | GET | Get cooperative details |
| `/api/v1/cooperatives/{coop_id}` | PUT | Update cooperative |
| `/api/v1/cooperatives/{coop_id}` | DELETE | Delete cooperative |
| `/api/v1/cooperatives/{coop_id}/stats` | GET | Get cooperative statistics |

### Members

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/cooperatives/{coop_id}/members` | GET | List members |
| `/api/v1/cooperatives/{coop_id}/members` | POST | Add member |
| `/api/v1/cooperatives/{coop_id}/members/{member_id}` | GET | Get member details |
| `/api/v1/cooperatives/{coop_id}/members/{member_id}` | PUT | Update member |
| `/api/v1/cooperatives/{coop_id}/members/{member_id}` | DELETE | Remove member |
| `/api/v1/cooperatives/{coop_id}/members/{member_id}/shares` | GET | Get member shares |

### Resources

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/cooperatives/{coop_id}/resources` | GET | List shared resources |
| `/api/v1/cooperatives/{coop_id}/resources` | POST | Register resource |
| `/api/v1/cooperatives/{coop_id}/resources/{resource_id}` | GET | Get resource details |
| `/api/v1/cooperatives/{coop_id}/resources/{resource_id}` | PUT | Update resource |
| `/api/v1/cooperatives/{coop_id}/resources/{resource_id}/availability` | GET | Get availability |
| `/api/v1/cooperatives/{coop_id}/resources/{resource_id}/usage` | GET | Get usage statistics |

### Bookings

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/cooperatives/{coop_id}/bookings` | GET | List bookings |
| `/api/v1/cooperatives/{coop_id}/bookings` | POST | Create booking |
| `/api/v1/cooperatives/{coop_id}/bookings/{booking_id}` | GET | Get booking details |
| `/api/v1/cooperatives/{coop_id}/bookings/{booking_id}` | PUT | Update booking |
| `/api/v1/cooperatives/{coop_id}/bookings/{booking_id}/cancel` | POST | Cancel booking |
| `/api/v1/cooperatives/{coop_id}/bookings/{booking_id}/complete` | POST | Complete booking |

### Group Purchases

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/cooperatives/{coop_id}/purchases` | GET | List purchase orders |
| `/api/v1/cooperatives/{coop_id}/purchases` | POST | Create purchase order |
| `/api/v1/cooperatives/{coop_id}/purchases/{order_id}` | GET | Get order details |
| `/api/v1/cooperatives/{coop_id}/purchases/{order_id}/members` | POST | Add member order |
| `/api/v1/cooperatives/{coop_id}/purchases/{order_id}/finalize` | POST | Finalize order |

### Revenue & Finance

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/cooperatives/{coop_id}/periods` | GET | List financial periods |
| `/api/v1/cooperatives/{coop_id}/periods` | POST | Create financial period |
| `/api/v1/cooperatives/{coop_id}/periods/{period_id}` | GET | Get period details |
| `/api/v1/cooperatives/{coop_id}/periods/{period_id}/close` | POST | Close period |
| `/api/v1/cooperatives/{coop_id}/transactions` | GET | List transactions |
| `/api/v1/cooperatives/{coop_id}/transactions` | POST | Record transaction |
| `/api/v1/cooperatives/{coop_id}/distribution` | POST | Create distribution plan |
| `/api/v1/cooperatives/{coop_id}/distribution/{plan_id}` | GET | Get distribution plan |
| `/api/v1/cooperatives/{coop_id}/distribution/{plan_id}/execute` | POST | Execute distribution |
| `/api/v1/cooperatives/{coop_id}/reports/revenue` | GET | Generate revenue report |

---

## Events | الأحداث

### Produces

| Event | Description |
|-------|-------------|
| `CooperativeCreated.v1` | New cooperative created |
| `MemberJoined.v1` | Member joined cooperative |
| `ResourceBooked.v1` | Resource booking created |
| `RevenueDistributed.v1` | Revenue distributed to members |
| `PurchaseOrderFinalized.v1` | Group purchase order finalized |

### Consumes

| Event | Description |
|-------|-------------|
| `YieldPredicted.v1` | Yield prediction for revenue planning |
| `FieldCreated.v1` | Field creation for land area tracking |
| `TaskCompleted.v1` | Task completion for resource usage |
| `OrderPaid.v1` | Marketplace order payment |

---

## Environment Variables | متغيرات البيئة

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `PORT` | Service port | `8127` | No |
| `HOST` | Bind address | `0.0.0.0` | No |
| `ENVIRONMENT` | Environment (development/staging/production) | `development` | No |
| `DATABASE_URL` | PostgreSQL connection string | - | Yes |
| `REDIS_URL` | Redis connection string | - | Yes |
| `NATS_URL` | NATS server URL | - | Yes |
| `LOG_LEVEL` | Logging level | `INFO` | No |

---

## Port

**8127**

---

## Quick Start | البداية السريعة

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the service
uvicorn src.main:app --host 0.0.0.0 --port 8127 --reload
```

### Docker

```bash
# Build image
docker build -t sahool/cooperative-service .

# Run container
docker run -p 8127:8127 \
  -e DATABASE_URL=postgresql://user:pass@localhost:5432/sahool \
  -e REDIS_URL=redis://localhost:6379 \
  -e NATS_URL=nats://localhost:4222 \
  sahool/cooperative-service
```

---

## Kubernetes Deployment | نشر Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cooperative-service
  namespace: sahool
  labels:
    app: cooperative-service
    tier: business
spec:
  replicas: 2
  selector:
    matchLabels:
      app: cooperative-service
  template:
    metadata:
      labels:
        app: cooperative-service
    spec:
      containers:
        - name: cooperative-service
          image: sahool/cooperative-service:latest
          ports:
            - containerPort: 8127
          env:
            - name: PORT
              value: "8127"
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
          livenessProbe:
            httpGet:
              path: /healthz
              port: 8127
            initialDelaySeconds: 10
            periodSeconds: 15
          readinessProbe:
            httpGet:
              path: /readyz
              port: 8127
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
  name: cooperative-service
  namespace: sahool
spec:
  selector:
    app: cooperative-service
  ports:
    - port: 8127
      targetPort: 8127
  type: ClusterIP
```

---

## Testing | الاختبار

```bash
# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test
pytest tests/test_revenue.py -v
```

---

## Dependencies | التبعيات

This service uses the shared cooperatives module:

```python
from shared.cooperatives import (
    Cooperative,
    CooperativeMember,
    SharedResource,
    ResourcePoolService,
    RevenueService,
    RevenueShareMethod,
)
```

---

## License | الترخيص

Proprietary - KAFAAT

---

**Version**: 16.0.0
**Last Updated**: March 2026
