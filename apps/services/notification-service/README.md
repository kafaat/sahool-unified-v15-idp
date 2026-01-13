# Notification Service - خدمة الإشعارات

## نظرة عامة | Overview

خدمة إدارة وإرسال الإشعارات لمنصة سهول عبر قنوات متعددة.

Multi-channel notification management service for SAHOOL platform.

**Port:** 8109
**Version:** 15.4.0

---

## الميزات | Features

### قنوات الإرسال | Delivery Channels

| القناة   | Channel       | الوصف                |
| -------- | ------------- | -------------------- |
| Push     | Firebase FCM  | إشعارات الهاتف       |
| In-App   | WebSocket     | إشعارات داخل التطبيق |
| Email    | SMTP/SendGrid | البريد الإلكتروني    |
| SMS      | Twilio        | الرسائل النصية       |
| WhatsApp | Twilio        | واتساب للأعمال       |

### فئات الإشعارات | Notification Categories

| الفئة       | Category    | الوصف                   |
| ----------- | ----------- | ----------------------- |
| weather     | الطقس       | تحديثات وتنبيهات الطقس  |
| task        | المهام      | تذكيرات المهام الزراعية |
| alert       | التنبيهات   | تنبيهات المستشعرات      |
| irrigation  | الري        | جداول ونتائج الري       |
| crop_health | صحة المحصول | تحديثات صحة المحاصيل    |
| marketplace | السوق       | عروض وطلبات السوق       |
| payment     | المدفوعات   | معاملات مالية           |
| system      | النظام      | إشعارات النظام          |

---

## API Endpoints

### الإشعارات | Notifications

```http
# جلب الإشعارات
GET /notifications?page=1&limit=20&unread_only=true

# عدد غير المقروءة
GET /notifications/unread/count

# تحديد كمقروء
POST /notifications/{notification_id}/read

# تحديد الكل كمقروء
POST /notifications/read-all

# حذف إشعار
DELETE /notifications/{notification_id}

# مسح الكل
DELETE /notifications/clear-all
```

### إشعارات الدفع | Push Notifications

```http
# تسجيل رمز FCM
POST /push/register
{
    "token": "fcm_token_here",
    "platform": "android",
    "device_id": "device-001"
}

# إلغاء التسجيل
POST /push/unregister
{
    "token": "fcm_token_here"
}
```

### التفضيلات | Preferences

```http
# جلب التفضيلات
GET /preferences

# تحديث التفضيلات
PUT /preferences
{
    "push_enabled": true,
    "email_enabled": true,
    "sms_enabled": false,
    "categories": {
        "weather": true,
        "task": true,
        "marketplace": false
    },
    "quiet_hours": {
        "enabled": true,
        "start_time": "22:00",
        "end_time": "07:00"
    },
    "language": "ar"
}

# تبديل فئة
POST /preferences/category
{
    "category": "weather",
    "enabled": false
}
```

### الاشتراكات | Subscriptions

```http
# الاشتراك في إشعارات حقل
POST /subscriptions/fields/{field_id}

# إلغاء الاشتراك
DELETE /subscriptions/fields/{field_id}

# الحقول المشترك فيها
GET /subscriptions/fields
```

### إرسال إشعار (داخلي) | Send Notification (Internal)

```http
# إرسال إشعار
POST /internal/send
{
    "tenant_id": "tenant-001",
    "user_ids": ["user-001", "user-002"],
    "title": "تنبيه الري",
    "body": "حان وقت ري الحقل رقم 1",
    "category": "irrigation",
    "priority": "high",
    "channels": ["push", "in_app"],
    "data": {
        "field_id": "field-001",
        "action": "start_irrigation"
    }
}

# إرسال جماعي
POST /internal/broadcast
{
    "tenant_id": "tenant-001",
    "title": "تحديث النظام",
    "body": "سيتم إجراء صيانة مجدولة",
    "category": "system"
}
```

---

## نماذج البيانات | Data Models

### AppNotification

```json
{
  "id": "notif-001",
  "title": "تنبيه الري",
  "body": "رطوبة التربة منخفضة في الحقل 1",
  "category": "irrigation",
  "priority": "high",
  "is_read": false,
  "created_at": "2024-01-15T10:30:00Z",
  "action_type": "navigate",
  "data": {
    "field_id": "field-001",
    "screen": "irrigation_control"
  },
  "image_url": "https://..."
}
```

### NotificationList

```json
{
    "notifications": [...],
    "total": 150,
    "unread_count": 12,
    "page": 1,
    "total_pages": 8
}
```

### NotificationPreferences

```json
{
  "push_enabled": true,
  "email_enabled": true,
  "sms_enabled": false,
  "categories": {
    "weather": true,
    "task": true,
    "alert": true,
    "irrigation": true,
    "crop_health": true,
    "marketplace": false,
    "payment": true,
    "system": true
  },
  "quiet_hours": {
    "enabled": true,
    "start_time": "22:00",
    "end_time": "07:00"
  },
  "language": "ar"
}
```

---

## قوالب الإشعارات | Notification Templates

### باللغة العربية

```
الطقس: ⛈️ تحذير من أمطار غزيرة خلال الساعات القادمة
الري: 💧 تم إكمال ري {field_name} بنجاح
المهمة: 📋 تذكير: {task_title} - موعد التسليم غداً
التنبيه: ⚠️ رطوبة التربة منخفضة: {value}%
صحة المحصول: 🌱 تم اكتشاف {issue} في {field_name}
```

---

## متغيرات البيئة | Environment Variables

```env
# الخادم
PORT=8109
HOST=0.0.0.0

# Firebase
FIREBASE_PROJECT_ID=sahool-app
FIREBASE_CREDENTIALS_PATH=/etc/secrets/firebase.json

# البريد الإلكتروني
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=your_sendgrid_key
EMAIL_FROM=notifications@sahool.app

# SMS
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+967...

# قاعدة البيانات
DATABASE_URL=postgresql://...

# Redis
REDIS_URL=redis://localhost:6379

# الحدود
MAX_NOTIFICATIONS_PER_USER=1000
NOTIFICATION_RETENTION_DAYS=90
RATE_LIMIT_PER_MINUTE=100
```

---

## الأولويات | Priority Levels

| الأولوية | Priority | السلوك             |
| -------- | -------- | ------------------ |
| urgent   | عاجل     | تجاوز ساعات الهدوء |
| high     | مرتفع    | إرسال فوري         |
| normal   | عادي     | إرسال عادي         |
| low      | منخفض    | تجميع وإرسال دفعات |

---

## WebSocket للإشعارات الفورية | Real-time Notifications

```javascript
const ws = new WebSocket("ws://localhost:8109/ws/user/{user_id}?token=JWT");

ws.onmessage = (event) => {
  const notification = JSON.parse(event.data);
  showNotification(notification);
};
```

---

## Health Check

```http
GET /healthz

Response:
{
    "status": "healthy",
    "service": "notification-service",
    "version": "15.4.0",
    "dependencies": {
        "database": "connected",
        "redis": "connected",
        "firebase": "connected"
    }
}
```

---

## التغييرات | Changelog

### v15.4.0

- إضافة دعم WhatsApp
- تحسين ساعات الهدوء
- إضافة قوالب الإشعارات
- دعم الإشعارات المجدولة

### v15.3.0

- إضافة WebSocket للتحديثات الفورية
- تحسين تفضيلات المستخدم
- دعم الإشعارات الجماعية

---

## الترخيص | License

Proprietary - KAFAAT © 2024
