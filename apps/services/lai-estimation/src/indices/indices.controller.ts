// ═══════════════════════════════════════════════════════════════════════════════
// Vegetation Indices Controller - مراقب مؤشرات الغطاء النباتي
// ═══════════════════════════════════════════════════════════════════════════════

import { Controller, Get, Post, Body, Param, Query } from "@nestjs/common";
import {
  ApiTags,
  ApiOperation,
  ApiResponse,
  ApiQuery,
  ApiBody,
} from "@nestjs/swagger";
import { VegetationIndicesService, IndexInfo } from "./indices.service";

class SpectralBandsInput {
  green: number;
  red: number;
  redEdge: number;
  nir: number;
  blue?: number;
  swir?: number;
}

@ApiTags("indices")
@Controller("api/v1/indices")
export class VegetationIndicesController {
  constructor(private readonly indicesService: VegetationIndicesService) {}

  // ─────────────────────────────────────────────────────────────────────────────
  // Calculate All Vegetation Indices
  // حساب جميع مؤشرات الغطاء النباتي
  // ─────────────────────────────────────────────────────────────────────────────

  @Post("calculate")
  @ApiOperation({
    summary: "Calculate all vegetation indices from spectral bands",
    description: "حساب جميع مؤشرات الغطاء النباتي من النطاقات الطيفية",
  })
  @ApiBody({
    description: "Spectral band reflectance values (0-1)",
    schema: {
      type: "object",
      properties: {
        green: {
          type: "number",
          example: 0.08,
          description: "Green band (0-1)",
        },
        red: { type: "number", example: 0.05, description: "Red band (0-1)" },
        redEdge: {
          type: "number",
          example: 0.15,
          description: "Red Edge band (0-1)",
        },
        nir: { type: "number", example: 0.45, description: "NIR band (0-1)" },
      },
      required: ["green", "red", "redEdge", "nir"],
    },
  })
  @ApiResponse({
    status: 200,
    description: "All vegetation indices calculated",
  })
  calculateAllIndices(@Body() bands: SpectralBandsInput) {
    return this.indicesService.calculateAllIndices(bands);
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Calculate Single Index
  // حساب مؤشر واحد
  // ─────────────────────────────────────────────────────────────────────────────

  @Post("calculate/:indexName")
  @ApiOperation({
    summary: "Calculate a specific vegetation index",
    description: "حساب مؤشر غطاء نباتي محدد",
  })
  @ApiResponse({ status: 200, description: "Index calculation result" })
  calculateIndex(
    @Param("indexName") indexName: string,
    @Body() bands: SpectralBandsInput,
  ): {
    value: number;
    status: string;
    statusAr: string;
    info: IndexInfo;
  } | null {
    return this.indicesService.calculateIndex(indexName, bands);
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Analyze Vegetation Health
  // تحليل صحة الغطاء النباتي
  // ─────────────────────────────────────────────────────────────────────────────

  @Post("health")
  @ApiOperation({
    summary: "Analyze overall vegetation health from spectral bands",
    description: "تحليل صحة الغطاء النباتي الشاملة من النطاقات الطيفية",
  })
  @ApiResponse({ status: 200, description: "Vegetation health analysis" })
  analyzeHealth(@Body() bands: SpectralBandsInput) {
    return this.indicesService.analyzeVegetationHealth(bands);
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Index Information
  // الحصول على معلومات المؤشر
  // ─────────────────────────────────────────────────────────────────────────────

  @Get("info")
  @ApiOperation({
    summary: "Get information about all vegetation indices",
    description: "الحصول على معلومات حول جميع مؤشرات الغطاء النباتي",
  })
  @ApiResponse({ status: 200, description: "Index information" })
  getAllIndicesInfo(): Record<string, IndexInfo> {
    return this.indicesService.getIndexInfo() as Record<string, IndexInfo>;
  }

  @Get("info/:indexName")
  @ApiOperation({
    summary: "Get information about a specific vegetation index",
    description: "الحصول على معلومات حول مؤشر غطاء نباتي محدد",
  })
  @ApiResponse({ status: 200, description: "Index information" })
  getIndexInfo(@Param("indexName") indexName: string): IndexInfo | null {
    return this.indicesService.getIndexInfo(indexName) as IndexInfo | null;
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // List Available Indices
  // قائمة المؤشرات المتاحة
  // ─────────────────────────────────────────────────────────────────────────────

  @Get("list")
  @ApiOperation({
    summary: "List all available vegetation indices",
    description: "قائمة بجميع مؤشرات الغطاء النباتي المتاحة",
  })
  @ApiResponse({ status: 200, description: "List of available indices" })
  listAvailableIndices() {
    return this.indicesService.getAvailableIndices();
  }
}
