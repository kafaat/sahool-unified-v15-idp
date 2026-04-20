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

/**
 * Service health-check endpoints routed through Kong Gateway.
 * Pattern: `${API_PREFIX}/{service-slug}/healthz`
 * Used by the web Service Health Dashboard and platform monitoring.
 */
export const SERVICE_HEALTH_ENDPOINTS = {
  FIELD_MANAGEMENT: `${API_PREFIX}/fields/healthz`,
  WEATHER: `${API_PREFIX}/weather/healthz`,
  VEGETATION: `${API_PREFIX}/vegetation/healthz`,
  IRRIGATION: `${API_PREFIX}/irrigation/healthz`,
  ADVISORY: `${API_PREFIX}/advisory/healthz`,
  TASKS: `${API_PREFIX}/tasks/healthz`,
  NOTIFICATIONS: `${API_PREFIX}/notifications/healthz`,
  ALERTS: `${API_PREFIX}/alerts/healthz`,
  CROP_HEALTH: `${API_PREFIX}/crop-health/healthz`,
  SATELLITE: `${API_PREFIX}/satellite/healthz`,
  EQUIPMENT: `${API_PREFIX}/equipment/healthz`,
  IOT: `${API_PREFIX}/iot/healthz`,
  MARKETPLACE: `${API_PREFIX}/marketplace/healthz`,
  BILLING: `${API_PREFIX}/billing/healthz`,
  CHAT: `${API_PREFIX}/chat/healthz`,
  YIELD: `${API_PREFIX}/yield/healthz`,
  DISASTERS: `${API_PREFIX}/disasters/healthz`,
  PROVIDERS: `${API_PREFIX}/providers/healthz`,
  AGRO_RULES: `${API_PREFIX}/agro-rules/healthz`,
  INTELLIGENCE: `${API_PREFIX}/intelligence/healthz`,
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
  /**
   * Field boundary endpoints (current external path via Kong).
   *
   * IMPORTANT — paths must NOT include the legacy `field-core/` segment.
   * The owning service is `field-management-service` and its NestJS
   * controller is mounted at `/api/v1/fields`
   * (`@Controller("api/v1/fields")` + `@Put(":id/boundary")`). The Kong
   * route block is `["/api/v1/fields", "/api/v1/field", "/field"]` —
   * none of which actually proxy `/api/v1/field-core/...` to the
   * upstream, so the previous paths produced 404 in production. This is
   * a vertical-slice fix surfaced by the end-to-end review on
   * 2026-04-13. See docs/audits/E2E_USER_JOURNEY_AUDIT.md.
   */
  BOUNDARY: `${API_PREFIX}/fields/{fieldId}/boundary`,
  BOUNDARY_UPDATE: `${API_PREFIX}/fields/{fieldId}/boundary`,
  BOUNDARY_HISTORY: `${API_PREFIX}/fields/{fieldId}/boundary-history`,
  BOUNDARY_ROLLBACK: `${API_PREFIX}/fields/{fieldId}/boundary-history/rollback`,
  /** @since 4.18.0 — Field KPI snapshot (cached weekly KPI aggregate) */
  KPI_SNAPSHOT: `${API_PREFIX}/fields/{fieldId}/kpi-snapshot`,
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
  /** @since 4.7.0 — Generate a signed SVG weather graph URL for a field (Farmonaut-style get-past-weather-graph) */
  FIELD_GRAPH_GENERATE: `${API_PREFIX}/weather/fields/{fieldId}/graph`,
  /** @since 4.7.0 — Fetch a previously generated weather graph by signed id */
  FIELD_GRAPH_FETCH: `${API_PREFIX}/weather/graphs/{graphId}`,
  /**
   * Kong-routed actual external paths.
   * Kong routes /api/v1/weather/* → weather-service which has /weather/* endpoints.
   * Use these until Kong strip_path is enabled for weather routes.
   */
  KONG_CURRENT: `${API_PREFIX}/weather/weather/current`,
  KONG_FORECAST: `${API_PREFIX}/weather/weather/forecast`,
  KONG_AGRICULTURAL_REPORT: `${API_PREFIX}/weather/weather/agricultural-report`,
  /** Yemen/location-scoped endpoints (Kong-routed with v1 prefix) */
  KONG_CURRENT_BY_LOCATION: `${API_PREFIX}/weather/v1/current/{locationId}`,
  KONG_FORECAST_BY_LOCATION: `${API_PREFIX}/weather/v1/forecast/{locationId}`,
  KONG_LOCATIONS: `${API_PREFIX}/weather/v1/locations`,
  /** @deprecated Use WEATHER_ENDPOINTS.CURRENT instead. WEATHER_CORE has been consolidated into WEATHER. Removal: v18.0.0 */
  WEATHER_CORE_CURRENT: `${API_PREFIX}/weather-core/weather/current`,
  /** @deprecated Use WEATHER_ENDPOINTS.FORECAST instead. WEATHER_CORE has been consolidated into WEATHER. Removal: v18.0.0 */
  WEATHER_CORE_FORECAST: `${API_PREFIX}/weather-core/weather/forecast`,
  /** @deprecated Use WEATHER_ENDPOINTS.AGRICULTURAL_CALENDAR instead. WEATHER_CORE has been consolidated into WEATHER. Removal: v18.0.0 */
  WEATHER_CORE_AG_REPORT: `${API_PREFIX}/weather-core/weather/agricultural-report`,
  /** @since 4.18.0 — Growing Degree Days journal (weather-service) */
  GDD: `${API_PREFIX}/weather/gdd`,
  /** @since 4.18.0 — Spray-window candidates (weather-service) */
  SPRAY_WINDOWS: `${API_PREFIX}/weather/spray-windows`,
} as const;

// ---------------------------------------------------------------------------
// Satellite & NDVI Endpoints - نقاط الأقمار الصناعية
// ---------------------------------------------------------------------------

export const SATELLITE_ENDPOINTS = {
  ANALYZE: `${API_PREFIX}/satellite/v1/analyze`,
  ANALYZE_FIELD: `${API_PREFIX}/satellite/analyze/{fieldId}`,
  TIMESERIES: `${API_PREFIX}/satellite/v1/timeseries/{fieldId}`,
  INDICES: `${API_PREFIX}/satellite/v1/indices/{fieldId}`,
  /**
   * Raster tile metadata for a specific mappable vegetation index. Returns
   * `{rasterUrl, bounds, colorScale}`, backs the MapLibre layer that lets
   * users switch between NDVI / NDRE / NDWI / EVI / SAVI / LAI on the map.
   * @since CONTRACT 1.7.0
   */
  INDEX_MAP: `${API_PREFIX}/satellite/v1/indices/{fieldId}/{indexName}/map`,
  /**
   * Per-pixel "click to inspect" inspector — returns every computed index
   * at a given lat/lon for the field (EOSDA/OneSoil pattern).
   * @since CONTRACT 1.7.0
   */
  INDEX_PIXEL: `${API_PREFIX}/satellite/v1/indices/{fieldId}/pixel`,
  /**
   * N-day composite summary (median/mean/p25/p75 per window). Backs the
   * "weekly/monthly composite" view.
   * @since CONTRACT 4.21.0
   */
  INDEX_COMPOSITE: `${API_PREFIX}/satellite/v1/indices/{fieldId}/{indexName}/composite`,
  /**
   * Filmstrip of per-date thumbnail metadata (date + rasterUrl + value +
   * status) at a fixed cadence, capped at ~20 entries.
   * @since CONTRACT 4.21.0
   */
  INDEX_FILMSTRIP: `${API_PREFIX}/satellite/v1/indices/{fieldId}/{indexName}/filmstrip`,
  /**
   * Multi-date compare (N up to 12) — POST body with `dates[]` or
   * `{start, end, step_days}`. Replaces the legacy 2-date compare
   * endpoint for all mappable indices.
   * @since CONTRACT 4.21.0
   */
  INDEX_MULTI_COMPARE: `${API_PREFIX}/satellite/v1/indices/{fieldId}/{indexName}/multi-date-compare`,
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
  /**
   * @since 4.18.0 — crop-intelligence-service alias paths (different
   * Kong route from /crop-health, used by Phase-2 web client).
   */
  INTELLIGENCE_ANALYZE: `${API_PREFIX}/crop-intelligence/analyze`,
  INTELLIGENCE_DECISION: `${API_PREFIX}/crop-intelligence/decision`,
  INTELLIGENCE_HISTORY: `${API_PREFIX}/crop-intelligence/fields/{fieldId}/history`,
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
  /** @since 4.16.0 — Surfaced by the web irrigation + pivot-irrigation features */
  EFFICIENCY_REPORT: `${API_PREFIX}/irrigation/efficiency-report`,
  IRRIGATION_EXECUTED: `${API_PREFIX}/irrigation/irrigation-executed`,
  CALCULATE_WITH_ACTION: `${API_PREFIX}/irrigation/calculate-with-action`,
  PIVOT_SPEED: `${API_PREFIX}/irrigation/pivot/speed`,
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
  /** Current external paths (via Kong) - advisory-service */
  ADVICE: `${API_PREFIX}/advisory/advice`,
  DISEASE: `${API_PREFIX}/advisory/disease`,
  NUTRIENTS: `${API_PREFIX}/advisory/nutrients`,
  /** @deprecated Use ADVICE instead (agro-advisor service was consolidated into advisory-service) */
  AGRO_ADVICE: `${API_PREFIX}/agro-advisor/advice`,
  /** @deprecated Use DISEASE instead */
  AGRO_DISEASE: `${API_PREFIX}/agro-advisor/disease`,
  /** @deprecated Use NUTRIENTS instead */
  AGRO_NUTRIENTS: `${API_PREFIX}/agro-advisor/nutrients`,
  /** @since 4.7.0 — Jeevn-style unified per-field advisory (one call → comprehensive answer) */
  COMPREHENSIVE: `${API_PREFIX}/advisory/comprehensive/{fieldId}`,
  /** @since 4.14.0 — Field-scoped advisory actions used by the web proxy layer */
  RECOMMENDATIONS_BY_FIELD: `${API_PREFIX}/advisory/recommendations/{fieldId}`,
  DISEASE_ASSESS: `${API_PREFIX}/advisory/disease-assess/{fieldId}`,
  FERTILIZER_PLAN: `${API_PREFIX}/advisory/fertilizer-plan/{fieldId}`,
  CROP_ADVICE: `${API_PREFIX}/advisory/crop-advice/{fieldId}`,
  /** @since 4.16.0 — Spray-timing windows used by the web crop-protection feature */
  SPRAY_WINDOWS: `${API_PREFIX}/advisory/spray-windows`,
  /** @since 4.18.0 — Spray-history journal (advisory-service) */
  SPRAY_HISTORY: `${API_PREFIX}/advisory/spray-history`,
} as const;

// ---------------------------------------------------------------------------
// Pest Management Endpoints - نقاط إدارة الآفات
// @since 4.14.0 — separated from CROP_HEALTH (diseases only) because the
// pest-detection-service exposes /pests and /treatments as its own domain.
// ---------------------------------------------------------------------------

export const PEST_ENDPOINTS = {
  LIST: `${API_PREFIX}/pests`,
  BY_CROP: `${API_PREFIX}/pests/crop/{cropType}`,
  IDENTIFY: `${API_PREFIX}/pests/identify`,
  TREATMENT_RECOMMEND: `${API_PREFIX}/treatments/recommend`,
} as const;

// ---------------------------------------------------------------------------
// Crop Loan Verification Endpoints - نقاط التحقق من القروض الزراعية
// Satellite-backed verification surfaced by advisory-service; banks use
// this to confirm farmer declarations against real NDVI before lending.
// ---------------------------------------------------------------------------

export const LOAN_VERIFICATION_ENDPOINTS = {
  /** @since 4.7.0 — Satellite-backed crop loan verification for a field */
  VERIFY: `${API_PREFIX}/loans/crop-loan-verification/{fieldId}`,
} as const;

// ---------------------------------------------------------------------------
// Task Endpoints - نقاط المهام
// WIP: task-service (port 8103) currently implements a subset only.
// Endpoints marked below are tracked by endpoint-reality-check.
// See: scripts/endpoint-reality-check.ts
// ---------------------------------------------------------------------------

export const TASK_ENDPOINTS = {
  LIST: `${API_PREFIX}/tasks`,
  GET: `${API_PREFIX}/tasks/{taskId}`,
  CREATE: `${API_PREFIX}/tasks`,
  UPDATE: `${API_PREFIX}/tasks/{taskId}`,
  DELETE: `${API_PREFIX}/tasks/{taskId}`,
  STATUS: `${API_PREFIX}/tasks/{taskId}/status`,
  COMPLETE: `${API_PREFIX}/tasks/{taskId}/complete`,
  /** @since 4.14.0 — Task assignment action surfaced by the web proxy */
  ASSIGN: `${API_PREFIX}/tasks/{taskId}/assign`,
} as const;

/** WIP services allowed to have partial endpoint implementation. */
export const WIP_SERVICES = ["task-service", "yolo26-vision-service", "drone-service"] as const;

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
  /** @since 4.7.0 — Geofence event ingest (auto-drafts FieldOperation on entry into a field zone) */
  GEOFENCE_EVENT: `${API_PREFIX}/equipment/geofence/event`,
  /** @since 4.14.0 — Surfaced by the web proxy */
  MAINTENANCE_SCHEDULE: `${API_PREFIX}/equipment/maintenance-schedule`,
  MAINTENANCE_SCHEDULE_BY_ID: `${API_PREFIX}/equipment/{equipmentId}/maintenance-schedule`,
  ISSUES: `${API_PREFIX}/equipment/{equipmentId}/issues`,
  /** @since 4.15.0 — Mobile equipment tracking surface */
  ALERTS: `${API_PREFIX}/equipment/alerts`,
  LOCATION: `${API_PREFIX}/equipment/{equipmentId}/location`,
  TELEMETRY: `${API_PREFIX}/equipment/{equipmentId}/telemetry`,
  FUEL: `${API_PREFIX}/equipment/{equipmentId}/fuel`,
  FUEL_SUMMARY: `${API_PREFIX}/equipment/{equipmentId}/fuel/summary`,
  USAGE: `${API_PREFIX}/equipment/{equipmentId}/usage`,
  USAGE_START: `${API_PREFIX}/equipment/{equipmentId}/usage/start`,
  USAGE_END: `${API_PREFIX}/equipment/{equipmentId}/usage/{logId}/end`,
  USAGE_SUMMARY: `${API_PREFIX}/equipment/{equipmentId}/usage/summary`,
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
  /**
   * @since 4.15.0 — Mobile billing surface.
   * NOTE: DEPOSIT/WITHDRAW/TRANSFER are *flat* `/billing/deposit` paths
   * (what the mobile app actually hits), while WALLET_DEPOSIT/WITHDRAW/TRANSFER
   * above use the `/billing/wallet/*` variant. Both shapes are kept because
   * billing-core exposes them in parallel; picking one over the other is a
   * separate reconciliation tracked with the 2026-04 audit.
   */
  DEPOSIT: `${API_PREFIX}/billing/deposit`,
  WITHDRAW: `${API_PREFIX}/billing/withdraw`,
  TRANSFER: `${API_PREFIX}/billing/transfer`,
  PAYMENTS: `${API_PREFIX}/billing/payments`,
  INVOICE_PAYMENT_INTENT: `${API_PREFIX}/billing/invoices/{invoiceId}/payment-intent`,
  /** Stripe payment-intent lifecycle (mobile pays via Stripe SDK) */
  STRIPE_CONFIG: `${API_PREFIX}/billing/stripe/config`,
  STRIPE_PAYMENT_INTENTS: `${API_PREFIX}/billing/stripe/payment-intents`,
  STRIPE_PAYMENT_INTENT_CONFIRM: `${API_PREFIX}/billing/stripe/payment-intents/{paymentIntentId}/confirm`,
  STRIPE_SETUP_INTENTS: `${API_PREFIX}/billing/stripe/setup-intents`,
  STRIPE_SETUP_INTENT_CONFIRM: `${API_PREFIX}/billing/stripe/setup-intents/{setupIntentId}/confirm`,
  /** Saved payment methods */
  PAYMENT_METHODS: `${API_PREFIX}/billing/payment-methods`,
  PAYMENT_METHOD_GET: `${API_PREFIX}/billing/payment-methods/{paymentMethodId}`,
  PAYMENT_METHOD_DEFAULT: `${API_PREFIX}/billing/payment-methods/{paymentMethodId}/default`,
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
  /**
   * Legacy field-chat paths. Preserved for back-compat.
   * @deprecated Use FIELD_MESSAGES_V2 / FIELD_SEND_V2 / FIELD_PARTICIPANTS_V2
   * which route through the consolidated chat-service at /api/v1/chat/fields/*.
   * Removal: v5.0.0
   */
  FIELD_MESSAGES: `${API_PREFIX}/field-chat/fields/{fieldId}/messages`,
  FIELD_SEND: `${API_PREFIX}/field-chat/fields/{fieldId}/messages`,
  FIELD_PARTICIPANTS: `${API_PREFIX}/field-chat/fields/{fieldId}/participants`,
  /**
   * @since 4.18.0 - Canonical chat-service paths (post field-chat consolidation).
   * Use these in new code. The *_V2 suffix is a transitional marker until
   * the legacy FIELD_* constants are removed in v5.0.0.
   */
  FIELD_MESSAGES_V2: `${API_PREFIX}/chat/fields/{fieldId}/messages`,
  FIELD_SEND_V2: `${API_PREFIX}/chat/fields/{fieldId}/messages`,
  FIELD_PARTICIPANTS_V2: `${API_PREFIX}/chat/fields/{fieldId}/participants`,
  COMMUNITY_POSTS: `${API_PREFIX}/posts`,
  COMMUNITY_POST_GET: `${API_PREFIX}/posts/{postId}`,
  COMMUNITY_COMMENTS: `${API_PREFIX}/posts/{postId}/comments`,
  /** @since 4.15.0 — Conversation moderation actions used by mobile chat */
  MUTE: `${API_PREFIX}/chat/conversations/{conversationId}/mute`,
  REPORT: `${API_PREFIX}/chat/conversations/{conversationId}/report`,
  /** Same URL as MESSAGES but DELETE method — clears conversation history */
  CLEAR_MESSAGES: `${API_PREFIX}/chat/conversations/{conversationId}/messages`,
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
  /**
   * @since 4.18.0 — Copilot service direct paths (not routed via Kong).
   * The page uses `${COPILOT_API_BASE}/api/v1/chat` style concatenation
   * where COPILOT_API_BASE is the direct service URL. Keep the `/api/v1`
   * prefix here so the builder can pair it with `${COPILOT_API_BASE}`
   * without double-prefixing.
   */
  COPILOT_CHAT_DIRECT: `${API_PREFIX}/chat`,
  COPILOT_CHAT_STREAM_DIRECT: `${API_PREFIX}/chat/stream`,
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
  /**
   * @since 4.3.0 - Corrected to field-scoped path under /hydrology/drainage
   * @deprecated Use HYDROLOGY_ENDPOINTS.DRAINAGE_BY_FIELD instead
   */
  HYDROLOGY_DRAINAGE: `${API_PREFIX}/hydrology/drainage/{fieldId}`,
  /**
   * @since 4.3.0 - Corrected to field-scoped path under /hydrology/basins
   * @deprecated Use HYDROLOGY_ENDPOINTS.WATERSHED_DELINEATE instead
   */
  HYDROLOGY_WATERSHED: `${API_PREFIX}/hydrology/basins/{fieldId}`,
  /**
   * @since 4.3.0 - Corrected to field-scoped path under /terrain/flow
   * @deprecated Use HYDROLOGY_ENDPOINTS.FLOW_ACCUMULATION instead
   */
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
  /** @since 4.7.1 — RUSLE soil-erosion assessment (replaces hardcoded erosion_risk stub) */
  EROSION: `${API_PREFIX}/terrain/erosion`,
  /** @since 4.9.0 — RWEQ wind-erosion assessment (for Yemen plains: Tihama, Marib, Al-Jawf, Hadramawt) */
  EROSION_WIND: `${API_PREFIX}/terrain/erosion/wind`,
  /** @since 4.9.0 — Combined water + wind erosion; returns whichever process dominates */
  EROSION_COMBINED: `${API_PREFIX}/terrain/erosion/combined`,
  /** @since 4.9.0 — Yemen region preset shortcut (fewest inputs, auto-fills climate + soil defaults) */
  EROSION_YEMEN: `${API_PREFIX}/terrain/erosion/yemen`,
  /** @since 4.14.0 — Field-scoped terrain endpoints surfaced by the web proxy */
  DEM_FIELD: `${API_PREFIX}/terrain/dem/{fieldId}`,
  SLOPE_FIELD: `${API_PREFIX}/terrain/slope/{fieldId}`,
  TWI: `${API_PREFIX}/terrain/twi/{fieldId}`,
  CONTOURS: `${API_PREFIX}/terrain/contours/{fieldId}`,
  ANALYZE: `${API_PREFIX}/terrain/analyze`,
} as const;

/**
 * Hydrology Service Endpoints (port 8165)
 * نقاط خدمة الهيدرولوجيا - watershed, drainage, and flow analysis
 */
export const HYDROLOGY_ENDPOINTS = {
  DRAINAGE: `${API_PREFIX}/hydrology/drainage`,
  DRAINAGE_BY_FIELD: `${API_PREFIX}/hydrology/drainage/{fieldId}`,
  WATERSHED: `${API_PREFIX}/hydrology/watershed`,
  WATERSHED_DELINEATE: `${API_PREFIX}/hydrology/watershed/delineate`,
  FLOW: `${API_PREFIX}/hydrology/flow`,
  FLOW_ACCUMULATION: `${API_PREFIX}/hydrology/flow/accumulation`,
  STREAM_NETWORK: `${API_PREFIX}/hydrology/streams`,
  RAINFALL_RUNOFF: `${API_PREFIX}/hydrology/rainfall-runoff`,
  INFILTRATION: `${API_PREFIX}/hydrology/infiltration`,
} as const;

/**
 * Vegetation Analysis Service Endpoints (port 8090)
 * نقاط تحليل الغطاء النباتي - specialized vegetation indices beyond SATELLITE_ENDPOINTS
 */
export const VEGETATION_ENDPOINTS = {
  ANALYZE: `${API_PREFIX}/vegetation/analyze`,
  NDVI: `${API_PREFIX}/vegetation/ndvi/{fieldId}`,
  EVI: `${API_PREFIX}/vegetation/evi/{fieldId}`,
  SAVI: `${API_PREFIX}/vegetation/savi/{fieldId}`,
  NDWI: `${API_PREFIX}/vegetation/ndwi/{fieldId}`,
  LAI: `${API_PREFIX}/vegetation/lai/{fieldId}`,
  CHLOROPHYLL: `${API_PREFIX}/vegetation/chlorophyll/{fieldId}`,
  TIMESERIES: `${API_PREFIX}/vegetation/timeseries/{fieldId}`,
  STRESS_MAP: `${API_PREFIX}/vegetation/stress/{fieldId}`,
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
  /** @since 4.15.0 — Block another user (used by mobile chat) */
  BLOCK: `${API_PREFIX}/users/{userId}/block`,
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
  /** Per-resource audit trail (reverse chronological). Exposed by
   *  audit-service as
   *    `GET /api/v1/audit/resources/{resource_type}/{resource_id}/trail`
   *  The handler accepts ONLY `skip` and `limit` — no category / user /
   *  date-range filtering. The admin Field History panel therefore uses
   *  LOGS (above) with resource_type + resource_id pinned in the query
   *  string instead of this endpoint. Kept for use cases that truly
   *  want an unfiltered reverse-chronological stream. */
  RESOURCE_TRAIL: `${API_PREFIX}/audit/resources/{resourceType}/{resourceId}/trail`,
  /** Per-user audit trail. Same skip+limit-only constraint as
   *  RESOURCE_TRAIL; callers that need filtering should use LOGS with
   *  `user_id` in the query string. */
  USER_TRAIL: `${API_PREFIX}/audit/users/{userId}/trail`,
  /** Chain-integrity validation. Response shape matches
   *  audit-service's `HashChainValidationResponse`:
   *    { valid, total_entries, validated_entries, invalid_entries,
   *      errors, retention_gaps_crossed }
   *  `retention_gaps_crossed` is non-zero once the audit-retention-worker
   *  has run for the tenant — a chain is still `valid: true` across
   *  legitimate retention-driven gaps. */
  CHAIN_VALIDATE: `${API_PREFIX}/audit/chain/validate`,
} as const;

// ---------------------------------------------------------------------------
// Additional Domain Endpoints - نقاط إضافية
// ---------------------------------------------------------------------------

export const SOIL_ENDPOINTS = {
  TESTS: `${API_PREFIX}/soil/tests`,
  TEST_GET: `${API_PREFIX}/soil/tests/{testId}`,
  TEST_CREATE: `${API_PREFIX}/soil/tests`,
  TEST_UPDATE: `${API_PREFIX}/soil/tests/{testId}`,
  TEST_DELETE: `${API_PREFIX}/soil/tests/{testId}`,
  /** @deprecated Use TESTS_BY_FIELD instead (different path shape from main). */
  TESTS_BY_FIELD_LEGACY: `${API_PREFIX}/soil/fields/{fieldId}/tests`,
  ANALYSIS: `${API_PREFIX}/soil/analysis`,
  ANALYSIS_INTERPRET: `${API_PREFIX}/soil/analysis/interpret`,
  SENSORS: `${API_PREFIX}/soil/sensors`,
  SENSOR_READINGS: `${API_PREFIX}/soil/sensors/{sensorId}/readings`,
  MOISTURE: `${API_PREFIX}/soil/moisture/{fieldId}`,
  SALINITY: `${API_PREFIX}/soil/salinity/{fieldId}`,
  PH: `${API_PREFIX}/soil/ph/{fieldId}`,
  NUTRIENTS: `${API_PREFIX}/soil/nutrients/{fieldId}`,
  RECOMMENDATIONS: `${API_PREFIX}/soil/recommendations`,
  RECOMMENDATIONS_BY_FIELD: `${API_PREFIX}/soil/recommendations/{fieldId}`,
  /** @since 4.14.0 — Endpoints surfaced by the web `/api/soil-analysis` proxy */
  TESTS_BY_FIELD: `${API_PREFIX}/soil/tests/field/{fieldId}`,
  PRODUCTS: `${API_PREFIX}/soil/products`,
  CROP_REQUIREMENTS: `${API_PREFIX}/soil/crops/{crop}/requirements`,
  INTERPRET: `${API_PREFIX}/soil/interpret`,
  AMENDMENT_PLAN: `${API_PREFIX}/soil/recommendations/amendment-plan`,
  PH_STATUS: `${API_PREFIX}/soil/interpretation/ph-status`,
  EC_STATUS: `${API_PREFIX}/soil/interpretation/ec-status`,
} as const;

export const DRONE_ENDPOINTS = {
  FLIGHTS: `${API_PREFIX}/drone/flights`,
  FLIGHT_GET: `${API_PREFIX}/drone/flights/{flightId}`,
  FLIGHT_CREATE: `${API_PREFIX}/drone/flights`,
  FLIGHT_UPDATE: `${API_PREFIX}/drone/flights/{flightId}`,
  FLIGHT_DELETE: `${API_PREFIX}/drone/flights/{flightId}`,
  FLIGHT_PLAN: `${API_PREFIX}/drone/flights/plan`,
  FLIGHT_START: `${API_PREFIX}/drone/flights/{flightId}/start`,
  FLIGHT_PAUSE: `${API_PREFIX}/drone/flights/{flightId}/pause`,
  FLIGHT_RESUME: `${API_PREFIX}/drone/flights/{flightId}/resume`,
  FLIGHT_ABORT: `${API_PREFIX}/drone/flights/{flightId}/abort`,
  FLIGHT_MISSIONS: `${API_PREFIX}/drone/flights/{flightId}/missions`,
  FLIGHT_TELEMETRY: `${API_PREFIX}/drone/flights/{flightId}/telemetry`,
  DEVICES: `${API_PREFIX}/drone/devices`,
  DEVICE_GET: `${API_PREFIX}/drone/devices/{deviceId}`,
  DEVICE_REGISTER: `${API_PREFIX}/drone/devices`,
  DEVICE_STATUS: `${API_PREFIX}/drone/devices/{deviceId}/status`,
  VRA_APPLY: `${API_PREFIX}/drone/vra/apply`,
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
  /** @since 4.7.0 - List blockchain-style anchors for a field */
  ANCHORS_LIST: `${API_PREFIX}/traceability/anchors/{tenantId}/{fieldId}`,
  /** @since 4.7.0 - Verify the anchor chain for a field */
  ANCHORS_VERIFY: `${API_PREFIX}/traceability/anchors/{tenantId}/{fieldId}/verify`,
  /** @since 4.7.0 - Subscriber stats (messages consumed, anchors created) */
  ANCHORS_STATS: `${API_PREFIX}/traceability/anchors/stats`,
} as const;

export const PROVIDER_ENDPOINTS = {
  LIST: `${API_PREFIX}/providers`,
  CONFIG: `${API_PREFIX}/providers/{providerId}/config`,
  CONFIG_UPDATE: `${API_PREFIX}/providers/{providerId}/config`,
  /** @since 4.18.0 — provider-config-service flat URL (web client) */
  PROVIDER_CONFIG_LIST: `${API_PREFIX}/provider-config`,
  PROVIDER_CONFIG_ITEM: `${API_PREFIX}/provider-config/{providerId}`,
} as const;

export const DISASTER_ENDPOINTS = {
  ASSESS: `${API_PREFIX}/disasters/assess`,
  ALERTS: `${API_PREFIX}/disasters/alerts`,
  /** @since 4.18.0 — singular `/disaster/*` paths used by Phase-2 web client */
  ASSESS_SINGULAR: `${API_PREFIX}/disaster/assess`,
  ALERTS_SINGULAR: `${API_PREFIX}/disaster/alerts`,
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
  /** @since 4.16.0 — Seed variety recommendations used by the web seeds feature */
  RECOMMENDATIONS: `${API_PREFIX}/seeds/recommendations`,
} as const;

// ---------------------------------------------------------------------------
// Epidemic Surveillance Endpoints
// @since 4.16.0 — surfaced by the web `epidemic` feature
// ---------------------------------------------------------------------------

export const EPIDEMIC_ENDPOINTS = {
  LIST: `${API_PREFIX}/epidemics`,
  GET: `${API_PREFIX}/epidemics/{epidemicId}`,
  REPORT: `${API_PREFIX}/epidemics/report`,
} as const;

// ---------------------------------------------------------------------------
// Field Leveling Endpoints
// @since 4.16.0 — surfaced by the web `leveling` feature (distinct from the
// `/leveling/analyze` etc. constants under TERRAIN_ENDPOINTS, which the
// terrain-core-service exposes directly; these field-scoped paths live on
// the leveling-optimizer-service).
// ---------------------------------------------------------------------------

export const LEVELING_ENDPOINTS = {
  ANALYZE: `${API_PREFIX}/leveling/analyze`,
  PLAN: `${API_PREFIX}/leveling/plan/{fieldId}`,
  COST: `${API_PREFIX}/leveling/cost/{fieldId}`,
  EQUIPMENT: `${API_PREFIX}/leveling/equipment/{fieldId}`,
  SIMULATE: `${API_PREFIX}/leveling/simulate`,
} as const;

// ---------------------------------------------------------------------------
// Precision Agriculture Endpoints
// @since 4.16.0 — surfaced by the web `precision-agriculture` feature.
// Wraps VRA prescriptions, GDD accumulation, and per-field fertilizer
// calculators exposed by precision-ag services.
// ---------------------------------------------------------------------------

export const PRECISION_ENDPOINTS = {
  VRA: `${API_PREFIX}/precision-agriculture/vra/{fieldId}`,
  GDD: `${API_PREFIX}/precision-agriculture/gdd/{fieldId}`,
  FERTILIZER_CALCULATE: `${API_PREFIX}/precision-agriculture/fertilizer/calculate`,
} as const;

// ---------------------------------------------------------------------------
// Satellite Monitor Endpoints
// @since 4.16.0 — dashboard aggregator (distinct from vegetation-analysis
// SATELLITE_ENDPOINTS which expose raw analysis; this sits on top of it
// and powers the /satellite-monitor dashboard page).
// ---------------------------------------------------------------------------

export const SATELLITE_MONITOR_ENDPOINTS = {
  FIELDS: `${API_PREFIX}/satellite-monitor/fields`,
  FIELD_GET: `${API_PREFIX}/satellite-monitor/fields/{fieldId}`,
  STATS: `${API_PREFIX}/satellite-monitor/stats`,
  ALERTS: `${API_PREFIX}/satellite-monitor/alerts`,
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

// ===========================================================================
// Wave 0: FieldView-Inspired Partner & Upload Contracts (@since 4.10.0)
// إضافات الموجة 0 — بنية شركاء مُستلهَمة من FieldView v4.0.11
//
// These are ADDITIVE constants that standardize chunked upload, vendor MIME
// types, header-based pagination, state machines, and a partner-facing OAuth
// 2.0 surface — without touching any existing endpoint.
//
// Design goals:
//   1. Drop-in compatibility for partners already integrated with FieldView
//      (Leaf Agriculture, DroneDeploy, SWAT Maps, ag-retailers, soil labs).
//   2. Clean separation of identity (OAuth) from metering (X-Sahool-Partner-Key)
//      — Stripe/Shopify-style.
//   3. Interop standards: AgGateway Modus 1.0 XML, ISOXML, shapefile Rx.
//   4. Offline-first mobile benefits from ETag + 304 + chunked resumable upload.
// ===========================================================================

// ---------------------------------------------------------------------------
// GDD (Growing Degree Days) Endpoints
// @since 4.17.0 — surfaced by the mobile `features/gdd` service. Distinct
// from the precision-agriculture `GDD` entry which is a single per-field
// summary; this group covers the full GDD domain (accumulation, stages,
// forecasts, settings, trend, comparison).
// ---------------------------------------------------------------------------

export const GDD_ENDPOINTS = {
  ACCUMULATION: `${API_PREFIX}/gdd/fields/{fieldId}/accumulation`,
  RECORDS: `${API_PREFIX}/gdd/fields/{fieldId}/records`,
  CALCULATE: `${API_PREFIX}/gdd/fields/{fieldId}/calculate`,
  CURRENT_STAGE: `${API_PREFIX}/gdd/fields/{fieldId}/current-stage`,
  STAGES: `${API_PREFIX}/gdd/fields/{fieldId}/stages`,
  CROPS: `${API_PREFIX}/gdd/crops`,
  CROP_REQUIREMENTS: `${API_PREFIX}/gdd/crops/{cropType}/requirements`,
  FORECAST: `${API_PREFIX}/gdd/fields/{fieldId}/forecast`,
  SETTINGS: `${API_PREFIX}/gdd/fields/{fieldId}/settings`,
  COMPARE: `${API_PREFIX}/gdd/fields/{fieldId}/compare`,
  TREND: `${API_PREFIX}/gdd/fields/{fieldId}/trend`,
} as const;

// ---------------------------------------------------------------------------
// Gamification Endpoints
// @since 4.17.0 — surfaced by the mobile gamification feature (farmer
// profile + community leaderboard). Backend service TBD.
// ---------------------------------------------------------------------------

export const GAMIFICATION_ENDPOINTS = {
  PROFILE: `${API_PREFIX}/gamification/profile/{userId}`,
  LEADERBOARD: `${API_PREFIX}/gamification/leaderboard`,
} as const;

// ---------------------------------------------------------------------------
// Lab Sample Tracking Endpoints
// @since 4.17.0 — surfaced by the mobile lab feature (soil/leaf/water
// sample submission + barcode lookup).
// ---------------------------------------------------------------------------

export const LAB_ENDPOINTS = {
  SAMPLES: `${API_PREFIX}/lab/samples`,
  SAMPLE_BY_BARCODE: `${API_PREFIX}/lab/samples/barcode/{barcode}`,
} as const;

// ---------------------------------------------------------------------------
// Payment Endpoints (Tharwatt wallet integration)
// @since 4.17.0 — distinct from BILLING_ENDPOINTS which covers Stripe and
// the platform wallet; PAYMENT_ENDPOINTS is the Tharwatt-specific top-up /
// withdrawal / transfer surface used by the mobile app in Yemen.
// ---------------------------------------------------------------------------

export const PAYMENT_ENDPOINTS = {
  DEPOSIT: `${API_PREFIX}/payment/deposit`,
  WITHDRAW: `${API_PREFIX}/payment/withdraw`,
  TRANSFER: `${API_PREFIX}/payment/transfer`,
  TOPUP: `${API_PREFIX}/payment/topup`,
  STATUS: `${API_PREFIX}/payment/status/{transactionId}`,
  TRANSACTIONS: `${API_PREFIX}/payment/transactions`,
  BALANCE: `${API_PREFIX}/payment/balance/{walletId}`,
  VALIDATE_PHONE: `${API_PREFIX}/payment/validate-phone`,
  OPERATORS: `${API_PREFIX}/payment/operators`,
  CANCEL: `${API_PREFIX}/payment/cancel/{transactionId}`,
} as const;

// ---------------------------------------------------------------------------
// Unified Upload Endpoints - نقاط الرفع الموحَّدة (@since 4.10.0)
//
// Chunked resumable upload inspired by FieldView POST /v4/uploads.
// Backend contract: MinIO multipart upload wrapped behind this surface.
// ---------------------------------------------------------------------------

/** @since 4.10.0 — Chunked resumable upload API (FieldView-compatible semantics) */
export const UPLOAD_ENDPOINTS = {
  /** POST — Initiate. Body: {md5, length, contentType}. Returns 201 + uploadId. */
  CREATE: `${API_PREFIX}/uploads`,
  /** PUT — Upload chunk. Required: Content-Range: bytes N-M/TOTAL. Max 5 MiB per chunk. Returns 204. */
  CHUNK: `${API_PREFIX}/uploads/{uploadId}`,
  /** GET — Poll processing status. Returns current UploadState. */
  STATUS: `${API_PREFIX}/uploads/{uploadId}/status`,
  /** POST — Batch status query. Body: {ids: string[]} (≤100). */
  BATCH_STATUS: `${API_PREFIX}/uploads/status/query`,
  /** DELETE — Cancel an in-progress upload (cleans up partial chunks). */
  CANCEL: `${API_PREFIX}/uploads/{uploadId}`,
} as const;

/** @since 4.10.0 — Numeric limits on the upload surface (matches FieldView for interop) */
export const UPLOAD_LIMITS = {
  /** 500 MiB — hard cap on any single upload */
  MAX_BYTES: 524_288_000,
  /** 5 MiB — required chunk size (final chunk may be smaller) */
  CHUNK_BYTES: 5_242_880,
  /** 20 MiB — photo cap for scouting attachments */
  PHOTO_MAX_BYTES: 20_971_520,
  /** 100 — max upload IDs per /uploads/status/query batch */
  BATCH_STATUS_MAX_IDS: 100,
} as const;

// ---------------------------------------------------------------------------
// Export Endpoints (async job resource) - نقاط التصدير (@since 4.10.0)
// ---------------------------------------------------------------------------

/** @since 4.10.0 — Async export jobs (GeoJSON feature collections for planting/harvest) */
export const EXPORT_ENDPOINTS = {
  /** POST — Create export job. Body: {contentType, definition?}. Returns 201 + {id}. */
  CREATE: `${API_PREFIX}/exports`,
  /** GET — Poll export status. Returns ExportState + checksum + xNextToken. */
  STATUS: `${API_PREFIX}/exports/{exportId}/status`,
  /** GET — Stream binary contents (Range-chunked, 1–5 MiB). */
  CONTENTS: `${API_PREFIX}/exports/{exportId}/contents`,
} as const;

// ---------------------------------------------------------------------------
// Media Types (Vendor MIME Contract) - أنواع الوسائط (@since 4.10.0)
//
// Vendor MIME types for the unified uploads surface. These mirror FieldView's
// `image/vnd.climate.*` and `application/vnd.climate.*` families so that
// partners ported from FieldView can use the same client code. SAHOOL
// namespace (`vnd.sahool.*`) is used except for AgGateway open standards
// (Modus, ISOXML) which keep their canonical vendor strings.
// ---------------------------------------------------------------------------

/** @since 4.10.0 — Media (MIME) type catalog for /uploads/{CREATE} contentType field */
export const MEDIA_TYPES = {
  // Imagery rasters (GeoTIFF in UTM / WGS-84 datum)
  NDVI_GEOTIFF: "image/vnd.sahool.ndvi.geotiff",
  NDRE_GEOTIFF: "image/vnd.sahool.ndre.geotiff",
  NDWI_GEOTIFF: "image/vnd.sahool.ndwi.geotiff",
  SAVI_GEOTIFF: "image/vnd.sahool.savi.geotiff",
  EVI_GEOTIFF: "image/vnd.sahool.evi.geotiff",
  LAI_GEOTIFF: "image/vnd.sahool.lai.geotiff",
  SCI_GEOTIFF: "image/vnd.sahool.sci.geotiff",
  THERMAL_GEOTIFF: "image/vnd.sahool.thermal.geotiff",
  RGB_GEOTIFF: "image/vnd.sahool.rgb.geotiff",
  RGB_NIR_GEOTIFF: "image/vnd.sahool.rgb-nir.geotiff",
  RGB_CIR_GEOTIFF: "image/vnd.sahool.rgb-cir.geotiff",
  WATER_STRESS_GEOTIFF: "image/vnd.sahool.waterstress.geotiff",
  ELEVATION_GEOTIFF: "image/vnd.sahool.elevation.geotiff",
  RAW_GEOTIFF: "image/vnd.sahool.raw.geotiff",
  // Agronomic data (ZIP / GeoJSON)
  FIELD_GEOJSON: "application/vnd.sahool.field.geojson",
  RX_PLANTING_SHP: "application/vnd.sahool.rx.planting.shp",
  RX_ZONES_SHP: "application/vnd.sahool.prescription.zones.shp",
  STAND_COUNT_GEOJSON: "application/vnd.sahool.stand-count.geojson",
  WEED_COUNT_GEOJSON: "application/vnd.sahool.weed-count.geojson",
  AS_PLANTED_ZIP: "application/vnd.sahool.as-planted.zip",
  AS_HARVESTED_ZIP: "application/vnd.sahool.as-harvested.zip",
  AS_APPLIED_ZIP: "application/vnd.sahool.as-applied.zip",
  // Soil - dual-format (native JSON + AgGateway Modus for lab interop)
  SOIL_SAHOOL_JSON: "application/vnd.sahool.soil.json",
  SOIL_MODUS_XML: "application/vnd.agwg.modus.xml",
  // Machinery telemetry (AgGateway open standards)
  ISOXML_TASKDATA_ZIP: "application/vnd.agwg.isoxml.zip",
  // Generic
  OCTET_STREAM: "application/octet-stream",
} as const;

// ---------------------------------------------------------------------------
// Pagination (Header-Based, Cursor Style) - ترقيم الصفحات (@since 4.10.0)
// ---------------------------------------------------------------------------

/** @since 4.10.0 — Header names for cursor-based pagination (FieldView-compatible) */
export const PAGINATION_HEADERS = {
  /** Request/response: opaque cursor token for next page */
  NEXT_TOKEN: "X-Next-Token",
  /** Request: page size (1..MAX_LIMIT) */
  LIMIT: "X-Limit",
  /** Response: stable request id for support */
  REQUEST_ID: "X-Request-Id",
  /** Response: ETag for conditional GET (304 Not Modified) */
  ETAG: "ETag",
  /** Request: If-None-Match for conditional GET */
  IF_NONE_MATCH: "If-None-Match",
} as const;

/** @since 4.10.0 — Pagination numeric defaults */
export const PAGINATION_DEFAULTS = {
  /** Default items per page when X-Limit omitted */
  DEFAULT_LIMIT: 100,
  /** Hard ceiling on X-Limit */
  MAX_LIMIT: 1000,
} as const;

/** @since 4.10.0 — Canonical HTTP status meanings for paginated list endpoints */
export const PAGINATION_STATUS = {
  /** 200 — complete result (no more pages) */
  COMPLETE: 200,
  /** 206 — partial content; more pages available via X-Next-Token */
  PARTIAL: 206,
  /** 304 — nothing modified since client's X-Next-Token */
  NOT_MODIFIED: 304,
  /** 409 — X-Next-Token expired; client must discard cache and refetch */
  NEXT_TOKEN_EXPIRED: 409,
} as const;

// ---------------------------------------------------------------------------
// State Machines - آلات الحالة (@since 4.10.0)
//
// Explicit, closed enumerations for the Upload and Export lifecycles.
// FieldView's INBOX state (partner-uploads-to-grower with consent gating) is
// adopted to support our `cooperatives` module where dealers upload on behalf
// of farmers; the farmer must ACCEPT before the data enters their account.
// ---------------------------------------------------------------------------

/** @since 4.10.0 — Upload lifecycle states (includes INBOX for dealer-delegation) */
export const UPLOAD_STATES = [
  "UPLOADING",
  "PENDING",
  "INBOX",
  "DECLINED",
  "IMPORTING",
  "SUCCESS",
  "INVALID",
] as const;

/** @since 4.10.0 — Export job lifecycle states */
export const EXPORT_STATES = [
  "PROCESSING",
  "COMPLETED",
  "NO_DATA",
  "INVALID",
  "EXPIRED",
] as const;

// ===========================================================================
// Partner API Surface (@since 4.10.0)
//
// A parallel, OAuth-2.0-authenticated surface for external partners. Mirrors
// FieldView's `/v4/*` so third-party integrations that already speak FieldView
// need minimal adaptation. Serves at `/partner/v1/*` on Kong gateway.
//
// Auth model (per-request):
//   Authorization: Bearer <access_token>   ← identity (OAuth 2.0 + OIDC)
//   X-Sahool-Partner-Key: <opaque>          ← throttling + metering (per partner)
// ===========================================================================

/** @since 4.10.0 — Partner API version (independent of internal /api/v1) */
export const PARTNER_API_VERSION = "v1" as const;

/** @since 4.10.0 — Partner API base path (Kong routes to partner-facing BFF) */
export const PARTNER_PREFIX = `/partner/${PARTNER_API_VERSION}` as const;

/** @since 4.10.0 — Partner OAuth 2.0 + OIDC endpoints */
export const PARTNER_OAUTH_ENDPOINTS = {
  /** GET — Browser redirect for authorization code flow (farmer consent screen) */
  AUTHORIZE: `${PARTNER_PREFIX}/oauth/authorize`,
  /** POST — Token exchange (authorization_code + refresh_token grants) */
  TOKEN: `${PARTNER_PREFIX}/oauth/token`,
  /** POST — Revoke access or refresh token */
  REVOKE: `${PARTNER_PREFIX}/oauth/revoke`,
  /** POST — RFC 7662 token introspection */
  INTROSPECT: `${PARTNER_PREFIX}/oauth/introspect`,
  /** GET — OIDC UserInfo */
  USERINFO: `${PARTNER_PREFIX}/oauth/userinfo`,
  /** GET — OIDC discovery document */
  DISCOVERY: `/.well-known/openid-configuration`,
  /** GET — JWKS for id_token signature verification */
  JWKS: `/.well-known/jwks.json`,
} as const;

/** @since 4.10.0 — Partner OAuth scopes (space-delimited when requested) */
export const PARTNER_OAUTH_SCOPES = [
  // OIDC foundational
  "openid",
  "profile",
  "email",
  "offline_access",
  // Fields & boundaries
  "fields:read",
  "fields:write",
  "boundaries:read",
  "boundaries:write",
  // Agronomic activity layers
  "operations:planting:read",
  "operations:planting:write",
  "operations:harvest:read",
  "operations:harvest:write",
  "operations:application:read",
  "operations:application:write",
  "operations:scouting:read",
  "operations:scouting:write",
  // Imagery
  "imagery:ndvi:read",
  "imagery:ndvi:write",
  "imagery:thermal:read",
  "imagery:rgb:read",
  // Soil & weather
  "soil:read",
  "soil:write",
  "weather:read",
  // Advisory & AI
  "advisory:read",
  "ai:vision:invoke",
  // Carbon (SAHOOL-unique)
  "carbon:read",
  "carbon:mrv:export",
  // Export jobs
  "exports:read",
  // Platform (always granted)
  "partnerapis",
  "platform",
] as const;

/** @since 4.10.0 — Partner request headers (metering, delegation, versioning) */
export const PARTNER_HEADERS = {
  /** Opaque partner API key (separate from OAuth — for throttling + billing metering) */
  API_KEY: "X-Sahool-Partner-Key",
  /** Trace id (echo on every response for support correlation) */
  REQUEST_ID: "X-Request-Id",
  /** Cursor pagination */
  NEXT_TOKEN: "X-Next-Token",
  /** Page size */
  LIMIT: "X-Limit",
  /** Dealer-on-behalf-of-grower delegation (FieldView X-Recipient-Email analogue) */
  RECIPIENT_EMAIL: "X-Recipient-Email",
  /** Contract version the partner client was compiled against */
  CONTRACT_VERSION: "X-Sahool-Contract-Version",
} as const;

/** @since 4.10.0 — Partner limits & rate-ceiling defaults */
export const PARTNER_LIMITS = {
  /** Access token TTL (seconds) — 4h to match FieldView convention */
  ACCESS_TOKEN_TTL_SEC: 14_400,
  /** Refresh token TTL (days) */
  REFRESH_TOKEN_TTL_DAYS: 30,
  /** Used refresh token re-TTL (seconds) — rotation window after a refresh */
  REFRESH_ROTATION_TTL_SEC: 3_600,
  /** Max boundary ids per /boundaries/query batch (FieldView parity) */
  BATCH_BOUNDARY_IDS: 10,
  /** Max field area (hectares) — generous for MENA mega-farms */
  FIELD_MAX_HECTARES: 50_000,
  /** Max polygon vertices per boundary */
  FIELD_MAX_VERTICES: 10_000,
  /** Max VRA/Rx zones per prescription shapefile */
  RX_MAX_ZONES: 100,
} as const;

// ---------------------------------------------------------------------------
// Partner Endpoints — Field & Boundary (@since 4.10.0)
//
// Boundaries are decoupled from Fields (FieldView pattern): listing fields
// returns `{id, name, boundaryId}` only — partners fetch geometry on demand.
// Boundary records are immutable; editing geometry creates a new boundary id
// and the Field row is updated to reference it.
// ---------------------------------------------------------------------------

/** @since 4.10.0 — Partner field directory (lightweight; no inline geometry) */
export const PARTNER_FIELD_ENDPOINTS = {
  /** GET — List fields owned by the authenticated resource owner */
  LIST: `${PARTNER_PREFIX}/fields`,
  /** GET — List fields owned + shared with the authenticated user (may 409) */
  LIST_ALL: `${PARTNER_PREFIX}/fields/all`,
  /** GET — Retrieve a single field (id, name, boundaryId, cropType) */
  GET: `${PARTNER_PREFIX}/fields/{fieldId}`,
} as const;

/** @since 4.10.0 — Partner boundary endpoints (standalone, immutable) */
export const PARTNER_BOUNDARY_ENDPOINTS = {
  /** POST — Upload standalone boundary (does not create a field) */
  CREATE: `${PARTNER_PREFIX}/boundaries`,
  /** GET — Retrieve a boundary by immutable id */
  GET: `${PARTNER_PREFIX}/boundaries/{boundaryId}`,
  /** POST — Batch query boundaries (body: {ids: string[]} ≤ BATCH_BOUNDARY_IDS) */
  BATCH_QUERY: `${PARTNER_PREFIX}/boundaries/query`,
} as const;

/** @since 4.10.0 — Partner resource-owner & farm-organization hierarchy */
export const PARTNER_ORG_ENDPOINTS = {
  /** GET — Resource owner (client account) details */
  RESOURCE_OWNER: `${PARTNER_PREFIX}/resourceOwners/{resourceOwnerId}`,
  /** GET — Farm organization (supports `parent` reference for cooperative hierarchies) */
  FARM_ORG: `${PARTNER_PREFIX}/farmOrganizations/{farmOrganizationType}/{farmOrganizationId}`,
  /** GET — Operations (machine operators) list */
  OPERATIONS: `${PARTNER_PREFIX}/operations/all`,
} as const;

// ---------------------------------------------------------------------------
// Partner Endpoints — Activity Layers (@since 4.10.0)
//
// asPlanted / asHarvested / asApplied / scoutingObservations — FieldView-style
// time-sliced activity layers. `contents` endpoints stream the raw agronomic
// payload (ZIP / ISOXML / shapefile) via Range-chunked download.
// ---------------------------------------------------------------------------

/** @since 4.10.0 — Activity layer endpoints (planting, harvest, application, scouting) */
export const PARTNER_LAYER_ENDPOINTS = {
  AS_PLANTED_LIST: `${PARTNER_PREFIX}/layers/asPlanted`,
  AS_PLANTED_CONTENTS: `${PARTNER_PREFIX}/layers/asPlanted/{activityId}/contents`,
  AS_HARVESTED_LIST: `${PARTNER_PREFIX}/layers/asHarvested`,
  AS_HARVESTED_CONTENTS: `${PARTNER_PREFIX}/layers/asHarvested/{activityId}/contents`,
  AS_APPLIED_LIST: `${PARTNER_PREFIX}/layers/asApplied`,
  AS_APPLIED_CONTENTS: `${PARTNER_PREFIX}/layers/asApplied/{activityId}/contents`,
  SCOUTING_LIST: `${PARTNER_PREFIX}/layers/scoutingObservations`,
  SCOUTING_GET: `${PARTNER_PREFIX}/layers/scoutingObservations/{observationId}`,
  SCOUTING_ATTACHMENTS: `${PARTNER_PREFIX}/layers/scoutingObservations/{observationId}/attachments`,
  SCOUTING_ATTACHMENT_CONTENTS: `${PARTNER_PREFIX}/layers/scoutingObservations/{observationId}/attachments/{attachmentId}/contents`,
} as const;

/** @since 4.10.0 — Partner upload endpoints (same semantics as internal UPLOAD_ENDPOINTS) */
export const PARTNER_UPLOAD_ENDPOINTS = {
  CREATE: `${PARTNER_PREFIX}/uploads`,
  CHUNK: `${PARTNER_PREFIX}/uploads/{uploadId}`,
  STATUS: `${PARTNER_PREFIX}/uploads/{uploadId}/status`,
  BATCH_STATUS: `${PARTNER_PREFIX}/uploads/status/query`,
  CANCEL: `${PARTNER_PREFIX}/uploads/{uploadId}`,
} as const;

/** @since 4.10.0 — Partner export endpoints */
export const PARTNER_EXPORT_ENDPOINTS = {
  CREATE: `${PARTNER_PREFIX}/exports`,
  STATUS: `${PARTNER_PREFIX}/exports/{exportId}/status`,
  CONTENTS: `${PARTNER_PREFIX}/exports/{exportId}/contents`,
} as const;

// ---------------------------------------------------------------------------
// Partner Admin Endpoints (@since 4.12.0)
//
// SAHOOL-internal administration of the partner OAuth ecosystem. These
// live under /api/v1/admin/partner-auth/* (NOT /partner/v1/*) because
// partners themselves never call these — only SAHOOL staff (via admin
// portal) and automated on-boarding tooling.
//
// Protected by role check: JWT must carry `role: "ADMIN"`. Served by
// partner-auth-service (port 3030) via Kong route `/api/v1/admin/
// partner-auth/*` → partner-auth-service.
// ---------------------------------------------------------------------------

const ADMIN_PARTNER_AUTH_PREFIX = `${API_PREFIX}/admin/partner-auth` as const;

/** @since 4.12.0 — Partner OAuth client management (CRUD + secret rotation) */
export const PARTNER_ADMIN_CLIENT_ENDPOINTS = {
  /** POST — Register a new partner app. Returns {client_id, client_secret} ONCE. */
  CREATE: `${ADMIN_PARTNER_AUTH_PREFIX}/clients`,
  /** GET — List all registered clients (paginated, supports ?status= filter) */
  LIST: `${ADMIN_PARTNER_AUTH_PREFIX}/clients`,
  /** GET — Retrieve one client's public metadata (never returns secret hash) */
  GET: `${ADMIN_PARTNER_AUTH_PREFIX}/clients/{clientId}`,
  /** PATCH — Update name, description, redirect URIs, allowed scopes, rate tier */
  UPDATE: `${ADMIN_PARTNER_AUTH_PREFIX}/clients/{clientId}`,
  /** POST — Generate a new client_secret and invalidate the old one. Returns the
   *  plaintext once — caller must capture it. */
  ROTATE_SECRET: `${ADMIN_PARTNER_AUTH_PREFIX}/clients/{clientId}/rotate-secret`,
  /** POST — Generate a new X-Sahool-Partner-Key (for throttling/metering).
   *  Separate from client_secret so metering can rotate independently. */
  ROTATE_API_KEY: `${ADMIN_PARTNER_AUTH_PREFIX}/clients/{clientId}/rotate-api-key`,
  /** POST — Set status=suspended (temporarily blocks all flows) */
  SUSPEND: `${ADMIN_PARTNER_AUTH_PREFIX}/clients/{clientId}/suspend`,
  /** POST — Unsuspend (status=active) */
  UNSUSPEND: `${ADMIN_PARTNER_AUTH_PREFIX}/clients/{clientId}/unsuspend`,
  /** DELETE — Permanently revoke (status=revoked + cascade revoke all tokens) */
  REVOKE: `${ADMIN_PARTNER_AUTH_PREFIX}/clients/{clientId}`,
} as const;

/** @since 4.12.0 — Consent grant inspection + revocation (per-client or per-user) */
export const PARTNER_ADMIN_CONSENT_ENDPOINTS = {
  /** GET — List consents (filter by ?clientId= or ?userId=) */
  LIST: `${ADMIN_PARTNER_AUTH_PREFIX}/consents`,
  /** DELETE — Revoke a consent grant (user's "forget me" for this client) */
  REVOKE: `${ADMIN_PARTNER_AUTH_PREFIX}/consents/{grantId}`,
} as const;

/** @since 4.12.0 — Token visibility + incident-response revocation */
export const PARTNER_ADMIN_TOKEN_ENDPOINTS = {
  /** GET — List active access tokens (filter by ?clientId= or ?userId=) */
  LIST_ACCESS: `${ADMIN_PARTNER_AUTH_PREFIX}/tokens/access`,
  /** GET — List active refresh tokens + rotation chains */
  LIST_REFRESH: `${ADMIN_PARTNER_AUTH_PREFIX}/tokens/refresh`,
  /** POST — Emergency revoke all tokens for a client (breach response) */
  REVOKE_ALL_FOR_CLIENT: `${ADMIN_PARTNER_AUTH_PREFIX}/tokens/revoke-all/client/{clientId}`,
  /** POST — Revoke all tokens for a user across all partners */
  REVOKE_ALL_FOR_USER: `${ADMIN_PARTNER_AUTH_PREFIX}/tokens/revoke-all/user/{userId}`,
} as const;

/** @since 4.12.0 — RSA signing key rotation (id_token JWS keys) */
export const PARTNER_ADMIN_SIGNING_KEY_ENDPOINTS = {
  /** GET — List all signing keys (active + retired-but-verifying) */
  LIST: `${ADMIN_PARTNER_AUTH_PREFIX}/signing-keys`,
  /** POST — Generate a new RSA keypair, mark it active, retire the old */
  ROTATE: `${ADMIN_PARTNER_AUTH_PREFIX}/signing-keys/rotate`,
  /** DELETE — Permanently delete a fully-expired retired key */
  DELETE: `${ADMIN_PARTNER_AUTH_PREFIX}/signing-keys/{kid}`,
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
