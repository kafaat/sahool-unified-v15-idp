// ═══════════════════════════════════════════════════════════════════════════════
// Satellite Data Selector Controller - مراقب اختيار البيانات الساتلية
// REST API for intelligent satellite data source selection
// ═══════════════════════════════════════════════════════════════════════════════

import { Controller, Get, Post, Body, Param, Query, HttpException, HttpStatus, NotFoundException } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse, ApiQuery, ApiBody, ApiParam } from '@nestjs/swagger';
import { SatelliteDataService } from './satellite-data.service';

class DataRequirementsInput {
  spatialResolution: 'high' | 'medium' | 'low';
  temporalResolution: 'daily' | 'weekly' | 'biweekly' | 'monthly';
  cloudFree: boolean;
  budget: 'free' | 'commercial' | 'any';
  application: 'lai' | 'ndvi' | 'water' | 'disaster' | 'yield' | 'phenology' | 'soil' | 'thermal';
  region?: string;
}

class CompareInput {
  satelliteIds: string[];
}

@ApiTags('satellite-data')
@Controller('api/v1/satellite-data')
export class SatelliteDataController {
  constructor(private readonly satelliteDataService: SatelliteDataService) {}

  // ─────────────────────────────────────────────────────────────────────────────
  // Select Optimal Data Source - اختيار مصدر البيانات الأمثل
  // ─────────────────────────────────────────────────────────────────────────────

  @Post('select')
  @ApiOperation({
    summary: 'Select optimal satellite data source',
    description: 'اختيار مصدر البيانات الساتلية الأمثل بناءً على المتطلبات',
  })
  @ApiBody({
    description: 'Data requirements',
    schema: {
      type: 'object',
      properties: {
        spatialResolution: {
          type: 'string',
          enum: ['high', 'medium', 'low'],
          example: 'high',
          description: 'Required spatial resolution (high: <10m, medium: 10-30m, low: >30m)',
        },
        temporalResolution: {
          type: 'string',
          enum: ['daily', 'weekly', 'biweekly', 'monthly'],
          example: 'weekly',
          description: 'Required temporal resolution',
        },
        cloudFree: {
          type: 'boolean',
          example: false,
          description: 'Whether cloud-free capability is required (SAR)',
        },
        budget: {
          type: 'string',
          enum: ['free', 'commercial', 'any'],
          example: 'free',
          description: 'Budget constraint',
        },
        application: {
          type: 'string',
          enum: ['lai', 'ndvi', 'water', 'disaster', 'yield', 'phenology', 'soil', 'thermal'],
          example: 'ndvi',
          description: 'Target application',
        },
        region: {
          type: 'string',
          example: 'Middle East',
          description: 'Geographic region (optional)',
        },
      },
      required: ['spatialResolution', 'temporalResolution', 'cloudFree', 'budget', 'application'],
    },
  })
  @ApiResponse({ status: 200, description: 'Optimal satellite recommendation' })
  selectOptimalSource(@Body() input: DataRequirementsInput) {
    const recommendation = this.satelliteDataService.selectOptimalDataSource(input);

    return {
      request: input,
      recommendation,
      timestamp: new Date().toISOString(),
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // List All Satellites - قائمة جميع الأقمار الصناعية
  // ─────────────────────────────────────────────────────────────────────────────

  @Get('satellites')
  @ApiOperation({
    summary: 'List all available satellites',
    description: 'قائمة جميع الأقمار الصناعية المتاحة للاستشعار عن بعد الزراعي',
  })
  @ApiResponse({ status: 200, description: 'List of satellites' })
  listSatellites() {
    const satellites = this.satelliteDataService.getAllSatellites();

    return {
      satellites,
      total: satellites.length,
      freeSatellites: satellites.filter(s => s.isFree).length,
      commercialSatellites: satellites.filter(s => !s.isFree).length,
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Free Satellites Only - الأقمار المجانية فقط
  // ─────────────────────────────────────────────────────────────────────────────

  @Get('satellites/free')
  @ApiOperation({
    summary: 'List free satellite data sources',
    description: 'قائمة مصادر البيانات الساتلية المجانية',
  })
  @ApiResponse({ status: 200, description: 'List of free satellites' })
  listFreeSatellites() {
    const satellites = this.satelliteDataService.getFreeSatellites();

    return {
      satellites,
      total: satellites.length,
      downloadUrls: satellites.map(s => ({
        name: s.nameEn,
        url: s.dataUrl,
      })),
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Satellite by ID - الحصول على قمر صناعي بالمعرف
  // ─────────────────────────────────────────────────────────────────────────────

  @Get('satellites/:id')
  @ApiOperation({
    summary: 'Get satellite details by ID',
    description: 'الحصول على تفاصيل قمر صناعي بالمعرف',
  })
  @ApiParam({ name: 'id', example: 'SENTINEL_2' })
  @ApiResponse({ status: 200, description: 'Satellite details' })
  @ApiResponse({ status: 404, description: 'Satellite not found' })
  getSatelliteById(@Param('id') id: string) {
    const satellite = this.satelliteDataService.getSatelliteById(id.toUpperCase());

    if (!satellite) {
      const availableSatellites = this.satelliteDataService.getAllSatellites().map(s => s.id);
      throw new NotFoundException({
        statusCode: HttpStatus.NOT_FOUND,
        message: `Satellite ${id} not found`,
        availableSatellites,
      });
    }

    return { satellite };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Satellites by Application - أقمار حسب التطبيق
  // ─────────────────────────────────────────────────────────────────────────────

  @Get('satellites/application/:application')
  @ApiOperation({
    summary: 'Get satellites suitable for specific application',
    description: 'الحصول على الأقمار المناسبة لتطبيق محدد',
  })
  @ApiParam({
    name: 'application',
    example: 'lai',
    enum: ['lai', 'ndvi', 'water', 'disaster', 'yield', 'phenology', 'soil', 'thermal'],
  })
  @ApiResponse({ status: 200, description: 'Satellites for application' })
  getSatellitesByApplication(@Param('application') application: string) {
    const satellites = this.satelliteDataService.getSatellitesByApplication(application);

    return {
      application,
      satellites,
      total: satellites.length,
      freeSatellites: satellites.filter(s => s.isFree).map(s => s.nameEn),
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Compare Satellites - مقارنة الأقمار الصناعية
  // ─────────────────────────────────────────────────────────────────────────────

  @Post('compare')
  @ApiOperation({
    summary: 'Compare multiple satellites',
    description: 'مقارنة عدة أقمار صناعية',
  })
  @ApiBody({
    description: 'Satellite IDs to compare',
    schema: {
      type: 'object',
      properties: {
        satelliteIds: {
          type: 'array',
          items: { type: 'string' },
          example: ['SENTINEL_2', 'LANDSAT_8', 'MODIS'],
        },
      },
      required: ['satelliteIds'],
    },
  })
  @ApiResponse({ status: 200, description: 'Comparison results' })
  compareSatellites(@Body() input: CompareInput) {
    const result = this.satelliteDataService.compareSatellites(input.satelliteIds);

    return {
      ...result,
      timestamp: new Date().toISOString(),
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Band Combinations - تركيبات النطاقات
  // ─────────────────────────────────────────────────────────────────────────────

  @Get('indices')
  @ApiOperation({
    summary: 'List vegetation indices and band combinations',
    description: 'قائمة المؤشرات النباتية وتركيبات النطاقات',
  })
  @ApiResponse({ status: 200, description: 'List of indices' })
  listIndices() {
    const indices = this.satelliteDataService.getBandCombinations();

    return {
      indices,
      total: indices.length,
    };
  }

  @Get('indices/:name')
  @ApiOperation({
    summary: 'Get specific vegetation index details',
    description: 'الحصول على تفاصيل مؤشر نباتي محدد',
  })
  @ApiParam({ name: 'name', example: 'NDVI' })
  @ApiResponse({ status: 200, description: 'Index details' })
  @ApiResponse({ status: 404, description: 'Index not found' })
  getIndexByName(@Param('name') name: string) {
    const index = this.satelliteDataService.getBandCombinationByIndex(name);

    if (!index) {
      const availableIndices = this.satelliteDataService.getBandCombinations().map(i => i.name);
      throw new NotFoundException({
        statusCode: HttpStatus.NOT_FOUND,
        message: `Index ${name} not found`,
        availableIndices,
      });
    }

    return { index };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Recommendations for Crop Model Modules
  // توصيات لوحدات نموذج نمو المحاصيل
  // ─────────────────────────────────────────────────────────────────────────────

  @Get('recommend/:module')
  @ApiOperation({
    summary: 'Get satellite recommendations for crop model module',
    description: 'الحصول على توصيات الأقمار الصناعية لوحدة نموذج نمو المحاصيل',
  })
  @ApiParam({
    name: 'module',
    example: 'water',
    enum: ['phenology', 'photosynthesis', 'biomass', 'roots', 'water'],
  })
  @ApiResponse({ status: 200, description: 'Module recommendations' })
  @ApiResponse({ status: 400, description: 'Invalid module' })
  getModuleRecommendations(@Param('module') module: string) {
    const validModules = ['phenology', 'photosynthesis', 'biomass', 'roots', 'water'];

    if (!validModules.includes(module)) {
      throw new HttpException(
        {
          statusCode: HttpStatus.BAD_REQUEST,
          message: `Invalid module: ${module}`,
          validModules,
        },
        HttpStatus.BAD_REQUEST,
      );
    }

    const recommendations = this.satelliteDataService.getRecommendationForModule(
      module as 'phenology' | 'photosynthesis' | 'biomass' | 'roots' | 'water',
    );

    return {
      module,
      ...recommendations,
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Quick Recommendations for Common Use Cases
  // توصيات سريعة لحالات الاستخدام الشائعة
  // ─────────────────────────────────────────────────────────────────────────────

  @Get('quick-recommend')
  @ApiOperation({
    summary: 'Get quick recommendations for common agricultural applications',
    description: 'توصيات سريعة للتطبيقات الزراعية الشائعة',
  })
  @ApiQuery({
    name: 'useCase',
    required: true,
    enum: ['crop-monitoring', 'irrigation', 'yield-prediction', 'disaster-assessment', 'digital-twin'],
    example: 'crop-monitoring',
  })
  @ApiResponse({ status: 200, description: 'Quick recommendations' })
  @ApiResponse({ status: 400, description: 'Unknown use case' })
  getQuickRecommendations(@Query('useCase') useCase: string) {
    const recommendations: { [key: string]: any } = {
      'crop-monitoring': {
        primary: 'SENTINEL_2',
        alternative: 'LANDSAT_8',
        indices: ['NDVI', 'EVI', 'NDRE'],
        frequency: 'weekly',
        notes: ['Use Sentinel-2 for 10m resolution NDVI', 'Combine with Landsat for gap-filling'],
        notesAr: ['استخدم Sentinel-2 لدقة 10م NDVI', 'ادمج مع Landsat لملء الفجوات'],
      },
      'irrigation': {
        primary: 'MODIS',
        alternative: 'SENTINEL_1',
        indices: ['NDWI', 'LST'],
        frequency: 'daily',
        notes: ['MODIS ET product for reference ET', 'SAR for soil moisture'],
        notesAr: ['منتج ET من MODIS للتبخر-نتح المرجعي', 'SAR لرطوبة التربة'],
      },
      'yield-prediction': {
        primary: 'SENTINEL_2',
        alternative: 'MODIS',
        indices: ['NDVI', 'LAI (from NDVI)', 'EVI'],
        frequency: 'biweekly',
        notes: ['Time series analysis crucial', 'Combine with weather and soil data'],
        notesAr: ['تحليل السلاسل الزمنية ضروري', 'ادمج مع بيانات الطقس والتربة'],
      },
      'disaster-assessment': {
        primary: 'SENTINEL_1',
        alternative: 'SENTINEL_2',
        indices: ['NDVI change', 'NDWI'],
        frequency: 'daily',
        notes: ['SAR for all-weather monitoring', 'Pre/post event comparison'],
        notesAr: ['SAR للرصد في جميع الأحوال الجوية', 'مقارنة ما قبل/بعد الحدث'],
      },
      'digital-twin': {
        primary: 'PLANET',
        alternative: 'SENTINEL_2',
        indices: ['NDVI', 'EVI', 'LAI (from NDVI)', 'NDWI'],
        frequency: 'daily',
        notes: ['Daily Planet data ideal for real-time twin', 'Supplement with free Sentinel-2'],
        notesAr: ['بيانات Planet اليومية مثالية للتوأم الرقمي', 'ادعم ببيانات Sentinel-2 المجانية'],
      },
    };

    const rec = recommendations[useCase];

    if (!rec) {
      throw new HttpException(
        {
          statusCode: HttpStatus.BAD_REQUEST,
          message: `Unknown use case: ${useCase}`,
          availableUseCases: Object.keys(recommendations),
        },
        HttpStatus.BAD_REQUEST,
      );
    }

    // Get full satellite details
    const primary = this.satelliteDataService.getSatelliteById(rec.primary);
    const alternative = this.satelliteDataService.getSatelliteById(rec.alternative);

    return {
      useCase,
      recommendation: {
        ...rec,
        primaryDetails: primary,
        alternativeDetails: alternative,
      },
      timestamp: new Date().toISOString(),
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Health Check
  // ─────────────────────────────────────────────────────────────────────────────

  @Get('health')
  @ApiOperation({
    summary: 'Satellite data service health check',
    description: 'فحص صحة خدمة البيانات الساتلية',
  })
  @ApiResponse({ status: 200, description: 'Service is healthy' })
  healthCheck() {
    const satellites = this.satelliteDataService.getAllSatellites();
    const indices = this.satelliteDataService.getBandCombinations();

    return {
      status: 'healthy',
      service: 'satellite-data',
      timestamp: new Date().toISOString(),
      version: '1.0.0',
      stats: {
        totalSatellites: satellites.length,
        freeSatellites: satellites.filter(s => s.isFree).length,
        activeSatellites: satellites.filter(s => s.status === 'active').length,
        vegetationIndices: indices.length,
      },
      dataSources: [
        'NASA/USGS (Landsat)',
        'ESA (Sentinel)',
        'NASA (MODIS)',
        'CNSA (Gaofen)',
        'Planet Labs',
        'Maxar (WorldView)',
      ],
    };
  }
}
