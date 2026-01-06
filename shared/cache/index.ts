/**
 * SAHOOL Platform - Cache Module
 * ==============================
 * 
 * Main entry point for the advanced caching module
 */

// Core cache manager
export {
  CacheManager,
  CacheConfig,
  CacheMetrics,
  CacheEntry,
  CacheWarmingOptions,
  CacheTTL,
  getCacheManager,
  resetCacheManager,
} from './cache-manager';

// Metrics service
export {
  CacheMetricsService,
  DetailedCacheMetrics,
  CacheHealthStatus,
} from './cache-metrics.service';

// Cache warming service
export {
  CacheWarmingService,
  WarmingStrategy,
  createUserWarmingStrategy,
  createFieldWarmingStrategy,
  createPredictiveWarmingStrategy,
} from './cache-warming.service';

// Redis Sentinel client
export {
  RedisSentinelClient,
  RedisSentinelConfig,
  HealthCheckResult,
  SentinelInfo,
  getRedisSentinelClient,
  closeRedisSentinelClient,
} from './redis-sentinel';

// Re-export for convenience
export { default as RedisSentinel } from './redis-sentinel';
