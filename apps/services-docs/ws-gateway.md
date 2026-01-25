# ws-gateway Microservice Analysis

**Service Name**: WebSocket Gateway
**Type**: Python/FastAPI
**Port**: 8081
**Version**: 16.0.0
**Location**: `/home/user/sahool-unified-v15-idp/apps/services/ws-gateway/`

---

## Table of Contents

1. [Service Overview](#service-overview)
2. [Architecture](#architecture)
3. [WebSocket Endpoints](#websocket-endpoints)
4. [REST API Endpoints](#rest-api-endpoints)
5. [Message Formats](#message-formats)
6. [NATS Events](#nats-events)
7. [Room Management](#room-management)
8. [Dependencies](#dependencies)
9. [Environment Variables](#environment-variables)
10. [Security](#security)
11. [Bugs and Recommended Fixes](#bugs-and-recommended-fixes)

---

## Service Overview

The **ws-gateway** service is the real-time communication hub for the SAHOOL platform. It provides:

- WebSocket connections for real-time bidirectional communication
- Room-based message routing for targeted delivery
- NATS-to-WebSocket bridging for platform event distribution
- REST API for server-to-client message broadcasting
- Multi-tenant support with JWT authentication

### Key Features

| Feature | Description |
|---------|-------------|
| Real-time messaging | Full-duplex WebSocket communication |
| Room system | Hierarchical rooms (tenant, user, field, farm, chat, alerts, weather) |
| NATS bridge | Subscribes to 11 NATS event categories and forwards to WebSocket clients |
| Bilingual | Arabic and English message support |
| Event priorities | LOW, MEDIUM, HIGH, CRITICAL priority levels |

---

## Architecture

```
                                   +------------------+
                                   |   Kong Gateway   |
                                   |  (Route: /ws)    |
                                   +--------+---------+
                                            |
                                            v
+------------------+              +------------------+              +------------------+
|   NATS Server    | <----------> |   ws-gateway     | <----------> |   WebSocket      |
|   (pub/sub)      |   events     |   (Port 8081)    |  bidirectional|   Clients        |
+------------------+              +--------+---------+              +------------------+
                                            |
                                            v
                                   +------------------+
                                   |   Room Manager   |
                                   |  - Connections   |
                                   |  - Rooms         |
                                   |  - Metadata      |
                                   +------------------+
```

### Source Files

| File | Purpose |
|------|---------|
| `src/main.py` | FastAPI application, WebSocket endpoint, broadcast API |
| `src/handlers.py` | WebSocket message handlers for client messages |
| `src/events.py` | Event type definitions with bilingual messages |
| `src/nats_bridge.py` | NATS subscription and event routing to WebSocket |
| `src/rooms.py` | Room and connection management |

---

## WebSocket Endpoints

### Main WebSocket Endpoint

**URL**: `GET /ws`

**Query Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tenant_id` | string | Yes | Tenant identifier |
| `token` | string | No (deprecated) | JWT token for authentication |

**Headers** (preferred for authentication):

| Header | Value | Description |
|--------|-------|-------------|
| `Authorization` | `Bearer <token>` | JWT token (preferred over query param) |

**Connection Flow**:

1. Client connects with `tenant_id` and JWT token
2. Server validates JWT and checks tenant match
3. On success: WebSocket is accepted, connection added to room manager
4. Client receives connection confirmation message
5. Client is auto-joined to tenant and user rooms

**Connection Confirmation Message**:

```json
{
  "type": "connected",
  "connection_id": "uuid-v4",
  "user_id": "user-123",
  "tenant_id": "tenant-456",
  "timestamp": "2026-01-25T10:30:00.000Z",
  "message_ar": "تم الاتصال بنجاح"
}
```

**WebSocket Close Codes**:

| Code | Reason |
|------|--------|
| 4001 | Authentication required / Invalid authentication token |
| 4003 | Tenant mismatch |

---

## REST API Endpoints

### Health Check

**Endpoint**: `GET /healthz`

**Response**:

```json
{
  "status": "healthy",
  "service": "ws-gateway",
  "version": "16.0.0",
  "nats_connected": true,
  "connections": {
    "total_connections": 25,
    "total_rooms": 10
  },
  "timestamp": "2026-01-25T10:30:00.000Z"
}
```

**Note**: Status is `degraded` if NATS is not connected, but service remains operational.

---

### Readiness Check

**Endpoint**: `GET /readyz`

**Response**:

```json
{
  "status": "ok",
  "nats": true,
  "connections": {
    "total_connections": 25,
    "total_rooms": 10
  }
}
```

---

### Statistics

**Endpoint**: `GET /stats`

**Response**:

```json
{
  "connections": {
    "total_connections": 25,
    "total_rooms": 10,
    "rooms": {
      "tenant:tenant-123": {
        "type": "tenant",
        "connections": 15,
        "created_at": "2026-01-25T10:00:00.000Z"
      }
    },
    "connections_by_room_type": {
      "tenant": 25,
      "user": 25,
      "field": 10
    }
  },
  "nats": {
    "connected": true,
    "subscriptions": 11
  },
  "timestamp": "2026-01-25T10:30:00.000Z"
}
```

---

### Broadcast Message

**Endpoint**: `POST /broadcast`

**Headers**:

| Header | Value | Required |
|--------|-------|----------|
| `Authorization` | `Bearer <token>` | Yes |
| `Content-Type` | `application/json` | Yes |

**Request Body**:

```json
{
  "tenant_id": "tenant-456",
  "user_id": "user-123",
  "field_id": "field-789",
  "room": "custom-room",
  "message": {
    "type": "notification",
    "title": "Alert",
    "body": "Important update"
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `tenant_id` | string | No | Broadcast to all users in tenant |
| `user_id` | string | No | Broadcast to specific user |
| `field_id` | string | No | Broadcast to field watchers |
| `room` | string | No | Broadcast to specific room |
| `message` | object | Yes | Message payload |

**Note**: Specify one of `tenant_id`, `user_id`, `field_id`, or `room`.

**Response**:

```json
{
  "status": "sent",
  "recipients": 10,
  "timestamp": "2026-01-25T10:30:00.000Z"
}
```

**Authorization Rules**:
- Users can only broadcast to their own tenant
- `super_admin` role can broadcast to any tenant

---

## Message Formats

### Client-to-Server Messages

#### Subscribe to Topics

```json
{
  "type": "subscribe",
  "topics": ["field:field-123", "weather", "alerts"]
}
```

**Response**:

```json
{
  "type": "subscribed",
  "topics": ["field:field-123", "weather", "alerts"],
  "failed": [],
  "timestamp": "2026-01-25T10:30:00.000Z",
  "message_ar": "تم الاشتراك في 3 موضوع"
}
```

---

#### Unsubscribe from Topics

```json
{
  "type": "unsubscribe",
  "topics": ["field:field-123"]
}
```

**Response**:

```json
{
  "type": "unsubscribed",
  "topics": ["field:field-123"],
  "timestamp": "2026-01-25T10:30:00.000Z",
  "message_ar": "تم إلغاء الاشتراك من 1 موضوع"
}
```

---

#### Ping (Heartbeat)

```json
{
  "type": "ping"
}
```

**Response**:

```json
{
  "type": "pong",
  "timestamp": "2026-01-25T10:30:00.000Z"
}
```

---

#### Broadcast to Room

```json
{
  "type": "broadcast",
  "room": "field:field-123",
  "message": {
    "content": "Hello everyone!"
  }
}
```

**Response**:

```json
{
  "type": "broadcast_sent",
  "room": "field:field-123",
  "recipients": 5,
  "timestamp": "2026-01-25T10:30:00.000Z"
}
```

**Broadcast Message (to other clients)**:

```json
{
  "type": "message",
  "room": "field:field-123",
  "from": {
    "connection_id": "uuid-v4",
    "user_id": "user-123"
  },
  "message": {
    "content": "Hello everyone!"
  },
  "timestamp": "2026-01-25T10:30:00.000Z"
}
```

---

#### Join Room

```json
{
  "type": "join_room",
  "room": "field:field-123"
}
```

**Response**:

```json
{
  "type": "room_joined",
  "room": "field:field-123",
  "timestamp": "2026-01-25T10:30:00.000Z",
  "message_ar": "تم الانضمام للغرفة"
}
```

---

#### Leave Room

```json
{
  "type": "leave_room",
  "room": "field:field-123"
}
```

**Response**:

```json
{
  "type": "room_left",
  "room": "field:field-123",
  "timestamp": "2026-01-25T10:30:00.000Z",
  "message_ar": "تم مغادرة الغرفة"
}
```

---

#### Typing Indicator

```json
{
  "type": "typing",
  "room": "chat:room-456",
  "typing": true
}
```

**Response**:

```json
{
  "type": "typing_sent",
  "room": "chat:room-456"
}
```

**Broadcast to Room**:

```json
{
  "type": "chat.typing",
  "room": "chat:room-456",
  "user_id": "user-123",
  "typing": true,
  "timestamp": "2026-01-25T10:30:00.000Z"
}
```

---

#### Read Receipt

```json
{
  "type": "read",
  "room": "chat:room-456",
  "message_id": "msg-789"
}
```

**Response**:

```json
{
  "type": "read_sent",
  "room": "chat:room-456",
  "message_id": "msg-789"
}
```

**Broadcast to Room**:

```json
{
  "type": "chat.read",
  "room": "chat:room-456",
  "message_id": "msg-789",
  "user_id": "user-123",
  "timestamp": "2026-01-25T10:30:00.000Z"
}
```

---

### Error Response Format

```json
{
  "type": "error",
  "error": "Error message in English",
  "message_ar": "رسالة الخطأ بالعربية"
}
```

---

## NATS Events

### Subscribed Subjects

The service subscribes to the following NATS subject patterns:

| Subject Pattern | Handler | Description |
|-----------------|---------|-------------|
| `sahool.fields.>` | `_handle_field_event` | Field CRUD events |
| `sahool.weather.>` | `_handle_weather_event` | Weather updates and alerts |
| `sahool.satellite.>` | `_handle_satellite_event` | Satellite imagery processing |
| `sahool.ndvi.>` | `_handle_ndvi_event` | NDVI analysis results |
| `sahool.inventory.>` | `_handle_inventory_event` | Stock level changes |
| `sahool.crop.>` | `_handle_crop_event` | Crop health events |
| `sahool.spray.>` | `_handle_spray_event` | Spray timing events |
| `sahool.chat.>` | `_handle_chat_event` | Chat messages |
| `sahool.tasks.>` | `_handle_task_event` | Task management |
| `sahool.iot.>` | `_handle_iot_event` | IoT sensor data |
| `sahool.alerts.>` | `_handle_alert_event` | General alerts |

### Event Types and Routing

#### Field Events

| NATS Subject | WebSocket Event Type | Routing |
|--------------|---------------------|---------|
| `sahool.fields.{field_id}.created` | `field.created` | Field room + Tenant room |
| `sahool.fields.{field_id}.updated` | `field.updated` | Field room + Tenant room |
| `sahool.fields.{field_id}.deleted` | `field.deleted` | Field room + Tenant room |

---

#### Weather Events

| NATS Subject | WebSocket Event Type | Routing |
|--------------|---------------------|---------|
| `sahool.weather.*` | `weather.updated` | Weather room + Tenant room |
| `sahool.weather.*.alert` | `weather.alert` | Weather room + Alerts room + Tenant room |

---

#### Satellite Events

| NATS Subject | WebSocket Event Type | Routing |
|--------------|---------------------|---------|
| `sahool.satellite.*.ready` | `satellite.ready` | Field room + Tenant room |
| `sahool.satellite.*.processing` | `satellite.processing` | Field room + Tenant room |
| `sahool.satellite.*.failed` | `satellite.failed` | Field room + Tenant room |

---

#### NDVI Events

| NATS Subject | WebSocket Event Type | Routing |
|--------------|---------------------|---------|
| `sahool.ndvi.*` | `ndvi.updated` | Field room + Tenant room |
| `sahool.ndvi.*.analysis` | `ndvi.analysis.ready` | Field room + Tenant room |

---

#### Inventory Events

| NATS Subject | WebSocket Event Type | Routing |
|--------------|---------------------|---------|
| `sahool.inventory.*` | `inventory.updated` | Tenant room |
| `sahool.inventory.*.low_stock` | `inventory.low_stock` | Tenant room + Alerts room |
| `sahool.inventory.*.out_of_stock` | `inventory.out_of_stock` | Tenant room + Alerts room |

---

#### Crop Health Events

| NATS Subject | WebSocket Event Type | Routing |
|--------------|---------------------|---------|
| `sahool.crop.*` | `crop.health.alert` | Field room + Tenant room + Alerts room |
| `sahool.crop.*.disease` | `crop.disease.detected` | Field room + Tenant room + Alerts room |
| `sahool.crop.*.pest` | `crop.pest.detected` | Field room + Tenant room + Alerts room |

---

#### Spray Events

| NATS Subject | WebSocket Event Type | Routing |
|--------------|---------------------|---------|
| `sahool.spray.*` | `spray.scheduled` | Field room + Tenant room |
| `sahool.spray.*.window` | `spray.window.optimal` | Field room + Tenant room |
| `sahool.spray.*.warning` | `spray.window.warning` | Field room + Tenant room |

---

#### Chat Events

| NATS Subject | WebSocket Event Type | Routing |
|--------------|---------------------|---------|
| `sahool.chat.*` | `chat.message` | Chat room |
| `sahool.chat.*.typing` | `chat.typing` | Chat room |
| `sahool.chat.*.read` | `chat.read` | Chat room |

---

#### Task Events

| NATS Subject | WebSocket Event Type | Routing |
|--------------|---------------------|---------|
| `sahool.tasks.*.created` | `task.created` | Assigned user room + Tenant room |
| `sahool.tasks.*` | `task.updated` | Assigned user room + Tenant room |
| `sahool.tasks.*.completed` | `task.completed` | Assigned user room + Tenant room |
| `sahool.tasks.*.overdue` | `task.overdue` | Assigned user room + Tenant room |

---

#### IoT Events

| NATS Subject | WebSocket Event Type | Routing |
|--------------|---------------------|---------|
| `sahool.iot.*` | `iot.reading` | Field room + Tenant room |
| `sahool.iot.*.alert` | `iot.alert` | Field room + Tenant room + Alerts room |
| `sahool.iot.*.offline` | `iot.offline` | Field room + Tenant room + Alerts room |

---

#### Alert Events

| NATS Subject | WebSocket Event Type | Routing |
|--------------|---------------------|---------|
| `sahool.alerts.*` | `system.notification` | Alerts room + Tenant room + User room |

---

### WebSocket Event Message Format

All NATS events are transformed to this WebSocket format:

```json
{
  "type": "event",
  "event_type": "field.updated",
  "priority": "low",
  "message": "Field data updated",
  "message_ar": "تم تحديث بيانات الحقل",
  "data": {
    "field_id": "field-123",
    "tenant_id": "tenant-456",
    "changes": {}
  },
  "subject": "sahool.fields.field-123.updated",
  "timestamp": "2026-01-25T10:30:00.000Z"
}
```

---

### Event Priority Levels

| Priority | Events |
|----------|--------|
| **CRITICAL** | (none defined) |
| **HIGH** | `weather.alert`, `crop.disease.detected`, `crop.pest.detected`, `inventory.out_of_stock`, `iot.alert` |
| **MEDIUM** | `task.overdue`, `inventory.low_stock`, `spray.window.warning` |
| **LOW** | `satellite.ready`, `chat.message`, and all others |

---

## Room Management

### Room Types

| Type | Prefix | Description | Auto-Join |
|------|--------|-------------|-----------|
| `tenant` | `tenant:` | All users in a tenant | Yes |
| `user` | `user:` | Specific user's connections | Yes |
| `field` | `field:` | Field watchers | No |
| `farm` | `farm:` | Farm watchers | No |
| `chat` | `chat:` | Chat rooms | No |
| `alerts` | `alerts` | Global alerts room | No |
| `weather` | `weather` | Weather updates room | No |
| `global` | `global:` | Global rooms | No |

### Room Access Validation

| Topic Type | Access Rule |
|------------|-------------|
| `alerts`, `weather`, `global` | Always allowed |
| `tenant:{id}` | Only if tenant matches |
| `user:{id}` | Only if user matches |
| `field:{id}`, `farm:{id}` | Simplified (always allowed - see bugs) |

### Room Lifecycle

- **Creation**: Rooms are created on first join
- **Persistence**: `tenant:*` and `global:*` rooms persist even when empty
- **Cleanup**: Other empty rooms are automatically deleted

---

## Dependencies

### Python Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `fastapi` | 0.126.0 | Web framework |
| `starlette` | >=0.49.1 | ASGI framework |
| `uvicorn[standard]` | >=0.30.0,<1.0.0 | ASGI server |
| `pydantic` | 2.9.2 | Data validation |
| `httpx` | 0.28.1 | HTTP client |
| `python-dotenv` | 1.0.1 | Environment loading |
| `nats-py` | 2.9.0 | NATS messaging |
| `python-jose[cryptography]` | >=3.4.0 | JWT handling |
| `websockets` | 14.1 | WebSocket protocol |
| `python-dateutil` | 2.8.2 | Date utilities |
| `structlog` | >=24.1.0 | Structured logging |

### Unused Dependencies (in requirements.txt)

| Package | Version | Status |
|---------|---------|--------|
| `asyncpg` | 0.30.0 | Not used (no DB access) |
| `tortoise-orm` | 0.21.7 | Not used (no DB access) |
| `redis` | 5.2.1 | Not used (see bugs) |
| `passlib[bcrypt]` | 1.7.4 | Not used |

### Infrastructure Dependencies

| Service | Required | Description |
|---------|----------|-------------|
| NATS | Optional | Event messaging (degraded mode without) |
| Redis | Configured but unused | See bugs section |

---

## Environment Variables

### Currently Used

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PORT` | No | `8081` | HTTP/WebSocket port |
| `NATS_URL` | No | - | NATS server URL (e.g., `nats://nats:4222`) |
| `JWT_SECRET_KEY` | Yes | - | JWT signing secret |
| `JWT_SECRET` | No | - | Fallback for JWT_SECRET_KEY |

### Configured but NOT Used

| Variable | Status | Notes |
|----------|--------|-------|
| `REDIS_URL` | Not used | Redis dependency exists but not utilized |
| `JWT_ALGORITHM` | Not used | Hardcoded whitelist for security |
| `LOG_LEVEL` | Not used | Hardcoded to INFO |
| `ENVIRONMENT` | Not used | No environment-specific logic |
| `CORS_ALLOWED_ORIGINS` | Not used | No CORS middleware configured |

### Recommended Missing Variables

| Variable | Purpose |
|----------|---------|
| `MAX_CONNECTIONS` | Limit total WebSocket connections |
| `HEARTBEAT_INTERVAL` | Client ping/pong timeout |
| `MESSAGE_MAX_SIZE` | WebSocket message size limit |

---

## Security

### Authentication

- JWT token required for WebSocket connections
- Token can be passed via:
  - `Authorization: Bearer <token>` header (preferred)
  - `token` query parameter (deprecated)
- Tenant ID in token must match requested tenant

### JWT Algorithm Whitelist

Hardcoded for security (prevents algorithm confusion attacks):

```python
ALLOWED_ALGORITHMS = ["HS256", "HS384", "HS512", "RS256", "RS384", "RS512"]
```

The `none` algorithm is explicitly rejected.

### Authorization

- Users can only broadcast to their own tenant
- `super_admin` role bypasses tenant restriction
- Room access validated based on topic type and user/tenant ownership

---

## Bugs and Recommended Fixes

### BUG-001: Redis Dependency Not Used

**Severity**: Low
**Location**: `requirements.txt`, `docker-compose.yml`

**Description**: Redis is listed as a dependency and configured in docker-compose, but the code never uses Redis. This appears to be preparation for distributed room state but is incomplete.

**Impact**: Unnecessary dependency, potential confusion, connection to Redis never established.

**Recommended Fix**:
- Either implement Redis for distributed room state (for horizontal scaling)
- Or remove Redis from requirements.txt and docker-compose configuration

---

### BUG-002: Field/Farm Access Validation Incomplete

**Severity**: Medium
**Location**: `src/handlers.py:366-367`

**Description**: The `_validate_topic_access` method returns `True` for all field and farm rooms without verifying ownership.

```python
# Current code:
if topic_type in [RoomType.FIELD, RoomType.FARM]:
    return True  # Simplified - add proper validation
```

**Impact**: Any authenticated user can subscribe to any field or farm room, potentially accessing data from other tenants.

**Recommended Fix**:
- Implement database lookup to verify field/farm belongs to user's tenant
- Or validate against a cached field ownership map

---

### BUG-003: Connection Not Cleaned Up on Send Failure

**Severity**: Medium
**Location**: `src/rooms.py:242-243`

**Description**: When `_send_to_connection` fails, there's a comment "Schedule cleanup" but no implementation.

```python
except Exception as e:
    logger.error(f"Failed to send to {connection_id}: {e}")
    # Schedule cleanup  <-- Not implemented
    return False
```

**Impact**: Dead connections may accumulate, consuming memory and causing repeated failed send attempts.

**Recommended Fix**:
- Track failed sends per connection
- Remove connection after N consecutive failures
- Or immediately call `remove_connection` on critical errors

---

### BUG-004: Deprecated datetime.utcnow() Usage

**Severity**: Low
**Location**: Multiple files

**Description**: `datetime.utcnow()` is deprecated in Python 3.12+. Should use `datetime.now(timezone.utc)`.

**Files affected**:
- `src/main.py`: lines 145, 261, 336, 362
- `src/handlers.py`: lines 118, 142, 152, 197, 209, etc.
- `src/rooms.py`: line 39, 99
- `src/nats_bridge.py`: line 447

**Recommended Fix**:
```python
from datetime import datetime, timezone

# Replace:
datetime.utcnow()

# With:
datetime.now(timezone.utc)
```

---

### BUG-005: Missing /metrics Endpoint

**Severity**: Low
**Location**: `src/main.py`

**Description**: Standard SAHOOL services expose `/metrics` for Prometheus, but ws-gateway does not implement this endpoint.

**Impact**: Cannot collect WebSocket-specific metrics (connections, messages, room counts) in monitoring stack.

**Recommended Fix**:
- Add Prometheus metrics using `prometheus_client` or `shared/monitoring`
- Expose connection counts, message throughput, room statistics

---

### BUG-006: Unused Environment Variables

**Severity**: Low
**Location**: `src/main.py`, docker-compose configuration

**Description**: Several environment variables are configured but never read:
- `LOG_LEVEL` - logging level is hardcoded to INFO
- `ENVIRONMENT` - no environment-specific behavior
- `CORS_ALLOWED_ORIGINS` - no CORS middleware

**Recommended Fix**:
- Implement configurable log level
- Add CORS middleware if cross-origin WebSocket is needed
- Or remove these from docker-compose configuration

---

### BUG-007: No Rate Limiting for WebSocket Messages

**Severity**: Medium
**Location**: `src/main.py:267-272`

**Description**: WebSocket message loop has no rate limiting. A malicious client could flood the server.

```python
while True:
    data = await websocket.receive_json()
    response = await message_handler.handle_message(connection_id, data)
```

**Recommended Fix**:
- Implement message rate limiting per connection
- Add message size validation
- Consider using token bucket or sliding window algorithm

---

### BUG-008: Missing Health Check for NATS Subscriptions

**Severity**: Low
**Location**: `src/main.py:137`

**Description**: Health check only verifies NATS connection, not subscription health.

**Impact**: NATS could be connected but subscriptions could be in error state.

**Recommended Fix**:
- Track subscription errors
- Include subscription health in `/readyz` response

---

## Test Coverage

### Test Files

| File | Coverage |
|------|----------|
| `tests/test_ws_gateway_service.py` | Health endpoints, WebSocket connection, broadcast API |
| `tests/test_handlers.py` | Message handler tests |
| `tests/test_rooms.py` | Room manager tests |
| `tests/test_api_endpoints.py` | REST API tests |

### Running Tests

```bash
# Run all tests
pytest apps/services/ws-gateway/tests/ -v

# Run with coverage
pytest apps/services/ws-gateway/tests/ --cov=src --cov-report=html
```

---

## Kong Gateway Configuration

From Kong configuration:
- **Host**: `ws-gateway`
- **Port**: `8081`
- **Route**: `/ws`
- **Strip Path**: `true`

External URL: `wss://api.sahool.io/ws`

---

## Usage Examples

### JavaScript WebSocket Client

```javascript
const token = 'your-jwt-token';
const tenantId = 'tenant-123';

const ws = new WebSocket(
  `wss://api.sahool.io/ws?tenant_id=${tenantId}`,
  [],
  { headers: { 'Authorization': `Bearer ${token}` } }
);

ws.onopen = () => {
  console.log('Connected');

  // Subscribe to field updates
  ws.send(JSON.stringify({
    type: 'subscribe',
    topics: ['field:field-123', 'alerts', 'weather']
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);

  if (data.type === 'event') {
    console.log(`Event: ${data.event_type}`, data.data);
    console.log(`Arabic: ${data.message_ar}`);
  }
};

// Heartbeat
setInterval(() => {
  ws.send(JSON.stringify({ type: 'ping' }));
}, 30000);
```

### Python Client

```python
import asyncio
import websockets
import json

async def connect():
    uri = "wss://api.sahool.io/ws?tenant_id=tenant-123"
    headers = {"Authorization": "Bearer your-jwt-token"}

    async with websockets.connect(uri, extra_headers=headers) as ws:
        # Receive connection confirmation
        msg = await ws.recv()
        print(f"Connected: {msg}")

        # Subscribe to topics
        await ws.send(json.dumps({
            "type": "subscribe",
            "topics": ["field:field-123", "alerts"]
        }))

        # Listen for events
        async for message in ws:
            data = json.loads(message)
            print(f"Received: {data}")

asyncio.run(connect())
```

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 16.0.0 | Jan 2026 | Initial documentation |

---

*Generated: 2026-01-25*
*Service Location: `/home/user/sahool-unified-v15-idp/apps/services/ws-gateway/`*
