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

          // Dynamically import to avoid loading Redis modules during module load
          const { createClient } = await import("redis");
          const { redisInsStore } = await import("cache-manager-redis-yet");

          logger.log(`Initializing Redis client for ${url.hostname}:${url.port || 6379}`);

          const redisClient = createClient({
            socket: {
              host: url.hostname,
              port: parseInt(url.port) || 6379,
              connectTimeout: 5000, // 5 second per-attempt timeout
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
            // Fail immediately instead of queuing when Redis is offline.
            // CacheService wraps every operation in try/catch so failures are
            // treated as cache misses, keeping the application fully functional.
            disableOfflineQueue: true,
          });

          // MUST attach error listener BEFORE connect() to prevent unhandled 'error' events
          // from crashing the Node.js process (EventEmitter throws if no listener).
          redisClient.on("error", (err: Error) => {
            logger.warn(`Redis client error: ${err.message}`);
          });

          // Fire-and-forget: start connecting in the background so that NestJS module
          // initialization completes immediately and /healthz can respond.
          // This mirrors the pattern used for DB connections in PrismaService.
          redisClient.connect().then(() => {
            logger.log(`Redis connected successfully at ${url.hostname}:${url.port || 6379}`);
          }).catch((err: Error) => {
            logger.warn(`Initial Redis connection attempt failed: ${err.message}. Background reconnection is active.`);
          });

          // Return a pre-built store object; @nestjs/cache-manager / cache-manager v5
          // accepts a non-function store directly (uses it as-is).
          //
          // The `as unknown as Parameters<typeof redisInsStore>[0]` cast bridges a
          // TypeScript type incompatibility: this workspace has two physical copies of
          // @redis/client (one at the root, one bundled inside cache-manager-redis-yet),
          // which makes their RedisClientType definitions nominally unrelated even
          // though they are structurally identical at runtime.
          return {
            store: redisInsStore(redisClient as unknown as Parameters<typeof redisInsStore>[0]),
            ttl: 300000, // 5 minutes default TTL
            prefix: "field-mgmt:",
          };
        } catch (error) {
          // Fallback to in-memory cache if Redis initialization fails
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
