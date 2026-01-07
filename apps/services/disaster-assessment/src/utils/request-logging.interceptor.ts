/**
 * Request Logging Interceptor for Marketplace Service
 * اعتراض تسجيل الطلبات لخدمة السوق
 *
 * Provides structured JSON logging for all HTTP requests.
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
 * Extended Express Request with custom properties
 */
interface ExtendedRequest extends Request {
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
    '/api/v1/healthz',
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
    response.setHeader('X-Correlation-ID', correlationId);

    // Record start time
    const startTime = Date.now();

    // Log incoming request
    this.logRequest(request, correlationId, tenantId, userId);

    return next.handle().pipe(
      tap(() => {
        const duration = Date.now() - startTime;
        this.logResponse(request, response, correlationId, tenantId, userId, duration);
      }),
      catchError((error) => {
        const duration = Date.now() - startTime;
        this.logError(request, response, error, correlationId, tenantId, userId, duration);
        throw error;
      }),
    );
  }

  private shouldExclude(path: string): boolean {
    return this.excludePaths.some((excludePath) => path.startsWith(excludePath));
  }

  private getOrCreateCorrelationId(request: ExtendedRequest): string {
    return (
      (request.headers['x-correlation-id'] as string) ||
      (request.headers['x-request-id'] as string) ||
      randomUUID()
    );
  }

  private extractTenantId(request: ExtendedRequest): string | undefined {
    let tenantId = request.headers['x-tenant-id'] as string;
    if (!tenantId && request.user?.tenantId) {
      tenantId = request.user.tenantId;
    }
    return tenantId;
  }

  private extractUserId(request: ExtendedRequest): string | undefined {
    let userId = request.headers['x-user-id'] as string;
    if (!userId && request.user?.sub) {
      userId = request.user.sub;
    }
    if (!userId && request.user?.id) {
      userId = request.user.id;
    }
    return userId;
  }

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

    if (statusCode >= 500) {
      this.logger.error(JSON.stringify(logEntry));
    } else if (statusCode >= 400) {
      this.logger.warn(JSON.stringify(logEntry));
    } else {
      this.logger.log(JSON.stringify(logEntry));
    }
  }

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
