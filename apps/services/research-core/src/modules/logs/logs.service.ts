import {
  Injectable,
  Logger,
  NotFoundException,
  BadRequestException,
} from "@nestjs/common";
import { PrismaService } from "@/config/prisma.service";
import { Prisma } from "@prisma/client";
import { SignatureService } from "@/core/services/signature.service";
import { CreateLogDto, UpdateLogDto, SyncLogDto } from "./dto/log.dto";

@Injectable()
export class LogsService {
  private readonly logger = new Logger(LogsService.name);

  constructor(
    private readonly prisma: PrismaService,
    private readonly signatureService: SignatureService,
  ) {}

  async create(dto: CreateLogDto, userId: string) {
    this.logger.log(
      `Creating research log for experiment: ${dto.experimentId}`,
    );

    // Generate hash for data integrity
    const hash = this.signatureService.hashResearchLog({
      experimentId: dto.experimentId,
      plotId: dto.plotId,
      logDate: new Date(dto.logDate),
      category: dto.category,
      notes: dto.notes,
      measurements: dto.measurements,
      recordedBy: userId,
    });

    return this.prisma.researchDailyLog.create({
      data: {
        experimentId: dto.experimentId,
        plotId: dto.plotId,
        treatmentId: dto.treatmentId,
        logDate: new Date(dto.logDate),
        logTime: dto.logTime,
        category: dto.category,
        title: dto.title,
        titleAr: dto.titleAr,
        notes: dto.notes,
        notesAr: dto.notesAr,
        measurements: (dto.measurements || {}) as Prisma.InputJsonValue,
        weatherConditions: (dto.weatherConditions ||
          {}) as Prisma.InputJsonValue,
        photos: dto.photos || [],
        attachments: dto.attachments || [],
        recordedBy: userId,
        deviceId: dto.deviceId,
        offlineId: dto.offlineId,
        hash,
      },
    });
  }

  async findAll(
    experimentId: string,
    filters?: {
      plotId?: string;
      category?: string;
      startDate?: string;
      endDate?: string;
      page?: number;
      limit?: number;
    },
  ) {
    const page = filters?.page || 1;
    const limit = filters?.limit || 50;
    const skip = (page - 1) * limit;

    const where: any = { experimentId };

    if (filters?.plotId) where.plotId = filters.plotId;
    if (filters?.category) where.category = filters.category;
    if (filters?.startDate || filters?.endDate) {
      where.logDate = {};
      if (filters.startDate) where.logDate.gte = new Date(filters.startDate);
      if (filters.endDate) where.logDate.lte = new Date(filters.endDate);
    }

    const [data, total] = await Promise.all([
      this.prisma.researchDailyLog.findMany({
        where,
        skip,
        take: limit,
        orderBy: [{ logDate: "desc" }, { logTime: "desc" }],
        include: {
          plot: { select: { plotCode: true, name: true } },
          treatment: { select: { treatmentCode: true, name: true } },
        },
      }),
      this.prisma.researchDailyLog.count({ where }),
    ]);

    return {
      data,
      meta: { total, page, limit, totalPages: Math.ceil(total / limit) },
    };
  }

  async findOne(id: string) {
    const log = await this.prisma.researchDailyLog.findUnique({
      where: { id },
      include: {
        experiment: { select: { title: true, status: true } },
        plot: true,
        treatment: true,
      },
    });

    if (!log) {
      throw new NotFoundException(`Log ${id} not found`);
    }

    return log;
  }

  async update(id: string, dto: UpdateLogDto, userId: string) {
    const existing = await this.findOne(id);

    // Regenerate hash if data fields changed
    const hash = this.signatureService.hashResearchLog({
      experimentId: existing.experimentId,
      plotId: dto.plotId ?? existing.plotId ?? undefined,
      logDate: dto.logDate ? new Date(dto.logDate) : existing.logDate,
      category: dto.category || existing.category,
      notes: dto.notes ?? existing.notes ?? undefined,
      measurements:
        dto.measurements ?? (existing.measurements as Record<string, unknown>),
      recordedBy: userId,
    });

    const { experimentId, measurements, weatherConditions, ...restDto } = dto;

    return this.prisma.researchDailyLog.update({
      where: { id },
      data: {
        ...restDto,
        logDate: dto.logDate ? new Date(dto.logDate) : undefined,
        measurements:
          measurements !== undefined
            ? (measurements as Prisma.InputJsonValue)
            : undefined,
        weatherConditions:
          weatherConditions !== undefined
            ? (weatherConditions as Prisma.InputJsonValue)
            : undefined,
        hash,
      },
    });
  }

  async delete(id: string) {
    await this.findOne(id);
    return this.prisma.researchDailyLog.delete({ where: { id } });
  }

  /**
   * Sync offline logs
   * مزامنة السجلات غير المتصلة
   */
  async syncOfflineLogs(logs: SyncLogDto[], userId: string) {
    const results = {
      synced: [] as string[],
      skipped: [] as string[],
      failed: [] as { offlineId: string; error: string }[],
    };

    for (const log of logs) {
      try {
        // Check if already synced
        const existing = await this.prisma.researchDailyLog.findFirst({
          where: { offlineId: log.offlineId },
        });

        if (existing) {
          results.skipped.push(log.offlineId);
          continue;
        }

        // Verify experiment exists
        const experiment = await this.prisma.experiment.findUnique({
          where: { id: log.experimentId },
          select: { id: true, status: true },
        });

        if (!experiment) {
          results.failed.push({
            offlineId: log.offlineId,
            error: "Experiment not found",
          });
          continue;
        }

        if (experiment.status === "locked") {
          results.failed.push({
            offlineId: log.offlineId,
            error: "Experiment is locked",
          });
          continue;
        }

        // Create log
        await this.create(
          {
            ...log,
            offlineId: log.offlineId,
          },
          userId,
        );

        // Update sync timestamp
        await this.prisma.researchDailyLog.updateMany({
          where: { offlineId: log.offlineId },
          data: { syncedAt: new Date() },
        });

        results.synced.push(log.offlineId);
      } catch (error) {
        results.failed.push({
          offlineId: log.offlineId,
          error: error.message,
        });
      }
    }

    this.logger.log(
      `Sync completed: ${results.synced.length} synced, ${results.skipped.length} skipped, ${results.failed.length} failed`,
    );

    return results;
  }

  /**
   * Verify log integrity
   * التحقق من سلامة السجل
   */
  async verifyLogIntegrity(
    id: string,
  ): Promise<{ isValid: boolean; message: string }> {
    const log = await this.findOne(id);

    const expectedHash = this.signatureService.hashResearchLog({
      experimentId: log.experimentId,
      plotId: log.plotId ?? undefined,
      logDate: log.logDate,
      category: log.category,
      notes: log.notes ?? undefined,
      measurements: log.measurements as Record<string, unknown>,
      recordedBy: log.recordedBy,
    });

    if (log.hash !== expectedHash) {
      return {
        isValid: false,
        message:
          "Data integrity check failed - log data may have been modified",
      };
    }

    return {
      isValid: true,
      message: "Log integrity verified",
    };
  }
}
