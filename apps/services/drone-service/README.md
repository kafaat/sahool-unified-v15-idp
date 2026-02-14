# SAHOOL Drone Service

## خدمة الطائرات بدون طيار

Comprehensive drone integration service for agricultural operations including flight planning, VRA maps, and aerial imagery.

خدمة شاملة لتكامل الطائرات بدون طيار للعمليات الزراعية بما في ذلك تخطيط الرحلات وخرائط التطبيق المتغير والصور الجوية.

---

## Features | الميزات

- **Flight Planning** | تخطيط الرحلات
  - Parallel (boustrophedon) patterns
  - Crosshatch patterns for thorough coverage
  - Perimeter flights
  - Mapping missions with overlap calculation
  - Weather assessment before flight

- **Variable Rate Application (VRA)** | التطبيق بالمعدل المتغير
  - NDVI-based prescription maps
  - Weed/pest spot spray maps
  - Fertilizer prescription maps
  - Multiple classification methods

- **Mission Management** | إدارة المهام
  - Spray mission planning and execution
  - Mapping mission management
  - Resource estimation (time, battery, chemical)
  - Real-time telemetry tracking

- **Aerial Imagery** | الصور الجوية
  - Multispectral image processing
  - Orthomosaic generation
  - NDVI/vegetation index extraction
  - Anomaly detection

### Supported Drones | الطائرات المدعومة

**DJI Agricultural Drones:**
- DJI Agras T40, T30, T20P
- DJI Mavic 3 Multispectral
- DJI Phantom 4 RTK
- DJI Matrice 300/350 RTK

**Open Source Platforms:**
- ArduPilot-based drones (MAVLink)
- PX4-based drones (MAVLink)
- Custom platforms

---

## API Endpoints | نقاط النهاية

### Health Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/healthz` | GET | Kubernetes liveness probe |
| `/readyz` | GET | Kubernetes readiness probe |
| `/health` | GET | Comprehensive health check with dependencies |
| `/metrics` | GET | Prometheus metrics |

### Drones

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/drones` | GET | List registered drones |
| `/api/v1/drones` | POST | Register new drone |
| `/api/v1/drones/{drone_id}` | GET | Get drone details |
| `/api/v1/drones/{drone_id}` | PUT | Update drone info |
| `/api/v1/drones/{drone_id}` | DELETE | Deregister drone |
| `/api/v1/drones/{drone_id}/status` | GET | Get real-time status |
| `/api/v1/drones/{drone_id}/telemetry` | GET | Get telemetry history |

### Flight Planning

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/flights/plan/spray` | POST | Create spray flight plan |
| `/api/v1/flights/plan/mapping` | POST | Create mapping flight plan |
| `/api/v1/flights/plan/perimeter` | POST | Create perimeter flight plan |
| `/api/v1/flights/weather-check` | POST | Check weather for flight |
| `/api/v1/flights/estimate` | POST | Estimate flight resources |

### Missions

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/missions` | GET | List missions |
| `/api/v1/missions` | POST | Create mission |
| `/api/v1/missions/{mission_id}` | GET | Get mission details |
| `/api/v1/missions/{mission_id}` | PUT | Update mission |
| `/api/v1/missions/{mission_id}/start` | POST | Start mission execution |
| `/api/v1/missions/{mission_id}/pause` | POST | Pause mission |
| `/api/v1/missions/{mission_id}/resume` | POST | Resume mission |
| `/api/v1/missions/{mission_id}/abort` | POST | Abort mission |
| `/api/v1/missions/{mission_id}/export` | GET | Export mission (KML/MAVLink) |

### VRA (Variable Rate Application)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/vra/prescription` | POST | Generate prescription map |
| `/api/v1/vra/prescription/ndvi` | POST | Generate NDVI-based prescription |
| `/api/v1/vra/prescription/spot-spray` | POST | Generate spot spray map |
| `/api/v1/vra/{prescription_id}` | GET | Get prescription map |
| `/api/v1/vra/{prescription_id}/export` | GET | Export prescription (Shapefile/GeoJSON) |
| `/api/v1/vra/{prescription_id}/zones` | GET | Get application zones |

### Flight Logs

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/logs` | GET | List flight logs |
| `/api/v1/logs/{log_id}` | GET | Get flight log details |
| `/api/v1/logs/{log_id}/track` | GET | Get flight track |
| `/api/v1/logs/{log_id}/export` | GET | Export log (GeoJSON/KML) |
| `/api/v1/logs/{log_id}/analytics` | GET | Get flight analytics |

### Imagery

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/imagery` | GET | List captured imagery |
| `/api/v1/imagery` | POST | Upload imagery |
| `/api/v1/imagery/{imagery_id}` | GET | Get imagery details |
| `/api/v1/imagery/{imagery_id}/process` | POST | Process imagery (NDVI, etc.) |
| `/api/v1/imagery/{imagery_id}/download` | GET | Download processed imagery |

---

## Events | الأحداث

### Produces

| Event | Description |
|-------|-------------|
| `FlightPlanCreated.v1` | Flight plan has been created |
| `MissionStarted.v1` | Drone mission has started |
| `MissionCompleted.v1` | Drone mission completed |
| `DroneAlert.v1` | Drone alert (low battery, weather, etc.) |
| `AerialImageProcessed.v1` | Aerial imagery processed |
| `PrescriptionMapReady.v1` | VRA prescription map ready |

### Consumes

| Event | Description |
|-------|-------------|
| `FieldCreated.v1` | New field for mission planning |
| `NDVIProcessed.v1` | NDVI data for prescription maps |
| `WeatherForecastReady.v1` | Weather for flight assessment |
| `PestDetected.v1` | Pest detection for spot spray |

---

## Environment Variables | متغيرات البيئة

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `PORT` | Service port | `8126` | No |
| `HOST` | Bind address | `0.0.0.0` | No |
| `ENVIRONMENT` | Environment (development/staging/production) | `development` | No |
| `DATABASE_URL` | PostgreSQL connection string | - | Yes |
| `REDIS_URL` | Redis connection string | - | Yes |
| `NATS_URL` | NATS server URL | - | Yes |
| `DJI_APP_KEY` | DJI FlightHub API key | - | No |
| `DJI_APP_SECRET` | DJI FlightHub API secret | - | No |
| `MAVLINK_CONNECTION` | MAVLink connection string | - | No |
| `LOG_LEVEL` | Logging level | `INFO` | No |

---

## Port

**8126**

---

## Quick Start | البداية السريعة

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the service
uvicorn src.main:app --host 0.0.0.0 --port 8126 --reload
```

### Docker

```bash
# Build image
docker build -t sahool/drone-service .

# Run container
docker run -p 8126:8126 \
  -e DATABASE_URL=postgresql://user:pass@localhost:5432/sahool \
  -e REDIS_URL=redis://localhost:6379 \
  -e NATS_URL=nats://localhost:4222 \
  sahool/drone-service
```

---

## Kubernetes Deployment | نشر Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: drone-service
  namespace: sahool
  labels:
    app: drone-service
    tier: integration
spec:
  replicas: 2
  selector:
    matchLabels:
      app: drone-service
  template:
    metadata:
      labels:
        app: drone-service
    spec:
      containers:
        - name: drone-service
          image: sahool/drone-service:latest
          ports:
            - containerPort: 8126
          env:
            - name: PORT
              value: "8126"
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
            - name: DJI_APP_KEY
              valueFrom:
                secretKeyRef:
                  name: drone-secrets
                  key: dji-app-key
                  optional: true
          livenessProbe:
            httpGet:
              path: /healthz
              port: 8126
            initialDelaySeconds: 10
            periodSeconds: 15
          readinessProbe:
            httpGet:
              path: /readyz
              port: 8126
            initialDelaySeconds: 5
            periodSeconds: 10
          resources:
            requests:
              cpu: "300m"
              memory: "384Mi"
            limits:
              cpu: "600m"
              memory: "768Mi"
---
apiVersion: v1
kind: Service
metadata:
  name: drone-service
  namespace: sahool
spec:
  selector:
    app: drone-service
  ports:
    - port: 8126
      targetPort: 8126
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
pytest tests/test_flight_planner.py -v
```

---

## Dependencies | التبعيات

This service uses the shared drone integration module:

```python
from shared.drone_integration import (
    FlightPlanner,
    FlightPlanConfig,
    VRAGenerator,
    create_spray_flight_plan,
    create_ndvi_prescription,
)
```

---

## License | الترخيص

Proprietary - KAFAAT

---

**Version**: 1.0.0
**Last Updated**: January 2026
