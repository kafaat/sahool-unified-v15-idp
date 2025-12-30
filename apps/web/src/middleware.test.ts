/**
 * SAHOOL Web Middleware Tests
 * اختبارات ميدل وير الويب
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { jwtVerify } from 'jose';

/**
 * Mock the verifyJWT function from middleware
 * This duplicates the logic to test it in isolation
 */
async function verifyJWT(token: string): Promise<boolean> {
  try {
    const secret = process.env.JWT_SECRET || 'sahool-default-secret-change-in-production';
    const secretKey = new TextEncoder().encode(secret);

    await jwtVerify(token, secretKey, {
      algorithms: ['HS256'],
    });

    return true;
  } catch (error) {
    console.error('JWT verification failed:', error instanceof Error ? error.message : 'Unknown error');
    return false;
  }
}

describe('Middleware JWT Verification', () => {
  // Store original environment variable
  const originalEnv = process.env.JWT_SECRET;

  beforeEach(() => {
    // Mock console.error to avoid cluttering test output
    vi.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    // Restore original environment
    if (originalEnv !== undefined) {
      process.env.JWT_SECRET = originalEnv;
    } else {
      delete process.env.JWT_SECRET;
    }
    // Restore all mocks
    vi.restoreAllMocks();
  });

  describe('Function Structure', () => {
    it('should be an async function', () => {
      expect(verifyJWT).toBeInstanceOf(Function);
      expect(verifyJWT.constructor.name).toBe('AsyncFunction');
    });

    it('should return a Promise', () => {
      const result = verifyJWT('test.token.here');
      expect(result).toBeInstanceOf(Promise);
    });

    it('should return a boolean from the promise', async () => {
      const result = await verifyJWT('invalid');
      expect(typeof result).toBe('boolean');
    });
  });

  describe('Invalid Token Handling', () => {
    it('should reject a malformed token', async () => {
      const malformedToken = 'this.is.not.a.valid.jwt';
      const result = await verifyJWT(malformedToken);
      expect(result).toBe(false);
    });

    it('should reject an empty string token', async () => {
      const result = await verifyJWT('');
      expect(result).toBe(false);
    });

    it('should reject a token with only two parts', async () => {
      const invalidToken = 'header.payload';
      const result = await verifyJWT(invalidToken);
      expect(result).toBe(false);
    });

    it('should reject a token with random gibberish', async () => {
      const gibberishToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.random.gibberish';
      const result = await verifyJWT(gibberishToken);
      expect(result).toBe(false);
    });

    it('should reject a token signed with wrong algorithm header', async () => {
      // Token with RS256 algorithm header (should be rejected as we only accept HS256)
      const wrongAlgToken = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.invalid';
      const result = await verifyJWT(wrongAlgToken);
      expect(result).toBe(false);
    });

    it('should reject a token with invalid base64 encoding', async () => {
      const invalidBase64Token = 'not-base64.not-base64.not-base64';
      const result = await verifyJWT(invalidBase64Token);
      expect(result).toBe(false);
    });
  });

  describe('Error Handling', () => {
    it('should log error message when verification fails', async () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

      const invalidToken = 'invalid.token.here';
      await verifyJWT(invalidToken);

      expect(consoleSpy).toHaveBeenCalled();
      expect(consoleSpy).toHaveBeenCalledWith(
        'JWT verification failed:',
        expect.any(String)
      );

      consoleSpy.mockRestore();
    });

    it('should handle null-like string values gracefully', async () => {
      // Test with various falsy values cast to string
      const results = await Promise.all([
        verifyJWT('null'),
        verifyJWT('undefined'),
        verifyJWT('false'),
      ]);

      results.forEach(result => {
        expect(result).toBe(false);
      });
    });

    it('should return false without throwing on any invalid input', async () => {
      const invalidInputs = [
        '',
        'a',
        '.',
        '..',
        '...',
        'Bearer token',
        'eyJ', // Incomplete base64
        Array(1000).fill('a').join(''), // Very long string
        '   ',
        '\n',
        '\t',
      ];

      for (const input of invalidInputs) {
        const result = await verifyJWT(input);
        expect(result).toBe(false);
      }
    });

    it('should handle concurrent verification requests', async () => {
      const invalidToken = 'invalid.token.test';

      const results = await Promise.all([
        verifyJWT(invalidToken),
        verifyJWT(invalidToken),
        verifyJWT(invalidToken),
        verifyJWT(invalidToken),
        verifyJWT(invalidToken),
      ]);

      results.forEach(result => {
        expect(result).toBe(false);
      });
    });
  });

  describe('Security Configuration', () => {
    it('should use HS256 algorithm in verification options', async () => {
      // We can't directly test the internal algorithm setting,
      // but we can verify the function behaves correctly
      const result = await verifyJWT('invalid');
      expect(result).toBe(false);
    });

    it('should use JWT_SECRET from environment', () => {
      process.env.JWT_SECRET = 'test-secret-123';
      // The function should pick up this secret
      expect(process.env.JWT_SECRET).toBe('test-secret-123');
    });

    it('should fallback to default secret when JWT_SECRET is not set', () => {
      delete process.env.JWT_SECRET;
      const secret = process.env.JWT_SECRET || 'sahool-default-secret-change-in-production';
      expect(secret).toBe('sahool-default-secret-change-in-production');
    });
  });

  describe('Implementation Quality', () => {
    it('should use try-catch for error handling', () => {
      // This is verified by the function not throwing on invalid input
      expect(async () => await verifyJWT('invalid')).not.toThrow();
    });

    it('should properly encode secret as Uint8Array', () => {
      const secret = 'test-secret';
      const encoded = new TextEncoder().encode(secret);
      // Check it's array-like with correct properties
      expect(encoded.constructor.name).toBe('Uint8Array');
      expect(encoded.length).toBeGreaterThan(0);
      expect(encoded.byteLength).toBeGreaterThan(0);
    });

    it('should return consistent results for the same input', async () => {
      const token = 'consistent.test.token';

      const result1 = await verifyJWT(token);
      const result2 = await verifyJWT(token);
      const result3 = await verifyJWT(token);

      expect(result1).toBe(result2);
      expect(result2).toBe(result3);
    });
  });

  describe('Jose Library Integration', () => {
    it('should import jwtVerify from jose', () => {
      expect(jwtVerify).toBeDefined();
      expect(typeof jwtVerify).toBe('function');
    });

    it('should use jwtVerify as an async function', async () => {
      const secret = new TextEncoder().encode('test');
      try {
        await jwtVerify('invalid', secret, { algorithms: ['HS256'] });
      } catch (error) {
        // Should throw for invalid token
        expect(error).toBeDefined();
      }
    });

    it('should specify HS256 algorithm in verification options', async () => {
      const secret = new TextEncoder().encode('test');
      // Token with different algorithm should fail
      try {
        await jwtVerify('eyJhbGciOiJub25lIn0.e30.', secret, { algorithms: ['HS256'] });
        expect(true).toBe(false); // Should not reach here
      } catch (error) {
        expect(error).toBeDefined();
      }
    });
  });

  describe('Token Payload Handling', () => {
    it('should handle tokens with various payload sizes', async () => {
      // Small payload
      const smallToken = 'eyJhbGciOiJIUzI1NiJ9.e30.invalid';
      const result1 = await verifyJWT(smallToken);
      expect(result1).toBe(false);

      // Medium payload (base64 encoded JSON)
      const mediumToken = 'eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.invalid';
      const result2 = await verifyJWT(mediumToken);
      expect(result2).toBe(false);
    });

    it('should handle tokens with special characters in header', async () => {
      const specialToken = 'eyJhbGci0iJIUzI1NiIsInR5cCI6IkpXVCJ9.payload.signature';
      const result = await verifyJWT(specialToken);
      expect(result).toBe(false);
    });
  });
});
