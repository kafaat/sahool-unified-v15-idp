/**
 * SAHOOL Admin Authentication Utilities
 * أدوات التوثيق للوحة الإدارة
 *
 * NOTE: This file is kept for backward compatibility.
 * New code should use the AuthProvider context from @/stores/auth.store
 */

import Cookies from 'js-cookie';
import { logger } from './logger';

const AUTH_TOKEN_KEY = 'sahool_admin_token';
const AUTH_USER_KEY = 'sahool_admin_user';

// API URL - configurable via environment
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3000';

// Enforce HTTPS in production
if (typeof window !== 'undefined' && process.env.NODE_ENV === 'production' && !API_URL.startsWith('https://')) {
  logger.warn('Warning: API_URL should use HTTPS in production environment');
}

export interface User {
  id: string;
  email: string;
  name: string;
  name_ar?: string;
  role: 'admin' | 'supervisor' | 'viewer';
  tenant_id?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

/**
 * Login with email and password
 * تسجيل الدخول بالبريد وكلمة المرور
 *
 * @deprecated Use the useAuth hook from @/stores/auth.store instead
 */
export async function login(credentials: LoginCredentials): Promise<AuthResponse> {
  const response = await fetch(`${API_URL}/api/v1/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(credentials),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: 'فشل تسجيل الدخول' }));
    throw new Error(error.message || error.detail || 'فشل تسجيل الدخول');
  }

  const data: AuthResponse = await response.json();

  // Store token and user
  setToken(data.access_token);
  setUser(data.user);

  return data;
}

/**
 * Logout user
 * تسجيل الخروج
 *
 * @deprecated Use the useAuth hook from @/stores/auth.store instead
 */
export function logout(): void {
  Cookies.remove(AUTH_TOKEN_KEY);
  if (typeof window !== 'undefined') {
    localStorage.removeItem(AUTH_USER_KEY);
  }
  // Redirect to login
  if (typeof window !== 'undefined') {
    window.location.href = '/login';
  }
}

/**
 * Get stored token
 * الحصول على التوكن المخزن
 */
export function getToken(): string | undefined {
  return Cookies.get(AUTH_TOKEN_KEY);
}

/**
 * Set token in cookies
 * حفظ التوكن في الكوكيز
 */
export function setToken(token: string): void {
  // Set cookie with secure options
  Cookies.set(AUTH_TOKEN_KEY, token, {
    expires: 7, // 7 days
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'strict',
  });
}

/**
 * Get stored user
 * الحصول على بيانات المستخدم
 */
export function getUser(): User | null {
  if (typeof window === 'undefined') return null;

  const userStr = localStorage.getItem(AUTH_USER_KEY);
  if (!userStr) return null;

  try {
    return JSON.parse(userStr);
  } catch {
    return null;
  }
}

/**
 * Set user in localStorage
 * حفظ بيانات المستخدم
 */
export function setUser(user: User): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem(AUTH_USER_KEY, JSON.stringify(user));
  }
}

/**
 * Check if user is authenticated
 * التحقق من حالة التوثيق
 */
export function isAuthenticated(): boolean {
  return !!getToken();
}

/**
 * Check if user has required role
 * التحقق من الصلاحيات
 */
export function hasRole(requiredRole: User['role']): boolean {
  const user = getUser();
  if (!user) return false;

  const roleHierarchy: Record<User['role'], number> = {
    admin: 3,
    supervisor: 2,
    viewer: 1,
  };

  return roleHierarchy[user.role] >= roleHierarchy[requiredRole];
}

/**
 * Get authorization headers
 * الحصول على رؤوس التوثيق
 */
export function getAuthHeaders(): Record<string, string> {
  const token = getToken();
  if (!token) return {};

  return {
    Authorization: `Bearer ${token}`,
  };
}
