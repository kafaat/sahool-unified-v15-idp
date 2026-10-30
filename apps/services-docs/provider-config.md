# Provider Configuration Service Analysis

**Service Name:** provider-config
**Service Name (Arabic):** خدمة إدارة المزودين
**Port:** 8104
**Type:** Python/FastAPI
**Version:** 16.0.0
**Layer:** Business
**Category:** Core
**Status:** Active

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [API Endpoints](#api-endpoints)
4. [Request/Response Schemas](#requestresponse-schemas)
5. [NATS Events](#nats-events)
6. [Provider Management](#provider-management)
7. [Database Schema](#database-schema)
8. [Dependencies](#dependencies)
9. [Environment Variables](#environment-variables)
10. [Bugs and Issues](#bugs-and-issues)
11. [Recommended Fixes](#recommended-fixes)

---

## Overview

The Provider Configuration Service manages external service providers for the SAHOOL platform. It handles configuration and health checking for:

- **Map Providers**: OpenStreetMap, Google Maps, Mapbox, ESRI
- **Weather Providers**: Open-Meteo, OpenWeatherMap, WeatherAPI, Visual Crossing
- **Satellite Providers**: Sentinel Hub, Planet Labs, Landsat, Maxar, Google Earth Engine, Copernicus
- **Payment Providers**: Stripe, PayPal, Moyasar, HyperPay, Tap, PayFort, Telr, Tharwatt
- **SMS Providers**: Twilio, Vonage, Unifonic, Yamamah
- **Notification Providers**: Firebase FCM, OneSignal, Pusher

### Key Features

- Tenant-based configuration management
- Provider health checking
- Priority-based failover chains
- Smart provider selection by country/currency
- Provider recommendations based on budget
- Configuration version history and rollback
- Redis caching for configuration data

---

## Architecture

### File Structure

```
apps/services/provider-config/
├── Dockerfile
├── README.md
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── main.py              # FastAPI application & endpoints
│   ├── models.py            # SQLAlchemy database models
│   ├── database_service.py  # Database & cache service layer
│   └── db_init.sql          # Database initialization script
└── tests/
    ├── __init__.py
    └── test_providers.py    # Unit tests
```

### Data Flow

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Client    │────>│  Kong API    │────>│  Provider   │
│  (Web/App)  │     │   Gateway    │     │   Config    │
└─────────────┘     └──────────────┘     │   Service   │
                                          └──────┬──────┘
                                                 │
                    ┌────────────────────────────┼────────────────────────────┐
                    │                            │                            │
                    v                            v                            v
              ┌──────────┐               ┌──────────────┐             ┌──────────┐
              │  Redis   │               │  PostgreSQL  │             │ External │
              │  Cache   │               │  (PgBouncer) │             │ Providers│
              └──────────┘               └──────────────┘             └──────────┘
```

### Kong Gateway Configuration

```yaml
- name: provider-config
  host: provider-config
  port: 8104
  protocol: http
  routes:
    - name: provider-config-route
      paths: ["/api/v1/provider-config", "/provider-config"]
      strip_path: true
      protocols: ["http", "https"]
```

---

## API Endpoints

### Health & Status Endpoints

| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| GET | `/` | Service information | None |
| GET | `/healthz` | Liveness probe | None |
| GET | `/readyz` | Readiness probe | None |

### Provider Listing Endpoints

| Method | Endpoint | Description | Response |
|--------|----------|-------------|----------|
| GET | `/providers` | List all providers | `ProvidersListResponse` |
| GET | `/providers/maps` | List map providers | Map providers with free list |
| GET | `/providers/weather` | List weather providers | Weather providers with free list |
| GET | `/providers/satellite` | List satellite providers | Satellite providers with free list |
| GET | `/providers/payment` | List payment providers | Payment providers by country |
| GET | `/providers/sms` | List SMS providers | SMS providers by region |
| GET | `/providers/notification` | List notification providers | Notification providers |

### Smart Provider Selection

| Method | Endpoint | Description | Parameters |
|--------|----------|-------------|------------|
| GET | `/providers/select/{provider_type}` | Smart provider selection | `country`, `currency`, `fallback` |
| GET | `/providers/failover-chain/{provider_type}` | Get failover chain | `country` |
| GET | `/providers/recommend` | Get recommendations | `use_case`, `budget`, `offline_required` |

### Provider Health Checks

| Method | Endpoint | Description | Request Body |
|--------|----------|-------------|--------------|
| POST | `/providers/check` | Check specific provider health | `HealthCheckRequest` |
| GET | `/providers/check/all` | Check all free providers | None |

### Tenant Configuration

| Method | Endpoint | Description | Request/Response |
|--------|----------|-------------|------------------|
| GET | `/config/{tenant_id}` | Get tenant configuration | Tenant config or defaults |
| POST | `/config/{tenant_id}` | Update tenant configuration | `TenantProviderConfig` |
| DELETE | `/config/{tenant_id}` | Reset to defaults | Success response |
| GET | `/config/{tenant_id}/history` | Get config history | History list |
| POST | `/config/{tenant_id}/rollback` | Rollback to version | `config_id`, `version` |

---

## Request/Response Schemas

### Enums

#### ProviderType

```python
class ProviderType(str, Enum):
    MAP = "map"
    WEATHER = "weather"
    SATELLITE = "satellite"
    NOTIFICATION = "notification"
    PAYMENT = "payment"
    SMS = "sms"
```

#### ProviderPriority

```python
class ProviderPriority(str, Enum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    TERTIARY = "tertiary"
    DISABLED = "disabled"
```

#### ProviderStatus

```python
class ProviderStatus(str, Enum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    RATE_LIMITED = "rate_limited"
    ERROR = "error"
    CHECKING = "checking"
```

### Request Models

#### HealthCheckRequest

```json
{
  "provider_type": "map",
  "provider_name": "openstreetmap",
  "api_key": "optional_api_key"
}
```

#### ProviderConfig

```json
{
  "provider_name": "mapbox_streets",
  "api_key": "pk.xxx",
  "priority": "primary",
  "enabled": true
}
```

#### TenantProviderConfig

```json
{
  "tenant_id": "tenant_001",
  "map_providers": [
    {
      "provider_name": "openstreetmap",
      "priority": "primary",
      "enabled": true
    }
  ],
  "weather_providers": [],
  "satellite_providers": []
}
```

### Response Models

#### Service Root Response

```json
{
  "service": "SAHOOL Provider Configuration Service",
  "service_ar": "خدمة إدارة المزودين - سهول",
  "version": "1.0.0",
  "description": "Manage external service providers (Maps, Weather, Satellite)"
}
```

#### ProviderStatusResponse

```json
{
  "provider_name": "openstreetmap",
  "status": "available",
  "last_check": "2026-01-25T10:30:00Z",
  "response_time_ms": 145.5,
  "error_message": null
}
```

#### ProvidersListResponse

```json
{
  "map_providers": [
    {
      "id": "openstreetmap",
      "type": "map",
      "name": "OpenStreetMap",
      "name_ar": "خريطة الشارع المفتوحة",
      "url_template": "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
      "requires_api_key": false,
      "max_zoom": 19,
      "attribution": "© OpenStreetMap contributors",
      "supports_offline": true,
      "cost_per_1k_requests": 0
    }
  ],
  "weather_providers": [...],
  "satellite_providers": [...]
}
```

#### Tenant Config Response

```json
{
  "tenant_id": "tenant_001",
  "map_providers": [
    {
      "id": "uuid",
      "tenant_id": "tenant_001",
      "provider_type": "map",
      "provider_name": "openstreetmap",
      "priority": "primary",
      "enabled": true,
      "config_data": {},
      "has_api_key": false,
      "created_at": "2026-01-25T10:00:00Z",
      "updated_at": "2026-01-25T10:00:00Z",
      "version": 1
    }
  ],
  "weather_providers": [],
  "satellite_providers": [],
  "payment_providers": [],
  "sms_providers": [],
  "notification_providers": [],
  "is_default": false
}
```

#### Smart Selection Response

```json
{
  "provider_type": "payment",
  "country": "YE",
  "currency": "YER",
  "selected": [
    {
      "id": "tharwatt",
      "name": "Tharwatt",
      "name_ar": "ثروات",
      "transaction_fee_percent": 1.5
    }
  ],
  "fallback_providers": [...]
}
```

#### Failover Chain Response

```json
{
  "provider_type": "payment",
  "country": "YE",
  "failover_chain": [
    {
      "order": 1,
      "provider_id": "tharwatt",
      "name": "Tharwatt",
      "name_ar": "ثروات",
      "priority": "primary",
      "fee_percent": 1.5
    }
  ],
  "total_providers": 3
}
```

#### Recommendations Response

```json
{
  "use_case": "agricultural",
  "budget": "free",
  "offline_required": true,
  "map": [
    {
      "provider": "openstreetmap",
      "reason": "Free, supports offline",
      "reason_ar": "مجاني، يدعم الاستخدام غير المتصل"
    }
  ],
  "weather": [
    {
      "provider": "open_meteo",
      "reason": "Free, 16-day forecast",
      "reason_ar": "مجاني، 16 يوم توقعات"
    }
  ],
  "satellite": []
}
```

---

## NATS Events

### Declared Events (governance/services.yaml)

According to the service registry, this service should produce:

| Event | Version | Status |
|-------|---------|--------|
| `ProviderConfigUpdated` | v1 | **NOT IMPLEMENTED** |

### Current Implementation

**WARNING:** The service currently does NOT publish any NATS events despite:
1. Having NATS_URL as environment variable in docker-compose
2. Being declared to produce `ProviderConfigUpdated.v1` in governance/services.yaml

### Expected Event Schema (Recommended)

```json
// sahool.{tenant_id}.provider_config.updated
{
  "event_type": "ProviderConfigUpdated",
  "version": "v1",
  "timestamp": "2026-01-25T10:30:00Z",
  "tenant_id": "tenant_001",
  "data": {
    "config_id": "uuid",
    "provider_type": "map",
    "provider_name": "mapbox_streets",
    "action": "created|updated|deleted|enabled|disabled",
    "priority": "primary",
    "enabled": true,
    "changed_by": "user_id"
  }
}
```

---

## Provider Management

### Supported Providers

#### Map Providers (10 providers)

| Provider | API Key Required | Cost/1K | Offline | Max Zoom | Default Priority |
|----------|------------------|---------|---------|----------|------------------|
| OpenStreetMap | No | Free | Yes | 19 | Primary |
| Google Maps | Yes | $7.00 | No | 21 | Secondary |
| Google Satellite | Yes | $7.00 | No | 21 | Secondary |
| Google Hybrid | Yes | $7.00 | No | 21 | Tertiary |
| Mapbox Streets | Yes | $0.50 | Yes | 22 | Secondary |
| Mapbox Satellite | Yes | $0.50 | Yes | 22 | Secondary |
| Mapbox Hybrid | Yes | $0.50 | Yes | 22 | Tertiary |
| ESRI Satellite | No | Free | Yes | 19 | Tertiary |
| ESRI Streets | No | Free | Yes | 18 | Tertiary |
| OpenTopoMap | No | Free | Yes | 17 | Tertiary |

#### Weather Providers (4 providers)

| Provider | API Key Required | Forecast Days | Historical | Alerts | Rate Limit |
|----------|------------------|---------------|------------|--------|------------|
| Open-Meteo | No | 16 | Yes | No | 10000/min |
| OpenWeatherMap | Yes | 8 | No | Yes | 60/min |
| WeatherAPI | Yes | 14 | Yes | Yes | 100/min |
| Visual Crossing | Yes | 15 | Yes | Yes | 1000/min |

#### Satellite Providers (6 providers)

| Provider | API Key Required | Resolution | Revisit Days | Cost/km2 | Indices |
|----------|------------------|------------|--------------|----------|---------|
| Sentinel Hub | Yes | 10m | 5 | $0.001 | NDVI, NDWI, EVI, SAVI, NDMI, LAI |
| Planet Labs | Yes | 3m | 1 | $0.10 | NDVI, NDWI, EVI, GNDVI |
| Maxar | Yes | 0.3m | 3 | $15.00 | NDVI |
| Landsat (USGS) | No | 30m | 16 | Free | NDVI, NDWI, EVI, SAVI |
| Google Earth Engine | Yes | 10m | 5 | Free | NDVI, NDWI, EVI, SAVI, LAI, FAPAR |
| Copernicus | Yes | 10m | 5 | Free | NDVI, NDWI, EVI, SAVI |

#### Payment Providers (8 providers)

| Provider | Countries | Currencies | Mada Support | Fee % | Payout Days |
|----------|-----------|------------|--------------|-------|-------------|
| Stripe | Global | USD, EUR, SAR, AED, YER | No | 2.9% + $0.30 | 2 |
| PayPal | Global | USD, EUR, SAR, AED | No | 3.49% + $0.49 | 1 |
| Moyasar | SA | SAR | Yes | 2.0% | 2 |
| HyperPay | GCC + YE | SAR, AED, BHD, KWD, OMR, QAR, YER | Yes | 2.5% | 3 |
| Tap | MENA | SAR, AED, BHD, KWD, OMR, QAR, EGP, JOD | Yes | 2.75% | 2 |
| PayFort | MENA | AED, SAR, EGP, JOD, LBP | Yes | 2.8% | 3 |
| Telr | GCC | AED, SAR, BHD, KWD, OMR, QAR | No | 2.85% | 3 |
| Tharwatt | YE | YER | No | 1.5% | 1 |

#### SMS Providers (4 providers)

| Provider | Coverage | Arabic Sender | Cost/SMS | Delivery Reports |
|----------|----------|---------------|----------|------------------|
| Twilio | Global | No | $0.0075 | Yes |
| Vonage | Global | No | $0.0068 | Yes |
| Unifonic | Middle East | Yes | $0.035 | Yes |
| Yamamah | SA, YE | Yes | $0.03 | Yes |

#### Notification Providers (3 providers)

| Provider | Android | iOS | Web | Cost/1K |
|----------|---------|-----|-----|---------|
| Firebase FCM | Yes | Yes | Yes | Free |
| OneSignal | Yes | Yes | Yes | Free (10K/month) |
| Pusher Beams | Yes | Yes | Yes | $0.02 |

---

## Database Schema

### Tables

#### provider_configs

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | UUID | No | Primary key |
| tenant_id | VARCHAR(255) | No | Tenant identifier |
| provider_type | VARCHAR(50) | No | map, weather, satellite, payment, sms, notification |
| provider_name | VARCHAR(100) | No | Provider identifier |
| api_key | TEXT | Yes | API key (should be encrypted) |
| api_secret | TEXT | Yes | API secret (should be encrypted) |
| priority | VARCHAR(20) | No | primary, secondary, tertiary |
| enabled | BOOLEAN | No | Is provider enabled |
| config_data | JSONB | Yes | Additional settings |
| created_at | TIMESTAMP | No | Creation timestamp |
| updated_at | TIMESTAMP | No | Last update timestamp |
| created_by | VARCHAR(255) | Yes | Creator user ID |
| updated_by | VARCHAR(255) | Yes | Last modifier user ID |
| version | INTEGER | No | Version number |

**Indexes:**
- `idx_tenant_provider_type` (tenant_id, provider_type)
- `idx_tenant_provider_name` (tenant_id, provider_name)
- `idx_tenant_type_enabled` (tenant_id, provider_type, enabled)
- `idx_tenant_type_priority` (tenant_id, provider_type, priority)

**Constraints:**
- UNIQUE (tenant_id, provider_type, provider_name)

#### config_versions

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | UUID | No | Primary key |
| config_id | UUID | No | Reference to provider_configs |
| tenant_id | VARCHAR(255) | No | Tenant identifier (denormalized) |
| provider_type | VARCHAR(50) | No | Provider type snapshot |
| provider_name | VARCHAR(100) | No | Provider name snapshot |
| api_key | TEXT | Yes | API key snapshot |
| api_secret | TEXT | Yes | API secret snapshot |
| priority | VARCHAR(20) | No | Priority snapshot |
| enabled | BOOLEAN | No | Enabled snapshot |
| config_data | JSONB | Yes | Config data snapshot |
| version | INTEGER | No | Version number |
| change_type | VARCHAR(20) | No | created, updated, deleted, enabled, disabled |
| changed_at | TIMESTAMP | No | Change timestamp |
| changed_by | VARCHAR(255) | Yes | User who made the change |
| change_reason | TEXT | Yes | Reason for change |

**Indexes:**
- `idx_config_version` (config_id, version)
- `idx_tenant_changed_at` (tenant_id, changed_at)
- `idx_tenant_provider_changed` (tenant_id, provider_type, changed_at)

### Database Triggers

1. **update_provider_configs_updated_at**: Auto-updates `updated_at` and increments `version` on UPDATE
2. **trigger_config_version_insert**: Creates version history on INSERT
3. **trigger_config_version_update**: Creates version history on UPDATE
4. **trigger_config_version_delete**: Creates version history on DELETE

---

## Dependencies

### Python Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| fastapi | 0.126.0 | Web framework |
| starlette | >=0.49.1 | ASGI framework |
| uvicorn[standard] | >=0.30.0,<1.0.0 | ASGI server |
| pydantic | 2.9.2 | Data validation |
| httpx | 0.28.1 | HTTP client for health checks |
| python-dotenv | 1.0.1 | Environment variables |
| python-multipart | 0.0.18 | Form data handling |
| sqlalchemy | 2.0.23 | ORM |
| psycopg2-binary | 2.9.9 | PostgreSQL driver |
| alembic | 1.13.1 | Database migrations |
| redis | 5.0.1 | Caching |
| structlog | >=24.1.0 | Structured logging |

### Internal Dependencies

| Module | Path | Purpose |
|--------|------|---------|
| shared.errors_py | shared/errors_py | Unified error handling |
| shared.cors_config | shared/cors_config | CORS configuration |

### Infrastructure Dependencies

| Service | Purpose | Required |
|---------|---------|----------|
| PostgreSQL (via PgBouncer) | Data storage | Yes |
| Redis | Configuration caching | Yes (graceful degradation) |
| NATS | Event publishing | No (declared but not implemented) |

---

## Environment Variables

### Required Variables

| Variable | Default | Description |
|----------|---------|-------------|
| PORT | 8104 | Service port |
| DATABASE_URL | postgresql://pgbouncer:6432/sahool | PostgreSQL connection URL |
| REDIS_URL | redis://redis:6379/0 | Redis connection URL |

### Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| LOG_LEVEL | INFO | Logging level |
| CORS_ORIGINS | https://sahool.io,https://admin.sahool.io,http://localhost:3000 | Allowed CORS origins |
| NATS_URL | nats://nats:4222 | NATS connection URL (currently unused) |

### Missing Environment Variables

The following environment variables are mentioned in documentation or expected but not implemented:

| Variable | Purpose | Status |
|----------|---------|--------|
| GOOGLE_MAPS_API_KEY | Google Maps API key for health checks | Not implemented |
| MAPBOX_ACCESS_TOKEN | Mapbox API key for health checks | Not implemented |
| OPENWEATHERMAP_API_KEY | OpenWeatherMap API key | Not implemented |
| SENTINEL_HUB_CLIENT_ID | Sentinel Hub OAuth | Not implemented |
| SENTINEL_HUB_CLIENT_SECRET | Sentinel Hub OAuth | Not implemented |
| JWT_SECRET_KEY | Authentication | Not implemented |
| ENCRYPTION_KEY | API key encryption | Not implemented |

---

## Bugs and Issues

### Critical Issues

#### 1. Missing NATS Event Publishing

**Location:** `src/main.py`
**Severity:** High
**Description:** The service is declared to produce `ProviderConfigUpdated.v1` events in governance/services.yaml but no NATS client or event publishing code exists.

```python
# NATS_URL is provided in docker-compose but never used
# No nats-py or similar library in requirements.txt
# No event publishing on config create/update/delete
```

#### 2. Test File References Non-Existent Endpoint

**Location:** `tests/test_providers.py:42-44`
**Severity:** Medium
**Description:** Test expects `/health` endpoint but service implements `/healthz`

```python
# Test code (WRONG):
def test_health_check(self, client):
    response = client.get("/health")  # Should be /healthz
```

#### 3. API Keys Stored in Plain Text

**Location:** `src/models.py:59-60`
**Severity:** High
**Description:** API keys are stored unencrypted in the database. Comments indicate encryption should be used but it's not implemented.

```python
api_key = Column(Text, nullable=True)  # Encrypted in production - NOT IMPLEMENTED
api_secret = Column(Text, nullable=True)  # Encrypted in production - NOT IMPLEMENTED
```

### Medium Issues

#### 4. Cache Returns Dict When Model Expected

**Location:** `src/database_service.py:179-181`
**Severity:** Medium
**Description:** `get_tenant_configs` returns cached dict data directly when cache hit, but callers expect ProviderConfig objects.

```python
cached = self.cache.get(tenant_id, provider_type)
if cached:
    return cached  # Returns dict, not ProviderConfig list
```

#### 5. Missing Authentication on Tenant Endpoints

**Location:** `src/main.py:1203-1373`
**Severity:** Medium
**Description:** Tenant configuration endpoints have no authentication. Any caller can read/modify any tenant's configuration.

```python
@app.get("/config/{tenant_id}")
async def get_tenant_config(tenant_id: str, session: Session = Depends(get_db_session)):
    # No authentication check - any tenant_id can be accessed
```

#### 6. Version Field Not Updated in update_config

**Location:** `src/database_service.py:233-278`
**Severity:** Low
**Description:** The `update_config` method doesn't explicitly increment the version field. It relies on database trigger, but SQLAlchemy might not refresh this properly.

#### 7. Missing Metrics Endpoint

**Location:** `src/main.py`
**Severity:** Low
**Description:** No `/metrics` endpoint for Prometheus monitoring, though other SAHOOL services provide this.

### Low Issues

#### 8. Deprecated Event Handler Syntax

**Location:** `src/main.py:672-711`
**Severity:** Low
**Description:** Uses deprecated `@app.on_event("startup")` instead of lifespan context manager.

```python
# Current (deprecated):
@app.on_event("startup")
async def startup_event():

# Should be:
@asynccontextmanager
async def lifespan(app: FastAPI):
```

#### 9. Hardcoded Default Database URL

**Location:** `src/main.py:679`
**Severity:** Low
**Description:** Default DATABASE_URL doesn't include credentials, could cause connection failures.

```python
database_url = os.getenv("DATABASE_URL", "postgresql://pgbouncer:6432/sahool")
# Missing user:password in default
```

#### 10. Test Provider Enum Mismatch

**Location:** `tests/test_providers.py:347-349`
**Severity:** Low
**Description:** Test for satellite providers is incomplete, missing `google_earth_engine` and `copernicus`.

```python
valid_ids = ["sentinel_hub", "planet_labs", "maxar", "landsat"]
# Missing: "google_earth_engine", "copernicus"
```

---

## Recommended Fixes

### High Priority

#### 1. Implement NATS Event Publishing

```python
# Add to requirements.txt
nats-py>=2.6.0

# Add to main.py
import nats
from nats.aio.client import Client as NATSClient

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ... existing code ...

    # NATS connection
    nats_url = os.getenv("NATS_URL")
    if nats_url:
        app.state.nc = await nats.connect(nats_url)

    yield

    if hasattr(app.state, "nc") and app.state.nc:
        await app.state.nc.close()

async def publish_config_event(nc: NATSClient, tenant_id: str, event_data: dict):
    subject = f"sahool.{tenant_id}.provider_config.updated"
    await nc.publish(subject, json.dumps(event_data).encode())
```

#### 2. Implement API Key Encryption

```python
# Add to requirements.txt
cryptography>=41.0.0

# Add encryption utilities
from cryptography.fernet import Fernet

ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
cipher = Fernet(ENCRYPTION_KEY.encode()) if ENCRYPTION_KEY else None

def encrypt_api_key(api_key: str) -> str:
    if cipher and api_key:
        return cipher.encrypt(api_key.encode()).decode()
    return api_key

def decrypt_api_key(encrypted_key: str) -> str:
    if cipher and encrypted_key:
        return cipher.decrypt(encrypted_key.encode()).decode()
    return encrypted_key
```

#### 3. Add Authentication

```python
from shared.auth.dependencies import get_current_user, get_tenant_id
from shared.auth.models import User

@app.get("/config/{tenant_id}")
async def get_tenant_config(
    tenant_id: str,
    session: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
    user_tenant: str = Depends(get_tenant_id)
):
    # Verify user has access to this tenant
    if user_tenant != tenant_id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Access denied")
    # ... existing code
```

### Medium Priority

#### 4. Fix Cache Return Type

```python
def get_tenant_configs(
    self, session: Session, tenant_id: str, provider_type: str | None = None
) -> list[ProviderConfig]:
    # Check cache first
    cached = self.cache.get(tenant_id, provider_type)
    if cached:
        # Convert cached dicts back to model objects for type consistency
        # OR return early indicator that cache was hit
        pass  # Consider returning a CacheHit wrapper or reconstructing models

    # Query database
    # ... existing code
```

#### 5. Fix Test Health Endpoint

```python
# In tests/test_providers.py
def test_health_check(self, client):
    response = client.get("/healthz")  # Fixed
    assert response.status_code == 200
```

#### 6. Add Metrics Endpoint

```python
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response

PROVIDER_CHECKS = Counter('provider_health_checks_total', 'Total provider health checks', ['provider_type', 'provider_name', 'status'])
CHECK_DURATION = Histogram('provider_health_check_duration_seconds', 'Health check duration')

@app.get("/metrics")
async def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
```

### Low Priority

#### 7. Migrate to Lifespan Context Manager

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global database, cache_manager, config_service
    # ... initialization code ...

    yield

    # Shutdown
    if cache_manager and cache_manager.redis_client:
        cache_manager.redis_client.close()

app = FastAPI(
    title="SAHOOL Provider Configuration Service",
    lifespan=lifespan
)
```

#### 8. Fix Test Satellite Provider List

```python
def test_all_satellite_provider_ids_valid(self, client):
    valid_ids = [
        "sentinel_hub",
        "planet_labs",
        "maxar",
        "landsat",
        "google_earth_engine",
        "copernicus"
    ]
```

---

## Service Dependencies Graph

```
                    ┌─────────────────┐
                    │  Kong Gateway   │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ provider-config │
                    │    (8104)       │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│   PgBouncer   │   │    Redis      │   │     NATS      │
│    (6432)     │   │    (6379)     │   │    (4222)     │
└───────────────┘   └───────────────┘   └───────────────┘
        │                                        │
        ▼                                        │
┌───────────────┐                                │
│  PostgreSQL   │                     (Not connected)
│    (5432)     │
└───────────────┘
```

---

## Related Services

| Service | Relationship | Events |
|---------|--------------|--------|
| field-management-service | Consumer - uses map provider config | Subscribes to config changes |
| weather-service | Consumer - uses weather provider config | Subscribes to config changes |
| vegetation-analysis-service | Consumer - uses satellite provider config | Subscribes to config changes |
| billing-core | Consumer - uses payment provider config | Subscribes to config changes |
| notification-service | Consumer - uses notification/SMS provider config | Subscribes to config changes |

---

## API Documentation Links

- **OpenAPI Spec:** `http://localhost:8104/docs`
- **ReDoc:** `http://localhost:8104/redoc`
- **Kong Route:** `http://kong:8000/api/v1/provider-config`

---

*Generated: 2026-01-25*
*Service Version: 16.0.0*
*Analysis Tool: Claude Code*
