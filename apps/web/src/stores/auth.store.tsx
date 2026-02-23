"use client";
import * as React from "react";
import Cookies from "js-cookie";
import { authApiClient } from "@/lib/api/auth-client";
import { logger } from "@/lib/logger";

/**
 * Fetch CSRF token from the server
 * جلب رمز CSRF من الخادم
 *
 * SECURITY: CSRF tokens are required for all state-changing requests.
 * If token fetch fails, subsequent requests may fail with 403.
 */
async function fetchCsrfToken(): Promise<boolean> {
  try {
    const response = await fetch("/api/csrf-token");
    if (response.ok) {
      // Token is automatically set in cookie by the API route
      return true;
    }
    logger.error("CSRF token fetch failed with status:", response.status);
    return false;
  } catch (error) {
    logger.error("Failed to fetch CSRF token:", error);
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
function isE2ETestModeEnabled(): boolean {
  // CRITICAL: Production builds MUST have NODE_ENV=production
  if (process.env.NODE_ENV !== "development") {
    return false;
  }

  // SECURITY: Require explicit E2E flag - no implicit localhost detection
  return process.env.NEXT_PUBLIC_E2E_TEST === "true";
}

/**
 * Attempt to load mock user session for E2E testing
 * محاولة تحميل جلسة مستخدم وهمية لاختبار E2E
 *
 * SECURITY: This function should ONLY be called after isE2ETestModeEnabled() returns true
 */
function tryLoadMockSession(): User | null {
  if (!isE2ETestModeEnabled()) {
    return null;
  }

  const mockSession = Cookies.get("user_session");
  if (!mockSession) {
    return null;
  }

  try {
    const mockUser = JSON.parse(mockSession);
    logger.warn(
      "[SECURITY WARNING] Using mock authentication - E2E test mode only. " +
        "This should NEVER appear in production logs."
    );
    return {
      id: mockUser.id || "test-user",
      email: mockUser.email || "test@sahool.com",
      name: mockUser.name || "Test User",
      name_ar: mockUser.nameAr || "مستخدم اختباري",
      role: mockUser.role || "user",
    };
  } catch {
    logger.warn("Invalid mock session format");
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
      const sessionResponse = await fetch("/api/auth/session", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          access_token,
          refresh_token,
        }),
      });

      if (!sessionResponse.ok) {
        throw new Error("Failed to create secure session");
      }

      // Set token in API client for immediate use
      // Note: Subsequent requests will use the httpOnly cookie automatically
      authApiClient.setToken(access_token);

      // User type from API matches our User interface
      setUser(user);

      // Fetch CSRF token for subsequent requests
      await fetchCsrfToken();
    } else {
      throw new Error(response.error || "Login failed");
    }
  }, []);

  const logout = React.useCallback(async () => {
    // Remove cookies via secure server-side API route
    try {
      await fetch("/api/auth/session", {
        method: "DELETE",
      });
    } catch (error) {
      // Continue with logout even if API call fails
      logger.error("Failed to clear session cookies:", error);
    }

    // Clear CSRF token
    Cookies.remove("csrf_token");

    // Clear client-side state
    authApiClient.clearToken();
    setUser(null);
  }, []);

  const checkAuth = React.useCallback(async () => {
    try {
      // Check if session exists via server-side API
      // Note: We can't read httpOnly cookies from client-side JS
      const sessionCheck = await fetch("/api/auth/session");
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
        setUser(response.data);
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
        await fetch("/api/auth/session", { method: "DELETE" });
      }
    } catch (error) {
      logger.error("Auth check failed:", error);

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
        await fetch("/api/auth/session", { method: "DELETE" });
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
    [user, isLoading, login, logout, checkAuth],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export const useAuth = () => {
  const context = React.useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within AuthProvider");
  return context;
};
