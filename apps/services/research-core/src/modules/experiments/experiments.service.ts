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

    // Validate date strings
    const startDate = new Date(dto.startDate);
    if (isNaN(startDate.getTime())) {
      throw new Error('Invalid startDate format');
    }

    let endDate: Date | null = null;
    if (dto.endDate) {
      endDate = new Date(dto.endDate);
      if (isNaN(endDate.getTime())) {
        throw new Error('Invalid endDate format');
      }
      // Ensure endDate is after startDate
      if (endDate <= startDate) {
        throw new Error('endDate must be after startDate');
      }
    }

    return this.prisma.experiment.create({
      data: {
        ...restDto,
        principalResearcherId: userId,
        startDate,
        endDate,
        metadata: metadata as Prisma.InputJsonValue | undefined,
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

    // Validate date strings if provided
    let validatedStartDate: Date | undefined;
    let validatedEndDate: Date | undefined;

    if (dto.startDate) {
      validatedStartDate = new Date(dto.startDate);
      if (isNaN(validatedStartDate.getTime())) {
        throw new Error('Invalid startDate format');
      }
    }

    if (dto.endDate) {
      validatedEndDate = new Date(dto.endDate);
      if (isNaN(validatedEndDate.getTime())) {
        throw new Error('Invalid endDate format');
      }
    }

    // If both dates are provided, ensure endDate is after startDate
    if (validatedStartDate && validatedEndDate && validatedEndDate <= validatedStartDate) {
      throw new Error('endDate must be after startDate');
    }

    return this.prisma.experiment.update({
      where: { id },
      data: {
        ...restDto,
        startDate: validatedStartDate,
        endDate: validatedEndDate,
        version: { increment: 1 },
        metadata: metadata !== undefined ? (metadata as Prisma.InputJsonValue) : undefined,
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
    // Use single query with _count aggregation and include last log
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
        logs: {
          orderBy: { logDate: 'desc' },
          take: 1,
          select: { logDate: true, title: true },
        },
      },
    });

    if (!experiment) {
      throw new NotFoundException(`Experiment ${id} not found`);
    }

    const lastLog = experiment.logs[0];

    return {
      ...experiment,
      statistics: {
        logsCount: experiment._count.logs,
        samplesCount: experiment._count.samples,
        lastLogDate: lastLog?.logDate,
        lastLogTitle: lastLog?.title,
      },
    };
  }
}
