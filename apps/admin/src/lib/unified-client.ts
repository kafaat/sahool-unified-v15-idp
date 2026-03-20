// Unified API Client for Admin Portal
// عميل API الموحد للوحة الإدارة
//
// This module creates a configured SahoolApiClient instance from @sahool/api-client
// that replaces the raw axios instance previously defined in api.ts.
// Benefits: token refresh with queuing, retry with exponential backoff, HTTPS enforcement.

import { SahoolApiClient } from "@sahool/api-client";
import Cookies from "js-cookie";
import { API_BASE_URL, API_BASE_HOST, IS_PRODUCTION, TIMEOUT_TIERS } from "@/config/api";
import { apiClient as authApiClient } from "./api-client";
import { logger } from "./logger";

/**
 * Configured SahoolApiClient for the admin portal.
 *
 * Key behaviors:
 * - withCredentials: true (httpOnly cookies sent with every request)
 * - Token from js-cookie as fallback for non-httpOnly setups
 * - 401 → logout via Next.js API route + redirect to /login
 * - Token refresh via /api/auth/refresh proxy
 * - Retry with exponential backoff + jitter on transient errors
 * - HTTPS enforcement disabled in dev (localhost)
 */
export const sahoolClient = new SahoolApiClient(
  {
    baseUrl: IS_PRODUCTION ? API_BASE_URL : API_BASE_HOST,
    timeout: TIMEOUT_TIERS.default,
    locale: "ar",
    withCredentials: true,
    enforceHttps: IS_PRODUCTION,
    errorHandling: "throw",
    logLevel: "error",

    // Token from cookie (may be undefined with httpOnly cookies)
    getToken: () => Cookies.get("sahool_admin_token") ?? null,

    // 401 handler: logout + redirect
    onUnauthorized: async () => {
      try {
        await fetch("/api/auth/logout", {
          method: "POST",
          credentials: "same-origin",
        });
      } catch (logoutError) {
        logger.warn("Logout error:", logoutError);
      }
      authApiClient.clearToken();
      if (typeof window !== "undefined") {
        window.location.href = "/login";
      }
    },

    // Token refresh via Next.js proxy
    tokenRefresh: {
      refreshToken: async () => {
        try {
          const res = await fetch("/api/auth/refresh", {
            method: "POST",
            credentials: "same-origin",
          });
          if (!res.ok) return null;
          const data = await res.json();
          const token = data.access_token ?? data.token;
          if (token) {
            Cookies.set("sahool_admin_token", token);
            return token;
          }
          return null;
        } catch {
          return null;
        }
      },
      maxRefreshAttempts: 1,
    },

    // Retry transient failures
    retry: {
      maxRetries: 3,
      baseDelay: 1000,
      maxDelay: 30000,
      retryableStatuses: [408, 429, 500, 502, 503, 504],
      retryOnNetworkError: true,
    },
  },
);

/**
 * The underlying axios instance from the unified client.
 * Drop-in replacement for the old `apiClient` in api.ts.
 *
 * Uses the same fully-qualified API_URLS from @/config/api — no URL changes needed.
 */
export const apiClient = sahoolClient.axiosInstance;
