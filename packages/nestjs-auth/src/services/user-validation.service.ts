/**
 * User Validation Service for JWT Authentication
 * خدمة التحقق من المستخدمين للمصادقة بواسطة JWT
 *
 * Provides:
 * - Database lookup for user validation
 * - Redis caching for performance
 * - User status validation (active, verified, deleted, suspended)
 */

import { Injectable, Logger, UnauthorizedException } from '@nestjs/common';
import { InjectRedis } from '@liaoliaots/nestjs-redis';
import Redis from 'ioredis';
import { AuthErrors } from '../config/jwt.config';

/**
 * User validation data interface
 */
export interface UserValidationData {
  userId: string;
  email: string;
  isActive: boolean;
  isVerified: boolean;
  roles: string[];
  tenantId?: string;
  isDeleted?: boolean;
  isSuspended?: boolean;
}

/**
 * User repository interface
 * Implement this in your application to provide database access
 */
export interface IUserRepository {
  /**
   * Get user validation data from database
   */
  getUserValidationData(userId: string): Promise<UserValidationData | null>;

  /**
   * Update user's last login timestamp
   */
  updateLastLogin(userId: string): Promise<void>;
}

/**
 * User validation service with caching
 */
@Injectable()
export class UserValidationService {
  private readonly logger = new Logger(UserValidationService.name);
  private readonly cacheKeyPrefix = 'user_auth:';
  private readonly cacheTTL = 300; // 5 minutes

  constructor(
    @InjectRedis() private readonly redis: Redis,
    private readonly userRepository?: IUserRepository,
  ) {}

  /**
   * Validate user and get user data
   *
   * @param userId - User identifier
   * @returns User validation data
   * @throws UnauthorizedException if user is invalid
   */
  async validateUser(userId: string): Promise<UserValidationData> {
    // Try cache first
    const cached = await this.getCachedUser(userId);
    if (cached) {
      this.logger.debug(`User ${userId} validated from cache`);
      return cached;
    }

    // Cache miss - get from database
    if (!this.userRepository) {
      this.logger.warn('No user repository configured - skipping database validation');
      // Return minimal validation data
      return {
        userId,
        email: '',
        isActive: true,
        isVerified: true,
        roles: [],
      };
    }

    const userData = await this.userRepository.getUserValidationData(userId);

    if (!userData) {
      this.logger.warn(`User ${userId} not found in database`);
      throw new UnauthorizedException(AuthErrors.INVALID_TOKEN.en);
    }

    // Validate user status
    this.validateUserStatus(userData);

    // Cache the user data
    await this.cacheUser(userData);

    this.logger.log(`User ${userId} validated from database`);
    return userData;
  }

  /**
   * Validate user status (active, verified, not deleted/suspended)
   *
   * @param userData - User validation data
   * @throws UnauthorizedException if user status is invalid
   */
  private validateUserStatus(userData: UserValidationData): void {
    const { userId, isActive, isVerified, isDeleted, isSuspended } = userData;

    if (isDeleted) {
      this.logger.warn(`Authentication failed: User ${userId} is deleted`);
      throw new UnauthorizedException(AuthErrors.ACCOUNT_DISABLED.en);
    }

    if (isSuspended) {
      this.logger.warn(`Authentication failed: User ${userId} is suspended`);
      throw new UnauthorizedException(AuthErrors.ACCOUNT_DISABLED.en);
    }

    if (!isActive) {
      this.logger.warn(`Authentication failed: User ${userId} is inactive`);
      throw new UnauthorizedException(AuthErrors.ACCOUNT_DISABLED.en);
    }

    if (!isVerified) {
      this.logger.warn(`Authentication failed: User ${userId} is not verified`);
      throw new UnauthorizedException(AuthErrors.ACCOUNT_NOT_VERIFIED.en);
    }
  }

  /**
   * Get cached user data
   *
   * @param userId - User identifier
   * @returns Cached user data or null
   */
  private async getCachedUser(
    userId: string,
  ): Promise<UserValidationData | null> {
    try {
      const key = `${this.cacheKeyPrefix}${userId}`;
      const cached = await this.redis.get(key);

      if (cached) {
        return JSON.parse(cached);
      }

      return null;
    } catch (error) {
      this.logger.warn(`Cache get error for user ${userId}: ${error.message}`);
      return null;
    }
  }

  /**
   * Cache user data
   *
   * @param userData - User validation data
   */
  private async cacheUser(userData: UserValidationData): Promise<void> {
    try {
      const key = `${this.cacheKeyPrefix}${userData.userId}`;
      await this.redis.setex(key, this.cacheTTL, JSON.stringify(userData));
      this.logger.debug(`Cached user ${userData.userId}`);
    } catch (error) {
      this.logger.warn(
        `Cache set error for user ${userData.userId}: ${error.message}`,
      );
    }
  }

  /**
   * Invalidate cached user data
   *
   * @param userId - User identifier
   */
  async invalidateUser(userId: string): Promise<void> {
    try {
      const key = `${this.cacheKeyPrefix}${userId}`;
      await this.redis.del(key);
      this.logger.debug(`Invalidated cache for user ${userId}`);
    } catch (error) {
      this.logger.warn(
        `Cache invalidate error for user ${userId}: ${error.message}`,
      );
    }
  }

  /**
   * Clear all cached user data
   *
   * @returns Number of keys deleted
   */
  async clearAll(): Promise<number> {
    try {
      const pattern = `${this.cacheKeyPrefix}*`;
      const keys = await this.redis.keys(pattern);

      if (keys.length > 0) {
        const count = await this.redis.del(...keys);
        this.logger.log(`Cleared ${count} cached users`);
        return count;
      }

      return 0;
    } catch (error) {
      this.logger.error(`Cache clear error: ${error.message}`);
      return 0;
    }
  }
}
