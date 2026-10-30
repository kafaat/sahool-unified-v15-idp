# SAHOOL Notification Templating System

# نظام قوالب الإشعارات

A comprehensive bilingual notification templating system for Yemen's agricultural platform with support for multiple channels (Push, SMS, Email, WhatsApp).

## Features / المميزات

- **Bilingual Support** (Arabic primary, English secondary) / دعم ثنائي اللغة
- **Template Categories** / فئات القوالب:
  - `ALERT`: Urgent notifications (disease, weather, pests)
  - `REMINDER`: Scheduled tasks (irrigation, fertilizer)
  - `REPORT`: Daily/weekly summaries
  - `RECOMMENDATION`: AI-powered suggestions

- **Channel-Specific Formatting** / تنسيق خاص بكل قناة:
  - Push Notifications (with icons, priority, action URLs)
  - SMS (max 160 chars, no emojis)
  - Email (HTML + plain text)
  - WhatsApp (with emojis and formatting)

- **Dynamic Context Rendering** / عرض ديناميكي للسياق:
  - Placeholder replacement: `{field_name}`, `{crop_type}`, `{value}`, etc.
  - Safe handling of missing context values

## Directory Structure / هيكل الدليل

```
templates/
├── notification_templates.py   # Main template manager
├── template_examples.py        # Usage examples
├── __init__.py
├── ar/                        # Arabic templates
│   ├── disease_detected.json
│   ├── irrigation_reminder.json
│   ├── weather_alert.json
│   ├── harvest_ready.json
│   ├── yield_prediction.json
│   ├── sensor_alert.json
│   ├── fertilizer_reminder.json
│   ├── pest_outbreak.json
│   ├── daily_report.json
│   ├── weekly_report.json
│   ├── ai_recommendation.json
│   ├── market_price.json
│   └── water_shortage.json
└── en/                        # English templates
    └── [same files as ar/]
```

## Available Templates / القوالب المتاحة

### ALERT Templates (تنبيهات عاجلة)

| Template ID        | Description                           | Priority |
| ------------------ | ------------------------------------- | -------- |
| `disease_detected` | Disease detection alert               | HIGH     |
| `weather_alert`    | Weather warnings (frost, storm, etc.) | HIGH     |
| `sensor_alert`     | Sensor threshold violations           | HIGH     |
| `pest_outbreak`    | Pest outbreak warnings                | CRITICAL |
| `water_shortage`   | Water shortage alerts                 | CRITICAL |

### REMINDER Templates (تذكيرات)

| Template ID           | Description                  | Priority |
| --------------------- | ---------------------------- | -------- |
| `irrigation_reminder` | Irrigation schedule reminder | MEDIUM   |
| `fertilizer_reminder` | Fertilization schedule       | MEDIUM   |
| `harvest_ready`       | Harvest time notification    | HIGH     |

### REPORT Templates (تقارير)

| Template ID        | Description                | Priority |
| ------------------ | -------------------------- | -------- |
| `daily_report`     | Daily summary of fields    | LOW      |
| `weekly_report`    | Weekly performance summary | LOW      |
| `yield_prediction` | Yield forecast updates     | MEDIUM   |
| `market_price`     | Market price updates       | MEDIUM   |

### RECOMMENDATION Templates (توصيات)

| Template ID         | Description                     | Priority |
| ------------------- | ------------------------------- | -------- |
| `ai_recommendation` | AI-powered farm recommendations | MEDIUM   |

## Usage / الاستخدام

### Basic Usage

```python
from templates import get_template_manager, NotificationChannel

# Get the template manager
manager = get_template_manager()

# Define context data
context = {"disease_name": "البياض الدقيقي", "field_name": "حقل القمح", "field_id": "field_123", "confidence": 92}

# Render for Push notification (Arabic)
push = manager.format_for_push(template_id="disease_detected", context=context, language="ar")

# Send via Firebase/FCM
send_push_notification(title=push["notification"]["title"], body=push["notification"]["body"], data=push["data"])
```

### Multi-Channel Delivery

```python
# SMS (max 160 chars)
sms_text = manager.format_for_sms("irrigation_reminder", context, language="ar", max_length=160)

# Email (HTML)
email = manager.format_for_email("harvest_ready", context, language="ar")
send_email(subject=email["subject"], html=email["html_body"], text=email["text_body"])

# WhatsApp
whatsapp_msg = manager.format_for_whatsapp("weather_alert", context, language="ar")
```

### Template Methods

#### 1. Get Template

```python
template = manager.get_template("disease_detected", language="ar")
```

#### 2. Render Template

```python
rendered = manager.render_template(
    template_id="irrigation_reminder", context={"field_name": "الحقل الأول", "water_amount": 5000}, language="ar"
)
# Returns: {"title": "...", "body": "...", "action_url": "...", ...}
```

#### 3. Register Custom Template

```python
from templates import NotificationTemplate, TemplateCategory

custom = NotificationTemplate(
    template_id="custom_alert",
    category=TemplateCategory.ALERT,
    title={"ar": "تنبيه مخصص", "en": "Custom Alert"},
    body={"ar": "رسالة: {message}", "en": "Message: {message}"},
    priority="high",
)

manager.register_template("custom_alert", custom)
```

#### 4. List Templates

```python
# All templates
all_templates = manager.list_templates()

# By category
alerts = manager.list_templates(category=TemplateCategory.ALERT)
reminders = manager.list_templates(category=TemplateCategory.REMINDER)
```

## Template Format / صيغة القالب

JSON template structure:

```json
{
  "template_id": "disease_detected",
  "category": "alert",
  "title": "🦠 تنبيه: مرض مكتشف",
  "body": "تم اكتشاف {disease_name} في حقل {field_name}...",
  "action_url": "/fields/{field_id}/diseases",
  "icon": "🦠",
  "priority": "high",
  "metadata": {
    "requires_action": true,
    "sound": "alert",
    "vibration": true
  }
}
```

## Context Placeholders / متغيرات السياق

Common placeholders used across templates:

| Placeholder      | Description (EN)      | الوصف (AR)      |
| ---------------- | --------------------- | --------------- |
| `{field_name}`   | Field name            | اسم الحقل       |
| `{field_id}`     | Field identifier      | معرف الحقل      |
| `{crop_type}`    | Crop type             | نوع المحصول     |
| `{disease_name}` | Disease name          | اسم المرض       |
| `{location}`     | Location/Governorate  | الموقع/المحافظة |
| `{temperature}`  | Temperature           | درجة الحرارة    |
| `{water_amount}` | Water quantity        | كمية الماء      |
| `{confidence}`   | Confidence percentage | نسبة الثقة      |
| `{date}`         | Date                  | التاريخ         |
| `{value}`        | Generic value         | قيمة            |

## Channel-Specific Features

### Push Notifications

- Full rich content (title, body, icon, action URL)
- Priority levels (low, medium, high, critical)
- Custom data payload
- Sound and vibration control

### SMS

- Character limit enforcement (160 chars default)
- Emoji removal for compatibility
- Concise title + body format
- Fallback truncation

### Email

- HTML formatting with RTL support
- Responsive design
- Plain text alternative
- SAHOOL branding
- Action buttons

### WhatsApp

- Emoji support
- Basic markdown formatting (\* for bold)
- Action URL links
- Platform branding footer

## Integration Example / مثال التكامل

```python
from templates import render_notification, NotificationChannel

# Send disease alert via multiple channels
context = {"disease_name": "صدأ القمح", "field_name": "الحقل الشرقي", "field_id": "field_789", "confidence": 95}

# Push
push_data = render_notification("disease_detected", context, language="ar", channel=NotificationChannel.PUSH)
await send_push(user_id, push_data)

# SMS (for critical alerts)
sms_text = render_notification("disease_detected", context, language="ar", channel=NotificationChannel.SMS)
await send_sms(user_phone, sms_text)

# Email (for detailed info)
email_data = render_notification("disease_detected", context, language="ar", channel=NotificationChannel.EMAIL)
await send_email(user_email, email_data)
```

## Testing / الاختبار

Run the examples:

```bash
cd /home/user/sahool-unified-v15-idp/apps/services/notification-service/src/templates
python template_examples.py
```

This will demonstrate:

- All template types
- Multi-language rendering
- Channel-specific formatting
- Custom template registration
- Template listing and filtering

## Best Practices / أفضل الممارسات

1. **Language Selection**: Always default to Arabic (`language="ar"`) for Yemen farmers
2. **Context Validation**: Ensure all required placeholders are in context before rendering
3. **Channel Selection**:
   - Use SMS for critical alerts (reliability)
   - Use Push for regular notifications (rich content)
   - Use Email for detailed reports
   - Use WhatsApp for community updates
4. **Priority Levels**:
   - CRITICAL: Water shortage, pest outbreaks
   - HIGH: Disease detection, weather alerts, harvest time
   - MEDIUM: Irrigation reminders, AI recommendations
   - LOW: Daily reports, market updates
5. **Timing**: Send irrigation/fertilizer reminders at optimal times (5-7 AM)

## Adding New Templates / إضافة قوالب جديدة

1. Create JSON files in both `ar/` and `en/` directories
2. Use consistent template_id across languages
3. Include all required fields (template_id, category, title, body)
4. Define appropriate placeholders in body text
5. Set correct priority level
6. Add relevant metadata
7. Test with sample context data

Example:

```json
// ar/my_template.json
{
  "template_id": "my_template",
  "category": "reminder",
  "title": "العنوان بالعربية مع {placeholder}",
  "body": "النص بالعربية...",
  "action_url": "/path/{id}",
  "icon": "🌾",
  "priority": "medium"
}
```

## Dependencies / المتطلبات

- Python 3.8+
- No external dependencies (uses stdlib only)
- JSON templates loaded at initialization

## License

Part of the SAHOOL Unified Platform - Smart Agriculture for Yemen

---

**Contact**: For template requests or issues, contact the SAHOOL development team.

**نظام قوالب الإشعارات - سَهُول**
