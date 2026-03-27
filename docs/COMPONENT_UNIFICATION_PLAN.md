# خطة توحيد المكونات — SAHOOL Unified Intelligence Layer
**Component Unification Plan**

> **الإصدار**: 1.0.0 | **التاريخ**: مارس 2026 | **الحالة**: جاهز للتنفيذ

---

## 1. المشكلة الحالية (Problem Statement)

المزارع الذي يريد سؤالاً زراعياً واحداً يواجه 6 خدمات متضاربة تعمل باستقلالية:

```
copilot-api       (8088)  → RAG + LLM multi-provider
advisory-service  (8093)  → أمراض + تسميد (قواعد ثابتة)
ai-advisor        (8112)  → استشارة ذكاء اصطناعي منفصلة
llm-orchestrator-service  (8164)  → يوجه للـ agents (CrewAI/NLP/Satellite)
ai-chat-assistant         (8260)  → يستدعي llm-orchestrator-service
whatsapp-bot-service      (8240)  → يكتشف النية ويوجه لـ llm-orchestrator-service
```

**النتيجة**: 5 خدمات تجيب على نفس السؤال بطرق مختلفة، بلا تجربة موحدة ولا حوكمة مركزية.

---

## 2. الهدف (Target Architecture)

```
المستخدم (ويب / واتساب / USSD / WeChat)
         ↓
┌─────────────────────────────────┐
│   Unified Query Gateway         │
│   copilot-api (8088) — ترقية   │
│   + IntentRouter                │
│   + ContextAggregator           │
│   + ChannelNormalizer           │
└─────────────┬───────────────────┘
              ↓  (توجيه ذكي حسب النية)
┌──────────────────────────────────────────────────────────────┐
│                     Expert Microservices                     │
│  pest-detection-service  yolo26-vision-service               │
│  irrigation-smart  advisory-service  weather-service         │
│  agro-rules  vegetation-analysis-service  marketplace-service│
└──────────────────────────────────────────────────────────────┘
              ↓
      استجابة موحدة الشكل (AR/EN)
```

**المبدأ الأساسي**: لا نحذف أي خدمة — نضيف طبقة توحيد فوقها.

---

## 3. المراحل الأربع

---

### المرحلة الأولى: توحيد بوابة الاستعلام (Unified Query Gateway)

**الهدف**: ترقية `copilot-api` ليكون نقطة الدخول الوحيدة.

#### 1.1 — `shared/ai/intent_classifier.py` (جديد)

نقل منطق تصنيف النية من `apps/services/whatsapp-bot-service/src/handlers/message_handler.py`
إلى مكتبة مشتركة تُستخدم من جميع نقاط الدخول.

```python
class AgriIntentClassifier:
    """
    Unified intent classification for all entry points.
    يُستخدم من: copilot-api, whatsapp-bot, ussd-gateway, wechat-service
    """
    INTENTS = [
        "crop_disease", "irrigation", "fertilizer", "pest_detection",
        "weather", "market_price", "policy_query", "ndvi_analysis",
        "general_advisory", "greeting", "help"
    ]

    async def classify(self, text: str, image: bytes | None = None) -> IntentResult:
        # 1. Arabic pattern matching (fast, offline)
        # 2. LLM classification (if patterns fail)
        # 3. Vision classification (if image provided)
```

**النوايا المدعومة وخدماتها**:

| النية | الخدمة المستهدفة | المنفذ |
|-------|-----------------|---------|
| `crop_disease` | pest-detection-service + yolo26-vision | 8125 / 8150 |
| `irrigation` | irrigation-smart + ml_irrigation | 8094 |
| `fertilizer` | advisory-service | 8093 |
| `pest_detection` | pest-detection-service | 8125 |
| `weather` | weather-service | 8092 |
| `market_price` | marketplace-service | 3010 |
| `policy_query` | agro-rules (NATS worker) | NATS (موضوع `agro-rules.policy_query`) |
| `ndvi_analysis` | vegetation-analysis-service | 8090 |
| `general_advisory` | copilot RAG pipeline | داخلي |

#### 1.2 — `apps/services/copilot-api/src/core/intent_router.py` (جديد)

```python
class IntentRouter:
    """
    Routes queries to appropriate expert services based on classified intent.
    يوجه الاستعلامات للخدمات المتخصصة بناءً على النية المكتشفة.
    """
    async def route(self, intent: IntentResult, query: str, context: dict) -> RouterResult:
        ...
```

#### 1.3 — تعديل `apps/services/copilot-api/src/api/v1/chat.py`

إضافة `IntentRouter` و`ContextAggregator` في pipeline المحادثة:

```
POST /api/v1/chat
  → IntentClassifier.classify(message)
  → IntentRouter.route(intent)
  → ContextAggregator.build_context(query, field_id)
  → LLM.generate(context)
  → UnifiedResponse(answer, answer_ar, intent, sources)
```

#### 1.4 — تعديل `apps/services/copilot-api/src/models/schemas.py`

إضافة حقول في `ChatResponse`:
- `intent: str` — النية المكتشفة
- `sources: list[Source]` — مصادر الإجابة
- `services_used: list[str]` — الخدمات التي استُعينت بها
- `confidence: float` — مستوى الثقة

---

### المرحلة الثانية: توحيد قنوات الوصول (Multi-Channel Adapter)

**الهدف**: جعل WhatsApp + USSD + WeChat + Web يصلون جميعاً لنفس `copilot-api`.

#### 2.1 — `shared/channel_adapter/` (جديد)

```
shared/channel_adapter/
├── __init__.py
├── models.py          # ChannelMessage, ChannelResponse
├── normalizer.py      # تحويل رسائل كل قناة لصيغة موحدة
└── channels/
    ├── whatsapp.py    # يستورد منطق message_handler الموجود
    ├── ussd.py        # يستورد منطق ussd-gateway الموجود
    ├── wechat.py      # يستورد منطق wechat-service الموجود
    └── web.py         # REST/WebSocket
```

**تدفق الرسائل الموحد**:
```
WhatsApp → normalizer → POST /api/v1/chat → copilot-api → WhatsApp formatter
USSD     → normalizer → POST /api/v1/chat → copilot-api → USSD formatter (140 chars)
WeChat   → normalizer → POST /api/v1/chat → copilot-api → WeChat formatter
```

#### 2.2 — تعديل `apps/services/whatsapp-bot-service/src/handlers/message_handler.py`

**قبل**: يُجري تصنيف النية ويوجه مباشرة لـ `llm-orchestrator`
**بعد**: يُرسّل الرسالة إلى `copilot-api` → يُنسّق الرد

```python
# بدلاً من:
response = await self._call_llm_orchestrator(message)

# يصبح:
from shared.channel_adapter.channels.whatsapp import WhatsAppNormalizer
channel_msg = WhatsAppNormalizer.normalize(message)
response = await CopilotClient.query(channel_msg)
formatted = WhatsAppFormatter.format(response)
```

#### 2.3 — تعديل `apps/services/ussd-gateway/src/main.py`

إضافة bridge داخلي يستدعي `copilot-api` ويُلخِّص الرد في 140 حرفاً (قيد USSD).

---

### المرحلة الثالثة: الشريحة المجانية (Free C-Tier)

**الهدف**: تفعيل الطبقة المجانية لجذب المزارعين غير المتصلين بالإنترنت.

#### 3.1 — تعديل `apps/services/billing-core/src/main.py`

تفعيل `SubscriptionPlan.free` (النوع موجود في `packages/shared-types/src/contracts/api-responses.ts`):

```python
FREE_TIER_LIMITS = {
    "daily_queries": 20,          # 20 سؤال زراعي يومياً
    "image_detection": 3,         # 3 صور كشف أمراض يومياً
    "weather_alerts": True,       # طقس مجاني دائماً
    "market_prices": True,        # أسعار السوق مجانية
    "field_count": 1,             # حقل واحد
    "advanced_ndvi": False,       # NDVI متقدم للمدفوعين فقط
    "ai_advisor_full": False,     # الاستشارة الكاملة للمدفوعين
}
```

**المبدأ**: الإجابة البسيطة مجانية، التحليل المتعمق مدفوع.

#### 3.2 — `apps/services/user-service/src/auth/quick-register.controller.ts` (جديد)

تسجيل مبسّط بدون بيانات كثيرة:

```
POST /api/v1/auth/quick-register
Body: { "phone": "+967XXXXXXXX", "channel": "whatsapp" | "ussd" | "web" }
Response: JWT صالح 30 يوماً، plan = "free" تلقائياً
```

#### 3.3 — تعديل `packages/shared-types/src/contracts/api-responses.ts`

إضافة `FreeTierLimits` type:

```typescript
export interface FreeTierLimits {
  dailyQueries: number;
  imageDetection: number;
  weatherAlerts: boolean;
  marketPrices: boolean;
  fieldCount: number;
  advancedNdvi: boolean;
  aiAdvisorFull: boolean;
}
```

---

### المرحلة الرابعة: الاستشارة الزراعية الموحدة (Unified Advisory)

**الهدف**: دمج `advisory-service` + `ai-advisor` + `copilot-api` في سياق واحد.

#### 4.1 — `apps/services/copilot-api/src/core/context_aggregator.py` (جديد)

```python
class AgriContextAggregator:
    """
    يجمع: RAG knowledge + expert rules + field sensor data + weather
    في سياق واحد يُغذَّى للـ LLM لإجابة شاملة.
    """
    async def build_context(
        self,
        query: str,
        field_id: str | None,
        tenant_id: str
    ) -> AggregatedContext:
        tasks = [
            self.rag.search(query),                    # ultraRAG
            self.advisory.get_rules(query),             # advisory-service (8093)
            self.field_data.get(field_id, tenant_id),  # field-management-service (3000)
            self.weather.get_current(field_id),         # weather-service (8092)
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return AggregatedContext.merge(results)
```

#### 4.2 — `apps/services/copilot-api/src/api/v1/encyclopedia.py` (جديد)

موسوعة زراعية مبنية على المعرفة الموجودة في:
- `shared/ai/knowledge/collections.py` — 13 مجموعة معرفية
- `shared/ai/ultrarag/workflows/` — 11 سير عمل زراعي
- `docs/knowledge-base/` — 91 مستند زراعي

```
GET /api/v1/encyclopedia/{crop_type}
GET /api/v1/encyclopedia/search?q={term}&lang=ar|en
```

#### 4.3 — `apps/services/copilot-api/src/api/v1/services_rec.py` (جديد)

توصية الخدمات الاجتماعية والمتخصصة:

```
POST /api/v1/services/recommend
Body: { "query": "أريد تمويلاً لشراء مضخة ري", "location": {...}, "field_id": "..." }

Response: {
  "equipment_rental": [...],  // drone-service + equipment-service
  "financing": [...],          // billing-core + crop-insurance
  "training": [...],           // skills-service + learning_marketplace
  "subsidies": [...]           // agro-rules (policy queries)
}
```

---

## 4. قائمة الملفات الكاملة

### ملفات جديدة

| الملف | الغرض | المرحلة |
|-------|--------|---------|
| `shared/ai/intent_classifier.py` | تصنيف النية الموحد | 1 |
| `shared/channel_adapter/__init__.py` | محوّل القنوات | 2 |
| `shared/channel_adapter/models.py` | نماذج الرسائل الموحدة | 2 |
| `shared/channel_adapter/normalizer.py` | تطبيع الرسائل | 2 |
| `shared/channel_adapter/channels/whatsapp.py` | محوّل واتساب | 2 |
| `shared/channel_adapter/channels/ussd.py` | محوّل USSD | 2 |
| `shared/channel_adapter/channels/wechat.py` | محوّل WeChat | 2 |
| `shared/channel_adapter/channels/web.py` | محوّل الويب | 2 |
| `apps/services/copilot-api/src/core/intent_router.py` | توجيه النية | 1 |
| `apps/services/copilot-api/src/core/context_aggregator.py` | تجميع السياق | 4 |
| `apps/services/copilot-api/src/api/v1/encyclopedia.py` | موسوعة زراعية | 4 |
| `apps/services/copilot-api/src/api/v1/services_rec.py` | توصية خدمات | 4 |
| `apps/services/user-service/src/auth/quick-register.controller.ts` | تسجيل سريع | 3 |

### ملفات مُعدَّلة

| الملف | التعديل | المرحلة |
|-------|--------|---------|
| `apps/services/copilot-api/src/api/v1/chat.py` | + IntentRouter + ContextAggregator | 1 |
| `apps/services/copilot-api/src/models/schemas.py` | + intent, sources, services_used | 1 |
| `apps/services/whatsapp-bot-service/src/handlers/message_handler.py` | → يستدعي copilot-api | 2 |
| `apps/services/ussd-gateway/src/main.py` | + copilot-api bridge | 2 |
| `apps/services/billing-core/src/main.py` | + FREE_TIER_LIMITS | 3 |
| `packages/shared-types/src/contracts/api-responses.ts` | + FreeTierLimits type | 3 |

---

## 5. أولويات التنفيذ

| الأولوية | المهمة | الأثر | الجهد التقديري |
|---------|--------|-------|---------------|
| **P0** | `IntentClassifier` في `shared/ai/` | أساس كل شيء | 1 يوم |
| **P0** | ترقية `copilot-api` كبوابة موحدة | فوري | 2 أيام |
| **P1** | `Free tier` في `billing-core` | جذب مزارعين C | 1 يوم |
| **P1** | `whatsapp-bot` → `copilot-api` | قناة رئيسية للـ C tier | 1 يوم |
| **P2** | `ContextAggregator` (advisory + RAG) | جودة الإجابة | 2 أيام |
| **P2** | Encyclopedia endpoint | موسوعة §2.6 | 1 يوم |
| **P3** | `ussd-gateway` → `copilot-api` | Basic phones | 1 يوم |
| **P3** | Services Recommender | خدمات اجتماعية | 1 يوم |
| **P3** | Quick Register | تسجيل مبسط | 0.5 يوم |

**المجموع التقديري**: ~10.5 يوم عمل للتوحيد الكامل.

---

## 6. اعتبارات التنفيذ

### التوافق مع الكود الحالي
- جميع الخدمات الموجودة تبقى تعمل بدون تغيير
- `copilot-api` يضيف طبقة فوق الخدمات، لا يستبدلها
- التعديلات على `whatsapp-bot` و`ussd-gateway` اختيارية في المرحلة الأولى

### الأمان
- جميع الطلبات تمر عبر JWT auth (`shared.auth.dependencies.get_current_user`)
- `tenant_id` مطلوب في كل استعلام (متوافق مع `EventPublisher.publish_event`)
- حدود الطبقة المجانية تُطبَّق في `billing-core` قبل وصول الطلب للـ LLM

### الأداء
- `IntentClassifier` يعمل offline بالأنماط العربية أولاً (< 1ms)
- `ContextAggregator` يستخدم `asyncio.gather` لتوازي استدعاء الخدمات
- Redis cache للنوايا المتكررة (TTL: 5 دقائق)

### الاختبار
- وحدة اختبار لكل intent في `tests/unit/test_intent_classifier.py`
- اختبار تكامل في `tests/integration/test_copilot_gateway.py`
- Pytest markers: `@pytest.mark.unit` و`@pytest.mark.integration`

---

## 7. خريطة التبعيات

```
shared/ai/intent_classifier.py
    ↑ يستخدمه
apps/services/copilot-api/src/core/intent_router.py
    ↑ يستخدمه
apps/services/copilot-api/src/api/v1/chat.py
    ↑ يغذّيه
shared/channel_adapter/normalizer.py
    ↑ يستخدمه
apps/services/whatsapp-bot-service/
apps/services/ussd-gateway/
apps/services/wechat-service/
```

---

*آخر تحديث: مارس 2026 | المؤلف: KAFAAT Platform Team*
