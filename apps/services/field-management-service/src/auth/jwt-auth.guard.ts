/**
 * JWT Authentication Guard
 * حارس مصادقة JWT
 *
 * Validates JWT Bearer tokens on all routes except those marked with @Public().
 * Extracts user information (id, tenantId, roles) from the token payload
 * and attaches it to request.user.
 */

import {
  Injectable,
  CanActivate,
  ExecutionContext,
  UnauthorizedException,
  Logger,
} from "@nestjs/common";
import { Reflector } from "@nestjs/core";
import { IS_PUBLIC_KEY } from "./public.decorator";
import * as crypto from "crypto";

@Injectable()
export class JwtAuthGuard implements CanActivate {
  private readonly logger = new Logger(JwtAuthGuard.name);

  constructor(private reflector: Reflector) {}

  canActivate(context: ExecutionContext): boolean {
    // Skip authentication for @Public() routes
    const isPublic = this.reflector.getAllAndOverride<boolean>(IS_PUBLIC_KEY, [
      context.getHandler(),
      context.getClass(),
    ]);
    if (isPublic) return true;

    const request = context.switchToHttp().getRequest();
    const authHeader = request.headers["authorization"];

    if (!authHeader || !authHeader.startsWith("Bearer ")) {
      throw new UnauthorizedException(
        "Missing or invalid Authorization header - رأس المصادقة مفقود أو غير صالح",
      );
    }

    const token = authHeader.substring(7);

    try {
      const payload = this.decodeAndVerifyToken(token);

      // Attach user to request
      request.user = {
        id: payload.sub,
        tenantId: payload.tid,
        roles: payload.roles || [],
        email: payload.email,
      };

      return true;
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Token validation failed";
      this.logger.warn(
        `JWT validation failed [${request.method} ${request.url}]: ${message}`,
      );
      throw new UnauthorizedException(
        "Invalid or expired token - رمز غير صالح أو منتهي الصلاحية",
      );
    }
  }

  /**
   * Decode and verify JWT token using HS256.
   * Uses the JWT_SECRET_KEY environment variable.
   */
  private decodeAndVerifyToken(token: string): any {
    const parts = token.split(".");
    if (parts.length !== 3) {
      throw new Error("Invalid JWT format");
    }

    const [headerB64, payloadB64, signatureB64] = parts;

    // Verify signature
    const secret = process.env.JWT_SECRET_KEY;
    if (!secret) {
      throw new Error("JWT_SECRET_KEY not configured");
    }

    const algorithm = process.env.JWT_ALGORITHM || "HS256";
    if (algorithm !== "HS256") {
      throw new Error(`Unsupported JWT algorithm: ${algorithm}`);
    }

    const expectedSignature = crypto
      .createHmac("sha256", secret)
      .update(`${headerB64}.${payloadB64}`)
      .digest("base64url");

    if (
      !crypto.timingSafeEqual(
        Buffer.from(signatureB64),
        Buffer.from(expectedSignature),
      )
    ) {
      throw new Error("Invalid JWT signature");
    }

    // Decode payload
    const payload = JSON.parse(
      Buffer.from(payloadB64, "base64url").toString("utf8"),
    );

    // Check expiration
    if (payload.exp && payload.exp < Math.floor(Date.now() / 1000)) {
      throw new Error("Token expired");
    }

    return payload;
  }
}
