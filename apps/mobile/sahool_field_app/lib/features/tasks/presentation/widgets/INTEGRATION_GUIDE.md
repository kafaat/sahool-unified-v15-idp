# دليل التكامل السريع - Astronomical Task Widget Integration Guide

## الخطوات السريعة للتكامل

### الخطوة 1: استيراد الويدجت

```dart
import 'package:mobile/features/tasks/presentation/widgets/astronomical_task_widget.dart';
```

### الخطوة 2: إضافة دالة مساعدة

أضف هذه الدالة في أي ملف يحتاج لعرض التقويم الفلكي:

```dart
void showAstronomicalTaskSheet(
  BuildContext context, {
  String? fieldId,
  String? fieldName,
}) {
  showModalBottomSheet(
    context: context,
    isScrollControlled: true,
    backgroundColor: Colors.transparent,
    builder: (context) => DraggableScrollableSheet(
      initialChildSize: 0.9,
      minChildSize: 0.5,
      maxChildSize: 0.95,
      builder: (context, scrollController) => AstronomicalTaskWidget(
        fieldId: fieldId,
        fieldName: fieldName,
      ),
    ),
  );
}
```

### الخطوة 3: إضافة زر في الواجهة

#### أ. في شاشة المهام (Tasks Screen)

```dart
// في AppBar
AppBar(
  title: Text('المهام'),
  actions: [
    IconButton(
      icon: Icon(Icons.auto_awesome),
      tooltip: 'التقويم الفلكي',
      onPressed: () => showAstronomicalTaskSheet(context),
    ),
  ],
)
```

#### ب. في شاشة تفاصيل الحقل (Field Details)

```dart
FloatingActionButton.extended(
  onPressed: () => showAstronomicalTaskSheet(
    context,
    fieldId: field.id,
    fieldName: field.name,
  ),
  icon: Icon(Icons.auto_awesome),
  label: Text('التقويم الفلكي'),
  backgroundColor: Color(0xFF367C2B),
)
```

#### ج. في قائمة الحقول (Fields List)

```dart
ListTile(
  title: Text(field.name),
  trailing: IconButton(
    icon: Icon(Icons.auto_awesome),
    onPressed: () => showAstronomicalTaskSheet(
      context,
      fieldId: field.id,
      fieldName: field.name,
    ),
  ),
)
```

## أمثلة التكامل الكامل

### 1. تعديل شاشة المهام الحالية

**الملف:** `/apps/mobile/lib/features/tasks/presentation/tasks_list_screen.dart`

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'widgets/astronomical_task_widget.dart';

class TasksListScreen extends ConsumerWidget {
  final String? fieldId;
  final String? fieldName;

  const TasksListScreen({
    super.key,
    this.fieldId,
    this.fieldName,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('المهام'),
        actions: [
          // زر التقويم الفلكي الجديد
          IconButton(
            icon: const Icon(Icons.auto_awesome),
            tooltip: 'التقويم الفلكي',
            onPressed: () => _showAstronomicalSheet(context),
          ),
        ],
      ),
      body: _buildTasksList(),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => _showAstronomicalSheet(context),
        icon: const Icon(Icons.auto_awesome),
        label: const Text('مهمة فلكية'),
      ),
    );
  }

  void _showAstronomicalSheet(BuildContext context) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => DraggableScrollableSheet(
        initialChildSize: 0.9,
        minChildSize: 0.5,
        maxChildSize: 0.95,
        builder: (context, scrollController) => AstronomicalTaskWidget(
          fieldId: fieldId,
          fieldName: fieldName,
        ),
      ),
    );
  }

  Widget _buildTasksList() {
    // قائمة المهام الحالية
    return const Center(child: Text('قائمة المهام'));
  }
}
```

### 2. إضافة تبويب في شاشة الحقل

**الملف:** `/apps/mobile/lib/features/field/presentation/field_details_screen.dart`

```dart
import 'package:flutter/material.dart';
import '../../tasks/presentation/widgets/astronomical_task_widget.dart';

class FieldDetailsScreen extends StatelessWidget {
  final String fieldId;
  final String fieldName;

  const FieldDetailsScreen({
    super.key,
    required this.fieldId,
    required this.fieldName,
  });

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 4,
      child: Scaffold(
        appBar: AppBar(
          title: Text(fieldName),
          bottom: const TabBar(
            isScrollable: true,
            tabs: [
              Tab(icon: Icon(Icons.info), text: 'معلومات'),
              Tab(icon: Icon(Icons.task), text: 'المهام'),
              Tab(icon: Icon(Icons.auto_awesome), text: 'التقويم الفلكي'), // جديد
              Tab(icon: Icon(Icons.analytics), text: 'الإحصائيات'),
            ],
          ),
        ),
        body: TabBarView(
          children: [
            _buildInfoTab(),
            _buildTasksTab(),
            // تبويب التقويم الفلكي الجديد
            AstronomicalTaskWidget(
              fieldId: fieldId,
              fieldName: fieldName,
            ),
            _buildAnalyticsTab(),
          ],
        ),
      ),
    );
  }

  Widget _buildInfoTab() => const Center(child: Text('معلومات الحقل'));
  Widget _buildTasksTab() => const Center(child: Text('المهام'));
  Widget _buildAnalyticsTab() => const Center(child: Text('الإحصائيات'));
}
```

### 3. إضافة في القائمة الرئيسية

**الملف:** `/apps/mobile/lib/core/widgets/drawer_menu.dart`

```dart
// في قائمة الدرج (Drawer)
ListTile(
  leading: const Icon(Icons.auto_awesome),
  title: const Text('التقويم الفلكي'),
  subtitle: const Text('أفضل أيام الزراعة حسب المنازل القمرية'),
  onTap: () {
    Navigator.pop(context); // إغلاق الدرج
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => DraggableScrollableSheet(
        initialChildSize: 0.9,
        minChildSize: 0.5,
        maxChildSize: 0.95,
        builder: (context, scrollController) => const AstronomicalTaskWidget(),
      ),
    );
  },
)
```

### 4. إضافة في الشاشة الرئيسية كبطاقة

**الملف:** `/apps/mobile/lib/features/home/home_screen.dart`

```dart
// في GridView أو ListView للبطاقات الرئيسية
Card(
  child: InkWell(
    onTap: () => _showAstronomicalSheet(context),
    child: Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: const Color(0xFF367C2B).withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: const Icon(
              Icons.auto_awesome,
              size: 48,
              color: Color(0xFF367C2B),
            ),
          ),
          const SizedBox(height: 12),
          const Text(
            'التقويم الفلكي',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            'أفضل أيام الزراعة',
            style: TextStyle(
              fontSize: 12,
              color: Colors.grey[600],
            ),
          ),
        ],
      ),
    ),
  ),
)
```

## نصائح للتكامل

### 1. التخصيص حسب السياق

```dart
// في شاشة حقل معين
showAstronomicalTaskSheet(
  context,
  fieldId: currentFieldId,
  fieldName: currentFieldName,
)

// في الشاشة الرئيسية (بدون حقل محدد)
showAstronomicalTaskSheet(context)
```

### 2. التعامل مع النتيجة

```dart
// الاستماع لنتيجة إنشاء المهمة
Navigator.push(context, ...).then((created) {
  if (created == true) {
    // تحديث قائمة المهام
    ref.refresh(tasksProvider);
  }
});
```

### 3. التكامل مع الإشعارات

```dart
// عرض إشعار عند إنشاء مهمة فلكية
void _onTaskCreated(BestDay day, String activity) {
  showNotification(
    title: 'مهمة فلكية جديدة',
    body: 'تم إنشاء مهمة $activity في ${day.date}',
    // ... تفاصيل الإشعار
  );
}
```

## اختبار التكامل

### 1. اختبار الفتح

```dart
// تحقق من فتح الويدجت
testWidgets('Opens astronomical task widget', (tester) async {
  await tester.pumpWidget(MyApp());
  await tester.tap(find.byIcon(Icons.auto_awesome));
  await tester.pumpAndSettle();

  expect(find.text('التقويم الفلكي للمهام'), findsOneWidget);
});
```

### 2. اختبار اختيار النشاط

```dart
// تحقق من تغيير النشاط
testWidgets('Changes activity', (tester) async {
  // ... فتح الويدجت
  await tester.tap(find.text('ري'));
  await tester.pumpAndSettle();

  // التحقق من تحديث البيانات
});
```

### 3. اختبار إنشاء المهمة

```dart
// تحقق من إنشاء مهمة
testWidgets('Creates task from selected day', (tester) async {
  // ... فتح الويدجت واختيار يوم
  await tester.tap(find.text('إنشاء مهمة'));
  await tester.pumpAndSettle();

  expect(find.byType(CreateTaskScreen), findsOneWidget);
});
```

## الأخطاء الشائعة وحلولها

### 1. خطأ: لا يظهر الويدجت

**الحل:**

```dart
// تأكد من وجود ProviderScope في التطبيق
void main() {
  runApp(
    ProviderScope(
      child: MyApp(),
    ),
  );
}
```

### 2. خطأ: البيانات لا تحمّل

**الحل:**

```dart
// تحقق من تكوين API
// في EnvConfig
static String get apiBaseUrl => 'https://your-api.com';
```

### 3. خطأ: التاريخ لا يعمل

**الحل:**

```dart
// تأكد من تهيئة intl
import 'package:intl/date_symbol_data_local.dart';

void main() async {
  await initializeDateFormatting('ar', null);
  runApp(MyApp());
}
```

## قائمة المراجعة

- [ ] استيراد الويدجت في الملف المطلوب
- [ ] إضافة دالة `showAstronomicalTaskSheet`
- [ ] إضافة زر أو عنصر UI للفتح
- [ ] اختبار الفتح والإغلاق
- [ ] اختبار اختيار الأنشطة
- [ ] اختبار اختيار الأيام
- [ ] اختبار إنشاء المهام
- [ ] اختبار في وضع عدم الاتصال
- [ ] اختبار على أحجام شاشات مختلفة
- [ ] مراجعة تجربة المستخدم

## الدعم والمساعدة

للأسئلة والمشاكل، راجع:

- `astronomical_task_widget_README.md` - الوثائق الكاملة
- `astronomical_task_widget_example.dart` - أمثلة الاستخدام
- `/apps/mobile/lib/features/astronomical/` - الميزة الفلكية الأساسية

---

تم إنشاء الدليل بواسطة فريق تطوير SAHOOL
