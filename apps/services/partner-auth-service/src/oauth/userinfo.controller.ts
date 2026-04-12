/**
 * GET /partner/v1/oauth/userinfo — OIDC UserInfo Endpoint.
 *
 * Requires `Authorization: Bearer <access_token>` with `openid` scope.
 * Returns claims about the authenticated user (subject of the token).
 *
 * Per OIDC Core 1.0 § 5.3.2, optional claims (email, name) are only
 * returned when the corresponding scope (`email`, `profile`) was granted.
 *
 * In this scaffold we return claims from the token itself. A future
 * branch will call user-service to fetch fresh profile data (with a
 * cache) so claim values stay up to date as the user updates their
 * profile.
 */

import { Controller, Get, Req, UseGuards } from "@nestjs/common";
import { ApiBearerAuth, ApiOperation, ApiTags } from "@nestjs/swagger";
import type { Request } from "express";
import { BearerAuthGuard } from "./bearer.guard";

interface UserInfoResponse {
  sub: string;
  tenant_id?: string;
  scope?: string;
  // Conditionally present per granted scope:
  email?: string;
  email_verified?: boolean;
  name?: string;
  name_ar?: string;
  locale?: string;
}

@ApiTags("OAuth")
@ApiBearerAuth()
@Controller("oauth/userinfo")
export class UserinfoController {
  @Get()
  @UseGuards(BearerAuthGuard)
  @ApiOperation({ summary: "OIDC UserInfo endpoint (OIDC Core 1.0 § 5.3)" })
  userinfo(@Req() req: Request): UserInfoResponse {
    const claims = req.accessTokenClaims;
    if (!claims) {
      // Guard should have thrown; defensive fallback.
      throw new Error("BearerAuthGuard did not attach accessTokenClaims");
    }

    const scopes = new Set(claims.scope);
    const out: UserInfoResponse = {
      sub: claims.sub,
      tenant_id: claims.tenantId,
      scope: claims.scope.join(" "),
    };

    // TODO(wave1-branch-3): fetch fresh profile from user-service.
    // For this scaffold, if profile/email scopes were granted, we'd
    // populate them from the cached user-service row. Here we return
    // only the sub + tenant_id since that's all we can prove from the
    // access token alone.
    if (scopes.has("email")) {
      // email claim only present when scope granted
      out.email = undefined;
      out.email_verified = undefined;
    }
    if (scopes.has("profile")) {
      out.name = undefined;
      out.name_ar = undefined;
      out.locale = undefined;
    }

    return out;
  }
}
