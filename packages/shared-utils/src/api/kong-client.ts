/**
 * SAHOOL Kong Gateway Client
 * Unified API client for connecting to Kong API Gateway
 * عميل موحد للاتصال ببوابة Kong
 *
 * @module @sahool/shared-utils/api/kong-client
 */

// ═══════════════════════════════════════════════════════════════════════════
// Types
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Package tier for rate limiting and feature access
 */
export type PackageTier =
  | "trial"
  | "starter"
  | "professional"
  | "enterprise"
  | "research";

/**
 * Service definition for Kong gateway
 */
export interface KongService {
  name: string;
  port: number;
  basePath: string;
  healthPath: string;
  description: string;
  descriptionAr: string;
  tier: PackageTier[];
}

/**
 * Kong gateway configuration
 */
export interface KongConfig {
  baseUrl: string;
  apiVersion: "v1" | "v2";
  timeout: number;
  retryAttempts: number;
  retryDelay: number;
}

/**
 * Service health status
 */
export interface ServiceHealth {
  service: string;
  status: "healthy" | "degraded" | "unhealthy" | "unknown";
  latencyMs: number;
  lastChecked: string;
  details?: Record<string, unknown>;
}

/**
 * API response wrapper
 */
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    messageAr?: string;
    details?: Record<string, unknown>;
  };
  meta?: {
    requestId: string;
    timestamp: string;
    apiVersion: string;
  };
}

// ═══════════════════════════════════════════════════════════════════════════
// Service Registry (synced with Kong configuration)
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Complete service registry matching Kong gateway configuration
 */
export const KONG_SERVICES: Record<string, KongService> = {
  // Core Services - الخدمات الأساسية
  "field-management": {
    name: "field-management-service",
    port: 3000,
    basePath: "/api/v1/fields",
    healthPath: "/healthz",
    description: "Field management and boundaries",
    descriptionAr: "إدارة الحقول والحدود",
    tier: ["starter", "professional", "enterprise", "research"],
  },
  "user-service": {
    name: "user-service",
    port: 3025,
    basePath: "/api/v1/auth",
    healthPath: "/healthz",
    description: "Authentication and user management",
    descriptionAr: "المصادقة وإدارة المستخدمين",
    tier: ["trial", "starter", "professional", "enterprise", "research"],
  },

  // Satellite & Remote Sensing - الأقمار الصناعية
  "vegetation-analysis": {
    name: "vegetation-analysis-service",
    port: 8090,
    basePath: "/api/v1/vegetation",
    healthPath: "/healthz",
    description: "NDVI and satellite imagery analysis",
    descriptionAr: "تحليل NDVI وصور الأقمار الصناعية",
    tier: ["professional", "enterprise", "research"],
  },
  satellite: {
    name: "vegetation-analysis-service",
    port: 8090,
    basePath: "/api/v1/satellite",
    healthPath: "/healthz",
    description: "Satellite data processing",
    descriptionAr: "معالجة بيانات الأقمار الصناعية",
    tier: ["professional", "enterprise", "research"],
  },
  ndvi: {
    name: "vegetation-analysis-service",
    port: 8090,
    basePath: "/api/v1/ndvi",
    healthPath: "/healthz",
    description: "NDVI vegetation index",
    descriptionAr: "مؤشر الغطاء النباتي NDVI",
    tier: ["professional", "enterprise", "research"],
  },

  // Weather Services - خدمات الطقس
  weather: {
    name: "weather-service",
    port: 8092,
    basePath: "/api/v1/weather",
    healthPath: "/healthz",
    description: "Weather data and forecasts",
    descriptionAr: "بيانات الطقس والتنبؤات",
    tier: ["starter", "professional", "enterprise", "research"],
  },

  // AI & Analytics - الذكاء الاصطناعي والتحليلات
  "crop-intelligence": {
    name: "crop-intelligence-service",
    port: 8095,
    basePath: "/api/v1/crop-health",
    healthPath: "/healthz",
    description: "Crop health AI analysis",
    descriptionAr: "تحليل صحة المحاصيل بالذكاء الاصطناعي",
    tier: ["professional", "enterprise", "research"],
  },
  advisory: {
    name: "advisory-service",
    port: 8093,
    basePath: "/api/v1/advisory",
    healthPath: "/healthz",
    description: "Agricultural advisory recommendations",
    descriptionAr: "توصيات استشارية زراعية",
    tier: ["starter", "professional", "enterprise", "research"],
  },
  irrigation: {
    name: "irrigation-smart",
    port: 8094,
    basePath: "/api/v1/irrigation",
    healthPath: "/healthz",
    description: "Smart irrigation management",
    descriptionAr: "إدارة الري الذكي",
    tier: ["starter", "professional", "enterprise", "research"],
  },
  indicators: {
    name: "indicators-service",
    port: 8091,
    basePath: "/api/v1/indicators",
    healthPath: "/healthz",
    description: "Field health indicators",
    descriptionAr: "مؤشرات صحة الحقل",
    tier: ["professional", "enterprise", "research"],
  },

  // Operations - العمليات
  tasks: {
    name: "task-service",
    port: 8103,
    basePath: "/api/v1/tasks",
    healthPath: "/healthz",
    description: "Task management",
    descriptionAr: "إدارة المهام",
    tier: ["starter", "professional", "enterprise", "research"],
  },
  equipment: {
    name: "equipment-service",
    port: 8101,
    basePath: "/api/v1/equipment",
    healthPath: "/healthz",
    description: "Equipment tracking",
    descriptionAr: "تتبع المعدات",
    tier: ["professional", "enterprise"],
  },
  alerts: {
    name: "alert-service",
    port: 8113,
    basePath: "/api/v1/alerts",
    healthPath: "/healthz",
    description: "Alert management",
    descriptionAr: "إدارة التنبيهات",
    tier: ["starter", "professional", "enterprise", "research"],
  },

  // IoT - إنترنت الأشياء
  iot: {
    name: "iot-service",
    port: 8117,
    basePath: "/api/v1/iot",
    healthPath: "/healthz",
    description: "IoT device management",
    descriptionAr: "إدارة أجهزة إنترنت الأشياء",
    tier: ["enterprise"],
  },
  "virtual-sensors": {
    name: "virtual-sensors",
    port: 8119,
    basePath: "/api/v1/virtual-sensors",
    healthPath: "/healthz",
    description: "Virtual sensor calculations",
    descriptionAr: "حسابات المستشعرات الافتراضية",
    tier: ["professional", "enterprise", "research"],
  },

  // Communication - التواصل
  notifications: {
    name: "notification-service",
    port: 8110,
    basePath: "/api/v1/notifications",
    healthPath: "/healthz",
    description: "Push notifications",
    descriptionAr: "الإشعارات الفورية",
    tier: ["starter", "professional", "enterprise", "research"],
  },
  community: {
    name: "chat-service",
    port: 8115,
    basePath: "/api/v1/community",
    healthPath: "/healthz",
    description: "Community features",
    descriptionAr: "ميزات المجتمع",
    tier: ["starter", "professional", "enterprise"],
  },

  // Business - الأعمال
  marketplace: {
    name: "marketplace-service",
    port: 3010,
    basePath: "/api/v1/marketplace",
    healthPath: "/healthz",
    description: "Agricultural marketplace",
    descriptionAr: "سوق زراعي",
    tier: ["starter", "professional", "enterprise"],
  },
  billing: {
    name: "billing-core",
    port: 8089,
    basePath: "/api/v1/billing",
    healthPath: "/healthz",
    description: "Billing and invoicing",
    descriptionAr: "الفواتير والمحاسبة",
    tier: ["starter", "professional", "enterprise", "research"],
  },

  // Yield & Predictions - الإنتاج والتنبؤات
  yield: {
    name: "yield-prediction-service",
    port: 8152,
    basePath: "/api/v1/yield",
    healthPath: "/healthz",
    description: "Yield prediction",
    descriptionAr: "تنبؤ الإنتاج",
    tier: ["professional", "enterprise", "research"],
  },

  // Research - البحث
  research: {
    name: "research-core",
    port: 3015,
    basePath: "/api/v1/research",
    healthPath: "/healthz",
    description: "Research trials",
    descriptionAr: "التجارب البحثية",
    tier: ["research"],
  },

  // WebSocket - الاتصال المباشر
  websocket: {
    name: "ws-gateway",
    port: 8081,
    basePath: "/ws",
    healthPath: "/healthz",
    description: "Real-time WebSocket gateway",
    descriptionAr: "بوابة الاتصال المباشر",
    tier: ["starter", "professional", "enterprise", "research"],
  },
};

// ═══════════════════════════════════════════════════════════════════════════
// Default Configuration
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Default Kong gateway configuration
 */
export const DEFAULT_KONG_CONFIG: KongConfig = {
  baseUrl: "http://localhost:8000",
  apiVersion: "v1",
  timeout: 30000,
  retryAttempts: 3,
  retryDelay: 1000,
};

/**
 * Rate limits by package tier (requests per minute)
 */
export const RATE_LIMITS: Record<PackageTier, { minute: number; hour: number }> =
  {
    trial: { minute: 50, hour: 2000 },
    starter: { minute: 100, hour: 5000 },
    professional: { minute: 1000, hour: 50000 },
    enterprise: { minute: 10000, hour: 500000 },
    research: { minute: 10000, hour: 500000 },
  };

// ═══════════════════════════════════════════════════════════════════════════
// Helper Functions
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Build service URL through Kong gateway
 */
export function buildServiceUrl(
  config: KongConfig,
  serviceName: keyof typeof KONG_SERVICES,
  path: string = ""
): string {
  const service = KONG_SERVICES[serviceName];
  if (!service) {
    throw new Error(`Unknown service: ${serviceName}`);
  }

  const basePath = service.basePath.replace("/v1/", `/v${config.apiVersion}/`);
  const fullPath = path ? `${basePath}${path}` : basePath;

  return `${config.baseUrl}${fullPath}`;
}

/**
 * Get services available for a package tier
 */
export function getServicesForTier(
  tier: PackageTier
): Record<string, KongService> {
  return Object.fromEntries(
    Object.entries(KONG_SERVICES).filter(([_, service]) =>
      service.tier.includes(tier)
    )
  );
}

/**
 * Check if a service is available for a tier
 */
export function isServiceAvailable(
  serviceName: keyof typeof KONG_SERVICES,
  tier: PackageTier
): boolean {
  const service = KONG_SERVICES[serviceName];
  return service?.tier.includes(tier) ?? false;
}

/**
 * Get health check URL for a service
 */
export function getHealthCheckUrl(
  config: KongConfig,
  serviceName: keyof typeof KONG_SERVICES
): string {
  const service = KONG_SERVICES[serviceName];
  if (!service) {
    throw new Error(`Unknown service: ${serviceName}`);
  }

  return `${config.baseUrl}${service.basePath}${service.healthPath}`;
}

// ═══════════════════════════════════════════════════════════════════════════
// Exports
// ═══════════════════════════════════════════════════════════════════════════

export default {
  KONG_SERVICES,
  DEFAULT_KONG_CONFIG,
  RATE_LIMITS,
  buildServiceUrl,
  getServicesForTier,
  isServiceAvailable,
  getHealthCheckUrl,
};
