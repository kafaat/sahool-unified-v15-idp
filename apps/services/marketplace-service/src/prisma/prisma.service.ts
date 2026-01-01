/**
 * Prisma Service - Database Connection
 * خدمة الاتصال بقاعدة البيانات
 */

import { Injectable, OnModuleInit, OnModuleDestroy } from '@nestjs/common';
import { PrismaClient } from '@prisma/client';
// NOTE: Soft delete middleware requires @sahool/shared-db package
// Enable when Docker build supports shared packages monorepo context
// import { createSoftDeleteMiddleware } from '@sahool/shared-db';

@Injectable()
export class PrismaService
  extends PrismaClient
  implements OnModuleInit, OnModuleDestroy
{
  constructor() {
    super({
      log: ['query', 'info', 'warn', 'error'],
    });

    // NOTE: Soft delete middleware disabled until shared packages are available
    // Apply soft delete middleware
    // Exclude audit tables and logs from soft delete behavior
    // this.$use(
    //   createSoftDeleteMiddleware({
    //     excludedModels: [
    //       'WalletAuditLog',
    //       'CreditEvent',
    //       'Transaction', // Keep transaction history permanent
    //     ],
    //     enableLogging: process.env.NODE_ENV === 'development',
    //   })
    // );
  }

  async onModuleInit() {
    await this.$connect();
    console.log('Database connected successfully');
  }

  async onModuleDestroy() {
    await this.$disconnect();
  }
}
