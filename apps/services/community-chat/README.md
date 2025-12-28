# ⚠️ DEPRECATED - Use chat-service instead

This service has been deprecated. All chat functionality is now handled by `chat-service` (Port 8114).

## Migration Guide

The `chat-service` provides:
- Persistent message storage (PostgreSQL)
- Real-time messaging (Socket.IO)
- Read receipts and typing indicators
- Multiple message types (TEXT, IMAGE, OFFER, SYSTEM)

Please update your references to use `chat-service` instead.

---

# 🌿 Sahool Community Chat Service
# خدمة الدردشة الحية لمجتمع سهول

[![Service Status](https://img.shields.io/badge/status-active-success)](http://localhost:8097/healthz)
[![API Docs](https://img.shields.io/badge/API-documented-blue)](http://localhost:8097/api-docs)
[![Version](https://img.shields.io/badge/version-1.0.0-green)](./CHANGELOG.md)
[![Node](https://img.shields.io/badge/node-%3E%3D20.0.0-brightgreen)](https://nodejs.org)

Real-time chat service connecting farmers with agricultural experts on the Sahool platform.

خدمة دردشة فورية تربط المزارعين بالخبراء الزراعيين في منصة سهول.

**Port:** 8097
**Version:** 1.0.0

---

## 📋 Table of Contents / جدول المحتويات

- [Features](#-features--الميزات)
- [Quick Start](#-quick-start--البدء-السريع)
- [API Documentation](#-api-documentation--توثيق-الـ-api)
- [Usage Examples](#-usage-examples--أمثلة-الاستخدام)
- [Security](#-security--الأمان)
- [Support](#-support--الدعم)

---

## ✨ Features / الميزات

### Core Features / الميزات الأساسية
- 🔌 **Real-time Communication** - Socket.io for instant messaging
- 👥 **Farmer-Expert Matching** - Connect farmers with agricultural experts
- 💬 **Group Chat Rooms** - Multi-participant support sessions
- 📝 **Message History** - Persistent chat history
- ✍️ **Typing Indicators** - Real-time typing status
- 👤 **Presence Tracking** - Online/offline status
- 📎 **File Attachments** - Support for images and documents
- 🔐 **JWT Authentication** - Secure token-based auth
- 🌐 **Bilingual Support** - Arabic and English

### Technical Features / الميزات التقنية
- ⚡ **High Performance** - Optimized for concurrent connections
- 🔒 **Security First** - Input validation, XSS prevention, access control
- 📊 **Real-time Stats** - Service metrics and monitoring
- 🎯 **RESTful API** - Clean REST endpoints for management
- 📚 **OpenAPI 3.0** - Complete API documentation
- 🧪 **Testable** - Example clients and Postman collection

---

## 🚀 Quick Start / البدء السريع

```bash
# Install dependencies
npm install

# Set environment variables
export JWT_SECRET_KEY="your-secret-key-minimum-32-characters-long"
export PORT=8097

# Start service
npm start

# Open API documentation
open http://localhost:8097/api-docs
```

👉 **For detailed setup, see [QUICK_START.md](./QUICK_START.md)**

---

## 📚 API Documentation / توثيق الـ API

### Interactive Documentation / التوثيق التفاعلي

| Documentation | URL | Description |
|---------------|-----|-------------|
| **Swagger UI** | http://localhost:8097/api-docs | Interactive API testing |
| **ReDoc** | http://localhost:8097/redoc | Clean, readable docs |
| **OpenAPI JSON** | http://localhost:8097/api-docs.json | Machine-readable spec |

### REST API Endpoints

```http
GET  /healthz                          # Health check
GET  /v1/requests                      # Get support requests
GET  /v1/rooms/:roomId/messages        # Get room messages
GET  /v1/experts/online                # Get online experts
GET  /v1/stats                         # Get statistics
```

### WebSocket Events

**Client → Server:**
- `register_user` - Register user
- `join_room` - Join chat room
- `send_message` - Send message
- `request_expert` - Request help
- `accept_request` - Accept request

**Server → Client:**
- `receive_message` - New message
- `user_joined` - User joined
- `expert_online` - Expert online
- `load_history` - Message history

👉 **Complete API docs: [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)**

---

## 💡 Usage Examples / أمثلة الاستخدام

### Node.js Client

```javascript
const io = require('socket.io-client');

const socket = io('http://localhost:8097', {
  auth: { token: 'your-jwt-token' }
});

socket.on('connect', () => {
  socket.emit('register_user', {
    userId: '12345',
    userName: 'محمد أحمد',
    userType: 'farmer',
    governorate: 'القاهرة'
  });
});

socket.on('receive_message', (message) => {
  console.log('New message:', message);
});
```

👉 **More examples: [examples/](./examples/)**

---

## 🔒 Security / الأمان

### Authentication / المصادقة
- ✅ JWT token required
- ✅ Token validation
- ✅ Role verification

### Input Validation / التحقق
- ✅ XSS prevention
- ✅ Length limits
- ✅ URL whitelisting

### Network Security / أمان الشبكة
- ✅ CORS protection
- ✅ Rate limiting (recommended)
- ✅ HTTPS (production)

---

## 📞 Support / الدعم

### Documentation / التوثيق
- 📖 [API Documentation](./API_DOCUMENTATION.md) - Complete reference
- 🚀 [Quick Start](./QUICK_START.md) - 5-minute setup
- 💡 [Examples](./examples/README.md) - Integration examples
- 📝 [Changelog](./CHANGELOG.md) - Version history

### Links / الروابط
- 🔧 Swagger UI: http://localhost:8097/api-docs
- 💚 Health Check: http://localhost:8097/healthz
- 📧 Email: support@sahool.io
- 🌐 Website: https://sahool.io

---

## 📄 License / الترخيص

Proprietary - Sahool Platform © 2025

---

<div align="center">

**Built with ❤️ for Sahool Agricultural Platform**

**مبني بكل ❤️ لمنصة سهول الزراعية**

[Documentation](./API_DOCUMENTATION.md) • [Quick Start](./QUICK_START.md) • [Examples](./examples/) • [Changelog](./CHANGELOG.md)

</div>
