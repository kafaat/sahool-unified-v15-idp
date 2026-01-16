# SAHOOL Configuration

## Overview

ملفات تكوين المنصة - تحتوي على إعدادات البيئات المختلفة وسجل الخدمات.

---

## Files

```
config/
├── base.env              # Default values for all environments
├── local.env             # Local development overrides
├── ci.env                # CI/CD environment settings
├── prod.env              # Production environment settings
├── service-registry.yaml # Service classification and registry
└── README.md             # This file
```

---

## Environment Files

### base.env (Base Configuration)

Base configuration that all environments inherit from:

```env
# Core
ENVIRONMENT=development
LOG_LEVEL=INFO

# Database
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_USER=sahool
POSTGRES_DB=sahool

# Message Queue
NATS_HOST=nats
NATS_PORT=4222

# Cache
REDIS_HOST=redis
REDIS_PORT=6379

# IoT
MQTT_HOST=mqtt
MQTT_PORT=1883

# JWT
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
JWT_REFRESH_TOKEN_EXPIRE_DAYS=30
```

### local.env (Development)

Local development settings:

| Setting                           | Value       | Notes               |
| --------------------------------- | ----------- | ------------------- |
| `ENVIRONMENT`                     | development |                     |
| `LOG_LEVEL`                       | DEBUG       | Verbose logging     |
| `*_HOST`                          | localhost   | All services local  |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | 1440        | 24h for convenience |
| `MFA_ENABLED`                     | false       | Disabled for dev    |
| `SAHOOL_AUTH_ENABLED`             | false       | Bypass auth         |

### ci.env (CI/CD)

CI/CD pipeline settings:

| Setting                 | Value   | Notes      |
| ----------------------- | ------- | ---------- |
| `ENVIRONMENT`           | ci      |            |
| `LOG_LEVEL`             | WARNING | Less noise |
| Test-specific overrides |         |            |

### prod.env (Production)

Production security settings:

| Setting                           | Value      | Notes       |
| --------------------------------- | ---------- | ----------- |
| `ENVIRONMENT`                     | production |             |
| `LOG_LEVEL`                       | INFO       |             |
| `MFA_ENABLED`                     | true       | Required    |
| `SAHOOL_AUTH_ENABLED`             | true       | Required    |
| `MAX_LOGIN_ATTEMPTS`              | 3          | Stricter    |
| `LOCKOUT_DURATION_MINUTES`        | 60         |             |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | 30         | Short lived |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS`   | 7          |             |

---

## Service Registry

`service-registry.yaml` defines service classification according to Field-First Architecture:

### Service Layers

```yaml
layers:
  field-critical: # Priority 1 - Never stops
    - field-service
    - billing-core
    - astronomical-calendar
    - notification-service

  bridge: # Priority 2 - Transform & Route
    - indicators-service
    - yield-engine
    - irrigation-smart
    - fertilizer-advisor

  analysis: # Priority 3 - Can be delayed
    - satellite-service
    - crop-health-ai
    - weather-advanced
```

### Usage

```python
import yaml

with open('config/service-registry.yaml') as f:
    registry = yaml.safe_load(f)

# Get all field-critical services
critical = registry['services']['field-critical']
```

---

## Environment Variable Categories

### Database

```env
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_USER=sahool
POSTGRES_PASSWORD=changeme
POSTGRES_DB=sahool
DATABASE_URL=postgresql://...
```

### Message Queue (NATS)

```env
NATS_HOST=nats
NATS_PORT=4222
NATS_URL=nats://nats:4222
```

### Cache (Redis)

```env
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=changeme
REDIS_URL=redis://:password@host:port
```

### IoT (MQTT)

```env
MQTT_HOST=mqtt
MQTT_PORT=1883
MQTT_WS_PORT=9001
```

### Authentication

```env
JWT_SECRET_KEY=changeme_at_least_32_characters_long
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
JWT_REFRESH_TOKEN_EXPIRE_DAYS=30
JWT_AUDIENCE=sahool-api
JWT_ISSUER=sahool-platform
```

### Security

```env
APP_SECRET_KEY=changeme_at_least_32_characters_long
SAHOOL_AUTH_ENABLED=true
MFA_ENABLED=false
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION_MINUTES=30
```

### CORS

```env
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
```

### Service Ports

```env
API_GATEWAY_PORT=8000
FIELD_CORE_PORT=3000
WEB_APP_PORT=3001
ADMIN_APP_PORT=3002
AUTH_SERVICE_PORT=8001
USER_SERVICE_PORT=8002
TENANT_SERVICE_PORT=8003
GEO_SERVICE_PORT=8005
```

### External Services (Optional)

```env
SENTRY_DSN=
GOOGLE_CLOUD_PROJECT=
AWS_REGION=
```

---

## Loading Configuration

### Python Services

```python
from dotenv import load_dotenv

# Load base first, then environment-specific
load_dotenv('config/base.env')
load_dotenv(f'config/{ENVIRONMENT}.env', override=True)
```

### Docker Compose

```yaml
services:
  my-service:
    env_file:
      - config/base.env
      - config/${ENVIRONMENT:-local}.env
```

---

## Security Notes

1. **Never commit secrets** - Use `.env.local` or CI/CD secrets
2. **Change defaults** - All `changeme` values must be replaced
3. **Use secret management** - Vault, AWS Secrets Manager, etc.
4. **Rotate regularly** - Especially JWT secrets and API keys

---

## Related Documentation

- [Docker Guide](../docs/DOCKER.md)
- [Services Map](../docs/SERVICES_MAP.md)
- [Architecture Principles](../docs/architecture/PRINCIPLES.md)

---

<p align="center">
  <sub>SAHOOL Configuration v15.5</sub>
  <br>
  <sub>December 2025</sub>
</p>
