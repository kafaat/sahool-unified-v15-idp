/**
 * Performance Utilities
 * أدوات تحسين الأداء
 */

/**
 * Debounced function interface with cancel capability
 * واجهة الدالة المؤخرة مع إمكانية الإلغاء
 */
export interface DebouncedFunction<T extends (...args: unknown[]) => unknown> {
  (...args: Parameters<T>): void;
  /** Cancel any pending execution / إلغاء أي تنفيذ معلق */
  cancel: () => void;
  /** Flush pending execution immediately / تنفيذ معلق فوراً */
  flush: () => void;
  /** Check if there's a pending execution / التحقق من وجود تنفيذ معلق */
  pending: () => boolean;
}

/**
 * Debounce function - delays execution until after wait time
 * تأخير تنفيذ الدالة حتى انتهاء وقت الانتظار
 *
 * @param func - الدالة - Function to debounce
 * @param wait - الانتظار - Wait time in milliseconds
 * @param options - الخيارات - Options for leading/trailing edge
 * @returns دالة مؤخرة - Debounced function with cancel/flush
 *
 * @example
 * const debouncedSearch = debounce(search, 300);
 * debouncedSearch('query');
 * debouncedSearch.cancel(); // Cancel pending
 */
export function debounce<T extends (...args: unknown[]) => unknown>(
  func: T,
  wait: number,
  options: { leading?: boolean; trailing?: boolean } = {},
): DebouncedFunction<T> {
  const { leading = false, trailing = true } = options;

  let timeoutId: ReturnType<typeof setTimeout> | null = null;
  let lastArgs: Parameters<T> | null = null;
  let lastCallTime: number | undefined;
  let leadingInvoked = false;

  function invokeFunc(args: Parameters<T>): void {
    func(...args);
  }

  function debounced(...args: Parameters<T>): void {
    const now = Date.now();
    lastArgs = args;
    lastCallTime = now;

    // Leading edge invocation
    if (leading && !timeoutId && !leadingInvoked) {
      leadingInvoked = true;
      invokeFunc(args);
    }

    // Clear existing timeout
    if (timeoutId) {
      clearTimeout(timeoutId);
    }

    // Set up trailing edge
    timeoutId = setTimeout(() => {
      if (trailing && lastArgs) {
        // Only invoke if not already invoked on leading edge
        if (!leading || !leadingInvoked || lastCallTime !== now) {
          invokeFunc(lastArgs);
        }
      }
      timeoutId = null;
      lastArgs = null;
      leadingInvoked = false;
    }, wait);
  }

  debounced.cancel = function cancel(): void {
    if (timeoutId) {
      clearTimeout(timeoutId);
      timeoutId = null;
    }
    lastArgs = null;
    leadingInvoked = false;
  };

  debounced.flush = function flush(): void {
    if (timeoutId && lastArgs) {
      clearTimeout(timeoutId);
      invokeFunc(lastArgs);
      timeoutId = null;
      lastArgs = null;
      leadingInvoked = false;
    }
  };

  debounced.pending = function pending(): boolean {
    return timeoutId !== null;
  };

  return debounced;
}

/**
 * Throttled function interface with cancel capability
 * واجهة الدالة المُقيّدة مع إمكانية الإلغاء
 */
export interface ThrottledFunction<T extends (...args: unknown[]) => unknown> {
  (...args: Parameters<T>): void;
  /** Cancel any pending execution / إلغاء أي تنفيذ معلق */
  cancel: () => void;
  /** Flush pending execution immediately / تنفيذ معلق فوراً */
  flush: () => void;
}

/**
 * Throttle function - limits execution to once per wait time
 * تقييد تنفيذ الدالة لمرة واحدة خلال فترة الانتظار
 *
 * @param func - الدالة - Function to throttle
 * @param wait - الانتظار - Wait time in milliseconds
 * @param options - الخيارات - Options for leading/trailing edge
 * @returns دالة مُقيّدة - Throttled function with cancel/flush
 *
 * @example
 * const throttledScroll = throttle(handleScroll, 100);
 * window.addEventListener('scroll', throttledScroll);
 */
export function throttle<T extends (...args: unknown[]) => unknown>(
  func: T,
  wait: number,
  options: { leading?: boolean; trailing?: boolean } = {},
): ThrottledFunction<T> {
  const { leading = true, trailing = true } = options;

  let lastTime = 0;
  let timeoutId: ReturnType<typeof setTimeout> | null = null;
  let lastArgs: Parameters<T> | null = null;

  function invokeFunc(args: Parameters<T>): void {
    func(...args);
    lastTime = Date.now();
  }

  function throttled(...args: Parameters<T>): void {
    const now = Date.now();
    const remaining = wait - (now - lastTime);
    lastArgs = args;

    if (remaining <= 0 || remaining > wait) {
      if (timeoutId) {
        clearTimeout(timeoutId);
        timeoutId = null;
      }

      if (leading) {
        invokeFunc(args);
      } else {
        lastTime = now;
      }
    } else if (!timeoutId && trailing) {
      timeoutId = setTimeout(() => {
        if (lastArgs) {
          invokeFunc(lastArgs);
        }
        timeoutId = null;
        lastArgs = null;
      }, remaining);
    }
  }

  throttled.cancel = function cancel(): void {
    if (timeoutId) {
      clearTimeout(timeoutId);
      timeoutId = null;
    }
    lastArgs = null;
    lastTime = 0;
  };

  throttled.flush = function flush(): void {
    if (timeoutId && lastArgs) {
      clearTimeout(timeoutId);
      invokeFunc(lastArgs);
      timeoutId = null;
      lastArgs = null;
    }
  };

  return throttled;
}

/**
 * Memoize options
 * خيارات التخزين المؤقت
 */
export interface MemoizeOptions<T extends (...args: unknown[]) => unknown> {
  /** Key resolver function / دالة حل المفتاح */
  keyResolver?: (...args: Parameters<T>) => string;
  /** Maximum cache size / الحد الأقصى لحجم الذاكرة المؤقتة */
  maxSize?: number;
  /** Time-to-live in milliseconds / مدة الصلاحية بالمللي ثانية */
  ttl?: number;
}

/**
 * Memoized function interface
 * واجهة الدالة المُخزّنة مؤقتاً
 */
export interface MemoizedFunction<T extends (...args: unknown[]) => unknown> {
  (...args: Parameters<T>): ReturnType<T>;
  /** Clear the cache / مسح الذاكرة المؤقتة */
  clear: () => void;
  /** Delete a specific cache entry / حذف إدخال محدد */
  delete: (...args: Parameters<T>) => boolean;
  /** Check if key exists in cache / التحقق من وجود المفتاح */
  has: (...args: Parameters<T>) => boolean;
  /** Get cache size / الحصول على حجم الذاكرة المؤقتة */
  size: () => number;
}

interface CacheEntry<V> {
  value: V;
  timestamp: number;
}

/**
 * Memoize function results with optional TTL and max size
 * تخزين نتائج الدالة مؤقتاً مع خيارات TTL والحد الأقصى للحجم
 *
 * @param func - الدالة - Function to memoize
 * @param options - الخيارات - Memoization options
 * @returns دالة مُخزّنة مؤقتاً - Memoized function with cache control
 *
 * @example
 * const memoizedFetch = memoize(fetchData, {
 *   maxSize: 100,
 *   ttl: 60000 // 1 minute
 * });
 */
export function memoize<T extends (...args: unknown[]) => unknown>(
  func: T,
  options: MemoizeOptions<T> | ((...args: Parameters<T>) => string) = {},
): MemoizedFunction<T> {
  // Support legacy signature (keyResolver as second argument)
  const opts: MemoizeOptions<T> =
    typeof options === "function" ? { keyResolver: options } : options;

  const { keyResolver, maxSize = 1000, ttl } = opts;

  const cache = new Map<string, CacheEntry<ReturnType<T>>>();

  function getKey(args: Parameters<T>): string {
    return keyResolver ? keyResolver(...args) : JSON.stringify(args);
  }

  function isExpired(entry: CacheEntry<ReturnType<T>>): boolean {
    if (!ttl) return false;
    return Date.now() - entry.timestamp > ttl;
  }

  function evictOldest(): void {
    // Simple LRU-like eviction: remove first (oldest) entry
    const firstKey = cache.keys().next().value;
    if (firstKey !== undefined) {
      cache.delete(firstKey);
    }
  }

  function memoized(...args: Parameters<T>): ReturnType<T> {
    const key = getKey(args);
    const cached = cache.get(key);

    if (cached && !isExpired(cached)) {
      // Move to end (most recently used) - LRU behavior
      cache.delete(key);
      cache.set(key, cached);
      return cached.value;
    }

    // Remove expired entry if exists
    if (cached) {
      cache.delete(key);
    }

    // Evict if at capacity
    if (cache.size >= maxSize) {
      evictOldest();
    }

    const result = func(...args) as ReturnType<T>;
    cache.set(key, { value: result, timestamp: Date.now() });
    return result;
  }

  memoized.clear = function clear(): void {
    cache.clear();
  };

  memoized.delete = function deleteEntry(...args: Parameters<T>): boolean {
    return cache.delete(getKey(args));
  };

  memoized.has = function has(...args: Parameters<T>): boolean {
    const key = getKey(args);
    const entry = cache.get(key);
    if (!entry) return false;
    if (isExpired(entry)) {
      cache.delete(key);
      return false;
    }
    return true;
  };

  memoized.size = function size(): number {
    // Clean up expired entries on size check
    if (ttl) {
      for (const [key, entry] of cache) {
        if (isExpired(entry)) {
          cache.delete(key);
        }
      }
    }
    return cache.size;
  };

  return memoized as MemoizedFunction<T>;
}

/**
 * Batch multiple calls into a single execution
 * تجميع عدة استدعاءات في تنفيذ واحد
 */
export function batchCalls<T>(
  callback: (items: T[]) => void,
  wait: number = 16, // ~1 frame at 60fps
): (item: T) => void {
  let batch: T[] = [];
  let timeoutId: ReturnType<typeof setTimeout> | null = null;

  return function batched(item: T) {
    batch.push(item);

    if (!timeoutId) {
      timeoutId = setTimeout(() => {
        callback(batch);
        batch = [];
        timeoutId = null;
      }, wait);
    }
  };
}

/**
 * Request idle callback with fallback
 * طلب استدعاء وقت الفراغ مع بديل
 */
export function requestIdleCallback(
  callback: () => void,
  options?: { timeout?: number },
): number {
  if (typeof window !== "undefined" && "requestIdleCallback" in window) {
    return (
      window as Window & {
        requestIdleCallback: (
          cb: () => void,
          opts?: { timeout?: number },
        ) => number;
      }
    ).requestIdleCallback(callback, options);
  }
  // Fallback to setTimeout
  return setTimeout(callback, options?.timeout || 1) as unknown as number;
}

/**
 * Cancel idle callback
 */
export function cancelIdleCallback(id: number): void {
  if (typeof window !== "undefined" && "cancelIdleCallback" in window) {
    (
      window as Window & { cancelIdleCallback: (id: number) => void }
    ).cancelIdleCallback(id);
  } else {
    clearTimeout(id);
  }
}

/**
 * Measure execution time
 * قياس وقت التنفيذ
 */
export async function measureTime<T>(
  fn: () => T | Promise<T>,
  label?: string,
): Promise<{ result: T; duration: number }> {
  const start = performance.now();
  const result = await fn();
  const duration = performance.now() - start;

  if (label && process.env.NODE_ENV === "development") {
    console.log(`[Performance] ${label}: ${duration.toFixed(2)}ms`);
  }

  return { result, duration };
}

/**
 * Create a simple LRU cache
 * إنشاء ذاكرة تخزين مؤقت LRU بسيطة
 */
export function createLRUCache<K, V>(maxSize: number = 100) {
  const cache = new Map<K, V>();

  return {
    get(key: K): V | undefined {
      if (!cache.has(key)) return undefined;
      // Move to end (most recently used)
      const value = cache.get(key)!;
      cache.delete(key);
      cache.set(key, value);
      return value;
    },
    set(key: K, value: V): void {
      if (cache.has(key)) {
        cache.delete(key);
      } else if (cache.size >= maxSize) {
        // Delete oldest (first)
        const firstKey = cache.keys().next().value;
        if (firstKey !== undefined) {
          cache.delete(firstKey);
        }
      }
      cache.set(key, value);
    },
    has(key: K): boolean {
      return cache.has(key);
    },
    delete(key: K): boolean {
      return cache.delete(key);
    },
    clear(): void {
      cache.clear();
    },
    get size(): number {
      return cache.size;
    },
  };
}
