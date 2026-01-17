/**
 * Route Protection Configuration
 * Defines which routes require which roles
 */

export type UserRole = "admin" | "supervisor" | "viewer";

/**
 * Route protection rules
 * Maps route patterns to required roles (any of the listed roles can access)
 */
export const PROTECTED_ROUTES: Record<string, UserRole[]> = {
  // Admin-only routes
  "/settings": ["admin"],
  "/settings/security": ["admin"],
  "/api/settings": ["admin"],
  "/api/users": ["admin"],
  "/api/admin": ["admin"],

  // Admin and Supervisor routes
  "/farms": ["admin", "supervisor"],
  "/diseases": ["admin", "supervisor"],
  "/alerts": ["admin", "supervisor"],
  "/sensors": ["admin", "supervisor"],
  "/irrigation": ["admin", "supervisor"],
  "/yield": ["admin", "supervisor"],
  "/api/farms": ["admin", "supervisor"],
  "/api/diseases": ["admin", "supervisor"],
  "/api/sensors": ["admin", "supervisor"],

  // All authenticated users (admin, supervisor, viewer)
  "/dashboard": ["admin", "supervisor", "viewer"],
  "/analytics": ["admin", "supervisor", "viewer"],
  "/analytics/profitability": ["admin", "supervisor", "viewer"],
  "/analytics/satellite": ["admin", "supervisor", "viewer"],
  "/precision-agriculture": ["admin", "supervisor", "viewer"],
  "/precision-agriculture/gdd": ["admin", "supervisor", "viewer"],
  "/precision-agriculture/spray": ["admin", "supervisor", "viewer"],
  "/precision-agriculture/vra": ["admin", "supervisor", "viewer"],
  "/epidemic": ["admin", "supervisor", "viewer"],
  "/lab": ["admin", "supervisor", "viewer"],
  "/support": ["admin", "supervisor", "viewer"],
};

/**
 * Public routes that don't require authentication
 */
export const PUBLIC_ROUTES = [
  "/login",
  "/register",
  "/forgot-password",
  "/reset-password",
  "/verify-otp",
  "/api/auth/login",
  "/api/auth/register",
  "/api/auth/forgot-password",
  "/api/auth/reset-password",
  "/api/auth/verify-otp",
  "/api/auth/resend-otp",
  "/api/auth/refresh",
  "/api/health",
  "/api/csrf-token",
];

/**
 * Get required roles for a route
 * @param pathname - Route pathname to check
 * @returns Array of allowed roles, or null if route is public
 */
export function getRequiredRoles(pathname: string): UserRole[] | null {
  // Check if route is public
  if (PUBLIC_ROUTES.some((route) => pathname.startsWith(route))) {
    return null;
  }

  // Check for exact match first
  if (PROTECTED_ROUTES[pathname]) {
    return PROTECTED_ROUTES[pathname];
  }

  // Check for prefix match (e.g., /settings/security matches /settings)
  const matchingRoute = Object.keys(PROTECTED_ROUTES).find((route) =>
    pathname.startsWith(route),
  );

  if (matchingRoute && PROTECTED_ROUTES[matchingRoute]) {
    return PROTECTED_ROUTES[matchingRoute];
  }

  // Default: require at least viewer role for any non-public route
  return ["admin", "supervisor", "viewer"];
}

/**
 * Check if a route is public (doesn't require authentication)
 * @param pathname - Route pathname to check
 * @returns true if route is public
 */
export function isPublicRoute(pathname: string): boolean {
  return PUBLIC_ROUTES.some((route) => pathname.startsWith(route));
}

/**
 * Check if a route requires admin role
 * @param pathname - Route pathname to check
 * @returns true if route requires admin role only
 */
export function isAdminOnlyRoute(pathname: string): boolean {
  const requiredRoles = getRequiredRoles(pathname);
  return requiredRoles?.length === 1 && requiredRoles[0] === "admin";
}

/**
 * Check if user has access to a route
 * @param pathname - Route pathname to check
 * @param userRole - User's role
 * @returns true if user has access
 */
export function hasRouteAccess(pathname: string, userRole: UserRole): boolean {
  const requiredRoles = getRequiredRoles(pathname);

  // Public route - everyone has access
  if (requiredRoles === null) {
    return true;
  }

  // Check if user role is in the list of allowed roles
  return requiredRoles.includes(userRole);
}

/**
 * Get unauthorized redirect URL
 * @param userRole - User's role
 * @returns Redirect URL based on user role
 */
export function getUnauthorizedRedirect(userRole: UserRole): string {
  // Redirect based on role
  switch (userRole) {
    case "admin":
      return "/dashboard"; // Admin shouldn't hit this, but redirect to dashboard
    case "supervisor":
      return "/dashboard";
    case "viewer":
      return "/dashboard";
    default:
      return "/dashboard";
  }
}
