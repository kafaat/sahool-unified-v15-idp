/**
 * SAHOOL Database Connection Pool Configuration
 * تكوين تجمع اتصالات قاعدة البيانات سهول
 *
 * This module provides optimized database connection pool configurations
 * for different service types and deployment environments.
 *
 * هذه الوحدة توفر تكوينات محسنة لتجمع اتصالات قاعدة البيانات
 * لأنواع الخدمات المختلفة وبيئات النشر المختلفة.
 */

/**
 * Environment types for connection pool optimization
 * أنواع البيئات لتحسين تجمع الاتصالات
 */
export type Environment = 'development' | 'staging' | 'production';

/**
 * Service types with different connection requirements
 * أنواع الخدمات مع متطلبات اتصال مختلفة
 */
export type ServiceType =
  | 'api'          // Standard API services
  | 'background'   // Background workers
  | 'sync'         // Sync/batch operations
  | 'analytics'    // Read-heavy analytics
  | 'realtime';    // WebSocket/real-time

/**
 * Connection pool configuration interface
 * واجهة تكوين تجمع الاتصالات
 */
export interface PoolConfig {
  /** Minimum number of connections in pool / الحد الأدنى للاتصالات */
  minConnections: number;
  /** Maximum number of connections in pool / الحد الأقصى للاتصالات */
  maxConnections: number;
  /** Timeout for acquiring connection (ms) / مهلة الحصول على اتصال */
  connectionTimeout: number;
  /** Idle timeout before connection is released (ms) / مهلة الخمول */
  idleTimeout: number;
  /** Maximum lifetime of a connection (ms) / الحد الأقصى لعمر الاتصال */
  maxLifetime: number;
  /** Connection reuse time (ms) / وقت إعادة استخدام الاتصال */
  reuseTimeout: number;
  /** Enable statement caching / تفعيل تخزين البيانات المؤقت */
  statementCacheSize: number;
  /** Pool health check interval (ms) / فترة فحص صحة التجمع */
  healthCheckInterval: number;
}

/**
 * PgBouncer-specific configuration
 * تكوين خاص بـ PgBouncer
 */
export interface PgBouncerConfig {
  /** Pool mode: session, transaction, or statement */
  poolMode: 'session' | 'transaction' | 'statement';
  /** Maximum client connections per pool */
  maxClientConnections: number;
  /** Default pool size per database */
  defaultPoolSize: number;
  /** Reserve pool size */
  reservePoolSize: number;
  /** Reserve pool timeout */
  reservePoolTimeout: number;
  /** Server idle timeout */
  serverIdleTimeout: number;
  /** Query timeout */
  queryTimeout: number;
}

/**
 * Default connection pool configurations by service type
 * تكوينات تجمع الاتصالات الافتراضية حسب نوع الخدمة
 */
export const SERVICE_POOL_CONFIGS: Record<ServiceType, PoolConfig> = {
  api: {
    minConnections: 2,
    maxConnections: 10,
    connectionTimeout: 10000,    // 10 seconds
    idleTimeout: 60000,          // 1 minute
    maxLifetime: 3600000,        // 1 hour
    reuseTimeout: 30000,         // 30 seconds
    statementCacheSize: 100,
    healthCheckInterval: 30000,  // 30 seconds
  },
  background: {
    minConnections: 1,
    maxConnections: 5,
    connectionTimeout: 30000,    // 30 seconds
    idleTimeout: 120000,         // 2 minutes
    maxLifetime: 7200000,        // 2 hours
    reuseTimeout: 60000,         // 1 minute
    statementCacheSize: 50,
    healthCheckInterval: 60000,  // 1 minute
  },
  sync: {
    minConnections: 1,
    maxConnections: 3,
    connectionTimeout: 60000,    // 1 minute
    idleTimeout: 180000,         // 3 minutes
    maxLifetime: 7200000,        // 2 hours
    reuseTimeout: 120000,        // 2 minutes
    statementCacheSize: 200,
    healthCheckInterval: 60000,  // 1 minute
  },
  analytics: {
    minConnections: 2,
    maxConnections: 8,
    connectionTimeout: 30000,    // 30 seconds
    idleTimeout: 120000,         // 2 minutes
    maxLifetime: 3600000,        // 1 hour
    reuseTimeout: 60000,         // 1 minute
    statementCacheSize: 500,     // Large cache for analytics queries
    healthCheckInterval: 30000,  // 30 seconds
  },
  realtime: {
    minConnections: 3,
    maxConnections: 15,
    connectionTimeout: 5000,     // 5 seconds - fast timeout for real-time
    idleTimeout: 30000,          // 30 seconds
    maxLifetime: 1800000,        // 30 minutes
    reuseTimeout: 15000,         // 15 seconds
    statementCacheSize: 50,
    healthCheckInterval: 15000,  // 15 seconds
  },
};

/**
 * Environment-specific pool size multipliers
 * معاملات حجم التجمع حسب البيئة
 */
const ENVIRONMENT_MULTIPLIERS: Record<Environment, number> = {
  development: 0.5,  // Reduced connections for local development
  staging: 0.75,     // Moderate connections for staging
  production: 1.0,   // Full connections for production
};

/**
 * PgBouncer configuration by environment
 * تكوين PgBouncer حسب البيئة
 */
export const PGBOUNCER_CONFIGS: Record<Environment, PgBouncerConfig> = {
  development: {
    poolMode: 'transaction',
    maxClientConnections: 50,
    defaultPoolSize: 5,
    reservePoolSize: 2,
    reservePoolTimeout: 5,
    serverIdleTimeout: 600,
    queryTimeout: 120,
  },
  staging: {
    poolMode: 'transaction',
    maxClientConnections: 150,
    defaultPoolSize: 20,
    reservePoolSize: 5,
    reservePoolTimeout: 3,
    serverIdleTimeout: 300,
    queryTimeout: 60,
  },
  production: {
    poolMode: 'transaction',
    maxClientConnections: 500,
    defaultPoolSize: 50,
    reservePoolSize: 25,
    reservePoolTimeout: 2,
    serverIdleTimeout: 120,
    queryTimeout: 30,
  },
};

/**
 * Get optimized pool configuration for a service
 * الحصول على تكوين تجمع محسن للخدمة
 *
 * @param serviceType - Type of service
 * @param environment - Deployment environment
 * @returns Optimized pool configuration
 */
export function getPoolConfig(
  serviceType: ServiceType,
  environment: Environment = (process.env.NODE_ENV as Environment) || 'development'
): PoolConfig {
  const baseConfig = SERVICE_POOL_CONFIGS[serviceType];
  const multiplier = ENVIRONMENT_MULTIPLIERS[environment];

  return {
    ...baseConfig,
    minConnections: Math.max(1, Math.floor(baseConfig.minConnections * multiplier)),
    maxConnections: Math.max(2, Math.floor(baseConfig.maxConnections * multiplier)),
  };
}

/**
 * Build Prisma DATABASE_URL with connection pool parameters
 * بناء DATABASE_URL لـ Prisma مع معاملات تجمع الاتصالات
 *
 * @param baseUrl - Base database URL (without pool params)
 * @param config - Pool configuration
 * @returns URL with pool parameters
 */
export function buildDatabaseUrl(baseUrl: string, config: PoolConfig): string {
  const url = new URL(baseUrl);

  // Add connection pool parameters
  url.searchParams.set('connection_limit', String(config.maxConnections));
  url.searchParams.set('pool_timeout', String(Math.floor(config.connectionTimeout / 1000)));
  url.searchParams.set('connect_timeout', String(Math.floor(config.connectionTimeout / 1000)));

  // Ensure SSL is enabled
  if (!url.searchParams.has('sslmode')) {
    url.searchParams.set('sslmode', 'require');
  }

  return url.toString();
}

/**
 * Connection health metrics interface
 * واجهة مقاييس صحة الاتصال
 */
export interface ConnectionMetrics {
  totalConnections: number;
  activeConnections: number;
  idleConnections: number;
  waitingRequests: number;
  avgAcquireTime: number;
  avgQueryTime: number;
}

/**
 * Recommended Prisma configuration comments
 * تعليقات تكوين Prisma الموصى بها
 *
 * Add these to your Prisma schema datasource block:
 *
 * datasource db {
 *   provider   = "postgresql"
 *   url        = env("DATABASE_URL")
 *   directUrl  = env("DATABASE_URL_DIRECT")  // Bypasses PgBouncer for migrations
 * }
 *
 * DATABASE_URL should point to PgBouncer (port 6432):
 *   postgresql://user:pass@pgbouncer:6432/db?sslmode=disable&connection_limit=10
 *
 * DATABASE_URL_DIRECT should point directly to PostgreSQL (port 5432):
 *   postgresql://user:pass@postgres:5432/db?sslmode=require
 */

/**
 * Best practices for connection pooling
 * أفضل الممارسات لتجميع الاتصالات
 *
 * 1. Use PgBouncer in transaction mode for serverless/container environments
 *    استخدم PgBouncer في وضع المعاملات للبيئات بدون خادم/الحاويات
 *
 * 2. Set connection_limit lower than PgBouncer's default_pool_size
 *    اضبط connection_limit أقل من default_pool_size في PgBouncer
 *
 * 3. Use directUrl for migrations to avoid prepared statement issues
 *    استخدم directUrl للترحيلات لتجنب مشاكل البيانات المعدة
 *
 * 4. Monitor connection metrics with Prometheus
 *    راقب مقاييس الاتصال باستخدام Prometheus
 *
 * 5. Set appropriate timeouts based on your query patterns
 *    اضبط المهلات المناسبة بناءً على أنماط الاستعلام الخاصة بك
 *
 * 6. Use read replicas for analytics queries
 *    استخدم النسخ المتماثلة للقراءة لاستعلامات التحليلات
 *
 * 7. Enable SSL/TLS for all database connections
 *    فعّل SSL/TLS لجميع اتصالات قاعدة البيانات
 */

export default {
  getPoolConfig,
  buildDatabaseUrl,
  SERVICE_POOL_CONFIGS,
  PGBOUNCER_CONFIGS,
  ENVIRONMENT_MULTIPLIERS,
};
