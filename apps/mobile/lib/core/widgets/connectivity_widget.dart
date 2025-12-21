import 'dart:async';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// مزود Connectivity Plus
final connectivityPlusProvider = Provider<Connectivity>((ref) {
  return Connectivity();
});

/// مزود حالة الاتصال
final connectivityProvider = StateNotifierProvider<ConnectivityNotifier, ConnectivityState>((ref) {
  final connectivity = ref.watch(connectivityPlusProvider);
  return ConnectivityNotifier(connectivity);
});

/// حالة الاتصال
enum ConnectionStatus { online, offline, syncing }

class ConnectivityState {
  final ConnectionStatus status;
  final int pendingSyncCount;
  final DateTime? lastSyncTime;
  final String? errorMessage;

  const ConnectivityState({
    this.status = ConnectionStatus.online,
    this.pendingSyncCount = 0,
    this.lastSyncTime,
    this.errorMessage,
  });

  ConnectivityState copyWith({
    ConnectionStatus? status,
    int? pendingSyncCount,
    DateTime? lastSyncTime,
    String? errorMessage,
  }) {
    return ConnectivityState(
      status: status ?? this.status,
      pendingSyncCount: pendingSyncCount ?? this.pendingSyncCount,
      lastSyncTime: lastSyncTime ?? this.lastSyncTime,
      errorMessage: errorMessage ?? this.errorMessage,
    );
  }

  bool get isOnline => status == ConnectionStatus.online;
  bool get isOffline => status == ConnectionStatus.offline;
  bool get isSyncing => status == ConnectionStatus.syncing;
}

/// منطق إدارة الاتصال
class ConnectivityNotifier extends StateNotifier<ConnectivityState> {
  final Connectivity _connectivity;
  StreamSubscription<List<ConnectivityResult>>? _subscription;

  ConnectivityNotifier(this._connectivity) : super(const ConnectivityState()) {
    _initialize();
  }

  Future<void> _initialize() async {
    // Check initial connectivity
    await checkConnectivity();

    // Listen for connectivity changes
    _subscription = _connectivity.onConnectivityChanged.listen(
      (List<ConnectivityResult> results) {
        _updateFromResults(results);
      },
    );
  }

  void _updateFromResults(List<ConnectivityResult> results) {
    final hasConnection = results.isNotEmpty &&
        !results.every((r) => r == ConnectivityResult.none);

    if (hasConnection) {
      if (state.pendingSyncCount > 0) {
        // Auto-sync when back online
        startSync();
      } else {
        setOnline();
      }
    } else {
      setOffline();
    }
  }

  /// فحص حالة الاتصال الحالية
  Future<void> checkConnectivity() async {
    try {
      final results = await _connectivity.checkConnectivity();
      _updateFromResults(results);
    } catch (e) {
      state = state.copyWith(
        status: ConnectionStatus.offline,
        errorMessage: e.toString(),
      );
    }
  }

  /// محاولة إعادة الاتصال
  Future<bool> tryReconnect() async {
    state = state.copyWith(errorMessage: null);
    await checkConnectivity();
    return state.isOnline;
  }

  void setOnline() {
    state = state.copyWith(
      status: ConnectionStatus.online,
      errorMessage: null,
    );
  }

  void setOffline() {
    state = state.copyWith(status: ConnectionStatus.offline);
  }

  void startSync() {
    state = state.copyWith(status: ConnectionStatus.syncing);
  }

  void finishSync({bool success = true}) {
    state = state.copyWith(
      status: ConnectionStatus.online,
      pendingSyncCount: success ? 0 : state.pendingSyncCount,
      lastSyncTime: success ? DateTime.now() : state.lastSyncTime,
      errorMessage: success ? null : 'فشلت المزامنة',
    );
  }

  void addPendingSync([int count = 1]) {
    state = state.copyWith(pendingSyncCount: state.pendingSyncCount + count);
  }

  void setPendingSyncCount(int count) {
    state = state.copyWith(pendingSyncCount: count);
  }

  /// مزامنة يدوية
  Future<void> manualSync() async {
    if (state.isSyncing) return;

    startSync();

    // Simulate sync - replace with actual sync logic
    await Future.delayed(const Duration(seconds: 2));

    finishSync(success: true);
  }

  @override
  void dispose() {
    _subscription?.cancel();
    super.dispose();
  }
}

/// شريط حالة الاتصال
class ConnectivityBanner extends ConsumerWidget {
  const ConnectivityBanner({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final connectivity = ref.watch(connectivityProvider);

    if (connectivity.isOnline && connectivity.pendingSyncCount == 0) {
      return const SizedBox.shrink();
    }

    return AnimatedContainer(
      duration: const Duration(milliseconds: 300),
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      color: _getBackgroundColor(connectivity.status),
      child: SafeArea(
        bottom: false,
        child: Row(
          children: [
            Icon(
              _getIcon(connectivity.status),
              color: Colors.white,
              size: 18,
            ),
            const SizedBox(width: 8),
            Expanded(
              child: Text(
                _getMessage(connectivity),
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 13,
                ),
              ),
            ),
            if (connectivity.isOffline)
              TextButton(
                onPressed: () async {
                  final notifier = ref.read(connectivityProvider.notifier);
                  final success = await notifier.tryReconnect();
                  if (context.mounted && success) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                        content: Text('تم إعادة الاتصال'),
                        backgroundColor: Colors.green,
                      ),
                    );
                  }
                },
                style: TextButton.styleFrom(
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(horizontal: 8),
                ),
                child: const Text('إعادة المحاولة'),
              ),
            if (connectivity.isSyncing)
              const SizedBox(
                width: 16,
                height: 16,
                child: CircularProgressIndicator(
                  strokeWidth: 2,
                  color: Colors.white,
                ),
              ),
          ],
        ),
      ),
    );
  }

  Color _getBackgroundColor(ConnectionStatus status) {
    switch (status) {
      case ConnectionStatus.online:
        return const Color(0xFF367C2B);
      case ConnectionStatus.offline:
        return Colors.red;
      case ConnectionStatus.syncing:
        return Colors.orange;
    }
  }

  IconData _getIcon(ConnectionStatus status) {
    switch (status) {
      case ConnectionStatus.online:
        return Icons.cloud_done;
      case ConnectionStatus.offline:
        return Icons.cloud_off;
      case ConnectionStatus.syncing:
        return Icons.cloud_sync;
    }
  }

  String _getMessage(ConnectivityState state) {
    switch (state.status) {
      case ConnectionStatus.online:
        if (state.pendingSyncCount > 0) {
          return '${state.pendingSyncCount} عناصر في انتظار المزامنة';
        }
        return 'متصل';
      case ConnectionStatus.offline:
        return 'غير متصل - البيانات محفوظة محلياً';
      case ConnectionStatus.syncing:
        return 'جاري المزامنة...';
    }
  }
}

/// أيقونة حالة الاتصال المصغرة
class ConnectivityIndicator extends ConsumerWidget {
  final double size;

  const ConnectivityIndicator({super.key, this.size = 24});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final connectivity = ref.watch(connectivityProvider);

    return Tooltip(
      message: _getTooltip(connectivity),
      child: Container(
        width: size,
        height: size,
        decoration: BoxDecoration(
          color: _getColor(connectivity.status).withOpacity(0.1),
          shape: BoxShape.circle,
        ),
        child: Icon(
          _getIcon(connectivity.status),
          size: size * 0.6,
          color: _getColor(connectivity.status),
        ),
      ),
    );
  }

  Color _getColor(ConnectionStatus status) {
    switch (status) {
      case ConnectionStatus.online:
        return Colors.green;
      case ConnectionStatus.offline:
        return Colors.red;
      case ConnectionStatus.syncing:
        return Colors.orange;
    }
  }

  IconData _getIcon(ConnectionStatus status) {
    switch (status) {
      case ConnectionStatus.online:
        return Icons.cloud_done;
      case ConnectionStatus.offline:
        return Icons.cloud_off;
      case ConnectionStatus.syncing:
        return Icons.sync;
    }
  }

  String _getTooltip(ConnectivityState state) {
    switch (state.status) {
      case ConnectionStatus.online:
        final lastSync = state.lastSyncTime;
        if (lastSync != null) {
          return 'متصل - آخر مزامنة: ${_formatTime(lastSync)}';
        }
        return 'متصل';
      case ConnectionStatus.offline:
        return 'غير متصل';
      case ConnectionStatus.syncing:
        return 'جاري المزامنة...';
    }
  }

  String _formatTime(DateTime time) {
    final now = DateTime.now();
    final diff = now.difference(time);

    if (diff.inMinutes < 1) {
      return 'الآن';
    } else if (diff.inMinutes < 60) {
      return 'منذ ${diff.inMinutes} دقيقة';
    } else if (diff.inHours < 24) {
      return 'منذ ${diff.inHours} ساعة';
    } else {
      return 'منذ ${diff.inDays} يوم';
    }
  }
}

/// بطاقة حالة المزامنة
class SyncStatusCard extends ConsumerWidget {
  const SyncStatusCard({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final connectivity = ref.watch(connectivityProvider);

    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                ConnectivityIndicator(size: 32),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        _getStatusTitle(connectivity.status),
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
                      if (connectivity.lastSyncTime != null)
                        Text(
                          'آخر مزامنة: ${_formatDateTime(connectivity.lastSyncTime!)}',
                          style: TextStyle(
                            fontSize: 12,
                            color: Colors.grey[600],
                          ),
                        ),
                    ],
                  ),
                ),
              ],
            ),
            if (connectivity.pendingSyncCount > 0) ...[
              const Divider(height: 24),
              Row(
                children: [
                  const Icon(Icons.pending, color: Colors.orange, size: 20),
                  const SizedBox(width: 8),
                  Text(
                    '${connectivity.pendingSyncCount} عناصر في انتظار المزامنة',
                    style: const TextStyle(color: Colors.orange),
                  ),
                ],
              ),
            ],
            if (connectivity.errorMessage != null) ...[
              const SizedBox(height: 8),
              Row(
                children: [
                  const Icon(Icons.error_outline, color: Colors.red, size: 20),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      connectivity.errorMessage!,
                      style: const TextStyle(color: Colors.red, fontSize: 12),
                    ),
                  ),
                ],
              ),
            ],
            const Divider(height: 24),
            SizedBox(
              width: double.infinity,
              child: OutlinedButton.icon(
                onPressed: connectivity.isSyncing
                    ? null
                    : () async {
                        final notifier = ref.read(connectivityProvider.notifier);
                        await notifier.manualSync();
                        if (context.mounted) {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(
                              content: Text('تمت المزامنة بنجاح'),
                              backgroundColor: Colors.green,
                            ),
                          );
                        }
                      },
                icon: connectivity.isSyncing
                    ? const SizedBox(
                        width: 16,
                        height: 16,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Icon(Icons.sync),
                label: Text(connectivity.isSyncing ? 'جاري المزامنة...' : 'مزامنة الآن'),
              ),
            ),
          ],
        ),
      ),
    );
  }

  String _getStatusTitle(ConnectionStatus status) {
    switch (status) {
      case ConnectionStatus.online:
        return 'متصل بالإنترنت';
      case ConnectionStatus.offline:
        return 'غير متصل';
      case ConnectionStatus.syncing:
        return 'جاري المزامنة';
    }
  }

  String _formatDateTime(DateTime time) {
    return '${time.day}/${time.month}/${time.year} - ${time.hour}:${time.minute.toString().padLeft(2, '0')}';
  }
}

/// Wrapper للتطبيق مع دعم Offline
class OfflineAwareWidget extends ConsumerWidget {
  final Widget child;
  final Widget? offlineChild;

  const OfflineAwareWidget({
    super.key,
    required this.child,
    this.offlineChild,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final connectivity = ref.watch(connectivityProvider);

    return Column(
      children: [
        const ConnectivityBanner(),
        Expanded(
          child: connectivity.isOffline && offlineChild != null
              ? offlineChild!
              : child,
        ),
      ],
    );
  }
}
