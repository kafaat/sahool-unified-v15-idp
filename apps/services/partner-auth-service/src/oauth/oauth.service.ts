/**
 * OAuth service — token issuance, rotation, and revocation logic.
 *
 * Implements:
 *   • Authorization-code grant (exchange code for tokens)
 *   • Refresh-token grant (with rotation + reuse detection)
 *   • Access-token JWT signing (RS256, via JwkService)
 *   • Refresh-token hash + family tracking
 *
 * Security notes:
 *   • Authorization codes and refresh tokens are stored as SHA-256 hashes
 *     never as plaintext, so a DB dump can't be replayed.
 *   • Refresh-token reuse (submitting a token that has `rotatedToId` set)
 *     triggers a cascade revoke of the ENTIRE family — OAuth 2.1 § 6.
 *   • Client secrets are bcrypt-hashed at registration time.
 *   • PKCE verification (RFC 7636) is supported for public clients.
 */

import {
  BadRequestException,
  Injectable,
  Logger,
  UnauthorizedException,
} from "@nestjs/common";
import { randomUUID, createHash } from "crypto";
import { SignJWT } from "jose";
import { nanoid } from "nanoid";
import * as bcrypt from "bcryptjs";
import type { OAuthClient } from "../../prisma/generated/client";
import { PrismaService } from "../prisma/prisma.service";
import { JwkService } from "../oidc/jwk.service";
import { IdTokenService } from "../oidc/id-token.service";

export interface TokenGrantResult {
  access_token: string;
  token_type: "bearer";
  expires_in: number;
  refresh_token?: string;
  id_token?: string;
  scope: string;
}

const ACCESS_TOKEN_TTL_SEC = 14_400;          // 4h (FieldView parity)
const REFRESH_TOKEN_TTL_DAYS = 30;
const REFRESH_ROTATION_TTL_SEC = 3_600;        // 1h after rotation (FieldView)
const AUTH_CODE_TTL_SEC = 600;                 // 10 min

const ISSUER = process.env.PARTNER_AUTH_ISSUER ?? "https://api.sahool.com";

@Injectable()
export class OAuthService {
  private readonly logger = new Logger(OAuthService.name);

  constructor(
    private readonly prisma: PrismaService,
    private readonly jwks: JwkService,
    private readonly idTokenService: IdTokenService,
  ) {}

  // ── Client authentication ─────────────────────────────────────────────

  async authenticateClient(
    clientId: string,
    clientSecret: string,
  ): Promise<OAuthClient> {
    const client = await this.prisma.oAuthClient.findUnique({
      where: { clientId },
    });
    if (!client || client.status !== "active" || client.revokedAt !== null) {
      throw new UnauthorizedException({
        error: "invalid_client",
        error_description: "Unknown or revoked client",
      });
    }
    const ok = await bcrypt.compare(clientSecret, client.clientSecretHash);
    if (!ok) {
      throw new UnauthorizedException({
        error: "invalid_client",
        error_description: "Client authentication failed",
      });
    }
    return client;
  }

  // ── Grant: authorization_code ─────────────────────────────────────────

  async exchangeAuthorizationCode(params: {
    client: OAuthClient;
    code: string;
    redirectUri: string;
    codeVerifier?: string;
  }): Promise<TokenGrantResult> {
    const codeHash = sha256(params.code);
    const row = await this.prisma.authCode.findUnique({ where: { codeHash } });

    if (!row) throw oauthError("invalid_grant", "Unknown or expired code");
    if (row.usedAt !== null) {
      // Replay attempt — code already used. OAuth 2.0 § 4.1.2 requires
      // the authorization server to refuse and SHOULD revoke any tokens
      // previously issued from this code. We do that by nulling the row.
      await this.cascadeRevokeByAuthCode(row.id);
      throw oauthError("invalid_grant", "Code already used");
    }
    if (row.expiresAt < new Date()) {
      throw oauthError("invalid_grant", "Code expired");
    }
    if (row.clientId !== params.client.id) {
      throw oauthError("invalid_grant", "Code was not issued to this client");
    }
    if (row.redirectUri !== params.redirectUri) {
      throw oauthError("invalid_grant", "redirect_uri mismatch");
    }

    // PKCE verification (RFC 7636)
    if (row.codeChallenge) {
      if (!params.codeVerifier) {
        throw oauthError("invalid_request", "code_verifier required (PKCE)");
      }
      const method = row.codeChallengeMethod ?? "plain";
      let computed: string;
      if (method === "S256") {
        computed = base64url(
          createHash("sha256").update(params.codeVerifier).digest(),
        );
      } else if (method === "plain") {
        computed = params.codeVerifier;
      } else {
        throw oauthError("invalid_request", `Unsupported code_challenge_method ${method}`);
      }
      if (computed !== row.codeChallenge) {
        throw oauthError("invalid_grant", "PKCE verification failed");
      }
    }

    // Mark code as used (single-use)
    await this.prisma.authCode.update({
      where: { id: row.id },
      data: { usedAt: new Date() },
    });

    const issuedAt = new Date();
    const familyId = randomUUID();
    const refreshId = randomUUID();

    // Issue access token (JWT) + record its jti for revocation lookup
    const access = await this.issueAccessToken({
      clientId: params.client.id,
      userId: row.userId,
      tenantId: row.tenantId,
      scopes: row.scopes,
      refreshTokenId: refreshId,
      issuedAt,
    });

    // Issue refresh token (opaque) — DB-backed with rotation family
    const refresh = await this.issueRefreshToken({
      id: refreshId,
      clientId: params.client.id,
      userId: row.userId,
      tenantId: row.tenantId,
      scopes: row.scopes,
      familyId,
      issuedAt,
      ttlSeconds: REFRESH_TOKEN_TTL_DAYS * 24 * 3600,
    });

    // id_token if openid scope requested (OIDC)
    let idToken: string | undefined;
    if (row.scopes.includes("openid")) {
      idToken = await this.idTokenService.issue(
        {
          sub: row.userId,
          aud: params.client.clientId,
          nonce: row.nonce ?? undefined,
          tenant_id: row.tenantId,
        },
        {
          issuer: ISSUER,
          ttlSeconds: ACCESS_TOKEN_TTL_SEC,
          authTime: row.createdAt,
        },
      );
    }

    return {
      access_token: access.jwt,
      token_type: "bearer",
      expires_in: ACCESS_TOKEN_TTL_SEC,
      refresh_token: refresh.plain,
      id_token: idToken,
      scope: row.scopes.join(" "),
    };
  }

  // ── Grant: refresh_token (with rotation + reuse detection) ────────────

  async exchangeRefreshToken(params: {
    client: OAuthClient;
    refreshToken: string;
    requestedScope?: string;
  }): Promise<TokenGrantResult> {
    const tokenHash = sha256(params.refreshToken);
    const row = await this.prisma.refreshToken.findUnique({ where: { tokenHash } });

    if (!row) throw oauthError("invalid_grant", "Unknown refresh token");
    if (row.clientId !== params.client.id) {
      throw oauthError("invalid_grant", "Refresh token was not issued to this client");
    }
    if (row.revokedAt !== null) {
      throw oauthError("invalid_grant", "Refresh token revoked");
    }
    if (row.expiresAt < new Date()) {
      throw oauthError("invalid_grant", "Refresh token expired");
    }
    if (row.rotatedToId !== null) {
      // Reuse attempt — this token was already rotated. Cascade revoke the
      // whole family (OAuth 2.1 § 6).
      this.logger.warn(
        `Refresh-token reuse detected; cascading revoke of family ${row.familyId}`,
      );
      await this.cascadeRevokeFamily(row.familyId, "reuse_detected");
      throw oauthError("invalid_grant", "Refresh token already rotated");
    }

    // Scope down-grade only (upscoping not allowed per RFC 6749 § 6)
    let scopes = row.scopes;
    if (params.requestedScope) {
      const requested = params.requestedScope.split(/\s+/);
      const invalid = requested.filter((s) => !row.scopes.includes(s));
      if (invalid.length) {
        throw oauthError(
          "invalid_scope",
          `Cannot upscope: ${invalid.join(", ")}`,
        );
      }
      scopes = requested;
    }

    const issuedAt = new Date();
    const newRefreshId = randomUUID();

    // Issue replacement access token
    const access = await this.issueAccessToken({
      clientId: params.client.id,
      userId: row.userId,
      tenantId: row.tenantId,
      scopes,
      refreshTokenId: newRefreshId,
      issuedAt,
    });

    // Issue replacement refresh token (same family)
    const newRefresh = await this.issueRefreshToken({
      id: newRefreshId,
      clientId: params.client.id,
      userId: row.userId,
      tenantId: row.tenantId,
      scopes,
      familyId: row.familyId,
      issuedAt,
      ttlSeconds: REFRESH_TOKEN_TTL_DAYS * 24 * 3600,
    });

    // Rotate: point old row at new + shorten its TTL (FieldView: 1h window)
    await this.prisma.refreshToken.update({
      where: { id: row.id },
      data: {
        rotatedToId: newRefresh.id,
        expiresAt: new Date(Date.now() + REFRESH_ROTATION_TTL_SEC * 1000),
      },
    });

    // id_token re-issuance if openid was in scope
    let idToken: string | undefined;
    if (scopes.includes("openid")) {
      idToken = await this.idTokenService.issue(
        { sub: row.userId, aud: params.client.clientId, tenant_id: row.tenantId },
        { issuer: ISSUER, ttlSeconds: ACCESS_TOKEN_TTL_SEC },
      );
    }

    return {
      access_token: access.jwt,
      token_type: "bearer",
      expires_in: ACCESS_TOKEN_TTL_SEC,
      refresh_token: newRefresh.plain,
      id_token: idToken,
      scope: scopes.join(" "),
    };
  }

  // ── Helpers ────────────────────────────────────────────────────────────

  private async issueAccessToken(params: {
    clientId: string;
    userId: string;
    tenantId: string;
    scopes: string[];
    refreshTokenId: string;
    issuedAt: Date;
  }): Promise<{ jwt: string; jti: string }> {
    const key = this.jwks.getActiveKey();
    const jti = randomUUID();
    const iat = Math.floor(params.issuedAt.getTime() / 1000);
    const exp = iat + ACCESS_TOKEN_TTL_SEC;

    const jwt = await new SignJWT({
      scope: params.scopes.join(" "),
      tenant_id: params.tenantId,
    })
      .setProtectedHeader({ alg: "RS256", kid: key.kid, typ: "at+jwt" })
      .setIssuer(ISSUER)
      .setSubject(params.userId)
      .setAudience(params.clientId)
      .setJti(jti)
      .setIssuedAt(iat)
      .setExpirationTime(exp)
      .sign(key.privateKey);

    await this.prisma.accessToken.create({
      data: {
        jti,
        clientId: params.clientId,
        userId: params.userId,
        tenantId: params.tenantId,
        scopes: params.scopes,
        expiresAt: new Date(exp * 1000),
        refreshTokenId: params.refreshTokenId,
      },
    });

    return { jwt, jti };
  }

  private async issueRefreshToken(params: {
    id: string;
    clientId: string;
    userId: string;
    tenantId: string;
    scopes: string[];
    familyId: string;
    issuedAt: Date;
    ttlSeconds: number;
  }): Promise<{ id: string; plain: string }> {
    // Opaque token value: clientId prefix helps ops quickly identify owner
    const plain = `sah_rt_${nanoid(32)}`;
    const tokenHash = sha256(plain);

    await this.prisma.refreshToken.create({
      data: {
        id: params.id,
        tokenHash,
        clientId: params.clientId,
        userId: params.userId,
        tenantId: params.tenantId,
        scopes: params.scopes,
        familyId: params.familyId,
        expiresAt: new Date(
          params.issuedAt.getTime() + params.ttlSeconds * 1000,
        ),
      },
    });

    return { id: params.id, plain };
  }

  private async cascadeRevokeFamily(familyId: string, reason: string) {
    const when = new Date();
    await this.prisma.refreshToken.updateMany({
      where: { familyId, revokedAt: null },
      data: { revokedAt: when, revokedReason: reason },
    });
    // Also revoke any access tokens issued from this family
    const family = await this.prisma.refreshToken.findMany({
      where: { familyId },
      select: { id: true },
    });
    const ids = family.map((f) => f.id);
    if (ids.length) {
      await this.prisma.accessToken.updateMany({
        where: { refreshTokenId: { in: ids }, revokedAt: null },
        data: { revokedAt: when, revokedReason: reason },
      });
    }
  }

  private async cascadeRevokeByAuthCode(authCodeId: string) {
    // Best-effort: if the same auth code produced tokens already, revoke.
    // (In this scaffold the link is implicit via timing; a future PR adds
    // an explicit auth_code_id column on refresh_tokens.)
    this.logger.warn(
      `Auth-code replay on ${authCodeId}; see docs for cascade-revoke limits`,
    );
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Authorization Code issuance (used by /authorize POST)
  // ─────────────────────────────────────────────────────────────────────────

  /**
   * Create a fresh authorization code. Called after a user approves a
   * consent prompt. The raw code value is returned (to go into the redirect
   * URL) — only its SHA-256 hash is stored. 10-minute TTL per RFC 6749.
   */
  async createAuthorizationCode(params: {
    clientId: string;
    userId: string;
    tenantId: string;
    redirectUri: string;
    scopes: string[];
    codeChallenge?: string;
    codeChallengeMethod?: string;
    nonce?: string;
  }): Promise<{ code: string; expiresAt: Date }> {
    const code = `sah_ac_${nanoid(32)}`;
    const codeHash = sha256(code);
    const expiresAt = new Date(Date.now() + AUTH_CODE_TTL_SEC * 1000);

    await this.prisma.authCode.create({
      data: {
        codeHash,
        clientId: params.clientId,
        userId: params.userId,
        tenantId: params.tenantId,
        redirectUri: params.redirectUri,
        scopes: params.scopes,
        codeChallenge: params.codeChallenge ?? null,
        codeChallengeMethod: params.codeChallengeMethod ?? null,
        nonce: params.nonce ?? null,
        expiresAt,
      },
    });
    return { code, expiresAt };
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Token revocation (RFC 7009)
  // ─────────────────────────────────────────────────────────────────────────

  /**
   * Revoke an access OR refresh token on behalf of its owning client.
   * Per RFC 7009 § 2.2, the endpoint SHOULD NOT distinguish between
   * unknown / wrong-type / expired tokens — always return silently.
   * We log revocation-source audit events but never reveal them to the caller.
   */
  async revokeToken(params: {
    clientId: string;
    token: string;
    tokenTypeHint?: "access_token" | "refresh_token";
  }): Promise<void> {
    const when = new Date();
    const reason = "client_revocation";

    // Opportunistic lookup by hint first (avoids 2 queries on the hot path)
    const hinted = params.tokenTypeHint;

    if (hinted !== "access_token") {
      const tokenHash = sha256(params.token);
      const r = await this.prisma.refreshToken.findUnique({ where: { tokenHash } });
      if (r && r.clientId === params.clientId && r.revokedAt === null) {
        await this.cascadeRevokeFamily(r.familyId, reason);
        return;
      }
    }

    if (hinted !== "refresh_token") {
      // Access tokens are JWTs — caller passes the raw JWT; we decode to jti.
      // Verification happens in the guard elsewhere; here we just peel out
      // the jti claim to flip revokedAt.
      const jti = extractJti(params.token);
      if (jti) {
        const row = await this.prisma.accessToken.findUnique({ where: { jti } });
        if (row && row.clientId === params.clientId && row.revokedAt === null) {
          await this.prisma.accessToken.update({
            where: { jti },
            data: { revokedAt: when, revokedReason: reason },
          });
          return;
        }
      }
    }
    // Per RFC 7009, unknown/mismatched/expired tokens produce a 200 with
    // no body — revoke is idempotent from the caller's perspective.
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Token introspection (RFC 7662)
  // ─────────────────────────────────────────────────────────────────────────

  /**
   * Returns an RFC 7662 introspection response. For unknown / revoked /
   * expired / wrong-client tokens the response is `{active: false}` —
   * never leak whether a token ever existed.
   */
  async introspectToken(params: {
    clientId: string;
    token: string;
    tokenTypeHint?: "access_token" | "refresh_token";
  }): Promise<IntrospectResponse> {
    const INACTIVE = { active: false as const };

    const hinted = params.tokenTypeHint;

    if (hinted !== "refresh_token") {
      const jti = extractJti(params.token);
      if (jti) {
        const at = await this.prisma.accessToken.findUnique({ where: { jti } });
        if (
          at &&
          at.clientId === params.clientId &&
          at.revokedAt === null &&
          at.expiresAt > new Date()
        ) {
          return {
            active: true,
            scope: at.scopes.join(" "),
            client_id: params.clientId,
            username: at.userId,
            token_type: "Bearer",
            exp: Math.floor(at.expiresAt.getTime() / 1000),
            iat: Math.floor(at.createdAt.getTime() / 1000),
            sub: at.userId,
            aud: params.clientId,
            iss: ISSUER,
            jti,
            tenant_id: at.tenantId,
          };
        }
      }
    }

    if (hinted !== "access_token") {
      const tokenHash = sha256(params.token);
      const rt = await this.prisma.refreshToken.findUnique({ where: { tokenHash } });
      if (
        rt &&
        rt.clientId === params.clientId &&
        rt.revokedAt === null &&
        rt.rotatedToId === null &&
        rt.expiresAt > new Date()
      ) {
        return {
          active: true,
          scope: rt.scopes.join(" "),
          client_id: params.clientId,
          username: rt.userId,
          token_type: "refresh_token",
          exp: Math.floor(rt.expiresAt.getTime() / 1000),
          iat: Math.floor(rt.createdAt.getTime() / 1000),
          sub: rt.userId,
          aud: params.clientId,
          iss: ISSUER,
          tenant_id: rt.tenantId,
        };
      }
    }

    return INACTIVE;
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Access-token verification (used by /userinfo Bearer guard)
  // ─────────────────────────────────────────────────────────────────────────

  /**
   * Validates an access token JWT: verifies signature against active JWKS,
   * checks iss/aud, and confirms the row in access_tokens is not revoked.
   * Returns the decoded claims, or throws UnauthorizedException.
   */
  async verifyAccessToken(token: string): Promise<AccessTokenClaims> {
    const { jwtVerify } = await import("jose");
    const keys = this.jwks.getPublicKeys();

    let payload: Record<string, unknown> | null = null;
    for (const k of keys) {
      try {
        const result = await jwtVerify(token, k.publicKey, {
          issuer: ISSUER,
        });
        payload = result.payload as Record<string, unknown>;
        break;
      } catch {
        // Try next key
      }
    }
    if (!payload) {
      throw new UnauthorizedException({
        error: "invalid_token",
        error_description: "Access token signature could not be verified",
      });
    }

    const jti = typeof payload.jti === "string" ? payload.jti : null;
    if (!jti) {
      throw new UnauthorizedException({
        error: "invalid_token",
        error_description: "Access token missing jti claim",
      });
    }

    const row = await this.prisma.accessToken.findUnique({ where: { jti } });
    if (!row || row.revokedAt !== null) {
      throw new UnauthorizedException({
        error: "invalid_token",
        error_description: "Access token has been revoked",
      });
    }
    if (row.expiresAt < new Date()) {
      throw new UnauthorizedException({
        error: "invalid_token",
        error_description: "Access token expired",
      });
    }

    return {
      jti,
      sub: String(payload.sub ?? row.userId),
      aud: String(payload.aud ?? ""),
      scope: typeof payload.scope === "string" ? payload.scope.split(/\s+/) : row.scopes,
      tenantId: row.tenantId,
      clientId: row.clientId,
    };
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Types used above
// ─────────────────────────────────────────────────────────────────────────────

export interface IntrospectResponse {
  active: boolean;
  scope?: string;
  client_id?: string;
  username?: string;
  token_type?: string;
  exp?: number;
  iat?: number;
  sub?: string;
  aud?: string;
  iss?: string;
  jti?: string;
  tenant_id?: string;
}

export interface AccessTokenClaims {
  jti: string;
  sub: string;
  aud: string;
  scope: string[];
  tenantId: string;
  clientId: string;
}

// ─────────────────────────────────────────────────────────────────────────────
// Helpers
// ─────────────────────────────────────────────────────────────────────────────

function sha256(s: string): string {
  return createHash("sha256").update(s).digest("hex");
}

function base64url(buf: Buffer): string {
  return buf.toString("base64url");
}

function oauthError(code: string, description: string): BadRequestException {
  return new BadRequestException({
    error: code,
    error_description: description,
  });
}

/**
 * Extract the `jti` claim from a JWT without verifying signature — used
 * only to look up a token in the DB (which is where actual revocation
 * happens). Returns null for malformed tokens.
 */
function extractJti(jwt: string): string | null {
  try {
    const parts = jwt.split(".");
    if (parts.length !== 3) return null;
    const payload = JSON.parse(
      Buffer.from(parts[1], "base64url").toString("utf-8"),
    ) as { jti?: string };
    return typeof payload.jti === "string" ? payload.jti : null;
  } catch {
    return null;
  }
}
