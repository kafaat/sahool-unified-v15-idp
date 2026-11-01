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

import Cookies from 'js-cookie';
import { logger } from '../logger';

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
  expires_in?: number;
  token_type?: string;
  user: AuthUser & { firstName?: string; lastName?: string; tenantId?: string };
}

interface RegistrationAcknowledgement {
  success: true;
  message: string;
  access_token?: never;
  refresh_token?: never;
}

function isJsonObject(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

async function readAuthPayload(response: Response): Promise<Record<string, unknown> | null> {
  try {
    const data: unknown = await response.json();
    return isJsonObject(data) ? data : null;
  } catch {
    return null;
  }
}

function isNonEmptyString(value: unknown): value is string {
  return typeof value === 'string' && value.trim().length > 0;
}

function getAuthError(data: Record<string, unknown>, fallback: string): string {
  if (isNonEmptyString(data.error)) return data.error;
  if (isNonEmptyString(data.message)) return data.message;
  return fallback;
}

function isLoginPayload(
  data: Record<string, unknown>
): data is Record<string, unknown> & LoginResponse {
  // The auth store immediately creates a session and consumes the user's ID.
  return (
    isNonEmptyString(data.access_token)
    && isJsonObject(data.user)
    && isNonEmptyString(data.user.id)
  );
}

function isRegistrationAcknowledgement(
  data: Record<string, unknown>
): data is Record<string, unknown> & RegistrationAcknowledgement {
  // Existing-account registration deliberately returns a token-free success
  // envelope to avoid revealing whether an email address is registered.
  return (
    data.success === true
    && isNonEmptyString(data.message)
    && data.access_token === undefined
    && data.refresh_token === undefined
    && data.user === undefined
  );
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

  protected async request<T>(
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

      return { success: true as const, data: data as T };
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

  async login(identifier: string, password: string) {
    const trimmed = identifier.trim();
    if (!trimmed) {
      return { success: false as const, error: 'Email or phone is required' };
    }

    const isEmail = trimmed.includes('@');
    if (isEmail && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(trimmed)) {
      return { success: false as const, error: 'Invalid email format' };
    }

    // Send email or phone as the appropriate field so backend validation passes
    const body = isEmail
      ? { email: trimmed.toLowerCase(), password }
      : { phone: trimmed, password };

    // Route through the Next.js server-side proxy (/api/auth/login) instead of
    // calling Kong directly. This avoids the browser→Kong CORS issue (wildcard
    // origin + credentials:false) and lets the proxy set httpOnly cookies.
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), DEFAULT_TIMEOUT);
      let response: Response;
      try {
        response = await fetch('/api/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body),
          credentials: 'include',
          signal: controller.signal,
        });
      } finally {
        clearTimeout(timeoutId);
      }
      const data = await readAuthPayload(response);
      if (!data) {
        return { success: false as const, error: 'Invalid JSON response from server' };
      }
      if (!response.ok || data.success === false) {
        return {
          success: false as const,
          error: getAuthError(
            data, response.ok ? 'Login failed' : `Request failed with status ${response.status}`
          ),
        };
      }
      if (!isLoginPayload(data)) {
        return { success: false as const, error: 'Invalid login response from server' };
      }
      return { success: true as const, data };
    } catch (error) {
      if (error instanceof Error && error.name === 'AbortError') {
        return { success: false as const, error: 'Request timeout' };
      }
      return {
        success: false as const,
        error: error instanceof Error ? error.message : 'Network error - please check your connection',
      };
    }
  }

  /**
   * Self-registration. Routes through the same Next.js rewrite as login
   * (`/api/v1/auth/register` → Kong → user-service). Replaces a raw
   * `fetch(${NEXT_PUBLIC_API_URL}/api/v1/auth/register)` call that
   * `RegisterClient.tsx` used to make.
   *
   * What this client actually provides (vs what it does NOT):
   *   * provides : 30 s default request timeout (DEFAULT_TIMEOUT),
   *                same-origin cookie credentials (via `request()`),
   *                a `{ success, ... }` discriminated-union return —
   *                ERRORS ARE RETURNED, NOT THROWN, except for the
   *                token-refresh path (which throws on failure).
   *   * does NOT : automatic retry on transient failure, CSRF
   *                double-submit token injection (auth endpoints are
   *                anonymous so CSRF is unnecessary), bilingual error
   *                normalization (the caller is responsible for
   *                surfacing `messageAr` if present in the response).
   *   For richer behavior use `unifiedApiClient` from
   *   `lib/api/unified-client.ts`, which adds CSRF + interceptors.
   *
   * `phone` is normalized by the caller (RegisterClient handles the
   * Yemen-specific operator detection + +967 prefix).
   */
  async register(input: {
    email?: string;
    phone?: string;
    password: string;
    firstName: string;
    lastName: string;
  }) {
    // Normalise email BEFORE validation so a value like ` user@x.com `
    // isn't rejected as "Invalid email format" only to be silently
    // accepted by the body's `.toLowerCase().trim()` a few lines down.
    const normalizedEmail = input.email?.toLowerCase().trim();

    if (!normalizedEmail && !input.phone) {
      return {
        success: false as const,
        error: 'Either email or phone is required',
      };
    }
    if (normalizedEmail && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(normalizedEmail)) {
      return { success: false as const, error: 'Invalid email format' };
    }

    // Route through the Next.js server-side proxy (/api/auth/register) instead of
    // calling Kong directly. Avoids browser→Kong CORS failure.
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), DEFAULT_TIMEOUT);
      let response: Response;
      try {
        response = await fetch('/api/auth/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email: normalizedEmail || undefined,
            phone: input.phone || undefined,
            password: input.password,
            firstName: input.firstName.trim(),
            lastName: input.lastName.trim(),
          }),
          credentials: 'include',
          signal: controller.signal,
        });
      } finally {
        clearTimeout(timeoutId);
      }
      const data = await readAuthPayload(response);
      if (!data) {
        return { success: false as const, error: 'Invalid JSON response from server' };
      }
      if (!response.ok || data.success === false) {
        return {
          success: false as const,
          error: getAuthError(
            data, response.ok ? 'Registration failed' : `Request failed with status ${response.status}`
          ),
        };
      }
      if (!isLoginPayload(data) && !isRegistrationAcknowledgement(data)) {
        return { success: false as const, error: 'Invalid registration response from server' };
      }
      return { success: true as const, data };
    } catch (error) {
      if (error instanceof Error && error.name === 'AbortError') {
        return { success: false as const, error: 'Request timeout' };
      }
      return {
        success: false as const,
        error: error instanceof Error ? error.message : 'Network error - please check your connection',
      };
    }
  }

  async getCurrentUser() {
    // Use the Next.js server-side proxy which decodes the httpOnly cookie.
    // The backend POST /api/v1/auth/me endpoint is not reliably reachable
    // from the browser (Kong routing + httpOnly cookie constraints).
    const response = await fetch('/api/auth/me', { credentials: 'include' });
    if (!response.ok) {
      return { success: false as const, error: 'No active session' };
    }
    return response.json() as Promise<{ success: boolean; data?: AuthUser; error?: string }>;
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
      this.clearToken();
      return false;
    }
  }
}

// Singleton instance
export const authApiClient = new AuthApiClient();
