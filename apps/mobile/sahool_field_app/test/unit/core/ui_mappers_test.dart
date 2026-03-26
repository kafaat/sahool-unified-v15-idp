import 'dart:ui';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/field/domain/entities/field.dart';
import 'package:sahool_field_app/features/tasks/domain/entities/field_task.dart';
import 'package:sahool_field_app/core/ui/field_status_mapper.dart';
import 'package:sahool_field_app/core/ui/task_mapper.dart';

void main() {
  // ===========================================================================
  // FieldStatusMapper Tests
  // ===========================================================================

  group('FieldStatusMapper - toColor', () {
    test('healthy returns dark green', () {
      expect(FieldStatus.healthy.toColor(), const Color(0xFF2E7D32));
    });

    test('stressed returns yellow/orange', () {
      expect(FieldStatus.stressed.toColor(), const Color(0xFFF9A825));
    });

    test('critical returns red', () {
      expect(FieldStatus.critical.toColor(), const Color(0xFFC62828));
    });

    test('unknown returns grey', () {
      expect(FieldStatus.unknown.toColor(), const Color(0xFF9E9E9E));
    });

    test('all enum values produce distinct colors', () {
      final colors =
          FieldStatus.values.map((s) => s.toColor().value).toSet();
      expect(colors.length, equals(FieldStatus.values.length));
    });
  });

  group('FieldStatusMapper - toLightColor', () {
    test('healthy returns light green', () {
      expect(FieldStatus.healthy.toLightColor(), const Color(0xFFE8F5E9));
    });

    test('stressed returns light yellow', () {
      expect(FieldStatus.stressed.toLightColor(), const Color(0xFFFFF8E1));
    });

    test('critical returns light red', () {
      expect(FieldStatus.critical.toLightColor(), const Color(0xFFFFEBEE));
    });

    test('unknown returns light grey', () {
      expect(FieldStatus.unknown.toLightColor(), const Color(0xFFF5F5F5));
    });

    test('all enum values produce distinct light colors', () {
      final colors =
          FieldStatus.values.map((s) => s.toLightColor().value).toSet();
      expect(colors.length, equals(FieldStatus.values.length));
    });
  });

  group('FieldStatusMapper - toText (Arabic)', () {
    test('healthy returns Arabic text', () {
      expect(FieldStatus.healthy.toText(), 'ممتاز');
    });

    test('stressed returns Arabic text', () {
      expect(FieldStatus.stressed.toText(), 'إجهاد');
    });

    test('critical returns Arabic text', () {
      expect(FieldStatus.critical.toText(), 'خطر');
    });

    test('unknown returns Arabic text', () {
      expect(FieldStatus.unknown.toText(), 'غير معروف');
    });

    test('all values return non-empty strings', () {
      for (final status in FieldStatus.values) {
        expect(status.toText(), isNotEmpty);
      }
    });
  });

  group('FieldStatusMapper - toTextEn', () {
    test('healthy returns Healthy', () {
      expect(FieldStatus.healthy.toTextEn(), 'Healthy');
    });

    test('stressed returns Stressed', () {
      expect(FieldStatus.stressed.toTextEn(), 'Stressed');
    });

    test('critical returns Critical', () {
      expect(FieldStatus.critical.toTextEn(), 'Critical');
    });

    test('unknown returns Unknown', () {
      expect(FieldStatus.unknown.toTextEn(), 'Unknown');
    });

    test('all values return non-empty strings', () {
      for (final status in FieldStatus.values) {
        expect(status.toTextEn(), isNotEmpty);
      }
    });
  });

  group('FieldStatusMapper - toIcon', () {
    test('healthy returns check_circle', () {
      expect(FieldStatus.healthy.toIcon(), Icons.check_circle);
    });

    test('stressed returns warning_amber', () {
      expect(FieldStatus.stressed.toIcon(), Icons.warning_amber);
    });

    test('critical returns error', () {
      expect(FieldStatus.critical.toIcon(), Icons.error);
    });

    test('unknown returns help_outline', () {
      expect(FieldStatus.unknown.toIcon(), Icons.help_outline);
    });
  });

  group('FieldStatusMapper - toEmoji', () {
    test('healthy returns check mark emoji', () {
      expect(FieldStatus.healthy.toEmoji(), '✅');
    });

    test('stressed returns warning emoji', () {
      expect(FieldStatus.stressed.toEmoji(), '⚠️');
    });

    test('critical returns alert emoji', () {
      expect(FieldStatus.critical.toEmoji(), '🚨');
    });

    test('unknown returns question emoji', () {
      expect(FieldStatus.unknown.toEmoji(), '❓');
    });

    test('all values return non-empty emoji strings', () {
      for (final status in FieldStatus.values) {
        expect(status.toEmoji(), isNotEmpty);
      }
    });
  });

  group('FieldStatusMapper - exhaustive coverage', () {
    test('FieldStatus has exactly 4 values', () {
      expect(FieldStatus.values.length, 4);
    });

    test('all enum values have all mappings defined', () {
      for (final status in FieldStatus.values) {
        expect(() => status.toColor(), returnsNormally);
        expect(() => status.toLightColor(), returnsNormally);
        expect(() => status.toText(), returnsNormally);
        expect(() => status.toTextEn(), returnsNormally);
        expect(() => status.toIcon(), returnsNormally);
        expect(() => status.toEmoji(), returnsNormally);
      }
    });
  });

  // ===========================================================================
  // FieldUIExtension Tests
  // ===========================================================================

  group('FieldUIExtension', () {
    Field _makeField({double? ndvi, double area = 5.0}) {
      final now = DateTime.now();
      return Field(
        id: 'test-field',
        tenantId: 'tenant-1',
        name: 'Test Field',
        areaHectares: area,
        ndviCurrent: ndvi,
        createdAt: now,
        updatedAt: now,
      );
    }

    test('statusColor delegates to healthStatus.toColor for healthy field', () {
      final field = _makeField(ndvi: 0.75);
      expect(field.statusColor, const Color(0xFF2E7D32));
    });

    test('statusColor delegates to healthStatus.toColor for stressed field',
        () {
      final field = _makeField(ndvi: 0.5);
      expect(field.statusColor, const Color(0xFFF9A825));
    });

    test('statusColor delegates to healthStatus.toColor for critical field',
        () {
      final field = _makeField(ndvi: 0.2);
      expect(field.statusColor, const Color(0xFFC62828));
    });

    test('statusColor delegates to healthStatus.toColor for unknown field', () {
      final field = _makeField(ndvi: null);
      expect(field.statusColor, const Color(0xFF9E9E9E));
    });

    test('statusText returns Arabic text for healthy field', () {
      final field = _makeField(ndvi: 0.75);
      expect(field.statusText, 'ممتاز');
    });

    test('areaFormatted includes hectares label in Arabic', () {
      final field = _makeField(area: 12.345);
      expect(field.areaFormatted, '12.3 هكتار');
    });

    test('areaFormatted rounds to one decimal', () {
      final field = _makeField(area: 7.0);
      expect(field.areaFormatted, '7.0 هكتار');
    });

    test('ndviFormatted shows two decimal places', () {
      final field = _makeField(ndvi: 0.726);
      expect(field.ndviFormatted, '0.73');
    });

    test('ndviFormatted defaults to 0.00 when ndvi is null', () {
      final field = _makeField(ndvi: null);
      expect(field.ndviFormatted, '0.00');
    });

    test('ndviPercentage returns percentage string', () {
      final field = _makeField(ndvi: 0.65);
      expect(field.ndviPercentage, '65%');
    });

    test('statusBackgroundColor delegates to toLightColor', () {
      final field = _makeField(ndvi: 0.75);
      expect(field.statusBackgroundColor, const Color(0xFFE8F5E9));
    });

    test('statusIcon delegates to toIcon', () {
      final field = _makeField(ndvi: 0.75);
      expect(field.statusIcon, Icons.check_circle);
    });
  });

  // ===========================================================================
  // TaskTypeMapper Tests
  // ===========================================================================

  group('TaskTypeMapper - icon', () {
    test('irrigation returns water_drop', () {
      expect(TaskType.irrigation.icon, Icons.water_drop);
    });

    test('fertilization returns grass', () {
      expect(TaskType.fertilization.icon, Icons.grass);
    });

    test('scouting returns search', () {
      expect(TaskType.scouting.icon, Icons.search);
    });

    test('harvest returns agriculture', () {
      expect(TaskType.harvest.icon, Icons.agriculture);
    });

    test('other returns assignment', () {
      expect(TaskType.other.icon, Icons.assignment);
    });
  });

  group('TaskTypeMapper - color', () {
    test('irrigation returns blue', () {
      expect(TaskType.irrigation.color, const Color(0xFF1976D2));
    });

    test('fertilization returns green', () {
      expect(TaskType.fertilization.color, const Color(0xFF388E3C));
    });

    test('scouting returns orange', () {
      expect(TaskType.scouting.color, const Color(0xFFF57C00));
    });

    test('harvest returns gold', () {
      expect(TaskType.harvest.color, const Color(0xFFFFA000));
    });

    test('other returns grey', () {
      expect(TaskType.other.color, const Color(0xFF757575));
    });

    test('all task type colors are distinct', () {
      final colors = TaskType.values.map((t) => t.color.value).toSet();
      expect(colors.length, equals(TaskType.values.length));
    });
  });

  group('TaskTypeMapper - lightColor', () {
    test('irrigation returns light blue', () {
      expect(TaskType.irrigation.lightColor, const Color(0xFFE3F2FD));
    });

    test('fertilization returns light green', () {
      expect(TaskType.fertilization.lightColor, const Color(0xFFE8F5E9));
    });

    test('scouting returns light orange', () {
      expect(TaskType.scouting.lightColor, const Color(0xFFFFF3E0));
    });

    test('harvest returns light gold', () {
      expect(TaskType.harvest.lightColor, const Color(0xFFFFF8E1));
    });

    test('other returns light grey', () {
      expect(TaskType.other.lightColor, const Color(0xFFF5F5F5));
    });
  });

  group('TaskTypeMapper - textAr', () {
    test('irrigation returns Arabic ري', () {
      expect(TaskType.irrigation.textAr, 'ري');
    });

    test('fertilization returns Arabic تسميد', () {
      expect(TaskType.fertilization.textAr, 'تسميد');
    });

    test('scouting returns Arabic فحص', () {
      expect(TaskType.scouting.textAr, 'فحص');
    });

    test('harvest returns Arabic حصاد', () {
      expect(TaskType.harvest.textAr, 'حصاد');
    });

    test('other returns Arabic أخرى', () {
      expect(TaskType.other.textAr, 'أخرى');
    });

    test('all values return non-empty Arabic text', () {
      for (final type in TaskType.values) {
        expect(type.textAr, isNotEmpty);
      }
    });
  });

  group('TaskTypeMapper - textEn', () {
    test('irrigation returns Irrigation', () {
      expect(TaskType.irrigation.textEn, 'Irrigation');
    });

    test('fertilization returns Fertilization', () {
      expect(TaskType.fertilization.textEn, 'Fertilization');
    });

    test('scouting returns Scouting', () {
      expect(TaskType.scouting.textEn, 'Scouting');
    });

    test('harvest returns Harvest', () {
      expect(TaskType.harvest.textEn, 'Harvest');
    });

    test('other returns Other', () {
      expect(TaskType.other.textEn, 'Other');
    });
  });

  group('TaskTypeMapper - exhaustive coverage', () {
    test('TaskType has exactly 5 values', () {
      expect(TaskType.values.length, 5);
    });

    test('all enum values have all mappings defined', () {
      for (final type in TaskType.values) {
        expect(() => type.icon, returnsNormally);
        expect(() => type.color, returnsNormally);
        expect(() => type.lightColor, returnsNormally);
        expect(() => type.textAr, returnsNormally);
        expect(() => type.textEn, returnsNormally);
      }
    });
  });

  // ===========================================================================
  // TaskPriorityMapper Tests
  // ===========================================================================

  group('TaskPriorityMapper - color', () {
    test('urgent returns red', () {
      expect(TaskPriority.urgent.color, const Color(0xFFC62828));
    });

    test('high returns orange', () {
      expect(TaskPriority.high.color, const Color(0xFFF57C00));
    });

    test('normal returns blue', () {
      expect(TaskPriority.normal.color, const Color(0xFF1976D2));
    });

    test('low returns grey', () {
      expect(TaskPriority.low.color, const Color(0xFF757575));
    });

    test('all priority colors are distinct', () {
      final colors = TaskPriority.values.map((p) => p.color.value).toSet();
      expect(colors.length, equals(TaskPriority.values.length));
    });
  });

  group('TaskPriorityMapper - icon', () {
    test('urgent returns priority_high', () {
      expect(TaskPriority.urgent.icon, Icons.priority_high);
    });

    test('high returns arrow_upward', () {
      expect(TaskPriority.high.icon, Icons.arrow_upward);
    });

    test('normal returns remove (dash)', () {
      expect(TaskPriority.normal.icon, Icons.remove);
    });

    test('low returns arrow_downward', () {
      expect(TaskPriority.low.icon, Icons.arrow_downward);
    });
  });

  group('TaskPriorityMapper - textAr', () {
    test('urgent returns عاجل', () {
      expect(TaskPriority.urgent.textAr, 'عاجل');
    });

    test('high returns عالي', () {
      expect(TaskPriority.high.textAr, 'عالي');
    });

    test('normal returns عادي', () {
      expect(TaskPriority.normal.textAr, 'عادي');
    });

    test('low returns منخفض', () {
      expect(TaskPriority.low.textAr, 'منخفض');
    });

    test('all values return non-empty Arabic text', () {
      for (final priority in TaskPriority.values) {
        expect(priority.textAr, isNotEmpty);
      }
    });
  });

  group('TaskPriorityMapper - exhaustive coverage', () {
    test('TaskPriority has exactly 4 values', () {
      expect(TaskPriority.values.length, 4);
    });

    test('all enum values have all mappings defined', () {
      for (final priority in TaskPriority.values) {
        expect(() => priority.color, returnsNormally);
        expect(() => priority.icon, returnsNormally);
        expect(() => priority.textAr, returnsNormally);
      }
    });
  });

  // ===========================================================================
  // FieldTaskUIExtension Tests
  // ===========================================================================

  group('FieldTaskUIExtension', () {
    FieldTask _makeTask({
      TaskType type = TaskType.irrigation,
      TaskPriority priority = TaskPriority.normal,
      DateTime? dueTime,
      bool isCompleted = false,
    }) {
      return FieldTask(
        id: 'task-1',
        title: 'Test Task',
        fieldName: 'Field A',
        dueTime: dueTime ?? DateTime.now().add(const Duration(hours: 2)),
        type: type,
        priority: priority,
        isCompleted: isCompleted,
      );
    }

    test('typeIcon delegates to type.icon', () {
      final task = _makeTask(type: TaskType.harvest);
      expect(task.typeIcon, Icons.agriculture);
    });

    test('typeColor delegates to type.color', () {
      final task = _makeTask(type: TaskType.fertilization);
      expect(task.typeColor, const Color(0xFF388E3C));
    });

    test('typeLightColor delegates to type.lightColor', () {
      final task = _makeTask(type: TaskType.scouting);
      expect(task.typeLightColor, const Color(0xFFFFF3E0));
    });

    test('typeText delegates to type.textAr', () {
      final task = _makeTask(type: TaskType.irrigation);
      expect(task.typeText, 'ري');
    });

    test('priorityColor delegates to priority.color', () {
      final task = _makeTask(priority: TaskPriority.urgent);
      expect(task.priorityColor, const Color(0xFFC62828));
    });

    test('dueTimeFormatted formats AM time correctly', () {
      final task = _makeTask(
        dueTime: DateTime(2026, 1, 15, 9, 5),
      );
      expect(task.dueTimeFormatted, '9:05 ص');
    });

    test('dueTimeFormatted formats PM time correctly', () {
      final task = _makeTask(
        dueTime: DateTime(2026, 1, 15, 14, 30),
      );
      expect(task.dueTimeFormatted, '2:30 م');
    });

    test('dueTimeFormatted handles midnight (0:00) as 12 AM', () {
      final task = _makeTask(
        dueTime: DateTime(2026, 1, 15, 0, 0),
      );
      expect(task.dueTimeFormatted, '12:00 ص');
    });

    test('dueTimeFormatted handles noon (12:00) as 12 PM', () {
      final task = _makeTask(
        dueTime: DateTime(2026, 1, 15, 12, 0),
      );
      expect(task.dueTimeFormatted, '12:00 م');
    });

    test('timeRemainingFormatted returns مكتملة for completed task', () {
      final task = _makeTask(isCompleted: true);
      expect(task.timeRemainingFormatted, 'مكتملة');
    });

    test('timeRemainingFormatted returns متأخرة for overdue task', () {
      final task = _makeTask(
        dueTime: DateTime.now().subtract(const Duration(hours: 1)),
      );
      expect(task.timeRemainingFormatted, 'متأخرة');
    });

    test('timeRemainingFormatted shows minutes when less than 1 hour', () {
      final task = _makeTask(
        dueTime: DateTime.now().add(const Duration(minutes: 30)),
      );
      expect(task.timeRemainingFormatted, contains('دقيقة'));
    });

    test('timeRemainingFormatted shows hours when less than 24 hours', () {
      final task = _makeTask(
        dueTime: DateTime.now().add(const Duration(hours: 5)),
      );
      expect(task.timeRemainingFormatted, contains('ساعة'));
    });

    test('timeRemainingFormatted shows days when 24+ hours remaining', () {
      final task = _makeTask(
        dueTime: DateTime.now().add(const Duration(days: 3)),
      );
      expect(task.timeRemainingFormatted, contains('يوم'));
    });
  });
}
