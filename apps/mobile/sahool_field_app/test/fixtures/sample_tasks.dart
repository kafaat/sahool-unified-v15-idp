/// Sample Tasks Data for Testing
/// بيانات المهام النموذجية للاختبارات

import 'package:sahool_field_app/core/storage/database.dart';
import 'package:drift/drift.dart';

/// Extension to help with Task entity copying in tests
extension TaskCopyWith on Task {
  Task copyWith({
    String? id,
    String? tenantId,
    String? fieldId,
    String? farmId,
    String? title,
    String? description,
    String? status,
    String? priority,
    DateTime? dueDate,
    String? assignedTo,
    String? evidenceNotes,
    String? evidencePhotos,
    DateTime? createdAt,
    DateTime? updatedAt,
    bool? synced,
  }) {
    return Task(
      id: id ?? this.id,
      tenantId: tenantId ?? this.tenantId,
      fieldId: fieldId ?? this.fieldId,
      farmId: farmId ?? this.farmId,
      title: title ?? this.title,
      description: description ?? this.description,
      status: status ?? this.status,
      priority: priority ?? this.priority,
      dueDate: dueDate ?? this.dueDate,
      assignedTo: assignedTo ?? this.assignedTo,
      evidenceNotes: evidenceNotes ?? this.evidenceNotes,
      evidencePhotos: evidencePhotos ?? this.evidencePhotos,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      synced: synced ?? this.synced,
    );
  }
}

class SampleTasks {
  /// Sample pending task
  static Task createPendingTask({
    String? id,
    String tenantId = 'tenant_test',
    String fieldId = 'field_001',
  }) {
    return Task(
      id: id ?? 'task_pending_001',
      tenantId: tenantId,
      fieldId: fieldId,
      farmId: 'farm_001',
      title: 'ري الحقل الشمالي',
      description: 'ري الحقل بكمية 500 لتر ماء',
      status: 'open',
      priority: 'high',
      dueDate: DateTime.now().add(const Duration(days: 2)),
      assignedTo: 'user_001',
      evidenceNotes: null,
      evidencePhotos: null,
      createdAt: DateTime.now().subtract(const Duration(days: 1)),
      updatedAt: DateTime.now().subtract(const Duration(days: 1)),
      synced: true,
    );
  }

  /// Sample in-progress task
  static Task createInProgressTask({
    String? id,
    String tenantId = 'tenant_test',
    String fieldId = 'field_001',
  }) {
    return Task(
      id: id ?? 'task_progress_001',
      tenantId: tenantId,
      fieldId: fieldId,
      farmId: 'farm_001',
      title: 'تسميد البيت المحمي',
      description: 'استخدام السماد العضوي NPK',
      status: 'in_progress',
      priority: 'medium',
      dueDate: DateTime.now().add(const Duration(days: 1)),
      assignedTo: 'user_001',
      evidenceNotes: 'تم البدء بالعمل',
      evidencePhotos: null,
      createdAt: DateTime.now().subtract(const Duration(days: 3)),
      updatedAt: DateTime.now(),
      synced: false,
    );
  }

  /// Sample completed task
  static Task createCompletedTask({
    String? id,
    String tenantId = 'tenant_test',
    String fieldId = 'field_001',
  }) {
    return Task(
      id: id ?? 'task_done_001',
      tenantId: tenantId,
      fieldId: fieldId,
      farmId: 'farm_001',
      title: 'حصاد القمح',
      description: 'حصاد محصول القمح من الحقل الجنوبي',
      status: 'done',
      priority: 'high',
      dueDate: DateTime.now().subtract(const Duration(days: 1)),
      assignedTo: 'user_001',
      evidenceNotes: 'تم الحصاد بنجاح',
      evidencePhotos: 'photo1.jpg,photo2.jpg',
      createdAt: DateTime.now().subtract(const Duration(days: 7)),
      updatedAt: DateTime.now().subtract(const Duration(hours: 2)),
      synced: true,
    );
  }

  /// Sample overdue task
  static Task createOverdueTask({
    String? id,
    String tenantId = 'tenant_test',
    String fieldId = 'field_002',
  }) {
    return Task(
      id: id ?? 'task_overdue_001',
      tenantId: tenantId,
      fieldId: fieldId,
      farmId: 'farm_001',
      title: 'مكافحة الآفات',
      description: 'رش المبيدات الحشرية',
      status: 'open',
      priority: 'urgent',
      dueDate: DateTime.now().subtract(const Duration(days: 2)),
      assignedTo: 'user_001',
      evidenceNotes: null,
      evidencePhotos: null,
      createdAt: DateTime.now().subtract(const Duration(days: 5)),
      updatedAt: DateTime.now().subtract(const Duration(days: 5)),
      synced: true,
    );
  }

  /// Sample unsynced task
  static Task createUnsyncedTask({
    String? id,
    String tenantId = 'tenant_test',
    String fieldId = 'field_001',
  }) {
    return Task(
      id: id ?? 'task_unsynced_001',
      tenantId: tenantId,
      fieldId: fieldId,
      farmId: 'farm_001',
      title: 'فحص نظام الري',
      description: 'التأكد من سلامة أنابيب الري',
      status: 'open',
      priority: 'low',
      dueDate: DateTime.now().add(const Duration(days: 5)),
      assignedTo: 'user_001',
      evidenceNotes: null,
      evidencePhotos: null,
      createdAt: DateTime.now(),
      updatedAt: DateTime.now(),
      synced: false,
    );
  }

  /// Create list of sample tasks
  static List<Task> createSampleTaskList({
    String tenantId = 'tenant_test',
    String fieldId = 'field_001',
  }) {
    return [
      createPendingTask(tenantId: tenantId, fieldId: fieldId),
      createInProgressTask(tenantId: tenantId, fieldId: fieldId),
      createCompletedTask(tenantId: tenantId, fieldId: fieldId),
      createOverdueTask(tenantId: tenantId, fieldId: fieldId),
      createUnsyncedTask(tenantId: tenantId, fieldId: fieldId),
    ];
  }

  /// Create TasksCompanion for insertion
  static TasksCompanion createTaskCompanion({
    String? id,
    String tenantId = 'tenant_test',
    String fieldId = 'field_001',
    String title = 'مهمة اختبارية',
    String status = 'open',
    String priority = 'medium',
  }) {
    return TasksCompanion.insert(
      id: id ?? 'task_${DateTime.now().millisecondsSinceEpoch}',
      tenantId: tenantId,
      fieldId: fieldId,
      farmId: const Value('farm_001'),
      title: title,
      description: const Value('وصف المهمة'),
      status: Value(status),
      priority: Value(priority),
      dueDate: Value(DateTime.now().add(const Duration(days: 7))),
      assignedTo: const Value('user_001'),
      createdAt: DateTime.now(),
      updatedAt: DateTime.now(),
    );
  }
}
