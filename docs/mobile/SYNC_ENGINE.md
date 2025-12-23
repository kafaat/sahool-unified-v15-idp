# Sync Engine Documentation
# توثيق محرك المزامنة

> **الغرض:** مزامنة البيانات المحلية مع الخادم بشكل موثوق وفعّال

---

## نظرة عامة | Overview

محرك المزامنة مسؤول عن:
1. تتبع التغييرات المحلية
2. مزامنة التغييرات عند توفر الاتصال
3. حل التعارضات
4. ضمان تكامل البيانات

```
┌─────────────────────────────────────────────────────────────────┐
│                      SYNC ENGINE FLOW                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐  │
│  │  Local   │───▶│  Sync    │───▶│ Conflict │───▶│  Remote  │  │
│  │  Changes │    │  Queue   │    │ Resolver │    │  Server  │  │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘  │
│       │                │                               │        │
│       │                │         ┌──────────┐         │        │
│       │                └────────▶│  Retry   │◀────────┘        │
│       │                          │  Queue   │                   │
│       │                          └──────────┘                   │
│       │                                                         │
│       └───────────────────[Optimistic Update]──────────────────▶│
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## هيكل المحرك | Engine Architecture

### المكونات الرئيسية

```dart
/// محرك المزامنة الرئيسي
class SyncEngine {
  final SyncQueue _queue;
  final ConflictResolver _conflictResolver;
  final ApiClient _apiClient;
  final ConnectivityMonitor _connectivity;
  final RetryPolicy _retryPolicy;

  /// بدء المزامنة
  Future<SyncResult> sync() async {
    if (!await _connectivity.hasConnection) {
      return SyncResult.offline();
    }

    final pending = await _queue.getPending();
    if (pending.isEmpty) {
      return SyncResult.upToDate();
    }

    return _processBatch(pending);
  }
}
```

### طابور المزامنة

```dart
/// عمليات المزامنة المعلقة
@DataClassName('SyncQueueEntry')
class SyncQueue extends Table {
  IntColumn get id => integer().autoIncrement()();
  TextColumn get entityType => text()();      // task, field, alert
  TextColumn get entityId => text()();        // UUID
  TextColumn get operation => text()();       // create, update, delete
  TextColumn get payload => text()();         // JSON data
  IntColumn get createdAt => integer()();     // timestamp
  IntColumn get retryCount => integer().withDefault(const Constant(0))();
  TextColumn get lastError => text().nullable()();
  IntColumn get priority => integer().withDefault(const Constant(0))();
}
```

---

## أنواع العمليات | Operation Types

### 1. Create (إنشاء)

```dart
class CreateSyncOperation extends SyncOperation {
  @override
  Future<SyncOperationResult> execute(ApiClient api) async {
    final response = await api.post(
      endpoint: '/${entityType}s',
      body: payload,
    );

    if (response.isSuccess) {
      // تحديث ID المحلي بالـ ID من الخادم
      await _updateLocalId(entityId, response.data['id']);
      return SyncOperationResult.success();
    }

    return SyncOperationResult.failed(response.error);
  }
}
```

### 2. Update (تحديث)

```dart
class UpdateSyncOperation extends SyncOperation {
  @override
  Future<SyncOperationResult> execute(ApiClient api) async {
    // جلب النسخة الحالية من الخادم
    final remote = await api.get('/${entityType}s/$entityId');

    // فحص التعارضات
    if (remote.updatedAt > localUpdatedAt) {
      return _handleConflict(remote);
    }

    // تطبيق التحديث
    final response = await api.patch(
      endpoint: '/${entityType}s/$entityId',
      body: payload,
    );

    return response.isSuccess
        ? SyncOperationResult.success()
        : SyncOperationResult.failed(response.error);
  }
}
```

### 3. Delete (حذف)

```dart
class DeleteSyncOperation extends SyncOperation {
  @override
  Future<SyncOperationResult> execute(ApiClient api) async {
    final response = await api.delete('/${entityType}s/$entityId');

    if (response.isSuccess || response.statusCode == 404) {
      // حذف ناجح أو العنصر محذوف مسبقاً
      await _confirmLocalDeletion(entityId);
      return SyncOperationResult.success();
    }

    return SyncOperationResult.failed(response.error);
  }
}
```

---

## سياسة إعادة المحاولة | Retry Policy

```dart
class RetryPolicy {
  static const int maxRetries = 5;

  static const List<Duration> backoffDelays = [
    Duration(seconds: 1),
    Duration(seconds: 5),
    Duration(seconds: 30),
    Duration(minutes: 5),
    Duration(minutes: 30),
  ];

  /// هل يجب إعادة المحاولة؟
  bool shouldRetry(SyncQueueEntry entry, Exception error) {
    // لا إعادة محاولة للأخطاء الدائمة
    if (error is PermanentError) return false;

    // لا إعادة محاولة بعد الحد الأقصى
    if (entry.retryCount >= maxRetries) return false;

    // إعادة محاولة للأخطاء المؤقتة
    return error is NetworkException ||
           error is TimeoutException ||
           error is ServerException && error.statusCode >= 500;
  }

  /// وقت الانتظار قبل المحاولة التالية
  Duration getDelay(int retryCount) {
    return backoffDelays[min(retryCount, backoffDelays.length - 1)];
  }
}
```

---

## المزامنة الخلفية | Background Sync

### إعداد Workmanager

```dart
void initBackgroundSync() {
  Workmanager().initialize(
    callbackDispatcher,
    isInDebugMode: kDebugMode,
  );

  // مزامنة دورية كل 15 دقيقة
  Workmanager().registerPeriodicTask(
    'periodic-sync',
    'syncPendingChanges',
    frequency: Duration(minutes: 15),
    constraints: Constraints(
      networkType: NetworkType.connected,
      requiresBatteryNotLow: true,
    ),
  );
}

@pragma('vm:entry-point')
void callbackDispatcher() {
  Workmanager().executeTask((task, inputData) async {
    final engine = await SyncEngine.initialize();
    final result = await engine.sync();

    // إرسال إشعار عند وجود تعارضات
    if (result.hasConflicts) {
      await _showConflictNotification(result.conflicts);
    }

    return result.isSuccess;
  });
}
```

### مشغلات المزامنة

```dart
class SyncTriggers {
  /// عند استعادة الاتصال
  void onConnectivityRestored() {
    SyncEngine.instance.sync();
  }

  /// عند فتح التطبيق
  void onAppResume() {
    SyncEngine.instance.sync();
  }

  /// عند إنشاء/تعديل محلي
  void onLocalChange(String entityType, String entityId) {
    // مزامنة فورية إذا متصل
    if (ConnectivityMonitor.isOnline) {
      SyncEngine.instance.syncEntity(entityType, entityId);
    }
  }

  /// عند تلقي Push Notification
  void onPushReceived(String topic) {
    SyncEngine.instance.pullChanges(topic);
  }
}
```

---

## تتبع حالة المزامنة | Sync Status Tracking

### حالات المزامنة

```dart
enum SyncStatus {
  /// متزامن مع الخادم
  synced,

  /// ينتظر المزامنة
  pending,

  /// قيد المزامنة
  syncing,

  /// فشلت المزامنة
  failed,

  /// يوجد تعارض
  conflict,
}

/// امتداد للكيانات
mixin Syncable {
  String get id;
  SyncStatus get syncStatus;
  DateTime? get syncedAt;
  DateTime get updatedAt;

  bool get needsSync => syncStatus != SyncStatus.synced;
  bool get hasConflict => syncStatus == SyncStatus.conflict;
}
```

### واجهة المستخدم

```dart
/// أيقونة حالة المزامنة
class SyncStatusIndicator extends StatelessWidget {
  final SyncStatus status;

  @override
  Widget build(BuildContext context) {
    return switch (status) {
      SyncStatus.synced => Icon(Icons.cloud_done, color: Colors.green),
      SyncStatus.pending => Icon(Icons.cloud_upload, color: Colors.orange),
      SyncStatus.syncing => CircularProgressIndicator(strokeWidth: 2),
      SyncStatus.failed => Icon(Icons.cloud_off, color: Colors.red),
      SyncStatus.conflict => Icon(Icons.warning, color: Colors.amber),
    };
  }
}
```

---

## مراقبة الأداء | Performance Monitoring

### مقاييس المزامنة

```dart
class SyncMetrics {
  /// متوسط وقت المزامنة
  Duration averageSyncTime;

  /// عدد العمليات الناجحة
  int successCount;

  /// عدد العمليات الفاشلة
  int failureCount;

  /// عدد التعارضات
  int conflictCount;

  /// آخر مزامنة ناجحة
  DateTime? lastSuccessfulSync;

  /// حجم الطابور الحالي
  int pendingQueueSize;

  double get successRate =>
      successCount / (successCount + failureCount) * 100;
}

/// تسجيل المقاييس
class SyncLogger {
  void logSyncResult(SyncResult result) {
    _analytics.track('sync_completed', {
      'duration_ms': result.duration.inMilliseconds,
      'operations_count': result.operationsCount,
      'success_count': result.successCount,
      'failure_count': result.failureCount,
      'conflict_count': result.conflictCount,
    });
  }
}
```

---

## معالجة الأخطاء | Error Handling

### أنواع الأخطاء

```dart
/// أخطاء مؤقتة - إعادة محاولة
class TransientError extends SyncException {
  // انقطاع الشبكة، timeout، خطأ 5xx
}

/// أخطاء دائمة - لا إعادة محاولة
class PermanentError extends SyncException {
  // 400 Bad Request, 401 Unauthorized, 404 Not Found
}

/// تعارض - يحتاج تدخل
class ConflictError extends SyncException {
  final dynamic localVersion;
  final dynamic remoteVersion;
}
```

### معالجة الأخطاء

```dart
class SyncErrorHandler {
  Future<void> handleError(
    SyncQueueEntry entry,
    SyncException error,
  ) async {
    if (error is PermanentError) {
      // نقل للأرشيف مع تسجيل
      await _archiveFailedOperation(entry, error);
      _notifyUser('فشل مزامنة: ${entry.entityType}');
      return;
    }

    if (error is ConflictError) {
      // تحديث الحالة وانتظار حل المستخدم
      await _markAsConflict(entry, error);
      _notifyUser('يوجد تعارض يحتاج مراجعة');
      return;
    }

    // خطأ مؤقت - جدولة إعادة محاولة
    if (_retryPolicy.shouldRetry(entry, error)) {
      await _scheduleRetry(entry);
    } else {
      await _archiveFailedOperation(entry, error);
    }
  }
}
```

---

## التحسينات | Optimizations

### دمج العمليات

```dart
/// دمج عمليات متعددة على نفس الكيان
class OperationCoalescer {
  List<SyncOperation> coalesce(List<SyncOperation> operations) {
    final grouped = groupBy(operations, (op) => op.entityId);

    return grouped.entries.map((entry) {
      final ops = entry.value;

      // create + update = create with latest data
      // create + delete = nothing
      // update + update = single update with merged data
      // update + delete = delete
      // delete + create = update (resurrection)

      return _mergeOperations(ops);
    }).whereNotNull().toList();
  }
}
```

### مزامنة تفاضلية

```dart
/// فقط التغييرات منذ آخر مزامنة
class DeltaSync {
  Future<void> pullChanges() async {
    final lastSync = await _getLastSyncTimestamp();

    final changes = await _api.getChanges(
      since: lastSync,
      entities: ['tasks', 'fields', 'alerts'],
    );

    await _applyChanges(changes);
    await _updateSyncTimestamp();
  }
}
```

---

## الموارد | Resources

- [OFFLINE_FIRST.md](./OFFLINE_FIRST.md)
- [CONFLICT_RESOLUTION.md](./CONFLICT_RESOLUTION.md)
- [ADR-001: Offline-First Architecture](../adr/ADR-001-offline-first-architecture.md)

---

<p align="center">
  <sub>SAHOOL Mobile - Sync Engine</sub>
</p>
