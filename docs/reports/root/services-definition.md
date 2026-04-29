# Kong Services Definition | تعريف خدمات Kong

> تحليل شامل لجميع الخدمات المعرفة في بوابة Kong API Gateway
>
> **المصدر**: `infrastructure/gateway/kong/kong.yml`
> **تاريخ التحديث**: 2026-01-24
> **إجمالي الخدمات**: 62 خدمة

---

## جدول المحتويات

1. [نظرة عامة](#نظرة-عامة)
2. [الإضافات العالمية](#الإضافات-العالمية-global-plugins)
3. [خدمات Node.js](#خدمات-nodejs)
4. [خدمات Python](#خدمات-python)
5. [الخدمات المضافة حديثاً](#الخدمات-المضافة-حديثاً)
6. [الخدمات المهملة](#الخدمات-المهملة-deprecated)
7. [نقاط النهاية للمنصة](#نقاط-النهاية-للمنصة)
8. [الخدمات غير المضمنة في Kong](#الخدمات-غير-المضمنة-في-kong)

---

## نظرة عامة

| البند | القيمة |
|-------|--------|
| **إصدار التكوين** | 3.0 |
| **وضع قاعدة البيانات** | DB-less (تكوين تصريحي) |
| **إجمالي الخدمات** | 62 خدمة |
| **خدمات Node.js** | 12 خدمة |
| **خدمات Python** | 46 خدمة |
| **خدمات مهملة** | 8 خدمات |

---

## الإضافات العالمية (Global Plugins)

الإضافات التالية مُطبقة على جميع المسارات والخدمات:

### 1. CORS (مشاركة الموارد عبر المصادر)

| المتغير | النوع | القيمة | الوصف |
|---------|-------|--------|-------|
| `origins` | `string[]` | `["*"]` | المصادر المسموح بها (في الإنتاج: نطاقات محددة) |
| `methods` | `string[]` | `["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]` | طرق HTTP المسموحة |
| `headers` | `string[]` | Accept, Authorization, Content-Type, X-Request-Id, X-Correlation-Id | رؤوس الطلب المسموحة |
| `exposed_headers` | `string[]` | X-Request-Id, X-Correlation-Id, X-RateLimit-* | الرؤوس المكشوفة للعميل |
| `credentials` | `boolean` | `false` | دعم بيانات الاعتماد |
| `max_age` | `integer` | `3600` | مدة تخزين preflight بالثواني |

### 2. Prometheus (المراقبة)

| المتغير | النوع | القيمة | الوصف |
|---------|-------|--------|-------|
| `config` | `object` | `{}` | التكوين الافتراضي للمقاييس |

### 3. Correlation-ID (التتبع الموزع)

| المتغير | النوع | القيمة | الوصف |
|---------|-------|--------|-------|
| `header_name` | `string` | `X-Correlation-Id` | اسم رأس معرف الارتباط |
| `generator` | `string` | `uuid#counter` | طريقة توليد المعرف |
| `echo_downstream` | `boolean` | `true` | إرسال المعرف في الاستجابة |

### 4. Request-Size-Limiting (تحديد حجم الطلب)

| المتغير | النوع | القيمة | الوصف |
|---------|-------|--------|-------|
| `allowed_payload_size` | `integer` | `10` | الحد الأقصى للحجم |
| `size_unit` | `string` | `megabytes` | وحدة القياس |
| `require_content_length` | `boolean` | `false` | طلب رأس Content-Length |

---

## خدمات Node.js

### 1. field-management-service (إدارة الحقول)

| البند | القيمة |
|-------|--------|
| **المضيف** | `field-management-service` |
| **المنفذ** | `3000` |
| **البروتوكول** | `http` |
| **المسارات** | `/api/v1/fields`, `/api/v1/field`, `/field` |
| **strip_path** | `true` |

#### المتغيرات المدخلة (Input)

| النقطة | الطريقة | المتغيرات | النوع |
|--------|---------|-----------|-------|
| `/fields` | `POST` | `name`, `tenantId`, `cropType`, `areaHectares`, `boundary` | `CreateFieldDto` |
| `/fields` | `GET` | `tenantId`, `status`, `page`, `limit` | `QueryParams` |
| `/fields/:id` | `PUT` | `name`, `cropType`, `status`, `irrigationType` | `UpdateFieldDto` |
| `/fields/:id/boundary` | `PUT` | `boundary` (GeoJSON), `changeReason` | `UpdateBoundaryDto` |
| `/fields/:id/ndvi` | `POST` | `value` (-1 to 1), `source`, `cloudCover` | `NdviReadingDto` |

#### المتغيرات المخرجة (Output)

| النقطة | المتغيرات | النوع |
|--------|-----------|-------|
| `/fields` | `id`, `name`, `tenantId`, `cropType`, `areaHectares`, `boundary`, `healthScore`, `ndviValue`, `status`, `irrigationType`, `createdAt`, `updatedAt` | `Field` |
| `/fields/:id/history` | `previousBoundary`, `newBoundary`, `areaChangeHectares`, `changedBy`, `changeReason` | `FieldBoundaryHistory[]` |

```typescript
// Enums
FieldStatus: "active" | "fallow" | "harvested" | "preparing" | "inactive"
IrrigationType: "drip" | "sprinkler" | "flood" | "pivot" | "none"
CropType: "wheat" | "barley" | "date_palm" | "tomato" | "cucumber" | ...
```

---

### 2. user-service-public (المصادقة العامة)

| البند | القيمة |
|-------|--------|
| **المضيف** | `user-service` |
| **المنفذ** | `3025` |
| **البروتوكول** | `http` |
| **المسارات** | `/api/v1/auth/login`, `/api/v1/auth/register`, `/api/v1/auth/forgot-password`, `/api/v1/auth/reset-password`, `/api/v1/auth/send-otp`, `/api/v1/auth/verify-otp`, `/api/v1/auth/refresh` |
| **Rate Limiting** | 30/دقيقة، 500/ساعة |

#### المتغيرات المدخلة (Input)

| النقطة | الطريقة | المتغيرات | النوع |
|--------|---------|-----------|-------|
| `/auth/login` | `POST` | `email`, `password` | `LoginDto` |
| `/auth/register` | `POST` | `tenantId`, `email`, `phone`, `password`, `firstName`, `lastName`, `role` | `CreateUserDto` |
| `/auth/forgot-password` | `POST` | `email` | `ForgotPasswordDto` |
| `/auth/reset-password` | `POST` | `token`, `newPassword` | `ResetPasswordDto` |
| `/auth/send-otp` | `POST` | `phone` or `email` | `SendOtpDto` |
| `/auth/verify-otp` | `POST` | `phone` or `email`, `otp` | `VerifyOtpDto` |
| `/auth/refresh` | `POST` | `refreshToken` | `RefreshTokenDto` |

#### المتغيرات المخرجة (Output)

| النقطة | المتغيرات | النوع |
|--------|-----------|-------|
| `/auth/login` | `accessToken`, `refreshToken`, `expiresIn`, `user` | `AuthResponse` |
| `/auth/register` | `id`, `email`, `status`, `message` | `RegisterResponse` |

```typescript
// Types
UserRole: "ADMIN" | "MANAGER" | "FARMER" | "WORKER" | "VIEWER"
UserStatus: "ACTIVE" | "INACTIVE" | "SUSPENDED" | "PENDING"
```

---

### 3. user-service (المستخدمين المحمية)

| البند | القيمة |
|-------|--------|
| **المضيف** | `user-service` |
| **المنفذ** | `3025` |
| **البروتوكول** | `http` |
| **المسارات** | `/api/v1/auth/logout`, `/api/v1/auth/logout-all`, `/api/v1/auth/me`, `/api/v1/users` |
| **Rate Limiting** | 100/دقيقة، 2000/ساعة |

#### المتغيرات المدخلة (Input)

| النقطة | الطريقة | المتغيرات | النوع |
|--------|---------|-----------|-------|
| `/auth/me` | `GET` | `Authorization: Bearer <token>` | Header |
| `/users` | `GET` | `tenantId`, `role`, `status`, `page`, `limit` | `QueryParams` |
| `/users/:id` | `PUT` | `firstName`, `lastName`, `phone`, `role`, `status` | `UpdateUserDto` |

#### المتغيرات المخرجة (Output)

| النقطة | المتغيرات | النوع |
|--------|-----------|-------|
| `/auth/me` | `id`, `tenantId`, `email`, `firstName`, `lastName`, `role`, `status` | `User` |
| `/users` | Array of User objects with pagination | `PaginatedResponse<User>` |

---

### 4. user-service-health (فحص الصحة)

| البند | القيمة |
|-------|--------|
| **المضيف** | `user-service` |
| **المنفذ** | `3025` |
| **المسارات** | `/api/v1/health`, `/api/v1/healthz`, `/api/v1/readyz` |

#### المتغيرات المخرجة (Output)

```json
{
  "status": "ok",
  "service": "user-service",
  "version": "16.0.0",
  "database": true,
  "nats": true,
  "uptime": 12345
}
```

---

### 5. marketplace-service (السوق الزراعي)

| البند | القيمة |
|-------|--------|
| **المضيف** | `marketplace-service` |
| **المنفذ** | `3010` |
| **البروتوكول** | `http` |
| **المسارات** | `/api/v1/marketplace`, `/marketplace` |

#### المتغيرات المدخلة (Input)

| النقطة | الطريقة | المتغيرات | النوع |
|--------|---------|-----------|-------|
| `/products` | `POST` | `name`, `category`, `price`, `unit`, `quantity`, `farmerId` | `CreateProductDto` |
| `/products` | `GET` | `category`, `minPrice`, `maxPrice`, `location` | `QueryParams` |
| `/orders` | `POST` | `productId`, `quantity`, `buyerId`, `deliveryAddress` | `CreateOrderDto` |

#### المتغيرات المخرجة (Output)

| النقطة | المتغيرات | النوع |
|--------|-----------|-------|
| `/products` | `id`, `name`, `category`, `price`, `unit`, `quantity`, `farmerId`, `status` | `Product` |
| `/orders` | `id`, `productId`, `quantity`, `totalPrice`, `status`, `deliveryDate` | `Order` |

---

### 6. research-core (البحث العلمي)

| البند | القيمة |
|-------|--------|
| **المضيف** | `research-core` |
| **المنفذ** | `3015` |
| **البروتوكول** | `http` |
| **المسارات** | `/api/v1/research`, `/research` |

#### المتغيرات المدخلة (Input)

| النقطة | الطريقة | المتغيرات | النوع |
|--------|---------|-----------|-------|
| `/trials` | `POST` | `name`, `cropType`, `startDate`, `endDate`, `treatments[]` | `CreateTrialDto` |
| `/trials/:id/results` | `POST` | `trialId`, `treatmentId`, `measurements[]` | `RecordResultDto` |

#### المتغيرات المخرجة (Output)

| النقطة | المتغيرات | النوع |
|--------|-----------|-------|
| `/trials` | `id`, `name`, `status`, `cropType`, `treatments`, `results` | `Trial` |
| `/trials/:id/analysis` | `statisticalSummary`, `significanceTests`, `recommendations` | `TrialAnalysis` |

---

### 7. disaster-assessment (تقييم الكوارث)

| البند | القيمة |
|-------|--------|
| **المضيف** | `disaster-assessment` |
| **المنفذ** | `3020` |
| **البروتوكول** | `http` |
| **المسارات** | `/api/v1/disaster`, `/disaster` |

#### المتغيرات المدخلة (Input)

| النقطة | الطريقة | المتغيرات | النوع |
|--------|---------|-----------|-------|
| `/assessments` | `POST` | `fieldId`, `disasterType`, `severity`, `affectedArea`, `images[]` | `CreateAssessmentDto` |
| `/risk` | `POST` | `location` (lat/lon), `cropType`, `season` | `RiskAnalysisRequest` |

#### المتغيرات المخرجة (Output)

| النقطة | المتغيرات | النوع |
|--------|-----------|-------|
| `/assessments` | `id`, `fieldId`, `disasterType`, `severity`, `estimatedLoss`, `recommendations` | `Assessment` |
| `/risk` | `riskLevel`, `factors[]`, `mitigationMeasures[]` | `RiskAnalysis` |

```typescript
// Enums
DisasterType: "flood" | "drought" | "frost" | "hail" | "pest" | "disease" | "fire"
Severity: "low" | "medium" | "high" | "critical"
```

---

### 8. chat-service (الدردشة)

| البند | القيمة |
|-------|--------|
| **المضيف** | `chat-service` |
| **المنفذ** | `8000` |
| **البروتوكول** | `http` |
| **المسارات** | `/api/v1/chat`, `/chat` |

#### المتغيرات المدخلة (Input)

| النقطة | الطريقة | المتغيرات | النوع |
|--------|---------|-----------|-------|
| `/messages` | `POST` | `conversationId`, `content`, `senderId`, `type` | `SendMessageDto` |
| `/conversations` | `POST` | `participants[]`, `type`, `metadata` | `CreateConversationDto` |

#### المتغيرات المخرجة (Output)

| النقطة | المتغيرات | النوع |
|--------|-----------|-------|
| `/messages` | `id`, `conversationId`, `content`, `senderId`, `timestamp`, `status` | `Message` |
| `/conversations/:id/messages` | Array of messages with pagination | `PaginatedResponse<Message>` |

---

### 9. iot-service (إنترنت الأشياء)

| البند | القيمة |
|-------|--------|
| **المضيف** | `iot-service` |
| **المنفذ** | `8117` |
| **البروتوكول** | `http` |
| **المسارات** | `/api/v1/iot`, `/iot` |

#### المتغيرات المدخلة (Input)

| النقطة | الطريقة | المتغيرات | النوع |
|--------|---------|-----------|-------|
| `/devices` | `POST` | `name`, `type`, `fieldId`, `serialNumber`, `config` | `RegisterDeviceDto` |
| `/devices/:id/data` | `POST` | `readings[]` (timestamp, value, unit) | `SensorDataDto` |
| `/devices/:id/commands` | `POST` | `command`, `parameters` | `DeviceCommandDto` |

#### المتغيرات المخرجة (Output)

| النقطة | المتغيرات | النوع |
|--------|-----------|-------|
| `/devices` | `id`, `name`, `type`, `status`, `lastSeen`, `batteryLevel` | `Device` |
| `/devices/:id/data` | `deviceId`, `readings[]`, `aggregates` | `SensorDataResponse` |

```typescript
// Enums
DeviceType: "soil_moisture" | "weather_station" | "irrigation_controller" | "camera" | "flow_meter"
DeviceStatus: "online" | "offline" | "error" | "maintenance"
```

---

### 10. community-chat (مجتمع المزارعين)

| البند | القيمة |
|-------|--------|
| **المضيف** | `community-chat` |
| **المنفذ** | `8097` |
| **البروتوكول** | `http` |
| **المسارات** | `/api/v1/community`, `/api/v1/posts`, `/community` |

#### المتغيرات المدخلة (Input)

| النقطة | الطريقة | المتغيرات | النوع |
|--------|---------|-----------|-------|
| `/posts` | `POST` | `title`, `content`, `category`, `tags[]`, `images[]` | `CreatePostDto` |
| `/posts/:id/comments` | `POST` | `content`, `parentId` | `CreateCommentDto` |
| `/posts/:id/reactions` | `POST` | `type` (like, helpful, etc.) | `ReactionDto` |

#### المتغيرات المخرجة (Output)

| النقطة | المتغيرات | النوع |
|--------|-----------|-------|
| `/posts` | `id`, `title`, `content`, `author`, `category`, `likes`, `comments`, `createdAt` | `Post` |
| `/posts/:id/comments` | `id`, `content`, `author`, `replies[]`, `createdAt` | `Comment[]` |

---

## خدمات Python

### 11. ws-gateway (بوابة WebSocket)

| البند | القيمة |
|-------|--------|
| **المضيف** | `ws-gateway` |
| **المنفذ** | `8081` |
| **البروتوكول** | `http` |
| **المسارات** | `/ws` |

#### المتغيرات المدخلة (Input)

| النوع | المتغيرات | الوصف |
|-------|-----------|-------|
| WebSocket | `Authorization` header | رمز JWT للمصادقة |
| WebSocket | `subscribe` message | `{ "channel": "field.updates", "fieldId": "..." }` |

#### المتغيرات المخرجة (Output)

| الحدث | المتغيرات | النوع |
|-------|-----------|-------|
| `field.updated` | `fieldId`, `changes`, `timestamp` | `FieldUpdateEvent` |
| `alert.created` | `alertId`, `type`, `severity`, `message` | `AlertEvent` |
| `sensor.reading` | `deviceId`, `readings[]` | `SensorEvent` |

---

### 12. billing-core (الفوترة)

| البند | القيمة |
|-------|--------|
| **المضيف** | `billing-core` |
| **المنفذ** | `8089` |
| **البروتوكول** | `http` |
| **المسارات** | `/api/v1/billing`, `/billing` |

#### المتغيرات المدخلة (Input)

| النقطة | الطريقة | المتغيرات | النوع |
|--------|---------|-----------|-------|
| `/subscriptions` | `POST` | `tenantId`, `planId`, `paymentMethod`, `autoRenew` | `CreateSubscriptionDto` |
| `/invoices/:id/pay` | `POST` | `paymentMethod`, `transactionId` | `PaymentDto` |
| `/usage` | `POST` | `tenantId`, `feature`, `quantity` | `RecordUsageDto` |

#### المتغيرات المخرجة (Output)

| النقطة | المتغيرات | النوع |
|--------|-----------|-------|
| `/plans` | `planId`, `name`, `nameAr`, `price`, `currency`, `billingCycle`, `features` | `Plan[]` |
| `/subscriptions` | `id`, `tenantId`, `planId`, `status`, `startDate`, `endDate`, `autoRenew` | `Subscription` |
| `/invoices` | `id`, `amount`, `currency`, `status`, `dueDate`, `items[]` | `Invoice` |

```python
# Enums
SubscriptionStatus: "ACTIVE" | "TRIAL" | "PAST_DUE" | "CANCELED" | "SUSPENDED" | "EXPIRED"
InvoiceStatus: "DRAFT" | "PENDING" | "PAID" | "OVERDUE" | "CANCELED" | "REFUNDED"
PaymentMethod: "CREDIT_CARD" | "BANK_TRANSFER" | "MOBILE_MONEY" | "CASH"
PlanTier: "FREE" | "STARTER" | "PROFESSIONAL" | "ENTERPRISE"
BillingCycle: "MONTHLY" | "QUARTERLY" | "YEARLY"
```

---

### 13. vegetation-analysis-service (تحليل الغطاء النباتي)

| البند | القيمة |
|-------|--------|
| **المضيف** | `vegetation-analysis-service` |
| **المنفذ** | `8090` |
| **البروتوكول** | `http` |
| **المسارات** | `/api/v1/vegetation`, `/api/v1/satellite`, `/api/v1/ndvi` |

#### المتغيرات المدخلة (Input)

| النقطة | الطريقة | المتغيرات | النوع |
|--------|---------|-----------|-------|
| `/analyze` | `POST` | `fieldId`, `boundary` (GeoJSON), `startDate`, `endDate` | `AnalysisRequest` |
| `/ndvi` | `POST` | `fieldId`, `date`, `cloudCoverMax` | `NdviRequest` |
| `/timeseries` | `GET` | `fieldId`, `startDate`, `endDate`, `interval` | `QueryParams` |

#### المتغيرات المخرجة (Output)

| النقطة | المتغيرات | النوع |
|--------|-----------|-------|
| `/analyze` | `fieldId`, `ndviMean`, `ndviMin`, `ndviMax`, `healthScore`, `anomalies[]` | `AnalysisResult` |
| `/ndvi` | `value` (-1 to 1), `date`, `source`, `cloudCover`, `quality` | `NdviReading` |
| `/timeseries` | `readings[]` with date and value | `TimeseriesData` |

---

### 14. indicators-service (المؤشرات الزراعية)

| البند | القيمة |
|-------|--------|
| **المضيف** | `indicators-service` |
| **المنفذ** | `8091` |
| **البروتوكول** | `http` |
| **المسارات** | `/api/v1/indicators`, `/indicators` |

#### المتغيرات المدخلة (Input)

| النقطة | الطريقة | المتغيرات | النوع |
|--------|---------|-----------|-------|
| `/compute` | `POST` | `fieldId`, `indicators[]`, `dateRange` | `ComputeRequest` |
| `/lai` | `POST` | `fieldId`, `ndvi`, `cropType`, `growthStage` | `LaiRequest` |

#### المتغيرات المخرجة (Output)

| النقطة | المتغيرات | النوع |
|--------|-----------|-------|
| `/compute` | `fieldId`, `indicators` (NDVI, LAI, NDWI, EVI), `computedAt` | `IndicatorsResult` |
| `/lai` | `value`, `confidence`, `method` | `LaiResult` |

```python
# Indicator Types
IndicatorType: "NDVI" | "LAI" | "NDWI" | "EVI" | "SAVI" | "GNDVI"
```

---

### 15. weather-service (الطقس)

| البند | القيمة |
|-------|--------|
| **المضيف** | `weather-service` |
| **المنفذ** | `8092` |
| **البروتوكول** | `http` |
| **المسارات** | `/api/v1/weather`, `/weather` |

#### المتغيرات المدخلة (Input)

| النقطة | الطريقة | المتغيرات | النوع |
|--------|---------|-----------|-------|
| `/assess` | `POST` | `tenantId`, `fieldId`, `tempC`, `humidityPct`, `windSpeedKmh`, `precipitationMm`, `uvIndex` | `WeatherAssessRequest` |
| `/current` | `POST` | `tenantId`, `fieldId`, `lat` (-90 to 90), `lon` (-180 to 180) | `LocationRequest` |
| `/forecast` | `POST` | `tenantId`, `fieldId`, `lat`, `lon`, `days` (1-16) | `ForecastRequest` |
| `/evapotranspiration` | `POST` | `tenantId`, `fieldId`, `tempC`, `humidityPct`, `windSpeedKmh`, `solarRadiationMj` | `ETRequest` |
| `/gdd` | `POST` | `tenantId`, `fieldId`, `tempMaxC`, `tempMinC`, `baseTempC`, `upperTempC` | `GDDRequest` |
| `/spray-window` | `POST` | `tenantId`, `fieldId`, `tempC`, `humidityPct`, `windSpeedKmh`, `precipitationProbability` | `SprayWindowRequest` |
| `/frost-risk` | `POST` | `tenantId`, `fieldId`, `tempC`, `humidityPct`, `windSpeedKmh`, `cloudCoverPct`, `dewPointC` | `FrostRiskRequest` |
| `/heat-stress` | `POST` | `tenantId`, `fieldId`, `tempC`, `humidityPct`, `solarRadiationMj`, `windSpeedKmh` | `HeatStressRequest` |

#### المتغيرات المخرجة (Output)

| النقطة | المتغيرات | النوع |
|--------|-----------|-------|
| `/current` | `temperatureC`, `humidityPct`, `windSpeedKmh`, `precipitationMm`, `uvIndex`, `timestamp` | `CurrentWeather` |
| `/forecast` | `daily[]` with date, tempMin, tempMax, precipitation, condition | `ForecastResponse` |
| `/evapotranspiration` | `et0Mm`, `method` ("FAO-56 Penman-Monteith") | `ETResult` |
| `/gdd` | `gddValue`, `accumulatedGdd` | `GDDResult` |
| `/spray-window` | `suitable` (boolean), `factors[]`, `optimalWindow` | `SprayWindowResult` |
| `/frost-risk` | `riskLevel`, `probability`, `recommendedActions[]` | `FrostRiskResult` |

---

### 16. advisory-service (الاستشارات الزراعية)

| البند | القيمة |
|-------|--------|
| **المضيف** | `advisory-service` |
| **المنفذ** | `8093` |
| **البروتوكول** | `http` |
| **المسارات** | `/api/v1/advisory`, `/api/v1/fertilizer`, `/advisory` |

#### المتغيرات المدخلة (Input)

| النقطة | الطريقة | المتغيرات | النوع |
|--------|---------|-----------|-------|
| `/disease/assess` | `POST` | `tenantId`, `fieldId`, `conditionId`, `confidence` (0-1), `crop`, `weather` | `DiseaseAssessRequest` |
| `/disease/symptoms` | `POST` | `tenantId`, `fieldId`, `crop`, `symptoms[]`, `lang` | `SymptomAssessRequest` |
| `/nutrient/ndvi` | `POST` | `tenantId`, `fieldId`, `ndvi` (-1 to 1), `ndviHistory`, `crop`, `stage` | `NDVIAssessRequest` |
| `/nutrient/visual` | `POST` | `tenantId`, `fieldId`, `leafColor`, `pattern`, `location`, `crop` | `VisualAssessRequest` |
| `/fertilizer/plan` | `POST` | `tenantId`, `fieldId`, `crop`, `stage`, `fieldSizeHa`, `soilFertility`, `irrigationType` | `FertilizerPlanRequest` |

#### المتغيرات المخرجة (Output)

| النقطة | المتغيرات | النوع |
|--------|-----------|-------|
| `/disease/assess` | `category`, `severity`, `titleAr`, `titleEn`, `confidence`, `actions[]`, `details` | `DiseaseAssessment` |
| `/disease/symptoms` | `possibleDiseases[]` with name, probability, treatments | `SymptomAnalysis` |
| `/nutrient/ndvi` | `deficiency`, `severity`, `recommendations[]` | `NutrientAssessment` |
| `/fertilizer/plan` | `applications[]` with product, rate, timing, method | `FertilizerPlan` |
| `/crops` | `code`, `nameAr`, `nameEn`, `category`, `seasons`, `stages[]` | `Crop[]` |

```python
# Enums
Severity: "none" | "low" | "medium" | "high" | "critical"
GrowthStage: "germination" | "seedling" | "tillering" | "heading" | "flowering" | "ripening"
```

---

### 17. irrigation-smart (الري الذكي)

| البند | القيمة |
|-------|--------|
| **المضيف** | `irrigation-smart` |
| **المنفذ** | `8094` |
| **البروتوكول** | `http` |
| **المسارات** | `/api/v1/irrigation`, `/irrigation` |

#### المتغيرات المدخلة (Input)

| النقطة | الطريقة | المتغيرات | النوع |
|--------|---------|-----------|-------|
| `/schedule` | `POST` | `fieldId`, `cropType`, `soilType`, `irrigationType`, `waterSource` | `ScheduleRequest` |
| `/recommend` | `POST` | `fieldId`, `soilMoisture`, `et0`, `cropKc`, `rainfallMm` | `RecommendRequest` |
| `/zones` | `POST` | `fieldId`, `zones[]` with area, soilType, cropType | `ZoneConfigRequest` |

#### المتغيرات المخرجة (Output)

| النقطة | المتغيرات | النوع |
|--------|-----------|-------|
| `/schedule` | `schedules[]` with date, duration, volume, zone | `IrrigationSchedule` |
| `/recommend` | `waterNeededMm`, `irrigationDuration`, `nextIrrigationDate`, `efficiency` | `IrrigationRecommendation` |
| `/status/:fieldId` | `currentMoisture`, `lastIrrigation`, `nextScheduled`, `waterUsage` | `IrrigationStatus` |

---

### 18. crop-intelligence-service (ذكاء المحاصيل)

| البند | القيمة |
|-------|--------|
| **المضيف** | `crop-intelligence-service` |
| **المنفذ** | `8095` |
| **البروتوكول** | `http` |
| **المسارات** | `/api/v1/crop-health`, `/api/v1/crop`, `/crop` |

#### المتغيرات المدخلة (Input)

| النقطة | الطريقة | المتغيرات | النوع |
|--------|---------|-----------|-------|
| `/analyze` | `POST` | `fieldId`, `image` (base64), `cropType` | `ImageAnalysisRequest` |
| `/diagnose` | `POST` | `fieldId`, `symptoms[]`, `cropType`, `growthStage` | `DiagnoseRequest` |
| `/predict` | `POST` | `fieldId`, `cropType`, `plantingDate`, `currentStage` | `PredictionRequest` |

#### المتغيرات المخرجة (Output)

| النقطة | المتغيرات | النوع |
|--------|-----------|-------|
| `/analyze` | `healthScore`, `issues[]`, `recommendations[]`, `confidence` | `HealthAnalysis` |
| `/diagnose` | `diagnosis`, `probability`, `treatments[]`, `preventiveMeasures[]` | `DiagnosisResult` |
| `/predict` | `expectedYield`, `harvestDate`, `riskFactors[]` | `YieldPrediction` |

---

### 19. virtual-sensors (المستشعرات الافتراضية)

| البند | القيمة |
|-------|--------|
| **المضيف** | `virtual-sensors` |
| **المنفذ** | `8119` |
| **البروتوكول** | `http` |
| **المسارات** | `/api/v1/virtual-sensors`, `/virtual-sensors` |

#### المتغيرات المدخلة (Input)

| النقطة | الطريقة | المتغيرات | النوع |
|--------|---------|-----------|-------|
| `/compute` | `POST` | `fieldId`, `sensorType`, `inputs` (weather, satellite, etc.) | `ComputeRequest` |
| `/calibrate` | `POST` | `sensorId`, `groundTruthValues[]` | `CalibrationRequest` |

#### المتغيرات المخرجة (Output)

| النقطة | المتغيرات | النوع |
|--------|-----------|-------|
| `/compute` | `sensorType`, `value`, `unit`, `confidence`, `methodology` | `VirtualReading` |
| `/:fieldId/readings` | `readings[]` with type, value, timestamp | `SensorReadings` |

```python
# Virtual Sensor Types
VirtualSensorType: "soil_moisture" | "evapotranspiration" | "crop_water_stress" | "nitrogen_status"
```

---

### 20. yield-prediction-service (التنبؤ بالمحصول)

| البند | القيمة |
|-------|--------|
| **المضيف** | `yield-prediction-service` |
| **المنفذ** | `8098` |
| **البروتوكول** | `http` |
| **المسارات** | `/api/v1/yield`, `/yield` |

#### المتغيرات المدخلة (Input)

| النقطة | الطريقة | المتغيرات | النوع |
|--------|---------|-----------|-------|
| `/predict` | `POST` | `fieldId`, `cropType`, `plantingDate`, `areaHa`, `ndviHistory[]`, `weatherData` | `PredictionRequest` |
| `/compare` | `POST` | `fieldId`, `actualYield`, `predictedYield` | `CompareRequest` |

#### المتغيرات المخرجة (Output)

| النقطة | المتغيرات | النوع |
|--------|-----------|-------|
| `/predict` | `expectedYield`, `yieldRange` (min, max), `confidence`, `factors[]` | `YieldPrediction` |
| `/history/:fieldId` | `predictions[]`, `actuals[]`, `accuracy` | `PredictionHistory` |

---

### 21. field-chat (دردشة الحقل)

| البند | القيمة |
|-------|--------|
| **المضيف** | `field-chat` |
| **المنفذ** | `8099` |
| **البروتوكول** | `http` |
| **المسارات** | `/api/v1/field-chat`, `/field-chat` |

#### المتغيرات المدخلة (Input)

| النقطة | الطريقة | المتغيرات | النوع |
|--------|---------|-----------|-------|
| `/ask` | `POST` | `fieldId`, `question`, `context`, `language` | `QuestionRequest` |
| `/history` | `GET` | `fieldId`, `limit` | `QueryParams` |

#### المتغيرات المخرجة (Output)

| النقطة | المتغيرات | النوع |
|--------|-----------|-------|
| `/ask` | `answer`, `answerAr`, `sources[]`, `confidence`, `suggestions[]` | `ChatResponse` |

---

### 22. equipment-service (المعدات)

| البند | القيمة |
|-------|--------|
| **المضيف** | `equipment-service` |
| **المنفذ** | `8101` |
| **البروتوكول** | `http` |
| **المسارات** | `/api/v1/equipment`, `/equipment` |

#### المتغيرات المدخلة (Input)

| النقطة | الطريقة | المتغيرات | النوع |
|--------|---------|-----------|-------|
| `/` | `POST` | `name`, `type`, `model`, `purchaseDate`, `condition` | `CreateEquipmentDto` |
| `/:id/maintenance` | `POST` | `type`, `description`, `cost`, `performedBy` | `MaintenanceRecordDto` |
| `/:id/assign` | `POST` | `fieldId`, `taskId`, `startDate`, `endDate` | `AssignmentDto` |

#### المتغيرات المخرجة (Output)

| النقطة | المتغيرات | النوع |
|--------|-----------|-------|
| `/` | `id`, `name`, `type`, `model`, `condition`, `lastMaintenance`, `nextMaintenance` | `Equipment` |
| `/:id/history` | `maintenanceRecords[]`, `assignments[]`, `usageHours` | `EquipmentHistory` |

```python
# Enums
EquipmentType: "tractor" | "harvester" | "sprayer" | "irrigation_pump" | "seeder" | "plow"
Condition: "excellent" | "good" | "fair" | "poor" | "needs_repair"
```

---

### 23. task-service (المهام)

| البند | القيمة |
|-------|--------|
| **المضيف** | `task-service` |
| **المنفذ** | `8103` |
| **البروتوكول** | `http` |
| **المسارات** | `/api/v1/tasks`, `/api/v1/task`, `/task` |

#### المتغيرات المدخلة (Input)

| النقطة | الطريقة | المتغيرات | النوع |
|--------|---------|-----------|-------|
| `/` | `POST` | `title`, `description`, `taskType`, `priority`, `dueDate`, `assignedTo`, `fieldId` | `CreateTaskDto` |
| `/:id/status` | `PATCH` | `status`, `completionNotes`, `evidence` | `UpdateStatusDto` |
| `/:id/assign` | `PATCH` | `assignedTo` | `AssignDto` |

#### المتغيرات المخرجة (Output)

| النقطة | المتغيرات | النوع |
|--------|-----------|-------|
| `/` | `id`, `title`, `taskType`, `priority`, `status`, `dueDate`, `assignedTo`, `field` | `Task` |
| `/overdue` | Tasks where dueDate < now and status != completed | `Task[]` |

```python
# Enums
TaskType: "irrigation" | "fertilization" | "spraying" | "scouting" | "maintenance" | "harvest" | "planting"
Priority: "low" | "medium" | "high" | "urgent"
TaskStatus: "pending" | "in_progress" | "completed" | "cancelled" | "overdue"
```

---

### 24. provider-config (تكوين المزودين)

| البند | القيمة |
|-------|--------|
| **المضيف** | `provider-config` |
| **المنفذ** | `8104` |
| **البروتوكول** | `http` |
| **المسارات** | `/api/v1/provider-config`, `/provider-config` |

#### المتغيرات المدخلة (Input)

| النقطة | الطريقة | المتغيرات | النوع |
|--------|---------|-----------|-------|
| `/` | `POST` | `providerType`, `name`, `config`, `priority`, `enabled` | `CreateProviderDto` |
| `/:id` | `PUT` | `config`, `priority`, `enabled` | `UpdateProviderDto` |

#### المتغيرات المخرجة (Output)

| النقطة | المتغيرات | النوع |
|--------|-----------|-------|
| `/` | `id`, `providerType`, `name`, `config`, `priority`, `enabled`, `healthStatus` | `Provider` |
| `/types` | Available provider types | `string[]` |

---

### 25. agro-advisor (المستشار الزراعي)

| البند | القيمة |
|-------|--------|
| **المضيف** | `agro-advisor` |
| **المنفذ** | `8105` |
| **البروتوكول** | `http` |
| **المسارات** | `/api/v1/agro-advisor`, `/api/v1/agro-rules`, `/agro-advisor` |

#### المتغيرات المدخلة (Input)

| النقطة | الطريقة | المتغيرات | النوع |
|--------|---------|-----------|-------|
| `/advise` | `POST` | `fieldId`, `cropType`, `currentStage`, `issues[]`, `context` | `AdviceRequest` |
| `/rules/evaluate` | `POST` | `conditions`, `cropType`, `region` | `RuleEvaluationRequest` |

#### المتغيرات المخرجة (Output)

| النقطة | المتغيرات | النوع |
|--------|-----------|-------|
| `/advise` | `recommendations[]`, `priority`, `timing`, `expectedOutcome` | `AgronomicAdvice` |
| `/rules` | `ruleId`, `condition`, `action`, `priority`, `applicableCrops[]` | `AgroRule[]` |

---

### 26. iot-gateway (بوابة IoT)

| البند | القيمة |
|-------|--------|
| **المضيف** | `iot-gateway` |
| **المنفذ** | `8106` |
| **البروتوكول** | `http` |
| **المسارات** | `/api/v1/iot-gateway`, `/iot-gateway` |

#### المتغيرات المدخلة (Input)

| النقطة | الطريقة | المتغيرات | النوع |
|--------|---------|-----------|-------|
| `/ingest` | `POST` | `deviceId`, `protocol`, `payload` | `IngestRequest` |
| `/protocols` | `GET` | - | - |

#### المتغيرات المخرجة (Output)

| النقطة | المتغيرات | النوع |
|--------|-----------|-------|
| `/ingest` | `accepted`, `deviceId`, `messageId` | `IngestResponse` |
| `/protocols` | `mqtt`, `http`, `coap`, `lorawan` | `string[]` |

---

### 27. weather-core (الطقس المتقدم)

| البند | القيمة |
|-------|--------|
| **المضيف** | `weather-core` |
| **المنفذ** | `8108` |
| **البروتوكول** | `http` |
| **المسارات** | `/api/v1/weather-core`, `/weather-core` |

#### المتغيرات المدخلة (Input)

| النقطة | الطريقة | المتغيرات | النوع |
|--------|---------|-----------|-------|
| `/comprehensive-stress-report` | `POST` | `tenantId`, `fieldId`, `lat`, `lon`, `cropType` | `StressReportRequest` |
| `/agricultural-report` | `POST` | `tenantId`, `fieldId`, `lat`, `lon` | `AgReportRequest` |

#### المتغيرات المخرجة (Output)

| النقطة | المتغيرات | النوع |
|--------|-----------|-------|
| `/comprehensive-stress-report` | `heatStress`, `frostRisk`, `droughtIndex`, `overallRisk`, `recommendations[]` | `StressReport` |
| `/agricultural-report` | `current`, `forecast`, `agriculturalAlerts[]`, `sprayWindows[]` | `AgReport` |

---

### 28. notification-service (الإشعارات)

| البند | القيمة |
|-------|--------|
| **المضيف** | `notification-service` |
| **المنفذ** | `8110` |
| **البروتوكول** | `http` |
| **المسارات** | `/api/v1/notifications`, `/api/v1/channels`, `/api/v1/preferences`, `/api/v1/alerts`, `/api/v1/reminders`, `/api/v1/farmers` |

#### المتغيرات المدخلة (Input)

| النقطة | الطريقة | المتغيرات | النوع |
|--------|---------|-----------|-------|
| `/` | `POST` | `type`, `priority`, `title`, `titleAr`, `body`, `bodyAr`, `targetFarmers[]`, `targetGovernorates[]`, `targetCrops[]`, `channels[]`, `expiresInHours` | `CreateNotificationRequest` |
| `/weather` | `POST` | `governorates[]`, `alertType`, `severity`, `expectedDate`, `details` | `WeatherAlertRequest` |
| `/pest` | `POST` | `governorate`, `pestName`, `pestNameAr`, `affectedCrops[]`, `severity` | `PestAlertRequest` |
| `/irrigation` | `POST` | `farmerId`, `fieldId`, `fieldName`, `crop`, `waterNeededMm`, `urgency` | `IrrigationReminderRequest` |
| `/register` | `POST` | `farmerId`, `name`, `nameAr`, `governorate`, `crops[]`, `phone`, `email`, `fcmToken`, `language` | `FarmerProfile` |

#### المتغيرات المخرجة (Output)

| النقطة | المتغيرات | النوع |
|--------|-----------|-------|
| `/farmer/:farmerId` | `notifications[]` with id, title, body, type, priority, status, sentAt, readAt | `Notification[]` |
| `/stats` | `total`, `sent`, `read`, `byType`, `byChannel` | `NotificationStats` |

```python
# Enums
NotificationType: "WEATHER_ALERT" | "PEST_OUTBREAK" | "IRRIGATION_REMINDER" | "DISEASE_DETECTED" | "HARVEST_REMINDER" | "MARKET_PRICE" | "SYSTEM"
NotificationPriority: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL"
NotificationChannel: "PUSH" | "SMS" | "EMAIL" | "WHATSAPP" | "IN_APP"
Governorate: "sanaa" | "aden" | "taiz" | "hodeidah" | "ibb" | ...
```

---

### 29. astronomical-calendar (التقويم الفلكي)

| البند | القيمة |
|-------|--------|
| **المضيف** | `astronomical-calendar` |
| **المنفذ** | `8111` |
| **البروتوكول** | `http` |
| **المسارات** | `/api/v1/astronomy`, `/astronomy` |

#### المتغيرات المدخلة (Input)

| النقطة | الطريقة | المتغيرات | النوع |
|--------|---------|-----------|-------|
| `/prayer-times` | `GET` | `lat`, `lon`, `date`, `method` | `QueryParams` |
| `/moon-phase` | `GET` | `date` | `QueryParams` |
| `/seasons` | `GET` | `year`, `hemisphere` | `QueryParams` |

#### المتغيرات المخرجة (Output)

| النقطة | المتغيرات | النوع |
|--------|-----------|-------|
| `/prayer-times` | `fajr`, `sunrise`, `dhuhr`, `asr`, `maghrib`, `isha` | `PrayerTimes` |
| `/moon-phase` | `phase`, `illumination`, `age`, `nextFullMoon` | `MoonPhase` |
| `/hijri-date` | `day`, `month`, `year`, `monthName`, `monthNameAr` | `HijriDate` |

---

### 30. ai-advisor (المستشار الذكي)

| البند | القيمة |
|-------|--------|
| **المضيف** | `ai-advisor` |
| **المنفذ** | `8112` |
| **البروتوكول** | `http` |
| **المسارات** | `/api/v1/ai-advisor`, `/ai-advisor` |

#### المتغيرات المدخلة (Input)

| النقطة | الطريقة | المتغيرات | النوع |
|--------|---------|-----------|-------|
| `/chat` | `POST` | `message`, `context`, `fieldId`, `language` | `ChatRequest` |
| `/analyze-image` | `POST` | `image` (base64), `cropType`, `question` | `ImageAnalysisRequest` |

#### المتغيرات المخرجة (Output)

| النقطة | المتغيرات | النوع |
|--------|-----------|-------|
| `/chat` | `response`, `responseAr`, `suggestions[]`, `references[]` | `AiResponse` |
| `/analyze-image` | `diagnosis`, `confidence`, `recommendations[]` | `ImageAnalysisResult` |

---

### 31. alert-service (التنبيهات)

| البند | القيمة |
|-------|--------|
| **المضيف** | `alert-service` |
| **المنفذ** | `8113` |
| **البروتوكول** | `http` |
| **المسارات** | `/api/v1/alerts`, `/alerts` |

#### المتغيرات المدخلة (Input)

| النقطة | الطريقة | المتغيرات | النوع |
|--------|---------|-----------|-------|
| `/` | `POST` | `type`, `severity`, `title`, `message`, `fieldId`, `metadata` | `CreateAlertDto` |
| `/:id/acknowledge` | `PATCH` | `acknowledgedBy`, `notes` | `AcknowledgeDto` |
| `/:id/resolve` | `PATCH` | `resolution`, `resolvedBy` | `ResolveDto` |

#### المتغيرات المخرجة (Output)

| النقطة | المتغيرات | النوع |
|--------|-----------|-------|
| `/` | `id`, `type`, `severity`, `title`, `message`, `status`, `createdAt`, `acknowledgedAt`, `resolvedAt` | `Alert` |
| `/active` | Active alerts filtered by status | `Alert[]` |

```python
# Enums
AlertType: "weather" | "pest" | "disease" | "irrigation" | "equipment" | "system"
AlertSeverity: "info" | "warning" | "critical" | "emergency"
AlertStatus: "active" | "acknowledged" | "resolved" | "expired"
```

---

### 32. inventory-service (المخزون)

| البند | القيمة |
|-------|--------|
| **المضيف** | `inventory-service` |
| **المنفذ** | `8116` |
| **البروتوكول** | `http` |
| **المسارات** | `/api/v1/inventory`, `/inventory` |

#### المتغيرات المدخلة (Input)

| النقطة | الطريقة | المتغيرات | النوع |
|--------|---------|-----------|-------|
| `/items` | `POST` | `name`, `category`, `quantity`, `unit`, `minStock`, `location` | `CreateItemDto` |
| `/items/:id/adjust` | `POST` | `adjustment`, `reason`, `reference` | `AdjustmentDto` |
| `/transactions` | `POST` | `itemId`, `type`, `quantity`, `reference` | `TransactionDto` |

#### المتغيرات المخرجة (Output)

| النقطة | المتغيرات | النوع |
|--------|-----------|-------|
| `/items` | `id`, `name`, `category`, `quantity`, `unit`, `minStock`, `status` | `InventoryItem` |
| `/low-stock` | Items where quantity <= minStock | `InventoryItem[]` |
| `/transactions` | `id`, `itemId`, `type`, `quantity`, `balanceBefore`, `balanceAfter`, `createdAt` | `Transaction[]` |

```python
# Enums
ItemCategory: "seeds" | "fertilizer" | "pesticide" | "equipment" | "fuel" | "other"
TransactionType: "in" | "out" | "adjustment" | "transfer"
```

---

### 33. field-intelligence (ذكاء الحقل)

| البند | القيمة |
|-------|--------|
| **المضيف** | `field-intelligence` |
| **المنفذ** | `8120` |
| **البروتوكول** | `http` |
| **المسارات** | `/api/v1/field-intelligence`, `/api/v1/field-core`, `/field-intelligence` |

#### المتغيرات المدخلة (Input)

| النقطة | الطريقة | المتغيرات | النوع |
|--------|---------|-----------|-------|
| `/analyze` | `POST` | `fieldId`, `analysisType[]`, `dateRange` | `AnalysisRequest` |
| `/insights` | `GET` | `fieldId`, `category` | `QueryParams` |

#### المتغيرات المخرجة (Output)

| النقطة | المتغيرات | النوع |
|--------|-----------|-------|
| `/analyze` | `healthScore`, `trends[]`, `anomalies[]`, `recommendations[]` | `FieldAnalysis` |
| `/insights` | `insights[]` with category, title, description, actionItems | `Insight[]` |

---

### 34. mcp-server (Model Context Protocol)

| البند | القيمة |
|-------|--------|
| **المضيف** | `mcp-server` |
| **المنفذ** | `8200` |
| **البروتوكول** | `http` |
| **المسارات** | `/api/v1/mcp`, `/mcp` |

#### المتغيرات المدخلة (Input)

| النقطة | الطريقة | المتغيرات | النوع |
|--------|---------|-----------|-------|
| `/tools` | `GET` | - | - |
| `/execute` | `POST` | `toolName`, `parameters` | `ExecuteRequest` |

#### المتغيرات المخرجة (Output)

| النقطة | المتغيرات | النوع |
|--------|-----------|-------|
| `/tools` | `tools[]` with name, description, parameters | `Tool[]` |
| `/execute` | `result`, `metadata` | `ExecutionResult` |

---

### 35. skills-service (المهارات)

| البند | القيمة |
|-------|--------|
| **المضيف** | `skills-service` |
| **المنفذ** | `8121` |
| **البروتوكول** | `http` |
| **المسارات** | `/api/v1/skills`, `/skills` |

#### المتغيرات المدخلة (Input)

| النقطة | الطريقة | المتغيرات | النوع |
|--------|---------|-----------|-------|
| `/assess` | `POST` | `farmerId`, `skillCategories[]` | `AssessmentRequest` |
| `/training` | `POST` | `farmerId`, `skillId`, `completionStatus` | `TrainingRecordDto` |

#### المتغيرات المخرجة (Output)

| النقطة | المتغيرات | النوع |
|--------|-----------|-------|
| `/assess` | `skillLevels[]`, `gaps[]`, `recommendations[]` | `SkillAssessment` |
| `/farmer/:id` | `skills[]` with name, level, certifications | `FarmerSkills` |

---

### 36. code-review-service (مراجعة الكود)

| البند | القيمة |
|-------|--------|
| **المضيف** | `code-review-service` |
| **المنفذ** | `8102` |
| **البروتوكول** | `http` |
| **المسارات** | `/api/v1/code-review`, `/code-review` |
| **ملاحظة** | يتطلب GPU profile |

#### المتغيرات المدخلة (Input)

| النقطة | الطريقة | المتغيرات | النوع |
|--------|---------|-----------|-------|
| `/review` | `POST` | `code`, `language`, `context` | `ReviewRequest` |
| `/fix` | `POST` | `code`, `issues[]` | `FixRequest` |

#### المتغيرات المخرجة (Output)

| النقطة | المتغيرات | النوع |
|--------|-----------|-------|
| `/review` | `issues[]`, `suggestions[]`, `score` | `ReviewResult` |
| `/fix` | `fixedCode`, `changes[]` | `FixResult` |

---

## الخدمات المضافة حديثاً

> تاريخ الإضافة: 2026-01-23

### 37. audit-service (التدقيق)

| البند | القيمة |
|-------|--------|
| **المضيف** | `audit-service` |
| **المنفذ** | `8114` |
| **المسارات** | `/api/v1/audit`, `/audit` |

#### المتغيرات المدخلة/المخرجة

| النقطة | Input | Output |
|--------|-------|--------|
| `/logs` | `entityType`, `entityId`, `action`, `dateRange` | `AuditLog[]` |
| `/` | `action`, `entityType`, `entityId`, `userId`, `details`, `ipAddress` | `AuditEntry` |

---

### 38. crop-health (صحة المحاصيل الأساسية)

| البند | القيمة |
|-------|--------|
| **المضيف** | `crop-health` |
| **المنفذ** | `8100` |
| **المسارات** | `/api/v1/crop-health-basic`, `/crop-health` |

---

### 39. crm-service (إدارة علاقات المزارعين)

| البند | القيمة |
|-------|--------|
| **المضيف** | `crm-service` |
| **المنفذ** | `8131` |
| **المسارات** | `/api/v1/crm`, `/crm` |

---

### 40. lowcode-engine (منصة التطوير السريع)

| البند | القيمة |
|-------|--------|
| **المضيف** | `lowcode-engine` |
| **المنفذ** | `8132` |
| **المسارات** | `/api/v1/lowcode`, `/lowcode` |

---

### 41. wechat-service (تكامل WeChat)

| البند | القيمة |
|-------|--------|
| **المضيف** | `wechat-service` |
| **المنفذ** | `8133` |
| **المسارات** | `/api/v1/wechat`, `/wechat` |

---

### 42. globalgap-compliance (شهادة GlobalGAP)

| البند | القيمة |
|-------|--------|
| **المضيف** | `globalgap-compliance` |
| **المنفذ** | `8123` |
| **المسارات** | `/api/v1/globalgap`, `/globalgap` |

---

### 43. logistics-service (اللوجستيات)

| البند | القيمة |
|-------|--------|
| **المضيف** | `logistics-service` |
| **المنفذ** | `8162` |
| **المسارات** | `/api/v1/logistics`, `/logistics` |

---

### 44. ussd-gateway (بوابة USSD)

| البند | القيمة |
|-------|--------|
| **المضيف** | `ussd-gateway` |
| **المنفذ** | `8163` |
| **المسارات** | `/api/v1/ussd`, `/ussd` |

---

### 45. agent-registry (سجل الوكلاء)

| البند | القيمة |
|-------|--------|
| **المضيف** | `agent-registry` |
| **المنفذ** | `8160` |
| **المسارات** | `/api/v1/agents`, `/agents` |

---

### 46. ai-agents-core (البنية التحتية للوكلاء)

| البند | القيمة |
|-------|--------|
| **المضيف** | `ai-agents-core` |
| **المنفذ** | `8122` |
| **المسارات** | `/api/v1/ai-agents`, `/ai-agents` |

---

### 47. knowledge-graph (رسم المعرفة)

| البند | القيمة |
|-------|--------|
| **المضيف** | `knowledge-graph` |
| **المنفذ** | `8140` |
| **المسارات** | `/api/v1/knowledge`, `/knowledge` |

---

### 48. yield-engine (محرك المحصول)

| البند | القيمة |
|-------|--------|
| **المضيف** | `yield-engine` |
| **المنفذ** | `8098` |
| **المسارات** | `/api/v1/yield-engine`, `/yield-engine` |

---

### 49. ai-agents-service (تنسيق الوكلاء)

| البند | القيمة |
|-------|--------|
| **المضيف** | `ai-agents-service` |
| **المنفذ** | `8130` |
| **المسارات** | `/api/v1/ai-agents-service`, `/ai-agents-service` |

---

### 50. field-core (خدمة الحقول القديمة)

| البند | القيمة |
|-------|--------|
| **المضيف** | `field-core` |
| **المنفذ** | `3005` |
| **النوع** | NestJS |
| **المسارات** | `/api/v1/field-core`, `/field-core` |

---

## الخدمات المهملة (Deprecated)

> ⚠️ هذه الخدمات مهملة ويجب استخدام البدائل المذكورة

### 51. yield-prediction (Node.js - مهمل)

| البند | القيمة |
|-------|--------|
| **المضيف** | `yield-prediction` |
| **المنفذ** | `3021` |
| **المسارات** | `/yield-legacy` |
| **البديل** | `yield-prediction-service` |

---

### 52. lai-estimation (Node.js - مهمل)

| البند | القيمة |
|-------|--------|
| **المضيف** | `lai-estimation` |
| **المنفذ** | `3022` |
| **المسارات** | `/lai-legacy` |
| **البديل** | `indicators-service` |

---

### 53. crop-growth-model (Node.js - مهمل)

| البند | القيمة |
|-------|--------|
| **المضيف** | `crop-growth-model` |
| **المنفذ** | `3023` |
| **المسارات** | `/crop-growth-legacy` |
| **البديل** | `crop-intelligence-service` |

---

### 54. field-ops (Python - مهمل)

| البند | القيمة |
|-------|--------|
| **المضيف** | `field-ops` |
| **المنفذ** | `8080` |
| **المسارات** | `/field-ops-legacy` |
| **البديل** | `field-management-service` |

---

### 55. ndvi-engine (Python - مهمل)

| البند | القيمة |
|-------|--------|
| **المضيف** | `ndvi-engine` |
| **المنفذ** | `8107` |
| **المسارات** | `/ndvi-engine-legacy` |
| **البديل** | `vegetation-analysis-service` |

---

### 56. field-service (Python - مهمل)

| البند | القيمة |
|-------|--------|
| **المضيف** | `field-service` |
| **المنفذ** | `8115` |
| **المسارات** | `/field-service-legacy` |
| **البديل** | `field-management-service` |

---

### 57. ndvi-processor (Python - مهمل)

| البند | القيمة |
|-------|--------|
| **المضيف** | `ndvi-processor` |
| **المنفذ** | `8118` |
| **المسارات** | `/ndvi-processor-legacy` |
| **البديل** | `vegetation-analysis-service` |

---

### 58. satellite-service (مهمل)

| البند | القيمة |
|-------|--------|
| **المضيف** | `satellite-service` |
| **المنفذ** | `9190` |
| **المسارات** | `/api/v1/satellite-legacy`, `/satellite-legacy` |
| **البديل** | `vegetation-analysis-service` |
| **تاريخ الإهمال** | 2026-01-11 |

---

### 59. weather-advanced (مهمل)

| البند | القيمة |
|-------|--------|
| **المضيف** | `weather-advanced` |
| **المنفذ** | `9092` |
| **المسارات** | `/api/v1/weather-advanced`, `/weather-advanced` |
| **البديل** | `weather-service` |
| **تاريخ الإهمال** | 2026-01-11 |

---

### 60. crop-health-ai (مهمل)

| البند | القيمة |
|-------|--------|
| **المضيف** | `crop-health-ai` |
| **المنفذ** | `9095` |
| **المسارات** | `/api/v1/crop-health-ai`, `/crop-health-ai` |
| **البديل** | `crop-intelligence-service` |
| **تاريخ الإهمال** | 2026-01-11 |

---

### 61. fertilizer-advisor (مهمل)

| البند | القيمة |
|-------|--------|
| **المضيف** | `fertilizer-advisor` |
| **المنفذ** | `9093` |
| **المسارات** | `/api/v1/fertilizer-advisor`, `/fertilizer-advisor` |
| **البديل** | `advisory-service` |
| **تاريخ الإهمال** | 2026-01-11 |

---

## نقاط النهاية للمنصة

### 62. root-endpoint (الجذر)

| البند | القيمة |
|-------|--------|
| **المسار** | `/` |
| **الطريقة** | `GET` |

#### المخرجات

```json
{
  "platform": "SAHOOL",
  "version": "16.0.0",
  "description": "National Agricultural Intelligence Platform",
  "status": "operational",
  "endpoints": {
    "/health": "Health check",
    "/ping": "Ping check",
    "/api/v1": "API Gateway"
  },
  "documentation": "https://github.com/kafaat/sahool-unified-v15-idp"
}
```

---

### health-check (فحص الصحة)

| البند | القيمة |
|-------|--------|
| **المسارات** | `/health`, `/ping` |
| **الطريقة** | `GET` |

#### المخرجات

```json
{
  "message": "SAHOOL Platform is healthy"
}
```

---

## الخدمات غير المضمنة في Kong

الخدمات التالية **لا** يتم توجيهها عبر Kong لأنها:
- بنية تحتية داخلية
- لا تحتوي على واجهة HTTP
- عمال خلفية (workers)

| الخدمة | السبب |
|--------|-------|
| `postgres` | قاعدة بيانات داخلية |
| `pgbouncer` | مجمع اتصالات |
| `redis` | ذاكرة تخزين مؤقت |
| `nats` | ناقل الرسائل |
| `nats-prometheus-exporter` | مصدر مقاييس |
| `mqtt` | بروتوكول IoT |
| `qdrant` | قاعدة بيانات متجهات |
| `etcd` | تخزين التكوين |
| `etcd-init` | تهيئة etcd |
| `minio` | تخزين الكائنات |
| `milvus` | بحث متجهي |
| `agro-rules` | عامل NATS (لا HTTP) |
| `demo-data` | بيانات تجريبية |
| `ollama` | LLM محلي |
| `ollama-model-loader` | محمل النماذج |
| `code-fix-agent` | وكيل مستقل |
| `code-review-agent` | وكيل مستقل |

---

## ملخص الإحصائيات

| الفئة | العدد |
|-------|-------|
| **إجمالي الخدمات** | 62 |
| **خدمات Node.js** | 12 |
| **خدمات Python** | 46 |
| **خدمات مهملة** | 11 |
| **نقاط نهاية المنصة** | 2 |
| **الإضافات العالمية** | 4 |

---

## المراجع

- **ملف التكوين**: `infrastructure/gateway/kong/kong.yml`
- **سجل الخدمات**: `governance/services.yaml`
- **التوثيق**: `docs/API_GATEWAY.md`

---

_آخر تحديث: 2026-01-24_
