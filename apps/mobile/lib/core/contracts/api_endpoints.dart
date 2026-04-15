/// SAHOOL Unified API Endpoint Paths (auto-generated)
/// DO NOT EDIT - Generated from packages/shared-types/src/contracts/api-endpoints.ts
/// Run: npx tsx scripts/sync-contracts-to-dart.ts
///
/// Contract version: 4.18.0
library;

/// API version prefix
const String apiVersion = 'v1';
const String apiPrefix = '/api/$apiVersion';

/// health
abstract final class Healthendpoints {
  static const String liveness = '/healthz';
  static const String readiness = '/readyz';
  static const String health = '/health';
  static const String metrics = '/metrics';
}

/// service health
abstract final class ServiceHealthendpoints {
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
  static const String yieldServiceHealthendpoints = '\$apiPrefix/yield/healthz';
  static const String disasters = '\$apiPrefix/disasters/healthz';
  static const String providers = '\$apiPrefix/providers/healthz';
  static const String agroRules = '\$apiPrefix/agro-rules/healthz';
  static const String intelligence = '\$apiPrefix/intelligence/healthz';
}

/// auth
abstract final class Authendpoints {
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
abstract final class Advisoryendpoints {
  static const String recommend = '\$apiPrefix/fertilizer/recommend';
  static const String soilInterpret = '\$apiPrefix/fertilizer/soil/interpret';
  static const String crops = '\$apiPrefix/fertilizer/crops';
  static const String fertilizers = '\$apiPrefix/fertilizer/fertilizers';
  static const String deficiencySymptoms = '\$apiPrefix/fertilizer/deficiency/symptoms';
  static const String schedule = '\$apiPrefix/fertilizer/schedule';
  static const String recommendations = '\$apiPrefix/advisory/recommendations';
  static const String fertilizerAdvisory = '\$apiPrefix/advisory/fertilizer';
  static const String fertilizerCalculate = '\$apiPrefix/advisory/fertilizer/calculate';
  static String fertilizerUpdate(String prescriptionId) => '\$apiPrefix/advisory/fertilizer/$prescriptionId';
  static String fertilizerZoneUpdate(String prescriptionId, String zoneId) => '\$apiPrefix/advisory/fertilizer/$prescriptionId/zones/$zoneId';
  static const String advice = '\$apiPrefix/advisory/advice';
  static const String disease = '\$apiPrefix/advisory/disease';
  static const String nutrients = '\$apiPrefix/advisory/nutrients';
  static const String agroAdvice = '\$apiPrefix/agro-advisor/advice';
  static const String agroDisease = '\$apiPrefix/agro-advisor/disease';
  static const String agroNutrients = '\$apiPrefix/agro-advisor/nutrients';
  static String comprehensive(String fieldId) => '\$apiPrefix/advisory/comprehensive/$fieldId';
  static String recommendationsByField(String fieldId) => '\$apiPrefix/advisory/recommendations/$fieldId';
  static String diseaseAssess(String fieldId) => '\$apiPrefix/advisory/disease-assess/$fieldId';
  static String fertilizerPlan(String fieldId) => '\$apiPrefix/advisory/fertilizer-plan/$fieldId';
  static String cropAdvice(String fieldId) => '\$apiPrefix/advisory/crop-advice/$fieldId';
  static const String sprayWindows = '\$apiPrefix/advisory/spray-windows';
  static const String sprayHistory = '\$apiPrefix/advisory/spray-history';
}

/// agri calendar
abstract final class AgriCalendarendpoints {
  static const String events = '\$apiPrefix/agri-calendar/events';
  static const String plantingTimes = '\$apiPrefix/agri-calendar/planting-times';
  static const String harvestTimes = '\$apiPrefix/agri-calendar/harvest-times';
}

/// agro rules
abstract final class AgroRulesendpoints {
  static String fieldRules(String fieldId) => '\$apiPrefix/agro-rules/fields/$fieldId/rules';
  static const String createRule = '\$apiPrefix/agro-rules/rules';
  static String triggerRule(String ruleId) => '\$apiPrefix/agro-rules/rules/$ruleId/trigger';
  static const String gdd = '\$apiPrefix/agro-rules/gdd';
  static const String sprayWindows = '\$apiPrefix/agro-rules/spray-windows';
}

/// ai
abstract final class Aiendpoints {
  static const String copilotChat = '\$apiPrefix/copilot/chat';
  static const String copilotChatDirect = '\$apiPrefix/chat';
  static const String copilotChatStreamDirect = '\$apiPrefix/chat/stream';
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

/// alert
abstract final class Alertendpoints {
  static const String list = '\$apiPrefix/alerts';
  static String getAlertendpoints(String alertId) => '\$apiPrefix/alerts/$alertId';
  static const String create = '\$apiPrefix/alerts';
  static String delete(String alertId) => '\$apiPrefix/alerts/$alertId';
  static String acknowledge(String alertId) => '\$apiPrefix/alerts/$alertId/acknowledge';
  static String resolve(String alertId) => '\$apiPrefix/alerts/$alertId/resolve';
  static String dismiss(String alertId) => '\$apiPrefix/alerts/$alertId/dismiss';
  static const String rules = '\$apiPrefix/alerts/rules';
}

/// astronomical
abstract final class Astronomicalendpoints {
  static const String calendar = '\$apiPrefix/astronomy/calendar';
  static const String prayerTimes = '\$apiPrefix/astronomy/prayer-times';
  static const String moonPhases = '\$apiPrefix/astronomy/moon-phases';
  static const String seasons = '\$apiPrefix/astronomy/seasons';
  static const String events = '\$apiPrefix/astronomy/events';
}

/// audit
abstract final class Auditendpoints {
  static const String logs = '\$apiPrefix/audit/logs';
  static String logGet(String logId) => '\$apiPrefix/audit/logs/$logId';
  static const String stats = '\$apiPrefix/audit/stats';
  static const String adminAudit = '\$apiPrefix/admin/audit';
  static const String adminBatch = '\$apiPrefix/admin/audit/batch';
}

/// billing
abstract final class Billingendpoints {
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
  static const String deposit = '\$apiPrefix/billing/deposit';
  static const String withdraw = '\$apiPrefix/billing/withdraw';
  static const String transfer = '\$apiPrefix/billing/transfer';
  static const String payments = '\$apiPrefix/billing/payments';
  static String invoicePaymentIntent(String invoiceId) => '\$apiPrefix/billing/invoices/$invoiceId/payment-intent';
  static const String stripeConfig = '\$apiPrefix/billing/stripe/config';
  static const String stripePaymentIntents = '\$apiPrefix/billing/stripe/payment-intents';
  static String stripePaymentIntentConfirm(String paymentIntentId) => '\$apiPrefix/billing/stripe/payment-intents/$paymentIntentId/confirm';
  static const String stripeSetupIntents = '\$apiPrefix/billing/stripe/setup-intents';
  static String stripeSetupIntentConfirm(String setupIntentId) => '\$apiPrefix/billing/stripe/setup-intents/$setupIntentId/confirm';
  static const String paymentMethods = '\$apiPrefix/billing/payment-methods';
  static String paymentMethodGet(String paymentMethodId) => '\$apiPrefix/billing/payment-methods/$paymentMethodId';
  static String paymentMethodDefault(String paymentMethodId) => '\$apiPrefix/billing/payment-methods/$paymentMethodId/default';
}

/// carbon
abstract final class Carbonendpoints {
  static const String compute = '\$apiPrefix/carbon/compute';
  static String computeOperation(String operationId) => '\$apiPrefix/carbon/operations/$operationId/compute';
  static String fieldSummary(String fieldId) => '\$apiPrefix/carbon/fields/$fieldId/summary';
  static String cropSeasonSummary(String cropSeasonId) => '\$apiPrefix/carbon/crop-seasons/$cropSeasonId/summary';
}

/// chat
abstract final class Chatendpoints {
  static const String conversations = '\$apiPrefix/chat/conversations';
  static String conversationGet(String conversationId) => '\$apiPrefix/chat/conversations/$conversationId';
  static String messages(String conversationId) => '\$apiPrefix/chat/conversations/$conversationId/messages';
  static String sendMessage(String conversationId) => '\$apiPrefix/chat/conversations/$conversationId/messages';
  static String markRead(String conversationId) => '\$apiPrefix/chat/conversations/$conversationId/read';
  static const String createConversation = '\$apiPrefix/chat/conversations';
  static const String unreadCount = '\$apiPrefix/chat/conversations/unread-count';
  static String fieldMessages(String fieldId) => '\$apiPrefix/field-chat/fields/$fieldId/messages';
  static String fieldSend(String fieldId) => '\$apiPrefix/field-chat/fields/$fieldId/messages';
  static String fieldParticipants(String fieldId) => '\$apiPrefix/field-chat/fields/$fieldId/participants';
  static String fieldMessagesV2(String fieldId) => '\$apiPrefix/chat/fields/$fieldId/messages';
  static String fieldSendV2(String fieldId) => '\$apiPrefix/chat/fields/$fieldId/messages';
  static String fieldParticipantsV2(String fieldId) => '\$apiPrefix/chat/fields/$fieldId/participants';
  static const String communityPosts = '\$apiPrefix/posts';
  static String communityPostGet(String postId) => '\$apiPrefix/posts/$postId';
  static String communityComments(String postId) => '\$apiPrefix/posts/$postId/comments';
  static String mute(String conversationId) => '\$apiPrefix/chat/conversations/$conversationId/mute';
  static String report(String conversationId) => '\$apiPrefix/chat/conversations/$conversationId/report';
  static String clearMessages(String conversationId) => '\$apiPrefix/chat/conversations/$conversationId/messages';
}

/// community
abstract final class Communityendpoints {
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

/// compliance
abstract final class Complianceendpoints {
  static const String checklists = '\$apiPrefix/compliance/checklists';
  static String checklistGet(String checklistId) => '\$apiPrefix/compliance/checklists/$checklistId';
  static const String audits = '\$apiPrefix/compliance/audits';
  static const String certificates = '\$apiPrefix/compliance/certificates';
  static const String standards = '\$apiPrefix/compliance/standards';
}

/// cooperative
abstract final class Cooperativeendpoints {
  static const String bookings = '\$apiPrefix/cooperatives/bookings';
  static const String purchaseOrders = '\$apiPrefix/cooperatives/purchase-orders';
  static const String revenue = '\$apiPrefix/cooperatives/revenue';
  static const String revenueCalculate = '\$apiPrefix/cooperatives/revenue/calculate';
}

/// crop
abstract final class Cropendpoints {
  static const String list = '\$apiPrefix/crops';
  static String getCropendpoints(String cropId) => '\$apiPrefix/crops/$cropId';
  static const String create = '\$apiPrefix/crops';
  static String update(String cropId) => '\$apiPrefix/crops/$cropId';
  static String delete(String cropId) => '\$apiPrefix/crops/$cropId';
  static const String stats = '\$apiPrefix/crops/stats';
}

/// crop health
abstract final class CropHealthendpoints {
  static const String analyze = '\$apiPrefix/crop-health/analyze';
  static const String diagnose = '\$apiPrefix/crop-health/diagnose';
  static const String diagnoseBatch = '\$apiPrefix/crop-health/diagnose/batch';
  static const String decision = '\$apiPrefix/crop-health/decision';
  static String history(String fieldId) => '\$apiPrefix/crop-health/fields/$fieldId/history';
  static const String intelligenceAnalyze = '\$apiPrefix/crop-intelligence/analyze';
  static const String intelligenceDecision = '\$apiPrefix/crop-intelligence/decision';
  static String intelligenceHistory(String fieldId) => '\$apiPrefix/crop-intelligence/fields/$fieldId/history';
  static const String crops = '\$apiPrefix/crop-health/crops';
  static const String diseases = '\$apiPrefix/crop-health/diseases';
  static String treatment(String diseaseId) => '\$apiPrefix/crop-health/treatment/$diseaseId';
  static const String expertReview = '\$apiPrefix/crop-health/expert-review';
  static const String diagnosesList = '\$apiPrefix/crop-health/diagnoses';
  static const String diagnosesStats = '\$apiPrefix/crop-health/diagnoses/stats';
  static String diagnosesUpdate(String diagnosisId) => '\$apiPrefix/crop-health/diagnoses/$diagnosisId';
}

/// crop planning
abstract final class CropPlanningendpoints {
  static const String plans = '\$apiPrefix/crop-planning/plans';
  static String planById(String planId) => '\$apiPrefix/crop-planning/plans/$planId';
  static const String recommendations = '\$apiPrefix/crop-planning/recommendations';
}

/// crop rotation
abstract final class CropRotationendpoints {
  static const String plans = '\$apiPrefix/crop-rotation/plans';
  static const String recommend = '\$apiPrefix/crop-rotation/recommend';
  static const String multiYearPlan = '\$apiPrefix/crop-rotation/multi-year-plan';
  static String history(String fieldId) => '\$apiPrefix/crop-rotation/history/$fieldId';
  static const String pestBreak = '\$apiPrefix/crop-rotation/pest-break';
  static const String soilHealth = '\$apiPrefix/crop-rotation/soil-health';
  static const String stats = '\$apiPrefix/crop-rotation/stats';
}

/// crop season
abstract final class CropSeasonendpoints {
  static const String list = '\$apiPrefix/crop-seasons';
  static String getCropSeasonendpoints(String cropSeasonId) => '\$apiPrefix/crop-seasons/$cropSeasonId';
  static String update(String cropSeasonId) => '\$apiPrefix/crop-seasons/$cropSeasonId';
  static String end(String cropSeasonId) => '\$apiPrefix/crop-seasons/$cropSeasonId/end';
  static String delete(String cropSeasonId) => '\$apiPrefix/crop-seasons/$cropSeasonId';
  static String listByField(String fieldId) => '\$apiPrefix/fields/$fieldId/crop-seasons';
  static String create(String fieldId) => '\$apiPrefix/fields/$fieldId/crop-seasons';
  static String rollup(String cropSeasonId) => '\$apiPrefix/crop-seasons/$cropSeasonId/rollup';
}

/// dashboard
abstract final class Dashboardendpoints {
  static const String summary = '\$apiPrefix/dashboard/summary';
  static const String stats = '\$apiPrefix/dashboard/stats';
  static const String recentActivity = '\$apiPrefix/dashboard/recent-activity';
  static const String weatherWidget = '\$apiPrefix/dashboard/weather';
  static const String alertsWidget = '\$apiPrefix/dashboard/alerts';
}

/// disaster
abstract final class Disasterendpoints {
  static const String assess = '\$apiPrefix/disasters/assess';
  static const String alerts = '\$apiPrefix/disasters/alerts';
  static const String assessSingular = '\$apiPrefix/disaster/assess';
  static const String alertsSingular = '\$apiPrefix/disaster/alerts';
  static const String events = '\$apiPrefix/disasters/events';
  static String eventById(String eventId) => '\$apiPrefix/disasters/events/$eventId';
  static const String stats = '\$apiPrefix/disasters/stats/summary';
  static const String risks = '\$apiPrefix/disasters/risks';
}

/// document
abstract final class Documentendpoints {
  static const String list = '\$apiPrefix/documents';
  static String getDocumentendpoints(String documentId) => '\$apiPrefix/documents/$documentId';
  static const String upload = '\$apiPrefix/documents/upload';
  static String delete(String documentId) => '\$apiPrefix/documents/$documentId';
  static const String categories = '\$apiPrefix/documents/categories';
}

/// drone
abstract final class Droneendpoints {
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

/// edge
abstract final class Edgeendpoints {
  static const String devices = '\$apiPrefix/edge/devices';
  static String deviceGet(String deviceId) => '\$apiPrefix/edge/devices/$deviceId';
  static const String deviceCreate = '\$apiPrefix/edge/devices';
  static String deviceUpdate(String deviceId) => '\$apiPrefix/edge/devices/$deviceId';
  static String deviceDelete(String deviceId) => '\$apiPrefix/edge/devices/$deviceId';
  static String deviceStatus(String deviceId) => '\$apiPrefix/edge/devices/$deviceId/status';
  static const String deployModel = '\$apiPrefix/edge/deploy';
  static String deployStatus(String deploymentId) => '\$apiPrefix/edge/deploy/$deploymentId/status';
  static const String syncEdgeendpoints = '\$apiPrefix/edge/sync';
  static String syncStatus(String syncId) => '\$apiPrefix/edge/sync/$syncId/status';
  static String metrics(String deviceId) => '\$apiPrefix/edge/devices/$deviceId/metrics';
}

/// epidemic
abstract final class Epidemicendpoints {
  static const String list = '\$apiPrefix/epidemics';
  static String getEpidemicendpoints(String epidemicId) => '\$apiPrefix/epidemics/$epidemicId';
  static const String report = '\$apiPrefix/epidemics/report';
}

/// equipment
abstract final class Equipmentendpoints {
  static const String list = '\$apiPrefix/equipment';
  static String getEquipmentendpoints(String equipmentId) => '\$apiPrefix/equipment/$equipmentId';
  static const String create = '\$apiPrefix/equipment';
  static String update(String equipmentId) => '\$apiPrefix/equipment/$equipmentId';
  static String delete(String equipmentId) => '\$apiPrefix/equipment/$equipmentId';
  static String status(String equipmentId) => '\$apiPrefix/equipment/$equipmentId/status';
  static String maintenance(String equipmentId) => '\$apiPrefix/equipment/$equipmentId/maintenance';
  static String qrLookup(String qrCode) => '\$apiPrefix/equipment/qr/$qrCode';
  static const String stats = '\$apiPrefix/equipment/stats';
  static const String maintenanceAlerts = '\$apiPrefix/equipment/maintenance/alerts';
  static const String geofenceEvent = '\$apiPrefix/equipment/geofence/event';
  static const String maintenanceSchedule = '\$apiPrefix/equipment/maintenance-schedule';
  static String maintenanceScheduleById(String equipmentId) => '\$apiPrefix/equipment/$equipmentId/maintenance-schedule';
  static String issues(String equipmentId) => '\$apiPrefix/equipment/$equipmentId/issues';
  static const String alerts = '\$apiPrefix/equipment/alerts';
  static String location(String equipmentId) => '\$apiPrefix/equipment/$equipmentId/location';
  static String telemetry(String equipmentId) => '\$apiPrefix/equipment/$equipmentId/telemetry';
  static String fuel(String equipmentId) => '\$apiPrefix/equipment/$equipmentId/fuel';
  static String fuelSummary(String equipmentId) => '\$apiPrefix/equipment/$equipmentId/fuel/summary';
  static String usage(String equipmentId) => '\$apiPrefix/equipment/$equipmentId/usage';
  static String usageStart(String equipmentId) => '\$apiPrefix/equipment/$equipmentId/usage/start';
  static String usageEnd(String equipmentId, String logId) => '\$apiPrefix/equipment/$equipmentId/usage/$logId/end';
  static String usageSummary(String equipmentId) => '\$apiPrefix/equipment/$equipmentId/usage/summary';
}

/// erp sync
abstract final class ErpSyncendpoints {
  static String postFieldOperation(String operationId) => '\$apiPrefix/erp-sync/field-operations/$operationId/post';
  static const String health = '\$apiPrefix/erp-sync/health';
}

/// export
abstract final class Exportendpoints {
  static const String create = '\$apiPrefix/exports';
  static String status(String exportId) => '\$apiPrefix/exports/$exportId/status';
  static String contents(String exportId) => '\$apiPrefix/exports/$exportId/contents';
}

/// farm
abstract final class Farmendpoints {
  static const String list = '\$apiPrefix/farms';
  static String getFarmendpoints(String farmId) => '\$apiPrefix/farms/$farmId';
  static const String create = '\$apiPrefix/farms';
  static String update(String farmId) => '\$apiPrefix/farms/$farmId';
  static String delete(String farmId) => '\$apiPrefix/farms/$farmId';
  static String stats(String farmId) => '\$apiPrefix/farms/$farmId/stats';
  static String members(String farmId) => '\$apiPrefix/farms/$farmId/members';
  static String statsByTenant(String tenantId) => '\$apiPrefix/farms/stats/$tenantId';
}

/// field
abstract final class Fieldendpoints {
  static const String list = '\$apiPrefix/fields';
  static String getFieldendpoints(String fieldId) => '\$apiPrefix/fields/$fieldId';
  static const String create = '\$apiPrefix/fields';
  static String update(String fieldId) => '\$apiPrefix/fields/$fieldId';
  static String delete(String fieldId) => '\$apiPrefix/fields/$fieldId';
  static const String nearby = '\$apiPrefix/fields/nearby';
  static const String syncFieldendpoints = '\$apiPrefix/fields/sync';
  static const String syncBatch = '\$apiPrefix/fields/sync/batch';
  static String boundary(String fieldId) => '\$apiPrefix/fields/$fieldId/boundary';
  static String boundaryUpdate(String fieldId) => '\$apiPrefix/fields/$fieldId/boundary';
  static String boundaryHistory(String fieldId) => '\$apiPrefix/fields/$fieldId/boundary-history';
  static String boundaryRollback(String fieldId) => '\$apiPrefix/fields/$fieldId/boundary-history/rollback';
  static String kpiSnapshot(String fieldId) => '\$apiPrefix/fields/$fieldId/kpi-snapshot';
}

/// field operation
abstract final class FieldOperationendpoints {
  static const String list = '\$apiPrefix/field-operations';
  static String getFieldOperationendpoints(String operationId) => '\$apiPrefix/field-operations/$operationId';
  static String update(String operationId) => '\$apiPrefix/field-operations/$operationId';
  static String delete(String operationId) => '\$apiPrefix/field-operations/$operationId';
  static String listByField(String fieldId) => '\$apiPrefix/fields/$fieldId/operations';
  static String create(String fieldId) => '\$apiPrefix/fields/$fieldId/operations';
  static String approve(String operationId) => '\$apiPrefix/field-operations/$operationId/approve';
  static String reject(String operationId) => '\$apiPrefix/field-operations/$operationId/reject';
}

/// field report
abstract final class FieldReportendpoints {
  static String create(String fieldId) => '\$apiPrefix/fields/$fieldId/reports';
  static String listByField(String fieldId) => '\$apiPrefix/fields/$fieldId/reports';
  static String getFieldReportendpoints(String reportId) => '\$apiPrefix/field-reports/$reportId';
  static String getContent(String reportId) => '\$apiPrefix/field-reports/$reportId/content';
}

/// field sub zone
abstract final class FieldSubZoneendpoints {
  static String listByField(String fieldId) => '\$apiPrefix/fields/$fieldId/sub-zones';
  static String create(String fieldId) => '\$apiPrefix/fields/$fieldId/sub-zones';
  static String getFieldSubZoneendpoints(String subZoneId) => '\$apiPrefix/field-sub-zones/$subZoneId';
  static String update(String subZoneId) => '\$apiPrefix/field-sub-zones/$subZoneId';
  static String delete(String subZoneId) => '\$apiPrefix/field-sub-zones/$subZoneId';
}

/// gamification
abstract final class Gamificationendpoints {
  static String profile(String userId) => '\$apiPrefix/gamification/profile/$userId';
  static const String leaderboard = '\$apiPrefix/gamification/leaderboard';
}

/// gdd
abstract final class Gddendpoints {
  static String accumulation(String fieldId) => '\$apiPrefix/gdd/fields/$fieldId/accumulation';
  static String records(String fieldId) => '\$apiPrefix/gdd/fields/$fieldId/records';
  static String calculate(String fieldId) => '\$apiPrefix/gdd/fields/$fieldId/calculate';
  static String currentStage(String fieldId) => '\$apiPrefix/gdd/fields/$fieldId/current-stage';
  static String stages(String fieldId) => '\$apiPrefix/gdd/fields/$fieldId/stages';
  static const String crops = '\$apiPrefix/gdd/crops';
  static String cropRequirements(String cropType) => '\$apiPrefix/gdd/crops/$cropType/requirements';
  static String forecast(String fieldId) => '\$apiPrefix/gdd/fields/$fieldId/forecast';
  static String settings(String fieldId) => '\$apiPrefix/gdd/fields/$fieldId/settings';
  static String compare(String fieldId) => '\$apiPrefix/gdd/fields/$fieldId/compare';
  static String trend(String fieldId) => '\$apiPrefix/gdd/fields/$fieldId/trend';
}

/// hydrology
abstract final class Hydrologyendpoints {
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

/// indicator
abstract final class Indicatorendpoints {
  static const String dashboard = '\$apiPrefix/indicators/dashboard';
  static String dashboardTenant(String tenantId) => '\$apiPrefix/indicators/dashboard/$tenantId';
  static const String summary = '\$apiPrefix/indicators/summary';
  static const String trends = '\$apiPrefix/indicators/trends';
  static String field(String fieldId) => '\$apiPrefix/indicators/field/$fieldId';
  static const String definitions = '\$apiPrefix/indicators/definitions';
  static const String alerts = '\$apiPrefix/indicators/alerts';
}

/// intelligence
abstract final class Intelligenceendpoints {
  static String fieldScore(String fieldId) => '\$apiPrefix/fields/$fieldId/intelligence/score';
  static String fieldZones(String fieldId) => '\$apiPrefix/fields/$fieldId/intelligence/zones';
  static String fieldAlerts(String fieldId) => '\$apiPrefix/fields/$fieldId/intelligence/alerts';
  static String fieldRecommendations(String fieldId) => '\$apiPrefix/fields/$fieldId/intelligence/recommendations';
  static String createTask(String alertId) => '\$apiPrefix/intelligence/alerts/$alertId/create-task';
  static const String bestDays = '\$apiPrefix/intelligence/best-days';
  static const String validateDate = '\$apiPrefix/intelligence/validate-date';
  static String fieldData(String fieldId) => '\$apiPrefix/field-intelligence/$fieldId';
}

/// inventory
abstract final class Inventoryendpoints {
  static const String list = '\$apiPrefix/inventory';
  static String getInventoryendpoints(String itemId) => '\$apiPrefix/inventory/$itemId';
  static const String create = '\$apiPrefix/inventory';
  static String update(String itemId) => '\$apiPrefix/inventory/$itemId';
  static String delete(String itemId) => '\$apiPrefix/inventory/$itemId';
  static const String stockLevels = '\$apiPrefix/inventory/stock-levels';
}

/// iot
abstract final class Iotendpoints {
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
  static const String sensors = '\$apiPrefix/iot/sensors';
  static const String actuators = '\$apiPrefix/iot/actuators';
  static const String alertRules = '\$apiPrefix/iot/alert-rules';
  static const String sensorStream = '\$apiPrefix/iot/sensors/stream';
  static const String sensorStats = '\$apiPrefix/iot/sensors/stats';
  static String sensorLatest(String sensorId) => '\$apiPrefix/iot/sensors/$sensorId/latest';
}

/// irrigation
abstract final class Irrigationendpoints {
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
  static const String pivotControl = '\$apiPrefix/irrigation/pivot/control';
  static const String efficiencyReport = '\$apiPrefix/irrigation/efficiency-report';
  static const String irrigationExecuted = '\$apiPrefix/irrigation/irrigation-executed';
  static const String calculateWithAction = '\$apiPrefix/irrigation/calculate-with-action';
  static const String pivotSpeed = '\$apiPrefix/irrigation/pivot/speed';
}

/// labor
abstract final class Laborendpoints {
  static const String workers = '\$apiPrefix/labor/workers';
  static String workerById(String workerId) => '\$apiPrefix/labor/workers/$workerId';
  static const String schedule = '\$apiPrefix/labor/schedule';
  static const String payroll = '\$apiPrefix/labor/payroll';
}

/// lab
abstract final class Labendpoints {
  static const String samples = '\$apiPrefix/lab/samples';
  static String sampleByBarcode(String barcode) => '\$apiPrefix/lab/samples/barcode/$barcode';
}

/// leveling
abstract final class Levelingendpoints {
  static const String analyze = '\$apiPrefix/leveling/analyze';
  static String plan(String fieldId) => '\$apiPrefix/leveling/plan/$fieldId';
  static String cost(String fieldId) => '\$apiPrefix/leveling/cost/$fieldId';
  static String equipment(String fieldId) => '\$apiPrefix/leveling/equipment/$fieldId';
  static const String simulate = '\$apiPrefix/leveling/simulate';
}

/// loan verification
abstract final class LoanVerificationendpoints {
  static String verify(String fieldId) => '\$apiPrefix/loans/crop-loan-verification/$fieldId';
}

/// logistics
abstract final class Logisticsendpoints {
  static const String shipments = '\$apiPrefix/logistics/shipments';
  static String shipmentGet(String shipmentId) => '\$apiPrefix/logistics/shipments/$shipmentId';
  static const String shipmentCreate = '\$apiPrefix/logistics/shipments';
  static const String vehicles = '\$apiPrefix/logistics/vehicles';
  static const String routes = '\$apiPrefix/logistics/routes';
  static String tracking(String shipmentId) => '\$apiPrefix/logistics/tracking/$shipmentId';
}

/// marketplace
abstract final class Marketplaceendpoints {
  static const String listings = '\$apiPrefix/marketplace/listings';
  static const String listingCreate = '\$apiPrefix/marketplace/listings';
  static const String products = '\$apiPrefix/marketplace/products';
  static String productGet(String productId) => '\$apiPrefix/marketplace/products/$productId';
  static String productApprove(String productId) => '\$apiPrefix/marketplace/products/$productId/approve';
  static String productReject(String productId) => '\$apiPrefix/marketplace/products/$productId/reject';
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

/// notification
abstract final class Notificationendpoints {
  static const String list = '\$apiPrefix/notifications';
  static String getNotificationendpoints(String notificationId) => '\$apiPrefix/notifications/$notificationId';
  static String markRead(String notificationId) => '\$apiPrefix/notifications/$notificationId/read';
  static const String markAllRead = '\$apiPrefix/notifications/read-all';
  static const String preferences = '\$apiPrefix/notifications/preferences';
  static const String subscribe = '\$apiPrefix/notifications/subscribe';
  static const String unsubscribe = '\$apiPrefix/notifications/unsubscribe';
}

/// partner admin client
abstract final class PartnerAdminClientendpoints {
  static const String create = '\$apiPrefix/admin/partner-auth/clients';
  static const String list = '\$apiPrefix/admin/partner-auth/clients';
  static String getPartnerAdminClientendpoints(String clientId) => '\$apiPrefix/admin/partner-auth/clients/$clientId';
  static String update(String clientId) => '\$apiPrefix/admin/partner-auth/clients/$clientId';
  static String rotateSecret(String clientId) => '\$apiPrefix/admin/partner-auth/clients/$clientId/rotate-secret';
  static String rotateApiKey(String clientId) => '\$apiPrefix/admin/partner-auth/clients/$clientId/rotate-api-key';
  static String suspend(String clientId) => '\$apiPrefix/admin/partner-auth/clients/$clientId/suspend';
  static String unsuspend(String clientId) => '\$apiPrefix/admin/partner-auth/clients/$clientId/unsuspend';
  static String revoke(String clientId) => '\$apiPrefix/admin/partner-auth/clients/$clientId';
}

/// partner admin consent
abstract final class PartnerAdminConsentendpoints {
  static const String list = '\$apiPrefix/admin/partner-auth/consents';
  static String revoke(String grantId) => '\$apiPrefix/admin/partner-auth/consents/$grantId';
}

/// partner admin signing key
abstract final class PartnerAdminSigningKeyendpoints {
  static const String list = '\$apiPrefix/admin/partner-auth/signing-keys';
  static const String rotate = '\$apiPrefix/admin/partner-auth/signing-keys/rotate';
  static String delete(String kid) => '\$apiPrefix/admin/partner-auth/signing-keys/$kid';
}

/// partner admin token
abstract final class PartnerAdminTokenendpoints {
  static const String listAccess = '\$apiPrefix/admin/partner-auth/tokens/access';
  static const String listRefresh = '\$apiPrefix/admin/partner-auth/tokens/refresh';
  static String revokeAllForClient(String clientId) => '\$apiPrefix/admin/partner-auth/tokens/revoke-all/client/$clientId';
  static String revokeAllForUser(String userId) => '\$apiPrefix/admin/partner-auth/tokens/revoke-all/user/$userId';
}

/// partner boundary
abstract final class PartnerBoundaryendpoints {
  static const String create = '/partner/v1/boundaries';
  static String getPartnerBoundaryendpoints(String boundaryId) => '/partner/v1/boundaries/$boundaryId';
  static const String batchQuery = '/partner/v1/boundaries/query';
}

/// partner export
abstract final class PartnerExportendpoints {
  static const String create = '/partner/v1/exports';
  static String status(String exportId) => '/partner/v1/exports/$exportId/status';
  static String contents(String exportId) => '/partner/v1/exports/$exportId/contents';
}

/// partner field
abstract final class PartnerFieldendpoints {
  static const String list = '/partner/v1/fields';
  static const String listAll = '/partner/v1/fields/all';
  static String getPartnerFieldendpoints(String fieldId) => '/partner/v1/fields/$fieldId';
}

/// partner layer
abstract final class PartnerLayerendpoints {
  static const String asPlantedList = '/partner/v1/layers/asPlanted';
  static String asPlantedContents(String activityId) => '/partner/v1/layers/asPlanted/$activityId/contents';
  static const String asHarvestedList = '/partner/v1/layers/asHarvested';
  static String asHarvestedContents(String activityId) => '/partner/v1/layers/asHarvested/$activityId/contents';
  static const String asAppliedList = '/partner/v1/layers/asApplied';
  static String asAppliedContents(String activityId) => '/partner/v1/layers/asApplied/$activityId/contents';
  static const String scoutingList = '/partner/v1/layers/scoutingObservations';
  static String scoutingGet(String observationId) => '/partner/v1/layers/scoutingObservations/$observationId';
  static String scoutingAttachments(String observationId) => '/partner/v1/layers/scoutingObservations/$observationId/attachments';
  static String scoutingAttachmentContents(String observationId, String attachmentId) => '/partner/v1/layers/scoutingObservations/$observationId/attachments/$attachmentId/contents';
}

/// partner oauth
abstract final class PartnerOauthendpoints {
  static const String authorize = '/partner/v1/oauth/authorize';
  static const String token = '/partner/v1/oauth/token';
  static const String revoke = '/partner/v1/oauth/revoke';
  static const String introspect = '/partner/v1/oauth/introspect';
  static const String userinfo = '/partner/v1/oauth/userinfo';
  static const String discovery = '/.well-known/openid-configuration';
  static const String jwks = '/.well-known/jwks.json';
}

/// partner org
abstract final class PartnerOrgendpoints {
  static String resourceOwner(String resourceOwnerId) => '/partner/v1/resourceOwners/$resourceOwnerId';
  static String farmOrg(String farmOrganizationType, String farmOrganizationId) => '/partner/v1/farmOrganizations/$farmOrganizationType/$farmOrganizationId';
  static const String operations = '/partner/v1/operations/all';
}

/// partner upload
abstract final class PartnerUploadendpoints {
  static const String create = '/partner/v1/uploads';
  static String chunk(String uploadId) => '/partner/v1/uploads/$uploadId';
  static String status(String uploadId) => '/partner/v1/uploads/$uploadId/status';
  static const String batchStatus = '/partner/v1/uploads/status/query';
  static String cancel(String uploadId) => '/partner/v1/uploads/$uploadId';
}

/// payment
abstract final class Paymentendpoints {
  static const String deposit = '\$apiPrefix/payment/deposit';
  static const String withdraw = '\$apiPrefix/payment/withdraw';
  static const String transfer = '\$apiPrefix/payment/transfer';
  static const String topup = '\$apiPrefix/payment/topup';
  static String status(String transactionId) => '\$apiPrefix/payment/status/$transactionId';
  static const String transactions = '\$apiPrefix/payment/transactions';
  static String balance(String walletId) => '\$apiPrefix/payment/balance/$walletId';
  static const String validatePhone = '\$apiPrefix/payment/validate-phone';
  static const String operators = '\$apiPrefix/payment/operators';
  static String cancel(String transactionId) => '\$apiPrefix/payment/cancel/$transactionId';
}

/// pest
abstract final class Pestendpoints {
  static const String list = '\$apiPrefix/pests';
  static String byCrop(String cropType) => '\$apiPrefix/pests/crop/$cropType';
  static const String identify = '\$apiPrefix/pests/identify';
  static const String treatmentRecommend = '\$apiPrefix/treatments/recommend';
}

/// precision
abstract final class Precisionendpoints {
  static String vra(String fieldId) => '\$apiPrefix/precision-agriculture/vra/$fieldId';
  static String gdd(String fieldId) => '\$apiPrefix/precision-agriculture/gdd/$fieldId';
  static const String fertilizerCalculate = '\$apiPrefix/precision-agriculture/fertilizer/calculate';
}

/// provider
abstract final class Providerendpoints {
  static const String list = '\$apiPrefix/providers';
  static String config(String providerId) => '\$apiPrefix/providers/$providerId/config';
  static String configUpdate(String providerId) => '\$apiPrefix/providers/$providerId/config';
  static const String providerConfigList = '\$apiPrefix/provider-config';
  static String providerConfigItem(String providerId) => '\$apiPrefix/provider-config/$providerId';
}

/// public
abstract final class Publicendpoints {
  static const String 0 = '\$apiPrefix/auth/login';
  static const String 1 = '\$apiPrefix/auth/register';
  static const String 2 = '\$apiPrefix/auth/forgot-password';
  static const String 3 = '\$apiPrefix/auth/reset-password';
  static const String 4 = '\$apiPrefix/auth/verify-otp';
  static const String 5 = '\$apiPrefix/auth/send-otp';
  static const String 6 = '/healthz';
  static const String 7 = '/readyz';
  static const String 8 = '/health';
}

/// research
abstract final class Researchendpoints {
  static const String trials = '\$apiPrefix/research/trials';
  static String trialGet(String trialId) => '\$apiPrefix/research/trials/$trialId';
  static const String trialCreate = '\$apiPrefix/research/trials';
  static String trialUpdate(String trialId) => '\$apiPrefix/research/trials/$trialId';
  static String observations(String trialId) => '\$apiPrefix/research/trials/$trialId/observations';
  static String analysis(String trialId) => '\$apiPrefix/research/trials/$trialId/analysis';
}

/// satellite
abstract final class Satelliteendpoints {
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

/// satellite monitor
abstract final class SatelliteMonitorendpoints {
  static const String fields = '\$apiPrefix/satellite-monitor/fields';
  static String fieldGet(String fieldId) => '\$apiPrefix/satellite-monitor/fields/$fieldId';
  static const String stats = '\$apiPrefix/satellite-monitor/stats';
  static const String alerts = '\$apiPrefix/satellite-monitor/alerts';
}

/// scouting
abstract final class Scoutingendpoints {
  static const String list = '\$apiPrefix/scouting/reports';
  static String getScoutingendpoints(String reportId) => '\$apiPrefix/scouting/reports/$reportId';
  static const String create = '\$apiPrefix/scouting/reports';
  static String update(String reportId) => '\$apiPrefix/scouting/reports/$reportId';
  static String delete(String reportId) => '\$apiPrefix/scouting/reports/$reportId';
  static String fieldReports(String fieldId) => '\$apiPrefix/scouting/fields/$fieldId/reports';
  static const String stats = '\$apiPrefix/scouting/stats';
}

/// season
abstract final class Seasonendpoints {
  static const String list = '\$apiPrefix/seasons';
  static String getSeasonendpoints(String seasonId) => '\$apiPrefix/seasons/$seasonId';
  static const String create = '\$apiPrefix/seasons';
  static String update(String seasonId) => '\$apiPrefix/seasons/$seasonId';
  static String delete(String seasonId) => '\$apiPrefix/seasons/$seasonId';
  static const String active = '\$apiPrefix/seasons/active';
}

/// seed
abstract final class Seedendpoints {
  static const String list = '\$apiPrefix/seeds';
  static String getSeedendpoints(String seedId) => '\$apiPrefix/seeds/$seedId';
  static const String recommendations = '\$apiPrefix/seeds/recommendations';
}

/// soil
abstract final class Soilendpoints {
  static const String tests = '\$apiPrefix/soil/tests';
  static String testGet(String testId) => '\$apiPrefix/soil/tests/$testId';
  static const String testCreate = '\$apiPrefix/soil/tests';
  static String testUpdate(String testId) => '\$apiPrefix/soil/tests/$testId';
  static String testDelete(String testId) => '\$apiPrefix/soil/tests/$testId';
  static String testsByFieldLegacy(String fieldId) => '\$apiPrefix/soil/fields/$fieldId/tests';
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
  static String testsByField(String fieldId) => '\$apiPrefix/soil/tests/field/$fieldId';
  static const String products = '\$apiPrefix/soil/products';
  static String cropRequirements(String crop) => '\$apiPrefix/soil/crops/$crop/requirements';
  static const String interpret = '\$apiPrefix/soil/interpret';
  static const String amendmentPlan = '\$apiPrefix/soil/recommendations/amendment-plan';
  static const String phStatus = '\$apiPrefix/soil/interpretation/ph-status';
  static const String ecStatus = '\$apiPrefix/soil/interpretation/ec-status';
}

/// support
abstract final class Supportendpoints {
  static const String tickets = '\$apiPrefix/support/tickets';
  static String ticketById(String ticketId) => '\$apiPrefix/support/tickets/$ticketId';
}

/// task
abstract final class Taskendpoints {
  static const String list = '\$apiPrefix/tasks';
  static String getTaskendpoints(String taskId) => '\$apiPrefix/tasks/$taskId';
  static const String create = '\$apiPrefix/tasks';
  static String update(String taskId) => '\$apiPrefix/tasks/$taskId';
  static String delete(String taskId) => '\$apiPrefix/tasks/$taskId';
  static String status(String taskId) => '\$apiPrefix/tasks/$taskId/status';
  static String complete(String taskId) => '\$apiPrefix/tasks/$taskId/complete';
  static String assign(String taskId) => '\$apiPrefix/tasks/$taskId/assign';
}

/// team
abstract final class Teamendpoints {
  static const String members = '\$apiPrefix/team/members';
  static String memberGet(String memberId) => '\$apiPrefix/team/members/$memberId';
  static const String memberInvite = '\$apiPrefix/team/members/invite';
  static String memberRemove(String memberId) => '\$apiPrefix/team/members/$memberId';
  static String memberRole(String memberId) => '\$apiPrefix/team/members/$memberId/role';
  static const String roles = '\$apiPrefix/team/roles';
}

/// terrain
abstract final class Terrainendpoints {
  static const String dem = '\$apiPrefix/terrain/dem';
  static const String slope = '\$apiPrefix/terrain/slope';
  static String aspect(String fieldId) => '\$apiPrefix/terrain/aspect/$fieldId';
  static String hydrologyDrainage(String fieldId) => '\$apiPrefix/hydrology/drainage/$fieldId';
  static String hydrologyWatershed(String fieldId) => '\$apiPrefix/hydrology/basins/$fieldId';
  static String hydrologyFlow(String fieldId) => '\$apiPrefix/terrain/flow/$fieldId';
  static const String levelingOptimize = '\$apiPrefix/leveling/analyze';
  static const String levelingCutFill = '\$apiPrefix/leveling/cut-fill';
  static String levelingCost(String fieldId) => '\$apiPrefix/leveling/cost/$fieldId';
  static const String erosion = '\$apiPrefix/terrain/erosion';
  static const String erosionWind = '\$apiPrefix/terrain/erosion/wind';
  static const String erosionCombined = '\$apiPrefix/terrain/erosion/combined';
  static const String erosionYemen = '\$apiPrefix/terrain/erosion/yemen';
  static String demField(String fieldId) => '\$apiPrefix/terrain/dem/$fieldId';
  static String slopeField(String fieldId) => '\$apiPrefix/terrain/slope/$fieldId';
  static String twi(String fieldId) => '\$apiPrefix/terrain/twi/$fieldId';
  static String contours(String fieldId) => '\$apiPrefix/terrain/contours/$fieldId';
  static const String analyze = '\$apiPrefix/terrain/analyze';
}

/// traceability
abstract final class Traceabilityendpoints {
  static const String batches = '\$apiPrefix/traceability/batches';
  static String batchGet(String batchId) => '\$apiPrefix/traceability/batches/$batchId';
  static const String events = '\$apiPrefix/traceability/events';
  static String qrCode(String batchId) => '\$apiPrefix/traceability/batches/$batchId/qr';
  static String batchEvents(String batchId) => '\$apiPrefix/traceability/batches/$batchId/events';
  static String anchorsList(String tenantId, String fieldId) => '\$apiPrefix/traceability/anchors/$tenantId/$fieldId';
  static String anchorsVerify(String tenantId, String fieldId) => '\$apiPrefix/traceability/anchors/$tenantId/$fieldId/verify';
  static const String anchorsStats = '\$apiPrefix/traceability/anchors/stats';
}

/// upload
abstract final class Uploadendpoints {
  static const String create = '\$apiPrefix/uploads';
  static String chunk(String uploadId) => '\$apiPrefix/uploads/$uploadId';
  static String status(String uploadId) => '\$apiPrefix/uploads/$uploadId/status';
  static const String batchStatus = '\$apiPrefix/uploads/status/query';
  static String cancel(String uploadId) => '\$apiPrefix/uploads/$uploadId';
}

/// user
abstract final class Userendpoints {
  static const String list = '\$apiPrefix/users';
  static String getUserendpoints(String userId) => '\$apiPrefix/users/$userId';
  static const String create = '\$apiPrefix/users';
  static String update(String userId) => '\$apiPrefix/users/$userId';
  static String delete(String userId) => '\$apiPrefix/users/$userId';
  static String block(String userId) => '\$apiPrefix/users/$userId/block';
}

/// vegetation
abstract final class Vegetationendpoints {
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

/// virtual sensor
abstract final class VirtualSensorendpoints {
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

/// vision
abstract final class Visionendpoints {
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

/// vra
abstract final class Vraendpoints {
  static const String maps = '\$apiPrefix/vra/maps';
  static String mapGet(String mapId) => '\$apiPrefix/vra/maps/$mapId';
  static const String mapCreate = '\$apiPrefix/vra/maps';
  static const String prescriptions = '\$apiPrefix/vra/prescriptions';
  static String prescriptionGet(String prescriptionId) => '\$apiPrefix/vra/prescriptions/$prescriptionId';
  static String zones(String fieldId) => '\$apiPrefix/vra/zones/$fieldId';
}

/// weather
abstract final class Weatherendpoints {
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
  static String fieldGraphGenerate(String fieldId) => '\$apiPrefix/weather/fields/$fieldId/graph';
  static String fieldGraphFetch(String graphId) => '\$apiPrefix/weather/graphs/$graphId';
  static const String kongCurrent = '\$apiPrefix/weather/weather/current';
  static const String kongForecast = '\$apiPrefix/weather/weather/forecast';
  static const String kongAgriculturalReport = '\$apiPrefix/weather/weather/agricultural-report';
  static String kongCurrentByLocation(String locationId) => '\$apiPrefix/weather/v1/current/$locationId';
  static String kongForecastByLocation(String locationId) => '\$apiPrefix/weather/v1/forecast/$locationId';
  static const String kongLocations = '\$apiPrefix/weather/v1/locations';
  static const String weatherCoreCurrent = '\$apiPrefix/weather-core/weather/current';
  static const String weatherCoreForecast = '\$apiPrefix/weather-core/weather/forecast';
  static const String weatherCoreAgReport = '\$apiPrefix/weather-core/weather/agricultural-report';
  static const String gdd = '\$apiPrefix/weather/gdd';
  static const String sprayWindows = '\$apiPrefix/weather/spray-windows';
}

/// yield
abstract final class Yieldendpoints {
  static String predict(String fieldId) => '\$apiPrefix/yield/fields/$fieldId/predict';
  static String history(String fieldId) => '\$apiPrefix/yield/fields/$fieldId/history';
  static const String predictPost = '\$apiPrefix/yield/predict';
  static const String predictions = '\$apiPrefix/yield/predictions';
  static const String profitability = '\$apiPrefix/yield/profitability';
}
