'use client';
import * as React from 'react';
import Cookies from 'js-cookie';
import { authApiClient } from '@/lib/api/auth-client';
import { logger } from '@/lib/logger';

/**
 * Fetch CSRF token from the server
 * جلب رمز CSRF من الخادم
 *
 * SECURITY: CSRF tokens are required for all state-changing requests.
 * If token fetch fails, subsequent requests may fail with 403.
 */
export async function fetchCsrfToken(): Promise<boolean> {
  try {
    const response = await fetch('/api/csrf-token');
    if (response.ok) {
      // Token is automatically set in cookie by the API route
      return true;
    }
    logger.error('CSRF token fetch failed with status:', response.status);
    return false;
  } catch (error) {
    logger.error('Failed to fetch CSRF token:', error);
    // SECURITY: Treat CSRF failure as critical - log for monitoring
    return false;
  }
}

/**
 * Check if E2E test mode is explicitly enabled
 * تحقق من تمكين وضع اختبار E2E صراحةً
 *
 * SECURITY: This function ONLY returns true when:
 * 1. NODE_ENV is explicitly "development" (never in production)
 * 2. NEXT_PUBLIC_E2E_TEST environment variable is explicitly "true"
 *
 * The localhost check has been REMOVED as it could be bypassed.
 */
export function isE2ETestModeEnabled(): boolean {
  // CRITICAL: Production builds MUST have NODE_ENV=production
  if (process.env.NODE_ENV !== 'development') {
    return false;
  }

  // SECURITY: Require explicit E2E flag - no implicit localhost detection
  return process.env.NEXT_PUBLIC_E2E_TEST === 'true';
}

/**
 * Attempt to load mock user session for E2E testing
 * محاولة تحميل جلسة مستخدم وهمية لاختبار E2E
 *
 * SECURITY: This function should ONLY be called after isE2ETestModeEnabled() returns true
 */
export function tryLoadMockSession(): User | null {
  if (!isE2ETestModeEnabled()) {
    return null;
  }

  const mockSession = Cookies.get('user_session');
  if (!mockSession) {
    return null;
  }

  try {
    const mockUser = JSON.parse(mockSession);
    logger.warn(
      '[SECURITY WARNING] Using mock authentication - E2E test mode only. ' +
        'This should NEVER appear in production logs.'
    );
    return {
      id: mockUser.id || 'test-user',
      email: mockUser.email || 'test@sahool.com',
      name: mockUser.name || 'Test User',
      name_ar: mockUser.nameAr || 'مستخدم اختباري',
      role: mockUser.role || 'user',
    };
  } catch {
    logger.warn('Invalid mock session format');
    return null;
  }
}

interface User {
  id: string;
  email: string;
  name: string;
  name_ar?: string;
  role: string;
  tenant_id?: string;
}

/** Validate UUID v4 format for tenant IDs to prevent injection */
const UUID_REGEX = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

function sanitizeUser(data: User): User {
  const user = { ...data };
  if (user.tenant_id && !UUID_REGEX.test(user.tenant_id)) {
    logger.error('Invalid tenant_id format, clearing value');
    user.tenant_id = undefined;
  }
  return user;
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<void>;
}

const AuthContext = React.createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = React.useState<User | null>(null);
  const [isLoading, setIsLoading] = React.useState(true);

  const login = React.useCallback(async (email: string, password: string) => {
    const response = await authApiClient.login(email, password);
    if (response.success && response.data) {
      const { access_token, refresh_token, user } = response.data;

      // Set cookies via secure server-side API route
      // This ensures httpOnly flag is set, preventing XSS attacks
      const sessionResponse = await fetch('/api/auth/session', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          access_token,
          refresh_token,
        }),
      });

      if (!sessionResponse.ok) {
        throw new Error('Failed to create secure session');
      }

      // Set token in API client for immediate use
      // Note: Subsequent requests will use the httpOnly cookie automatically
      authApiClient.setToken(access_token);

      // User type from API matches our User interface
      setUser(sanitizeUser(user));

      // Fetch CSRF token for subsequent requests
      await fetchCsrfToken();
    } else {
      throw new Error(response.error || 'Login failed');
    }
  }, []);

  const logout = React.useCallback(async () => {
    // Remove cookies via secure server-side API route with timeout
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);
      try {
        await fetch('/api/auth/session', {
          method: 'DELETE',
          signal: controller.signal,
        });
      } finally {
        clearTimeout(timeoutId);
      }
    } catch (error) {
      // Continue with logout even if API call fails
      logger.error('Failed to clear session cookies:', error);
    }

    // Clear all client-accessible cookies.
    // httpOnly cookies (access_token, refresh_token, csrf_token) are cleared
    // server-side by DELETE /api/auth/session, but if that request failed
    // we still need to clean up any non-httpOnly copies the browser may hold.
    Cookies.remove('_csrf', { path: '/' });
    Cookies.remove('access_token', { path: '/' });
    Cookies.remove('refresh_token', { path: '/' });

    // Also remove legacy path-scoped cookies (set without explicit path by
    // older builds, which default to the current route). Without this, a
    // stale cookie scoped to e.g. /dashboard could shadow the root removal.
    Cookies.remove('access_token');
    Cookies.remove('refresh_token');

    // Clear E2E mock session cookie so logout is fully effective in test mode
    if (isE2ETestModeEnabled()) {
      Cookies.remove('user_session', { path: '/' });
    }

    // Notify other tabs about logout
    try {
      if (typeof BroadcastChannel !== 'undefined') {
        const channel = new BroadcastChannel('sahool_auth');
        channel.postMessage({ type: 'logout' });
        channel.close();
      }
    } catch {
      // BroadcastChannel not supported
    }

    // Clear client-side state
    authApiClient.clearToken();
    setUser(null);
  }, []);

  const checkAuth = React.useCallback(async () => {
    try {
      // Check if session exists via server-side API
      // Note: We can't read httpOnly cookies from client-side JS
      const sessionCheck = await fetch('/api/auth/session');
      const sessionData = await sessionCheck.json();

      if (!sessionData.hasSession) {
        // SECURITY: Try E2E mock session only in explicit test mode
        const mockUser = tryLoadMockSession();
        if (mockUser) {
          setUser(mockUser);
        }
        setIsLoading(false);
        return;
      }

      // Attempt to get current user - httpOnly cookie will be sent automatically
      const response = await authApiClient.getCurrentUser();
      if (response.success && response.data) {
        // User type from API matches our User interface
        setUser(sanitizeUser(response.data));
      } else {
        // SECURITY: Try E2E mock session only in explicit test mode
        const mockUser = tryLoadMockSession();
        if (mockUser) {
          setUser(mockUser);
          return;
        }

        setUser(null);
        authApiClient.clearToken();
        // Clear session via API
        try {
          const ctrl = new AbortController();
          const tid = setTimeout(() => ctrl.abort(), 5000);
          try {
            await fetch('/api/auth/session', { method: 'DELETE', signal: ctrl.signal });
          } finally {
            clearTimeout(tid);
          }
        } catch {
          /* best-effort cleanup */
        }
      }
    } catch (error) {
      logger.error('Auth check failed:', error);

      // SECURITY: Try E2E mock session only in explicit test mode
      const mockUser = tryLoadMockSession();
      if (mockUser) {
        setUser(mockUser);
        return;
      }

      setUser(null);
      authApiClient.clearToken();
      // Clear session via API
      try {
        const ctrl = new AbortController();
        const tid = setTimeout(() => ctrl.abort(), 5000);
        try {
          await fetch('/api/auth/session', { method: 'DELETE', signal: ctrl.signal });
        } finally {
          clearTimeout(tid);
        }
      } catch {
        // Ignore cleanup errors
      }
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Auto-check authentication on mount so isLoading transitions to false
  React.useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  // Listen for session-expired events dispatched by the API layer on 401s
  React.useEffect(() => {
    const handleSessionExpired = () => {
      logout();
    };
    window.addEventListener('auth:session-expired', handleSessionExpired);
    return () => {
      window.removeEventListener('auth:session-expired', handleSessionExpired);
    };
  }, [logout]);

  // Broadcast logout across browser tabs via BroadcastChannel
  React.useEffect(() => {
    if (typeof BroadcastChannel === 'undefined') return;

    const channel = new BroadcastChannel('sahool_auth');

    const handleMessage = (event: MessageEvent) => {
      if (event.data?.type === 'logout') {
        authApiClient.clearToken();
        setUser(null);
      }
    };

    channel.addEventListener('message', handleMessage);
    return () => {
      channel.removeEventListener('message', handleMessage);
      channel.close();
    };
  }, []);

  const value = React.useMemo(
    () => ({
      user,
      isAuthenticated: !!user,
      isLoading,
      login,
      logout,
      checkAuth,
    }),
    [user, isLoading, login, logout, checkAuth]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export const useAuth = () => {
  const context = React.useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
};
