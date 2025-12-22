# Field-First Architecture - العمارة الميدانية أولاً
## SAHOOL Unified Platform v15.5

> **المبدأ الأساسي:** المنصة ميدانية، والتحليل يخدم الميدان
>
> **Core Principle:** The platform is field-first; analysis serves the field

---

## 📋 جدول المحتويات | Table of Contents

1. [نظرة عامة | Overview](#overview)
2. [المكونات الأساسية | Core Components](#core-components)
3. [خريطة الخدمات | Service Map](#service-map)
4. [تدفق البيانات | Data Flow](#data-flow)
5. [قالب الإجراء | ActionTemplate](#action-template)
6. [طبقة الجسر | Bridge Layer](#bridge-layer)
7. [دليل التكامل | Integration Guide](#integration-guide)

---

## <a name="overview"></a>🎯 نظرة عامة | Overview

### المشكلة | The Problem
```
التحليلات المتقدمة ← لوحات البيانات ← [فجوة] ← عمل الميدان
Advanced Analytics → Dashboards → [GAP] → Field Action
```

### الحل | The Solution
```
التحليل ← ActionTemplate ← NATS ← الإشعارات ← التطبيق المحمول ← المزارع
Analysis → ActionTemplate → NATS → Notifications → Mobile App → Farmer
```

### القواعد الذهبية | Golden Rules

| القاعدة | Rule | الوصف |
|---------|------|--------|
| 🎯 **الإجراء أولاً** | Action First | كل تحليل ينتج ActionTemplate |
| 📱 **قابل للتنفيذ** | Executable | التعليمات واضحة ومحددة |
| 🔌 **يعمل بدون إنترنت** | Offline Ready | Fallback لكل إجراء |
| ⏰ **متى وليس فقط كيف** | When not just How | قرارات التوقيت واضحة |
| 🏷️ **الشفافية** | Transparency | Badges توضح مصدر البيانات |

---

## <a name="core-components"></a>🏗️ المكونات الأساسية | Core Components

### 1. ActionTemplate - قالب الإجراء

```
┌─────────────────────────────────────────────────────────────┐
│                     ActionTemplate                          │
├─────────────────────────────────────────────────────────────┤
│  📌 WHAT (ماذا)    │ "إجراء ري طارئ"                        │
│  ❓ WHY (لماذا)    │ "رطوبة التربة منخفضة (22%)"           │
│  ⏰ WHEN (متى)     │ "خلال 6 ساعات"                         │
│  📝 HOW (كيف)      │ ["شغل المضخة", "اسقِ 15 دقيقة", ...]  │
│  🔌 FALLBACK       │ "إذا لم تتوفر المضخة: ري يدوي عميق"   │
├─────────────────────────────────────────────────────────────┤
│  🏷️ Badge          │ { type: "virtual_estimate", ... }      │
│  📊 Confidence     │ 0.75                                   │
│  🚨 Priority       │ "high"                                 │
└─────────────────────────────────────────────────────────────┘
```

### 2. NATS Event Spine - العمود الفقري للأحداث

```
┌──────────────┐    ┌──────────────┐    ┌──────────────────────┐
│   Analysis   │───▶│    NATS      │───▶│ Notification Service │
│   Service    │    │   Broker     │    │                      │
└──────────────┘    └──────────────┘    └──────────┬───────────┘
                                                    │
                    sahool.analysis.completed       │
                    sahool.alerts.created           ▼
                                            ┌──────────────┐
                                            │  Mobile App  │
                                            │  (Firebase)  │
                                            └──────────────┘
```

### 3. Badge System - نظام الشارات

| الشارة | Badge | اللون | الاستخدام |
|--------|-------|-------|-----------|
| 🛰️ قراءة قمر صناعي | Satellite Reading | `#10B981` | بيانات مباشرة من القمر الصناعي |
| 📡 قراءة حساس | IoT Reading | `#3B82F6` | بيانات من أجهزة IoT |
| 🧮 تقدير افتراضي | Virtual Estimate | `#6366F1` | حساب برمجي بدون حساس |
| ⚠️ تقدير تاريخي | Historical Estimate | `#F59E0B` | بناء على بيانات سابقة |

---

## <a name="service-map"></a>🗺️ خريطة الخدمات | Service Map

### الخدمات المُفعّلة | Activated Services

```
┌─────────────────────────────────────────────────────────────────────┐
│                    FIELD-FIRST ACTIVATED SERVICES                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐ │
│  │ satellite       │    │ virtual-sensors │    │ crop-growth     │ │
│  │ service         │    │                 │    │ timing          │ │
│  │ :8090           │    │ :8085           │    │ :8098           │ │
│  │                 │    │                 │    │                 │ │
│  │ ✅ ActionTemplate│    │ ✅ ActionTemplate│    │ ✅ ActionTemplate│ │
│  │ ✅ NATS Events  │    │ ✅ NATS Events  │    │ ✅ NATS Events  │ │
│  │ ✅ Badges       │    │ ✅ Badges       │    │ ✅ Badges       │ │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘ │
│                                                                     │
│  ┌─────────────────┐    ┌─────────────────┐                        │
│  │ notification    │    │ irrigation      │                        │
│  │ service         │    │ smart           │                        │
│  │ :8083           │    │ :8086           │                        │
│  │                 │    │                 │                        │
│  │ ✅ NATS Sub     │    │ ✅ ActionTemplate│                        │
│  │ ✅ Firebase Push│    │ ✅ NATS Events  │                        │
│  └─────────────────┘    └─────────────────┘                        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### الخدمات المطلوب تفعيلها | Services to Activate

| الخدمة | Service | المنفذ | الأولوية | الحالة |
|--------|---------|--------|----------|--------|
| yield-prediction | توقع الإنتاجية | 8091 | 🔴 عالية | 📋 مخطط |
| lai-estimation | تقدير LAI | 8093 | 🟡 متوسطة | 📋 مخطط |
| disaster-assessment | تقييم الكوارث | 8094 | 🟡 متوسطة | 📋 مخطط |
| weather-advanced | الطقس المتقدم | 8092 | 🟢 منخفضة | 📋 مخطط |

---

## <a name="data-flow"></a>🔄 تدفق البيانات | Data Flow

### سيناريو: توصية ري طارئة

```
┌─────────────────────────────────────────────────────────────────────┐
│                     IRRIGATION ALERT FLOW                           │
└─────────────────────────────────────────────────────────────────────┘

1️⃣ الطلب | Request
   ┌──────────────────────────────────────────────────────────────┐
   │ POST /v1/irrigation/recommend-with-action                    │
   │ { "field_id": "field-001", "location": {...} }              │
   └──────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
2️⃣ التحليل | Analysis
   ┌──────────────────────────────────────────────────────────────┐
   │ virtual-sensors :8085                                        │
   │ • حساب ET₀ باستخدام FAO-56 Penman-Monteith                  │
   │ • تقدير رطوبة التربة (بدون IoT)                              │
   │ • إنشاء ActionTemplate مع badge "تقدير افتراضي"              │
   └──────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
3️⃣ نشر الحدث | Event Publishing
   ┌──────────────────────────────────────────────────────────────┐
   │ NATS: sahool.analysis.completed                              │
   │ {                                                            │
   │   "type": "irrigation_recommendation",                       │
   │   "field_id": "field-001",                                  │
   │   "priority": "high",                                        │
   │   "action_template": { ... }                                 │
   │ }                                                            │
   └──────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
4️⃣ الإشعار | Notification
   ┌──────────────────────────────────────────────────────────────┐
   │ notification-service :8083                                   │
   │ • استقبال من NATS                                            │
   │ • إرسال Firebase Push                                        │
   │ • حفظ في قاعدة البيانات                                      │
   └──────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
5️⃣ التطبيق المحمول | Mobile App
   ┌──────────────────────────────────────────────────────────────┐
   │ 📱 إشعار: "تنبيه ري - حقل الوادي"                            │
   │                                                              │
   │ 🏷️ تقدير افتراضي (بدون حساس)                                │
   │                                                              │
   │ ⏰ متى: خلال 6 ساعات                                        │
   │ 📝 كيف:                                                      │
   │    1. شغّل المضخة الرئيسية                                   │
   │    2. اسقِ لمدة 15 دقيقة                                     │
   │    3. راقب تشرب التربة                                       │
   │                                                              │
   │ 🔌 بدون مضخة: ري يدوي عميق حول الجذور                       │
   │                                                              │
   │ [✅ تم التنفيذ] [⏰ تأجيل] [❌ تجاهل]                         │
   └──────────────────────────────────────────────────────────────┘
```

### سيناريو: توقيت النمو

```
┌─────────────────────────────────────────────────────────────────────┐
│                     GROWTH TIMING FLOW                              │
└─────────────────────────────────────────────────────────────────────┘

1️⃣ POST /v1/analyze-timing
   { "field_id": "field-001", "crop_type": "wheat", ... }
                                    │
                                    ▼
2️⃣ crop-growth-timing :8098
   • تحديد مرحلة النمو الحالية (التفريع)
   • تحليل نافذة المخاطر (7 أيام)
   • توليد توصيات التوقيت
                                    │
                                    ▼
3️⃣ ActionTemplate
   {
     "what": "تطبيق الدفعة الأولى من السماد",
     "why": "المحصول في مرحلة التفريع - الوقت المثالي للتسميد",
     "when": {
       "deadline": "2024-01-25",
       "optimal_window": "صباحاً قبل الحرارة"
     },
     "how": [
       "استخدم سماد NPK 15-15-15",
       "الكمية: 50 كجم/هكتار",
       "وزّع بالتساوي حول النباتات"
     ],
     "fallback": "إذا لم يتوفر NPK: استخدم يوريا 25 كجم"
   }
```

---

## <a name="action-template"></a>📋 قالب الإجراء | ActionTemplate

### البنية الكاملة | Full Structure

```python
class ActionTemplate(BaseModel):
    """قالب الإجراء الميداني"""

    # === الهوية | Identity ===
    id: str                          # معرف فريد
    type: ActionType                 # نوع الإجراء
    priority: Priority               # الأولوية

    # === السياق | Context ===
    field_id: str                    # معرف الحقل
    source_analysis: str             # مصدر التحليل

    # === المحتوى | Content ===
    what: str                        # ماذا نفعل
    why: str                         # لماذا
    when: ActionTiming               # متى (deadline, optimal_window)
    how: List[str]                   # خطوات التنفيذ
    fallback: str                    # البديل بدون موارد

    # === البيانات الوصفية | Metadata ===
    badge: Optional[Badge]           # شارة مصدر البيانات
    confidence: float                # مستوى الثقة (0-1)
    expires_at: datetime             # تاريخ انتهاء الصلاحية

    # === التتبع | Tracking ===
    created_at: datetime
    acknowledged_at: Optional[datetime]
    executed_at: Optional[datetime]
    execution_notes: Optional[str]
```

### أنواع الإجراءات | Action Types

```python
class ActionType(str, Enum):
    # ري | Irrigation
    IRRIGATION_URGENT = "irrigation_urgent"
    IRRIGATION_SCHEDULED = "irrigation_scheduled"

    # تسميد | Fertilization
    FERTILIZATION_TIMING = "fertilization_timing"
    FERTILIZATION_URGENT = "fertilization_urgent"

    # حماية | Protection
    PEST_ALERT = "pest_alert"
    DISEASE_ALERT = "disease_alert"
    WEATHER_PROTECTION = "weather_protection"

    # حصاد | Harvest
    HARVEST_TIMING = "harvest_timing"
    HARVEST_URGENT = "harvest_urgent"

    # مراقبة | Monitoring
    FIELD_INSPECTION = "field_inspection"
    GROWTH_CHECK = "growth_check"
```

---

## <a name="bridge-layer"></a>🌉 طبقة الجسر | Bridge Layer

### لماذا طبقة الجسر؟ | Why Bridge Layer?

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│   خدمة TypeScript/NestJS          خدمة Python FastAPI              │
│   ┌─────────────────────┐         ┌─────────────────────┐          │
│   │ crop-growth-model   │         │ crop-growth-timing  │          │
│   │ :8097               │         │ :8098 (Python)      │          │
│   │                     │────────▶│                     │          │
│   │ • محاكاة DSSAT      │         │ • قرارات "متى"      │          │
│   │ • محاكاة AquaCrop   │         │ • ActionTemplates   │          │
│   │ • نماذج معقدة       │         │ • NATS Publishing   │          │
│   └─────────────────────┘         └─────────────────────┘          │
│                                                                     │
│   الخدمة الأصلية تبقى كما هي    الجسر يضيف Field-First            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### متى نستخدم الجسر؟ | When to Use Bridge?

| الحالة | الحل |
|--------|------|
| خدمة Python موجودة | إضافة endpoints مباشرة |
| خدمة NestJS/TypeScript | إنشاء Python Bridge |
| خدمة Java/Go | إنشاء Python Bridge أو TypeScript wrapper |
| خدمة جديدة | Python FastAPI من البداية |

---

## <a name="integration-guide"></a>📚 دليل التكامل | Integration Guide

### 1. إضافة ActionTemplate لخدمة موجودة

```python
# الخطوة 1: استيراد المكتبات
from shared.contracts.actions import ActionTemplateFactory, ActionType, Priority
from shared.libs.events import publish_analysis_completed_sync, NATS_AVAILABLE

# الخطوة 2: إنشاء endpoint جديد
@app.post("/v1/{analysis_type}/with-action")
async def analysis_with_action(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
):
    # الخطوة 3: تنفيذ التحليل
    result = perform_analysis(request)

    # الخطوة 4: إنشاء ActionTemplate
    action = ActionTemplateFactory.create_recommendation(
        action_type=ActionType.IRRIGATION_URGENT,
        priority=Priority.HIGH,
        field_id=request.field_id,
        source_analysis="my-service",
        what="...",
        why="...",
        when=ActionTiming(deadline=..., optimal_window="..."),
        how=["step 1", "step 2"],
        fallback="...",
        badge=Badge(type="virtual_estimate", ...),
        confidence=0.75,
    )

    # الخطوة 5: نشر إلى NATS (في الخلفية)
    if NATS_AVAILABLE and action.priority in [Priority.HIGH, Priority.CRITICAL]:
        background_tasks.add_task(
            publish_analysis_completed_sync,
            analysis_type="my_analysis",
            field_id=request.field_id,
            priority=action.priority.value,
            action_template=action.model_dump(),
        )

    return {"result": result, "action_template": action}
```

### 2. إنشاء خدمة جسر جديدة

```bash
# الهيكل
apps/services/existing-service/
├── src/                    # الكود الأصلي (NestJS/Java/etc)
└── python-bridge/
    ├── main.py            # FastAPI app
    ├── requirements.txt   # Dependencies
    └── Dockerfile         # Container config

# المنفذ: الخدمة الأصلية + 1
# مثال: crop-growth-model :8097 → crop-growth-timing :8098
```

### 3. تكوين NATS

```python
# shared/libs/events/nats_publisher.py

NATS_CONFIG = NATSConfig(
    servers=["nats://localhost:4222"],
    subject_prefix="sahool",
)

# المواضيع | Subjects
# sahool.analysis.completed     - تحليل اكتمل
# sahool.alerts.created         - تنبيه جديد
# sahool.actions.acknowledged   - إجراء تم الاعتراف به
# sahool.actions.executed       - إجراء تم تنفيذه
```

### 4. اختبار التكامل

```bash
# 1. تشغيل NATS
docker run -p 4222:4222 nats:latest

# 2. تشغيل الخدمة
cd apps/services/virtual-sensors
python -m uvicorn src.main:app --port 8085

# 3. اختبار الـ endpoint
curl -X POST http://localhost:8085/v1/irrigation/recommend-with-action \
  -H "Content-Type: application/json" \
  -d '{
    "field_id": "field-001",
    "location": {"lat": 15.35, "lon": 44.21}
  }'

# 4. التحقق من NATS (في terminal آخر)
nats sub "sahool.>"
```

---

## 📊 الفجوات المتبقية | Remaining Gaps

### الأولوية العالية | High Priority

| الفجوة | Gap | الحل المقترح |
|--------|-----|---------------|
| yield-prediction لا يُنتج ActionTemplate | إضافة endpoint `/with-action` |
| لا يوجد تنبيه قبل الحصاد | ربط yield-prediction بـ NATS |
| lai-estimation غير متصل | إضافة early-stress ActionTemplate |

### الأولوية المتوسطة | Medium Priority

| الفجوة | Gap | الحل المقترح |
|--------|-----|---------------|
| disaster-assessment بدون playbooks | إنشاء Playbook ActionTemplates |
| weather-advanced لا يُجدول | ربط بـ irrigation-smart للجدولة |
| لا يوجد تجميع للتنبيهات | Alert aggregation في notification-service |

### الأولوية المنخفضة | Low Priority

| الفجوة | Gap | الحل المقترح |
|--------|-----|---------------|
| لا يوجد تتبع تنفيذ | إضافة execution tracking |
| لا يوجد تحليل أداء | Performance analytics dashboard |
| لا يوجد تعلم من الملاحظات | Feedback loop للتحسين |

---

## 🚀 الخطوات التالية | Next Steps

### المرحلة 1.3: تفعيل yield-prediction
```
- [ ] إضافة /v1/predict-with-action endpoint
- [ ] إنشاء PRE_HARVEST_ALERT ActionType
- [ ] ربط بـ NATS للتنبيهات
- [ ] اختبار التكامل
```

### المرحلة 1.4: تفعيل lai-estimation
```
- [ ] إضافة /v1/estimate-with-action endpoint
- [ ] إنشاء EARLY_STRESS_ALERT ActionType
- [ ] Badge: "تقدير من القمر الصناعي"
- [ ] اختبار التكامل
```

### المرحلة 1.5: تفعيل disaster-assessment
```
- [ ] إنشاء Playbook model
- [ ] تعريف playbooks للكوارث الشائعة
- [ ] ربط بـ NATS للطوارئ
- [ ] اختبار التكامل
```

---

## 📞 المراجع | References

- [ActionTemplate Contract](/shared/contracts/actions/)
- [NATS Publisher](/shared/libs/events/nats_publisher.py)
- [Notification Service](/apps/services/notification-service/)
- [Virtual Sensors](/apps/services/virtual-sensors/)
- [Crop Growth Timing](/apps/services/crop-growth-model/python-bridge/)

---

**آخر تحديث | Last Updated:** 2024-01-20
**الإصدار | Version:** 15.5.0
**المؤلف | Author:** KAFAAT Engineering Team
