/**
 * JWT Strategy for NestJS Passport Authentication
 * Implements passport-jwt strategy for SAHOOL platform
 *
 * Enhanced with:
 * - Database user validation
 * - Redis caching for performance
 * - User status checks (active, verified, deleted, suspended)
 * - Failed authentication logging
 */

import { Injectable, UnauthorizedException, Logger } from "@nestjs/common";
import { PassportStrategy } from "@nestjs/passport";
import { ExtractJwt, Strategy } from "passport-jwt";
import { JWTConfig, AuthErrors } from "../config/jwt.config";
import { UserValidationService } from "../services/user-validation.service";

/**
 * JWT Token Payload Interface
 */
export interface JwtPayload {
  sub: string; // user_id
  roles: string[];
  exp: number;
  iat: number;
  tid?: string; // tenant_id
  jti?: string; // token_id
  type?: string; // access or refresh
  permissions?: string[];
}

/**
 * User object returned after authentication
 */
export interface AuthenticatedUser {
  id: string;
  roles: string[];
  tenantId?: string;
  permissions: string[];
  tokenId?: string;
}

/**
 * JWT Strategy for validating JWT tokens
 *
 * @example
 * ```typescript
 * // In your auth.module.ts
 * import { JwtStrategy } from '@shared/auth/jwt.strategy';
 * import { UserValidationService } from '@shared/auth/user-validation.service';
 *
 * @Module({
 *   imports: [
 *     PassportModule,
 *     JwtModule.register({
 *       secret: JWTConfig.SECRET,
 *       signOptions: JWTConfig.getJwtOptions().signOptions,
 *     }),
 *   ],
 *   providers: [JwtStrategy, UserValidationService],
 *   exports: [JwtStrategy],
 * })
 * export class AuthModule {}
 * ```
 */
@Injectable()
export class JwtStrategy extends PassportStrategy(Strategy) {
  private readonly logger = new Logger(JwtStrategy.name);

  constructor(private readonly userValidationService?: UserValidationService) {
    super({
      jwtFromRequest: ExtractJwt.fromAuthHeaderAsBearerToken(),
      ignoreExpiration: false,
      secretOrKey: JWTConfig.getVerificationKey(),
      issuer: JWTConfig.ISSUER,
      audience: JWTConfig.AUDIENCE,
      algorithms: [JWTConfig.ALGORITHM],
    });

    if (!userValidationService) {
      this.logger.warn(
        "UserValidationService not provided - database validation disabled",
      );
    }
  }

  /**
   * Validate JWT payload and return user object
   *
   * This method is called automatically by Passport after token verification.
   * It performs additional validation:
   * 1. Checks if user exists in database (with caching)
   * 2. Validates user status (active, verified, not deleted/suspended)
   * 3. Logs failed authentication attempts
   *
   * @param payload - Decoded JWT payload
   * @returns Authenticated user object
   * @throws UnauthorizedException if validation fails
   */
  async validate(payload: JwtPayload): Promise<AuthenticatedUser> {
    // Ensure required fields exist
    if (!payload.sub) {
      this.logger.warn("JWT validation failed: Missing subject (user ID)");
      throw new UnauthorizedException(AuthErrors.INVALID_TOKEN.en);
    }

    const userId = payload.sub;

    try {
      // Validate user with database lookup and caching
      if (this.userValidationService) {
        const userData = await this.userValidationService.validateUser(userId);

        this.logger.debug(
          `JWT validated successfully for user ${userId} (${userData.email})`,
        );

        // Return user object with database data
        return {
          id: userId,
          roles: userData.roles || payload.roles || [],
          tenantId: userData.tenantId || payload.tid,
          permissions: payload.permissions || [],
          tokenId: payload.jti,
        };
      }

      // No validation service - return user from token only
      this.logger.debug(
        `JWT validated successfully for user ${userId} (token only)`,
      );

      return {
        id: userId,
        roles: payload.roles || [],
        tenantId: payload.tid,
        permissions: payload.permissions || [],
        tokenId: payload.jti,
      };
    } catch (error) {
      // Log the error and re-throw
      if (error instanceof UnauthorizedException) {
        this.logger.warn(
          `JWT validation failed for user ${userId}: ${error.message}`,
        );
        throw error;
      }

      this.logger.error(
        `JWT validation error for user ${userId}: ${error.message}`,
        error.stack,
      );
      throw new UnauthorizedException(AuthErrors.INVALID_TOKEN.en);
    }
  }
}

/**
 * Extended JWT Strategy with user database lookup
 *
 * Use this if you want to validate against database on every request
 *
 * @example
 * ```typescript
 * @Injectable()
 * export class JwtStrategyWithUserLookup extends JwtStrategy {
 *   constructor(private readonly userService: UserService) {
 *     super();
 *   }
 *
 *   async validate(payload: JwtPayload): Promise<AuthenticatedUser> {
 *     const baseUser = await super.validate(payload);
 *
 *     // Fetch user from database
 *     const user = await this.userService.findById(baseUser.id);
 *
 *     if (!user) {
 *       throw new UnauthorizedException('User not found');
 *     }
 *
 *     if (!user.isActive) {
 *       throw new UnauthorizedException(AuthErrors.ACCOUNT_DISABLED.en);
 *     }
 *
 *     return {
 *       ...baseUser,
 *       email: user.email,
 *       farmIds: user.farmIds,
 *     };
 *   }
 * }
 * ```
 */
