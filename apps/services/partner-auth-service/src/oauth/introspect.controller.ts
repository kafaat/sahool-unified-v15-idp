/**
 * POST /partner/v1/oauth/introspect — RFC 7662 Token Introspection.
 *
 * Resource servers (downstream SAHOOL microservices) use this to validate
 * an opaque/JWT token without decoding/verifying it themselves. This is
 * the pattern FieldView uses for its /introspect endpoint.
 *
 * Returns `{active: true, scope, client_id, username, exp, iat, sub, aud,
 *          iss, jti, tenant_id}` for valid tokens, or `{active: false}`
 * for unknown / expired / revoked / wrong-client tokens — the RFC requires
 * the response body NOT to reveal whether the token existed.
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
import { OAuthService, IntrospectResponse } from "./oauth.service";

interface IntrospectBody {
  token?: string;
  token_type_hint?: "access_token" | "refresh_token";
  client_id?: string;
  client_secret?: string;
}

@ApiTags("OAuth")
@Controller("oauth/introspect")
export class IntrospectController {
  constructor(private readonly oauth: OAuthService) {}

  @Post()
  @HttpCode(200)
  @ApiOperation({ summary: "RFC 7662 token introspection" })
  async introspect(
    @Headers("authorization") authz: string | undefined,
    @Body() body: IntrospectBody,
  ): Promise<IntrospectResponse> {
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

    return await this.oauth.introspectToken({
      clientId: client.id,
      token: body.token,
      tokenTypeHint: body.token_type_hint,
    });
  }
}

function extractClientCreds(
  authz: string | undefined,
  body: IntrospectBody,
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
