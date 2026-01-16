// ═══════════════════════════════════════════════════════════════════════════════
// Photosynthesis Controller - مراقب التمثيل الضوئي
// Based on Farquhar-von Caemmerer-Berry (FvCB) Model and Light Use Efficiency
// ═══════════════════════════════════════════════════════════════════════════════

import { Controller, Get, Post, Body, Param, Query } from "@nestjs/common";
import {
  ApiTags,
  ApiOperation,
  ApiResponse,
  ApiQuery,
  ApiBody,
  ApiParam,
} from "@nestjs/swagger";
import { PhotosynthesisService } from "./photosynthesis.service";

class GPPInput {
  par: number;
  fpar: number;
  cropType: string;
  temperature?: number;
}

class PhotosynthesisInput {
  ci: number;
  par: number;
  cropType: string;
  temperature?: number;
}

@ApiTags("photosynthesis")
@Controller("api/v1/photosynthesis")
export class PhotosynthesisController {
  constructor(private readonly photosynthesisService: PhotosynthesisService) {}

  // ─────────────────────────────────────────────────────────────────────────────
  // Calculate Gross Primary Production (GPP)
  // حساب الإنتاج الأولي الإجمالي
  // ─────────────────────────────────────────────────────────────────────────────

  @Post("gpp")
  @ApiOperation({
    summary: "Calculate Gross Primary Production using LUE model",
    description:
      "حساب الإنتاج الأولي الإجمالي باستخدام نموذج كفاءة استخدام الضوء (LUE)",
  })
  @ApiBody({
    description: "GPP calculation parameters",
    schema: {
      type: "object",
      properties: {
        par: {
          type: "number",
          example: 8.5,
          description: "PAR (MJ m⁻² day⁻¹)",
        },
        fpar: {
          type: "number",
          example: 0.85,
          description: "Fraction of PAR absorbed (0-1)",
        },
        cropType: {
          type: "string",
          example: "WHEAT",
          description: "Crop type identifier",
        },
        temperature: {
          type: "number",
          example: 25,
          description: "Temperature (°C)",
        },
      },
      required: ["par", "fpar", "cropType"],
    },
  })
  @ApiResponse({ status: 200, description: "GPP calculation result" })
  calculateGPP(@Body() input: GPPInput) {
    const result = this.photosynthesisService.calculateGrossPrimaryProduction(
      input.par,
      input.fpar,
      input.cropType,
      input.temperature,
    );

    return {
      input: {
        par: input.par,
        fpar: input.fpar,
        cropType: input.cropType,
        temperature: input.temperature,
      },
      result,
      formula: "GPP = PAR × fPAR × LUE × temperature_scalar",
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Calculate Net Photosynthesis (Farquhar Model)
  // حساب التمثيل الضوئي الصافي (نموذج فاركوار)
  // ─────────────────────────────────────────────────────────────────────────────

  @Post("farquhar")
  @ApiOperation({
    summary: "Calculate net photosynthesis using Farquhar model",
    description: "حساب التمثيل الضوئي الصافي باستخدام نموذج فاركوار (FvCB)",
  })
  @ApiBody({
    description: "Farquhar model parameters",
    schema: {
      type: "object",
      properties: {
        ci: {
          type: "number",
          example: 280,
          description: "Intercellular CO₂ (μmol mol⁻¹)",
        },
        par: {
          type: "number",
          example: 1500,
          description: "PAR (μmol m⁻² s⁻¹)",
        },
        cropType: {
          type: "string",
          example: "CORN",
          description: "Crop type identifier",
        },
        temperature: {
          type: "number",
          example: 30,
          description: "Leaf temperature (°C)",
        },
      },
      required: ["ci", "par", "cropType"],
    },
  })
  @ApiResponse({
    status: 200,
    description: "Farquhar model calculation result",
  })
  calculateFarquhar(@Body() input: PhotosynthesisInput) {
    const result = this.photosynthesisService.calculateNetPhotosynthesis(
      input.ci,
      input.par,
      input.cropType,
      input.temperature ?? 25,
    );

    return {
      input: {
        ci: input.ci,
        par: input.par,
        cropType: input.cropType,
        temperature: input.temperature ?? 25,
      },
      result,
      model: "Farquhar-von Caemmerer-Berry (FvCB)",
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Generate Light Response Curve
  // إنشاء منحنى استجابة الضوء
  // ─────────────────────────────────────────────────────────────────────────────

  @Get("curve/light/:cropType")
  @ApiOperation({
    summary: "Generate light response curve",
    description: "إنشاء منحنى استجابة التمثيل الضوئي للضوء",
  })
  @ApiParam({
    name: "cropType",
    example: "WHEAT",
    description: "Crop type identifier",
  })
  @ApiQuery({
    name: "ci",
    required: false,
    example: 400,
    description: "CO₂ concentration",
  })
  @ApiQuery({
    name: "temperature",
    required: false,
    example: 25,
    description: "Temperature (°C)",
  })
  @ApiResponse({ status: 200, description: "Light response curve data" })
  getLightResponseCurve(
    @Param("cropType") cropType: string,
    @Query("ci") ci?: string,
    @Query("temperature") temperature?: string,
  ) {
    const ciValue = ci ? parseFloat(ci) : 400;
    const tempValue = temperature ? parseFloat(temperature) : 25;

    const curve = this.photosynthesisService.generateLightResponseCurve(
      cropType,
      ciValue,
      tempValue,
    );

    return {
      parameters: {
        cropType,
        ci: ciValue,
        temperature: tempValue,
      },
      curve,
      description: "Light response curve showing An vs PAR",
      descriptionAr: "منحنى استجابة الضوء يوضح An مقابل PAR",
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Generate CO2 Response Curve (A-Ci)
  // إنشاء منحنى استجابة ثاني أكسيد الكربون
  // ─────────────────────────────────────────────────────────────────────────────

  @Get("curve/co2/:cropType")
  @ApiOperation({
    summary: "Generate CO₂ response curve (A-Ci)",
    description: "إنشاء منحنى استجابة التمثيل الضوئي لثاني أكسيد الكربون",
  })
  @ApiParam({
    name: "cropType",
    example: "SOYBEAN",
    description: "Crop type identifier",
  })
  @ApiQuery({
    name: "par",
    required: false,
    example: 1500,
    description: "PAR (μmol m⁻² s⁻¹)",
  })
  @ApiQuery({
    name: "temperature",
    required: false,
    example: 25,
    description: "Temperature (°C)",
  })
  @ApiResponse({ status: 200, description: "CO₂ response curve data" })
  getCO2ResponseCurve(
    @Param("cropType") cropType: string,
    @Query("par") par?: string,
    @Query("temperature") temperature?: string,
  ) {
    const parValue = par ? parseFloat(par) : 1500;
    const tempValue = temperature ? parseFloat(temperature) : 25;

    const curve = this.photosynthesisService.generateCO2ResponseCurve(
      cropType,
      parValue,
      tempValue,
    );

    return {
      parameters: {
        cropType,
        par: parValue,
        temperature: tempValue,
      },
      curve,
      description: "A-Ci curve showing An vs intercellular CO₂",
      descriptionAr: "منحنى A-Ci يوضح An مقابل تركيز CO₂ بين الخلايا",
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Generate Temperature Response Curve
  // إنشاء منحنى استجابة درجة الحرارة
  // ─────────────────────────────────────────────────────────────────────────────

  @Get("curve/temperature/:cropType")
  @ApiOperation({
    summary: "Generate temperature response curve",
    description: "إنشاء منحنى استجابة التمثيل الضوئي لدرجة الحرارة",
  })
  @ApiParam({
    name: "cropType",
    example: "RICE",
    description: "Crop type identifier",
  })
  @ApiQuery({
    name: "par",
    required: false,
    example: 1500,
    description: "PAR (μmol m⁻² s⁻¹)",
  })
  @ApiQuery({
    name: "ci",
    required: false,
    example: 400,
    description: "CO₂ concentration",
  })
  @ApiResponse({ status: 200, description: "Temperature response curve data" })
  getTemperatureResponseCurve(
    @Param("cropType") cropType: string,
    @Query("par") par?: string,
    @Query("ci") ci?: string,
  ) {
    const parValue = par ? parseFloat(par) : 1500;
    const ciValue = ci ? parseFloat(ci) : 400;

    const curve = this.photosynthesisService.generateTemperatureResponseCurve(
      cropType,
      parValue,
      ciValue,
    );

    return {
      parameters: {
        cropType,
        par: parValue,
        ci: ciValue,
      },
      curve,
      description:
        "Temperature response curve showing An and temperature scalar",
      descriptionAr: "منحنى استجابة درجة الحرارة يوضح An ومعامل الحرارة",
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Crop Photosynthesis Parameters
  // الحصول على معاملات التمثيل الضوئي للمحصول
  // ─────────────────────────────────────────────────────────────────────────────

  @Get("parameters/:cropType")
  @ApiOperation({
    summary: "Get crop photosynthesis parameters",
    description:
      "الحصول على معاملات التمثيل الضوئي للمحصول (Vcmax, Jmax, LUE, etc.)",
  })
  @ApiParam({
    name: "cropType",
    example: "CORN",
    description: "Crop type identifier",
  })
  @ApiResponse({ status: 200, description: "Crop photosynthesis parameters" })
  getCropParameters(@Param("cropType") cropType: string) {
    const params = this.photosynthesisService.getCropParameters(cropType);
    if (!params) {
      return {
        error: `Crop type ${cropType} not found`,
        availableCrops: this.photosynthesisService.getAvailableCrops(),
      };
    }
    return { cropType, parameters: params };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // List Available Crops
  // قائمة المحاصيل المتاحة
  // ─────────────────────────────────────────────────────────────────────────────

  @Get("crops")
  @ApiOperation({
    summary: "List available crops with photosynthesis models",
    description: "قائمة المحاصيل المتاحة مع نماذج التمثيل الضوئي",
  })
  @ApiResponse({ status: 200, description: "List of available crops" })
  listAvailableCrops() {
    const crops = this.photosynthesisService.getAvailableCrops();
    const c3Crops = crops.filter((c) => c.pathway === "C3");
    const c4Crops = crops.filter((c) => c.pathway === "C4");

    return {
      crops,
      summary: {
        total: crops.length,
        c3: c3Crops.length,
        c4: c4Crops.length,
      },
      pathwayInfo: {
        C3: "Calvin cycle only - less efficient at high temperatures",
        C4: "Hatch-Slack pathway - more efficient at high temperatures",
      },
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Health Check
  // فحص صحة الخدمة
  // ─────────────────────────────────────────────────────────────────────────────

  @Get("health")
  @ApiOperation({
    summary: "Photosynthesis service health check",
    description: "فحص صحة خدمة التمثيل الضوئي",
  })
  @ApiResponse({ status: 200, description: "Service is healthy" })
  healthCheck() {
    return {
      status: "healthy",
      service: "photosynthesis",
      timestamp: new Date().toISOString(),
      version: "1.0.0",
      models: ["LUE", "Farquhar-FvCB"],
    };
  }
}
