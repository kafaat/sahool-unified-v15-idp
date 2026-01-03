// ═══════════════════════════════════════════════════════════════════════════════
// Disaster Controller - مراقب الكوارث
// ═══════════════════════════════════════════════════════════════════════════════

import {
  Controller,
  Get,
  Post,
  Body,
  Param,
  Query,
  HttpCode,
  HttpStatus,
  UseGuards,
} from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse, ApiQuery } from '@nestjs/swagger';
import { Throttle } from '@nestjs/throttler';
import { DisasterService } from './disaster.service';
import {
  CreateDisasterReportDto,
  DisasterAssessmentDto,
  DisasterType,
} from './disaster.dto';
import { JwtAuthGuard } from '../auth/jwt-auth.guard';

@ApiTags('disasters')
@Controller('api/v1/disasters')
export class DisasterController {
  constructor(private readonly disasterService: DisasterService) {}

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Active Disasters - الكوارث النشطة
  // ─────────────────────────────────────────────────────────────────────────────

  @Get()
  @ApiOperation({
    summary: 'Get active disasters',
    description: 'الحصول على الكوارث النشطة في المنطقة',
  })
  @ApiQuery({ name: 'type', enum: DisasterType, required: false })
  @ApiQuery({ name: 'governorate', required: false })
  @ApiQuery({ name: 'severity', enum: ['low', 'medium', 'high', 'critical'], required: false })
  @ApiResponse({ status: 200, description: 'List of active disasters' })
  async getActiveDisasters(
    @Query('type') type?: DisasterType,
    @Query('governorate') governorate?: string,
    @Query('severity') severity?: string,
  ) {
    return this.disasterService.getActiveDisasters({ type, governorate, severity });
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Disaster by ID - تفاصيل الكارثة
  // ─────────────────────────────────────────────────────────────────────────────

  @Get(':id')
  @ApiOperation({
    summary: 'Get disaster details',
    description: 'الحصول على تفاصيل كارثة محددة',
  })
  @ApiResponse({ status: 200, description: 'Disaster details' })
  async getDisasterById(@Param('id') id: string) {
    return this.disasterService.getDisasterById(id);
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Report New Disaster - الإبلاغ عن كارثة
  // ─────────────────────────────────────────────────────────────────────────────

  @Post('report')
  @UseGuards(JwtAuthGuard)
  @HttpCode(HttpStatus.CREATED)
  @ApiOperation({
    summary: 'Report a new disaster',
    description: 'الإبلاغ عن كارثة جديدة',
  })
  @ApiResponse({ status: 201, description: 'Disaster reported successfully' })
  async reportDisaster(@Body() dto: CreateDisasterReportDto) {
    return this.disasterService.reportDisaster(dto);
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Assess Field Damage - تقييم أضرار الحقل
  // ─────────────────────────────────────────────────────────────────────────────

  @Post('assess/:fieldId')
  @UseGuards(JwtAuthGuard)
  @ApiOperation({
    summary: 'Assess field damage',
    description: 'تقييم أضرار حقل معين من كارثة',
  })
  @ApiResponse({ status: 200, description: 'Damage assessment result' })
  async assessFieldDamage(
    @Param('fieldId') fieldId: string,
    @Body() dto: DisasterAssessmentDto,
  ) {
    return this.disasterService.assessFieldDamage(fieldId, dto);
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Flood Risk Map - خريطة مخاطر الفيضانات
  // ─────────────────────────────────────────────────────────────────────────────

  @Get('risk/flood')
  @ApiOperation({
    summary: 'Get flood risk map data',
    description: 'الحصول على بيانات خريطة مخاطر الفيضانات',
  })
  @ApiQuery({ name: 'governorate', required: true })
  async getFloodRiskMap(@Query('governorate') governorate: string) {
    return this.disasterService.getFloodRiskMap(governorate);
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Drought Index - مؤشر الجفاف
  // ─────────────────────────────────────────────────────────────────────────────

  @Get('risk/drought')
  @ApiOperation({
    summary: 'Get drought index',
    description: 'الحصول على مؤشر الجفاف للمنطقة',
  })
  @ApiQuery({ name: 'governorate', required: true })
  async getDroughtIndex(@Query('governorate') governorate: string) {
    return this.disasterService.getDroughtIndex(governorate);
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Statistics - إحصائيات الكوارث
  // ─────────────────────────────────────────────────────────────────────────────

  @Get('stats/summary')
  @ApiOperation({
    summary: 'Get disaster statistics',
    description: 'الحصول على إحصائيات الكوارث',
  })
  @ApiQuery({ name: 'year', required: false })
  @ApiQuery({ name: 'governorate', required: false })
  async getStatistics(
    @Query('year') year?: number,
    @Query('governorate') governorate?: string,
  ) {
    return this.disasterService.getStatistics({ year, governorate });
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Health Check
  // ─────────────────────────────────────────────────────────────────────────────

  @Get('health')
  @Throttle({ limit: 10, ttl: 60000 })
  @ApiOperation({ summary: 'Health check' })
  healthCheck() {
    return { status: 'ok', service: 'disaster-assessment', timestamp: new Date().toISOString() };
  }
}
