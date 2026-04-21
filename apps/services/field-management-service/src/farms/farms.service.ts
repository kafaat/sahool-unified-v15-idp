/**
 * Farms Service - SAHOOL Field Management
 * خدمة المزارع
 *
 * Tenant-scoped CRUD for farms. All queries enforce tenant isolation by
 * injecting `tenantId` into every `where` clause — the controller is
 * responsible for extracting the JWT `tid` claim and passing it here.
 */

import {
  Injectable,
  Logger,
  NotFoundException,
} from "@nestjs/common";
import { PrismaService } from "../prisma/prisma.service";
import { CreateFarmDto, FarmStatus } from "./dto/create-farm.dto";
import { UpdateFarmDto } from "./dto/update-farm.dto";
import { QueryFarmsDto } from "./dto/query-farms.dto";

// Convert Prisma Decimal fields to plain numbers for UI consumption.
function toNumber(value: any): number | undefined {
  if (value === null || value === undefined) return undefined;
  if (typeof value === "number") return value;
  if (typeof value === "object" && typeof value.toNumber === "function") {
    return value.toNumber();
  }
  const n = Number(value);
  return Number.isFinite(n) ? n : undefined;
}

export interface FarmResponse {
  id: string;
  name: string;
  nameAr: string | null;
  tenantId: string;
  ownerId: string | null;
  owner: string | null;
  region: string | null;
  regionAr: string | null;
  waterSource: string | null;
  waterSourceAr: string | null;
  workersCount: number;
  status: string;
  totalAreaHectares?: number;
  cultivatedAreaHectares?: number;
  location: string | null;
  locationAr: string | null;
  address: string | null;
  phone: string | null;
  email: string | null;
  isDeleted: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export interface FarmStats {
  total: number;
  active: number;
  inactive: number;
  archived: number;
  totalAreaHectares: number;
  totalWorkers: number;
}

/**
 * Field selection used across all list / get queries. We deliberately
 * exclude the PostGIS `locationGeom` / `boundary` geometry columns (they
 * are not plain-serialisable and not used by the Admin/Web UIs).
 *
 * NOTE: The Prisma column names `locationLabel` / `locationLabelAr` differ
 * from the API-facing DTO names `location` / `locationAr`. Mapping happens
 * in `serializeFarm` (read) and in `create`/`update` (write). See the
 * schema.prisma comment on the Farm model for why the rename was needed.
 */
const FARM_SELECT = {
  id: true,
  name: true,
  nameAr: true,
  tenantId: true,
  ownerId: true,
  owner: true,
  region: true,
  regionAr: true,
  waterSource: true,
  waterSourceAr: true,
  workersCount: true,
  status: true,
  totalAreaHectares: true,
  cultivatedAreaHectares: true,
  locationLabel: true,
  locationLabelAr: true,
  address: true,
  phone: true,
  email: true,
  isDeleted: true,
  createdAt: true,
  updatedAt: true,
} as const;

function serializeFarm(f: any): FarmResponse {
  return {
    id: f.id,
    name: f.name,
    nameAr: f.nameAr ?? null,
    tenantId: f.tenantId,
    ownerId: f.ownerId ?? null,
    owner: f.owner ?? null,
    region: f.region ?? null,
    regionAr: f.regionAr ?? null,
    waterSource: f.waterSource ?? null,
    waterSourceAr: f.waterSourceAr ?? null,
    workersCount: typeof f.workersCount === "number" ? f.workersCount : 0,
    status: f.status ?? "active",
    totalAreaHectares: toNumber(f.totalAreaHectares),
    cultivatedAreaHectares: toNumber(f.cultivatedAreaHectares),
    // Prisma field → DTO field rename (see FARM_SELECT comment above).
    location: f.locationLabel ?? null,
    locationAr: f.locationLabelAr ?? null,
    address: f.address ?? null,
    phone: f.phone ?? null,
    email: f.email ?? null,
    isDeleted: !!f.isDeleted,
    createdAt: f.createdAt,
    updatedAt: f.updatedAt,
  };
}

@Injectable()
export class FarmsService {
  private readonly logger = new Logger(FarmsService.name);

  constructor(private readonly prisma: PrismaService) {}

  /**
   * Create a new farm for the authenticated tenant.
   */
  async create(tenantId: string, dto: CreateFarmDto): Promise<FarmResponse> {
    const created = await this.prisma.farm.create({
      data: {
        tenantId,
        name: dto.name,
        nameAr: dto.nameAr,
        ownerId: dto.ownerId,
        owner: dto.owner,
        region: dto.region,
        regionAr: dto.regionAr,
        waterSource: dto.waterSource,
        waterSourceAr: dto.waterSourceAr,
        workersCount: dto.workersCount ?? 0,
        status: dto.status ?? FarmStatus.ACTIVE,
        totalAreaHectares: dto.totalAreaHectares,
        cultivatedAreaHectares: dto.cultivatedAreaHectares,
        // DTO field → Prisma field rename (see FARM_SELECT comment above).
        locationLabel: dto.location,
        locationLabelAr: dto.locationAr,
        address: dto.address,
        phone: dto.phone,
        email: dto.email,
      },
      select: FARM_SELECT,
    });
    this.logger.log(`Farm created: ${created.id} (tenant=${tenantId})`);
    return serializeFarm(created);
  }

  /**
   * List farms with pagination & filtering.
   * Always scoped to the authenticated tenant.
   */
  async findAll(
    tenantId: string,
    query: QueryFarmsDto,
  ): Promise<{
    farms: FarmResponse[];
    total: number;
    page: number;
    limit: number;
  }> {
    const page = query.page && query.page > 0 ? query.page : 1;
    const limit = Math.min(Math.max(query.limit ?? 20, 1), 100);
    const skip = (page - 1) * limit;

    const where: any = {
      tenantId,
      isDeleted: false,
    };
    if (query.status) where.status = query.status;
    if (query.region) where.region = query.region;
    if (query.search) {
      where.OR = [
        { name: { contains: query.search, mode: "insensitive" } },
        { nameAr: { contains: query.search, mode: "insensitive" } },
        { locationLabel: { contains: query.search, mode: "insensitive" } },
        { locationLabelAr: { contains: query.search, mode: "insensitive" } },
      ];
    }

    const [rows, total] = await Promise.all([
      this.prisma.farm.findMany({
        where,
        select: FARM_SELECT,
        skip,
        take: limit,
        orderBy: { createdAt: "desc" },
      }),
      this.prisma.farm.count({ where }),
    ]);

    return {
      farms: rows.map(serializeFarm),
      total,
      page,
      limit,
    };
  }

  /**
   * Get a single farm by ID, enforcing tenant ownership.
   */
  async findById(id: string, tenantId: string): Promise<FarmResponse> {
    const farm = await this.prisma.farm.findFirst({
      where: { id, tenantId, isDeleted: false },
      select: FARM_SELECT,
    });

    if (!farm) {
      throw new NotFoundException({
        message: "Farm not found",
        messageAr: "المزرعة غير موجودة",
      });
    }

    return serializeFarm(farm);
  }

  /**
   * Update an existing farm. Tenant ownership is enforced via the `where`
   * clause, so cross-tenant updates silently return 404.
   */
  async update(
    id: string,
    tenantId: string,
    dto: UpdateFarmDto,
  ): Promise<FarmResponse> {
    // Verify existence & ownership first so we return a bilingual 404
    // instead of Prisma's opaque RecordNotFound error.
    const existing = await this.prisma.farm.findFirst({
      where: { id, tenantId, isDeleted: false },
      select: { id: true },
    });
    if (!existing) {
      throw new NotFoundException({
        message: "Farm not found",
        messageAr: "المزرعة غير موجودة",
      });
    }

    const updated = await this.prisma.farm.update({
      where: { id_tenantId: { id, tenantId } },
      data: {
        ...(dto.name !== undefined && { name: dto.name }),
        ...(dto.nameAr !== undefined && { nameAr: dto.nameAr }),
        ...(dto.ownerId !== undefined && { ownerId: dto.ownerId }),
        ...(dto.owner !== undefined && { owner: dto.owner }),
        ...(dto.region !== undefined && { region: dto.region }),
        ...(dto.regionAr !== undefined && { regionAr: dto.regionAr }),
        ...(dto.waterSource !== undefined && { waterSource: dto.waterSource }),
        ...(dto.waterSourceAr !== undefined && {
          waterSourceAr: dto.waterSourceAr,
        }),
        ...(dto.workersCount !== undefined && {
          workersCount: dto.workersCount,
        }),
        ...(dto.status !== undefined && { status: dto.status }),
        ...(dto.totalAreaHectares !== undefined && {
          totalAreaHectares: dto.totalAreaHectares,
        }),
        ...(dto.cultivatedAreaHectares !== undefined && {
          cultivatedAreaHectares: dto.cultivatedAreaHectares,
        }),
        // DTO field → Prisma field rename (see FARM_SELECT comment above).
        ...(dto.location !== undefined && { locationLabel: dto.location }),
        ...(dto.locationAr !== undefined && {
          locationLabelAr: dto.locationAr,
        }),
        ...(dto.address !== undefined && { address: dto.address }),
        ...(dto.phone !== undefined && { phone: dto.phone }),
        ...(dto.email !== undefined && { email: dto.email }),
      },
      select: FARM_SELECT,
    });

    this.logger.log(`Farm updated: ${id} (tenant=${tenantId})`);
    return serializeFarm(updated);
  }

  /**
   * Soft-delete a farm by setting `isDeleted = true`. Falls through to a
   * hard delete if the row has already been soft-deleted (belt-and-braces).
   */
  async delete(id: string, tenantId: string): Promise<void> {
    const existing = await this.prisma.farm.findFirst({
      where: { id, tenantId },
      select: { id: true, isDeleted: true },
    });
    if (!existing) {
      throw new NotFoundException({
        message: "Farm not found",
        messageAr: "المزرعة غير موجودة",
      });
    }

    await this.prisma.farm.update({
      where: { id_tenantId: { id, tenantId } },
      data: {
        isDeleted: true,
        status: "archived",
      },
    });

    this.logger.log(`Farm soft-deleted: ${id} (tenant=${tenantId})`);
  }

  /**
   * Aggregate stats for the authenticated tenant.
   */
  async getStats(tenantId: string): Promise<FarmStats> {
    const [total, active, inactive, archived, aggregate] = await Promise.all([
      this.prisma.farm.count({
        where: { tenantId, isDeleted: false },
      }),
      this.prisma.farm.count({
        where: { tenantId, isDeleted: false, status: "active" },
      }),
      this.prisma.farm.count({
        where: { tenantId, isDeleted: false, status: "inactive" },
      }),
      this.prisma.farm.count({
        where: { tenantId, status: "archived" },
      }),
      this.prisma.farm.aggregate({
        where: { tenantId, isDeleted: false },
        _sum: {
          totalAreaHectares: true,
          workersCount: true,
        },
      }),
    ]);

    return {
      total,
      active,
      inactive,
      archived,
      totalAreaHectares: toNumber(aggregate._sum.totalAreaHectares) ?? 0,
      totalWorkers: toNumber(aggregate._sum.workersCount) ?? 0,
    };
  }
}
