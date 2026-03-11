import 'reflect-metadata';

/**
 * Circuit Breaker Pattern Tests
 * اختبارات نمط قاطع الدائرة
 *
 * Verifies the CircuitBreaker implementation from shared/errors:
 * - State transitions: CLOSED -> OPEN -> HALF_OPEN -> CLOSED
 * - Failure threshold triggers OPEN state
 * - OPEN state rejects calls with ExternalServiceException
 * - Timeout-based recovery to HALF_OPEN
 * - Successful call in HALF_OPEN resets to CLOSED
 * - reset() clears all state
 *
 * Also covers retryWithBackoff, handleAsync, withTimeout, and ErrorAggregator.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

// Mock @nestjs/swagger to avoid decorator metadata issues in vitest/vite-node
vi.mock('@nestjs/swagger', () => ({
  ApiProperty: () => () => {},
  ApiPropertyOptional: () => () => {},
}));

import {
  CircuitBreaker,
  retryWithBackoff,
  handleAsync,
  withTimeout,
  ErrorAggregator,
  AppException,
  ExternalServiceException,
  InternalServerException,
  ErrorCode,
} from '../../../apps/services/shared/errors';

// ==========================================================================
// CircuitBreaker
// ==========================================================================

describe('CircuitBreaker', () => {
  let breaker: CircuitBreaker;

  beforeEach(() => {
    // threshold=3, timeout=60000, resetTimeout=100 (short for testing)
    breaker = new CircuitBreaker(3, 60000, 100);
  });

  // -----------------------------------------------------------------------
  // State transitions
  // -----------------------------------------------------------------------
  describe('state transitions', () => {
    it('starts in CLOSED state', () => {
      const state = breaker.getState();
      expect(state.state).toBe('CLOSED');
      expect(state.failureCount).toBe(0);
      expect(state.lastFailureTime).toBeNull();
    });

    it('stays CLOSED on successful calls', async () => {
      const result = await breaker.execute(() => Promise.resolve('ok'));
      expect(result).toBe('ok');
      expect(breaker.getState().state).toBe('CLOSED');
    });

    it('increments failure count but stays CLOSED below threshold', async () => {
      const failFn = () => Promise.reject(new Error('fail'));

      for (let i = 0; i < 2; i++) {
        await expect(breaker.execute(failFn)).rejects.toThrow('fail');
      }

      const state = breaker.getState();
      expect(state.state).toBe('CLOSED');
      expect(state.failureCount).toBe(2);
    });

    it('transitions to OPEN when failure threshold is reached', async () => {
      const failFn = () => Promise.reject(new Error('service down'));

      for (let i = 0; i < 3; i++) {
        await expect(breaker.execute(failFn)).rejects.toThrow();
      }

      expect(breaker.getState().state).toBe('OPEN');
      expect(breaker.getState().failureCount).toBe(3);
    });

    it('rejects calls immediately when OPEN', async () => {
      const failFn = () => Promise.reject(new Error('fail'));

      // Trip the breaker
      for (let i = 0; i < 3; i++) {
        await expect(breaker.execute(failFn)).rejects.toThrow();
      }

      // Now any call should be rejected without executing the function
      const spyFn = vi.fn().mockResolvedValue('should not run');
      await expect(breaker.execute(spyFn)).rejects.toThrow('circuit breaker is open');
      expect(spyFn).not.toHaveBeenCalled();
    });

    it('throws ExternalServiceException when OPEN', async () => {
      const failFn = () => Promise.reject(new Error('fail'));

      for (let i = 0; i < 3; i++) {
        await expect(breaker.execute(failFn)).rejects.toThrow();
      }

      try {
        await breaker.execute(() => Promise.resolve('x'));
        expect.fail('should have thrown');
      } catch (e) {
        expect(e).toBeInstanceOf(ExternalServiceException);
        expect(e).toBeInstanceOf(AppException);
      }
    });

    it('transitions from OPEN to HALF_OPEN after reset timeout', async () => {
      const failFn = () => Promise.reject(new Error('fail'));

      // Trip the breaker
      for (let i = 0; i < 3; i++) {
        await expect(breaker.execute(failFn)).rejects.toThrow();
      }
      expect(breaker.getState().state).toBe('OPEN');

      // Wait for the reset timeout (100ms)
      await new Promise((r) => setTimeout(r, 150));

      // The next call should be attempted (HALF_OPEN allows a probe)
      const result = await breaker.execute(() => Promise.resolve('recovered'));
      expect(result).toBe('recovered');
      // After success in HALF_OPEN, should transition back to CLOSED
      expect(breaker.getState().state).toBe('CLOSED');
      expect(breaker.getState().failureCount).toBe(0);
    });

    it('returns to OPEN if the HALF_OPEN probe fails', async () => {
      const failFn = () => Promise.reject(new Error('fail'));

      // Trip the breaker
      for (let i = 0; i < 3; i++) {
        await expect(breaker.execute(failFn)).rejects.toThrow();
      }

      // Wait for reset timeout
      await new Promise((r) => setTimeout(r, 150));

      // Probe call fails
      await expect(breaker.execute(failFn)).rejects.toThrow('fail');

      // failure count incremented past threshold again => OPEN
      expect(breaker.getState().state).toBe('OPEN');
    });
  });

  // -----------------------------------------------------------------------
  // reset()
  // -----------------------------------------------------------------------
  describe('reset()', () => {
    it('resets all state to initial values', async () => {
      const failFn = () => Promise.reject(new Error('fail'));

      // Trip the breaker
      for (let i = 0; i < 3; i++) {
        await expect(breaker.execute(failFn)).rejects.toThrow();
      }
      expect(breaker.getState().state).toBe('OPEN');

      breaker.reset();

      const state = breaker.getState();
      expect(state.state).toBe('CLOSED');
      expect(state.failureCount).toBe(0);
      expect(state.lastFailureTime).toBeNull();

      // Should be able to execute again
      const result = await breaker.execute(() => Promise.resolve('after reset'));
      expect(result).toBe('after reset');
    });
  });

  // -----------------------------------------------------------------------
  // Concurrency behavior
  // -----------------------------------------------------------------------
  describe('concurrent calls', () => {
    it('tracks failure count across concurrent failures', async () => {
      const failFn = () => Promise.reject(new Error('concurrent fail'));

      // Fire 3 failures concurrently
      const results = await Promise.allSettled([
        breaker.execute(failFn),
        breaker.execute(failFn),
        breaker.execute(failFn),
      ]);

      expect(results.every((r) => r.status === 'rejected')).toBe(true);
      expect(breaker.getState().state).toBe('OPEN');
    });
  });
});

// ==========================================================================
// retryWithBackoff
// ==========================================================================

describe('retryWithBackoff', () => {
  it('returns the result on first success', async () => {
    const fn = vi.fn().mockResolvedValue('success');
    const result = await retryWithBackoff(fn, { maxRetries: 3, initialDelay: 10 });

    expect(result).toBe('success');
    expect(fn).toHaveBeenCalledTimes(1);
  });

  it('retries on failure and returns on eventual success', async () => {
    const fn = vi
      .fn()
      .mockRejectedValueOnce(new Error('fail 1'))
      .mockRejectedValueOnce(new Error('fail 2'))
      .mockResolvedValue('success');

    const result = await retryWithBackoff(fn, { maxRetries: 3, initialDelay: 10 });

    expect(result).toBe('success');
    expect(fn).toHaveBeenCalledTimes(3);
  });

  it('throws the last error when all retries are exhausted', async () => {
    const fn = vi.fn().mockRejectedValue(new Error('persistent failure'));

    await expect(
      retryWithBackoff(fn, { maxRetries: 3, initialDelay: 10 }),
    ).rejects.toThrow('persistent failure');
    expect(fn).toHaveBeenCalledTimes(3);
  });

  it('does not retry non-retryable AppExceptions', async () => {
    const nonRetryable = new AppException(ErrorCode.VALIDATION_ERROR);
    const fn = vi.fn().mockRejectedValue(nonRetryable);

    await expect(
      retryWithBackoff(fn, { maxRetries: 3, initialDelay: 10 }),
    ).rejects.toThrow();
    expect(fn).toHaveBeenCalledTimes(1);
  });

  it('respects custom shouldRetry predicate', async () => {
    const fn = vi.fn().mockRejectedValue(new Error('custom'));

    await expect(
      retryWithBackoff(fn, {
        maxRetries: 3,
        initialDelay: 10,
        shouldRetry: () => false,
      }),
    ).rejects.toThrow('custom');
    expect(fn).toHaveBeenCalledTimes(1);
  });
});

// ==========================================================================
// handleAsync
// ==========================================================================

describe('handleAsync', () => {
  it('returns the result of a successful async function', async () => {
    const result = await handleAsync(() => Promise.resolve(42));
    expect(result).toBe(42);
  });

  it('rethrows AppException without wrapping', async () => {
    const appExc = new AppException(ErrorCode.FARM_NOT_FOUND);
    await expect(handleAsync(() => Promise.reject(appExc))).rejects.toBe(appExc);
  });

  it('wraps non-AppException errors as InternalServerException', async () => {
    try {
      await handleAsync(() => Promise.reject(new Error('raw error')));
      expect.fail('should have thrown');
    } catch (e) {
      expect(e).toBeInstanceOf(InternalServerException);
      expect(e).toBeInstanceOf(AppException);
    }
  });

  it('returns fallback value when provided and function fails', async () => {
    const result = await handleAsync(() => Promise.reject(new Error('fail')), 'fallback');
    expect(result).toBe('fallback');
  });

  it('does NOT use fallback for AppException errors', async () => {
    const appExc = new AppException(ErrorCode.FORBIDDEN);
    await expect(handleAsync(() => Promise.reject(appExc), 'fallback')).rejects.toBe(appExc);
  });
});

// ==========================================================================
// withTimeout
// ==========================================================================

describe('withTimeout', () => {
  it('returns the value if promise resolves before timeout', async () => {
    const result = await withTimeout(Promise.resolve('fast'), 1000);
    expect(result).toBe('fast');
  });

  it('throws InternalServerException when timeout is exceeded', async () => {
    const slowPromise = new Promise((resolve) => setTimeout(resolve, 500, 'slow'));

    try {
      await withTimeout(slowPromise, 50);
      expect.fail('should have thrown');
    } catch (e) {
      expect(e).toBeInstanceOf(InternalServerException);
      expect((e as any).messageEn).toContain('timed out');
    }
  });

  it('includes custom error message in timeout exception', async () => {
    const slowPromise = new Promise((resolve) => setTimeout(resolve, 500));

    try {
      await withTimeout(slowPromise, 50, 'Database query took too long');
      expect.fail('should have thrown');
    } catch (e) {
      expect((e as any).messageEn).toBe('Database query took too long');
    }
  });
});

// ==========================================================================
// ErrorAggregator
// ==========================================================================

describe('ErrorAggregator', () => {
  it('starts with no errors', () => {
    const agg = new ErrorAggregator();
    expect(agg.hasErrors()).toBe(false);
    expect(agg.getErrors()).toHaveLength(0);
  });

  it('collects errors with indices', () => {
    const agg = new ErrorAggregator();
    agg.add(0, new Error('first'));
    agg.add(2, new Error('third'));

    expect(agg.hasErrors()).toBe(true);
    expect(agg.getErrors()).toHaveLength(2);
    expect(agg.getErrors()[0].index).toBe(0);
    expect(agg.getErrors()[1].index).toBe(2);
  });

  it('does not throw when no errors collected', () => {
    const agg = new ErrorAggregator();
    expect(() => agg.throwIfHasErrors()).not.toThrow();
  });

  it('throws BUSINESS_RULE_VIOLATION with aggregated details', () => {
    const agg = new ErrorAggregator();
    agg.add(0, new Error('row 0 failed'));
    agg.add(3, new Error('row 3 invalid'));

    try {
      agg.throwIfHasErrors();
      expect.fail('should have thrown');
    } catch (e) {
      expect(e).toBeInstanceOf(AppException);
      expect((e as AppException).errorCode).toBe(ErrorCode.BUSINESS_RULE_VIOLATION);
      expect((e as AppException).messageEn).toContain('2 errors');
      expect((e as AppException).details.errors).toHaveLength(2);
      expect((e as AppException).details.errors[0].index).toBe(0);
      expect((e as AppException).details.errors[0].message).toBe('row 0 failed');
    }
  });
});
