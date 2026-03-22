import 'dart:async';

import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../utils/app_logger.dart';
import '../error_handling/app_exceptions.dart';

/// Network connectivity state with detailed information
class NetworkConnectivityState {
  /// Whether device has network connectivity
  final bool isConnected;

  /// Type of connection (wifi, mobile, ethernet, none)
  final ConnectivityResult connectionType;

  /// Whether the connection has been verified with an actual request
  final bool isVerified;

  /// Last time connectivity was checked
  final DateTime lastCheck;

  /// Network latency in milliseconds (if measured)
  final int? latencyMs;

  /// Signal strength indicator (if available)
  final NetworkQuality quality;

  /// Error message if connectivity check failed
  final String? errorMessage;

  const NetworkConnectivityState({
    required this.isConnected,
    required this.connectionType,
    this.isVerified = false,
    required this.lastCheck,
    this.latencyMs,
    this.quality = NetworkQuality.unknown,
    this.errorMessage,
  });

  /// Create an offline state
  factory NetworkConnectivityState.offline() {
    return NetworkConnectivityState(
      isConnected: false,
      connectionType: ConnectivityResult.none,
      isVerified: true,
      lastCheck: DateTime.now(),
      quality: NetworkQuality.none,
    );
  }

  /// Create an online state
  factory NetworkConnectivityState.online(ConnectivityResult type) {
    return NetworkConnectivityState(
      isConnected: true,
      connectionType: type,
      isVerified: false,
      lastCheck: DateTime.now(),
      quality: NetworkQuality.unknown,
    );
  }

  /// Copy with updated values
  NetworkConnectivityState copyWith({
    bool? isConnected,
    ConnectivityResult? connectionType,
    bool? isVerified,
    DateTime? lastCheck,
    int? latencyMs,
    NetworkQuality? quality,
    String? errorMessage,
  }) {
    return NetworkConnectivityState(
      isConnected: isConnected ?? this.isConnected,
      connectionType: connectionType ?? this.connectionType,
      isVerified: isVerified ?? this.isVerified,
      lastCheck: lastCheck ?? this.lastCheck,
      latencyMs: latencyMs ?? this.latencyMs,
      quality: quality ?? this.quality,
      errorMessage: errorMessage ?? this.errorMessage,
    );
  }

  /// Whether this is a metered connection (mobile data)
  bool get isMetered => connectionType == ConnectivityResult.mobile;

  /// Whether this is an unmetered connection (wifi/ethernet)
  bool get isUnmetered =>
      connectionType == ConnectivityResult.wifi ||
      connectionType == ConnectivityResult.ethernet;

  @override
  String toString() {
    return 'NetworkConnectivityState('
        'connected: $isConnected, '
        'type: ${connectionType.name}, '
        'verified: $isVerified, '
        'quality: ${quality.name}, '
        'latency: ${latencyMs ?? "N/A"}ms'
        ')';
  }
}

/// Network quality classification
enum NetworkQuality {
  /// No connection
  none,

  /// Poor connection (high latency, unstable)
  poor,

  /// Fair connection (moderate latency)
  fair,

  /// Good connection (low latency)
  good,

  /// Excellent connection (very low latency)
  excellent,

  /// Unknown (not yet measured)
  unknown,
}

/// Network quality extension methods
extension NetworkQualityExtension on NetworkQuality {
  /// Get quality from latency measurement
  static NetworkQuality fromLatency(int latencyMs) {
    if (latencyMs < 0) return NetworkQuality.unknown;
    if (latencyMs < 100) return NetworkQuality.excellent;
    if (latencyMs < 300) return NetworkQuality.good;
    if (latencyMs < 1000) return NetworkQuality.fair;
    return NetworkQuality.poor;
  }

  /// Whether this quality is acceptable for real-time operations
  bool get isAcceptableForRealtime =>
      this == NetworkQuality.excellent || this == NetworkQuality.good;

  /// Whether this quality is acceptable for background sync
  bool get isAcceptableForSync =>
      this != NetworkQuality.none && this != NetworkQuality.unknown;
}

/// Network connectivity monitor service
/// Provides real-time connectivity monitoring with quality assessment
class NetworkConnectivityService {
  final Connectivity _connectivity;
  final Dio? _healthCheckDio;
  final String _healthCheckUrl;
  final Duration _healthCheckInterval;
  final Duration _healthCheckTimeout;

  StreamSubscription<List<ConnectivityResult>>? _connectivitySubscription;
  Timer? _healthCheckTimer;

  final _stateController =
      StreamController<NetworkConnectivityState>.broadcast();
  NetworkConnectivityState _currentState = NetworkConnectivityState.offline();

  NetworkConnectivityService({
    Connectivity? connectivity,
    Dio? healthCheckDio,
    String? healthCheckUrl,
    Duration healthCheckInterval = const Duration(seconds: 30),
    Duration healthCheckTimeout = const Duration(seconds: 5),
  })  : _connectivity = connectivity ?? Connectivity(),
        _healthCheckDio = healthCheckDio,
        _healthCheckUrl = healthCheckUrl ?? 'https://api.sahool.app/healthz',
        _healthCheckInterval = healthCheckInterval,
        _healthCheckTimeout = healthCheckTimeout;

  /// Stream of connectivity state changes
  Stream<NetworkConnectivityState> get stateStream => _stateController.stream;

  /// Current connectivity state
  NetworkConnectivityState get currentState => _currentState;

  /// Whether currently connected
  bool get isConnected => _currentState.isConnected;

  /// Whether connection has been verified
  bool get isVerified => _currentState.isVerified;

  /// Start monitoring connectivity
  Future<void> startMonitoring() async {
    // Initial check
    await checkConnectivity();

    // Listen for connectivity changes
    _connectivitySubscription = _connectivity.onConnectivityChanged.listen(
      _handleConnectivityChange,
      onError: (error) {
        AppLogger.e('Connectivity stream error',
            tag: 'NetworkConnectivity', error: error);
      },
    );

    // Start periodic health checks if Dio is configured
    if (_healthCheckDio != null) {
      _startHealthChecks();
    }

    if (kDebugMode) {
      AppLogger.i('Network connectivity monitoring started',
          tag: 'NetworkConnectivity');
    }
  }

  /// Stop monitoring connectivity
  void stopMonitoring() {
    _connectivitySubscription?.cancel();
    _connectivitySubscription = null;
    _healthCheckTimer?.cancel();
    _healthCheckTimer = null;

    if (kDebugMode) {
      AppLogger.i('Network connectivity monitoring stopped',
          tag: 'NetworkConnectivity');
    }
  }

  /// Check connectivity manually
  Future<NetworkConnectivityState> checkConnectivity() async {
    try {
      final results = await _connectivity.checkConnectivity();
      await _handleConnectivityChange(results);
      return _currentState;
    } catch (e) {
      AppLogger.e('Error checking connectivity',
          tag: 'NetworkConnectivity', error: e);
      _updateState(NetworkConnectivityState.offline().copyWith(
        errorMessage: e.toString(),
      ));
      return _currentState;
    }
  }

  /// Verify connectivity with an actual network request
  Future<bool> verifyConnectivity() async {
    if (_healthCheckDio == null) {
      // Without Dio, we can only rely on the connectivity plugin
      return _currentState.isConnected;
    }

    try {
      final stopwatch = Stopwatch()..start();

      final response = await _healthCheckDio.get(
        _healthCheckUrl,
        options: Options(
          receiveTimeout: _healthCheckTimeout,
          sendTimeout: _healthCheckTimeout,
          validateStatus: (status) => status != null && status < 500,
        ),
      );

      stopwatch.stop();
      final latencyMs = stopwatch.elapsedMilliseconds;

      if (response.statusCode == 200) {
        _updateState(_currentState.copyWith(
          isConnected: true,
          isVerified: true,
          latencyMs: latencyMs,
          quality: NetworkQualityExtension.fromLatency(latencyMs),
          lastCheck: DateTime.now(),
          errorMessage: null,
        ));

        if (kDebugMode) {
          AppLogger.d('Connectivity verified',
              tag: 'NetworkConnectivity',
              data: {
                'latency': latencyMs,
                'quality': _currentState.quality.name,
              });
        }

        return true;
      }
    } on DioException catch (e) {
      AppLogger.w('Health check failed', tag: 'NetworkConnectivity', data: {
        'error': e.type.toString(),
      });

      if (e.type == DioExceptionType.connectionError ||
          e.type == DioExceptionType.connectionTimeout) {
        _updateState(_currentState.copyWith(
          isConnected: false,
          isVerified: true,
          quality: NetworkQuality.none,
          lastCheck: DateTime.now(),
          errorMessage: 'Connection failed',
        ));
      }
    } catch (e) {
      AppLogger.e('Error verifying connectivity',
          tag: 'NetworkConnectivity', error: e);
    }

    return false;
  }

  /// Handle connectivity change events
  Future<void> _handleConnectivityChange(
      List<ConnectivityResult> results) async {
    final hasConnection = results.isNotEmpty &&
        !results.every((r) => r == ConnectivityResult.none);

    final connectionType =
        results.isNotEmpty ? results.first : ConnectivityResult.none;

    if (hasConnection) {
      _updateState(NetworkConnectivityState(
        isConnected: true,
        connectionType: connectionType,
        isVerified: false,
        lastCheck: DateTime.now(),
        quality: NetworkQuality.unknown,
      ));

      // Verify with actual request
      await verifyConnectivity();
    } else {
      _updateState(NetworkConnectivityState(
        isConnected: false,
        connectionType: ConnectivityResult.none,
        isVerified: true,
        lastCheck: DateTime.now(),
        quality: NetworkQuality.none,
      ));
    }
  }

  /// Start periodic health checks
  void _startHealthChecks() {
    _healthCheckTimer?.cancel();
    _healthCheckTimer = Timer.periodic(_healthCheckInterval, (_) async {
      if (_currentState.isConnected) {
        await verifyConnectivity();
      }
    });
  }

  /// Update state and notify listeners
  void _updateState(NetworkConnectivityState newState) {
    if (_currentState.isConnected != newState.isConnected ||
        _currentState.quality != newState.quality) {
      if (kDebugMode) {
        AppLogger.i('Connectivity state changed',
            tag: 'NetworkConnectivity',
            data: {
              'from': _currentState.toString(),
              'to': newState.toString(),
            });
      }
    }

    _currentState = newState;
    _stateController.add(newState);
  }

  /// Dispose resources
  void dispose() {
    stopMonitoring();
    _stateController.close();
  }
}

/// Riverpod provider for network connectivity service
final networkConnectivityServiceProvider =
    Provider<NetworkConnectivityService>((ref) {
  final service = NetworkConnectivityService();
  ref.onDispose(() => service.dispose());
  return service;
});

/// Riverpod provider for current network connectivity state
final networkConnectivityStateProvider =
    StreamProvider<NetworkConnectivityState>((ref) {
  final service = ref.watch(networkConnectivityServiceProvider);
  return service.stateStream;
});

/// Riverpod provider for simple online/offline check
final isOnlineProvider = Provider<bool>((ref) {
  final stateAsync = ref.watch(networkConnectivityStateProvider);
  return stateAsync.maybeWhen(
    data: (state) => state.isConnected,
    orElse: () => false,
  );
});

/// Dio interceptor that checks connectivity before requests
class ConnectivityInterceptor extends Interceptor {
  final NetworkConnectivityService _connectivityService;
  final bool blockOfflineRequests;
  final bool queueOfflineRequests;

  ConnectivityInterceptor({
    required NetworkConnectivityService connectivityService,
    this.blockOfflineRequests = false,
    this.queueOfflineRequests = false,
  }) : _connectivityService = connectivityService;

  @override
  Future<void> onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    // Check connectivity
    if (!_connectivityService.isConnected) {
      if (blockOfflineRequests) {
        handler.reject(
          DioException(
            requestOptions: options,
            type: DioExceptionType.connectionError,
            error: NetworkException.noConnection(),
          ),
        );
        return;
      }

      if (kDebugMode) {
        AppLogger.w('Request while offline',
            tag: 'ConnectivityInterceptor',
            data: {
              'path': options.path,
              'queued': queueOfflineRequests,
            });
      }
    }

    // Add connectivity info to request extras
    options.extra['connectivity_state'] = _connectivityService.currentState;

    handler.next(options);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    // Update connectivity state on connection errors
    if (err.type == DioExceptionType.connectionError ||
        err.type == DioExceptionType.connectionTimeout) {
      _connectivityService.checkConnectivity();
    }

    handler.next(err);
  }
}
