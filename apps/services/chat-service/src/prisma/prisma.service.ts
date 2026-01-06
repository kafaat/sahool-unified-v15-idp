/**
 * Prisma Service - Database Connection
 * خدمة الاتصال بقاعدة البيانات
 */

import { Injectable, OnModuleInit, OnModuleDestroy, Logger } from '@nestjs/common';
import { PrismaClient } from '@prisma/client';
import { createQueryLogger } from '@sahool/shared-db';

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
      // High traffic service: real-time messaging
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
   * تفعيل تسجيل الاستعلامات البطيئة
   */
  private enableQueryLogging() {
    // Log queries that take longer than 1 second
    this.$on('query', createQueryLogger(this.logger));
    this.logger.log('Query performance logging enabled (threshold: 1000ms)');
  }

  async onModuleInit() {
    await this.$connect();
    this.logger.log('Chat Database connected successfully');
    this.startPoolMetricsLogging();
  }

  async onModuleDestroy() {
    await this.$disconnect();
    this.logger.log('Chat Database disconnected');
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
}
