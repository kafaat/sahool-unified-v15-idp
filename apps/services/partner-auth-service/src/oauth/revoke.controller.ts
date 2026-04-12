/**
 * POST /partner/v1/oauth/revoke — RFC 7009 Token Revocation.
 *
 * Partners call this to revoke an access token (JWT jti) or a refresh
 * token (opaque). The server:
 *   • Authenticates the client (HTTP Basic or body)
 *   • Looks up the token and ensures it belongs to that client
 *   • Marks revoked (for refresh tokens this cascades the family)
 *   • Returns 200 with empty body — ALWAYS, even on unknown tokens
 *     (RFC 7009 § 2.2: do not distinguish valid-but-wrong-type from
 *      unknown, to avoid leaking information).
 */

import {
  BadRequestException,
  Body,
  Controller,
  Headers,
  HttpCode,
  Post,
} from "@nestjs/common";
import { ApiOperation, ApiTags } from "@nestjs/swagger";
import { OAuthService } from "./oauth.service";

interface RevokeBody {
  token?: string;
  token_type_hint?: "access_token" | "refresh_token";
  client_id?: string;
  client_secret?: string;
}

@ApiTags("OAuth")
@Controller("oauth/revoke")
export class RevokeController {
  constructor(private readonly oauth: OAuthService) {}

  @Post()
  @HttpCode(200)
  @ApiOperation({ summary: "RFC 7009 token revocation" })
  async revoke(
    @Headers("authorization") authz: string | undefined,
    @Body() body: RevokeBody,
  ): Promise<void> {
    const creds = extractClientCreds(authz, body);
    if (!creds) {
      throw new BadRequestException({
        error: "invalid_client",
        error_description:
          "Missing client authentication (HTTP Basic or client_id+client_secret body)",
      });
    }
    if (!body.token) {
      throw new BadRequestException({
        error: "invalid_request",
        error_description: "token parameter is required",
      });
    }

    const client = await this.oauth.authenticateClient(
      creds.clientId,
      creds.clientSecret,
    );

    await this.oauth.revokeToken({
      clientId: client.id,
      token: body.token,
      tokenTypeHint: body.token_type_hint,
    });
    // 200 with no body — RFC 7009 § 2.2
  }
}

function extractClientCreds(
  authz: string | undefined,
  body: RevokeBody,
): { clientId: string; clientSecret: string } | null {
  if (authz?.startsWith("Basic ")) {
    try {
      const decoded = Buffer.from(authz.slice(6).trim(), "base64").toString(
        "utf-8",
      );
      const sep = decoded.indexOf(":");
      if (sep <= 0) return null;
      return {
        clientId: decodeURIComponent(decoded.slice(0, sep)),
        clientSecret: decodeURIComponent(decoded.slice(sep + 1)),
      };
    } catch {
      return null;
    }
  }
  if (body.client_id && body.client_secret) {
    return { clientId: body.client_id, clientSecret: body.client_secret };
  }
  return null;
}
