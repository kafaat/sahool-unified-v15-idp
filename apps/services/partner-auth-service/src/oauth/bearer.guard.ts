/**
 * Bearer access-token guard — enforces `Authorization: Bearer <at>`.
 *
 * Verifies the JWT against JWKS, checks revocation in access_tokens,
 * attaches the decoded AccessTokenClaims to `req.accessTokenClaims`.
 * On failure, returns a WWW-Authenticate 401 per RFC 6750 § 3.
 */

import {
  CanActivate,
  ExecutionContext,
  Injectable,
  UnauthorizedException,
} from "@nestjs/common";
import type { Request } from "express";
import { OAuthService, AccessTokenClaims } from "./oauth.service";

declare module "express" {
  interface Request {
    accessTokenClaims?: AccessTokenClaims;
  }
}

@Injectable()
export class BearerAuthGuard implements CanActivate {
  constructor(private readonly oauth: OAuthService) {}

  async canActivate(ctx: ExecutionContext): Promise<boolean> {
    const req = ctx.switchToHttp().getRequest<Request>();
    const header = req.headers.authorization;
    if (!header?.startsWith("Bearer ")) {
      throw new UnauthorizedException({
        error: "invalid_token",
        error_description:
          "Authorization: Bearer <token> header is required",
      });
    }
    const token = header.slice(7).trim();
    req.accessTokenClaims = await this.oauth.verifyAccessToken(token);
    return true;
  }
}
