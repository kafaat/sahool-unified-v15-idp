/**
 * Redis Sentinel Usage Examples (TypeScript)
 * ===========================================
 *
 * أمثلة على استخدام Redis Sentinel في TypeScript/Node.js
 *
 * @author Sahool Platform Team
 */

import { getRedisSentinelClient, RedisSentinelClient } from './redis-sentinel';

// ═══════════════════════════════════════════════════════════════════════════
// Example 1: Cache Decorator
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Cache decorator للدوال
 */
function CacheResult(keyPrefix: string, ttl: number = 3600) {
  return function (
    target: any,
    propertyKey: string,
    descriptor: PropertyDescriptor
  ) {
    const originalMethod = descriptor.value;

    descriptor.value = async function (...args: any[]) {
      const redis = getRedisSentinelClient();
      const cacheKey = `${keyPrefix}:${JSON.stringify(args)}`;

      // محاولة القراءة من Cache
      try {
        const cached = await redis.get(cacheKey, true);
        if (cached) {
          console.log(`✓ Cache hit: ${cacheKey}`);
          return JSON.parse(cached);
        }
      } catch (error) {
        console.error('Cache read error:', error);
      }

      console.log(`✗ Cache miss: ${cacheKey}`);

      // تنفيذ الدالة الأصلية
      const result = await originalMethod.apply(this, args);

      // حفظ في Cache
      try {
        await redis.set(cacheKey, JSON.stringify(result), { ex: ttl });
      } catch (error) {
        console.error('Cache write error:', error);
      }

      return result;
    };

    return descriptor;
  };
}

// ═══════════════════════════════════════════════════════════════════════════
// Example 2: Rate Limiter
// ═══════════════════════════════════════════════════════════════════════════

/**
 * معدل تحديد الطلبات باستخدام Redis
 */
export class RateLimiter {
  private redis: RedisSentinelClient;
  private maxRequests: number;
  private window: number; // seconds

  constructor(maxRequests: number = 100, window: number = 60) {
    this.redis = getRedisSentinelClient();
    this.maxRequests = maxRequests;
    this.window = window;
  }

  /**
   * التحقق من السماح بالطلب
   */
  async isAllowed(identifier: string): Promise<boolean> {
    const key = `rate_limit:${identifier}`;
    const current = Math.floor(Date.now() / 1000);

    // استخدام Pipeline للعمليات المتعددة
    const pipeline = this.redis.pipeline();

    // حذف الطلبات القديمة
    pipeline.zremrangebyscore(key, 0, current - this.window);

    // إضافة الطلب الحالي
    pipeline.zadd(key, current, String(current));

    // عد الطلبات
    pipeline.zcard(key);

    // تعيين TTL
    pipeline.expire(key, this.window);

    const results = await pipeline.exec();

    if (!results) {
      return false;
    }

    const requestCount = results[2][1] as number;
    return requestCount <= this.maxRequests;
  }

  /**
   * الحصول على عدد الطلبات المتبقية
   */
  async getRemaining(identifier: string): Promise<number> {
    const key = `rate_limit:${identifier}`;
    const current = Math.floor(Date.now() / 1000);

    const pipeline = this.redis.pipeline();
    pipeline.zremrangebyscore(key, 0, current - this.window);
    pipeline.zcard(key);

    const results = await pipeline.exec();
    if (!results) {
      return this.maxRequests;
    }

    const currentCount = results[1][1] as number;
    return Math.max(0, this.maxRequests - currentCount);
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Example 3: Distributed Lock
// ═══════════════════════════════════════════════════════════════════════════

/**
 * قفل موزع باستخدام Redis
 */
export class DistributedLock {
  private redis: RedisSentinelClient;
  private lockName: string;
  private timeout: number;
  private identifier: string;

  constructor(lockName: string, timeout: number = 10) {
    this.redis = getRedisSentinelClient();
    this.lockName = `lock:${lockName}`;
    this.timeout = timeout;
    this.identifier = `${Date.now()}-${Math.random()}`;
  }

  /**
   * الحصول على القفل
   */
  async acquire(
    blocking: boolean = true,
    acquireTimeout?: number
  ): Promise<boolean> {
    const endTime = Date.now() + (acquireTimeout || this.timeout) * 1000;

    while (true) {
      // محاولة الحصول على القفل
      const result = await this.redis.set(this.lockName, this.identifier, {
        nx: true,
        ex: this.timeout,
      });

      if (result === 'OK') {
        return true;
      }

      if (!blocking || Date.now() >= endTime) {
        return false;
      }

      // انتظار قصير
      await new Promise((resolve) => setTimeout(resolve, 10));
    }
  }

  /**
   * تحرير القفل
   */
  async release(): Promise<boolean> {
    const value = await this.redis.get(this.lockName, false);
    if (value === this.identifier) {
      await this.redis.delete(this.lockName);
      return true;
    }
    return false;
  }

  /**
   * استخدام القفل في Context
   */
  async withLock<T>(
    callback: () => Promise<T>,
    acquireTimeout?: number
  ): Promise<T> {
    const acquired = await this.acquire(true, acquireTimeout);
    if (!acquired) {
      throw new Error(`Could not acquire lock: ${this.lockName}`);
    }

    try {
      return await callback();
    } finally {
      await this.release();
    }
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Example 4: Session Manager
// ═══════════════════════════════════════════════════════════════════════════

/**
 * إدارة جلسات المستخدم
 */
export class SessionManager {
  private redis: RedisSentinelClient;
  private prefix: string;

  constructor(prefix: string = 'session') {
    this.redis = getRedisSentinelClient();
    this.prefix = prefix;
  }

  /**
   * إنشاء جلسة جديدة
   */
  async create(
    sessionId: string,
    data: Record<string, any>,
    ttl: number = 3600
  ): Promise<boolean> {
    const key = `${this.prefix}:${sessionId}`;
    const result = await this.redis.set(key, JSON.stringify(data), { ex: ttl });
    return result === 'OK';
  }

  /**
   * الحصول على بيانات الجلسة
   */
  async get(sessionId: string): Promise<Record<string, any> | null> {
    const key = `${this.prefix}:${sessionId}`;
    const data = await this.redis.get(key, true);
    return data ? JSON.parse(data) : null;
  }

  /**
   * تحديث بيانات الجلسة
   */
  async update(
    sessionId: string,
    data: Record<string, any>,
    ttl?: number
  ): Promise<boolean> {
    const key = `${this.prefix}:${sessionId}`;

    if (ttl) {
      const result = await this.redis.set(key, JSON.stringify(data), { ex: ttl });
      return result === 'OK';
    } else {
      // الحفاظ على TTL الحالي
      const currentTtl = await this.redis.ttl(key);
      if (currentTtl > 0) {
        const result = await this.redis.set(key, JSON.stringify(data), {
          ex: currentTtl,
        });
        return result === 'OK';
      }
      const result = await this.redis.set(key, JSON.stringify(data));
      return result === 'OK';
    }
  }

  /**
   * حذف جلسة
   */
  async delete(sessionId: string): Promise<boolean> {
    const key = `${this.prefix}:${sessionId}`;
    const result = await this.redis.delete(key);
    return result > 0;
  }

  /**
   * تجديد مدة الجلسة
   */
  async refresh(sessionId: string, ttl: number = 3600): Promise<boolean> {
    const key = `${this.prefix}:${sessionId}`;
    const result = await this.redis.expire(key, ttl);
    return result === 1;
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Example 5: Cache Service Class
// ═══════════════════════════════════════════════════════════════════════════

/**
 * خدمة التخزين المؤقت
 */
export class CacheService {
  private redis: RedisSentinelClient;

  constructor() {
    this.redis = getRedisSentinelClient();
  }

  /**
   * الحصول من Cache أو تنفيذ الدالة
   */
  async getOrSet<T>(
    key: string,
    factory: () => Promise<T>,
    ttl: number = 3600
  ): Promise<T> {
    // محاولة القراءة من Cache
    const cached = await this.redis.get(key, true);
    if (cached) {
      return JSON.parse(cached);
    }

    // تنفيذ الدالة
    const value = await factory();

    // حفظ في Cache
    await this.redis.set(key, JSON.stringify(value), { ex: ttl });

    return value;
  }

  /**
   * حذف من Cache
   */
  async invalidate(...keys: string[]): Promise<number> {
    return this.redis.delete(...keys);
  }

  /**
   * حذف جميع المفاتيح بنمط معين
   */
  async invalidatePattern(pattern: string): Promise<number> {
    // Note: هذه عملية مكلفة، استخدمها بحذر
    const pipeline = this.redis.pipeline();

    // في بيئة إنتاجية، استخدم SCAN بدلاً من KEYS
    // هنا نستخدم Pipeline لحذف المفاتيح

    let deleted = 0;
    // Simplified version - في الإنتاج استخدم SCAN
    // await this.redis.delete(...matchingKeys);

    return deleted;
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Example Usage
// ═══════════════════════════════════════════════════════════════════════════

/**
 * مثال على استخدام جميع الأمثلة
 */
async function runExamples() {
  console.log('Redis Sentinel Examples\n');

  // Example 1: Basic Operations
  console.log('Example 1: Basic Operations');
  const redis = getRedisSentinelClient();

  await redis.set('test:key', 'Hello from Redis Sentinel!', { ex: 60 });
  const value = await redis.get('test:key');
  console.log(`  Value: ${value}`);
  await redis.delete('test:key');
  console.log();

  // Example 2: Rate Limiter
  console.log('Example 2: Rate Limiter');
  const limiter = new RateLimiter(5, 10);

  for (let i = 0; i < 7; i++) {
    const allowed = await limiter.isAllowed('user:1000');
    const remaining = await limiter.getRemaining('user:1000');

    if (allowed) {
      console.log(`  Request ${i + 1}: Allowed (Remaining: ${remaining})`);
    } else {
      console.log(`  Request ${i + 1}: Denied (Rate limit exceeded)`);
    }
  }
  console.log();

  // Example 3: Distributed Lock
  console.log('Example 3: Distributed Lock');
  const lock = new DistributedLock('export:process', 5);

  await lock.withLock(async () => {
    console.log('  Lock acquired, processing...');
    await new Promise((resolve) => setTimeout(resolve, 1000));
    console.log('  Processing completed');
  });
  console.log('  Lock released');
  console.log();

  // Example 4: Session Manager
  console.log('Example 4: Session Manager');
  const session = new SessionManager();

  await session.create(
    'user:1000',
    { username: 'ahmed', role: 'admin' },
    300
  );
  const sessionData = await session.get('user:1000');
  console.log(`  Session data:`, sessionData);
  await session.delete('user:1000');
  console.log();

  // Example 5: Cache Service
  console.log('Example 5: Cache Service');
  const cache = new CacheService();

  const userData = await cache.getOrSet(
    'user:profile:1000',
    async () => {
      console.log('  Fetching from database...');
      return { id: 1000, name: 'Ahmed', email: 'ahmed@example.com' };
    },
    60
  );
  console.log(`  User data:`, userData);

  // Second call should use cache
  const cachedUserData = await cache.getOrSet(
    'user:profile:1000',
    async () => {
      console.log('  This should not print!');
      return {};
    },
    60
  );
  console.log(`  Cached user data:`, cachedUserData);
  console.log();

  // Health Check
  console.log('Health Check:');
  const health = await redis.healthCheck();
  console.log(`  Status: ${health.status}`);
  console.log(`  Master Ping: ${health.checks.masterPing}`);
  console.log(`  Circuit Breaker: ${health.checks.circuitBreaker}`);
  console.log();

  // Cleanup
  await redis.close();
}

// Run examples if this file is executed directly
if (require.main === module) {
  runExamples()
    .then(() => {
      console.log('✓ All examples completed successfully!');
      process.exit(0);
    })
    .catch((error) => {
      console.error('✗ Error running examples:', error);
      process.exit(1);
    });
}

// Export for use in other files
export { runExamples };
