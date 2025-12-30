// ═══════════════════════════════════════════════════════════════════════════
// SAHOOL - Enhanced Connectivity Service
// خدمة الاتصال المحسنة
// ═══════════════════════════════════════════════════════════════════════════

import 'dart:async';
import 'dart:io';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:http/http.dart' as http;

/// Enhanced connectivity service that monitors both network availability
/// and actual internet connectivity
///
/// خدمة الاتصال المحسنة التي تراقب توفر الشبكة والاتصال الفعلي بالإنترنت
class ConnectivityService {
  final Connectivity _connectivity = Connectivity();
  final List<String> _pingUrls;
  final Duration _checkInterval;
  final Duration _pingTimeout;

  StreamController<ConnectivityStatus>? _statusController;
  Timer? _periodicCheckTimer;
  StreamSubscription<List<ConnectivityResult>>? _connectivitySubscription;

  ConnectivityStatus _currentStatus = ConnectivityStatus.unknown;
  DateTime? _lastSuccessfulCheck;
  int _consecutiveFailures = 0;

  /// Constructor
  ///
  /// [pingUrls] - List of URLs to ping for internet availability check
  /// [checkInterval] - Interval for periodic connectivity checks
  /// [pingTimeout] - Timeout for ping requests
  ConnectivityService({
    List<String>? pingUrls,
    Duration? checkInterval,
    Duration? pingTimeout,
  })  : _pingUrls = pingUrls ??
            [
              'https://www.google.com',
              'https://www.cloudflare.com',
              'https://1.1.1.1',
            ],
        _checkInterval = checkInterval ?? const Duration(seconds: 30),
        _pingTimeout = pingTimeout ?? const Duration(seconds: 5);

  /// Stream of connectivity status changes
  Stream<ConnectivityStatus> get statusStream {
    _statusController ??= StreamController<ConnectivityStatus>.broadcast(
      onListen: _startMonitoring,
      onCancel: _stopMonitoring,
    );
    return _statusController!.stream;
  }

  /// Get current connectivity status
  ConnectivityStatus get currentStatus => _currentStatus;

  /// Check if currently online
  bool get isOnline =>
      _currentStatus == ConnectivityStatus.online ||
      _currentStatus == ConnectivityStatus.poorConnection;

  /// Check if currently offline
  bool get isOffline => _currentStatus == ConnectivityStatus.offline;

  /// Check if connection quality is poor
  bool get isPoorConnection =>
      _currentStatus == ConnectivityStatus.poorConnection;

  /// Check if currently reconnecting
  bool get isReconnecting => _currentStatus == ConnectivityStatus.reconnecting;

  /// Time of last successful connectivity check
  DateTime? get lastSuccessfulCheck => _lastSuccessfulCheck;

  /// Start monitoring connectivity
  void _startMonitoring() {
    // Check initial connectivity
    _checkConnectivity();

    // Listen to connectivity changes
    _connectivitySubscription =
        _connectivity.onConnectivityChanged.listen(_onConnectivityChanged);

    // Start periodic checks
    _periodicCheckTimer = Timer.periodic(_checkInterval, (_) {
      _checkConnectivity();
    });
  }

  /// Stop monitoring connectivity
  void _stopMonitoring() {
    _periodicCheckTimer?.cancel();
    _connectivitySubscription?.cancel();
  }

  /// Handle connectivity changes from connectivity_plus
  void _onConnectivityChanged(List<ConnectivityResult> results) {
    final hasNetworkConnection = results.isNotEmpty &&
        !results.every((r) => r == ConnectivityResult.none);

    if (!hasNetworkConnection) {
      _updateStatus(ConnectivityStatus.offline);
    } else {
      // Network is available, but check actual internet connectivity
      _checkInternetAvailability();
    }
  }

  /// Check connectivity (network + internet availability)
  Future<void> _checkConnectivity() async {
    try {
      // First check if we have network connection
      final results = await _connectivity.checkConnectivity();
      final hasNetworkConnection = results.isNotEmpty &&
          !results.every((r) => r == ConnectivityResult.none);

      if (!hasNetworkConnection) {
        _updateStatus(ConnectivityStatus.offline);
        return;
      }

      // Network is available, check actual internet connectivity
      await _checkInternetAvailability();
    } catch (e) {
      _updateStatus(ConnectivityStatus.offline);
    }
  }

  /// Check actual internet availability by pinging known URLs
  Future<void> _checkInternetAvailability() async {
    final startTime = DateTime.now();
    bool hasInternet = false;

    // Try pinging each URL until one succeeds
    for (final url in _pingUrls) {
      try {
        final response = await http
            .head(Uri.parse(url))
            .timeout(_pingTimeout);

        if (response.statusCode >= 200 && response.statusCode < 400) {
          hasInternet = true;
          break;
        }
      } on SocketException {
        // No internet connection
        continue;
      } on TimeoutException {
        // Timeout - might indicate poor connection
        continue;
      } catch (e) {
        // Other errors
        continue;
      }
    }

    final responseTime = DateTime.now().difference(startTime);

    if (hasInternet) {
      _consecutiveFailures = 0;
      _lastSuccessfulCheck = DateTime.now();

      // Check if connection is poor based on response time
      if (responseTime > const Duration(seconds: 3)) {
        _updateStatus(ConnectivityStatus.poorConnection);
      } else {
        _updateStatus(ConnectivityStatus.online);
      }
    } else {
      _consecutiveFailures++;

      if (_consecutiveFailures == 1 &&
          _currentStatus == ConnectivityStatus.online) {
        // First failure after being online - might be temporary
        _updateStatus(ConnectivityStatus.reconnecting);
      } else if (_consecutiveFailures >= 2) {
        // Multiple consecutive failures - definitely offline
        _updateStatus(ConnectivityStatus.offline);
      }
    }
  }

  /// Update connectivity status and notify listeners
  void _updateStatus(ConnectivityStatus newStatus) {
    if (_currentStatus != newStatus) {
      _currentStatus = newStatus;
      _statusController?.add(newStatus);
    }
  }

  /// Manually trigger connectivity check
  Future<ConnectivityStatus> checkNow() async {
    await _checkConnectivity();
    return _currentStatus;
  }

  /// Attempt to reconnect
  Future<bool> tryReconnect() async {
    _updateStatus(ConnectivityStatus.reconnecting);
    await _checkConnectivity();
    return isOnline;
  }

  /// Dispose resources
  void dispose() {
    _stopMonitoring();
    _statusController?.close();
  }
}

/// Connectivity status enumeration
/// حالة الاتصال
enum ConnectivityStatus {
  /// Unknown status (initial state)
  /// حالة غير معروفة
  unknown,

  /// Fully online with good connection
  /// متصل بالإنترنت بشكل جيد
  online,

  /// Connected but with poor/slow connection
  /// متصل ولكن الاتصال ضعيف
  poorConnection,

  /// Attempting to reconnect
  /// محاولة إعادة الاتصال
  reconnecting,

  /// Completely offline
  /// غير متصل
  offline,
}

/// Extension methods for ConnectivityStatus
extension ConnectivityStatusExtension on ConnectivityStatus {
  /// Check if status indicates some level of connectivity
  bool get hasConnection =>
      this == ConnectivityStatus.online ||
      this == ConnectivityStatus.poorConnection;

  /// Check if status indicates no connectivity
  bool get hasNoConnection =>
      this == ConnectivityStatus.offline ||
      this == ConnectivityStatus.unknown;

  /// Get display message for status
  String get displayMessage {
    switch (this) {
      case ConnectivityStatus.unknown:
        return 'جاري التحقق من الاتصال...';
      case ConnectivityStatus.online:
        return 'متصل';
      case ConnectivityStatus.poorConnection:
        return 'اتصال ضعيف';
      case ConnectivityStatus.reconnecting:
        return 'إعادة الاتصال...';
      case ConnectivityStatus.offline:
        return 'غير متصل - البيانات محفوظة محلياً';
    }
  }

  /// Get English display message for status
  String get displayMessageEn {
    switch (this) {
      case ConnectivityStatus.unknown:
        return 'Checking connection...';
      case ConnectivityStatus.online:
        return 'Online';
      case ConnectivityStatus.poorConnection:
        return 'Poor connection';
      case ConnectivityStatus.reconnecting:
        return 'Reconnecting...';
      case ConnectivityStatus.offline:
        return 'Offline - Data saved locally';
    }
  }
}
