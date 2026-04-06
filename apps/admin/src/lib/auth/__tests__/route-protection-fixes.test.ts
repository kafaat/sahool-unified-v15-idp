/**
 * Tests for developer route protection fixes
 * اختبارات حماية مسارات المطورين
 *
 * Validates:
 * - /audit, /code-review, /code-fix, /copilot are admin-only
 * - API proxy routes are admin-only
 * - Non-admin users cannot access developer routes
 */

import { describe, it, expect } from 'vitest';
import {
  getRequiredRoles,
  hasRouteAccess,
  isAdminOnlyRoute,
  PROTECTED_ROUTES,
} from '../route-protection';

describe('Developer Route Protection', () => {
  const developerRoutes = [
    '/audit',
    '/code-review',
    '/code-fix',
    '/copilot',
  ];

  const developerApiRoutes = [
    '/api/audit',
    '/api/code-review',
    '/api/code-fix',
  ];

  describe('Developer routes registered as admin-only', () => {
    developerRoutes.forEach((route) => {
      it(`${route} should be registered in PROTECTED_ROUTES`, () => {
        expect(PROTECTED_ROUTES[route]).toBeDefined();
      });

      it(`${route} should require only admin role`, () => {
        const roles = getRequiredRoles(route);
        expect(roles).toEqual(['admin']);
      });

      it(`${route} should be flagged as admin-only`, () => {
        expect(isAdminOnlyRoute(route)).toBe(true);
      });
    });
  });

  describe('Developer API routes registered as admin-only', () => {
    developerApiRoutes.forEach((route) => {
      it(`${route} should be registered in PROTECTED_ROUTES`, () => {
        expect(PROTECTED_ROUTES[route]).toBeDefined();
      });

      it(`${route} should require only admin role`, () => {
        const roles = getRequiredRoles(route);
        expect(roles).toEqual(['admin']);
      });
    });
  });

  describe('Role-based access control', () => {
    it('admin can access all developer routes', () => {
      developerRoutes.forEach((route) => {
        expect(hasRouteAccess(route, 'admin')).toBe(true);
      });
    });

    it('supervisor cannot access developer routes', () => {
      developerRoutes.forEach((route) => {
        expect(hasRouteAccess(route, 'supervisor')).toBe(false);
      });
    });

    it('viewer cannot access developer routes', () => {
      developerRoutes.forEach((route) => {
        expect(hasRouteAccess(route, 'viewer')).toBe(false);
      });
    });
  });

  describe('Sub-routes inherit protection', () => {
    it('/audit/export should inherit /audit admin-only protection', () => {
      const roles = getRequiredRoles('/audit/export');
      expect(roles).toEqual(['admin']);
    });

    it('/code-fix/results should inherit /code-fix admin-only protection', () => {
      const roles = getRequiredRoles('/code-fix/results');
      expect(roles).toEqual(['admin']);
    });

    it('/api/audit/logs should inherit /api/audit admin-only protection', () => {
      const roles = getRequiredRoles('/api/audit/logs');
      expect(roles).toEqual(['admin']);
    });
  });

  describe('Non-developer routes are not affected', () => {
    it('/dashboard is accessible to all authenticated users', () => {
      expect(hasRouteAccess('/dashboard', 'admin')).toBe(true);
      expect(hasRouteAccess('/dashboard', 'supervisor')).toBe(true);
      expect(hasRouteAccess('/dashboard', 'viewer')).toBe(true);
    });

    it('/farms requires admin or supervisor', () => {
      expect(hasRouteAccess('/farms', 'admin')).toBe(true);
      expect(hasRouteAccess('/farms', 'supervisor')).toBe(true);
      expect(hasRouteAccess('/farms', 'viewer')).toBe(false);
    });
  });
});
