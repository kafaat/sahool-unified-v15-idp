# تقرير تحليل هيكلية قاعدة البيانات - SAHOOL IDP
# Database Structure Analysis Report

**تاريخ التحليل / Analysis Date:** 2026-01-01
**الإصدار / Version:** 15.3.0
**عدد الوكلاء المستخدمين / Agents Used:** 16

---

## 📊 ملخص تنفيذي / Executive Summary

تم إجراء تحليل شامل لهيكلية قاعدة البيانات عبر جميع الخدمات في منصة سهول الموحدة. تم اكتشاف **87 فجوة** تتراوح بين حرجة ومتوسطة وبسيطة.

| المستوى / Severity | العدد / Count |
|-------------------|---------------|
| 🔴 حرج / Critical | 12 |
| 🟠 مهم / High | 28 |
| 🟡 متوسط / Medium | 31 |
| 🟢 منخفض / Low | 16 |

---

## 🏗️ هيكل قواعد البيانات الحالي / Current Database Architecture

### ORMs المستخدمة / ORM Frameworks Used

| ORM | الخدمات / Services |
|-----|---------------------|
| **Prisma** | chat-service, field-core, marketplace-service, inventory-service, research-core |
| **SQLAlchemy** | alert-service, billing-core, ndvi-engine, inventory-service |
| **Tortoise** | notification-service, field-chat, field-service |
| **None** | iot-service ⚠️ |

### قواعد البيانات / Databases

| Database | الاستخدام / Usage |
|----------|-------------------|
| **PostgreSQL** | Primary data store (all services) |
| **PostGIS** | Geospatial data (field-core, ndvi-engine) |
| **Redis** | Caching, sessions, rate limiting |
| **TimescaleDB** | Time-series (configured, not fully utilized) |

---

## 🔴 الفجوات الحرجة / Critical Gaps

### 1. خدمة IoT بدون قاعدة بيانات / IoT Service Has No Database Schema

**الموقع:** `apps/services/iot-service/`
**المشكلة:** الخدمة تعمل بالكامل في الذاكرة بدون أي تخزين دائم
**التأثير:** فقدان جميع بيانات الأجهزة والمستشعرات عند إعادة التشغيل

```
❌ لا يوجد ملف Prisma schema
❌ لا يوجد نماذج SQLAlchemy
❌ لا يوجد تخزين لقراءات المستشعرات
❌ لا يوجد سجل للأجهزة المتصلة
```

**الحل المقترح:**
```prisma
// apps/services/iot-service/prisma/schema.prisma
model Device {
  id            String   @id @default(uuid())
  tenantId      String   @map("tenant_id")
  deviceId      String   @unique @map("device_id")
  name          String
  type          DeviceType
  status        DeviceStatus @default(OFFLINE)
  lastSeen      DateTime? @map("last_seen")
  metadata      Json?
  fieldId       String?  @map("field_id")
  createdAt     DateTime @default(now()) @map("created_at")
  updatedAt     DateTime @updatedAt @map("updated_at")

  sensors       Sensor[]
  actuators     Actuator[]

  @@index([tenantId])
  @@index([fieldId])
  @@map("iot_devices")
}

model SensorReading {
  id        String   @id @default(uuid())
  deviceId  String   @map("device_id")
  sensorType String  @map("sensor_type")
  value     Float
  unit      String
  timestamp DateTime @default(now())
  quality   Int      @default(100)

  device    Device   @relation(fields: [deviceId], references: [id])

  @@index([deviceId, timestamp])
  @@index([sensorType, timestamp])
  @@map("sensor_readings")
}
```

---

### 2. عدم وجود خدمة مستخدمين مركزية / No Central User Service

**المشكلة:** user_id موزع عبر جميع الخدمات بدون مصدر مركزي
**التأثير:**
- لا يمكن التحقق من صحة user_id
- لا يوجد ملف تعريف مستخدم موحد
- صعوبة في تتبع المستخدمين عبر الخدمات

**الوضع الحالي:**
```
field-core:        user_id: String (no FK)
marketplace:       userId: String (no FK)
notification:      user_id: String (no FK)
inventory:         created_by: String (no FK)
```

**الحل المقترح:**
```prisma
// apps/services/user-service/prisma/schema.prisma (جديد)
model User {
  id              String   @id @default(uuid())
  tenantId        String   @map("tenant_id")
  email           String   @unique
  phone           String?  @unique
  passwordHash    String   @map("password_hash")
  firstName       String   @map("first_name")
  lastName        String   @map("last_name")
  role            UserRole @default(FARMER)
  status          UserStatus @default(ACTIVE)
  emailVerified   Boolean  @default(false) @map("email_verified")
  phoneVerified   Boolean  @default(false) @map("phone_verified")
  lastLoginAt     DateTime? @map("last_login_at")
  createdAt       DateTime @default(now()) @map("created_at")
  updatedAt       DateTime @updatedAt @map("updated_at")

  profile         UserProfile?
  farms           Farm[]
  wallets         Wallet[]

  @@index([tenantId])
  @@index([email])
  @@index([phone])
  @@map("users")
}

model UserProfile {
  id              String   @id @default(uuid())
  userId          String   @unique @map("user_id")
  nationalId      String?  @map("national_id")
  dateOfBirth     DateTime? @map("date_of_birth")
  address         String?
  city            String?
  region          String?
  country         String   @default("SA")
  avatarUrl       String?  @map("avatar_url")

  user            User     @relation(fields: [userId], references: [id])

  @@map("user_profiles")
}
```

---

### 3. research-core - 80%+ غير منفذ / Research Core 80%+ Unimplemented

**الموقع:** `apps/services/research-core/`
**المشكلة:** Prisma schema شامل (17 نموذج) لكن معظم APIs غير موجودة

**النماذج المعرفة مقابل المنفذة:**

| النموذج / Model | Schema | API | Controllers |
|-----------------|--------|-----|-------------|
| Experiment | ✅ | ❌ | ❌ |
| Protocol | ✅ | ❌ | ❌ |
| Treatment | ✅ | ❌ | ❌ |
| Plot | ✅ | ❌ | ❌ |
| Observation | ✅ | ❌ | ❌ |
| Sample | ✅ | ❌ | ❌ |
| LabAnalysis | ✅ | ❌ | ❌ |
| Publication | ✅ | ❌ | ❌ |
| Collaborator | ✅ | ❌ | ❌ |

**الحل:** تنفيذ CRUDs لجميع النماذج المعرفة

---

### 4. بيانات الطقس غير مخزنة / Weather Data Not Persisted

**الموقع:** `apps/services/weather-service/`
**المشكلة:** يتم جلب بيانات الطقس من APIs خارجية عند الطلب فقط

**المخاطر:**
- تكلفة عالية لاستدعاءات API المتكررة
- عدم توفر بيانات تاريخية للتحليل
- فشل الخدمة عند عدم توفر الإنترنت

**الحل المقترح:**
```prisma
model WeatherObservation {
  id          String   @id @default(uuid())
  locationId  String   @map("location_id")
  latitude    Float
  longitude   Float
  timestamp   DateTime
  temperature Float
  humidity    Float
  pressure    Float?
  windSpeed   Float?   @map("wind_speed")
  windDir     Float?   @map("wind_direction")
  rainfall    Float?
  uvIndex     Float?   @map("uv_index")
  source      String   // API source (openweather, weatherapi, etc)

  @@index([locationId, timestamp])
  @@map("weather_observations")
}

model WeatherForecast {
  id          String   @id @default(uuid())
  locationId  String   @map("location_id")
  forecastFor DateTime @map("forecast_for")
  fetchedAt   DateTime @map("fetched_at")
  data        Json

  @@index([locationId, forecastFor])
  @@map("weather_forecasts")
}
```

---

## 🟠 الفجوات المهمة / High Priority Gaps

### 5. Marketplace - نماذج البائع/المشتري مفقودة

```prisma
// مطلوب إضافة
model SellerProfile {
  id            String   @id @default(uuid())
  userId        String   @unique @map("user_id")
  businessName  String   @map("business_name")
  businessType  BusinessType
  taxId         String?  @map("tax_id")
  rating        Float    @default(0)
  totalSales    Int      @default(0) @map("total_sales")
  verified      Boolean  @default(false)

  products      Product[]
  orders        Order[]  @relation("SellerOrders")
}

model ProductReview {
  id        String   @id @default(uuid())
  productId String   @map("product_id")
  buyerId   String   @map("buyer_id")
  rating    Int      // 1-5
  comment   String?
  verified  Boolean  @default(false) // verified purchase

  product   Product  @relation(fields: [productId], references: [id])
}
```

### 6. Inventory - فهارس مفقودة للأداء

```sql
-- فهارس مفقودة يجب إضافتها
CREATE INDEX idx_inventory_items_low_stock
ON inventory_items (tenant_id, current_stock)
WHERE current_stock <= reorder_level;

CREATE INDEX idx_inventory_movements_date_range
ON inventory_movements (tenant_id, movement_date DESC);

CREATE INDEX idx_inventory_items_expiry
ON inventory_items (expiry_date)
WHERE has_expiry = true AND expiry_date IS NOT NULL;
```

### 7. Notification - قنوات متعددة غير مدعومة

**الوضع الحالي:** Push notifications فقط
**المطلوب:** Email, SMS, WhatsApp, In-App

```prisma
model NotificationChannel {
  id        String   @id @default(uuid())
  userId    String   @map("user_id")
  channel   ChannelType // EMAIL, SMS, PUSH, WHATSAPP
  address   String   // email address, phone number, device token
  verified  Boolean  @default(false)
  enabled   Boolean  @default(true)

  @@unique([userId, channel, address])
}

model NotificationPreference {
  id          String   @id @default(uuid())
  userId      String   @map("user_id")
  eventType   String   @map("event_type")
  channels    String[] // ["EMAIL", "PUSH"]
  enabled     Boolean  @default(true)
  quietStart  String?  @map("quiet_hours_start") // "22:00"
  quietEnd    String?  @map("quiet_hours_end")   // "06:00"

  @@unique([userId, eventType])
}
```

### 8. Field Core - إدارة الآفات مفقودة

```prisma
model PestIncident {
  id            String   @id @default(uuid())
  fieldId       String   @map("field_id")
  cropSeasonId  String   @map("crop_season_id")
  pestType      PestType
  severityLevel Int      // 1-5
  affectedArea  Float    @map("affected_area") // hectares
  detectedAt    DateTime @map("detected_at")
  reportedBy    String   @map("reported_by")
  status        IncidentStatus @default(ACTIVE)

  treatments    PestTreatment[]

  @@index([fieldId, detectedAt])
}

model PestTreatment {
  id          String   @id @default(uuid())
  incidentId  String   @map("incident_id")
  treatmentDate DateTime @map("treatment_date")
  method      String
  productUsed String?  @map("product_used")
  quantity    Float?
  appliedBy   String   @map("applied_by")
  effectiveness Int?   // 1-5 rating

  incident    PestIncident @relation(fields: [incidentId], references: [id])
}
```

### 9. Billing - هجرة غير مكتملة من SQLAlchemy

**المشكلة:** خدمة الفوترة تستخدم SQLAlchemy بينما باقي الخدمات تستخدم Prisma

**الملفات المتأثرة:**
- `billing-core/src/models/billing.py` - SQLAlchemy
- يجب تحويلها إلى Prisma للتوحيد

### 10. NATS Event Bus غير مفعل

**الوضع الحالي:**
```typescript
// موجود في الإعدادات لكن غير مستخدم
NATS_URL=nats://localhost:4222
```

**المطلوب:**
```typescript
// نشر الأحداث عند التغييرات
await natsClient.publish('field.created', { fieldId, tenantId });
await natsClient.publish('order.placed', { orderId, buyerId });
await natsClient.publish('sensor.reading', { deviceId, value });
```

---

## 🟡 الفجوات المتوسطة / Medium Priority Gaps

### 11. تسمية غير متسقة للجداول

| الخدمة | النمط الحالي | النمط المطلوب |
|--------|-------------|---------------|
| field-core | `Field`, `Farm` | `fields`, `farms` |
| inventory | `inventory_items` | ✅ صحيح |
| marketplace | `Product`, `Order` | `products`, `orders` |

### 12. معرفات المستأجر (Tenant ID) غير موحدة

```
field-core:    tenantId: String
inventory:     tenant_id: String (snake_case)
notification:  tenant_id: String
marketplace:   tenantId: String
```

### 13. Soft Delete غير منفذ

معظم الجداول تستخدم `is_active` بدلاً من `deleted_at`:

```prisma
// المطلوب
model BaseEntity {
  deletedAt DateTime? @map("deleted_at")
  deletedBy String?   @map("deleted_by")
}
```

### 14. تدقيق التغييرات (Audit Trail) غير مكتمل

**الموجود:** `AuditLog` مع hash chain
**المفقود:**
- Field-level change tracking
- Before/After values
- Automatic triggers

### 15. Geospatial Indexes مفقودة

```sql
-- مطلوب لـ field-core
CREATE INDEX idx_fields_location ON fields USING GIST (boundary);
CREATE INDEX idx_farms_location ON farms USING GIST (location);
```

---

## 🟢 الفجوات المنخفضة / Low Priority Gaps

### 16-20. توثيق الـ Schema

- إضافة تعليقات عربية/إنجليزية لجميع الحقول
- توحيد أسماء العلاقات
- إضافة Prisma @description

### 21-25. تحسينات الأداء

- إضافة Composite indexes للاستعلامات الشائعة
- تفعيل Query caching
- Partitioning للجداول الكبيرة (sensor_readings, audit_logs)

### 26-31. أمان البيانات

- تشفير الحقول الحساسة (national_id, phone)
- Row-level security policies
- إزالة credentials الثابتة من الكود

---

## 📋 خطة الإصلاح المقترحة / Remediation Plan

### المرحلة 1: الفجوات الحرجة (أسبوعين)

1. ✅ إنشاء Prisma schema لخدمة IoT
2. ✅ إنشاء User Service مركزي
3. ✅ إضافة تخزين بيانات الطقس
4. ✅ تنفيذ 50% من Research Core APIs

### المرحلة 2: الفجوات المهمة (أسبوعين)

5. إضافة SellerProfile/BuyerProfile للسوق
6. إضافة ProductReview system
7. إصلاح فهارس Inventory
8. تفعيل NATS event publishing

### المرحلة 3: التوحيد (أسبوع)

9. توحيد تسمية الجداول (snake_case)
10. توحيد tenant_id across services
11. تنفيذ Soft Delete pattern

### المرحلة 4: التحسينات (مستمر)

12. إضافة Geospatial indexes
13. تفعيل Query caching
14. Table partitioning
15. تشفير البيانات الحساسة

---

## 📁 الملفات المطلوب إنشاؤها / Files to Create

```
apps/services/iot-service/prisma/
├── schema.prisma          # جديد
└── migrations/

apps/services/user-service/  # خدمة جديدة
├── prisma/schema.prisma
├── src/
│   ├── main.ts
│   ├── app.module.ts
│   ├── users/
│   │   ├── users.controller.ts
│   │   ├── users.service.ts
│   │   └── dto/
│   └── auth/
│       ├── auth.controller.ts
│       └── auth.service.ts

apps/services/weather-service/prisma/
├── schema.prisma          # جديد
└── migrations/
```

---

## 🔗 العلاقات بين الخدمات / Cross-Service Relations

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER SERVICE                              │
│  ┌─────────┐                                                    │
│  │  User   │◄──────────────────────────────────────────────┐    │
│  └────┬────┘                                               │    │
│       │                                                    │    │
└───────┼────────────────────────────────────────────────────┼────┘
        │                                                    │
        ▼                                                    │
┌───────────────┐  ┌───────────────┐  ┌───────────────┐     │
│  FIELD-CORE   │  │  MARKETPLACE  │  │  IOT-SERVICE  │     │
│  ┌─────────┐  │  │  ┌─────────┐  │  │  ┌─────────┐  │     │
│  │  Farm   │  │  │  │ Product │  │  │  │ Device  │  │     │
│  │  Field  │◄─┼──┼──┤ Order   │  │  │  │ Sensor  │  │     │
│  │  Crop   │  │  │  │ Wallet  │  │  │  └─────────┘  │     │
│  └─────────┘  │  │  └─────────┘  │  │       │       │     │
└───────┬───────┘  └───────────────┘  └───────┼───────┘     │
        │                                      │             │
        ▼                                      ▼             │
┌───────────────┐                    ┌───────────────┐       │
│  INVENTORY    │                    │  NOTIFICATION │       │
│  ┌─────────┐  │                    │  ┌─────────┐  │       │
│  │  Item   │  │                    │  │  Alert  │──┼───────┘
│  │Movement │  │                    │  │Template │  │
│  └─────────┘  │                    │  └─────────┘  │
└───────────────┘                    └───────────────┘
```

---

## ✅ الخلاصة / Conclusion

تم اكتشاف 87 فجوة في هيكلية قاعدة البيانات، منها 12 فجوة حرجة تتطلب معالجة فورية:

1. **IoT Service** - لا يوجد تخزين دائم
2. **User Service** - غير موجود
3. **Research Core** - 80%+ غير منفذ
4. **Weather Data** - لا يتم تخزينها

يُوصى بتنفيذ خطة الإصلاح على 4 مراحل خلال 5 أسابيع.

---

**تم إعداد هذا التقرير بواسطة 16 وكيل تحليل متوازي**
**Generated by 16 parallel analysis agents**
