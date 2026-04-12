/**
 * Admin role guard — only lets SAHOOL staff reach /api/v1/admin/partner-auth/*.
 *
 * Accepts the same `Authorization: Bearer <jwt>` that user-service issues,
 * verified against SAHOOL_SESSION_SECRET (HS256). Rejects the request with
 * 401 unless the JWT carries `role: "ADMIN"` (or `roles: [..., "ADMIN", ...]`).
 *
 * In a follow-up branch this should move to RS256 + JWKS so partner-auth
 * doesn't need the shared secret, and should integrate with a proper
 * RBAC policy engine.
 */

import {
  CanActivate,
  ExecutionContext,
  ForbiddenException,
  Injectable,
  UnauthorizedException,
} from "@nestjs/common";
import type { Request } from "express";
import { jwtVerify } from "jose";

export interface AdminPrincipal {
  id: string;
  email?: string;
  roles: string[];
  tenantId?: string;
}

declare module "express" {
  interface Request {
    adminPrincipal?: AdminPrincipal;
  }
}

@Injectable()
export class AdminGuard implements CanActivate {
  private readonly secret: Uint8Array;

  constructor() {
    const raw =
      process.env.SAHOOL_SESSION_SECRET ??
      "dev-session-secret-CHANGE-ME-32-chars-minimum";
    if (process.env.NODE_ENV === "production" && raw.startsWith("dev-")) {
      throw new Error(
        "SAHOOL_SESSION_SECRET must be set to a production secret",
      );
    }
    this.secret = new TextEncoder().encode(raw);
  }

  async canActivate(ctx: ExecutionContext): Promise<boolean> {
    const req = ctx.switchToHttp().getRequest<Request>();
    const header = req.headers.authorization;
    if (!header?.startsWith("Bearer ")) {
      throw new UnauthorizedException({
        error: "unauthorized",
        error_description: "Missing Bearer token",
      });
    }
    const token = header.slice(7).trim();

    let payload: Record<string, unknown>;
    try {
      const result = await jwtVerify(token, this.secret);
      payload = result.payload as Record<string, unknown>;
    } catch {
      throw new UnauthorizedException({
        error: "unauthorized",
        error_description: "Invalid admin token",
      });
    }

    const roles = extractRoles(payload);
    if (!roles.includes("ADMIN")) {
      throw new ForbiddenException({
        error: "forbidden",
        error_description: "ADMIN role required",
      });
    }

    req.adminPrincipal = {
      id: String(payload.sub ?? ""),
      email: typeof payload.email === "string" ? payload.email : undefined,
      roles,
      tenantId: typeof payload.tid === "string" ? payload.tid : undefined,
    };
    return true;
  }
}

function extractRoles(payload: Record<string, unknown>): string[] {
  if (Array.isArray(payload.roles)) {
    return payload.roles.filter((r): r is string => typeof r === "string");
  }
  if (typeof payload.role === "string") return [payload.role];
  return [];
}
