# SAHOOL Microservices Architecture Documentation

> **Generated**: 2026-01-25 | **Updated**: 2026-03-04
> **Platform Version**: 16.0.0
> **Total Services Analyzed**: 41 (72 service directories total)
> **Total Documentation Lines**: ~30,000+

---

## Coding Agent Instructions (Antigravity Coding Agent)

### Purpose

This documentation enables the Antigravity Coding Agent to understand and modify the SAHOOL microservices architecture, specifically for making the `apps/admin` portal dynamic by integrating with real backend APIs instead of static data.

### Critical Understanding

Before making any modifications, understand that SAHOOL uses:

1. **Kong API Gateway** (Port 8000) - All API requests must go through Kong
2. **4-Layer Event Architecture** via NATS:
   - **Acquisition**: Data ingestion (satellite, IoT, weather)
   - **Intelligence**: Feature extraction (NDVI, indicators, crop analysis)
   - **Decision**: Recommendations (advisory, irrigation, yield)
   - **Business**: User-facing (notifications, marketplace, billing)
3. **Multi-tenant Architecture** - Always include `tenant_id` in requests
4. **Bilingual Support** - Arabic (ar) and English (en) throughout

### API Base URL Pattern

```typescript
// Development
const API_BASE = 'http://localhost:8000';

// Production
const API_BASE = 'https://api.sahool.com';

// All service calls go through Kong
const endpoints = {
  users: `${API_BASE}/api/v1/users`,
  fields: `${API_BASE}/api/v1/fields`,
  billing: `${API_BASE}/api/v1/billing`,
  // ... etc
};
```

### Authentication Pattern

```typescript
// All protected endpoints require JWT Bearer token
const headers = {
  'Authorization': `Bearer ${accessToken}`,
  'Content-Type': 'application/json',
  'X-Tenant-Id': tenantId, // Required for multi-tenant isolation
};
```

### React Query Integration Pattern

```typescript
// Standard pattern for admin portal API integration
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

// List query
export function useFields(tenantId: string) {
  return useQuery({
    queryKey: ['fields', tenantId],
    queryFn: () => api.get(`/api/v1/fields?tenant_id=${tenantId}`),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

// Mutation with optimistic update
export function useUpdateField() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: FieldUpdate) => api.patch(`/api/v1/fields/${data.id}`, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['fields'] });
    },
  });
}
```

---

## Service Index

### Infrastructure Services

| Service | Port | Documentation | Status |
|---------|------|---------------|--------|
| PostgreSQL + PostGIS | 5432 | [infrastructure.md](./infrastructure.md) | Active |
| PgBouncer | 6432 | [infrastructure.md](./infrastructure.md) | Active |
| NATS JetStream | 4222 | [infrastructure.md](./infrastructure.md) | Active |
| Kong Gateway | 8000 | [infrastructure.md](./infrastructure.md) | Active |
| Redis | 6379 | [infrastructure.md](./infrastructure.md) | Active |
| Ollama LLM | 11434 | [ollama-infrastructure.md](./ollama-infrastructure.md) | GPU Profile |

### Node.js Services (NestJS/Express)

| Service | Port | Kong Route | Documentation | Admin Integration |
|---------|------|------------|---------------|-------------------|
| user-service | 3025 | /api/v1/auth, /api/v1/users | [user-service.md](./user-service.md) | User Management |
| field-management-service | 3000 | /api/v1/fields | [field-management-service.md](./field-management-service.md) | Field Management |
| marketplace-service | 3010 | /api/v1/marketplace | [marketplace-service.md](./marketplace-service.md) | Marketplace |
| research-core | 3015 | /api/v1/research | [research-core.md](./research-core.md) | Research Trials |
| disaster-assessment | 3020 | /api/v1/disaster | [disaster-assessment.md](./disaster-assessment.md) | Disaster Reports |
| chat-service | 8115 | /api/v1/chat | [chat-service.md](./chat-service.md) | Chat Management |
| iot-service | 8117 | /api/v1/iot | [iot-service.md](./iot-service.md) | IoT Dashboard |
| community-chat *(deprecated)* | 8097 | /api/v1/community | [community-chat.md](./community-chat.md) | DEPRECATED |

### Python Services (FastAPI)

| Service | Port | Kong Route | Documentation | Admin Integration |
|---------|------|------------|---------------|-------------------|
| ws-gateway | 8081 | /ws | [ws-gateway.md](./ws-gateway.md) | WebSocket Monitor |
| billing-core | 8089 | /api/v1/billing | [billing-core.md](./billing-core.md) | Billing Dashboard |
| vegetation-analysis-service | 8090 | /api/v1/vegetation, /api/v1/ndvi | [vegetation-analysis-service.md](./vegetation-analysis-service.md) | NDVI Analytics |
| indicators-service | 8091 | /api/v1/indicators | [indicators-service.md](./indicators-service.md) | Indicators Dashboard |
| weather-service | 8092 | /api/v1/weather | [weather-service.md](./weather-service.md) | Weather Dashboard |
| advisory-service | 8093 | /api/v1/advisory | [advisory-service.md](./advisory-service.md) | Advisory Management |
| irrigation-smart | 8094 | /api/v1/irrigation | [irrigation-smart.md](./irrigation-smart.md) | Irrigation Control |
| crop-intelligence-service | 8095 | /api/v1/crop-health | [crop-intelligence-service.md](./crop-intelligence-service.md) | Crop Health |
| virtual-sensors | 8119 | /api/v1/virtual-sensors | [virtual-sensors.md](./virtual-sensors.md) | Virtual Sensors |
| yield-prediction-service | 8152 | /api/v1/yield | [yield-prediction-service.md](./yield-prediction-service.md) | Yield Forecasts |
| field-chat *(deprecated)* | 8099 | /api/v1/field-chat | [field-chat.md](./field-chat.md) | DEPRECATED |
| equipment-service | 8101 | /api/v1/equipment | [equipment-service.md](./equipment-service.md) | Equipment Mgmt |
| task-service | 8103 | /api/v1/tasks | [task-service.md](./task-service.md) | Task Management |
| provider-config | 8104 | /api/v1/provider-config | [provider-config.md](./provider-config.md) | Provider Config |
| agro-advisor *(deprecated)* | 8105 | /api/v1/agro-advisor | [agro-advisor.md](./agro-advisor.md) | DEPRECATED |
| iot-gateway | 8106 | /api/v1/iot-gateway | [iot-gateway.md](./iot-gateway.md) | IoT Gateway |
| weather-core *(deprecated)* | 8108 | /api/v1/weather-core | [weather-core.md](./weather-core.md) | DEPRECATED |
| notification-service | 8110 | /api/v1/notifications | [notification-service.md](./notification-service.md) | Notifications |
| astronomical-calendar | 8111 | /api/v1/astronomy | [astronomical-calendar.md](./astronomical-calendar.md) | Calendar |
| ai-advisor | 8112 | /api/v1/ai-advisor | [ai-advisor.md](./ai-advisor.md) | AI Advisor |
| alert-service | 8113 | /api/v1/alerts | [alert-service.md](./alert-service.md) | Alert Management |
| inventory-service | 8116 | /api/v1/inventory | [inventory-service.md](./inventory-service.md) | Inventory |
| field-intelligence | 8120 | /api/v1/field-intelligence | [field-intelligence.md](./field-intelligence.md) | Field Analytics |
| skills-service | 8121 | /api/v1/skills | [skills-service.md](./skills-service.md) | Skills Assessment |
| code-review-service | 8102 | /api/v1/code-review | [code-review-service.md](./code-review-service.md) | Code Review |
| crm-service | 8131 | /api/v1/crm | [crm-service.md](./crm-service.md) | CRM Dashboard |
| lowcode-engine | 8132 | /api/v1/lowcode | [lowcode-engine.md](./lowcode-engine.md) | Low-Code Builder |
| ai-agents-service | 8130 | /api/v1/ai-agents-service | [ai-agents-service.md](./ai-agents-service.md) | AI Agents |
| copilot-api | 8088 | /api/v1/copilot | - | AI Copilot (multi-LLM, RAG) |
| ai-chat-assistant | 8260 | /api/v1/ai-chat | - | AI Chat Assistant |
| code-fix-agent | 8162 | /api/v1/code-fix | - | Code Fix AI Agent |
| ground-vision-service | 8182 | /api/v1/ground-vision | - | Ground-level Vision Analysis |
| mcp-server | 8200 | /api/v1/mcp | [mcp-server.md](./mcp-server.md) | MCP Protocol |
| agro-rules | N/A | NATS-only | [agro-rules.md](./agro-rules.md) | N/A (Worker) |

---

## Critical Issues Summary

### Port Mismatches (MUST FIX)

| Service | Kong Config | Docker Config | Code Default | Fix Required |
|---------|-------------|---------------|--------------|--------------|
| yield-prediction-service | 8152 | 8152 | 8152 | Fixed - all aligned to 8152 |
| chat-service | 8000 | 8115 | 8115 | Update Kong to 8115 |
| skills-service | 8121 | 8121 | 8170 | Update code to 8121 |
| code-review-service | 8102 | 8102 | 8096 | Update code to 8102 |

### Missing NATS Integration

The following services have NATS_URL configured but do NOT publish events:

- `indicators-service` - Should publish indicator calculations
- `crop-intelligence-service` - Should publish disease detections
- `irrigation-smart` - Should publish irrigation plans
- `provider-config` - Should publish config changes
- `skills-service` - Should publish skill assessments
- `lowcode-engine` - Should publish page/model changes

### In-Memory Storage (Data Loss Risk)

These services use in-memory storage and lose data on restart:

| Service | Data at Risk | Recommended Fix |
|---------|--------------|-----------------|
| community-chat | All chat data | Add PostgreSQL persistence |
| disaster-assessment | Disaster reports | Add PostgreSQL persistence |
| crop-intelligence-service | Health observations | Add PostgreSQL persistence |
| indicators-service | Indicator values | Add PostgreSQL persistence |
| lowcode-engine | Pages, models | Add PostgreSQL persistence |
| iot-gateway | Device registry | Add PostgreSQL/Redis |

### Missing Authentication

These endpoints lack authentication but should require it:

| Service | Endpoint | Risk Level |
|---------|----------|------------|
| marketplace-service | PUT /fintech/wallet/:id/limits | HIGH |
| chat-service | POST /conversations | MEDIUM |
| field-chat | All endpoints | HIGH |
| crop-intelligence-service | All endpoints | HIGH |
| irrigation-smart | All endpoints | HIGH |

---

## Admin Portal Integration Guide

### Recommended Admin Pages

Based on the service analysis, the following admin pages should be created or updated:

#### 1. User Management (`/admin/users`)
**Service**: user-service (Port 3025)
```typescript
// API endpoints to integrate
GET  /api/v1/users                    // List users with pagination
GET  /api/v1/users/:id                // Get user details
POST /api/v1/users                    // Create user (admin only)
PUT  /api/v1/users/:id                // Update user
DELETE /api/v1/users/:id              // Delete user (soft delete)
GET  /api/v1/users/stats              // User statistics
```

#### 2. Field Management (`/admin/fields`)
**Service**: field-management-service (Port 3000)
```typescript
GET  /api/v1/fields                   // List fields with filters
GET  /api/v1/fields/:id               // Get field with geometry
POST /api/v1/fields                   // Create field
PUT  /api/v1/fields/:id               // Update field
DELETE /api/v1/fields/:id             // Delete field
GET  /api/v1/fields/:id/ndvi          // Get NDVI history
GET  /api/v1/fields/:id/health        // Get health analysis
```

#### 3. Billing Dashboard (`/admin/billing`)
**Service**: billing-core (Port 8089)
```typescript
GET  /api/v1/billing/v1/plans         // List subscription plans
GET  /api/v1/billing/v1/tenants/:id   // Get tenant billing info
GET  /api/v1/billing/v1/invoices      // List invoices
GET  /api/v1/billing/v1/reports/revenue // Revenue reports
```

#### 4. Notification Center (`/admin/notifications`)
**Service**: notification-service (Port 8110)
```typescript
GET  /api/v1/notifications            // List notifications
POST /api/v1/notifications/broadcast  // Send broadcast
GET  /api/v1/notifications/stats      // Notification statistics
GET  /api/v1/channels                 // List channels
```

#### 5. IoT Dashboard (`/admin/iot`)
**Services**: iot-service (8117), iot-gateway (8106)
```typescript
GET  /api/v1/iot/devices              // List all devices
GET  /api/v1/iot/field/:id/sensors    // Field sensors
POST /api/v1/iot-gateway/device/register // Register device
GET  /api/v1/iot-gateway/stats        // Gateway statistics
```

#### 6. Weather Dashboard (`/admin/weather`)
**Service**: weather-service (Port 8092)
```typescript
GET  /api/v1/weather/current          // Current weather
GET  /api/v1/weather/forecast         // Weather forecast
GET  /api/v1/weather/agricultural-report // Ag report
```

#### 7. Alert Management (`/admin/alerts`)
**Service**: alert-service (Port 8113)
```typescript
GET  /api/v1/alerts                   // List alerts
POST /api/v1/alerts                   // Create alert
POST /api/v1/alerts/:id/acknowledge   // Acknowledge alert
POST /api/v1/alerts/:id/resolve       // Resolve alert
GET  /api/v1/alerts/stats             // Alert statistics
```

#### 8. Inventory Management (`/admin/inventory`)
**Service**: inventory-service (Port 8116)
```typescript
GET  /api/v1/inventory                // List inventory items
POST /api/v1/inventory                // Add item
GET  /api/v1/inventory/analytics/dashboard // Dashboard data
GET  /api/v1/inventory/alerts         // Low stock alerts
```

#### 9. Task Management (`/admin/tasks`)
**Service**: task-service (Port 8103)
```typescript
GET  /api/v1/tasks                    // List tasks
POST /api/v1/tasks                    // Create task
PUT  /api/v1/tasks/:id                // Update task
POST /api/v1/tasks/:id/complete       // Complete task
GET  /api/v1/tasks/stats              // Task statistics
```

#### 10. CRM Dashboard (`/admin/crm`)
**Service**: crm-service (Port 8131)
```typescript
GET  /api/v1/crm/farmers              // List farmers
POST /api/v1/crm/farmers              // Create farmer
GET  /api/v1/crm/deals                // List deals
GET  /api/v1/crm/interactions         // List interactions
GET  /api/v1/crm/metrics              // CRM metrics
```

---

## Environment Variables Summary

### Required for All Services

```bash
# Database (via PgBouncer)
DATABASE_URL=postgresql://user:pass@pgbouncer:6432/sahool

# NATS Messaging
NATS_URL=nats://user:pass@nats:4222

# Redis Cache
REDIS_URL=redis://:pass@redis:6379/0

# JWT Authentication
JWT_SECRET_KEY=your-32-char-minimum-secret-key
JWT_ALGORITHM=HS256

# General
ENVIRONMENT=development|staging|production
LOG_LEVEL=INFO|DEBUG|WARNING|ERROR
```

### Service-Specific Variables

See individual service documentation for complete lists. Key external integrations:

| Service | External API Keys Required |
|---------|---------------------------|
| vegetation-analysis-service | SENTINEL_HUB_*, NASA_EARTHDATA_*, PLANET_* |
| weather-service | OPENWEATHER_API_KEY, WEATHERAPI_KEY |
| billing-core | STRIPE_*, THARWATT_* |
| notification-service | TWILIO_*, SENDGRID_*, FIREBASE_* |
| ai-advisor | ANTHROPIC_API_KEY, OPENAI_API_KEY |

---

## File Structure

```
apps/services-docs/
├── README.md                          # This file (Master Index)
├── infrastructure.md                  # PostgreSQL, PgBouncer, NATS, Kong
├── ollama-infrastructure.md           # Ollama LLM Server
│
├── # Node.js Services
├── user-service.md
├── field-management-service.md
├── marketplace-service.md
├── research-core.md
├── disaster-assessment.md
├── chat-service.md
├── iot-service.md
├── community-chat.md                  # DEPRECATED
│
├── # Python Services - Core
├── ws-gateway.md
├── billing-core.md
├── notification-service.md
├── alert-service.md
├── task-service.md
├── equipment-service.md
├── inventory-service.md
│
├── # Python Services - Intelligence
├── vegetation-analysis-service.md
├── indicators-service.md
├── weather-service.md
├── weather-core.md                    # DEPRECATED
├── advisory-service.md
├── agro-advisor.md                    # DEPRECATED
├── irrigation-smart.md
├── crop-intelligence-service.md
├── virtual-sensors.md
├── yield-prediction-service.md
├── field-intelligence.md
│
├── # Python Services - AI/ML
├── ai-advisor.md
├── ai-agents-service.md
├── mcp-server.md
├── skills-service.md
├── code-review-service.md
│
├── # Python Services - Business
├── provider-config.md
├── astronomical-calendar.md
├── field-chat.md
├── crm-service.md
├── lowcode-engine.md
├── iot-gateway.md
│
└── # Workers (No HTTP)
    └── agro-rules.md
```

---

## Quick Reference Commands

```bash
# Start all services
make dev

# View service logs
docker compose logs -f <service-name>

# Check service health
curl http://localhost:8000/<route>/healthz

# Access PostgreSQL
make db-shell

# Run tests
make test

# Lint code
make lint
```

---

## Changelog

### 2026-01-25
- Initial documentation generation
- 41 services analyzed
- 30,000+ lines of documentation
- Critical issues identified
- Admin integration guide created

---

*Generated by Claude Code for SAHOOL Platform v16.0.0*
