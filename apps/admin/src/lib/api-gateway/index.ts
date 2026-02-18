/**
 * SAHOOL Admin API Gateway
 * بوابة API للوحة الإدارة
 *
 * Features:
 * - Centralized service discovery
 * - Circuit breaker pattern
 * - Health checks
 * - Request retry with backoff
 * - Error standardization
 */

import axios, { AxiosError, AxiosInstance, AxiosRequestConfig } from "axios";
import { logger } from "../logger";

// ═══════════════════════════════════════════════════════════════════════════
// Types
// ═══════════════════════════════════════════════════════════════════════════

// NOTE: Some service names are deprecated and mapped to new names:
//   - field-core → field-management (both supported for backward compatibility)
//   - satellite → vegetation-analysis (actual service name)
//   - weather-advanced → weather (consolidated)
export type ServiceName =
  // Core Services
  | "field-core" // @deprecated use "field-management"
  | "field-management"
  | "auth"
  | "users"
  // Satellite & Remote Sensing
  | "satellite" // @deprecated use "vegetation-analysis"
  | "vegetation-analysis"
  | "ndvi-processor"
  // Weather
  | "weather"
  // AI & Analytics
  | "crop-health" // @deprecated use "crop-intelligence"
  | "crop-intelligence"
  | "indicators"
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
  | "tasks"
  | "equipment"
  | "inventory"
  | "logistics"
  // Communication
  | "notifications"
  | "field-chat"
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
  | "crm"
  // Supply Chain & Cooperative
  | "supply-chain"
  | "cooperative"
  // Vision & Terrain
  | "yolo-vision"
  | "terrain-core"
  | "hydrology"
  | "leveling-optimizer"
  | "edge-orchestrator";

export interface ServiceConfig {
  name: ServiceName;
  baseUrl: string;
  port: number;
  healthEndpoint?: string;
  timeout?: number;
  retries?: number;
}

export interface ServiceHealth {
  name: ServiceName;
  status: "healthy" | "degraded" | "unhealthy" | "unknown";
  latency?: number;
  lastCheck: Date;
  error?: string;
}

export interface CircuitBreakerState {
  failures: number;
  lastFailure: Date | null;
  state: "closed" | "open" | "half-open";
  nextRetry: Date | null;
}

export interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: unknown;
  };
  meta?: {
    service: ServiceName;
    latency: number;
    cached: boolean;
  };
}

// ═══════════════════════════════════════════════════════════════════════════
// Configuration
// ═══════════════════════════════════════════════════════════════════════════

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost";

const SERVICES: Record<ServiceName, ServiceConfig> = {
  // ═══════════════════════════════════════════════════════════════════════════
  // Core Services
  // ═══════════════════════════════════════════════════════════════════════════
  "field-core": {
    name: "field-core",
    baseUrl: `${API_BASE}:3000`,
    port: 3000,
    healthEndpoint: "/health",
    timeout: 10000,
    retries: 3,
  },
  "field-management": {
    name: "field-management",
    baseUrl: `${API_BASE}:3000`,
    port: 3000,
    healthEndpoint: "/health",
    timeout: 10000,
    retries: 3,
  },
  auth: {
    name: "auth",
    baseUrl: `${API_BASE}:3025`,
    port: 3025,
    healthEndpoint: "/health",
    timeout: 5000,
    retries: 2,
  },
  users: {
    name: "users",
    baseUrl: `${API_BASE}:3025`,
    port: 3025,
    healthEndpoint: "/api/v1/health",
    timeout: 10000,
    retries: 3,
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // Satellite & Remote Sensing
  // ═══════════════════════════════════════════════════════════════════════════
  satellite: {
    name: "satellite",
    baseUrl: `${API_BASE}:8090`,
    port: 8090,
    healthEndpoint: "/healthz",
    timeout: 30000,
    retries: 2,
  },
  "vegetation-analysis": {
    name: "vegetation-analysis",
    baseUrl: `${API_BASE}:8090`,
    port: 8090,
    healthEndpoint: "/healthz",
    timeout: 30000,
    retries: 2,
  },
  "ndvi-processor": {
    name: "ndvi-processor",
    baseUrl: `${API_BASE}:8118`,
    port: 8118,
    healthEndpoint: "/healthz",
    timeout: 30000,
    retries: 2,
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // Weather
  // ═══════════════════════════════════════════════════════════════════════════
  weather: {
    name: "weather",
    baseUrl: `${API_BASE}:8092`,
    port: 8092,
    healthEndpoint: "/healthz",
    timeout: 15000,
    retries: 3,
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // AI & Analytics
  // ═══════════════════════════════════════════════════════════════════════════
  "crop-health": {
    name: "crop-health",
    baseUrl: `${API_BASE}:8095`,
    port: 8095,
    healthEndpoint: "/healthz",
    timeout: 20000,
    retries: 2,
  },
  "crop-intelligence": {
    name: "crop-intelligence",
    baseUrl: `${API_BASE}:8095`,
    port: 8095,
    healthEndpoint: "/healthz",
    timeout: 20000,
    retries: 2,
  },
  indicators: {
    name: "indicators",
    baseUrl: `${API_BASE}:8091`,
    port: 8091,
    healthEndpoint: "/healthz",
    timeout: 15000,
    retries: 2,
  },
  advisory: {
    name: "advisory",
    baseUrl: `${API_BASE}:8093`,
    port: 8093,
    healthEndpoint: "/healthz",
    timeout: 20000,
    retries: 2,
  },
  "yield-prediction": {
    name: "yield-prediction",
    baseUrl: `${API_BASE}:8152`,
    port: 8152,
    healthEndpoint: "/healthz",
    timeout: 30000,
    retries: 2,
  },
  analytics: {
    name: "analytics",
    baseUrl: `${API_BASE}:8100`,
    port: 8100,
    healthEndpoint: "/healthz",
    timeout: 30000,
    retries: 2,
  },
  copilot: {
    name: "copilot",
    baseUrl: `${API_BASE}:8088`,
    port: 8088,
    healthEndpoint: "/healthz",
    timeout: 60000,
    retries: 1,
  },
  "ai-advisor": {
    name: "ai-advisor",
    baseUrl: `${API_BASE}:8112`,
    port: 8112,
    healthEndpoint: "/healthz",
    timeout: 30000,
    retries: 2,
  },
  "knowledge-graph": {
    name: "knowledge-graph",
    baseUrl: `${API_BASE}:8140`,
    port: 8140,
    healthEndpoint: "/healthz",
    timeout: 20000,
    retries: 2,
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // IoT & Sensors
  // ═══════════════════════════════════════════════════════════════════════════
  "virtual-sensors": {
    name: "virtual-sensors",
    baseUrl: `${API_BASE}:8119`,
    port: 8119,
    healthEndpoint: "/healthz",
    timeout: 10000,
    retries: 3,
  },
  "iot-gateway": {
    name: "iot-gateway",
    baseUrl: `${API_BASE}:8106`,
    port: 8106,
    healthEndpoint: "/healthz",
    timeout: 10000,
    retries: 2,
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // Operations
  // ═══════════════════════════════════════════════════════════════════════════
  irrigation: {
    name: "irrigation",
    baseUrl: `${API_BASE}:8094`,
    port: 8094,
    healthEndpoint: "/healthz",
    timeout: 10000,
    retries: 3,
  },
  tasks: {
    name: "tasks",
    baseUrl: `${API_BASE}:8103`,
    port: 8103,
    healthEndpoint: "/healthz",
    timeout: 10000,
    retries: 3,
  },
  equipment: {
    name: "equipment",
    baseUrl: `${API_BASE}:8101`,
    port: 8101,
    healthEndpoint: "/healthz",
    timeout: 10000,
    retries: 3,
  },
  inventory: {
    name: "inventory",
    baseUrl: `${API_BASE}:8116`,
    port: 8116,
    healthEndpoint: "/healthz",
    timeout: 10000,
    retries: 3,
  },
  logistics: {
    name: "logistics",
    baseUrl: `${API_BASE}:8167`,
    port: 8167,
    healthEndpoint: "/healthz",
    timeout: 15000,
    retries: 2,
  },
  "supply-chain": {
    name: "supply-chain",
    baseUrl: `${API_BASE}:8230`,
    port: 8230,
    healthEndpoint: "/healthz",
    timeout: 15000,
    retries: 2,
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // Communication
  // ═══════════════════════════════════════════════════════════════════════════
  notifications: {
    name: "notifications",
    baseUrl: `${API_BASE}:8110`,
    port: 8110,
    healthEndpoint: "/healthz",
    timeout: 5000,
    retries: 2,
  },
  "field-chat": {
    name: "field-chat",
    baseUrl: `${API_BASE}:8099`,
    port: 8099,
    healthEndpoint: "/healthz",
    timeout: 10000,
    retries: 2,
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // Configuration & Misc
  // ═══════════════════════════════════════════════════════════════════════════
  "provider-config": {
    name: "provider-config",
    baseUrl: `${API_BASE}:8104`,
    port: 8104,
    healthEndpoint: "/healthz",
    timeout: 10000,
    retries: 2,
  },
  alerts: {
    name: "alerts",
    baseUrl: `${API_BASE}:8113`,
    port: 8113,
    healthEndpoint: "/healthz",
    timeout: 5000,
    retries: 2,
  },
  reports: {
    name: "reports",
    baseUrl: `${API_BASE}:8084`,
    port: 8084,
    healthEndpoint: "/healthz",
    timeout: 30000,
    retries: 2,
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // Billing & Audit
  // ═══════════════════════════════════════════════════════════════════════════
  billing: {
    name: "billing",
    baseUrl: `${API_BASE}:8089`,
    port: 8089,
    healthEndpoint: "/healthz",
    timeout: 15000,
    retries: 2,
  },
  audit: {
    name: "audit",
    baseUrl: `${API_BASE}:8114`,
    port: 8114,
    healthEndpoint: "/healthz",
    timeout: 10000,
    retries: 2,
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // Agriculture Domain
  // ═══════════════════════════════════════════════════════════════════════════
  drone: {
    name: "drone",
    baseUrl: `${API_BASE}:8126`,
    port: 8126,
    healthEndpoint: "/healthz",
    timeout: 20000,
    retries: 2,
  },
  "soil-analysis": {
    name: "soil-analysis",
    baseUrl: `${API_BASE}:8124`,
    port: 8124,
    healthEndpoint: "/healthz",
    timeout: 15000,
    retries: 2,
  },
  "pest-detection": {
    name: "pest-detection",
    baseUrl: `${API_BASE}:8125`,
    port: 8125,
    healthEndpoint: "/healthz",
    timeout: 20000,
    retries: 2,
  },
  traceability: {
    name: "traceability",
    baseUrl: `${API_BASE}:8123`,
    port: 8123,
    healthEndpoint: "/healthz",
    timeout: 15000,
    retries: 2,
  },
  globalgap: {
    name: "globalgap",
    baseUrl: `${API_BASE}:8128`,
    port: 8128,
    healthEndpoint: "/healthz",
    timeout: 15000,
    retries: 2,
  },
  crm: {
    name: "crm",
    baseUrl: `${API_BASE}:8131`,
    port: 8131,
    healthEndpoint: "/healthz",
    timeout: 10000,
    retries: 2,
  },
  cooperative: {
    name: "cooperative",
    baseUrl: `${API_BASE}:8127`,
    port: 8127,
    healthEndpoint: "/healthz",
    timeout: 15000,
    retries: 2,
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // Vision & Terrain
  // ═══════════════════════════════════════════════════════════════════════════
  "yolo-vision": {
    name: "yolo-vision",
    baseUrl: `${API_BASE}:8150`,
    port: 8150,
    healthEndpoint: "/healthz",
    timeout: 60000,
    retries: 1,
  },
  "terrain-core": {
    name: "terrain-core",
    baseUrl: `${API_BASE}:8185`,
    port: 8185,
    healthEndpoint: "/healthz",
    timeout: 30000,
    retries: 2,
  },
  hydrology: {
    name: "hydrology",
    baseUrl: `${API_BASE}:8165`,
    port: 8165,
    healthEndpoint: "/healthz",
    timeout: 30000,
    retries: 2,
  },
  "leveling-optimizer": {
    name: "leveling-optimizer",
    baseUrl: `${API_BASE}:8170`,
    port: 8170,
    healthEndpoint: "/healthz",
    timeout: 30000,
    retries: 2,
  },
  "edge-orchestrator": {
    name: "edge-orchestrator",
    baseUrl: `${API_BASE}:8180`,
    port: 8180,
    healthEndpoint: "/healthz",
    timeout: 20000,
    retries: 2,
  },
};

// ═══════════════════════════════════════════════════════════════════════════
// Circuit Breaker
// ═══════════════════════════════════════════════════════════════════════════

const CIRCUIT_BREAKER_THRESHOLD = 5;
const CIRCUIT_BREAKER_TIMEOUT = 30000; // 30 seconds

const circuitBreakers = new Map<ServiceName, CircuitBreakerState>();

function getCircuitBreaker(service: ServiceName): CircuitBreakerState {
  if (!circuitBreakers.has(service)) {
    circuitBreakers.set(service, {
      failures: 0,
      lastFailure: null,
      state: "closed",
      nextRetry: null,
    });
  }
  return circuitBreakers.get(service)!;
}

function recordFailure(service: ServiceName): void {
  const breaker = getCircuitBreaker(service);
  breaker.failures++;
  breaker.lastFailure = new Date();

  if (breaker.failures >= CIRCUIT_BREAKER_THRESHOLD) {
    breaker.state = "open";
    breaker.nextRetry = new Date(Date.now() + CIRCUIT_BREAKER_TIMEOUT);
    logger.warn(`🔴 Circuit breaker OPEN for ${service}`);
  }
}

function recordSuccess(service: ServiceName): void {
  const breaker = getCircuitBreaker(service);
  breaker.failures = 0;
  breaker.state = "closed";
  breaker.nextRetry = null;
}

function canRequest(service: ServiceName): boolean {
  const breaker = getCircuitBreaker(service);

  if (breaker.state === "closed") return true;

  if (breaker.state === "open" && breaker.nextRetry) {
    if (new Date() >= breaker.nextRetry) {
      breaker.state = "half-open";
      logger.log(`🟡 Circuit breaker HALF-OPEN for ${service}`);
      return true;
    }
    return false;
  }

  return breaker.state === "half-open";
}

// ═══════════════════════════════════════════════════════════════════════════
// Service Clients
// ═══════════════════════════════════════════════════════════════════════════

const serviceClients = new Map<ServiceName, AxiosInstance>();

function getServiceClient(service: ServiceName): AxiosInstance {
  if (!serviceClients.has(service)) {
    const config = SERVICES[service];

    const client = axios.create({
      baseURL: config.baseUrl,
      timeout: config.timeout || 10000,
      headers: {
        "Content-Type": "application/json",
      },
    });

    // Request interceptor - add auth token
    client.interceptors.request.use((reqConfig) => {
      const token = getAuthToken();
      if (token) {
        reqConfig.headers.Authorization = `Bearer ${token}`;
      }
      return reqConfig;
    });

    // Response interceptor - handle errors
    client.interceptors.response.use(
      (response) => {
        recordSuccess(service);
        return response;
      },
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          handleAuthError();
        }
        recordFailure(service);
        throw error;
      },
    );

    serviceClients.set(service, client);
  }

  return serviceClients.get(service)!;
}

// ═══════════════════════════════════════════════════════════════════════════
// Auth Helpers
// ═══════════════════════════════════════════════════════════════════════════

function getAuthToken(): string | null {
  if (typeof document === "undefined") return null;
  const match = document.cookie.match(/(?:^|; )sahool_admin_token=([^;]*)/);
  return match && match[1] ? decodeURIComponent(match[1]) : null;
}

function handleAuthError(): void {
  if (typeof window !== "undefined") {
    window.location.href = "/login";
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// API Gateway Methods
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Make a request through the API Gateway
 * إرسال طلب عبر بوابة API
 */
export async function request<T>(
  service: ServiceName,
  endpoint: string,
  options: AxiosRequestConfig = {},
): Promise<ApiResponse<T>> {
  const startTime = Date.now();

  // Check circuit breaker
  if (!canRequest(service)) {
    return {
      success: false,
      error: {
        code: "CIRCUIT_OPEN",
        message: `Service ${service} is temporarily unavailable`,
      },
      meta: {
        service,
        latency: 0,
        cached: false,
      },
    };
  }

  const config = SERVICES[service];
  const client = getServiceClient(service);
  const retries = options.method === "GET" ? config.retries || 3 : 1;

  let lastError: Error | null = null;

  for (let attempt = 0; attempt < retries; attempt++) {
    try {
      const response = await client.request<T>({
        url: endpoint,
        ...options,
      });

      return {
        success: true,
        data: response.data,
        meta: {
          service,
          latency: Date.now() - startTime,
          cached: false,
        },
      };
    } catch (error) {
      lastError = error as Error;

      // Don't retry on client errors (4xx)
      if (
        axios.isAxiosError(error) &&
        error.response?.status &&
        error.response.status < 500
      ) {
        break;
      }

      // Wait before retry with exponential backoff
      if (attempt < retries - 1) {
        await sleep(Math.pow(2, attempt) * 1000);
      }
    }
  }

  const axiosError = lastError as AxiosError;

  return {
    success: false,
    error: {
      code: axiosError.code || "REQUEST_FAILED",
      message: axiosError.message,
      details: axiosError.response?.data,
    },
    meta: {
      service,
      latency: Date.now() - startTime,
      cached: false,
    },
  };
}

/**
 * GET request
 */
export function get<T>(
  service: ServiceName,
  endpoint: string,
  params?: Record<string, unknown>,
): Promise<ApiResponse<T>> {
  return request<T>(service, endpoint, { method: "GET", params });
}

/**
 * POST request
 */
export function post<T>(
  service: ServiceName,
  endpoint: string,
  data?: unknown,
): Promise<ApiResponse<T>> {
  return request<T>(service, endpoint, { method: "POST", data });
}

/**
 * PUT request
 */
export function put<T>(
  service: ServiceName,
  endpoint: string,
  data?: unknown,
): Promise<ApiResponse<T>> {
  return request<T>(service, endpoint, { method: "PUT", data });
}

/**
 * DELETE request
 */
export function del<T>(
  service: ServiceName,
  endpoint: string,
): Promise<ApiResponse<T>> {
  return request<T>(service, endpoint, { method: "DELETE" });
}

// ═══════════════════════════════════════════════════════════════════════════
// Health Checks
// ═══════════════════════════════════════════════════════════════════════════

const healthCache = new Map<ServiceName, ServiceHealth>();

/**
 * Check health of a service
 * فحص صحة خدمة
 */
export async function checkServiceHealth(
  service: ServiceName,
): Promise<ServiceHealth> {
  const config = SERVICES[service];
  const startTime = Date.now();

  try {
    await axios.get(`${config.baseUrl}${config.healthEndpoint || "/health"}`, {
      timeout: 5000,
    });

    const health: ServiceHealth = {
      name: service,
      status: "healthy",
      latency: Date.now() - startTime,
      lastCheck: new Date(),
    };

    healthCache.set(service, health);
    return health;
  } catch (error) {
    const health: ServiceHealth = {
      name: service,
      status: "unhealthy",
      latency: Date.now() - startTime,
      lastCheck: new Date(),
      error: (error as Error).message,
    };

    healthCache.set(service, health);
    return health;
  }
}

/**
 * Check health of all services
 * فحص صحة جميع الخدمات
 */
export async function checkAllServicesHealth(): Promise<ServiceHealth[]> {
  const services = Object.keys(SERVICES) as ServiceName[];
  const results = await Promise.all(services.map(checkServiceHealth));
  return results;
}

/**
 * Get cached health status
 * الحصول على حالة الصحة المخزنة
 */
export function getCachedHealth(service: ServiceName): ServiceHealth | null {
  return healthCache.get(service) || null;
}

// ═══════════════════════════════════════════════════════════════════════════
// Utilities
// ═══════════════════════════════════════════════════════════════════════════

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Get service configuration
 */
export function getServiceConfig(service: ServiceName): ServiceConfig {
  return SERVICES[service];
}

/**
 * Get all services
 */
export function getAllServices(): ServiceName[] {
  return Object.keys(SERVICES) as ServiceName[];
}

/**
 * Get circuit breaker status
 */
export function getCircuitBreakerStatus(): Map<
  ServiceName,
  CircuitBreakerState
> {
  return new Map(circuitBreakers);
}

// ═══════════════════════════════════════════════════════════════════════════
// Export
// ═══════════════════════════════════════════════════════════════════════════

export const ApiGateway = {
  request,
  get,
  post,
  put,
  delete: del,
  checkServiceHealth,
  checkAllServicesHealth,
  getCachedHealth,
  getServiceConfig,
  getAllServices,
  getCircuitBreakerStatus,
};

export default ApiGateway;
