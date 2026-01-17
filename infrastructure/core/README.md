# SAHOOL Infrastructure

## Overview

ملفات البنية التحتية للمنصة - تكوينات الخدمات الأساسية.

---

## Structure

```
infra/
├── kong/                   # API Gateway
│   └── kong.yml            # Kong declarative config
│
├── mqtt/                   # IoT Message Broker
│   └── mosquitto.conf      # Mosquitto configuration
│
├── postgres/               # Database
│   ├── init/               # Initialization scripts
│   │   ├── 00-init-sahool.sql
│   │   └── 01-research-expansion.sql
│   └── migrations/         # Schema migrations
│       ├── 001_init_extensions.sql
│       └── 002_base_tables.sql
│
├── qdrant/                 # Vector Database
│   └── docker-compose.qdrant.yml
│
├── vault/                  # Secret Management
│   ├── docker-compose.vault.yml
│   └── README.md
│
└── README.md               # This file
```

---

## Components

### Kong API Gateway

Unified API gateway for all services.

```yaml
# infra/kong/kong.yml
_format_version: "3.0"

services:
  - name: field-service
    url: http://field-service:8080
    routes:
      - name: field-route
        paths: ["/api/v1/fields"]
```

**Features:**

- Request routing
- Rate limiting
- Authentication
- Load balancing

### Mosquitto MQTT Broker

IoT message broker for sensor data.

```conf
# infra/mqtt/mosquitto.conf
listener 1883
allow_anonymous false
password_file /mosquitto/config/password.txt
```

**Ports:**

- 1883: MQTT protocol
- 9001: WebSocket

### PostgreSQL + PostGIS

Primary database with geospatial support.

```sql
-- infra/postgres/init/00-init-sahool.sql
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

**Extensions:**

- `postgis` - Geospatial queries
- `uuid-ossp` - UUID generation
- `pg_trgm` - Text search

**Migrations:**

| File                      | Description        |
| ------------------------- | ------------------ |
| `001_init_extensions.sql` | Install extensions |
| `002_base_tables.sql`     | Core tables        |

### Qdrant Vector Database

Vector database for AI embeddings.

```bash
docker compose -f infra/qdrant/docker-compose.qdrant.yml up -d
```

**Usage:**

- Crop disease image similarity
- Document embeddings
- Semantic search

### HashiCorp Vault

Secret management and encryption.

```bash
docker compose -f infra/vault/docker-compose.vault.yml up -d
```

**Features:**

- Secret storage
- Dynamic credentials
- Encryption as a service
- PKI management

---

## Database Initialization

### First-time Setup

```bash
# 1. Start PostgreSQL
docker compose up -d postgres

# 2. Run init scripts
docker exec -i sahool-postgres psql -U sahool < infra/postgres/init/00-init-sahool.sql

# 3. Run migrations
for f in infra/postgres/migrations/*.sql; do
  docker exec -i sahool-postgres psql -U sahool < "$f"
done
```

### Adding New Migrations

```sql
-- infra/postgres/migrations/003_new_feature.sql
BEGIN;

CREATE TABLE new_table (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  created_at TIMESTAMP DEFAULT NOW()
);

COMMIT;
```

---

## Service Dependencies

```
┌─────────────┐     ┌─────────────┐
│   Kong      │────►│   Services  │
└─────────────┘     └─────────────┘
       │
       ▼
┌─────────────┐     ┌─────────────┐
│  PostgreSQL │◄────│   Services  │
└─────────────┘     └─────────────┘
       │
       ▼
┌─────────────┐     ┌─────────────┐
│   Redis     │◄────│   Services  │
└─────────────┘     └─────────────┘
       │
       ▼
┌─────────────┐     ┌─────────────┐
│   NATS      │◄────│   Services  │
└─────────────┘     └─────────────┘
       │
       ▼
┌─────────────┐     ┌─────────────┐
│  Mosquitto  │◄────│ IoT Devices │
└─────────────┘     └─────────────┘
```

---

## Ports Reference

| Component    | Port | Protocol |
| ------------ | ---- | -------- |
| Kong         | 8000 | HTTP     |
| Kong Admin   | 8001 | HTTP     |
| PostgreSQL   | 5432 | TCP      |
| Redis        | 6379 | TCP      |
| NATS         | 4222 | TCP      |
| NATS Monitor | 8222 | HTTP     |
| MQTT         | 1883 | TCP      |
| MQTT WS      | 9001 | WS       |
| Qdrant       | 6333 | HTTP     |
| Vault        | 8200 | HTTP     |

---

## Related Documentation

- [Docker Guide](../docs/DOCKER.md)
- [Services Map](../docs/SERVICES_MAP.md)
- [Helm Charts](../helm/README.md)

---

<p align="center">
  <sub>SAHOOL Infrastructure v15.5</sub>
  <br>
  <sub>December 2025</sub>
</p>
