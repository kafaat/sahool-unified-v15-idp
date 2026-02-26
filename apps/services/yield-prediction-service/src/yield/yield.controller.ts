// ═══════════════════════════════════════════════════════════════════════════════
// Yield Controller - مراقب الإنتاجية
// Field-First Architecture - Pre-Harvest Alerts
// ═══════════════════════════════════════════════════════════════════════════════

import { Controller, Get, Param, Query, UseGuards, Req } from "@nestjs/common";
import { JwtAuthGuard, SkipTenantCheck } from "@sahool/nestjs-auth";
import { ApiTags, ApiOperation, ApiResponse, ApiQuery } from "@nestjs/swagger";
import {
  YieldService,
  ActionTemplate,
  PreHarvestAlertResponse,
} from "./yield.service";

@ApiTags("yield")
@Controller("api/v1/yield")
@UseGuards(JwtAuthGuard)
export class YieldController {
  constructor(private readonly yieldService: YieldService) {}

  // ─────────────────────────────────────────────────────────────────────────────
  // Predict Field Yield - التنبؤ بإنتاجية الحقل
  // ─────────────────────────────────────────────────────────────────────────────

  @Get("predict/:fieldId")
  @ApiOperation({
    summary: "Predict field yield",
    description: "التنبؤ بإنتاجية حقل معين بناءً على بيانات الاستشعار عن بُعد",
  })
  @ApiResponse({ status: 200, description: "Yield prediction result" })
  async predictFieldYield(@Param("fieldId") fieldId: string) {
    return this.yieldService.predictFieldYield(fieldId);
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Growth Stage - مرحلة النمو
  // ─────────────────────────────────────────────────────────────────────────────

  @Get("growth-stage/:fieldId")
  @ApiOperation({
    summary: "Get crop growth stage",
    description: "الحصول على مرحلة نمو المحصول الحالية",
  })
  async getGrowthStage(@Param("fieldId") fieldId: string) {
    return this.yieldService.getGrowthStage(fieldId);
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Predict Harvest Date - التنبؤ بموعد الحصاد
  // ─────────────────────────────────────────────────────────────────────────────

  @Get("harvest-date/:fieldId")
  @ApiOperation({
    summary: "Predict harvest date",
    description: "التنبؤ بموعد الحصاد الأمثل",
  })
  async predictHarvestDate(@Param("fieldId") fieldId: string) {
    return this.yieldService.predictHarvestDate(fieldId);
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Regional Statistics - إحصائيات المنطقة
  // ─────────────────────────────────────────────────────────────────────────────

  @Get("regional/:governorate")
  @ApiOperation({
    summary: "Get regional yield statistics",
    description: "الحصول على إحصائيات الإنتاجية للمنطقة",
  })
  @ApiQuery({ name: "cropType", required: false })
  @ApiQuery({ name: "year", required: false })
  async getRegionalStats(
    @Param("governorate") governorate: string,
    @Query("cropType") cropType?: string,
    @Query("year") year?: string,
  ) {
    const parsedYear = year ? parseInt(year, 10) : undefined;
    return this.yieldService.getRegionalStats({ governorate, cropType, year: parsedYear });
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Historical Yields - الإنتاجية التاريخية
  // ─────────────────────────────────────────────────────────────────────────────

  @Get("history/:fieldId")
  @ApiOperation({
    summary: "Get historical yield data",
    description: "الحصول على بيانات الإنتاجية التاريخية للحقل",
  })
  @ApiQuery({ name: "years", required: false, type: Number })
  async getHistoricalYields(
    @Param("fieldId") fieldId: string,
    @Query("years") years?: string,
  ) {
    const parsedYears = years ? parseInt(years, 10) : 5;
    return this.yieldService.getHistoricalYields(fieldId, parsedYears);
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Maturity Monitoring - مراقبة النضج
  // ─────────────────────────────────────────────────────────────────────────────

  @Get("maturity/:fieldId")
  @ApiOperation({
    summary: "Get maturity monitoring data",
    description: "مراقبة نضج المحصول",
  })
  async getMaturityMonitoring(@Param("fieldId") fieldId: string) {
    return this.yieldService.getMaturityMonitoring(fieldId);
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Field-First: Pre-Harvest Alert with ActionTemplate
  // تنبيه ما قبل الحصاد مع قالب الإجراء
  // ─────────────────────────────────────────────────────────────────────────────

  @Get("predict-with-action/:fieldId")
  @ApiOperation({
    summary: "Predict yield with ActionTemplate",
    description: "التنبؤ بالإنتاجية مع قالب إجراء ما قبل الحصاد - Field-First",
  })
  @ApiResponse({
    status: 200,
    description: "Pre-harvest alert with ActionTemplate",
  })
  async predictWithAction(
    @Req() req: any,
    @Param("fieldId") fieldId: string,
    @Query("farmerId") farmerId?: string,
    @Query("tenantId") queryTenantId?: string,
  ): Promise<PreHarvestAlertResponse> {
    const tenantId = req.user?.tenantId || req.headers['x-tenant-id'] || queryTenantId;
    return this.yieldService.predictWithAction(fieldId, farmerId, tenantId);
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Field-First: Harvest Readiness Check
  // فحص جاهزية الحصاد
  // ─────────────────────────────────────────────────────────────────────────────

  @Get("harvest-readiness/:fieldId")
  @ApiOperation({
    summary: "Check harvest readiness with ActionTemplate",
    description: "فحص جاهزية الحصاد مع توصيات عملية",
  })
  async getHarvestReadiness(
    @Req() req: any,
    @Param("fieldId") fieldId: string,
    @Query("farmerId") farmerId?: string,
    @Query("tenantId") queryTenantId?: string,
  ) {
    const tenantId = req.user?.tenantId || req.headers['x-tenant-id'] || queryTenantId;
    return this.yieldService.getHarvestReadiness(fieldId, farmerId, tenantId);
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Health Check
  // ─────────────────────────────────────────────────────────────────────────────

  @Get("health")
  @SkipTenantCheck()
  healthCheck() {
    return {
      status: "ok",
      service: "yield-prediction",
      timestamp: new Date().toISOString(),
    };
  }
}
