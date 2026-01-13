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

export type ServiceName =
  | "field-core"
  | "satellite"
  | "weather"
  | "crop-health"
  | "virtual-sensors"
  | "notifications"
  | "irrigation"
  | "analytics"
  | "auth"
  | "users"
  | "tasks"
  | "alerts"
  | "reports"
  | "ai-advisor"
  | "lab"
  | "epidemic";

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
  "field-core": {
    name: "field-core",
    baseUrl: `${API_BASE}:3000`,
    port: 3000,
    healthEndpoint: "/health",
    timeout: 10000,
    retries: 3,
  },
  satellite: {
    name: "satellite",
    baseUrl: `${API_BASE}:8090`,
    port: 8090,
    healthEndpoint: "/api/health",
    timeout: 30000,
    retries: 2,
  },
  weather: {
    name: "weather",
    baseUrl: `${API_BASE}:8092`,
    port: 8092,
    healthEndpoint: "/api/health",
    timeout: 15000,
    retries: 3,
  },
  "crop-health": {
    name: "crop-health",
    baseUrl: `${API_BASE}:8095`,
    port: 8095,
    healthEndpoint: "/api/health",
    timeout: 20000,
    retries: 2,
  },
  "virtual-sensors": {
    name: "virtual-sensors",
    baseUrl: `${API_BASE}:8096`,
    port: 8096,
    healthEndpoint: "/api/health",
    timeout: 10000,
    retries: 3,
  },
  notifications: {
    name: "notifications",
    baseUrl: `${API_BASE}:8110`,
    port: 8110,
    healthEndpoint: "/api/health",
    timeout: 5000,
    retries: 2,
  },
  irrigation: {
    name: "irrigation",
    baseUrl: `${API_BASE}:8093`,
    port: 8093,
    healthEndpoint: "/api/health",
    timeout: 10000,
    retries: 3,
  },
  analytics: {
    name: "analytics",
    baseUrl: `${API_BASE}:8100`,
    port: 8100,
    healthEndpoint: "/api/health",
    timeout: 30000,
    retries: 2,
  },
  auth: {
    name: "auth",
    baseUrl: `${API_BASE}:8080`,
    port: 8080,
    healthEndpoint: "/health",
    timeout: 5000,
    retries: 2,
  },
  users: {
    name: "users",
    baseUrl: `${API_BASE}:8081`,
    port: 8081,
    healthEndpoint: "/health",
    timeout: 10000,
    retries: 3,
  },
  tasks: {
    name: "tasks",
    baseUrl: `${API_BASE}:8082`,
    port: 8082,
    healthEndpoint: "/health",
    timeout: 10000,
    retries: 3,
  },
  alerts: {
    name: "alerts",
    baseUrl: `${API_BASE}:8083`,
    port: 8083,
    healthEndpoint: "/health",
    timeout: 5000,
    retries: 2,
  },
  reports: {
    name: "reports",
    baseUrl: `${API_BASE}:8084`,
    port: 8084,
    healthEndpoint: "/health",
    timeout: 30000,
    retries: 2,
  },
  "ai-advisor": {
    name: "ai-advisor",
    baseUrl: `${API_BASE}:8091`,
    port: 8091,
    healthEndpoint: "/api/health",
    timeout: 30000,
    retries: 2,
  },
  lab: {
    name: "lab",
    baseUrl: `${API_BASE}:8097`,
    port: 8097,
    healthEndpoint: "/api/health",
    timeout: 15000,
    retries: 2,
  },
  epidemic: {
    name: "epidemic",
    baseUrl: `${API_BASE}:8098`,
    port: 8098,
    healthEndpoint: "/api/health",
    timeout: 15000,
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
  return match ? decodeURIComponent(match[1]) : null;
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
