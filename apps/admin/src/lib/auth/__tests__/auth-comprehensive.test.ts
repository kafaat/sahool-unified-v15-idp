/**
 * Auth Comprehensive Tests
 * اختبارات شاملة للمصادقة والتفويض
 *
 * Tests route-protection.ts and auth/index.ts barrel exports
 * using source analysis and runtime behavior
 */

import { describe, it, expect } from 'vitest';
import * as fs from 'fs';
import * as path from 'path';

// ---------------------------------------------------------------------------
// Source analysis
// ---------------------------------------------------------------------------
const ROUTE_PROTECTION_PATH = path.resolve(__dirname, '../route-protection.ts');
const AUTH_INDEX_PATH = path.resolve(__dirname, '../index.ts');

const routeProtectionSource = fs.readFileSync(ROUTE_PROTECTION_PATH, 'utf-8');
const authIndexSource = fs.readFileSync(AUTH_INDEX_PATH, 'utf-8');

// ---------------------------------------------------------------------------
// Runtime imports
// ---------------------------------------------------------------------------
import {
  getRequiredRoles,
  isPublicRoute,
  isAdminOnlyRoute,
  hasRouteAccess,
  getUnauthorizedRedirect,
  PROTECTED_ROUTES,
  PUBLIC_ROUTES,
  type UserRole,
} from '../route-protection';

// ═══════════════════════════════════════════════════════════════════════════
// Route Protection — Source Structure
// ═══════════════════════════════════════════════════════════════════════════

describe('route-protection.ts — source structure', () => {
  it('file exists and is non-empty', () => {
    expect(routeProtectionSource.length).toBeGreaterThan(0);
  });

  it('exports UserRole type', () => {
    expect(routeProtectionSource).toMatch(/export\s+type\s+UserRole/);
  });

  it('defines three roles: admin, supervisor, viewer', () => {
    expect(routeProtectionSource).toContain("'admin'");
    expect(routeProtectionSource).toContain("'supervisor'");
    expect(routeProtectionSource).toContain("'viewer'");
  });

  it('exports PROTECTED_ROUTES constant', () => {
    expect(routeProtectionSource).toMatch(/export\s+const\s+PROTECTED_ROUTES/);
  });

  it('exports PUBLIC_ROUTES constant', () => {
    expect(routeProtectionSource).toMatch(/export\s+const\s+PUBLIC_ROUTES/);
  });

  it('exports getRequiredRoles function', () => {
    expect(routeProtectionSource).toMatch(/export\s+function\s+getRequiredRoles/);
  });

  it('exports isPublicRoute function', () => {
    expect(routeProtectionSource).toMatch(/export\s+function\s+isPublicRoute/);
  });

  it('exports isAdminOnlyRoute function', () => {
    expect(routeProtectionSource).toMatch(/export\s+function\s+isAdminOnlyRoute/);
  });

  it('exports hasRouteAccess function', () => {
    expect(routeProtectionSource).toMatch(/export\s+function\s+hasRouteAccess/);
  });

  it('exports getUnauthorizedRedirect function', () => {
    expect(routeProtectionSource).toMatch(/export\s+function\s+getUnauthorizedRedirect/);
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Route Protection — Public Routes
// ═══════════════════════════════════════════════════════════════════════════

describe('route-protection — PUBLIC_ROUTES', () => {
  it('includes /login', () => {
    expect(PUBLIC_ROUTES).toContain('/login');
  });

  it('includes /register', () => {
    expect(PUBLIC_ROUTES).toContain('/register');
  });

  it('includes /forgot-password', () => {
    expect(PUBLIC_ROUTES).toContain('/forgot-password');
  });

  it('includes /reset-password', () => {
    expect(PUBLIC_ROUTES).toContain('/reset-password');
  });

  it('includes /verify-otp', () => {
    expect(PUBLIC_ROUTES).toContain('/verify-otp');
  });

  it('includes /api/auth/login', () => {
    expect(PUBLIC_ROUTES).toContain('/api/auth/login');
  });

  it('includes /api/auth/register', () => {
    expect(PUBLIC_ROUTES).toContain('/api/auth/register');
  });

  it('includes /api/auth/refresh', () => {
    expect(PUBLIC_ROUTES).toContain('/api/auth/refresh');
  });

  it('includes /api/health', () => {
    expect(PUBLIC_ROUTES).toContain('/api/health');
  });

  it('includes /api/auth/forgot-password', () => {
    expect(PUBLIC_ROUTES).toContain('/api/auth/forgot-password');
  });

  it('includes /api/auth/resend-otp', () => {
    expect(PUBLIC_ROUTES).toContain('/api/auth/resend-otp');
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Route Protection — PROTECTED_ROUTES
// ═══════════════════════════════════════════════════════════════════════════

describe('route-protection — PROTECTED_ROUTES', () => {
  it('has admin-only routes for /settings', () => {
    expect(PROTECTED_ROUTES['/settings']).toEqual(['admin']);
  });

  it('has admin-only routes for /settings/security', () => {
    expect(PROTECTED_ROUTES['/settings/security']).toEqual(['admin']);
  });

  it('has admin-only routes for /api/settings', () => {
    expect(PROTECTED_ROUTES['/api/settings']).toEqual(['admin']);
  });

  it('has admin-only routes for /api/users', () => {
    expect(PROTECTED_ROUTES['/api/users']).toEqual(['admin']);
  });

  it('has admin-only routes for /api/admin', () => {
    expect(PROTECTED_ROUTES['/api/admin']).toEqual(['admin']);
  });

  it('has admin+supervisor for /farms', () => {
    expect(PROTECTED_ROUTES['/farms']).toEqual(['admin', 'supervisor']);
  });

  it('has admin+supervisor for /diseases', () => {
    expect(PROTECTED_ROUTES['/diseases']).toEqual(['admin', 'supervisor']);
  });

  it('has admin+supervisor for /alerts', () => {
    expect(PROTECTED_ROUTES['/alerts']).toEqual(['admin', 'supervisor']);
  });

  it('has admin+supervisor for /sensors', () => {
    expect(PROTECTED_ROUTES['/sensors']).toEqual(['admin', 'supervisor']);
  });

  it('has admin+supervisor for /irrigation', () => {
    expect(PROTECTED_ROUTES['/irrigation']).toEqual(['admin', 'supervisor']);
  });

  it('has all roles for /dashboard', () => {
    expect(PROTECTED_ROUTES['/dashboard']).toEqual(['admin', 'supervisor', 'viewer']);
  });

  it('has all roles for /analytics', () => {
    expect(PROTECTED_ROUTES['/analytics']).toEqual(['admin', 'supervisor', 'viewer']);
  });

  it('has all roles for /precision-agriculture', () => {
    expect(PROTECTED_ROUTES['/precision-agriculture']).toEqual([
      'admin',
      'supervisor',
      'viewer',
    ]);
  });

  it('has all roles for /epidemic', () => {
    expect(PROTECTED_ROUTES['/epidemic']).toEqual(['admin', 'supervisor', 'viewer']);
  });

  it('has all roles for /lab', () => {
    expect(PROTECTED_ROUTES['/lab']).toEqual(['admin', 'supervisor', 'viewer']);
  });

  it('has all roles for /support', () => {
    expect(PROTECTED_ROUTES['/support']).toEqual(['admin', 'supervisor', 'viewer']);
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Route Protection — isPublicRoute
// ═══════════════════════════════════════════════════════════════════════════

describe('route-protection — isPublicRoute()', () => {
  it('returns true for /login', () => {
    expect(isPublicRoute('/login')).toBe(true);
  });

  it('returns true for /register', () => {
    expect(isPublicRoute('/register')).toBe(true);
  });

  it('returns true for /api/auth/login', () => {
    expect(isPublicRoute('/api/auth/login')).toBe(true);
  });

  it('returns true for /api/health', () => {
    expect(isPublicRoute('/api/health')).toBe(true);
  });

  it('returns true for sub-paths of public routes (e.g. /login/callback)', () => {
    expect(isPublicRoute('/login/callback')).toBe(true);
  });

  it('returns false for /dashboard', () => {
    expect(isPublicRoute('/dashboard')).toBe(false);
  });

  it('returns false for /settings', () => {
    expect(isPublicRoute('/settings')).toBe(false);
  });

  it('returns false for /farms', () => {
    expect(isPublicRoute('/farms')).toBe(false);
  });

  it('returns false for /api/farms', () => {
    expect(isPublicRoute('/api/farms')).toBe(false);
  });

  it('returns false for arbitrary unknown paths', () => {
    expect(isPublicRoute('/some-unknown-path')).toBe(false);
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Route Protection — getRequiredRoles
// ═══════════════════════════════════════════════════════════════════════════

describe('route-protection — getRequiredRoles()', () => {
  it('returns null for public routes', () => {
    expect(getRequiredRoles('/login')).toBeNull();
    expect(getRequiredRoles('/api/auth/login')).toBeNull();
    expect(getRequiredRoles('/api/health')).toBeNull();
    expect(getRequiredRoles('/register')).toBeNull();
  });

  it('returns admin-only for /settings', () => {
    expect(getRequiredRoles('/settings')).toEqual(['admin']);
  });

  it('returns admin-only for /api/admin', () => {
    expect(getRequiredRoles('/api/admin')).toEqual(['admin']);
  });

  it('returns admin+supervisor for /farms', () => {
    expect(getRequiredRoles('/farms')).toEqual(['admin', 'supervisor']);
  });

  it('returns all roles for /dashboard', () => {
    expect(getRequiredRoles('/dashboard')).toEqual(['admin', 'supervisor', 'viewer']);
  });

  it('handles prefix matching for sub-routes (/settings/security)', () => {
    expect(getRequiredRoles('/settings/security')).toEqual(['admin']);
  });

  it('returns prefix-matched roles for nested routes (/analytics/profitability)', () => {
    expect(getRequiredRoles('/analytics/profitability')).toEqual([
      'admin',
      'supervisor',
      'viewer',
    ]);
  });

  it('defaults unknown routes to all three roles', () => {
    expect(getRequiredRoles('/brand-new-page')).toEqual(['admin', 'supervisor', 'viewer']);
  });

  it('returns null for sub-paths of public routes', () => {
    expect(getRequiredRoles('/api/auth/login/sso')).toBeNull();
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Route Protection — isAdminOnlyRoute
// ═══════════════════════════════════════════════════════════════════════════

describe('route-protection — isAdminOnlyRoute()', () => {
  it('returns true for /settings', () => {
    expect(isAdminOnlyRoute('/settings')).toBe(true);
  });

  it('returns true for /api/admin', () => {
    expect(isAdminOnlyRoute('/api/admin')).toBe(true);
  });

  it('returns true for /api/users', () => {
    expect(isAdminOnlyRoute('/api/users')).toBe(true);
  });

  it('returns false for /farms (admin+supervisor)', () => {
    expect(isAdminOnlyRoute('/farms')).toBe(false);
  });

  it('returns false for /dashboard (all roles)', () => {
    expect(isAdminOnlyRoute('/dashboard')).toBe(false);
  });

  it('returns false for public routes (returns null required roles)', () => {
    expect(isAdminOnlyRoute('/login')).toBe(false);
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Route Protection — hasRouteAccess
// ═══════════════════════════════════════════════════════════════════════════

describe('route-protection — hasRouteAccess()', () => {
  const roles: UserRole[] = ['admin', 'supervisor', 'viewer'];

  it('everyone has access to public routes', () => {
    for (const role of roles) {
      expect(hasRouteAccess('/login', role)).toBe(true);
      expect(hasRouteAccess('/api/health', role)).toBe(true);
    }
  });

  it('admin has access to all protected routes', () => {
    expect(hasRouteAccess('/settings', 'admin')).toBe(true);
    expect(hasRouteAccess('/farms', 'admin')).toBe(true);
    expect(hasRouteAccess('/dashboard', 'admin')).toBe(true);
    expect(hasRouteAccess('/api/admin', 'admin')).toBe(true);
  });

  it('supervisor can access supervisor+admin routes but not admin-only', () => {
    expect(hasRouteAccess('/farms', 'supervisor')).toBe(true);
    expect(hasRouteAccess('/diseases', 'supervisor')).toBe(true);
    expect(hasRouteAccess('/alerts', 'supervisor')).toBe(true);
    expect(hasRouteAccess('/dashboard', 'supervisor')).toBe(true);
    expect(hasRouteAccess('/settings', 'supervisor')).toBe(false);
    expect(hasRouteAccess('/api/admin', 'supervisor')).toBe(false);
    expect(hasRouteAccess('/api/users', 'supervisor')).toBe(false);
  });

  it('viewer can only access viewer-level routes', () => {
    expect(hasRouteAccess('/dashboard', 'viewer')).toBe(true);
    expect(hasRouteAccess('/analytics', 'viewer')).toBe(true);
    expect(hasRouteAccess('/support', 'viewer')).toBe(true);
    expect(hasRouteAccess('/settings', 'viewer')).toBe(false);
    expect(hasRouteAccess('/farms', 'viewer')).toBe(false);
    expect(hasRouteAccess('/sensors', 'viewer')).toBe(false);
  });

  it('all roles can access unknown routes (default policy)', () => {
    for (const role of roles) {
      expect(hasRouteAccess('/unknown-route', role)).toBe(true);
    }
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Route Protection — getUnauthorizedRedirect
// ═══════════════════════════════════════════════════════════════════════════

describe('route-protection — getUnauthorizedRedirect()', () => {
  it('redirects admin to /dashboard', () => {
    expect(getUnauthorizedRedirect('admin')).toBe('/dashboard');
  });

  it('redirects supervisor to /dashboard', () => {
    expect(getUnauthorizedRedirect('supervisor')).toBe('/dashboard');
  });

  it('redirects viewer to /dashboard', () => {
    expect(getUnauthorizedRedirect('viewer')).toBe('/dashboard');
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Auth Index Barrel — Source Structure
// ═══════════════════════════════════════════════════════════════════════════

describe('auth/index.ts — barrel exports', () => {
  it('file exists and is non-empty', () => {
    expect(authIndexSource.length).toBeGreaterThan(0);
  });

  it('re-exports verifyToken from jwt-verify', () => {
    expect(authIndexSource).toContain('verifyToken');
    expect(authIndexSource).toContain("from './jwt-verify'");
  });

  it('re-exports decodeTokenUnsafe from jwt-verify', () => {
    expect(authIndexSource).toContain('decodeTokenUnsafe');
  });

  it('re-exports getUserRole from jwt-verify', () => {
    expect(authIndexSource).toContain('getUserRole');
  });

  it('re-exports getUserFromToken from jwt-verify', () => {
    expect(authIndexSource).toContain('getUserFromToken');
  });

  it('re-exports isTokenExpired from jwt-verify', () => {
    expect(authIndexSource).toContain('isTokenExpired');
  });

  it('re-exports hasRequiredRole from jwt-verify', () => {
    expect(authIndexSource).toContain('hasRequiredRole');
  });

  it('re-exports hasAnyRole from jwt-verify', () => {
    expect(authIndexSource).toContain('hasAnyRole');
  });

  it('re-exports TokenPayload type from jwt-verify', () => {
    expect(authIndexSource).toContain('TokenPayload');
  });

  it('re-exports User type from jwt-verify', () => {
    expect(authIndexSource).toContain('User');
  });

  it('re-exports route-protection functions', () => {
    expect(authIndexSource).toContain('getRequiredRoles');
    expect(authIndexSource).toContain('isPublicRoute');
    expect(authIndexSource).toContain('isAdminOnlyRoute');
    expect(authIndexSource).toContain('hasRouteAccess');
    expect(authIndexSource).toContain('getUnauthorizedRedirect');
    expect(authIndexSource).toContain("from './route-protection'");
  });

  it('re-exports PROTECTED_ROUTES and PUBLIC_ROUTES', () => {
    expect(authIndexSource).toContain('PROTECTED_ROUTES');
    expect(authIndexSource).toContain('PUBLIC_ROUTES');
  });

  it('re-exports UserRole type from route-protection', () => {
    expect(authIndexSource).toContain('UserRole');
  });

  it('re-exports API middleware functions', () => {
    expect(authIndexSource).toContain('withAuth');
    expect(authIndexSource).toContain('withRole');
    expect(authIndexSource).toContain('withAdmin');
    expect(authIndexSource).toContain('withSupervisor');
    expect(authIndexSource).toContain("from './api-middleware'");
  });

  it('re-exports getAuthenticatedUser from api-middleware', () => {
    expect(authIndexSource).toContain('getAuthenticatedUser');
  });

  it('re-exports checkUserRole from api-middleware', () => {
    expect(authIndexSource).toContain('checkUserRole');
  });

  it('re-exports errorResponse from api-middleware', () => {
    expect(authIndexSource).toContain('errorResponse');
  });

  it('re-exports AuthenticatedContext type from api-middleware', () => {
    expect(authIndexSource).toContain('AuthenticatedContext');
  });

  it('re-exports AuthenticatedHandler type from api-middleware', () => {
    expect(authIndexSource).toContain('AuthenticatedHandler');
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Route Protection — Token Extraction Patterns (source analysis)
// ═══════════════════════════════════════════════════════════════════════════

describe('route-protection — design patterns (source analysis)', () => {
  it('uses exact match before prefix match for route lookup', () => {
    // getRequiredRoles checks exact first, then prefix
    expect(routeProtectionSource).toContain('exactMatch');
    expect(routeProtectionSource).toContain('pathname.startsWith(route)');
  });

  it('returns default all-role access for unmatched routes', () => {
    // Default return at end of getRequiredRoles
    expect(routeProtectionSource).toContain("['admin', 'supervisor', 'viewer']");
  });

  it('uses startsWith for public route matching', () => {
    expect(routeProtectionSource).toContain('pathname.startsWith(route)');
  });

  it('isAdminOnlyRoute checks for single admin role', () => {
    expect(routeProtectionSource).toContain("requiredRoles?.length === 1");
    expect(routeProtectionSource).toContain("requiredRoles[0] === 'admin'");
  });

  it('hasRouteAccess returns true for null required roles (public)', () => {
    expect(routeProtectionSource).toContain('requiredRoles === null');
  });

  it('hasRouteAccess uses includes to check role membership', () => {
    expect(routeProtectionSource).toContain('requiredRoles.includes(userRole)');
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Route Protection — Permission Matrix (comprehensive)
// ═══════════════════════════════════════════════════════════════════════════

describe('route-protection — full permission matrix', () => {
  const adminOnlyRoutes = ['/settings', '/settings/security', '/api/settings', '/api/users', '/api/admin'];
  const supervisorRoutes = ['/farms', '/diseases', '/alerts', '/sensors', '/irrigation', '/yield'];
  const allRoleRoutes = ['/dashboard', '/analytics', '/precision-agriculture', '/epidemic', '/lab', '/support'];

  it.each(adminOnlyRoutes)('admin can access %s', (route) => {
    expect(hasRouteAccess(route, 'admin')).toBe(true);
  });

  it.each(adminOnlyRoutes)('supervisor cannot access %s', (route) => {
    expect(hasRouteAccess(route, 'supervisor')).toBe(false);
  });

  it.each(adminOnlyRoutes)('viewer cannot access %s', (route) => {
    expect(hasRouteAccess(route, 'viewer')).toBe(false);
  });

  it.each(supervisorRoutes)('admin can access %s', (route) => {
    expect(hasRouteAccess(route, 'admin')).toBe(true);
  });

  it.each(supervisorRoutes)('supervisor can access %s', (route) => {
    expect(hasRouteAccess(route, 'supervisor')).toBe(true);
  });

  it.each(supervisorRoutes)('viewer cannot access %s', (route) => {
    expect(hasRouteAccess(route, 'viewer')).toBe(false);
  });

  it.each(allRoleRoutes)('admin can access %s', (route) => {
    expect(hasRouteAccess(route, 'admin')).toBe(true);
  });

  it.each(allRoleRoutes)('supervisor can access %s', (route) => {
    expect(hasRouteAccess(route, 'supervisor')).toBe(true);
  });

  it.each(allRoleRoutes)('viewer can access %s', (route) => {
    expect(hasRouteAccess(route, 'viewer')).toBe(true);
  });
});
