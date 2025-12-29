# SAHOOL Port Reference - Quick Card
## بطاقة مرجعية سريعة للمنافذ

**Last Updated**: 2025-12-28 | **Version**: v16.0.0

---

## 🌐 Public Access (الوصول العام)

| Port | Service | URL | Description |
|------|---------|-----|-------------|
| **8000** | **Kong API Gateway** | `http://localhost:8000` | **Main API entry point** |

> ⚠️ **All API requests MUST go through Kong Gateway on port 8000**

---

## 🔒 Infrastructure (Internal Only)

| Port | Service | Connection String |
|------|---------|-------------------|
| 5432 | PostgreSQL | `postgres:5432` or `127.0.0.1:5432` |
| 6379 | Redis | `redis:6379` or `127.0.0.1:6379` |
| 4222 | NATS | `nats:4222` or `127.0.0.1:4222` |
| 1883 | MQTT | `mqtt:1883` or `127.0.0.1:1883` |
| 6333 | Qdrant | `qdrant:6333` or `127.0.0.1:6333` |

---

## 🟢 Node.js Services (Range: 3000-3099)

| Port | Service | Internal URL |
|------|---------|--------------|
| 3000 | Field Management | `http://field-management-service:3000` |
| 3010 | Marketplace | `http://marketplace_service:3010` |
| 3015 | Research Core | `http://research_core:3015` |
| 3020 | Disaster Assessment | `http://disaster_assessment:3020` |
| 8114 | Chat Service | `http://chat_service:8114` |
| 8117 | IoT Service | `http://iot_service:8117` |

---

## 🐍 Python Services (Range: 8080-8200)

### Core Services
| Port | Service | Internal URL |
|------|---------|--------------|
| 8081 | WebSocket Gateway | `http://ws_gateway:8081` |
| 8089 | Billing Core | `http://billing_core:8089` |

### Data & Intelligence
| Port | Service | Internal URL | Type |
|------|---------|--------------|------|
| 8090 | Vegetation Analysis | `http://vegetation-analysis-service:8090` | ✓ Consolidated |
| 8091 | Indicators | `http://indicators_service:8091` | - |
| 8092 | Weather Service | `http://weather-service:8092` | ✓ Consolidated |
| 8093 | Advisory Service | `http://advisory-service:8093` | ✓ Consolidated |
| 8094 | Irrigation Smart | `http://irrigation_smart:8094` | - |
| 8095 | Crop Intelligence | `http://crop-intelligence-service:8095` | ✓ Consolidated |
| 8096 | Virtual Sensors | `http://virtual_sensors:8096` | - |
| 8098 | Yield Prediction | `http://yield-prediction-service:8098` | ✓ Consolidated |

### Support Services
| Port | Service | Internal URL |
|------|---------|--------------|
| 8101 | Equipment | `http://equipment_service:8101` |
| 8103 | Task Service | `http://task_service:8103` |
| 8104 | Provider Config | `http://provider_config:8104` |
| 8106 | IoT Gateway | `http://iot_gateway:8106` |
| 8110 | Notification | `http://notification_service:8110` |
| 8111 | Astronomical Calendar | `http://astronomical_calendar:8111` |
| 8112 | AI Advisor | `http://ai_advisor:8112` |
| 8113 | Alert Service | `http://alert_service:8113` |
| 8116 | Inventory | `http://inventory_service:8116` |

### Integration
| Port | Service | Internal URL |
|------|---------|--------------|
| 8200 | MCP Server | `http://mcp-server:8200` |

---

## 📡 Service Communication Examples

### From External Client
```bash
# ✅ Correct - Via Kong Gateway
curl http://localhost:8000/api/v1/fields

# ❌ Wrong - Direct service access will fail from outside
curl http://localhost:3000/api/v1/fields
```

### From Inside Docker Network
```javascript
// Node.js service calling Weather Service
const weatherUrl = 'http://weather-service:8092/api/v1/weather';
const response = await fetch(weatherUrl);
```

```python
# Python service calling Vegetation Analysis
import requests
veg_url = "http://vegetation-analysis-service:8090/api/v1/ndvi"
response = requests.get(veg_url)
```

### Database Connection
```javascript
// Node.js TypeORM configuration
const config = {
  type: 'postgres',
  host: 'postgres',  // or 'localhost' if running outside Docker
  port: 5432,
  database: process.env.POSTGRES_DB,
  username: process.env.POSTGRES_USER,
  password: process.env.POSTGRES_PASSWORD
};
```

```python
# Python SQLAlchemy connection
DATABASE_URL = "postgresql://sahool:password@postgres:5432/sahool"
# or from localhost: "postgresql://sahool:password@127.0.0.1:5432/sahool"
```

---

## 🔧 Local Development

### Access Services Locally

```bash
# Access Kong Gateway (Public)
curl http://localhost:8000/api/v1/health

# Access Kong Admin (Localhost only)
curl http://localhost:8001/

# Access PostgreSQL (Localhost only)
psql -h localhost -p 5432 -U sahool -d sahool

# Access Redis (Localhost only)
redis-cli -h localhost -p 6379

# Access Qdrant (Localhost only)
curl http://localhost:6333/collections
```

### SSH Tunnel for Remote Access

```bash
# If you need to access services from a remote machine
ssh -L 3000:localhost:3000 user@server  # Field Management
ssh -L 8090:localhost:8090 user@server  # Vegetation Analysis
ssh -L 8112:localhost:8112 user@server  # AI Advisor
```

---

## 🚀 Quick Start Commands

### Start All Services
```bash
docker-compose up -d
```

### Check Service Health
```bash
# Via Kong
curl http://localhost:8000/api/v1/health

# Direct service check (from host)
curl http://localhost:3000/healthz           # Field Management
curl http://localhost:8090/healthz           # Vegetation Analysis
curl http://localhost:8092/healthz           # Weather Service
```

### View Service Logs
```bash
docker-compose logs -f field-management-service
docker-compose logs -f vegetation-analysis-service
docker-compose logs -f weather-service
```

---

## ⚠️ Deprecated Services (Backwards Compatibility Only)

| Old Port | Old Service | New Port | New Service | Status |
|----------|-------------|----------|-------------|--------|
| 8080 | Field Ops | 3000 | Field Management | ⚠️ Will be removed |
| 8107 | NDVI Engine | 8090 | Vegetation Analysis | ⚠️ Will be removed |
| 8108 | Weather Core | 8092 | Weather Service | ⚠️ Will be removed |
| 8105 | Agro Advisor | 8093 | Advisory Service | ⚠️ Will be removed |
| 8100 | Crop Health | 8095 | Crop Intelligence | ⚠️ Will be removed |
| 3021 | Yield Prediction | 8098 | Yield Prediction | ⚠️ Will be removed |
| 3022 | LAI Estimation | 8090 | Vegetation Analysis | ⚠️ Will be removed |
| 3023 | Crop Growth Model | 8095 | Crop Intelligence | ⚠️ Will be removed |

> **Migration Timeline**: Q1 2026

---

## 🔐 Security Best Practices

1. **Always use Kong Gateway** (port 8000) for external API access
2. **Never expose service ports** directly to the internet
3. **Use environment variables** for sensitive configuration
4. **Enable SSL/TLS** on Kong proxy in production
5. **Restrict Kong Admin** (8001) to trusted networks only
6. **Use strong passwords** for database, Redis, MQTT

---

## 📚 Additional Resources

- **Full Port Mapping**: `docs/PORT_MAPPING.md`
- **Network Architecture**: `docs/NETWORK_ARCHITECTURE.md`
- **Change Summary**: `docs/PORT_UNIFICATION_SUMMARY.md`
- **Docker Compose**: `docker-compose.yml`
- **Environment Template**: `.env.example`

---

## 🆘 Troubleshooting

### "Connection Refused" Errors

```bash
# Check if service is running
docker-compose ps

# Check service logs
docker-compose logs service-name

# Check port binding
docker-compose port service-name 8000
```

### "Cannot access service from outside"

```bash
# ✅ Use Kong Gateway
curl http://localhost:8000/api/v1/endpoint

# ❌ Don't try to access service directly
# This will fail: curl http://localhost:3000/api/v1/endpoint
```

### "Service cannot connect to database"

```bash
# From inside Docker network, use service name
DATABASE_URL=postgresql://user:pass@postgres:5432/db

# From host machine, use localhost
DATABASE_URL=postgresql://user:pass@localhost:5432/db
```

---

**Print this card and keep it handy! احفظ هذه البطاقة للرجوع إليها!**

---

**Version**: v16.0.0  
**Last Updated**: 2025-12-28  
**Author**: SAHOOL Platform Team
