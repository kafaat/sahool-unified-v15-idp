/**
 * Cache Module - Redis Caching Layer for Marketplace
 */

import { Module, Global } from "@nestjs/common";
import { CacheModule as NestCacheModule } from "@nestjs/cache-manager";
import { redisStore } from "cache-manager-redis-yet";
import { CacheService } from "./cache.service";

@Global()
@Module({
  imports: [
    NestCacheModule.registerAsync({
      useFactory: async () => {
        const redisUrl = process.env.REDIS_URL || "redis://localhost:6379";

        try {
          const url = new URL(redisUrl);
          const password = url.password || process.env.REDIS_PASSWORD;

          return {
            store: redisStore,
            socket: {
              host: url.hostname,
              port: parseInt(url.port) || 6379,
            },
            password: password || undefined,
            ttl: 300000, // 5 minutes default TTL
            prefix: "marketplace:",
          };
        } catch {
          // Fallback to in-memory cache if Redis URL is invalid
          console.warn("Invalid REDIS_URL, using in-memory cache");
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
