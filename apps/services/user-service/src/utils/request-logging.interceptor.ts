/**
 * Request Logging Interceptor for User Service
 * اعتراض تسجيل الطلبات لخدمة المستخدمين
 *
 * Provides structured JSON logging for all HTTP requests.
 */

import {
  Injectable,
  NestInterceptor,
  ExecutionContext,
  CallHandler,
  Logger,
} from "@nestjs/common";
import { Observable } from "rxjs";
import { tap, catchError } from "rxjs/operators";
import { Request, Response } from "express";
import { randomUUID } from "crypto";

/**
 * Extended Express Request with custom properties
 */
interface ExtendedRequest {
  url: string;
  method: string;
  path: string;
  query: Record<string, any>;
  headers: Record<string, string | string[] | undefined>;
  correlationId?: string;
  tenantId?: string;
  userId?: string;
  user?: {
    sub?: string;
    id?: string;
    tenantId?: string;
    [key: string]: any;
  };
}

/**
 * Request log entry structure
 */
interface LogEntry {
  timestamp: string;
  service: string;
  type: "request" | "response" | "error";
  correlation_id: string;
  http: {
    method: string;
    path: string;
    query?: Record<string, any>;
    status_code?: number;
    duration_ms?: number;
    user_agent?: string;
  };
  tenant_id?: string;
  user_id?: string;
  error?: {
    type: string;
    message: string;
    stack?: string;
  };
  message?: string;
}

/**
 * Request Logging Interceptor
 *
 * Intercepts all HTTP requests and logs them with structured JSON format.
 */
@Injectable()
export class RequestLoggingInterceptor implements NestInterceptor {
  private readonly logger = new Logger(RequestLoggingInterceptor.name);

  // Paths to exclude from logging
  private readonly excludePaths: string[] = [
    "/healthz",
    "/readyz",
    "/livez",
    "/health",
    "/metrics",
    "/docs",
    "/api-docs",
    "/api/v1/healthz",
  ];

  constructor(
    private readonly serviceName: string,
    private readonly logRequestBody: boolean = false,
    private readonly logResponseBody: boolean = false,
  ) {}

  intercept(context: ExecutionContext, next: CallHandler): Observable<any> {
    const ctx = context.switchToHttp();
    const request = ctx.getRequest<ExtendedRequest>();
    const response = ctx.getResponse<Response>();

    // Skip excluded paths
    if (this.shouldExclude(request.url)) {
      return next.handle();
    }

    // Generate or extract correlation ID
    const correlationId = this.getOrCreateCorrelationId(request);

    // Extract tenant and user IDs
    const tenantId = this.extractTenantId(request);
    const userId = this.extractUserId(request);

    // Store in request for downstream use
    request.correlationId = correlationId;
    request.tenantId = tenantId;
    request.userId = userId;

    // Add correlation ID to response headers
    response.setHeader("X-Correlation-ID", correlationId);

    // Record start time
    const startTime = Date.now();

    // Log incoming request
    this.logRequest(request, correlationId, tenantId, userId);

    return next.handle().pipe(
      tap(() => {
        const duration = Date.now() - startTime;
        this.logResponse(
          request,
          response,
          correlationId,
          tenantId,
          userId,
          duration,
        );
      }),
      catchError((error: Error & { status?: number }) => {
        const duration = Date.now() - startTime;
        this.logError(
          request,
          response,
          error,
          correlationId,
          tenantId,
          userId,
          duration,
        );
        throw error;
      }),
    );
  }

  private shouldExclude(path: string): boolean {
    return this.excludePaths.some((excludePath) =>
      path.startsWith(excludePath),
    );
  }

  private getOrCreateCorrelationId(request: ExtendedRequest): string {
    return (
      (request.headers["x-correlation-id"] as string) ||
      (request.headers["x-request-id"] as string) ||
      randomUUID()
    );
  }

  private extractTenantId(request: ExtendedRequest): string | undefined {
    let tenantId = request.headers["x-tenant-id"] as string;
    if (!tenantId && request.user?.tenantId) {
      tenantId = request.user.tenantId;
    }
    return tenantId;
  }

  private extractUserId(request: ExtendedRequest): string | undefined {
    let userId = request.headers["x-user-id"] as string;
    if (!userId && request.user?.sub) {
      userId = request.user.sub;
    }
    if (!userId && request.user?.id) {
      userId = request.user.id;
    }
    return userId;
  }

  /**
   * Redact well-known sensitive keys before emitting a log entry.
   * Keeps operational visibility over unusual traffic while preventing
   * accidental disclosure of secrets passed in the query string.
   */
  private sanitizeQuery(
    query: Record<string, any> | undefined,
  ): Record<string, any> | undefined {
    if (!query || Object.keys(query).length === 0) {
      return undefined;
    }
    const SENSITIVE = new Set([
      "password",
      "pass",
      "pwd",
      "token",
      "access_token",
      "refresh_token",
      "id_token",
      "secret",
      "api_key",
      "apikey",
      "authorization",
      "auth",
      "code",
      "state",
      "otp",
      "session",
      "sid",
    ]);
    // Build sanitized entries, dropping dangerous keys to prevent prototype
    // pollution / remote property injection. See CodeQL
    // js/prototype-polluting-assignment and js/remote-property-injection.
    const entries: [string, any][] = [];
    for (const [k, v] of Object.entries(query)) {
      if (k === "__proto__" || k === "constructor" || k === "prototype") {
        continue;
      }
      entries.push([k, SENSITIVE.has(k.toLowerCase()) ? "[REDACTED]" : v]);
    }
    // Object.fromEntries creates own enumerable properties on a fresh object
    // without ever writing to a computed index expression, which satisfies
    // CodeQL's remote-property-injection check.
    return Object.fromEntries(entries);
  }

  private logRequest(
    request: ExtendedRequest,
    correlationId: string,
    tenantId?: string,
    userId?: string,
  ): void {
    const logEntry: LogEntry = {
      timestamp: new Date().toISOString(),
      service: this.serviceName,
      type: "request",
      correlation_id: correlationId,
      http: {
        method: request.method,
        path: request.path,
        query: this.sanitizeQuery(request.query),
        user_agent: request.headers["user-agent"] as string | undefined,
      },
      tenant_id: tenantId,
      user_id: userId,
      message: `Incoming request: ${request.method} ${request.path}`,
    };

    this.logger.log(JSON.stringify(logEntry));
  }

  private logResponse(
    request: ExtendedRequest,
    response: Response,
    correlationId: string,
    tenantId: string | undefined,
    userId: string | undefined,
    duration: number,
  ): void {
    const statusCode = response.statusCode;

    const logEntry: LogEntry = {
      timestamp: new Date().toISOString(),
      service: this.serviceName,
      type: "response",
      correlation_id: correlationId,
      http: {
        method: request.method,
        path: request.path,
        status_code: statusCode,
        duration_ms: duration,
      },
      tenant_id: tenantId,
      user_id: userId,
      message: `${request.method} ${request.path} ${statusCode} ${duration}ms`,
    };

    if (statusCode >= 500) {
      this.logger.error(JSON.stringify(logEntry));
    } else if (statusCode >= 400) {
      this.logger.warn(JSON.stringify(logEntry));
    } else {
      this.logger.log(JSON.stringify(logEntry));
    }
  }

  private logError(
    request: ExtendedRequest,
    response: Response,
    error: Error & { status?: number },
    correlationId: string,
    tenantId: string | undefined,
    userId: string | undefined,
    duration: number,
  ): void {
    const statusCode = error.status || response.statusCode || 500;

    const logEntry: LogEntry = {
      timestamp: new Date().toISOString(),
      service: this.serviceName,
      type: "error",
      correlation_id: correlationId,
      http: {
        method: request.method,
        path: request.path,
        status_code: statusCode,
        duration_ms: duration,
      },
      tenant_id: tenantId,
      user_id: userId,
      error: {
        type: error.name || "Error",
        message: error.message || "Unknown error",
        stack: error.stack,
      },
      message: `Request failed: ${request.method} ${request.path} - ${error.message}`,
    };

    this.logger.error(JSON.stringify(logEntry));
  }
}
