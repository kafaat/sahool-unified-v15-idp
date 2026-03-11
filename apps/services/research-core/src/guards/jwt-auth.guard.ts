/**
 * JWT Authentication Guard
 * حارس المصادقة باستخدام JWT
 *
 * Local implementation to avoid Docker build dependency on @sahool/nestjs-auth.
 * Validates JWT tokens and attaches user info to the request.
 * Respects @Public() decorator to skip auth for health endpoints.
 */

import {
  Injectable,
  CanActivate,
  ExecutionContext,
  UnauthorizedException,
  SetMetadata,
  Logger,
} from "@nestjs/common";
import { Reflector } from "@nestjs/core";
import * as jwt from "jsonwebtoken";

export const IS_PUBLIC_KEY = "isPublic";
export const Public = () => SetMetadata(IS_PUBLIC_KEY, true);

@Injectable()
export class JwtAuthGuard implements CanActivate {
  private readonly logger = new Logger(JwtAuthGuard.name);

  constructor(private readonly reflector: Reflector) {}

  canActivate(context: ExecutionContext): boolean {
    // Check if endpoint is marked as public
    const isPublic = this.reflector.getAllAndOverride<boolean>(IS_PUBLIC_KEY, [
      context.getHandler(),
      context.getClass(),
    ]);

    if (isPublic) {
      return true;
    }

    const request = context.switchToHttp().getRequest();
    const authHeader = request.headers.authorization;

    if (!authHeader) {
      throw new UnauthorizedException("Missing authorization header");
    }

    const [type, token] = authHeader.split(" ");

    if (type !== "Bearer" || !token) {
      throw new UnauthorizedException("Invalid authorization format");
    }

    try {
      const secret = process.env.JWT_SECRET_KEY || process.env.JWT_SECRET;
      if (!secret) {
        throw new UnauthorizedException("JWT secret not configured");
      }

      // SECURITY: Hardcoded whitelist of allowed algorithms to prevent algorithm confusion attacks
      const ALLOWED_ALGORITHMS: jwt.Algorithm[] = [
        "HS256",
        "HS384",
        "HS512",
        "RS256",
        "RS384",
        "RS512",
      ];

      // Decode header without verification to check algorithm
      const header = jwt.decode(token, { complete: true })?.header;
      if (!header || !header.alg) {
        throw new UnauthorizedException("Invalid token: missing algorithm");
      }

      // Reject 'none' algorithm explicitly
      if (header.alg.toLowerCase() === "none") {
        throw new UnauthorizedException(
          "Invalid token: none algorithm not allowed",
        );
      }

      // Verify algorithm is in whitelist
      if (!ALLOWED_ALGORITHMS.includes(header.alg as jwt.Algorithm)) {
        throw new UnauthorizedException("Invalid token: unsupported algorithm");
      }

      const decoded = jwt.verify(token, secret, {
        algorithms: ALLOWED_ALGORITHMS,
      }) as jwt.JwtPayload;

      // Attach user info to request
      request.user = {
        id: decoded.sub || decoded.user_id,
        email: decoded.email,
        roles: decoded.roles || [],
        tenantId: decoded.tenant_id || decoded.tid,
      };

      return true;
    } catch (error) {
      if (error instanceof UnauthorizedException) {
        throw error;
      }
      if (error instanceof jwt.TokenExpiredError) {
        throw new UnauthorizedException("Token expired");
      }
      if (error instanceof jwt.JsonWebTokenError) {
        throw new UnauthorizedException("Invalid token");
      }
      this.logger.error(
        `Authentication failed: ${error instanceof Error ? error.message : String(error)}`,
      );
      throw new UnauthorizedException("Authentication failed");
    }
  }
}
