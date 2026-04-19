/**
 * Tenant Isolation Guard
 * حارس عزل المستأجرين
 *
 * Local implementation to avoid Docker build dependency on @sahool/nestjs-auth.
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

export const SkipTenantCheck = () => SetMetadata(SKIP_TENANT_KEY, true);

@Injectable()
export class TenantGuard implements CanActivate {
  private readonly logger = new Logger(TenantGuard.name);

  constructor(private reflector: Reflector) {}

  canActivate(context: ExecutionContext): boolean {
    const isPublic = this.reflector.getAllAndOverride<boolean>("isPublic", [
      context.getHandler(),
      context.getClass(),
    ]);
    if (isPublic) return true;

    const skipTenant = this.reflector.getAllAndOverride<boolean>(
      SKIP_TENANT_KEY,
      [context.getHandler(), context.getClass()],
    );
    if (skipTenant) return true;

    const request = context.switchToHttp().getRequest();
    const user = request.user;
    const headerTenantId = request.headers["x-tenant-id"];

    const userTenantId = user?.tenantId;
    const isAdmin = user?.roles?.includes("admin");

    // Require a tenant claim on the JWT for any non-admin caller. This closes
    // the gap where an attacker with a valid JWT that lacks `tenant_id` could
    // pass an arbitrary X-Tenant-ID header and have it accepted as authoritative.
    // Admins can still scope queries to a specific tenant via the header.
    if (!userTenantId && !isAdmin) {
      this.logger.warn(
        `JWT missing tenant_id [${request.method} ${request.url}]`,
      );
      throw new ForbiddenException(
        "JWT tenant_id claim is required for non-admin callers",
      );
    }

    const requestedTenantId = userTenantId || headerTenantId;

    if (!requestedTenantId) {
      this.logger.warn(
        `Tenant ID missing [${request.method} ${request.url}]`,
      );
      throw new BadRequestException(
        "Tenant ID is required. Provide via JWT or X-Tenant-ID header.",
      );
    }

    if (headerTenantId && userTenantId && headerTenantId !== userTenantId) {
      if (!isAdmin) {
        this.logger.warn(
          `Tenant mismatch [${request.method} ${request.url}]: user=${userTenantId} requested=${headerTenantId}`,
        );
        throw new ForbiddenException("Access denied: tenant mismatch");
      }
    }

    request.tenantId = requestedTenantId;
    return true;
  }
}
