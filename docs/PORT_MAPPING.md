# SAHOOL Platform - Port Mapping Reference
## خريطة المنافذ الموحدة لمنصة صهول

This document provides a comprehensive overview of all ports used in the SAHOOL platform, organized by service category and security level.

## Port Security Policy

- **Public Ports**: Accessible from outside (0.0.0.0:port)
- **Internal Ports**: Bound to localhost only (127.0.0.1:port)

---

## Infrastructure Services (المكونات الأساسية)

| Service | Port | Binding | Description |
|---------|------|---------|-------------|
| **PostgreSQL** | 5432 | 127.0.0.1 | PostGIS spatial database |
| **Redis** | 6379 | 127.0.0.1 | In-memory cache and session store |
| **NATS** | 4222 | 127.0.0.1 | Message queue (client connections) |
| **NATS Monitoring** | 8222 | 127.0.0.1 | NATS monitoring interface |
| **MQTT** | 1883 | 127.0.0.1 | IoT device communication |
| **MQTT WebSocket** | 9001 | 127.0.0.1 | MQTT over WebSocket |
| **Qdrant (HTTP)** | 6333 | 127.0.0.1 | Vector database HTTP API |
| **Qdrant (gRPC)** | 6334 | 127.0.0.1 | Vector database gRPC API |

---

## API Gateway (بوابة الواجهة البرمجية)

| Service | Port | Binding | Description |
|---------|------|---------|-------------|
| **Kong Proxy** | 8000 | 0.0.0.0 | **PUBLIC** - Main API Gateway |
| **Kong Admin** | 8001 | 127.0.0.1 | Kong administration API |

---

## Node.js Services (خدمات Node.js)

### Core Services (الخدمات الأساسية)

| Service | Port | Binding | Description |
|---------|------|---------|-------------|
| **Field Management** | 3000 | 127.0.0.1 | Unified field operations service |
| **Marketplace** | 3010 | 127.0.0.1 | Agricultural marketplace & FinTech |
| **Research Core** | 3015 | 127.0.0.1 | Scientific research management |
| **Disaster Assessment** | 3020 | 127.0.0.1 | Disaster impact assessment |

### Deprecated Services (خدمات قديمة - للتوافق المؤقت)

| Service | Port | Binding | Description | Status |
|---------|------|---------|-------------|--------|
| **Yield Prediction** | 3021 | 127.0.0.1 | Yield prediction (old) | ⚠️ Migrating to 8098 |
| **LAI Estimation** | 3022 | 127.0.0.1 | LAI estimation (old) | ⚠️ Migrating to 8090 |
| **Crop Growth Model** | 3023 | 127.0.0.1 | Crop growth simulation (old) | ⚠️ Migrating to 8095 |

### Communication Services (خدمات التواصل)

| Service | Port | Binding | Description |
|---------|------|---------|-------------|
| **Chat Service** | 8114 | 127.0.0.1 | Real-time chat & messaging |
| **IoT Service** | 8117 | 127.0.0.1 | IoT device & sensor management |
| **Community Chat** | 8097 | 127.0.0.1 | Community discussions (deprecated) |

---

## Python Services (خدمات Python)

### Core Python Services (الخدمات الأساسية)

| Service | Port | Binding | Description |
|---------|------|---------|-------------|
| **Field Ops** | 8080 | 127.0.0.1 | Field operations (deprecated) |
| **WebSocket Gateway** | 8081 | 127.0.0.1 | Real-time WebSocket connections |
| **Billing Core** | 8089 | 127.0.0.1 | Payment & billing service |
| **Field Chat** | 8099 | 127.0.0.1 | Field-specific chat |

### Data & Intelligence Services (خدمات البيانات والذكاء)

| Service | Port | Binding | Description |
|---------|------|---------|-------------|
| **Vegetation Analysis** | 8090 | 127.0.0.1 | Unified satellite & vegetation analysis |
| **Indicators** | 8091 | 127.0.0.1 | Agricultural indicators service |
| **Weather Service** | 8092 | 127.0.0.1 | Unified weather operations |
| **Advisory Service** | 8093 | 127.0.0.1 | Unified agricultural advisory |
| **Irrigation Smart** | 8094 | 127.0.0.1 | Smart irrigation recommendations |
| **Crop Intelligence** | 8095 | 127.0.0.1 | Unified crop analysis & AI |
| **Virtual Sensors** | 8096 | 127.0.0.1 | Virtual sensor estimation |
| **Yield Prediction** | 8098 | 127.0.0.1 | Unified yield prediction service |

### Deprecated Analysis Services (خدمات قديمة)

| Service | Port | Binding | Description | Status |
|---------|------|---------|-------------|--------|
| **Crop Health** | 8100 | 127.0.0.1 | Crop health (old) | ⚠️ Migrated to 8095 |
| **NDVI Engine** | 8107 | 127.0.0.1 | NDVI processing (old) | ⚠️ Migrated to 8090 |
| **Weather Core** | 8108 | 127.0.0.1 | Weather core (old) | ⚠️ Migrated to 8092 |
| **Agro Advisor** | 8105 | 127.0.0.1 | Advisory (old) | ⚠️ Migrated to 8093 |
| **NDVI Processor** | 8118 | 127.0.0.1 | NDVI processor (old) | ⚠️ Migrated to 8090 |
| **Field Service** | 8115 | 127.0.0.1 | Field service (old) | ⚠️ Migrated to 3000 |

### Support Services (خدمات الدعم)

| Service | Port | Binding | Description |
|---------|------|---------|-------------|
| **Equipment Service** | 8101 | 127.0.0.1 | Farm equipment management |
| **Task Service** | 8103 | 127.0.0.1 | Task scheduling & tracking |
| **Provider Config** | 8104 | 127.0.0.1 | Service provider configuration |
| **IoT Gateway** | 8106 | 127.0.0.1 | IoT device gateway |
| **Notification** | 8110 | 127.0.0.1 | Email/SMS/Push notifications |
| **Astronomical Calendar** | 8111 | 127.0.0.1 | Islamic & agricultural calendar |
| **AI Advisor** | 8112 | 127.0.0.1 | AI-powered agricultural advisor |
| **Alert Service** | 8113 | 127.0.0.1 | Real-time alert management |
| **Inventory** | 8116 | 127.0.0.1 | Inventory & stock management |

### Integration Services (خدمات التكامل)

| Service | Port | Binding | Description |
|---------|------|---------|-------------|
| **MCP Server** | 8200 | 127.0.0.1 | Model Context Protocol integration |

---

## Port Range Summary (ملخص نطاقات المنافذ)

| Range | Purpose | Example Services |
|-------|---------|------------------|
| **1883, 4222** | Messaging protocols | MQTT, NATS |
| **3000-3099** | Node.js services | Field Management, Marketplace, Research |
| **5432** | Database | PostgreSQL |
| **6333-6379** | Data stores | Qdrant, Redis |
| **8000-8001** | API Gateway | Kong Proxy, Kong Admin |
| **8080-8200** | Python services | All Python microservices |
| **9001** | WebSocket | MQTT WebSocket |

---

## Service Access Matrix (مصفوفة الوصول للخدمات)

### Public Access (الوصول العام)
- **Kong API Gateway** (8000) - Main entry point for all API requests

### Internal-Only Access (الوصول الداخلي فقط)
- All infrastructure services (PostgreSQL, Redis, NATS, MQTT, Qdrant)
- All microservices (Node.js and Python services)
- Kong Admin interface
- MCP Server

---

## Security Notes (ملاحظات أمنية)

1. **Port Binding Strategy**:
   - Infrastructure services: `127.0.0.1` (localhost only)
   - Microservices: `127.0.0.1` (internal access via Kong)
   - API Gateway (Kong): `0.0.0.0:8000` (public), `127.0.0.1:8001` (admin)

2. **Network Isolation**:
   - All services run on `sahool-network` bridge network
   - No direct external access except through Kong Gateway (port 8000)

3. **Service Discovery**:
   - Services communicate using container names (e.g., `postgres:5432`)
   - Docker internal DNS resolves service names

4. **Production Recommendations**:
   - Use reverse proxy (nginx/Apache) in front of Kong
   - Enable SSL/TLS for Kong proxy (port 8000)
   - Use firewall rules to restrict access to Kong admin (8001)
   - Consider VPN for administrative access

---

## Migration Guide (دليل الترحيل)

### Deprecated Services → New Services

| Old Service | Old Port | New Service | New Port | Status |
|-------------|----------|-------------|----------|--------|
| Field Service | 8115 | Field Management | 3000 | ✅ Active |
| Field Ops | 8080 | Field Management | 3000 | ⚠️ Compatibility |
| Satellite Service | N/A | Vegetation Analysis | 8090 | ✅ Consolidated |
| NDVI Engine | 8107 | Vegetation Analysis | 8090 | ⚠️ Compatibility |
| NDVI Processor | 8118 | Vegetation Analysis | 8090 | ⚠️ Compatibility |
| LAI Estimation | 3022 | Vegetation Analysis | 8090 | ⚠️ Compatibility |
| Weather Core | 8108 | Weather Service | 8092 | ⚠️ Compatibility |
| Weather Advanced | N/A | Weather Service | 8092 | ✅ Consolidated |
| Agro Advisor | 8105 | Advisory Service | 8093 | ⚠️ Compatibility |
| Fertilizer Advisor | N/A | Advisory Service | 8093 | ✅ Consolidated |
| Crop Health | 8100 | Crop Intelligence | 8095 | ⚠️ Compatibility |
| Crop Health AI | N/A | Crop Intelligence | 8095 | ✅ Consolidated |
| Crop Growth Model | 3023 | Crop Intelligence | 8095 | ⚠️ Compatibility |
| Yield Engine | N/A | Yield Prediction | 8098 | ✅ Consolidated |
| Yield Prediction | 3021 | Yield Prediction | 8098 | ⚠️ Compatibility |

**Status Legend**:
- ✅ Active: New consolidated service is primary
- ⚠️ Compatibility: Old service maintained for backwards compatibility only

---

## Configuration Files (ملفات التكوين)

Port configuration is managed in:
- `docker-compose.yml` - Main deployment configuration
- `.env.example` - Environment variable template
- `config/base.env` - Base configuration
- `infrastructure/gateway/kong/kong.yml` - Kong routing configuration

---

**Last Updated**: 2025-12-28
**Version**: v16.0.0
