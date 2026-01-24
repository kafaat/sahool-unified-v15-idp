# Admin-Kong Services Mapping | ربط خدمات Kong بلوحة الإدارة

> تقرير تحليلي للتحقق من ارتباط خدمات Kong بتطبيق Admin
>
> **تاريخ التحليل**: 2026-01-24
> **المصادر**:
> - `apps/admin/src/config/api.ts`
> - `apps/admin/src/lib/api.ts`
> - `apps/admin/src/lib/api-gateway/index.ts`
> - `services-definition.md`

---

## ملخص تنفيذي | Executive Summary

| البند | العدد |
|-------|-------|
| **إجمالي خدمات Kong** | 62 |
| **الخدمات المستخدمة في Admin** | 17 |
| **الخدمات غير المستخدمة في Admin** | 45 |
| **نسبة التغطية** | 27.4% |

---

## 1. الخدمات المتصلة بـ Admin | Connected Services

### 1.1 الخدمات المستخدمة فعلياً (Active Usage)

| الخدمة في Admin | Kong Service | المنفذ | الملفات المستخدمة | نقاط النهاية |
|----------------|--------------|--------|-------------------|--------------|
| `fieldCore` | field-management-service | 3000 | `api.ts` | `/api/v1/fields`, `/api/v1/fields/:id` |
| `indicators` | indicators-service | 8091 | `api.ts` | `/api/v1/indicators/dashboard` |
| `cropHealth` | crop-intelligence-service | 8095 | `api.ts` | `/api/v1/crop-health/diagnoses`, `/diagnoses/stats`, `/diagnoses/:id` |
| `weatherCore` | weather-core | 8108 | `api.ts` | `/weather/current`, `/weather/forecast`, `/weather/agricultural-report` |
| `weather` | weather-service | 8092 | `api.ts`, `precision.ts` | `/v1/current/:id`, `/v1/forecast/:id`, `/v1/locations`, `/v1/alerts/:id`, `/v1/gdd`, `/v1/spray-windows` |
| `virtualSensors` | virtual-sensors | 8119 | `api.ts`, `sensors/page.tsx` | `/api/v1/iot/readings/:farmId`, `/v1/farms/readings` |
| `notifications` | notification-service | 8110 | `api.ts` | `/api/v1/notifications`, `/notifications/:id/read` |
| `task` | task-service | 8103 | `api.ts` | `/api/v1/tasks`, `/tasks/:id` |
| `community` | community-chat | 8097 | `api.ts` | `/api/v1/posts` |
| `equipment` | equipment-service | 8101 | `api.ts` | `/api/v1/equipment` |
| `satellite` | vegetation-analysis-service | 8090 | `api.ts`, `analytics.ts` | `/v1/timeseries/:id`, `/v1/analyze`, `/v1/indices/:id`, `/v1/satellites`, `/v1/analysis`, `/v1/ndvi-trends` |
| `yieldEngine` | yield-prediction-service / yield-engine | 8098 | `yield/page.tsx`, `analytics.ts` | `/v1/predict`, `/v1/profitability` |
| `fertilizer` | advisory-service | 8093 | `precision.ts` | `/v1/prescriptions`, `/prescriptions/:id/approve`, `/prescriptions/:id/reject`, `/v1/spray-history` |
| `irrigation` | irrigation-smart | 8094 | `irrigation/page.tsx` | `/v1/calculate`, `/v1/water-balance/:id`, `/v1/methods`, `/v1/crops` |
| `communityChat` | community-chat | 8097 | `support/page.tsx` | `/v1/stats`, `/v1/requests` |

### 1.2 الخدمات المُعرَّفة في Config فقط (Defined but Limited Usage)

| الخدمة في Admin | Kong Service | المنفذ | حالة الاستخدام |
|----------------|--------------|--------|----------------|
| `auth` | user-service | 8080 | معرَّفة - تستخدم للمصادقة |
| `users` | user-service | 3025 | معرَّفة - إدارة المستخدمين |
| `wsGateway` | ws-gateway | 8081 | معرَّفة - WebSocket |
| `ndviEngine` | ~~ndvi-engine~~ (deprecated) | 8107 | معرَّفة - مهملة |
| `analytics` | crop-health (basic) | 8100 | معرَّفة - تحليلات أساسية |
| `providerConfig` | provider-config | 8104 | معرَّفة - تكوين المزودين |
| `alerts` | alert-service | 8113 | معرَّفة - التنبيهات |
| `reports` | - | 8084 | معرَّفة - غير موجودة في Kong |
| `lab` | community-chat | 8097 | معرَّفة - نفس منفذ community |
| `epidemic` | yield-prediction-service | 8098 | معرَّفة - نفس منفذ yieldEngine |

---

## 2. الخدمات غير المتصلة بـ Admin | Unconnected Services

### 2.1 خدمات الأعمال (Business Services) - غير مستخدمة

| Kong Service | المنفذ | الوصف | سبب عدم الاتصال المحتمل |
|--------------|--------|-------|------------------------|
| `marketplace-service` | 3010 | السوق الزراعي | ميزة مستقلة غير مدمجة في Admin |
| `research-core` | 3015 | البحث العلمي | وظيفة متخصصة للباحثين |
| `disaster-assessment` | 3020 | تقييم الكوارث | ميزة طوارئ منفصلة |
| `chat-service` | 8000 | الدردشة | استخدام community-chat بدلاً منه |
| `billing-core` | 8089 | الفوترة | نظام فوترة مستقل |
| `inventory-service` | 8116 | المخزون | غير مدمج في لوحة Admin |

### 2.2 خدمات الذكاء الاصطناعي (AI Services) - غير مستخدمة

| Kong Service | المنفذ | الوصف | سبب عدم الاتصال المحتمل |
|--------------|--------|-------|------------------------|
| `ai-advisor` | 8112 | المستشار الذكي | ميزة متقدمة قيد التطوير |
| `agro-advisor` | 8105 | المستشار الزراعي | تكامل مستقبلي |
| `field-chat` | 8099 | دردشة الحقل | ميزة chatbot منفصلة |
| `field-intelligence` | 8120 | ذكاء الحقل | تكامل مستقبلي |
| `skills-service` | 8121 | المهارات | تدريب المزارعين - منفصل |
| `code-review-service` | 8102 | مراجعة الكود | أداة داخلية للمطورين |

### 2.3 خدمات الوكلاء (Agent Services) - غير مستخدمة

| Kong Service | المنفذ | الوصف | سبب عدم الاتصال المحتمل |
|--------------|--------|-------|------------------------|
| `agent-registry` | 8160 | سجل الوكلاء | بنية تحتية AI |
| `ai-agents-core` | 8122 | نواة الوكلاء | بنية تحتية AI |
| `ai-agents-service` | 8130 | تنسيق الوكلاء | بنية تحتية AI |
| `knowledge-graph` | 8140 | رسم المعرفة | بنية تحتية AI |
| `mcp-server` | 8200 | Model Context Protocol | بنية تحتية AI |

### 2.4 خدمات IoT والبنية التحتية - غير مستخدمة

| Kong Service | المنفذ | الوصف | سبب عدم الاتصال المحتمل |
|--------------|--------|-------|------------------------|
| `iot-service` | 8117 | إدارة الأجهزة | Admin يستخدم virtual-sensors |
| `iot-gateway` | 8106 | بوابة IoT | بنية تحتية داخلية |
| `astronomical-calendar` | 8111 | التقويم الفلكي | ميزة ثانوية |

### 2.5 خدمات جديدة - غير مستخدمة

| Kong Service | المنفذ | الوصف | سبب عدم الاتصال المحتمل |
|--------------|--------|-------|------------------------|
| `audit-service` | 8114 | التدقيق | تكامل مستقبلي |
| `crm-service` | 8131 | CRM | نظام مستقل |
| `lowcode-engine` | 8132 | التطوير السريع | أداة داخلية |
| `wechat-service` | 8133 | WeChat | سوق صيني محدد |
| `globalgap-compliance` | 8123 | GlobalGAP | شهادات متخصصة |
| `logistics-service` | 8162 | اللوجستيات | نظام مستقل |
| `ussd-gateway` | 8163 | USSD | قنوات بديلة |

### 2.6 الخدمات المهملة (Deprecated) - يجب عدم استخدامها

| Kong Service | المنفذ | البديل |
|--------------|--------|--------|
| `yield-prediction` | 3021 | `yield-prediction-service` |
| `lai-estimation` | 3022 | `indicators-service` |
| `crop-growth-model` | 3023 | `crop-intelligence-service` |
| `field-ops` | 8080 | `field-management-service` |
| `ndvi-engine` | 8107 | `vegetation-analysis-service` |
| `field-service` | 8115 | `field-management-service` |
| `ndvi-processor` | 8118 | `vegetation-analysis-service` |
| `satellite-service` | 9190 | `vegetation-analysis-service` |
| `weather-advanced` | 9092 | `weather-service` |
| `crop-health-ai` | 9095 | `crop-intelligence-service` |
| `fertilizer-advisor` | 9093 | `advisory-service` |

---

## 3. تحليل الفجوات | Gap Analysis

### 3.1 فجوات في التكامل

| الفئة | الخدمات المفقودة | الأولوية | التأثير |
|-------|-----------------|---------|--------|
| **الفوترة** | billing-core | عالية | لا يمكن إدارة الاشتراكات من Admin |
| **المخزون** | inventory-service | متوسطة | لا يمكن تتبع المخزون |
| **التدقيق** | audit-service | عالية | لا يمكن مراجعة سجلات الأمان |
| **التنبيهات** | alert-service (active usage) | عالية | محدودية في إدارة التنبيهات |
| **السوق** | marketplace-service | منخفضة | ميزة منفصلة |

### 3.2 تداخل في المنافذ (Port Conflicts)

| المنفذ | الخدمات | الملاحظة |
|--------|---------|---------|
| 8097 | `community-chat`, `lab` | نفس المنفذ لخدمتين مختلفتين في Admin |
| 8098 | `yield-prediction-service`, `yield-engine`, `epidemic` | ثلاث خدمات على نفس المنفذ |
| 3000 | `fieldCore`, `fieldManagement` | نفس الخدمة بأسماء مختلفة |

### 3.3 خدمات معرفة في Admin لكن غير موجودة في Kong

| الخدمة في Admin | المنفذ | الحالة |
|----------------|--------|--------|
| `reports` | 8084 | غير موجودة في kong.yml |

---

## 4. التوصيات | Recommendations

### 4.1 تكاملات مطلوبة (High Priority)

1. **billing-core (8089)**: إضافة واجهة إدارة الاشتراكات والفواتير
2. **audit-service (8114)**: إضافة صفحة سجلات التدقيق الأمني
3. **alert-service (8113)**: تفعيل الاستخدام الفعلي لإدارة التنبيهات
4. **inventory-service (8116)**: إضافة إدارة المخزون الزراعي

### 4.2 تنظيف مطلوب (Code Cleanup)

1. إزالة `ndviEngine` من التكوين (مهمل)
2. توحيد `lab` و `community` (نفس المنفذ)
3. توحيد `epidemic` و `yieldEngine` (نفس المنفذ)
4. إضافة `reports` service إلى Kong أو إزالتها من Admin

### 4.3 تكاملات مستقبلية (Medium Priority)

1. **AI Services**: ai-advisor, agro-advisor, field-intelligence
2. **Agent Services**: للمستخدمين المتقدمين
3. **GlobalGAP**: للمزارع التي تحتاج شهادات

---

## 5. مخطط الاتصال | Connection Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Admin Application                                   │
│                        (apps/admin/)                                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     Kong API Gateway (:8000)                                │
│                    https://api.sahool.sa/api/v1                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  ✅ CONNECTED    │    │  ⚠️ PARTIAL      │    │  ❌ NOT USED     │
│                  │    │                  │    │                  │
│ field-mgmt:3000  │    │ alert:8113       │    │ billing:8089     │
│ indicators:8091  │    │ users:3025       │    │ inventory:8116   │
│ crop-intel:8095  │    │ wsGateway:8081   │    │ marketplace:3010 │
│ weather:8092     │    │ provider:8104    │    │ ai-advisor:8112  │
│ weather-core:8108│    │                  │    │ agent-reg:8160   │
│ v-sensors:8119   │    │                  │    │ audit:8114       │
│ notifications:8110│   │                  │    │ iot-service:8117 │
│ task:8103        │    │                  │    │ knowledge:8140   │
│ community:8097   │    │                  │    │ mcp:8200         │
│ equipment:8101   │    │                  │    │ + 30 more...     │
│ satellite:8090   │    │                  │    │                  │
│ yield:8098       │    │                  │    │                  │
│ fertilizer:8093  │    │                  │    │                  │
│ irrigation:8094  │    │                  │    │                  │
└──────────────────┘    └──────────────────┘    └──────────────────┘
     15 services            4 services             43 services
```

---

## 6. ملفات Admin ذات الصلة | Relevant Admin Files

| الملف | الوصف | الخدمات المستخدمة |
|-------|-------|-------------------|
| `src/config/api.ts` | تكوين API المركزي | جميع الخدمات المعرفة |
| `src/lib/api.ts` | وظائف API الرئيسية | fieldCore, indicators, cropHealth, weather, weatherCore, virtualSensors, notifications, task, community, equipment, satellite |
| `src/lib/api/precision.ts` | API الزراعة الدقيقة | fertilizer, weather |
| `src/lib/api/analytics.ts` | API التحليلات | yieldEngine, satellite |
| `src/lib/api-gateway/index.ts` | API Gateway مع Circuit Breaker | 16 خدمة معرفة |
| `src/app/yield/page.tsx` | صفحة المحصول | yieldEngine |
| `src/app/irrigation/page.tsx` | صفحة الري | irrigation |
| `src/app/sensors/page.tsx` | صفحة المستشعرات | virtualSensors |
| `src/app/support/page.tsx` | صفحة الدعم | communityChat |

---

## 7. الخلاصة | Conclusion

تطبيق Admin يستخدم حالياً **27.4%** فقط من خدمات Kong المتاحة. الخدمات المستخدمة تركز على:

1. **إدارة الحقول**: field-management-service
2. **التحليلات**: indicators, satellite, crop-health
3. **الطقس**: weather, weather-core
4. **العمليات**: task, equipment, irrigation
5. **التواصل**: notifications, community

الخدمات غير المتصلة تمثل فرصاً للتوسع في:
- نظام الفوترة والاشتراكات
- الذكاء الاصطناعي والوكلاء
- إدارة المخزون والسوق
- التدقيق والامتثال

---

_آخر تحديث: 2026-01-24_
