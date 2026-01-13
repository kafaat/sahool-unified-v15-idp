/**
 * Service-to-Service Authentication Guard for NestJS
 * Guard and decorators for verifying service tokens
 */

import {
  Injectable,
  CanActivate,
  ExecutionContext,
  UnauthorizedException,
  ForbiddenException,
  SetMetadata,
  createParamDecorator,
} from "@nestjs/common";
import { Reflector } from "@nestjs/core";
import { Request } from "express";
import {
  verifyServiceToken,
  ServiceAuthErrors,
  ServiceTokenPayload,
  ServiceAuthException,
} from "./service_auth";

/**
 * Metadata key for allowed services
 */
const ALLOWED_SERVICES_KEY = "allowed_services";

/**
 * Metadata key for current service name
 */
const CURRENT_SERVICE_KEY = "current_service";

/**
 * Decorator to specify which services are allowed to call an endpoint
 *
 * @param services - List of service names allowed to call this endpoint
 *
 * @example
 * ```typescript
 * @Controller('internal')
 * export class InternalController {
 *   @Get('data')
 *   @AllowedServices(['farm-service', 'crop-service'])
 *   @UseGuards(ServiceAuthGuard)
 *   async getData() {
 *     return { data: 'internal data' };
 *   }
 * }
 * ```
 */
export const AllowedServices = (...services: string[]) =>
  SetMetadata(ALLOWED_SERVICES_KEY, services);

/**
 * Decorator to specify the current service name
 *
 * @param serviceName - Name of the current service
 *
 * @example
 * ```typescript
 * @Controller('internal')
 * @CurrentService('farm-service')
 * export class InternalController {
 *   // ...
 * }
 * ```
 */
export const CurrentService = (serviceName: string) =>
  SetMetadata(CURRENT_SERVICE_KEY, serviceName);

/**
 * Parameter decorator to extract service information from request
 *
 * @example
 * ```typescript
 * @Get('data')
 * @UseGuards(ServiceAuthGuard)
 * async getData(@ServiceInfo() serviceInfo: ServiceTokenPayload) {
 *   console.log(`Called by: ${serviceInfo.service_name}`);
 *   return { data: 'internal data' };
 * }
 * ```
 */
export const ServiceInfo = createParamDecorator(
  (data: unknown, ctx: ExecutionContext): ServiceTokenPayload => {
    const request = ctx.switchToHttp().getRequest();
    return request.serviceInfo;
  },
);

/**
 * Parameter decorator to extract calling service name from request
 *
 * @example
 * ```typescript
 * @Get('data')
 * @UseGuards(ServiceAuthGuard)
 * async getData(@CallingService() callingService: string) {
 *   console.log(`Called by: ${callingService}`);
 *   return { data: 'internal data' };
 * }
 * ```
 */
export const CallingService = createParamDecorator(
  (data: unknown, ctx: ExecutionContext): string => {
    const request = ctx.switchToHttp().getRequest();
    return request.serviceInfo?.service_name;
  },
);

/**
 * Extend Express Request interface to include service information
 */
declare global {
  namespace Express {
    interface Request {
      serviceInfo?: ServiceTokenPayload;
      isServiceRequest?: boolean;
    }
  }
}

/**
 * Service Authentication Guard for NestJS
 *
 * This guard validates service tokens for inter-service communication.
 * It extracts the service token from X-Service-Token header and validates it.
 *
 * @example
 * ```typescript
 * // In your controller
 * import { Controller, Get, UseGuards } from '@nestjs/common';
 * import { ServiceAuthGuard, AllowedServices, ServiceInfo } from './service-auth.guard';
 *
 * @Controller('internal')
 * export class InternalController {
 *   @Get('fields')
 *   @UseGuards(ServiceAuthGuard)
 *   @AllowedServices(['farm-service', 'crop-service'])
 *   async getFields(@ServiceInfo() serviceInfo: ServiceTokenPayload) {
 *     return {
 *       message: `Called by ${serviceInfo.service_name}`,
 *       fields: [...],
 *     };
 *   }
 * }
 * ```
 *
 * @example
 * ```typescript
 * // Global guard in main.ts
 * import { NestFactory, Reflector } from '@nestjs/core';
 * import { ServiceAuthGuard } from './shared/auth/service-auth.guard';
 *
 * const app = await NestFactory.create(AppModule);
 * const reflector = app.get(Reflector);
 * app.useGlobalGuards(new ServiceAuthGuard(reflector, 'farm-service'));
 * ```
 */
@Injectable()
export class ServiceAuthGuard implements CanActivate {
  constructor(
    private reflector: Reflector,
    private currentService?: string,
  ) {}

  async canActivate(context: ExecutionContext): Promise<boolean> {
    const request = context.switchToHttp().getRequest<Request>();

    // Get current service from decorator or constructor
    const currentService =
      this.reflector.get<string>(CURRENT_SERVICE_KEY, context.getHandler()) ||
      this.reflector.get<string>(CURRENT_SERVICE_KEY, context.getClass()) ||
      this.currentService ||
      process.env.SERVICE_NAME;

    if (!currentService) {
      throw new Error(
        "Current service name not configured. Use @CurrentService() decorator or set SERVICE_NAME env variable",
      );
    }

    // Extract service token from header
    const serviceToken = request.headers["x-service-token"] as string;

    if (!serviceToken) {
      throw new UnauthorizedException({
        error: "missing_service_token",
        message: "Service authentication token is required",
      });
    }

    try {
      // Verify service token
      const payload = verifyServiceToken(serviceToken);

      // Verify the target service matches current service
      if (payload.target_service !== currentService) {
        throw new ForbiddenException({
          error: ServiceAuthErrors.UNAUTHORIZED_SERVICE_CALL.code,
          message: ServiceAuthErrors.UNAUTHORIZED_SERVICE_CALL.en,
        });
      }

      // Check allowed services if specified
      const allowedServices =
        this.reflector.get<string[]>(
          ALLOWED_SERVICES_KEY,
          context.getHandler(),
        ) ||
        this.reflector.get<string[]>(ALLOWED_SERVICES_KEY, context.getClass());

      if (allowedServices && allowedServices.length > 0) {
        if (!allowedServices.includes(payload.service_name)) {
          throw new ForbiddenException({
            error: ServiceAuthErrors.UNAUTHORIZED_SERVICE_CALL.code,
            message: `Service ${payload.service_name} is not allowed to call this endpoint`,
          });
        }
      }

      // Add service information to request
      request.serviceInfo = payload;
      request.isServiceRequest = true;

      return true;
    } catch (error) {
      if (error instanceof ServiceAuthException) {
        throw new UnauthorizedException(error.toJSON());
      }

      if (
        error instanceof UnauthorizedException ||
        error instanceof ForbiddenException
      ) {
        throw error;
      }

      throw new UnauthorizedException({
        error: ServiceAuthErrors.INVALID_SERVICE_TOKEN.code,
        message: ServiceAuthErrors.INVALID_SERVICE_TOKEN.en,
      });
    }
  }
}

/**
 * Optional Service Authentication Guard
 *
 * This guard validates service tokens if present, but doesn't require them.
 * Useful for endpoints that can be called by both users and services.
 *
 * @example
 * ```typescript
 * @Controller('data')
 * export class DataController {
 *   @Get('items')
 *   @UseGuards(OptionalServiceAuthGuard)
 *   async getItems(@ServiceInfo() serviceInfo?: ServiceTokenPayload) {
 *     if (serviceInfo) {
 *       // Called by a service
 *       console.log(`Service call from ${serviceInfo.service_name}`);
 *     } else {
 *       // Called by a user
 *       console.log('User call');
 *     }
 *     return { items: [...] };
 *   }
 * }
 * ```
 */
@Injectable()
export class OptionalServiceAuthGuard implements CanActivate {
  constructor(
    private reflector: Reflector,
    private currentService?: string,
  ) {}

  async canActivate(context: ExecutionContext): Promise<boolean> {
    const request = context.switchToHttp().getRequest<Request>();

    // Extract service token from header
    const serviceToken = request.headers["x-service-token"] as string;

    if (!serviceToken) {
      // No service token, continue without service authentication
      return true;
    }

    try {
      // Get current service
      const currentService =
        this.reflector.get<string>(CURRENT_SERVICE_KEY, context.getHandler()) ||
        this.reflector.get<string>(CURRENT_SERVICE_KEY, context.getClass()) ||
        this.currentService ||
        process.env.SERVICE_NAME;

      // Verify service token
      const payload = verifyServiceToken(serviceToken);

      // Verify the target service matches current service if specified
      if (currentService && payload.target_service !== currentService) {
        // Invalid target, but we're optional, so just ignore
        return true;
      }

      // Add service information to request
      request.serviceInfo = payload;
      request.isServiceRequest = true;

      return true;
    } catch (error) {
      // If token verification fails, continue without service authentication
      // This is "optional" after all
      return true;
    }
  }
}

/**
 * Decorator to require service authentication for an entire controller
 *
 * @param currentService - Name of the current service
 * @param allowedServices - Optional list of allowed services
 *
 * @example
 * ```typescript
 * @Controller('internal')
 * @RequireServiceAuth('farm-service', ['crop-service', 'field-service'])
 * export class InternalController {
 *   @Get('data')
 *   async getData(@ServiceInfo() serviceInfo: ServiceTokenPayload) {
 *     return { data: 'internal data' };
 *   }
 * }
 * ```
 */
export function RequireServiceAuth(
  currentService: string,
  allowedServices?: string[],
) {
  return function (target: any) {
    SetMetadata(CURRENT_SERVICE_KEY, currentService)(target);
    if (allowedServices) {
      SetMetadata(ALLOWED_SERVICES_KEY, allowedServices)(target);
    }
  };
}
