# USSD Gateway Service - بوابة USSD

SMS, USSD, and WhatsApp support for farmers with basic phones.

## Features | الميزات

- **USSD Menus**: Interactive menu navigation via `*384#`
- **SMS Keywords**: Text-based queries (WEATHER, FIELD, etc.)
- **SMS Alerts**: Forward system alerts to SMS
- **WhatsApp Integration**: WhatsApp Business API support
- **Bilingual**: Arabic and English support

## USSD Menu Structure | هيكل قوائم USSD

```
*384# Main Menu
├── 1. Weather (طقس)
│   ├── 1. Today
│   ├── 2. 3-Day Forecast
│   └── 3. Rain Alert
├── 2. My Fields (حقولي)
│   ├── 1. Field Status
│   ├── 2. NDVI Health
│   └── 3. Recent Alerts
├── 3. Irrigation (الري)
│   ├── 1. Today's Schedule
│   ├── 2. Soil Moisture
│   ├── 3. Start Irrigation
│   └── 4. Stop Irrigation
├── 4. Alerts (التنبيهات)
├── 5. Market Prices (أسعار السوق)
└── 6. Help (مساعدة)
```

## SMS Keywords | كلمات SMS المفتاحية

| English | Arabic | Response |
|---------|--------|----------|
| WEATHER | طقس | Today's weather |
| RAIN | مطر | Rain alert subscription |
| FIELD | حقل | Field status |
| NDVI | - | Crop health |
| WATER | ماء | Soil moisture |
| PRICE | سعر | Market prices |
| HELP | مساعدة | Usage guide |
| REGISTER | تسجيل | New farm registration |

## API Endpoints

### USSD
- `POST /ussd/callback` - USSD callback from telco
- `POST /ussd/simulate` - Test USSD session

### SMS
- `POST /sms/send` - Send SMS
- `POST /sms/receive` - Receive SMS webhook
- `POST /sms/bulk` - Bulk SMS

### WhatsApp
- `POST /whatsapp/webhook` - WhatsApp webhook
- `POST /whatsapp/send` - Send WhatsApp message

## Supported Providers

- **SMS**: Unifonic (Saudi), Africa's Talking, Twilio
- **USSD**: Africa's Talking, local telcos
- **WhatsApp**: Meta Business API

## Environment Variables

```bash
SMS_PROVIDER=unifonic
UNIFONIC_APP_SID=xxx
UNIFONIC_SENDER_ID=SAHOOL

WHATSAPP_PHONE_ID=xxx
WHATSAPP_ACCESS_TOKEN=xxx
```

## Port: 8130
