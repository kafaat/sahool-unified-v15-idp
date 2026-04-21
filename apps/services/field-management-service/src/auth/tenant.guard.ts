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
    // Normalize header: some proxies duplicate headers producing `string[]`.
    // Take the first non-empty value so the comparison below never does a
    // reference-equality check against an array and accidentally passes.
    const rawHeader = request.headers["x-tenant-id"];
    const headerTenantId = Array.isArray(rawHeader) ? rawHeader[0] : rawHeader;

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

    // If X-Tenant-ID header is provided, it can only be used as override by admins.
    // Role match is case-insensitive and covers the canonical Prisma enum values
    // (`ADMIN`, `SUPER_ADMIN`) as well as lower-case legacy spellings. Platform
    // JWTs mint uppercase roles (see user-service UserRole enum), so the previous
    // lowercase-only check `includes("admin")` silently forbade every real admin
    // override in production while accidentally passing in test fixtures.
    if (headerTenantId && headerTenantId !== userTenantId) {
      const roles: string[] = Array.isArray(user.roles) ? user.roles : [];
      const normalizedRoles = roles
        .filter((r): r is string => typeof r === "string")
        .map((r) => r.toUpperCase());
      const isAdmin =
        normalizedRoles.includes("ADMIN") ||
        normalizedRoles.includes("SUPER_ADMIN");
      if (!isAdmin) {
        this.logger.warn(
          `Tenant mismatch [${request.method} ${request.url}]: user=${userTenantId} requested=${headerTenantId}`,
        );
        throw new ForbiddenException("Access denied: tenant mismatch");
      }
      // Admin can override tenant. Emit a structured audit line so the
      // privileged cross-tenant access is visible in log aggregation / SIEM.
      // An admin impersonating a tenant is a sensitive operation and must
      // never happen silently. The downstream audit-service can correlate
      // on `admin_tenant_override` to build a compliance trail even if the
      // individual handler forgets to emit its own event.
      this.logger.warn(
        `admin_tenant_override: userId=${user.id ?? "unknown"} fromTenant=${userTenantId ?? "none"} toTenant=${headerTenantId} method=${request.method} url=${request.url}`,
      );
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
