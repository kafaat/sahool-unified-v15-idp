import 'dart:async';
import 'package:connectivity_plus/connectivity_plus.dart';

/// Network Status Monitor
/// مراقب حالة الشبكة
class NetworkStatus {
  final Connectivity _connectivity = Connectivity();
  StreamSubscription<List<ConnectivityResult>>? _subscription;

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

  void _updateStatus(List<ConnectivityResult> results) {
    final wasOnline = _isOnline;

    // Check if any result indicates connectivity
    _isOnline = results.isNotEmpty &&
        results.any((result) => result != ConnectivityResult.none);

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
