# SAHOOL API Gateway Documentation

<!-- وثائق بوابة واجهة برمجة التطبيقات - SAHOOL API Gateway -->

**Version**: 16.1.0
**Last Updated**: December 30, 2025
**Gateway Technology**: Kong API Gateway (DB-less mode)

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Service Catalog](#service-catalog)
4. [Security Features](#security-features)
5. [Health Monitoring](#health-monitoring)
6. [Rate Limiting](#rate-limiting)
7. [Configuration](#configuration)
8. [Best Practices](#best-practices)

---

## Overview

The SAHOOL platform utilizes **Kong API Gateway** as the central entry point for all microservices. Kong provides a unified interface for managing authentication, rate limiting, load balancing, health monitoring, and traffic routing across 31 microservices.

### Key Features

- **Declarative Configuration**: DB-less mode using `kong.yml`
- **Health Checks**: Active and passive monitoring for all services
- **Rate Limiting**: Tiered rate limits based on service criticality
- **JWT Authentication**: RS256 algorithm with consumer-based access control
- **Load Balancing**: Weighted round-robin with automatic failover
- **Service Discovery**: 31 upstream services with health-based routing

### Architecture Benefits

- Single point of entry for all API requests
- Centralized authentication and authorization
- Automatic service health monitoring and failover
- Request/response transformation and validation
- Traffic management and throttling
- Standardized error handling

---

## Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                             │
│         (Mobile App, Web Dashboard, Admin Portal)                │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Kong API Gateway :8000                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ JWT Auth     │  │ Rate Limiting│  │ Health Check │          │
│  │ RS256        │  │ Tiered Limits│  │ Active/Pass. │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└────────────────────────────┬─────────────────────────────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ▼                   ▼                   ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  Core Services  │  │  AI & Analytics │  │ Communication   │
│  - field-ops    │  │  - ndvi-engine  │  │  - field-chat   │
│  - field-core   │  │  - crop-health  │  │  - ws-gateway   │
│  - task-service │  │  - agro-advisor │  │  - community    │
└─────────────────┘  └─────────────────┘  └─────────────────┘
         │                   │                   │
         └───────────────────┼───────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                  NATS (Event Bus / Message Queue)                │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              PostgreSQL + PostGIS (Geospatial Database)          │
└─────────────────────────────────────────────────────────────────┘
```

### Kong Configuration Model

Kong operates in **declarative (DB-less) mode** using a configuration file (`kong.yml`) that defines:

1. **Upstreams**: Target services with load balancing and health checks
2. **Services**: Logical groupings of upstream targets
3. **Routes**: URL paths that map to services
4. **Consumers**: API clients (web, mobile, internal services)
5. **Plugins**: Rate limiting, authentication, logging, etc.

---

## Service Catalog

### Complete Service Registry (31 Services)

#### Core Services (Field Operations)

| Service             | Port | Routes                                                   | Description                      |
| ------------------- | ---- | -------------------------------------------------------- | -------------------------------- |
| `field-ops`         | 8080 | `/api/v1/fields`, `/api/v1/tasks`, `/api/v1/assignments` | Field & Task Management          |
| `field-core`        | 3000 | `/api/v1/field-core/*`                                   | Core Field Operations            |
| `task-service`      | 8103 | `/api/v1/task/*`                                         | Task Management Service          |
| `equipment-service` | 8101 | `/api/v1/equipment/*`                                    | Equipment & Machinery Management |

#### AI & Analytics Services

| Service             | Port | Routes                                       | Description                       |
| ------------------- | ---- | -------------------------------------------- | --------------------------------- |
| `ndvi-engine`       | 8107 | `/api/v1/ndvi`, `/api/v1/satellite`          | Satellite Imagery & NDVI Analysis |
| `crop-health-ai`    | 8095 | `/api/v1/crop-health/*`                      | AI-Powered Crop Health Detection  |
| `agro-advisor`      | 8105 | `/api/v1/advisor`, `/api/v1/recommendations` | AI Agricultural Recommendations   |
| `yield-engine`      | 8098 | `/api/v1/yield/*`                            | Yield Prediction Engine           |
| `lai-estimation`    | 3022 | `/api/v1/lai/*`                              | Leaf Area Index Estimation        |
| `yield-prediction`  | 3021 | `/api/v1/yield-prediction/*`                 | Advanced Yield Forecasting        |
| `crop-growth-model` | 3023 | `/api/v1/crop-growth/*`                      | Crop Growth Modeling              |

#### Weather & Environmental Services

| Service                 | Port | Routes                                | Description                     |
| ----------------------- | ---- | ------------------------------------- | ------------------------------- |
| `weather-core`          | 8108 | `/api/v1/weather`, `/api/v1/forecast` | Weather Forecasting & Alerts    |
| `weather-advanced`      | 8092 | `/api/v1/weather-advanced/*`          | Advanced Weather Analytics      |
| `astronomical-calendar` | 8111 | `/api/v1/astronomy/*`                 | Agricultural Astronomy Calendar |

#### Communication Services

| Service                | Port | Routes                             | Description                   |
| ---------------------- | ---- | ---------------------------------- | ----------------------------- |
| `field-chat`           | 8099 | `/api/v1/chat`, `/api/v1/messages` | Real-time Team Collaboration  |
| `community-chat`       | 8097 | `/api/v1/community-chat/*`         | Community Discussion Platform |
| `ws-gateway`           | 8081 | `/ws/*`                            | WebSocket Real-time Events    |
| `notification-service` | 8110 | `/api/v1/notifications/*`          | Push Notification Service     |

#### IoT & Sensor Services

| Service              | Port | Routes                                              | Description                              |
| -------------------- | ---- | --------------------------------------------------- | ---------------------------------------- |
| `iot-gateway`        | 8106 | `/api/v1/iot`, `/api/v1/sensors`, `/api/v1/devices` | IoT Sensor Integration & Data Collection |
| `virtual-sensors`    | 8096 | `/api/v1/virtual-sensors/*`                         | Virtual Sensor Management                |
| `satellite-service`  | 8090 | `/api/v1/satellite-service/*`                       | Satellite Data Processing                |
| `indicators-service` | 8091 | `/api/v1/indicators/*`                              | Agricultural Indicators                  |

#### Specialized Services

| Service               | Port | Routes                          | Description                       |
| --------------------- | ---- | ------------------------------- | --------------------------------- |
| `marketplace`         | 3010 | `/api/v1/marketplace/*`         | Agricultural Marketplace          |
| `fertilizer-advisor`  | 8093 | `/api/v1/fertilizer/*`          | Fertilizer Recommendations        |
| `irrigation-smart`    | 8094 | `/api/v1/irrigation/*`          | Smart Irrigation Management       |
| `crop-health`         | 8100 | `/api/v1/crop-health-monitor/*` | Crop Health Monitoring            |
| `community-service`   | 8102 | `/api/v1/community/*`           | Community Management              |
| `provider-config`     | 8104 | `/api/v1/provider-config/*`     | Provider Configuration Service    |
| `billing-core`        | 8089 | `/api/v1/billing/*`             | Billing & Subscription Management |
| `disaster-assessment` | 3020 | `/api/v1/disaster/*`            | Disaster Risk Assessment          |
| `research-core`       | 3015 | `/api/v1/research/*`            | Agricultural Research Core        |

### Service Access Pattern

All services are accessible through Kong at:

```
http://kong:8000/<route-path>
```

Example:

```bash
# Field operations
curl http://kong:8000/api/v1/fields

# NDVI analysis
curl http://kong:8000/api/v1/ndvi/analyze

# Weather forecast
curl http://kong:8000/api/v1/weather/forecast
```

---

## Security Features

### 1. Authentication & Authorization

#### JWT-Based Authentication

- **Algorithm**: RS256 (RSA Signature with SHA-256)
- **Consumer Types**:
  - `sahool-web-app`: Web dashboard client
  - `sahool-mobile-app`: Mobile application client
  - `sahool-internal-service`: Internal service-to-service communication

#### Consumer Configuration

```yaml
consumers:
  - username: sahool-web-app
    custom_id: web-client
    jwt_secrets:
      - key: sahool-web-key
        algorithm: RS256

  - username: sahool-mobile-app
    custom_id: mobile-client
    jwt_secrets:
      - key: sahool-mobile-key
        algorithm: RS256

  - username: sahool-internal-service
    custom_id: internal-service
    jwt_secrets:
      - key: sahool-internal-key
        algorithm: RS256
```

### 2. CORS Security Enhancements (v16.0.1)

**Security Hardening Implemented**:

- ❌ **Removed**: Wildcard CORS (`allow_origins=["*"]`) from all services
- ✅ **Added**: Centralized CORS configuration (`shared/config/cors_config.py`)
- ✅ **Environment-Based Whitelisting**:
  - **Production**: `https://app.sahool.sa`, `https://admin.sahool.sa`
  - **Staging**: `https://staging.sahool.sa`
  - **Development**: `http://localhost:3000`, `http://localhost:5173`

**Affected Services** (CORS hardened):

1. `alert-service`
2. `crop-health-ai`
3. `field-service`
4. `ndvi-processor`

### 3. WebSocket Security

**Enhanced in v16.0.1**:

- ✅ Mandatory authentication (removed `WS_REQUIRE_AUTH` bypass)
- ✅ Comprehensive JWT validation with error logging
- ✅ Production-grade token verification
- ✅ Connection rejection for unauthorized clients

### 4. IoT Gateway Security

**Multi-Layer Security Model**:

1. **Device Authorization**: All devices must be registered and authorized
2. **Sensor Validation**: Range validation for 14 sensor types
3. **Tenant Isolation**: Strict data segregation between tenants
4. **Data Validation**: Pydantic models with field-level validation
5. **Registration Enforcement**: Devices must register before data submission

**Validated Sensor Types**:

- Soil Moisture (0-100%)
- Temperature (-50°C to 70°C)
- Humidity (0-100%)
- pH (0-14)
- Electrical Conductivity
- Nitrogen, Phosphorus, Potassium levels
- Light Intensity, CO2, Pressure
- Wind Speed, Rainfall, Battery Voltage

### 5. Rate Limiting Strategy

Kong implements **tiered rate limiting** based on service criticality and expected load:

#### High-Volume Services (IoT, Real-time)

```yaml
iot-gateway:
  minute: 200
  hour: 10,000

field-chat:
  minute: 120
  hour: 3,000
```

#### Standard Services (Field Operations)

```yaml
field-ops:
  minute: 60
  hour: 2,000

agro-advisor:
  minute: 30
  hour: 500
```

#### Resource-Intensive Services (Satellite, AI)

```yaml
ndvi-engine:
  minute: 30
  hour: 500

crop-health-ai:
  minute: 20
  hour: 200
```

#### Analytics Services

```yaml
weather-core:
  minute: 60
  hour: 1,500
```

---

## Security Improvements (v16.1.0)

### 1. CORS Security Hardening

- **Removed**: Wildcard CORS (`origins: "*"`) - security risk
- **Added**: Explicit origin whitelist for production domains
- **Configuration**:
  - Production: `https://sahool.app`, `https://admin.sahool.app`, `https://api.sahool.app`
  - Development: `http://localhost:3000`, `http://localhost:5173`

### 2. TLS/HTTPS Support

- **Added**: HTTPS listener on port 8443
- **Configuration**: SSL certificates mounted at `/etc/kong/ssl/`
- **Recommendation**: Use Let's Encrypt for production certificates

### 3. Distributed Rate Limiting

- **Changed**: Rate limiting policy from `local` to `redis`
- **Benefit**: Consistent rate limiting across multiple Kong nodes
- **Configuration**: Redis connection via environment variables

### 4. Upstream Health Checks

- **Added**: Health checks for 14 critical services
- **Configuration**: Active checks every 10s, passive failure detection

### 5. JWT RS256 Support

- **Added**: RS256 asymmetric encryption alongside HS256
- **Benefit**: More secure for distributed systems
- **Configuration**: RSA public/private keys via environment variables

### 6. Security Headers

- **Added**: Global security headers via response-transformer plugin:
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY`
  - `X-XSS-Protection: 1; mode=block`
  - `Strict-Transport-Security: max-age=31536000`
  - `Content-Security-Policy`
  - `Referrer-Policy`

### 7. IP Restrictions

- **Added**: IP restrictions for sensitive services:
  - billing-core, iot-gateway, marketplace-service, disaster-assessment, research-core
- **Allowed Subnets**: RFC 1918 private networks only

### 8. Admin API Security

- **Secured**: Admin API bound to localhost only (127.0.0.1:8001)

---

## Health Monitoring

### Standardized Health Checks

All 31 services expose standardized health endpoints:

```
/healthz - Unified health check endpoint
```

**Response Format**:

```json
{
  "status": "healthy",
  "timestamp": "2024-12-24T12:00:00Z",
  "service": "field-ops",
  "version": "16.0.1"
}
```

### Kong Health Check Configuration

#### Active Health Checks

- **Type**: HTTP
- **Path**: `/healthz`
- **Interval**: Every 10 seconds
- **Success Threshold**: 2 consecutive successes
- **Failure Handling**:
  - Check interval: Every 5 seconds
  - Failure threshold: 3 consecutive failures
  - Timeout threshold: 3 consecutive timeouts

#### Passive Health Checks

- **Success Threshold**: 5 successful requests
- **Failure Thresholds**:
  - HTTP failures: 5
  - Timeouts: 3

### Automatic Failover

Kong automatically removes unhealthy upstreams from the load balancing pool:

```yaml
healthchecks:
  active:
    type: http
    http_path: /healthz
    healthy:
      interval: 10
      successes: 2
    unhealthy:
      interval: 5
      http_failures: 3
      timeouts: 3
  passive:
    healthy:
      successes: 5
    unhealthy:
      http_failures: 5
      timeouts: 3
```

---

## Rate Limiting

### Rate Limiting Policies

Kong uses **local** rate limiting policy with per-consumer tracking:

```yaml
plugins:
  - name: rate-limiting
    config:
      minute: <requests_per_minute>
      hour: <requests_per_hour>
      policy: local
```

### Service-Specific Limits

| Service Category        | Requests/Min | Requests/Hour | Rationale                  |
| ----------------------- | ------------ | ------------- | -------------------------- |
| **IoT Data Collection** | 200          | 10,000        | High-frequency sensor data |
| **Real-time Chat**      | 120          | 3,000         | Active messaging           |
| **Field Operations**    | 60           | 2,000         | Standard CRUD operations   |
| **AI/Satellite**        | 20-30        | 200-500       | Computationally expensive  |
| **Weather**             | 60           | 1,500         | Moderate frequency         |

### Bypassing Rate Limits

For internal services requiring higher limits:

1. Use the `sahool-internal-service` consumer
2. Configure custom rate limits per service
3. Implement Redis-based distributed rate limiting (future)

---

## Configuration

### Kong Gateway Environment

```bash
# Kong Gateway Port
KONG_PROXY_PORT=8000
KONG_ADMIN_PORT=8001

# Database Mode
KONG_DATABASE=off  # DB-less mode

# Declarative Configuration
KONG_DECLARATIVE_CONFIG=/etc/kong/kong.yml
```

### Service Timeout Configuration

Different services have different timeout requirements:

```yaml
# Standard Timeouts
connect_timeout: 30000  # 30 seconds
write_timeout: 60000    # 60 seconds
read_timeout: 60000     # 60 seconds

# NDVI/Satellite (longer processing)
write_timeout: 120000   # 120 seconds
read_timeout: 120000    # 120 seconds

# AI Services (computational tasks)
write_timeout: 90000    # 90 seconds
read_timeout: 90000     # 90 seconds
```

### Load Balancing

All upstreams use weighted round-robin load balancing:

```yaml
upstreams:
  - name: field-ops-upstream
    targets:
      - target: sahool-field-ops:8080
        weight: 100 # Default weight
```

**Future Enhancement**: Multi-replica deployments with automatic weight distribution.

---

## Best Practices

### 1. API Versioning

All routes include API version in the path:

```
/api/v1/resource
/api/v2/resource (when available)
```

### 2. Service Naming Convention

- **Upstream**: `{service}-upstream`
- **Service**: `{service}-service`
- **Route**: `{service}-route`
- **Container**: `sahool-{service}`

### 3. Error Handling

Kong automatically returns standard HTTP errors:

- `429 Too Many Requests`: Rate limit exceeded
- `401 Unauthorized`: Missing or invalid JWT
- `503 Service Unavailable`: All upstreams unhealthy
- `504 Gateway Timeout`: Request timeout exceeded

### 4. Monitoring & Observability

- Monitor Kong metrics at `:8001/metrics` (Prometheus format)
- Track health check results in Kong admin API
- Log all gateway errors to centralized logging (future: ELK stack)

### 5. Security Recommendations

- ✅ Always use HTTPS in production (TLS termination at gateway)
- ✅ Rotate JWT signing keys regularly
- ✅ Implement IP whitelisting for admin API
- ✅ Use environment variables for sensitive configuration
- ✅ Enable CORS only for trusted origins

---

## Recent Changes (v16.0.1)

### Security Fixes

1. **CORS Hardening**: Removed wildcard origins, added environment-based whitelisting
2. **WebSocket Auth**: Mandatory authentication for all WS connections
3. **IoT Security**: Device authorization, sensor validation, tenant isolation
4. **Health Checks**: Standardized `/healthz` across all services

### Configuration Updates

1. **Port Fixes**:
   - `ws-gateway`: 8089 → 8081
   - `crop-growth-model`: 3000 → 3023
2. **New Services Added**: 7 services added to Kong configuration
3. **Total Upstreams**: 31 services now managed by Kong

### Documentation

- Added centralized CORS configuration documentation
- Updated service catalog with all 31 services
- Enhanced security section with IoT validation details

---

## Support & Maintenance

### Configuration File Location

```
/home/user/sahool-unified-v15-idp/infra/kong/kong.yml
```

### Applying Configuration Changes

```bash
# Reload Kong with new configuration
docker-compose restart kong

# Validate configuration
docker exec -it kong kong config parse /etc/kong/kong.yml
```

### Health Check Debugging

```bash
# Check Kong admin API
curl http://localhost:8001/status

# View upstream health
curl http://localhost:8001/upstreams

# Check specific service
curl http://localhost:8001/upstreams/{upstream-name}/health
```

---

## Related Documentation

- [Main README](../README.md)
- [CHANGELOG](../CHANGELOG.md)
- [Security Guide](SECURITY.md)
- [Deployment Guide](DEPLOYMENT.md)
- [Operations Guide](OPERATIONS.md)

---

<p align="center">
  <strong>SAHOOL API Gateway v16.0.1</strong><br>
  Last Updated: December 24, 2024<br>
  <sub>31 Microservices | Enterprise Security | Production Ready</sub>
</p>
