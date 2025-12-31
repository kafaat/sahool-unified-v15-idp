/**
 * Token Revocation System with Redis (TypeScript/NestJS)
 * نظام إلغاء الرموز مع Redis
 *
 * Provides:
 * - Redis-based token revocation storage
 * - Individual token revocation by JTI
 * - User-level revocation (revoke all user tokens)
 * - Tenant-level revocation (revoke all tenant tokens)
 * - Automatic TTL management
 * - High-performance async operations
 */

import { Injectable, Logger, OnModuleDestroy, OnModuleInit } from '@nestjs/common';
import { createClient, RedisClientType } from 'redis';
import { JWTConfig } from '../config/jwt.config';

/**
 * Revocation information interface
 */
export interface RevocationInfo {
  revokedAt: number;
  reason: string;
  userId?: string;
  tenantId?: string;
}

/**
 * Token revocation check result
 */
export interface RevocationCheckResult {
  isRevoked: boolean;
  reason?: string;
}

/**
 * Revocation statistics
 */
export interface RevocationStats {
  initialized: boolean;
  revokedTokens: number;
  revokedUsers: number;
  revokedTenants: number;
  redisUrl?: string;
}

/**
 * Redis-based token revocation service
 * خدمة إلغاء الرموز القائمة على Redis
 *
 * Features:
 * - Fast O(1) token lookup
 * - Automatic expiration with TTL
 * - Distributed across multiple instances
 * - Support for different revocation strategies
 *
 * @example
 * ```typescript
 * const store = new RedisTokenRevocationStore();
 * await store.initialize();
 * await store.revokeToken('jti-123', { expiresIn: 3600, reason: 'logout' });
 * const isRevoked = await store.isTokenRevoked('jti-123');
 * ```
 */
@Injectable()
export class RedisTokenRevocationStore implements OnModuleInit, OnModuleDestroy {
  private readonly logger = new Logger(RedisTokenRevocationStore.name);

  // Redis key prefixes
  private readonly TOKEN_PREFIX = 'revoked:token:';
  private readonly USER_PREFIX = 'revoked:user:';
  private readonly TENANT_PREFIX = 'revoked:tenant:';

  private redis: RedisClientType | null = null;
  private initialized = false;

  constructor(private readonly redisUrl?: string) {}

  /**
   * Initialize on module startup
   */
  async onModuleInit(): Promise<void> {
    await this.initialize();
  }

  /**
   * Cleanup on module shutdown
   */
  async onModuleDestroy(): Promise<void> {
    await this.close();
  }

  /**
   * Build Redis URL from configuration
   */
  private buildRedisUrl(): string {
    if (this.redisUrl) {
      return this.redisUrl;
    }

    if (JWTConfig.REDIS_URL) {
      return JWTConfig.REDIS_URL;
    }

    const password = JWTConfig.REDIS_PASSWORD;
    const host = JWTConfig.REDIS_HOST;
    const port = JWTConfig.REDIS_PORT;
    const db = JWTConfig.REDIS_DB;

    if (password) {
      return `redis://:${password}@${host}:${port}/${db}`;
    }

    return `redis://${host}:${port}/${db}`;
  }

  /**
   * Initialize Redis connection
   * تهيئة اتصال Redis
   */
  async initialize(): Promise<void> {
    if (this.initialized) {
      return;
    }

    try {
      const url = this.buildRedisUrl();

      this.redis = createClient({
        url,
        socket: {
          connectTimeout: 5000,
          keepAlive: true,
        },
      });

      // Error handling
      this.redis.on('error', (err) => {
        this.logger.error(`Redis error: ${err.message}`);
      });

      this.redis.on('connect', () => {
        this.logger.log('Redis connected');
      });

      this.redis.on('ready', () => {
        this.logger.log('Redis ready');
      });

      // Connect to Redis
      await this.redis.connect();

      // Test connection
      await this.redis.ping();

      this.initialized = true;
      this.logger.log('Redis token revocation store initialized');
    } catch (error) {
      this.logger.error(`Failed to initialize Redis: ${error.message}`);
      throw error;
    }
  }

  /**
   * Close Redis connection
   * إغلاق اتصال Redis
   */
  async close(): Promise<void> {
    if (this.redis) {
      await this.redis.quit();
      this.redis = null;
      this.initialized = false;
      this.logger.log('Redis token revocation store closed');
    }
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Token (JTI) Revocation
  // ─────────────────────────────────────────────────────────────────────────

  /**
   * Revoke a single token by JTI
   * إلغاء رمز واحد بواسطة JTI
   *
   * @param jti - JWT ID to revoke
   * @param options - Revocation options
   * @returns True if revoked successfully
   *
   * @example
   * ```typescript
   * await store.revokeToken('abc123', {
   *   expiresIn: 3600,
   *   reason: 'user_logout',
   *   userId: 'user-456'
   * });
   * ```
   */
  async revokeToken(
    jti: string,
    options: {
      expiresIn?: number;
      reason?: string;
      userId?: string;
      tenantId?: string;
    } = {},
  ): Promise<boolean> {
    if (!this.initialized) {
      await this.initialize();
    }

    if (!jti) {
      return false;
    }

    // Default TTL: 24 hours
    const ttl = options.expiresIn || 86400;
    const reason = options.reason || 'manual';

    // Store revocation info
    const key = `${this.TOKEN_PREFIX}${jti}`;
    const value: RevocationInfo = {
      revokedAt: Date.now() / 1000,
      reason,
      userId: options.userId,
      tenantId: options.tenantId,
    };

    try {
      // Store with TTL (auto-cleanup)
      await this.redis!.setEx(key, ttl, JSON.stringify(value));

      this.logger.log(
        `Token revoked: jti=${jti.substring(0, 8)}..., ` +
          `reason=${reason}, ttl=${ttl}s`,
      );

      return true;
    } catch (error) {
      this.logger.error(`Failed to revoke token: ${error.message}`);
      return false;
    }
  }

  /**
   * Check if a token is revoked by JTI
   * التحقق من إلغاء الرمز بواسطة JTI
   *
   * @param jti - JWT ID to check
   * @returns True if token is revoked
   *
   * @example
   * ```typescript
   * const isRevoked = await store.isTokenRevoked('abc123');
   * ```
   */
  async isTokenRevoked(jti: string): Promise<boolean> {
    if (!this.initialized) {
      await this.initialize();
    }

    if (!jti) {
      return false;
    }

    try {
      const key = `${this.TOKEN_PREFIX}${jti}`;
      const exists = await this.redis!.exists(key);
      return exists > 0;
    } catch (error) {
      this.logger.error(`Error checking token revocation: ${error.message}`);
      // Fail open: don't block access on Redis errors
      return false;
    }
  }

  /**
   * Get detailed revocation information for a token
   * الحصول على معلومات إلغاء مفصلة للرمز
   *
   * @param jti - JWT ID
   * @returns Revocation info or null
   */
  async getRevocationInfo(jti: string): Promise<RevocationInfo | null> {
    if (!this.initialized) {
      await this.initialize();
    }

    if (!jti) {
      return null;
    }

    try {
      const key = `${this.TOKEN_PREFIX}${jti}`;
      const value = await this.redis!.get(key);

      if (value) {
        return JSON.parse(value) as RevocationInfo;
      }

      return null;
    } catch (error) {
      this.logger.error(`Error getting revocation info: ${error.message}`);
      return null;
    }
  }

  // ─────────────────────────────────────────────────────────────────────────
  // User-Level Revocation
  // ─────────────────────────────────────────────────────────────────────────

  /**
   * Revoke all tokens for a user
   * إلغاء جميع الرموز للمستخدم
   *
   * Any token issued before this timestamp will be invalid.
   *
   * @param userId - User ID
   * @param reason - Reason for revocation
   * @returns True if revoked successfully
   *
   * @example
   * ```typescript
   * await store.revokeAllUserTokens('user-456', 'password_change');
   * ```
   */
  async revokeAllUserTokens(
    userId: string,
    reason: string = 'user_logout',
  ): Promise<boolean> {
    if (!this.initialized) {
      await this.initialize();
    }

    if (!userId) {
      return false;
    }

    try {
      const key = `${this.USER_PREFIX}${userId}`;
      const value: RevocationInfo = {
        revokedAt: Date.now() / 1000,
        reason,
      };

      // Store with long TTL (30 days)
      await this.redis!.setEx(key, 2592000, JSON.stringify(value));

      this.logger.log(
        `All user tokens revoked: userId=${userId}, reason=${reason}`,
      );

      return true;
    } catch (error) {
      this.logger.error(`Failed to revoke user tokens: ${error.message}`);
      return false;
    }
  }

  /**
   * Check if a user's token is revoked
   * التحقق من إلغاء رمز المستخدم
   *
   * @param userId - User ID
   * @param tokenIssuedAt - When token was issued (iat claim)
   * @returns True if token was issued before user revocation
   *
   * @example
   * ```typescript
   * const isRevoked = await store.isUserTokenRevoked('user-456', 1640000000);
   * ```
   */
  async isUserTokenRevoked(
    userId: string,
    tokenIssuedAt: number,
  ): Promise<boolean> {
    if (!this.initialized) {
      await this.initialize();
    }

    if (!userId) {
      return false;
    }

    try {
      const key = `${this.USER_PREFIX}${userId}`;
      const value = await this.redis!.get(key);

      if (value) {
        const data: RevocationInfo = JSON.parse(value);
        const revokedAt = data.revokedAt || 0;

        // Token is revoked if it was issued before revocation
        return tokenIssuedAt < revokedAt;
      }

      return false;
    } catch (error) {
      this.logger.error(
        `Error checking user token revocation: ${error.message}`,
      );
      return false;
    }
  }

  /**
   * Clear user-level revocation
   * مسح إلغاء على مستوى المستخدم
   *
   * Use after user re-authenticates with new password.
   *
   * @param userId - User ID
   * @returns True if cleared successfully
   */
  async clearUserRevocation(userId: string): Promise<boolean> {
    if (!this.initialized) {
      await this.initialize();
    }

    if (!userId) {
      return false;
    }

    try {
      const key = `${this.USER_PREFIX}${userId}`;
      const deleted = await this.redis!.del(key);

      if (deleted) {
        this.logger.log(`User revocation cleared: userId=${userId}`);
      }

      return deleted > 0;
    } catch (error) {
      this.logger.error(`Failed to clear user revocation: ${error.message}`);
      return false;
    }
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Tenant-Level Revocation
  // ─────────────────────────────────────────────────────────────────────────

  /**
   * Revoke all tokens for a tenant
   * إلغاء جميع الرموز للمستأجر
   *
   * Use with caution - affects all users in the tenant.
   *
   * @param tenantId - Tenant ID
   * @param reason - Reason for revocation
   * @returns True if revoked successfully
   */
  async revokeAllTenantTokens(
    tenantId: string,
    reason: string = 'security',
  ): Promise<boolean> {
    if (!this.initialized) {
      await this.initialize();
    }

    if (!tenantId) {
      return false;
    }

    try {
      const key = `${this.TENANT_PREFIX}${tenantId}`;
      const value: RevocationInfo = {
        revokedAt: Date.now() / 1000,
        reason,
      };

      // Store with long TTL (30 days)
      await this.redis!.setEx(key, 2592000, JSON.stringify(value));

      this.logger.warn(
        `All tenant tokens revoked: tenantId=${tenantId}, reason=${reason}`,
      );

      return true;
    } catch (error) {
      this.logger.error(`Failed to revoke tenant tokens: ${error.message}`);
      return false;
    }
  }

  /**
   * Check if a tenant's token is revoked
   * التحقق من إلغاء رمز المستأجر
   *
   * @param tenantId - Tenant ID
   * @param tokenIssuedAt - When token was issued (iat claim)
   * @returns True if token was issued before tenant revocation
   */
  async isTenantTokenRevoked(
    tenantId: string,
    tokenIssuedAt: number,
  ): Promise<boolean> {
    if (!this.initialized) {
      await this.initialize();
    }

    if (!tenantId) {
      return false;
    }

    try {
      const key = `${this.TENANT_PREFIX}${tenantId}`;
      const value = await this.redis!.get(key);

      if (value) {
        const data: RevocationInfo = JSON.parse(value);
        const revokedAt = data.revokedAt || 0;

        return tokenIssuedAt < revokedAt;
      }

      return false;
    } catch (error) {
      this.logger.error(
        `Error checking tenant token revocation: ${error.message}`,
      );
      return false;
    }
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Combined Check
  // ─────────────────────────────────────────────────────────────────────────

  /**
   * Check if a token is revoked by any method
   * التحقق من إلغاء الرمز بأي طريقة
   *
   * @param options - Check options
   * @returns Revocation check result
   *
   * @example
   * ```typescript
   * const result = await store.isRevoked({
   *   jti: 'abc123',
   *   userId: 'user-456',
   *   issuedAt: 1640000000
   * });
   *
   * if (result.isRevoked) {
   *   console.log(`Token revoked: ${result.reason}`);
   * }
   * ```
   */
  async isRevoked(options: {
    jti?: string;
    userId?: string;
    tenantId?: string;
    issuedAt?: number;
  }): Promise<RevocationCheckResult> {
    if (!this.initialized) {
      await this.initialize();
    }

    // Check JTI revocation
    if (options.jti && (await this.isTokenRevoked(options.jti))) {
      return { isRevoked: true, reason: 'token_revoked' };
    }

    // Check user revocation
    if (options.userId && options.issuedAt) {
      if (await this.isUserTokenRevoked(options.userId, options.issuedAt)) {
        return { isRevoked: true, reason: 'user_tokens_revoked' };
      }
    }

    // Check tenant revocation
    if (options.tenantId && options.issuedAt) {
      if (await this.isTenantTokenRevoked(options.tenantId, options.issuedAt)) {
        return { isRevoked: true, reason: 'tenant_tokens_revoked' };
      }
    }

    return { isRevoked: false };
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Statistics and Health
  // ─────────────────────────────────────────────────────────────────────────

  /**
   * Get revocation statistics
   * الحصول على إحصائيات الإلغاء
   *
   * @returns Statistics object
   */
  async getStats(): Promise<RevocationStats> {
    if (!this.initialized) {
      await this.initialize();
    }

    try {
      // Count keys by prefix
      const tokenKeys = await this.redis!.keys(`${this.TOKEN_PREFIX}*`);
      const userKeys = await this.redis!.keys(`${this.USER_PREFIX}*`);
      const tenantKeys = await this.redis!.keys(`${this.TENANT_PREFIX}*`);

      return {
        initialized: this.initialized,
        revokedTokens: tokenKeys.length,
        revokedUsers: userKeys.length,
        revokedTenants: tenantKeys.length,
        redisUrl: this.buildRedisUrl().split('@').pop(), // Hide password
      };
    } catch (error) {
      this.logger.error(`Error getting stats: ${error.message}`);
      return {
        initialized: this.initialized,
        revokedTokens: 0,
        revokedUsers: 0,
        revokedTenants: 0,
      };
    }
  }

  /**
   * Check if Redis connection is healthy
   * التحقق من صحة اتصال Redis
   *
   * @returns True if healthy
   */
  async healthCheck(): Promise<boolean> {
    try {
      if (!this.initialized) {
        await this.initialize();
      }

      await this.redis!.ping();
      return true;
    } catch (error) {
      this.logger.error(`Health check failed: ${error.message}`);
      return false;
    }
  }
}

/**
 * Token Revocation Module
 * وحدة إلغاء الرموز
 *
 * @example
 * ```typescript
 * import { Module } from '@nestjs/common';
 * import { TokenRevocationModule } from '@shared/auth/token-revocation';
 *
 * @Module({
 *   imports: [TokenRevocationModule],
 * })
 * export class AppModule {}
 * ```
 */
import { Module, Global } from '@nestjs/common';

@Global()
@Module({
  providers: [RedisTokenRevocationStore],
  exports: [RedisTokenRevocationStore],
})
export class TokenRevocationModule {}
