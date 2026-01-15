/**
 * Authentication Controller for SAHOOL User Service
 * متحكم المصادقة لخدمة المستخدمين
 *
 * Provides endpoints for:
 * - User login
 * - Token refresh
 * - Logout (with token revocation)
 * - Logout from all devices
 */

import {
  Controller,
  Post,
  Body,
  HttpCode,
  HttpStatus,
  UseGuards,
  Req,
  UnauthorizedException,
} from "@nestjs/common";
import {
  ApiTags,
  ApiOperation,
  ApiResponse,
  ApiBearerAuth,
  ApiBody,
} from "@nestjs/swagger";
import { Throttle, SkipThrottle } from "@nestjs/throttler";
import { Request } from "express";
import { AuthService, LoginDto, RegisterDto, ForgotPasswordDto, ResetPasswordDto, SendOtpDto, VerifyOtpDto } from "./auth.service";
import { JwtAuthGuard } from "./jwt-auth.guard";
import { IsEmail, IsNotEmpty, IsString, MinLength, IsOptional, MaxLength, IsIn } from "class-validator";

// Extend Express Request to include user property set by JWT guard
interface AuthenticatedRequest extends Request {
  user?: { id: string; email: string; tenantId?: string };
}

// DTOs
class LoginRequestDto implements LoginDto {
  @ApiProperty({
    description: "User email address",
    example: "user@sahool.com",
  })
  @IsEmail({}, { message: "Invalid email format" })
  @IsNotEmpty({ message: "Email is required" })
  email: string;

  @ApiProperty({
    description: "User password",
    example: "SecurePassword123!",
  })
  @IsString()
  @IsNotEmpty({ message: "Password is required" })
  @MinLength(8, { message: "Password must be at least 8 characters long" })
  password: string;
}

class RefreshTokenDto {
  @ApiProperty({
    description: "Refresh token",
    example: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  })
  @IsString()
  @IsNotEmpty({ message: "Refresh token is required" })
  refreshToken: string;
}

class ForgotPasswordRequestDto implements ForgotPasswordDto {
  @ApiProperty({
    description: "User email address",
    example: "user@sahool.com",
  })
  @IsEmail({}, { message: "Invalid email format" })
  @IsNotEmpty({ message: "Email is required" })
  email: string;
}

class ResetPasswordRequestDto implements ResetPasswordDto {
  @ApiProperty({
    description: "Password reset token from email",
    example: "abc123def456...",
  })
  @IsString()
  @IsNotEmpty({ message: "Reset token is required" })
  token: string;

  @ApiProperty({
    description: "New password (min 8 characters)",
    example: "NewSecurePassword123!",
  })
  @IsString()
  @IsNotEmpty({ message: "New password is required" })
  @MinLength(8, { message: "Password must be at least 8 characters long" })
  newPassword: string;
}

class SendOtpRequestDto implements SendOtpDto {
  @ApiProperty({
    description: "User identifier (phone number or email)",
    example: "+967712345678",
  })
  @IsString()
  @IsNotEmpty({ message: "Identifier is required" })
  identifier: string;

  @ApiProperty({
    description: "Channel for OTP delivery",
    example: "sms",
    enum: ["sms", "whatsapp", "telegram", "email"],
  })
  @IsString()
  @IsNotEmpty({ message: "Channel is required" })
  @IsIn(["sms", "whatsapp", "telegram", "email"], { message: "Channel must be sms, whatsapp, telegram, or email" })
  channel: "sms" | "whatsapp" | "telegram" | "email";

  @ApiProperty({
    description: "Purpose of OTP",
    example: "password_reset",
    enum: ["password_reset", "verify_phone"],
  })
  @IsString()
  @IsNotEmpty({ message: "Purpose is required" })
  @IsIn(["password_reset", "verify_phone"], { message: "Purpose must be password_reset or verify_phone" })
  purpose: "password_reset" | "verify_phone";

  @ApiPropertyOptional({
    description: "Preferred language for OTP message",
    example: "ar",
  })
  @IsOptional()
  @IsString()
  language?: string;
}

class VerifyOtpRequestDto implements VerifyOtpDto {
  @ApiProperty({
    description: "User identifier (phone number or email)",
    example: "+967712345678",
  })
  @IsString()
  @IsNotEmpty({ message: "Identifier is required" })
  identifier: string;

  @ApiProperty({
    description: "OTP code received",
    example: "123456",
  })
  @IsString()
  @IsNotEmpty({ message: "OTP code is required" })
  @MinLength(4, { message: "OTP code must be at least 4 characters" })
  @MaxLength(8, { message: "OTP code must not exceed 8 characters" })
  otpCode: string;

  @ApiProperty({
    description: "Purpose of OTP verification",
    example: "password_reset",
  })
  @IsString()
  @IsNotEmpty({ message: "Purpose is required" })
  purpose: string;
}

// Import ApiProperty
import { ApiProperty, ApiPropertyOptional } from "@nestjs/swagger";

class RegisterRequestDto implements RegisterDto {
  @ApiProperty({
    description: "User email address",
    example: "farmer@sahool.com",
  })
  @IsEmail({}, { message: "Invalid email format" })
  @IsNotEmpty({ message: "Email is required" })
  email: string;

  @ApiProperty({
    description: "User password (min 8 characters)",
    example: "SecurePassword123!",
  })
  @IsString()
  @IsNotEmpty({ message: "Password is required" })
  @MinLength(8, { message: "Password must be at least 8 characters long" })
  password: string;

  @ApiProperty({
    description: "User first name",
    example: "أحمد",
  })
  @IsString()
  @IsNotEmpty({ message: "First name is required" })
  @MinLength(2, { message: "First name must be at least 2 characters" })
  @MaxLength(50, { message: "First name must not exceed 50 characters" })
  firstName: string;

  @ApiProperty({
    description: "User last name",
    example: "محمد",
  })
  @IsString()
  @IsNotEmpty({ message: "Last name is required" })
  @MinLength(2, { message: "Last name must be at least 2 characters" })
  @MaxLength(50, { message: "Last name must not exceed 50 characters" })
  lastName: string;

  @ApiPropertyOptional({
    description: "User phone number",
    example: "+967712345678",
  })
  @IsOptional()
  @IsString()
  phone?: string;

  @ApiPropertyOptional({
    description: "Tenant ID (optional, defaults to 'default-tenant')",
    example: "tenant_123",
  })
  @IsOptional()
  @IsString()
  tenantId?: string;
}

@ApiTags("Authentication")
@Controller("auth")
export class AuthController {
  constructor(private readonly authService: AuthService) {}

  /**
   * Login endpoint with token revocation support
   * نقطة تسجيل الدخول مع دعم إلغاء الرموز
   */
  @Post("login")
  @HttpCode(HttpStatus.OK)
  @Throttle({ default: { limit: 5, ttl: 60000 } }) // 5 requests per minute
  @ApiOperation({
    summary: "User login",
    description:
      "Authenticate user with email and password. Returns JWT access and refresh tokens with JTI for revocation support.",
  })
  @ApiBody({ type: LoginRequestDto })
  @ApiResponse({
    status: 200,
    description: "Login successful",
    schema: {
      type: "object",
      properties: {
        access_token: {
          type: "string",
          example: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        },
        refresh_token: {
          type: "string",
          example: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        },
        expires_in: { type: "number", example: 1800 },
        token_type: { type: "string", example: "Bearer" },
        user: {
          type: "object",
          properties: {
            id: { type: "string", example: "usr_123456" },
            email: { type: "string", example: "user@sahool.com" },
            firstName: { type: "string", example: "Ahmed" },
            lastName: { type: "string", example: "Ali" },
            role: { type: "string", example: "FARMER" },
            tenantId: { type: "string", example: "tenant_123" },
          },
        },
      },
    },
  })
  @ApiResponse({
    status: 401,
    description: "Invalid credentials or account inactive",
  })
  @ApiResponse({ status: 429, description: "Too many login attempts" })
  async login(@Body() loginDto: LoginRequestDto, @Req() request: Request) {
    const ip = request.ip || request.socket.remoteAddress;
    // SECURITY: Don't log email addresses - only log anonymized info for auditing
    // Use a hash or masked email for correlation if needed in production logging system
    console.log(`Login attempt from IP: ${ip}`);

    return this.authService.login(loginDto);
  }

  /**
   * Register endpoint - Create new user account
   * نقطة التسجيل - إنشاء حساب مستخدم جديد
   */
  @Post("register")
  @HttpCode(HttpStatus.CREATED)
  @Throttle({ default: { limit: 10, ttl: 60000 } }) // 10 requests per minute
  @ApiOperation({
    summary: "User registration",
    description:
      "Create a new user account. Returns JWT tokens for immediate login after successful registration.",
  })
  @ApiBody({ type: RegisterRequestDto })
  @ApiResponse({
    status: 201,
    description: "Registration successful",
    schema: {
      type: "object",
      properties: {
        access_token: {
          type: "string",
          example: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        },
        refresh_token: {
          type: "string",
          example: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        },
        expires_in: { type: "number", example: 1800 },
        token_type: { type: "string", example: "Bearer" },
        user: {
          type: "object",
          properties: {
            id: { type: "string", example: "usr_123456" },
            email: { type: "string", example: "farmer@sahool.com" },
            firstName: { type: "string", example: "أحمد" },
            lastName: { type: "string", example: "محمد" },
            role: { type: "string", example: "FARMER" },
            tenantId: { type: "string", example: "default-tenant" },
          },
        },
      },
    },
  })
  @ApiResponse({
    status: 400,
    description: "Invalid registration data",
  })
  @ApiResponse({
    status: 401,
    description: "Email already registered",
  })
  @ApiResponse({ status: 429, description: "Too many registration attempts" })
  async register(@Body() registerDto: RegisterRequestDto, @Req() request: Request) {
    const ip = request.ip || request.socket.remoteAddress;
    console.log(`Registration attempt from IP: ${ip}`);

    return this.authService.register(registerDto);
  }

  /**
   * Forgot password - Request password reset
   * نسيان كلمة المرور - طلب إعادة تعيين كلمة المرور
   */
  @Post("forgot-password")
  @HttpCode(HttpStatus.OK)
  @Throttle({ default: { limit: 3, ttl: 60000 } }) // 3 requests per minute to prevent abuse
  @ApiOperation({
    summary: "Request password reset",
    description:
      "Request a password reset link to be sent to the user's email address. Always returns success to prevent email enumeration.",
  })
  @ApiBody({ type: ForgotPasswordRequestDto })
  @ApiResponse({
    status: 200,
    description: "Password reset request processed",
    schema: {
      type: "object",
      properties: {
        success: { type: "boolean", example: true },
        message: {
          type: "string",
          example: "If an account with that email exists, a password reset link has been sent.",
        },
      },
    },
  })
  @ApiResponse({ status: 429, description: "Too many password reset requests" })
  async forgotPassword(@Body() dto: ForgotPasswordRequestDto, @Req() request: Request) {
    const ip = request.ip || request.socket.remoteAddress;
    console.log(`Password reset request from IP: ${ip}`);

    return this.authService.forgotPassword(dto.email);
  }

  /**
   * Reset password - Set new password using reset token
   * إعادة تعيين كلمة المرور - تعيين كلمة مرور جديدة باستخدام رمز إعادة التعيين
   */
  @Post("reset-password")
  @HttpCode(HttpStatus.OK)
  @Throttle({ default: { limit: 5, ttl: 60000 } }) // 5 requests per minute
  @ApiOperation({
    summary: "Reset password with token",
    description:
      "Reset user password using the token received via email. The token is valid for 1 hour.",
  })
  @ApiBody({ type: ResetPasswordRequestDto })
  @ApiResponse({
    status: 200,
    description: "Password reset successful",
    schema: {
      type: "object",
      properties: {
        success: { type: "boolean", example: true },
        message: {
          type: "string",
          example: "Password has been reset successfully. Please login with your new password.",
        },
      },
    },
  })
  @ApiResponse({
    status: 400,
    description: "Invalid or expired reset token",
  })
  @ApiResponse({ status: 429, description: "Too many reset attempts" })
  async resetPassword(@Body() dto: ResetPasswordRequestDto, @Req() request: Request) {
    const ip = request.ip || request.socket.remoteAddress;
    console.log(`Password reset attempt from IP: ${ip}`);

    return this.authService.resetPassword(dto.token, dto.newPassword);
  }

  /**
   * Send OTP for password reset or phone verification
   * إرسال رمز التحقق لإعادة تعيين كلمة المرور أو التحقق من الهاتف
   */
  @Post("send-otp")
  @HttpCode(HttpStatus.OK)
  @Throttle({ default: { limit: 3, ttl: 60000 } }) // 3 requests per minute to prevent abuse
  @ApiOperation({
    summary: "Send OTP for password reset or verification",
    description:
      "Send a one-time password (OTP) to the user via SMS, WhatsApp, Telegram, or email for password reset or phone verification.",
  })
  @ApiBody({ type: SendOtpRequestDto })
  @ApiResponse({
    status: 200,
    description: "OTP sent successfully",
    schema: {
      type: "object",
      properties: {
        success: { type: "boolean", example: true },
        message: {
          type: "string",
          example: "OTP has been sent to your phone/email.",
        },
        expiresIn: { type: "number", example: 300 },
      },
    },
  })
  @ApiResponse({
    status: 400,
    description: "Invalid request parameters",
  })
  @ApiResponse({ status: 429, description: "Too many OTP requests" })
  async sendOtp(@Body() dto: SendOtpRequestDto, @Req() request: Request) {
    const ip = request.ip || request.socket.remoteAddress;
    console.log(`OTP send request from IP: ${ip}`);

    return this.authService.sendOtp(dto);
  }

  /**
   * Verify OTP and get reset token
   * التحقق من رمز OTP والحصول على رمز إعادة التعيين
   */
  @Post("verify-otp")
  @HttpCode(HttpStatus.OK)
  @Throttle({ default: { limit: 5, ttl: 60000 } }) // 5 requests per minute
  @ApiOperation({
    summary: "Verify OTP and get reset token",
    description:
      "Verify the OTP code sent to the user. For password_reset purpose, returns a reset token that can be used with the reset-password endpoint.",
  })
  @ApiBody({ type: VerifyOtpRequestDto })
  @ApiResponse({
    status: 200,
    description: "OTP verified successfully",
    schema: {
      type: "object",
      properties: {
        success: { type: "boolean", example: true },
        message: {
          type: "string",
          example: "OTP verified successfully.",
        },
        resetToken: {
          type: "string",
          example: "abc123def456...",
          description: "Reset token (only for password_reset purpose)",
        },
      },
    },
  })
  @ApiResponse({
    status: 400,
    description: "Invalid or expired OTP",
  })
  @ApiResponse({ status: 429, description: "Too many verification attempts" })
  async verifyOtp(@Body() dto: VerifyOtpRequestDto, @Req() request: Request) {
    const ip = request.ip || request.socket.remoteAddress;
    console.log(`OTP verification attempt from IP: ${ip}`);

    return this.authService.verifyOtp(dto);
  }

  /**
   * Logout endpoint - Revokes current token
   * نقطة تسجيل الخروج - إلغاء الرمز الحالي
   */
  @Post("logout")
  @HttpCode(HttpStatus.OK)
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth()
  @SkipThrottle() // No rate limiting needed for logout
  @ApiOperation({
    summary: "User logout",
    description:
      "Logout current user and revoke the access token. Token will be added to Redis blacklist until expiration.",
  })
  @ApiResponse({
    status: 200,
    description: "Logout successful - token revoked",
    schema: {
      type: "object",
      properties: {
        success: { type: "boolean", example: true },
        message: { type: "string", example: "Logged out successfully" },
      },
    },
  })
  @ApiResponse({
    status: 401,
    description: "Unauthorized - Invalid or missing token",
  })
  async logout(@Req() request: AuthenticatedRequest) {
    // Extract token from Authorization header with secure validation
    const authorization = request.headers.authorization;
    if (!authorization) {
      throw new UnauthorizedException("No token provided");
    }

    // SECURITY: Validate Bearer token format properly
    const parts = authorization.split(" ");
    if (parts.length !== 2 || parts[0] !== "Bearer") {
      throw new UnauthorizedException(
        'Invalid token format: expected "Bearer <token>"',
      );
    }
    const token = parts[1];
    if (!token || token.length < 10) {
      throw new UnauthorizedException("Invalid token: token is too short");
    }

    // Get user from request (set by JWT guard)
    const user = request.user as any;
    if (!user || !user.id) {
      throw new UnauthorizedException("User not found in request");
    }

    // Revoke token
    await this.authService.logout(token, user.id);

    return {
      success: true,
      message: "Logged out successfully",
    };
  }

  /**
   * Logout from all devices - Revokes all user tokens
   * تسجيل الخروج من جميع الأجهزة - إلغاء جميع رموز المستخدم
   */
  @Post("logout-all")
  @HttpCode(HttpStatus.OK)
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth()
  @SkipThrottle()
  @ApiOperation({
    summary: "Logout from all devices",
    description:
      "Logout user from all devices by revoking all tokens. All active sessions will be terminated.",
  })
  @ApiResponse({
    status: 200,
    description: "Logged out from all devices successfully",
    schema: {
      type: "object",
      properties: {
        success: { type: "boolean", example: true },
        message: {
          type: "string",
          example: "Logged out from all devices successfully",
        },
      },
    },
  })
  @ApiResponse({ status: 401, description: "Unauthorized" })
  async logoutAll(@Req() request: AuthenticatedRequest) {
    const user = request.user as any;
    if (!user || !user.id) {
      throw new UnauthorizedException("User not found in request");
    }

    await this.authService.logoutAll(user.id);

    return {
      success: true,
      message: "Logged out from all devices successfully",
    };
  }

  /**
   * Refresh access token with rotation
   * تحديث رمز الوصول مع التدوير
   */
  @Post("refresh")
  @HttpCode(HttpStatus.OK)
  @Throttle({ default: { limit: 10, ttl: 60000 } }) // 10 requests per minute
  @ApiOperation({
    summary: "Refresh access token with rotation",
    description:
      "Get a new access token and refresh token using a valid refresh token. Implements refresh token rotation for enhanced security.",
  })
  @ApiBody({ type: RefreshTokenDto })
  @ApiResponse({
    status: 200,
    description: "Token refreshed successfully with rotation",
    schema: {
      type: "object",
      properties: {
        access_token: {
          type: "string",
          example: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        },
        refresh_token: {
          type: "string",
          example: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        },
        expires_in: { type: "number", example: 1800 },
        token_type: { type: "string", example: "Bearer" },
      },
    },
  })
  @ApiResponse({
    status: 401,
    description: "Invalid or expired refresh token, or token reuse detected",
  })
  @ApiResponse({ status: 429, description: "Too many refresh requests" })
  async refreshToken(@Body() refreshTokenDto: RefreshTokenDto) {
    return this.authService.refreshToken(refreshTokenDto.refreshToken);
  }

  /**
   * Get current user info (for testing authentication)
   * الحصول على معلومات المستخدم الحالي
   */
  @Post("me")
  @HttpCode(HttpStatus.OK)
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth()
  @ApiOperation({
    summary: "Get current user",
    description: "Get information about the currently authenticated user.",
  })
  @ApiResponse({
    status: 200,
    description: "Current user information",
  })
  @ApiResponse({ status: 401, description: "Unauthorized" })
  async getCurrentUser(@Req() request: AuthenticatedRequest) {
    const user = request.user as any;

    return {
      success: true,
      data: {
        id: user.id,
        email: user.email,
        roles: user.roles,
        tenantId: user.tenantId,
      },
    };
  }
}
