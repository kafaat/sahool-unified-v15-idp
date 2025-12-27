# Quick Start Guide - Sahool Community Chat
# دليل البدء السريع - خدمة الدردشة

## ⚡ 5-Minute Setup / الإعداد في 5 دقائق

### Step 1: Install Dependencies / الخطوة 1: تثبيت المتطلبات

```bash
cd apps/services/community-chat
npm install
```

### Step 2: Configure Environment / الخطوة 2: تكوين البيئة

Create a `.env` file or export variables:

```bash
export JWT_SECRET_KEY="your-secret-key-minimum-32-characters-long"
export PORT=8097
```

### Step 3: Start Service / الخطوة 3: تشغيل الخدمة

```bash
npm start
```

You should see:
```
╔═══════════════════════════════════════════════════════════════╗
║         🌿 Sahool Community Chat Service 🌿                   ║
║                                                               ║
║   Service: community-chat     Version: 1.0.0                 ║
║   Port: 8097                                                  ║
║                                                               ║
║   خدمة الدردشة الحية لمجتمع سهول الزراعي                     ║
╚═══════════════════════════════════════════════════════════════╝

📚 Swagger documentation available at:
   • Swagger UI: http://localhost:8097/api-docs
   • OpenAPI JSON: http://localhost:8097/api-docs.json
   • ReDoc: http://localhost:8097/redoc
```

### Step 4: Explore API / الخطوة 4: استكشاف الـ API

Open in your browser:
- **Swagger UI**: http://localhost:8097/api-docs
- **ReDoc**: http://localhost:8097/redoc

### Step 5: Test Health / الخطوة 5: اختبار الصحة

```bash
curl http://localhost:8097/healthz
```

Expected response:
```json
{
  "status": "healthy",
  "service": "community-chat",
  "version": "1.0.0",
  "activeConnections": 0,
  "onlineExperts": 0,
  "activeRooms": 0,
  "timestamp": "2025-12-27T10:30:00.000Z"
}
```

## 🔌 WebSocket Quick Test / اختبار سريع للـ WebSocket

### Using Node.js

```javascript
const io = require('socket.io-client');

const socket = io('http://localhost:8097', {
  auth: { token: 'your-jwt-token' }
});

socket.on('connect', () => {
  console.log('Connected:', socket.id);

  socket.emit('register_user', {
    userId: 'test_123',
    userName: 'Test User',
    userType: 'farmer',
    governorate: 'Cairo'
  });
});

socket.on('registration_confirmed', (data) => {
  console.log('Registered:', data);
});
```

### Using Browser Console

```javascript
const socket = io('http://localhost:8097', {
  auth: { token: 'your-jwt-token' }
});

socket.on('connect', () => {
  console.log('Connected!');
  socket.emit('register_user', {
    userId: 'browser_test',
    userName: 'Browser Tester',
    userType: 'farmer',
    governorate: 'Cairo'
  });
});

socket.on('registration_confirmed', (data) => {
  console.log('Success:', data);
});
```

## 📡 REST API Quick Tests / اختبارات سريعة لـ REST API

### Get Online Experts / الحصول على الخبراء المتصلين

```bash
curl http://localhost:8097/v1/experts/online
```

### Get Support Requests / الحصول على طلبات الدعم

```bash
curl http://localhost:8097/v1/requests?status=pending
```

### Get Statistics / الحصول على الإحصائيات

```bash
curl http://localhost:8097/v1/stats
```

### Get Room Messages / الحصول على رسائل الغرفة

```bash
curl http://localhost:8097/v1/rooms/support_12345_1735295400000/messages
```

## 🧪 Run Example Clients / تشغيل عملاء الأمثلة

### Farmer Client

```bash
cd examples
npm install
export JWT_TOKEN="your-jwt-token"
npm run farmer
```

### Expert Client

```bash
cd examples
npm install
export JWT_TOKEN="your-jwt-token"
npm run expert
```

## 🔐 Generate Test JWT Token / توليد توكن JWT للاختبار

### Using Node.js

```javascript
const jwt = require('jsonwebtoken');

const token = jwt.sign(
  {
    sub: 'test_user_123',
    role: 'farmer',
    name: 'Test User'
  },
  'your-secret-key-minimum-32-characters-long',
  { expiresIn: '24h' }
);

console.log('JWT Token:', token);
```

### Using jwt.io

1. Go to https://jwt.io
2. In the "PAYLOAD" section, enter:
```json
{
  "sub": "test_user_123",
  "role": "farmer",
  "name": "Test User",
  "iat": 1735295400,
  "exp": 1735381800
}
```
3. In "VERIFY SIGNATURE", enter your secret key
4. Copy the encoded JWT from the left panel

## 📚 Next Steps / الخطوات التالية

1. **Read Full Documentation** / اقرأ التوثيق الكامل
   - [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)
   - [Swagger UI](http://localhost:8097/api-docs)

2. **Try Examples** / جرب الأمثلة
   - [examples/README.md](./examples/README.md)
   - [examples/client-example.js](./examples/client-example.js)

3. **Integrate with Your App** / تكامل مع تطبيقك
   - Use the `ChatClient` class from examples
   - Implement event handlers for your UI
   - Handle connection states and errors

4. **Production Setup** / إعداد الإنتاج
   - Configure Redis for state management
   - Set up proper CORS origins
   - Enable rate limiting
   - Configure HTTPS
   - Set up monitoring

## 🐛 Troubleshooting / حل المشاكل

### Service won't start / الخدمة لا تبدأ

**Error**: `JWT_SECRET_KEY environment variable is required`

**Solution**: Set the JWT secret key
```bash
export JWT_SECRET_KEY="your-secret-key-minimum-32-characters-long"
```

### Cannot connect via WebSocket / لا يمكن الاتصال عبر WebSocket

**Error**: `Authentication required`

**Solution**:
1. Generate a valid JWT token
2. Pass it in the connection:
```javascript
const socket = io('http://localhost:8097', {
  auth: { token: 'your-valid-token' }
});
```

### Port already in use / المنفذ قيد الاستخدام

**Error**: `EADDRINUSE: address already in use :::8097`

**Solution**:
1. Stop the other process using port 8097
2. Or use a different port:
```bash
export PORT=8098
npm start
```

### CORS Error / خطأ CORS

**Error**: `has been blocked by CORS policy`

**Solution**: Add your origin to CORS_ORIGINS
```bash
export CORS_ORIGINS="http://localhost:3000,http://localhost:3001,http://your-domain.com"
```

## 📞 Getting Help / الحصول على المساعدة

- **Documentation**: http://localhost:8097/api-docs
- **Health Check**: http://localhost:8097/healthz
- **Support**: support@sahool.io

## ✅ Checklist / قائمة التحقق

- [ ] Dependencies installed (`npm install`)
- [ ] JWT_SECRET_KEY configured
- [ ] Service started successfully
- [ ] Health check returns "healthy"
- [ ] Swagger UI accessible
- [ ] Can connect via WebSocket
- [ ] Can send/receive messages
- [ ] Tested example clients

## 🎉 You're Ready! / أنت جاهز!

Your Community Chat Service is now running and ready to use!

خدمة الدردشة جاهزة الآن للاستخدام!

---

**Need more help? Check the full documentation!**
**تحتاج مزيد من المساعدة؟ راجع التوثيق الكامل!**
