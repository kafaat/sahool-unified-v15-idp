/**
 * SAHOOL Rate Limiter Utility
 * أداة تحديد المعدل
 *
 * Provides rate limiting with Redis support and in-memory fallback
 * يوفر تحديد المعدل مع دعم Redis والتراجع إلى الذاكرة
 */

import { Redis } from "ioredis";
import { logger } from "@/lib/logger";

// ═══════════════════════════════════════════════════════════════════════════
// Types
// ═══════════════════════════════════════════════════════════════════════════

export interface RateLimiterOptions {
  /** Time window in milliseconds */
  windowMs: number;
  /** Maximum number of requests allowed in the window */
  maxRequests: number;
  /** Prefix for the rate limit key */
  keyPrefix: string;
}

interface MemoryRecord {
  count: number;
  resetTime: number;
}

// ═══════════════════════════════════════════════════════════════════════════
// In-Memory Store (Fallback for Development)
// ═══════════════════════════════════════════════════════════════════════════

const memoryStore = new Map<string, MemoryRecord>();

/**
 * Clean up expired entries from memory store
 * تنظيف الإدخالات المنتهية من مخزن الذاكرة
 */
function cleanupMemoryStore(): void {
  const now = Date.now();
  for (const [key, record] of memoryStore.entries()) {
    if (now > record.resetTime) {
      memoryStore.delete(key);
    }
  }
}

// Clean up memory store every 60 seconds
setInterval(cleanupMemoryStore, 60000);

/**
 * Check rate limit using in-memory store
 * التحقق من حد المعدل باستخدام مخزن الذاكرة
 */
function checkMemoryRateLimit(
  key: string,
  options: RateLimiterOptions,
): boolean {
  const now = Date.now();
  const record = memoryStore.get(key);

  if (!record || now > record.resetTime) {
    // Create new record
    memoryStore.set(key, {
      count: 1,
      resetTime: now + options.windowMs,
    });
    return false;
  }

  if (record.count >= options.maxRequests) {
    return true; // Rate limited
  }

  // Increment count
  record.count++;
  return false;
}

// ═══════════════════════════════════════════════════════════════════════════
// Redis Store (Production)
// ═══════════════════════════════════════════════════════════════════════════

let redisClient: Redis | null = null;
let redisError = false;

/**
 * Initialize Redis client
 * تهيئة عميل Redis
 */
function getRedisClient(): Redis | null {
  if (redisError) {
    return null; // Skip if Redis previously failed
  }

  if (!redisClient && process.env.REDIS_URL) {
    try {
      redisClient = new Redis(process.env.REDIS_URL, {
        maxRetriesPerRequest: 3,
        retryStrategy: (times: number) => {
          if (times > 3) {
            redisError = true;
            logger.error(
              "[Rate Limiter] Redis connection failed, falling back to memory",
            );
            return null;
          }
          return Math.min(times * 50, 2000);
        },
        lazyConnect: true,
      });

      // Handle connection errors
      redisClient.on("error", (err) => {
        logger.error("[Rate Limiter] Redis error:", err.message);
        redisError = true;
      });

      redisClient.on("connect", () => {
        logger.log("[Rate Limiter] Redis connected successfully");
        redisError = false;
      });
    } catch (error) {
      logger.error("[Rate Limiter] Failed to initialize Redis:", error);
      redisError = true;
      return null;
    }
  }

  return redisClient;
}

/**
 * Check rate limit using Redis
 * التحقق من حد المعدل باستخدام Redis
 */
async function checkRedisRateLimit(
  key: string,
  options: RateLimiterOptions,
): Promise<boolean> {
  const redis = getRedisClient();
  if (!redis) {
    return checkMemoryRateLimit(key, options);
  }

  try {
    // Ensure Redis is connected
    if (redis.status !== "ready" && redis.status !== "connecting") {
      await redis.connect();
    }

    // Increment counter with atomic operation
    const count = await redis.incr(key);

    // Set expiry on first request
    if (count === 1) {
      await redis.pexpire(key, options.windowMs);
    }

    // Check if rate limit exceeded
    return count > options.maxRequests;
  } catch (error) {
    logger.error(
      "[Rate Limiter] Redis operation failed, falling back to memory:",
      error,
    );
    // Fallback to memory on Redis errors
    return checkMemoryRateLimit(key, options);
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Public API
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Check if an identifier is rate limited
 * التحقق مما إذا كان المعرف محدودًا بالمعدل
 *
 * @param identifier - Unique identifier (e.g., IP address, user ID)
 * @param options - Rate limiter configuration
 * @returns Promise<boolean> - true if rate limited, false otherwise
 *
 * @example
 * ```typescript
 * const limited = await isRateLimited('192.168.1.1', {
 *   windowMs: 60000, // 1 minute
 *   maxRequests: 100,
 *   keyPrefix: 'csp-report'
 * });
 *
 * if (limited) {
 *   return NextResponse.json({ error: 'Too many requests' }, { status: 429 });
 * }
 * ```
 */
export async function isRateLimited(
  identifier: string,
  options: RateLimiterOptions,
): Promise<boolean> {
  const key = `${options.keyPrefix}:${identifier}`;

  // Use Redis in production if available, otherwise use in-memory
  if (process.env.REDIS_URL && !redisError) {
    return await checkRedisRateLimit(key, options);
  }

  // Fallback to in-memory for development or if Redis is unavailable
  return checkMemoryRateLimit(key, options);
}

/**
 * Get remaining requests for an identifier
 * الحصول على الطلبات المتبقية للمعرف
 *
 * @param identifier - Unique identifier
 * @param options - Rate limiter configuration
 * @returns Promise<number> - Number of remaining requests (or -1 if unknown)
 */
export async function getRemainingRequests(
  identifier: string,
  options: RateLimiterOptions,
): Promise<number> {
  const key = `${options.keyPrefix}:${identifier}`;

  // Try Redis first
  if (process.env.REDIS_URL && !redisError) {
    const redis = getRedisClient();
    if (redis) {
      try {
        if (redis.status !== "ready" && redis.status !== "connecting") {
          await redis.connect();
        }
        const count = await redis.get(key);
        const currentCount = count ? parseInt(count, 10) : 0;
        return Math.max(0, options.maxRequests - currentCount);
      } catch (error) {
        logger.error(
          "[Rate Limiter] Failed to get remaining requests from Redis:",
          error,
        );
      }
    }
  }

  // Fallback to memory
  const record = memoryStore.get(key);
  if (!record) {
    return options.maxRequests;
  }

  const now = Date.now();
  if (now > record.resetTime) {
    return options.maxRequests;
  }

  return Math.max(0, options.maxRequests - record.count);
}

/**
 * Reset rate limit for an identifier
 * إعادة تعيين حد المعدل للمعرف
 *
 * @param identifier - Unique identifier to reset
 * @param keyPrefix - Prefix for the rate limit key
 */
export async function resetRateLimit(
  identifier: string,
  keyPrefix: string,
): Promise<void> {
  const key = `${keyPrefix}:${identifier}`;

  // Try Redis first
  if (process.env.REDIS_URL && !redisError) {
    const redis = getRedisClient();
    if (redis) {
      try {
        if (redis.status !== "ready" && redis.status !== "connecting") {
          await redis.connect();
        }
        await redis.del(key);
        return;
      } catch (error) {
        logger.error(
          "[Rate Limiter] Failed to reset rate limit in Redis:",
          error,
        );
      }
    }
  }

  // Fallback to memory
  memoryStore.delete(key);
}

/**
 * Close Redis connection (cleanup)
 * إغلاق اتصال Redis (تنظيف)
 */
export async function closeRateLimiter(): Promise<void> {
  if (redisClient) {
    try {
      await redisClient.quit();
      redisClient = null;
    } catch (error) {
      logger.error("[Rate Limiter] Failed to close Redis connection:", error);
    }
  }
  memoryStore.clear();
}
