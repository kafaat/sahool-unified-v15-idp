# WebSocket Gateway Service

**بوابة WebSocket - مركز الاتصالات الفورية**

## Overview | نظرة عامة

Real-time WebSocket communication hub for all platform events. Manages authenticated WebSocket connections, topic subscriptions, and broadcasts events to connected clients.

مركز اتصالات WebSocket الفوري لجميع أحداث المنصة. يدير اتصالات WebSocket المصادق عليها واشتراكات المواضيع وبث الأحداث للعملاء المتصلين.

## Port

```
8090
```

## Features | الميزات

### Connection Management | إدارة الاتصالات
- JWT-authenticated connections
- Tenant isolation
- Connection tracking

### Topic Subscriptions | اشتراكات المواضيع
- Field-specific topics
- Event type filtering
- Dynamic subscribe/unsubscribe

### Event Broadcasting | بث الأحداث
- Tenant-scoped broadcasts
- Topic-based routing
- Connection-specific messages

### Presence Tracking | تتبع الحضور
- Online users per tenant
- Connection metadata
- Last activity tracking

## WebSocket Endpoints

### Main Connection
```
ws://localhost:8090/ws?token=JWT_TOKEN
```

### With Tenant Override
```
ws://localhost:8090/ws?token=JWT_TOKEN&tenant_id=tenant_001
```

## Message Protocol

### Client → Server

#### Subscribe to Topic
```json
{
  "type": "subscribe",
  "topic": "field.field_001.ndvi"
}
```

#### Unsubscribe
```json
{
  "type": "unsubscribe",
  "topic": "field.field_001.ndvi"
}
```

#### Ping
```json
{
  "type": "ping"
}
```

### Server → Client

#### Event Message
```json
{
  "type": "event",
  "topic": "field.field_001.ndvi",
  "data": {
    "ndvi": 0.72,
    "timestamp": "2025-12-23T10:00:00Z"
  },
  "timestamp": "2025-12-23T10:00:00Z"
}
```

#### Subscription Confirmed
```json
{
  "type": "subscribed",
  "topic": "field.field_001.ndvi"
}
```

#### Pong
```json
{
  "type": "pong",
  "timestamp": "2025-12-23T10:00:00Z"
}
```

#### Error
```json
{
  "type": "error",
  "message": "Invalid topic format",
  "code": "INVALID_TOPIC"
}
```

## Topic Patterns

| Pattern | Example | Description |
|---------|---------|-------------|
| `field.{id}.*` | `field.field_001.*` | All events for a field |
| `field.{id}.ndvi` | `field.field_001.ndvi` | NDVI updates |
| `field.{id}.weather` | `field.field_001.weather` | Weather alerts |
| `field.{id}.iot` | `field.field_001.iot` | IoT sensor readings |
| `field.{id}.task` | `field.field_001.task` | Task updates |
| `tenant.{id}.alerts` | `tenant.tenant_001.alerts` | Tenant-wide alerts |

## API Endpoints (HTTP)

### Health
| Method | Path | Description |
|--------|------|-------------|
| GET | `/healthz` | Health check |

### Stats
| Method | Path | Description |
|--------|------|-------------|
| GET | `/stats` | Connection statistics |
| GET | `/stats/tenant/{id}` | Tenant-specific stats |

### Admin
| Method | Path | Description |
|--------|------|-------------|
| POST | `/broadcast` | Broadcast message (admin) |
| DELETE | `/connections/{id}` | Force disconnect |

## Usage Examples | أمثلة الاستخدام

### JavaScript Client
```javascript
const ws = new WebSocket('ws://localhost:8090/ws?token=YOUR_JWT');

ws.onopen = () => {
  // Subscribe to field events
  ws.send(JSON.stringify({
    type: 'subscribe',
    topic: 'field.field_001.*'
  }));
};

ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  if (msg.type === 'event') {
    console.log(`Event on ${msg.topic}:`, msg.data);
  }
};
```

### Python Client
```python
import websockets
import json

async def connect():
    uri = "ws://localhost:8090/ws?token=YOUR_JWT"
    async with websockets.connect(uri) as ws:
        # Subscribe
        await ws.send(json.dumps({
            "type": "subscribe",
            "topic": "field.field_001.ndvi"
        }))

        # Listen for events
        async for message in ws:
            data = json.loads(message)
            print(f"Received: {data}")
```

## JWT Token Claims

Required claims in JWT token:
```json
{
  "sub": "user_001",
  "tenant_id": "tenant_001",
  "exp": 1735000000,
  "iat": 1734900000
}
```

## Connection Limits

| Limit | Value |
|-------|-------|
| Max connections per tenant | 1000 |
| Max subscriptions per connection | 50 |
| Message size limit | 64 KB |
| Idle timeout | 5 minutes |
| Ping interval | 30 seconds |

## Dependencies

- FastAPI
- WebSockets
- python-jose (JWT)
- NATS (for event ingestion)

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Service port | `8090` |
| `JWT_SECRET` | JWT signing key | **required** |
| `JWT_ALGORITHM` | JWT algorithm | `HS256` |
| `WS_REQUIRE_AUTH` | Require authentication | `true` |
| `NATS_URL` | NATS server URL | - |
| `MAX_CONNECTIONS_PER_TENANT` | Connection limit | `1000` |

## Events Consumed (from NATS)

All events from other services are forwarded to WebSocket clients:
- `ndvi.*`
- `weather.*`
- `iot.*`
- `task.*`
- `alert.*`
- `field.*`
