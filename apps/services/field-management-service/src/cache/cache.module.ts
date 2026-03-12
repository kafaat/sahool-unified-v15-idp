/**
 * Cache Module - Redis Caching Layer for Field Management
 * Gracefully falls back to in-memory cache if Redis is unavailable
 */

import { Module, Global, Logger } from "@nestjs/common";
import { CacheModule as NestCacheModule } from "@nestjs/cache-manager";
import { CacheService } from "./cache.service";

const logger = new Logger("CacheModule");

// Check if we should skip Redis connection
const isTestEnvironment = ["test", "ci", "testing"].includes(
  (process.env.ENVIRONMENT || process.env.NODE_ENV || "").toLowerCase()
);
const hasRedisUrl = !!process.env.REDIS_URL;

@Global()
@Module({
  imports: [
    NestCacheModule.registerAsync({
      isGlobal: true,
      useFactory: async () => {
        // Skip Redis connection if no URL provided or in test/CI environment
        if (!hasRedisUrl || isTestEnvironment) {
          logger.warn(
            isTestEnvironment
              ? "Running in test environment, using in-memory cache"
              : "REDIS_URL not configured, using in-memory cache"
          );
          return {
            ttl: 300000, // 5 minutes default TTL
          };
        }

        try {
          const redisUrl = process.env.REDIS_URL!;
          const url = new URL(redisUrl);
          const password = url.password || process.env.REDIS_PASSWORD;

          // Dynamically import redis store to avoid connection during module load
          const { redisStore } = await import("cache-manager-redis-yet");

          logger.log(`Connecting to Redis at ${url.hostname}:${url.port || 6379}`);

          return {
            store: redisStore,
            socket: {
              host: url.hostname,
              port: parseInt(url.port) || 6379,
              connectTimeout: 5000, // 5 second connection timeout
              reconnectStrategy: (retries: number) => {
                if (retries > 10) {
                  // For node-redis's socket.reconnectStrategy, this sets an upper bound
                  // on the backoff interval so the service gradually recovers without thrashing.
                  if (retries === 11) {
                    // Log only once when entering the capped-backoff regime to avoid
                    // flooding logs during a long Redis outage (every 30 s indefinitely).
                    logger.warn("Redis reconnect: entering slow-retry mode (30 s intervals)");
                  }
                  return 30000; // 30 s – keep retrying but slowly
                }
                return Math.min(retries * 1000, 5000); // backoff up to 5 s
              },
            },
            password: password || undefined,
            ttl: 300000, // 5 minutes default TTL
            prefix: "field-mgmt:",
          };
        } catch (error) {
          // Fallback to in-memory cache if Redis connection fails
          logger.warn(`Redis initialization failed: ${error instanceof Error ? error.message : "unknown error"}, using in-memory cache`);
          return {
            ttl: 300000,
          };
        }
      },
    }),
  ],
  providers: [CacheService],
  exports: [CacheService, NestCacheModule],
})
export class CacheModule {}
