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
  fieldCore: 3000,
  fieldManagement: 3000,
  auth: 8080,
  users: 8081,
  wsGateway: 8081,

  // Satellite & Remote Sensing
  satellite: 8090,
  ndviEngine: 8107,

  // Weather Services
  weather: 8092,
  weatherCore: 8108,

  // AI & Analytics
  indicators: 8091,
  cropHealth: 8095,
  fertilizer: 8093,
  yieldEngine: 8098,
  analytics: 8100,

  // IoT & Sensors
  virtualSensors: 8119,

  // Operations
  irrigation: 8094,
  task: 8103,
  equipment: 8101,

  // Communication
  communityChat: 8097,
  community: 8097,
  notifications: 8110,

  // Configuration & Misc
  providerConfig: 8104,
  alerts: 8083,
  reports: 8084,
  lab: 8097,
  epidemic: 8098,
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
  fieldCore: getServiceUrl(SERVICE_PORTS.fieldCore),
  fieldManagement: getServiceUrl(SERVICE_PORTS.fieldManagement),
  auth: getServiceUrl(SERVICE_PORTS.auth),
  users: getServiceUrl(SERVICE_PORTS.users),
  wsGateway: getServiceUrl(SERVICE_PORTS.wsGateway),
  satellite: getServiceUrl(SERVICE_PORTS.satellite),
  ndviEngine: getServiceUrl(SERVICE_PORTS.ndviEngine),
  weather: getServiceUrl(SERVICE_PORTS.weather),
  weatherCore: getServiceUrl(SERVICE_PORTS.weatherCore),
  indicators: getServiceUrl(SERVICE_PORTS.indicators),
  cropHealth: getServiceUrl(SERVICE_PORTS.cropHealth),
  fertilizer: getServiceUrl(SERVICE_PORTS.fertilizer),
  yieldEngine: getServiceUrl(SERVICE_PORTS.yieldEngine),
  analytics: getServiceUrl(SERVICE_PORTS.analytics),
  virtualSensors: getServiceUrl(SERVICE_PORTS.virtualSensors),
  irrigation: getServiceUrl(SERVICE_PORTS.irrigation),
  task: getServiceUrl(SERVICE_PORTS.task),
  equipment: getServiceUrl(SERVICE_PORTS.equipment),
  communityChat: getServiceUrl(SERVICE_PORTS.communityChat),
  community: getServiceUrl(SERVICE_PORTS.community),
  notifications: getServiceUrl(SERVICE_PORTS.notifications),
  providerConfig: getServiceUrl(SERVICE_PORTS.providerConfig),
  alerts: getServiceUrl(SERVICE_PORTS.alerts),
  reports: getServiceUrl(SERVICE_PORTS.reports),
  lab: getServiceUrl(SERVICE_PORTS.lab),
  epidemic: getServiceUrl(SERVICE_PORTS.epidemic),
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

  // Fertilizer
  fertilizer: {
    recommendations: "/api/v1/fertilizer/recommendations",
    calculate: "/api/v1/fertilizer/calculate",
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
  // Service base URLs (for backward compatibility)
  fieldCore: SERVICE_URLS.fieldCore,
  satellite: SERVICE_URLS.satellite,
  indicators: SERVICE_URLS.indicators,
  weather: SERVICE_URLS.weather,
  weatherCore: SERVICE_URLS.weatherCore,
  fertilizer: SERVICE_URLS.fertilizer,
  irrigation: SERVICE_URLS.irrigation,
  cropHealth: SERVICE_URLS.cropHealth,
  virtualSensors: SERVICE_URLS.virtualSensors,
  communityChat: SERVICE_URLS.communityChat,
  yieldEngine: SERVICE_URLS.yieldEngine,
  equipment: SERVICE_URLS.equipment,
  community: SERVICE_URLS.community,
  task: SERVICE_URLS.task,
  providerConfig: SERVICE_URLS.providerConfig,
  notifications: SERVICE_URLS.notifications,
  wsGateway: SERVICE_URLS.wsGateway,

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
    list: `${SERVICE_URLS.fieldCore}${API_PATHS.fields.list}`,
    byId: (id: string) => `${SERVICE_URLS.fieldCore}${API_PATHS.fields.byId(id)}`,
    create: `${SERVICE_URLS.fieldCore}${API_PATHS.fields.create}`,
    update: (id: string) => `${SERVICE_URLS.fieldCore}${API_PATHS.fields.update(id)}`,
    delete: (id: string) => `${SERVICE_URLS.fieldCore}${API_PATHS.fields.delete(id)}`,
  },

  // Crop health endpoints
  diagnoses: {
    list: `${SERVICE_URLS.cropHealth}${API_PATHS.cropHealth.diagnoses}`,
    byId: (id: string) =>
      `${SERVICE_URLS.cropHealth}${API_PATHS.cropHealth.diagnosisById(id)}`,
    stats: `${SERVICE_URLS.cropHealth}${API_PATHS.cropHealth.stats}`,
    analyze: `${SERVICE_URLS.cropHealth}${API_PATHS.cropHealth.analyze}`,
  },

  // Weather endpoints
  weatherEndpoints: {
    current: `${SERVICE_URLS.weatherCore}${API_PATHS.weather.current}`,
    forecast: `${SERVICE_URLS.weatherCore}${API_PATHS.weather.forecast}`,
    agricultural: `${SERVICE_URLS.weatherCore}${API_PATHS.weather.agricultural}`,
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

  // Community endpoints
  communityEndpoints: {
    posts: `${SERVICE_URLS.communityChat}${API_PATHS.community.posts}`,
    postById: (id: string) =>
      `${SERVICE_URLS.communityChat}${API_PATHS.community.postById(id)}`,
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
 */
export type ServiceName =
  | "field-core"
  | "field-management"
  | "auth"
  | "users"
  | "ws-gateway"
  | "satellite"
  | "ndvi-engine"
  | "weather"
  | "weather-core"
  | "indicators"
  | "crop-health"
  | "fertilizer"
  | "yield-engine"
  | "analytics"
  | "virtual-sensors"
  | "irrigation"
  | "task"
  | "equipment"
  | "community-chat"
  | "community"
  | "notifications"
  | "provider-config"
  | "alerts"
  | "reports"
  | "lab"
  | "epidemic";

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
