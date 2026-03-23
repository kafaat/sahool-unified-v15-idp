/// SAHOOL Service Health Monitor
/// مراقب صحة الخدمات
///
/// Features:
/// - Monitor service health status
/// - Display service status to user
/// - Graceful degradation support
/// - Automatic health checks
/// - Health dashboard support
library;

import 'dart:async';
import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../utils/app_logger.dart';
import 'service_registry.dart';
import 'event_bus.dart';

/// Health check result
class HealthCheckResult {
  final String serviceId;
  final ServiceStatus status;
  final Duration latency;
  final DateTime timestamp;
  final String? version;
  final String? errorMessage;
  final Map<String, dynamic>? details;

  const HealthCheckResult({
    required this.serviceId,
    required this.status,
    required this.latency,
    required this.timestamp,
    this.version,
    this.errorMessage,
    this.details,
  });

  bool get isHealthy => status == ServiceStatus.healthy;
  bool get isDegraded => status == ServiceStatus.degraded;
  bool get isUnhealthy => status == ServiceStatus.unhealthy || status == ServiceStatus.offline;
}

/// System health summary
class SystemHealthSummary {
  final ServiceStatus overallStatus;
  final int totalServices;
  final int healthyServices;
  final int degradedServices;
  final int unhealthyServices;
  final int offlineServices;
  final DateTime lastCheck;
  final Map<String, HealthCheckResult> serviceResults;

  const SystemHealthSummary({
    required this.overallStatus,
    required this.totalServices,
    required this.healthyServices,
    required this.degradedServices,
    required this.unhealthyServices,
    required this.offlineServices,
    required this.lastCheck,
    required this.serviceResults,
  });

  double get healthPercentage {
    if (totalServices == 0) return 0;
    return (healthyServices + (degradedServices * 0.5)) / totalServices * 100;
  }

  bool get allHealthy => healthyServices == totalServices;
  bool get anyUnhealthy => unhealthyServices > 0 || offlineServices > 0;
}

/// Service Health Monitor
/// مراقب صحة الخدمات
class ServiceHealthMonitor {
  final Ref _ref;
  final Dio _dio;

  Timer? _periodicCheckTimer;
  final Map<String, HealthCheckResult> _healthResults = {};
  final StreamController<SystemHealthSummary> _summaryController =
      StreamController<SystemHealthSummary>.broadcast();

  bool _isRunning = false;
  DateTime? _lastFullCheck;

  // Configuration
  static const Duration _defaultCheckInterval = Duration(minutes: 5);
  static const Duration _degradedCheckInterval = Duration(minutes: 1);
  static const Duration _healthCheckTimeout = Duration(seconds: 10);

  ServiceHealthMonitor(this._ref)
      : _dio = Dio(BaseOptions(
          connectTimeout: _healthCheckTimeout,
          receiveTimeout: _healthCheckTimeout,
        ));

  /// Stream of health summaries
  Stream<SystemHealthSummary> get healthStream => _summaryController.stream;

  /// Get current health results
  Map<String, HealthCheckResult> get healthResults => Map.unmodifiable(_healthResults);

  /// Is monitor running
  bool get isRunning => _isRunning;

  /// Start periodic health monitoring
  /// بدء مراقبة الصحة الدورية
  void startMonitoring({Duration? interval}) {
    if (_isRunning) return;

    _isRunning = true;

    // Initial check
    checkAllServices();

    // Start periodic checks
    _periodicCheckTimer?.cancel();
    _periodicCheckTimer = Timer.periodic(
      interval ?? _defaultCheckInterval,
      (_) => checkAllServices(),
    );

    AppLogger.i('Health monitoring started', tag: 'HealthMonitor');
  }

  /// Stop health monitoring
  /// إيقاف مراقبة الصحة
  void stopMonitoring() {
    _periodicCheckTimer?.cancel();
    _isRunning = false;
    AppLogger.i('Health monitoring stopped', tag: 'HealthMonitor');
  }

  /// Check all registered services
  /// فحص جميع الخدمات المسجلة
  Future<SystemHealthSummary> checkAllServices() async {
    final registry = _ref.read(serviceRegistryProvider);
    final services = registry.services.values.toList();

    AppLogger.d('Checking health of ${services.length} services', tag: 'HealthMonitor');

    // Check all services in parallel
    final results = await Future.wait(
      services.map((service) => checkService(service)),
    );

    // Update health results
    for (final result in results) {
      _healthResults[result.serviceId] = result;
      registry.updateHealth(
        result.serviceId,
        ServiceHealth(
          serviceId: result.serviceId,
          status: result.status,
          lastCheck: result.timestamp,
          latency: result.latency,
          errorMessage: result.errorMessage,
          metadata: result.details,
        ),
      );
    }

    _lastFullCheck = DateTime.now();

    // Create summary
    final summary = _createSummary(results);
    _summaryController.add(summary);

    // Emit event if system is degraded
    if (summary.anyUnhealthy) {
      _ref.read(eventBusProvider).emit(AppEvent(
            type: EventType.errorOccurred,
            priority: EventPriority.high,
            data: {
              'type': 'service_health',
              'unhealthy_count': summary.unhealthyServices + summary.offlineServices,
              'overall_status': summary.overallStatus.name,
            },
          ));
    }

    return summary;
  }

  /// Check a single service
  /// فحص خدمة واحدة
  Future<HealthCheckResult> checkService(ServiceConfig service) async {
    final startTime = DateTime.now();

    try {
      final response = await _dio.get(service.healthUrl);
      final latency = DateTime.now().difference(startTime);

      final status = _determineStatus(response, latency);
      final version = _extractVersion(response.data);

      return HealthCheckResult(
        serviceId: service.id,
        status: status,
        latency: latency,
        timestamp: DateTime.now(),
        version: version,
        details: response.data is Map ? response.data as Map<String, dynamic> : null,
      );
    } on DioException catch (e) {
      final latency = DateTime.now().difference(startTime);
      final status = _determineStatusFromError(e);

      return HealthCheckResult(
        serviceId: service.id,
        status: status,
        latency: latency,
        timestamp: DateTime.now(),
        errorMessage: _getErrorMessage(e),
      );
    } catch (e) {
      final latency = DateTime.now().difference(startTime);

      return HealthCheckResult(
        serviceId: service.id,
        status: ServiceStatus.unknown,
        latency: latency,
        timestamp: DateTime.now(),
        errorMessage: e.toString(),
      );
    }
  }

  /// Check specific service by ID
  /// فحص خدمة معينة بالمعرف
  Future<HealthCheckResult?> checkServiceById(String serviceId) async {
    final registry = _ref.read(serviceRegistryProvider);
    final service = registry.getService(serviceId);

    if (service == null) return null;

    final result = await checkService(service);
    _healthResults[serviceId] = result;

    registry.updateHealth(
      serviceId,
      ServiceHealth(
        serviceId: serviceId,
        status: result.status,
        lastCheck: result.timestamp,
        latency: result.latency,
        errorMessage: result.errorMessage,
      ),
    );

    return result;
  }

  /// Get health status for a service
  /// الحصول على حالة صحة الخدمة
  HealthCheckResult? getServiceHealth(String serviceId) {
    return _healthResults[serviceId];
  }

  /// Check if service is available for use
  /// التحقق من توفر الخدمة للاستخدام
  bool isServiceAvailable(String serviceId) {
    final result = _healthResults[serviceId];
    if (result == null) return true; // Assume available if not checked
    return result.isHealthy || result.isDegraded;
  }

  /// Get degraded features based on service health
  /// الحصول على الميزات المتدهورة بناءً على صحة الخدمة
  List<String> getDegradedFeatures() {
    final degraded = <String>[];

    for (final entry in _healthResults.entries) {
      if (entry.value.isUnhealthy) {
        final features = _mapServiceToFeatures(entry.key);
        degraded.addAll(features);
      }
    }

    return degraded;
  }

  List<String> _mapServiceToFeatures(String serviceId) {
    switch (serviceId) {
      case 'weather':
        return ['Weather forecast', 'Agricultural calendar'];
      case 'vegetation-analysis':
      case 'vegetation-analysis-service':
        return ['NDVI analysis', 'Satellite imagery', 'Field health'];
      case 'irrigation':
        return ['Smart irrigation', 'Water balance'];
      case 'advisory':
        return ['Fertilizer recommendations', 'Crop diagnostics'];
      case 'notifications':
        return ['Push notifications'];
      case 'billing':
        return ['Billing', 'Subscription'];
      default:
        return [];
    }
  }

  ServiceStatus _determineStatus(Response response, Duration latency) {
    if (response.statusCode != 200) {
      return ServiceStatus.unhealthy;
    }

    // Check latency thresholds
    if (latency.inMilliseconds > 5000) {
      return ServiceStatus.degraded;
    }

    // Check response body for status
    if (response.data is Map) {
      final data = response.data as Map<String, dynamic>;
      final status = data['status'] as String?;

      if (status == 'degraded') {
        return ServiceStatus.degraded;
      }
      if (status == 'unhealthy' || status == 'error') {
        return ServiceStatus.unhealthy;
      }
    }

    return ServiceStatus.healthy;
  }

  ServiceStatus _determineStatusFromError(DioException e) {
    switch (e.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
        return ServiceStatus.degraded;
      case DioExceptionType.connectionError:
        return ServiceStatus.offline;
      case DioExceptionType.badResponse:
        final statusCode = e.response?.statusCode;
        if (statusCode != null && statusCode >= 500) {
          return ServiceStatus.unhealthy;
        }
        return ServiceStatus.degraded;
      default:
        return ServiceStatus.unknown;
    }
  }

  String? _extractVersion(dynamic data) {
    if (data is Map) {
      return data['version'] as String? ?? data['app_version'] as String?;
    }
    return null;
  }

  String _getErrorMessage(DioException e) {
    switch (e.type) {
      case DioExceptionType.connectionTimeout:
        return 'Connection timeout';
      case DioExceptionType.sendTimeout:
        return 'Send timeout';
      case DioExceptionType.receiveTimeout:
        return 'Receive timeout';
      case DioExceptionType.connectionError:
        return 'Connection failed';
      case DioExceptionType.badResponse:
        return 'HTTP ${e.response?.statusCode}';
      default:
        return e.message ?? 'Unknown error';
    }
  }

  SystemHealthSummary _createSummary(List<HealthCheckResult> results) {
    int healthy = 0;
    int degraded = 0;
    int unhealthy = 0;
    int offline = 0;

    final resultMap = <String, HealthCheckResult>{};

    for (final result in results) {
      resultMap[result.serviceId] = result;

      switch (result.status) {
        case ServiceStatus.healthy:
          healthy++;
          break;
        case ServiceStatus.degraded:
          degraded++;
          break;
        case ServiceStatus.unhealthy:
          unhealthy++;
          break;
        case ServiceStatus.offline:
          offline++;
          break;
        default:
          break;
      }
    }

    // Determine overall status
    ServiceStatus overallStatus;
    if (offline > 0 || unhealthy > results.length / 3) {
      overallStatus = ServiceStatus.unhealthy;
    } else if (degraded > 0 || unhealthy > 0) {
      overallStatus = ServiceStatus.degraded;
    } else if (healthy == results.length) {
      overallStatus = ServiceStatus.healthy;
    } else {
      overallStatus = ServiceStatus.unknown;
    }

    return SystemHealthSummary(
      overallStatus: overallStatus,
      totalServices: results.length,
      healthyServices: healthy,
      degradedServices: degraded,
      unhealthyServices: unhealthy,
      offlineServices: offline,
      lastCheck: DateTime.now(),
      serviceResults: resultMap,
    );
  }

  /// Dispose resources
  void dispose() {
    stopMonitoring();
    _summaryController.close();
    _dio.close();
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Riverpod Providers
// ═══════════════════════════════════════════════════════════════════════════════

/// Service Health Monitor Provider
final serviceHealthMonitorProvider = Provider<ServiceHealthMonitor>((ref) {
  final monitor = ServiceHealthMonitor(ref);
  ref.onDispose(() => monitor.dispose());
  return monitor;
});

/// System Health Summary Provider
final systemHealthSummaryProvider = StreamProvider<SystemHealthSummary>((ref) {
  final monitor = ref.watch(serviceHealthMonitorProvider);
  return monitor.healthStream;
});

/// Service Health by ID Provider
final serviceHealthByIdProvider =
    Provider.family<HealthCheckResult?, String>((ref, serviceId) {
  final monitor = ref.watch(serviceHealthMonitorProvider);
  return monitor.getServiceHealth(serviceId);
});

/// Is Service Available Provider
final isServiceAvailableProvider = Provider.family<bool, String>((ref, serviceId) {
  final monitor = ref.watch(serviceHealthMonitorProvider);
  return monitor.isServiceAvailable(serviceId);
});

/// Degraded Features Provider
final degradedFeaturesProvider = Provider<List<String>>((ref) {
  final monitor = ref.watch(serviceHealthMonitorProvider);
  return monitor.getDegradedFeatures();
});

/// Overall System Status Provider
final overallSystemStatusProvider = Provider<ServiceStatus>((ref) {
  final summary = ref.watch(systemHealthSummaryProvider);
  return summary.whenOrNull(data: (s) => s.overallStatus) ?? ServiceStatus.unknown;
});

// ═══════════════════════════════════════════════════════════════════════════════
// UI Widgets
// ═══════════════════════════════════════════════════════════════════════════════

/// Service status indicator widget
class ServiceStatusIndicator extends StatelessWidget {
  final ServiceStatus status;
  final double size;
  final bool showLabel;

  const ServiceStatusIndicator({
    super.key,
    required this.status,
    this.size = 12,
    this.showLabel = false,
  });

  @override
  Widget build(BuildContext context) {
    final color = _getStatusColor();
    final label = _getStatusLabel();

    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: size,
          height: size,
          decoration: BoxDecoration(
            color: color,
            shape: BoxShape.circle,
          ),
        ),
        if (showLabel) ...[
          const SizedBox(width: 4),
          Text(
            label,
            style: TextStyle(
              color: color,
              fontSize: size,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ],
    );
  }

  Color _getStatusColor() {
    switch (status) {
      case ServiceStatus.healthy:
        return Colors.green;
      case ServiceStatus.degraded:
        return Colors.orange;
      case ServiceStatus.unhealthy:
        return Colors.red;
      case ServiceStatus.offline:
        return Colors.grey;
      default:
        return Colors.grey.shade400;
    }
  }

  String _getStatusLabel() {
    switch (status) {
      case ServiceStatus.healthy:
        return 'Healthy';
      case ServiceStatus.degraded:
        return 'Degraded';
      case ServiceStatus.unhealthy:
        return 'Unhealthy';
      case ServiceStatus.offline:
        return 'Offline';
      default:
        return 'Unknown';
    }
  }
}

/// Service health banner widget
class ServiceHealthBanner extends ConsumerWidget {
  const ServiceHealthBanner({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final degradedFeatures = ref.watch(degradedFeaturesProvider);

    if (degradedFeatures.isEmpty) return const SizedBox.shrink();

    return MaterialBanner(
      backgroundColor: Colors.orange.shade50,
      leading: const Icon(Icons.warning_amber, color: Colors.orange),
      content: Text(
        'Some features may be limited: ${degradedFeatures.join(", ")}',
        style: const TextStyle(color: Colors.orange),
      ),
      actions: [
        TextButton(
          onPressed: () => ref.read(serviceHealthMonitorProvider).checkAllServices(),
          child: const Text('Refresh'),
        ),
      ],
    );
  }
}
