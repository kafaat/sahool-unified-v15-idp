import {
  Controller,
  Get,
  Query,
  Param,
  UseGuards,
  Logger,
} from '@nestjs/common';
import { AnalyticsService } from './analytics.service';
import {
  AnalyticsQueryDto,
  KpiQueryDto,
  TrendQueryDto,
} from './dto/analytics.dto';

/**
 * Analytics Controller - Dashboard and KPI endpoints
 * وحدة التحليلات - نقاط نهاية لوحة القيادة ومؤشرات الأداء
 */
@Controller('analytics')
export class AnalyticsController {
  private readonly logger = new Logger(AnalyticsController.name);

  constructor(private readonly analyticsService: AnalyticsService) {}

  /**
   * GET /analytics/dashboard
   * Get dashboard overview
   * الحصول على نظرة عامة للوحة القيادة
   */
  @Get('dashboard')
  async getDashboard(@Query() query: AnalyticsQueryDto) {
    this.logger.log('Getting dashboard overview');
    return this.analyticsService.getDashboardOverview(query);
  }

  /**
   * GET /analytics/kpis
   * Get KPI calculations
   * الحصول على حسابات مؤشرات الأداء
   */
  @Get('kpis')
  async getKpis(@Query() query: KpiQueryDto) {
    this.logger.log('Calculating KPIs');
    return this.analyticsService.calculateKpis(query);
  }

  /**
   * GET /analytics/trends
   * Get trend data for a metric
   * الحصول على بيانات الاتجاه لمقياس
   */
  @Get('trends')
  async getTrend(@Query() query: TrendQueryDto) {
    this.logger.log(`Getting trend for metric: ${query.metric}`);
    return this.analyticsService.getTrend(query);
  }

  /**
   * GET /analytics/experiments/:id
   * Get experiment-specific analytics
   * الحصول على تحليلات خاصة بالتجربة
   */
  @Get('experiments/:id')
  async getExperimentAnalytics(@Param('id') id: string) {
    this.logger.log(`Getting analytics for experiment: ${id}`);
    return this.analyticsService.getExperimentAnalytics(id);
  }

  /**
   * GET /analytics/health
   * Get system health analytics
   * الحصول على تحليلات صحة النظام
   */
  @Get('health')
  async getSystemHealth() {
    this.logger.log('Getting system health analytics');

    const kpis = await this.analyticsService.calculateKpis({
      types: ['data_integrity', 'experiment_progress'],
    } as KpiQueryDto);

    return {
      status: 'healthy',
      timestamp: new Date(),
      kpis: kpis.kpis,
    };
  }
}
