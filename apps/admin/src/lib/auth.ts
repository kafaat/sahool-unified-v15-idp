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
// User type is now defined in ./auth/jwt-verify.ts (canonical location) to
// avoid circular barrel imports that pull @sentry/nextjs into the edge bundle.
// Import it here for local use; it is re-exported via `export *` below.
import type { User } from './auth/jwt-verify';

// Re-export server-side authorization utilities
export * from './auth/jwt-verify';
export * from './auth/route-protection';
export * from './auth/api-middleware';

const AUTH_USER_KEY = 'sahool_admin_user';

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
  logger.warn(
    'getToken() is deprecated. Tokens are now stored in httpOnly cookies and not accessible from client-side.'
  );
  return undefined;
}

/**
 * Set token in cookies
 * حفظ التوكن في الكوكيز
 *
 * @deprecated Use server-side /api/auth/login endpoint instead
 * Tokens are now set via httpOnly cookies from server-side for security
 */
export function setToken(_token: string): void {
  logger.warn(
    'setToken() is deprecated. Use /api/auth/login endpoint to set tokens securely via httpOnly cookies.'
  );
  // No-op - tokens are now managed server-side only
}

/**
 * Get stored user (for UI display only)
 * الحصول على بيانات المستخدم (للعرض فقط)
 *
 * SECURITY NOTE: User data in localStorage is for client-side display only.
 * Do NOT use this for authorization decisions - always verify on server.
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
 * Set user in localStorage (for UI display only)
 * حفظ بيانات المستخدم (للعرض فقط)
 *
 * SECURITY NOTE: This cached user data is for UI convenience.
 * Authorization must always be verified server-side via JWT claims.
 */
export function setUser(user: User): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem(AUTH_USER_KEY, JSON.stringify(user));
  }
}

/**
 * Check if user is authenticated (client-side)
 * التحقق من حالة التوثيق
 *
 * @deprecated Tokens are in httpOnly cookies; use server-side /api/auth/me instead.
 * This now checks for cached user data as an approximation.
 */
export function isAuthenticated(): boolean {
  return !!getUser();
}

/**
 * Check if user has required role (client-side only)
 * التحقق من الصلاحيات (جانب العميل فقط)
 *
 * SECURITY WARNING: This function is for UI display purposes only!
 * The role stored in localStorage can be manipulated by the user.
 *
 * For actual authorization decisions, ALWAYS use server-side role verification:
 * - Use the route-protection.ts middleware for API routes
 * - Use the api-middleware.ts for protected API endpoints
 * - JWT claims should contain the authoritative role from the server
 *
 * @deprecated Use server-side authorization for security-sensitive operations
 */
export function hasRole(requiredRole: User['role']): boolean {
  // SECURITY: This is only for client-side UI purposes
  // Actual authorization MUST be done server-side
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
 *
 * @deprecated Tokens are in httpOnly cookies and sent automatically.
 * Use fetch with `credentials: "same-origin"` instead.
 */
export function getAuthHeaders(): Record<string, string> {
  // Tokens are now in httpOnly cookies - headers are not needed for same-origin requests
  return {};
}
