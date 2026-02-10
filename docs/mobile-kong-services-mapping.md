# Mobile-Kong Services Mapping | ربط خدمات Kong بتطبيقات الموبايل

> تقرير تحليلي للتحقق من ارتباط خدمات Kong بتطبيقات الموبايل
>
> **تاريخ التحليل**: 2026-01-24 (محدث)
> **المصادر**:
> - `apps/mobile/lib/core/config/api_config.dart`
> - `apps/mobile/lib/core/config/env_config.dart`
> - `apps/mobile/lib/core/api/kong_gateway_client.dart`
> - `apps/mobile/lib/core/services/service_registry.dart`
> - `apps/mobile/sahool_field_app/`
> - `apps/mobile/sahol_atmosphere/`
> - `apps/mobile/sahool-mobile/` (React Native)
> - `services-definition.md`

---

## ملخص تنفيذي | Executive Summary

| البند | العدد |
|-------|-------|
| **إجمالي خدمات Kong** | 62 |
| **الخدمات المستخدمة في Mobile (جميع التطبيقات)** | 32 |
| **الخدمات غير المستخدمة** | 30 |
| **نسبة التغطية الإجمالية** | 51.6% |

### تطبيقات الموبايل المكتشفة

| التطبيق | الموقع | التقنية | الوصف | الخدمات |
|---------|--------|---------|-------|---------|
| **SAHOOL Field App (Main)** | `apps/mobile/lib/` | Flutter | التطبيق الرئيسي الكامل v16.0.0 | 29 خدمة |
| **Sahool Field App** | `apps/mobile/sahool_field_app/` | Flutter | تطبيق الحقول المتخصص v15.5.0 | 5 خدمات |
| **Sahol Atmosphere** | `apps/mobile/sahol_atmosphere/` | Flutter | مراقبة صحة الخدمات v16.0.0 | 4 خدمات |
| **Sahool Mobile (React Native)** | `apps/mobile/sahool-mobile/` | React Native + TypeScript | مدير المزامنة Offline-First | 7 خدمات |

---

## 1. تطبيق SAHOOL Field الرئيسي | Main Mobile App

### 1.1 خدمات Kong المُعرَّفة في KongGatewayClient

```dart
// من kong_gateway_client.dart
class KongServices {
  static const fields       = KongService(name: 'field-management', basePath: '/api/v1/fields');
  static const auth         = KongService(name: 'user-service', basePath: '/api/v1/auth');
  static const weather      = KongService(name: 'weather-service', basePath: '/api/v1/weather');
  static const vegetation   = KongService(name: 'vegetation-analysis', basePath: '/api/v1/vegetation');
  static const satellite    = KongService(name: 'satellite', basePath: '/api/v1/satellite');
  static const ndvi         = KongService(name: 'ndvi', basePath: '/api/v1/ndvi');
  static const irrigation   = KongService(name: 'irrigation-smart', basePath: '/api/v1/irrigation');
  static const advisory     = KongService(name: 'advisory-service', basePath: '/api/v1/advisory');
  static const cropHealth   = KongService(name: 'crop-intelligence', basePath: '/api/v1/crop-health');
  static const tasks        = KongService(name: 'task-service', basePath: '/api/v1/tasks');
  static const equipment    = KongService(name: 'equipment-service', basePath: '/api/v1/equipment');
  static const alerts       = KongService(name: 'alert-service', basePath: '/api/v1/alerts');
  static const notifications = KongService(name: 'notification-service', basePath: '/api/v1/notifications');
  static const marketplace  = KongService(name: 'marketplace', basePath: '/api/v1/marketplace');
  static const iot          = KongService(name: 'iot-service', basePath: '/api/v1/iot');
  static const yield_       = KongService(name: 'yield-engine', basePath: '/api/v1/yield');
}
```

### 1.2 الخدمات المتصلة فعلياً (Full List)

| الخدمة | Kong Service | المنفذ | نقاط النهاية الرئيسية |
|--------|--------------|--------|----------------------|
| **auth** | user-service | 3025 | `/api/v1/auth/login`, `/api/v1/auth/refresh`, `/api/v1/auth/logout`, `/api/v1/auth/register`, `/api/v1/auth/otp/*` |
| **users** | user-service | 3025 | `/api/v1/users/profile` |
| **fields** | field-management-service | 3000 | `/api/v1/fields`, `/api/v1/fields/sync`, `/api/v1/fields/batch`, `/api/v1/fields/nearby`, `/api/v1/fields/:id/boundary` |
| **tasks** | task-service | 8103 | `/api/v1/tasks`, `/api/v1/tasks/:id/complete` |
| **weather** | weather-service | 8092 | `/api/v1/weather/current`, `/api/v1/weather/forecast`, `/api/v1/weather/alerts`, `/api/v1/weather/locations`, `/api/v1/weather/agricultural-calendar` |
| **satellite** | vegetation-analysis-service | 8090 | `/api/v1/satellite/analyze`, `/api/v1/satellite/timeseries`, `/api/v1/satellite/imagery`, `/api/v1/satellite/indices`, `/api/v1/satellite/health`, `/api/v1/satellite/phenology`, `/api/v1/satellite/satellites` |
| **ndvi** | vegetation-analysis-service | 8090 | `/api/v1/ndvi/process`, `/api/v1/ndvi/timeseries`, `/api/v1/ndvi/comparison`, `/api/v1/ndvi/tiles` |
| **indicators** | indicators-service | 8091 | `/api/v1/indicators/definitions`, `/api/v1/indicators/field/:id`, `/api/v1/indicators/dashboard`, `/api/v1/indicators/alerts`, `/api/v1/indicators/trends` |
| **crop-health** | crop-intelligence-service | 8095 | `/api/v1/crop-health/diagnose`, `/api/v1/crop-health/diagnose/batch`, `/api/v1/crop-health/crops`, `/api/v1/crop-health/diseases`, `/api/v1/crop-health/treatment`, `/api/v1/crop-health/expert-review` |
| **fertilizer** | advisory-service | 8093 | `/api/v1/fertilizer/crops`, `/api/v1/fertilizer/fertilizers`, `/api/v1/fertilizer/recommend`, `/api/v1/fertilizer/soil/interpret`, `/api/v1/fertilizer/deficiency/symptoms`, `/api/v1/fertilizer/schedule` |
| **irrigation** | irrigation-smart | 8094 | `/api/v1/irrigation/crops`, `/api/v1/irrigation/methods`, `/api/v1/irrigation/calculate`, `/api/v1/irrigation/water-balance`, `/api/v1/irrigation/sensor-reading`, `/api/v1/irrigation/efficiency`, `/api/v1/irrigation/schedule` |
| **virtual-sensors** | virtual-sensors | 8119 | `/api/v1/virtual-sensors/et0/calculate`, `/api/v1/virtual-sensors/etc/calculate`, `/api/v1/virtual-sensors/soil-moisture/estimate`, `/api/v1/virtual-sensors/irrigation/recommend`, `/api/v1/virtual-sensors/irrigation/quick-check` |
| **equipment** | equipment-service | 8101 | `/api/v1/equipment`, `/api/v1/equipment/:id`, `/api/v1/equipment/qr/:code`, `/api/v1/equipment/stats`, `/api/v1/equipment/maintenance/*`, `/api/v1/equipment/:id/fuel/*`, `/api/v1/equipment/:id/usage/*` |
| **inventory** | inventory-service | 8116 | `/api/v1/inventory`, `/api/v1/inventory/categories`, `/api/v1/inventory/transactions`, `/api/v1/inventory/alerts` |
| **iot** | iot-service | 8117 | `/api/v1/iot/devices`, `/api/v1/iot/sensors`, `/api/v1/iot/device-types` |
| **notifications** | notification-service | 8110 | `/api/v1/notifications`, `/api/v1/notifications/preferences`, `/api/v1/notifications/subscribe`, `/api/v1/notifications/unsubscribe`, `/api/v1/notifications/mark-read`, `/api/v1/notifications/device/*` |
| **alerts** | alert-service | 8113 | `/api/v1/alerts` |
| **billing** | billing-core | 8089 | `/api/v1/billing/wallet`, `/api/v1/billing/deposit`, `/api/v1/billing/withdraw`, `/api/v1/billing/transfer`, `/api/v1/billing/transactions`, `/api/v1/billing/subscription`, `/api/v1/billing/plans`, `/api/v1/billing/invoices`, `/api/v1/billing/usage`, `/api/v1/billing/stripe/*`, `/api/v1/billing/payment-methods/*` |
| **marketplace** | marketplace-service | 3010 | `/api/v1/marketplace/products`, `/api/v1/marketplace/harvest`, `/api/v1/marketplace/orders`, `/api/v1/marketplace/fintech/wallet`, `/api/v1/marketplace/fintech/loans`, `/api/v1/marketplace/fintech/calculate-score` |
| **yield** | yield-prediction-service | 8098 | `/api/v1/yield/predict`, `/api/v1/yield/history`, `/api/v1/yield/factors` |
| **ai-advisor** | ai-advisor | 8112 | `/api/v1/ai-advisor/query`, `/api/v1/ai-advisor/chat`, `/api/v1/ai-advisor/diagnose`, `/api/v1/ai-advisor/recommendations`, `/api/v1/ai-advisor/analyze`, `/api/v1/ai-advisor/history` |
| **advisor** | agro-advisor | 8105 | `/api/v1/advisor/ask`, `/api/v1/advisor/diagnose`, `/api/v1/advisor/recommend`, `/api/v1/advisor/irrigation`, `/api/v1/advisor/fertilizer`, `/api/v1/advisor/analyze-field`, `/api/v1/advisor/context`, `/api/v1/advisor/history`, `/api/v1/advisor/advisories`, `/api/v1/advisor/feedback` |
| **community** | community-chat | 8097 | `/api/v1/community/requests`, `/api/v1/community/rooms`, `/api/v1/community/experts/online`, `/api/v1/community/stats` |
| **chat** | field-chat | 8099 | `/api/v1/chat/conversations`, `/api/v1/chat/messages`, `/api/v1/conversations/*` |
| **gdd** | - | - | `/api/v1/gdd/fields/:id/accumulation`, `/api/v1/gdd/fields/:id/records`, `/api/v1/gdd/fields/:id/calculate`, `/api/v1/gdd/crops`, `/api/v1/gdd/fields/:id/forecast`, `/api/v1/gdd/fields/:id/settings` |
| **reports** | - | 8084 | `/api/v1/reports/templates`, `/api/v1/reports/generate`, `/api/v1/reports/history`, `/api/v1/reports/data/*`, `/api/v1/reports/:id/export/*` |
| **payment** | - | - | `/api/v1/payment/deposit`, `/api/v1/payment/withdraw`, `/api/v1/payment/transfer`, `/api/v1/payment/topup`, `/api/v1/payment/status`, `/api/v1/payment/transactions`, `/api/v1/payment/balance`, `/api/v1/payment/operators` |
| **astronomical** | astronomical-calendar | 8111 | `/api/v1/astronomical/*` |
| **crm** | crm-service | 8131 | `/api/v1/crm/*` |

### 1.3 منافذ الخدمات (EnvConfig)

```dart
// Service Ports from env_config.dart
fieldCorePort: 3000       // field-management-service
marketplacePort: 3010     // marketplace-service
chatPort: 8099            // field-chat
gatewayPort: 8000         // Kong gateway
satellitePort: 8090       // vegetation-analysis-service
indicatorsPort: 8091      // indicators-service
cropHealthPort: 8095      // crop-intelligence-service
virtualSensorsPort: 8119  // virtual-sensors
weatherPort: 8092         // weather-service
fertilizerPort: 8093      // advisory-service
irrigationPort: 8094      // irrigation-smart
sprayPort: 8098           // yield-engine
communityChatPort: 8097   // community-chat
equipmentPort: 8101       // equipment-service
inventoryPort: 8116       // inventory-service
notificationsPort: 8110   // notification-service
billingPort: 8089         // billing-core
aiAdvisorPort: 8112       // ai-advisor
```

---

## 2. تطبيق Sahool Field App | Sahool Field App

تطبيق متخصص للعمل الميداني مع مجموعة فرعية من الميزات.

### 2.1 الخدمات المستخدمة

| الخدمة | نقاط النهاية |
|--------|--------------|
| **ai-advisor** | `/api/v1/advisor/ask`, `/api/v1/advisor/diagnose`, `/api/v1/advisor/recommend`, `/api/v1/advisor/analyze-field`, `/api/v1/advisor/history` |
| **equipment** | `/api/v1/equipment`, `/api/v1/equipment/:id`, `/api/v1/equipment/qr/:code`, `/api/v1/equipment/:id/status`, `/api/v1/equipment/:id/location`, `/api/v1/equipment/:id/telemetry`, `/api/v1/equipment/stats`, `/api/v1/equipment/alerts`, `/api/v1/equipment/:id/maintenance` |
| **tasks** | `/api/v1/tasks`, `/api/v1/tasks/:id`, `/api/v1/tasks/:id/complete` |
| **fields** | `/api/v1/fields`, `/api/v1/fields/:id` |

---

## 3. تطبيق Sahol Atmosphere | Sahol Atmosphere

تطبيق بسيط لمراقبة صحة الخدمات.

### 3.1 الخدمات المراقبة

```dart
// Health check endpoints
_ServiceConfig('Fields', 'الحقول', '/api/v1/fields/healthz'),
_ServiceConfig('Weather', 'الطقس', '/api/v1/weather/healthz'),
_ServiceConfig('NDVI', 'NDVI', '/api/v1/ndvi/healthz'),
_ServiceConfig('Tasks', 'المهام', '/api/v1/tasks/healthz'),
```

---

## 4. تطبيق Sahool Mobile (React Native) | Sahool Mobile App

تطبيق React Native/TypeScript متخصص في إدارة المزامنة بدون اتصال (Offline-First Sync Manager).

### 4.1 معلومات التطبيق

| البند | القيمة |
|-------|--------|
| **الموقع** | `apps/mobile/sahool-mobile/` |
| **التقنية** | React Native + TypeScript |
| **الإصدار** | 1.0.0 |
| **الوصف** | Offline-first agricultural management system |
| **حجم الكود** | 6,500+ سطر |

### 4.2 المكتبات الرئيسية

```json
{
  "react": "^18.2.0",
  "react-native": "^0.72.0",
  "@react-native-async-storage/async-storage": "^1.19.0",
  "@react-native-community/netinfo": "^9.4.0"
}
```

### 4.3 أنواع البيانات المدعومة للمزامنة

| نوع البيانات | الوصف بالعربية | Kong Service |
|--------------|----------------|--------------|
| `FIELD_OBSERVATION` | ملاحظات الحقول | field-management-service |
| `SENSOR_READING` | قراءات المستشعرات | iot-service |
| `TASK_COMPLETION` | إكمال المهام | task-service |
| `IMAGE_UPLOAD` | رفع الصور | notification-service |
| `FIELD_UPDATE` | تحديث بيانات الحقل | field-management-service |
| `FARM_UPDATE` | تحديث بيانات المزرعة | field-management-service |
| `IRRIGATION_LOG` | سجل الري | irrigation-smart |
| `PEST_REPORT` | تقرير الآفات | crop-intelligence-service |

### 4.4 الخدمات المتصلة عبر Kong

| الخدمة | نقاط النهاية |
|--------|--------------|
| **field-management-service** | `/api/v1/field-observations`, `/api/v1/fields/*` |
| **iot-service** | `/api/v1/sensor-readings` |
| **task-service** | `/api/v1/tasks/{id}/complete` |
| **notification-service** | `/api/v1/images` (uploads) |
| **irrigation-smart** | `/api/v1/irrigation/logs` |
| **crop-intelligence-service** | `/api/v1/pest-reports` |
| **user-service** | `/api/v1/auth/*` (implicit) |

### 4.5 ميزات المزامنة

```typescript
// Default Sync Configuration
{
  autoSync: true,
  syncInterval: 5 * 60 * 1000,  // 5 دقائق
  maxRetries: 5,
  retryDelayBase: 1000,
  retryDelayMax: 30000,
  batchSize: 10,
  maxQueueSize: 1000,
  conflictResolution: 'LAST_WRITE_WINS',
  syncOnlyOnWifi: false,
  throttleOnSlowConnection: true,
  persistQueue: true,
  maxUploadSize: 10 * 1024 * 1024  // 10 MB
}
```

### 4.6 استراتيجيات حل التعارض

| الاستراتيجية | الوصف بالعربية | الوصف |
|--------------|----------------|-------|
| `LAST_WRITE_WINS` | آخر كتابة تفوز | Based on timestamp |
| `SERVER_WINS` | الخادم يفوز دائماً | Server data takes priority |
| `CLIENT_WINS` | العميل يفوز دائماً | Client data takes priority |
| `MANUAL_MERGE` | دمج يدوي | Requires user intervention |
| `FIELD_LEVEL_MERGE` | دمج على مستوى الحقول | Merges field by field |
| `CUSTOM` | استراتيجية مخصصة | Per data type resolver |

### 4.7 نظام الأحداث

| نوع الحدث | الوصف |
|-----------|-------|
| `SYNC_STARTED` | بدء المزامنة |
| `SYNC_COMPLETED` | اكتمال المزامنة |
| `SYNC_FAILED` | فشل المزامنة |
| `OPERATION_QUEUED` | إضافة عملية للقائمة |
| `OPERATION_COMPLETED` | اكتمال العملية |
| `OPERATION_FAILED` | فشل العملية |
| `CONFLICT_DETECTED` | اكتشاف تعارض |
| `CONFLICT_RESOLVED` | حل التعارض |
| `NETWORK_STATUS_CHANGED` | تغير حالة الشبكة |
| `QUEUE_CLEARED` | مسح القائمة |

### 4.8 مثال الاستخدام

```typescript
import SyncManager from './services/syncManager';
import { SyncOperationType, SyncDataType, SyncPriority } from './models/syncTypes';

// Initialize
const syncManager = SyncManager.getInstance({
  autoSync: true,
  syncInterval: 5 * 60 * 1000
});

// Queue field observation
await syncManager.queueOperation(
  SyncOperationType.CREATE,
  SyncDataType.FIELD_OBSERVATION,
  {
    fieldId: 'field-123',
    notes: 'ملاحظات الحقل',
    timestamp: new Date().toISOString()
  },
  {
    priority: SyncPriority.HIGH,
    endpoint: '/api/v1/field-observations'
  }
);

// Check status
const status = await syncManager.getSyncStatus();
console.log('Pending:', status.pendingCount);

// Force sync
await syncManager.forceSync();
```

---

## 5. الخدمات غير المتصلة | Unconnected Services

### 5.1 خدمات الوكلاء (Agent Services)

| Kong Service | المنفذ | الوصف |
|--------------|--------|-------|
| `agent-registry` | 8160 | سجل الوكلاء |
| `ai-agents-core` | 8161 | نواة الوكلاء |
| `ai-agents-service` | 8130 | تنسيق الوكلاء |
| `knowledge-graph` | 8140 | رسم المعرفة |
| `mcp-server` | 8200 | Model Context Protocol |
| `skills-service` | 8121 | خدمة المهارات |

### 5.2 خدمات أخرى غير مستخدمة

| Kong Service | المنفذ | الوصف |
|--------------|--------|-------|
| `research-core` | 3015 | البحث العلمي |
| `disaster-assessment` | 3020 | تقييم الكوارث |
| `ws-gateway` | 8081 | بوابة WebSocket |
| `iot-gateway` | 8106 | بوابة IoT |
| `audit-service` | 8114 | التدقيق |
| `code-review-service` | 8102 | مراجعة الكود |
| `lowcode-engine` | 8132 | محرك Low-Code |
| `wechat-service` | 8133 | تكامل WeChat |
| `globalgap-compliance` | 8128 | شهادة GlobalGAP |
| `logistics-service` | 8167 | اللوجستيات |
| `ussd-gateway` | 8183 | بوابة USSD |

### 5.3 الخدمات المهملة (لا يجب استخدامها)

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

## 6. مقارنة بين التطبيقات | Comparison

| الخدمة | Mobile Main | Field App | Atmosphere | RN Sync | Web | Admin |
|--------|-------------|-----------|------------|---------|-----|-------|
| field-management-service | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| user-service | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ |
| weather-service | ✅ | ❌ | ✅ | ❌ | ✅ | ✅ |
| vegetation-analysis-service | ✅ | ❌ | ✅ | ❌ | ✅ | ✅ |
| indicators-service | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ |
| crop-intelligence-service | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ |
| advisory-service | ✅ | ❌ | ❌ | ❌ | ✅ | ✅ |
| irrigation-smart | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ |
| virtual-sensors | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ |
| equipment-service | ✅ | ✅ | ❌ | ❌ | ✅ | ✅ |
| task-service | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| alert-service | ✅ | ❌ | ❌ | ❌ | ✅ | ⚠️ |
| notification-service | ✅ | ❌ | ❌ | ✅ | ❌ | ✅ |
| marketplace-service | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ |
| billing-core | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ |
| iot-service | ✅ | ❌ | ❌ | ✅ | ✅ | ❌ |
| yield-prediction-service | ✅ | ❌ | ❌ | ❌ | ✅ | ✅ |
| ai-advisor | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| agro-advisor | ✅ | ✅ | ❌ | ❌ | ✅ | ❌ |
| community-chat | ✅ | ❌ | ❌ | ❌ | ✅ | ✅ |
| field-chat | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ |
| inventory-service | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| astronomical-calendar | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ |
| crm-service | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |

> **RN Sync** = Sahool Mobile (React Native Sync Manager)

---

## 7. ملفات التكوين الرئيسية | Key Configuration Files

### 7.1 تطبيق Mobile الرئيسي

| الملف | الوصف |
|-------|-------|
| `lib/core/config/api_config.dart` | تكوين API endpoints لجميع الخدمات |
| `lib/core/config/env_config.dart` | متغيرات البيئة ومنافذ الخدمات |
| `lib/core/api/kong_gateway_client.dart` | عميل Kong Gateway مع Circuit Breaker |
| `lib/core/services/service_registry.dart` | سجل جميع الخدمات ونقاط النهاية |
| `lib/core/config/service_switcher.dart` | محول الخدمات للتبديل بين البيئات |

### 7.2 ملفات Features API

| الملف | الخدمات |
|-------|---------|
| `lib/features/auth/services/` | auth, otp |
| `lib/features/field/data/` | fields |
| `lib/features/billing/data/remote/` | billing, stripe |
| `lib/features/equipment/data/` | equipment |
| `lib/features/ai_advisor/data/remote/` | ai-advisor, agro-advisor |
| `lib/features/chat/data/remote/` | chat, conversations |
| `lib/features/gdd/services/` | gdd |
| `lib/features/reports/data/` | reports |
| `lib/features/payment/data/` | payment (tharwatt) |
| `lib/features/notifications/data/` | notifications |
| `lib/features/marketplace/` | marketplace, fintech |
| `lib/features/wallet/` | wallet, loans |

---

## 8. مخطط الاتصال | Connection Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                            Mobile Applications                                        │
├─────────────────┬──────────────────┬──────────────────┬───────────────────────────────┤
│  SAHOOL Field   │   Sahool Field   │ Sahol Atmosphere │    Sahool Mobile (RN)        │
│    (Main)       │      App         │  (Health Monitor)│   (Offline Sync Manager)     │
│  Flutter v16    │  Flutter v15.5   │   Flutter v16    │  React Native + TypeScript   │
│   29 services   │    5 services    │    4 services    │        7 services            │
└─────────────────┴──────────────────┴──────────────────┴───────────────────────────────┘
                                    │
                      ┌─────────────┼─────────────┐
                      │   Offline   │   Online    │
                      │    Cache    │   Request   │
                      └─────────────┴─────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     Kong API Gateway (:8000)                                │
│                  api.sahool.app / api-staging.sahool.app                    │
│                                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │  Rate Limiting  │  │  Auth (JWT)     │  │  CORS           │             │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  Core Services   │    │   AI Services    │    │ Business Services│
│                  │    │                  │    │                  │
│ fields:3000      │    │ crop-health:8095 │    │ marketplace:3010 │
│ users:3025       │    │ ai-advisor:8112  │    │ billing:8089     │
│ tasks:8103       │    │ agro-advisor:8105│    │ community:8097   │
│ equipment:8101   │    │ advisory:8093    │    │ chat:8099        │
│ weather:8092     │    │ yield:8098       │    │ notifications:8110│
│ irrigation:8094  │    │ indicators:8091  │    │ inventory:8116   │
│ satellite:8090   │    │ v-sensors:8119   │    │ crm:8131         │
│ iot:8117         │    │                  │    │ astronomical:8111│
│ alerts:8113      │    │                  │    │                  │
└──────────────────┘    └──────────────────┘    └──────────────────┘
```

---

## 9. ميزات Mobile الفريدة | Mobile-Specific Features

### 9.1 Offline-First Architecture

```dart
// Offline sync configuration
syncInterval: 30 seconds (foreground)
backgroundSyncInterval: 15 minutes (background)
maxRetryCount: 5
outboxBatchSize: 50
```

### 9.2 Circuit Breaker Pattern

```dart
// Circuit breaker configuration
failureThreshold: 3 failures
circuitTimeout: 30 seconds
```

### 9.3 Service Health Monitoring

```dart
// Health check configuration
enableServiceHealthMonitoring: true
serviceHealthCheckInterval: 5 minutes
serviceHealthCheckTimeout: 10 seconds
```

### 9.4 Multi-Environment Support

| البيئة | API URL | WS URL |
|--------|---------|--------|
| Development | `http://10.0.2.2:8000/api/v1` | `ws://10.0.2.2:8081` |
| Staging | `https://api-staging.sahool.app/api/v1` | `wss://ws-staging.sahool.app` |
| Production | `https://api.sahool.app/api/v1` | `wss://ws.sahool.app` |

---

## 10. التوصيات | Recommendations

### 10.1 خدمات مفقودة يُنصح بتكاملها

| الخدمة | الأولوية | السبب |
|--------|---------|-------|
| `audit-service` | عالية | تتبع الأمان والامتثال |
| `disaster-assessment` | متوسطة | تنبيهات الكوارث للمزارعين |
| `ws-gateway` | عالية | Real-time updates للإشعارات |

### 10.2 تحسينات مقترحة

1. **توحيد ai-advisor و agro-advisor**: كلاهما يقدم خدمات استشارية مشابهة
2. **إضافة offline support لـ reports**: تخزين التقارير محلياً
3. **تكامل GDD مع Kong**: خدمة GDD غير موجودة في kong.yml

### 10.3 ملاحظات أمنية

- Certificate Pinning مُفعَّل للإنتاج
- Token refresh تلقائي
- PII filtering في crash reports
- Secure storage للـ tokens

---

## 11. الخلاصة | Conclusion

تطبيقات Mobile الأربعة تستخدم مجتمعة **51.6%** من خدمات Kong المتاحة (32 من 62 خدمة).

### ملخص التطبيقات

| التطبيق | التقنية | الخدمات | الغرض |
|---------|---------|---------|-------|
| **SAHOOL Field (Main)** | Flutter v16.0.0 | 29 | التطبيق الرئيسي الشامل |
| **Sahool Field App** | Flutter v15.5.0 | 5 | العمليات الميدانية الأساسية |
| **Sahol Atmosphere** | Flutter v16.0.0 | 4 | مراقبة صحة الخدمات |
| **Sahool Mobile (RN)** | React Native + TS | 7 | مدير المزامنة Offline |

### نقاط القوة

- ✅ تكامل شامل مع خدمات الذكاء الاصطناعي (ai-advisor, agro-advisor, crop-health)
- ✅ دعم كامل للعمل بدون اتصال (Offline-First) في جميع التطبيقات
- ✅ Circuit Breaker و Retry patterns
- ✅ تكامل Billing و Marketplace كامل
- ✅ دعم CRM و Inventory (غير موجود في Web/Admin)
- ✅ تطبيق React Native متخصص للمزامنة مع دعم TypeScript كامل
- ✅ استراتيجيات متعددة لحل التعارضات في المزامنة

### نقاط التحسين

- ⚠️ إضافة تكامل WebSocket Gateway للتحديثات الفورية
- ⚠️ توحيد خدمات AI المتعددة
- ⚠️ إضافة audit-service للأمان
- ⚠️ توحيد التطبيقين Flutter (Main v16 و Field App v15.5) في تطبيق واحد

### ملاحظة حول sahool-mobile

تطبيق `sahool-mobile` هو **مكتبة/تطبيق React Native** متخصص في إدارة المزامنة بدون اتصال. يمكن استخدامه:
1. كتطبيق مستقل للمزامنة
2. كمكتبة يتم دمجها في تطبيقات React Native أخرى

يحتوي على:
- 1,900+ سطر من كود مدير المزامنة
- 650+ سطر من تعريفات TypeScript
- 800+ سطر من الأمثلة
- 600+ سطر من الاختبارات
- **إجمالي: 6,500+ سطر**

---

_آخر تحديث: 2026-01-24_
