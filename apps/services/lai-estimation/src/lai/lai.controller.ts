// ═══════════════════════════════════════════════════════════════════════════════
// LAI Controller - مراقب مؤشر مساحة الأوراق
// Field-First Architecture - Early Stress Detection
// ═══════════════════════════════════════════════════════════════════════════════

import { Controller, Get, Post, Body, Param, Query } from "@nestjs/common";
import { ApiTags, ApiOperation, ApiResponse, ApiQuery } from "@nestjs/swagger";
import { LAIService, StressDetectionResponse } from "./lai.service";
import {
  DataSource,
  CropType,
  EstimateLAIDto,
  CalculateLAIFromBandsDto,
  TimeSeriesLAIDto,
} from "./lai.dto";

@ApiTags("lai")
@Controller("api/v1/lai")
export class LAIController {
  constructor(private readonly laiService: LAIService) {}

  // ─────────────────────────────────────────────────────────────────────────────
  // Estimate LAI for Field
  // تقدير مؤشر مساحة الأوراق للحقل
  // ─────────────────────────────────────────────────────────────────────────────

  @Get("estimate/:fieldId")
  @ApiOperation({
    summary: "Estimate LAI for a field",
    description: "تقدير مؤشر مساحة الأوراق للحقل باستخدام LAI-TransNet",
  })
  @ApiQuery({ name: "dataSource", enum: DataSource, required: false })
  @ApiQuery({ name: "cropType", enum: CropType, required: false })
  @ApiQuery({ name: "date", required: false, type: String })
  @ApiResponse({ status: 200, description: "LAI estimation result" })
  async estimateLAI(
    @Param("fieldId") fieldId: string,
    @Query("dataSource") dataSource?: DataSource,
    @Query("cropType") cropType?: CropType,
    @Query("date") date?: string,
  ) {
    return this.laiService.estimateLAI(
      fieldId,
      dataSource || DataSource.FUSION,
      cropType,
      date,
    );
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Calculate LAI from Spectral Bands
  // حساب مؤشر مساحة الأوراق من النطاقات الطيفية
  // ─────────────────────────────────────────────────────────────────────────────

  @Post("calculate")
  @ApiOperation({
    summary: "Calculate LAI from spectral bands",
    description: "حساب مؤشر مساحة الأوراق من القيم الطيفية الخام",
  })
  @ApiResponse({ status: 200, description: "LAI calculation result" })
  calculateLAI(@Body() dto: CalculateLAIFromBandsDto) {
    const indices = this.laiService.calculateVegetationIndices(dto.bands);
    return this.laiService.estimateLAIFromIndices(
      indices,
      dto.cropType,
      dto.growthStage,
    );
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get LAI Time Series
  // الحصول على السلسلة الزمنية لمؤشر مساحة الأوراق
  // ─────────────────────────────────────────────────────────────────────────────

  @Get("timeseries/:fieldId")
  @ApiOperation({
    summary: "Get LAI time series for a field",
    description: "الحصول على السلسلة الزمنية لمؤشر مساحة الأوراق",
  })
  @ApiQuery({ name: "startDate", required: false, type: String })
  @ApiQuery({ name: "endDate", required: false, type: String })
  @ApiQuery({ name: "dataSource", enum: DataSource, required: false })
  @ApiResponse({ status: 200, description: "LAI time series data" })
  async getLAITimeSeries(
    @Param("fieldId") fieldId: string,
    @Query("startDate") startDate?: string,
    @Query("endDate") endDate?: string,
    @Query("dataSource") dataSource?: DataSource,
  ) {
    return this.laiService.getLAITimeSeries(
      fieldId,
      startDate,
      endDate,
      dataSource || DataSource.PLANETSCOPE,
    );
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Compare LAI with Optimal
  // مقارنة مؤشر مساحة الأوراق مع المثالي
  // ─────────────────────────────────────────────────────────────────────────────

  @Get("compare/:fieldId")
  @ApiOperation({
    summary: "Compare field LAI with optimal values",
    description: "مقارنة مؤشر مساحة الأوراق للحقل مع القيم المثلى",
  })
  @ApiQuery({ name: "cropType", enum: CropType, required: false })
  @ApiResponse({ status: 200, description: "LAI comparison result" })
  async compareLAI(
    @Param("fieldId") fieldId: string,
    @Query("cropType") cropType?: CropType,
  ) {
    return this.laiService.compareLAI(fieldId, cropType || CropType.SOYBEAN);
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Model Information
  // معلومات النموذج
  // ─────────────────────────────────────────────────────────────────────────────

  @Get("model/info")
  @ApiOperation({
    summary: "Get LAI-TransNet model information",
    description: "الحصول على معلومات نموذج LAI-TransNet",
  })
  @ApiResponse({ status: 200, description: "Model information" })
  getModelInfo() {
    return this.laiService.getModelInfo();
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Field-First: Stress Detection with ActionTemplate
  // الكشف المبكر عن الإجهاد مع قالب الإجراء
  // ─────────────────────────────────────────────────────────────────────────────

  @Get("stress-detection/:fieldId")
  @ApiOperation({
    summary: "Detect early stress with ActionTemplate",
    description: "الكشف المبكر عن الإجهاد مع قالب إجراء - Field-First",
  })
  @ApiQuery({ name: "cropType", enum: CropType, required: false })
  @ApiQuery({ name: "farmerId", required: false })
  @ApiQuery({ name: "tenantId", required: false })
  @ApiResponse({
    status: 200,
    description: "Stress detection with ActionTemplate",
  })
  async detectStress(
    @Param("fieldId") fieldId: string,
    @Query("cropType") cropType?: CropType,
    @Query("farmerId") farmerId?: string,
    @Query("tenantId") tenantId?: string,
  ): Promise<StressDetectionResponse> {
    return this.laiService.detectStressWithAction(
      fieldId,
      cropType || CropType.SOYBEAN,
      farmerId,
      tenantId,
    );
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Field-First: LAI Anomaly Alert
  // تنبيه شذوذ LAI
  // ─────────────────────────────────────────────────────────────────────────────

  @Get("anomaly-check/:fieldId")
  @ApiOperation({
    summary: "Check for LAI anomalies with ActionTemplate",
    description: "فحص شذوذ LAI مع توصيات عملية",
  })
  @ApiQuery({ name: "cropType", enum: CropType, required: false })
  async checkAnomaly(
    @Param("fieldId") fieldId: string,
    @Query("cropType") cropType?: CropType,
    @Query("farmerId") farmerId?: string,
  ) {
    return this.laiService.checkAnomalyWithAction(
      fieldId,
      cropType || CropType.SOYBEAN,
      farmerId,
    );
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Health Check
  // ─────────────────────────────────────────────────────────────────────────────

  @Get("health")
  healthCheck() {
    return {
      status: "ok",
      service: "lai-estimation",
      model: "LAI-TransNet",
      timestamp: new Date().toISOString(),
    };
  }
}
