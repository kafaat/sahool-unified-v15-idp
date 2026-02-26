// ═══════════════════════════════════════════════════════════════════════════════
// Yield Controller - مراقب الإنتاجية
// Field-First Architecture - Pre-Harvest Alerts
// ═══════════════════════════════════════════════════════════════════════════════

import {
  Controller,
  Get,
  Param,
  Query,
  UseGuards,
  Req,
  BadRequestException,
  ParseUUIDPipe,
} from "@nestjs/common";
import { JwtAuthGuard, SkipTenantCheck } from "@sahool/nestjs-auth";
import { ApiTags, ApiOperation, ApiResponse, ApiQuery } from "@nestjs/swagger";
import {
  YieldService,
  ActionTemplate,
  PreHarvestAlertResponse,
  FEATURE_SCHEMA,
} from "./yield.service";

const VALID_GOVERNORATES = [
  "sanaa",
  "aden",
  "taiz",
  "hodeidah",
  "ibb",
  "dhamar",
  "hadramaut",
  "marib",
] as const;

const VALID_CROP_TYPES = ["wheat", "coffee", "sorghum", "tomato"] as const;

@ApiTags("yield")
@Controller("api/v1/yield")
@UseGuards(JwtAuthGuard)
export class YieldController {
  constructor(private readonly yieldService: YieldService) {}

  @Get("feature-schema")
  @ApiOperation({
    summary: "Get ML feature schema",
    description: "Return the feature schema definition for data drift monitoring",
  })
  getFeatureSchema() {
    return FEATURE_SCHEMA;
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Predict Field Yield - التنبؤ بإنتاجية الحقل
  // ─────────────────────────────────────────────────────────────────────────────

  @Get("predict/:fieldId")
  @ApiOperation({
    summary: "Predict field yield",
    description: "التنبؤ بإنتاجية حقل معين بناءً على بيانات الاستشعار عن بُعد",
  })
  @ApiResponse({ status: 200, description: "Yield prediction result" })
  @ApiResponse({ status: 400, description: "Invalid fieldId format" })
  async predictFieldYield(
    @Param("fieldId", new ParseUUIDPipe({ optional: true })) fieldId: string,
  ) {
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
  async getGrowthStage(@Param("fieldId", new ParseUUIDPipe({ optional: true })) fieldId: string) {
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
  async predictHarvestDate(@Param("fieldId", new ParseUUIDPipe({ optional: true })) fieldId: string) {
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
  @ApiQuery({ name: "cropType", required: false, enum: VALID_CROP_TYPES })
  @ApiQuery({ name: "year", required: false, type: Number })
  @ApiResponse({ status: 400, description: "Invalid governorate, cropType, or year" })
  async getRegionalStats(
    @Param("governorate") governorate: string,
    @Query("cropType") cropType?: string,
    @Query("year") year?: string,
  ) {
    if (!VALID_GOVERNORATES.includes(governorate as any)) {
      throw new BadRequestException(
        `Invalid governorate "${governorate}". Valid values: ${VALID_GOVERNORATES.join(", ")}`,
      );
    }
    if (cropType && !VALID_CROP_TYPES.includes(cropType as any)) {
      throw new BadRequestException(
        `Invalid cropType "${cropType}". Valid values: ${VALID_CROP_TYPES.join(", ")}`,
      );
    }
    const parsedYear = year ? parseInt(year, 10) : undefined;
    if (parsedYear !== undefined && (isNaN(parsedYear) || parsedYear < 2000 || parsedYear > 2100)) {
      throw new BadRequestException("Year must be a number between 2000 and 2100");
    }
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
  @ApiResponse({ status: 400, description: "Invalid years parameter" })
  async getHistoricalYields(
    @Param("fieldId", new ParseUUIDPipe({ optional: true })) fieldId: string,
    @Query("years") years?: string,
  ) {
    const parsedYears = years ? parseInt(years, 10) : 5;
    if (isNaN(parsedYears) || parsedYears < 1 || parsedYears > 50) {
      throw new BadRequestException("Years must be a number between 1 and 50");
    }
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
  async getMaturityMonitoring(@Param("fieldId", new ParseUUIDPipe({ optional: true })) fieldId: string) {
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
