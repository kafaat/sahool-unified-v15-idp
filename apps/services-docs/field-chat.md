> **⚠️ DEPRECATED**: This service has been replaced by `chat-service`. See [chat-service.md](chat-service.md) for current documentation.

---

# Field Chat Service Analysis

**Service Name**: field-chat
**Version**: 15.3.3 (Dockerfile references 16.0.0)
**Type**: Python/FastAPI
**Port**: 8099
**Description**: Real-time collaboration service for fields, tasks, and incidents with WebSocket support

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [API Endpoints](#api-endpoints)
4. [Request/Response Schemas](#requestresponse-schemas)
5. [NATS Events](#nats-events)
6. [WebSocket Protocol](#websocket-protocol)
7. [Database Models](#database-models)
8. [Dependencies](#dependencies)
9. [Environment Variables](#environment-variables)
10. [Configuration](#configuration)
11. [Field-Specific Features](#field-specific-features)
12. [Bugs and Issues](#bugs-and-issues)
13. [Recommended Fixes](#recommended-fixes)
14. [Testing](#testing)

---

## Overview

The Field Chat service provides real-time messaging capabilities for SAHOOL platform users. It enables field workers, agronomists, and farm managers to communicate within the context of specific fields, tasks, or incidents.

### Key Features

| Feature | Description (EN) | Description (AR) |
|---------|-----------------|------------------|
| Scoped Threads | Chat threads tied to fields, tasks, or incidents | محادثات مرتبطة بالحقول والمهام والحوادث |
| Real-time WebSocket | Live message delivery via WebSocket | تسليم الرسائل الفورية عبر WebSocket |
| Message Threading | Reply-to support for message threads | دعم الردود المترابطة للرسائل |
| Read Receipts | Track message read status per user | تتبع حالة قراءة الرسائل لكل مستخدم |
| Unread Counts | Per-thread unread message counting | عد الرسائل غير المقروءة لكل محادثة |
| Attachments | Support for file attachments | دعم المرفقات |
| Search | Full-text message search | البحث النصي الكامل في الرسائل |
| Archiving | Thread archival capability | إمكانية أرشفة المحادثات |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                       Kong API Gateway                          │
│              Routes: /api/v1/field-chat, /field-chat            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Field Chat Service (8099)                    │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                      FastAPI App                           │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐ │ │
│  │  │   REST API   │  │  WebSocket   │  │ Health Endpoints │ │ │
│  │  │   /chat/*    │  │ /ws/chat/*   │  │ /healthz /readyz │ │ │
│  │  └──────┬───────┘  └──────┬───────┘  └──────────────────┘ │ │
│  │         │                 │                                │ │
│  │         ▼                 ▼                                │ │
│  │  ┌─────────────────────────────────────────────────────┐  │ │
│  │  │              ChatRepository (Data Layer)            │  │ │
│  │  └─────────────────────────┬───────────────────────────┘  │ │
│  │                            │                               │ │
│  │  ┌─────────────────────────┴───────────────────────────┐  │ │
│  │  │              ChatPublisher (Events)                 │  │ │
│  │  └─────────────────────────┬───────────────────────────┘  │ │
│  └────────────────────────────┼───────────────────────────────┘ │
└────────────────────────────────┼─────────────────────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
│   PostgreSQL    │   │      NATS       │   │     Redis       │
│  (Tortoise ORM) │   │   (JetStream)   │   │   (Caching)     │
└─────────────────┘   └─────────────────┘   └─────────────────┘
```

### Event Flow

```
REST API Request
      │
      ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Validate Input │ ──▶ │  Repository     │ ──▶ │  Publish Event  │
│  (Pydantic)     │     │  (DB Operation) │     │  (NATS)         │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                       │
                                                       ▼
                                              ┌─────────────────┐
                                              │  Projection     │
                                              │  Worker         │
                                              │  (Subscribers)  │
                                              └─────────────────┘
                                                       │
                                                       ▼
                                              ┌─────────────────┐
                                              │  WebSocket      │
                                              │  Broadcast      │
                                              └─────────────────┘
```

---

## API Endpoints

### Health Endpoints

| Method | Path | Description (EN) | Description (AR) |
|--------|------|-----------------|------------------|
| GET | `/healthz` | Liveness probe | فحص الحياة |
| GET | `/readyz` | Readiness probe (checks DB) | فحص الجاهزية |
| GET | `/` | Service information | معلومات الخدمة |

### Thread Endpoints

| Method | Path | Description (EN) | Description (AR) |
|--------|------|-----------------|------------------|
| POST | `/chat/threads` | Create new chat thread | إنشاء محادثة جديدة |
| GET | `/chat/threads` | List threads with filters | قائمة المحادثات |
| GET | `/chat/threads/{thread_id}` | Get thread by ID | الحصول على محادثة بالمعرف |
| GET | `/chat/threads/by-scope/{scope_type}/{scope_id}` | Get thread by scope | الحصول على محادثة بالنطاق |
| POST | `/chat/threads/{thread_id}/archive` | Archive thread | أرشفة المحادثة |

### Message Endpoints

| Method | Path | Description (EN) | Description (AR) |
|--------|------|-----------------|------------------|
| POST | `/chat/threads/{thread_id}/messages` | Send message | إرسال رسالة |
| GET | `/chat/threads/{thread_id}/messages` | List messages | قائمة الرسائل |
| GET | `/chat/messages/search` | Search messages | البحث في الرسائل |

### Participant Endpoints

| Method | Path | Description (EN) | Description (AR) |
|--------|------|-----------------|------------------|
| POST | `/chat/threads/{thread_id}/participants` | Add participant | إضافة مشارك |
| DELETE | `/chat/threads/{thread_id}/participants/{user_id}` | Remove participant | إزالة مشارك |
| POST | `/chat/threads/{thread_id}/read` | Mark as read | وضع علامة مقروءة |
| GET | `/chat/unread-counts` | Get unread counts | الحصول على عدد غير المقروء |

### WebSocket Endpoints

| Path | Description (EN) | Description (AR) |
|------|-----------------|------------------|
| `/ws/chat/{thread_id}` | Real-time chat connection | اتصال الدردشة الفورية |

---

## Request/Response Schemas

### CreateThreadRequest

```json
{
  "tenant_id": "string (required)",
  "scope_type": "string (required) - field|task|incident",
  "scope_id": "string (required)",
  "created_by": "string (required)",
  "title": "string (optional)",
  "correlation_id": "string (optional)"
}
```

### ThreadResponse

```json
{
  "thread_id": "uuid",
  "tenant_id": "string",
  "scope_type": "string",
  "scope_id": "string",
  "created_by": "string",
  "title": "string | null",
  "is_archived": "boolean",
  "message_count": "integer",
  "last_message_at": "ISO8601 timestamp | null",
  "created_at": "ISO8601 timestamp"
}
```

### SendMessageRequest

```json
{
  "tenant_id": "string (required)",
  "sender_id": "string (required)",
  "text": "string (optional)",
  "attachments": ["array of URLs (optional)"],
  "reply_to_id": "uuid (optional)",
  "correlation_id": "string (optional)"
}
```

### MessageResponse

```json
{
  "message_id": "uuid",
  "thread_id": "uuid",
  "sender_id": "string",
  "text": "string | null",
  "attachments": ["array of URLs"],
  "reply_to_id": "uuid | null",
  "message_type": "string - text|attachment|mixed",
  "created_at": "ISO8601 timestamp"
}
```

### MarkReadRequest

```json
{
  "user_id": "string (required)",
  "last_read_message_id": "uuid (optional)"
}
```

### AddParticipantRequest

```json
{
  "tenant_id": "string (required)",
  "user_id": "string (required)",
  "added_by": "string (optional)",
  "correlation_id": "string (optional)"
}
```

### UnreadCountsResponse

```json
{
  "total_unread": "integer",
  "threads": {
    "thread_id_1": "integer",
    "thread_id_2": "integer"
  }
}
```

### Error Response

```json
{
  "detail": {
    "error": "error_code",
    "message_ar": "رسالة الخطأ بالعربية",
    "message_en": "English error message"
  }
}
```

---

## NATS Events

### Event Envelope Structure

All events use a standard envelope format:

```json
{
  "event_id": "uuid",
  "event_type": "string",
  "version": 1,
  "aggregate_id": "thread_id",
  "tenant_id": "string",
  "correlation_id": "string",
  "timestamp": "ISO8601 timestamp",
  "payload": {}
}
```

### Published Events

| Event Type | Subject | Description |
|------------|---------|-------------|
| `chat_thread_created` | `sahool.chat.thread_created` | New thread created |
| `chat_thread_archived` | `sahool.chat.thread_archived` | Thread archived |
| `chat_message_sent` | `sahool.chat.message_sent` | New message sent |
| `chat_message_edited` | `sahool.chat.message_edited` | Message edited |
| `chat_message_deleted` | `sahool.chat.message_deleted` | Message deleted (defined but not implemented) |
| `chat_participant_joined` | `sahool.chat.participant_joined` | User joined thread |
| `chat_participant_left` | `sahool.chat.participant_left` | User left thread |
| `chat_messages_read` | `sahool.chat.messages_read` | Messages marked as read |

### Event Payloads

#### chat_thread_created

```json
{
  "thread_id": "uuid",
  "scope_type": "field|task|incident",
  "scope_id": "string",
  "created_by": "user_id",
  "title": "string | null"
}
```

#### chat_thread_archived

```json
{
  "thread_id": "uuid",
  "archived_by": "user_id"
}
```

#### chat_message_sent

```json
{
  "thread_id": "uuid",
  "message_id": "uuid",
  "sender_id": "user_id",
  "text": "string",
  "attachments": ["urls"],
  "reply_to_id": "uuid | null"
}
```

#### chat_message_edited

```json
{
  "thread_id": "uuid",
  "message_id": "uuid",
  "edited_by": "user_id",
  "new_text": "string"
}
```

#### chat_participant_joined

```json
{
  "thread_id": "uuid",
  "user_id": "string",
  "added_by": "user_id | null"
}
```

#### chat_participant_left

```json
{
  "thread_id": "uuid",
  "user_id": "string"
}
```

#### chat_messages_read

```json
{
  "thread_id": "uuid",
  "user_id": "string",
  "last_read_message_id": "uuid"
}
```

### Subscribed Events (Projection Worker)

The `ChatProjectionWorker` subscribes to:

| Subject | Handler | Purpose |
|---------|---------|---------|
| `sahool.chat.thread_created` | `_handle_thread_created` | Broadcast to WebSocket |
| `sahool.chat.message_sent` | `_handle_message_sent` | Broadcast + notifications |
| `sahool.chat.message_edited` | `_handle_message_edited` | Broadcast edit |
| `sahool.chat.participant_joined` | `_handle_participant_joined` | Broadcast join |
| `sahool.chat.participant_left` | `_handle_participant_left` | Broadcast leave |
| `sahool.chat.messages_read` | `_handle_messages_read` | Broadcast read receipt |

---

## WebSocket Protocol

### Connection

```
WebSocket URL: ws://host:8099/ws/chat/{thread_id}
```

### Client Messages

#### Ping/Pong (Keep-alive)

```json
// Send any text
"ping"

// Response
{
  "type": "pong",
  "data": "ping"
}
```

### Server Messages

#### New Message

```json
{
  "type": "new_message",
  "thread_id": "uuid",
  "message_id": "uuid",
  "sender_id": "user_id",
  "text": "message content",
  "attachments": [],
  "reply_to_id": "uuid | null",
  "timestamp": "ISO8601"
}
```

#### Message Edited

```json
{
  "type": "message_edited",
  "thread_id": "uuid",
  "message_id": "uuid",
  "edited_by": "user_id",
  "new_text": "updated content",
  "timestamp": "ISO8601"
}
```

#### Participant Joined

```json
{
  "type": "participant_joined",
  "thread_id": "uuid",
  "user_id": "user_id",
  "added_by": "user_id | null",
  "timestamp": "ISO8601"
}
```

#### Participant Left

```json
{
  "type": "participant_left",
  "thread_id": "uuid",
  "user_id": "user_id",
  "timestamp": "ISO8601"
}
```

#### Read Receipt

```json
{
  "type": "read_receipt",
  "thread_id": "uuid",
  "user_id": "user_id",
  "last_read_message_id": "uuid",
  "timestamp": "ISO8601"
}
```

#### Thread Created

```json
{
  "type": "thread_created",
  "thread_id": "uuid",
  "scope_type": "field|task|incident",
  "scope_id": "string",
  "created_by": "user_id",
  "timestamp": "ISO8601"
}
```

---

## Database Models

### chat_threads

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Thread identifier |
| tenant_id | VARCHAR(64) | INDEX | Multi-tenant isolation |
| scope_type | VARCHAR(16) | INDEX | field\|task\|incident |
| scope_id | VARCHAR(128) | INDEX | Reference to field/task/incident |
| created_by | VARCHAR(64) | | Creator user ID |
| created_at | TIMESTAMP | AUTO | Creation timestamp |
| title | VARCHAR(255) | NULL | Optional thread title |
| is_archived | BOOLEAN | DEFAULT FALSE | Archive status |
| last_message_at | TIMESTAMP | NULL | Last message timestamp |
| message_count | INTEGER | DEFAULT 0 | Message count |

**Unique Constraint**: (tenant_id, scope_type, scope_id)

**Indexes**:
- (tenant_id, scope_type)
- (tenant_id, last_message_at)

### chat_messages

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Message identifier |
| tenant_id | VARCHAR(64) | INDEX | Multi-tenant isolation |
| thread_id | UUID | INDEX | Parent thread |
| sender_id | VARCHAR(64) | INDEX | Sender user ID |
| text | TEXT | NULL | Message content |
| attachments | JSON | NULL | List of attachment URLs |
| reply_to_id | UUID | NULL | Reply-to message |
| message_type | VARCHAR(32) | DEFAULT "text" | text\|image\|file\|system |
| is_edited | BOOLEAN | DEFAULT FALSE | Edit flag |
| edited_at | TIMESTAMP | NULL | Edit timestamp |
| created_at | TIMESTAMP | AUTO | Creation timestamp |

**Indexes**:
- (thread_id, created_at)
- (tenant_id, sender_id)

### chat_participants

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Participant record ID |
| tenant_id | VARCHAR(64) | INDEX | Multi-tenant isolation |
| thread_id | UUID | INDEX | Thread reference |
| user_id | VARCHAR(64) | INDEX | User ID |
| last_read_at | TIMESTAMP | NULL | Last read timestamp |
| last_read_message_id | UUID | NULL | Last read message |
| unread_count | INTEGER | DEFAULT 0 | Unread message count |
| is_muted | BOOLEAN | DEFAULT FALSE | Mute status |
| joined_at | TIMESTAMP | AUTO | Join timestamp |

**Unique Constraint**: (thread_id, user_id)

**Indexes**:
- (tenant_id, user_id)

### chat_attachments

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Attachment ID |
| tenant_id | VARCHAR(64) | INDEX | Multi-tenant isolation |
| message_id | UUID | INDEX | Parent message |
| file_name | VARCHAR(255) | | Original filename |
| file_type | VARCHAR(64) | | MIME type |
| file_size | INTEGER | | Size in bytes |
| file_url | TEXT | | Storage URL |
| width | INTEGER | NULL | Image width |
| height | INTEGER | NULL | Image height |
| thumbnail_url | TEXT | NULL | Thumbnail URL |
| created_at | TIMESTAMP | AUTO | Creation timestamp |

---

## Dependencies

### Python Packages (requirements.txt)

| Package | Version | Purpose |
|---------|---------|---------|
| fastapi | 0.126.0 | Web framework |
| starlette | >=0.49.1 | ASGI framework |
| uvicorn[standard] | >=0.30.0,<1.0.0 | ASGI server |
| pydantic | 2.9.2 | Data validation |
| httpx | 0.28.1 | HTTP client |
| python-dotenv | 1.0.1 | Environment loading |
| asyncpg | 0.30.0 | PostgreSQL async driver |
| tortoise-orm | 0.21.7 | Async ORM |
| nats-py | 2.9.0 | NATS client |
| redis | 5.2.1 | Redis client |
| python-jose[cryptography] | >=3.4.0 | JWT handling |
| passlib[bcrypt] | 1.7.4 | Password hashing |
| aerich | 0.7.2 | Tortoise migrations |
| aiosqlite | 0.20.0 | SQLite async (testing) |
| websockets | 14.1 | WebSocket support |
| python-dateutil | 2.8.2 | Date utilities |
| structlog | >=24.1.0 | Structured logging |

### Infrastructure Dependencies

| Service | Purpose | Required |
|---------|---------|----------|
| PostgreSQL | Primary database | Yes |
| NATS | Event messaging | Yes |
| Redis | Caching/sessions | Optional |

### Shared Libraries

| Module | Purpose |
|--------|---------|
| shared.errors_py | Unified error handling |
| shared.cors_config | CORS configuration |

---

## Environment Variables

### Configured Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DATABASE_URL` | PostgreSQL connection string | sqlite://:memory: | Yes (production) |
| `NATS_URL` | NATS server URL | nats://nats:4222 | Yes |
| `CORS_ORIGINS` | Allowed CORS origins | sahool.io domains | No |
| `PORT` | Service port | 8099 | No |
| `LOG_LEVEL` | Logging level | INFO | No |
| `ENVIRONMENT` | Runtime environment | development | No |

### Missing Environment Variables

The following variables are referenced in docker-compose but **NOT** used in code:

| Variable | Status | Impact |
|----------|--------|--------|
| `REDIS_URL` | **NOT USED** | Redis client imported but never initialized |
| `JWT_SECRET_KEY` | **NOT USED** | No authentication implemented |
| `JWT_ALGORITHM` | **NOT USED** | No authentication implemented |

### Recommended Additional Variables

| Variable | Purpose | Recommendation |
|----------|---------|----------------|
| `MAX_MESSAGE_LENGTH` | Limit message text length | Add validation |
| `MAX_ATTACHMENTS` | Limit attachments per message | Add validation |
| `WS_HEARTBEAT_INTERVAL` | WebSocket keep-alive | Configure timeout |
| `NATS_RECONNECT_ATTEMPTS` | NATS resilience | Add retry config |

---

## Configuration

### CORS Configuration

```python
# Default allowed origins
ALLOWED_ORIGINS = [
    "https://sahool.io",
    "https://admin.sahool.io",
    "http://localhost:3000"
]

# Allowed methods
ALLOWED_METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]

# Allowed headers
ALLOWED_HEADERS = ["Authorization", "Content-Type", "Accept", "X-Tenant-Id"]
```

### Tortoise ORM Configuration

```python
TORTOISE_ORM = {
    "connections": {
        "default": DATABASE_URL,
    },
    "apps": {
        "models": {
            "models": ["src.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}
```

---

## Field-Specific Features

### Scope Types

The service supports three scope types for chat threads:

| Scope | Use Case (EN) | Use Case (AR) |
|-------|---------------|---------------|
| `field` | Chat for a specific agricultural field | محادثة لحقل زراعي محدد |
| `task` | Chat for a specific task/activity | محادثة لمهمة/نشاط محدد |
| `incident` | Chat for incident/issue resolution | محادثة لحل حادثة/مشكلة |

### Thread Lifecycle

1. **Creation**: Threads are created on-demand (idempotent)
2. **One-to-One**: Each scope (field/task/incident) has exactly one thread
3. **Auto-Title**: Default bilingual titles are generated
4. **Archival**: Archived threads cannot receive new messages

### Default Thread Titles

```python
titles = {
    "field": "محادثة الحقل | Field Chat",
    "task": "محادثة المهمة | Task Chat",
    "incident": "محادثة الحادثة | Incident Chat",
}
```

### Participant Management

- Creator is automatically added as participant
- Participants can be added/removed via API
- Per-participant read tracking
- Mute capability (stored but not implemented)

---

## Bugs and Issues

### Critical Issues

#### 1. Version Mismatch

| Location | Version |
|----------|---------|
| `src/__init__.py` | 15.3.3 |
| `src/main.py` | 15.3.3 |
| `Dockerfile` | 16.0.0 |
| `requirements.txt` | 16.0.0 |

**Impact**: Inconsistent version reporting in health checks and documentation.

#### 2. Missing Authentication

The service has no authentication middleware:

```python
# No JWT validation on endpoints
# No user verification
# No tenant isolation enforcement
```

**Impact**: Security vulnerability - any user can access any tenant's data.

#### 3. Test Subject Mismatch

In `tests/test_api.py` line 48:

```python
assert SUBJECTS[CHAT_MESSAGE_SENT] == "chat.chat_message_sent"  # WRONG
# Actual value: "sahool.chat.message_sent"
```

**Impact**: Test is checking incorrect value.

#### 4. README Port Mismatch

README.md states port 8091, but actual port is 8099.

#### 5. README API Endpoints Mismatch

README documents `/api/v1/fields/{field_id}/messages` but actual endpoints use `/chat/threads/{thread_id}/messages`.

### Medium Issues

#### 1. NATS Connection Not Reused

Each API call creates a new NATS connection and closes it:

```python
# In api.py
await pub.publish_thread_created(...)
await pub.close()  # Connection closed after each publish
```

**Impact**: Performance overhead from repeated connections.

#### 2. No Message Edit API

`publish_message_edited` exists but no REST endpoint to edit messages.

#### 3. No Message Delete API

`CHAT_MESSAGE_DELETED` event type defined but no implementation.

#### 4. WebSocket Not Integrated with Projection Worker

The `ConnectionManager` in `main.py` is separate from `ChatProjectionWorker`. Broadcasts from NATS events are not wired to WebSocket connections.

```python
# ConnectionManager defined in main.py
# ChatProjectionWorker has broadcast_callback but not connected
```

#### 5. Redis Not Used

Redis is listed as a dependency but never initialized or used:

```python
# requirements.txt includes redis==5.2.1
# No Redis connection in main.py
```

### Minor Issues

#### 1. Hardcoded NATS URL in Multiple Places

```python
# publish.py
NATS_URL = os.getenv("NATS_URL", "nats://nats:4222")

# worker.py
NATS_URL = os.getenv("NATS_URL", "nats://nats:4222")
```

Should be centralized.

#### 2. Missing Input Validation

- No max length on message text
- No limit on attachments array size
- No URL validation on attachments

#### 3. Deprecated datetime.utcnow()

```python
# repository.py line 142, 250
last_message_at=datetime.utcnow(),  # Deprecated in Python 3.12
```

---

## Recommended Fixes

### High Priority

#### 1. Add Authentication Middleware

```python
from shared.auth.dependencies import get_current_user

@router.post("/threads", response_model=ThreadResponse)
async def create_thread(
    req: CreateThreadRequest,
    user: User = Depends(get_current_user),  # Add auth
    repo: ChatRepository = Depends(get_repository),
    pub: ChatPublisher = Depends(get_publisher),
):
    # Verify user has access to tenant
    if user.tenant_id != req.tenant_id:
        raise HTTPException(status_code=403, detail="forbidden")
```

#### 2. Fix Version Consistency

Update all files to version 16.0.0:

```python
# src/__init__.py
__version__ = "16.0.0"

# src/main.py
version="16.0.0"
```

#### 3. Wire WebSocket to Projection Worker

```python
# main.py
from .projections.worker import ChatProjectionWorker

# Create worker with broadcast callback
worker = ChatProjectionWorker(broadcast_callback=manager.broadcast)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start projection worker
    asyncio.create_task(worker.start())
    yield
    await worker.close()
```

### Medium Priority

#### 4. Add Connection Pool for NATS

```python
class ChatPublisher:
    _instance: "ChatPublisher | None" = None

    @classmethod
    async def get_instance(cls) -> "ChatPublisher":
        if cls._instance is None:
            cls._instance = ChatPublisher()
            await cls._instance.connect()
        return cls._instance
```

#### 5. Add Message Edit Endpoint

```python
@router.put("/threads/{thread_id}/messages/{message_id}")
async def edit_message(
    thread_id: UUID,
    message_id: UUID,
    req: EditMessageRequest,
    ...
):
    # Verify sender
    # Update message
    # Publish event
```

#### 6. Add Input Validation

```python
class SendMessageRequest(BaseModel):
    text: str | None = Field(None, max_length=10000)
    attachments: list[str] | None = Field(None, max_items=10)

    @validator("attachments")
    def validate_attachments(cls, v):
        if v:
            for url in v:
                if not url.startswith(("https://", "http://")):
                    raise ValueError("Invalid attachment URL")
        return v
```

### Low Priority

#### 7. Fix datetime Deprecation

```python
from datetime import datetime, timezone

# Replace
datetime.utcnow()
# With
datetime.now(timezone.utc)
```

#### 8. Add Redis Caching

```python
# Cache unread counts
async def get_unread_counts(self, tenant_id: str, user_id: str) -> dict:
    cache_key = f"unread:{tenant_id}:{user_id}"
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)
    # ... fetch from DB
    await redis.setex(cache_key, 60, json.dumps(result))
    return result
```

#### 9. Update README

- Correct port to 8099
- Document actual API endpoints
- Add WebSocket authentication docs

---

## Testing

### Test Structure

```
tests/
├── __init__.py
├── conftest.py          # Fixtures and DB setup
├── test_api.py          # API endpoint tests
└── test_health.py       # Health check tests
```

### Running Tests

```bash
# From service directory
cd apps/services/field-chat

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test class
pytest tests/test_health.py::TestHealthEndpoints -v
```

### Test Coverage

| Module | Coverage | Status |
|--------|----------|--------|
| Health endpoints | Good | Tested |
| Thread CRUD | Partial | Validation tested |
| Messages | Partial | Error cases tested |
| Events | Partial | Types tested |
| Repository | Partial | Helpers tested |
| WebSocket | None | Not tested |

### Test Fixtures

```python
@pytest.fixture
def client():
    """Create test client"""
    from src.main import app
    return TestClient(app)

@pytest.fixture
def db_available():
    """Check if database is available"""
    if not DB_AVAILABLE:
        pytest.skip("Database not available")
    return True
```

---

## Kong Gateway Configuration

```yaml
services:
  - name: field-chat
    host: field-chat
    port: 8099
    routes:
      - name: field-chat-api
        paths:
          - /api/v1/field-chat
        strip_path: true
      - name: field-chat-direct
        paths:
          - /field-chat
        strip_path: true
```

---

## Related Services

| Service | Interaction | Purpose |
|---------|-------------|---------|
| field-management-service | Consumer | Field context |
| task-service | Consumer | Task context |
| notification-service | Producer | Push notifications |
| user-service | Dependency | User validation |
| ws-gateway | Potential | WebSocket routing |

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 15.3.3 | 2025-12 | Current release |
| 16.0.0 | 2026-01 | Dockerfile/deps update |

---

*Last Updated: 2026-01-25*
*Generated by: SAHOOL Platform Analysis*
