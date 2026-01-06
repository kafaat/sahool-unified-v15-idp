/**
 * SAHOOL User Service App Module
 * وحدة التطبيق الرئيسية
 *
 * Includes:
 * - Authentication with JWT and token revocation
 * - User management
 * - Rate limiting
 * - Health checks
 */

import { Module } from '@nestjs/common';
import { APP_GUARD } from '@nestjs/core';
import { ThrottlerModule, ThrottlerGuard } from '@nestjs/throttler';
import { PrismaModule } from './prisma/prisma.module';
import { UsersModule } from './users/users.module';
import { AuthModule } from './auth/auth.module';
import { HealthController } from './health/health.controller';
import { JwtService, JwtModule } from '@nestjs/jwt';
import { Reflector } from '@nestjs/core';

// Import token revocation guard
import { TokenRevocationGuard } from '@sahool/nestjs-auth/guards/token-revocation.guard';
import { RedisTokenRevocationStore } from '@sahool/nestjs-auth/services/token-revocation';
import { JWTConfig } from '@sahool/nestjs-auth/config/jwt.config';

@Module({
  imports: [
    // Rate limiting configuration
    ThrottlerModule.forRoot([
      {
        name: 'short',
        ttl: 1000, // 1 second
        limit: 10, // 10 requests per second
      },
      {
        name: 'medium',
        ttl: 60000, // 1 minute
        limit: 100, // 100 requests per minute
      },
      {
        name: 'long',
        ttl: 3600000, // 1 hour
        limit: 1000, // 1000 requests per hour
      },
    ]),
    // JWT Module for token decoding in revocation guard
    JwtModule.register({
      secret: JWTConfig.getVerificationKey(),
    }),
    PrismaModule,
    AuthModule, // Authentication module with token revocation
    UsersModule,
  ],
  controllers: [HealthController],
  providers: [
    // Global rate limiting guard
    {
      provide: APP_GUARD,
      useClass: ThrottlerGuard,
    },
    // Global token revocation guard (checks all authenticated requests)
    {
      provide: APP_GUARD,
      useClass: TokenRevocationGuard,
    },
  ],
})
export class AppModule {}
