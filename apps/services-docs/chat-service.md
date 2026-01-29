# Chat Service Analysis

## Service Overview

| Property | Value |
|----------|-------|
| **Service Name** | chat-service |
| **Version** | 16.0.0 |
| **Type** | Node.js (NestJS) |
| **Description** | SAHOOL Marketplace Chat Service - Real-time buyer-seller messaging for the agricultural marketplace |
| **Arabic Name** | خدمة المحادثات للسوق الزراعي |
| **Source Path** | `/home/user/sahool-unified-v15-idp/apps/services/chat-service/` |

### Key Features

- Real-time buyer-seller messaging using Socket.IO WebSocket
- Message history with pagination (offset-based and cursor-based)
- Typing indicators and read receipts
- Online/offline status tracking
- Product and order-linked conversations
- Support for text messages, images, and price offers
- JWT authentication with algorithm whitelist security

---

## Port Configuration

### CRITICAL: Port Mismatch Issue

| Source | Port | Status |
|--------|------|--------|
| **docker-compose.yml** | 8114 | Correct |
| **main.ts (default)** | 8114 | Correct |
| **Kong Gateway (User Context)** | 8000 | **INCORRECT** |
| **Kong Legacy Config** | chat-upstream -> 8099 | **INCORRECT** (points to field-chat) |

**Issue**: The Kong gateway configuration provided in the user context states `Host: chat-service, Port: 8000`, but the actual service runs on port **8114**. Additionally, the legacy Kong configuration (`infrastructure/gateway/kong-legacy/kong.yml`) routes `chat-service` to `chat-upstream` which targets `sahool-field-chat:8099` - a different deprecated service.

**Recommendation**: Update Kong configuration to:
```yaml
targets:
  - target: sahool-chat-service:8114
    weight: 100
```

---

## API Endpoints

### Health Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/api/v1/health` | No | Combined health check with dependencies |
| `GET` | `/api/v1/healthz` | No | Kubernetes liveness probe |
| `GET` | `/api/v1/readyz` | No | Kubernetes readiness probe |
| `GET` | `/api/v1/livez` | No | Liveness check |
| `GET` | `/api/v1/chat/health` | No | Chat controller health (rate limited: 10/min) |

#### Health Response Schema

```json
{
  "status": "healthy",
  "service": "chat-service",
  "version": "16.0.0",
  "timestamp": "2026-01-25T12:00:00.000Z",
  "uptime": "2h 30m",
  "dependencies": {
    "database": "connected"
  }
}
```

---

### Conversation Endpoints

#### Create Conversation

| Property | Value |
|----------|-------|
| **Method** | `POST` |
| **Path** | `/api/v1/chat/conversations` |
| **Auth** | None (should require JWT) |
| **Rate Limit** | Default (100/min) |

**Request Body** (`CreateConversationDto`):

```json
{
  "participantIds": ["user-123", "user-456"],
  "productId": "prod-789",
  "orderId": "order-101"
}
```

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| `participantIds` | `string[]` | Yes | Min 2 items, each must be string |
| `productId` | `string` | No | Product ID for context |
| `orderId` | `string` | No | Order ID for context |

**Response** (201 Created):

```json
{
  "id": "conv-uuid",
  "participantIds": ["user-123", "user-456"],
  "productId": "prod-789",
  "orderId": "order-101",
  "lastMessage": null,
  "lastMessageAt": null,
  "isActive": true,
  "createdAt": "2026-01-25T12:00:00.000Z",
  "updatedAt": "2026-01-25T12:00:00.000Z",
  "participants": [
    {
      "id": "part-uuid-1",
      "conversationId": "conv-uuid",
      "userId": "user-123",
      "role": "BUYER",
      "unreadCount": 0,
      "isOnline": false,
      "isTyping": false,
      "joinedAt": "2026-01-25T12:00:00.000Z"
    },
    {
      "id": "part-uuid-2",
      "conversationId": "conv-uuid",
      "userId": "user-456",
      "role": "SELLER",
      "unreadCount": 0,
      "isOnline": false,
      "isTyping": false,
      "joinedAt": "2026-01-25T12:00:00.000Z"
    }
  ],
  "messages": []
}
```

---

#### Get User Conversations

| Property | Value |
|----------|-------|
| **Method** | `GET` |
| **Path** | `/api/v1/chat/conversations/me` |
| **Auth** | JWT Required |

**Response** (200 OK):

```json
[
  {
    "id": "conv-uuid",
    "participantIds": ["user-123", "user-456"],
    "productId": "prod-789",
    "orderId": null,
    "lastMessage": "Hello, I'm interested in your wheat",
    "lastMessageAt": "2026-01-25T14:30:00.000Z",
    "isActive": true,
    "createdAt": "2026-01-25T12:00:00.000Z",
    "updatedAt": "2026-01-25T14:30:00.000Z",
    "unreadCount": 3,
    "lastReadAt": "2026-01-25T14:00:00.000Z",
    "messages": [
      {
        "id": "msg-uuid",
        "content": "Hello, I'm interested in your wheat",
        "senderId": "user-456",
        "messageType": "TEXT",
        "createdAt": "2026-01-25T14:30:00.000Z"
      }
    ]
  }
]
```

---

#### Get Conversation by ID

| Property | Value |
|----------|-------|
| **Method** | `GET` |
| **Path** | `/api/v1/chat/conversations/:id` |
| **Auth** | JWT Required |
| **Access Control** | User must be a participant |

**Path Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | `string` | Conversation ID |

**Response** (200 OK): Same as single conversation in list response

**Error Responses**:
- `401 Unauthorized`: User is not a participant
- `404 Not Found`: Conversation does not exist

---

#### Get Conversation Messages

| Property | Value |
|----------|-------|
| **Method** | `GET` |
| **Path** | `/api/v1/chat/conversations/:id/messages` |
| **Auth** | JWT Required |
| **Access Control** | User must be a participant |

**Query Parameters**:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | `number` | 1 | Page number |
| `limit` | `number` | 50 | Messages per page |

**Response** (200 OK):

```json
{
  "messages": [
    {
      "id": "msg-uuid-1",
      "conversationId": "conv-uuid",
      "senderId": "user-123",
      "content": "Hello!",
      "messageType": "TEXT",
      "attachmentUrl": null,
      "offerAmount": null,
      "offerCurrency": "YER",
      "isRead": true,
      "readAt": "2026-01-25T12:05:00.000Z",
      "createdAt": "2026-01-25T12:00:00.000Z",
      "updatedAt": "2026-01-25T12:05:00.000Z"
    }
  ],
  "total": 100,
  "page": 1,
  "limit": 50,
  "totalPages": 2
}
```

---

#### Send Message (REST Fallback)

| Property | Value |
|----------|-------|
| **Method** | `POST` |
| **Path** | `/api/v1/chat/messages` |
| **Auth** | JWT Required |

**Request Body** (`SendMessageDto`):

```json
{
  "conversationId": "conv-123",
  "senderId": "user-123",
  "content": "Hello, I am interested in buying your wheat harvest.",
  "messageType": "TEXT",
  "attachmentUrl": "https://cdn.sahool.com/images/product-photo.jpg",
  "offerAmount": 5000.00,
  "offerCurrency": "YER"
}
```

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| `conversationId` | `string` | Yes | Non-empty string |
| `senderId` | `string` | Yes | Non-empty string (overwritten by auth) |
| `content` | `string` | Yes | Max 10,000 chars, sanitized |
| `messageType` | `enum` | No | `TEXT`, `IMAGE`, `OFFER`, `SYSTEM` |
| `attachmentUrl` | `string` | No | Valid URL |
| `offerAmount` | `number` | No | Positive, max 2 decimal places |
| `offerCurrency` | `string` | No | Default: `YER` |

**Response** (201 Created):

```json
{
  "id": "msg-uuid",
  "conversationId": "conv-123",
  "senderId": "user-123",
  "content": "Hello, I am interested in buying your wheat harvest.",
  "messageType": "TEXT",
  "attachmentUrl": null,
  "offerAmount": null,
  "offerCurrency": "YER",
  "isRead": false,
  "readAt": null,
  "createdAt": "2026-01-25T12:00:00.000Z",
  "updatedAt": "2026-01-25T12:00:00.000Z"
}
```

---

#### Mark Message as Read

| Property | Value |
|----------|-------|
| **Method** | `POST` |
| **Path** | `/api/v1/chat/messages/:messageId/read` |
| **Auth** | JWT Required |

**Path Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `messageId` | `string` | Message ID |

**Response** (200 OK): Returns the updated message object

---

#### Mark Conversation as Read

| Property | Value |
|----------|-------|
| **Method** | `POST` |
| **Path** | `/api/v1/chat/conversations/:id/read` |
| **Auth** | JWT Required |
| **Access Control** | User must be a participant |

**Response** (200 OK):

```json
{
  "success": true,
  "conversationId": "conv-123"
}
```

---

#### Get Unread Message Count

| Property | Value |
|----------|-------|
| **Method** | `GET` |
| **Path** | `/api/v1/chat/unread-count` |
| **Auth** | JWT Required |

**Response** (200 OK):

```json
{
  "userId": "user-123",
  "unreadCount": 5
}
```

---

## WebSocket API

### Connection

| Property | Value |
|----------|-------|
| **Namespace** | `/chat` |
| **Protocol** | Socket.IO |
| **Port** | 8114 (same as HTTP) |
| **Auth** | JWT token in handshake |

**Connection URL**:
```
wss://api.sahool.com/chat
```

**Authentication**:
```javascript
const socket = io('/chat', {
  auth: {
    token: 'your-jwt-token'
  },
  // OR via query
  query: {
    token: 'your-jwt-token'
  }
});
```

### CORS Configuration

Allowed origins (configurable via `CORS_ALLOWED_ORIGINS`):
- `https://sahool.com`
- `https://app.sahool.com`
- `http://localhost:3000`
- `http://localhost:8080`

---

### WebSocket Events

#### Client-to-Server Events

| Event | Payload | Description |
|-------|---------|-------------|
| `join_conversation` | `JoinConversationDto` | Join a conversation room |
| `leave_conversation` | `{ conversationId: string }` | Leave a conversation room |
| `send_message` | `SendMessageDto` | Send a message |
| `typing` | `TypingIndicatorDto` | Send typing indicator |
| `read_receipt` | `ReadReceiptDto` | Mark message as read |
| `mark_conversation_read` | `{ conversationId: string }` | Mark all messages read |

#### Server-to-Client Events

| Event | Payload | Description |
|-------|---------|-------------|
| `error` | `{ message: string }` | Error notification |
| `joined_conversation` | `{ conversationId, userId, timestamp }` | Successfully joined |
| `left_conversation` | `{ conversationId, userId }` | Successfully left |
| `message_received` | `{ message, timestamp }` | New message in room |
| `message_sent` | `{ message }` | Message sent confirmation |
| `typing_indicator` | `{ conversationId, userId, isTyping, timestamp }` | User typing status |
| `typing_updated` | `{ conversationId, userId, isTyping }` | Typing update confirmation |
| `message_read` | `{ conversationId, messageId, userId, timestamp }` | Message read notification |
| `read_receipt_sent` | `{ messageId, userId }` | Read receipt confirmation |
| `conversation_read` | `{ conversationId, userId, timestamp }` | Conversation read notification |
| `conversation_marked_read` | `{ conversationId, userId }` | Read confirmation |
| `user_online` | `{ userId, timestamp }` | User came online |
| `user_offline` | `{ userId, timestamp }` | User went offline |

---

### WebSocket DTOs

#### JoinConversationDto

```typescript
{
  conversationId: string;  // Required
  userId: string;          // Required (validated against auth)
}
```

#### TypingIndicatorDto

```typescript
{
  conversationId: string;  // Required
  userId: string;          // Required
  isTyping: boolean;       // Required
}
```

#### ReadReceiptDto

```typescript
{
  conversationId: string;  // Required
  userId: string;          // Required
  messageId: string;       // Required
}
```

---

## Database Schema

### Conversation Model

```prisma
model Conversation {
  id             String   @id @default(uuid())
  participantIds String[] @map("participant_ids")
  productId      String?  @map("product_id")
  orderId        String?  @map("order_id")
  lastMessage    String?  @map("last_message")
  lastMessageAt  DateTime? @map("last_message_at")
  isActive       Boolean  @default(true) @map("is_active")
  createdAt      DateTime @default(now()) @map("created_at")
  updatedAt      DateTime @updatedAt @map("updated_at")

  messages     Message[]
  participants Participant[]
}
```

**Indexes**:
- `productId`
- `orderId`
- `[isActive, lastMessageAt]` - Active conversations sorted by recent activity
- `[isActive]` - Filter active conversations

---

### Message Model

```prisma
model Message {
  id             String      @id @default(uuid())
  conversationId String      @map("conversation_id")
  senderId       String      @map("sender_id")
  content        String
  messageType    MessageType @default(TEXT) @map("message_type")
  attachmentUrl  String?     @map("attachment_url")
  offerAmount    Float?      @map("offer_amount")
  offerCurrency  String?     @default("YER") @map("offer_currency")
  isRead         Boolean     @default(false) @map("is_read")
  readAt         DateTime?   @map("read_at")
  createdAt      DateTime    @default(now()) @map("created_at")
  updatedAt      DateTime    @updatedAt @map("updated_at")

  conversation   Conversation @relation(...)
}

enum MessageType {
  TEXT    // رسالة نصية
  IMAGE   // صورة
  OFFER   // عرض سعر
  SYSTEM  // رسالة النظام
}
```

**Indexes**:
- `conversationId`
- `senderId`
- `createdAt`
- `[conversationId, senderId, isRead]` - Optimize unread count queries
- `[conversationId, createdAt]` - Optimize message pagination

---

### Participant Model

```prisma
model Participant {
  id             String          @id @default(uuid())
  conversationId String          @map("conversation_id")
  userId         String          @map("user_id")
  role           ParticipantRole @default(BUYER)
  lastReadAt     DateTime?       @map("last_read_at")
  unreadCount    Int             @default(0) @map("unread_count")
  isOnline       Boolean         @default(false) @map("is_online")
  lastSeenAt     DateTime?       @map("last_seen_at")
  isTyping       Boolean         @default(false) @map("is_typing")
  joinedAt       DateTime        @default(now()) @map("joined_at")

  conversation   Conversation @relation(...)
}

enum ParticipantRole {
  BUYER   // مشتري
  SELLER  // بائع
}
```

**Indexes**:
- `userId`
- `conversationId`
- `[userId, isOnline]` - Optimize online user queries
- **Unique**: `[conversationId, userId]`

---

## NATS Events

### Current Status: NOT IMPLEMENTED

The chat-service has NATS configured in the environment variables but **does not currently publish or subscribe to any NATS events**. The codebase uses Socket.IO for real-time communication instead.

**Environment Variable** (unused):
```bash
NATS_URL=nats://${NATS_USER}:${NATS_PASSWORD}@nats:4222
```

### Recommended Events (Future Implementation)

| Event Subject | Direction | Payload | Description |
|---------------|-----------|---------|-------------|
| `sahool.{tenant_id}.chat.message.sent` | Publish | `{ conversationId, messageId, senderId, content, timestamp }` | Message sent notification |
| `sahool.{tenant_id}.chat.conversation.created` | Publish | `{ conversationId, participantIds, productId }` | New conversation created |
| `sahool.{tenant_id}.chat.user.online` | Publish | `{ userId, timestamp }` | User online status |
| `sahool.{tenant_id}.notification.send` | Subscribe | `{ userId, type, payload }` | Receive push notification requests |

---

## Dependencies

### Production Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `@nestjs/common` | ^10.4.15 | NestJS core |
| `@nestjs/core` | ^10.4.15 | NestJS core |
| `@nestjs/platform-express` | ^10.4.15 | HTTP adapter |
| `@nestjs/platform-socket.io` | ^10.4.15 | Socket.IO adapter |
| `@nestjs/swagger` | ^8.1.0 | OpenAPI documentation |
| `@nestjs/throttler` | ^6.2.1 | Rate limiting |
| `@nestjs/websockets` | ^10.4.15 | WebSocket support |
| `@prisma/client` | ^5.22.0 | Database ORM |
| `prisma` | ^5.22.0 | Prisma CLI |
| `class-transformer` | ^0.5.1 | DTO transformation |
| `class-validator` | ^0.14.1 | DTO validation |
| `jsonwebtoken` | ^9.0.2 | JWT authentication |
| `reflect-metadata` | ^0.2.2 | Decorator metadata |
| `rxjs` | ^7.8.1 | Reactive extensions |
| `socket.io` | ^4.8.1 | WebSocket library |
| `nestjs-pino` | ^4.1.0 | Structured logging |
| `pino-http` | ^10.3.0 | HTTP logging |
| `pino-pretty` | ^13.0.0 | Log formatting |

### Development Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `@nestjs/cli` | ^10.4.9 | NestJS CLI |
| `@nestjs/testing` | ^10.4.15 | Testing utilities |
| `@types/express` | ^5.0.0 | Express types |
| `@types/jest` | ^30.0.0 | Jest types |
| `@types/jsonwebtoken` | ^9.0.7 | JWT types |
| `@types/node` | ^22.10.2 | Node.js types |
| `jest` | ^30.2.0 | Testing framework |
| `ts-jest` | ^29.4.6 | TypeScript Jest transformer |
| `typescript` | ^5.7.2 | TypeScript compiler |

### Engine Requirements

```json
{
  "engines": {
    "node": ">=20.0.0"
  }
}
```

---

## Environment Variables

### Required

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string via PgBouncer | `postgresql://user:pass@pgbouncer:6432/sahool` |
| `JWT_SECRET_KEY` | JWT signing secret (min 32 chars) | `your-32-char-minimum-secret-key` |

### Optional

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Service port | `8114` |
| `NODE_ENV` | Environment mode | `development` |
| `REDIS_URL` | Redis connection URL | `redis://:password@redis:6379/0` |
| `NATS_URL` | NATS connection URL (currently unused) | `nats://user:pass@nats:4222` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `CORS_ALLOWED_ORIGINS` | Comma-separated allowed origins | See defaults |
| `DATABASE_URL_DIRECT` | Direct DB URL for migrations | Same as DATABASE_URL |
| `ENVIRONMENT` | Environment name | `development` |

### Missing Environment Variables

The following variables are referenced in code but may not be documented:

| Variable | Location | Status |
|----------|----------|--------|
| `JWT_SECRET` | `jwt-auth.guard.ts` | Fallback for `JWT_SECRET_KEY` |
| `CORS_ALLOWED_ORIGINS` | `main.ts`, `chat.gateway.ts` | Optional, has defaults |

---

## Rate Limiting

### Global Configuration

| Tier | TTL | Limit | Description |
|------|-----|-------|-------------|
| Short | 1s | 10 | Burst protection |
| Medium | 1min | 100 | Normal usage |
| Long | 1hr | 1000 | Sustained usage |

### Endpoint-Specific

| Endpoint | Limit | TTL |
|----------|-------|-----|
| `/api/v1/chat/health` | 10 | 60s |

---

## Security Features

### JWT Authentication

- **Algorithm Whitelist**: `HS256`, `HS384`, `HS512`, `RS256`, `RS384`, `RS512`
- **Explicitly Rejected**: `none` algorithm (CVE protection)
- **Token Sources**: `Authorization: Bearer <token>` header, WebSocket handshake auth/query

### Input Sanitization

- **Plain Text Sanitization**: Removes HTML tags, decodes entities, normalizes whitespace
- **Iterative Decoding**: Handles nested/encoded HTML (max 5 iterations)
- **Control Character Removal**: Strips null bytes and control characters
- **Money Value Validation**: Positive numbers, max 2 decimal places

### WebSocket Security

- **Authentication Required**: Connection rejected without valid JWT
- **User ID Verification**: Server-side user ID from token, not client input
- **Participant Verification**: Users can only join conversations they're part of
- **Stale Connection Cleanup**: 30-minute timeout, 5-minute cleanup interval
- **Log Injection Prevention**: Sanitized logging of user input

### CORS

- Configurable allowed origins
- Credentials support enabled
- Allowed headers: `Content-Type`, `Authorization`, `X-Tenant-ID`, `X-Request-ID`

---

## Swagger Documentation

Available at: `http://localhost:8114/docs`

### Tags

- **Chat**: Chat conversation management
- **Messages**: Message operations
- **Health**: Health check endpoints

### Authentication

- Bearer token authentication
- API key header: `X-Tenant-ID`

---

## Docker Configuration

### Healthcheck

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8114/api/v1/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 15s
```

### Resource Limits

```yaml
deploy:
  resources:
    limits:
      cpus: '0.5'
```

### Security Options

```yaml
security_opt:
  - no-new-privileges:true
```

---

## Related Services

| Service | Relationship | Port |
|---------|--------------|------|
| **community-chat** | Deprecated predecessor | 8097 |
| **field-chat** | Deprecated (legacy) | 8099 |
| **marketplace-service** | Product/Order context | 3010 |
| **user-service** | User authentication | 3025 |
| **notification-service** | Push notifications | 8110 |

---

## Test Coverage

### Test Files

| File | Description |
|------|-------------|
| `src/__tests__/chat.controller.spec.ts` | Controller unit tests |
| `src/__tests__/chat.service.spec.ts` | Service unit tests |
| `src/__tests__/conversation.service.spec.ts` | Conversation operations |
| `src/__tests__/message.service.spec.ts` | Message operations |
| `src/__tests__/websocket.gateway.spec.ts` | WebSocket gateway tests |
| `test/chat.service.spec.ts` | Integration tests |

### Commands

```bash
npm run test           # Run all tests
npm run test:watch     # Watch mode
npm run test:cov       # Coverage report
```

---

## Known Issues

### 1. Port Mismatch (CRITICAL)

**Issue**: Kong gateway configuration does not match actual service port.

**Current State**:
- Service runs on port 8114
- Kong may be routing to wrong port/service

**Resolution**: Update Kong upstream configuration to target `sahool-chat-service:8114`

### 2. NATS Integration Not Implemented

**Issue**: NATS URL is configured but not used in the codebase.

**Impact**: No event-driven integration with other services.

**Recommendation**: Implement NATS event publishing for:
- Message sent notifications
- User presence updates
- Integration with notification-service

### 3. Create Conversation Endpoint Lacks Authentication

**Issue**: `POST /api/v1/chat/conversations` does not require JWT authentication.

**Impact**: Potential unauthorized conversation creation.

**Recommendation**: Add `@UseGuards(JwtAuthGuard)` decorator.

---

## File Structure

```
apps/services/chat-service/
├── Dockerfile
├── package.json
├── tsconfig.json
├── nest-cli.json
├── prisma/
│   └── schema.prisma
├── src/
│   ├── main.ts                    # Application entry point
│   ├── app.module.ts              # Root module
│   ├── auth/
│   │   ├── decorators.ts          # @CurrentUser, @UserId
│   │   └── jwt-auth.guard.ts      # JWT validation guard
│   ├── chat/
│   │   ├── chat.controller.ts     # REST API endpoints
│   │   ├── chat.gateway.ts        # WebSocket gateway
│   │   ├── chat.service.ts        # Business logic
│   │   └── dto/
│   │       ├── create-conversation.dto.ts
│   │       ├── send-message.dto.ts
│   │       ├── join-conversation.dto.ts
│   │       ├── typing-indicator.dto.ts
│   │       └── read-receipt.dto.ts
│   ├── health/
│   │   └── health.controller.ts   # Health endpoints
│   ├── prisma/
│   │   └── prisma.service.ts      # Database connection
│   ├── utils/
│   │   ├── db-utils.ts            # Transaction configs
│   │   ├── validation.ts          # Custom validators
│   │   ├── http-exception.filter.ts
│   │   ├── pino-logger.config.ts
│   │   └── request-logging.interceptor.ts
│   └── __tests__/                 # Unit tests
└── test/                          # Integration tests
```

---

## Changelog

### Version 16.0.0

- Initial implementation of marketplace chat service
- Real-time messaging with Socket.IO
- JWT authentication with algorithm whitelist
- Prisma ORM for database operations
- Rate limiting with @nestjs/throttler
- Structured logging with Pino

---

*Document generated: 2026-01-25*
*Service Version: 16.0.0*
*Analysis Path: `/home/user/sahool-unified-v15-idp/apps/services/chat-service/`*
