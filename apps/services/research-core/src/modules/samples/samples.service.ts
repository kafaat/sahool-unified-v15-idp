import {
  Injectable,
  Logger,
  NotFoundException,
  BadRequestException,
} from "@nestjs/common";
import { PrismaService } from "@/config/prisma.service";
import { Prisma } from "@prisma/client";
import { CreateSampleDto, UpdateSampleDto } from "./dto/sample.dto";

@Injectable()
export class SamplesService {
  private readonly logger = new Logger(SamplesService.name);

  constructor(private readonly prisma: PrismaService) {}

  /**
   * Sanitize input for safe logging (prevents log injection)
   */
  private sanitizeForLog(input: string): string {
    if (typeof input !== "string") return String(input);
    return input.replace(/[\r\n]/g, "").replace(/[\x00-\x1F\x7F]/g, "").slice(0, 100);
  }

  async create(dto: CreateSampleDto) {
    this.logger.log("Creating sample", { sampleCode: this.sanitizeForLog(dto.sampleCode) });

    // Check if sample code already exists
    const existing = await this.prisma.labSample.findUnique({
      where: { sampleCode: dto.sampleCode },
    });

    if (existing) {
      throw new BadRequestException(
        `Sample with code ${dto.sampleCode} already exists`,
      );
    }

    const { analysisResults, metadata, ...restDto } = dto;

    return this.prisma.labSample.create({
      data: {
        ...restDto,
        collectionDate: new Date(dto.collectionDate),
        analyzedAt: dto.analyzedAt ? new Date(dto.analyzedAt) : null,
        analysisResults: analysisResults as Prisma.InputJsonValue | undefined,
        metadata: metadata as Prisma.InputJsonValue | undefined,
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
        log: {
          select: {
            id: true,
            logDate: true,
            title: true,
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
      analysisStatus?: string;
      collectedBy?: string;
      startDate?: string;
      endDate?: string;
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
    if (filters?.analysisStatus) {
      where.analysisStatus = filters.analysisStatus;
    }
    if (filters?.collectedBy) {
      where.collectedBy = filters.collectedBy;
    }
    if (filters?.startDate || filters?.endDate) {
      where.collectionDate = {};
      if (filters?.startDate) {
        where.collectionDate.gte = new Date(filters.startDate);
      }
      if (filters?.endDate) {
        where.collectionDate.lte = new Date(filters.endDate);
      }
    }

    const [data, total] = await Promise.all([
      this.prisma.labSample.findMany({
        where,
        skip,
        take: limit,
        orderBy: { collectionDate: "desc" },
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
          log: {
            select: {
              id: true,
              logDate: true,
              title: true,
            },
          },
        },
      }),
      this.prisma.labSample.count({ where }),
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
    const sample = await this.prisma.labSample.findUnique({
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
        log: {
          select: {
            id: true,
            logDate: true,
            logTime: true,
            title: true,
            titleAr: true,
            category: true,
          },
        },
      },
    });

    if (!sample) {
      throw new NotFoundException(`Sample ${id} not found`);
    }

    return sample;
  }

  async findBySampleCode(sampleCode: string) {
    const sample = await this.prisma.labSample.findUnique({
      where: { sampleCode },
      include: {
        experiment: true,
        plot: true,
        log: true,
      },
    });

    if (!sample) {
      throw new NotFoundException(`Sample with code ${sampleCode} not found`);
    }

    return sample;
  }

  async update(id: string, dto: UpdateSampleDto) {
    await this.findOne(id);

    const { analysisResults, metadata, ...restDto } = dto;

    return this.prisma.labSample.update({
      where: { id },
      data: {
        ...restDto,
        collectionDate: dto.collectionDate
          ? new Date(dto.collectionDate)
          : undefined,
        analyzedAt: dto.analyzedAt ? new Date(dto.analyzedAt) : undefined,
        analysisResults:
          analysisResults !== undefined
            ? (analysisResults as Prisma.InputJsonValue)
            : undefined,
        metadata:
          metadata !== undefined
            ? (metadata as Prisma.InputJsonValue)
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
        plot: {
          select: {
            id: true,
            plotCode: true,
            name: true,
          },
        },
        log: {
          select: {
            id: true,
            logDate: true,
            title: true,
          },
        },
      },
    });
  }

  async delete(id: string) {
    await this.findOne(id);

    return this.prisma.labSample.delete({
      where: { id },
    });
  }

  async updateAnalysisStatus(
    id: string,
    status: string,
    analyzedBy?: string,
    analysisResults?: Record<string, unknown>,
  ) {
    await this.findOne(id);

    return this.prisma.labSample.update({
      where: { id },
      data: {
        analysisStatus: status,
        analyzedBy: analyzedBy || undefined,
        analyzedAt: analyzedBy ? new Date() : undefined,
        analysisResults: analysisResults
          ? (analysisResults as Prisma.InputJsonValue)
          : undefined,
      },
    });
  }
}
