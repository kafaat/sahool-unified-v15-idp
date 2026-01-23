// ═══════════════════════════════════════════════════════════════════════════════
// SAHOOL API Client - Caching Strategy
// استراتيجية التخزين المؤقت
// ═══════════════════════════════════════════════════════════════════════════════

import { AxiosRequestConfig, AxiosResponse } from "axios";

// ─────────────────────────────────────────────────────────────────────────────
// Types
// ─────────────────────────────────────────────────────────────────────────────

export interface CacheConfig {
  /**
   * Enable/disable caching globally
   * @default true
   */
  enabled: boolean;

  /**
   * Default TTL (Time To Live) in milliseconds
   * @default 300000 (5 minutes)
   */
  defaultTTL: number;

  /**
   * Maximum number of entries in cache
   * @default 100
   */
  maxEntries: number;

  /**
   * HTTP methods that should be cached
   * @default ['GET', 'HEAD']
   */
  cacheableMethods: string[];

  /**
   * Whether to use stale-while-revalidate pattern
   * @default true
   */
  staleWhileRevalidate: boolean;

  /**
   * Grace period for stale data in milliseconds
   * Data can be served stale for this duration while revalidation happens
   * @default 60000 (1 minute)
   */
  staleGracePeriod: number;

  /**
   * Whether to cache error responses (useful for offline mode)
   * @default false
   */
  cacheErrors: boolean;

  /**
   * Custom function to generate cache key
   */
  keyGenerator?: (config: AxiosRequestConfig) => string;

  /**
   * Custom function to determine if response should be cached
   */
  shouldCache?: (response: AxiosResponse) => boolean;

  /**
   * Callback when cache is hit
   */
  onCacheHit?: (key: string, entry: CacheEntry) => void;

  /**
   * Callback when cache is missed
   */
  onCacheMiss?: (key: string) => void;

  /**
   * Callback when cache is updated
   */
  onCacheUpdate?: (key: string, entry: CacheEntry) => void;

  /**
   * Callback when stale data is served
   */
  onStaleServed?: (key: string, entry: CacheEntry) => void;
}

export interface CacheEntry<T = unknown> {
  /**
   * Cached data
   */
  data: T;

  /**
   * Timestamp when entry was created
   */
  createdAt: number;

  /**
   * Timestamp when entry expires (TTL)
   */
  expiresAt: number;

  /**
   * Timestamp when stale grace period ends
   */
  staleUntil: number;

  /**
   * HTTP status code of original response
   */
  status: number;

  /**
   * HTTP status text of original response
   */
  statusText: string;

  /**
   * Response headers (selected)
   */
  headers: Record<string, string>;

  /**
   * Whether a revalidation is currently in progress
   */
  revalidating?: boolean;

  /**
   * Number of times this entry has been accessed
   */
  hitCount: number;

  /**
   * ETag for conditional requests
   */
  etag?: string;

  /**
   * Last-Modified header for conditional requests
   */
  lastModified?: string;
}

export interface CacheStats {
  /**
   * Total number of cache hits
   */
  hits: number;

  /**
   * Total number of cache misses
   */
  misses: number;

  /**
   * Total number of stale-while-revalidate serves
   */
  staleHits: number;

  /**
   * Current number of entries in cache
   */
  size: number;

  /**
   * Cache hit ratio (hits / (hits + misses))
   */
  hitRatio: number;

  /**
   * Memory usage estimation in bytes
   */
  estimatedMemory: number;
}

export type CachePolicy = "cache-first" | "network-first" | "cache-only" | "network-only" | "stale-while-revalidate";

// Extend AxiosRequestConfig to include cache options
declare module "axios" {
  interface AxiosRequestConfig {
    cache?: boolean | {
      enabled?: boolean;
      ttl?: number;
      policy?: CachePolicy;
      key?: string;
      forceRefresh?: boolean;
    };
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Default Configuration
// ─────────────────────────────────────────────────────────────────────────────

export const DEFAULT_CACHE_CONFIG: CacheConfig = {
  enabled: true,
  defaultTTL: 5 * 60 * 1000, // 5 minutes
  maxEntries: 100,
  cacheableMethods: ["GET", "HEAD"],
  staleWhileRevalidate: true,
  staleGracePeriod: 60 * 1000, // 1 minute
  cacheErrors: false,
};

// ─────────────────────────────────────────────────────────────────────────────
// Cache Key Generation
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Generate a cache key from request config
 */
export function generateCacheKey(config: AxiosRequestConfig): string {
  const method = config.method?.toUpperCase() || "GET";
  const url = config.url || "";
  const params = config.params ? JSON.stringify(sortObject(config.params)) : "";
  const headers = config.headers
    ? JSON.stringify(
        sortObject({
          Authorization: config.headers.Authorization,
          "Accept-Language": config.headers["Accept-Language"],
        }),
      )
    : "";

  // Create a deterministic key
  return `${method}:${url}:${params}:${headers}`;
}

/**
 * Sort object keys for consistent cache keys
 */
function sortObject(obj: Record<string, unknown>): Record<string, unknown> {
  const sorted: Record<string, unknown> = {};
  const keys = Object.keys(obj).sort();

  for (const key of keys) {
    const value = obj[key];
    if (value !== undefined && value !== null) {
      sorted[key] =
        typeof value === "object" && !Array.isArray(value)
          ? sortObject(value as Record<string, unknown>)
          : value;
    }
  }

  return sorted;
}

// ─────────────────────────────────────────────────────────────────────────────
// In-Memory Cache Implementation
// ─────────────────────────────────────────────────────────────────────────────

export class MemoryCache {
  private cache: Map<string, CacheEntry> = new Map();
  private config: CacheConfig;
  private stats: CacheStats = {
    hits: 0,
    misses: 0,
    staleHits: 0,
    size: 0,
    hitRatio: 0,
    estimatedMemory: 0,
  };

  constructor(config: Partial<CacheConfig> = {}) {
    this.config = { ...DEFAULT_CACHE_CONFIG, ...config };
  }

  /**
   * Get an entry from cache
   */
  get<T>(key: string): CacheEntry<T> | null {
    const entry = this.cache.get(key) as CacheEntry<T> | undefined;

    if (!entry) {
      this.stats.misses += 1;
      this.updateHitRatio();
      this.config.onCacheMiss?.(key);
      return null;
    }

    const now = Date.now();

    // Check if entry has completely expired (beyond stale grace period)
    if (now > entry.staleUntil) {
      this.delete(key);
      this.stats.misses += 1;
      this.updateHitRatio();
      this.config.onCacheMiss?.(key);
      return null;
    }

    // Check if entry is stale but within grace period
    if (now > entry.expiresAt) {
      entry.hitCount += 1;
      this.stats.staleHits += 1;
      this.stats.hits += 1;
      this.updateHitRatio();
      this.config.onStaleServed?.(key, entry);
      return entry;
    }

    // Entry is fresh
    entry.hitCount += 1;
    this.stats.hits += 1;
    this.updateHitRatio();
    this.config.onCacheHit?.(key, entry);
    return entry;
  }

  /**
   * Set an entry in cache
   */
  set<T>(
    key: string,
    response: AxiosResponse<T>,
    ttl: number = this.config.defaultTTL,
  ): CacheEntry<T> {
    // Enforce max entries limit (LRU eviction)
    if (this.cache.size >= this.config.maxEntries) {
      this.evictLRU();
    }

    const now = Date.now();
    const entry: CacheEntry<T> = {
      data: response.data,
      createdAt: now,
      expiresAt: now + ttl,
      staleUntil: now + ttl + this.config.staleGracePeriod,
      status: response.status,
      statusText: response.statusText,
      headers: this.extractCacheHeaders(response.headers),
      hitCount: 0,
      etag: response.headers["etag"],
      lastModified: response.headers["last-modified"],
    };

    this.cache.set(key, entry);
    this.stats.size = this.cache.size;
    this.updateMemoryEstimate();
    this.config.onCacheUpdate?.(key, entry);

    return entry;
  }

  /**
   * Delete an entry from cache
   */
  delete(key: string): boolean {
    const deleted = this.cache.delete(key);
    this.stats.size = this.cache.size;
    this.updateMemoryEstimate();
    return deleted;
  }

  /**
   * Check if cache has an entry (fresh or stale)
   */
  has(key: string): boolean {
    const entry = this.cache.get(key);
    if (!entry) return false;

    // Check if beyond stale grace period
    if (Date.now() > entry.staleUntil) {
      this.delete(key);
      return false;
    }

    return true;
  }

  /**
   * Check if entry is fresh (not stale)
   */
  isFresh(key: string): boolean {
    const entry = this.cache.get(key);
    if (!entry) return false;
    return Date.now() <= entry.expiresAt;
  }

  /**
   * Check if entry is stale (but within grace period)
   */
  isStale(key: string): boolean {
    const entry = this.cache.get(key);
    if (!entry) return false;
    const now = Date.now();
    return now > entry.expiresAt && now <= entry.staleUntil;
  }

  /**
   * Mark entry as revalidating
   */
  markRevalidating(key: string): void {
    const entry = this.cache.get(key);
    if (entry) {
      entry.revalidating = true;
    }
  }

  /**
   * Clear revalidating flag
   */
  clearRevalidating(key: string): void {
    const entry = this.cache.get(key);
    if (entry) {
      entry.revalidating = false;
    }
  }

  /**
   * Check if entry is currently revalidating
   */
  isRevalidating(key: string): boolean {
    const entry = this.cache.get(key);
    return entry?.revalidating ?? false;
  }

  /**
   * Clear all cache entries
   */
  clear(): void {
    this.cache.clear();
    this.stats = {
      hits: 0,
      misses: 0,
      staleHits: 0,
      size: 0,
      hitRatio: 0,
      estimatedMemory: 0,
    };
  }

  /**
   * Get cache statistics
   */
  getStats(): CacheStats {
    return { ...this.stats };
  }

  /**
   * Get all cache keys
   */
  keys(): string[] {
    return Array.from(this.cache.keys());
  }

  /**
   * Invalidate entries matching a pattern
   */
  invalidatePattern(pattern: RegExp): number {
    let count = 0;
    for (const key of this.cache.keys()) {
      if (pattern.test(key)) {
        this.delete(key);
        count += 1;
      }
    }
    return count;
  }

  /**
   * Invalidate entries by URL prefix
   */
  invalidateByUrl(urlPrefix: string): number {
    return this.invalidatePattern(new RegExp(`^[A-Z]+:${urlPrefix}`));
  }

  /**
   * Prune expired entries
   */
  prune(): number {
    const now = Date.now();
    let pruned = 0;

    for (const [key, entry] of this.cache.entries()) {
      if (now > entry.staleUntil) {
        this.delete(key);
        pruned += 1;
      }
    }

    return pruned;
  }

  /**
   * Export cache to JSON (for persistence)
   */
  export(): Record<string, CacheEntry> {
    const exported: Record<string, CacheEntry> = {};
    const now = Date.now();

    for (const [key, entry] of this.cache.entries()) {
      // Only export non-expired entries
      if (now <= entry.staleUntil) {
        exported[key] = entry;
      }
    }

    return exported;
  }

  /**
   * Import cache from JSON (for persistence)
   */
  import(data: Record<string, CacheEntry>): number {
    const now = Date.now();
    let imported = 0;

    for (const [key, entry] of Object.entries(data)) {
      // Only import non-expired entries
      if (now <= entry.staleUntil) {
        this.cache.set(key, entry);
        imported += 1;
      }
    }

    this.stats.size = this.cache.size;
    this.updateMemoryEstimate();
    return imported;
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Private Methods
  // ─────────────────────────────────────────────────────────────────────────

  private extractCacheHeaders(
    headers: Record<string, unknown>,
  ): Record<string, string> {
    const cacheHeaders: Record<string, string> = {};
    const headersToExtract = [
      "cache-control",
      "etag",
      "last-modified",
      "expires",
      "age",
      "vary",
    ];

    for (const header of headersToExtract) {
      if (headers[header]) {
        cacheHeaders[header] = String(headers[header]);
      }
    }

    return cacheHeaders;
  }

  private updateHitRatio(): void {
    const total = this.stats.hits + this.stats.misses;
    this.stats.hitRatio = total > 0 ? this.stats.hits / total : 0;
  }

  private updateMemoryEstimate(): void {
    // Rough estimation: 1KB per entry average
    this.stats.estimatedMemory = this.cache.size * 1024;
  }

  private evictLRU(): void {
    // Find entry with lowest hit count and oldest creation time
    let oldestKey: string | null = null;
    let lowestScore = Infinity;

    for (const [key, entry] of this.cache.entries()) {
      // Score = hitCount * 1000 + (now - createdAt)
      // Lower score = better candidate for eviction
      const age = Date.now() - entry.createdAt;
      const score = entry.hitCount * 1000 - age / 1000;

      if (score < lowestScore) {
        lowestScore = score;
        oldestKey = key;
      }
    }

    if (oldestKey) {
      this.delete(oldestKey);
    }
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Cache Interceptor Helper
// ─────────────────────────────────────────────────────────────────────────────

export interface CacheableRequest {
  cache: MemoryCache;
  config: CacheConfig;
}

/**
 * Determine if a request should be cached
 */
export function shouldCacheRequest(
  requestConfig: AxiosRequestConfig,
  cacheConfig: CacheConfig,
): boolean {
  // Check if caching is globally disabled
  if (!cacheConfig.enabled) {
    return false;
  }

  // Check request-level cache config
  const reqCache = requestConfig.cache;
  if (reqCache === false) {
    return false;
  }

  if (typeof reqCache === "object" && reqCache.enabled === false) {
    return false;
  }

  // Check if method is cacheable
  const method = requestConfig.method?.toUpperCase() || "GET";
  if (!cacheConfig.cacheableMethods.includes(method)) {
    return false;
  }

  return true;
}

/**
 * Get TTL for a request
 */
export function getRequestTTL(
  requestConfig: AxiosRequestConfig,
  cacheConfig: CacheConfig,
): number {
  const reqCache = requestConfig.cache;

  if (typeof reqCache === "object" && reqCache.ttl !== undefined) {
    return reqCache.ttl;
  }

  return cacheConfig.defaultTTL;
}

/**
 * Get cache policy for a request
 */
export function getCachePolicy(
  requestConfig: AxiosRequestConfig,
  cacheConfig: CacheConfig,
): CachePolicy {
  const reqCache = requestConfig.cache;

  if (typeof reqCache === "object" && reqCache.policy) {
    return reqCache.policy;
  }

  return cacheConfig.staleWhileRevalidate
    ? "stale-while-revalidate"
    : "cache-first";
}

/**
 * Check if request should force refresh
 */
export function shouldForceRefresh(requestConfig: AxiosRequestConfig): boolean {
  const reqCache = requestConfig.cache;

  if (typeof reqCache === "object" && reqCache.forceRefresh) {
    return true;
  }

  return false;
}

/**
 * Get cache key for a request
 */
export function getCacheKey(
  requestConfig: AxiosRequestConfig,
  cacheConfig: CacheConfig,
): string {
  // Check for custom key in request config
  const reqCache = requestConfig.cache;
  if (typeof reqCache === "object" && reqCache.key) {
    return reqCache.key;
  }

  // Check for custom key generator
  if (cacheConfig.keyGenerator) {
    return cacheConfig.keyGenerator(requestConfig);
  }

  // Use default key generation
  return generateCacheKey(requestConfig);
}

// ─────────────────────────────────────────────────────────────────────────────
// Predefined TTL Constants
// ─────────────────────────────────────────────────────────────────────────────

export const CacheTTL = {
  /** 30 seconds - for rapidly changing data */
  VERY_SHORT: 30 * 1000,

  /** 1 minute */
  SHORT: 60 * 1000,

  /** 5 minutes - default */
  MEDIUM: 5 * 60 * 1000,

  /** 15 minutes */
  LONG: 15 * 60 * 1000,

  /** 1 hour */
  VERY_LONG: 60 * 60 * 1000,

  /** 24 hours - for static data */
  DAY: 24 * 60 * 60 * 1000,

  /** No caching */
  NONE: 0,
} as const;

// ─────────────────────────────────────────────────────────────────────────────
// Cache Factory
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Create a cache instance with common configurations
 */
export function createCache(
  preset: "aggressive" | "conservative" | "offline" | "default" = "default",
): MemoryCache {
  const presets: Record<string, Partial<CacheConfig>> = {
    default: DEFAULT_CACHE_CONFIG,

    aggressive: {
      enabled: true,
      defaultTTL: CacheTTL.LONG,
      maxEntries: 200,
      staleWhileRevalidate: true,
      staleGracePeriod: CacheTTL.MEDIUM,
    },

    conservative: {
      enabled: true,
      defaultTTL: CacheTTL.SHORT,
      maxEntries: 50,
      staleWhileRevalidate: false,
      staleGracePeriod: 0,
    },

    offline: {
      enabled: true,
      defaultTTL: CacheTTL.DAY,
      maxEntries: 500,
      staleWhileRevalidate: true,
      staleGracePeriod: CacheTTL.DAY,
      cacheErrors: true,
    },
  };

  return new MemoryCache(presets[preset]);
}
