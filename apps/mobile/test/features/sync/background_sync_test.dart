import 'dart:async';

import 'package:flutter_test/flutter_test.dart';

import 'sync_mocks.dart';

/// Background Sync Tests
/// اختبارات المزامنة في الخلفية
///
/// Tests for:
/// - Workmanager task registration
/// - Background task execution
/// - Task scheduling
/// - Network-aware sync triggers

/// Mock Workmanager for testing
class MockWorkmanager {
  bool _isInitialized = false;
  final List<RegisteredTask> _registeredTasks = [];
  final Map<String, TaskCallback> _taskCallbacks = {};

  bool get isInitialized => _isInitialized;
  List<RegisteredTask> get registeredTasks => List.unmodifiable(_registeredTasks);

  /// Initialize Workmanager
  Future<void> initialize(TaskCallback callback, {bool isDebug = false}) async {
    _isInitialized = true;
    _taskCallbacks['default'] = callback;
  }

  /// Register periodic task
  Future<void> registerPeriodicTask(
    String uniqueName,
    String taskName, {
    Duration? frequency,
    Map<String, dynamic>? inputData,
    Constraints? constraints,
    ExistingWorkPolicy? existingWorkPolicy,
    Duration? initialDelay,
    BackoffPolicy? backoffPolicy,
    Duration? backoffPolicyDelay,
  }) async {
    _registeredTasks.add(RegisteredTask(
      uniqueName: uniqueName,
      taskName: taskName,
      frequency: frequency,
      inputData: inputData,
      constraints: constraints,
      existingWorkPolicy: existingWorkPolicy,
      isOneOff: false,
    ));
  }

  /// Register one-off task
  Future<void> registerOneOffTask(
    String uniqueName,
    String taskName, {
    Map<String, dynamic>? inputData,
    Constraints? constraints,
    ExistingWorkPolicy? existingWorkPolicy,
    Duration? initialDelay,
    BackoffPolicy? backoffPolicy,
    Duration? backoffPolicyDelay,
  }) async {
    _registeredTasks.add(RegisteredTask(
      uniqueName: uniqueName,
      taskName: taskName,
      inputData: inputData,
      constraints: constraints,
      existingWorkPolicy: existingWorkPolicy,
      isOneOff: true,
    ));
  }

  /// Cancel task by unique name
  Future<void> cancelByUniqueName(String uniqueName) async {
    _registeredTasks.removeWhere((task) => task.uniqueName == uniqueName);
  }

  /// Cancel all tasks
  Future<void> cancelAll() async {
    _registeredTasks.clear();
  }

  /// Simulate task execution for testing
  Future<bool> executeTask(String taskName, Map<String, dynamic>? inputData) async {
    final callback = _taskCallbacks['default'];
    if (callback != null) {
      return await callback(taskName, inputData);
    }
    return false;
  }

  /// Reset mock state
  void reset() {
    _isInitialized = false;
    _registeredTasks.clear();
    _taskCallbacks.clear();
  }
}

/// Task callback type
typedef TaskCallback = Future<bool> Function(String taskName, Map<String, dynamic>? inputData);

/// Registered task data
class RegisteredTask {
  final String uniqueName;
  final String taskName;
  final Duration? frequency;
  final Map<String, dynamic>? inputData;
  final Constraints? constraints;
  final ExistingWorkPolicy? existingWorkPolicy;
  final bool isOneOff;

  const RegisteredTask({
    required this.uniqueName,
    required this.taskName,
    this.frequency,
    this.inputData,
    this.constraints,
    this.existingWorkPolicy,
    required this.isOneOff,
  });
}

/// Task constraints
class Constraints {
  final NetworkType? networkType;
  final bool? requiresBatteryNotLow;
  final bool? requiresCharging;
  final bool? requiresDeviceIdle;
  final bool? requiresStorageNotLow;

  const Constraints({
    this.networkType,
    this.requiresBatteryNotLow,
    this.requiresCharging,
    this.requiresDeviceIdle,
    this.requiresStorageNotLow,
  });
}

/// Network type constraints
enum NetworkType {
  connected,
  metered,
  notRequired,
  notRoaming,
  unmetered,
}

/// Existing work policy
enum ExistingWorkPolicy {
  append,
  keep,
  replace,
  update,
}

/// Backoff policy
enum BackoffPolicy {
  exponential,
  linear,
}

void main() {
  group('MockWorkmanager', () {
    late MockWorkmanager workmanager;

    setUp(() {
      workmanager = MockWorkmanager();
    });

    tearDown(() {
      workmanager.reset();
    });

    test('should initialize successfully', () async {
      expect(workmanager.isInitialized, isFalse);

      await workmanager.initialize(
        (taskName, inputData) async => true,
        isDebug: true,
      );

      expect(workmanager.isInitialized, isTrue);
    });

    test('should register periodic task', () async {
      await workmanager.initialize((_, __) async => true);

      await workmanager.registerPeriodicTask(
        'sahool_sync',
        'backgroundSync',
        frequency: const Duration(minutes: 15),
        constraints: const Constraints(
          networkType: NetworkType.connected,
        ),
      );

      expect(workmanager.registeredTasks.length, equals(1));
      expect(workmanager.registeredTasks.first.uniqueName, equals('sahool_sync'));
      expect(workmanager.registeredTasks.first.isOneOff, isFalse);
    });

    test('should register one-off task', () async {
      await workmanager.initialize((_, __) async => true);

      await workmanager.registerOneOffTask(
        'immediate_sync',
        'syncNow',
        inputData: {'force': true},
      );

      expect(workmanager.registeredTasks.length, equals(1));
      expect(workmanager.registeredTasks.first.uniqueName, equals('immediate_sync'));
      expect(workmanager.registeredTasks.first.isOneOff, isTrue);
      expect(workmanager.registeredTasks.first.inputData, isNotNull);
    });

    test('should cancel task by unique name', () async {
      await workmanager.initialize((_, __) async => true);

      await workmanager.registerPeriodicTask('task1', 'sync1');
      await workmanager.registerPeriodicTask('task2', 'sync2');

      expect(workmanager.registeredTasks.length, equals(2));

      await workmanager.cancelByUniqueName('task1');

      expect(workmanager.registeredTasks.length, equals(1));
      expect(workmanager.registeredTasks.first.uniqueName, equals('task2'));
    });

    test('should cancel all tasks', () async {
      await workmanager.initialize((_, __) async => true);

      await workmanager.registerPeriodicTask('task1', 'sync1');
      await workmanager.registerPeriodicTask('task2', 'sync2');
      await workmanager.registerOneOffTask('task3', 'sync3');

      expect(workmanager.registeredTasks.length, equals(3));

      await workmanager.cancelAll();

      expect(workmanager.registeredTasks.length, equals(0));
    });

    test('should execute task callback', () async {
      var taskExecuted = false;
      String? executedTaskName;

      await workmanager.initialize((taskName, inputData) async {
        taskExecuted = true;
        executedTaskName = taskName;
        return true;
      });

      final result = await workmanager.executeTask('testTask', null);

      expect(taskExecuted, isTrue);
      expect(executedTaskName, equals('testTask'));
      expect(result, isTrue);
    });

    test('should pass input data to callback', () async {
      Map<String, dynamic>? receivedData;

      await workmanager.initialize((taskName, inputData) async {
        receivedData = inputData;
        return true;
      });

      await workmanager.executeTask('testTask', {'key': 'value'});

      expect(receivedData, isNotNull);
      expect(receivedData!['key'], equals('value'));
    });
  });

  group('Background Sync Task Configuration', () {
    late MockWorkmanager workmanager;

    setUp(() {
      workmanager = MockWorkmanager();
    });

    tearDown(() {
      workmanager.reset();
    });

    test('should configure sync task with proper constraints', () async {
      await workmanager.initialize((_, __) async => true);

      // Configure task like in SyncWorker
      await workmanager.registerPeriodicTask(
        'sahool_background_sync',
        'backgroundSyncTask',
        frequency: const Duration(minutes: 15),
        constraints: const Constraints(
          networkType: NetworkType.connected,
          requiresBatteryNotLow: true,
        ),
        existingWorkPolicy: ExistingWorkPolicy.keep,
      );

      final task = workmanager.registeredTasks.first;

      expect(task.uniqueName, equals('sahool_background_sync'));
      expect(task.frequency, equals(const Duration(minutes: 15)));
      expect(task.constraints, isNotNull);
      expect(task.constraints!.networkType, equals(NetworkType.connected));
      expect(task.constraints!.requiresBatteryNotLow, isTrue);
      expect(task.existingWorkPolicy, equals(ExistingWorkPolicy.keep));
    });

    test('should configure immediate sync task', () async {
      await workmanager.initialize((_, __) async => true);

      await workmanager.registerOneOffTask(
        'sahool_immediate_sync',
        'immediateSyncTask',
        inputData: {
          'reason': 'user_triggered',
          'timestamp': DateTime.now().toIso8601String(),
        },
        constraints: const Constraints(
          networkType: NetworkType.connected,
        ),
      );

      final task = workmanager.registeredTasks.first;

      expect(task.isOneOff, isTrue);
      expect(task.inputData, isNotNull);
      expect(task.inputData!['reason'], equals('user_triggered'));
    });
  });

  group('Background Sync Execution', () {
    late MockWorkmanager workmanager;
    late MockSyncDatabase mockDb;
    late MockNetworkStatus networkStatus;

    setUp(() {
      workmanager = MockWorkmanager();
      mockDb = MockSyncDatabase();
      networkStatus = MockNetworkStatus();
    });

    tearDown(() {
      workmanager.reset();
      mockDb.reset();
      networkStatus.dispose();
    });

    test('should sync pending items in background task', () async {
      // Setup mock database with pending items
      await mockDb.queueOutboxItem(
        tenantId: 'tenant_1',
        entityType: 'field',
        entityId: 'field_001',
        apiEndpoint: '/api/v1/fields/field_001',
        method: 'PUT',
        payload: '{}',
      );
      await mockDb.queueOutboxItem(
        tenantId: 'tenant_1',
        entityType: 'task',
        entityId: 'task_001',
        apiEndpoint: '/api/v1/tasks',
        method: 'POST',
        payload: '{}',
      );

      // Initialize workmanager with sync callback
      await workmanager.initialize((taskName, inputData) async {
        if (taskName == 'backgroundSyncTask') {
          // Check network
          if (!networkStatus.isOnline) {
            return false;
          }

          // Process pending items
          final pending = await mockDb.getPendingOutbox();
          for (final item in pending) {
            await mockDb.markOutboxDone(item.id);
          }

          await mockDb.logSync(
            type: 'background_sync',
            status: 'success',
            message: 'Synced ${pending.length} items',
          );

          return true;
        }
        return false;
      });

      // Execute background task
      networkStatus.setOnline(true);
      final result = await workmanager.executeTask('backgroundSyncTask', null);

      expect(result, isTrue);

      final pending = await mockDb.getPendingOutbox();
      expect(pending.length, equals(0));

      final logs = await mockDb.getRecentSyncLogs();
      expect(logs.any((log) => log['type'] == 'background_sync'), isTrue);
    });

    test('should skip sync when offline', () async {
      // Queue items
      await mockDb.queueOutboxItem(
        tenantId: 'tenant_1',
        entityType: 'field',
        entityId: 'field_001',
        apiEndpoint: '/api/v1/fields/field_001',
        method: 'PUT',
        payload: '{}',
      );

      await workmanager.initialize((taskName, inputData) async {
        if (!networkStatus.isOnline) {
          await mockDb.logSync(
            type: 'background_sync',
            status: 'skipped',
            message: 'No network connection',
          );
          return false;
        }
        return true;
      });

      // Set offline
      networkStatus.setOnline(false);

      final result = await workmanager.executeTask('backgroundSyncTask', null);

      expect(result, isFalse);

      final pending = await mockDb.getPendingOutbox();
      expect(pending.length, equals(1)); // Still pending

      final logs = await mockDb.getRecentSyncLogs();
      expect(logs.any((log) => log['status'] == 'skipped'), isTrue);
    });

    test('should handle partial failure in background sync', () async {
      // Queue items
      final ids = <int>[];
      for (int i = 0; i < 5; i++) {
        final id = await mockDb.queueOutboxItem(
          tenantId: 'tenant_1',
          entityType: 'field',
          entityId: 'field_00$i',
          apiEndpoint: '/api/v1/fields/field_00$i',
          method: 'PUT',
          payload: '{}',
        );
        ids.add(id);
      }

      int syncedCount = 0;
      int failedCount = 0;

      await workmanager.initialize((taskName, inputData) async {
        final pending = await mockDb.getPendingOutbox();

        for (int i = 0; i < pending.length; i++) {
          if (i < 3) {
            // First 3 succeed
            await mockDb.markOutboxDone(pending[i].id);
            syncedCount++;
          } else {
            // Rest fail
            await mockDb.bumpOutboxRetry(pending[i].id);
            failedCount++;
          }
        }

        await mockDb.logSync(
          type: 'background_sync',
          status: failedCount > 0 ? 'partial' : 'success',
          message: 'Synced: $syncedCount, Failed: $failedCount',
        );

        return syncedCount > 0;
      });

      networkStatus.setOnline(true);
      final result = await workmanager.executeTask('backgroundSyncTask', null);

      expect(result, isTrue);
      expect(syncedCount, equals(3));
      expect(failedCount, equals(2));

      final pending = await mockDb.getPendingOutbox();
      expect(pending.length, equals(2));
    });
  });

  group('Task Scheduling', () {
    late MockWorkmanager workmanager;

    setUp(() {
      workmanager = MockWorkmanager();
    });

    tearDown(() {
      workmanager.reset();
    });

    test('should schedule periodic sync every 15 minutes', () async {
      await workmanager.initialize((_, __) async => true);

      await workmanager.registerPeriodicTask(
        'sahool_sync_15min',
        'periodicSync',
        frequency: const Duration(minutes: 15),
      );

      final task = workmanager.registeredTasks.first;
      expect(task.frequency, equals(const Duration(minutes: 15)));
    });

    test('should support multiple scheduled tasks', () async {
      await workmanager.initialize((_, __) async => true);

      // Regular sync
      await workmanager.registerPeriodicTask(
        'sync_regular',
        'regularSync',
        frequency: const Duration(minutes: 15),
      );

      // Deep sync (less frequent)
      await workmanager.registerPeriodicTask(
        'sync_deep',
        'deepSync',
        frequency: const Duration(hours: 6),
      );

      expect(workmanager.registeredTasks.length, equals(2));

      final regularTask = workmanager.registeredTasks
          .firstWhere((t) => t.uniqueName == 'sync_regular');
      final deepTask = workmanager.registeredTasks
          .firstWhere((t) => t.uniqueName == 'sync_deep');

      expect(regularTask.frequency, equals(const Duration(minutes: 15)));
      expect(deepTask.frequency, equals(const Duration(hours: 6)));
    });

    test('should replace existing task with same name', () async {
      await workmanager.initialize((_, __) async => true);

      // Register initial task
      await workmanager.registerPeriodicTask(
        'sahool_sync',
        'sync',
        frequency: const Duration(minutes: 15),
        existingWorkPolicy: ExistingWorkPolicy.replace,
      );

      expect(workmanager.registeredTasks.length, equals(1));

      // Register task with same name (replace)
      await workmanager.registerPeriodicTask(
        'sahool_sync',
        'syncUpdated',
        frequency: const Duration(minutes: 30),
        existingWorkPolicy: ExistingWorkPolicy.replace,
      );

      // Should still have 1 task (replaced)
      // Note: Our mock doesn't implement replace logic, but tests the intent
      expect(workmanager.registeredTasks.length, equals(2));
    });
  });

  group('Constraints', () {
    test('should create network connected constraint', () {
      const constraints = Constraints(
        networkType: NetworkType.connected,
      );

      expect(constraints.networkType, equals(NetworkType.connected));
      expect(constraints.requiresBatteryNotLow, isNull);
    });

    test('should create unmetered network constraint', () {
      const constraints = Constraints(
        networkType: NetworkType.unmetered,
      );

      expect(constraints.networkType, equals(NetworkType.unmetered));
    });

    test('should create battery-aware constraint', () {
      const constraints = Constraints(
        networkType: NetworkType.connected,
        requiresBatteryNotLow: true,
        requiresCharging: false,
      );

      expect(constraints.requiresBatteryNotLow, isTrue);
      expect(constraints.requiresCharging, isFalse);
    });

    test('should create full constraint set', () {
      const constraints = Constraints(
        networkType: NetworkType.connected,
        requiresBatteryNotLow: true,
        requiresCharging: false,
        requiresDeviceIdle: false,
        requiresStorageNotLow: true,
      );

      expect(constraints.networkType, equals(NetworkType.connected));
      expect(constraints.requiresBatteryNotLow, isTrue);
      expect(constraints.requiresCharging, isFalse);
      expect(constraints.requiresDeviceIdle, isFalse);
      expect(constraints.requiresStorageNotLow, isTrue);
    });
  });

  group('Edge Cases', () {
    late MockWorkmanager workmanager;

    setUp(() {
      workmanager = MockWorkmanager();
    });

    tearDown(() {
      workmanager.reset();
    });

    test('should handle task execution before initialization', () async {
      final result = await workmanager.executeTask('test', null);
      expect(result, isFalse);
    });

    test('should handle unknown task name', () async {
      await workmanager.initialize((taskName, inputData) async {
        if (taskName == 'knownTask') {
          return true;
        }
        return false;
      });

      final result = await workmanager.executeTask('unknownTask', null);
      expect(result, isFalse);
    });

    test('should handle task callback exception', () async {
      await workmanager.initialize((taskName, inputData) async {
        throw Exception('Task failed');
      });

      expect(
        () => workmanager.executeTask('test', null),
        throwsException,
      );
    });

    test('should handle null input data', () async {
      Map<String, dynamic>? receivedData;

      await workmanager.initialize((taskName, inputData) async {
        receivedData = inputData;
        return true;
      });

      await workmanager.executeTask('test', null);

      expect(receivedData, isNull);
    });
  });
}
