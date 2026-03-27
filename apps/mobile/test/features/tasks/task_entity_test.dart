import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/tasks/domain/entities/task.dart';

void main() {
  group('FieldTask', () {
    final now = DateTime(2026, 3, 24, 10, 0);

    FieldTask createTask({
      String id = 'task_001',
      TaskStatus status = TaskStatus.open,
      TaskPriority priority = TaskPriority.medium,
      DateTime? dueDate,
    }) {
      return FieldTask(
        id: id,
        tenantId: 'tenant_1',
        fieldId: 'field_001',
        title: 'ري حقل القمح',
        description: 'ري الحقل بمعدل 25 مم',
        status: status,
        priority: priority,
        dueDate: dueDate,
        createdAt: now,
        updatedAt: now,
      );
    }

    group('Constructor & Defaults', () {
      test('should create task with required fields', () {
        final task = createTask();
        expect(task.id, 'task_001');
        expect(task.tenantId, 'tenant_1');
        expect(task.fieldId, 'field_001');
        expect(task.title, 'ري حقل القمح');
      });

      test('should have correct default values', () {
        final task = createTask();
        expect(task.status, TaskStatus.open);
        expect(task.priority, TaskPriority.medium);
        expect(task.evidencePhotos, isEmpty);
        expect(task.synced, false);
        expect(task.farmId, isNull);
        expect(task.assignedTo, isNull);
      });
    });

    group('fromJson / toJson', () {
      test('should deserialize from JSON correctly', () {
        final json = {
          'id': 'task_002',
          'tenant_id': 'tenant_1',
          'field_id': 'field_001',
          'title': 'فحص الآفات',
          'status': 'in_progress',
          'priority': 'high',
          'due_date': '2026-03-25T08:00:00.000',
          'evidence_photos': ['photo1.jpg', 'photo2.jpg'],
          'created_at': '2026-03-24T10:00:00.000',
          'updated_at': '2026-03-24T10:00:00.000',
        };

        final task = FieldTask.fromJson(json);
        expect(task.id, 'task_002');
        expect(task.title, 'فحص الآفات');
        expect(task.status, TaskStatus.inProgress);
        expect(task.priority, TaskPriority.high);
        expect(task.evidencePhotos, hasLength(2));
        expect(task.synced, true); // fromJson sets synced = true
      });

      test('should handle null optional fields in JSON', () {
        final json = {
          'id': 'task_003',
          'tenant_id': 'tenant_1',
          'field_id': 'field_001',
          'title': 'مهمة بسيطة',
          'created_at': '2026-03-24T10:00:00.000',
          'updated_at': '2026-03-24T10:00:00.000',
        };

        final task = FieldTask.fromJson(json);
        expect(task.description, isNull);
        expect(task.dueDate, isNull);
        expect(task.assignedTo, isNull);
        expect(task.evidencePhotos, isEmpty);
        expect(task.status, TaskStatus.open); // default
        expect(task.priority, TaskPriority.medium); // default
      });

      test('toJson and fromJson should be symmetric', () {
        final original = createTask(
          dueDate: DateTime(2026, 3, 25, 8, 0),
        );

        final json = original.toJson();
        final restored = FieldTask.fromJson(json);

        expect(restored.id, original.id);
        expect(restored.title, original.title);
        expect(restored.status, original.status);
        expect(restored.priority, original.priority);
        expect(restored.fieldId, original.fieldId);
      });
    });

    group('fromDb', () {
      test('should parse database row correctly', () {
        final row = {
          'id': 'task_004',
          'tenant_id': 'tenant_1',
          'field_id': 'field_001',
          'title': 'تسميد',
          'status': 'done',
          'priority': 'low',
          'synced': 1,
          'created_at': '2026-03-24T10:00:00.000',
          'updated_at': '2026-03-24T10:00:00.000',
        };

        final task = FieldTask.fromDb(row);
        expect(task.status, TaskStatus.done);
        expect(task.priority, TaskPriority.low);
        expect(task.synced, true);
      });

      test('should handle synced as bool', () {
        final row = {
          'id': 'task_005',
          'tenant_id': 'tenant_1',
          'field_id': 'field_001',
          'title': 'test',
          'synced': true,
          'created_at': '2026-03-24T10:00:00.000',
          'updated_at': '2026-03-24T10:00:00.000',
        };

        final task = FieldTask.fromDb(row);
        expect(task.synced, true);
      });

      test('should parse evidence_photos CSV string', () {
        final row = {
          'id': 'task_006',
          'tenant_id': 'tenant_1',
          'field_id': 'field_001',
          'title': 'test',
          'evidence_photos': 'a.jpg,b.jpg,c.jpg',
          'created_at': '2026-03-24T10:00:00.000',
          'updated_at': '2026-03-24T10:00:00.000',
        };

        final task = FieldTask.fromDb(row);
        expect(task.evidencePhotos, ['a.jpg', 'b.jpg', 'c.jpg']);
      });
    });

    group('copyWith', () {
      test('should preserve values when not specified', () {
        final original = createTask();
        final copy = original.copyWith();
        expect(copy.id, original.id);
        expect(copy.title, original.title);
        expect(copy.status, original.status);
      });

      test('should update specified values only', () {
        final original = createTask();
        final updated = original.copyWith(
          status: TaskStatus.done,
          title: 'مهمة محدثة',
        );

        expect(updated.status, TaskStatus.done);
        expect(updated.title, 'مهمة محدثة');
        expect(updated.id, original.id); // unchanged
        expect(updated.priority, original.priority); // unchanged
      });

      test('should not mutate original', () {
        final original = createTask();
        original.copyWith(status: TaskStatus.done);
        expect(original.status, TaskStatus.open);
      });
    });

    group('isOverdue', () {
      test('should return false when no due date', () {
        final task = createTask();
        expect(task.isOverdue, false);
      });

      test('should return false when completed', () {
        final task = createTask(
          status: TaskStatus.done,
          dueDate: DateTime(2020, 1, 1),
        );
        expect(task.isOverdue, false);
      });

      test('should return true when past due and open', () {
        final task = createTask(
          dueDate: DateTime(2020, 1, 1),
        );
        expect(task.isOverdue, true);
      });

      test('should return false when due date is in future', () {
        final task = createTask(
          dueDate: DateTime(2099, 12, 31),
        );
        expect(task.isOverdue, false);
      });
    });

    group('isDueToday', () {
      test('should return false when no due date', () {
        final task = createTask();
        expect(task.isDueToday, false);
      });

      test('should return true when due date is today', () {
        final today = DateTime.now();
        final task = createTask(
          dueDate: DateTime(today.year, today.month, today.day, 14, 0),
        );
        expect(task.isDueToday, true);
      });

      test('should return false when due date is tomorrow', () {
        final tomorrow = DateTime.now().add(const Duration(days: 1));
        final task = createTask(dueDate: tomorrow);
        expect(task.isDueToday, false);
      });
    });
  });

  group('TaskStatus', () {
    test('should have all expected values', () {
      expect(TaskStatus.values, hasLength(4));
      expect(TaskStatus.values, contains(TaskStatus.open));
      expect(TaskStatus.values, contains(TaskStatus.inProgress));
      expect(TaskStatus.values, contains(TaskStatus.done));
      expect(TaskStatus.values, contains(TaskStatus.cancelled));
    });

    test('fromString should parse valid values', () {
      expect(TaskStatus.fromString('open'), TaskStatus.open);
      expect(TaskStatus.fromString('in_progress'), TaskStatus.inProgress);
      expect(TaskStatus.fromString('done'), TaskStatus.done);
      expect(TaskStatus.fromString('cancelled'), TaskStatus.cancelled);
    });

    test('fromString should default to open for unknown value', () {
      expect(TaskStatus.fromString('invalid'), TaskStatus.open);
      expect(TaskStatus.fromString(''), TaskStatus.open);
    });

    test('should have Arabic labels', () {
      expect(TaskStatus.open.arabicLabel, 'مفتوحة');
      expect(TaskStatus.done.arabicLabel, 'مكتملة');
    });
  });

  group('TaskPriority', () {
    test('fromString should parse valid values', () {
      expect(TaskPriority.fromString('low'), TaskPriority.low);
      expect(TaskPriority.fromString('medium'), TaskPriority.medium);
      expect(TaskPriority.fromString('high'), TaskPriority.high);
      expect(TaskPriority.fromString('urgent'), TaskPriority.urgent);
    });

    test('fromString should default to medium for unknown value', () {
      expect(TaskPriority.fromString('invalid'), TaskPriority.medium);
    });

    test('should have Arabic labels', () {
      expect(TaskPriority.urgent.arabicLabel, 'عاجلة');
      expect(TaskPriority.low.arabicLabel, 'منخفضة');
    });
  });
}
