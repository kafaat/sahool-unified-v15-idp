'use client';
import * as React from 'react';
import Cookies from 'js-cookie';
import { apiClient } from '@/lib/api/client';

/**
 * Fetch CSRF token from the server
 * جلب رمز CSRF من الخادم
 */
async function fetchCsrfToken(): Promise<void> {
  try {
    const response = await fetch('/api/csrf-token');
    if (response.ok) {
      // Token is automatically set in cookie by the API route
      // No need to manually set it here
    }
  } catch (error) {
    console.warn('Failed to fetch CSRF token:', error);
    // Non-fatal error - continue without CSRF token
    // The middleware will generate one on next authenticated request
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
    const response = await apiClient.login(email, password);
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
          refresh_token
        }),
      });

      if (!sessionResponse.ok) {
        throw new Error('Failed to create secure session');
      }

      // Set token in API client for immediate use
      // Note: Subsequent requests will use the httpOnly cookie automatically
      apiClient.setToken(access_token);

      // User type from API matches our User interface
      setUser(user);

      // Fetch CSRF token for subsequent requests
      await fetchCsrfToken();
    } else {
      throw new Error(response.error || 'Login failed');
    }
  }, []);

  const logout = React.useCallback(async () => {
    // Remove cookies via secure server-side API route
    try {
      await fetch('/api/auth/session', {
        method: 'DELETE',
      });
    } catch (error) {
      // Continue with logout even if API call fails
      console.error('Failed to clear session cookies:', error);
    }

    // Clear CSRF token
    Cookies.remove('csrf_token');

    // Clear client-side state
    apiClient.clearToken();
    setUser(null);
  }, []);

  const checkAuth = React.useCallback(async () => {
    try {
      // Check if session exists via server-side API
      // Note: We can't read httpOnly cookies from client-side JS
      const sessionCheck = await fetch('/api/auth/session');
      const sessionData = await sessionCheck.json();

      if (!sessionData.hasSession) {
        setIsLoading(false);
        return;
      }

      // Attempt to get current user - httpOnly cookie will be sent automatically
      const response = await apiClient.getCurrentUser();
      if (response.success && response.data) {
        // User type from API matches our User interface
        setUser(response.data);
      } else {
        // SECURITY: Mock authentication bypass for E2E tests
        // This MUST only be enabled in development environments
        // WARNING: Allowing mock sessions in production is a critical security vulnerability
        // that would allow anyone to bypass authentication by setting a cookie
        if (process.env.NODE_ENV === 'development') {
          const mockSession = Cookies.get('user_session');
          if (mockSession) {
            try {
              const mockUser = JSON.parse(mockSession);
              setUser({
                id: mockUser.id || 'test-user',
                email: mockUser.email || 'test@sahool.com',
                name: mockUser.name || 'Test User',
                name_ar: mockUser.nameAr || 'مستخدم اختباري',
                role: mockUser.role || 'user',
              });
              return;
            } catch {
              // Invalid mock session
            }
          }
        }
        setUser(null);
        apiClient.clearToken();
        // Clear session via API
        await fetch('/api/auth/session', { method: 'DELETE' });
      }
    } catch {
      // SECURITY: Mock authentication bypass for E2E tests
      // This MUST only be enabled in development environments
      // WARNING: Allowing mock sessions in production is a critical security vulnerability
      // that would allow anyone to bypass authentication by setting a cookie
      if (process.env.NODE_ENV === 'development') {
        const mockSession = Cookies.get('user_session');
        if (mockSession) {
          try {
            const mockUser = JSON.parse(mockSession);
            setUser({
              id: mockUser.id || 'test-user',
              email: mockUser.email || 'test@sahool.com',
              name: mockUser.name || 'Test User',
              name_ar: mockUser.nameAr || 'مستخدم اختباري',
              role: mockUser.role || 'user',
            });
            return;
          } catch {
            // Invalid mock session
          }
        }
      }
      setUser(null);
      apiClient.clearToken();
      // Clear session via API
      try {
        await fetch('/api/auth/session', { method: 'DELETE' });
      } catch {
        // Ignore cleanup errors
      }
    } finally {
      setIsLoading(false);
    }
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

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = React.useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
};
