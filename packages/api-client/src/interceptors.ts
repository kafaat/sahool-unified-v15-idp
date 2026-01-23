// ═══════════════════════════════════════════════════════════════════════════════
// SAHOOL API Client - Enhanced Interceptors
// المعترضات المحسنة للطلبات والردود
// ═══════════════════════════════════════════════════════════════════════════════

import {
  AxiosInstance,
  AxiosRequestConfig,
  AxiosResponse,
  AxiosError,
  InternalAxiosRequestConfig,
  CancelTokenSource,
} from "axios";
import axios from "axios";

// ─────────────────────────────────────────────────────────────────────────────
// Types
// ─────────────────────────────────────────────────────────────────────────────

export interface RequestMetadata {
  /**
   * Unique request ID for tracing
   */
  requestId: string;

  /**
   * Timestamp when request was initiated
   */
  startTime: number;

  /**
   * Request URL
   */
  url: string;

  /**
   * HTTP method
   */
  method: string;

  /**
   * Whether request is a duplicate
   */
  isDuplicate?: boolean;

  /**
   * Custom metadata
   */
  custom?: Record<string, unknown>;
}

export interface ResponseMetadata extends RequestMetadata {
  /**
   * Timestamp when response was received
   */
  endTime: number;

  /**
   * Total duration in milliseconds
   */
  duration: number;

  /**
   * HTTP status code
   */
  status: number;

  /**
   * Response size in bytes (if available)
   */
  size?: number;

  /**
   * Whether response was served from cache
   */
  fromCache?: boolean;

  /**
   * Whether response was stale
   */
  isStale?: boolean;
}

export interface InterceptorConfig {
  /**
   * Enable request deduplication
   * @default true
   */
  deduplication: boolean;

  /**
   * Window in ms to consider requests as duplicates
   * @default 100
   */
  deduplicationWindow: number;

  /**
   * Enable request timing/performance tracking
   * @default true
   */
  timing: boolean;

  /**
   * Enable request ID header
   * @default true
   */
  requestId: boolean;

  /**
   * Header name for request ID
   * @default 'X-Request-ID'
   */
  requestIdHeader: string;

  /**
   * Enable automatic request cancellation on unmount
   * @default true
   */
  autoCancelation: boolean;

  /**
   * Request transformers
   */
  transformers?: {
    request?: RequestTransformer[];
    response?: ResponseTransformer[];
  };

  /**
   * Callback for request start
   */
  onRequestStart?: (metadata: RequestMetadata) => void;

  /**
   * Callback for request complete
   */
  onRequestComplete?: (metadata: ResponseMetadata) => void;

  /**
   * Callback for request error
   */
  onRequestError?: (
    metadata: RequestMetadata,
    error: AxiosError,
    duration: number,
  ) => void;

  /**
   * Callback for slow requests (exceeding threshold)
   */
  onSlowRequest?: (metadata: ResponseMetadata, threshold: number) => void;

  /**
   * Slow request threshold in milliseconds
   * @default 3000
   */
  slowRequestThreshold: number;
}

export type RequestTransformer = (
  config: InternalAxiosRequestConfig,
) => InternalAxiosRequestConfig | Promise<InternalAxiosRequestConfig>;

export type ResponseTransformer = (
  response: AxiosResponse,
) => AxiosResponse | Promise<AxiosResponse>;

// Extend AxiosRequestConfig for metadata
declare module "axios" {
  interface InternalAxiosRequestConfig {
    __metadata?: RequestMetadata;
    __cancelSource?: CancelTokenSource;
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Default Configuration
// ─────────────────────────────────────────────────────────────────────────────

export const DEFAULT_INTERCEPTOR_CONFIG: InterceptorConfig = {
  deduplication: true,
  deduplicationWindow: 100,
  timing: true,
  requestId: true,
  requestIdHeader: "X-Request-ID",
  autoCancelation: true,
  slowRequestThreshold: 3000,
};

// ─────────────────────────────────────────────────────────────────────────────
// Utility Functions
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Generate a unique request ID
 */
export function generateRequestId(): string {
  // Use crypto.randomUUID if available, otherwise fallback
  if (typeof crypto !== "undefined" && crypto.randomUUID) {
    return crypto.randomUUID();
  }

  // Fallback: timestamp + random
  return `${Date.now().toString(36)}-${Math.random().toString(36).substring(2, 11)}`;
}

/**
 * Generate a deduplication key for a request
 */
export function generateDedupeKey(config: AxiosRequestConfig): string {
  const method = config.method?.toUpperCase() || "GET";
  const url = config.url || "";
  const params = config.params ? JSON.stringify(config.params) : "";
  const data = config.data ? JSON.stringify(config.data) : "";

  return `${method}:${url}:${params}:${data}`;
}

/**
 * Calculate response size from headers or data
 */
export function calculateResponseSize(response: AxiosResponse): number {
  // Try content-length header first
  const contentLength = response.headers["content-length"];
  if (contentLength) {
    return parseInt(contentLength, 10);
  }

  // Estimate from data
  if (response.data) {
    const json = JSON.stringify(response.data);
    return new Blob([json]).size;
  }

  return 0;
}

// ─────────────────────────────────────────────────────────────────────────────
// Request Deduplication
// ─────────────────────────────────────────────────────────────────────────────

interface PendingRequest {
  promise: Promise<AxiosResponse>;
  timestamp: number;
  cancelSource: CancelTokenSource;
}

class RequestDeduplicator {
  private pendingRequests: Map<string, PendingRequest> = new Map();
  private window: number;

  constructor(window: number = 100) {
    this.window = window;
  }

  /**
   * Check if a similar request is already pending
   */
  isDuplicate(key: string): boolean {
    const pending = this.pendingRequests.get(key);
    if (!pending) return false;

    // Check if still within deduplication window
    if (Date.now() - pending.timestamp > this.window) {
      this.pendingRequests.delete(key);
      return false;
    }

    return true;
  }

  /**
   * Get the pending promise for a duplicate request
   */
  getPending(key: string): Promise<AxiosResponse> | null {
    const pending = this.pendingRequests.get(key);
    return pending?.promise ?? null;
  }

  /**
   * Register a new request as pending
   */
  register(
    key: string,
    promise: Promise<AxiosResponse>,
    cancelSource: CancelTokenSource,
  ): void {
    this.pendingRequests.set(key, {
      promise,
      timestamp: Date.now(),
      cancelSource,
    });

    // Auto-cleanup when promise resolves/rejects
    promise.finally(() => {
      this.pendingRequests.delete(key);
    });
  }

  /**
   * Cancel all pending requests
   */
  cancelAll(reason?: string): void {
    for (const [key, request] of this.pendingRequests) {
      request.cancelSource.cancel(reason || "Request cancelled");
      this.pendingRequests.delete(key);
    }
  }

  /**
   * Cancel a specific request by key
   */
  cancel(key: string, reason?: string): boolean {
    const pending = this.pendingRequests.get(key);
    if (pending) {
      pending.cancelSource.cancel(reason || "Request cancelled");
      this.pendingRequests.delete(key);
      return true;
    }
    return false;
  }

  /**
   * Get count of pending requests
   */
  get pendingCount(): number {
    return this.pendingRequests.size;
  }

  /**
   * Clean up old pending requests
   */
  cleanup(): void {
    const now = Date.now();
    for (const [key, request] of this.pendingRequests) {
      if (now - request.timestamp > this.window) {
        this.pendingRequests.delete(key);
      }
    }
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Performance Tracker
// ─────────────────────────────────────────────────────────────────────────────

export interface PerformanceStats {
  totalRequests: number;
  successfulRequests: number;
  failedRequests: number;
  averageDuration: number;
  minDuration: number;
  maxDuration: number;
  slowRequests: number;
  totalBytes: number;
  requestsByEndpoint: Map<string, EndpointStats>;
}

export interface EndpointStats {
  count: number;
  totalDuration: number;
  averageDuration: number;
  minDuration: number;
  maxDuration: number;
  errors: number;
}

class PerformanceTracker {
  private stats: PerformanceStats = {
    totalRequests: 0,
    successfulRequests: 0,
    failedRequests: 0,
    averageDuration: 0,
    minDuration: Infinity,
    maxDuration: 0,
    slowRequests: 0,
    totalBytes: 0,
    requestsByEndpoint: new Map(),
  };

  private durations: number[] = [];
  private maxSamples: number = 1000;

  /**
   * Record a successful request
   */
  recordSuccess(
    endpoint: string,
    duration: number,
    size: number,
    isSlow: boolean,
  ): void {
    this.stats.totalRequests += 1;
    this.stats.successfulRequests += 1;
    this.stats.totalBytes += size;

    if (isSlow) {
      this.stats.slowRequests += 1;
    }

    this.recordDuration(duration);
    this.updateEndpointStats(endpoint, duration, false);
  }

  /**
   * Record a failed request
   */
  recordError(endpoint: string, duration: number): void {
    this.stats.totalRequests += 1;
    this.stats.failedRequests += 1;
    this.recordDuration(duration);
    this.updateEndpointStats(endpoint, duration, true);
  }

  /**
   * Get current performance statistics
   */
  getStats(): PerformanceStats {
    return { ...this.stats };
  }

  /**
   * Get stats for a specific endpoint
   */
  getEndpointStats(endpoint: string): EndpointStats | undefined {
    return this.stats.requestsByEndpoint.get(endpoint);
  }

  /**
   * Reset all statistics
   */
  reset(): void {
    this.stats = {
      totalRequests: 0,
      successfulRequests: 0,
      failedRequests: 0,
      averageDuration: 0,
      minDuration: Infinity,
      maxDuration: 0,
      slowRequests: 0,
      totalBytes: 0,
      requestsByEndpoint: new Map(),
    };
    this.durations = [];
  }

  private recordDuration(duration: number): void {
    this.durations.push(duration);

    // Keep only recent samples
    if (this.durations.length > this.maxSamples) {
      this.durations.shift();
    }

    // Update stats
    this.stats.minDuration = Math.min(this.stats.minDuration, duration);
    this.stats.maxDuration = Math.max(this.stats.maxDuration, duration);
    this.stats.averageDuration =
      this.durations.reduce((a, b) => a + b, 0) / this.durations.length;
  }

  private updateEndpointStats(
    endpoint: string,
    duration: number,
    isError: boolean,
  ): void {
    // Extract base endpoint (without query params)
    const baseEndpoint = endpoint.split("?")[0];

    let stats = this.stats.requestsByEndpoint.get(baseEndpoint);

    if (!stats) {
      stats = {
        count: 0,
        totalDuration: 0,
        averageDuration: 0,
        minDuration: Infinity,
        maxDuration: 0,
        errors: 0,
      };
      this.stats.requestsByEndpoint.set(baseEndpoint, stats);
    }

    stats.count += 1;
    stats.totalDuration += duration;
    stats.averageDuration = stats.totalDuration / stats.count;
    stats.minDuration = Math.min(stats.minDuration, duration);
    stats.maxDuration = Math.max(stats.maxDuration, duration);

    if (isError) {
      stats.errors += 1;
    }
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Cancel Token Manager
// ─────────────────────────────────────────────────────────────────────────────

class CancelTokenManager {
  private tokens: Map<string, CancelTokenSource> = new Map();
  private groupTokens: Map<string, Set<string>> = new Map();

  /**
   * Create a cancel token for a request
   */
  create(requestId: string, group?: string): CancelTokenSource {
    const source = axios.CancelToken.source();
    this.tokens.set(requestId, source);

    if (group) {
      if (!this.groupTokens.has(group)) {
        this.groupTokens.set(group, new Set());
      }
      this.groupTokens.get(group)!.add(requestId);
    }

    return source;
  }

  /**
   * Cancel a specific request
   */
  cancel(requestId: string, reason?: string): boolean {
    const source = this.tokens.get(requestId);
    if (source) {
      source.cancel(reason || "Request cancelled");
      this.tokens.delete(requestId);
      return true;
    }
    return false;
  }

  /**
   * Cancel all requests in a group
   */
  cancelGroup(group: string, reason?: string): number {
    const requestIds = this.groupTokens.get(group);
    if (!requestIds) return 0;

    let count = 0;
    for (const requestId of requestIds) {
      if (this.cancel(requestId, reason)) {
        count += 1;
      }
    }

    this.groupTokens.delete(group);
    return count;
  }

  /**
   * Cancel all pending requests
   */
  cancelAll(reason?: string): number {
    let count = 0;
    for (const [requestId, source] of this.tokens) {
      source.cancel(reason || "All requests cancelled");
      count += 1;
    }
    this.tokens.clear();
    this.groupTokens.clear();
    return count;
  }

  /**
   * Remove a token (after request completes)
   */
  remove(requestId: string): void {
    this.tokens.delete(requestId);

    // Also remove from groups
    for (const [, requestIds] of this.groupTokens) {
      requestIds.delete(requestId);
    }
  }

  /**
   * Check if a request was cancelled
   */
  isCancelled(requestId: string): boolean {
    const source = this.tokens.get(requestId);
    return source?.token.reason !== undefined;
  }

  /**
   * Get count of active tokens
   */
  get activeCount(): number {
    return this.tokens.size;
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Enhanced Interceptors Setup
// ─────────────────────────────────────────────────────────────────────────────

export interface InterceptorManager {
  deduplicator: RequestDeduplicator;
  performanceTracker: PerformanceTracker;
  cancelTokenManager: CancelTokenManager;
  getStats: () => PerformanceStats;
  cancelAll: (reason?: string) => void;
  cancelGroup: (group: string, reason?: string) => number;
}

/**
 * Setup enhanced interceptors on an Axios instance
 */
export function setupEnhancedInterceptors(
  axiosInstance: AxiosInstance,
  config: Partial<InterceptorConfig> = {},
): InterceptorManager {
  const cfg: InterceptorConfig = { ...DEFAULT_INTERCEPTOR_CONFIG, ...config };

  const deduplicator = new RequestDeduplicator(cfg.deduplicationWindow);
  const performanceTracker = new PerformanceTracker();
  const cancelTokenManager = new CancelTokenManager();

  // Request interceptor
  axiosInstance.interceptors.request.use(
    async (requestConfig) => {
      // Generate request ID
      const requestId = generateRequestId();

      // Create metadata
      const metadata: RequestMetadata = {
        requestId,
        startTime: Date.now(),
        url: requestConfig.url || "",
        method: requestConfig.method?.toUpperCase() || "GET",
      };

      requestConfig.__metadata = metadata;

      // Add request ID header
      if (cfg.requestId) {
        requestConfig.headers[cfg.requestIdHeader] = requestId;
      }

      // Setup cancel token
      if (cfg.autoCancelation) {
        const cancelSource = cancelTokenManager.create(requestId);
        requestConfig.cancelToken = cancelSource.token;
        requestConfig.__cancelSource = cancelSource;
      }

      // Check for duplicates (only for GET requests)
      if (
        cfg.deduplication &&
        requestConfig.method?.toUpperCase() === "GET"
      ) {
        const dedupeKey = generateDedupeKey(requestConfig);

        if (deduplicator.isDuplicate(dedupeKey)) {
          metadata.isDuplicate = true;
          // Return pending promise (will be handled specially)
          const pending = deduplicator.getPending(dedupeKey);
          if (pending) {
            // Mark request as cancelled to skip actual request
            const cancelSource = axios.CancelToken.source();
            cancelSource.cancel("DEDUPE:" + dedupeKey);
            requestConfig.cancelToken = cancelSource.token;
          }
        }
      }

      // Apply custom transformers
      if (cfg.transformers?.request) {
        let transformedConfig = requestConfig;
        for (const transformer of cfg.transformers.request) {
          transformedConfig = await transformer(transformedConfig);
        }
        return transformedConfig;
      }

      // Call onRequestStart callback
      if (cfg.timing && cfg.onRequestStart) {
        cfg.onRequestStart(metadata);
      }

      return requestConfig;
    },
    (error) => Promise.reject(error),
  );

  // Response interceptor
  axiosInstance.interceptors.response.use(
    async (response) => {
      const metadata = response.config.__metadata;
      const endTime = Date.now();

      if (metadata && cfg.timing) {
        const duration = endTime - metadata.startTime;
        const size = calculateResponseSize(response);
        const isSlow = duration > cfg.slowRequestThreshold;

        const responseMetadata: ResponseMetadata = {
          ...metadata,
          endTime,
          duration,
          status: response.status,
          size,
        };

        // Track performance
        performanceTracker.recordSuccess(metadata.url, duration, size, isSlow);

        // Call callbacks
        cfg.onRequestComplete?.(responseMetadata);

        if (isSlow && cfg.onSlowRequest) {
          cfg.onSlowRequest(responseMetadata, cfg.slowRequestThreshold);
        }
      }

      // Clean up cancel token
      if (metadata) {
        cancelTokenManager.remove(metadata.requestId);
      }

      // Apply custom response transformers
      if (cfg.transformers?.response) {
        let transformedResponse = response;
        for (const transformer of cfg.transformers.response) {
          transformedResponse = await transformer(transformedResponse);
        }
        return transformedResponse;
      }

      return response;
    },
    async (error: AxiosError) => {
      const config = error.config;
      const metadata = config?.__metadata;

      // Handle deduplicated requests
      if (axios.isCancel(error) && error.message?.startsWith("DEDUPE:")) {
        const dedupeKey = error.message.substring(7);
        const pending = deduplicator.getPending(dedupeKey);
        if (pending) {
          return pending;
        }
      }

      if (metadata && cfg.timing) {
        const endTime = Date.now();
        const duration = endTime - metadata.startTime;

        // Track error
        performanceTracker.recordError(metadata.url, duration);

        // Call error callback
        cfg.onRequestError?.(metadata, error, duration);
      }

      // Clean up cancel token
      if (metadata) {
        cancelTokenManager.remove(metadata.requestId);
      }

      return Promise.reject(error);
    },
  );

  return {
    deduplicator,
    performanceTracker,
    cancelTokenManager,
    getStats: () => performanceTracker.getStats(),
    cancelAll: (reason) => {
      deduplicator.cancelAll(reason);
      cancelTokenManager.cancelAll(reason);
    },
    cancelGroup: (group, reason) => cancelTokenManager.cancelGroup(group, reason),
  };
}

// ─────────────────────────────────────────────────────────────────────────────
// Common Request Transformers
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Add tenant ID to all requests
 */
export function tenantIdTransformer(
  getTenantId: () => string | null,
): RequestTransformer {
  return (config) => {
    const tenantId = getTenantId();
    if (tenantId) {
      config.headers["X-Tenant-ID"] = tenantId;
    }
    return config;
  };
}

/**
 * Add correlation ID for distributed tracing
 */
export function correlationIdTransformer(
  getCorrelationId: () => string | null,
): RequestTransformer {
  return (config) => {
    const correlationId = getCorrelationId() || generateRequestId();
    config.headers["X-Correlation-ID"] = correlationId;
    return config;
  };
}

/**
 * Add timestamp to all requests
 */
export function timestampTransformer(): RequestTransformer {
  return (config) => {
    config.headers["X-Request-Time"] = new Date().toISOString();
    return config;
  };
}

/**
 * Camel case to snake case transformer for request data
 */
export function snakeCaseTransformer(): RequestTransformer {
  return (config) => {
    if (config.data && typeof config.data === "object") {
      config.data = toSnakeCase(config.data);
    }
    if (config.params && typeof config.params === "object") {
      config.params = toSnakeCase(config.params);
    }
    return config;
  };
}

/**
 * Snake case to camel case transformer for response data
 */
export function camelCaseTransformer(): ResponseTransformer {
  return (response) => {
    if (response.data && typeof response.data === "object") {
      response.data = toCamelCase(response.data);
    }
    return response;
  };
}

// Helper functions for case conversion
function toSnakeCase(obj: Record<string, unknown>): Record<string, unknown> {
  if (Array.isArray(obj)) {
    return obj.map((item) =>
      typeof item === "object" && item !== null
        ? toSnakeCase(item as Record<string, unknown>)
        : item,
    ) as unknown as Record<string, unknown>;
  }

  const result: Record<string, unknown> = {};
  for (const [key, value] of Object.entries(obj)) {
    const snakeKey = key.replace(/([A-Z])/g, "_$1").toLowerCase();
    result[snakeKey] =
      value && typeof value === "object"
        ? toSnakeCase(value as Record<string, unknown>)
        : value;
  }
  return result;
}

function toCamelCase(obj: Record<string, unknown>): Record<string, unknown> {
  if (Array.isArray(obj)) {
    return obj.map((item) =>
      typeof item === "object" && item !== null
        ? toCamelCase(item as Record<string, unknown>)
        : item,
    ) as unknown as Record<string, unknown>;
  }

  const result: Record<string, unknown> = {};
  for (const [key, value] of Object.entries(obj)) {
    const camelKey = key.replace(/_([a-z])/g, (_, letter) =>
      letter.toUpperCase(),
    );
    result[camelKey] =
      value && typeof value === "object"
        ? toCamelCase(value as Record<string, unknown>)
        : value;
  }
  return result;
}
