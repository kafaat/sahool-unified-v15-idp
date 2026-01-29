# Notification Service

## Service Overview

| Property | Value |
|----------|-------|
| **Service Name** | notification-service |
| **Type** | Python / FastAPI |
| **Port** | 8110 |
| **Version** | 16.0.0 (API version 15.4.0) |
| **Description** | Personalized agricultural notifications for Yemeni farmers with multi-channel delivery (Push, SMS, Email, WhatsApp, Telegram, In-App) |

### Key Features

- **Multi-Channel Notifications**: Push (Firebase), SMS (Twilio/Unifonic/MSEGAT), Email (SendGrid/SMTP), WhatsApp (Meta/Twilio), Telegram
- **Personalized Alerts**: Based on farmer's crops, location (governorate), and preferences
- **Weather Warnings**: Frost, heat waves, storms, floods, drought alerts
- **Pest Outbreak Alerts**: Location and crop-specific pest notifications
- **Irrigation Reminders**: Smart irrigation scheduling notifications
- **Market Price Notifications**: Price updates for agricultural products
- **OTP Service**: Multi-channel one-time password delivery with rate limiting
- **NATS Integration**: Field-First Architecture for real-time event processing
- **Bilingual Support**: Arabic (primary) and English

---

## Architecture

### Field-First Architecture
```
Analysis Services --> NATS --> notification-service --> Mobile App
                                      |
                                      +--> SMS (Twilio/Unifonic/MSEGAT)
                                      +--> Email (SendGrid/SMTP)
                                      +--> Push (Firebase)
                                      +--> WhatsApp (Meta/Twilio)
                                      +--> Telegram
```

### Database Schema

The service uses PostgreSQL with the following main tables:

| Table | Description |
|-------|-------------|
| `notifications` | Core notification records |
| `notification_templates` | Reusable notification templates |
| `notification_preferences` | User notification preferences |
| `notification_logs` | Delivery audit trail |
| `farmer_profiles` | Farmer profile information |
| `farmer_crops` | Junction table for farmer crops |
| `farmer_fields` | Junction table for farmer fields |

---

## API Endpoints

### Health Endpoints

#### GET /healthz
Liveness probe for Kubernetes.

**Response:**
```json
{
  "status": "ok",
  "service": "notification-service",
  "version": "16.0.0"
}
```

#### GET /readyz
Readiness probe with dependency checks.

**Response:**
```json
{
  "status": "ready",
  "service": "notification-service",
  "version": "16.0.0",
  "mode": "normal",
  "checks": {
    "nats": "connected",
    "database": "connected"
  },
  "stats": {
    "total_notifications": 150,
    "pending_notifications": 5,
    "total_templates": 10,
    "total_preferences": 25
  },
  "registered_farmers": 100
}
```

---

### Notification Management

#### POST /
Create a custom notification.

**Kong Route:** `/api/v1/notifications` (strip_path: true)

**Request Body:**
```json
{
  "type": "weather_alert",
  "priority": "high",
  "title": "Frost Warning",
  "title_ar": "تحذير من الصقيع",
  "body": "Frost expected tonight in your area",
  "body_ar": "يُتوقع صقيع الليلة في منطقتك",
  "data": {
    "temperature": -2,
    "duration_hours": 6
  },
  "target_farmers": ["farmer-001", "farmer-002"],
  "target_governorates": ["sanaa", "dhamar"],
  "target_crops": ["tomato", "wheat"],
  "channels": ["push", "sms", "in_app"],
  "expires_in_hours": 24
}
```

**Response:**
```json
{
  "id": "uuid-string",
  "type": "weather_alert",
  "type_ar": "تنبيه طقس",
  "priority": "high",
  "priority_ar": "عالية",
  "title": "Frost Warning",
  "title_ar": "تحذير من الصقيع",
  "body": "Frost expected tonight in your area",
  "body_ar": "يُتوقع صقيع الليلة في منطقتك",
  "data": {},
  "created_at": "2025-01-25T10:30:00Z",
  "expires_at": "2025-01-26T10:30:00Z",
  "status": "pending"
}
```

#### GET /farmer/{farmer_id}
Get notifications for a specific farmer.

**Kong Route:** `/api/v1/notifications/farmer/{farmer_id}`

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `unread_only` | boolean | false | Filter to unread notifications only |
| `type` | string | null | Filter by notification type |
| `limit` | integer | 50 | Max results (1-100) |
| `offset` | integer | 0 | Pagination offset |

**Response:**
```json
{
  "farmer_id": "farmer-001",
  "total": 25,
  "unread_count": 5,
  "notifications": [
    {
      "id": "uuid-string",
      "type": "weather_alert",
      "type_ar": "تنبيه طقس",
      "priority": "high",
      "priority_ar": "عالية",
      "title": "Frost Warning",
      "title_ar": "تحذير من الصقيع",
      "body": "...",
      "body_ar": "...",
      "data": {},
      "is_read": false,
      "created_at": "2025-01-25T10:30:00Z",
      "expires_at": "2025-01-26T10:30:00Z",
      "action_url": "/fields/field-001"
    }
  ]
}
```

#### PATCH /{notification_id}/read
Mark a notification as read.

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `farmer_id` | string | Yes | Farmer ID for authorization |

**Response:**
```json
{
  "success": true,
  "notification_id": "uuid-string",
  "is_read": true,
  "read_at": "2025-01-25T10:35:00Z"
}
```

#### GET /broadcast
Get broadcast notifications (public alerts).

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `governorate` | string | Filter by governorate |
| `crop` | string | Filter by crop type |
| `limit` | integer | Max results (1-50, default 20) |

**Response:**
```json
{
  "total": 10,
  "notifications": [
    {
      "id": "uuid-string",
      "type": "pest_outbreak",
      "type_ar": "انتشار آفات",
      "priority": "high",
      "priority_ar": "عالية",
      "title": "Pest Outbreak Alert",
      "title_ar": "تنبيه انتشار آفة",
      "body": "...",
      "body_ar": "...",
      "data": {},
      "created_at": "2025-01-25T10:30:00Z",
      "expires_at": "2025-01-27T10:30:00Z",
      "target_governorates": ["sanaa"],
      "target_crops": ["tomato"]
    }
  ]
}
```

---

### Alert Endpoints

#### POST /weather
Create a weather alert for specific governorates.

**Kong Route:** `/api/v1/alerts/weather`

**Request Body:**
```json
{
  "governorates": ["sanaa", "dhamar"],
  "alert_type": "frost",
  "severity": "high",
  "expected_date": "2025-01-26",
  "details": {
    "min_temperature": -3,
    "duration_hours": 8
  }
}
```

**Alert Types:**
- `frost` - Frost warning
- `heat_wave` - Extreme heat alert
- `storm` - Storm warning
- `flood` - Flood risk
- `drought` - Extended dry period

**Response:**
```json
{
  "id": "uuid-string",
  "type": "weather_alert",
  "title": "Frost Warning in sanaa",
  "title_ar": "تحذير من الصقيع في صنعاء",
  "body": "Expected frost tonight...",
  "body_ar": "يُتوقع صقيع الليلة...",
  "created_at": "2025-01-25T10:30:00Z"
}
```

#### POST /pest
Create a pest outbreak alert.

**Kong Route:** `/api/v1/alerts/pest`

**Request Body:**
```json
{
  "governorate": "sanaa",
  "pest_name": "Tomato Leaf Miner",
  "pest_name_ar": "حفار أوراق الطماطم",
  "affected_crops": ["tomato"],
  "severity": "high",
  "recommendations": [
    "Apply neem oil spray",
    "Remove affected leaves"
  ],
  "recommendations_ar": [
    "رش زيت النيم",
    "إزالة الأوراق المصابة"
  ]
}
```

**Response:**
```json
{
  "id": "uuid-string",
  "type": "pest_outbreak",
  "title": "Pest Outbreak: Tomato Leaf Miner",
  "title_ar": "انتشار آفة: حفار أوراق الطماطم",
  "body": "...",
  "body_ar": "...",
  "created_at": "2025-01-25T10:30:00Z"
}
```

---

### Reminder Endpoints

#### POST /irrigation
Create an irrigation reminder for a farmer.

**Kong Route:** `/api/v1/reminders/irrigation`

**Request Body:**
```json
{
  "farmer_id": "farmer-001",
  "field_id": "field-001",
  "field_name": "North Field",
  "crop": "tomato",
  "water_needed_mm": 25.5,
  "urgency": "high"
}
```

**Response:**
```json
{
  "id": "uuid-string",
  "type": "irrigation_reminder",
  "title": "Irrigation Reminder: North Field",
  "title_ar": "تذكير ري: North Field",
  "body": "Your tomato field needs 25.5mm of water",
  "body_ar": "حقل طماطم يحتاج 25.5 ملم من المياه...",
  "created_at": "2025-01-25T10:30:00Z"
}
```

---

### Farmer Management

#### POST /register
Register a farmer for notifications.

**Kong Route:** `/api/v1/farmers/register`

**Request Body:**
```json
{
  "farmer_id": "farmer-001",
  "name": "Ahmed Ali",
  "name_ar": "أحمد علي",
  "governorate": "sanaa",
  "district": "Bani Hushaish",
  "crops": ["tomato", "wheat"],
  "field_ids": ["field-001", "field-002"],
  "phone": "+967771234567",
  "email": "ahmed@example.com",
  "fcm_token": "firebase-token-string",
  "notification_channels": ["push", "sms", "in_app"],
  "language": "ar"
}
```

**Response:**
```json
{
  "success": true,
  "farmer_id": "farmer-001",
  "message": "تم تسجيل المزارع بنجاح",
  "message_en": "Farmer registered successfully"
}
```

#### PUT /{farmer_id}/preferences
Update notification preferences for a farmer.

**Kong Route:** `/api/v1/farmers/{farmer_id}/preferences`

**Request Body:**
```json
{
  "farmer_id": "farmer-001",
  "weather_alerts": true,
  "pest_alerts": true,
  "irrigation_reminders": true,
  "crop_health_alerts": true,
  "market_prices": false,
  "quiet_hours_start": "22:00",
  "quiet_hours_end": "06:00",
  "min_priority": "medium"
}
```

**Response:**
```json
{
  "success": true,
  "farmer_id": "farmer-001",
  "preferences": {},
  "message": "تم تحديث التفضيلات",
  "message_en": "Preferences updated successfully"
}
```

---

### Statistics

#### GET /stats
Get notification statistics.

**Kong Route:** `/api/v1/notification-stats`

**Response:**
```json
{
  "total_notifications": 5000,
  "pending_notifications": 150,
  "registered_farmers": 250,
  "total_templates": 15,
  "total_preferences": 500,
  "by_type": {
    "weather_alert": 1200,
    "pest_outbreak": 300,
    "irrigation_reminder": 2500,
    "crop_health": 500,
    "market_price": 400,
    "system": 100
  },
  "active_weather_alerts": 5,
  "active_pest_alerts": 2
}
```

---

### Channels Controller (channels_controller.py)

**Router Prefix:** `/channels`

#### POST /channels/add
Add a notification channel (FCM token, phone, email).

**Request Body:**
```json
{
  "user_id": "user-001",
  "channel_type": "push",
  "identifier": "fcm-token-string",
  "device_info": {
    "platform": "android",
    "model": "Samsung Galaxy S21"
  }
}
```

#### GET /channels/list
List user's notification channels.

**Query Parameters:**
| Parameter | Type | Required |
|-----------|------|----------|
| `user_id` | string | Yes |

#### DELETE /channels/remove
Remove a notification channel.

**Query Parameters:**
| Parameter | Type | Required |
|-----------|------|----------|
| `user_id` | string | Yes |
| `channel_type` | string | Yes |

#### POST /channels/verify
Verify a channel (send OTP).

**Request Body:**
```json
{
  "user_id": "user-001",
  "channel_type": "sms",
  "identifier": "+967771234567"
}
```

#### POST /channels/confirm
Confirm channel verification with OTP.

**Request Body:**
```json
{
  "user_id": "user-001",
  "channel_type": "sms",
  "otp": "123456"
}
```

---

### Preferences Controller (preferences_controller.py)

**Router Prefix:** `/preferences`

#### GET /preferences/
Get user notification preferences.

**Query Parameters:**
| Parameter | Type | Required |
|-----------|------|----------|
| `user_id` | string | Yes |
| `tenant_id` | string | No |

#### PUT /preferences/update
Update notification preferences.

**Request Body:**
```json
{
  "user_id": "user-001",
  "event_types": {
    "weather_alert": {
      "enabled": true,
      "channels": ["push", "sms"]
    },
    "pest_outbreak": {
      "enabled": true,
      "channels": ["push"]
    },
    "irrigation_reminder": {
      "enabled": true,
      "channels": ["push", "in_app"]
    }
  },
  "quiet_hours": {
    "enabled": true,
    "start": "22:00",
    "end": "06:00"
  },
  "language": "ar"
}
```

#### POST /preferences/reset
Reset preferences to defaults.

---

### OTP Controller (otp_controller.py)

**Router Prefix:** `/otp`

#### POST /otp/generate
Generate and send OTP.

**Request Body:**
```json
{
  "user_id": "user-001",
  "phone_or_email": "+967771234567",
  "channel": "sms",
  "purpose": "login",
  "language": "ar"
}
```

**Channels:** `sms`, `whatsapp`, `telegram`, `email`

**Purposes:** `login`, `registration`, `password_reset`, `phone_verification`, `email_verification`, `transaction`, `two_factor`

**Response:**
```json
{
  "success": true,
  "message": "OTP sent successfully",
  "message_ar": "تم إرسال رمز التحقق بنجاح",
  "otp_sent": true,
  "time_remaining": 600,
  "attempts_remaining": 3,
  "delivery_id": "message-sid"
}
```

#### POST /otp/verify
Verify OTP code.

**Request Body:**
```json
{
  "user_id": "user-001",
  "otp_code": "123456",
  "purpose": "login"
}
```

**Response:**
```json
{
  "success": true,
  "message": "OTP verified successfully",
  "message_ar": "تم التحقق من رمز OTP بنجاح"
}
```

#### GET /otp/status
Get OTP status.

**Query Parameters:**
| Parameter | Type | Required |
|-----------|------|----------|
| `user_id` | string | Yes |
| `purpose` | string | Yes |

#### POST /otp/invalidate
Invalidate existing OTP.

---

## NATS Events

### Subscribed Events

| Subject Pattern | Description |
|-----------------|-------------|
| `sahool.*.notifications.send` | Send notification request |
| `sahool.*.analysis.complete` | Analysis completion events (triggers notifications) |
| `sahool.*.weather.alert` | Weather alert events |
| `sahool.*.pest.detected` | Pest detection events |
| `sahool.*.irrigation.reminder` | Irrigation reminder events |
| `sahool.*.crop.health` | Crop health events |

### NATS Message Format

```json
{
  "type": "weather_alert",
  "priority": "high",
  "title": "Storm Warning",
  "title_ar": "تحذير من عاصفة",
  "body": "Heavy rain expected",
  "body_ar": "متوقع أمطار غزيرة",
  "data": {},
  "target_farmers": ["farmer-001"],
  "channels": ["push", "sms"],
  "expires_in_hours": 24
}
```

### Published Events

| Subject | Description |
|---------|-------------|
| `sahool.{tenant_id}.notification.sent` | Notification sent confirmation |
| `sahool.{tenant_id}.notification.delivered` | Delivery confirmation |
| `sahool.{tenant_id}.notification.failed` | Delivery failure |

---

## Notification Channels

### SMS Providers

#### Twilio (Primary)
```
Environment Variables:
- TWILIO_ACCOUNT_SID
- TWILIO_AUTH_TOKEN
- TWILIO_PHONE_NUMBER
```

#### Unifonic (Middle East)
```
Environment Variables:
- UNIFONIC_APP_SID
- UNIFONIC_SENDER_ID
```

#### MSEGAT (Saudi Arabia)
```
Environment Variables:
- MSEGAT_API_KEY
- MSEGAT_USER_NAME
- MSEGAT_SENDER_NAME
```

### Email Providers

#### SendGrid (Primary)
```
Environment Variables:
- SENDGRID_API_KEY
- SENDGRID_FROM_EMAIL
```

#### SMTP (Fallback)
```
Environment Variables:
- SMTP_HOST
- SMTP_PORT
- SMTP_USER
- SMTP_PASSWORD
- SMTP_FROM_EMAIL
```

### Push Notifications

#### Firebase Cloud Messaging (FCM)
```
Environment Variables:
- FIREBASE_PROJECT_ID
- FIREBASE_CREDENTIALS_PATH
- FCM_SERVER_KEY
```

### WhatsApp

#### Meta Business API (Primary)
```
Environment Variables:
- META_WHATSAPP_TOKEN
- META_WHATSAPP_PHONE_ID
```

#### Twilio WhatsApp (Fallback)
```
Environment Variables:
- TWILIO_WHATSAPP_NUMBER (format: whatsapp:+1234567890)
```

### Telegram
```
Environment Variables:
- TELEGRAM_BOT_TOKEN
```

---

## Enums and Constants

### NotificationType
| Value | Arabic |
|-------|--------|
| `weather_alert` | تنبيه طقس |
| `pest_outbreak` | انتشار آفات |
| `irrigation_reminder` | تذكير ري |
| `crop_health` | صحة المحصول |
| `market_price` | أسعار السوق |
| `system` | نظام |
| `task_reminder` | تذكير مهمة |

### NotificationPriority
| Value | Arabic |
|-------|--------|
| `low` | منخفضة |
| `medium` | متوسطة |
| `high` | عالية |
| `critical` | حرجة |

### NotificationChannel
| Value | Description |
|-------|-------------|
| `push` | Firebase Cloud Messaging |
| `sms` | SMS text message |
| `email` | Email |
| `whatsapp` | WhatsApp Business |
| `in_app` | In-app notification |

### Governorate (Yemen)
| Value | Arabic |
|-------|--------|
| `sanaa` | صنعاء |
| `aden` | عدن |
| `taiz` | تعز |
| `hodeidah` | الحديدة |
| `ibb` | إب |
| `dhamar` | ذمار |
| `hadramaut` | حضرموت |
| `marib` | مأرب |
| `hajjah` | حجة |
| `saada` | صعدة |
| `lahj` | لحج |
| `abyan` | أبين |

### CropType
| Value | Arabic |
|-------|--------|
| `tomato` | طماطم |
| `wheat` | قمح |
| `coffee` | بن |
| `qat` | قات |
| `banana` | موز |
| `date_palm` | نخيل |
| `mango` | مانجو |
| `grapes` | عنب |
| `corn` | ذرة |
| `potato` | بطاطس |

---

## Dependencies

### Python Dependencies (requirements.txt)

```
fastapi>=0.110.0,<0.128.0
uvicorn>=0.27.0
pydantic>=2.0.0,<3.0.0
httpx>=0.27.0
nats-py>=2.7.0
firebase-admin>=6.4.0
twilio>=9.0.0
sendgrid>=6.11.0
aiosmtplib>=3.0.0
tortoise-orm>=0.21.0
asyncpg>=0.29.0
python-multipart>=0.0.9
redis>=5.0.0
```

### Service Dependencies

| Service | Purpose |
|---------|---------|
| PostgreSQL (pgbouncer) | Primary database |
| Redis | Rate limiting, OTP storage, caching |
| NATS | Event-driven messaging |
| Firebase | Push notifications |
| Twilio | SMS and WhatsApp |
| SendGrid | Email delivery |

### Downstream Dependents

| Service | Dependency Type |
|---------|-----------------|
| `user-service` | Depends on notification-service |
| `alert-service` | Depends on notification-service |
| `field-intelligence` | Publishes events consumed by this service |

---

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `PORT` | Service port | `8110` |
| `DATABASE_URL` | PostgreSQL connection | `postgresql://user:pass@pgbouncer:6432/sahool` |
| `REDIS_URL` | Redis connection | `redis://:password@redis:6379/0` |
| `NATS_URL` | NATS connection | `nats://user:pass@nats:4222` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ENVIRONMENT` | Environment name | `development` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `CREATE_DB_SCHEMA` | Auto-create schema | `false` |
| `JWT_SECRET_KEY` | JWT secret for OTP hashing | - |
| `JWT_ALGORITHM` | JWT algorithm | `HS256` |

### SMS Configuration

| Variable | Description | Required |
|----------|-------------|----------|
| `TWILIO_ACCOUNT_SID` | Twilio Account SID | Optional |
| `TWILIO_AUTH_TOKEN` | Twilio Auth Token | Optional |
| `TWILIO_PHONE_NUMBER` | Twilio phone number | Optional |
| `UNIFONIC_APP_SID` | Unifonic App SID | Optional |
| `UNIFONIC_SENDER_ID` | Unifonic Sender ID | Optional |
| `MSEGAT_API_KEY` | MSEGAT API Key | Optional |
| `MSEGAT_USER_NAME` | MSEGAT Username | Optional |
| `MSEGAT_SENDER_NAME` | MSEGAT Sender | Optional |

### Email Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `SENDGRID_API_KEY` | SendGrid API Key | - |
| `SENDGRID_FROM_EMAIL` | SendGrid from email | - |
| `SMTP_HOST` | SMTP server host | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP server port | `587` |
| `SMTP_USER` | SMTP username | - |
| `SMTP_PASSWORD` | SMTP password | - |
| `SMTP_FROM_EMAIL` | SMTP from email | `noreply@sahool.com` |

### Push Notification Configuration

| Variable | Description | Required |
|----------|-------------|----------|
| `FIREBASE_PROJECT_ID` | Firebase Project ID | Optional |
| `FIREBASE_CREDENTIALS_PATH` | Path to credentials JSON | Optional |
| `FCM_SERVER_KEY` | FCM server key | Optional |

### WhatsApp Configuration

| Variable | Description | Required |
|----------|-------------|----------|
| `META_WHATSAPP_TOKEN` | Meta Business API token | Optional |
| `META_WHATSAPP_PHONE_ID` | Meta WhatsApp phone ID | Optional |
| `TWILIO_WHATSAPP_NUMBER` | Twilio WhatsApp number | Optional |

### Telegram Configuration

| Variable | Description | Required |
|----------|-------------|----------|
| `TELEGRAM_BOT_TOKEN` | Telegram Bot token | Optional |

---

## Missing Environment Variables

Based on code analysis, the following environment variables are used but not documented in docker-compose:

| Variable | Used In | Issue |
|----------|---------|-------|
| `UNIFONIC_APP_SID` | sms_providers.py | Not in docker-compose |
| `UNIFONIC_SENDER_ID` | sms_providers.py | Not in docker-compose |
| `MSEGAT_API_KEY` | sms_providers.py | Not in docker-compose |
| `MSEGAT_USER_NAME` | sms_providers.py | Not in docker-compose |
| `MSEGAT_SENDER_NAME` | sms_providers.py | Not in docker-compose |
| `SENDGRID_API_KEY` | email_client.py | Not in docker-compose |
| `SENDGRID_FROM_EMAIL` | email_client.py | Not in docker-compose |
| `FIREBASE_PROJECT_ID` | firebase_client.py | Not in docker-compose |
| `FIREBASE_CREDENTIALS_PATH` | firebase_client.py | Not in docker-compose |
| `META_WHATSAPP_TOKEN` | whatsapp_client.py | Not in docker-compose |
| `META_WHATSAPP_PHONE_ID` | whatsapp_client.py | Not in docker-compose |
| `TWILIO_ACCOUNT_SID` | sms_client.py | Not in docker-compose |
| `TWILIO_AUTH_TOKEN` | sms_client.py | Not in docker-compose |
| `TWILIO_PHONE_NUMBER` | sms_client.py | Not in docker-compose |
| `TWILIO_WHATSAPP_NUMBER` | whatsapp_client.py | Not in docker-compose |
| `TELEGRAM_BOT_TOKEN` | telegram_client.py | Not in docker-compose |
| `CREATE_DB_SCHEMA` | main.py | Not in docker-compose |
| `JWT_SECRET_KEY` | otp_service.py | Not in docker-compose for notification-service |

---

## Bugs, Issues, and Recommendations

### Critical Issues

#### 1. Missing `await` in NATS Callback
**File:** `/home/user/sahool-unified-v15-idp/apps/services/notification-service/src/main.py`
**Line:** 894

```python
# BUG: create_notification is an async function but called without await
def create_notification_from_nats(notification_data: dict[str, Any]):
    ...
    create_notification(  # Missing await!
        type=ntype,
        ...
    )
```

**Fix:** The callback should be async and use `await` or use `asyncio.create_task()`.

#### 2. Rate Limiting Redis Access Pattern
**File:** `/home/user/sahool-unified-v15-idp/apps/services/notification-service/src/otp_service.py`
**Lines:** 577-583

```python
# BUG: Accessing private attribute _master which may not exist
self._redis_client._master.zremrangebyscore(...)
self._redis_client._master.zcard(...)
```

**Fix:** Use the public Redis client interface or check for attribute existence.

### Medium Issues

#### 3. Inconsistent Version Numbers
**File:** `/home/user/sahool-unified-v15-idp/apps/services/notification-service/src/main.py`

- FastAPI app version: `15.4.0` (line 1019)
- Health endpoint version: `16.0.0` (line 1070)

**Fix:** Align version numbers across the service.

#### 4. Hardcoded Default Secret in OTP Hashing
**File:** `/home/user/sahool-unified-v15-idp/apps/services/notification-service/src/otp_service.py`
**Line:** 440

```python
salt = f"{user_id}:{os.getenv('JWT_SECRET_KEY', 'default-secret')}"  # Weak default
```

**Risk:** If `JWT_SECRET_KEY` is not set, OTPs use a predictable salt.

**Fix:** Fail startup if `JWT_SECRET_KEY` is not set in production.

#### 5. Synchronous Firebase Call in Async Context
**File:** `/home/user/sahool-unified-v15-idp/apps/services/notification-service/src/main.py`
**Line:** 646

```python
# firebase_client.send_notification is synchronous but called in async context
message_id = firebase_client.send_notification(...)  # Blocks event loop
```

**Fix:** Use `asyncio.to_thread()` or make Firebase client async.

### Minor Issues

#### 6. Deprecated .dict() Method
**File:** `/home/user/sahool-unified-v15-idp/apps/services/notification-service/src/main.py`
**Line:** 1469

```python
"preferences": preferences.dict(),  # Deprecated in Pydantic v2
```

**Fix:** Use `preferences.model_dump()` instead.

#### 7. Missing Error Handling for Invalid Enum Conversion
**File:** `/home/user/sahool-unified-v15-idp/apps/services/notification-service/src/main.py`
**Lines:** 908-911

```python
if isinstance(channel, str):
    channel = OTPChannel(channel)  # May raise ValueError if invalid
```

**Fix:** Add try-except block for invalid enum values.

#### 8. Potential Memory Leak in In-Memory OTP Storage
**File:** `/home/user/sahool-unified-v15-idp/apps/services/notification-service/src/otp_service.py`

The `InMemoryStorage` class doesn't automatically expire old entries in `_otp_store`. While Redis handles TTL automatically, in-memory fallback doesn't clean expired entries unless explicitly deleted.

**Fix:** Add periodic cleanup task for in-memory storage.

---

## Recommendations

### High Priority

1. **Add missing environment variables to docker-compose** - Many notification channel configurations are missing from docker-compose files.

2. **Fix async/await issues** - The NATS callback and Firebase calls need proper async handling.

3. **Align version numbers** - Ensure consistent versioning across FastAPI app and health endpoints.

### Medium Priority

4. **Add input validation** - Validate phone numbers, email formats, and FCM tokens before sending.

5. **Implement circuit breaker** - Add circuit breaker pattern for external services (Twilio, SendGrid, Firebase).

6. **Add delivery receipts** - Track message delivery status from providers.

7. **Implement retry logic** - Add exponential backoff retry for failed deliveries.

### Low Priority

8. **Add OpenAPI tags** - Organize endpoints with OpenAPI tags for better documentation.

9. **Add rate limiting per channel** - Different rate limits for SMS vs push notifications.

10. **Add notification batching** - Batch notifications to reduce API calls to external services.

---

## Kong Gateway Routes

| Route | Service Route | Strip Path |
|-------|---------------|------------|
| `/api/v1/notifications` | `/` | true |
| `/api/v1/notification` | `/` | true |
| `/notification` | `/` | true |
| `/api/v1/channels` | `/channels` | true |
| `/api/v1/preferences` | `/preferences` | true |
| `/api/v1/alerts` | `/` | true |
| `/alerts` | `/` | true |
| `/api/v1/notification-stats` | `/stats` | true |
| `/api/v1/reminders` | `/` | true |
| `/api/v1/farmers` | `/` | true |

---

## File Structure

```
apps/services/notification-service/
├── Dockerfile
├── requirements.txt
├── init_db.py
├── migrate_farmer_profiles.py
├── test_api.py
├── examples/
│   └── farmer_profile_usage.py
├── src/
│   ├── __init__.py
│   ├── main.py                      # FastAPI application
│   ├── models.py                    # Tortoise ORM models
│   ├── database.py                  # Database initialization
│   ├── repository.py                # Data access layer
│   ├── nats_subscriber.py           # NATS event handler
│   ├── notification_scheduler.py    # Scheduled notifications
│   ├── notification_types.py        # Type definitions
│   ├── channels_controller.py       # Channel management API
│   ├── channels_service.py          # Channel business logic
│   ├── preferences_controller.py    # Preferences API
│   ├── preferences_service.py       # Preferences business logic
│   ├── otp_controller.py            # OTP API
│   ├── otp_service.py               # OTP business logic
│   ├── sms_client.py                # Twilio SMS client
│   ├── sms_providers.py             # Multi-provider SMS
│   ├── email_client.py              # SendGrid/SMTP email client
│   ├── firebase_client.py           # FCM push notifications
│   ├── whatsapp_client.py           # WhatsApp client
│   ├── telegram_client.py           # Telegram client
│   ├── security_utils.py            # Security utilities
│   └── templates/
│       ├── __init__.py
│       ├── notification_templates.py
│       ├── template_examples.py
│       ├── test_templates.py
│       ├── ar/                      # Arabic templates
│       │   └── *.json
│       └── en/                      # English templates
│           └── weather_alert.json
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── test_email_sms_services.py
    ├── test_notification_api.py
    ├── test_notification_controller.py
    ├── test_notification_service.py
    ├── test_notification_service_comprehensive.py
    ├── test_notification_service_extended.py
    ├── test_notifications.py
    ├── test_push_service.py
    └── test_security_utils.py
```

---

## Health Check Configuration

```yaml
healthcheck:
  test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8110/healthz')"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 15s
```

---

## Resource Limits (Docker)

```yaml
deploy:
  resources:
    limits:
      cpus: '0.5'
      memory: 512M
    reservations:
      cpus: '0.25'
      memory: 128M
```
