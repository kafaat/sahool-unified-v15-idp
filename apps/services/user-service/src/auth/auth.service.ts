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
  Optional,
  UnauthorizedException,
  NotFoundException,
  BadRequestException,
  ConflictException,
  Logger,
} from "@nestjs/common";
import { JwtService } from "@nestjs/jwt";
import * as bcrypt from "bcryptjs";
import * as crypto from "crypto";
import * as nodemailer from "nodemailer";
import { v4 as uuidv4 } from "uuid";
import { PrismaService } from "../prisma/prisma.service";
import { UserEventsService } from "../events/user-events.service";
import { RedisTokenRevocationStore } from "../utils/token-revocation";
import { JWTConfig } from "../utils/jwt.config";
import { UserStatus } from "../utils/validation";
import { BCRYPT_ROUNDS, DEFAULT_TENANT_ID, splitFullName } from "../utils/security.config";

export interface LoginDto {
  email?: string;
  phone?: string;
  password: string;
}

export interface RegisterDto {
  email: string;
  password: string;
  name?: string;
  firstName?: string;
  lastName?: string;
  phone?: string;
  tenantId?: string;
}

export interface ForgotPasswordDto {
  email: string;
}

export interface ResetPasswordDto {
  token: string;
  newPassword: string;
}

export interface SendOtpDto {
  identifier: string;
  channel: "sms" | "whatsapp" | "telegram" | "email";
  purpose: "password_reset" | "verify_phone";
  language?: string;
}

export interface VerifyOtpDto {
  identifier: string;
  otpCode: string;
  purpose: string;
}

// Account lockout configuration
const LOCKOUT_CONFIG = {
  MAX_FAILED_ATTEMPTS: 5,
  LOCKOUT_DURATION_MINUTES: 30,
  PROGRESSIVE_DELAY_SECONDS: [0, 2, 4, 8, 16], // Progressive delays after each failed attempt
};

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  expires_in: number;
  token_type: string;
  user: {
    id: string;
    email: string;
    name: string;
    name_ar?: string;
    firstName: string;
    lastName: string;
    role: string;
    tenantId: string;
    tenant_id: string;
  };
}

export interface JwtPayload {
  sub: string;
  email: string;
  roles: string[];
  tid?: string;
  jti: string;
  type: "access" | "refresh";
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
    // Optional — UserEventsService comes from the global EventsModule.
    // Marked Optional() so the constructor still works in tests that
    // don't set up the events module.
    @Optional() private readonly userEvents?: UserEventsService,
  ) { }

  /**
   * Sanitize user input for safe logging (prevents log injection)
   * @param input - User-provided value to sanitize
   * @returns Sanitized string safe for logging
   */
  private sanitizeForLog(input: string): string {
    if (typeof input !== "string") {
      return String(input);
    }
    // Remove newlines, carriage returns, and control characters to prevent log injection
    return input
      .replace(/[\r\n]/g, "")
      .replace(/[\x00-\x1F\x7F]/g, "")
      .slice(0, 100); // Limit length
  }

  /**
   * User login with account lockout protection
   * تسجيل دخول المستخدم مع حماية قفل الحساب
   */
  async login(loginDto: LoginDto): Promise<TokenResponse> {
    const { password } = loginDto;

    // Find user by email or phone
    let user;
    if (loginDto.email) {
      const email = loginDto.email.toLowerCase().trim();
      user = await this.prisma.user.findUnique({ where: { email } });
    } else if (loginDto.phone) {
      const phone = loginDto.phone.trim();
      user = await this.prisma.user.findFirst({ where: { phone } });
    }

    if (!user) {
      const identifier = loginDto.email || loginDto.phone || 'unknown';
      this.logger.warn(
        `Login attempt failed: User not found`,
        { identifier: this.sanitizeForLog(identifier) },
      );
      throw new UnauthorizedException("Invalid email or password");
    }

    const identifier = loginDto.email || loginDto.phone || user.email;

    // Check if account is locked
    const lockoutStatus = await this.checkAccountLockout(user.id);
    if (lockoutStatus.isLocked) {
      this.logger.warn(
        `Login attempt blocked: Account is locked`,
        { identifier: this.sanitizeForLog(identifier), remainingMinutes: lockoutStatus.remainingMinutes },
      );
      throw new UnauthorizedException(
        `Account is temporarily locked due to too many failed login attempts. Please try again in ${lockoutStatus.remainingMinutes} minutes.`,
      );
    }

    // Apply progressive delay based on failed attempts
    const delay = this.getProgressiveDelay(lockoutStatus.failedAttempts);
    if (delay > 0) {
      await new Promise(resolve => setTimeout(resolve, delay));
    }

    // Verify password
    const isPasswordValid = await bcrypt.compare(password, user.passwordHash);
    if (!isPasswordValid) {
      // Record failed attempt
      const lockResult = await this.recordFailedLoginAttempt(user.id);

      this.logger.warn(
        `Login attempt failed: Invalid password`,
        {
          identifier: this.sanitizeForLog(identifier),
          attemptsRemaining: lockResult.attemptsRemaining,
          isNowLocked: lockResult.isNowLocked,
        },
      );

      if (lockResult.isNowLocked) {
        throw new UnauthorizedException(
          `Account has been locked due to too many failed login attempts. Please try again in ${LOCKOUT_CONFIG.LOCKOUT_DURATION_MINUTES} minutes or reset your password.`,
        );
      }

      throw new UnauthorizedException(
        lockResult.attemptsRemaining > 0
          ? `Invalid email or password. ${lockResult.attemptsRemaining} attempts remaining before account lockout.`
          : "Invalid email or password",
      );
    }

    // Check user status
    if (user.status !== UserStatus.ACTIVE) {
      this.logger.warn(
        `Login attempt failed: User status is ${user.status}`,
        { identifier: this.sanitizeForLog(identifier) },
      );
      throw new UnauthorizedException(
        'Account is not available. Please contact support.',
      );
    }

    // Check if email is verified (optional based on your requirements)
    if (!user.emailVerified) {
      this.logger.warn(
        `Login attempt: Email not verified`,
        { identifier: this.sanitizeForLog(identifier) },
      );
      // You can either throw an error or allow login
      // throw new UnauthorizedException('Email not verified');
    }

    // Reset failed login attempts on successful login
    await this.resetFailedLoginAttempts(user.id);

    // Generate tokens
    const tokens = await this.generateTokens(user);

    // Update last login timestamp
    await this.prisma.user.update({
      where: { id: user.id },
      data: { lastLoginAt: new Date() },
    });

    this.logger.log(`User logged in successfully`, {
      userId: user.id,
      identifier: this.sanitizeForLog(identifier),
    });

    return {
      ...tokens,
      user: {
        id: user.id,
        email: user.email,
        name: `${user.firstName} ${user.lastName}`.trim(),
        name_ar: user.nameAr || undefined,
        firstName: user.firstName,
        lastName: user.lastName,
        role: user.role,
        tenantId: user.tenantId,
        tenant_id: user.tenantId,
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
      type: "access",
    };

    // Refresh token payload
    const refreshPayload: JwtPayload = {
      sub: user.id,
      email: user.email,
      roles: [user.role],
      tid: user.tenantId,
      jti: refreshJti,
      type: "refresh",
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

    // Store hashed refresh token in database (security: never store tokens in plaintext)
    const expiresAt = new Date(
      Date.now() + JWTConfig.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60 * 1000,
    );
    const tokenHash = crypto
      .createHash("sha256")
      .update(refresh_token)
      .digest("hex");

    await this.prisma.refreshToken.create({
      data: {
        tenantId: user.tenantId,
        userId: user.id,
        jti: refreshJti,
        family: tokenFamily,
        token: tokenHash, // Store hash, not plaintext
        expiresAt,
      },
    });

    return {
      access_token,
      refresh_token,
      expires_in: JWTConfig.ACCESS_TOKEN_EXPIRE_MINUTES * 60, // in seconds
      token_type: "Bearer",
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
        this.logger.warn("Logout attempt with invalid token (no JTI)");
        throw new UnauthorizedException("Invalid token");
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
        reason: "user_logout",
        userId,
        tenantId: payload.tid,
      });

      if (success) {
        this.logger.log(
          `User logged out successfully: ${userId} (jti: ${payload.jti.substring(0, 8)}...)`,
        );
      } else {
        this.logger.error(`Failed to revoke token for user: ${userId}`);
        throw new Error("Failed to revoke token");
      }
    } catch (error) {
      if (error instanceof UnauthorizedException) {
        throw error;
      }
      const message = error instanceof Error ? error.message : String(error);
      const stack = error instanceof Error ? error.stack : undefined;
      this.logger.error(`Logout error: ${message}`, stack);
      throw new Error("Logout failed");
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
        "user_logout_all",
      );

      if (success) {
        this.logger.log(`User logged out from all devices: ${userId}`);
      } else {
        this.logger.error(`Failed to revoke all tokens for user: ${userId}`);
        throw new Error("Failed to revoke all tokens");
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      const stack = error instanceof Error ? error.stack : undefined;
      this.logger.error(`Logout all error: ${message}`, stack);
      throw new Error("Logout from all devices failed");
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
        take: 100,
      });

      // Revoke each token in Redis
      const revokePromises = familyTokens.map((token: { jti: string }) =>
        this.revocationStore.revokeToken(token.jti, {
          expiresIn: JWTConfig.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
          reason: "token_reuse_detected",
        }),
      );

      await Promise.all(revokePromises);

      this.logger.warn(
        `Token family invalidated due to reuse detection: family=${family.substring(0, 8)}...`,
      );
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      const stack = error instanceof Error ? error.stack : undefined;
      this.logger.error(
        `Failed to invalidate token family: ${message}`,
        stack,
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
        secret: JWTConfig.SECRET,
        issuer: JWTConfig.ISSUER,
        audience: JWTConfig.AUDIENCE,
      }) as JwtPayload;

      // Verify it's a refresh token
      if (payload.type !== "refresh") {
        throw new UnauthorizedException("Invalid token type");
      }

      // Check if refresh token exists in database
      const storedToken = await this.prisma.refreshToken.findUnique({
        where: { jti: payload.jti },
      });

      if (!storedToken) {
        this.logger.warn(
          `Refresh attempt with unknown token: ${payload.jti.substring(0, 8)}...`,
        );
        throw new UnauthorizedException("Invalid refresh token");
      }

      // Use interactive transaction to prevent race condition on concurrent
      // refresh requests with the same token (check-then-update atomicity)
      const { user } = await this.prisma.$transaction(async (tx) => {
        // Re-fetch token inside transaction for atomicity
        const tokenRecord = await tx.refreshToken.findUnique({
          where: { jti: payload.jti },
        });

        if (!tokenRecord) {
          throw new UnauthorizedException("Invalid refresh token");
        }

        // Check if token was already used (replay attack detection)
        if (tokenRecord.used) {
          this.logger.error(
            `Token reuse detected! Token: ${payload.jti.substring(0, 8)}..., Family: ${payload.family?.substring(0, 8)}...`,
          );

          // Invalidate entire token family
          if (payload.family) {
            await this.invalidateTokenFamily(payload.family);
          }

          throw new UnauthorizedException(
            "Token reuse detected - all tokens in family have been invalidated",
          );
        }

        // Check if token is revoked
        if (tokenRecord.revoked) {
          throw new UnauthorizedException("Token has been revoked");
        }

        // Check if token is expired
        if (tokenRecord.expiresAt < new Date()) {
          throw new UnauthorizedException("Refresh token has expired");
        }

        // Verify user still exists and is active
        const txUser = await tx.user.findUnique({
          where: { id: payload.sub },
        });

        if (!txUser || txUser.status !== UserStatus.ACTIVE) {
          throw new UnauthorizedException("User account is not active");
        }

        // Atomically mark current refresh token as used
        await tx.refreshToken.update({
          where: { jti: payload.jti },
          data: {
            used: true,
            usedAt: new Date(),
          },
        });

        return { user: txUser };
      });

      // Outside transaction: Redis revocation and new token generation
      await this.revocationStore.revokeToken(payload.jti, {
        expiresIn: 300, // 5 minutes to detect concurrent reuse attempts
        reason: "refresh_token_rotated",
        userId: user.id,
        tenantId: user.tenantId,
      });

      // Generate new token pair with same family
      const newTokens = await this.generateTokens(user, payload.family);

      // Update replacedBy with actual new refresh token JTI (verified from generated token)
      try {
        const newPayload = this.jwtService.verify(newTokens.refresh_token, {
          secret: JWTConfig.SECRET,
          issuer: JWTConfig.ISSUER,
          audience: JWTConfig.AUDIENCE,
        }) as JwtPayload;
        await this.prisma.refreshToken.update({
          where: { jti: payload.jti },
          data: { replacedBy: newPayload.jti },
        });
      } catch (error) {
        const message = error instanceof Error ? error.message : String(error);
        this.logger.warn(
          `Failed to update refresh token chain for JTI ${payload.jti.substring(0, 8)}...: ${message}`,
        );
      }

      this.logger.log(
        `Refresh token rotated for user: ${user.id}, Old JTI: ${payload.jti.substring(0, 8)}...`,
      );

      return newTokens;
    } catch (error) {
      if (error instanceof UnauthorizedException) {
        throw error;
      }
      const message = error instanceof Error ? error.message : String(error);
      const stack = error instanceof Error ? error.stack : undefined;
      this.logger.error(`Token refresh error: ${message}`, stack);
      throw new UnauthorizedException("Invalid refresh token");
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

  /**
   * User registration
   * تسجيل مستخدم جديد
   */
  async register(registerDto: RegisterDto): Promise<TokenResponse> {
    const { password, phone, tenantId } = registerDto;
    const email = registerDto.email.toLowerCase().trim();

    // Handle name splitting: accept either `name` or `firstName`+`lastName`
    const names = splitFullName(registerDto.name, registerDto.firstName, registerDto.lastName);
    if (!names) {
      throw new BadRequestException(
        "Either 'name' or both 'firstName' and 'lastName' must be provided",
      );
    }
    const { firstName, lastName } = names;

    // Check if user already exists
    const existingUser = await this.prisma.user.findUnique({
      where: { email },
    });

    if (existingUser) {
      this.logger.warn(
        `Registration attempt with existing email`,
        { email: this.sanitizeForLog(email) },
      );
      throw new ConflictException("Email already registered");
    }

    // Hash password
    const passwordHash = await bcrypt.hash(password, BCRYPT_ROUNDS);

    // Create user with default tenant if not provided
    // Use the default tenant UUID from database (sahool-demo tenant)
    const defaultTenantId = tenantId || DEFAULT_TENANT_ID;

    const user = await this.prisma.user.create({
      data: {
        id: uuidv4(),
        email,
        passwordHash,
        firstName,
        lastName,
        phone: phone || null,
        tenantId: defaultTenantId,
        role: "FARMER", // Default role for self-registration
        status: UserStatus.ACTIVE, // Set to ACTIVE for immediate login
        emailVerified: false,
        phoneVerified: false,
      },
    });

    this.logger.log(`User registered successfully`, {
      userId: user.id,
      email: this.sanitizeForLog(email),
    });

    // Publish `sahool.user.created` so audit-service, notification-service,
    // and any future consumer can react. Self-registration was previously
    // bypassing the event bus entirely (the R-1a fix only covered the
    // admin path via UsersService.create) — this completes that work.
    // Fire-and-forget; degraded NATS does not block account creation.
    void this.userEvents?.publishUserCreated({
      tenantId: user.tenantId,
      userId: user.id,
      email: user.email,
      firstName: user.firstName ?? undefined,
      lastName: user.lastName ?? undefined,
      role: String(user.role),
      createdAt: user.createdAt,
    });

    // Generate tokens for immediate login
    const tokens = await this.generateTokens(user);

    return {
      ...tokens,
      user: {
        id: user.id,
        email: user.email,
        name: `${user.firstName} ${user.lastName}`.trim(),
        name_ar: user.nameAr || undefined,
        firstName: user.firstName,
        lastName: user.lastName,
        role: user.role,
        tenantId: user.tenantId,
        tenant_id: user.tenantId,
      },
    };
  }

  /**
   * Check if account is locked due to failed login attempts
   * التحقق مما إذا كان الحساب مقفلاً بسبب محاولات تسجيل الدخول الفاشلة
   */
  private async checkAccountLockout(userId: string): Promise<{
    isLocked: boolean;
    remainingMinutes?: number;
    failedAttempts: number;
  }> {
    const user = await this.prisma.user.findUnique({
      where: { id: userId },
      select: {
        failedLoginAttempts: true,
        lockoutUntil: true,
      },
    });

    if (!user) {
      return { isLocked: false, failedAttempts: 0 };
    }

    const failedAttempts = user.failedLoginAttempts || 0;

    // Check if currently locked
    if (user.lockoutUntil && user.lockoutUntil > new Date()) {
      const remainingMs = user.lockoutUntil.getTime() - Date.now();
      const remainingMinutes = Math.ceil(remainingMs / 60000);
      return { isLocked: true, remainingMinutes, failedAttempts };
    }

    return { isLocked: false, failedAttempts };
  }

  /**
   * Record failed login attempt and potentially lock account
   * تسجيل محاولة تسجيل دخول فاشلة وربما قفل الحساب
   */
  private async recordFailedLoginAttempt(userId: string): Promise<{
    isNowLocked: boolean;
    attemptsRemaining: number;
  }> {
    const user = await this.prisma.user.findUnique({
      where: { id: userId },
      select: { failedLoginAttempts: true },
    });

    const currentAttempts = (user?.failedLoginAttempts || 0) + 1;
    const attemptsRemaining = Math.max(0, LOCKOUT_CONFIG.MAX_FAILED_ATTEMPTS - currentAttempts);

    let lockoutUntil: Date | null = null;

    if (currentAttempts >= LOCKOUT_CONFIG.MAX_FAILED_ATTEMPTS) {
      // Lock the account
      lockoutUntil = new Date(
        Date.now() + LOCKOUT_CONFIG.LOCKOUT_DURATION_MINUTES * 60 * 1000
      );
      this.logger.warn(`Account locked due to ${currentAttempts} failed attempts`, {
        userId,
        lockoutUntil: lockoutUntil.toISOString(),
      });
    }

    await this.prisma.user.update({
      where: { id: userId },
      data: {
        failedLoginAttempts: currentAttempts,
        lockoutUntil,
        lastFailedLoginAt: new Date(),
      },
    });

    return {
      isNowLocked: lockoutUntil !== null,
      attemptsRemaining,
    };
  }

  /**
   * Reset failed login attempts after successful login
   * إعادة تعيين محاولات تسجيل الدخول الفاشلة بعد تسجيل دخول ناجح
   */
  private async resetFailedLoginAttempts(userId: string): Promise<void> {
    await this.prisma.user.update({
      where: { id: userId },
      data: {
        failedLoginAttempts: 0,
        lockoutUntil: null,
        lastFailedLoginAt: null,
      },
    });
  }

  /**
   * Send password reset email
   * إرسال بريد إلكتروني لإعادة تعيين كلمة المرور
   *
   * @param email - User's email address
   * @param firstName - User's first name for personalization
   * @param resetToken - The password reset token
   */
  private async sendPasswordResetEmail(
    email: string,
    firstName: string,
    resetToken: string,
  ): Promise<void> {
    // Get email configuration from environment variables
    const smtpHost = process.env.SMTP_HOST;
    const smtpPort = parseInt(process.env.SMTP_PORT || "587", 10);
    const smtpUser = process.env.SMTP_USER;
    const smtpPassword = process.env.SMTP_PASSWORD;
    const emailFrom = process.env.EMAIL_FROM || "noreply@sahool.app";
    const frontendUrl = process.env.FRONTEND_URL || "https://app.sahool.app";

    // Build the reset link URL
    const resetLink = `${frontendUrl}/reset-password?token=${resetToken}`;

    // Check if SMTP is configured
    if (!smtpHost || !smtpUser || !smtpPassword) {
      this.logger.warn(
        "SMTP not configured, skipping password reset email. Set SMTP_HOST, SMTP_USER, SMTP_PASSWORD environment variables.",
        { email: this.sanitizeForLog(email) },
      );
      // In development, log the reset link for testing
      if (process.env.NODE_ENV === "development") {
        this.logger.debug(`[DEV] Password reset link: ${resetLink}`);
      }
      return;
    }

    // Create nodemailer transporter
    const transporter = nodemailer.createTransport({
      host: smtpHost,
      port: smtpPort,
      secure: smtpPort === 465, // true for 465, false for other ports
      auth: {
        user: smtpUser,
        pass: smtpPassword,
      },
    });

    // Build bilingual email content (Arabic/English)
    const subject = "SAHOOL - Password Reset Request | طلب إعادة تعيين كلمة المرور";

    const htmlBody = `
<!DOCTYPE html>
<html dir="ltr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Password Reset | إعادة تعيين كلمة المرور</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
  <!-- English Section -->
  <div style="margin-bottom: 40px;">
    <h2 style="color: #2c5530;">Password Reset Request</h2>
    <p>Hello ${firstName},</p>
    <p>We received a request to reset your password for your SAHOOL account.</p>
    <p>Click the button below to reset your password:</p>
    <p style="text-align: center; margin: 30px 0;">
      <a href="${resetLink}"
         style="background-color: #2c5530; color: white; padding: 14px 28px; text-decoration: none; border-radius: 6px; display: inline-block; font-weight: bold;">
        Reset Password
      </a>
    </p>
    <p>Or copy and paste this link into your browser:</p>
    <p style="word-break: break-all; color: #666; font-size: 14px;">${resetLink}</p>
    <p><strong>This link will expire in 1 hour.</strong></p>
    <p>If you did not request a password reset, please ignore this email or contact support if you have concerns.</p>
  </div>

  <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">

  <!-- Arabic Section -->
  <div dir="rtl" style="text-align: right;">
    <h2 style="color: #2c5530;">طلب إعادة تعيين كلمة المرور</h2>
    <p>مرحباً ${firstName}،</p>
    <p>لقد تلقينا طلباً لإعادة تعيين كلمة المرور الخاصة بحسابك في ساهول.</p>
    <p>انقر على الزر أدناه لإعادة تعيين كلمة المرور:</p>
    <p style="text-align: center; margin: 30px 0;">
      <a href="${resetLink}"
         style="background-color: #2c5530; color: white; padding: 14px 28px; text-decoration: none; border-radius: 6px; display: inline-block; font-weight: bold;">
        إعادة تعيين كلمة المرور
      </a>
    </p>
    <p>أو انسخ والصق هذا الرابط في متصفحك:</p>
    <p style="word-break: break-all; color: #666; font-size: 14px;" dir="ltr">${resetLink}</p>
    <p><strong>ستنتهي صلاحية هذا الرابط خلال ساعة واحدة.</strong></p>
    <p>إذا لم تطلب إعادة تعيين كلمة المرور، يرجى تجاهل هذا البريد الإلكتروني أو الاتصال بالدعم إذا كانت لديك مخاوف.</p>
  </div>

  <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">

  <!-- Footer -->
  <div style="text-align: center; color: #888; font-size: 12px;">
    <p>SAHOOL - National Agricultural Intelligence Platform</p>
    <p>ساهول - المنصة الوطنية للذكاء الزراعي</p>
    <p>&copy; ${new Date().getFullYear()} KAFAAT. All rights reserved.</p>
  </div>
</body>
</html>
`;

    const textBody = `
Password Reset Request | طلب إعادة تعيين كلمة المرور
=====================================================

Hello ${firstName},

We received a request to reset your password for your SAHOOL account.

Reset your password by visiting this link:
${resetLink}

This link will expire in 1 hour.

If you did not request a password reset, please ignore this email.

-----------------------------------------------------

مرحباً ${firstName}،

لقد تلقينا طلباً لإعادة تعيين كلمة المرور الخاصة بحسابك في ساهول.

أعد تعيين كلمة المرور بزيارة هذا الرابط:
${resetLink}

ستنتهي صلاحية هذا الرابط خلال ساعة واحدة.

إذا لم تطلب إعادة تعيين كلمة المرور، يرجى تجاهل هذا البريد الإلكتروني.

-----------------------------------------------------
SAHOOL - National Agricultural Intelligence Platform
ساهول - المنصة الوطنية للذكاء الزراعي
`;

    try {
      this.logger.log("Sending password reset email", {
        email: this.sanitizeForLog(email),
        smtpHost,
      });

      await transporter.sendMail({
        from: emailFrom,
        to: email,
        subject,
        text: textBody,
        html: htmlBody,
      });

      this.logger.log("Password reset email sent successfully", {
        email: this.sanitizeForLog(email),
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      const stack = error instanceof Error ? error.stack : undefined;
      this.logger.error("Failed to send password reset email", {
        email: this.sanitizeForLog(email),
        error: message,
        stack,
      });
      // Don't throw error to prevent email enumeration
      // The caller will still return success message
    }
  }

  /**
   * Request password reset - generates reset token
   * طلب إعادة تعيين كلمة المرور - إنشاء رمز إعادة التعيين
   */
  async forgotPassword(email: string): Promise<{
    success: boolean;
    message: string;
  }> {
    // Find user by email
    const user = await this.prisma.user.findUnique({
      where: { email },
    });

    // Always return success to prevent email enumeration
    if (!user) {
      this.logger.log(`Password reset requested for non-existent email`, {
        email: this.sanitizeForLog(email),
      });
      return {
        success: true,
        message: "If an account with that email exists, a password reset link has been sent.",
      };
    }

    // Generate secure random token
    const resetToken = crypto.randomBytes(32).toString("hex");
    const resetTokenHash = crypto
      .createHash("sha256")
      .update(resetToken)
      .digest("hex");

    // Token expires in 1 hour
    const resetTokenExpiry = new Date(Date.now() + 60 * 60 * 1000);

    // Store hashed token in database
    await this.prisma.user.update({
      where: { id: user.id },
      data: {
        passwordResetToken: resetTokenHash,
        passwordResetExpiry: resetTokenExpiry,
      },
    });

    // Send password reset email
    await this.sendPasswordResetEmail(user.email, user.firstName, resetToken);

    this.logger.log(`Password reset email sent`, {
      userId: user.id,
      email: this.sanitizeForLog(email),
    });

    return {
      success: true,
      message: "If an account with that email exists, a password reset link has been sent.",
    };
  }

  /**
   * Reset password using token
   * إعادة تعيين كلمة المرور باستخدام الرمز
   */
  async resetPassword(token: string, newPassword: string, tenantId?: string): Promise<{
    success: boolean;
    message: string;
  }> {
    // Hash the provided token
    const tokenHash = crypto
      .createHash("sha256")
      .update(token)
      .digest("hex");

    // Find user with matching token that hasn't expired
    // SECURITY: Filter by tenantId to prevent cross-tenant password reset
    const user = await this.prisma.user.findFirst({
      where: {
        passwordResetToken: tokenHash,
        passwordResetExpiry: {
          gt: new Date(),
        },
        ...(tenantId && { tenantId }),
      },
    });

    if (!user) {
      this.logger.warn(`Invalid or expired password reset token used`);
      throw new BadRequestException("Invalid or expired password reset token");
    }

    // Validate new password
    if (newPassword.length < 8) {
      throw new BadRequestException("Password must be at least 8 characters long");
    }

    // Hash new password
    const passwordHash = await bcrypt.hash(newPassword, BCRYPT_ROUNDS);

    // Update password and clear reset token
    await this.prisma.user.update({
      where: { id: user.id },
      data: {
        passwordHash,
        passwordResetToken: null,
        passwordResetExpiry: null,
        // Reset failed login attempts on password change
        failedLoginAttempts: 0,
        lockoutUntil: null,
      },
    });

    // Revoke all existing refresh tokens for security
    await this.prisma.refreshToken.updateMany({
      where: { userId: user.id },
      data: { revoked: true },
    });

    this.logger.log(`Password reset successful`, {
      userId: user.id,
      email: this.sanitizeForLog(user.email),
    });

    return {
      success: true,
      message: "Password has been reset successfully. Please login with your new password.",
    };
  }

  /**
   * Send OTP for password reset or phone verification
   * إرسال رمز التحقق لإعادة تعيين كلمة المرور أو التحقق من الهاتف
   */
  async sendOtp(dto: SendOtpDto, tenantId?: string): Promise<{
    success: boolean;
    message: string;
    expiresIn?: number;
  }> {
    const { identifier, channel, purpose, language } = dto;

    // For password_reset, verify user exists (but don't reveal if not found)
    if (purpose === "password_reset") {
      // Check if identifier is email or phone
      // SECURITY: Filter by tenantId to prevent cross-tenant user enumeration
      const isEmail = identifier.includes("@");
      const user = await this.prisma.user.findFirst({
        where: {
          ...(isEmail ? { email: identifier } : { phone: identifier }),
          ...(tenantId && { tenantId }),
        },
      });

      if (!user) {
        this.logger.log(`OTP requested for non-existent user`, {
          identifier: this.sanitizeForLog(identifier),
          purpose,
        });
        // Return success to prevent enumeration
        return {
          success: true,
          message: "If an account exists, an OTP will be sent.",
          expiresIn: 300,
        };
      }
    }

    try {
      // Call notification service to send OTP
      const notificationServiceUrl =
        process.env.NOTIFICATION_SERVICE_URL || "http://notification-service:8110";

      const response = await fetch(`${notificationServiceUrl}/otp/send`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          identifier,
          channel,
          purpose,
          language: language || "en",
        }),
      });

      if (!response.ok) {
        const errorData = (await response.json().catch(() => ({}))) as {
          message?: string;
        };
        this.logger.error(`Failed to send OTP via notification service`, {
          identifier: this.sanitizeForLog(identifier),
          status: response.status,
          error: errorData,
        });
        throw new BadRequestException(
          errorData.message || "Failed to send OTP. Please try again later.",
        );
      }

      const result = (await response.json()) as {
        message?: string;
        expiresIn?: number;
      };

      this.logger.log(`OTP sent successfully`, {
        identifier: this.sanitizeForLog(identifier),
        channel,
        purpose,
      });

      return {
        success: true,
        message: result.message || "OTP has been sent successfully.",
        expiresIn: result.expiresIn || 300,
      };
    } catch (error) {
      if (error instanceof BadRequestException) {
        throw error;
      }
      const message = error instanceof Error ? error.message : String(error);
      const stack = error instanceof Error ? error.stack : undefined;
      this.logger.error(`Error sending OTP: ${message}`, stack);
      throw new BadRequestException(
        "Failed to send OTP. Please try again later.",
      );
    }
  }

  /**
   * Verify OTP and return reset token for password reset
   * التحقق من رمز OTP وإرجاع رمز إعادة التعيين لإعادة تعيين كلمة المرور
   */
  async verifyOtp(dto: VerifyOtpDto, tenantId?: string): Promise<{
    success: boolean;
    message: string;
    resetToken?: string;
    verified?: boolean;
  }> {
    const { identifier, otpCode, purpose } = dto;

    // OTP brute-force protection: max 5 attempts per identifier per 15 minutes
    const otpAttemptKey = `otp_attempts:${identifier}`;
    try {
      const attempts = await this.revocationStore.getOtpAttempts(otpAttemptKey);
      if (attempts >= 5) {
        this.logger.warn('OTP verification blocked: too many attempts', {
          identifier: this.sanitizeForLog(identifier),
        });
        throw new BadRequestException(
          'Too many verification attempts. Please wait 15 minutes and try again.',
        );
      }
      await this.revocationStore.incrementOtpAttempts(otpAttemptKey);
    } catch (error) {
      if (error instanceof BadRequestException) throw error;
      // If Redis is unavailable, allow the attempt but log warning
      this.logger.warn('OTP rate limit check failed (Redis unavailable), allowing attempt');
    }

    try {
      // Call notification service to verify OTP
      const notificationServiceUrl =
        process.env.NOTIFICATION_SERVICE_URL || "http://notification-service:8110";

      const response = await fetch(`${notificationServiceUrl}/otp/verify`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          identifier,
          otpCode,
          purpose,
        }),
      });

      if (!response.ok) {
        const errorData = (await response.json().catch(() => ({}))) as {
          message?: string;
        };
        this.logger.warn(`OTP verification failed`, {
          identifier: this.sanitizeForLog(identifier),
          status: response.status,
        });
        throw new BadRequestException(
          errorData.message || "Invalid or expired OTP code.",
        );
      }

      const result = (await response.json()) as {
        verified?: boolean;
        message?: string;
      };

      this.logger.log(`OTP verified successfully`, {
        identifier: this.sanitizeForLog(identifier),
        purpose,
      });

      // Reset OTP attempt counter on successful verification
      try {
        await this.revocationStore.resetOtpAttempts(`otp_attempts:${identifier}`);
      } catch {
        // Best effort
      }

      // For password_reset, generate a reset token
      if (purpose === "password_reset") {
        // Find user by identifier
        // SECURITY: Filter by tenantId to prevent cross-tenant password reset via OTP
        const isEmail = identifier.includes("@");
        const user = await this.prisma.user.findFirst({
          where: {
            ...(isEmail ? { email: identifier } : { phone: identifier }),
            ...(tenantId && { tenantId }),
          },
        });

        if (!user) {
          throw new BadRequestException("User not found.");
        }

        // Generate secure reset token
        const resetToken = crypto.randomBytes(32).toString("hex");
        const resetTokenHash = crypto
          .createHash("sha256")
          .update(resetToken)
          .digest("hex");

        // Token expires in 15 minutes (shorter than email reset for security)
        const resetTokenExpiry = new Date(Date.now() + 15 * 60 * 1000);

        // Store hashed token in database
        await this.prisma.user.update({
          where: { id: user.id },
          data: {
            passwordResetToken: resetTokenHash,
            passwordResetExpiry: resetTokenExpiry,
          },
        });

        this.logger.log(`Password reset token generated via OTP`, {
          userId: user.id,
          identifier: this.sanitizeForLog(identifier),
        });

        return {
          success: true,
          message: "OTP verified successfully. Use the reset token to set a new password.",
          resetToken,
        };
      }

      // For verify_phone, update user's phone verification status
      // SECURITY: Filter by tenantId to prevent cross-tenant phone verification
      if (purpose === "verify_phone") {
        const user = await this.prisma.user.findFirst({
          where: {
            phone: identifier,
            ...(tenantId && { tenantId }),
          },
        });

        if (user) {
          await this.prisma.user.update({
            where: { id: user.id },
            data: { phoneVerified: true },
          });

          this.logger.log(`Phone verified for user`, {
            userId: user.id,
            identifier: this.sanitizeForLog(identifier),
          });
        }

        return {
          success: true,
          message: "Phone number verified successfully.",
          verified: true,
        };
      }

      return {
        success: true,
        message: result.message || "OTP verified successfully.",
        verified: true,
      };
    } catch (error) {
      if (error instanceof BadRequestException) {
        throw error;
      }
      const message = error instanceof Error ? error.message : String(error);
      const stack = error instanceof Error ? error.stack : undefined;
      this.logger.error(`Error verifying OTP: ${message}`, stack);
      throw new BadRequestException(
        "Failed to verify OTP. Please try again.",
      );
    }
  }

  /**
   * Get progressive delay based on failed attempts
   * الحصول على التأخير التدريجي بناءً على المحاولات الفاشلة
   */
  private getProgressiveDelay(failedAttempts: number): number {
    const delays = LOCKOUT_CONFIG.PROGRESSIVE_DELAY_SECONDS;
    const index = Math.min(failedAttempts, delays.length - 1);
    return delays[index] * 1000; // Convert to milliseconds
  }
}
