/**
 * اختبارات حراس المصادقة NestJS
 * NestJS Auth Guards Tests
 *
 * Tests for JWT, Roles, Permissions, and other auth guards.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { ExecutionContext, UnauthorizedException, ForbiddenException } from '@nestjs/common';
import { Reflector } from '@nestjs/core';
import {
  JwtAuthGuard,
  RolesGuard,
  PermissionsGuard,
  FarmAccessGuard,
  OptionalAuthGuard,
  ActiveAccountGuard,
} from '../guards/jwt.guard';

// ─────────────────────────────────────────────────────────────────────────────
// Mock Setup
// ─────────────────────────────────────────────────────────────────────────────

const createMockExecutionContext = (options: {
  user?: any;
  params?: any;
  url?: string;
  method?: string;
}): ExecutionContext => {
  const request = {
    user: options.user,
    params: options.params || {},
    url: options.url || '/test',
    method: options.method || 'GET',
  };

  return {
    switchToHttp: () => ({
      getRequest: () => request,
    }),
    getHandler: () => ({}),
    getClass: () => ({}),
  } as unknown as ExecutionContext;
};

// ─────────────────────────────────────────────────────────────────────────────
// JwtAuthGuard Tests
// ─────────────────────────────────────────────────────────────────────────────

describe('JwtAuthGuard', () => {
  let guard: JwtAuthGuard;
  let reflector: Reflector;

  beforeEach(() => {
    reflector = new Reflector();
    guard = new JwtAuthGuard(reflector);
  });

  describe('canActivate', () => {
    it('should allow public routes', () => {
      vi.spyOn(reflector, 'getAllAndOverride').mockReturnValue(true);

      const context = createMockExecutionContext({});
      const result = guard.canActivate(context);

      expect(result).toBe(true);
    });
  });

  describe('handleRequest', () => {
    it('should return user when authentication succeeds', () => {
      const context = createMockExecutionContext({ url: '/test', method: 'GET' });
      const user = { id: 'user-123', email: 'test@test.com' };

      const result = guard.handleRequest(null, user, null, context);

      expect(result).toBe(user);
    });

    it('should throw UnauthorizedException for expired token', () => {
      const context = createMockExecutionContext({ url: '/test', method: 'GET' });
      const info = { name: 'TokenExpiredError' };

      expect(() => guard.handleRequest(null, null, info, context)).toThrow(UnauthorizedException);
    });

    it('should throw UnauthorizedException for invalid token', () => {
      const context = createMockExecutionContext({ url: '/test', method: 'GET' });
      const info = { name: 'JsonWebTokenError', message: 'invalid signature' };

      expect(() => guard.handleRequest(null, null, info, context)).toThrow(UnauthorizedException);
    });

    it('should throw UnauthorizedException for missing token', () => {
      const context = createMockExecutionContext({ url: '/test', method: 'GET' });

      expect(() => guard.handleRequest(null, null, null, context)).toThrow(UnauthorizedException);
    });

    it('should rethrow errors', () => {
      const context = createMockExecutionContext({ url: '/test', method: 'GET' });
      const error = new Error('Some error');

      expect(() => guard.handleRequest(error, null, null, context)).toThrow(error);
    });
  });
});

// ─────────────────────────────────────────────────────────────────────────────
// RolesGuard Tests
// ─────────────────────────────────────────────────────────────────────────────

describe('RolesGuard', () => {
  let guard: RolesGuard;
  let reflector: Reflector;

  beforeEach(() => {
    reflector = new Reflector();
    guard = new RolesGuard(reflector);
  });

  it('should allow when no roles required', () => {
    vi.spyOn(reflector, 'getAllAndOverride').mockReturnValue(null);

    const context = createMockExecutionContext({
      user: { id: '1', roles: ['user'] },
    });

    expect(guard.canActivate(context)).toBe(true);
  });

  it('should allow when user has required role', () => {
    vi.spyOn(reflector, 'getAllAndOverride').mockReturnValue(['admin', 'manager']);

    const context = createMockExecutionContext({
      user: { id: '1', roles: ['admin'] },
    });

    expect(guard.canActivate(context)).toBe(true);
  });

  it('should throw ForbiddenException when user lacks required role', () => {
    vi.spyOn(reflector, 'getAllAndOverride').mockReturnValue(['admin']);

    const context = createMockExecutionContext({
      user: { id: '1', roles: ['user'] },
    });

    expect(() => guard.canActivate(context)).toThrow(ForbiddenException);
  });

  it('should throw ForbiddenException when user has no roles', () => {
    vi.spyOn(reflector, 'getAllAndOverride').mockReturnValue(['admin']);

    const context = createMockExecutionContext({
      user: { id: '1' },
    });

    expect(() => guard.canActivate(context)).toThrow(ForbiddenException);
  });

  it('should throw ForbiddenException when no user', () => {
    vi.spyOn(reflector, 'getAllAndOverride').mockReturnValue(['admin']);

    const context = createMockExecutionContext({});

    expect(() => guard.canActivate(context)).toThrow(ForbiddenException);
  });
});

// ─────────────────────────────────────────────────────────────────────────────
// PermissionsGuard Tests
// ─────────────────────────────────────────────────────────────────────────────

describe('PermissionsGuard', () => {
  let guard: PermissionsGuard;
  let reflector: Reflector;

  beforeEach(() => {
    reflector = new Reflector();
    guard = new PermissionsGuard(reflector);
  });

  it('should allow when no permissions required', () => {
    vi.spyOn(reflector, 'getAllAndOverride').mockReturnValue(null);

    const context = createMockExecutionContext({
      user: { id: '1', permissions: [] },
    });

    expect(guard.canActivate(context)).toBe(true);
  });

  it('should allow when user has required permission', () => {
    vi.spyOn(reflector, 'getAllAndOverride').mockReturnValue(['farm:read', 'farm:write']);

    const context = createMockExecutionContext({
      user: { id: '1', permissions: ['farm:read', 'field:read'] },
    });

    expect(guard.canActivate(context)).toBe(true);
  });

  it('should throw ForbiddenException when user lacks permission', () => {
    vi.spyOn(reflector, 'getAllAndOverride').mockReturnValue(['farm:delete']);

    const context = createMockExecutionContext({
      user: { id: '1', permissions: ['farm:read'] },
    });

    expect(() => guard.canActivate(context)).toThrow(ForbiddenException);
  });

  it('should throw ForbiddenException when user has no permissions', () => {
    vi.spyOn(reflector, 'getAllAndOverride').mockReturnValue(['farm:read']);

    const context = createMockExecutionContext({
      user: { id: '1' },
    });

    expect(() => guard.canActivate(context)).toThrow(ForbiddenException);
  });
});

// ─────────────────────────────────────────────────────────────────────────────
// FarmAccessGuard Tests
// ─────────────────────────────────────────────────────────────────────────────

describe('FarmAccessGuard', () => {
  let guard: FarmAccessGuard;
  let reflector: Reflector;

  beforeEach(() => {
    reflector = new Reflector();
    guard = new FarmAccessGuard(reflector);
  });

  it('should throw ForbiddenException when no user', () => {
    const context = createMockExecutionContext({});

    expect(() => guard.canActivate(context)).toThrow(ForbiddenException);
  });

  it('should allow admin users access to any farm', () => {
    const context = createMockExecutionContext({
      user: { id: '1', roles: ['admin'] },
      params: { farmId: 'farm-123' },
    });

    expect(guard.canActivate(context)).toBe(true);
  });

  it('should allow when no farmId in params', () => {
    const context = createMockExecutionContext({
      user: { id: '1', roles: ['farmer'], farmIds: ['farm-456'] },
      params: {},
    });

    expect(guard.canActivate(context)).toBe(true);
  });

  it('should allow user with access to the farm', () => {
    const context = createMockExecutionContext({
      user: { id: '1', roles: ['farmer'], farmIds: ['farm-123', 'farm-456'] },
      params: { farmId: 'farm-123' },
    });

    expect(guard.canActivate(context)).toBe(true);
  });

  it('should throw ForbiddenException when user lacks farm access', () => {
    const context = createMockExecutionContext({
      user: { id: '1', roles: ['farmer'], farmIds: ['farm-456'] },
      params: { farmId: 'farm-123' },
    });

    expect(() => guard.canActivate(context)).toThrow(ForbiddenException);
  });

  it('should handle farm_id param format', () => {
    const context = createMockExecutionContext({
      user: { id: '1', roles: ['farmer'], farmIds: ['farm-123'] },
      params: { farm_id: 'farm-123' },
    });

    expect(guard.canActivate(context)).toBe(true);
  });
});

// ─────────────────────────────────────────────────────────────────────────────
// OptionalAuthGuard Tests
// ─────────────────────────────────────────────────────────────────────────────

describe('OptionalAuthGuard', () => {
  let guard: OptionalAuthGuard;

  beforeEach(() => {
    guard = new OptionalAuthGuard();
  });

  it('should return user when authenticated', () => {
    const user = { id: '1', email: 'test@test.com' };

    const result = guard.handleRequest(null, user);

    expect(result).toBe(user);
  });

  it('should return null when not authenticated', () => {
    const result = guard.handleRequest(null, null);

    expect(result).toBeNull();
  });

  it('should return null on error', () => {
    const result = guard.handleRequest(new Error('test'), null);

    expect(result).toBeNull();
  });
});

// ─────────────────────────────────────────────────────────────────────────────
// ActiveAccountGuard Tests
// ─────────────────────────────────────────────────────────────────────────────

describe('ActiveAccountGuard', () => {
  let guard: ActiveAccountGuard;

  beforeEach(() => {
    guard = new ActiveAccountGuard();
  });

  it('should throw UnauthorizedException when no user', () => {
    const context = createMockExecutionContext({});

    expect(() => guard.canActivate(context)).toThrow(UnauthorizedException);
  });

  it('should throw ForbiddenException when account is disabled', () => {
    const context = createMockExecutionContext({
      user: { id: '1', isActive: false },
    });

    expect(() => guard.canActivate(context)).toThrow(ForbiddenException);
  });

  it('should throw ForbiddenException when account is not verified', () => {
    const context = createMockExecutionContext({
      user: { id: '1', isActive: true, isVerified: false },
    });

    expect(() => guard.canActivate(context)).toThrow(ForbiddenException);
  });

  it('should allow active and verified accounts', () => {
    const context = createMockExecutionContext({
      user: { id: '1', isActive: true, isVerified: true },
    });

    expect(guard.canActivate(context)).toBe(true);
  });

  it('should allow when isActive and isVerified are undefined', () => {
    const context = createMockExecutionContext({
      user: { id: '1' },
    });

    expect(guard.canActivate(context)).toBe(true);
  });
});
