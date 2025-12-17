import { Module } from '@nestjs/common';
import { AnalyticsController } from './analytics.controller';
import { AnalyticsService } from './analytics.service';
import { PrismaService } from '@/config/prisma.service';

/**
 * Analytics Module - KPIs and Dashboard
 * وحدة التحليلات - مؤشرات الأداء ولوحة القيادة
 */
@Module({
  controllers: [AnalyticsController],
  providers: [AnalyticsService, PrismaService],
  exports: [AnalyticsService],
})
export class AnalyticsModule {}
