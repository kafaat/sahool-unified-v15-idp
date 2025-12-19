// ═══════════════════════════════════════════════════════════════════════════════
// Irrigation Decision Support Controller - مراقب دعم قرارات الري
// REST API for smart irrigation decision making
// ═══════════════════════════════════════════════════════════════════════════════

import { Controller, Get, Post, Body, Param, Query } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse, ApiQuery, ApiBody, ApiParam } from '@nestjs/swagger';
import { IrrigationDecisionService } from './irrigation-decision.service';

class ScenarioInput {
  budget: 'high' | 'medium' | 'low';
  terrain: 'plain' | 'mountain' | 'greenhouse' | 'terrace';
  cropType: string;
  cropValue: 'high' | 'medium' | 'low';
  technicalCapability: 'advanced' | 'basic' | 'minimal';
  waterAvailability: 'abundant' | 'limited' | 'scarce';
}

class ETcInput {
  cropType: string;
  daysAfterPlanting: number;
  et0: number;
  soilType: 'sandy' | 'loam' | 'clay' | 'silt';
  stressCoefficient?: number;
  growthStageAdjustment?: boolean;
}

class ThresholdInput {
  cropType: string;
  soilType: 'sandy' | 'loam' | 'clay' | 'silt';
  currentSoilMoisture: number;
  growthStage: 'seedling' | 'vegetative' | 'flowering' | 'maturity';
  rootDepth: number;
}

class SmartScheduleInput {
  cropType: string;
  sowingDate: string;
  soilParams: {
    fieldCapacity: number;
    wiltingPoint: number;
    currentMoisture: number;
    soilType: 'sandy' | 'loam' | 'clay' | 'silt';
  };
  weatherForecast: Array<{
    date: string;
    et0: number;
    precipitation: number;
    temperature: number;
  }>;
  irrigationSystem: {
    type: 'drip' | 'sprinkler' | 'furrow' | 'flood';
    efficiency: number;
  };
  budget: 'high' | 'medium' | 'low';
}

@ApiTags('irrigation-decision')
@Controller('api/v1/irrigation-decision')
export class IrrigationDecisionController {
  constructor(private readonly irrigationDecisionService: IrrigationDecisionService) {}

  // ─────────────────────────────────────────────────────────────────────────────
  // Select Optimal Method - اختيار الطريقة المثلى
  // ─────────────────────────────────────────────────────────────────────────────

  @Post('method-selector')
  @ApiOperation({
    summary: 'Select optimal irrigation decision method',
    description: 'اختيار طريقة اتخاذ قرار الري المثلى بناءً على السيناريو',
  })
  @ApiBody({
    description: 'Scenario parameters',
    schema: {
      type: 'object',
      properties: {
        budget: { type: 'string', enum: ['high', 'medium', 'low'], example: 'medium' },
        terrain: { type: 'string', enum: ['plain', 'mountain', 'greenhouse', 'terrace'], example: 'plain' },
        cropType: { type: 'string', example: 'CORN' },
        cropValue: { type: 'string', enum: ['high', 'medium', 'low'], example: 'medium' },
        technicalCapability: { type: 'string', enum: ['advanced', 'basic', 'minimal'], example: 'basic' },
        waterAvailability: { type: 'string', enum: ['abundant', 'limited', 'scarce'], example: 'limited' },
      },
      required: ['budget', 'terrain', 'cropType', 'cropValue', 'technicalCapability', 'waterAvailability'],
    },
  })
  @ApiResponse({ status: 200, description: 'Method recommendation' })
  selectMethod(@Body() input: ScenarioInput) {
    const recommendation = this.irrigationDecisionService.selectOptimalMethod(input);

    return {
      scenario: input,
      recommendation,
      timestamp: new Date().toISOString(),
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Calculate ETc - حساب التبخر-نتح للمحصول
  // ─────────────────────────────────────────────────────────────────────────────

  @Post('calculate-etc')
  @ApiOperation({
    summary: 'Calculate crop evapotranspiration (ETc)',
    description: 'حساب التبخر-نتح للمحصول باستخدام FAO-56 مع تعديلات ديناميكية',
  })
  @ApiBody({
    description: 'ETc calculation parameters',
    schema: {
      type: 'object',
      properties: {
        cropType: { type: 'string', example: 'CORN' },
        daysAfterPlanting: { type: 'number', example: 60 },
        et0: { type: 'number', example: 5.5, description: 'Reference ET (mm/day)' },
        soilType: { type: 'string', enum: ['sandy', 'loam', 'clay', 'silt'], example: 'loam' },
        stressCoefficient: { type: 'number', example: 1.0, description: 'Ks (0-1)' },
        growthStageAdjustment: { type: 'boolean', example: true },
      },
      required: ['cropType', 'daysAfterPlanting', 'et0', 'soilType'],
    },
  })
  @ApiResponse({ status: 200, description: 'ETc calculation result' })
  calculateETc(@Body() input: ETcInput) {
    const result = this.irrigationDecisionService.calculateETc(input);

    return {
      input: {
        cropType: input.cropType,
        daysAfterPlanting: input.daysAfterPlanting,
        et0: input.et0,
        soilType: input.soilType,
      },
      result,
      methodology: 'FAO-56 Penman-Monteith with dynamic Kc',
      reference: 'Allen et al., 1998 - FAO Irrigation and Drainage Paper 56',
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Threshold Control Decision - قرار التحكم بالعتبة
  // ─────────────────────────────────────────────────────────────────────────────

  @Post('threshold-control')
  @ApiOperation({
    summary: 'Evaluate threshold-based irrigation decision',
    description: 'تقييم قرار الري القائم على عتبة رطوبة التربة',
  })
  @ApiBody({
    description: 'Threshold control parameters',
    schema: {
      type: 'object',
      properties: {
        cropType: { type: 'string', example: 'TOMATO' },
        soilType: { type: 'string', enum: ['sandy', 'loam', 'clay', 'silt'], example: 'loam' },
        currentSoilMoisture: { type: 'number', example: 0.22, description: 'Volumetric water content (0-1)' },
        growthStage: { type: 'string', enum: ['seedling', 'vegetative', 'flowering', 'maturity'], example: 'flowering' },
        rootDepth: { type: 'number', example: 0.4, description: 'Current root depth (m)' },
      },
      required: ['cropType', 'soilType', 'currentSoilMoisture', 'growthStage', 'rootDepth'],
    },
  })
  @ApiResponse({ status: 200, description: 'Threshold control recommendation' })
  evaluateThreshold(@Body() input: ThresholdInput) {
    const recommendation = this.irrigationDecisionService.evaluateThresholdControl(input);

    return {
      input,
      recommendation,
      methodology: 'Soil moisture threshold control with growth-stage specific thresholds',
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Generate Smart Schedule - جدولة الري الذكي
  // ─────────────────────────────────────────────────────────────────────────────

  @Post('smart-schedule')
  @ApiOperation({
    summary: 'Generate smart irrigation schedule',
    description: 'إنشاء جدول ري ذكي بناءً على توقعات الطقس ونموذج المحصول',
  })
  @ApiBody({
    description: 'Smart schedule parameters',
    schema: {
      type: 'object',
      properties: {
        cropType: { type: 'string', example: 'WHEAT' },
        sowingDate: { type: 'string', example: '2024-10-15' },
        soilParams: {
          type: 'object',
          properties: {
            fieldCapacity: { type: 'number', example: 0.28 },
            wiltingPoint: { type: 'number', example: 0.12 },
            currentMoisture: { type: 'number', example: 0.24 },
            soilType: { type: 'string', enum: ['sandy', 'loam', 'clay', 'silt'], example: 'loam' },
          },
        },
        weatherForecast: {
          type: 'array',
          items: {
            type: 'object',
            properties: {
              date: { type: 'string' },
              et0: { type: 'number' },
              precipitation: { type: 'number' },
              temperature: { type: 'number' },
            },
          },
          example: [
            { date: '2024-11-01', et0: 3.5, precipitation: 0, temperature: 18 },
            { date: '2024-11-02', et0: 4.0, precipitation: 5, temperature: 20 },
          ],
        },
        irrigationSystem: {
          type: 'object',
          properties: {
            type: { type: 'string', enum: ['drip', 'sprinkler', 'furrow', 'flood'], example: 'drip' },
            efficiency: { type: 'number', example: 0.9 },
          },
        },
        budget: { type: 'string', enum: ['high', 'medium', 'low'], example: 'medium' },
      },
      required: ['cropType', 'sowingDate', 'soilParams', 'weatherForecast', 'irrigationSystem', 'budget'],
    },
  })
  @ApiResponse({ status: 200, description: 'Smart irrigation schedule' })
  generateSchedule(@Body() input: SmartScheduleInput) {
    const result = this.irrigationDecisionService.generateSmartSchedule(input);

    return {
      parameters: {
        cropType: input.cropType,
        sowingDate: input.sowingDate,
        forecastDays: input.weatherForecast.length,
        irrigationType: input.irrigationSystem.type,
      },
      ...result,
      timestamp: new Date().toISOString(),
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Compare Methods - مقارنة الطرق
  // ─────────────────────────────────────────────────────────────────────────────

  @Get('compare-methods')
  @ApiOperation({
    summary: 'Compare irrigation decision methods',
    description: 'مقارنة أساليب اتخاذ قرارات الري (FAO-56، العتبة، نماذج المحاصيل)',
  })
  @ApiResponse({ status: 200, description: 'Methods comparison' })
  compareMethods() {
    return this.irrigationDecisionService.compareMethods();
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Quick Recommendation - توصية سريعة
  // ─────────────────────────────────────────────────────────────────────────────

  @Get('quick-recommend')
  @ApiOperation({
    summary: 'Get quick irrigation recommendation',
    description: 'الحصول على توصية ري سريعة لسيناريو شائع',
  })
  @ApiQuery({ name: 'scenario', required: true, enum: ['small_farm', 'modern_garden', 'greenhouse', 'mountain', 'plain_large', 'high_value'] })
  @ApiResponse({ status: 200, description: 'Quick recommendation' })
  quickRecommend(@Query('scenario') scenario: string) {
    const scenarios: { [key: string]: ScenarioInput } = {
      small_farm: {
        budget: 'low',
        terrain: 'plain',
        cropType: 'WHEAT',
        cropValue: 'low',
        technicalCapability: 'minimal',
        waterAvailability: 'limited',
      },
      modern_garden: {
        budget: 'high',
        terrain: 'plain',
        cropType: 'TOMATO',
        cropValue: 'high',
        technicalCapability: 'advanced',
        waterAvailability: 'abundant',
      },
      greenhouse: {
        budget: 'high',
        terrain: 'greenhouse',
        cropType: 'STRAWBERRY',
        cropValue: 'high',
        technicalCapability: 'advanced',
        waterAvailability: 'abundant',
      },
      mountain: {
        budget: 'medium',
        terrain: 'mountain',
        cropType: 'GRAPE',
        cropValue: 'high',
        technicalCapability: 'basic',
        waterAvailability: 'limited',
      },
      plain_large: {
        budget: 'medium',
        terrain: 'plain',
        cropType: 'CORN',
        cropValue: 'medium',
        technicalCapability: 'basic',
        waterAvailability: 'abundant',
      },
      high_value: {
        budget: 'high',
        terrain: 'plain',
        cropType: 'GRAPE',
        cropValue: 'high',
        technicalCapability: 'advanced',
        waterAvailability: 'limited',
      },
    };

    const scenarioInput = scenarios[scenario];
    if (!scenarioInput) {
      return {
        error: `Unknown scenario: ${scenario}`,
        availableScenarios: Object.keys(scenarios),
      };
    }

    const recommendation = this.irrigationDecisionService.selectOptimalMethod(scenarioInput);

    return {
      scenario,
      scenarioDetails: scenarioInput,
      recommendation,
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Crop Parameters - الحصول على معاملات المحصول
  // ─────────────────────────────────────────────────────────────────────────────

  @Get('crops')
  @ApiOperation({
    summary: 'List available crops with Kc parameters',
    description: 'قائمة المحاصيل المتاحة مع معاملات Kc',
  })
  @ApiResponse({ status: 200, description: 'List of crops' })
  listCrops() {
    const crops = this.irrigationDecisionService.getAvailableCrops();
    const cropsWithParams = crops.map(crop => ({
      name: crop,
      params: this.irrigationDecisionService.getCropParams(crop),
    }));

    return {
      crops: cropsWithParams,
      total: crops.length,
    };
  }

  @Get('crops/:cropType')
  @ApiOperation({
    summary: 'Get crop Kc parameters',
    description: 'الحصول على معاملات Kc للمحصول',
  })
  @ApiParam({ name: 'cropType', example: 'CORN' })
  @ApiResponse({ status: 200, description: 'Crop parameters' })
  getCropParams(@Param('cropType') cropType: string) {
    const params = this.irrigationDecisionService.getCropParams(cropType);

    if (!params) {
      return {
        error: `Crop type ${cropType} not found`,
        availableCrops: this.irrigationDecisionService.getAvailableCrops(),
      };
    }

    return {
      cropType: cropType.toUpperCase(),
      params,
      reference: 'FAO-56 Table 12 - Single crop coefficients',
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Soil Types - الحصول على أنواع التربة
  // ─────────────────────────────────────────────────────────────────────────────

  @Get('soils')
  @ApiOperation({
    summary: 'List soil types with properties',
    description: 'قائمة أنواع التربة مع خصائصها',
  })
  @ApiResponse({ status: 200, description: 'List of soil types' })
  listSoils() {
    const soils = this.irrigationDecisionService.getSoilTypes();
    const soilsWithProps = soils.map(soil => ({
      type: soil,
      properties: this.irrigationDecisionService.getSoilProperties(soil),
    }));

    return {
      soils: soilsWithProps,
      total: soils.length,
    };
  }

  @Get('soils/:soilType')
  @ApiOperation({
    summary: 'Get soil properties',
    description: 'الحصول على خصائص التربة',
  })
  @ApiParam({ name: 'soilType', example: 'loam' })
  @ApiResponse({ status: 200, description: 'Soil properties' })
  getSoilProperties(@Param('soilType') soilType: string) {
    const properties = this.irrigationDecisionService.getSoilProperties(soilType);

    if (!properties) {
      return {
        error: `Soil type ${soilType} not found`,
        availableSoils: this.irrigationDecisionService.getSoilTypes(),
      };
    }

    return {
      soilType,
      properties,
      units: {
        fieldCapacity: 'cm³/cm³',
        wiltingPoint: 'cm³/cm³',
        saturation: 'cm³/cm³',
        hydraulicConductivity: 'mm/day',
        availableWater: 'mm/m',
      },
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Health Check
  // ─────────────────────────────────────────────────────────────────────────────

  @Get('health')
  @ApiOperation({
    summary: 'Irrigation decision service health check',
    description: 'فحص صحة خدمة قرارات الري',
  })
  @ApiResponse({ status: 200, description: 'Service is healthy' })
  healthCheck() {
    return {
      status: 'healthy',
      service: 'irrigation-decision',
      timestamp: new Date().toISOString(),
      version: '1.0.0',
      methods: ['FAO-56', 'Threshold Control', 'Crop Growth Models', 'Hybrid'],
      supportedCrops: this.irrigationDecisionService.getAvailableCrops().length,
      supportedSoils: this.irrigationDecisionService.getSoilTypes().length,
      references: [
        'FAO-56 Penman-Monteith',
        'FAO-33 Yield Response to Water',
        'DSSAT-CSM',
        'AquaCrop',
        'IrriPro Methodology',
      ],
    };
  }
}
