/**
 * Custom Decorators for NestJS Authentication
 * Useful decorators for SAHOOL platform authentication and authorization
 */

import { createParamDecorator, ExecutionContext, SetMetadata } from '@nestjs/common';

/**
 * Public route decorator
 *
 * Mark routes that don't require authentication
 *
 * @example
 * ```typescript
 * @Controller('auth')
 * export class AuthController {
 *   @Public()
 *   @Post('login')
 *   login(@Body() credentials: LoginDto) {
 *     return this.authService.login(credentials);
 *   }
 * }
 * ```
 */
export const Public = () => SetMetadata('isPublic', true);

/**
 * Roles decorator
 *
 * Specify required roles for a route
 * User must have at least one of the specified roles
 *
 * @param roles - One or more role names
 *
 * @example
 * ```typescript
 * @Controller('admin')
 * export class AdminController {
 *   @Roles('admin', 'manager')
 *   @Get('users')
 *   getAllUsers() {
 *     return this.userService.findAll();
 *   }
 * }
 * ```
 */
export const Roles = (...roles: string[]) => SetMetadata('roles', roles);

/**
 * Require Permissions decorator
 *
 * Specify required permissions for a route
 * User must have at least one of the specified permissions
 *
 * @param permissions - One or more permission names
 *
 * @example
 * ```typescript
 * @Controller('farms')
 * export class FarmsController {
 *   @RequirePermissions('farm:write', 'farm:delete')
 *   @Delete(':id')
 *   deleteFarm(@Param('id') id: string) {
 *     return this.farmsService.delete(id);
 *   }
 * }
 * ```
 */
export const RequirePermissions = (...permissions: string[]) =>
  SetMetadata('permissions', permissions);

/**
 * Current User decorator
 *
 * Extract the current authenticated user from the request
 *
 * @example
 * ```typescript
 * @Controller('profile')
 * export class ProfileController {
 *   @Get()
 *   getProfile(@CurrentUser() user: AuthenticatedUser) {
 *     return this.profileService.getProfile(user.id);
 *   }
 *
 *   // Get specific property
 *   @Get('email')
 *   getEmail(@CurrentUser('email') email: string) {
 *     return { email };
 *   }
 * }
 * ```
 */
export const CurrentUser = createParamDecorator(
  (data: string | undefined, ctx: ExecutionContext) => {
    const request = ctx.switchToHttp().getRequest();
    const user = request.user;

    return data ? user?.[data] : user;
  },
);

/**
 * User ID decorator
 *
 * Extract the user ID from the authenticated user
 *
 * @example
 * ```typescript
 * @Controller('farms')
 * export class FarmsController {
 *   @Get()
 *   getUserFarms(@UserId() userId: string) {
 *     return this.farmsService.findByUser(userId);
 *   }
 * }
 * ```
 */
export const UserId = createParamDecorator(
  (data: unknown, ctx: ExecutionContext): string => {
    const request = ctx.switchToHttp().getRequest();
    return request.user?.id;
  },
);

/**
 * User Roles decorator
 *
 * Extract the roles from the authenticated user
 *
 * @example
 * ```typescript
 * @Controller('dashboard')
 * export class DashboardController {
 *   @Get()
 *   getDashboard(@UserRoles() roles: string[]) {
 *     if (roles.includes('admin')) {
 *       return this.dashboardService.getAdminDashboard();
 *     }
 *     return this.dashboardService.getUserDashboard();
 *   }
 * }
 * ```
 */
export const UserRoles = createParamDecorator(
  (data: unknown, ctx: ExecutionContext): string[] => {
    const request = ctx.switchToHttp().getRequest();
    return request.user?.roles || [];
  },
);

/**
 * Tenant ID decorator
 *
 * Extract the tenant ID from the authenticated user
 *
 * @example
 * ```typescript
 * @Controller('data')
 * export class DataController {
 *   @Get()
 *   getData(@TenantId() tenantId: string) {
 *     return this.dataService.findByTenant(tenantId);
 *   }
 * }
 * ```
 */
export const TenantId = createParamDecorator(
  (data: unknown, ctx: ExecutionContext): string | undefined => {
    const request = ctx.switchToHttp().getRequest();
    return request.user?.tenantId || request.headers['x-tenant-id'];
  },
);

/**
 * User Permissions decorator
 *
 * Extract the permissions from the authenticated user
 *
 * @example
 * ```typescript
 * @Controller('features')
 * export class FeaturesController {
 *   @Get()
 *   getAvailableFeatures(@UserPermissions() permissions: string[]) {
 *     return this.featuresService.getEnabledFeatures(permissions);
 *   }
 * }
 * ```
 */
export const UserPermissions = createParamDecorator(
  (data: unknown, ctx: ExecutionContext): string[] => {
    const request = ctx.switchToHttp().getRequest();
    return request.user?.permissions || [];
  },
);

/**
 * Auth Token decorator
 *
 * Extract the raw JWT token from the Authorization header
 *
 * @example
 * ```typescript
 * @Controller('auth')
 * export class AuthController {
 *   @Post('refresh')
 *   refreshToken(@AuthToken() token: string) {
 *     return this.authService.refreshToken(token);
 *   }
 * }
 * ```
 */
export const AuthToken = createParamDecorator(
  (data: unknown, ctx: ExecutionContext): string | undefined => {
    const request = ctx.switchToHttp().getRequest();
    const authorization = request.headers.authorization;

    if (!authorization) {
      return undefined;
    }

    const [scheme, token] = authorization.split(' ');

    if (scheme.toLowerCase() !== 'bearer') {
      return undefined;
    }

    return token;
  },
);

/**
 * Request Language decorator
 *
 * Extract the language preference from Accept-Language header or query parameter
 *
 * @example
 * ```typescript
 * @Controller('content')
 * export class ContentController {
 *   @Get()
 *   getContent(@RequestLanguage() lang: string) {
 *     return this.contentService.getContent(lang);
 *   }
 * }
 * ```
 */
export const RequestLanguage = createParamDecorator(
  (data: unknown, ctx: ExecutionContext): string => {
    const request = ctx.switchToHttp().getRequest();

    // Check query parameter first
    const queryLang = request.query?.lang || request.query?.language;
    if (queryLang) {
      return queryLang;
    }

    // Check Accept-Language header
    const acceptLanguage = request.headers['accept-language'];
    if (acceptLanguage) {
      // Extract first language from Accept-Language header
      const lang = acceptLanguage.split(',')[0].split('-')[0];
      return lang;
    }

    // Default to English
    return 'en';
  },
);

/**
 * Has Role decorator (for use in guards/validators)
 *
 * Check if user has a specific role
 *
 * @example
 * ```typescript
 * import { hasRole } from '@shared/auth/decorators';
 *
 * if (hasRole(user, 'admin')) {
 *   // User is admin
 * }
 * ```
 */
export const hasRole = (user: any, role: string): boolean => {
  return user?.roles?.includes(role) || false;
};

/**
 * Has Any Role decorator (for use in guards/validators)
 *
 * Check if user has any of the specified roles
 *
 * @example
 * ```typescript
 * import { hasAnyRole } from '@shared/auth/decorators';
 *
 * if (hasAnyRole(user, ['admin', 'manager'])) {
 *   // User is admin or manager
 * }
 * ```
 */
export const hasAnyRole = (user: any, roles: string[]): boolean => {
  return roles.some((role) => user?.roles?.includes(role)) || false;
};

/**
 * Has Permission decorator (for use in guards/validators)
 *
 * Check if user has a specific permission
 *
 * @example
 * ```typescript
 * import { hasPermission } from '@shared/auth/decorators';
 *
 * if (hasPermission(user, 'farm:delete')) {
 *   // User can delete farms
 * }
 * ```
 */
export const hasPermission = (user: any, permission: string): boolean => {
  return user?.permissions?.includes(permission) || false;
};

/**
 * Has Any Permission decorator (for use in guards/validators)
 *
 * Check if user has any of the specified permissions
 *
 * @example
 * ```typescript
 * import { hasAnyPermission } from '@shared/auth/decorators';
 *
 * if (hasAnyPermission(user, ['farm:read', 'farm:write'])) {
 *   // User can read or write farms
 * }
 * ```
 */
export const hasAnyPermission = (user: any, permissions: string[]): boolean => {
  return permissions.some((perm) => user?.permissions?.includes(perm)) || false;
};
