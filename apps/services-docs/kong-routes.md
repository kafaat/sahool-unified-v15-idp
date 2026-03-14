# Kong Gateway Routes - Complete Configuration

**Last Updated:** 2026-01-30  
**Kong Version:** 3.4  
**Configuration Mode:** DB-less (Declarative)  
**Total Routes:** 62

---

## 🌐 Route Configuration Overview

All HTTP traffic to SAHOOL services flows through Kong Gateway on port 8000. Kong provides:

- **API Gateway:** Single entry point for all services
- **Rate Limiting:** Prevents abuse
- **CORS:** Cross-origin resource sharing
- **Prometheus Metrics:** Monitoring and observability
- **Request Correlation:** Distributed tracing via X-Correlation-Id

---

## 🔓 Public Routes (No Authentication)

### User Authentication

| Method | Route | Service | Port | Purpose |
|--------|-------|---------|------|---------|
| POST | `/api/v1/auth/login` | user-service | 3025 | User login |
| POST | `/api/v1/auth/register` | user-service | 3025 | User registration |
| POST | `/api/v1/auth/forgot-password` | user-service | 3025 | Password reset request |
| POST | `/api/v1/auth/reset-password` | user-service | 3025 | Password reset confirmation |
| POST | `/api/v1/auth/send-otp` | user-service | 3025 | Send OTP |
| POST | `/api/v1/auth/verify-otp` | user-service | 3025 | Verify OTP |
| POST | `/api/v1/auth/refresh` | user-service | 3025 | Refresh access token |

**Rate Limit:** 30 requests/minute, 500 requests/hour

### Health Checks

| Method | Route | Service | Purpose |
|--------|-------|---------|---------|
| GET | `/health` | kong | Platform health check |
| GET | `/ping` | kong | Platform ping check |
| GET | `/api/v1/health` | user-service | User service health |
| GET | `/api/v1/healthz` | user-service | User service health (alt) |
| GET | `/api/v1/readyz` | user-service | User service readiness |

**Rate Limit:** None

---

## 🔒 Protected Routes (JWT Required)

### User Management

| Method | Route | Service | Port | Purpose |
|--------|-------|---------|------|---------|
| POST | `/api/v1/auth/logout` | user-service | 3025 | Logout current session |
| POST | `/api/v1/auth/logout-all` | user-service | 3025 | Logout all sessions |
| GET | `/api/v1/auth/me` | user-service | 3025 | Get current user |
| GET/POST/PUT/DELETE | `/api/v1/users` | user-service | 3025 | User CRUD operations |

**Rate Limit:** 100 requests/minute, 2000 requests/hour

### Field Management

| Method | Route | Service | Port | Purpose |
|--------|-------|---------|------|---------|
| ALL | `/api/v1/fields` | field-management-service | 3000 | Field operations |
| ALL | `/api/v1/field` | field-management-service | 3000 | Single field operations |
| ALL | `/field` | field-management-service | 3000 | Legacy field route |

### Marketplace & FinTech

| Method | Route | Service | Port | Purpose |
|--------|-------|---------|------|---------|
| ALL | `/api/v1/marketplace` | marketplace-service | 3010 | Marketplace operations |
| ALL | `/marketplace` | marketplace-service | 3010 | Legacy marketplace route |

### Research Management

| Method | Route | Service | Port | Purpose |
|--------|-------|---------|------|---------|
| ALL | `/api/v1/research` | research-core | 3015 | Research trials |
| ALL | `/research` | research-core | 3015 | Legacy research route |

### Disaster Assessment

| Method | Route | Service | Port | Purpose |
|--------|-------|---------|------|---------|
| ALL | `/api/v1/disaster` | disaster-assessment | 3020 | Disaster reports |
| ALL | `/disaster` | disaster-assessment | 3020 | Legacy disaster route |

### Chat & Communication

| Method | Route | Service | Port | Purpose |
|--------|-------|---------|------|---------|
| ALL | `/api/v1/chat` | chat-service | 8000 | Chat operations |
| ALL | `/chat` | chat-service | 8000 | Legacy chat route |
| ALL | `/api/v1/field-chat` | field-chat | 8099 | Field-specific chat |
| ALL | `/field-chat` | field-chat | 8099 | Legacy field chat route |
| ALL | `/api/v1/community` | community-chat | 8097 | Community posts |
| ALL | `/api/v1/posts` | community-chat | 8097 | Community posts (alt) |
| ALL | `/community` | community-chat | 8097 | Legacy community route |

### IoT & Sensors

| Method | Route | Service | Port | Purpose |
|--------|-------|---------|------|---------|
| ALL | `/api/v1/iot` | iot-service | 8117 | IoT device management |
| ALL | `/iot` | iot-service | 8117 | Legacy IoT route |
| ALL | `/api/v1/iot-gateway` | iot-gateway | 8106 | IoT gateway operations |
| ALL | `/iot-gateway` | iot-gateway | 8106 | Legacy IoT gateway route |
| ALL | `/api/v1/virtual-sensors` | virtual-sensors | 8119 | Virtual sensor engine |
| ALL | `/virtual-sensors` | virtual-sensors | 8119 | Legacy virtual sensors route |

### Agricultural Intelligence

| Method | Route | Service | Port | Purpose |
|--------|-------|---------|------|---------|
| ALL | `/api/v1/vegetation` | vegetation-analysis-service | 8090 | Vegetation analysis |
| ALL | `/vegetation` | vegetation-analysis-service | 8090 | Legacy vegetation route |
| ALL | `/api/v1/satellite` | vegetation-analysis-service | 8090 | Satellite imagery |
| ALL | `/satellite` | vegetation-analysis-service | 8090 | Legacy satellite route |
| ALL | `/api/v1/ndvi` | vegetation-analysis-service | 8090 | NDVI calculations |
| ALL | `/ndvi` | vegetation-analysis-service | 8090 | Legacy NDVI route |
| ALL | `/api/v1/indicators` | indicators-service | 8091 | Agricultural indicators |
| ALL | `/indicators` | indicators-service | 8091 | Legacy indicators route |
| ALL | `/api/v1/weather` | weather-service | 8092 | Weather data |
| ALL | `/weather` | weather-service | 8092 | Legacy weather route |
| ALL | `/api/v1/advisory` | advisory-service | 8093 | Agricultural advice |
| ALL | `/api/v1/fertilizer` | advisory-service | 8093 | Fertilizer recommendations |
| ALL | `/advisory` | advisory-service | 8093 | Legacy advisory route |
| ALL | `/fertilizer` | advisory-service | 8093 | Legacy fertilizer route |
| ALL | `/api/v1/irrigation` | irrigation-smart | 8094 | Irrigation management |
| ALL | `/irrigation` | irrigation-smart | 8094 | Legacy irrigation route |
| ALL | `/api/v1/crop-health` | crop-intelligence-service | 8095 | Crop health monitoring |
| ALL | `/api/v1/crop` | crop-intelligence-service | 8095 | Crop operations |
| ALL | `/crop` | crop-intelligence-service | 8095 | Legacy crop route |
| ALL | `/api/v1/yield` | yield-prediction-service | 8152 | Yield predictions |
| ALL | `/yield` | yield-prediction-service | 8152 | Legacy yield route |

### AI & Intelligence

| Method | Route | Service | Port | Purpose |
|--------|-------|---------|------|---------|
| ALL | `/api/v1/ai-advisor` | ai-advisor | 8112 | AI agricultural advisor |
| ALL | `/ai-advisor` | ai-advisor | 8112 | Legacy AI advisor route |
| ALL | `/api/v1/ai-agents` | ai-agents-core | 8122 | AI agent infrastructure |
| ALL | `/ai-agents` | ai-agents-core | 8122 | Legacy AI agents route |
| ALL | `/api/v1/ai-agents-service` | ai-agents-service | 8130 | AI agent orchestration |
| ALL | `/ai-agents-service` | ai-agents-service | 8130 | Legacy AI agents service route |
| ALL | `/api/v1/knowledge` | knowledge-graph | 8140 | Knowledge graph |
| ALL | `/knowledge` | knowledge-graph | 8140 | Legacy knowledge route |
| ALL | `/api/v1/field-intelligence` | field-intelligence | 8120 | Field intelligence |
| ALL | `/api/v1/field-core` | field-intelligence | 8120 | Field core operations |
| ALL | `/field-intelligence` | field-intelligence | 8120 | Legacy field intelligence route |

### Business Services

| Method | Route | Service | Port | Purpose |
|--------|-------|---------|------|---------|
| ALL | `/api/v1/billing` | billing-core | 8089 | Billing operations |
| ALL | `/billing` | billing-core | 8089 | Legacy billing route |
| ALL | `/api/v1/inventory` | inventory-service | 8116 | Inventory management |
| ALL | `/inventory` | inventory-service | 8116 | Legacy inventory route |
| ALL | `/api/v1/equipment` | equipment-service | 8101 | Equipment tracking |
| ALL | `/equipment` | equipment-service | 8101 | Legacy equipment route |
| ALL | `/api/v1/tasks` | task-service | 8103 | Task management |
| ALL | `/api/v1/task` | task-service | 8103 | Single task operations |
| ALL | `/task` | task-service | 8103 | Legacy task route |
| ALL | `/api/v1/crm` | crm-service | 8131 | CRM operations |
| ALL | `/crm` | crm-service | 8131 | Legacy CRM route |
| ALL | `/api/v1/globalgap` | globalgap-compliance | 8128 | GlobalGAP compliance |
| ALL | `/globalgap` | globalgap-compliance | 8128 | Legacy GlobalGAP route |
| ALL | `/api/v1/logistics` | logistics-service | 8167 | Logistics operations |
| ALL | `/logistics` | logistics-service | 8167 | Legacy logistics route |

### Notifications & Alerts

| Method | Route | Service | Port | Purpose |
|--------|-------|---------|------|---------|
| ALL | `/api/v1/notifications` | notification-service | 8110 | Notification management |
| ALL | `/api/v1/notification` | notification-service | 8110 | Single notification |
| ALL | `/notification` | notification-service | 8110 | Legacy notification route |
| ALL | `/api/v1/channels` | notification-service | 8110 | Notification channels |
| ALL | `/api/v1/preferences` | notification-service | 8110 | Notification preferences |
| ALL | `/api/v1/alerts` | notification-service | 8110 | Alert management |
| ALL | `/alerts` | notification-service | 8110 | Legacy alerts route |
| ALL | `/api/v1/notification-stats` | notification-service | 8110 | Notification statistics |
| ALL | `/api/v1/reminders` | notification-service | 8110 | Reminder management |
| ALL | `/api/v1/farmers` | notification-service | 8110 | Farmer notifications |

### Utility Services

| Method | Route | Service | Port | Purpose |
|--------|-------|---------|------|---------|
| ALL | `/api/v1/astronomy` | astronomical-calendar | 8111 | Astronomical calculations |
| ALL | `/astronomy` | astronomical-calendar | 8111 | Legacy astronomy route |
| ALL | `/api/v1/provider-config` | provider-config | 8104 | Provider configuration |
| ALL | `/provider-config` | provider-config | 8104 | Legacy provider config route |
| ALL | `/api/v1/skills` | skills-service | 8121 | Skills assessment |
| ALL | `/skills` | skills-service | 8121 | Legacy skills route |
| ALL | `/api/v1/mcp` | mcp-server | 8200 | Model Context Protocol |
| ALL | `/mcp` | mcp-server | 8200 | Legacy MCP route |
| ALL | `/api/v1/ussd` | ussd-gateway | 8163 | USSD gateway |
| ALL | `/ussd` | ussd-gateway | 8163 | Legacy USSD route |
| ALL | `/api/v1/wechat` | wechat-service | 8133 | WeChat integration |
| ALL | `/wechat` | wechat-service | 8133 | Legacy WeChat route |
| ALL | `/api/v1/lowcode` | lowcode-engine | 8132 | Low-code builder |
| ALL | `/lowcode` | lowcode-engine | 8132 | Legacy lowcode route |
| ALL | `/api/v1/agents` | agent-registry | 8160 | Agent registry |
| ALL | `/agents` | agent-registry | 8160 | Legacy agents route |
| ALL | `/api/v1/code-review` | code-review-service | 8102 | Code review |
| ALL | `/code-review` | code-review-service | 8102 | Legacy code review route |
| ALL | `/ws` | ws-gateway | 8081 | WebSocket gateway |

---

## ⚠️ Deprecated Routes (Legacy Support)

| Route | Service | Port | Replacement | Status |
|-------|---------|------|-------------|--------|
| `/yield-legacy` | yield-prediction | 3021 | `/api/v1/yield` → yield-prediction-service:8152 | DEPRECATED |
| `/lai-legacy` | lai-estimation | 3022 | `/api/v1/vegetation` → vegetation-analysis-service:8090 | DEPRECATED |
| `/crop-growth-legacy` | crop-growth-model | 3023 | `/api/v1/crop` → crop-intelligence-service:8095 | DEPRECATED |
| `/field-ops-legacy` | field-ops | 8080 | `/api/v1/fields` → field-management-service:3000 | DEPRECATED |
| `/ndvi-engine-legacy` | ndvi-engine | 8107 | `/api/v1/ndvi` → vegetation-analysis-service:8090 | DEPRECATED |
| `/weather-core-legacy` | weather-core | 8108 | `/api/v1/weather` → weather-service:8092 | DEPRECATED |
| `/ndvi-processor-legacy` | ndvi-processor | 8118 | `/api/v1/ndvi` → vegetation-analysis-service:8090 | DEPRECATED |
| `/field-service-legacy` | field-service | 8115 | `/api/v1/fields` → field-management-service:3000 | DEPRECATED |
| `/agro-advisor-legacy` | agro-advisor | 8105 | `/api/v1/advisory` → advisory-service:8093 | DEPRECATED |
| `/community-chat-legacy` | community-chat | 8097 | `/api/v1/chat` → chat-service:8114 | DEPRECATED |

---

## 🔧 Kong Configuration

### Global Plugins

1. **CORS Plugin**
   - Origins: `*` (development), specific domains (production)
   - Methods: GET, POST, PUT, PATCH, DELETE, OPTIONS
   - Headers: Authorization, Content-Type, X-Request-Id, X-Correlation-Id
   - Credentials: false (development), true (production with specific origins)

2. **Prometheus Plugin**
   - Metrics endpoint: `http://localhost:8001/metrics`
   - Exports: Request count, latency, status codes

3. **Correlation ID Plugin**
   - Header: X-Correlation-Id
   - Generator: uuid#counter
   - Echo downstream: true

4. **Request Size Limiting**
   - Max payload: 10 MB
   - Unit: megabytes

### DNS Configuration

```yaml
KONG_DNS_RESOLVER: 127.0.0.11:53
KONG_DNS_ORDER: LAST,A,CNAME
KONG_DNS_CACHE_TTL: 300
KONG_DNS_STALE_TTL: 30
KONG_DNS_ERROR_TTL: 30
KONG_DNS_NO_SYNC: "off"
KONG_DNS_NOT_FOUND_TTL: 30
```

### Performance Optimization

```yaml
KONG_NGINX_WORKER_PROCESSES: 4    # Fixed: 'auto' caused startup delays on high-core hosts
KONG_NGINX_WORKER_CONNECTIONS: 4096
KONG_NGINX_KEEPALIVE_TIMEOUT: 60s
KONG_NGINX_KEEPALIVE_REQUESTS: 1000
KONG_UPSTREAM_KEEPALIVE_POOL_SIZE: 60
KONG_UPSTREAM_KEEPALIVE_MAX_REQUESTS: 100
KONG_UPSTREAM_KEEPALIVE_IDLE_TIMEOUT: 60
KONG_MEM_CACHE_SIZE: 128m
```

---

## 🐛 Known Issues

### Resolved Port Conflicts (Feb 2026)

All port conflicts have been resolved:
- **audit-service**: 8114 (no longer conflicts with chat-service which uses 8000 internally)
- **agent-registry**: moved to 8160 (was 8121, conflicted with skills-service)
- **globalgap-compliance**: moved to 8128 (was 8123, conflicted with traceability-service)
- **ussd-gateway**: moved to 8183 (was 8180, conflicted with edge-orchestrator)

### Missing Routes

1. **ground-vision-service** (8182) - Not configured in Kong
   - **Recommendation:** Add route `/api/v1/ground-vision`

---

## 📝 Usage Examples

### Admin App Integration

```typescript
// Base API client configuration
const apiClient = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth interceptor
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('accessToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Example: Fetch fields
const fields = await apiClient.get('/api/v1/fields');

// Example: Create notification
const notification = await apiClient.post('/api/v1/notifications', {
  title: 'Weather Alert',
  message: 'Heavy rain expected',
  type: 'weather',
  priority: 'high',
});
```

### WebSocket Connection

```typescript
const ws = new WebSocket('ws://localhost:8081/ws');

ws.onopen = () => {
  console.log('WebSocket connected');
  ws.send(JSON.stringify({
    type: 'subscribe',
    channel: 'field-updates',
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};
```

---

**Last Updated:** 2026-01-30  
**Maintainer:** SAHOOL Platform Team
