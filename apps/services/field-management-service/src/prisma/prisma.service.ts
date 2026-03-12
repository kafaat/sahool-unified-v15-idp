/**
 * Prisma Service - Database Connection with Enhanced Features
 * - Connection pooling configuration
 * - Health check support
 * - Query logging for slow queries
 * - Graceful shutdown
 * - Graceful degraded mode: service starts even when DB is temporarily unavailable
 */

import {
  Injectable,
  OnModuleInit,
  OnModuleDestroy,
  Logger,
} from "@nestjs/common";
import { PrismaClient, Prisma } from "../../prisma/generated/client";

// Slow query threshold in milliseconds
const SLOW_QUERY_THRESHOLD = 1000;
// Background reconnect interval (30 s)
const RECONNECT_INTERVAL_MS = 30_000;

@Injectable()
export class PrismaService
  extends PrismaClient<Prisma.PrismaClientOptions, "query" | "error">
  implements OnModuleInit, OnModuleDestroy
{
  private readonly logger = new Logger(PrismaService.name);
  private isConnected = false;
  private readonly isTestEnvironment: boolean;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;

  constructor() {
    super({
      log: [
        { level: "query", emit: "event" },
        { level: "error", emit: "stdout" },
        { level: "warn", emit: "stdout" },
      ],
      datasources: {
        db: {
          url: process.env.DATABASE_URL,
        },
      },
    });

    this.isTestEnvironment = ["test", "ci", "testing"].includes(
      (process.env.ENVIRONMENT || process.env.NODE_ENV || "").toLowerCase(),
    );

    // Log slow queries
    this.$on("query", (event) => {
      if (event.duration > SLOW_QUERY_THRESHOLD) {
        this.logger.warn(
          `Slow query detected (${event.duration}ms): ${event.query.substring(0, 200)}...`,
        );
      }
    });
  }

  async onModuleInit() {
    await this._tryConnect();
  }

  /**
   * Attempt to connect with exponential-backoff retries.
   * On final failure the service starts in degraded mode (isConnected = false)
   * so the liveness probe (/healthz) still returns 200, while the readiness
   * probe (/readyz) correctly returns 503 until the database is reachable.
   * A background timer keeps retrying so the service self-heals automatically.
   */
  private async _tryConnect(): Promise<void> {
    const maxRetries = this.isTestEnvironment ? 1 : 3;

    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        await this.$connect();
        this.isConnected = true;
        this.logger.log("Field Management Database connected successfully");

        // Enable PostGIS extension if not already present
        try {
          await this.$queryRaw`CREATE EXTENSION IF NOT EXISTS postgis`;
          this.logger.log("PostGIS extension verified");
        } catch {
          this.logger.debug("PostGIS extension already exists or insufficient privilege (non-fatal)");
        }
        return; // Success — exit retry loop
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : String(error);

        if (this.isTestEnvironment) {
          this.logger.warn(
            `Database connection failed in test environment: ${errorMessage}`,
          );
          this.logger.warn("Running in degraded mode without database");
          this.isConnected = false;
          return;
        }

        if (attempt < maxRetries) {
          const delay = attempt * 2000; // 2 s, 4 s backoff
          this.logger.warn(
            `Database connection failed (attempt ${attempt}/${maxRetries}): ${errorMessage}. Retrying in ${delay}ms...`,
          );
          await new Promise((resolve) => setTimeout(resolve, delay));
        } else {
          // All retries exhausted — start in degraded mode instead of crashing.
          // The liveness probe will still pass; readyz will report not-ready until
          // the background reconnect loop succeeds.
          this.logger.error(
            `Database connection failed after ${maxRetries} attempts: ${errorMessage}. ` +
            "Starting in degraded mode. Background reconnect will retry every " +
            `${RECONNECT_INTERVAL_MS / 1000}s.`,
          );
          this.isConnected = false;
          this._scheduleReconnect();
        }
      }
    }
  }

  /** Schedule a background reconnect attempt */
  private _scheduleReconnect(): void {
    if (this.reconnectTimer !== null || this.isTestEnvironment) return;

    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null;
      // Wrap the async work and catch any unexpected rejection so the
      // Node.js process is never taken down by an unhandled promise.
      this._doReconnect().catch((err: unknown) => {
        const msg = err instanceof Error ? err.message : String(err);
        this.logger.error(`Unexpected error in background DB reconnect: ${msg}`);
        this._scheduleReconnect();
      });
    }, RECONNECT_INTERVAL_MS);
  }

  /** Perform a single reconnect attempt (called from the background timer). */
  private async _doReconnect(): Promise<void> {
    this.logger.log("Background DB reconnect attempt starting...");
    try {
      await this.$connect();
      this.isConnected = true;
      this.logger.log("Field Management Database reconnected successfully");

      try {
        await this.$queryRaw`CREATE EXTENSION IF NOT EXISTS postgis`;
      } catch {
        // non-fatal
      }
    } catch (error) {
      const msg = error instanceof Error ? error.message : String(error);
      this.logger.warn(`Background DB reconnect failed: ${msg}. Will retry in ${RECONNECT_INTERVAL_MS / 1000}s.`);
      this._scheduleReconnect(); // keep retrying
    }
  }

  async onModuleDestroy() {
    if (this.reconnectTimer !== null) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    if (this.isConnected) {
      await this.$disconnect();
      this.logger.log("Field Management Database disconnected");
    }
  }

  /**
   * Check if database is connected
   */
  isHealthy(): boolean {
    return this.isConnected;
  }

  /**
   * Get detailed connection status
   */
  async getConnectionStatus() {
    try {
      await this.$queryRaw`SELECT 1`;
      this.isConnected = true; // update flag on successful live check
      return {
        connected: true,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      this.isConnected = false;
      this.logger.error("Database connection check failed:", error);
      this._scheduleReconnect(); // trigger background reconnect if not already running
      return {
        connected: false,
        timestamp: new Date().toISOString(),
        error: error instanceof Error ? error.message : "Unknown error",
      };
    }
  }
}
