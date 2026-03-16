/**
 * SAHOOL Admin API Client v16.0.0
 * عميل API لوحة التحكم الإدارية - سهول
 *
 * Unified API client for admin dashboard with:
 * - Role-Based Access Control (RBAC) integration
 * - Audit logging for admin actions
 * - Centralized token management
 * - Bilingual error handling (Arabic/English)
 *
 * ميزات العميل:
 * - تكامل التحكم في الوصول المستند إلى الدور (RBAC)
 * - تسجيل التدقيق لإجراءات المسؤول
 * - إدارة الرموز المركزية
 * - معالجة الأخطاء ثنائية اللغة (العربية/الإنجليزية)
 */

import { sanitizeInput } from "./sanitize";
import { logger } from "./logger";
import {
  API_BASE_URL,
  DEFAULT_TIMEOUT,
  MAX_RETRY_ATTEMPTS,
  RETRY_DELAY,
  IS_PRODUCTION,
} from "@/config/api";

// =============================================================================
// Types & Interfaces | الأنواع والواجهات
// =============================================================================

interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: string;
  errorAr?: string;
  errorCode?: string;
  requestId?: string;
}

/**
 * Admin user roles | أدوار المستخدم الإداري
 */
export type AdminRole = "super_admin" | "admin" | "supervisor" | "viewer";

/**
 * Permission types | أنواع الصلاحيات
 */
export type Permission =
  | "users:read"
  | "users:write"
  | "users:delete"
  | "fields:read"
  | "fields:write"
  | "fields:delete"
  | "reports:read"
  | "reports:export"
  | "settings:read"
  | "settings:write"
  | "audit:read"
  | "billing:read"
  | "billing:write";

/**
 * Audit log entry | سجل التدقيق
 */
export interface AuditLogEntry {
  id: string;
  timestamp: string;
  action: string;
  actionAr: string;
  resource: string;
  resourceId?: string;
  userId: string;
  userEmail: string;
  ipAddress?: string;
  userAgent?: string;
  details?: Record<string, unknown>;
  success: boolean;
}

/**
 * RBAC context | سياق التحكم في الوصول
 */
interface RBACContext {
  role: AdminRole;
  permissions: Permission[];
  tenantId?: string;
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

// Helper function to delay for retry logic
function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// =============================================================================
// RBAC (Role-Based Access Control) | التحكم في الوصول المستند إلى الدور
// =============================================================================

/**
 * Role permissions mapping | خريطة صلاحيات الأدوار
 */
const ROLE_PERMISSIONS: Record<AdminRole, Permission[]> = {
  super_admin: [
    "users:read", "users:write", "users:delete",
    "fields:read", "fields:write", "fields:delete",
    "reports:read", "reports:export",
    "settings:read", "settings:write",
    "audit:read",
    "billing:read", "billing:write",
  ],
  admin: [
    "users:read", "users:write",
    "fields:read", "fields:write", "fields:delete",
    "reports:read", "reports:export",
    "settings:read", "settings:write",
    "audit:read",
    "billing:read",
  ],
  supervisor: [
    "users:read",
    "fields:read", "fields:write",
    "reports:read",
    "settings:read",
  ],
  viewer: [
    "users:read",
    "fields:read",
    "reports:read",
  ],
};

class AdminApiClient {
  private baseUrl: string;
  private token: string | null = null;
  private rbacContext: RBACContext | null = null;
  private auditQueue: AuditLogEntry[] = [];
  private auditFlushTimer: ReturnType<typeof setTimeout> | null = null;
  private currentUserId: string = "";
  private currentUserEmail: string = "";
  private onUnauthorized: (() => void) | null = null;

  constructor(baseUrl: string = API_BASE_URL) {
    // Block HTTP in production instead of just warning
    if (
      IS_PRODUCTION &&
      !baseUrl.startsWith("https://") &&
      !baseUrl.includes("localhost")
    ) {
      throw new Error(
        "API_BASE_URL must use HTTPS in production. " +
        "يجب استخدام HTTPS في بيئة الإنتاج"
      );
    }
    this.baseUrl = baseUrl;
  }

  setToken(token: string) {
    this.token = token;
  }

  setUserContext(userId: string, email: string) {
    this.currentUserId = userId;
    this.currentUserEmail = email;
  }

  setOnUnauthorized(callback: () => void) {
    this.onUnauthorized = callback;
  }

  clearToken() {
    this.token = null;
    this.rbacContext = null;
    this.currentUserId = "";
    this.currentUserEmail = "";
  }

  // ===========================================================================
  // RBAC Methods | طرق التحكم في الوصول
  // ===========================================================================

  /**
   * Set RBAC context after login
   * تعيين سياق التحكم في الوصول بعد تسجيل الدخول
   */
  setRBACContext(role: AdminRole, tenantId?: string): void {
    this.rbacContext = {
      role,
      permissions: ROLE_PERMISSIONS[role] || [],
      tenantId,
    };
    logger.info(`RBAC context set for role: ${role}`);
  }

  /**
   * Check if user has permission
   * التحقق من وجود صلاحية للمستخدم
   */
  hasPermission(permission: Permission): boolean {
    if (!this.rbacContext) return false;
    return this.rbacContext.permissions.includes(permission);
  }

  /**
   * Check if user has any of the permissions
   * التحقق من وجود أي من الصلاحيات
   */
  hasAnyPermission(permissions: Permission[]): boolean {
    return permissions.some((p) => this.hasPermission(p));
  }

  /**
   * Check if user has all permissions
   * التحقق من وجود جميع الصلاحيات
   */
  hasAllPermissions(permissions: Permission[]): boolean {
    return permissions.every((p) => this.hasPermission(p));
  }

  /**
   * Get current role
   * الحصول على الدور الحالي
   */
  getCurrentRole(): AdminRole | null {
    return this.rbacContext?.role || null;
  }

  /**
   * Get all permissions for current user
   * الحصول على جميع صلاحيات المستخدم الحالي
   */
  getPermissions(): Permission[] {
    return this.rbacContext?.permissions || [];
  }

  // ===========================================================================
  // Audit Logging | تسجيل التدقيق
  // ===========================================================================

  /**
   * Log an admin action for audit trail
   * تسجيل إجراء إداري لمسار التدقيق
   */
  async logAuditAction(
    action: string,
    actionAr: string,
    resource: string,
    resourceId?: string,
    details?: Record<string, unknown>,
    success: boolean = true
  ): Promise<void> {
    const entry: AuditLogEntry = {
      id: crypto.randomUUID(),
      timestamp: new Date().toISOString(),
      action,
      actionAr,
      resource,
      resourceId,
      userId: this.currentUserId,
      userEmail: this.currentUserEmail,
      details,
      success,
    };

    this.auditQueue.push(entry);

    if (this.auditQueue.length >= 10) {
      await this.flushAuditLogs();
    } else if (!this.auditFlushTimer) {
      this.auditFlushTimer = setTimeout(() => {
        this.flushAuditLogs();
      }, 5000);
    }
  }

  private async flushAuditLogs(): Promise<void> {
    if (this.auditFlushTimer) {
      clearTimeout(this.auditFlushTimer);
      this.auditFlushTimer = null;
    }

    if (this.auditQueue.length === 0) return;

    const logsToSend = [...this.auditQueue];
    this.auditQueue = [];

    try {
      await this.post("/api/v1/admin/audit/batch", { entries: logsToSend });
      logger.info(`Flushed ${logsToSend.length} audit log entries`);
    } catch (error) {
      this.auditQueue = [...logsToSend, ...this.auditQueue];
      logger.error("Failed to flush audit logs", error);
    }
  }

  async getAuditLogs(options: {
    page?: number;
    limit?: number;
    userId?: string;
    action?: string;
    resource?: string;
    startDate?: string;
    endDate?: string;
  }): Promise<ApiResponse<{ data: AuditLogEntry[]; total: number; page: number }>> {
    if (!this.hasPermission("audit:read")) {
      return {
        success: false,
        error: "Permission denied: audit:read required",
        errorAr: "الوصول مرفوض: صلاحية قراءة التدقيق مطلوبة",
      };
    }

    const params: Record<string, string> = {};
    if (options.page) params.page = String(options.page);
    if (options.limit) params.limit = String(options.limit);
    if (options.userId) params.user_id = options.userId;
    if (options.action) params.action = options.action;
    if (options.resource) params.resource = options.resource;
    if (options.startDate) params.start_date = options.startDate;
    if (options.endDate) params.end_date = options.endDate;

    return this.get("/api/v1/admin/audit", params);
  }

  // ===========================================================================
  // Private Request Method | طريقة الطلب الخاصة
  // ===========================================================================

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

    let url = `${this.baseUrl}${endpoint}`;
    if (params) {
      const searchParams = new URLSearchParams(params);
      url += `?${searchParams.toString()}`;
    }

    const headers: HeadersInit = {
      "Content-Type": "application/json",
      Accept: "application/json",
      "Accept-Language": "ar,en",
      "X-Request-ID": crypto.randomUUID(),
      ...options.headers,
    };

    if (this.token) {
      (headers as Record<string, string>)["Authorization"] =
        `Bearer ${this.token}`;
    }

    if (this.rbacContext?.tenantId) {
      (headers as Record<string, string>)["X-Tenant-Id"] =
        this.rbacContext.tenantId;
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
          // Handle 401 Unauthorized - token expired or invalid
          if (response.status === 401) {
            this.clearToken();
            if (this.onUnauthorized) {
              this.onUnauthorized();
            } else if (typeof window !== "undefined") {
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

/** Extract Arabic error message from response */
export function extractErrorMessageAr(data: unknown, fallback: string): string {
  if (isRawApiResponse(data)) {
    const raw = data as { error_ar?: string; message_ar?: string };
    return (
      (typeof raw.error_ar === "string" ? raw.error_ar : undefined) ||
      (typeof raw.message_ar === "string" ? raw.message_ar : undefined) ||
      fallback
    );
  }
  return fallback;
}

// Singleton instance
export const apiClient = new AdminApiClient();
export default apiClient;
