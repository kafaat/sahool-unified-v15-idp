/**
 * Tenant Isolation Guard
 * حارس عزل المستأجرين
 *
 * Local implementation of TenantGuard to avoid Docker build dependency
 * on @sahool/nestjs-auth monorepo package.
 *
 * Security: Requires authenticated user for all non-public routes.
 * The X-Tenant-ID header can only override the JWT tenant for admin users.
 */

import {
  Injectable,
  CanActivate,
  ExecutionContext,
  ForbiddenException,
  BadRequestException,
  UnauthorizedException,
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

    // Require authenticated user for all non-public routes
    if (!user) {
      this.logger.warn(
        `Unauthenticated request to tenant-protected route [${request.method} ${request.url}]`,
      );
      throw new UnauthorizedException(
        "Authentication required - المصادقة مطلوبة",
      );
    }

    const userTenantId = user.tenantId;

    // If X-Tenant-ID header is provided, it can only be used as override by admins
    if (headerTenantId && headerTenantId !== userTenantId) {
      const isAdmin = user.roles?.includes("admin");
      if (!isAdmin) {
        this.logger.warn(
          `Tenant mismatch [${request.method} ${request.url}]: user=${userTenantId} requested=${headerTenantId}`,
        );
        throw new ForbiddenException("Access denied: tenant mismatch");
      }
      // Admin can override tenant
      request.tenantId = headerTenantId;
      return true;
    }

    // Use the authenticated user's tenant ID, or header if it matches
    const resolvedTenantId = userTenantId || headerTenantId;

    if (!resolvedTenantId) {
      this.logger.warn(
        `Tenant ID missing for authenticated user [${request.method} ${request.url}]`,
      );
      throw new BadRequestException(
        "Tenant ID is required in JWT token - معرف المستأجر مطلوب في رمز JWT",
      );
    }

    request.tenantId = resolvedTenantId;
    return true;
  }
}
