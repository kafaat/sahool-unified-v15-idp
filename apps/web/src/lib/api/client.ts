/**
 * SAHOOL API Client
 * Unified API client for connecting frontend to backend services
 */

import Cookies from "js-cookie";
import {
  ADVISORY_ENDPOINTS,
  AGRO_RULES_ENDPOINTS,
  ALERT_ENDPOINTS,
  AUTH_ENDPOINTS,
  CHAT_ENDPOINTS,
  CROP_HEALTH_ENDPOINTS,
  DISASTER_ENDPOINTS,
  EQUIPMENT_ENDPOINTS,
  FIELD_ENDPOINTS,
  INTELLIGENCE_ENDPOINTS,
  IOT_ENDPOINTS,
  IRRIGATION_ENDPOINTS,
  MARKETPLACE_ENDPOINTS,
  PROVIDER_ENDPOINTS,
  SATELLITE_ENDPOINTS,
  TASK_ENDPOINTS,
  BILLING_ENDPOINTS,
  WEATHER_ENDPOINTS,
  YIELD_ENDPOINTS,
  buildUrl,
} from "@sahool/shared-types/contracts";
import { sanitizers, validators, validationErrors } from "../validation";
import { logger } from "../logger";
import { getCsrfHeaders } from "../security/security";
import type {
  AgriculturalRisk,
  ApiResponse,
  Field,
  FieldCreateRequest,
  FieldUpdateRequest,
  NdviData,
  NdviSummary,
  WeatherData,
  WeatherForecast,
  Sensor,
  SensorReading,
  IrrigationRecommendation,
  ET0Calculation,
  FertilizerRecommendation,
  CropHealthAnalysis,
  Task,
  TaskCreateRequest,
  Equipment,
  MaintenanceSchedule,
  MarketplaceListing,
  Subscription,
  Invoice,
  User,
} from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "";

// Only warn during development, don't throw during build
if (typeof window !== "undefined") {
  if (!API_BASE_URL) {
    console.warn("NEXT_PUBLIC_API_URL environment variable is not set");
  } else if (
    process.env.NODE_ENV === "production" &&
    !API_BASE_URL.startsWith("https://") &&
    !API_BASE_URL.includes("localhost")
  ) {
    logger.warn(
      "Warning: API_BASE_URL should use HTTPS in production environment",
    );
  }
}

interface RequestOptions extends RequestInit {
  params?: Record<string, string>;
  skipRetry?: boolean;
  timeout?: number;
}

// Configuration
const DEFAULT_TIMEOUT = 30000; // 30 seconds
const MAX_RETRY_ATTEMPTS = 3;
const RETRY_DELAY = 1000; // 1 second

// Helper function to delay for retry logic
function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

class SahoolApiClient {
  private baseUrl: string;
  private token: string | null = null;
  private refreshPromise: Promise<boolean> | null = null;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  setToken(token: string) {
    this.token = token;
  }

  clearToken() {
    this.token = null;
  }

  /**
   * Attempt to refresh the access token using the refresh token from cookies
   * Returns true if successful, false otherwise
   */
  private async attemptTokenRefresh(): Promise<boolean> {
    // If there's already a refresh in progress, wait for it
    if (this.refreshPromise) {
      return this.refreshPromise;
    }

    // Start a new refresh
    this.refreshPromise = (async () => {
      try {
        // Only attempt in browser environment
        if (typeof window === "undefined") {
          return false;
        }

        const refreshToken = Cookies.get("refresh_token");

        if (!refreshToken) {
          logger.warn("No refresh token available");
          return false;
        }

        logger.info("Attempting to refresh access token");

        // Call the refresh endpoint
        const response = await this.refreshToken(refreshToken);

        if (response.success && response.data?.access_token) {
          const newAccessToken = response.data.access_token;

          // Clear any legacy path-scoped cookie before setting the root one,
          // so an old cookie on the current route cannot shadow the new value.
          Cookies.remove("access_token");

          // Update the stored token
          Cookies.set("access_token", newAccessToken, {
            expires: 7,
            secure: window.location.protocol === "https:",
            sameSite: "strict",
            path: "/",
          });
          this.setToken(newAccessToken);

          logger.info("Successfully refreshed access token");
          return true;
        } else {
          logger.warn("Failed to refresh token:", response.error);

          // Clear invalid tokens (root-scoped + legacy path-scoped)
          Cookies.remove("access_token", { path: "/" });
          Cookies.remove("refresh_token", { path: "/" });
          Cookies.remove("access_token");
          Cookies.remove("refresh_token");
          this.clearToken();

          return false;
        }
      } catch (error) {
        logger.error("Error refreshing token:", error);
        return false;
      } finally {
        // Clear the refresh promise after completion
        this.refreshPromise = null;
      }
    })();

    return this.refreshPromise;
  }

  /**
   * Redirect to login page
   */
  private redirectToLogin() {
    if (typeof window !== "undefined") {
      logger.info("Redirecting to login page");
      window.location.href = "/login";
    }
  }

  /**
   * Decode JWT payload from a token string.
   * Handles base64url encoding with proper padding.
   *
   * @returns Parsed payload object, or null if decoding fails
   */
  private decodeJwtPayload(token: string): Record<string, any> | null {
    try {
      const parts = token.split(".");
      if (parts.length !== 3 || !parts[1]) return null;
      let b64 = parts[1].replace(/-/g, "+").replace(/_/g, "/");
      const pad = b64.length % 4;
      if (pad) b64 += "=".repeat(4 - pad);
      const binary = atob(b64);
      const bytes = Uint8Array.from(binary, (c) => c.charCodeAt(0));
      return JSON.parse(new TextDecoder().decode(bytes));
    } catch {
      return null;
    }
  }

  /**
   * Check if JWT token is expired
   * Returns true if token is expired or will expire within 60 seconds
   */
  private isTokenExpired(token: string): boolean {
    const payload = this.decodeJwtPayload(token);
    if (!payload?.exp) return true;

    const expirationTime = payload.exp * 1000;
    const bufferTime = 60 * 1000;
    return Date.now() >= expirationTime - bufferTime;
  }

  /**
   * Check token and refresh if necessary before making a request
   * Returns true if token is valid or was successfully refreshed
   */
  private async ensureValidToken(): Promise<boolean> {
    // No token check needed if no token is set
    if (!this.token) {
      return true;
    }

    // Check if token is expired
    if (this.isTokenExpired(this.token)) {
      logger.info("Token is expired or expiring soon, attempting refresh");
      return await this.attemptTokenRefresh();
    }

    return true;
  }

  /**
   * Extract tenant_id (tid) from JWT token payload.
   * Used to automatically set X-Tenant-ID header for server-side RLS.
   */
  private extractTenantFromToken(token: string): string | null {
    const payload = this.decodeJwtPayload(token);
    return payload?.tid || null;
  }

  private async request<T>(
    endpoint: string,
    options: RequestOptions = {},
  ): Promise<ApiResponse<T>> {
    const {
      params,
      skipRetry = false,
      timeout = DEFAULT_TIMEOUT,
      ...fetchOptions
    } = options;

    // Check and refresh token if needed (skip for auth endpoints)
    if (
      endpoint !== AUTH_ENDPOINTS.REFRESH &&
      endpoint !== AUTH_ENDPOINTS.LOGIN
    ) {
      const tokenValid = await this.ensureValidToken();
      if (!tokenValid) {
        logger.warn("Unable to ensure valid token, redirecting to login");
        this.redirectToLogin();
        return {
          success: false,
          error: "Session expired. Please login again.",
        };
      }
    }

    // Build URL with query params
    let url = `${this.baseUrl}${endpoint}`;
    if (params) {
      const searchParams = new URLSearchParams(params);
      url += `?${searchParams.toString()}`;
    }

    // Set headers
    const headers: HeadersInit = {
      "Content-Type": "application/json",
      ...options.headers,
    };

    if (this.token) {
      (headers as Record<string, string>)["Authorization"] =
        `Bearer ${this.token}`;

      // Extract tenant_id (tid) from JWT and set X-Tenant-ID header
      // This enables server-side tenant isolation (RLS + middleware filtering)
      const tenantId = this.extractTenantFromToken(this.token);
      if (tenantId) {
        (headers as Record<string, string>)["X-Tenant-ID"] = tenantId;
      }
    }

    // Add CSRF headers for state-changing requests
    const method = (fetchOptions.method || "GET").toUpperCase();
    if (["POST", "PUT", "DELETE", "PATCH"].includes(method)) {
      const csrfHeaders = getCsrfHeaders();
      Object.assign(headers, csrfHeaders);
    }

    // Retry logic
    let lastError: Error | null = null;
    const maxAttempts = skipRetry ? 1 : MAX_RETRY_ATTEMPTS;

    for (let attempt = 0; attempt < maxAttempts; attempt++) {
      try {
        // Create AbortController for timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeout);

        let response: Response;
        try {
          response = await fetch(url, {
            ...fetchOptions,
            headers,
            signal: controller.signal,
            credentials: "include", // Ensure httpOnly cookies are sent with requests
          });
        } finally {
          clearTimeout(timeoutId);
        }

        // Parse response
        let data: any;
        const contentType = response.headers.get("content-type");

        if (contentType && contentType.includes("application/json")) {
          try {
            data = await response.json();
          } catch {
            return {
              success: false,
              error: "Invalid JSON response from server",
            };
          }
        } else {
          data = await response.text();
        }

        // Handle HTTP errors
        if (!response.ok) {
          // Handle 401 Unauthorized - try to refresh token
          if (
            response.status === 401 &&
            endpoint !== AUTH_ENDPOINTS.REFRESH &&
            endpoint !== AUTH_ENDPOINTS.LOGIN
          ) {
            logger.info("Received 401 response, attempting token refresh");

            const refreshSuccess = await this.attemptTokenRefresh();

            if (refreshSuccess) {
              // Token refreshed successfully, retry the original request
              logger.info("Token refreshed, retrying original request");

              // Update authorization header with new token
              if (this.token) {
                (headers as Record<string, string>)["Authorization"] =
                  `Bearer ${this.token}`;
              }

              // Retry the request with the new token
              const retryController = new AbortController();
              const retryTimeoutId = setTimeout(
                () => retryController.abort(),
                timeout,
              );

              let retryResponse: Response;
              try {
                retryResponse = await fetch(url, {
                  ...fetchOptions,
                  headers,
                  credentials: "include",
                  signal: retryController.signal,
                });
              } finally {
                clearTimeout(retryTimeoutId);
              }

              // Parse retry response
              let retryData: any;
              const retryContentType =
                retryResponse.headers.get("content-type");

              if (
                retryContentType &&
                retryContentType.includes("application/json")
              ) {
                try {
                  retryData = await retryResponse.json();
                } catch {
                  return {
                    success: false,
                    error: "Invalid JSON response from server",
                  };
                }
              } else {
                retryData = await retryResponse.text();
              }

              if (!retryResponse.ok) {
                return {
                  success: false,
                  error:
                    retryData.error ||
                    retryData.message ||
                    `Request failed with status ${retryResponse.status}`,
                };
              }

              // Successful retry response
              return typeof retryData === "object" && retryData !== null
                ? retryData
                : { success: true, data: retryData as T };
            } else {
              // Token refresh failed, redirect to login
              logger.warn("Token refresh failed, redirecting to login");
              this.redirectToLogin();

              return {
                success: false,
                error: "Session expired. Please login again.",
              };
            }
          }

          // Don't retry other client errors (4xx), only server errors (5xx) and network issues
          if (response.status >= 400 && response.status < 500) {
            return {
              success: false,
              error:
                data.error ||
                data.message ||
                `Request failed with status ${response.status}`,
            };
          }

          // For server errors, retry if we have attempts left
          if (attempt < maxAttempts - 1) {
            await delay(RETRY_DELAY * (attempt + 1)); // Exponential backoff
            continue;
          }

          return {
            success: false,
            error:
              data.error || data.message || `Server error: ${response.status}`,
          };
        }

        // Successful response
        return typeof data === "object" && data !== null
          ? data
          : { success: true, data: data as T };
      } catch (error) {
        lastError = error instanceof Error ? error : new Error("Unknown error");

        // Handle abort/timeout
        if (error instanceof Error && error.name === "AbortError") {
          return {
            success: false,
            error: "Request timeout - please try again",
          };
        }

        // Retry on network errors if we have attempts left
        if (attempt < maxAttempts - 1) {
          await delay(RETRY_DELAY * (attempt + 1));
          continue;
        }
      }
    }

    // All retries failed
    return {
      success: false,
      error:
        lastError?.message || "Network error - please check your connection",
    };
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Authentication API
  // ═══════════════════════════════════════════════════════════════════════════

  async login(email: string, password: string) {
    // Sanitize email input to prevent XSS
    const sanitizedEmail = sanitizers.email(email);

    // Validate email format using comprehensive validator
    if (!validators.email(sanitizedEmail)) {
      return {
        success: false,
        error: validationErrors.email,
      };
    }

    return this.request<{
      access_token: string;
      refresh_token?: string;
      user: User;
    }>(AUTH_ENDPOINTS.LOGIN, {
      method: "POST",
      body: JSON.stringify({ email: sanitizedEmail, password }),
      skipRetry: true, // Don't retry auth requests
    });
  }

  async getCurrentUser() {
    return this.request<User>(AUTH_ENDPOINTS.ME);
  }

  async refreshToken(refreshToken: string) {
    return this.request<{ access_token: string }>(AUTH_ENDPOINTS.REFRESH, {
      method: "POST",
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Field Operations API
  // ═══════════════════════════════════════════════════════════════════════════

  async getFields(
    tenantId: string,
    options?: { limit?: number; offset?: number },
  ) {
    return this.request<Field[]>(FIELD_ENDPOINTS.LIST, {
      params: {
        tenantId,
        limit: String(options?.limit || 100),
        offset: String(options?.offset || 0),
      },
    });
  }

  async getField(fieldId: string) {
    return this.request<Field>(buildUrl(FIELD_ENDPOINTS.GET, { fieldId }));
  }

  async createField(data: FieldCreateRequest) {
    return this.request<Field>(FIELD_ENDPOINTS.CREATE, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async updateField(fieldId: string, data: FieldUpdateRequest, etag?: string) {
    const headers: HeadersInit = {};
    if (etag) {
      headers["If-Match"] = etag;
    }
    return this.request<Field>(buildUrl(FIELD_ENDPOINTS.UPDATE, { fieldId }), {
      method: "PUT",
      body: JSON.stringify(data),
      headers,
    });
  }

  async deleteField(fieldId: string) {
    return this.request<void>(buildUrl(FIELD_ENDPOINTS.DELETE, { fieldId }), {
      method: "DELETE",
    });
  }

  async getNearbyFields(lat: number, lng: number, radius: number = 5000) {
    return this.request<Field[]>(FIELD_ENDPOINTS.NEARBY, {
      params: {
        lat: String(lat),
        lng: String(lng),
        radius: String(radius),
      },
    });
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // NDVI Analysis API
  // ═══════════════════════════════════════════════════════════════════════════

  async getFieldNdvi(fieldId: string) {
    return this.request<NdviData>(
      buildUrl(SATELLITE_ENDPOINTS.NDVI_FIELD, { fieldId }),
    );
  }

  async getNdviSummary(tenantId: string) {
    return this.request<NdviSummary>(SATELLITE_ENDPOINTS.NDVI_SUMMARY, {
      params: { tenantId },
    });
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Weather API (weather-service on port 8092)
  // Kong route: /api/v1/weather → strips to / → service has /weather/* endpoints
  // ═══════════════════════════════════════════════════════════════════════════

  async getWeather(lat: number, lng: number, fieldId: string = "default") {
    return this.request<WeatherData>(WEATHER_ENDPOINTS.KONG_CURRENT, {
      method: "POST",
      body: JSON.stringify({
        tenant_id: "default",
        field_id: fieldId,
        lat,
        lon: lng,
      }),
    });
  }

  async getWeatherForecast(lat: number, lng: number, days: number = 7, fieldId: string = "default") {
    return this.request<WeatherForecast>(WEATHER_ENDPOINTS.KONG_FORECAST, {
      method: "POST",
      body: JSON.stringify({
        tenant_id: "default",
        field_id: fieldId,
        lat,
        lon: lng,
        days,
      }),
    });
  }

  async getAgriculturalRisks(lat: number, lng: number, fieldId: string = "default") {
    return this.request<AgriculturalRisk[]>(
      WEATHER_ENDPOINTS.KONG_AGRICULTURAL_REPORT,
      {
        method: "POST",
        body: JSON.stringify({
          tenant_id: "default",
          field_id: fieldId,
          lat,
          lon: lng,
        }),
      },
    );
  }

  // Weather Advanced API (location_id based - for Yemen locations)
  // Kong route: /api/v1/weather → strips to / → service has /v1/* endpoints
  async getWeatherByLocation(locationId: string) {
    return this.request<WeatherData>(
      buildUrl(WEATHER_ENDPOINTS.KONG_CURRENT_BY_LOCATION, { locationId }),
    );
  }

  async getWeatherForecastByLocation(locationId: string, days: number = 7) {
    return this.request<WeatherForecast>(
      buildUrl(WEATHER_ENDPOINTS.KONG_FORECAST_BY_LOCATION, { locationId }),
      { params: { days: String(days) } },
    );
  }

  async getWeatherLocations(): Promise<ApiResponse<unknown>> {
    return this.request(WEATHER_ENDPOINTS.KONG_LOCATIONS);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Crop Health AI API
  // ═══════════════════════════════════════════════════════════════════════════

  async analyzeCropHealth(
    imageFile: File,
  ): Promise<ApiResponse<CropHealthAnalysis>> {
    // Validate file type
    const allowedTypes = ["image/jpeg", "image/jpg", "image/png", "image/webp"];
    if (!allowedTypes.includes(imageFile.type)) {
      return {
        success: false,
        error: "Invalid file type. Please upload a JPEG, PNG, or WebP image.",
      };
    }

    // Validate file size (max 10MB)
    const maxSize = 10 * 1024 * 1024;
    if (imageFile.size > maxSize) {
      return {
        success: false,
        error: "File size exceeds 10MB limit.",
      };
    }

    const formData = new FormData();
    formData.append("image", imageFile);

    try {
      // Create AbortController for timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 60000); // 60 second timeout for image upload

      // Build headers with auth and CSRF tokens
      const uploadHeaders: Record<string, string> = this.token
        ? { Authorization: `Bearer ${this.token}` }
        : {};

      // Add CSRF protection for file upload (POST request)
      const csrfHeaders = getCsrfHeaders();
      Object.assign(uploadHeaders, csrfHeaders);

      let response: Response;
      try {
        response = await fetch(
          `${this.baseUrl}${CROP_HEALTH_ENDPOINTS.ANALYZE}`,
          {
            method: "POST",
            headers: uploadHeaders,
            body: formData,
            signal: controller.signal,
            credentials: "include", // Ensure httpOnly cookies are sent with requests
          },
        );
      } finally {
        clearTimeout(timeoutId);
      }

      // Dynamic API response
      let data: any;
      try {
        data = await response.json();
      } catch {
        return {
          success: false,
          error: "Invalid response from server",
        };
      }

      if (!response.ok) {
        return {
          success: false,
          error: data?.error || data?.message || "Failed to analyze image",
        };
      }

      return data as ApiResponse<CropHealthAnalysis>;
    } catch (error) {
      if (error instanceof Error && error.name === "AbortError") {
        return {
          success: false,
          error: "Upload timeout - please try again with a smaller image",
        };
      }

      return {
        success: false,
        error: error instanceof Error ? error.message : "Network error",
      };
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // IoT Sensors API
  // ═══════════════════════════════════════════════════════════════════════════

  async getSensorData(fieldId: string) {
    return this.request<Sensor[]>(
      buildUrl(IOT_ENDPOINTS.FIELD_SENSORS, { fieldId }),
    );
  }

  async getSensorHistory(sensorId: string, from: Date, to: Date) {
    return this.request<SensorReading[]>(
      buildUrl(IOT_ENDPOINTS.SENSOR_HISTORY, { sensorId }),
      {
        params: {
          from: from.toISOString(),
          to: to.toISOString(),
        },
      },
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Irrigation API
  // ═══════════════════════════════════════════════════════════════════════════

  async getIrrigationRecommendation(fieldId: string) {
    return this.request<IrrigationRecommendation>(
      buildUrl(IRRIGATION_ENDPOINTS.RECOMMENDATION, { fieldId }),
    );
  }

  async calculateET0(data: {
    temperature: number;
    humidity: number;
    windSpeed: number;
    solarRadiation: number;
  }) {
    return this.request<ET0Calculation>(IRRIGATION_ENDPOINTS.ET0, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Fertilizer Advisor API
  // ═══════════════════════════════════════════════════════════════════════════

  async getFertilizerRecommendation(data: {
    cropType: string;
    growthStage: string;
    soilType: string;
    soilAnalysis?: {
      nitrogen: number;
      phosphorus: number;
      potassium: number;
      ph: number;
    };
  }) {
    return this.request<FertilizerRecommendation>(
      ADVISORY_ENDPOINTS.RECOMMEND,
      {
        method: "POST",
        body: JSON.stringify(data),
      },
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Sync API (for Mobile)
  // ═══════════════════════════════════════════════════════════════════════════

  async syncFields(tenantId: string, since?: string) {
    const params: Record<string, string> = { tenantId };
    if (since) params.since = since;

    return this.request<any>(FIELD_ENDPOINTS.SYNC, { params });
  }

  async batchSync(data: {
    deviceId: string;
    userId: string;
    tenantId: string;
    fields: any[];
  }) {
    return this.request<any>(FIELD_ENDPOINTS.SYNC_BATCH, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Advisory Service API (خدمة الاستشارات - port 8093)
  // Kong route: /api/v1/advisory → advisory-service:8093
  // ═══════════════════════════════════════════════════════════════════════════

  async getAgroAdvice(data: {
    fieldId: string;
    cropType: string;
    currentConditions: {
      temperature?: number;
      humidity?: number;
      soilMoisture?: number;
    };
  }) {
    return this.request<any>(ADVISORY_ENDPOINTS.ADVICE, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async getDiseaseDetection(cropType: string, symptoms: string[]) {
    return this.request<any>(ADVISORY_ENDPOINTS.DISEASE, {
      method: "POST",
      body: JSON.stringify({ cropType, symptoms }),
    });
  }

  async getNutrientRecommendation(data: {
    cropType: string;
    growthStage: string;
    soilAnalysis: any;
  }) {
    return this.request<any>(ADVISORY_ENDPOINTS.NUTRIENTS, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Agro Rules API (خدمة مسترجعة من kernel)
  // ═══════════════════════════════════════════════════════════════════════════

  async getIoTRules(fieldId: string) {
    return this.request<any>(
      buildUrl(AGRO_RULES_ENDPOINTS.FIELD_RULES, { fieldId }),
    );
  }

  async createIoTRule(data: {
    fieldId: string;
    condition: string;
    action: string;
    threshold: number;
  }) {
    return this.request<any>(AGRO_RULES_ENDPOINTS.CREATE_RULE, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async triggerRule(ruleId: string) {
    return this.request<any>(
      buildUrl(AGRO_RULES_ENDPOINTS.TRIGGER_RULE, { ruleId }),
      {
        method: "POST",
      },
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Chat Service API (خدمة المحادثات - port 8115)
  // Kong route: /api/v1/chat → chat-service:8115
  // ═══════════════════════════════════════════════════════════════════════════

  async getFieldMessages(
    fieldId: string,
    options?: { limit?: number; offset?: number },
  ) {
    return this.request<any[]>(
      buildUrl(CHAT_ENDPOINTS.FIELD_MESSAGES, { fieldId }),
      {
        params: {
          limit: String(options?.limit || 50),
          offset: String(options?.offset || 0),
        },
      },
    );
  }

  async sendFieldMessage(fieldId: string, message: string) {
    // Sanitize message to prevent XSS using comprehensive sanitizer
    const sanitizedMessage = sanitizers.html(message);

    // Validate message is safe text
    if (!validators.safeText(message)) {
      return {
        success: false,
        error: validationErrors.unsafeText,
      };
    }

    // Validate message length
    if (sanitizedMessage.length === 0) {
      return {
        success: false,
        error: validationErrors.required,
      };
    }

    if (sanitizedMessage.length > 2000) {
      return {
        success: false,
        error: validationErrors.tooLong,
      };
    }

    return this.request<any>(
      buildUrl(CHAT_ENDPOINTS.FIELD_SEND, { fieldId }),
      {
        method: "POST",
        body: JSON.stringify({ message: sanitizedMessage }),
      },
    );
  }

  async getFieldChatParticipants(fieldId: string) {
    return this.request<any[]>(
      buildUrl(CHAT_ENDPOINTS.FIELD_PARTICIPANTS, { fieldId }),
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Field Management Service API (خدمة إدارة الحقول - port 3000)
  // Kong route: /api/v1/fields → field-management-service:3000
  // ═══════════════════════════════════════════════════════════════════════════

  async getFieldBoundary(fieldId: string) {
    return this.request<any>(buildUrl(FIELD_ENDPOINTS.BOUNDARY, { fieldId }));
  }

  async updateFieldBoundary(fieldId: string, boundary: any, etag?: string) {
    const headers: HeadersInit = {};
    if (etag) headers["If-Match"] = etag;

    return this.request<any>(
      buildUrl(FIELD_ENDPOINTS.BOUNDARY_UPDATE, { fieldId }),
      {
        method: "PUT",
        body: JSON.stringify({ boundary }),
        headers,
      },
    );
  }

  async getFieldBoundaryHistory(fieldId: string) {
    return this.request<any[]>(
      buildUrl(FIELD_ENDPOINTS.BOUNDARY_HISTORY, { fieldId }),
    );
  }

  async rollbackFieldBoundary(
    fieldId: string,
    historyId: string,
    reason?: string,
  ) {
    return this.request<any>(
      buildUrl(FIELD_ENDPOINTS.BOUNDARY_ROLLBACK, { fieldId }),
      {
        method: "POST",
        body: JSON.stringify({ historyId, reason }),
      },
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Equipment Service API (خدمة مسترجعة من kernel)
  // ═══════════════════════════════════════════════════════════════════════════

  async getEquipment(tenantId: string) {
    return this.request<Equipment[]>(EQUIPMENT_ENDPOINTS.LIST, {
      params: { tenantId },
    });
  }

  async getEquipmentById(equipmentId: string) {
    return this.request<Equipment>(
      buildUrl(EQUIPMENT_ENDPOINTS.GET, { equipmentId }),
    );
  }

  async createEquipment(data: {
    name: string;
    type: string;
    tenantId: string;
    specifications?: any;
  }) {
    return this.request<Equipment>(EQUIPMENT_ENDPOINTS.CREATE, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async updateEquipmentStatus(equipmentId: string, status: string) {
    return this.request<Equipment>(
      buildUrl(EQUIPMENT_ENDPOINTS.STATUS, { equipmentId }),
      {
        method: "PUT",
        body: JSON.stringify({ status }),
      },
    );
  }

  async getEquipmentMaintenanceSchedule(equipmentId: string) {
    return this.request<MaintenanceSchedule[]>(
      buildUrl(EQUIPMENT_ENDPOINTS.MAINTENANCE, { equipmentId }),
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Task Service API (خدمة مسترجعة من kernel)
  // ═══════════════════════════════════════════════════════════════════════════

  async getTasks(options: {
    tenantId?: string;
    fieldId?: string;
    userId?: string;
    status?: string;
    limit?: number;
    offset?: number;
  }) {
    const params: Record<string, string> = {};
    if (options.tenantId) params.tenantId = options.tenantId;
    if (options.fieldId) params.fieldId = options.fieldId;
    if (options.userId) params.userId = options.userId;
    if (options.status) params.status = options.status;
    if (options.limit) params.limit = String(options.limit);
    if (options.offset) params.offset = String(options.offset);

    return this.request<Task[]>(TASK_ENDPOINTS.LIST, { params });
  }

  async getTask(taskId: string) {
    return this.request<Task>(buildUrl(TASK_ENDPOINTS.GET, { taskId }));
  }

  async updateTask(
    taskId: string,
    data: { status?: string; title?: string; description?: string },
  ) {
    return this.request<Task>(buildUrl(TASK_ENDPOINTS.UPDATE, { taskId }), {
      method: "PUT",
      body: JSON.stringify(data),
    });
  }

  async createTask(data: TaskCreateRequest) {
    return this.request<Task>(TASK_ENDPOINTS.CREATE, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async updateTaskStatus(
    taskId: string,
    status: "pending" | "in_progress" | "completed" | "cancelled",
  ) {
    return this.request<Task>(buildUrl(TASK_ENDPOINTS.STATUS, { taskId }), {
      method: "PUT",
      body: JSON.stringify({ status }),
    });
  }

  async completeTask(taskId: string, notes?: string) {
    return this.request<Task>(buildUrl(TASK_ENDPOINTS.COMPLETE, { taskId }), {
      method: "POST",
      body: JSON.stringify({ notes }),
    });
  }

  async deleteTask(taskId: string) {
    return this.request<void>(buildUrl(TASK_ENDPOINTS.DELETE, { taskId }), {
      method: "DELETE",
    });
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Alerts API
  // ═══════════════════════════════════════════════════════════════════════════

  async getAlerts(options: {
    tenantId?: string;
    status?: string;
    fieldId?: string;
  }) {
    const params: Record<string, string> = {};
    if (options.tenantId) params.tenantId = options.tenantId;
    if (options.status) params.status = options.status;
    if (options.fieldId) params.fieldId = options.fieldId;

    return this.request<any[]>(ALERT_ENDPOINTS.LIST, { params });
  }

  async acknowledgeAlert(alertId: string) {
    return this.request<any>(
      buildUrl(ALERT_ENDPOINTS.ACKNOWLEDGE, { alertId }),
      {
        method: "POST",
      },
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // WebSocket Gateway API (خدمة مسترجعة من kernel)
  // ═══════════════════════════════════════════════════════════════════════════

  getWebSocketUrl(): string {
    const wsProtocol = this.baseUrl.startsWith("https") ? "wss" : "ws";
    const wsHost = this.baseUrl.replace(/^https?:\/\//, "");
    return `${wsProtocol}://${wsHost}/ws`;
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Provider Config API (خدمة مسترجعة من kernel)
  // ═══════════════════════════════════════════════════════════════════════════

  async getProviders() {
    return this.request<any[]>(PROVIDER_ENDPOINTS.LIST);
  }

  async getProviderConfig(providerId: string) {
    return this.request<any>(
      buildUrl(PROVIDER_ENDPOINTS.CONFIG, { providerId }),
    );
  }

  async updateProviderConfig(providerId: string, config: any) {
    return this.request<any>(
      buildUrl(PROVIDER_ENDPOINTS.CONFIG_UPDATE, { providerId }),
      {
        method: "PUT",
        body: JSON.stringify(config),
      },
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Crop Health API (خدمة مسترجعة من kernel - مع OpenAPI)
  // ═══════════════════════════════════════════════════════════════════════════

  async getCropHealthDecision(data: {
    cropType: string;
    ndviValue: number;
    weatherConditions: any;
    soilMoisture?: number;
  }) {
    return this.request<any>(CROP_HEALTH_ENDPOINTS.DECISION, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async getCropHealthHistory(fieldId: string, days: number = 30) {
    return this.request<any[]>(
      buildUrl(CROP_HEALTH_ENDPOINTS.HISTORY, { fieldId }),
      {
        params: { days: String(days) },
      },
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Satellite Service API (vegetation-analysis-service)
  // Kong route: /api/v1/satellite → strips to / → service has /v1/* endpoints
  // ═══════════════════════════════════════════════════════════════════════════

  async getSatelliteImagery(
    fieldId: string,
    options?: { from?: string; to?: string },
  ) {
    // Maps to vegetation-analysis-service /v1/timeseries/{field_id}
    // Filter out undefined values to prevent "undefined" string in query params
    const params = options
      ? Object.fromEntries(Object.entries(options).filter(([, v]) => v != null))
      : undefined;
    return this.request<any[]>(
      buildUrl(SATELLITE_ENDPOINTS.TIMESERIES, { fieldId }),
      {
        params: params as Record<string, string>,
      },
    );
  }

  async requestSatelliteAnalysis(
    fieldId: string,
    analysisType: "ndvi" | "moisture" | "thermal",
  ) {
    // Maps to vegetation-analysis-service /v1/analyze (POST)
    return this.request<any>(SATELLITE_ENDPOINTS.ANALYZE, {
      method: "POST",
      body: JSON.stringify({ field_id: fieldId, analysis_type: analysisType }),
    });
  }

  async getSatelliteIndices(fieldId: string) {
    // Maps to vegetation-analysis-service /v1/indices/{field_id}
    return this.request<any>(
      buildUrl(SATELLITE_ENDPOINTS.INDICES, { fieldId }),
    );
  }

  async getSatelliteSatellites() {
    // Maps to vegetation-analysis-service /v1/satellites
    return this.request<any>(SATELLITE_ENDPOINTS.SATELLITES);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Marketplace API
  // ═══════════════════════════════════════════════════════════════════════════

  async getMarketplaceListings(options?: {
    category?: string;
    region?: string;
  }) {
    const params = options
      ? Object.fromEntries(Object.entries(options).filter(([, v]) => v != null))
      : undefined;
    return this.request<MarketplaceListing[]>(MARKETPLACE_ENDPOINTS.LISTINGS, {
      params: params as Record<string, string>,
    });
  }

  async createListing(data: {
    title: string;
    description: string;
    category: string;
    price: number;
    quantity: number;
    unit: string;
  }) {
    return this.request<MarketplaceListing>(
      MARKETPLACE_ENDPOINTS.LISTING_CREATE,
      {
        method: "POST",
        body: JSON.stringify(data),
      },
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Billing Core API
  // ═══════════════════════════════════════════════════════════════════════════

  async getSubscription(tenantId: string) {
    return this.request<Subscription>(
      buildUrl(BILLING_ENDPOINTS.TENANT_SUBSCRIPTION, { tenantId }),
    );
  }

  async getInvoices(tenantId: string) {
    return this.request<Invoice[]>(
      buildUrl(BILLING_ENDPOINTS.TENANT_INVOICES, { tenantId }),
    );
  }

  async getUsageStats(tenantId: string) {
    return this.request<any>(
      buildUrl(BILLING_ENDPOINTS.TENANT_USAGE, { tenantId }),
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Yield Prediction API
  // ═══════════════════════════════════════════════════════════════════════════

  async predictYield(fieldId: string) {
    return this.request<any>(buildUrl(YIELD_ENDPOINTS.PREDICT, { fieldId }));
  }

  async getYieldHistory(fieldId: string) {
    return this.request<any[]>(buildUrl(YIELD_ENDPOINTS.HISTORY, { fieldId }));
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Disaster Assessment API
  // ═══════════════════════════════════════════════════════════════════════════

  async assessDisaster(fieldId: string, disasterType: string) {
    return this.request<any>(DISASTER_ENDPOINTS.ASSESS, {
      method: "POST",
      body: JSON.stringify({ fieldId, disasterType }),
    });
  }

  async getDisasterAlerts(region: string) {
    return this.request<any[]>(DISASTER_ENDPOINTS.ALERTS, {
      params: { region },
    });
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Field Intelligence API
  // ═══════════════════════════════════════════════════════════════════════════

  async getLivingFieldScore(fieldId: string) {
    return this.request<any>(
      buildUrl(INTELLIGENCE_ENDPOINTS.FIELD_SCORE, { fieldId }),
    );
  }

  async getFieldZones(fieldId: string) {
    return this.request<any[]>(
      buildUrl(INTELLIGENCE_ENDPOINTS.FIELD_ZONES, { fieldId }),
    );
  }

  async getFieldIntelligenceAlerts(fieldId: string) {
    return this.request<any[]>(
      buildUrl(INTELLIGENCE_ENDPOINTS.FIELD_ALERTS, { fieldId }),
      {
        params: { status: "active" },
      },
    );
  }

  async createTaskFromAlert(
    alertId: string,
    taskData: {
      title: string;
      titleAr: string;
      description?: string;
      descriptionAr?: string;
      priority: "urgent" | "high" | "medium" | "low";
      dueDate?: string;
      assigneeId?: string;
    },
  ) {
    return this.request<any>(
      buildUrl(INTELLIGENCE_ENDPOINTS.CREATE_TASK, { alertId }),
      {
        method: "POST",
        body: JSON.stringify(taskData),
      },
    );
  }

  async getBestDaysForActivity(activity: string, days: number = 14) {
    return this.request<any[]>(INTELLIGENCE_ENDPOINTS.BEST_DAYS, {
      params: {
        activity: activity.toLowerCase(),
        days: String(Math.max(1, Math.min(days, 30))),
      },
    });
  }

  async validateTaskDate(date: string, activity: string) {
    return this.request<any>(INTELLIGENCE_ENDPOINTS.VALIDATE_DATE, {
      method: "POST",
      body: JSON.stringify({
        date: new Date(date).toISOString(),
        activity: activity.toLowerCase(),
      }),
    });
  }

  async getFieldRecommendations(fieldId: string) {
    return this.request<any[]>(
      buildUrl(INTELLIGENCE_ENDPOINTS.FIELD_RECOMMENDATIONS, { fieldId }),
    );
  }
}

// Singleton instance
export const apiClient = new SahoolApiClient();
export default apiClient;
