/**
 * Token Revocation Guard for NestJS
 * حارس إلغاء الرموز لـ NestJS
 *
 * Checks if tokens are revoked before allowing access to protected routes.
 */

import {
  Injectable,
  CanActivate,
  ExecutionContext,
  UnauthorizedException,
  Logger,
} from "@nestjs/common";
import { Reflector } from "@nestjs/core";
import { JwtService } from "@nestjs/jwt";
import { Request } from "express";
import { RedisTokenRevocationStore } from "../services/token-revocation";
import { JwtPayload } from "../strategies/jwt.strategy";
import { AuthErrors } from "../config/jwt.config";

/**
 * Metadata key for skipping revocation check
 */
export const SKIP_REVOCATION_CHECK_KEY = "skipRevocationCheck";

/**
 * Decorator to skip token revocation check
 *
 * @example
 * ```typescript
 * import { Controller, Get } from '@nestjs/common';
 * import { SkipRevocationCheck } from '@shared/auth/token-revocation.guard';
 *
 * @Controller('public')
 * export class PublicController {
 *   @Get('data')
 *   @SkipRevocationCheck()
 *   async getData() {
 *     return { data: 'public' };
 *   }
 * }
 * ```
 */
export const SkipRevocationCheck = () =>
  Reflect.metadata(SKIP_REVOCATION_CHECK_KEY, true);

/**
 * Guard to check if tokens are revoked
 * حارس للتحقق من إلغاء الرموز
 *
 * This guard should be used globally or on specific routes to check
 * if authenticated tokens have been revoked.
 *
 * @example
 * ```typescript
 * import { Module } from '@nestjs/common';
 * import { APP_GUARD } from '@nestjs/core';
 * import { TokenRevocationGuard } from '@shared/auth/token-revocation.guard';
 *
 * @Module({
 *   providers: [
 *     {
 *       provide: APP_GUARD,
 *       useClass: TokenRevocationGuard,
 *     },
 *   ],
 * })
 * export class AppModule {}
 * ```
 */
@Injectable()
export class TokenRevocationGuard implements CanActivate {
  private readonly logger = new Logger(TokenRevocationGuard.name);

  constructor(
    private readonly revocationStore: RedisTokenRevocationStore,
    private readonly jwtService: JwtService,
    private readonly reflector: Reflector,
  ) {}

  /**
   * Check if request can activate (token is not revoked)
   */
  async canActivate(context: ExecutionContext): Promise<boolean> {
    // Check if revocation check should be skipped
    const skipRevocationCheck = this.reflector.getAllAndOverride<boolean>(
      SKIP_REVOCATION_CHECK_KEY,
      [context.getHandler(), context.getClass()],
    );

    if (skipRevocationCheck) {
      return true;
    }

    const request = context.switchToHttp().getRequest<Request>();

    // Extract token
    const token = this.extractTokenFromHeader(request);
    if (!token) {
      // No token present - let AuthGuard handle it
      return true;
    }

    try {
      // Decode token (without verification - already done by JWT guard)
      const payload = this.jwtService.decode(token) as JwtPayload;

      if (!payload) {
        // Invalid token - let AuthGuard handle it
        return true;
      }

      // Check if token is revoked
      const result = await this.revocationStore.isRevoked({
        jti: payload.jti,
        userId: payload.sub,
        tenantId: payload.tid,
        issuedAt: payload.iat,
      });

      if (result.isRevoked) {
        this.logger.warn(
          `Revoked token access attempt: userId=${payload.sub}, reason=${result.reason}`,
        );

        throw new UnauthorizedException({
          error: AuthErrors.TOKEN_REVOKED.code,
          message: AuthErrors.TOKEN_REVOKED.en,
          messageAr: AuthErrors.TOKEN_REVOKED.ar,
          reason: result.reason,
        });
      }

      return true;
    } catch (error) {
      if (error instanceof UnauthorizedException) {
        throw error;
      }

      // Log error but allow access (fail open)
      const errorMessage =
        error instanceof Error ? error.message : "Unknown error";
      this.logger.error(`Error checking token revocation: ${errorMessage}`);
      return true;
    }
  }

  /**
   * Extract JWT token from Authorization header
   */
  private extractTokenFromHeader(request: Request): string | null {
    const authorization = request.headers.authorization;

    if (!authorization) {
      return null;
    }

    const [scheme, token] = authorization.split(" ");

    if (scheme?.toLowerCase() !== "bearer" || !token) {
      return null;
    }

    return token;
  }
}

/**
 * Token Revocation Interceptor
 * اعتراض إلغاء الرموز
 *
 * Alternative to guard - can be used as an interceptor for more flexibility.
 *
 * @example
 * ```typescript
 * import { Controller, Get, UseInterceptors } from '@nestjs/common';
 * import { TokenRevocationInterceptor } from '@shared/auth/token-revocation.guard';
 *
 * @Controller('protected')
 * @UseInterceptors(TokenRevocationInterceptor)
 * export class ProtectedController {
 *   @Get('data')
 *   async getData() {
 *     return { data: 'protected' };
 *   }
 * }
 * ```
 */
import {
  Injectable as InjectableInterceptor,
  NestInterceptor,
  CallHandler,
} from "@nestjs/common";
import { Observable } from "rxjs";

@InjectableInterceptor()
export class TokenRevocationInterceptor implements NestInterceptor {
  private readonly logger = new Logger(TokenRevocationInterceptor.name);

  constructor(
    private readonly revocationStore: RedisTokenRevocationStore,
    private readonly jwtService: JwtService,
  ) {}

  async intercept(
    context: ExecutionContext,
    next: CallHandler,
  ): Promise<Observable<any>> {
    const request = context.switchToHttp().getRequest<Request>();

    // Extract token
    const token = this.extractTokenFromHeader(request);
    if (token) {
      try {
        // Decode token
        const payload = this.jwtService.decode(token) as JwtPayload;

        if (payload) {
          // Check if token is revoked
          const result = await this.revocationStore.isRevoked({
            jti: payload.jti,
            userId: payload.sub,
            tenantId: payload.tid,
            issuedAt: payload.iat,
          });

          if (result.isRevoked) {
            this.logger.warn(
              `Revoked token access attempt: userId=${payload.sub}, reason=${result.reason}`,
            );

            throw new UnauthorizedException({
              error: AuthErrors.TOKEN_REVOKED.code,
              message: AuthErrors.TOKEN_REVOKED.en,
              messageAr: AuthErrors.TOKEN_REVOKED.ar,
              reason: result.reason,
            });
          }
        }
      } catch (error) {
        if (error instanceof UnauthorizedException) {
          throw error;
        }

        // Log error but continue (fail open)
        const errorMessage =
          error instanceof Error ? error.message : "Unknown error";
        this.logger.error(`Error checking token revocation: ${errorMessage}`);
      }
    }

    return next.handle();
  }

  private extractTokenFromHeader(request: Request): string | null {
    const authorization = request.headers.authorization;

    if (!authorization) {
      return null;
    }

    const [scheme, token] = authorization.split(" ");

    if (scheme?.toLowerCase() !== "bearer" || !token) {
      return null;
    }

    return token;
  }
}
