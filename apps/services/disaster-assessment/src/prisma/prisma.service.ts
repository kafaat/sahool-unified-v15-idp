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
    try {
      await this.$connect();
      this.logger.log("Disaster Assessment Service Database connected successfully");
    } catch (error) {
      this.logger.error("Failed to connect to database:", error);
      throw error;
    }
  }

  async onModuleDestroy() {
    await this.$disconnect();
    this.logger.log("Disaster Assessment Service Database disconnected");
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
    try {
      await this.$queryRaw`SELECT 1`;
      return { connected: true, timestamp: new Date().toISOString() };
    } catch (error) {
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
    const status = await this.getConnectionStatus();
    return status.connected;
  }
}
