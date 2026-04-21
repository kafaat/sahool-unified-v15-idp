/**
 * Cache Service - Redis Caching Layer
 *
 * Provides typed caching with:
 * - Automatic key prefixing
 * - TTL management
 * - Cache invalidation patterns
 * - Tenant-aware caching
 */

import { Injectable, Inject, Logger } from "@nestjs/common";
import { CACHE_MANAGER } from "@nestjs/cache-manager";
import { Cache } from "cache-manager";

// Cache TTL constants (in seconds)
export const CACHE_TTL = {
  SHORT: 60, // 1 minute
  MEDIUM: 300, // 5 minutes
  LONG: 3600, // 1 hour
  VERY_LONG: 86400, // 1 day
} as const;

// Cache key patterns
export const CACHE_KEYS = {
  /**
   * Tenant-scoped field cache key. Parameter order mirrors the
   * output format (``field:${tenantId}:${id}``) so that accidental
   * argument swaps are visually obvious at call sites (PR #1729
   * review, comment on pullrequestreview-4150593669). Also matches
   * ``SYNC_STATUS(deviceId, tenantId)``'s left-to-right-as-in-key
   * convention. Without the tenant component, two tenants holding
   * fields with the same ``id`` would fight for one cache slot,
   * enabling cross-tenant hits.
   */
  FIELD: (tenantId: string, id: string) => `field:${tenantId}:${id}`,
  FIELD_STATS: (tenantId: string) => `field-stats:${tenantId}`,
  NDVI: (fieldId: string) => `ndvi:${fieldId}`,
  NDVI_SUMMARY: (tenantId: string) => `ndvi-summary:${tenantId}`,
  TASK_LIST: (fieldId: string) => `tasks:${fieldId}`,
  SYNC_STATUS: (deviceId: string, tenantId: string) =>
    `sync:${deviceId}:${tenantId}`,
} as const;

@Injectable()
export class CacheService {
  private readonly logger = new Logger(CacheService.name);

  constructor(@Inject(CACHE_MANAGER) private cacheManager: Cache) {}

  /**
   * Get cached value with type safety
   */
  async get<T>(key: string): Promise<T | null> {
    try {
      const value = await this.cacheManager.get<T>(key);
      if (value) {
        this.logger.debug(`Cache HIT: ${key}`);
      } else {
        this.logger.debug(`Cache MISS: ${key}`);
      }
      return value ?? null;
    } catch (error) {
      // Log at debug level for expected offline errors (Redis reconnecting);
      // log at warn for unexpected issues to avoid noise in startup logs.
      const msg = error instanceof Error ? error.message : String(error);
      if (msg.includes("offline") || msg.includes("closed")) {
        this.logger.debug(`Cache GET skipped (Redis offline): ${key}`);
      } else {
        this.logger.warn(`Cache GET error for ${key}: ${msg}`);
      }
      return null;
    }
  }

  /**
   * Set cached value with TTL
   */
  async set<T>(key: string, value: T, ttl: number = CACHE_TTL.MEDIUM): Promise<void> {
    try {
      await this.cacheManager.set(key, value, ttl * 1000); // Convert to ms
      this.logger.debug(`Cache SET: ${key} (TTL: ${ttl}s)`);
    } catch (error) {
      const msg = error instanceof Error ? error.message : String(error);
      if (msg.includes("offline") || msg.includes("closed")) {
        this.logger.debug(`Cache SET skipped (Redis offline): ${key}`);
      } else {
        this.logger.warn(`Cache SET error for ${key}: ${msg}`);
      }
    }
  }

  /**
   * Delete cached value
   */
  async del(key: string): Promise<void> {
    try {
      await this.cacheManager.del(key);
      this.logger.debug(`Cache DEL: ${key}`);
    } catch (error) {
      const msg = error instanceof Error ? error.message : String(error);
      if (msg.includes("offline") || msg.includes("closed")) {
        this.logger.debug(`Cache DEL skipped (Redis offline): ${key}`);
      } else {
        this.logger.warn(`Cache DEL error for ${key}: ${msg}`);
      }
    }
  }

  /**
   * Delete multiple keys by pattern
   */
  async delByPattern(pattern: string): Promise<void> {
    try {
      // Note: This requires Redis client access for KEYS/SCAN
      // For now, we'll use store-specific methods if available
      const store = this.cacheManager.store as any;
      if (store.keys) {
        const keys = await store.keys(pattern);
        if (keys.length > 0) {
          await Promise.all(keys.map((key: string) => this.del(key)));
          this.logger.debug(`Cache DEL pattern: ${pattern} (${keys.length} keys)`);
        }
      }
    } catch (error) {
      this.logger.error(`Cache DEL pattern error for ${pattern}:`, error);
    }
  }

  /**
   * Get or set pattern - fetch from cache or execute function
   */
  async getOrSet<T>(
    key: string,
    fn: () => Promise<T>,
    ttl: number = CACHE_TTL.MEDIUM,
  ): Promise<T> {
    const cached = await this.get<T>(key);
    if (cached !== null) {
      return cached;
    }

    const value = await fn();
    await this.set(key, value, ttl);
    return value;
  }

  /**
   * Invalidate field-related caches
   */
  async invalidateField(fieldId: string, tenantId: string): Promise<void> {
    await Promise.all([
      this.del(CACHE_KEYS.FIELD(tenantId, fieldId)),
      this.del(CACHE_KEYS.NDVI(fieldId)),
      this.del(CACHE_KEYS.TASK_LIST(fieldId)),
      this.delByPattern(`fields:${tenantId}:*`),
      this.del(CACHE_KEYS.FIELD_STATS(tenantId)),
    ]);
    this.logger.debug(`Invalidated caches for field: ${fieldId}`);
  }

  /**
   * Invalidate tenant-related caches
   */
  async invalidateTenant(tenantId: string): Promise<void> {
    await Promise.all([
      this.delByPattern(`fields:${tenantId}:*`),
      this.del(CACHE_KEYS.FIELD_STATS(tenantId)),
      this.del(CACHE_KEYS.NDVI_SUMMARY(tenantId)),
    ]);
    this.logger.debug(`Invalidated caches for tenant: ${tenantId}`);
  }

  /**
   * Check if cache is available.
   * Uses a 2-second timeout so that a pending Redis connection (offline-queue mode)
   * does not hang the /readyz probe indefinitely.
   */
  async isHealthy(): Promise<boolean> {
    let timeoutId: ReturnType<typeof setTimeout> | undefined;
    try {
      const checkFn = async () => {
        const testKey = "health-check";
        await this.set(testKey, "ok", CACHE_TTL.SHORT);
        const value = await this.get<string>(testKey);
        await this.del(testKey);
        return value === "ok";
      };
      const timeoutFn = new Promise<never>((_, reject) => {
        timeoutId = setTimeout(
          () => reject(new Error("Cache health-check timeout")),
          2000,
        );
      });
      const result = await Promise.race([checkFn(), timeoutFn]);
      clearTimeout(timeoutId);
      return result;
    } catch {
      clearTimeout(timeoutId);
      return false;
    }
  }
}
