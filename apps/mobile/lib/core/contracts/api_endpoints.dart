/// SAHOOL Unified API Endpoint Paths (auto-generated)
/// DO NOT EDIT - Generated from packages/shared-types/src/contracts/api-endpoints.ts
/// Run: npx tsx scripts/sync-contracts-to-dart.ts
///
/// Contract version: 2.4.0
library;

/// API version prefix
const String apiVersion = 'v1';
const String apiPrefix = '/api/$apiVersion';

/// Health & Infrastructure
abstract final class HealthEndpoints {
  static const String liveness = '/healthz';
  static const String readiness = '/readyz';
  static const String health = '/health';
  static const String metrics = '/metrics';
}

/// Per-service Kong health checks
abstract final class ServiceHealthEndpoints {
  static const String fieldManagement = '\$apiPrefix/fields/healthz';
  static const String weather = '\$apiPrefix/weather/healthz';
  static const String vegetation = '\$apiPrefix/vegetation/healthz';
  static const String irrigation = '\$apiPrefix/irrigation/healthz';
  static const String advisory = '\$apiPrefix/advisory/healthz';
  static const String tasks = '\$apiPrefix/tasks/healthz';
  static const String notifications = '\$apiPrefix/notifications/healthz';
  static const String alerts = '\$apiPrefix/alerts/healthz';
  static const String cropHealth = '\$apiPrefix/crop-health/healthz';
  static const String satellite = '\$apiPrefix/satellite/healthz';
  static const String equipment = '\$apiPrefix/equipment/healthz';
  static const String iot = '\$apiPrefix/iot/healthz';
  static const String marketplace = '\$apiPrefix/marketplace/healthz';
  static const String billing = '\$apiPrefix/billing/healthz';
  static const String chat = '\$apiPrefix/chat/healthz';
  static const String yieldServiceHealth = '\$apiPrefix/yield/healthz';
  static const String disasters = '\$apiPrefix/disasters/healthz';
  static const String providers = '\$apiPrefix/providers/healthz';
  static const String agroRules = '\$apiPrefix/agro-rules/healthz';
  static const String intelligence = '\$apiPrefix/intelligence/healthz';
}

/// Auth - المصادقة
abstract final class AuthEndpoints {
  static const String login = '\$apiPrefix/auth/login';
  static const String logout = '\$apiPrefix/auth/logout';
  static const String refresh = '\$apiPrefix/auth/refresh';
  static const String me = '\$apiPrefix/auth/me';
  static const String register = '\$apiPrefix/auth/register';
  static const String forgotPassword = '\$apiPrefix/auth/forgot-password';
  static const String resetPassword = '\$apiPrefix/auth/reset-password';
  static const String verifyOtp = '\$apiPrefix/auth/verify-otp';
  static const String sendOtp = '\$apiPrefix/auth/send-otp';
  static const String resendOtp = '\$apiPrefix/auth/resend-otp';
  static const String activity = '\$apiPrefix/auth/activity';
}

/// Field Management - إدارة الحقول
abstract final class FieldEndpoints {
  static const String list = '\$apiPrefix/fields';
  static String getField(String fieldId) => '\$apiPrefix/fields/$fieldId';
  static const String create = '\$apiPrefix/fields';
  static String update(String fieldId) => '\$apiPrefix/fields/$fieldId';
  static String delete(String fieldId) => '\$apiPrefix/fields/$fieldId';
  static const String nearby = '\$apiPrefix/fields/nearby';
  static const String syncField = '\$apiPrefix/fields/sync';
  static const String syncBatch = '\$apiPrefix/fields/sync/batch';
  static String boundary(String fieldId) => '\$apiPrefix/fields/$fieldId/boundary';
  static String boundaryUpdate(String fieldId) => '\$apiPrefix/fields/$fieldId/boundary';
  static String boundaryHistory(String fieldId) => '\$apiPrefix/fields/$fieldId/boundary-history';
  static String boundaryRollback(String fieldId) => '\$apiPrefix/fields/$fieldId/boundary-history/rollback';
}

/// Weather - الطقس
abstract final class WeatherEndpoints {
  static const String current = '\$apiPrefix/weather/current';
  static String currentByLocation(String locationId) => '\$apiPrefix/weather/current/$locationId';
  static const String forecast = '\$apiPrefix/weather/forecast';
  static String forecastByLocation(String locationId) => '\$apiPrefix/weather/forecast/$locationId';
  static String forecastByField(String fieldId) => '\$apiPrefix/weather/forecast/field/$fieldId';
  static const String alerts = '\$apiPrefix/weather/alerts';
  static String alertsByLocation(String locationId) => '\$apiPrefix/weather/alerts/$locationId';
  static String alertsByField(String fieldId) => '\$apiPrefix/weather/alerts/field/$fieldId';
  static const String locations = '\$apiPrefix/weather/locations';
  static const String agriculturalCalendar = '\$apiPrefix/weather/agricultural-calendar';
  static const String kongCurrent = '\$apiPrefix/weather/weather/current';
  static const String kongForecast = '\$apiPrefix/weather/weather/forecast';
  static const String kongAgriculturalReport = '\$apiPrefix/weather/weather/agricultural-report';
  static String kongCurrentByLocation(String locationId) => '\$apiPrefix/weather/v1/current/$locationId';
  static String kongForecastByLocation(String locationId) => '\$apiPrefix/weather/v1/forecast/$locationId';
  static const String kongLocations = '\$apiPrefix/weather/v1/locations';
  static const String weatherCoreCurrent = '\$apiPrefix/weather-core/weather/current';
  static const String weatherCoreForecast = '\$apiPrefix/weather-core/weather/forecast';
  static const String weatherCoreAgReport = '\$apiPrefix/weather-core/weather/agricultural-report';
}

/// Satellite & NDVI - الأقمار الصناعية
abstract final class SatelliteEndpoints {
  static const String analyze = '\$apiPrefix/satellite/v1/analyze';
  static String analyzeField(String fieldId) => '\$apiPrefix/satellite/analyze/$fieldId';
  static String timeseries(String fieldId) => '\$apiPrefix/satellite/v1/timeseries/$fieldId';
  static String indices(String fieldId) => '\$apiPrefix/satellite/v1/indices/$fieldId';
  static const String satellites = '\$apiPrefix/satellite/v1/satellites';
  static String health(String fieldId) => '\$apiPrefix/satellite/health/$fieldId';
  static String phenology(String fieldId) => '\$apiPrefix/satellite/phenology/$fieldId';
  static String imagery(String fieldId) => '\$apiPrefix/satellite/imagery/$fieldId';
  static String ndviField(String fieldId) => '\$apiPrefix/fields/$fieldId/ndvi';
  static const String ndviSummary = '\$apiPrefix/ndvi/summary';
}

/// Crop Health - صحة المحاصيل
abstract final class CropHealthEndpoints {
  static const String analyze = '\$apiPrefix/crop-health/analyze';
  static const String diagnose = '\$apiPrefix/crop-health/diagnose';
  static const String diagnoseBatch = '\$apiPrefix/crop-health/diagnose/batch';
  static const String decision = '\$apiPrefix/crop-health/decision';
  static String history(String fieldId) => '\$apiPrefix/crop-health/fields/$fieldId/history';
  static const String crops = '\$apiPrefix/crop-health/crops';
  static const String diseases = '\$apiPrefix/crop-health/diseases';
  static String treatment(String diseaseId) => '\$apiPrefix/crop-health/treatment/$diseaseId';
  static const String expertReview = '\$apiPrefix/crop-health/expert-review';
  static const String diagnosesList = '\$apiPrefix/crop-health/diagnoses';
  static const String diagnosesStats = '\$apiPrefix/crop-health/diagnoses/stats';
  static String diagnosesUpdate(String diagnosisId) => '\$apiPrefix/crop-health/diagnoses/$diagnosisId';
}

/// Irrigation - الري
abstract final class IrrigationEndpoints {
  static String recommendation(String fieldId) => '\$apiPrefix/irrigation/fields/$fieldId/recommendation';
  static const String calculate = '\$apiPrefix/irrigation/calculate';
  static const String et0 = '\$apiPrefix/irrigation/et0';
  static const String waterBalance = '\$apiPrefix/irrigation/water-balance';
  static const String sensorReading = '\$apiPrefix/irrigation/sensor-reading';
  static const String efficiency = '\$apiPrefix/irrigation/efficiency';
  static const String schedule = '\$apiPrefix/irrigation/schedule';
  static const String schedulesList = '\$apiPrefix/irrigation/schedules';
  static String schedulesGet(String scheduleId) => '\$apiPrefix/irrigation/schedules/$scheduleId';
  static const String schedulesCreate = '\$apiPrefix/irrigation/schedules';
  static String schedulesUpdate(String scheduleId) => '\$apiPrefix/irrigation/schedules/$scheduleId';
  static String schedulesDelete(String scheduleId) => '\$apiPrefix/irrigation/schedules/$scheduleId';
  static String history(String fieldId) => '\$apiPrefix/irrigation/history/$fieldId';
  static const String recommendations = '\$apiPrefix/irrigation/recommendations';
  static const String crops = '\$apiPrefix/irrigation/crops';
  static const String methods = '\$apiPrefix/irrigation/methods';
}

/// Advisory - الاستشارات
abstract final class AdvisoryEndpoints {
  static const String recommend = '\$apiPrefix/fertilizer/recommend';
  static const String soilInterpret = '\$apiPrefix/fertilizer/soil/interpret';
  static const String crops = '\$apiPrefix/fertilizer/crops';
  static const String fertilizers = '\$apiPrefix/fertilizer/fertilizers';
  static const String deficiencySymptoms = '\$apiPrefix/fertilizer/deficiency/symptoms';
  static const String schedule = '\$apiPrefix/fertilizer/schedule';
  static const String recommendations = '\$apiPrefix/advisory/recommendations';
  static const String fertilizerAdvisory = '\$apiPrefix/advisory/fertilizer';
  static const String fertilizerCalculate = '\$apiPrefix/advisory/fertilizer/calculate';
  static const String advice = '\$apiPrefix/advisory/advice';
  static const String disease = '\$apiPrefix/advisory/disease';
  static const String nutrients = '\$apiPrefix/advisory/nutrients';
  static const String agroAdvice = '\$apiPrefix/agro-advisor/advice';
  static const String agroDisease = '\$apiPrefix/agro-advisor/disease';
  static const String agroNutrients = '\$apiPrefix/agro-advisor/nutrients';
}

/// Tasks - المهام
abstract final class TaskEndpoints {
  static const String list = '\$apiPrefix/tasks';
  static String getTask(String taskId) => '\$apiPrefix/tasks/$taskId';
  static const String create = '\$apiPrefix/tasks';
  static String update(String taskId) => '\$apiPrefix/tasks/$taskId';
  static String delete(String taskId) => '\$apiPrefix/tasks/$taskId';
  static String status(String taskId) => '\$apiPrefix/tasks/$taskId/status';
  static String complete(String taskId) => '\$apiPrefix/tasks/$taskId/complete';
}

/// Equipment - المعدات
abstract final class EquipmentEndpoints {
  static const String list = '\$apiPrefix/equipment';
  static String getEquipment(String equipmentId) => '\$apiPrefix/equipment/$equipmentId';
  static const String create = '\$apiPrefix/equipment';
  static String update(String equipmentId) => '\$apiPrefix/equipment/$equipmentId';
  static String delete(String equipmentId) => '\$apiPrefix/equipment/$equipmentId';
  static String status(String equipmentId) => '\$apiPrefix/equipment/$equipmentId/status';
  static String maintenance(String equipmentId) => '\$apiPrefix/equipment/$equipmentId/maintenance';
  static String qrLookup(String qrCode) => '\$apiPrefix/equipment/qr/$qrCode';
  static const String stats = '\$apiPrefix/equipment/stats';
  static const String maintenanceAlerts = '\$apiPrefix/equipment/maintenance/alerts';
}

/// Alerts - التنبيهات
abstract final class AlertEndpoints {
  static const String list = '\$apiPrefix/alerts';
  static String getAlert(String alertId) => '\$apiPrefix/alerts/$alertId';
  static const String create = '\$apiPrefix/alerts';
  static String delete(String alertId) => '\$apiPrefix/alerts/$alertId';
  static String acknowledge(String alertId) => '\$apiPrefix/alerts/$alertId/acknowledge';
  static String resolve(String alertId) => '\$apiPrefix/alerts/$alertId/resolve';
}

/// Notifications - الإشعارات
abstract final class NotificationEndpoints {
  static const String list = '\$apiPrefix/notifications';
  static String getNotification(String notificationId) => '\$apiPrefix/notifications/$notificationId';
  static String markRead(String notificationId) => '\$apiPrefix/notifications/$notificationId/read';
  static const String markAllRead = '\$apiPrefix/notifications/read-all';
  static const String preferences = '\$apiPrefix/notifications/preferences';
  static const String subscribe = '\$apiPrefix/notifications/subscribe';
  static const String unsubscribe = '\$apiPrefix/notifications/unsubscribe';
}

/// IoT - إنترنت الأشياء
abstract final class IotEndpoints {
  static const String devices = '\$apiPrefix/iot/devices';
  static String deviceGet(String deviceId) => '\$apiPrefix/iot/devices/$deviceId';
  static const String deviceCreate = '\$apiPrefix/iot/devices';
  static String deviceUpdate(String deviceId) => '\$apiPrefix/iot/devices/$deviceId';
  static String deviceDelete(String deviceId) => '\$apiPrefix/iot/devices/$deviceId';
  static String deviceReadings(String deviceId) => '\$apiPrefix/iot/sensors/$deviceId/readings';
  static String deviceCommand(String deviceId) => '\$apiPrefix/iot/devices/$deviceId/command';
  static const String deviceTypes = '\$apiPrefix/iot/device-types';
  static String fieldDevices(String fieldId) => '\$apiPrefix/iot/devices/field/$fieldId';
  static String fieldSensors(String fieldId) => '\$apiPrefix/iot/fields/$fieldId/sensors';
  static String sensorHistory(String sensorId) => '\$apiPrefix/iot/sensors/$sensorId/history';
  static String readingsByFarm(String farmId) => '\$apiPrefix/iot/readings/$farmId';
}

/// Virtual Sensors
abstract final class VirtualSensorEndpoints {
  static const String et0Calculate = '\$apiPrefix/virtual-sensors/et0/calculate';
  static const String etcCalculate = '\$apiPrefix/virtual-sensors/etc/calculate';
  static const String crops = '\$apiPrefix/virtual-sensors/crops';
  static String cropKc(String cropType) => '\$apiPrefix/virtual-sensors/crops/$cropType/kc';
  static const String soils = '\$apiPrefix/virtual-sensors/soils';
  static const String soilMoisture = '\$apiPrefix/virtual-sensors/soil-moisture/estimate';
  static const String irrigationMethods = '\$apiPrefix/virtual-sensors/irrigation-methods';
  static const String irrigationRecommend = '\$apiPrefix/virtual-sensors/irrigation/recommend';
  static const String irrigationQuickCheck = '\$apiPrefix/virtual-sensors/irrigation/quick-check';
}

/// Marketplace - السوق
abstract final class MarketplaceEndpoints {
  static const String listings = '\$apiPrefix/marketplace/listings';
  static const String listingCreate = '\$apiPrefix/marketplace/listings';
  static const String products = '\$apiPrefix/marketplace/products';
  static String productGet(String productId) => '\$apiPrefix/marketplace/products/$productId';
  static const String orders = '\$apiPrefix/marketplace/orders';
  static String ordersByUser(String userId) => '\$apiPrefix/marketplace/orders/user/$userId';
  static const String harvest = '\$apiPrefix/marketplace/harvest';
  static const String stats = '\$apiPrefix/marketplace/stats';
  static String wallet(String userId) => '\$apiPrefix/marketplace/fintech/wallet/$userId';
  static String walletDeposit(String walletId) => '\$apiPrefix/marketplace/fintech/wallet/$walletId/deposit';
  static String walletWithdraw(String walletId) => '\$apiPrefix/marketplace/fintech/wallet/$walletId/withdraw';
  static String walletTransactions(String walletId) => '\$apiPrefix/marketplace/fintech/wallet/$walletId/transactions';
  static const String creditScore = '\$apiPrefix/marketplace/fintech/calculate-score';
  static const String loans = '\$apiPrefix/marketplace/fintech/loans';
  static String loansByUser(String walletId) => '\$apiPrefix/marketplace/fintech/loans/$walletId';
  static String loanRepay(String loanId) => '\$apiPrefix/marketplace/fintech/loans/$loanId/repay';
}

/// Billing - الفوترة
abstract final class BillingEndpoints {
  static const String subscription = '\$apiPrefix/billing/subscription';
  static const String subscriptions = '\$apiPrefix/billing/subscriptions';
  static const String plans = '\$apiPrefix/billing/plans';
  static const String invoices = '\$apiPrefix/billing/invoices';
  static String invoiceGet(String invoiceId) => '\$apiPrefix/billing/invoices/$invoiceId';
  static String invoicePay(String invoiceId) => '\$apiPrefix/billing/invoices/$invoiceId/pay';
  static const String usage = '\$apiPrefix/billing/usage';
  static const String wallet = '\$apiPrefix/billing/wallet';
  static const String walletDeposit = '\$apiPrefix/billing/wallet/deposit';
  static const String walletWithdraw = '\$apiPrefix/billing/wallet/withdraw';
  static const String walletTransfer = '\$apiPrefix/billing/wallet/transfer';
  static const String transactions = '\$apiPrefix/billing/transactions';
  static String tenantSubscription(String tenantId) => '\$apiPrefix/billing/tenants/$tenantId/subscription';
  static String tenantInvoices(String tenantId) => '\$apiPrefix/billing/tenants/$tenantId/invoices';
  static String tenantUsage(String tenantId) => '\$apiPrefix/billing/tenants/$tenantId/usage';
}

/// Chat - الدردشة
abstract final class ChatEndpoints {
  static const String conversations = '\$apiPrefix/chat/conversations';
  static String conversationGet(String conversationId) => '\$apiPrefix/chat/conversations/$conversationId';
  static String messages(String conversationId) => '\$apiPrefix/chat/conversations/$conversationId/messages';
  static String sendMessage(String conversationId) => '\$apiPrefix/chat/conversations/$conversationId/messages';
  static String markRead(String conversationId) => '\$apiPrefix/chat/conversations/$conversationId/read';
  static const String createConversation = '\$apiPrefix/chat/conversations';
  static const String unreadCount = '\$apiPrefix/chat/conversations/unread-count';
  static String fieldMessages(String fieldId) => '\$apiPrefix/chat/fields/$fieldId/messages';
  static String fieldSend(String fieldId) => '\$apiPrefix/chat/fields/$fieldId/messages';
  static String fieldParticipants(String fieldId) => '\$apiPrefix/chat/fields/$fieldId/participants';
  static String fieldChatMessages(String fieldId) => '\$apiPrefix/field-chat/fields/$fieldId/messages';
  static String fieldChatParticipants(String fieldId) => '\$apiPrefix/field-chat/fields/$fieldId/participants';
  static const String communityPosts = '\$apiPrefix/posts';
  static String communityPostGet(String postId) => '\$apiPrefix/posts/$postId';
  static String communityComments(String postId) => '\$apiPrefix/posts/$postId/comments';
}

/// Indicators - المؤشرات
abstract final class IndicatorEndpoints {
  static const String dashboard = '\$apiPrefix/indicators/dashboard';
  static String dashboardTenant(String tenantId) => '\$apiPrefix/indicators/dashboard/$tenantId';
  static const String summary = '\$apiPrefix/indicators/summary';
  static const String trends = '\$apiPrefix/indicators/trends';
  static String field(String fieldId) => '\$apiPrefix/indicators/field/$fieldId';
  static const String definitions = '\$apiPrefix/indicators/definitions';
  static const String alerts = '\$apiPrefix/indicators/alerts';
}

/// Intelligence - الذكاء الحقلي
abstract final class IntelligenceEndpoints {
  static String fieldScore(String fieldId) => '\$apiPrefix/fields/$fieldId/intelligence/score';
  static String fieldZones(String fieldId) => '\$apiPrefix/fields/$fieldId/intelligence/zones';
  static String fieldAlerts(String fieldId) => '\$apiPrefix/fields/$fieldId/intelligence/alerts';
  static String fieldRecommendations(String fieldId) => '\$apiPrefix/fields/$fieldId/intelligence/recommendations';
  static String createTask(String alertId) => '\$apiPrefix/intelligence/alerts/$alertId/create-task';
  static const String bestDays = '\$apiPrefix/intelligence/best-days';
  static const String validateDate = '\$apiPrefix/intelligence/validate-date';
  static String fieldData(String fieldId) => '\$apiPrefix/field-intelligence/$fieldId';
}

/// Yield - الإنتاجية
abstract final class YieldEndpoints {
  static String predict(String fieldId) => '\$apiPrefix/yield/fields/$fieldId/predict';
  static String history(String fieldId) => '\$apiPrefix/yield/fields/$fieldId/history';
  static const String predictPost = '\$apiPrefix/yield/predict';
  static const String predictions = '\$apiPrefix/yield/predictions';
  static const String profitability = '\$apiPrefix/yield/profitability';
}

/// AI & Copilot
abstract final class AiEndpoints {
  static const String copilotChat = '\$apiPrefix/copilot/chat';
  static const String copilotHistory = '\$apiPrefix/copilot/chat/history';
  static const String copilotTools = '\$apiPrefix/copilot/tools';
  static String copilotExecuteTool(String toolName) => '\$apiPrefix/copilot/tools/$toolName/execute';
  static const String ragDocuments = '\$apiPrefix/copilot/rag/documents';
  static const String ragSearch = '\$apiPrefix/copilot/rag/search';
  static const String aiAdvisorQuery = '\$apiPrefix/ai-advisor/query';
  static const String aiAdvisorChat = '\$apiPrefix/ai-advisor/chat';
  static const String aiAdvisorDiagnose = '\$apiPrefix/ai-advisor/diagnose';
  static String aiAdvisorRecommendations(String fieldId) => '\$apiPrefix/ai-advisor/recommendations/$fieldId';
  static String aiAdvisorAnalyze(String fieldId) => '\$apiPrefix/ai-advisor/analyze/$fieldId';
  static const String aiAdvisorHistory = '\$apiPrefix/ai-advisor/history';
}

/// Vision - الرؤية الحاسوبية
abstract final class VisionEndpoints {
  static const String detectPest = '\$apiPrefix/vision/detect/pest';
  static const String detectDisease = '\$apiPrefix/vision/detect/disease';
  static const String detectWeed = '\$apiPrefix/vision/detect/weed';
  static const String countPlants = '\$apiPrefix/vision/count/plants';
  static const String classifyRipeness = '\$apiPrefix/vision/classify/ripeness';
  static const String segmentLeaf = '\$apiPrefix/vision/segment/leaf';
  static const String trackObjects = '\$apiPrefix/vision/track/objects';
  static String trackClear(String trackerId) => '\$apiPrefix/vision/track/$trackerId';
  static const String batchPest = '\$apiPrefix/vision/batch/detect/pest';
  static const String batchDisease = '\$apiPrefix/vision/batch/detect/disease';
  static const String batchStatus = '\$apiPrefix/vision/batch/status';
  static const String modelsList = '\$apiPrefix/vision/models/versions';
  static String modelInfo(String variant) => '\$apiPrefix/vision/models/$variant/info';
  static const String modelsWarmup = '\$apiPrefix/vision/models/warmup';
  static const String modelsLoaded = '\$apiPrefix/vision/models/loaded';
}

/// Terrain & Hydrology
abstract final class TerrainEndpoints {
  static const String dem = '\$apiPrefix/terrain/dem';
  static const String slope = '\$apiPrefix/terrain/slope';
  static const String aspect = '\$apiPrefix/terrain/aspect';
  static const String hydrologyDrainage = '\$apiPrefix/hydrology/drainage';
  static const String hydrologyWatershed = '\$apiPrefix/hydrology/watershed';
  static const String hydrologyFlow = '\$apiPrefix/hydrology/flow';
  static const String levelingOptimize = '\$apiPrefix/leveling/optimize';
  static const String levelingCutFill = '\$apiPrefix/leveling/cut-fill';
  static const String levelingCost = '\$apiPrefix/leveling/cost';
}

/// Hydrology - الهيدرولوجيا
abstract final class HydrologyEndpoints {
  static const String drainage = '\$apiPrefix/hydrology/drainage';
  static String drainageByField(String fieldId) => '\$apiPrefix/hydrology/drainage/$fieldId';
  static const String watershed = '\$apiPrefix/hydrology/watershed';
  static const String watershedDelineate = '\$apiPrefix/hydrology/watershed/delineate';
  static const String flow = '\$apiPrefix/hydrology/flow';
  static const String flowAccumulation = '\$apiPrefix/hydrology/flow/accumulation';
  static const String streamNetwork = '\$apiPrefix/hydrology/streams';
  static const String rainfallRunoff = '\$apiPrefix/hydrology/rainfall-runoff';
  static const String infiltration = '\$apiPrefix/hydrology/infiltration';
}

/// Vegetation - الغطاء النباتي
abstract final class VegetationEndpoints {
  static const String analyze = '\$apiPrefix/vegetation/analyze';
  static String ndvi(String fieldId) => '\$apiPrefix/vegetation/ndvi/$fieldId';
  static String evi(String fieldId) => '\$apiPrefix/vegetation/evi/$fieldId';
  static String savi(String fieldId) => '\$apiPrefix/vegetation/savi/$fieldId';
  static String ndwi(String fieldId) => '\$apiPrefix/vegetation/ndwi/$fieldId';
  static String lai(String fieldId) => '\$apiPrefix/vegetation/lai/$fieldId';
  static String chlorophyll(String fieldId) => '\$apiPrefix/vegetation/chlorophyll/$fieldId';
  static String timeseries(String fieldId) => '\$apiPrefix/vegetation/timeseries/$fieldId';
  static String stressMap(String fieldId) => '\$apiPrefix/vegetation/stress/$fieldId';
}

/// Users (Admin)
abstract final class UserEndpoints {
  static const String list = '\$apiPrefix/users';
  static String getUser(String userId) => '\$apiPrefix/users/$userId';
  static const String create = '\$apiPrefix/users';
  static String update(String userId) => '\$apiPrefix/users/$userId';
  static String delete(String userId) => '\$apiPrefix/users/$userId';
}

/// Audit (Admin)
abstract final class AuditEndpoints {
  static const String logs = '\$apiPrefix/audit/logs';
  static String logGet(String logId) => '\$apiPrefix/audit/logs/$logId';
  static const String stats = '\$apiPrefix/audit/stats';
  static const String adminAudit = '\$apiPrefix/admin/audit';
  static const String adminBatch = '\$apiPrefix/admin/audit/batch';
}

/// Soil - التربة
abstract final class SoilEndpoints {
  static const String tests = '\$apiPrefix/soil/tests';
  static String testGet(String testId) => '\$apiPrefix/soil/tests/$testId';
  static const String testCreate = '\$apiPrefix/soil/tests';
  static String testUpdate(String testId) => '\$apiPrefix/soil/tests/$testId';
  static String testDelete(String testId) => '\$apiPrefix/soil/tests/$testId';
  static String testsByField(String fieldId) => '\$apiPrefix/soil/fields/$fieldId/tests';
  static const String analysis = '\$apiPrefix/soil/analysis';
  static const String analysisInterpret = '\$apiPrefix/soil/analysis/interpret';
  static const String sensors = '\$apiPrefix/soil/sensors';
  static String sensorReadings(String sensorId) => '\$apiPrefix/soil/sensors/$sensorId/readings';
  static String moisture(String fieldId) => '\$apiPrefix/soil/moisture/$fieldId';
  static String salinity(String fieldId) => '\$apiPrefix/soil/salinity/$fieldId';
  static String ph(String fieldId) => '\$apiPrefix/soil/ph/$fieldId';
  static String nutrients(String fieldId) => '\$apiPrefix/soil/nutrients/$fieldId';
  static const String recommendations = '\$apiPrefix/soil/recommendations';
  static String recommendationsByField(String fieldId) => '\$apiPrefix/soil/recommendations/$fieldId';
}

/// Drone - الطائرات المسيّرة
abstract final class DroneEndpoints {
  static const String flights = '\$apiPrefix/drone/flights';
  static String flightGet(String flightId) => '\$apiPrefix/drone/flights/$flightId';
  static const String flightCreate = '\$apiPrefix/drone/flights';
  static String flightUpdate(String flightId) => '\$apiPrefix/drone/flights/$flightId';
  static String flightDelete(String flightId) => '\$apiPrefix/drone/flights/$flightId';
  static const String flightPlan = '\$apiPrefix/drone/flights/plan';
  static String flightStart(String flightId) => '\$apiPrefix/drone/flights/$flightId/start';
  static String flightPause(String flightId) => '\$apiPrefix/drone/flights/$flightId/pause';
  static String flightResume(String flightId) => '\$apiPrefix/drone/flights/$flightId/resume';
  static String flightAbort(String flightId) => '\$apiPrefix/drone/flights/$flightId/abort';
  static String flightMissions(String flightId) => '\$apiPrefix/drone/flights/$flightId/missions';
  static String flightTelemetry(String flightId) => '\$apiPrefix/drone/flights/$flightId/telemetry';
  static const String devices = '\$apiPrefix/drone/devices';
  static String deviceGet(String deviceId) => '\$apiPrefix/drone/devices/$deviceId';
  static const String deviceRegister = '\$apiPrefix/drone/devices';
  static String deviceStatus(String deviceId) => '\$apiPrefix/drone/devices/$deviceId/status';
  static const String vraApply = '\$apiPrefix/drone/vra/apply';
}

/// Inventory - المخزون
abstract final class InventoryEndpoints {
  static const String list = '\$apiPrefix/inventory';
  static String getInventory(String itemId) => '\$apiPrefix/inventory/$itemId';
  static const String create = '\$apiPrefix/inventory';
  static String update(String itemId) => '\$apiPrefix/inventory/$itemId';
  static String delete(String itemId) => '\$apiPrefix/inventory/$itemId';
  static const String stockLevels = '\$apiPrefix/inventory/stock-levels';
}

/// Traceability - التتبع
abstract final class TraceabilityEndpoints {
  static const String batches = '\$apiPrefix/traceability/batches';
  static String batchGet(String batchId) => '\$apiPrefix/traceability/batches/$batchId';
  static const String events = '\$apiPrefix/traceability/events';
  static String qrCode(String batchId) => '\$apiPrefix/traceability/batches/$batchId/qr';
}

/// Providers
abstract final class ProviderEndpoints {
  static const String list = '\$apiPrefix/providers';
  static String config(String providerId) => '\$apiPrefix/providers/$providerId/config';
  static String configUpdate(String providerId) => '\$apiPrefix/providers/$providerId/config';
}

/// Disasters - الكوارث
abstract final class DisasterEndpoints {
  static const String assess = '\$apiPrefix/disasters/assess';
  static const String alerts = '\$apiPrefix/disasters/alerts';
}

/// Agro Rules
abstract final class AgroRulesEndpoints {
  static String fieldRules(String fieldId) => '\$apiPrefix/agro-rules/fields/$fieldId/rules';
  static const String createRule = '\$apiPrefix/agro-rules/rules';
  static String triggerRule(String ruleId) => '\$apiPrefix/agro-rules/rules/$ruleId/trigger';
  static const String gdd = '\$apiPrefix/agro-rules/gdd';
  static const String sprayWindows = '\$apiPrefix/agro-rules/spray-windows';
}

/// Edge Orchestrator
abstract final class EdgeEndpoints {
  static const String devices = '\$apiPrefix/edge/devices';
  static String deviceGet(String deviceId) => '\$apiPrefix/edge/devices/$deviceId';
  static const String deviceCreate = '\$apiPrefix/edge/devices';
  static String deviceUpdate(String deviceId) => '\$apiPrefix/edge/devices/$deviceId';
  static String deviceDelete(String deviceId) => '\$apiPrefix/edge/devices/$deviceId';
  static String deviceStatus(String deviceId) => '\$apiPrefix/edge/devices/$deviceId/status';
  static const String deployModel = '\$apiPrefix/edge/deploy';
  static String deployStatus(String deploymentId) => '\$apiPrefix/edge/deploy/$deploymentId/status';
  static const String syncEdge = '\$apiPrefix/edge/sync';
  static String syncStatus(String syncId) => '\$apiPrefix/edge/sync/$syncId/status';
  static String metrics(String deviceId) => '\$apiPrefix/edge/devices/$deviceId/metrics';
}

/// Community - المجتمع
abstract final class CommunityEndpoints {
  static const String posts = '\$apiPrefix/community/posts';
  static String postGet(String postId) => '\$apiPrefix/community/posts/$postId';
  static const String postCreate = '\$apiPrefix/community/posts';
  static String postUpdate(String postId) => '\$apiPrefix/community/posts/$postId';
  static String postDelete(String postId) => '\$apiPrefix/community/posts/$postId';
  static String postLike(String postId) => '\$apiPrefix/community/posts/$postId/like';
  static String postSave(String postId) => '\$apiPrefix/community/posts/$postId/save';
  static String postShare(String postId) => '\$apiPrefix/community/posts/$postId/share';
  static String postComments(String postId) => '\$apiPrefix/community/posts/$postId/comments';
  static const String trending = '\$apiPrefix/community/posts/trending';
  static const String saved = '\$apiPrefix/community/posts/saved';
  static const String myPosts = '\$apiPrefix/community/posts/my-posts';
  static const String groups = '\$apiPrefix/community/groups';
  static String groupGet(String groupId) => '\$apiPrefix/community/groups/$groupId';
  static String groupJoin(String groupId) => '\$apiPrefix/community/groups/$groupId/join';
  static String groupLeave(String groupId) => '\$apiPrefix/community/groups/$groupId/leave';
  static String groupMembers(String groupId) => '\$apiPrefix/community/groups/$groupId/members';
  static String groupMessages(String groupId) => '\$apiPrefix/community/groups/$groupId/messages';
  static const String myGroups = '\$apiPrefix/community/groups/my-groups';
  static const String experts = '\$apiPrefix/community/experts';
  static const String expertQuestions = '\$apiPrefix/community/expert-questions';
  static String expertRate(String questionId) => '\$apiPrefix/community/expert-questions/$questionId/rate';
}

/// Dashboard - لوحة المعلومات
abstract final class DashboardEndpoints {
  static const String summary = '\$apiPrefix/dashboard/summary';
  static const String stats = '\$apiPrefix/dashboard/stats';
  static const String recentActivity = '\$apiPrefix/dashboard/recent-activity';
  static const String weatherWidget = '\$apiPrefix/dashboard/weather';
  static const String alertsWidget = '\$apiPrefix/dashboard/alerts';
}

/// Astronomical - التقويم الفلكي
abstract final class AstronomicalEndpoints {
  static const String calendar = '\$apiPrefix/astronomical/calendar';
  static const String prayerTimes = '\$apiPrefix/astronomical/prayer-times';
  static const String moonPhases = '\$apiPrefix/astronomical/moon-phases';
  static const String seasons = '\$apiPrefix/astronomical/seasons';
  static const String events = '\$apiPrefix/astronomical/events';
}

/// Farms - المزارع
abstract final class FarmEndpoints {
  static const String list = '\$apiPrefix/farms';
  static String getFarm(String farmId) => '\$apiPrefix/farms/$farmId';
  static const String create = '\$apiPrefix/farms';
  static String update(String farmId) => '\$apiPrefix/farms/$farmId';
  static String delete(String farmId) => '\$apiPrefix/farms/$farmId';
  static String stats(String farmId) => '\$apiPrefix/farms/$farmId/stats';
  static String members(String farmId) => '\$apiPrefix/farms/$farmId/members';
}

/// Seasons - المواسم
abstract final class SeasonEndpoints {
  static const String list = '\$apiPrefix/seasons';
  static String getSeason(String seasonId) => '\$apiPrefix/seasons/$seasonId';
  static const String create = '\$apiPrefix/seasons';
  static String update(String seasonId) => '\$apiPrefix/seasons/$seasonId';
  static String delete(String seasonId) => '\$apiPrefix/seasons/$seasonId';
  static const String active = '\$apiPrefix/seasons/active';
}

/// Compliance - الامتثال
abstract final class ComplianceEndpoints {
  static const String checklists = '\$apiPrefix/compliance/checklists';
  static String checklistGet(String checklistId) => '\$apiPrefix/compliance/checklists/$checklistId';
  static const String audits = '\$apiPrefix/compliance/audits';
  static const String certificates = '\$apiPrefix/compliance/certificates';
  static const String standards = '\$apiPrefix/compliance/standards';
}

/// Documents - المستندات
abstract final class DocumentEndpoints {
  static const String list = '\$apiPrefix/documents';
  static String getDocument(String documentId) => '\$apiPrefix/documents/$documentId';
  static const String upload = '\$apiPrefix/documents/upload';
  static String delete(String documentId) => '\$apiPrefix/documents/$documentId';
  static const String categories = '\$apiPrefix/documents/categories';
}

/// Logistics - اللوجستيات
abstract final class LogisticsEndpoints {
  static const String shipments = '\$apiPrefix/logistics/shipments';
  static String shipmentGet(String shipmentId) => '\$apiPrefix/logistics/shipments/$shipmentId';
  static const String shipmentCreate = '\$apiPrefix/logistics/shipments';
  static const String vehicles = '\$apiPrefix/logistics/vehicles';
  static const String routes = '\$apiPrefix/logistics/routes';
  static String tracking(String shipmentId) => '\$apiPrefix/logistics/tracking/$shipmentId';
}

/// Research - الأبحاث
abstract final class ResearchEndpoints {
  static const String trials = '\$apiPrefix/research/trials';
  static String trialGet(String trialId) => '\$apiPrefix/research/trials/$trialId';
  static const String trialCreate = '\$apiPrefix/research/trials';
  static String trialUpdate(String trialId) => '\$apiPrefix/research/trials/$trialId';
  static String observations(String trialId) => '\$apiPrefix/research/trials/$trialId/observations';
  static String analysis(String trialId) => '\$apiPrefix/research/trials/$trialId/analysis';
}

/// Scouting - الكشف
abstract final class ScoutingEndpoints {
  static const String list = '\$apiPrefix/scouting/reports';
  static String getScouting(String reportId) => '\$apiPrefix/scouting/reports/$reportId';
  static const String create = '\$apiPrefix/scouting/reports';
  static String update(String reportId) => '\$apiPrefix/scouting/reports/$reportId';
  static String delete(String reportId) => '\$apiPrefix/scouting/reports/$reportId';
  static String fieldReports(String fieldId) => '\$apiPrefix/scouting/fields/$fieldId/reports';
  static const String stats = '\$apiPrefix/scouting/stats';
}

/// VRA - التطبيق المتغير
abstract final class VraEndpoints {
  static const String maps = '\$apiPrefix/vra/maps';
  static String mapGet(String mapId) => '\$apiPrefix/vra/maps/$mapId';
  static const String mapCreate = '\$apiPrefix/vra/maps';
  static const String prescriptions = '\$apiPrefix/vra/prescriptions';
  static String prescriptionGet(String prescriptionId) => '\$apiPrefix/vra/prescriptions/$prescriptionId';
  static String zones(String fieldId) => '\$apiPrefix/vra/zones/$fieldId';
}

/// Team - الفريق
abstract final class TeamEndpoints {
  static const String members = '\$apiPrefix/team/members';
  static String memberGet(String memberId) => '\$apiPrefix/team/members/$memberId';
  static const String memberInvite = '\$apiPrefix/team/members/invite';
  static String memberRemove(String memberId) => '\$apiPrefix/team/members/$memberId';
  static String memberRole(String memberId) => '\$apiPrefix/team/members/$memberId/role';
  static const String roles = '\$apiPrefix/team/roles';
}
