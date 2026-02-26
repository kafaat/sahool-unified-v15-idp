# USSD Gateway | بوابة USSD

SMS, USSD, and WhatsApp support for farmers using basic (feature) phones without smartphone access.

**Port:** 8183 | **Type:** Python / FastAPI | **Version:** 16.0.0

---

## Overview

The USSD Gateway extends SAHOOL platform reach to smallholder farmers in low-connectivity environments who use basic phones. It provides three interaction channels: USSD menus (accessed via `*384#`), SMS keyword responses, and WhatsApp Business API integration. All channels support full Arabic and English bilingual responses, with language preference persisted per phone number in the database.

Key capabilities:
- Interactive USSD menu navigation with session state management
- SMS keyword-based queries (weather, field status, NDVI, prices, irrigation, registration)
- Bulk SMS broadcasting to farmer groups
- WhatsApp Business API webhook and outbound messaging
- Alert forwarding from NATS to SMS for subscribed farmers
- Automatic language detection from user database preference
- Multi-provider SMS support: Unifonic (Saudi), Africa's Talking, Twilio
- WhatsApp via Meta Business Cloud API

---

## Architecture

```
Telecom Provider / Meta Cloud API
        |
USSD Gateway (8183)
├── USSD Callback Processor    — Menu state machine navigation
├── SMS Keyword Processor      — Keyword → action mapping
├── WhatsApp Webhook Handler   — Message and button events
├── NATS Subscriber            — sahool.*.alert.* → SMS forwarding
├── src/api/v1/                — Additional API routes
└── src/handlers/ussd_actions.py — Action handlers per menu item

External:
├── PostgreSQL  — User language preferences, notification settings
├── NATS        — Alert event subscription for SMS forwarding
└── SMS/WA providers (configured via env vars)
```

---

## USSD Menu Structure (`*384#`)

```
Main Menu | القائمة الرئيسية
├── 1. Weather | الطقس
│   ├── 1. Today | اليوم
│   ├── 2. 3-Day Forecast | توقعات 3 أيام
│   └── 3. Rain Alert | تنبيه مطر
├── 2. My Fields | حقولي
│   ├── 1. Field Status | حالة الحقل
│   ├── 2. NDVI Health | صحة المحصول (NDVI)
│   └── 3. Recent Alerts | التنبيهات الأخيرة
├── 3. Irrigation | الري
│   ├── 1. Today's Schedule | جدول اليوم
│   ├── 2. Soil Moisture | رطوبة التربة
│   ├── 3. Start Irrigation | بدء الري
│   └── 4. Stop Irrigation | إيقاف الري
├── 4. Alerts | التنبيهات
├── 5. Market Prices | أسعار السوق (Wheat, Barley, Dates, Vegetables)
└── 6. Help | مساعدة (Usage guide, Contact support, Register farm)
```

---

## SMS Keywords

| English Keyword | Arabic Keyword | Response |
|----------------|----------------|----------|
| `WEATHER` | `طقس` | Current weather conditions |
| `RAIN` | `مطر` | Rain probability / alert subscription |
| `FIELD` | `حقل` | Active field status |
| `NDVI` | — | Crop health index |
| `WATER` | `ماء` | Current soil moisture |
| `PRICE` | `سعر` | Wheat market price |
| `HELP` | `مساعدة` | Usage guide |
| `REGISTER` | `تسجيل` | New farm registration flow |

---

## API Endpoints

### Health

| Method | Path | Description |
|--------|------|-------------|
| GET | `/healthz` | Kubernetes liveness probe |
| GET | `/readyz` | Readiness probe (DB + NATS status) |

### USSD

| Method | Path | Description |
|--------|------|-------------|
| POST | `/ussd/callback` | USSD callback from telecom provider (JSON or form-data) |
| POST | `/ussd/simulate` | Simulate USSD session for testing |

The callback endpoint auto-detects Africa's Talking (form data) and JSON formats. Responses use `CON` prefix for continuation and `END` prefix for session termination.

### SMS

| Method | Path | Description |
|--------|------|-------------|
| POST | `/sms/send` | Send SMS to a farmer (language auto-selected from DB) |
| POST | `/sms/receive` | Receive incoming SMS webhook (keyword processing) |
| POST | `/sms/bulk` | Send bulk SMS to multiple phone numbers |

### WhatsApp

| Method | Path | Description |
|--------|------|-------------|
| POST | `/whatsapp/webhook` | WhatsApp Business API webhook (text and interactive button messages) |
| POST | `/whatsapp/send` | Send WhatsApp message (plain text, template, with buttons) |

---

## NATS Events

### Subscribes

| Subject | Purpose |
|---------|---------|
| `sahool.*.alert.*` | Forward critical/warning alerts to farmer SMS |

Subscription handler queries `user_notification_settings` table for phone numbers with `sms_enabled=true` matching the alert type, then sends SMS via configured provider.

---

## Environment Variables

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `PORT` | `8183` | No | Service port |
| `ENVIRONMENT` | `development` | No | Environment name |
| `DATABASE_URL` | - | No | PostgreSQL (for language prefs, notification settings) |
| `NATS_URL` | - | No | NATS for alert subscription |
| `CORS_ORIGINS` | `https://sahool.kafaat.io,...` | No | Allowed CORS origins |
| `SMS_PROVIDER` | `unifonic` | No | SMS provider: `unifonic`, `africastalking`, `twilio` |
| `UNIFONIC_APP_SID` | - | No | Unifonic application SID |
| `UNIFONIC_SENDER_ID` | `SAHOOL` | No | Unifonic sender ID |
| `WHATSAPP_PHONE_ID` | - | No | WhatsApp Business phone number ID |
| `WHATSAPP_ACCESS_TOKEN` | - | No | Meta WhatsApp Cloud API access token |
| `LOG_LEVEL` | `INFO` | No | Logging verbosity |

---

## Dependencies

- **FastAPI** 0.128.5 — HTTP framework
- **asyncpg** — PostgreSQL async driver
- **nats-py** — NATS alert subscription
- `shared.errors_py` — Unified error handling
- `shared.observability.logging` — Structured logging
- SMS provider SDKs (Unifonic / Africa's Talking / Twilio)

---

## Related Services

- **weather-service** (8092) — Weather data for SMS/USSD weather actions
- **irrigation-smart** (8094) — Soil moisture and irrigation schedule data
- **alert-service** (8113) — Alert events forwarded to SMS
- **field-management-service** (3000) — Field status for USSD field menu
- **whatsapp-bot-service** (8240) — Full AI-powered WhatsApp chatbot (complementary service)
