/**
 * Request-logging interceptor with correlation id propagation.
 * Sensitive OAuth bodies (grant_type, code, refresh_token, client_secret)
 * are redacted — we NEVER log a token value, even in debug.
 */

import {
  CallHandler,
  ExecutionContext,
  Injectable,
  Logger,
  NestInterceptor,
} from "@nestjs/common";
import { randomUUID } from "crypto";
import type { Request, Response } from "express";
import { Observable, tap } from "rxjs";

const REDACT_FIELDS = new Set([
  "client_secret",
  "code",
  "refresh_token",
  "access_token",
  "id_token",
  "password",
  "authorization",
]);

@Injectable()
export class RequestLoggingInterceptor implements NestInterceptor {
  private readonly logger: Logger;

  constructor(serviceName: string) {
    this.logger = new Logger(serviceName);
  }

  intercept(ctx: ExecutionContext, next: CallHandler): Observable<unknown> {
    const http = ctx.switchToHttp();
    const req = http.getRequest<Request>();
    const res = http.getResponse<Response>();

    const reqId = (req.headers["x-request-id"] as string) ?? randomUUID();
    res.setHeader("X-Request-Id", reqId);

    const started = Date.now();
    const { method, path } = req;

    return next.handle().pipe(
      tap({
        next: () => {
          const elapsed = Date.now() - started;
          this.logger.log(
            JSON.stringify({
              reqId,
              method,
              path,
              status: res.statusCode,
              elapsedMs: elapsed,
            }),
          );
        },
        error: (err: unknown) => {
          const elapsed = Date.now() - started;
          const message = err instanceof Error ? err.message : String(err);
          this.logger.warn(
            JSON.stringify({
              reqId,
              method,
              path,
              status: res.statusCode,
              elapsedMs: elapsed,
              error: message,
            }),
          );
        },
      }),
    );
  }

  /** Exposed for tests — redacts sensitive keys from a flat object. */
  static redact(obj: Record<string, unknown>): Record<string, unknown> {
    const out: Record<string, unknown> = {};
    for (const [k, v] of Object.entries(obj)) {
      out[k] = REDACT_FIELDS.has(k.toLowerCase()) ? "[REDACTED]" : v;
    }
    return out;
  }
}
