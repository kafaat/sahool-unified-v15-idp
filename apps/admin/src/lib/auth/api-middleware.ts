/**
 * API Route Middleware Helpers
 * Utilities for protecting API routes with role-based authorization
 */

import { NextRequest, NextResponse } from 'next/server';
import { cookies } from 'next/headers';
import { verifyToken, getUserFromToken } from './jwt-verify';
import { hasAnyRole } from './jwt-verify';
import type { UserRole } from './route-protection';
import type { User } from '@/lib/auth';

/**
 * Context object passed to API route handlers
 */
export interface AuthenticatedContext {
  user: User;
  token: string;
}

/**
 * API route handler with authentication context
 */
export type AuthenticatedHandler<T = any> = (
  request: NextRequest,
  context: AuthenticatedContext
) => Promise<NextResponse<T>>;

/**
 * Require authentication for an API route
 * Verifies JWT token and extracts user information
 *
 * @param handler - API route handler function
 * @returns Wrapped handler with authentication
 *
 * @example
 * export const GET = withAuth(async (request, { user }) => {
 *   return NextResponse.json({ user });
 * });
 */
export function withAuth<T = any>(
  handler: AuthenticatedHandler<T>
): (request: NextRequest) => Promise<NextResponse<T>> {
  return async (request: NextRequest) => {
    const cookieStore = await cookies();
    const token = cookieStore.get('sahool_admin_token')?.value;

    if (!token) {
      return NextResponse.json(
        { error: 'Unauthorized', message: 'Authentication required' },
        { status: 401 }
      ) as NextResponse<T>;
    }

    try {
      // Verify token and extract user
      const user = await getUserFromToken(token);

      if (!user) {
        return NextResponse.json(
          { error: 'Unauthorized', message: 'Invalid token' },
          { status: 401 }
        ) as NextResponse<T>;
      }

      // Call handler with authenticated context
      return handler(request, { user, token });
    } catch (error) {
      console.error('Authentication error:', error);
      return NextResponse.json(
        { error: 'Unauthorized', message: 'Token verification failed' },
        { status: 401 }
      ) as NextResponse<T>;
    }
  };
}

/**
 * Require specific role(s) for an API route
 * Combines authentication with role-based authorization
 *
 * @param allowedRoles - Array of roles allowed to access this route
 * @param handler - API route handler function
 * @returns Wrapped handler with authentication and authorization
 *
 * @example
 * // Admin only
 * export const POST = withRole(['admin'], async (request, { user }) => {
 *   return NextResponse.json({ message: 'Admin action performed' });
 * });
 *
 * @example
 * // Admin or supervisor
 * export const GET = withRole(['admin', 'supervisor'], async (request, { user }) => {
 *   return NextResponse.json({ data: 'Sensitive data' });
 * });
 */
export function withRole<T = any>(
  allowedRoles: UserRole[],
  handler: AuthenticatedHandler<T>
): (request: NextRequest) => Promise<NextResponse<T>> {
  return withAuth<T>(async (request, context) => {
    const { user } = context;

    // Check if user has one of the allowed roles
    if (!hasAnyRole(user.role, allowedRoles)) {
      return NextResponse.json(
        {
          error: 'Forbidden',
          message: 'You do not have permission to access this resource',
          required_roles: allowedRoles,
          your_role: user.role,
        },
        { status: 403 }
      ) as NextResponse<T>;
    }

    // User has required role - call handler
    return handler(request, context);
  });
}

/**
 * Require admin role for an API route
 * Convenience wrapper for admin-only routes
 *
 * @param handler - API route handler function
 * @returns Wrapped handler with admin authorization
 *
 * @example
 * export const DELETE = withAdmin(async (request, { user }) => {
 *   // Only admins can access this
 *   return NextResponse.json({ message: 'User deleted' });
 * });
 */
export function withAdmin<T = any>(
  handler: AuthenticatedHandler<T>
): (request: NextRequest) => Promise<NextResponse<T>> {
  return withRole<T>(['admin'], handler);
}

/**
 * Require admin or supervisor role for an API route
 * Convenience wrapper for supervisor+ routes
 *
 * @param handler - API route handler function
 * @returns Wrapped handler with supervisor+ authorization
 *
 * @example
 * export const PATCH = withSupervisor(async (request, { user }) => {
 *   // Admins and supervisors can access this
 *   return NextResponse.json({ message: 'Farm updated' });
 * });
 */
export function withSupervisor<T = any>(
  handler: AuthenticatedHandler<T>
): (request: NextRequest) => Promise<NextResponse<T>> {
  return withRole<T>(['admin', 'supervisor'], handler);
}

/**
 * Get authenticated user from request
 * Utility function to extract user from cookies in API routes
 *
 * @param request - Next.js request object (optional, will use cookies() if not provided)
 * @returns User object or null if not authenticated
 *
 * @example
 * export async function GET(request: NextRequest) {
 *   const user = await getAuthenticatedUser();
 *   if (!user) {
 *     return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
 *   }
 *   return NextResponse.json({ user });
 * }
 */
export async function getAuthenticatedUser(
  request?: NextRequest
): Promise<User | null> {
  try {
    const cookieStore = await cookies();
    const token = cookieStore.get('sahool_admin_token')?.value;

    if (!token) {
      return null;
    }

    return await getUserFromToken(token);
  } catch (error) {
    console.error('Failed to get authenticated user:', error);
    return null;
  }
}

/**
 * Check if user has required role
 * Utility function for manual role checks in API routes
 *
 * @param user - User object
 * @param allowedRoles - Array of allowed roles
 * @returns true if user has one of the allowed roles
 *
 * @example
 * const user = await getAuthenticatedUser();
 * if (!user || !checkUserRole(user, ['admin', 'supervisor'])) {
 *   return NextResponse.json({ error: 'Forbidden' }, { status: 403 });
 * }
 */
export function checkUserRole(user: User, allowedRoles: UserRole[]): boolean {
  return hasAnyRole(user.role, allowedRoles);
}

/**
 * Create a standardized error response
 * Utility for consistent error formatting
 */
export function errorResponse(
  message: string,
  status: number = 400,
  additionalData?: Record<string, any>
): NextResponse {
  return NextResponse.json(
    {
      error: getErrorType(status),
      message,
      ...additionalData,
    },
    { status }
  );
}

/**
 * Get error type string from status code
 */
function getErrorType(status: number): string {
  switch (status) {
    case 400:
      return 'Bad Request';
    case 401:
      return 'Unauthorized';
    case 403:
      return 'Forbidden';
    case 404:
      return 'Not Found';
    case 409:
      return 'Conflict';
    case 422:
      return 'Validation Error';
    case 429:
      return 'Too Many Requests';
    case 500:
      return 'Internal Server Error';
    default:
      return 'Error';
  }
}
