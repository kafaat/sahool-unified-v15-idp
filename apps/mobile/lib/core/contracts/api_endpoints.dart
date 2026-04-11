/// SAHOOL Unified API Endpoint Paths (Dart)
/// مسارات نقاط النهاية الموحدة
///
/// Auto-generated from: packages/shared-types/src/contracts/api-endpoints.ts
/// Used by: Mobile app (Flutter/Dart)
///
/// @version 16.0.0
library;

/// API version prefix
const String apiVersion = 'v1';
const String apiPrefix = '/api/$apiVersion';

/// Health & Infrastructure
abstract final class HealthEndpoints {
  static const String liveness = '/healthz';
  static const String readiness = '/readyz';
  static const String health = '/health';
}

/// Auth - المصادقة
abstract final class AuthEndpoints {
  static const String login = '$apiPrefix/auth/login';
  static const String logout = '$apiPrefix/auth/logout';
  static const String refresh = '$apiPrefix/auth/refresh';
  static const String me = '$apiPrefix/auth/me';
  static const String register = '$apiPrefix/auth/register';
  static const String forgotPassword = '$apiPrefix/auth/forgot-password';
  static const String resetPassword = '$apiPrefix/auth/reset-password';
  static const String verifyOtp = '$apiPrefix/auth/verify-otp';
  static const String sendOtp = '$apiPrefix/auth/send-otp';
}

/// Field Management - إدارة الحقول
abstract final class FieldEndpoints {
  static const String list = '$apiPrefix/fields';
  static const String create = '$apiPrefix/fields';
  static String get(String fieldId) => '$apiPrefix/fields/$fieldId';
  static String update(String fieldId) => '$apiPrefix/fields/$fieldId';
  static String delete(String fieldId) => '$apiPrefix/fields/$fieldId';
  static const String nearby = '$apiPrefix/fields/nearby';
  static const String sync = '$apiPrefix/fields/sync';
  static const String syncBatch = '$apiPrefix/fields/sync/batch';
}

/// Weather - الطقس
abstract final class WeatherEndpoints {
  static const String current = '$apiPrefix/weather/current';
  static String currentByLocation(String locationId) =>
      '$apiPrefix/weather/current/$locationId';
  static const String forecast = '$apiPrefix/weather/forecast';
  static String forecastByLocation(String locationId) =>
      '$apiPrefix/weather/forecast/$locationId';
  static String forecastByField(String fieldId) =>
      '$apiPrefix/weather/forecast/field/$fieldId';
  static const String alerts = '$apiPrefix/weather/alerts';
  static String alertsByField(String fieldId) =>
      '$apiPrefix/weather/alerts/field/$fieldId';
  static const String locations = '$apiPrefix/weather/locations';
  static const String agriculturalCalendar =
      '$apiPrefix/weather/agricultural-calendar';

  /// @since 4.7.0 — Generate a signed SVG weather graph URL for a field
  static String fieldGraphGenerate(String fieldId) =>
      '$apiPrefix/weather/fields/$fieldId/graph';

  /// @since 4.7.0 — Fetch a previously generated weather graph by signed id
  static String fieldGraphFetch(String graphId) =>
      '$apiPrefix/weather/graphs/$graphId';
}

/// Satellite & NDVI - الأقمار الصناعية
abstract final class SatelliteEndpoints {
  static const String analyze = '$apiPrefix/satellite/v1/analyze';
  static String analyzeField(String fieldId) =>
      '$apiPrefix/satellite/analyze/$fieldId';
  static String timeseries(String fieldId) =>
      '$apiPrefix/satellite/v1/timeseries/$fieldId';
  static String indices(String fieldId) =>
      '$apiPrefix/satellite/v1/indices/$fieldId';
  static const String satellites = '$apiPrefix/satellite/v1/satellites';
  static String health(String fieldId) =>
      '$apiPrefix/satellite/health/$fieldId';
  static String ndviField(String fieldId) =>
      '$apiPrefix/fields/$fieldId/ndvi';
  static const String ndviSummary = '$apiPrefix/ndvi/summary';
}

/// Crop Health - صحة المحاصيل
abstract final class CropHealthEndpoints {
  static const String analyze = '$apiPrefix/crop-health/analyze';
  static const String diagnose = '$apiPrefix/crop-health/diagnose';
  static const String diagnoseBatch = '$apiPrefix/crop-health/diagnose/batch';
  static const String crops = '$apiPrefix/crop-health/crops';
  static const String diseases = '$apiPrefix/crop-health/diseases';
  static String treatment(String diseaseId) =>
      '$apiPrefix/crop-health/treatment/$diseaseId';
  static String history(String fieldId) =>
      '$apiPrefix/crop-health/fields/$fieldId/history';
}

/// Irrigation - الري
abstract final class IrrigationEndpoints {
  static String recommendation(String fieldId) =>
      '$apiPrefix/irrigation/fields/$fieldId/recommendation';
  static const String calculate = '$apiPrefix/irrigation/calculate';
  static const String et0 = '$apiPrefix/irrigation/et0';
  static const String schedule = '$apiPrefix/irrigation/schedule';
  static const String crops = '$apiPrefix/irrigation/crops';
  static const String methods = '$apiPrefix/irrigation/methods';
}

/// Advisory & Fertilizer - الاستشارات والتسميد
abstract final class AdvisoryEndpoints {
  static const String recommend = '$apiPrefix/fertilizer/recommend';
  static const String soilInterpret = '$apiPrefix/fertilizer/soil/interpret';
  static const String crops = '$apiPrefix/fertilizer/crops';
  static const String fertilizers = '$apiPrefix/fertilizer/fertilizers';
  static const String deficiencySymptoms =
      '$apiPrefix/fertilizer/deficiency/symptoms';

  /// @since 4.7.0 — Jeevn-style unified per-field advisory
  static String comprehensive(String fieldId) =>
      '$apiPrefix/advisory/comprehensive/$fieldId';
}

/// Crop Loan Verification - التحقق من القروض الزراعية
/// @since 4.7.0 — Satellite-backed crop loan verification for banks / lenders
abstract final class LoanVerificationEndpoints {
  static String verify(String fieldId) =>
      '$apiPrefix/loans/crop-loan-verification/$fieldId';
}

/// Tasks - المهام
abstract final class TaskEndpoints {
  static const String list = '$apiPrefix/tasks';
  static const String create = '$apiPrefix/tasks';
  static String get(String taskId) => '$apiPrefix/tasks/$taskId';
  static String update(String taskId) => '$apiPrefix/tasks/$taskId';
  static String delete(String taskId) => '$apiPrefix/tasks/$taskId';
  static String complete(String taskId) => '$apiPrefix/tasks/$taskId/complete';
}

/// Equipment - المعدات
abstract final class EquipmentEndpoints {
  static const String list = '$apiPrefix/equipment';
  static const String create = '$apiPrefix/equipment';
  static String get(String equipmentId) => '$apiPrefix/equipment/$equipmentId';
  static String update(String equipmentId) =>
      '$apiPrefix/equipment/$equipmentId';
  static String maintenance(String equipmentId) =>
      '$apiPrefix/equipment/$equipmentId/maintenance';
  static String qrLookup(String qrCode) => '$apiPrefix/equipment/qr/$qrCode';
  static const String stats = '$apiPrefix/equipment/stats';

  /// @since 4.7.0 — Geofence event ingest (auto-drafts FieldOperation)
  static const String geofenceEvent = '$apiPrefix/equipment/geofence/event';
}

/// Traceability - التتبع
/// @since 4.7.0 — Blockchain-style anchor endpoints
abstract final class TraceabilityEndpoints {
  static const String batches = '$apiPrefix/traceability/batches';
  static String batchGet(String batchId) =>
      '$apiPrefix/traceability/batches/$batchId';
  static String batchEvents(String batchId) =>
      '$apiPrefix/traceability/batches/$batchId/events';
  static String qrCode(String batchId) =>
      '$apiPrefix/traceability/batches/$batchId/qr';

  /// List anchors for a field's chain
  static String anchorsList(String tenantId, String fieldId) =>
      '$apiPrefix/traceability/anchors/$tenantId/$fieldId';

  /// Verify the chain integrity for a field
  static String anchorsVerify(String tenantId, String fieldId) =>
      '$apiPrefix/traceability/anchors/$tenantId/$fieldId/verify';

  /// Subscriber stats (messages consumed, anchors created)
  static const String anchorsStats = '$apiPrefix/traceability/anchors/stats';
}

/// Alerts - التنبيهات
abstract final class AlertEndpoints {
  static const String list = '$apiPrefix/alerts';
  static String get(String alertId) => '$apiPrefix/alerts/$alertId';
  static String acknowledge(String alertId) =>
      '$apiPrefix/alerts/$alertId/acknowledge';
  static String resolve(String alertId) =>
      '$apiPrefix/alerts/$alertId/resolve';
}

/// Notifications - الإشعارات
abstract final class NotificationEndpoints {
  static const String list = '$apiPrefix/notifications';
  static String markRead(String notificationId) =>
      '$apiPrefix/notifications/$notificationId/read';
  static const String markAllRead = '$apiPrefix/notifications/read-all';
  static const String preferences = '$apiPrefix/notifications/preferences';
  static const String subscribe = '$apiPrefix/notifications/subscribe';
}

/// IoT - إنترنت الأشياء
abstract final class IoTEndpoints {
  static const String devices = '$apiPrefix/iot/devices';
  static String deviceGet(String deviceId) =>
      '$apiPrefix/iot/devices/$deviceId';
  static String deviceReadings(String deviceId) =>
      '$apiPrefix/iot/sensors/$deviceId/readings';
  static String fieldDevices(String fieldId) =>
      '$apiPrefix/iot/devices/field/$fieldId';
  static String deviceCommand(String deviceId) =>
      '$apiPrefix/iot/devices/$deviceId/command';
}

/// Virtual Sensors - الاستشعار الافتراضي
abstract final class VirtualSensorEndpoints {
  static const String et0Calculate =
      '$apiPrefix/virtual-sensors/et0/calculate';
  static const String etcCalculate =
      '$apiPrefix/virtual-sensors/etc/calculate';
  static const String crops = '$apiPrefix/virtual-sensors/crops';
  static String cropKc(String cropType) =>
      '$apiPrefix/virtual-sensors/crops/$cropType/kc';
  static const String irrigationRecommend =
      '$apiPrefix/virtual-sensors/irrigation/recommend';
  static const String irrigationQuickCheck =
      '$apiPrefix/virtual-sensors/irrigation/quick-check';
}

/// Marketplace - السوق
abstract final class MarketplaceEndpoints {
  static const String listings = '$apiPrefix/marketplace/listings';
  static const String products = '$apiPrefix/marketplace/products';
  static String productGet(String productId) =>
      '$apiPrefix/marketplace/products/$productId';
  static const String orders = '$apiPrefix/marketplace/orders';
  static String wallet(String userId) =>
      '$apiPrefix/marketplace/fintech/wallet/$userId';
}

/// Billing - الفوترة
abstract final class BillingEndpoints {
  static const String subscription = '$apiPrefix/billing/subscription';
  static const String plans = '$apiPrefix/billing/plans';
  static const String invoices = '$apiPrefix/billing/invoices';
  static const String usage = '$apiPrefix/billing/usage';
  static const String wallet = '$apiPrefix/billing/wallet';
  static const String transactions = '$apiPrefix/billing/transactions';
}

/// Chat & Community - الدردشة والمجتمع
abstract final class ChatEndpoints {
  static const String conversations = '$apiPrefix/chat/conversations';
  static String messages(String conversationId) =>
      '$apiPrefix/chat/conversations/$conversationId/messages';
  static String markRead(String conversationId) =>
      '$apiPrefix/chat/conversations/$conversationId/read';
  static const String unreadCount =
      '$apiPrefix/chat/conversations/unread-count';
  static String fieldMessages(String fieldId) =>
      '$apiPrefix/chat/fields/$fieldId/messages';
}

/// AI Advisor - المستشار الذكي
abstract final class AiAdvisorEndpoints {
  static const String query = '$apiPrefix/ai-advisor/query';
  static const String chat = '$apiPrefix/ai-advisor/chat';
  static const String diagnose = '$apiPrefix/ai-advisor/diagnose';
  static String recommendations(String fieldId) =>
      '$apiPrefix/ai-advisor/recommendations/$fieldId';
  static String analyze(String fieldId) =>
      '$apiPrefix/ai-advisor/analyze/$fieldId';
  static const String history = '$apiPrefix/ai-advisor/history';
}

/// Vision - الرؤية الحاسوبية
abstract final class VisionEndpoints {
  static const String detectPest = '$apiPrefix/vision/detect/pest';
  static const String detectDisease = '$apiPrefix/vision/detect/disease';
  static const String detectWeed = '$apiPrefix/vision/detect/weed';
  static const String countPlants = '$apiPrefix/vision/count/plants';
  static const String classifyRipeness = '$apiPrefix/vision/classify/ripeness';
  static const String modelsList = '$apiPrefix/vision/models/versions';
}

/// Indicators - المؤشرات
abstract final class IndicatorEndpoints {
  static const String dashboard = '$apiPrefix/indicators/dashboard';
  static String field(String fieldId) =>
      '$apiPrefix/indicators/field/$fieldId';
  static const String trends = '$apiPrefix/indicators/trends';
}

/// Crop Seasons - مواسم المحاصيل
///
/// First-class archive of per-field crop rotations (replaces the legacy
/// `field.metadata.cropHistory[]` JSON shim). Served by
/// field-management-service.
abstract final class CropSeasonEndpoints {
  static const String list = '$apiPrefix/crop-seasons';
  static String get(String cropSeasonId) =>
      '$apiPrefix/crop-seasons/$cropSeasonId';
  static String update(String cropSeasonId) =>
      '$apiPrefix/crop-seasons/$cropSeasonId';
  static String end(String cropSeasonId) =>
      '$apiPrefix/crop-seasons/$cropSeasonId/end';
  static String delete(String cropSeasonId) =>
      '$apiPrefix/crop-seasons/$cropSeasonId';
  static String listByField(String fieldId) =>
      '$apiPrefix/fields/$fieldId/crop-seasons';
  static String create(String fieldId) =>
      '$apiPrefix/fields/$fieldId/crop-seasons';
  static String rollup(String cropSeasonId) =>
      '$apiPrefix/crop-seasons/$cropSeasonId/rollup';
}

/// Field Operations - عمليات الحقل
///
/// Per-field operation log (plowing, land preparation, fertilization,
/// spraying, irrigation, harvesting, ...). Each row optionally links
/// to a CropSeason and an Equipment record for per-season and per-
/// equipment cost rollups.
abstract final class FieldOperationEndpoints {
  static const String list = '$apiPrefix/field-operations';
  static String get(String operationId) =>
      '$apiPrefix/field-operations/$operationId';
  static String update(String operationId) =>
      '$apiPrefix/field-operations/$operationId';
  static String delete(String operationId) =>
      '$apiPrefix/field-operations/$operationId';
  static String listByField(String fieldId) =>
      '$apiPrefix/fields/$fieldId/operations';
  static String create(String fieldId) =>
      '$apiPrefix/fields/$fieldId/operations';
  static String approve(String operationId) =>
      '$apiPrefix/field-operations/$operationId/approve';
  static String reject(String operationId) =>
      '$apiPrefix/field-operations/$operationId/reject';
}

/// ERP Sync - تكامل نظام المحاسبة
///
/// Routes for posting field operations to external accounting systems
/// (QuickBooks, SAP, Odoo, Xero, Oracle NetSuite, ...) via the
/// pluggable IErpAdapter interface in field-management-service.
abstract final class ErpSyncEndpoints {
  static String postFieldOperation(String operationId) =>
      '$apiPrefix/erp-sync/field-operations/$operationId/post';
  static const String health = '$apiPrefix/erp-sync/health';
}

/// Field Sub-Zones - المناطق الفرعية للحقل
///
/// Multi-polygon sub-zones within a single Field record. Critical for
/// terraced Yemeni farms where one "field" is actually many small
/// terraces with different elevation, slope, aspect, and crop
/// performance.
abstract final class FieldSubZoneEndpoints {
  static String listByField(String fieldId) =>
      '$apiPrefix/fields/$fieldId/sub-zones';
  static String create(String fieldId) =>
      '$apiPrefix/fields/$fieldId/sub-zones';
  static String get(String subZoneId) =>
      '$apiPrefix/field-sub-zones/$subZoneId';
  static String update(String subZoneId) =>
      '$apiPrefix/field-sub-zones/$subZoneId';
  static String delete(String subZoneId) =>
      '$apiPrefix/field-sub-zones/$subZoneId';
}

/// Field Reports - تقارير الحقل
///
/// Async HTML/PDF report generation, Arabic RTL first. Caller POSTs a
/// request and polls for status until 'ready', then fetches the content
/// via the signed URL or the /content endpoint.
abstract final class FieldReportEndpoints {
  static String create(String fieldId) =>
      '$apiPrefix/fields/$fieldId/reports';
  static String listByField(String fieldId) =>
      '$apiPrefix/fields/$fieldId/reports';
  static String get(String reportId) =>
      '$apiPrefix/field-reports/$reportId';
  static String getContent(String reportId) =>
      '$apiPrefix/field-reports/$reportId/content';
}

/// Carbon Footprint - البصمة الكربونية (IPCC Tier 1)
///
/// Served by carbon-service (port 8195). Aggregates per-operation CO2e
/// into per-field and per-season dashboards. See Python engine at
/// apps/services/carbon-service/src/engine/ipcc_tier1.py for the
/// factor table.
abstract final class CarbonEndpoints {
  static const String compute = '$apiPrefix/carbon/compute';
  static String computeOperation(String operationId) =>
      '$apiPrefix/carbon/operations/$operationId/compute';
  static String fieldSummary(String fieldId) =>
      '$apiPrefix/carbon/fields/$fieldId/summary';
  static String cropSeasonSummary(String cropSeasonId) =>
      '$apiPrefix/carbon/crop-seasons/$cropSeasonId/summary';
}

/// Public endpoints (no auth required)
const List<String> publicEndpoints = [
  AuthEndpoints.login,
  AuthEndpoints.register,
  AuthEndpoints.forgotPassword,
  AuthEndpoints.resetPassword,
  AuthEndpoints.verifyOtp,
  AuthEndpoints.sendOtp,
  HealthEndpoints.liveness,
  HealthEndpoints.readiness,
  HealthEndpoints.health,
];
