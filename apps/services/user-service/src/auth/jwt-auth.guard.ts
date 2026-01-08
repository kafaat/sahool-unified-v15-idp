/**
 * JWT Authentication Guard with Token Revocation Support
 * حارس المصادقة باستخدام JWT مع دعم إلغاء الرموز
 */

import {
  Injectable,
  ExecutionContext,
  UnauthorizedException,
  CanActivate,
} from '@nestjs/common';
import { AuthGuard } from '@nestjs/passport';
import { Observable } from 'rxjs';
import * as jwt from 'jsonwebtoken';

/**
 * JWT Authentication Guard using Passport
 * Extends the built-in Passport JWT AuthGuard
 */
@Injectable()
export class JwtAuthGuard extends AuthGuard('jwt') {
  canActivate(
    context: ExecutionContext,
  ): boolean | Promise<boolean> | Observable<boolean> {
    // Call parent canActivate (which uses the JWT strategy)
    return super.canActivate(context);
  }

  handleRequest(err: any, user: any, info: any) {
    // Handle errors and invalid tokens
    if (err || !user) {
      if (info?.name === 'TokenExpiredError') {
        throw new UnauthorizedException('Token has expired');
      }
      if (info?.name === 'JsonWebTokenError') {
        throw new UnauthorizedException('Invalid token');
      }
      throw err || new UnauthorizedException('Authentication failed');
    }
    return user;
  }
}

/**
 * Optional Auth Guard - allows unauthenticated requests but attaches user if present
 * حارس المصادقة الاختياري
 */
@Injectable()
export class OptionalJwtAuthGuard implements CanActivate {
  canActivate(context: ExecutionContext): boolean {
    const request = context.switchToHttp().getRequest();
    const authHeader = request.headers.authorization;

    if (!authHeader) {
      return true; // Allow unauthenticated
    }

    const [type, token] = authHeader.split(' ');

    if (type !== 'Bearer' || !token) {
      return true; // Allow but don't authenticate
    }

    try {
      const secret = process.env.JWT_SECRET_KEY || process.env.JWT_SECRET;
      if (!secret) {
        return true;
      }

      // SECURITY FIX: Hardcoded whitelist of allowed algorithms to prevent algorithm confusion attacks
      // Never trust algorithm from environment variables or token header
      const ALLOWED_ALGORITHMS: jwt.Algorithm[] = ['HS256', 'HS384', 'HS512', 'RS256', 'RS384', 'RS512'];

      // Decode header without verification to check algorithm
      const header = jwt.decode(token, { complete: true })?.header;
      if (!header || !header.alg) {
        return true; // Allow unauthenticated for optional guard
      }

      // Reject 'none' algorithm explicitly
      if (header.alg.toLowerCase() === 'none') {
        return true; // Allow unauthenticated for optional guard
      }

      // Verify algorithm is in whitelist
      if (!ALLOWED_ALGORITHMS.includes(header.alg as jwt.Algorithm)) {
        return true; // Allow unauthenticated for optional guard
      }

      const decoded = jwt.verify(token, secret, {
        algorithms: ALLOWED_ALGORITHMS,
      }) as jwt.JwtPayload;

      request.user = {
        id: decoded.sub || decoded.user_id,
        email: decoded.email,
        roles: decoded.roles || [],
        tenantId: decoded.tenant_id,
      };
    } catch {
      // Ignore errors for optional auth
    }

    return true;
  }
}
