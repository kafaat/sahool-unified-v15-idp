/**
 * Rate Limiting Guard for NestJS Authentication
 * حارس تحديد المعدل للمصادقة
 *
 * Provides rate limiting functionality to protect authentication endpoints
 * from brute force attacks and abuse.
 *
 * SECURITY: Rate limiting is critical for preventing brute force attacks
 * on authentication endpoints.
 */

import {
  Injectable,
  CanActivate,
  ExecutionContext,
  HttpException,
  HttpStatus,
  Logger,
  SetMetadata,
} from "@nestjs/common";
import { Reflector } from "@nestjs/core";
import { JWTConfig, AuthErrors } from "../config/jwt.config";

/**
 * Rate limit configuration for a route
 */
export interface RateLimitConfig {
  /** Maximum requests allowed in the time window */
  limit: number;
  /** Time window in seconds */
  windowSeconds: number;
  /** Key prefix for rate limit tracking */
  keyPrefix?: string;
  /** Use user ID instead of IP for rate limiting (requires authentication) */
  byUser?: boolean;
  /** Skip rate limiting for certain conditions */
  skip?: (request: any) => boolean;
}

/**
 * Default rate limit tiers
 */
export const RATE_LIMIT_TIERS = {
  /** Strict - for sensitive endpoints like login */
  STRICT: { limit: 5, windowSeconds: 60 },
  /** Standard - for normal API endpoints */
  STANDARD: { limit: 60, windowSeconds: 60 },
  /** Relaxed - for read-only endpoints */
  RELAXED: { limit: 120, windowSeconds: 60 },
  /** Auth - specifically for authentication endpoints */
  AUTH: { limit: 10, windowSeconds: 300 },
} as const;

/**
 * Metadata key for rate limit configuration
 */
export const RATE_LIMIT_KEY = "rateLimit";

/**
 * Rate Limit decorator
 *
 * Apply rate limiting to a route or controller
 *
 * @example
 * ```typescript
 * @Controller('auth')
 * export class AuthController {
 *   @Post('login')
 *   @RateLimit({ limit: 5, windowSeconds: 300 }) // 5 attempts per 5 minutes
 *   login(@Body() dto: LoginDto) {
 *     return this.authService.login(dto);
 *   }
 *
 *   @Post('refresh')
 *   @RateLimit(RATE_LIMIT_TIERS.STANDARD)
 *   refresh(@Body() dto: RefreshDto) {
 *     return this.authService.refresh(dto);
 *   }
 * }
 * ```
 */
export const RateLimit = (config: RateLimitConfig) =>
  SetMetadata(RATE_LIMIT_KEY, config);

/**
 * In-memory rate limit store (for simple deployments)
 * For production, use Redis-based implementation
 */
class InMemoryRateLimitStore {
  private store: Map<string, { count: number; resetTime: number }> = new Map();
  private cleanupInterval: NodeJS.Timeout;

  constructor() {
    // Cleanup expired entries every minute
    this.cleanupInterval = setInterval(() => this.cleanup(), 60000);
  }

  async increment(key: string, windowSeconds: number): Promise<{ count: number; resetTime: number }> {
    const now = Date.now();
    const existing = this.store.get(key);

    if (existing && existing.resetTime > now) {
      // Within window - increment count
      existing.count++;
      return existing;
    }

    // New window
    const entry = {
      count: 1,
      resetTime: now + windowSeconds * 1000,
    };
    this.store.set(key, entry);
    return entry;
  }

  private cleanup(): void {
    const now = Date.now();
    for (const [key, value] of this.store.entries()) {
      if (value.resetTime <= now) {
        this.store.delete(key);
      }
    }
  }

  destroy(): void {
    clearInterval(this.cleanupInterval);
    this.store.clear();
  }
}

/**
 * Redis-based rate limit store
 */
export class RedisRateLimitStore {
  constructor(private readonly redis: any) {}

  async increment(key: string, windowSeconds: number): Promise<{ count: number; resetTime: number }> {
    const now = Date.now();
    const redisKey = `ratelimit:${key}`;

    // Use Redis MULTI for atomic increment with expiry
    const multi = this.redis.multi();
    multi.incr(redisKey);
    multi.pttl(redisKey);

    const results = await multi.exec();
    const count = results[0][1] as number;
    const ttl = results[1][1] as number;

    // Set expiry if this is the first request in window
    if (ttl === -1) {
      await this.redis.pexpire(redisKey, windowSeconds * 1000);
    }

    return {
      count,
      resetTime: ttl > 0 ? now + ttl : now + windowSeconds * 1000,
    };
  }
}

/**
 * Rate Limit Guard
 *
 * Implements rate limiting based on decorator configuration or defaults.
 *
 * @example
 * ```typescript
 * @Module({
 *   providers: [
 *     {
 *       provide: APP_GUARD,
 *       useClass: RateLimitGuard,
 *     },
 *   ],
 * })
 * export class AppModule {}
 * ```
 */
@Injectable()
export class RateLimitGuard implements CanActivate {
  private readonly logger = new Logger(RateLimitGuard.name);
  private readonly store: InMemoryRateLimitStore;
  private redisStore?: RedisRateLimitStore;

  constructor(private readonly reflector: Reflector) {
    this.store = new InMemoryRateLimitStore();
  }

  /**
   * Set Redis client for distributed rate limiting
   */
  setRedisClient(redis: any): void {
    this.redisStore = new RedisRateLimitStore(redis);
  }

  async canActivate(context: ExecutionContext): Promise<boolean> {
    // Check if rate limiting is enabled globally
    if (!JWTConfig.RATE_LIMIT_ENABLED) {
      return true;
    }

    const request = context.switchToHttp().getRequest();

    // Get rate limit config from decorator or use defaults
    const config = this.reflector.getAllAndOverride<RateLimitConfig>(
      RATE_LIMIT_KEY,
      [context.getHandler(), context.getClass()],
    );

    // Use default config if not specified
    const limit = config?.limit || JWTConfig.RATE_LIMIT_REQUESTS;
    const windowSeconds = config?.windowSeconds || JWTConfig.RATE_LIMIT_WINDOW_SECONDS;
    const keyPrefix = config?.keyPrefix || "default";
    const byUser = config?.byUser || false;

    // Check skip condition
    if (config?.skip && config.skip(request)) {
      return true;
    }

    // Generate rate limit key
    const key = this.generateKey(request, keyPrefix, byUser);

    try {
      // Use Redis store if available, otherwise in-memory
      const store = this.redisStore || this.store;
      const result = await store.increment(key, windowSeconds);

      // Set rate limit headers
      const response = context.switchToHttp().getResponse();
      response.setHeader("X-RateLimit-Limit", limit);
      response.setHeader("X-RateLimit-Remaining", Math.max(0, limit - result.count));
      response.setHeader("X-RateLimit-Reset", Math.ceil(result.resetTime / 1000));

      if (result.count > limit) {
        this.logger.warn(
          `Rate limit exceeded for ${key}: ${result.count}/${limit} requests`,
        );

        const retryAfter = Math.ceil((result.resetTime - Date.now()) / 1000);
        response.setHeader("Retry-After", retryAfter);

        throw new HttpException(
          {
            statusCode: HttpStatus.TOO_MANY_REQUESTS,
            error: AuthErrors.RATE_LIMIT_EXCEEDED.code,
            message: AuthErrors.RATE_LIMIT_EXCEEDED.en,
            messageAr: AuthErrors.RATE_LIMIT_EXCEEDED.ar,
            retryAfter,
          },
          HttpStatus.TOO_MANY_REQUESTS,
        );
      }

      return true;
    } catch (error) {
      if (error instanceof HttpException) {
        throw error;
      }

      // Log error but allow request (fail open for rate limiting)
      // This prevents rate limiting failures from blocking legitimate requests
      this.logger.error(`Rate limit check failed: ${error.message}`);
      return true;
    }
  }

  /**
   * Generate rate limit key from request
   */
  private generateKey(request: any, prefix: string, byUser: boolean): string {
    // By user (requires authentication)
    if (byUser && request.user?.id) {
      return `${prefix}:user:${request.user.id}`;
    }

    // By IP address
    const ip =
      request.ip ||
      request.headers?.["x-forwarded-for"]?.split(",")[0] ||
      request.connection?.remoteAddress ||
      "unknown";

    // Include path for more granular rate limiting
    const path = request.url?.split("?")[0] || "";

    return `${prefix}:ip:${ip}:${path}`;
  }

  /**
   * Cleanup on module destroy
   */
  onModuleDestroy(): void {
    this.store.destroy();
  }
}

/**
 * Skip Rate Limit decorator
 *
 * Skip rate limiting for specific routes
 *
 * @example
 * ```typescript
 * @Controller('health')
 * export class HealthController {
 *   @Get()
 *   @SkipRateLimit()
 *   health() {
 *     return { status: 'ok' };
 *   }
 * }
 * ```
 */
export const SkipRateLimit = () => SetMetadata("skipRateLimit", true);
