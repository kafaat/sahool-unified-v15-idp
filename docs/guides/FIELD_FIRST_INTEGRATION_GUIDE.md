# Field-First Integration Guide - دليل تكامل الميدان أولاً

## SAHOOL Platform v15.5

---

## 📋 جدول المحتويات

1. [مقدمة](#introduction)
2. [المتطلبات الأساسية](#prerequisites)
3. [إضافة ActionTemplate لخدمة موجودة](#add-action-template)
4. [ربط خدمة بـ NATS](#nats-integration)
5. [نظام الشارات](#badge-system)
6. [إنشاء Python Bridge](#python-bridge)
7. [أمثلة عملية](#examples)
8. [استكشاف الأخطاء](#troubleshooting)

---

## <a name="introduction"></a>🎯 مقدمة | Introduction

هذا الدليل يشرح كيفية تحويل خدمة تحليل موجودة إلى خدمة متوافقة مع Field-First Architecture.

**المبدأ الأساسي:**

```
كل تحليل يجب أن ينتج ActionTemplate قابل للتنفيذ في الميدان
```

---

## <a name="prerequisites"></a>📦 المتطلبات الأساسية | Prerequisites

### 1. المكتبات المشتركة

```python
# تأكد من وجود هذه المكتبات في PYTHONPATH
# shared/contracts/actions/ - ActionTemplate models
# shared/libs/events/ - NATS publisher

import sys
sys.path.insert(0, "/path/to/sahool-unified-v15-idp")

from shared.contracts.actions import (
    ActionTemplate,
    ActionTemplateFactory,
    ActionType,
    Priority,
    ActionTiming,
    Badge,
)
from shared.libs.events import (
    publish_analysis_completed_sync,
    NATS_AVAILABLE,
)
```

### 2. تبعيات Python

```txt
# requirements.txt
fastapi>=0.100.0
uvicorn>=0.22.0
pydantic>=2.0.0
nats-py>=2.3.0  # للتكامل مع NATS
```

### 3. متغيرات البيئة

```env
# NATS Configuration
NATS_URL=nats://localhost:4222
NATS_ENABLED=true

# Service Configuration
SERVICE_NAME=my-service
SERVICE_PORT=8XXX
```

---

## <a name="add-action-template"></a>📝 إضافة ActionTemplate لخدمة موجودة

### الخطوة 1: تعريف Request/Response Models

```python
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class MyAnalysisRequest(BaseModel):
    """طلب التحليل"""
    field_id: str = Field(..., description="معرف الحقل")
    # أضف الحقول الخاصة بتحليلك
    parameter1: float
    parameter2: Optional[str] = None

class MyAnalysisResponse(BaseModel):
    """استجابة التحليل مع ActionTemplate"""
    field_id: str
    analysis_result: dict
    action_template: Optional[dict] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### الخطوة 2: إنشاء Endpoint جديد

```python
from fastapi import FastAPI, BackgroundTasks

app = FastAPI(title="My Service")

@app.post("/v1/analyze-with-action", response_model=MyAnalysisResponse)
async def analyze_with_action(
    request: MyAnalysisRequest,
    background_tasks: BackgroundTasks,
):
    """
    تحليل مع إنتاج ActionTemplate
    Field-First: ينتج إجراء قابل للتنفيذ
    """

    # 1. تنفيذ التحليل الفعلي
    analysis_result = perform_my_analysis(request)

    # 2. تحديد الإجراء المطلوب بناءً على النتائج
    action_template = create_action_from_result(
        result=analysis_result,
        field_id=request.field_id,
    )

    # 3. نشر إلى NATS إذا كانت الأولوية عالية
    if action_template and action_template.get("priority") in ["high", "critical"]:
        background_tasks.add_task(
            publish_to_nats,
            analysis_type="my_analysis",
            field_id=request.field_id,
            action_template=action_template,
        )

    return MyAnalysisResponse(
        field_id=request.field_id,
        analysis_result=analysis_result,
        action_template=action_template,
    )
```

### الخطوة 3: إنشاء ActionTemplate

```python
from datetime import datetime, timedelta

def create_action_from_result(result: dict, field_id: str) -> dict:
    """
    تحويل نتيجة التحليل إلى ActionTemplate
    """

    # تحديد نوع الإجراء والأولوية
    if result["severity"] == "critical":
        action_type = "urgent_intervention"
        priority = "critical"
        deadline = datetime.utcnow() + timedelta(hours=2)
    elif result["severity"] == "warning":
        action_type = "scheduled_action"
        priority = "high"
        deadline = datetime.utcnow() + timedelta(hours=24)
    else:
        action_type = "routine_check"
        priority = "medium"
        deadline = datetime.utcnow() + timedelta(days=3)

    # بناء ActionTemplate
    action_template = {
        "id": f"action-{field_id}-{datetime.utcnow().timestamp()}",
        "type": action_type,
        "priority": priority,
        "field_id": field_id,
        "source_analysis": "my-service",

        # المحتوى الأساسي
        "what": determine_what(result),
        "why": determine_why(result),
        "when": {
            "deadline": deadline.isoformat(),
            "optimal_window": determine_optimal_window(result),
        },
        "how": generate_steps(result),
        "fallback": generate_fallback(result),

        # البيانات الوصفية
        "confidence": result.get("confidence", 0.8),
        "created_at": datetime.utcnow().isoformat(),
        "expires_at": (deadline + timedelta(hours=6)).isoformat(),
    }

    return action_template

def determine_what(result: dict) -> str:
    """تحديد ماذا يجب فعله"""
    # منطق تحديد الإجراء
    if result["type"] == "irrigation_needed":
        return "إجراء ري عاجل"
    elif result["type"] == "pest_detected":
        return "معالجة آفات"
    # ... المزيد من الحالات
    return "فحص الحقل"

def determine_why(result: dict) -> str:
    """تحديد سبب الإجراء"""
    return f"بناءً على التحليل: {result['summary']}"

def determine_optimal_window(result: dict) -> str:
    """تحديد الوقت الأمثل"""
    if result["type"] == "irrigation_needed":
        return "المساء بعد غروب الشمس"
    elif result["type"] == "fertilization":
        return "صباحاً قبل الحرارة"
    return "في أقرب وقت ممكن"

def generate_steps(result: dict) -> list:
    """توليد خطوات التنفيذ"""
    return [
        "الخطوة الأولى",
        "الخطوة الثانية",
        "الخطوة الثالثة",
    ]

def generate_fallback(result: dict) -> str:
    """توليد البديل"""
    return "إذا لم تتوفر الموارد: [الإجراء البديل]"
```

---

## <a name="nats-integration"></a>📡 ربط خدمة بـ NATS

### الخطوة 1: إعداد الناشر

```python
import os

# استيراد الناشر المشترك
try:
    from shared.libs.events import (
        publish_analysis_completed_sync,
        NATS_AVAILABLE,
    )
except ImportError:
    NATS_AVAILABLE = False
    publish_analysis_completed_sync = None

# التحقق من تفعيل NATS
NATS_ENABLED = os.getenv("NATS_ENABLED", "false").lower() == "true"
```

### الخطوة 2: النشر في Background Task

```python
async def publish_to_nats(
    analysis_type: str,
    field_id: str,
    action_template: dict,
):
    """نشر إلى NATS بشكل غير متزامن"""

    if not NATS_AVAILABLE or not NATS_ENABLED:
        logger.info("NATS not available, skipping publish")
        return

    try:
        publish_analysis_completed_sync(
            analysis_type=analysis_type,
            field_id=field_id,
            priority=action_template.get("priority", "medium"),
            action_template=action_template,
            metadata={
                "source": "my-service",
                "version": "15.5.0",
            }
        )
        logger.info(f"Published to NATS: {analysis_type} for {field_id}")
    except Exception as e:
        logger.error(f"Failed to publish to NATS: {e}")
```

### الخطوة 3: المواضيع المستخدمة

```python
# المواضيع التي ينشر إليها التحليل
NATS_SUBJECTS = {
    "analysis_completed": "sahool.analysis.completed",
    "alert_created": "sahool.alerts.created",
}

# بنية الرسالة
message_structure = {
    "event_id": "uuid",
    "timestamp": "ISO datetime",
    "type": "analysis_type",
    "field_id": "field-001",
    "priority": "high",
    "action_template": { ... },
    "metadata": {
        "source": "service-name",
        "version": "15.5.0",
    }
}
```

---

## <a name="badge-system"></a>🏷️ نظام الشارات | Badge System

### أنواع الشارات المتاحة

```python
from enum import Enum

class BadgeType(str, Enum):
    # قراءات مباشرة
    IOT_READING = "iot_reading"           # من أجهزة IoT
    SATELLITE_READING = "satellite_reading" # من القمر الصناعي

    # تقديرات
    VIRTUAL_ESTIMATE = "virtual_estimate"   # حساب برمجي
    HISTORICAL_ESTIMATE = "historical_estimate" # بيانات تاريخية
    MODEL_PREDICTION = "model_prediction"   # نموذج تنبؤي

    # مركبة
    HYBRID = "hybrid"                       # مزيج من المصادر

# الألوان المعتمدة
BADGE_COLORS = {
    "iot_reading": "#3B82F6",        # Blue
    "satellite_reading": "#10B981",   # Green
    "virtual_estimate": "#6366F1",    # Indigo
    "historical_estimate": "#F59E0B", # Amber
    "model_prediction": "#8B5CF6",    # Purple
    "hybrid": "#EC4899",              # Pink
}
```

### إضافة Badge للـ ActionTemplate

```python
def create_badge(badge_type: str, custom_label: str = None) -> dict:
    """إنشاء شارة للـ ActionTemplate"""

    labels = {
        "iot_reading": ("قراءة حساس", "IoT Reading"),
        "satellite_reading": ("قراءة قمر صناعي", "Satellite Reading"),
        "virtual_estimate": ("تقدير افتراضي", "Virtual Estimate"),
        "historical_estimate": ("تقدير تاريخي", "Historical Estimate"),
        "model_prediction": ("تنبؤ نموذج", "Model Prediction"),
    }

    label_ar, label_en = labels.get(badge_type, ("غير محدد", "Unknown"))

    return {
        "type": badge_type,
        "label_ar": custom_label or label_ar,
        "label_en": label_en,
        "color": BADGE_COLORS.get(badge_type, "#6B7280"),
    }

# استخدام في ActionTemplate
action_template = {
    # ... الحقول الأخرى
    "badge": create_badge("virtual_estimate"),
    "confidence": 0.75,  # أقل لأنه تقدير افتراضي
}
```

### إرشادات مستويات الثقة

| مصدر البيانات       | Confidence | السبب                  |
| ------------------- | ---------- | ---------------------- |
| IoT Reading         | 0.90-0.95  | قراءة مباشرة من حساس   |
| Satellite Reading   | 0.85-0.90  | قراءة مباشرة مع تأخر   |
| Virtual Estimate    | 0.70-0.80  | حساب نظري              |
| Historical Estimate | 0.60-0.75  | بناء على الماضي        |
| Model Prediction    | 0.65-0.85  | يعتمد على جودة النموذج |

---

## <a name="python-bridge"></a>🌉 إنشاء Python Bridge

### متى نستخدم Python Bridge؟

```
┌─────────────────────────────────────────────────────────────────┐
│  الخدمة الأصلية       │  الحل                                   │
├───────────────────────┼─────────────────────────────────────────┤
│  Python FastAPI       │  إضافة endpoints مباشرة                │
│  NestJS/TypeScript    │  Python Bridge                         │
│  Java Spring          │  Python Bridge                         │
│  Go                   │  Python Bridge أو Go wrapper           │
└─────────────────────────────────────────────────────────────────┘
```

### هيكل Python Bridge

```
apps/services/my-service/
├── src/                      # الكود الأصلي (NestJS/Java/etc)
│   └── main.ts
├── python-bridge/            # الجسر الجديد
│   ├── main.py              # FastAPI app
│   ├── models.py            # Pydantic models
│   ├── logic.py             # منطق التحويل
│   ├── requirements.txt     # تبعيات Python
│   └── Dockerfile           # للـ containerization
└── docker-compose.yml       # تشغيل الاثنين معاً
```

### مثال: main.py للجسر

```python
"""
Python Bridge for [Service Name]
Field-First Architecture - يحول مخرجات الخدمة إلى ActionTemplates
"""

from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
import httpx
import os

# إعدادات
ORIGINAL_SERVICE_URL = os.getenv("ORIGINAL_SERVICE_URL", "http://localhost:8097")
BRIDGE_PORT = int(os.getenv("BRIDGE_PORT", "8098"))

app = FastAPI(
    title="My Service - Python Bridge",
    version="15.5.0",
)

# --- Models ---

class BridgeRequest(BaseModel):
    field_id: str
    # المدخلات الإضافية

class BridgeResponse(BaseModel):
    original_result: dict
    action_template: dict

# --- Endpoints ---

@app.post("/v1/analyze-with-action", response_model=BridgeResponse)
async def analyze_with_action(
    request: BridgeRequest,
    background_tasks: BackgroundTasks,
):
    """
    1. استدعاء الخدمة الأصلية
    2. تحويل النتيجة إلى ActionTemplate
    3. نشر إلى NATS
    """

    # 1. استدعاء الخدمة الأصلية
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{ORIGINAL_SERVICE_URL}/original-endpoint",
                json=request.model_dump(),
                timeout=30.0,
            )
            response.raise_for_status()
            original_result = response.json()
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=502,
                detail=f"Original service error: {str(e)}"
            )

    # 2. تحويل إلى ActionTemplate
    action_template = convert_to_action_template(
        original_result=original_result,
        field_id=request.field_id,
    )

    # 3. نشر إلى NATS
    if action_template["priority"] in ["high", "critical"]:
        background_tasks.add_task(
            publish_to_nats,
            action_template=action_template,
        )

    return BridgeResponse(
        original_result=original_result,
        action_template=action_template,
    )

def convert_to_action_template(original_result: dict, field_id: str) -> dict:
    """تحويل نتيجة الخدمة الأصلية إلى ActionTemplate"""
    # منطق التحويل
    return {
        "id": f"action-{field_id}-...",
        "type": "...",
        "what": "...",
        # ...
    }

# --- Health ---

@app.get("/health")
async def health():
    return {"status": "healthy", "type": "python-bridge"}

# --- Main ---

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=BRIDGE_PORT)
```

### docker-compose.yml

```yaml
version: "3.8"

services:
  my-service-original:
    build:
      context: .
      dockerfile: Dockerfile # للخدمة الأصلية
    ports:
      - "8097:8097"
    environment:
      - PORT=8097

  my-service-bridge:
    build:
      context: ./python-bridge
    ports:
      - "8098:8098"
    environment:
      - ORIGINAL_SERVICE_URL=http://my-service-original:8097
      - BRIDGE_PORT=8098
      - NATS_URL=nats://nats:4222
    depends_on:
      - my-service-original
      - nats

  nats:
    image: nats:latest
    ports:
      - "4222:4222"
```

---

## <a name="examples"></a>💡 أمثلة عملية | Practical Examples

### مثال 1: خدمة توقع الطقس

```python
@app.post("/v1/forecast-with-action")
async def forecast_with_action(request: ForecastRequest):

    # الحصول على التوقع
    forecast = get_weather_forecast(request.location, request.days)

    # تحديد المخاطر
    risks = analyze_forecast_risks(forecast)

    # إنشاء ActionTemplate إذا وجدت مخاطر
    if risks:
        action_template = {
            "type": "weather_protection",
            "priority": "high" if risks[0]["severity"] == "severe" else "medium",
            "what": f"تحضير للـ{risks[0]['type']}",
            "why": f"توقع {risks[0]['type']} خلال {risks[0]['hours_until']} ساعة",
            "when": {
                "deadline": risks[0]["expected_time"],
                "optimal_window": "قبل الحدث بـ 6 ساعات"
            },
            "how": risks[0]["protection_steps"],
            "fallback": risks[0]["fallback_action"],
            "badge": create_badge("model_prediction"),
        }
    else:
        action_template = None

    return {
        "forecast": forecast,
        "risks": risks,
        "action_template": action_template,
    }
```

### مثال 2: خدمة كشف الآفات

```python
@app.post("/v1/detect-pests-with-action")
async def detect_pests_with_action(request: PestDetectionRequest):

    # تحليل الصورة
    detections = analyze_image_for_pests(request.image_url)

    if not detections:
        return {"detections": [], "action_template": None}

    # أعلى كشف
    top_detection = max(detections, key=lambda x: x["confidence"])

    action_template = {
        "type": "pest_alert",
        "priority": "critical" if top_detection["severity"] == "high" else "high",
        "what": f"معالجة {top_detection['pest_name_ar']}",
        "why": f"تم الكشف عن {top_detection['pest_name_ar']} بثقة {top_detection['confidence']*100:.0f}%",
        "when": {
            "deadline": (datetime.utcnow() + timedelta(hours=24)).isoformat(),
            "optimal_window": "صباحاً باكراً قبل الحرارة"
        },
        "how": [
            f"استخدم مبيد {top_detection['recommended_pesticide']}",
            f"الجرعة: {top_detection['dosage']}",
            "رش على الأوراق المصابة",
            "كرر بعد 7 أيام إذا لزم الأمر",
        ],
        "fallback": "إذا لم يتوفر المبيد: إزالة يدوية للأوراق المصابة",
        "badge": create_badge("satellite_reading"),
        "confidence": top_detection["confidence"],
    }

    return {
        "detections": detections,
        "action_template": action_template,
    }
```

---

## <a name="troubleshooting"></a>🔧 استكشاف الأخطاء | Troubleshooting

### المشكلة 1: NATS غير متصل

```python
# التحقق
import nats

async def check_nats():
    try:
        nc = await nats.connect("nats://localhost:4222")
        await nc.close()
        return True
    except Exception as e:
        print(f"NATS connection failed: {e}")
        return False

# الحل
# 1. تأكد من تشغيل NATS: docker run -p 4222:4222 nats:latest
# 2. تحقق من NATS_URL في البيئة
# 3. تحقق من الشبكة بين الخدمات
```

### المشكلة 2: ActionTemplate غير صالح

```python
# التحقق
from pydantic import ValidationError

def validate_action_template(template: dict) -> bool:
    try:
        ActionTemplate(**template)
        return True
    except ValidationError as e:
        print(f"Invalid template: {e}")
        return False

# الحل
# تأكد من وجود جميع الحقول المطلوبة:
# - id, type, priority, field_id
# - what, why, when, how, fallback
```

### المشكلة 3: الخدمة الأصلية لا تستجيب

```python
# إضافة retry مع backoff
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
)
async def call_original_service(url: str, payload: dict):
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, timeout=30.0)
        response.raise_for_status()
        return response.json()
```

---

## 📞 الدعم | Support

للمساعدة أو الاستفسارات:

- راجع [FIELD_FIRST_ARCHITECTURE.md](../architecture/FIELD_FIRST_ARCHITECTURE.md)
- راجع [SERVICE_ACTIVATION_MAP.md](../architecture/SERVICE_ACTIVATION_MAP.md)
- افتح Issue في المستودع

---

**آخر تحديث | Last Updated:** 2024-01-20
**الإصدار | Version:** 15.5.0
