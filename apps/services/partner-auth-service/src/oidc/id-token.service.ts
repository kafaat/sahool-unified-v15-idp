/**
 * id_token service — builds and signs OIDC id_tokens.
 * Claims follow OIDC Core 1.0 § 2.
 */

import { Injectable } from "@nestjs/common";
import { SignJWT } from "jose";
import { JwkService } from "./jwk.service";

export interface IdTokenClaims {
  sub: string;              // user id (UUID)
  aud: string;              // client_id
  nonce?: string;           // replay protection
  email?: string;
  email_verified?: boolean;
  name?: string;
  roles?: string[];
  tenant_id?: string;
  locale?: "ar" | "en";
}

@Injectable()
export class IdTokenService {
  constructor(private readonly jwkService: JwkService) {}

  /** Sign a fresh id_token for the given user + client + optional nonce. */
  async issue(
    claims: IdTokenClaims,
    opts: { issuer: string; ttlSeconds: number; authTime?: Date },
  ): Promise<string> {
    const key = this.jwkService.getActiveKey();
    const now = Math.floor(Date.now() / 1000);

    return await new SignJWT({
      email: claims.email,
      email_verified: claims.email_verified,
      name: claims.name,
      roles: claims.roles,
      tenant_id: claims.tenant_id,
      locale: claims.locale,
      nonce: claims.nonce,
      auth_time: opts.authTime
        ? Math.floor(opts.authTime.getTime() / 1000)
        : now,
    })
      .setProtectedHeader({ alg: "RS256", kid: key.kid, typ: "JWT" })
      .setIssuer(opts.issuer)
      .setSubject(claims.sub)
      .setAudience(claims.aud)
      .setIssuedAt(now)
      .setExpirationTime(now + opts.ttlSeconds)
      .sign(key.privateKey);
  }
}
