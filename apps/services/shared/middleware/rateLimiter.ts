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
    trustedProxies?: string[]; // List of trusted proxy IPs
    failClosedForAuth?: boolean; // If true, reject AUTH requests when Redis fails (default: true)
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
// In-Memory Rate Limiter (Fallback)
// ═══════════════════════════════════════════════════════════════════════════════

interface RequestEntry {
    timestamp: number;
}

/**
 * Simple in-memory rate limiter using Map
 * Used as fallback when Redis is unavailable
 */
class InMemoryRateLimiter {
    private requests: Map<string, RequestEntry[]> = new Map();
    private cleanupInterval: NodeJS.Timeout;

    constructor() {
        // Cleanup expired entries every 60 seconds
        this.cleanupInterval = setInterval(() => {
            this.cleanup();
        }, 60000);
    }

    checkLimit(
        key: string,
        config: RateLimitConfig
    ): { allowed: boolean; remaining: number; resetTime: number } {
        const now = Date.now();
        const windowStart = now - config.windowMs;

        // Get existing requests for this key
        let entries = this.requests.get(key) || [];

        // Filter out expired entries (outside the window)
        entries = entries.filter(entry => entry.timestamp > windowStart);

        // Check if limit exceeded
        const currentCount = entries.length;
        const allowed = currentCount < config.requestsPerMinute;
        const remaining = Math.max(0, config.requestsPerMinute - currentCount - 1);

        if (allowed) {
            // Add current request
            entries.push({ timestamp: now });
            this.requests.set(key, entries);
        }

        return {
            allowed,
            remaining,
            resetTime: Math.ceil(config.windowMs / 1000)
        };
    }

    private cleanup(): void {
        const now = Date.now();
        const maxAge = 2 * 60000; // Keep entries for 2 minutes max

        for (const [key, entries] of this.requests.entries()) {
            // Remove entries older than maxAge
            const filtered = entries.filter(entry => now - entry.timestamp < maxAge);

            if (filtered.length === 0) {
                this.requests.delete(key);
            } else {
                this.requests.set(key, filtered);
            }
        }
    }

    destroy(): void {
        if (this.cleanupInterval) {
            clearInterval(this.cleanupInterval);
        }
        this.requests.clear();
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Redis Rate Limiter
// ═══════════════════════════════════════════════════════════════════════════════

export class RedisRateLimiter {
    private client: RedisClientType | null = null;
    private readonly keyPrefix: string;
    private connected: boolean = false;
    private inMemoryLimiter: InMemoryRateLimiter;
    private failClosedForAuth: boolean;

    constructor(
        redisUrl?: string,
        keyPrefix: string = 'ratelimit:',
        failClosedForAuth: boolean = true
    ) {
        this.keyPrefix = keyPrefix;
        this.failClosedForAuth = failClosedForAuth;
        this.inMemoryLimiter = new InMemoryRateLimiter();

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
        config: RateLimitConfig,
        endpointType?: EndpointType
    ): Promise<{ allowed: boolean; remaining: number; resetTime: number }> {
        // If Redis is not connected, use in-memory fallback
        if (!this.client || !this.connected) {
            console.warn('Redis not available, using in-memory rate limiter');

            // SECURITY: Fail-closed for AUTH endpoints
            if (this.failClosedForAuth && endpointType === EndpointType.AUTH) {
                console.error('Redis unavailable - rejecting AUTH request (fail-closed)');
                return {
                    allowed: false,
                    remaining: 0,
                    resetTime: Math.ceil(config.windowMs / 1000)
                };
            }

            // Use in-memory fallback for other endpoints
            return this.inMemoryLimiter.checkLimit(key, config);
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

            // SECURITY: Fail-closed for AUTH endpoints
            if (this.failClosedForAuth && endpointType === EndpointType.AUTH) {
                console.error('Redis error - rejecting AUTH request (fail-closed)');
                return {
                    allowed: false,
                    remaining: 0,
                    resetTime: Math.ceil(config.windowMs / 1000)
                };
            }

            // Use in-memory fallback for other endpoints
            console.warn('Using in-memory rate limiter due to Redis error');
            return this.inMemoryLimiter.checkLimit(key, config);
        }
    }

    async disconnect(): Promise<void> {
        if (this.client) {
            await this.client.quit();
            this.connected = false;
        }
        this.inMemoryLimiter.destroy();
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Express Middleware
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Default key generator - uses client IP address
 * SECURITY: Does NOT use X-Forwarded-For without trusted proxy validation
 */
const defaultKeyGenerator = (req: Request): string => {
    // Use direct connection IP (safe default)
    return req.ip || req.socket.remoteAddress || 'unknown';
};

/**
 * Create a key generator with trusted proxy support
 * @param trustedProxies List of trusted proxy IPs (e.g., load balancer IPs)
 */
const createKeyGeneratorWithProxySupport = (trustedProxies: string[] = []) => {
    return (req: Request): string => {
        // Get the direct connection IP
        const directIp = req.socket.remoteAddress || 'unknown';

        // Only trust X-Forwarded-For if the direct connection is from a trusted proxy
        if (trustedProxies.length > 0 && trustedProxies.includes(directIp)) {
            const forwarded = req.headers['x-forwarded-for'];
            if (forwarded) {
                // Get the leftmost IP (client's real IP)
                const clientIp = Array.isArray(forwarded)
                    ? forwarded[0]
                    : forwarded.split(',')[0];
                return clientIp.trim();
            }
        }

        // Fallback to direct IP (safe default)
        return req.ip || directIp;
    };
};


/**
 * Normalize and sanitize path to prevent traversal attacks
 * Removes ../, ./, and duplicate slashes
 */
const normalizePath = (path: string): string => {
    // Remove query string and fragment
    const cleanPath = path.split('?')[0].split('#')[0];

    // Split by slash, filter out empty, '.', and '..' segments
    const segments: string[] = [];
    for (const segment of cleanPath.split('/')) {
        if (segment === '' || segment === '.') {
            continue;
        }
        if (segment === '..') {
            // Remove last segment if going up (prevent path traversal)
            segments.pop();
        } else {
            segments.push(segment);
        }
    }

    // Reconstruct path with leading slash
    return '/' + segments.join('/');
};

/**
 * Check if a normalized path should be skipped for rate limiting
 * Uses exact matching to prevent bypass attacks
 * SECURITY: Prevents path traversal bypasses like /healthz/../../auth
 */
const shouldSkipPath = (requestPath: string, skipPaths: string[]): boolean => {
    const normalizedPath = normalizePath(requestPath);

    return skipPaths.some(skipPath => {
        const normalizedSkipPath = normalizePath(skipPath);

        // Exact match
        if (normalizedPath === normalizedSkipPath) {
            return true;
        }

        // Prefix match only if skip path ends with wildcard
        // This prevents /healthz matching /healthz/../../auth
        if (normalizedSkipPath.endsWith('/*')) {
            const prefix = normalizedSkipPath.slice(0, -2);
            return normalizedPath === prefix || normalizedPath.startsWith(prefix + '/');
        }

        return false;
    });
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
        keyGenerator,
        endpointTypeDetector = defaultEndpointTypeDetector,
        onLimitReached,
        trustedProxies = [],
        failClosedForAuth = true
    } = options;

    // Use trusted proxy key generator if trustedProxies is provided, otherwise use default
    const finalKeyGenerator = keyGenerator ||
        (trustedProxies.length > 0
            ? createKeyGeneratorWithProxySupport(trustedProxies)
            : defaultKeyGenerator);

    // Initialize Redis rate limiter with fail-closed option
    const limiter = new RedisRateLimiter(
        redis?.url || process.env.REDIS_URL,
        redis?.keyPrefix,
        failClosedForAuth
    );

    return async (req: Request, res: Response, next: NextFunction) => {
        try {
            // Skip certain paths
            if (shouldSkipPath(req.path, skipPaths)) {
                return next();
            }

            // Determine endpoint type and get rate limit config
            const endpointType = endpointTypeDetector(req);
            const config = DEFAULT_RATE_LIMITS[endpointType];

            // Generate unique key for this client/endpoint
            const clientKey = finalKeyGenerator(req);
            const rateLimitKey = `${endpointType}:${clientKey}`;

            // Check rate limit (pass endpointType for fail-closed behavior)
            const { allowed, remaining, resetTime } = await limiter.checkLimit(
                rateLimitKey,
                config,
                endpointType
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
        keyGenerator,
        endpointTypeDetector = defaultEndpointTypeDetector,
        onLimitReached,
        trustedProxies = [],
        failClosedForAuth = true
    } = options;

    // Use trusted proxy key generator if trustedProxies is provided, otherwise use default
    const finalKeyGenerator = keyGenerator ||
        (trustedProxies.length > 0
            ? createKeyGeneratorWithProxySupport(trustedProxies)
            : defaultKeyGenerator);

    const limiter = new RedisRateLimiter(
        redis?.url || process.env.REDIS_URL,
        redis?.keyPrefix,
        failClosedForAuth
    );

    return async (req: Request, res: Response, next: NextFunction) => {
        try {
            if (shouldSkipPath(req.path, skipPaths)) {
                return next();
            }

            const endpointType = endpointTypeDetector(req);
            const config = mergedLimits[endpointType];

            const clientKey = finalKeyGenerator(req);
            const rateLimitKey = `${endpointType}:${clientKey}`;

            const { allowed, remaining, resetTime } = await limiter.checkLimit(
                rateLimitKey,
                config,
                endpointType
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
