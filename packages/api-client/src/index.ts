// ═══════════════════════════════════════════════════════════════════════════════
// SAHOOL Unified API Client
// عميل API الموحد لمنصة سهول
// ═══════════════════════════════════════════════════════════════════════════════

import axios, { AxiosInstance, AxiosRequestConfig, AxiosError, AxiosResponse } from "axios";
import type {
  ApiClientConfig,
  ServicePorts,
  Task,
  CreateTaskRequest,
  TaskEvidence,
  Field,
  Farm,
  WeatherData,
  WeatherForecast,
  WeatherAlert,
  DiagnosisRecord,
  DiagnosisStats,
  DashboardStats,
  DashboardData,
  FieldIndicators,
  SensorReading,
  Equipment,
  Notification,
  CommunityPost,
  Severity,
  DiagnosisStatus,
  LogLevel,
  PaginatedResponse,
} from "./types";
import { ApiError, parseAxiosError } from "./errors";
import {
  RetryConfig,
  DEFAULT_RETRY_CONFIG,
  setupRetryInterceptor,
  CircuitBreaker,
  CircuitBreakerConfig,
  withRetry,
} from "./retry";
import {
  CacheConfig,
  DEFAULT_CACHE_CONFIG,
  MemoryCache,
  createCache,
  shouldCacheRequest,
  getRequestTTL,
  getCacheKey,
  getCachePolicy,
  shouldForceRefresh,
  CacheTTL,
} from "./cache";
import {
  InterceptorConfig,
  DEFAULT_INTERCEPTOR_CONFIG,
  setupEnhancedInterceptors,
  InterceptorManager,
  PerformanceStats,
} from "./interceptors";
import {
  Result,
  AsyncState,
  success,
  failure,
  toResult,
  ValidationResult,
} from "./validation";

// Re-export all types
export * from "./types";
// Re-export all errors
export * from "./errors";
// Re-export retry utilities
export * from "./retry";
// Re-export cache utilities
export * from "./cache";
// Re-export interceptor utilities
export * from "./interceptors";
// Re-export validation utilities
export * from "./validation";

// ─────────────────────────────────────────────────────────────────────────────
// Enhanced Configuration Types
// ─────────────────────────────────────────────────────────────────────────────

export interface EnhancedApiClientConfig extends ApiClientConfig {
  /**
   * Retry configuration
   */
  retry?: Partial<RetryConfig> | boolean;

  /**
   * Cache configuration
   */
  cache?: Partial<CacheConfig> | boolean | "aggressive" | "conservative" | "offline";

  /**
   * Interceptor configuration
   */
  interceptors?: Partial<InterceptorConfig>;

  /**
   * Circuit breaker configuration
   */
  circuitBreaker?: Partial<CircuitBreakerConfig> | boolean;

  /**
   * Whether to validate responses at runtime
   * @default false
   */
  validateResponses?: boolean;

  /**
   * Tenant ID for multi-tenancy
   */
  tenantId?: string;

  /**
   * Get tenant ID dynamically
   */
  getTenantId?: () => string | null;
}

// ─────────────────────────────────────────────────────────────────────────────
// Default Configuration
// ─────────────────────────────────────────────────────────────────────────────

const DEFAULT_PORTS: ServicePorts = {
  fieldCore: 3000,
  satellite: 8090,
  indicators: 8091,
  weather: 8092,
  fertilizer: 8093,
  irrigation: 8094,
  cropHealth: 8095,
  virtualSensors: 8096,
  communityChat: 8097,
  yieldEngine: 8098,
  equipment: 8101,
  community: 8102,
  task: 8103,
  providerConfig: 8104,
  notifications: 8110,
  wsGateway: 8090,
  marketplace: 3010,
  auth: 8001,
};

// ─────────────────────────────────────────────────────────────────────────────
// SAHOOL API Client Class
// ─────────────────────────────────────────────────────────────────────────────

export class SahoolApiClient {
  private client: AxiosInstance;
  private config: EnhancedApiClientConfig;
  private ports: ServicePorts;
  private isProduction: boolean;
  private logLevel: LogLevel;
  private errorHandling: "throw" | "silent";

  // Enhanced features
  private cache?: MemoryCache;
  private circuitBreakers: Map<string, CircuitBreaker> = new Map();
  private interceptorManager?: InterceptorManager;

  constructor(
    config: EnhancedApiClientConfig,
    ports: Partial<ServicePorts> = {},
  ) {
    this.config = {
      timeout: 30000,
      locale: "ar",
      enableMockData: false,
      errorHandling: "throw",
      logLevel: "error",
      validateResponses: false,
      ...config,
    };
    this.ports = { ...DEFAULT_PORTS, ...ports };
    this.isProduction = process.env.NODE_ENV === "production";
    this.logLevel = this.config.logLevel || "error";
    this.errorHandling = this.config.errorHandling || "throw";

    // Create axios instance
    this.client = axios.create({
      timeout: this.config.timeout,
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
        "Accept-Language": `${this.config.locale},en`,
      },
    });

    // Setup features
    this.setupInterceptors();
    this.setupCache();
    this.setupRetry();
    this.setupCircuitBreakers();
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Setup Methods
  // ─────────────────────────────────────────────────────────────────────────

  private setupInterceptors(): void {
    // Request interceptor - add auth token
    this.client.interceptors.request.use((config) => {
      const token = this.config.getToken?.();
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }

      // Add tenant ID if available
      const tenantId = this.config.tenantId || this.config.getTenantId?.();
      if (tenantId) {
        config.headers["X-Tenant-ID"] = tenantId;
      }

      return config;
    });

    // Response interceptor - handle errors
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          this.config.onUnauthorized?.();
        }
        return Promise.reject(error);
      },
    );

    // Setup enhanced interceptors if configured
    if (this.config.interceptors) {
      this.interceptorManager = setupEnhancedInterceptors(
        this.client,
        this.config.interceptors,
      );
    }
  }

  private setupCache(): void {
    const cacheConfig = this.config.cache;

    if (cacheConfig === false) {
      return;
    }

    if (typeof cacheConfig === "string") {
      // Preset name
      this.cache = createCache(cacheConfig);
    } else if (cacheConfig === true || cacheConfig === undefined) {
      // Default cache
      this.cache = new MemoryCache();
    } else {
      // Custom config
      this.cache = new MemoryCache(cacheConfig);
    }
  }

  private setupRetry(): void {
    const retryConfig = this.config.retry;

    if (retryConfig === false) {
      return;
    }

    const config: Partial<RetryConfig> =
      retryConfig === true ? {} : retryConfig || {};

    // Add retry callbacks for logging
    const enhancedConfig: Partial<RetryConfig> = {
      ...config,
      onRetry: (error, attempt, delay) => {
        this.log("warn", `Retry attempt ${attempt} after ${delay}ms`, {
          url: error.config?.url,
          method: error.config?.method,
          error: error.message,
        });
        config.onRetry?.(error, attempt, delay);
      },
      onExhausted: (error, attempts) => {
        this.log("error", `All ${attempts} retry attempts exhausted`, {
          url: error.config?.url,
          method: error.config?.method,
          error: error.message,
        });
        config.onExhausted?.(error, attempts);
      },
    };

    setupRetryInterceptor(this.client, enhancedConfig);
  }

  private setupCircuitBreakers(): void {
    const cbConfig = this.config.circuitBreaker;

    if (cbConfig === false) {
      return;
    }

    // Create circuit breaker for each service
    const serviceNames = Object.keys(this.ports);
    const config: Partial<CircuitBreakerConfig> =
      cbConfig === true ? {} : cbConfig || {};

    for (const service of serviceNames) {
      this.circuitBreakers.set(
        service,
        new CircuitBreaker({
          ...config,
          onOpen: (failures) => {
            this.log("warn", `Circuit breaker opened for ${service}`, {
              failures,
            });
            config.onOpen?.(failures);
          },
          onClose: () => {
            this.log("info", `Circuit breaker closed for ${service}`);
            config.onClose?.();
          },
          onHalfOpen: () => {
            this.log("info", `Circuit breaker half-open for ${service}`);
            config.onHalfOpen?.();
          },
        }),
      );
    }
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Logging Utilities
  // ─────────────────────────────────────────────────────────────────────────

  private log(
    level: LogLevel,
    message: string,
    context?: Record<string, unknown>,
  ): void {
    const logLevels: Record<LogLevel, number> = {
      none: 0,
      error: 1,
      warn: 2,
      info: 3,
      debug: 4,
    };

    // Skip logging if level is 'none' or below threshold
    if (level === "none" || logLevels[this.logLevel] < logLevels[level]) {
      return;
    }

    const logger = this.config.logger;
    const logMessage = `[SAHOOL API Client] ${message}`;
    const logContext = context
      ? { ...context, timestamp: new Date().toISOString() }
      : undefined;

    if (logger) {
      // Logger doesn't have 'none', so we check for valid log levels
      const validLogLevel = level as "error" | "warn" | "info" | "debug";
      logger[validLogLevel]?.(logMessage, logContext);
    } else {
      // Fallback to console
      switch (level) {
        case "error":
          console.error(logMessage, logContext);
          break;
        case "warn":
          console.warn(logMessage, logContext);
          break;
        case "info":
          console.info(logMessage, logContext);
          break;
        case "debug":
          console.debug(logMessage, logContext);
          break;
      }
    }
  }

  private logError(error: ApiError): void {
    this.log("error", error.message, error.toJSON());
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Error Handling Utilities
  // ─────────────────────────────────────────────────────────────────────────

  private handleError(
    error: unknown,
    endpoint?: string,
    method?: string,
  ): never {
    let apiError: ApiError;

    if (axios.isAxiosError(error)) {
      apiError = parseAxiosError(error, endpoint, method);
    } else if (error instanceof ApiError) {
      apiError = error;
    } else if (error instanceof Error) {
      apiError = new ApiError(error.message, {
        originalError: error,
        endpoint,
        method,
      });
    } else {
      apiError = new ApiError("Unknown error occurred", {
        endpoint,
        method,
        context: { error },
      });
    }

    this.logError(apiError);
    throw apiError;
  }

  /**
   * Safe execution wrapper with backward compatibility
   * Returns fallback value in silent mode, throws error in throw mode
   */
  private async safeExecute<T>(
    operation: () => Promise<T>,
    fallback: T,
    context?: { endpoint?: string; method?: string },
  ): Promise<T> {
    try {
      return await operation();
    } catch (error) {
      if (this.errorHandling === "silent") {
        // Log the error even in silent mode
        if (axios.isAxiosError(error)) {
          const apiError = parseAxiosError(
            error,
            context?.endpoint,
            context?.method,
          );
          this.logError(apiError);
        } else {
          this.log(
            "error",
            `Silent error: ${error instanceof Error ? error.message : "Unknown error"}`,
            {
              error,
              ...context,
            },
          );
        }
        return fallback;
      } else {
        // In throw mode, let handleError do its job
        this.handleError(error, context?.endpoint, context?.method);
      }
    }
  }

  // ─────────────────────────────────────────────────────────────────────────
  // URL Helpers
  // ─────────────────────────────────────────────────────────────────────────

  private getServiceUrl(port: number): string {
    return this.isProduction
      ? `${this.config.baseUrl}/api`
      : `${this.config.baseUrl}:${port}`;
  }

  get urls() {
    return {
      fieldCore: this.getServiceUrl(this.ports.fieldCore),
      satellite: this.getServiceUrl(this.ports.satellite),
      indicators: this.getServiceUrl(this.ports.indicators),
      weather: this.getServiceUrl(this.ports.weather),
      fertilizer: this.getServiceUrl(this.ports.fertilizer),
      irrigation: this.getServiceUrl(this.ports.irrigation),
      cropHealth: this.getServiceUrl(this.ports.cropHealth),
      virtualSensors: this.getServiceUrl(this.ports.virtualSensors),
      communityChat: this.getServiceUrl(this.ports.communityChat),
      yieldEngine: this.getServiceUrl(this.ports.yieldEngine),
      equipment: this.getServiceUrl(this.ports.equipment),
      community: this.getServiceUrl(this.ports.community),
      task: this.getServiceUrl(this.ports.task),
      providerConfig: this.getServiceUrl(this.ports.providerConfig),
      notifications: this.getServiceUrl(this.ports.notifications),
      wsGateway: this.getServiceUrl(this.ports.wsGateway),
      marketplace: this.getServiceUrl(this.ports.marketplace),
      auth: this.getServiceUrl(this.ports.auth),
    };
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Generic Request Method with Caching
  // ─────────────────────────────────────────────────────────────────────────

  private async request<T>(
    url: string,
    options: AxiosRequestConfig = {},
  ): Promise<T> {
    const cacheConfig = this.cache
      ? { ...DEFAULT_CACHE_CONFIG, ...(this.config.cache as Partial<CacheConfig>) }
      : null;

    // Check cache for GET requests
    if (cacheConfig && this.cache && shouldCacheRequest(options, cacheConfig)) {
      const cacheKey = getCacheKey({ url, ...options }, cacheConfig);
      const policy = getCachePolicy(options, cacheConfig);
      const forceRefresh = shouldForceRefresh(options);

      // Try to get from cache first (unless force refresh)
      if (!forceRefresh && (policy === "cache-first" || policy === "cache-only")) {
        const cached = this.cache.get<T>(cacheKey);
        if (cached) {
          this.log("debug", `Cache hit for ${url}`, { cacheKey });
          return cached.data;
        }

        if (policy === "cache-only") {
          throw new ApiError("Resource not found in cache", {
            code: "CACHE_MISS",
            endpoint: url,
            method: options.method,
          });
        }
      }

      // Handle stale-while-revalidate
      if (policy === "stale-while-revalidate" && !forceRefresh) {
        const cached = this.cache.get<T>(cacheKey);
        if (cached) {
          const isFresh = this.cache.isFresh(cacheKey);

          if (!isFresh && !this.cache.isRevalidating(cacheKey)) {
            // Serve stale and revalidate in background
            this.log("debug", `Serving stale data for ${url}, revalidating`, {
              cacheKey,
            });
            this.cache.markRevalidating(cacheKey);

            // Background revalidation
            this.fetchAndCache<T>(url, options, cacheKey, cacheConfig)
              .catch((error) => {
                this.log("warn", `Background revalidation failed for ${url}`, {
                  error: error.message,
                });
              })
              .finally(() => {
                this.cache?.clearRevalidating(cacheKey);
              });

            return cached.data;
          }

          return cached.data;
        }
      }

      // Fetch from network and cache
      return this.fetchAndCache<T>(url, options, cacheKey, cacheConfig);
    }

    // Non-cached request
    return this.fetchFromNetwork<T>(url, options);
  }

  private async fetchAndCache<T>(
    url: string,
    options: AxiosRequestConfig,
    cacheKey: string,
    cacheConfig: CacheConfig,
  ): Promise<T> {
    const response = await this.fetchFromNetwork<T>(url, options, true);
    const ttl = getRequestTTL(options, cacheConfig);

    if (this.cache) {
      this.cache.set(cacheKey, {
        data: response,
        status: 200,
        statusText: "OK",
        headers: {},
        config: options as never,
      } as AxiosResponse<T>, ttl);
      this.log("debug", `Cached response for ${url}`, { cacheKey, ttl });
    }

    return response;
  }

  private async fetchFromNetwork<T>(
    url: string,
    options: AxiosRequestConfig,
    skipLog = false,
  ): Promise<T> {
    try {
      if (!skipLog) {
        this.log("debug", `Request: ${options.method || "GET"} ${url}`, {
          params: options.params,
          data: options.data,
        });
      }

      const response = await this.client.request<T>({ url, ...options });

      if (!skipLog) {
        this.log("debug", `Response: ${options.method || "GET"} ${url}`, {
          status: response.status,
          statusText: response.statusText,
        });
      }

      return response.data;
    } catch (error) {
      this.handleError(error, url, options.method?.toUpperCase() || "GET");
    }
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Result-based Request Method
  // ─────────────────────────────────────────────────────────────────────────

  /**
   * Make a request and return Result type instead of throwing
   */
  async requestSafe<T>(
    url: string,
    options: AxiosRequestConfig = {},
  ): Promise<Result<T, ApiError>> {
    try {
      const data = await this.request<T>(url, options);
      return success(data);
    } catch (error) {
      if (error instanceof ApiError) {
        return failure(error);
      }
      return failure(
        new ApiError(
          error instanceof Error ? error.message : "Unknown error",
          { endpoint: url, method: options.method },
        ),
      );
    }
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Auth Token Management
  // ─────────────────────────────────────────────────────────────────────────

  setToken(token: string): void {
    this.config.setToken?.(token);
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Cache Management
  // ─────────────────────────────────────────────────────────────────────────

  /**
   * Clear all cached data
   */
  clearCache(): void {
    this.cache?.clear();
    this.log("info", "Cache cleared");
  }

  /**
   * Invalidate cache entries by URL pattern
   */
  invalidateCache(urlPattern: string | RegExp): number {
    if (!this.cache) return 0;

    const pattern =
      typeof urlPattern === "string" ? new RegExp(urlPattern) : urlPattern;
    const count = this.cache.invalidatePattern(pattern);
    this.log("info", `Invalidated ${count} cache entries`, { pattern: String(pattern) });
    return count;
  }

  /**
   * Get cache statistics
   */
  getCacheStats() {
    return this.cache?.getStats() ?? null;
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Performance Management
  // ─────────────────────────────────────────────────────────────────────────

  /**
   * Get performance statistics
   */
  getPerformanceStats(): PerformanceStats | null {
    return this.interceptorManager?.getStats() ?? null;
  }

  /**
   * Cancel all pending requests
   */
  cancelAllRequests(reason?: string): void {
    this.interceptorManager?.cancelAll(reason);
    this.log("info", "All pending requests cancelled", { reason });
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Circuit Breaker Management
  // ─────────────────────────────────────────────────────────────────────────

  /**
   * Get circuit breaker status for a service
   */
  getCircuitBreakerStatus(service: string) {
    const cb = this.circuitBreakers.get(service);
    if (!cb) return null;

    return {
      state: cb.currentState,
      isOpen: cb.isOpen,
      isClosed: cb.isClosed,
      isHalfOpen: cb.isHalfOpen,
      timeUntilReset: cb.getTimeUntilReset(),
    };
  }

  /**
   * Reset circuit breaker for a service
   */
  resetCircuitBreaker(service: string): void {
    const cb = this.circuitBreakers.get(service);
    if (cb) {
      cb.reset();
      this.log("info", `Circuit breaker reset for ${service}`);
    }
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Tasks API
  // ─────────────────────────────────────────────────────────────────────────

  async getTasks(params?: {
    field_id?: string;
    status?: string;
    type?: string;
    assigned_to?: string;
    limit?: number;
  }): Promise<Task[]> {
    const endpoint = `${this.urls.task}/api/v1/tasks`;
    return this.safeExecute(
      () =>
        this.request<Task[]>(endpoint, {
          params,
          cache: { ttl: CacheTTL.SHORT },
        }),
      [],
      { endpoint, method: "GET" },
    );
  }

  async getTask(taskId: string): Promise<Task> {
    return this.request<Task>(`${this.urls.task}/api/v1/tasks/${taskId}`, {
      cache: { ttl: CacheTTL.SHORT },
    });
  }

  async createTask(task: CreateTaskRequest): Promise<Task> {
    const result = await this.request<Task>(`${this.urls.task}/api/v1/tasks`, {
      method: "POST",
      data: task,
    });

    // Invalidate tasks cache
    this.invalidateCache(/\/api\/v1\/tasks/);

    return result;
  }

  async updateTask(
    taskId: string,
    data: Partial<CreateTaskRequest>,
  ): Promise<Task> {
    const result = await this.request<Task>(
      `${this.urls.task}/api/v1/tasks/${taskId}`,
      {
        method: "PUT",
        data,
      },
    );

    // Invalidate tasks cache
    this.invalidateCache(/\/api\/v1\/tasks/);

    return result;
  }

  async updateTaskStatus(taskId: string, status: string): Promise<boolean> {
    const endpoint = `${this.urls.task}/api/v1/tasks/${taskId}`;
    return this.safeExecute(
      async () => {
        await this.request(endpoint, {
          method: "PATCH",
          data: { status },
        });
        // Invalidate tasks cache
        this.invalidateCache(/\/api\/v1\/tasks/);
        return true;
      },
      false,
      { endpoint, method: "PATCH" },
    );
  }

  async deleteTask(taskId: string): Promise<void> {
    await this.request<void>(`${this.urls.task}/api/v1/tasks/${taskId}`, {
      method: "DELETE",
    });
    // Invalidate tasks cache
    this.invalidateCache(/\/api\/v1\/tasks/);
  }

  async completeTask(taskId: string, evidence?: TaskEvidence): Promise<Task> {
    const result = await this.request<Task>(
      `${this.urls.task}/api/v1/tasks/${taskId}/complete`,
      {
        method: "POST",
        data: evidence || {},
      },
    );
    // Invalidate tasks cache
    this.invalidateCache(/\/api\/v1\/tasks/);
    return result;
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Fields API
  // ─────────────────────────────────────────────────────────────────────────

  async getFields(params?: { farm_id?: string }): Promise<Field[]> {
    const endpoint = `${this.urls.fieldCore}/api/v1/fields`;
    return this.safeExecute(
      () =>
        this.request<Field[]>(endpoint, {
          params,
          cache: { ttl: CacheTTL.MEDIUM },
        }),
      [],
      { endpoint, method: "GET" },
    );
  }

  async getField(fieldId: string): Promise<Field> {
    return this.request<Field>(
      `${this.urls.fieldCore}/api/v1/fields/${fieldId}`,
      { cache: { ttl: CacheTTL.MEDIUM } },
    );
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Farms API
  // ─────────────────────────────────────────────────────────────────────────

  async getFarms(): Promise<Farm[]> {
    const endpoint = `${this.urls.fieldCore}/api/v1/fields`;
    return this.safeExecute(
      async () => {
        const response = await this.request<Field[]>(endpoint, {
          cache: { ttl: CacheTTL.MEDIUM },
        });
        // Map fields to farms format
        return response.map(
          (f): Farm => ({
            id: f.id,
            name: f.name,
            nameAr: f.name_ar,
            ownerId: f.tenant_id || "",
            governorate: "",
            area: f.area_hectares || f.area || 0,
            coordinates: f.coordinates || { lat: 0, lng: 0 },
            crops: [f.crop_type || f.crop || ""],
            status: f.status as "active" | "inactive" | "suspended",
            healthScore: f.health_score || 0,
            lastUpdated: f.updated_at || new Date().toISOString(),
            createdAt: f.created_at || new Date().toISOString(),
          }),
        );
      },
      this.config.enableMockData ? this.generateMockFarms() : [],
      { endpoint, method: "GET" },
    );
  }

  async getFarmById(id: string): Promise<Farm | null> {
    const endpoint = `${this.urls.fieldCore}/api/v1/fields/${id}`;
    return this.safeExecute(
      async () => {
        const field = await this.getField(id);
        return {
          id: field.id,
          name: field.name,
          nameAr: field.name_ar,
          ownerId: field.tenant_id || "",
          governorate: "",
          area: field.area_hectares || field.area || 0,
          coordinates: field.coordinates || { lat: 0, lng: 0 },
          crops: [field.crop_type || field.crop || ""],
          status: field.status as "active" | "inactive" | "suspended",
          healthScore: field.health_score || 0,
          lastUpdated: field.updated_at || new Date().toISOString(),
          createdAt: field.created_at || new Date().toISOString(),
        };
      },
      null,
      { endpoint, method: "GET" },
    );
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Weather API
  // ─────────────────────────────────────────────────────────────────────────

  async getWeather(locationId: string): Promise<WeatherData | null> {
    const endpoint = `${this.urls.weather}/api/v1/weather/current/${locationId}`;
    return this.safeExecute(
      () =>
        this.request<WeatherData>(endpoint, {
          cache: { ttl: CacheTTL.SHORT }, // Weather changes frequently
        }),
      null,
      { endpoint, method: "GET" },
    );
  }

  async getWeatherForecast(
    locationId: string,
    days = 7,
  ): Promise<WeatherForecast | null> {
    const endpoint = `${this.urls.weather}/api/v1/weather/forecast/${locationId}`;
    return this.safeExecute(
      () =>
        this.request<WeatherForecast>(endpoint, {
          params: { days },
          cache: { ttl: CacheTTL.MEDIUM }, // Forecast less volatile
        }),
      null,
      { endpoint, method: "GET" },
    );
  }

  async getWeatherAlerts(): Promise<WeatherAlert[]> {
    const endpoint = `${this.urls.weather}/v1/alerts`;
    return this.safeExecute(
      () =>
        this.request<WeatherAlert[]>(endpoint, {
          cache: { ttl: CacheTTL.VERY_SHORT }, // Alerts need to be fresh
        }),
      [],
      { endpoint, method: "GET" },
    );
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Diagnosis API
  // ─────────────────────────────────────────────────────────────────────────

  async getDiagnoses(params?: {
    status?: string;
    severity?: string;
    farmId?: string;
    governorate?: string;
    limit?: number;
    offset?: number;
  }): Promise<DiagnosisRecord[]> {
    const endpoint = `${this.urls.cropHealth}/v1/diagnoses`;
    return this.safeExecute(
      async () => {
        const response = await this.request<Record<string, unknown>[]>(
          endpoint,
          {
            params: {
              status: params?.status,
              severity: params?.severity,
              governorate: params?.governorate,
              limit: params?.limit || 50,
              offset: params?.offset || 0,
            },
            cache: { ttl: CacheTTL.SHORT },
          },
        );

        return response.map((d) => ({
          id: d.id as string,
          farmId:
            (d.field_id as string) ||
            `farm-${Math.floor(Math.random() * 25) + 1}`,
          farmName: d.governorate ? `مزرعة في ${d.governorate}` : "مزرعة",
          imageUrl: (d.image_url as string) || "/api/placeholder/400/300",
          thumbnailUrl:
            (d.thumbnail_url as string) ||
            (d.image_url as string) ||
            "/api/placeholder/100/100",
          cropType: (d.crop_type as string) || "unknown",
          diseaseId: d.disease_id as string,
          diseaseName: d.disease_name as string,
          diseaseNameAr: d.disease_name_ar as string,
          confidence: (d.confidence as number) * 100,
          severity: d.severity as Severity,
          status: d.status as DiagnosisStatus,
          location: (d.location as { lat: number; lng: number }) || {
            lat: 15.3694,
            lng: 44.191,
          },
          diagnosedAt: d.timestamp as string,
          createdBy: (d.farmer_id as string) || "unknown",
          expertReview: d.expert_notes
            ? {
                expertId: "expert-1",
                expertName: "خبير زراعي",
                notes: d.expert_notes as string,
                reviewedAt: d.updated_at as string,
              }
            : undefined,
        }));
      },
      this.config.enableMockData ? this.generateMockDiagnoses() : [],
      { endpoint, method: "GET" },
    );
  }

  async getDiagnosisStats(): Promise<DiagnosisStats> {
    const endpoint = `${this.urls.cropHealth}/v1/diagnoses/stats`;
    return this.safeExecute(
      async () => {
        const response = await this.request<Record<string, unknown>>(endpoint, {
          cache: { ttl: CacheTTL.SHORT },
        });
        return {
          total: response.total as number,
          pending: response.pending as number,
          confirmed: response.confirmed as number,
          treated: response.treated as number,
          criticalCount: response.critical_count as number,
          highCount: response.high_count as number,
          byDisease: response.by_disease as Record<string, number>,
          byGovernorate: response.by_governorate as Record<string, number>,
        };
      },
      {
        total: 0,
        pending: 0,
        confirmed: 0,
        treated: 0,
        criticalCount: 0,
        highCount: 0,
        byDisease: {},
        byGovernorate: {},
      },
      { endpoint, method: "GET" },
    );
  }

  async updateDiagnosisStatus(
    id: string,
    status: DiagnosisStatus,
    notes?: string,
  ): Promise<{ success: boolean; diagnosis_id: string; status: string }> {
    const endpoint = `${this.urls.cropHealth}/v1/diagnoses/${id}`;
    const result = await this.safeExecute(
      () =>
        this.request(endpoint, {
          method: "PATCH",
          params: { status, expert_notes: notes },
        }),
      { success: true, diagnosis_id: id, status },
      { endpoint, method: "PATCH" },
    );

    // Invalidate diagnoses cache
    this.invalidateCache(/\/v1\/diagnoses/);

    return result;
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Dashboard & Indicators API
  // ─────────────────────────────────────────────────────────────────────────

  async getDashboardStats(): Promise<DashboardStats> {
    const endpoint = `${this.urls.indicators}/v1/dashboard`;
    const mockData = {
      totalFarms: 156,
      activeFarms: 142,
      totalArea: 2450.5,
      totalDiagnoses: 1247,
      pendingReviews: 23,
      criticalAlerts: 5,
      avgHealthScore: 78.5,
      weeklyDiagnoses: 89,
    };
    const emptyData = {
      totalFarms: 0,
      activeFarms: 0,
      totalArea: 0,
      totalDiagnoses: 0,
      pendingReviews: 0,
      criticalAlerts: 0,
      avgHealthScore: 0,
      weeklyDiagnoses: 0,
    };

    return this.safeExecute(
      () =>
        this.request<DashboardStats>(endpoint, {
          cache: { ttl: CacheTTL.SHORT },
        }),
      this.config.enableMockData ? mockData : emptyData,
      { endpoint, method: "GET" },
    );
  }

  async getDashboard(tenantId: string): Promise<DashboardData | null> {
    const endpoint = `${this.urls.indicators}/api/v1/indicators/dashboard/${tenantId}`;
    return this.safeExecute(
      () =>
        this.request<DashboardData>(endpoint, {
          cache: { ttl: CacheTTL.SHORT },
        }),
      null,
      { endpoint, method: "GET" },
    );
  }

  async getFieldIndicators(fieldId: string): Promise<FieldIndicators | null> {
    const endpoint = `${this.urls.indicators}/api/v1/indicators/field/${fieldId}`;
    return this.safeExecute(
      () =>
        this.request<FieldIndicators>(endpoint, {
          cache: { ttl: CacheTTL.SHORT },
        }),
      null,
      { endpoint, method: "GET" },
    );
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Sensors & Equipment API
  // ─────────────────────────────────────────────────────────────────────────

  async getSensorReadings(farmId: string): Promise<SensorReading[]> {
    const endpoint = `${this.urls.virtualSensors}/v1/readings/${farmId}`;
    return this.safeExecute(
      () =>
        this.request<SensorReading[]>(endpoint, {
          cache: { ttl: CacheTTL.VERY_SHORT }, // Sensor data is real-time
        }),
      [],
      { endpoint, method: "GET" },
    );
  }

  async getEquipment(params?: {
    type?: string;
    status?: string;
  }): Promise<Equipment[]> {
    const endpoint = `${this.urls.equipment}/api/v1/equipment`;
    return this.safeExecute(
      () =>
        this.request<Equipment[]>(endpoint, {
          params,
          cache: { ttl: CacheTTL.MEDIUM },
        }),
      [],
      { endpoint, method: "GET" },
    );
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Notifications API
  // ─────────────────────────────────────────────────────────────────────────

  async getNotifications(params?: {
    type?: string;
    priority?: string;
    limit?: number;
  }): Promise<Notification[]> {
    const endpoint = `${this.urls.notifications}/v1/notifications`;
    return this.safeExecute(
      () =>
        this.request<Notification[]>(endpoint, {
          params,
          cache: { ttl: CacheTTL.VERY_SHORT }, // Notifications should be fresh
        }),
      [],
      { endpoint, method: "GET" },
    );
  }

  async markNotificationRead(id: string): Promise<boolean> {
    const endpoint = `${this.urls.notifications}/v1/notifications/${id}/read`;
    const result = await this.safeExecute(
      async () => {
        await this.request(endpoint, { method: "PATCH" });
        return true;
      },
      false,
      { endpoint, method: "PATCH" },
    );

    // Invalidate notifications cache
    this.invalidateCache(/\/v1\/notifications/);

    return result;
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Community API
  // ─────────────────────────────────────────────────────────────────────────

  async getCommunityPosts(params?: {
    category?: string;
    limit?: number;
  }): Promise<CommunityPost[]> {
    const endpoint = `${this.urls.community}/api/v1/posts`;
    return this.safeExecute(
      () =>
        this.request<CommunityPost[]>(endpoint, {
          params,
          cache: { ttl: CacheTTL.SHORT },
        }),
      [],
      { endpoint, method: "GET" },
    );
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Health Check
  // ─────────────────────────────────────────────────────────────────────────

  async health(): Promise<{ status: string }> {
    return this.request<{ status: string }>(`${this.urls.fieldCore}/healthz`, {
      cache: false, // Never cache health checks
    });
  }

  async checkServicesHealth(): Promise<Record<string, boolean>> {
    const services = Object.entries(this.urls);
    const results: Record<string, boolean> = {};

    await Promise.all(
      services.map(async ([name, url]) => {
        try {
          await this.client.get(`${url}/healthz`, {
            timeout: 5000,
            cache: false,
          } as AxiosRequestConfig);
          results[name] = true;
          this.log("debug", `Service health check passed: ${name}`, { url });
        } catch (error) {
          results[name] = false;
          this.log("warn", `Service health check failed: ${name}`, {
            url,
            error: error instanceof Error ? error.message : "Unknown error",
          });
        }
      }),
    );

    return results;
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Paginated Requests Helper
  // ─────────────────────────────────────────────────────────────────────────

  /**
   * Fetch all pages of a paginated endpoint
   */
  async fetchAllPages<T>(
    endpoint: string,
    params: Record<string, unknown> = {},
    options?: {
      pageSize?: number;
      maxPages?: number;
      onProgress?: (loaded: number, total: number) => void;
    },
  ): Promise<T[]> {
    const pageSize = options?.pageSize || 50;
    const maxPages = options?.maxPages || 100;
    const allItems: T[] = [];
    let page = 1;
    let hasMore = true;

    while (hasMore && page <= maxPages) {
      const response = await this.request<PaginatedResponse<T>>(endpoint, {
        params: {
          ...params,
          page,
          limit: pageSize,
        },
      });

      allItems.push(...response.data);
      hasMore = response.hasMore;
      page += 1;

      if (options?.onProgress) {
        options.onProgress(allItems.length, response.total);
      }
    }

    return allItems;
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Mock Data Generators
  // ─────────────────────────────────────────────────────────────────────────

  private generateMockFarms(): Farm[] {
    const governorates = [
      "sanaa",
      "taiz",
      "ibb",
      "hadramaut",
      "hodeidah",
      "dhamar",
    ] as const;
    const crops = [
      "wheat",
      "coffee",
      "qat",
      "date_palm",
      "mango",
      "banana",
      "sorghum",
    ] as const;

    return Array.from({ length: 25 }, (_, i) => ({
      id: `farm-${i + 1}`,
      name: `Farm ${i + 1}`,
      nameAr: `مزرعة ${i + 1}`,
      ownerId: `user-${Math.floor(Math.random() * 10) + 1}`,
      governorate:
        governorates[Math.floor(Math.random() * governorates.length)] ??
        "sanaa",
      district: "District",
      area: Math.random() * 50 + 5,
      coordinates: {
        lat: 13.5 + Math.random() * 3,
        lng: 43.5 + Math.random() * 5,
      },
      crops: [crops[Math.floor(Math.random() * crops.length)] ?? "wheat"],
      status: "active" as const,
      healthScore: Math.floor(Math.random() * 40) + 60,
      lastUpdated: new Date().toISOString(),
      createdAt: new Date(
        Date.now() - Math.random() * 90 * 24 * 60 * 60 * 1000,
      ).toISOString(),
    }));
  }

  private generateMockDiagnoses(): DiagnosisRecord[] {
    const diseases = [
      {
        id: "tomato_late_blight",
        name: "Late Blight",
        nameAr: "اللفحة المتأخرة",
      },
      {
        id: "tomato_early_blight",
        name: "Early Blight",
        nameAr: "اللفحة المبكرة",
      },
      {
        id: "powdery_mildew",
        name: "Powdery Mildew",
        nameAr: "البياض الدقيقي",
      },
      {
        id: "bacterial_spot",
        name: "Bacterial Spot",
        nameAr: "التبقع البكتيري",
      },
    ] as const;
    const defaultDisease = diseases[0];
    const severities: Severity[] = ["low", "medium", "high", "critical"];
    const statuses: DiagnosisStatus[] = [
      "pending",
      "confirmed",
      "rejected",
      "treated",
    ];

    return Array.from({ length: 20 }, (_, i) => {
      const disease =
        diseases[Math.floor(Math.random() * diseases.length)] ?? defaultDisease;
      return {
        id: `diag-${i + 1}`,
        farmId: `farm-${Math.floor(Math.random() * 25) + 1}`,
        farmName: `مزرعة ${Math.floor(Math.random() * 25) + 1}`,
        imageUrl: `/api/placeholder/400/300`,
        thumbnailUrl: `/api/placeholder/100/100`,
        cropType: "tomato",
        diseaseId: disease.id,
        diseaseName: disease.name,
        diseaseNameAr: disease.nameAr,
        confidence: Math.random() * 30 + 70,
        severity:
          severities[Math.floor(Math.random() * severities.length)] ?? "medium",
        status:
          statuses[Math.floor(Math.random() * statuses.length)] ?? "pending",
        location: {
          lat: 13.5 + Math.random() * 3,
          lng: 43.5 + Math.random() * 5,
        },
        diagnosedAt: new Date(
          Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000,
        ).toISOString(),
        createdBy: `user-${Math.floor(Math.random() * 10) + 1}`,
      };
    });
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Factory Function
// ─────────────────────────────────────────────────────────────────────────────

export function createApiClient(
  config: EnhancedApiClientConfig,
): SahoolApiClient {
  return new SahoolApiClient(config);
}

// ─────────────────────────────────────────────────────────────────────────────
// Convenience Factory Functions
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Create API client with aggressive caching (good for offline-first)
 */
export function createOfflineFirstClient(
  config: ApiClientConfig,
): SahoolApiClient {
  return new SahoolApiClient({
    ...config,
    cache: "offline",
    retry: {
      maxRetries: 5,
      initialDelay: 2000,
    },
  });
}

/**
 * Create API client optimized for real-time data
 */
export function createRealtimeClient(config: ApiClientConfig): SahoolApiClient {
  return new SahoolApiClient({
    ...config,
    cache: "conservative",
    retry: {
      maxRetries: 2,
      initialDelay: 500,
    },
  });
}

/**
 * Create minimal API client without advanced features
 */
export function createMinimalClient(config: ApiClientConfig): SahoolApiClient {
  return new SahoolApiClient({
    ...config,
    cache: false,
    retry: false,
    circuitBreaker: false,
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// Default Export
// ─────────────────────────────────────────────────────────────────────────────

export default SahoolApiClient;
