// ═══════════════════════════════════════════════════════════════════════════════
// Yield Controller - مراقب الإنتاجية
// Field-First Architecture - Pre-Harvest Alerts
// ═══════════════════════════════════════════════════════════════════════════════

import { Controller, Get, Post, Body, Param, Query, HttpException, HttpStatus } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse, ApiQuery } from '@nestjs/swagger';
import { YieldService, ActionTemplate, PreHarvestAlertResponse } from './yield.service';

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
    try {
      return await this.yieldService.predictFieldYield(fieldId);
    } catch (error) {
      throw new HttpException(
        error.message || 'Failed to predict field yield',
        error.status || HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
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
    try {
      return await this.yieldService.getGrowthStage(fieldId);
    } catch (error) {
      throw new HttpException(
        error.message || 'Failed to get growth stage',
        error.status || HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
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
    try {
      return await this.yieldService.predictHarvestDate(fieldId);
    } catch (error) {
      throw new HttpException(
        error.message || 'Failed to predict harvest date',
        error.status || HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
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
    try {
      return await this.yieldService.getRegionalStats({ governorate, cropType, year });
    } catch (error) {
      throw new HttpException(
        error.message || 'Failed to get regional statistics',
        error.status || HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
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
    try {
      return await this.yieldService.getHistoricalYields(fieldId, years || 5);
    } catch (error) {
      throw new HttpException(
        error.message || 'Failed to get historical yields',
        error.status || HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
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
    try {
      return await this.yieldService.getMaturityMonitoring(fieldId);
    } catch (error) {
      throw new HttpException(
        error.message || 'Failed to get maturity monitoring data',
        error.status || HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Field-First: Pre-Harvest Alert with ActionTemplate
  // تنبيه ما قبل الحصاد مع قالب الإجراء
  // ─────────────────────────────────────────────────────────────────────────────

  @Get('predict-with-action/:fieldId')
  @ApiOperation({
    summary: 'Predict yield with ActionTemplate',
    description: 'التنبؤ بالإنتاجية مع قالب إجراء ما قبل الحصاد - Field-First',
  })
  @ApiResponse({ status: 200, description: 'Pre-harvest alert with ActionTemplate' })
  async predictWithAction(
    @Param('fieldId') fieldId: string,
    @Query('farmerId') farmerId?: string,
    @Query('tenantId') tenantId?: string,
  ): Promise<PreHarvestAlertResponse> {
    try {
      return await this.yieldService.predictWithAction(fieldId, farmerId, tenantId);
    } catch (error) {
      throw new HttpException(
        error.message || 'Failed to predict with action template',
        error.status || HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Field-First: Harvest Readiness Check
  // فحص جاهزية الحصاد
  // ─────────────────────────────────────────────────────────────────────────────

  @Get('harvest-readiness/:fieldId')
  @ApiOperation({
    summary: 'Check harvest readiness with ActionTemplate',
    description: 'فحص جاهزية الحصاد مع توصيات عملية',
  })
  async getHarvestReadiness(
    @Param('fieldId') fieldId: string,
    @Query('farmerId') farmerId?: string,
  ) {
    try {
      return await this.yieldService.getHarvestReadiness(fieldId, farmerId);
    } catch (error) {
      throw new HttpException(
        error.message || 'Failed to get harvest readiness',
        error.status || HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Health Check
  // ─────────────────────────────────────────────────────────────────────────────

  @Get('health')
  healthCheck() {
    return { status: 'ok', service: 'yield-prediction', timestamp: new Date().toISOString() };
  }
}
