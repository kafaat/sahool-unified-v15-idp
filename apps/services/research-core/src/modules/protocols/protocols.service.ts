import { Injectable, Logger, NotFoundException } from "@nestjs/common";
import { PrismaService } from "@/config/prisma.service";
import { Prisma } from "@prisma/client";
import { CreateProtocolDto, UpdateProtocolDto } from "./dto/protocol.dto";

@Injectable()
export class ProtocolsService {
  private readonly logger = new Logger(ProtocolsService.name);

  constructor(private readonly prisma: PrismaService) {}

  async create(dto: CreateProtocolDto) {
    this.logger.log(`Creating protocol: ${dto.name}`);

    const { variables, measurementSchedule, ...restDto } = dto;

    return this.prisma.researchProtocol.create({
      data: {
        ...restDto,
        approvedAt: dto.approvedAt ? new Date(dto.approvedAt) : null,
        variables: variables as Prisma.InputJsonValue | undefined,
        measurementSchedule: measurementSchedule as
          | Prisma.InputJsonValue
          | undefined,
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
    filters?: {
      page?: number;
      limit?: number;
    },
  ) {
    const page = filters?.page || 1;
    const limit = filters?.limit || 20;
    const skip = (page - 1) * limit;

    const where = { experimentId };

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

  async findOne(id: string) {
    const protocol = await this.prisma.researchProtocol.findUnique({
      where: { id },
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

  async update(id: string, dto: UpdateProtocolDto) {
    await this.findOne(id);

    const { variables, measurementSchedule, ...restDto } = dto;

    return this.prisma.researchProtocol.update({
      where: { id },
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

  async delete(id: string) {
    await this.findOne(id);

    return this.prisma.researchProtocol.delete({
      where: { id },
    });
  }

  async approve(id: string, approvedBy: string) {
    await this.findOne(id);

    return this.prisma.researchProtocol.update({
      where: { id },
      data: {
        approvedBy,
        approvedAt: new Date(),
      },
    });
  }
}
