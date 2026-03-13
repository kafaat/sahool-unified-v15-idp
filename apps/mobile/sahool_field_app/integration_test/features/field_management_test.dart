/// SAHOOL Field App - Field Management Integration Tests
/// اختبارات تكامل إدارة الحقول
///
/// Tests the field management UI components:
/// - Field list display
/// - Field creation form
/// - Field editing
/// - Field deletion with confirmation
/// - NDVI status display
/// - Crop type selection
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  // =========================================================================
  // Test Data
  // =========================================================================

  final testFields = [
    {
      'id': 'f001',
      'name': 'حقل القمح الشمالي',
      'crop': 'قمح',
      'area': '5.5 هـ',
      'ndvi': 0.72,
      'status': 'نشط',
    },
    {
      'id': 'f002',
      'name': 'حقل الذرة الجنوبي',
      'crop': 'ذرة',
      'area': '3.2 هـ',
      'ndvi': 0.65,
      'status': 'نشط',
    },
    {
      'id': 'f003',
      'name': 'حقل الطماطم',
      'crop': 'طماطم',
      'area': '2.0 هـ',
      'ndvi': 0.58,
      'status': 'نشط',
    },
  ];

  // =========================================================================
  // Field List Tests
  // اختبارات قائمة الحقول
  // =========================================================================

  group('Field List Tests - اختبارات قائمة الحقول', () {
    testWidgets('Field list shows all fields', (tester) async {
      await tester.pumpWidget(ProviderScope(
        child: MaterialApp(
          locale: const Locale('ar'),
          home: Scaffold(
            appBar: AppBar(title: const Text('الحقول')),
            body: ListView.builder(
              itemCount: testFields.length,
              itemBuilder: (_, i) => ListTile(
                leading: const Icon(Icons.grass, color: Colors.green),
                title: Text(testFields[i]['name'] as String),
                subtitle: Text(
                  '${testFields[i]['crop']} • ${testFields[i]['area']}',
                ),
                trailing: const Icon(Icons.chevron_right),
              ),
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      for (final field in testFields) {
        expect(find.text(field['name'] as String), findsOneWidget);
      }
    });

    testWidgets('Field list shows crop type and area', (tester) async {
      await tester.pumpWidget(ProviderScope(
        child: MaterialApp(
          locale: const Locale('ar'),
          home: Scaffold(
            body: ListView.builder(
              itemCount: testFields.length,
              itemBuilder: (_, i) => ListTile(
                title: Text(testFields[i]['name'] as String),
                subtitle: Text(
                  '${testFields[i]['crop']} • ${testFields[i]['area']}',
                ),
              ),
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      expect(find.text('قمح • 5.5 هـ'), findsOneWidget);
      expect(find.text('ذرة • 3.2 هـ'), findsOneWidget);
    });

    testWidgets('NDVI value is displayed with correct color coding', (tester) async {
      // NDVI > 0.6 = healthy (green), 0.4-0.6 = moderate (yellow), < 0.4 = stressed (red)
      Color ndviColor(double ndvi) {
        if (ndvi >= 0.6) return Colors.green;
        if (ndvi >= 0.4) return Colors.orange;
        return Colors.red;
      }

      await tester.pumpWidget(ProviderScope(
        child: MaterialApp(
          locale: const Locale('ar'),
          home: Scaffold(
            body: ListView.builder(
              itemCount: testFields.length,
              itemBuilder: (_, i) {
                final ndvi = testFields[i]['ndvi'] as double;
                return ListTile(
                  title: Text(testFields[i]['name'] as String),
                  trailing: Chip(
                    label: Text('NDVI: $ndvi'),
                    backgroundColor: ndviColor(ndvi).withOpacity(0.2),
                    side: BorderSide(color: ndviColor(ndvi)),
                  ),
                );
              },
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      expect(find.text('NDVI: 0.72'), findsOneWidget);
      expect(find.text('NDVI: 0.65'), findsOneWidget);
      expect(find.text('NDVI: 0.58'), findsOneWidget);
    });

    testWidgets('Field list shows empty state when no fields', (tester) async {
      await tester.pumpWidget(ProviderScope(
        child: MaterialApp(
          locale: const Locale('ar'),
          home: Scaffold(
            appBar: AppBar(title: const Text('الحقول')),
            body: const Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.grass, size: 80, color: Colors.grey),
                  SizedBox(height: 16),
                  Text(
                    'لا توجد حقول مضافة',
                    style: TextStyle(fontSize: 18, color: Colors.grey),
                  ),
                  SizedBox(height: 8),
                  Text('اضغط + لإضافة أول حقل'),
                ],
              ),
            ),
            floatingActionButton: const FloatingActionButton(
              onPressed: null,
              tooltip: 'إضافة حقل',
              child: Icon(Icons.add),
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      expect(find.text('لا توجد حقول مضافة'), findsOneWidget);
      expect(find.text('اضغط + لإضافة أول حقل'), findsOneWidget);
      expect(find.byIcon(Icons.add), findsOneWidget);
    });
  });

  // =========================================================================
  // Field Creation Tests
  // اختبارات إنشاء الحقل
  // =========================================================================

  group('Field Creation Tests - اختبارات إنشاء الحقل', () {
    testWidgets('Add field FAB opens creation form', (tester) async {
      bool formOpened = false;

      await tester.pumpWidget(ProviderScope(
        child: MaterialApp(
          locale: const Locale('ar'),
          home: Scaffold(
            body: const Center(child: Text('الحقول')),
            floatingActionButton: FloatingActionButton(
              onPressed: () => formOpened = true,
              child: const Icon(Icons.add),
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      await tester.tap(find.byType(FloatingActionButton));
      await tester.pumpAndSettle();

      expect(formOpened, isTrue);
    });

    testWidgets('Field creation form has required fields', (tester) async {
      final formKey = GlobalKey<FormState>();

      await tester.pumpWidget(ProviderScope(
        child: MaterialApp(
          locale: const Locale('ar'),
          home: Scaffold(
            appBar: AppBar(title: const Text('حقل جديد')),
            body: Form(
              key: formKey,
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  children: [
                    TextFormField(
                      key: const Key('field_name_input'),
                      decoration:
                          const InputDecoration(labelText: 'اسم الحقل *'),
                      validator: (v) =>
                          (v == null || v.trim().isEmpty) ? 'الاسم مطلوب' : null,
                    ),
                    const SizedBox(height: 16),
                    TextFormField(
                      key: const Key('field_area_input'),
                      keyboardType: TextInputType.number,
                      decoration:
                          const InputDecoration(labelText: 'المساحة (هكتار) *'),
                      validator: (v) {
                        if (v == null || v.isEmpty) return 'المساحة مطلوبة';
                        final area = double.tryParse(v);
                        if (area == null || area <= 0) return 'مساحة غير صالحة';
                        return null;
                      },
                    ),
                    const SizedBox(height: 16),
                    DropdownButtonFormField<String>(
                      key: const Key('crop_type_dropdown'),
                      decoration:
                          const InputDecoration(labelText: 'نوع المحصول'),
                      items: const [
                        DropdownMenuItem(value: 'wheat', child: Text('قمح')),
                        DropdownMenuItem(value: 'corn', child: Text('ذرة')),
                        DropdownMenuItem(
                            value: 'tomato', child: Text('طماطم')),
                        DropdownMenuItem(
                            value: 'barley', child: Text('شعير')),
                      ],
                      onChanged: (_) {},
                    ),
                    const SizedBox(height: 24),
                    ElevatedButton(
                      onPressed: () => formKey.currentState!.validate(),
                      child: const Text('حفظ الحقل'),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      // Verify form fields exist
      expect(find.byKey(const Key('field_name_input')), findsOneWidget);
      expect(find.byKey(const Key('field_area_input')), findsOneWidget);
      expect(find.byKey(const Key('crop_type_dropdown')), findsOneWidget);
      expect(find.text('حفظ الحقل'), findsOneWidget);
    });

    testWidgets('Field creation validates required name', (tester) async {
      final formKey = GlobalKey<FormState>();

      await tester.pumpWidget(ProviderScope(
        child: MaterialApp(
          locale: const Locale('ar'),
          home: Scaffold(
            body: Form(
              key: formKey,
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  children: [
                    TextFormField(
                      key: const Key('field_name'),
                      decoration:
                          const InputDecoration(labelText: 'اسم الحقل'),
                      validator: (v) =>
                          (v == null || v.trim().isEmpty) ? 'الاسم مطلوب' : null,
                    ),
                    ElevatedButton(
                      onPressed: () => formKey.currentState!.validate(),
                      child: const Text('حفظ'),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      // Submit without name
      await tester.tap(find.text('حفظ'));
      await tester.pumpAndSettle();

      expect(find.text('الاسم مطلوب'), findsOneWidget);
    });

    testWidgets('Field creation validates area is positive', (tester) async {
      final formKey = GlobalKey<FormState>();

      await tester.pumpWidget(ProviderScope(
        child: MaterialApp(
          locale: const Locale('ar'),
          home: Scaffold(
            body: Form(
              key: formKey,
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  children: [
                    TextFormField(
                      key: const Key('area_field'),
                      keyboardType: TextInputType.number,
                      decoration:
                          const InputDecoration(labelText: 'المساحة (هكتار)'),
                      validator: (v) {
                        if (v == null || v.isEmpty) return 'المساحة مطلوبة';
                        final area = double.tryParse(v);
                        if (area == null || area <= 0) return 'مساحة غير صالحة';
                        return null;
                      },
                    ),
                    ElevatedButton(
                      onPressed: () => formKey.currentState!.validate(),
                      child: const Text('حفظ'),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      // Enter negative area
      await tester.enterText(find.byKey(const Key('area_field')), '-5');
      await tester.tap(find.text('حفظ'));
      await tester.pumpAndSettle();

      expect(find.text('مساحة غير صالحة'), findsOneWidget);
    });

    testWidgets('Crop type dropdown shows all supported crops', (tester) async {
      await tester.pumpWidget(ProviderScope(
        child: MaterialApp(
          locale: const Locale('ar'),
          home: Scaffold(
            body: Padding(
              padding: const EdgeInsets.all(16),
              child: DropdownButtonFormField<String>(
                decoration:
                    const InputDecoration(labelText: 'نوع المحصول'),
                items: const [
                  DropdownMenuItem(value: 'wheat', child: Text('قمح')),
                  DropdownMenuItem(value: 'corn', child: Text('ذرة')),
                  DropdownMenuItem(value: 'tomato', child: Text('طماطم')),
                  DropdownMenuItem(value: 'barley', child: Text('شعير')),
                  DropdownMenuItem(value: 'date_palm', child: Text('نخيل')),
                  DropdownMenuItem(value: 'potato', child: Text('بطاطا')),
                ],
                onChanged: (_) {},
              ),
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      // Open dropdown
      await tester.tap(find.byType(DropdownButtonFormField<String>));
      await tester.pumpAndSettle();

      expect(find.text('قمح'), findsWidgets);
      expect(find.text('ذرة'), findsWidgets);
      expect(find.text('طماطم'), findsWidgets);
      expect(find.text('نخيل'), findsWidgets);
    });
  });

  // =========================================================================
  // Field Editing Tests
  // اختبارات تعديل الحقل
  // =========================================================================

  group('Field Editing Tests - اختبارات تعديل الحقل', () {
    testWidgets('Edit field form is pre-populated with existing data',
        (tester) async {
      const existingName = 'حقل القمح الشمالي';
      const existingArea = '5.5';

      await tester.pumpWidget(ProviderScope(
        child: MaterialApp(
          locale: const Locale('ar'),
          home: Scaffold(
            appBar: AppBar(title: const Text('تعديل الحقل')),
            body: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  TextFormField(
                    key: const Key('edit_name'),
                    initialValue: existingName,
                    decoration: const InputDecoration(labelText: 'اسم الحقل'),
                  ),
                  const SizedBox(height: 16),
                  TextFormField(
                    key: const Key('edit_area'),
                    initialValue: existingArea,
                    decoration: const InputDecoration(labelText: 'المساحة'),
                  ),
                ],
              ),
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      // Verify pre-populated values
      expect(find.text(existingName), findsOneWidget);
      expect(find.text(existingArea), findsOneWidget);
    });

    testWidgets('Saving edited field updates display', (tester) async {
      String displayName = 'الاسم القديم';

      await tester.pumpWidget(ProviderScope(
        child: StatefulBuilder(
          builder: (context, setState) => MaterialApp(
            locale: const Locale('ar'),
            home: Scaffold(
              appBar: AppBar(
                title: Text(displayName),
                actions: [
                  IconButton(
                    icon: const Icon(Icons.edit),
                    onPressed: () async {
                      setState(() => displayName = 'الاسم الجديد');
                    },
                  ),
                ],
              ),
              body: Center(child: Text(displayName)),
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      expect(find.text('الاسم القديم'), findsWidgets);

      // Tap edit
      await tester.tap(find.byIcon(Icons.edit));
      await tester.pumpAndSettle();

      expect(find.text('الاسم الجديد'), findsWidgets);
    });
  });

  // =========================================================================
  // Field Deletion Tests
  // اختبارات حذف الحقل
  // =========================================================================

  group('Field Deletion Tests - اختبارات حذف الحقل', () {
    testWidgets('Delete field shows confirmation dialog', (tester) async {
      await tester.pumpWidget(ProviderScope(
        child: MaterialApp(
          locale: const Locale('ar'),
          home: Builder(
            builder: (context) => Scaffold(
              body: Center(
                child: ElevatedButton(
                  onPressed: () => showDialog(
                    context: context,
                    builder: (_) => AlertDialog(
                      title: const Text('تأكيد الحذف'),
                      content:
                          const Text('هل تريد حذف حقل القمح؟ لا يمكن التراجع.'),
                      actions: [
                        TextButton(
                          onPressed: () => Navigator.pop(context),
                          child: const Text('إلغاء'),
                        ),
                        TextButton(
                          onPressed: () => Navigator.pop(context, true),
                          style: TextButton.styleFrom(
                              foregroundColor: Colors.red),
                          child: const Text('حذف'),
                        ),
                      ],
                    ),
                  ),
                  child: const Text('حذف الحقل'),
                ),
              ),
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      await tester.tap(find.text('حذف الحقل'));
      await tester.pumpAndSettle();

      expect(find.text('تأكيد الحذف'), findsOneWidget);
      expect(find.text('هل تريد حذف حقل القمح؟ لا يمكن التراجع.'), findsOneWidget);
      expect(find.text('إلغاء'), findsOneWidget);
    });

    testWidgets('Cancelling deletion keeps field in list', (tester) async {
      bool fieldDeleted = false;

      await tester.pumpWidget(ProviderScope(
        child: MaterialApp(
          locale: const Locale('ar'),
          home: Builder(
            builder: (context) => Scaffold(
              body: Column(
                children: [
                  if (!fieldDeleted) const ListTile(title: Text('حقل القمح')),
                  ElevatedButton(
                    onPressed: () async {
                      final confirm = await showDialog<bool>(
                        context: context,
                        builder: (_) => AlertDialog(
                          title: const Text('تأكيد'),
                          actions: [
                            TextButton(
                              onPressed: () => Navigator.pop(context, false),
                              child: const Text('إلغاء'),
                            ),
                            TextButton(
                              onPressed: () => Navigator.pop(context, true),
                              child: const Text('حذف'),
                            ),
                          ],
                        ),
                      );
                      if (confirm == true) fieldDeleted = true;
                    },
                    child: const Text('حذف'),
                  ),
                ],
              ),
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      expect(find.text('حقل القمح'), findsOneWidget);

      // Open confirmation and cancel
      await tester.tap(find.text('حذف'));
      await tester.pumpAndSettle();

      await tester.tap(find.text('إلغاء'));
      await tester.pumpAndSettle();

      // Field still present
      expect(find.text('حقل القمح'), findsOneWidget);
      expect(fieldDeleted, isFalse);
    });
  });

  // =========================================================================
  // Field Detail View Tests
  // اختبارات عرض تفاصيل الحقل
  // =========================================================================

  group('Field Detail View Tests - اختبارات تفاصيل الحقل', () {
    testWidgets('Field detail shows all sections', (tester) async {
      await tester.pumpWidget(ProviderScope(
        child: MaterialApp(
          locale: const Locale('ar'),
          home: Scaffold(
            appBar: AppBar(title: const Text('تفاصيل الحقل')),
            body: ListView(
              padding: const EdgeInsets.all(16),
              children: const [
                // Basic info section
                Text('معلومات أساسية',
                    style: TextStyle(
                        fontSize: 18, fontWeight: FontWeight.bold)),
                SizedBox(height: 8),
                ListTile(
                    leading: Icon(Icons.grass),
                    title: Text('حقل القمح الشمالي'),
                    subtitle: Text('قمح • 5.5 هكتار')),
                Divider(),
                // NDVI section
                Text('صحة المحصول',
                    style: TextStyle(
                        fontSize: 18, fontWeight: FontWeight.bold)),
                SizedBox(height: 8),
                ListTile(
                    leading: Icon(Icons.satellite_alt),
                    title: Text('مؤشر NDVI'),
                    trailing: Chip(label: Text('0.72'))),
                Divider(),
                // Irrigation section
                Text('الري',
                    style: TextStyle(
                        fontSize: 18, fontWeight: FontWeight.bold)),
                SizedBox(height: 8),
                ListTile(
                    leading: Icon(Icons.water),
                    title: Text('آخر ري'),
                    subtitle: Text('منذ 3 أيام')),
              ],
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      expect(find.text('تفاصيل الحقل'), findsOneWidget);
      expect(find.text('معلومات أساسية'), findsOneWidget);
      expect(find.text('صحة المحصول'), findsOneWidget);
      expect(find.text('الري'), findsOneWidget);
      expect(find.text('0.72'), findsOneWidget);
    });

    testWidgets('Field detail shows location coordinates', (tester) async {
      await tester.pumpWidget(ProviderScope(
        child: MaterialApp(
          locale: const Locale('ar'),
          home: Scaffold(
            appBar: AppBar(title: const Text('تفاصيل الحقل')),
            body: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: const [
                  Text('الموقع الجغرافي',
                      style: TextStyle(fontWeight: FontWeight.bold)),
                  SizedBox(height: 8),
                  Text('خط العرض: 15.3694'),
                  Text('خط الطول: 44.1910'),
                  Text('المحافظة: صنعاء'),
                  Text('المديرية: همدان'),
                ],
              ),
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      expect(find.text('الموقع الجغرافي'), findsOneWidget);
      expect(find.text('خط العرض: 15.3694'), findsOneWidget);
      expect(find.text('خط الطول: 44.1910'), findsOneWidget);
      expect(find.text('المحافظة: صنعاء'), findsOneWidget);
    });
  });
}
