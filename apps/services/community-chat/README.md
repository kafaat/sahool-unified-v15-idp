# Community Chat - مجتمع المزارعين

## نظرة عامة | Overview

خدمة التواصل والمحادثة بين المزارعين لتبادل الخبرات والمعرفة الزراعية.

Farmers community chat service for sharing agricultural knowledge and experiences.

**Port:** 8106
**Version:** 15.4.0

---

## الميزات | Features

### المحادثات | Conversations
| الميزة | Feature | الوصف |
|--------|---------|--------|
| محادثات خاصة | Private Chat | بين مزارعين |
| مجموعات | Groups | مجموعات نقاش |
| قنوات | Channels | قنوات عامة للمتابعة |
| استشارات | Consultations | استشارات من الخبراء |

### المحتوى | Content
| الميزة | Feature | الوصف |
|--------|---------|--------|
| نص | Text | رسائل نصية |
| صور | Images | مشاركة صور المحاصيل |
| موقع | Location | مشاركة مواقع الحقول |
| ملفات | Files | مشاركة وثائق |

---

## API Endpoints

### المحادثات | Conversations

```http
# جلب المحادثات
GET /conversations?type=group&limit=20

# إنشاء محادثة
POST /conversations
{
    "type": "group",
    "name": "مزارعي البن - حضرموت",
    "members": ["user-001", "user-002"],
    "crop_type": "coffee"
}

# جلب محادثة
GET /conversations/{conversation_id}

# تحديث محادثة
PATCH /conversations/{conversation_id}
{
    "name": "اسم جديد"
}
```

### الرسائل | Messages

```http
# جلب الرسائل
GET /conversations/{conversation_id}/messages?limit=50&before={message_id}

# إرسال رسالة
POST /conversations/{conversation_id}/messages
{
    "content": "السلام عليكم، كيف أتعامل مع صدأ البن؟",
    "type": "text",
    "attachments": []
}

# رفع مرفق
POST /messages/upload
Content-Type: multipart/form-data
{
    "file": <image>
}

# حذف رسالة
DELETE /messages/{message_id}
```

### المجموعات | Groups

```http
# إنشاء مجموعة
POST /groups
{
    "name": "مزارعي القمح",
    "description": "مجموعة لمزارعي القمح في اليمن",
    "region": "المرتفعات الشمالية",
    "crop_types": ["wheat", "barley"],
    "is_public": true
}

# انضمام لمجموعة
POST /groups/{group_id}/join

# مغادرة مجموعة
POST /groups/{group_id}/leave

# أعضاء المجموعة
GET /groups/{group_id}/members
```

### القنوات | Channels

```http
# القنوات العامة
GET /channels?category=agricultural_tips

# الاشتراك في قناة
POST /channels/{channel_id}/subscribe

# إلغاء الاشتراك
DELETE /channels/{channel_id}/subscribe
```

### البحث | Search

```http
# البحث في الرسائل
GET /search/messages?q=صدأ+البن&crop_type=coffee

# البحث عن مزارعين
GET /search/farmers?region=hadhramaut&crop=coffee
```

---

## نماذج البيانات | Data Models

### Conversation
```json
{
    "id": "conv-001",
    "type": "group",
    "name": "مزارعي البن - حضرموت",
    "members_count": 156,
    "crop_types": ["coffee"],
    "last_message": {
        "content": "شكراً على النصيحة",
        "sender_name": "أحمد محمد",
        "sent_at": "2024-01-15T14:30:00Z"
    },
    "unread_count": 3,
    "created_at": "2024-01-01T00:00:00Z"
}
```

### Message
```json
{
    "id": "msg-001",
    "conversation_id": "conv-001",
    "sender": {
        "id": "user-001",
        "name": "أحمد محمد",
        "avatar_url": "https://..."
    },
    "content": "هذه صورة لأوراق البن المصابة",
    "type": "image",
    "attachments": [
        {
            "type": "image",
            "url": "https://...",
            "thumbnail_url": "https://..."
        }
    ],
    "reactions": {
        "helpful": 5,
        "thanks": 3
    },
    "sent_at": "2024-01-15T10:30:00Z"
}
```

---

## WebSocket Events

```javascript
// الاتصال (استخدم wss:// في الإنتاج)
wss://community-chat:8106/ws?token={jwt}

// استقبال رسالة
{
    "event": "message",
    "data": {
        "conversation_id": "conv-001",
        "message": {...}
    }
}

// إرسال رسالة
{
    "event": "send_message",
    "data": {
        "conversation_id": "conv-001",
        "content": "مرحبا"
    }
}

// حالة الكتابة
{
    "event": "typing",
    "data": {
        "conversation_id": "conv-001",
        "user_id": "user-001",
        "is_typing": true
    }
}
```

---

## متغيرات البيئة | Environment Variables

```env
# الخادم
PORT=8106
HOST=0.0.0.0

# قاعدة البيانات
DATABASE_URL=postgresql://...
REDIS_URL=redis://redis:6379

# التخزين
S3_BUCKET=sahool-chat-media
MAX_FILE_SIZE_MB=10

# الحدود
MAX_MESSAGE_LENGTH=2000
MAX_GROUP_MEMBERS=500
```

---

## Health Check

```http
GET /healthz

Response:
{
    "status": "healthy",
    "service": "community-chat",
    "version": "15.4.0",
    "websocket_connections": 1250
}
```

---

## الترخيص | License

Proprietary - KAFAAT © 2024
