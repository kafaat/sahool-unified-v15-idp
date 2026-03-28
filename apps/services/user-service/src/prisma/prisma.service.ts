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
  private _isReconnecting = false;

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
    const readOnlyActions = [
      'findUnique', 'findUniqueOrThrow', 'findFirst', 'findFirstOrThrow',
      'findMany', 'aggregate', 'count', 'groupBy',
    ];

    this.$use(async (params, next) => {
      try {
        return await next(params);
      } catch (error: any) {
        const isConnectionError =
          error?.message?.includes('Server has closed the connection') ||
          error?.message?.includes('Connection reset by peer') ||
          error?.code === 'P2024';

        // Only retry read-only actions to avoid duplicating writes
        if (isConnectionError && readOnlyActions.includes(params.action)) {
          this.logger.warn(
            `Database connection lost during ${params.model}.${params.action}, reconnecting...`,
          );

          // Mutex: prevent multiple concurrent reconnects
          if (!this._isReconnecting) {
            this._isReconnecting = true;
            try {
              await this.$disconnect();
              await this.$connect();
            } finally {
              this._isReconnecting = false;
            }
          }

          // Retry the read query once after reconnecting
          return await next(params);
        }

        // For write operations on connection error, log but don't retry
        if (isConnectionError) {
          this.logger.error(
            `Database connection lost during write ${params.model}.${params.action} - not retrying to avoid duplicates`,
          );
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
