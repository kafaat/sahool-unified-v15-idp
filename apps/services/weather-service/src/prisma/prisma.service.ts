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
    this.logger.log('Weather Database connected successfully');
  }

  async onModuleDestroy() {
    await this.$disconnect();
    this.logger.log('Weather Database disconnected');
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

  /**
   * Clean up old observations
   * حذف الأرصاد القديمة
   */
  async cleanupOldObservations(daysToKeep: number = 30) {
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - daysToKeep);

    const result = await this.weatherObservation.deleteMany({
      where: {
        timestamp: {
          lt: cutoffDate,
        },
      },
    });

    this.logger.log(`Cleaned up ${result.count} old weather observations`);
    return result;
  }

  /**
   * Clean up old forecasts
   * حذف التنبؤات القديمة
   */
  async cleanupOldForecasts(daysToKeep: number = 7) {
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - daysToKeep);

    const result = await this.weatherForecast.deleteMany({
      where: {
        fetchedAt: {
          lt: cutoffDate,
        },
      },
    });

    this.logger.log(`Cleaned up ${result.count} old weather forecasts`);
    return result;
  }

  /**
   * Clean up expired alerts
   * حذف التنبيهات المنتهية
   */
  async cleanupExpiredAlerts(daysToKeep: number = 7) {
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - daysToKeep);

    const result = await this.weatherAlert.deleteMany({
      where: {
        endTime: {
          lt: cutoffDate,
        },
      },
    });

    this.logger.log(`Cleaned up ${result.count} expired weather alerts`);
    return result;
  }
}
