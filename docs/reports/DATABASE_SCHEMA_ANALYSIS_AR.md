# تحليل شامل لمخططات قواعد البيانات والهجرات

## منصة سهول الموحدة v15 IDP

**تاريخ التحليل:** 2025-12-24
**نطاق التحليل:** جميع مخططات قواعد البيانات، الهجرات، ونماذج ORM

---

## 1. نظرة عامة على البنية المعمارية لقاعدة البيانات

### 1.1 تقنيات ORM المستخدمة

تستخدم المنصة **أربع تقنيات ORM مختلفة** في وقت واحد:

1. **Prisma** (TypeScript/Node.js)
   - خدمة Field Core: `/apps/services/field-core/prisma/schema.prisma`
   - خدمة Research Core: `/apps/services/research-core/prisma/schema.prisma`
   - خدمة Marketplace: `/apps/services/marketplace-service/prisma/schema.prisma`

2. **Tortoise ORM** (Python)
   - خدمة Field Chat: `/apps/services/field-chat/src/models.py`

3. **SQLAlchemy** (Python)
   - محرك NDVI: `/apps/services/ndvi-engine/src/models.py`
   - Field Suite: `/packages/field_suite/spatial/orm_models.py`
   - نظام Outbox: `/shared/libs/outbox/models.py`
   - نظام المراجعة: `/shared/libs/audit/models.py`

4. **SQL الخام** (Raw SQL)
   - هجرات PostgreSQL: `/infra/postgres/migrations/`
   - نصوص التهيئة: `/infra/postgres/init/`

### 1.2 الجداول الرئيسية المكتشفة

تم التعرف على **70+ جدول** عبر المنصة:

#### الجداول الأساسية (Core Tables):

- `tenants` - المستأجرين/المنظمات
- `users` - المستخدمين
- `fields` - الحقول الزراعية ⚠️ **تعارض**
- `farms` - المزارع
- `crops` - المحاصيل

#### جداول البحث العلمي (Research):

- `experiments` - التجارب
- `research_protocols` - البروتوكولات
- `research_plots` - قطع التجارب
- `treatments` - المعاملات
- `research_daily_logs` - السجلات اليومية
- `lab_samples` - العينات المختبرية
- `digital_signatures` - التوقيعات الرقمية

#### جداول NDVI والأقمار الصناعية:

- `ndvi_observations` - مشاهدات NDVI
- `ndvi_alerts` - تنبيهات NDVI
- `ndvi_records` - سجلات NDVI ⚠️ **تعارض مع ndvi_readings**
- `ndvi_readings` - قراءات NDVI ⚠️ **تعارض**

#### جداول السوق (Marketplace):

- `products` - المنتجات
- `orders` - الطلبات
- `order_items` - عناصر الطلب
- `wallets` - المحافظ المالية
- `transactions` - المعاملات المالية
- `loans` - القروض

#### جداول المحادثات (Chat):

- `chat_threads` - خيوط المحادثات
- `chat_messages` - الرسائل
- `chat_participants` - المشاركون
- `chat_attachments` - المرفقات

#### جداول IoT:

- `iot_devices` - أجهزة إنترنت الأشياء
- `iot_readings` - قراءات المستشعرات

#### جداول المهام والتنبيهات:

- `tasks` - المهام ⚠️ **تعارض**
- `alerts` - التنبيهات
- `notification_log` - سجل الإشعارات

#### جداول الطقس:

- `weather_records` - سجلات الطقس
- `weather_forecasts` - توقعات الطقس

#### جداول الأنواء:

- `anwa_events` - أحداث الأنواء

#### جداول المزامنة والتدقيق:

- `sync_status` - حالة المزامنة ⚠️ **تعارض**
- `audit_logs` - سجلات التدقيق ⚠️ **تعارض**
- `outbox_events` - أحداث Outbox Pattern

---

## 2. التعارضات المكتشفة (Conflicts)

### ⚠️ 2.1 تعارضات أسماء الجداول

تم اكتشاف **تعارضات خطيرة** بين الخدمات المختلفة:

#### 🔴 **تعارض حرج: جدول `fields`**

- **الموقع 1:** `/infra/postgres/init/00-init-sahool.sql` (SQL الخام)
- **الموقع 2:** Field Core Prisma (`/apps/services/field-core/prisma/schema.prisma`)
- **الموقع 3:** Field Suite SQLAlchemy (`/packages/field_suite/spatial/orm_models.py`)

**المشكلة:**

- نفس اسم الجدول `fields` معرف في 3 أماكن مختلفة
- احتمال تضارب في البنية (Schema Collision)
- مخططات مختلفة للأعمدة قد تؤدي إلى فشل في التهيئة

**التأثير:** 🔥 **حرج - يمنع بدء الخدمات**

---

#### 🔴 **تعارض: جدول `tasks`**

- **الموقع 1:** `/infra/postgres/init/00-init-sahool.sql`
- **الموقع 2:** Field Core Prisma

**المشكلة:**

- تعريف مزدوج لجدول المهام
- احتمال اختلاف في الأعمدة والقيود

**التأثير:** 🔥 **حرج**

---

#### 🟡 **تعارض: جدول `ndvi_readings`**

- **الموقع 1:** `/infra/postgres/init/00-init-sahool.sql`
- **الموقع 2:** Field Core Prisma

**ملاحظة:** يوجد أيضاً جدول `ndvi_observations` في محرك NDVI - غير واضح إذا كان مقصوداً أن يكونا جدولين منفصلين

**التأثير:** 🟡 **متوسط**

---

#### 🟡 **تعارض: جدول `sync_status`**

- **الموقع 1:** `/infra/postgres/init/00-init-sahool.sql`
- **الموقع 2:** Field Core Prisma

**التأثير:** 🟡 **متوسط**

---

#### 🟡 **تعارض: جدول `field_boundary_history`**

- **الموقع 1:** `/infra/postgres/init/00-init-sahool.sql`
- **الموقع 2:** Field Core Prisma

**التأثير:** 🟡 **متوسط**

---

#### 🟡 **تعارض: جدول `audit_logs`**

- **الموقع 1:** `/infra/postgres/init/00-init-sahool.sql`
- **الموقع 2:** Audit SQLAlchemy (`/shared/libs/audit/models.py`)

**المشكلة:**

- بنية مختلفة للأعمدة
- الجدول في SQL الخام لا يحتوي على hash chain
- الجدول في SQLAlchemy يحتوي على `prev_hash` و `entry_hash` للحماية من التلاعب

**التأثير:** 🟡 **متوسط - قد يؤدي إلى فقدان ميزة الأمان**

---

#### 🟢 **تعارض محتمل: جدول `farms`**

- **الموقع 1:** `/infra/postgres/migrations/002_base_tables.sql` (في schema `geo.farms`)
- **الموقع 2:** Field Suite SQLAlchemy (في schema `public.farms`)

**ملاحظة:** قد لا يكون تعارضاً حقيقياً إذا كانا في schemas مختلفة

**التأثير:** 🟢 **منخفض - إذا كانت الـschemas منفصلة**

---

#### 🟡 **تكرار كامل للجداول البحثية**

الجداول التالية **معرفة مرتين** تماماً:

- `experiments`
- `research_protocols`
- `research_plots`
- `treatments`
- `research_daily_logs`
- `lab_samples`
- `digital_signatures`
- `experiment_collaborators`
- `experiment_audit_log`

**الموقع 1:** `/infra/postgres/init/00-init-sahool.sql`
**الموقع 2:** Research Core Prisma

**التأثير:** 🟡 **متوسط - تكرار غير ضروري**

---

#### 🟡 **تكرار كامل لجداول السوق**

- `products`
- `orders`
- `order_items`
- `wallets`
- `transactions`
- `loans`

**الموقع 1:** `/infra/postgres/init/00-init-sahool.sql`
**الموقع 2:** Marketplace Prisma

**التأثير:** 🟡 **متوسط**

---

#### 🟡 **تكرار كامل لجداول المحادثات**

- `chat_threads`
- `chat_messages`
- `chat_participants`
- `chat_attachments`

**الموقع 1:** `/infra/postgres/init/00-init-sahool.sql`
**الموقع 2:** Field Chat Tortoise ORM

**التأثير:** 🟡 **متوسط**

---

## 3. مراجع المفاتيح الأجنبية عبر حدود الخدمات (Anti-Pattern)

### 🔴 3.1 انتهاكات مبادئ الـMicroservices

تم اكتشاف **مراجع مباشرة** بين الخدمات تنتهك مبدأ Database-per-Service:

#### **Field Core → Users Service**

```prisma
// في Field Core Prisma
field_id UUID REFERENCES fields(id)
owner_id UUID  // يشير إلى users من خدمة أخرى بدون foreign key
```

**المشكلة:** غياب FK صريح ولكن المنطق يعتمد على وجود المستخدمين في خدمة منفصلة

---

#### **Research Core → Fields/Farms**

```prisma
// في Research Core
farmId String? @map("farm_id")  // لا توجد relation معرفة
```

**المشكلة:** المزارع موجودة في خدمة Fields، لكن يتم الإشارة إليها من خدمة Research

---

#### **Marketplace → Users**

```prisma
// في Marketplace
sellerId String @map("seller_id")  // يشير إلى users
buyerId  String @map("buyer_id")   // يشير إلى users
```

**المشكلة:** الاعتماد على جدول users من خدمة مختلفة

---

#### **Tasks → Fields**

```sql
-- في جدول tasks
field_id UUID REFERENCES fields(id) ON DELETE SET NULL
```

**المشكلة:** إذا كانت Tasks في خدمة منفصلة عن Fields، هذا يخالف مبدأ العزل

---

### 🟡 3.2 استخدام Tenant ID كمفتاح مشترك

**الإيجابيات:**
✅ جميع الجداول تحتوي على `tenant_id` للتمييز بين المستأجرين
✅ يسمح بالعزل المنطقي (Logical Isolation)

**السلبيات:**
⚠️ **عدم اتساق في نوع البيانات:**

- بعض الجداول: `tenant_id UUID`
- بعض الجداول: `tenant_id VARCHAR(100)`

**التأثير:** 🟡 قد يسبب مشاكل في الـJOINs ومقارنة البيانات

---

## 4. الفهارس المفقودة (Missing Indexes)

### 🔴 4.1 فهارس حرجة مفقودة

#### **جدول `ndvi_observations`**

```sql
✅ موجود: INDEX ix_ndvi_field_date (field_id, obs_date)
✅ موجود: INDEX ix_ndvi_tenant_date (tenant_id, obs_date)
✅ موجود: UNIQUE INDEX uq_ndvi_field_date_source
```

**الحالة:** ✅ جيدة

---

#### **جدول `chat_messages`**

```sql
✅ موجود: INDEX idx_messages_thread (thread_id, created_at)
❌ مفقود: INDEX على sender_id منفرداً (للاستعلام عن رسائل المستخدم)
```

**التوصية:**

```sql
CREATE INDEX idx_chat_messages_sender ON chat_messages(sender_id, created_at);
```

---

#### **جدول `transactions`**

```sql
✅ موجود: INDEX idx_transactions_wallet
❌ مفقود: INDEX على (wallet_id, created_at) للاستعلامات الزمنية
❌ مفقود: INDEX على reference_id للبحث السريع
```

**التوصية:**

```sql
CREATE INDEX idx_transactions_wallet_date ON transactions(wallet_id, created_at);
CREATE INDEX idx_transactions_reference ON transactions(reference_id);
```

---

#### **جدول `research_data_points`**

```sql
✅ موجود: INDEX idx_data_points_experiment
✅ موجود: INDEX idx_data_points_plot
✅ موجود: INDEX idx_data_points_date
❌ مفقود: INDEX مركب على (experiment_id, parameter_code, measurement_date) للتحليلات
```

**التوصية:**

```sql
CREATE INDEX idx_data_points_analysis ON research_data_points(
    experiment_id, parameter_code, measurement_date
);
```

---

#### **جدول `iot_readings`**

```sql
✅ موجود: INDEX idx_iot_readings_device
❌ مفقود: INDEX على (tenant_id, recorded_at) للاستعلامات على مستوى المستأجر
❌ مفقود: PARTIAL INDEX للقراءات الأخيرة فقط
```

**التوصية:**

```sql
CREATE INDEX idx_iot_readings_tenant_time ON iot_readings(tenant_id, recorded_at DESC);

-- Partial index للأداء الأفضل (آخر 30 يوم فقط)
CREATE INDEX idx_iot_readings_recent ON iot_readings(device_id, recorded_at)
WHERE recorded_at > NOW() - INTERVAL '30 days';
```

---

### 🟡 4.2 فهارس GIST مفقودة للجداول الجغرافية

#### **جدول `research_plots`**

```sql
❌ مفقود: GIST INDEX على boundary و centroid
```

**التوصية:**

```sql
CREATE INDEX idx_research_plots_boundary ON research_plots USING GIST(boundary);
CREATE INDEX idx_research_plots_centroid ON research_plots USING GIST(centroid);
```

---

## 5. مشاكل سلامة البيانات (Data Integrity Issues)

### 🔴 5.1 عدم اتساق أنواع البيانات

#### **مشكلة: tenant_id**

| الجدول            | النوع          |
| ----------------- | -------------- |
| infra SQL         | `UUID`         |
| Field Core Prisma | `VARCHAR(100)` |
| Chat Tortoise     | `VARCHAR(64)`  |

**التأثير:** 🔥 **حرج - قد يمنع JOINs والمقارنات**

---

#### **مشكلة: أنواع الـGeometry**

| الجدول                     | النوع                      |
| -------------------------- | -------------------------- |
| fields (infra SQL)         | `GEOMETRY(POLYGON, 4326)`  |
| research_plots (infra SQL) | `GEOGRAPHY(POLYGON, 4326)` |
| Field Suite                | `geometry(Polygon, 4326)`  |

**الفرق:**

- `GEOMETRY`: يعامل الإحداثيات كـCartesian (x, y)
- `GEOGRAPHY`: يعامل الإحداثيات كـSpherical (lat, lon) - أدق للحسابات الجغرافية

**التأثير:** 🟡 **متوسط - قد يسبب اختلاف في حسابات المساحة والمسافة**

---

#### **مشكلة: NDVI value precision**

| الجدول                    | النوع                                       |
| ------------------------- | ------------------------------------------- |
| ndvi_observations         | `DECIMAL(4,3)` - نطاق: -1.000 إلى 1.000     |
| ndvi_records              | `DECIMAL(6,4)` - نطاق: -10.0000 إلى 10.0000 |
| fields.ndvi_value (infra) | `DECIMAL(5,4)`                              |

**التأثير:** 🟢 **منخفض - لكن يفضل التوحيد**

---

### 🟡 5.2 عدم اتساق في الـENUMs

#### **مثال: field_status**

```sql
-- في infra SQL
CREATE TYPE field_status AS ENUM ('active', 'fallow', 'preparing', 'harvested', 'archived');

-- في Field Core Prisma
enum FieldStatus {
  active
  fallow
  harvested
  preparing
  inactive  // مختلف عن 'archived'
}
```

**المشكلة:** `archived` في SQL ≠ `inactive` في Prisma

**التأثير:** 🟡 **متوسط - قد يسبب أخطاء runtime**

---

#### **مثال: task_type**

```sql
-- في infra SQL
CREATE TYPE task_type AS ENUM ('irrigation', 'fertilization', 'pesticide', 'harvest', 'planting', 'soil_prep', 'pruning', 'inspection', 'maintenance', 'other');

-- في Field Core Prisma
enum TaskType {
  irrigation
  fertilization
  spraying  // مختلف عن 'pesticide'
  scouting  // غير موجود في SQL
  maintenance
  sampling  // غير موجود في SQL
  harvest
  planting
  other
}
```

**التأثير:** 🔴 **حرج - عدم توافق كامل**

---

### 🔴 5.3 قيود مفقودة (Missing Constraints)

#### **جدول wallets**

```sql
-- لا توجد قيود CHECK على:
balance >= 0  -- يجب أن يكون الرصيد موجباً
current_loan <= loan_limit  -- القرض الحالي يجب ألا يتجاوز الحد
credit_score BETWEEN 300 AND 850  -- نطاق التصنيف الائتماني
```

**التوصية:**

```sql
ALTER TABLE wallets ADD CONSTRAINT chk_wallet_balance CHECK (balance >= 0);
ALTER TABLE wallets ADD CONSTRAINT chk_wallet_loan CHECK (current_loan <= loan_limit);
ALTER TABLE wallets ADD CONSTRAINT chk_credit_score CHECK (credit_score BETWEEN 300 AND 850);
```

---

#### **جدول loans**

```sql
-- قيود مفقودة:
amount > 0
total_due >= amount
paid_amount >= 0
paid_amount <= total_due
term_months > 0
```

**التوصية:**

```sql
ALTER TABLE loans ADD CONSTRAINT chk_loan_amounts CHECK (
    amount > 0 AND
    total_due >= amount AND
    paid_amount >= 0 AND
    paid_amount <= total_due AND
    term_months > 0
);
```

---

## 6. مشاكل إصدار المخططات (Schema Versioning)

### 🔴 6.1 عدم وجود آلية موحدة لإدارة الهجرات

**المشكلة:**

- **Prisma** يستخدم مجلد `migrations/` الخاص به
- **Alembic** (SQLAlchemy) يستخدم `versions/` مع تسمية `s{sprint}_{number}`
- **SQL الخام** في `infra/postgres/` بدون أي tracking تلقائي
- **Tortoise ORM** لا يوجد دليل على استخدام migrations

**التأثير:** 🔥 **حرج - احتمال تطبيق هجرات متضاربة**

---

### 🟡 6.2 جدول `_migrations` يدوي

```sql
-- في 001_init_extensions.sql
CREATE TABLE IF NOT EXISTS public._migrations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**المشكلة:**

- لا يتتبع **checksum** للهجرات
- لا يتتبع **rollback**
- لا يدعم **branching**

**التوصية:** استخدام أداة موحدة مثل Flyway أو Liquibase

---

### 🟡 6.3 عدم وجود أرقام إصدارات منسقة

**الملاحظات:**

- Alembic: `s7_0001`, `s8_0001` (sprint-based)
- Prisma: timestamps
- SQL: `001_`, `002_` (sequential)

**التأثير:** 🟡 صعوبة في تتبع ترتيب التطبيق عبر الأنظمة المختلفة

---

## 7. تبعيات ترتيب الهجرات (Migration Order Dependencies)

### 🔴 7.1 تبعيات غير موثقة

#### **السلسلة المطلوبة:**

```
1. infra/postgres/migrations/001_init_extensions.sql
   ↓ (يُنشئ PostGIS و UUID extensions)

2. infra/postgres/migrations/002_base_tables.sql
   ↓ (يُنشئ tenants, users, farms, fields)

3. packages/field_suite/migrations/s7_0001_postgis_hierarchy.py
   ↓ (قد يتعارض مع 002 لأنه ينشئ farms و fields أيضاً!)

4. apps/services/ndvi-engine/src/migrations/s8_0001_ndvi_timeseries.py
   ↓ (يحتاج fields لإنشاء FK)

5. shared/libs/outbox/alembic/versions/s4_0001_create_outbox_events.py
   ↓ (مستقل)

6. Prisma migrations (تلقائية، قد تتعارض مع الكل!)
```

**المشكلة:** 🔥 **حرج - لا يوجد ضمان لتطبيق الهجرات بالترتيب الصحيح**

---

### 🔴 7.2 PostGIS extension يُطلب في أماكن متعددة

```sql
-- في 001_init_extensions.sql
CREATE EXTENSION IF NOT EXISTS postgis;

-- في 00-init-sahool.sql
CREATE EXTENSION IF NOT EXISTS "postgis";
CREATE EXTENSION IF NOT EXISTS "postgis_topology";

-- في Field Core Prisma migration
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- في Field Suite Alembic
op.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
```

**النتيجة:** ✅ استخدام `IF NOT EXISTS` يمنع الأخطاء، لكن يوضح التكرار

---

### 🟡 7.3 Functions و Triggers متكررة

```sql
-- Function update_updated_at_column() معرفة في:
1. Field Core Prisma migration
2. infra/postgres/init/00-init-sahool.sql

-- Function calculate_field_area() معرفة في:
1. Field Core Prisma migration
2. infra/postgres/init/00-init-sahool.sql

-- Function sync_geometry_from_wkt() معرفة في:
1. Field Suite Alembic migration
```

**التأثير:** 🟡 **متوسط - قد يسبب تحذيرات عند إعادة التهيئة**

---

## 8. توصيات لعزل البيانات (Data Isolation)

### ✅ 8.1 توصيات قصيرة المدى (Quick Wins)

#### **1. إنشاء schemas منفصلة لكل خدمة**

```sql
-- بدلاً من:
CREATE TABLE public.fields (...)
CREATE TABLE public.experiments (...)
CREATE TABLE public.products (...)

-- استخدم:
CREATE SCHEMA IF NOT EXISTS field_service;
CREATE TABLE field_service.fields (...);

CREATE SCHEMA IF NOT EXISTS research_service;
CREATE TABLE research_service.experiments (...);

CREATE SCHEMA IF NOT EXISTS marketplace_service;
CREATE TABLE marketplace_service.products (...);

CREATE SCHEMA IF NOT EXISTS chat_service;
CREATE TABLE chat_service.threads (...);
```

**الفوائد:**
✅ حل فوري لتعارضات الأسماء
✅ عزل منطقي واضح
✅ سهولة إدارة الصلاحيات
✅ إمكانية نقل الـschema إلى قاعدة بيانات منفصلة لاحقاً

---

#### **2. إنشاء جداول مرجعية مشتركة (Shared Reference Tables)**

```sql
CREATE SCHEMA IF NOT EXISTS shared;

-- نسخة read-only من users للمراجع
CREATE TABLE shared.user_refs (
    user_id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL,
    full_name VARCHAR(255),
    email VARCHAR(255),
    last_synced_at TIMESTAMPTZ DEFAULT NOW()
);

-- نسخة read-only من fields للمراجع
CREATE TABLE shared.field_refs (
    field_id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL,
    name VARCHAR(255),
    last_synced_at TIMESTAMPTZ DEFAULT NOW()
);
```

**الاستخدام:**

- خدمة Research تشير إلى `shared.field_refs` بدلاً من `field_service.fields`
- يتم تحديث هذه الجداول عبر **CDC (Change Data Capture)** أو **Event Sourcing**

---

#### **3. استخدام UUID موحد لـtenant_id**

```sql
-- تحويل جميع tenant_id إلى UUID
ALTER TABLE chat_threads ALTER COLUMN tenant_id TYPE UUID USING tenant_id::UUID;
-- كرر لجميع الجداول
```

---

#### **4. توحيد ENUMs**

**خيار 1: استخدام جداول lookup**

```sql
CREATE TABLE shared.field_statuses (
    code VARCHAR(50) PRIMARY KEY,
    name_en VARCHAR(100),
    name_ar VARCHAR(100),
    is_active BOOLEAN DEFAULT true
);

INSERT INTO shared.field_statuses VALUES
    ('active', 'Active', 'نشط', true),
    ('fallow', 'Fallow', 'بور', true),
    ('harvested', 'Harvested', 'محصود', true),
    ('preparing', 'Preparing', 'قيد التحضير', true),
    ('inactive', 'Inactive', 'غير نشط', true);

-- في الجداول:
ALTER TABLE fields ADD CONSTRAINT fk_field_status
    FOREIGN KEY (status) REFERENCES shared.field_statuses(code);
```

**الفوائد:**
✅ مرونة في إضافة قيم جديدة بدون ALTER TYPE
✅ دعم متعدد اللغات
✅ إمكانية soft delete للقيم

---

### ✅ 8.2 توصيات متوسطة المدى

#### **1. تطبيق Database-per-Service Pattern**

```
sahool-field-db (PostgreSQL + PostGIS)
  ├── schema: field_service
  │   ├── fields
  │   ├── field_boundary_history
  │   ├── sync_status
  │   └── tasks

sahool-research-db (PostgreSQL)
  ├── schema: research_service
  │   ├── experiments
  │   ├── research_protocols
  │   ├── research_plots
  │   └── ...

sahool-marketplace-db (PostgreSQL)
  ├── schema: marketplace_service
  │   ├── products
  │   ├── orders
  │   ├── wallets
  │   └── ...

sahool-core-db (PostgreSQL)
  ├── schema: tenants_service
  │   └── tenants
  ├── schema: users_service
  │   └── users
  ├── schema: shared
  │   ├── user_refs (materialized view)
  │   └── field_refs (materialized view)
```

---

#### **2. استخدام Event-Driven Architecture للمراجع**

```javascript
// مثال: عند تحديث field
await publishEvent({
  type: "field.updated",
  tenant_id: field.tenant_id,
  field_id: field.id,
  data: {
    name: field.name,
    status: field.status,
    updated_at: field.updated_at,
  },
});

// خدمة Research تستمع وتحدث shared.field_refs
```

---

#### **3. تطبيق SAGA Pattern للمعاملات الموزعة**

مثال: إنشاء طلب في Marketplace يحتاج تحديث wallet:

```javascript
// Orchestrated SAGA
async function createOrderSaga(order) {
  const sagaId = uuid();

  try {
    // Step 1: Reserve wallet balance
    await walletService.reserveBalance(sagaId, order.total);

    // Step 2: Create order
    await orderService.create(sagaId, order);

    // Step 3: Deduct balance
    await walletService.deductBalance(sagaId, order.total);

    // Commit
    await sagaService.commit(sagaId);
  } catch (error) {
    // Compensate
    await walletService.releaseReservation(sagaId);
    await orderService.cancel(sagaId);
    throw error;
  }
}
```

---

### ✅ 8.3 توصيات طويلة المدى

#### **1. Migrate to Separate Databases**

**الهدف النهائي:**

```
┌─────────────────────────────────────────┐
│         API Gateway / BFF               │
└─────────────────────────────────────────┘
           │
    ┌──────┴──────┬──────────┬──────────┐
    │             │          │          │
┌───▼────┐  ┌────▼───┐  ┌──▼─────┐  ┌─▼──────┐
│Field   │  │Research│  │Market  │  │Chat    │
│Service │  │Service │  │Service │  │Service │
└───┬────┘  └────┬───┘  └──┬─────┘  └─┬──────┘
    │            │         │          │
┌───▼────┐  ┌───▼────┐  ┌─▼──────┐  ┌▼───────┐
│Field DB│  │Res. DB │  │Market  │  │Chat DB │
│PostGIS │  │PG      │  │DB PG   │  │PG      │
└────────┘  └────────┘  └────────┘  └────────┘
```

---

#### **2. استخدام Read Replicas لـShared Data**

```
Master DB (Core)
  ├── tenants
  └── users
       │
       ↓ (Replication)
       │
Read Replicas في كل خدمة
  ├── field-service-replica
  ├── research-service-replica
  └── marketplace-service-replica
```

---

#### **3. تطبيق CQRS (Command Query Responsibility Segregation)**

```
Write Model (Normalized)          Read Model (Denormalized)
┌─────────────────┐              ┌──────────────────────┐
│ fields          │──Events──────▶│ field_summaries     │
│  - id           │              │  - id                │
│  - name         │              │  - name              │
│  - status       │              │  - owner_name ✓     │
└─────────────────┘              │  - crop_name ✓      │
                                 │  - latest_ndvi ✓    │
┌─────────────────┐              │  - task_count ✓     │
│ ndvi_readings   │──Events──────▶│                     │
└─────────────────┘              └──────────────────────┘
```

---

## 9. ملخص المشاكل حسب الأولوية

### 🔴 **حرج - يجب الحل فوراً:**

1. ✋ **تعارض جدول `fields`** (3 تعريفات مختلفة)
2. ✋ **تعارض جدول `tasks`** (تعريفين)
3. ✋ **عدم اتساق ENUMs** (field_status, task_type)
4. ✋ **عدم اتساق tenant_id type** (UUID vs VARCHAR)
5. ✋ **عدم وجود آلية موحدة للهجرات**

---

### 🟡 **متوسط - يجب التخطيط للحل:**

6. ⚠️ تكرار الجداول البحثية (9 جداول)
7. ⚠️ تكرار جداول السوق (6 جداول)
8. ⚠️ تكرار جداول المحادثات (4 جداول)
9. ⚠️ مراجع FK عبر حدود الخدمات
10. ⚠️ فهارس مفقودة على جداول عالية الاستخدام
11. ⚠️ قيود CHECK مفقودة (wallets, loans)
12. ⚠️ عدم اتساق GEOMETRY vs GEOGRAPHY

---

### 🟢 **تحسينات - يمكن الحل لاحقاً:**

13. ℹ️ Functions و Triggers متكررة
14. ℹ️ عدم اتساق دقة NDVI values
15. ℹ️ جدول \_migrations يدوي يحتاج تحسين

---

## 10. خطة العمل المقترحة

### 📋 **المرحلة 1: التوحيد الفوري (أسبوع 1-2)**

```sql
-- 1. إنشاء schemas منفصلة
CREATE SCHEMA IF NOT EXISTS field_service;
CREATE SCHEMA IF NOT EXISTS research_service;
CREATE SCHEMA IF NOT EXISTS marketplace_service;
CREATE SCHEMA IF NOT EXISTS chat_service;
CREATE SCHEMA IF NOT EXISTS shared;

-- 2. نقل الجداول المتعارضة
ALTER TABLE fields SET SCHEMA field_service;
ALTER TABLE tasks SET SCHEMA field_service;
ALTER TABLE experiments SET SCHEMA research_service;
ALTER TABLE products SET SCHEMA marketplace_service;
ALTER TABLE chat_threads SET SCHEMA chat_service;

-- 3. توحيد tenant_id
-- (يتطلب migration script لتحويل البيانات)

-- 4. توحيد ENUMs
-- (إنشاء lookup tables كما هو موضح أعلاه)
```

---

### 📋 **المرحلة 2: إضافة الفهارس (أسبوع 3)**

```sql
-- تطبيق جميع الفهارس المقترحة في القسم 4
CREATE INDEX idx_chat_messages_sender ON chat_service.chat_messages(sender_id, created_at);
CREATE INDEX idx_transactions_wallet_date ON marketplace_service.transactions(wallet_id, created_at);
-- ... إلخ
```

---

### 📋 **المرحلة 3: إضافة القيود (أسبوع 4)**

```sql
-- إضافة CHECK constraints
ALTER TABLE marketplace_service.wallets ADD CONSTRAINT chk_wallet_balance CHECK (balance >= 0);
-- ... إلخ
```

---

### 📋 **المرحلة 4: توحيد الهجرات (أسبوع 5-6)**

- اختيار أداة واحدة (مقترح: **Liquibase** لدعم multi-language)
- تحويل جميع الهجرات الحالية إلى changelog موحد
- إعداد CI/CD للتحقق من الهجرات

---

### 📋 **المرحلة 5: Event-Driven Refs (أسبوع 7-10)**

- تطبيق Event Bus (Kafka/RabbitMQ)
- إنشاء جداول shared refs
- إعداد CDC للمزامنة التلقائية

---

### 📋 **المرحلة 6: فصل قواعد البيانات (شهر 3-6)**

- إنشاء قاعدة بيانات منفصلة لكل خدمة
- تطبيق data migration
- تحديث connection strings
- اختبار شامل

---

## 11. معايير النجاح (Success Metrics)

### ✅ **معايير فنية:**

- ✓ صفر تعارضات في أسماء الجداول
- ✓ 100% اتساق في أنواع البيانات
- ✓ جميع الفهارس الحرجة موجودة
- ✓ صفر FK مباشر بين الخدمات
- ✓ آلية موحدة للهجرات

### ✅ **معايير الأداء:**

- ✓ زمن استجابة الاستعلامات < 100ms (P95)
- ✓ القدرة على scale الخدمات بشكل مستقل
- ✓ صفر deadlocks بين الخدمات

### ✅ **معايير الصيانة:**

- ✓ وثائق كاملة للمخططات
- ✓ اختبارات integration تلقائية
- ✓ CI/CD pipeline للهجرات

---

## 12. الخلاصة

### 📊 **الوضع الحالي:**

| المعيار              | الحالة | التقييم               |
| -------------------- | ------ | --------------------- |
| توحيد المخططات       | ❌     | تعارضات متعددة        |
| عزل البيانات         | ⚠️     | schemas مشتركة        |
| الفهارس              | 🟡     | جيدة جزئياً           |
| سلامة البيانات       | ⚠️     | قيود مفقودة           |
| إدارة الهجرات        | ❌     | غير موحدة             |
| العلاقات بين الخدمات | ❌     | FK مباشرة             |
| الأداء               | 🟡     | جيد مع تحسينات مطلوبة |

---

### 🎯 **الرؤية المستقبلية:**

```
المنصة الحالية (Monolithic Database)
         ↓
   [المرحلة 1-2: توحيد فوري]
         ↓
Shared Database with Isolated Schemas
         ↓
   [المرحلة 3-5: Event-Driven]
         ↓
Database-per-Service with Event Bus
         ↓
   [المرحلة 6: فصل كامل]
         ↓
  Truly Distributed Microservices
```

---

### ⚡ **الأولوية القصوى:**

**يجب حل هذه المشاكل قبل Production:**

1. 🔴 تعارض `fields` table
2. 🔴 توحيد `tenant_id` type
3. 🔴 توحيد ENUMs
4. 🔴 إنشاء schemas منفصلة
5. 🔴 إضافة آلية tracking موحدة للهجرات

**التقدير الزمني:** 2-3 أسابيع للحل الحرج

---

## 13. مراجع إضافية

### 📚 **وثائق ذات صلة:**

- [Database Schemas Documentation](./docs/DATABASE.md)
- [Migration Guide](./docs/MIGRATIONS.md)
- [PostGIS Optimization](./docs/infrastructure/POSTGIS_OPTIMIZATION.md)
- [Comprehensive Review Report (Arabic)](./COMPREHENSIVE_REVIEW_REPORT_AR.md)

### 🔧 **ملفات المخططات:**

- Field Core: `/apps/services/field-core/prisma/schema.prisma`
- Research Core: `/apps/services/research-core/prisma/schema.prisma`
- Marketplace: `/apps/services/marketplace-service/prisma/schema.prisma`
- NDVI Engine: `/apps/services/ndvi-engine/src/models.py`
- Field Suite: `/packages/field_suite/spatial/orm_models.py`

### 🛠️ **ملفات الهجرات:**

- Infra Migrations: `/infra/postgres/migrations/`
- Infra Init: `/infra/postgres/init/`
- Alembic Migrations: `*/migrations/versions/`
- Prisma Migrations: `*/prisma/migrations/`

---

**تاريخ الإنشاء:** 2025-12-24
**الإصدار:** 1.0
**المحلل:** Claude Code Assistant
**الحالة:** 🔴 يتطلب إجراءات فورية
