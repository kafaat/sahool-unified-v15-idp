// ═══════════════════════════════════════════════════════════════════════════════
// Remote Sensing World Model Controller - مراقب نموذج العالم للاستشعار عن بعد
// REST API for RemoteBAGEL spatial reasoning capabilities
// Paper: https://arxiv.org/abs/2509.17808 (2025)
// ═══════════════════════════════════════════════════════════════════════════════

import { Controller, Get, Post, Body, Param, Query } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse, ApiQuery, ApiBody, ApiParam } from '@nestjs/swagger';
import { RSWorldModelService } from './rs-world-model.service';

type Direction = 'up' | 'down' | 'left' | 'right';
type ScenarioType = 'general' | 'flood' | 'urban' | 'rural' | 'agricultural';

class SpatialReasoningInput {
  centralTile: {
    id: string;
    position: { row: number; col: number };
    bounds: { minLat: number; maxLat: number; minLng: number; maxLng: number };
    indices: { ndvi: number; ndwi: number; ndbi: number };
    scenario: ScenarioType;
  };
  direction: Direction;
}

class MultiDirectionalInput {
  centralTile: {
    id: string;
    position: { row: number; col: number };
    bounds: { minLat: number; maxLat: number; minLng: number; maxLng: number };
    indices: { ndvi: number; ndwi: number; ndbi: number };
    scenario: ScenarioType;
  };
  expansionLevels?: number;
}

class GridPartitionInput {
  imageWidth: number;
  imageHeight: number;
  centerLat: number;
  centerLng: number;
  scenario: ScenarioType;
}

@ApiTags('rs-world-model')
@Controller('api/v1/rs-world-model')
export class RSWorldModelController {
  constructor(private readonly rsWorldModelService: RSWorldModelService) {}

  // ─────────────────────────────────────────────────────────────────────────────
  // Model Architecture & Info - البنية المعمارية ومعلومات النموذج
  // ─────────────────────────────────────────────────────────────────────────────

  @Get('architecture')
  @ApiOperation({
    summary: 'Get RemoteBAGEL model architecture',
    description: 'الحصول على بنية نموذج RemoteBAGEL ثلاثية المراحل',
  })
  @ApiResponse({ status: 200, description: 'Model architecture details' })
  getArchitecture() {
    const architecture = this.rsWorldModelService.getModelArchitecture();

    return {
      model: 'RemoteBAGEL',
      baseModel: 'BAGEL-7B',
      paper: 'https://arxiv.org/abs/2509.17808',
      year: 2025,
      institutions: [
        'Sydney University of Science and Technology',
        'Chinese Academy of Sciences',
        'University of Alabama Birmingham',
        'Beijing University',
      ],
      architecture,
      innovation: 'First World Model for Remote Sensing Spatial Reasoning',
      innovationAr: 'أول نموذج عالمي للاستشعار عن بعد للاستدلال المكاني',
    };
  }

  @Get('scenarios')
  @ApiOperation({
    summary: 'List available scenarios',
    description: 'قائمة السيناريوهات المتاحة للتوليد',
  })
  @ApiResponse({ status: 200, description: 'Available scenarios' })
  getScenarios() {
    const scenarios = this.rsWorldModelService.getScenarios();

    return {
      scenarios,
      total: scenarios.length,
      note: 'Each scenario has unique land cover patterns and indices',
      noteAr: 'كل سيناريو له أنماط غطاء أرضي ومؤشرات فريدة',
    };
  }

  @Get('benchmarks')
  @ApiOperation({
    summary: 'Get RSWISE benchmark results',
    description: 'نتائج معيار RSWISE للتقييم',
  })
  @ApiResponse({ status: 200, description: 'Benchmark results' })
  getBenchmarks() {
    const benchmarks = this.rsWorldModelService.getBenchmarks();

    return {
      benchmark: 'RSWISE',
      description: 'Remote Sensing World Intelligence Spatial Evaluation',
      descriptionAr: 'تقييم الذكاء المكاني العالمي للاستشعار عن بعد',
      totalTasks: 1600,
      taskBreakdown: {
        general: 400,
        flood: 400,
        urban: 400,
        rural: 400,
      },
      evaluationDimensions: ['FID (Visual Fidelity)', 'GPT-4o (Spatial Reasoning)'],
      results: benchmarks,
      keyFinding: 'RemoteBAGEL achieves 88.8 RSWISE score, 42.3% improvement over baseline',
      keyFindingAr: 'RemoteBAGEL يحقق درجة 88.8، تحسين 42.3% مقارنة بخط الأساس',
    };
  }

  @Get('capabilities')
  @ApiOperation({
    summary: 'List model capabilities',
    description: 'قائمة قدرات النموذج',
  })
  @ApiResponse({ status: 200, description: 'Model capabilities' })
  getCapabilities() {
    const capabilities = this.rsWorldModelService.getCapabilities();

    return {
      capabilities,
      supported: capabilities.filter(c => c.supported).length,
      total: capabilities.length,
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Spatial Reasoning - الاستدلال المكاني
  // ─────────────────────────────────────────────────────────────────────────────

  @Post('reason')
  @ApiOperation({
    summary: 'Perform directional spatial reasoning',
    description: 'تنفيذ الاستدلال المكاني الاتجاهي - توليد اللوحة المجاورة',
  })
  @ApiBody({
    description: 'Spatial reasoning parameters',
    schema: {
      type: 'object',
      properties: {
        centralTile: {
          type: 'object',
          properties: {
            id: { type: 'string', example: 'tile_1_1' },
            position: {
              type: 'object',
              properties: {
                row: { type: 'number', example: 1 },
                col: { type: 'number', example: 1 },
              },
            },
            bounds: {
              type: 'object',
              properties: {
                minLat: { type: 'number', example: 24.7 },
                maxLat: { type: 'number', example: 24.71 },
                minLng: { type: 'number', example: 46.7 },
                maxLng: { type: 'number', example: 46.71 },
              },
            },
            indices: {
              type: 'object',
              properties: {
                ndvi: { type: 'number', example: 0.55 },
                ndwi: { type: 'number', example: 0.15 },
                ndbi: { type: 'number', example: -0.1 },
              },
            },
            scenario: { type: 'string', enum: ['general', 'flood', 'urban', 'rural', 'agricultural'], example: 'agricultural' },
          },
        },
        direction: { type: 'string', enum: ['up', 'down', 'left', 'right'], example: 'right' },
      },
    },
  })
  @ApiResponse({ status: 200, description: 'Spatial reasoning result' })
  performSpatialReasoning(@Body() input: SpatialReasoningInput) {
    // Fill in missing properties
    const centralTile = {
      ...input.centralTile,
      landCover: [],
      features: [],
      timestamp: new Date().toISOString(),
    };

    const result = this.rsWorldModelService.performSpatialReasoning({
      centralTile: centralTile as any,
      direction: input.direction,
    });

    return {
      ...result,
      method: 'RemoteBAGEL Directional Conditional Spatial Reasoning',
      methodAr: 'الاستدلال المكاني الشرطي الاتجاهي RemoteBAGEL',
      paper: 'arxiv:2509.17808',
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Multi-Directional Expansion - التوسع متعدد الاتجاهات
  // ─────────────────────────────────────────────────────────────────────────────

  @Post('expand')
  @ApiOperation({
    summary: 'Expand satellite image in all 4 directions',
    description: 'توسيع صورة القمر الصناعي في 4 اتجاهات - أعلى/أسفل/يسار/يمين',
  })
  @ApiBody({
    description: 'Multi-directional expansion parameters',
    schema: {
      type: 'object',
      properties: {
        centralTile: {
          type: 'object',
          properties: {
            id: { type: 'string', example: 'tile_center' },
            position: { type: 'object', properties: { row: { type: 'number' }, col: { type: 'number' } } },
            bounds: { type: 'object' },
            indices: { type: 'object' },
            scenario: { type: 'string', example: 'agricultural' },
          },
        },
        expansionLevels: { type: 'number', example: 1, description: 'Number of expansion levels (1 = 3x3, 2 = 5x5)' },
      },
    },
  })
  @ApiResponse({ status: 200, description: 'Multi-directional expansion result' })
  expandMultiDirectional(@Body() input: MultiDirectionalInput) {
    const centralTile = {
      ...input.centralTile,
      landCover: [],
      features: [],
      timestamp: new Date().toISOString(),
    };

    const result = this.rsWorldModelService.expandMultiDirectional({
      centralTile: centralTile as any,
      expansionLevels: input.expansionLevels,
    });

    return {
      ...result,
      gridSize: `${1 + (input.expansionLevels || 1) * 2}×${1 + (input.expansionLevels || 1) * 2}`,
      method: 'RemoteBAGEL Multi-Directional Spatial Expansion',
      methodAr: 'التوسع المكاني متعدد الاتجاهات RemoteBAGEL',
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Grid Partitioning - تقسيم الشبكة
  // ─────────────────────────────────────────────────────────────────────────────

  @Post('partition')
  @ApiOperation({
    summary: 'Partition image into 3x3 overlapping grid',
    description: 'تقسيم الصورة إلى شبكة 3×3 متداخلة للتدريب',
  })
  @ApiBody({
    description: 'Grid partition parameters',
    schema: {
      type: 'object',
      properties: {
        imageWidth: { type: 'number', example: 1024, description: 'Image width in pixels' },
        imageHeight: { type: 'number', example: 1024, description: 'Image height in pixels' },
        centerLat: { type: 'number', example: 24.7 },
        centerLng: { type: 'number', example: 46.7 },
        scenario: { type: 'string', enum: ['general', 'flood', 'urban', 'rural', 'agricultural'], example: 'agricultural' },
      },
    },
  })
  @ApiResponse({ status: 200, description: 'Grid partition result' })
  partitionImage(@Body() input: GridPartitionInput) {
    const partition = this.rsWorldModelService.partitionImage(input);
    const trainingData = this.rsWorldModelService.generateTrainingData(partition);

    return {
      partition,
      trainingData,
      selfSupervised: true,
      note: 'No manual labeling required - training pairs generated automatically',
      noteAr: 'لا حاجة لوضع علامات يدوية - أزواج التدريب تُولد تلقائياً',
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Evaluation - التقييم
  // ─────────────────────────────────────────────────────────────────────────────

  @Post('evaluate')
  @ApiOperation({
    summary: 'Evaluate generated tile quality (RSWISE-style)',
    description: 'تقييم جودة اللوحة المولدة بأسلوب RSWISE',
  })
  @ApiBody({
    description: 'Evaluation parameters',
    schema: {
      type: 'object',
      properties: {
        predictedTile: { type: 'object' },
        groundTruthTile: { type: 'object', description: 'Optional ground truth for comparison' },
      },
    },
  })
  @ApiResponse({ status: 200, description: 'Evaluation scores' })
  evaluateGeneration(@Body() input: { predictedTile: any; groundTruthTile?: any }) {
    const scores = this.rsWorldModelService.evaluateGeneration(input);

    return {
      scores,
      benchmark: 'RSWISE',
      dimensions: {
        fid: 'Fréchet Inception Distance - Visual Fidelity',
        gptScore: 'GPT-4o Spatial Reasoning Assessment',
      },
      interpretation: {
        overall: scores.overall > 85 ? 'Excellent' : scores.overall > 70 ? 'Good' : 'Needs Improvement',
        overallAr: scores.overall > 85 ? 'ممتاز' : scores.overall > 70 ? 'جيد' : 'يحتاج تحسين',
      },
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Demo Endpoints - نقاط النهاية التجريبية
  // ─────────────────────────────────────────────────────────────────────────────

  @Get('demo/reason')
  @ApiOperation({
    summary: 'Run spatial reasoning demo',
    description: 'تشغيل عرض توضيحي للاستدلال المكاني',
  })
  @ApiQuery({ name: 'direction', required: false, enum: ['up', 'down', 'left', 'right'], example: 'right' })
  @ApiQuery({ name: 'scenario', required: false, enum: ['general', 'flood', 'urban', 'rural', 'agricultural'], example: 'agricultural' })
  @ApiResponse({ status: 200, description: 'Demo result' })
  demoReasoning(
    @Query('direction') direction?: Direction,
    @Query('scenario') scenario?: ScenarioType,
  ) {
    const centralTile = {
      id: 'demo_tile',
      position: { row: 1, col: 1 },
      bounds: { minLat: 24.7, maxLat: 24.71, minLng: 46.7, maxLng: 46.71 },
      indices: { ndvi: 0.55, ndwi: 0.12, ndbi: -0.08 },
      landCover: [],
      features: ['farmland', 'irrigation channel'],
      scenario: scenario || 'agricultural',
      timestamp: new Date().toISOString(),
    };

    const result = this.rsWorldModelService.performSpatialReasoning({
      centralTile: centralTile as any,
      direction: direction || 'right',
    });

    const evaluation = this.rsWorldModelService.evaluateGeneration({
      predictedTile: result.predictedTile,
    });

    return {
      demo: true,
      input: { centralTile, direction: direction || 'right' },
      result,
      evaluation,
    };
  }

  @Get('demo/expand')
  @ApiOperation({
    summary: 'Run multi-directional expansion demo',
    description: 'تشغيل عرض توضيحي للتوسع متعدد الاتجاهات',
  })
  @ApiQuery({ name: 'scenario', required: false, enum: ['general', 'flood', 'urban', 'rural', 'agricultural'], example: 'agricultural' })
  @ApiResponse({ status: 200, description: 'Demo expansion result' })
  demoExpansion(@Query('scenario') scenario?: ScenarioType) {
    const centralTile = {
      id: 'demo_center',
      position: { row: 1, col: 1 },
      bounds: { minLat: 24.7, maxLat: 24.71, minLng: 46.7, maxLng: 46.71 },
      indices: { ndvi: 0.60, ndwi: 0.10, ndbi: -0.05 },
      landCover: [],
      features: ['crop field', 'scattered trees'],
      scenario: scenario || 'agricultural',
      timestamp: new Date().toISOString(),
    };

    const result = this.rsWorldModelService.expandMultiDirectional({
      centralTile: centralTile as any,
      expansionLevels: 1,
    });

    return {
      demo: true,
      input: { centralTile, expansionLevels: 1 },
      result,
    };
  }

  @Get('demo/flood')
  @ApiOperation({
    summary: 'Run flood scenario demo',
    description: 'تشغيل عرض توضيحي لسيناريو الفيضانات',
  })
  @ApiResponse({ status: 200, description: 'Flood scenario demo result' })
  demoFloodScenario() {
    const centralTile = {
      id: 'flood_center',
      position: { row: 1, col: 1 },
      bounds: { minLat: 24.7, maxLat: 24.71, minLng: 46.7, maxLng: 46.71 },
      indices: { ndvi: 0.15, ndwi: 0.65, ndbi: -0.20 },
      landCover: [],
      features: ['flooded area', 'submerged vegetation', 'debris'],
      scenario: 'flood' as ScenarioType,
      timestamp: new Date().toISOString(),
    };

    const expansion = this.rsWorldModelService.expandMultiDirectional({
      centralTile: centralTile as any,
      expansionLevels: 1,
    });

    return {
      demo: true,
      scenario: 'flood',
      scenarioAr: 'فيضانات',
      description: 'Flood disaster response scenario - most challenging for spatial reasoning',
      descriptionAr: 'سيناريو استجابة كارثة الفيضانات - الأكثر تحدياً للاستدلال المكاني',
      result: expansion,
      riskAssessment: expansion.scenarioAnalysis.riskAssessment,
      recommendations: expansion.scenarioAnalysis.recommendations,
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Health Check
  // ─────────────────────────────────────────────────────────────────────────────

  @Get('health')
  @ApiOperation({
    summary: 'RS World Model service health check',
    description: 'فحص صحة خدمة نموذج العالم للاستشعار عن بعد',
  })
  @ApiResponse({ status: 200, description: 'Service is healthy' })
  healthCheck() {
    const architecture = this.rsWorldModelService.getModelArchitecture();
    const scenarios = this.rsWorldModelService.getScenarios();
    const capabilities = this.rsWorldModelService.getCapabilities();
    const benchmarks = this.rsWorldModelService.getBenchmarks();

    return {
      status: 'healthy',
      service: 'rs-world-model',
      timestamp: new Date().toISOString(),
      version: '1.0.0',
      model: {
        name: 'RemoteBAGEL',
        baseModel: 'BAGEL-7B',
        rswise: benchmarks[0].rswise,
        improvement: '42.3% over baseline',
      },
      paper: 'https://arxiv.org/abs/2509.17808',
      architecture: {
        stages: architecture.length,
        type: 'Three-stage encoder-integration-decoder',
      },
      scenarios: scenarios.length,
      capabilities: capabilities.filter(c => c.supported).length,
      training: {
        method: 'Self-supervised (no manual labeling)',
        images: 4000,
        pairs: 10080,
        gpus: '4×H100',
        hours: 20,
      },
      features: [
        'Directional spatial reasoning',
        'Multi-directional expansion',
        'Scenario-aware generation',
        'Spatial continuity preservation',
        'Self-supervised training',
        'Digital Twin integration',
      ],
      featuresAr: [
        'الاستدلال المكاني الاتجاهي',
        'التوسع متعدد الاتجاهات',
        'التوليد الواعي بالسيناريو',
        'الحفاظ على الاستمرارية المكانية',
        'التدريب الذاتي الإشراف',
        'تكامل التوأم الرقمي',
      ],
    };
  }
}
