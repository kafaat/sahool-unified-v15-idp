// ═══════════════════════════════════════════════════════════════════════════════
// Water Balance Controller - مراقب توازن المياه
// Integrated Soil-Crop-Atmosphere Water Balance
// ═══════════════════════════════════════════════════════════════════════════════

import { Controller, Get, Post, Body, Param, Query } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse, ApiQuery, ApiBody, ApiParam } from '@nestjs/swagger';
import { WaterBalanceService } from './water-balance.service';

class KcInput {
  cropType: string;
  daysAfterPlanting: number;
}

class ETcInput {
  cropType: string;
  et0: number;
  daysAfterPlanting: number;
  waterStress?: number;
}

class WaterBalanceInput {
  cropType: string;
  rootingDepth: number;
  soilParams: {
    fieldCapacity: number;
    wiltingPoint: number;
    currentWaterContent: number;
  };
  dailyInputs: {
    et0: number;
    precipitation: number;
    irrigation: number;
    daysAfterPlanting: number;
  };
}

class IrrigationScheduleInput {
  cropType: string;
  sowingDate: string;
  weatherForecast: Array<{
    date: string;
    et0: number;
    precipitation: number;
  }>;
  soilParams: {
    fieldCapacity: number;
    wiltingPoint: number;
    initialWaterContent: number;
  };
  irrigationSystem: {
    type: 'drip' | 'sprinkler' | 'furrow' | 'flood';
    efficiency: number;
    maxDailyApplication: number;
  };
}

@ApiTags('water-balance')
@Controller('api/v1/water')
export class WaterBalanceController {
  constructor(private readonly waterBalanceService: WaterBalanceService) {}

  // ─────────────────────────────────────────────────────────────────────────────
  // Calculate Crop Coefficient (Kc)
  // حساب معامل المحصول
  // ─────────────────────────────────────────────────────────────────────────────

  @Post('kc')
  @ApiOperation({
    summary: 'Calculate crop coefficient (Kc) - FAO-56',
    description: 'حساب معامل المحصول (Kc) حسب منظمة الفاو-56',
  })
  @ApiBody({
    description: 'Kc calculation parameters',
    schema: {
      type: 'object',
      properties: {
        cropType: { type: 'string', example: 'CORN' },
        daysAfterPlanting: { type: 'number', example: 60 },
      },
      required: ['cropType', 'daysAfterPlanting'],
    },
  })
  @ApiResponse({ status: 200, description: 'Kc calculation result' })
  calculateKc(@Body() input: KcInput) {
    const result = this.waterBalanceService.calculateKc(
      input.cropType,
      input.daysAfterPlanting,
    );

    return {
      input,
      result,
      reference: 'FAO Irrigation and Drainage Paper 56',
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Calculate Crop Evapotranspiration (ETc)
  // حساب التبخر-نتح للمحصول
  // ─────────────────────────────────────────────────────────────────────────────

  @Post('etc')
  @ApiOperation({
    summary: 'Calculate crop evapotranspiration (ETc)',
    description: 'حساب التبخر-نتح للمحصول ETc = Kc × ET0',
  })
  @ApiBody({
    description: 'ETc calculation parameters',
    schema: {
      type: 'object',
      properties: {
        cropType: { type: 'string', example: 'WHEAT' },
        et0: { type: 'number', example: 5.5, description: 'Reference ET (mm day⁻¹)' },
        daysAfterPlanting: { type: 'number', example: 45 },
        waterStress: { type: 'number', example: 0.9, description: 'Stress coefficient (0-1)' },
      },
      required: ['cropType', 'et0', 'daysAfterPlanting'],
    },
  })
  @ApiResponse({ status: 200, description: 'ETc calculation result' })
  calculateETc(@Body() input: ETcInput) {
    const result = this.waterBalanceService.calculateETc(
      input.cropType,
      input.et0,
      input.daysAfterPlanting,
      input.waterStress,
    );

    return {
      input,
      result,
      formula: 'ETc = Kc × ET0; ETc_adj = Ks × Kc × ET0',
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Calculate Water Balance
  // حساب توازن المياه
  // ─────────────────────────────────────────────────────────────────────────────

  @Post('balance')
  @ApiOperation({
    summary: 'Calculate daily soil water balance',
    description: 'حساب توازن مياه التربة اليومي وتوصيات الري',
  })
  @ApiBody({
    description: 'Water balance parameters',
    schema: {
      type: 'object',
      properties: {
        cropType: { type: 'string', example: 'RICE' },
        rootingDepth: { type: 'number', example: 0.4, description: 'Current root depth (m)' },
        soilParams: {
          type: 'object',
          properties: {
            fieldCapacity: { type: 'number', example: 0.35 },
            wiltingPoint: { type: 'number', example: 0.15 },
            currentWaterContent: { type: 'number', example: 0.28 },
          },
        },
        dailyInputs: {
          type: 'object',
          properties: {
            et0: { type: 'number', example: 6 },
            precipitation: { type: 'number', example: 0 },
            irrigation: { type: 'number', example: 0 },
            daysAfterPlanting: { type: 'number', example: 50 },
          },
        },
      },
      required: ['cropType', 'rootingDepth', 'soilParams', 'dailyInputs'],
    },
  })
  @ApiResponse({ status: 200, description: 'Water balance calculation' })
  calculateWaterBalance(@Body() input: WaterBalanceInput) {
    const result = this.waterBalanceService.calculateWaterBalance(
      input.cropType,
      input.rootingDepth,
      input.soilParams,
      input.dailyInputs,
    );

    return {
      input: {
        cropType: input.cropType,
        rootingDepth: input.rootingDepth,
      },
      result,
      model: 'FAO-56 / SWAP water balance',
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Generate Irrigation Schedule
  // جدولة الري الذكي
  // ─────────────────────────────────────────────────────────────────────────────

  @Post('irrigation/schedule')
  @ApiOperation({
    summary: 'Generate smart irrigation schedule',
    description: 'إنشاء جدول ري ذكي بناءً على توقعات الطقس وظروف التربة',
  })
  @ApiBody({
    description: 'Irrigation scheduling parameters',
    schema: {
      type: 'object',
      properties: {
        cropType: { type: 'string', example: 'SOYBEAN' },
        sowingDate: { type: 'string', example: '2024-04-15' },
        weatherForecast: {
          type: 'array',
          items: {
            type: 'object',
            properties: {
              date: { type: 'string' },
              et0: { type: 'number' },
              precipitation: { type: 'number' },
            },
          },
        },
        soilParams: {
          type: 'object',
          properties: {
            fieldCapacity: { type: 'number', example: 0.32 },
            wiltingPoint: { type: 'number', example: 0.12 },
            initialWaterContent: { type: 'number', example: 0.28 },
          },
        },
        irrigationSystem: {
          type: 'object',
          properties: {
            type: { type: 'string', enum: ['drip', 'sprinkler', 'furrow', 'flood'] },
            efficiency: { type: 'number', example: 0.9 },
            maxDailyApplication: { type: 'number', example: 30 },
          },
        },
      },
      required: ['cropType', 'sowingDate', 'weatherForecast', 'soilParams', 'irrigationSystem'],
    },
  })
  @ApiResponse({ status: 200, description: 'Irrigation schedule' })
  generateIrrigationSchedule(@Body() input: IrrigationScheduleInput) {
    const result = this.waterBalanceService.generateIrrigationSchedule(
      input.cropType,
      input.sowingDate,
      input.weatherForecast,
      input.soilParams,
      input.irrigationSystem,
    );

    return {
      parameters: {
        cropType: input.cropType,
        sowingDate: input.sowingDate,
        forecastDays: input.weatherForecast.length,
        irrigationType: input.irrigationSystem.type,
      },
      ...result,
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Calculate Yield Response to Water Stress
  // حساب استجابة الغلة لإجهاد المياه
  // ─────────────────────────────────────────────────────────────────────────────

  @Get('yield-response/:cropType')
  @ApiOperation({
    summary: 'Calculate yield reduction from water stress',
    description: 'حساب انخفاض الغلة بسبب إجهاد المياه (معادلة Ky)',
  })
  @ApiParam({ name: 'cropType', example: 'CORN' })
  @ApiQuery({ name: 'etDeficit', required: true, example: 0.2, description: 'Relative ET deficit (0-1)' })
  @ApiResponse({ status: 200, description: 'Yield response calculation' })
  calculateYieldResponse(
    @Param('cropType') cropType: string,
    @Query('etDeficit') etDeficit: string,
  ) {
    const result = this.waterBalanceService.calculateYieldReduction(
      cropType,
      parseFloat(etDeficit),
    );

    return {
      input: {
        cropType,
        relativeETDeficit: parseFloat(etDeficit),
      },
      result,
      formula: 'Ya/Ym = 1 - Ky × (1 - ETa/ETm)',
      reference: 'FAO-33 Yield Response to Water',
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Crop Water Parameters
  // الحصول على معاملات المياه للمحصول
  // ─────────────────────────────────────────────────────────────────────────────

  @Get('parameters/:cropType')
  @ApiOperation({
    summary: 'Get crop water parameters (FAO-56)',
    description: 'الحصول على معاملات المياه للمحصول حسب FAO-56',
  })
  @ApiParam({ name: 'cropType', example: 'SUGARCANE' })
  @ApiResponse({ status: 200, description: 'Crop water parameters' })
  getCropParameters(@Param('cropType') cropType: string) {
    const params = this.waterBalanceService.getCropParameters(cropType);
    if (!params) {
      return {
        error: `Crop type ${cropType} not found`,
        availableCrops: this.waterBalanceService.getAvailableCrops(),
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
    summary: 'List crops with water balance models',
    description: 'قائمة المحاصيل مع نماذج توازن المياه',
  })
  @ApiResponse({ status: 200, description: 'List of crops' })
  listCrops() {
    return {
      crops: this.waterBalanceService.getAvailableCrops(),
      total: this.waterBalanceService.getAvailableCrops().length,
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Health Check
  // ─────────────────────────────────────────────────────────────────────────────

  @Get('health')
  @ApiOperation({
    summary: 'Water balance service health check',
    description: 'فحص صحة خدمة توازن المياه',
  })
  @ApiResponse({ status: 200, description: 'Service is healthy' })
  healthCheck() {
    return {
      status: 'healthy',
      service: 'water-balance',
      timestamp: new Date().toISOString(),
      version: '1.0.0',
      models: ['FAO-56', 'FAO-33', 'SWAP'],
    };
  }
}
