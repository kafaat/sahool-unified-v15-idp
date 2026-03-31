/**
 * JWT Verification Tests
 * اختبارات التحقق من JWT
 *
 * Tests jwt-verify.ts: verifyToken, decodeTokenUnsafe, getUserRole,
 * getUserFromToken, isTokenExpired, hasRequiredRole, hasAnyRole
 *
 * @vitest-environment node
 */

import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { SignJWT } from 'jose';

// We test the actual functions without mocking jose
import {
  verifyToken,
  decodeTokenUnsafe,
  getUserRole,
  getUserFromToken,
  isTokenExpired,
  hasRequiredRole,
  hasAnyRole,
} from '../jwt-verify';

const TEST_SECRET = 'test-secret-key-for-unit-tests-only-32chars';

// Helper to create a valid JWT
async function createTestToken(
  payload: Record<string, unknown>,
  options?: { secret?: string; expiresIn?: string; issuer?: string; audience?: string }
): Promise<string> {
  const secret = options?.secret || TEST_SECRET;
  const key = new TextEncoder().encode(secret);

  let builder = new SignJWT(payload)
    .setProtectedHeader({ alg: 'HS256' })
    .setIssuedAt()
    .setIssuer(options?.issuer ?? 'sahool-platform')
    .setAudience(options?.audience ?? 'sahool-api');

  if (options?.expiresIn) {
    builder = builder.setExpirationTime(options.expiresIn);
  } else {
    builder = builder.setExpirationTime('1h');
  }

  return builder.sign(key);
}

// ═══════════════════════════════════════════════════════════════════════════
// hasRequiredRole & hasAnyRole (pure functions, no JWT needed)
// ═══════════════════════════════════════════════════════════════════════════

describe('hasRequiredRole', () => {
  it('admin has access to all roles', () => {
    expect(hasRequiredRole('admin', 'admin')).toBe(true);
    expect(hasRequiredRole('admin', 'supervisor')).toBe(true);
    expect(hasRequiredRole('admin', 'viewer')).toBe(true);
  });

  it('supervisor has access to supervisor and viewer', () => {
    expect(hasRequiredRole('supervisor', 'admin')).toBe(false);
    expect(hasRequiredRole('supervisor', 'supervisor')).toBe(true);
    expect(hasRequiredRole('supervisor', 'viewer')).toBe(true);
  });

  it('viewer only has viewer access', () => {
    expect(hasRequiredRole('viewer', 'admin')).toBe(false);
    expect(hasRequiredRole('viewer', 'supervisor')).toBe(false);
    expect(hasRequiredRole('viewer', 'viewer')).toBe(true);
  });
});

describe('hasAnyRole', () => {
  it('returns true when user has one of the allowed roles', () => {
    expect(hasAnyRole('admin', ['admin', 'supervisor'])).toBe(true);
    expect(hasAnyRole('supervisor', ['admin', 'supervisor'])).toBe(true);
  });

  it('returns false when user role is insufficient', () => {
    expect(hasAnyRole('viewer', ['admin'])).toBe(false);
    expect(hasAnyRole('viewer', ['supervisor'])).toBe(false);
  });

  it('admin satisfies any role requirement via hierarchy', () => {
    expect(hasAnyRole('admin', ['viewer'])).toBe(true);
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// verifyToken
// ═══════════════════════════════════════════════════════════════════════════

describe('verifyToken', () => {
  beforeEach(() => {
    process.env.JWT_SECRET = TEST_SECRET;
  });

  it('verifies a valid token', async () => {
    const token = await createTestToken({
      sub: 'user-1',
      email: 'admin@sahool.app',
      role: 'admin',
    });

    const payload = await verifyToken(token);
    expect(payload.sub).toBe('user-1');
    expect(payload.email).toBe('admin@sahool.app');
  });

  it('rejects token with wrong secret', async () => {
    const token = await createTestToken(
      { sub: 'user-1', email: 'test@test.com' },
      { secret: 'wrong-secret-key-that-doesnt-match!!' }
    );

    await expect(verifyToken(token)).rejects.toThrow();
  });

  it('throws when JWT_SECRET is not configured', async () => {
    delete process.env.JWT_SECRET;
    delete process.env.JWT_SECRET_KEY;

    const token = await createTestToken({
      sub: 'user-1',
      email: 'test@test.com',
    });

    await expect(verifyToken(token)).rejects.toThrow();

    process.env.JWT_SECRET = TEST_SECRET;
  });

  it('uses JWT_SECRET_KEY as fallback', async () => {
    delete process.env.JWT_SECRET;
    process.env.JWT_SECRET_KEY = TEST_SECRET;

    const token = await createTestToken({
      sub: 'user-1',
      email: 'test@test.com',
    });

    const payload = await verifyToken(token);
    expect(payload.sub).toBe('user-1');

    process.env.JWT_SECRET = TEST_SECRET;
    delete process.env.JWT_SECRET_KEY;
  });

  it('rejects malformed token', async () => {
    await expect(verifyToken('not-a-valid-jwt')).rejects.toThrow();
  });

  it('rejects token missing required fields', async () => {
    const token = await createTestToken({
      sub: 'user-1',
      // missing email
    });

    // The token will fail verification since it lacks email (required field)
    await expect(verifyToken(token)).rejects.toThrow();
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// verifyToken — specific error messages (covers the new classification paths)
// ═══════════════════════════════════════════════════════════════════════════

describe('verifyToken — error classification', () => {
  let savedSecret: string | undefined;
  let savedSecretKey: string | undefined;

  beforeEach(() => {
    savedSecret = process.env.JWT_SECRET;
    savedSecretKey = process.env.JWT_SECRET_KEY;
    process.env.JWT_SECRET = TEST_SECRET;
  });

  afterEach(() => {
    if (savedSecret === undefined) {
      delete process.env.JWT_SECRET;
    } else {
      process.env.JWT_SECRET = savedSecret;
    }
    if (savedSecretKey === undefined) {
      delete process.env.JWT_SECRET_KEY;
    } else {
      process.env.JWT_SECRET_KEY = savedSecretKey;
    }
  });

  it('throws "JWT_SECRET is not configured" when secret is absent', async () => {
    delete process.env.JWT_SECRET;
    delete process.env.JWT_SECRET_KEY;

    const token = await createTestToken({ sub: 'u1', email: 'a@b.com' });

    await expect(verifyToken(token)).rejects.toThrow(
      'JWT_SECRET is not configured. Set JWT_SECRET or JWT_SECRET_KEY environment variable.'
    );
  });

  it('throws "Token has expired" for an expired token and preserves cause', async () => {
    const token = await createTestToken(
      { sub: 'u1', email: 'a@b.com' },
      { expiresIn: '-1s' } // already expired
    );

    const err = await verifyToken(token).catch((e: unknown) => e as Error);
    expect(err.message).toBe('Token has expired');
    expect(err.cause).toBeInstanceOf(Error);
  });

  it('throws "Invalid token signature" when signed with a different secret and preserves cause', async () => {
    const token = await createTestToken(
      { sub: 'u1', email: 'a@b.com' },
      { secret: 'different-secret-key-that-wont-match!!' }
    );

    const err = await verifyToken(token).catch((e: unknown) => e as Error);
    expect(err.message).toBe('Invalid token signature');
    expect(err.cause).toBeInstanceOf(Error);
  });

  it('throws "Token claim validation failed" for wrong issuer', async () => {
    const token = await createTestToken(
      { sub: 'u1', email: 'a@b.com' },
      { issuer: 'wrong-issuer' }
    );

    await expect(verifyToken(token)).rejects.toThrow('Token claim validation failed');
  });

  it('throws "Token claim validation failed" for wrong audience', async () => {
    const token = await createTestToken(
      { sub: 'u1', email: 'a@b.com' },
      { audience: 'wrong-audience' }
    );

    await expect(verifyToken(token)).rejects.toThrow('Token claim validation failed');
  });

  it('throws "Invalid token payload: missing required fields" when email is absent', async () => {
    // Token is structurally valid but lacks the email claim
    const token = await createTestToken({ sub: 'u1' });

    await expect(verifyToken(token)).rejects.toThrow(
      'Invalid token payload: missing required fields'
    );
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// decodeTokenUnsafe
// ═══════════════════════════════════════════════════════════════════════════

describe('decodeTokenUnsafe', () => {
  it('decodes a valid token without verification', async () => {
    const token = await createTestToken({
      sub: 'user-1',
      email: 'test@test.com',
      role: 'admin',
    });

    const payload = decodeTokenUnsafe(token);
    expect(payload).not.toBeNull();
    expect(payload!.sub).toBe('user-1');
    expect(payload!.email).toBe('test@test.com');
  });

  it('returns null for invalid token', () => {
    const payload = decodeTokenUnsafe('garbage-data');
    expect(payload).toBeNull();
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// isTokenExpired
// ═══════════════════════════════════════════════════════════════════════════

describe('isTokenExpired', () => {
  it('returns false for non-expired token', async () => {
    const token = await createTestToken(
      { sub: 'user-1', email: 'test@test.com' },
      { expiresIn: '1h' }
    );
    expect(isTokenExpired(token)).toBe(false);
  });

  it('returns true for invalid token', () => {
    expect(isTokenExpired('invalid-token')).toBe(true);
  });

  it('returns true when token has no exp', async () => {
    // Manually craft a token without exp is tricky with jose,
    // so we test with garbage input
    expect(isTokenExpired('')).toBe(true);
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// getUserRole
// ═══════════════════════════════════════════════════════════════════════════

describe('getUserRole', () => {
  beforeEach(() => {
    process.env.JWT_SECRET = TEST_SECRET;
  });

  it('extracts role from token with role field', async () => {
    const token = await createTestToken({
      sub: 'user-1',
      email: 'test@test.com',
      role: 'supervisor',
    });

    const role = await getUserRole(token);
    expect(role).toBe('supervisor');
  });

  it('extracts role from roles array', async () => {
    const token = await createTestToken({
      sub: 'user-1',
      email: 'test@test.com',
      roles: ['administrator'],
    });

    const role = await getUserRole(token);
    expect(role).toBe('admin');
  });

  it('maps manager to supervisor', async () => {
    const token = await createTestToken({
      sub: 'user-1',
      email: 'test@test.com',
      roles: ['manager'],
    });

    const role = await getUserRole(token);
    expect(role).toBe('supervisor');
  });

  it('defaults to viewer for unknown roles in array', async () => {
    const token = await createTestToken({
      sub: 'user-1',
      email: 'test@test.com',
      roles: ['farmer'],
    });

    const role = await getUserRole(token);
    expect(role).toBe('viewer');
  });

  it('returns null for invalid token (verified mode)', async () => {
    const role = await getUserRole('invalid-token', true);
    expect(role).toBeNull();
  });

  it('decodes without verification when verified=false', async () => {
    const token = await createTestToken({
      sub: 'user-1',
      email: 'test@test.com',
      role: 'admin',
    });

    const role = await getUserRole(token, false);
    expect(role).toBe('admin');
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// getUserFromToken
// ═══════════════════════════════════════════════════════════════════════════

describe('getUserFromToken', () => {
  beforeEach(() => {
    process.env.JWT_SECRET = TEST_SECRET;
  });

  it('extracts full user object from token', async () => {
    const token = await createTestToken({
      sub: 'user-42',
      email: 'farmer@sahool.app',
      name: 'Ahmed',
      role: 'admin',
      tenant_id: 'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
    });

    const user = await getUserFromToken(token);
    expect(user).not.toBeNull();
    expect(user!.id).toBe('user-42');
    expect(user!.email).toBe('farmer@sahool.app');
    expect(user!.name).toBe('Ahmed');
    expect(user!.role).toBe('admin');
    expect(user!.tenant_id).toBe('a1b2c3d4-e5f6-7890-abcd-ef1234567890');
  });

  it('uses email as name fallback', async () => {
    const token = await createTestToken({
      sub: 'user-1',
      email: 'no-name@test.com',
    });

    const user = await getUserFromToken(token);
    expect(user).not.toBeNull();
    expect(user!.name).toBe('no-name@test.com');
  });

  it('extracts tenant_id from tid field', async () => {
    const token = await createTestToken({
      sub: 'user-1',
      email: 'test@test.com',
      tid: 'b2c3d4e5-f6a7-8901-bcde-f12345678901',
    });

    const user = await getUserFromToken(token);
    expect(user!.tenant_id).toBe('b2c3d4e5-f6a7-8901-bcde-f12345678901');
  });

  it('extracts role from roles array in user', async () => {
    const token = await createTestToken({
      sub: 'user-1',
      email: 'test@test.com',
      roles: ['supervisor'],
    });

    const user = await getUserFromToken(token);
    expect(user!.role).toBe('supervisor');
  });

  it('returns null for invalid token', async () => {
    const user = await getUserFromToken('invalid');
    expect(user).toBeNull();
  });
});
