import 'dart:async';
import 'package:mocktail/mocktail.dart';
import 'package:sahool_field_app/core/sync/network_status.dart';

/// Mock NetworkStatus for testing
/// حالة الشبكة الوهمية للاختبارات
class MockNetworkStatus extends Mock implements NetworkStatus {
  bool _isOnline = true;
  final _onlineController = StreamController<bool>.broadcast();

  MockNetworkStatus({bool isOnline = true}) {
    _isOnline = isOnline;
  }

  /// Set online/offline status
  void setOnlineStatus(bool online) {
    if (_isOnline != online) {
      _isOnline = online;
      _onlineController.add(_isOnline);
    }
  }

  /// Simulate network going offline
  void goOffline() {
    setOnlineStatus(false);
  }

  /// Simulate network coming back online
  void goOnline() {
    setOnlineStatus(true);
  }

  @override
  bool get isOnline => _isOnline;

  @override
  Stream<bool> get onlineStream => _onlineController.stream;

  @override
  Future<bool> checkOnline() async {
    return _isOnline;
  }

  @override
  void dispose() {
    _onlineController.close();
  }
}
