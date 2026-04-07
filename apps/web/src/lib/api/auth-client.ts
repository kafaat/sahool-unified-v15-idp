/**
 * SAHOOL Auth API Client (Lightweight)
 * عميل API المصادقة الخفيف
 *
 * Minimal API client for authentication operations only.
 * Used by the auth store to avoid pulling the full 1300-line api/client.ts
 * (with all domain types, validation, and security modules) into auth page bundles.
 *
 * The full `apiClient` from `./client.ts` should be used for dashboard pages
 * that need field, weather, sensor, irrigation, and other domain API methods.
 */

import { logger } from '../logger';
import Cookies from 'js-cookie';

// ---------------------------------------------------------------------------
// Types (inline to avoid importing the 510-line types.ts)
// ---------------------------------------------------------------------------

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface AuthUser {
  id: string;
  email: string;
  name: string;
  name_ar?: string;
  role: string;
  tenant_id?: string;
}

interface LoginResponse {
  access_token: string;
  refresh_token?: string;
  user: AuthUser;
}

// ---------------------------------------------------------------------------
// Config
// ---------------------------------------------------------------------------

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';
const DEFAULT_TIMEOUT = 30000;

// ---------------------------------------------------------------------------
// Client
// ---------------------------------------------------------------------------

class AuthApiClient {
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

    // Clear cookies to prevent stale tokens from being sent
    // Uses both root-scoped and unscoped removal for backwards compatibility
    if (typeof window !== 'undefined') {
      Cookies.remove('access_token', { path: '/' });
      Cookies.remove('refresh_token', { path: '/' });
      // Legacy path-scoped removal (cookies set without explicit path)
      Cookies.remove('access_token');
      Cookies.remove('refresh_token');
    }
  }

  // -------------------------------------------------------------------------
  // Core request (auth-only, no CSRF, no domain types)
  // -------------------------------------------------------------------------

  private async request<T>(
    endpoint: string,
    options: RequestInit & { timeout?: number } = {}
  ): Promise<ApiResponse<T>> {
    const { timeout = DEFAULT_TIMEOUT, ...fetchOptions } = options;

    const url = `${this.baseUrl}${endpoint}`;

    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.token) {
      (headers as Record<string, string>)['Authorization'] = `Bearer ${this.token}`;
    }

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), timeout);

      let response: Response;
      try {
        response = await fetch(url, {
          ...fetchOptions,
          headers,
          signal: controller.signal,
          credentials: 'include',
        });
      } finally {
        clearTimeout(timeoutId);
      }

      let data: any;
      const contentType = response.headers.get('content-type');

      if (contentType && contentType.includes('application/json')) {
        try {
          data = await response.json();
        } catch {
          return { success: false, error: 'Invalid JSON response from server' };
        }
      } else {
        data = await response.text();
      }

      if (!response.ok) {
        return {
          success: false,
          error: data?.error || data?.message || `Request failed with status ${response.status}`,
        };
      }

      return typeof data === 'object' && data !== null ? data : { success: true, data: data as T };
    } catch (error) {
      if (error instanceof Error && error.name === 'AbortError') {
        return { success: false, error: 'Request timeout' };
      }
      return {
        success: false,
        error:
          error instanceof Error ? error.message : 'Network error - please check your connection',
      };
    }
  }

  // -------------------------------------------------------------------------
  // Auth endpoints
  // -------------------------------------------------------------------------

  async login(email: string, password: string) {
    // Basic email validation (avoids importing the full validation.ts)
    const trimmedEmail = email.trim().toLowerCase();
    if (!trimmedEmail || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(trimmedEmail)) {
      return { success: false as const, error: 'Invalid email format' };
    }

    return this.request<LoginResponse>('/api/v1/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email: trimmedEmail, password }),
    });
  }

  async getCurrentUser() {
    return this.request<AuthUser>('/api/v1/auth/me');
  }

  /**
   * Gap #4: Token refresh must go through the Next.js server-side proxy
   * (/api/auth/refresh) which reads the httpOnly refresh_token cookie.
   * The httpOnly cookie cannot be accessed by client-side JavaScript.
   */
  async refreshToken() {
    const response = await fetch('/api/auth/refresh', { method: 'POST', credentials: 'include' });
    if (!response.ok) {
      throw new Error('Token refresh failed');
    }
    return response.json() as Promise<{ success: boolean; access_token?: string }>;
  }

  /**
   * Attempt to refresh the access token using the httpOnly refresh_token cookie
   * via the server-side proxy route. Returns true if successful, false otherwise.
   */
  async attemptTokenRefresh(): Promise<boolean> {
    try {
      if (typeof window === 'undefined') return false;

      // Gap #4: use server-side proxy which reads the httpOnly refresh_token cookie.
      // Direct Cookies.get('refresh_token') would fail because it is httpOnly.
      const response = await this.refreshToken();

      if (response.success && response.access_token) {
        this.setToken(response.access_token);
        return true;
      } else {
        this.clearToken();
        return false;
      }
    } catch (error) {
      logger.error('Error refreshing token:', error);
      return false;
    }
  }
}

// Singleton instance
export const authApiClient = new AuthApiClient();
