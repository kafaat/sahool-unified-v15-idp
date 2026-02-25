/// Task Reminder Service
/// خدمة تذكير المهام
///
/// Provides task reminder scheduling and overdue task checking.
/// Integrates with NotificationManager for local notifications.

import 'dart:async';

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/di/providers.dart' show apiClientProvider;
import '../../../core/notifications/notification_manager.dart';
import '../../../core/notifications/notification_types.dart';
import '../../../core/utils/app_logger.dart';
import '../domain/entities/task.dart';
import '../data/repo/tasks_repo.dart';
import '../providers/tasks_provider.dart';

/// Task Reminder Service
/// خدمة تذكير المهام
class TaskReminderService {
  final TasksRepo _repo;
  final NotificationManager _notificationManager;
  final String _tenantId;

  Timer? _overdueCheckTimer;
  static const _tag = 'TaskReminderService';

  /// Reminder notification ID offset to avoid conflicts
  static const _reminderIdOffset = 100000;

  /// Overdue notification ID offset
  static const _overdueIdOffset = 200000;

  TaskReminderService({
    required TasksRepo repo,
    required NotificationManager notificationManager,
    required String tenantId,
  })  : _repo = repo,
        _notificationManager = notificationManager,
        _tenantId = tenantId;

  /// Start periodic overdue task checking
  /// بدء الفحص الدوري للمهام المتأخرة
  void startOverdueChecking({Duration interval = const Duration(hours: 1)}) {
    _overdueCheckTimer?.cancel();
    _overdueCheckTimer = Timer.periodic(interval, (_) => checkOverdueTasks());
    AppLogger.i('Started overdue task checking',
        tag: _tag, data: {'interval': interval.inMinutes});
  }

  /// Stop periodic overdue checking
  /// إيقاف الفحص الدوري للمهام المتأخرة
  void stopOverdueChecking() {
    _overdueCheckTimer?.cancel();
    _overdueCheckTimer = null;
    AppLogger.i('Stopped overdue task checking', tag: _tag);
  }

  /// Check for overdue tasks and send notifications
  /// فحص المهام المتأخرة وإرسال الإشعارات
  Future<void> checkOverdueTasks() async {
    try {
      final overdueTasks = await _repo.getOverdueTasks(_tenantId);

      for (final task in overdueTasks) {
        await _sendOverdueNotification(task);
      }

      if (overdueTasks.isNotEmpty) {
        AppLogger.i('Checked overdue tasks',
            tag: _tag, data: {'count': overdueTasks.length});
      }
    } catch (e, stackTrace) {
      AppLogger.e('Failed to check overdue tasks',
          tag: _tag, error: e, stackTrace: stackTrace);
    }
  }

  /// Schedule a reminder for a task
  /// جدولة تذكير لمهمة
  Future<void> scheduleReminder({
    required FieldTask task,
    Duration reminderBefore = const Duration(hours: 1),
  }) async {
    if (task.dueDate == null) {
      AppLogger.w('Cannot schedule reminder for task without due date',
          tag: _tag);
      return;
    }

    final reminderTime = task.dueDate!.subtract(reminderBefore);
    final now = DateTime.now();

    if (reminderTime.isBefore(now)) {
      AppLogger.d('Reminder time is in the past, skipping', tag: _tag);
      return;
    }

    // Generate unique notification ID from task ID
    final notificationId = _reminderIdOffset + task.id.hashCode.abs() % 100000;

    try {
      await _notificationManager.scheduleNotification(
        id: notificationId,
        title: 'تذكير بالمهمة | Task Reminder',
        body:
            '${task.title}\nموعد الاستحقاق: ${_formatDateTime(task.dueDate!)}',
        scheduledTime: reminderTime,
        type: SAHOOLNotificationType.taskReminder,
        priority: _getPriorityFromTask(task),
        data: {
          'task_id': task.id,
          'field_id': task.fieldId,
          'action': 'view_task',
        },
      );

      AppLogger.i('Scheduled task reminder', tag: _tag, data: {
        'taskId': task.id,
        'reminderTime': reminderTime.toIso8601String(),
      });
    } catch (e, stackTrace) {
      AppLogger.e('Failed to schedule task reminder',
          tag: _tag, error: e, stackTrace: stackTrace);
    }
  }

  /// Schedule reminders for all pending tasks
  /// جدولة تذكيرات لجميع المهام المعلقة
  Future<void> scheduleAllPendingReminders() async {
    try {
      final pendingTasks = await _repo.getPendingTasks(_tenantId);

      for (final task in pendingTasks) {
        if (task.dueDate != null) {
          await scheduleReminder(task: task);
        }
      }

      AppLogger.i('Scheduled reminders for pending tasks',
          tag: _tag, data: {'count': pendingTasks.length});
    } catch (e, stackTrace) {
      AppLogger.e('Failed to schedule pending reminders',
          tag: _tag, error: e, stackTrace: stackTrace);
    }
  }

  /// Cancel reminder for a task
  /// إلغاء تذكير لمهمة
  Future<void> cancelReminder(String taskId) async {
    final notificationId = _reminderIdOffset + taskId.hashCode.abs() % 100000;

    try {
      await _notificationManager.cancelNotification(notificationId);
      AppLogger.d('Cancelled task reminder',
          tag: _tag, data: {'taskId': taskId});
    } catch (e) {
      AppLogger.w('Failed to cancel task reminder',
          tag: _tag, data: {'taskId': taskId});
    }
  }

  /// Cancel all task reminders
  /// إلغاء جميع تذكيرات المهام
  Future<void> cancelAllReminders() async {
    // Get all pending notifications and cancel task-related ones
    final pending = await _notificationManager.getPendingNotifications();

    for (final notification in pending) {
      if (notification.id >= _reminderIdOffset &&
          notification.id < _overdueIdOffset) {
        await _notificationManager.cancelNotification(notification.id);
      }
    }

    AppLogger.i('Cancelled all task reminders', tag: _tag);
  }

  /// Send overdue notification for a task
  /// إرسال إشعار تأخر لمهمة
  Future<void> _sendOverdueNotification(FieldTask task) async {
    final notificationId = _overdueIdOffset + task.id.hashCode.abs() % 100000;

    final overdueDays = DateTime.now().difference(task.dueDate!).inDays;
    final overdueText =
        overdueDays == 0 ? 'متأخرة اليوم' : 'متأخرة $overdueDays يوم';

    try {
      await _notificationManager.showNotification(
        id: notificationId,
        title: 'مهمة متأخرة! | Overdue Task!',
        body: '${task.title}\n$overdueText',
        type: SAHOOLNotificationType.taskReminder,
        priority: NotificationPriority.high,
        data: {
          'task_id': task.id,
          'field_id': task.fieldId,
          'action': 'view_task',
          'overdue': true,
        },
      );
    } catch (e, stackTrace) {
      AppLogger.e('Failed to send overdue notification',
          tag: _tag, error: e, stackTrace: stackTrace);
    }
  }

  /// Get notification priority from task priority
  NotificationPriority _getPriorityFromTask(FieldTask task) {
    switch (task.priority) {
      case TaskPriority.urgent:
        return NotificationPriority.critical;
      case TaskPriority.high:
        return NotificationPriority.high;
      case TaskPriority.medium:
        return NotificationPriority.medium;
      case TaskPriority.low:
        return NotificationPriority.low;
    }
  }

  /// Format date time for display
  String _formatDateTime(DateTime dateTime) {
    return '${dateTime.day}/${dateTime.month}/${dateTime.year} ${dateTime.hour.toString().padLeft(2, '0')}:${dateTime.minute.toString().padLeft(2, '0')}';
  }

  /// Dispose resources
  void dispose() {
    stopOverdueChecking();
  }
}

/// Task Reminder Service Provider
final taskReminderServiceProvider =
    Provider.autoDispose<TaskReminderService>((ref) {
  final repo = ref.watch(tasksRepoProvider);
  final notificationManager = ref.watch(notificationManagerProvider);
  final client = ref.watch(apiClientProvider);

  final service = TaskReminderService(
    repo: repo,
    notificationManager: notificationManager,
    tenantId: client.tenantId,
  );

  // Start overdue checking when service is created
  service.startOverdueChecking();

  // Cleanup when disposed
  ref.onDispose(() {
    service.dispose();
  });

  return service;
});

/// Tasks due today provider
final tasksDueTodayProvider =
    FutureProvider.autoDispose<List<FieldTask>>((ref) async {
  final repo = ref.watch(tasksRepoProvider);
  final client = ref.watch(apiClientProvider);
  return repo.getTasksDueToday(client.tenantId);
});

/// Tasks due this week provider
final tasksDueThisWeekProvider =
    FutureProvider.autoDispose<List<FieldTask>>((ref) async {
  final repo = ref.watch(tasksRepoProvider);
  final client = ref.watch(apiClientProvider);
  return repo.getTasksDueWithin(client.tenantId, 7);
});
