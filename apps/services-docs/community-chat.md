> **⚠️ DEPRECATED**: This service has been replaced by `chat-service`. See [chat-service.md](chat-service.md) for current documentation.

---

# Community Chat Service Analysis

## Service Overview

| Property | Value |
|----------|-------|
| **Service Name** | community-chat |
| **Arabic Name** | خدمة الدردشة الحية لمجتمع سهول |
| **Port** | 8097 |
| **Type** | Node.js (Express + Socket.io) |
| **Version** | 16.0.0 (package.json) / 1.0.0 (service version) |
| **Status** | **DEPRECATED** |
| **Replacement** | `chat-service` (Port 8114) |

---

## Deprecation Notice

> **WARNING**: This service has been deprecated. All chat functionality should migrate to `chat-service` (Port 8114).

### Migration Path

| Feature | community-chat | chat-service |
|---------|---------------|--------------|
| Message Storage | In-memory (Map) | PostgreSQL (Prisma) |
| Real-time | Socket.io | Socket.io |
| Read Receipts | Not implemented | Implemented |
| Message Types | TEXT only | TEXT, IMAGE, OFFER, SYSTEM |
| Persistence | Lost on restart | Permanent |
| Framework | Express.js | NestJS |

### Migration Timeline

- **Deprecation Date**: As per README, migrating to chat-service
- **Replacement Service**: `/home/user/sahool-unified-v15-idp/apps/services/chat-service/`

---

## Kong Gateway Configuration

### Routes

| Route Path | Strip Path | Protocols |
|-----------|------------|-----------|
| `/api/v1/community` | true | HTTP, HTTPS |
| `/api/v1/posts` | true | HTTP, HTTPS |
| `/community` | true | HTTP, HTTPS |
| `/community-chat-legacy` | true | HTTP, HTTPS |

### Service Configuration

```yaml
- name: community-chat
  host: community-chat
  port: 8097
  protocol: http
```

---

## REST API Endpoints

### Health & Monitoring

#### GET /healthz
Health check endpoint for liveness probes.

**Response Schema:**
```json
{
  "status": "healthy",
  "service": "community-chat",
  "version": "1.0.0",
  "activeConnections": 42,
  "onlineExperts": 5,
  "activeRooms": 12,
  "timestamp": "2025-12-27T10:30:00.000Z"
}
```

---

### Support Requests

#### GET /v1/requests
Retrieve all active support requests with optional status filter.

**Query Parameters:**
| Parameter | Type | Required | Values |
|-----------|------|----------|--------|
| `status` | string | No | `pending`, `active`, `resolved`, `closed` |

**Response Schema:**
```json
[
  {
    "roomId": "support_12345_1735295400000",
    "farmerId": "12345",
    "farmerName": "محمد أحمد",
    "governorate": "القاهرة",
    "topic": "مرض في نباتات الطماطم",
    "diagnosisId": "diag_98765",
    "status": "pending",
    "createdAt": "2025-12-27T10:30:00.000Z",
    "expertId": null,
    "expertName": null,
    "acceptedAt": null
  }
]
```

---

### Room Management

#### GET /v1/rooms/:roomId/messages
Retrieve message history for a specific chat room.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `roomId` | string | Unique room identifier |

**Response Schema:**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "roomId": "support_12345_1735295400000",
    "author": "محمد أحمد",
    "authorType": "farmer",
    "message": "السلام عليكم، أحتاج استشارة",
    "attachments": [],
    "timestamp": "2025-12-27T10:30:00.000Z",
    "status": "delivered"
  }
]
```

---

### Expert Management

#### GET /v1/experts/online
Get count of currently online experts.

**Response Schema:**
```json
{
  "count": 5,
  "available": true
}
```

---

### Statistics

#### GET /v1/stats
Get comprehensive service statistics.

**Response Schema:**
```json
{
  "totalConnections": 42,
  "onlineExperts": 5,
  "activeRooms": 12,
  "totalMessages": 1548,
  "timestamp": "2025-12-27T10:30:00.000Z"
}
```

---

### Documentation Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api-docs` | Swagger UI interactive documentation |
| `GET /api-docs.json` | OpenAPI 3.0 JSON specification |
| `GET /redoc` | ReDoc documentation viewer |

---

## WebSocket Events (Socket.io)

### Connection

```javascript
const io = require('socket.io-client');
const socket = io('http://localhost:8097', {
  auth: { token: 'your-jwt-token' }
});
```

### Client-to-Server Events

#### `register_user`
Register user on connection.

**Payload:**
```json
{
  "userId": "12345",
  "userName": "محمد أحمد",
  "userNameAr": "محمد أحمد",
  "userType": "farmer|expert|admin|support",
  "governorate": "القاهرة"
}
```

**Response Event:** `registration_confirmed`
```json
{
  "success": true,
  "socketId": "abc123def456",
  "onlineExperts": 5
}
```

---

#### `join_room`
Join a chat room.

**Payload:**
```json
{
  "roomId": "support_12345_1735295400000",
  "userName": "محمد أحمد",
  "userType": "farmer|expert|admin|support"
}
```

**Response Events:**
- `load_history` - Array of previous messages
- `user_joined` (broadcast to room)
- `error` - If access denied

**Validation Rules:**
- `roomId`: Max 100 characters
- `userName`: Max 100 characters
- `userType`: Must be `farmer`, `expert`, `admin`, or `support`

---

#### `send_message`
Send a message to a room.

**Payload:**
```json
{
  "roomId": "support_12345_1735295400000",
  "author": "محمد أحمد",
  "authorType": "farmer|expert|admin|support|system",
  "message": "السلام عليكم، أحتاج استشارة",
  "attachments": [
    {
      "url": "https://sahool.io/uploads/image123.jpg",
      "type": "image",
      "name": "plant_disease.jpg",
      "size": 245678
    }
  ]
}
```

**Response Event:** `receive_message` (broadcast to room)

**Validation Rules:**
- `message`: Max 10,000 characters
- `attachments`: Max 10 items
- URL whitelist: `sahool.io`, `sahool.app`, `localhost`
- XSS prevention: `<`, `>`, `"`, `'` are escaped

---

#### `typing_start` / `typing_stop`
Typing indicator events.

**Payload:**
```json
{
  "roomId": "support_12345_1735295400000",
  "userName": "محمد أحمد"
}
```

**Response Event:** `user_typing` (broadcast to room)
```json
{
  "userName": "محمد أحمد",
  "isTyping": true|false
}
```

---

#### `request_expert`
Farmer requests expert assistance.

**Payload:**
```json
{
  "farmerId": "12345",
  "farmerName": "محمد أحمد",
  "governorate": "القاهرة",
  "topic": "مرض في نباتات الطماطم",
  "diagnosisId": "diag_98765"
}
```

**Response Events:**
- `expert_request_created` - Confirmation to farmer
- `new_support_request` (broadcast to all) - Notify experts

---

#### `accept_request`
Expert accepts a support request.

**Payload:**
```json
{
  "roomId": "support_12345_1735295400000",
  "expertId": "expert_123",
  "expertName": "د. أحمد الخبير"
}
```

**Response Events:**
- `expert_joined` (to room)
- `request_taken` (broadcast to all experts)

---

#### `leave_room`
Leave a chat room.

**Payload:**
```json
{
  "roomId": "support_12345_1735295400000",
  "userName": "محمد أحمد"
}
```

**Response Event:** `user_left` (broadcast to room)

---

### Server-to-Client Events

| Event | Trigger | Payload |
|-------|---------|---------|
| `registration_confirmed` | After `register_user` | `{success, socketId, onlineExperts}` |
| `expert_online` | Expert registers | `{expertId, expertName}` |
| `expert_offline` | Expert disconnects | `{expertId}` |
| `load_history` | After `join_room` | Array of messages |
| `user_joined` | User joins room | `{userName, userType, time}` |
| `user_left` | User leaves room | `{userName, time}` |
| `receive_message` | Message sent | Message object |
| `user_typing` | Typing indicator | `{userName, isTyping}` |
| `new_support_request` | Expert requested | SupportRequest object |
| `expert_request_created` | Request confirmed | `{success, roomId, message}` |
| `expert_joined` | Expert accepts | `{expertId, expertName, message}` |
| `request_taken` | Request accepted | `{roomId, expertName}` |
| `error` | Validation failure | `{code, message}` |

---

### Error Codes

| Code | Arabic Message | Description |
|------|---------------|-------------|
| `INVALID_ROOM_ID` | معرف الغرفة غير صالح | Room ID validation failed |
| `INVALID_USERNAME` | اسم المستخدم غير صالح | Username validation failed |
| `INVALID_USER_TYPE` | نوع المستخدم غير صالح | Invalid user type |
| `INVALID_AUTHOR` | اسم المؤلف غير صالح | Author validation failed |
| `INVALID_MESSAGE` | محتوى الرسالة غير صالح | Message content invalid |
| `MESSAGE_TOO_LONG` | الرسالة طويلة جداً | Exceeds 10,000 chars |
| `ACCESS_DENIED` | لا يمكنك الوصول لهذه الغرفة | Room access denied |

---

## NATS Events

> **Note**: Despite `NATS_URL` being configured in docker-compose, the current implementation does NOT use NATS. All real-time communication is handled via Socket.io only.

### Events NOT Implemented (Potential Future)

The service could publish/subscribe to:
- `sahool.{tenant_id}.chat.message.sent`
- `sahool.{tenant_id}.chat.room.created`
- `sahool.{tenant_id}.chat.expert.requested`
- `sahool.{tenant_id}.chat.expert.assigned`

---

## Dependencies

### NPM Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `express` | ^4.21.2 | HTTP server framework |
| `socket.io` | ^4.8.1 | Real-time WebSocket communication |
| `cors` | ^2.8.5 | Cross-Origin Resource Sharing |
| `uuid` | ^11.0.3 | UUID generation for messages |
| `jsonwebtoken` | ^9.0.2 | JWT authentication |
| `swagger-jsdoc` | ^6.2.8 | OpenAPI spec generation |
| `swagger-ui-express` | ^5.0.0 | Swagger UI serving |
| `js-yaml` | ^4.1.0 | YAML parsing for OpenAPI |

### Dev Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `nodemon` | ^3.1.9 | Development auto-reload |

### Runtime Requirements

- Node.js >= 20.0.0

---

## Infrastructure Dependencies

| Service | Purpose | Connection |
|---------|---------|------------|
| PostgreSQL | Database (via PgBouncer) | `DATABASE_URL` (configured but NOT used) |
| Redis | Caching/Sessions | `REDIS_URL` (configured but NOT used) |
| NATS | Event messaging | `NATS_URL` (configured but NOT used) |

> **Important**: The current implementation uses in-memory storage only. PostgreSQL, Redis, and NATS connections are configured in docker-compose but not utilized by the service code.

---

## Environment Variables

### Required

| Variable | Description | Example |
|----------|-------------|---------|
| `JWT_SECRET_KEY` | **REQUIRED** - JWT signing key (min 32 chars) | `your-secret-key-minimum-32-characters-long` |

### Optional

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Service port | `8097` |
| `NODE_ENV` | Environment mode | `development` |
| `CORS_ORIGINS` | Comma-separated allowed origins | `https://sahool.io,https://admin.sahool.io,https://app.sahool.io,http://localhost:3000,http://localhost:3001` |

### Configured but NOT Used

| Variable | Description | Notes |
|----------|-------------|-------|
| `DATABASE_URL` | PostgreSQL connection | In-memory storage used instead |
| `REDIS_URL` | Redis connection | Not implemented |
| `NATS_URL` | NATS connection | Not implemented |

---

## Security Features

### Authentication

- JWT token required for all WebSocket connections
- Token passed via `auth.token` or `query.token`
- Strict algorithm whitelist: `HS256`, `HS384`, `HS512`, `RS256`, `RS384`, `RS512`
- `none` algorithm explicitly rejected
- Token must contain `sub` (subject) and `role` claims

### Input Validation

| Check | Implementation |
|-------|---------------|
| XSS Prevention | HTML entities escaped (`<`, `>`, `"`, `'`) |
| Message Length | Max 10,000 characters |
| Room ID Length | Max 100 characters |
| Username Length | Max 100 characters |
| Attachment URLs | Whitelisted domains only |
| User Types | Validated against enum |

### Access Control

- Support rooms (`support_*`): Only original farmer, assigned expert, or admin can join
- Role verification from JWT token
- Connection attempts without token are rejected

### CORS Configuration

```javascript
origin: [
  "https://sahool.io",
  "https://admin.sahool.io",
  "https://app.sahool.io",
  "http://localhost:3000",
  "http://localhost:3001"
]
```

---

## Docker Configuration

### Dockerfile

- **Base Image**: `node:20-alpine`
- **Multi-stage Build**: Yes (builder + production)
- **Non-root User**: `nodejs` (UID 1001)
- **Health Check**: HTTP GET to `/healthz` every 30s

### Resource Limits (docker-compose)

| Resource | Limit |
|----------|-------|
| CPU | 0.5 cores |
| Memory | 384 MB |

### Health Check Configuration

```yaml
test: ["CMD", "curl", "-f", "http://localhost:8097/healthz"]
interval: 30s
timeout: 10s
retries: 3
start_period: 15s
```

---

## In-Memory Storage

> **Warning**: All data is lost on service restart.

| Storage | Type | Max Items |
|---------|------|-----------|
| `messageHistory` | `Map<roomId, Message[]>` | 500 messages per room |
| `activeUsers` | `Map<socketId, User>` | Unlimited |
| `rooms` | `Map<roomId, RoomMetadata>` | Unlimited |
| `onlineExperts` | `Set<socketId>` | Unlimited |

---

## File Structure

```
apps/services/community-chat/
├── Dockerfile                 # Multi-stage Docker build
├── package.json               # NPM dependencies
├── package-lock.json          # Dependency lock file
├── openapi.yaml               # OpenAPI 3.0 specification
├── postman_collection.json    # Postman API collection
├── README.md                  # Service documentation (DEPRECATED notice)
├── QUICK_START.md             # Quick start guide
├── CHANGELOG.md               # Version history
├── API_DOCUMENTATION.md       # Detailed API docs
├── .dockerignore              # Docker ignore patterns
├── src/
│   ├── index.js               # Main application entry point
│   └── swagger.js             # Swagger/OpenAPI configuration
├── test/
│   └── chat.spec.js           # Unit tests
└── examples/
    ├── README.md              # Examples documentation
    ├── client-example.js      # Socket.io client example
    └── package.json           # Examples dependencies
```

---

## Known Issues & Limitations

### Critical

1. **No Data Persistence**: Messages stored in memory only
2. **No Horizontal Scaling**: Single instance limitation
3. **No Message Encryption**: Messages stored/transmitted in plaintext
4. **Unused Infrastructure**: DATABASE_URL, REDIS_URL, NATS_URL configured but not used

### Moderate

1. **No Rate Limiting**: Potential DoS vulnerability
2. **No Message Pagination**: All history loaded at once
3. **No File Upload**: Only URL attachments supported
4. **No Message Editing/Deletion**: Once sent, cannot be modified

### Minor

1. **No Read Receipts**: Cannot track message read status
2. **No Offline Message Queue**: Messages lost if recipient offline
3. **No Search**: Cannot search message history
4. **Test Coverage**: Tests use mock implementation, not actual service

---

## Recommendations

### Immediate Actions

1. **Migrate to chat-service**: The replacement service at port 8114 provides:
   - PostgreSQL persistence
   - Read receipts
   - Multiple message types
   - Proper NestJS architecture

2. **Add Deprecation Logging**: Log deprecation warnings at startup

3. **Document Migration Path**: Create detailed migration guide for clients

### If Maintaining This Service

1. **Implement Redis**: For session storage and message persistence
2. **Implement NATS**: For event-driven architecture integration
3. **Add Rate Limiting**: Prevent abuse and DoS
4. **Add Message Pagination**: Implement cursor-based pagination
5. **Add Monitoring**: Prometheus metrics endpoint

---

## Related Services

| Service | Port | Relationship |
|---------|------|--------------|
| `chat-service` | 8114 | **Replacement** - Use this instead |
| `field-chat` | 8099 | Deprecated, redirects to community-chat |
| `community_service` | N/A | Deprecated, merged into community-chat |
| `notification-service` | 8110 | Could integrate for push notifications |
| `ws-gateway` | 8081 | WebSocket gateway for platform |

---

## Service Registry Entry

From `/home/user/sahool-unified-v15-idp/config/service-registry.yaml`:

```yaml
community_chat:
  layer: communication
  port: 8097
  path: "apps/services/community-chat"
  language: nodejs
  framework: nestjs  # Note: Actually Express, not NestJS
  description: "الدردشة المجتمعية الزراعية"
  description_en: "Agricultural community chat"
  realtime: true
  websocket: true
  endpoints:
    health: "/healthz"
    ws: "/ws"
```

---

## Version History

- **16.0.0** (package.json): Current package version
- **1.0.0** (service): Initial service release
- **Deprecation**: Announced in README, migrating to chat-service

---

*Document Generated: 2026-01-25*
*Source: `/home/user/sahool-unified-v15-idp/apps/services/community-chat/`*
