# SAHOOL WebSocket Gateway

Real-time communication hub for the SAHOOL platform with room-based messaging and NATS event bridging.

## Features

- **Room-Based Messaging**: Organized message routing using rooms (field, farm, user, tenant, etc.)
- **NATS Event Bridge**: Automatic forwarding of NATS events to WebSocket clients
- **JWT Authentication**: Secure WebSocket connections with JWT token validation
- **Auto-Reconnection**: Client-side automatic reconnection with exponential backoff
- **Event Types**: Comprehensive event system for all platform activities
- **Arabic Support**: Bilingual event messages (Arabic and English)

## Architecture

```
┌─────────────────┐     NATS      ┌──────────────────┐     WebSocket    ┌────────────┐
│ Backend Services│ ───────────►  │  WS Gateway      │ ───────────────► │  Clients   │
│  (Publishers)   │               │  - NATS Bridge   │                  │  (Flutter) │
└─────────────────┘               │  - Room Manager  │                  └────────────┘
                                  │  - Event Handler │
                                  └──────────────────┘
```

## Connection

### WebSocket URL

```
ws://localhost:8081/ws?tenant_id={tenant_id}
```

### Parameters

- `tenant_id` (required): Tenant identifier

### Headers

- `Authorization: Bearer {jwt_token}` (required): JWT authentication token

**SECURITY NOTE**: As of v16.0.0, tokens should be passed via the Authorization header for enhanced security. Passing tokens in URL query parameters (deprecated) exposes them in logs and proxies.

### Example Connection (JavaScript)

```javascript
const token = "your_jwt_token";
const tenantId = "tenant_123";

// Modern approach (RECOMMENDED)
const ws = new WebSocket(`ws://localhost:8081/ws?tenant_id=${tenantId}`, {
  headers: {
    Authorization: `Bearer ${token}`,
  },
});

// DEPRECATED: Query parameter approach (less secure)
// const ws = new WebSocket(`ws://localhost:8081/ws?tenant_id=${tenantId}&token=${token}`);

ws.onopen = () => {
  console.log("Connected to WebSocket");
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log("Received:", data);
};
```

### Example Connection (Flutter)

```dart
import 'package:sahool/core/websocket/websocket_service.dart';

final wsService = WebSocketService(
  baseUrl: 'http://localhost:8081',
  getToken: () => authService.token,
  getTenantId: () => authService.tenantId,
);

await wsService.connect();

wsService.events.listen((event) {
  print('Event: ${event.eventType}');
});
```

**Note**: The Flutter WebSocketService automatically passes the token via the Authorization header for enhanced security (v16.0.0+).

## Room Types

### Automatic Rooms

When a client connects, they are automatically joined to:

- `tenant:{tenant_id}` - All users in the tenant
- `user:{user_id}` - All connections of the user

### Available Room Types

| Room Type | Format               | Description                  |
| --------- | -------------------- | ---------------------------- |
| Field     | `field:{field_id}`   | Updates for a specific field |
| Farm      | `farm:{farm_id}`     | Updates for a farm           |
| User      | `user:{user_id}`     | Personal messages to a user  |
| Tenant    | `tenant:{tenant_id}` | Tenant-wide broadcasts       |
| Alerts    | `alerts`             | Critical system alerts       |
| Weather   | `weather`            | Weather updates              |
| Chat      | `chat:{room_id}`     | Chat room messages           |
| Global    | `global`             | Global announcements         |

## Message Types

### Client → Server Messages

#### 1. Subscribe to Topics

```json
{
  "type": "subscribe",
  "topics": ["field:123", "weather", "alerts"]
}
```

Response:

```json
{
  "type": "subscribed",
  "topics": ["field:123", "weather", "alerts"],
  "failed": [],
  "timestamp": "2024-01-15T10:30:00Z",
  "message_ar": "تم الاشتراك في 3 موضوع"
}
```

#### 2. Unsubscribe from Topics

```json
{
  "type": "unsubscribe",
  "topics": ["field:123"]
}
```

#### 3. Join Room

```json
{
  "type": "join_room",
  "room": "field:123"
}
```

#### 4. Leave Room

```json
{
  "type": "leave_room",
  "room": "field:123"
}
```

#### 5. Broadcast Message

```json
{
  "type": "broadcast",
  "room": "field:123",
  "message": {
    "action": "update",
    "data": {...}
  }
}
```

#### 6. Ping (Keep-Alive)

```json
{
  "type": "ping"
}
```

Response:

```json
{
  "type": "pong",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### 7. Typing Indicator

```json
{
  "type": "typing",
  "room": "chat:456",
  "typing": true
}
```

#### 8. Read Receipt

```json
{
  "type": "read",
  "room": "chat:456",
  "message_id": "msg_789"
}
```

### Server → Client Events

#### Event Structure

```json
{
  "type": "event",
  "event_type": "field.updated",
  "priority": "medium",
  "message": "Field data updated",
  "message_ar": "تم تحديث بيانات الحقل",
  "data": {
    "field_id": "123",
    "tenant_id": "tenant_456",
    ...
  },
  "subject": "sahool.fields.123.updated",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Event Types

### Field Events

| Event Type      | Priority | Description        |
| --------------- | -------- | ------------------ |
| `field.updated` | Medium   | Field data updated |
| `field.created` | Medium   | New field created  |
| `field.deleted` | Medium   | Field deleted      |

### Weather Events

| Event Type        | Priority | Description             |
| ----------------- | -------- | ----------------------- |
| `weather.alert`   | High     | Important weather alert |
| `weather.updated` | Low      | Weather data updated    |

### Satellite Events

| Event Type             | Priority | Description                  |
| ---------------------- | -------- | ---------------------------- |
| `satellite.ready`      | Low      | Satellite imagery ready      |
| `satellite.processing` | Low      | Processing satellite imagery |
| `satellite.failed`     | Medium   | Satellite processing failed  |

### NDVI Events

| Event Type            | Priority | Description             |
| --------------------- | -------- | ----------------------- |
| `ndvi.updated`        | Low      | NDVI data updated       |
| `ndvi.analysis.ready` | Low      | NDVI analysis completed |

### Inventory Events

| Event Type               | Priority | Description     |
| ------------------------ | -------- | --------------- |
| `inventory.low_stock`    | Medium   | Low stock alert |
| `inventory.out_of_stock` | High     | Out of stock    |
| `inventory.updated`      | Low      | Stock updated   |

### Crop Health Events

| Event Type              | Priority | Description           |
| ----------------------- | -------- | --------------------- |
| `crop.disease.detected` | High     | Disease detected      |
| `crop.pest.detected`    | High     | Pest detected         |
| `crop.health.alert`     | High     | Health issue detected |

### Spray Events

| Event Type             | Priority | Description               |
| ---------------------- | -------- | ------------------------- |
| `spray.window.optimal` | Medium   | Optimal spray window      |
| `spray.window.warning` | Medium   | Spray window warning      |
| `spray.scheduled`      | Low      | Spray operation scheduled |

### Chat Events

| Event Type     | Priority | Description  |
| -------------- | -------- | ------------ |
| `chat.message` | Low      | New message  |
| `chat.typing`  | Low      | User typing  |
| `chat.read`    | Low      | Message read |

### Task Events

| Event Type       | Priority | Description    |
| ---------------- | -------- | -------------- |
| `task.created`   | Low      | Task created   |
| `task.updated`   | Low      | Task updated   |
| `task.completed` | Low      | Task completed |
| `task.overdue`   | Medium   | Task overdue   |

### IoT Events

| Event Type    | Priority | Description    |
| ------------- | -------- | -------------- |
| `iot.reading` | Low      | Sensor reading |
| `iot.alert`   | High     | Sensor alert   |
| `iot.offline` | Medium   | Sensor offline |

### System Events

| Event Type            | Priority | Description         |
| --------------------- | -------- | ------------------- |
| `system.notification` | Medium   | System notification |
| `sync_required`       | Low      | Sync required       |

## REST API Endpoints

### Health Check

```
GET /healthz
```

Response:

```json
{
  "status": "healthy",
  "service": "ws-gateway",
  "version": "16.0.0",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Readiness Check

```
GET /readyz
```

Response:

```json
{
  "status": "ok",
  "nats": true,
  "connections": {
    "total_connections": 150,
    "total_rooms": 45,
    "rooms": {...}
  }
}
```

### Statistics

```
GET /stats
```

Response:

```json
{
  "connections": {
    "total_connections": 150,
    "total_rooms": 45,
    "connections_by_room_type": {
      "tenant": 150,
      "user": 150,
      "field": 75
    }
  },
  "nats": {
    "connected": true,
    "subscriptions": 11
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Broadcast Message

```
POST /broadcast
```

Request Body:

```json
{
  "tenant_id": "tenant_123",
  "message": {
    "type": "announcement",
    "text": "System maintenance scheduled"
  }
}
```

Or target specific rooms/users:

```json
{
  "room": "field:123",
  "message": {...}
}
```

```json
{
  "user_id": "user_456",
  "message": {...}
}
```

```json
{
  "field_id": "field_789",
  "message": {...}
}
```

Response:

```json
{
  "status": "sent",
  "recipients": 25,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## NATS Event Integration

The WebSocket gateway automatically subscribes to these NATS subjects:

- `sahool.fields.>` - Field events
- `sahool.weather.>` - Weather events
- `sahool.satellite.>` - Satellite events
- `sahool.ndvi.>` - NDVI events
- `sahool.inventory.>` - Inventory events
- `sahool.crop.>` - Crop health events
- `sahool.spray.>` - Spray events
- `sahool.chat.>` - Chat events
- `sahool.tasks.>` - Task events
- `sahool.iot.>` - IoT events
- `sahool.alerts.>` - Alert events

### Publishing Events to WebSocket

From any backend service, publish to NATS and it will be automatically forwarded to WebSocket clients:

```python
import nats
import json

nc = await nats.connect("nats://localhost:4222")

# Publish field update
await nc.publish(
    "sahool.fields.123.updated",
    json.dumps({
        "field_id": "123",
        "tenant_id": "tenant_456",
        "name": "North Field",
        "updated_at": "2024-01-15T10:30:00Z"
    }).encode()
)
```

## Error Codes

| Code | Reason                  | Description                                 |
| ---- | ----------------------- | ------------------------------------------- |
| 4001 | Authentication Required | Missing or invalid token                    |
| 4003 | Tenant Mismatch         | Token tenant doesn't match requested tenant |

## Environment Variables

```bash
PORT=8081
NATS_URL=nats://nats:4222
REDIS_URL=redis://:password@redis:6379/0
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
LOG_LEVEL=INFO
ENVIRONMENT=production
CORS_ALLOWED_ORIGINS=https://app.sahool.com
```

## Docker Deployment

The service is already configured in `docker-compose.yml`:

```yaml
ws_gateway:
  build:
    context: ./apps/services/ws-gateway
    dockerfile: Dockerfile
  container_name: sahool-ws-gateway
  environment:
    - PORT=8081
    - NATS_URL=nats://nats:4222
    - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
    - JWT_SECRET_KEY=${JWT_SECRET_KEY}
  ports:
    - "8081:8081"
  depends_on:
    - nats
    - redis
```

## Flutter Integration

### Setup

1. Add dependencies to `pubspec.yaml`:

```yaml
dependencies:
  web_socket_channel: ^2.4.0
  flutter_riverpod: ^2.4.0
```

2. Initialize WebSocket on app startup:

```dart
@override
Widget build(BuildContext context) {
  return ProviderScope(
    child: WebSocketEventListener(
      child: MaterialApp(
        home: HomePage(),
      ),
    ),
  );
}
```

3. Connect when user logs in:

```dart
final wsConnection = ref.watch(webSocketConnectionProvider.notifier);
await wsConnection.connect();
```

### Subscribe to Field Updates

```dart
final fieldEvents = ref.watch(fieldEventsProvider('field_123'));

fieldEvents.when(
  data: (event) {
    // Handle field update
    print('Field event: ${event.eventType}');
  },
  loading: () => CircularProgressIndicator(),
  error: (err, stack) => Text('Error: $err'),
);
```

### Listen to Alerts

```dart
final alerts = ref.watch(highPriorityAlertsProvider);

alerts.when(
  data: (event) {
    // Show alert dialog or notification
    _showAlert(event);
  },
  loading: () {},
  error: (err, stack) {},
);
```

## Testing

### Testing with wscat

```bash
# Install wscat
npm install -g wscat

# Connect to WebSocket with Authorization header (RECOMMENDED)
wscat -c "ws://localhost:8081/ws?tenant_id=test" -H "Authorization: Bearer your_jwt_token"

# For backward compatibility, query parameter still works (DEPRECATED)
# wscat -c "ws://localhost:8081/ws?tenant_id=test&token=your_jwt_token"

# Subscribe to topics
> {"type":"subscribe","topics":["weather","alerts"]}

# Send ping
> {"type":"ping"}
```

### Load Testing

```bash
# Using autocannon
npm install -g autocannon
autocannon -c 100 -d 30 ws://localhost:8081/ws?tenant_id=test&token=token
```

## Monitoring

### Connection Statistics

```bash
curl http://localhost:8081/stats
```

### Health Check

```bash
curl http://localhost:8081/healthz
```

## Security Considerations

1. **Always use WSS (WebSocket Secure) in production**
2. **Pass JWT tokens via Authorization header** - Never pass tokens in URL query parameters as they are visible in logs, proxy servers, and browser history
3. **JWT tokens should have short expiration times**
4. **Validate tenant permissions server-side**
5. **Rate limit connections per IP/tenant**
6. **Monitor for abnormal connection patterns**
7. **Use hardcoded algorithm whitelists** - The gateway uses a hardcoded list of allowed JWT algorithms to prevent algorithm confusion attacks

## Troubleshooting

### Connection Refused

- Check if the service is running: `docker ps | grep ws-gateway`
- Check logs: `docker logs sahool-ws-gateway`
- Verify NATS is running: `curl http://localhost:8222/healthz`

### Authentication Fails

- Verify JWT_SECRET_KEY matches across services
- Check token expiration
- Ensure tenant_id in token matches query parameter

### Events Not Received

- Verify NATS connection: Check `/readyz` endpoint
- Confirm you're subscribed to the correct room
- Check NATS subject matches event type

## Development

### Running Locally

```bash
cd apps/services/ws-gateway
pip install -r requirements.txt
python -m src.main
```

### Running Tests

```bash
pytest tests/
```

## License

Copyright © 2024 SAHOOL. All rights reserved.
