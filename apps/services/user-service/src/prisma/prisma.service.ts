/**
 * Prisma Service - Database Connection with Encryption
 * خدمة الاتصال بقاعدة البيانات مع التشفير
 */

import { Injectable, OnModuleInit, OnModuleDestroy, Logger } from '@nestjs/common';
import { PrismaClient } from '@prisma/client';
import { createPrismaEncryptionMiddleware } from '../../../../packages/shared-crypto/src/prisma-encryption';
import { createQueryLogger } from '../utils/db-utils';

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
      // High traffic service: auth, user management
      datasources: {
        db: {
          url: process.env.DATABASE_URL,
        },
      },
    });

    // Apply encryption middleware
    this.enableEncryption();

    // Enable query performance logging
    this.enableQueryLogging();
  }

  /**
   * Enable field-level encryption for sensitive data
   * تفعيل التشفير على مستوى الحقول للبيانات الحساسة
   */
  private enableEncryption() {
    const encryptionConfig = {
      // User model - phone is searchable (deterministic encryption)
      User: {
        phone: { type: 'deterministic' as const },
      },
      // UserProfile model - nationalId and phone are searchable
      UserProfile: {
        nationalId: { type: 'deterministic' as const },
        dateOfBirth: { type: 'standard' as const },
      },
    };

    this.$use(
      createPrismaEncryptionMiddleware(encryptionConfig, {
        debug: process.env.CRYPTO_DEBUG === 'true',
        onError: (error, context) => {
          // nosemgrep: javascript.lang.security.audit.unsafe-formatstring.unsafe-formatstring
          console.error(
            '[Encryption Error] %s failed for %s.%s: %s',
            context.operation,
            context.model,
            context.field,
            error.message
          );
        },
      })
    );

    console.log('Field-level encryption enabled for User Service');
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
    this.logger.log('User Service Database connected successfully');

    // Log connection pool metrics periodically
    this.startPoolMetricsLogging();
  }

  async onModuleDestroy() {
    await this.$disconnect();
    this.logger.log('User Service Database disconnected');
  }

  /**
   * Start periodic logging of connection pool metrics
   * بدء تسجيل مقاييس تجمع الاتصالات بشكل دوري
   */
  private startPoolMetricsLogging() {
    // Log pool metrics every 5 minutes
    setInterval(() => {
      this.$metrics
        .json()
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
        .catch((err) => {
          this.logger.warn('Failed to collect pool metrics:', err.message);
        });
    }, 300000); // 5 minutes
  }

  /**
   * Get current connection pool metrics
   * الحصول على مقاييس تجمع الاتصالات الحالية
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
