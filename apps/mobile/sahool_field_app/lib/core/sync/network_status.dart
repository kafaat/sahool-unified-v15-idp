import 'dart:async';
import 'package:connectivity_plus/connectivity_plus.dart';

/// Network Status Monitor
/// مراقب حالة الشبكة
class NetworkStatus {
  // Singleton instance
  static final NetworkStatus instance = NetworkStatus._internal();

  final Connectivity _connectivity = Connectivity();
  StreamSubscription<List<ConnectivityResult>>? _subscription;

  bool _isOnline = false;
  final _onlineController = StreamController<bool>.broadcast();

  Stream<bool> get onlineStream => _onlineController.stream;
  bool get isOnline => _isOnline;

  /// Alias for isOnline (used by OfflineSyncEngine)
  Future<bool> get isConnected async {
    await checkOnline();
    return _isOnline;
  }

  /// Private constructor for singleton
  NetworkStatus._internal() {
    _init();
  }

  /// Public constructor that returns singleton or creates new instance
  /// (allows DI while maintaining singleton behavior)
  factory NetworkStatus() {
    return instance;
  }

  void _init() {
    // Check initial status
    _connectivity.checkConnectivity().then(_updateStatus);

    // Listen for changes
    _subscription = _connectivity.onConnectivityChanged.listen(_updateStatus);
  }

  void _updateStatus(List<ConnectivityResult> results) {
    final wasOnline = _isOnline;

    // Check if any result indicates connectivity (not none)
    _isOnline = results.isNotEmpty &&
        !results.every((r) => r == ConnectivityResult.none);

    if (wasOnline != _isOnline) {
      _onlineController.add(_isOnline);
    }
  }

  Future<bool> checkOnline() async {
    final results = await _connectivity.checkConnectivity();
    _updateStatus(results);
    return _isOnline;
  }

  void dispose() {
    _subscription?.cancel();
    _onlineController.close();
  }
}
