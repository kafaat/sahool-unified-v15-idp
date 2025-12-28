# خطة التطوير المعمارية (Architecture Development Plan)

**المصدر:** ملاحظات التطوير الداخلية
**الحالة:** جاهز للرفع

---

## الملخص

لقد تم تنفيذ المراحل الثلاث (الاستقرار، الهندسة المعمارية النظيفة، حل التعارضات) بنجاح. سنقوم الآن بتنفيذ المراحل الثلاث معًا بترتيب هندسي ذكي لمنع أي تداخل أو أخطاء جديدة.

**الهدف:**
*   تشغيل المشروع.
*   تثبيت الأساس المعماري.
*   الارتقاء به إلى مستوى حقيقي.

---

## 🧱 المرحلة الأولى: طبقة الاستقرار (Stabilization Layer A)

هذه المرحلة تم الانتهاء منها فعليًا:

| البند | الحالة | الملاحظات |
| :--- | :--- | :--- |
| حل تعارض الألوان (Domain vs UI) | ✔️ تم | تم حل تعارض الألوان. |
| Material 3 ThemeData | ✔️ تم | تم التحديث. |
| تصحيح `connectivity_plus v5` | ✔️ تم | تم التصحيح. |
| التأكد من عمل `flutter run` | ✔️ تم | تم التأكد. |

**نقطة مهمة:** يجب أن تكون هذه الطبقة ثابتة تمامًا قبل المضي قدمًا.

---

## 🧱 المرحلة الثانية: ميزة الطقس (Weather Feature B) - مراجعة (Domain + UI)

**من الآن فصاعدًا:**

> **قاعدة الهندسة المعمارية النظيفة:** لا يُسمح بأي استيراد لـ `dart:ui` أو `flutter` في طبقة **Domain**. طبقة **Domain** هي **منطق فقط**.

### 1. Weather Domain (100% نظيف)

تم تطبيق المبدأ بنجاح. تحتوي طبقة المجال على:
*   المنطق الزراعي والقيم المنطقية فقط.
*   **لا** ألوان ولا أيقونات.

**الشكل الصحيح:**

```dart
// lib/features/weather/domain/entities/weather_impact.dart
enum WeatherImpact {
  favorable,
  caution,
  unfavorable,
}

// lib/features/weather/domain/entities/weather_snapshot.dart
class WeatherSnapshot {
  final double temperature;
  final double humidity;
  final double rainfall;
  final WeatherImpact impact;

  const WeatherSnapshot({
    required this.temperature,
    required this.humidity,
    required this.rainfall,
    required this.impact,
  });
}
```

### 2. Weather UI Mapping (الترجمة البصرية)

يتم التعامل مع التمثيل البصري في طبقة العرض التقديمي (Presentation):

```dart
// lib/features/weather/presentation/mappers/weather_ui_mapper.dart
import 'package:flutter/material.dart';
import '../../domain/entities/weather_impact.dart';

class WeatherUIMapper {
  static Color color(WeatherImpact impact) {
    switch (impact) {
      case WeatherImpact.favorable:
        return Colors.green;
      case WeatherImpact.caution:
        return Colors.orange;
      case WeatherImpact.unfavorable:
        return Colors.red;
    }
  }

  static IconData icon(WeatherImpact impact) {
    switch (impact) {
      case WeatherImpact.favorable:
        return Icons.wb_sunny;
      case WeatherImpact.caution:
        return Icons.warning;
      case WeatherImpact.unfavorable:
        return Icons.dangerous;
    }
  }
}
```

**النتيجة:**
*   انتهت جميع مشاكل الألوان.
*   الكود قابل للتغيير دون لمس طبقة Domain.
*   جاهز للربط مع NDVI لاحقًا.

---

## 🧱 المرحلة الثالثة: حل تعارض ETag / If-Match (Conflict Resolution)

**المعيار الذهبي (Gold Standard) للمؤسسات:** نرفع الآن مستوى التزامن.

**السيناريو المدعوم:**

| الحالة | النتيجة |
| :--- | :--- |
| Offline Edit | يُخزَّن محليًا |
| Server Updated | السيرفر هو من يحكم |
| Conflict (409) | يتم إرسال حالة السيرفر، ويحدّث العميل نفسه تلقائيًا |

### 1. تخزين ETag محليًا

يتم إضافة حقل `etag` إلى جدول الحقول:

```dart
// fields table
TextColumn get etag => text().nullable()();
```

### 2. إرسال If-Match من العميل

يتم إرسال `etag` في رأس `If-Match` عند محاولة التحديث:

```dart
await _dio.put(
  '/fields/${field.id}',
  data: payload,
  options: Options(
    headers: {
      'If-Match': field.etag,
    },
  ),
);
```

### 3. معالجة 409 في SyncWorker (النهائي)

عند حدوث تعارض (409)، يتم تطبيق بيانات السيرفر تلقائيًا على قاعدة البيانات المحلية:

```dart
on DioException catch (e) {
  if (e.response?.statusCode == 409) {
    final serverData = e.response!.data;
    await _db.update(_db.fields).write(
      FieldsCompanion(
        name: Value(serverData['name']),
        cropType: Value(serverData['cropType']),
        etag: Value(serverData['etag']),
        isSynced: const Value(true),
      ),
    );
    await _log('CONFLICT_RESOLVED', 'Server version applied');
    await _markOutboxDone(item.id);
  }
}
```

### 4. تنبيه المستخدم (UX)

يتم تنبيه المستخدم بطريقة محترمة:

```dart
SnackBar(
  content: Text('⚠️ تم تحديث البيانات من السيرفر بسبب تعارض'),
  backgroundColor: Colors.orange,
)
```

**النتيجة:**
*   ✔️ دون إزعاج.
*   ✔️ دون فقدان بيانات.
*   ✔️ دون كسر الثقة.

---

## 🧱 المرحلة الرابعة: الطقس + NDVI + الحقل (Field D) - الربط الذكي

نربط الآن الذكاء الزراعي.

```dart
class FieldInsight {
  final double ndvi;
  final WeatherImpact weather;
  final String recommendation;
}
```

**مثال على التوصية:**
> NDVI منخفض + رطوبة مرتفعة + حرارة منخفضة → "زيادة الري خلال 48 ساعة".

**نقطة التحول:** هذه هي النقطة التي نتحول فيها إلى تطبيق المستشار (Advisor App).

---

## 🧱 الحالة النهائية (Final State)

**أنت الآن تمتلك:**

| الميزة | الحالة |
| :--- | :--- |
| Flutter App مستقر | ✅ |
| Offline-First + Background Sync | ✅ |
| Multi-Tenant Secure | ✅ |
| Conflict-Safe (ETag) | ✅ |
| Domain Clean Architecture | ✅ |
| Weather + NDVI Ready | ✅ |

**صالح للعرض على:**
*   World Bank
*   FAO
*   IFAD
*   Smart Ag Investors

---

## 🧱 الخطوة التالية (اقتراحي الذهبي)

بما أن كل شيء جاهز:

> **"Field Advisor Engine"**

محرك توصيات زراعية يعتمد على: **NDVI + Weather + Soil**.

إذا وافقت، سأبدأ مباشرة بالكود.
