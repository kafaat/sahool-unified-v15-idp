/**
 * SAHOOL Admin API Client
 * Unified API client for admin dashboard with centralized token management
 */

import DOMPurify from "dompurify";
import { logger } from "./logger";

interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: string;
}

/** Raw API response structure before type narrowing */
interface RawApiResponse {
  success?: boolean;
  data?: unknown;
  error?: string;
  message?: string;
  detail?: string;
}

/** Login request body structure */
interface LoginRequestBody {
  email: string;
  password: string;
  totp_code?: string;
}

/** Type guard to check if value is a RawApiResponse object */
function isRawApiResponse(value: unknown): value is RawApiResponse {
  return (
    typeof value === "object" &&
    value !== null &&
    !Array.isArray(value)
  );
}

/** Extract error message from raw API response */
function extractErrorMessage(data: unknown, fallback: string): string {
  if (isRawApiResponse(data)) {
    return (
      (typeof data.error === "string" ? data.error : undefined) ||
      (typeof data.message === "string" ? data.message : undefined) ||
      (typeof data.detail === "string" ? data.detail : undefined) ||
      fallback
    );
  }
  return fallback;
}

interface User {
  id: string;
  email: string;
  name: string;
  name_ar?: string;
  role: "admin" | "supervisor" | "viewer";
  tenant_id?: string;
}

interface RequestOptions extends RequestInit {
  params?: Record<string, string>;
  skipRetry?: boolean;
  timeout?: number;
}

// Configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:3000";
const DEFAULT_TIMEOUT = 30000; // 30 seconds
const MAX_RETRY_ATTEMPTS = 3;
const RETRY_DELAY = 1000; // 1 second

// Enforce HTTPS in production
if (
  typeof window !== "undefined" &&
  process.env.NODE_ENV === "production" &&
  !API_BASE_URL.startsWith("https://") &&
  !API_BASE_URL.includes("localhost")
) {
  logger.warn(
    "Warning: API_BASE_URL should use HTTPS in production environment",
  );
}

// Helper function to sanitize HTML and prevent XSS using DOMPurify
function sanitizeInput(input: string): string {
  if (typeof input !== "string") return input;

  // Use DOMPurify with strict configuration - remove all HTML tags
  // ALLOWED_TAGS: [] means no HTML tags are allowed (pure text output)
  // ALLOWED_ATTR: [] means no attributes are allowed
  const sanitized = DOMPurify.sanitize(input, {
    ALLOWED_TAGS: [],
    ALLOWED_ATTR: [],
    KEEP_CONTENT: true,
  });

  // Remove null bytes and control characters
  return sanitized.replace(/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/g, "").trim();
}

// Helper function to delay for retry logic
function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

class AdminApiClient {
  private baseUrl: string;
  private token: string | null = null;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  setToken(token: string) {
    this.token = token;
  }

  clearToken() {
    this.token = null;
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

    // Build URL with query params
    let url = `${this.baseUrl}${endpoint}`;
    if (params) {
      const searchParams = new URLSearchParams(params);
      url += `?${searchParams.toString()}`;
    }

    // Set headers
    const headers: HeadersInit = {
      "Content-Type": "application/json",
      Accept: "application/json",
      "Accept-Language": "ar,en",
      ...options.headers,
    };

    if (this.token) {
      (headers as Record<string, string>)["Authorization"] =
        `Bearer ${this.token}`;
    }

    // Retry logic
    let lastError: Error | null = null;
    const maxAttempts = skipRetry ? 1 : MAX_RETRY_ATTEMPTS;

    for (let attempt = 0; attempt < maxAttempts; attempt++) {
      try {
        // Create AbortController for timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeout);

        const response = await fetch(url, {
          ...fetchOptions,
          headers,
          signal: controller.signal,
        });

        clearTimeout(timeoutId);

        // Parse response
        let data: unknown;
        const contentType = response.headers.get("content-type");

        if (contentType && contentType.includes("application/json")) {
          try {
            data = await response.json();
          } catch (parseError) {
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
          // Handle 401 Unauthorized - token expired or invalid
          if (response.status === 401) {
            this.clearToken();
            if (typeof window !== "undefined") {
              window.location.href = "/login";
            }
          }

          // Don't retry client errors (4xx), only server errors (5xx) and network issues
          if (response.status >= 400 && response.status < 500) {
            return {
              success: false,
              error: extractErrorMessage(
                data,
                `Request failed with status ${response.status}`,
              ),
            };
          }

          // For server errors, retry if we have attempts left
          if (attempt < maxAttempts - 1) {
            await delay(RETRY_DELAY * (attempt + 1)); // Exponential backoff
            continue;
          }

          return {
            success: false,
            error: extractErrorMessage(data, `Server error: ${response.status}`),
          };
        }

        // Successful response
        if (isRawApiResponse(data)) {
          return data as ApiResponse<T>;
        }
        return { success: true, data: data as T };
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

  async login(email: string, password: string, totp_code?: string) {
    // Sanitize email input to prevent XSS
    const sanitizedEmail = sanitizeInput(email);

    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(sanitizedEmail)) {
      return {
        success: false,
        error: "Invalid email format",
      };
    }

    const body: LoginRequestBody = { email: sanitizedEmail, password };
    if (totp_code) {
      body.totp_code = totp_code;
    }

    return this.request<{
      access_token: string;
      token_type: string;
      user: User;
      requires_2fa?: boolean;
      temp_token?: string;
    }>("/api/v1/auth/login", {
      method: "POST",
      body: JSON.stringify(body),
      skipRetry: true, // Don't retry auth requests
    });
  }

  async getCurrentUser() {
    return this.request<User>("/api/v1/auth/me");
  }

  async refreshToken(refreshToken: string) {
    return this.request<{ access_token: string }>("/api/v1/auth/refresh", {
      method: "POST",
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Generic API Methods (for existing endpoints)
  // ═══════════════════════════════════════════════════════════════════════════

  async get<T>(endpoint: string, params?: Record<string, string>) {
    return this.request<T>(endpoint, { method: "GET", params });
  }

  async post<T, B = Record<string, unknown>>(endpoint: string, body?: B) {
    return this.request<T>(endpoint, {
      method: "POST",
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  async patch<T, B = Record<string, unknown>>(
    endpoint: string,
    body?: B,
    params?: Record<string, string>,
  ) {
    return this.request<T>(endpoint, {
      method: "PATCH",
      body: body ? JSON.stringify(body) : undefined,
      params,
    });
  }

  async put<T, B = Record<string, unknown>>(endpoint: string, body?: B) {
    return this.request<T>(endpoint, {
      method: "PUT",
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  async delete<T>(endpoint: string) {
    return this.request<T>(endpoint, { method: "DELETE" });
  }
}

// Singleton instance
export const apiClient = new AdminApiClient();
export default apiClient;
