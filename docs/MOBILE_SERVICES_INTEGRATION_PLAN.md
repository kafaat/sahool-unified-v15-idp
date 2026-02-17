# خطة ربط الخدمات بتطبيق الهاتف - SAHOOL Mobile Services Integration Plan

**التاريخ**: 2026-02-16
**الإصدار**: 16.0.0
**المراجع**: Deep Service Audit + Mobile App Feature Review

---

## ملخص تنفيذي | Executive Summary

بناءً على المراجعة العميقة لـ **72 خدمة خلفية** و **57 وحدة ميزة** في تطبيق Flutter، تم تصنيف الخدمات إلى:

| التصنيف | العدد | النسبة |
|---------|-------|--------|
| خدمات واجهة (Frontend-Facing) | 32 | 44% |
| خدمات خلفية (Backend-Only) | 40 | 56% |

**الحالة الحالية**: 19 خدمة مربوطة من أصل 32 خدمة واجهة (59%)
**المطلوب**: ربط 13 خدمة إضافية + إنشاء 5 شاشات جديدة

---

## الجزء الأول: تقييم اكتمال الخدمات الشامل

### 1.1 خدمات أساسية (Core)

| الخدمة | المنفذ | النوع | الاكتمال | DB | NATS | Auth | الحالة |
|--------|--------|-------|----------|----|----|------|--------|
| field-management-service | 3000 | Node+Python | 3/5 | ✅ PostGIS | ✅ | ✅ JWT | هجين (منفذان) |
| user-service | 3025 | NestJS | 4/5 | ✅ Prisma | ❌ | ✅ JWT+bcrypt | جاهزة للإنتاج |
| notification-service | 8110 | FastAPI | 4/5 | ✅ Tortoise | ✅ | ✅ | FCM+SMS+Email+WhatsApp |
| billing-core | 8089 | FastAPI | 4/5 | ✅ SQLAlchemy | ✅ JetStream | ✅ | Stripe+Tharwatt webhooks |
| task-service | 8103 | FastAPI | 3.5/5 | ✅ | ~ | ✅ | بعض pass stubs |
| equipment-service | 8101 | FastAPI | 4/5 | ✅ SQLAlchemy | ❌ | ✅ | GPS+QR+telemetry |
| alert-service | 8113 | FastAPI | 4/5 | ✅ SQLAlchemy | ✅ | ✅ | NDVI+Weather+IoT events |
| provider-config | 8104 | FastAPI | 4/5 | ✅ | ✅ | ✅ | failover chain |
| audit-service | 8114 | FastAPI | 4/5 | ✅ | ✅ | ✅ | hash chain integrity |
| inventory-service | 8116 | FastAPI | 4/5 | ✅ async | ✅ | ✅ | stock+warehouse |
| ws-gateway | 8081 | FastAPI | 4/5 | ❌ | ✅ bridge | ✅ JWT | WebSocket rooms |

### 1.2 خدمات الذكاء والتحليل (Intelligence)

| الخدمة | المنفذ | النوع | الاكتمال | DB | NATS | النماذج/الخوارزميات |
|--------|--------|-------|----------|----|----|---------------------|
| vegetation-analysis-service | 8090 | FastAPI | 4/5 | ✅ | ✅ | Sentinel-2, NDVI/EVI/NDRE/SAVI |
| crop-intelligence-service | 8095 | FastAPI | 4/5 | ✅ | ✅ | Disease AI, DSSAT/AquaCrop/WOFOST |
| indicators-service | 8091 | FastAPI | 4/5 | ✅ | ✅ | Vegetation+Performance indices |
| field-intelligence | 8120 | FastAPI | 3/5 | ✅ | ~ | Zone analytics |
| lai-estimation | 3022 | NestJS | 3/5 | ✅ | ✅ | Leaf Area Index |
| skills-service | 8121 | FastAPI | 3/5 | ✅ | ~ | Farmer skill assessment |
| soil-analysis-service | 8134 | FastAPI | 3/5 | ~ | ✅ | NPK analysis |
| pest-detection-service | 8125 | FastAPI | 3/5 | ~ | ✅ | IPM + threshold control |
| digital-twin-engine | 8253 | FastAPI | 3/5 | ~ | ✅ | Field simulation |
| yield-prediction-service | 8152 | NestJS | 4/5 | ✅ Prisma | ✅ | RF, XGBoost, LSTM, Ensemble |
| advisory-service | 8093 | FastAPI | 4/5 | ✅ | ✅ | Rule-based + scientific |
| irrigation-smart | 8094 | FastAPI | 4/5 | ✅ | ✅ | ET₀, scheduling |
| crop-growth-model | 3023 | NestJS | 3/5 | ✅ | ✅ | DSSAT, AquaCrop |
| agro-rules | 8151 | FastAPI | 3/5 | ✅ | ✅ | Rule engine |

### 1.3 خدمات الرؤية والتضاريس (Vision/Terrain)

| الخدمة | المنفذ | النوع | الاكتمال | DB | NATS | التقنية |
|--------|--------|-------|----------|----|----|---------|
| yolo26-vision-service | 8150 | FastAPI | 4/5 | ✅ | ✅ | YOLO26 (22 آفة, 34 مرض, 12 عشب) |
| ground-vision-service | 8182 | FastAPI | 3/5 | ✅ | ✅ | Tower cameras + anomaly detection |
| terrain-core-service | 8185 | FastAPI | 4/5 | ✅ | ✅ | DEM, slope, aspect |
| hydrology-service | 8165 | FastAPI | 4/5 | ✅ | ✅ | Drainage, watershed |
| leveling-optimizer-service | 8170 | FastAPI | 4/5 | ✅ | ✅ | Cut/fill optimization |
| edge-orchestrator-service | 8180 | FastAPI | 4/5 | ✅ Redis | ✅ | Jetson Orin management |

### 1.4 خدمات IoT والطقس

| الخدمة | المنفذ | النوع | الاكتمال | DB | NATS | الدور |
|--------|--------|-------|----------|----|----|-------|
| iot-service | 8117 | NestJS | 4/5 | ✅ | ✅ | Device CRUD |
| iot-gateway | 8106 | FastAPI | 4/5 | ❌ | ✅ | MQTT→NATS bridge |
| iot-sensor-hub | 8251 | FastAPI | 4/5 | ✅ | ✅ | LoRaWAN fusion, Kalman |
| virtual-sensors | 8119 | FastAPI | 3/5 | ~ | ✅ | Computed indices |
| weather-service | 8092 | FastAPI | 4/5 | ✅ | ✅ | Multi-provider weather |
| astronomical-calendar | 8111 | FastAPI | 3/5 | ~ | ~ | Islamic calendar |
| drone-service | 8126 | FastAPI | 2/5 | ❌ | ~ | Skeleton |

### 1.5 خدمات الأعمال والمجتمع (Business)

| الخدمة | المنفذ | النوع | الاكتمال | DB | NATS | الميزات الرئيسية |
|--------|--------|-------|----------|----|----|-----------------|
| marketplace-service | 3010 | NestJS | **5/5** | ✅ Prisma | ✅ | Fintech كامل (محفظة, قروض, ضمان) |
| chat-service | 8000 | NestJS | 4/5 | ✅ Prisma | Socket.IO | Real-time buyer-seller |
| research-core | 3015 | NestJS | 3/5 | ✅ | ~ | ANOVA, LSD statistics |
| disaster-assessment | 3020 | NestJS | 4/5 | ✅ | ✅ | 6 أنواع كوارث |
| cooperative-service | 8127 | FastAPI | 4/5 | ✅ | ✅ | 6 طرق توزيع أرباح |
| crm-service | 8131 | FastAPI | 4/5 | ✅ | ✅ | 7 مراحل صفقة الحصاد |
| logistics-service | 8167 | FastAPI | 4/5 | ✅ | ✅ | تحسين المسارات |
| supply-chain-service | 8230 | FastAPI | 3/5 | ~ | ✅ | شراء تلقائي |
| traceability-service | 8123 | FastAPI | 3/5 | ~ | ✅ | QR + blockchain |
| globalgap-compliance | 8128 | FastAPI | 3/5 | Memory | ✅ | IFA v6 |

### 1.6 خدمات AI والوكلاء

| الخدمة | المنفذ | النوع | الاكتمال | DB | NATS | الدور |
|--------|--------|-------|----------|----|----|-------|
| copilot-api | 8088 | FastAPI | **4/5** | ✅ | ✅ | Multi-LLM RAG (Ollama, Claude, OpenAI) |
| ai-advisor | 8112 | FastAPI | 3/5 | ~ | ✅ | Multi-agent advisory |
| agent-registry | 8160 | FastAPI | 4/5 | ✅ Redis | ✅ | A2A Protocol |
| ai-agents-core | 8161 | FastAPI | 3/5 | ~ | ~ | 5 agents (Master, Mobile, IoT, Drone, Feedback) |
| ai-agents-service | 8130 | FastAPI | 2/5 | ❌ | ❌ | Stub |
| ai-chat-assistant | 8260 | FastAPI | 2/5 | ❌ | ❌ | Early impl |
| knowledge-graph | 8140 | FastAPI | 3/5 | Memory | ~ | NetworkX (10 relationship types) |
| llm-orchestrator-service | 8164 | FastAPI | 3/5 | ✅ Redis | ~ | 11 agricultural intents |
| mcp-server | 8200 | FastAPI | 3/5 | ❌ | ~ | MCP JSON-RPC |

### 1.7 خدمات الري المتخصصة

| الخدمة | المنفذ | النوع | الاكتمال | الميزات |
|--------|--------|-------|----------|---------|
| irrigation-cycle-engine | 8250 | FastAPI | **4/5** | FAO-56 Penman-Monteith, 25-param AutoIrrigate, Yemen crops |
| fertigation-engine | 8252 | FastAPI | **4/5** | NPK by stage, WOFOST, 7 growth phases, 12 fertilizer types |

### 1.8 خدمات أخرى

| الخدمة | المنفذ | النوع | الاكتمال | ملاحظات |
|--------|--------|-------|----------|---------|
| code-review-service | 8102 | FastAPI | 2/5 | Stub - مطورين فقط |
| code-review-agent | 8145 | NestJS | 2/5 | Skeleton - مطورين فقط |
| code-fix-agent | 8162 | FastAPI | 2/5 | Skeleton - مطورين فقط |
| lowcode-engine | 8132 | FastAPI | 3/5 | Admin portal only |
| demo-data | 8261 | FastAPI | 2/5 | Development only |
| whatsapp-bot-service | 8240 | FastAPI | 3/5 | قناة بديلة |
| ussd-gateway | 8183 | FastAPI | 3/5 | هواتف بسيطة |
| wechat-service | 8133 | FastAPI | 3/5 | سوق صيني |
| community-chat | 8097 | FastAPI | 2/5 | **DEPRECATED** → chat-service |
| field-chat | 8099 | FastAPI | 2/5 | Stub |

---

## الجزء الثاني: تقييم تطبيق الهاتف

### 2.1 البنية التحتية للتطبيق

| المكون | الحالة | التقييم |
|--------|--------|---------|
| Kong Gateway Client | ✅ كامل | 26 خدمة، circuit breaker، retry، ETag |
| Drift Database (SQLCipher) | ✅ كامل | تشفير 256-bit AES |
| Outbox Sync Engine | ✅ كامل | 4-layer events، background sync |
| Certificate Pinning | ✅ كامل | SHA256 + public key |
| Device Integrity | ✅ كامل | Root detection، screenshot prevention |
| Riverpod State | ✅ كامل | 40+ providers |
| Arabic RTL Support | ✅ كامل | ثنائي اللغة |

### 2.2 تقييم وحدات الميزات (57 وحدة)

#### الطبقة 1: كاملة ومتصلة بالخلفية (22 وحدة) ✅

| الوحدة | الملفات | LOC | الخدمة المتصلة |
|--------|---------|-----|---------------|
| field/ | 14 | 3,500+ | field-management-service |
| weather/ | 15 | 4,200+ | weather-service |
| tasks/ | 16 | 5,200+ | task-service |
| crop_health/ | 21 | 6,000+ | crop-intelligence + vegetation |
| irrigation/ | 7 | 2,800+ | irrigation-smart |
| satellite/ | 17 | 5,500+ | vegetation-analysis |
| equipment/ | 6 | 3,000+ | equipment-service |
| notifications/ | 8 | 2,400+ | notification-service |
| inventory/ | 13 | 3,900+ | inventory-service |
| chat/ | 11 | 3,600+ | chat-service |
| community/ | 5 | 1,500+ | community-chat |
| advisor/ | 7 | 2,200+ | advisory-service |
| ndvi/ | 5 | 1,800+ | ndvi-processor |
| marketplace/ | 2 | 800+ | marketplace-service |
| rotation/ | 11 | 4,735 | advisory-service |
| profitability/ | 8 | 4,101 | field-management |
| gdd/ | 9 | 2,900+ | weather-service |
| spray/ | 10 | 3,000+ | task-service |
| virtual_sensors/ | 4 | 1,200+ | virtual-sensors |
| vision/ | 5 | 2,685 | yolo26-vision (image upload) |
| vra/ | 8 | 3,608 | irrigation-smart |
| research/ | 3 | 950+ | research-core |

#### الطبقة 2: موجودة لكن بدون ربط حقيقي (12 وحدة) ⚠️

| الوحدة | الملفات | المشكلة | الخدمة المطلوبة |
|--------|---------|---------|----------------|
| alerts/ | 1 | **بيانات وهمية مشفرة** | alert-service (8113) |
| ai_advisor/ | 1 | API محدود بدون RAG | copilot-api (8088) |
| daily_brief/ | 2 | بدون أي API | copilot-api (8088) |
| analytics/ | 11 | بيانات محلية فقط | field-intelligence (8120) |
| lab/ | 1 | شاشة فارغة | soil-analysis-service (8134) |
| pivot_irrigation/ | 10 | UI بدون حسابات خلفية | irrigation-cycle-engine (8250) |
| scanner/ | 1 | محاكاة 3 ثوانٍ | traceability-service (8123) |
| scouting/ | 1 | هيكل فقط | pest-detection-service (8125) |
| gamification/ | 1 | هيكل فقط | skills-service (8121) |
| astronomical_calendar/ | 3 | UI جزئي | astronomical-calendar (8111) |
| field_hub/ | 1 | هيكل فقط | field-intelligence (8120) |
| terrain/ | 2 | جزئي | terrain-core-service (8185) |

#### الطبقة 3: كاملة ذاتياً بدون خدمة خلفية (10 وحدات) ✅

| الوحدة | الملفات | ملاحظة |
|--------|---------|--------|
| auth/ | 11 | JWT + 2FA + biometric |
| home/ + home_v16/ | 14 | Dashboard aggregation |
| billing/ + payment/ + wallet/ | 9 | billing-core connection |
| profile/ | 2 | user-service connection |
| settings/ | 1 | local preferences |
| onboarding/ | 1 | local flow |
| splash/ | 1 | startup |
| main_layout/ | 2 | navigation |
| sync/ | 3 | outbox engine |
| shared/ | varies | reusable components |

#### الطبقة 4: وحدات تحتاج إنشاء جديد (5 وحدات مقترحة)

| الوحدة المقترحة | الخدمة | الأولوية | السبب |
|----------------|--------|---------|-------|
| cooperative/ | cooperative-service (8127) | عالية | إدارة التعاونيات الزراعية |
| logistics/ | logistics-service (8167) | متوسطة | تتبع النقل والتخزين |
| disaster/ | disaster-assessment (3020) | متوسطة | تقييم الأضرار والتعويضات |
| compliance/ | globalgap-compliance (8128) | منخفضة | شهادات GlobalGAP |
| crm/ | crm-service (8131) | منخفضة | صفقات الحصاد والتسويق |

---

## الجزء الثالث: تصنيف الخدمات (واجهة vs خلفية)

### 3.1 خدمات الواجهة (Frontend-Facing) - 32 خدمة

هذه الخدمات يستدعيها تطبيق الهاتف مباشرة عبر Kong Gateway.

#### مربوطة حالياً (19 خدمة) ✅

```
field-management-service (3000)  │  user-service (3025)
weather-service (8092)           │  vegetation-analysis-service (8090)
crop-intelligence-service (8095) │  irrigation-smart (8094)
advisory-service (8093)          │  task-service (8103)
equipment-service (8101)         │  alert-service (8113)
notification-service (8110)      │  marketplace-service (3010)
billing-core (8089)              │  inventory-service (8116)
chat-service (8000)              │  iot-service (8117)
virtual-sensors (8119)           │  indicators-service (8091)
research-core (3015)
```

#### يجب ربطها (13 خدمة) ⚠️

**أولوية 1 - ربط فوري (لها شاشات جاهزة):**

| # | الخدمة | المنفذ | شاشة Flutter | التعديل المطلوب |
|---|--------|--------|-------------|----------------|
| 1 | copilot-api | 8088 | ai_advisor/, daily_brief/ | إضافة KongService + تحديث AiAdvisorRepository |
| 2 | pest-detection-service | 8125 | vision/, scouting/ | إضافة cloud fallback بعد TFLite |
| 3 | soil-analysis-service | 8134 | lab/ | تطوير شاشة sample_tracking |
| 4 | irrigation-cycle-engine | 8250 | pivot_irrigation/ | ربط حسابات FAO-56 |
| 5 | field-intelligence | 8120 | analytics/, field_hub/ | استبدال البيانات المحلية |
| 6 | astronomical-calendar | 8111 | astronomical_calendar/ | ربط بيانات التقويم |

**أولوية 2 - ربط مع تحسين الشاشات:**

| # | الخدمة | المنفذ | شاشة Flutter | التعديل المطلوب |
|---|--------|--------|-------------|----------------|
| 7 | skills-service | 8121 | gamification/ | تطوير نظام النقاط والشارات |
| 8 | disaster-assessment | 3020 | -- (جديدة) | إنشاء شاشة تقييم الأضرار |
| 9 | terrain-core-service | 8185 | terrain/ | تطوير واجهة تحليل التضاريس |

**أولوية 3 - شاشات جديدة بالكامل:**

| # | الخدمة | المنفذ | شاشة Flutter | التعديل المطلوب |
|---|--------|--------|-------------|----------------|
| 10 | cooperative-service | 8127 | -- (جديدة) | إنشاء وحدة cooperative/ |
| 11 | crm-service | 8131 | -- (جديدة) | إنشاء وحدة crm/ |
| 12 | logistics-service | 8167 | -- (جديدة) | إنشاء وحدة logistics/ |
| 13 | traceability-service | 8123 | scanner/ | تطوير QR code scanning |

### 3.2 خدمات الخلفية (Backend-Only) - 40 خدمة

هذه الخدمات لا يستدعيها التطبيق مباشرة - تعمل وراء الكواليس.

#### A. بنية تحتية (7 خدمات)

| الخدمة | المنفذ | الدور | كيف تُستخدم |
|--------|--------|-------|-------------|
| ws-gateway | 8081 | بوابة WebSocket | التطبيق يتصل عبر socket ضمنياً |
| provider-config | 8104 | تبديل المزودين | يعمل تلقائياً عند تعطل مزود |
| audit-service | 8114 | تدقيق | يسجل كل العمليات بصمت |
| iot-gateway | 8106 | جسر MQTT→NATS | يحول بروتوكولات IoT |
| edge-orchestrator-service | 8180 | إدارة Jetson | DevOps فقط |
| mcp-server | 8200 | سياق النماذج | داخلي بالكامل |
| demo-data | 8261 | بيانات تجريبية | تطوير فقط |

#### B. محركات حسابية (11 خدمة)

| الخدمة | المنفذ | تخدم من؟ | الدور |
|--------|--------|----------|-------|
| ndvi-processor | 8118 | vegetation-analysis | معالجة NDVI (مهملة) |
| lai-estimation | 3022 | vegetation-analysis | تقدير مساحة الورقة |
| crop-growth-model | 3023 | crop-intelligence | محاكاة DSSAT/AquaCrop |
| agro-rules | 8151 | advisory-service | محرك القواعد |
| yield-prediction-service | 8152 | indicators | ML predictions |
| yield-engine | 8098 | -- | مهملة |
| fertigation-engine | 8252 | irrigation-smart | NPK + WOFOST |
| digital-twin-engine | 8253 | field-intelligence | محاكاة رقمية |
| hydrology-service | 8165 | terrain-core | تحليل الصرف |
| leveling-optimizer-service | 8170 | terrain-core | تسوية الحقول |
| supply-chain-service | 8230 | logistics | سلسلة التوريد |

#### C. ذكاء اصطناعي (9 خدمات)

| الخدمة | المنفذ | تخدم من؟ | الدور |
|--------|--------|----------|-------|
| yolo26-vision-service | 8150 | pest-detection, copilot | استدلال YOLO26 |
| ground-vision-service | 8182 | alert-service | كاميرات الأبراج |
| agent-registry | 8160 | ai-agents-core | سجل الوكلاء A2A |
| ai-agents-core | 8161 | copilot-api | إطار الوكلاء |
| ai-agents-service | 8130 | copilot-api | تنظيم الوكلاء |
| llm-orchestrator-service | 8164 | copilot-api | توجيه النية |
| knowledge-graph | 8140 | advisory, copilot | رسم المعرفة |
| iot-sensor-hub | 8251 | iot-service | دمج المستشعرات |
| ai-advisor | 8112 | copilot-api | استشارات AI |

#### D. خدمات مطورين (4 خدمات)

| الخدمة | المنفذ | الدور |
|--------|--------|-------|
| code-review-service | 8102 | مراجعة الكود |
| code-review-agent | 8145 | وكيل مراجعة |
| code-fix-agent | 8162 | إصلاح تلقائي |
| lowcode-engine | 8132 | Admin portal فقط |

#### E. قنوات بديلة (3 خدمات)

| الخدمة | المنفذ | الدور |
|--------|--------|-------|
| whatsapp-bot-service | 8240 | بوت واتساب |
| ussd-gateway | 8183 | هواتف بسيطة |
| wechat-service | 8133 | سوق صيني |

#### F. مهملة (4 خدمات) - يجب أرشفتها

| الخدمة | المنفذ | البديل |
|--------|--------|--------|
| community-chat | 8097 | → chat-service |
| yield-engine | 8098 | → yield-prediction-service |
| ndvi-processor | 8118 | → vegetation-analysis-service |
| field-chat | 8099 | → chat-service |

#### G. AI داعمة (2 خدمة)

| الخدمة | المنفذ | الدور |
|--------|--------|-------|
| ai-chat-assistant | 8260 | يُدمج مع copilot-api |
| globalgap-compliance | 8128 | يُدمج مع compliance screen |

---

## الجزء الرابع: خطة التنفيذ المقترحة

### المرحلة 1: إصلاحات فورية (أسبوع 1-2)

#### 1.1 ربط alert-service بشاشة الإنذارات

**المشكلة**: شاشة `alerts/alerts_screen.dart` تستخدم بيانات وهمية مشفرة يدوياً
**الحل**: ربط مع alert-service (8113) الذي لديه 10+ endpoints جاهزة

```dart
// الإضافة في kong_gateway_client.dart
static const alertsBackend = KongService(
  name: 'alert-service',
  nameAr: 'خدمة التنبيهات',
  basePath: '/api/v1/alerts',
);
```

**الملفات المتأثرة**:
- `lib/core/api/kong_gateway_client.dart` - إضافة KongService
- `lib/features/alerts/alerts_screen.dart` - استبدال البيانات الوهمية
- إنشاء `lib/features/alerts/data/alerts_repository.dart`
- إنشاء `lib/features/alerts/providers/alerts_provider.dart`

#### 1.2 ربط copilot-api بالمساعد الذكي

**المشكلة**: ai_advisor يستخدم API محدود بدون RAG
**الحل**: ربط مع copilot-api (8088) الذي يدعم Multi-LLM + RAG

```dart
static const copilot = KongService(
  name: 'copilot-api',
  nameAr: 'المساعد الذكي',
  basePath: '/api/v1/copilot',
  timeout: Duration(seconds: 120), // AI operations need longer timeout
);
```

#### 1.3 أرشفة 4 خدمات مهملة

```bash
# نقل إلى archive/
mv apps/services/community-chat archive/deprecated-services/
mv apps/services/yield-engine archive/deprecated-services/
mv apps/services/ndvi-processor archive/deprecated-services/
mv apps/services/field-chat archive/deprecated-services/
```

### المرحلة 2: ربط الخدمات الجاهزة (أسبوع 3-4)

#### 2.1 pest-detection-service → vision/ + scouting/

**الوضع الحالي**: التطبيق يستخدم TFLite محلي فقط
**الحل**: إضافة cloud fallback عند فشل النموذج المحلي

```dart
// في detection_screen.dart
Future<DetectionResult> detect(File image) async {
  try {
    // 1. محاولة محلية أولاً (offline-first)
    return await _localTFLiteDetect(image);
  } catch (e) {
    // 2. Cloud fallback عبر pest-detection-service
    return await _cloudDetect(image);
  }
}
```

#### 2.2 soil-analysis-service → lab/

**الملفات الجديدة**:
- `lib/features/lab/data/soil_repository.dart`
- `lib/features/lab/providers/soil_provider.dart`
- `lib/features/lab/screens/soil_analysis_screen.dart`
- `lib/features/lab/screens/sample_submission_screen.dart`
- `lib/features/lab/widgets/npk_chart_widget.dart`

#### 2.3 irrigation-cycle-engine → pivot_irrigation/

**المشكلة**: 10 ملفات UI جاهزة بدون حسابات FAO-56
**الحل**: ربط مع irrigation-cycle-engine (8250) الذي يوفر:
- ET₀ (Penman-Monteith)
- AutoIrrigate (25 معامل)
- Salinity-adjusted Kc
- قاعدة بيانات المحاصيل اليمنية

#### 2.4 field-intelligence → analytics/

**الحل**: استبدال البيانات المحلية ببيانات حقيقية من field-intelligence
- Zone analytics
- Performance metrics
- Historical trends

### المرحلة 3: شاشات جديدة (أسبوع 5-8)

#### 3.1 وحدة cooperative/ (جديدة)

**الخدمة**: cooperative-service (8127) - اكتمال 4/5
**الشاشات المطلوبة**:

```
lib/features/cooperative/
├── screens/
│   ├── cooperative_list_screen.dart      # قائمة التعاونيات
│   ├── cooperative_detail_screen.dart    # تفاصيل التعاونية
│   ├── member_management_screen.dart     # إدارة الأعضاء
│   ├── resource_pool_screen.dart         # تجمع الموارد
│   └── revenue_distribution_screen.dart  # توزيع الأرباح
├── data/
│   └── cooperative_repository.dart
├── providers/
│   └── cooperative_provider.dart
├── models/
│   └── cooperative_models.dart
└── widgets/
    ├── revenue_chart.dart
    └── member_card.dart
```

**الميزات**: 6 طرق توزيع أرباح (متساوي، حسب المساهمة، حسب الإنتاج، حسب المساحة، مرجّح، هجين)

#### 3.2 وحدة disaster/ (جديدة)

**الخدمة**: disaster-assessment (3020) - اكتمال 4/5
**الشاشات المطلوبة**:

```
lib/features/disaster/
├── screens/
│   ├── disaster_report_screen.dart    # إبلاغ عن كارثة
│   ├── damage_assessment_screen.dart  # تقييم الأضرار
│   ├── claim_screen.dart              # طلب تعويض
│   └── disaster_history_screen.dart   # سجل الكوارث
├── data/
│   └── disaster_repository.dart
├── providers/
│   └── disaster_provider.dart
└── models/
    └── disaster_models.dart           # 6 أنواع: فيضان، جفاف، صقيع، حرارة، رياح، آفات
```

#### 3.3 وحدة logistics/ (جديدة)

**الخدمة**: logistics-service (8167) - اكتمال 4/5
**الشاشات المطلوبة**:

```
lib/features/logistics/
├── screens/
│   ├── fleet_screen.dart               # إدارة الأسطول
│   ├── storage_screen.dart             # مرافق التخزين
│   ├── harvest_collection_screen.dart  # جمع الحصاد
│   └── shipment_tracking_screen.dart   # تتبع الشحنات
├── data/
│   └── logistics_repository.dart
├── providers/
│   └── logistics_provider.dart
└── widgets/
    ├── route_map.dart                  # خريطة المسار المحسن
    └── storage_conditions.dart         # حرارة/رطوبة
```

#### 3.4 تطوير scanner/ (QR Traceability)

**الخدمة**: traceability-service (8123)
**التطوير المطلوب**:
- استبدال المحاكاة بـ `mobile_scanner` package
- ربط مع QR code endpoints
- عرض رحلة المنتج من المزرعة للمستهلك

### المرحلة 4: تحسينات متقدمة (أسبوع 9-12)

#### 4.1 Terrain Visualization

ربط terrain-core-service مع شاشة terrain/ لعرض:
- DEM 3D visualization
- Slope & aspect maps
- Hydrology drainage patterns
- Cut/fill optimization results

#### 4.2 Gamification System

تطوير شاشة gamification/ مع skills-service:
- نظام النقاط والشارات
- تحديات زراعية أسبوعية
- لوحة المتصدرين
- مسار التعلم

#### 4.3 GlobalGAP Compliance

إنشاء شاشة compliance/ مع globalgap-compliance:
- قوائم فحص IFA v6
- تتبع عدم المطابقة
- إدارة الشهادات
- جدولة التدقيق

---

## الجزء الخامس: أفضل الممارسات المتبعة

### 5.1 نمط Offline-First (مطبق)

```
المستخدم → Drift DB (محلي) → Outbox → Kong Gateway → الخدمة
                ↑                                        ↓
                └──────── Background Sync ←──────────────┘
```

**القاعدة**: كل خدمة واجهة يجب أن تدعم:
1. قراءة من Drift cache أولاً
2. تحديث في الخلفية عند توفر الاتصال
3. حفظ التغييرات في Outbox عند عدم الاتصال
4. مزامنة تلقائية عبر Workmanager

### 5.2 نمط BFF (Backend-for-Frontend)

**المبدأ**: التطبيق يستدعي خدمة واجهة واحدة → الخدمة تستدعي خدمات خلفية متعددة

```
📱 صحة الحقل → crop-intelligence (واجهة)
                  ├→ vegetation-analysis (خلفية)
                  ├→ weather-service (خلفية عبر NATS)
                  ├→ yolo26-vision (خلفية عند رفع صورة)
                  └→ knowledge-graph (خلفية للتوصيات)
```

### 5.3 نمط Circuit Breaker (مطبق)

```dart
// KongGatewayClient يطبق:
// - 3 فشلات → فتح الدارة لمدة 30 ثانية
// - Retry مع exponential backoff
// - Rate limit tracking
// - Health monitoring
```

### 5.4 نمط أمان الهاتف (مطبق)

| الطبقة | التقنية | الحالة |
|--------|---------|--------|
| التخزين | SQLCipher 256-bit AES | ✅ |
| النقل | TLS + Certificate Pinning | ✅ |
| المصادقة | JWT + Biometric + 2FA | ✅ |
| الجهاز | Root detection + Screenshot prevention | ✅ |
| التوقيع | HMAC request signing | ✅ |

### 5.5 نمط Kong Service Registration

عند إضافة خدمة جديدة للتطبيق:

```dart
// 1. إضافة في KongServices class
static const newService = KongService(
  name: 'service-name',
  nameAr: 'اسم الخدمة',
  basePath: '/api/v1/endpoint',
  timeout: Duration(seconds: 30),
  maxRetries: 3,
);

// 2. إضافة في all list
static List<KongService> get all => [
  ...existing,
  newService,
];

// 3. إنشاء Repository
class NewServiceRepository {
  final KongGatewayClient _client;

  Future<List<Item>> getItems() async {
    final response = await _client.get(
      KongServices.newService,
      '/items',
    );
    return (response.data as List)
        .map((e) => Item.fromJson(e))
        .toList();
  }
}

// 4. إنشاء Riverpod Provider
@riverpod
Future<List<Item>> items(ItemsRef ref) async {
  final repo = ref.watch(newServiceRepositoryProvider);
  return repo.getItems();
}

// 5. إضافة Drift table للتخزين المحلي
class NewServiceItems extends Table {
  TextColumn get id => text()();
  TextColumn get data => text()();
  DateTimeColumn get syncedAt => dateTime().nullable()();
}
```

---

## الجزء السادس: ملخص الإحصائيات

### إحصائيات الخدمات

| المقياس | القيمة |
|---------|--------|
| إجمالي الخدمات | 72 |
| خدمات واجهة | 32 (44%) |
| خدمات خلفية | 40 (56%) |
| مربوطة حالياً | 19/32 (59%) |
| تحتاج ربط | 13/32 (41%) |
| اكتمال 4-5/5 | 38 خدمة (53%) |
| اكتمال 3/5 | 22 خدمة (31%) |
| اكتمال 1-2/5 | 12 خدمة (16%) |
| مهملة | 4 خدمات |

### إحصائيات التطبيق

| المقياس | القيمة |
|---------|--------|
| إجمالي الملفات | 488 ملف Dart |
| إجمالي الأكواد | 240,401 سطر |
| وحدات الميزات | 57 وحدة |
| كاملة ومتصلة | 22 وحدة (39%) |
| جزئية/بدون ربط | 12 وحدة (21%) |
| كاملة ذاتياً | 10 وحدات (17%) |
| تحتاج إنشاء | 5 وحدات (9%) |
| هيكلية فقط | 8 وحدات (14%) |

### مصفوفة الأولويات

| الأولوية | الخدمات | الوحدات | الأسابيع |
|----------|---------|---------|----------|
| 🔴 فوري | 6 خدمات + 4 أرشفة | 6 وحدات تحديث | 1-2 |
| 🟠 متوسط | 4 خدمات | 3 وحدات تحسين | 3-4 |
| 🟡 مخطط | 5 خدمات | 5 وحدات جديدة | 5-8 |
| 🟢 متقدم | 3 خدمات | 3 وحدات تطوير | 9-12 |

---

## التوصيات النهائية

### يجب تنفيذه فوراً
1. ربط `alert-service` بشاشة الإنذارات (بيانات وهمية حالياً)
2. ربط `copilot-api` بالمساعد الذكي (RAG + Multi-LLM)
3. أرشفة 4 خدمات مهملة
4. ربط `irrigation-cycle-engine` بشاشة الري المحوري

### يجب تجنبه
1. عدم ربط خدمات المطورين (code-review, code-fix) بالتطبيق
2. عدم كشف خدمات AI الداخلية (agent-registry, llm-orchestrator) مباشرة
3. عدم استدعاء محركات حسابية (yolo26, hydrology) مباشرة من التطبيق
4. عدم إنشاء شاشات لخدمات البنية التحتية (audit, ws-gateway)

### قاعدة ذهبية
> **كل شاشة في التطبيق = خدمة واجهة واحدة**
> **كل خدمة واجهة = 2-5 خدمات خلفية**
> **المزارع لا يحتاج معرفة ما يحدث وراء الكواليس**

---

_التاريخ: 2026-02-16 | الإصدار: 16.0.0 | المراجع: Deep Service Audit_
