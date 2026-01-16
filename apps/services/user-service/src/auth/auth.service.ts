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
  BadRequestException,
  Logger,
} from "@nestjs/common";
import { JwtService } from "@nestjs/jwt";
import * as bcrypt from "bcryptjs";
import * as crypto from "crypto";
import { v4 as uuidv4 } from "uuid";
import { PrismaService } from "../prisma/prisma.service";
import { RedisTokenRevocationStore } from "../utils/token-revocation";
import { JWTConfig } from "../utils/jwt.config";
import { UserStatus } from "../utils/validation";

export interface LoginDto {
  email: string;
  password: string;
}

export interface RegisterDto {
  email: string;
  password: string;
  firstName: string;
  lastName: string;
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
    const { email, password } = loginDto;

    // Find user by email
    const user = await this.prisma.user.findUnique({
      where: { email },
    });

    if (!user) {
      this.logger.warn(
        `Login attempt failed: User not found`,
        { email: this.sanitizeForLog(email) },
      );
      throw new UnauthorizedException("Invalid email or password");
    }

    // Check if account is locked
    const lockoutStatus = await this.checkAccountLockout(user.id);
    if (lockoutStatus.isLocked) {
      this.logger.warn(
        `Login attempt blocked: Account is locked`,
        { email: this.sanitizeForLog(email), remainingMinutes: lockoutStatus.remainingMinutes },
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
          email: this.sanitizeForLog(email),
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
        { email: this.sanitizeForLog(email) },
      );
      throw new UnauthorizedException(
        `Account is ${user.status.toLowerCase()}. Please contact support.`,
      );
    }

    // Check if email is verified (optional based on your requirements)
    if (!user.emailVerified) {
      this.logger.warn(
        `Login attempt: Email not verified`,
        { email: this.sanitizeForLog(email) },
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
      email: this.sanitizeForLog(email),
    });

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
      this.logger.error(`Logout error: ${error.message}`, error.stack);
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
      this.logger.error(`Logout all error: ${error.message}`, error.stack);
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
      });

      // Revoke each token in Redis
      const revokePromises = familyTokens.map((token) =>
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
          "Token reuse detected - all tokens in family have been invalidated",
        );
      }

      // Check if token is revoked
      if (storedToken.revoked) {
        this.logger.warn(
          `Refresh attempt with revoked token: ${payload.jti.substring(0, 8)}...`,
        );
        throw new UnauthorizedException("Token has been revoked");
      }

      // Check if token is expired
      if (storedToken.expiresAt < new Date()) {
        this.logger.warn(
          `Refresh attempt with expired token: ${payload.jti.substring(0, 8)}...`,
        );
        throw new UnauthorizedException("Refresh token has expired");
      }

      // Verify user still exists and is active
      const user = await this.prisma.user.findUnique({
        where: { id: payload.sub },
      });

      if (!user || user.status !== UserStatus.ACTIVE) {
        throw new UnauthorizedException("User account is not active");
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
        reason: "refresh_token_rotated",
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
    const { email, password, firstName, lastName, phone, tenantId } = registerDto;

    // Check if user already exists
    const existingUser = await this.prisma.user.findUnique({
      where: { email },
    });

    if (existingUser) {
      this.logger.warn(
        `Registration attempt with existing email`,
        { email: this.sanitizeForLog(email) },
      );
      throw new UnauthorizedException("Email already registered");
    }

    // Hash password
    const saltRounds = 12;
    const passwordHash = await bcrypt.hash(password, saltRounds);

    // Create user with default tenant if not provided
    const defaultTenantId = tenantId || "default-tenant";

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

    // Generate tokens for immediate login
    const tokens = await this.generateTokens(user);

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

    // TODO: Send email with reset link
    // The reset link should be: ${FRONTEND_URL}/reset-password?token=${resetToken}
    // For now, we log it (in production, send via email service)
    this.logger.log(`Password reset token generated for user`, {
      userId: user.id,
      email: this.sanitizeForLog(email),
      // In production, NEVER log the actual token
      // This is only for development/testing
      tokenPreview: process.env.NODE_ENV === "development" ? resetToken.substring(0, 8) + "..." : "[hidden]",
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
  async resetPassword(token: string, newPassword: string): Promise<{
    success: boolean;
    message: string;
  }> {
    // Hash the provided token
    const tokenHash = crypto
      .createHash("sha256")
      .update(token)
      .digest("hex");

    // Find user with matching token that hasn't expired
    const user = await this.prisma.user.findFirst({
      where: {
        passwordResetToken: tokenHash,
        passwordResetExpiry: {
          gt: new Date(),
        },
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
    const saltRounds = 12;
    const passwordHash = await bcrypt.hash(newPassword, saltRounds);

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
  async sendOtp(dto: SendOtpDto): Promise<{
    success: boolean;
    message: string;
    expiresIn?: number;
  }> {
    const { identifier, channel, purpose, language } = dto;

    // For password_reset, verify user exists (but don't reveal if not found)
    if (purpose === "password_reset") {
      // Check if identifier is email or phone
      const isEmail = identifier.includes("@");
      const user = await this.prisma.user.findFirst({
        where: isEmail ? { email: identifier } : { phone: identifier },
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
        const errorData = await response.json().catch(() => ({}));
        this.logger.error(`Failed to send OTP via notification service`, {
          identifier: this.sanitizeForLog(identifier),
          status: response.status,
          error: errorData,
        });
        throw new BadRequestException(
          errorData.message || "Failed to send OTP. Please try again later.",
        );
      }

      const result = await response.json();

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
      this.logger.error(`Error sending OTP: ${error.message}`, error.stack);
      throw new BadRequestException(
        "Failed to send OTP. Please try again later.",
      );
    }
  }

  /**
   * Verify OTP and return reset token for password reset
   * التحقق من رمز OTP وإرجاع رمز إعادة التعيين لإعادة تعيين كلمة المرور
   */
  async verifyOtp(dto: VerifyOtpDto): Promise<{
    success: boolean;
    message: string;
    resetToken?: string;
    verified?: boolean;
  }> {
    const { identifier, otpCode, purpose } = dto;

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
        const errorData = await response.json().catch(() => ({}));
        this.logger.warn(`OTP verification failed`, {
          identifier: this.sanitizeForLog(identifier),
          status: response.status,
        });
        throw new BadRequestException(
          errorData.message || "Invalid or expired OTP code.",
        );
      }

      const result = await response.json();

      this.logger.log(`OTP verified successfully`, {
        identifier: this.sanitizeForLog(identifier),
        purpose,
      });

      // For password_reset, generate a reset token
      if (purpose === "password_reset") {
        // Find user by identifier
        const isEmail = identifier.includes("@");
        const user = await this.prisma.user.findFirst({
          where: isEmail ? { email: identifier } : { phone: identifier },
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
      if (purpose === "verify_phone") {
        const user = await this.prisma.user.findFirst({
          where: { phone: identifier },
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
      this.logger.error(`Error verifying OTP: ${error.message}`, error.stack);
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
