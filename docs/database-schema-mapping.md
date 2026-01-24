# Database Schema Mapping | توثيق مخطط قاعدة البيانات

> **الإصدار**: 16.0.0
> **تاريخ التحديث**: 2026-01-24
> **قاعدة البيانات**: PostgreSQL 16+ with PostGIS 3.4
> **إجمالي الجداول**: 60+ جدول

---

## جدول المحتويات | Table of Contents

1. [نظرة عامة | Overview](#نظرة-عامة--overview)
2. [خدمات Prisma ORM | Prisma ORM Services](#خدمات-prisma-orm--prisma-orm-services)
3. [خدمات SQLAlchemy | SQLAlchemy Services](#خدمات-sqlalchemy--sqlalchemy-services)
4. [خدمات Tortoise ORM | Tortoise ORM Services](#خدمات-tortoise-orm--tortoise-orm-services)
5. [العلاقات الرئيسية | Key Relationships](#العلاقات-الرئيسية--key-relationships)
6. [ملخص الإحصائيات | Statistics Summary](#ملخص-الإحصائيات--statistics-summary)

---

## نظرة عامة | Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     PostgreSQL 16+ with PostGIS 3.4                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐              │
│  │   Prisma ORM    │  │   SQLAlchemy    │  │  Tortoise ORM   │              │
│  │   (Node.js)     │  │    (Python)     │  │    (Python)     │              │
│  │   8 خدمات       │  │   4 خدمات       │  │   1 خدمة        │              │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘              │
│           │                    │                    │                        │
│           ▼                    ▼                    ▼                        │
│  ┌─────────────────────────────────────────────────────────────────┐        │
│  │                     Database Tables (60+)                        │        │
│  └─────────────────────────────────────────────────────────────────┘        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### تقنيات ORM المستخدمة | ORM Technologies

| التقنية | الخدمات | اللغة |
|---------|---------|-------|
| Prisma | user-service, field-management, marketplace, chat, iot, inventory, weather, research | Node.js/TypeScript |
| SQLAlchemy | alert-service, billing-core, equipment-service, task-service | Python |
| Tortoise ORM | notification-service | Python |

### الأنماط الشائعة | Common Patterns

| النمط | الوصف |
|-------|-------|
| Multi-Tenancy | جميع الجداول تحتوي على `tenant_id` لعزل البيانات |
| Soft Deletes | `deleted_at`, `deleted_by` للحذف الناعم |
| Bilingual | أعمدة `*_ar` للنصوص العربية |
| Optimistic Locking | `version` لمنع التضاربات |
| Audit Trail | `created_at`, `updated_at` مع timezone |
| PostGIS | دعم البيانات الجغرافية (Point, Polygon) |

---

## خدمات Prisma ORM | Prisma ORM Services

### 1. User Service | خدمة المستخدمين

**الملف**: `apps/services/user-service/prisma/schema.prisma`

#### users | المستخدمون

| العمود | Column | النوع | Type | المفتاح | Key | ملاحظات |
|--------|--------|-------|------|---------|-----|---------|
| id | UUID | PK | مُولّد تلقائياً |
| tenant_id | String | - | معرف المستأجر |
| email | String | UNIQUE | البريد الإلكتروني |
| phone | String? | - | الهاتف (اختياري) |
| password_hash | String | - | كلمة المرور المشفرة |
| first_name | String | - | الاسم الأول |
| last_name | String | - | اسم العائلة |
| role | UserRole | - | ADMIN, MANAGER, FARMER, WORKER, VIEWER |
| status | UserStatus | - | ACTIVE, INACTIVE, SUSPENDED, PENDING |
| email_verified | Boolean | - | false افتراضياً |
| phone_verified | Boolean | - | false افتراضياً |
| last_login_at | DateTime? | - | آخر تسجيل دخول |
| failed_login_attempts | Int | - | 0 افتراضياً |
| lockout_until | DateTime? | - | قفل الحساب حتى |
| password_reset_token | String? | - | توكن إعادة التعيين |
| password_reset_expiry | DateTime? | - | انتهاء صلاحية التوكن |
| created_at | DateTime | - | تاريخ الإنشاء |
| updated_at | DateTime | - | تاريخ التحديث |

**العلاقات**: `sessions[]`, `refreshTokens[]`, `profile`, `roles[]`
**الفهارس**: `tenant_id`, `email`, `status`, `role`

```prisma
model User {
  id                    String        @id @default(uuid())
  tenantId             String        @map("tenant_id")
  email                String        @unique
  phone                String?
  passwordHash         String        @map("password_hash")
  firstName            String        @map("first_name")
  lastName             String        @map("last_name")
  role                 UserRole      @default(FARMER)
  status               UserStatus    @default(ACTIVE)
  emailVerified        Boolean       @default(false) @map("email_verified")
  phoneVerified        Boolean       @default(false) @map("phone_verified")
  lastLoginAt          DateTime?     @map("last_login_at")
  failedLoginAttempts  Int           @default(0) @map("failed_login_attempts")
  lockoutUntil         DateTime?     @map("lockout_until")
  passwordResetToken   String?       @map("password_reset_token")
  passwordResetExpiry  DateTime?     @map("password_reset_expiry")
  createdAt            DateTime      @default(now()) @map("created_at")
  updatedAt            DateTime      @updatedAt @map("updated_at")

  sessions      UserSession[]
  refreshTokens RefreshToken[]
  profile       UserProfile?

  @@index([tenantId])
  @@index([email])
  @@index([status])
  @@index([role])
  @@map("users")
}
```

#### user_profiles | ملفات المستخدمين

| العمود | النوع | المفتاح | ملاحظات |
|--------|-------|---------|---------|
| id | UUID | PK | مُولّد تلقائياً |
| user_id | UUID | FK, UNIQUE | مرجع المستخدم |
| national_id | String? | - | الهوية الوطنية |
| date_of_birth | DateTime? | - | تاريخ الميلاد |
| address | String? | - | العنوان |
| city | String? | - | المدينة |
| region | String? | - | المنطقة |
| country | String | - | "SA" افتراضياً |
| avatar_url | String? | - | صورة الملف الشخصي |

#### user_sessions | جلسات المستخدمين

| العمود | النوع | المفتاح | ملاحظات |
|--------|-------|---------|---------|
| id | UUID | PK | مُولّد تلقائياً |
| user_id | String | FK | مرجع المستخدم |
| token | String | UNIQUE | توكن الجلسة |
| ip_address | String? | - | عنوان IP |
| user_agent | String? | - | معلومات المتصفح |
| expires_at | DateTime | - | انتهاء الصلاحية |

#### refresh_tokens | توكنات التجديد

| العمود | النوع | المفتاح | ملاحظات |
|--------|-------|---------|---------|
| id | UUID | PK | مُولّد تلقائياً |
| user_id | String | FK | مرجع المستخدم |
| jti | String | UNIQUE | معرف JWT |
| family | String | - | عائلة التوكن للتدوير |
| token | String | UNIQUE | توكن التجديد |
| expires_at | DateTime | - | انتهاء الصلاحية |
| revoked | Boolean | - | false افتراضياً |
| used | Boolean | - | false افتراضياً |
| replaced_by | String? | - | JTI البديل |

---

### 2. Field Management Service | خدمة إدارة الحقول

**الملف**: `apps/services/field-management-service/prisma/schema.prisma`

#### farms | المزارع

| العمود | النوع | المفتاح | ملاحظات |
|--------|-------|---------|---------|
| id | UUID | PK | مُولّد تلقائياً |
| name | String(255) | - | اسم المزرعة |
| tenant_id | String(100) | - | معرف المستأجر |
| owner_id | UUID? | - | المالك |
| location | Geometry | - | PostGIS Point(4326) |
| boundary | Geometry | - | PostGIS Polygon(4326) |
| total_area_hectares | Decimal(10,4)? | - | المساحة الإجمالية |
| address | String? | - | العنوان |
| phone | String? | - | الهاتف |
| email | String? | - | البريد الإلكتروني |
| is_deleted | Boolean | - | false افتراضياً |
| created_at | DateTime | - | timestamptz |
| updated_at | DateTime | - | timestamptz |

**العلاقات**: `fields[]`

#### fields | الحقول

| العمود | النوع | المفتاح | ملاحظات |
|--------|-------|---------|---------|
| id | UUID | PK | مُولّد تلقائياً |
| version | Int | - | 1 افتراضياً (Optimistic Locking) |
| name | String(255) | - | اسم الحقل |
| tenant_id | String(100) | - | معرف المستأجر |
| crop_type | String(100) | - | نوع المحصول |
| owner_id | UUID? | - | المالك |
| farm_id | UUID? | FK | مرجع المزرعة |
| boundary | Geometry | - | PostGIS Polygon(4326) |
| centroid | Geometry | - | PostGIS Point(4326) |
| area_hectares | Decimal(10,4)? | - | المساحة |
| health_score | Decimal(3,2)? | - | درجة الصحة |
| ndvi_value | Decimal(4,3)? | - | قيمة NDVI |
| status | FieldStatus | - | active, fallow, harvested, preparing, inactive |
| planting_date | Date? | - | تاريخ الزراعة |
| expected_harvest | Date? | - | الحصاد المتوقع |
| irrigation_type | String(50)? | - | نوع الري |
| soil_type | String(100)? | - | نوع التربة |
| metadata | JSONB? | - | بيانات إضافية |
| is_deleted | Boolean | - | false افتراضياً |
| server_updated_at | DateTime | - | آخر تحديث الخادم |
| etag | String(64)? | - | للتحكم بالتخزين المؤقت |

**العلاقات**: `farm`, `boundaryHistory[]`, `tasks[]`, `ndviReadings[]`
**الفهارس**: `tenant_id`, `server_updated_at`, `status`, `crop_type`

```prisma
model Field {
  id                String         @id @default(uuid())
  version           Int            @default(1)
  name              String         @db.VarChar(255)
  tenantId          String         @map("tenant_id") @db.VarChar(100)
  cropType          String         @map("crop_type") @db.VarChar(100)
  ownerId           String?        @map("owner_id") @db.Uuid
  farmId            String?        @map("farm_id") @db.Uuid
  boundary          Unsupported("geometry(Polygon,4326)")?
  centroid          Unsupported("geometry(Point,4326)")?
  areaHectares      Decimal?       @map("area_hectares") @db.Decimal(10, 4)
  healthScore       Decimal?       @map("health_score") @db.Decimal(3, 2)
  ndviValue         Decimal?       @map("ndvi_value") @db.Decimal(4, 3)
  status            FieldStatus    @default(active)
  plantingDate      DateTime?      @map("planting_date") @db.Date
  expectedHarvest   DateTime?      @map("expected_harvest") @db.Date
  irrigationType    String?        @map("irrigation_type") @db.VarChar(50)
  soilType          String?        @map("soil_type") @db.VarChar(100)
  metadata          Json?          @db.JsonB
  isDeleted         Boolean        @default(false) @map("is_deleted")
  serverUpdatedAt   DateTime       @default(now()) @map("server_updated_at") @db.Timestamptz
  etag              String?        @db.VarChar(64)
  createdAt         DateTime       @default(now()) @map("created_at") @db.Timestamptz
  updatedAt         DateTime       @updatedAt @map("updated_at") @db.Timestamptz

  farm              Farm?          @relation(fields: [farmId], references: [id])
  boundaryHistory   FieldBoundaryHistory[]
  tasks             Task[]
  ndviReadings      NdviReading[]

  @@index([tenantId])
  @@index([serverUpdatedAt])
  @@index([status])
  @@index([cropType])
  @@map("fields")
}
```

#### sync_status | حالة المزامنة

| العمود | النوع | المفتاح | ملاحظات |
|--------|-------|---------|---------|
| id | UUID | PK | مُولّد تلقائياً |
| device_id | String(100) | UNIQUE مع user_id | معرف الجهاز |
| user_id | String(100) | - | معرف المستخدم |
| tenant_id | String(100) | - | معرف المستأجر |
| last_sync_at | DateTime? | - | آخر مزامنة |
| last_sync_version | BigInt | - | 0 افتراضياً |
| status | SyncState | - | idle, syncing, error, conflict |
| pending_uploads | Int | - | 0 افتراضياً |
| pending_downloads | Int | - | 0 افتراضياً |
| conflicts_count | Int | - | 0 افتراضياً |
| last_error | Text? | - | آخر خطأ |
| device_info | JSONB? | - | معلومات الجهاز |

#### tasks | المهام

| العمود | النوع | المفتاح | ملاحظات |
|--------|-------|---------|---------|
| id | UUID | PK | مُولّد تلقائياً |
| title | String(255) | - | العنوان بالإنجليزية |
| title_ar | String(255)? | - | العنوان بالعربية |
| description | Text? | - | الوصف |
| task_type | TaskType | - | irrigation, fertilization, spraying, etc. |
| priority | Priority | - | low, medium, high, urgent |
| status | TaskState | - | pending, in_progress, completed, cancelled, overdue |
| due_date | DateTime? | - | تاريخ الاستحقاق |
| scheduled_time | String(10)? | - | HH:MM |
| completed_at | DateTime? | - | تاريخ الإكمال |
| assigned_to | String(100)? | - | المكلف |
| created_by | String(100) | - | المنشئ |
| field_id | UUID? | FK | مرجع الحقل |
| estimated_minutes | Int? | - | الوقت المقدر |
| actual_minutes | Int? | - | الوقت الفعلي |
| completion_notes | Text? | - | ملاحظات الإكمال |
| evidence | JSONB? | - | الأدلة (صور، ملاحظات) |

#### ndvi_readings | قراءات NDVI

| العمود | النوع | المفتاح | ملاحظات |
|--------|-------|---------|---------|
| id | UUID | PK | مُولّد تلقائياً |
| field_id | UUID | FK | مرجع الحقل |
| value | Decimal(4,3) | - | -1.000 إلى 1.000 |
| captured_at | DateTime | - | وقت الالتقاط |
| source | String(50) | - | "satellite" افتراضياً |
| cloud_cover | Decimal(5,2)? | - | 0-100% |
| quality | String(20)? | - | good, moderate, poor |
| satellite_name | String(50)? | - | اسم القمر الصناعي |
| band_info | JSONB? | - | معلومات النطاق |

---

### 3. Marketplace Service | خدمة السوق

**الملف**: `apps/services/marketplace-service/prisma/schema.prisma`

#### products | المنتجات

| العمود | النوع | المفتاح | ملاحظات |
|--------|-------|---------|---------|
| id | UUID | PK | مُولّد تلقائياً |
| name | String | - | اسم المنتج بالإنجليزية |
| name_ar | String | - | اسم المنتج بالعربية |
| category | ProductCategory | - | HARVEST, SEEDS, FERTILIZER, PESTICIDE, EQUIPMENT, IRRIGATION, OTHER |
| price | Float | - | السعر بالريال |
| stock | Float | - | الكمية |
| unit | String | - | ton, kg, unit |
| description | String? | - | الوصف بالإنجليزية |
| description_ar | String? | - | الوصف بالعربية |
| image_url | String? | - | رابط الصورة |
| seller_id | String | - | معرف البائع |
| seller_type | SellerType | - | FARMER, COMPANY, COOPERATIVE |
| seller_name | String? | - | اسم البائع |
| governorate | String? | - | المحافظة |
| district | String? | - | المديرية |
| crop_type | String? | - | نوع المحصول |
| harvest_date | DateTime? | - | تاريخ الحصاد |
| quality_grade | String? | - | A, B, C |
| status | ProductStatus | - | AVAILABLE, SOLD_OUT, RESERVED, PENDING |
| featured | Boolean | - | false افتراضياً |
| deleted_at | DateTime? | - | الحذف الناعم |
| deleted_by | String? | - | من حذف |

**العلاقات**: `orderItems[]`

#### orders | الطلبات

| العمود | النوع | المفتاح | ملاحظات |
|--------|-------|---------|---------|
| id | UUID | PK | مُولّد تلقائياً |
| order_number | String | UNIQUE | رقم الطلب |
| buyer_id | String | - | معرف المشتري |
| buyer_name | String? | - | اسم المشتري |
| buyer_phone | String? | - | هاتف المشتري |
| subtotal | Float | - | المجموع الفرعي |
| delivery_fee | Float | - | 0 افتراضياً |
| service_fee | Float | - | 0 افتراضياً |
| total_amount | Float | - | المجموع الكلي |
| status | OrderStatus | - | PENDING, CONFIRMED, PROCESSING, SHIPPED, DELIVERED, CANCELLED |
| payment_status | PaymentStatus | - | UNPAID, PARTIAL, PAID, REFUNDED |
| payment_method | String? | - | wallet, cash, bank_transfer |
| delivery_address | String? | - | عنوان التوصيل |
| delivery_date | DateTime? | - | تاريخ التوصيل |
| delivery_notes | String? | - | ملاحظات التوصيل |
| deleted_at | DateTime? | - | الحذف الناعم |

**العلاقات**: `items[]`, `transactions[]`

#### wallets | المحافظ

| العمود | النوع | المفتاح | ملاحظات |
|--------|-------|---------|---------|
| id | UUID | PK | مُولّد تلقائياً |
| user_id | String | UNIQUE | معرف المستخدم |
| user_type | String | - | farmer, company, buyer |
| balance | Float | - | 0 افتراضياً |
| escrow_balance | Float | - | 0 افتراضياً |
| currency | String | - | "YER" افتراضياً |
| credit_score | Int | - | 300 افتراضياً (300-850) |
| credit_tier | CreditTier | - | BRONZE, SILVER, GOLD, PLATINUM |
| loan_limit | Float | - | 0 افتراضياً |
| current_loan | Float | - | 0 افتراضياً |
| daily_withdraw_limit | Float | - | 10000 افتراضياً |
| single_transaction_limit | Float | - | 50000 افتراضياً |
| requires_pin_for_amount | Float | - | 5000 افتراضياً |
| daily_withdrawn_today | Float | - | 0 افتراضياً |
| version | Int | - | 0 افتراضياً (Optimistic Locking) |
| is_verified | Boolean | - | false افتراضياً |
| kyc_status | String? | - | pending, approved, rejected |
| pin | String? | - | مشفر |

**العلاقات**: `transactions[]`, `loans[]`, `escrows[]`, `scheduledPayments[]`

#### transactions | المعاملات

| العمود | النوع | المفتاح | ملاحظات |
|--------|-------|---------|---------|
| id | UUID | PK | مُولّد تلقائياً |
| wallet_id | String | FK | مرجع المحفظة |
| type | TransactionType | - | DEPOSIT, WITHDRAWAL, PURCHASE, SALE, LOAN, REPAYMENT, FEE, REFUND |
| amount | Float | - | المبلغ |
| balance_after | Float | - | الرصيد بعد |
| balance_before | Float? | - | الرصيد قبل |
| reference_id | String? | - | order_id, loan_id |
| reference_type | String? | - | نوع المرجع |
| description | String? | - | الوصف بالإنجليزية |
| description_ar | String? | - | الوصف بالعربية |
| status | TransactionStatus | - | PENDING, COMPLETED, FAILED, CANCELLED |
| idempotency_key | String? | UNIQUE | لمنع التكرار |
| user_id | String? | - | معرف المستخدم |
| ip_address | String? | - | عنوان IP |

#### loans | القروض

| العمود | النوع | المفتاح | ملاحظات |
|--------|-------|---------|---------|
| id | UUID | PK | مُولّد تلقائياً |
| wallet_id | String | FK | مرجع المحفظة |
| amount | Float | - | مبلغ القرض |
| interest_rate | Float | - | 0 افتراضياً |
| total_due | Float | - | الإجمالي المستحق |
| paid_amount | Float | - | 0 افتراضياً |
| term_months | Int | - | مدة القرض |
| start_date | DateTime | - | تاريخ البدء |
| due_date | DateTime | - | تاريخ الاستحقاق |
| purpose | LoanPurpose | - | SEEDS, FERTILIZER, EQUIPMENT, IRRIGATION, EXPANSION, EMERGENCY, OTHER |
| purpose_details | String? | - | تفاصيل الغرض |
| collateral_type | String? | - | crop, equipment, land |
| collateral_value | Float? | - | قيمة الضمان |
| status | LoanStatus | - | PENDING, APPROVED, ACTIVE, PAID, DEFAULTED, REJECTED |

#### escrows | الضمانات

| العمود | النوع | المفتاح | ملاحظات |
|--------|-------|---------|---------|
| id | UUID | PK | مُولّد تلقائياً |
| order_id | String | UNIQUE, FK | مرجع الطلب |
| buyer_wallet_id | String | FK | محفظة المشتري |
| seller_wallet_id | String | FK | محفظة البائع |
| amount | Float | - | مبلغ الضمان |
| status | EscrowStatus | - | HELD, RELEASED, REFUNDED, DISPUTED, CANCELLED |
| notes | String? | - | ملاحظات |
| dispute_reason | String? | - | سبب النزاع |
| released_at | DateTime? | - | تاريخ التحرير |
| refunded_at | DateTime? | - | تاريخ الاسترداد |

---

### 4. Chat Service | خدمة المحادثة

**الملف**: `apps/services/chat-service/prisma/schema.prisma`

#### conversations | المحادثات

| العمود | النوع | المفتاح | ملاحظات |
|--------|-------|---------|---------|
| id | UUID | PK | مُولّد تلقائياً |
| participant_ids | String[] | - | مصفوفة معرفات المشاركين |
| product_id | String? | - | مرجع المنتج |
| order_id | String? | - | مرجع الطلب |
| last_message | String? | - | آخر رسالة |
| last_message_at | DateTime? | - | وقت آخر رسالة |
| is_active | Boolean | - | true افتراضياً |

**العلاقات**: `messages[]`, `participants[]`

#### messages | الرسائل

| العمود | النوع | المفتاح | ملاحظات |
|--------|-------|---------|---------|
| id | UUID | PK | مُولّد تلقائياً |
| conversation_id | String | FK | مرجع المحادثة |
| sender_id | String | - | معرف المرسل |
| content | String | - | محتوى الرسالة |
| message_type | MessageType | - | TEXT, IMAGE, OFFER, SYSTEM |
| attachment_url | String? | - | رابط المرفق |
| offer_amount | Float? | - | مبلغ العرض |
| offer_currency | String | - | "YER" افتراضياً |
| is_read | Boolean | - | false افتراضياً |
| read_at | DateTime? | - | وقت القراءة |

#### participants | المشاركون

| العمود | النوع | المفتاح | ملاحظات |
|--------|-------|---------|---------|
| id | UUID | PK | مُولّد تلقائياً |
| conversation_id | String | FK | مرجع المحادثة |
| user_id | String | - | معرف المستخدم |
| role | ParticipantRole | - | BUYER, SELLER |
| last_read_at | DateTime? | - | آخر قراءة |
| unread_count | Int | - | 0 افتراضياً |
| is_online | Boolean | - | false افتراضياً |
| last_seen_at | DateTime? | - | آخر ظهور |
| is_typing | Boolean | - | false افتراضياً |

**القيود**: UNIQUE(conversation_id, user_id)

---

### 5. IoT Service | خدمة إنترنت الأشياء

**الملف**: `apps/services/iot-service/prisma/schema.prisma`

#### devices | الأجهزة

| العمود | النوع | المفتاح | ملاحظات |
|--------|-------|---------|---------|
| id | UUID | PK | مُولّد تلقائياً |
| tenant_id | String | - | معرف المستأجر |
| device_id | String | UNIQUE مع tenant_id | معرف الجهاز الفيزيائي |
| name | String | - | اسم الجهاز |
| type | DeviceType | - | SOIL_MOISTURE_SENSOR, TEMPERATURE_SENSOR, etc. |
| status | DeviceStatus | - | ONLINE, OFFLINE, MAINTENANCE, ERROR, INACTIVE |
| last_seen | DateTime? | - | آخر اتصال |
| metadata | JSONB? | - | بيانات إضافية |
| field_id | String? | - | مرجع الحقل |

**العلاقات**: `sensors[]`, `sensorReadings[]`, `actuators[]`, `alerts[]`

#### sensors | المستشعرات

| العمود | النوع | المفتاح | ملاحظات |
|--------|-------|---------|---------|
| id | UUID | PK | مُولّد تلقائياً |
| device_id | String | FK | مرجع الجهاز |
| sensor_type | SensorType | - | SOIL_MOISTURE, TEMPERATURE, etc. |
| unit | String | - | %, °C, L/min |
| calibration_data | JSONB? | - | بيانات المعايرة |
| last_reading | Float? | - | آخر قراءة |
| last_reading_at | DateTime? | - | وقت آخر قراءة |

#### sensor_readings | قراءات المستشعرات

| العمود | النوع | المفتاح | ملاحظات |
|--------|-------|---------|---------|
| id | UUID | PK | مُولّد تلقائياً |
| sensor_id | String | FK | مرجع المستشعر |
| device_id | String | FK | مرجع الجهاز |
| value | Float | - | القيمة |
| unit | String | - | وحدة القياس |
| timestamp | DateTime | - | الوقت |
| quality | Float? | - | 0-1, null=unknown |
| metadata | JSONB? | - | بيانات إضافية |

#### actuators | المشغلات

| العمود | النوع | المفتاح | ملاحظات |
|--------|-------|---------|---------|
| id | UUID | PK | مُولّد تلقائياً |
| device_id | String | FK | مرجع الجهاز |
| actuator_type | ActuatorType | - | VALVE, PUMP, MOTOR, RELAY, SWITCH, SERVO, CUSTOM |
| name | String? | - | الاسم |
| current_state | JSONB? | - | {position, enabled} |
| last_command | String? | - | آخر أمر |
| last_command_at | DateTime? | - | وقت آخر أمر |

#### actuator_commands | أوامر المشغلات

| العمود | النوع | المفتاح | ملاحظات |
|--------|-------|---------|---------|
| id | UUID | PK | مُولّد تلقائياً |
| actuator_id | String | FK | مرجع المشغل |
| command | String | - | open, close, set_position |
| parameters | JSONB? | - | معاملات إضافية |
| status | CommandStatus | - | PENDING, EXECUTING, COMPLETED, FAILED, TIMEOUT, CANCELLED |
| requested_at | DateTime | - | وقت الطلب |
| executed_at | DateTime? | - | وقت التنفيذ |
| completed_at | DateTime? | - | وقت الإكمال |
| error_message | String? | - | رسالة الخطأ |

#### device_alerts | تنبيهات الأجهزة

| العمود | النوع | المفتاح | ملاحظات |
|--------|-------|---------|---------|
| id | UUID | PK | مُولّد تلقائياً |
| device_id | String | FK | مرجع الجهاز |
| tenant_id | String | - | للتصفية السريع |
| alert_type | String | - | offline, battery_low, sensor_error |
| severity | AlertSeverity | - | INFO, WARNING, ERROR, CRITICAL |
| message | String | - | رسالة التنبيه |
| acknowledged | Boolean | - | false افتراضياً |
| acknowledged_by | String? | - | من أقرّ |
| acknowledged_at | DateTime? | - | وقت الإقرار |
| resolved_at | DateTime? | - | وقت الحل |

---

### 6. Inventory Service | خدمة المخزون

**الملف**: `apps/services/inventory-service/prisma/schema.prisma`

#### inventory_items | عناصر المخزون

| العمود | النوع | المفتاح | ملاحظات |
|--------|-------|---------|---------|
| id | UUID | PK | مُولّد تلقائياً |
| tenant_id | String | - | معرف المستأجر |
| name | String | - | الاسم بالإنجليزية |
| name_ar | String | - | الاسم بالعربية |
| sku | String? | UNIQUE | رمز المنتج |
| category | ItemCategory | - | SEEDS, FERTILIZER, PESTICIDE, HERBICIDE, FUNGICIDE, etc. |
| description | String? | - | الوصف بالإنجليزية |
| description_ar | String? | - | الوصف بالعربية |
| quantity | Float | - | 0 افتراضياً |
| unit | String | - | kg, liter, bag, bottle |
| reorder_level | Float | - | 0 افتراضياً |
| reorder_point | Float? | - | نقطة إعادة الطلب |
| max_stock | Float? | - | الحد الأقصى |
| unit_cost | Float? | - | تكلفة الوحدة |
| selling_price | Float? | - | سعر البيع |
| location | String? | - | موقع المستودع |
| batch_number | String? | - | رقم الدفعة |
| expiry_date | DateTime? | - | تاريخ الانتهاء |
| min_temperature | Float? | - | الحرارة الدنيا |
| max_temperature | Float? | - | الحرارة القصوى |
| min_humidity | Float? | - | الرطوبة الدنيا |
| max_humidity | Float? | - | الرطوبة القصوى |
| supplier | String? | - | المورد |
| barcode | String? | - | الباركود |
| image_url | String? | - | رابط الصورة |

**العلاقات**: `movements[]`, `alerts[]`

#### inventory_movements | حركات المخزون

| العمود | النوع | المفتاح | ملاحظات |
|--------|-------|---------|---------|
| id | UUID | PK | مُولّد تلقائياً |
| item_id | String | FK | مرجع العنصر |
| tenant_id | String | - | معرف المستأجر |
| type | MovementType | - | PURCHASE, SALE, RETURN, ADJUSTMENT, TRANSFER, WASTE, USAGE, PRODUCTION, RESTOCK |
| quantity | Float | - | الكمية |
| unit_cost | Float? | - | تكلفة الوحدة |
| reference_id | String? | - | مرجع خارجي |
| reference_type | String? | - | purchase_order, sale, waste, adjustment |
| from_location | String? | - | من موقع |
| to_location | String? | - | إلى موقع |
| notes | String? | - | الملاحظات بالإنجليزية |
| notes_ar | String? | - | الملاحظات بالعربية |
| performed_by | String | - | المنفذ |

#### warehouses | المستودعات

| العمود | النوع | المفتاح | ملاحظات |
|--------|-------|---------|---------|
| id | UUID | PK | مُولّد تلقائياً |
| name | String | - | الاسم بالإنجليزية |
| name_ar | String | - | الاسم بالعربية |
| warehouse_type | WarehouseType | - | MAIN, FIELD, COLD, CHEMICAL, SEED, FUEL |
| latitude | Float? | - | خط العرض |
| longitude | Float? | - | خط الطول |
| address | String? | - | العنوان |
| governorate | String? | - | المحافظة |
| capacity_value | Float | - | السعة |
| capacity_unit | String | - | "cubic_meter" افتراضياً |
| current_usage | Float | - | 0 افتراضياً |
| storage_condition | StorageCondition | - | AMBIENT, COOL, COLD, FROZEN, DRY, CONTROLLED |
| temp_min | Float? | - | الحرارة الدنيا |
| temp_max | Float? | - | الحرارة القصوى |
| humidity_min | Float? | - | الرطوبة الدنيا |
| humidity_max | Float? | - | الرطوبة القصوى |
| is_active | Boolean | - | true افتراضياً |
| manager_id | String? | - | معرف المدير |
| manager_name | String? | - | اسم المدير |

**العلاقات**: `zones[]`, `transfersFrom[]`, `transfersTo[]`

---

### 7. Weather Service | خدمة الطقس

**الملف**: `apps/services/weather-service/prisma/schema.prisma`

#### weather_observations | رصدات الطقس

| العمود | النوع | المفتاح | ملاحظات |
|--------|-------|---------|---------|
| id | UUID | PK | مُولّد تلقائياً |
| location_id | String | - | مرجع الموقع |
| tenant_id | String? | - | معرف المستأجر |
| latitude | Float | - | خط العرض |
| longitude | Float | - | خط الطول |
| timestamp | DateTime | - | الوقت |
| temperature | Float | - | الحرارة (سلزيوس) |
| humidity | Float | - | الرطوبة (%) |
| pressure | Float | - | الضغط (hPa) |
| wind_speed | Float | - | سرعة الرياح (m/s) |
| wind_direction | Float | - | اتجاه الرياح (درجات) |
| rainfall | Float? | - | هطول الأمطار (mm) |
| uv_index | Float? | - | مؤشر الأشعة فوق البنفسجية |
| cloud_cover | Float? | - | تغطية السحب (%) |
| visibility | Float? | - | الرؤية (متر) |
| source | String | - | open-meteo, openweathermap, weatherapi |
| raw_data | JSONB? | - | البيانات الخام |

#### weather_forecasts | توقعات الطقس

| العمود | النوع | المفتاح | ملاحظات |
|--------|-------|---------|---------|
| id | UUID | PK | مُولّد تلقائياً |
| location_id | String | - | مرجع الموقع |
| tenant_id | String? | - | معرف المستأجر |
| forecast_for | DateTime | - | التاريخ المتوقع |
| fetched_at | DateTime | - | وقت الجلب |
| provider | String | - | مزود التوقع |
| hourly_data | JSONB | - | توقع 48 ساعة |
| daily_data | JSONB | - | توقع 7-14 يوم |

**القيود**: UNIQUE(location_id, forecast_for, provider)

#### weather_alerts | تنبيهات الطقس

| العمود | النوع | المفتاح | ملاحظات |
|--------|-------|---------|---------|
| id | UUID | PK | مُولّد تلقائياً |
| location_id | String | - | مرجع الموقع |
| tenant_id | String? | - | معرف المستأجر |
| alert_type | AlertType | - | HEAT_STRESS, FROST, HEAVY_RAIN, DROUGHT, STRONG_WIND, STORM, DISEASE_RISK, OTHER |
| severity | AlertSeverity | - | INFO, MINOR, MODERATE, SEVERE, EXTREME |
| headline | String | - | العنوان |
| description | Text | - | الوصف |
| start_time | DateTime | - | وقت البدء |
| end_time | DateTime | - | وقت الانتهاء |
| source | String | - | المصدر |

---

### 8. Research Core Service | خدمة البحث العلمي

**الملف**: `apps/services/research-core/prisma/schema.prisma`

#### experiments | التجارب

| العمود | النوع | المفتاح | ملاحظات |
|--------|-------|---------|---------|
| id | UUID | PK | مُولّد تلقائياً |
| title | String | - | العنوان بالإنجليزية |
| title_ar | String? | - | العنوان بالعربية |
| description | Text? | - | الوصف بالإنجليزية |
| description_ar | Text? | - | الوصف بالعربية |
| hypothesis | Text? | - | الفرضية بالإنجليزية |
| hypothesis_ar | Text? | - | الفرضية بالعربية |
| start_date | Date | - | تاريخ البدء |
| end_date | Date? | - | تاريخ الانتهاء |
| status | ExperimentStatus | - | draft, active, locked, completed, archived |
| locked_at | DateTime? | - | وقت القفل |
| locked_by | String? | - | من قفل |
| principal_researcher_id | String | - | الباحث الرئيسي |
| organization_id | String? | - | المنظمة |
| farm_id | String? | - | المزرعة |
| metadata | JSONB? | - | بيانات إضافية |
| tags | String[]? | - | الوسوم |
| version | Int | - | 1 افتراضياً |

**العلاقات**: `protocols[]`, `plots[]`, `treatments[]`, `logs[]`, `samples[]`, `collaborators[]`, `auditLogs[]`, `plantings[]`

#### germplasm | الأصول الوراثية

| العمود | النوع | المفتاح | ملاحظات |
|--------|-------|---------|---------|
| id | UUID | PK | مُولّد تلقائياً |
| accession_number | String | UNIQUE | رقم الانضمام |
| common_name | String | - | الاسم الشائع بالإنجليزية |
| common_name_ar | String? | - | الاسم الشائع بالعربية |
| scientific_name | String? | - | الاسم العلمي |
| genus | String? | - | الجنس |
| species | String? | - | النوع |
| subspecies | String? | - | تحت النوع |
| cultivar | String? | - | الصنف |
| variety | String? | - | الصنف الفرعي |
| pedigree | Text? | - | سلسلة النسب |
| type | GermplasmType | - | seed, cutting, tissue, pollen, other |
| country_of_origin | String? | - | بلد المنشأ |
| region_of_origin | String? | - | منطقة المنشأ |
| collection_site | String? | - | موقع الجمع |
| collection_date | Date? | - | تاريخ الجمع |
| collected_by | String? | - | من جمع |
| donor_institution | String? | - | المؤسسة المانحة |
| donor_accession_number | String? | - | رقم انضمام المانح |
| growth_habit | String? | - | عادة النمو |
| maturity_days | Int? | - | أيام النضج |
| yield_potential | String? | - | إمكانية الإنتاجية |
| drought_tolerance | String? | - | تحمل الجفاف |
| disease_resistance | JSONB | - | {} افتراضياً |
| pest_resistance | JSONB | - | {} افتراضياً |
| quality_traits | JSONB | - | {} افتراضياً |
| storage_location | String? | - | موقع التخزين |
| storage_conditions | String? | - | ظروف التخزين |
| storage_temperature | Decimal(5,2)? | - | حرارة التخزين |
| storage_humidity | Decimal(5,2)? | - | رطوبة التخزين |
| is_available | Boolean | - | true افتراضياً |
| quantity_available | Decimal(10,3)? | - | الكمية المتاحة |
| quantity_unit | String? | - | وحدة الكمية |
| photos | String[] | - | [] افتراضياً |
| documents | String[] | - | [] افتراضياً |
| metadata | JSONB | - | {} افتراضياً |

**العلاقات**: `seedLots[]`, `plantings[]`

#### seed_lots | دفعات البذور

| العمود | النوع | المفتاح | ملاحظات |
|--------|-------|---------|---------|
| id | UUID | PK | مُولّد تلقائياً |
| germplasm_id | String | FK | مرجع الأصل الوراثي |
| lot_number | String | UNIQUE | رقم الدفعة |
| initial_quantity | Decimal(10,3) | - | الكمية الأولية |
| current_quantity | Decimal(10,3) | - | الكمية الحالية |
| quantity_unit | String | - | وحدة الكمية |
| seed_count | Int? | - | عدد البذور |
| thousand_seed_weight | Decimal(8,3)? | - | وزن 1000 بذرة |
| quality_grade | SeedQualityGrade | - | certified, foundation, registered, breeder, commercial, farmer_saved |
| germination_rate | Decimal(5,2)? | - | معدل الإنبات |
| germination_test_date | Date? | - | تاريخ اختبار الإنبات |
| purity_percentage | Decimal(5,2)? | - | نسبة النقاء |
| moisture_content | Decimal(5,2)? | - | محتوى الرطوبة |
| vigor_index | Decimal(5,2)? | - | مؤشر الحيوية |
| production_date | Date? | - | تاريخ الإنتاج |
| harvest_date | Date? | - | تاريخ الحصاد |
| production_location | String? | - | موقع الإنتاج |
| production_season | String? | - | موسم الإنتاج |
| produced_by | String? | - | المنتج |
| certification_number | String? | - | رقم الشهادة |
| certified_by | String? | - | المُعتمِد |
| certification_date | Date? | - | تاريخ الاعتماد |
| expiry_date | Date? | - | تاريخ الانتهاء |
| is_treated | Boolean | - | false افتراضياً |
| treatment_type | String? | - | نوع المعالجة |
| treatment_product | String? | - | منتج المعالجة |
| treatment_date | Date? | - | تاريخ المعالجة |
| storage_location | String? | - | موقع التخزين |
| storage_conditions | String? | - | ظروف التخزين |
| photos | String[] | - | [] افتراضياً |
| documents | String[] | - | [] افتراضياً |
| metadata | JSONB | - | {} افتراضياً |

#### research_daily_logs | السجلات اليومية

| العمود | النوع | المفتاح | ملاحظات |
|--------|-------|---------|---------|
| id | UUID | PK | مُولّد تلقائياً |
| experiment_id | String | FK | مرجع التجربة |
| plot_id | String? | FK | مرجع القطعة |
| treatment_id | String? | FK | مرجع المعالجة |
| log_date | Date | - | تاريخ السجل |
| log_time | String? | - | HH:MM |
| category | LogCategory | - | observation, measurement, treatment, harvest, weather, pest, planting, germination, other |
| title | String | - | العنوان بالإنجليزية |
| title_ar | String? | - | العنوان بالعربية |
| notes | Text? | - | الملاحظات بالإنجليزية |
| notes_ar | Text? | - | الملاحظات بالعربية |
| measurements | JSONB | - | {} افتراضياً |
| weather_conditions | JSONB | - | {} افتراضياً |
| photos | String[] | - | [] افتراضياً |
| attachments | String[] | - | [] افتراضياً |
| recorded_by | String | - | المسجل |
| device_id | String? | - | معرف الجهاز |
| offline_id | String? | UNIQUE | معرف للعمل بدون اتصال |
| hash | String? | - | للتحقق |
| synced_at | DateTime? | - | وقت المزامنة |

---

## خدمات SQLAlchemy | SQLAlchemy Services

### 9. Alert Service | خدمة التنبيهات

**الملف**: `apps/services/alert-service/src/db_models.py`

#### alerts | التنبيهات

| العمود | النوع | المفتاح | ملاحظات |
|--------|-------|---------|---------|
| id | UUID | PK | مُولّد تلقائياً |
| tenant_id | UUID? | - | معرف المستأجر |
| field_id | String | - | مرجع الحقل |
| type | String(40) | - | نوع التنبيه |
| severity | String(20) | - | الشدة |
| status | String | - | active, acknowledged, dismissed, resolved, expired |
| title | String | - | العنوان بالعربية |
| title_en | String? | - | العنوان بالإنجليزية |
| message | Text | - | الرسالة بالعربية |
| message_en | Text? | - | الرسالة بالإنجليزية |
| recommendations | JSONB? | - | التوصيات (مصفوفة) |
| recommendations_en | JSONB? | - | التوصيات بالإنجليزية |
| extra_metadata | JSONB? | - | بيانات إضافية |
| source_service | String(80)? | - | الخدمة المصدر |
| correlation_id | String(100)? | - | معرف الارتباط |
| expires_at | DateTime? | - | تاريخ الانتهاء |
| acknowledged_at | DateTime? | - | وقت الإقرار |
| acknowledged_by | String? | - | من أقرّ |
| dismissed_at | DateTime? | - | وقت الرفض |
| dismissed_by | String? | - | من رفض |
| resolved_at | DateTime? | - | وقت الحل |
| resolved_by | String? | - | من حل |
| resolution_note | Text? | - | ملاحظة الحل |

#### alert_rules | قواعد التنبيه

| العمود | النوع | المفتاح | ملاحظات |
|--------|-------|---------|---------|
| id | UUID | PK | مُولّد تلقائياً |
| tenant_id | UUID? | - | معرف المستأجر |
| field_id | String | - | مرجع الحقل |
| name | String | - | اسم القاعدة بالعربية |
| name_en | String? | - | اسم القاعدة بالإنجليزية |
| enabled | Boolean | - | هل القاعدة مفعلة |
| condition | JSONB | - | {metric, operator, value, duration_minutes} |
| alert_config | JSONB | - | {type, severity, title, message_template} |
| cooldown_hours | Int | - | ساعات الانتظار |
| last_triggered_at | DateTime? | - | آخر تفعيل |

---

### 10. Billing Core Service | خدمة الفوترة

**الملف**: `apps/services/billing-core/src/models.py`

#### plans | الخطط

| العمود | النوع | المفتاح | ملاحظات |
|--------|-------|---------|---------|
| id | UUID | PK | مُولّد تلقائياً |
| plan_id | String | UNIQUE | معرف الخطة |
| name | String | - | الاسم بالإنجليزية |
| name_ar | String | - | الاسم بالعربية |
| description | Text | - | الوصف بالإنجليزية |
| description_ar | Text | - | الوصف بالعربية |
| tier | PlanTier | - | free, starter, professional, enterprise |
| pricing | JSONB | - | monthly_usd, quarterly_usd, yearly_usd, setup_fee_usd |
| features | JSONB | - | الميزات |
| limits | JSONB | - | الحدود |
| is_active | Boolean | - | true افتراضياً |
| trial_days | Int | - | 14 افتراضياً |

#### tenants | المستأجرون

| العمود | النوع | المفتاح | ملاحظات |
|--------|-------|---------|---------|
| id | UUID | PK | مُولّد تلقائياً |
| tenant_id | String | UNIQUE | معرف المستأجر الخارجي |
| name | String | - | الاسم بالإنجليزية |
| name_ar | String | - | الاسم بالعربية |
| contact | JSONB | - | {name, email, phone, address} |
| tax_id | String? | - | الرقم الضريبي |
| is_active | Boolean | - | true افتراضياً |
| metadata | JSONB? | - | بيانات إضافية |

#### subscriptions | الاشتراكات

| العمود | النوع | المفتاح | ملاحظات |
|--------|-------|---------|---------|
| id | UUID | PK | مُولّد تلقائياً |
| tenant_id | String | - | مرجع المستأجر |
| plan_id | String | - | مرجع الخطة |
| status | SubscriptionStatus | - | active, trial, past_due, canceled, suspended, expired |
| billing_cycle | BillingCycle | - | monthly, quarterly, yearly |
| currency | Currency | - | USD, YER |
| start_date | Date | - | تاريخ البدء |
| end_date | Date | - | تاريخ الانتهاء |
| trial_end_date | Date? | - | نهاية الفترة التجريبية |
| canceled_at | DateTime? | - | وقت الإلغاء |
| next_billing_date | Date | - | تاريخ الفوترة التالي |
| last_billing_date | Date? | - | آخر فوترة |
| payment_method | PaymentMethod? | - | طريقة الدفع |
| stripe_subscription_id | String? | - | مرجع Stripe |
| metadata | JSONB? | - | بيانات إضافية |

**العلاقات**: `invoices[]`, `usage_records[]`

#### invoices | الفواتير

| العمود | النوع | المفتاح | ملاحظات |
|--------|-------|---------|---------|
| id | UUID | PK | مُولّد تلقائياً |
| invoice_number | String | UNIQUE | رقم الفاتورة |
| tenant_id | String | - | مرجع المستأجر |
| subscription_id | UUID | FK | مرجع الاشتراك |
| status | InvoiceStatus | - | draft, pending, paid, overdue, canceled, refunded |
| currency | Currency | - | USD, YER |
| issue_date | Date | - | تاريخ الإصدار |
| due_date | Date | - | تاريخ الاستحقاق |
| paid_date | Date? | - | تاريخ الدفع |
| subtotal | Numeric(12,2) | - | المجموع الفرعي |
| tax_rate | Numeric(5,2) | - | 0 افتراضياً |
| tax_amount | Numeric(12,2) | - | 0 افتراضياً |
| discount_amount | Numeric(12,2) | - | 0 افتراضياً |
| total | Numeric(12,2) | - | الإجمالي |
| amount_paid | Numeric(12,2) | - | 0 افتراضياً |
| amount_due | Numeric(12,2) | - | المستحق |
| line_items | JSONB | - | بنود الفاتورة |
| notes | Text? | - | ملاحظات بالإنجليزية |
| notes_ar | Text? | - | ملاحظات بالعربية |
| stripe_invoice_id | String? | - | مرجع Stripe |

**العلاقات**: `subscription`, `payments[]`

#### payments | المدفوعات

| العمود | النوع | المفتاح | ملاحظات |
|--------|-------|---------|---------|
| id | UUID | PK | مُولّد تلقائياً |
| invoice_id | UUID | FK | مرجع الفاتورة |
| tenant_id | String | - | مرجع المستأجر |
| amount | Numeric(12,2) | - | المبلغ |
| currency | Currency | - | USD, YER |
| status | PaymentStatus | - | pending, processing, succeeded, failed, refunded |
| method | PaymentMethod | - | credit_card, bank_transfer, mobile_money, cash, tharwatt |
| paid_at | DateTime? | - | وقت الدفع |
| processed_at | DateTime? | - | وقت المعالجة |
| failure_reason | Text? | - | سبب الفشل |
| stripe_payment_id | String? | - | مرجع Stripe |
| tharwatt_transaction_id | String? | - | مرجع Tharwatt |
| receipt_url | String? | - | رابط الإيصال |
| metadata | JSONB? | - | بيانات إضافية |

#### usage_records | سجلات الاستخدام

| العمود | النوع | المفتاح | ملاحظات |
|--------|-------|---------|---------|
| id | UUID | PK | مُولّد تلقائياً |
| subscription_id | UUID | FK | مرجع الاشتراك |
| tenant_id | String | - | مرجع المستأجر |
| metric_type | String | - | satellite_analyses, api_calls |
| quantity | Int | - | 1 افتراضياً |
| recorded_at | DateTime | - | وقت التسجيل |
| metadata | JSONB? | - | {resource_id, user_id} |

---

### 11. Equipment Service | خدمة المعدات

**الملف**: `apps/services/equipment-service/src/db_models.py`

#### equipment | المعدات

| العمود | النوع | المفتاح | ملاحظات |
|--------|-------|---------|---------|
| equipment_id | String | PK | معرف المعدة |
| tenant_id | String | - | معرف المستأجر |
| name | String | - | الاسم بالإنجليزية |
| name_ar | String? | - | الاسم بالعربية |
| equipment_type | String | - | tractor, pump, drone, harvester, sprayer, pivot, sensor, vehicle, other |
| status | String | - | operational, maintenance, inactive, repair |
| brand | String? | - | العلامة التجارية |
| model | String? | - | الموديل |
| serial_number | String? | UNIQUE | الرقم التسلسلي |
| year | Int? | - | سنة الصنع |
| purchase_date | DateTime? | - | تاريخ الشراء |
| purchase_price | Numeric(12,2)? | - | سعر الشراء |
| field_id | String? | - | مرجع الحقل |
| location_name | String? | - | اسم الموقع |
| horsepower | Int? | - | القوة الحصانية |
| fuel_capacity_liters | Numeric(8,2)? | - | سعة الوقود |
| current_fuel_percent | Numeric(5,2)? | - | نسبة الوقود الحالية |
| current_hours | Numeric(10,2)? | - | ساعات التشغيل الحالية |
| current_lat | Numeric(10,7)? | - | خط العرض الحالي |
| current_lon | Numeric(10,7)? | - | خط الطول الحالي |
| last_maintenance_at | DateTime? | - | آخر صيانة |
| next_maintenance_at | DateTime? | - | الصيانة التالية |
| next_maintenance_hours | Numeric(10,2)? | - | ساعات الصيانة التالية |
| qr_code | String? | UNIQUE | رمز QR |
| metadata | JSONB? | - | بيانات إضافية |

#### equipment_maintenance | صيانة المعدات

| العمود | النوع | المفتاح | ملاحظات |
|--------|-------|---------|---------|
| record_id | String | PK | معرف السجل |
| equipment_id | String | - | مرجع المعدة |
| maintenance_type | String | - | oil_change, filter_change, tire_check, battery_check, calibration, general_service, repair, other |
| description | Text | - | الوصف بالإنجليزية |
| description_ar | Text? | - | الوصف بالعربية |
| performed_by | String? | - | المنفذ |
| performed_at | DateTime | - | وقت التنفيذ |
| cost | Numeric(10,2)? | - | التكلفة |
| notes | Text? | - | ملاحظات |
| parts_replaced | String[]? | - | القطع المستبدلة |

#### equipment_alerts | تنبيهات المعدات

| العمود | النوع | المفتاح | ملاحظات |
|--------|-------|---------|---------|
| alert_id | String | PK | معرف التنبيه |
| equipment_id | String | - | مرجع المعدة |
| equipment_name | String | - | اسم المعدة |
| maintenance_type | String | - | نوع الصيانة المطلوبة |
| description | Text | - | الوصف بالإنجليزية |
| description_ar | Text? | - | الوصف بالعربية |
| priority | String | - | low, medium, high, critical |
| due_at | DateTime? | - | تاريخ الاستحقاق |
| due_hours | Numeric(10,2)? | - | ساعات الاستحقاق |
| is_overdue | Boolean | - | false افتراضياً |

---

## خدمات Tortoise ORM | Tortoise ORM Services

### 12. Notification Service | خدمة الإشعارات

**الملف**: `apps/services/notification-service/src/models.py`

#### notifications | الإشعارات

| العمود | النوع | المفتاح | ملاحظات |
|--------|-------|---------|---------|
| id | UUID | PK | مُولّد تلقائياً |
| tenant_id | String(100)? | - | معرف المستأجر |
| user_id | String(100) | - | معرف المستخدم |
| title | String | - | العنوان بالإنجليزية |
| title_ar | String? | - | العنوان بالعربية |
| body | Text | - | المحتوى بالإنجليزية |
| body_ar | Text? | - | المحتوى بالعربية |
| type | String(50) | - | weather_alert, pest_outbreak, irrigation_reminder |
| priority | String | - | low, medium, high, critical |
| channel | String | - | push, sms, in_app, email |
| status | String | - | pending, sent, failed, read |
| sent_at | DateTime? | - | وقت الإرسال |
| read_at | DateTime? | - | وقت القراءة |
| data | JSON? | - | بيانات إضافية |
| action_url | String? | - | رابط الإجراء |
| target_governorates | JSON? | - | المحافظات المستهدفة |
| target_crops | JSON? | - | المحاصيل المستهدفة |
| expires_at | DateTime? | - | تاريخ الانتهاء |

#### notification_templates | قوالب الإشعارات

| العمود | النوع | المفتاح | ملاحظات |
|--------|-------|---------|---------|
| id | UUID | PK | مُولّد تلقائياً |
| tenant_id | String? | - | معرف المستأجر |
| name | String | UNIQUE | اسم/رمز القالب |
| description | String? | - | الوصف |
| title_template | String | - | قالب العنوان مع {{variables}} |
| title_template_ar | String? | - | قالب العنوان بالعربية |
| body_template | Text | - | قالب المحتوى مع {{variables}} |
| body_template_ar | Text? | - | قالب المحتوى بالعربية |
| type | String | - | نوع الإشعار الافتراضي |
| priority | String | - | medium افتراضياً |
| channel | String | - | in_app افتراضياً |
| variables | JSON? | - | المتغيرات المتاحة |
| default_data | JSON? | - | البيانات الافتراضية |
| is_active | Boolean | - | true افتراضياً |

#### notification_channels | قنوات الإشعارات

| العمود | النوع | المفتاح | ملاحظات |
|--------|-------|---------|---------|
| id | UUID | PK | مُولّد تلقائياً |
| tenant_id | String? | - | معرف المستأجر |
| user_id | String | - | معرف المستخدم |
| channel | ChannelType | - | EMAIL, SMS, PUSH, WHATSAPP, IN_APP |
| address | String | - | البريد، الهاتف، توكن FCM |
| verified | Boolean | - | false افتراضياً |
| verified_at | DateTime? | - | وقت التحقق |
| verification_code | String? | - | رمز التحقق |
| enabled | Boolean | - | true افتراضياً |
| metadata | JSON? | - | بيانات إضافية |

**القيود**: UNIQUE(user_id, channel, address)

#### notification_preferences | تفضيلات الإشعارات

| العمود | النوع | المفتاح | ملاحظات |
|--------|-------|---------|---------|
| id | UUID | PK | مُولّد تلقائياً |
| tenant_id | String? | - | معرف المستأجر |
| user_id | String | - | معرف المستخدم |
| event_type | String | - | weather_alert, pest_outbreak, etc. |
| channels | JSON | - | ['email', 'sms', 'push'] |
| enabled | Boolean | - | true افتراضياً |
| quiet_hours_start | Time? | - | مثال: 22:00 |
| quiet_hours_end | Time? | - | مثال: 06:00 |
| metadata | JSON? | - | بيانات إضافية |

**القيود**: UNIQUE(user_id, event_type)

#### farmer_profiles | ملفات المزارعين

| العمود | النوع | المفتاح | ملاحظات |
|--------|-------|---------|---------|
| id | UUID | PK | مُولّد تلقائياً |
| tenant_id | String? | - | معرف المستأجر |
| farmer_id | String | UNIQUE | معرف المزارع |
| name | String | - | الاسم بالإنجليزية |
| name_ar | String? | - | الاسم بالعربية |
| governorate | String | - | المحافظة |
| district | String? | - | المديرية |
| phone | String? | - | للرسائل القصيرة/واتساب |
| email | String? | - | البريد الإلكتروني |
| fcm_token | String? | - | توكن Firebase |
| language | String | - | "ar" افتراضياً (ar, en) |
| is_active | Boolean | - | true افتراضياً |
| metadata | JSON? | - | بيانات إضافية |
| last_login_at | DateTime? | - | آخر تسجيل دخول |

#### farmer_crops | محاصيل المزارعين

| العمود | النوع | المفتاح | ملاحظات |
|--------|-------|---------|---------|
| id | UUID | PK | مُولّد تلقائياً |
| farmer_id | UUID | FK | مرجع المزارع |
| crop_type | String | - | tomato, wheat, coffee, etc. |
| area_hectares | Float? | - | المساحة |
| planting_date | Date? | - | تاريخ الزراعة |
| harvest_date | Date? | - | تاريخ الحصاد |
| is_active | Boolean | - | true افتراضياً |

**القيود**: UNIQUE(farmer_id, crop_type)

#### farmer_fields | حقول المزارعين

| العمود | النوع | المفتاح | ملاحظات |
|--------|-------|---------|---------|
| id | UUID | PK | مُولّد تلقائياً |
| farmer_id | UUID | FK | مرجع المزارع |
| field_id | String | - | معرف الحقل |
| field_name | String? | - | اسم/تسمية الحقل |
| latitude | Float? | - | خط العرض |
| longitude | Float? | - | خط الطول |
| is_active | Boolean | - | true افتراضياً |

**القيود**: UNIQUE(farmer_id, field_id)

---

## العلاقات الرئيسية | Key Relationships

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Entity Relationship Diagram                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────┐      ┌─────────┐      ┌─────────┐                             │
│  │  Users  │──1:N─│Sessions │      │ Wallets │──1:N─┌───────────────┐      │
│  └────┬────┘      └─────────┘      └────┬────┘      │  Transactions │      │
│       │                                  │          └───────────────┘      │
│       │ 1:N                              │ 1:N                              │
│       ▼                                  ▼                                  │
│  ┌─────────┐                        ┌─────────┐                             │
│  │ Fields  │──1:N─┌─────────┐       │  Loans  │                             │
│  └────┬────┘      │  Tasks  │       └─────────┘                             │
│       │           └─────────┘                                               │
│       │ 1:N                                                                 │
│       ▼                                                                     │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐                │
│  │ NDVI Readings│     │   Products   │──1:N│ Order Items  │                │
│  └──────────────┘     └──────────────┘     └──────────────┘                │
│                                                     │                       │
│                                                     │ N:1                   │
│                                                     ▼                       │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐                │
│  │   Devices    │──1:N│   Sensors    │     │    Orders    │                │
│  └──────────────┘     └──────────────┘     └──────────────┘                │
│         │                    │                                              │
│         │ 1:N                │ 1:N                                          │
│         ▼                    ▼                                              │
│  ┌──────────────┐     ┌──────────────┐                                     │
│  │  Actuators   │     │   Readings   │                                     │
│  └──────────────┘     └──────────────┘                                     │
│                                                                             │
│  ┌───────────────┐     ┌───────────────┐     ┌───────────────┐             │
│  │  Experiments  │──1:N│     Plots     │──1:N│  Daily Logs   │             │
│  └───────┬───────┘     └───────────────┘     └───────────────┘             │
│          │                                                                  │
│          │ 1:N                                                              │
│          ▼                                                                  │
│  ┌───────────────┐     ┌───────────────┐                                   │
│  │   Germplasm   │──1:N│   Seed Lots   │                                   │
│  └───────────────┘     └───────────────┘                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## ملخص الإحصائيات | Statistics Summary

### إجمالي الجداول | Total Tables

| التقنية | Technology | الجداول | Tables |
|---------|------------|---------|--------|
| Prisma ORM | Node.js | 45+ | جداول |
| SQLAlchemy | Python | 12+ | جداول |
| Tortoise ORM | Python | 6+ | جداول |
| **الإجمالي** | **Total** | **60+** | **جداول** |

### الخدمات حسب ORM | Services by ORM

| ORM | الخدمات |
|-----|---------|
| Prisma | user-service, field-management, marketplace, chat, iot, inventory, weather, research |
| SQLAlchemy | alert-service, billing-core, equipment-service, task-service |
| Tortoise | notification-service |

### أنواع البيانات الشائعة | Common Data Types

| النوع | الاستخدام |
|-------|-----------|
| UUID | المفاتيح الأساسية |
| JSONB | البيانات المرنة (metadata, features) |
| Geometry | PostGIS (Point, Polygon) |
| Numeric/Decimal | القيم المالية والإحداثيات |
| Enum | الحالات والأنواع |
| DateTime(TZ) | الطوابع الزمنية مع timezone |

### الفهارس الشائعة | Common Indexes

| النوع | الغرض |
|-------|-------|
| tenant_id | عزل البيانات متعدد المستأجرين |
| status + created_at | فلترة الحالة والترتيب |
| user_id | البحث بالمستخدم |
| field_id | ربط بيانات الحقول |
| timestamp DESC | ترتيب تنازلي بالوقت |

---

## المراجع | References

- [Kong Backend API Mapping](./kong-backend-services-api-mapping.md)
- [CLAUDE.md](../CLAUDE.md) - Project Guidelines
- [Prisma Schema Files](../apps/services/*/prisma/schema.prisma)
- [SQLAlchemy Models](../apps/services/*/src/models.py)

---

> **آخر تحديث**: 2026-01-24
> **الإصدار**: 16.0.0
> **المسؤول**: KAFAAT Development Team
