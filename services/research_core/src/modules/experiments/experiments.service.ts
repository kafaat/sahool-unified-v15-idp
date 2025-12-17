import { Injectable, Logger, NotFoundException } from '@nestjs/common';
import { PrismaService } from '@/config/prisma.service';
import { Prisma } from '@prisma/client';
import { CreateExperimentDto, UpdateExperimentDto } from './dto/experiment.dto';

@Injectable()
export class ExperimentsService {
  private readonly logger = new Logger(ExperimentsService.name);

  constructor(private readonly prisma: PrismaService) {}

  async create(dto: CreateExperimentDto, userId: string) {
    this.logger.log(`Creating experiment: ${dto.title}`);

    const { metadata, ...restDto } = dto;

    return this.prisma.experiment.create({
      data: {
        ...restDto,
        principalResearcherId: userId,
        startDate: new Date(dto.startDate),
        endDate: dto.endDate ? new Date(dto.endDate) : undefined,
        metadata: metadata ? (metadata as Prisma.InputJsonValue) : Prisma.DbNull,
      },
    });
  }

  async findAll(filters?: {
    status?: string;
    researcherId?: string;
    farmId?: string;
    page?: number;
    limit?: number;
  }) {
    const page = filters?.page || 1;
    const limit = filters?.limit || 20;
    const skip = (page - 1) * limit;

    const where: any = {};

    if (filters?.status) {
      where.status = filters.status;
    }
    if (filters?.researcherId) {
      where.principalResearcherId = filters.researcherId;
    }
    if (filters?.farmId) {
      where.farmId = filters.farmId;
    }

    const [data, total] = await Promise.all([
      this.prisma.experiment.findMany({
        where,
        skip,
        take: limit,
        orderBy: { createdAt: 'desc' },
        include: {
          _count: {
            select: {
              protocols: true,
              plots: true,
              treatments: true,
              logs: true,
              samples: true,
            },
          },
        },
      }),
      this.prisma.experiment.count({ where }),
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
    const experiment = await this.prisma.experiment.findUnique({
      where: { id },
      include: {
        protocols: true,
        plots: true,
        treatments: true,
        collaborators: true,
        _count: {
          select: {
            logs: true,
            samples: true,
          },
        },
      },
    });

    if (!experiment) {
      throw new NotFoundException(`Experiment ${id} not found`);
    }

    return experiment;
  }

  async update(id: string, dto: UpdateExperimentDto) {
    await this.findOne(id);

    const { metadata, ...restDto } = dto;

    return this.prisma.experiment.update({
      where: { id },
      data: {
        ...restDto,
        startDate: dto.startDate ? new Date(dto.startDate) : undefined,
        endDate: dto.endDate ? new Date(dto.endDate) : undefined,
        metadata: metadata !== undefined
          ? (metadata ? (metadata as Prisma.InputJsonValue) : Prisma.DbNull)
          : undefined,
        version: { increment: 1 },
      },
    });
  }

  async delete(id: string) {
    await this.findOne(id);

    return this.prisma.experiment.delete({
      where: { id },
    });
  }

  async lock(id: string, userId: string) {
    await this.findOne(id);

    return this.prisma.experiment.update({
      where: { id },
      data: {
        status: 'locked',
        lockedAt: new Date(),
        lockedBy: userId,
      },
    });
  }

  async getSummary(id: string) {
    const experiment = await this.findOne(id);

    const [logsCount, samplesCount, lastLog] = await Promise.all([
      this.prisma.researchDailyLog.count({
        where: { experimentId: id },
      }),
      this.prisma.labSample.count({
        where: { experimentId: id },
      }),
      this.prisma.researchDailyLog.findFirst({
        where: { experimentId: id },
        orderBy: { logDate: 'desc' },
        select: { logDate: true, title: true },
      }),
    ]);

    return {
      ...experiment,
      statistics: {
        logsCount,
        samplesCount,
        lastLogDate: lastLog?.logDate,
        lastLogTitle: lastLog?.title,
      },
    };
  }
}
