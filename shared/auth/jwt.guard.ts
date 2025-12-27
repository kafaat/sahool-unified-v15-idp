/**
 * JWT Guards for NestJS
 * Authentication and authorization guards for SAHOOL platform
 */

import {
  Injectable,
  CanActivate,
  ExecutionContext,
  UnauthorizedException,
  ForbiddenException,
} from '@nestjs/common';
import { Reflector } from '@nestjs/core';
import { AuthGuard } from '@nestjs/passport';
import { Observable } from 'rxjs';
import { AuthErrors } from './config';

/**
 * JWT Authentication Guard
 *
 * Extends the default Passport JWT guard with custom error messages
 *
 * @example
 * ```typescript
 * @Controller('farms')
 * @UseGuards(JwtAuthGuard)
 * export class FarmsController {
 *   @Get()
 *   findAll() {
 *     return this.farmsService.findAll();
 *   }
 * }
 * ```
 */
@Injectable()
export class JwtAuthGuard extends AuthGuard('jwt') {
  constructor(private reflector: Reflector) {
    super();
  }

  /**
   * Handle authentication request
   */
  canActivate(
    context: ExecutionContext,
  ): boolean | Promise<boolean> | Observable<boolean> {
    // Check if route is marked as public
    const isPublic = this.reflector.getAllAndOverride<boolean>('isPublic', [
      context.getHandler(),
      context.getClass(),
    ]);

    if (isPublic) {
      return true;
    }

    return super.canActivate(context);
  }

  /**
   * Handle authentication errors
   */
  handleRequest(err: any, user: any, info: any) {
    if (err || !user) {
      if (info?.name === 'TokenExpiredError') {
        throw new UnauthorizedException(AuthErrors.EXPIRED_TOKEN.en);
      }

      if (info?.name === 'JsonWebTokenError') {
        throw new UnauthorizedException(AuthErrors.INVALID_TOKEN.en);
      }

      throw err || new UnauthorizedException(AuthErrors.MISSING_TOKEN.en);
    }

    return user;
  }
}

/**
 * Roles Guard
 *
 * Checks if the authenticated user has the required roles
 *
 * @example
 * ```typescript
 * @Controller('admin')
 * @UseGuards(JwtAuthGuard, RolesGuard)
 * export class AdminController {
 *   @Get('settings')
 *   @Roles('admin', 'manager')
 *   getSettings() {
 *     return this.adminService.getSettings();
 *   }
 * }
 * ```
 */
@Injectable()
export class RolesGuard implements CanActivate {
  constructor(private reflector: Reflector) {}

  canActivate(context: ExecutionContext): boolean {
    const requiredRoles = this.reflector.getAllAndOverride<string[]>('roles', [
      context.getHandler(),
      context.getClass(),
    ]);

    if (!requiredRoles || requiredRoles.length === 0) {
      return true;
    }

    const request = context.switchToHttp().getRequest();
    const user = request.user;

    if (!user || !user.roles) {
      throw new ForbiddenException(AuthErrors.INSUFFICIENT_PERMISSIONS.en);
    }

    const hasRole = requiredRoles.some((role) => user.roles.includes(role));

    if (!hasRole) {
      throw new ForbiddenException(AuthErrors.INSUFFICIENT_PERMISSIONS.en);
    }

    return true;
  }
}

/**
 * Permissions Guard
 *
 * Checks if the authenticated user has the required permissions
 *
 * @example
 * ```typescript
 * @Controller('farms')
 * @UseGuards(JwtAuthGuard, PermissionsGuard)
 * export class FarmsController {
 *   @Delete(':id')
 *   @RequirePermissions('farm:delete')
 *   deleteFarm(@Param('id') id: string) {
 *     return this.farmsService.delete(id);
 *   }
 * }
 * ```
 */
@Injectable()
export class PermissionsGuard implements CanActivate {
  constructor(private reflector: Reflector) {}

  canActivate(context: ExecutionContext): boolean {
    const requiredPermissions = this.reflector.getAllAndOverride<string[]>(
      'permissions',
      [context.getHandler(), context.getClass()],
    );

    if (!requiredPermissions || requiredPermissions.length === 0) {
      return true;
    }

    const request = context.switchToHttp().getRequest();
    const user = request.user;

    if (!user || !user.permissions) {
      throw new ForbiddenException(AuthErrors.INSUFFICIENT_PERMISSIONS.en);
    }

    const hasPermission = requiredPermissions.some((permission) =>
      user.permissions.includes(permission),
    );

    if (!hasPermission) {
      throw new ForbiddenException(AuthErrors.INSUFFICIENT_PERMISSIONS.en);
    }

    return true;
  }
}

/**
 * Farm Access Guard
 *
 * Checks if the authenticated user has access to the specified farm
 *
 * @example
 * ```typescript
 * @Controller('farms')
 * @UseGuards(JwtAuthGuard, FarmAccessGuard)
 * export class FarmsController {
 *   @Get(':farmId/fields')
 *   getFields(@Param('farmId') farmId: string) {
 *     return this.fieldsService.findByFarm(farmId);
 *   }
 * }
 * ```
 */
@Injectable()
export class FarmAccessGuard implements CanActivate {
  constructor(private reflector: Reflector) {}

  canActivate(context: ExecutionContext): boolean {
    const request = context.switchToHttp().getRequest();
    const user = request.user;

    if (!user) {
      throw new ForbiddenException(AuthErrors.INSUFFICIENT_PERMISSIONS.en);
    }

    // Admin users have access to all farms
    if (user.roles && user.roles.includes('admin')) {
      return true;
    }

    // Get farm ID from route parameters
    const farmId = request.params.farmId || request.params.farm_id;

    if (!farmId) {
      // If no farm ID in route, allow (will be checked at service level)
      return true;
    }

    // Check if user has access to this farm
    if (!user.farmIds || !user.farmIds.includes(farmId)) {
      throw new ForbiddenException(AuthErrors.INSUFFICIENT_PERMISSIONS.en);
    }

    return true;
  }
}

/**
 * Optional Authentication Guard
 *
 * Allows both authenticated and unauthenticated requests,
 * but populates user if token is present
 *
 * @example
 * ```typescript
 * @Controller('content')
 * export class ContentController {
 *   @Get()
 *   @UseGuards(OptionalAuthGuard)
 *   getContent(@CurrentUser() user?: any) {
 *     if (user) {
 *       return this.contentService.getPremiumContent();
 *     }
 *     return this.contentService.getPublicContent();
 *   }
 * }
 * ```
 */
@Injectable()
export class OptionalAuthGuard extends AuthGuard('jwt') {
  handleRequest(err: any, user: any) {
    // Return user if authenticated, null otherwise
    return user || null;
  }
}

/**
 * Active Account Guard
 *
 * Ensures the user account is active and verified
 *
 * @example
 * ```typescript
 * @Controller('profile')
 * @UseGuards(JwtAuthGuard, ActiveAccountGuard)
 * export class ProfileController {
 *   @Get()
 *   getProfile(@CurrentUser() user: any) {
 *     return this.profileService.getProfile(user.id);
 *   }
 * }
 * ```
 */
@Injectable()
export class ActiveAccountGuard implements CanActivate {
  canActivate(context: ExecutionContext): boolean {
    const request = context.switchToHttp().getRequest();
    const user = request.user;

    if (!user) {
      throw new UnauthorizedException(AuthErrors.MISSING_TOKEN.en);
    }

    if (user.isActive === false) {
      throw new ForbiddenException(AuthErrors.ACCOUNT_DISABLED.en);
    }

    if (user.isVerified === false) {
      throw new ForbiddenException(AuthErrors.ACCOUNT_NOT_VERIFIED.en);
    }

    return true;
  }
}
