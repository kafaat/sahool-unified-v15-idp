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
import { IS_PUBLIC_KEY } from "./public.decorator";

export const SKIP_TENANT_KEY = "skipTenantCheck";

export const SkipTenantCheck = () => SetMetadata(SKIP_TENANT_KEY, true);

@Injectable()
export class TenantGuard implements CanActivate {
  private readonly logger = new Logger(TenantGuard.name);

  constructor(private reflector: Reflector) {}

  canActivate(context: ExecutionContext): boolean {
    const isPublic = this.reflector.getAllAndOverride<boolean>(IS_PUBLIC_KEY, [
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
    const requestedTenantId = headerTenantId || userTenantId;

    if (!requestedTenantId) {
      this.logger.warn(
        `Tenant ID missing [${request.method} ${request.url}]`,
      );
      throw new BadRequestException(
        "Tenant ID is required. Provide via JWT or X-Tenant-ID header.",
      );
    }

    const isAdmin = user?.roles?.includes("admin");

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
