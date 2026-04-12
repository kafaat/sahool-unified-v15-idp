/**
 * SAHOOL session guard — resolves an authenticated user for /authorize.
 *
 * Accepts either:
 *   • `X-Sahool-Session` header with a session JWT (signed by user-service)
 *   • `sahool_session` cookie with the same JWT
 *
 * On failure, sets `login_redirect` on the request so the controller can
 * 302 to the SAHOOL login page with a `?return_to=` parameter.
 *
 * The JWT verification uses `SAHOOL_SESSION_SECRET` (HS256, shared with
 * user-service). In a future branch, this should move to RS256 + JWKS so
 * partner-auth never holds the signing secret.
 */

import {
  CanActivate,
  ExecutionContext,
  Injectable,
  Logger,
} from "@nestjs/common";
import type { Request } from "express";
import { jwtVerify } from "jose";

export interface RequestUser {
  id: string;
  tenantId: string;
  email?: string;
  name?: string;
  nameAr?: string;
  locale?: "ar" | "en";
}

declare module "express" {
  interface Request {
    sahoolUser?: RequestUser;
    loginRedirect?: string;
  }
}

@Injectable()
export class SahoolSessionGuard implements CanActivate {
  private readonly logger = new Logger(SahoolSessionGuard.name);
  private readonly secret: Uint8Array;
  private readonly loginUrl: string;

  constructor() {
    const raw =
      process.env.SAHOOL_SESSION_SECRET ??
      "dev-session-secret-CHANGE-ME-32-chars-minimum";
    if (process.env.NODE_ENV === "production" && raw.startsWith("dev-")) {
      throw new Error("SAHOOL_SESSION_SECRET must be set in production");
    }
    this.secret = new TextEncoder().encode(raw);
    this.loginUrl =
      process.env.SAHOOL_LOGIN_URL ?? "https://app.sahool.com/login";
  }

  async canActivate(ctx: ExecutionContext): Promise<boolean> {
    const req = ctx.switchToHttp().getRequest<Request>();
    const token = this.extractToken(req);

    if (!token) {
      this.setLoginRedirect(req);
      return false;
    }

    try {
      const { payload } = await jwtVerify(token, this.secret);
      const sub = typeof payload.sub === "string" ? payload.sub : null;
      const tenantId =
        typeof payload.tid === "string" ? payload.tid : undefined;
      if (!sub || !tenantId) {
        this.setLoginRedirect(req);
        return false;
      }
      req.sahoolUser = {
        id: sub,
        tenantId,
        email: typeof payload.email === "string" ? payload.email : undefined,
        name: typeof payload.name === "string" ? payload.name : undefined,
        nameAr:
          typeof payload.name_ar === "string" ? payload.name_ar : undefined,
        locale:
          payload.locale === "ar" || payload.locale === "en"
            ? payload.locale
            : undefined,
      };
      return true;
    } catch (err) {
      this.logger.debug(
        `Session verify failed: ${err instanceof Error ? err.message : err}`,
      );
      this.setLoginRedirect(req);
      return false;
    }
  }

  private extractToken(req: Request): string | null {
    const header = req.headers["x-sahool-session"];
    if (typeof header === "string" && header.length) return header;
    const cookie = this.readCookie(req, "sahool_session");
    return cookie;
  }

  private readCookie(req: Request, name: string): string | null {
    const raw = req.headers.cookie;
    if (!raw) return null;
    const parts = raw.split(/;\s*/);
    for (const p of parts) {
      const eq = p.indexOf("=");
      if (eq === -1) continue;
      if (p.slice(0, eq) === name) return decodeURIComponent(p.slice(eq + 1));
    }
    return null;
  }

  private setLoginRedirect(req: Request) {
    const returnTo = encodeURIComponent(
      `${req.protocol}://${req.get("host")}${req.originalUrl}`,
    );
    req.loginRedirect = `${this.loginUrl}?return_to=${returnTo}`;
  }
}
