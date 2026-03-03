/**
 * SAHOOL IoT Prisma Service
 * خدمة Prisma لإدارة اتصال قاعدة البيانات
 */

import { Injectable, OnModuleInit, OnModuleDestroy, Logger } from "@nestjs/common";
import { PrismaClient } from "../../prisma/generated/client";

@Injectable()
export class PrismaService extends PrismaClient implements OnModuleInit, OnModuleDestroy {
  private readonly logger = new Logger(PrismaService.name);

  constructor() {
    super({
      log: process.env.NODE_ENV === "development" ? ["query", "info", "warn", "error"] : ["error"],
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
      this.logger.log("Connected to PostgreSQL database");
    } catch (error: unknown) {
      this.logger.error(`Failed to connect to database: ${error instanceof Error ? error.message : String(error)}`);
      // Don't throw - allow service to run in degraded mode (Redis only)
      this.logger.warn("Running in degraded mode without database persistence");
    }
  }

  async onModuleDestroy() {
    await this.$disconnect();
    this.logger.log("Disconnected from PostgreSQL database");
  }
}
