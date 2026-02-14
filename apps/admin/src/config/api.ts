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
// Service Ports
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Port mapping for all backend services
 */
export const SERVICE_PORTS = {
  // Core Services
  fieldCore: 3000, // @deprecated - use fieldManagement
  fieldManagement: 3000,
  auth: 8080,
  users: 3025,
  wsGateway: 8081,

  // Satellite & Remote Sensing
  satellite: 8090, // vegetation-analysis-service
  ndviProcessor: 8118,

  // Weather Services
  weather: 8092,

  // AI & Analytics
  indicators: 8091,
  cropIntelligence: 8095,
  advisory: 8093,
  yieldPrediction: 8152,
  analytics: 8100,
  copilot: 8088,
  aiAdvisor: 8112,
  knowledgeGraph: 8140,

  // IoT & Sensors
  virtualSensors: 8119,
  iotGateway: 8106,

  // Operations
  irrigation: 8094,
  task: 8103,
  equipment: 8101,
  inventory: 8116,
  logistics: 8167,
  supplyChain: 8230,

  // Communication
  notifications: 8110,
  fieldChat: 8099,
  chatService: 8000,

  // Configuration & Misc
  providerConfig: 8104,
  alerts: 8113,
  reports: 8084,

  // Billing & Audit
  billing: 8089,
  audit: 8114,

  // Agriculture Domain
  drone: 8126,
  soilAnalysis: 8124,
  pestDetection: 8125,
  traceability: 8123,
  globalgap: 8128,
  cooperative: 8127,
  crm: 8131,

  // Vision & Terrain
  yoloVision: 8150,
  terrainCore: 8185,
  hydrology: 8165,
  levelingOptimizer: 8170,
  edgeOrchestrator: 8180,
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
  analytics: getServiceUrl(SERVICE_PORTS.analytics),
  copilot: getServiceUrl(SERVICE_PORTS.copilot),
  aiAdvisor: getServiceUrl(SERVICE_PORTS.aiAdvisor),
  knowledgeGraph: getServiceUrl(SERVICE_PORTS.knowledgeGraph),

  // IoT & Sensors
  virtualSensors: getServiceUrl(SERVICE_PORTS.virtualSensors),
  iotGateway: getServiceUrl(SERVICE_PORTS.iotGateway),

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

  // Configuration & Misc
  providerConfig: getServiceUrl(SERVICE_PORTS.providerConfig),
  alerts: getServiceUrl(SERVICE_PORTS.alerts),
  reports: getServiceUrl(SERVICE_PORTS.reports),

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
  // Health Endpoints
  health: {
    live: "/healthz",
    ready: "/readyz",
    check: "/health",
    metrics: "/metrics",
  },

  // Authentication
  auth: {
    login: "/api/v1/auth/login",
    logout: "/api/v1/auth/logout",
    refresh: "/api/v1/auth/refresh",
    me: "/api/v1/auth/me",
    activity: "/api/v1/auth/activity",
  },

  // Fields & Farms
  fields: {
    list: "/api/v1/fields",
    byId: (id: string) => `/api/v1/fields/${id}`,
    create: "/api/v1/fields",
    update: (id: string) => `/api/v1/fields/${id}`,
    delete: (id: string) => `/api/v1/fields/${id}`,
  },

  // Crop Health & Diagnoses
  cropHealth: {
    diagnoses: "/api/v1/crop-health/diagnoses",
    diagnosisById: (id: string) => `/api/v1/crop-health/diagnoses/${id}`,
    stats: "/api/v1/crop-health/diagnoses/stats",
    analyze: "/api/v1/crop-health/analyze",
  },

  // Weather Services
  weather: {
    current: "/weather/current",
    forecast: "/weather/forecast",
    agricultural: "/weather/agricultural-report",
    alerts: (locationId: string) => `/v1/alerts/${locationId}`,
    locations: "/v1/locations",
    byLocation: (locationId: string) => `/v1/current/${locationId}`,
    forecastByLocation: (locationId: string) => `/v1/forecast/${locationId}`,
  },

  // Satellite & Vegetation
  satellite: {
    timeseries: (fieldId: string) => `/v1/timeseries/${fieldId}`,
    analyze: "/v1/analyze",
    indices: (fieldId: string) => `/v1/indices/${fieldId}`,
    satellites: "/v1/satellites",
  },

  // Dashboard & Indicators
  indicators: {
    dashboard: "/api/v1/indicators/dashboard",
    summary: "/api/v1/indicators/summary",
    trends: "/api/v1/indicators/trends",
  },

  // IoT & Sensors
  sensors: {
    readings: (farmId: string) => `/api/v1/iot/readings/${farmId}`,
    devices: "/api/v1/iot/devices",
    deviceById: (id: string) => `/api/v1/iot/devices/${id}`,
  },

  // Irrigation
  irrigation: {
    schedules: "/api/v1/irrigation/schedules",
    recommendations: "/api/v1/irrigation/recommendations",
    history: (fieldId: string) => `/api/v1/irrigation/history/${fieldId}`,
  },

  // Notifications
  notifications: {
    list: "/api/v1/notifications",
    byId: (id: string) => `/api/v1/notifications/${id}`,
    markRead: (id: string) => `/api/v1/notifications/${id}/read`,
    markAllRead: "/api/v1/notifications/read-all",
  },

  // Tasks
  tasks: {
    list: "/api/v1/tasks",
    byId: (id: string) => `/api/v1/tasks/${id}`,
    create: "/api/v1/tasks",
    update: (id: string) => `/api/v1/tasks/${id}`,
  },

  // Equipment
  equipment: {
    list: "/api/v1/equipment",
    byId: (id: string) => `/api/v1/equipment/${id}`,
    maintenance: (id: string) => `/api/v1/equipment/${id}/maintenance`,
  },

  // Community
  community: {
    posts: "/api/v1/posts",
    postById: (id: string) => `/api/v1/posts/${id}`,
    comments: (postId: string) => `/api/v1/posts/${postId}/comments`,
  },

  // Advisory (fertilizer + crop recommendations)
  advisory: {
    recommendations: "/api/v1/advisory/recommendations",
    fertilizer: "/api/v1/advisory/fertilizer",
    calculate: "/api/v1/advisory/fertilizer/calculate",
  },

  // Yield
  yield: {
    predictions: "/api/v1/yield/predictions",
    history: (fieldId: string) => `/api/v1/yield/history/${fieldId}`,
  },

  // Analytics
  analytics: {
    overview: "/api/v1/analytics/overview",
    reports: "/api/v1/analytics/reports",
    export: "/api/v1/analytics/export",
  },

  // Copilot (AI Assistant)
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

  // Billing
  billing: {
    invoices: "/api/v1/billing/invoices",
    invoiceById: (id: string) => `/api/v1/billing/invoices/${id}`,
    subscriptions: "/api/v1/billing/subscriptions",
    usage: "/api/v1/billing/usage",
  },

  // Audit
  audit: {
    logs: "/api/v1/audit/logs",
    logById: (id: string) => `/api/v1/audit/logs/${id}`,
    stats: "/api/v1/audit/stats",
  },

  // Inventory
  inventory: {
    items: "/api/v1/inventory",
    itemById: (id: string) => `/api/v1/inventory/${id}`,
    stockLevels: "/api/v1/inventory/stock-levels",
  },

  // Drone
  drone: {
    flights: "/api/v1/drone/flights",
    flightById: (id: string) => `/api/v1/drone/flights/${id}`,
    plan: "/api/v1/drone/flights/plan",
    devices: "/api/v1/drone/devices",
  },

  // Soil Analysis
  soilAnalysis: {
    tests: "/api/v1/soil/tests",
    testById: (id: string) => `/api/v1/soil/tests/${id}`,
    recommendations: "/api/v1/soil/recommendations",
  },

  // Traceability
  traceability: {
    batches: "/api/v1/traceability/batches",
    batchById: (id: string) => `/api/v1/traceability/batches/${id}`,
    events: "/api/v1/traceability/events",
    qrCode: (batchId: string) => `/api/v1/traceability/batches/${batchId}/qr`,
  },

  // Vision
  vision: {
    detectPest: "/api/v1/detect/pest",
    detectDisease: "/api/v1/detect/disease",
    detectWeed: "/api/v1/detect/weed",
    models: "/api/v1/models/versions",
  },

  // Terrain
  terrain: {
    analyze: "/api/v1/terrain/dem",
    slope: "/api/v1/terrain/slope",
    aspect: "/api/v1/terrain/aspect",
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
  virtualSensors: SERVICE_URLS.virtualSensors,
  equipment: SERVICE_URLS.equipment,
  task: SERVICE_URLS.task,
  providerConfig: SERVICE_URLS.providerConfig,
  notifications: SERVICE_URLS.notifications,
  wsGateway: SERVICE_URLS.wsGateway,
  copilot: SERVICE_URLS.copilot,
  billing: SERVICE_URLS.billing,
  audit: SERVICE_URLS.audit,
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
  | "analytics"
  | "copilot"
  | "ai-advisor"
  | "knowledge-graph"
  // IoT & Sensors
  | "virtual-sensors"
  | "iot-gateway"
  // Operations
  | "irrigation"
  | "task"
  | "equipment"
  | "inventory"
  | "logistics"
  | "supply-chain"
  // Communication
  | "notifications"
  | "field-chat"
  | "chat-service"
  // Configuration & Misc
  | "provider-config"
  | "alerts"
  | "reports"
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
