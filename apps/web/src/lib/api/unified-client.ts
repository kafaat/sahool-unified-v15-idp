/**
 * SAHOOL Unified API Client (Web)
 * عميل API الموحد للويب
 *
 * Wraps @sahool/api-client with web-specific configuration:
 * - httpOnly cookie-based auth (cookies sent automatically via withCredentials)
 * - CSRF double-submit cookie protection
 * - Token refresh via Next.js server-side proxy (/api/auth/refresh)
 *
 * Note: access_token and refresh_token are httpOnly cookies — they cannot
 * be read by client-side JS. Auth works because withCredentials: true
 * sends cookies automatically, and the backend reads them directly.
 * Token refresh uses a same-origin proxy that can read the httpOnly cookie.
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

  // getToken returns null for httpOnly cookies — auth is handled by the
  // browser automatically sending cookies with withCredentials: true.
  // The backend reads the token from the cookie, not from Authorization header.
  getToken: () => null,

  onUnauthorized: async () => {
    if (typeof window !== "undefined") {
      window.dispatchEvent(new CustomEvent("auth:session-expired"));
    }
  },

  tokenRefresh: {
    // Uses a same-origin Next.js API route that can read the httpOnly
    // refresh_token cookie server-side and forward it to the backend.
    refreshToken: async () => {
      try {
        if (typeof window === "undefined") return null;

        const res = await fetch("/api/auth/refresh", {
          method: "POST",
          credentials: "same-origin",
        });
        if (!res.ok) return null;

        const data = await res.json();
        // The proxy route already set the new httpOnly cookie.
        // Return the token so the shared client can retry the failed request.
        return data?.access_token ?? null;
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
  const method = config.method?.toLowerCase();
  if (typeof window !== "undefined" && method && method !== "get") {
    const csrfToken = Cookies.get("_csrf");
    if (csrfToken) {
      config.headers.set("X-CSRF-Token", csrfToken);
    }
  }
  return config;
});

// ─── Exports ─────────────────────────────────────────────────────────────────

/** Raw AxiosInstance for feature modules via factory.ts */
export const unifiedApiClient = sahoolClient.axiosInstance;
