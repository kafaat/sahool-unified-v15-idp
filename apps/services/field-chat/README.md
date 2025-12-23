# Field Chat Service

**خدمة الدردشة الميدانية - التواصل في الوقت الفعلي**

## Overview | نظرة عامة

Real-time chat service for field workers, agronomists, and farm managers. Supports WebSocket connections for instant messaging with field-specific channels.

خدمة دردشة في الوقت الفعلي للعاملين الميدانيين والمهندسين الزراعيين ومديري المزارع. تدعم اتصالات WebSocket للرسائل الفورية مع قنوات خاصة بالحقول.

## Port

```
8091
```

## Features | الميزات

### Real-time Messaging | الرسائل الفورية
- WebSocket-based communication
- Field-specific chat channels
- Instant message delivery

### Message Management | إدارة الرسائل
- Message history retrieval
- Read receipts
- Message search

### Channel Management | إدارة القنوات
- Field-based channels
- User presence tracking
- Channel membership

## API Endpoints

### Health
| Method | Path | Description |
|--------|------|-------------|
| GET | `/healthz` | Health check |

### Messages
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/fields/{field_id}/messages` | Get message history |
| POST | `/api/v1/fields/{field_id}/messages` | Send message |
| GET | `/api/v1/messages/{message_id}` | Get message |

### WebSocket
| Path | Description |
|------|-------------|
| `/ws/{field_id}` | WebSocket connection for field chat |

## WebSocket Protocol

### Connect
```javascript
const ws = new WebSocket('ws://localhost:8091/ws/field_001?token=JWT_TOKEN');
```

### Send Message
```json
{
  "type": "message",
  "content": "تم الانتهاء من الري",
  "field_id": "field_001"
}
```

### Receive Message
```json
{
  "type": "message",
  "id": "msg_123",
  "sender_id": "user_001",
  "sender_name": "أحمد",
  "content": "تم الانتهاء من الري",
  "timestamp": "2025-12-23T10:30:00Z"
}
```

## Usage Examples | أمثلة الاستخدام

### Get Message History
```bash
curl "http://localhost:8091/api/v1/fields/field_001/messages?limit=50"
```

### Send Message
```bash
curl -X POST http://localhost:8091/api/v1/fields/field_001/messages \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer JWT_TOKEN" \
  -d '{
    "content": "تم فحص الحقل - لا توجد مشاكل",
    "type": "text"
  }'
```

## Dependencies

- FastAPI
- WebSockets
- TortoiseORM
- PostgreSQL

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Service port | `8091` |
| `DATABASE_URL` | PostgreSQL connection | - |
| `JWT_SECRET` | JWT signing key | - |

## Database Models

### Message
- `id` - Unique identifier
- `field_id` - Associated field
- `sender_id` - Message author
- `content` - Message text
- `type` - Message type (text, image, location)
- `created_at` - Timestamp
