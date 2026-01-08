/**
 * JWT Strategy for User Service
 * استراتيجية JWT لخدمة المستخدمين
 */

import { Injectable, UnauthorizedException } from '@nestjs/common';
import { PassportStrategy } from '@nestjs/passport';
import { ExtractJwt, Strategy } from 'passport-jwt';
import { PrismaService } from '../prisma/prisma.service';
import { JWTConfig } from '../utils/jwt.config';

export interface JwtPayload {
  sub: string;
  email: string;
  roles: string[];
  tid?: string;
  jti?: string;
  type?: 'access' | 'refresh';
  iat?: number;
  exp?: number;
}

@Injectable()
export class JwtStrategy extends PassportStrategy(Strategy) {
  constructor(private readonly prisma: PrismaService) {
    super({
      jwtFromRequest: ExtractJwt.fromAuthHeaderAsBearerToken(),
      ignoreExpiration: false,
      secretOrKey: JWTConfig.getVerificationKey(),
      issuer: JWTConfig.ISSUER,
      audience: JWTConfig.AUDIENCE,
      algorithms: [JWTConfig.ALGORITHM],
    });
  }

  async validate(payload: JwtPayload) {
    // Validate user exists in database
    const user = await this.prisma.user.findUnique({
      where: { id: payload.sub },
    });

    if (!user) {
      throw new UnauthorizedException('User not found');
    }

    // Check if user is active
    if (user.status !== 'ACTIVE') {
      throw new UnauthorizedException('User account is not active');
    }

    // Return user object (will be attached to request.user)
    return {
      id: user.id,
      email: user.email,
      roles: [user.role],
      tenantId: user.tenantId,
      tokenId: payload.jti,
    };
  }
}
