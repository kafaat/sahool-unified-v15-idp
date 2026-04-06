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

import axios, { AxiosError, AxiosInstance, AxiosRequestConfig } from 'axios';
import { SERVICE_PORTS } from '@sahool/shared-types/contracts';
import { logger } from '../logger';

// ═══════════════════════════════════════════════════════════════════════════
// Types
// ═══════════════════════════════════════════════════════════════════════════

// NOTE: Some service names are deprecated and mapped to new names:
//   - field-core → field-management (both supported for backward compatibility)
//   - satellite → vegetation-analysis (actual service name)
//   - weather-advanced → weather (consolidated)
export type ServiceName =
  // Core Services
  | 'field-core' // @deprecated use "field-management"
  | 'field-management'
  | 'auth'
  | 'users'
  // Satellite & Remote Sensing
  | 'satellite' // @deprecated use "vegetation-analysis"
  | 'vegetation-analysis'
  | 'ndvi-processor'
  // Weather
  | 'weather'
  // AI & Analytics
  | 'crop-health' // @deprecated use "crop-intelligence"
  | 'crop-intelligence'
  | 'indicators'
  | 'advisory'
  | 'yield-prediction'
  | 'analytics'
  | 'copilot'
  | 'ai-advisor'
  | 'knowledge-graph'
  // IoT & Sensors
  | 'virtual-sensors'
  | 'iot-gateway'
  // Operations
  | 'irrigation'
  | 'tasks'
  | 'equipment'
  | 'inventory'
  | 'logistics'
  // Communication
  | 'notifications'
  | 'chat-service'
  // Configuration & Misc
  | 'provider-config'
  | 'alerts'
  | 'reports'
  // Billing & Audit
  | 'billing'
  | 'audit'
  // Agriculture Domain
  | 'drone'
  | 'soil-analysis'
  | 'pest-detection'
  | 'traceability'
  | 'globalgap'
  | 'crm'
  // Supply Chain & Cooperative
  | 'supply-chain'
  | 'cooperative'
  // Vision & Terrain
  | 'yolo-vision'
  | 'terrain-core'
  | 'hydrology'
  | 'leveling-optimizer'
  | 'edge-orchestrator';

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
  status: 'healthy' | 'degraded' | 'unhealthy' | 'unknown';
  latency?: number;
  lastCheck: Date;
  error?: string;
}

export interface CircuitBreakerState {
  failures: number;
  lastFailure: Date | null;
  state: 'closed' | 'open' | 'half-open';
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

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost';

const SERVICES: Record<ServiceName, ServiceConfig> = {
  // ═══════════════════════════════════════════════════════════════════════════
  // Core Services
  // ═══════════════════════════════════════════════════════════════════════════
  'field-core': {
    name: 'field-core',
    baseUrl: `${API_BASE}:${SERVICE_PORTS.FIELD_MANAGEMENT}`,
    port: SERVICE_PORTS.FIELD_MANAGEMENT,
    healthEndpoint: '/health',
    timeout: 10000,
    retries: 3,
  },
  'field-management': {
    name: 'field-management',
    baseUrl: `${API_BASE}:${SERVICE_PORTS.FIELD_MANAGEMENT}`,
    port: SERVICE_PORTS.FIELD_MANAGEMENT,
    healthEndpoint: '/health',
    timeout: 10000,
    retries: 3,
  },
  auth: {
    name: 'auth',
    baseUrl: `${API_BASE}:${SERVICE_PORTS.USER_SERVICE}`,
    port: SERVICE_PORTS.USER_SERVICE,
    healthEndpoint: '/api/v1/health',
    timeout: 5000,
    retries: 2,
  },
  users: {
    name: 'users',
    baseUrl: `${API_BASE}:${SERVICE_PORTS.USER_SERVICE}`,
    port: SERVICE_PORTS.USER_SERVICE,
    healthEndpoint: '/api/v1/health',
    timeout: 10000,
    retries: 3,
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // Satellite & Remote Sensing
  // ═══════════════════════════════════════════════════════════════════════════
  satellite: {
    name: 'satellite',
    baseUrl: `${API_BASE}:${SERVICE_PORTS.VEGETATION_ANALYSIS}`,
    port: SERVICE_PORTS.VEGETATION_ANALYSIS,
    healthEndpoint: '/healthz',
    timeout: 30000,
    retries: 2,
  },
  'vegetation-analysis': {
    name: 'vegetation-analysis',
    baseUrl: `${API_BASE}:${SERVICE_PORTS.VEGETATION_ANALYSIS}`,
    port: SERVICE_PORTS.VEGETATION_ANALYSIS,
    healthEndpoint: '/healthz',
    timeout: 30000,
    retries: 2,
  },
  'ndvi-processor': {
    name: 'ndvi-processor',
    baseUrl: `${API_BASE}:${SERVICE_PORTS.NDVI_PROCESSOR}`,
    port: SERVICE_PORTS.NDVI_PROCESSOR,
    healthEndpoint: '/healthz',
    timeout: 30000,
    retries: 2,
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // Weather
  // ═══════════════════════════════════════════════════════════════════════════
  weather: {
    name: 'weather',
    baseUrl: `${API_BASE}:${SERVICE_PORTS.WEATHER}`,
    port: SERVICE_PORTS.WEATHER,
    healthEndpoint: '/healthz',
    timeout: 15000,
    retries: 3,
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // AI & Analytics
  // ═══════════════════════════════════════════════════════════════════════════
  'crop-health': {
    name: 'crop-health',
    baseUrl: `${API_BASE}:${SERVICE_PORTS.CROP_INTELLIGENCE}`,
    port: SERVICE_PORTS.CROP_INTELLIGENCE,
    healthEndpoint: '/healthz',
    timeout: 20000,
    retries: 2,
  },
  'crop-intelligence': {
    name: 'crop-intelligence',
    baseUrl: `${API_BASE}:${SERVICE_PORTS.CROP_INTELLIGENCE}`,
    port: SERVICE_PORTS.CROP_INTELLIGENCE,
    healthEndpoint: '/healthz',
    timeout: 20000,
    retries: 2,
  },
  indicators: {
    name: 'indicators',
    baseUrl: `${API_BASE}:${SERVICE_PORTS.INDICATORS}`,
    port: SERVICE_PORTS.INDICATORS,
    healthEndpoint: '/healthz',
    timeout: 15000,
    retries: 2,
  },
  advisory: {
    name: 'advisory',
    baseUrl: `${API_BASE}:${SERVICE_PORTS.ADVISORY}`,
    port: SERVICE_PORTS.ADVISORY,
    healthEndpoint: '/healthz',
    timeout: 20000,
    retries: 2,
  },
  'yield-prediction': {
    name: 'yield-prediction',
    baseUrl: `${API_BASE}:${SERVICE_PORTS.YIELD_PREDICTION}`,
    port: SERVICE_PORTS.YIELD_PREDICTION,
    healthEndpoint: '/healthz',
    timeout: 30000,
    retries: 2,
  },
  analytics: {
    name: 'analytics',
    // Routes through indicators-service (port 8091) via Kong gateway
    baseUrl: `${API_BASE}:${SERVICE_PORTS.INDICATORS}`,
    port: SERVICE_PORTS.INDICATORS,
    healthEndpoint: '/healthz',
    timeout: 30000,
    retries: 2,
  },
  copilot: {
    name: 'copilot',
    baseUrl: `${API_BASE}:${SERVICE_PORTS.COPILOT_API}`,
    port: SERVICE_PORTS.COPILOT_API,
    healthEndpoint: '/healthz',
    timeout: 60000,
    retries: 1,
  },
  'ai-advisor': {
    name: 'ai-advisor',
    baseUrl: `${API_BASE}:${SERVICE_PORTS.AI_ADVISOR}`,
    port: SERVICE_PORTS.AI_ADVISOR,
    healthEndpoint: '/healthz',
    timeout: 30000,
    retries: 2,
  },
  'knowledge-graph': {
    name: 'knowledge-graph',
    baseUrl: `${API_BASE}:${SERVICE_PORTS.KNOWLEDGE_GRAPH}`,
    port: SERVICE_PORTS.KNOWLEDGE_GRAPH,
    healthEndpoint: '/healthz',
    timeout: 20000,
    retries: 2,
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // IoT & Sensors
  // ═══════════════════════════════════════════════════════════════════════════
  'virtual-sensors': {
    name: 'virtual-sensors',
    baseUrl: `${API_BASE}:${SERVICE_PORTS.VIRTUAL_SENSORS}`,
    port: SERVICE_PORTS.VIRTUAL_SENSORS,
    healthEndpoint: '/healthz',
    timeout: 10000,
    retries: 3,
  },
  'iot-gateway': {
    name: 'iot-gateway',
    baseUrl: `${API_BASE}:${SERVICE_PORTS.IOT_GATEWAY}`,
    port: SERVICE_PORTS.IOT_GATEWAY,
    healthEndpoint: '/healthz',
    timeout: 10000,
    retries: 2,
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // Operations
  // ═══════════════════════════════════════════════════════════════════════════
  irrigation: {
    name: 'irrigation',
    baseUrl: `${API_BASE}:${SERVICE_PORTS.IRRIGATION_SMART}`,
    port: SERVICE_PORTS.IRRIGATION_SMART,
    healthEndpoint: '/healthz',
    timeout: 10000,
    retries: 3,
  },
  tasks: {
    name: 'tasks',
    baseUrl: `${API_BASE}:${SERVICE_PORTS.TASK_SERVICE}`,
    port: SERVICE_PORTS.TASK_SERVICE,
    healthEndpoint: '/healthz',
    timeout: 10000,
    retries: 3,
  },
  equipment: {
    name: 'equipment',
    baseUrl: `${API_BASE}:${SERVICE_PORTS.EQUIPMENT}`,
    port: SERVICE_PORTS.EQUIPMENT,
    healthEndpoint: '/healthz',
    timeout: 10000,
    retries: 3,
  },
  inventory: {
    name: 'inventory',
    baseUrl: `${API_BASE}:${SERVICE_PORTS.INVENTORY}`,
    port: SERVICE_PORTS.INVENTORY,
    healthEndpoint: '/healthz',
    timeout: 10000,
    retries: 3,
  },
  logistics: {
    name: 'logistics',
    baseUrl: `${API_BASE}:${SERVICE_PORTS.LOGISTICS}`,
    port: SERVICE_PORTS.LOGISTICS,
    healthEndpoint: '/healthz',
    timeout: 15000,
    retries: 2,
  },
  'supply-chain': {
    name: 'supply-chain',
    baseUrl: `${API_BASE}:${SERVICE_PORTS.SUPPLY_CHAIN}`,
    port: SERVICE_PORTS.SUPPLY_CHAIN,
    healthEndpoint: '/healthz',
    timeout: 15000,
    retries: 2,
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // Communication
  // ═══════════════════════════════════════════════════════════════════════════
  notifications: {
    name: 'notifications',
    baseUrl: `${API_BASE}:${SERVICE_PORTS.NOTIFICATIONS}`,
    port: SERVICE_PORTS.NOTIFICATIONS,
    healthEndpoint: '/healthz',
    timeout: 5000,
    retries: 2,
  },
  'chat-service': {
    name: 'chat-service',
    baseUrl: `${API_BASE}:${SERVICE_PORTS.CHAT_SERVICE}`,
    port: SERVICE_PORTS.CHAT_SERVICE,
    healthEndpoint: '/healthz',
    timeout: 10000,
    retries: 2,
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // Configuration & Misc
  // ═══════════════════════════════════════════════════════════════════════════
  'provider-config': {
    name: 'provider-config',
    baseUrl: `${API_BASE}:${SERVICE_PORTS.PROVIDER_CONFIG}`,
    port: SERVICE_PORTS.PROVIDER_CONFIG,
    healthEndpoint: '/healthz',
    timeout: 10000,
    retries: 2,
  },
  alerts: {
    name: 'alerts',
    baseUrl: `${API_BASE}:${SERVICE_PORTS.ALERT_SERVICE}`,
    port: SERVICE_PORTS.ALERT_SERVICE,
    healthEndpoint: '/healthz',
    timeout: 5000,
    retries: 2,
  },
  reports: {
    name: 'reports',
    // Reports port (8084) - not registered in SERVICE_PORTS
    baseUrl: `${API_BASE}:8084`,
    port: 8084,
    healthEndpoint: '/healthz',
    timeout: 30000,
    retries: 2,
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // Billing & Audit
  // ═══════════════════════════════════════════════════════════════════════════
  billing: {
    name: 'billing',
    baseUrl: `${API_BASE}:${SERVICE_PORTS.BILLING_CORE}`,
    port: SERVICE_PORTS.BILLING_CORE,
    healthEndpoint: '/healthz',
    timeout: 15000,
    retries: 2,
  },
  audit: {
    name: 'audit',
    baseUrl: `${API_BASE}:${SERVICE_PORTS.AUDIT_SERVICE}`,
    port: SERVICE_PORTS.AUDIT_SERVICE,
    healthEndpoint: '/healthz',
    timeout: 10000,
    retries: 2,
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // Agriculture Domain
  // ═══════════════════════════════════════════════════════════════════════════
  drone: {
    name: 'drone',
    baseUrl: `${API_BASE}:${SERVICE_PORTS.DRONE_SERVICE}`,
    port: SERVICE_PORTS.DRONE_SERVICE,
    healthEndpoint: '/healthz',
    timeout: 20000,
    retries: 2,
  },
  'soil-analysis': {
    name: 'soil-analysis',
    baseUrl: `${API_BASE}:${SERVICE_PORTS.SOIL_ANALYSIS}`,
    port: SERVICE_PORTS.SOIL_ANALYSIS,
    healthEndpoint: '/healthz',
    timeout: 15000,
    retries: 2,
  },
  'pest-detection': {
    name: 'pest-detection',
    baseUrl: `${API_BASE}:${SERVICE_PORTS.PEST_DETECTION}`,
    port: SERVICE_PORTS.PEST_DETECTION,
    healthEndpoint: '/healthz',
    timeout: 20000,
    retries: 2,
  },
  traceability: {
    name: 'traceability',
    baseUrl: `${API_BASE}:${SERVICE_PORTS.TRACEABILITY}`,
    port: SERVICE_PORTS.TRACEABILITY,
    healthEndpoint: '/healthz',
    timeout: 15000,
    retries: 2,
  },
  globalgap: {
    name: 'globalgap',
    baseUrl: `${API_BASE}:${SERVICE_PORTS.GLOBALGAP}`,
    port: SERVICE_PORTS.GLOBALGAP,
    healthEndpoint: '/healthz',
    timeout: 15000,
    retries: 2,
  },
  crm: {
    name: 'crm',
    baseUrl: `${API_BASE}:${SERVICE_PORTS.CRM_SERVICE}`,
    port: SERVICE_PORTS.CRM_SERVICE,
    healthEndpoint: '/healthz',
    timeout: 10000,
    retries: 2,
  },
  cooperative: {
    name: 'cooperative',
    baseUrl: `${API_BASE}:${SERVICE_PORTS.COOPERATIVE}`,
    port: SERVICE_PORTS.COOPERATIVE,
    healthEndpoint: '/healthz',
    timeout: 15000,
    retries: 2,
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // Vision & Terrain
  // ═══════════════════════════════════════════════════════════════════════════
  'yolo-vision': {
    name: 'yolo-vision',
    baseUrl: `${API_BASE}:${SERVICE_PORTS.YOLO_VISION}`,
    port: SERVICE_PORTS.YOLO_VISION,
    healthEndpoint: '/healthz',
    timeout: 60000,
    retries: 1,
  },
  'terrain-core': {
    name: 'terrain-core',
    baseUrl: `${API_BASE}:${SERVICE_PORTS.TERRAIN_CORE}`,
    port: SERVICE_PORTS.TERRAIN_CORE,
    healthEndpoint: '/healthz',
    timeout: 30000,
    retries: 2,
  },
  hydrology: {
    name: 'hydrology',
    baseUrl: `${API_BASE}:${SERVICE_PORTS.HYDROLOGY}`,
    port: SERVICE_PORTS.HYDROLOGY,
    healthEndpoint: '/healthz',
    timeout: 30000,
    retries: 2,
  },
  'leveling-optimizer': {
    name: 'leveling-optimizer',
    baseUrl: `${API_BASE}:${SERVICE_PORTS.LEVELING_OPTIMIZER}`,
    port: SERVICE_PORTS.LEVELING_OPTIMIZER,
    healthEndpoint: '/healthz',
    timeout: 30000,
    retries: 2,
  },
  'edge-orchestrator': {
    name: 'edge-orchestrator',
    baseUrl: `${API_BASE}:${SERVICE_PORTS.EDGE_ORCHESTRATOR}`,
    port: SERVICE_PORTS.EDGE_ORCHESTRATOR,
    healthEndpoint: '/healthz',
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
      state: 'closed',
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
    breaker.state = 'open';
    breaker.nextRetry = new Date(Date.now() + CIRCUIT_BREAKER_TIMEOUT);
    logger.warn(`🔴 Circuit breaker OPEN for ${service}`);
  }
}

function recordSuccess(service: ServiceName): void {
  const breaker = getCircuitBreaker(service);
  breaker.failures = 0;
  breaker.state = 'closed';
  breaker.nextRetry = null;
}

function canRequest(service: ServiceName): boolean {
  const breaker = getCircuitBreaker(service);

  if (breaker.state === 'closed') return true;

  if (breaker.state === 'open' && breaker.nextRetry) {
    if (new Date() >= breaker.nextRetry) {
      breaker.state = 'half-open';
      logger.log(`🟡 Circuit breaker HALF-OPEN for ${service}`);
      return true;
    }
    return false;
  }

  return breaker.state === 'half-open';
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
        'Content-Type': 'application/json',
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
        // Only record server errors (5xx) as circuit breaker failures
        // Client errors (4xx) indicate the service is reachable
        const status = error.response?.status;
        if (!status || status >= 500) {
          recordFailure(service);
        }
        throw error;
      }
    );

    serviceClients.set(service, client);
  }

  return serviceClients.get(service)!;
}

// ═══════════════════════════════════════════════════════════════════════════
// Auth Helpers
// ═══════════════════════════════════════════════════════════════════════════

function getAuthToken(): string | null {
  if (typeof document === 'undefined') return null;
  // nosemgrep: javascript.browser.security.insecure-document-method (read-only cookie access for auth token retrieval)
  const match = document.cookie.match(/(?:^|; )sahool_admin_token=([^;]*)/);
  return match && match[1] ? decodeURIComponent(match[1]) : null;
}

function handleAuthError(): void {
  if (typeof window !== 'undefined') {
    window.location.href = '/login';
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
  options: AxiosRequestConfig = {}
): Promise<ApiResponse<T>> {
  const startTime = Date.now();

  // Check circuit breaker
  if (!canRequest(service)) {
    return {
      success: false,
      error: {
        code: 'CIRCUIT_OPEN',
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
  const retries = options.method === 'GET' ? config.retries || 3 : 1;

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
      if (axios.isAxiosError(error) && error.response?.status && error.response.status < 500) {
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
      code: axiosError.code || 'REQUEST_FAILED',
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
  params?: Record<string, unknown>
): Promise<ApiResponse<T>> {
  return request<T>(service, endpoint, { method: 'GET', params });
}

/**
 * POST request
 */
export function post<T>(
  service: ServiceName,
  endpoint: string,
  data?: unknown
): Promise<ApiResponse<T>> {
  return request<T>(service, endpoint, { method: 'POST', data });
}

/**
 * PUT request
 */
export function put<T>(
  service: ServiceName,
  endpoint: string,
  data?: unknown
): Promise<ApiResponse<T>> {
  return request<T>(service, endpoint, { method: 'PUT', data });
}

/**
 * DELETE request
 */
export function del<T>(service: ServiceName, endpoint: string): Promise<ApiResponse<T>> {
  return request<T>(service, endpoint, { method: 'DELETE' });
}

// ═══════════════════════════════════════════════════════════════════════════
// Health Checks
// ═══════════════════════════════════════════════════════════════════════════

const healthCache = new Map<ServiceName, ServiceHealth>();

/**
 * Check health of a service
 * فحص صحة خدمة
 */
export async function checkServiceHealth(service: ServiceName): Promise<ServiceHealth> {
  const config = SERVICES[service];
  const startTime = Date.now();

  try {
    await axios.get(`${config.baseUrl}${config.healthEndpoint || '/health'}`, {
      timeout: 5000,
    });

    const health: ServiceHealth = {
      name: service,
      status: 'healthy',
      latency: Date.now() - startTime,
      lastCheck: new Date(),
    };

    healthCache.set(service, health);
    return health;
  } catch (error) {
    const health: ServiceHealth = {
      name: service,
      status: 'unhealthy',
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
export function getCircuitBreakerStatus(): Map<ServiceName, CircuitBreakerState> {
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
