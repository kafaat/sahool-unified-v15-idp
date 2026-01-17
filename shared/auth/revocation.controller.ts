/**
 * Token Revocation Controller for NestJS
 * متحكم إلغاء الرموز لـ NestJS
 *
 * Provides REST API endpoints for token revocation operations.
 */

import {
  Controller,
  Post,
  Get,
  Body,
  Param,
  UseGuards,
  Request,
  HttpStatus,
  HttpException,
  Logger,
  ForbiddenException,
} from "@nestjs/common";
import {
  ApiTags,
  ApiOperation,
  ApiResponse,
  ApiBearerAuth,
  ApiBody,
} from "@nestjs/swagger";
import { JwtService } from "@nestjs/jwt";
import { RedisTokenRevocationStore, RevocationStats } from "./token-revocation";
import { JwtAuthGuard } from "./jwt.guard";
import { AuthenticatedUser, JwtPayload } from "./jwt.strategy";

// ─────────────────────────────────────────────────────────────────────────────
// DTOs (Data Transfer Objects)
// ─────────────────────────────────────────────────────────────────────────────

import { IsString, IsOptional, IsNotEmpty } from "class-validator";
import { ApiProperty } from "@nestjs/swagger";

/**
 * Request to revoke a single token
 */
export class RevokeTokenDto {
  @ApiProperty({
    description: "JWT ID to revoke",
    example: "550e8400-e29b-41d4-a716-446655440000",
  })
  @IsString()
  @IsNotEmpty()
  jti: string;

  @ApiProperty({
    description: "Reason for revocation",
    example: "user_logout",
    required: false,
  })
  @IsString()
  @IsOptional()
  reason?: string = "manual";
}

/**
 * Request to revoke all tokens for a user
 */
export class RevokeUserTokensDto {
  @ApiProperty({
    description: "User ID",
    example: "user-123",
  })
  @IsString()
  @IsNotEmpty()
  userId: string;

  @ApiProperty({
    description: "Reason for revocation",
    example: "password_change",
    required: false,
  })
  @IsString()
  @IsOptional()
  reason?: string = "manual";
}

/**
 * Request to revoke all tokens for a tenant
 */
export class RevokeTenantTokensDto {
  @ApiProperty({
    description: "Tenant ID",
    example: "tenant-456",
  })
  @IsString()
  @IsNotEmpty()
  tenantId: string;

  @ApiProperty({
    description: "Reason for revocation",
    example: "security_breach",
    required: false,
  })
  @IsString()
  @IsOptional()
  reason?: string = "security";
}

/**
 * Response for revocation operations
 */
export class RevocationResponse {
  @ApiProperty({ description: "Whether operation succeeded" })
  success: boolean;

  @ApiProperty({ description: "Response message" })
  message: string;

  @ApiProperty({ description: "Number of tokens revoked", required: false })
  revokedCount?: number;
}

/**
 * Response for token status check
 */
export class TokenStatusResponse {
  @ApiProperty({ description: "Whether token is revoked" })
  isRevoked: boolean;

  @ApiProperty({ description: "Revocation reason", required: false })
  reason?: string;

  @ApiProperty({ description: "When token was revoked", required: false })
  revokedAt?: number;
}

// ─────────────────────────────────────────────────────────────────────────────
// Controller
// ─────────────────────────────────────────────────────────────────────────────

@ApiTags("Token Revocation")
@Controller("auth/revocation")
export class RevocationController {
  private readonly logger = new Logger(RevocationController.name);

  constructor(
    private readonly revocationStore: RedisTokenRevocationStore,
    private readonly jwtService: JwtService,
  ) {}

  /**
   * Revoke a single token by JTI
   * إلغاء رمز واحد بواسطة JTI
   */
  @Post("revoke")
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth()
  @ApiOperation({
    summary: "Revoke a single token",
    description: "Revoke a specific token by its JTI (JWT ID)",
  })
  @ApiResponse({
    status: HttpStatus.OK,
    description: "Token revoked successfully",
    type: RevocationResponse,
  })
  @ApiResponse({
    status: HttpStatus.UNAUTHORIZED,
    description: "Unauthorized",
  })
  @ApiBody({ type: RevokeTokenDto })
  async revokeToken(
    @Body() dto: RevokeTokenDto,
    @Request() req: any,
  ): Promise<RevocationResponse> {
    try {
      const user: AuthenticatedUser = req.user;

      const success = await this.revocationStore.revokeToken(dto.jti, {
        reason: dto.reason,
        userId: user.id,
      });

      if (success) {
        return {
          success: true,
          message: "Token revoked successfully",
          revokedCount: 1,
        };
      } else {
        throw new HttpException(
          "Failed to revoke token",
          HttpStatus.INTERNAL_SERVER_ERROR,
        );
      }
    } catch (error) {
      this.logger.error(`Error revoking token: ${error.message}`);
      throw new HttpException(
        `Failed to revoke token: ${error.message}`,
        HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }

  /**
   * Revoke current token (logout)
   * إلغاء الرمز الحالي (تسجيل الخروج)
   */
  @Post("revoke-current")
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth()
  @ApiOperation({
    summary: "Revoke current token",
    description: "Revoke the currently authenticated token (logout)",
  })
  @ApiResponse({
    status: HttpStatus.OK,
    description: "Successfully logged out",
    type: RevocationResponse,
  })
  async revokeCurrentToken(@Request() req: any): Promise<RevocationResponse> {
    try {
      // Extract token from request
      const authorization = req.headers.authorization;
      if (!authorization) {
        throw new HttpException("No token provided", HttpStatus.BAD_REQUEST);
      }

      const token = authorization.split(" ")[1];
      const payload = this.jwtService.decode(token) as JwtPayload;

      if (!payload || !payload.jti) {
        throw new HttpException(
          "Token does not have JTI claim",
          HttpStatus.BAD_REQUEST,
        );
      }

      const user: AuthenticatedUser = req.user;

      // Revoke token
      const success = await this.revocationStore.revokeToken(payload.jti, {
        reason: "user_logout",
        userId: user.id,
      });

      if (success) {
        return {
          success: true,
          message: "Successfully logged out",
          revokedCount: 1,
        };
      } else {
        throw new HttpException(
          "Failed to logout",
          HttpStatus.INTERNAL_SERVER_ERROR,
        );
      }
    } catch (error) {
      if (error instanceof HttpException) {
        throw error;
      }

      this.logger.error(`Error revoking current token: ${error.message}`);
      throw new HttpException(
        `Failed to logout: ${error.message}`,
        HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }

  /**
   * Revoke all tokens for a user
   * إلغاء جميع رموز المستخدم
   */
  @Post("revoke-user-tokens")
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth()
  @ApiOperation({
    summary: "Revoke all user tokens",
    description: "Revoke all tokens for a specific user",
  })
  @ApiResponse({
    status: HttpStatus.OK,
    description: "All user tokens revoked",
    type: RevocationResponse,
  })
  @ApiResponse({
    status: HttpStatus.FORBIDDEN,
    description: "Forbidden - can only revoke own tokens",
  })
  @ApiBody({ type: RevokeUserTokensDto })
  async revokeUserTokens(
    @Body() dto: RevokeUserTokensDto,
    @Request() req: any,
  ): Promise<RevocationResponse> {
    const user: AuthenticatedUser = req.user;

    // Check authorization
    const isAdmin =
      user.roles.includes("admin") || user.roles.includes("superadmin");

    if (dto.userId !== user.id && !isAdmin) {
      throw new ForbiddenException("You can only revoke your own tokens");
    }

    try {
      const success = await this.revocationStore.revokeAllUserTokens(
        dto.userId,
        dto.reason,
      );

      if (success) {
        return {
          success: true,
          message: `All tokens revoked for user ${dto.userId}`,
        };
      } else {
        throw new HttpException(
          "Failed to revoke user tokens",
          HttpStatus.INTERNAL_SERVER_ERROR,
        );
      }
    } catch (error) {
      if (error instanceof HttpException) {
        throw error;
      }

      this.logger.error(`Error revoking user tokens: ${error.message}`);
      throw new HttpException(
        `Failed to revoke user tokens: ${error.message}`,
        HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }

  /**
   * Revoke all current user's tokens
   * إلغاء جميع رموز المستخدم الحالي
   */
  @Post("revoke-all")
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth()
  @ApiOperation({
    summary: "Revoke all current user's tokens",
    description: "Revoke all tokens for the currently authenticated user",
  })
  @ApiResponse({
    status: HttpStatus.OK,
    description: "All tokens revoked",
    type: RevocationResponse,
  })
  async revokeAllCurrentUserTokens(
    @Request() req: any,
  ): Promise<RevocationResponse> {
    try {
      const user: AuthenticatedUser = req.user;

      const success = await this.revocationStore.revokeAllUserTokens(
        user.id,
        "user_logout_all",
      );

      if (success) {
        return {
          success: true,
          message:
            "All your tokens have been revoked. Logged out from all devices.",
        };
      } else {
        throw new HttpException(
          "Failed to revoke all tokens",
          HttpStatus.INTERNAL_SERVER_ERROR,
        );
      }
    } catch (error) {
      this.logger.error(`Error revoking all user tokens: ${error.message}`);
      throw new HttpException(
        `Failed to revoke all tokens: ${error.message}`,
        HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }

  /**
   * Revoke all tenant tokens (Admin only)
   * إلغاء جميع رموز المستأجر (للمسؤولين فقط)
   */
  @Post("revoke-tenant-tokens")
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth()
  @ApiOperation({
    summary: "Revoke all tenant tokens (Admin only)",
    description:
      "Revoke all tokens for a specific tenant (requires admin privileges)",
  })
  @ApiResponse({
    status: HttpStatus.OK,
    description: "All tenant tokens revoked",
    type: RevocationResponse,
  })
  @ApiResponse({
    status: HttpStatus.FORBIDDEN,
    description: "Forbidden - admin privileges required",
  })
  @ApiBody({ type: RevokeTenantTokensDto })
  async revokeTenantTokens(
    @Body() dto: RevokeTenantTokensDto,
    @Request() req: any,
  ): Promise<RevocationResponse> {
    const user: AuthenticatedUser = req.user;

    // Check admin authorization
    const isAdmin =
      user.roles.includes("admin") || user.roles.includes("superadmin");

    if (!isAdmin) {
      throw new ForbiddenException("Admin privileges required");
    }

    try {
      const success = await this.revocationStore.revokeAllTenantTokens(
        dto.tenantId,
        dto.reason,
      );

      if (success) {
        return {
          success: true,
          message: `All tokens revoked for tenant ${dto.tenantId}`,
        };
      } else {
        throw new HttpException(
          "Failed to revoke tenant tokens",
          HttpStatus.INTERNAL_SERVER_ERROR,
        );
      }
    } catch (error) {
      if (error instanceof HttpException) {
        throw error;
      }

      this.logger.error(`Error revoking tenant tokens: ${error.message}`);
      throw new HttpException(
        `Failed to revoke tenant tokens: ${error.message}`,
        HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }

  /**
   * Check token status
   * التحقق من حالة الرمز
   */
  @Get("status/:jti")
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth()
  @ApiOperation({
    summary: "Check token status",
    description: "Check if a specific token is revoked",
  })
  @ApiResponse({
    status: HttpStatus.OK,
    description: "Token status",
    type: TokenStatusResponse,
  })
  async checkTokenStatus(
    @Param("jti") jti: string,
  ): Promise<TokenStatusResponse> {
    try {
      // Check if token is revoked
      const isRevoked = await this.revocationStore.isTokenRevoked(jti);

      // Get revocation info if revoked
      let info = null;
      if (isRevoked) {
        info = await this.revocationStore.getRevocationInfo(jti);
      }

      return {
        isRevoked,
        reason: info?.reason,
        revokedAt: info?.revokedAt,
      };
    } catch (error) {
      this.logger.error(`Error checking token status: ${error.message}`);
      throw new HttpException(
        `Failed to check token status: ${error.message}`,
        HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }

  /**
   * Get revocation statistics (Admin only)
   * الحصول على إحصائيات الإلغاء (للمسؤولين فقط)
   */
  @Get("stats")
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth()
  @ApiOperation({
    summary: "Get revocation statistics (Admin only)",
    description: "Get statistics about revoked tokens",
  })
  @ApiResponse({
    status: HttpStatus.OK,
    description: "Revocation statistics",
  })
  @ApiResponse({
    status: HttpStatus.FORBIDDEN,
    description: "Forbidden - admin privileges required",
  })
  async getRevocationStats(@Request() req: any): Promise<RevocationStats> {
    const user: AuthenticatedUser = req.user;

    // Check admin authorization
    const isAdmin =
      user.roles.includes("admin") || user.roles.includes("superadmin");

    if (!isAdmin) {
      throw new ForbiddenException("Admin privileges required");
    }

    try {
      return await this.revocationStore.getStats();
    } catch (error) {
      this.logger.error(`Error getting revocation stats: ${error.message}`);
      throw new HttpException(
        `Failed to get revocation stats: ${error.message}`,
        HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }

  /**
   * Health check
   * فحص الصحة
   */
  @Get("health")
  @ApiOperation({
    summary: "Health check",
    description: "Check if token revocation service is healthy",
  })
  @ApiResponse({
    status: HttpStatus.OK,
    description: "Service health status",
  })
  async healthCheck(): Promise<{
    status: string;
    service: string;
    redis: string;
  }> {
    try {
      const isHealthy = await this.revocationStore.healthCheck();

      return {
        status: isHealthy ? "healthy" : "unhealthy",
        service: "token_revocation",
        redis: isHealthy ? "connected" : "disconnected",
      };
    } catch (error) {
      this.logger.error(`Health check failed: ${error.message}`);
      return {
        status: "unhealthy",
        service: "token_revocation",
        redis: "error",
      };
    }
  }
}
