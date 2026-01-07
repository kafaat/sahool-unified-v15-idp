/**
 * Token Revocation Guard for NestJS
 * حارس إلغاء الرموز لـ NestJS
 */

import {
  Injectable,
  CanActivate,
  ExecutionContext,
  UnauthorizedException,
  Logger,
  NestInterceptor,
  CallHandler,
} from '@nestjs/common';
import { Reflector } from '@nestjs/core';
import { JwtService } from '@nestjs/jwt';
import { Request } from 'express';
import { Observable } from 'rxjs';
import { RedisTokenRevocationStore } from './token-revocation';
import { AuthErrors } from './jwt.config';

/**
 * JWT Payload interface
 */
export interface JwtPayload {
  sub: string;
  jti?: string;
  tid?: string;
  iat?: number;
  exp?: number;
  [key: string]: any;
}

/**
 * Metadata key for skipping revocation check
 */
export const SKIP_REVOCATION_CHECK_KEY = 'skipRevocationCheck';

/**
 * Decorator to skip token revocation check
 */
export const SkipRevocationCheck = () =>
  Reflect.metadata(SKIP_REVOCATION_CHECK_KEY, true);

/**
 * Guard to check if tokens are revoked
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
    const skipRevocationCheck = this.reflector.getAllAndOverride<boolean>(
      SKIP_REVOCATION_CHECK_KEY,
      [context.getHandler(), context.getClass()],
    );

    if (skipRevocationCheck) {
      return true;
    }

    const request = context.switchToHttp().getRequest<Request>();

    const token = this.extractTokenFromHeader(request);
    if (!token) {
      return true;
    }

    try {
      const payload = this.jwtService.decode(token) as JwtPayload;

      if (!payload) {
        return true;
      }

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

      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
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

    const [scheme, token] = authorization.split(' ');

    if (scheme?.toLowerCase() !== 'bearer' || !token) {
      return null;
    }

    return token;
  }
}

/**
 * Token Revocation Interceptor - alternative to guard
 */
@Injectable()
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

    const token = this.extractTokenFromHeader(request);
    if (token) {
      try {
        const payload = this.jwtService.decode(token) as JwtPayload;

        if (payload) {
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

        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
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

    const [scheme, token] = authorization.split(' ');

    if (scheme?.toLowerCase() !== 'bearer' || !token) {
      return null;
    }

    return token;
  }
}
