/**
 * SAHOOL Services - Rate Limiting Middleware for Express/TypeScript
 * ميدلوير التحكم في معدل الطلبات
 *
 * Provides Redis-backed distributed rate limiting for Express services with:
 * - Per-endpoint type rate limits (auth, read, write)
 * - Redis-backed distributed rate limiting
 * - Automatic 429 responses with Retry-After header
 * - Rate limit headers (X-RateLimit-*)
 *
 * Version: 1.0.0
 * Created: 2025
 */

import { Request, Response, NextFunction } from 'express';
import { createClient, RedisClientType } from 'redis';

// ═══════════════════════════════════════════════════════════════════════════════
// Types & Interfaces
// ═══════════════════════════════════════════════════════════════════════════════

export enum EndpointType {
    AUTH = 'auth',
    READ = 'read',
    WRITE = 'write',
    HEALTH = 'health'
}

export interface RateLimitConfig {
    requestsPerMinute: number;
    windowMs: number;
}

export interface RateLimitOptions {
    redis?: {
        url: string;
        keyPrefix?: string;
    };
    skipPaths?: string[];
    keyGenerator?: (req: Request) => string;
    endpointTypeDetector?: (req: Request) => EndpointType;
    onLimitReached?: (req: Request, res: Response) => void;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Default Configurations
// ═══════════════════════════════════════════════════════════════════════════════

const DEFAULT_RATE_LIMITS: Record<EndpointType, RateLimitConfig> = {
    [EndpointType.AUTH]: {
        requestsPerMinute: 5,
        windowMs: 60000 // 1 minute
    },
    [EndpointType.READ]: {
        requestsPerMinute: 100,
        windowMs: 60000
    },
    [EndpointType.WRITE]: {
        requestsPerMinute: 30,
        windowMs: 60000
    },
    [EndpointType.HEALTH]: {
        requestsPerMinute: 1000, // Very high limit for health checks
        windowMs: 60000
    }
};

// ═══════════════════════════════════════════════════════════════════════════════
// Redis Rate Limiter
// ═══════════════════════════════════════════════════════════════════════════════

export class RedisRateLimiter {
    private client: RedisClientType | null = null;
    private readonly keyPrefix: string;
    private connected: boolean = false;

    constructor(redisUrl?: string, keyPrefix: string = 'ratelimit:') {
        this.keyPrefix = keyPrefix;

        if (redisUrl) {
            this.initRedis(redisUrl);
        }
    }

    private async initRedis(url: string): Promise<void> {
        try {
            this.client = createClient({
                url,
                socket: {
                    reconnectStrategy: (retries) => {
                        if (retries > 10) {
                            console.error('Redis reconnect failed after 10 attempts');
                            return new Error('Redis connection failed');
                        }
                        return Math.min(retries * 100, 3000);
                    }
                }
            });

            this.client.on('error', (err) => {
                console.error('Redis Client Error:', err);
                this.connected = false;
            });

            this.client.on('connect', () => {
                console.log('✅ Redis rate limiter connected');
                this.connected = true;
            });

            this.client.on('disconnect', () => {
                console.warn('⚠️  Redis rate limiter disconnected');
                this.connected = false;
            });

            await this.client.connect();
        } catch (error) {
            console.error('Failed to initialize Redis for rate limiting:', error);
            this.client = null;
            this.connected = false;
        }
    }

    async checkLimit(
        key: string,
        config: RateLimitConfig
    ): Promise<{ allowed: boolean; remaining: number; resetTime: number }> {
        // If Redis is not connected, allow the request (fail open)
        if (!this.client || !this.connected) {
            console.warn('Redis not available, allowing request');
            return {
                allowed: true,
                remaining: config.requestsPerMinute,
                resetTime: Math.ceil(config.windowMs / 1000)
            };
        }

        const redisKey = `${this.keyPrefix}${key}`;
        const now = Date.now();
        const windowStart = now - config.windowMs;

        try {
            // Use Redis sorted set with sliding window algorithm
            const multi = this.client.multi();

            // Remove old entries outside the window
            multi.zRemRangeByScore(redisKey, 0, windowStart);

            // Count current requests in the window
            multi.zCard(redisKey);

            // Add current request timestamp
            multi.zAdd(redisKey, { score: now, value: `${now}` });

            // Set expiry on the key (2x window to account for clock skew)
            multi.expire(redisKey, Math.ceil(config.windowMs * 2 / 1000));

            const results = await multi.exec();

            // results[1] contains the count before adding current request
            const currentCount = results[1] as number;
            const remaining = Math.max(0, config.requestsPerMinute - currentCount - 1);
            const allowed = currentCount < config.requestsPerMinute;

            // If not allowed, remove the request we just added
            if (!allowed) {
                await this.client.zRem(redisKey, `${now}`);
            }

            return {
                allowed,
                remaining,
                resetTime: Math.ceil(config.windowMs / 1000)
            };
        } catch (error) {
            console.error('Redis rate limit check failed:', error);
            // Fail open - allow the request if Redis has issues
            return {
                allowed: true,
                remaining: config.requestsPerMinute,
                resetTime: Math.ceil(config.windowMs / 1000)
            };
        }
    }

    async disconnect(): Promise<void> {
        if (this.client) {
            await this.client.quit();
            this.connected = false;
        }
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Express Middleware
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Default key generator - uses client IP address
 */
const defaultKeyGenerator = (req: Request): string => {
    const forwarded = req.headers['x-forwarded-for'];
    const ip = forwarded
        ? (Array.isArray(forwarded) ? forwarded[0] : forwarded.split(',')[0]).trim()
        : req.ip || req.socket.remoteAddress || 'unknown';
    return ip;
};

/**
 * Default endpoint type detector based on HTTP method and path
 */
const defaultEndpointTypeDetector = (req: Request): EndpointType => {
    const path = req.path.toLowerCase();

    // Health check endpoints
    if (path.includes('/health') || path.includes('/ready') || path.includes('/live')) {
        return EndpointType.HEALTH;
    }

    // Auth endpoints
    if (path.includes('/auth') || path.includes('/login') || path.includes('/register') ||
        path.includes('/token') || path.includes('/password')) {
        return EndpointType.AUTH;
    }

    // Write endpoints
    if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(req.method)) {
        return EndpointType.WRITE;
    }

    // Default to read
    return EndpointType.READ;
};

/**
 * Create rate limiting middleware for Express
 */
export function createRateLimiter(options: RateLimitOptions = {}) {
    const {
        redis,
        skipPaths = ['/healthz', '/readyz', '/livez', '/metrics'],
        keyGenerator = defaultKeyGenerator,
        endpointTypeDetector = defaultEndpointTypeDetector,
        onLimitReached
    } = options;

    // Initialize Redis rate limiter
    const limiter = new RedisRateLimiter(
        redis?.url || process.env.REDIS_URL,
        redis?.keyPrefix
    );

    return async (req: Request, res: Response, next: NextFunction) => {
        try {
            // Skip certain paths
            if (skipPaths.some(path => req.path.startsWith(path))) {
                return next();
            }

            // Determine endpoint type and get rate limit config
            const endpointType = endpointTypeDetector(req);
            const config = DEFAULT_RATE_LIMITS[endpointType];

            // Generate unique key for this client/endpoint
            const clientKey = keyGenerator(req);
            const rateLimitKey = `${endpointType}:${clientKey}`;

            // Check rate limit
            const { allowed, remaining, resetTime } = await limiter.checkLimit(
                rateLimitKey,
                config
            );

            // Add rate limit headers
            res.setHeader('X-RateLimit-Limit', config.requestsPerMinute.toString());
            res.setHeader('X-RateLimit-Remaining', remaining.toString());
            res.setHeader('X-RateLimit-Reset', resetTime.toString());

            if (!allowed) {
                // Add Retry-After header
                res.setHeader('Retry-After', resetTime.toString());

                // Call custom handler if provided
                if (onLimitReached) {
                    onLimitReached(req, res);
                }

                // Log rate limit hit
                console.warn(`⚠️  Rate limit exceeded: ${endpointType} - ${clientKey}`);

                return res.status(429).json({
                    success: false,
                    error: 'rate_limit_exceeded',
                    error_ar: 'تم تجاوز حد المعدل',
                    message: 'Too many requests. Please slow down.',
                    message_ar: 'عدد كبير جدًا من الطلبات. يرجى التباطؤ.',
                    retryAfter: resetTime,
                    limit: config.requestsPerMinute,
                    endpointType
                });
            }

            // Request allowed, continue
            next();
        } catch (error) {
            // Log error but allow request to proceed (fail open)
            console.error('Rate limiter error:', error);
            next();
        }
    };
}

/**
 * Middleware factory with custom rate limits
 */
export function createCustomRateLimiter(
    customLimits: Partial<Record<EndpointType, RateLimitConfig>>,
    options: RateLimitOptions = {}
) {
    // Merge custom limits with defaults
    const mergedLimits = { ...DEFAULT_RATE_LIMITS, ...customLimits };

    const {
        redis,
        skipPaths = ['/healthz', '/readyz', '/livez', '/metrics'],
        keyGenerator = defaultKeyGenerator,
        endpointTypeDetector = defaultEndpointTypeDetector,
        onLimitReached
    } = options;

    const limiter = new RedisRateLimiter(
        redis?.url || process.env.REDIS_URL,
        redis?.keyPrefix
    );

    return async (req: Request, res: Response, next: NextFunction) => {
        try {
            if (skipPaths.some(path => req.path.startsWith(path))) {
                return next();
            }

            const endpointType = endpointTypeDetector(req);
            const config = mergedLimits[endpointType];

            const clientKey = keyGenerator(req);
            const rateLimitKey = `${endpointType}:${clientKey}`;

            const { allowed, remaining, resetTime } = await limiter.checkLimit(
                rateLimitKey,
                config
            );

            res.setHeader('X-RateLimit-Limit', config.requestsPerMinute.toString());
            res.setHeader('X-RateLimit-Remaining', remaining.toString());
            res.setHeader('X-RateLimit-Reset', resetTime.toString());

            if (!allowed) {
                res.setHeader('Retry-After', resetTime.toString());

                if (onLimitReached) {
                    onLimitReached(req, res);
                }

                console.warn(`⚠️  Rate limit exceeded: ${endpointType} - ${clientKey}`);

                return res.status(429).json({
                    success: false,
                    error: 'rate_limit_exceeded',
                    error_ar: 'تم تجاوز حد المعدل',
                    message: 'Too many requests. Please slow down.',
                    message_ar: 'عدد كبير جدًا من الطلبات. يرجى التباطؤ.',
                    retryAfter: resetTime,
                    limit: config.requestsPerMinute,
                    endpointType
                });
            }

            next();
        } catch (error) {
            console.error('Rate limiter error:', error);
            next();
        }
    };
}

// ═══════════════════════════════════════════════════════════════════════════════
// Exports
// ═══════════════════════════════════════════════════════════════════════════════

export default createRateLimiter;
