/**
 * Rate Limiter Tests
 * اختبارات محدد المعدل
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { checkRateLimit, resetRateLimit, cleanupExpiredEntries } from '../rate-limiter';

// Use a counter for unique IDs to avoid state leakage between tests
let testCounter = 0;
function uniqueId(prefix: string) {
  return `${prefix}-${++testCounter}-${Math.random().toString(36).slice(2)}`;
}

describe('Rate Limiter', () => {
  let dateNowSpy: ReturnType<typeof vi.spyOn>;
  let currentTime: number;

  beforeEach(() => {
    currentTime = 1000000000000; // Fixed starting point
    dateNowSpy = vi.spyOn(Date, 'now').mockImplementation(() => currentTime);
  });

  afterEach(() => {
    dateNowSpy.mockRestore();
  });

  it('allows first request', () => {
    const id = uniqueId('first');
    const result = checkRateLimit(id);
    expect(result.allowed).toBe(true);
    expect(result.remaining).toBe(4); // 5 max - 1
  });

  it('tracks multiple attempts', () => {
    const id = uniqueId('multi');

    const r1 = checkRateLimit(id);
    expect(r1.allowed).toBe(true);
    expect(r1.remaining).toBe(4);

    const r2 = checkRateLimit(id);
    expect(r2.allowed).toBe(true);
    expect(r2.remaining).toBe(3);

    const r3 = checkRateLimit(id);
    expect(r3.allowed).toBe(true);
    expect(r3.remaining).toBe(2);
  });

  it('blocks after max attempts exceeded', () => {
    const id = uniqueId('block');

    // Use up all 5 attempts
    for (let i = 0; i < 5; i++) {
      checkRateLimit(id);
    }

    // 6th attempt should be blocked
    const result = checkRateLimit(id);
    expect(result.allowed).toBe(false);
    expect(result.remaining).toBe(0);
    expect(result.message).toBeDefined();
    expect(result.message).toContain('temporarily locked');
  });

  it('stays blocked during lockout period', () => {
    const id = uniqueId('lockout');

    // Exceed limit
    for (let i = 0; i <= 5; i++) {
      checkRateLimit(id);
    }

    // Advance 5 minutes (still within 30-min lockout)
    currentTime += 5 * 60 * 1000;

    const result = checkRateLimit(id);
    expect(result.allowed).toBe(false);
  });

  it('resets after lockout period expires', () => {
    const id = uniqueId('reset');

    // Exceed limit
    for (let i = 0; i <= 5; i++) {
      checkRateLimit(id);
    }

    // Wait for lockout to expire (30 min + 1ms)
    currentTime += 30 * 60 * 1000 + 1;

    const result = checkRateLimit(id);
    expect(result.allowed).toBe(true);
  });

  it('resets window after time passes', () => {
    const id = uniqueId('window');

    // Make some attempts
    checkRateLimit(id);
    checkRateLimit(id);

    // Advance past the 15 min window
    currentTime += 16 * 60 * 1000;

    const result = checkRateLimit(id);
    expect(result.allowed).toBe(true);
    expect(result.remaining).toBe(4); // Reset to max - 1
  });

  it('supports custom config', () => {
    const id = uniqueId('custom');
    const config = { maxAttempts: 2, windowMs: 1000, lockoutDurationMs: 2000 };

    checkRateLimit(id, config);
    checkRateLimit(id, config);
    const result = checkRateLimit(id, config);

    expect(result.allowed).toBe(false);
  });

  describe('resetRateLimit', () => {
    it('resets rate limit for identifier', () => {
      const id = uniqueId('reset-fn');

      // Exceed limit
      for (let i = 0; i <= 5; i++) {
        checkRateLimit(id);
      }

      expect(checkRateLimit(id).allowed).toBe(false);

      // Reset
      resetRateLimit(id);

      // Should be allowed again
      expect(checkRateLimit(id).allowed).toBe(true);
    });
  });

  describe('cleanupExpiredEntries', () => {
    it('runs without errors', () => {
      const id = uniqueId('cleanup');
      checkRateLimit(id);

      expect(() => cleanupExpiredEntries()).not.toThrow();
    });
  });
});
