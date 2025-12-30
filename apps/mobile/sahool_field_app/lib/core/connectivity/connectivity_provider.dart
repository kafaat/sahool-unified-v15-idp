// ═══════════════════════════════════════════════════════════════════════════
// SAHOOL - Enhanced Connectivity Provider
// مزود الاتصال المحسن
// ═══════════════════════════════════════════════════════════════════════════

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'connectivity_service.dart';

// ─────────────────────────────────────────────────────────────────────────────
// CONNECTIVITY SERVICE PROVIDER
// ─────────────────────────────────────────────────────────────────────────────

/// Enhanced connectivity service provider
/// مزود خدمة الاتصال المحسنة
final enhancedConnectivityServiceProvider = Provider<ConnectivityService>((ref) {
  final service = ConnectivityService(
    checkInterval: const Duration(seconds: 30),
    pingTimeout: const Duration(seconds: 5),
  );

  // Dispose when provider is disposed
  ref.onDispose(() {
    service.dispose();
  });

  return service;
});

// ─────────────────────────────────────────────────────────────────────────────
// CONNECTIVITY STATUS STREAM PROVIDER
// ─────────────────────────────────────────────────────────────────────────────

/// Stream provider for connectivity status changes
/// مزود البث لتغييرات حالة الاتصال
final connectivityStatusStreamProvider =
    StreamProvider<ConnectivityStatus>((ref) {
  final service = ref.watch(enhancedConnectivityServiceProvider);
  return service.statusStream;
});

/// Current connectivity status provider
/// مزود حالة الاتصال الحالية
final currentConnectivityStatusProvider = Provider<ConnectivityStatus>((ref) {
  final statusAsync = ref.watch(connectivityStatusStreamProvider);
  return statusAsync.when(
    data: (status) => status,
    loading: () => ConnectivityStatus.unknown,
    error: (_, __) => ConnectivityStatus.offline,
  );
});

// ─────────────────────────────────────────────────────────────────────────────
// CONNECTIVITY STATE PROVIDER (Enhanced)
// ─────────────────────────────────────────────────────────────────────────────

/// Enhanced connectivity state with additional metadata
/// حالة الاتصال المحسنة مع بيانات إضافية
final enhancedConnectivityStateProvider =
    StateNotifierProvider<EnhancedConnectivityNotifier, EnhancedConnectivityState>(
  (ref) {
    final service = ref.watch(enhancedConnectivityServiceProvider);
    return EnhancedConnectivityNotifier(service);
  },
);

/// Enhanced connectivity state model
/// نموذج حالة الاتصال المحسنة
class EnhancedConnectivityState {
  final ConnectivityStatus status;
  final DateTime? lastOnlineTime;
  final DateTime? lastCheckTime;
  final int pendingSyncCount;
  final bool autoSyncEnabled;
  final String? errorMessage;

  const EnhancedConnectivityState({
    this.status = ConnectivityStatus.unknown,
    this.lastOnlineTime,
    this.lastCheckTime,
    this.pendingSyncCount = 0,
    this.autoSyncEnabled = true,
    this.errorMessage,
  });

  EnhancedConnectivityState copyWith({
    ConnectivityStatus? status,
    DateTime? lastOnlineTime,
    DateTime? lastCheckTime,
    int? pendingSyncCount,
    bool? autoSyncEnabled,
    String? errorMessage,
  }) {
    return EnhancedConnectivityState(
      status: status ?? this.status,
      lastOnlineTime: lastOnlineTime ?? this.lastOnlineTime,
      lastCheckTime: lastCheckTime ?? this.lastCheckTime,
      pendingSyncCount: pendingSyncCount ?? this.pendingSyncCount,
      autoSyncEnabled: autoSyncEnabled ?? this.autoSyncEnabled,
      errorMessage: errorMessage,
    );
  }

  // Convenience getters
  bool get isOnline => status.hasConnection;
  bool get isOffline => status.hasNoConnection;
  bool get isPoorConnection => status == ConnectivityStatus.poorConnection;
  bool get isReconnecting => status == ConnectivityStatus.reconnecting;
  bool get hasPendingSync => pendingSyncCount > 0;
}

/// Enhanced connectivity state notifier
/// مدير حالة الاتصال المحسنة
class EnhancedConnectivityNotifier
    extends StateNotifier<EnhancedConnectivityState> {
  final ConnectivityService _service;

  EnhancedConnectivityNotifier(this._service)
      : super(const EnhancedConnectivityState()) {
    _initialize();
  }

  void _initialize() {
    // Listen to connectivity status changes
    _service.statusStream.listen((status) {
      _updateStatus(status);
    });
  }

  void _updateStatus(ConnectivityStatus status) {
    state = state.copyWith(
      status: status,
      lastCheckTime: DateTime.now(),
      lastOnlineTime: status.hasConnection ? DateTime.now() : state.lastOnlineTime,
      errorMessage: null,
    );

    // Auto-sync when coming back online
    if (status.hasConnection &&
        state.autoSyncEnabled &&
        state.pendingSyncCount > 0) {
      // Trigger auto-sync (to be implemented by app)
      _autoSync();
    }
  }

  /// Check connectivity now
  Future<void> checkNow() async {
    try {
      final status = await _service.checkNow();
      _updateStatus(status);
    } catch (e) {
      state = state.copyWith(
        errorMessage: e.toString(),
      );
    }
  }

  /// Attempt to reconnect
  Future<bool> reconnect() async {
    try {
      state = state.copyWith(
        status: ConnectivityStatus.reconnecting,
        errorMessage: null,
      );

      final success = await _service.tryReconnect();
      return success;
    } catch (e) {
      state = state.copyWith(
        errorMessage: e.toString(),
        status: ConnectivityStatus.offline,
      );
      return false;
    }
  }

  /// Add pending sync items
  void addPendingSync([int count = 1]) {
    state = state.copyWith(
      pendingSyncCount: state.pendingSyncCount + count,
    );
  }

  /// Set pending sync count
  void setPendingSyncCount(int count) {
    state = state.copyWith(pendingSyncCount: count);
  }

  /// Clear pending sync
  void clearPendingSync() {
    state = state.copyWith(pendingSyncCount: 0);
  }

  /// Enable/disable auto-sync
  void setAutoSync(bool enabled) {
    state = state.copyWith(autoSyncEnabled: enabled);
  }

  /// Auto-sync implementation (to be customized)
  Future<void> _autoSync() async {
    // This is a placeholder - implement actual sync logic
    // in your app by listening to the state provider
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// CONVENIENCE PROVIDERS
// ─────────────────────────────────────────────────────────────────────────────

/// Check if device is online
/// التحقق من الاتصال
final isOnlineProvider = Provider<bool>((ref) {
  final state = ref.watch(enhancedConnectivityStateProvider);
  return state.isOnline;
});

/// Check if device is offline
/// التحقق من عدم الاتصال
final isOfflineProvider = Provider<bool>((ref) {
  final state = ref.watch(enhancedConnectivityStateProvider);
  return state.isOffline;
});

/// Check if connection is poor
/// التحقق من ضعف الاتصال
final isPoorConnectionProvider = Provider<bool>((ref) {
  final state = ref.watch(enhancedConnectivityStateProvider);
  return state.isPoorConnection;
});

/// Get time since last online
/// الحصول على الوقت منذ آخر اتصال
final timeSinceOnlineProvider = Provider<Duration?>((ref) {
  final state = ref.watch(enhancedConnectivityStateProvider);
  if (state.lastOnlineTime == null) return null;
  return DateTime.now().difference(state.lastOnlineTime!);
});
