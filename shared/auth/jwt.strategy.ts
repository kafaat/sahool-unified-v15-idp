/**
 * JWT Strategy for NestJS Passport Authentication
 * Implements passport-jwt strategy for SAHOOL platform
 */

import { Injectable, UnauthorizedException } from '@nestjs/common';
import { PassportStrategy } from '@nestjs/passport';
import { ExtractJwt, Strategy } from 'passport-jwt';
import { JWTConfig, AuthErrors } from './config';

/**
 * JWT Token Payload Interface
 */
export interface JwtPayload {
  sub: string;           // user_id
  roles: string[];
  exp: number;
  iat: number;
  tid?: string;          // tenant_id
  jti?: string;          // token_id
  type?: string;         // access or refresh
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
 *
 * @Module({
 *   imports: [
 *     PassportModule,
 *     JwtModule.register({
 *       secret: JWTConfig.SECRET,
 *       signOptions: JWTConfig.getJwtOptions().signOptions,
 *     }),
 *   ],
 *   providers: [JwtStrategy],
 *   exports: [JwtStrategy],
 * })
 * export class AuthModule {}
 * ```
 */
@Injectable()
export class JwtStrategy extends PassportStrategy(Strategy) {
  constructor() {
    super({
      jwtFromRequest: ExtractJwt.fromAuthHeaderAsBearerToken(),
      ignoreExpiration: false,
      secretOrKey: JWTConfig.getVerificationKey(),
      issuer: JWTConfig.ISSUER,
      audience: JWTConfig.AUDIENCE,
      algorithms: [JWTConfig.ALGORITHM],
    });
  }

  /**
   * Validate JWT payload and return user object
   *
   * This method is called automatically by Passport after token verification.
   * Add additional validation logic here (e.g., check if user exists in database).
   *
   * @param payload - Decoded JWT payload
   * @returns Authenticated user object
   * @throws UnauthorizedException if validation fails
   */
  async validate(payload: JwtPayload): Promise<AuthenticatedUser> {
    // Ensure required fields exist
    if (!payload.sub) {
      throw new UnauthorizedException(AuthErrors.INVALID_TOKEN.en);
    }

    // Optional: Check if user exists in database
    // const user = await this.userService.findById(payload.sub);
    // if (!user || !user.isActive) {
    //   throw new UnauthorizedException(AuthErrors.ACCOUNT_DISABLED.en);
    // }

    // Optional: Check token revocation
    // if (JWTConfig.TOKEN_REVOCATION_ENABLED && payload.jti) {
    //   const isRevoked = await this.tokenRevocationService.isRevoked(payload.jti);
    //   if (isRevoked) {
    //     throw new UnauthorizedException(AuthErrors.TOKEN_REVOKED.en);
    //   }
    // }

    // Return user object
    return {
      id: payload.sub,
      roles: payload.roles || [],
      tenantId: payload.tid,
      permissions: payload.permissions || [],
      tokenId: payload.jti,
    };
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
