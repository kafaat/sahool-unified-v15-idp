# SAHOOL Chat Service v16.0.0

## خدمة المحادثات للسوق الزراعي

Real-time buyer-seller messaging service for the SAHOOL agricultural marketplace platform.

## Features

- **Real-time Messaging**: Socket.IO WebSocket for instant communication
- **Buyer-Seller Chat**: Direct messaging between buyers and sellers
- **Product Context**: Link conversations to specific products in the marketplace
- **Order Integration**: Associate chats with marketplace orders
- **Rich Messages**: Support for text, images, and price offers
- **Read Receipts**: Track message delivery and read status
- **Typing Indicators**: Real-time typing notifications
- **Online Status**: Track user presence (online/offline)
- **Message History**: Paginated message retrieval
- **Unread Count**: Track unread messages per conversation

## Architecture

### Technology Stack

- **Framework**: NestJS 10.x
- **WebSocket**: Socket.IO 4.8.x
- **Database**: PostgreSQL with Prisma 5.x ORM
- **Language**: TypeScript 5.x
- **Container**: Docker (multi-stage build)

### Database Models

#### Conversation

- Manages chat conversations between users
- Links to products and orders
- Tracks last message and activity

#### Message

- Stores chat messages
- Supports multiple types: TEXT, IMAGE, OFFER, SYSTEM
- Tracks read status and timestamps

#### Participant

- Manages conversation participants
- Tracks roles (BUYER/SELLER)
- Monitors online status and typing indicators
- Maintains unread message counts

## API Endpoints (REST)

### Health Check

```
GET /api/v1/chat/health
```

### Conversations

```
POST   /api/v1/chat/conversations              - Create new conversation
GET    /api/v1/chat/conversations/user/:userId - Get user's conversations
GET    /api/v1/chat/conversations/:id          - Get conversation details
GET    /api/v1/chat/conversations/:id/messages - Get conversation messages (paginated)
POST   /api/v1/chat/conversations/:id/read     - Mark conversation as read
```

### Messages

```
POST   /api/v1/chat/messages                   - Send message (REST fallback)
POST   /api/v1/chat/messages/:messageId/read   - Mark message as read
```

### User

```
GET    /api/v1/chat/users/:userId/unread-count - Get unread message count
```

## WebSocket Events (Socket.IO)

### Client -> Server Events

#### join_conversation

Join a conversation room to receive real-time updates.

```javascript
socket.emit("join_conversation", {
  conversationId: "conv-123",
  userId: "user-456",
});
```

#### send_message

Send a message to a conversation.

```javascript
socket.emit("send_message", {
  conversationId: "conv-123",
  senderId: "user-456",
  content: "Hello, I am interested in your wheat harvest",
  messageType: "TEXT",
});
```

#### typing

Indicate that user is typing.

```javascript
socket.emit("typing", {
  conversationId: "conv-123",
  userId: "user-456",
  isTyping: true,
});
```

#### read_receipt

Mark a message as read.

```javascript
socket.emit("read_receipt", {
  conversationId: "conv-123",
  userId: "user-456",
  messageId: "msg-789",
});
```

#### mark_conversation_read

Mark all messages in a conversation as read.

```javascript
socket.emit("mark_conversation_read", {
  conversationId: "conv-123",
  userId: "user-456",
});
```

#### leave_conversation

Leave a conversation room.

```javascript
socket.emit("leave_conversation", {
  conversationId: "conv-123",
  userId: "user-456",
});
```

### Server -> Client Events

#### message_received

Receive a new message.

```javascript
socket.on("message_received", (data) => {
  console.log("New message:", data.message);
});
```

#### typing_indicator

Receive typing indicator updates.

```javascript
socket.on("typing_indicator", (data) => {
  console.log(`${data.userId} is typing: ${data.isTyping}`);
});
```

#### message_read

Notification that a message was read.

```javascript
socket.on("message_read", (data) => {
  console.log(`Message ${data.messageId} read by ${data.userId}`);
});
```

#### user_online

User came online.

```javascript
socket.on("user_online", (data) => {
  console.log(`User ${data.userId} is online`);
});
```

#### user_offline

User went offline.

```javascript
socket.on("user_offline", (data) => {
  console.log(`User ${data.userId} is offline`);
});
```

## Environment Variables

```env
# Server
PORT=3015
NODE_ENV=production

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/sahool_chat

# CORS
CORS_ALLOWED_ORIGINS=https://sahool.com,https://app.sahool.com,http://localhost:3000
```

## Installation & Setup

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Database

Create a `.env` file:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/sahool_chat
PORT=3015
```

### 3. Generate Prisma Client

```bash
npm run prisma:generate
```

### 4. Run Database Migrations

```bash
npm run prisma:migrate
# or for development
npm run prisma:push
```

### 5. Start Development Server

```bash
npm run start:dev
```

### 6. Access API Documentation

Open http://localhost:3015/docs for Swagger documentation.

## Docker Deployment

### Build Image

```bash
docker build -t sahool-chat-service:16.0.0 .
```

### Run Container

```bash
docker run -d \
  -p 3015:3015 \
  -e DATABASE_URL=postgresql://user:password@db:5432/sahool_chat \
  -e PORT=3015 \
  --name chat-service \
  sahool-chat-service:16.0.0
```

## Client Integration Example

### JavaScript/TypeScript

```typescript
import { io } from "socket.io-client";

// Connect to chat service
const socket = io("ws://localhost:3015/chat", {
  query: { userId: "user-123" },
});

// Join conversation
socket.emit("join_conversation", {
  conversationId: "conv-456",
  userId: "user-123",
});

// Listen for messages
socket.on("message_received", (data) => {
  console.log("New message:", data.message);
  // Update UI with new message
});

// Send message
socket.emit("send_message", {
  conversationId: "conv-456",
  senderId: "user-123",
  content: "Hello!",
  messageType: "TEXT",
});

// Typing indicator
socket.emit("typing", {
  conversationId: "conv-456",
  userId: "user-123",
  isTyping: true,
});
```

## Message Types

### TEXT

Standard text message.

### IMAGE

Image message with URL.

```javascript
{
  messageType: 'IMAGE',
  content: 'Check out this photo',
  attachmentUrl: 'https://cdn.sahool.com/images/photo.jpg'
}
```

### OFFER

Price offer message.

```javascript
{
  messageType: 'OFFER',
  content: 'I can offer you this price',
  offerAmount: 5000.0,
  offerCurrency: 'YER'
}
```

### SYSTEM

System-generated message.

```javascript
{
  messageType: 'SYSTEM',
  content: 'Order #12345 has been confirmed'
}
```

## Testing

### Run Tests

```bash
npm test
```

### Run Tests with Coverage

```bash
npm run test:cov
```

### Watch Mode

```bash
npm run test:watch
```

## Production Considerations

1. **Authentication**: Implement JWT authentication for WebSocket connections
2. **Rate Limiting**: Add rate limiting to prevent message spam
3. **Message Validation**: Implement content moderation and filtering
4. **Scalability**: Use Redis adapter for Socket.IO clustering
5. **Monitoring**: Add logging and monitoring (e.g., Prometheus, Grafana)
6. **Database**: Enable connection pooling and optimize queries
7. **Backups**: Regular database backups for message history
8. **File Storage**: Use CDN (e.g., S3) for image attachments

## Service Integration

This chat service integrates with:

- **Marketplace Service**: Links conversations to products and orders
- **User Service**: Retrieves user profiles and authentication
- **Notification Service**: Sends push notifications for new messages

## License

MIT License - SAHOOL Team

## Support

For support and questions, contact the SAHOOL development team.
