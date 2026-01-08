/**
 * JWT Auth Guard Unit Tests
 * اختبارات وحدة حارس المصادقة JWT
 *
 * Tests for:
 * - Token validation
 * - Error handling (expired, invalid, malformed tokens)
 * - Optional authentication
 * - Algorithm security
 */

import { ExecutionContext, UnauthorizedException } from '@nestjs/common';
import { JwtAuthGuard, OptionalJwtAuthGuard } from './jwt-auth.guard';
import * as jwt from 'jsonwebtoken';

describe('JwtAuthGuard', () => {
  let guard: JwtAuthGuard;
  let mockExecutionContext: ExecutionContext;

  beforeEach(() => {
    guard = new JwtAuthGuard();
    mockExecutionContext = {
      switchToHttp: jest.fn().mockReturnValue({
        getRequest: jest.fn().mockReturnValue({
          headers: {},
        }),
      }),
      getClass: jest.fn(),
      getHandler: jest.fn(),
    } as any;
  });

  describe('canActivate', () => {
    it('should call parent canActivate method', async () => {
      const superCanActivateSpy = jest.spyOn(Object.getPrototypeOf(JwtAuthGuard.prototype), 'canActivate');
      superCanActivateSpy.mockReturnValue(true);

      const result = guard.canActivate(mockExecutionContext);

      expect(superCanActivateSpy).toHaveBeenCalledWith(mockExecutionContext);
      expect(result).toBe(true);

      superCanActivateSpy.mockRestore();
    });
  });

  describe('handleRequest', () => {
    it('should return user when authentication is successful', () => {
      const mockUser = {
        id: 'user-123',
        email: 'test@example.com',
        roles: ['VIEWER'],
      };

      const result = guard.handleRequest(null, mockUser, null);

      expect(result).toEqual(mockUser);
    });

    it('should throw UnauthorizedException for expired token', () => {
      const tokenExpiredError = {
        name: 'TokenExpiredError',
        message: 'jwt expired',
      };

      expect(() => guard.handleRequest(null, null, tokenExpiredError)).toThrow(UnauthorizedException);
      expect(() => guard.handleRequest(null, null, tokenExpiredError)).toThrow('Token has expired');
    });

    it('should throw UnauthorizedException for invalid token', () => {
      const jsonWebTokenError = {
        name: 'JsonWebTokenError',
        message: 'invalid token',
      };

      expect(() => guard.handleRequest(null, null, jsonWebTokenError)).toThrow(UnauthorizedException);
      expect(() => guard.handleRequest(null, null, jsonWebTokenError)).toThrow('Invalid token');
    });

    it('should throw UnauthorizedException when user is null', () => {
      expect(() => guard.handleRequest(null, null, null)).toThrow(UnauthorizedException);
      expect(() => guard.handleRequest(null, null, null)).toThrow('Authentication failed');
    });

    it('should throw UnauthorizedException when user is undefined', () => {
      expect(() => guard.handleRequest(null, undefined, null)).toThrow(UnauthorizedException);
      expect(() => guard.handleRequest(null, undefined, null)).toThrow('Authentication failed');
    });

    it('should throw the original error when error is provided', () => {
      const customError = new Error('Custom authentication error');

      expect(() => guard.handleRequest(customError, null, null)).toThrow(customError);
    });

    it('should handle other JWT errors', () => {
      const otherError = {
        name: 'NotBeforeError',
        message: 'jwt not active',
      };

      expect(() => guard.handleRequest(null, null, otherError)).toThrow(UnauthorizedException);
      expect(() => guard.handleRequest(null, null, otherError)).toThrow('Authentication failed');
    });
  });
});

describe('OptionalJwtAuthGuard', () => {
  let guard: OptionalJwtAuthGuard;
  let mockExecutionContext: ExecutionContext;
  let mockRequest: any;

  const validSecret = 'test-secret-key-for-jwt-validation-must-be-long-enough';
  const originalEnv = process.env;

  beforeEach(() => {
    guard = new OptionalJwtAuthGuard();
    mockRequest = {
      headers: {},
      user: undefined,
    };
    mockExecutionContext = {
      switchToHttp: jest.fn().mockReturnValue({
        getRequest: jest.fn().mockReturnValue(mockRequest),
      }),
      getClass: jest.fn(),
      getHandler: jest.fn(),
    } as any;

    // Set up environment
    process.env = { ...originalEnv };
    process.env.JWT_SECRET_KEY = validSecret;
  });

  afterEach(() => {
    process.env = originalEnv;
    jest.clearAllMocks();
  });

  describe('canActivate', () => {
    it('should return true when no authorization header is present', () => {
      const result = guard.canActivate(mockExecutionContext);

      expect(result).toBe(true);
      expect(mockRequest.user).toBeUndefined();
    });

    it('should return true when authorization header is empty', () => {
      mockRequest.headers.authorization = '';

      const result = guard.canActivate(mockExecutionContext);

      expect(result).toBe(true);
      expect(mockRequest.user).toBeUndefined();
    });

    it('should return true when token type is not Bearer', () => {
      mockRequest.headers.authorization = 'Basic dGVzdDp0ZXN0';

      const result = guard.canActivate(mockExecutionContext);

      expect(result).toBe(true);
      expect(mockRequest.user).toBeUndefined();
    });

    it('should return true when token is missing after Bearer', () => {
      mockRequest.headers.authorization = 'Bearer ';

      const result = guard.canActivate(mockExecutionContext);

      expect(result).toBe(true);
      expect(mockRequest.user).toBeUndefined();
    });

    it('should attach user to request when valid token is provided', () => {
      const payload = {
        sub: 'user-123',
        email: 'test@example.com',
        roles: ['VIEWER'],
        tenant_id: 'tenant-123',
      };

      const token = jwt.sign(payload, validSecret, { algorithm: 'HS256' });
      mockRequest.headers.authorization = `Bearer ${token}`;

      const result = guard.canActivate(mockExecutionContext);

      expect(result).toBe(true);
      expect(mockRequest.user).toEqual({
        id: 'user-123',
        email: 'test@example.com',
        roles: ['VIEWER'],
        tenantId: 'tenant-123',
      });
    });

    it('should use user_id from payload if sub is not present', () => {
      const payload = {
        user_id: 'user-456',
        email: 'test2@example.com',
        roles: ['ADMIN'],
        tenant_id: 'tenant-456',
      };

      const token = jwt.sign(payload, validSecret, { algorithm: 'HS256' });
      mockRequest.headers.authorization = `Bearer ${token}`;

      const result = guard.canActivate(mockExecutionContext);

      expect(result).toBe(true);
      expect(mockRequest.user.id).toBe('user-456');
    });

    it('should return true but not attach user when token is invalid', () => {
      mockRequest.headers.authorization = 'Bearer invalid.token.here';

      const result = guard.canActivate(mockExecutionContext);

      expect(result).toBe(true);
      expect(mockRequest.user).toBeUndefined();
    });

    it('should return true but not attach user when token is expired', () => {
      const payload = {
        sub: 'user-123',
        email: 'test@example.com',
        exp: Math.floor(Date.now() / 1000) - 3600, // Expired 1 hour ago
      };

      const token = jwt.sign(payload, validSecret, { algorithm: 'HS256', noTimestamp: true });
      mockRequest.headers.authorization = `Bearer ${token}`;

      const result = guard.canActivate(mockExecutionContext);

      expect(result).toBe(true);
      expect(mockRequest.user).toBeUndefined();
    });

    it('should return true when JWT_SECRET is not configured', () => {
      delete process.env.JWT_SECRET_KEY;
      delete process.env.JWT_SECRET;

      const token = jwt.sign({ sub: 'user-123' }, 'any-secret', { algorithm: 'HS256' });
      mockRequest.headers.authorization = `Bearer ${token}`;

      const result = guard.canActivate(mockExecutionContext);

      expect(result).toBe(true);
      expect(mockRequest.user).toBeUndefined();
    });

    it('should set empty roles array when roles are not in token', () => {
      const payload = {
        sub: 'user-123',
        email: 'test@example.com',
      };

      const token = jwt.sign(payload, validSecret, { algorithm: 'HS256' });
      mockRequest.headers.authorization = `Bearer ${token}`;

      const result = guard.canActivate(mockExecutionContext);

      expect(result).toBe(true);
      expect(mockRequest.user.roles).toEqual([]);
    });
  });

  describe('algorithm security', () => {
    it('should reject "none" algorithm tokens', () => {
      // Create a token with 'none' algorithm (security vulnerability test)
      const header = Buffer.from(JSON.stringify({ alg: 'none', typ: 'JWT' })).toString('base64');
      const payload = Buffer.from(JSON.stringify({ sub: 'user-123', email: 'test@example.com' })).toString('base64');
      const noneToken = `${header}.${payload}.`;

      mockRequest.headers.authorization = `Bearer ${noneToken}`;

      const result = guard.canActivate(mockExecutionContext);

      expect(result).toBe(true);
      expect(mockRequest.user).toBeUndefined(); // Should not authenticate
    });

    it('should accept tokens with allowed algorithms (HS256)', () => {
      const payload = { sub: 'user-123', email: 'test@example.com' };
      const token = jwt.sign(payload, validSecret, { algorithm: 'HS256' });

      mockRequest.headers.authorization = `Bearer ${token}`;

      const result = guard.canActivate(mockExecutionContext);

      expect(result).toBe(true);
      expect(mockRequest.user).toBeDefined();
    });

    it('should accept tokens with allowed algorithms (HS384)', () => {
      const payload = { sub: 'user-123', email: 'test@example.com' };
      const token = jwt.sign(payload, validSecret, { algorithm: 'HS384' });

      mockRequest.headers.authorization = `Bearer ${token}`;

      const result = guard.canActivate(mockExecutionContext);

      expect(result).toBe(true);
      expect(mockRequest.user).toBeDefined();
    });

    it('should accept tokens with allowed algorithms (HS512)', () => {
      const payload = { sub: 'user-123', email: 'test@example.com' };
      const token = jwt.sign(payload, validSecret, { algorithm: 'HS512' });

      mockRequest.headers.authorization = `Bearer ${token}`;

      const result = guard.canActivate(mockExecutionContext);

      expect(result).toBe(true);
      expect(mockRequest.user).toBeDefined();
    });

    it('should reject tokens with unsupported algorithms', () => {
      // Create a malformed token with unsupported algorithm
      const header = Buffer.from(JSON.stringify({ alg: 'XXX', typ: 'JWT' })).toString('base64');
      const payload = Buffer.from(JSON.stringify({ sub: 'user-123' })).toString('base64');
      const signature = Buffer.from('fake-signature').toString('base64');
      const unsupportedToken = `${header}.${payload}.${signature}`;

      mockRequest.headers.authorization = `Bearer ${unsupportedToken}`;

      const result = guard.canActivate(mockExecutionContext);

      expect(result).toBe(true);
      expect(mockRequest.user).toBeUndefined(); // Should not authenticate
    });

    it('should handle tokens without algorithm in header', () => {
      const header = Buffer.from(JSON.stringify({ typ: 'JWT' })).toString('base64');
      const payload = Buffer.from(JSON.stringify({ sub: 'user-123' })).toString('base64');
      const signature = Buffer.from('fake-signature').toString('base64');
      const noAlgToken = `${header}.${payload}.${signature}`;

      mockRequest.headers.authorization = `Bearer ${noAlgToken}`;

      const result = guard.canActivate(mockExecutionContext);

      expect(result).toBe(true);
      expect(mockRequest.user).toBeUndefined();
    });

    it('should handle malformed tokens gracefully', () => {
      mockRequest.headers.authorization = 'Bearer not.a.valid.jwt.token';

      const result = guard.canActivate(mockExecutionContext);

      expect(result).toBe(true);
      expect(mockRequest.user).toBeUndefined();
    });
  });

  describe('edge cases', () => {
    it('should handle tokens with extra whitespace', () => {
      const payload = { sub: 'user-123', email: 'test@example.com' };
      const token = jwt.sign(payload, validSecret, { algorithm: 'HS256' });

      mockRequest.headers.authorization = `  Bearer   ${token}  `;

      const result = guard.canActivate(mockExecutionContext);

      // The current implementation uses split(' '), so extra spaces would cause issues
      // This documents the current behavior
      expect(result).toBe(true);
    });

    it('should handle case-sensitive Bearer keyword', () => {
      const payload = { sub: 'user-123', email: 'test@example.com' };
      const token = jwt.sign(payload, validSecret, { algorithm: 'HS256' });

      mockRequest.headers.authorization = `bearer ${token}`; // lowercase

      const result = guard.canActivate(mockExecutionContext);

      expect(result).toBe(true);
      expect(mockRequest.user).toBeUndefined(); // Should not match 'Bearer'
    });

    it('should handle tokens with special characters in payload', () => {
      const payload = {
        sub: 'user-123',
        email: 'test+special@example.com',
        roles: ['ADMIN', 'VIEWER'],
        tenant_id: 'tenant-<script>alert("xss")</script>',
      };

      const token = jwt.sign(payload, validSecret, { algorithm: 'HS256' });
      mockRequest.headers.authorization = `Bearer ${token}`;

      const result = guard.canActivate(mockExecutionContext);

      expect(result).toBe(true);
      expect(mockRequest.user).toBeDefined();
      expect(mockRequest.user.email).toBe('test+special@example.com');
    });

    it('should use JWT_SECRET as fallback when JWT_SECRET_KEY is not set', () => {
      delete process.env.JWT_SECRET_KEY;
      process.env.JWT_SECRET = validSecret;

      const payload = { sub: 'user-123', email: 'test@example.com' };
      const token = jwt.sign(payload, validSecret, { algorithm: 'HS256' });

      mockRequest.headers.authorization = `Bearer ${token}`;

      const result = guard.canActivate(mockExecutionContext);

      expect(result).toBe(true);
      expect(mockRequest.user).toBeDefined();
    });
  });
});
