/// SAHOOL Sync Engine
/// محرك المزامنة للعمل بدون اتصال

import 'dart:async';
import 'offline_queue.dart';
import 'conflict_policy.dart';
import 'models.dart';

typedef ApiCallFunction = Future<bool> Function(OfflineCommand command);

class SyncEngine {
  final OfflineQueue queue;
  final ConflictPolicy policy;
  final ApiCallFunction apiCall;

  bool _isSyncing = false;
  Timer? _autoSyncTimer;

  SyncEngine({
    required this.queue,
    required this.policy,
    required this.apiCall,
  });

  bool get isSyncing => _isSyncing;
  int get pendingCount => queue.length;

  void startAutoSync({Duration interval = const Duration(minutes: 5)}) {
    _autoSyncTimer?.cancel();
    _autoSyncTimer = Timer.periodic(interval, (_) => syncOnce());
  }

  void stopAutoSync() {
    _autoSyncTimer?.cancel();
    _autoSyncTimer = null;
  }

  Future<SyncResult> syncOnce() async {
    if (_isSyncing) {
      return SyncResult(synced: 0, failed: 0, remaining: queue.length);
    }

    _isSyncing = true;
    int synced = 0;
    int failed = 0;

    try {
      for (final command in List.from(queue.pending)) {
        try {
          final success = await apiCall(command);

          if (success) {
            queue.remove(command.id);
            synced++;
          } else {
            queue.incrementRetry(command.id);
            failed++;
          }
        } catch (e) {
          queue.incrementRetry(command.id);
          failed++;
          break; // توقف عند خطأ الشبكة للحفاظ على الترتيب
        }
      }
    } finally {
      _isSyncing = false;
    }

    return SyncResult(synced: synced, failed: failed, remaining: queue.length);
  }

  /// إضافة أمر للقائمة
  void addCommand(OfflineCommand command) {
    queue.enqueue(command);
  }

  /// إنشاء أمر جديد
  OfflineCommand createCommand({
    required String type,
    required Map<String, dynamic> payload,
  }) {
    final command = OfflineCommand(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      type: type,
      payload: payload,
      createdAt: DateTime.now(),
    );
    queue.enqueue(command);
    return command;
  }

  void dispose() {
    stopAutoSync();
  }
}
