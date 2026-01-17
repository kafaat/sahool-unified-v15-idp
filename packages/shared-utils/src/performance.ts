/**
 * Performance Utilities
 * أدوات تحسين الأداء
 */

/**
 * Debounce function - delays execution until after wait time
 * تأخير تنفيذ الدالة حتى انتهاء وقت الانتظار
 */
export function debounce<T extends (...args: unknown[]) => unknown>(
  func: T,
  wait: number,
): (...args: Parameters<T>) => void {
  let timeoutId: ReturnType<typeof setTimeout> | null = null;

  return function debounced(...args: Parameters<T>) {
    if (timeoutId) {
      clearTimeout(timeoutId);
    }
    timeoutId = setTimeout(() => {
      func(...args);
      timeoutId = null;
    }, wait);
  };
}

/**
 * Throttle function - limits execution to once per wait time
 * تقييد تنفيذ الدالة لمرة واحدة خلال فترة الانتظار
 */
export function throttle<T extends (...args: unknown[]) => unknown>(
  func: T,
  wait: number,
): (...args: Parameters<T>) => void {
  let lastTime = 0;
  let timeoutId: ReturnType<typeof setTimeout> | null = null;

  return function throttled(...args: Parameters<T>) {
    const now = Date.now();
    const remaining = wait - (now - lastTime);

    if (remaining <= 0) {
      if (timeoutId) {
        clearTimeout(timeoutId);
        timeoutId = null;
      }
      lastTime = now;
      func(...args);
    } else if (!timeoutId) {
      timeoutId = setTimeout(() => {
        lastTime = Date.now();
        timeoutId = null;
        func(...args);
      }, remaining);
    }
  };
}

/**
 * Memoize function results
 * تخزين نتائج الدالة مؤقتاً
 */
export function memoize<T extends (...args: unknown[]) => unknown>(
  func: T,
  keyResolver?: (...args: Parameters<T>) => string,
): T {
  const cache = new Map<string, ReturnType<T>>();

  return function memoized(...args: Parameters<T>): ReturnType<T> {
    const key = keyResolver ? keyResolver(...args) : JSON.stringify(args);

    if (cache.has(key)) {
      return cache.get(key)!;
    }

    const result = func(...args) as ReturnType<T>;
    cache.set(key, result);
    return result;
  } as T;
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
