/// SAHOOL Service Switcher
/// نظام التبديل بين الخدمات للمقارنة والاختبار
///
/// يتيح للمستخدم:
/// - التبديل بين الخدمات القديمة والحديثة
/// - مقارنة الأداء والنتائج
/// - اختبار الخدمات قبل الترقية

import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';
import 'dart:async';
import 'package:http/http.dart' as http;

/// أنواع الخدمات المتاحة
enum ServiceType {
  satellite,
  weather,
  ndvi,
  fertilizer,
  irrigation,
  cropHealth,
  community,
  notifications,
  tasks,
  equipment,
}

/// نسخ الخدمة
enum ServiceVersion {
  legacy,
  modern,
  mock,
}

/// حالة الخدمة
enum ServiceStatus {
  deprecated,
  active,
  beta,
  development,
}

/// إعدادات نقطة النهاية
class EndpointConfig {
  final int port;
  final String endpoint;
  final ServiceStatus status;

  const EndpointConfig({
    required this.port,
    required this.endpoint,
    this.status = ServiceStatus.active,
  });
}

/// إعدادات الخدمة
class ServiceConfig {
  final String name;
  final String nameAr;
  final EndpointConfig? legacy;
  final EndpointConfig modern;
  final EndpointConfig? mock;

  const ServiceConfig({
    required this.name,
    required this.nameAr,
    this.legacy,
    required this.modern,
    this.mock,
  });

  bool get hasConflict => legacy != null;
}

/// سجل الخدمات
class ServiceRegistry {
  static const Map<ServiceType, ServiceConfig> services = {
    ServiceType.satellite: ServiceConfig(
      name: 'Satellite Service',
      nameAr: 'خدمة الأقمار الصناعية',
      legacy: EndpointConfig(
        port: 8107,
        endpoint: '/ndvi',
        status: ServiceStatus.deprecated,
      ),
      modern: EndpointConfig(
        port: 8090,
        endpoint: '/v1/satellite/analyze',
      ),
      mock: EndpointConfig(
        port: 8000,
        endpoint: '/api/v1/ndvi',
      ),
    ),
    ServiceType.weather: ServiceConfig(
      name: 'Weather Service',
      nameAr: 'خدمة الطقس',
      legacy: EndpointConfig(
        port: 8108,
        endpoint: '/forecast',
        status: ServiceStatus.deprecated,
      ),
      modern: EndpointConfig(
        port: 8092,
        endpoint: '/v1/weather/forecast',
      ),
      mock: EndpointConfig(
        port: 8000,
        endpoint: '/api/v1/weather',
      ),
    ),
    ServiceType.ndvi: ServiceConfig(
      name: 'NDVI Engine',
      nameAr: 'محرك NDVI',
      legacy: EndpointConfig(
        port: 8107,
        endpoint: '/ndvi/{fieldId}',
        status: ServiceStatus.deprecated,
      ),
      modern: EndpointConfig(
        port: 8090,
        endpoint: '/v1/analyze/{fieldId}',
      ),
      mock: EndpointConfig(
        port: 8000,
        endpoint: '/api/v1/ndvi/summary',
      ),
    ),
    ServiceType.fertilizer: ServiceConfig(
      name: 'Fertilizer Advisor',
      nameAr: 'مستشار التسميد',
      legacy: EndpointConfig(
        port: 8105,
        endpoint: '/advise',
        status: ServiceStatus.deprecated,
      ),
      modern: EndpointConfig(
        port: 8093,
        endpoint: '/v1/fertilizer/recommend',
      ),
      mock: EndpointConfig(
        port: 8000,
        endpoint: '/api/v1/fertilizer',
      ),
    ),
    ServiceType.irrigation: ServiceConfig(
      name: 'Irrigation Smart',
      nameAr: 'الري الذكي',
      modern: EndpointConfig(
        port: 8094,
        endpoint: '/v1/irrigation/schedule',
      ),
      mock: EndpointConfig(
        port: 8000,
        endpoint: '/api/v1/irrigation',
      ),
    ),
    ServiceType.cropHealth: ServiceConfig(
      name: 'Crop Health AI',
      nameAr: 'صحة المحاصيل (AI)',
      legacy: EndpointConfig(
        port: 8100,
        endpoint: '/diagnose',
        status: ServiceStatus.deprecated,
      ),
      modern: EndpointConfig(
        port: 8095,
        endpoint: '/v1/diagnose',
      ),
      mock: EndpointConfig(
        port: 8000,
        endpoint: '/api/v1/crop-health',
      ),
    ),
    ServiceType.community: ServiceConfig(
      name: 'Community Chat',
      nameAr: 'الدردشة المجتمعية',
      legacy: EndpointConfig(
        port: 8099,
        endpoint: '/ws',
        status: ServiceStatus.deprecated,
      ),
      modern: EndpointConfig(
        port: 8097,
        endpoint: '/ws',
      ),
      mock: EndpointConfig(
        port: 8081,
        endpoint: '/events',
      ),
    ),
    ServiceType.notifications: ServiceConfig(
      name: 'Notification Service',
      nameAr: 'خدمة الإشعارات',
      legacy: EndpointConfig(
        port: 8089,
        endpoint: '/notify',
        status: ServiceStatus.deprecated,
      ),
      modern: EndpointConfig(
        port: 8110,
        endpoint: '/v1/notify',
      ),
      mock: EndpointConfig(
        port: 8000,
        endpoint: '/api/v1/alerts',
      ),
    ),
    ServiceType.tasks: ServiceConfig(
      name: 'Task Service',
      nameAr: 'خدمة المهام',
      modern: EndpointConfig(
        port: 8103,
        endpoint: '/api/v1/tasks',
      ),
      mock: EndpointConfig(
        port: 8000,
        endpoint: '/api/v1/tasks',
      ),
    ),
    ServiceType.equipment: ServiceConfig(
      name: 'Equipment Service',
      nameAr: 'خدمة المعدات',
      modern: EndpointConfig(
        port: 8101,
        endpoint: '/api/v1/equipment',
      ),
      mock: EndpointConfig(
        port: 8000,
        endpoint: '/api/v1/equipment',
      ),
    ),
  };

  /// الحصول على الخدمات المتعارضة فقط
  static List<MapEntry<ServiceType, ServiceConfig>> get conflictingServices {
    return services.entries.where((e) => e.value.hasConflict).toList();
  }
}

/// نتيجة فحص الصحة
class HealthCheckResult {
  final bool healthy;
  final int latency;
  final String? error;

  const HealthCheckResult({
    required this.healthy,
    required this.latency,
    this.error,
  });
}

/// مدير تبديل الخدمات
class ServiceSwitcher {
  static const String _storageKey = 'sahool_service_versions';
  static ServiceSwitcher? _instance;

  final Map<ServiceType, ServiceVersion> _versions = {};
  final StreamController<Map<ServiceType, ServiceVersion>> _controller =
      StreamController.broadcast();

  /// الحالة الافتراضية
  static const Map<ServiceType, ServiceVersion> _defaults = {
    ServiceType.satellite: ServiceVersion.modern,
    ServiceType.weather: ServiceVersion.modern,
    ServiceType.ndvi: ServiceVersion.modern,
    ServiceType.fertilizer: ServiceVersion.modern,
    ServiceType.irrigation: ServiceVersion.modern,
    ServiceType.cropHealth: ServiceVersion.modern,
    ServiceType.community: ServiceVersion.modern,
    ServiceType.notifications: ServiceVersion.modern,
    ServiceType.tasks: ServiceVersion.modern,
    ServiceType.equipment: ServiceVersion.modern,
  };

  ServiceSwitcher._();

  static ServiceSwitcher get instance {
    _instance ??= ServiceSwitcher._();
    return _instance!;
  }

  /// Stream للاستماع للتغييرات
  Stream<Map<ServiceType, ServiceVersion>> get onVersionsChanged =>
      _controller.stream;

  /// تحميل الإعدادات المحفوظة
  Future<void> initialize() async {
    final prefs = await SharedPreferences.getInstance();
    final stored = prefs.getString(_storageKey);

    if (stored != null) {
      try {
        final Map<String, dynamic> parsed = jsonDecode(stored);
        for (final entry in parsed.entries) {
          final serviceType = ServiceType.values.firstWhere(
            (e) => e.name == entry.key,
            orElse: () => ServiceType.satellite,
          );
          final version = ServiceVersion.values.firstWhere(
            (e) => e.name == entry.value,
            orElse: () => ServiceVersion.modern,
          );
          _versions[serviceType] = version;
        }
      } catch (e) {
        print('Failed to load service versions: $e');
      }
    }

    // تطبيق الإعدادات الافتراضية للخدمات الغير محفوظة
    for (final entry in _defaults.entries) {
      _versions.putIfAbsent(entry.key, () => entry.value);
    }
  }

  /// حفظ الإعدادات
  Future<void> _save() async {
    final prefs = await SharedPreferences.getInstance();
    final Map<String, String> toSave = {};

    for (final entry in _versions.entries) {
      toSave[entry.key.name] = entry.value.name;
    }

    await prefs.setString(_storageKey, jsonEncode(toSave));
    _controller.add(Map.from(_versions));
  }

  /// الحصول على نسخة خدمة
  ServiceVersion getVersion(ServiceType service) {
    return _versions[service] ?? _defaults[service] ?? ServiceVersion.modern;
  }

  /// تعيين نسخة خدمة
  Future<void> setVersion(ServiceType service, ServiceVersion version) async {
    _versions[service] = version;
    await _save();
  }

  /// الحصول على جميع النسخ
  Map<ServiceType, ServiceVersion> getAllVersions() {
    return Map.from(_versions);
  }

  /// تبديل جميع الخدمات
  Future<void> switchAll(ServiceVersion version) async {
    for (final service in ServiceType.values) {
      final config = ServiceRegistry.services[service];
      if (config == null) continue;

      // تأكد من وجود النسخة
      if (version == ServiceVersion.legacy && config.legacy == null) continue;
      if (version == ServiceVersion.mock && config.mock == null) continue;

      _versions[service] = version;
    }
    await _save();
  }

  /// إعادة تعيين للإعدادات الافتراضية
  Future<void> resetToDefaults() async {
    _versions.clear();
    _versions.addAll(_defaults);
    await _save();
  }

  /// الحصول على URL الخدمة
  String getServiceUrl(ServiceType service, {String baseHost = '10.0.2.2'}) {
    final config = ServiceRegistry.services[service];
    if (config == null) return '';

    final version = getVersion(service);
    EndpointConfig? endpointConfig;

    switch (version) {
      case ServiceVersion.legacy:
        endpointConfig = config.legacy;
        break;
      case ServiceVersion.mock:
        endpointConfig = config.mock;
        break;
      case ServiceVersion.modern:
      default:
        endpointConfig = config.modern;
    }

    endpointConfig ??= config.modern;

    return 'http://$baseHost:${endpointConfig.port}${endpointConfig.endpoint}';
  }

  /// فحص صحة خدمة
  Future<HealthCheckResult> checkHealth(
    ServiceType service,
    ServiceVersion version, {
    String baseHost = '10.0.2.2',
  }) async {
    final config = ServiceRegistry.services[service];
    if (config == null) {
      return const HealthCheckResult(
        healthy: false,
        latency: -1,
        error: 'Service not found',
      );
    }

    EndpointConfig? endpointConfig;
    switch (version) {
      case ServiceVersion.legacy:
        endpointConfig = config.legacy;
        break;
      case ServiceVersion.mock:
        endpointConfig = config.mock;
        break;
      case ServiceVersion.modern:
        endpointConfig = config.modern;
        break;
    }

    if (endpointConfig == null) {
      return const HealthCheckResult(
        healthy: false,
        latency: -1,
        error: 'Version not available',
      );
    }

    final url = 'http://$baseHost:${endpointConfig.port}/healthz';
    final stopwatch = Stopwatch()..start();

    try {
      final response = await http.get(Uri.parse(url)).timeout(
            const Duration(seconds: 5),
          );
      stopwatch.stop();

      return HealthCheckResult(
        healthy: response.statusCode == 200,
        latency: stopwatch.elapsedMilliseconds,
      );
    } catch (e) {
      stopwatch.stop();
      return HealthCheckResult(
        healthy: false,
        latency: stopwatch.elapsedMilliseconds,
        error: e.toString(),
      );
    }
  }

  /// فحص صحة جميع الخدمات
  Future<Map<ServiceType, Map<ServiceVersion, HealthCheckResult>>>
      checkAllHealth({String baseHost = '10.0.2.2'}) async {
    final results = <ServiceType, Map<ServiceVersion, HealthCheckResult>>{};

    for (final entry in ServiceRegistry.services.entries) {
      final service = entry.key;
      final config = entry.value;
      results[service] = {};

      // Modern
      results[service]![ServiceVersion.modern] = await checkHealth(
        service,
        ServiceVersion.modern,
        baseHost: baseHost,
      );

      // Legacy
      if (config.legacy != null) {
        results[service]![ServiceVersion.legacy] = await checkHealth(
          service,
          ServiceVersion.legacy,
          baseHost: baseHost,
        );
      }

      // Mock
      if (config.mock != null) {
        results[service]![ServiceVersion.mock] = await checkHealth(
          service,
          ServiceVersion.mock,
          baseHost: baseHost,
        );
      }
    }

    return results;
  }

  /// إغلاق الموارد
  void dispose() {
    _controller.close();
  }
}
