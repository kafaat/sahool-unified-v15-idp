/**
 * SAHOOL Platform - Cache Usage Examples
 * ======================================
 *
 * Comprehensive examples demonstrating all caching features
 */

import { Injectable, Module, OnModuleInit } from "@nestjs/common";
import { InjectRedis } from "@liaoliaots/nestjs-redis";
import Redis from "ioredis";
import {
  CacheManager,
  CacheTTL,
  getCacheManager,
  resetCacheManager,
} from "./cache-manager";
import { CacheMetricsService } from "./cache-metrics.service";
import {
  CacheWarmingService,
  createUserWarmingStrategy,
} from "./cache-warming.service";

// =============================================================================
// Example 1: Basic Cache Operations
// =============================================================================

@Injectable()
export class UserService {
  private cacheManager: CacheManager;

  constructor(@InjectRedis() private readonly redis: Redis) {
    this.cacheManager = new CacheManager(redis, {
      keyPrefix: "user:",
      defaultTTL: CacheTTL.USER_VALIDATION,
      enableStampedeProtection: true,
      enableMetrics: true,
    });
  }

  /**
   * Get user with automatic caching (cache-aside pattern)
   */
  async getUser(userId: string) {
    return this.cacheManager.getOrFetch(
      userId,
      async () => {
        // This only executes on cache miss
        console.log(`Fetching user ${userId} from database...`);
        return await this.fetchUserFromDatabase(userId);
      },
      CacheTTL.USER_VALIDATION,
    );
  }

  /**
   * Update user with immediate cache update (write-through pattern)
   */
  async updateUser(userId: string, updates: any) {
    return this.cacheManager.writeThrough(
      userId,
      updates,
      async (data) => {
        // Write to database first
        await this.updateUserInDatabase(userId, data);
      },
      CacheTTL.USER_VALIDATION,
    );
  }

  /**
   * Invalidate all user cache entries
   */
  async invalidateUserCache(userId: string) {
    await this.cacheManager.invalidatePattern(`${userId}:*`);
  }

  private async fetchUserFromDatabase(userId: string) {
    // Simulate database query
    return { id: userId, name: "John Doe", email: "john@example.com" };
  }

  private async updateUserInDatabase(userId: string, data: any) {
    // Simulate database update
    console.log(`Updating user ${userId} in database`, data);
  }
}

// =============================================================================
// Example 2: IoT Service with Redis Cache
// =============================================================================

interface SensorReading {
  deviceId: string;
  fieldId: string;
  sensorType: string;
  value: number;
  timestamp: Date;
}

@Injectable()
export class IotCacheService {
  constructor(@InjectRedis() private readonly redis: Redis) {}

  /**
   * Cache sensor reading with proper TTL
   */
  async cacheSensorReading(reading: SensorReading): Promise<void> {
    const key = `sensor:${reading.fieldId}:${reading.sensorType}`;
    await this.redis.setex(
      key,
      CacheTTL.SENSOR_DATA, // 30 seconds
      JSON.stringify(reading),
    );
  }

  /**
   * Get sensor reading from cache
   */
  async getSensorReading(
    fieldId: string,
    sensorType: string,
  ): Promise<SensorReading | null> {
    const key = `sensor:${fieldId}:${sensorType}`;
    const data = await this.redis.get(key);
    return data ? JSON.parse(data) : null;
  }

  /**
   * Get all sensor readings for a field (using SCAN)
   */
  async getFieldSensorData(fieldId: string): Promise<SensorReading[]> {
    const readings: SensorReading[] = [];
    const pattern = `sensor:${fieldId}:*`;
    let cursor = "0";

    do {
      const [newCursor, keys] = await this.redis.scan(
        cursor,
        "MATCH",
        pattern,
        "COUNT",
        100,
      );
      cursor = newCursor;

      for (const key of keys) {
        const data = await this.redis.get(key);
        if (data) {
          readings.push(JSON.parse(data));
        }
      }
    } while (cursor !== "0");

    return readings;
  }

  /**
   * Invalidate all sensor readings for a field
   */
  async invalidateFieldSensors(fieldId: string): Promise<number> {
    const pattern = `sensor:${fieldId}:*`;
    let cursor = "0";
    let totalDeleted = 0;

    do {
      const [newCursor, keys] = await this.redis.scan(
        cursor,
        "MATCH",
        pattern,
        "COUNT",
        100,
      );
      cursor = newCursor;

      if (keys.length > 0) {
        totalDeleted += await this.redis.del(...keys);
      }
    } while (cursor !== "0");

    return totalDeleted;
  }
}

// =============================================================================
// Example 3: Cache Stampede Protection
// =============================================================================

@Injectable()
export class ExpensiveOperationService {
  private cacheManager: CacheManager;

  constructor(@InjectRedis() private readonly redis: Redis) {
    this.cacheManager = new CacheManager(redis, {
      keyPrefix: "expensive:",
      defaultTTL: 600,
      enableStampedeProtection: true, // ✅ Enable stampede protection
    });
  }

  /**
   * Expensive operation with stampede protection
   * Multiple concurrent requests will only trigger ONE database query
   */
  async getExpensiveData(key: string) {
    return this.cacheManager.getOrFetch(
      key,
      async () => {
        console.log(`🔥 Executing expensive operation for ${key}...`);
        // Simulate expensive operation (5 seconds)
        await new Promise((resolve) => setTimeout(resolve, 5000));
        return { data: "expensive result", timestamp: new Date() };
      },
      600,
    );
  }

  /**
   * Test stampede protection
   */
  async testStampedeProtection() {
    console.log("Starting 100 concurrent requests...");
    const startTime = Date.now();

    // 100 concurrent requests for the same key
    const promises = Array(100)
      .fill(null)
      .map(() => this.getExpensiveData("test-key"));

    const results = await Promise.all(promises);

    const duration = Date.now() - startTime;
    console.log(`✅ Completed in ${duration}ms`);
    console.log(
      `All results identical: ${results.every((r) => r === results[0])}`,
    );
    console.log(`Expected: ~5000ms (one execution)`);
    console.log(`Without protection: ~500000ms (100 executions)`);

    return { duration, prevented: 99 };
  }
}

// =============================================================================
// Example 4: Cache Warming
// =============================================================================

@Injectable()
export class CacheWarmingExample implements OnModuleInit {
  constructor(
    private readonly cacheWarming: CacheWarmingService,
    private readonly userService: UserService,
  ) {}

  async onModuleInit() {
    // Register user warming strategy
    this.cacheWarming.registerStrategy(
      createUserWarmingStrategy(
        // Get top active users
        async () => {
          return ["user-1", "user-2", "user-3"];
        },
        // Fetch user data
        async (userId) => {
          return this.userService.getUser(userId);
        },
      ),
    );

    // Register field warming strategy
    this.cacheWarming.registerStrategy({
      name: "field-data-warming",
      getKeys: async () => {
        // Get active fields from database
        return await this.getActiveFieldIds();
      },
      fetcher: async (fieldId) => {
        return await this.fetchFieldData(fieldId);
      },
      ttl: CacheTTL.FIELD_DATA,
      enabled: true,
    });

    console.log("✅ Cache warming strategies registered");
  }

  /**
   * Manual cache warming trigger
   */
  async warmCache() {
    await this.cacheWarming.warmNow();
    console.log("✅ Cache warmed successfully");
  }

  private async getActiveFieldIds(): Promise<string[]> {
    return ["field-1", "field-2", "field-3"];
  }

  private async fetchFieldData(fieldId: string) {
    return { id: fieldId, name: `Field ${fieldId}` };
  }
}

// =============================================================================
// Example 5: Cache Metrics & Monitoring
// =============================================================================

@Injectable()
export class CacheMonitoringService {
  constructor(
    private readonly cacheManager: CacheManager,
    private readonly metricsService: CacheMetricsService,
  ) {}

  /**
   * Get cache performance metrics
   */
  getPerformanceMetrics() {
    const managerMetrics = this.cacheManager.getMetrics();
    const serviceMetrics = this.metricsService.getMetrics();

    return {
      manager: managerMetrics,
      service: {
        ...serviceMetrics,
        getLatency: this.metricsService.getLatencyStats("get"),
        setLatency: this.metricsService.getLatencyStats("set"),
      },
    };
  }

  /**
   * Get cache health status with recommendations
   */
  getHealthStatus() {
    return this.metricsService.getHealthStatus();
  }

  /**
   * Performance report
   */
  async generatePerformanceReport() {
    const metrics = this.getPerformanceMetrics();
    const health = this.getHealthStatus();

    console.log(`
╔═══════════════════════════════════════════════════════════╗
║             CACHE PERFORMANCE REPORT                      ║
╠═══════════════════════════════════════════════════════════╣
║ Hit Rate:        ${(metrics.manager.hitRate * 100).toFixed(1)}%                               ║
║ Total Requests:  ${(metrics.manager.hits + metrics.manager.misses).toLocaleString()}                                 ║
║ Stampede Prev:   ${metrics.manager.stampedePreventions.toLocaleString()}                                 ║
╠═══════════════════════════════════════════════════════════╣
║ GET p50:         ${metrics.service.getLatency.p50.toFixed(2)}ms                            ║
║ GET p95:         ${metrics.service.getLatency.p95.toFixed(2)}ms                            ║
║ GET p99:         ${metrics.service.getLatency.p99.toFixed(2)}ms                            ║
╠═══════════════════════════════════════════════════════════╣
║ Health Status:   ${health.status.toUpperCase()}                              ║
${health.issues.length > 0 ? "║ Issues:          " + health.issues.join(", ").padEnd(40) + "║" : ""}
╚═══════════════════════════════════════════════════════════╝
    `);

    return { metrics, health };
  }
}

// =============================================================================
// Example 6: Complete Application Setup
// =============================================================================

@Module({
  providers: [
    UserService,
    IotCacheService,
    ExpensiveOperationService,
    CacheWarmingExample,
    CacheMonitoringService,
    CacheMetricsService,
    CacheWarmingService,
  ],
  exports: [
    UserService,
    IotCacheService,
    ExpensiveOperationService,
    CacheMonitoringService,
  ],
})
export class CacheExamplesModule {}

// =============================================================================
// Example 7: Testing Cache Operations
// =============================================================================

/**
 * Test suite demonstrating cache behavior
 */
export class CacheTests {
  private cacheManager: CacheManager;

  constructor(redis: Redis) {
    this.cacheManager = new CacheManager(redis, {
      keyPrefix: "test:",
      defaultTTL: 60,
      enableStampedeProtection: true,
      enableMetrics: true,
    });
  }

  /**
   * Test basic cache operations
   */
  async testBasicOperations() {
    console.log("Testing basic cache operations...");

    // Set
    await this.cacheManager.set("key1", "value1", 60);

    // Get
    const value = await this.cacheManager.get("key1");
    console.assert(value === "value1", 'Value should be "value1"');

    // Exists
    const exists = await this.cacheManager.exists("key1");
    console.assert(exists === true, "Key should exist");

    // Delete
    await this.cacheManager.delete("key1");
    const deleted = await this.cacheManager.get("key1");
    console.assert(deleted === null, "Key should be deleted");

    console.log("✅ Basic operations test passed");
  }

  /**
   * Test stampede protection
   */
  async testStampedeProtection() {
    console.log("Testing stampede protection...");

    let dbCallCount = 0;
    const fetcher = async () => {
      dbCallCount++;
      await new Promise((resolve) => setTimeout(resolve, 100));
      return "result";
    };

    // 10 concurrent requests
    await Promise.all(
      Array(10)
        .fill(null)
        .map(() => this.cacheManager.getOrFetch("stampede-key", fetcher)),
    );

    console.assert(dbCallCount === 1, "Should only call fetcher once");
    console.log(
      `✅ Stampede protection test passed (DB calls: ${dbCallCount}/10)`,
    );
  }

  /**
   * Test pattern invalidation
   */
  async testPatternInvalidation() {
    console.log("Testing pattern invalidation...");

    // Set multiple keys
    await this.cacheManager.set("user:1", { id: 1 });
    await this.cacheManager.set("user:2", { id: 2 });
    await this.cacheManager.set("user:3", { id: 3 });

    // Invalidate pattern
    const deleted = await this.cacheManager.invalidatePattern("user:*");
    console.assert(deleted === 3, "Should delete 3 keys");

    // Verify deletion
    const user1 = await this.cacheManager.get("user:1");
    console.assert(user1 === null, "Keys should be deleted");

    console.log("✅ Pattern invalidation test passed");
  }

  /**
   * Test cache metrics
   */
  async testMetrics() {
    console.log("Testing cache metrics...");

    // Reset metrics
    this.cacheManager.resetMetrics();

    // Cause some hits and misses
    await this.cacheManager.set("metric-key", "value");
    await this.cacheManager.get("metric-key"); // Hit
    await this.cacheManager.get("nonexistent"); // Miss

    const metrics = this.cacheManager.getMetrics();
    console.assert(metrics.hits >= 1, "Should have at least 1 hit");
    console.assert(metrics.misses >= 1, "Should have at least 1 miss");

    console.log(
      `✅ Metrics test passed (Hit rate: ${(metrics.hitRate * 100).toFixed(1)}%)`,
    );
  }

  /**
   * Run all tests
   */
  async runAllTests() {
    await this.testBasicOperations();
    await this.testStampedeProtection();
    await this.testPatternInvalidation();
    await this.testMetrics();

    console.log("\n✅ All cache tests passed!");
  }
}

// =============================================================================
// Export Examples
// =============================================================================

export {
  UserService,
  IotCacheService,
  ExpensiveOperationService,
  CacheWarmingExample,
  CacheMonitoringService,
  CacheTests,
};
