# SAHOOL Soil Analysis Service

## خدمة تحليل التربة

Comprehensive soil testing and analysis service for agricultural operations with Middle East soil type classifications.

خدمة شاملة لتحليل واختبار التربة للعمليات الزراعية مع تصنيفات أنواع التربة في الشرق الأوسط.

---

## Features | الميزات

- **Soil Test Management** | إدارة اختبارات التربة
  - Record and store soil test results from multiple labs
  - Support for NPK, pH, EC, organic matter, micronutrients
  - Sample location tracking with GPS coordinates

- **Nutrient Interpretation** | تفسير مستويات العناصر الغذائية
  - Crop-specific nutrient level assessment
  - Deficiency and toxicity detection
  - Middle East regional thresholds

- **Amendment Recommendations** | توصيات التعديل والتسميد
  - 50+ fertilizer products database
  - Cost-effective amendment plans
  - Application rate calculations

- **Historical Trend Analysis** | تحليل الاتجاهات التاريخية
  - Multi-year soil health tracking
  - Nutrient depletion/accumulation patterns
  - Management practice impact analysis

---

## API Endpoints | نقاط النهاية

### Health Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/healthz` | GET | Kubernetes liveness probe |
| `/readyz` | GET | Kubernetes readiness probe |
| `/health` | GET | Comprehensive health check with dependencies |
| `/metrics` | GET | Prometheus metrics |

### Soil Tests

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/soil/tests` | POST | Create new soil test record |
| `/api/v1/soil/tests/{test_id}` | GET | Get specific soil test result |
| `/api/v1/soil/tests/{test_id}` | DELETE | Delete soil test record |
| `/api/v1/soil/tests/field/{field_id}` | GET | Get all tests for a field |

### Interpretation

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/soil/interpret` | POST | Interpret soil test results (crop-specific) |
| `/api/v1/soil/interpretation/nutrient-status` | POST | Check individual nutrient status (nutrient, value, extraction_method) |
| `/api/v1/soil/interpretation/ph-status` | POST | Check soil pH status and classification |
| `/api/v1/soil/interpretation/ec-status` | POST | Check soil EC/salinity status |

### Recommendations

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/soil/recommendations/amendment-plan` | POST | Generate amendment plan (crop, target_yield, field_area_ha) |
| `/api/v1/soil/recommendations/calculate-rate` | POST | Calculate fertilizer application rate (nutrient_needed_kg_ha, fertilizer_nutrient_percent) |
| `/api/v1/soil/products` | GET | List available fertilizer products |
| `/api/v1/soil/crops/{crop}/requirements` | GET | Get crop nutrient requirements |

### Trends

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/soil/trends` | POST | Analyze soil trends for a field (field_id, tenant_id) |
| `/api/v1/soil/trends/nutrient` | POST | Get trend for a specific nutrient (field_id, tenant_id, nutrient) |
| `/api/v1/soil/trends/compare-periods` | POST | Compare soil health between two time periods |

---

## Events | الأحداث

### Produces

| Event | Description |
|-------|-------------|
| `SoilAnalysisCompleted.v1` | Soil test analysis has been completed |
| `AmendmentPlanGenerated.v1` | Amendment recommendation plan generated |
| `SoilTrendAlert.v1` | Alert for significant soil health changes |

### Consumes

| Event | Description |
|-------|-------------|
| `FieldCreated.v1` | New field created, initialize soil profile |
| `WeatherForecastReady.v1` | Weather data for application timing |
| `TaskCompleted.v1` | Track completed amendment tasks |

---

## Environment Variables | متغيرات البيئة

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `PORT` | Service port | `8134` | No |
| `HOST` | Bind address | `0.0.0.0` | No |
| `ENVIRONMENT` | Environment (development/staging/production) | `development` | No |
| `DATABASE_URL` | PostgreSQL connection string | - | Yes |
| `REDIS_URL` | Redis connection string | - | Yes |
| `NATS_URL` | NATS server URL | - | Yes |
| `LOG_LEVEL` | Logging level | `INFO` | No |

---

## Port

**8134**

---

## Quick Start | البداية السريعة

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the service
uvicorn src.main:app --host 0.0.0.0 --port 8134 --reload
```

### Docker

```bash
# Build image
docker build -t sahool/soil-analysis-service .

# Run container
docker run -p 8134:8134 \
  -e DATABASE_URL=postgresql://user:pass@localhost:5432/sahool \
  -e REDIS_URL=redis://localhost:6379 \
  -e NATS_URL=nats://localhost:4222 \
  sahool/soil-analysis-service
```

---

## Kubernetes Deployment | نشر Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: soil-analysis-service
  namespace: sahool
  labels:
    app: soil-analysis-service
    tier: intelligence
spec:
  replicas: 2
  selector:
    matchLabels:
      app: soil-analysis-service
  template:
    metadata:
      labels:
        app: soil-analysis-service
    spec:
      containers:
        - name: soil-analysis-service
          image: sahool/soil-analysis-service:latest
          ports:
            - containerPort: 8134
          env:
            - name: PORT
              value: "8134"
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
              port: 8134
            initialDelaySeconds: 10
            periodSeconds: 15
          readinessProbe:
            httpGet:
              path: /readyz
              port: 8134
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
  name: soil-analysis-service
  namespace: sahool
spec:
  selector:
    app: soil-analysis-service
  ports:
    - port: 8134
      targetPort: 8134
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
pytest tests/test_interpretation.py -v
```

---

## Dependencies | التبعيات

This service uses the shared soil testing module:

```python
from shared.soil_testing import (
    SoilTestResult,
    SoilTestInterpreter,
    SoilAmendmentRecommender,
    SoilTrendAnalyzer,
)
```

---

## License | الترخيص

Proprietary - KAFAAT

---

**Version**: 16.0.0
**Last Updated**: February 2026
