/**
 * JWT Strategy for User Service
 * استراتيجية JWT لخدمة المستخدمين
 *
 * Security features:
 * - Token revocation check via Redis
 * - User-level revocation check
 * - Tenant-level revocation check
 * - User status validation
 */

import { Injectable, UnauthorizedException, Logger } from "@nestjs/common";
import { PassportStrategy } from "@nestjs/passport";
import { ExtractJwt, Strategy } from "passport-jwt";
import { PrismaService } from "../prisma/prisma.service";
import { RedisTokenRevocationStore } from "../utils/token-revocation";
import { JWTConfig } from "../utils/jwt.config";

export interface JwtPayload {
  sub: string;
  email: string;
  roles: string[];
  tid?: string;
  jti?: string;
  type?: "access" | "refresh";
  iat?: number;
  exp?: number;
}

@Injectable()
export class JwtStrategy extends PassportStrategy(Strategy) {
  private readonly logger = new Logger(JwtStrategy.name);

  constructor(
    private readonly prisma: PrismaService,
    private readonly revocationStore: RedisTokenRevocationStore,
  ) {
    super({
      jwtFromRequest: ExtractJwt.fromAuthHeaderAsBearerToken(),
      ignoreExpiration: false,
      secretOrKey: JWTConfig.SECRET,
      issuer: JWTConfig.ISSUER,
      audience: JWTConfig.AUDIENCE,
      algorithms: [JWTConfig.ALGORITHM],
    });
  }

  async validate(payload: JwtPayload) {
    // Reject refresh tokens used as access tokens
    if (payload.type && payload.type !== "access") {
      this.logger.warn(
        `Non-access token used for authentication: type=${payload.type}, jti=${payload.jti?.substring(0, 8)}...`,
      );
      throw new UnauthorizedException("Invalid token type");
    }

    // Check if token is revoked (fail-closed: deny on Redis errors)
    try {
      const revocationResult = await this.revocationStore.isRevoked({
        jti: payload.jti,
        userId: payload.sub,
        tenantId: payload.tid,
        issuedAt: payload.iat,
      });

      if (revocationResult.isRevoked) {
        this.logger.warn(
          `Revoked token used: jti=${payload.jti?.substring(0, 8)}..., reason=${revocationResult.reason}`,
        );
        throw new UnauthorizedException("Token has been revoked");
      }
    } catch (error) {
      if (error instanceof UnauthorizedException) {
        throw error;
      }
      // Fail-closed: If Redis is unavailable, deny access for security
      const message = error instanceof Error ? error.message : String(error);
      this.logger.error(
        `Token revocation check failed (fail-closed): ${message}`,
      );
      throw new UnauthorizedException(
        "Authentication service temporarily unavailable",
      );
    }

    // Validate user exists in database
    const user = await this.prisma.user.findUnique({
      where: { id: payload.sub },
    });

    if (!user) {
      throw new UnauthorizedException("User not found");
    }

    // Cross-check tenant binding: if the token carries a tenant id, it MUST
    // match the persisted user row. Protects against a user that was moved
    // between tenants: the pre-move tokens must not be usable against the
    // new tenant's data.
    if (payload.tid && user.tenantId && payload.tid !== user.tenantId) {
      this.logger.warn(
        `Token tenant mismatch: jti=${payload.jti?.substring(0, 8)}..., token_tid=${payload.tid}, user_tid=${user.tenantId}`,
      );
      throw new UnauthorizedException("Token tenant mismatch");
    }

    // Check if user is active
    if (user.status !== "ACTIVE") {
      throw new UnauthorizedException("User account is not active");
    }

    // Return user object (will be attached to request.user)
    return {
      id: user.id,
      email: user.email,
      roles: [user.role],
      tenantId: user.tenantId,
      tokenId: payload.jti,
    };
  }
}
