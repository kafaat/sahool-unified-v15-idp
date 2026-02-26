# Kernel | النواة

Core backend modules for the SAHOOL platform. The kernel provides shared analytics, database, middleware, queue, and monitoring infrastructure used by all Python microservices.

## Structure

```
apps/kernel/
├── analytics/          # User & platform analytics
│   ├── models.py       # Analytics data models
│   └── user_analytics.py # User behavior tracking
├── common/             # Shared infrastructure
│   ├── database/       # Database connection, migrations, pooling
│   ├── middleware/      # HTTP middleware (auth, logging, rate limiting)
│   ├── monitoring/     # Prometheus metrics & health checks
│   ├── queue/          # NATS message queue integration
│   └── docs/           # Internal documentation
├── field_ops/          # Field operations logic
│   ├── models/         # Domain models (fields, crops, irrigation)
│   ├── services/       # Business logic services
│   └── data/           # Reference data (crop calendars, boundaries)
└── requirements.txt    # Python dependencies
```

## Modules

### Analytics (`analytics/`)

User behavior tracking and platform usage analytics. Provides models and utilities for recording user actions, session data, and generating usage reports.

### Common (`common/`)

Shared infrastructure components:

- **Database**: Connection pooling (asyncpg), migration management, query helpers
- **Middleware**: Authentication, request logging, rate limiting, CORS
- **Monitoring**: Prometheus metrics collection, health check endpoints
- **Queue**: NATS JetStream integration for event publishing/subscribing

### Field Operations (`field_ops/`)

Core field management logic including:

- **Boundary Validation**: Field geometry validation using PostGIS/Shapely
- **Crop Calendar**: Planting/harvest timing based on region and crop type
- **Irrigation Management**: Scheduling and optimization

See `field_ops/README.md` for detailed documentation.

## Usage

```python
# Database connection
from apps.kernel.common.database import get_db_pool

# Middleware setup
from apps.kernel.common.middleware import setup_middleware

# Queue integration
from apps.kernel.common.queue import get_nats_connection

# Analytics
from apps.kernel.analytics import UserAnalytics
```

## Testing

```bash
# Run kernel tests
pytest apps/kernel/ -v

# Run field_ops tests
pytest apps/kernel/field_ops/ -v
```
