import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sahool_field_app/features/tasks/data/repo/tasks_repo.dart';
import 'package:sahool_field_app/features/tasks/data/remote/tasks_api.dart';
import 'package:sahool_field_app/features/tasks/domain/entities/task.dart';
import '../../../mocks/mock_app_database.dart';
import '../../../mocks/mock_network_status.dart';
import '../../../fixtures/sample_tasks.dart';

/// Mock TasksApi for testing
class MockTasksApi extends Mock implements TasksApi {}

void main() {
  group('TasksRepo', () {
    late TasksRepo tasksRepo;
    late MockAppDatabase mockDatabase;
    late MockTasksApi mockApi;
    late MockNetworkStatus mockNetworkStatus;

    setUp(() {
      mockDatabase = MockAppDatabase();
      mockApi = MockTasksApi();
      mockNetworkStatus = MockNetworkStatus(isOnline: true);

      tasksRepo = TasksRepo(
        database: mockDatabase,
        api: mockApi,
        networkStatus: mockNetworkStatus,
      );

      // Clear database before each test
      mockDatabase.clearAll();
    });

    group('getAllTasks', () {
      test('should return tasks from local database', () async {
        // Arrange
        const tenantId = 'tenant_test';
        final task1 = SampleTasks.createPendingTask(tenantId: tenantId);
        final task2 = SampleTasks.createCompletedTask(tenantId: tenantId);

        mockDatabase.seedTask(task1);
        mockDatabase.seedTask(task2);

        // Act
        final tasks = await tasksRepo.getAllTasks(tenantId);

        // Assert
        expect(tasks.length, 2);
        expect(tasks.any((t) => t.id == task1.id), isTrue);
        expect(tasks.any((t) => t.id == task2.id), isTrue);
      });

      test('should return empty list when no tasks', () async {
        // Act
        final tasks = await tasksRepo.getAllTasks('tenant_test');

        // Assert
        expect(tasks, isEmpty);
      });

      test('should only return tasks for specified tenant', () async {
        // Arrange
        final task1 = SampleTasks.createPendingTask(tenantId: 'tenant_1');
        final task2 = SampleTasks.createPendingTask(tenantId: 'tenant_2');

        mockDatabase.seedTask(task1);
        mockDatabase.seedTask(task2);

        // Act
        final tasks = await tasksRepo.getAllTasks('tenant_1');

        // Assert
        expect(tasks.length, 1);
        expect(tasks.first.tenantId, 'tenant_1');
      });
    });

    group('getTasksForField', () {
      test('should return tasks for specific field', () async {
        // Arrange
        const fieldId = 'field_001';
        final task1 = SampleTasks.createPendingTask(fieldId: fieldId);
        final task2 = SampleTasks.createCompletedTask(fieldId: fieldId);
        final task3 = SampleTasks.createPendingTask(fieldId: 'field_002');

        mockDatabase.seedTask(task1);
        mockDatabase.seedTask(task2);
        mockDatabase.seedTask(task3);

        // Act
        final tasks = await tasksRepo.getTasksForField(fieldId);

        // Assert
        expect(tasks.length, 2);
        expect(tasks.every((t) => t.fieldId == fieldId), isTrue);
      });
    });

    group('getPendingTasks', () {
      test('should return only open and in_progress tasks', () async {
        // Arrange
        const tenantId = 'tenant_test';
        final pendingTask = SampleTasks.createPendingTask(tenantId: tenantId);
        final inProgressTask = SampleTasks.createInProgressTask(tenantId: tenantId);
        final completedTask = SampleTasks.createCompletedTask(tenantId: tenantId);

        mockDatabase.seedTask(pendingTask);
        mockDatabase.seedTask(inProgressTask);
        mockDatabase.seedTask(completedTask);

        // Act
        final tasks = await tasksRepo.getPendingTasks(tenantId);

        // Assert
        expect(tasks.length, 2);
        expect(tasks.any((t) => t.status == TaskStatus.open), isTrue);
        expect(tasks.any((t) => t.status == TaskStatus.inProgress), isTrue);
        expect(tasks.any((t) => t.status == TaskStatus.done), isFalse);
      });

      test('should sort by due date', () async {
        // Arrange
        const tenantId = 'tenant_test';
        final task1 = SampleTasks.createPendingTask(
          id: 'task_1',
          tenantId: tenantId,
        );
        final task2 = SampleTasks.createPendingTask(
          id: 'task_2',
          tenantId: tenantId,
        );

        // Make task2 have earlier due date
        mockDatabase.seedTask(task1.copyWith(
          dueDate: DateTime.now().add(const Duration(days: 5)),
        ));
        mockDatabase.seedTask(task2.copyWith(
          dueDate: DateTime.now().add(const Duration(days: 2)),
        ));

        // Act
        final tasks = await tasksRepo.getPendingTasks(tenantId);

        // Assert - task2 should come first (earlier due date)
        expect(tasks.first.id, 'task_2');
      });
    });

    group('getTaskById', () {
      test('should return task when found', () async {
        // Arrange
        const taskId = 'task_001';
        final task = SampleTasks.createPendingTask(id: taskId);
        mockDatabase.seedTask(task);

        // Act
        final result = await tasksRepo.getTaskById(taskId);

        // Assert
        expect(result, isNotNull);
        expect(result!.id, taskId);
      });

      test('should return null when not found', () async {
        // Act
        final result = await tasksRepo.getTaskById('nonexistent');

        // Assert
        expect(result, isNull);
      });
    });

    group('completeTaskOfflineFirst', () {
      test('should mark task as done locally', () async {
        // Arrange
        const taskId = 'task_001';
        const notes = 'Task completed successfully';
        final photos = ['photo1.jpg', 'photo2.jpg'];

        final task = SampleTasks.createPendingTask(id: taskId);
        mockDatabase.seedTask(task);

        // Act
        await tasksRepo.completeTaskOfflineFirst(
          taskId: taskId,
          notes: notes,
          photos: photos,
        );

        // Assert
        final updatedTask = await mockDatabase.getTaskById(taskId);
        expect(updatedTask!.status, 'done');
        expect(updatedTask.evidenceNotes, notes);
        expect(updatedTask.synced, isFalse);
      });

      test('should queue task completion in outbox', () async {
        // Arrange
        const taskId = 'task_001';
        final task = SampleTasks.createPendingTask(id: taskId);
        mockDatabase.seedTask(task);

        // Act
        await tasksRepo.completeTaskOfflineFirst(taskId: taskId);

        // Assert
        final outboxItems = await mockDatabase.getPendingOutbox();
        expect(outboxItems.length, 1);
        expect(outboxItems.first.entityType, 'task');
        expect(outboxItems.first.entityId, taskId);
        expect(outboxItems.first.method, 'PUT');
      });
    });

    group('updateTaskStatus', () {
      test('should update task status locally', () async {
        // Arrange
        const taskId = 'task_001';
        final task = SampleTasks.createPendingTask(id: taskId);
        mockDatabase.seedTask(task);

        // Act
        await tasksRepo.updateTaskStatus(
          taskId: taskId,
          status: TaskStatus.inProgress,
        );

        // Assert
        final updatedTask = await mockDatabase.getTaskById(taskId);
        expect(updatedTask!.status, 'in_progress');
        expect(updatedTask.synced, isFalse);
      });

      test('should queue status update in outbox', () async {
        // Arrange
        const taskId = 'task_001';
        final task = SampleTasks.createPendingTask(id: taskId);
        mockDatabase.seedTask(task);

        // Act
        await tasksRepo.updateTaskStatus(
          taskId: taskId,
          status: TaskStatus.inProgress,
        );

        // Assert
        final outboxItems = await mockDatabase.getPendingOutbox();
        expect(outboxItems, isNotEmpty);
        expect(outboxItems.first.entityType, 'task');
      });
    });

    group('createTask', () {
      test('should create task locally', () async {
        // Arrange
        const tenantId = 'tenant_test';
        const fieldId = 'field_001';
        const title = 'New Task';
        const description = 'Task description';

        // Act
        final task = await tasksRepo.createTask(
          tenantId: tenantId,
          fieldId: fieldId,
          title: title,
          description: description,
          priority: TaskPriority.high,
        );

        // Assert
        expect(task.title, title);
        expect(task.description, description);
        expect(task.fieldId, fieldId);
        expect(task.status, TaskStatus.open);
        expect(task.priority, TaskPriority.high);

        // Verify saved in database
        final savedTask = await mockDatabase.getTaskById(task.id);
        expect(savedTask, isNotNull);
      });

      test('should queue new task in outbox', () async {
        // Arrange & Act
        await tasksRepo.createTask(
          tenantId: 'tenant_test',
          fieldId: 'field_001',
          title: 'New Task',
        );

        // Assert
        final outboxItems = await mockDatabase.getPendingOutbox();
        expect(outboxItems, isNotEmpty);
        expect(outboxItems.first.method, 'POST');
        expect(outboxItems.first.apiEndpoint, '/api/v1/tasks');
      });

      test('should generate unique ID for each task', () async {
        // Act
        final task1 = await tasksRepo.createTask(
          tenantId: 'tenant_test',
          fieldId: 'field_001',
          title: 'Task 1',
        );

        final task2 = await tasksRepo.createTask(
          tenantId: 'tenant_test',
          fieldId: 'field_001',
          title: 'Task 2',
        );

        // Assert
        expect(task1.id, isNot(equals(task2.id)));
      });
    });

    group('refreshFromServer', () {
      test('should throw when offline', () async {
        // Arrange
        mockNetworkStatus.setOnlineStatus(false);

        // Act & Assert
        expect(
          () => tasksRepo.refreshFromServer(),
          throwsA(isA<Exception>()),
        );
      });

      test('should fetch and save tasks from server', () async {
        // Arrange
        mockNetworkStatus.setOnlineStatus(true);

        final serverTasks = [
          FieldTask(
            id: 'server_task_1',
            tenantId: 'tenant_test',
            fieldId: 'field_001',
            title: 'Server Task',
            status: TaskStatus.open,
            priority: TaskPriority.medium,
            createdAt: DateTime.now(),
            updatedAt: DateTime.now(),
            synced: true,
          ),
        ];

        when(() => mockApi.fetchTasks(fieldId: any(named: 'fieldId')))
            .thenAnswer((_) async => serverTasks);

        // Act
        final count = await tasksRepo.refreshFromServer();

        // Assert
        expect(count, serverTasks.length);
        verify(() => mockApi.fetchTasks(fieldId: any(named: 'fieldId'))).called(1);
      });
    });
  });
}
