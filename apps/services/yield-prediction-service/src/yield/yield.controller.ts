// ═══════════════════════════════════════════════════════════════════════════════
// Yield Controller - مراقب الإنتاجية
// Field-First Architecture - Pre-Harvest Alerts
// ═══════════════════════════════════════════════════════════════════════════════

import { Controller, Get, Post, Param, Query, Body, UseGuards, Req, UsePipes, ValidationPipe } from "@nestjs/common";
import { JwtAuthGuard } from "@sahool/nestjs-auth";
import { ApiTags, ApiOperation, ApiResponse, ApiQuery, ApiProperty } from "@nestjs/swagger";
import { IsNumber, IsOptional, IsString, IsIn, Min, Max } from "class-validator";
import { Type } from "class-transformer";
import {
  YieldService,
  ActionTemplate,
  PreHarvestAlertResponse,
  FEATURE_SCHEMA,
  validateFeatureInput,
} from "./yield.service";

// ─────────────────────────────────────────────────────────────────────────────
// DTOs - التحقق من صحة المدخلات
// ─────────────────────────────────────────────────────────────────────────────

class ValidateInputDto {
  @IsOptional()
  @IsNumber()
  @Min(-1.0)
  @Max(1.0)
  @Type(() => Number)
  @ApiProperty({ required: false, minimum: -1.0, maximum: 1.0, description: "NDVI index value" })
  ndvi?: number;

  @IsOptional()
  @IsNumber()
  @Min(0.01)
  @Max(10000)
  @Type(() => Number)
  @ApiProperty({ required: false, minimum: 0.01, maximum: 10000, description: "Field area in hectares" })
  areaHectares?: number;

  @IsOptional()
  @IsNumber()
  @Min(0)
  @Max(100)
  @Type(() => Number)
  @ApiProperty({ required: false, minimum: 0, maximum: 100, description: "Growth stage percentage" })
  growthStagePercent?: number;

  @IsOptional()
  @IsNumber()
  @Min(0)
  @Max(50000)
  @Type(() => Number)
  @ApiProperty({ required: false, minimum: 0, maximum: 50000, description: "Historical yield in kg/ha" })
  historicalYieldKgHa?: number;

  @IsOptional()
  @IsNumber()
  @Min(0)
  @Max(1)
  @Type(() => Number)
  @ApiProperty({ required: false, minimum: 0, maximum: 1, description: "Water stress factor (0-1)" })
  waterStressFactor?: number;

  @IsOptional()
  @IsNumber()
  @Min(0)
  @Max(1)
  @Type(() => Number)
  @ApiProperty({ required: false, minimum: 0, maximum: 1, description: "Disease factor (0-1)" })
  diseaseFactor?: number;

  @IsOptional()
  @IsNumber()
  @Min(0)
  @Max(100)
  @Type(() => Number)
  @ApiProperty({ required: false, minimum: 0, maximum: 100, description: "Grain moisture percentage" })
  grainMoisture?: number;

  @IsOptional()
  @IsNumber()
  @Min(-10)
  @Max(60)
  @Type(() => Number)
  @ApiProperty({ required: false, minimum: -10, maximum: 60, description: "Canopy temperature in °C" })
  canopyTemperature?: number;

  @IsOptional()
  @IsString()
  @IsIn(["wheat", "coffee", "sorghum", "tomato", "barley", "date_palm", "mango", "grape"])
  @ApiProperty({ required: false, enum: ["wheat", "coffee", "sorghum", "tomato", "barley", "date_palm", "mango", "grape"] })
  cropType?: string;
}

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

  @Post("validate-input")
  @UsePipes(new ValidationPipe({ transform: true, whitelist: true }))
  @ApiOperation({
    summary: "Validate ML input data",
    description: "التحقق من صحة بيانات الإدخال مقابل مخطط المدخلات لكشف انحراف البيانات",
  })
  @ApiResponse({ status: 200, description: "Validation result" })
  @ApiResponse({ status: 400, description: "Invalid input data" })
  validateInput(@Body() data: ValidateInputDto) {
    const result = validateFeatureInput(data as Record<string, unknown>);
    return {
      ...result,
      schema_version: FEATURE_SCHEMA.version,
    };
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
  healthCheck() {
    return {
      status: "ok",
      service: "yield-prediction",
      timestamp: new Date().toISOString(),
    };
  }
}
