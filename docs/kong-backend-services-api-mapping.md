# Kong Backend Services API Mapping | توثيق ربط خدمات Kong مع Backend

> **الإصدار**: 16.0.0
> **تاريخ التحديث**: 2026-01-24
> **إجمالي الخدمات**: 62 خدمة Kong
> **إجمالي نقاط النهاية**: 350+ endpoints

---

## جدول المحتويات | Table of Contents

1. [نظرة عامة | Overview](#نظرة-عامة--overview)
2. [خدمات Node.js | Node.js Services](#خدمات-nodejs--nodejs-services)
3. [خدمات Python | Python Services](#خدمات-python--python-services)
4. [الخدمات المضافة حديثاً | Newly Registered Services](#الخدمات-المضافة-حديثاً--newly-registered-services)
5. [الخدمات المهملة | Deprecated Services](#الخدمات-المهملة--deprecated-services)
6. [ملخص الإحصائيات | Statistics Summary](#ملخص-الإحصائيات--statistics-summary)

---

## نظرة عامة | Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Kong API Gateway (Port 8000)                        │
│                              62 خدمة مُعرَّفة                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │   Node.js (11)  │  │   Python (35)   │  │    New (16)     │             │
│  │   خدمات نود     │  │  خدمات بايثون   │  │  خدمات جديدة    │             │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘             │
│           │                    │                    │                       │
│           ▼                    ▼                    ▼                       │
│  ┌─────────────────────────────────────────────────────────────────┐       │
│  │                     Backend Services                             │       │
│  │                   خدمات الخلفية (Microservices)                  │       │
│  └─────────────────────────────────────────────────────────────────┘       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### تصنيف الخدمات حسب الطبقة | Services by Layer

| الطبقة | Layer | الخدمات | Count |
|--------|-------|---------|-------|
| الاستحواذ | Acquisition | satellite, iot, weather, virtual-sensors, iot-gateway | 5 |
| الذكاء | Intelligence | indicators, lai, crop-intelligence, vegetation-analysis, ndvi-processor, field-intelligence, skills | 7 |
| القرار | Decision | crop-growth-model, advisory, irrigation-smart, yield-engine, yield-prediction, agro-advisor | 6 |
| الأعمال | Business | notification, marketplace, billing, community-chat, task, equipment, ws-gateway | 7 |

---

## خدمات Node.js | Node.js Services

### 1. Field Management Service | خدمة إدارة الحقول

| البند | القيمة |
|-------|--------|
| **Kong Service** | `field-management-service` |
| **Port** | 3000 |
| **Kong Routes** | `/api/v1/fields`, `/api/v1/field`, `/field` |
| **Framework** | Express + TypeORM |

#### API Endpoints

| Method | Endpoint | Input | Output | الوصف |
|--------|----------|-------|--------|-------|
| GET | `/healthz` | - | `{status, service, timestamp}` | فحص الصحة |
| GET | `/readyz` | - | `{status, database}` | فحص الجاهزية |
| GET | `/fields` | Query: `tenantId`, `status`, `cropType`, `limit`, `offset` | `{success, data: Field[], pagination}` | قائمة الحقول |
| GET | `/fields/:id` | Path: `id`, Header: `If-Match` | `{success, data: Field, etag}` | حقل واحد |
| POST | `/fields` | Body: `FieldCreateDto` | `{success, data: Field, etag}` | إنشاء حقل |
| PUT | `/fields/:id` | Body: `FieldUpdateDto`, Header: `If-Match` | `{success, data: Field, etag}` | تحديث حقل |
| DELETE | `/fields/:id` | Path: `id` | `{success, message}` | حذف حقل |
| GET | `/fields/nearby` | Query: `lat`, `lng`, `radius` | `{success, data: Field[]}` | حقول قريبة |
| GET | `/fields/:id/ndvi` | Path: `id` | `NDVIResponse` | بيانات NDVI |
| PUT | `/fields/:id/ndvi` | Body: `{value, source}` | `NDVIUpdateResponse` | تحديث NDVI |
| GET | `/ndvi/summary` | Query: `tenantId` | `NDVISummaryResponse` | ملخص NDVI |
| GET | `/fields/sync` | Query: `tenantId`, `since`, `includeDeleted` | `SyncResponse` | مزامنة دلتا |
| POST | `/fields/sync/batch` | Body: `BatchSyncDto` | `BatchSyncResponse` | مزامنة دفعية |
| GET | `/sync/status` | Query: `deviceId`, `tenantId` | `SyncStatusResponse` | حالة المزامنة |

**Input Models:**

```typescript
// FieldCreateDto
{
  name: string;              // required
  tenantId: string;          // required
  cropType: string;          // required
  coordinates?: [number, number][];
  ownerId?: string;
  irrigationType?: string;
  soilType?: string;
  plantingDate?: string;     // ISO date
  expectedHarvest?: string;  // ISO date
  metadata?: object;
}

// FieldUpdateDto
{
  name?: string;
  cropType?: string;
  status?: string;
  irrigationType?: string;
  soilType?: string;
  plantingDate?: string;
  expectedHarvest?: string;
  metadata?: object;
}

// BatchSyncDto
{
  deviceId: string;          // required
  userId: string;            // required
  tenantId: string;          // required
  fields: FieldSyncItem[];   // required
}
```

**Output Models:**

```typescript
// Field
{
  id: string;
  name: string;
  tenantId: string;
  cropType: string;
  status: string;
  coordinates: [number, number][];
  areaHectares: number;
  ndviValue?: number;
  healthScore?: number;
  irrigationType?: string;
  soilType?: string;
  plantingDate?: string;
  expectedHarvest?: string;
  metadata?: object;
  createdAt: string;
  updatedAt: string;
  version: number;
}

// NDVIResponse
{
  fieldId: string;
  fieldName: string;
  current: {
    value: number;           // -1 to 1
    category: string;
    date: string;
  };
  statistics: {
    average: number;
    min: number;
    max: number;
    trend: number;
    trendDirection: string;
  };
  history: NDVIRecord[];
  lastUpdated: string;
}
```

---

### 2. User Service | خدمة المستخدمين

| البند | القيمة |
|-------|--------|
| **Kong Service** | `user-service`, `user-service-public`, `user-service-health` |
| **Port** | 3025 |
| **Kong Routes** | `/api/v1/auth/*`, `/api/v1/users` |
| **Framework** | NestJS |

#### Authentication Endpoints (Public)

| Method | Endpoint | Input | Output | الوصف |
|--------|----------|-------|--------|-------|
| POST | `/auth/login` | `LoginDto` | `AuthResponse` | تسجيل الدخول |
| POST | `/auth/register` | `RegisterDto` | `AuthResponse` | إنشاء حساب |
| POST | `/auth/forgot-password` | `{email}` | `{success, message}` | طلب استعادة كلمة المرور |
| POST | `/auth/reset-password` | `{token, newPassword}` | `{success, message}` | تغيير كلمة المرور |
| POST | `/auth/send-otp` | `OtpRequestDto` | `{success, message, expiresIn}` | إرسال OTP |
| POST | `/auth/verify-otp` | `{identifier, otpCode, purpose}` | `{success, resetToken}` | التحقق من OTP |
| POST | `/auth/refresh` | `{refreshToken}` | `AuthResponse` | تجديد التوكن |

#### Protected Endpoints (JWT Required)

| Method | Endpoint | Input | Output | الوصف |
|--------|----------|-------|--------|-------|
| POST | `/auth/logout` | Header: `Authorization` | `{success, message}` | تسجيل الخروج |
| POST | `/auth/logout-all` | Header: `Authorization` | `{success, message}` | خروج من كل الأجهزة |
| POST | `/auth/me` | Header: `Authorization` | `{success, data: User}` | بيانات المستخدم الحالي |
| GET | `/users` | Query: `tenantId`, `role`, `status`, `skip`, `take` | `{success, data: User[], count}` | قائمة المستخدمين |
| GET | `/users/:id` | Path: `id` | `{success, data: User}` | مستخدم واحد |
| POST | `/users` | `CreateUserDto` | `{success, data: User}` | إنشاء مستخدم |
| PUT | `/users/:id` | `UpdateUserDto` | `{success, data: User}` | تحديث مستخدم |
| DELETE | `/users/:id` | Path: `id` | `{success, message}` | حذف مستخدم |

**Input Models:**

```typescript
// LoginDto
{
  email: string;             // required, valid email
  password: string;          // required, min 8 chars
}

// RegisterDto
{
  email: string;             // required
  password: string;          // required, min 8 chars
  firstName: string;         // required
  lastName: string;          // required
  phone?: string;
  tenantId?: string;
}

// OtpRequestDto
{
  identifier: string;        // phone or email
  channel: "sms" | "whatsapp" | "telegram" | "email";
  purpose: "password_reset" | "verify_phone";
  language?: string;
}
```

**Output Models:**

```typescript
// AuthResponse
{
  access_token: string;      // JWT
  refresh_token: string;     // JWT
  expires_in: number;        // seconds
  token_type: "Bearer";
  user: {
    id: string;
    email: string;
    firstName: string;
    lastName: string;
    role: string;
    tenantId: string;
  };
}

// User
{
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  phone?: string;
  role: string;
  tenantId: string;
  status: string;
  createdAt: string;
  updatedAt: string;
}
```

---

### 3. Marketplace Service | خدمة السوق

| البند | القيمة |
|-------|--------|
| **Kong Service** | `marketplace-service` |
| **Port** | 3010 |
| **Kong Routes** | `/api/v1/marketplace`, `/marketplace` |
| **Framework** | NestJS |

#### Market Endpoints

| Method | Endpoint | Input | Output | الوصف |
|--------|----------|-------|--------|-------|
| GET | `/market/products` | Query: `category`, `governorate`, `sellerId`, `minPrice`, `maxPrice` | `{products: Product[], total}` | قائمة المنتجات |
| GET | `/market/products/:id` | Path: `id` | `{data: Product}` | منتج واحد |
| POST | `/market/products` | `CreateProductDto` | `{success, data: Product}` | إنشاء منتج |
| POST | `/market/list-harvest` | `{userId, yieldData}` | `{success, data: Product}` | تحويل محصول لمنتج |
| POST | `/market/orders` | `{productId, quantity, buyerId}` | `{success, data: Order}` | إنشاء طلب |
| GET | `/market/orders/:userId` | Query: `role` | `{success, data: Order[]}` | طلبات المستخدم |
| GET | `/market/stats` | - | `MarketStats` | إحصائيات السوق |

#### FinTech & Wallet Endpoints

| Method | Endpoint | Input | Output | الوصف |
|--------|----------|-------|--------|-------|
| GET | `/fintech/wallet/:userId` | Query: `userType` | `Wallet` | المحفظة |
| POST | `/fintech/wallet/:walletId/deposit` | `{amount, description}` | `{success, newBalance}` | إيداع |
| POST | `/fintech/wallet/:walletId/withdraw` | `{amount, description}` | `{success, newBalance}` | سحب |
| GET | `/fintech/wallet/:walletId/transactions` | Query: `limit` | `{transactions: Transaction[]}` | سجل المعاملات |
| POST | `/fintech/calculate-score` | `{userId, farmData}` | `{creditScore, rating}` | حساب التصنيف الائتماني |
| POST | `/fintech/loans` | `LoanRequestDto` | `{loanId, status}` | طلب قرض |
| PUT | `/fintech/loans/:id/approve` | Path: `id` | `{loanId, status}` | الموافقة على القرض |
| POST | `/fintech/loans/:id/repay` | `{amount}` | `{success, remainingBalance}` | سداد القرض |
| POST | `/fintech/escrow` | `EscrowCreateDto` | `{escrowId, status}` | إنشاء ضمان |
| POST | `/fintech/escrow/:id/release` | `{notes}` | `{escrowId, status}` | تحرير الضمان |
| POST | `/fintech/escrow/:id/refund` | `{reason}` | `{escrowId, status}` | استرداد الضمان |

**Input/Output Models:**

```typescript
// CreateProductDto
{
  name: string;
  description?: string;
  category: string;
  price: number;
  governorate: string;
  images?: string[];
}

// LoanRequestDto
{
  userId: string;
  amount: number;
  duration: number;         // months
  purpose?: string;
}

// Wallet
{
  walletId: string;
  userId: string;
  balance: number;
  currency: string;
}

// CreditScore
{
  creditScore: number;      // 0-1000
  rating: "A" | "B" | "C" | "D" | "E";
}
```

---

### 4. Research Core | خدمة البحث العلمي

| البند | القيمة |
|-------|--------|
| **Kong Service** | `research-core` |
| **Port** | 3015 |
| **Kong Routes** | `/api/v1/research`, `/research` |
| **Framework** | NestJS |

#### Experiment Endpoints

| Method | Endpoint | Input | Output | الوصف |
|--------|----------|-------|--------|-------|
| POST | `/experiments` | `ExperimentCreateDto` | `Experiment` | إنشاء تجربة |
| GET | `/experiments` | Query: `status`, `researcherId`, `page`, `limit` | `{experiments, total, page}` | قائمة التجارب |
| GET | `/experiments/:id` | Path: `id` | `{experiment: Experiment}` | تفاصيل التجربة |
| GET | `/experiments/:id/summary` | Path: `id` | `{summary: object}` | ملخص التجربة |
| PUT | `/experiments/:id` | `ExperimentUpdateDto` | `Experiment` | تحديث التجربة |
| POST | `/experiments/:id/lock` | Path: `id` | `{experimentId, locked}` | قفل التجربة |
| DELETE | `/experiments/:id` | Path: `id` | `{success}` | حذف التجربة |
| GET/POST | `/protocols` | - | Protocols | إدارة البروتوكولات |
| GET/POST | `/samples` | - | Samples | إدارة العينات |
| GET/POST | `/treatments` | - | Treatments | إدارة المعالجات |
| GET/POST | `/logs` | - | Logs | سجل النشاط |
| GET/POST | `/signatures` | - | Signatures | التوقيعات الرقمية |

---

### 5. Disaster Assessment | خدمة تقييم الكوارث

| البند | القيمة |
|-------|--------|
| **Kong Service** | `disaster-assessment` |
| **Port** | 3020 |
| **Kong Routes** | `/api/v1/disaster`, `/disaster` |
| **Framework** | NestJS |

#### Disaster Endpoints

| Method | Endpoint | Input | Output | الوصف |
|--------|----------|-------|--------|-------|
| GET | `/disasters` | Query: `type`, `governorate`, `severity` | `{disasters: Disaster[]}` | قائمة الكوارث |
| GET | `/disasters/:id` | Path: `id` | `{disaster: Disaster}` | تفاصيل الكارثة |
| POST | `/disasters/report` | `DisasterReportDto` | `{disasterId, status}` | الإبلاغ عن كارثة |
| POST | `/disasters/assess/:fieldId` | `DamageAssessmentDto` | `{fieldId, damageAssessment}` | تقييم الأضرار |
| GET | `/disasters/risk/flood` | Query: `governorate` | `{governorate, riskMap, riskLevel}` | مخاطر الفيضان |
| GET | `/disasters/risk/drought` | Query: `governorate` | `{governorate, droughtIndex, severity}` | مؤشر الجفاف |
| GET | `/disasters/stats/summary` | Query: `year`, `governorate` | `DisasterStats` | إحصائيات الكوارث |

#### Alert Endpoints

| Method | Endpoint | Input | Output | الوصف |
|--------|----------|-------|--------|-------|
| GET | `/alerts` | Query: `governorate`, `type`, `severity` | `{alerts: Alert[]}` | قائمة التنبيهات |
| GET | `/alerts/weather` | Query: `governorate` | `{weatherAlerts: Alert[]}` | تنبيهات الطقس |
| GET | `/alerts/pest-disease` | Query: `governorate`, `cropType` | `{pestDiseaseAlerts: Alert[]}` | تنبيهات الآفات |
| POST | `/alerts/subscribe` | `{userId, governorate, types[]}` | `{success, subscriptionId}` | الاشتراك في التنبيهات |
| POST | `/alerts/:id/read` | Path: `id` | `{alertId, read}` | تحديد كمقروء |

**Enums:**

```typescript
enum DisasterType {
  FLOOD = "flood",
  DROUGHT = "drought",
  FROST = "frost",
  PEST = "pest",
  HAIL = "hail",
  FIRE = "fire"
}

enum Severity {
  LOW = "low",
  MEDIUM = "medium",
  HIGH = "high",
  CRITICAL = "critical"
}
```

---

### 6. Yield Prediction (Node.js) | خدمة توقع المحصول

| البند | القيمة |
|-------|--------|
| **Kong Service** | `yield-prediction` (DEPRECATED) |
| **Port** | 3021 |
| **Kong Routes** | `/yield-legacy` |
| **Framework** | NestJS |

> ⚠️ **ملاحظة**: هذه الخدمة مهملة. استخدم `yield-prediction-service` (Port 8098) بدلاً منها.

| Method | Endpoint | Input | Output | الوصف |
|--------|----------|-------|--------|-------|
| GET | `/yield/predict/:fieldId` | Path: `fieldId` | `YieldPrediction` | توقع المحصول |
| GET | `/yield/growth-stage/:fieldId` | Path: `fieldId` | `GrowthStage` | مرحلة النمو |
| GET | `/yield/harvest-date/:fieldId` | Path: `fieldId` | `HarvestDate` | تاريخ الحصاد |
| GET | `/yield/regional/:governorate` | Query: `cropType`, `year` | `RegionalStats` | إحصائيات المنطقة |
| GET | `/yield/history/:fieldId` | Query: `years` | `{fieldId, history[]}` | سجل المحاصيل |
| GET | `/yield/maturity/:fieldId` | Path: `fieldId` | `MaturityResponse` | نضج المحصول |
| GET | `/yield/predict-with-action/:fieldId` | Query: `farmerId`, `tenantId` | `ActionTemplate` | توقع مع إجراء |
| GET | `/yield/harvest-readiness/:fieldId` | Query: `farmerId` | `HarvestReadiness` | جاهزية الحصاد |

---

### 7. LAI Estimation | خدمة تقدير مؤشر مساحة الورق

| البند | القيمة |
|-------|--------|
| **Kong Service** | `lai-estimation` (DEPRECATED) |
| **Port** | 3022 |
| **Kong Routes** | `/lai-legacy` |
| **Framework** | NestJS |

> ⚠️ **ملاحظة**: هذه الخدمة مهملة.

| Method | Endpoint | Input | Output | الوصف |
|--------|----------|-------|--------|-------|
| GET | `/lai/estimate/:fieldId` | Query: `dataSource`, `cropType`, `date` | `LAIEstimate` | تقدير LAI |
| POST | `/lai/calculate` | `{bands, cropType, growthStage}` | `{lai, vegetationIndices}` | حساب LAI |
| GET | `/lai/timeseries/:fieldId` | Query: `startDate`, `endDate` | `{timeSeries: LAIRecord[]}` | سلسلة زمنية |
| GET | `/lai/compare/:fieldId` | Query: `cropType` | `LAIComparison` | مقارنة LAI |
| GET | `/lai/model/info` | - | `ModelInfo` | معلومات النموذج |
| GET | `/lai/stress-detection/:fieldId` | Query: `cropType`, `farmerId` | `StressDetection` | كشف الإجهاد |
| GET | `/lai/anomaly-check/:fieldId` | Query: `cropType`, `farmerId` | `AnomalyCheck` | فحص الشذوذ |

---

### 8. Crop Growth Model | نموذج نمو المحصول

| البند | القيمة |
|-------|--------|
| **Kong Service** | `crop-growth-model` (DEPRECATED) |
| **Port** | 3023 |
| **Kong Routes** | `/crop-growth-legacy` |
| **Framework** | NestJS |

> ⚠️ **ملاحظة**: هذه الخدمة مهملة.

| Method | Endpoint | Input | Output | الوصف |
|--------|----------|-------|--------|-------|
| POST | `/irrigation-decision/method-selector` | `MethodSelectorDto` | `{scenario, recommendation}` | اختيار طريقة الري |
| POST | `/irrigation-decision/calculate-etc` | `ETcCalculateDto` | `{input, result, methodology}` | حساب ETc |
| POST | `/irrigation-decision/threshold-control` | `ThresholdControlDto` | `{input, recommendation}` | التحكم بالعتبة |
| POST | `/irrigation-decision/smart-schedule` | `SmartScheduleDto` | `{parameters, schedule[]}` | جدول ري ذكي |
| GET | `/irrigation-decision/compare-methods` | - | `{methods[], comparison}` | مقارنة الطرق |
| GET | `/irrigation-decision/quick-recommend` | Query: `scenario` | `{recommendation}` | توصية سريعة |
| GET | `/irrigation-decision/crops` | - | `{crops[], total}` | قائمة المحاصيل |
| GET | `/irrigation-decision/crops/:cropType` | Path: `cropType` | `{cropType, params}` | معاملات المحصول |
| GET | `/irrigation-decision/soils` | - | `{soils[], total}` | أنواع التربة |
| GET | `/irrigation-decision/soils/:soilType` | Path: `soilType` | `{soilType, properties}` | خصائص التربة |

**Input Models:**

```typescript
// MethodSelectorDto
{
  budget: "high" | "medium" | "low";
  terrain: "plain" | "mountain" | "greenhouse" | "terrace";
  cropType: string;
  cropValue: "high" | "medium" | "low";
  technicalCapability: "advanced" | "basic" | "minimal";
  waterAvailability: "abundant" | "limited" | "scarce";
}

// ETcCalculateDto
{
  cropType: string;
  daysAfterPlanting: number;
  et0: number;                    // mm/day
  soilType: "sandy" | "loam" | "clay" | "silt";
  stressCoefficient?: number;     // 0-1
  growthStageAdjustment?: boolean;
}

// SmartScheduleDto
{
  cropType: string;
  sowingDate: string;
  soilParams: {
    fieldCapacity: number;
    wiltingPoint: number;
    currentMoisture: number;
    soilType: string;
  };
  weatherForecast: WeatherDay[];
  irrigationSystem: {
    type: "drip" | "sprinkler" | "furrow" | "flood";
    efficiency: number;
  };
  budget: "high" | "medium" | "low";
}
```

---

### 9. IoT Service | خدمة إنترنت الأشياء

| البند | القيمة |
|-------|--------|
| **Kong Service** | `iot-service` |
| **Port** | 8117 |
| **Kong Routes** | `/api/v1/iot`, `/iot` |
| **Framework** | NestJS |

| Method | Endpoint | Input | Output | الوصف |
|--------|----------|-------|--------|-------|
| GET | `/iot/health` | - | `{status, service, timestamp}` | فحص الصحة |
| GET | `/iot/field/:fieldId/sensors` | Path: `fieldId` | `{sensors: SensorReading[]}` | قراءات المستشعرات |
| GET | `/iot/field/:fieldId/sensor/:sensorType` | Path: `fieldId`, `sensorType` | `SensorReading` | قراءة مستشعر واحد |
| POST | `/iot/field/:fieldId/pump` | `{status, duration}` | `{success, message}` | تشغيل/إيقاف المضخة |
| POST | `/iot/field/:fieldId/valve/:valveId` | `{status}` | `{success, message}` | تشغيل/إيقاف الصمام |
| POST | `/iot/field/:fieldId/irrigation/schedule` | `ScheduleDto` | `{success, message}` | جدولة الري |
| GET | `/iot/field/:fieldId/actuators` | Path: `fieldId` | `{pump, valves}` | حالة المشغلات |
| GET | `/iot/devices` | - | `{devices[], stats}` | الأجهزة المتصلة |
| GET | `/iot/dashboard/:fieldId` | Path: `fieldId` | `DashboardData` | لوحة بيانات IoT |

**Enums:**

```typescript
enum SensorType {
  TEMPERATURE = "temperature",
  HUMIDITY = "humidity",
  SOIL_MOISTURE = "soil_moisture",
  EC = "ec",
  PH = "ph",
  SOIL_TEMP = "soil_temp"
}
```

---

### 10. Community Chat | خدمة المحادثة المجتمعية

| البند | القيمة |
|-------|--------|
| **Kong Service** | `community-chat` |
| **Port** | 8097 |
| **Kong Routes** | `/api/v1/community`, `/api/v1/posts`, `/community` |
| **Framework** | Express + Socket.io |

#### REST Endpoints

| Method | Endpoint | Input | Output | الوصف |
|--------|----------|-------|--------|-------|
| GET | `/healthz` | - | `HealthResponse` | فحص الصحة |
| GET | `/v1/requests` | Query: `status` | `{requests: SupportRequest[]}` | طلبات الدعم |
| GET | `/v1/rooms/:roomId/messages` | Path: `roomId` | `{roomId, messages[]}` | سجل الرسائل |
| GET | `/v1/experts/online` | - | `{count, available}` | الخبراء المتصلين |
| GET | `/v1/stats` | - | `ServiceStats` | إحصائيات الخدمة |

#### WebSocket Events (Client → Server)

| Event | Payload | الوصف |
|-------|---------|-------|
| `register_user` | `{userId, userName, userType, governorate}` | تسجيل المستخدم |
| `join_room` | `{roomId, userName, userType}` | الانضمام لغرفة |
| `send_message` | `{roomId, author, authorType, message, attachments?}` | إرسال رسالة |
| `typing_start` | `{roomId, userName}` | بدء الكتابة |
| `typing_stop` | `{roomId, userName}` | إيقاف الكتابة |
| `request_expert` | `{farmerId, farmerName, governorate, topic, diagnosisId?}` | طلب خبير |
| `accept_request` | `{roomId, expertId, expertName}` | قبول الطلب |
| `leave_room` | `{roomId, userName}` | مغادرة الغرفة |

#### WebSocket Events (Server → Client)

| Event | Payload | الوصف |
|-------|---------|-------|
| `registration_confirmed` | `{success, socketId, onlineExperts}` | تأكيد التسجيل |
| `load_history` | `Message[]` | تحميل السجل |
| `receive_message` | `Message` | استلام رسالة |
| `user_joined` | `{userName, userType, time}` | انضمام مستخدم |
| `user_left` | `{userName, time}` | مغادرة مستخدم |
| `user_typing` | `{userName, isTyping}` | مؤشر الكتابة |
| `expert_online` | `{expertId, expertName}` | خبير متصل |
| `expert_offline` | `{expertId}` | خبير غير متصل |
| `new_support_request` | `SupportRequest` | طلب دعم جديد |
| `expert_joined` | `{expertId, expertName, message}` | انضمام خبير |
| `error` | `{code, message}` | خطأ |

---

### 11. Chat Service | خدمة المحادثة

| البند | القيمة |
|-------|--------|
| **Kong Service** | `chat-service` |
| **Port** | 8000 |
| **Kong Routes** | `/api/v1/chat`, `/chat` |
| **Framework** | NestJS + Socket.io |

| Method | Endpoint | Input | Output | الوصف |
|--------|----------|-------|--------|-------|
| GET | `/chat/health` | - | `{status, service}` | فحص الصحة |
| POST | `/chat/conversations` | `{participantIds, subject?, type?}` | `Conversation` | إنشاء محادثة |
| GET | `/chat/conversations/me` | Header: `Authorization` | `{conversations[]}` | محادثاتي |
| GET | `/chat/conversations/:id` | Path: `id` | `{conversation}` | تفاصيل المحادثة |
| GET | `/chat/conversations/:id/messages` | Query: `page`, `limit` | `{messages[], pagination}` | رسائل المحادثة |
| POST | `/chat/messages` | `{conversationId, content, attachments?}` | `Message` | إرسال رسالة |
| POST | `/chat/messages/:messageId/read` | Path: `messageId` | `{messageId, readAt}` | تحديد كمقروء |
| POST | `/chat/conversations/:id/read` | Path: `id` | `{conversationId, readAt}` | تحديد الكل كمقروء |
| GET | `/chat/unread-count` | Header: `Authorization` | `{userId, unreadCount}` | عدد غير المقروء |

---

## خدمات Python | Python Services

### 12. Vegetation Analysis Service | خدمة تحليل الغطاء النباتي

| البند | القيمة |
|-------|--------|
| **Kong Service** | `vegetation-analysis-service` |
| **Port** | 8090 |
| **Kong Routes** | `/api/v1/vegetation`, `/vegetation`, `/api/v1/satellite`, `/satellite`, `/api/v1/ndvi`, `/ndvi` |
| **Framework** | FastAPI |

| Method | Endpoint | Input | Output | الوصف |
|--------|----------|-------|--------|-------|
| GET | `/healthz` | - | `{status, service, version}` | فحص الصحة |
| GET | `/readyz` | - | `{status, database}` | فحص الجاهزية |
| GET | `/v1/providers` | - | `{providers[]}` | مزودي البيانات |
| GET | `/v1/satellites` | - | `{satellites[]}` | مصادر الأقمار الصناعية |
| GET | `/v1/regions` | - | `{regions[]}` | المناطق المتاحة |
| POST | `/v1/imagery/request` | `ImageryRequest` | `SatelliteImagery` | طلب صورة قمر صناعي |
| POST | `/v1/analyze` | `AnalyzeRequest` | `FieldAnalysis` | تحليل الحقل |
| POST | `/v1/analyze-with-action` | `AnalyzeWithActionRequest` | `{..., actionTemplate}` | تحليل مع إجراء |
| GET | `/v1/timeseries/{field_id}` | Path: `field_id` | `TimeSeriesResponse` | سلسلة زمنية NDVI |
| POST | `/v1/ndvi-timeseries/analyze/{field_id}` | `TimeSeriesAnalysisRequest` | `{trends, anomalies}` | تحليل الاتجاهات |
| GET | `/v1/phenology/{field_id}` | Path: `field_id` | `PhenologyResponse` | مرحلة النمو |
| GET | `/v1/phenology/{field_id}/timeline` | Path: `field_id` | `TimelineResponse` | جدول زمني للنمو |
| POST | `/v1/yield-prediction` | `YieldPredictionRequest` | `YieldPredictionResponse` | توقع المحصول |
| GET | `/v1/yield-history/{field_id}` | Path: `field_id` | `{history[]}` | سجل المحاصيل |
| GET | `/v1/indices/{field_id}` | Path: `field_id` | `IndicesResponse` | جميع المؤشرات |
| POST | `/v1/indices/interpret` | `InterpretRequest` | `IndexInterpretationResponse` | تفسير المؤشرات |
| GET | `/v1/cloud-cover/{field_id}` | Path: `field_id` | `CloudCoverResponse` | تغطية السحب |
| GET | `/v1/changes/{field_id}` | Path: `field_id` | `ChangeReportResponse` | تقرير التغييرات |
| POST | `/v1/vra/generate` | `VRARequest` | `PrescriptionMapResponse` | توليد خريطة VRT |
| POST | `/v1/boundaries/detect` | `BoundaryRequest` | `{boundaries[]}` | كشف حدود الحقل |
| GET | `/v1/gdd/chart/{field_id}` | Path: `field_id` | `GDDChartResponse` | رسم درجات النمو |
| GET | `/v1/spray/forecast` | Query params | `SprayForecastResponse` | توقع الرش |
| GET | `/v1/export/analysis/{field_id}` | Path: `field_id` | `ExportResponse` | تصدير التحليل |

**Input Models:**

```python
class ImageryRequest(BaseModel):
    tenant_id: str
    field_id: str
    lat: float
    lon: float
    start_date: date
    end_date: date

class AnalyzeRequest(BaseModel):
    tenant_id: str
    field_id: str
    crop_type: str
    include_recommendations: bool = True

class YieldPredictionRequest(BaseModel):
    field_id: str
    ndvi: float          # -1 to 1
    evi: float           # -1 to 1
    historical_yield: Optional[float]
```

**Output Models:**

```python
class FieldAnalysis(BaseModel):
    field_id: str
    indices: Dict[str, float]
    crop_type: str
    phenology_stage: str
    alerts: List[Alert]
    recommendations: List[str]
    timestamp: datetime

class SatelliteImagery(BaseModel):
    image_id: str
    field_id: str
    date: date
    source: str
    cloud_cover_pct: float
    url: str

class YieldPredictionResponse(BaseModel):
    predicted_yield_kg_ha: float
    confidence: float
    recommendations: List[str]
```

---

### 13. Indicators Service | خدمة المؤشرات

| البند | القيمة |
|-------|--------|
| **Kong Service** | `indicators-service` |
| **Port** | 8091 |
| **Kong Routes** | `/api/v1/indicators`, `/indicators` |
| **Framework** | FastAPI |

| Method | Endpoint | Input | Output | الوصف |
|--------|----------|-------|--------|-------|
| GET | `/healthz` | - | `{status}` | فحص الصحة |
| GET | `/readyz` | - | `{status}` | فحص الجاهزية |
| GET | `/v1/indicators/definitions` | - | `{definitions[]}` | تعريفات المؤشرات |
| GET | `/v1/field/{field_id}/indicators` | Query: `category` | `FieldIndicators` | مؤشرات الحقل |
| GET | `/v1/dashboard/{tenant_id}` | Query: `num_fields` | `DashboardSummary` | لوحة المتابعة |
| GET | `/v1/alerts/{tenant_id}` | Query: `severity`, `limit` | `AlertsResponse` | تنبيهات المستأجر |
| GET | `/v1/trends/{field_id}/{indicator_id}` | Query: `days` (7-365) | `TrendResponse` | اتجاهات المؤشر |

**Enums:**

```python
class IndicatorCategory(str, Enum):
    VEGETATION = "vegetation"
    WATER = "water"
    SOIL = "soil"
    WEATHER = "weather"
    CROP_HEALTH = "crop_health"
    PRODUCTIVITY = "productivity"
    FINANCIAL = "financial"

class AlertSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

class TrendDirection(str, Enum):
    UP = "up"
    DOWN = "down"
    STABLE = "stable"
```

**Output Models:**

```python
class Indicator(BaseModel):
    id: str
    name_ar: str
    name_en: str
    category: IndicatorCategory
    value: float
    unit: str
    status: str
    trend: TrendDirection
    last_updated: datetime

class FieldIndicators(BaseModel):
    field_id: str
    area_hectares: float
    crop_type: str
    indicators: List[Indicator]
    overall_score: float
    alerts: List[IndicatorAlert]

class DashboardSummary(BaseModel):
    tenant_id: str
    total_fields: int
    average_health_score: float
    indicators_summary: Dict[str, Any]
    alerts: List[IndicatorAlert]
```

---

### 14. Weather Service | خدمة الطقس

| البند | القيمة |
|-------|--------|
| **Kong Service** | `weather-service` |
| **Port** | 8092 |
| **Kong Routes** | `/api/v1/weather`, `/weather` |
| **Framework** | FastAPI |

| Method | Endpoint | Input | Output | الوصف |
|--------|----------|-------|--------|-------|
| GET | `/healthz` | - | `{status}` | فحص الصحة |
| GET | `/readyz` | - | `{status}` | فحص الجاهزية |
| POST | `/weather/assess` | `WeatherAssessRequest` | `WeatherAssessment` | تقييم الطقس |
| POST | `/weather/current` | `LocationRequest` | `CurrentWeatherResponse` | الطقس الحالي |
| POST | `/weather/forecast` | `LocationRequest` | `ForecastResponse` | توقع 7-16 يوم |
| POST | `/weather/irrigation` | `IrrigationRequest` | `IrrigationAdjustmentResponse` | تعديل الري |
| POST | `/weather/evapotranspiration` | `ETRequest` | `ETResponse` | حساب ET0 |
| POST | `/weather/gdd` | `GDDRequest` | `GDDResponse` | درجات النمو |
| POST | `/weather/spray-window` | `SprayWindowRequest` | `SprayWindowResponse` | نافذة الرش |
| POST | `/weather/frost-risk` | `FrostRiskRequest` | `FrostRiskResponse` | مخاطر الصقيع |
| POST/GET | `/weather/heat-stress` | `HeatStressRequest`/`temp_c` | `HeatStressResponse` | مؤشر الحرارة |
| POST | `/weather/chill-hours` | `ChillHoursRequest` | `ChillHoursResponse` | ساعات البرد |
| POST | `/weather/drought-index` | `DroughtIndexRequest` | `DroughtIndexResponse` | مؤشر الجفاف |
| GET | `/weather/providers` | - | `ProvidersResponse` | مزودي الطقس |
| POST | `/weather/agricultural-report` | `LocationRequest` | `AgriculturalReportResponse` | تقرير زراعي شامل |
| POST | `/weather/comprehensive-stress-report` | `LocationRequest` | `StressReportResponse` | تقرير الإجهاد |

**Input Models:**

```python
class WeatherAssessRequest(BaseModel):
    tenant_id: str
    field_id: str
    temp_c: float
    humidity_pct: float
    wind_speed_kmh: float
    precipitation_mm: float
    uv_index: float

class LocationRequest(BaseModel):
    tenant_id: str
    field_id: str
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)

class ETRequest(BaseModel):
    temp_c: float
    humidity_pct: float
    wind_speed_kmh: float
    solar_radiation_mj: float

class GDDRequest(BaseModel):
    temp_max_c: float
    temp_min_c: float
    base_temp_c: float
    upper_temp_c: float

class FrostRiskRequest(BaseModel):
    temp_c: float
    humidity_pct: float
    wind_speed_kmh: float
    cloud_cover_pct: float
    dew_point_c: float

class ChillHoursRequest(BaseModel):
    hourly_temps: List[float]
    model: str = "simple"      # simple/utah/dynamic
    base_temp_c: float
```

---

### 15. Advisory Service | خدمة التوصيات

| البند | القيمة |
|-------|--------|
| **Kong Service** | `advisory-service` |
| **Port** | 8093 |
| **Kong Routes** | `/api/v1/advisory`, `/api/v1/fertilizer`, `/advisory`, `/fertilizer` |
| **Framework** | FastAPI |

| Method | Endpoint | Input | Output | الوصف |
|--------|----------|-------|--------|-------|
| GET | `/healthz` | - | `{status}` | فحص الصحة |
| GET | `/readyz` | - | `{status}` | فحص الجاهزية |
| POST | `/disease/assess` | `DiseaseAssessRequest` | `DiseaseResponse` | تقييم المرض |
| POST | `/disease/symptoms` | `SymptomAssessRequest` | `SymptomResponse` | تقييم الأعراض |
| GET | `/disease/search` | Query: `q`, `lang` | `SearchResponse` | بحث عن الأمراض |
| GET | `/disease/crop/{crop}` | Path: `crop` | `DiseaseListResponse` | أمراض المحصول |
| GET | `/disease/{disease_id}` | Path: `disease_id`, Query: `lang` | `DiseaseInfoResponse` | تفاصيل المرض |
| POST | `/nutrient/ndvi` | `NDVIAssessRequest` | `NutrientResponse` | تقييم من NDVI |
| POST | `/nutrient/visual` | `VisualAssessRequest` | `NutrientResponse` | تقييم بصري |
| GET | `/nutrient/{deficiency_id}` | Path: `deficiency_id` | `DeficiencyResponse` | تفاصيل النقص |
| POST | `/fertilizer/plan` | `FertilizerPlanRequest` | `FertilizerPlanResponse` | خطة التسميد |
| GET | `/fertilizer/{fertilizer_id}` | Path: `fertilizer_id` | `FertilizerResponse` | تفاصيل السماد |
| GET | `/fertilizer/nutrient/{nutrient}` | Path: `nutrient` | `FertilizersByNutrientResponse` | أسمدة حسب العنصر |
| GET | `/crops/categories` | - | `CategoriesResponse` | فئات المحاصيل |
| GET | `/crops/search` | Query: `q` (min 2 chars) | `SearchCropsResponse` | بحث المحاصيل |
| GET | `/crops` | Query: `limit`, `offset` | `AllCropsResponse` | قائمة المحاصيل |
| GET | `/crops/{crop_code}` | Path: `crop_code` | `CropDetailsResponse` | تفاصيل المحصول |
| GET | `/crops/{crop_code}/varieties` | Path: `crop_code` | `VarietiesResponse` | أصناف يمنية |
| GET | `/crops/{crop}/stages` | Path: `crop` | `StagesResponse` | مراحل النمو |
| GET | `/crops/{crop}/requirements` | Path: `crop` | `RequirementsResponse` | متطلبات المحصول |
| GET | `/actions/{action_id}` | Path: `action_id`, Query: `lang` | `ActionDetailsResponse` | تعليمات الإجراء |

**Input Models:**

```python
class DiseaseAssessRequest(BaseModel):
    tenant_id: str
    field_id: str
    condition_id: str
    confidence: float = Field(..., ge=0, le=1)
    crop: str
    weather: Dict[str, Any]

class SymptomAssessRequest(BaseModel):
    tenant_id: str
    field_id: str
    crop: str
    symptoms: List[str]
    lang: str = "ar"

class NDVIAssessRequest(BaseModel):
    tenant_id: str
    field_id: str
    ndvi: float = Field(..., ge=-1, le=1)
    crop: str
    stage: str

class VisualAssessRequest(BaseModel):
    tenant_id: str
    field_id: str
    leaf_color: str
    pattern: str
    crop: str
    lang: str = "ar"

class FertilizerPlanRequest(BaseModel):
    tenant_id: str
    field_id: str
    crop: str
    stage: str
    field_size_ha: float
    soil_fertility: str
    irrigation_type: str
```

---

### 16. Irrigation Smart | خدمة الري الذكي

| البند | القيمة |
|-------|--------|
| **Kong Service** | `irrigation-smart` |
| **Port** | 8094 |
| **Kong Routes** | `/api/v1/irrigation`, `/irrigation` |
| **Framework** | FastAPI |

| Method | Endpoint | Input | Output | الوصف |
|--------|----------|-------|--------|-------|
| GET | `/healthz` | - | `{status}` | فحص الصحة |
| GET | `/readyz` | - | `{status}` | فحص الجاهزية |
| GET | `/v1/crops` | - | `CropsListResponse` | المحاصيل المدعومة |
| GET | `/v1/methods` | - | `MethodsListResponse` | طرق الري |
| POST | `/v1/calculate` | `IrrigationRequest` | `IrrigationPlan` | حساب احتياجات الري |
| GET | `/v1/water-balance/{field_id}` | Query: `crop`, `days` | `WaterBalanceResponse` | ميزانية المياه |
| POST | `/v1/sensor-reading` | `SoilMoistureReading` | `ReadingResponse` | تسجيل قراءة |
| GET | `/v1/efficiency-report/{field_id}` | Query: `current_method`, `area_hectares` | `EfficiencyReportResponse` | تقرير الكفاءة |
| POST | `/v1/calculate-with-action` | `IrrigationRequest` | `PlanWithActionResponse` | حساب مع إجراء |
| POST | `/v1/sensor-reading-with-action` | `SoilMoistureReading` | `ReadingWithActionResponse` | قراءة مع إجراء |

**Input Models:**

```python
class IrrigationRequest(BaseModel):
    field_id: str
    crop: CropType
    growth_stage: GrowthStage
    area_hectares: float
    soil_type: SoilType
    irrigation_method: str
    current_soil_moisture: float = Field(..., ge=0, le=100)
    last_irrigation_date: date
    weather_forecast: List[WeatherDay]

class SoilMoistureReading(BaseModel):
    field_id: str
    sensor_id: str
    reading_time: datetime
    depth_cm: float
    moisture_percent: float = Field(..., ge=0, le=100)
    temperature_c: Optional[float]
    ec_ds_m: Optional[float]
```

**Output Models:**

```python
class IrrigationPlan(BaseModel):
    plan_id: str
    field_id: str
    crop: str
    schedules: List[IrrigationSchedule]
    total_water_m3: float
    estimated_cost_yer: float
    water_savings_m3: float
    recommendations_ar: List[str]
    recommendations_en: List[str]
    alerts_ar: List[str]

class IrrigationSchedule(BaseModel):
    schedule_id: str
    irrigation_date: date
    start_time: time
    duration_minutes: int
    water_amount_liters: float
    water_amount_m3: float
    urgency: UrgencyLevel
    reasoning_ar: str
    reasoning_en: str
    weather_adjusted: bool
    savings_percent: float

class WaterBalance(BaseModel):
    field_id: str
    date: date
    et_mm: float
    rainfall_mm: float
    irrigation_mm: float
    soil_moisture_change_mm: float
    water_deficit_mm: float
    cumulative_deficit_mm: float
```

**Enums:**

```python
class CropType(str, Enum):
    TOMATO = "tomato"
    WHEAT = "wheat"
    COFFEE = "coffee"
    QAT = "qat"
    # ... 15 types

class GrowthStage(str, Enum):
    SEEDLING = "seedling"
    VEGETATIVE = "vegetative"
    FLOWERING = "flowering"
    FRUITING = "fruiting"
    MATURITY = "maturity"

class SoilType(str, Enum):
    SANDY = "sandy"
    SANDY_LOAM = "sandy_loam"
    LOAM = "loam"
    CLAY_LOAM = "clay_loam"
    CLAY = "clay"
    SILTY_CLAY = "silty_clay"

class UrgencyLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
```

---

### 17. Crop Intelligence Service | خدمة الذكاء الزراعي

| البند | القيمة |
|-------|--------|
| **Kong Service** | `crop-intelligence-service` |
| **Port** | 8095 |
| **Kong Routes** | `/api/v1/crop-health`, `/api/v1/crop`, `/crop` |
| **Framework** | FastAPI |

| Method | Endpoint | Input | Output | الوصف |
|--------|----------|-------|--------|-------|
| GET | `/healthz` | - | `{status}` | فحص الصحة |
| GET | `/readyz` | - | `{status}` | فحص الجاهزية |
| POST | `/api/v1/fields/{field_id}/zones` | `ZoneCreate` | `ZoneCreatedResponse` | إنشاء منطقة |
| GET | `/api/v1/fields/{field_id}/zones` | Path: `field_id` | `ZonesListResponse` | قائمة المناطق |
| GET | `/api/v1/fields/{field_id}/zones.geojson` | Path: `field_id` | `GeoJSONResponse` | مناطق GeoJSON |
| POST | `/api/v1/fields/{field_id}/zones/{zone_id}/observations` | `ObservationIn` | `ObservationOut` | إضافة ملاحظة |
| GET | `/api/v1/fields/{field_id}/zones/{zone_id}/observations` | Query: `limit` | `ObservationsListResponse` | قائمة الملاحظات |
| GET | `/api/v1/fields/{field_id}/diagnosis` | Query: `date` | `FieldDiagnosisOut` | تشخيص الحقل |
| GET | `/api/v1/fields/{field_id}/zones/{zone_id}/timeline` | Query: `from`, `to` | `ZoneTimelineOut` | خط زمني |
| GET | `/api/v1/fields/{field_id}/vrt` | Query: `date`, `action_type` | `VRTExportOut` | خريطة VRT |
| POST | `/api/v1/diagnose` | `ObservationIn` | `DiagnosisResponse` | تشخيص سريع |
| POST | `/api/v1/disease/detect` | `DiseaseDetectionRequest` | `DiseaseDetectionResponse` | كشف الأمراض |
| GET | `/api/v1/fields/{field_id}/zones/{zone_id}/disease-analysis` | Query params | `DiseaseAnalysisResponse` | تحليل الأمراض |
| GET | `/api/v1/disease/types` | - | `DiseaseTypesResponse` | أنواع الأمراض |
| POST | `/api/v1/nutrients/detect` | `NutrientDetectionRequest` | `NutrientDetectionResponse` | كشف النقص الغذائي |
| POST | `/api/v1/nutrients/fertilizer-plan` | `FertilizerPlanRequest` | `FertilizerPlanResponse` | خطة تسميد |
| GET | `/api/v1/fields/{field_id}/zones/{zone_id}/nutrient-analysis` | Query params | `NutrientAnalysisResponse` | تحليل التغذية |
| GET | `/api/v1/nutrients/types` | - | `NutrientTypesResponse` | أنواع العناصر |
| POST | `/api/v1/yield/predict` | `YieldPredictionRequest` | `YieldPredictionResponse` | توقع المحصول |
| GET | `/api/v1/fields/{field_id}/zones/{zone_id}/yield-prediction` | Query params | `ZoneYieldResponse` | توقع محصول المنطقة |
| GET | `/api/v1/yield/crop-parameters` | Query: `crop_type` | `CropParametersResponse` | معاملات المحصول |
| POST | `/api/v1/pests/assess` | `PestAssessmentRequest` | `PestAssessmentResponse` | تقييم الآفات |
| GET | `/api/v1/fields/{field_id}/zones/{zone_id}/pest-assessment` | Query params | `ZonePestResponse` | تقييم آفات المنطقة |
| GET | `/api/v1/pests/types` | - | `PestTypesResponse` | أنواع الآفات |
| POST | `/api/v1/comprehensive-analysis` | Query params | `ComprehensiveAnalysisResponse` | تحليل شامل |

**Input Models:**

```python
class IndicesIn(BaseModel):
    ndvi: float = Field(..., ge=-1, le=1)
    evi: float = Field(..., ge=-1, le=1)
    ndre: float = Field(..., ge=-1, le=1)
    lci: float = Field(..., ge=-1, le=1)
    ndwi: float = Field(..., ge=-1, le=1)
    savi: float = Field(..., ge=-1, le=1)

class ObservationIn(BaseModel):
    captured_at: datetime
    source: str             # sentinel-2/drone/planet/landsat
    growth_stage: str
    indices: IndicesIn
    cloud_pct: float = Field(..., ge=0, le=100)
    notes: Optional[str]

class ZoneCreate(BaseModel):
    name: str
    name_ar: str
    geometry: Dict          # GeoJSON geometry
    area_hectares: float

class DiseaseDetectionRequest(BaseModel):
    ndvi: float
    evi: float
    ndre: float
    ndwi: float
    lci: float
    savi: float
    crop_type: str
    humidity_pct: float
    temp_c: float

class NutrientDetectionRequest(BaseModel):
    ndvi: float
    evi: float
    ndre: float
    ndwi: float
    lci: float
    savi: float
    growth_stage: str

class YieldPredictionRequest(BaseModel):
    crop_type: str
    ndvi: float
    evi: float
    ndwi: float
    ndre: float
    lci: float
    savi: float
    field_area_hectares: float
    growth_stage_percent: float

class PestAssessmentRequest(BaseModel):
    temp_c: float
    humidity_pct: float
    ndvi: float
    crop_type: str
    season: str
```

---

### 18-35. Additional Python Services (Summary)

#### خدمات إضافية | Additional Services

| # | Service | Port | Kong Route | الوصف |
|---|---------|------|------------|-------|
| 18 | `virtual-sensors` | 8119 | `/api/v1/virtual-sensors` | حساسات افتراضية (ET0, ETc) |
| 19 | `yield-prediction-service` | 8098 | `/api/v1/yield` | توقع المحصول ML |
| 20 | `field-chat` | 8099 | `/api/v1/field-chat` | محادثة الحقل |
| 21 | `equipment-service` | 8101 | `/api/v1/equipment` | إدارة المعدات |
| 22 | `task-service` | 8103 | `/api/v1/tasks` | إدارة المهام |
| 23 | `provider-config` | 8104 | `/api/v1/provider-config` | تكوين المزودين |
| 24 | `agro-advisor` | 8105 | `/api/v1/agro-advisor` | المستشار الزراعي |
| 25 | `iot-gateway` | 8106 | `/api/v1/iot-gateway` | بوابة IoT |
| 26 | `weather-core` | 8108 | `/api/v1/weather-core` | تقييم الطقس المتقدم |
| 27 | `notification-service` | 8110 | `/api/v1/notifications` | الإشعارات متعددة القنوات |
| 28 | `astronomical-calendar` | 8111 | `/api/v1/astronomy` | التقويم الفلكي اليمني |
| 29 | `ai-advisor` | 8112 | `/api/v1/ai-advisor` | مستشار AI متعدد الوكلاء |
| 30 | `alert-service` | 8113 | `/api/v1/alerts` | إدارة التنبيهات |
| 31 | `inventory-service` | 8116 | `/api/v1/inventory` | إدارة المخزون |
| 32 | `ndvi-processor` | 8118 | `/ndvi-processor-legacy` | معالجة NDVI |
| 33 | `field-intelligence` | 8120 | `/api/v1/field-intelligence` | محرك القواعد |
| 34 | `mcp-server` | 8200 | `/api/v1/mcp` | بروتوكول سياق النموذج |
| 35 | `skills-service` | 8121 | `/api/v1/skills` | ضغط وتقييم المهارات |

---

## الخدمات المضافة حديثاً | Newly Registered Services

> تاريخ الإضافة: 2026-01-23

### 36. Audit Service | خدمة التدقيق

| البند | القيمة |
|-------|--------|
| **Kong Service** | `audit-service` |
| **Port** | 8114 |
| **Kong Routes** | `/api/v1/audit`, `/audit` |
| **Framework** | FastAPI |

| Method | Endpoint | Input | Output | الوصف |
|--------|----------|-------|--------|-------|
| GET | `/healthz` | - | `{status}` | فحص الصحة |
| GET | `/readyz` | - | `{status, database, integrity}` | فحص الجاهزية |
| POST | `/v1/audit/log` | `AuditLogEntry` | `{entry_id, hash}` | تسجيل حدث |
| GET | `/v1/audit/logs` | Query: `tenant_id`, `entity_type`, `from`, `to` | `{logs[], total}` | استعراض السجلات |
| GET | `/v1/audit/logs/{entry_id}` | Path: `entry_id` | `AuditLogEntry` | سجل واحد |
| POST | `/v1/audit/verify` | `{entry_id}` | `{valid, hash, chain_valid}` | التحقق من السلامة |
| GET | `/v1/audit/chain/status` | - | `{chain_length, last_hash, valid}` | حالة السلسلة |

**Input Model:**

```python
class AuditLogEntry(BaseModel):
    tenant_id: str
    user_id: str
    action: str               # CREATE, UPDATE, DELETE, READ, LOGIN, LOGOUT
    entity_type: str          # field, user, task, etc.
    entity_id: str
    changes: Optional[Dict]
    ip_address: Optional[str]
    user_agent: Optional[str]
    metadata: Optional[Dict]
```

---

### 37. CRM Service | خدمة إدارة العلاقات

| البند | القيمة |
|-------|--------|
| **Kong Service** | `crm-service` |
| **Port** | 8131 |
| **Kong Routes** | `/api/v1/crm`, `/crm` |
| **Framework** | FastAPI |

| Method | Endpoint | Input | Output | الوصف |
|--------|----------|-------|--------|-------|
| GET | `/healthz` | - | `{status}` | فحص الصحة |
| POST | `/v1/contacts` | `ContactCreate` | `Contact` | إنشاء جهة اتصال |
| GET | `/v1/contacts` | Query: `tenant_id`, `segment`, `status` | `{contacts[], total}` | قائمة جهات الاتصال |
| GET | `/v1/contacts/{contact_id}` | Path: `contact_id` | `Contact` | جهة اتصال واحدة |
| PUT | `/v1/contacts/{contact_id}` | `ContactUpdate` | `Contact` | تحديث جهة اتصال |
| POST | `/v1/deals` | `DealCreate` | `Deal` | إنشاء صفقة |
| GET | `/v1/deals` | Query: `tenant_id`, `stage`, `assigned_to` | `{deals[], total}` | قائمة الصفقات |
| PUT | `/v1/deals/{deal_id}/stage` | `{stage}` | `Deal` | تحديث مرحلة الصفقة |
| POST | `/v1/activities` | `ActivityCreate` | `Activity` | تسجيل نشاط |
| GET | `/v1/contacts/{contact_id}/activities` | Path: `contact_id` | `{activities[]}` | أنشطة جهة اتصال |
| GET | `/v1/pipeline/summary` | Query: `tenant_id` | `PipelineSummary` | ملخص خط المبيعات |

**Models:**

```python
class Contact(BaseModel):
    contact_id: str
    name: str
    name_ar: str
    phone: str
    email: Optional[str]
    governorate: str
    farm_size_hectares: Optional[float]
    crops: List[str]
    segment: str              # small_holder, medium, large, enterprise
    status: str               # lead, prospect, customer, churned
    created_at: datetime

class Deal(BaseModel):
    deal_id: str
    contact_id: str
    title: str
    value: float
    currency: str
    stage: str                # lead, qualified, proposal, negotiation, closed_won, closed_lost
    probability: float
    expected_close: date
    assigned_to: str
    created_at: datetime
```

---

### 38. GlobalGAP Compliance | خدمة الامتثال للجودة العالمية

| البند | القيمة |
|-------|--------|
| **Kong Service** | `globalgap-compliance` |
| **Port** | 8123 |
| **Kong Routes** | `/api/v1/globalgap`, `/globalgap` |
| **Framework** | FastAPI |

| Method | Endpoint | Input | Output | الوصف |
|--------|----------|-------|--------|-------|
| GET | `/healthz` | - | `{status}` | فحص الصحة |
| POST | `/v1/certifications` | `CertificationCreate` | `Certification` | بدء شهادة |
| GET | `/v1/certifications` | Query: `tenant_id`, `status` | `{certifications[]}` | قائمة الشهادات |
| GET | `/v1/certifications/{cert_id}` | Path: `cert_id` | `Certification` | تفاصيل الشهادة |
| POST | `/v1/checklists/{cert_id}` | `ChecklistItem` | `ChecklistItem` | إضافة عنصر فحص |
| GET | `/v1/checklists/{cert_id}` | Path: `cert_id` | `{checklist[]}` | قائمة الفحص |
| PUT | `/v1/checklists/{cert_id}/{item_id}` | `ChecklistUpdate` | `ChecklistItem` | تحديث عنصر |
| GET | `/v1/certifications/{cert_id}/score` | Path: `cert_id` | `ComplianceScore` | نقاط الامتثال |
| POST | `/v1/documents/{cert_id}` | `DocumentUpload` | `Document` | رفع مستند |
| GET | `/v1/standards` | - | `{standards[]}` | معايير IFA v6 |
| GET | `/v1/standards/{standard_id}/cpcc` | Path: `standard_id` | `{control_points[]}` | نقاط التحكم |

**Enums:**

```python
class ComplianceLevel(str, Enum):
    MAJOR_MUST = "major_must"
    MINOR_MUST = "minor_must"
    RECOMMENDATION = "recommendation"

class ChecklistStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    NOT_APPLICABLE = "not_applicable"
```

---

### 39. Logistics Service | خدمة اللوجستيات

| البند | القيمة |
|-------|--------|
| **Kong Service** | `logistics-service` |
| **Port** | 8162 |
| **Kong Routes** | `/api/v1/logistics`, `/logistics` |
| **Framework** | FastAPI |

| Method | Endpoint | Input | Output | الوصف |
|--------|----------|-------|--------|-------|
| GET | `/healthz` | - | `{status}` | فحص الصحة |
| POST | `/v1/fleet/vehicles` | `VehicleCreate` | `Vehicle` | إضافة مركبة |
| GET | `/v1/fleet/vehicles` | Query: `tenant_id`, `status` | `{vehicles[]}` | قائمة المركبات |
| GET | `/v1/fleet/vehicles/{vehicle_id}` | Path: `vehicle_id` | `Vehicle` | تفاصيل المركبة |
| PUT | `/v1/fleet/vehicles/{vehicle_id}/location` | `{lat, lon}` | `Vehicle` | تحديث الموقع |
| POST | `/v1/collections` | `CollectionCreate` | `Collection` | جدولة جمع |
| GET | `/v1/collections` | Query: `tenant_id`, `date`, `status` | `{collections[]}` | قائمة الجمع |
| PUT | `/v1/collections/{collection_id}/status` | `{status}` | `Collection` | تحديث الحالة |
| GET | `/v1/routes/optimize` | Query: `vehicle_id`, `date` | `OptimizedRoute` | تحسين المسار |
| GET | `/v1/deliveries/tracking/{delivery_id}` | Path: `delivery_id` | `DeliveryTracking` | تتبع التسليم |

---

### 40. USSD Gateway | بوابة USSD

| البند | القيمة |
|-------|--------|
| **Kong Service** | `ussd-gateway` |
| **Port** | 8163 |
| **Kong Routes** | `/api/v1/ussd`, `/ussd` |
| **Framework** | FastAPI |

| Method | Endpoint | Input | Output | الوصف |
|--------|----------|-------|--------|-------|
| GET | `/healthz` | - | `{status}` | فحص الصحة |
| POST | `/v1/ussd/session` | `USSDRequest` | `USSDResponse` | جلسة USSD |
| POST | `/v1/sms/send` | `SMSRequest` | `{message_id, status}` | إرسال SMS |
| GET | `/v1/sms/status/{message_id}` | Path: `message_id` | `SMSStatus` | حالة الرسالة |
| POST | `/v1/sms/receive` | `IncomingSMS` | `{acknowledged}` | استقبال SMS |
| GET | `/v1/menus` | Query: `lang` | `{menus[]}` | قوائم USSD |

**Input Models:**

```python
class USSDRequest(BaseModel):
    session_id: str
    msisdn: str               # phone number
    input: str
    service_code: str         # e.g., *123#
    network: str

class USSDResponse(BaseModel):
    session_id: str
    message: str
    message_ar: str
    action: str               # continue, end
    next_menu: Optional[str]
```

---

### 41. Agent Registry | سجل الوكلاء

| البند | القيمة |
|-------|--------|
| **Kong Service** | `agent-registry` |
| **Port** | 8160 |
| **Kong Routes** | `/api/v1/agents`, `/agents` |
| **Framework** | FastAPI |

| Method | Endpoint | Input | Output | الوصف |
|--------|----------|-------|--------|-------|
| GET | `/healthz` | - | `{status}` | فحص الصحة |
| POST | `/v1/agents/register` | `AgentCard` | `{agent_id, registered}` | تسجيل وكيل |
| GET | `/v1/agents` | Query: `capability`, `status` | `{agents[]}` | قائمة الوكلاء |
| GET | `/v1/agents/{agent_id}` | Path: `agent_id` | `AgentCard` | تفاصيل الوكيل |
| DELETE | `/v1/agents/{agent_id}` | Path: `agent_id` | `{success}` | إلغاء التسجيل |
| PUT | `/v1/agents/{agent_id}/heartbeat` | Path: `agent_id` | `{last_seen}` | نبض القلب |
| GET | `/v1/agents/discover` | Query: `capability`, `input_schema` | `{agents[]}` | اكتشاف الوكلاء |
| POST | `/v1/agents/{agent_id}/invoke` | `InvokeRequest` | `InvokeResponse` | استدعاء وكيل |

**Input Model (A2A Protocol):**

```python
class AgentCard(BaseModel):
    agent_id: str
    name: str
    name_ar: str
    description: str
    description_ar: str
    version: str
    capabilities: List[str]
    input_schema: Dict
    output_schema: Dict
    endpoint: str
    authentication: Dict
    status: str               # active, inactive, maintenance
```

---

### 42. AI Agents Core | نواة وكلاء AI

| البند | القيمة |
|-------|--------|
| **Kong Service** | `ai-agents-core` |
| **Port** | 8122 |
| **Kong Routes** | `/api/v1/ai-agents`, `/ai-agents` |
| **Framework** | FastAPI |

| Method | Endpoint | Input | Output | الوصف |
|--------|----------|-------|--------|-------|
| GET | `/healthz` | - | `{status}` | فحص الصحة |
| GET | `/v1/agents` | - | `{agents[]}` | قائمة الوكلاء |
| POST | `/v1/agents/execute` | `ExecuteRequest` | `ExecuteResponse` | تنفيذ مهمة |
| GET | `/v1/executions/{execution_id}` | Path: `execution_id` | `ExecutionStatus` | حالة التنفيذ |
| DELETE | `/v1/executions/{execution_id}` | Path: `execution_id` | `{cancelled}` | إلغاء التنفيذ |
| GET | `/v1/tools` | - | `{tools[]}` | الأدوات المتاحة |
| POST | `/v1/memory/store` | `MemoryEntry` | `{stored}` | تخزين في الذاكرة |
| GET | `/v1/memory/recall` | Query: `context`, `limit` | `{memories[]}` | استرجاع الذاكرة |

**Input Model:**

```python
class ExecuteRequest(BaseModel):
    agent_type: str           # field_analyst, disease_expert, irrigation_advisor
    task: str
    task_ar: Optional[str]
    context: Dict
    tenant_id: str
    field_id: Optional[str]
    max_steps: int = Field(default=50, ge=1, le=100)
    timeout_seconds: int = Field(default=300, ge=30, le=600)
```

---

### 43. Knowledge Graph | الرسم البياني المعرفي

| البند | القيمة |
|-------|--------|
| **Kong Service** | `knowledge-graph` |
| **Port** | 8140 |
| **Kong Routes** | `/api/v1/knowledge`, `/knowledge` |
| **Framework** | FastAPI |

| Method | Endpoint | Input | Output | الوصف |
|--------|----------|-------|--------|-------|
| GET | `/healthz` | - | `{status}` | فحص الصحة |
| GET | `/v1/entities/crops` | - | `{crops[]}` | المحاصيل |
| GET | `/v1/entities/diseases` | - | `{diseases[]}` | الأمراض |
| GET | `/v1/entities/treatments` | - | `{treatments[]}` | العلاجات |
| GET | `/v1/entities/search` | Query: `q`, `type` | `{entities[]}` | بحث الكيانات |
| GET | `/v1/relationships/affected-crops/{disease_id}` | Path: `disease_id` | `{crops[]}` | المحاصيل المتأثرة |
| GET | `/v1/relationships/disease-treatments/{disease_id}` | Path: `disease_id` | `{treatments[]}` | علاجات المرض |
| GET | `/v1/relationships/diseases-by-crop/{crop_id}` | Path: `crop_id` | `{diseases[]}` | أمراض المحصول |
| GET | `/v1/relationships/path/{source_type}/{source_id}/{target_type}/{target_id}` | Path params | `{path[]}` | المسار بين كيانين |
| GET | `/v1/graphs/stats` | - | `GraphStats` | إحصائيات الرسم |
| GET | `/v1/graphs/search` | Query: `q` | `{results[]}` | بحث الرسم |

---

### 44. Yield Engine | محرك توقع المحصول

| البند | القيمة |
|-------|--------|
| **Kong Service** | `yield-engine` |
| **Port** | 8098 |
| **Kong Routes** | `/api/v1/yield-engine`, `/yield-engine` |
| **Framework** | FastAPI |

| Method | Endpoint | Input | Output | الوصف |
|--------|----------|-------|--------|-------|
| GET | `/healthz` | - | `{status, model_ready}` | فحص الصحة |
| POST | `/v1/predict` | `YieldRequest` | `YieldPrediction` | توقع المحصول |
| GET | `/v1/crops` | - | `{crops[]}` | المحاصيل المدعومة |
| GET | `/v1/price/{crop_type}` | Path: `crop_type` | `{price_usd, price_yer}` | سعر المحصول |

**Input Model:**

```python
class YieldRequest(BaseModel):
    field_id: Optional[str]
    area_hectares: float = Field(..., gt=0)
    crop_type: CropType
    avg_rainfall: Optional[float] = Field(None, ge=0)
    avg_temperature: Optional[float]
    soil_quality: str = "medium"
    irrigation_type: str = "rain-fed"
    governorate: Optional[str]
    target_yield_kg_ha: Optional[float] = Field(None, ge=0)
```

**Output Model:**

```python
class YieldPrediction(BaseModel):
    prediction_id: str
    field_id: Optional[str]
    crop_type: str
    crop_name_ar: str
    area_hectares: float
    predicted_yield_tons: float
    predicted_yield_per_hectare: float
    yield_range_min: float
    yield_range_max: float
    estimated_revenue_usd: float
    estimated_revenue_yer: float
    confidence_percent: float
    factors_applied: List[str]
    recommendations: List[str]
    timestamp: datetime
```

---

### 45. AI Agents Service | خدمة وكلاء AI

| البند | القيمة |
|-------|--------|
| **Kong Service** | `ai-agents-service` |
| **Port** | 8130 |
| **Kong Routes** | `/api/v1/ai-agents-service`, `/ai-agents-service` |
| **Framework** | FastAPI |

| Method | Endpoint | Input | Output | Rate Limit |
|--------|----------|-------|--------|-----------|
| GET | `/api/v1/agents` | - | `{agents[]}` | 60/min |
| POST | `/api/v1/agents/execute` | `AgentExecuteRequest` | `AgentExecuteResponse` | 10/min |
| GET | `/api/v1/agents/executions/{execution_id}` | Path: `execution_id` | `AgentExecuteResponse` | 60/min |
| GET | `/api/v1/agents/executions/{execution_id}/status` | Path: `execution_id` | `ExecutionStatusResponse` | 60/min |
| DELETE | `/api/v1/agents/executions/{execution_id}` | Path: `execution_id` | `{cancelled}` | 60/min |
| GET | `/api/v1/agents/executions` | Query params | `{executions[]}` | 60/min |
| POST | `/api/v1/agents/quick/analyze` | `QuickAnalysisRequest` | `QuickAnalysisResponse` | 60/min |
| GET | `/metrics` | - | Prometheus | - |

**Input Models:**

```python
class AgentExecuteRequest(BaseModel):
    task: str
    task_ar: Optional[str]
    agent_type: str = "farm_advisor"
    mode: str = "hybrid"
    context: Optional[Dict]
    tenant_id: str
    field_id: Optional[str]
    farm_id: Optional[str]
    max_steps: int = Field(default=50, ge=1, le=100)
    timeout_seconds: int = Field(default=300, ge=30, le=600)

class QuickAnalysisRequest(BaseModel):
    field_id: str
    tenant_id: str
    analysis_type: str = "crop_health"
```

**Output Models:**

```python
class AgentExecuteResponse(BaseModel):
    execution_id: str
    tenant_id: str
    agent_type: str
    mode: str
    task: str
    status: str               # running, completed, failed, timeout
    state: str
    steps: List[AgentStep]
    final_result: Optional[Dict]
    error: Optional[str]
    started_at: datetime
    completed_at: Optional[datetime]
    total_duration_ms: Optional[int]

class AgentStep(BaseModel):
    step_number: int
    action: str
    action_ar: Optional[str]
    tool_used: Optional[str]
    result: Optional[Dict]
    timestamp: datetime
    duration_ms: Optional[int]
```

---

### 46. Field Core | خدمة الحقول الأساسية

| البند | القيمة |
|-------|--------|
| **Kong Service** | `field-core` |
| **Port** | 3005 |
| **Kong Routes** | `/api/v1/field-core`, `/field-core` |
| **Framework** | FastAPI |

| Method | Endpoint | Input | Output | الوصف |
|--------|----------|-------|--------|-------|
| GET | `/healthz` | - | `{status}` | فحص الصحة |
| GET | `/readyz` | - | `{status, database}` | فحص الجاهزية |
| GET | `/v1/profitability/crop/{crop_season_id}` | Query: `field_id`, `crop_code`, `area_ha` | `ProfitabilityReport` | ربحية المحصول |
| POST | `/v1/profitability/analyze` | `AnalyzeCropRequest` | `AnalysisResult` | تحليل الربحية |
| POST | `/v1/profitability/season` | `AnalyzeSeasonRequest` | `SeasonResult` | تحليل الموسم |
| GET | `/v1/profitability/compare` | Query: `crops`, `area_ha`, `region` | `ComparisonResult` | مقارنة المحاصيل |
| GET | `/v1/profitability/break-even` | Query params | `BreakEvenResult` | نقطة التعادل |
| GET | `/v1/profitability/history/{field_id}/{crop_code}` | Query: `years` | `{history[]}` | سجل الربحية |
| GET | `/v1/profitability/benchmarks/{crop_code}` | Query: `region` | `{benchmarks}` | معايير المنطقة |
| GET | `/v1/profitability/cost-breakdown/{crop_code}` | Query: `area_ha` | `{costs}` | تفصيل التكاليف |
| GET | `/v1/crops/list` | - | `{crops[]}` | قائمة المحاصيل |
| GET | `/v1/costs/categories` | - | `{categories[]}` | فئات التكاليف |

**Input Models:**

```python
class CostItemRequest(BaseModel):
    category: str
    description: str
    amount: float
    unit: str = "YER"
    quantity: float = 1.0
    unit_cost: Optional[float]

class RevenueItemRequest(BaseModel):
    description: str
    quantity: float
    unit: str = "kg"
    unit_price: float
    grade: Optional[str]

class AnalyzeCropRequest(BaseModel):
    field_id: str
    crop_season_id: str
    crop_code: str
    area_ha: float = Field(..., gt=0)
    costs: Optional[List[CostItemRequest]]
    revenues: Optional[List[RevenueItemRequest]]
```

---

## الخدمات المهملة | Deprecated Services

> ⚠️ **تحذير**: هذه الخدمات مهملة ويجب استخدام البدائل الموضحة.

| Service | Port | Kong Route | البديل | Alternative |
|---------|------|------------|--------|-------------|
| `satellite-service` | 9190 | `/api/v1/satellite-legacy` | `vegetation-analysis-service` | Port 8090 |
| `weather-advanced` | 9092 | `/api/v1/weather-advanced` | `weather-service` | Port 8092 |
| `crop-health-ai` | 9095 | `/api/v1/crop-health-ai` | `crop-intelligence-service` | Port 8095 |
| `fertilizer-advisor` | 9093 | `/api/v1/fertilizer-advisor` | `advisory-service` | Port 8093 |
| `yield-prediction` (Node.js) | 3021 | `/yield-legacy` | `yield-prediction-service` | Port 8098 |
| `lai-estimation` | 3022 | `/lai-legacy` | `vegetation-analysis-service` | Port 8090 |
| `crop-growth-model` | 3023 | `/crop-growth-legacy` | `irrigation-smart` | Port 8094 |
| `ndvi-engine` | 8107 | `/ndvi-engine-legacy` | `ndvi-processor` | Port 8118 |
| `field-ops` | 8080 | `/field-ops-legacy` | `field-management-service` | Port 3000 |
| `field-service` | 8115 | `/field-service-legacy` | `field-management-service` | Port 3000 |
| `crop-health` | 8100 | `/api/v1/crop-health-basic` | `crop-intelligence-service` | Port 8095 |

---

## ملخص الإحصائيات | Statistics Summary

### إجمالي الخدمات | Total Services

| الفئة | Category | العدد | Count |
|-------|----------|-------|-------|
| خدمات Node.js | Node.js Services | 11 | Active |
| خدمات Python | Python Services | 35 | Active |
| خدمات جديدة | New Services (2026-01-23) | 16 | Active |
| خدمات مهملة | Deprecated Services | 11 | Legacy |
| **الإجمالي** | **Total Kong Services** | **62** | |

### نقاط النهاية | Endpoints

| الفئة | Category | العدد |
|-------|----------|-------|
| REST Endpoints | نقاط REST | 350+ |
| WebSocket Events | أحداث WebSocket | 50+ |
| Health Endpoints | فحص الصحة | 124 (2 per service) |
| **الإجمالي** | **Total** | **500+** |

### التقنيات المستخدمة | Technologies

| التقنية | Technology | الاستخدام |
|---------|------------|-----------|
| FastAPI | Python | 46 خدمة |
| NestJS | Node.js | 8 خدمات |
| Express | Node.js | 3 خدمات |
| Socket.io | WebSocket | 4 خدمات |
| Pydantic v2 | Validation | Python |
| TypeScript | Types | Node.js |

### المصادقة والأمان | Authentication & Security

| العنصر | Element | الوصف |
|--------|---------|-------|
| JWT | التوكن | Bearer Token |
| Rate Limiting | تحديد المعدل | 30-120 req/min |
| CORS | المصادر المتقاطعة | مُفعّل |
| Request ID | معرف الطلب | X-Correlation-Id |
| Tenant Isolation | عزل المستأجرين | X-Tenant-Id |

---

## المراجع | References

- [Kong Configuration](../infrastructure/gateway/kong/kong.yml)
- [CLAUDE.md](../CLAUDE.md) - Project Guidelines
- [API Gateway Documentation](./API_GATEWAY.md)
- [Services Registry](../governance/services.yaml)

---

> **آخر تحديث**: 2026-01-24
> **الإصدار**: 16.0.0
> **المسؤول**: KAFAAT Development Team
