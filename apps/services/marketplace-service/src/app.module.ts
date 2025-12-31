/**
 * SAHOOL Marketplace App Module
 * وحدة التطبيق الرئيسية
 */

import { Module } from '@nestjs/common';
import { APP_GUARD } from '@nestjs/core';
import { ThrottlerModule, ThrottlerGuard } from '@nestjs/throttler';
import { AppController } from './app.controller';
import { PrismaService } from './prisma/prisma.service';
import { MarketService } from './market/market.service';
import { FintechService } from './fintech/fintech.service';
import { JwtAuthGuard, OptionalJwtAuthGuard } from './auth/jwt-auth.guard';

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
  ],
  controllers: [AppController],
  providers: [
    PrismaService,
    MarketService,
    FintechService,
    JwtAuthGuard,
    OptionalJwtAuthGuard,
    // Global rate limiting guard
    {
      provide: APP_GUARD,
      useClass: ThrottlerGuard,
    },
  ],
})
export class AppModule {}
