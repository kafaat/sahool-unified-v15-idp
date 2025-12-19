// ═══════════════════════════════════════════════════════════════════════════════
// Root Growth Controller - مراقب نمو الجذور
// Based on SimRoot 3D Root Architecture Model
// ═══════════════════════════════════════════════════════════════════════════════

import { Controller, Get, Post, Body, Param, Query } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse, ApiQuery, ApiBody, ApiParam } from '@nestjs/swagger';
import { RootGrowthService } from './root-growth.service';

class RootDepthInput {
  cropType: string;
  daysAfterEmergence: number;
  soilTemperature?: number;
  waterStress?: number;
}

class WaterUptakeInput {
  cropType: string;
  potentialTranspiration: number;
  rootDepth: number;
  soilLayers: Array<{
    depth: number;
    thickness: number;
    waterContent: number;
    fieldCapacity: number;
    wiltingPoint: number;
    bulkDensity: number;
    nitrogen: number;
    phosphorus: number;
    potassium: number;
  }>;
}

class NutrientUptakeInput {
  cropType: string;
  rootBiomass: number;
  soilNutrientConc: {
    nitrogen: number;
    phosphorus: number;
    potassium: number;
  };
  waterUptake: number;
}

class RootArchitectureInput {
  cropType: string;
  daysAfterEmergence: number;
  soilConditions: {
    temperature: number;
    waterStress: number;
    nutrientStress: number;
  };
}

@ApiTags('root-growth')
@Controller('api/v1/roots')
export class RootGrowthController {
  constructor(private readonly rootGrowthService: RootGrowthService) {}

  // ─────────────────────────────────────────────────────────────────────────────
  // Calculate Root Depth
  // حساب عمق الجذور
  // ─────────────────────────────────────────────────────────────────────────────

  @Post('depth')
  @ApiOperation({
    summary: 'Calculate current root depth',
    description: 'حساب عمق الجذور الحالي بناءً على أيام بعد الإنبات والظروف البيئية',
  })
  @ApiBody({
    description: 'Root depth calculation parameters',
    schema: {
      type: 'object',
      properties: {
        cropType: { type: 'string', example: 'CORN' },
        daysAfterEmergence: { type: 'number', example: 45 },
        soilTemperature: { type: 'number', example: 22 },
        waterStress: { type: 'number', example: 0.9 },
      },
      required: ['cropType', 'daysAfterEmergence'],
    },
  })
  @ApiResponse({ status: 200, description: 'Root depth calculation' })
  calculateRootDepth(@Body() input: RootDepthInput) {
    const result = this.rootGrowthService.calculateRootDepth(
      input.cropType,
      input.daysAfterEmergence,
      input.soilTemperature ?? 20,
      input.waterStress ?? 1.0,
    );

    return {
      input,
      result,
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Calculate Root Length Density Profile
  // حساب توزيع كثافة طول الجذور
  // ─────────────────────────────────────────────────────────────────────────────

  @Get('rld/:cropType')
  @ApiOperation({
    summary: 'Get root length density profile',
    description: 'الحصول على توزيع كثافة طول الجذور مع العمق',
  })
  @ApiParam({ name: 'cropType', example: 'WHEAT' })
  @ApiQuery({ name: 'rootBiomass', required: true, example: 150, description: 'Root biomass (g m⁻²)' })
  @ApiQuery({ name: 'rootDepth', required: true, example: 80, description: 'Current root depth (cm)' })
  @ApiResponse({ status: 200, description: 'Root length density profile' })
  getRootLengthDensity(
    @Param('cropType') cropType: string,
    @Query('rootBiomass') rootBiomass: string,
    @Query('rootDepth') rootDepth: string,
  ) {
    const profile = this.rootGrowthService.calculateRootLengthDensity(
      cropType,
      parseFloat(rootBiomass),
      parseFloat(rootDepth),
    );

    return {
      parameters: {
        cropType,
        rootBiomass: parseFloat(rootBiomass),
        rootDepth: parseFloat(rootDepth),
      },
      profile,
      description: 'Root length density decreases exponentially with depth',
      descriptionAr: 'كثافة طول الجذور تتناقص أسياً مع العمق',
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Calculate Water Uptake
  // حساب امتصاص الماء
  // ─────────────────────────────────────────────────────────────────────────────

  @Post('water-uptake')
  @ApiOperation({
    summary: 'Calculate water uptake by roots (Feddes model)',
    description: 'حساب امتصاص الماء بواسطة الجذور باستخدام نموذج فيديز',
  })
  @ApiBody({
    description: 'Water uptake parameters',
    schema: {
      type: 'object',
      properties: {
        cropType: { type: 'string', example: 'RICE' },
        potentialTranspiration: { type: 'number', example: 5, description: 'mm day⁻¹' },
        rootDepth: { type: 'number', example: 40, description: 'cm' },
        soilLayers: {
          type: 'array',
          items: {
            type: 'object',
            properties: {
              depth: { type: 'number', example: 10 },
              thickness: { type: 'number', example: 10 },
              waterContent: { type: 'number', example: 0.25 },
              fieldCapacity: { type: 'number', example: 0.35 },
              wiltingPoint: { type: 'number', example: 0.12 },
            },
          },
        },
      },
      required: ['cropType', 'potentialTranspiration', 'rootDepth', 'soilLayers'],
    },
  })
  @ApiResponse({ status: 200, description: 'Water uptake calculation' })
  calculateWaterUptake(@Body() input: WaterUptakeInput) {
    const result = this.rootGrowthService.calculateWaterUptake(
      input.cropType,
      input.potentialTranspiration,
      input.soilLayers,
      input.rootDepth,
    );

    return {
      input: {
        cropType: input.cropType,
        potentialTranspiration: input.potentialTranspiration,
        rootDepth: input.rootDepth,
        soilLayersCount: input.soilLayers.length,
      },
      result,
      model: 'Feddes water uptake model',
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Calculate Nutrient Uptake
  // حساب امتصاص المغذيات
  // ─────────────────────────────────────────────────────────────────────────────

  @Post('nutrient-uptake')
  @ApiOperation({
    summary: 'Calculate nutrient uptake (Michaelis-Menten)',
    description: 'حساب امتصاص المغذيات باستخدام حركية ميكايليس-مينتين',
  })
  @ApiBody({
    description: 'Nutrient uptake parameters',
    schema: {
      type: 'object',
      properties: {
        cropType: { type: 'string', example: 'SOYBEAN' },
        rootBiomass: { type: 'number', example: 100, description: 'g m⁻²' },
        soilNutrientConc: {
          type: 'object',
          properties: {
            nitrogen: { type: 'number', example: 100, description: 'μmol L⁻¹' },
            phosphorus: { type: 'number', example: 10 },
            potassium: { type: 'number', example: 50 },
          },
        },
        waterUptake: { type: 'number', example: 4, description: 'mm day⁻¹' },
      },
      required: ['cropType', 'rootBiomass', 'soilNutrientConc', 'waterUptake'],
    },
  })
  @ApiResponse({ status: 200, description: 'Nutrient uptake calculation' })
  calculateNutrientUptake(@Body() input: NutrientUptakeInput) {
    const result = this.rootGrowthService.calculateNutrientUptake(
      input.cropType,
      input.rootBiomass,
      input.soilNutrientConc,
      input.waterUptake,
    );

    return {
      input,
      result,
      model: 'Michaelis-Menten kinetics',
      formula: 'V = Vmax × [S] / (Km + [S])',
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Simulate Root Architecture
  // محاكاة بنية الجذور
  // ─────────────────────────────────────────────────────────────────────────────

  @Post('architecture')
  @ApiOperation({
    summary: 'Simulate 3D root architecture',
    description: 'محاكاة بنية الجذور ثلاثية الأبعاد على غرار SimRoot',
  })
  @ApiBody({
    description: 'Root architecture simulation parameters',
    schema: {
      type: 'object',
      properties: {
        cropType: { type: 'string', example: 'CORN' },
        daysAfterEmergence: { type: 'number', example: 60 },
        soilConditions: {
          type: 'object',
          properties: {
            temperature: { type: 'number', example: 22 },
            waterStress: { type: 'number', example: 0.85 },
            nutrientStress: { type: 'number', example: 0.9 },
          },
        },
      },
      required: ['cropType', 'daysAfterEmergence', 'soilConditions'],
    },
  })
  @ApiResponse({ status: 200, description: 'Root architecture simulation' })
  simulateArchitecture(@Body() input: RootArchitectureInput) {
    const result = this.rootGrowthService.simulateRootArchitecture(
      input.cropType,
      input.daysAfterEmergence,
      input.soilConditions,
    );

    return {
      input,
      result,
      model: 'SimRoot-inspired 3D architecture model',
      reference: 'Penn State Root Lab',
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Crop Root Parameters
  // الحصول على معاملات جذور المحصول
  // ─────────────────────────────────────────────────────────────────────────────

  @Get('parameters/:cropType')
  @ApiOperation({
    summary: 'Get crop root parameters',
    description: 'الحصول على معاملات نمو الجذور للمحصول',
  })
  @ApiParam({ name: 'cropType', example: 'SUGARCANE' })
  @ApiResponse({ status: 200, description: 'Root parameters' })
  getCropParameters(@Param('cropType') cropType: string) {
    const params = this.rootGrowthService.getCropParameters(cropType);
    if (!params) {
      return {
        error: `Crop type ${cropType} not found`,
        availableCrops: this.rootGrowthService.getAvailableCrops(),
      };
    }
    return { cropType, parameters: params };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // List Available Crops
  // قائمة المحاصيل المتاحة
  // ─────────────────────────────────────────────────────────────────────────────

  @Get('crops')
  @ApiOperation({
    summary: 'List crops with root growth models',
    description: 'قائمة المحاصيل مع نماذج نمو الجذور',
  })
  @ApiResponse({ status: 200, description: 'List of crops' })
  listCrops() {
    return {
      crops: this.rootGrowthService.getAvailableCrops(),
      total: this.rootGrowthService.getAvailableCrops().length,
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Health Check
  // ─────────────────────────────────────────────────────────────────────────────

  @Get('health')
  @ApiOperation({
    summary: 'Root growth service health check',
    description: 'فحص صحة خدمة نمو الجذور',
  })
  @ApiResponse({ status: 200, description: 'Service is healthy' })
  healthCheck() {
    return {
      status: 'healthy',
      service: 'root-growth',
      timestamp: new Date().toISOString(),
      version: '1.0.0',
      models: ['SimRoot-3D', 'Feddes', 'Michaelis-Menten'],
    };
  }
}
