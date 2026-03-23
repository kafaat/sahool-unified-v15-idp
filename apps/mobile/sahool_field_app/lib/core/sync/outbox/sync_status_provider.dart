import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../storage/database.dart';
import '../network_status.dart';
import 'outbox_processor.dart';
import 'outbox_service.dart';

/// SAHOOL Sync Status Providers
/// مزودات حالة المزامنة
///
/// Riverpod providers for reactive sync status updates.
/// Provides:
/// - Overall sync status
/// - Pending operation count
/// - Network connectivity status
/// - Processor state
/// - Outbox statistics

// ═══════════════════════════════════════════════════════════════════════════
// Core Providers - المزودات الأساسية
// ═══════════════════════════════════════════════════════════════════════════

/// Database provider (should be provided by main.dart)
final databaseInstanceProvider = Provider<AppDatabase>((ref) {
  throw UnimplementedError('Database provider must be overridden');
});

/// Network status provider
final networkStatusProvider = Provider<NetworkStatus>((ref) {
  final networkStatus = NetworkStatus();
  ref.onDispose(() => networkStatus.dispose());
  return networkStatus;
});

/// Outbox service provider
final outboxServiceProvider = Provider<OutboxService>((ref) {
  final db = ref.watch(databaseInstanceProvider);
  final service = OutboxService(database: db);
  ref.onDispose(() => service.dispose());
  return service;
});

/// Outbox processor provider
final outboxProcessorProvider = Provider<OutboxProcessor>((ref) {
  final db = ref.watch(databaseInstanceProvider);
  final outboxService = ref.watch(outboxServiceProvider);
  final networkStatus = ref.watch(networkStatusProvider);

  final processor = OutboxProcessor(
    database: db,
    outboxService: outboxService,
    networkStatus: networkStatus,
  );

  // Start processor automatically
  processor.start();

  ref.onDispose(() => processor.dispose());
  return processor;
});

// ═══════════════════════════════════════════════════════════════════════════
// Status Streams - تيارات الحالة
// ═══════════════════════════════════════════════════════════════════════════

/// Stream of network connectivity status
final isOnlineStreamProvider = StreamProvider<bool>((ref) {
  final networkStatus = ref.watch(networkStatusProvider);
  return networkStatus.onlineStream;
});

/// Current online status (synchronous)
final isOnlineProvider = StateProvider<bool>((ref) {
  // Subscribe to stream updates
  ref.listen<AsyncValue<bool>>(isOnlineStreamProvider, (prev, next) {
    next.whenData((isOnline) {
      ref.controller.state = isOnline;
    });
  });

  // Initial value
  return true;
});

/// Stream of processor state
final processorStateStreamProvider = StreamProvider<ProcessorState>((ref) {
  final processor = ref.watch(outboxProcessorProvider);
  return processor.stateStream;
});

/// Current processor state (synchronous)
final processorStateProvider = StateProvider<ProcessorState>((ref) {
  ref.listen<AsyncValue<ProcessorState>>(processorStateStreamProvider,
      (prev, next) {
    next.whenData((state) {
      ref.controller.state = state;
    });
  });
  return ProcessorState.idle;
});

/// Stream of outbox statistics
final outboxStatsStreamProvider = StreamProvider<OutboxStats>((ref) {
  final outboxService = ref.watch(outboxServiceProvider);
  return outboxService.statsStream;
});

/// Current outbox statistics
final outboxStatsProvider = FutureProvider<OutboxStats>((ref) async {
  final outboxService = ref.watch(outboxServiceProvider);
  return outboxService.getStats();
});

/// Stream of processing progress
final processingProgressStreamProvider =
    StreamProvider<ProcessingProgress>((ref) {
  final processor = ref.watch(outboxProcessorProvider);
  return processor.progressStream;
});

// ═══════════════════════════════════════════════════════════════════════════
// Computed Status - الحالة المحسوبة
// ═══════════════════════════════════════════════════════════════════════════

/// Overall sync status for UI display
final syncStatusProvider = Provider<SyncStatusInfo>((ref) {
  final isOnline = ref.watch(isOnlineProvider);
  final processorState = ref.watch(processorStateProvider);
  final stats = ref.watch(outboxStatsProvider);

  return stats.when(
    data: (outboxStats) {
      // Offline
      if (!isOnline) {
        return SyncStatusInfo(
          status: SyncStatus.offline,
          pendingCount: outboxStats.pendingCount,
          failedCount: outboxStats.failedCount,
          message: 'غير متصل',
          messageEn: 'Offline',
        );
      }

      // Syncing
      if (processorState == ProcessorState.processing) {
        return SyncStatusInfo(
          status: SyncStatus.syncing,
          pendingCount: outboxStats.pendingCount,
          failedCount: outboxStats.failedCount,
          message: 'جاري المزامنة...',
          messageEn: 'Syncing...',
        );
      }

      // Has failures
      if (outboxStats.failedCount > 0) {
        return SyncStatusInfo(
          status: SyncStatus.error,
          pendingCount: outboxStats.pendingCount,
          failedCount: outboxStats.failedCount,
          message: 'يوجد ${outboxStats.failedCount} عملية فاشلة',
          messageEn: '${outboxStats.failedCount} failed operations',
        );
      }

      // Has pending
      if (outboxStats.pendingCount > 0) {
        return SyncStatusInfo(
          status: SyncStatus.pending,
          pendingCount: outboxStats.pendingCount,
          failedCount: 0,
          message: '${outboxStats.pendingCount} عملية قيد الانتظار',
          messageEn: '${outboxStats.pendingCount} pending',
        );
      }

      // All synced
      return const SyncStatusInfo(
        status: SyncStatus.synced,
        pendingCount: 0,
        failedCount: 0,
        message: 'متزامن',
        messageEn: 'Synced',
      );
    },
    loading: () => const SyncStatusInfo(
      status: SyncStatus.syncing,
      pendingCount: 0,
      failedCount: 0,
      message: 'جاري التحميل...',
      messageEn: 'Loading...',
    ),
    error: (_, __) => const SyncStatusInfo(
      status: SyncStatus.error,
      pendingCount: 0,
      failedCount: 0,
      message: 'خطأ',
      messageEn: 'Error',
    ),
  );
});

/// Pending operations count (for badges)
final pendingCountProvider = Provider<int>((ref) {
  final stats = ref.watch(outboxStatsProvider);
  return stats.maybeWhen(
    data: (s) => s.pendingCount,
    orElse: () => 0,
  );
});

/// Failed operations count (for alerts)
final failedCountProvider = Provider<int>((ref) {
  final stats = ref.watch(outboxStatsProvider);
  return stats.maybeWhen(
    data: (s) => s.failedCount,
    orElse: () => 0,
  );
});

/// Has pending changes (for UI indicators)
final hasPendingChangesProvider = Provider<bool>((ref) {
  final count = ref.watch(pendingCountProvider);
  return count > 0;
});

/// Needs attention (failures or conflicts)
final needsAttentionProvider = Provider<bool>((ref) {
  final stats = ref.watch(outboxStatsProvider);
  return stats.maybeWhen(
    data: (s) => s.failedCount > 0,
    orElse: () => false,
  );
});

// ═══════════════════════════════════════════════════════════════════════════
// Actions - الإجراءات
// ═══════════════════════════════════════════════════════════════════════════

/// Force sync action
final forceSyncProvider =
    FutureProvider.family<ProcessingResult, void>((ref, _) async {
  final processor = ref.read(outboxProcessorProvider);
  return processor.processNow();
});

/// Retry failed operations
final retryFailedProvider = FutureProvider.family<void, void>((ref, _) async {
  final outboxService = ref.read(outboxServiceProvider);
  await outboxService.resetFailedEntries();
});

// ═══════════════════════════════════════════════════════════════════════════
// Status Models - نماذج الحالة
// ═══════════════════════════════════════════════════════════════════════════

/// Overall sync status enum
enum SyncStatus {
  synced,
  syncing,
  pending,
  error,
  offline,
}

/// Extension for sync status
extension SyncStatusExtension on SyncStatus {
  String get labelAr {
    switch (this) {
      case SyncStatus.synced:
        return 'متزامن';
      case SyncStatus.syncing:
        return 'جاري المزامنة';
      case SyncStatus.pending:
        return 'قيد الانتظار';
      case SyncStatus.error:
        return 'خطأ';
      case SyncStatus.offline:
        return 'غير متصل';
    }
  }

  String get labelEn {
    switch (this) {
      case SyncStatus.synced:
        return 'Synced';
      case SyncStatus.syncing:
        return 'Syncing';
      case SyncStatus.pending:
        return 'Pending';
      case SyncStatus.error:
        return 'Error';
      case SyncStatus.offline:
        return 'Offline';
    }
  }

  bool get isHealthy => this == SyncStatus.synced;
  bool get isActive => this == SyncStatus.syncing;
  bool get needsAttention => this == SyncStatus.error;
}

/// Sync status info for UI
class SyncStatusInfo {
  final SyncStatus status;
  final int pendingCount;
  final int failedCount;
  final String message;
  final String messageEn;

  const SyncStatusInfo({
    required this.status,
    required this.pendingCount,
    required this.failedCount,
    required this.message,
    required this.messageEn,
  });

  bool get isHealthy => status.isHealthy;
  bool get isActive => status.isActive;
  bool get needsAttention => status.needsAttention;
  int get totalPending => pendingCount + failedCount;
}
