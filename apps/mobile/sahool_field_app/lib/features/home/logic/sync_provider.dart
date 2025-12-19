import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../main.dart';

/// حالة المزامنة للواجهة
enum SyncStatus {
  synced,   // كل شيء متزامن
  syncing,  // جاري المزامنة
  offline,  // غير متصل
}

/// مزود حالة المزامنة للواجهة
final syncStatusUiProvider = StateProvider<SyncStatus>((ref) {
  // الاستماع للـ SyncEngine وتحديد الحالة
  final syncEngine = ref.watch(syncEngineProvider);

  // هذا placeholder - في التطبيق الحقيقي نستمع لـ stream من SyncEngine
  return SyncStatus.synced;
});

/// مزود عدد العمليات المعلقة
final pendingOperationsProvider = FutureProvider<int>((ref) async {
  final db = ref.watch(databaseProvider);

  // حساب عدد السجلات في الـ Outbox
  try {
    final outbox = await db.customSelect(
      'SELECT COUNT(*) as count FROM outbox WHERE synced = 0',
    ).getSingle();
    return outbox.read<int>('count');
  } catch (e) {
    return 0;
  }
});

/// مزود حالة الاتصال
final isOnlineProvider = StateProvider<bool>((ref) {
  // في التطبيق الحقيقي، نستخدم connectivity_plus
  return true;
});

/// Extension للحصول على معلومات الحالة
extension SyncStatusExtension on SyncStatus {
  String get label {
    switch (this) {
      case SyncStatus.synced:
        return 'متزامن';
      case SyncStatus.syncing:
        return 'جاري المزامنة...';
      case SyncStatus.offline:
        return 'غير متصل';
    }
  }

  String get labelEn {
    switch (this) {
      case SyncStatus.synced:
        return 'Synced';
      case SyncStatus.syncing:
        return 'Syncing...';
      case SyncStatus.offline:
        return 'Offline';
    }
  }
}
