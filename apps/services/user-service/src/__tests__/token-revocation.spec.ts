/**
 * RedisTokenRevocationStore Unit Tests
 * اختبارات وحدة مخزن إلغاء الرموز
 *
 * Covers:
 * - Redis unavailable: initialize() must NOT crash the process
 * - Fail-closed behaviour: isTokenRevoked/isRevoked return true when Redis is down
 * - Write operations (revokeToken, revokeAllUserTokens) return false when Redis is down
 * - healthCheck() returns false when Redis is down
 * - 'end' event does NOT reset this.initializing (prevents concurrent-initialize race)
 * - Successful happy-path revocation and lookup
 */

import { Test, TestingModule } from '@nestjs/testing';
import { Logger } from '@nestjs/common';
import { createClient } from 'redis';
import { RedisTokenRevocationStore } from '../utils/token-revocation';

// ─── Mock redis module ────────────────────────────────────────────────────────
jest.mock('redis', () => ({
  createClient: jest.fn(),
}));

const mockCreateClient = createClient as jest.MockedFunction<typeof createClient>;

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function makeMockRedis(overrides: Record<string, jest.Mock> = {}): any {
  const handlers: Record<string, Array<(...args: unknown[]) => void>> = {};
  // Declare type explicitly to avoid circular reference inference error
  const client: Record<string, unknown> = {
    on: jest.fn((event: string, handler: (...args: unknown[]) => void) => {
      handlers[event] = handlers[event] ?? [];
      handlers[event].push(handler);
      return client;
    }),
    connect: jest.fn().mockResolvedValue(undefined),
    ping: jest.fn().mockResolvedValue('PONG'),
    quit: jest.fn().mockResolvedValue(undefined),
    disconnect: jest.fn(),
    get: jest.fn().mockResolvedValue(null),
    setEx: jest.fn().mockResolvedValue('OK'),
    exists: jest.fn().mockResolvedValue(0),
    del: jest.fn().mockResolvedValue(1),
    incr: jest.fn().mockResolvedValue(1),
    expire: jest.fn().mockResolvedValue(1),
    // Helper to emit events in tests
    _emit: (event: string, ...args: any[]) => {
      (handlers[event] ?? []).forEach(h => h(...args));
    },
    ...overrides,
  };
  return client;
}

// ─── Tests ────────────────────────────────────────────────────────────────────

describe('RedisTokenRevocationStore', () => {
  let store: RedisTokenRevocationStore;

  beforeEach(() => {
    jest.clearAllMocks();
    // Silence logger output in tests
    jest.spyOn(Logger.prototype, 'log').mockImplementation(() => {});
    jest.spyOn(Logger.prototype, 'warn').mockImplementation(() => {});
    jest.spyOn(Logger.prototype, 'error').mockImplementation(() => {});
  });

  afterEach(async () => {
    // Attempt graceful close; ignore if already closed
    try { await store?.close(); } catch { /* ignore */ }
    jest.restoreAllMocks();
  });

  // ── 1. Redis unavailable: no crash ──────────────────────────────────────────

  describe('when Redis is unavailable (ECONNREFUSED)', () => {
    beforeEach(() => {
      const mockRedis = makeMockRedis({
        // Always reject so every initialize() attempt fails fast
        connect: jest.fn().mockRejectedValue(new Error('Max reconnection attempts exceeded')),
        disconnect: jest.fn(() => { throw new Error('ClientClosedError: The client is closed'); }),
      });
      mockCreateClient.mockReturnValue(mockRedis);
      store = new RedisTokenRevocationStore('redis://localhost:6379');
    });

    it('initialize() must NOT throw or crash the process when connect rejects', async () => {
      await expect(store.initialize()).resolves.toBeUndefined();
    });

    it('onModuleInit() must NOT produce an unhandled promise rejection when Redis is down', async () => {
      const unhandledHandler = jest.fn();
      process.on('unhandledRejection', unhandledHandler);

      store.onModuleInit();

      // Flush microtasks / macrotasks to let the fire-and-forget complete
      await new Promise(resolve => setImmediate(resolve));
      await new Promise(resolve => setImmediate(resolve));

      process.off('unhandledRejection', unhandledHandler);
      expect(unhandledHandler).not.toHaveBeenCalled();
    });

    it('isTokenRevoked() returns true (fail-closed) when Redis is unavailable', async () => {
      const result = await store.isTokenRevoked('some-jti');
      expect(result).toBe(true);
    });

    it('isUserTokenRevoked() returns true (fail-closed) when Redis is unavailable', async () => {
      const result = await store.isUserTokenRevoked('user-id', Date.now() / 1000 - 60);
      expect(result).toBe(true);
    });

    it('isTenantTokenRevoked() returns true (fail-closed) when Redis is unavailable', async () => {
      const result = await store.isTenantTokenRevoked('tenant-id', Date.now() / 1000 - 60);
      expect(result).toBe(true);
    });

    it('isRevoked() returns isRevoked:true (fail-closed) when Redis is unavailable', async () => {
      const result = await store.isRevoked({ jti: 'some-jti', userId: 'u1', issuedAt: 0 });
      expect(result.isRevoked).toBe(true);
    });

    it('revokeToken() returns false (graceful degradation) when Redis is unavailable', async () => {
      const result = await store.revokeToken('jti-123', { reason: 'logout' });
      expect(result).toBe(false);
    });

    it('revokeAllUserTokens() returns false when Redis is unavailable', async () => {
      const result = await store.revokeAllUserTokens('user-id');
      expect(result).toBe(false);
    });

    it('healthCheck() returns false when Redis is unavailable', async () => {
      const result = await store.healthCheck();
      expect(result).toBe(false);
    });
  });

  // ── 2. ClientClosedError from disconnect() must be swallowed ────────────────

  describe('ClientClosedError during cleanup', () => {
    it('initialize() must NOT propagate ClientClosedError thrown by disconnect()', async () => {
      const clientClosedError = new Error('ClientClosedError: The client is closed');
      const mockRedis = makeMockRedis({
        connect: jest.fn().mockRejectedValue(new Error('Max reconnection attempts exceeded')),
        disconnect: jest.fn(() => { throw clientClosedError; }),
      });
      mockCreateClient.mockReturnValue(mockRedis);
      store = new RedisTokenRevocationStore('redis://localhost:6379');

      // Must resolve, not reject
      await expect(store.initialize()).resolves.toBeUndefined();
    });
  });

  // ── 3. 'end' event does NOT reset this.initializing ─────────────────────────

  describe("'end' event handler", () => {
    it("does NOT reset initializing flag while initialize() is still running", async () => {
      let resolveConnect!: () => void;
      const connectPromise = new Promise<void>(resolve => {
        resolveConnect = resolve;
      });
      const mockRedis = makeMockRedis({
        connect: jest.fn(() => connectPromise),
        ping: jest.fn().mockResolvedValue('PONG'),
      });
      mockCreateClient.mockReturnValue(mockRedis);
      store = new RedisTokenRevocationStore('redis://localhost:6379');

      // Start initialize() without awaiting so it stays in-flight
      const initPromise = store.initialize();

      // Verify initializing is true while connect is pending
      // Access private field via cast
      expect((store as any).initializing).toBe(true);

      // Fire 'end' event while initialize() is still running
      mockRedis._emit('end');

      // initializing must remain true (initialize() is still running)
      expect((store as any).initializing).toBe(true);

      // Now let connect() succeed to complete initialize()
      resolveConnect();
      await initPromise;

      // After initialize() completes, initializing is false (reset by finally block)
      expect((store as any).initializing).toBe(false);
    });

    it("resets initialized and redis when fired after a successful connection is lost", async () => {
      const mockRedis = makeMockRedis();
      mockCreateClient.mockReturnValue(mockRedis);
      store = new RedisTokenRevocationStore('redis://localhost:6379');

      await store.initialize();
      expect((store as any).initialized).toBe(true);

      // Simulate connection drop after successful init
      mockRedis._emit('end');

      expect((store as any).initialized).toBe(false);
      expect((store as any).redis).toBeNull();
    });
  });

  // ── 4. Happy-path: successful revocation and lookup ──────────────────────────

  describe('happy path (Redis available)', () => {
    let mockRedis: ReturnType<typeof makeMockRedis>;

    beforeEach(async () => {
      mockRedis = makeMockRedis();
      mockCreateClient.mockReturnValue(mockRedis);
      store = new RedisTokenRevocationStore('redis://localhost:6379');
      await store.initialize();
    });

    it('revokeToken() returns true on success', async () => {
      const result = await store.revokeToken('jti-abc', { reason: 'logout', userId: 'u1' });
      expect(result).toBe(true);
      expect(mockRedis.setEx).toHaveBeenCalledWith(
        'revoked:token:jti-abc',
        expect.any(Number),
        expect.stringContaining('"reason":"logout"'),
      );
    });

    it('isTokenRevoked() returns false when token not in Redis', async () => {
      mockRedis.exists.mockResolvedValue(0);
      const result = await store.isTokenRevoked('jti-unknown');
      expect(result).toBe(false);
    });

    it('isTokenRevoked() returns true when token is in Redis', async () => {
      mockRedis.exists.mockResolvedValue(1);
      const result = await store.isTokenRevoked('jti-revoked');
      expect(result).toBe(true);
    });

    it('isUserTokenRevoked() returns false when no revocation record exists', async () => {
      mockRedis.get.mockResolvedValue(null);
      const result = await store.isUserTokenRevoked('user-id', Date.now() / 1000 - 60);
      expect(result).toBe(false);
    });

    it('isUserTokenRevoked() returns true when token issued before revocation timestamp', async () => {
      const revokedAt = Date.now() / 1000;
      mockRedis.get.mockResolvedValue(JSON.stringify({ revokedAt, reason: 'logout' }));
      // Token issued 60s before revocation
      const result = await store.isUserTokenRevoked('user-id', revokedAt - 60);
      expect(result).toBe(true);
    });

    it('isUserTokenRevoked() returns false when token issued after revocation timestamp', async () => {
      const revokedAt = Date.now() / 1000 - 120;
      mockRedis.get.mockResolvedValue(JSON.stringify({ revokedAt, reason: 'logout' }));
      // Token issued 60s after revocation
      const result = await store.isUserTokenRevoked('user-id', revokedAt + 60);
      expect(result).toBe(false);
    });

    it('healthCheck() returns true when Redis responds to PING', async () => {
      mockRedis.ping.mockResolvedValue('PONG');
      const result = await store.healthCheck();
      expect(result).toBe(true);
    });

    it('duplicate initialize() calls are idempotent', async () => {
      await store.initialize(); // already initialized
      expect(mockCreateClient).toHaveBeenCalledTimes(1);
    });
  });

  // ── 5. Module lifecycle ───────────────────────────────────────────────────────

  describe('module lifecycle', () => {
    it('onModuleInit() triggers initialize() asynchronously without blocking', () => {
      const mockRedis = makeMockRedis();
      mockCreateClient.mockReturnValue(mockRedis);
      store = new RedisTokenRevocationStore('redis://localhost:6379');

      // Must return synchronously (void, not a Promise)
      const result = store.onModuleInit();
      expect(result).toBeUndefined();
    });

    it('onModuleDestroy() calls close() which quits Redis', async () => {
      const mockRedis = makeMockRedis();
      mockCreateClient.mockReturnValue(mockRedis);
      store = new RedisTokenRevocationStore('redis://localhost:6379');
      await store.initialize();

      await store.onModuleDestroy();
      expect(mockRedis.quit).toHaveBeenCalled();
    });
  });
});
