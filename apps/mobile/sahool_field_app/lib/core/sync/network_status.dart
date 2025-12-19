import 'dart:async';
import 'package:connectivity_plus/connectivity_plus.dart';

/// Network Status Monitor
/// مراقب حالة الشبكة
class NetworkStatus {
  final Connectivity _connectivity = Connectivity();
  StreamSubscription<ConnectivityResult>? _subscription;

  bool _isOnline = false;
  final _onlineController = StreamController<bool>.broadcast();

  Stream<bool> get onlineStream => _onlineController.stream;
  bool get isOnline => _isOnline;

  NetworkStatus() {
    _init();
  }

  void _init() {
    // Check initial status
    _connectivity.checkConnectivity().then(_updateStatus);

    // Listen for changes
    _subscription = _connectivity.onConnectivityChanged.listen(_updateStatus);
  }

  void _updateStatus(ConnectivityResult result) {
    final wasOnline = _isOnline;

    // Check if result indicates connectivity
    _isOnline = result != ConnectivityResult.none;

    if (wasOnline != _isOnline) {
      _onlineController.add(_isOnline);
    }
  }

  Future<bool> checkOnline() async {
    final result = await _connectivity.checkConnectivity();
    _updateStatus(result);
    return _isOnline;
  }

  void dispose() {
    _subscription?.cancel();
    _onlineController.close();
  }
}
