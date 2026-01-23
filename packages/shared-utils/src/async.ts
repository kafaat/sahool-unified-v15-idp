/**
 * Async Utility Functions
 * دوال غير متزامنة مساعدة
 */

/**
 * Sleep/delay for specified milliseconds
 * تأخير لمدة محددة بالمللي ثانية
 *
 * @param ms - المللي ثانية - Milliseconds to sleep
 * @returns وعد - Promise that resolves after delay
 *
 * @example
 * await sleep(1000); // Sleep for 1 second
 */
export function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Retry configuration options
 * خيارات إعادة المحاولة
 */
export interface RetryOptions {
  /** عدد المحاولات - Maximum number of attempts */
  maxAttempts?: number;
  /** التأخير الأولي - Initial delay in ms between retries */
  initialDelay?: number;
  /** الحد الأقصى للتأخير - Maximum delay in ms */
  maxDelay?: number;
  /** المضاعف - Delay multiplier for exponential backoff */
  backoffMultiplier?: number;
  /** إضافة عشوائية - Add jitter to delay */
  jitter?: boolean;
  /** دالة إعادة المحاولة - Predicate to determine if error is retryable */
  retryIf?: (error: Error, attempt: number) => boolean;
  /** عند المحاولة - Callback on each retry attempt */
  onRetry?: (error: Error, attempt: number, delay: number) => void;
}

/**
 * Retry a function with exponential backoff
 * إعادة محاولة دالة مع تراجع أسي
 *
 * @param fn - الدالة - Function to retry
 * @param options - الخيارات - Retry options
 * @returns النتيجة - Result of successful execution
 *
 * @example
 * const result = await retry(
 *   () => fetchData(),
 *   { maxAttempts: 3, initialDelay: 1000 }
 * );
 */
export async function retry<T>(
  fn: () => Promise<T>,
  options: RetryOptions = {},
): Promise<T> {
  const {
    maxAttempts = 3,
    initialDelay = 1000,
    maxDelay = 30000,
    backoffMultiplier = 2,
    jitter = true,
    retryIf = () => true,
    onRetry,
  } = options;

  let lastError: Error | undefined;
  let currentDelay = initialDelay;

  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      return await fn();
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err));
      lastError = error;

      const isLastAttempt = attempt === maxAttempts;
      const shouldRetry = !isLastAttempt && retryIf(error, attempt);

      if (!shouldRetry) {
        throw error;
      }

      // Calculate delay with optional jitter
      let delay = Math.min(currentDelay, maxDelay);
      if (jitter) {
        delay = delay * (0.5 + Math.random());
      }

      // Notify on retry
      if (onRetry) {
        onRetry(error, attempt, delay);
      }

      await sleep(delay);

      // Increase delay for next attempt
      currentDelay *= backoffMultiplier;
    }
  }

  throw lastError || new Error("Retry failed");
}

/**
 * Timeout options
 * خيارات المهلة
 */
export interface TimeoutOptions {
  /** رسالة الخطأ - Custom error message */
  message?: string;
  /** عند المهلة - Callback when timeout occurs */
  onTimeout?: () => void;
}

/**
 * Wrap a promise with a timeout
 * تغليف الوعد بمهلة زمنية
 *
 * @param promise - الوعد - Promise to wrap
 * @param ms - المللي ثانية - Timeout in milliseconds
 * @param options - الخيارات - Timeout options
 * @returns النتيجة - Result or throws TimeoutError
 *
 * @example
 * const result = await timeout(fetchData(), 5000);
 */
export async function timeout<T>(
  promise: Promise<T>,
  ms: number,
  options: TimeoutOptions = {},
): Promise<T> {
  const { message = `Operation timed out after ${ms}ms`, onTimeout } = options;

  let timeoutId: ReturnType<typeof setTimeout>;

  const timeoutPromise = new Promise<never>((_, reject) => {
    timeoutId = setTimeout(() => {
      if (onTimeout) {
        onTimeout();
      }
      reject(new TimeoutError(message, ms));
    }, ms);
  });

  try {
    return await Promise.race([promise, timeoutPromise]);
  } finally {
    clearTimeout(timeoutId!);
  }
}

/**
 * Custom timeout error class
 * فئة خطأ المهلة المخصصة
 */
export class TimeoutError extends Error {
  /** مدة المهلة - Timeout duration in ms */
  readonly timeout: number;

  constructor(message: string, timeout: number) {
    super(message);
    this.name = "TimeoutError";
    this.timeout = timeout;
  }
}

/**
 * Rate limiting options
 * خيارات تحديد المعدل
 */
export interface RateLimitOptions {
  /** عدد الطلبات - Number of requests allowed */
  limit: number;
  /** الفترة الزمنية - Time window in ms */
  window: number;
  /** عند الرفض - Callback when request is rejected */
  onReject?: () => void;
}

/**
 * Create a rate-limited version of a function
 * إنشاء نسخة محدودة المعدل من دالة
 *
 * @param fn - الدالة - Function to rate limit
 * @param options - الخيارات - Rate limit options
 * @returns دالة محدودة - Rate-limited function
 */
export function rateLimit<T extends (...args: unknown[]) => Promise<unknown>>(
  fn: T,
  options: RateLimitOptions,
): T {
  const { limit, window, onReject } = options;
  const timestamps: number[] = [];

  return (async (...args: Parameters<T>) => {
    const now = Date.now();

    // Remove timestamps outside the window
    while (timestamps.length > 0 && timestamps[0] <= now - window) {
      timestamps.shift();
    }

    if (timestamps.length >= limit) {
      if (onReject) {
        onReject();
      }
      throw new Error(`Rate limit exceeded: ${limit} requests per ${window}ms`);
    }

    timestamps.push(now);
    return fn(...args);
  }) as T;
}

/**
 * Queue async operations to run sequentially
 * ترتيب العمليات غير المتزامنة للتشغيل بالتتابع
 */
export class AsyncQueue {
  private queue: Array<() => Promise<void>> = [];
  private running = false;

  /**
   * Add an operation to the queue
   * إضافة عملية إلى قائمة الانتظار
   *
   * @param fn - الدالة - Async function to queue
   * @returns وعد - Promise that resolves when the operation completes
   */
  enqueue<T>(fn: () => Promise<T>): Promise<T> {
    return new Promise((resolve, reject) => {
      this.queue.push(async () => {
        try {
          const result = await fn();
          resolve(result);
        } catch (error) {
          reject(error);
        }
      });

      this.processQueue();
    });
  }

  /**
   * Process the queue
   * معالجة قائمة الانتظار
   */
  private async processQueue(): Promise<void> {
    if (this.running) {
      return;
    }

    this.running = true;

    while (this.queue.length > 0) {
      const operation = this.queue.shift();
      if (operation) {
        await operation();
      }
    }

    this.running = false;
  }

  /**
   * Get queue size
   * الحصول على حجم قائمة الانتظار
   */
  get size(): number {
    return this.queue.length;
  }

  /**
   * Check if queue is currently processing
   * التحقق مما إذا كانت قائمة الانتظار قيد المعالجة
   */
  get isRunning(): boolean {
    return this.running;
  }
}

/**
 * Run promises in parallel with concurrency limit
 * تشغيل الوعود بالتوازي مع حد التزامن
 *
 * @param tasks - المهام - Array of async functions
 * @param concurrency - التزامن - Maximum concurrent executions
 * @returns النتائج - Array of results
 *
 * @example
 * const results = await parallelLimit(
 *   urls.map(url => () => fetch(url)),
 *   5
 * );
 */
export async function parallelLimit<T>(
  tasks: Array<() => Promise<T>>,
  concurrency: number,
): Promise<T[]> {
  const results: T[] = new Array(tasks.length);
  const executing: Promise<void>[] = [];
  let currentIndex = 0;

  const runTask = async (index: number): Promise<void> => {
    results[index] = await tasks[index]();
  };

  for (const [index, _] of tasks.entries()) {
    const promise = runTask(index).then(() => {
      executing.splice(executing.indexOf(promise), 1);
    });

    executing.push(promise);

    if (executing.length >= concurrency) {
      await Promise.race(executing);
    }
  }

  await Promise.all(executing);
  return results;
}

/**
 * Run promises in sequence
 * تشغيل الوعود بالتتابع
 *
 * @param tasks - المهام - Array of async functions
 * @returns النتائج - Array of results
 */
export async function sequential<T>(
  tasks: Array<() => Promise<T>>,
): Promise<T[]> {
  const results: T[] = [];

  for (const task of tasks) {
    results.push(await task());
  }

  return results;
}

/**
 * Poll a condition until it returns true or timeout
 * استقصاء شرط حتى يُرجع صحيح أو انتهاء المهلة
 *
 * @param condition - الشرط - Condition function to poll
 * @param options - الخيارات - Poll options
 * @returns القيمة - Final value when condition is met
 */
export async function poll<T>(
  condition: () => Promise<T | null | false>,
  options: {
    interval?: number;
    timeout?: number;
    onPoll?: (attempt: number) => void;
  } = {},
): Promise<T> {
  const { interval = 1000, timeout: timeoutMs = 30000, onPoll } = options;

  const startTime = Date.now();
  let attempt = 0;

  while (Date.now() - startTime < timeoutMs) {
    attempt++;

    if (onPoll) {
      onPoll(attempt);
    }

    const result = await condition();

    if (result !== null && result !== false) {
      return result;
    }

    await sleep(interval);
  }

  throw new TimeoutError(`Polling timed out after ${timeoutMs}ms`, timeoutMs);
}

/**
 * Create a deferred promise (manually resolvable/rejectable)
 * إنشاء وعد مؤجل (قابل للحل/الرفض يدوياً)
 */
export interface Deferred<T> {
  promise: Promise<T>;
  resolve: (value: T | PromiseLike<T>) => void;
  reject: (reason?: unknown) => void;
}

/**
 * Create a deferred promise
 * إنشاء وعد مؤجل
 *
 * @returns الوعد المؤجل - Deferred promise object
 *
 * @example
 * const deferred = createDeferred<string>();
 * // Later...
 * deferred.resolve('done');
 */
export function createDeferred<T>(): Deferred<T> {
  let resolve!: (value: T | PromiseLike<T>) => void;
  let reject!: (reason?: unknown) => void;

  const promise = new Promise<T>((res, rej) => {
    resolve = res;
    reject = rej;
  });

  return { promise, resolve, reject };
}

/**
 * Debounce async function (waits for settle, returns latest result)
 * تأخير دالة غير متزامنة
 *
 * @param fn - الدالة - Function to debounce
 * @param wait - الانتظار - Wait time in ms
 * @returns دالة مؤخرة - Debounced function
 */
export function debounceAsync<T, Args extends unknown[]>(
  fn: (...args: Args) => Promise<T>,
  wait: number,
): (...args: Args) => Promise<T> {
  let timeoutId: ReturnType<typeof setTimeout> | null = null;
  let pending: Deferred<T> | null = null;

  return (...args: Args): Promise<T> => {
    if (timeoutId) {
      clearTimeout(timeoutId);
    }

    if (!pending) {
      pending = createDeferred<T>();
    }

    const currentPending = pending;

    timeoutId = setTimeout(async () => {
      try {
        const result = await fn(...args);
        currentPending.resolve(result);
      } catch (error) {
        currentPending.reject(error);
      } finally {
        pending = null;
        timeoutId = null;
      }
    }, wait);

    return currentPending.promise;
  };
}

/**
 * Lock mechanism for async operations
 * آلية القفل للعمليات غير المتزامنة
 */
export class AsyncLock {
  private locked = false;
  private waitQueue: Array<() => void> = [];

  /**
   * Acquire the lock
   * الحصول على القفل
   */
  async acquire(): Promise<void> {
    if (!this.locked) {
      this.locked = true;
      return;
    }

    return new Promise((resolve) => {
      this.waitQueue.push(resolve);
    });
  }

  /**
   * Release the lock
   * تحرير القفل
   */
  release(): void {
    if (this.waitQueue.length > 0) {
      const next = this.waitQueue.shift();
      if (next) {
        next();
      }
    } else {
      this.locked = false;
    }
  }

  /**
   * Execute a function with the lock
   * تنفيذ دالة مع القفل
   */
  async withLock<T>(fn: () => Promise<T>): Promise<T> {
    await this.acquire();
    try {
      return await fn();
    } finally {
      this.release();
    }
  }

  /**
   * Check if lock is currently held
   * التحقق مما إذا كان القفل محتفظاً به حالياً
   */
  get isLocked(): boolean {
    return this.locked;
  }
}
