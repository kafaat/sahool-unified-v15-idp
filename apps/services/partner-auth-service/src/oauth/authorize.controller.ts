/**
 * /partner/v1/oauth/authorize — OAuth 2.0 Authorization Endpoint.
 *
 * GET:
 *   1. Validate request + client + redirect_uri.
 *   2. Ensure user is signed in (SahoolSessionGuard).
 *   3. If user has previously consented to a superset of requested scopes
 *      AND prompt != "consent", skip the screen and immediately redirect.
 *   4. Otherwise render the bilingual consent HTML.
 *
 * POST:
 *   1. Verify CSRF token is valid for the current user.
 *   2. Re-validate OAuth params (defense against tampered hidden fields).
 *   3. On decision=allow: record consent + mint auth code + 302 to client.
 *   4. On decision=deny: 302 to client with error=access_denied.
 */

import {
  BadRequestException,
  Body,
  Controller,
  Get,
  HttpCode,
  HttpStatus,
  Post,
  Query,
  Req,
  Res,
  UseGuards,
} from "@nestjs/common";
import { ApiOperation, ApiTags } from "@nestjs/swagger";
import type { Request, Response } from "express";
import { AuthorizeService } from "./authorize.service";
import type {
  AuthorizeRequest,
  AuthenticatedUser,
  ValidatedAuthorize,
} from "./authorize.service";
import { CsrfService } from "../utils/csrf.service";
import { SahoolSessionGuard } from "../utils/sahool-session.guard";
import { renderConsent } from "../templates/consent.html";

interface AuthorizePostBody extends AuthorizeRequest {
  csrf_token?: string;
  decision?: "allow" | "deny";
}

@ApiTags("OAuth")
@Controller("partner/v1/oauth/authorize")
export class AuthorizeController {
  constructor(
    private readonly authorize: AuthorizeService,
    private readonly csrf: CsrfService,
  ) {}

  @Get()
  @UseGuards(SahoolSessionGuard)
  @ApiOperation({
    summary: "OAuth 2.0 authorization endpoint (renders consent screen)",
  })
  async get(
    @Query() query: AuthorizeRequest,
    @Req() req: Request,
    @Res() res: Response,
  ) {
    if (!req.sahoolUser) {
      // Guard set loginRedirect; bounce to SAHOOL login
      return res.redirect(302, req.loginRedirect ?? "https://app.sahool.com/login");
    }

    let validated: ValidatedAuthorize;
    try {
      validated = await this.authorize.validateRequest(query, req.sahoolUser);
    } catch (err) {
      // Client-level errors: render safe error page, do NOT redirect
      if (err instanceof BadRequestException || (err as Error).name === "NotFoundException") {
        const e = err as BadRequestException;
        const body = e.getResponse();
        return res
          .status(e.getStatus ? e.getStatus() : HttpStatus.BAD_REQUEST)
          .type("text/html")
          .send(this.renderError(body));
      }
      throw err;
    }

    // Skip consent if user already approved equal-or-greater scopes
    // (unless the client explicitly requests re-prompt).
    const canSkip =
      validated.prompt !== "consent" &&
      validated.consentMemory !== null &&
      validated.scopes.every((s) => validated.consentMemory!.includes(s));

    if (canSkip) {
      const target = await this.authorize.buildSuccessRedirect(
        validated,
        req.sahoolUser,
        req.ip,
        req.headers["user-agent"],
      );
      return res.redirect(302, target);
    }

    const html = renderConsent({
      csrfToken: this.csrf.issue(req.sahoolUser.id),
      client: {
        name: validated.client.name,
        nameAr: validated.client.nameAr,
        logoUrl: validated.client.logoUrl,
        homepageUrl: validated.client.homepageUrl,
        description: validated.client.description,
      },
      scopes: validated.scopes,
      priorScopes: validated.consentMemory ?? [],
      form: {
        client_id: validated.client.clientId,
        redirect_uri: validated.redirectUri,
        scope: validated.scopes.join(" "),
        state: validated.state,
        nonce: validated.nonce,
        code_challenge: validated.codeChallenge,
        code_challenge_method: validated.codeChallengeMethod,
        response_type: "code",
      },
      user: {
        email: req.sahoolUser.email,
        name: req.sahoolUser.name,
        nameAr: req.sahoolUser.nameAr,
      },
      locale: req.sahoolUser.locale ?? "ar",
      postUrl: req.originalUrl.split("?")[0],
      signOutUrl:
        process.env.SAHOOL_SIGNOUT_URL ?? "https://app.sahool.com/logout",
    });

    res
      .status(HttpStatus.OK)
      .type("text/html")
      .setHeader("X-Frame-Options", "DENY")
      .setHeader("Content-Security-Policy", "default-src 'self'; frame-ancestors 'none'")
      .send(html);
  }

  @Post()
  @UseGuards(SahoolSessionGuard)
  @HttpCode(HttpStatus.FOUND)
  @ApiOperation({ summary: "Process consent decision → redirect to client" })
  async post(
    @Body() body: AuthorizePostBody,
    @Req() req: Request,
    @Res() res: Response,
  ) {
    if (!req.sahoolUser) {
      return res.redirect(302, req.loginRedirect ?? "https://app.sahool.com/login");
    }

    const user: AuthenticatedUser = req.sahoolUser;

    // CSRF first — before we touch anything
    if (!this.csrf.verify(body.csrf_token, user.id)) {
      return res
        .status(HttpStatus.FORBIDDEN)
        .type("text/html")
        .send(this.renderError({
          error: "csrf_failed",
          error_description:
            "CSRF token missing, expired, or not bound to the current user",
        }));
    }

    let validated: ValidatedAuthorize;
    try {
      validated = await this.authorize.validateRequest(body, user);
    } catch (err) {
      // Protocol errors at POST time should still redirect to the client
      // (we've verified the client + redirect URI on the GET already, so
      // the `redirect_uri` in the body is trusted).
      if (body.client_id && body.redirect_uri) {
        const e = err as BadRequestException;
        const resp = (e.getResponse && typeof e.getResponse === "function"
          ? e.getResponse()
          : {}) as { error?: string; error_description?: string };
        return res.redirect(
          302,
          this.authorize.buildErrorRedirect(
            body.redirect_uri,
            resp.error ?? "invalid_request",
            resp.error_description ?? "Invalid request",
            body.state ?? null,
          ),
        );
      }
      throw err;
    }

    if (body.decision === "deny") {
      return res.redirect(302, this.authorize.buildDenialRedirect(validated));
    }
    if (body.decision !== "allow") {
      return res.redirect(
        302,
        this.authorize.buildErrorRedirect(
          validated.redirectUri,
          "invalid_request",
          "Missing decision",
          validated.state,
        ),
      );
    }

    const target = await this.authorize.buildSuccessRedirect(
      validated,
      user,
      req.ip,
      req.headers["user-agent"],
    );
    return res.redirect(302, target);
  }

  // Minimal safe error HTML (no template engine dependency)
  private renderError(body: unknown): string {
    const errObj =
      typeof body === "object" && body !== null
        ? (body as Record<string, string>)
        : { error: "error", error_description: String(body) };
    const escape = (s: string) =>
      s.replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&#34;", "'": "&#39;" })[c]!);
    // nosemgrep: javascript.lang.security.audit.xss.direct-response-write.html-in-template-string,html-in-template-string -- intentional HTML template; user data escaped via esc()
    return `<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>${escape(errObj.error ?? "Error")}</title><meta name="viewport" content="width=device-width,initial-scale=1"><style>body{font-family:-apple-system,sans-serif;max-width:520px;margin:60px auto;padding:24px;color:#1a2332}.code{background:#f2f5f9;padding:16px;border-radius:8px;font-family:monospace}</style></head><body><h1>${escape(errObj.error ?? "Error")}</h1><p class="code">${escape(errObj.error_description ?? "")}</p><p style="color:#7a8699;font-size:13px">If you arrived here from an application, please return to the application — do not proceed with a browser back/forward.</p></body></html>`;
  }
}
