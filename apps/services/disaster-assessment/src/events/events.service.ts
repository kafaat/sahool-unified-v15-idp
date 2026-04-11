// ═══════════════════════════════════════════════════════════════════════════════
// Disaster Events Service - خدمة أحداث الكوارث
// ═══════════════════════════════════════════════════════════════════════════════
//
// Thin wrapper around the existing DisasterReport storage used by the
// /api/v1/disasters/events/* endpoints. We intentionally reuse the underlying
// `disaster_reports` Prisma model instead of duplicating logic or storage.
//
// Optimistic locking:
//   The logical "version" of an event is derived from its updatedAt timestamp
//   expressed as a millisecond epoch. Clients must include the version they
//   last observed when calling PUT; the service throws ConflictException on
//   mismatch. This keeps the existing schema untouched while still providing
//   the optimistic-locking contract expected by the frontend.
// ═══════════════════════════════════════════════════════════════════════════════

import {
  Injectable,
  Logger,
  ConflictException,
  NotFoundException,
} from "@nestjs/common";
import { PrismaService } from "../prisma/prisma.service";
import { DisasterType, Severity } from "../disaster/disaster.dto";
import {
  CreateDisasterEventDto,
  DisasterEventStatus,
  ListEventsQueryDto,
  UpdateDisasterEventDto,
  UpdateEventStatusDto,
} from "./events.dto";

// Prisma enum values as string constants (mirrors disaster.service.ts to avoid
// depending on the generated @prisma/client enums during Docker builds).
const PrismaDisasterStatus = {
  reported: "reported",
  verified: "verified",
  active: "active",
  monitoring: "monitoring",
  resolved: "resolved",
  archived: "archived",
} as const;

type EventRow = {
  id: string;
  type: string;
  severity: string;
  status: string;
  title: string;
  titleAr: string | null;
  description: string | null;
  descriptionAr?: string | null;
  governorate: string;
  district: string | null;
  location: unknown;
  affectedRadiusKm: number | null;
  affectedFieldsCount: number;
  totalAffectedAreaHectares: number | null;
  reportedBy: string;
  startDate: Date | null;
  endDate: Date | null;
  createdAt: Date;
  updatedAt: Date;
};

@Injectable()
export class EventsService {
  private readonly logger = new Logger(EventsService.name);

  constructor(private readonly prisma: PrismaService) {}

  // ─────────────────────────────────────────────────────────────────────────
  // Internal helpers
  // ─────────────────────────────────────────────────────────────────────────

  private toVersion(row: { updatedAt: Date }): number {
    return row.updatedAt.getTime();
  }

  private serialize(row: EventRow) {
    return {
      id: row.id,
      type: row.type,
      severity: row.severity,
      status: row.status,
      title: row.title,
      titleAr: row.titleAr,
      description: row.description,
      descriptionAr: row.descriptionAr ?? null,
      governorate: row.governorate,
      district: row.district,
      location: row.location,
      affectedRadiusKm: row.affectedRadiusKm,
      affectedFieldsCount: row.affectedFieldsCount,
      totalAffectedAreaHectares: row.totalAffectedAreaHectares,
      reportedBy: row.reportedBy,
      reportedAt: row.createdAt.toISOString(),
      startDate: row.startDate?.toISOString() ?? null,
      endDate: row.endDate?.toISOString() ?? null,
      updatedAt: row.updatedAt.toISOString(),
      version: this.toVersion(row),
    };
  }

  // ─────────────────────────────────────────────────────────────────────────
  // List events
  // ─────────────────────────────────────────────────────────────────────────

  async listEvents(tenantId: string, query: ListEventsQueryDto) {
    const where: Record<string, unknown> = { tenantId };

    if (query.type) where.type = query.type;
    if (query.severity) where.severity = query.severity;
    if (query.status) where.status = query.status;
    if (query.governorate) where.governorate = query.governorate;

    if (query.fromDate || query.toDate) {
      const createdAt: Record<string, Date> = {};
      if (query.fromDate) createdAt.gte = new Date(query.fromDate);
      if (query.toDate) createdAt.lte = new Date(query.toDate);
      where.createdAt = createdAt;
    }

    const limit = query.limit ?? 50;
    const offset = query.offset ?? 0;

    const [items, total] = await Promise.all([
      this.prisma.disasterReport.findMany({
        where,
        orderBy: { createdAt: "desc" },
        take: limit,
        skip: offset,
      }),
      this.prisma.disasterReport.count({ where }),
    ]);

    return {
      total,
      limit,
      offset,
      events: items.map((row: unknown) => this.serialize(row as EventRow)),
    };
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Get event by ID
  // ─────────────────────────────────────────────────────────────────────────

  async getEvent(id: string, tenantId: string) {
    const row = await this.prisma.disasterReport.findFirst({
      where: { id, tenantId },
    });
    if (!row) {
      throw new NotFoundException({
        error: "Event not found",
        errorAr: "الحدث غير موجود",
      });
    }
    return this.serialize(row as unknown as EventRow);
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Create event
  // ─────────────────────────────────────────────────────────────────────────

  async createEvent(dto: CreateDisasterEventDto, tenantId: string) {
    const row = await this.prisma.disasterReport.create({
      data: {
        type: dto.type as unknown as DisasterType,
        severity: dto.severity as unknown as Severity,
        status: PrismaDisasterStatus.active,
        title: dto.title,
        titleAr: dto.titleAr ?? dto.title,
        description: dto.description ?? null,
        descriptionAr: dto.descriptionAr ?? null,
        governorate: dto.governorate,
        district: dto.district ?? null,
        location: dto.location as unknown as object,
        affectedRadiusKm: dto.affectedRadiusKm ?? null,
        startDate: dto.startDate ? new Date(dto.startDate) : null,
        images: (dto.images ?? null) as unknown as object | null,
        reportedBy: dto.reportedBy ?? "system",
        tenantId,
        affectedFieldsCount: 0,
        totalAffectedAreaHectares: 0,
        totalEstimatedLossYER: BigInt(0),
      } as Record<string, unknown>,
    });

    this.logger.log(`Created disaster event ${row.id} for tenant ${tenantId}`);
    return this.serialize(row as unknown as EventRow);
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Update event (optimistic locking via version == updatedAt ms)
  // ─────────────────────────────────────────────────────────────────────────

  async updateEvent(
    id: string,
    tenantId: string,
    dto: UpdateDisasterEventDto,
  ) {
    const existing = await this.prisma.disasterReport.findFirst({
      where: { id, tenantId },
    });
    if (!existing) {
      throw new NotFoundException({
        error: "Event not found",
        errorAr: "الحدث غير موجود",
      });
    }

    const currentVersion = this.toVersion(existing as { updatedAt: Date });
    if (dto.version !== currentVersion) {
      throw new ConflictException({
        error: "Version conflict",
        errorAr: "تعارض الإصدار",
        currentVersion,
        providedVersion: dto.version,
      });
    }

    const data: Record<string, unknown> = {};
    if (dto.title !== undefined) data.title = dto.title;
    if (dto.titleAr !== undefined) data.titleAr = dto.titleAr;
    if (dto.description !== undefined) data.description = dto.description;
    if (dto.descriptionAr !== undefined) data.descriptionAr = dto.descriptionAr;
    if (dto.severity !== undefined) data.severity = dto.severity;
    if (dto.status !== undefined) data.status = dto.status;
    if (dto.affectedRadiusKm !== undefined) {
      data.affectedRadiusKm = dto.affectedRadiusKm;
    }
    if (dto.endDate !== undefined) data.endDate = new Date(dto.endDate);

    const updated = await this.prisma.disasterReport.update({
      where: { id },
      data,
    });

    return this.serialize(updated as unknown as EventRow);
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Update status (status-only shortcut)
  // ─────────────────────────────────────────────────────────────────────────

  async updateStatus(
    id: string,
    tenantId: string,
    dto: UpdateEventStatusDto,
  ) {
    const existing = await this.prisma.disasterReport.findFirst({
      where: { id, tenantId },
    });
    if (!existing) {
      throw new NotFoundException({
        error: "Event not found",
        errorAr: "الحدث غير موجود",
      });
    }

    const updated = await this.prisma.disasterReport.update({
      where: { id },
      data: {
        status: dto.status,
        ...(dto.status === DisasterEventStatus.RESOLVED
          ? { resolvedAt: new Date() }
          : {}),
      },
    });

    if (dto.note) {
      this.logger.log(
        `Event ${id} status -> ${dto.status} (note: ${dto.note})`,
      );
    }

    return this.serialize(updated as unknown as EventRow);
  }
}
