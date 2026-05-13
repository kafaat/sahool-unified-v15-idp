# مقارنة ميزات الخدمات المهملة مع بدائلها النشطة
# Deprecated Services Feature Comparison with Active Replacements

**آخر تحديث / Last Updated**: 2026-05-13  
**المرجع / Reference**: `governance/services.yaml`, `archive/deprecated-services/README.md`, `apps/services/DEPRECATION_SUMMARY.md`  
**الإصدار / Version**: v16.0.0

---

## ملخص تنفيذي / Executive Summary

تم تحليل جميع الخدمات المهملة والمؤرشفة (17 خدمة) في منصة SAHOOL. **لا توجد أي خدمة بدون بديل نشط ومحدد**. جميعها لديها `replaced_by` واضح في `governance/services.yaml`.

All 17 deprecated/archived services have been analyzed. **No service is left without a defined active replacement.** Every entry carries a clear `replaced_by` in `governance/services.yaml`.

| المجموعة | العدد | وصف |
|-----------|-------|-----|
| استبدال مباشر (نفس المنفذ) | 3 | Direct replacement, same port |
| دمج خدمات متعددة | 7 | Multiple services consolidated |
| ترقية تقنية | 4 | Technical upgrade |
| تغيير المنصة | 3 | Platform change |
| **المجموع** | **17** | |

---

## المجموعة 1: استبدال مباشر — نفس المنفذ
## Group 1: Direct Replacement — Same Port

### 1. `weather-advanced` → `weather-service`

| البند | القديم | الجديد |
|-------|--------|--------|
| المنفذ | 8092 | 8092 |
| الحالة | archived | active |
| مسار governance | `archive/deprecated-services/weather-advanced` | `apps/services/weather-service` |
| تاريخ التقادم | 2025-01-01 | — |
| تاريخ الأرشفة | 2025-06-01 | — |

**الميزات المضافة في البديل:**
- 9 نقاط نهاية متقدمة: evapotranspiration, GDD, spray window, frost risk, heat stress, chill hours, drought index
- حدث NATS: `WeatherForecastReady.v1`
- تكامل مباشر مع weather-alerts وirrigation-smart

**ملاحظة:** ⚠️ OVERDUE — تجاوز تاريخ الغروب بأكثر من 9 أشهر.

---

### 2. `crop-health-ai` → `crop-intelligence-service`

| البند | القديم | الجديد |
|-------|--------|--------|
| المنفذ | 8095 | 8095 |
| الحالة | archived | active |
| مسار governance | `archive/deprecated-services/crop-health-ai` | `apps/services/crop-intelligence-service` |
| تاريخ التقادم | 2025-01-01 | — |

**الميزات المضافة في البديل:**
- أحداث NATS: `CropHealthAssessed.v1`, `DiseaseDetected.v1`
- يستهلك: `IndexTileReady.v1`, `SatelliteSceneIngested.v1`
- تكامل مع `vegetation-analysis-service`
- اكتشاف أمراض متقدم عبر التعلم الآلي

**ملاحظة:** ⚠️ OVERDUE — تجاوز تاريخ الغروب بأكثر من 9 أشهر.

---

### 3. `satellite-service` → `vegetation-analysis-service`

| البند | القديم | الجديد |
|-------|--------|--------|
| المنفذ | 8090 | 8090 |
| الحالة | archived | active |
| مسار governance | `archive/deprecated-services/satellite-service` | `apps/services/vegetation-analysis-service` |
| تاريخ التقادم | 2025-01-01 | — |

**الميزات المضافة في البديل:**
- 70+ نقطة نهاية مقابل المحدودة في satellite-service
- أحداث NATS: `VegetationIndexCalculated.v1`, `NDVITimeseriesReady.v1`, `FieldBoundaryDetected.v1`
- يستهلك: `SatelliteSceneIngested.v1`, `WeatherDataReady.v1`
- تحليل متعدد المؤشرات (NDVI, EVI, NDRE, LCI, NDWI, SAVI)

**ملاحظة:** ⚠️ OVERDUE — تجاوز تاريخ الغروب بأكثر من 9 أشهر.

---

## المجموعة 2: دمج خدمات متعددة
## Group 2: Multiple Services Consolidated

### 4–6. `field-core` + `field-ops` + `field-service` → `field-management-service`

| البند | field-core | field-ops | field-service | البديل |
|-------|-----------|-----------|--------------|--------|
| المنفذ | 3005 | 8155 | 8156 | **3000** |
| الحالة | archived | archived | archived | active |
| تاريخ الأرشفة | 2026-01-25 | 2026-01-25 | 2026-01-25 | — |

**سبب الدمج:**
ثلاث خدمات كانت تتداخل في إدارة حقول المزارع. الدمج يقلل التعقيد ويوحد دورة حياة الحقل.

**الميزات المضافة في البديل:**
- أحداث NATS: `FieldCreated.v1`, `FieldUpdated.v1`, `FieldDeleted.v1`
- يستهلك: `NDVIProcessed.v1`, `WeatherDataReady.v1`
- NestJS مع Prisma ORM
- API موحد لجميع عمليات الحقول
- تكامل مع Redis وNATS

**مرجع الترحيل:** `docs/migrations/FIELD_OPS_MIGRATION_SUMMARY.md`

---

### 7. `fertilizer-advisor` → `advisory-service`

| البند | القديم | الجديد |
|-------|--------|--------|
| المنفذ | 9093 | 8093 |
| الحالة | archived | active |
| مسار governance | `archive/deprecated-services/fertilizer-advisor` | `apps/services/advisory-service` |
| تاريخ التقادم | 2025-01-01 | — |

**أحداث NATS القديمة:** `FertilizerPlanProposed.v1`  
**أحداث NATS الجديدة:** `AdvisoryGenerated.v1`, `FertilizerRecommendation.v1`

**الميزات المضافة في البديل:**
- يستهلك: `SoilAnalysisCompleted.v1`, `CropHealthAssessed.v1`, `WeatherForecastReady.v1`
- استشارات أسمدة **ضمن منظومة استشارية أشمل** (لا استشارات أسمدة فقط)
- دعم cache layer وrate limiting وpagination
- تكامل مع NATS وRedis

**مرجع الترحيل:** `docs/migrations/AGRO_ADVISOR_MIGRATION_SUMMARY.md`

---

### 8. `agro-advisor` → `advisory-service`

| البند | القديم | الجديد |
|-------|--------|--------|
| المنفذ | 8105 | 8093 |
| الحالة | archived | active |
| تاريخ الأرشفة | 2026-02-14 | — |

**أحداث NATS القديمة:** `AgroAdviceGenerated.v1`  
**أحداث NATS الجديدة:** `AdvisoryGenerated.v1`

**الميزات المضافة في البديل:**
- 21 نقطة نهاية من agro-advisor مغطاة بالكامل في advisory-service
- إضافة: cache layer, rate limiter, pagination, token revocation
- استشارات زراعية أشمل (أسمدة + محاصيل + ري)

**مرجع الترحيل:** `docs/migrations/AGRO_ADVISOR_MIGRATION_SUMMARY.md`

---

### 9. `crop-health` → `crop-intelligence-service`

| البند | القديم | الجديد |
|-------|--------|--------|
| المنفذ | 8100 | 8095 |
| الحالة | archived | active |
| تاريخ الأرشفة | 2026-01-25 | — |

**الميزات المضافة في البديل:**
- مراقبة صحة المحاصيل المبنية على منطقة (zone-based)
- مؤشرات نباتية متعددة (NDVI, EVI, NDRE, LCI, NDWI, SAVI)
- تصدير VRT
- اكتشاف أمراض عبر نماذج ذكاء اصطناعي متقدمة
- أحداث NATS: `CropHealthAssessed.v1`, `DiseaseDetected.v1`

---

### 10. `ndvi-engine` → `vegetation-analysis-service`

| البند | القديم | الجديد |
|-------|--------|--------|
| المنفذ | 8107 | 8090 |
| الحالة | archived | active |
| تاريخ الأرشفة | 2026-02-14 | — |

**أحداث NATS القديمة:** `NDVICalculated.v1`  
**أحداث NATS الجديدة:** `VegetationIndexCalculated.v1`, `NDVITimeseriesReady.v1`

**الميزات المضافة في البديل:**
- جميع نقاط نهاية ndvi-engine مغطاة في vegetation-analysis-service (70+ نقطة نهاية)
- إضافة: confidence scoring, cloud cover detection, advanced caching, analytics
- تحليل السلاسل الزمنية (time-series) لـ NDVI
- اكتشاف الشذوذات (anomaly detection)
- تحليل المناطق (zone analysis)

---

## المجموعة 3: ترقية تقنية
## Group 3: Technical Upgrade

### 11. `yield-prediction` → `yield-prediction-service`

| البند | القديم | الجديد |
|-------|--------|--------|
| المنفذ | 3021 | **8152** |
| الحالة | deprecated (profiles: [deprecated]) | active |
| مسار compose | `apps/services/yield-prediction` | `apps/services/yield-prediction-service` |
| ORM | بدون | **Prisma** |
| Rate Limiting | بدون | **@nestjs/throttler** (3 مستويات) |

**أحداث NATS:** `YieldPredicted.v1`

**التحسينات التقنية:**
- قاعدة الكود **متطابقة 100%** لكن yield-prediction-service يضيف:
  - `@prisma/client` ORM للتخزين المنظم
  - `@nestjs/throttler` بثلاثة مستويات من تحديد المعدل
  - بنية NestJS أكثر استقراراً
- يعتمد على: `crop-growth-model`, `weather-service`, Redis

**ملاحظة مهمة:** `yield-prediction-service` ما زال يُدرج `crop-growth-model` كتبعية في `governance/services.yaml`. تحقق من هذه التبعية قبل الحذف النهائي لـ `crop-growth-model`.

---

### 12. `yield-engine` → `yield-prediction-service`

| البند | القديم | الجديد |
|-------|--------|--------|
| المنفذ | 8098 | 8152 |
| الحالة | archived | active |
| تاريخ الأرشفة | 2026-02-19 | — |

**أحداث NATS القديمة:** `YieldEstimated.v1`  
**أحداث NATS الجديدة:** `YieldPredicted.v1`

**الميزات المضافة في البديل:**
- من محرك تقدير (estimation) إلى خدمة تنبؤ (prediction) قائمة على التعلم الآلي
- يستهلك: `FieldIndicatorsComputed.v1`, `WeatherForecastReady.v1`
- نماذج تنبؤ محسّنة

---

### 13. `lai-estimation` → `vegetation-analysis-service`

| البند | القديم | الجديد |
|-------|--------|--------|
| المنفذ | 3022 | 8090 |
| الحالة | deprecated (profiles: [deprecated]) | active |
| نوع الخدمة | Node.js | Python |

**الميزات المضافة في البديل:**
- تقدير مؤشر مساحة الأوراق (LAI) مدمج مع تحليل الغطاء النباتي
- سياق أشمل: NDVI + EVI + LAI في نفس الاستجابة
- تخزين مؤقت أفضل عبر Redis

---

### 14. `crop-growth-model` → `advisory-service`

| البند | القديم | الجديد |
|-------|--------|--------|
| المنفذ | 3023 | 8093 |
| الحالة | deprecated (profiles: [deprecated]) | active |
| نوع الخدمة | Node.js | Python |

**الميزات المضافة في البديل:**
- نمذجة نمو المحاصيل مدمجة في استشارات زراعية عملية
- من نموذج معزول إلى توصيات قابلة للتنفيذ مباشرة
- يستهلك: `SoilAnalysisCompleted.v1`, `CropHealthAssessed.v1`, `WeatherForecastReady.v1`

**⚠️ تحذير تبعية:** `yield-prediction-service` يُدرج هذه الخدمة كتبعية. يجب التحقق قبل الحذف النهائي.

---

## المجموعة 4: تغيير المنصة
## Group 4: Platform Change

### 15. `wechat-service` → `community-service`

| البند | القديم | الجديد |
|-------|--------|--------|
| المنفذ | 8135 (كان 8133) | **8133** |
| الحالة | deprecated (profiles: [deprecated]) | active |
| المنصة | WeChat (خاص/مدفوع) | **Rocket.Chat (مفتوح المصدر)** |
| تاريخ التقادم | 2026-03-13 | — |

**سبب الاستبدال:**
- التحرر من منصة WeChat الخاصة وقيودها الجغرافية
- Rocket.Chat self-hosted يوفر خصوصية كاملة للبيانات
- دعم بوتات الاستشارة الزراعية

**الميزات المضافة في البديل:**
- أحداث NATS: `CommunityChannelCreated.v1`, `CommunityUserJoined.v1`, `CommunityMessagePosted.v1`, `CommunityAdvisoryPosted.v1`, `CommunityAlertPosted.v1`, `CommunityTenantSetup.v1`
- يستهلك: أحداث الإشعارات والاستشارات والتنبيهات
- قنوات موضوعية (topic channels) لمجتمعات المزارعين
- مجموعات التعاونيات
- بوتات إرشاد زراعي

**مرجع:** `archive/deprecated-services/wechat-service/DEPRECATION_NOTICE.md`

---

### 16. `community-chat` → `chat-service`

| البند | القديم | الجديد |
|-------|--------|--------|
| المنفذ | 8097 | 8115 |
| الحالة | archived | active |
| تاريخ الأرشفة | 2026-01-15 | — |

**أحداث NATS القديمة:** `CommunityPostCreated.v1`  
**أحداث NATS الجديدة:** `ChatMessageSent.v1`, `ChatRoomCreated.v1`

**الميزات المضافة في البديل:**
- من منتديات مجتمعية (posts/threads) إلى مراسلة فورية (real-time chat)
- دعم الرد الفوري farmer-to-expert
- يستهلك: `UserAuthenticated.v1`
- NestJS مع PostgreSQL (`sahool_chat`)

---

### 17. `field-chat` → `chat-service`

| البند | القديم | الجديد |
|-------|--------|--------|
| المنفذ | 8099 | 8115 |
| الحالة | archived | active |
| تاريخ الأرشفة | 2026-01-15 | — |

**الميزات المضافة في البديل:**
- دمج قنوات الدردشة الخاصة بالحقول في منصة مراسلة موحدة
- نفس البديل لـ `community-chat`، إلغاء التداخل بين الخدمتين

---

## ملاحظات تشغيلية مهمة
## Important Operational Notes

### خدمات بـ `profiles: [deprecated]` — قيد الاستخدام المحدود

الخدمات التالية ما زالت موجودة في `docker-compose.yml` لكنها **لا تعمل افتراضياً**:

```bash
# لتشغيلها للاختبار فقط:
docker compose --profile deprecated up yield-prediction lai-estimation crop-growth-model ndvi-processor wechat-service
```

| الخدمة | المنفذ | docker-compose.yml |
|--------|--------|-------------------|
| `yield-prediction` | 3021 | `profiles: [deprecated]` — السطر 1593 |
| `lai-estimation` | 3022 | `profiles: [deprecated]` — السطر 1644 |
| `crop-growth-model` | 3023 | `profiles: [deprecated]` — السطر 1695 |
| `ndvi-processor` | 8118 | `profiles: [deprecated]` — السطر 3071 |
| `wechat-service` | 8135 | `profiles: [deprecated]` — السطر 3512 |

### تبعية حرجة تستدعي الانتباه

```
yield-prediction-service (نشط) → يعتمد على → crop-growth-model (مهملة)
```

قبل الحذف النهائي لـ `crop-growth-model`، يجب:
1. التحقق من أن `yield-prediction-service` لا يستدعيها فعلياً في الكود
2. تحديث `governance/services.yaml` لإزالة التبعية
3. اختبار `yield-prediction-service` بعد الإزالة

---

## ملخص الحالة الكاملة
## Complete Status Summary

| الخدمة المهملة | البديل النشط | المنفذ القديم | المنفذ الجديد | الحالة | مجموعة |
|----------------|-------------|--------------|--------------|--------|---------|
| weather-advanced | weather-service | 8092 | 8092 | archived ⚠️ OVERDUE | 1 |
| crop-health-ai | crop-intelligence-service | 8095 | 8095 | archived ⚠️ OVERDUE | 1 |
| satellite-service | vegetation-analysis-service | 8090 | 8090 | archived ⚠️ OVERDUE | 1 |
| field-core | field-management-service | 3005 | 3000 | archived ✅ | 2 |
| field-ops | field-management-service | 8155 | 3000 | archived ✅ | 2 |
| field-service | field-management-service | 8156 | 3000 | archived ✅ | 2 |
| fertilizer-advisor | advisory-service | 9093 | 8093 | archived ✅ | 2 |
| agro-advisor | advisory-service | 8105 | 8093 | archived ✅ | 2 |
| crop-health | crop-intelligence-service | 8100 | 8095 | archived ✅ | 2 |
| ndvi-engine | vegetation-analysis-service | 8107 | 8090 | archived ✅ | 2 |
| yield-prediction | yield-prediction-service | 3021 | 8152 | deprecated 🔒 | 3 |
| yield-engine | yield-prediction-service | 8098 | 8152 | archived ✅ | 3 |
| lai-estimation | vegetation-analysis-service | 3022 | 8090 | deprecated 🔒 | 3 |
| crop-growth-model | advisory-service | 3023 | 8093 | deprecated 🔒 ⚠️ تبعية | 3 |
| wechat-service | community-service | 8135 | 8133 | deprecated 🔒 | 4 |
| community-chat | chat-service | 8097 | 8115 | archived ✅ | 4 |
| field-chat | chat-service | 8099 | 8115 | archived ✅ | 4 |

**المفتاح:**
- ✅ archived: مؤرشفة بالكامل، لا تعمل
- 🔒 deprecated: موجودة في compose لكن opt-in فقط (`--profile deprecated`)
- ⚠️ OVERDUE: تجاوزت تاريخ الغروب المحدد، تحتاج إجراء فوري
- ⚠️ تبعية: تحتاج تحققاً قبل الحذف النهائي

---

## الخطوات التالية الموصى بها
## Recommended Next Steps

### الأولوية القصوى — إجراء فوري
1. **weather-advanced, crop-health-ai, satellite-service**: تجاوزت تاريخ الغروب بأكثر من 9 أشهر. يجب التأكد من عدم وجود أي استدعاء نشط لها ثم حذفها نهائياً.

### الأولوية المتوسطة — خلال Sprint القادم
2. **crop-growth-model**: التحقق من أن `yield-prediction-service` لا تستدعيها، ثم تحديث التبعية في governance وحذفها.
3. **yield-prediction, lai-estimation**: التأكد من ترحيل جميع المستهلكين، ثم حذفها من compose.

### الأولوية المنخفضة — خلال الإصدار التالي
4. **wechat-service**: استكمال ترحيل جميع مستخدمي WeChat إلى community-service، ثم الحذف النهائي.
5. **ndvi-processor**: (موجودة في apps/services وليس في archive فقط) — تأكيد الأرشفة الكاملة.

---

*تم إنشاء هذا المستند بناءً على تحليل شامل لـ `governance/services.yaml`, `docker-compose.yml`, `archive/deprecated-services/README.md`, وكود الخدمات.*
