/**
 * Prisma Service - Database Connection
 * خدمة الاتصال بقاعدة البيانات
 */

import {
  Injectable,
  OnModuleInit,
  OnModuleDestroy,
  Logger,
} from "@nestjs/common";
import { PrismaClient } from "@prisma/client";

@Injectable()
export class PrismaService
  extends PrismaClient
  implements OnModuleInit, OnModuleDestroy
{
  private readonly logger = new Logger(PrismaService.name);
  private isConnected = false;
  private readonly isTestEnvironment: boolean;

  constructor() {
    super({
      log: [
        { level: "error", emit: "stdout" },
        { level: "warn", emit: "stdout" },
        { level: "info", emit: "stdout" },
      ],
      // Connection pool configuration
      // High traffic service: marketplace transactions
      datasources: {
        db: {
          url: process.env.DATABASE_URL,
        },
      },
    });

    this.isTestEnvironment = ["test", "ci", "testing"].includes(
      (process.env.ENVIRONMENT || process.env.NODE_ENV || "").toLowerCase(),
    );
  }

  async onModuleInit() {
    try {
      await this.$connect();
      this.isConnected = true;
      this.logger.log("Marketplace Database connected successfully");
    } catch (error) {
      if (this.isTestEnvironment) {
        this.logger.warn(
          `Database connection failed in test environment: ${error.message}`,
        );
        this.logger.warn("Running in degraded mode without database");
        this.isConnected = false;
      } else {
        throw error;
      }
    }
  }

  async onModuleDestroy() {
    if (this.isConnected) {
      await this.$disconnect();
      this.logger.log("Marketplace Database disconnected");
    }
  }

  /**
   * Get current connection status
   */
  async getConnectionStatus() {
    try {
      await this.$queryRaw`SELECT 1`;
      return {
        connected: true,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      this.logger.error("Database connection check failed:", error);
      return {
        connected: false,
        timestamp: new Date().toISOString(),
      };
    }
  }
}
