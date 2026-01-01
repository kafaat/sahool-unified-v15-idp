/**
 * Audit Module for Marketplace Service
 * Integrates enhanced audit trail system
 */

import { Module, NestModule, MiddlewareConsumer } from '@nestjs/common';
import { APP_INTERCEPTOR } from '@nestjs/core';
import {
  AuditLogger,
  AuditMiddleware,
  AuditInterceptor,
  consoleAlertHandler,
} from '@sahool/shared-audit';
import { PrismaService } from '../prisma/prisma.service';

@Module({
  providers: [
    // Provide AuditLogger with PrismaService
    {
      provide: AuditLogger,
      useFactory: (prisma: PrismaService) => {
        return new AuditLogger({
          prisma,
          defaultTenantId: 'marketplace',
          enableHashChain: true,
          enableAlerts: true,
          alertConfig: {
            handlers: [consoleAlertHandler],
            batchAlerts: true,
            batchWindowMs: 60000, // 1 minute
          },
          globalRedactFields: [
            'password',
            'token',
            'secret',
            'apiKey',
            'privateKey',
            'accessToken',
            'refreshToken',
            'creditCardNumber',
            'cvv',
            'pin',
          ],
        });
      },
      inject: [PrismaService],
    },
    // Global audit interceptor
    {
      provide: APP_INTERCEPTOR,
      useClass: AuditInterceptor,
    },
  ],
  exports: [AuditLogger],
})
export class AuditModule implements NestModule {
  configure(consumer: MiddlewareConsumer) {
    // Apply audit middleware to all routes
    consumer.apply(AuditMiddleware).forRoutes('*');
  }
}
