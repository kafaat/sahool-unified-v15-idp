# Web-Kong Services Mapping | ربط خدمات Kong بتطبيق الويب

> تقرير تحليلي للتحقق من ارتباط خدمات Kong بتطبيق Web Dashboard
>
> **تاريخ التحليل**: 2026-01-24
> **المصادر**:
> - `apps/web/src/lib/api/client.ts`
> - `apps/web/src/features/*/api.ts`
> - `apps/web/src/lib/services/service-switcher.ts`
> - `services-definition.md`

---

## ملخص تنفيذي | Executive Summary

| البند | العدد |
|-------|-------|
| **إجمالي خدمات Kong** | 62 |
| **الخدمات المستخدمة في Web** | 31 |
| **الخدمات غير المستخدمة في Web** | 31 |
| **نسبة التغطية** | 50% |

---

## 1. الخدمات المتصلة بـ Web | Connected Services

### 1.1 خدمات المصادقة والمستخدمين (Auth & Users)

| الخدمة | Kong Service | نقاط النهاية المستخدمة |
|--------|--------------|------------------------|
| **auth** | user-service (3025) | `/api/v1/auth/login`, `/api/v1/auth/refresh`, `/api/v1/auth/me` |
| **users** | user-service (3025) | `/api/v1/users`, `/api/v1/users/:id`, `/api/v1/users/profile`, `/api/v1/users/settings/*` |

### 1.2 خدمات إدارة الحقول (Field Management)

| الخدمة | Kong Service | نقاط النهاية المستخدمة |
|--------|--------------|------------------------|
| **fields** | field-management-service (3000) | `/api/v1/fields`, `/api/v1/fields/:id`, `/api/v1/fields/nearby`, `/api/v1/fields/stats`, `/api/v1/fields/geojson`, `/api/v1/fields/sync` |
| **field-core** | field-core (3005) | `/api/v1/field-core/fields/:id/boundary`, `/api/v1/field-core/fields/:id/boundary-history` |
| **field-intelligence** | field-intelligence (8120) | `/api/v1/fields/:id/intelligence/score`, `/api/v1/fields/:id/intelligence/zones`, `/api/v1/fields/:id/intelligence/alerts`, `/api/v1/intelligence/*` |

### 1.3 خدمات الطقس (Weather Services)

| الخدمة | Kong Service | نقاط النهاية المستخدمة |
|--------|--------------|------------------------|
| **weather** | weather-service (8092) | `/api/v1/weather/v1/current/:id`, `/api/v1/weather/v1/forecast/:id`, `/api/v1/weather/v1/locations`, `/api/v1/weather/forecast` |
| **weather-core** | weather-core (8108) | `/api/v1/weather-core/weather/current`, `/api/v1/weather-core/weather/forecast`, `/api/v1/weather-core/weather/agricultural-report` |

### 1.4 خدمات التحليل والأقمار الصناعية (Analysis & Satellite)

| الخدمة | Kong Service | نقاط النهاية المستخدمة |
|--------|--------------|------------------------|
| **satellite** | vegetation-analysis-service (8090) | `/api/v1/satellite/v1/timeseries/:id`, `/api/v1/satellite/v1/analyze`, `/api/v1/satellite/v1/indices/:id`, `/api/v1/satellite/v1/satellites` |
| **ndvi** | vegetation-analysis-service (8090) | `/api/v1/ndvi/latest`, `/api/v1/ndvi/fields/:id`, `/api/v1/ndvi/fields/:id/timeseries`, `/api/v1/ndvi/fields/:id/map`, `/api/v1/ndvi/fields/:id/analyze`, `/api/v1/ndvi/summary`, `/api/v1/ndvi/stats/regional` |
| **analytics** | analytics-service | `/api/v1/analytics/summary`, `/api/v1/analytics/yield`, `/api/v1/analytics/cost`, `/api/v1/analytics/revenue`, `/api/v1/analytics/kpis`, `/api/v1/analytics/comparison`, `/api/v1/analytics/resources`, `/api/v1/analytics/reports/*` |

### 1.5 خدمات صحة المحاصيل والاستشارات (Crop Health & Advisory)

| الخدمة | Kong Service | نقاط النهاية المستخدمة |
|--------|--------------|------------------------|
| **crop-health** | crop-intelligence-service (8095) | `/api/v1/crop-health/analyze`, `/api/v1/crop-health/decision`, `/api/v1/crop-health/fields/:id/history`, `/api/v1/crop-health/summary`, `/api/v1/crop-health/records`, `/api/v1/crop-health/diagnoses`, `/api/v1/crop-health/diseases`, `/api/v1/crop-health/alerts`, `/api/v1/crop-health/consultations` |
| **fertilizer** | advisory-service (8093) | `/api/v1/fertilizer/recommend` |
| **advice** | advisory-service (8093) | `/api/v1/advice/recommendations`, `/api/v1/advice/ask`, `/api/v1/advice/history`, `/api/v1/advice/stats` |
| **agro-advisor** | agro-advisor (8105) | `/api/v1/agro-advisor/advice`, `/api/v1/agro-advisor/disease`, `/api/v1/agro-advisor/nutrients` |
| **agro-rules** | agro-rules (8151) | `/api/v1/agro-rules/fields/:id/rules`, `/api/v1/agro-rules/rules`, `/api/v1/agro-rules/rules/:id/trigger` |

### 1.6 خدمات الري والمحصول (Irrigation & Yield)

| الخدمة | Kong Service | نقاط النهاية المستخدمة |
|--------|--------------|------------------------|
| **irrigation** | irrigation-smart (8094) | `/api/v1/irrigation/fields/:id/recommendation`, `/api/v1/irrigation/et0` |
| **yield** | yield-prediction-service (8098) | `/api/v1/yield/fields/:id/predict`, `/api/v1/yield/fields/:id/history` |
| **action-windows** | - | `/api/v1/action-windows/spray`, `/api/v1/action-windows/irrigation`, `/api/v1/action-windows/recommendations` |

### 1.7 خدمات IoT والمستشعرات (IoT & Sensors)

| الخدمة | Kong Service | نقاط النهاية المستخدمة |
|--------|--------------|------------------------|
| **iot** | iot-service (8117) | `/api/v1/iot/fields/:id/sensors`, `/api/v1/iot/sensors/:id/history`, `/api/v1/iot/sensors`, `/api/v1/iot/sensors/readings`, `/api/v1/iot/sensors/stats`, `/api/v1/iot/sensors/stream`, `/api/v1/iot/actuators`, `/api/v1/iot/alert-rules` |

### 1.8 خدمات المهام والمعدات (Tasks & Equipment)

| الخدمة | Kong Service | نقاط النهاية المستخدمة |
|--------|--------------|------------------------|
| **tasks** | task-service (8103) | `/api/v1/tasks`, `/api/v1/tasks/:id`, `/api/v1/tasks/:id/complete`, `/api/v1/tasks/:id/status` |
| **equipment** | equipment-service (8101) | `/api/v1/equipment`, `/api/v1/equipment/:id`, `/api/v1/equipment/:id/location`, `/api/v1/equipment/maintenance`, `/api/v1/equipment/stats` |

### 1.9 خدمات التنبيهات والإشعارات (Alerts & Notifications)

| الخدمة | Kong Service | نقاط النهاية المستخدمة |
|--------|--------------|------------------------|
| **alerts** | alert-service (8113) | `/api/v1/alerts`, `/api/v1/alerts/:id`, `/api/v1/alerts/:id/acknowledge`, `/api/v1/alerts/:id/resolve`, `/api/v1/alerts/:id/dismiss`, `/api/v1/alerts/stats`, `/api/v1/alerts/bulk/*`, `/api/v1/alerts/stream`, `/api/v1/alerts/count` |

### 1.10 خدمات المجتمع والتواصل (Community & Communication)

| الخدمة | Kong Service | نقاط النهاية المستخدمة |
|--------|--------------|------------------------|
| **community** | community-chat (8097) | `/api/v1/community/posts`, `/api/v1/community/posts/trending`, `/api/v1/community/posts/saved`, `/api/v1/community/posts/:id/comments`, `/api/v1/community/posts/:id/like`, `/api/v1/community/groups`, `/api/v1/community/experts`, `/api/v1/community/expert-questions` |
| **field-chat** | field-chat (8099) | `/api/v1/field-chat/fields/:id/messages`, `/api/v1/field-chat/fields/:id/participants` |

### 1.11 خدمات الأعمال (Business Services)

| الخدمة | Kong Service | نقاط النهاية المستخدمة |
|--------|--------------|------------------------|
| **marketplace** | marketplace-service (3010) | `/api/v1/marketplace/listings`, `/api/v1/marketplace/products`, `/api/v1/marketplace/categories`, `/api/v1/marketplace/orders`, `/api/v1/marketplace/cart`, `/api/v1/marketplace/products/:id/reviews` |
| **billing** | billing-core (8089) | `/api/v1/billing/tenants/:id/subscription`, `/api/v1/billing/tenants/:id/invoices`, `/api/v1/billing/tenants/:id/usage` |
| **disasters** | disaster-assessment (3020) | `/api/v1/disasters/assess`, `/api/v1/disasters/alerts` |

### 1.12 خدمات أخرى (Other Services)

| الخدمة | Kong Service | نقاط النهاية المستخدمة |
|--------|--------------|------------------------|
| **reports** | - | `/api/v1/reports`, `/api/v1/reports/generate`, `/api/v1/reports/templates`, `/api/v1/reports/schedule`, `/api/v1/reports/field/generate`, `/api/v1/reports/season/generate` |
| **dashboard** | - | `/api/v1/dashboard`, `/api/v1/dashboard/stats`, `/api/v1/dashboard/weather`, `/api/v1/dashboard/activity`, `/api/v1/dashboard/tasks/upcoming`, `/api/v1/dashboard/alerts` |
| **scouting** | - | `/api/v1/scouting/sessions`, `/api/v1/scouting/observations`, `/api/v1/scouting/photos`, `/api/v1/scouting/statistics` |
| **astronomical** | astronomical-calendar (8111) | `/api/v1/astronomical/*` |
| **providers** | provider-config (8104) | `/api/v1/providers`, `/api/v1/providers/:id/config` |

---

## 2. الخدمات غير المتصلة بـ Web | Unconnected Services

### 2.1 خدمات الوكلاء (Agent Services) - غير مستخدمة

| Kong Service | المنفذ | الوصف |
|--------------|--------|-------|
| `agent-registry` | 8160 | سجل الوكلاء |
| `ai-agents-core` | 8122 | نواة الوكلاء |
| `ai-agents-service` | 8130 | تنسيق الوكلاء |
| `knowledge-graph` | 8140 | رسم المعرفة |
| `mcp-server` | 8200 | Model Context Protocol |
| `skills-service` | 8121 | المهارات |

### 2.2 خدمات متقدمة - غير مستخدمة

| Kong Service | المنفذ | الوصف |
|--------------|--------|-------|
| `ai-advisor` | 8112 | المستشار الذكي (يُستخدم agro-advisor بدلاً منه) |
| `research-core` | 3015 | البحث العلمي |
| `code-review-service` | 8102 | مراجعة الكود (داخلي) |

### 2.3 خدمات جديدة - غير مستخدمة

| Kong Service | المنفذ | الوصف |
|--------------|--------|-------|
| `audit-service` | 8114 | التدقيق |
| `crm-service` | 8131 | CRM |
| `lowcode-engine` | 8132 | التطوير السريع |
| `wechat-service` | 8133 | تكامل WeChat |
| `globalgap-compliance` | 8123 | شهادة GlobalGAP |
| `logistics-service` | 8162 | اللوجستيات |
| `ussd-gateway` | 8163 | بوابة USSD |
| `inventory-service` | 8116 | إدارة المخزون |

### 2.4 خدمات الإشعارات والبوابات - غير مستخدمة مباشرة

| Kong Service | المنفذ | الملاحظة |
|--------------|--------|---------|
| `notification-service` | 8110 | يُستخدم عبر WebSocket |
| `ws-gateway` | 8081 | WebSocket داخلي |
| `iot-gateway` | 8106 | بوابة IoT داخلية |
| `virtual-sensors` | 8119 | مستشعرات افتراضية (يُستخدم iot بدلاً منه) |
| `indicators-service` | 8091 | (يُستخدم ndvi بدلاً منه) |

### 2.5 الخدمات المهملة (لا يجب استخدامها)

| Kong Service | البديل |
|--------------|--------|
| `yield-prediction` (3021) | `yield-prediction-service` |
| `lai-estimation` (3022) | `indicators-service` |
| `crop-growth-model` (3023) | `crop-intelligence-service` |
| `field-ops` (8080) | `field-management-service` |
| `ndvi-engine` (8107) | `vegetation-analysis-service` |
| `field-service` (8115) | `field-management-service` |
| `ndvi-processor` (8118) | `vegetation-analysis-service` |
| `satellite-service` (9190) | `vegetation-analysis-service` |
| `weather-advanced` (9092) | `weather-service` |
| `crop-health-ai` (9095) | `crop-intelligence-service` |
| `fertilizer-advisor` (9093) | `advisory-service` |

---

## 3. مقارنة Web vs Admin | Comparison

| الخدمة | Web | Admin | الملاحظة |
|--------|-----|-------|---------|
| field-management-service | ✅ | ✅ | كلاهما |
| weather-service | ✅ | ✅ | كلاهما |
| weather-core | ✅ | ✅ | كلاهما |
| crop-intelligence-service | ✅ | ✅ | كلاهما |
| task-service | ✅ | ✅ | كلاهما |
| equipment-service | ✅ | ✅ | كلاهما |
| advisory-service | ✅ | ✅ | كلاهما |
| irrigation-smart | ✅ | ✅ | كلاهما |
| alert-service | ✅ | ⚠️ | Web أكثر تكاملاً |
| community-chat | ✅ | ✅ | كلاهما |
| **marketplace-service** | ✅ | ❌ | Web فقط |
| **billing-core** | ✅ | ❌ | Web فقط |
| **disaster-assessment** | ✅ | ❌ | Web فقط |
| **iot-service** | ✅ | ❌ | Web فقط |
| **agro-advisor** | ✅ | ❌ | Web فقط |
| **agro-rules** | ✅ | ❌ | Web فقط |
| **field-chat** | ✅ | ❌ | Web فقط |
| **field-intelligence** | ✅ | ❌ | Web فقط |
| **astronomical-calendar** | ✅ | ❌ | Web فقط |
| yield-prediction-service | ✅ | ✅ | كلاهما |
| vegetation-analysis-service | ✅ | ✅ | كلاهما |
| indicators-service | ❌ | ✅ | Admin فقط |
| virtual-sensors | ❌ | ✅ | Admin فقط |
| notification-service | ❌ | ✅ | Admin فقط |

---

## 4. ملفات Web ذات الصلة | Relevant Web Files

### 4.1 ملفات API الرئيسية

| الملف | الوصف | الخدمات |
|-------|-------|---------|
| `src/lib/api/client.ts` | عميل API الموحد | جميع الخدمات الأساسية |
| `src/lib/services/service-switcher.ts` | محول الخدمات | ndvi, weather, fertilizer, irrigation, crop-health, alerts, tasks, equipment |

### 4.2 ملفات Features API

| الملف | الخدمات المستخدمة |
|-------|-------------------|
| `src/features/fields/api.ts` | fields, field-core, field-intelligence |
| `src/features/weather/hooks/useWeather.ts` | weather, weather-core |
| `src/features/crop-health/api.ts` | crop-health |
| `src/features/iot/api.ts` | iot (sensors, actuators, alert-rules) |
| `src/features/tasks/api.ts` | tasks |
| `src/features/equipment/api.ts` | equipment |
| `src/features/alerts/api.ts` | alerts |
| `src/features/community/api.ts` | community |
| `src/features/marketplace/api.ts` | marketplace |
| `src/features/analytics/api.ts` | analytics |
| `src/features/ndvi/api.ts` | ndvi (satellite) |
| `src/features/advisor/api.ts` | advice (advisory-service) |
| `src/features/home/api.ts` | dashboard |
| `src/features/wallet/api.ts` | billing |
| `src/features/settings/api.ts` | users |
| `src/features/reports/api.ts` | reports |
| `src/features/scouting/api/scouting-api.ts` | scouting |
| `src/features/team/api/team-api.ts` | users |
| `src/features/action-windows/api/action-windows-api.ts` | fields, weather, action-windows |
| `src/features/astronomical/api.ts` | astronomical |

---

## 5. مخطط الاتصال | Connection Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Web Application                                     │
│                        (apps/web/)                                          │
│                                                                             │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │   Fields    │ │   Weather   │ │ Crop Health │ │     IoT     │           │
│  │   Feature   │ │   Feature   │ │   Feature   │ │   Feature   │           │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘           │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │    Tasks    │ │  Equipment  │ │   Alerts    │ │  Community  │           │
│  │   Feature   │ │   Feature   │ │   Feature   │ │   Feature   │           │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘           │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │ Marketplace │ │  Analytics  │ │   Reports   │ │   Wallet    │           │
│  │   Feature   │ │   Feature   │ │   Feature   │ │   Feature   │           │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘           │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     Kong API Gateway (:8000)                                │
│                    NEXT_PUBLIC_API_URL                                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
    ┌───────────────────────────────┼───────────────────────────────┐
    │                               │                               │
    ▼                               ▼                               ▼
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  ✅ CONNECTED    │    │  ✅ CONNECTED    │    │  ❌ NOT USED     │
│   (31 services)  │    │   (Business)     │    │   (31 services)  │
│                  │    │                  │    │                  │
│ field-mgmt:3000  │    │ marketplace:3010 │    │ agent-reg:8160   │
│ field-core:3005  │    │ billing:8089     │    │ ai-agents:8122   │
│ field-intel:8120 │    │ disaster:3020    │    │ knowledge:8140   │
│ weather:8092     │    │ community:8097   │    │ mcp-server:8200  │
│ weather-core:8108│    │ reports:8084     │    │ skills:8121      │
│ crop-intel:8095  │    │ analytics:8100   │    │ ai-advisor:8112  │
│ iot-service:8117 │    │                  │    │ research:3015    │
│ task:8103        │    │                  │    │ audit:8114       │
│ equipment:8101   │    │                  │    │ crm:8131         │
│ alert:8113       │    │                  │    │ lowcode:8132     │
│ advisory:8093    │    │                  │    │ wechat:8133      │
│ irrigation:8094  │    │                  │    │ globalgap:8123   │
│ yield:8098       │    │                  │    │ logistics:8162   │
│ satellite:8090   │    │                  │    │ ussd:8163        │
│ agro-advisor:8105│    │                  │    │ inventory:8116   │
│ agro-rules:8151  │    │                  │    │ + deprecated...  │
│ field-chat:8099  │    │                  │    │                  │
│ astronomical:8111│    │                  │    │                  │
│ provider:8104    │    │                  │    │                  │
│ users:3025       │    │                  │    │                  │
└──────────────────┘    └──────────────────┘    └──────────────────┘
```

---

## 6. التوصيات | Recommendations

### 6.1 خدمات مفقودة يُنصح بتكاملها

| الخدمة | الأولوية | السبب |
|--------|---------|-------|
| `audit-service` | عالية | تتبع الأمان والامتثال |
| `notification-service` | عالية | إشعارات Push للمستخدمين |
| `inventory-service` | متوسطة | تتبع المخزون الزراعي |
| `virtual-sensors` | متوسطة | بيانات المستشعرات المحسوبة |

### 6.2 خدمات للمستقبل

| الخدمة | الأولوية | السبب |
|--------|---------|-------|
| `ai-agents-*` | منخفضة | وكلاء ذكاء اصطناعي متقدمين |
| `knowledge-graph` | منخفضة | رسم المعرفة الزراعية |
| `globalgap-compliance` | منخفضة | شهادات الجودة |

### 6.3 خدمات تحتاج مراجعة

- `dashboard` و `scouting` و `action-windows`: غير موجودة كخدمات منفصلة في Kong - قد تكون جزءاً من خدمات أخرى
- `reports`: غير موجودة كخدمة منفصلة في kong.yml

---

## 7. الخلاصة | Conclusion

تطبيق Web يستخدم **50%** من خدمات Kong المتاحة - ضعف ما يستخدمه Admin (27.4%).

**نقاط القوة في Web:**
- تكامل شامل مع خدمات الأعمال (marketplace, billing)
- دعم كامل لـ IoT والمستشعرات
- تكامل مع المجتمع والدردشة
- دعم التقارير والتحليلات

**نقاط التحسين:**
- إضافة تكامل audit-service للأمان
- إضافة notification-service للإشعارات
- توحيد dashboard/scouting/action-windows كخدمات Kong منفصلة

---

_آخر تحديث: 2026-01-24_
