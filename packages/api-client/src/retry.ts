// ═══════════════════════════════════════════════════════════════════════════════
// SAHOOL API Client - Retry Logic with Exponential Backoff
// منطق إعادة المحاولة مع التراجع الأسي
// ═══════════════════════════════════════════════════════════════════════════════

import { AxiosError, AxiosInstance, AxiosRequestConfig, AxiosResponse } from "axios";

// ─────────────────────────────────────────────────────────────────────────────
// Types
// ─────────────────────────────────────────────────────────────────────────────

export interface RetryConfig {
  /**
   * Maximum number of retry attempts
   * @default 3
   */
  maxRetries: number;

  /**
   * Initial delay in milliseconds before first retry
   * @default 1000
   */
  initialDelay: number;

  /**
   * Maximum delay in milliseconds between retries
   * @default 30000
   */
  maxDelay: number;

  /**
   * Multiplier for exponential backoff
   * @default 2
   */
  backoffMultiplier: number;

  /**
   * Whether to add jitter to prevent thundering herd
   * @default true
   */
  jitter: boolean;

  /**
   * HTTP status codes that should trigger a retry
   * @default [408, 429, 500, 502, 503, 504]
   */
  retryableStatusCodes: number[];

  /**
   * HTTP methods that should be retried (idempotent methods)
   * @default ['GET', 'HEAD', 'OPTIONS', 'PUT', 'DELETE']
   */
  retryableMethods: string[];

  /**
   * Whether to retry on network errors
   * @default true
   */
  retryOnNetworkError: boolean;

  /**
   * Whether to retry on timeout errors
   * @default true
   */
  retryOnTimeout: boolean;

  /**
   * Custom function to determine if a request should be retried
   */
  shouldRetry?: (error: AxiosError, attemptNumber: number) => boolean;

  /**
   * Callback called before each retry attempt
   */
  onRetry?: (
    error: AxiosError,
    attemptNumber: number,
    delay: number,
  ) => void | Promise<void>;

  /**
   * Callback called when all retries are exhausted
   */
  onExhausted?: (error: AxiosError, totalAttempts: number) => void;
}

export interface RetryState {
  attemptNumber: number;
  lastError?: AxiosError;
  startTime: number;
  totalDelay: number;
}

// Extend AxiosRequestConfig to include retry state
declare module "axios" {
  interface InternalAxiosRequestConfig {
    __retryState?: RetryState;
    __retryConfig?: Partial<RetryConfig>;
    __skipRetry?: boolean;
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Default Configuration
// ─────────────────────────────────────────────────────────────────────────────

export const DEFAULT_RETRY_CONFIG: RetryConfig = {
  maxRetries: 3,
  initialDelay: 1000,
  maxDelay: 30000,
  backoffMultiplier: 2,
  jitter: true,
  retryableStatusCodes: [408, 429, 500, 502, 503, 504],
  retryableMethods: ["GET", "HEAD", "OPTIONS", "PUT", "DELETE"],
  retryOnNetworkError: true,
  retryOnTimeout: true,
};

// ─────────────────────────────────────────────────────────────────────────────
// Utility Functions
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Calculate delay with exponential backoff and optional jitter
 */
export function calculateDelay(
  attemptNumber: number,
  config: RetryConfig,
): number {
  // Exponential backoff: delay = initialDelay * (multiplier ^ attemptNumber)
  const exponentialDelay =
    config.initialDelay * Math.pow(config.backoffMultiplier, attemptNumber - 1);

  // Cap at max delay
  const cappedDelay = Math.min(exponentialDelay, config.maxDelay);

  // Add jitter (random value between 0 and 50% of delay)
  if (config.jitter) {
    const jitterRange = cappedDelay * 0.5;
    const jitterValue = Math.random() * jitterRange;
    return Math.round(cappedDelay + jitterValue);
  }

  return Math.round(cappedDelay);
}

/**
 * Calculate delay respecting Retry-After header (for 429 responses)
 */
export function calculateRetryAfterDelay(
  error: AxiosError,
  config: RetryConfig,
  attemptNumber: number,
): number {
  const retryAfterHeader = error.response?.headers?.["retry-after"];

  if (retryAfterHeader) {
    // Retry-After can be seconds or HTTP date
    const retryAfterSeconds = parseInt(retryAfterHeader, 10);

    if (!isNaN(retryAfterSeconds)) {
      // Value is in seconds, convert to ms
      return Math.min(retryAfterSeconds * 1000, config.maxDelay);
    }

    // Try to parse as HTTP date
    const retryAfterDate = new Date(retryAfterHeader).getTime();
    if (!isNaN(retryAfterDate)) {
      const delayMs = retryAfterDate - Date.now();
      return Math.min(Math.max(delayMs, 0), config.maxDelay);
    }
  }

  // Fall back to exponential backoff
  return calculateDelay(attemptNumber, config);
}

/**
 * Check if an error is a network error (no response)
 */
export function isNetworkError(error: AxiosError): boolean {
  return !error.response && Boolean(error.code);
}

/**
 * Check if an error is a timeout error
 */
export function isTimeoutError(error: AxiosError): boolean {
  return (
    error.code === "ECONNABORTED" ||
    error.code === "ETIMEDOUT" ||
    error.message.toLowerCase().includes("timeout")
  );
}

/**
 * Check if a request method is idempotent
 */
export function isIdempotentMethod(method?: string): boolean {
  if (!method) return false;
  const idempotentMethods = ["GET", "HEAD", "OPTIONS", "PUT", "DELETE"];
  return idempotentMethods.includes(method.toUpperCase());
}

/**
 * Determine if a request should be retried based on error and config
 */
export function shouldRetryRequest(
  error: AxiosError,
  config: RetryConfig,
  attemptNumber: number,
): boolean {
  // Don't retry if max retries exceeded
  if (attemptNumber > config.maxRetries) {
    return false;
  }

  // Check custom retry function first
  if (config.shouldRetry) {
    return config.shouldRetry(error, attemptNumber);
  }

  // Get request method
  const method = error.config?.method?.toUpperCase() || "GET";

  // Only retry idempotent methods by default
  if (!config.retryableMethods.includes(method)) {
    return false;
  }

  // Check for network errors
  if (isNetworkError(error) && config.retryOnNetworkError) {
    return true;
  }

  // Check for timeout errors
  if (isTimeoutError(error) && config.retryOnTimeout) {
    return true;
  }

  // Check for retryable status codes
  const statusCode = error.response?.status;
  if (statusCode && config.retryableStatusCodes.includes(statusCode)) {
    return true;
  }

  return false;
}

/**
 * Sleep for specified milliseconds
 */
export function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// ─────────────────────────────────────────────────────────────────────────────
// Retry Interceptor
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Create retry interceptors for an Axios instance
 */
export function setupRetryInterceptor(
  axiosInstance: AxiosInstance,
  defaultConfig: Partial<RetryConfig> = {},
): void {
  const config: RetryConfig = { ...DEFAULT_RETRY_CONFIG, ...defaultConfig };

  // Request interceptor to initialize retry state
  axiosInstance.interceptors.request.use((requestConfig) => {
    // Skip if retry is disabled for this request
    if (requestConfig.__skipRetry) {
      return requestConfig;
    }

    // Initialize retry state if not already set
    if (!requestConfig.__retryState) {
      requestConfig.__retryState = {
        attemptNumber: 0,
        startTime: Date.now(),
        totalDelay: 0,
      };
    }

    return requestConfig;
  });

  // Response interceptor to handle retries
  axiosInstance.interceptors.response.use(
    // Success - pass through
    (response: AxiosResponse) => response,

    // Error - potentially retry
    async (error: AxiosError): Promise<AxiosResponse> => {
      const requestConfig = error.config;

      // If no config (shouldn't happen) or retry is disabled, reject immediately
      if (!requestConfig || requestConfig.__skipRetry) {
        return Promise.reject(error);
      }

      // Merge configs
      const retryConfig: RetryConfig = {
        ...config,
        ...(requestConfig.__retryConfig || {}),
      };

      // Initialize or increment retry state
      if (!requestConfig.__retryState) {
        requestConfig.__retryState = {
          attemptNumber: 1,
          lastError: error,
          startTime: Date.now(),
          totalDelay: 0,
        };
      } else {
        requestConfig.__retryState.attemptNumber += 1;
        requestConfig.__retryState.lastError = error;
      }

      const { attemptNumber } = requestConfig.__retryState;

      // Check if we should retry
      if (!shouldRetryRequest(error, retryConfig, attemptNumber)) {
        // Call exhausted callback if we've made at least one retry attempt
        if (attemptNumber > 1 && retryConfig.onExhausted) {
          retryConfig.onExhausted(error, attemptNumber);
        }
        return Promise.reject(error);
      }

      // Calculate delay (respecting Retry-After header for 429)
      const delay =
        error.response?.status === 429
          ? calculateRetryAfterDelay(error, retryConfig, attemptNumber)
          : calculateDelay(attemptNumber, retryConfig);

      // Update total delay
      requestConfig.__retryState.totalDelay += delay;

      // Call onRetry callback
      if (retryConfig.onRetry) {
        await retryConfig.onRetry(error, attemptNumber, delay);
      }

      // Wait before retrying
      await sleep(delay);

      // Retry the request
      return axiosInstance.request(requestConfig);
    },
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Retry Wrapper (Alternative Approach)
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Wrap an async function with retry logic
 * Useful for wrapping individual requests without modifying interceptors
 */
export async function withRetry<T>(
  operation: () => Promise<T>,
  config: Partial<RetryConfig> = {},
): Promise<T> {
  const retryConfig: RetryConfig = { ...DEFAULT_RETRY_CONFIG, ...config };
  let lastError: Error | undefined;

  for (let attempt = 1; attempt <= retryConfig.maxRetries + 1; attempt++) {
    try {
      return await operation();
    } catch (error) {
      lastError = error as Error;

      // If this is an Axios error and we shouldn't retry, throw immediately
      if (
        (error as AxiosError).isAxiosError &&
        !shouldRetryRequest(error as AxiosError, retryConfig, attempt)
      ) {
        throw error;
      }

      // If we've exhausted retries, throw
      if (attempt > retryConfig.maxRetries) {
        if (retryConfig.onExhausted && (error as AxiosError).isAxiosError) {
          retryConfig.onExhausted(error as AxiosError, attempt);
        }
        throw error;
      }

      // Calculate and wait for delay
      const delay = calculateDelay(attempt, retryConfig);

      if (retryConfig.onRetry && (error as AxiosError).isAxiosError) {
        await retryConfig.onRetry(error as AxiosError, attempt, delay);
      }

      await sleep(delay);
    }
  }

  // This should never be reached, but TypeScript needs it
  throw lastError || new Error("Retry failed");
}

// ─────────────────────────────────────────────────────────────────────────────
// Circuit Breaker Pattern
// ─────────────────────────────────────────────────────────────────────────────

export type CircuitState = "closed" | "open" | "half-open";

export interface CircuitBreakerConfig {
  /**
   * Number of failures before opening the circuit
   * @default 5
   */
  failureThreshold: number;

  /**
   * Time in ms to wait before attempting to close circuit
   * @default 30000
   */
  resetTimeout: number;

  /**
   * Number of successful requests needed to close circuit from half-open
   * @default 3
   */
  successThreshold: number;

  /**
   * Time window in ms for counting failures
   * @default 60000
   */
  failureWindow: number;

  /**
   * Callback when circuit opens
   */
  onOpen?: (failures: number) => void;

  /**
   * Callback when circuit closes
   */
  onClose?: () => void;

  /**
   * Callback when circuit transitions to half-open
   */
  onHalfOpen?: () => void;
}

export const DEFAULT_CIRCUIT_BREAKER_CONFIG: CircuitBreakerConfig = {
  failureThreshold: 5,
  resetTimeout: 30000,
  successThreshold: 3,
  failureWindow: 60000,
};

export class CircuitBreaker {
  private state: CircuitState = "closed";
  private failures: number[] = [];
  private successes: number = 0;
  private lastFailureTime?: number;
  private config: CircuitBreakerConfig;

  constructor(config: Partial<CircuitBreakerConfig> = {}) {
    this.config = { ...DEFAULT_CIRCUIT_BREAKER_CONFIG, ...config };
  }

  get currentState(): CircuitState {
    return this.state;
  }

  get isOpen(): boolean {
    return this.state === "open";
  }

  get isClosed(): boolean {
    return this.state === "closed";
  }

  get isHalfOpen(): boolean {
    return this.state === "half-open";
  }

  /**
   * Check if circuit allows requests
   */
  canExecute(): boolean {
    this.checkStateTransition();
    return this.state !== "open";
  }

  /**
   * Record a successful request
   */
  recordSuccess(): void {
    if (this.state === "half-open") {
      this.successes += 1;

      if (this.successes >= this.config.successThreshold) {
        this.close();
      }
    } else if (this.state === "closed") {
      // Reset failure count on success
      this.failures = [];
    }
  }

  /**
   * Record a failed request
   */
  recordFailure(): void {
    const now = Date.now();
    this.lastFailureTime = now;

    // Add failure timestamp
    this.failures.push(now);

    // Remove failures outside the window
    const windowStart = now - this.config.failureWindow;
    this.failures = this.failures.filter((t) => t > windowStart);

    // Check if we should open the circuit
    if (
      this.state === "closed" &&
      this.failures.length >= this.config.failureThreshold
    ) {
      this.open();
    } else if (this.state === "half-open") {
      // Any failure in half-open state opens the circuit
      this.open();
    }
  }

  /**
   * Execute a function with circuit breaker protection
   */
  async execute<T>(operation: () => Promise<T>): Promise<T> {
    if (!this.canExecute()) {
      throw new CircuitOpenError(
        `Circuit breaker is open. Reset in ${this.getTimeUntilReset()}ms`,
      );
    }

    try {
      const result = await operation();
      this.recordSuccess();
      return result;
    } catch (error) {
      this.recordFailure();
      throw error;
    }
  }

  /**
   * Force reset the circuit breaker
   */
  reset(): void {
    this.state = "closed";
    this.failures = [];
    this.successes = 0;
    this.lastFailureTime = undefined;
  }

  /**
   * Get time until circuit attempts to reset (in open state)
   */
  getTimeUntilReset(): number {
    if (this.state !== "open" || !this.lastFailureTime) {
      return 0;
    }

    const elapsed = Date.now() - this.lastFailureTime;
    return Math.max(0, this.config.resetTimeout - elapsed);
  }

  private checkStateTransition(): void {
    if (this.state === "open" && this.lastFailureTime) {
      const elapsed = Date.now() - this.lastFailureTime;

      if (elapsed >= this.config.resetTimeout) {
        this.halfOpen();
      }
    }
  }

  private open(): void {
    this.state = "open";
    this.successes = 0;
    this.config.onOpen?.(this.failures.length);
  }

  private close(): void {
    this.state = "closed";
    this.failures = [];
    this.successes = 0;
    this.config.onClose?.();
  }

  private halfOpen(): void {
    this.state = "half-open";
    this.successes = 0;
    this.config.onHalfOpen?.();
  }
}

/**
 * Error thrown when circuit breaker is open
 */
export class CircuitOpenError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "CircuitOpenError";

    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, this.constructor);
    }
  }
}
