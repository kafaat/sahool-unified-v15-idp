# تحليل بنية تطبيق الموبايل SAHOOL

**تاريخ التحليل:** 2025-12-21
**الإصدار:** 15.5.0

---

## ملخص تنفيذي

تطبيق SAHOOL Mobile يتبع **Clean Architecture جزئياً** مع نمط **Offline-First** متكامل.

| الجانب | الحالة | التفاصيل |
|--------|--------|----------|
| Clean Architecture | جزئي (60%) | معظم الميزات الرئيسية تتبعه |
| فصل الطبقات | جيد | domain/data/presentation واضحة |
| تدفق البيانات | ممتاز | Offline-First مع Outbox |
| إدارة الحالة | ممتاز | Riverpod متكامل |
| نظام المزامنة | ممتاز | Outbox + ETag |
| الذكاء الاصطناعي | متقدم | تحليل صحة المحاصيل + أوامر صوتية |

---

## 1. البنية المعمارية

### هيكل المجلدات

```
lib/
├── core/                      # البنية التحتية المشتركة
│   ├── auth/                 # خدمات المصادقة (Secure + Biometric)
│   ├── config/               # الإعدادات والتكوين
│   ├── di/                   # حقن التبعيات
│   ├── domain/models/        # النماذج الموحدة (CreditTier)
│   ├── http/                 # عميل API (Dio)
│   ├── storage/              # قاعدة البيانات (Drift ORM)
│   ├── sync/                 # محرك المزامنة (Outbox)
│   ├── voice/                # خدمة الأوامر الصوتية
│   └── map/                  # خدمات الخرائط
│
├── features/                  # الوحدات الوظيفية
│   ├── auth/                 # تسجيل الدخول
│   ├── crop_health/          # تحليل صحة المحاصيل (AI)
│   ├── field/                # كيانات الحقول (GIS)
│   ├── fields/               # شاشات الحقول
│   ├── home/                 # الشاشة الرئيسية
│   ├── market/               # السوق والمالية
│   ├── notifications/        # الإشعارات
│   ├── tasks/                # المهام
│   ├── wallet/               # المحفظة
│   └── weather/              # الطقس
│
└── main.dart                  # نقطة البداية
```

---

## 2. مكونات الذكاء الاصطناعي

### 2.1 تحليل صحة المحاصيل (`crop_health/`)

```dart
// المؤشرات النباتية المدعومة
VegetationIndices:
  - NDVI (Normalized Difference Vegetation Index)
  - EVI  (Enhanced Vegetation Index)
  - NDRE (Normalized Difference Red Edge)
  - LCI  (Leaf Chlorophyll Index)
  - NDWI (Normalized Difference Water Index)
  - SAVI (Soil Adjusted Vegetation Index)

// تشخيص الحقل
FieldDiagnosis:
  - تحليل المناطق (Zones)
  - إجراءات موصى بها بأولويات (P0-P3)
  - طبقات خريطة Raster (NDVI, NDWI, NDRE)
  - تصدير VRT للزراعة الدقيقة
```

### 2.2 الأوامر الصوتية (`core/voice/`)

```dart
// أوامر مدعومة باللهجة اليمنية
VoiceCommandType:
  - openField        // "افتح حقل رقم 1"
  - cropStatus       // "كيف المحصول"
  - recordIrrigation // "سجل ري"
  - showTasks        // "عرض المهام"
  - weather          // "كيف الطقس"
  - startScout       // "ابدأ مسح"
  - capturePhoto     // "التقط صورة"
  - dailySummary     // "ملخص اليوم"
```

### 2.3 خدمة AI الخلفية

```dart
// نقطة نهاية AI
EnvConfig.aiServiceUrl:
  - Development: http://10.0.2.2:8085
  - Staging: https://ai-staging.sahool.app
  - Production: https://ai.sahool.app
```

---

## 3. تدفق البيانات (Offline-First)

```
┌─────────────────────────────────────────────────────────────────┐
│                    طبقة العرض (PRESENTATION)                    │
│         ConsumerWidget -> ref.watch() -> إعادة البناء           │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                   إدارة الحالة (Riverpod)                       │
│  StateNotifierProvider | FutureProvider | StreamProvider        │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│             طبقة المستودع (Offline-First)                       │
│  1. حفظ محلي في SQLite                                          │
│  2. إضافة إلى Outbox للمزامنة                                   │
│  3. إرجاع البيانات المحلية فوراً                                │
└──────────────────────┬──────────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
   ┌────────┐  ┌──────────┐  ┌──────────────┐
   │ SQLite │  │ Outbox   │  │  API Client  │
   │ (Drift)│  │  Queue   │  │    (Dio)     │
   └────────┘  └──────────┘  └──────────────┘
```

### نمط الكتابة (Offline-First)
```
المستخدم يُنشئ حقل
    ↓
saveLocally() -> INSERT في جدول Fields
    ↓
createGeoJSON payload
    ↓
queueForSync() -> INSERT في جدول Outbox
    ↓
syncEngine.runOnce() -> إذا متصل، معالجة Outbox
    ↓
POST إلى /api/v1/fields + تعليم كـ synced
```

---

## 4. خدمات الخلفية

| الخدمة | المنفذ | المسار | الوصف |
|--------|--------|--------|-------|
| Kong Gateway | 8000 | /api/v1/* | بوابة API الموحدة |
| Field Service | 3000 | /fields, /gis | خدمة الحقول |
| Weather Service | 8092 | /weather | خدمة الطقس |
| Marketplace | 3010 | /market, /fintech | السوق والمالية |
| AI Service | 8085 | /predict, /diagnose | الذكاء الاصطناعي |
| WebSocket | 8090 | ws:// | التحديثات الفورية |

---

## 5. قاعدة البيانات المحلية

### جداول Drift ORM
```sql
-- الجداول الرئيسية
Tasks         -- المهام مع GeoJSON
Fields        -- الحقول مع Polygon boundaries
Outbox        -- طابور المزامنة مع ETag
SyncLogs      -- سجل التدقيق
SyncEvents    -- تتبع التعارضات
```

### دعم GIS
```dart
// تحويل GeoJSON <-> List<LatLng>
TextColumn get boundary =>
    text().map(const GeoPolygonConverter())();
```

---

## 6. إدارة الحالة (Riverpod)

| النوع | الاستخدام | مثال |
|-------|----------|------|
| `Provider<T>` | قراءة فقط | `fieldsRepoProvider` |
| `StateProvider<T>` | حالة بسيطة | `selectedFieldIdProvider` |
| `StateNotifierProvider` | منطق معقد | `walletProvider` |
| `FutureProvider<T>` | async لمرة واحدة | `diagnosisProvider` |
| `StreamProvider<T>` | تحديثات حية | `fieldsStreamProvider` |

---

## 7. الملفات المحذوفة وتحليلها

### ملفات تم حذفها بأمان:

| الملف | السبب | التأثير |
|-------|-------|---------|
| `core/notifications/notification_provider.dart` | مكرر مبسط | ✅ لا تأثير |
| `core/services/auth_service.dart` | نسخة قديمة بدون Biometric | ✅ لا تأثير |
| `features/wallet/ui/wallet_screen.dart` | StatefulWidget مكرر | ✅ لا تأثير |
| `features/home_v16/*` | غير مربوط بالRouter | ⚠️ كان يحتوي KPI جميل |
| `features/notifications/notification_provider.dart` | مكرر | ⚠️ كان يحتوي NotificationType enum |

### ملاحظات مهمة:

1. **home_v16** كان يحتوي على شاشة رئيسية حديثة بـ:
   - KPI Grid (NDVI, Alerts, Tasks, Weather)
   - Quick Actions
   - Alerts Preview
   - **لكنه لم يكن مستخدماً في Router**

2. **notification_provider.dart** كان يحتوي على:
   - `NotificationType` enum مفصل
   - `NotificationPriority` enum
   - نموذج `AppNotification` أغنى
   - **تم استبداله بـ domain/entities**

---

## 8. التوصيات

### أولوية عالية:
1. ✅ توحيد هيكل الـ features
2. ⬜ إضافة طبقة Use Cases
3. ⬜ توحيد معالجة الأخطاء

### أولوية متوسطة:
4. ⬜ توحيد تسمية المجلدات (ui vs presentation)
5. ⬜ مركزة جميع Providers
6. ⬜ استخراج Magic Strings

### تحسينات أداء:
7. ⬜ استخدام Stream لحالة الشبكة
8. ⬜ تحسين Drift queries

---

## 9. مقارنة قبل وبعد

| المقياس | قبل | بعد |
|---------|-----|-----|
| ملفات مكررة | 8 | 0 |
| خدمات Auth | 2 | 1 (موحد) |
| مزودات Notification | 3 | 1 |
| CreditTier enum | 2 | 1 (موحد) |
| شاشات Wallet | 2 | 1 |

---

## 10. الخلاصة

التطبيق يمتلك بنية قوية للذكاء الاصطناعي:
- ✅ تحليل صحة المحاصيل (NDVI, EVI, etc.)
- ✅ أوامر صوتية عربية
- ✅ VRT export للزراعة الدقيقة
- ✅ Offline-First مع مزامنة ذكية

الملفات المحذوفة **لم تحتوِ على منطق AI أساسي** - كانت:
- نسخ UI مكررة
- خدمات بميزات أقل
- كود غير مستخدم

**لم يتم حذف أي كود AI أو ML أو بنية حديثة مهمة.**

---

**SAHOOL - سهول الزراعية**
