import { Injectable, Logger, NotFoundException } from '@nestjs/common';
import { PrismaService } from '@/config/prisma.service';
import { Prisma } from '@prisma/client';
import { CreateTreatmentDto, UpdateTreatmentDto } from './dto/treatment.dto';

@Injectable()
export class TreatmentsService {
  private readonly logger = new Logger(TreatmentsService.name);

  constructor(private readonly prisma: PrismaService) {}

  async create(dto: CreateTreatmentDto) {
    this.logger.log(`Creating treatment: ${dto.name}`);

    const { parameters, ...restDto } = dto;

    return this.prisma.treatment.create({
      data: {
        ...restDto,
        startDate: dto.startDate ? new Date(dto.startDate) : null,
        endDate: dto.endDate ? new Date(dto.endDate) : null,
        parameters: parameters as Prisma.InputJsonValue | undefined,
      },
      include: {
        experiment: {
          select: {
            id: true,
            title: true,
            status: true,
          },
        },
        plot: {
          select: {
            id: true,
            plotCode: true,
            name: true,
          },
        },
      },
    });
  }

  async findAll(
    experimentId: string,
    filters?: {
      plotId?: string;
      type?: string;
      isControl?: boolean;
      page?: number;
      limit?: number;
    },
  ) {
    const page = filters?.page || 1;
    const limit = filters?.limit || 20;
    const skip = (page - 1) * limit;

    const where: any = { experimentId };

    if (filters?.plotId) {
      where.plotId = filters.plotId;
    }
    if (filters?.type) {
      where.type = filters.type;
    }
    if (filters?.isControl !== undefined) {
      where.isControl = filters.isControl;
    }

    const [data, total] = await Promise.all([
      this.prisma.treatment.findMany({
        where,
        skip,
        take: limit,
        orderBy: { createdAt: 'desc' },
        include: {
          experiment: {
            select: {
              id: true,
              title: true,
              status: true,
            },
          },
          plot: {
            select: {
              id: true,
              plotCode: true,
              name: true,
            },
          },
          _count: {
            select: {
              logs: true,
            },
          },
        },
      }),
      this.prisma.treatment.count({ where }),
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
    const treatment = await this.prisma.treatment.findUnique({
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
        plot: {
          select: {
            id: true,
            plotCode: true,
            name: true,
            nameAr: true,
            areaSqm: true,
          },
        },
        _count: {
          select: {
            logs: true,
          },
        },
      },
    });

    if (!treatment) {
      throw new NotFoundException(`Treatment ${id} not found`);
    }

    return treatment;
  }

  async update(id: string, dto: UpdateTreatmentDto) {
    await this.findOne(id);

    const { parameters, ...restDto } = dto;

    return this.prisma.treatment.update({
      where: { id },
      data: {
        ...restDto,
        startDate: dto.startDate ? new Date(dto.startDate) : undefined,
        endDate: dto.endDate ? new Date(dto.endDate) : undefined,
        parameters: parameters !== undefined ? (parameters as Prisma.InputJsonValue) : undefined,
      },
      include: {
        experiment: {
          select: {
            id: true,
            title: true,
            status: true,
          },
        },
        plot: {
          select: {
            id: true,
            plotCode: true,
            name: true,
          },
        },
      },
    });
  }

  async delete(id: string) {
    await this.findOne(id);

    return this.prisma.treatment.delete({
      where: { id },
    });
  }

  async findByExperimentAndPlot(experimentId: string, plotId: string) {
    return this.prisma.treatment.findMany({
      where: {
        experimentId,
        plotId,
      },
      orderBy: { createdAt: 'desc' },
    });
  }
}
