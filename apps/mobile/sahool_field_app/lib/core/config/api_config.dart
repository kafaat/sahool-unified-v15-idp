/// API Configuration for SAHOOL Field App
/// إعدادات الاتصال بالخادم - توحيد جميع المسارات عبر Kong Gateway
library;

import 'dart:io';

/// Service ports for local development (direct access, bypass Kong)
/// منافذ الخدمات للتطوير المحلي (الوصول المباشر)
class ServicePorts {
  static const int fieldCore = 3000;
  static const int marketplace = 3010;
  static const int satellite = 8090;
  static const int indicators = 8091;
  static const int weather = 8092;
  static const int fertilizer = 8093;
  static const int irrigation = 8094;
  static const int cropHealth = 8095;
  static const int virtualSensors = 8119;
  static const int communityChat = 8097;
  static const int equipment = 8101;
  static const int notifications = 8110;
  static const int astronomicalCalendar = 8111;
  static const int gateway = 8000; // Kong API Gateway
}

/// API configuration class - Unified Kong Gateway routing
/// جميع الطلبات تمر عبر Kong Gateway للتوحيد والأمان
///
/// Kong strip_path convention:
///   Client sends: /api/v1/{service}/*
///   Kong strips:  /api/v1/{service}
///   Service gets: /*
///
/// 10.0.2.2 للمحاكي الأندرويد، localhost للـ iOS Simulator
/// لأجهزة Android الحقيقية: استخدم IP الكمبيوتر (192.168.x.x)
class ApiConfig {
  ApiConfig._();

  /// ⚠️ للتجربة على جهاز حقيقي:
  /// 1. اكتب `ipconfig` (Windows) أو `ifconfig` (Mac/Linux)
  /// 2. انسخ عنوان IPv4 (مثل 192.168.1.5)
  /// 3. ضعه في المتغير أدناه
  static const String? _customHost = null; // مثال: '192.168.1.5'

  /// Production API URL
  static const String _productionHost = 'api.sahool.io';

  /// Check if running in release mode
  static bool get isProduction => const bool.fromEnvironment('dart.vm.product');

  /// Get host based on platform and environment
  static String get _host {
    if (isProduction && _customHost == null) {
      return _productionHost;
    }
    if (_customHost != null && _customHost!.isNotEmpty) {
      return _customHost!;
    }
    if (Platform.isAndroid) {
      return '10.0.2.2';
    }
    return 'localhost';
  }

  /// Get protocol (https for production, http for development)
  static String get _protocol => isProduction ? 'https' : 'http';

  /// Kong Gateway URL - ALL requests go through this
  /// عنوان Kong Gateway - جميع الطلبات تمر من هنا
  static String get gatewayUrl => '$_protocol://$_host:${ServicePorts.gateway}';

  /// Production base URL
  static const String productionBaseUrl = 'https://api.sahool.io';

  /// Effective base URL (Kong Gateway)
  static String get baseUrl {
    return isProduction ? productionBaseUrl : gatewayUrl;
  }

  /// Legacy base URL for field-core (direct access in dev only)
  static String get fieldCoreUrl => '$_protocol://$_host:${ServicePorts.fieldCore}';

  // ═══════════════════════════════════════════════════════════════════════════
  // KONG GATEWAY ROUTES - All services accessed via /api/v1/{service}/*
  // جميع الخدمات عبر Kong Gateway
  // ═══════════════════════════════════════════════════════════════════════════

  // ─────────────────────────────────────────────────────────────────────────────
  // Field Core Service
  // خدمة الحقول الأساسية
  // Kong route: /api/v1/fields → field-management-service
  // ─────────────────────────────────────────────────────────────────────────────

  static String get fields => '$baseUrl/api/v1/fields';
  static String fieldById(String id) => '$baseUrl/api/v1/fields/$id';
  static String get fieldsSync => '$baseUrl/api/v1/fields/sync';
  static String get fieldsBatch => '$baseUrl/api/v1/fields/batch';
  static String get fieldsNearby => '$baseUrl/api/v1/fields/nearby';

  // ─────────────────────────────────────────────────────────────────────────────
  // Tasks Service
  // خدمة المهام
  // ─────────────────────────────────────────────────────────────────────────────

  static String get tasks => '$baseUrl/api/v1/tasks';
  static String taskById(String id) => '$baseUrl/api/v1/tasks/$id';

  // ─────────────────────────────────────────────────────────────────────────────
  // Auth Service
  // خدمة المصادقة
  // Kong route: /api/v1/auth → auth-service
  // ─────────────────────────────────────────────────────────────────────────────

  static String get login => '$baseUrl/api/v1/auth/login';
  static String get authRegister => '$baseUrl/api/v1/auth/register';
  static String get refreshToken => '$baseUrl/api/v1/auth/refresh';

  // ─────────────────────────────────────────────────────────────────────────────
  // Satellite Service (vegetation-analysis-service)
  // خدمة الأقمار الصناعية
  // Kong route: /api/v1/satellite → strips to / → service receives /*
  // ─────────────────────────────────────────────────────────────────────────────

  static String get ndvi => '$baseUrl/api/v1/satellite/analyze';
  static String ndviByFieldId(String fieldId) => '$baseUrl/api/v1/satellite/analyze/$fieldId';
  static String get ndviTimeseries => '$baseUrl/api/v1/satellite/timeseries';
  static String get satellites => '$baseUrl/api/v1/satellite/satellites';
  static String get regions => '$baseUrl/api/v1/satellite/regions';
  static String get imagery => '$baseUrl/api/v1/satellite/imagery';

  // ─────────────────────────────────────────────────────────────────────────────
  // Weather Service (weather-core)
  // خدمة الطقس
  // Kong route: /api/v1/weather-core → strips to / → service receives /*
  // ─────────────────────────────────────────────────────────────────────────────

  static String get weather => '$baseUrl/api/v1/weather-core/weather/current';
  static String weatherByLocation(double lat, double lng) =>
      '$baseUrl/api/v1/weather-core/weather/current?lat=$lat&lon=$lng';
  static String get forecast => '$baseUrl/api/v1/weather-core/weather/forecast';
  static String forecastByLocation(double lat, double lng, {int days = 7}) =>
      '$baseUrl/api/v1/weather-core/weather/forecast?lat=$lat&lon=$lng&days=$days';
  static String get weatherAlerts => '$baseUrl/api/v1/weather-core/weather/alerts';
  static String get agriculturalCalendar => '$baseUrl/api/v1/weather-core/agricultural-calendar';

  // ─────────────────────────────────────────────────────────────────────────────
  // Indicators Service
  // خدمة المؤشرات
  // Kong route: /api/v1/indicators → strips to / → service receives /*
  // ─────────────────────────────────────────────────────────────────────────────

  static String get indicatorDefinitions => '$baseUrl/api/v1/indicators/definitions';
  static String indicatorsByField(String fieldId) => '$baseUrl/api/v1/indicators/field/$fieldId';
  static String get dashboard => '$baseUrl/api/v1/indicators/dashboard';
  static String dashboardByTenant(String tenantId) => '$baseUrl/api/v1/indicators/dashboard/$tenantId';
  static String get indicatorAlerts => '$baseUrl/api/v1/indicators/alerts';
  static String get indicatorTrends => '$baseUrl/api/v1/indicators/trends';

  // ─────────────────────────────────────────────────────────────────────────────
  // Fertilizer Advisor Service
  // مستشار التسميد
  // Kong route: /api/v1/fertilizer → strips to / → service receives /*
  // ─────────────────────────────────────────────────────────────────────────────

  static String get fertilizerCrops => '$baseUrl/api/v1/fertilizer/crops';
  static String get fertilizerTypes => '$baseUrl/api/v1/fertilizer/fertilizers';
  static String get fertilizerRecommendation => '$baseUrl/api/v1/fertilizer/recommend';
  static String get soilInterpretation => '$baseUrl/api/v1/fertilizer/soil/interpret';
  static String get deficiencySymptoms => '$baseUrl/api/v1/fertilizer/deficiency/symptoms';
  static String get applicationSchedule => '$baseUrl/api/v1/fertilizer/schedule';

  // ─────────────────────────────────────────────────────────────────────────────
  // Irrigation Smart Service
  // الري الذكي
  // Kong route: /api/v1/irrigation → strips to / → service receives /*
  // ─────────────────────────────────────────────────────────────────────────────

  static String get irrigationCrops => '$baseUrl/api/v1/irrigation/crops';
  static String get irrigationMethods => '$baseUrl/api/v1/irrigation/methods';
  static String get irrigationCalculate => '$baseUrl/api/v1/irrigation/calculate';
  static String get waterBalance => '$baseUrl/api/v1/irrigation/water-balance';
  static String get sensorReading => '$baseUrl/api/v1/irrigation/sensor-reading';
  static String get irrigationEfficiency => '$baseUrl/api/v1/irrigation/efficiency';
  static String get irrigationSchedule => '$baseUrl/api/v1/irrigation/schedule';

  // ─────────────────────────────────────────────────────────────────────────────
  // Crop Health AI Service (crop-health-ai)
  // سهول فيجن - الذكاء الاصطناعي لصحة المحاصيل
  // Kong route: /api/v1/crop-health → strips to / → service receives /*
  // ─────────────────────────────────────────────────────────────────────────────

  static String get diagnose => '$baseUrl/api/v1/crop-health/diagnose';
  static String get diagnoseBatch => '$baseUrl/api/v1/crop-health/diagnose/batch';
  static String get supportedCrops => '$baseUrl/api/v1/crop-health/crops';
  static String get diseases => '$baseUrl/api/v1/crop-health/diseases';
  static String treatmentDetails(String diseaseId) => '$baseUrl/api/v1/crop-health/treatment/$diseaseId';
  static String get expertReview => '$baseUrl/api/v1/crop-health/expert-review';

  // ─────────────────────────────────────────────────────────────────────────────
  // Virtual Sensors Engine
  // محرك المستشعرات الافتراضية
  // Kong route: /api/v1/virtual-sensors → strips to / → service receives /*
  // ─────────────────────────────────────────────────────────────────────────────

  static String get et0Calculate => '$baseUrl/api/v1/virtual-sensors/et0/calculate';
  static String get virtualSensorsCrops => '$baseUrl/api/v1/virtual-sensors/crops';
  static String cropKc(String cropType) => '$baseUrl/api/v1/virtual-sensors/crops/$cropType/kc';
  static String get etcCalculate => '$baseUrl/api/v1/virtual-sensors/etc/calculate';
  static String get virtualSensorsSoils => '$baseUrl/api/v1/virtual-sensors/soils';
  static String get soilMoistureEstimate => '$baseUrl/api/v1/virtual-sensors/soil-moisture/estimate';
  static String get irrigationMethodsInfo => '$baseUrl/api/v1/virtual-sensors/irrigation-methods';
  static String get irrigationRecommend => '$baseUrl/api/v1/virtual-sensors/irrigation/recommend';
  static String get irrigationQuickCheck => '$baseUrl/api/v1/virtual-sensors/irrigation/quick-check';

  // ─────────────────────────────────────────────────────────────────────────────
  // Equipment Service
  // خدمة المعدات
  // Kong route: /api/v1/equipment → strips to / → service receives /*
  // ─────────────────────────────────────────────────────────────────────────────

  static String get equipment => '$baseUrl/api/v1/equipment';
  static String equipmentById(String id) => '$baseUrl/api/v1/equipment/$id';
  static String equipmentByQr(String qrCode) => '$baseUrl/api/v1/equipment/qr/$qrCode';
  static String get equipmentStats => '$baseUrl/api/v1/equipment/stats';
  static String get maintenanceAlerts => '$baseUrl/api/v1/equipment/maintenance/alerts';
  static String maintenanceByEquipment(String id) => '$baseUrl/api/v1/equipment/maintenance/$id';

  // ─────────────────────────────────────────────────────────────────────────────
  // Community Chat Service
  // خدمة الدردشة المجتمعية
  // Kong route: /api/v1/community → strips to / → service receives /*
  // ─────────────────────────────────────────────────────────────────────────────

  static String get chatUrl => '$_protocol://$_host:${ServicePorts.communityChat}'; // Socket.io direct
  static String get chatRequests => '$baseUrl/api/v1/community/requests';
  static String chatRoomMessages(String roomId) => '$baseUrl/api/v1/community/rooms/$roomId/messages';
  static String get chatOnlineExperts => '$baseUrl/api/v1/community/experts/online';
  static String get chatStats => '$baseUrl/api/v1/community/stats';

  // ─────────────────────────────────────────────────────────────────────────────
  // Notification Service
  // خدمة الإشعارات
  // Kong routes (all strip_path: true, service has NO /v1 prefix):
  //   /api/v1/notifications → service receives /*, /farmer/{id}, /broadcast, etc.
  //   /api/v1/alerts        → service receives /weather, /pest
  //   /api/v1/reminders     → service receives /irrigation
  //   /api/v1/farmers       → service receives /register, /{id}/preferences
  //   /api/v1/channels      → service receives /add, /list, etc.
  //   /api/v1/preferences   → service receives /, /update, etc.
  // ─────────────────────────────────────────────────────────────────────────────

  /// Create notification: POST /api/v1/notifications
  static String get notifications => '$baseUrl/api/v1/notifications';
  /// Get farmer notifications: GET /api/v1/notifications/farmer/{farmerId}
  static String notificationForFarmer(String farmerId) => '$baseUrl/api/v1/notifications/farmer/$farmerId';
  /// Mark as read: PATCH /api/v1/notifications/{id}/read
  static String notificationMarkAsRead(String id) => '$baseUrl/api/v1/notifications/$id/read';
  /// Get broadcast: GET /api/v1/notifications/broadcast
  static String get notificationBroadcast => '$baseUrl/api/v1/notifications/broadcast';
  /// Weather alert: POST /api/v1/alerts/weather
  static String get weatherAlert => '$baseUrl/api/v1/alerts/weather';
  /// Pest alert: POST /api/v1/alerts/pest
  static String get pestAlert => '$baseUrl/api/v1/alerts/pest';
  /// Irrigation reminder: POST /api/v1/reminders/irrigation
  static String get irrigationReminder => '$baseUrl/api/v1/reminders/irrigation';
  /// Register farmer: POST /api/v1/farmers/register
  static String get farmerRegister => '$baseUrl/api/v1/farmers/register';
  /// Update preferences: PUT /api/v1/farmers/{id}/preferences
  static String farmerPreferences(String farmerId) => '$baseUrl/api/v1/farmers/$farmerId/preferences';
  /// Notification channels: /api/v1/channels/*
  static String get notificationChannels => '$baseUrl/api/v1/channels';
  static String get addChannel => '$baseUrl/api/v1/channels/add';
  static String get listChannels => '$baseUrl/api/v1/channels/list';
  /// Notification preferences: /api/v1/preferences/*
  static String get notificationPreferences => '$baseUrl/api/v1/preferences';
  static String get updatePreference => '$baseUrl/api/v1/preferences/update';
  /// Stats: GET /api/v1/notification-stats/stats
  static String get notificationStats => '$baseUrl/api/v1/notification-stats/stats';

  // ─────────────────────────────────────────────────────────────────────────────
  // Marketplace & FinTech Service
  // خدمة السوق والمحفظة المالية
  // Kong route: /api/v1/marketplace → strips to / → service receives /*
  // ─────────────────────────────────────────────────────────────────────────────

  /// Wallet endpoints
  static String wallet(String userId) => '$baseUrl/api/v1/marketplace/fintech/wallet/$userId';
  static String walletDeposit(String walletId) => '$baseUrl/api/v1/marketplace/fintech/wallet/$walletId/deposit';
  static String walletWithdraw(String walletId) => '$baseUrl/api/v1/marketplace/fintech/wallet/$walletId/withdraw';
  static String walletTransactions(String walletId) => '$baseUrl/api/v1/marketplace/fintech/wallet/$walletId/transactions';

  /// Credit & Loans
  static String get calculateCreditScore => '$baseUrl/api/v1/marketplace/fintech/calculate-score';
  static String get loans => '$baseUrl/api/v1/marketplace/fintech/loans';
  static String userLoans(String walletId) => '$baseUrl/api/v1/marketplace/fintech/loans/$walletId';
  static String repayLoan(String loanId) => '$baseUrl/api/v1/marketplace/fintech/loans/$loanId/repay';

  /// Market products
  static String get marketProducts => '$baseUrl/api/v1/marketplace/market/products';
  static String marketProductById(String productId) => '$baseUrl/api/v1/marketplace/market/products/$productId';
  static String get listHarvest => '$baseUrl/api/v1/marketplace/market/harvest';
  static String get marketOrders => '$baseUrl/api/v1/marketplace/market/orders';
  static String userMarketOrders(String userId) => '$baseUrl/api/v1/marketplace/market/orders/user/$userId';
  static String get marketStats => '$baseUrl/api/v1/marketplace/market/stats';

  // ─────────────────────────────────────────────────────────────────────────────
  // Astronomical Calendar Service
  // خدمة التقويم الفلكي
  // Kong route: /api/v1/astronomy → strips to / → service receives /*
  // ─────────────────────────────────────────────────────────────────────────────

  static String get astronomyCalendar => '$baseUrl/api/v1/astronomy/calendar';
  static String get moonPhases => '$baseUrl/api/v1/astronomy/moon-phases';
  static String get prayerTimes => '$baseUrl/api/v1/astronomy/prayer-times';

  // ═══════════════════════════════════════════════════════════════════════════
  // Timeouts Configuration
  // ═══════════════════════════════════════════════════════════════════════════

  static const Duration connectTimeout = Duration(seconds: 30);
  static const Duration sendTimeout = Duration(seconds: 15);
  static const Duration receiveTimeout = Duration(seconds: 15);
  static const Duration longOperationTimeout = Duration(seconds: 60);

  // ═══════════════════════════════════════════════════════════════════════════
  // Headers
  // ═══════════════════════════════════════════════════════════════════════════

  static Map<String, String> get defaultHeaders => {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Accept-Language': 'ar,en',
  };

  static Map<String, String> authHeaders(String token) => {
    ...defaultHeaders,
    'Authorization': 'Bearer $token',
  };

  static Map<String, String> tenantHeaders(String token, String tenantId) => {
    ...authHeaders(token),
    'X-Tenant-Id': tenantId,
  };

  // ═══════════════════════════════════════════════════════════════════════════
  // Health Check Endpoints (via Kong)
  // ═══════════════════════════════════════════════════════════════════════════

  static String healthCheck(String service) => '$baseUrl/api/v1/$service/healthz';

  static Map<String, String> get allHealthChecks => {
    'satellite': healthCheck('satellite'),
    'indicators': healthCheck('indicators'),
    'weather': healthCheck('weather-core'),
    'fertilizer': healthCheck('fertilizer'),
    'irrigation': healthCheck('irrigation'),
    'cropHealth': healthCheck('crop-health'),
    'virtualSensors': healthCheck('virtual-sensors'),
    'community': healthCheck('community'),
    'equipment': healthCheck('equipment'),
    'notifications': healthCheck('notifications'),
    'marketplace': healthCheck('marketplace'),
  };
}
