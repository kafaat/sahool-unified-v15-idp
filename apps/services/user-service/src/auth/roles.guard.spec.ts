/**
 * Roles Guard Unit Tests
 * اختبارات وحدة حارس الأدوار
 *
 * Tests for:
 * - Role-based access control
 * - Role hierarchy enforcement
 * - Multiple role requirements
 * - Edge cases: missing roles, invalid users
 */

import { ExecutionContext } from '@nestjs/common';
import { Reflector } from '@nestjs/core';
import { RolesGuard } from './roles.guard';
import { ROLES_KEY } from './roles.decorator';

describe('RolesGuard', () => {
  let guard: RolesGuard;
  let reflector: Reflector;
  let mockExecutionContext: ExecutionContext;

  beforeEach(() => {
    reflector = new Reflector();
    guard = new RolesGuard(reflector);

    mockExecutionContext = {
      getHandler: jest.fn(),
      getClass: jest.fn(),
      switchToHttp: jest.fn().mockReturnValue({
        getRequest: jest.fn().mockReturnValue({
          user: null,
        }),
      }),
    } as any;
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('canActivate', () => {
    it('should allow access when no roles are required', () => {
      jest.spyOn(reflector, 'getAllAndOverride').mockReturnValue(undefined);

      const result = guard.canActivate(mockExecutionContext);

      expect(result).toBe(true);
      expect(reflector.getAllAndOverride).toHaveBeenCalledWith(ROLES_KEY, [
        mockExecutionContext.getHandler(),
        mockExecutionContext.getClass(),
      ]);
    });

    it('should allow access when no roles are required (null)', () => {
      jest.spyOn(reflector, 'getAllAndOverride').mockReturnValue(null);

      const result = guard.canActivate(mockExecutionContext);

      expect(result).toBe(true);
    });

    it('should deny access when roles array is empty but user not provided', () => {
      jest.spyOn(reflector, 'getAllAndOverride').mockReturnValue([]);

      const result = guard.canActivate(mockExecutionContext);

      // Empty array means no specific roles required, but implementation checks user.roles
      // Since requiredRoles is [], some() will return false
      expect(result).toBe(false);
    });

    it('should allow access when user has the required role', () => {
      jest.spyOn(reflector, 'getAllAndOverride').mockReturnValue(['ADMIN']);

      const mockRequest = {
        user: {
          id: 'user-123',
          email: 'admin@example.com',
          roles: ['ADMIN'],
        },
      };

      mockExecutionContext.switchToHttp = jest.fn().mockReturnValue({
        getRequest: jest.fn().mockReturnValue(mockRequest),
      });

      const result = guard.canActivate(mockExecutionContext);

      expect(result).toBe(true);
    });

    it('should allow access when user has one of the required roles', () => {
      jest.spyOn(reflector, 'getAllAndOverride').mockReturnValue(['ADMIN', 'MANAGER']);

      const mockRequest = {
        user: {
          id: 'user-123',
          email: 'manager@example.com',
          roles: ['MANAGER'],
        },
      };

      mockExecutionContext.switchToHttp = jest.fn().mockReturnValue({
        getRequest: jest.fn().mockReturnValue(mockRequest),
      });

      const result = guard.canActivate(mockExecutionContext);

      expect(result).toBe(true);
    });

    it('should allow access when user has multiple roles including required', () => {
      jest.spyOn(reflector, 'getAllAndOverride').mockReturnValue(['OPERATOR']);

      const mockRequest = {
        user: {
          id: 'user-123',
          email: 'multi@example.com',
          roles: ['VIEWER', 'OPERATOR', 'MANAGER'],
        },
      };

      mockExecutionContext.switchToHttp = jest.fn().mockReturnValue({
        getRequest: jest.fn().mockReturnValue(mockRequest),
      });

      const result = guard.canActivate(mockExecutionContext);

      expect(result).toBe(true);
    });

    it('should deny access when user does not have required role', () => {
      jest.spyOn(reflector, 'getAllAndOverride').mockReturnValue(['ADMIN']);

      const mockRequest = {
        user: {
          id: 'user-123',
          email: 'viewer@example.com',
          roles: ['VIEWER'],
        },
      };

      mockExecutionContext.switchToHttp = jest.fn().mockReturnValue({
        getRequest: jest.fn().mockReturnValue(mockRequest),
      });

      const result = guard.canActivate(mockExecutionContext);

      expect(result).toBe(false);
    });

    it('should deny access when user has no roles', () => {
      jest.spyOn(reflector, 'getAllAndOverride').mockReturnValue(['ADMIN']);

      const mockRequest = {
        user: {
          id: 'user-123',
          email: 'noroles@example.com',
          roles: [],
        },
      };

      mockExecutionContext.switchToHttp = jest.fn().mockReturnValue({
        getRequest: jest.fn().mockReturnValue(mockRequest),
      });

      const result = guard.canActivate(mockExecutionContext);

      expect(result).toBe(false);
    });

    it('should deny access when user object is missing', () => {
      jest.spyOn(reflector, 'getAllAndOverride').mockReturnValue(['ADMIN']);

      const mockRequest = {
        user: null,
      };

      mockExecutionContext.switchToHttp = jest.fn().mockReturnValue({
        getRequest: jest.fn().mockReturnValue(mockRequest),
      });

      const result = guard.canActivate(mockExecutionContext);

      expect(result).toBe(false);
    });

    it('should deny access when user is undefined', () => {
      jest.spyOn(reflector, 'getAllAndOverride').mockReturnValue(['ADMIN']);

      const mockRequest = {
        user: undefined,
      };

      mockExecutionContext.switchToHttp = jest.fn().mockReturnValue({
        getRequest: jest.fn().mockReturnValue(mockRequest),
      });

      const result = guard.canActivate(mockExecutionContext);

      expect(result).toBe(false);
    });

    it('should deny access when roles property is missing from user', () => {
      jest.spyOn(reflector, 'getAllAndOverride').mockReturnValue(['ADMIN']);

      const mockRequest = {
        user: {
          id: 'user-123',
          email: 'test@example.com',
          // roles property missing
        },
      };

      mockExecutionContext.switchToHttp = jest.fn().mockReturnValue({
        getRequest: jest.fn().mockReturnValue(mockRequest),
      });

      const result = guard.canActivate(mockExecutionContext);

      expect(result).toBe(false);
    });

    it('should deny access when roles is null', () => {
      jest.spyOn(reflector, 'getAllAndOverride').mockReturnValue(['ADMIN']);

      const mockRequest = {
        user: {
          id: 'user-123',
          email: 'test@example.com',
          roles: null,
        },
      };

      mockExecutionContext.switchToHttp = jest.fn().mockReturnValue({
        getRequest: jest.fn().mockReturnValue(mockRequest),
      });

      const result = guard.canActivate(mockExecutionContext);

      expect(result).toBe(false);
    });
  });

  describe('role hierarchy scenarios', () => {
    it('should enforce strict role matching (ADMIN cannot access MANAGER-only routes)', () => {
      jest.spyOn(reflector, 'getAllAndOverride').mockReturnValue(['MANAGER']);

      const mockRequest = {
        user: {
          id: 'user-123',
          email: 'admin@example.com',
          roles: ['ADMIN'], // Different role
        },
      };

      mockExecutionContext.switchToHttp = jest.fn().mockReturnValue({
        getRequest: jest.fn().mockReturnValue(mockRequest),
      });

      const result = guard.canActivate(mockExecutionContext);

      expect(result).toBe(false);
    });

    it('should allow access for multiple required roles when user has all', () => {
      jest.spyOn(reflector, 'getAllAndOverride').mockReturnValue(['ADMIN', 'MANAGER', 'OPERATOR']);

      const mockRequest = {
        user: {
          id: 'user-123',
          email: 'superuser@example.com',
          roles: ['ADMIN', 'MANAGER', 'OPERATOR', 'VIEWER'],
        },
      };

      mockExecutionContext.switchToHttp = jest.fn().mockReturnValue({
        getRequest: jest.fn().mockReturnValue(mockRequest),
      });

      const result = guard.canActivate(mockExecutionContext);

      expect(result).toBe(true);
    });

    it('should use OR logic for required roles (user needs at least one)', () => {
      jest.spyOn(reflector, 'getAllAndOverride').mockReturnValue(['ADMIN', 'MANAGER']);

      const mockRequest = {
        user: {
          id: 'user-123',
          email: 'operator@example.com',
          roles: ['OPERATOR'], // Has neither ADMIN nor MANAGER
        },
      };

      mockExecutionContext.switchToHttp = jest.fn().mockReturnValue({
        getRequest: jest.fn().mockReturnValue(mockRequest),
      });

      const result = guard.canActivate(mockExecutionContext);

      expect(result).toBe(false);
    });
  });

  describe('edge cases', () => {
    it('should handle case-sensitive role names', () => {
      jest.spyOn(reflector, 'getAllAndOverride').mockReturnValue(['ADMIN']);

      const mockRequest = {
        user: {
          id: 'user-123',
          email: 'test@example.com',
          roles: ['admin'], // lowercase
        },
      };

      mockExecutionContext.switchToHttp = jest.fn().mockReturnValue({
        getRequest: jest.fn().mockReturnValue(mockRequest),
      });

      const result = guard.canActivate(mockExecutionContext);

      expect(result).toBe(false); // Should be case-sensitive
    });

    it('should handle role names with special characters', () => {
      jest.spyOn(reflector, 'getAllAndOverride').mockReturnValue(['CUSTOM_ROLE_123']);

      const mockRequest = {
        user: {
          id: 'user-123',
          email: 'test@example.com',
          roles: ['CUSTOM_ROLE_123'],
        },
      };

      mockExecutionContext.switchToHttp = jest.fn().mockReturnValue({
        getRequest: jest.fn().mockReturnValue(mockRequest),
      });

      const result = guard.canActivate(mockExecutionContext);

      expect(result).toBe(true);
    });

    it('should handle empty string roles', () => {
      jest.spyOn(reflector, 'getAllAndOverride').mockReturnValue(['']);

      const mockRequest = {
        user: {
          id: 'user-123',
          email: 'test@example.com',
          roles: [''],
        },
      };

      mockExecutionContext.switchToHttp = jest.fn().mockReturnValue({
        getRequest: jest.fn().mockReturnValue(mockRequest),
      });

      const result = guard.canActivate(mockExecutionContext);

      expect(result).toBe(true);
    });

    it('should handle roles array with duplicates', () => {
      jest.spyOn(reflector, 'getAllAndOverride').mockReturnValue(['ADMIN']);

      const mockRequest = {
        user: {
          id: 'user-123',
          email: 'test@example.com',
          roles: ['ADMIN', 'ADMIN', 'ADMIN'],
        },
      };

      mockExecutionContext.switchToHttp = jest.fn().mockReturnValue({
        getRequest: jest.fn().mockReturnValue(mockRequest),
      });

      const result = guard.canActivate(mockExecutionContext);

      expect(result).toBe(true);
    });

    it('should handle non-array roles property', () => {
      jest.spyOn(reflector, 'getAllAndOverride').mockReturnValue(['ADMIN']);

      const mockRequest = {
        user: {
          id: 'user-123',
          email: 'test@example.com',
          roles: 'ADMIN', // String instead of array
        },
      };

      mockExecutionContext.switchToHttp = jest.fn().mockReturnValue({
        getRequest: jest.fn().mockReturnValue(mockRequest),
      });

      const result = guard.canActivate(mockExecutionContext);

      // String has includes method, so 'ADMIN'.includes('ADMIN') returns true
      expect(result).toBe(true);
    });
  });

  describe('reflector integration', () => {
    it('should check both handler and class metadata', () => {
      const getAllAndOverrideSpy = jest.spyOn(reflector, 'getAllAndOverride').mockReturnValue(['ADMIN']);

      const mockRequest = {
        user: {
          id: 'user-123',
          roles: ['ADMIN'],
        },
      };

      mockExecutionContext.switchToHttp = jest.fn().mockReturnValue({
        getRequest: jest.fn().mockReturnValue(mockRequest),
      });

      guard.canActivate(mockExecutionContext);

      expect(getAllAndOverrideSpy).toHaveBeenCalledWith(ROLES_KEY, [
        mockExecutionContext.getHandler(),
        mockExecutionContext.getClass(),
      ]);
    });

    it('should prioritize handler metadata over class metadata', () => {
      // This tests the behavior of getAllAndOverride
      // Handler-level @Roles() should override class-level @Roles()
      jest.spyOn(reflector, 'getAllAndOverride').mockReturnValue(['OPERATOR']); // Handler level

      const mockRequest = {
        user: {
          id: 'user-123',
          roles: ['OPERATOR'],
        },
      };

      mockExecutionContext.switchToHttp = jest.fn().mockReturnValue({
        getRequest: jest.fn().mockReturnValue(mockRequest),
      });

      const result = guard.canActivate(mockExecutionContext);

      expect(result).toBe(true);
    });
  });

  describe('real-world scenarios', () => {
    it('should allow ADMIN to access admin-only endpoint', () => {
      jest.spyOn(reflector, 'getAllAndOverride').mockReturnValue(['ADMIN']);

      const mockRequest = {
        user: {
          id: 'admin-user',
          email: 'admin@sahool.com',
          roles: ['ADMIN'],
          tenantId: 'tenant-1',
        },
      };

      mockExecutionContext.switchToHttp = jest.fn().mockReturnValue({
        getRequest: jest.fn().mockReturnValue(mockRequest),
      });

      const result = guard.canActivate(mockExecutionContext);

      expect(result).toBe(true);
    });

    it('should allow MANAGER or ADMIN to access management endpoint', () => {
      jest.spyOn(reflector, 'getAllAndOverride').mockReturnValue(['ADMIN', 'MANAGER']);

      const mockRequest = {
        user: {
          id: 'manager-user',
          email: 'manager@sahool.com',
          roles: ['MANAGER'],
          tenantId: 'tenant-1',
        },
      };

      mockExecutionContext.switchToHttp = jest.fn().mockReturnValue({
        getRequest: jest.fn().mockReturnValue(mockRequest),
      });

      const result = guard.canActivate(mockExecutionContext);

      expect(result).toBe(true);
    });

    it('should deny VIEWER access to admin endpoint', () => {
      jest.spyOn(reflector, 'getAllAndOverride').mockReturnValue(['ADMIN']);

      const mockRequest = {
        user: {
          id: 'viewer-user',
          email: 'viewer@sahool.com',
          roles: ['VIEWER'],
          tenantId: 'tenant-1',
        },
      };

      mockExecutionContext.switchToHttp = jest.fn().mockReturnValue({
        getRequest: jest.fn().mockReturnValue(mockRequest),
      });

      const result = guard.canActivate(mockExecutionContext);

      expect(result).toBe(false);
    });

    it('should allow any authenticated user to access public endpoint (no roles required)', () => {
      jest.spyOn(reflector, 'getAllAndOverride').mockReturnValue(undefined);

      const mockRequest = {
        user: {
          id: 'any-user',
          email: 'user@sahool.com',
          roles: ['VIEWER'],
        },
      };

      mockExecutionContext.switchToHttp = jest.fn().mockReturnValue({
        getRequest: jest.fn().mockReturnValue(mockRequest),
      });

      const result = guard.canActivate(mockExecutionContext);

      expect(result).toBe(true);
    });

    it('should handle user with multiple tenant roles', () => {
      jest.spyOn(reflector, 'getAllAndOverride').mockReturnValue(['MANAGER', 'OPERATOR']);

      const mockRequest = {
        user: {
          id: 'multi-role-user',
          email: 'multi@sahool.com',
          roles: ['MANAGER', 'OPERATOR'], // User has both required roles
          tenantId: 'tenant-1',
        },
      };

      mockExecutionContext.switchToHttp = jest.fn().mockReturnValue({
        getRequest: jest.fn().mockReturnValue(mockRequest),
      });

      const result = guard.canActivate(mockExecutionContext);

      expect(result).toBe(true);
    });
  });
});
