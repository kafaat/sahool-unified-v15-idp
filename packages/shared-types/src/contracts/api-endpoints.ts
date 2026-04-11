/**
 * SAHOOL Unified API Endpoint Paths
 * مسارات نقاط النهاية الموحدة
 *
 * Single source of truth for all API endpoint paths.
 * Used by: Web, Admin, Mobile, api-client, Kong Gateway configuration.
 *
 * Conventions:
 * - All paths start with /api/v1/ (routed through Kong Gateway)
 * - {param} indicates a path parameter
 * - Paths are grouped by service domain
 *
 * @module @sahool/shared-types/contracts
 * @version 16.0.0
 */

// ---------------------------------------------------------------------------
// API Version - إصدار الـ API
// ---------------------------------------------------------------------------

export const API_VERSION = 'v1' as const;
export const API_PREFIX = `/api/${API_VERSION}` as const;

// ---------------------------------------------------------------------------
// Health & Infrastructure Endpoints
// ---------------------------------------------------------------------------

export const HEALTH_ENDPOINTS = {
  LIVENESS: '/healthz',
  READINESS: '/readyz',
  HEALTH: '/health',
  METRICS: '/metrics',
} as const;

// ---------------------------------------------------------------------------
// Auth Endpoints - نقاط المصادقة
// ---------------------------------------------------------------------------

export const AUTH_ENDPOINTS = {
  LOGIN: `${API_PREFIX}/auth/login`,
  LOGOUT: `${API_PREFIX}/auth/logout`,
  REFRESH: `${API_PREFIX}/auth/refresh`,
  ME: `${API_PREFIX}/auth/me`,
  REGISTER: `${API_PREFIX}/auth/register`,
  FORGOT_PASSWORD: `${API_PREFIX}/auth/forgot-password`,
  RESET_PASSWORD: `${API_PREFIX}/auth/reset-password`,
  VERIFY_OTP: `${API_PREFIX}/auth/verify-otp`,
  SEND_OTP: `${API_PREFIX}/auth/send-otp`,
  RESEND_OTP: `${API_PREFIX}/auth/resend-otp`,
  ACTIVITY: `${API_PREFIX}/auth/activity`,
} as const;

// ---------------------------------------------------------------------------
// Field Management Endpoints - نقاط إدارة الحقول
// ---------------------------------------------------------------------------

export const FIELD_ENDPOINTS = {
  LIST: `${API_PREFIX}/fields`,
  GET: `${API_PREFIX}/fields/{fieldId}`,
  CREATE: `${API_PREFIX}/fields`,
  UPDATE: `${API_PREFIX}/fields/{fieldId}`,
  DELETE: `${API_PREFIX}/fields/{fieldId}`,
  NEARBY: `${API_PREFIX}/fields/nearby`,
  SYNC: `${API_PREFIX}/fields/sync`,
  SYNC_BATCH: `${API_PREFIX}/fields/sync/batch`,
  BOUNDARY: `${API_PREFIX}/field-core/fields/{fieldId}/boundary`,
  BOUNDARY_UPDATE: `${API_PREFIX}/field-core/fields/{fieldId}/boundary`,
  BOUNDARY_HISTORY: `${API_PREFIX}/field-core/fields/{fieldId}/boundary-history`,
  BOUNDARY_ROLLBACK: `${API_PREFIX}/field-core/fields/{fieldId}/boundary-history/rollback`,
} as const;

// ---------------------------------------------------------------------------
// Crop Season Endpoints - نقاط مواسم المحاصيل
// First-class crop rotation archive. Replaces the earlier
// `field.metadata.cropHistory[]` JSON shim with a proper relational API.
// Served by field-management-service (port 3000, Kong-routed).
// ---------------------------------------------------------------------------

export const CROP_SEASON_ENDPOINTS = {
  /** List crop seasons tenant-wide (with optional filters) */
  LIST: `${API_PREFIX}/crop-seasons`,
  /** Get a specific season by id */
  GET: `${API_PREFIX}/crop-seasons/{cropSeasonId}`,
  /** Partial update (PATCH) */
  UPDATE: `${API_PREFIX}/crop-seasons/{cropSeasonId}`,
  /** End an active season (soft close) */
  END: `${API_PREFIX}/crop-seasons/{cropSeasonId}/end`,
  /** Hard delete (rare) */
  DELETE: `${API_PREFIX}/crop-seasons/{cropSeasonId}`,
  /** List all seasons for one field */
  LIST_BY_FIELD: `${API_PREFIX}/fields/{fieldId}/crop-seasons`,
  /** Start a new season on a field (automatically closes the previous) */
  CREATE: `${API_PREFIX}/fields/{fieldId}/crop-seasons`,
  /** Per-season operation rollup (hours + cost) */
  ROLLUP: `${API_PREFIX}/crop-seasons/{cropSeasonId}/rollup`,
} as const;

// ---------------------------------------------------------------------------
// Field Operation Endpoints - نقاط عمليات الحقل
// Per-field operation log (plowing, land prep, fertilization, spraying, ...).
// Links to CropSeason + Equipment for per-season and per-equipment rollups.
// ---------------------------------------------------------------------------

export const FIELD_OPERATION_ENDPOINTS = {
  /** Tenant-wide list with filters */
  LIST: `${API_PREFIX}/field-operations`,
  /** Get an operation by id */
  GET: `${API_PREFIX}/field-operations/{operationId}`,
  /** Partial update */
  UPDATE: `${API_PREFIX}/field-operations/{operationId}`,
  /** Soft-delete (SOX/IFRS audit safe) */
  DELETE: `${API_PREFIX}/field-operations/{operationId}`,
  /** List all operations for one field */
  LIST_BY_FIELD: `${API_PREFIX}/fields/{fieldId}/operations`,
  /** Record a new operation against a field */
  CREATE: `${API_PREFIX}/fields/{fieldId}/operations`,
  /** Approve a pending operation (required before ERP posting) */
  APPROVE: `${API_PREFIX}/field-operations/{operationId}/approve`,
  /** Reject a pending operation with a mandatory reason */
  REJECT: `${API_PREFIX}/field-operations/{operationId}/reject`,
} as const;

// ---------------------------------------------------------------------------
// Field Sub-Zone Endpoints - المناطق الفرعية للحقل
// Multi-polygon sub-zones within a single Field. Critical for terraced
// Yemeni farms where one "field" is actually many small terraces with
// different elevation, slope, aspect, and crop performance.
// ---------------------------------------------------------------------------

export const FIELD_SUB_ZONE_ENDPOINTS = {
  /** List all sub-zones for a field (ordered by display_order) */
  LIST_BY_FIELD: `${API_PREFIX}/fields/{fieldId}/sub-zones`,
  /** Create a new sub-zone under a field */
  CREATE: `${API_PREFIX}/fields/{fieldId}/sub-zones`,
  /** Get a sub-zone by id */
  GET: `${API_PREFIX}/field-sub-zones/{subZoneId}`,
  /** Partial update */
  UPDATE: `${API_PREFIX}/field-sub-zones/{subZoneId}`,
  /** Soft-delete */
  DELETE: `${API_PREFIX}/field-sub-zones/{subZoneId}`,
} as const;

// ---------------------------------------------------------------------------
// Field Report Endpoints - تقارير الحقل
// Async HTML/PDF report generation, Arabic RTL first. Caller POSTs a
// request and polls for status until 'ready', then fetches the content
// via the signed URL or the /content endpoint (depending on storage).
// ---------------------------------------------------------------------------

export const FIELD_REPORT_ENDPOINTS = {
  /** Enqueue a new report (returns 202 with pending row) */
  CREATE: `${API_PREFIX}/fields/{fieldId}/reports`,
  /** List reports for a field */
  LIST_BY_FIELD: `${API_PREFIX}/fields/{fieldId}/reports`,
  /** Get report metadata (poll for status) */
  GET: `${API_PREFIX}/field-reports/{reportId}`,
  /** Stream the rendered HTML content */
  GET_CONTENT: `${API_PREFIX}/field-reports/{reportId}/content`,
} as const;

// ---------------------------------------------------------------------------
// Carbon Footprint Endpoints - البصمة الكربونية (IPCC Tier 1)
// Served by carbon-service (port 8195). Aggregates per-operation CO2e
// into per-field and per-season dashboards. See src/engine/ipcc_tier1.py
// for the factor table.
// ---------------------------------------------------------------------------

export const CARBON_ENDPOINTS = {
  /** Stateless what-if compute — no persistence */
  COMPUTE: `${API_PREFIX}/carbon/compute`,
  /** DB-backed compute — persists results on the field_operations row */
  COMPUTE_OPERATION: `${API_PREFIX}/carbon/operations/{operationId}/compute`,
  /** Per-field aggregate (emissions + sequestration + net by source) */
  FIELD_SUMMARY: `${API_PREFIX}/carbon/fields/{fieldId}/summary`,
  /** Per-season aggregate (with by-operation-type breakdown) */
  CROP_SEASON_SUMMARY: `${API_PREFIX}/carbon/crop-seasons/{cropSeasonId}/summary`,
} as const;

// ---------------------------------------------------------------------------
// ERP Sync Endpoints - تكامل نظام المحاسبة
// Routes for posting field operations / crop seasons to external accounting
// systems (QuickBooks, SAP, Odoo, Xero, Oracle NetSuite, ...) via the
// pluggable IErpAdapter interface in field-management-service.
// ---------------------------------------------------------------------------

export const ERP_SYNC_ENDPOINTS = {
  /** Post a single field operation to every enabled ERP adapter */
  POST_FIELD_OPERATION: `${API_PREFIX}/erp-sync/field-operations/{operationId}/post`,
  /** Health check — returns reachability of each configured adapter */
  HEALTH: `${API_PREFIX}/erp-sync/health`,
} as const;

// ---------------------------------------------------------------------------
// Weather Endpoints - نقاط الطقس
// ---------------------------------------------------------------------------

export const WEATHER_ENDPOINTS = {
  CURRENT: `${API_PREFIX}/weather/current`,
  CURRENT_BY_LOCATION: `${API_PREFIX}/weather/current/{locationId}`,
  FORECAST: `${API_PREFIX}/weather/forecast`,
  FORECAST_BY_LOCATION: `${API_PREFIX}/weather/forecast/{locationId}`,
  FORECAST_BY_FIELD: `${API_PREFIX}/weather/forecast/field/{fieldId}`,
  ALERTS: `${API_PREFIX}/weather/alerts`,
  ALERTS_BY_LOCATION: `${API_PREFIX}/weather/alerts/{locationId}`,
  ALERTS_BY_FIELD: `${API_PREFIX}/weather/alerts/field/{fieldId}`,
  LOCATIONS: `${API_PREFIX}/weather/locations`,
  AGRICULTURAL_CALENDAR: `${API_PREFIX}/weather/agricultural-calendar`,
  /** @deprecated Use WEATHER_ENDPOINTS.CURRENT instead. WEATHER_CORE has been consolidated into WEATHER. Removal: v18.0.0 */
  WEATHER_CORE_CURRENT: `${API_PREFIX}/weather-core/weather/current`,
  /** @deprecated Use WEATHER_ENDPOINTS.FORECAST instead. WEATHER_CORE has been consolidated into WEATHER. Removal: v18.0.0 */
  WEATHER_CORE_FORECAST: `${API_PREFIX}/weather-core/weather/forecast`,
  /** @deprecated Use WEATHER_ENDPOINTS.AGRICULTURAL_CALENDAR instead. WEATHER_CORE has been consolidated into WEATHER. Removal: v18.0.0 */
  WEATHER_CORE_AG_REPORT: `${API_PREFIX}/weather-core/weather/agricultural-report`,
} as const;

// ---------------------------------------------------------------------------
// Satellite & NDVI Endpoints - نقاط الأقمار الصناعية
// ---------------------------------------------------------------------------

export const SATELLITE_ENDPOINTS = {
  ANALYZE: `${API_PREFIX}/satellite/v1/analyze`,
  ANALYZE_FIELD: `${API_PREFIX}/satellite/analyze/{fieldId}`,
  TIMESERIES: `${API_PREFIX}/satellite/v1/timeseries/{fieldId}`,
  INDICES: `${API_PREFIX}/satellite/v1/indices/{fieldId}`,
  SATELLITES: `${API_PREFIX}/satellite/v1/satellites`,
  HEALTH: `${API_PREFIX}/satellite/health/{fieldId}`,
  PHENOLOGY: `${API_PREFIX}/satellite/phenology/{fieldId}`,
  IMAGERY: `${API_PREFIX}/satellite/imagery/{fieldId}`,
  NDVI_FIELD: `${API_PREFIX}/fields/{fieldId}/ndvi`,
  NDVI_SUMMARY: `${API_PREFIX}/ndvi/summary`,
} as const;

// ---------------------------------------------------------------------------
// Crop Health & Intelligence Endpoints - نقاط صحة المحاصيل
// ---------------------------------------------------------------------------

export const CROP_HEALTH_ENDPOINTS = {
  ANALYZE: `${API_PREFIX}/crop-health/analyze`,
  DIAGNOSE: `${API_PREFIX}/crop-health/diagnose`,
  DIAGNOSE_BATCH: `${API_PREFIX}/crop-health/diagnose/batch`,
  DECISION: `${API_PREFIX}/crop-health/decision`,
  HISTORY: `${API_PREFIX}/crop-health/fields/{fieldId}/history`,
  CROPS: `${API_PREFIX}/crop-health/crops`,
  DISEASES: `${API_PREFIX}/crop-health/diseases`,
  TREATMENT: `${API_PREFIX}/crop-health/treatment/{diseaseId}`,
  EXPERT_REVIEW: `${API_PREFIX}/crop-health/expert-review`,
  DIAGNOSES_LIST: `${API_PREFIX}/crop-health/diagnoses`,
  DIAGNOSES_STATS: `${API_PREFIX}/crop-health/diagnoses/stats`,
  DIAGNOSES_UPDATE: `${API_PREFIX}/crop-health/diagnoses/{diagnosisId}`,
} as const;

// ---------------------------------------------------------------------------
// Irrigation Endpoints - نقاط الري
// ---------------------------------------------------------------------------

export const IRRIGATION_ENDPOINTS = {
  RECOMMENDATION: `${API_PREFIX}/irrigation/fields/{fieldId}/recommendation`,
  CALCULATE: `${API_PREFIX}/irrigation/calculate`,
  ET0: `${API_PREFIX}/irrigation/et0`,
  WATER_BALANCE: `${API_PREFIX}/irrigation/water-balance`,
  SENSOR_READING: `${API_PREFIX}/irrigation/sensor-reading`,
  EFFICIENCY: `${API_PREFIX}/irrigation/efficiency`,
  SCHEDULE: `${API_PREFIX}/irrigation/schedule`,
  SCHEDULES_LIST: `${API_PREFIX}/irrigation/schedules`,
  SCHEDULES_GET: `${API_PREFIX}/irrigation/schedules/{scheduleId}`,
  SCHEDULES_CREATE: `${API_PREFIX}/irrigation/schedules`,
  SCHEDULES_UPDATE: `${API_PREFIX}/irrigation/schedules/{scheduleId}`,
  SCHEDULES_DELETE: `${API_PREFIX}/irrigation/schedules/{scheduleId}`,
  HISTORY: `${API_PREFIX}/irrigation/history/{fieldId}`,
  RECOMMENDATIONS: `${API_PREFIX}/irrigation/recommendations`,
  CROPS: `${API_PREFIX}/irrigation/crops`,
  METHODS: `${API_PREFIX}/irrigation/methods`,
  PIVOT_CONTROL: `${API_PREFIX}/irrigation/pivot/control`,
} as const;

// ---------------------------------------------------------------------------
// Advisory & Fertilizer Endpoints - نقاط الاستشارات والتسميد
// ---------------------------------------------------------------------------

export const ADVISORY_ENDPOINTS = {
  RECOMMEND: `${API_PREFIX}/fertilizer/recommend`,
  SOIL_INTERPRET: `${API_PREFIX}/fertilizer/soil/interpret`,
  CROPS: `${API_PREFIX}/fertilizer/crops`,
  FERTILIZERS: `${API_PREFIX}/fertilizer/fertilizers`,
  DEFICIENCY_SYMPTOMS: `${API_PREFIX}/fertilizer/deficiency/symptoms`,
  SCHEDULE: `${API_PREFIX}/fertilizer/schedule`,
  RECOMMENDATIONS: `${API_PREFIX}/advisory/recommendations`,
  FERTILIZER_ADVISORY: `${API_PREFIX}/advisory/fertilizer`,
  FERTILIZER_CALCULATE: `${API_PREFIX}/advisory/fertilizer/calculate`,
  FERTILIZER_UPDATE: `${API_PREFIX}/advisory/fertilizer/{prescriptionId}`,
  FERTILIZER_ZONE_UPDATE: `${API_PREFIX}/advisory/fertilizer/{prescriptionId}/zones/{zoneId}`,
  AGRO_ADVICE: `${API_PREFIX}/agro-advisor/advice`,
  AGRO_DISEASE: `${API_PREFIX}/agro-advisor/disease`,
  AGRO_NUTRIENTS: `${API_PREFIX}/agro-advisor/nutrients`,
} as const;

// ---------------------------------------------------------------------------
// Task Endpoints - نقاط المهام
// ---------------------------------------------------------------------------

export const TASK_ENDPOINTS = {
  LIST: `${API_PREFIX}/tasks`,
  GET: `${API_PREFIX}/tasks/{taskId}`,
  CREATE: `${API_PREFIX}/tasks`,
  UPDATE: `${API_PREFIX}/tasks/{taskId}`,
  DELETE: `${API_PREFIX}/tasks/{taskId}`,
  STATUS: `${API_PREFIX}/tasks/{taskId}/status`,
  COMPLETE: `${API_PREFIX}/tasks/{taskId}/complete`,
} as const;

// ---------------------------------------------------------------------------
// Equipment Endpoints - نقاط المعدات
// ---------------------------------------------------------------------------

export const EQUIPMENT_ENDPOINTS = {
  LIST: `${API_PREFIX}/equipment`,
  GET: `${API_PREFIX}/equipment/{equipmentId}`,
  CREATE: `${API_PREFIX}/equipment`,
  UPDATE: `${API_PREFIX}/equipment/{equipmentId}`,
  DELETE: `${API_PREFIX}/equipment/{equipmentId}`,
  STATUS: `${API_PREFIX}/equipment/{equipmentId}/status`,
  MAINTENANCE: `${API_PREFIX}/equipment/{equipmentId}/maintenance`,
  QR_LOOKUP: `${API_PREFIX}/equipment/qr/{qrCode}`,
  STATS: `${API_PREFIX}/equipment/stats`,
  MAINTENANCE_ALERTS: `${API_PREFIX}/equipment/maintenance/alerts`,
} as const;

// ---------------------------------------------------------------------------
// Alert Endpoints - نقاط التنبيهات
// ---------------------------------------------------------------------------

export const ALERT_ENDPOINTS = {
  LIST: `${API_PREFIX}/alerts`,
  GET: `${API_PREFIX}/alerts/{alertId}`,
  CREATE: `${API_PREFIX}/alerts`,
  DELETE: `${API_PREFIX}/alerts/{alertId}`,
  ACKNOWLEDGE: `${API_PREFIX}/alerts/{alertId}/acknowledge`,
  RESOLVE: `${API_PREFIX}/alerts/{alertId}/resolve`,
  DISMISS: `${API_PREFIX}/alerts/{alertId}/dismiss`,
  RULES: `${API_PREFIX}/alerts/rules`,
} as const;

// ---------------------------------------------------------------------------
// Notification Endpoints - نقاط الإشعارات
// ---------------------------------------------------------------------------

export const NOTIFICATION_ENDPOINTS = {
  LIST: `${API_PREFIX}/notifications`,
  GET: `${API_PREFIX}/notifications/{notificationId}`,
  MARK_READ: `${API_PREFIX}/notifications/{notificationId}/read`,
  MARK_ALL_READ: `${API_PREFIX}/notifications/read-all`,
  PREFERENCES: `${API_PREFIX}/notifications/preferences`,
  SUBSCRIBE: `${API_PREFIX}/notifications/subscribe`,
  UNSUBSCRIBE: `${API_PREFIX}/notifications/unsubscribe`,
} as const;

// ---------------------------------------------------------------------------
// IoT & Sensor Endpoints - نقاط إنترنت الأشياء
// ---------------------------------------------------------------------------

export const IOT_ENDPOINTS = {
  DEVICES: `${API_PREFIX}/iot/devices`,
  DEVICE_GET: `${API_PREFIX}/iot/devices/{deviceId}`,
  DEVICE_CREATE: `${API_PREFIX}/iot/devices`,
  DEVICE_UPDATE: `${API_PREFIX}/iot/devices/{deviceId}`,
  DEVICE_DELETE: `${API_PREFIX}/iot/devices/{deviceId}`,
  DEVICE_READINGS: `${API_PREFIX}/iot/sensors/{deviceId}/readings`,
  DEVICE_COMMAND: `${API_PREFIX}/iot/devices/{deviceId}/command`,
  DEVICE_TYPES: `${API_PREFIX}/iot/device-types`,
  FIELD_DEVICES: `${API_PREFIX}/iot/devices/field/{fieldId}`,
  FIELD_SENSORS: `${API_PREFIX}/iot/fields/{fieldId}/sensors`,
  SENSOR_HISTORY: `${API_PREFIX}/iot/sensors/{sensorId}/history`,
  READINGS_BY_FARM: `${API_PREFIX}/iot/readings/{farmId}`,
  /** @since 4.3.0 - Sensor resource collection */
  SENSORS: `${API_PREFIX}/iot/sensors`,
  /** @since 4.3.0 - Actuator resource collection */
  ACTUATORS: `${API_PREFIX}/iot/actuators`,
  /** @since 4.3.0 - Alert rule resource collection */
  ALERT_RULES: `${API_PREFIX}/iot/alert-rules`,
  /** @since 4.3.0 - Server-sent / WebSocket sensor data stream */
  SENSOR_STREAM: `${API_PREFIX}/iot/sensors/stream`,
  /** @since 4.3.0 - Aggregated sensor statistics */
  SENSOR_STATS: `${API_PREFIX}/iot/sensors/stats`,
  /** @since 4.3.0 - Latest reading for a single sensor */
  SENSOR_LATEST: `${API_PREFIX}/iot/sensors/{sensorId}/latest`,
} as const;

// ---------------------------------------------------------------------------
// Virtual Sensors Endpoints - نقاط الاستشعار الافتراضي
// ---------------------------------------------------------------------------

export const VIRTUAL_SENSOR_ENDPOINTS = {
  ET0_CALCULATE: `${API_PREFIX}/virtual-sensors/et0/calculate`,
  ETC_CALCULATE: `${API_PREFIX}/virtual-sensors/etc/calculate`,
  CROPS: `${API_PREFIX}/virtual-sensors/crops`,
  CROP_KC: `${API_PREFIX}/virtual-sensors/crops/{cropType}/kc`,
  SOILS: `${API_PREFIX}/virtual-sensors/soils`,
  SOIL_MOISTURE: `${API_PREFIX}/virtual-sensors/soil-moisture/estimate`,
  IRRIGATION_METHODS: `${API_PREFIX}/virtual-sensors/irrigation-methods`,
  IRRIGATION_RECOMMEND: `${API_PREFIX}/virtual-sensors/irrigation/recommend`,
  IRRIGATION_QUICK_CHECK: `${API_PREFIX}/virtual-sensors/irrigation/quick-check`,
} as const;

// ---------------------------------------------------------------------------
// Marketplace Endpoints - نقاط السوق
// ---------------------------------------------------------------------------

export const MARKETPLACE_ENDPOINTS = {
  LISTINGS: `${API_PREFIX}/marketplace/listings`,
  LISTING_CREATE: `${API_PREFIX}/marketplace/listings`,
  PRODUCTS: `${API_PREFIX}/marketplace/products`,
  PRODUCT_GET: `${API_PREFIX}/marketplace/products/{productId}`,
  PRODUCT_APPROVE: `${API_PREFIX}/marketplace/products/{productId}/approve`,
  PRODUCT_REJECT: `${API_PREFIX}/marketplace/products/{productId}/reject`,
  ORDERS: `${API_PREFIX}/marketplace/orders`,
  ORDERS_BY_USER: `${API_PREFIX}/marketplace/orders/user/{userId}`,
  HARVEST: `${API_PREFIX}/marketplace/harvest`,
  STATS: `${API_PREFIX}/marketplace/stats`,
  WALLET: `${API_PREFIX}/marketplace/fintech/wallet/{userId}`,
  WALLET_DEPOSIT: `${API_PREFIX}/marketplace/fintech/wallet/{walletId}/deposit`,
  WALLET_WITHDRAW: `${API_PREFIX}/marketplace/fintech/wallet/{walletId}/withdraw`,
  WALLET_TRANSACTIONS: `${API_PREFIX}/marketplace/fintech/wallet/{walletId}/transactions`,
  CREDIT_SCORE: `${API_PREFIX}/marketplace/fintech/calculate-score`,
  LOANS: `${API_PREFIX}/marketplace/fintech/loans`,
  LOANS_BY_USER: `${API_PREFIX}/marketplace/fintech/loans/{walletId}`,
  LOAN_REPAY: `${API_PREFIX}/marketplace/fintech/loans/{loanId}/repay`,
} as const;

// ---------------------------------------------------------------------------
// Billing Endpoints - نقاط الفوترة
// ---------------------------------------------------------------------------

export const BILLING_ENDPOINTS = {
  SUBSCRIPTION: `${API_PREFIX}/billing/subscription`,
  SUBSCRIPTIONS: `${API_PREFIX}/billing/subscriptions`,
  PLANS: `${API_PREFIX}/billing/plans`,
  INVOICES: `${API_PREFIX}/billing/invoices`,
  INVOICE_GET: `${API_PREFIX}/billing/invoices/{invoiceId}`,
  INVOICE_PAY: `${API_PREFIX}/billing/invoices/{invoiceId}/pay`,
  USAGE: `${API_PREFIX}/billing/usage`,
  WALLET: `${API_PREFIX}/billing/wallet`,
  WALLET_DEPOSIT: `${API_PREFIX}/billing/wallet/deposit`,
  WALLET_WITHDRAW: `${API_PREFIX}/billing/wallet/withdraw`,
  WALLET_TRANSFER: `${API_PREFIX}/billing/wallet/transfer`,
  TRANSACTIONS: `${API_PREFIX}/billing/transactions`,
  /** Tenant-scoped billing (web) */
  TENANT_SUBSCRIPTION: `${API_PREFIX}/billing/tenants/{tenantId}/subscription`,
  TENANT_INVOICES: `${API_PREFIX}/billing/tenants/{tenantId}/invoices`,
  TENANT_USAGE: `${API_PREFIX}/billing/tenants/{tenantId}/usage`,
} as const;

// ---------------------------------------------------------------------------
// Chat & Community Endpoints - نقاط الدردشة والمجتمع
// ---------------------------------------------------------------------------

export const CHAT_ENDPOINTS = {
  CONVERSATIONS: `${API_PREFIX}/chat/conversations`,
  CONVERSATION_GET: `${API_PREFIX}/chat/conversations/{conversationId}`,
  MESSAGES: `${API_PREFIX}/chat/conversations/{conversationId}/messages`,
  SEND_MESSAGE: `${API_PREFIX}/chat/conversations/{conversationId}/messages`,
  MARK_READ: `${API_PREFIX}/chat/conversations/{conversationId}/read`,
  CREATE_CONVERSATION: `${API_PREFIX}/chat/conversations`,
  UNREAD_COUNT: `${API_PREFIX}/chat/conversations/unread-count`,
  FIELD_MESSAGES: `${API_PREFIX}/field-chat/fields/{fieldId}/messages`,
  FIELD_SEND: `${API_PREFIX}/field-chat/fields/{fieldId}/messages`,
  FIELD_PARTICIPANTS: `${API_PREFIX}/field-chat/fields/{fieldId}/participants`,
  COMMUNITY_POSTS: `${API_PREFIX}/posts`,
  COMMUNITY_POST_GET: `${API_PREFIX}/posts/{postId}`,
  COMMUNITY_COMMENTS: `${API_PREFIX}/posts/{postId}/comments`,
} as const;

// ---------------------------------------------------------------------------
// Indicators & Intelligence Endpoints - نقاط المؤشرات
// ---------------------------------------------------------------------------

export const INDICATOR_ENDPOINTS = {
  DASHBOARD: `${API_PREFIX}/indicators/dashboard`,
  DASHBOARD_TENANT: `${API_PREFIX}/indicators/dashboard/{tenantId}`,
  SUMMARY: `${API_PREFIX}/indicators/summary`,
  TRENDS: `${API_PREFIX}/indicators/trends`,
  FIELD: `${API_PREFIX}/indicators/field/{fieldId}`,
  DEFINITIONS: `${API_PREFIX}/indicators/definitions`,
  ALERTS: `${API_PREFIX}/indicators/alerts`,
} as const;

export const INTELLIGENCE_ENDPOINTS = {
  FIELD_SCORE: `${API_PREFIX}/fields/{fieldId}/intelligence/score`,
  FIELD_ZONES: `${API_PREFIX}/fields/{fieldId}/intelligence/zones`,
  FIELD_ALERTS: `${API_PREFIX}/fields/{fieldId}/intelligence/alerts`,
  FIELD_RECOMMENDATIONS: `${API_PREFIX}/fields/{fieldId}/intelligence/recommendations`,
  CREATE_TASK: `${API_PREFIX}/intelligence/alerts/{alertId}/create-task`,
  BEST_DAYS: `${API_PREFIX}/intelligence/best-days`,
  VALIDATE_DATE: `${API_PREFIX}/intelligence/validate-date`,
  FIELD_DATA: `${API_PREFIX}/field-intelligence/{fieldId}`,
} as const;

// ---------------------------------------------------------------------------
// Yield & Analytics Endpoints - نقاط الإنتاجية
// ---------------------------------------------------------------------------

export const YIELD_ENDPOINTS = {
  PREDICT: `${API_PREFIX}/yield/fields/{fieldId}/predict`,
  HISTORY: `${API_PREFIX}/yield/fields/{fieldId}/history`,
  PREDICT_POST: `${API_PREFIX}/yield/predict`,
  PREDICTIONS: `${API_PREFIX}/yield/predictions`,
  PROFITABILITY: `${API_PREFIX}/yield/profitability`,
} as const;

// ---------------------------------------------------------------------------
// AI & Copilot Endpoints - نقاط الذكاء الاصطناعي
// ---------------------------------------------------------------------------

export const AI_ENDPOINTS = {
  COPILOT_CHAT: `${API_PREFIX}/copilot/chat`,
  COPILOT_HISTORY: `${API_PREFIX}/copilot/chat/history`,
  COPILOT_TOOLS: `${API_PREFIX}/copilot/tools`,
  COPILOT_EXECUTE_TOOL: `${API_PREFIX}/copilot/tools/{toolName}/execute`,
  RAG_DOCUMENTS: `${API_PREFIX}/copilot/rag/documents`,
  RAG_SEARCH: `${API_PREFIX}/copilot/rag/search`,
  AI_ADVISOR_QUERY: `${API_PREFIX}/ai-advisor/query`,
  AI_ADVISOR_CHAT: `${API_PREFIX}/ai-advisor/chat`,
  AI_ADVISOR_DIAGNOSE: `${API_PREFIX}/ai-advisor/diagnose`,
  AI_ADVISOR_RECOMMENDATIONS: `${API_PREFIX}/ai-advisor/recommendations/{fieldId}`,
  AI_ADVISOR_ANALYZE: `${API_PREFIX}/ai-advisor/analyze/{fieldId}`,
  AI_ADVISOR_HISTORY: `${API_PREFIX}/ai-advisor/history`,
} as const;

// ---------------------------------------------------------------------------
// Vision Service Endpoints - نقاط الرؤية الحاسوبية
// ---------------------------------------------------------------------------

export const VISION_ENDPOINTS = {
  DETECT_PEST: `${API_PREFIX}/vision/detect/pest`,
  DETECT_DISEASE: `${API_PREFIX}/vision/detect/disease`,
  DETECT_WEED: `${API_PREFIX}/vision/detect/weed`,
  COUNT_PLANTS: `${API_PREFIX}/vision/count/plants`,
  CLASSIFY_RIPENESS: `${API_PREFIX}/vision/classify/ripeness`,
  SEGMENT_LEAF: `${API_PREFIX}/vision/segment/leaf`,
  TRACK_OBJECTS: `${API_PREFIX}/vision/track/objects`,
  TRACK_CLEAR: `${API_PREFIX}/vision/track/{trackerId}`,
  BATCH_PEST: `${API_PREFIX}/vision/batch/detect/pest`,
  BATCH_DISEASE: `${API_PREFIX}/vision/batch/detect/disease`,
  BATCH_STATUS: `${API_PREFIX}/vision/batch/status`,
  MODELS_LIST: `${API_PREFIX}/vision/models/versions`,
  MODEL_INFO: `${API_PREFIX}/vision/models/{variant}/info`,
  MODELS_WARMUP: `${API_PREFIX}/vision/models/warmup`,
  MODELS_LOADED: `${API_PREFIX}/vision/models/loaded`,
} as const;

// ---------------------------------------------------------------------------
// Terrain & Hydrology Endpoints - نقاط التضاريس
// ---------------------------------------------------------------------------

export const TERRAIN_ENDPOINTS = {
  DEM: `${API_PREFIX}/terrain/dem`,
  SLOPE: `${API_PREFIX}/terrain/slope`,
  /** @since 4.3.0 - Corrected to field-scoped path */
  ASPECT: `${API_PREFIX}/terrain/aspect/{fieldId}`,
  /** @since 4.3.0 - Corrected to field-scoped path under /hydrology/drainage */
  HYDROLOGY_DRAINAGE: `${API_PREFIX}/hydrology/drainage/{fieldId}`,
  /** @since 4.3.0 - Corrected to field-scoped path under /hydrology/basins */
  HYDROLOGY_WATERSHED: `${API_PREFIX}/hydrology/basins/{fieldId}`,
  /** @since 4.3.0 - Corrected to field-scoped path under /terrain/flow */
  HYDROLOGY_FLOW: `${API_PREFIX}/terrain/flow/{fieldId}`,
  /** @since 4.3.0 - Corrected to /leveling/analyze (cut/fill data included in response) */
  LEVELING_OPTIMIZE: `${API_PREFIX}/leveling/analyze`,
  /**
   * @deprecated Use LEVELING_OPTIMIZE instead. Cut/fill data is part of the
   * `/leveling/analyze` response body. Removal: v6.0.0
   */
  LEVELING_CUT_FILL: `${API_PREFIX}/leveling/cut-fill`,
  /** @since 4.3.0 - Corrected to field-scoped path */
  LEVELING_COST: `${API_PREFIX}/leveling/cost/{fieldId}`,
} as const;

// ---------------------------------------------------------------------------
// User Management Endpoints (Admin) - نقاط إدارة المستخدمين
// ---------------------------------------------------------------------------

export const USER_ENDPOINTS = {
  LIST: `${API_PREFIX}/users`,
  GET: `${API_PREFIX}/users/{userId}`,
  CREATE: `${API_PREFIX}/users`,
  UPDATE: `${API_PREFIX}/users/{userId}`,
  DELETE: `${API_PREFIX}/users/{userId}`,
} as const;

// ---------------------------------------------------------------------------
// Audit Endpoints (Admin) - نقاط التدقيق
// ---------------------------------------------------------------------------

export const AUDIT_ENDPOINTS = {
  LOGS: `${API_PREFIX}/audit/logs`,
  LOG_GET: `${API_PREFIX}/audit/logs/{logId}`,
  STATS: `${API_PREFIX}/audit/stats`,
  ADMIN_AUDIT: `${API_PREFIX}/admin/audit`,
  ADMIN_BATCH: `${API_PREFIX}/admin/audit/batch`,
} as const;

// ---------------------------------------------------------------------------
// Additional Domain Endpoints - نقاط إضافية
// ---------------------------------------------------------------------------

export const SOIL_ENDPOINTS = {
  TESTS: `${API_PREFIX}/soil/tests`,
  TEST_GET: `${API_PREFIX}/soil/tests/{testId}`,
  TEST_CREATE: `${API_PREFIX}/soil/tests`,
  RECOMMENDATIONS: `${API_PREFIX}/soil/recommendations`,
} as const;

export const DRONE_ENDPOINTS = {
  FLIGHTS: `${API_PREFIX}/drone/flights`,
  FLIGHT_GET: `${API_PREFIX}/drone/flights/{flightId}`,
  FLIGHT_PLAN: `${API_PREFIX}/drone/flights/plan`,
  DEVICES: `${API_PREFIX}/drone/devices`,
} as const;

export const INVENTORY_ENDPOINTS = {
  LIST: `${API_PREFIX}/inventory`,
  GET: `${API_PREFIX}/inventory/{itemId}`,
  CREATE: `${API_PREFIX}/inventory`,
  UPDATE: `${API_PREFIX}/inventory/{itemId}`,
  DELETE: `${API_PREFIX}/inventory/{itemId}`,
  STOCK_LEVELS: `${API_PREFIX}/inventory/stock-levels`,
} as const;

export const TRACEABILITY_ENDPOINTS = {
  BATCHES: `${API_PREFIX}/traceability/batches`,
  BATCH_GET: `${API_PREFIX}/traceability/batches/{batchId}`,
  EVENTS: `${API_PREFIX}/traceability/events`,
  QR_CODE: `${API_PREFIX}/traceability/batches/{batchId}/qr`,
  /** @since 4.3.0 - Events nested under a specific batch */
  BATCH_EVENTS: `${API_PREFIX}/traceability/batches/{batchId}/events`,
} as const;

export const PROVIDER_ENDPOINTS = {
  LIST: `${API_PREFIX}/providers`,
  CONFIG: `${API_PREFIX}/providers/{providerId}/config`,
  CONFIG_UPDATE: `${API_PREFIX}/providers/{providerId}/config`,
} as const;

export const DISASTER_ENDPOINTS = {
  ASSESS: `${API_PREFIX}/disasters/assess`,
  ALERTS: `${API_PREFIX}/disasters/alerts`,
  /** @since 4.3.0 - Disaster events collection */
  EVENTS: `${API_PREFIX}/disasters/events`,
  /** @since 4.3.0 - Single disaster event by id */
  EVENT_BY_ID: `${API_PREFIX}/disasters/events/{eventId}`,
  /** @since 4.3.0 - Aggregated disaster statistics */
  STATS: `${API_PREFIX}/disasters/stats/summary`,
  /** @since 4.3.0 - Risk profiles */
  RISKS: `${API_PREFIX}/disasters/risks`,
} as const;

export const AGRO_RULES_ENDPOINTS = {
  FIELD_RULES: `${API_PREFIX}/agro-rules/fields/{fieldId}/rules`,
  CREATE_RULE: `${API_PREFIX}/agro-rules/rules`,
  TRIGGER_RULE: `${API_PREFIX}/agro-rules/rules/{ruleId}/trigger`,
  GDD: `${API_PREFIX}/agro-rules/gdd`,
  SPRAY_WINDOWS: `${API_PREFIX}/agro-rules/spray-windows`,
} as const;

// ---------------------------------------------------------------------------
// Edge Orchestrator Endpoints - نقاط إدارة الأجهزة الطرفية
// ---------------------------------------------------------------------------

export const EDGE_ENDPOINTS = {
  DEVICES: `${API_PREFIX}/edge/devices`,
  DEVICE_GET: `${API_PREFIX}/edge/devices/{deviceId}`,
  DEVICE_CREATE: `${API_PREFIX}/edge/devices`,
  DEVICE_UPDATE: `${API_PREFIX}/edge/devices/{deviceId}`,
  DEVICE_DELETE: `${API_PREFIX}/edge/devices/{deviceId}`,
  DEVICE_STATUS: `${API_PREFIX}/edge/devices/{deviceId}/status`,
  DEPLOY_MODEL: `${API_PREFIX}/edge/deploy`,
  DEPLOY_STATUS: `${API_PREFIX}/edge/deploy/{deploymentId}/status`,
  SYNC: `${API_PREFIX}/edge/sync`,
  SYNC_STATUS: `${API_PREFIX}/edge/sync/{syncId}/status`,
  METRICS: `${API_PREFIX}/edge/devices/{deviceId}/metrics`,
} as const;

// ---------------------------------------------------------------------------
// Community Endpoints - نقاط المجتمع الزراعي
// ---------------------------------------------------------------------------

export const COMMUNITY_ENDPOINTS = {
  POSTS: `${API_PREFIX}/community/posts`,
  POST_GET: `${API_PREFIX}/community/posts/{postId}`,
  POST_CREATE: `${API_PREFIX}/community/posts`,
  POST_UPDATE: `${API_PREFIX}/community/posts/{postId}`,
  POST_DELETE: `${API_PREFIX}/community/posts/{postId}`,
  POST_LIKE: `${API_PREFIX}/community/posts/{postId}/like`,
  POST_SAVE: `${API_PREFIX}/community/posts/{postId}/save`,
  POST_SHARE: `${API_PREFIX}/community/posts/{postId}/share`,
  POST_COMMENTS: `${API_PREFIX}/community/posts/{postId}/comments`,
  TRENDING: `${API_PREFIX}/community/posts/trending`,
  SAVED: `${API_PREFIX}/community/posts/saved`,
  MY_POSTS: `${API_PREFIX}/community/posts/my-posts`,
  GROUPS: `${API_PREFIX}/community/groups`,
  GROUP_GET: `${API_PREFIX}/community/groups/{groupId}`,
  GROUP_JOIN: `${API_PREFIX}/community/groups/{groupId}/join`,
  GROUP_LEAVE: `${API_PREFIX}/community/groups/{groupId}/leave`,
  GROUP_MEMBERS: `${API_PREFIX}/community/groups/{groupId}/members`,
  GROUP_MESSAGES: `${API_PREFIX}/community/groups/{groupId}/messages`,
  MY_GROUPS: `${API_PREFIX}/community/groups/my-groups`,
  EXPERTS: `${API_PREFIX}/community/experts`,
  EXPERT_QUESTIONS: `${API_PREFIX}/community/expert-questions`,
  EXPERT_RATE: `${API_PREFIX}/community/expert-questions/{questionId}/rate`,
} as const;

// ---------------------------------------------------------------------------
// Home Dashboard Endpoints - نقاط لوحة المعلومات
// ---------------------------------------------------------------------------

export const DASHBOARD_ENDPOINTS = {
  SUMMARY: `${API_PREFIX}/dashboard/summary`,
  STATS: `${API_PREFIX}/dashboard/stats`,
  RECENT_ACTIVITY: `${API_PREFIX}/dashboard/recent-activity`,
  WEATHER_WIDGET: `${API_PREFIX}/dashboard/weather`,
  ALERTS_WIDGET: `${API_PREFIX}/dashboard/alerts`,
} as const;

// ---------------------------------------------------------------------------
// Astronomical Calendar Endpoints - نقاط التقويم الفلكي
// Kong route: /api/v1/astronomy  (service: astronomical-calendar, port: 8111)
// Note: Kong path is /astronomy not /astronomical — all endpoints use this prefix.
// ---------------------------------------------------------------------------

export const ASTRONOMICAL_ENDPOINTS = {
  CALENDAR: `${API_PREFIX}/astronomy/calendar`,
  PRAYER_TIMES: `${API_PREFIX}/astronomy/prayer-times`,
  MOON_PHASES: `${API_PREFIX}/astronomy/moon-phases`,
  SEASONS: `${API_PREFIX}/astronomy/seasons`,
  EVENTS: `${API_PREFIX}/astronomy/events`,
} as const;

// ---------------------------------------------------------------------------
// Farms & Seasons Endpoints - نقاط المزارع والمواسم
// ---------------------------------------------------------------------------

export const FARM_ENDPOINTS = {
  LIST: `${API_PREFIX}/farms`,
  GET: `${API_PREFIX}/farms/{farmId}`,
  CREATE: `${API_PREFIX}/farms`,
  UPDATE: `${API_PREFIX}/farms/{farmId}`,
  DELETE: `${API_PREFIX}/farms/{farmId}`,
  STATS: `${API_PREFIX}/farms/{farmId}/stats`,
  MEMBERS: `${API_PREFIX}/farms/{farmId}/members`,
  /** @since 4.3.0 - Tenant-scoped aggregated farm statistics */
  STATS_BY_TENANT: `${API_PREFIX}/farms/stats/{tenantId}`,
} as const;

export const SEASON_ENDPOINTS = {
  LIST: `${API_PREFIX}/seasons`,
  GET: `${API_PREFIX}/seasons/{seasonId}`,
  CREATE: `${API_PREFIX}/seasons`,
  UPDATE: `${API_PREFIX}/seasons/{seasonId}`,
  DELETE: `${API_PREFIX}/seasons/{seasonId}`,
  ACTIVE: `${API_PREFIX}/seasons/active`,
} as const;

// ---------------------------------------------------------------------------
// Compliance & Documents Endpoints - نقاط الامتثال والمستندات
// ---------------------------------------------------------------------------

export const COMPLIANCE_ENDPOINTS = {
  CHECKLISTS: `${API_PREFIX}/compliance/checklists`,
  CHECKLIST_GET: `${API_PREFIX}/compliance/checklists/{checklistId}`,
  AUDITS: `${API_PREFIX}/compliance/audits`,
  CERTIFICATES: `${API_PREFIX}/compliance/certificates`,
  STANDARDS: `${API_PREFIX}/compliance/standards`,
} as const;

/** @deprecated No backend service exists yet. Planned for future release. */
export const DOCUMENT_ENDPOINTS = {
  LIST: `${API_PREFIX}/documents`,
  GET: `${API_PREFIX}/documents/{documentId}`,
  UPLOAD: `${API_PREFIX}/documents/upload`,
  DELETE: `${API_PREFIX}/documents/{documentId}`,
  CATEGORIES: `${API_PREFIX}/documents/categories`,
} as const;

// ---------------------------------------------------------------------------
// Logistics & Research Endpoints - نقاط اللوجستيات والأبحاث
// ---------------------------------------------------------------------------

export const LOGISTICS_ENDPOINTS = {
  SHIPMENTS: `${API_PREFIX}/logistics/shipments`,
  SHIPMENT_GET: `${API_PREFIX}/logistics/shipments/{shipmentId}`,
  SHIPMENT_CREATE: `${API_PREFIX}/logistics/shipments`,
  VEHICLES: `${API_PREFIX}/logistics/vehicles`,
  ROUTES: `${API_PREFIX}/logistics/routes`,
  TRACKING: `${API_PREFIX}/logistics/tracking/{shipmentId}`,
} as const;

export const RESEARCH_ENDPOINTS = {
  TRIALS: `${API_PREFIX}/research/trials`,
  TRIAL_GET: `${API_PREFIX}/research/trials/{trialId}`,
  TRIAL_CREATE: `${API_PREFIX}/research/trials`,
  TRIAL_UPDATE: `${API_PREFIX}/research/trials/{trialId}`,
  OBSERVATIONS: `${API_PREFIX}/research/trials/{trialId}/observations`,
  ANALYSIS: `${API_PREFIX}/research/trials/{trialId}/analysis`,
} as const;

// ---------------------------------------------------------------------------
// Scouting & VRA Endpoints - نقاط الكشف والتطبيق المتغير
// ---------------------------------------------------------------------------

export const SCOUTING_ENDPOINTS = {
  LIST: `${API_PREFIX}/scouting/reports`,
  GET: `${API_PREFIX}/scouting/reports/{reportId}`,
  CREATE: `${API_PREFIX}/scouting/reports`,
  UPDATE: `${API_PREFIX}/scouting/reports/{reportId}`,
  DELETE: `${API_PREFIX}/scouting/reports/{reportId}`,
  FIELD_REPORTS: `${API_PREFIX}/scouting/fields/{fieldId}/reports`,
  STATS: `${API_PREFIX}/scouting/stats`,
} as const;

export const VRA_ENDPOINTS = {
  MAPS: `${API_PREFIX}/vra/maps`,
  MAP_GET: `${API_PREFIX}/vra/maps/{mapId}`,
  MAP_CREATE: `${API_PREFIX}/vra/maps`,
  PRESCRIPTIONS: `${API_PREFIX}/vra/prescriptions`,
  PRESCRIPTION_GET: `${API_PREFIX}/vra/prescriptions/{prescriptionId}`,
  ZONES: `${API_PREFIX}/vra/zones/{fieldId}`,
} as const;

// ---------------------------------------------------------------------------
// Team Management Endpoints - نقاط إدارة الفريق
// ---------------------------------------------------------------------------

export const TEAM_ENDPOINTS = {
  MEMBERS: `${API_PREFIX}/team/members`,
  MEMBER_GET: `${API_PREFIX}/team/members/{memberId}`,
  MEMBER_INVITE: `${API_PREFIX}/team/members/invite`,
  MEMBER_REMOVE: `${API_PREFIX}/team/members/{memberId}`,
  MEMBER_ROLE: `${API_PREFIX}/team/members/{memberId}/role`,
  ROLES: `${API_PREFIX}/team/roles`,
} as const;

// ---------------------------------------------------------------------------
// Crop & Seed Endpoints - نقاط المحاصيل والبذور
// @since 4.3.0
// ---------------------------------------------------------------------------

/** @since 4.3.0 - Crop catalog endpoints */
export const CROP_ENDPOINTS = {
  LIST: `${API_PREFIX}/crops`,
  GET: `${API_PREFIX}/crops/{cropId}`,
  CREATE: `${API_PREFIX}/crops`,
  UPDATE: `${API_PREFIX}/crops/{cropId}`,
  DELETE: `${API_PREFIX}/crops/{cropId}`,
  STATS: `${API_PREFIX}/crops/stats`,
} as const;

/** @since 4.3.0 - Seed catalog endpoints */
export const SEED_ENDPOINTS = {
  LIST: `${API_PREFIX}/seeds`,
  GET: `${API_PREFIX}/seeds/{seedId}`,
} as const;

// ---------------------------------------------------------------------------
// Crop Planning Endpoints - نقاط تخطيط المحاصيل
// @since 4.3.0
// ---------------------------------------------------------------------------

/** @since 4.3.0 - Crop planning endpoints */
export const CROP_PLANNING_ENDPOINTS = {
  PLANS: `${API_PREFIX}/crop-planning/plans`,
  PLAN_BY_ID: `${API_PREFIX}/crop-planning/plans/{planId}`,
  RECOMMENDATIONS: `${API_PREFIX}/crop-planning/recommendations`,
} as const;

// ---------------------------------------------------------------------------
// Crop Rotation Endpoints - نقاط دورة المحاصيل
// @since 4.3.0
// ---------------------------------------------------------------------------

/** @since 4.3.0 - Crop rotation planning endpoints */
export const CROP_ROTATION_ENDPOINTS = {
  PLANS: `${API_PREFIX}/crop-rotation/plans`,
  RECOMMEND: `${API_PREFIX}/crop-rotation/recommend`,
  MULTI_YEAR_PLAN: `${API_PREFIX}/crop-rotation/multi-year-plan`,
  HISTORY: `${API_PREFIX}/crop-rotation/history/{fieldId}`,
  PEST_BREAK: `${API_PREFIX}/crop-rotation/pest-break`,
  SOIL_HEALTH: `${API_PREFIX}/crop-rotation/soil-health`,
  STATS: `${API_PREFIX}/crop-rotation/stats`,
} as const;

// ---------------------------------------------------------------------------
// Labor & Workforce Endpoints - نقاط العمالة
// @since 4.3.0
// ---------------------------------------------------------------------------

/** @since 4.3.0 - Labor & workforce management endpoints */
export const LABOR_ENDPOINTS = {
  WORKERS: `${API_PREFIX}/labor/workers`,
  WORKER_BY_ID: `${API_PREFIX}/labor/workers/{workerId}`,
  SCHEDULE: `${API_PREFIX}/labor/schedule`,
  PAYROLL: `${API_PREFIX}/labor/payroll`,
} as const;

// ---------------------------------------------------------------------------
// Support Endpoints - نقاط الدعم الفني
// @since 4.3.0
// ---------------------------------------------------------------------------

/** @since 4.3.0 - Support ticket endpoints */
export const SUPPORT_ENDPOINTS = {
  TICKETS: `${API_PREFIX}/support/tickets`,
  TICKET_BY_ID: `${API_PREFIX}/support/tickets/{ticketId}`,
} as const;

// ---------------------------------------------------------------------------
// Agricultural Calendar Endpoints - نقاط التقويم الزراعي
// @since 4.3.0
// ---------------------------------------------------------------------------

/** @since 4.3.0 - Agricultural calendar endpoints */
export const AGRI_CALENDAR_ENDPOINTS = {
  EVENTS: `${API_PREFIX}/agri-calendar/events`,
  PLANTING_TIMES: `${API_PREFIX}/agri-calendar/planting-times`,
  HARVEST_TIMES: `${API_PREFIX}/agri-calendar/harvest-times`,
} as const;

// ---------------------------------------------------------------------------
// Cooperative Endpoints - نقاط التعاونيات
// @since 4.3.0
// ---------------------------------------------------------------------------

/** @since 4.3.0 - Cooperative management endpoints */
export const COOPERATIVE_ENDPOINTS = {
  BOOKINGS: `${API_PREFIX}/cooperatives/bookings`,
  PURCHASE_ORDERS: `${API_PREFIX}/cooperatives/purchase-orders`,
  REVENUE: `${API_PREFIX}/cooperatives/revenue`,
  REVENUE_CALCULATE: `${API_PREFIX}/cooperatives/revenue/calculate`,
} as const;

// ---------------------------------------------------------------------------
// Public Endpoints (no auth required) - النقاط العامة
// ---------------------------------------------------------------------------

export const PUBLIC_ENDPOINTS: readonly string[] = [
  AUTH_ENDPOINTS.LOGIN,
  AUTH_ENDPOINTS.REGISTER,
  AUTH_ENDPOINTS.FORGOT_PASSWORD,
  AUTH_ENDPOINTS.RESET_PASSWORD,
  AUTH_ENDPOINTS.VERIFY_OTP,
  AUTH_ENDPOINTS.SEND_OTP,
  HEALTH_ENDPOINTS.LIVENESS,
  HEALTH_ENDPOINTS.READINESS,
  HEALTH_ENDPOINTS.HEALTH,
];

// ---------------------------------------------------------------------------
// Helper: Replace path parameters - استبدال المعلمات
// ---------------------------------------------------------------------------

/**
 * Replace path parameters in an endpoint template.
 *
 * @example
 * buildUrl(FIELD_ENDPOINTS.GET, { fieldId: "abc-123" })
 * // => "/api/v1/fields/abc-123"
 */
export function buildUrl(template: string, params: Record<string, string>): string {
  let url = template;
  for (const [key, value] of Object.entries(params)) {
    url = url.replace(`{${key}}`, encodeURIComponent(value));
  }
  return url;
}
