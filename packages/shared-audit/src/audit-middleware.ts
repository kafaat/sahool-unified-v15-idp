/**
 * Audit Middleware for Express/NestJS
 * Automatically captures request context and enables audit logging
 */

import { Injectable, NestMiddleware } from '@nestjs/common';
import { Request, Response, NextFunction } from 'express';
import { v4 as uuidv4 } from 'uuid';
import { AuditLogger } from './audit-logger';
import { ActorType, AuditCategory, AuditSeverity } from './audit-types';

/**
 * Audit context stored in request
 */
export interface AuditContext {
  tenantId: string;
  actorId?: string;
  actorType: ActorType;
  correlationId: string;
  sessionId?: string;
  ipAddress?: string;
  userAgent?: string;
}

/**
 * Extended Express Request with audit context
 */
export interface RequestWithAudit extends Request {
  audit?: AuditContext;
}

/**
 * Middleware to inject audit context into requests
 */
@Injectable()
export class AuditMiddleware implements NestMiddleware {
  constructor(private readonly auditLogger?: AuditLogger) {}

  use(req: RequestWithAudit, res: Response, next: NextFunction): void {
    // Extract tenant and actor from headers (adjust based on your auth system)
    const tenantId = req.headers['x-tenant-id'] as string || 'default';
    const actorId = req.headers['x-user-id'] as string;
    const sessionId = req.headers['x-session-id'] as string;

    // Generate or extract correlation ID
    const correlationId =
      (req.headers['x-correlation-id'] as string) ||
      (req.headers['x-request-id'] as string) ||
      uuidv4();

    // Get client IP (handle proxies)
    const ipAddress = this.getClientIp(req);

    // Get user agent
    const userAgent = req.headers['user-agent'];

    // Determine actor type
    const actorType = this.determineActorType(req, actorId);

    // Create audit context
    req.audit = {
      tenantId,
      actorId,
      actorType,
      correlationId,
      sessionId,
      ipAddress,
      userAgent,
    };

    // Add correlation ID to response headers
    res.setHeader('X-Correlation-Id', correlationId);

    // Log request if logger is available
    if (this.auditLogger) {
      this.logRequest(req);
    }

    // Log response on finish
    res.on('finish', () => {
      if (this.auditLogger && req.audit) {
        this.logResponse(req, res);
      }
    });

    next();
  }

  /**
   * Get client IP address, handling proxies
   */
  private getClientIp(req: Request): string | undefined {
    // Check X-Forwarded-For (proxies)
    const forwardedFor = req.headers['x-forwarded-for'];
    if (forwardedFor) {
      const ips = (forwardedFor as string).split(',');
      return ips[0].trim();
    }

    // Check X-Real-IP
    const realIp = req.headers['x-real-ip'];
    if (realIp) {
      return realIp as string;
    }

    // Fall back to socket
    return req.ip || req.socket.remoteAddress;
  }

  /**
   * Determine actor type based on request
   */
  private determineActorType(req: Request, actorId?: string): ActorType {
    // Check for API key
    const apiKey = req.headers['x-api-key'];
    if (apiKey) {
      return ActorType.API_KEY;
    }

    // Check for service-to-service
    const serviceAuth = req.headers['x-service-auth'];
    if (serviceAuth) {
      return ActorType.SERVICE;
    }

    // Check if user is authenticated
    if (actorId) {
      // Check if admin (you can customize this logic)
      const isAdmin = req.headers['x-user-role'] === 'admin';
      return isAdmin ? ActorType.ADMIN : ActorType.USER;
    }

    return ActorType.SYSTEM;
  }

  /**
   * Log incoming request
   */
  private logRequest(req: RequestWithAudit): void {
    if (!req.audit) return;

    // Only log certain methods (avoid logging GET for performance)
    const shouldLog = ['POST', 'PUT', 'PATCH', 'DELETE'].includes(req.method);
    if (!shouldLog) return;

    this.auditLogger?.log({
      tenantId: req.audit.tenantId,
      actorId: req.audit.actorId,
      actorType: req.audit.actorType,
      action: `http.${req.method.toLowerCase()}.request`,
      category: AuditCategory.ACCESS,
      severity: AuditSeverity.DEBUG,
      resourceType: 'endpoint',
      resourceId: req.path,
      correlationId: req.audit.correlationId,
      sessionId: req.audit.sessionId,
      ipAddress: req.audit.ipAddress,
      userAgent: req.audit.userAgent,
      metadata: {
        method: req.method,
        path: req.path,
        query: req.query,
      },
      success: true,
    });
  }

  /**
   * Log response
   */
  private logResponse(req: RequestWithAudit, res: Response): void {
    if (!req.audit) return;

    // Only log certain methods
    const shouldLog = ['POST', 'PUT', 'PATCH', 'DELETE'].includes(req.method);
    if (!shouldLog) return;

    const success = res.statusCode >= 200 && res.statusCode < 400;
    const severity = success ? AuditSeverity.DEBUG : AuditSeverity.WARNING;

    this.auditLogger?.log({
      tenantId: req.audit.tenantId,
      actorId: req.audit.actorId,
      actorType: req.audit.actorType,
      action: `http.${req.method.toLowerCase()}.response`,
      category: AuditCategory.ACCESS,
      severity,
      resourceType: 'endpoint',
      resourceId: req.path,
      correlationId: req.audit.correlationId,
      sessionId: req.audit.sessionId,
      ipAddress: req.audit.ipAddress,
      userAgent: req.audit.userAgent,
      metadata: {
        method: req.method,
        path: req.path,
        statusCode: res.statusCode,
      },
      success,
      errorCode: success ? undefined : `HTTP_${res.statusCode}`,
    });
  }
}

/**
 * Helper to get audit context from request
 */
export function getAuditContext(req: RequestWithAudit): AuditContext | undefined {
  return req.audit;
}

/**
 * NestJS Guard to ensure audit context exists
 */
@Injectable()
export class AuditGuard {
  canActivate(context: any): boolean {
    const request = context.switchToHttp().getRequest() as RequestWithAudit;
    return !!request.audit;
  }
}

/**
 * Decorator to extract audit context in NestJS controllers
 */
import { createParamDecorator, ExecutionContext } from '@nestjs/common';

export const Audit = createParamDecorator(
  (data: unknown, ctx: ExecutionContext): AuditContext | undefined => {
    const request = ctx.switchToHttp().getRequest() as RequestWithAudit;
    return request.audit;
  },
);

/**
 * Decorator to extract tenant ID from audit context
 */
export const TenantId = createParamDecorator(
  (data: unknown, ctx: ExecutionContext): string | undefined => {
    const request = ctx.switchToHttp().getRequest() as RequestWithAudit;
    return request.audit?.tenantId;
  },
);

/**
 * Decorator to extract actor ID from audit context
 */
export const ActorId = createParamDecorator(
  (data: unknown, ctx: ExecutionContext): string | undefined => {
    const request = ctx.switchToHttp().getRequest() as RequestWithAudit;
    return request.audit?.actorId;
  },
);

/**
 * Decorator to extract correlation ID from audit context
 */
export const CorrelationId = createParamDecorator(
  (data: unknown, ctx: ExecutionContext): string | undefined => {
    const request = ctx.switchToHttp().getRequest() as RequestWithAudit;
    return request.audit?.correlationId;
  },
);
