/**
 * Authentication Service for SAHOOL User Service
 * خدمة المصادقة لخدمة المستخدمين
 *
 * Handles:
 * - User login and token generation
 * - Token refresh
 * - Logout with token revocation
 * - Password validation
 */

import {
  Injectable,
  UnauthorizedException,
  NotFoundException,
  Logger,
} from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';
import * as bcrypt from 'bcryptjs';
import { v4 as uuidv4 } from 'uuid';
import { PrismaService } from '../prisma/prisma.service';
import { RedisTokenRevocationStore } from '@sahool/nestjs-auth/services/token-revocation';
import { JWTConfig } from '@sahool/nestjs-auth/config/jwt.config';
import { UserStatus } from '@prisma/client';

export interface LoginDto {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  expires_in: number;
  token_type: string;
  user: {
    id: string;
    email: string;
    firstName: string;
    lastName: string;
    role: string;
    tenantId: string;
  };
}

export interface JwtPayload {
  sub: string;
  email: string;
  roles: string[];
  tid?: string;
  jti: string;
  type: 'access' | 'refresh';
  family?: string; // Token family for refresh token rotation
  iat?: number;
  exp?: number;
}

@Injectable()
export class AuthService {
  private readonly logger = new Logger(AuthService.name);

  constructor(
    private readonly prisma: PrismaService,
    private readonly jwtService: JwtService,
    private readonly revocationStore: RedisTokenRevocationStore,
  ) {}

  /**
   * User login
   * تسجيل دخول المستخدم
   */
  async login(loginDto: LoginDto): Promise<TokenResponse> {
    const { email, password } = loginDto;

    // Find user by email
    const user = await this.prisma.user.findUnique({
      where: { email },
    });

    if (!user) {
      this.logger.warn(`Login attempt failed: User not found (${email})`);
      throw new UnauthorizedException('Invalid email or password');
    }

    // Verify password
    const isPasswordValid = await bcrypt.compare(password, user.passwordHash);
    if (!isPasswordValid) {
      this.logger.warn(`Login attempt failed: Invalid password (${email})`);
      throw new UnauthorizedException('Invalid email or password');
    }

    // Check user status
    if (user.status !== UserStatus.ACTIVE) {
      this.logger.warn(
        `Login attempt failed: User status is ${user.status} (${email})`,
      );
      throw new UnauthorizedException(
        `Account is ${user.status.toLowerCase()}. Please contact support.`,
      );
    }

    // Check if email is verified (optional based on your requirements)
    if (!user.emailVerified) {
      this.logger.warn(`Login attempt: Email not verified (${email})`);
      // You can either throw an error or allow login
      // throw new UnauthorizedException('Email not verified');
    }

    // Generate tokens
    const tokens = await this.generateTokens(user);

    // Update last login timestamp
    await this.prisma.user.update({
      where: { id: user.id },
      data: { lastLoginAt: new Date() },
    });

    this.logger.log(`User logged in successfully: ${user.id} (${email})`);

    return {
      ...tokens,
      user: {
        id: user.id,
        email: user.email,
        firstName: user.firstName,
        lastName: user.lastName,
        role: user.role,
        tenantId: user.tenantId,
      },
    };
  }

  /**
   * Generate access and refresh tokens
   * إنشاء رموز الوصول والتحديث
   */
  private async generateTokens(
    user: any,
    family?: string,
  ): Promise<{
    access_token: string;
    refresh_token: string;
    expires_in: number;
    token_type: string;
  }> {
    // Generate unique JTI for access token
    const accessJti = uuidv4();
    const refreshJti = uuidv4();
    // Generate new family if not provided (initial login)
    const tokenFamily = family || uuidv4();

    // Access token payload
    const accessPayload: JwtPayload = {
      sub: user.id,
      email: user.email,
      roles: [user.role],
      tid: user.tenantId,
      jti: accessJti,
      type: 'access',
    };

    // Refresh token payload
    const refreshPayload: JwtPayload = {
      sub: user.id,
      email: user.email,
      roles: [user.role],
      tid: user.tenantId,
      jti: refreshJti,
      type: 'refresh',
      family: tokenFamily,
    };

    // Generate tokens
    const access_token = this.jwtService.sign(accessPayload, {
      expiresIn: `${JWTConfig.ACCESS_TOKEN_EXPIRE_MINUTES}m`,
      issuer: JWTConfig.ISSUER,
      audience: JWTConfig.AUDIENCE,
    });

    const refresh_token = this.jwtService.sign(refreshPayload, {
      expiresIn: `${JWTConfig.REFRESH_TOKEN_EXPIRE_DAYS}d`,
      issuer: JWTConfig.ISSUER,
      audience: JWTConfig.AUDIENCE,
    });

    // Store refresh token in database
    const expiresAt = new Date(
      Date.now() + JWTConfig.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60 * 1000,
    );
    await this.prisma.refreshToken.create({
      data: {
        userId: user.id,
        jti: refreshJti,
        family: tokenFamily,
        token: refresh_token,
        expiresAt,
      },
    });

    return {
      access_token,
      refresh_token,
      expires_in: JWTConfig.ACCESS_TOKEN_EXPIRE_MINUTES * 60, // in seconds
      token_type: 'Bearer',
    };
  }

  /**
   * Logout - Revoke current token
   * تسجيل الخروج - إلغاء الرمز الحالي
   *
   * @param token - The JWT token to revoke
   * @param userId - The user ID from the token payload
   */
  async logout(token: string, userId: string): Promise<void> {
    try {
      // Decode token to get JTI and expiration
      const payload = this.jwtService.decode(token) as JwtPayload;

      if (!payload || !payload.jti) {
        this.logger.warn('Logout attempt with invalid token (no JTI)');
        throw new UnauthorizedException('Invalid token');
      }

      // Calculate TTL based on token expiration
      let ttl = 86400; // Default 24 hours
      if (payload.exp) {
        const expiresIn = payload.exp - Math.floor(Date.now() / 1000);
        ttl = expiresIn > 0 ? expiresIn : 60; // Minimum 60 seconds
      }

      // Revoke token in Redis
      const success = await this.revocationStore.revokeToken(payload.jti, {
        expiresIn: ttl,
        reason: 'user_logout',
        userId,
        tenantId: payload.tid,
      });

      if (success) {
        this.logger.log(
          `User logged out successfully: ${userId} (jti: ${payload.jti.substring(0, 8)}...)`,
        );
      } else {
        this.logger.error(`Failed to revoke token for user: ${userId}`);
        throw new Error('Failed to revoke token');
      }
    } catch (error) {
      if (error instanceof UnauthorizedException) {
        throw error;
      }
      this.logger.error(`Logout error: ${error.message}`, error.stack);
      throw new Error('Logout failed');
    }
  }

  /**
   * Logout from all devices - Revoke all user tokens
   * تسجيل الخروج من جميع الأجهزة - إلغاء جميع رموز المستخدم
   *
   * @param userId - The user ID
   */
  async logoutAll(userId: string): Promise<void> {
    try {
      const success = await this.revocationStore.revokeAllUserTokens(
        userId,
        'user_logout_all',
      );

      if (success) {
        this.logger.log(
          `User logged out from all devices: ${userId}`,
        );
      } else {
        this.logger.error(
          `Failed to revoke all tokens for user: ${userId}`,
        );
        throw new Error('Failed to revoke all tokens');
      }
    } catch (error) {
      this.logger.error(
        `Logout all error: ${error.message}`,
        error.stack,
      );
      throw new Error('Logout from all devices failed');
    }
  }

  /**
   * Invalidate entire token family (for reuse detection)
   * إبطال عائلة الرموز بالكامل
   *
   * @param family - The token family ID
   */
  private async invalidateTokenFamily(family: string): Promise<void> {
    try {
      // Mark all tokens in family as revoked in database
      await this.prisma.refreshToken.updateMany({
        where: { family },
        data: { revoked: true },
      });

      // Get all tokens in family to revoke in Redis
      const familyTokens = await this.prisma.refreshToken.findMany({
        where: { family },
        select: { jti: true },
      });

      // Revoke each token in Redis
      const revokePromises = familyTokens.map((token) =>
        this.revocationStore.revokeToken(token.jti, {
          expiresIn: JWTConfig.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
          reason: 'token_reuse_detected',
        }),
      );

      await Promise.all(revokePromises);

      this.logger.warn(
        `Token family invalidated due to reuse detection: family=${family.substring(0, 8)}...`,
      );
    } catch (error) {
      this.logger.error(
        `Failed to invalidate token family: ${error.message}`,
        error.stack,
      );
      throw error;
    }
  }

  /**
   * Refresh access token with rotation
   * تحديث رمز الوصول مع التدوير
   *
   * @param refreshToken - The refresh token
   */
  async refreshToken(refreshToken: string): Promise<{
    access_token: string;
    refresh_token: string;
    expires_in: number;
    token_type: string;
  }> {
    try {
      // Verify refresh token
      const payload = this.jwtService.verify(refreshToken, {
        secret: JWTConfig.getVerificationKey(),
        issuer: JWTConfig.ISSUER,
        audience: JWTConfig.AUDIENCE,
      }) as JwtPayload;

      // Verify it's a refresh token
      if (payload.type !== 'refresh') {
        throw new UnauthorizedException('Invalid token type');
      }

      // Check if refresh token exists in database
      const storedToken = await this.prisma.refreshToken.findUnique({
        where: { jti: payload.jti },
      });

      if (!storedToken) {
        this.logger.warn(
          `Refresh attempt with unknown token: ${payload.jti.substring(0, 8)}...`,
        );
        throw new UnauthorizedException('Invalid refresh token');
      }

      // Check if token was already used (replay attack detection)
      if (storedToken.used) {
        this.logger.error(
          `Token reuse detected! Token: ${payload.jti.substring(0, 8)}..., Family: ${payload.family?.substring(0, 8)}...`,
        );

        // Invalidate entire token family
        if (payload.family) {
          await this.invalidateTokenFamily(payload.family);
        }

        throw new UnauthorizedException(
          'Token reuse detected - all tokens in family have been invalidated',
        );
      }

      // Check if token is revoked
      if (storedToken.revoked) {
        this.logger.warn(
          `Refresh attempt with revoked token: ${payload.jti.substring(0, 8)}...`,
        );
        throw new UnauthorizedException('Token has been revoked');
      }

      // Check if token is expired
      if (storedToken.expiresAt < new Date()) {
        this.logger.warn(
          `Refresh attempt with expired token: ${payload.jti.substring(0, 8)}...`,
        );
        throw new UnauthorizedException('Refresh token has expired');
      }

      // Verify user still exists and is active
      const user = await this.prisma.user.findUnique({
        where: { id: payload.sub },
      });

      if (!user || user.status !== UserStatus.ACTIVE) {
        throw new UnauthorizedException('User account is not active');
      }

      // Mark current refresh token as used
      const newRefreshJti = uuidv4();
      await this.prisma.refreshToken.update({
        where: { jti: payload.jti },
        data: {
          used: true,
          usedAt: new Date(),
          replacedBy: newRefreshJti,
        },
      });

      // Mark old token as used in Redis (with short TTL for detection window)
      await this.revocationStore.revokeToken(payload.jti, {
        expiresIn: 300, // 5 minutes to detect concurrent reuse attempts
        reason: 'refresh_token_rotated',
        userId: user.id,
        tenantId: user.tenantId,
      });

      // Generate new token pair with same family
      const tokens = await this.generateTokens(user, payload.family);

      this.logger.log(
        `Refresh token rotated for user: ${user.id}, Old JTI: ${payload.jti.substring(0, 8)}..., New JTI: ${newRefreshJti.substring(0, 8)}...`,
      );

      return tokens;
    } catch (error) {
      if (error instanceof UnauthorizedException) {
        throw error;
      }
      this.logger.error(`Token refresh error: ${error.message}`, error.stack);
      throw new UnauthorizedException('Invalid refresh token');
    }
  }

  /**
   * Validate user credentials (for manual validation)
   * التحقق من بيانات اعتماد المستخدم
   */
  async validateUser(email: string, password: string): Promise<any> {
    const user = await this.prisma.user.findUnique({
      where: { email },
    });

    if (user && (await bcrypt.compare(password, user.passwordHash))) {
      const { passwordHash, ...result } = user;
      return result;
    }

    return null;
  }
}
