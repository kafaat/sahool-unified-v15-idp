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
| `/api/v1/flights/plan/spray` | POST | Create spray flight plan (boundary, spray_rate_l_ha, swath_width_m, altitude_m) |
| `/api/v1/flights/plan/mapping` | POST | Create mapping flight plan (boundary, gsd_cm_px, frontal_overlap, side_overlap) |
| `/api/v1/flights/weather-check` | POST | Check weather conditions for flight safety |
| `/api/v1/flights/estimate` | POST | Estimate flight resources (area_ha, spray_rate_l_ha, tank_capacity_l) |
| `/api/v1/flights/plans` | GET | List flight plans (optional field_id filter) |
| `/api/v1/flights/plans/{plan_id}` | GET | Get flight plan details |

### Missions

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/missions` | GET | List missions |
| `/api/v1/missions` | POST | Create mission |
| `/api/v1/missions/{mission_id}` | GET | Get mission details |
| `/api/v1/missions/{mission_id}/start` | POST | Start mission execution |
| `/api/v1/missions/{mission_id}/pause` | POST | Pause mission |
| `/api/v1/missions/{mission_id}/resume` | POST | Resume mission |
| `/api/v1/missions/{mission_id}/abort` | POST | Abort mission |

### VRA (Variable Rate Application)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/vra/prescription/ndvi` | POST | Create NDVI-based prescription map |
| `/api/v1/vra/prescription/spot-spray` | POST | Create spot spray map from detection points |
| `/api/v1/vra/prescriptions` | GET | List prescription maps (optional field_id filter) |
| `/api/v1/vra/prescriptions/{prescription_id}` | GET | Get prescription map details |

### Planned Endpoints (Not Yet Implemented)

The following endpoints are planned for future releases:

- **Flight Logs**: `/api/v1/logs/*` - Flight log management and analytics
- **Imagery**: `/api/v1/imagery/*` - Aerial imagery processing
- **Perimeter Flights**: `/api/v1/flights/plan/perimeter`
- **Mission Export**: `/api/v1/missions/{mission_id}/export`
- **VRA Export**: `/api/v1/vra/{id}/export` - Export prescription (Shapefile/GeoJSON)

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
    Coordinate,
    create_spray_flight_plan,
    create_mapping_flight_plan,
    assess_flight_weather,
    estimate_flight_resources,
)
```

---

## License | الترخيص

Proprietary - KAFAAT

---

**Version**: 16.0.0
**Last Updated**: February 2026
