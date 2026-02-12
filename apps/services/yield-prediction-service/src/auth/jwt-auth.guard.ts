/**
 * JWT Authentication Guard
 */

import {
  Injectable,
  CanActivate,
  ExecutionContext,
  UnauthorizedException,
} from "@nestjs/common";
import * as jwt from "jsonwebtoken";

@Injectable()
export class JwtAuthGuard implements CanActivate {
  canActivate(context: ExecutionContext): boolean {
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

      const ALLOWED_ALGORITHMS: jwt.Algorithm[] = [
        "HS256",
        "HS384",
        "HS512",
        "RS256",
        "RS384",
        "RS512",
      ];

      const header = jwt.decode(token, { complete: true })?.header;
      if (!header || !header.alg) {
        throw new UnauthorizedException("Invalid token: missing algorithm");
      }

      if (header.alg.toLowerCase() === "none") {
        throw new UnauthorizedException(
          "Invalid token: none algorithm not allowed",
        );
      }

      if (!ALLOWED_ALGORITHMS.includes(header.alg as jwt.Algorithm)) {
        throw new UnauthorizedException("Invalid token: unsupported algorithm");
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
