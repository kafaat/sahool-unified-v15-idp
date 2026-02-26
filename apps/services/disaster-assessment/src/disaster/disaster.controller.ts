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
  Req,
} from "@nestjs/common";
import { ApiTags, ApiOperation, ApiResponse, ApiQuery } from "@nestjs/swagger";
import { Throttle } from "@nestjs/throttler";
import { DisasterService } from "./disaster.service";
import {
  CreateDisasterReportDto,
  DisasterAssessmentDto,
  DisasterType,
} from "./disaster.dto";
import { JwtAuthGuard } from "../auth/jwt-auth.guard";
import { SkipTenantCheck } from "@sahool/nestjs-auth";

@ApiTags("disasters")
@Controller("api/v1/disasters")
@UseGuards(JwtAuthGuard)
export class DisasterController {
  constructor(private readonly disasterService: DisasterService) {}

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Active Disasters - الكوارث النشطة
  // ─────────────────────────────────────────────────────────────────────────────

  @Get()
  @ApiOperation({
    summary: "Get active disasters",
    description: "الحصول على الكوارث النشطة في المنطقة",
  })
  @ApiQuery({ name: "type", enum: DisasterType, required: false })
  @ApiQuery({ name: "governorate", required: false })
  @ApiQuery({
    name: "severity",
    enum: ["low", "medium", "high", "critical"],
    required: false,
  })
  @ApiResponse({ status: 200, description: "List of active disasters" })
  async getActiveDisasters(
    @Req() req: any,
    @Query("type") type?: DisasterType,
    @Query("governorate") governorate?: string,
    @Query("severity") severity?: string,
  ) {
    const tenantId = req.user?.tenantId || req.headers['x-tenant-id'];
    return this.disasterService.getActiveDisasters(tenantId, {
      type,
      governorate,
      severity,
    });
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Disaster by ID - تفاصيل الكارثة
  // ─────────────────────────────────────────────────────────────────────────────

  @Get(":id")
  @ApiOperation({
    summary: "Get disaster details",
    description: "الحصول على تفاصيل كارثة محددة",
  })
  @ApiResponse({ status: 200, description: "Disaster details" })
  async getDisasterById(@Param("id") id: string, @Req() req: any) {
    const tenantId = req.user?.tenantId || req.headers['x-tenant-id'];
    return this.disasterService.getDisasterById(id, tenantId);
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Report New Disaster - الإبلاغ عن كارثة
  // ─────────────────────────────────────────────────────────────────────────────

  @Post("report")
  @UseGuards(JwtAuthGuard)
  @HttpCode(HttpStatus.CREATED)
  @ApiOperation({
    summary: "Report a new disaster",
    description: "الإبلاغ عن كارثة جديدة",
  })
  @ApiResponse({ status: 201, description: "Disaster reported successfully" })
  async reportDisaster(@Body() dto: CreateDisasterReportDto, @Req() req: any) {
    const tenantId = req.user?.tenantId || req.headers['x-tenant-id'];
    return this.disasterService.reportDisaster(dto, tenantId);
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Assess Field Damage - تقييم أضرار الحقل
  // ─────────────────────────────────────────────────────────────────────────────

  @Post("assess/:fieldId")
  @UseGuards(JwtAuthGuard)
  @ApiOperation({
    summary: "Assess field damage",
    description: "تقييم أضرار حقل معين من كارثة",
  })
  @ApiResponse({ status: 200, description: "Damage assessment result" })
  async assessFieldDamage(
    @Param("fieldId") fieldId: string,
    @Body() dto: DisasterAssessmentDto,
    @Req() req: any,
  ) {
    const tenantId = req.user?.tenantId || req.headers['x-tenant-id'];
    return this.disasterService.assessFieldDamage(fieldId, dto, tenantId);
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Flood Risk Map - خريطة مخاطر الفيضانات
  // ─────────────────────────────────────────────────────────────────────────────

  @Get("risk/flood")
  @ApiOperation({
    summary: "Get flood risk map data",
    description: "الحصول على بيانات خريطة مخاطر الفيضانات",
  })
  @ApiQuery({ name: "governorate", required: true })
  async getFloodRiskMap(@Query("governorate") governorate: string, @Req() req: any) {
    const tenantId = req.user?.tenantId || req.headers['x-tenant-id'];
    return this.disasterService.getFloodRiskMap(governorate, tenantId);
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Drought Index - مؤشر الجفاف
  // ─────────────────────────────────────────────────────────────────────────────

  @Get("risk/drought")
  @ApiOperation({
    summary: "Get drought index",
    description: "الحصول على مؤشر الجفاف للمنطقة",
  })
  @ApiQuery({ name: "governorate", required: true })
  async getDroughtIndex(@Query("governorate") governorate: string, @Req() req: any) {
    const tenantId = req.user?.tenantId || req.headers['x-tenant-id'];
    return this.disasterService.getDroughtIndex(governorate, tenantId);
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Statistics - إحصائيات الكوارث
  // ─────────────────────────────────────────────────────────────────────────────

  @Get("stats/summary")
  @ApiOperation({
    summary: "Get disaster statistics",
    description: "الحصول على إحصائيات الكوارث",
  })
  @ApiQuery({ name: "year", required: false })
  @ApiQuery({ name: "governorate", required: false })
  async getStatistics(
    @Req() req: any,
    @Query("year") year?: number,
    @Query("governorate") governorate?: string,
  ) {
    const tenantId = req.user?.tenantId || req.headers['x-tenant-id'];
    return this.disasterService.getStatistics(tenantId, { year, governorate });
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Health Check
  // ─────────────────────────────────────────────────────────────────────────────

  @Get("health")
  @SkipTenantCheck()
  @Throttle({ default: { limit: 10, ttl: 60000 } })
  @ApiOperation({ summary: "Health check" })
  healthCheck() {
    return {
      status: "ok",
      service: "disaster-assessment",
      timestamp: new Date().toISOString(),
    };
  }
}
