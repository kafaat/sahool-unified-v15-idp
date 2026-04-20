/// SAHOOL Unified API Endpoint Paths (auto-generated)
/// DO NOT EDIT - Generated from packages/shared-types/src/contracts/api-endpoints.ts
/// Run: npx tsx scripts/sync-contracts-to-dart.ts
///
/// Contract version: 4.21.0
library;

/// API version prefix
const String apiVersion = 'v1';
const String apiPrefix = '/api/$apiVersion';

/// health
abstract final class HealthEndpoints {
  static const String liveness = '/healthz';
  static const String readiness = '/readyz';
  static const String health = '/health';
  static const String metrics = '/metrics';
}

/// service health
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

/// auth
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

/// advisory
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
  static String fertilizerUpdate(String prescriptionId) => '\$apiPrefix/advisory/fertilizer/${Uri.encodeComponent(prescriptionId)}';
  static String fertilizerZoneUpdate(String prescriptionId, String zoneId) => '\$apiPrefix/advisory/fertilizer/${Uri.encodeComponent(prescriptionId)}/zones/${Uri.encodeComponent(zoneId)}';
  static const String advice = '\$apiPrefix/advisory/advice';
  static const String disease = '\$apiPrefix/advisory/disease';
  static const String nutrients = '\$apiPrefix/advisory/nutrients';
  static const String agroAdvice = '\$apiPrefix/agro-advisor/advice';
  static const String agroDisease = '\$apiPrefix/agro-advisor/disease';
  static const String agroNutrients = '\$apiPrefix/agro-advisor/nutrients';
  static String comprehensive(String fieldId) => '\$apiPrefix/advisory/comprehensive/${Uri.encodeComponent(fieldId)}';
  static String recommendationsByField(String fieldId) => '\$apiPrefix/advisory/recommendations/${Uri.encodeComponent(fieldId)}';
  static String diseaseAssess(String fieldId) => '\$apiPrefix/advisory/disease-assess/${Uri.encodeComponent(fieldId)}';
  static String fertilizerPlan(String fieldId) => '\$apiPrefix/advisory/fertilizer-plan/${Uri.encodeComponent(fieldId)}';
  static String cropAdvice(String fieldId) => '\$apiPrefix/advisory/crop-advice/${Uri.encodeComponent(fieldId)}';
  static const String sprayWindows = '\$apiPrefix/advisory/spray-windows';
  static const String sprayHistory = '\$apiPrefix/advisory/spray-history';
}

/// agri calendar
abstract final class AgriCalendarEndpoints {
  static const String events = '\$apiPrefix/agri-calendar/events';
  static const String plantingTimes = '\$apiPrefix/agri-calendar/planting-times';
  static const String harvestTimes = '\$apiPrefix/agri-calendar/harvest-times';
}

/// agro rules
abstract final class AgroRulesEndpoints {
  static String fieldRules(String fieldId) => '\$apiPrefix/agro-rules/fields/${Uri.encodeComponent(fieldId)}/rules';
  static const String createRule = '\$apiPrefix/agro-rules/rules';
  static String triggerRule(String ruleId) => '\$apiPrefix/agro-rules/rules/${Uri.encodeComponent(ruleId)}/trigger';
  static const String gdd = '\$apiPrefix/agro-rules/gdd';
  static const String sprayWindows = '\$apiPrefix/agro-rules/spray-windows';
}

/// ai
abstract final class AiEndpoints {
  static const String copilotChat = '\$apiPrefix/copilot/chat';
  static const String copilotChatDirect = '\$apiPrefix/chat';
  static const String copilotChatStreamDirect = '\$apiPrefix/chat/stream';
  static const String copilotHistory = '\$apiPrefix/copilot/chat/history';
  static const String copilotTools = '\$apiPrefix/copilot/tools';
  static String copilotExecuteTool(String toolName) => '\$apiPrefix/copilot/tools/${Uri.encodeComponent(toolName)}/execute';
  static const String ragDocuments = '\$apiPrefix/copilot/rag/documents';
  static const String ragSearch = '\$apiPrefix/copilot/rag/search';
  static const String aiAdvisorQuery = '\$apiPrefix/ai-advisor/query';
  static const String aiAdvisorChat = '\$apiPrefix/ai-advisor/chat';
  static const String aiAdvisorDiagnose = '\$apiPrefix/ai-advisor/diagnose';
  static String aiAdvisorRecommendations(String fieldId) => '\$apiPrefix/ai-advisor/recommendations/${Uri.encodeComponent(fieldId)}';
  static String aiAdvisorAnalyze(String fieldId) => '\$apiPrefix/ai-advisor/analyze/${Uri.encodeComponent(fieldId)}';
  static const String aiAdvisorHistory = '\$apiPrefix/ai-advisor/history';
}

/// alert
abstract final class AlertEndpoints {
  static const String list = '\$apiPrefix/alerts';
  static String getAlert(String alertId) => '\$apiPrefix/alerts/${Uri.encodeComponent(alertId)}';
  static const String create = '\$apiPrefix/alerts';
  static String delete(String alertId) => '\$apiPrefix/alerts/${Uri.encodeComponent(alertId)}';
  static String acknowledge(String alertId) => '\$apiPrefix/alerts/${Uri.encodeComponent(alertId)}/acknowledge';
  static String resolve(String alertId) => '\$apiPrefix/alerts/${Uri.encodeComponent(alertId)}/resolve';
  static String dismiss(String alertId) => '\$apiPrefix/alerts/${Uri.encodeComponent(alertId)}/dismiss';
  static const String rules = '\$apiPrefix/alerts/rules';
}

/// astronomical
abstract final class AstronomicalEndpoints {
  static const String calendar = '\$apiPrefix/astronomy/calendar';
  static const String prayerTimes = '\$apiPrefix/astronomy/prayer-times';
  static const String moonPhases = '\$apiPrefix/astronomy/moon-phases';
  static const String seasons = '\$apiPrefix/astronomy/seasons';
  static const String events = '\$apiPrefix/astronomy/events';
}

/// audit
abstract final class AuditEndpoints {
  static const String logs = '\$apiPrefix/audit/logs';
  static String logGet(String logId) => '\$apiPrefix/audit/logs/${Uri.encodeComponent(logId)}';
  static const String stats = '\$apiPrefix/audit/stats';
  static const String adminAudit = '\$apiPrefix/admin/audit';
  static const String adminBatch = '\$apiPrefix/admin/audit/batch';
  static String resourceTrail(String resourceType, String resourceId) => '\$apiPrefix/audit/resources/${Uri.encodeComponent(resourceType)}/${Uri.encodeComponent(resourceId)}/trail';
  static String userTrail(String userId) => '\$apiPrefix/audit/users/${Uri.encodeComponent(userId)}/trail';
  static const String chainValidate = '\$apiPrefix/audit/chain/validate';
}

/// billing
abstract final class BillingEndpoints {
  static const String subscription = '\$apiPrefix/billing/subscription';
  static const String subscriptions = '\$apiPrefix/billing/subscriptions';
  static const String plans = '\$apiPrefix/billing/plans';
  static const String invoices = '\$apiPrefix/billing/invoices';
  static String invoiceGet(String invoiceId) => '\$apiPrefix/billing/invoices/${Uri.encodeComponent(invoiceId)}';
  static String invoicePay(String invoiceId) => '\$apiPrefix/billing/invoices/${Uri.encodeComponent(invoiceId)}/pay';
  static const String usage = '\$apiPrefix/billing/usage';
  static const String wallet = '\$apiPrefix/billing/wallet';
  static const String walletDeposit = '\$apiPrefix/billing/wallet/deposit';
  static const String walletWithdraw = '\$apiPrefix/billing/wallet/withdraw';
  static const String walletTransfer = '\$apiPrefix/billing/wallet/transfer';
  static const String transactions = '\$apiPrefix/billing/transactions';
  static String tenantSubscription(String tenantId) => '\$apiPrefix/billing/tenants/${Uri.encodeComponent(tenantId)}/subscription';
  static String tenantInvoices(String tenantId) => '\$apiPrefix/billing/tenants/${Uri.encodeComponent(tenantId)}/invoices';
  static String tenantUsage(String tenantId) => '\$apiPrefix/billing/tenants/${Uri.encodeComponent(tenantId)}/usage';
  static const String deposit = '\$apiPrefix/billing/deposit';
  static const String withdraw = '\$apiPrefix/billing/withdraw';
  static const String transfer = '\$apiPrefix/billing/transfer';
  static const String payments = '\$apiPrefix/billing/payments';
  static String invoicePaymentIntent(String invoiceId) => '\$apiPrefix/billing/invoices/${Uri.encodeComponent(invoiceId)}/payment-intent';
  static const String stripeConfig = '\$apiPrefix/billing/stripe/config';
  static const String stripePaymentIntents = '\$apiPrefix/billing/stripe/payment-intents';
  static String stripePaymentIntentConfirm(String paymentIntentId) => '\$apiPrefix/billing/stripe/payment-intents/${Uri.encodeComponent(paymentIntentId)}/confirm';
  static const String stripeSetupIntents = '\$apiPrefix/billing/stripe/setup-intents';
  static String stripeSetupIntentConfirm(String setupIntentId) => '\$apiPrefix/billing/stripe/setup-intents/${Uri.encodeComponent(setupIntentId)}/confirm';
  static const String paymentMethods = '\$apiPrefix/billing/payment-methods';
  static String paymentMethodGet(String paymentMethodId) => '\$apiPrefix/billing/payment-methods/${Uri.encodeComponent(paymentMethodId)}';
  static String paymentMethodDefault(String paymentMethodId) => '\$apiPrefix/billing/payment-methods/${Uri.encodeComponent(paymentMethodId)}/default';
}

/// carbon
abstract final class CarbonEndpoints {
  static const String compute = '\$apiPrefix/carbon/compute';
  static String computeOperation(String operationId) => '\$apiPrefix/carbon/operations/${Uri.encodeComponent(operationId)}/compute';
  static String fieldSummary(String fieldId) => '\$apiPrefix/carbon/fields/${Uri.encodeComponent(fieldId)}/summary';
  static String cropSeasonSummary(String cropSeasonId) => '\$apiPrefix/carbon/crop-seasons/${Uri.encodeComponent(cropSeasonId)}/summary';
}

/// chat
abstract final class ChatEndpoints {
  static const String conversations = '\$apiPrefix/chat/conversations';
  static String conversationGet(String conversationId) => '\$apiPrefix/chat/conversations/${Uri.encodeComponent(conversationId)}';
  static String messages(String conversationId) => '\$apiPrefix/chat/conversations/${Uri.encodeComponent(conversationId)}/messages';
  static String sendMessage(String conversationId) => '\$apiPrefix/chat/conversations/${Uri.encodeComponent(conversationId)}/messages';
  static String markRead(String conversationId) => '\$apiPrefix/chat/conversations/${Uri.encodeComponent(conversationId)}/read';
  static const String createConversation = '\$apiPrefix/chat/conversations';
  static const String unreadCount = '\$apiPrefix/chat/conversations/unread-count';
  static String fieldMessages(String fieldId) => '\$apiPrefix/field-chat/fields/${Uri.encodeComponent(fieldId)}/messages';
  static String fieldSend(String fieldId) => '\$apiPrefix/field-chat/fields/${Uri.encodeComponent(fieldId)}/messages';
  static String fieldParticipants(String fieldId) => '\$apiPrefix/field-chat/fields/${Uri.encodeComponent(fieldId)}/participants';
  static String fieldMessagesV2(String fieldId) => '\$apiPrefix/chat/fields/${Uri.encodeComponent(fieldId)}/messages';
  static String fieldSendV2(String fieldId) => '\$apiPrefix/chat/fields/${Uri.encodeComponent(fieldId)}/messages';
  static String fieldParticipantsV2(String fieldId) => '\$apiPrefix/chat/fields/${Uri.encodeComponent(fieldId)}/participants';
  static const String communityPosts = '\$apiPrefix/posts';
  static String communityPostGet(String postId) => '\$apiPrefix/posts/${Uri.encodeComponent(postId)}';
  static String communityComments(String postId) => '\$apiPrefix/posts/${Uri.encodeComponent(postId)}/comments';
  static String mute(String conversationId) => '\$apiPrefix/chat/conversations/${Uri.encodeComponent(conversationId)}/mute';
  static String report(String conversationId) => '\$apiPrefix/chat/conversations/${Uri.encodeComponent(conversationId)}/report';
  static String clearMessages(String conversationId) => '\$apiPrefix/chat/conversations/${Uri.encodeComponent(conversationId)}/messages';
}

/// community
abstract final class CommunityEndpoints {
  static const String posts = '\$apiPrefix/community/posts';
  static String postGet(String postId) => '\$apiPrefix/community/posts/${Uri.encodeComponent(postId)}';
  static const String postCreate = '\$apiPrefix/community/posts';
  static String postUpdate(String postId) => '\$apiPrefix/community/posts/${Uri.encodeComponent(postId)}';
  static String postDelete(String postId) => '\$apiPrefix/community/posts/${Uri.encodeComponent(postId)}';
  static String postLike(String postId) => '\$apiPrefix/community/posts/${Uri.encodeComponent(postId)}/like';
  static String postSave(String postId) => '\$apiPrefix/community/posts/${Uri.encodeComponent(postId)}/save';
  static String postShare(String postId) => '\$apiPrefix/community/posts/${Uri.encodeComponent(postId)}/share';
  static String postComments(String postId) => '\$apiPrefix/community/posts/${Uri.encodeComponent(postId)}/comments';
  static const String trending = '\$apiPrefix/community/posts/trending';
  static const String saved = '\$apiPrefix/community/posts/saved';
  static const String myPosts = '\$apiPrefix/community/posts/my-posts';
  static const String groups = '\$apiPrefix/community/groups';
  static String groupGet(String groupId) => '\$apiPrefix/community/groups/${Uri.encodeComponent(groupId)}';
  static String groupJoin(String groupId) => '\$apiPrefix/community/groups/${Uri.encodeComponent(groupId)}/join';
  static String groupLeave(String groupId) => '\$apiPrefix/community/groups/${Uri.encodeComponent(groupId)}/leave';
  static String groupMembers(String groupId) => '\$apiPrefix/community/groups/${Uri.encodeComponent(groupId)}/members';
  static String groupMessages(String groupId) => '\$apiPrefix/community/groups/${Uri.encodeComponent(groupId)}/messages';
  static const String myGroups = '\$apiPrefix/community/groups/my-groups';
  static const String experts = '\$apiPrefix/community/experts';
  static const String expertQuestions = '\$apiPrefix/community/expert-questions';
  static String expertRate(String questionId) => '\$apiPrefix/community/expert-questions/${Uri.encodeComponent(questionId)}/rate';
}

/// compliance
abstract final class ComplianceEndpoints {
  static const String checklists = '\$apiPrefix/compliance/checklists';
  static String checklistGet(String checklistId) => '\$apiPrefix/compliance/checklists/${Uri.encodeComponent(checklistId)}';
  static const String audits = '\$apiPrefix/compliance/audits';
  static const String certificates = '\$apiPrefix/compliance/certificates';
  static const String standards = '\$apiPrefix/compliance/standards';
}

/// cooperative
abstract final class CooperativeEndpoints {
  static const String bookings = '\$apiPrefix/cooperatives/bookings';
  static const String purchaseOrders = '\$apiPrefix/cooperatives/purchase-orders';
  static const String revenue = '\$apiPrefix/cooperatives/revenue';
  static const String revenueCalculate = '\$apiPrefix/cooperatives/revenue/calculate';
}

/// crop
abstract final class CropEndpoints {
  static const String list = '\$apiPrefix/crops';
  static String getCrop(String cropId) => '\$apiPrefix/crops/${Uri.encodeComponent(cropId)}';
  static const String create = '\$apiPrefix/crops';
  static String update(String cropId) => '\$apiPrefix/crops/${Uri.encodeComponent(cropId)}';
  static String delete(String cropId) => '\$apiPrefix/crops/${Uri.encodeComponent(cropId)}';
  static const String stats = '\$apiPrefix/crops/stats';
}

/// crop health
abstract final class CropHealthEndpoints {
  static const String analyze = '\$apiPrefix/crop-health/analyze';
  static const String diagnose = '\$apiPrefix/crop-health/diagnose';
  static const String diagnoseBatch = '\$apiPrefix/crop-health/diagnose/batch';
  static const String decision = '\$apiPrefix/crop-health/decision';
  static String history(String fieldId) => '\$apiPrefix/crop-health/fields/${Uri.encodeComponent(fieldId)}/history';
  static const String intelligenceAnalyze = '\$apiPrefix/crop-intelligence/analyze';
  static const String intelligenceDecision = '\$apiPrefix/crop-intelligence/decision';
  static String intelligenceHistory(String fieldId) => '\$apiPrefix/crop-intelligence/fields/${Uri.encodeComponent(fieldId)}/history';
  static const String crops = '\$apiPrefix/crop-health/crops';
  static const String diseases = '\$apiPrefix/crop-health/diseases';
  static String treatment(String diseaseId) => '\$apiPrefix/crop-health/treatment/${Uri.encodeComponent(diseaseId)}';
  static const String expertReview = '\$apiPrefix/crop-health/expert-review';
  static const String diagnosesList = '\$apiPrefix/crop-health/diagnoses';
  static const String diagnosesStats = '\$apiPrefix/crop-health/diagnoses/stats';
  static String diagnosesUpdate(String diagnosisId) => '\$apiPrefix/crop-health/diagnoses/${Uri.encodeComponent(diagnosisId)}';
}

/// crop planning
abstract final class CropPlanningEndpoints {
  static const String plans = '\$apiPrefix/crop-planning/plans';
  static String planById(String planId) => '\$apiPrefix/crop-planning/plans/${Uri.encodeComponent(planId)}';
  static const String recommendations = '\$apiPrefix/crop-planning/recommendations';
}

/// crop rotation
abstract final class CropRotationEndpoints {
  static const String plans = '\$apiPrefix/crop-rotation/plans';
  static const String recommend = '\$apiPrefix/crop-rotation/recommend';
  static const String multiYearPlan = '\$apiPrefix/crop-rotation/multi-year-plan';
  static String history(String fieldId) => '\$apiPrefix/crop-rotation/history/${Uri.encodeComponent(fieldId)}';
  static const String pestBreak = '\$apiPrefix/crop-rotation/pest-break';
  static const String soilHealth = '\$apiPrefix/crop-rotation/soil-health';
  static const String stats = '\$apiPrefix/crop-rotation/stats';
}

/// crop season
abstract final class CropSeasonEndpoints {
  static const String list = '\$apiPrefix/crop-seasons';
  static String getCropSeason(String cropSeasonId) => '\$apiPrefix/crop-seasons/${Uri.encodeComponent(cropSeasonId)}';
  static String update(String cropSeasonId) => '\$apiPrefix/crop-seasons/${Uri.encodeComponent(cropSeasonId)}';
  static String end(String cropSeasonId) => '\$apiPrefix/crop-seasons/${Uri.encodeComponent(cropSeasonId)}/end';
  static String delete(String cropSeasonId) => '\$apiPrefix/crop-seasons/${Uri.encodeComponent(cropSeasonId)}';
  static String listByField(String fieldId) => '\$apiPrefix/fields/${Uri.encodeComponent(fieldId)}/crop-seasons';
  static String create(String fieldId) => '\$apiPrefix/fields/${Uri.encodeComponent(fieldId)}/crop-seasons';
  static String rollup(String cropSeasonId) => '\$apiPrefix/crop-seasons/${Uri.encodeComponent(cropSeasonId)}/rollup';
}

/// dashboard
abstract final class DashboardEndpoints {
  static const String summary = '\$apiPrefix/dashboard/summary';
  static const String stats = '\$apiPrefix/dashboard/stats';
  static const String recentActivity = '\$apiPrefix/dashboard/recent-activity';
  static const String weatherWidget = '\$apiPrefix/dashboard/weather';
  static const String alertsWidget = '\$apiPrefix/dashboard/alerts';
}

/// disaster
abstract final class DisasterEndpoints {
  static const String assess = '\$apiPrefix/disasters/assess';
  static const String alerts = '\$apiPrefix/disasters/alerts';
  static const String assessSingular = '\$apiPrefix/disaster/assess';
  static const String alertsSingular = '\$apiPrefix/disaster/alerts';
  static const String events = '\$apiPrefix/disasters/events';
  static String eventById(String eventId) => '\$apiPrefix/disasters/events/${Uri.encodeComponent(eventId)}';
  static const String stats = '\$apiPrefix/disasters/stats/summary';
  static const String risks = '\$apiPrefix/disasters/risks';
}

/// document
abstract final class DocumentEndpoints {
  static const String list = '\$apiPrefix/documents';
  static String getDocument(String documentId) => '\$apiPrefix/documents/${Uri.encodeComponent(documentId)}';
  static const String upload = '\$apiPrefix/documents/upload';
  static String delete(String documentId) => '\$apiPrefix/documents/${Uri.encodeComponent(documentId)}';
  static const String categories = '\$apiPrefix/documents/categories';
}

/// drone
abstract final class DroneEndpoints {
  static const String flights = '\$apiPrefix/drone/flights';
  static String flightGet(String flightId) => '\$apiPrefix/drone/flights/${Uri.encodeComponent(flightId)}';
  static const String flightCreate = '\$apiPrefix/drone/flights';
  static String flightUpdate(String flightId) => '\$apiPrefix/drone/flights/${Uri.encodeComponent(flightId)}';
  static String flightDelete(String flightId) => '\$apiPrefix/drone/flights/${Uri.encodeComponent(flightId)}';
  static const String flightPlan = '\$apiPrefix/drone/flights/plan';
  static String flightStart(String flightId) => '\$apiPrefix/drone/flights/${Uri.encodeComponent(flightId)}/start';
  static String flightPause(String flightId) => '\$apiPrefix/drone/flights/${Uri.encodeComponent(flightId)}/pause';
  static String flightResume(String flightId) => '\$apiPrefix/drone/flights/${Uri.encodeComponent(flightId)}/resume';
  static String flightAbort(String flightId) => '\$apiPrefix/drone/flights/${Uri.encodeComponent(flightId)}/abort';
  static String flightMissions(String flightId) => '\$apiPrefix/drone/flights/${Uri.encodeComponent(flightId)}/missions';
  static String flightTelemetry(String flightId) => '\$apiPrefix/drone/flights/${Uri.encodeComponent(flightId)}/telemetry';
  static const String devices = '\$apiPrefix/drone/devices';
  static String deviceGet(String deviceId) => '\$apiPrefix/drone/devices/${Uri.encodeComponent(deviceId)}';
  static const String deviceRegister = '\$apiPrefix/drone/devices';
  static String deviceStatus(String deviceId) => '\$apiPrefix/drone/devices/${Uri.encodeComponent(deviceId)}/status';
  static const String vraApply = '\$apiPrefix/drone/vra/apply';
}

/// edge
abstract final class EdgeEndpoints {
  static const String devices = '\$apiPrefix/edge/devices';
  static String deviceGet(String deviceId) => '\$apiPrefix/edge/devices/${Uri.encodeComponent(deviceId)}';
  static const String deviceCreate = '\$apiPrefix/edge/devices';
  static String deviceUpdate(String deviceId) => '\$apiPrefix/edge/devices/${Uri.encodeComponent(deviceId)}';
  static String deviceDelete(String deviceId) => '\$apiPrefix/edge/devices/${Uri.encodeComponent(deviceId)}';
  static String deviceStatus(String deviceId) => '\$apiPrefix/edge/devices/${Uri.encodeComponent(deviceId)}/status';
  static const String deployModel = '\$apiPrefix/edge/deploy';
  static String deployStatus(String deploymentId) => '\$apiPrefix/edge/deploy/${Uri.encodeComponent(deploymentId)}/status';
  static const String syncEdge = '\$apiPrefix/edge/sync';
  static String syncStatus(String syncId) => '\$apiPrefix/edge/sync/${Uri.encodeComponent(syncId)}/status';
  static String metrics(String deviceId) => '\$apiPrefix/edge/devices/${Uri.encodeComponent(deviceId)}/metrics';
}

/// epidemic
abstract final class EpidemicEndpoints {
  static const String list = '\$apiPrefix/epidemics';
  static String getEpidemic(String epidemicId) => '\$apiPrefix/epidemics/${Uri.encodeComponent(epidemicId)}';
  static const String report = '\$apiPrefix/epidemics/report';
}

/// equipment
abstract final class EquipmentEndpoints {
  static const String list = '\$apiPrefix/equipment';
  static String getEquipment(String equipmentId) => '\$apiPrefix/equipment/${Uri.encodeComponent(equipmentId)}';
  static const String create = '\$apiPrefix/equipment';
  static String update(String equipmentId) => '\$apiPrefix/equipment/${Uri.encodeComponent(equipmentId)}';
  static String delete(String equipmentId) => '\$apiPrefix/equipment/${Uri.encodeComponent(equipmentId)}';
  static String status(String equipmentId) => '\$apiPrefix/equipment/${Uri.encodeComponent(equipmentId)}/status';
  static String maintenance(String equipmentId) => '\$apiPrefix/equipment/${Uri.encodeComponent(equipmentId)}/maintenance';
  static String qrLookup(String qrCode) => '\$apiPrefix/equipment/qr/${Uri.encodeComponent(qrCode)}';
  static const String stats = '\$apiPrefix/equipment/stats';
  static const String maintenanceAlerts = '\$apiPrefix/equipment/maintenance/alerts';
  static const String geofenceEvent = '\$apiPrefix/equipment/geofence/event';
  static const String maintenanceSchedule = '\$apiPrefix/equipment/maintenance-schedule';
  static String maintenanceScheduleById(String equipmentId) => '\$apiPrefix/equipment/${Uri.encodeComponent(equipmentId)}/maintenance-schedule';
  static String issues(String equipmentId) => '\$apiPrefix/equipment/${Uri.encodeComponent(equipmentId)}/issues';
  static const String alerts = '\$apiPrefix/equipment/alerts';
  static String location(String equipmentId) => '\$apiPrefix/equipment/${Uri.encodeComponent(equipmentId)}/location';
  static String telemetry(String equipmentId) => '\$apiPrefix/equipment/${Uri.encodeComponent(equipmentId)}/telemetry';
  static String fuel(String equipmentId) => '\$apiPrefix/equipment/${Uri.encodeComponent(equipmentId)}/fuel';
  static String fuelSummary(String equipmentId) => '\$apiPrefix/equipment/${Uri.encodeComponent(equipmentId)}/fuel/summary';
  static String usage(String equipmentId) => '\$apiPrefix/equipment/${Uri.encodeComponent(equipmentId)}/usage';
  static String usageStart(String equipmentId) => '\$apiPrefix/equipment/${Uri.encodeComponent(equipmentId)}/usage/start';
  static String usageEnd(String equipmentId, String logId) => '\$apiPrefix/equipment/${Uri.encodeComponent(equipmentId)}/usage/${Uri.encodeComponent(logId)}/end';
  static String usageSummary(String equipmentId) => '\$apiPrefix/equipment/${Uri.encodeComponent(equipmentId)}/usage/summary';
}

/// erp sync
abstract final class ErpSyncEndpoints {
  static String postFieldOperation(String operationId) => '\$apiPrefix/erp-sync/field-operations/${Uri.encodeComponent(operationId)}/post';
  static const String health = '\$apiPrefix/erp-sync/health';
}

/// export
abstract final class ExportEndpoints {
  static const String create = '\$apiPrefix/exports';
  static String status(String exportId) => '\$apiPrefix/exports/${Uri.encodeComponent(exportId)}/status';
  static String contents(String exportId) => '\$apiPrefix/exports/${Uri.encodeComponent(exportId)}/contents';
}

/// farm
abstract final class FarmEndpoints {
  static const String list = '\$apiPrefix/farms';
  static String getFarm(String farmId) => '\$apiPrefix/farms/${Uri.encodeComponent(farmId)}';
  static const String create = '\$apiPrefix/farms';
  static String update(String farmId) => '\$apiPrefix/farms/${Uri.encodeComponent(farmId)}';
  static String delete(String farmId) => '\$apiPrefix/farms/${Uri.encodeComponent(farmId)}';
  static String stats(String farmId) => '\$apiPrefix/farms/${Uri.encodeComponent(farmId)}/stats';
  static String members(String farmId) => '\$apiPrefix/farms/${Uri.encodeComponent(farmId)}/members';
  static String statsByTenant(String tenantId) => '\$apiPrefix/farms/stats/${Uri.encodeComponent(tenantId)}';
}

/// field
abstract final class FieldEndpoints {
  static const String list = '\$apiPrefix/fields';
  static String getField(String fieldId) => '\$apiPrefix/fields/${Uri.encodeComponent(fieldId)}';
  static const String create = '\$apiPrefix/fields';
  static String update(String fieldId) => '\$apiPrefix/fields/${Uri.encodeComponent(fieldId)}';
  static String delete(String fieldId) => '\$apiPrefix/fields/${Uri.encodeComponent(fieldId)}';
  static const String nearby = '\$apiPrefix/fields/nearby';
  static const String syncField = '\$apiPrefix/fields/sync';
  static const String syncBatch = '\$apiPrefix/fields/sync/batch';
  static String boundary(String fieldId) => '\$apiPrefix/fields/${Uri.encodeComponent(fieldId)}/boundary';
  static String boundaryUpdate(String fieldId) => '\$apiPrefix/fields/${Uri.encodeComponent(fieldId)}/boundary';
  static String boundaryHistory(String fieldId) => '\$apiPrefix/fields/${Uri.encodeComponent(fieldId)}/boundary-history';
  static String boundaryRollback(String fieldId) => '\$apiPrefix/fields/${Uri.encodeComponent(fieldId)}/boundary-history/rollback';
  static String kpiSnapshot(String fieldId) => '\$apiPrefix/fields/${Uri.encodeComponent(fieldId)}/kpi-snapshot';
}

/// field operation
abstract final class FieldOperationEndpoints {
  static const String list = '\$apiPrefix/field-operations';
  static String getFieldOperation(String operationId) => '\$apiPrefix/field-operations/${Uri.encodeComponent(operationId)}';
  static String update(String operationId) => '\$apiPrefix/field-operations/${Uri.encodeComponent(operationId)}';
  static String delete(String operationId) => '\$apiPrefix/field-operations/${Uri.encodeComponent(operationId)}';
  static String listByField(String fieldId) => '\$apiPrefix/fields/${Uri.encodeComponent(fieldId)}/operations';
  static String create(String fieldId) => '\$apiPrefix/fields/${Uri.encodeComponent(fieldId)}/operations';
  static String approve(String operationId) => '\$apiPrefix/field-operations/${Uri.encodeComponent(operationId)}/approve';
  static String reject(String operationId) => '\$apiPrefix/field-operations/${Uri.encodeComponent(operationId)}/reject';
}

/// field report
abstract final class FieldReportEndpoints {
  static String create(String fieldId) => '\$apiPrefix/fields/${Uri.encodeComponent(fieldId)}/reports';
  static String listByField(String fieldId) => '\$apiPrefix/fields/${Uri.encodeComponent(fieldId)}/reports';
  static String getFieldReport(String reportId) => '\$apiPrefix/field-reports/${Uri.encodeComponent(reportId)}';
  static String getContent(String reportId) => '\$apiPrefix/field-reports/${Uri.encodeComponent(reportId)}/content';
}

/// field sub zone
abstract final class FieldSubZoneEndpoints {
  static String listByField(String fieldId) => '\$apiPrefix/fields/${Uri.encodeComponent(fieldId)}/sub-zones';
  static String create(String fieldId) => '\$apiPrefix/fields/${Uri.encodeComponent(fieldId)}/sub-zones';
  static String getFieldSubZone(String subZoneId) => '\$apiPrefix/field-sub-zones/${Uri.encodeComponent(subZoneId)}';
  static String update(String subZoneId) => '\$apiPrefix/field-sub-zones/${Uri.encodeComponent(subZoneId)}';
  static String delete(String subZoneId) => '\$apiPrefix/field-sub-zones/${Uri.encodeComponent(subZoneId)}';
}

/// gamification
abstract final class GamificationEndpoints {
  static String profile(String userId) => '\$apiPrefix/gamification/profile/${Uri.encodeComponent(userId)}';
  static const String leaderboard = '\$apiPrefix/gamification/leaderboard';
}

/// gdd
abstract final class GddEndpoints {
  static String accumulation(String fieldId) => '\$apiPrefix/gdd/fields/${Uri.encodeComponent(fieldId)}/accumulation';
  static String records(String fieldId) => '\$apiPrefix/gdd/fields/${Uri.encodeComponent(fieldId)}/records';
  static String calculate(String fieldId) => '\$apiPrefix/gdd/fields/${Uri.encodeComponent(fieldId)}/calculate';
  static String currentStage(String fieldId) => '\$apiPrefix/gdd/fields/${Uri.encodeComponent(fieldId)}/current-stage';
  static String stages(String fieldId) => '\$apiPrefix/gdd/fields/${Uri.encodeComponent(fieldId)}/stages';
  static const String crops = '\$apiPrefix/gdd/crops';
  static String cropRequirements(String cropType) => '\$apiPrefix/gdd/crops/${Uri.encodeComponent(cropType)}/requirements';
  static String forecast(String fieldId) => '\$apiPrefix/gdd/fields/${Uri.encodeComponent(fieldId)}/forecast';
  static String settings(String fieldId) => '\$apiPrefix/gdd/fields/${Uri.encodeComponent(fieldId)}/settings';
  static String compare(String fieldId) => '\$apiPrefix/gdd/fields/${Uri.encodeComponent(fieldId)}/compare';
  static String trend(String fieldId) => '\$apiPrefix/gdd/fields/${Uri.encodeComponent(fieldId)}/trend';
}

/// hydrology
abstract final class HydrologyEndpoints {
  static const String drainage = '\$apiPrefix/hydrology/drainage';
  static String drainageByField(String fieldId) => '\$apiPrefix/hydrology/drainage/${Uri.encodeComponent(fieldId)}';
  static const String watershed = '\$apiPrefix/hydrology/watershed';
  static const String watershedDelineate = '\$apiPrefix/hydrology/watershed/delineate';
  static const String flow = '\$apiPrefix/hydrology/flow';
  static const String flowAccumulation = '\$apiPrefix/hydrology/flow/accumulation';
  static const String streamNetwork = '\$apiPrefix/hydrology/streams';
  static const String rainfallRunoff = '\$apiPrefix/hydrology/rainfall-runoff';
  static const String infiltration = '\$apiPrefix/hydrology/infiltration';
}

/// indicator
abstract final class IndicatorEndpoints {
  static const String dashboard = '\$apiPrefix/indicators/dashboard';
  static String dashboardTenant(String tenantId) => '\$apiPrefix/indicators/dashboard/${Uri.encodeComponent(tenantId)}';
  static const String summary = '\$apiPrefix/indicators/summary';
  static const String trends = '\$apiPrefix/indicators/trends';
  static String field(String fieldId) => '\$apiPrefix/indicators/field/${Uri.encodeComponent(fieldId)}';
  static const String definitions = '\$apiPrefix/indicators/definitions';
  static const String alerts = '\$apiPrefix/indicators/alerts';
}

/// intelligence
abstract final class IntelligenceEndpoints {
  static String fieldScore(String fieldId) => '\$apiPrefix/fields/${Uri.encodeComponent(fieldId)}/intelligence/score';
  static String fieldZones(String fieldId) => '\$apiPrefix/fields/${Uri.encodeComponent(fieldId)}/intelligence/zones';
  static String fieldAlerts(String fieldId) => '\$apiPrefix/fields/${Uri.encodeComponent(fieldId)}/intelligence/alerts';
  static String fieldRecommendations(String fieldId) => '\$apiPrefix/fields/${Uri.encodeComponent(fieldId)}/intelligence/recommendations';
  static String createTask(String alertId) => '\$apiPrefix/intelligence/alerts/${Uri.encodeComponent(alertId)}/create-task';
  static const String bestDays = '\$apiPrefix/intelligence/best-days';
  static const String validateDate = '\$apiPrefix/intelligence/validate-date';
  static String fieldData(String fieldId) => '\$apiPrefix/field-intelligence/${Uri.encodeComponent(fieldId)}';
}

/// inventory
abstract final class InventoryEndpoints {
  static const String list = '\$apiPrefix/inventory';
  static String getInventory(String itemId) => '\$apiPrefix/inventory/${Uri.encodeComponent(itemId)}';
  static const String create = '\$apiPrefix/inventory';
  static String update(String itemId) => '\$apiPrefix/inventory/${Uri.encodeComponent(itemId)}';
  static String delete(String itemId) => '\$apiPrefix/inventory/${Uri.encodeComponent(itemId)}';
  static const String stockLevels = '\$apiPrefix/inventory/stock-levels';
}

/// iot
abstract final class IotEndpoints {
  static const String devices = '\$apiPrefix/iot/devices';
  static String deviceGet(String deviceId) => '\$apiPrefix/iot/devices/${Uri.encodeComponent(deviceId)}';
  static const String deviceCreate = '\$apiPrefix/iot/devices';
  static String deviceUpdate(String deviceId) => '\$apiPrefix/iot/devices/${Uri.encodeComponent(deviceId)}';
  static String deviceDelete(String deviceId) => '\$apiPrefix/iot/devices/${Uri.encodeComponent(deviceId)}';
  static String deviceReadings(String deviceId) => '\$apiPrefix/iot/sensors/${Uri.encodeComponent(deviceId)}/readings';
  static String deviceCommand(String deviceId) => '\$apiPrefix/iot/devices/${Uri.encodeComponent(deviceId)}/command';
  static const String deviceTypes = '\$apiPrefix/iot/device-types';
  static String fieldDevices(String fieldId) => '\$apiPrefix/iot/devices/field/${Uri.encodeComponent(fieldId)}';
  static String fieldSensors(String fieldId) => '\$apiPrefix/iot/fields/${Uri.encodeComponent(fieldId)}/sensors';
  static String sensorHistory(String sensorId) => '\$apiPrefix/iot/sensors/${Uri.encodeComponent(sensorId)}/history';
  static String readingsByFarm(String farmId) => '\$apiPrefix/iot/readings/${Uri.encodeComponent(farmId)}';
  static const String sensors = '\$apiPrefix/iot/sensors';
  static const String actuators = '\$apiPrefix/iot/actuators';
  static const String alertRules = '\$apiPrefix/iot/alert-rules';
  static const String sensorStream = '\$apiPrefix/iot/sensors/stream';
  static const String sensorStats = '\$apiPrefix/iot/sensors/stats';
  static String sensorLatest(String sensorId) => '\$apiPrefix/iot/sensors/${Uri.encodeComponent(sensorId)}/latest';
}

/// irrigation
abstract final class IrrigationEndpoints {
  static String recommendation(String fieldId) => '\$apiPrefix/irrigation/fields/${Uri.encodeComponent(fieldId)}/recommendation';
  static const String calculate = '\$apiPrefix/irrigation/calculate';
  static const String et0 = '\$apiPrefix/irrigation/et0';
  static const String waterBalance = '\$apiPrefix/irrigation/water-balance';
  static const String sensorReading = '\$apiPrefix/irrigation/sensor-reading';
  static const String efficiency = '\$apiPrefix/irrigation/efficiency';
  static const String schedule = '\$apiPrefix/irrigation/schedule';
  static const String schedulesList = '\$apiPrefix/irrigation/schedules';
  static String schedulesGet(String scheduleId) => '\$apiPrefix/irrigation/schedules/${Uri.encodeComponent(scheduleId)}';
  static const String schedulesCreate = '\$apiPrefix/irrigation/schedules';
  static String schedulesUpdate(String scheduleId) => '\$apiPrefix/irrigation/schedules/${Uri.encodeComponent(scheduleId)}';
  static String schedulesDelete(String scheduleId) => '\$apiPrefix/irrigation/schedules/${Uri.encodeComponent(scheduleId)}';
  static String history(String fieldId) => '\$apiPrefix/irrigation/history/${Uri.encodeComponent(fieldId)}';
  static const String recommendations = '\$apiPrefix/irrigation/recommendations';
  static const String crops = '\$apiPrefix/irrigation/crops';
  static const String methods = '\$apiPrefix/irrigation/methods';
  static const String pivotControl = '\$apiPrefix/irrigation/pivot/control';
  static const String efficiencyReport = '\$apiPrefix/irrigation/efficiency-report';
  static const String irrigationExecuted = '\$apiPrefix/irrigation/irrigation-executed';
  static const String calculateWithAction = '\$apiPrefix/irrigation/calculate-with-action';
  static const String pivotSpeed = '\$apiPrefix/irrigation/pivot/speed';
}

/// labor
abstract final class LaborEndpoints {
  static const String workers = '\$apiPrefix/labor/workers';
  static String workerById(String workerId) => '\$apiPrefix/labor/workers/${Uri.encodeComponent(workerId)}';
  static const String schedule = '\$apiPrefix/labor/schedule';
  static const String payroll = '\$apiPrefix/labor/payroll';
}

/// lab
abstract final class LabEndpoints {
  static const String samples = '\$apiPrefix/lab/samples';
  static String sampleByBarcode(String barcode) => '\$apiPrefix/lab/samples/barcode/${Uri.encodeComponent(barcode)}';
}

/// leveling
abstract final class LevelingEndpoints {
  static const String analyze = '\$apiPrefix/leveling/analyze';
  static String plan(String fieldId) => '\$apiPrefix/leveling/plan/${Uri.encodeComponent(fieldId)}';
  static String cost(String fieldId) => '\$apiPrefix/leveling/cost/${Uri.encodeComponent(fieldId)}';
  static String equipment(String fieldId) => '\$apiPrefix/leveling/equipment/${Uri.encodeComponent(fieldId)}';
  static const String simulate = '\$apiPrefix/leveling/simulate';
}

/// loan verification
abstract final class LoanVerificationEndpoints {
  static String verify(String fieldId) => '\$apiPrefix/loans/crop-loan-verification/${Uri.encodeComponent(fieldId)}';
}

/// logistics
abstract final class LogisticsEndpoints {
  static const String shipments = '\$apiPrefix/logistics/shipments';
  static String shipmentGet(String shipmentId) => '\$apiPrefix/logistics/shipments/${Uri.encodeComponent(shipmentId)}';
  static const String shipmentCreate = '\$apiPrefix/logistics/shipments';
  static const String vehicles = '\$apiPrefix/logistics/vehicles';
  static const String routes = '\$apiPrefix/logistics/routes';
  static String tracking(String shipmentId) => '\$apiPrefix/logistics/tracking/${Uri.encodeComponent(shipmentId)}';
}

/// marketplace
abstract final class MarketplaceEndpoints {
  static const String listings = '\$apiPrefix/marketplace/listings';
  static const String listingCreate = '\$apiPrefix/marketplace/listings';
  static const String products = '\$apiPrefix/marketplace/products';
  static String productGet(String productId) => '\$apiPrefix/marketplace/products/${Uri.encodeComponent(productId)}';
  static String productApprove(String productId) => '\$apiPrefix/marketplace/products/${Uri.encodeComponent(productId)}/approve';
  static String productReject(String productId) => '\$apiPrefix/marketplace/products/${Uri.encodeComponent(productId)}/reject';
  static const String orders = '\$apiPrefix/marketplace/orders';
  static String ordersByUser(String userId) => '\$apiPrefix/marketplace/orders/user/${Uri.encodeComponent(userId)}';
  static const String harvest = '\$apiPrefix/marketplace/harvest';
  static const String stats = '\$apiPrefix/marketplace/stats';
  static String wallet(String userId) => '\$apiPrefix/marketplace/fintech/wallet/${Uri.encodeComponent(userId)}';
  static String walletDeposit(String walletId) => '\$apiPrefix/marketplace/fintech/wallet/${Uri.encodeComponent(walletId)}/deposit';
  static String walletWithdraw(String walletId) => '\$apiPrefix/marketplace/fintech/wallet/${Uri.encodeComponent(walletId)}/withdraw';
  static String walletTransactions(String walletId) => '\$apiPrefix/marketplace/fintech/wallet/${Uri.encodeComponent(walletId)}/transactions';
  static const String creditScore = '\$apiPrefix/marketplace/fintech/calculate-score';
  static const String loans = '\$apiPrefix/marketplace/fintech/loans';
  static String loansByUser(String walletId) => '\$apiPrefix/marketplace/fintech/loans/${Uri.encodeComponent(walletId)}';
  static String loanRepay(String loanId) => '\$apiPrefix/marketplace/fintech/loans/${Uri.encodeComponent(loanId)}/repay';
}

/// notification
abstract final class NotificationEndpoints {
  static const String list = '\$apiPrefix/notifications';
  static String getNotification(String notificationId) => '\$apiPrefix/notifications/${Uri.encodeComponent(notificationId)}';
  static String markRead(String notificationId) => '\$apiPrefix/notifications/${Uri.encodeComponent(notificationId)}/read';
  static const String markAllRead = '\$apiPrefix/notifications/read-all';
  static const String preferences = '\$apiPrefix/notifications/preferences';
  static const String subscribe = '\$apiPrefix/notifications/subscribe';
  static const String unsubscribe = '\$apiPrefix/notifications/unsubscribe';
}

/// partner admin client
abstract final class PartnerAdminClientEndpoints {
  static const String create = '\$apiPrefix/admin/partner-auth/clients';
  static const String list = '\$apiPrefix/admin/partner-auth/clients';
  static String getPartnerAdminClient(String clientId) => '\$apiPrefix/admin/partner-auth/clients/${Uri.encodeComponent(clientId)}';
  static String update(String clientId) => '\$apiPrefix/admin/partner-auth/clients/${Uri.encodeComponent(clientId)}';
  static String rotateSecret(String clientId) => '\$apiPrefix/admin/partner-auth/clients/${Uri.encodeComponent(clientId)}/rotate-secret';
  static String rotateApiKey(String clientId) => '\$apiPrefix/admin/partner-auth/clients/${Uri.encodeComponent(clientId)}/rotate-api-key';
  static String suspend(String clientId) => '\$apiPrefix/admin/partner-auth/clients/${Uri.encodeComponent(clientId)}/suspend';
  static String unsuspend(String clientId) => '\$apiPrefix/admin/partner-auth/clients/${Uri.encodeComponent(clientId)}/unsuspend';
  static String revoke(String clientId) => '\$apiPrefix/admin/partner-auth/clients/${Uri.encodeComponent(clientId)}';
}

/// partner admin consent
abstract final class PartnerAdminConsentEndpoints {
  static const String list = '\$apiPrefix/admin/partner-auth/consents';
  static String revoke(String grantId) => '\$apiPrefix/admin/partner-auth/consents/${Uri.encodeComponent(grantId)}';
}

/// partner admin signing key
abstract final class PartnerAdminSigningKeyEndpoints {
  static const String list = '\$apiPrefix/admin/partner-auth/signing-keys';
  static const String rotate = '\$apiPrefix/admin/partner-auth/signing-keys/rotate';
  static String delete(String kid) => '\$apiPrefix/admin/partner-auth/signing-keys/${Uri.encodeComponent(kid)}';
}

/// partner admin token
abstract final class PartnerAdminTokenEndpoints {
  static const String listAccess = '\$apiPrefix/admin/partner-auth/tokens/access';
  static const String listRefresh = '\$apiPrefix/admin/partner-auth/tokens/refresh';
  static String revokeAllForClient(String clientId) => '\$apiPrefix/admin/partner-auth/tokens/revoke-all/client/${Uri.encodeComponent(clientId)}';
  static String revokeAllForUser(String userId) => '\$apiPrefix/admin/partner-auth/tokens/revoke-all/user/${Uri.encodeComponent(userId)}';
}

/// partner boundary
abstract final class PartnerBoundaryEndpoints {
  static const String create = '/partner/v1/boundaries';
  static String getPartnerBoundary(String boundaryId) => '/partner/v1/boundaries/${Uri.encodeComponent(boundaryId)}';
  static const String batchQuery = '/partner/v1/boundaries/query';
}

/// partner export
abstract final class PartnerExportEndpoints {
  static const String create = '/partner/v1/exports';
  static String status(String exportId) => '/partner/v1/exports/${Uri.encodeComponent(exportId)}/status';
  static String contents(String exportId) => '/partner/v1/exports/${Uri.encodeComponent(exportId)}/contents';
}

/// partner field
abstract final class PartnerFieldEndpoints {
  static const String list = '/partner/v1/fields';
  static const String listAll = '/partner/v1/fields/all';
  static String getPartnerField(String fieldId) => '/partner/v1/fields/${Uri.encodeComponent(fieldId)}';
}

/// partner layer
abstract final class PartnerLayerEndpoints {
  static const String asPlantedList = '/partner/v1/layers/asPlanted';
  static String asPlantedContents(String activityId) => '/partner/v1/layers/asPlanted/${Uri.encodeComponent(activityId)}/contents';
  static const String asHarvestedList = '/partner/v1/layers/asHarvested';
  static String asHarvestedContents(String activityId) => '/partner/v1/layers/asHarvested/${Uri.encodeComponent(activityId)}/contents';
  static const String asAppliedList = '/partner/v1/layers/asApplied';
  static String asAppliedContents(String activityId) => '/partner/v1/layers/asApplied/${Uri.encodeComponent(activityId)}/contents';
  static const String scoutingList = '/partner/v1/layers/scoutingObservations';
  static String scoutingGet(String observationId) => '/partner/v1/layers/scoutingObservations/${Uri.encodeComponent(observationId)}';
  static String scoutingAttachments(String observationId) => '/partner/v1/layers/scoutingObservations/${Uri.encodeComponent(observationId)}/attachments';
  static String scoutingAttachmentContents(String observationId, String attachmentId) => '/partner/v1/layers/scoutingObservations/${Uri.encodeComponent(observationId)}/attachments/${Uri.encodeComponent(attachmentId)}/contents';
}

/// partner oauth
abstract final class PartnerOauthEndpoints {
  static const String authorize = '/partner/v1/oauth/authorize';
  static const String token = '/partner/v1/oauth/token';
  static const String revoke = '/partner/v1/oauth/revoke';
  static const String introspect = '/partner/v1/oauth/introspect';
  static const String userinfo = '/partner/v1/oauth/userinfo';
  static const String discovery = '/.well-known/openid-configuration';
  static const String jwks = '/.well-known/jwks.json';
}

/// partner org
abstract final class PartnerOrgEndpoints {
  static String resourceOwner(String resourceOwnerId) => '/partner/v1/resourceOwners/${Uri.encodeComponent(resourceOwnerId)}';
  static String farmOrg(String farmOrganizationType, String farmOrganizationId) => '/partner/v1/farmOrganizations/${Uri.encodeComponent(farmOrganizationType)}/${Uri.encodeComponent(farmOrganizationId)}';
  static const String operations = '/partner/v1/operations/all';
}

/// partner upload
abstract final class PartnerUploadEndpoints {
  static const String create = '/partner/v1/uploads';
  static String chunk(String uploadId) => '/partner/v1/uploads/${Uri.encodeComponent(uploadId)}';
  static String status(String uploadId) => '/partner/v1/uploads/${Uri.encodeComponent(uploadId)}/status';
  static const String batchStatus = '/partner/v1/uploads/status/query';
  static String cancel(String uploadId) => '/partner/v1/uploads/${Uri.encodeComponent(uploadId)}';
}

/// payment
abstract final class PaymentEndpoints {
  static const String deposit = '\$apiPrefix/payment/deposit';
  static const String withdraw = '\$apiPrefix/payment/withdraw';
  static const String transfer = '\$apiPrefix/payment/transfer';
  static const String topup = '\$apiPrefix/payment/topup';
  static String status(String transactionId) => '\$apiPrefix/payment/status/${Uri.encodeComponent(transactionId)}';
  static const String transactions = '\$apiPrefix/payment/transactions';
  static String balance(String walletId) => '\$apiPrefix/payment/balance/${Uri.encodeComponent(walletId)}';
  static const String validatePhone = '\$apiPrefix/payment/validate-phone';
  static const String operators = '\$apiPrefix/payment/operators';
  static String cancel(String transactionId) => '\$apiPrefix/payment/cancel/${Uri.encodeComponent(transactionId)}';
}

/// pest
abstract final class PestEndpoints {
  static const String list = '\$apiPrefix/pests';
  static String byCrop(String cropType) => '\$apiPrefix/pests/crop/${Uri.encodeComponent(cropType)}';
  static const String identify = '\$apiPrefix/pests/identify';
  static const String treatmentRecommend = '\$apiPrefix/treatments/recommend';
}

/// precision
abstract final class PrecisionEndpoints {
  static String vra(String fieldId) => '\$apiPrefix/precision-agriculture/vra/${Uri.encodeComponent(fieldId)}';
  static String gdd(String fieldId) => '\$apiPrefix/precision-agriculture/gdd/${Uri.encodeComponent(fieldId)}';
  static const String fertilizerCalculate = '\$apiPrefix/precision-agriculture/fertilizer/calculate';
}

/// provider
abstract final class ProviderEndpoints {
  static const String list = '\$apiPrefix/providers';
  static String config(String providerId) => '\$apiPrefix/providers/${Uri.encodeComponent(providerId)}/config';
  static String configUpdate(String providerId) => '\$apiPrefix/providers/${Uri.encodeComponent(providerId)}/config';
  static const String providerConfigList = '\$apiPrefix/provider-config';
  static String providerConfigItem(String providerId) => '\$apiPrefix/provider-config/${Uri.encodeComponent(providerId)}';
}

/// research
abstract final class ResearchEndpoints {
  static const String trials = '\$apiPrefix/research/trials';
  static String trialGet(String trialId) => '\$apiPrefix/research/trials/${Uri.encodeComponent(trialId)}';
  static const String trialCreate = '\$apiPrefix/research/trials';
  static String trialUpdate(String trialId) => '\$apiPrefix/research/trials/${Uri.encodeComponent(trialId)}';
  static String observations(String trialId) => '\$apiPrefix/research/trials/${Uri.encodeComponent(trialId)}/observations';
  static String analysis(String trialId) => '\$apiPrefix/research/trials/${Uri.encodeComponent(trialId)}/analysis';
}

/// satellite
abstract final class SatelliteEndpoints {
  static const String analyze = '\$apiPrefix/satellite/v1/analyze';
  static String analyzeField(String fieldId) => '\$apiPrefix/satellite/analyze/${Uri.encodeComponent(fieldId)}';
  static String timeseries(String fieldId) => '\$apiPrefix/satellite/v1/timeseries/${Uri.encodeComponent(fieldId)}';
  static String indices(String fieldId) => '\$apiPrefix/satellite/v1/indices/${Uri.encodeComponent(fieldId)}';
  static String indexMap(String fieldId, String indexName) => '\$apiPrefix/satellite/v1/indices/${Uri.encodeComponent(fieldId)}/${Uri.encodeComponent(indexName)}/map';
  static String indexPixel(String fieldId) => '\$apiPrefix/satellite/v1/indices/${Uri.encodeComponent(fieldId)}/pixel';
  static String indexComposite(String fieldId, String indexName) => '\$apiPrefix/satellite/v1/indices/${Uri.encodeComponent(fieldId)}/${Uri.encodeComponent(indexName)}/composite';
  static String indexFilmstrip(String fieldId, String indexName) => '\$apiPrefix/satellite/v1/indices/${Uri.encodeComponent(fieldId)}/${Uri.encodeComponent(indexName)}/filmstrip';
  static String indexMultiCompare(String fieldId, String indexName) => '\$apiPrefix/satellite/v1/indices/${Uri.encodeComponent(fieldId)}/${Uri.encodeComponent(indexName)}/multi-date-compare';
  static const String satellites = '\$apiPrefix/satellite/v1/satellites';
  static String health(String fieldId) => '\$apiPrefix/satellite/health/${Uri.encodeComponent(fieldId)}';
  static String phenology(String fieldId) => '\$apiPrefix/satellite/phenology/${Uri.encodeComponent(fieldId)}';
  static String imagery(String fieldId) => '\$apiPrefix/satellite/imagery/${Uri.encodeComponent(fieldId)}';
  static String ndviField(String fieldId) => '\$apiPrefix/fields/${Uri.encodeComponent(fieldId)}/ndvi';
  static const String ndviSummary = '\$apiPrefix/ndvi/summary';
}

/// satellite monitor
abstract final class SatelliteMonitorEndpoints {
  static const String fields = '\$apiPrefix/satellite-monitor/fields';
  static String fieldGet(String fieldId) => '\$apiPrefix/satellite-monitor/fields/${Uri.encodeComponent(fieldId)}';
  static const String stats = '\$apiPrefix/satellite-monitor/stats';
  static const String alerts = '\$apiPrefix/satellite-monitor/alerts';
}

/// scouting
abstract final class ScoutingEndpoints {
  static const String list = '\$apiPrefix/scouting/reports';
  static String getScouting(String reportId) => '\$apiPrefix/scouting/reports/${Uri.encodeComponent(reportId)}';
  static const String create = '\$apiPrefix/scouting/reports';
  static String update(String reportId) => '\$apiPrefix/scouting/reports/${Uri.encodeComponent(reportId)}';
  static String delete(String reportId) => '\$apiPrefix/scouting/reports/${Uri.encodeComponent(reportId)}';
  static String fieldReports(String fieldId) => '\$apiPrefix/scouting/fields/${Uri.encodeComponent(fieldId)}/reports';
  static const String stats = '\$apiPrefix/scouting/stats';
}

/// season
abstract final class SeasonEndpoints {
  static const String list = '\$apiPrefix/seasons';
  static String getSeason(String seasonId) => '\$apiPrefix/seasons/${Uri.encodeComponent(seasonId)}';
  static const String create = '\$apiPrefix/seasons';
  static String update(String seasonId) => '\$apiPrefix/seasons/${Uri.encodeComponent(seasonId)}';
  static String delete(String seasonId) => '\$apiPrefix/seasons/${Uri.encodeComponent(seasonId)}';
  static const String active = '\$apiPrefix/seasons/active';
}

/// seed
abstract final class SeedEndpoints {
  static const String list = '\$apiPrefix/seeds';
  static String getSeed(String seedId) => '\$apiPrefix/seeds/${Uri.encodeComponent(seedId)}';
  static const String recommendations = '\$apiPrefix/seeds/recommendations';
}

/// soil
abstract final class SoilEndpoints {
  static const String tests = '\$apiPrefix/soil/tests';
  static String testGet(String testId) => '\$apiPrefix/soil/tests/${Uri.encodeComponent(testId)}';
  static const String testCreate = '\$apiPrefix/soil/tests';
  static String testUpdate(String testId) => '\$apiPrefix/soil/tests/${Uri.encodeComponent(testId)}';
  static String testDelete(String testId) => '\$apiPrefix/soil/tests/${Uri.encodeComponent(testId)}';
  static String testsByFieldLegacy(String fieldId) => '\$apiPrefix/soil/fields/${Uri.encodeComponent(fieldId)}/tests';
  static const String analysis = '\$apiPrefix/soil/analysis';
  static const String analysisInterpret = '\$apiPrefix/soil/analysis/interpret';
  static const String sensors = '\$apiPrefix/soil/sensors';
  static String sensorReadings(String sensorId) => '\$apiPrefix/soil/sensors/${Uri.encodeComponent(sensorId)}/readings';
  static String moisture(String fieldId) => '\$apiPrefix/soil/moisture/${Uri.encodeComponent(fieldId)}';
  static String salinity(String fieldId) => '\$apiPrefix/soil/salinity/${Uri.encodeComponent(fieldId)}';
  static String ph(String fieldId) => '\$apiPrefix/soil/ph/${Uri.encodeComponent(fieldId)}';
  static String nutrients(String fieldId) => '\$apiPrefix/soil/nutrients/${Uri.encodeComponent(fieldId)}';
  static const String recommendations = '\$apiPrefix/soil/recommendations';
  static String recommendationsByField(String fieldId) => '\$apiPrefix/soil/recommendations/${Uri.encodeComponent(fieldId)}';
  static String testsByField(String fieldId) => '\$apiPrefix/soil/tests/field/${Uri.encodeComponent(fieldId)}';
  static const String products = '\$apiPrefix/soil/products';
  static String cropRequirements(String crop) => '\$apiPrefix/soil/crops/${Uri.encodeComponent(crop)}/requirements';
  static const String interpret = '\$apiPrefix/soil/interpret';
  static const String amendmentPlan = '\$apiPrefix/soil/recommendations/amendment-plan';
  static const String phStatus = '\$apiPrefix/soil/interpretation/ph-status';
  static const String ecStatus = '\$apiPrefix/soil/interpretation/ec-status';
}

/// support
abstract final class SupportEndpoints {
  static const String tickets = '\$apiPrefix/support/tickets';
  static String ticketById(String ticketId) => '\$apiPrefix/support/tickets/${Uri.encodeComponent(ticketId)}';
}

/// task
abstract final class TaskEndpoints {
  static const String list = '\$apiPrefix/tasks';
  static String getTask(String taskId) => '\$apiPrefix/tasks/${Uri.encodeComponent(taskId)}';
  static const String create = '\$apiPrefix/tasks';
  static String update(String taskId) => '\$apiPrefix/tasks/${Uri.encodeComponent(taskId)}';
  static String delete(String taskId) => '\$apiPrefix/tasks/${Uri.encodeComponent(taskId)}';
  static String status(String taskId) => '\$apiPrefix/tasks/${Uri.encodeComponent(taskId)}/status';
  static String complete(String taskId) => '\$apiPrefix/tasks/${Uri.encodeComponent(taskId)}/complete';
  static String assign(String taskId) => '\$apiPrefix/tasks/${Uri.encodeComponent(taskId)}/assign';
}

/// team
abstract final class TeamEndpoints {
  static const String members = '\$apiPrefix/team/members';
  static String memberGet(String memberId) => '\$apiPrefix/team/members/${Uri.encodeComponent(memberId)}';
  static const String memberInvite = '\$apiPrefix/team/members/invite';
  static String memberRemove(String memberId) => '\$apiPrefix/team/members/${Uri.encodeComponent(memberId)}';
  static String memberRole(String memberId) => '\$apiPrefix/team/members/${Uri.encodeComponent(memberId)}/role';
  static const String roles = '\$apiPrefix/team/roles';
}

/// terrain
abstract final class TerrainEndpoints {
  static const String dem = '\$apiPrefix/terrain/dem';
  static const String slope = '\$apiPrefix/terrain/slope';
  static String aspect(String fieldId) => '\$apiPrefix/terrain/aspect/${Uri.encodeComponent(fieldId)}';
  static String hydrologyDrainage(String fieldId) => '\$apiPrefix/hydrology/drainage/${Uri.encodeComponent(fieldId)}';
  static String hydrologyWatershed(String fieldId) => '\$apiPrefix/hydrology/basins/${Uri.encodeComponent(fieldId)}';
  static String hydrologyFlow(String fieldId) => '\$apiPrefix/terrain/flow/${Uri.encodeComponent(fieldId)}';
  static const String levelingOptimize = '\$apiPrefix/leveling/analyze';
  static const String levelingCutFill = '\$apiPrefix/leveling/cut-fill';
  static String levelingCost(String fieldId) => '\$apiPrefix/leveling/cost/${Uri.encodeComponent(fieldId)}';
  static const String erosion = '\$apiPrefix/terrain/erosion';
  static const String erosionWind = '\$apiPrefix/terrain/erosion/wind';
  static const String erosionCombined = '\$apiPrefix/terrain/erosion/combined';
  static const String erosionYemen = '\$apiPrefix/terrain/erosion/yemen';
  static String demField(String fieldId) => '\$apiPrefix/terrain/dem/${Uri.encodeComponent(fieldId)}';
  static String slopeField(String fieldId) => '\$apiPrefix/terrain/slope/${Uri.encodeComponent(fieldId)}';
  static String twi(String fieldId) => '\$apiPrefix/terrain/twi/${Uri.encodeComponent(fieldId)}';
  static String contours(String fieldId) => '\$apiPrefix/terrain/contours/${Uri.encodeComponent(fieldId)}';
  static const String analyze = '\$apiPrefix/terrain/analyze';
}

/// traceability
abstract final class TraceabilityEndpoints {
  static const String batches = '\$apiPrefix/traceability/batches';
  static String batchGet(String batchId) => '\$apiPrefix/traceability/batches/${Uri.encodeComponent(batchId)}';
  static const String events = '\$apiPrefix/traceability/events';
  static String qrCode(String batchId) => '\$apiPrefix/traceability/batches/${Uri.encodeComponent(batchId)}/qr';
  static String batchEvents(String batchId) => '\$apiPrefix/traceability/batches/${Uri.encodeComponent(batchId)}/events';
  static String anchorsList(String tenantId, String fieldId) => '\$apiPrefix/traceability/anchors/${Uri.encodeComponent(tenantId)}/${Uri.encodeComponent(fieldId)}';
  static String anchorsVerify(String tenantId, String fieldId) => '\$apiPrefix/traceability/anchors/${Uri.encodeComponent(tenantId)}/${Uri.encodeComponent(fieldId)}/verify';
  static const String anchorsStats = '\$apiPrefix/traceability/anchors/stats';
}

/// upload
abstract final class UploadEndpoints {
  static const String create = '\$apiPrefix/uploads';
  static String chunk(String uploadId) => '\$apiPrefix/uploads/${Uri.encodeComponent(uploadId)}';
  static String status(String uploadId) => '\$apiPrefix/uploads/${Uri.encodeComponent(uploadId)}/status';
  static const String batchStatus = '\$apiPrefix/uploads/status/query';
  static String cancel(String uploadId) => '\$apiPrefix/uploads/${Uri.encodeComponent(uploadId)}';
}

/// user
abstract final class UserEndpoints {
  static const String list = '\$apiPrefix/users';
  static String getUser(String userId) => '\$apiPrefix/users/${Uri.encodeComponent(userId)}';
  static const String create = '\$apiPrefix/users';
  static String update(String userId) => '\$apiPrefix/users/${Uri.encodeComponent(userId)}';
  static String delete(String userId) => '\$apiPrefix/users/${Uri.encodeComponent(userId)}';
  static String block(String userId) => '\$apiPrefix/users/${Uri.encodeComponent(userId)}/block';
}

/// vegetation
abstract final class VegetationEndpoints {
  static const String analyze = '\$apiPrefix/vegetation/analyze';
  static String ndvi(String fieldId) => '\$apiPrefix/vegetation/ndvi/${Uri.encodeComponent(fieldId)}';
  static String evi(String fieldId) => '\$apiPrefix/vegetation/evi/${Uri.encodeComponent(fieldId)}';
  static String savi(String fieldId) => '\$apiPrefix/vegetation/savi/${Uri.encodeComponent(fieldId)}';
  static String ndwi(String fieldId) => '\$apiPrefix/vegetation/ndwi/${Uri.encodeComponent(fieldId)}';
  static String lai(String fieldId) => '\$apiPrefix/vegetation/lai/${Uri.encodeComponent(fieldId)}';
  static String chlorophyll(String fieldId) => '\$apiPrefix/vegetation/chlorophyll/${Uri.encodeComponent(fieldId)}';
  static String timeseries(String fieldId) => '\$apiPrefix/vegetation/timeseries/${Uri.encodeComponent(fieldId)}';
  static String stressMap(String fieldId) => '\$apiPrefix/vegetation/stress/${Uri.encodeComponent(fieldId)}';
}

/// virtual sensor
abstract final class VirtualSensorEndpoints {
  static const String et0Calculate = '\$apiPrefix/virtual-sensors/et0/calculate';
  static const String etcCalculate = '\$apiPrefix/virtual-sensors/etc/calculate';
  static const String crops = '\$apiPrefix/virtual-sensors/crops';
  static String cropKc(String cropType) => '\$apiPrefix/virtual-sensors/crops/${Uri.encodeComponent(cropType)}/kc';
  static const String soils = '\$apiPrefix/virtual-sensors/soils';
  static const String soilMoisture = '\$apiPrefix/virtual-sensors/soil-moisture/estimate';
  static const String irrigationMethods = '\$apiPrefix/virtual-sensors/irrigation-methods';
  static const String irrigationRecommend = '\$apiPrefix/virtual-sensors/irrigation/recommend';
  static const String irrigationQuickCheck = '\$apiPrefix/virtual-sensors/irrigation/quick-check';
}

/// vision
abstract final class VisionEndpoints {
  static const String detectPest = '\$apiPrefix/vision/detect/pest';
  static const String detectDisease = '\$apiPrefix/vision/detect/disease';
  static const String detectWeed = '\$apiPrefix/vision/detect/weed';
  static const String countPlants = '\$apiPrefix/vision/count/plants';
  static const String classifyRipeness = '\$apiPrefix/vision/classify/ripeness';
  static const String segmentLeaf = '\$apiPrefix/vision/segment/leaf';
  static const String trackObjects = '\$apiPrefix/vision/track/objects';
  static String trackClear(String trackerId) => '\$apiPrefix/vision/track/${Uri.encodeComponent(trackerId)}';
  static const String batchPest = '\$apiPrefix/vision/batch/detect/pest';
  static const String batchDisease = '\$apiPrefix/vision/batch/detect/disease';
  static const String batchStatus = '\$apiPrefix/vision/batch/status';
  static const String modelsList = '\$apiPrefix/vision/models/versions';
  static String modelInfo(String variant) => '\$apiPrefix/vision/models/${Uri.encodeComponent(variant)}/info';
  static const String modelsWarmup = '\$apiPrefix/vision/models/warmup';
  static const String modelsLoaded = '\$apiPrefix/vision/models/loaded';
}

/// vra
abstract final class VraEndpoints {
  static const String maps = '\$apiPrefix/vra/maps';
  static String mapGet(String mapId) => '\$apiPrefix/vra/maps/${Uri.encodeComponent(mapId)}';
  static const String mapCreate = '\$apiPrefix/vra/maps';
  static const String prescriptions = '\$apiPrefix/vra/prescriptions';
  static String prescriptionGet(String prescriptionId) => '\$apiPrefix/vra/prescriptions/${Uri.encodeComponent(prescriptionId)}';
  static String zones(String fieldId) => '\$apiPrefix/vra/zones/${Uri.encodeComponent(fieldId)}';
}

/// weather
abstract final class WeatherEndpoints {
  static const String current = '\$apiPrefix/weather/current';
  static String currentByLocation(String locationId) => '\$apiPrefix/weather/current/${Uri.encodeComponent(locationId)}';
  static const String forecast = '\$apiPrefix/weather/forecast';
  static String forecastByLocation(String locationId) => '\$apiPrefix/weather/forecast/${Uri.encodeComponent(locationId)}';
  static String forecastByField(String fieldId) => '\$apiPrefix/weather/forecast/field/${Uri.encodeComponent(fieldId)}';
  static const String alerts = '\$apiPrefix/weather/alerts';
  static String alertsByLocation(String locationId) => '\$apiPrefix/weather/alerts/${Uri.encodeComponent(locationId)}';
  static String alertsByField(String fieldId) => '\$apiPrefix/weather/alerts/field/${Uri.encodeComponent(fieldId)}';
  static const String locations = '\$apiPrefix/weather/locations';
  static const String agriculturalCalendar = '\$apiPrefix/weather/agricultural-calendar';
  static String fieldGraphGenerate(String fieldId) => '\$apiPrefix/weather/fields/${Uri.encodeComponent(fieldId)}/graph';
  static String fieldGraphFetch(String graphId) => '\$apiPrefix/weather/graphs/${Uri.encodeComponent(graphId)}';
  static const String kongCurrent = '\$apiPrefix/weather/weather/current';
  static const String kongForecast = '\$apiPrefix/weather/weather/forecast';
  static const String kongAgriculturalReport = '\$apiPrefix/weather/weather/agricultural-report';
  static String kongCurrentByLocation(String locationId) => '\$apiPrefix/weather/v1/current/${Uri.encodeComponent(locationId)}';
  static String kongForecastByLocation(String locationId) => '\$apiPrefix/weather/v1/forecast/${Uri.encodeComponent(locationId)}';
  static const String kongLocations = '\$apiPrefix/weather/v1/locations';
  static const String weatherCoreCurrent = '\$apiPrefix/weather-core/weather/current';
  static const String weatherCoreForecast = '\$apiPrefix/weather-core/weather/forecast';
  static const String weatherCoreAgReport = '\$apiPrefix/weather-core/weather/agricultural-report';
  static const String gdd = '\$apiPrefix/weather/gdd';
  static const String sprayWindows = '\$apiPrefix/weather/spray-windows';
}

/// yield
abstract final class YieldEndpoints {
  static String predict(String fieldId) => '\$apiPrefix/yield/fields/${Uri.encodeComponent(fieldId)}/predict';
  static String history(String fieldId) => '\$apiPrefix/yield/fields/${Uri.encodeComponent(fieldId)}/history';
  static const String predictPost = '\$apiPrefix/yield/predict';
  static const String predictions = '\$apiPrefix/yield/predictions';
  static const String profitability = '\$apiPrefix/yield/profitability';
}
