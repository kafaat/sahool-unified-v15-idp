/**
 * Prisma Service - Database Connection
 * خدمة الاتصال بقاعدة البيانات
 */

import { Injectable, OnModuleInit, OnModuleDestroy, Logger } from '@nestjs/common';
import { PrismaClient } from '@prisma/client';

@Injectable()
export class PrismaService
  extends PrismaClient
  implements OnModuleInit, OnModuleDestroy
{
  private readonly logger = new Logger(PrismaService.name);

  constructor() {
    super({
      log: [
        { level: 'error', emit: 'stdout' },
        { level: 'warn', emit: 'stdout' },
        { level: 'info', emit: 'stdout' },
      ],
      datasources: {
        db: {
          url: process.env.DATABASE_URL,
        },
      },
    });
  }

  async onModuleInit() {
    await this.$connect();
    this.logger.log('Chat Database connected successfully');
  }

  async onModuleDestroy() {
    await this.$disconnect();
    this.logger.log('Chat Database disconnected');
  }

  /**
   * Get current connection status
   */
  async getConnectionStatus() {
    try {
      await this.$queryRaw`SELECT 1`;
      return { connected: true, timestamp: new Date().toISOString() };
    } catch (error) {
      this.logger.error('Database connection check failed:', error);
      return { connected: false, timestamp: new Date().toISOString() };
    }
  }
}
