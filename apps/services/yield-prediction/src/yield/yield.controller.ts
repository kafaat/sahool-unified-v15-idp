// ═══════════════════════════════════════════════════════════════════════════════
// Yield Controller - مراقب الإنتاجية
// ═══════════════════════════════════════════════════════════════════════════════

import { Controller, Get, Post, Body, Param, Query } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse, ApiQuery } from '@nestjs/swagger';
import { YieldService } from './yield.service';

@ApiTags('yield')
@Controller('api/v1/yield')
export class YieldController {
  constructor(private readonly yieldService: YieldService) {}

  // ─────────────────────────────────────────────────────────────────────────────
  // Predict Field Yield - التنبؤ بإنتاجية الحقل
  // ─────────────────────────────────────────────────────────────────────────────

  @Get('predict/:fieldId')
  @ApiOperation({
    summary: 'Predict field yield',
    description: 'التنبؤ بإنتاجية حقل معين بناءً على بيانات الاستشعار عن بُعد',
  })
  @ApiResponse({ status: 200, description: 'Yield prediction result' })
  async predictFieldYield(@Param('fieldId') fieldId: string) {
    return this.yieldService.predictFieldYield(fieldId);
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Growth Stage - مرحلة النمو
  // ─────────────────────────────────────────────────────────────────────────────

  @Get('growth-stage/:fieldId')
  @ApiOperation({
    summary: 'Get crop growth stage',
    description: 'الحصول على مرحلة نمو المحصول الحالية',
  })
  async getGrowthStage(@Param('fieldId') fieldId: string) {
    return this.yieldService.getGrowthStage(fieldId);
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Predict Harvest Date - التنبؤ بموعد الحصاد
  // ─────────────────────────────────────────────────────────────────────────────

  @Get('harvest-date/:fieldId')
  @ApiOperation({
    summary: 'Predict harvest date',
    description: 'التنبؤ بموعد الحصاد الأمثل',
  })
  async predictHarvestDate(@Param('fieldId') fieldId: string) {
    return this.yieldService.predictHarvestDate(fieldId);
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Regional Statistics - إحصائيات المنطقة
  // ─────────────────────────────────────────────────────────────────────────────

  @Get('regional/:governorate')
  @ApiOperation({
    summary: 'Get regional yield statistics',
    description: 'الحصول على إحصائيات الإنتاجية للمنطقة',
  })
  @ApiQuery({ name: 'cropType', required: false })
  @ApiQuery({ name: 'year', required: false })
  async getRegionalStats(
    @Param('governorate') governorate: string,
    @Query('cropType') cropType?: string,
    @Query('year') year?: number,
  ) {
    return this.yieldService.getRegionalStats({ governorate, cropType, year });
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Historical Yields - الإنتاجية التاريخية
  // ─────────────────────────────────────────────────────────────────────────────

  @Get('history/:fieldId')
  @ApiOperation({
    summary: 'Get historical yield data',
    description: 'الحصول على بيانات الإنتاجية التاريخية للحقل',
  })
  @ApiQuery({ name: 'years', required: false, type: Number })
  async getHistoricalYields(
    @Param('fieldId') fieldId: string,
    @Query('years') years?: number,
  ) {
    return this.yieldService.getHistoricalYields(fieldId, years || 5);
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Maturity Monitoring - مراقبة النضج
  // ─────────────────────────────────────────────────────────────────────────────

  @Get('maturity/:fieldId')
  @ApiOperation({
    summary: 'Get maturity monitoring data',
    description: 'مراقبة نضج المحصول',
  })
  async getMaturityMonitoring(@Param('fieldId') fieldId: string) {
    return this.yieldService.getMaturityMonitoring(fieldId);
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Health Check
  // ─────────────────────────────────────────────────────────────────────────────

  @Get('health')
  healthCheck() {
    return { status: 'ok', service: 'yield-prediction', timestamp: new Date().toISOString() };
  }
}
