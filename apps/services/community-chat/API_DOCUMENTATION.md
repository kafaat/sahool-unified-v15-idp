# Sahool Community Chat Service - API Documentation
# توثيق خدمة الدردشة الحية لمجتمع سهول

## 📚 Overview / نظرة عامة

خدمة الدردشة الحية لمنصة سهول توفر اتصال فوري بين المزارعين والخبراء الزراعيين. تستخدم الخدمة Socket.io للرسائل الفورية و REST API لإدارة الجلسات والبيانات.

This service provides real-time chat communication between farmers and agricultural experts on the Sahool platform. It uses Socket.io for real-time messaging and REST API for session management.

## 🚀 Quick Start / البدء السريع

### 1. Install Dependencies / تثبيت المتطلبات

```bash
cd apps/services/community-chat
npm install
```

### 2. Set Environment Variables / تعيين متغيرات البيئة

```bash
export JWT_SECRET_KEY="your-secret-key-here"
export PORT=8097
export CHAT_REQUIRE_AUTH=true
export CORS_ORIGINS="http://localhost:3000,http://localhost:3001"
```

### 3. Start Service / تشغيل الخدمة

```bash
npm start
# or for development with auto-reload
npm run dev
```

## 📖 API Documentation Access / الوصول للتوثيق

Once the service is running, you can access the API documentation at:

بعد تشغيل الخدمة، يمكنك الوصول للتوثيق عبر:

### Swagger UI (Interactive)
**URL:** http://localhost:8097/api-docs

واجهة Swagger التفاعلية تتيح لك:
- استعراض جميع endpoints
- اختبار الـ API مباشرة من المتصفح
- رؤية أمثلة على الطلبات والردود
- فهم بنية البيانات (schemas)

### OpenAPI JSON
**URL:** http://localhost:8097/api-docs.json

مواصفات OpenAPI بصيغة JSON لاستخدامها في:
- أدوات توليد الكود (code generators)
- أدوات الاختبار (testing tools)
- الاستيراد إلى Postman

### ReDoc (Alternative UI)
**URL:** http://localhost:8097/redoc

واجهة بديلة أنيقة وسهلة القراءة للتوثيق.

## 🔌 WebSocket Connection / الاتصال عبر WebSocket

### Client Example / مثال للعميل

```javascript
const io = require('socket.io-client');

// Connect to service
const socket = io('http://localhost:8097', {
  auth: {
    token: 'your-jwt-token-here'
  }
});

// Handle connection
socket.on('connect', () => {
  console.log('Connected:', socket.id);

  // Register user
  socket.emit('register_user', {
    userId: '12345',
    userName: 'محمد أحمد',
    userType: 'farmer',
    governorate: 'القاهرة'
  });
});

// Handle registration confirmation
socket.on('registration_confirmed', (data) => {
  console.log('Registered successfully:', data);
});

// Handle errors
socket.on('error', (error) => {
  console.error('Error:', error);
});

// Disconnect
socket.on('disconnect', () => {
  console.log('Disconnected');
});
```

## 🔐 Authentication / المصادقة

All connections require JWT authentication. The token must include:

جميع الاتصالات تتطلب مصادقة JWT. يجب أن يحتوي التوكن على:

```json
{
  "sub": "user-id",
  "role": "farmer|expert|admin",
  "iat": 1234567890,
  "exp": 1234567890
}
```

## 📡 REST API Endpoints

### Health Check
```http
GET /healthz
```
Check service health and get current statistics.

**Response:**
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

### Get Support Requests
```http
GET /v1/requests?status=pending
```
Retrieve support requests, optionally filtered by status.

**Query Parameters:**
- `status` (optional): `pending`, `active`, `resolved`, `closed`

### Get Room Messages
```http
GET /v1/rooms/{roomId}/messages
```
Get message history for a specific room.

**Path Parameters:**
- `roomId` (required): Room identifier

### Get Online Experts
```http
GET /v1/experts/online
```
Get count of currently online experts.

**Response:**
```json
{
  "count": 5,
  "available": true
}
```

### Get Statistics
```http
GET /v1/stats
```
Get comprehensive service statistics.

## 🎯 WebSocket Events

### Client → Server Events

#### register_user
Register user on connection.

```javascript
socket.emit('register_user', {
  userId: '12345',
  userName: 'محمد أحمد',
  userType: 'farmer',
  governorate: 'القاهرة'
});
```

#### join_room
Join a chat room.

```javascript
socket.emit('join_room', {
  roomId: 'support_12345_1735295400000',
  userName: 'محمد أحمد',
  userType: 'farmer'
});
```

#### send_message
Send a message to a room.

```javascript
socket.emit('send_message', {
  roomId: 'support_12345_1735295400000',
  author: 'محمد أحمد',
  authorType: 'farmer',
  message: 'السلام عليكم، أحتاج استشارة',
  attachments: []
});
```

#### typing_start / typing_stop
Indicate typing status.

```javascript
socket.emit('typing_start', {
  roomId: 'support_12345_1735295400000',
  userName: 'محمد أحمد'
});
```

#### request_expert
Farmer requests expert assistance.

```javascript
socket.emit('request_expert', {
  farmerId: '12345',
  farmerName: 'محمد أحمد',
  governorate: 'القاهرة',
  topic: 'مرض في نباتات الطماطم',
  diagnosisId: 'diag_98765'
});
```

#### accept_request
Expert accepts a support request.

```javascript
socket.emit('accept_request', {
  roomId: 'support_12345_1735295400000',
  expertId: 'expert_123',
  expertName: 'د. أحمد الخبير'
});
```

#### leave_room
Leave a chat room.

```javascript
socket.emit('leave_room', {
  roomId: 'support_12345_1735295400000',
  userName: 'محمد أحمد'
});
```

### Server → Client Events

#### registration_confirmed
Confirmation of successful registration.

```javascript
socket.on('registration_confirmed', (data) => {
  // { success: true, socketId: 'abc123', onlineExperts: 5 }
});
```

#### load_history
Receive room message history when joining.

```javascript
socket.on('load_history', (messages) => {
  // Array of message objects
});
```

#### receive_message
Receive a new message in a room.

```javascript
socket.on('receive_message', (message) => {
  // Message object with id, author, content, timestamp, etc.
});
```

#### user_joined / user_left
Notification when users join or leave a room.

```javascript
socket.on('user_joined', (data) => {
  // { userName: 'محمد', userType: 'farmer', time: '...' }
});
```

#### user_typing
Typing indicator for room participants.

```javascript
socket.on('user_typing', (data) => {
  // { userName: 'محمد', isTyping: true }
});
```

#### expert_online / expert_offline
Expert presence notifications.

```javascript
socket.on('expert_online', (data) => {
  // { expertId: 'expert_123', expertName: 'د. أحمد' }
});
```

#### new_support_request
Broadcast to all experts about new support request.

```javascript
socket.on('new_support_request', (request) => {
  // Support request object
});
```

#### expert_joined
Notification that expert has joined a support session.

```javascript
socket.on('expert_joined', (data) => {
  // { expertId: '...', expertName: '...', message: '...' }
});
```

#### error
Error notifications.

```javascript
socket.on('error', (error) => {
  // { code: 'ACCESS_DENIED', message: 'لا يمكنك الوصول لهذه الغرفة' }
});
```

## 🔒 Security Features / الميزات الأمنية

### JWT Authentication / مصادقة JWT
- Required for all connections / مطلوبة لجميع الاتصالات
- Token must be valid and not expired / يجب أن يكون التوكن صالحاً وغير منتهي الصلاحية
- Subject (sub) and role fields required / حقول sub و role مطلوبة

### Room Access Control / التحكم بالوصول للغرف
- Support rooms: Only farmer, assigned expert, or admin / غرف الدعم: المزارع أو الخبير المعين أو المشرف فقط
- Room ID validation / التحقق من معرف الغرفة
- User type validation / التحقق من نوع المستخدم

### Message Validation / التحقق من الرسائل
- HTML escaping (XSS prevention) / تجنب HTML لمنع هجمات XSS
- Message length limits (10,000 chars) / حد أقصى لطول الرسالة (10,000 حرف)
- Attachment URL validation / التحقق من روابط المرفقات
- Maximum 10 attachments per message / حد أقصى 10 مرفقات لكل رسالة

### CORS Protection / حماية CORS
- Configurable allowed origins / أصول مسموحة قابلة للتكوين
- Credentials support / دعم بيانات الاعتماد

## 📊 Monitoring & Statistics / المراقبة والإحصائيات

The service provides real-time statistics through the `/v1/stats` endpoint:

الخدمة توفر إحصائيات فورية عبر endpoint `/v1/stats`:

- Total active connections / إجمالي الاتصالات النشطة
- Online experts count / عدد الخبراء المتصلين
- Active chat rooms / الغرف النشطة
- Total messages / إجمالي الرسائل

## 🧪 Testing the API / اختبار الـ API

### Using Swagger UI / استخدام Swagger UI

1. Open http://localhost:8097/api-docs
2. Select an endpoint to test
3. Click "Try it out"
4. Fill in required parameters
5. Click "Execute"

### Using cURL

```bash
# Health check
curl http://localhost:8097/healthz

# Get online experts
curl http://localhost:8097/v1/experts/online

# Get support requests
curl http://localhost:8097/v1/requests?status=pending

# Get room messages
curl http://localhost:8097/v1/rooms/support_12345_1735295400000/messages
```

### Using Postman

1. Import OpenAPI spec from http://localhost:8097/api-docs.json
2. All endpoints will be auto-configured
3. Test each endpoint with sample data

## 📝 Data Models / نماذج البيانات

### Message
```typescript
{
  id: string;              // UUID
  roomId: string;          // Room identifier
  author: string;          // Author name
  authorType: 'farmer' | 'expert' | 'admin' | 'support' | 'system';
  message: string;         // Message content (HTML-escaped)
  attachments: Attachment[];
  timestamp: string;       // ISO 8601 date-time
  status: 'sent' | 'delivered' | 'read' | 'failed';
}
```

### Support Request
```typescript
{
  roomId: string;          // Unique room ID
  farmerId: string;        // Farmer's user ID
  farmerName: string;      // Farmer's display name
  governorate: string;     // Farmer's governorate
  topic: string;           // Request topic
  diagnosisId?: string;    // Related diagnosis ID (optional)
  status: 'pending' | 'active' | 'resolved' | 'closed';
  expertId?: string;       // Assigned expert ID (optional)
  expertName?: string;     // Assigned expert name (optional)
  createdAt: string;       // ISO 8601 date-time
  acceptedAt?: string;     // ISO 8601 date-time (optional)
}
```

### Attachment
```typescript
{
  url: string;             // Must be from allowed domains
  type: 'image' | 'document' | 'video' | 'audio';
  name: string;            // Filename
  size: number;            // Size in bytes
}
```

## 🔧 Configuration / التكوين

### Environment Variables / متغيرات البيئة

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `PORT` | Service port | 8097 | No |
| `JWT_SECRET_KEY` | JWT secret for token verification | - | **Yes** |
| `CHAT_REQUIRE_AUTH` | Require authentication | true | No |
| `CORS_ORIGINS` | Allowed CORS origins (comma-separated) | See code | No |

### Production Recommendations / توصيات الإنتاج

1. **Use Redis** for message history and state management instead of in-memory storage
   استخدم Redis لتخزين سجل الرسائل بدلاً من الذاكرة

2. **Enable rate limiting** to prevent abuse
   فعّل تحديد معدل الطلبات لمنع الإساءة

3. **Use HTTPS** for all connections
   استخدم HTTPS لجميع الاتصالات

4. **Monitor performance** using the stats endpoint
   راقب الأداء باستخدام endpoint الإحصائيات

5. **Set up logging** for audit trails
   أنشئ نظام تسجيل للمراجعة

## 🐛 Error Codes / رموز الأخطاء

| Code | Description (EN) | Description (AR) |
|------|------------------|------------------|
| `INVALID_ROOM_ID` | Invalid room identifier | معرف الغرفة غير صالح |
| `INVALID_USERNAME` | Invalid username | اسم المستخدم غير صالح |
| `INVALID_USER_TYPE` | Invalid user type | نوع المستخدم غير صالح |
| `INVALID_AUTHOR` | Invalid message author | مؤلف الرسالة غير صالح |
| `INVALID_MESSAGE` | Invalid message content | محتوى الرسالة غير صالح |
| `MESSAGE_TOO_LONG` | Message exceeds length limit | الرسالة طويلة جداً |
| `ACCESS_DENIED` | No permission to access room | لا يمكنك الوصول لهذه الغرفة |

## 📞 Support / الدعم

For issues or questions:
للمشاكل أو الاستفسارات:

- Check API documentation at `/api-docs`
- Review this README
- Contact: support@sahool.io

## 📄 License / الترخيص

Proprietary - Sahool Platform

---

**Built with ❤️ for Sahool Agricultural Platform**
**مبني بكل ❤️ لمنصة سهول الزراعية**
