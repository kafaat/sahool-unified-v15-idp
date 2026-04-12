/**
 * FieldView-compatible error envelope:
 *   { error: { code: "…", id: "<uuid>", message: "…", path?: "…" } }
 *
 * Maps NestJS HttpException + runtime errors to this wire shape so partners
 * migrating from Climate FieldView get the same error semantics. OAuth 2.0
 * errors (RFC 6749 § 5.2) are passed through with their canonical codes:
 * invalid_request, invalid_client, invalid_grant, unauthorized_client,
 * unsupported_grant_type, invalid_scope.
 */

import {
  ArgumentsHost,
  Catch,
  ExceptionFilter,
  HttpException,
  HttpStatus,
  Logger,
} from "@nestjs/common";
import { randomUUID } from "crypto";
import type { Request, Response } from "express";

interface OAuthErrorBody {
  error: string;
  error_description?: string;
  error_uri?: string;
}

interface PartnerErrorBody {
  error: {
    code: string;
    id: string;
    message: string;
    path?: string;
  };
}

/** Canonical OAuth 2.0 error codes (RFC 6749 § 5.2, § 4.1.2.1) */
const OAUTH_ERROR_CODES = new Set([
  "invalid_request",
  "invalid_client",
  "invalid_grant",
  "unauthorized_client",
  "unsupported_grant_type",
  "invalid_scope",
  "access_denied",
  "server_error",
  "temporarily_unavailable",
  "unsupported_response_type",
]);

@Catch()
export class PartnerErrorFilter implements ExceptionFilter {
  private readonly logger = new Logger("PartnerErrorFilter");

  catch(exception: unknown, host: ArgumentsHost) {
    const ctx = host.switchToHttp();
    const res = ctx.getResponse<Response>();
    const req = ctx.getRequest<Request>();

    const errorId = (req.headers["x-request-id"] as string) ?? randomUUID();

    let status = HttpStatus.INTERNAL_SERVER_ERROR;
    let code = "server_error";
    let message = "Internal server error";

    if (exception instanceof HttpException) {
      status = exception.getStatus();
      const body = exception.getResponse();
      if (typeof body === "string") {
        message = body;
      } else if (typeof body === "object" && body !== null) {
        const b = body as Record<string, unknown>;
        // Allow controllers to throw OAuth-shaped errors directly
        if (typeof b.error === "string" && OAUTH_ERROR_CODES.has(b.error)) {
          // RFC 6749 § 5.2 — pass through OAuth error body unchanged on /token
          if (req.path.endsWith("/oauth/token") || req.path.endsWith("/oauth/revoke")) {
            res.status(status).json(b as OAuthErrorBody);
            return;
          }
          code = b.error;
          message = (b.error_description as string) ?? String(b.error);
        } else {
          message =
            (b.message as string) ?? (b.error as string) ?? "Request failed";
          code = (b.code as string) ?? this.mapStatusToCode(status);
        }
      }
    } else if (exception instanceof Error) {
      message = exception.message;
      code = "server_error";
      this.logger.error(`Unhandled error: ${exception.stack ?? exception.message}`);
    } else {
      this.logger.error(`Unknown error: ${JSON.stringify(exception)}`);
    }

    if (!OAUTH_ERROR_CODES.has(code)) {
      code = this.mapStatusToCode(status);
    }

    const body: PartnerErrorBody = {
      error: {
        code,
        id: errorId,
        message,
        path: req.path,
      },
    };

    res.setHeader("X-Request-Id", errorId);
    res.status(status).json(body);
  }

  private mapStatusToCode(status: number): string {
    switch (status) {
      case 400: return "invalid_request";
      case 401: return "invalid_client";
      case 403: return "access_denied";
      case 404: return "not_found";
      case 409: return "conflict";
      case 429: return "rate_limited";
      case 500: return "server_error";
      case 502: return "upstream_error";
      case 503: return "temporarily_unavailable";
      case 504: return "gateway_timeout";
      default: return status >= 500 ? "server_error" : "invalid_request";
    }
  }
}
