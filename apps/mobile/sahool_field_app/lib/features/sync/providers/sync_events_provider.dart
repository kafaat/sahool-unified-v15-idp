import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/storage/database.dart';
import '../../../core/sync/sync_engine.dart';
import '../../../core/sync/queue_manager.dart';
import '../../../core/config/config.dart';
import '../../../main.dart';

/// Sync Events State
class SyncEventsState {
  final List<SyncEvent> events;
  final int unreadCount;
  final bool isLoading;
  final String? error;

  const SyncEventsState({
    this.events = const [],
    this.unreadCount = 0,
    this.isLoading = false,
    this.error,
  });

  SyncEventsState copyWith({
    List<SyncEvent>? events,
    int? unreadCount,
    bool? isLoading,
    String? error,
  }) {
    return SyncEventsState(
      events: events ?? this.events,
      unreadCount: unreadCount ?? this.unreadCount,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }

  bool get hasUnread => unreadCount > 0;
  bool get hasConflicts => events.any((e) => e.type == 'CONFLICT' && !e.isRead);
}

/// Sync Events Notifier
class SyncEventsNotifier extends StateNotifier<SyncEventsState> {
  final AppDatabase _database;
  final String _tenantId;
  StreamSubscription? _subscription;

  SyncEventsNotifier({
    required AppDatabase database,
    String? tenantId,
  })  : _database = database,
        _tenantId = tenantId ?? AppConfig.defaultTenantId,
        super(const SyncEventsState(isLoading: true)) {
    _init();
  }

  void _init() {
    _loadEvents();
    _watchUnreadCount();
  }

  Future<void> _loadEvents() async {
    try {
      state = state.copyWith(isLoading: true, error: null);
      final events = await _database.getUnreadSyncEvents(_tenantId);
      state = state.copyWith(
        events: events,
        unreadCount: events.length,
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: 'فشل في تحميل أحداث المزامنة',
      );
    }
  }

  void _watchUnreadCount() {
    _subscription = _database.watchUnreadEventsCount(_tenantId).listen((count) {
      state = state.copyWith(unreadCount: count);
      if (count > state.events.length) {
        _loadEvents();
      }
    });
  }

  /// Refresh events
  Future<void> refresh() => _loadEvents();

  /// Mark event as read
  Future<void> markAsRead(int eventId) async {
    await _database.markSyncEventRead(eventId);
    await _loadEvents();
  }

  /// Mark all events as read
  Future<void> markAllAsRead() async {
    await _database.markAllSyncEventsRead(_tenantId);
    await _loadEvents();
  }

  /// Get conflicts only
  List<SyncEvent> get conflicts =>
      state.events.where((e) => e.type == 'CONFLICT').toList();

  @override
  void dispose() {
    _subscription?.cancel();
    super.dispose();
  }
}

/// Sync Events Provider
final syncEventsProvider =
    StateNotifierProvider<SyncEventsNotifier, SyncEventsState>((ref) {
  final database = ref.watch(databaseProvider);
  return SyncEventsNotifier(database: database);
});

/// Unread conflicts count provider
final unreadConflictsCountProvider = Provider<int>((ref) {
  final state = ref.watch(syncEventsProvider);
  return state.events.where((e) => e.type == 'CONFLICT' && !e.isRead).length;
});

/// Has unread conflicts provider
final hasUnreadConflictsProvider = Provider<bool>((ref) {
  return ref.watch(unreadConflictsCountProvider) > 0;
});

// ============================================================
// Sync Status Provider
// ============================================================

/// Comprehensive Sync Status
class SyncStatusState {
  final SyncStatus engineStatus;
  final QueueStats? queueStats;
  final bool isOnline;
  final DateTime? lastSyncTime;
  final String? lastError;

  const SyncStatusState({
    this.engineStatus = SyncStatus.idle,
    this.queueStats,
    this.isOnline = false,
    this.lastSyncTime,
    this.lastError,
  });

  SyncStatusState copyWith({
    SyncStatus? engineStatus,
    QueueStats? queueStats,
    bool? isOnline,
    DateTime? lastSyncTime,
    String? lastError,
  }) {
    return SyncStatusState(
      engineStatus: engineStatus ?? this.engineStatus,
      queueStats: queueStats ?? this.queueStats,
      isOnline: isOnline ?? this.isOnline,
      lastSyncTime: lastSyncTime ?? this.lastSyncTime,
      lastError: lastError,
    );
  }

  bool get isSyncing => engineStatus == SyncStatus.syncing;
  bool get hasError => engineStatus == SyncStatus.error || lastError != null;
  bool get isFullySynced =>
      isOnline && (queueStats?.isEmpty ?? true) && !hasError;

  int get pendingCount => queueStats?.totalPending ?? 0;
  int get failedCount => queueStats?.totalFailed ?? 0;
  int get conflictsCount => queueStats?.totalConflicts ?? 0;
}

/// Sync Status Notifier
class SyncStatusNotifier extends StateNotifier<SyncStatusState> {
  final SyncEngine _syncEngine;
  final QueueManager _queueManager;
  StreamSubscription? _statusSubscription;
  StreamSubscription? _queueSubscription;

  SyncStatusNotifier({
    required SyncEngine syncEngine,
    required QueueManager queueManager,
  })  : _syncEngine = syncEngine,
        _queueManager = queueManager,
        super(const SyncStatusState()) {
    _init();
  }

  void _init() {
    // Listen to sync engine status
    _statusSubscription = _syncEngine.syncStatus.listen((status) {
      state = state.copyWith(
        engineStatus: status,
        lastSyncTime: status == SyncStatus.idle ? DateTime.now() : null,
      );
    });

    // Listen to queue stats
    _queueSubscription = _queueManager.statsStream.listen((stats) {
      state = state.copyWith(queueStats: stats);
    });
  }

  /// Trigger manual sync
  Future<SyncResult> syncNow() async {
    final result = await _syncEngine.runOnce();
    if (!result.success) {
      state = state.copyWith(lastError: result.message);
    }
    return result;
  }

  /// Force refresh from server
  Future<void> forceRefresh() async {
    try {
      await _syncEngine.forceRefresh();
      state = state.copyWith(lastError: null);
    } catch (e) {
      state = state.copyWith(lastError: e.toString());
    }
  }

  /// Update online status
  void setOnlineStatus(bool isOnline) {
    state = state.copyWith(isOnline: isOnline);
  }

  @override
  void dispose() {
    _statusSubscription?.cancel();
    _queueSubscription?.cancel();
    super.dispose();
  }
}

/// Queue Manager Provider
final queueManagerProvider = Provider<QueueManager>((ref) {
  final database = ref.watch(databaseProvider);
  return QueueManager(database: database);
});

/// Sync Status Provider
final syncStatusProvider =
    StateNotifierProvider<SyncStatusNotifier, SyncStatusState>((ref) {
  final syncEngine = ref.watch(syncEngineProvider);
  final queueManager = ref.watch(queueManagerProvider);
  return SyncStatusNotifier(
    syncEngine: syncEngine,
    queueManager: queueManager,
  );
});

/// Is syncing provider (simple boolean)
final isSyncingProvider = Provider<bool>((ref) {
  return ref.watch(syncStatusProvider).isSyncing;
});

/// Pending items count provider
final pendingItemsCountProvider = Provider<int>((ref) {
  return ref.watch(syncStatusProvider).pendingCount;
});

/// Sync health status provider
final syncHealthProvider = Provider<QueueHealthStatus>((ref) {
  final queueManager = ref.watch(queueManagerProvider);
  return queueManager.getHealthStatus();
});
