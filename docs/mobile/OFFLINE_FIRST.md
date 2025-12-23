# Offline-First Strategy
# استراتيجية Offline-First

> **المبدأ:** التطبيق يعمل بالكامل بدون إنترنت، والمزامنة تحدث عند توفر الاتصال

---

## لماذا Offline-First؟ | Why Offline-First?

### واقع المزارع اليمني

```
┌─────────────────────────────────────────────────────────────────┐
│                    FIELD CONNECTIVITY REALITY                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  🏔️ المناطق الجبلية: تغطية ضعيفة (2G أو لا شيء)                │
│  🌾 الحقول البعيدة: انقطاع متكرر                                │
│  ⚡ انقطاع الكهرباء: أبراج الاتصال تتوقف                        │
│  📱 شحن الهاتف: محدود في بعض المناطق                            │
│                                                                  │
│  الحل: التطبيق يعمل 100% بدون إنترنت                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## المبادئ الأساسية | Core Principles

### 1. Local-First (المحلي أولاً)

```dart
// كل عملية تكتب محلياً أولاً
class TaskRepository {
  Future<Task> createTask(TaskInput input) async {
    // الخطوة 1: حفظ محلي فوري
    final task = await _localDb.insertTask(input);

    // الخطوة 2: إضافة للطابور
    await _syncQueue.enqueue(SyncOperation.create(task));

    // الخطوة 3: إرجاع النتيجة فوراً
    return task; // المستخدم لا ينتظر الشبكة
  }
}
```

### 2. Optimistic Updates (التحديثات المتفائلة)

```dart
// الواجهة تتحدث فوراً، والتراجع عند الفشل
class TaskNotifier extends StateNotifier<TaskState> {
  Future<void> completeTask(String taskId) async {
    // تحديث فوري في الواجهة
    state = state.markCompleted(taskId);

    try {
      await _repository.completeTask(taskId);
    } catch (e) {
      // تراجع عند الفشل
      state = state.revert(taskId);
      _showError('فشل تحديث المهمة');
    }
  }
}
```

### 3. Background Sync (المزامنة الخلفية)

```dart
// المزامنة تحدث في الخلفية بدون تدخل المستخدم
@pragma('vm:entry-point')
void callbackDispatcher() {
  Workmanager().executeTask((task, inputData) async {
    final syncEngine = SyncEngine();
    await syncEngine.syncPendingChanges();
    return Future.value(true);
  });
}
```

---

## هيكل البيانات المحلية | Local Data Structure

### قاعدة البيانات (Drift/SQLite)

```dart
@DriftDatabase(tables: [
  Tasks,
  Fields,
  Alerts,
  SyncQueue,
  CacheMetadata,
])
class AppDatabase extends _$AppDatabase {
  @override
  int get schemaVersion => 16;

  @override
  MigrationStrategy get migration => MigrationStrategy(
    onCreate: (m) async {
      await m.createAll();
      await _seedDefaultData();
    },
    onUpgrade: (m, from, to) async {
      // ترحيل البيانات القديمة
      await _runMigrations(m, from, to);
    },
  );
}
```

### جداول البيانات

```sql
-- المهام
CREATE TABLE tasks (
  id TEXT PRIMARY KEY,
  field_id TEXT NOT NULL,
  title TEXT NOT NULL,
  description TEXT,
  priority TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending',
  due_date INTEGER,
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL,
  synced_at INTEGER,
  sync_status TEXT NOT NULL DEFAULT 'pending',
  FOREIGN KEY (field_id) REFERENCES fields(id)
);

-- طابور المزامنة
CREATE TABLE sync_queue (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  entity_type TEXT NOT NULL,
  entity_id TEXT NOT NULL,
  operation TEXT NOT NULL, -- create, update, delete
  payload TEXT NOT NULL,
  created_at INTEGER NOT NULL,
  retry_count INTEGER DEFAULT 0,
  last_error TEXT,
  priority INTEGER DEFAULT 0
);

-- البيانات المؤقتة
CREATE TABLE cache_metadata (
  key TEXT PRIMARY KEY,
  expires_at INTEGER NOT NULL,
  etag TEXT,
  last_modified INTEGER
);
```

---

## أنماط الاستخدام | Usage Patterns

### 1. قراءة البيانات (Read)

```dart
/// دائماً من المحلي، مع تحديث في الخلفية
class FieldsRepository {
  Stream<List<Field>> watchFields() {
    // الخطوة 1: بث من قاعدة البيانات المحلية
    final localStream = _localDb.watchAllFields();

    // الخطوة 2: محاولة تحديث في الخلفية
    _refreshInBackground();

    return localStream;
  }

  Future<void> _refreshInBackground() async {
    if (!await _connectivity.hasConnection) return;

    try {
      final remote = await _api.getFields();
      await _localDb.upsertFields(remote);
    } catch (_) {
      // فشل صامت - البيانات المحلية كافية
    }
  }
}
```

### 2. كتابة البيانات (Write)

```dart
/// كتابة محلية فورية + طابور للمزامنة
class TasksRepository {
  Future<Task> updateTask(String id, TaskUpdate update) async {
    // الخطوة 1: تحديث محلي
    final task = await _localDb.updateTask(id, update);

    // الخطوة 2: إضافة للطابور
    await _syncQueue.enqueue(
      SyncOperation(
        entityType: 'task',
        entityId: id,
        operation: 'update',
        payload: update.toJson(),
        priority: update.isUrgent ? 1 : 0,
      ),
    );

    // الخطوة 3: محاولة مزامنة فورية
    _trySyncNow();

    return task;
  }
}
```

### 3. حذف البيانات (Delete)

```dart
/// Soft delete محلياً + مزامنة الحذف
class TasksRepository {
  Future<void> deleteTask(String id) async {
    // الخطوة 1: وضع علامة محذوف (لا حذف فعلي)
    await _localDb.markDeleted(id);

    // الخطوة 2: إضافة للطابور
    await _syncQueue.enqueue(
      SyncOperation(
        entityType: 'task',
        entityId: id,
        operation: 'delete',
        payload: '{}',
      ),
    );

    // الخطوة 3: حذف فعلي بعد تأكيد المزامنة
    // يحدث في SyncEngine.confirmDeletion()
  }
}
```

---

## مؤشرات الاتصال | Connectivity Indicators

### UI Components

```dart
/// شريط حالة الاتصال
class ConnectivityBanner extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final status = ref.watch(connectivityProvider);

    return AnimatedContainer(
      duration: Duration(milliseconds: 300),
      height: status.isOffline ? 24 : 0,
      color: Colors.orange,
      child: Center(
        child: Text(
          'وضع عدم الاتصال - التغييرات محفوظة محلياً',
          style: TextStyle(color: Colors.white, fontSize: 12),
        ),
      ),
    );
  }
}

/// أيقونة المزامنة
class SyncStatusIcon extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final pendingCount = ref.watch(pendingSyncCountProvider);

    if (pendingCount == 0) {
      return Icon(Icons.cloud_done, color: Colors.green);
    }

    return Badge(
      label: Text('$pendingCount'),
      child: Icon(Icons.cloud_upload, color: Colors.orange),
    );
  }
}
```

---

## استراتيجية التخزين المؤقت | Caching Strategy

### مستويات التخزين

```
┌─────────────────────────────────────────────────────────────────┐
│                      CACHE LEVELS                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Level 1: Memory Cache (Riverpod State)                         │
│  ├── سريع جداً (< 1ms)                                          │
│  ├── يختفي عند إغلاق التطبيق                                    │
│  └── للبيانات المستخدمة حالياً                                   │
│                                                                  │
│  Level 2: SQLite Database (Drift)                               │
│  ├── سريع (< 10ms)                                              │
│  ├── دائم (يبقى بعد الإغلاق)                                    │
│  └── للبيانات الأساسية والمهمة                                   │
│                                                                  │
│  Level 3: File System (Images/Documents)                        │
│  ├── متوسط السرعة (< 100ms)                                     │
│  ├── للملفات الكبيرة                                             │
│  └── يُنظف دورياً                                                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### سياسات التخزين

```dart
class CachePolicy {
  static const Map<String, Duration> ttl = {
    'weather': Duration(hours: 1),
    'satellite': Duration(hours: 6),
    'alerts': Duration(days: 7),
    'tasks': Duration(days: 30),
    'fields': Duration(days: 365), // شبه دائم
  };

  static const Map<String, int> maxItems = {
    'weather': 100,
    'alerts': 500,
    'tasks': 1000,
    'images': 100,
  };
}
```

---

## معالجة الأخطاء | Error Handling

### سيناريوهات الفشل

```dart
class OfflineErrorHandler {
  Future<T> handleWithFallback<T>({
    required Future<T> Function() operation,
    required T Function() fallback,
    required String operationName,
  }) async {
    try {
      return await operation();
    } on NetworkException {
      // لا إنترنت - استخدم البيانات المحلية
      _logger.info('$operationName: using local fallback');
      return fallback();
    } on TimeoutException {
      // بطء الشبكة - استخدم البيانات المحلية
      _logger.warn('$operationName: timeout, using fallback');
      return fallback();
    } on ServerException catch (e) {
      // خطأ الخادم - حفظ للمحاولة لاحقاً
      _logger.error('$operationName: server error', e);
      await _queueForRetry(operationName);
      return fallback();
    }
  }
}
```

---

## الاختبار | Testing

### اختبار Offline

```dart
void main() {
  group('Offline Functionality', () {
    late MockConnectivity mockConnectivity;
    late TasksRepository repository;

    setUp(() {
      mockConnectivity = MockConnectivity();
      when(mockConnectivity.hasConnection).thenReturn(false);
      repository = TasksRepository(connectivity: mockConnectivity);
    });

    test('creates task locally when offline', () async {
      final task = await repository.createTask(
        TaskInput(title: 'ري الحقل', fieldId: 'field-1'),
      );

      expect(task.id, isNotEmpty);
      expect(task.syncStatus, SyncStatus.pending);

      final queued = await repository.getPendingSyncOperations();
      expect(queued, hasLength(1));
    });

    test('reads from local database when offline', () async {
      // Seed local data
      await repository.seedLocalData([mockTask]);

      final tasks = await repository.getTasks();

      expect(tasks, hasLength(1));
    });
  });
}
```

---

## أفضل الممارسات | Best Practices

### Do's ✅

1. **احفظ محلياً أولاً** - لا تنتظر الشبكة أبداً للعمليات الأساسية
2. **أظهر حالة المزامنة** - المستخدم يجب أن يعرف أن البيانات ستُزامن
3. **تعامل مع التعارضات** - جهّز سياسة واضحة لحل التعارضات
4. **نظّف البيانات القديمة** - لا تترك التطبيق يمتلئ ببيانات منتهية الصلاحية
5. **اختبر Offline** - اختبر كل ميزة في وضع الطيران

### Don'ts ❌

1. **لا تحظر الواجهة** - المستخدم لا ينتظر الشبكة
2. **لا تفقد البيانات** - أي كتابة يجب أن تُحفظ محلياً
3. **لا تتجاهل الأخطاء** - سجّل وأعد المحاولة
4. **لا تعتمد على الاتصال** - افترض دائماً أنه قد ينقطع
5. **لا تخزّن كل شيء** - حدد ما هو ضروري Offline

---

## الموارد | Resources

- [ADR-001: Offline-First Architecture](../adr/ADR-001-offline-first-architecture.md)
- [SYNC_ENGINE.md](./SYNC_ENGINE.md)
- [CONFLICT_RESOLUTION.md](./CONFLICT_RESOLUTION.md)

---

<p align="center">
  <sub>SAHOOL Mobile - Offline-First Strategy</sub>
</p>
