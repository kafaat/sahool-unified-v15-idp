# 🚀 دليل البدء السريع - Quick Start Guide

## Astronomical Task Widget

---

## ⚡ التشغيل في 3 خطوات

### الخطوة 1: نسخ الكود التالي

```dart
import 'package:mobile/features/tasks/presentation/widgets/astronomical_task_widget.dart';

void showAstronomicalTaskSheet(BuildContext context) {
  showModalBottomSheet(
    context: context,
    isScrollControlled: true,
    backgroundColor: Colors.transparent,
    builder: (context) => DraggableScrollableSheet(
      initialChildSize: 0.9,
      minChildSize: 0.5,
      maxChildSize: 0.95,
      builder: (_, __) => const AstronomicalTaskWidget(),
    ),
  );
}
```

### الخطوة 2: إضافة زر

```dart
IconButton(
  icon: const Icon(Icons.auto_awesome),
  tooltip: 'التقويم الفلكي',
  onPressed: () => showAstronomicalTaskSheet(context),
)
```

### الخطوة 3: تشغيل التطبيق

```bash
flutter run
```

**هذا كل شيء! الويدجت جاهز للعمل! ✨**

---

## 📋 قائمة التحقق السريعة

### التثبيت

- [x] الملف الرئيسي: `astronomical_task_widget.dart` ✓
- [x] جميع التبعيات موجودة في pubspec.yaml ✓
- [x] لا حاجة لتثبيت أي شيء إضافي ✓

### الاستخدام

- [ ] نسخ دالة `showAstronomicalTaskSheet`
- [ ] إضافة زر في الواجهة
- [ ] اختبار الفتح والإغلاق
- [ ] اختبار اختيار الأنشطة
- [ ] اختبار إنشاء المهام

### الاختبار

- [ ] الفتح يعمل بشكل صحيح
- [ ] البيانات تحمّل من API
- [ ] التبديل بين التقويم والقائمة
- [ ] اختيار الأيام يعمل
- [ ] زر إنشاء المهمة يعمل
- [ ] التخزين المؤقت يعمل (اختبار offline)

---

## 🎯 أمثلة سريعة

### مثال 1: في AppBar

```dart
AppBar(
  title: Text('المهام'),
  actions: [
    IconButton(
      icon: Icon(Icons.auto_awesome),
      onPressed: () => showAstronomicalTaskSheet(context),
    ),
  ],
)
```

### مثال 2: كـ FAB

```dart
FloatingActionButton.extended(
  onPressed: () => showAstronomicalTaskSheet(context),
  icon: Icon(Icons.auto_awesome),
  label: Text('التقويم الفلكي'),
  backgroundColor: Color(0xFF367C2B),
)
```

### مثال 3: في Card

```dart
Card(
  child: ListTile(
    leading: Icon(Icons.auto_awesome),
    title: Text('التقويم الفلكي'),
    subtitle: Text('أفضل أيام الزراعة'),
    onTap: () => showAstronomicalTaskSheet(context),
  ),
)
```

### مثال 4: مع معلومات الحقل

```dart
// تمرير معلومات الحقل
showModalBottomSheet(
  context: context,
  isScrollControlled: true,
  backgroundColor: Colors.transparent,
  builder: (context) => DraggableScrollableSheet(
    initialChildSize: 0.9,
    builder: (_, __) => AstronomicalTaskWidget(
      fieldId: 'field_123',
      fieldName: 'حقل القمح الشمالي',
    ),
  ),
);
```

---

## 🎨 التخصيص السريع

### تغيير الألوان

في ملف `astronomical_task_widget.dart`:

```dart
// البحث عن
backgroundColor: Color(0xFF367C2B)

// واستبدالها بـ
backgroundColor: Color(0xYourColor)
```

### تغيير النشاط الافتراضي

```dart
// البحث عن
final astronomicalTaskActivityProvider = StateProvider<String>((ref) => 'زراعة');

// تغيير إلى
final astronomicalTaskActivityProvider = StateProvider<String>((ref) => 'ري');
```

### تغيير مدة التخزين المؤقت

```dart
// البحث عن
if (DateTime.now().difference(timestamp).inDays > 7)

// تغيير إلى
if (DateTime.now().difference(timestamp).inDays > 3) // 3 أيام
```

---

## 🐛 حل المشاكل السريع

### المشكلة 1: لا يفتح الويدجت

**السبب المحتمل:** نسيان ProviderScope

**الحل:**

```dart
void main() {
  runApp(
    ProviderScope(  // ✓ تأكد من وجود هذا
      child: MyApp(),
    ),
  );
}
```

### المشكلة 2: البيانات لا تظهر

**السبب المحتمل:** مشكلة في الـ API

**الحل:**

```dart
// تحقق من تكوين API في EnvConfig
print(EnvConfig.apiBaseUrl);  // يجب أن يطبع رابط API الصحيح
```

### المشكلة 3: خطأ في التاريخ

**السبب المحتمل:** عدم تهيئة intl

**الحل:**

```dart
import 'package:intl/date_symbol_data_local.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await initializeDateFormatting('ar', null);  // ✓ إضافة هذا
  runApp(MyApp());
}
```

### المشكلة 4: لا يعمل في وضع Offline

**السبب المحتمل:** لم يتم تخزين البيانات بعد

**الحل:**

```dart
// 1. شغّل التطبيق مع الإنترنت أولاً
// 2. افتح الويدجت لتحميل البيانات
// 3. الآن جرب وضع offline
```

---

## 📱 اختبار سريع

### اختبار وظيفي (2 دقيقة)

1. افتح التطبيق
2. اضغط زر التقويم الفلكي ⭐
3. اختر "زراعة"
4. اختر يوم من التقويم
5. اضغط "إنشاء مهمة"
6. تحقق من الانتقال لشاشة المهام

### اختبار offline (1 دقيقة)

1. افتح الويدجت مرة (مع الإنترنت)
2. فعّل وضع الطيران ✈️
3. افتح الويدجت مرة أخرى
4. تحقق من ظهور البيانات

---

## 📚 المراجع السريعة

| الملف                                   | الوصف           | الحجم |
| --------------------------------------- | --------------- | ----- |
| `astronomical_task_widget.dart`         | الويدجت الرئيسي | 37 KB |
| `astronomical_task_widget_README.md`    | الوثائق الكاملة | 12 KB |
| `astronomical_task_widget_example.dart` | 6 أمثلة جاهزة   | 11 KB |
| `INTEGRATION_GUIDE.md`                  | دليل التكامل    | -     |
| `ASTRONOMICAL_WIDGET_SUMMARY.md`        | الملخص الشامل   | -     |

---

## ⚙️ الإعدادات الموصى بها

### للتطوير

```dart
// في dev mode، قلل مدة التخزين للاختبار
if (kDebugMode) {
  if (DateTime.now().difference(timestamp).inMinutes > 5) {
    return null; // 5 دقائق بدلاً من 7 أيام
  }
}
```

### للإنتاج

```dart
// في production، استخدم المدة الافتراضية
if (DateTime.now().difference(timestamp).inDays > 7) {
  return null; // 7 أيام
}
```

---

## 🎯 نصائح الأداء

### ✅ افعل

- استخدم `const` حيثما أمكن
- اترك التخزين المؤقت مفعّلاً
- استخدم `AutoDispose` للمزودات
- اختبر على أجهزة مختلفة

### ❌ لا تفعل

- لا تعطل التخزين المؤقت
- لا تحمّل البيانات في كل مرة
- لا تستخدم `setState` بكثرة
- لا تنسى إدارة الذاكرة

---

## 🚀 الخطوات التالية

1. ✅ **الآن**: اختبر الويدجت في تطبيقك
2. 📖 **بعدها**: اقرأ الوثائق الكاملة في README
3. 🎨 **ثم**: خصص التصميم حسب احتياجك
4. 🔧 **أخيراً**: أضف ميزات إضافية إذا احتجت

---

## 💡 نصيحة أخيرة

> **الويدجت جاهز للعمل مباشرة!**
> فقط انسخ دالة `showAstronomicalTaskSheet` وأضف زر.
> كل شيء آخر سيعمل تلقائياً! ✨

---

## 📞 الدعم

إذا واجهت أي مشكلة:

1. راجع `astronomical_task_widget_README.md` للوثائق الكاملة
2. راجع `astronomical_task_widget_example.dart` لأمثلة عملية
3. راجع `INTEGRATION_GUIDE.md` لخطوات التكامل
4. راجع قسم "حل المشاكل" في هذا الملف

---

**تم إنشاء الويدجت بواسطة فريق SAHOOL**
**جاهز للاستخدام • مفتوح المصدر • موثّق بالكامل**

🌟 استمتع بالتقويم الفلكي اليمني! 🌙
