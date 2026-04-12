/**
 * Authorize service — validates /authorize requests and manages consent
 * grants. Two public methods:
 *
 *   • validateRequest   — parses + validates every OAuth parameter
 *                          against the registered client before showing
 *                          the user a consent screen.
 *   • buildSuccessRedirect  — called after the user approves.
 *   • buildDenialRedirect   — called after the user denies.
 *
 * All errors up to the client-validation step are returned to the user
 * as safe HTML (we cannot redirect back until we've verified the redirect
 * URI — RFC 6749 § 3.1.2.4). Errors after that redirect to the client
 * with error= and state=.
 */

import {
  BadRequestException,
  Injectable,
  Logger,
  NotFoundException,
} from "@nestjs/common";
import type { OAuthClient } from "../../prisma/generated/client";
import { PrismaService } from "../prisma/prisma.service";
import { OAuthService } from "./oauth.service";

export interface AuthorizeRequest {
  response_type?: string;
  client_id?: string;
  redirect_uri?: string;
  scope?: string;
  state?: string;
  nonce?: string;
  code_challenge?: string;
  code_challenge_method?: string;
  prompt?: string;
}

export interface ValidatedAuthorize {
  client: OAuthClient;
  redirectUri: string;
  scopes: string[];
  state: string | null;
  nonce: string | null;
  codeChallenge: string | null;
  codeChallengeMethod: string | null;
  prompt: string | null;
  /** True when the user has already consented to this (or a superset) scope */
  consentMemory: string[] | null;
}

export interface AuthenticatedUser {
  id: string;
  tenantId: string;
  email?: string;
  name?: string;
  nameAr?: string;
  locale?: "ar" | "en";
}

@Injectable()
export class AuthorizeService {
  private readonly logger = new Logger(AuthorizeService.name);

  constructor(
    private readonly prisma: PrismaService,
    private readonly oauth: OAuthService,
  ) {}

  /**
   * Validate an /authorize request. Client-level errors (unknown client,
   * bad redirect_uri) throw NotFoundException / BadRequestException; the
   * controller shows a safe HTML page and does NOT redirect.
   *
   * Protocol-level errors that DO permit a redirect (bad scope, bad
   * response_type) are still thrown here; the controller is responsible
   * for catching them and building a redirect back to the client.
   */
  async validateRequest(
    req: AuthorizeRequest,
    user: AuthenticatedUser,
  ): Promise<ValidatedAuthorize> {
    if (!req.client_id) {
      throw new BadRequestException({
        error: "invalid_request",
        error_description: "client_id is required",
      });
    }
    const client = await this.prisma.oAuthClient.findUnique({
      where: { clientId: req.client_id },
    });
    if (!client || client.status !== "active" || client.revokedAt !== null) {
      // DO NOT redirect — per RFC 6749 § 3.1.2.4 we must not redirect
      // unless we've verified the redirect_uri, which we can't without
      // a known client.
      throw new NotFoundException({
        error: "invalid_client",
        error_description: "Unknown or suspended client",
      });
    }

    if (!req.redirect_uri) {
      throw new BadRequestException({
        error: "invalid_request",
        error_description: "redirect_uri is required",
      });
    }
    if (!client.redirectUris.includes(req.redirect_uri)) {
      // Same safety rule — do not redirect to an unregistered URI.
      throw new BadRequestException({
        error: "invalid_request",
        error_description: "redirect_uri is not registered for this client",
      });
    }

    if (req.response_type !== "code") {
      throw new BadRequestException({
        error: "unsupported_response_type",
        error_description: "Only response_type=code is supported",
      });
    }

    const requestedScopes = (req.scope ?? "").split(/\s+/).filter(Boolean);
    if (requestedScopes.length === 0) {
      throw new BadRequestException({
        error: "invalid_scope",
        error_description: "scope parameter is required",
      });
    }
    const invalid = requestedScopes.filter(
      (s) => !client.allowedScopes.includes(s),
    );
    if (invalid.length) {
      throw new BadRequestException({
        error: "invalid_scope",
        error_description: `Client is not allowed to request: ${invalid.join(", ")}`,
      });
    }

    // PKCE validation — S256 recommended, plain allowed for confidential clients
    if (req.code_challenge) {
      const m = req.code_challenge_method ?? "plain";
      if (m !== "S256" && m !== "plain") {
        throw new BadRequestException({
          error: "invalid_request",
          error_description: `Unsupported code_challenge_method: ${m}`,
        });
      }
    }

    // Look up prior consent memory — may let us skip the consent screen
    const grant = await this.prisma.consentGrant.findUnique({
      where: {
        clientId_userId: {
          clientId: client.id,
          userId: user.id,
        },
      },
    });
    const consentMemory =
      grant && grant.revokedAt === null ? grant.scopes : null;

    return {
      client,
      redirectUri: req.redirect_uri,
      scopes: requestedScopes,
      state: req.state ?? null,
      nonce: req.nonce ?? null,
      codeChallenge: req.code_challenge ?? null,
      codeChallengeMethod: req.code_challenge_method ?? null,
      prompt: req.prompt ?? null,
      consentMemory,
    };
  }

  /**
   * After the user clicks "Allow", record the consent grant (upsert to
   * union scopes), mint an authorization code, and build the redirect URL.
   */
  async buildSuccessRedirect(
    validated: ValidatedAuthorize,
    user: AuthenticatedUser,
    consentIp?: string,
    consentUserAgent?: string,
  ): Promise<string> {
    // Upsert ConsentGrant so the next /authorize with same-or-subset scopes
    // can skip the prompt (consent memory).
    const newScopes = unique([
      ...(validated.consentMemory ?? []),
      ...validated.scopes,
    ]);
    await this.prisma.consentGrant.upsert({
      where: {
        clientId_userId: {
          clientId: validated.client.id,
          userId: user.id,
        },
      },
      update: {
        scopes: newScopes,
        revokedAt: null,
        consentIp: consentIp ?? undefined,
        consentUserAgent: consentUserAgent ?? undefined,
      },
      create: {
        clientId: validated.client.id,
        userId: user.id,
        tenantId: user.tenantId,
        scopes: newScopes,
        consentIp: consentIp ?? null,
        consentUserAgent: consentUserAgent ?? null,
      },
    });

    const { code } = await this.oauth.createAuthorizationCode({
      clientId: validated.client.id,
      userId: user.id,
      tenantId: user.tenantId,
      redirectUri: validated.redirectUri,
      scopes: validated.scopes,
      codeChallenge: validated.codeChallenge ?? undefined,
      codeChallengeMethod: validated.codeChallengeMethod ?? undefined,
      nonce: validated.nonce ?? undefined,
    });

    return this.appendParams(validated.redirectUri, {
      code,
      state: validated.state ?? undefined,
    });
  }

  /**
   * After the user clicks "Deny", bounce back to the client with
   * error=access_denied (OAuth 2.0 § 4.1.2.1).
   */
  buildDenialRedirect(validated: ValidatedAuthorize): string {
    return this.appendParams(validated.redirectUri, {
      error: "access_denied",
      error_description: "User denied the authorization request",
      state: validated.state ?? undefined,
    });
  }

  /**
   * After a non-fatal protocol error post-client-validation (e.g. PKCE
   * method mismatch), bounce back with an OAuth error.
   */
  buildErrorRedirect(
    redirectUri: string,
    error: string,
    description: string,
    state: string | null,
  ): string {
    return this.appendParams(redirectUri, {
      error,
      error_description: description,
      state: state ?? undefined,
    });
  }

  private appendParams(
    base: string,
    params: Record<string, string | undefined>,
  ): string {
    const url = new URL(base);
    for (const [k, v] of Object.entries(params)) {
      if (v !== undefined) url.searchParams.set(k, v);
    }
    return url.toString();
  }
}

function unique<T>(arr: T[]): T[] {
  return Array.from(new Set(arr));
}
