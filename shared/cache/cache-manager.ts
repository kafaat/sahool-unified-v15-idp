/**
 * Advanced Cache Manager for SAHOOL Platform
 * ==========================================
 *
 * Comprehensive caching utilities with:
 * - Cache-aside pattern with stampede protection
 * - Write-through pattern for critical data
 * - Cache warming strategies
 * - Hit/miss metrics tracking
 * - Invalidation patterns with SCAN
 * - TTL management
 * - Distributed locking
 *
 * @author SAHOOL Platform Team
 * @version 2.0.0
 */

import Redis from 'ioredis';
import { Logger } from '@nestjs/common';

// =============================================================================
// Types & Interfaces
// =============================================================================

export interface CacheConfig {
  /** Cache key prefix */
  keyPrefix: string;
  /** Default TTL in seconds */
  defaultTTL: number;
  /** Enable stampede protection */
  enableStampedeProtection?: boolean;
  /** Enable metrics tracking */
  enableMetrics?: boolean;
}

export interface CacheMetrics {
  hits: number;
  misses: number;
  sets: number;
  deletes: number;
  errors: number;
  stampedePreventions: number;
  hitRate: number;
}

export interface CacheEntry<T> {
  data: T;
  cachedAt: number;
  version: number;
}

export interface CacheWarmingOptions {
  /** Keys to warm */
  keys: string[];
  /** Data fetcher function */
  fetcher: (key: string) => Promise<any>;
  /** TTL for warmed data */
  ttl?: number;
}

// =============================================================================
// Cache Manager Class
// =============================================================================

export class CacheManager {
  private readonly logger = new Logger(CacheManager.name);
  private readonly config: Required<CacheConfig>;
  private metrics: CacheMetrics;
  private readonly CACHE_VERSION = 1;

  constructor(
    private readonly redis: Redis,
    config: CacheConfig,
  ) {
    this.config = {
      enableStampedeProtection: true,
      enableMetrics: true,
      ...config,
    };

    this.metrics = {
      hits: 0,
      misses: 0,
      sets: 0,
      deletes: 0,
      errors: 0,
      stampedePreventions: 0,
      hitRate: 0,
    };
  }

  // ===========================================================================
  // Cache-Aside Pattern (Lazy Loading)
  // ===========================================================================

  /**
   * Get value from cache, fetch from source if missing (cache-aside pattern)
   *
   * @param key - Cache key
   * @param fetcher - Function to fetch data on cache miss
   * @param ttl - Time to live in seconds
   * @returns Cached or fetched data
   */
  async getOrFetch<T>(
    key: string,
    fetcher: () => Promise<T>,
    ttl?: number,
  ): Promise<T> {
    const fullKey = this.makeKey(key);

    // Try to get from cache
    const cached = await this.get<T>(key);
    if (cached !== null) {
      this.recordHit();
      return cached;
    }

    this.recordMiss();

    // Use stampede protection if enabled
    if (this.config.enableStampedeProtection) {
      return this.getOrFetchWithLock(key, fetcher, ttl);
    }

    // Fetch and cache
    const data = await fetcher();
    await this.set(key, data, ttl);
    return data;
  }

  /**
   * Get or fetch with distributed lock to prevent cache stampede
   */
  private async getOrFetchWithLock<T>(
    key: string,
    fetcher: () => Promise<T>,
    ttl?: number,
  ): Promise<T> {
    const lockKey = `lock:${key}`;
    const lockValue = `${Date.now()}-${Math.random()}`;
    const lockTTL = 10; // 10 seconds lock timeout

    try {
      // Try to acquire lock
      const acquired = await this.redis.set(
        this.makeKey(lockKey),
        lockValue,
        'EX',
        lockTTL,
        'NX',
      );

      if (acquired === 'OK') {
        // We got the lock, fetch data
        this.recordStampedePrevention();

        try {
          // Double-check cache after acquiring lock
          const cached = await this.get<T>(key);
          if (cached !== null) {
            return cached;
          }

          // Fetch and cache
          const data = await fetcher();
          await this.set(key, data, ttl);
          return data;
        } finally {
          // Release lock
          await this.releaseLock(lockKey, lockValue);
        }
      } else {
        // Another process is fetching, wait and retry
        await this.sleep(100);

        // Try to get from cache again
        const cached = await this.get<T>(key);
        if (cached !== null) {
          return cached;
        }

        // If still not in cache, fetch ourselves (lock might have expired)
        const data = await fetcher();
        await this.set(key, data, ttl);
        return data;
      }
    } catch (error) {
      this.logger.error(`Error in getOrFetchWithLock: ${error.message}`);
      // Fallback to direct fetch
      return fetcher();
    }
  }

  // ===========================================================================
  // Write-Through Pattern
  // ===========================================================================

  /**
   * Write data to both cache and source (write-through pattern)
   *
   * @param key - Cache key
   * @param data - Data to write
   * @param persister - Function to persist data to source
   * @param ttl - Time to live in seconds
   */
  async writeThrough<T>(
    key: string,
    data: T,
    persister: (data: T) => Promise<void>,
    ttl?: number,
  ): Promise<void> {
    try {
      // Write to source first
      await persister(data);

      // Then update cache
      await this.set(key, data, ttl);

      this.logger.debug(`Write-through completed for key: ${key}`);
    } catch (error) {
      this.logger.error(`Write-through failed for key ${key}: ${error.message}`);
      throw error;
    }
  }

  // ===========================================================================
  // Basic Operations
  // ===========================================================================

  /**
   * Get value from cache
   */
  async get<T>(key: string): Promise<T | null> {
    try {
      const fullKey = this.makeKey(key);
      const value = await this.redis.get(fullKey);

      if (!value) {
        return null;
      }

      const entry: CacheEntry<T> = JSON.parse(value);

      // Check version compatibility
      if (entry.version !== this.CACHE_VERSION) {
        this.logger.warn(`Cache version mismatch for ${key}, invalidating`);
        await this.delete(key);
        return null;
      }

      return entry.data;
    } catch (error) {
      this.recordError();
      this.logger.error(`Cache get error for ${key}: ${error.message}`);
      return null;
    }
  }

  /**
   * Set value in cache
   */
  async set<T>(key: string, value: T, ttl?: number): Promise<void> {
    try {
      const fullKey = this.makeKey(key);
      const cacheTTL = ttl || this.config.defaultTTL;

      const entry: CacheEntry<T> = {
        data: value,
        cachedAt: Date.now(),
        version: this.CACHE_VERSION,
      };

      await this.redis.setex(fullKey, cacheTTL, JSON.stringify(entry));
      this.recordSet();
    } catch (error) {
      this.recordError();
      this.logger.error(`Cache set error for ${key}: ${error.message}`);
    }
  }

  /**
   * Delete value from cache
   */
  async delete(key: string): Promise<void> {
    try {
      const fullKey = this.makeKey(key);
      await this.redis.del(fullKey);
      this.recordDelete();
    } catch (error) {
      this.recordError();
      this.logger.error(`Cache delete error for ${key}: ${error.message}`);
    }
  }

  /**
   * Check if key exists in cache
   */
  async exists(key: string): Promise<boolean> {
    try {
      const fullKey = this.makeKey(key);
      const exists = await this.redis.exists(fullKey);
      return exists === 1;
    } catch (error) {
      this.recordError();
      this.logger.error(`Cache exists error for ${key}: ${error.message}`);
      return false;
    }
  }

  /**
   * Get remaining TTL for a key
   */
  async ttl(key: string): Promise<number> {
    try {
      const fullKey = this.makeKey(key);
      return await this.redis.ttl(fullKey);
    } catch (error) {
      this.recordError();
      this.logger.error(`Cache TTL error for ${key}: ${error.message}`);
      return -1;
    }
  }

  // ===========================================================================
  // Invalidation Patterns (Using SCAN instead of KEYS)
  // ===========================================================================

  /**
   * Invalidate all keys matching a pattern (using SCAN for safety)
   *
   * @param pattern - Key pattern (e.g., "user:*", "field:123:*")
   * @returns Number of keys deleted
   */
  async invalidatePattern(pattern: string): Promise<number> {
    try {
      const fullPattern = this.makeKey(pattern);
      let cursor = '0';
      let totalDeleted = 0;
      const batchSize = 100;

      do {
        const [newCursor, keys] = await this.redis.scan(
          cursor,
          'MATCH',
          fullPattern,
          'COUNT',
          batchSize,
        );

        cursor = newCursor;

        if (keys.length > 0) {
          const deleted = await this.redis.del(...keys);
          totalDeleted += deleted;
          this.logger.debug(`Deleted ${deleted} keys matching ${pattern}`);
        }
      } while (cursor !== '0');

      this.logger.log(`Invalidated ${totalDeleted} keys matching pattern: ${pattern}`);
      return totalDeleted;
    } catch (error) {
      this.recordError();
      this.logger.error(`Pattern invalidation error for ${pattern}: ${error.message}`);
      return 0;
    }
  }

  /**
   * Clear all cache entries with this prefix
   */
  async clearAll(): Promise<number> {
    return this.invalidatePattern('*');
  }

  // ===========================================================================
  // Cache Warming
  // ===========================================================================

  /**
   * Warm cache with pre-loaded data
   *
   * @param options - Warming options
   */
  async warm(options: CacheWarmingOptions): Promise<void> {
    this.logger.log(`Warming cache for ${options.keys.length} keys...`);

    const results = await Promise.allSettled(
      options.keys.map(async (key) => {
        try {
          const data = await options.fetcher(key);
          await this.set(key, data, options.ttl);
          return { key, success: true };
        } catch (error) {
          this.logger.error(`Failed to warm cache for ${key}: ${error.message}`);
          return { key, success: false, error };
        }
      }),
    );

    const successful = results.filter((r) => r.status === 'fulfilled').length;
    const failed = results.length - successful;

    this.logger.log(`Cache warming completed: ${successful} succeeded, ${failed} failed`);
  }

  /**
   * Warm cache for top accessed items
   */
  async warmTopAccessed<T>(
    getTopKeys: () => Promise<string[]>,
    fetcher: (key: string) => Promise<T>,
    ttl?: number,
  ): Promise<void> {
    const topKeys = await getTopKeys();
    await this.warm({
      keys: topKeys,
      fetcher,
      ttl,
    });
  }

  // ===========================================================================
  // Metrics & Monitoring
  // ===========================================================================

  /**
   * Get cache metrics
   */
  getMetrics(): CacheMetrics {
    const total = this.metrics.hits + this.metrics.misses;
    this.metrics.hitRate = total > 0 ? this.metrics.hits / total : 0;
    return { ...this.metrics };
  }

  /**
   * Reset metrics
   */
  resetMetrics(): void {
    this.metrics = {
      hits: 0,
      misses: 0,
      sets: 0,
      deletes: 0,
      errors: 0,
      stampedePreventions: 0,
      hitRate: 0,
    };
  }

  private recordHit(): void {
    if (this.config.enableMetrics) {
      this.metrics.hits++;
    }
  }

  private recordMiss(): void {
    if (this.config.enableMetrics) {
      this.metrics.misses++;
    }
  }

  private recordSet(): void {
    if (this.config.enableMetrics) {
      this.metrics.sets++;
    }
  }

  private recordDelete(): void {
    if (this.config.enableMetrics) {
      this.metrics.deletes++;
    }
  }

  private recordError(): void {
    if (this.config.enableMetrics) {
      this.metrics.errors++;
    }
  }

  private recordStampedePrevention(): void {
    if (this.config.enableMetrics) {
      this.metrics.stampedePreventions++;
    }
  }

  // ===========================================================================
  // Helper Methods
  // ===========================================================================

  private makeKey(key: string): string {
    return `${this.config.keyPrefix}${key}`;
  }

  private async releaseLock(lockKey: string, lockValue: string): Promise<void> {
    const script = `
      if redis.call("get", KEYS[1]) == ARGV[1] then
        return redis.call("del", KEYS[1])
      else
        return 0
      end
    `;

    try {
      await this.redis.eval(script, 1, this.makeKey(lockKey), lockValue);
    } catch (error) {
      this.logger.error(`Failed to release lock ${lockKey}: ${error.message}`);
    }
  }

  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}

// =============================================================================
// TTL Constants
// =============================================================================

export const CacheTTL = {
  /** Token revocation: 24 hours (matches JWT expiration) */
  TOKEN_REVOCATION: 86400,
  /** User validation: 5 minutes (balance freshness/performance) */
  USER_VALIDATION: 300,
  /** Session data: 1 hour (standard web session) */
  SESSION: 3600,
  /** Rate limit: 1 minute (per-request tracking) */
  RATE_LIMIT: 60,
  /** User revocation: 30 days (long-term invalidation) */
  USER_REVOCATION: 2592000,
  /** Tenant revocation: 30 days */
  TENANT_REVOCATION: 2592000,
  /** Field data: 2 minutes (semi-static data) */
  FIELD_DATA: 120,
  /** NDVI data: 1 minute (real-time updates) */
  NDVI_DATA: 60,
  /** Weather data: 5 minutes (weather API limits) */
  WEATHER_DATA: 300,
  /** Sensor data: 30 seconds (IoT real-time data) */
  SENSOR_DATA: 30,
  /** Forecast data: 1 hour (slow-changing predictions) */
  FORECAST_DATA: 3600,
} as const;

// =============================================================================
// Factory Functions
// =============================================================================

let cacheManagerInstance: CacheManager | null = null;

/**
 * Get or create cache manager singleton
 */
export function getCacheManager(
  redis?: Redis,
  config?: CacheConfig,
): CacheManager {
  if (!cacheManagerInstance && redis && config) {
    cacheManagerInstance = new CacheManager(redis, config);
  }

  if (!cacheManagerInstance) {
    throw new Error('CacheManager not initialized. Call with redis and config first.');
  }

  return cacheManagerInstance;
}

/**
 * Reset cache manager singleton (for testing)
 */
export function resetCacheManager(): void {
  cacheManagerInstance = null;
}
