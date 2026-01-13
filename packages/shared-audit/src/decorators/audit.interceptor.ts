/**
 * Audit Interceptor
 * Automatically logs audit events for methods decorated with @Auditable
 */

import {
  Injectable,
  NestInterceptor,
  ExecutionContext,
  CallHandler,
  Logger,
} from "@nestjs/common";
import { Reflector } from "@nestjs/core";
import { Observable } from "rxjs";
import { tap, catchError } from "rxjs/operators";
import { AuditLogger } from "../audit-logger";
import {
  AUDIT_METADATA,
  AuditableOptions,
  AuditSeverity,
} from "../audit-types";
import { RequestWithAudit } from "../audit-middleware";
import { getAuditFieldMetadata } from "./audit-field.decorator";

/**
 * Interceptor that handles @Auditable decorator
 */
@Injectable()
export class AuditInterceptor implements NestInterceptor {
  private readonly logger = new Logger(AuditInterceptor.name);

  constructor(
    private readonly reflector: Reflector,
    private readonly auditLogger: AuditLogger,
  ) {}

  intercept(context: ExecutionContext, next: CallHandler): Observable<any> {
    // Get metadata from @Auditable decorator
    const options = this.reflector.get<AuditableOptions>(
      AUDIT_METADATA.AUDITABLE,
      context.getHandler(),
    );

    // If not auditable, pass through
    if (!options) {
      return next.handle();
    }

    // Get request
    const request = context.switchToHttp().getRequest<RequestWithAudit>();
    const auditContext = request.audit;

    if (!auditContext) {
      this.logger.warn("Audit context not found in request");
      return next.handle();
    }

    // Extract resource info from request
    const resourceId = this.extractResourceId(request);
    const resourceType =
      options.resourceType || this.extractResourceType(context);

    // Capture old value if tracking changes
    let oldValue: Record<string, unknown> | undefined;
    if (options.trackChanges) {
      oldValue = this.extractOldValue(request);
    }

    // Execute the handler
    const startTime = Date.now();

    return next.handle().pipe(
      tap(async (result) => {
        const duration = Date.now() - startTime;

        // Capture new value if tracking changes
        let newValue: Record<string, unknown> | undefined;
        if (options.trackChanges) {
          newValue = this.extractNewValue(result);
        }

        // Log audit event
        try {
          if (options.trackChanges && oldValue && newValue) {
            await this.auditLogger.logWithChanges(
              {
                tenantId: auditContext.tenantId,
                actorId: auditContext.actorId,
                actorType: auditContext.actorType,
                action: options.action || "unknown",
                category: options.category,
                severity: options.severity,
                resourceType,
                resourceId,
                correlationId: auditContext.correlationId,
                sessionId: auditContext.sessionId,
                ipAddress: auditContext.ipAddress,
                userAgent: auditContext.userAgent,
                metadata: {
                  duration,
                  controller: context.getClass().name,
                  handler: context.getHandler().name,
                },
                success: true,
              },
              oldValue,
              newValue,
              {
                trackChanges: true,
                generateDiff: true,
                excludeFields: options.excludeFields,
                redactFields: options.redactFields,
              },
            );
          } else {
            await this.auditLogger.log(
              {
                tenantId: auditContext.tenantId,
                actorId: auditContext.actorId,
                actorType: auditContext.actorType,
                action: options.action || "unknown",
                category: options.category,
                severity: options.severity,
                resourceType,
                resourceId,
                correlationId: auditContext.correlationId,
                sessionId: auditContext.sessionId,
                ipAddress: auditContext.ipAddress,
                userAgent: auditContext.userAgent,
                metadata: {
                  duration,
                  controller: context.getClass().name,
                  handler: context.getHandler().name,
                },
                success: true,
              },
              {
                excludeFields: options.excludeFields,
                redactFields: options.redactFields,
              },
            );
          }
        } catch (error) {
          this.logger.error("Failed to log audit event", error);
        }
      }),
      catchError(async (error) => {
        const duration = Date.now() - startTime;

        // Log failure
        try {
          await this.auditLogger.log({
            tenantId: auditContext.tenantId,
            actorId: auditContext.actorId,
            actorType: auditContext.actorType,
            action: options.action || "unknown",
            category: options.category,
            severity: AuditSeverity.ERROR,
            resourceType,
            resourceId,
            correlationId: auditContext.correlationId,
            sessionId: auditContext.sessionId,
            ipAddress: auditContext.ipAddress,
            userAgent: auditContext.userAgent,
            metadata: {
              duration,
              controller: context.getClass().name,
              handler: context.getHandler().name,
            },
            success: false,
            errorCode: error.name || "UnknownError",
            errorMessage: error.message,
          });
        } catch (auditError) {
          this.logger.error("Failed to log audit event", auditError);
        }

        // Re-throw the original error
        throw error;
      }),
    );
  }

  /**
   * Extract resource ID from request
   */
  private extractResourceId(request: RequestWithAudit): string {
    // Try to get from path params
    if (request.params?.id) {
      return request.params.id;
    }

    // Try to get from query
    if (request.query?.id) {
      return request.query.id as string;
    }

    // Try to get from body
    if (request.body?.id) {
      return request.body.id;
    }

    // Fall back to path
    return request.path;
  }

  /**
   * Extract resource type from context
   */
  private extractResourceType(context: ExecutionContext): string {
    const className = context.getClass().name;

    // Remove 'Controller' suffix if present
    return className.replace(/Controller$/i, "").toLowerCase();
  }

  /**
   * Extract old value from request (for updates)
   */
  private extractOldValue(
    request: RequestWithAudit,
  ): Record<string, unknown> | undefined {
    // This is a placeholder - in real implementation, you might:
    // 1. Fetch from database using resource ID
    // 2. Get from request metadata
    // 3. Use a service to retrieve current state

    // For now, return undefined (can be enhanced)
    return undefined;
  }

  /**
   * Extract new value from result
   */
  private extractNewValue(result: any): Record<string, unknown> | undefined {
    if (!result) return undefined;

    // If result is an object, use it
    if (typeof result === "object" && !Array.isArray(result)) {
      return result as Record<string, unknown>;
    }

    return undefined;
  }
}
