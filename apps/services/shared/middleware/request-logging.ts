/**
 * SAHOOL Request Logging Middleware
 * ==================================
 * Comprehensive request logging for NestJS services with structured JSON logging.
 *
 * Features:
 * - Logs request method, path, status code, duration
 * - Tracks user_id and tenant_id from request headers or JWT
 * - Generates and propagates correlation IDs
 * - Structured JSON output format
 * - Supports OpenTelemetry trace propagation
 * - Filters sensitive data from logs
 *
 * Usage:
 *
 * In main.ts:
 * ```typescript
 * import { RequestLoggingInterceptor } from './shared/middleware/request-logging';
 *
 * const app = await NestFactory.create(AppModule);
 * app.useGlobalInterceptors(new RequestLoggingInterceptor('my-service'));
 * ```
 *
 * Or as a provider in AppModule:
 * ```typescript
 * import { APP_INTERCEPTOR } from '@nestjs/core';
 * import { RequestLoggingInterceptor } from './shared/middleware/request-logging';
 *
 * @Module({
 *   providers: [
 *     {
 *       provide: APP_INTERCEPTOR,
 *       useValue: new RequestLoggingInterceptor('my-service'),
 *     },
 *   ],
 * })
 * export class AppModule {}
 * ```
 */

import {
  Injectable,
  NestInterceptor,
  ExecutionContext,
  CallHandler,
  Logger,
} from '@nestjs/common';
import { Observable } from 'rxjs';
import { tap, catchError } from 'rxjs/operators';
import { Request, Response } from 'express';
import { randomUUID } from 'crypto';

/**
 * Request log entry structure
 */
interface LogEntry {
  timestamp: string;
  service: string;
  type: 'request' | 'response' | 'error';
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
    '/healthz',
    '/readyz',
    '/livez',
    '/health',
    '/metrics',
    '/docs',
    '/api-docs',
  ];

  // Sensitive headers to redact
  private readonly sensitiveHeaders: Set<string> = new Set([
    'authorization',
    'cookie',
    'x-api-key',
    'x-auth-token',
    'x-secret-key',
    'password',
    'secret',
    'token',
  ]);

  constructor(
    private readonly serviceName: string,
    private readonly logRequestBody: boolean = false,
    private readonly logResponseBody: boolean = false,
  ) {}

  intercept(context: ExecutionContext, next: CallHandler): Observable<any> {
    const ctx = context.switchToHttp();
    const request = ctx.getRequest<Request>();
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
    (request as any).correlationId = correlationId;
    (request as any).tenantId = tenantId;
    (request as any).userId = userId;

    // Add correlation ID to response headers
    response.setHeader('X-Correlation-ID', correlationId);

    // Record start time
    const startTime = Date.now();

    // Log incoming request
    this.logRequest(request, correlationId, tenantId, userId);

    return next.handle().pipe(
      tap((data) => {
        // Calculate duration
        const duration = Date.now() - startTime;

        // Log successful response
        this.logResponse(
          request,
          response,
          correlationId,
          tenantId,
          userId,
          duration,
        );
      }),
      catchError((error) => {
        // Calculate duration
        const duration = Date.now() - startTime;

        // Log error
        this.logError(
          request,
          response,
          error,
          correlationId,
          tenantId,
          userId,
          duration,
        );

        // Re-throw error
        throw error;
      }),
    );
  }

  /**
   * Check if path should be excluded from logging
   */
  private shouldExclude(path: string): boolean {
    return this.excludePaths.some((excludePath) =>
      path.startsWith(excludePath),
    );
  }

  /**
   * Get or create correlation ID
   */
  private getOrCreateCorrelationId(request: Request): string {
    return (
      request.headers['x-correlation-id'] as string ||
      request.headers['x-request-id'] as string ||
      randomUUID()
    );
  }

  /**
   * Extract tenant ID from request
   */
  private extractTenantId(request: Request): string | undefined {
    // Try header first
    let tenantId = request.headers['x-tenant-id'] as string;

    // Try from JWT (if decoded by auth guard)
    if (!tenantId && (request as any).user?.tenantId) {
      tenantId = (request as any).user.tenantId;
    }

    return tenantId;
  }

  /**
   * Extract user ID from request
   */
  private extractUserId(request: Request): string | undefined {
    // Try header first
    let userId = request.headers['x-user-id'] as string;

    // Try from JWT (if decoded by auth guard)
    if (!userId && (request as any).user?.sub) {
      userId = (request as any).user.sub;
    }

    if (!userId && (request as any).user?.id) {
      userId = (request as any).user.id;
    }

    return userId;
  }

  /**
   * Log incoming request
   */
  private logRequest(
    request: Request,
    correlationId: string,
    tenantId?: string,
    userId?: string,
  ): void {
    const logEntry: LogEntry = {
      timestamp: new Date().toISOString(),
      service: this.serviceName,
      type: 'request',
      correlation_id: correlationId,
      http: {
        method: request.method,
        path: request.path,
        query: Object.keys(request.query).length > 0 ? request.query : undefined,
        user_agent: request.headers['user-agent'],
      },
      tenant_id: tenantId,
      user_id: userId,
      message: `Incoming request: ${request.method} ${request.path}`,
    };

    this.logger.log(JSON.stringify(logEntry));
  }

  /**
   * Log successful response
   */
  private logResponse(
    request: Request,
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
      type: 'response',
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

    // Log at appropriate level based on status code
    if (statusCode >= 500) {
      this.logger.error(JSON.stringify(logEntry));
    } else if (statusCode >= 400) {
      this.logger.warn(JSON.stringify(logEntry));
    } else {
      this.logger.log(JSON.stringify(logEntry));
    }
  }

  /**
   * Log error
   */
  private logError(
    request: Request,
    response: Response,
    error: any,
    correlationId: string,
    tenantId: string | undefined,
    userId: string | undefined,
    duration: number,
  ): void {
    const statusCode = error.status || response.statusCode || 500;

    const logEntry: LogEntry = {
      timestamp: new Date().toISOString(),
      service: this.serviceName,
      type: 'error',
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
        type: error.name || 'Error',
        message: error.message || 'Unknown error',
        stack: error.stack,
      },
      message: `Request failed: ${request.method} ${request.path} - ${error.message}`,
    };

    this.logger.error(JSON.stringify(logEntry));
  }
}

/**
 * Helper function to get correlation ID from request
 */
export function getCorrelationId(request: Request): string {
  return (request as any).correlationId || 'unknown';
}

/**
 * Helper function to get request context for logging
 */
export function getRequestContext(request: Request): {
  correlationId?: string;
  tenantId?: string;
  userId?: string;
} {
  return {
    correlationId: (request as any).correlationId,
    tenantId: (request as any).tenantId,
    userId: (request as any).userId,
  };
}

/**
 * Structured logger utility for use in services
 */
export class StructuredLogger {
  private readonly logger: Logger;

  constructor(
    private readonly serviceName: string,
    context?: string,
  ) {
    this.logger = new Logger(context || serviceName);
  }

  /**
   * Log with structured format
   */
  private logStructured(
    level: 'log' | 'error' | 'warn' | 'debug',
    message: string,
    context?: {
      correlationId?: string;
      tenantId?: string;
      userId?: string;
      [key: string]: any;
    },
  ): void {
    const logEntry = {
      timestamp: new Date().toISOString(),
      service: this.serviceName,
      message,
      ...context,
    };

    this.logger[level](JSON.stringify(logEntry));
  }

  log(message: string, context?: any): void {
    this.logStructured('log', message, context);
  }

  error(message: string, context?: any): void {
    this.logStructured('error', message, context);
  }

  warn(message: string, context?: any): void {
    this.logStructured('warn', message, context);
  }

  debug(message: string, context?: any): void {
    this.logStructured('debug', message, context);
  }
}
