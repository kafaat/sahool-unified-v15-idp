/**
 * Redis Sentinel Client for High Availability (TypeScript)
 * =========================================================
 *
 * يوفر هذا الملف اتصالاً بـ Redis Sentinel مع:
 * - Automatic failover handling
 * - Connection pooling
 * - Circuit breaker pattern
 * - Health monitoring
 * - Retry logic with exponential backoff
 *
 * @author Sahool Platform Team
 * @license MIT
 */

import Redis, { RedisOptions, Cluster } from 'ioredis';

/**
 * تكوين Redis Sentinel
 */
export interface RedisSentinelConfig {
  /** قائمة عناوين Sentinel */
  sentinels: Array<{ host: string; port: number }>;
  /** اسم المجموعة الرئيسية */
  masterName: string;
  /** كلمة مرور Redis */
  password?: string;
  /** رقم قاعدة البيانات */
  db?: number;
  /** مهلة الاتصال (ميلي ثانية) */
  connectTimeout?: number;
  /** مهلة القيادة (ميلي ثانية) */
  commandTimeout?: number;
  /** الحد الأقصى لإعادة المحاولة */
  maxRetriesPerRequest?: number;
  /** تمكين قراءة من Replicas */
  enableReadyCheck?: boolean;
  /** تمكين اتصالات دائمة */
  enableOfflineQueue?: boolean;
  /** استراتيجية إعادة الاتصال */
  retryStrategy?: (times: number) => number | null;
}

/**
 * حالات Circuit Breaker
 */
enum CircuitBreakerState {
  CLOSED = 'CLOSED',
  OPEN = 'OPEN',
  HALF_OPEN = 'HALF_OPEN',
}

/**
 * Circuit Breaker للحماية من الأخطاء المتكررة
 */
class CircuitBreaker {
  private state: CircuitBreakerState = CircuitBreakerState.CLOSED;
  private failureCount: number = 0;
  private lastFailureTime: number | null = null;
  private successCount: number = 0;

  constructor(
    private failureThreshold: number = 5,
    private recoveryTimeout: number = 60000, // 60 seconds
    private halfOpenMaxAttempts: number = 3
  ) {}

  /**
   * استدعاء دالة مع حماية Circuit Breaker
   */
  async call<T>(func: () => Promise<T>): Promise<T> {
    if (this.state === CircuitBreakerState.OPEN) {
      if (
        this.lastFailureTime &&
        Date.now() - this.lastFailureTime > this.recoveryTimeout
      ) {
        this.state = CircuitBreakerState.HALF_OPEN;
        this.successCount = 0;
        console.log('Circuit breaker entering HALF_OPEN state');
      } else {
        throw new Error('Circuit breaker is OPEN');
      }
    }

    try {
      const result = await func();
      this.onSuccess();
      return result;
    } catch (error) {
      this.onFailure();
      throw error;
    }
  }

  /**
   * نجاح العملية
   */
  private onSuccess(): void {
    if (this.state === CircuitBreakerState.HALF_OPEN) {
      this.successCount++;
      if (this.successCount >= this.halfOpenMaxAttempts) {
        this.state = CircuitBreakerState.CLOSED;
        this.failureCount = 0;
        console.log('Circuit breaker closed after successful recovery');
      }
    } else {
      this.failureCount = 0;
    }
  }

  /**
   * فشل العملية
   */
  private onFailure(): void {
    this.failureCount++;
    this.lastFailureTime = Date.now();

    if (this.failureCount >= this.failureThreshold) {
      this.state = CircuitBreakerState.OPEN;
      console.error(
        `Circuit breaker opened after ${this.failureCount} failures`
      );
    }
  }

  /**
   * الحصول على حالة Circuit Breaker
   */
  getState(): CircuitBreakerState {
    return this.state;
  }

  /**
   * إعادة تعيين Circuit Breaker
   */
  reset(): void {
    this.state = CircuitBreakerState.CLOSED;
    this.failureCount = 0;
    this.successCount = 0;
    this.lastFailureTime = null;
  }
}

/**
 * معلومات صحة النظام
 */
export interface HealthCheckResult {
  status: 'healthy' | 'degraded' | 'unhealthy';
  timestamp: number;
  checks: {
    masterPing?: boolean;
    sentinelInfo?: SentinelInfo;
    circuitBreaker?: CircuitBreakerState;
  };
  error?: string;
}

/**
 * معلومات Sentinel
 */
export interface SentinelInfo {
  master: { host: string; port: number } | null;
  slaves: Array<{ host: string; port: number }>;
  masterName: string;
  sentinelCount: number;
  isConnected: boolean;
  circuitBreakerState: CircuitBreakerState;
}

/**
 * Redis Sentinel Client مع دعم التوافر العالي
 */
export class RedisSentinelClient {
  private masterClient: Redis;
  private slaveClient: Redis;
  private circuitBreaker: CircuitBreaker;
  private config: Required<RedisSentinelConfig>;

  constructor(config: RedisSentinelConfig) {
    this.config = this.normalizeConfig(config);
    this.circuitBreaker = new CircuitBreaker();

    // إنشاء اتصال Master
    this.masterClient = this.createSentinelConnection(false);

    // إنشاء اتصال Slave للقراءة
    this.slaveClient = this.createSentinelConnection(true);

    this.setupEventHandlers();
  }

  /**
   * تطبيع التكوين مع القيم الافتراضية
   */
  private normalizeConfig(
    config: RedisSentinelConfig
  ): Required<RedisSentinelConfig> {
    return {
      sentinels: config.sentinels,
      masterName: config.masterName,
      password: config.password || process.env.REDIS_PASSWORD || '',
      db: config.db || 0,
      connectTimeout: config.connectTimeout || 10000,
      commandTimeout: config.commandTimeout || 5000,
      maxRetriesPerRequest: config.maxRetriesPerRequest || 3,
      enableReadyCheck: config.enableReadyCheck ?? true,
      enableOfflineQueue: config.enableOfflineQueue ?? true,
      retryStrategy:
        config.retryStrategy ||
        ((times: number) => {
          if (times > 10) {
            return null; // Stop retrying
          }
          return Math.min(times * 100, 3000); // Exponential backoff
        }),
    };
  }

  /**
   * إنشاء اتصال Sentinel
   */
  private createSentinelConnection(isSlaveRead: boolean = false): Redis {
    const options: RedisOptions = {
      sentinels: this.config.sentinels,
      name: this.config.masterName,
      password: this.config.password,
      db: this.config.db,
      connectTimeout: this.config.connectTimeout,
      commandTimeout: this.config.commandTimeout,
      maxRetriesPerRequest: this.config.maxRetriesPerRequest,
      enableReadyCheck: this.config.enableReadyCheck,
      enableOfflineQueue: this.config.enableOfflineQueue,
      retryStrategy: this.config.retryStrategy,
      sentinelRetryStrategy: (times: number) => {
        return Math.min(times * 100, 3000);
      },
      // استخدام Slave للقراءة إذا تم تحديده
      role: isSlaveRead ? 'slave' : 'master',
      preferredSlaves: isSlaveRead
        ? [
            { ip: '127.0.0.1', port: '6380', flags: 'slave' },
            { ip: '127.0.0.1', port: '6381', flags: 'slave' },
          ]
        : undefined,
    };

    return new Redis(options);
  }

  /**
   * إعداد معالجات الأحداث
   */
  private setupEventHandlers(): void {
    // Master events
    this.masterClient.on('connect', () => {
      console.log('Connected to Redis master');
    });

    this.masterClient.on('ready', () => {
      console.log('Redis master is ready');
      this.circuitBreaker.reset();
    });

    this.masterClient.on('error', (err) => {
      console.error('Redis master error:', err);
    });

    this.masterClient.on('close', () => {
      console.warn('Redis master connection closed');
    });

    this.masterClient.on('reconnecting', () => {
      console.log('Reconnecting to Redis master...');
    });

    this.masterClient.on('+switch-master', (data) => {
      console.log('Master switched:', data);
    });

    // Slave events
    this.slaveClient.on('connect', () => {
      console.log('Connected to Redis slave');
    });

    this.slaveClient.on('error', (err) => {
      console.error('Redis slave error:', err);
    });
  }

  /**
   * تنفيذ عملية مع إعادة المحاولة
   */
  private async executeWithRetry<T>(
    func: () => Promise<T>,
    maxRetries: number = 3,
    retryDelay: number = 500
  ): Promise<T> {
    return this.circuitBreaker.call(async () => {
      let lastError: Error | null = null;

      for (let attempt = 0; attempt < maxRetries; attempt++) {
        try {
          return await func();
        } catch (error) {
          lastError = error as Error;

          if (attempt < maxRetries - 1) {
            const delay = retryDelay * Math.pow(2, attempt); // Exponential backoff
            console.warn(
              `Retry ${attempt + 1}/${maxRetries} after ${delay}ms due to:`,
              error
            );
            await new Promise((resolve) => setTimeout(resolve, delay));
          }
        }
      }

      throw lastError || new Error('All retries failed');
    });
  }

  // ───────────────────────────────────────────────────────────────────────
  // Basic Operations
  // ───────────────────────────────────────────────────────────────────────

  /**
   * تعيين قيمة مفتاح
   */
  async set(
    key: string,
    value: string | number,
    options?: {
      ex?: number; // Seconds
      px?: number; // Milliseconds
      nx?: boolean; // Only set if not exists
      xx?: boolean; // Only set if exists
    }
  ): Promise<'OK' | null> {
    return this.executeWithRetry(async () => {
      const args: any[] = [key, value];

      if (options?.ex) args.push('EX', options.ex);
      if (options?.px) args.push('PX', options.px);
      if (options?.nx) args.push('NX');
      if (options?.xx) args.push('XX');

      return this.masterClient.set(...args);
    });
  }

  /**
   * الحصول على قيمة مفتاح
   */
  async get(key: string, useSlave: boolean = true): Promise<string | null> {
    const client = useSlave ? this.slaveClient : this.masterClient;
    return this.executeWithRetry(() => client.get(key));
  }

  /**
   * حذف مفاتيح
   */
  async delete(...keys: string[]): Promise<number> {
    return this.executeWithRetry(() => this.masterClient.del(...keys));
  }

  /**
   * التحقق من وجود مفاتيح
   */
  async exists(...keys: string[]): Promise<number> {
    return this.executeWithRetry(() => this.slaveClient.exists(...keys));
  }

  /**
   * تعيين وقت انتهاء صلاحية مفتاح
   */
  async expire(key: string, seconds: number): Promise<number> {
    return this.executeWithRetry(() => this.masterClient.expire(key, seconds));
  }

  /**
   * الحصول على وقت انتهاء الصلاحية المتبقي
   */
  async ttl(key: string): Promise<number> {
    return this.executeWithRetry(() => this.slaveClient.ttl(key));
  }

  // ───────────────────────────────────────────────────────────────────────
  // Hash Operations
  // ───────────────────────────────────────────────────────────────────────

  /**
   * تعيين قيمة في Hash
   */
  async hset(name: string, key: string, value: string | number): Promise<number> {
    return this.executeWithRetry(() => this.masterClient.hset(name, key, value));
  }

  /**
   * الحصول على قيمة من Hash
   */
  async hget(
    name: string,
    key: string,
    useSlave: boolean = true
  ): Promise<string | null> {
    const client = useSlave ? this.slaveClient : this.masterClient;
    return this.executeWithRetry(() => client.hget(name, key));
  }

  /**
   * الحصول على جميع قيم Hash
   */
  async hgetall(
    name: string,
    useSlave: boolean = true
  ): Promise<Record<string, string>> {
    const client = useSlave ? this.slaveClient : this.masterClient;
    return this.executeWithRetry(() => client.hgetall(name));
  }

  /**
   * حذف مفاتيح من Hash
   */
  async hdel(name: string, ...keys: string[]): Promise<number> {
    return this.executeWithRetry(() => this.masterClient.hdel(name, ...keys));
  }

  // ───────────────────────────────────────────────────────────────────────
  // List Operations
  // ───────────────────────────────────────────────────────────────────────

  /**
   * إضافة عناصر في بداية القائمة
   */
  async lpush(name: string, ...values: (string | number)[]): Promise<number> {
    return this.executeWithRetry(() => this.masterClient.lpush(name, ...values));
  }

  /**
   * إضافة عناصر في نهاية القائمة
   */
  async rpush(name: string, ...values: (string | number)[]): Promise<number> {
    return this.executeWithRetry(() => this.masterClient.rpush(name, ...values));
  }

  /**
   * إزالة وإرجاع أول عنصر
   */
  async lpop(name: string): Promise<string | null> {
    return this.executeWithRetry(() => this.masterClient.lpop(name));
  }

  /**
   * إزالة وإرجاع آخر عنصر
   */
  async rpop(name: string): Promise<string | null> {
    return this.executeWithRetry(() => this.masterClient.rpop(name));
  }

  /**
   * الحصول على نطاق من القائمة
   */
  async lrange(
    name: string,
    start: number,
    end: number,
    useSlave: boolean = true
  ): Promise<string[]> {
    const client = useSlave ? this.slaveClient : this.masterClient;
    return this.executeWithRetry(() => client.lrange(name, start, end));
  }

  // ───────────────────────────────────────────────────────────────────────
  // Set Operations
  // ───────────────────────────────────────────────────────────────────────

  /**
   * إضافة عناصر إلى مجموعة
   */
  async sadd(name: string, ...values: (string | number)[]): Promise<number> {
    return this.executeWithRetry(() => this.masterClient.sadd(name, ...values));
  }

  /**
   * الحصول على جميع عناصر المجموعة
   */
  async smembers(name: string, useSlave: boolean = true): Promise<string[]> {
    const client = useSlave ? this.slaveClient : this.masterClient;
    return this.executeWithRetry(() => client.smembers(name));
  }

  /**
   * إزالة عناصر من مجموعة
   */
  async srem(name: string, ...values: (string | number)[]): Promise<number> {
    return this.executeWithRetry(() => this.masterClient.srem(name, ...values));
  }

  // ───────────────────────────────────────────────────────────────────────
  // Sorted Set Operations
  // ───────────────────────────────────────────────────────────────────────

  /**
   * إضافة عناصر إلى مجموعة مرتبة
   */
  async zadd(
    name: string,
    ...args: (string | number)[]
  ): Promise<number | string> {
    return this.executeWithRetry(() => this.masterClient.zadd(name, ...args));
  }

  /**
   * الحصول على نطاق من المجموعة المرتبة
   */
  async zrange(
    name: string,
    start: number,
    end: number,
    withScores: boolean = false,
    useSlave: boolean = true
  ): Promise<string[]> {
    const client = useSlave ? this.slaveClient : this.masterClient;
    const args: any[] = [name, start, end];
    if (withScores) args.push('WITHSCORES');
    return this.executeWithRetry(() => client.zrange(...args));
  }

  /**
   * إزالة عناصر من مجموعة مرتبة
   */
  async zrem(name: string, ...values: (string | number)[]): Promise<number> {
    return this.executeWithRetry(() => this.masterClient.zrem(name, ...values));
  }

  // ───────────────────────────────────────────────────────────────────────
  // Pipeline Operations
  // ───────────────────────────────────────────────────────────────────────

  /**
   * إنشاء Pipeline لتنفيذ عمليات متعددة
   *
   * @example
   * const pipeline = client.pipeline();
   * pipeline.set('key1', 'value1');
   * pipeline.set('key2', 'value2');
   * await pipeline.exec();
   */
  pipeline() {
    return this.masterClient.pipeline();
  }

  /**
   * إنشاء Multi/Transaction
   */
  multi() {
    return this.masterClient.multi();
  }

  // ───────────────────────────────────────────────────────────────────────
  // Health & Monitoring
  // ───────────────────────────────────────────────────────────────────────

  /**
   * فحص الاتصال
   */
  async ping(): Promise<boolean> {
    try {
      const result = await this.masterClient.ping();
      return result === 'PONG';
    } catch (error) {
      console.error('Ping failed:', error);
      return false;
    }
  }

  /**
   * الحصول على معلومات Redis
   */
  async info(section?: string): Promise<string> {
    try {
      return section
        ? await this.masterClient.info(section)
        : await this.masterClient.info();
    } catch (error) {
      console.error('Failed to get info:', error);
      return '';
    }
  }

  /**
   * الحصول على معلومات Sentinel
   */
  async getSentinelInfo(): Promise<SentinelInfo> {
    try {
      const sentinelNodes = await this.masterClient.sentinelSentinels(
        this.config.masterName
      );

      const masterNode = await this.masterClient.sentinelMaster(
        this.config.masterName
      );

      const slaveNodes = await this.masterClient.sentinelSlaves(
        this.config.masterName
      );

      return {
        master: masterNode
          ? { host: masterNode.ip, port: parseInt(masterNode.port) }
          : null,
        slaves: slaveNodes.map((slave: any) => ({
          host: slave.ip,
          port: parseInt(slave.port),
        })),
        masterName: this.config.masterName,
        sentinelCount: this.config.sentinels.length,
        isConnected: await this.ping(),
        circuitBreakerState: this.circuitBreaker.getState(),
      };
    } catch (error) {
      console.error('Failed to get sentinel info:', error);
      throw error;
    }
  }

  /**
   * فحص صحة شامل
   */
  async healthCheck(): Promise<HealthCheckResult> {
    const health: HealthCheckResult = {
      status: 'healthy',
      timestamp: Date.now(),
      checks: {},
    };

    // Check master connection
    try {
      health.checks.masterPing = await this.ping();
      if (!health.checks.masterPing) {
        health.status = 'unhealthy';
      }
    } catch (error) {
      health.checks.masterPing = false;
      health.status = 'unhealthy';
      health.error = (error as Error).message;
    }

    // Check sentinel
    try {
      health.checks.sentinelInfo = await this.getSentinelInfo();
    } catch (error) {
      health.status = 'degraded';
    }

    // Check circuit breaker
    health.checks.circuitBreaker = this.circuitBreaker.getState();
    if (this.circuitBreaker.getState() === CircuitBreakerState.OPEN) {
      health.status = 'degraded';
    }

    return health;
  }

  /**
   * إغلاق جميع الاتصالات
   */
  async close(): Promise<void> {
    try {
      await Promise.all([this.masterClient.quit(), this.slaveClient.quit()]);
      console.log('Redis connections closed');
    } catch (error) {
      console.error('Error closing connections:', error);
      // Force disconnect
      this.masterClient.disconnect();
      this.slaveClient.disconnect();
    }
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Factory Function
// ═══════════════════════════════════════════════════════════════════════════

let redisClientInstance: RedisSentinelClient | null = null;

/**
 * الحصول على Redis Client (Singleton)
 */
export function getRedisSentinelClient(
  config?: RedisSentinelConfig
): RedisSentinelClient {
  if (!redisClientInstance) {
    const defaultConfig: RedisSentinelConfig = {
      sentinels: [
        { host: process.env.REDIS_SENTINEL_HOST_1 || 'localhost', port: 26379 },
        { host: process.env.REDIS_SENTINEL_HOST_2 || 'localhost', port: 26380 },
        { host: process.env.REDIS_SENTINEL_HOST_3 || 'localhost', port: 26381 },
      ],
      masterName: process.env.REDIS_MASTER_NAME || 'sahool-master',
      password: process.env.REDIS_PASSWORD,
      db: parseInt(process.env.REDIS_DB || '0'),
    };

    redisClientInstance = new RedisSentinelClient(config || defaultConfig);
  }

  return redisClientInstance;
}

/**
 * إغلاق Redis Client
 */
export async function closeRedisSentinelClient(): Promise<void> {
  if (redisClientInstance) {
    await redisClientInstance.close();
    redisClientInstance = null;
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Export Default
// ═══════════════════════════════════════════════════════════════════════════

export default RedisSentinelClient;
