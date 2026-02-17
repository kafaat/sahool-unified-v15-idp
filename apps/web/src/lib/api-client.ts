/**
 * SAHOOL Web API Client v16.0.0
 * عميل API موحد للويب - سهول
 *
 * Enhanced API client for connecting to Kong Gateway with:
 * - Automatic JWT token handling with proactive refresh
 * - Request/response interceptors
 * - Bilingual error handling (Arabic/English)
 * - Retry logic with exponential backoff
 * - Circuit breaker pattern for resilience
 * - Rate limit awareness
 *
 * ميزات العميل:
 * - معالجة رمز JWT التلقائي مع التحديث الاستباقي
 * - معترضات الطلب/الاستجابة
 * - معالجة الأخطاء ثنائية اللغة (العربية/الإنجليزية)
 * - منطق إعادة المحاولة مع التراجع الأسي
 * - نمط قاطع الدارة للمرونة
 * - الوعي بحدود المعدل
 */

import Cookies from "js-cookie";
import { logger } from "./logger";
import { getCsrfHeaders } from "./security/security";
import { sanitizers, validators, validationErrors } from "./validation";
import {
  ERROR_MESSAGES as UNIFIED_ERROR_MESSAGES,
} from "@sahool/shared-types/contracts";

// =============================================================================
// Types & Interfaces | الأنواع والواجهات
// =============================================================================

/**
 * API Response wrapper with bilingual support
 * غلاف استجابة API مع دعم ثنائي اللغة
 */
export interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: string;
  errorAr?: string;
  errorCode?: string;
  requestId?: string;
  meta?: {
    page?: number;
    limit?: number;
    total?: number;
    hasMore?: boolean;
  };
}

/**
 * Request configuration options
 * خيارات تكوين الطلب
 */
export interface RequestOptions extends RequestInit {
  params?: Record<string, string | number | boolean>;
  skipRetry?: boolean;
  skipAuth?: boolean;
  timeout?: number;
  language?: "ar" | "en" | "both";
}

/**
 * Error message structure with bilingual support
 * هيكل رسالة الخطأ مع الدعم ثنائي اللغة
 */
interface ErrorMessage {
  code: string;
  message: string;
  messageAr: string;
}

/**
 * Rate limit information
 * معلومات حد المعدل
 */
export interface RateLimitInfo {
  remaining: number | null;
  limit: number | null;
  resetAt: Date | null;
}

/**
 * Circuit breaker state
 * حالة قاطع الدارة
 */
export interface CircuitBreakerState {
  isOpen: boolean;
  failures: number;
  lastFailure: Date | null;
  nextRetry: Date | null;
}

// =============================================================================
// Configuration | التكوين
// =============================================================================

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const DEFAULT_TIMEOUT = 30000;
const MAX_RETRY_ATTEMPTS = 3;
const RETRY_DELAY_BASE = 1000;
const CIRCUIT_BREAKER_THRESHOLD = 5;
const CIRCUIT_BREAKER_RESET_MS = 30000;
const TOKEN_REFRESH_BUFFER_MS = 60000; // Refresh 1 minute before expiry

// Bilingual error messages - sourced from @sahool/shared-types/contracts
// رسائل الخطأ ثنائية اللغة - مصدرها العقود الموحدة
const ERROR_MESSAGES: Record<string, ErrorMessage> = Object.fromEntries(
  Object.entries(UNIFIED_ERROR_MESSAGES).map(([key, unified]) => [
    key,
    {
      code: unified.code,
      message: unified.en,
      messageAr: unified.ar,
    },
  ]),
);

// =============================================================================
// Helper Functions | الدوال المساعدة
// =============================================================================

function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function isTokenExpired(token: string, bufferMs: number = 0): boolean {
  try {
    const parts = token.split(".");
    if (parts.length !== 3 || !parts[1]) return true;

    const payload = JSON.parse(atob(parts[1].replace(/-/g, "+").replace(/_/g, "/")));

    if (payload.exp) {
      const expirationTime = payload.exp * 1000;
      return Date.now() >= expirationTime - bufferMs;
    }

    return true;
  } catch {
    return true;
  }
}

function getErrorMessage(code: string): ErrorMessage {
  return (
    ERROR_MESSAGES[code] || {
      code: "UNKNOWN",
      message: "An unexpected error occurred",
      messageAr: "حدث خطأ غير متوقع",
    }
  );
}

// =============================================================================
// SahoolApiClient Class | فئة عميل API سهول
// =============================================================================

export class SahoolApiClient {
  private baseUrl: string;
  private token: string | null = null;
  private refreshPromise: Promise<boolean> | null = null;
  private rateLimitInfo: RateLimitInfo = {
    remaining: null,
    limit: null,
    resetAt: null,
  };
  private circuitBreaker: Map<string, CircuitBreakerState> = new Map();
  private requestInterceptors: Array<(options: RequestOptions) => RequestOptions | Promise<RequestOptions>> = [];
  private responseInterceptors: Array<(response: ApiResponse<unknown>) => ApiResponse<unknown> | Promise<ApiResponse<unknown>>> = [];

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
    this.initializeFromCookies();
  }

  // ===========================================================================
  // Token Management | إدارة الرموز
  // ===========================================================================

  private initializeFromCookies(): void {
    if (typeof window !== "undefined") {
      const token = Cookies.get("access_token");
      if (token) {
        this.token = token;
      }
    }
  }

  setToken(token: string): void {
    this.token = token;
    if (typeof window !== "undefined") {
      Cookies.set("access_token", token, {
        expires: 7,
        secure: process.env.NODE_ENV === "production",
        sameSite: "strict",
      });
    }
  }

  clearToken(): void {
    this.token = null;
    if (typeof window !== "undefined") {
      Cookies.remove("access_token");
      Cookies.remove("refresh_token");
    }
  }

  getToken(): string | null {
    return this.token;
  }

  private async ensureValidToken(): Promise<boolean> {
    if (!this.token) return true;

    if (isTokenExpired(this.token, TOKEN_REFRESH_BUFFER_MS)) {
      logger.info("Token expiring soon, attempting refresh");
      return await this.attemptTokenRefresh();
    }

    return true;
  }

  private async attemptTokenRefresh(): Promise<boolean> {
    if (this.refreshPromise) return this.refreshPromise;

    this.refreshPromise = (async () => {
      try {
        if (typeof window === "undefined") return false;

        const refreshToken = Cookies.get("refresh_token");
        if (!refreshToken) {
          logger.warn("No refresh token available");
          return false;
        }

        const response = await this.request<{ access_token: string }>(
          "/api/v1/auth/refresh",
          {
            method: "POST",
            body: JSON.stringify({ refresh_token: refreshToken }),
            skipRetry: true,
            skipAuth: true,
          }
        );

        if (response.success && response.data?.access_token) {
          this.setToken(response.data.access_token);
          logger.info("Token refreshed successfully");
          return true;
        }

        this.clearToken();
        return false;
      } catch {
        logger.error("Token refresh failed");
        return false;
      } finally {
        this.refreshPromise = null;
      }
    })();

    return this.refreshPromise;
  }

  // ===========================================================================
  // Circuit Breaker | قاطع الدارة
  // ===========================================================================

  private getCircuitState(endpoint: string): CircuitBreakerState {
    if (!this.circuitBreaker.has(endpoint)) {
      this.circuitBreaker.set(endpoint, {
        isOpen: false,
        failures: 0,
        lastFailure: null,
        nextRetry: null,
      });
    }
    return this.circuitBreaker.get(endpoint)!;
  }

  private recordFailure(endpoint: string): void {
    const state = this.getCircuitState(endpoint);
    state.failures++;
    state.lastFailure = new Date();

    if (state.failures >= CIRCUIT_BREAKER_THRESHOLD) {
      state.isOpen = true;
      state.nextRetry = new Date(Date.now() + CIRCUIT_BREAKER_RESET_MS);
      logger.warn(`Circuit breaker opened for ${endpoint}`);
    }
  }

  private resetCircuit(endpoint: string): void {
    const state = this.getCircuitState(endpoint);
    state.isOpen = false;
    state.failures = 0;
    state.lastFailure = null;
    state.nextRetry = null;
  }

  private isCircuitOpen(endpoint: string): boolean {
    const state = this.getCircuitState(endpoint);

    if (state.isOpen && state.nextRetry && new Date() >= state.nextRetry) {
      // Half-open state - allow one request to test
      state.isOpen = false;
    }

    return state.isOpen;
  }

  // ===========================================================================
  // Interceptors | المعترضات
  // ===========================================================================

  addRequestInterceptor(
    interceptor: (options: RequestOptions) => RequestOptions | Promise<RequestOptions>
  ): void {
    this.requestInterceptors.push(interceptor);
  }

  addResponseInterceptor(
    interceptor: (response: ApiResponse<unknown>) => ApiResponse<unknown> | Promise<ApiResponse<unknown>>
  ): void {
    this.responseInterceptors.push(interceptor);
  }

  // ===========================================================================
  // Rate Limiting | حدود المعدل
  // ===========================================================================

  getRateLimitInfo(): RateLimitInfo {
    return { ...this.rateLimitInfo };
  }

  private updateRateLimitInfo(headers: Headers): void {
    const remaining = headers.get("X-RateLimit-Remaining-Minute");
    const limit = headers.get("X-RateLimit-Limit-Minute");
    const reset = headers.get("X-RateLimit-Reset");

    if (remaining) this.rateLimitInfo.remaining = parseInt(remaining, 10);
    if (limit) this.rateLimitInfo.limit = parseInt(limit, 10);
    if (reset) this.rateLimitInfo.resetAt = new Date(parseInt(reset, 10) * 1000);
  }

  // ===========================================================================
  // Core Request Method | طريقة الطلب الأساسية
  // ===========================================================================

  private async request<T>(
    endpoint: string,
    options: RequestOptions = {}
  ): Promise<ApiResponse<T>> {
    const {
      params,
      skipRetry = false,
      skipAuth = false,
      timeout = DEFAULT_TIMEOUT,
      language = "both",
      ...fetchOptions
    } = options;

    // Apply request interceptors
    let processedOptions = options;
    for (const interceptor of this.requestInterceptors) {
      processedOptions = await interceptor(processedOptions);
    }

    // Check circuit breaker
    if (this.isCircuitOpen(endpoint)) {
      const err = getErrorMessage("CIRCUIT_OPEN");
      return {
        success: false,
        error: err.message,
        errorAr: err.messageAr,
        errorCode: err.code,
      };
    }

    // Ensure valid token for protected endpoints
    if (!skipAuth && !endpoint.includes("/auth/login") && !endpoint.includes("/auth/register")) {
      const tokenValid = await this.ensureValidToken();
      if (!tokenValid && this.token) {
        this.redirectToLogin();
        const err = getErrorMessage("UNAUTHORIZED");
        return {
          success: false,
          error: err.message,
          errorAr: err.messageAr,
          errorCode: err.code,
        };
      }
    }

    // Build URL with query params
    let url = `${this.baseUrl}${endpoint}`;
    if (params) {
      const searchParams = new URLSearchParams();
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          searchParams.append(key, String(value));
        }
      });
      const queryString = searchParams.toString();
      if (queryString) url += `?${queryString}`;
    }

    // Set headers
    const headers: HeadersInit = {
      "Content-Type": "application/json",
      "Accept": "application/json",
      "Accept-Language": language === "ar" ? "ar" : language === "en" ? "en" : "ar,en",
      ...processedOptions.headers,
    };

    if (this.token && !skipAuth) {
      (headers as Record<string, string>)["Authorization"] = `Bearer ${this.token}`;
    }

    // Add CSRF headers for state-changing requests
    const method = (fetchOptions.method || "GET").toUpperCase();
    if (["POST", "PUT", "DELETE", "PATCH"].includes(method)) {
      Object.assign(headers, getCsrfHeaders());
    }

    // Retry logic
    let lastError: Error | null = null;
    const maxAttempts = skipRetry ? 1 : MAX_RETRY_ATTEMPTS;

    for (let attempt = 0; attempt < maxAttempts; attempt++) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeout);

        const response = await fetch(url, {
          ...fetchOptions,
          headers,
          signal: controller.signal,
          credentials: "include",
        });

        clearTimeout(timeoutId);
        this.updateRateLimitInfo(response.headers);

        const requestId = response.headers.get("X-Request-Id") || undefined;

        // Parse response
        let data: unknown;
        const contentType = response.headers.get("content-type");

        if (contentType?.includes("application/json")) {
          try {
            data = await response.json();
          } catch {
            const err = getErrorMessage("INVALID_RESPONSE");
            return {
              success: false,
              error: err.message,
              errorAr: err.messageAr,
              errorCode: err.code,
              requestId,
            };
          }
        } else {
          data = await response.text();
        }

        // Handle HTTP errors
        if (!response.ok) {
          // Handle specific status codes
          if (response.status === 401 && !endpoint.includes("/auth/")) {
            const refreshed = await this.attemptTokenRefresh();
            if (refreshed) {
              // Retry with new token
              (headers as Record<string, string>)["Authorization"] = `Bearer ${this.token}`;
              const retryResponse = await fetch(url, {
                ...fetchOptions,
                headers,
                credentials: "include",
              });

              if (retryResponse.ok) {
                const retryData = await retryResponse.json();
                this.resetCircuit(endpoint);

                let result: ApiResponse<T> = {
                  success: true,
                  data: retryData as T,
                  requestId: retryResponse.headers.get("X-Request-Id") || undefined,
                };

                // Apply response interceptors
                for (const interceptor of this.responseInterceptors) {
                  result = (await interceptor(result)) as ApiResponse<T>;
                }

                return result;
              }
            }

            this.redirectToLogin();
            const err = getErrorMessage("UNAUTHORIZED");
            return {
              success: false,
              error: err.message,
              errorAr: err.messageAr,
              errorCode: err.code,
              requestId,
            };
          }

          if (response.status === 403) {
            const err = getErrorMessage("FORBIDDEN");
            return {
              success: false,
              error: err.message,
              errorAr: err.messageAr,
              errorCode: err.code,
              requestId,
            };
          }

          if (response.status === 404) {
            const err = getErrorMessage("NOT_FOUND");
            return {
              success: false,
              error: err.message,
              errorAr: err.messageAr,
              errorCode: err.code,
              requestId,
            };
          }

          if (response.status === 429) {
            const err = getErrorMessage("RATE_LIMITED");
            return {
              success: false,
              error: err.message,
              errorAr: err.messageAr,
              errorCode: err.code,
              requestId,
            };
          }

          // Don't retry 4xx errors (except 401 handled above)
          if (response.status >= 400 && response.status < 500) {
            const apiData = data as Record<string, unknown>;
            return {
              success: false,
              error: String(apiData?.error || apiData?.message || `Request failed: ${response.status}`),
              errorAr: String(apiData?.error_ar || apiData?.message_ar || "فشل الطلب"),
              errorCode: String(apiData?.code || `HTTP_${response.status}`),
              requestId,
            };
          }

          // Server errors - retry
          this.recordFailure(endpoint);
          if (attempt < maxAttempts - 1) {
            await delay(RETRY_DELAY_BASE * Math.pow(2, attempt));
            continue;
          }

          const err = getErrorMessage("SERVER_ERROR");
          return {
            success: false,
            error: err.message,
            errorAr: err.messageAr,
            errorCode: err.code,
            requestId,
          };
        }

        // Success
        this.resetCircuit(endpoint);

        let result: ApiResponse<T>;

        // Check if response has standard API structure
        if (typeof data === "object" && data !== null) {
          const apiData = data as Record<string, unknown>;
          if ("success" in apiData) {
            result = data as ApiResponse<T>;
          } else {
            result = { success: true, data: data as T, requestId };
          }
        } else {
          result = { success: true, data: data as T, requestId };
        }

        // Apply response interceptors
        for (const interceptor of this.responseInterceptors) {
          result = (await interceptor(result)) as ApiResponse<T>;
        }

        return result;
      } catch (error) {
        lastError = error instanceof Error ? error : new Error("Unknown error");

        if (error instanceof Error && error.name === "AbortError") {
          const err = getErrorMessage("TIMEOUT");
          return {
            success: false,
            error: err.message,
            errorAr: err.messageAr,
            errorCode: err.code,
          };
        }

        this.recordFailure(endpoint);

        if (attempt < maxAttempts - 1) {
          await delay(RETRY_DELAY_BASE * Math.pow(2, attempt));
          continue;
        }
      }
    }

    const err = getErrorMessage("NETWORK_ERROR");
    return {
      success: false,
      error: lastError?.message || err.message,
      errorAr: err.messageAr,
      errorCode: err.code,
    };
  }

  private redirectToLogin(): void {
    if (typeof window !== "undefined") {
      logger.info("Redirecting to login");
      window.location.href = "/login";
    }
  }

  // ===========================================================================
  // Public API Methods | طرق API العامة
  // ===========================================================================

  async get<T>(endpoint: string, params?: Record<string, string | number | boolean>): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { method: "GET", params });
  }

  async post<T, B = unknown>(endpoint: string, body?: B): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: "POST",
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  async put<T, B = unknown>(endpoint: string, body?: B): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: "PUT",
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  async patch<T, B = unknown>(endpoint: string, body?: B): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: "PATCH",
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  async delete<T>(endpoint: string): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { method: "DELETE" });
  }

  // ===========================================================================
  // Authentication API | API المصادقة
  // ===========================================================================

  async login(
    email: string,
    password: string,
    totpCode?: string
  ): Promise<ApiResponse<{
    access_token: string;
    refresh_token?: string;
    user: {
      id: string;
      email: string;
      name: string;
      nameAr?: string;
      role: string;
    };
    requires_2fa?: boolean;
  }>> {
    const sanitizedEmail = sanitizers.email(email);

    if (!validators.email(sanitizedEmail)) {
      return {
        success: false,
        error: validationErrors.email,
        errorAr: "صيغة البريد الإلكتروني غير صالحة",
        errorCode: "INVALID_EMAIL",
      };
    }

    const body: Record<string, string> = { email: sanitizedEmail, password };
    if (totpCode) body.totp_code = totpCode;

    const response = await this.request("/api/v1/auth/login", {
      method: "POST",
      body: JSON.stringify(body),
      skipRetry: true,
      skipAuth: true,
    });

    if (response.success && response.data) {
      const data = response.data as { access_token: string; refresh_token?: string };
      this.setToken(data.access_token);

      if (data.refresh_token && typeof window !== "undefined") {
        Cookies.set("refresh_token", data.refresh_token, {
          expires: 30,
          secure: process.env.NODE_ENV === "production",
          sameSite: "strict",
        });
      }
    }

    return response as ApiResponse<{
      access_token: string;
      refresh_token?: string;
      user: { id: string; email: string; name: string; nameAr?: string; role: string };
      requires_2fa?: boolean;
    }>;
  }

  async logout(): Promise<ApiResponse<void>> {
    const response = await this.post<void>("/api/v1/auth/logout");
    this.clearToken();
    return response;
  }

  async getCurrentUser(): Promise<ApiResponse<{
    id: string;
    email: string;
    name: string;
    nameAr?: string;
    role: string;
    tenantId?: string;
  }>> {
    return this.get("/api/v1/auth/me");
  }

  // ===========================================================================
  // Health Check | فحص الصحة
  // ===========================================================================

  async checkHealth(service?: string): Promise<ApiResponse<{
    status: string;
    service: string;
    version: string;
    timestamp: string;
  }>> {
    const endpoint = service ? `/api/v1/${service}/healthz` : "/healthz";
    return this.get(endpoint);
  }

  // ===========================================================================
  // Utility Methods | الطرق المساعدة
  // ===========================================================================

  getCircuitBreakerState(endpoint: string): CircuitBreakerState {
    return { ...this.getCircuitState(endpoint) };
  }

  resetAllCircuitBreakers(): void {
    this.circuitBreaker.clear();
  }
}

// =============================================================================
// Singleton Export | تصدير المثيل الوحيد
// =============================================================================

export const apiClient = new SahoolApiClient();
export default apiClient;
