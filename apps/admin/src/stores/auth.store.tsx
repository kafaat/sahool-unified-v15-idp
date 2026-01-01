'use client';
import * as React from 'react';
import Cookies from 'js-cookie';
import { apiClient } from '@/lib/api-client';

interface User {
  id: string;
  email: string;
  name: string;
  name_ar?: string;
  role: 'admin' | 'supervisor' | 'viewer';
  tenant_id?: string;
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  checkAuth: () => Promise<void>;
}

const AuthContext = React.createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = React.useState<User | null>(null);
  const [isLoading, setIsLoading] = React.useState(true);

  const login = React.useCallback(async (email: string, password: string, totp_code?: string) => {
    const response = await apiClient.login(email, password, totp_code);
    if (response.success && response.data) {
      // Check if 2FA is required
      if (response.data.requires_2fa) {
        // Return the response so the component can handle 2FA
        return response.data;
      }

      const { access_token, user } = response.data;
      // Set cookie with security flags
      Cookies.set('sahool_admin_token', access_token, {
        expires: 7, // 7 days
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'strict'
      });
      apiClient.setToken(access_token);
      setUser(user as User);
      return response.data;
    } else {
      throw new Error(response.error || 'Login failed');
    }
  }, []);

  const logout = React.useCallback(() => {
    Cookies.remove('sahool_admin_token');
    apiClient.clearToken();
    setUser(null);
    // Redirect to login
    if (typeof window !== 'undefined') {
      window.location.href = '/login';
    }
  }, []);

  const checkAuth = React.useCallback(async () => {
    try {
      const token = Cookies.get('sahool_admin_token');
      if (!token) {
        setIsLoading(false);
        return;
      }
      apiClient.setToken(token);
      const response = await apiClient.getCurrentUser();
      if (response.success && response.data) {
        setUser(response.data as User);
      } else {
        setUser(null);
        Cookies.remove('sahool_admin_token');
        apiClient.clearToken();
      }
    } catch {
      setUser(null);
      Cookies.remove('sahool_admin_token');
      apiClient.clearToken();
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
