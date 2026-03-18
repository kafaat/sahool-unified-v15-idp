// ═══════════════════════════════════════════════════════════════════════════════
// SAHOOL Unified API Client
// عميل API الموحد لمنصة سهول
// ═══════════════════════════════════════════════════════════════════════════════

import axios, { AxiosInstance, AxiosRequestConfig, AxiosError, type AxiosResponse, InternalAxiosRequestConfig } from "axios";
import type {
  ApiClientConfig,
  RetryConfig,
  TokenRefreshConfig,
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
} from "./types";
import { ApiError, parseAxiosError } from "./errors";

// Import unified contracts - استيراد العقود الموحدة
import { SERVICE_PORT_ALIASES, CUSTOM_HEADERS } from "@sahool/shared-types/contracts";

// Re-export all types
export * from "./types";
// Re-export all errors
export * from "./errors";

// ─────────────────────────────────────────────────────────────────────────────
// Default Configuration (from unified contracts)
// Ports sourced from @sahool/shared-types/contracts/service-ports.ts
// ─────────────────────────────────────────────────────────────────────────────

const DEFAULT_PORTS: ServicePorts = {
  ...SERVICE_PORT_ALIASES,
};

// ─────────────────────────────────────────────────────────────────────────────
// SAHOOL API Client Class
// ─────────────────────────────────────────────────────────────────────────────

export class SahoolApiClient {
  private client: AxiosInstance;
  private config: ApiClientConfig;
  private ports: ServicePorts;
  private isProduction: boolean;
  private logLevel: LogLevel;
  private errorHandling: "throw" | "silent";
  private retryConfig: Required<RetryConfig>;
  private tokenRefreshConfig: TokenRefreshConfig | null;
  private enforceHttps: boolean;
  private isRefreshing: boolean = false;
  private refreshSubscribers: Array<(token: string | null) => void> = [];
  private tenantId: string | null = null;

  // ─────────────────────────────────────────────────────────────────────────
  // Default retry configuration
  // ─────────────────────────────────────────────────────────────────────────

  private static readonly DEFAULT_RETRY_CONFIG: Required<RetryConfig> = {
    maxRetries: 3,
    baseDelay: 1000,
    maxDelay: 30000,
    retryableStatuses: [408, 429, 500, 502, 503, 504],
    retryOnNetworkError: true,
  };

  constructor(config: ApiClientConfig, ports: Partial<ServicePorts> = {}) {
    this.config = {
      timeout: 30000,
      locale: "ar",
      enableMockData: false,
      errorHandling: "throw",
      logLevel: "error",
      ...config,
    };
    this.ports = { ...DEFAULT_PORTS, ...ports };
    this.isProduction = process.env.NODE_ENV === "production";
    this.logLevel = this.config.logLevel || "error";
    this.errorHandling = this.config.errorHandling || "throw";

    // Retry configuration - defaults enabled unless explicitly set to false
    if (this.config.retry === false) {
      this.retryConfig = { ...SahoolApiClient.DEFAULT_RETRY_CONFIG, maxRetries: 0 };
    } else {
      this.retryConfig = {
        ...SahoolApiClient.DEFAULT_RETRY_CONFIG,
        ...(this.config.retry || {}),
      };
    }

    // Token refresh configuration
    this.tokenRefreshConfig = this.config.tokenRefresh || null;

    // HTTPS enforcement - defaults to true
    this.enforceHttps = this.config.enforceHttps !== false;

    // Enforce HTTPS on baseUrl in production
    const baseUrl = this.enforceHttps
      ? this.upgradeToHttps(this.config.baseUrl)
      : this.config.baseUrl;
    this.config.baseUrl = baseUrl;

    // Create axios instance
    this.client = axios.create({
      timeout: this.config.timeout,
      withCredentials: this.config.withCredentials ?? false,
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
        "Accept-Language": `${this.config.locale},en`,
      },
    });

    // Setup interceptors
    this.setupInterceptors();
  }

  private setupInterceptors(): void {
    // Request interceptor - add auth token, request ID, tenant ID, and enforce HTTPS
    this.client.interceptors.request.use((config: InternalAxiosRequestConfig) => {
      // Enforce HTTPS on outgoing request URLs in production
      if (this.enforceHttps && config.url) {
        config.url = this.upgradeToHttps(config.url);
      }

      // Add unique request ID for traceability (preserve caller-provided ID)
      if (!config.headers.has(CUSTOM_HEADERS.REQUEST_ID)) {
        config.headers.set(CUSTOM_HEADERS.REQUEST_ID, crypto.randomUUID());
      }

      const token = this.config.getToken?.();
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }

      // Add tenant ID header for multi-tenant isolation
      if (this.tenantId) {
        config.headers[CUSTOM_HEADERS.TENANT_ID] = this.tenantId;
      }

      return config;
    });

    // Response interceptor - handle 401 with token refresh, then fallback
    this.client.interceptors.response.use(
      (response: AxiosResponse) => response,
      async (error: AxiosError) => {
        const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

        // Only attempt token refresh on 401 if:
        // 1. We have a tokenRefresh config
        // 2. This request hasn't already been retried for auth
        // 3. The response status is 401
        if (
          error.response?.status === 401 &&
          this.tokenRefreshConfig &&
          originalRequest &&
          !originalRequest._retry
        ) {
          originalRequest._retry = true;

          // If a refresh is already in progress, queue this request
          if (this.isRefreshing) {
            return new Promise<AxiosResponse>((resolve, reject) => {
              this.refreshSubscribers.push((newToken: string | null) => {
                if (newToken) {
                  originalRequest.headers.Authorization = `Bearer ${newToken}`;
                  resolve(this.client.request(originalRequest));
                } else {
                  reject(error);
                }
              });
            });
          }

          this.isRefreshing = true;

          try {
            const maxAttempts = this.tokenRefreshConfig.maxRefreshAttempts ?? 1;
            let newToken: string | null = null;

            for (let attempt = 0; attempt < maxAttempts; attempt++) {
              newToken = await this.tokenRefreshConfig.refreshToken();
              if (newToken) break;
            }

            if (newToken) {
              // Store the new token
              this.config.setToken?.(newToken);
              this.log("info", "Token refreshed successfully");

              // Retry the original request with the new token
              originalRequest.headers.Authorization = `Bearer ${newToken}`;

              // Notify all queued subscribers
              this.refreshSubscribers.forEach((cb) => cb(newToken));
              this.refreshSubscribers = [];

              return this.client.request(originalRequest);
            }

            // Refresh failed - notify subscribers and call onUnauthorized
            this.refreshSubscribers.forEach((cb) => cb(null));
            this.refreshSubscribers = [];
            this.log("warn", "Token refresh failed, calling onUnauthorized");
            this.config.onUnauthorized?.();
            return Promise.reject(error);
          } catch (refreshError) {
            this.refreshSubscribers.forEach((cb) => cb(null));
            this.refreshSubscribers = [];
            this.log("error", "Token refresh threw an error", {
              error: refreshError instanceof Error ? refreshError.message : "Unknown",
            });
            this.config.onUnauthorized?.();
            return Promise.reject(error);
          } finally {
            this.isRefreshing = false;
          }
        }

        // For non-401 errors or when no token refresh is configured,
        // call onUnauthorized directly for 401s
        if (error.response?.status === 401 && !this.tokenRefreshConfig) {
          this.config.onUnauthorized?.();
        }

        return Promise.reject(error);
      },
    );
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
      }
      // In throw mode, let handleError do its job
      return this.handleError(error, context?.endpoint, context?.method);
    }
  }

  // ─────────────────────────────────────────────────────────────────────────
  // HTTPS Enforcement
  // فرض HTTPS للاتصالات الآمنة
  // ─────────────────────────────────────────────────────────────────────────

  /**
   * Upgrade an HTTP URL to HTTPS in production environments.
   * In non-production (development/test), localhost and private IPs are exempted.
   * ترقية عنوان URL من HTTP إلى HTTPS في بيئات الإنتاج
   */
  private upgradeToHttps(url: string): string {
    if (!url) return url;

    // Only upgrade URLs that start with http://
    if (!url.startsWith("http://")) return url;

    // In production, always upgrade to HTTPS
    if (this.isProduction) {
      return url.replace(/^http:\/\//, "https://");
    }

    // In non-production, skip localhost and private IPs
    const exemptPatterns = [
      /^http:\/\/localhost([:\/]|$)/,
      /^http:\/\/127\.0\.0\.1([:\/]|$)/,
      /^http:\/\/0\.0\.0\.0([:\/]|$)/,
      /^http:\/\/10\.\d{1,3}\.\d{1,3}\.\d{1,3}([:\/]|$)/,
      /^http:\/\/172\.(1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}([:\/]|$)/,
      /^http:\/\/192\.168\.\d{1,3}\.\d{1,3}([:\/]|$)/,
    ];

    const isExempt = exemptPatterns.some((pattern) => pattern.test(url));
    if (isExempt) return url;

    // Non-production, non-exempt: still upgrade to HTTPS
    return url.replace(/^http:\/\//, "https://");
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
      soilAnalysis: this.getServiceUrl(this.ports.soilAnalysis),
      drone: this.getServiceUrl(this.ports.drone),
      cooperative: this.getServiceUrl(this.ports.cooperative),
      traceability: this.getServiceUrl(this.ports.traceability),
      // Extended service URLs
      advisory: this.getServiceUrl(this.ports.advisory),
      yieldPrediction: this.getServiceUrl(this.ports.yieldPrediction),
      fieldIntelligence: this.getServiceUrl(this.ports.fieldIntelligence),
      billing: this.getServiceUrl(this.ports.billing),
      astronomicalCalendar: this.getServiceUrl(this.ports.astronomicalCalendar),
      alerts: this.getServiceUrl(this.ports.alerts),
      cropIntelligence: this.getServiceUrl(this.ports.cropIntelligence),
      yoloVision: this.getServiceUrl(this.ports.yoloVision),
      audit: this.getServiceUrl(this.ports.audit),
    };
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Retry Logic with Exponential Backoff
  // منطق إعادة المحاولة مع التأخير الأسي
  // ─────────────────────────────────────────────────────────────────────────

  /**
   * Determine whether a failed request should be retried.
   * Checks HTTP status codes and network errors against the retry config.
   */
  private isRetryable(error: unknown): boolean {
    if (this.retryConfig.maxRetries <= 0) return false;

    if (axios.isAxiosError(error)) {
      // Network error (no response received) - e.g. ECONNRESET, DNS failure
      if (!error.response) {
        return this.retryConfig.retryOnNetworkError;
      }

      // Check if the HTTP status code is in the retryable list
      return this.retryConfig.retryableStatuses.includes(error.response.status);
    }

    return false;
  }

  /**
   * Calculate the delay before the next retry using exponential backoff with jitter.
   * Formula: min(maxDelay, baseDelay * 2^attempt) + random jitter
   * حساب التأخير قبل إعادة المحاولة التالية
   */
  private getRetryDelay(attempt: number, error?: unknown): number {
    // If the server sent a Retry-After header (common for 429), respect it
    if (axios.isAxiosError(error) && error.response?.headers?.["retry-after"]) {
      const retryAfter = error.response.headers["retry-after"];
      const retryAfterSeconds = parseInt(retryAfter as string, 10);
      if (!isNaN(retryAfterSeconds) && retryAfterSeconds > 0) {
        return Math.min(retryAfterSeconds * 1000, this.retryConfig.maxDelay);
      }
    }

    // Exponential backoff: baseDelay * 2^attempt
    const exponentialDelay = this.retryConfig.baseDelay * Math.pow(2, attempt);

    // Cap at maxDelay
    const cappedDelay = Math.min(exponentialDelay, this.retryConfig.maxDelay);

    // Add random jitter (0-25% of the delay) to avoid thundering herd
    const jitter = cappedDelay * Math.random() * 0.25;

    return Math.floor(cappedDelay + jitter);
  }

  /**
   * Sleep for a specified duration in milliseconds.
   */
  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Generic Request Method (with retry)
  // ─────────────────────────────────────────────────────────────────────────

  private async request<T>(
    url: string,
    options: AxiosRequestConfig = {},
  ): Promise<T> {
    const method = options.method?.toUpperCase() || "GET";
    let lastError: unknown;

    // Attempt the request up to (1 + maxRetries) times
    for (let attempt = 0; attempt <= this.retryConfig.maxRetries; attempt++) {
      try {
        if (attempt > 0) {
          this.log("info", `Retry attempt ${attempt}/${this.retryConfig.maxRetries}: ${method} ${url}`, {
            attempt,
            maxRetries: this.retryConfig.maxRetries,
          });
        } else {
          this.log("debug", `Request: ${method} ${url}`, {
            params: options.params,
            data: options.data,
          });
        }

        const response = await this.client.request<T>({ url, ...options });

        this.log("debug", `Response: ${method} ${url}`, {
          status: response.status,
          statusText: response.statusText,
        });

        return response.data;
      } catch (error) {
        lastError = error;

        // Check if we should retry
        const hasMoreAttempts = attempt < this.retryConfig.maxRetries;
        if (hasMoreAttempts && this.isRetryable(error)) {
          const delay = this.getRetryDelay(attempt, error);
          this.log("warn", `Request failed, retrying in ${delay}ms: ${method} ${url}`, {
            attempt: attempt + 1,
            maxRetries: this.retryConfig.maxRetries,
            delay,
            error: error instanceof Error ? error.message : "Unknown error",
            status: axios.isAxiosError(error) ? error.response?.status : undefined,
          });
          await this.sleep(delay);
          continue;
        }

        // No more retries or not retryable - throw
        break;
      }
    }

    return this.handleError(lastError, url, method);
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Auth Token Management
  // ─────────────────────────────────────────────────────────────────────────

  setToken(token: string): void {
    this.config.setToken?.(token);
  }

  setTenantId(tenantId: string): void {
    this.tenantId = tenantId;
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
      () => this.request<Task[]>(endpoint, { params }),
      [],
      { endpoint, method: "GET" },
    );
  }

  async getTask(taskId: string): Promise<Task> {
    return this.request<Task>(`${this.urls.task}/api/v1/tasks/${taskId}`);
  }

  async createTask(task: CreateTaskRequest): Promise<Task> {
    return this.request<Task>(`${this.urls.task}/api/v1/tasks`, {
      method: "POST",
      data: task,
    });
  }

  async updateTask(
    taskId: string,
    data: Partial<CreateTaskRequest>,
  ): Promise<Task> {
    return this.request<Task>(`${this.urls.task}/api/v1/tasks/${taskId}`, {
      method: "PUT",
      data,
    });
  }

  async updateTaskStatus(taskId: string, status: string): Promise<boolean> {
    const endpoint = `${this.urls.task}/api/v1/tasks/${taskId}`;
    return this.safeExecute(
      async () => {
        await this.request(endpoint, {
          method: "PATCH",
          data: { status },
        });
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
  }

  async completeTask(taskId: string, evidence?: TaskEvidence): Promise<Task> {
    return this.request<Task>(
      `${this.urls.task}/api/v1/tasks/${taskId}/complete`,
      {
        method: "POST",
        data: evidence || {},
      },
    );
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Fields API
  // ─────────────────────────────────────────────────────────────────────────

  async getFields(params?: { farm_id?: string }): Promise<Field[]> {
    const endpoint = `${this.urls.fieldCore}/api/v1/fields`;
    return this.safeExecute(
      () => this.request<Field[]>(endpoint, { params }),
      [],
      { endpoint, method: "GET" },
    );
  }

  async getField(fieldId: string): Promise<Field> {
    return this.request<Field>(
      `${this.urls.fieldCore}/api/v1/fields/${fieldId}`,
    );
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Farms API
  // ─────────────────────────────────────────────────────────────────────────

  async getFarms(): Promise<Farm[]> {
    const endpoint = `${this.urls.fieldCore}/api/v1/fields`;
    return this.safeExecute(
      async () => {
        const response = await this.request<Field[]>(endpoint);
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
    return this.safeExecute(() => this.request<WeatherData>(endpoint), null, {
      endpoint,
      method: "GET",
    });
  }

  async getWeatherForecast(
    locationId: string,
    days = 7,
  ): Promise<WeatherForecast | null> {
    const endpoint = `${this.urls.weather}/api/v1/weather/forecast/${locationId}`;
    return this.safeExecute(
      () => this.request<WeatherForecast>(endpoint, { params: { days } }),
      null,
      { endpoint, method: "GET" },
    );
  }

  async getWeatherAlerts(): Promise<WeatherAlert[]> {
    const endpoint = `${this.urls.weather}/v1/alerts`;
    return this.safeExecute(() => this.request<WeatherAlert[]>(endpoint), [], {
      endpoint,
      method: "GET",
    });
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
        const response = await this.request<Record<string, unknown>>(endpoint);
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
    return this.safeExecute(
      () =>
        this.request(endpoint, {
          method: "PATCH",
          params: { status, expert_notes: notes },
        }),
      { success: true, diagnosis_id: id, status },
      { endpoint, method: "PATCH" },
    );
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
      () => this.request<DashboardStats>(endpoint),
      this.config.enableMockData ? mockData : emptyData,
      { endpoint, method: "GET" },
    );
  }

  async getDashboard(tenantId: string): Promise<DashboardData | null> {
    const endpoint = `${this.urls.indicators}/api/v1/indicators/dashboard/${tenantId}`;
    return this.safeExecute(() => this.request<DashboardData>(endpoint), null, {
      endpoint,
      method: "GET",
    });
  }

  async getFieldIndicators(fieldId: string): Promise<FieldIndicators | null> {
    const endpoint = `${this.urls.indicators}/api/v1/indicators/field/${fieldId}`;
    return this.safeExecute(
      () => this.request<FieldIndicators>(endpoint),
      null,
      { endpoint, method: "GET" },
    );
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Sensors & Equipment API
  // ─────────────────────────────────────────────────────────────────────────

  async getSensorReadings(farmId: string): Promise<SensorReading[]> {
    const endpoint = `${this.urls.virtualSensors}/v1/readings/${farmId}`;
    return this.safeExecute(() => this.request<SensorReading[]>(endpoint), [], {
      endpoint,
      method: "GET",
    });
  }

  async getEquipment(params?: {
    type?: string;
    status?: string;
  }): Promise<Equipment[]> {
    const endpoint = `${this.urls.equipment}/api/v1/equipment`;
    return this.safeExecute(
      () => this.request<Equipment[]>(endpoint, { params }),
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
      () => this.request<Notification[]>(endpoint, { params }),
      [],
      { endpoint, method: "GET" },
    );
  }

  async markNotificationRead(id: string): Promise<boolean> {
    const endpoint = `${this.urls.notifications}/v1/notifications/${id}/read`;
    return this.safeExecute(
      async () => {
        await this.request(endpoint, { method: "PATCH" });
        return true;
      },
      false,
      { endpoint, method: "PATCH" },
    );
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
      () => this.request<CommunityPost[]>(endpoint, { params }),
      [],
      { endpoint, method: "GET" },
    );
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Satellite / Vegetation Analysis API
  // تحليل الأقمار الصناعية
  // ─────────────────────────────────────────────────────────────────────────

  async getSatelliteTimeseries(
    fieldId: string,
    options?: { from?: string; to?: string },
  ): Promise<unknown[]> {
    const endpoint = `${this.urls.satellite}/v1/timeseries/${fieldId}`;
    return this.safeExecute(
      () => this.request<unknown[]>(endpoint, { params: options }),
      [],
      { endpoint, method: "GET" },
    );
  }

  async requestSatelliteAnalysis(
    fieldId: string,
    analysisType: "ndvi" | "moisture" | "thermal",
  ): Promise<unknown | null> {
    const endpoint = `${this.urls.satellite}/v1/analyze`;
    return this.safeExecute(
      () =>
        this.request(endpoint, {
          method: "POST",
          data: { field_id: fieldId, analysis_type: analysisType },
        }),
      null,
      { endpoint, method: "POST" },
    );
  }

  async getSatelliteIndices(fieldId: string): Promise<unknown | null> {
    const endpoint = `${this.urls.satellite}/v1/indices/${fieldId}`;
    return this.safeExecute(() => this.request(endpoint), null, {
      endpoint,
      method: "GET",
    });
  }

  async getAvailableSatellites(): Promise<{ satellites: unknown[] }> {
    const endpoint = `${this.urls.satellite}/v1/satellites`;
    return this.safeExecute(
      () => this.request(endpoint),
      { satellites: [] },
      { endpoint, method: "GET" },
    );
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Dashboard Analytics API
  // بيانات تحليلية للرسوم البيانية
  // ─────────────────────────────────────────────────────────────────────────

  async getYieldTrends(
    period: "7d" | "30d" | "90d" = "30d",
  ): Promise<Array<{ month: string; yield: number; forecast: number }>> {
    const endpoint = `${this.urls.indicators}/v1/trends`;
    return this.safeExecute(
      async () => {
        const response = await this.request<{ data?: unknown[] }>(endpoint, {
          params: { metric: "yield", period },
        });
        return (response?.data || []) as Array<{
          month: string;
          yield: number;
          forecast: number;
        }>;
      },
      [],
      { endpoint, method: "GET" },
    );
  }

  async getCropDistribution(): Promise<
    Array<{ name: string; value: number }>
  > {
    const endpoint = `${this.urls.indicators}/v1/dashboard`;
    return this.safeExecute(
      async () => {
        const response = await this.request<{
          crop_distribution?: Array<{ crop: string; area: number }>;
        }>(endpoint);
        return (
          response?.crop_distribution?.map(
            (c: { crop: string; area: number }) => ({
              name: c.crop,
              value: c.area,
            }),
          ) || []
        );
      },
      [],
      { endpoint, method: "GET" },
    );
  }

  async getWeeklyActivity(): Promise<
    Array<{
      day: string;
      diagnoses: number;
      irrigations: number;
      alerts: number;
    }>
  > {
    const endpoint = `${this.urls.indicators}/v1/trends`;
    return this.safeExecute(
      async () => {
        const response = await this.request<{ data?: unknown[] }>(endpoint, {
          params: { metric: "weekly_activity", period: "7d" },
        });
        return (response?.data || []) as Array<{
          day: string;
          diagnoses: number;
          irrigations: number;
          alerts: number;
        }>;
      },
      [],
      { endpoint, method: "GET" },
    );
  }

  async getPlatformMetrics(): Promise<{
    activeFarmers: number;
    dailySales: number;
    irrigationOps: number;
    avgTemperature: number;
    monthlyGrowthRate: number;
  }> {
    const endpoint = `${this.urls.indicators}/v1/dashboard`;
    const fallback = {
      activeFarmers: 0,
      dailySales: 0,
      irrigationOps: 0,
      avgTemperature: 0,
      monthlyGrowthRate: 0,
    };
    return this.safeExecute(
      async () => {
        const data = await this.request<Record<string, unknown>>(endpoint);
        return {
          activeFarmers: (data?.active_users as number) || 0,
          dailySales: (data?.daily_sales as number) || 0,
          irrigationOps: (data?.pending_tasks as number) || 0,
          avgTemperature: (data?.avg_temperature as number) || 0,
          monthlyGrowthRate: (data?.monthly_growth_rate as number) || 0,
        };
      },
      fallback,
      { endpoint, method: "GET" },
    );
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Advisory & Intelligence API
  // ─────────────────────────────────────────────────────────────────────────

  async getAdvisoryRecommendations(
    fieldId: string,
    cropType?: string,
  ): Promise<{ recommendations: unknown[]; sources: unknown[] }> {
    const endpoint = `${this.urls.advisory}/api/v1/advisory/recommendations`;
    return this.safeExecute(
      () =>
        this.request(endpoint, {
          method: "POST",
          data: { field_id: fieldId, crop_type: cropType },
        }),
      { recommendations: [], sources: [] },
      { endpoint, method: "POST" },
    );
  }

  async getYieldPrediction(
    fieldId: string,
    cropType: string,
  ): Promise<unknown | null> {
    const endpoint = `${this.urls.yieldPrediction}/api/v1/yield/predict`;
    return this.safeExecute(
      () =>
        this.request(endpoint, {
          method: "POST",
          data: { field_id: fieldId, crop_type: cropType },
        }),
      null,
      { endpoint, method: "POST" },
    );
  }

  async getFieldIntelligence(fieldId: string): Promise<unknown | null> {
    const endpoint = `${this.urls.fieldIntelligence}/api/v1/field-intelligence/${fieldId}`;
    return this.safeExecute(() => this.request(endpoint), null, {
      endpoint,
      method: "GET",
    });
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Alerts API
  // ─────────────────────────────────────────────────────────────────────────

  async getAlerts(params?: {
    severity?: string;
    type?: string;
    acknowledged?: boolean;
    limit?: number;
  }): Promise<{ data: unknown[]; meta: { total: number; page: number; limit: number } }> {
    const endpoint = `${this.urls.alerts}/api/v1/alerts`;
    return this.safeExecute(
      () => this.request(endpoint, { params }),
      { data: [], meta: { total: 0, page: 1, limit: 20 } },
      { endpoint, method: "GET" },
    );
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Billing API
  // ─────────────────────────────────────────────────────────────────────────

  async getBillingSubscription(): Promise<unknown | null> {
    const endpoint = `${this.urls.billing}/api/v1/billing/subscription`;
    return this.safeExecute(() => this.request(endpoint), null, {
      endpoint,
      method: "GET",
    });
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Astronomical Calendar API
  // ─────────────────────────────────────────────────────────────────────────

  async getAstronomicalToday(
    lat?: number,
    lon?: number,
  ): Promise<unknown | null> {
    const endpoint = `${this.urls.astronomicalCalendar}/api/v1/astronomical/today`;
    return this.safeExecute(
      () => this.request(endpoint, { params: { lat, lon } }),
      null,
      { endpoint, method: "GET" },
    );
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Image Upload API (FormData)
  // رفع الصور عبر FormData
  // ─────────────────────────────────────────────────────────────────────────

  async uploadImage(
    url: string,
    formData: FormData,
    timeout?: number,
  ): Promise<unknown> {
    return this.client.post(url, formData, {
      headers: { "Content-Type": "multipart/form-data" },
      timeout: timeout || 120000,
    }).then((r) => r.data);
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Vision Detection API
  // ─────────────────────────────────────────────────────────────────────────

  async detectVision(
    task: "pest" | "disease" | "weed",
    formData: FormData,
    timeout?: number,
  ): Promise<{
    detections: Array<{
      class: string;
      confidence: number;
      bbox: [number, number, number, number];
    }>;
    imageUrl?: string;
    processingTime?: number;
  }> {
    const endpoint = `${this.urls.yoloVision}/api/v1/detect/${task}`;
    return this.client
      .post(endpoint, formData, {
        headers: { "Content-Type": "multipart/form-data" },
        timeout: timeout || 180000,
      })
      .then((r) => r.data);
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Weather by Location API (direct service access)
  // ─────────────────────────────────────────────────────────────────────────

  async getWeatherByLocation(locationId: string): Promise<unknown | null> {
    const endpoint = `${this.urls.weather}/v1/current/${locationId}`;
    return this.safeExecute(() => this.request(endpoint), null, {
      endpoint,
      method: "GET",
    });
  }

  async getWeatherForecastByLocation(
    locationId: string,
    days = 7,
  ): Promise<unknown | null> {
    const endpoint = `${this.urls.weather}/v1/forecast/${locationId}`;
    return this.safeExecute(
      () => this.request(endpoint, { params: { days } }),
      null,
      { endpoint, method: "GET" },
    );
  }

  async getWeatherLocations(): Promise<{ locations: unknown[] }> {
    const endpoint = `${this.urls.weather}/v1/locations`;
    return this.safeExecute(
      () => this.request(endpoint),
      { locations: [] },
      { endpoint, method: "GET" },
    );
  }

  async getWeatherAlertsByLocation(
    locationId: string = "sanaa",
  ): Promise<WeatherAlert[]> {
    const endpoint = `${this.urls.weather}/v1/alerts/${locationId}`;
    return this.safeExecute(
      async () => {
        const response = await this.request<{ alerts?: WeatherAlert[] }>(
          endpoint,
        );
        return response?.alerts || [];
      },
      [],
      { endpoint, method: "GET" },
    );
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Generic Request Access (for custom endpoints)
  // وصول عام للطلبات المخصصة
  // ─────────────────────────────────────────────────────────────────────────

  /**
   * Expose the underlying axios instance for advanced use cases
   * (e.g., custom endpoints, FormData uploads).
   * يتيح الوصول لمثيل axios للحالات المتقدمة
   */
  get axiosInstance(): AxiosInstance {
    return this.client;
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Health Check
  // ─────────────────────────────────────────────────────────────────────────

  async health(): Promise<{ status: string }> {
    return this.request<{ status: string }>(`${this.urls.fieldCore}/healthz`);
  }

  async checkServicesHealth(): Promise<Record<string, boolean>> {
    const services = Object.entries(this.urls);
    const results: Record<string, boolean> = {};

    await Promise.all(
      services.map(async ([name, url]) => {
        try {
          await this.client.get(`${url}/healthz`, { timeout: 5000 });
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

export function createApiClient(config: ApiClientConfig): SahoolApiClient {
  return new SahoolApiClient(config);
}

// ─────────────────────────────────────────────────────────────────────────────
// Default Export
// ─────────────────────────────────────────────────────────────────────────────

export default SahoolApiClient;
