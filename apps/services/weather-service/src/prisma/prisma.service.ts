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
        { level: 'query', emit: 'event' },
        { level: 'error', emit: 'stdout' },
        { level: 'warn', emit: 'stdout' },
        { level: 'info', emit: 'stdout' },
      ],
      // Connection pool configuration
      // Medium traffic service: weather data fetching
      datasources: {
        db: {
          url: process.env.DATABASE_URL,
        },
      },
    });

    // Enable query performance logging
    this.enableQueryLogging();
  }

  /**
   * Enable query performance logging for slow queries
   */
  private enableQueryLogging() {
    this.$on('query', (e: any) => {
      if (e.duration > 1000) {
        this.logger.warn(`Slow query detected (${e.duration}ms): ${e.query}`);
      }
    });
    this.logger.log('Query performance logging enabled (threshold: 1000ms)');
  }

  async onModuleInit() {
    await this.$connect();
    this.logger.log('Weather Database connected successfully');
    this.startPoolMetricsLogging();
  }

  async onModuleDestroy() {
    await this.$disconnect();
    this.logger.log('Weather Database disconnected');
  }

  /**
   * Start periodic logging of connection pool metrics
   */
  private startPoolMetricsLogging() {
    setInterval(() => {
      this.$metrics.json()
        .then((metrics) => {
          this.logger.debug('Connection Pool Metrics:', {
            pool: {
              active: metrics.counters.filter((c) => c.key === 'prisma_client_queries_active')[0]?.value || 0,
              wait: metrics.counters.filter((c) => c.key === 'prisma_client_queries_wait')[0]?.value || 0,
              total: metrics.counters.filter((c) => c.key === 'prisma_client_queries_total')[0]?.value || 0,
            },
            timestamp: new Date().toISOString(),
          });
        })
        .catch((err) => this.logger.warn('Failed to collect pool metrics:', err.message));
    }, 300000);
  }

  /**
   * Get current connection pool metrics
   */
  async getPoolMetrics() {
    try {
      const metrics = await this.$metrics.json();
      return {
        activeConnections: metrics.counters.filter((c) => c.key === 'prisma_client_queries_active')[0]?.value || 0,
        waitingConnections: metrics.counters.filter((c) => c.key === 'prisma_client_queries_wait')[0]?.value || 0,
        totalQueries: metrics.counters.filter((c) => c.key === 'prisma_client_queries_total')[0]?.value || 0,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      this.logger.error('Failed to get pool metrics:', error);
      return null;
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
