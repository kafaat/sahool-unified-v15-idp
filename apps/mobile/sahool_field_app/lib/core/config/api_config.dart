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
  // Kong route: /api/v1/satellite
  // ─────────────────────────────────────────────────────────────────────────────

  static String get _satelliteBase => useDirectServices ? satelliteServiceUrl : '$effectiveBaseUrl/api/v1/satellite';

  /// NDVI analysis endpoints
  static String get ndvi => '$_satelliteBase/analyze';
  static String ndviByFieldId(String fieldId) => '$_satelliteBase/analyze/$fieldId';
  static String get ndviTimeseries => '$_satelliteBase/timeseries';
  static String ndviTimeseriesByFieldId(String fieldId) => '$_satelliteBase/timeseries/$fieldId';
  static String get satellites => '$_satelliteBase/satellites';
  static String get regions => '$_satelliteBase/regions';
  static String get imagery => '$_satelliteBase/imagery';
  static String imageryByFieldId(String fieldId) => '$_satelliteBase/imagery/$fieldId';

  /// Vegetation indices endpoints
  static String get indices => '$_satelliteBase/indices';
  static String indicesByFieldId(String fieldId) => '$_satelliteBase/indices/$fieldId';

  /// Field health endpoints
  static String get fieldHealth => '$_satelliteBase/health';
  static String fieldHealthByFieldId(String fieldId) => '$_satelliteBase/health/$fieldId';

  /// Phenology endpoints
  static String get phenology => '$_satelliteBase/phenology';
  static String phenologyByFieldId(String fieldId) => '$_satelliteBase/phenology/$fieldId';

  // ─────────────────────────────────────────────────────────────────────────────
  // Weather Service Endpoints (port 8092)
  // خدمة الطقس
  // Kong route: /api/v1/weather
  // ─────────────────────────────────────────────────────────────────────────────

  static String get _weatherBase => useDirectServices ? weatherServiceUrl : '$effectiveBaseUrl/api/v1/weather';

  /// Weather endpoints
  static String get weather => '$_weatherBase/current';
  static String weatherByLocation(String location) => '$_weatherBase/current/$location';
  static String get forecast => '$_weatherBase/forecast';
  static String forecastByLocation(String location) => '$_weatherBase/forecast/$location';
  static String forecastByFieldId(String fieldId) => '$_weatherBase/forecast/field/$fieldId';
  static String get weatherAlerts => '$_weatherBase/alerts';
  static String weatherAlertsByLocation(String location) => '$_weatherBase/alerts/$location';
  static String weatherAlertsByFieldId(String fieldId) => '$_weatherBase/alerts/field/$fieldId';
  static String get weatherLocations => '$_weatherBase/locations';
  static String get agriculturalCalendar => '$_weatherBase/agricultural-calendar';

  // ─────────────────────────────────────────────────────────────────────────────
  // Indicators Service Endpoints (port 8091)
  // خدمة المؤشرات
  // Kong route: /api/v1/indicators
  // ─────────────────────────────────────────────────────────────────────────────

  static String get _indicatorsBase => useDirectServices ? indicatorsServiceUrl : '$effectiveBaseUrl/api/v1/indicators';

  /// Indicators endpoints
  static String get indicatorDefinitions => '$_indicatorsBase/definitions';
  static String indicatorsByField(String fieldId) => '$_indicatorsBase/field/$fieldId';
  static String get dashboard => '$_indicatorsBase/dashboard';
  static String dashboardByTenant(String tenantId) => '$_indicatorsBase/dashboard/$tenantId';
  static String get indicatorAlerts => '$_indicatorsBase/alerts';
  static String get indicatorTrends => '$_indicatorsBase/trends';

  // ─────────────────────────────────────────────────────────────────────────────
  // Fertilizer Advisor Endpoints (port 8093)
  // مستشار التسميد
  // Kong route: /api/v1/fertilizer
  // ─────────────────────────────────────────────────────────────────────────────

  static String get _fertilizerBase => useDirectServices ? fertilizerServiceUrl : '$effectiveBaseUrl/api/v1/fertilizer';

  /// Fertilizer recommendation endpoints
  static String get fertilizerCrops => '$_fertilizerBase/crops';
  static String get fertilizerTypes => '$_fertilizerBase/fertilizers';
  static String get fertilizerRecommendation => '$_fertilizerBase/recommend';
  static String get soilInterpretation => '$_fertilizerBase/soil/interpret';
  static String get deficiencySymptoms => '$_fertilizerBase/deficiency/symptoms';
  static String get applicationSchedule => '$_fertilizerBase/schedule';

  // ─────────────────────────────────────────────────────────────────────────────
  // Irrigation Smart Endpoints (port 8094)
  // الري الذكي
  // Kong route: /api/v1/irrigation
  // ─────────────────────────────────────────────────────────────────────────────

  static String get _irrigationBase => useDirectServices ? irrigationServiceUrl : '$effectiveBaseUrl/api/v1/irrigation';

  /// Irrigation planning endpoints
  static String get irrigationCrops => '$_irrigationBase/crops';
  static String get irrigationMethods => '$_irrigationBase/methods';
  static String get irrigationCalculate => '$_irrigationBase/calculate';
  static String get waterBalance => '$_irrigationBase/water-balance';
  static String get sensorReading => '$_irrigationBase/sensor-reading';
  static String get irrigationEfficiency => '$_irrigationBase/efficiency';
  static String get irrigationSchedule => '$_irrigationBase/schedule';

  // ─────────────────────────────────────────────────────────────────────────────
  // Crop Health AI Service Endpoints (port 8095)
  // سهول فيجن - الذكاء الاصطناعي لصحة المحاصيل
  // Kong route: /api/v1/crop-health
  // ─────────────────────────────────────────────────────────────────────────────

  static String get _cropHealthBase => useDirectServices ? cropHealthServiceUrl : '$effectiveBaseUrl/api/v1/crop-health';

  /// Crop health AI diagnosis endpoints
  static String get diagnose => '$_cropHealthBase/diagnose';
  static String get diagnoseBatch => '$_cropHealthBase/diagnose/batch';
  static String get supportedCrops => '$_cropHealthBase/crops';
  static String get diseases => '$_cropHealthBase/diseases';
  static String treatmentDetails(String diseaseId) => '$_cropHealthBase/treatment/$diseaseId';
  static String get expertReview => '$_cropHealthBase/expert-review';
  static String get cropHealthHealthz => '$_cropHealthBase/healthz';

  // ─────────────────────────────────────────────────────────────────────────────
  // Virtual Sensors Engine Endpoints (port 8096)
  // محرك المستشعرات الافتراضية
  // Kong route: /api/v1/sensors/virtual
  // ─────────────────────────────────────────────────────────────────────────────

  static String get _virtualSensorsBase => useDirectServices ? virtualSensorsServiceUrl : '$effectiveBaseUrl/api/v1/virtual-sensors';

  /// Virtual sensors endpoints
  static String get et0Calculate => '$_virtualSensorsBase/et0/calculate';
  static String get virtualSensorsCrops => '$_virtualSensorsBase/crops';
  static String cropKc(String cropType) => '$_virtualSensorsBase/crops/$cropType/kc';
  static String get etcCalculate => '$_virtualSensorsBase/etc/calculate';
  static String get virtualSensorsSoils => '$_virtualSensorsBase/soils';
  static String get soilMoistureEstimate => '$_virtualSensorsBase/soil-moisture/estimate';
  static String get irrigationMethodsInfo => '$_virtualSensorsBase/irrigation-methods';
  static String get irrigationRecommend => '$_virtualSensorsBase/irrigation/recommend';
  static String get irrigationQuickCheck => '$_virtualSensorsBase/irrigation/quick-check';
  static String get virtualSensorsHealthz => '$_virtualSensorsBase/healthz';

  // ─────────────────────────────────────────────────────────────────────────────
  // Equipment Service Endpoints (port 8101)
  // خدمة المعدات
  // Kong route: /api/v1/equipment
  // ─────────────────────────────────────────────────────────────────────────────

  static String get _equipmentBase => useDirectServices ? equipmentServiceUrl : '$effectiveBaseUrl/api/v1/equipment';

  /// Equipment endpoints
  static String get equipment => _equipmentBase;
  static String equipmentById(String id) => '$_equipmentBase/$id';
  static String equipmentByQr(String qrCode) => '$_equipmentBase/qr/$qrCode';
  static String get equipmentStats => '$_equipmentBase/stats';
  static String get maintenanceAlerts => '$_equipmentBase/maintenance/alerts';
  static String maintenanceByEquipment(String id) => '$_equipmentBase/maintenance/$id';

  // ─────────────────────────────────────────────────────────────────────────────
  // IoT Gateway Endpoints (port 8106)
  // بوابة إنترنت الأشياء
  // Kong route: /api/v1/iot
  // ─────────────────────────────────────────────────────────────────────────────

  static String get _iotBase => '$effectiveBaseUrl/api/v1/iot';

  /// IoT Gateway endpoints
  static String get iotDevices => '$_iotBase/devices';
  static String iotDeviceById(String id) => '$_iotBase/devices/$id';
  static String iotDevicesByField(String fieldId) => '$_iotBase/devices/field/$fieldId';
  static String iotSensorReadings(String deviceId) => '$_iotBase/sensors/$deviceId/readings';
  static String iotDeviceCommand(String deviceId) => '$_iotBase/devices/$deviceId/command';
  static String get iotDeviceTypes => '$_iotBase/device-types';
  static String get iotHealthz => '$_iotBase/healthz';

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
  // Kong route: /api/v1/community/chat
  // ─────────────────────────────────────────────────────────────────────────────

  static String get _communityChatBase => useDirectServices ? communityChatServiceUrl : '$effectiveBaseUrl/api/v1/community';

  /// Community chat endpoints
  static String get communityChatUrl => communityChatServiceUrl; // Socket.io URL
  static String get communityChatRequests => '$_communityChatBase/requests';
  static String communityChatRoomMessages(String roomId) => '$_communityChatBase/rooms/$roomId/messages';
  static String get communityChatOnlineExperts => '$_communityChatBase/experts/online';
  static String get communityChatStats => '$_communityChatBase/stats';
  static String get communityChatHealthz => '$_communityChatBase/healthz';

  // ─────────────────────────────────────────────────────────────────────────────
  // Notification Service Endpoints (port 8110)
  // خدمة الإشعارات
  // Kong route: /api/v1/notifications
  // ─────────────────────────────────────────────────────────────────────────────

  static String get _notificationsBase => useDirectServices ? notificationsServiceUrl : '$effectiveBaseUrl/api/v1/notifications';

  /// Notification service endpoints
  static String get notifications => _notificationsBase;
  static String notificationById(String id) => '$_notificationsBase/$id';
  static String get notificationPreferences => '$_notificationsBase/preferences';
  static String get notificationSubscribe => '$_notificationsBase/subscribe';
  static String get notificationUnsubscribe => '$_notificationsBase/unsubscribe';
  static String get notificationMarkRead => '$_notificationsBase/mark-read';
  static String get notificationsHealthz => '$_notificationsBase/healthz';

  // ─────────────────────────────────────────────────────────────────────────────
  // Marketplace & FinTech Service Endpoints (port 3010)
  // خدمة السوق والمحفظة المالية
  // Kong route: /api/v1/marketplace
  // ─────────────────────────────────────────────────────────────────────────────

  static String get _marketplaceBase => useDirectServices ? marketplaceServiceUrl : '$effectiveBaseUrl/api/v1/marketplace';

  /// Wallet endpoints - نقاط المحفظة
  static String wallet(String userId) => '$_marketplaceBase/fintech/wallet/$userId';
  static String walletDeposit(String walletId) => '$_marketplaceBase/fintech/wallet/$walletId/deposit';
  static String walletWithdraw(String walletId) => '$_marketplaceBase/fintech/wallet/$walletId/withdraw';
  static String walletTransactions(String walletId) => '$_marketplaceBase/fintech/wallet/$walletId/transactions';

  /// Credit & Loans endpoints - نقاط الائتمان والقروض
  static String get calculateCreditScore => '$_marketplaceBase/fintech/calculate-score';
  static String get loans => '$_marketplaceBase/fintech/loans';
  static String userLoans(String walletId) => '$_marketplaceBase/fintech/loans/$walletId';
  static String repayLoan(String loanId) => '$_marketplaceBase/fintech/loans/$loanId/repay';

  /// Market endpoints - نقاط السوق
  static String get marketProducts => '$_marketplaceBase/products';
  static String marketProductById(String productId) => '$_marketplaceBase/products/$productId';
  static String get listHarvest => '$_marketplaceBase/harvest';
  static String get marketOrders => '$_marketplaceBase/orders';
  static String userMarketOrders(String userId) => '$_marketplaceBase/orders/user/$userId';
  static String get marketStats => '$_marketplaceBase/stats';
  static String get marketplaceHealthz => '$_marketplaceBase/healthz';

  // ─────────────────────────────────────────────────────────────────────────────
  // Chat/Messaging Service Endpoints (port 3011)
  // خدمة المحادثات والرسائل
  // Kong route: /api/v1/chat
  // ─────────────────────────────────────────────────────────────────────────────

  static String get _chatMessagingBase => useDirectServices ? chatServiceUrl : '$effectiveBaseUrl/api/v1/chat';

  /// Chat REST endpoints
  static String get chatConversations => '$_chatMessagingBase/conversations';
  static String chatConversationById(String id) => '$_chatMessagingBase/conversations/$id';
  static String chatMessages(String conversationId) => '$_chatMessagingBase/conversations/$conversationId/messages';
  static String chatSendMessage(String conversationId) => '$_chatMessagingBase/conversations/$conversationId/messages';
  static String chatMarkRead(String conversationId) => '$_chatMessagingBase/conversations/$conversationId/read';
  static String get chatCreateConversation => '$_chatMessagingBase/conversations';
  static String get chatUnreadCount => '$_chatMessagingBase/conversations/unread-count';
  static String get chatHealthz => '$_chatMessagingBase/healthz';

  /// Chat Socket.io URL
  static String get chatSocketUrl => chatServiceUrl;

  // ─────────────────────────────────────────────────────────────────────────────
  // AI Advisor Service Endpoints (port 8112)
  // المستشار الذكي
  // Kong route: /api/v1/ai-advisor
  // ─────────────────────────────────────────────────────────────────────────────

  static String get _aiAdvisorBase => '$effectiveBaseUrl/api/v1/ai-advisor';

  /// AI Advisor endpoints
  static String get aiAdvisorQuery => '$_aiAdvisorBase/query';
  static String get aiAdvisorChat => '$_aiAdvisorBase/chat';
  static String get aiAdvisorDiagnose => '$_aiAdvisorBase/diagnose';
  static String aiAdvisorRecommendations(String fieldId) => '$_aiAdvisorBase/recommendations/$fieldId';
  static String aiAdvisorAnalyzeField(String fieldId) => '$_aiAdvisorBase/analyze/$fieldId';
  static String get aiAdvisorHistory => '$_aiAdvisorBase/history';
  static String get aiAdvisorHealthz => '$_aiAdvisorBase/healthz';

  // ─────────────────────────────────────────────────────────────────────────────
  // Billing Service Endpoints (port 8089)
  // خدمة الفوترة
  // Kong route: /api/v1/billing
  // ─────────────────────────────────────────────────────────────────────────────

  static String get _billingBase => '$effectiveBaseUrl/api/v1/billing';

  /// Billing endpoints
  static String get billingWallet => '$_billingBase/wallet';
  static String get billingDeposit => '$_billingBase/wallet/deposit';
  static String get billingWithdraw => '$_billingBase/wallet/withdraw';
  static String get billingTransfer => '$_billingBase/wallet/transfer';
  static String get billingTransactions => '$_billingBase/transactions';
  static String get billingSubscription => '$_billingBase/subscription';
  static String get billingPlans => '$_billingBase/plans';
  static String get billingInvoices => '$_billingBase/invoices';
  static String billingPayInvoice(String invoiceId) => '$_billingBase/invoices/$invoiceId/pay';
  static String get billingUsage => '$_billingBase/usage';
  static String get billingHealthz => '$_billingBase/healthz';
}
