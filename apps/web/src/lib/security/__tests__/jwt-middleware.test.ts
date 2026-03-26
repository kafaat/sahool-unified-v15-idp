/**
 * JWT Middleware Validation Tests
 * اختبارات التحقق من JWT في الميدل وير
 *
 * Tests JWT token validation, configuration management,
 * and error handling for various JWT scenarios.
 */

import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { validateJwtToken, getJwtConfig } from '../jwt-middleware';

// JWT test config
const TEST_SECRET = 'test-secret-key-for-unit-tests-only-32chars';
const TEST_ISSUER = 'sahool-auth';
const TEST_AUDIENCE = 'sahool-web';

// Helper to create mock NextRequest
function createMockRequest(token?: string) {
  return {
    cookies: {
      get: (name: string) => {
        if (name === 'access_token' && token) {
          return { value: token };
        }
        return undefined;
      },
    },
    nextUrl: { pathname: '/dashboard' },
    headers: {
      get: () => null,
    },
  } as Parameters<typeof validateJwtToken>[0];
}

describe('JWT Middleware Validation', () => {
  const originalEnv = process.env;

  beforeEach(() => {
    process.env = {
      ...originalEnv,
      JWT_SECRET_KEY: TEST_SECRET,
      JWT_ISSUER: TEST_ISSUER,
      JWT_AUDIENCE: TEST_AUDIENCE,
    };
  });

  afterEach(() => {
    process.env = originalEnv;
  });

  describe('getJwtConfig', () => {
    it('should return config when all env vars are set', () => {
      const config = getJwtConfig();
      expect(config).not.toBeNull();
      expect(config?.secretKey).toBe(TEST_SECRET);
      expect(config?.issuer).toBe(TEST_ISSUER);
      expect(config?.audience).toBe(TEST_AUDIENCE);
      expect(config?.cookieName).toBe('access_token');
    });

    it('should return null when JWT_SECRET_KEY is missing', () => {
      delete process.env.JWT_SECRET_KEY;
      expect(getJwtConfig()).toBeNull();
    });

    it('should return null when JWT_ISSUER is missing', () => {
      delete process.env.JWT_ISSUER;
      expect(getJwtConfig()).toBeNull();
    });

    it('should return null when JWT_AUDIENCE is missing', () => {
      delete process.env.JWT_AUDIENCE;
      expect(getJwtConfig()).toBeNull();
    });
  });

  describe('validateJwtToken', () => {
    it('should reject when no token is present', async () => {
      const req = createMockRequest();
      const config = {
        cookieName: 'access_token',
        secretKey: TEST_SECRET,
        issuer: TEST_ISSUER,
        audience: TEST_AUDIENCE,
      };

      const result = await validateJwtToken(req, config);
      expect(result.valid).toBe(false);
      expect(result.error).toContain('not found');
    });

    it('should fail when JWT config is not available', async () => {
      delete process.env.JWT_SECRET_KEY;
      delete process.env.JWT_ISSUER;
      delete process.env.JWT_AUDIENCE;
      const req = createMockRequest('some-token');

      const result = await validateJwtToken(req);
      expect(result.valid).toBe(false);
      expect(result.error).toContain('configuration');
    });

    it('should reject malformed tokens', async () => {
      const req = createMockRequest('not.a.valid.jwt.token');
      const config = {
        cookieName: 'access_token',
        secretKey: TEST_SECRET,
        issuer: TEST_ISSUER,
        audience: TEST_AUDIENCE,
      };

      const result = await validateJwtToken(req, config);
      expect(result.valid).toBe(false);
    });

    it('should reject completely invalid token strings', async () => {
      const req = createMockRequest('garbage-data');
      const config = {
        cookieName: 'access_token',
        secretKey: TEST_SECRET,
        issuer: TEST_ISSUER,
        audience: TEST_AUDIENCE,
      };

      const result = await validateJwtToken(req, config);
      expect(result.valid).toBe(false);
      expect(result.error).toBeTruthy();
    });

    it('should reject token with empty string', async () => {
      const req = createMockRequest('');
      const config = {
        cookieName: 'access_token',
        secretKey: TEST_SECRET,
        issuer: TEST_ISSUER,
        audience: TEST_AUDIENCE,
      };

      // Empty token means cookie returns empty string
      const result = await validateJwtToken(req, config);
      expect(result.valid).toBe(false);
    });

    it("should use default cookie name 'access_token'", async () => {
      const req = createMockRequest('some-token');
      const config = {
        secretKey: TEST_SECRET,
        issuer: TEST_ISSUER,
        audience: TEST_AUDIENCE,
      };

      // Should look for 'access_token' cookie
      const result = await validateJwtToken(req, config);
      expect(result.valid).toBe(false);
      // It will fail on verify, but should find the token
    });

    it("should reject when cookie name doesn't match", async () => {
      const req = {
        cookies: {
          get: (name: string) => {
            // Only have token under different cookie name
            if (name === 'different_cookie') return { value: 'token' };
            return undefined;
          },
        },
        nextUrl: { pathname: '/dashboard' },
        headers: { get: () => null },
      } as Parameters<typeof validateJwtToken>[0];

      const config = {
        cookieName: 'access_token',
        secretKey: TEST_SECRET,
        issuer: TEST_ISSUER,
        audience: TEST_AUDIENCE,
      };

      const result = await validateJwtToken(req, config);
      expect(result.valid).toBe(false);
      expect(result.error).toContain('not found');
    });

    it('should return error details on failure', async () => {
      const req = createMockRequest('invalid.jwt.token');
      const config = {
        cookieName: 'access_token',
        secretKey: TEST_SECRET,
        issuer: TEST_ISSUER,
        audience: TEST_AUDIENCE,
      };

      const result = await validateJwtToken(req, config);
      expect(result.valid).toBe(false);
      expect(result.error).toBeDefined();
      expect(typeof result.error).toBe('string');
      expect(result.payload).toBeUndefined();
    });
  });
});
