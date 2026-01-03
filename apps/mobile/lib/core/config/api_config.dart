/// API Configuration for SAHOOL Field App
/// إعدادات الاتصال بالخادم
library;

import 'env_config.dart';

/// Service ports for local development
/// منافذ الخدمات للتطوير المحلي
/// @deprecated Use EnvConfig.{serviceName}Port instead
class ServicePorts {
  static int get fieldCore => EnvConfig.fieldCorePort;
  static int get marketplace => EnvConfig.marketplacePort;
  static int get chat => EnvConfig.chatPort;
  static int get satellite => EnvConfig.satellitePort;
  static int get indicators => EnvConfig.indicatorsPort;
  static int get weather => EnvConfig.weatherPort;
  static int get fertilizer => EnvConfig.fertilizerPort;
  static int get irrigation => EnvConfig.irrigationPort;
  static int get cropHealth => EnvConfig.cropHealthPort;
  static int get virtualSensors => EnvConfig.virtualSensorsPort;
  static int get communityChat => EnvConfig.communityChatPort;
  static int get equipment => EnvConfig.equipmentPort;
  static int get inventory => EnvConfig.inventoryPort;
  static int get notifications => EnvConfig.notificationsPort;
  static int get spray => EnvConfig.sprayPort;
  static int get gateway => EnvConfig.gatewayPort;
}

/// API configuration class
/// Uses EnvConfig for all environment-specific values
class ApiConfig {
  ApiConfig._();

  /// Check if running in release mode
  static bool get isProduction => EnvConfig.isProduction;

  /// Get protocol (https for production, http for development)
  static String get _protocol => EnvConfig.apiProtocol;

  /// Get host based on environment
  static String get _host => EnvConfig.apiHost;

  /// Base URL for field-core service (legacy)
  static String get baseUrl => EnvConfig.fieldCoreUrl;

  /// Gateway URL (production-like routing)
  static String get gatewayUrl => EnvConfig.gatewayUrl;

  /// Service-specific URLs for direct access
  static String get satelliteServiceUrl => EnvConfig.satelliteUrl;
  static String get indicatorsServiceUrl => EnvConfig.indicatorsUrl;
  static String get weatherServiceUrl => EnvConfig.weatherUrl;
  static String get fertilizerServiceUrl => EnvConfig.fertilizerUrl;
  static String get irrigationServiceUrl => EnvConfig.irrigationUrl;
  static String get cropHealthServiceUrl => EnvConfig.cropHealthUrl;
  static String get virtualSensorsServiceUrl => EnvConfig.virtualSensorsUrl;
  static String get communityChatServiceUrl => EnvConfig.communityChatUrl;
  static String get chatServiceUrl => EnvConfig.chatUrl;
  static String get equipmentServiceUrl => EnvConfig.equipmentUrl;
  static String get inventoryServiceUrl => EnvConfig.inventoryUrl;
  static String get notificationsServiceUrl => EnvConfig.notificationsUrl;
  static String get sprayServiceUrl => EnvConfig.sprayUrl;
  static String get marketplaceServiceUrl => EnvConfig.marketplaceUrl;

  /// Production base URL (Kong Gateway)
  /// @deprecated Use EnvConfig.gatewayUrl instead
  static String get productionBaseUrl => 'https://${EnvConfig.productionHost}';

  /// Use production URL in release mode
  static String get effectiveBaseUrl => gatewayUrl;

  /// Use direct service URLs in development (bypass gateway)
  /// Set to false to use the unified gateway (mock-server on port 8000)
  static const bool useDirectServices = false;

  // ─────────────────────────────────────────────────────────────────────────────
  // Field Core Endpoints (port 3000)
  // ─────────────────────────────────────────────────────────────────────────────

  /// Fields endpoints
  static String get fields => '$baseUrl/api/v1/fields';
  static String fieldById(String id) => '$baseUrl/api/v1/fields/$id';
  static String get fieldsSync => '$baseUrl/api/v1/fields/sync';
  static String get fieldsBatch => '$baseUrl/api/v1/fields/batch';
  static String get fieldsNearby => '$baseUrl/api/v1/fields/nearby';

  /// Tasks endpoints
  static String get tasks => '$baseUrl/api/v1/tasks';
  static String taskById(String id) => '$baseUrl/api/v1/tasks/$id';

  /// Community endpoints
  static String get posts => '$baseUrl/api/v1/posts';
  static String get stories => '$baseUrl/api/v1/stories';
  static String get experts => '$baseUrl/api/v1/experts';

  /// Provider config endpoints
  static String get providers => '$baseUrl/api/v1/providers';
  static String get providerConfig => '$baseUrl/api/v1/config';

  /// Auth endpoints
  static String get login => '$baseUrl/api/v1/auth/login';
  static String get register => '$baseUrl/api/v1/auth/register';
  static String get refreshToken => '$baseUrl/api/v1/auth/refresh';

  // ─────────────────────────────────────────────────────────────────────────────
  // Satellite Service Endpoints (port 8090)
  // خدمة الأقمار الصناعية
  // ─────────────────────────────────────────────────────────────────────────────

  static String get _satelliteBase => useDirectServices ? satelliteServiceUrl : effectiveBaseUrl;

  /// NDVI analysis endpoints
  static String get ndvi => '$_satelliteBase/v1/analyze';
  static String ndviByFieldId(String fieldId) => '$_satelliteBase/v1/analyze/$fieldId';
  static String get ndviTimeseries => '$_satelliteBase/v1/timeseries';
  static String ndviTimeseriesByFieldId(String fieldId) => '$_satelliteBase/v1/timeseries/$fieldId';
  static String get satellites => '$_satelliteBase/v1/satellites';
  static String get regions => '$_satelliteBase/v1/regions';
  static String get imagery => '$_satelliteBase/v1/imagery';
  static String imageryByFieldId(String fieldId) => '$_satelliteBase/v1/imagery/$fieldId';

  /// Vegetation indices endpoints
  static String get indices => '$_satelliteBase/v1/indices';
  static String indicesByFieldId(String fieldId) => '$_satelliteBase/v1/indices/$fieldId';

  /// Field health endpoints
  static String get fieldHealth => '$_satelliteBase/v1/health';
  static String fieldHealthByFieldId(String fieldId) => '$_satelliteBase/v1/health/$fieldId';

  /// Phenology endpoints
  static String get phenology => '$_satelliteBase/v1/phenology';
  static String phenologyByFieldId(String fieldId) => '$_satelliteBase/v1/phenology/$fieldId';

  // ─────────────────────────────────────────────────────────────────────────────
  // Weather Service Endpoints (port 8092)
  // خدمة الطقس
  // ─────────────────────────────────────────────────────────────────────────────

  static String get _weatherBase => useDirectServices ? weatherServiceUrl : effectiveBaseUrl;

  /// Weather endpoints
  static String get weather => '$_weatherBase/v1/current';
  static String weatherByLocation(String location) => '$_weatherBase/v1/current/$location';
  static String get forecast => '$_weatherBase/v1/forecast';
  static String forecastByLocation(String location) => '$_weatherBase/v1/forecast/$location';
  static String forecastByFieldId(String fieldId) => '$_weatherBase/v1/forecast/field/$fieldId';
  static String get weatherAlerts => '$_weatherBase/v1/alerts';
  static String weatherAlertsByLocation(String location) => '$_weatherBase/v1/alerts/$location';
  static String weatherAlertsByFieldId(String fieldId) => '$_weatherBase/v1/alerts/field/$fieldId';
  static String get weatherLocations => '$_weatherBase/v1/locations';
  static String get agriculturalCalendar => '$_weatherBase/v1/agricultural-calendar';

  // ─────────────────────────────────────────────────────────────────────────────
  // Indicators Service Endpoints (port 8091)
  // خدمة المؤشرات
  // ─────────────────────────────────────────────────────────────────────────────

  static String get _indicatorsBase => useDirectServices ? indicatorsServiceUrl : effectiveBaseUrl;

  /// Indicators endpoints
  static String get indicatorDefinitions => '$_indicatorsBase/v1/indicators/definitions';
  static String indicatorsByField(String fieldId) => '$_indicatorsBase/v1/indicators/field/$fieldId';
  static String get dashboard => '$_indicatorsBase/v1/dashboard';
  static String dashboardByTenant(String tenantId) => '$_indicatorsBase/v1/dashboard/$tenantId';
  static String get indicatorAlerts => '$_indicatorsBase/v1/alerts';
  static String get indicatorTrends => '$_indicatorsBase/v1/trends';

  // ─────────────────────────────────────────────────────────────────────────────
  // Fertilizer Advisor Endpoints (port 8093)
  // مستشار التسميد
  // ─────────────────────────────────────────────────────────────────────────────

  static String get _fertilizerBase => useDirectServices ? fertilizerServiceUrl : effectiveBaseUrl;

  /// Fertilizer recommendation endpoints
  static String get fertilizerCrops => '$_fertilizerBase/v1/crops';
  static String get fertilizerTypes => '$_fertilizerBase/v1/fertilizers';
  static String get fertilizerRecommendation => '$_fertilizerBase/v1/recommend';
  static String get soilInterpretation => '$_fertilizerBase/v1/soil/interpret';
  static String get deficiencySymptoms => '$_fertilizerBase/v1/deficiency/symptoms';
  static String get applicationSchedule => '$_fertilizerBase/v1/schedule';

  // ─────────────────────────────────────────────────────────────────────────────
  // Irrigation Smart Endpoints (port 8094)
  // الري الذكي
  // ─────────────────────────────────────────────────────────────────────────────

  static String get _irrigationBase => useDirectServices ? irrigationServiceUrl : effectiveBaseUrl;

  /// Irrigation planning endpoints
  static String get irrigationCrops => '$_irrigationBase/v1/crops';
  static String get irrigationMethods => '$_irrigationBase/v1/methods';
  static String get irrigationCalculate => '$_irrigationBase/v1/calculate';
  static String get waterBalance => '$_irrigationBase/v1/water-balance';
  static String get sensorReading => '$_irrigationBase/v1/sensor-reading';
  static String get irrigationEfficiency => '$_irrigationBase/v1/efficiency';
  static String get irrigationSchedule => '$_irrigationBase/v1/schedule';

  // ─────────────────────────────────────────────────────────────────────────────
  // Crop Health AI Service Endpoints (port 8095)
  // سهول فيجن - الذكاء الاصطناعي لصحة المحاصيل
  // ─────────────────────────────────────────────────────────────────────────────

  static String get _cropHealthBase => useDirectServices ? cropHealthServiceUrl : effectiveBaseUrl;

  /// Crop health AI diagnosis endpoints
  static String get diagnose => '$_cropHealthBase/v1/diagnose';
  static String get diagnoseBatch => '$_cropHealthBase/v1/diagnose/batch';
  static String get supportedCrops => '$_cropHealthBase/v1/crops';
  static String get diseases => '$_cropHealthBase/v1/diseases';
  static String treatmentDetails(String diseaseId) => '$_cropHealthBase/v1/treatment/$diseaseId';
  static String get expertReview => '$_cropHealthBase/v1/expert-review';
  static String get cropHealthHealthz => '$_cropHealthBase/healthz';

  // ─────────────────────────────────────────────────────────────────────────────
  // Virtual Sensors Engine Endpoints (port 8096)
  // محرك المستشعرات الافتراضية
  // ─────────────────────────────────────────────────────────────────────────────

  static String get _virtualSensorsBase => useDirectServices ? virtualSensorsServiceUrl : effectiveBaseUrl;

  /// Virtual sensors endpoints
  static String get et0Calculate => '$_virtualSensorsBase/v1/et0/calculate';
  static String get virtualSensorsCrops => '$_virtualSensorsBase/v1/crops';
  static String cropKc(String cropType) => '$_virtualSensorsBase/v1/crops/$cropType/kc';
  static String get etcCalculate => '$_virtualSensorsBase/v1/etc/calculate';
  static String get virtualSensorsSoils => '$_virtualSensorsBase/v1/soils';
  static String get soilMoistureEstimate => '$_virtualSensorsBase/v1/soil-moisture/estimate';
  static String get irrigationMethodsInfo => '$_virtualSensorsBase/v1/irrigation-methods';
  static String get irrigationRecommend => '$_virtualSensorsBase/v1/irrigation/recommend';
  static String get irrigationQuickCheck => '$_virtualSensorsBase/v1/irrigation/quick-check';
  static String get virtualSensorsHealthz => '$_virtualSensorsBase/healthz';

  // ─────────────────────────────────────────────────────────────────────────────
  // Equipment Service Endpoints (port 8101)
  // خدمة المعدات
  // ─────────────────────────────────────────────────────────────────────────────

  static String get _equipmentBase => useDirectServices ? equipmentServiceUrl : effectiveBaseUrl;

  /// Equipment endpoints
  static String get equipment => '$_equipmentBase/api/v1/equipment';
  static String equipmentById(String id) => '$_equipmentBase/api/v1/equipment/$id';
  static String equipmentByQr(String qrCode) => '$_equipmentBase/api/v1/equipment/qr/$qrCode';
  static String get equipmentStats => '$_equipmentBase/api/v1/equipment/stats';
  static String get maintenanceAlerts => '$_equipmentBase/api/v1/maintenance/alerts';
  static String maintenanceByEquipment(String id) => '$_equipmentBase/api/v1/maintenance/$id';

  // ─────────────────────────────────────────────────────────────────────────────
  // Timeouts Configuration
  // ─────────────────────────────────────────────────────────────────────────────

  /// Connection timeout for areas with poor connectivity
  static const Duration connectTimeout = Duration(seconds: 30);

  /// Send timeout
  static const Duration sendTimeout = Duration(seconds: 15);

  /// Receive timeout
  static const Duration receiveTimeout = Duration(seconds: 15);

  /// Long operation timeout (for satellite imagery, large uploads)
  static const Duration longOperationTimeout = Duration(seconds: 60);

  // ─────────────────────────────────────────────────────────────────────────────
  // Headers
  // ─────────────────────────────────────────────────────────────────────────────

  /// Default headers for API requests
  static Map<String, String> get defaultHeaders => {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Accept-Language': 'ar,en',
  };

  /// Get headers with authorization token
  static Map<String, String> authHeaders(String token) => {
    ...defaultHeaders,
    'Authorization': 'Bearer $token',
  };

  /// Get headers with tenant ID for multi-tenancy
  static Map<String, String> tenantHeaders(String token, String tenantId) => {
    ...authHeaders(token),
    'X-Tenant-Id': tenantId,
  };

  /// Get headers with ETag for optimistic locking
  static Map<String, String> etagHeaders(String token, String etag) => {
    ...authHeaders(token),
    'If-Match': etag,
  };

  // ─────────────────────────────────────────────────────────────────────────────
  // Health Check Endpoints
  // ─────────────────────────────────────────────────────────────────────────────

  /// Get health check URL for a service
  static String healthCheck(String serviceUrl) => '$serviceUrl/healthz';

  /// Check all services health
  static Map<String, String> get allHealthChecks => {
    'satellite': healthCheck(satelliteServiceUrl),
    'indicators': healthCheck(indicatorsServiceUrl),
    'weather': healthCheck(weatherServiceUrl),
    'fertilizer': healthCheck(fertilizerServiceUrl),
    'irrigation': healthCheck(irrigationServiceUrl),
    'cropHealth': healthCheck(cropHealthServiceUrl),
    'virtualSensors': healthCheck(virtualSensorsServiceUrl),
    'communityChat': healthCheck(communityChatServiceUrl),
    'chat': healthCheck(chatServiceUrl),
    'equipment': healthCheck(equipmentServiceUrl),
    'inventory': healthCheck(inventoryServiceUrl),
    'notifications': healthCheck(notificationsServiceUrl),
    'spray': healthCheck(sprayServiceUrl),
    'marketplace': healthCheck(marketplaceServiceUrl),
  };

  // ─────────────────────────────────────────────────────────────────────────────
  // Community Chat Service Endpoints (port 8097)
  // خدمة الدردشة المجتمعية
  // ─────────────────────────────────────────────────────────────────────────────

  static String get _chatBase => useDirectServices ? communityChatServiceUrl : effectiveBaseUrl;

  /// Community chat endpoints
  static String get chatUrl => communityChatServiceUrl; // Socket.io URL
  static String get chatRequests => '$_chatBase/v1/requests';
  static String chatRoomMessages(String roomId) => '$_chatBase/v1/rooms/$roomId/messages';
  static String get chatOnlineExperts => '$_chatBase/v1/experts/online';
  static String get chatStats => '$_chatBase/v1/stats';
  static String get chatHealthz => '$_chatBase/healthz';

  // ─────────────────────────────────────────────────────────────────────────────
  // Notification Service Endpoints (port 8110)
  // خدمة الإشعارات
  // ─────────────────────────────────────────────────────────────────────────────

  static String get _notificationsBase => useDirectServices ? notificationsServiceUrl : effectiveBaseUrl;

  /// Notification service endpoints
  static String get notifications => '$_notificationsBase/v1/notifications';
  static String notificationById(String id) => '$_notificationsBase/v1/notifications/$id';
  static String get notificationPreferences => '$_notificationsBase/v1/preferences';
  static String get notificationSubscribe => '$_notificationsBase/v1/subscribe';
  static String get notificationUnsubscribe => '$_notificationsBase/v1/unsubscribe';
  static String get notificationMarkRead => '$_notificationsBase/v1/notifications/mark-read';
  static String get notificationsHealthz => '$_notificationsBase/healthz';

  // ─────────────────────────────────────────────────────────────────────────────
  // Marketplace & FinTech Service Endpoints (port 3010)
  // خدمة السوق والمحفظة المالية
  // ─────────────────────────────────────────────────────────────────────────────

  static String get _marketplaceBase => useDirectServices ? marketplaceServiceUrl : effectiveBaseUrl;

  /// Wallet endpoints - نقاط المحفظة
  static String wallet(String userId) => '$_marketplaceBase/api/v1/fintech/wallet/$userId';
  static String walletDeposit(String walletId) => '$_marketplaceBase/api/v1/fintech/wallet/$walletId/deposit';
  static String walletWithdraw(String walletId) => '$_marketplaceBase/api/v1/fintech/wallet/$walletId/withdraw';
  static String walletTransactions(String walletId) => '$_marketplaceBase/api/v1/fintech/wallet/$walletId/transactions';

  /// Credit & Loans endpoints - نقاط الائتمان والقروض
  static String get calculateCreditScore => '$_marketplaceBase/api/v1/fintech/calculate-score';
  static String get loans => '$_marketplaceBase/api/v1/fintech/loans';
  static String userLoans(String walletId) => '$_marketplaceBase/api/v1/fintech/loans/$walletId';
  static String repayLoan(String loanId) => '$_marketplaceBase/api/v1/fintech/loans/$loanId/repay';

  /// Market endpoints - نقاط السوق
  static String get marketProducts => '$_marketplaceBase/api/v1/market/products';
  static String marketProductById(String productId) => '$_marketplaceBase/api/v1/market/products/$productId';
  static String get listHarvest => '$_marketplaceBase/api/v1/market/harvest';
  static String get marketOrders => '$_marketplaceBase/api/v1/market/orders';
  static String userMarketOrders(String userId) => '$_marketplaceBase/api/v1/market/orders/user/$userId';
  static String get marketStats => '$_marketplaceBase/api/v1/market/stats';
  static String get marketplaceHealthz => '$_marketplaceBase/healthz';

  // ─────────────────────────────────────────────────────────────────────────────
  // Chat/Messaging Service Endpoints (port 3011)
  // خدمة المحادثات والرسائل
  // ─────────────────────────────────────────────────────────────────────────────

  static String get _chatBase => useDirectServices ? chatServiceUrl : effectiveBaseUrl;

  /// Chat REST endpoints
  static String get chatConversations => '$_chatBase/api/v1/conversations';
  static String chatConversationById(String id) => '$_chatBase/api/v1/conversations/$id';
  static String chatMessages(String conversationId) => '$_chatBase/api/v1/conversations/$conversationId/messages';
  static String chatSendMessage(String conversationId) => '$_chatBase/api/v1/conversations/$conversationId/messages';
  static String chatMarkRead(String conversationId) => '$_chatBase/api/v1/conversations/$conversationId/read';
  static String get chatCreateConversation => '$_chatBase/api/v1/conversations';
  static String get chatUnreadCount => '$_chatBase/api/v1/conversations/unread-count';
  static String get chatHealthz => '$_chatBase/healthz';

  /// Chat Socket.io URL
  static String get chatSocketUrl => chatServiceUrl;
}
