/// SAHOOL Service Registry
/// سجل الخدمات - نقطة مركزية لإدارة جميع الخدمات الخلفية
///
/// Features:
/// - Centralized service registration
/// - Service discovery
/// - Health check integration
/// - Service versioning
/// - Graceful degradation support
library;

import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../config/env_config.dart';
import '../utils/app_logger.dart';

/// Service status enumeration
/// حالات الخدمة
enum ServiceStatus {
  unknown,
  healthy,
  degraded,
  unhealthy,
  offline,
}

/// Service tier/layer classification
/// تصنيف طبقة الخدمة
enum ServiceTier {
  /// Data ingestion & normalization
  acquisition,

  /// Feature extraction & AI
  intelligence,

  /// Recommendations & planning
  decision,

  /// User-facing operations
  business,

  /// Core infrastructure
  infrastructure,
}

/// Service configuration model
/// نموذج تكوين الخدمة
class ServiceConfig {
  final String id;
  final String name;
  final String nameAr;
  final String baseUrl;
  final String healthEndpoint;
  final ServiceTier tier;
  final String version;
  final bool isRequired;
  final Duration timeout;
  final List<String> dependencies;
  final Map<String, String> endpoints;

  const ServiceConfig({
    required this.id,
    required this.name,
    required this.nameAr,
    required this.baseUrl,
    this.healthEndpoint = '/healthz',
    required this.tier,
    this.version = 'v1',
    this.isRequired = true,
    this.timeout = const Duration(seconds: 10),
    this.dependencies = const [],
    this.endpoints = const {},
  });

  /// Full health check URL
  String get healthUrl => '$baseUrl$healthEndpoint';

  /// API version prefix
  String get apiPrefix => '/api/$version';

  @override
  String toString() => 'ServiceConfig($id: $baseUrl)';
}

/// Service health status
/// حالة صحة الخدمة
class ServiceHealth {
  final String serviceId;
  final ServiceStatus status;
  final DateTime lastCheck;
  final Duration? latency;
  final String? errorMessage;
  final Map<String, dynamic>? metadata;

  const ServiceHealth({
    required this.serviceId,
    required this.status,
    required this.lastCheck,
    this.latency,
    this.errorMessage,
    this.metadata,
  });

  bool get isHealthy => status == ServiceStatus.healthy;
  bool get isAvailable =>
      status == ServiceStatus.healthy || status == ServiceStatus.degraded;

  ServiceHealth copyWith({
    ServiceStatus? status,
    DateTime? lastCheck,
    Duration? latency,
    String? errorMessage,
    Map<String, dynamic>? metadata,
  }) {
    return ServiceHealth(
      serviceId: serviceId,
      status: status ?? this.status,
      lastCheck: lastCheck ?? this.lastCheck,
      latency: latency ?? this.latency,
      errorMessage: errorMessage ?? this.errorMessage,
      metadata: metadata ?? this.metadata,
    );
  }
}

/// Service Registry - Central point for all backend services
/// سجل الخدمات المركزي
class ServiceRegistry {
  static final ServiceRegistry _instance = ServiceRegistry._internal();
  factory ServiceRegistry() => _instance;
  ServiceRegistry._internal();

  final Map<String, ServiceConfig> _services = {};
  final Map<String, ServiceHealth> _healthCache = {};
  final StreamController<Map<String, ServiceHealth>> _healthController =
      StreamController<Map<String, ServiceHealth>>.broadcast();

  bool _initialized = false;

  /// Stream of health status updates
  Stream<Map<String, ServiceHealth>> get healthStream => _healthController.stream;

  /// Get all registered services
  Map<String, ServiceConfig> get services => Map.unmodifiable(_services);

  /// Get health cache
  Map<String, ServiceHealth> get healthCache => Map.unmodifiable(_healthCache);

  /// Initialize the service registry with all SAHOOL services
  /// تهيئة سجل الخدمات
  Future<void> initialize() async {
    if (_initialized) return;

    AppLogger.i('Initializing Service Registry', tag: 'ServiceRegistry');

    // Register all services based on the 4-layer architecture
    _registerAcquisitionServices();
    _registerIntelligenceServices();
    _registerDecisionServices();
    _registerBusinessServices();
    _registerInfrastructureServices();

    _initialized = true;
    AppLogger.i(
      'Service Registry initialized with ${_services.length} services',
      tag: 'ServiceRegistry',
    );
  }

  /// Register Acquisition Layer Services
  /// تسجيل خدمات طبقة الاستحواذ
  void _registerAcquisitionServices() {
    // Vegetation Analysis Service (was satellite-service)
    register(ServiceConfig(
      id: 'vegetation-analysis',
      name: 'Vegetation Analysis Service',
      nameAr: 'خدمة تحليل الغطاء النباتي',
      baseUrl: EnvConfig.satelliteUrl,
      tier: ServiceTier.acquisition,
      endpoints: {
        'analyze': '/api/v1/satellite/analyze',
        'timeseries': '/api/v1/satellite/timeseries',
        'imagery': '/api/v1/satellite/imagery',
        'indices': '/api/v1/satellite/indices',
        'health': '/api/v1/satellite/health',
        'phenology': '/api/v1/satellite/phenology',
      },
    ));

    // Weather Service
    register(ServiceConfig(
      id: 'weather',
      name: 'Weather Service',
      nameAr: 'خدمة الطقس',
      baseUrl: EnvConfig.weatherUrl,
      tier: ServiceTier.acquisition,
      endpoints: {
        'current': '/api/v1/weather/current',
        'forecast': '/api/v1/weather/forecast',
        'alerts': '/api/v1/weather/alerts',
        'locations': '/api/v1/weather/locations',
        'agricultural-calendar': '/api/v1/weather/agricultural-calendar',
      },
    ));

    // Virtual Sensors Service
    register(ServiceConfig(
      id: 'virtual-sensors',
      name: 'Virtual Sensors Engine',
      nameAr: 'محرك المستشعرات الافتراضية',
      baseUrl: EnvConfig.virtualSensorsUrl,
      tier: ServiceTier.acquisition,
      endpoints: {
        'et0': '/api/v1/virtual-sensors/et0/calculate',
        'etc': '/api/v1/virtual-sensors/etc/calculate',
        'soil-moisture': '/api/v1/virtual-sensors/soil-moisture/estimate',
        'irrigation-recommend': '/api/v1/virtual-sensors/irrigation/recommend',
        'quick-check': '/api/v1/virtual-sensors/irrigation/quick-check',
      },
    ));

    // IoT Gateway
    register(ServiceConfig(
      id: 'iot-gateway',
      name: 'IoT Gateway',
      nameAr: 'بوابة إنترنت الأشياء',
      baseUrl: EnvConfig.gatewayUrl,
      tier: ServiceTier.acquisition,
      isRequired: false,
      endpoints: {
        'devices': '/api/v1/iot/devices',
        'readings': '/api/v1/iot/sensors',
        'device-types': '/api/v1/iot/device-types',
      },
    ));
  }

  /// Register Intelligence Layer Services
  /// تسجيل خدمات طبقة الذكاء
  void _registerIntelligenceServices() {
    // Indicators Service
    register(ServiceConfig(
      id: 'indicators',
      name: 'Indicators Service',
      nameAr: 'خدمة المؤشرات',
      baseUrl: EnvConfig.indicatorsUrl,
      tier: ServiceTier.intelligence,
      endpoints: {
        'definitions': '/api/v1/indicators/definitions',
        'field': '/api/v1/indicators/field',
        'dashboard': '/api/v1/indicators/dashboard',
        'alerts': '/api/v1/indicators/alerts',
        'trends': '/api/v1/indicators/trends',
      },
    ));

    // Crop Intelligence Service (was crop-health-ai)
    register(ServiceConfig(
      id: 'crop-intelligence',
      name: 'Crop Intelligence Service',
      nameAr: 'خدمة ذكاء المحاصيل',
      baseUrl: EnvConfig.cropHealthUrl,
      tier: ServiceTier.intelligence,
      endpoints: {
        'diagnose': '/api/v1/crop-health/diagnose',
        'diagnose-batch': '/api/v1/crop-health/diagnose/batch',
        'crops': '/api/v1/crop-health/crops',
        'diseases': '/api/v1/crop-health/diseases',
        'treatment': '/api/v1/crop-health/treatment',
        'expert-review': '/api/v1/crop-health/expert-review',
      },
    ));

    // NDVI Processor
    register(ServiceConfig(
      id: 'ndvi-processor',
      name: 'NDVI Processor',
      nameAr: 'معالج مؤشر الغطاء النباتي',
      baseUrl: EnvConfig.satelliteUrl,
      tier: ServiceTier.intelligence,
      endpoints: {
        'process': '/api/v1/ndvi/process',
        'timeseries': '/api/v1/ndvi/timeseries',
        'comparison': '/api/v1/ndvi/comparison',
      },
    ));
  }

  /// Register Decision Layer Services
  /// تسجيل خدمات طبقة القرار
  void _registerDecisionServices() {
    // Advisory Service (was fertilizer-advisor)
    register(ServiceConfig(
      id: 'advisory',
      name: 'Advisory Service',
      nameAr: 'خدمة الاستشارات',
      baseUrl: EnvConfig.fertilizerUrl,
      tier: ServiceTier.decision,
      endpoints: {
        'crops': '/api/v1/fertilizer/crops',
        'fertilizers': '/api/v1/fertilizer/fertilizers',
        'recommend': '/api/v1/fertilizer/recommend',
        'soil-interpret': '/api/v1/fertilizer/soil/interpret',
        'deficiency-symptoms': '/api/v1/fertilizer/deficiency/symptoms',
        'schedule': '/api/v1/fertilizer/schedule',
      },
    ));

    // Irrigation Smart Service
    register(ServiceConfig(
      id: 'irrigation',
      name: 'Smart Irrigation Service',
      nameAr: 'خدمة الري الذكي',
      baseUrl: EnvConfig.irrigationUrl,
      tier: ServiceTier.decision,
      endpoints: {
        'crops': '/api/v1/irrigation/crops',
        'methods': '/api/v1/irrigation/methods',
        'calculate': '/api/v1/irrigation/calculate',
        'water-balance': '/api/v1/irrigation/water-balance',
        'sensor-reading': '/api/v1/irrigation/sensor-reading',
        'efficiency': '/api/v1/irrigation/efficiency',
        'schedule': '/api/v1/irrigation/schedule',
      },
    ));

    // Yield Engine
    register(ServiceConfig(
      id: 'yield-engine',
      name: 'Yield Engine',
      nameAr: 'محرك الإنتاجية',
      baseUrl: EnvConfig.sprayUrl,
      tier: ServiceTier.decision,
      endpoints: {
        'predict': '/api/v1/yield/predict',
        'history': '/api/v1/yield/history',
        'factors': '/api/v1/yield/factors',
      },
    ));

    // AI Advisor
    register(ServiceConfig(
      id: 'ai-advisor',
      name: 'AI Advisor Service',
      nameAr: 'المستشار الذكي',
      baseUrl: EnvConfig.gatewayUrl,
      tier: ServiceTier.decision,
      isRequired: false,
      endpoints: {
        'query': '/api/v1/ai-advisor/query',
        'chat': '/api/v1/ai-advisor/chat',
        'diagnose': '/api/v1/ai-advisor/diagnose',
        'recommendations': '/api/v1/ai-advisor/recommendations',
        'analyze': '/api/v1/ai-advisor/analyze',
        'history': '/api/v1/ai-advisor/history',
      },
    ));
  }

  /// Register Business Layer Services
  /// تسجيل خدمات طبقة الأعمال
  void _registerBusinessServices() {
    // Field Management Service (consolidated field-core)
    register(ServiceConfig(
      id: 'field-management',
      name: 'Field Management Service',
      nameAr: 'خدمة إدارة الحقول',
      baseUrl: EnvConfig.fieldCoreUrl,
      tier: ServiceTier.business,
      endpoints: {
        'fields': '/api/v1/fields',
        'sync': '/api/v1/fields/sync',
        'batch': '/api/v1/fields/batch',
        'nearby': '/api/v1/fields/nearby',
        'tasks': '/api/v1/tasks',
      },
    ));

    // Notification Service
    register(ServiceConfig(
      id: 'notifications',
      name: 'Notification Service',
      nameAr: 'خدمة الإشعارات',
      baseUrl: EnvConfig.notificationsUrl,
      tier: ServiceTier.business,
      endpoints: {
        'list': '/api/v1/notifications',
        'preferences': '/api/v1/notifications/preferences',
        'subscribe': '/api/v1/notifications/subscribe',
        'unsubscribe': '/api/v1/notifications/unsubscribe',
        'mark-read': '/api/v1/notifications/mark-read',
      },
    ));

    // Billing Service
    register(ServiceConfig(
      id: 'billing',
      name: 'Billing Service',
      nameAr: 'خدمة الفوترة',
      baseUrl: EnvConfig.gatewayUrl,
      tier: ServiceTier.business,
      endpoints: {
        'wallet': '/api/v1/billing/wallet',
        'deposit': '/api/v1/billing/wallet/deposit',
        'withdraw': '/api/v1/billing/wallet/withdraw',
        'transfer': '/api/v1/billing/wallet/transfer',
        'transactions': '/api/v1/billing/transactions',
        'subscription': '/api/v1/billing/subscription',
        'plans': '/api/v1/billing/plans',
        'invoices': '/api/v1/billing/invoices',
        'usage': '/api/v1/billing/usage',
      },
    ));

    // Marketplace Service
    register(ServiceConfig(
      id: 'marketplace',
      name: 'Marketplace Service',
      nameAr: 'خدمة السوق',
      baseUrl: EnvConfig.marketplaceUrl,
      tier: ServiceTier.business,
      isRequired: false,
      endpoints: {
        'products': '/api/v1/marketplace/products',
        'harvest': '/api/v1/marketplace/harvest',
        'orders': '/api/v1/marketplace/orders',
        'wallet': '/api/v1/marketplace/fintech/wallet',
        'loans': '/api/v1/marketplace/fintech/loans',
        'credit-score': '/api/v1/marketplace/fintech/calculate-score',
      },
    ));

    // Equipment Service
    register(ServiceConfig(
      id: 'equipment',
      name: 'Equipment Service',
      nameAr: 'خدمة المعدات',
      baseUrl: EnvConfig.equipmentUrl,
      tier: ServiceTier.business,
      endpoints: {
        'list': '/api/v1/equipment',
        'stats': '/api/v1/equipment/stats',
        'maintenance': '/api/v1/equipment/maintenance',
        'alerts': '/api/v1/equipment/maintenance/alerts',
      },
    ));

    // Inventory Service
    register(ServiceConfig(
      id: 'inventory',
      name: 'Inventory Service',
      nameAr: 'خدمة المخزون',
      baseUrl: EnvConfig.inventoryUrl,
      tier: ServiceTier.business,
      endpoints: {
        'list': '/api/v1/inventory',
        'categories': '/api/v1/inventory/categories',
        'transactions': '/api/v1/inventory/transactions',
        'alerts': '/api/v1/inventory/alerts',
      },
    ));

    // Chat Service (consolidated from community-chat + field-chat)
    register(ServiceConfig(
      id: 'chat-service',
      name: 'Chat Service',
      nameAr: 'خدمة الدردشة',
      baseUrl: EnvConfig.chatUrl,
      tier: ServiceTier.business,
      isRequired: false,
      endpoints: {
        'conversations': '/api/v1/chat/conversations',
        'messages': '/api/v1/chat/messages',
        'unread-count': '/api/v1/chat/conversations/unread-count',
        // Community endpoints routed via Kong to chat-service
        'community-requests': '/api/v1/community/requests',
        'community-rooms': '/api/v1/community/rooms',
        'community-experts': '/api/v1/community/experts/online',
        'community-stats': '/api/v1/community/stats',
      },
    ));
  }

  /// Register Infrastructure Services
  /// تسجيل خدمات البنية التحتية
  void _registerInfrastructureServices() {
    // API Gateway (Kong)
    register(ServiceConfig(
      id: 'gateway',
      name: 'API Gateway',
      nameAr: 'بوابة API',
      baseUrl: EnvConfig.gatewayUrl,
      tier: ServiceTier.infrastructure,
      endpoints: {
        'health': '/health',
        'status': '/status',
      },
    ));

    // WebSocket Gateway
    register(ServiceConfig(
      id: 'ws-gateway',
      name: 'WebSocket Gateway',
      nameAr: 'بوابة WebSocket',
      baseUrl: EnvConfig.wsGatewayUrl,
      tier: ServiceTier.infrastructure,
      endpoints: {
        'connect': '/ws',
        'events': '/events',
      },
    ));

    // User Service
    register(ServiceConfig(
      id: 'user-service',
      name: 'User Service',
      nameAr: 'خدمة المستخدمين',
      baseUrl: EnvConfig.fieldCoreUrl,
      tier: ServiceTier.infrastructure,
      endpoints: {
        'login': '/api/v1/auth/login',
        'register': '/api/v1/auth/register',
        'refresh': '/api/v1/auth/refresh',
        'profile': '/api/v1/users/profile',
      },
    ));
  }

  /// Register a service
  /// تسجيل خدمة
  void register(ServiceConfig config) {
    _services[config.id] = config;
    _healthCache[config.id] = ServiceHealth(
      serviceId: config.id,
      status: ServiceStatus.unknown,
      lastCheck: DateTime.now(),
    );
    AppLogger.d(
      'Registered service: ${config.id} (${config.tier.name})',
      tag: 'ServiceRegistry',
    );
  }

  /// Unregister a service
  /// إلغاء تسجيل خدمة
  void unregister(String serviceId) {
    _services.remove(serviceId);
    _healthCache.remove(serviceId);
  }

  /// Get service configuration by ID
  /// الحصول على تكوين الخدمة بالمعرف
  ServiceConfig? getService(String serviceId) {
    return _services[serviceId];
  }

  /// Get service health by ID
  /// الحصول على صحة الخدمة بالمعرف
  ServiceHealth? getServiceHealth(String serviceId) {
    return _healthCache[serviceId];
  }

  /// Get services by tier
  /// الحصول على الخدمات حسب الطبقة
  List<ServiceConfig> getServicesByTier(ServiceTier tier) {
    return _services.values.where((s) => s.tier == tier).toList();
  }

  /// Get required services
  /// الحصول على الخدمات المطلوبة
  List<ServiceConfig> get requiredServices {
    return _services.values.where((s) => s.isRequired).toList();
  }

  /// Get optional services
  /// الحصول على الخدمات الاختيارية
  List<ServiceConfig> get optionalServices {
    return _services.values.where((s) => !s.isRequired).toList();
  }

  /// Update service health
  /// تحديث صحة الخدمة
  void updateHealth(String serviceId, ServiceHealth health) {
    _healthCache[serviceId] = health;
    _healthController.add(Map.from(_healthCache));
  }

  /// Check if all required services are healthy
  /// التحقق من صحة جميع الخدمات المطلوبة
  bool get allRequiredServicesHealthy {
    return requiredServices.every(
      (s) => _healthCache[s.id]?.isAvailable ?? false,
    );
  }

  /// Get overall system status
  /// الحصول على الحالة العامة للنظام
  ServiceStatus get overallStatus {
    final healthyCount = _healthCache.values.where((h) => h.isHealthy).length;
    final totalRequired = requiredServices.length;
    final healthyRequired = requiredServices
        .where((s) => _healthCache[s.id]?.isHealthy ?? false)
        .length;

    if (healthyRequired == totalRequired) {
      return healthyCount == _services.length
          ? ServiceStatus.healthy
          : ServiceStatus.degraded;
    }

    if (healthyRequired == 0) {
      return ServiceStatus.offline;
    }

    return ServiceStatus.unhealthy;
  }

  /// Get endpoint URL for a service
  /// الحصول على رابط نقطة النهاية للخدمة
  String? getEndpoint(String serviceId, String endpointKey) {
    final service = _services[serviceId];
    if (service == null) return null;

    final endpoint = service.endpoints[endpointKey];
    if (endpoint == null) return null;

    return '${service.baseUrl}$endpoint';
  }

  /// Dispose resources
  void dispose() {
    _healthController.close();
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Riverpod Providers
// ═══════════════════════════════════════════════════════════════════════════════

/// Service Registry Provider
final serviceRegistryProvider = Provider<ServiceRegistry>((ref) {
  final registry = ServiceRegistry();
  ref.onDispose(() => registry.dispose());
  return registry;
});

/// Service Health Stream Provider
final serviceHealthStreamProvider =
    StreamProvider<Map<String, ServiceHealth>>((ref) {
  final registry = ref.watch(serviceRegistryProvider);
  return registry.healthStream;
});

/// Overall System Status Provider
final systemStatusProvider = Provider<ServiceStatus>((ref) {
  ref.watch(serviceHealthStreamProvider);
  return ref.watch(serviceRegistryProvider).overallStatus;
});

/// Services by Tier Provider
final servicesByTierProvider =
    Provider.family<List<ServiceConfig>, ServiceTier>((ref, tier) {
  return ref.watch(serviceRegistryProvider).getServicesByTier(tier);
});

/// Service Config Provider
final serviceConfigProvider =
    Provider.family<ServiceConfig?, String>((ref, serviceId) {
  return ref.watch(serviceRegistryProvider).getService(serviceId);
});

/// Service Health Provider
final serviceHealthProvider =
    Provider.family<ServiceHealth?, String>((ref, serviceId) {
  ref.watch(serviceHealthStreamProvider);
  return ref.watch(serviceRegistryProvider).getServiceHealth(serviceId);
});
