// ═══════════════════════════════════════════════════════════════════════════════
// Phenology Controller - مراقب مراحل النمو
// Based on WOFOST DVS (Development Stage) and thermal time accumulation
// ═══════════════════════════════════════════════════════════════════════════════

import { Controller, Get, Post, Body, Param, Query } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse, ApiQuery, ApiBody, ApiParam } from '@nestjs/swagger';
import { PhenologyService } from './phenology.service';

class GDDInput {
  tmin: number;
  tmax: number;
  tbase?: number;
  tmaxEff?: number;
}

class DVSInput {
  accumulatedGDD: number;
  cropType: string;
  afterFlowering?: boolean;
}

class SimulationInput {
  cropType: string;
  sowingDate: string;
  weatherData: Array<{ date: string; tmin: number; tmax: number }>;
}

class PredictDatesInput {
  cropType: string;
  sowingDate: string;
  avgDailyGDD?: number;
}

@ApiTags('phenology')
@Controller('api/v1/phenology')
export class PhenologyController {
  constructor(private readonly phenologyService: PhenologyService) {}

  // ─────────────────────────────────────────────────────────────────────────────
  // Calculate Growing Degree Days (GDD)
  // حساب درجات الحرارة المتراكمة
  // ─────────────────────────────────────────────────────────────────────────────

  @Post('gdd')
  @ApiOperation({
    summary: 'Calculate Growing Degree Days',
    description: 'حساب درجات الحرارة المتراكمة (GDD) لتحديد تطور المحصول',
  })
  @ApiBody({
    description: 'Temperature data for GDD calculation',
    schema: {
      type: 'object',
      properties: {
        tmin: { type: 'number', example: 15, description: 'Minimum temperature (°C)' },
        tmax: { type: 'number', example: 28, description: 'Maximum temperature (°C)' },
        tbase: { type: 'number', example: 10, description: 'Base temperature (°C)' },
        tmaxEff: { type: 'number', example: 30, description: 'Maximum effective temperature (°C)' },
      },
      required: ['tmin', 'tmax'],
    },
  })
  @ApiResponse({ status: 200, description: 'GDD calculation result' })
  calculateGDD(@Body() input: GDDInput) {
    const tbase = input.tbase ?? 10;
    const tmaxEff = input.tmaxEff ?? 30;

    const gdd = this.phenologyService.calculateGDD(
      input.tmin,
      input.tmax,
      tbase,
      tmaxEff,
    );

    return {
      input: {
        tmin: input.tmin,
        tmax: input.tmax,
        tbase,
        tmaxEff,
      },
      result: {
        gdd,
        unit: '°C·day',
        tavg: (input.tmin + input.tmax) / 2,
      },
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Calculate Development Stage (DVS)
  // حساب مرحلة التطور
  // ─────────────────────────────────────────────────────────────────────────────

  @Post('dvs')
  @ApiOperation({
    summary: 'Calculate Development Stage (DVS)',
    description: 'حساب مرحلة التطور DVS من درجات الحرارة المتراكمة - نظام WOFOST',
  })
  @ApiBody({
    description: 'Accumulated GDD and crop parameters',
    schema: {
      type: 'object',
      properties: {
        accumulatedGDD: { type: 'number', example: 500, description: 'Accumulated GDD (°C·day)' },
        cropType: { type: 'string', example: 'WHEAT', description: 'Crop type identifier' },
        afterFlowering: { type: 'boolean', example: false, description: 'Is crop past flowering?' },
      },
      required: ['accumulatedGDD', 'cropType'],
    },
  })
  @ApiResponse({ status: 200, description: 'DVS calculation result' })
  calculateDVS(@Body() input: DVSInput) {
    const result = this.phenologyService.calculateDVS(
      input.accumulatedGDD,
      input.cropType,
      input.afterFlowering ?? false,
    );

    return {
      input: {
        accumulatedGDD: input.accumulatedGDD,
        cropType: input.cropType,
        afterFlowering: input.afterFlowering ?? false,
      },
      result: {
        ...result,
        description: `DVS ${result.dvs} corresponds to ${result.stage.name} (${result.stage.nameAr})`,
      },
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Simulate Phenology for Season
  // محاكاة مراحل النمو للموسم
  // ─────────────────────────────────────────────────────────────────────────────

  @Post('simulate')
  @ApiOperation({
    summary: 'Simulate crop phenology through season',
    description: 'محاكاة مراحل نمو المحصول خلال الموسم باستخدام بيانات الطقس',
  })
  @ApiBody({
    description: 'Simulation parameters with weather data',
    schema: {
      type: 'object',
      properties: {
        cropType: { type: 'string', example: 'WHEAT' },
        sowingDate: { type: 'string', example: '2024-11-15' },
        weatherData: {
          type: 'array',
          items: {
            type: 'object',
            properties: {
              date: { type: 'string', example: '2024-11-15' },
              tmin: { type: 'number', example: 12 },
              tmax: { type: 'number', example: 25 },
            },
          },
        },
      },
      required: ['cropType', 'sowingDate', 'weatherData'],
    },
  })
  @ApiResponse({ status: 200, description: 'Phenology simulation results' })
  simulatePhenology(@Body() input: SimulationInput) {
    const results = this.phenologyService.simulatePhenology(
      input.cropType,
      input.sowingDate,
      input.weatherData,
    );

    // Extract key transitions
    const stageTransitions: Array<{ stage: string; stageAr: string; day: number; date: string }> = [];
    let lastStage = '';
    results.forEach((r) => {
      if (r.stage !== lastStage) {
        stageTransitions.push({
          stage: r.stage,
          stageAr: r.stageAr,
          day: r.day,
          date: r.date,
        });
        lastStage = r.stage;
      }
    });

    return {
      simulation: {
        cropType: input.cropType,
        sowingDate: input.sowingDate,
        totalDays: input.weatherData.length,
      },
      stageTransitions,
      dailyResults: results,
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Predict Key Dates
  // التنبؤ بالتواريخ الرئيسية
  // ─────────────────────────────────────────────────────────────────────────────

  @Post('predict')
  @ApiOperation({
    summary: 'Predict key phenological dates',
    description: 'التنبؤ بالتواريخ الرئيسية لمراحل النمو (الإنبات، الإزهار، النضج)',
  })
  @ApiBody({
    description: 'Prediction parameters',
    schema: {
      type: 'object',
      properties: {
        cropType: { type: 'string', example: 'CORN' },
        sowingDate: { type: 'string', example: '2024-04-15' },
        avgDailyGDD: { type: 'number', example: 15, description: 'Average daily GDD (°C·day)' },
      },
      required: ['cropType', 'sowingDate'],
    },
  })
  @ApiResponse({ status: 200, description: 'Predicted key dates' })
  predictKeyDates(@Body() input: PredictDatesInput) {
    const predictions = this.phenologyService.predictKeyDates(
      input.cropType,
      input.sowingDate,
      input.avgDailyGDD ?? 15,
    );

    return {
      parameters: {
        cropType: input.cropType,
        sowingDate: input.sowingDate,
        avgDailyGDD: input.avgDailyGDD ?? 15,
      },
      predictions,
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Crop Parameters
  // الحصول على معاملات المحصول
  // ─────────────────────────────────────────────────────────────────────────────

  @Get('parameters/:cropType')
  @ApiOperation({
    summary: 'Get WOFOST-style crop phenology parameters',
    description: 'الحصول على معاملات مراحل النمو للمحصول بأسلوب WOFOST',
  })
  @ApiParam({ name: 'cropType', example: 'WHEAT', description: 'Crop type identifier' })
  @ApiResponse({ status: 200, description: 'Crop phenology parameters' })
  getCropParameters(@Param('cropType') cropType: string) {
    const params = this.phenologyService.getCropParameters(cropType);
    if (!params) {
      return {
        error: `Crop type ${cropType} not found`,
        availableCrops: this.phenologyService.getAvailableCrops(),
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
    summary: 'List available crops with phenology models',
    description: 'قائمة المحاصيل المتاحة مع نماذج مراحل النمو',
  })
  @ApiResponse({ status: 200, description: 'List of available crops' })
  listAvailableCrops() {
    return {
      crops: this.phenologyService.getAvailableCrops(),
      total: this.phenologyService.getAvailableCrops().length,
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Growth Stages for Crop
  // الحصول على مراحل النمو للمحصول
  // ─────────────────────────────────────────────────────────────────────────────

  @Get('stages/:cropType')
  @ApiOperation({
    summary: 'Get growth stages for a specific crop',
    description: 'الحصول على مراحل النمو لمحصول محدد مع نطاقات DVS',
  })
  @ApiParam({ name: 'cropType', example: 'RICE', description: 'Crop type identifier' })
  @ApiResponse({ status: 200, description: 'Growth stages for the crop' })
  getGrowthStages(@Param('cropType') cropType: string) {
    const stages = this.phenologyService.getGrowthStages(cropType);
    if (!stages) {
      return {
        error: `Crop type ${cropType} not found`,
        availableCrops: this.phenologyService.getAvailableCrops(),
      };
    }
    return { cropType, stages };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Health Check
  // فحص صحة الخدمة
  // ─────────────────────────────────────────────────────────────────────────────

  @Get('health')
  @ApiOperation({
    summary: 'Phenology service health check',
    description: 'فحص صحة خدمة مراحل النمو',
  })
  @ApiResponse({ status: 200, description: 'Service is healthy' })
  healthCheck() {
    return {
      status: 'healthy',
      service: 'phenology',
      timestamp: new Date().toISOString(),
      version: '1.0.0',
    };
  }
}
