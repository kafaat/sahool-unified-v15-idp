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
} from '@nestjs/common';
import {
  ApiTags,
  ApiOperation,
  ApiResponse,
  ApiBearerAuth,
  ApiBody,
} from '@nestjs/swagger';
import { Throttle, SkipThrottle } from '@nestjs/throttler';
import { Request } from 'express';
import { AuthService, LoginDto } from './auth.service';
import { JwtAuthGuard } from './jwt-auth.guard';
import { IsEmail, IsNotEmpty, IsString, MinLength } from 'class-validator';

// Extend Express Request to include user property set by JWT guard
interface AuthenticatedRequest extends Request {
  user?: { id: string; email: string; tenantId?: string };
}

// DTOs
class LoginRequestDto implements LoginDto {
  @ApiProperty({
    description: 'User email address',
    example: 'user@sahool.com',
  })
  @IsEmail({}, { message: 'Invalid email format' })
  @IsNotEmpty({ message: 'Email is required' })
  email: string;

  @ApiProperty({
    description: 'User password',
    example: 'SecurePassword123!',
  })
  @IsString()
  @IsNotEmpty({ message: 'Password is required' })
  @MinLength(8, { message: 'Password must be at least 8 characters long' })
  password: string;
}

class RefreshTokenDto {
  @ApiProperty({
    description: 'Refresh token',
    example: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
  })
  @IsString()
  @IsNotEmpty({ message: 'Refresh token is required' })
  refreshToken: string;
}

// Import ApiProperty
import { ApiProperty } from '@nestjs/swagger';

@ApiTags('Authentication')
@Controller('auth')
export class AuthController {
  constructor(private readonly authService: AuthService) {}

  /**
   * Login endpoint with token revocation support
   * نقطة تسجيل الدخول مع دعم إلغاء الرموز
   */
  @Post('login')
  @HttpCode(HttpStatus.OK)
  @Throttle({ default: { limit: 5, ttl: 60000 } }) // 5 requests per minute
  @ApiOperation({
    summary: 'User login',
    description:
      'Authenticate user with email and password. Returns JWT access and refresh tokens with JTI for revocation support.',
  })
  @ApiBody({ type: LoginRequestDto })
  @ApiResponse({
    status: 200,
    description: 'Login successful',
    schema: {
      type: 'object',
      properties: {
        access_token: { type: 'string', example: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' },
        refresh_token: { type: 'string', example: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' },
        expires_in: { type: 'number', example: 1800 },
        token_type: { type: 'string', example: 'Bearer' },
        user: {
          type: 'object',
          properties: {
            id: { type: 'string', example: 'usr_123456' },
            email: { type: 'string', example: 'user@sahool.com' },
            firstName: { type: 'string', example: 'Ahmed' },
            lastName: { type: 'string', example: 'Ali' },
            role: { type: 'string', example: 'FARMER' },
            tenantId: { type: 'string', example: 'tenant_123' },
          },
        },
      },
    },
  })
  @ApiResponse({ status: 401, description: 'Invalid credentials or account inactive' })
  @ApiResponse({ status: 429, description: 'Too many login attempts' })
  async login(
    @Body() loginDto: LoginRequestDto,
    @Req() request: Request,
  ) {
    const ip = request.ip || request.socket.remoteAddress;
    console.log(`Login attempt from IP: ${ip} for email: ${loginDto.email}`);

    return this.authService.login(loginDto);
  }

  /**
   * Logout endpoint - Revokes current token
   * نقطة تسجيل الخروج - إلغاء الرمز الحالي
   */
  @Post('logout')
  @HttpCode(HttpStatus.OK)
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth()
  @SkipThrottle() // No rate limiting needed for logout
  @ApiOperation({
    summary: 'User logout',
    description:
      'Logout current user and revoke the access token. Token will be added to Redis blacklist until expiration.',
  })
  @ApiResponse({
    status: 200,
    description: 'Logout successful - token revoked',
    schema: {
      type: 'object',
      properties: {
        success: { type: 'boolean', example: true },
        message: { type: 'string', example: 'Logged out successfully' },
      },
    },
  })
  @ApiResponse({ status: 401, description: 'Unauthorized - Invalid or missing token' })
  async logout(@Req() request: AuthenticatedRequest) {
    // Extract token from Authorization header
    const authorization = request.headers.authorization;
    if (!authorization) {
      throw new UnauthorizedException('No token provided');
    }

    const token = authorization.split(' ')[1];
    if (!token) {
      throw new UnauthorizedException('Invalid token format');
    }

    // Get user from request (set by JWT guard)
    const user = request.user as any;
    if (!user || !user.id) {
      throw new UnauthorizedException('User not found in request');
    }

    // Revoke token
    await this.authService.logout(token, user.id);

    return {
      success: true,
      message: 'Logged out successfully',
    };
  }

  /**
   * Logout from all devices - Revokes all user tokens
   * تسجيل الخروج من جميع الأجهزة - إلغاء جميع رموز المستخدم
   */
  @Post('logout-all')
  @HttpCode(HttpStatus.OK)
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth()
  @SkipThrottle()
  @ApiOperation({
    summary: 'Logout from all devices',
    description:
      'Logout user from all devices by revoking all tokens. All active sessions will be terminated.',
  })
  @ApiResponse({
    status: 200,
    description: 'Logged out from all devices successfully',
    schema: {
      type: 'object',
      properties: {
        success: { type: 'boolean', example: true },
        message: {
          type: 'string',
          example: 'Logged out from all devices successfully',
        },
      },
    },
  })
  @ApiResponse({ status: 401, description: 'Unauthorized' })
  async logoutAll(@Req() request: AuthenticatedRequest) {
    const user = request.user as any;
    if (!user || !user.id) {
      throw new UnauthorizedException('User not found in request');
    }

    await this.authService.logoutAll(user.id);

    return {
      success: true,
      message: 'Logged out from all devices successfully',
    };
  }

  /**
   * Refresh access token with rotation
   * تحديث رمز الوصول مع التدوير
   */
  @Post('refresh')
  @HttpCode(HttpStatus.OK)
  @Throttle({ default: { limit: 10, ttl: 60000 } }) // 10 requests per minute
  @ApiOperation({
    summary: 'Refresh access token with rotation',
    description:
      'Get a new access token and refresh token using a valid refresh token. Implements refresh token rotation for enhanced security.',
  })
  @ApiBody({ type: RefreshTokenDto })
  @ApiResponse({
    status: 200,
    description: 'Token refreshed successfully with rotation',
    schema: {
      type: 'object',
      properties: {
        access_token: { type: 'string', example: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' },
        refresh_token: { type: 'string', example: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' },
        expires_in: { type: 'number', example: 1800 },
        token_type: { type: 'string', example: 'Bearer' },
      },
    },
  })
  @ApiResponse({ status: 401, description: 'Invalid or expired refresh token, or token reuse detected' })
  @ApiResponse({ status: 429, description: 'Too many refresh requests' })
  async refreshToken(@Body() refreshTokenDto: RefreshTokenDto) {
    return this.authService.refreshToken(refreshTokenDto.refreshToken);
  }

  /**
   * Get current user info (for testing authentication)
   * الحصول على معلومات المستخدم الحالي
   */
  @Post('me')
  @HttpCode(HttpStatus.OK)
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth()
  @ApiOperation({
    summary: 'Get current user',
    description: 'Get information about the currently authenticated user.',
  })
  @ApiResponse({
    status: 200,
    description: 'Current user information',
  })
  @ApiResponse({ status: 401, description: 'Unauthorized' })
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
