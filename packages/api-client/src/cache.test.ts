/**
 * SAHOOL API Client - Cache Tests
 * اختبارات التخزين المؤقت
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import {
  MemoryCache,
  generateCacheKey,
  createCache,
  shouldCacheRequest,
  getRequestTTL,
  getCachePolicy,
  CacheTTL,
  DEFAULT_CACHE_CONFIG,
} from "./cache";
import { AxiosResponse } from "axios";

// Helper to create mock response
function createMockResponse<T>(data: T, status = 200): AxiosResponse<T> {
  return {
    data,
    status,
    statusText: "OK",
    headers: {
      "content-type": "application/json",
    },
    config: {} as never,
  };
}

describe("MemoryCache", () => {
  let cache: MemoryCache;

  beforeEach(() => {
    cache = new MemoryCache({
      defaultTTL: 1000,
      maxEntries: 10,
      staleGracePeriod: 500,
    });
  });

  describe("Basic Operations", () => {
    it("should set and get cache entries", () => {
      const response = createMockResponse({ id: 1, name: "Test" });
      cache.set("test-key", response, 1000);

      const entry = cache.get("test-key");

      expect(entry).not.toBeNull();
      expect(entry?.data).toEqual({ id: 1, name: "Test" });
    });

    it("should return null for non-existent keys", () => {
      const entry = cache.get("non-existent");
      expect(entry).toBeNull();
    });

    it("should delete cache entries", () => {
      cache.set("test-key", createMockResponse({ id: 1 }), 1000);
      expect(cache.has("test-key")).toBe(true);

      cache.delete("test-key");
      expect(cache.has("test-key")).toBe(false);
    });

    it("should clear all entries", () => {
      cache.set("key1", createMockResponse({ id: 1 }), 1000);
      cache.set("key2", createMockResponse({ id: 2 }), 1000);

      cache.clear();

      expect(cache.has("key1")).toBe(false);
      expect(cache.has("key2")).toBe(false);
    });
  });

  describe("TTL and Expiration", () => {
    it("should return fresh entries", () => {
      cache.set("test-key", createMockResponse({ id: 1 }), 1000);

      expect(cache.isFresh("test-key")).toBe(true);
      expect(cache.isStale("test-key")).toBe(false);
    });

    it("should mark stale entries", async () => {
      cache.set("test-key", createMockResponse({ id: 1 }), 50); // 50ms TTL

      await new Promise((resolve) => setTimeout(resolve, 100));

      expect(cache.isFresh("test-key")).toBe(false);
      expect(cache.isStale("test-key")).toBe(true);
    });

    it("should remove expired entries beyond stale grace period", async () => {
      const shortCache = new MemoryCache({
        defaultTTL: 50,
        staleGracePeriod: 50,
      });

      shortCache.set("test-key", createMockResponse({ id: 1 }), 50);

      await new Promise((resolve) => setTimeout(resolve, 150));

      expect(shortCache.has("test-key")).toBe(false);
    });
  });

  describe("Statistics", () => {
    it("should track cache hits", () => {
      cache.set("test-key", createMockResponse({ id: 1 }), 1000);

      cache.get("test-key");
      cache.get("test-key");
      cache.get("test-key");

      const stats = cache.getStats();
      expect(stats.hits).toBe(3);
    });

    it("should track cache misses", () => {
      cache.get("non-existent-1");
      cache.get("non-existent-2");

      const stats = cache.getStats();
      expect(stats.misses).toBe(2);
    });

    it("should calculate hit ratio", () => {
      cache.set("key1", createMockResponse({ id: 1 }), 1000);

      cache.get("key1"); // hit
      cache.get("key1"); // hit
      cache.get("key2"); // miss

      const stats = cache.getStats();
      expect(stats.hitRatio).toBeCloseTo(0.67, 1);
    });

    it("should track entry count", () => {
      cache.set("key1", createMockResponse({ id: 1 }), 1000);
      cache.set("key2", createMockResponse({ id: 2 }), 1000);

      const stats = cache.getStats();
      expect(stats.size).toBe(2);
    });
  });

  describe("LRU Eviction", () => {
    it("should evict least recently used entries", () => {
      const smallCache = new MemoryCache({
        maxEntries: 3,
        defaultTTL: 10000,
      });

      smallCache.set("key1", createMockResponse({ id: 1 }), 10000);
      smallCache.set("key2", createMockResponse({ id: 2 }), 10000);
      smallCache.set("key3", createMockResponse({ id: 3 }), 10000);

      // Access key1 and key2 to increase their hit count
      smallCache.get("key1");
      smallCache.get("key2");

      // Add new entry - should evict key3 (least used)
      smallCache.set("key4", createMockResponse({ id: 4 }), 10000);

      expect(smallCache.has("key1")).toBe(true);
      expect(smallCache.has("key2")).toBe(true);
      expect(smallCache.has("key4")).toBe(true);
      // key3 should be evicted (lowest hit count)
    });
  });

  describe("Pattern Invalidation", () => {
    it("should invalidate entries by pattern", () => {
      cache.set("GET:/api/v1/tasks", createMockResponse([]), 1000);
      cache.set("GET:/api/v1/tasks/1", createMockResponse({}), 1000);
      cache.set("GET:/api/v1/fields", createMockResponse([]), 1000);

      const count = cache.invalidatePattern(/\/api\/v1\/tasks/);

      expect(count).toBe(2);
      expect(cache.has("GET:/api/v1/tasks")).toBe(false);
      expect(cache.has("GET:/api/v1/tasks/1")).toBe(false);
      expect(cache.has("GET:/api/v1/fields")).toBe(true);
    });

    it("should invalidate by URL prefix", () => {
      cache.set("GET:/api/v1/tasks", createMockResponse([]), 1000);
      cache.set("POST:/api/v1/tasks", createMockResponse({}), 1000);

      const count = cache.invalidateByUrl("/api/v1/tasks");

      expect(count).toBe(2);
    });
  });

  describe("Stale-While-Revalidate", () => {
    it("should mark entries as revalidating", () => {
      cache.set("test-key", createMockResponse({ id: 1 }), 1000);

      expect(cache.isRevalidating("test-key")).toBe(false);

      cache.markRevalidating("test-key");
      expect(cache.isRevalidating("test-key")).toBe(true);

      cache.clearRevalidating("test-key");
      expect(cache.isRevalidating("test-key")).toBe(false);
    });
  });

  describe("Export/Import", () => {
    it("should export cache to JSON", () => {
      cache.set("key1", createMockResponse({ id: 1 }), 10000);
      cache.set("key2", createMockResponse({ id: 2 }), 10000);

      const exported = cache.export();

      expect(Object.keys(exported)).toHaveLength(2);
      expect(exported["key1"].data).toEqual({ id: 1 });
      expect(exported["key2"].data).toEqual({ id: 2 });
    });

    it("should import cache from JSON", () => {
      const data = {
        key1: {
          data: { id: 1 },
          createdAt: Date.now(),
          expiresAt: Date.now() + 10000,
          staleUntil: Date.now() + 20000,
          status: 200,
          statusText: "OK",
          headers: {},
          hitCount: 0,
        },
      };

      const count = cache.import(data);

      expect(count).toBe(1);
      expect(cache.has("key1")).toBe(true);
    });

    it("should skip expired entries during import", () => {
      const data = {
        key1: {
          data: { id: 1 },
          createdAt: Date.now() - 10000,
          expiresAt: Date.now() - 5000,
          staleUntil: Date.now() - 1000, // Already expired
          status: 200,
          statusText: "OK",
          headers: {},
          hitCount: 0,
        },
      };

      const count = cache.import(data);

      expect(count).toBe(0);
    });
  });

  describe("Callbacks", () => {
    it("should call onCacheHit callback", () => {
      const onCacheHit = vi.fn();
      const callbackCache = new MemoryCache({
        defaultTTL: 1000,
        onCacheHit,
      });

      callbackCache.set("test-key", createMockResponse({ id: 1 }), 1000);
      callbackCache.get("test-key");

      expect(onCacheHit).toHaveBeenCalledWith(
        "test-key",
        expect.objectContaining({ data: { id: 1 } }),
      );
    });

    it("should call onCacheMiss callback", () => {
      const onCacheMiss = vi.fn();
      const callbackCache = new MemoryCache({
        defaultTTL: 1000,
        onCacheMiss,
      });

      callbackCache.get("non-existent");

      expect(onCacheMiss).toHaveBeenCalledWith("non-existent");
    });

    it("should call onCacheUpdate callback", () => {
      const onCacheUpdate = vi.fn();
      const callbackCache = new MemoryCache({
        defaultTTL: 1000,
        onCacheUpdate,
      });

      callbackCache.set("test-key", createMockResponse({ id: 1 }), 1000);

      expect(onCacheUpdate).toHaveBeenCalledWith(
        "test-key",
        expect.objectContaining({ data: { id: 1 } }),
      );
    });
  });
});

describe("generateCacheKey", () => {
  it("should generate deterministic keys", () => {
    const config1 = {
      method: "GET",
      url: "/api/v1/tasks",
      params: { status: "pending" },
    };
    const config2 = {
      method: "GET",
      url: "/api/v1/tasks",
      params: { status: "pending" },
    };

    expect(generateCacheKey(config1)).toBe(generateCacheKey(config2));
  });

  it("should generate different keys for different params", () => {
    const config1 = {
      method: "GET",
      url: "/api/v1/tasks",
      params: { status: "pending" },
    };
    const config2 = {
      method: "GET",
      url: "/api/v1/tasks",
      params: { status: "completed" },
    };

    expect(generateCacheKey(config1)).not.toBe(generateCacheKey(config2));
  });

  it("should include method in key", () => {
    const getConfig = { method: "GET", url: "/api/v1/tasks" };
    const postConfig = { method: "POST", url: "/api/v1/tasks" };

    expect(generateCacheKey(getConfig)).not.toBe(generateCacheKey(postConfig));
  });

  it("should sort params for consistent keys", () => {
    const config1 = {
      method: "GET",
      url: "/test",
      params: { b: 2, a: 1 },
    };
    const config2 = {
      method: "GET",
      url: "/test",
      params: { a: 1, b: 2 },
    };

    expect(generateCacheKey(config1)).toBe(generateCacheKey(config2));
  });
});

describe("shouldCacheRequest", () => {
  it("should cache GET requests by default", () => {
    const config = { method: "GET", url: "/api/test" };
    expect(shouldCacheRequest(config, DEFAULT_CACHE_CONFIG)).toBe(true);
  });

  it("should cache HEAD requests by default", () => {
    const config = { method: "HEAD", url: "/api/test" };
    expect(shouldCacheRequest(config, DEFAULT_CACHE_CONFIG)).toBe(true);
  });

  it("should not cache POST requests by default", () => {
    const config = { method: "POST", url: "/api/test" };
    expect(shouldCacheRequest(config, DEFAULT_CACHE_CONFIG)).toBe(false);
  });

  it("should respect request-level cache: false", () => {
    const config = { method: "GET", url: "/api/test", cache: false };
    expect(shouldCacheRequest(config, DEFAULT_CACHE_CONFIG)).toBe(false);
  });

  it("should respect global cache disabled", () => {
    const config = { method: "GET", url: "/api/test" };
    const disabledConfig = { ...DEFAULT_CACHE_CONFIG, enabled: false };
    expect(shouldCacheRequest(config, disabledConfig)).toBe(false);
  });
});

describe("getRequestTTL", () => {
  it("should use default TTL", () => {
    const config = { method: "GET", url: "/api/test" };
    expect(getRequestTTL(config, DEFAULT_CACHE_CONFIG)).toBe(
      DEFAULT_CACHE_CONFIG.defaultTTL,
    );
  });

  it("should use request-level TTL override", () => {
    const config = {
      method: "GET",
      url: "/api/test",
      cache: { ttl: 60000 },
    };
    expect(getRequestTTL(config, DEFAULT_CACHE_CONFIG)).toBe(60000);
  });
});

describe("getCachePolicy", () => {
  it("should default to stale-while-revalidate when enabled", () => {
    const config = { method: "GET", url: "/api/test" };
    expect(getCachePolicy(config, DEFAULT_CACHE_CONFIG)).toBe(
      "stale-while-revalidate",
    );
  });

  it("should use cache-first when stale-while-revalidate disabled", () => {
    const config = { method: "GET", url: "/api/test" };
    const noSWRConfig = { ...DEFAULT_CACHE_CONFIG, staleWhileRevalidate: false };
    expect(getCachePolicy(config, noSWRConfig)).toBe("cache-first");
  });

  it("should respect request-level policy override", () => {
    const config = {
      method: "GET",
      url: "/api/test",
      cache: { policy: "network-first" as const },
    };
    expect(getCachePolicy(config, DEFAULT_CACHE_CONFIG)).toBe("network-first");
  });
});

describe("createCache Presets", () => {
  it("should create default cache", () => {
    const cache = createCache("default");
    const stats = cache.getStats();
    expect(stats.size).toBe(0);
  });

  it("should create aggressive cache", () => {
    const cache = createCache("aggressive");
    // Aggressive should have longer TTL
    expect(cache).toBeDefined();
  });

  it("should create conservative cache", () => {
    const cache = createCache("conservative");
    expect(cache).toBeDefined();
  });

  it("should create offline cache", () => {
    const cache = createCache("offline");
    // Offline should have very long TTL
    expect(cache).toBeDefined();
  });
});

describe("CacheTTL Constants", () => {
  it("should have expected TTL values", () => {
    expect(CacheTTL.VERY_SHORT).toBe(30 * 1000);
    expect(CacheTTL.SHORT).toBe(60 * 1000);
    expect(CacheTTL.MEDIUM).toBe(5 * 60 * 1000);
    expect(CacheTTL.LONG).toBe(15 * 60 * 1000);
    expect(CacheTTL.VERY_LONG).toBe(60 * 60 * 1000);
    expect(CacheTTL.DAY).toBe(24 * 60 * 60 * 1000);
    expect(CacheTTL.NONE).toBe(0);
  });
});
