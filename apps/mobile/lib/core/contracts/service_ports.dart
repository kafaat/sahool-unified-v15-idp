/// SAHOOL Unified Service Ports Registry (Dart)
/// مصدر الحقيقة الوحيد لمنافذ الخدمات
///
/// Auto-generated from: packages/shared-types/src/contracts/service-ports.ts
/// Used by: Mobile app (Flutter/Dart)
///
/// @version 16.0.0
library;

/// All microservice ports - ثوابت المنافذ
abstract final class ServicePorts {
  // ── Core Services ────────────────────────────────────────────────────
  /// Field management (consolidated) - إدارة الحقول
  static const int fieldManagement = 3000;

  /// User authentication & management - المصادقة وإدارة المستخدمين
  static const int userService = 3025;

  /// Marketplace service - خدمة السوق
  static const int marketplace = 3010;

  /// Research trials - التجارب البحثية
  static const int researchCore = 3015;

  /// Disaster risk assessment - تقييم مخاطر الكوارث
  static const int disasterAssessment = 3020;

  // ── Intelligence Layer ───────────────────────────────────────────────
  /// Satellite imagery & NDVI - صور الأقمار الصناعية
  static const int vegetationAnalysis = 8090;

  /// Field indicators computation - حساب المؤشرات
  static const int indicators = 8091;

  /// Weather data & forecasts - بيانات الطقس
  static const int weather = 8092;

  /// Advisory & fertilizer recommendations - الاستشارات والتسميد
  static const int advisory = 8093;

  /// Smart irrigation scheduling - الري الذكي
  static const int irrigationSmart = 8094;

  /// Crop health AI / disease detection - صحة المحاصيل
  static const int cropIntelligence = 8095;

  /// NDVI processing - معالجة NDVI
  static const int ndviProcessor = 8118;

  /// Virtual sensor computation (ET0, ETC) - أجهزة الاستشعار الافتراضية
  static const int virtualSensors = 8119;

  /// Field analytics - تحليلات الحقل
  static const int fieldIntelligence = 8120;

  /// Farmer skills assessment - تقييم مهارات المزارع
  static const int skillsService = 8121;

  // ── Decision Layer ───────────────────────────────────────────────────
  /// Yield prediction (NestJS) - التنبؤ بالإنتاجية
  static const int yieldPrediction = 8152;

  /// Yield engine (legacy) - محرك الإنتاجية
  static const int yieldEngine = 8098;

  /// Agronomic rules engine - محرك القواعد الزراعية
  static const int agroRules = 8151;

  // ── Business Layer ───────────────────────────────────────────────────
  /// Task management - إدارة المهام
  static const int taskService = 8103;

  /// Equipment tracking - تتبع المعدات
  static const int equipment = 8101;

  /// Notification service - خدمة الإشعارات
  static const int notifications = 8110;

  /// Alert management - إدارة التنبيهات
  static const int alertService = 8113;

  /// Audit logging - سجل التدقيق
  static const int auditService = 8114;

  /// Billing & invoicing - الفوترة
  static const int billingCore = 8089;

  /// Provider configuration - تكوين المزودين
  static const int providerConfig = 8104;

  /// Inventory management - إدارة المخزون
  static const int inventory = 8116;

  // ── Communication ────────────────────────────────────────────────────
  /// WebSocket gateway - بوابة WebSocket
  static const int wsGateway = 8081;

  /// Real-time messaging - الرسائل الفورية
  static const int chatService = 8000;

  /// Field-level chat - دردشة الحقل
  static const int fieldChat = 8099;

  /// Community features (deprecated → chatService)
  static const int communityChat = 8097;

  // ── IoT & Sensors ───────────────────────────────────────────────────
  /// IoT device management - إدارة أجهزة إنترنت الأشياء
  static const int iotService = 8117;

  /// IoT protocol gateway - بوابة بروتوكولات IoT
  static const int iotGateway = 8106;

  // ── AI & Agents ──────────────────────────────────────────────────────
  /// AI copilot (multi-LLM, RAG) - المساعد الذكي
  static const int copilotApi = 8088;

  /// AI advisory service - خدمة الاستشارات الذكية
  static const int aiAdvisor = 8112;

  /// AI agents core - وحدة الوكلاء الذكية
  static const int aiAgentsCore = 8161;

  /// Knowledge graph - الرسم البياني المعرفي
  static const int knowledgeGraph = 8140;

  // ── Vision & Terrain ─────────────────────────────────────────────────
  /// YOLO26 computer vision - الرؤية الحاسوبية
  static const int yoloVision = 8150;

  /// Terrain analysis - تحليل التضاريس
  static const int terrainCore = 8185;

  /// Hydrology analysis - تحليل المياه
  static const int hydrology = 8165;

  /// Field leveling optimization - تحسين تسوية الحقول
  static const int levelingOptimizer = 8170;

  /// Edge device management - إدارة الأجهزة الطرفية
  static const int edgeOrchestrator = 8180;

  // ── Agriculture Domain ───────────────────────────────────────────────
  /// Soil analysis - تحليل التربة
  static const int soilAnalysis = 8134;

  /// Pest detection AI - كشف الآفات
  static const int pestDetection = 8125;

  /// Drone integration - تكامل الطائرات بدون طيار
  static const int droneService = 8126;

  /// Cooperative management - إدارة التعاونيات
  static const int cooperative = 8127;

  /// GlobalGAP compliance - الامتثال لمعايير جلوبال جاب
  static const int globalgap = 8128;

  /// Product traceability - التتبع
  static const int traceability = 8123;

  /// Farmer CRM - إدارة علاقات المزارعين
  static const int crmService = 8131;

  /// Astronomical / Islamic calendar - التقويم الفلكي
  static const int astronomicalCalendar = 8111;

  // ── Infrastructure ───────────────────────────────────────────────────
  /// Kong API Gateway - بوابة API
  static const int kongGateway = 8000;

  /// NATS message queue - قائمة الرسائل
  static const int nats = 4222;

  /// PostgreSQL database - قاعدة البيانات
  static const int postgres = 5432;

  /// PgBouncer connection pool
  static const int pgbouncer = 6432;

  /// Redis cache - ذاكرة التخزين المؤقت
  static const int redis = 6379;
}

/// Get the full service URL for a given port.
String getServiceUrl(int port, {String host = 'localhost', String protocol = 'http'}) {
  return '$protocol://$host:$port';
}
