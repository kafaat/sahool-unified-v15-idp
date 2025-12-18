// ═══════════════════════════════════════════════════════════════════════════════
// Biomass Controller - مراقب الكتلة الحيوية
// Based on Source-Sink-Flow Assimilate Distribution Models (WOFOST/DSSAT)
// ═══════════════════════════════════════════════════════════════════════════════

import { Controller, Get, Post, Body, Param, Query } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse, ApiQuery, ApiBody, ApiParam } from '@nestjs/swagger';
import { BiomassService } from './biomass.service';

class BiomassProductionInput {
  par: number;
  fpar: number;
  cropType: string;
  temperature: number;
  existingBiomass?: { root: number; stem: number; leaf: number; storage: number };
}

class AssimilateDistributionInput {
  netProduction: number;
  cropType: string;
  dvs: number;
}

class BiomassSimulationInput {
  cropType: string;
  dailyData: Array<{
    date: string;
    par: number;
    fpar: number;
    temperature: number;
    dvs: number;
  }>;
}

class YieldInput {
  totalAbovegroundBiomass: number;
  cropType: string;
  moistureContent?: number;
}

@ApiTags('biomass')
@Controller('api/v1/biomass')
export class BiomassController {
  constructor(private readonly biomassService: BiomassService) {}

  // ─────────────────────────────────────────────────────────────────────────────
  // Calculate Daily Biomass Production
  // حساب إنتاج الكتلة الحيوية اليومي
  // ─────────────────────────────────────────────────────────────────────────────

  @Post('production')
  @ApiOperation({
    summary: 'Calculate daily biomass production',
    description: 'حساب إنتاج الكتلة الحيوية اليومي باستخدام نموذج RUE',
  })
  @ApiBody({
    description: 'Biomass production parameters',
    schema: {
      type: 'object',
      properties: {
        par: { type: 'number', example: 10, description: 'PAR (MJ m⁻² day⁻¹)' },
        fpar: { type: 'number', example: 0.85, description: 'Fraction of PAR intercepted (0-1)' },
        cropType: { type: 'string', example: 'WHEAT', description: 'Crop type identifier' },
        temperature: { type: 'number', example: 25, description: 'Temperature (°C)' },
        existingBiomass: {
          type: 'object',
          properties: {
            root: { type: 'number' },
            stem: { type: 'number' },
            leaf: { type: 'number' },
            storage: { type: 'number' },
          },
        },
      },
      required: ['par', 'fpar', 'cropType', 'temperature'],
    },
  })
  @ApiResponse({ status: 200, description: 'Biomass production calculation result' })
  calculateProduction(@Body() input: BiomassProductionInput) {
    const result = this.biomassService.calculateDailyBiomassProduction(
      input.par,
      input.fpar,
      input.cropType,
      input.temperature,
      input.existingBiomass,
    );

    return {
      input: {
        par: input.par,
        fpar: input.fpar,
        cropType: input.cropType,
        temperature: input.temperature,
        existingBiomass: input.existingBiomass,
      },
      result,
      formula: 'Net = Gross - Maintenance_Resp - Growth_Resp',
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Distribute Assimilates
  // توزيع المواد المتمثلة
  // ─────────────────────────────────────────────────────────────────────────────

  @Post('distribute')
  @ApiOperation({
    summary: 'Distribute assimilates to plant organs',
    description: 'توزيع المواد المتمثلة على أعضاء النبات (جذور، ساق، أوراق، حبوب)',
  })
  @ApiBody({
    description: 'Assimilate distribution parameters',
    schema: {
      type: 'object',
      properties: {
        netProduction: { type: 'number', example: 15, description: 'Net production (g m⁻² day⁻¹)' },
        cropType: { type: 'string', example: 'CORN', description: 'Crop type identifier' },
        dvs: { type: 'number', example: 0.8, description: 'Development stage (0-2)' },
      },
      required: ['netProduction', 'cropType', 'dvs'],
    },
  })
  @ApiResponse({ status: 200, description: 'Assimilate distribution result' })
  distributeAssimilates(@Body() input: AssimilateDistributionInput) {
    const result = this.biomassService.distributeAssimilates(
      input.netProduction,
      input.cropType,
      input.dvs,
    );

    return {
      input: {
        netProduction: input.netProduction,
        cropType: input.cropType,
        dvs: input.dvs,
      },
      result,
      model: 'Source-Sink-Flow (WOFOST style)',
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Simulate Biomass Accumulation
  // محاكاة تراكم الكتلة الحيوية
  // ─────────────────────────────────────────────────────────────────────────────

  @Post('simulate')
  @ApiOperation({
    summary: 'Simulate biomass accumulation through season',
    description: 'محاكاة تراكم الكتلة الحيوية خلال موسم النمو',
  })
  @ApiBody({
    description: 'Simulation parameters with daily data',
    schema: {
      type: 'object',
      properties: {
        cropType: { type: 'string', example: 'RICE' },
        dailyData: {
          type: 'array',
          items: {
            type: 'object',
            properties: {
              date: { type: 'string', example: '2024-05-01' },
              par: { type: 'number', example: 12 },
              fpar: { type: 'number', example: 0.75 },
              temperature: { type: 'number', example: 28 },
              dvs: { type: 'number', example: 0.5 },
            },
          },
        },
      },
      required: ['cropType', 'dailyData'],
    },
  })
  @ApiResponse({ status: 200, description: 'Biomass simulation results' })
  simulateBiomass(@Body() input: BiomassSimulationInput) {
    const results = this.biomassService.simulateBiomassAccumulation(
      input.cropType,
      input.dailyData,
    );

    // Get final state
    const finalState = results[results.length - 1];

    return {
      simulation: {
        cropType: input.cropType,
        totalDays: input.dailyData.length,
      },
      summary: {
        finalBiomass: finalState.biomass,
        maxLAI: Math.max(...results.map(r => r.lai)),
        totalProduction: results.reduce((sum, r) => sum + r.grossProduction, 0),
      },
      dailyResults: results,
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Calculate Yield
  // حساب الغلة
  // ─────────────────────────────────────────────────────────────────────────────

  @Post('yield')
  @ApiOperation({
    summary: 'Calculate crop yield from total biomass',
    description: 'حساب غلة المحصول من إجمالي الكتلة الحيوية باستخدام مؤشر الحصاد',
  })
  @ApiBody({
    description: 'Yield calculation parameters',
    schema: {
      type: 'object',
      properties: {
        totalAbovegroundBiomass: { type: 'number', example: 1200, description: 'Total aboveground biomass (g m⁻²)' },
        cropType: { type: 'string', example: 'WHEAT', description: 'Crop type identifier' },
        moistureContent: { type: 'number', example: 0.14, description: 'Grain moisture content (0-1)' },
      },
      required: ['totalAbovegroundBiomass', 'cropType'],
    },
  })
  @ApiResponse({ status: 200, description: 'Yield calculation result' })
  calculateYield(@Body() input: YieldInput) {
    const result = this.biomassService.calculateYield(
      input.totalAbovegroundBiomass,
      input.cropType,
      input.moistureContent ?? 0.14,
    );

    return {
      input: {
        totalAbovegroundBiomass: input.totalAbovegroundBiomass,
        cropType: input.cropType,
        moistureContent: input.moistureContent ?? 0.14,
      },
      result,
      description: 'Yield calculated using Harvest Index (HI)',
      descriptionAr: 'تم حساب الغلة باستخدام مؤشر الحصاد',
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Calculate LAI from Leaf Biomass
  // حساب مؤشر مساحة الأوراق من كتلة الأوراق
  // ─────────────────────────────────────────────────────────────────────────────

  @Get('lai/:cropType')
  @ApiOperation({
    summary: 'Calculate LAI from leaf biomass',
    description: 'حساب مؤشر مساحة الأوراق (LAI) من كتلة الأوراق',
  })
  @ApiParam({ name: 'cropType', example: 'SOYBEAN', description: 'Crop type identifier' })
  @ApiQuery({ name: 'leafBiomass', required: true, example: 150, description: 'Leaf biomass (g m⁻²)' })
  @ApiResponse({ status: 200, description: 'LAI calculation result' })
  calculateLAI(
    @Param('cropType') cropType: string,
    @Query('leafBiomass') leafBiomass: string,
  ) {
    const biomass = parseFloat(leafBiomass);
    const result = this.biomassService.calculateLAI(biomass, cropType);

    return {
      input: { cropType, leafBiomass: biomass },
      result,
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Partitioning Coefficients
  // الحصول على معاملات التوزيع
  // ─────────────────────────────────────────────────────────────────────────────

  @Get('partitioning/:cropType')
  @ApiOperation({
    summary: 'Get partitioning coefficients for a crop',
    description: 'الحصول على معاملات توزيع المادة الجافة لمحصول معين',
  })
  @ApiParam({ name: 'cropType', example: 'CORN', description: 'Crop type identifier' })
  @ApiQuery({ name: 'dvs', required: false, example: 0.8, description: 'Development stage for current phase' })
  @ApiResponse({ status: 200, description: 'Partitioning coefficients' })
  getPartitioning(
    @Param('cropType') cropType: string,
    @Query('dvs') dvs?: string,
  ) {
    const dvsValue = dvs ? parseFloat(dvs) : undefined;
    return this.biomassService.getPartitioningCoefficients(cropType, dvsValue);
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Crop Biomass Parameters
  // الحصول على معاملات الكتلة الحيوية للمحصول
  // ─────────────────────────────────────────────────────────────────────────────

  @Get('parameters/:cropType')
  @ApiOperation({
    summary: 'Get biomass model parameters for a crop',
    description: 'الحصول على معاملات نموذج الكتلة الحيوية للمحصول',
  })
  @ApiParam({ name: 'cropType', example: 'RICE', description: 'Crop type identifier' })
  @ApiResponse({ status: 200, description: 'Crop biomass parameters' })
  getCropParameters(@Param('cropType') cropType: string) {
    const params = this.biomassService.getCropParameters(cropType);
    if (!params) {
      return {
        error: `Crop type ${cropType} not found`,
        availableCrops: this.biomassService.getAvailableCrops(),
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
    summary: 'List available crops with biomass models',
    description: 'قائمة المحاصيل المتاحة مع نماذج الكتلة الحيوية',
  })
  @ApiResponse({ status: 200, description: 'List of available crops' })
  listAvailableCrops() {
    return {
      crops: this.biomassService.getAvailableCrops(),
      total: this.biomassService.getAvailableCrops().length,
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Health Check
  // فحص صحة الخدمة
  // ─────────────────────────────────────────────────────────────────────────────

  @Get('health')
  @ApiOperation({
    summary: 'Biomass service health check',
    description: 'فحص صحة خدمة الكتلة الحيوية',
  })
  @ApiResponse({ status: 200, description: 'Service is healthy' })
  healthCheck() {
    return {
      status: 'healthy',
      service: 'biomass',
      timestamp: new Date().toISOString(),
      version: '1.0.0',
      models: ['RUE', 'Source-Sink-Flow', 'Harvest Index'],
    };
  }
}
