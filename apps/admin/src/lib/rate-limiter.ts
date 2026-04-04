/**
 * Rate Limiter for Admin Dashboard
 * Prevents brute-force attacks on authentication endpoints
 *
 * معالج الحد من المحاولات لمنع هجمات القوة الغاشمة
 *
 * TODO: This rate limiter uses an in-memory Map, which does NOT persist across
 * server restarts and does NOT share state across multiple Node.js processes or
 * serverless function instances. In production, replace with a Redis-backed
 * implementation (e.g. using REDIS_URL from env) to ensure rate limits are
 * enforced consistently across all instances. See shared/cache/ for Redis
 * Sentinel HA utilities.
 */

interface RateLimitEntry {
  count: number;
  firstAttempt: number;
  lockedUntil?: number;
}

// WARNING: In-memory store — each serverless/edge instance has its own counter.
// In production with multiple replicas, brute-force attacks are distributed across
// instances and effectively bypass the limit. For production, rate limiting should
// be handled at the API Gateway (Kong) or via Redis-backed middleware.
const rateLimitStore = new Map<string, RateLimitEntry>();

if (
  typeof process !== 'undefined' &&
  process.env.NODE_ENV === 'production' &&
  !process.env.RATE_LIMIT_IN_MEMORY_ACKNOWLEDGED
) {
  console.warn(
    '[rate-limiter] Running with in-memory rate limiting in production. ' +
      'This is ineffective in multi-instance deployments. ' +
      'Rely on Kong rate-limiting plugin or set RATE_LIMIT_IN_MEMORY_ACKNOWLEDGED=1 to suppress.'
  );
}

export interface RateLimitConfig {
  maxAttempts: number; // Maximum attempts allowed
  windowMs: number; // Time window in milliseconds
  lockoutDurationMs: number; // Lockout duration after max attempts
}

const DEFAULT_CONFIG: RateLimitConfig = {
  maxAttempts: 5,
  windowMs: 15 * 60 * 1000, // 15 minutes
  lockoutDurationMs: 30 * 60 * 1000, // 30 minutes
};

/**
 * Check if request should be rate limited
 */
export function checkRateLimit(
  identifier: string,
  config: Partial<RateLimitConfig> = {}
): {
  allowed: boolean;
  remaining: number;
  resetTime?: number;
  message?: string;
} {
  const { maxAttempts, windowMs, lockoutDurationMs } = {
    ...DEFAULT_CONFIG,
    ...config,
  };

  const now = Date.now();
  const entry = rateLimitStore.get(identifier);

  // No previous attempts
  if (!entry) {
    rateLimitStore.set(identifier, {
      count: 1,
      firstAttempt: now,
    });

    return {
      allowed: true,
      remaining: maxAttempts - 1,
    };
  }

  // Check if still locked out
  if (entry.lockedUntil && now < entry.lockedUntil) {
    const resetTime = entry.lockedUntil;
    const minutesRemaining = Math.ceil((resetTime - now) / 60000);

    return {
      allowed: false,
      remaining: 0,
      resetTime,
      message: `Too many attempts. Please try again in ${minutesRemaining} minute(s). | محاولات كثيرة جداً. حاول مرة أخرى بعد ${minutesRemaining} دقيقة.`,
    };
  }

  // Reset if outside time window
  if (now - entry.firstAttempt > windowMs) {
    rateLimitStore.set(identifier, {
      count: 1,
      firstAttempt: now,
    });

    return {
      allowed: true,
      remaining: maxAttempts - 1,
    };
  }

  // Increment attempt count
  entry.count++;

  // Check if max attempts exceeded
  if (entry.count > maxAttempts) {
    entry.lockedUntil = now + lockoutDurationMs;
    rateLimitStore.set(identifier, entry);

    const resetTime = entry.lockedUntil;
    const minutesRemaining = Math.ceil(lockoutDurationMs / 60000);

    return {
      allowed: false,
      remaining: 0,
      resetTime,
      message: `Account temporarily locked due to too many failed attempts. Please try again in ${minutesRemaining} minute(s). | تم قفل الحساب مؤقتاً بسبب كثرة المحاولات الفاشلة. حاول مرة أخرى بعد ${minutesRemaining} دقيقة.`,
    };
  }

  // Still within limits
  rateLimitStore.set(identifier, entry);

  return {
    allowed: true,
    remaining: maxAttempts - entry.count,
  };
}

/**
 * Reset rate limit for identifier (use after successful login)
 */
export function resetRateLimit(identifier: string): void {
  rateLimitStore.delete(identifier);
}

/**
 * Clean up old entries (run periodically)
 */
export function cleanupExpiredEntries(): void {
  const now = Date.now();
  const maxAge = DEFAULT_CONFIG.windowMs + DEFAULT_CONFIG.lockoutDurationMs;

  for (const [key, entry] of rateLimitStore.entries()) {
    if (now - entry.firstAttempt > maxAge) {
      rateLimitStore.delete(key);
    }
  }
}

// Clean up every 5 minutes - track handle for testability and cleanup
let cleanupTimer: ReturnType<typeof setInterval> | null = null;
if (typeof setInterval !== 'undefined') {
  cleanupTimer = setInterval(cleanupExpiredEntries, 5 * 60 * 1000);
  // Allow process to exit without waiting for this timer
  if (cleanupTimer && typeof cleanupTimer === 'object' && 'unref' in cleanupTimer) {
    cleanupTimer.unref();
  }
}

/**
 * Stop the periodic cleanup timer (useful for tests)
 */
export function stopCleanupTimer(): void {
  if (cleanupTimer) {
    clearInterval(cleanupTimer);
    cleanupTimer = null;
  }
}
