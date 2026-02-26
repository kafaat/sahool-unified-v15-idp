/**
 * Tenant Isolation Guard for NestJS
 * Enforces multi-tenant data isolation across SAHOOL platform services
 *
 * Usage:
 *   @UseGuards(JwtAuthGuard, TenantGuard)
 *   @Controller('resources')
 *   export class ResourcesController { ... }
 */

import {
  Injectable,
  CanActivate,
  ExecutionContext,
  ForbiddenException,
  BadRequestException,
  Logger,
  SetMetadata,
} from "@nestjs/common";
import { Reflector } from "@nestjs/core";

const SKIP_TENANT_KEY = "skipTenantCheck";

/**
 * Decorator to skip tenant validation on specific routes
 * (e.g., admin endpoints that query across tenants)
 */
export const SkipTenantCheck = () => SetMetadata(SKIP_TENANT_KEY, true);

/**
 * TenantGuard - Enforces tenant isolation on every request.
 *
 * Extracts tenant_id from JWT (user.tenantId) or X-Tenant-ID header,
 * validates the user has access to the tenant, and attaches tenantId
 * to the request for downstream use.
 *
 * Admin users can access any tenant via X-Tenant-ID header.
 * Non-admin users are restricted to their own tenant.
 */
@Injectable()
export class TenantGuard implements CanActivate {
  private readonly logger = new Logger(TenantGuard.name);

  constructor(private reflector: Reflector) {}

  canActivate(context: ExecutionContext): boolean {
    // Check if route is public (skip tenant check)
    const isPublic = this.reflector.getAllAndOverride<boolean>("isPublic", [
      context.getHandler(),
      context.getClass(),
    ]);
    if (isPublic) return true;

    // Check if tenant check is explicitly skipped
    const skipTenant = this.reflector.getAllAndOverride<boolean>(
      SKIP_TENANT_KEY,
      [context.getHandler(), context.getClass()],
    );
    if (skipTenant) return true;

    const request = context.switchToHttp().getRequest();
    const user = request.user;
    const headerTenantId = request.headers["x-tenant-id"];

    // Get tenant from JWT user or header
    const userTenantId = user?.tenantId;
    const requestedTenantId = headerTenantId || userTenantId;

    if (!requestedTenantId) {
      this.logger.warn(
        `Tenant ID missing [${request.method} ${request.url}]`,
      );
      throw new BadRequestException(
        "Tenant ID is required. Provide via JWT or X-Tenant-ID header.",
      );
    }

    // Admin users can access any tenant
    const isAdmin = user?.roles?.includes("admin");

    if (headerTenantId && userTenantId && headerTenantId !== userTenantId) {
      if (!isAdmin) {
        this.logger.warn(
          `Tenant mismatch [${request.method} ${request.url}]: user=${userTenantId} requested=${headerTenantId}`,
        );
        throw new ForbiddenException("Access denied: tenant mismatch");
      }
    }

    // Attach validated tenantId to request for downstream services
    request.tenantId = requestedTenantId;

    this.logger.debug(
      `Tenant validated [${request.method} ${request.url}]: tenantId=${requestedTenantId}`,
    );

    return true;
  }
}
