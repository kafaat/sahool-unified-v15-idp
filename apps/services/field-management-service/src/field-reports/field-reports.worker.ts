/**
 * Field Reports Worker
 * عامل توليد التقارير في الخلفية
 *
 * Polls `field_reports` for rows in status='pending' every
 * REPORTS_POLL_MS (default 10s) and delegates rendering to
 * FieldReportsService.renderReport(). Bounded retries so a permanently
 * broken render doesn't poison the queue.
 */

import {
  Injectable,
  Logger,
  OnModuleInit,
  OnModuleDestroy,
} from "@nestjs/common";
import { PrismaService } from "../prisma/prisma.service";
import { FieldReportsService } from "./field-reports.service";

const POLL_INTERVAL_MS = Number(process.env.REPORTS_POLL_MS ?? 10000);
const BATCH_SIZE = Number(process.env.REPORTS_BATCH_SIZE ?? 5);
const MAX_ATTEMPTS = Number(process.env.REPORTS_MAX_ATTEMPTS ?? 5);

@Injectable()
export class FieldReportsWorker implements OnModuleInit, OnModuleDestroy {
  private readonly logger = new Logger(FieldReportsWorker.name);
  private timer: NodeJS.Timeout | null = null;
  private isProcessing = false;

  constructor(
    private readonly prisma: PrismaService,
    private readonly reports: FieldReportsService,
  ) {}

  onModuleInit() {
    if (process.env.REPORTS_WORKER_ENABLED === "false") {
      this.logger.log("Reports worker disabled via env");
      return;
    }
    this.timer = setInterval(
      () => this.tick().catch((e) => this.logger.error(`Tick error: ${e}`)),
      POLL_INTERVAL_MS,
    );
    this.logger.log(
      `Reports worker started (interval=${POLL_INTERVAL_MS}ms, batch=${BATCH_SIZE})`,
    );
  }

  onModuleDestroy() {
    if (this.timer) clearInterval(this.timer);
  }

  async tick(): Promise<void> {
    if (this.isProcessing) return;
    this.isProcessing = true;
    try {
      const pending = await this.prisma.fieldReport.findMany({
        where: {
          status: "pending",
          renderAttempts: { lt: MAX_ATTEMPTS },
        },
        orderBy: { createdAt: "asc" },
        take: BATCH_SIZE,
        select: { id: true },
      });
      if (pending.length === 0) return;

      for (const p of pending) {
        try {
          await this.reports.renderReport(p.id);
        } catch (e) {
          this.logger.warn(
            `Render error for ${p.id}: ${
              e instanceof Error ? e.message : e
            }`,
          );
        }
      }
    } finally {
      this.isProcessing = false;
    }
  }
}
