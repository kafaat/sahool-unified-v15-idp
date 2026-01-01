/**
 * Prisma Service - Database Connection
 * خدمة الاتصال بقاعدة البيانات
 */

import { Injectable, OnModuleInit, OnModuleDestroy } from '@nestjs/common';
import { PrismaClient } from '@prisma/client';

@Injectable()
export class PrismaService
  extends PrismaClient
  implements OnModuleInit, OnModuleDestroy
{
  constructor() {
    super({
      log: ['query', 'info', 'warn', 'error'],
    });
  }

  async onModuleInit() {
    await this.$connect();
    console.log('📦 Weather Database connected successfully');
  }

  async onModuleDestroy() {
    await this.$disconnect();
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

    console.log(`🧹 Cleaned up ${result.count} old weather observations`);
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

    console.log(`🧹 Cleaned up ${result.count} old weather forecasts`);
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

    console.log(`🧹 Cleaned up ${result.count} expired weather alerts`);
    return result;
  }
}
