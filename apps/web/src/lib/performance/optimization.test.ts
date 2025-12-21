/**
 * SAHOOL Performance Optimization Tests
 * اختبارات تحسين الأداء
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import {
  debounce,
  throttle,
  memoize,
  calculateVirtualScroll,
  getOptimalImageSize,
  deduplicateRequest,
  Performance,
} from './optimization';

describe('Performance Optimization', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  describe('debounce', () => {
    it('should debounce function calls', () => {
      const fn = vi.fn();
      const debouncedFn = debounce(fn, 100);

      debouncedFn();
      debouncedFn();
      debouncedFn();

      expect(fn).not.toHaveBeenCalled();

      vi.advanceTimersByTime(100);

      expect(fn).toHaveBeenCalledTimes(1);
    });

    it('should pass arguments correctly', () => {
      const fn = vi.fn();
      const debouncedFn = debounce(fn, 100);

      debouncedFn('arg1', 'arg2');
      vi.advanceTimersByTime(100);

      expect(fn).toHaveBeenCalledWith('arg1', 'arg2');
    });

    it('should handle leading option', () => {
      const fn = vi.fn();
      const debouncedFn = debounce(fn, 100, { leading: true });

      debouncedFn();
      expect(fn).toHaveBeenCalledTimes(1);

      debouncedFn();
      expect(fn).toHaveBeenCalledTimes(1);

      vi.advanceTimersByTime(100);
      expect(fn).toHaveBeenCalledTimes(2);
    });

    it('should have cancel method', () => {
      const fn = vi.fn();
      const debouncedFn = debounce(fn, 100);

      debouncedFn();
      debouncedFn.cancel();
      vi.advanceTimersByTime(100);

      expect(fn).not.toHaveBeenCalled();
    });

    it('should have flush method', () => {
      const fn = vi.fn();
      const debouncedFn = debounce(fn, 100);

      debouncedFn();
      debouncedFn.flush();

      expect(fn).toHaveBeenCalledTimes(1);
    });
  });

  describe('throttle', () => {
    it('should throttle function calls', () => {
      const fn = vi.fn();
      const throttledFn = throttle(fn, 100, { leading: true, trailing: false });

      throttledFn();
      throttledFn();
      throttledFn();

      expect(fn).toHaveBeenCalledTimes(1);

      vi.advanceTimersByTime(100);
      throttledFn();

      expect(fn).toHaveBeenCalledTimes(2);
    });

    it('should pass arguments correctly', () => {
      const fn = vi.fn();
      const throttledFn = throttle(fn, 100);

      throttledFn('arg1');
      expect(fn).toHaveBeenCalledWith('arg1');
    });

    it('should handle trailing option', () => {
      const fn = vi.fn();
      const throttledFn = throttle(fn, 100, { trailing: true });

      throttledFn('first');
      throttledFn('second');
      throttledFn('third');

      expect(fn).toHaveBeenCalledTimes(1);

      vi.advanceTimersByTime(100);

      expect(fn).toHaveBeenCalledTimes(2);
      expect(fn).toHaveBeenLastCalledWith('third');
    });

    it('should have cancel method', () => {
      const fn = vi.fn();
      const throttledFn = throttle(fn, 100, { trailing: true });

      throttledFn();
      throttledFn();
      throttledFn.cancel();
      vi.advanceTimersByTime(100);

      expect(fn).toHaveBeenCalledTimes(1);
    });
  });

  describe('memoize', () => {
    it('should cache function results', () => {
      const fn = vi.fn((x: number) => x * 2);
      const memoizedFn = memoize(fn);

      expect(memoizedFn(5)).toBe(10);
      expect(memoizedFn(5)).toBe(10);

      expect(fn).toHaveBeenCalledTimes(1);
    });

    it('should respect maxSize option', () => {
      const fn = vi.fn((x: number) => x * 2);
      const memoizedFn = memoize(fn, { maxSize: 2 });

      memoizedFn(1);
      memoizedFn(2);
      memoizedFn(3); // This should evict 1

      expect(fn).toHaveBeenCalledTimes(3);

      memoizedFn(1); // Should compute again
      expect(fn).toHaveBeenCalledTimes(4);

      memoizedFn(3); // Should be cached
      expect(fn).toHaveBeenCalledTimes(4);
    });

    it('should use custom key generator', () => {
      const fn = vi.fn((obj: { id: number }) => obj.id * 2);
      const memoizedFn = memoize(fn, {
        keyGenerator: (obj) => String(obj.id),
      });

      memoizedFn({ id: 1 });
      memoizedFn({ id: 1 }); // Different object, same id

      expect(fn).toHaveBeenCalledTimes(1);
    });
  });

  describe('calculateVirtualScroll', () => {
    it('should calculate visible items correctly', () => {
      const result = calculateVirtualScroll(0, {
        totalItems: 1000,
        itemHeight: 50,
        containerHeight: 500,
        overscan: 3,
      });

      expect(result.startIndex).toBe(0);
      expect(result.endIndex).toBeGreaterThan(result.startIndex);
      expect(result.offsetY).toBe(0);
    });

    it('should handle scroll position', () => {
      const result = calculateVirtualScroll(500, {
        totalItems: 1000,
        itemHeight: 50,
        containerHeight: 500,
        overscan: 3,
      });

      expect(result.startIndex).toBeGreaterThan(0);
      expect(result.offsetY).toBeGreaterThan(0);
    });

    it('should calculate total height correctly', () => {
      const result = calculateVirtualScroll(0, {
        totalItems: 100,
        itemHeight: 50,
        containerHeight: 500,
        overscan: 0,
      });

      expect(result.totalHeight).toBe(5000);
    });

    it('should handle empty list', () => {
      const result = calculateVirtualScroll(0, {
        totalItems: 0,
        itemHeight: 50,
        containerHeight: 500,
        overscan: 3,
      });

      expect(result.startIndex).toBe(0);
      expect(result.endIndex).toBe(0);
      expect(result.totalHeight).toBe(0);
    });
  });

  describe('getOptimalImageSize', () => {
    it('should return optimal image size for width', () => {
      const result = getOptimalImageSize(400);
      expect(result).toBeGreaterThanOrEqual(400);
    });

    it('should cap at maximum size', () => {
      const result = getOptimalImageSize(3000);
      expect(result).toBeLessThanOrEqual(1920);
    });

    it('should return smallest size for small widths', () => {
      const result = getOptimalImageSize(100);
      expect(result).toBe(320);
    });
  });

  describe('deduplicateRequest', () => {
    it('should deduplicate concurrent requests', async () => {
      vi.useRealTimers();

      const fn = vi.fn().mockResolvedValue('result');

      const promise1 = deduplicateRequest('key1', fn);
      const promise2 = deduplicateRequest('key1', fn);

      const [result1, result2] = await Promise.all([promise1, promise2]);

      expect(result1).toBe('result');
      expect(result2).toBe('result');
      expect(fn).toHaveBeenCalledTimes(1);
    });

    it('should make new request after window expires', async () => {
      vi.useRealTimers();

      const fn = vi.fn().mockResolvedValue('result');

      await deduplicateRequest('key2', fn, { window: 10 });
      // Wait for dedup window to expire
      await new Promise(resolve => setTimeout(resolve, 20));
      await deduplicateRequest('key2', fn, { window: 10 });

      expect(fn).toHaveBeenCalledTimes(2);
    });
  });

  describe('Performance export', () => {
    it('should export all functions', () => {
      expect(Performance.debounce).toBeDefined();
      expect(Performance.throttle).toBeDefined();
      expect(Performance.memoize).toBeDefined();
      expect(Performance.calculateVirtualScroll).toBeDefined();
      expect(Performance.getOptimalImageSize).toBeDefined();
      expect(Performance.deduplicateRequest).toBeDefined();
    });
  });
});
