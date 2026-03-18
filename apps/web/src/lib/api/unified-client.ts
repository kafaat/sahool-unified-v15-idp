/**
 * SAHOOL Unified API Client (Web)
 * عميل API الموحد للويب
 *
 * Wraps @sahool/api-client with web-specific configuration:
 * - httpOnly cookie-based token management
 * - CSRF double-submit cookie protection
 * - Token refresh via /api/auth/session
 * - Cross-tab logout via BroadcastChannel
 *
 * Usage:
 *   import { sahoolClient, unifiedApiClient } from "./unified-client";
 *   // sahoolClient — full SahoolApiClient instance (domain methods)
 *   // unifiedApiClient — raw AxiosInstance (for factory.ts / feature modules)
 */

import { SahoolApiClient } from "@sahool/api-client";
import Cookies from "js-cookie";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "";
const IS_PRODUCTION = process.env.NODE_ENV === "production";

// ─── Shared Client Instance ─────────────────────────────────────────────────

export const sahoolClient = new SahoolApiClient({
  baseUrl: API_BASE_URL,
  timeout: 15000,
  locale: "ar",
  withCredentials: true,
  enforceHttps: IS_PRODUCTION,
  errorHandling: "throw",
  logLevel: IS_PRODUCTION ? "error" : "info",

  // Read JWT from httpOnly-adjacent cookie (set by /api/auth/session)
  getToken: () => Cookies.get("access_token") ?? null,

  onUnauthorized: async () => {
    if (typeof window !== "undefined") {
      window.dispatchEvent(new CustomEvent("auth:session-expired"));
    }
  },

  tokenRefresh: {
    refreshToken: async () => {
      try {
        if (typeof window === "undefined") return null;
        const refreshTokenValue = Cookies.get("refresh_token");
        if (!refreshTokenValue) return null;

        const res = await fetch(
          `${API_BASE_URL}/api/v1/auth/refresh`,
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ refresh_token: refreshTokenValue }),
            credentials: "include",
          },
        );
        if (!res.ok) return null;

        const data = await res.json();
        const newToken = data?.access_token ?? data?.data?.access_token ?? null;
        if (newToken) {
          // Clear legacy path-scoped cookie, then set root-scoped one
          Cookies.remove("access_token");
          Cookies.set("access_token", newToken, {
            expires: 7,
            secure: window.location.protocol === "https:",
            sameSite: "strict",
            path: "/",
          });
        }
        return newToken;
      } catch {
        return null;
      }
    },
    maxRefreshAttempts: 1,
  },

  retry: {
    maxRetries: 3,
    baseDelay: 1000,
    maxDelay: 30000,
    retryableStatuses: [408, 429, 500, 502, 503, 504],
    retryOnNetworkError: true,
  },
});

// ─── CSRF Interceptor ────────────────────────────────────────────────────────
// The shared @sahool/api-client doesn't include CSRF protection.
// Web app uses double-submit cookie: httpOnly `csrf_token` + readable `_csrf`.

sahoolClient.axiosInstance.interceptors.request.use((config) => {
  if (typeof window !== "undefined" && config.method !== "get") {
    const csrfToken = Cookies.get("_csrf");
    if (csrfToken) {
      config.headers["X-CSRF-Token"] = csrfToken;
    }
  }
  return config;
});

// ─── Exports ─────────────────────────────────────────────────────────────────

/** Raw AxiosInstance for feature modules via factory.ts */
export const unifiedApiClient = sahoolClient.axiosInstance;
