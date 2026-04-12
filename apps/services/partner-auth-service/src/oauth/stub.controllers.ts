/**
 * Deliberate 501 stubs for endpoints planned in a follow-up PR.
 * Each replies with a machine-readable JSON body so partners know the
 * endpoint exists (in discovery) but is not yet live.
 *
 * Planned next branch: claude/wave1-partner-auth-consent-screen
 *   • /authorize — interactive consent screen (HTML + HTMX)
 *   • /revoke — RFC 7009 token revocation
 *   • /introspect — RFC 7662 token introspection
 *   • /userinfo — OIDC UserInfo endpoint
 */

import {
  Controller,
  Get,
  HttpCode,
  Post,
  HttpStatus,
} from "@nestjs/common";
import { ApiTags, ApiOperation } from "@nestjs/swagger";

const NOT_IMPLEMENTED_BODY = (endpoint: string, plannedBranch: string) => ({
  error: "not_implemented",
  error_description: `${endpoint} is scaffolded but not yet live. Planned: ${plannedBranch}`,
  documentation_url: "https://dev.sahool.app/partner/changelog",
});

@ApiTags("OAuth")
@Controller("oauth/authorize")
export class AuthorizeStubController {
  @Get()
  @HttpCode(HttpStatus.NOT_IMPLEMENTED)
  @ApiOperation({ summary: "[501] Authorization endpoint (consent screen) — planned" })
  get() {
    return NOT_IMPLEMENTED_BODY(
      "/oauth/authorize",
      "claude/wave1-partner-auth-consent-screen",
    );
  }
}

@ApiTags("OAuth")
@Controller("oauth/revoke")
export class RevokeStubController {
  @Post()
  @HttpCode(HttpStatus.NOT_IMPLEMENTED)
  @ApiOperation({ summary: "[501] Token revocation (RFC 7009) — planned" })
  post() {
    return NOT_IMPLEMENTED_BODY(
      "/oauth/revoke",
      "claude/wave1-partner-auth-consent-screen",
    );
  }
}

@ApiTags("OAuth")
@Controller("oauth/introspect")
export class IntrospectStubController {
  @Post()
  @HttpCode(HttpStatus.NOT_IMPLEMENTED)
  @ApiOperation({ summary: "[501] Token introspection (RFC 7662) — planned" })
  post() {
    return NOT_IMPLEMENTED_BODY(
      "/oauth/introspect",
      "claude/wave1-partner-auth-consent-screen",
    );
  }
}

@ApiTags("OAuth")
@Controller("oauth/userinfo")
export class UserinfoStubController {
  @Get()
  @HttpCode(HttpStatus.NOT_IMPLEMENTED)
  @ApiOperation({ summary: "[501] OIDC UserInfo endpoint — planned" })
  get() {
    return NOT_IMPLEMENTED_BODY(
      "/oauth/userinfo",
      "claude/wave1-partner-auth-consent-screen",
    );
  }
}
