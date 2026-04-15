# توثيق الخدمات والحاويات والوحدات المشتركة

**المشروع**: منصة سهول للاستخبارات الزراعية الوطنية (SAHOOL)
**الإصدار**: 16.0.0
**تاريخ التوثيق**: 2026-04-10
**الفرع**: `claude/document-services-containers-x39YJ`
**المالك**: KAFAAT

---

## نظرة عامة

يوفّر هذا المستند توثيقاً شاملاً باللغة العربية لمنصة SAHOOL يغطي ثلاثة محاور رئيسية:

1. **الخدمات المصغرة** — 73 خدمة مصغرة موزّعة بين Python (FastAPI) و Node.js (NestJS)
2. **الحاويات والبنية التحتية** — 15 ملف `docker-compose` بالإضافة إلى صور Docker الأساسية وخدمات البنية التحتية المشتركة
3. **الوحدات المشتركة** — 89 وحدة Python في مجلد `shared/` تُستخدم من قِبل جميع الخدمات

### ملخص الأرقام

| العنصر | العدد |
|---------|--------|
| الخدمات المصغرة النشطة | 73 |
| الخدمات المؤرشفة (مُلغاة) | 15 |
| التطبيقات الأمامية (Admin, Web, Mobile, Kernel) | 4 |
| ملفات Docker Compose | 15 |
| صور Docker الأساسية | 4 |
| الوحدات المشتركة في `shared/` | 89 |
| الحزم في `packages/` | 27 |

### التقنيات الرئيسية

- **Backend Python**: FastAPI 0.135.1, Tortoise ORM, asyncpg, Pydantic v2, Python 3.11+
- **Backend Node.js**: NestJS 10.x, Prisma 5.x, TypeScript 5.9.x, Node 20+
- **قاعدة البيانات**: PostgreSQL 16 + PostGIS 3.4
- **ناقل الأحداث**: NATS 2.10 مع JetStream
- **بوابة API**: Kong 3.x (105 مسار)
- **التخزين المؤقت**: Redis 7.x مع Sentinel HA
- **تجميع الاتصالات**: PgBouncer (transaction mode, 250 اتصال)

---

# الخدمات المصغرة (Microservices)

تحتوي منصة SAHOOL على **73 خدمة مصغرة** نشطة موزعة بين Python (FastAPI) و Node.js (NestJS)، تخدم جميع مجالات الذكاء الزراعي.

**ملخص التوزيع**: ~54 خدمة Python FastAPI + 17 خدمة Node.js NestJS + 2 خدمة Python متخصصة.

---

## 1. الخدمات الأساسية (Core Infrastructure)

الخدمات التي توفر القدرات الأساسية للمنصة: المصادقة، الإشعارات، الفوترة، المهام، والتدقيق.

| الخدمة | التقنية | المنفذ | الوصف |
|--------|---------|---------|--------|
| **user-service** | Node.js / NestJS | 3025 | إدارة الهوية والمصادقة: تسجيل، دخول، JWT، 2FA، RBAC، إدارة الجلسات |
| **notification-service** | Python / FastAPI | 8110 | تسليم إشعارات متعدد القنوات: بريد، SMS، Push، WebSocket |
| **billing-core** | Python / FastAPI | 8089 | إدارة الاشتراكات والفواتير والمدفوعات للمنصة |
| **task-service** | Python / FastAPI | 8103 | إدارة مهام زراعية (ري، تسميد، رش، تفتيش) |
| **equipment-service** | Python / FastAPI | 8101 | تتبع المعدات والأصول (جرارات، مضخات، طائرات مسيرة) |
| **alert-service** | Python / FastAPI | 8113 | إدارة التنبيهات والتحذيرات الزراعية (طقس، آفات، ري) |
| **provider-config** | Python / FastAPI | 8104 | إدارة إعدادات مزوّدي الخدمات الخارجية (خرائط، طقس، أقمار صناعية) |
| **audit-service** | Python / FastAPI | 8114 | تسجيل مركزي للتدقيق مع سلسلة هاش للسلامة وتقارير الامتثال |
| **ws-gateway** | Python / FastAPI | 8081 | بوابة WebSocket للاتصالات الفورية وربط NATS بالعملاء |

---

## 2. إدارة الحقول والعمليات (Field & Operations)

| الخدمة | التقنية | المنفذ | الوصف |
|--------|---------|---------|--------|
| **field-management-service** | Node.js / NestJS | 3000 | النظام الموحّد لإدارة الحقول مع تحليلات المناطق وتتبع المحاصيل (الخدمة الأكبر) |
| **field-intelligence** | Python / FastAPI | 8120 | تحليل شامل للحقول ودعم القرار مع تجميع البيانات |
| **inventory-service** | Python / FastAPI | 8116 | إدارة المخزون الزراعي المتقدمة مع التنبؤ والإشعارات |

---

## 3. التحليلات والذكاء (Analytics & Intelligence)

الخدمات المتعلقة بتحليل الصور الفضائية، نماذج الذكاء الاصطناعي للمحاصيل، واكتشاف الآفات.

| الخدمة | التقنية | المنفذ | الوصف |
|--------|---------|---------|--------|
| **vegetation-analysis-service** | Python / FastAPI | 8090 | تحليل موحّد للغطاء النباتي يشمل LAI و NDVI من الصور الفضائية |
| **crop-intelligence-service** | Python / FastAPI | 8095 | تحليل موحّد للمحاصيل، نمذجة النمو، وذكاء الحقول القائم على المناطق |
| **indicators-service** | Python / FastAPI | 8091 | حساب وتحليل مؤشرات الأداء الزراعي |
| **ndvi-processor** | Python / FastAPI | 8118 | معالجة الصور الفضائية وحساب NDVI (قيد الإلغاء لصالح vegetation-analysis-service) |
| **virtual-sensors** | Python / FastAPI | 8119 | تقدير القياسات الزراعية باستخدام نماذج ML وبيانات الأقمار الصناعية |
| **lai-estimation** | Node.js / NestJS | 3022 | تقدير مؤشر مساحة الأوراق (مُدمج في vegetation-analysis-service) |
| **skills-service** | Python / FastAPI | 8121 | تتبع مهارات المزارع وتقييم القدرات |
| **soil-analysis-service** | Python / FastAPI | 8134 | اختبار وتحليل شامل للتربة مع تصنيفات الشرق الأوسط |
| **pest-detection-service** | Python / FastAPI | 8125 | اكتشاف الآفات والأمراض بالذكاء الاصطناعي مع توصيات IPM |
| **digital-twin-engine** | Python / FastAPI | 8253 | محاكاة توأم رقمي متقدم لنمذجة ظروف الحقل |
| **yield-prediction-service** | Node.js / NestJS | 8152 | التنبؤ الموحّد بالإنتاجية باستخدام نماذج مجمّعة (ensemble) |
| **yield-prediction** | Node.js / NestJS | 3021 | خدمة التنبؤ بالإنتاجية القديمة (مُدمجة في yield-prediction-service) |

---

## 4. القرارات والاستشارات (Decision & Advisory)

الخدمات المسؤولة عن تقديم التوصيات الزراعية وجدولة العمليات.

| الخدمة | التقنية | المنفذ | الوصف |
|--------|---------|---------|--------|
| **crop-growth-model** | Node.js / NestJS | 3023 | محاكاة نمو المحاصيل (مُدمجة في crop-intelligence-service) |
| **advisory-service** | Python / FastAPI | 8093 | تشخيص موحّد للأمراض، تقييم المغذيات، تخطيط التسميد، توصيات المحاصيل |
| **irrigation-smart** | Python / FastAPI | 8094 | جدولة الري الذكية وتحسين استخدام المياه |
| **agro-rules** | Python / FastAPI | - | محرك قواعد قائم على الأحداث لتوليد المهام تلقائياً من NDVI/الطقس/IoT |
| **irrigation-cycle-engine** | Python / FastAPI | 8250 | إدارة دورات الري ومحرك التحسين |
| **fertigation-engine** | Python / FastAPI | 8252 | تكامل جدولة التسميد مع الري (fertigation) |

---

## 5. إنترنت الأشياء والتكامل (IoT & Integration)

| الخدمة | التقنية | المنفذ | الوصف |
|--------|---------|---------|--------|
| **iot-service** | Node.js / NestJS | 8117 | إدارة أجهزة الاستشعار والمشغّلات الذكية للري والمراقبة |
| **iot-gateway** | Python / FastAPI | 8106 | جسر MQTT ↔ NATS لأجهزة IoT وأجهزة الاستشعار |
| **iot-sensor-hub** | Python / FastAPI | 8251 | بوابة LoRaWAN + MQTT مع قدرات حوسبة طرفية |
| **weather-service** | Python / FastAPI | 8092 | تقييم موحّد للطقس مع التنبؤ والتنبيهات |
| **astronomical-calendar** | Python / FastAPI | 8111 | التقويم الفلكي اليمني التقليدي للتخطيط الزراعي |
| **drone-service** | Python / FastAPI | 8126 | تكامل شامل للطائرات المسيرة مع تخطيط الرحلات وخرائط VRA |
| **ussd-gateway** | Python / FastAPI | 8183 | دعم SMS/USSD/WhatsApp للهواتف الأساسية |
| **whatsapp-bot-service** | Python / FastAPI | - | بوت WhatsApp ذكي لمحادثات المزارعين |
| **wechat-service** | Python / FastAPI | 8135 | تكامل WeChat لمراسلة المزارعين (profile: deprecated) |

---

## 6. الأعمال والمجتمع (Community & Business)

| الخدمة | التقنية | المنفذ | الوصف |
|--------|---------|---------|--------|
| **marketplace-service** | Node.js / NestJS | 3010 | سوق زراعي لبيع وشراء المنتجات والمستلزمات |
| **chat-service** | Node.js / NestJS | 8115 | مراسلة فورية بين المشتري والبائع باستخدام Socket.IO |
| **community-service** | Python / FastAPI | 8133 | تكامل Rocket.Chat لمجتمعات المزارعين وبوتات الاستشارة |
| **research-core** | Node.js / NestJS | 3015 | إدارة الأبحاث الزراعية للتجارب والدراسات الحقلية |
| **disaster-assessment** | Node.js / NestJS | 3020 | تقييم أضرار المحاصيل من الكوارث الطبيعية |
| **cooperative-service** | Python / FastAPI | 8127 | إدارة التعاونيات الزراعية لتجميع الموارد والشراء الجماعي |
| **crm-service** | Python / FastAPI | 8131 | إدارة علاقات العملاء للعمليات الزراعية |
| **logistics-service** | Python / FastAPI | 8167 | إدارة اللوجستيات الزراعية وتنسيق سلسلة التوريد |
| **supply-chain-service** | Python / FastAPI | 8230 | ربط المزارعين بالموردين مع شراء تلقائي حسب التوصيات |
| **traceability-service** | Python / FastAPI | 8123 | تتبّع سلسلة التوريد من المزرعة إلى المائدة مع QR و blockchain |
| **globalgap-compliance** | Python / FastAPI | 8128 | تتبع شهادات المزارع لمعايير GlobalGAP IFA v6 |

---

## 7. الذكاء الاصطناعي والوكلاء (AI & Agents)

| الخدمة | التقنية | المنفذ | الوصف |
|--------|---------|---------|--------|
| **agent-registry** | Python / FastAPI | 8160 | سجل وكلاء بروتوكول A2A مع الاكتشاف ومراقبة الصحة |
| **code-fix-agent** | Python / FastAPI | 8162 | وكيل ذكاء اصطناعي لتحليل وإصلاح أخطاء الكود |
| **code-review-agent** | Node.js / NestJS | - | مراجعة الكود باستخدام Claude Agent SDK لتحليل الأخطاء والثغرات الأمنية |
| **code-review-service** | Python / FastAPI | 8102 | مراجعة كود فورية باستخدام DeepSeek/Ollama مع التركيز الأمني |
| **ai-advisor** | Python / FastAPI | 8112 | نظام متعدد الوكلاء للاستشارات الزراعية الشاملة عبر Claude/LangChain |
| **ai-agents-core** | Python / FastAPI | 8161 | نظام وكلاء هرمي متعدد الطبقات (4 طبقات) للزراعة الذكية مع معالجة طرفية |
| **ai-agents-service** | Python / FastAPI | 8130 | وكلاء مستقلون للذكاء الزراعي في الوقت الفعلي |
| **ai-chat-assistant** | Python / FastAPI | 8260 | تكامل محادثة ذكاء اصطناعي خفيف مع استشارات زراعية فورية |
| **llm-orchestrator-service** | Python / FastAPI | 8164 | تنسيق LLM مركزي وتوجيه الوكلاء |
| **copilot-api** | Python / FastAPI | 8088 | API المساعد الذكي لـ SAHOOL متعدد-LLM مع RAG |
| **knowledge-graph** | Python / FastAPI | 8140 | قاعدة معرفة دلالية لاسترجاع المعلومات الزراعية |
| **mcp-server** | Python / FastAPI | 8201 | خادم Model Context Protocol لتنسيق الوكلاء المتعددين |

---

## 8. الرؤية والتضاريس والحافة (Vision, Terrain & Edge)

خدمات متخصصة في رؤية الحاسوب، تحليل التضاريس، وإدارة أجهزة الحافة.

| الخدمة | التقنية | المنفذ | الوصف |
|--------|---------|---------|--------|
| **yolo26-vision-service** | Python / FastAPI + CUDA | 8150 | رؤية حاسوب YOLO26 لاكتشاف الآفات والأمراض والأعشاب (22 آفة، 34 مرض، 12 عُشب) |
| **ground-vision-service** | Python / FastAPI | 8182 | مراقبة بكاميرات مثبتة على الأبراج متكاملة مع الأقمار الصناعية و IoT |
| **terrain-core-service** | Python / FastAPI | 8185 | معالجة DEM وتحليل التضاريس |
| **hydrology-service** | Python / FastAPI | 8165 | تحليل الهيدرولوجيا والصرف لتخطيط الري |
| **leveling-optimizer-service** | Python / FastAPI | 8170 | تحليل الطبوغرافيا وتحسين تسوية الحقول |
| **edge-orchestrator-service** | Python / FastAPI | 8180 | تنسيق أجهزة الحافة (Jetson Orin) وإدارة النماذج |

---

## 9. الخدمات المتخصصة (Specialized)

| الخدمة | التقنية | المنفذ | الوصف |
|--------|---------|---------|--------|
| **lowcode-engine** | Python / FastAPI | 8132 | منشئ تطبيقات زراعية مرئي بدون كود |
| **demo-data** | Python / FastAPI | - | مولّد بيانات تجريبية واقعية للاختبار |
| **vllm-deepseek** | Python / vLLM | - | خادم استدلال vLLM لـ DeepSeek Coder 6.7B مع تسريع GPU (profile: gpu) |

---

## 10. نقاط نهاية API القياسية

كل خدمة Python أو Node.js تلتزم بنقاط النهاية التالية:

| النقطة | الوصف |
|---------|--------|
| `GET /healthz` | فحص الحياة (liveness probe) |
| `GET /readyz` | فحص الجاهزية (readiness probe) |
| `GET /health` | حالة مجمّعة |
| `GET /metrics` | مقاييس Prometheus |
| `GET /docs` | توثيق Swagger/OpenAPI (خدمات Python) |

بنية API موحّدة: `/api/v1/{resource}` مع إصدارات مسار واضحة.

---

## 11. أنماط الاتصال بين الخدمات

### 11.1 الأحداث (NATS)

جميع الخدمات تتواصل عبر NATS JetStream باستخدام بنية أحداث من 4 طبقات:

| الطبقة | الخدمات النموذجية |
|---------|-------------------|
| **الاستحواذ** | `vegetation-analysis-service`, `iot-service`, `weather-service`, `virtual-sensors`, `iot-gateway`, `edge-orchestrator-service` |
| **الذكاء** | `indicators-service`, `crop-intelligence-service`, `ndvi-processor`, `field-intelligence`, `skills-service`, `yolo26-vision-service`, `terrain-core-service` |
| **القرار** | `crop-growth-model`, `advisory-service`, `irrigation-smart`, `yield-prediction-service`, `hydrology-service`, `leveling-optimizer-service` |
| **الأعمال** | `notification-service`, `marketplace-service`, `billing-core`, `chat-service`, `task-service`, `equipment-service`, `ws-gateway` |

### 11.2 أنماط موضوعات NATS

```
sahool.{domain}.{action}                    # الأساسي
sahool.tenant.{tenant_id}.{domain}.{action}  # معزول حسب المستأجر
```

### 11.3 بوابة Kong

جميع طلبات HTTP الخارجية تمر عبر **Kong API Gateway** (المنفذ 8000/8001) الذي يوفر:
- المصادقة (JWT, OAuth2)
- Rate limiting حسب المستوى (Starter, Professional, Enterprise)
- CORS وأمن الرأس
- التوجيه عبر 105 مسار
- التتبع والمقاييس

---

## 12. ملخص إحصائي

| الفئة | عدد الخدمات |
|-------|--------------|
| البنية التحتية الأساسية | 9 |
| إدارة الحقول والعمليات | 3 |
| التحليلات والذكاء | 12 |
| القرارات والاستشارات | 6 |
| IoT والتكامل | 9 |
| الأعمال والمجتمع | 11 |
| الذكاء الاصطناعي والوكلاء | 12 |
| الرؤية والتضاريس والحافة | 6 |
| متخصصة | 3 |
| **المجموع النشط** | **71+** |
| الخدمات المُلغاة المؤرشفة | 15 |

> **ملاحظة**: بعض الخدمات القديمة (مثل `crop-growth-model`, `lai-estimation`, `yield-prediction`) لا تزال موجودة كـ Node.js في `docker-compose.yml` لكنها في طور الإلغاء لصالح الخدمات الموحّدة الأحدث.

---

# الحاويات والبنية التحتية (Containers & Infrastructure)

يوثّق هذا القسم جميع حاويات Docker المستخدَمة في منصة SAHOOL، بما في ذلك ملفات `docker-compose`، وصور Docker الأساسية، وخدمات البنية التحتية المشتركة.

---

## 1. ملفات Docker Compose

تحتوي المنصة على **15 ملف `docker-compose`** موزّعة بين جذر المشروع ومجلد `docker/`. كل ملف يخدم غرضاً محدداً (تطوير، إنتاج، HA، اختبارات، إلخ).

### 1.1 الملفات في جذر المشروع

#### `docker-compose.yml` — الملف الرئيسي (197 KB)

- **الغرض**: التنسيق الأساسي لكامل المنصة (تطوير وإنتاج). يحتوي على جميع الخدمات المصغرة والبنية التحتية المتكاملة.
- **عدد الخدمات**: أكثر من **85 حاوية** (72 خدمة مصغرة + 13 خدمة بنية تحتية).
- **الخدمات الرئيسية** (مختارة):
  - **البنية التحتية**: `postgres` (PostGIS 16)، `pgbouncer`، `redis`، `vault`، `nats`، `nats-prometheus-exporter`، `mlflow`، `mqtt`، `qdrant`، `mongo`، `rocketchat`، `ollama`، `vllm-deepseek`، `etcd`، `minio`، `milvus`، `kong`
  - **خدمات الأعمال** (Node.js): `field-management-service`، `marketplace-service`، `research-core`، `disaster-assessment`، `yield-prediction`، `lai-estimation`، `crop-growth-model`، `chat-service`، `iot-service`، `user-service`، `yield-prediction-service`، `code-review-agent`
  - **خدمات Python FastAPI**: `ws-gateway`، `billing-core`، `vegetation-analysis-service`، `indicators-service`، `weather-service`، `advisory-service`، `irrigation-smart`، `crop-intelligence-service`، `virtual-sensors`، `equipment-service`، `task-service`، `notification-service`، وغيرها كثير
- **الشبكات**: `sahool-network` (bridge)
- **التخزين (Volumes)**: `postgres_data`، `nats_data`، `vault_data`، `mlflow_artifacts`، `redis_data`، `qdrant_data`، `mqtt_data`، `mqtt_logs`، `kong_logs`، `ollama_data`، `vllm_models`، `vllm_hf_cache`، `etcd_data`، `minio_data`، `milvus_data`، `mongo_data`، `rocketchat_uploads`، `terrain-dem-data`
- **Profiles**:
  - `deprecated`: تفعيل الخدمات المُلغاة (rocketchat، wechat-service)
  - `gpu`: تفعيل خدمات GPU (vllm-deepseek)
  - `etcd-auth`: تفعيل مصادقة etcd
- **التسجيل**: محرك `json-file` بحجم أقصى 50MB وتدوير 3 ملفات

#### `docker-compose-core.yml` (125 KB)

- **الغرض**: بنية تحتية أساسية مخففة للتطوير السريع، بدون خدمات مصغرة غير ضرورية.
- **الخدمات الرئيسية**: PostgreSQL، PgBouncer، Redis، NATS، Kong فقط
- **التحسينات**: PgBouncer بوضع `transaction mode` مع 250 اتصالاً كحد أقصى وحجم pool = 30

#### `docker-compose.prod.yml`

- **الغرض**: تجاوزات (overrides) خاصة بالإنتاج لتطبيق حدود الموارد وتحسينات الأداء.
- **التطبيقات**:
  - PostgreSQL: حد أقصى 2 CPU / 2 GB RAM
  - Kong: حد أقصى 1 CPU / 512 MB مع 4 عمليات عاملة و8192 اتصالاً
  - NATS: فرض TLS باستخدام `nats-secure.conf`
- **التسجيل**: 100 MB بحجم أقصى وتدوير 5 ملفات (أكثر حزماً من التطوير)
- **الأمان**: يتطلب أسرار KONG_JWT لواجهات Web/Mobile/Internal

#### `docker-compose.ha.yml` (High Availability)

- **الغرض**: النسخ المتماثل (replication) لـ PostgreSQL مع دعم الفشل التلقائي.
- **الخدمات**: `postgres` (أساسي) + `postgres-replica` مع أرشفة WAL
- **النسخ المتماثل**: مستخدم مخصص `postgres_replication_user`، ودعم الاسترداد لنقطة زمنية (PITR)
- **التخزين**: `postgres_wal_archive` لتخزين WAL و`postgres_logs` للسجلات
- **TLS**: يدعم شهادات العميل والـ CA للاتصالات الآمنة

#### `docker-compose.redis-ha.yml`

- **الغرض**: Redis عالي التوفر مع Sentinel.
- **البنية**: 1 Redis master + 2 replicas + 3 Sentinels (quorum = 2)
- **المزايا**: فشل تلقائي، دعم ACL (app/admin/kong/readonly)
- **الصورة**: `redis:7.4-alpine`

#### `docker-compose.telemetry.yml` (مجموعة OpenTelemetry)

- **الغرض**: التتبع الموزع والمراقبة لأكثر من 44 خدمة.
- **الخدمات**: Jaeger (all-in-one)، OpenTelemetry Collector، Prometheus، Grafana
- **التخزين**: Jaeger يستخدم Badger لتخزين مؤقت، و Prometheus كخلفية للمقاييس
- **الشبكات**: `sahool-network` + `telemetry-network` (شبكة معزولة)
- **حدود الموارد**: Jaeger = 2 CPU / 2 GB

#### `docker-compose.test.yml`

- **الغرض**: بيئة اختبار معزولة مع بيانات اعتماد افتراضية.
- **الخدمات**:
  - `postgres_test` (port 5433)
  - `redis_test` (port 6380)
  - `nats_test` (port 4223)
  - `qdrant_test` (port 6335)
- **الشبكة**: `sahool-test-network` (منفصلة)
- **الأمان**: بيانات اعتماد اختبار فقط (ليست للإنتاج)

#### `docker-compose.tls.yml`

- **الغرض**: طبقة تغطية (overlay) لفرض TLS على اتصالات الخدمات الداخلية.
- **تجاوزات**:
  - PostgreSQL: وضع TLS
  - PgBouncer: فرض TLS باستخدام `pgbouncer-tls.ini`
  - etcd: شهادات يدوية
- **الشهادات**: يتوقع وجودها في `./config/certs/postgres`، `./config/certs/pgbouncer`، `./config/certs/etcd`

#### `docker-compose.walg.yml` (النسخ الاحتياطي)

- **الغرض**: أرشفة WAL إلى S3/MinIO للاسترداد لنقطة زمنية.
- **الصورة المخصصة**: `sahool/postgres-walg:16-3.4`
- **الإعدادات**:
  - ضغط Brotli
  - 6 خطوات delta كحد أقصى
  - 4 عمليات رفع/تنزيل متزامنة
  - احتفاظ لمدة 7 أيام
- **الأرشفة**: بادئة S3 مع بيانات اعتماد AWS

#### `docker-compose.wsl2.yml`

- **الغرض**: إصلاحات خاصة بـ Windows Subsystem for Linux 2 (حل مشكلة انحراف الساعة).
- **الخدمات المتأثرة**: `etcd`، `milvus` (مع قدرة `SYS_TIME`)
- **تحذير**: للتطوير فقط، ليس للإنتاج

### 1.2 الملفات في مجلد `docker/`

#### `docker/docker-compose.infra.yml`

- **الغرض**: نشر مستقل لخدمات البنية التحتية (قابل للتشغيل بشكل مستقل).
- **الخدمات**: PostgreSQL، `db-migrator` (تشغيل تلقائي للهجرات)، Redis، NATS، Kong، Vault
- **الاستخدام**: يمكن استخدامه كملف رئيسي للنشر الأدنى

#### `docker/docker-compose.dlq.yml`

- **الغرض**: إدارة ومراقبة رسائل قائمة الانتظار الميتة (Dead Letter Queue).
- **الخدمة**: `dlq-service` (FastAPI على المنفذ 8190)
- **الإعدادات**: 3 محاولات إعادة كحد أقصى، حد تنبيه 100 رسالة، احتفاظ 30 يوماً

#### `docker/docker-compose.iot.yml` (ملغى)

- **الغرض**: اختبار IoT مستقل (مُلغى — الوظائف مُدمجة في الملف الرئيسي).
- **الخدمات**:
  - `mqtt-broker-test` (eclipse-mosquitto على 11883)
  - `iot-gateway-test`
- **ملاحظة**: استخدم الملف الرئيسي في الإنتاج

#### `docker/docker-compose.logging.yml`

- **الغرض**: تجميع السجلات باستخدام Loki + Promtail.
- **الخدمات**:
  - `loki` (port 3100)
  - `promtail` (شاحن السجلات)
- **نقاط التركيب**: `/var/log` و socket لـ Docker daemon لسجلات الحاويات
- **حدود الموارد**: Loki = 1 CPU / 1 GB، Promtail = 0.5 CPU / 512 MB

#### `docker/docker-compose.secrets.yml`

- **الغرض**: قالب لإدارة الأسرار (Docker Swarm/Compose Secrets).
- **الأسرار المعرفة**:
  - قاعدة البيانات (`postgres`, `replication`)
  - Redis
  - NATS
  - JWT (secret / private / public)
  - مفاتيح التشفير
  - MinIO
  - شهادات TLS
- **مواقع الملفات**: `./secrets/` و `./certs/`

---

## 2. صور Docker الأساسية (Base Images)

تقع الملفات الأساسية في `docker/`:

| الملف | الصورة الأساسية | الغرض |
|-------|----------------|--------|
| `Dockerfile.python.base` | `python:3.11-slim-bookworm` | الصورة الأساسية لكل خدمات Python FastAPI |
| `Dockerfile.node.base` | `node:20-slim` | الصورة الأساسية لكل خدمات Node.js / NestJS |
| `Dockerfile.ai-base` | Python 3.11 مع تبعيات ML | للخدمات المتعلقة بالذكاء الاصطناعي مع مرايا Aliyun + Tsinghua |
| `Dockerfile.etcd-init` | مُهيِّئ مخصص | تهيئة كتلة etcd |

### خصائص مشتركة لجميع الصور الأساسية:

- **مستخدم غير root**: `sahool` (UID 1000, GID 1000)
- **دعم إشارات النظام**: يستخدم `tini` (Node.js) لمعالجة SIGTERM
- **متغيرات Python**: `PYTHONDONTWRITEBYTECODE=1`, `PYTHONUNBUFFERED=1`
- **متغيرات pip**: `PIP_NO_CACHE_DIR=1`, `PIP_DEFAULT_TIMEOUT=300`, `PIP_RETRIES=10`
- **مرايا pip** (متعددة المستويات): PyPI الرسمي → Aliyun → Tsinghua → Tencent
- **تقوية أمنية**: إزالة صلاحيات setuid، نظام ملفات للقراءة فقط حيث أمكن

### استثناء: `yolo26-vision-service`

يستخدم صورة مختلفة: `nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04` لدعم GPU وتسريع الاستدلال بـ TensorRT.

---

## 3. خدمات البنية التحتية المشتركة

توفّر هذه الخدمات الأساس التشغيلي لكامل المنصة:

### 3.1 قواعد البيانات والتخزين

| الخدمة | الصورة | المنفذ | الغرض |
|--------|---------|--------|--------|
| **postgres** | `postgis/postgis:16-3.4` | 5432 | قاعدة البيانات الرئيسية مع PostGIS للعمليات الجغرافية |
| **pgbouncer** | `edoburu/pgbouncer` | 6432 | تجميع الاتصالات (transaction mode، 250 اتصال كحد أقصى) |
| **redis** | `redis:7.4-alpine` | 6379 | التخزين المؤقت، إدارة الجلسات، rate limiting |
| **mongo** | `mongo:7` | 27017 | قاعدة بيانات NoSQL (لـ RocketChat وبعض الخدمات) |
| **minio** | `minio/minio` | 9000/9001 | تخزين كائنات متوافق مع S3 |
| **milvus** | `milvusdb/milvus` | 19530 | قاعدة بيانات متجهات للبحث الدلالي |
| **qdrant** | `qdrant/qdrant` | 6333 | قاعدة بيانات متجهات بديلة للـ RAG |

### 3.2 المراسلة والأحداث

| الخدمة | الصورة | المنفذ | الغرض |
|--------|---------|--------|--------|
| **nats** | `nats:2.10-alpine` | 4222 | ناقل الأحداث مع JetStream للاستمرارية |
| **nats-prometheus-exporter** | `natsio/prometheus-nats-exporter` | 7777 | تصدير مقاييس NATS إلى Prometheus |
| **nats-stream-init** | مخصص | - | تهيئة تدفقات JetStream عند الإقلاع |
| **mqtt** | `eclipse-mosquitto:2.0` | 1883/9001 | وسيط MQTT لأجهزة IoT |

### 3.3 بوابة API والأمان

| الخدمة | الصورة | المنفذ | الغرض |
|--------|---------|--------|--------|
| **kong** | `kong:3.x-alpine` | 8000/8001 | بوابة API مع 105 مسارات، مصادقة، rate limiting |
| **vault** | `hashicorp/vault` | 8200 | إدارة الأسرار والتشفير |
| **etcd** | `bitnami/etcd` | 2379/2380 | مخزن key-value موزع (لـ Milvus) |

### 3.4 الذكاء الاصطناعي والـ ML

| الخدمة | الصورة | المنفذ | الغرض |
|--------|---------|--------|--------|
| **ollama** | `ollama/ollama` | 11434 | استضافة LLMs محلياً (CodeLlama, Mistral, DeepSeek) |
| **ollama-model-loader** | مخصص | - | تحميل النماذج المطلوبة عند الإقلاع |
| **vllm-deepseek** | `vllm/vllm-openai` | 8270 | خادم استدلال GPU لـ DeepSeek Coder (profile: gpu) |
| **mlflow** | `ghcr.io/mlflow/mlflow` | 5000 | تتبع تجارب ML وتسجيل النماذج |

### 3.5 المراقبة والسجلات (من ملفات overlay)

| الخدمة | الصورة | المنفذ | الغرض |
|--------|---------|--------|--------|
| **prometheus** | `prom/prometheus` | 9090 | جمع المقاييس |
| **grafana** | `grafana/grafana` | 3000 | لوحات تحكم المراقبة (4 لوحات) |
| **jaeger** | `jaegertracing/all-in-one` | 16686 | التتبع الموزع (OpenTelemetry) |
| **otel-collector** | `otel/opentelemetry-collector-contrib` | 4317/4318 | جمع ونقل بيانات التتبع |
| **loki** | `grafana/loki` | 3100 | تجميع السجلات |
| **promtail** | `grafana/promtail` | - | شحن سجلات الحاويات إلى Loki |

### 3.6 التواصل والدردشة

| الخدمة | الصورة | المنفذ | الغرض |
|--------|---------|--------|--------|
| **rocketchat** | `rocket.chat` | 3000 | منصة دردشة لمجتمعات المزارعين (profile: deprecated) |

---

## 4. الشبكات والتخزين

### الشبكات المعرفة

| الشبكة | النوع | الاستخدام |
|--------|-------|------------|
| `sahool-network` | bridge | الشبكة الرئيسية لجميع الخدمات |
| `telemetry-network` | bridge | شبكة معزولة لمكونات المراقبة |
| `sahool-test-network` | bridge | بيئة الاختبار (منفصلة تماماً) |

### الأحجام المُسماة (Named Volumes)

الأحجام الرئيسية من `docker-compose.yml`:

| الحجم | المحتوى |
|-------|---------|
| `postgres_data` | بيانات PostgreSQL |
| `redis_data` | بيانات Redis |
| `nats_data` | تخزين JetStream |
| `vault_data` | أسرار Vault |
| `mlflow_artifacts` | قطع نماذج MLflow |
| `qdrant_data` | مؤشرات Qdrant |
| `milvus_data` | مؤشرات Milvus |
| `minio_data` | كائنات MinIO (S3) |
| `etcd_data` | حالة etcd |
| `mongo_data`, `mongo_configdb` | بيانات MongoDB |
| `mqtt_data`, `mqtt_logs`, `mqtt_passwd` | بيانات Mosquitto |
| `kong_logs` | سجلات Kong |
| `ollama_data` | نماذج Ollama |
| `vllm_models`, `vllm_hf_cache` | نماذج vLLM و HuggingFace cache |
| `rocketchat_uploads` | مرفقات RocketChat |
| `terrain-dem-data` | بيانات DEM للتضاريس |
| `code_review_logs` | سجلات خدمة مراجعة الكود |

---

## 5. الأوامر الشائعة (Makefile)

فيما يلي الأوامر الأكثر استخداماً لإدارة الحاويات:

### تشغيل البيئات

```bash
make dev                    # بدء البيئة الكاملة
make dev-starter            # حزمة البداية فقط
make dev-professional       # حزمة المحترفين
make dev-enterprise         # جميع خدمات المؤسسات
make infra-up               # البنية التحتية فقط (postgres، redis، nats، kong)
make dev-vision             # تشغيل خدمات الرؤية (yolo26-vision-service)
make dev-terrain            # تشغيل خدمات التضاريس
make dev-edge               # تشغيل edge-orchestrator
make dev-ai                 # تشغيل خدمات الذكاء الاصطناعي
make dev-agents             # تشغيل خدمات الوكلاء
make dev-mcp                # تشغيل خادم MCP
```

### البناء والإدارة

```bash
make build                  # بناء كل صور Docker (بالتوازي)
make build-python           # خدمات Python فقط
make build-node             # خدمات Node.js فقط
make build-ai               # صور خدمات الذكاء الاصطناعي
make up                     # بدء كل الخدمات
make down                   # إيقاف كل الخدمات
make down-volumes           # إيقاف وحذف الأحجام
make restart                # إعادة التشغيل
```

### السجلات والحالة

```bash
make logs                   # سجلات كل الخدمات
make logs-service SERVICE=field_ops   # سجلات خدمة محددة
make ps                     # قائمة الحاويات قيد التشغيل
make stats                  # إحصائيات المشروع
make status                 # حالة الخدمات وعناوينها
make health                 # فحص صحة جميع الخدمات
make shell SERVICE=name     # فتح shell داخل حاوية
```

### قاعدة البيانات

```bash
make db-migrate             # تشغيل الهجرات (Prisma)
make db-seed                # بيانات تجريبية
make db-reset               # إعادة تعيين (تحذير: يحذف البيانات)
make db-shell               # اتصال PostgreSQL
make db-backup              # نسخة احتياطية
```

### المراقبة والتنظيف

```bash
make monitoring-up          # تشغيل مجموعة Prometheus/Grafana
make monitoring-down        # إيقاف المراقبة
make monitoring-logs        # سجلات المراقبة
make clean                  # تنظيف الحاويات والأحجام
```

### تشغيل الخدمات المُلغاة (للاختبار فقط)

```bash
docker compose --profile deprecated up
docker compose --profile legacy up
```

---

## 6. أنماط الأمان والصحة

### فحوصات الصحة (Health Checks)

كل حاوية تعرّف `HEALTHCHECK` مع:
- `interval: 30s`
- `timeout: 10s`
- `retries: 3`
- `start_period: 10s-60s` (حسب الخدمة)

### نقاط النهاية القياسية للصحة

```
GET /healthz    # liveness probe
GET /readyz     # readiness probe  
GET /health     # حالة مجمّعة
GET /metrics    # مقاييس Prometheus
```

### ممارسات الأمان

- **مستخدم غير root**: جميع الحاويات تعمل باسم `sahool` (UID 1000)
- **نظام ملفات للقراءة فقط**: حيث أمكن
- **بناء متعدد المراحل**: 35+ خدمة تستخدم multi-stage builds
- **حدود الموارد**: CPU/RAM محددة في الإنتاج
- **شبكة معزولة**: الخدمات تتحدث فقط عبر `sahool-network`
- **TLS اختياري**: عبر `docker-compose.tls.yml`
- **إدارة الأسرار**: عبر Vault + Docker secrets

---

# الوحدات المشتركة (Shared Modules)

يحتوي مجلد `shared/` على **89 وحدة Python مشتركة** تُستخدم بواسطة جميع الخدمات المصغرة في منصة SAHOOL للاستخبارات الزراعية الوطنية. توفر هذه الوحدات طبقة موحدة للبنية التحتية، الأمان، الذكاء الاصطناعي، ومنطق المجال الزراعي.

> **إجمالي المحتويات**: 81 وحدة فرعية (مجلدات Python) + 6 ملفات Python على المستوى الأعلى + `README.md` + `__init__.py`.

---

## 1. البنية التحتية الأساسية (Core Infrastructure)

الوحدات الأساسية لتشغيل الخدمات (المصادقة، التخزين المؤقت، قاعدة البيانات، الأحداث، الوسيطات).

| الوحدة | الغرض |
|--------|--------|
| `auth` | المصادقة JWT، التحقق بخطوتين (2FA)، إبطال الرموز، Dependencies لـ FastAPI |
| `cache` | طبقة التخزين المؤقت مع Redis Sentinel عالي التوفر (HA) |
| `contracts` | عقود الـ API ومخططات الأحداث (Event Schemas) - مصدر الحقيقة الموحد |
| `db` | أدوات قاعدة البيانات وإدارة الاتصالات (asyncpg، Tortoise ORM) |
| `domain` | نماذج المجال الأساسية (المصادقة، المستخدمون، تعدد المستأجرين) |
| `events` | تعريفات أحداث NATS، موضوعات (Subjects)، Dead Letter Queue (DLQ) |
| `file_validation` | التحقق من صحة الملفات المرفوعة وفحص الفيروسات |
| `libs` | مكتبات مشتركة (Outbox pattern، التدقيق، التخزين المؤقت) |
| `middleware` | وسيطات HTTP (حدود المعدل، CORS، التسجيل، تتبع الطلبات) |
| `monitoring` | مقاييس Prometheus ومؤشرات SLI/SLO |
| `observability` | OpenTelemetry وJaeger للتتبع الموزع |
| `telemetry` | أدوات التتبع الموزع الإضافية |
| `secrets` | تكامل HashiCorp Vault لإدارة الأسرار |
| `security` | RBAC، JWT، محرك السياسات، تشفير البيانات |
| `versioning` | أدوات إدارة إصدارات الـ API |
| `audit_trail` | سجل التدقيق الموحد للعمليات الحساسة |
| `notification_preferences` | إدارة تفضيلات الإشعارات للمستخدمين |
| `service_enhancements` | وحدات تحسين الخدمات المشتركة |
| `design-system` | رموز نظام التصميم (Design Tokens) والأدوات المساعدة |
| `templates` | قوالب التهيئة والكود القابلة لإعادة الاستخدام |
| `integrations` | تكاملات الأنظمة الخارجية |
| `python-lib` | أدوات مكتبة Python العامة |
| `channel_adapter` | محوّل القنوات المتعددة - توحيد الرسائل من WhatsApp، USSD، WeChat، Web |

---

## 2. الذكاء الاصطناعي والتحليلات (AI & Intelligence)

الوحدات المتعلقة بالذكاء الاصطناعي، نماذج اللغة الكبيرة (LLM)، ومعالجة اللغة الطبيعية.

| الوحدة | الغرض |
|--------|--------|
| `ai` | محرك الذكاء الاصطناعي الشامل - Auto-Fix Engine، هندسة السياق، الوكلاء، الحراسات، سجل النماذج، قاعدة المعرفة، UltraRAG |
| `a2a` | بروتوكول الوكيل-إلى-الوكيل (Agent-to-Agent) من Linux Foundation |
| `agents` | تنسيق الوكلاء المتعددين عبر CrewAI (مستشار محاصيل، خبير ري، مشخّص أمراض) |
| `llm` | إعداد مزودي نماذج اللغة الكبيرة والتوجيه (Claude، OpenAI، Gemini، DeepSeek، Ollama) |
| `mcp` | بروتوكول سياق النموذج (Model Context Protocol) |
| `nlp` | معالجة اللغة العربية باستخدام AraBERT (تصنيف النوايا، استخراج الكيانات، تحليل المشاعر) |
| `satellite` | تكامل Sentinel Hub لتحليل NDVI والصور الفضائية |
| `ml` | مجموعات بيانات AgML الزراعية القياسية (PlantVillage، Wheat Rust، DeepWeeds) |
| `guardrails` | حراسات أمان الذكاء الاصطناعي (تصفية المدخلات والمخرجات) |
| `crm` | وحدة إدارة علاقات المزارعين (Farmer CRM) |

---

## 3. إدارة المحاصيل والحقول (Crop & Field Management)

وحدات منطق المجال الزراعي الأساسية لإدارة المحاصيل والحقول.

| الوحدة | الغرض |
|--------|--------|
| `agri_calendar` | التقويم الزراعي، التقويم الإسلامي، توقيت الزراعة والحصاد |
| `crop_rotation` | تخطيط تدوير المحاصيل لتحسين صحة التربة |
| `field_boundaries` | هندسة الحقل والعمليات الجغرافية المكانية (PostGIS، Shapely) |
| `geofencing` | التنبيهات القائمة على الحدود الجغرافية ومراقبة الوصول للحقول |
| `terrain` | معالجة نماذج الارتفاع الرقمية (DEM)، تحليل التضاريس، المعالجة الدفعية |
| `harvest_quality` | إدارة جودة ما بعد الحصاد، التصنيف، والتسعير |
| `farm_documents` | توثيق المزرعة، الامتثال، والتنبيهات |

---

## 4. الري والمياه (Irrigation & Water)

وحدات إدارة الري الذكي وكفاءة استخدام المياه.

| الوحدة | الغرض |
|--------|--------|
| `irrigation` | جدولة الري الذكي، محرك التعاون، قوائم التحقق |
| `water_management` | مراقبة استخدام المياه وتقارير الكفاءة |
| `ml_irrigation` | تحسين الري القائم على التعلم الآلي والتنبؤ |
| `salinity` | مراقبة ملوحة التربة وإدارة التخفيف |
| `pivot_management` | إدارة ري المحور المركزي (Center Pivot) |

---

## 5. التربة والمغذيات (Soil & Nutrients)

وحدات تحليل التربة وإدارة الأسمدة.

| الوحدة | الغرض |
|--------|--------|
| `soil_testing` | تفسير اختبار التربة والتوصيات |
| `soil_sensors` | معالجة بيانات حساسات التربة IoT والمحولات |
| `fertilizer_management` | توصيات المغذيات، تتبع المخزون، إدارة الأسمدة |

---

## 6. الآفات والأمراض (Pest & Disease)

وحدات اكتشاف الآفات وإدارة الأمراض والطقس.

| الوحدة | الغرض |
|--------|--------|
| `pest_scouting` | تحديد الآفات، الإدارة المتكاملة للآفات (IPM)، التحكم القائم على العتبات |
| `pesticide_compliance` | فترة ما قبل الحصاد (PHI)، تسجيل المبيدات، تنبيهات السلامة |
| `weather_alerts` | مراقبة الطقس، تحسين نافذة الرش، تنبيهات الظروف الخطرة |

---

## 7. الأعمال والعمليات (Business & Operations)

وحدات دعم العمليات التجارية للمزرعة والعمال والمعدات.

| الوحدة | الغرض |
|--------|--------|
| `mobile_sync` | المزامنة دون اتصال، حل التعارضات، المزامنة التدريجية (Delta Sync) |
| `batch_operations` | المعالجة الدفعية غير المتزامنة والجدولة |
| `labor_management` | جدولة القوى العاملة وإدارة السلامة |
| `equipment_maintenance` | دورة حياة المعدات والصيانة التنبؤية |
| `cooperatives` | إدارة الجمعيات التعاونية متعددة المزارع وتجميع الموارد |
| `market_prices` | تتبع أسعار السوق وتحليل الاتجاهات |
| `traceability` | تتبع سلسلة التوريد ورموز QR |
| `drone_integration` | تخطيط رحلات الطائرات المسيّرة وتطبيق المعدل المتغير (VRA) |
| `crop_insurance` | تأمين المحاصيل وتقييم المخاطر |
| `learning_marketplace` | تعليم المزارعين وتتبع التقدم |

---

## 8. التقنية المتقدمة (Advanced Technology)

الوحدات المبتكرة مثل Blockchain، الحافة السحابية، والأتمتة منخفضة الكود.

| الوحدة | الغرض |
|--------|--------|
| `smart_agriculture` | تتبع Blockchain، أتمتة IFTTT، وحدات التحكم PID |
| `edge_cloud` | بنية الحافة السحابية، الأنظمة التعاونية |
| `lowcode` | محرك أتمتة سير العمل منخفض/بدون كود |
| `scraping` | استخراج البيانات لأسعار السوق وبيانات الطقس |

---

## 9. الزراعة الدقيقة (Precision Agriculture)

وحدات الزراعة الدقيقة، المعايرة، والتوائم الرقمية.

| الوحدة | الغرض |
|--------|--------|
| `calibration` | معايرة الحساسات والمعدات |
| `digital_twin` | نماذج محاكاة التوأم الرقمي للمزارع والحقول |
| `drift_detection` | اكتشاف انحراف النموذج والبيانات |
| `vra_maps` | إنشاء خرائط تطبيق المعدل المتغير (Variable Rate Application) |
| `geospatial_metadata` | إدارة البيانات الوصفية الجغرافية المكانية |

---

## 10. التحليلات والمراقبة (Analytics & Monitoring)

وحدات لوحات التحكم والتقارير المالية ومراقبة الاستقرار.

| الوحدة | الغرض |
|--------|--------|
| `dashboard` | أدوات وأدوات مساعدة للوحات التحكم |
| `financial_reports` | التقارير المالية والتحليل |
| `iot_dashboard` | أدوات لوحة تحكم حساسات IoT |
| `marketplace_enhanced` | ميزات السوق المحسّنة |
| `stability` | مراقبة استقرار النظام والتنبيهات |

---

## 11. الإعدادات والتوجيه (Configuration & Routing)

وحدات إعداد الجوال، توجيه الإشعارات، وتعريفات العمليات.

| الوحدة | الغرض |
|--------|--------|
| `mobile_config` | إدارة إعدادات تطبيق الجوال |
| `notification_routing` | منطق توجيه الإشعارات والتسليم |
| `process_models` | تعريفات نماذج العمليات التجارية |
| `regional` | الملفات الشخصية الزراعية الإقليمية والبيانات |

---

## 12. الوحدات الإقليمية والامتثال (Regional & Compliance)

الوحدات الخاصة بمناطق جغرافية محددة وشهادات الامتثال.

| الوحدة | الغرض |
|--------|--------|
| `yemen` | البيانات الزراعية الخاصة باليمن (أصناف المحاصيل، المناخ، التربة) |
| `globalgap` | امتثال GlobalGAP IFA v6 وقوائم التحقق |

---

## 13. ملفات المستوى العلوي (Top-Level Files)

ملفات Python في جذر مجلد `shared/` تُستخدم بشكل مباشر عبر الخدمات.

| الملف | الغرض |
|-------|--------|
| `__init__.py` | ملف تهيئة الحزمة الرئيسية |
| `README.md` | توثيق نظرة عامة على الوحدات المشتركة |
| `cors_config.py` | إعداد CORS موحد لجميع خدمات FastAPI |
| `devops.py` | أدوات DevOps ومساعدات النشر |
| `errors_py.py` | معالجة الأخطاء الموحدة لـ FastAPI (`setup_exception_handlers`، `add_request_id_middleware`) |
| `logging_config.py` | إعداد التسجيل المهيكل (JSON) باستخدام structlog |
| `platform.py` | طبقة منصة متعددة المستأجرين v16.0.0 - عزل المستأجر الكامل عبر جميع طبقات البنية التحتية |
| `startup_checks.py` | فحوصات بدء تشغيل الخدمة (الاتصال بقاعدة البيانات، NATS، Redis) |

---

## ملاحظات الاستخدام

### نمط الاستيراد القياسي

```python
# المصادقة
from shared.auth.dependencies import get_current_user
from shared.auth.models import User

# الأحداث
from shared.events.subjects import SAHOOL_FIELD_CREATED, get_tenant_subject

# معالجة الأخطاء
from shared.errors_py import add_request_id_middleware, setup_exception_handlers

# التسجيل
from shared.logging_config import setup_logging

# منصة المستأجر
from shared.platform import TenantContext
```

### التقسيم حسب الطبقة المعمارية

- **طبقة البنية التحتية** (23 وحدة): المصادقة، التخزين المؤقت، قاعدة البيانات، الأحداث، المراقبة، الأمان
- **طبقة الذكاء الاصطناعي** (10 وحدات): الذكاء الاصطناعي، LLM، NLP، الأقمار الصناعية، الوكلاء، ML
- **طبقة منطق المجال الزراعي** (35+ وحدة): المحاصيل، الري، التربة، الآفات، الطقس، المعدات
- **طبقة التحليلات والأعمال** (15+ وحدة): لوحات التحكم، التقارير، العمليات، الأسواق
- **طبقة التكوين والأدوات** (6 ملفات علوية): CORS، DevOps، الأخطاء، التسجيل، المنصة، الفحوصات

### الترميز والتدويل

- جميع الوحدات تدعم **العربية/الإنجليزية** (ثنائية اللغة) في الرسائل والتوصيات
- جميع الوحدات تعتمد **عزل المستأجر** (Tenant Isolation) عبر `tenant_id` من مطالبة `tid` في JWT
- جميع الوحدات تتبع **بنية موجهة بالأحداث** عبر NATS مع أنماط `sahool.{domain}.{action}`

---

_آخر تحديث: أبريل 2026_

_إصدار المنصة: 16.0.0_

---

## مراجع إضافية

### المستندات ذات الصلة في المشروع

| المستند | المسار |
|---------|--------|
| الخريطة الرئيسية للخدمات | `docs/SERVICES_MAP.md` |
| توثيق خدمات Backend | `docs/BACKEND_SERVICES_DOCUMENTATION.md` |
| مرجع خدمات Docker | `docs/DOCKER_SERVICES_REFERENCE.md` |
| بوابة API | `docs/API_GATEWAY.md` |
| الأمان | `docs/SECURITY.md` |
| النشر | `docs/DEPLOYMENT.md` |
| الرصد والملاحظة | `docs/OBSERVABILITY.md` |
| كتاب التشغيل (Runbooks) | `docs/RUNBOOKS.md` |
| سجل الخدمات (Source of Truth) | `governance/services.yaml` |
| تعريف الوكلاء | `governance/agents.yaml` |

### أوامر التشغيل السريع

```bash
# البدء السريع للمطوّرين الجدد
make quickstart

# تشغيل البيئة الكاملة
make dev

# البنية التحتية فقط
make infra-up

# حالة الخدمات
make status
make health

# بناء كل الصور
make build

# السجلات
make logs
make logs-service SERVICE=<service-name>
```

### هيكل المستودع على مستوى عالٍ

```
sahool-unified-v15-idp/
├── apps/
│   ├── admin/          # بوابة الإدارة (React)
│   ├── web/            # لوحة Web (Next.js)
│   ├── mobile/         # تطبيق Flutter
│   ├── kernel/         # وحدات Python الأساسية
│   └── services/       # 73 خدمة مصغرة
├── packages/           # 27 حزمة npm مشتركة
├── shared/             # 89 وحدة Python مشتركة
├── docker/             # ملفات Docker base وأدوات compose
├── helm/               # Helm charts (24 chart)
├── infrastructure/     # IaC، مراقبة، Terraform
├── governance/         # سجل الخدمات والسياسات
├── idp/                # منصة المطوّر الداخلية (Backstage)
├── docs/               # 537+ ملف توثيق
└── tests/              # 19 فئة اختبارات
```

---

## خاتمة

هذا المستند يمثّل خريطة مرجعية شاملة لجميع مكوّنات منصة SAHOOL على مستوى الخدمات والحاويات والوحدات المشتركة. يُرجى الرجوع إلى المستندات المتخصصة المذكورة أعلاه للحصول على تفاصيل أعمق حول كل مكوّن على حدة.

**آخر تحديث**: 2026-04-10
