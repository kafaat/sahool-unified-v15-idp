/**
 * GET /.well-known/openid-configuration
 * OIDC Discovery (OpenID Connect Discovery 1.0).
 *
 * Base URL for issued endpoints comes from the ISSUER env var so the
 * same image runs behind sandbox.sahool.app, api.sahool.com, etc.
 */

import { Controller, Get, Header } from "@nestjs/common";
import { PARTNER_OAUTH_SCOPES } from "@sahool/shared-types/contracts";

const ISSUER = process.env.PARTNER_AUTH_ISSUER ?? "https://api.sahool.com";

@Controller(".well-known/openid-configuration")
export class DiscoveryController {
  @Get()
  @Header("Cache-Control", "public, max-age=3600")
  @Header("Content-Type", "application/json")
  discovery() {
    return {
      issuer: ISSUER,
      authorization_endpoint: `${ISSUER}/partner/v1/oauth/authorize`,
      token_endpoint: `${ISSUER}/partner/v1/oauth/token`,
      userinfo_endpoint: `${ISSUER}/partner/v1/oauth/userinfo`,
      revocation_endpoint: `${ISSUER}/partner/v1/oauth/revoke`,
      introspection_endpoint: `${ISSUER}/partner/v1/oauth/introspect`,
      jwks_uri: `${ISSUER}/.well-known/jwks.json`,
      // OIDC metadata
      scopes_supported: PARTNER_OAUTH_SCOPES,
      response_types_supported: ["code"],
      grant_types_supported: ["authorization_code", "refresh_token"],
      subject_types_supported: ["public"],
      id_token_signing_alg_values_supported: ["RS256"],
      token_endpoint_auth_methods_supported: [
        "client_secret_basic",
        "client_secret_post",
      ],
      code_challenge_methods_supported: ["S256", "plain"],
      claims_supported: [
        "sub",
        "iss",
        "aud",
        "exp",
        "iat",
        "auth_time",
        "nonce",
        "email",
        "email_verified",
        "name",
        "roles",
        "tenant_id",
        "locale",
      ],
      // Extensions
      service_documentation: "https://dev.sahool.app/partner/",
      ui_locales_supported: ["ar", "en"],
    };
  }
}
