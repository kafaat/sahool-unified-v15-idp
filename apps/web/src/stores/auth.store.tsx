'use client';
import { createContext, useContext, useState, useCallback, useMemo, ReactNode } from 'react';
import Cookies from 'js-cookie';
import { apiClient } from '@/lib/api/client';

interface User {
  id: string;
  email: string;
  name: string;
  name_ar: string;
  role: string;
  tenant_id: string;
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  checkAuth: () => Promise<void>;
}

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const login = useCallback(async (email: string, password: string) => {
    const response = await apiClient.login(email, password);
    if (response.success && response.data) {
      const { access_token, user } = response.data;
      // Set cookie with security flags
      // Note: httpOnly cannot be set from client-side JS - server should set this
      Cookies.set('access_token', access_token, {
        expires: 7,
        secure: true, // Only send over HTTPS
        sameSite: 'strict' // CSRF protection
      });
      apiClient.setToken(access_token);
      setUser(user as any);
    } else {
      throw new Error(response.error || 'Login failed');
    }
  }, []);

  const logout = useCallback(() => {
    Cookies.remove('access_token');
    apiClient.clearToken();
    setUser(null);
  }, []);

  const checkAuth = useCallback(async () => {
    try {
      const token = Cookies.get('access_token');
      if (!token) {
        setIsLoading(false);
        return;
      }
      apiClient.setToken(token);
      const response = await apiClient.getCurrentUser();
      if (response.success && response.data) {
        setUser(response.data);
      } else {
        setUser(null);
        Cookies.remove('access_token');
        apiClient.clearToken();
      }
    } catch {
      setUser(null);
      Cookies.remove('access_token');
      apiClient.clearToken();
    } finally {
      setIsLoading(false);
    }
  }, []);

  const value = useMemo(
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
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
};
