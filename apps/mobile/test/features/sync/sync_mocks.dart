import 'dart:async';

import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:dio/dio.dart';
import 'package:mocktail/mocktail.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// Sync Feature Mocks
/// موكات ميزة المزامنة
///
/// Using mocktail for mock creation and verification

// =============================================================================
// Connectivity Mocks
// =============================================================================

/// Mock for Connectivity class
class MockConnectivity extends Mock implements Connectivity {}

// Note: ConnectivityResult is an enum and cannot be faked with mocktail.
// Use real enum values like ConnectivityResult.none as fallback instead.

/// Mock network status class for testing
class MockNetworkStatus {
  bool _isOnline = true;
  final _onlineController = StreamController<bool>.broadcast();

  Stream<bool> get onlineStream => _onlineController.stream;
  bool get isOnline => _isOnline;

  void setOnline(bool online) {
    _isOnline = online;
    _onlineController.add(online);
  }

  Future<bool> checkOnline() async => _isOnline;

  void dispose() {
    _onlineController.close();
  }
}

// =============================================================================
// HTTP/API Mocks
// =============================================================================

/// Mock for Dio HTTP client
class MockDio extends Mock implements Dio {}

/// Mock Response for API calls
class MockResponse<T> extends Mock implements Response<T> {}

/// Fake RequestOptions for stubbing
class FakeRequestOptions extends Fake implements RequestOptions {}

/// Fake DioException for testing error scenarios
class FakeDioException extends Fake implements DioException {}

// =============================================================================
// Database Mocks
// =============================================================================

/// Mock outbox data for testing
class MockOutboxData {
  final int id;
  final String tenantId;
  final String entityType;
  final String entityId;
  final String apiEndpoint;
  final String method;
  final String payload;
  final String? ifMatch;
  final int retryCount;
  final DateTime createdAt;
  final bool synced;

  const MockOutboxData({
    required this.id,
    required this.tenantId,
    required this.entityType,
    required this.entityId,
    required this.apiEndpoint,
    required this.method,
    required this.payload,
    this.ifMatch,
    this.retryCount = 0,
    required this.createdAt,
    this.synced = false,
  });

  MockOutboxData copyWith({
    int? id,
    String? tenantId,
    String? entityType,
    String? entityId,
    String? apiEndpoint,
    String? method,
    String? payload,
    String? ifMatch,
    int? retryCount,
    DateTime? createdAt,
    bool? synced,
  }) {
    return MockOutboxData(
      id: id ?? this.id,
      tenantId: tenantId ?? this.tenantId,
      entityType: entityType ?? this.entityType,
      entityId: entityId ?? this.entityId,
      apiEndpoint: apiEndpoint ?? this.apiEndpoint,
      method: method ?? this.method,
      payload: payload ?? this.payload,
      ifMatch: ifMatch ?? this.ifMatch,
      retryCount: retryCount ?? this.retryCount,
      createdAt: createdAt ?? this.createdAt,
      synced: synced ?? this.synced,
    );
  }
}

/// Mock database for testing sync operations
class MockSyncDatabase {
  final List<MockOutboxData> _outbox = [];
  final List<Map<String, dynamic>> _syncLogs = [];
  final List<Map<String, dynamic>> _syncEvents = [];
  int _idCounter = 1;

  /// Add item to outbox
  Future<int> queueOutboxItem({
    required String tenantId,
    required String entityType,
    required String entityId,
    required String apiEndpoint,
    required String method,
    required String payload,
    String? ifMatch,
  }) async {
    final id = _idCounter++;
    _outbox.add(MockOutboxData(
      id: id,
      tenantId: tenantId,
      entityType: entityType,
      entityId: entityId,
      apiEndpoint: apiEndpoint,
      method: method,
      payload: payload,
      ifMatch: ifMatch,
      createdAt: DateTime.now(),
    ));
    return id;
  }

  /// Get pending outbox items
  Future<List<MockOutboxData>> getPendingOutbox({int? limit}) async {
    final pending = _outbox.where((item) => !item.synced).toList();
    if (limit != null && pending.length > limit) {
      return pending.sublist(0, limit);
    }
    return pending;
  }

  /// Mark outbox item as done
  Future<void> markOutboxDone(int id) async {
    final index = _outbox.indexWhere((item) => item.id == id);
    if (index >= 0) {
      _outbox[index] = _outbox[index].copyWith(synced: true);
    }
  }

  /// Bump retry count for failed item
  Future<void> bumpOutboxRetry(int id) async {
    final index = _outbox.indexWhere((item) => item.id == id);
    if (index >= 0) {
      _outbox[index] = _outbox[index].copyWith(
        retryCount: _outbox[index].retryCount + 1,
      );
    }
  }

  /// Log sync operation
  Future<void> logSync({
    required String type,
    required String status,
    required String message,
  }) async {
    _syncLogs.add({
      'type': type,
      'status': status,
      'message': message,
      'timestamp': DateTime.now().toIso8601String(),
    });
  }

  /// Get recent sync logs
  Future<List<Map<String, dynamic>>> getRecentSyncLogs({int limit = 100}) async {
    if (_syncLogs.length > limit) {
      return _syncLogs.sublist(_syncLogs.length - limit);
    }
    return List.from(_syncLogs);
  }

  /// Add sync event
  Future<void> addSyncEvent({
    required String tenantId,
    required String type,
    required String message,
    String? entityType,
    String? entityId,
  }) async {
    _syncEvents.add({
      'tenantId': tenantId,
      'type': type,
      'message': message,
      'entityType': entityType,
      'entityId': entityId,
      'timestamp': DateTime.now().toIso8601String(),
    });
  }

  /// Cleanup completed outbox items
  Future<void> cleanupOutbox() async {
    _outbox.removeWhere((item) => item.synced);
  }

  /// Clear all data (for testing)
  void reset() {
    _outbox.clear();
    _syncLogs.clear();
    _syncEvents.clear();
    _idCounter = 1;
  }

  /// Get sync events
  List<Map<String, dynamic>> get syncEvents => List.from(_syncEvents);

  /// Get sync logs
  List<Map<String, dynamic>> get syncLogs => List.from(_syncLogs);

  /// Get outbox items
  List<MockOutboxData> get outbox => List.from(_outbox);
}

// =============================================================================
// Test Fixtures
// =============================================================================

/// Sync test fixtures
class SyncTestFixtures {
  /// Create a mock outbox entry for field update
  static MockOutboxData createFieldUpdateOutboxItem({
    int id = 1,
    String fieldId = 'field_001',
    String? ifMatch,
    int retryCount = 0,
  }) {
    return MockOutboxData(
      id: id,
      tenantId: 'tenant_1',
      entityType: 'field',
      entityId: fieldId,
      apiEndpoint: '/api/v1/fields/$fieldId',
      method: 'PUT',
      payload: '{"id": "$fieldId", "name": "Updated Field", "area": 150.5}',
      ifMatch: ifMatch,
      retryCount: retryCount,
      createdAt: DateTime.now(),
    );
  }

  /// Create a mock outbox entry for task creation
  static MockOutboxData createTaskCreateOutboxItem({
    int id = 1,
    String taskId = 'task_001',
    int retryCount = 0,
  }) {
    return MockOutboxData(
      id: id,
      tenantId: 'tenant_1',
      entityType: 'task',
      entityId: taskId,
      apiEndpoint: '/api/v1/tasks',
      method: 'POST',
      payload: '{"title": "New Task", "field_id": "field_001"}',
      retryCount: retryCount,
      createdAt: DateTime.now(),
    );
  }

  /// Create a mock outbox entry for task deletion
  static MockOutboxData createDeleteOutboxItem({
    int id = 1,
    String entityType = 'task',
    String entityId = 'task_001',
    int retryCount = 0,
  }) {
    return MockOutboxData(
      id: id,
      tenantId: 'tenant_1',
      entityType: entityType,
      entityId: entityId,
      apiEndpoint: '/api/v1/$entityType/$entityId',
      method: 'DELETE',
      payload: '{}',
      retryCount: retryCount,
      createdAt: DateTime.now(),
    );
  }

  /// Sample local data for conflict testing
  static Map<String, dynamic> get sampleLocalData => {
    'id': 'field_001',
    'name': 'Local Field Name',
    'area': 100.0,
    'updatedAt': DateTime.now().subtract(const Duration(hours: 1)).toIso8601String(),
  };

  /// Sample server data for conflict testing
  static Map<String, dynamic> get sampleServerData => {
    'id': 'field_001',
    'name': 'Server Field Name',
    'area': 150.0,
    'updatedAt': DateTime.now().toIso8601String(),
  };

  /// Sample base data for conflict testing
  static Map<String, dynamic> get sampleBaseData => {
    'id': 'field_001',
    'name': 'Original Field Name',
    'area': 100.0,
    'updatedAt': DateTime.now().subtract(const Duration(hours: 2)).toIso8601String(),
  };

  /// Create multiple outbox items with different priorities
  static List<MockOutboxData> createMixedPriorityOutboxItems() {
    return [
      // Low priority: metadata update
      MockOutboxData(
        id: 1,
        tenantId: 'tenant_1',
        entityType: 'metadata',
        entityId: 'meta_001',
        apiEndpoint: '/api/v1/metadata/meta_001',
        method: 'PUT',
        payload: '{"key": "value"}',
        createdAt: DateTime.now().subtract(const Duration(minutes: 5)),
      ),
      // Normal priority: field update
      MockOutboxData(
        id: 2,
        tenantId: 'tenant_1',
        entityType: 'field',
        entityId: 'field_001',
        apiEndpoint: '/api/v1/fields/field_001',
        method: 'PUT',
        payload: '{"name": "Updated"}',
        createdAt: DateTime.now().subtract(const Duration(minutes: 4)),
      ),
      // High priority: task update
      MockOutboxData(
        id: 3,
        tenantId: 'tenant_1',
        entityType: 'task',
        entityId: 'task_001',
        apiEndpoint: '/api/v1/tasks/task_001',
        method: 'PUT',
        payload: '{"status": "completed"}',
        createdAt: DateTime.now().subtract(const Duration(minutes: 3)),
      ),
      // Critical priority: delete
      MockOutboxData(
        id: 4,
        tenantId: 'tenant_1',
        entityType: 'task',
        entityId: 'task_002',
        apiEndpoint: '/api/v1/tasks/task_002',
        method: 'DELETE',
        payload: '{}',
        createdAt: DateTime.now().subtract(const Duration(minutes: 2)),
      ),
    ];
  }
}

// =============================================================================
// Setup Helpers
// =============================================================================

/// Setup SharedPreferences mock for testing
Future<void> setupSharedPreferencesMock([Map<String, Object>? values]) async {
  SharedPreferences.setMockInitialValues(values ?? {});
}

/// Register fallback values for mocktail
void registerSyncFallbackValues() {
  registerFallbackValue(FakeRequestOptions());
  registerFallbackValue([ConnectivityResult.none]);
}
