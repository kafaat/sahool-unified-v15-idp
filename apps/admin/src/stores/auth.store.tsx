"use client";
import * as React from "react";
import { apiClient } from "@/lib/api-client";
import { logger } from "@/lib/logger";

interface User {
  id: string;
  email: string;
  name: string;
  name_ar?: string;
  role: "admin" | "supervisor" | "viewer";
  tenant_id?: string;
}

interface LoginResponse {
  requires_2fa?: boolean;
  temp_token?: string;
  user?: User;
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (
    email: string,
    password: string,
    totp_code?: string,
  ) => Promise<LoginResponse | void>;
  logout: () => void;
  checkAuth: () => Promise<void>;
}

const AuthContext = React.createContext<AuthState | null>(null);

// Idle timeout: 30 minutes in milliseconds
const IDLE_TIMEOUT = 30 * 60 * 1000;
// Token refresh interval: check every 5 minutes
const REFRESH_CHECK_INTERVAL = 5 * 60 * 1000;
// Activity tracking interval: update every 30 seconds when active
const ACTIVITY_UPDATE_INTERVAL = 30 * 1000;

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = React.useState<User | null>(null);
  const [isLoading, setIsLoading] = React.useState(true);
  const lastActivityRef = React.useRef<number>(Date.now());
  const activityTimerRef = React.useRef<NodeJS.Timeout | null>(null);
  const idleCheckTimerRef = React.useRef<NodeJS.Timeout | null>(null);
  const refreshTimerRef = React.useRef<NodeJS.Timeout | null>(null);

  // Logout function - defined first as other callbacks depend on it
  const logout = React.useCallback(async () => {
    try {
      await fetch("/api/auth/logout", {
        method: "POST",
        credentials: "same-origin",
      });
    } catch (error) {
      logger.error("Logout error:", error);
    } finally {
      apiClient.clearToken();
      setUser(null);
      // Redirect to login
      if (typeof window !== "undefined") {
        window.location.href = "/login";
      }
    }
  }, []);

  // Update last activity timestamp
  const updateActivity = React.useCallback(async () => {
    lastActivityRef.current = Date.now();

    // Update server-side activity timestamp
    try {
      await fetch("/api/auth/activity", {
        method: "POST",
        credentials: "same-origin",
      });
    } catch (error) {
      logger.error("Failed to update activity:", error);
    }
  }, []);

  // Check for idle timeout
  const checkIdleTimeout = React.useCallback(() => {
    const now = Date.now();
    const timeSinceLastActivity = now - lastActivityRef.current;

    if (timeSinceLastActivity >= IDLE_TIMEOUT) {
      logger.log("Session expired due to inactivity");
      logout();
    }
  }, [logout]);

  // Attempt to refresh token
  const refreshToken = React.useCallback(async () => {
    try {
      const response = await fetch("/api/auth/refresh", {
        method: "POST",
        credentials: "same-origin",
      });

      if (!response.ok) {
        logger.log("Token refresh failed, logging out");
        logout();
      }
    } catch (error) {
      logger.error("Token refresh error:", error);
    }
  }, [logout]);

  // Setup activity tracking and idle timeout monitoring
  React.useEffect(() => {
    if (!user) {
      // Clear all timers if not authenticated
      if (activityTimerRef.current) clearInterval(activityTimerRef.current);
      if (idleCheckTimerRef.current) clearInterval(idleCheckTimerRef.current);
      if (refreshTimerRef.current) clearInterval(refreshTimerRef.current);
      return;
    }

    // Track user activity
    const events = ["mousedown", "keydown", "scroll", "touchstart", "click"];
    const handleActivity = () => {
      updateActivity();
    };

    events.forEach((event) => {
      window.addEventListener(event, handleActivity, { passive: true });
    });

    // Periodic activity update (every 30 seconds if active)
    activityTimerRef.current = setInterval(() => {
      updateActivity();
    }, ACTIVITY_UPDATE_INTERVAL);

    // Check for idle timeout every minute
    idleCheckTimerRef.current = setInterval(() => {
      checkIdleTimeout();
    }, 60 * 1000);

    // Attempt token refresh every 5 minutes
    refreshTimerRef.current = setInterval(() => {
      refreshToken();
    }, REFRESH_CHECK_INTERVAL);

    return () => {
      events.forEach((event) => {
        window.removeEventListener(event, handleActivity);
      });
      if (activityTimerRef.current) clearInterval(activityTimerRef.current);
      if (idleCheckTimerRef.current) clearInterval(idleCheckTimerRef.current);
      if (refreshTimerRef.current) clearInterval(refreshTimerRef.current);
    };
  }, [user, updateActivity, checkIdleTimeout, refreshToken]);

  const login = React.useCallback(
    async (email: string, password: string, totp_code?: string) => {
      try {
        const response = await fetch("/api/auth/login", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          credentials: "same-origin",
          body: JSON.stringify({ email, password, totp_code }),
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.error || "Login failed");
        }

        // Check if 2FA is required
        if (data.requires_2fa) {
          return { requires_2fa: true, temp_token: data.temp_token };
        }

        // Set user and initialize activity tracking
        setUser(data.user);
        lastActivityRef.current = Date.now();

        return data;
      } catch (error) {
        throw error instanceof Error ? error : new Error("Login failed");
      }
    },
    [],
  );

  const checkAuth = React.useCallback(async () => {
    try {
      // Check auth by fetching current user via proxy route
      // Token is in httpOnly cookie, automatically sent with request
      const response = await fetch("/api/auth/me", {
        method: "GET",
        credentials: "same-origin",
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success && data.data) {
          setUser(data.data as User);
          lastActivityRef.current = Date.now();
        } else {
          setUser(null);
        }
      } else {
        setUser(null);
        if (response.status === 401) {
          // Session expired or invalid token
          await logout();
        }
      }
    } catch (error) {
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, [logout]);

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
