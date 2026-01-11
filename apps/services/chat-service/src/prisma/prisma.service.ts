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
    const databaseUrl = process.env.DATABASE_URL;
    
    // Validate DATABASE_URL before calling super() (can't use 'this' before super)
    if (!databaseUrl) {
      console.error('DATABASE_URL environment variable is not set');
      throw new Error('DATABASE_URL is required but not provided. Please check your .env file and ensure POSTGRES_PASSWORD is set correctly.');
    }

    // Call super() with validated URL
    super({
      log: [
        { level: 'error', emit: 'stdout' },
        { level: 'warn', emit: 'stdout' },
        { level: 'info', emit: 'stdout' },
      ],
      datasources: {
        db: {
          url: databaseUrl,
        },
      },
    });

    // Log connection details (mask password for security) - now we can use this.logger
    const maskedUrl = databaseUrl.replace(/:([^:@]+)@/, ':****@');
    this.logger.log(`Connecting to database: ${maskedUrl}`);
  }

  async onModuleInit() {
    try {
      await this.$connect();
      this.logger.log('Chat Database connected successfully');
    } catch (error: any) {
      this.logger.error('Failed to connect to database');
      this.logger.error(`Error: ${error.message}`);
      
      // Provide helpful error messages for common issues
      if (error.message?.includes('password authentication failed')) {
        this.logger.error('Authentication failed: Please verify POSTGRES_PASSWORD in your .env file');
        this.logger.error('Ensure POSTGRES_PASSWORD matches the PostgreSQL database password');
      } else if (error.message?.includes('connection refused') || error.message?.includes('ECONNREFUSED')) {
        this.logger.error('Connection refused: Ensure pgbouncer service is running and healthy');
      } else if (error.message?.includes('does not exist')) {
        this.logger.error('Database does not exist: Please verify POSTGRES_DB in your .env file');
      }
      
      throw error;
    }
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
