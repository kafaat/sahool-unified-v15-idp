# Conflict Resolution Strategy
# استراتيجية حل التعارضات

> **المبدأ:** التعارضات حتمية في النظام الموزع، والهدف هو حلها بشكل ذكي مع الحفاظ على بيانات المستخدم

---

## ما هو التعارض؟ | What is a Conflict?

```
┌─────────────────────────────────────────────────────────────────┐
│                      CONFLICT SCENARIO                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  الجهاز A                 الخادم                  الجهاز B       │
│     │                       │                       │           │
│     │                       │                       │           │
│  t1 │──تعديل المهمة────────▶│                       │           │
│     │                       │                       │           │
│     │        [انقطاع اتصال الجهاز B]                 │           │
│     │                       │                       │           │
│  t2 │                       │◀──تعديل نفس المهمة────│           │
│     │                       │                       │           │
│     │                       │        [استعادة الاتصال]           │
│     │                       │                       │           │
│  t3 │                       │◀──محاولة مزامنة───────│           │
│     │                       │                       │           │
│     │                       │        ⚠️ تعارض!                   │
│     │                       │                       │           │
└─────────────────────────────────────────────────────────────────┘
```

---

## أنواع التعارضات | Conflict Types

### 1. تعارض التحديث (Update-Update)

```dart
/// كلا الجهازين عدّلا نفس السجل
class UpdateConflict extends Conflict {
  final Map<String, dynamic> localChanges;
  final Map<String, dynamic> remoteChanges;
  final DateTime localTimestamp;
  final DateTime remoteTimestamp;
}
```

### 2. تعارض الحذف (Delete-Update)

```dart
/// جهاز حذف والآخر عدّل
class DeleteUpdateConflict extends Conflict {
  final bool localDeleted;
  final Map<String, dynamic>? remoteData;
}
```

### 3. تعارض الإنشاء (Create-Create)

```dart
/// نفس المعرف استُخدم في جهازين
class CreateConflict extends Conflict {
  final Map<String, dynamic> localData;
  final Map<String, dynamic> remoteData;
}
```

---

## استراتيجيات الحل | Resolution Strategies

### 1. Last-Write-Wins (الأخير يفوز)

```dart
/// الأبسط: آخر تعديل يفوز
class LastWriteWinsResolver implements ConflictResolver {
  @override
  ResolvedData resolve(Conflict conflict) {
    if (conflict.localTimestamp.isAfter(conflict.remoteTimestamp)) {
      return ResolvedData.useLocal();
    }
    return ResolvedData.useRemote();
  }
}
```

**متى نستخدمه:**
- بيانات غير حساسة
- إعدادات المستخدم
- حالات بسيطة

### 2. Merge (الدمج الذكي)

```dart
/// دمج التغييرات من الطرفين
class MergeResolver implements ConflictResolver {
  @override
  ResolvedData resolve(Conflict conflict) {
    final merged = <String, dynamic>{};
    final fields = {...conflict.localChanges.keys, ...conflict.remoteChanges.keys};

    for (final field in fields) {
      merged[field] = _resolveField(
        field,
        conflict.localChanges[field],
        conflict.remoteChanges[field],
        conflict.baseVersion[field],
      );
    }

    return ResolvedData.merged(merged);
  }

  dynamic _resolveField(
    String field,
    dynamic local,
    dynamic remote,
    dynamic base,
  ) {
    // إذا أحدهما لم يتغير، استخدم الآخر
    if (local == base) return remote;
    if (remote == base) return local;

    // كلاهما تغير - قاعدة خاصة بالحقل
    return _fieldSpecificMerge(field, local, remote);
  }
}
```

**متى نستخدمه:**
- المهام (يمكن دمج الملاحظات)
- القوائم (إضافة عناصر من الطرفين)
- البيانات المركبة

### 3. User Decision (قرار المستخدم)

```dart
/// المستخدم يختار
class UserDecisionResolver implements ConflictResolver {
  final ConflictUI _ui;

  @override
  Future<ResolvedData> resolve(Conflict conflict) async {
    // عرض واجهة المقارنة
    final choice = await _ui.showConflictDialog(
      local: conflict.localData,
      remote: conflict.remoteData,
      differences: conflict.calculateDifferences(),
    );

    return switch (choice) {
      ConflictChoice.keepLocal => ResolvedData.useLocal(),
      ConflictChoice.keepRemote => ResolvedData.useRemote(),
      ConflictChoice.merge => ResolvedData.merged(choice.mergedData),
      ConflictChoice.keepBoth => ResolvedData.duplicate(),
    };
  }
}
```

**متى نستخدمه:**
- بيانات حساسة
- تعارضات معقدة
- عندما لا يمكن الدمج تلقائياً

---

## قواعد الحل حسب الكيان | Entity-Specific Rules

### المهام (Tasks)

```dart
class TaskConflictResolver extends EntityConflictResolver<Task> {
  @override
  Resolution resolve(Task local, Task remote) {
    // القاعدة 1: المهمة المكتملة تفوز
    if (local.isCompleted && !remote.isCompleted) {
      return Resolution.useLocal(reason: 'Task completed locally');
    }
    if (remote.isCompleted && !local.isCompleted) {
      return Resolution.useRemote(reason: 'Task completed remotely');
    }

    // القاعدة 2: دمج الملاحظات
    if (local.notes != remote.notes) {
      final mergedNotes = _mergeNotes(local.notes, remote.notes);
      return Resolution.merge(
        local.copyWith(notes: mergedNotes),
      );
    }

    // القاعدة 3: الأحدث يفوز
    return local.updatedAt.isAfter(remote.updatedAt)
        ? Resolution.useLocal()
        : Resolution.useRemote();
  }

  String _mergeNotes(String? local, String? remote) {
    if (local == null) return remote ?? '';
    if (remote == null) return local;

    return '''
[ملاحظات محلية - ${DateTime.now()}]
$local

[ملاحظات من الخادم]
$remote
''';
  }
}
```

### الحقول (Fields)

```dart
class FieldConflictResolver extends EntityConflictResolver<Field> {
  @override
  Resolution resolve(Field local, Field remote) {
    // الحقول حساسة - دائماً اسأل المستخدم
    if (_hasSignificantChanges(local, remote)) {
      return Resolution.askUser(
        summary: 'تغييرات في بيانات الحقل "${local.name}"',
        localChanges: _describeChanges(local),
        remoteChanges: _describeChanges(remote),
      );
    }

    // تغييرات طفيفة - دمج تلقائي
    return Resolution.merge(_mergeFields(local, remote));
  }

  bool _hasSignificantChanges(Field local, Field remote) {
    return local.area != remote.area ||
           local.cropType != remote.cropType ||
           local.location != remote.location;
  }
}
```

### التنبيهات (Alerts)

```dart
class AlertConflictResolver extends EntityConflictResolver<Alert> {
  @override
  Resolution resolve(Alert local, Alert remote) {
    // القاعدة: المقروء يفوز على غير المقروء
    if (local.isRead && !remote.isRead) {
      return Resolution.useLocal();
    }
    if (remote.isRead && !local.isRead) {
      return Resolution.useRemote();
    }

    // القاعدة: المؤجل يفوز
    if (local.snoozedUntil != null && remote.snoozedUntil == null) {
      return Resolution.useLocal();
    }

    return Resolution.useRemote(); // الخادم هو المرجع للتنبيهات
  }
}
```

---

## واجهة حل التعارضات | Conflict Resolution UI

### شاشة التعارضات

```dart
class ConflictResolutionScreen extends ConsumerWidget {
  final Conflict conflict;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(
        title: Text('حل تعارض'),
        backgroundColor: Colors.orange,
      ),
      body: Column(
        children: [
          // شرح التعارض
          ConflictExplanationCard(conflict: conflict),

          // مقارنة جنباً إلى جنب
          Expanded(
            child: Row(
              children: [
                // النسخة المحلية
                Expanded(
                  child: VersionCard(
                    title: 'نسختك',
                    data: conflict.localData,
                    timestamp: conflict.localTimestamp,
                    color: Colors.blue,
                  ),
                ),

                // النسخة البعيدة
                Expanded(
                  child: VersionCard(
                    title: 'نسخة الخادم',
                    data: conflict.remoteData,
                    timestamp: conflict.remoteTimestamp,
                    color: Colors.green,
                  ),
                ),
              ],
            ),
          ),

          // أزرار الإجراءات
          ConflictActionButtons(
            onKeepLocal: () => _resolve(Resolution.useLocal()),
            onKeepRemote: () => _resolve(Resolution.useRemote()),
            onMerge: () => _showMergeDialog(),
          ),
        ],
      ),
    );
  }
}
```

### بطاقة التعارض

```dart
class ConflictCard extends StatelessWidget {
  final Conflict conflict;
  final VoidCallback onResolve;

  @override
  Widget build(BuildContext context) {
    return Card(
      color: Colors.orange.shade50,
      child: ListTile(
        leading: Icon(Icons.warning, color: Colors.orange),
        title: Text(conflict.entityName),
        subtitle: Text(
          'تعارض منذ ${timeAgo(conflict.detectedAt)}',
        ),
        trailing: TextButton(
          onPressed: onResolve,
          child: Text('حل'),
        ),
      ),
    );
  }
}
```

---

## منع التعارضات | Conflict Prevention

### 1. Optimistic Locking

```dart
/// استخدام version للتحقق
class VersionedEntity {
  final String id;
  final int version;  // يزيد مع كل تعديل

  Future<void> update(Map<String, dynamic> changes) async {
    final response = await api.patch(
      '/entities/$id',
      body: {...changes, 'expectedVersion': version},
    );

    if (response.statusCode == 409) {
      throw ConflictException('Version mismatch');
    }
  }
}
```

### 2. Field-Level Sync

```dart
/// مزامنة على مستوى الحقل لا السجل
class FieldLevelSync {
  Future<void> syncField(String entityId, String field, dynamic value) async {
    await api.patch(
      '/entities/$entityId/fields/$field',
      body: {'value': value, 'timestamp': DateTime.now().toIso8601String()},
    );
  }
}
```

### 3. Offline Lock

```dart
/// قفل السجل عند التعديل Offline
class OfflineLock {
  Future<void> lockForEditing(String entityId) async {
    await _localDb.setLock(entityId, userId, expiresAt: DateTime.now().add(Duration(hours: 1)));

    // عند الاتصال، نبلغ الخادم
    if (await _connectivity.hasConnection) {
      await api.post('/entities/$entityId/lock');
    }
  }
}
```

---

## مقاييس التعارضات | Conflict Metrics

```dart
class ConflictMetrics {
  /// عدد التعارضات الإجمالي
  int totalConflicts;

  /// التعارضات المحلولة تلقائياً
  int autoResolved;

  /// التعارضات التي احتاجت تدخل المستخدم
  int userResolved;

  /// التعارضات المعلقة
  int pending;

  /// أكثر الكيانات تعارضاً
  Map<String, int> conflictsByEntity;

  double get autoResolveRate =>
      autoResolved / totalConflicts * 100;
}
```

---

## أفضل الممارسات | Best Practices

### Do's ✅

1. **سجّل كل تعارض** - للتحليل والتحسين
2. **أظهر للمستخدم** - لا تخفِ التعارضات
3. **احفظ النسختين** - قبل الحل
4. **وفّر خيار التراجع** - بعد الحل
5. **استخدم timestamps دقيقة** - للمقارنة الصحيحة

### Don'ts ❌

1. **لا تفقد بيانات** - أي نسخة قد تكون مهمة
2. **لا تحل صامتاً** - المستخدم يجب أن يعرف
3. **لا تؤجل للأبد** - التعارضات تتراكم
4. **لا تتجاهل السياق** - قواعد مختلفة لكيانات مختلفة

---

## الموارد | Resources

- [SYNC_ENGINE.md](./SYNC_ENGINE.md)
- [OFFLINE_FIRST.md](./OFFLINE_FIRST.md)

---

<p align="center">
  <sub>SAHOOL Mobile - Conflict Resolution</sub>
</p>
