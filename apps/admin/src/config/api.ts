/**
 * SAHOOL Admin API Configuration
 * Centralized API configuration - Single source of truth
 * تكوين API المركزي - مصدر الحقيقة الوحيد
 *
 * This file provides centralized API URL configuration for the admin dashboard.
 * All services should import their API URLs from here for consistency.
 *
 * @module config/api
 */

// ═══════════════════════════════════════════════════════════════════════════
// Environment Configuration
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Determines if the application is running in production mode
 */
export const IS_PRODUCTION = process.env.NODE_ENV === "production";

/**
 * Determines if the application is running in development mode
 */
export const IS_DEVELOPMENT = process.env.NODE_ENV === "development";

/**
 * Determines if the application is running in test mode
 */
export const IS_TEST = process.env.NODE_ENV === "test";

// ═══════════════════════════════════════════════════════════════════════════
// Base URL Configuration
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Base URL for the API Gateway (Kong)
 * In production: Uses NEXT_PUBLIC_API_URL
 * In development: Falls back to localhost:8000 (Kong gateway port)
 */
export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Alias for API_BASE_URL for backward compatibility
 * @deprecated Use API_BASE_URL instead
 */
export const API_URL = API_BASE_URL;

/**
 * Base hostname without port for direct service access in development
 */
export const API_BASE_HOST =
  process.env.NEXT_PUBLIC_API_BASE || "http://localhost";

// ═══════════════════════════════════════════════════════════════════════════
// Service Ports (from unified contracts)
// Sourced from @sahool/shared-types/contracts/service-ports.ts
// ═══════════════════════════════════════════════════════════════════════════

import {
  SERVICE_PORTS as UNIFIED_PORTS,
  HEALTH_ENDPOINTS,
  AUTH_ENDPOINTS,
  FIELD_ENDPOINTS,
  CROP_HEALTH_ENDPOINTS,
  IRRIGATION_ENDPOINTS,
  ADVISORY_ENDPOINTS,
  TASK_ENDPOINTS,
  EQUIPMENT_ENDPOINTS,
  NOTIFICATION_ENDPOINTS,
  IOT_ENDPOINTS,
  INDICATOR_ENDPOINTS,
  BILLING_ENDPOINTS,
  AUDIT_ENDPOINTS,
  SOIL_ENDPOINTS,
  DRONE_ENDPOINTS,
  INVENTORY_ENDPOINTS,
  TRACEABILITY_ENDPOINTS,
  TERRAIN_ENDPOINTS,
  CHAT_ENDPOINTS,
  YIELD_ENDPOINTS,
  buildUrl,
} from "@sahool/shared-types/contracts";

/**
 * Port mapping for all backend services
 * Now sourced from @sahool/shared-types/contracts (single source of truth)
 *
 * FIXED: auth was 8080 → now 3025 (USER_SERVICE via Kong)
 * FIXED: soilAnalysis was 8124 → now 8134
 */
export const SERVICE_PORTS = {
  // Core Services
  fieldCore: UNIFIED_PORTS.FIELD_MANAGEMENT,
  fieldManagement: UNIFIED_PORTS.FIELD_MANAGEMENT,
  auth: UNIFIED_PORTS.USER_SERVICE,
  users: UNIFIED_PORTS.USER_SERVICE,
  wsGateway: UNIFIED_PORTS.WS_GATEWAY,

  // Satellite & Remote Sensing
  satellite: UNIFIED_PORTS.VEGETATION_ANALYSIS,
  ndviProcessor: UNIFIED_PORTS.NDVI_PROCESSOR,

  // Weather Services
  weather: UNIFIED_PORTS.WEATHER,

  // AI & Analytics
  indicators: UNIFIED_PORTS.INDICATORS,
  cropIntelligence: UNIFIED_PORTS.CROP_INTELLIGENCE,
  advisory: UNIFIED_PORTS.ADVISORY,
  yieldPrediction: UNIFIED_PORTS.YIELD_PREDICTION,
  fieldIntelligence: UNIFIED_PORTS.FIELD_INTELLIGENCE,
  // analytics: removed — port 8100 was deprecated crop-health service, no active service
  copilot: UNIFIED_PORTS.COPILOT_API,
  aiAdvisor: UNIFIED_PORTS.AI_ADVISOR,
  aiAgents: UNIFIED_PORTS.AI_AGENTS_CORE,
  knowledgeGraph: UNIFIED_PORTS.KNOWLEDGE_GRAPH,

  // IoT & Sensors
  virtualSensors: UNIFIED_PORTS.VIRTUAL_SENSORS,
  iotGateway: UNIFIED_PORTS.IOT_GATEWAY,
  iotService: UNIFIED_PORTS.IOT_SERVICE,

  // Operations
  irrigation: UNIFIED_PORTS.IRRIGATION_SMART,
  task: UNIFIED_PORTS.TASK_SERVICE,
  equipment: UNIFIED_PORTS.EQUIPMENT,
  inventory: UNIFIED_PORTS.INVENTORY,
  logistics: UNIFIED_PORTS.LOGISTICS,
  supplyChain: UNIFIED_PORTS.SUPPLY_CHAIN,

  // Communication
  notifications: UNIFIED_PORTS.NOTIFICATIONS,
  fieldChat: UNIFIED_PORTS.FIELD_CHAT,
  chatService: UNIFIED_PORTS.CHAT_SERVICE,
  communityChat: UNIFIED_PORTS.COMMUNITY_CHAT,

  // Configuration & Misc
  providerConfig: UNIFIED_PORTS.PROVIDER_CONFIG,
  alerts: UNIFIED_PORTS.ALERT_SERVICE,
  // reports: removed — port 8084 has no registered service in governance/services.yaml
  astronomicalCalendar: UNIFIED_PORTS.ASTRONOMICAL_CALENDAR,
  lowcode: UNIFIED_PORTS.LOWCODE_ENGINE,

  // Billing & Audit
  billing: UNIFIED_PORTS.BILLING_CORE,
  audit: UNIFIED_PORTS.AUDIT_SERVICE,

  // Agriculture Domain
  drone: UNIFIED_PORTS.DRONE_SERVICE,
  soilAnalysis: UNIFIED_PORTS.SOIL_ANALYSIS,
  pestDetection: UNIFIED_PORTS.PEST_DETECTION,
  traceability: UNIFIED_PORTS.TRACEABILITY,
  globalgap: UNIFIED_PORTS.GLOBALGAP,
  cooperative: UNIFIED_PORTS.COOPERATIVE,
  crm: UNIFIED_PORTS.CRM_SERVICE,

  // Community & Business
  marketplace: UNIFIED_PORTS.MARKETPLACE,
  research: UNIFIED_PORTS.RESEARCH_CORE,

  // Vision & Terrain
  yoloVision: UNIFIED_PORTS.YOLO_VISION,
  terrainCore: UNIFIED_PORTS.TERRAIN_CORE,
  hydrology: UNIFIED_PORTS.HYDROLOGY,
  levelingOptimizer: UNIFIED_PORTS.LEVELING_OPTIMIZER,
  edgeOrchestrator: UNIFIED_PORTS.EDGE_ORCHESTRATOR,
} as const;

/**
 * Type for service port keys
 */
export type ServicePortKey = keyof typeof SERVICE_PORTS;

// ═══════════════════════════════════════════════════════════════════════════
// Service URL Generation
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Generates a service URL based on environment
 * In production: Uses base URL (Kong gateway handles routing)
 * In development: Uses direct port access
 *
 * @param port - The service port number
 * @returns The complete service URL
 */
export function getServiceUrl(port: number): string {
  return IS_PRODUCTION ? API_BASE_URL : `${API_BASE_HOST}:${port}`;
}

// ═══════════════════════════════════════════════════════════════════════════
// Service URLs
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Complete URLs for all backend services
 */
export const SERVICE_URLS = {
  // Core Services
  fieldCore: getServiceUrl(SERVICE_PORTS.fieldCore),
  fieldManagement: getServiceUrl(SERVICE_PORTS.fieldManagement),
  auth: getServiceUrl(SERVICE_PORTS.auth),
  users: getServiceUrl(SERVICE_PORTS.users),
  wsGateway: getServiceUrl(SERVICE_PORTS.wsGateway),

  // Satellite & Remote Sensing
  satellite: getServiceUrl(SERVICE_PORTS.satellite),
  ndviProcessor: getServiceUrl(SERVICE_PORTS.ndviProcessor),

  // Weather
  weather: getServiceUrl(SERVICE_PORTS.weather),

  // AI & Analytics
  indicators: getServiceUrl(SERVICE_PORTS.indicators),
  cropIntelligence: getServiceUrl(SERVICE_PORTS.cropIntelligence),
  advisory: getServiceUrl(SERVICE_PORTS.advisory),
  yieldPrediction: getServiceUrl(SERVICE_PORTS.yieldPrediction),
  fieldIntelligence: getServiceUrl(SERVICE_PORTS.fieldIntelligence),
  // analytics: removed — no active service on port 8100
  copilot: getServiceUrl(SERVICE_PORTS.copilot),
  aiAdvisor: getServiceUrl(SERVICE_PORTS.aiAdvisor),
  aiAgents: getServiceUrl(SERVICE_PORTS.aiAgents),
  knowledgeGraph: getServiceUrl(SERVICE_PORTS.knowledgeGraph),

  // IoT & Sensors
  virtualSensors: getServiceUrl(SERVICE_PORTS.virtualSensors),
  iotGateway: getServiceUrl(SERVICE_PORTS.iotGateway),
  iotService: getServiceUrl(SERVICE_PORTS.iotService),

  // Operations
  irrigation: getServiceUrl(SERVICE_PORTS.irrigation),
  task: getServiceUrl(SERVICE_PORTS.task),
  equipment: getServiceUrl(SERVICE_PORTS.equipment),
  inventory: getServiceUrl(SERVICE_PORTS.inventory),
  logistics: getServiceUrl(SERVICE_PORTS.logistics),
  supplyChain: getServiceUrl(SERVICE_PORTS.supplyChain),

  // Communication
  notifications: getServiceUrl(SERVICE_PORTS.notifications),
  fieldChat: getServiceUrl(SERVICE_PORTS.fieldChat),
  chatService: getServiceUrl(SERVICE_PORTS.chatService),
  communityChat: getServiceUrl(SERVICE_PORTS.communityChat),

  // Configuration & Misc
  providerConfig: getServiceUrl(SERVICE_PORTS.providerConfig),
  alerts: getServiceUrl(SERVICE_PORTS.alerts),
  // reports: removed — no registered service on port 8084
  astronomicalCalendar: getServiceUrl(SERVICE_PORTS.astronomicalCalendar),
  lowcode: getServiceUrl(SERVICE_PORTS.lowcode),

  // Billing & Audit
  billing: getServiceUrl(SERVICE_PORTS.billing),
  audit: getServiceUrl(SERVICE_PORTS.audit),

  // Agriculture Domain
  drone: getServiceUrl(SERVICE_PORTS.drone),
  soilAnalysis: getServiceUrl(SERVICE_PORTS.soilAnalysis),
  pestDetection: getServiceUrl(SERVICE_PORTS.pestDetection),
  traceability: getServiceUrl(SERVICE_PORTS.traceability),
  globalgap: getServiceUrl(SERVICE_PORTS.globalgap),
  cooperative: getServiceUrl(SERVICE_PORTS.cooperative),
  crm: getServiceUrl(SERVICE_PORTS.crm),

  // Community & Business
  marketplace: getServiceUrl(SERVICE_PORTS.marketplace),
  research: getServiceUrl(SERVICE_PORTS.research),

  // Vision & Terrain
  yoloVision: getServiceUrl(SERVICE_PORTS.yoloVision),
  terrainCore: getServiceUrl(SERVICE_PORTS.terrainCore),
  hydrology: getServiceUrl(SERVICE_PORTS.hydrology),
  levelingOptimizer: getServiceUrl(SERVICE_PORTS.levelingOptimizer),
  edgeOrchestrator: getServiceUrl(SERVICE_PORTS.edgeOrchestrator),
} as const;

/**
 * Type for service URL keys
 */
export type ServiceUrlKey = keyof typeof SERVICE_URLS;

// ═══════════════════════════════════════════════════════════════════════════
// API Endpoint Paths
// ═══════════════════════════════════════════════════════════════════════════

/**
 * API endpoint path definitions
 * These are relative paths that can be combined with SERVICE_URLS
 */
export const API_PATHS = {
  // Health Endpoints (from unified contracts)
  health: {
    live: HEALTH_ENDPOINTS.LIVENESS,
    ready: HEALTH_ENDPOINTS.READINESS,
    check: HEALTH_ENDPOINTS.HEALTH,
    metrics: HEALTH_ENDPOINTS.METRICS,
  },

  // Authentication (from unified contracts)
  auth: {
    login: AUTH_ENDPOINTS.LOGIN,
    logout: AUTH_ENDPOINTS.LOGOUT,
    refresh: AUTH_ENDPOINTS.REFRESH,
    me: AUTH_ENDPOINTS.ME,
    activity: AUTH_ENDPOINTS.ACTIVITY,
  },

  // Fields & Farms (from unified contracts)
  fields: {
    list: FIELD_ENDPOINTS.LIST,
    byId: (id: string) => buildUrl(FIELD_ENDPOINTS.GET, { fieldId: id }),
    create: FIELD_ENDPOINTS.CREATE,
    update: (id: string) => buildUrl(FIELD_ENDPOINTS.UPDATE, { fieldId: id }),
    delete: (id: string) => buildUrl(FIELD_ENDPOINTS.DELETE, { fieldId: id }),
  },

  // Crop Health & Diagnoses (from unified contracts)
  cropHealth: {
    diagnoses: CROP_HEALTH_ENDPOINTS.DIAGNOSES_LIST,
    diagnosisById: (id: string) => buildUrl(CROP_HEALTH_ENDPOINTS.DIAGNOSES_UPDATE, { diagnosisId: id }),
    stats: CROP_HEALTH_ENDPOINTS.DIAGNOSES_STATS,
    analyze: CROP_HEALTH_ENDPOINTS.ANALYZE,
  },

  // Weather Services (direct service paths - not Kong-routed)
  weather: {
    current: "/weather/current",
    forecast: "/weather/forecast",
    agricultural: "/weather/agricultural-report",
    alerts: (locationId: string) => `/v1/alerts/${locationId}`,
    locations: "/v1/locations",
    byLocation: (locationId: string) => `/v1/current/${locationId}`,
    forecastByLocation: (locationId: string) => `/v1/forecast/${locationId}`,
  },

  // Satellite & Vegetation (direct service paths - not Kong-routed)
  satellite: {
    timeseries: (fieldId: string) => `/v1/timeseries/${fieldId}`,
    analyze: "/v1/analyze",
    indices: (fieldId: string) => `/v1/indices/${fieldId}`,
    satellites: "/v1/satellites",
  },

  // Dashboard & Indicators (from unified contracts)
  indicators: {
    dashboard: INDICATOR_ENDPOINTS.DASHBOARD,
    summary: INDICATOR_ENDPOINTS.SUMMARY,
    trends: INDICATOR_ENDPOINTS.TRENDS,
  },

  // IoT & Sensors (from unified contracts)
  sensors: {
    readings: (farmId: string) => buildUrl(IOT_ENDPOINTS.READINGS_BY_FARM, { farmId }),
    devices: IOT_ENDPOINTS.DEVICES,
    deviceById: (id: string) => buildUrl(IOT_ENDPOINTS.DEVICE_GET, { deviceId: id }),
  },

  // Irrigation (from unified contracts)
  irrigation: {
    schedules: IRRIGATION_ENDPOINTS.SCHEDULES_LIST,
    recommendations: IRRIGATION_ENDPOINTS.RECOMMENDATIONS,
    history: (fieldId: string) => buildUrl(IRRIGATION_ENDPOINTS.HISTORY, { fieldId }),
  },

  // Notifications (from unified contracts)
  notifications: {
    list: NOTIFICATION_ENDPOINTS.LIST,
    byId: (id: string) => buildUrl(NOTIFICATION_ENDPOINTS.GET, { notificationId: id }),
    markRead: (id: string) => buildUrl(NOTIFICATION_ENDPOINTS.MARK_READ, { notificationId: id }),
    markAllRead: NOTIFICATION_ENDPOINTS.MARK_ALL_READ,
  },

  // Tasks (from unified contracts)
  tasks: {
    list: TASK_ENDPOINTS.LIST,
    byId: (id: string) => buildUrl(TASK_ENDPOINTS.GET, { taskId: id }),
    create: TASK_ENDPOINTS.CREATE,
    update: (id: string) => buildUrl(TASK_ENDPOINTS.UPDATE, { taskId: id }),
  },

  // Equipment (from unified contracts)
  equipment: {
    list: EQUIPMENT_ENDPOINTS.LIST,
    byId: (id: string) => buildUrl(EQUIPMENT_ENDPOINTS.GET, { equipmentId: id }),
    maintenance: (id: string) => buildUrl(EQUIPMENT_ENDPOINTS.MAINTENANCE, { equipmentId: id }),
  },

  // Community (from unified contracts)
  community: {
    posts: CHAT_ENDPOINTS.COMMUNITY_POSTS,
    postById: (id: string) => buildUrl(CHAT_ENDPOINTS.COMMUNITY_POST_GET, { postId: id }),
    comments: (postId: string) => buildUrl(CHAT_ENDPOINTS.COMMUNITY_COMMENTS, { postId }),
  },

  // Advisory (from unified contracts)
  advisory: {
    recommendations: ADVISORY_ENDPOINTS.RECOMMENDATIONS,
    fertilizer: ADVISORY_ENDPOINTS.FERTILIZER_ADVISORY,
    calculate: ADVISORY_ENDPOINTS.FERTILIZER_CALCULATE,
  },

  // Yield (from unified contracts)
  yield: {
    predictions: YIELD_ENDPOINTS.PREDICTIONS,
    history: (fieldId: string) => buildUrl(YIELD_ENDPOINTS.HISTORY, { fieldId }),
  },

  // Analytics (admin-specific, no unified contract)
  analytics: {
    overview: "/api/v1/analytics/overview",
    reports: "/api/v1/analytics/reports",
    export: "/api/v1/analytics/export",
  },

  // Copilot (admin-specific routing, different from Kong paths)
  copilot: {
    chat: "/api/v1/chat",
    chatHistory: "/api/v1/chat/history",
    chatById: (id: string) => `/api/v1/chat/${id}`,
    tools: "/api/v1/tools",
    toolExecute: (toolName: string) => `/api/v1/tools/${toolName}/execute`,
    ragDocuments: "/api/v1/rag/documents",
    ragSearch: "/api/v1/rag/search",
    guardLogs: "/api/v1/security/guard-logs",
  },

  // Billing (from unified contracts)
  billing: {
    invoices: BILLING_ENDPOINTS.INVOICES,
    invoiceById: (id: string) => buildUrl(BILLING_ENDPOINTS.INVOICE_GET, { invoiceId: id }),
    subscriptions: BILLING_ENDPOINTS.SUBSCRIPTIONS,
    usage: BILLING_ENDPOINTS.USAGE,
  },

  // Audit (from unified contracts)
  audit: {
    logs: AUDIT_ENDPOINTS.LOGS,
    logById: (id: string) => buildUrl(AUDIT_ENDPOINTS.LOG_GET, { logId: id }),
    stats: AUDIT_ENDPOINTS.STATS,
  },

  // Inventory (from unified contracts)
  inventory: {
    items: INVENTORY_ENDPOINTS.LIST,
    itemById: (id: string) => buildUrl(INVENTORY_ENDPOINTS.GET, { itemId: id }),
    stockLevels: INVENTORY_ENDPOINTS.STOCK_LEVELS,
  },

  // Drone (from unified contracts)
  drone: {
    flights: DRONE_ENDPOINTS.FLIGHTS,
    flightById: (id: string) => buildUrl(DRONE_ENDPOINTS.FLIGHT_GET, { flightId: id }),
    plan: DRONE_ENDPOINTS.FLIGHT_PLAN,
    devices: DRONE_ENDPOINTS.DEVICES,
  },

  // Soil Analysis (from unified contracts)
  soilAnalysis: {
    tests: SOIL_ENDPOINTS.TESTS,
    testById: (id: string) => buildUrl(SOIL_ENDPOINTS.TEST_GET, { testId: id }),
    recommendations: SOIL_ENDPOINTS.RECOMMENDATIONS,
  },

  // Traceability (from unified contracts)
  traceability: {
    batches: TRACEABILITY_ENDPOINTS.BATCHES,
    batchById: (id: string) => buildUrl(TRACEABILITY_ENDPOINTS.BATCH_GET, { batchId: id }),
    events: TRACEABILITY_ENDPOINTS.EVENTS,
    qrCode: (batchId: string) => buildUrl(TRACEABILITY_ENDPOINTS.QR_CODE, { batchId }),
  },

  // Vision (direct service paths - vision service internal routing)
  vision: {
    detectPest: "/api/v1/detect/pest",
    detectDisease: "/api/v1/detect/disease",
    detectWeed: "/api/v1/detect/weed",
    models: "/api/v1/models/versions",
  },

  // Terrain (from unified contracts)
  terrain: {
    analyze: TERRAIN_ENDPOINTS.DEM,
    slope: TERRAIN_ENDPOINTS.SLOPE,
    aspect: TERRAIN_ENDPOINTS.ASPECT,
  },
} as const;

/**
 * Alias for API_PATHS for backward compatibility
 * @deprecated Use API_PATHS instead
 */
export const API_ENDPOINTS = API_PATHS;

// ═══════════════════════════════════════════════════════════════════════════
// Complete API URLs (Service URL + Path)
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Complete API URLs combining service URLs with endpoint paths
 * Usage: API_URLS.auth.login, API_URLS.fields.list, etc.
 */
export const API_URLS = {
  // Service base URLs
  fieldCore: SERVICE_URLS.fieldCore,
  fieldManagement: SERVICE_URLS.fieldManagement,
  satellite: SERVICE_URLS.satellite,
  indicators: SERVICE_URLS.indicators,
  weather: SERVICE_URLS.weather,
  advisory: SERVICE_URLS.advisory,
  irrigation: SERVICE_URLS.irrigation,
  cropIntelligence: SERVICE_URLS.cropIntelligence,
  yieldPrediction: SERVICE_URLS.yieldPrediction,
  fieldIntelligence: SERVICE_URLS.fieldIntelligence,
  aiAgents: SERVICE_URLS.aiAgents,
  virtualSensors: SERVICE_URLS.virtualSensors,
  equipment: SERVICE_URLS.equipment,
  task: SERVICE_URLS.task,
  providerConfig: SERVICE_URLS.providerConfig,
  alerts: SERVICE_URLS.alerts,
  astronomicalCalendar: SERVICE_URLS.astronomicalCalendar,
  lowcode: SERVICE_URLS.lowcode,
  iotService: SERVICE_URLS.iotService,
  notifications: SERVICE_URLS.notifications,
  wsGateway: SERVICE_URLS.wsGateway,
  copilot: SERVICE_URLS.copilot,
  billing: SERVICE_URLS.billing,
  audit: SERVICE_URLS.audit,
  crm: SERVICE_URLS.crm,
  fieldChat: SERVICE_URLS.fieldChat,
  chatService: SERVICE_URLS.chatService,
  communityChat: SERVICE_URLS.communityChat,
  marketplace: SERVICE_URLS.marketplace,
  research: SERVICE_URLS.research,
  drone: SERVICE_URLS.drone,
  soilAnalysis: SERVICE_URLS.soilAnalysis,
  traceability: SERVICE_URLS.traceability,
  yoloVision: SERVICE_URLS.yoloVision,
  terrainCore: SERVICE_URLS.terrainCore,

  // Authentication endpoints
  auth: {
    login: `${API_BASE_URL}${API_PATHS.auth.login}`,
    logout: `${API_BASE_URL}${API_PATHS.auth.logout}`,
    refresh: `${API_BASE_URL}${API_PATHS.auth.refresh}`,
    me: `${API_BASE_URL}${API_PATHS.auth.me}`,
    activity: `${API_BASE_URL}${API_PATHS.auth.activity}`,
  },

  // Field management endpoints
  fields: {
    list: `${SERVICE_URLS.fieldManagement}${API_PATHS.fields.list}`,
    byId: (id: string) => `${SERVICE_URLS.fieldManagement}${API_PATHS.fields.byId(id)}`,
    create: `${SERVICE_URLS.fieldManagement}${API_PATHS.fields.create}`,
    update: (id: string) => `${SERVICE_URLS.fieldManagement}${API_PATHS.fields.update(id)}`,
    delete: (id: string) => `${SERVICE_URLS.fieldManagement}${API_PATHS.fields.delete(id)}`,
  },

  // Crop intelligence endpoints
  diagnoses: {
    list: `${SERVICE_URLS.cropIntelligence}${API_PATHS.cropHealth.diagnoses}`,
    byId: (id: string) =>
      `${SERVICE_URLS.cropIntelligence}${API_PATHS.cropHealth.diagnosisById(id)}`,
    stats: `${SERVICE_URLS.cropIntelligence}${API_PATHS.cropHealth.stats}`,
    analyze: `${SERVICE_URLS.cropIntelligence}${API_PATHS.cropHealth.analyze}`,
  },

  // Weather endpoints
  weatherEndpoints: {
    current: `${SERVICE_URLS.weather}${API_PATHS.weather.current}`,
    forecast: `${SERVICE_URLS.weather}${API_PATHS.weather.forecast}`,
    agricultural: `${SERVICE_URLS.weather}${API_PATHS.weather.agricultural}`,
    alerts: (locationId: string) =>
      `${SERVICE_URLS.weather}${API_PATHS.weather.alerts(locationId)}`,
    locations: `${SERVICE_URLS.weather}${API_PATHS.weather.locations}`,
    byLocation: (locationId: string) =>
      `${SERVICE_URLS.weather}${API_PATHS.weather.byLocation(locationId)}`,
  },

  // Satellite endpoints
  satelliteEndpoints: {
    timeseries: (fieldId: string) =>
      `${SERVICE_URLS.satellite}${API_PATHS.satellite.timeseries(fieldId)}`,
    analyze: `${SERVICE_URLS.satellite}${API_PATHS.satellite.analyze}`,
    indices: (fieldId: string) =>
      `${SERVICE_URLS.satellite}${API_PATHS.satellite.indices(fieldId)}`,
    satellites: `${SERVICE_URLS.satellite}${API_PATHS.satellite.satellites}`,
  },

  // Dashboard/Indicators endpoints
  dashboard: {
    stats: `${SERVICE_URLS.indicators}${API_PATHS.indicators.dashboard}`,
    summary: `${SERVICE_URLS.indicators}${API_PATHS.indicators.summary}`,
    trends: `${SERVICE_URLS.indicators}${API_PATHS.indicators.trends}`,
  },

  // Sensor endpoints
  sensors: {
    readings: (farmId: string) =>
      `${SERVICE_URLS.virtualSensors}${API_PATHS.sensors.readings(farmId)}`,
    devices: `${SERVICE_URLS.virtualSensors}${API_PATHS.sensors.devices}`,
  },

  // Notification endpoints
  notificationEndpoints: {
    list: `${SERVICE_URLS.notifications}${API_PATHS.notifications.list}`,
    byId: (id: string) =>
      `${SERVICE_URLS.notifications}${API_PATHS.notifications.byId(id)}`,
    markRead: (id: string) =>
      `${SERVICE_URLS.notifications}${API_PATHS.notifications.markRead(id)}`,
    markAllRead: `${SERVICE_URLS.notifications}${API_PATHS.notifications.markAllRead}`,
  },

  // Task endpoints
  taskEndpoints: {
    list: `${SERVICE_URLS.task}${API_PATHS.tasks.list}`,
    byId: (id: string) => `${SERVICE_URLS.task}${API_PATHS.tasks.byId(id)}`,
    create: `${SERVICE_URLS.task}${API_PATHS.tasks.create}`,
  },

  // Equipment endpoints
  equipmentEndpoints: {
    list: `${SERVICE_URLS.equipment}${API_PATHS.equipment.list}`,
    byId: (id: string) => `${SERVICE_URLS.equipment}${API_PATHS.equipment.byId(id)}`,
  },

  // Copilot endpoints
  copilotEndpoints: {
    chat: `${SERVICE_URLS.copilot}${API_PATHS.copilot.chat}`,
    chatHistory: `${SERVICE_URLS.copilot}${API_PATHS.copilot.chatHistory}`,
    chatById: (id: string) => `${SERVICE_URLS.copilot}${API_PATHS.copilot.chatById(id)}`,
    tools: `${SERVICE_URLS.copilot}${API_PATHS.copilot.tools}`,
    ragDocuments: `${SERVICE_URLS.copilot}${API_PATHS.copilot.ragDocuments}`,
    ragSearch: `${SERVICE_URLS.copilot}${API_PATHS.copilot.ragSearch}`,
    guardLogs: `${SERVICE_URLS.copilot}${API_PATHS.copilot.guardLogs}`,
  },

  // Billing endpoints
  billingEndpoints: {
    invoices: `${SERVICE_URLS.billing}${API_PATHS.billing.invoices}`,
    invoiceById: (id: string) => `${SERVICE_URLS.billing}${API_PATHS.billing.invoiceById(id)}`,
    subscriptions: `${SERVICE_URLS.billing}${API_PATHS.billing.subscriptions}`,
    usage: `${SERVICE_URLS.billing}${API_PATHS.billing.usage}`,
  },

  // Audit endpoints
  auditEndpoints: {
    logs: `${SERVICE_URLS.audit}${API_PATHS.audit.logs}`,
    logById: (id: string) => `${SERVICE_URLS.audit}${API_PATHS.audit.logById(id)}`,
    stats: `${SERVICE_URLS.audit}${API_PATHS.audit.stats}`,
  },

  // Drone endpoints
  droneEndpoints: {
    flights: `${SERVICE_URLS.drone}${API_PATHS.drone.flights}`,
    flightById: (id: string) => `${SERVICE_URLS.drone}${API_PATHS.drone.flightById(id)}`,
    plan: `${SERVICE_URLS.drone}${API_PATHS.drone.plan}`,
    devices: `${SERVICE_URLS.drone}${API_PATHS.drone.devices}`,
  },

  // Soil Analysis endpoints
  soilEndpoints: {
    tests: `${SERVICE_URLS.soilAnalysis}${API_PATHS.soilAnalysis.tests}`,
    testById: (id: string) => `${SERVICE_URLS.soilAnalysis}${API_PATHS.soilAnalysis.testById(id)}`,
    recommendations: `${SERVICE_URLS.soilAnalysis}${API_PATHS.soilAnalysis.recommendations}`,
  },

  // Traceability endpoints
  traceabilityEndpoints: {
    batches: `${SERVICE_URLS.traceability}${API_PATHS.traceability.batches}`,
    batchById: (id: string) => `${SERVICE_URLS.traceability}${API_PATHS.traceability.batchById(id)}`,
    events: `${SERVICE_URLS.traceability}${API_PATHS.traceability.events}`,
    qrCode: (batchId: string) => `${SERVICE_URLS.traceability}${API_PATHS.traceability.qrCode(batchId)}`,
  },

  // Vision endpoints
  visionEndpoints: {
    detectPest: `${SERVICE_URLS.yoloVision}${API_PATHS.vision.detectPest}`,
    detectDisease: `${SERVICE_URLS.yoloVision}${API_PATHS.vision.detectDisease}`,
    detectWeed: `${SERVICE_URLS.yoloVision}${API_PATHS.vision.detectWeed}`,
    models: `${SERVICE_URLS.yoloVision}${API_PATHS.vision.models}`,
  },

  // Terrain endpoints
  terrainEndpoints: {
    analyze: `${SERVICE_URLS.terrainCore}${API_PATHS.terrain.analyze}`,
    slope: `${SERVICE_URLS.terrainCore}${API_PATHS.terrain.slope}`,
    aspect: `${SERVICE_URLS.terrainCore}${API_PATHS.terrain.aspect}`,
  },

  // Health check helper
  health: (serviceUrl: string) => `${serviceUrl}${API_PATHS.health.live}`,
} as const;

// ═══════════════════════════════════════════════════════════════════════════
// Request Configuration
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Default request timeout in milliseconds
 */
export const DEFAULT_TIMEOUT = 30000;

/**
 * Operation-specific timeout tiers (in milliseconds)
 * مهلات مخصصة حسب نوع العملية
 */
export const TIMEOUT_TIERS = {
  /** Default API calls */
  default: 30000,
  /** File uploads (images, documents) */
  upload: 120000,
  /** AI analysis and recommendations */
  analysis: 180000,
  /** Report generation and exports */
  report: 60000,
  /** Health checks */
  healthCheck: 5000,
} as const;

/**
 * Maximum retry attempts for failed requests
 */
export const MAX_RETRY_ATTEMPTS = 3;

/**
 * Delay between retry attempts in milliseconds
 */
export const RETRY_DELAY = 1000;

/**
 * Default request headers
 */
export const DEFAULT_HEADERS: Readonly<Record<string, string>> = {
  "Content-Type": "application/json",
  Accept: "application/json",
  "Accept-Language": "ar,en",
} as const;

/**
 * API configuration constants grouped together
 */
export const API_CONFIG = {
  timeout: DEFAULT_TIMEOUT,
  timeoutTiers: TIMEOUT_TIERS,
  maxRetryAttempts: MAX_RETRY_ATTEMPTS,
  retryDelay: RETRY_DELAY,
  headers: DEFAULT_HEADERS,
} as const;

// ═══════════════════════════════════════════════════════════════════════════
// Type Definitions
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Service name type for type-safe service references
 * Note: Some names are deprecated but kept for backward compatibility:
 *   - "field-core" → use "field-management"
 *   - "satellite" → use "vegetation-analysis"
 *   - "crop-health" → use "crop-intelligence"
 */
export type ServiceName =
  // Core Services
  | "field-core" // @deprecated - use "field-management"
  | "field-management"
  | "auth"
  | "users"
  | "ws-gateway"
  // Satellite & Remote Sensing
  | "satellite" // @deprecated - use "vegetation-analysis"
  | "vegetation-analysis"
  | "ndvi-processor"
  // Weather
  | "weather"
  // AI & Analytics
  | "indicators"
  | "crop-health" // @deprecated - use "crop-intelligence"
  | "crop-intelligence"
  | "advisory"
  | "yield-prediction"
  | "field-intelligence"
  | "analytics"
  | "copilot"
  | "ai-advisor"
  | "ai-agents"
  | "knowledge-graph"
  // IoT & Sensors
  | "virtual-sensors"
  | "iot-gateway"
  | "iot-service"
  // Operations
  | "irrigation"
  | "task"
  | "equipment"
  | "inventory"
  | "logistics"
  | "supply-chain"
  // Communication
  | "notifications"
  | "field-chat" // @deprecated Use "chat-service" instead. Sunset: v17.0.0
  | "chat-service"
  | "community-chat" // @deprecated Use "chat-service" instead. Sunset: v17.0.0
  // Configuration & Misc
  | "provider-config"
  | "alerts"
  | "reports"
  | "astronomical-calendar"
  | "lowcode"
  // Billing & Audit
  | "billing"
  | "audit"
  // Agriculture Domain
  | "drone"
  | "soil-analysis"
  | "pest-detection"
  | "traceability"
  | "globalgap"
  | "cooperative"
  | "crm"
  // Community & Business
  | "marketplace"
  | "research"
  // Vision & Terrain
  | "yolo-vision"
  | "terrain-core"
  | "hydrology"
  | "leveling-optimizer"
  | "edge-orchestrator";

/**
 * API configuration interface for service-specific settings
 */
export interface ApiConfigOptions {
  baseUrl: string;
  timeout: number;
  retries: number;
  headers: Record<string, string>;
}

/**
 * Get API configuration with optional overrides
 *
 * @param overrides - Optional configuration overrides
 * @returns Complete API configuration
 */
export function getApiConfig(overrides?: Partial<ApiConfigOptions>): ApiConfigOptions {
  return {
    baseUrl: API_BASE_URL,
    timeout: DEFAULT_TIMEOUT,
    retries: MAX_RETRY_ATTEMPTS,
    headers: { ...DEFAULT_HEADERS },
    ...overrides,
  };
}

// ═══════════════════════════════════════════════════════════════════════════
// Default Export
// ═══════════════════════════════════════════════════════════════════════════

const apiConfig = {
  // Primary exports
  API_BASE_URL,
  API_BASE_HOST,
  SERVICE_PORTS,
  SERVICE_URLS,
  API_PATHS,
  API_URLS,
  API_CONFIG,
  DEFAULT_TIMEOUT,
  TIMEOUT_TIERS,
  MAX_RETRY_ATTEMPTS,
  RETRY_DELAY,
  DEFAULT_HEADERS,
  IS_PRODUCTION,
  IS_DEVELOPMENT,
  IS_TEST,
  getServiceUrl,
  getApiConfig,
  // Backward compatibility aliases
  API_URL,
  API_ENDPOINTS,
} as const;

export default apiConfig;
