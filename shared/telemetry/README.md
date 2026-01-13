# OpenTelemetry Distributed Tracing for SAHOOL Platform

## Overview

This directory contains comprehensive OpenTelemetry distributed tracing, metrics, and logging instrumentation for the SAHOOL agricultural platform. It provides end-to-end observability across all 44+ microservices.

## Features

### 🔍 Distributed Tracing

- **OpenTelemetry SDK** integration for Python (FastAPI) and TypeScript (NestJS)
- **Jaeger** as the tracing backend
- **Auto-instrumentation** for HTTP, database, cache, and message queue operations
- **Context propagation** across service boundaries
- **Custom span** creation and attribute tagging

### 📊 Metrics Collection

- **Prometheus** metrics for all services
- **OpenTelemetry Metrics API** integration
- **Business metrics** tracking (fields created, satellite requests, AI recommendations)
- **Automatic HTTP metrics** (request count, latency, error rate)
- **Custom counters, histograms, and gauges**

### 📝 Structured Logging

- **JSON logging** with trace ID correlation
- **Automatic trace context** injection (trace_id, span_id)
- **Log level** configuration from environment
- **Arabic language** support in log messages

### 📈 Visualization

- **Grafana** dashboards for traces and metrics
- **Jaeger UI** for trace exploration
- **Service dependency** visualization
- **Real-time monitoring**

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    SAHOOL Services (44+)                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ Field    │  │ Weather  │  │Satellite │  │  AI/ML   │  ...  │
│  │ Services │  │ Services │  │ Services │  │ Services │       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
│       │             │              │             │              │
│       └─────────────┴──────────────┴─────────────┘              │
│                          │                                       │
│              OpenTelemetry SDK (Python/TS)                      │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
              ┌─────────────────────────┐
              │  OpenTelemetry Collector │
              │   - Receives traces      │
              │   - Processes data       │
              │   - Exports to backends  │
              └───────────┬──────────────┘
                          │
         ┌────────────────┼────────────────┐
         ▼                ▼                ▼
    ┌────────┐      ┌──────────┐    ┌──────────┐
    │ Jaeger │      │Prometheus│    │  Logs    │
    │Tracing │      │ Metrics  │    │  (JSON)  │
    └───┬────┘      └────┬─────┘    └──────────┘
        │                │
        └────────────────┘
                 │
                 ▼
          ┌────────────┐
          │  Grafana   │
          │ Dashboards │
          └────────────┘
```

## Quick Start

### 1. Start the Telemetry Stack

```bash
# Start Jaeger, OpenTelemetry Collector, Prometheus, and Grafana
docker-compose -f docker-compose.telemetry.yml up -d
```

### 2. Configure Environment Variables

Copy and update the `.env` file with telemetry configuration:

```bash
# OpenTelemetry Configuration
OTEL_ENABLED=true
OTEL_SERVICE_NAME=your-service-name
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
OTEL_TRACES_SAMPLER_ARG=0.1

# Prometheus
PROMETHEUS_METRICS_ENABLED=true
PROMETHEUS_PORT=9090

# Logging
LOG_FORMAT=json
LOG_INCLUDE_TRACE=true
```

### 3. Python (FastAPI) Integration

```python
from fastapi import FastAPI
from shared.telemetry import init_tracer, init_metrics, setup_logging, instrument_all

# Initialize at application startup
app = FastAPI()

# Setup observability
setup_logging(service_name="field_core", log_level="INFO")
init_tracer(service_name="field_core")
init_metrics(service_name="field_core")

# Auto-instrument FastAPI, SQLAlchemy, Redis, etc.
instrument_all(app=app, db_engine=engine)

# Use decorator for custom tracing
from shared.telemetry import trace_method

@trace_method(name="process_field")
async def process_field(field_id: str):
    # Your code here
    pass

# Track business metrics
from shared.telemetry import SahoolMetrics

SahoolMetrics.track_field_created(user_id="123", field_type="agricultural")
```

### 4. TypeScript (NestJS) Integration

```typescript
// main.ts
import { initTracer, initMetrics } from "./shared/telemetry/tracing";
import { NestFactory } from "@nestjs/core";

async function bootstrap() {
  // Initialize tracing
  initTracer({ serviceName: "chat-service" });

  // Initialize metrics
  initMetrics({ serviceName: "chat-service" });

  const app = await NestFactory.create(AppModule);
  await app.listen(3000);
}
bootstrap();

// Use decorator for tracing
import { Trace } from "./shared/telemetry/tracing";

@Injectable()
export class ChatService {
  @Trace("sendMessage")
  async sendMessage(userId: string, message: string) {
    // Your code here
  }
}

// Track business metrics
import { SahoolMetrics } from "./shared/telemetry/metrics";

SahoolMetrics.trackMessageSent("field-chat", "text", userId);
```

## Access UIs

Once the telemetry stack is running:

- **Jaeger UI**: http://localhost:16686
  - Explore distributed traces
  - View service dependencies
  - Analyze latency issues

- **Prometheus**: http://localhost:9090
  - Query metrics
  - View targets
  - Test PromQL queries

- **Grafana**: http://localhost:3002
  - Username: `admin`
  - Password: (from `GRAFANA_ADMIN_PASSWORD` in `.env`)
  - View pre-configured dashboards
  - Create custom visualizations

- **OpenTelemetry Collector**: http://localhost:13133
  - Health check endpoint
  - Metrics about collector itself

## Service Names

All 44+ SAHOOL services are instrumented with standardized service names:

### Core Services

- `field_core` - Field Core Service
- `field_ops` - Field Operations Service
- `field_service` - Field Management Service

### Weather Services

- `weather_core` - Weather Core Service
- `weather_advanced` - Advanced Weather Service

### Satellite & Imagery

- `satellite_service` - Satellite Imagery Service
- `ndvi_engine` - NDVI Calculation Engine
- `ndvi_processor` - NDVI Processor Service

### AI/ML Services

- `crop_health_ai` - Crop Health AI Service
- `crop_health` - Crop Health Monitoring
- `yield_engine` - Yield Calculation Engine
- `yield_prediction` - Yield Prediction Service
- `lai_estimation` - Leaf Area Index Estimation
- `crop_growth_model` - Crop Growth Model Service

### Advisory Services

- `ai_advisor` - AI Agricultural Advisor
- `agro_advisor` - Agronomy Advisor Service
- `fertilizer_advisor` - Fertilizer Recommendation
- `irrigation_smart` - Smart Irrigation Service
- `agro_rules` - Agronomy Rules Engine

### IoT & Sensors

- `iot_gateway` - IoT Gateway Service
- `iot_service` - IoT Management Service
- `virtual_sensors` - Virtual Sensors Service

### Analytics

- `indicators_service` - Agricultural Indicators
- `astronomical_calendar` - Astronomical Calendar
- `disaster_assessment` - Disaster Assessment

### Communication

- `notification_service` - Notification Service
- `alert_service` - Alert Management Service
- `chat_service` - Chat Service
- `community_chat` - Community Chat Service
- `field_chat` - Field Chat Service

### Business Services

- `billing_core` - Billing Core Service
- `marketplace_service` - Marketplace Service
- `inventory_service` - Inventory Management
- `equipment_service` - Equipment Management
- `task_service` - Task Management Service
- `research_core` - Research Core Service

### Infrastructure

- `ws_gateway` - WebSocket Gateway
- `kong` - API Gateway

## Business Metrics

### Python (SahoolMetrics)

```python
from shared.telemetry import SahoolMetrics

# Track field creation
SahoolMetrics.track_field_created(user_id="123", field_type="agricultural")

# Track satellite imagery request
SahoolMetrics.track_satellite_request(
    provider="sentinel",
    status="success",
    duration=2.5
)

# Track weather query
SahoolMetrics.track_weather_query(
    provider="openweathermap",
    location="yemen",
    status="success"
)

# Track NDVI calculation
SahoolMetrics.track_ndvi_calculation(field_id="field-123", duration=1.2)

# Track AI recommendation
SahoolMetrics.track_ai_recommendation(
    advisor_type="fertilizer",
    crop_type="wheat",
    duration=0.8
)

# Track IoT sensor reading
SahoolMetrics.track_iot_reading(
    sensor_type="soil_moisture",
    field_id="field-123",
    value=45.5
)

# Track notification
SahoolMetrics.track_notification_sent(
    notification_type="alert",
    channel="sms",
    status="delivered"
)

# Track irrigation event
SahoolMetrics.track_irrigation_event(
    field_id="field-123",
    event_type="automatic",
    water_amount=1000.0
)
```

### TypeScript (SahoolMetrics)

```typescript
import { SahoolMetrics } from "./shared/telemetry/metrics";

// Track chat message
SahoolMetrics.trackMessageSent("field-chat", "text", userId);

// Track notification
SahoolMetrics.trackNotificationSent("push", "mobile", "delivered");

// Track WebSocket connection
SahoolMetrics.trackWebSocketConnection("connect");

// Track billing transaction
SahoolMetrics.trackBillingTransaction("subscription", 99.99, "completed");

// Track marketplace listing
SahoolMetrics.trackMarketplaceListing("equipment", "create");

// Track inventory operation
SahoolMetrics.trackInventoryOperation("add", "fertilizer", 100);
```

## Trace Context Propagation

Traces automatically propagate across service boundaries using W3C Trace Context:

```
Client Request
    │
    ├─> Field Service (span: handle_request)
    │       │
    │       ├─> Weather Service (span: get_forecast)
    │       │       │
    │       │       └─> External API (span: fetch_weather)
    │       │
    │       └─> Satellite Service (span: get_ndvi)
    │               │
    │               └─> NDVI Engine (span: calculate_ndvi)
    │
    └─> Response
```

All spans share the same `trace_id` for end-to-end correlation.

## Logging with Trace Correlation

Logs automatically include trace context:

```json
{
  "timestamp": "2025-12-26T10:30:45.123Z",
  "level": "INFO",
  "logger": "field_core.service",
  "message": "Processing field data",
  "service": {
    "name": "field_core",
    "version": "1.0.0",
    "environment": "production"
  },
  "trace": {
    "trace_id": "0af7651916cd43dd8448eb211c80319c",
    "span_id": "b7ad6b7169203331",
    "trace_flags": 1
  },
  "field_id": "field-123",
  "user_id": "user-456"
}
```

Use the `trace_id` to find all logs related to a specific request across all services.

## Sampling Configuration

Control which traces are collected to manage volume and costs:

```bash
# Sample 100% of traces (development)
OTEL_TRACES_SAMPLER=always_on

# Sample 10% of traces (production)
OTEL_TRACES_SAMPLER=parentbased_traceidratio
OTEL_TRACES_SAMPLER_ARG=0.1

# Sample 1% of traces (high-traffic production)
OTEL_TRACES_SAMPLER=parentbased_traceidratio
OTEL_TRACES_SAMPLER_ARG=0.01

# Never sample (disable tracing)
OTEL_TRACES_SAMPLER=always_off
```

**Note**: The collector also applies tail sampling to always capture:

- All error traces (4xx, 5xx)
- Slow requests (>1 second)
- 10% of normal traffic

## Performance Considerations

### Overhead

- **Tracing**: ~1-5ms per traced operation
- **Metrics**: Negligible (<1ms)
- **Logging**: ~0.5-2ms per log statement

### Optimization

1. **Use sampling** in production (10% recommended)
2. **Batch exports** reduce network overhead
3. **Exclude health checks** from tracing
4. **Use async exporters** to avoid blocking
5. **Set memory limits** on collectors

## Troubleshooting

### No traces in Jaeger

1. Check OpenTelemetry Collector logs:

   ```bash
   docker logs sahool-telemetry-otel-collector
   ```

2. Verify service is sending traces:

   ```bash
   # Python
   OTEL_CONSOLE_EXPORT=true python app.py

   # TypeScript
   OTEL_CONSOLE_EXPORT=true npm start
   ```

3. Check firewall/network connectivity:
   ```bash
   curl http://otel-collector:4317
   ```

### Metrics not showing in Prometheus

1. Check Prometheus targets:
   - Go to http://localhost:9090/targets
   - Verify all services are "UP"

2. Check service metrics endpoint:

   ```bash
   curl http://field_core:9090/metrics
   ```

3. Verify Prometheus configuration:
   ```bash
   docker exec sahool-telemetry-prometheus cat /etc/prometheus/prometheus.yml
   ```

### High memory usage

1. Reduce trace sampling:

   ```bash
   OTEL_TRACES_SAMPLER_ARG=0.01  # 1% instead of 10%
   ```

2. Increase collector memory limit:

   ```yaml
   # docker-compose.telemetry.yml
   deploy:
     resources:
       limits:
         memory: 2G # Increase from 1G
   ```

3. Reduce retention period:
   ```bash
   # Prometheus
   --storage.tsdb.retention.time=15d  # Instead of 30d
   ```

## File Structure

```
shared/telemetry/
├── __init__.py                          # Python package initialization
├── tracing.py                           # Python tracing instrumentation
├── metrics.py                           # Python metrics collection
├── logging.py                           # Structured logging
├── tracing.ts                           # TypeScript tracing instrumentation
├── metrics.ts                           # TypeScript metrics collection
├── otel-collector-config.yaml           # OpenTelemetry Collector configuration
├── prometheus.yml                       # Prometheus scrape configuration
├── grafana/
│   ├── provisioning/
│   │   ├── datasources/
│   │   │   └── datasources.yml          # Grafana datasource configuration
│   │   └── dashboards/
│   │       └── dashboards.yml           # Dashboard provisioning
│   └── dashboards/                      # Pre-built Grafana dashboards
└── README.md                            # This file
```

## Docker Compose Services

The `docker-compose.telemetry.yml` includes:

| Service            | Port  | Description           |
| ------------------ | ----- | --------------------- |
| **jaeger**         | 16686 | Jaeger UI             |
|                    | 14268 | Jaeger Collector HTTP |
|                    | 4317  | OTLP gRPC             |
|                    | 4318  | OTLP HTTP             |
| **otel-collector** | 4317  | OTLP gRPC receiver    |
|                    | 4318  | OTLP HTTP receiver    |
|                    | 8889  | Prometheus exporter   |
|                    | 13133 | Health check          |
| **prometheus**     | 9090  | Prometheus UI & API   |
| **grafana**        | 3002  | Grafana UI            |

## Dependencies

### Python

```bash
pip install opentelemetry-api \
            opentelemetry-sdk \
            opentelemetry-instrumentation-fastapi \
            opentelemetry-instrumentation-httpx \
            opentelemetry-instrumentation-sqlalchemy \
            opentelemetry-instrumentation-redis \
            opentelemetry-instrumentation-psycopg2 \
            opentelemetry-exporter-otlp-proto-grpc \
            opentelemetry-exporter-prometheus \
            prometheus-client
```

### TypeScript/NestJS

```bash
npm install @opentelemetry/sdk-node \
            @opentelemetry/auto-instrumentations-node \
            @opentelemetry/instrumentation-nestjs-core \
            @opentelemetry/instrumentation-http \
            @opentelemetry/exporter-trace-otlp-grpc \
            @prisma/instrumentation \
            prom-client
```

## Best Practices

1. **Always set service name** - Use meaningful, unique names for each service
2. **Use semantic attributes** - Follow OpenTelemetry semantic conventions
3. **Avoid high cardinality** - Don't use user IDs or UUIDs as metric labels
4. **Sample in production** - Use 1-10% sampling to reduce overhead
5. **Monitor collector health** - Set up alerts for collector failures
6. **Correlate logs and traces** - Always include trace_id in logs
7. **Tag spans with business context** - Add custom attributes (field_id, crop_type, etc.)
8. **Create custom dashboards** - Build service-specific Grafana dashboards
9. **Set up alerts** - Configure Prometheus alerts for critical metrics
10. **Regular cleanup** - Archive or delete old traces/metrics

## Security Considerations

1. **Enable TLS** in production:

   ```yaml
   # otel-collector-config.yaml
   exporters:
     otlp/jaeger:
       endpoint: jaeger:4317
       tls:
         insecure: false # Enable TLS
         cert_file: /certs/cert.pem
         key_file: /certs/key.pem
   ```

2. **Secure Grafana**:
   - Change default admin password
   - Enable HTTPS
   - Set up SSO/LDAP authentication

3. **Protect sensitive data**:
   - Don't log passwords, API keys, or PII
   - Use attribute filtering in collector
   - Sanitize trace attributes

4. **Network isolation**:
   - Use internal Docker networks
   - Restrict external access to UIs
   - Use firewall rules

## Support

For issues or questions:

- Check the [OpenTelemetry documentation](https://opentelemetry.io/docs/)
- Review [Jaeger documentation](https://www.jaegertracing.io/docs/)
- Consult [Prometheus documentation](https://prometheus.io/docs/)
- Contact the SAHOOL Platform Team

## License

Copyright © 2025 SAHOOL Platform Team. All rights reserved.
