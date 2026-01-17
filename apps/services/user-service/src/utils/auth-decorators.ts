/**
 * Custom Decorators for NestJS Authentication
 * Useful decorators for SAHOOL platform authentication and authorization
 */

import {
  createParamDecorator,
  ExecutionContext,
  SetMetadata,
} from "@nestjs/common";

/**
 * Public route decorator - mark routes that don't require authentication
 */
export const Public = () => SetMetadata("isPublic", true);

/**
 * Roles decorator - specify required roles for a route
 */
export const Roles = (...roles: string[]) => SetMetadata("roles", roles);

/**
 * Require Permissions decorator
 */
export const RequirePermissions = (...permissions: string[]) =>
  SetMetadata("permissions", permissions);

/**
 * Current User decorator - extract the current authenticated user from the request
 */
export const CurrentUser = createParamDecorator(
  (data: string | undefined, ctx: ExecutionContext) => {
    const request = ctx.switchToHttp().getRequest();
    const user = request.user;

    return data ? user?.[data] : user;
  },
);

/**
 * User ID decorator - extract the user ID from the authenticated user
 */
export const UserId = createParamDecorator(
  (data: unknown, ctx: ExecutionContext): string => {
    const request = ctx.switchToHttp().getRequest();
    return request.user?.id;
  },
);

/**
 * User Roles decorator - extract the roles from the authenticated user
 */
export const UserRoles = createParamDecorator(
  (data: unknown, ctx: ExecutionContext): string[] => {
    const request = ctx.switchToHttp().getRequest();
    return request.user?.roles || [];
  },
);

/**
 * Tenant ID decorator - extract the tenant ID from the authenticated user
 */
export const TenantId = createParamDecorator(
  (data: unknown, ctx: ExecutionContext): string | undefined => {
    const request = ctx.switchToHttp().getRequest();
    return request.user?.tenantId || request.headers["x-tenant-id"];
  },
);

/**
 * User Permissions decorator
 */
export const UserPermissions = createParamDecorator(
  (data: unknown, ctx: ExecutionContext): string[] => {
    const request = ctx.switchToHttp().getRequest();
    return request.user?.permissions || [];
  },
);

/**
 * Auth Token decorator - extract the raw JWT token from the Authorization header
 */
export const AuthToken = createParamDecorator(
  (data: unknown, ctx: ExecutionContext): string | undefined => {
    const request = ctx.switchToHttp().getRequest();
    const authorization = request.headers.authorization;

    if (!authorization) {
      return undefined;
    }

    const [scheme, token] = authorization.split(" ");

    if (scheme.toLowerCase() !== "bearer") {
      return undefined;
    }

    return token;
  },
);

/**
 * Request Language decorator
 */
export const RequestLanguage = createParamDecorator(
  (data: unknown, ctx: ExecutionContext): string => {
    const request = ctx.switchToHttp().getRequest();

    const queryLang = request.query?.lang || request.query?.language;
    if (queryLang) {
      return queryLang;
    }

    const acceptLanguage = request.headers["accept-language"];
    if (acceptLanguage) {
      const lang = acceptLanguage.split(",")[0].split("-")[0];
      return lang;
    }

    return "en";
  },
);

/**
 * Helper functions for role/permission checking
 */
export const hasRole = (user: any, role: string): boolean => {
  return user?.roles?.includes(role) || false;
};

export const hasAnyRole = (user: any, roles: string[]): boolean => {
  return roles.some((role) => user?.roles?.includes(role)) || false;
};

export const hasPermission = (user: any, permission: string): boolean => {
  return user?.permissions?.includes(permission) || false;
};

export const hasAnyPermission = (user: any, permissions: string[]): boolean => {
  return permissions.some((perm) => user?.permissions?.includes(perm)) || false;
};
