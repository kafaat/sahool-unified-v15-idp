/**
 * SAHOOL Admin Authentication Utilities
 * أدوات التوثيق للوحة الإدارة
 *
 * UPDATED: This file now exports server-side authorization utilities
 * as well as legacy client-side utilities for backward compatibility.
 *
 * SECURITY NOTE: Auth tokens are now stored in httpOnly cookies via server-side
 * API routes (/api/auth/*) for enhanced security. Direct cookie manipulation
 * from client-side code is no longer recommended.
 */

import { logger } from './logger';

// Re-export server-side authorization utilities
export * from './auth/jwt-verify';
export * from './auth/route-protection';
export * from './auth/api-middleware';

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
 * This function now uses server-side API routes for secure httpOnly cookie management
 */
export async function login(credentials: LoginCredentials): Promise<AuthResponse> {
  // Use server-side login endpoint that sets httpOnly cookies
  const response = await fetch('/api/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'same-origin',
    body: JSON.stringify(credentials),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: 'فشل تسجيل الدخول' }));
    throw new Error(error.message || error.error || 'فشل تسجيل الدخول');
  }

  const data = await response.json();

  if (data.user) {
    setUser(data.user);
  }

  // Return mock response for backward compatibility
  return {
    access_token: 'stored_in_httponly_cookie',
    token_type: 'Bearer',
    user: data.user,
  };
}

/**
 * Logout user
 * تسجيل الخروج
 *
 * @deprecated Use the useAuth hook from @/stores/auth.store instead
 * This function now uses server-side API routes to clear httpOnly cookies
 */
export async function logout(): Promise<void> {
  // Use server-side logout endpoint to clear httpOnly cookies
  try {
    await fetch('/api/auth/logout', {
      method: 'POST',
      credentials: 'same-origin',
    });
  } catch (error) {
    logger.error('Logout error:', error);
  }

  if (typeof window !== 'undefined') {
    localStorage.removeItem(AUTH_USER_KEY);
    window.location.href = '/login';
  }
}

/**
 * Get stored token
 * الحصول على التوكن المخزن
 *
 * @deprecated Token is now stored in httpOnly cookie and not accessible from client-side
 * Returns undefined as tokens are now managed server-side
 */
export function getToken(): string | undefined {
  logger.warn('getToken() is deprecated. Tokens are now stored in httpOnly cookies and not accessible from client-side.');
  return undefined;
}

/**
 * Set token in cookies
 * حفظ التوكن في الكوكيز
 *
 * @deprecated Use server-side /api/auth/login endpoint instead
 * Tokens are now set via httpOnly cookies from server-side for security
 */
export function setToken(token: string): void {
  logger.warn('setToken() is deprecated. Use /api/auth/login endpoint to set tokens securely via httpOnly cookies.');
  // No-op - tokens are now managed server-side only
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
