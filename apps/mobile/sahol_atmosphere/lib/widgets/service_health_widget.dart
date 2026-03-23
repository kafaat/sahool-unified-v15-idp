// ═══════════════════════════════════════════════════════════════════════════════════════
// SAHOOL ATMOSPHERE - Service Health Widget
// ودجت صحة الخدمات
// ═══════════════════════════════════════════════════════════════════════════════════════
//
// Features:
// - Real-time service health monitoring
// - Connection status indicator
// - Glassmorphism design
//
// ═══════════════════════════════════════════════════════════════════════════════════════

import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:dio/dio.dart';
import '../theme/atmosphere_theme.dart';

/// Service health status
enum HealthStatus { healthy, degraded, unhealthy, checking }

/// Service health data
class ServiceHealthData {
  final String name;
  final String nameAr;
  final HealthStatus status;
  final int latencyMs;
  final DateTime checkedAt;

  const ServiceHealthData({
    required this.name,
    required this.nameAr,
    required this.status,
    required this.latencyMs,
    required this.checkedAt,
  });
}

/// Service configuration
class _ServiceConfig {
  final String name;
  final String nameAr;
  final String endpoint;

  const _ServiceConfig(this.name, this.nameAr, this.endpoint);
}

/// Service Health Widget
/// ودجت صحة الخدمات
class ServiceHealthWidget extends StatefulWidget {
  final bool compact;
  final VoidCallback? onTap;

  const ServiceHealthWidget({
    super.key,
    this.compact = false,
    this.onTap,
  });

  @override
  State<ServiceHealthWidget> createState() => _ServiceHealthWidgetState();
}

class _ServiceHealthWidgetState extends State<ServiceHealthWidget> {
  final List<ServiceHealthData> _services = [];
  bool _isChecking = false;
  DateTime? _lastChecked;
  Timer? _refreshTimer;

  // Dio client for health checks
  late Dio _dio;

  // Services to monitor
  static const List<_ServiceConfig> _serviceConfigs = [
    _ServiceConfig('Fields', 'الحقول', '/api/v1/fields/healthz'),
    _ServiceConfig('Weather', 'الطقس', '/api/v1/weather/healthz'),
    _ServiceConfig('NDVI', 'NDVI', '/api/v1/ndvi/healthz'),
    _ServiceConfig('Tasks', 'المهام', '/api/v1/tasks/healthz'),
  ];

  @override
  void initState() {
    super.initState();
    _initDio();
    _checkHealth();

    // Auto-refresh every 60 seconds
    _refreshTimer = Timer.periodic(
      const Duration(seconds: 60),
      (_) => _checkHealth(),
    );
  }

  void _initDio() {
    _dio = Dio(BaseOptions(
      // Use environment variable or default
      baseUrl: const String.fromEnvironment(
        'API_URL',
        defaultValue: 'http://localhost:8000',
      ),
      connectTimeout: const Duration(seconds: 5),
      receiveTimeout: const Duration(seconds: 5),
    ));
  }

  @override
  void dispose() {
    _refreshTimer?.cancel();
    _dio.close();
    super.dispose();
  }

  Future<void> _checkHealth() async {
    if (_isChecking) return;

    setState(() => _isChecking = true);

    final List<ServiceHealthData> results = [];

    for (final config in _serviceConfigs) {
      final stopwatch = Stopwatch()..start();

      try {
        final response = await _dio.get(
          config.endpoint,
          options: Options(validateStatus: (_) => true),
        );

        stopwatch.stop();
        final latency = stopwatch.elapsedMilliseconds;

        HealthStatus status;
        if (response.statusCode == 200) {
          status = latency > 2000 ? HealthStatus.degraded : HealthStatus.healthy;
        } else if (response.statusCode != null && response.statusCode! < 500) {
          status = HealthStatus.degraded;
        } else {
          status = HealthStatus.unhealthy;
        }

        results.add(ServiceHealthData(
          name: config.name,
          nameAr: config.nameAr,
          status: status,
          latencyMs: latency,
          checkedAt: DateTime.now(),
        ));
      } catch (e) {
        stopwatch.stop();
        results.add(ServiceHealthData(
          name: config.name,
          nameAr: config.nameAr,
          status: HealthStatus.unhealthy,
          latencyMs: stopwatch.elapsedMilliseconds,
          checkedAt: DateTime.now(),
        ));
      }
    }

    if (mounted) {
      setState(() {
        _services.clear();
        _services.addAll(results);
        _isChecking = false;
        _lastChecked = DateTime.now();
      });
    }
  }

  Color _getStatusColor(HealthStatus status) {
    switch (status) {
      case HealthStatus.healthy:
        return AtmosphereColors.success;
      case HealthStatus.degraded:
        return AtmosphereColors.warning;
      case HealthStatus.unhealthy:
        return AtmosphereColors.alert;
      case HealthStatus.checking:
        return AtmosphereColors.info;
    }
  }

  IconData _getStatusIcon(HealthStatus status) {
    switch (status) {
      case HealthStatus.healthy:
        return Icons.check_circle;
      case HealthStatus.degraded:
        return Icons.warning_amber;
      case HealthStatus.unhealthy:
        return Icons.error;
      case HealthStatus.checking:
        return Icons.sync;
    }
  }

  int get _healthyCount =>
      _services.where((s) => s.status == HealthStatus.healthy).length;
  int get _degradedCount =>
      _services.where((s) => s.status == HealthStatus.degraded).length;
  int get _unhealthyCount =>
      _services.where((s) => s.status == HealthStatus.unhealthy).length;

  HealthStatus get _overallStatus {
    if (_unhealthyCount > 0) return HealthStatus.unhealthy;
    if (_degradedCount > 0) return HealthStatus.degraded;
    if (_isChecking) return HealthStatus.checking;
    return HealthStatus.healthy;
  }

  @override
  Widget build(BuildContext context) {
    if (widget.compact) {
      return _buildCompactView();
    }
    return _buildExpandedView();
  }

  Widget _buildCompactView() {
    final overallColor = _getStatusColor(_overallStatus);

    return GestureDetector(
      onTap: () {
        HapticFeedback.lightImpact();
        widget.onTap?.call();
      },
      child: Container(
        padding: const EdgeInsets.symmetric(
          horizontal: AtmosphereSpacing.md,
          vertical: AtmosphereSpacing.sm,
        ),
        decoration: BoxDecoration(
          gradient: AtmosphereColors.glassGradient,
          borderRadius: BorderRadius.circular(AtmosphereRadius.md),
          border: Border.all(color: overallColor.withOpacity(0.3)),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              _getStatusIcon(_overallStatus),
              color: overallColor,
              size: 16,
            ),
            const SizedBox(width: AtmosphereSpacing.sm),
            Text(
              '$_healthyCount / ${_services.length}',
              style: AtmosphereTypography.labelSmall.copyWith(
                color: overallColor,
              ),
            ),
            if (_isChecking) ...[
              const SizedBox(width: AtmosphereSpacing.xs),
              SizedBox(
                width: 12,
                height: 12,
                child: CircularProgressIndicator(
                  strokeWidth: 2,
                  color: overallColor,
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildExpandedView() {
    return Container(
      padding: const EdgeInsets.all(AtmosphereSpacing.md),
      decoration: BoxDecoration(
        gradient: AtmosphereColors.glassGradient,
        borderRadius: BorderRadius.circular(AtmosphereRadius.lg),
        border: Border.all(color: AtmosphereColors.glassBorder),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'صحة الخدمات',
                    style: AtmosphereTypography.headlineSmall,
                  ),
                  Text(
                    'SERVICE HEALTH',
                    style: AtmosphereTypography.labelSmall.copyWith(
                      color: AtmosphereColors.success,
                      letterSpacing: 1,
                    ),
                  ),
                ],
              ),
              IconButton(
                icon: Icon(
                  _isChecking ? Icons.sync : Icons.refresh,
                  color: _isChecking
                      ? AtmosphereColors.info
                      : AtmosphereColors.textSecondary,
                ),
                onPressed: _isChecking ? null : () {
                  HapticFeedback.lightImpact();
                  _checkHealth();
                },
              ),
            ],
          ),

          const SizedBox(height: AtmosphereSpacing.md),

          // Summary
          Row(
            children: [
              _buildStatusBadge(HealthStatus.healthy, _healthyCount),
              const SizedBox(width: AtmosphereSpacing.sm),
              _buildStatusBadge(HealthStatus.degraded, _degradedCount),
              const SizedBox(width: AtmosphereSpacing.sm),
              _buildStatusBadge(HealthStatus.unhealthy, _unhealthyCount),
              const Spacer(),
              if (_lastChecked != null)
                Text(
                  _formatTime(_lastChecked!),
                  style: AtmosphereTypography.bodySmall.copyWith(
                    color: AtmosphereColors.textMuted,
                  ),
                ),
            ],
          ),

          const SizedBox(height: AtmosphereSpacing.md),

          // Service list
          ..._services.map((service) => _buildServiceRow(service)),
        ],
      ),
    );
  }

  Widget _buildStatusBadge(HealthStatus status, int count) {
    final color = _getStatusColor(status);
    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: AtmosphereSpacing.sm,
        vertical: AtmosphereSpacing.xs,
      ),
      decoration: BoxDecoration(
        color: color.withOpacity(0.15),
        borderRadius: BorderRadius.circular(AtmosphereRadius.sm),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(_getStatusIcon(status), color: color, size: 14),
          const SizedBox(width: 4),
          Text(
            '$count',
            style: AtmosphereTypography.labelSmall.copyWith(color: color),
          ),
        ],
      ),
    );
  }

  Widget _buildServiceRow(ServiceHealthData service) {
    final color = _getStatusColor(service.status);
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: AtmosphereSpacing.xs),
      child: Row(
        children: [
          Icon(_getStatusIcon(service.status), color: color, size: 16),
          const SizedBox(width: AtmosphereSpacing.sm),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  service.nameAr,
                  style: AtmosphereTypography.bodySmall,
                ),
                Text(
                  service.name,
                  style: AtmosphereTypography.labelSmall.copyWith(
                    color: AtmosphereColors.textMuted,
                    fontSize: 10,
                  ),
                ),
              ],
            ),
          ),
          Text(
            '${service.latencyMs}ms',
            style: AtmosphereTypography.labelSmall.copyWith(
              color: _getLatencyColor(service.latencyMs),
              fontFamily: 'monospace',
            ),
          ),
        ],
      ),
    );
  }

  Color _getLatencyColor(int latency) {
    if (latency < 200) return AtmosphereColors.success;
    if (latency < 500) return AtmosphereColors.warning;
    return AtmosphereColors.alert;
  }

  String _formatTime(DateTime time) {
    final diff = DateTime.now().difference(time);
    if (diff.inSeconds < 60) return 'الآن';
    if (diff.inMinutes < 60) return '${diff.inMinutes} د';
    return '${diff.inHours} س';
  }
}
