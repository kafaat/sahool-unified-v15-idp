# SAHOOL Pest Detection Service

## خدمة كشف الآفات

AI-powered pest and disease detection service with Middle East pest database and IPM recommendations.

خدمة كشف الآفات والأمراض بالذكاء الاصطناعي مع قاعدة بيانات آفات الشرق الأوسط وتوصيات المكافحة المتكاملة.

---

## Features | الميزات

- **Pest Identification** | تحديد الآفات
  - 100+ pest species database (Middle East focus)
  - Image-based identification with AI
  - Symptom-based diagnosis
  - Bilingual pest descriptions (Arabic/English)

- **Scouting Management** | إدارة المسح الحقلي
  - Scout report recording and tracking
  - GPS-tagged observations
  - Infestation level assessment
  - Historical outbreak tracking

- **Threshold-Based Alerts** | تنبيهات قائمة على العتبات
  - Economic threshold monitoring
  - Action threshold alerts
  - Yield loss estimation
  - Treatment ROI calculations

- **Treatment Recommendations** | توصيات العلاج
  - Chemical control options with PHI/REI
  - Biological control alternatives
  - Cultural practices
  - IPM calendar integration

### Supported Pests | الآفات المدعومة

- Red Palm Weevil (سوسة النخيل الحمراء)
- Dubas Bug (دوباس النخيل)
- Aphids (المن)
- Whiteflies (الذبابة البيضاء)
- Spider Mites (العنكبوت الأحمر)
- Locusts (الجراد الصحراوي)
- Date Moth (فراشة التمر)
- Tomato Leafminer - Tuta absoluta (حافرة أنفاق الطماطم)
- Thrips (التربس)
- Fruit Flies (ذباب الفاكهة)

---

## API Endpoints | نقاط النهاية

### Health Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/healthz` | GET | Kubernetes liveness probe |
| `/readyz` | GET | Kubernetes readiness probe |
| `/health` | GET | Comprehensive health check with dependencies |
| `/metrics` | GET | Prometheus metrics |

### Pest Identification

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/pests` | GET | List all pests in database |
| `/api/v1/pests/{pest_id}` | GET | Get pest details |
| `/api/v1/pests/search` | GET | Search pests by name |
| `/api/v1/pests/crop/{crop}` | GET | Get pests for specific crop |
| `/api/v1/pests/identify` | POST | Identify pest from image |
| `/api/v1/pests/identify/symptoms` | POST | Identify by symptoms |
| `/api/v1/pests/quarantine` | GET | List quarantine pests |
| `/api/v1/pests/seasonal` | GET | Get seasonal pest predictions |

### Scout Reports

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/scouts/reports` | GET | List scout reports |
| `/api/v1/scouts/reports` | POST | Create scout report |
| `/api/v1/scouts/reports/{report_id}` | GET | Get specific report |
| `/api/v1/scouts/reports/{report_id}` | PUT | Update report |
| `/api/v1/scouts/reports/field/{field_id}` | GET | Get reports for field |
| `/api/v1/scouts/observations` | POST | Add observation to report |

### Thresholds & Alerts

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/thresholds` | GET | List economic thresholds |
| `/api/v1/thresholds/crop/{crop}/pest/{pest}` | GET | Get threshold for crop-pest |
| `/api/v1/thresholds/assess` | POST | Assess threshold status |
| `/api/v1/alerts` | GET | List active pest alerts |
| `/api/v1/alerts/{alert_id}` | GET | Get alert details |
| `/api/v1/alerts/{alert_id}/acknowledge` | POST | Acknowledge alert |

### Treatment Recommendations

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/treatments/recommend` | POST | Get treatment recommendations |
| `/api/v1/treatments/protocols/{pest_id}` | GET | Get treatment protocol |
| `/api/v1/treatments/ipm-calendar` | GET | Get IPM calendar for crop |
| `/api/v1/treatments/rotation` | GET | Get pesticide rotation plan |

---

## Events | الأحداث

### Produces

| Event | Description |
|-------|-------------|
| `PestDetected.v1` | Pest identified in field |
| `InfestationAlert.v1` | Infestation level exceeds threshold |
| `TreatmentRecommended.v1` | Treatment recommendation generated |
| `OutbreakTracked.v1` | Pest outbreak recorded |

### Consumes

| Event | Description |
|-------|-------------|
| `FieldIndicatorsComputed.v1` | Use field health data for risk assessment |
| `WeatherForecastReady.v1` | Weather for pest risk prediction |
| `SatelliteSceneIngested.v1` | Imagery for pest detection |
| `TaskCompleted.v1` | Track treatment application |

---

## Environment Variables | متغيرات البيئة

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `PORT` | Service port | `8171` | No |
| `HOST` | Bind address | `0.0.0.0` | No |
| `ENVIRONMENT` | Environment (development/staging/production) | `development` | No |
| `DATABASE_URL` | PostgreSQL connection string | - | Yes |
| `REDIS_URL` | Redis connection string | - | Yes |
| `NATS_URL` | NATS server URL | - | Yes |
| `AI_MODEL_PATH` | Path to pest detection AI model | - | No |
| `LOG_LEVEL` | Logging level | `INFO` | No |

---

## Port

**8171**

---

## Quick Start | البداية السريعة

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the service
uvicorn src.main:app --host 0.0.0.0 --port 8171 --reload
```

### Docker

```bash
# Build image
docker build -t sahool/pest-detection-service .

# Run container
docker run -p 8171:8171 \
  -e DATABASE_URL=postgresql://user:pass@localhost:5432/sahool \
  -e REDIS_URL=redis://localhost:6379 \
  -e NATS_URL=nats://localhost:4222 \
  sahool/pest-detection-service
```

---

## Kubernetes Deployment | نشر Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pest-detection-service
  namespace: sahool
  labels:
    app: pest-detection-service
    tier: intelligence
spec:
  replicas: 2
  selector:
    matchLabels:
      app: pest-detection-service
  template:
    metadata:
      labels:
        app: pest-detection-service
    spec:
      containers:
        - name: pest-detection-service
          image: sahool/pest-detection-service:latest
          ports:
            - containerPort: 8171
          env:
            - name: PORT
              value: "8171"
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
              port: 8171
            initialDelaySeconds: 15
            periodSeconds: 20
          readinessProbe:
            httpGet:
              path: /readyz
              port: 8171
            initialDelaySeconds: 10
            periodSeconds: 10
          resources:
            requests:
              cpu: "300m"
              memory: "512Mi"
            limits:
              cpu: "800m"
              memory: "1Gi"
---
apiVersion: v1
kind: Service
metadata:
  name: pest-detection-service
  namespace: sahool
spec:
  selector:
    app: pest-detection-service
  ports:
    - port: 8171
      targetPort: 8171
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
pytest tests/test_identification.py -v
```

---

## Dependencies | التبعيات

This service uses the shared pest scouting module:

```python
from shared.pest_scouting import (
    PestIdentification,
    ScoutReport,
    get_pest_by_id,
    assess_threshold,
    generate_treatment_recommendation,
)
```

---

## License | الترخيص

Proprietary - KAFAAT

---

**Version**: 1.0.0
**Last Updated**: January 2026
