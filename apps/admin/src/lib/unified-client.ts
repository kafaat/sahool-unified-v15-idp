// Unified API Client for Admin Portal
// عميل API الموحد للوحة الإدارة
//
// This module creates a configured SahoolApiClient instance from @sahool/api-client
// that replaces the raw axios instance previously defined in api.ts.
// Benefits: token refresh with queuing, retry with exponential backoff, HTTPS enforcement.

import { SahoolApiClient } from '@sahool/api-client';
import Cookies from 'js-cookie';
import { API_BASE_URL, API_BASE_HOST, IS_PRODUCTION, TIMEOUT_TIERS } from '@/config/api';
import { apiClient as authApiClient } from './api-client';
import { logger } from './logger';

/**
 * In-memory token store — keeps the refreshed access token alive for the
 * current browser session without ever writing it to a JS-readable cookie.
 *
 * Security rationale:
 * - The server sets `sahool_admin_token` as httpOnly on login/refresh.
 * - httpOnly cookies cannot be read by JavaScript (XSS-safe).
 * - After a token refresh the server has already updated the httpOnly cookie.
 *   We also cache the new value in memory so SahoolApiClient can attach it as
 *   `Authorization: Bearer …` for direct backend requests that don't go through
 *   the Next.js proxy (where the httpOnly cookie would not be forwarded).
 * - Storing in memory (not document.cookie) means an XSS payload cannot steal
 *   the token across page loads — it is destroyed when the page unloads.
 */
let _inMemoryToken: string | null = null;

/**
 * Configured SahoolApiClient for the admin portal.
 *
 * Key behaviors:
 * - withCredentials: true (httpOnly cookies sent with every request)
 * - Token from in-memory store (post-refresh) or js-cookie fallback for
 *   non-httpOnly development setups
 * - 401 → logout via Next.js API route + redirect to /login
 * - Token refresh via /api/auth/refresh proxy
 * - Retry with exponential backoff + jitter on transient errors
 * - HTTPS enforcement disabled in dev (localhost)
 */
export const sahoolClient = new SahoolApiClient({
  baseUrl: IS_PRODUCTION ? API_BASE_URL : API_BASE_HOST,
  timeout: TIMEOUT_TIERS.default,
  locale: 'ar',
  withCredentials: true,
  enforceHttps: IS_PRODUCTION,
  errorHandling: 'throw',
  logLevel: 'error',

  // Read from in-memory store first (set after refresh), then fall back to a
  // non-httpOnly cookie that may exist in development / non-proxy setups.
  // httpOnly cookies are deliberately excluded here — they cannot be read by JS
  // and the server sends them automatically via withCredentials.
  getToken: () => _inMemoryToken ?? Cookies.get('sahool_admin_token') ?? null,

  // 401 handler: logout + redirect
  onUnauthorized: async () => {
    _inMemoryToken = null;
    try {
      await fetch('/api/auth/logout', {
        method: 'POST',
        credentials: 'same-origin',
      });
    } catch (logoutError) {
      logger.error('Logout error:', logoutError);
    }
    authApiClient.clearToken();
    if (typeof window !== 'undefined') {
      window.location.href = '/login';
    }
  },

  // Token refresh via Next.js proxy.
  // The proxy route (/api/auth/refresh) updates the httpOnly cookie server-side.
  // We also cache the new access token in memory so it can be used as a Bearer
  // token for direct backend requests without writing to a JS-readable cookie.
  tokenRefresh: {
    refreshToken: async () => {
      try {
        const res = await fetch('/api/auth/refresh', {
          method: 'POST',
          credentials: 'same-origin',
        });
        if (!res.ok) {
          _inMemoryToken = null;
          return null;
        }
        const data = await res.json();
        if (data.token) {
          // Store in memory only — never write to a JS-readable cookie.
          // The server already updated the httpOnly cookie.
          _inMemoryToken = data.token;
          return data.token;
        }
        return null;
      } catch {
        _inMemoryToken = null;
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
});

/**
 * The underlying axios instance from the unified client.
 * Drop-in replacement for the old `apiClient` in api.ts.
 *
 * Uses the same fully-qualified API_URLS from @/config/api — no URL changes needed.
 */
export const apiClient = sahoolClient.axiosInstance;
