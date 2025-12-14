# SAHOOL Unified v15 (IDP) 🌾
> **The National Agricultural Intelligence Platform**
> *From Field Data to AI-Driven Decisions.*

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)]()
[![Architecture](https://img.shields.io/badge/architecture-microservices-blue)]()
[![Platform](https://img.shields.io/badge/platform-mobile%20%7C%20web-orange)]()
[![Version](https://img.shields.io/badge/version-15.3.2-green)]()

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

| Layer | Technology |
|-------|------------|
| **Mobile** | Flutter 3.x, Riverpod, Isar DB, Google Fonts |
| **Backend** | Python (FastAPI), Node.js, Tortoise ORM |
| **Database** | PostgreSQL + PostGIS (Geospatial) |
| **Message Queue** | NATS (Event-Driven Architecture) |
| **API Gateway** | Kong (Authentication, Rate Limiting) |
| **Container** | Docker, Kubernetes (K8s) |
| **IaC** | Terraform, Helm Charts |
| **CI/CD** | GitHub Actions, Argo CD |

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

### Database Access

```bash
# Connect to PostGIS database
make db-shell

# Run SQL queries
SELECT * FROM fields WHERE ST_Within(geom, ST_MakeEnvelope(...));
```

---

## 📂 Repository Structure

| Path | Description |
|------|-------------|
| `/kernel` | Backend Microservices (Field Core, Auth, NDVI Engine) |
| `/mobile` | Flutter Field Application (Offline-first logic) |
| `/frontend` | Web Dashboard & Admin Portal |
| `/infra` | Infrastructure as Code (Docker, K8s, Terraform) |
| `/helm` | Kubernetes Helm Charts |
| `/gitops` | Argo CD Applications & GitOps Configuration |
| `/idp` | Internal Developer Platform (Backstage) |
| `/docs` | Technical Documentation |
| `/governance` | Security Policies & Compliance |

---

## 🔌 Microservices

| Service | Port | Description |
|---------|------|-------------|
| `field_ops` | 8080 | Field & Task Management |
| `ndvi_engine` | 8097 | Satellite Imagery Analysis (NDVI/NDWI) |
| `weather_core` | 8098 | Weather Forecasting & Alerts |
| `field_chat` | 8099 | Real-time Team Collaboration |
| `iot_gateway` | 8094 | IoT Sensor Integration |
| `agro_advisor` | 8095 | AI-Powered Recommendations |
| `ws_gateway` | 8090 | WebSocket Real-time Events |
| `kong` | 8000 | API Gateway |

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

## 📚 Documentation

- [Deployment Guide](docs/DEPLOYMENT.md)
- [Security Guide](docs/SECURITY.md)
- [Operations Runbook](docs/OPERATIONS.md)
- [API Documentation](docs/API.md)

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

## 🤝 Contributing

This is a proprietary project. For contribution guidelines, please contact the development team.

---

## 📄 License

**Proprietary Software** - Owned by KAFAAT.

All rights reserved. Unauthorized copying, modification, or distribution is prohibited.

---

<p align="center">
  <strong>SAHOOL v15.3.2</strong> | Built with ❤️ for Saudi Agriculture
  <br>
  <sub>Last Updated: December 2024</sub>
</p>
