import { Injectable, Logger } from '@nestjs/common';
import { PrismaService } from '@/config/prisma.service';
import {
  AnalyticsQueryDto,
  KpiQueryDto,
  KpiType,
  TrendQueryDto,
  AnalyticsPeriod,
} from './dto/analytics.dto';

/**
 * Analytics Service - KPIs and Dashboard Data
 * خدمة التحليلات - مؤشرات الأداء ولوحة القيادة
 */
@Injectable()
export class AnalyticsService {
  private readonly logger = new Logger(AnalyticsService.name);

  constructor(private readonly prisma: PrismaService) {}

  /**
   * Get dashboard overview
   * الحصول على نظرة عامة للوحة القيادة
   */
  async getDashboardOverview(query: AnalyticsQueryDto) {
    const dateFilter = this.buildDateFilter(query.startDate, query.endDate);

    const [experiments, logs, samples, plots] = await Promise.all([
      this.prisma.experiment.count({
        where: {
          ...(query.farmId && { farmId: query.farmId }),
          ...dateFilter,
        },
      }),
      this.prisma.researchDailyLog.count({
        where: {
          ...(query.experimentId && { experimentId: query.experimentId }),
          ...dateFilter,
        },
      }),
      this.prisma.labSample.count({
        where: {
          ...(query.experimentId && { experimentId: query.experimentId }),
          ...dateFilter,
        },
      }),
      this.prisma.experimentPlot.count({
        where: {
          ...(query.experimentId && { experimentId: query.experimentId }),
        },
      }),
    ]);

    // Get status breakdown
    const experimentsByStatus = await this.prisma.experiment.groupBy({
      by: ['status'],
      _count: { id: true },
      where: {
        ...(query.farmId && { farmId: query.farmId }),
      },
    });

    return {
      summary: {
        totalExperiments: experiments,
        totalLogs: logs,
        totalSamples: samples,
        totalPlots: plots,
      },
      experimentsByStatus: experimentsByStatus.reduce(
        (acc, item) => ({ ...acc, [item.status]: item._count.id }),
        {},
      ),
      period: {
        startDate: query.startDate,
        endDate: query.endDate,
      },
    };
  }

  /**
   * Calculate KPIs
   * حساب مؤشرات الأداء
   */
  async calculateKpis(query: KpiQueryDto) {
    const types = query.types || Object.values(KpiType);
    const asOfDate = query.asOfDate ? new Date(query.asOfDate) : new Date();

    const kpis: Record<string, KpiResult> = {};

    for (const type of types) {
      kpis[type] = await this.calculateKpi(type, query, asOfDate);
    }

    return {
      kpis,
      calculatedAt: new Date(),
      asOfDate,
    };
  }

  /**
   * Calculate single KPI
   */
  private async calculateKpi(
    type: KpiType,
    query: KpiQueryDto,
    asOfDate: Date,
  ): Promise<KpiResult> {
    switch (type) {
      case KpiType.EXPERIMENT_PROGRESS:
        return this.calcExperimentProgress(query, asOfDate);
      case KpiType.LOG_COMPLETION:
        return this.calcLogCompletion(query, asOfDate);
      case KpiType.SAMPLE_PROCESSING:
        return this.calcSampleProcessing(query, asOfDate);
      case KpiType.DATA_INTEGRITY:
        return this.calcDataIntegrity(query, asOfDate);
      case KpiType.TASK_COMPLETION:
        return this.calcTaskCompletion(query, asOfDate);
      default:
        return { value: 0, target: 100, unit: '%', status: 'unknown' };
    }
  }

  /**
   * Experiment Progress KPI
   * نسبة تقدم التجارب
   */
  private async calcExperimentProgress(
    query: KpiQueryDto,
    asOfDate: Date,
  ): Promise<KpiResult> {
    const where: any = {};
    if (query.experimentId) where.id = query.experimentId;
    if (query.farmId) where.farmId = query.farmId;

    const experiments = await this.prisma.experiment.findMany({
      where,
      select: {
        id: true,
        startDate: true,
        endDate: true,
        status: true,
      },
    });

    if (experiments.length === 0) {
      return { value: 0, target: 100, unit: '%', status: 'no_data' };
    }

    let totalProgress = 0;
    for (const exp of experiments) {
      if (exp.status === 'completed' || exp.status === 'locked') {
        totalProgress += 100;
      } else if (exp.startDate && exp.endDate) {
        const total = exp.endDate.getTime() - exp.startDate.getTime();
        const elapsed = asOfDate.getTime() - exp.startDate.getTime();
        const progress = Math.min(100, Math.max(0, (elapsed / total) * 100));
        totalProgress += progress;
      } else {
        totalProgress += 50; // Default for experiments without end date
      }
    }

    const avgProgress = Math.round(totalProgress / experiments.length);

    return {
      value: avgProgress,
      target: 100,
      unit: '%',
      status: avgProgress >= 80 ? 'on_track' : avgProgress >= 50 ? 'at_risk' : 'behind',
    };
  }

  /**
   * Log Completion KPI
   * نسبة إكمال السجلات
   */
  private async calcLogCompletion(
    query: KpiQueryDto,
    asOfDate: Date,
  ): Promise<KpiResult> {
    const thirtyDaysAgo = new Date(asOfDate.getTime() - 30 * 24 * 60 * 60 * 1000);

    const where: any = {
      logDate: { gte: thirtyDaysAgo, lte: asOfDate },
    };
    if (query.experimentId) where.experimentId = query.experimentId;

    // Count logs with all required fields
    const totalLogs = await this.prisma.researchDailyLog.count({ where });

    const completeLogs = await this.prisma.researchDailyLog.count({
      where: {
        ...where,
        notes: { not: null },
        measurements: { not: undefined },
      },
    });

    const completionRate = totalLogs > 0 ? Math.round((completeLogs / totalLogs) * 100) : 0;

    return {
      value: completionRate,
      target: 95,
      unit: '%',
      status: completionRate >= 95 ? 'excellent' : completionRate >= 80 ? 'good' : 'needs_improvement',
      metadata: { totalLogs, completeLogs },
    };
  }

  /**
   * Sample Processing KPI
   * معالجة العينات
   */
  private async calcSampleProcessing(
    query: KpiQueryDto,
    asOfDate: Date,
  ): Promise<KpiResult> {
    const where: any = {};
    if (query.experimentId) where.experimentId = query.experimentId;

    const [total, processed, pending] = await Promise.all([
      this.prisma.labSample.count({ where }),
      this.prisma.labSample.count({
        where: { ...where, status: 'analyzed' },
      }),
      this.prisma.labSample.count({
        where: { ...where, status: { in: ['collected', 'submitted'] } },
      }),
    ]);

    const processingRate = total > 0 ? Math.round((processed / total) * 100) : 0;

    return {
      value: processingRate,
      target: 90,
      unit: '%',
      status: processingRate >= 90 ? 'excellent' : processingRate >= 70 ? 'good' : 'behind',
      metadata: { total, processed, pending },
    };
  }

  /**
   * Data Integrity KPI
   * سلامة البيانات
   */
  private async calcDataIntegrity(
    query: KpiQueryDto,
    asOfDate: Date,
  ): Promise<KpiResult> {
    const where: any = {};
    if (query.experimentId) where.experimentId = query.experimentId;

    const totalLogs = await this.prisma.researchDailyLog.count({ where });
    const logsWithHash = await this.prisma.researchDailyLog.count({
      where: { ...where, hash: { not: null } },
    });

    const integrityRate = totalLogs > 0 ? Math.round((logsWithHash / totalLogs) * 100) : 100;

    return {
      value: integrityRate,
      target: 100,
      unit: '%',
      status: integrityRate === 100 ? 'verified' : integrityRate >= 95 ? 'good' : 'attention_needed',
      metadata: { totalLogs, logsWithHash },
    };
  }

  /**
   * Task Completion KPI
   * إكمال المهام
   */
  private async calcTaskCompletion(
    query: KpiQueryDto,
    asOfDate: Date,
  ): Promise<KpiResult> {
    // This would integrate with task system
    // Placeholder for now
    return {
      value: 85,
      target: 90,
      unit: '%',
      status: 'good',
    };
  }

  /**
   * Get trend data for a metric
   * الحصول على بيانات الاتجاه لمقياس
   */
  async getTrend(query: TrendQueryDto) {
    const startDate = query.startDate
      ? new Date(query.startDate)
      : new Date(Date.now() - 30 * 24 * 60 * 60 * 1000);
    const endDate = query.endDate ? new Date(query.endDate) : new Date();
    const dataPoints = query.dataPoints || 30;

    const interval = (endDate.getTime() - startDate.getTime()) / dataPoints;
    const points: TrendPoint[] = [];

    for (let i = 0; i < dataPoints; i++) {
      const pointDate = new Date(startDate.getTime() + interval * i);
      const value = await this.getMetricValueAt(query.metric, query.experimentId, pointDate);
      points.push({ date: pointDate, value });
    }

    return {
      metric: query.metric,
      period: { startDate, endDate },
      dataPoints: points,
      trend: this.calculateTrendDirection(points),
    };
  }

  /**
   * Get metric value at a specific date
   */
  private async getMetricValueAt(
    metric: string,
    experimentId: string | undefined,
    date: Date,
  ): Promise<number> {
    const where: any = {
      createdAt: { lte: date },
    };
    if (experimentId) where.experimentId = experimentId;

    switch (metric) {
      case 'logs_count':
        return this.prisma.researchDailyLog.count({ where });
      case 'samples_count':
        return this.prisma.labSample.count({ where });
      default:
        return 0;
    }
  }

  /**
   * Calculate trend direction
   */
  private calculateTrendDirection(points: TrendPoint[]): TrendDirection {
    if (points.length < 2) return 'stable';

    const firstHalf = points.slice(0, Math.floor(points.length / 2));
    const secondHalf = points.slice(Math.floor(points.length / 2));

    const firstAvg = firstHalf.reduce((sum, p) => sum + p.value, 0) / firstHalf.length;
    const secondAvg = secondHalf.reduce((sum, p) => sum + p.value, 0) / secondHalf.length;

    const change = ((secondAvg - firstAvg) / firstAvg) * 100;

    if (change > 10) return 'up';
    if (change < -10) return 'down';
    return 'stable';
  }

  /**
   * Get experiment analytics
   * تحليلات التجربة
   */
  async getExperimentAnalytics(experimentId: string) {
    const experiment = await this.prisma.experiment.findUnique({
      where: { id: experimentId },
      include: {
        _count: {
          select: {
            logs: true,
            samples: true,
            plots: true,
            treatments: true,
            protocols: true,
          },
        },
      },
    });

    if (!experiment) {
      return null;
    }

    // Get daily log activity
    const logsByDate = await this.prisma.researchDailyLog.groupBy({
      by: ['logDate'],
      where: { experimentId },
      _count: { id: true },
      orderBy: { logDate: 'asc' },
    });

    // Get category distribution
    const logsByCategory = await this.prisma.researchDailyLog.groupBy({
      by: ['category'],
      where: { experimentId },
      _count: { id: true },
    });

    // Get sample status distribution
    const samplesByStatus = await this.prisma.labSample.groupBy({
      by: ['status'],
      where: { experimentId },
      _count: { id: true },
    });

    return {
      experiment: {
        id: experiment.id,
        title: experiment.title,
        status: experiment.status,
        startDate: experiment.startDate,
        endDate: experiment.endDate,
      },
      counts: experiment._count,
      activity: {
        logsByDate: logsByDate.map((l) => ({
          date: l.logDate,
          count: l._count.id,
        })),
        logsByCategory: logsByCategory.reduce(
          (acc, l) => ({ ...acc, [l.category]: l._count.id }),
          {},
        ),
      },
      samples: {
        byStatus: samplesByStatus.reduce(
          (acc, s) => ({ ...acc, [s.status]: s._count.id }),
          {},
        ),
      },
    };
  }

  /**
   * Build date filter for queries
   */
  private buildDateFilter(startDate?: string, endDate?: string) {
    const filter: any = {};

    if (startDate || endDate) {
      filter.createdAt = {};
      if (startDate) filter.createdAt.gte = new Date(startDate);
      if (endDate) filter.createdAt.lte = new Date(endDate);
    }

    return filter;
  }
}

/**
 * KPI Result interface
 */
interface KpiResult {
  value: number;
  target: number;
  unit: string;
  status: string;
  metadata?: Record<string, any>;
}

/**
 * Trend point
 */
interface TrendPoint {
  date: Date;
  value: number;
}

/**
 * Trend direction
 */
type TrendDirection = 'up' | 'down' | 'stable';
