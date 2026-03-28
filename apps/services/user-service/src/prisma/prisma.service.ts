/**
 * Prisma Service - Database Connection with retry
 * خدمة الاتصال بقاعدة البيانات مع إعادة المحاولة
 */

import {
  Injectable,
  OnModuleInit,
  OnModuleDestroy,
  Logger,
} from "@nestjs/common";
import { PrismaClient } from "../../prisma/generated/client";

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

    // Handle connection errors gracefully by reconnecting
    // PgBouncer may close idle connections, causing "Server has closed the connection"
    this.$use(async (params, next) => {
      try {
        return await next(params);
      } catch (error: any) {
        // Retry on connection closed errors (PgBouncer idle timeout)
        if (
          error?.message?.includes('Server has closed the connection') ||
          error?.message?.includes('Connection reset by peer') ||
          error?.code === 'P2024' // Timed out fetching a new connection from pool
        ) {
          this.logger.warn(
            `Database connection lost during ${params.model}.${params.action}, reconnecting...`,
          );
          await this.$disconnect();
          await this.$connect();
          // Retry the query once after reconnecting
          return await next(params);
        }
        throw error;
      }
    });
  }

  async onModuleInit() {
    // Skip database connection in container tests (no DB available)
    if (process.env.SKIP_DB_INIT === 'true') {
      this.logger.log("Skipping database connection (SKIP_DB_INIT=true)");
      return;
    }
    await this.$connect();
    this.logger.log("User Service Database connected successfully");
  }

  async onModuleDestroy() {
    await this.$disconnect();
    this.logger.log("User Service Database disconnected");
  }

  /**
   * Get current connection status
   */
  async getConnectionStatus() {
    try {
      await this.$queryRaw`SELECT 1`;
      return { connected: true, timestamp: new Date().toISOString() };
    } catch (error) {
      this.logger.error("Database connection check failed:", error);
      return { connected: false, timestamp: new Date().toISOString() };
    }
  }
}
