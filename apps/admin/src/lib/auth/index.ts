/**
 * Authentication & Authorization Utilities
 * Central export point for all auth-related functions
 */

// JWT Verification
export {
  verifyToken,
  decodeTokenUnsafe,
  getUserRole,
  getUserFromToken,
  isTokenExpired,
  hasRequiredRole,
  hasAnyRole,
  type TokenPayload,
} from "./jwt-verify";

// Route Protection
export {
  getRequiredRoles,
  isPublicRoute,
  isAdminOnlyRoute,
  hasRouteAccess,
  getUnauthorizedRedirect,
  PROTECTED_ROUTES,
  PUBLIC_ROUTES,
  type UserRole,
} from "./route-protection";

// API Middleware
export {
  withAuth,
  withRole,
  withAdmin,
  withSupervisor,
  getAuthenticatedUser,
  checkUserRole,
  errorResponse,
  type AuthenticatedContext,
  type AuthenticatedHandler,
} from "./api-middleware";
