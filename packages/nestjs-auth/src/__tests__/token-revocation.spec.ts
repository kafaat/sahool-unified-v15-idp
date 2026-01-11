/**
 * اختبارات نظام إلغاء الرموز
 * Token Revocation Service Tests
 *
 * Tests for Redis-based token revocation with JTI, user, and tenant support.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

// ─────────────────────────────────────────────────────────────────────────────
// Mock Redis (hoisted to avoid initialization issues)
// ─────────────────────────────────────────────────────────────────────────────

const mockRedis = vi.hoisted(() => ({
  connect: vi.fn().mockResolvedValue(undefined),
  quit: vi.fn().mockResolvedValue(undefined),
  ping: vi.fn().mockResolvedValue('PONG'),
  setEx: vi.fn().mockResolvedValue('OK'),
  get: vi.fn(),
  exists: vi.fn(),
  del: vi.fn(),
  keys: vi.fn(),
  on: vi.fn(),
}));

vi.mock('redis', () => ({
  createClient: vi.fn().mockReturnValue(mockRedis),
}));

vi.mock('../config/jwt.config', () => ({
  JWTConfig: {
    REDIS_URL: null,
    REDIS_PASSWORD: 'test-password',
    REDIS_HOST: 'localhost',
    REDIS_PORT: 6379,
    REDIS_DB: 0,
  },
}));

import { RedisTokenRevocationStore } from '../services/token-revocation';

// ─────────────────────────────────────────────────────────────────────────────
// Test Suite
// ─────────────────────────────────────────────────────────────────────────────

describe('RedisTokenRevocationStore', () => {
  let store: RedisTokenRevocationStore;

  beforeEach(async () => {
    vi.clearAllMocks();
    store = new RedisTokenRevocationStore();
  });

  afterEach(async () => {
    await store.close();
  });

  // ─────────────────────────────────────────────────────────────────────────
  // Initialization Tests
  // ─────────────────────────────────────────────────────────────────────────

  describe('Initialization', () => {
    it('should initialize Redis connection', async () => {
      await store.initialize();

      expect(mockRedis.connect).toHaveBeenCalled();
      expect(mockRedis.ping).toHaveBeenCalled();
    });

    it('should not reinitialize if already initialized', async () => {
      await store.initialize();
      await store.initialize();

      expect(mockRedis.connect).toHaveBeenCalledTimes(1);
    });

    it('should throw error on connection failure', async () => {
      mockRedis.connect.mockRejectedValueOnce(new Error('Connection failed'));

      await expect(store.initialize()).rejects.toThrow('Connection failed');
    });
  });

  describe('close', () => {
    it('should close Redis connection', async () => {
      await store.initialize();
      await store.close();

      expect(mockRedis.quit).toHaveBeenCalled();
    });

    it('should handle close when not initialized', async () => {
      await expect(store.close()).resolves.not.toThrow();
    });
  });

  // ─────────────────────────────────────────────────────────────────────────
  // Token (JTI) Revocation Tests
  // ─────────────────────────────────────────────────────────────────────────

  describe('revokeToken', () => {
    it('should revoke token by JTI', async () => {
      await store.initialize();

      const result = await store.revokeToken('jti-123', {
        reason: 'logout',
        userId: 'user-456',
      });

      expect(result).toBe(true);
      expect(mockRedis.setEx).toHaveBeenCalledWith(
        'revoked:token:jti-123',
        expect.any(Number),
        expect.any(String)
      );
    });

    it('should use default TTL of 24 hours', async () => {
      await store.initialize();

      await store.revokeToken('jti-123');

      expect(mockRedis.setEx).toHaveBeenCalledWith(
        expect.any(String),
        86400, // 24 hours
        expect.any(String)
      );
    });

    it('should use custom TTL when provided', async () => {
      await store.initialize();

      await store.revokeToken('jti-123', { expiresIn: 3600 });

      expect(mockRedis.setEx).toHaveBeenCalledWith(
        expect.any(String),
        3600,
        expect.any(String)
      );
    });

    it('should return false for empty JTI', async () => {
      await store.initialize();

      const result = await store.revokeToken('');

      expect(result).toBe(false);
      expect(mockRedis.setEx).not.toHaveBeenCalled();
    });

    it('should return false on Redis error', async () => {
      await store.initialize();
      mockRedis.setEx.mockRejectedValueOnce(new Error('Redis error'));

      const result = await store.revokeToken('jti-123');

      expect(result).toBe(false);
    });
  });

  describe('isTokenRevoked', () => {
    it('should return true when token is revoked', async () => {
      await store.initialize();
      mockRedis.exists.mockResolvedValueOnce(1);

      const result = await store.isTokenRevoked('jti-123');

      expect(result).toBe(true);
    });

    it('should return false when token is not revoked', async () => {
      await store.initialize();
      mockRedis.exists.mockResolvedValueOnce(0);

      const result = await store.isTokenRevoked('jti-123');

      expect(result).toBe(false);
    });

    it('should return false for empty JTI', async () => {
      await store.initialize();

      const result = await store.isTokenRevoked('');

      expect(result).toBe(false);
    });

    it('should return false on Redis error (fail open)', async () => {
      await store.initialize();
      mockRedis.exists.mockRejectedValueOnce(new Error('Redis error'));

      const result = await store.isTokenRevoked('jti-123');

      expect(result).toBe(false);
    });
  });

  describe('getRevocationInfo', () => {
    it('should return revocation info when found', async () => {
      await store.initialize();
      const info = { revokedAt: 1640000000, reason: 'logout', userId: 'user-123' };
      mockRedis.get.mockResolvedValueOnce(JSON.stringify(info));

      const result = await store.getRevocationInfo('jti-123');

      expect(result).toEqual(info);
    });

    it('should return null when not found', async () => {
      await store.initialize();
      mockRedis.get.mockResolvedValueOnce(null);

      const result = await store.getRevocationInfo('jti-123');

      expect(result).toBeNull();
    });

    it('should return null for empty JTI', async () => {
      await store.initialize();

      const result = await store.getRevocationInfo('');

      expect(result).toBeNull();
    });
  });

  // ─────────────────────────────────────────────────────────────────────────
  // User-Level Revocation Tests
  // ─────────────────────────────────────────────────────────────────────────

  describe('revokeAllUserTokens', () => {
    it('should revoke all tokens for a user', async () => {
      await store.initialize();

      const result = await store.revokeAllUserTokens('user-123', 'password_change');

      expect(result).toBe(true);
      expect(mockRedis.setEx).toHaveBeenCalledWith(
        'revoked:user:user-123',
        2592000, // 30 days
        expect.any(String)
      );
    });

    it('should return false for empty userId', async () => {
      await store.initialize();

      const result = await store.revokeAllUserTokens('');

      expect(result).toBe(false);
    });
  });

  describe('isUserTokenRevoked', () => {
    it('should return true when token was issued before revocation', async () => {
      await store.initialize();
      const info = { revokedAt: 1640000000, reason: 'logout' };
      mockRedis.get.mockResolvedValueOnce(JSON.stringify(info));

      const result = await store.isUserTokenRevoked('user-123', 1639999999);

      expect(result).toBe(true);
    });

    it('should return false when token was issued after revocation', async () => {
      await store.initialize();
      const info = { revokedAt: 1640000000, reason: 'logout' };
      mockRedis.get.mockResolvedValueOnce(JSON.stringify(info));

      const result = await store.isUserTokenRevoked('user-123', 1640000001);

      expect(result).toBe(false);
    });

    it('should return false when no revocation exists', async () => {
      await store.initialize();
      mockRedis.get.mockResolvedValueOnce(null);

      const result = await store.isUserTokenRevoked('user-123', 1640000000);

      expect(result).toBe(false);
    });
  });

  describe('clearUserRevocation', () => {
    it('should clear user revocation', async () => {
      await store.initialize();
      mockRedis.del.mockResolvedValueOnce(1);

      const result = await store.clearUserRevocation('user-123');

      expect(result).toBe(true);
      expect(mockRedis.del).toHaveBeenCalledWith('revoked:user:user-123');
    });

    it('should return false when nothing to clear', async () => {
      await store.initialize();
      mockRedis.del.mockResolvedValueOnce(0);

      const result = await store.clearUserRevocation('user-123');

      expect(result).toBe(false);
    });
  });

  // ─────────────────────────────────────────────────────────────────────────
  // Tenant-Level Revocation Tests
  // ─────────────────────────────────────────────────────────────────────────

  describe('revokeAllTenantTokens', () => {
    it('should revoke all tokens for a tenant', async () => {
      await store.initialize();

      const result = await store.revokeAllTenantTokens('tenant-123', 'security');

      expect(result).toBe(true);
      expect(mockRedis.setEx).toHaveBeenCalledWith(
        'revoked:tenant:tenant-123',
        2592000,
        expect.any(String)
      );
    });

    it('should return false for empty tenantId', async () => {
      await store.initialize();

      const result = await store.revokeAllTenantTokens('');

      expect(result).toBe(false);
    });
  });

  describe('isTenantTokenRevoked', () => {
    it('should return true when token was issued before tenant revocation', async () => {
      await store.initialize();
      const info = { revokedAt: 1640000000, reason: 'security' };
      mockRedis.get.mockResolvedValueOnce(JSON.stringify(info));

      const result = await store.isTenantTokenRevoked('tenant-123', 1639999999);

      expect(result).toBe(true);
    });

    it('should return false when token was issued after tenant revocation', async () => {
      await store.initialize();
      const info = { revokedAt: 1640000000, reason: 'security' };
      mockRedis.get.mockResolvedValueOnce(JSON.stringify(info));

      const result = await store.isTenantTokenRevoked('tenant-123', 1640000001);

      expect(result).toBe(false);
    });
  });

  // ─────────────────────────────────────────────────────────────────────────
  // Combined Check Tests
  // ─────────────────────────────────────────────────────────────────────────

  describe('isRevoked', () => {
    it('should check JTI revocation', async () => {
      await store.initialize();
      mockRedis.exists.mockResolvedValueOnce(1);

      const result = await store.isRevoked({ jti: 'jti-123' });

      expect(result.isRevoked).toBe(true);
      expect(result.reason).toBe('token_revoked');
    });

    it('should check user revocation', async () => {
      await store.initialize();
      mockRedis.exists.mockResolvedValueOnce(0);
      const info = { revokedAt: 1640000000, reason: 'logout' };
      mockRedis.get.mockResolvedValueOnce(JSON.stringify(info));

      const result = await store.isRevoked({
        jti: 'jti-123',
        userId: 'user-123',
        issuedAt: 1639999999,
      });

      expect(result.isRevoked).toBe(true);
      expect(result.reason).toBe('user_tokens_revoked');
    });

    it('should check tenant revocation', async () => {
      await store.initialize();
      mockRedis.exists.mockResolvedValueOnce(0);
      mockRedis.get
        .mockResolvedValueOnce(null) // user check
        .mockResolvedValueOnce(JSON.stringify({ revokedAt: 1640000000 })); // tenant check

      const result = await store.isRevoked({
        jti: 'jti-123',
        userId: 'user-123',
        tenantId: 'tenant-123',
        issuedAt: 1639999999,
      });

      expect(result.isRevoked).toBe(true);
      expect(result.reason).toBe('tenant_tokens_revoked');
    });

    it('should return not revoked when all checks pass', async () => {
      await store.initialize();
      mockRedis.exists.mockResolvedValueOnce(0);
      mockRedis.get
        .mockResolvedValueOnce(null)
        .mockResolvedValueOnce(null);

      const result = await store.isRevoked({
        jti: 'jti-123',
        userId: 'user-123',
        tenantId: 'tenant-123',
        issuedAt: 1640000000,
      });

      expect(result.isRevoked).toBe(false);
    });
  });

  // ─────────────────────────────────────────────────────────────────────────
  // Statistics and Health Tests
  // ─────────────────────────────────────────────────────────────────────────

  describe('getStats', () => {
    it('should return revocation statistics', async () => {
      await store.initialize();
      mockRedis.keys
        .mockResolvedValueOnce(['revoked:token:1', 'revoked:token:2'])
        .mockResolvedValueOnce(['revoked:user:1'])
        .mockResolvedValueOnce([]);

      const stats = await store.getStats();

      expect(stats.initialized).toBe(true);
      expect(stats.revokedTokens).toBe(2);
      expect(stats.revokedUsers).toBe(1);
      expect(stats.revokedTenants).toBe(0);
    });
  });

  describe('healthCheck', () => {
    it('should return true when healthy', async () => {
      await store.initialize();
      mockRedis.ping.mockResolvedValueOnce('PONG');

      const result = await store.healthCheck();

      expect(result).toBe(true);
    });

    it('should return false when unhealthy', async () => {
      await store.initialize();
      mockRedis.ping.mockRejectedValueOnce(new Error('Connection lost'));

      const result = await store.healthCheck();

      expect(result).toBe(false);
    });
  });
});
