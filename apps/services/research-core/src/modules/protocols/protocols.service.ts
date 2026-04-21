import { Injectable, Logger, NotFoundException } from "@nestjs/common";
import { PrismaService } from "@/config/prisma.service";
import { Prisma } from "../../../prisma/generated/client";
import { CreateProtocolDto, UpdateProtocolDto } from "./dto/protocol.dto";
import { MAX_PAGE_SIZE, DEFAULT_PAGE_SIZE } from "../../utils/db-utils";

@Injectable()
export class ProtocolsService {
  private readonly logger = new Logger(ProtocolsService.name);

  constructor(private readonly prisma: PrismaService) {}

  /**
   * Sanitize input for safe logging (prevents log injection)
   */
  private sanitizeForLog(input: string): string {
    if (typeof input !== "string") return String(input);
    return input.replace(/[\r\n]/g, "").replace(/[\x00-\x1F\x7F]/g, "").slice(0, 100);
  }

  async create(dto: CreateProtocolDto, tenantId: string) {
    this.logger.log("Creating protocol", { name: this.sanitizeForLog(dto.name) });

    const { variables, measurementSchedule, ...restDto } = dto;

    return this.prisma.researchProtocol.create({
      data: {
        ...restDto,
        approvedAt: dto.approvedAt ? new Date(dto.approvedAt) : null,
        variables: variables as Prisma.InputJsonValue | undefined,
        measurementSchedule: measurementSchedule as
          | Prisma.InputJsonValue
          | undefined,
        tenantId,
      },
      include: {
        experiment: {
          select: {
            id: true,
            title: true,
            status: true,
          },
        },
      },
    });
  }

  async findAll(
    experimentId: string,
    tenantId: string,
    filters?: {
      page?: number;
      limit?: number;
    },
  ) {
    const page = filters?.page || 1;
    // Enforce maximum page size to prevent memory exhaustion
    const limit = Math.min(filters?.limit || DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE);
    const skip = (page - 1) * limit;

    const where = { experimentId, tenantId };

    const [data, total] = await Promise.all([
      this.prisma.researchProtocol.findMany({
        where,
        skip,
        take: limit,
        orderBy: { createdAt: "desc" },
        include: {
          experiment: {
            select: {
              id: true,
              title: true,
              status: true,
            },
          },
        },
      }),
      this.prisma.researchProtocol.count({ where }),
    ]);

    return {
      data,
      meta: {
        total,
        page,
        limit,
        totalPages: Math.ceil(total / limit),
      },
    };
  }

  async findOne(id: string, tenantId: string) {
    const protocol = await this.prisma.researchProtocol.findFirst({
      where: { id, tenantId },
      include: {
        experiment: {
          select: {
            id: true,
            title: true,
            titleAr: true,
            status: true,
            principalResearcherId: true,
          },
        },
      },
    });

    if (!protocol) {
      throw new NotFoundException(`Protocol ${id} not found`);
    }

    return protocol;
  }

  async update(id: string, dto: UpdateProtocolDto, tenantId: string) {
    await this.findOne(id, tenantId);

    const { variables, measurementSchedule, ...restDto } = dto;

    return this.prisma.researchProtocol.update({
      where: { id_tenantId: { id, tenantId } },
      data: {
        ...restDto,
        approvedAt: dto.approvedAt ? new Date(dto.approvedAt) : undefined,
        variables:
          variables !== undefined
            ? (variables as Prisma.InputJsonValue)
            : undefined,
        measurementSchedule:
          measurementSchedule !== undefined
            ? (measurementSchedule as Prisma.InputJsonValue)
            : undefined,
      },
      include: {
        experiment: {
          select: {
            id: true,
            title: true,
            status: true,
          },
        },
      },
    });
  }

  async delete(id: string, tenantId: string) {
    await this.findOne(id, tenantId);

    return this.prisma.researchProtocol.delete({
      where: { id_tenantId: { id, tenantId } },
    });
  }

  async approve(id: string, approvedBy: string, tenantId: string) {
    await this.findOne(id, tenantId);

    return this.prisma.researchProtocol.update({
      where: { id_tenantId: { id, tenantId } },
      data: {
        approvedBy,
        approvedAt: new Date(),
      },
    });
  }
}
