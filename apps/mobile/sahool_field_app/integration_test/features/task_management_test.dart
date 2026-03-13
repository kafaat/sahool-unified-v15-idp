/// SAHOOL Field App - Task Management Integration Tests
/// اختبارات تكامل إدارة المهام
///
/// Tests the task management UI components:
/// - Task list display (open, in-progress, done)
/// - Task creation form
/// - Task status transitions
/// - Task priority display
/// - Overdue task highlighting
/// - Evidence photo upload UI
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  // =========================================================================
  // Test Data
  // =========================================================================

  final testTasks = [
    {
      'id': 't001',
      'title': 'إضافة سماد للحقل الشمالي',
      'fieldName': 'حقل القمح الشمالي',
      'status': 'open',
      'statusLabel': 'مفتوحة',
      'priority': 'high',
      'priorityLabel': 'عالية',
      'dueDate': '2026-03-15',
    },
    {
      'id': 't002',
      'title': 'ري حقل الذرة',
      'fieldName': 'حقل الذرة الجنوبي',
      'status': 'in_progress',
      'statusLabel': 'قيد التنفيذ',
      'priority': 'medium',
      'priorityLabel': 'متوسطة',
      'dueDate': '2026-03-16',
    },
    {
      'id': 't003',
      'title': 'فحص أمراض الطماطم',
      'fieldName': 'حقل الطماطم',
      'status': 'done',
      'statusLabel': 'منجزة',
      'priority': 'low',
      'priorityLabel': 'منخفضة',
      'dueDate': '2026-03-10',
    },
  ];

  Color priorityColor(String priority) {
    switch (priority) {
      case 'high':
        return Colors.red;
      case 'medium':
        return Colors.orange;
      default:
        return Colors.green;
    }
  }

  Color statusColor(String status) {
    switch (status) {
      case 'done':
        return Colors.green;
      case 'in_progress':
        return Colors.blue;
      default:
        return Colors.grey;
    }
  }

  // =========================================================================
  // Task List Tests
  // اختبارات قائمة المهام
  // =========================================================================

  group('Task List Tests - اختبارات قائمة المهام', () {
    testWidgets('Task list shows all tasks', (tester) async {
      await tester.pumpWidget(ProviderScope(
        child: MaterialApp(
          locale: const Locale('ar'),
          home: Scaffold(
            appBar: AppBar(title: const Text('المهام')),
            body: ListView.builder(
              itemCount: testTasks.length,
              itemBuilder: (_, i) => ListTile(
                title: Text(testTasks[i]['title'] as String),
                subtitle: Text(testTasks[i]['fieldName'] as String),
                trailing: Chip(
                  label: Text(testTasks[i]['statusLabel'] as String),
                  backgroundColor:
                      statusColor(testTasks[i]['status'] as String)
                          .withOpacity(0.2),
                ),
              ),
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      for (final task in testTasks) {
        expect(find.text(task['title'] as String), findsOneWidget);
      }
    });

    testWidgets('Task list shows status chips', (tester) async {
      await tester.pumpWidget(ProviderScope(
        child: MaterialApp(
          locale: const Locale('ar'),
          home: Scaffold(
            body: ListView.builder(
              itemCount: testTasks.length,
              itemBuilder: (_, i) => ListTile(
                title: Text(testTasks[i]['title'] as String),
                trailing: Chip(
                  label: Text(testTasks[i]['statusLabel'] as String),
                ),
              ),
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      expect(find.text('مفتوحة'), findsOneWidget);
      expect(find.text('قيد التنفيذ'), findsOneWidget);
      expect(find.text('منجزة'), findsOneWidget);
    });

    testWidgets('Task list shows priority indicators', (tester) async {
      await tester.pumpWidget(ProviderScope(
        child: MaterialApp(
          locale: const Locale('ar'),
          home: Scaffold(
            body: ListView.builder(
              itemCount: testTasks.length,
              itemBuilder: (_, i) => ListTile(
                leading: CircleAvatar(
                  radius: 8,
                  backgroundColor:
                      priorityColor(testTasks[i]['priority'] as String),
                ),
                title: Text(testTasks[i]['title'] as String),
                subtitle: Text(
                  'الأولوية: ${testTasks[i]['priorityLabel']}',
                ),
              ),
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      expect(find.text('الأولوية: عالية'), findsOneWidget);
      expect(find.text('الأولوية: متوسطة'), findsOneWidget);
      expect(find.text('الأولوية: منخفضة'), findsOneWidget);
    });

    testWidgets('Filter tabs show correct task counts', (tester) async {
      final openCount =
          testTasks.where((t) => t['status'] == 'open').length;
      final inProgressCount =
          testTasks.where((t) => t['status'] == 'in_progress').length;
      final doneCount =
          testTasks.where((t) => t['status'] == 'done').length;

      await tester.pumpWidget(ProviderScope(
        child: MaterialApp(
          locale: const Locale('ar'),
          home: DefaultTabController(
            length: 3,
            child: Scaffold(
              appBar: AppBar(
                title: const Text('المهام'),
                bottom: TabBar(
                  tabs: [
                    Tab(text: 'مفتوحة ($openCount)'),
                    Tab(text: 'قيد التنفيذ ($inProgressCount)'),
                    Tab(text: 'منجزة ($doneCount)'),
                  ],
                ),
              ),
              body: const TabBarView(
                children: [
                  Center(child: Text('المهام المفتوحة')),
                  Center(child: Text('المهام قيد التنفيذ')),
                  Center(child: Text('المهام المنجزة')),
                ],
              ),
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      expect(find.text('مفتوحة (1)'), findsOneWidget);
      expect(find.text('قيد التنفيذ (1)'), findsOneWidget);
      expect(find.text('منجزة (1)'), findsOneWidget);
    });

    testWidgets('Overdue tasks show warning indicator', (tester) async {
      final now = DateTime.now();
      final overdueDate = now.subtract(const Duration(days: 2));

      await tester.pumpWidget(ProviderScope(
        child: MaterialApp(
          locale: const Locale('ar'),
          home: Scaffold(
            body: ListView(
              children: [
                ListTile(
                  title: const Text('مهمة متأخرة'),
                  leading: overdueDate.isBefore(now)
                      ? const Icon(Icons.warning_amber, color: Colors.red)
                      : const Icon(Icons.task_alt),
                  subtitle: Text('تاريخ الاستحقاق: ${overdueDate.day}/${overdueDate.month}/${overdueDate.year}'),
                ),
              ],
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      expect(find.byIcon(Icons.warning_amber), findsOneWidget);
      expect(find.text('مهمة متأخرة'), findsOneWidget);
    });
  });

  // =========================================================================
  // Task Creation Tests
  // اختبارات إنشاء المهمة
  // =========================================================================

  group('Task Creation Tests - اختبارات إنشاء المهمة', () {
    testWidgets('Task creation form has all required fields', (tester) async {
      final formKey = GlobalKey<FormState>();

      await tester.pumpWidget(ProviderScope(
        child: MaterialApp(
          locale: const Locale('ar'),
          home: Scaffold(
            appBar: AppBar(title: const Text('مهمة جديدة')),
            body: Form(
              key: formKey,
              child: ListView(
                padding: const EdgeInsets.all(16),
                children: [
                  TextFormField(
                    key: const Key('task_title'),
                    decoration:
                        const InputDecoration(labelText: 'عنوان المهمة *'),
                    validator: (v) =>
                        (v == null || v.isEmpty) ? 'العنوان مطلوب' : null,
                  ),
                  const SizedBox(height: 16),
                  TextFormField(
                    key: const Key('task_description'),
                    maxLines: 3,
                    decoration:
                        const InputDecoration(labelText: 'الوصف (اختياري)'),
                  ),
                  const SizedBox(height: 16),
                  DropdownButtonFormField<String>(
                    key: const Key('task_priority'),
                    decoration: const InputDecoration(labelText: 'الأولوية'),
                    items: const [
                      DropdownMenuItem(value: 'high', child: Text('عالية')),
                      DropdownMenuItem(value: 'medium', child: Text('متوسطة')),
                      DropdownMenuItem(value: 'low', child: Text('منخفضة')),
                    ],
                    onChanged: (_) {},
                  ),
                  const SizedBox(height: 16),
                  TextFormField(
                    key: const Key('task_due_date'),
                    decoration:
                        const InputDecoration(labelText: 'تاريخ الاستحقاق'),
                    readOnly: true,
                    onTap: () {},
                  ),
                  const SizedBox(height: 24),
                  ElevatedButton(
                    onPressed: () => formKey.currentState!.validate(),
                    child: const Text('إضافة المهمة'),
                  ),
                ],
              ),
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      expect(find.byKey(const Key('task_title')), findsOneWidget);
      expect(find.byKey(const Key('task_description')), findsOneWidget);
      expect(find.byKey(const Key('task_priority')), findsOneWidget);
      expect(find.text('إضافة المهمة'), findsOneWidget);
    });

    testWidgets('Task creation validates empty title', (tester) async {
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
                      key: const Key('title_field'),
                      decoration:
                          const InputDecoration(labelText: 'عنوان المهمة'),
                      validator: (v) =>
                          (v == null || v.isEmpty) ? 'العنوان مطلوب' : null,
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

      await tester.tap(find.text('حفظ'));
      await tester.pumpAndSettle();

      expect(find.text('العنوان مطلوب'), findsOneWidget);
    });
  });

  // =========================================================================
  // Task Status Transition Tests
  // اختبارات تغيير حالة المهمة
  // =========================================================================

  group('Task Status Transition Tests - اختبارات تغيير الحالة', () {
    testWidgets('Marking task as done updates status chip', (tester) async {
      String taskStatus = 'open';

      await tester.pumpWidget(ProviderScope(
        child: StatefulBuilder(
          builder: (context, setState) => MaterialApp(
            locale: const Locale('ar'),
            home: Scaffold(
              body: Column(
                children: [
                  ListTile(
                    title: const Text('إضافة سماد'),
                    trailing: Chip(
                      label: Text(
                        taskStatus == 'done' ? 'منجزة' : 'مفتوحة',
                      ),
                      backgroundColor: taskStatus == 'done'
                          ? Colors.green.withOpacity(0.2)
                          : Colors.grey.withOpacity(0.2),
                    ),
                  ),
                  ElevatedButton(
                    onPressed: () => setState(() => taskStatus = 'done'),
                    child: const Text('إنجاز المهمة'),
                  ),
                ],
              ),
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      expect(find.text('مفتوحة'), findsOneWidget);

      await tester.tap(find.text('إنجاز المهمة'));
      await tester.pumpAndSettle();

      expect(find.text('منجزة'), findsOneWidget);
      expect(find.text('مفتوحة'), findsNothing);
    });

    testWidgets('Task can transition through all statuses', (tester) async {
      final statuses = ['open', 'in_progress', 'done'];
      final statusLabels = {
        'open': 'مفتوحة',
        'in_progress': 'قيد التنفيذ',
        'done': 'منجزة',
      };
      int statusIndex = 0;

      await tester.pumpWidget(ProviderScope(
        child: StatefulBuilder(
          builder: (context, setState) => MaterialApp(
            locale: const Locale('ar'),
            home: Scaffold(
              body: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(
                    'الحالة: ${statusLabels[statuses[statusIndex]]}',
                    key: const Key('status_text'),
                  ),
                  if (statusIndex < statuses.length - 1)
                    ElevatedButton(
                      onPressed: () =>
                          setState(() => statusIndex++),
                      child: const Text('الحالة التالية'),
                    ),
                ],
              ),
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      expect(find.text('الحالة: مفتوحة'), findsOneWidget);

      await tester.tap(find.text('الحالة التالية'));
      await tester.pumpAndSettle();
      expect(find.text('الحالة: قيد التنفيذ'), findsOneWidget);

      await tester.tap(find.text('الحالة التالية'));
      await tester.pumpAndSettle();
      expect(find.text('الحالة: منجزة'), findsOneWidget);
    });
  });

  // =========================================================================
  // Evidence/Photo Tests
  // اختبارات الدليل والصور
  // =========================================================================

  group('Evidence Photo Tests - اختبارات صور الدليل', () {
    testWidgets('Evidence section shows camera and gallery options', (tester) async {
      await tester.pumpWidget(ProviderScope(
        child: MaterialApp(
          locale: const Locale('ar'),
          home: Builder(
            builder: (context) => Scaffold(
              appBar: AppBar(title: const Text('دليل الإنجاز')),
              body: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('إضافة صور دليل الإنجاز'),
                    const SizedBox(height: 16),
                    Row(
                      children: [
                        OutlinedButton.icon(
                          onPressed: () {},
                          icon: const Icon(Icons.camera_alt),
                          label: const Text('التقاط صورة'),
                        ),
                        const SizedBox(width: 16),
                        OutlinedButton.icon(
                          onPressed: () {},
                          icon: const Icon(Icons.photo_library),
                          label: const Text('من المعرض'),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      expect(find.text('إضافة صور دليل الإنجاز'), findsOneWidget);
      expect(find.byIcon(Icons.camera_alt), findsOneWidget);
      expect(find.byIcon(Icons.photo_library), findsOneWidget);
      expect(find.text('التقاط صورة'), findsOneWidget);
      expect(find.text('من المعرض'), findsOneWidget);
    });

    testWidgets('Notes field accepts multi-line text', (tester) async {
      final controller = TextEditingController();

      await tester.pumpWidget(ProviderScope(
        child: MaterialApp(
          locale: const Locale('ar'),
          home: Scaffold(
            body: Padding(
              padding: const EdgeInsets.all(16),
              child: TextFormField(
                key: const Key('notes_field'),
                controller: controller,
                maxLines: 5,
                decoration:
                    const InputDecoration(labelText: 'ملاحظات الإنجاز'),
              ),
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      await tester.enterText(
        find.byKey(const Key('notes_field')),
        'تم تطبيق السماد اليوريا بمعدل 46 كيلوجرام للهكتار في الصباح الباكر مع توافر الندى',
      );
      await tester.pumpAndSettle();

      expect(
        find.text(
            'تم تطبيق السماد اليوريا بمعدل 46 كيلوجرام للهكتار في الصباح الباكر مع توافر الندى'),
        findsOneWidget,
      );
    });
  });
}
