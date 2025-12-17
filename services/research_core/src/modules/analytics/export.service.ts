import { Injectable, Logger, NotFoundException } from '@nestjs/common';
import { PrismaService } from '@/config/prisma.service';
import { ExportQueryDto } from './dto/analytics.dto';

/**
 * Export Service - Data export functionality
 * خدمة التصدير - وظائف تصدير البيانات
 */
@Injectable()
export class ExportService {
  private readonly logger = new Logger(ExportService.name);

  constructor(private readonly prisma: PrismaService) {}

  /**
   * Export experiment data
   * تصدير بيانات التجربة
   */
  async exportExperiment(query: ExportQueryDto) {
    const experiment = await this.prisma.experiment.findUnique({
      where: { id: query.experimentId },
      include: {
        protocols: true,
        plots: true,
        treatments: true,
        collaborators: true,
      },
    });

    if (!experiment) {
      throw new NotFoundException(`Experiment ${query.experimentId} not found`);
    }

    const dateFilter: any = {};
    if (query.startDate) dateFilter.gte = new Date(query.startDate);
    if (query.endDate) dateFilter.lte = new Date(query.endDate);

    const includeEntities = query.includeEntities || [
      'logs',
      'samples',
      'protocols',
      'plots',
      'treatments',
    ];

    const data: any = {
      experiment: this.sanitizeExperiment(experiment),
      exportedAt: new Date(),
      exportedBy: 'system',
    };

    // Include logs
    if (includeEntities.includes('logs')) {
      data.logs = await this.prisma.researchDailyLog.findMany({
        where: {
          experimentId: query.experimentId,
          ...(Object.keys(dateFilter).length > 0 && { logDate: dateFilter }),
        },
        orderBy: { logDate: 'asc' },
      });
    }

    // Include samples
    if (includeEntities.includes('samples')) {
      data.samples = await this.prisma.labSample.findMany({
        where: {
          experimentId: query.experimentId,
          ...(Object.keys(dateFilter).length > 0 && { collectionDate: dateFilter }),
        },
        orderBy: { collectionDate: 'asc' },
      });
    }

    // Include protocols
    if (includeEntities.includes('protocols')) {
      data.protocols = experiment.protocols;
    }

    // Include plots
    if (includeEntities.includes('plots')) {
      data.plots = experiment.plots;
    }

    // Include treatments
    if (includeEntities.includes('treatments')) {
      data.treatments = experiment.treatments;
    }

    // Format based on requested format
    const format = query.format || 'json';

    switch (format) {
      case 'csv':
        return this.toCSV(data);
      case 'json':
      default:
        return data;
    }
  }

  /**
   * Export logs for date range
   * تصدير السجلات لنطاق تاريخي
   */
  async exportLogs(experimentId: string, startDate?: Date, endDate?: Date) {
    const where: any = { experimentId };

    if (startDate || endDate) {
      where.logDate = {};
      if (startDate) where.logDate.gte = startDate;
      if (endDate) where.logDate.lte = endDate;
    }

    const logs = await this.prisma.researchDailyLog.findMany({
      where,
      include: {
        plot: { select: { plotCode: true, name: true } },
        treatment: { select: { treatmentCode: true, name: true } },
      },
      orderBy: { logDate: 'asc' },
    });

    return {
      experimentId,
      exportedAt: new Date(),
      count: logs.length,
      logs: logs.map(this.sanitizeLog),
    };
  }

  /**
   * Export samples for date range
   * تصدير العينات لنطاق تاريخي
   */
  async exportSamples(experimentId: string, startDate?: Date, endDate?: Date) {
    const where: any = { experimentId };

    if (startDate || endDate) {
      where.collectionDate = {};
      if (startDate) where.collectionDate.gte = startDate;
      if (endDate) where.collectionDate.lte = endDate;
    }

    const samples = await this.prisma.labSample.findMany({
      where,
      include: {
        plot: { select: { plotCode: true, name: true } },
      },
      orderBy: { collectionDate: 'asc' },
    });

    return {
      experimentId,
      exportedAt: new Date(),
      count: samples.length,
      samples: samples.map(this.sanitizeSample),
    };
  }

  /**
   * Generate export summary
   * إنشاء ملخص التصدير
   */
  async getExportSummary(experimentId: string) {
    const [logsCount, samplesCount, firstLog, lastLog] = await Promise.all([
      this.prisma.researchDailyLog.count({ where: { experimentId } }),
      this.prisma.labSample.count({ where: { experimentId } }),
      this.prisma.researchDailyLog.findFirst({
        where: { experimentId },
        orderBy: { logDate: 'asc' },
        select: { logDate: true },
      }),
      this.prisma.researchDailyLog.findFirst({
        where: { experimentId },
        orderBy: { logDate: 'desc' },
        select: { logDate: true },
      }),
    ]);

    return {
      experimentId,
      counts: {
        logs: logsCount,
        samples: samplesCount,
      },
      dateRange: {
        first: firstLog?.logDate,
        last: lastLog?.logDate,
      },
      estimatedSize: this.estimateExportSize(logsCount, samplesCount),
    };
  }

  /**
   * Estimate export file size
   */
  private estimateExportSize(logsCount: number, samplesCount: number): string {
    // Rough estimate: ~2KB per log, ~1KB per sample
    const bytes = logsCount * 2000 + samplesCount * 1000;

    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  }

  /**
   * Convert data to CSV format
   */
  private toCSV(data: any): string {
    const lines: string[] = [];

    // Export experiment info
    lines.push('# Experiment Export');
    lines.push(`# Exported At: ${data.exportedAt}`);
    lines.push(`# Experiment: ${data.experiment.title}`);
    lines.push('');

    // Export logs as CSV
    if (data.logs && data.logs.length > 0) {
      lines.push('# Logs');
      const logHeaders = ['id', 'logDate', 'category', 'title', 'notes', 'plotId'];
      lines.push(logHeaders.join(','));

      for (const log of data.logs) {
        const row = logHeaders.map((h) => this.escapeCSV(log[h]));
        lines.push(row.join(','));
      }
      lines.push('');
    }

    // Export samples as CSV
    if (data.samples && data.samples.length > 0) {
      lines.push('# Samples');
      const sampleHeaders = ['id', 'sampleCode', 'collectionDate', 'status', 'plotId'];
      lines.push(sampleHeaders.join(','));

      for (const sample of data.samples) {
        const row = sampleHeaders.map((h) => this.escapeCSV(sample[h]));
        lines.push(row.join(','));
      }
    }

    return lines.join('\n');
  }

  /**
   * Escape value for CSV
   */
  private escapeCSV(value: any): string {
    if (value === null || value === undefined) return '';
    const str = String(value);
    if (str.includes(',') || str.includes('"') || str.includes('\n')) {
      return `"${str.replace(/"/g, '""')}"`;
    }
    return str;
  }

  /**
   * Sanitize experiment for export
   */
  private sanitizeExperiment(exp: any) {
    const { createdAt, updatedAt, ...rest } = exp;
    return {
      ...rest,
      createdAt: createdAt?.toISOString(),
      updatedAt: updatedAt?.toISOString(),
    };
  }

  /**
   * Sanitize log for export
   */
  private sanitizeLog(log: any) {
    return {
      id: log.id,
      logDate: log.logDate?.toISOString(),
      logTime: log.logTime,
      category: log.category,
      title: log.title,
      notes: log.notes,
      measurements: log.measurements,
      plotId: log.plotId,
      plotCode: log.plot?.plotCode,
      treatmentId: log.treatmentId,
      treatmentCode: log.treatment?.treatmentCode,
    };
  }

  /**
   * Sanitize sample for export
   */
  private sanitizeSample(sample: any) {
    return {
      id: sample.id,
      sampleCode: sample.sampleCode,
      collectionDate: sample.collectionDate?.toISOString(),
      status: sample.status,
      sampleType: sample.sampleType,
      plotId: sample.plotId,
      plotCode: sample.plot?.plotCode,
      labId: sample.labId,
      results: sample.results,
    };
  }
}
