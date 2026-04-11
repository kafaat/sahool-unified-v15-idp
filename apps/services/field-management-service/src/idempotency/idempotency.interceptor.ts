/**
 * Idempotency Interceptor
 * معترض Idempotency — يفحص رأس Idempotency-Key قبل تنفيذ الطلب
 *
 * Usage: annotate a controller method with @UseInterceptors(IdempotencyInterceptor)
 * and it will:
 *   1. Read the Idempotency-Key header.
 *   2. If absent, pass through unchanged.
 *   3. If present, look up (tenant, key, method, path). On hit, replay
 *      the stored response. On miss, execute the handler and cache the
 *      response afterwards.
 */

import {
  Injectable,
  NestInterceptor,
  ExecutionContext,
  CallHandler,
  HttpException,
  Logger,
} from "@nestjs/common";
import { Observable, from, throwError } from "rxjs";
import { switchMap, tap, catchError } from "rxjs/operators";
import { IdempotencyService } from "./idempotency.service";
import { getRequestTenantId } from "../auth/tenant.utils";

@Injectable()
export class IdempotencyInterceptor implements NestInterceptor {
  private readonly logger = new Logger(IdempotencyInterceptor.name);

  constructor(private readonly idem: IdempotencyService) {}

  intercept(ctx: ExecutionContext, next: CallHandler): Observable<unknown> {
    const req = ctx.switchToHttp().getRequest();
    const res = ctx.switchToHttp().getResponse();

    const key: string | undefined =
      req.headers?.["idempotency-key"] ??
      req.headers?.["Idempotency-Key"];

    // No key supplied — pass through untouched. Idempotency is
    // opt-in for each request.
    if (!key || typeof key !== "string" || !key.trim()) {
      return next.handle();
    }

    // Tenant context is required to scope the key — if TenantGuard
    // hasn't run yet (unexpected), bail out and let the request
    // proceed without idempotency protection.
    let tenantId: string;
    try {
      tenantId = getRequestTenantId(req);
    } catch {
      return next.handle();
    }

    const method: string = (req.method ?? "POST").toUpperCase();
    const path: string = (req.originalUrl ?? req.url ?? "/").split("?")[0];

    return from(
      this.idem.lookup({ tenantId, key, method, path, body: req.body }),
    ).pipe(
      switchMap((result) => {
        if (result.hit) {
          // Replay the cached response verbatim.
          this.logger.debug(
            `Idempotency hit: ${method} ${path} key=${key.slice(0, 8)}...`,
          );
          res.setHeader?.("Idempotent-Replayed", "true");
          res.status?.(result.status);
          return from([result.body]);
        }
        // Execute the handler, then cache the response.
        return next.handle().pipe(
          tap(async (body) => {
            const status: number =
              res.statusCode ?? (method === "POST" ? 201 : 200);
            await this.idem.store({
              tenantId,
              key,
              method,
              path,
              body: req.body,
              responseStatus: status,
              responseBody: body,
            });
          }),
          catchError((err) => {
            // On 4xx/5xx we do NOT cache — the client should be able
            // to retry after fixing whatever caused the failure.
            if (err instanceof HttpException && err.getStatus() >= 500) {
              // 5xx = transient. Don't persist so retries execute again.
            }
            return throwError(() => err);
          }),
        );
      }),
    );
  }
}
