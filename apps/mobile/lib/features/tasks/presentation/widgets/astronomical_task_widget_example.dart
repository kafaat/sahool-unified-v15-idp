/// SAHOOL Astronomical Task Widget - Usage Example
/// مثال على استخدام ويدجت المهام الفلكية
///
/// هذا الملف يوضح كيفية دمج ويدجت المهام الفلكية في التطبيق

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'astronomical_task_widget.dart';

// ═══════════════════════════════════════════════════════════════════════════════
// مثال 1: عرض الويدجت كـ Bottom Sheet
// ═══════════════════════════════════════════════════════════════════════════════

/// عرض ويدجت المهام الفلكية كـ Bottom Sheet
void showAstronomicalTaskSheet(BuildContext context, {String? fieldId, String? fieldName}) {
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

// ═══════════════════════════════════════════════════════════════════════════════
// مثال 2: دمج في شاشة المهام
// ═══════════════════════════════════════════════════════════════════════════════

class TasksScreenWithAstronomical extends ConsumerWidget {
  final String? fieldId;
  final String? fieldName;

  const TasksScreenWithAstronomical({
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
          // زر فتح التقويم الفلكي
          IconButton(
            icon: const Icon(Icons.auto_awesome),
            tooltip: 'التقويم الفلكي',
            onPressed: () => showAstronomicalTaskSheet(
              context,
              fieldId: fieldId,
              fieldName: fieldName,
            ),
          ),
        ],
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.task_alt, size: 80, color: Colors.grey),
            const SizedBox(height: 16),
            const Text('قائمة المهام'),
            const SizedBox(height: 32),
            ElevatedButton.icon(
              onPressed: () => showAstronomicalTaskSheet(
                context,
                fieldId: fieldId,
                fieldName: fieldName,
              ),
              icon: const Icon(Icons.auto_awesome),
              label: const Text('إنشاء مهمة حسب التقويم الفلكي'),
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF367C2B),
                padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// مثال 3: دمج كتبويب في شاشة الحقل
// ═══════════════════════════════════════════════════════════════════════════════

class FieldDetailScreenWithAstro extends ConsumerWidget {
  final String fieldId;
  final String fieldName;

  const FieldDetailScreenWithAstro({
    super.key,
    required this.fieldId,
    required this.fieldName,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
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
              Tab(icon: Icon(Icons.auto_awesome), text: 'التقويم الفلكي'),
              Tab(icon: Icon(Icons.analytics), text: 'الإحصائيات'),
            ],
          ),
        ),
        body: TabBarView(
          children: [
            // تبويب المعلومات
            const Center(child: Text('معلومات الحقل')),

            // تبويب المهام
            const Center(child: Text('قائمة المهام')),

            // تبويب التقويم الفلكي
            AstronomicalTaskWidget(
              fieldId: fieldId,
              fieldName: fieldName,
            ),

            // تبويب الإحصائيات
            const Center(child: Text('الإحصائيات')),
          ],
        ),
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// مثال 4: عرض كشاشة منفصلة
// ═══════════════════════════════════════════════════════════════════════════════

class AstronomicalTaskScreen extends ConsumerWidget {
  final String? fieldId;
  final String? fieldName;

  const AstronomicalTaskScreen({
    super.key,
    this.fieldId,
    this.fieldName,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      body: AstronomicalTaskWidget(
        fieldId: fieldId,
        fieldName: fieldName,
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// مثال 5: استخدام في قائمة الحقول مع FAB
// ═══════════════════════════════════════════════════════════════════════════════

class FieldsListScreenWithAstro extends ConsumerWidget {
  const FieldsListScreenWithAstro({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('الحقول'),
      ),
      body: ListView.builder(
        itemCount: 10, // مثال
        itemBuilder: (context, index) {
          return ListTile(
            leading: const Icon(Icons.landscape),
            title: Text('حقل ${index + 1}'),
            subtitle: const Text('القمح'),
            trailing: IconButton(
              icon: const Icon(Icons.auto_awesome),
              tooltip: 'التقويم الفلكي',
              onPressed: () => showAstronomicalTaskSheet(
                context,
                fieldId: 'field_${index + 1}',
                fieldName: 'حقل ${index + 1}',
              ),
            ),
          );
        },
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => showAstronomicalTaskSheet(context),
        icon: const Icon(Icons.auto_awesome),
        label: const Text('التقويم الفلكي'),
        backgroundColor: const Color(0xFF367C2B),
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// مثال 6: دمج في شاشة إنشاء المهمة
// ═══════════════════════════════════════════════════════════════════════════════

class CreateTaskScreenWithAstro extends ConsumerWidget {
  final String? fieldId;
  final String? fieldName;

  const CreateTaskScreenWithAstro({
    super.key,
    this.fieldId,
    this.fieldName,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('مهمة جديدة'),
        actions: [
          // زر الاقتراحات الفلكية
          TextButton.icon(
            onPressed: () => showAstronomicalTaskSheet(
              context,
              fieldId: fieldId,
              fieldName: fieldName,
            ),
            icon: const Icon(Icons.auto_awesome, color: Colors.white),
            label: const Text(
              'اقتراحات فلكية',
              style: TextStyle(color: Colors.white),
            ),
          ),
        ],
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.auto_awesome, size: 80, color: Color(0xFF367C2B)),
            const SizedBox(height: 16),
            const Text(
              'اختر التاريخ المناسب حسب التقويم الفلكي',
              style: TextStyle(fontSize: 16),
            ),
            const SizedBox(height: 32),
            ElevatedButton.icon(
              onPressed: () => showAstronomicalTaskSheet(
                context,
                fieldId: fieldId,
                fieldName: fieldName,
              ),
              icon: const Icon(Icons.calendar_month),
              label: const Text('عرض التقويم الفلكي'),
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF367C2B),
                padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
