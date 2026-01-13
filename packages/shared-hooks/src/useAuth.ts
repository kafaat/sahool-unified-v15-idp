// ═══════════════════════════════════════════════════════════════════════════════
// useAuth Hook
// خطاف التوثيق الموحد
// ═══════════════════════════════════════════════════════════════════════════════

import { useState, useCallback, useEffect } from "react";
import Cookies from "js-cookie";

// ─────────────────────────────────────────────────────────────────────────────
// Types
// ─────────────────────────────────────────────────────────────────────────────

export type UserRole = "admin" | "supervisor" | "viewer" | "farmer";

export interface User {
  id: string;
  email: string;
  name: string;
  name_ar?: string;
  role: UserRole;
  tenant_id?: string;
  avatar_url?: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token?: string;
  token_type: string;
  expires_in?: number;
  user: User;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface UseAuthOptions {
  apiUrl?: string;
  tokenKey?: string;
  userKey?: string;
  onLogout?: () => void;
  onUnauthorized?: () => void;
}

export interface UseAuthReturn {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (credentials: LoginCredentials) => Promise<AuthResponse>;
  logout: () => void;
  getToken: () => string | undefined;
  setToken: (token: string) => void;
  hasRole: (requiredRole: UserRole) => boolean;
  getAuthHeaders: () => Record<string, string>;
}

// ─────────────────────────────────────────────────────────────────────────────
// Constants
// ─────────────────────────────────────────────────────────────────────────────

const DEFAULT_TOKEN_KEY = "sahool_auth_token";
const DEFAULT_USER_KEY = "sahool_auth_user";

const ROLE_HIERARCHY: Record<UserRole, number> = {
  admin: 4,
  supervisor: 3,
  viewer: 2,
  farmer: 1,
};

// ─────────────────────────────────────────────────────────────────────────────
// Hook Implementation
// ─────────────────────────────────────────────────────────────────────────────

export function useAuth(options: UseAuthOptions = {}): UseAuthReturn {
  const {
    apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001",
    tokenKey = DEFAULT_TOKEN_KEY,
    userKey = DEFAULT_USER_KEY,
    onLogout,
    onUnauthorized,
  } = options;

  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Initialize user from storage
  useEffect(() => {
    if (typeof window === "undefined") {
      setIsLoading(false);
      return;
    }

    const storedUser = localStorage.getItem(userKey);
    const token = Cookies.get(tokenKey);

    if (storedUser && token) {
      try {
        setUser(JSON.parse(storedUser));
      } catch {
        localStorage.removeItem(userKey);
      }
    }
    setIsLoading(false);
  }, [tokenKey, userKey]);

  const getToken = useCallback((): string | undefined => {
    return Cookies.get(tokenKey);
  }, [tokenKey]);

  const setToken = useCallback(
    (token: string): void => {
      Cookies.set(tokenKey, token, {
        expires: 7,
        secure: process.env.NODE_ENV === "production",
        sameSite: "strict",
      });
    },
    [tokenKey],
  );

  const setUserData = useCallback(
    (userData: User): void => {
      if (typeof window !== "undefined") {
        localStorage.setItem(userKey, JSON.stringify(userData));
        setUser(userData);
      }
    },
    [userKey],
  );

  const login = useCallback(
    async (credentials: LoginCredentials): Promise<AuthResponse> => {
      setIsLoading(true);
      setError(null);

      try {
        const response = await fetch(`${apiUrl}/api/v1/auth/login`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(credentials),
        });

        if (!response.ok) {
          const errorData = await response
            .json()
            .catch(() => ({ message: "فشل تسجيل الدخول" }));
          throw new Error(
            errorData.message || errorData.detail || "فشل تسجيل الدخول",
          );
        }

        const data: AuthResponse = await response.json();

        setToken(data.access_token);
        setUserData(data.user);

        return data;
      } catch (err) {
        const message = err instanceof Error ? err.message : "فشل تسجيل الدخول";
        setError(message);
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    [apiUrl, setToken, setUserData],
  );

  const logout = useCallback((): void => {
    Cookies.remove(tokenKey);
    if (typeof window !== "undefined") {
      localStorage.removeItem(userKey);
    }
    setUser(null);
    onLogout?.();
  }, [tokenKey, userKey, onLogout]);

  const hasRole = useCallback(
    (requiredRole: UserRole): boolean => {
      if (!user) return false;
      return ROLE_HIERARCHY[user.role] >= ROLE_HIERARCHY[requiredRole];
    },
    [user],
  );

  const getAuthHeaders = useCallback((): Record<string, string> => {
    const token = getToken();
    if (!token) return {};
    return { Authorization: `Bearer ${token}` };
  }, [getToken]);

  return {
    user,
    isAuthenticated: !!user && !!getToken(),
    isLoading,
    error,
    login,
    logout,
    getToken,
    setToken,
    hasRole,
    getAuthHeaders,
  };
}

export default useAuth;
