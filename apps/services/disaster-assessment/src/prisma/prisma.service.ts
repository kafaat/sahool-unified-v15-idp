// ═══════════════════════════════════════════════════════════════════════════════
// Prisma Service - Database Connection
// خدمة الاتصال بقاعدة البيانات
// ═══════════════════════════════════════════════════════════════════════════════

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
  private _isConnected = false;

  constructor() {
    super({
      log: [
        { level: "error", emit: "stdout" },
        { level: "warn", emit: "stdout" },
        { level: "info", emit: "stdout" },
      ],
      datasources: {
        db: {
          url: process.env.DATABASE_URL,
        },
      },
    });
  }

  async onModuleInit() {
    // Skip database connection if SKIP_DB_INIT is set (for container tests)
    if (process.env.SKIP_DB_INIT === "true") {
      this.logger.warn("SKIP_DB_INIT=true - skipping database connection");
      return;
    }

    // Skip if no DATABASE_URL is configured
    if (!process.env.DATABASE_URL) {
      this.logger.warn("DATABASE_URL not configured - running without database");
      return;
    }

    try {
      await this.$connect();
      this._isConnected = true;
      this.logger.log("Disaster Assessment Service Database connected successfully");
    } catch (error) {
      this._isConnected = false;
      this.logger.warn("Failed to connect to database - service will run in degraded mode");
      this.logger.warn(`Database error: ${error instanceof Error ? error.message : "Unknown error"}`);
      // Don't throw - allow service to start without database for container tests
      // Database operations will fail gracefully
    }
  }

  async onModuleDestroy() {
    if (this._isConnected) {
      await this.$disconnect();
      this.logger.log("Disaster Assessment Service Database disconnected");
    }
  }

  /**
   * Get current connection status
   * التحقق من حالة الاتصال
   */
  async getConnectionStatus(): Promise<{
    connected: boolean;
    timestamp: string;
    error?: string;
  }> {
    // Quick check - if we never connected, don't try to query
    if (!this._isConnected) {
      return {
        connected: false,
        timestamp: new Date().toISOString(),
        error: "Database not connected",
      };
    }

    try {
      await this.$queryRaw`SELECT 1`;
      return { connected: true, timestamp: new Date().toISOString() };
    } catch (error) {
      this._isConnected = false;
      this.logger.error("Database connection check failed:", error);
      return {
        connected: false,
        timestamp: new Date().toISOString(),
        error: error instanceof Error ? error.message : "Unknown error",
      };
    }
  }

  /**
   * Health check for readiness probe
   * فحص الصحة لجاهزية الخدمة
   */
  async isHealthy(): Promise<boolean> {
    // Quick check without querying if we know we're not connected
    if (!this._isConnected) {
      return false;
    }
    const status = await this.getConnectionStatus();
    return status.connected;
  }
}
