/**
 * Token Revocation System with Redis (TypeScript/NestJS)
 * نظام إلغاء الرموز مع Redis
 */

import {
  Injectable,
  Logger,
  OnModuleDestroy,
  OnModuleInit,
  Module,
  Global,
} from "@nestjs/common";
import { createClient, RedisClientType } from "redis";
import { JWTConfig } from "./jwt.config";

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
 */
@Injectable()
export class RedisTokenRevocationStore
  implements OnModuleInit, OnModuleDestroy
{
  private readonly logger = new Logger(RedisTokenRevocationStore.name);

  // Redis key prefixes
  private readonly TOKEN_PREFIX = "revoked:token:";
  private readonly USER_PREFIX = "revoked:user:";
  private readonly TENANT_PREFIX = "revoked:tenant:";

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
          keepAlive: 5000,
        },
      });

      // Error handling
      this.redis.on("error", (err) => {
        this.logger.error(`Redis error: ${err.message}`);
      });

      this.redis.on("connect", () => {
        this.logger.log("Redis connected");
      });

      this.redis.on("ready", () => {
        this.logger.log("Redis ready");
      });

      // Connect to Redis
      await this.redis.connect();

      // Test connection
      await this.redis.ping();

      this.initialized = true;
      this.logger.log("Redis token revocation store initialized");
    } catch (error) {
      this.logger.error(`Failed to initialize Redis: ${error.message}`);
      throw error;
    }
  }

  /**
   * Close Redis connection
   */
  async close(): Promise<void> {
    if (this.redis) {
      await this.redis.quit();
      this.redis = null;
      this.initialized = false;
      this.logger.log("Redis token revocation store closed");
    }
  }

  /**
   * Revoke a single token by JTI
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

    const ttl = options.expiresIn || 86400;
    const reason = options.reason || "manual";

    const key = `${this.TOKEN_PREFIX}${jti}`;
    const value: RevocationInfo = {
      revokedAt: Date.now() / 1000,
      reason,
      userId: options.userId,
      tenantId: options.tenantId,
    };

    try {
      await this.redis!.setEx(key, ttl, JSON.stringify(value));

      this.logger.log(
        `Token revoked: jti=${jti.substring(0, 8)}..., reason=${reason}, ttl=${ttl}s`,
      );

      return true;
    } catch (error) {
      this.logger.error(`Failed to revoke token: ${error.message}`);
      return false;
    }
  }

  /**
   * Check if a token is revoked by JTI
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
      return false;
    }
  }

  /**
   * Revoke all tokens for a user
   */
  async revokeAllUserTokens(
    userId: string,
    reason: string = "user_logout",
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
   * Check if a tenant's token is revoked
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

  /**
   * Check if a token is revoked by any method
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

    if (options.jti && (await this.isTokenRevoked(options.jti))) {
      return { isRevoked: true, reason: "token_revoked" };
    }

    if (options.userId && options.issuedAt) {
      if (await this.isUserTokenRevoked(options.userId, options.issuedAt)) {
        return { isRevoked: true, reason: "user_tokens_revoked" };
      }
    }

    if (options.tenantId && options.issuedAt) {
      if (await this.isTenantTokenRevoked(options.tenantId, options.issuedAt)) {
        return { isRevoked: true, reason: "tenant_tokens_revoked" };
      }
    }

    return { isRevoked: false };
  }

  /**
   * Check if Redis connection is healthy
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

@Global()
@Module({
  providers: [RedisTokenRevocationStore],
  exports: [RedisTokenRevocationStore],
})
export class TokenRevocationModule {}
