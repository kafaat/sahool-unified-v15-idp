/**
 * Cache Service - Redis Caching for Marketplace Service
 *
 * Features:
 * - Product caching
 * - Wallet balance caching
 * - Order caching
 * - Cache invalidation patterns
 */

import { Injectable, Inject, Logger } from "@nestjs/common";
import { CACHE_MANAGER } from "@nestjs/cache-manager";
import { Cache } from "cache-manager";

// Cache TTL constants (in seconds)
export const CACHE_TTL = {
  SHORT: 60, // 1 minute
  MEDIUM: 300, // 5 minutes
  LONG: 3600, // 1 hour
  PRODUCT_LIST: 120, // 2 minutes
  WALLET: 60, // 1 minute (sensitive data)
  STATS: 300, // 5 minutes
} as const;

// Cache key patterns
export const CACHE_KEYS = {
  // Product keys
  PRODUCT: (id: string) => `product:${id}`,
  PRODUCT_LIST: (category?: string, page?: number) =>
    `products:${category || "all"}:${page || 1}`,
  PRODUCT_FEATURED: () => `products:featured`,
  PRODUCT_SELLER: (sellerId: string) => `products:seller:${sellerId}`,

  // Wallet keys
  WALLET: (userId: string) => `wallet:${userId}`,
  WALLET_TRANSACTIONS: (walletId: string) => `wallet:${walletId}:txns`,
  WALLET_LIMITS: (walletId: string) => `wallet:${walletId}:limits`,
  WALLET_DASHBOARD: (walletId: string) => `wallet:${walletId}:dashboard`,

  // Order keys
  ORDER: (id: string) => `order:${id}`,
  ORDER_USER: (userId: string) => `orders:user:${userId}`,

  // Stats keys
  MARKET_STATS: () => `market:stats`,
  FINANCE_STATS: () => `finance:stats`,

  // Profile keys
  SELLER_PROFILE: (userId: string) => `seller:${userId}`,
  BUYER_PROFILE: (userId: string) => `buyer:${userId}`,
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
      this.logger.error(`Cache GET error for ${key}:`, error);
      return null;
    }
  }

  /**
   * Set cached value with TTL
   */
  async set<T>(key: string, value: T, ttl: number = CACHE_TTL.MEDIUM): Promise<void> {
    try {
      await this.cacheManager.set(key, value, ttl * 1000);
      this.logger.debug(`Cache SET: ${key} (TTL: ${ttl}s)`);
    } catch (error) {
      this.logger.error(`Cache SET error for ${key}:`, error);
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
      this.logger.error(`Cache DEL error for ${key}:`, error);
    }
  }

  /**
   * Delete multiple keys by pattern (if supported by store)
   */
  async delByPattern(pattern: string): Promise<void> {
    try {
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
   * Invalidate product-related caches
   */
  async invalidateProduct(productId: string, sellerId?: string): Promise<void> {
    const keys = [
      CACHE_KEYS.PRODUCT(productId),
      CACHE_KEYS.PRODUCT_FEATURED(),
      CACHE_KEYS.MARKET_STATS(),
    ];

    if (sellerId) {
      keys.push(CACHE_KEYS.PRODUCT_SELLER(sellerId));
    }

    await Promise.all(keys.map((key) => this.del(key)));
    await this.delByPattern("products:*");

    this.logger.debug(`Invalidated caches for product: ${productId}`);
  }

  /**
   * Invalidate wallet-related caches
   */
  async invalidateWallet(walletId: string, userId?: string): Promise<void> {
    const keys = [
      CACHE_KEYS.WALLET_TRANSACTIONS(walletId),
      CACHE_KEYS.WALLET_LIMITS(walletId),
      CACHE_KEYS.WALLET_DASHBOARD(walletId),
      CACHE_KEYS.FINANCE_STATS(),
    ];

    if (userId) {
      keys.push(CACHE_KEYS.WALLET(userId));
    }

    await Promise.all(keys.map((key) => this.del(key)));

    this.logger.debug(`Invalidated caches for wallet: ${walletId}`);
  }

  /**
   * Invalidate order-related caches
   */
  async invalidateOrder(orderId: string, buyerId?: string): Promise<void> {
    const keys = [CACHE_KEYS.ORDER(orderId), CACHE_KEYS.MARKET_STATS()];

    if (buyerId) {
      keys.push(CACHE_KEYS.ORDER_USER(buyerId));
    }

    await Promise.all(keys.map((key) => this.del(key)));

    this.logger.debug(`Invalidated caches for order: ${orderId}`);
  }

  /**
   * Check if cache is available
   */
  async isHealthy(): Promise<boolean> {
    try {
      const testKey = "health-check";
      await this.set(testKey, "ok", CACHE_TTL.SHORT);
      const value = await this.get<string>(testKey);
      await this.del(testKey);
      return value === "ok";
    } catch {
      return false;
    }
  }
}
