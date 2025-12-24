/**
 * SAHOOL Performance Optimization Utilities
 * أدوات تحسين الأداء
 *
 * Features:
 * - Debounce and throttle utilities
 * - Memoization helpers
 * - Virtual scrolling utilities
 * - Image lazy loading
 * - Request deduplication
 */

// ═══════════════════════════════════════════════════════════════════════════
// Debounce & Throttle
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Debounce function execution
 * تأخير تنفيذ الدالة حتى توقف الاستدعاءات
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number,
  options: { leading?: boolean; trailing?: boolean; maxWait?: number } = {}
): T & { cancel: () => void; flush: () => void } {
  let timeoutId: ReturnType<typeof setTimeout> | null = null;
  let lastArgs: any[] | null = null;
  let lastCallTime: number | null = null;
  let lastInvokeTime = 0;
  let result: ReturnType<T>;

  const { leading = false, trailing = true, maxWait } = options;
  const maxing = typeof maxWait === 'number';
  const maxWaitValue = maxing ? Math.max(maxWait, wait) : 0;

  function invokeFunc(time: number): ReturnType<T> {
    const args = lastArgs!;
    lastArgs = null;
    lastInvokeTime = time;
    result = func(...args);
    return result;
  }

  function shouldInvoke(time: number): boolean {
    const timeSinceLastCall = lastCallTime === null ? 0 : time - lastCallTime;
    const timeSinceLastInvoke = time - lastInvokeTime;

    return (
      lastCallTime === null ||
      timeSinceLastCall >= wait ||
      timeSinceLastCall < 0 ||
      (maxing && timeSinceLastInvoke >= maxWaitValue)
    );
  }

  function trailingEdge(time: number): ReturnType<T> | undefined {
    timeoutId = null;

    if (trailing && lastArgs) {
      return invokeFunc(time);
    }
    lastArgs = null;
    return undefined;
  }

  function timerExpired(): void {
    const time = Date.now();
    if (shouldInvoke(time)) {
      trailingEdge(time);
      return;
    }
    const timeSinceLastCall = lastCallTime === null ? 0 : time - lastCallTime;
    const timeSinceLastInvoke = time - lastInvokeTime;
    const timeWaiting = wait - timeSinceLastCall;
    const remainingWait = maxing
      ? Math.min(timeWaiting, maxWaitValue - timeSinceLastInvoke)
      : timeWaiting;

    timeoutId = setTimeout(timerExpired, remainingWait);
  }

  function leadingEdge(time: number): ReturnType<T> | undefined {
    lastInvokeTime = time;
    timeoutId = setTimeout(timerExpired, wait);
    return leading ? invokeFunc(time) : undefined;
  }

  function debounced(this: unknown, ...args: Parameters<T>): ReturnType<T> | undefined {
    const time = Date.now();
    const isInvoking = shouldInvoke(time);

    lastArgs = args;
    lastCallTime = time;

    if (isInvoking) {
      if (timeoutId === null) {
        return leadingEdge(time);
      }
      if (maxing) {
        timeoutId = setTimeout(timerExpired, wait);
        return invokeFunc(time);
      }
    }
    if (timeoutId === null) {
      timeoutId = setTimeout(timerExpired, wait);
    }
    return result;
  }

  debounced.cancel = function (): void {
    if (timeoutId !== null) {
      clearTimeout(timeoutId);
    }
    lastInvokeTime = 0;
    lastArgs = null;
    lastCallTime = null;
    timeoutId = null;
  };

  debounced.flush = function (): ReturnType<T> | undefined {
    if (timeoutId === null) return result;
    return trailingEdge(Date.now());
  };

  return debounced as T & { cancel: () => void; flush: () => void };
}

/**
 * Throttle function execution
 * تحديد معدل تنفيذ الدالة
 */
export function throttle<T extends (...args: Parameters<T>) => ReturnType<T>>(
  func: T,
  wait: number,
  options: { leading?: boolean; trailing?: boolean } = {}
): T & { cancel: () => void } {
  const { leading = true, trailing = true } = options;
  return debounce(func, wait, { leading, trailing, maxWait: wait });
}

// ═══════════════════════════════════════════════════════════════════════════
// Memoization
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Memoize function results with cache
 * حفظ نتائج الدالة في الذاكرة
 */
export function memoize<T extends (...args: any[]) => any>(
  func: T,
  options: {
    maxSize?: number;
    ttl?: number;
    keyGenerator?: (...args: any[]) => string;
  } = {}
): T & { cache: Map<string, { value: ReturnType<T>; timestamp: number }>; clear: () => void } {
  const { maxSize = 100, ttl, keyGenerator = JSON.stringify } = options;
  const cache = new Map<string, { value: ReturnType<T>; timestamp: number }>();

  function memoized(this: unknown, ...args: any[]): ReturnType<T> {
    const key = keyGenerator(args);
    const cached = cache.get(key);
    const now = Date.now();

    if (cached) {
      if (!ttl || now - cached.timestamp < ttl) {
        return cached.value;
      }
      cache.delete(key);
    }

    const result = func.apply(this, args);
    cache.set(key, { value: result, timestamp: now });

    // Evict oldest entries if cache is full
    if (cache.size > maxSize) {
      const firstKey = cache.keys().next().value;
      if (firstKey) cache.delete(firstKey);
    }

    return result;
  }

  memoized.cache = cache;
  memoized.clear = () => cache.clear();

  return memoized as T & { cache: Map<string, { value: ReturnType<T>; timestamp: number }>; clear: () => void };
}

// ═══════════════════════════════════════════════════════════════════════════
// Request Deduplication
// ═══════════════════════════════════════════════════════════════════════════

type PendingRequest<T> = {
  promise: Promise<T>;
  timestamp: number;
};

const pendingRequests = new Map<string, PendingRequest<unknown>>();
const REQUEST_DEDUP_WINDOW = 100; // ms

/**
 * Deduplicate concurrent requests
 * منع تكرار الطلبات المتزامنة
 */
export async function deduplicateRequest<T>(
  key: string,
  requestFn: () => Promise<T>,
  options: { window?: number } = {}
): Promise<T> {
  const { window = REQUEST_DEDUP_WINDOW } = options;
  const now = Date.now();

  // Check for existing pending request
  const pending = pendingRequests.get(key) as PendingRequest<T> | undefined;
  if (pending && now - pending.timestamp < window) {
    return pending.promise;
  }

  // Create new request
  const promise = requestFn().finally(() => {
    // Clean up after request completes
    setTimeout(() => pendingRequests.delete(key), window);
  });

  pendingRequests.set(key, { promise, timestamp: now });

  return promise;
}

// ═══════════════════════════════════════════════════════════════════════════
// Virtual Scrolling Utilities
// ═══════════════════════════════════════════════════════════════════════════

export interface VirtualScrollConfig {
  totalItems: number;
  itemHeight: number;
  containerHeight: number;
  overscan?: number;
}

export interface VirtualScrollResult {
  startIndex: number;
  endIndex: number;
  offsetY: number;
  totalHeight: number;
  visibleItems: number[];
}

/**
 * Calculate virtual scroll indices
 * حساب مؤشرات التمرير الافتراضي
 */
export function calculateVirtualScroll(
  scrollTop: number,
  config: VirtualScrollConfig
): VirtualScrollResult {
  const { totalItems, itemHeight, containerHeight, overscan = 3 } = config;

  // Handle empty list
  if (totalItems === 0) {
    return {
      startIndex: 0,
      endIndex: 0,
      offsetY: 0,
      totalHeight: 0,
      visibleItems: [],
    };
  }

  const totalHeight = totalItems * itemHeight;
  const visibleCount = Math.ceil(containerHeight / itemHeight);

  let startIndex = Math.floor(scrollTop / itemHeight) - overscan;
  startIndex = Math.max(0, startIndex);

  let endIndex = startIndex + visibleCount + overscan * 2;
  endIndex = Math.min(totalItems - 1, endIndex);

  const offsetY = startIndex * itemHeight;
  const visibleItems = Array.from(
    { length: Math.max(0, endIndex - startIndex + 1) },
    (_, i) => startIndex + i
  );

  return {
    startIndex,
    endIndex,
    offsetY,
    totalHeight,
    visibleItems,
  };
}

// ═══════════════════════════════════════════════════════════════════════════
// Image Optimization
// ═══════════════════════════════════════════════════════════════════════════

const IMAGE_SIZES = [320, 640, 768, 1024, 1280, 1536, 1920];

/**
 * Get optimal image size for container width
 * الحصول على حجم الصورة الأمثل لعرض الحاوية
 */
export function getOptimalImageSize(containerWidth: number): number {
  for (const size of IMAGE_SIZES) {
    if (size >= containerWidth) {
      return size;
    }
  }
  return IMAGE_SIZES[IMAGE_SIZES.length - 1]; // Return max size
}

/**
 * Generate responsive image srcset
 * إنشاء srcset للصور المتجاوبة
 */
export function generateSrcSet(
  baseUrl: string,
  widths: number[] = [320, 640, 768, 1024, 1280, 1536]
): string {
  return widths
    .map((width) => {
      const url = baseUrl.includes('?')
        ? `${baseUrl}&w=${width}`
        : `${baseUrl}?w=${width}`;
      return `${url} ${width}w`;
    })
    .join(', ');
}

/**
 * Generate blur placeholder data URL
 * إنشاء صورة ضبابية مؤقتة
 */
export function generateBlurPlaceholder(
  width: number = 10,
  height: number = 10,
  color: string = '#e5e7eb'
): string {
  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}">
      <rect width="${width}" height="${height}" fill="${color}"/>
    </svg>
  `;
  return `data:image/svg+xml;base64,${btoa(svg)}`;
}

// ═══════════════════════════════════════════════════════════════════════════
// Intersection Observer Utilities
// ═══════════════════════════════════════════════════════════════════════════

type ObserverCallback = (entry: IntersectionObserverEntry) => void;

const observers = new Map<string, IntersectionObserver>();
const callbacks = new Map<Element, ObserverCallback>();

/**
 * Create or get shared intersection observer
 * إنشاء أو الحصول على مراقب التقاطع المشترك
 */
export function getIntersectionObserver(
  options: IntersectionObserverInit = {}
): IntersectionObserver {
  const key = JSON.stringify(options);

  if (!observers.has(key)) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        const callback = callbacks.get(entry.target);
        if (callback) callback(entry);
      });
    }, options);
    observers.set(key, observer);
  }

  return observers.get(key)!;
}

/**
 * Observe element with callback
 * مراقبة عنصر مع callback
 */
export function observeElement(
  element: Element,
  callback: ObserverCallback,
  options: IntersectionObserverInit = {}
): () => void {
  const observer = getIntersectionObserver(options);
  callbacks.set(element, callback);
  observer.observe(element);

  return () => {
    observer.unobserve(element);
    callbacks.delete(element);
  };
}

// ═══════════════════════════════════════════════════════════════════════════
// Bundle Analysis
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Mark performance measurement
 * تحديد قياس الأداء
 */
export function markPerformance(name: string): void {
  if (typeof performance !== 'undefined' && performance.mark) {
    performance.mark(name);
  }
}

/**
 * Measure performance between marks
 * قياس الأداء بين العلامات
 */
export function measurePerformance(
  name: string,
  startMark: string,
  endMark: string
): PerformanceEntry | null {
  if (typeof performance !== 'undefined' && performance.measure) {
    try {
      performance.measure(name, startMark, endMark);
      const entries = performance.getEntriesByName(name);
      return entries[entries.length - 1] || null;
    } catch {
      return null;
    }
  }
  return null;
}

// ═══════════════════════════════════════════════════════════════════════════
// Export
// ═══════════════════════════════════════════════════════════════════════════

export const Performance = {
  debounce,
  throttle,
  memoize,
  deduplicateRequest,
  calculateVirtualScroll,
  getOptimalImageSize,
  generateSrcSet,
  generateBlurPlaceholder,
  getIntersectionObserver,
  observeElement,
  markPerformance,
  measurePerformance,
};

export default Performance;
