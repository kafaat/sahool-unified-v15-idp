# SAHOOL Unified v15 (IDP) 🌾

> **The National Agricultural Intelligence Platform**
> _From Field Data to AI-Driven Decisions._

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)]()
[![Architecture](https://img.shields.io/badge/architecture-microservices-blue)]()
[![Platform](https://img.shields.io/badge/platform-mobile%20%7C%20web-orange)]()
[![Version](https://img.shields.io/badge/version-16.0.0-green)]()

---

## 📌 Executive Summary

SAHOOL is a robust, **offline-first** agricultural operating system designed for low-connectivity environments. Unlike traditional data collection apps, SAHOOL utilizes a **geospatial-centric core** (similar to John Deere Ops Center) to provide real-time advisory, irrigation management, and crop health monitoring (NDVI) to smallholder farmers.

### Key Differentiators

- **Offline-First Architecture**: Full functionality without internet connectivity
- **Geospatial Intelligence**: PostGIS-powered vector field rendering
- **AI-Driven Advisory**: Crop disease detection and fertilizer recommendations
- **Enterprise-Grade Security**: JWT authentication, RBAC, and audit logging

---

## 🏗️ Technical Architecture

The platform follows a **Domain-Driven Design (DDD)** approach within a Monorepo structure:

```
┌─────────────────────────────────────────────────────────────────┐
│                        SAHOOL Platform                          │
├─────────────────────────────────────────────────────────────────┤
│  📱 Mobile App          │  🌐 Web Dashboard    │  🔧 Admin Portal │
│  (Flutter/Offline)      │  (React/Analytics)   │  (Management)    │
├─────────────────────────────────────────────────────────────────┤
│                      Kong API Gateway                            │
│                   (Authentication & Rate Limiting)               │
├─────────────────────────────────────────────────────────────────┤
│  🌾 Field Ops  │  🛰️ NDVI Engine  │  🌤️ Weather  │  🤖 Agro AI   │
│  (Tasks)       │  (Satellite)      │  (Forecast)  │  (Advisory)   │
├─────────────────────────────────────────────────────────────────┤
│  💬 Field Chat │  📡 IoT Gateway  │  🔄 Sync Engine │  📊 Analytics │
│  (Real-time)   │  (Sensors)       │  (Offline)      │  (BI)         │
├─────────────────────────────────────────────────────────────────┤
│                    NATS (Event Bus / Message Queue)              │
├─────────────────────────────────────────────────────────────────┤
│                    PostGIS (Geospatial Database)                 │
└─────────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Layer             | Technology                                   |
| ----------------- | -------------------------------------------- |
| **Mobile**        | Flutter 3.x, Riverpod, Isar DB, Google Fonts |
| **Backend**       | Python (FastAPI), Node.js, Tortoise ORM      |
| **Database**      | PostgreSQL + PostGIS (Geospatial)            |
| **Message Queue** | NATS (Event-Driven Architecture)             |
| **API Gateway**   | Kong (Authentication, Rate Limiting)         |
| **Container**     | Docker, Kubernetes (K8s)                     |
| **IaC**           | Terraform, Helm Charts                       |
| **CI/CD**         | GitHub Actions, Argo CD                      |

---

## 🚀 Quick Start (Development)

### Prerequisites

- Docker & Docker Compose
- Flutter SDK (v3.x)
- Node.js (v18+)
- Python (v3.11+)

### Running the Infrastructure

Start the entire backend stack (Postgres, Kong, NATS, Core Services):

```bash
# First, create .env file (required for Docker Compose)
ln -s .env.development .env

# Using Make (recommended)
make up

# OR using Docker Compose directly
docker-compose up -d

# Check service health
make logs
```

### Running the Mobile App

```bash
cd mobile/sahool_field_app
flutter pub get
flutter run
```

### 🛡️ Enterprise Patch Generator (v2.0)

To quickly set up a patched Flutter mobile application with all Enterprise-grade fixes (Drift Singleton fix, Conflict Schema, Native Configs), use the following script:

```bash
./generate_sahool_v2.sh
```

This script ensures:

- Background stability (Drift Isolate fix).
- Conflict-ready schema (Outbox, SyncEvents).
- Correct native configurations (Android/iOS Workmanager).

### Database Access

```bash
# Connect to PostGIS database
make db-shell

# Run SQL queries
SELECT * FROM fields WHERE ST_Within(geom, ST_MakeEnvelope(...));
```

---

## 📂 Repository Structure

| Path          | Description                                           |
| ------------- | ----------------------------------------------------- |
| `/kernel`     | Backend Microservices (Field Core, Auth, NDVI Engine) |
| `/mobile`     | Flutter Field Application (Offline-first logic)       |
| `/frontend`   | Web Dashboard & Admin Portal                          |
| `/infra`      | Infrastructure as Code (Docker, K8s, Terraform)       |
| `/helm`       | Kubernetes Helm Charts                                |
| `/gitops`     | Argo CD Applications & GitOps Configuration           |
| `/idp`        | Internal Developer Platform (Backstage)               |
| `/docs`       | Technical Documentation                               |
| `/governance` | Security Policies & Compliance                        |

---

## 🔌 Microservices

| Service                   | Port | Description                            |
| ------------------------- | ---- | -------------------------------------- |
| **Core Services**         |      |                                        |
| `field_ops`               | 8080 | Field & Task Management                |
| `field_core`              | 3000 | Field Core Operations                  |
| `task_service`            | 8103 | Task Management Service                |
| **AI & Analytics**        |      |                                        |
| `ndvi_engine`             | 8107 | Satellite Imagery Analysis (NDVI/NDWI) |
| `crop_health_ai`          | 8095 | AI-Powered Crop Health Analysis        |
| `agro_advisor`            | 8105 | AI-Powered Recommendations             |
| `yield_engine`            | 8098 | Yield Prediction Engine                |
| `lai_estimation`          | 3022 | Leaf Area Index Estimation             |
| **Weather & Environment** |      |                                        |
| `weather_core`            | 8108 | Weather Forecasting & Alerts           |
| `weather_advanced`        | 8092 | Advanced Weather Analytics             |
| **Communication**         |      |                                        |
| `field_chat`              | 8099 | Real-time Team Collaboration           |
| `community_chat`          | 8097 | Community Discussion Platform          |
| `ws_gateway`              | 8081 | WebSocket Real-time Events             |
| **IoT & Sensors**         |      |                                        |
| `iot_gateway`             | 8106 | IoT Sensor Integration                 |
| `virtual_sensors`         | 8096 | Virtual Sensor Management              |
| **Infrastructure**        |      |                                        |
| `kong`                    | 8000 | API Gateway (31 upstreams)             |
| `marketplace`             | 3010 | Agricultural Marketplace               |
| `notification_service`    | 8110 | Push Notification Service              |

**Total Services**: 31 microservices managed through Kong API Gateway
**Full Service Reference**: See [API Gateway Documentation](docs/API_GATEWAY.md)

---

## 📱 Mobile Application Features

### Offline-First Capabilities

- **Local Database**: Isar DB for complete offline functionality
- **Background Sync**: Automatic data synchronization when online
- **Conflict Resolution**: Smart merge strategies for offline edits

### Core Features

- 🗺️ **Interactive Field Maps**: View and manage agricultural fields
- 📊 **Health Monitoring**: NDVI/NDWI crop health visualization
- ✅ **Task Management**: Create, assign, and track field tasks
- 📸 **Photo Documentation**: Capture and attach field images
- 🌤️ **Weather Integration**: Real-time weather data and forecasts
- 📍 **GPS Tracking**: Field boundary mapping and navigation

---

## 🛡️ Security & Compliance

- **Authentication**: JWT-based with refresh tokens
- **Authorization**: Role-Based Access Control (RBAC)
- **Audit Logging**: Complete activity tracking
- **Data Encryption**: At-rest and in-transit encryption
- **API Security**: Rate limiting, CORS, input validation

---

## Documentation

### Getting Started

- [Deployment Guide](docs/DEPLOYMENT.md) - Docker and Kubernetes deployment
- [Contributing Guide](CONTRIBUTING.md) - Contribution guidelines (AR/EN)
- [Troubleshooting Guide](docs/TROUBLESHOOTING.md) - Common issues and solutions

### Architecture

- [Architecture Diagrams](docs/ARCHITECTURE_DIAGRAMS.md) - System architecture visualizations
- [API Gateway Guide](docs/API_GATEWAY.md) - Kong configuration and security
- [Data Flow](docs/DATA_FLOW.md) - Data flow patterns

### API Reference

- [API Comprehensive Guide](docs/API_COMPREHENSIVE.md) - Developer-friendly API documentation
- [API Endpoints Reference](docs/API_ENDPOINTS_REFERENCE.md) - Complete endpoint listing

### Operations

- [Operations Guide](docs/OPERATIONS.md) - Operational procedures
- [Observability Guide](docs/OBSERVABILITY.md) - Monitoring and logging
- [Incident Runbooks](docs/RUNBOOKS.md) - Incident response
- [Security Guide](docs/SECURITY.md) - Security configuration

### Full Documentation Index

See [docs/README.md](docs/README.md) for the complete documentation index (140+ documents).

---

## 🔍 Observability & Monitoring

SAHOOL includes comprehensive observability features for production monitoring:

### Health Checks

All services expose standardized health check endpoints:

- **`/health/live`** - Liveness probe (is service running?)
- **`/health/ready`** - Readiness probe (can service handle requests?)
- **`/health/startup`** - Startup probe (has service initialized?)
- **`/health`** - Combined health status

```bash
# Check service health
curl http://localhost:8095/health
```

### Metrics (Prometheus)

All services expose Prometheus metrics at `/metrics`:

- Request count, duration, and status codes
- Error rates by type and severity
- Active connections and resource usage
- Custom business metrics

```bash
# View service metrics
curl http://localhost:8095/metrics

# Access Prometheus UI
open http://localhost:9090

# View Grafana dashboards
open http://localhost:3002
```

### Structured Logging

- **JSON logs** in production for machine parsing
- **Human-readable logs** in development
- **Request ID propagation** across all logs
- **Trace ID integration** with OpenTelemetry

### Distributed Tracing (Optional)

- OpenTelemetry support for distributed tracing
- Automatic instrumentation of FastAPI apps
- Trace context propagation across services

See [Observability Guide](docs/OBSERVABILITY.md) for details.

---

## 🔐 Security & Secrets Management

### Secrets Externalization

Supports multiple secret backends:

- **Environment variables** (default)
- **HashiCorp Vault** (recommended for production)
- **AWS Secrets Manager** (coming soon)
- **Azure Key Vault** (coming soon)

```bash
# Configure Vault (optional)
export SECRET_BACKEND=vault
export VAULT_ADDR=http://localhost:8200
export VAULT_TOKEN=your-token

# Services automatically use Vault
```

### Rate Limiting

Tiered rate limiting on all endpoints:

- **Free**: 30 req/min, 500 req/hour
- **Standard**: 60 req/min, 2000 req/hour
- **Premium**: 120 req/min, 5000 req/hour
- **Internal**: 1000 req/min, 50000 req/hour

### Security Scanning

- **SAST**: Bandit + Semgrep with SARIF upload
- **Dependency Scanning**: Safety + pip-audit + Trivy
- **Secret Scanning**: Pre-commit hooks + CI checks
- **Container Scanning**: Trivy for Docker images

---

## ⚡ Performance Optimizations

### Database Connection Pooling

Configured connection pooling with:

- Configurable pool size and overflow
- Automatic connection recycling
- Retry logic with exponential backoff
- Connection health checks

```bash
# Configure pooling
export DB_POOL_SIZE=20
export DB_MAX_OVERFLOW=10
export DB_POOL_RECYCLE=3600
```

### Caching Layer

Redis-first caching with in-memory fallback:

- Configurable TTL per data type
- Pattern-based cache invalidation
- Automatic fallback to in-memory cache
- Cache warming support

```bash
# Enable caching
export CACHE_ENABLED=true
export REDIS_URL=redis://localhost:6379
export CACHE_TTL_SECONDS=300
```

### Pagination

Both cursor-based and offset-based pagination:

- **Cursor-based**: For large datasets (efficient)
- **Offset-based**: For smaller datasets (simple)
- **Streaming**: For very large results (NDJSON, JSON arrays)

```python
# Cursor-based pagination
GET /api/items?first=50&after=cursor_abc123

# Offset-based pagination
GET /api/items?page=2&page_size=50
```

---

## 🧪 Testing

### Test Coverage

- **Unit tests**: Business logic and utilities
- **Integration tests**: API endpoints and database
- **Identity tests**: Login, token refresh, OAuth, MFA
- **Smoke tests**: Import and basic functionality

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test types
make test-unit
make test-integration
make test-smoke
```

### CI/CD Pipeline

- ✅ **Parallel testing** with pytest-xdist
- ✅ **Coverage regression checks** (minimum 60%)
- ✅ **Build caching** for faster CI runs
- ✅ **SARIF security reports** in GitHub Security tab

---

## 🏢 Internal Developer Platform (IDP)

This repository includes an **Internal Developer Platform** for streamlined development:

```bash
# Create local K3d cluster
./dev/k3d/create-cluster.sh

# Deploy IDP components
kubectl apply -f gitops/argocd/applications/idp-root-app.yaml

# Access Backstage Portal
kubectl -n backstage port-forward svc/backstage 7007:7007
```

### IDP Components

- **Backstage**: Developer portal with service catalog
- **Argo CD**: GitOps-based continuous deployment
- **Service Templates**: Scaffolding for new microservices

---

## 🔀 Pull Request Automation

SAHOOL includes a comprehensive PR automation system for efficient code review and merging:

### Quick Start

```bash
# Merge a specific PR
make pr-merge PR=123

# Check status of all open PRs
make pr-status

# Monitor PR health
make pr-monitor

# Get help
make pr-help
```

### Features

- **Automated Conflict Resolution**: Intelligently resolves merge conflicts
- **Multiple Merge Strategies**: Auto, merge, squash, or rebase
- **Safety Checks**: Requires CI/CD checks and approvals
- **PR Health Monitoring**: Daily reports on PR status
- **Detailed Reporting**: Audit trails for all merge operations

### GitHub Actions

The automation system includes two workflows:

1. **Auto-Merge PRs** (`.github/workflows/auto-merge-prs.yml`)
   - Automates the entire merge process
   - Supports batch processing
   - Dry-run mode for testing

2. **PR Status Monitor** (`.github/workflows/pr-status-monitor.yml`)
   - Monitors open PRs daily
   - Auto-updates branches
   - Sends notifications for conflicts

### Documentation

- 📚 **Full Guide**: [docs/PR_AUTOMATION.md](docs/PR_AUTOMATION.md)
- 🚀 **Quick Start**: [docs/PR_AUTOMATION_QUICKSTART.md](docs/PR_AUTOMATION_QUICKSTART.md)

---

## Contributing

We welcome contributions from the development team. Please read our [Contributing Guide](CONTRIBUTING.md) before submitting changes.

### Quick Contribution Steps

1. Create a feature branch from `develop`
2. Make your changes following our coding standards
3. Write tests for new functionality
4. Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

---

## 📄 License

**Proprietary Software** - Owned by KAFAAT.

All rights reserved. Unauthorized copying, modification, or distribution is prohibited.

---

<p align="center">
  <strong>SAHOOL v16.0.0</strong> | Built for Saudi Agriculture
  <br>
  <sub>Last Updated: February 2026</sub>
</p>
