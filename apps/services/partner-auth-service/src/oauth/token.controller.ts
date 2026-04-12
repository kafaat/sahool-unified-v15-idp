/**
 * POST /partner/v1/oauth/token
 *
 * OAuth 2.0 Token Endpoint (RFC 6749 § 3.2).
 * Accepts application/x-www-form-urlencoded. Client authenticates via:
 *   • HTTP Basic (Authorization: Basic base64(clientId:secret)) — preferred
 *   • Body params (client_id + client_secret) — fallback for legacy clients
 *
 * Supported grants:
 *   • authorization_code
 *   • refresh_token
 */

import {
  BadRequestException,
  Body,
  Controller,
  Headers,
  Post,
  HttpCode,
  Header,
} from "@nestjs/common";
import { ApiTags, ApiOperation } from "@nestjs/swagger";
import { OAuthService, TokenGrantResult } from "./oauth.service";

interface TokenRequestBody {
  grant_type?: string;
  code?: string;
  redirect_uri?: string;
  refresh_token?: string;
  scope?: string;
  code_verifier?: string;
  client_id?: string;
  client_secret?: string;
}

@ApiTags("OAuth")
@Controller("oauth/token")
export class TokenController {
  constructor(private readonly oauth: OAuthService) {}

  @Post()
  @HttpCode(200)
  @Header("Cache-Control", "no-store")
  @Header("Pragma", "no-cache")
  @ApiOperation({ summary: "OAuth 2.0 token endpoint (RFC 6749 § 3.2)" })
  async token(
    @Headers("authorization") authz: string | undefined,
    @Body() body: TokenRequestBody,
  ): Promise<TokenGrantResult> {
    const creds = extractClientCreds(authz, body);
    if (!creds) {
      throw new BadRequestException({
        error: "invalid_client",
        error_description:
          "Missing client authentication (expected HTTP Basic or client_id+client_secret body)",
      });
    }

    const client = await this.oauth.authenticateClient(
      creds.clientId,
      creds.clientSecret,
    );

    switch (body.grant_type) {
      case "authorization_code": {
        if (!body.code || !body.redirect_uri) {
          throw new BadRequestException({
            error: "invalid_request",
            error_description: "code and redirect_uri are required",
          });
        }
        return await this.oauth.exchangeAuthorizationCode({
          client,
          code: body.code,
          redirectUri: body.redirect_uri,
          codeVerifier: body.code_verifier,
        });
      }
      case "refresh_token": {
        if (!body.refresh_token) {
          throw new BadRequestException({
            error: "invalid_request",
            error_description: "refresh_token is required",
          });
        }
        return await this.oauth.exchangeRefreshToken({
          client,
          refreshToken: body.refresh_token,
          requestedScope: body.scope,
        });
      }
      default:
        throw new BadRequestException({
          error: "unsupported_grant_type",
          error_description: `grant_type='${body.grant_type}' is not supported`,
        });
    }
  }
}

/**
 * Extracts client_id + client_secret from either HTTP Basic or body params
 * (RFC 6749 § 2.3.1). HTTP Basic is preferred; body is a fallback.
 */
function extractClientCreds(
  authz: string | undefined,
  body: TokenRequestBody,
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
