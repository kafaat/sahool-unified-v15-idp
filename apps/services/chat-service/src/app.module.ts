/**
 * SAHOOL Chat Service App Module
 * وحدة التطبيق الرئيسية
 */

import { Module } from '@nestjs/common';
import { APP_GUARD } from '@nestjs/core';
import { ThrottlerModule, ThrottlerGuard } from '@nestjs/throttler';
import { LoggerModule } from 'nestjs-pino';
import { createPinoLoggerConfig } from './utils/pino-logger.config';
import { PrismaService } from './prisma/prisma.service';
import { ChatGateway } from './chat/chat.gateway';
import { ChatService } from './chat/chat.service';
import { ChatController } from './chat/chat.controller';
import { HealthController } from './health/health.controller';

@Module({
  imports: [
    // Structured JSON logging with Pino
    LoggerModule.forRoot(createPinoLoggerConfig('chat-service')),

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
  controllers: [ChatController, HealthController],
  providers: [
    PrismaService,
    ChatService,
    ChatGateway,
    // Global rate limiting guard
    {
      provide: APP_GUARD,
      useClass: ThrottlerGuard,
    },
  ],
})
export class AppModule {}
