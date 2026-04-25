/**
 * JWT Authentication Guard
 * حارس المصادقة باستخدام JWT
 */

import {
  Injectable,
  CanActivate,
  ExecutionContext,
  UnauthorizedException,
} from "@nestjs/common";
import { Reflector } from "@nestjs/core";
import { IS_PUBLIC_KEY } from "./public.decorator";
import * as jwt from "jsonwebtoken";

@Injectable()
export class JwtAuthGuard implements CanActivate {
  constructor(private reflector: Reflector) {}

  canActivate(context: ExecutionContext): boolean {
    // Skip authentication for @Public() routes
    const isPublic = this.reflector.getAllAndOverride<boolean>(IS_PUBLIC_KEY, [
      context.getHandler(),
      context.getClass(),
    ]);
    if (isPublic) return true;

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

      // SECURITY FIX: Hardcoded whitelist of allowed algorithms to prevent algorithm confusion attacks
      // Never trust algorithm from environment variables or token header
      const ALLOWED_ALGORITHMS: jwt.Algorithm[] = ["HS256"]; // Platform policy: HS256 only.
      // Including both HS* and RS* enables a classic algorithm-confusion
      // attack where a token signed with an RSA public key as HMAC secret
      // would verify under HS256. See shared/auth/jwt_handler.py and
      // shared/auth/config.ts for the canonical platform policy.

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
        tenantId: decoded.tenant_id,
      };

      return true;
    } catch (error) {
      if (error instanceof jwt.TokenExpiredError) {
        throw new UnauthorizedException("Token expired");
      }
      if (error instanceof jwt.JsonWebTokenError) {
        throw new UnauthorizedException("Invalid token");
      }
      throw new UnauthorizedException("Authentication failed");
    }
  }
}

/**
 * Optional Auth Guard - allows unauthenticated requests but attaches user if present
 * حارس المصادقة الاختياري
 */
@Injectable()
export class OptionalJwtAuthGuard implements CanActivate {
  canActivate(context: ExecutionContext): boolean {
    const request = context.switchToHttp().getRequest();
    const authHeader = request.headers.authorization;

    if (!authHeader) {
      return true; // Allow unauthenticated
    }

    const [type, token] = authHeader.split(" ");

    if (type !== "Bearer" || !token) {
      return true; // Allow but don't authenticate
    }

    try {
      const secret = process.env.JWT_SECRET_KEY || process.env.JWT_SECRET;
      if (!secret) {
        return true;
      }

      // SECURITY FIX: Hardcoded whitelist of allowed algorithms to prevent algorithm confusion attacks
      // Never trust algorithm from environment variables or token header
      const ALLOWED_ALGORITHMS: jwt.Algorithm[] = ["HS256"]; // Platform policy: HS256 only.
      // Including both HS* and RS* enables a classic algorithm-confusion
      // attack where a token signed with an RSA public key as HMAC secret
      // would verify under HS256. See shared/auth/jwt_handler.py and
      // shared/auth/config.ts for the canonical platform policy.

      // Decode header without verification to check algorithm
      const header = jwt.decode(token, { complete: true })?.header;
      if (!header || !header.alg) {
        return true; // Allow unauthenticated for optional guard
      }

      // Reject 'none' algorithm explicitly
      if (header.alg.toLowerCase() === "none") {
        return true; // Allow unauthenticated for optional guard
      }

      // Verify algorithm is in whitelist
      if (!ALLOWED_ALGORITHMS.includes(header.alg as jwt.Algorithm)) {
        return true; // Allow unauthenticated for optional guard
      }

      const decoded = jwt.verify(token, secret, {
        algorithms: ALLOWED_ALGORITHMS,
      }) as jwt.JwtPayload;

      request.user = {
        id: decoded.sub || decoded.user_id,
        email: decoded.email,
        roles: decoded.roles || [],
        tenantId: decoded.tenant_id,
      };
    } catch {
      // Ignore errors for optional auth
    }

    return true;
  }
}
