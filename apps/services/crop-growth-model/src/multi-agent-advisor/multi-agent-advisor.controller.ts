// ═══════════════════════════════════════════════════════════════════════════════
// Multi-Agent Agricultural Advisor Controller - مراقب المستشار الزراعي متعدد الوكلاء
// REST API for multi-AI collaboration on agricultural decisions
// ═══════════════════════════════════════════════════════════════════════════════

import { Controller, Get, Post, Body, Param, Query } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse, ApiQuery, ApiBody, ApiParam } from '@nestjs/swagger';
import { MultiAgentAdvisorService } from './multi-agent-advisor.service';

class IrrigationQuestionInput {
  cropType: string;
  currentSoilMoisture: number;
  weatherForecast: { temperature: number; precipitation: number; et0: number };
  growthStage: string;
  lastIrrigation?: string;
}

class PestQuestionInput {
  cropType: string;
  symptoms: string[];
  location: string;
  season: string;
  temperature: number;
  humidity: number;
}

@ApiTags('multi-agent-advisor')
@Controller('api/v1/advisor-council')
export class MultiAgentAdvisorController {
  constructor(private readonly multiAgentService: MultiAgentAdvisorService) {}

  // ─────────────────────────────────────────────────────────────────────────────
  // Irrigation Council - مجلس الري
  // ─────────────────────────────────────────────────────────────────────────────

  @Post('irrigation')
  @ApiOperation({
    summary: 'Consult multi-agent council for irrigation decision',
    description: 'استشارة مجلس متعدد الوكلاء لقرار الري - FAO Expert + Crop Model + Local Wisdom + Precision Ag + Economist',
  })
  @ApiBody({
    description: 'Irrigation question parameters',
    schema: {
      type: 'object',
      properties: {
        cropType: { type: 'string', example: 'CORN' },
        currentSoilMoisture: { type: 'number', example: 0.22, description: 'Volumetric water content (0-1)' },
        weatherForecast: {
          type: 'object',
          properties: {
            temperature: { type: 'number', example: 32 },
            precipitation: { type: 'number', example: 5, description: 'Expected rain (mm)' },
            et0: { type: 'number', example: 5.5, description: 'Reference ET (mm/day)' },
          },
        },
        growthStage: { type: 'string', example: 'flowering', enum: ['seedling', 'vegetative', 'flowering', 'maturity'] },
        lastIrrigation: { type: 'string', example: '2024-11-10' },
      },
      required: ['cropType', 'currentSoilMoisture', 'weatherForecast', 'growthStage'],
    },
  })
  @ApiResponse({ status: 200, description: 'Multi-agent council session result' })
  consultIrrigation(@Body() input: IrrigationQuestionInput) {
    const session = this.multiAgentService.consultIrrigationCouncil(input);

    return {
      ...session,
      apiNote: 'Council of 5 AI agents with different perspectives',
      apiNoteAr: 'مجلس من 5 وكلاء ذكاء اصطناعي بوجهات نظر مختلفة',
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Pest/Disease Council - مجلس الآفات والأمراض
  // ─────────────────────────────────────────────────────────────────────────────

  @Post('pest')
  @ApiOperation({
    summary: 'Consult multi-agent council for pest/disease diagnosis',
    description: 'استشارة مجلس متعدد الوكلاء لتشخيص الآفات والأمراض',
  })
  @ApiBody({
    description: 'Pest/disease question parameters',
    schema: {
      type: 'object',
      properties: {
        cropType: { type: 'string', example: 'TOMATO' },
        symptoms: {
          type: 'array',
          items: { type: 'string' },
          example: ['yellow leaves', 'brown spots', 'wilting'],
        },
        location: { type: 'string', example: 'Riyadh' },
        season: { type: 'string', example: 'summer' },
        temperature: { type: 'number', example: 35 },
        humidity: { type: 'number', example: 45 },
      },
      required: ['cropType', 'symptoms', 'location', 'season', 'temperature', 'humidity'],
    },
  })
  @ApiResponse({ status: 200, description: 'Multi-agent pest diagnosis result' })
  consultPest(@Body() input: PestQuestionInput) {
    const session = this.multiAgentService.consultPestCouncil(input);

    return {
      ...session,
      apiNote: 'Multi-perspective pest/disease diagnosis',
      apiNoteAr: 'تشخيص الآفات/الأمراض من وجهات نظر متعددة',
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Quick Consultation - استشارة سريعة
  // ─────────────────────────────────────────────────────────────────────────────

  @Get('quick')
  @ApiOperation({
    summary: 'Get quick advice without full council session',
    description: 'الحصول على نصيحة سريعة بدون جلسة مجلس كاملة',
  })
  @ApiQuery({ name: 'category', required: true, enum: ['irrigation', 'pest', 'fertilizer', 'general'] })
  @ApiQuery({ name: 'question', required: false, example: 'Should I irrigate today?' })
  @ApiResponse({ status: 200, description: 'Quick advice' })
  quickConsult(
    @Query('category') category: 'irrigation' | 'pest' | 'fertilizer' | 'general',
    @Query('question') question?: string,
  ) {
    const advice = this.multiAgentService.quickConsult(question || '', category);

    return {
      category,
      question: question || 'General guidance',
      ...advice,
      note: 'For detailed analysis, use the full council endpoints',
      noteAr: 'للتحليل التفصيلي، استخدم نقاط نهاية المجلس الكاملة',
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Council Agents - الحصول على وكلاء المجلس
  // ─────────────────────────────────────────────────────────────────────────────

  @Get('agents')
  @ApiOperation({
    summary: 'List all council agents and their specialties',
    description: 'قائمة جميع وكلاء المجلس وتخصصاتهم',
  })
  @ApiResponse({ status: 200, description: 'List of agents' })
  listAgents() {
    const agents = this.multiAgentService.getAgents();

    return {
      agents,
      total: agents.length,
      description: 'Each agent brings a unique perspective to agricultural decisions',
      descriptionAr: 'كل وكيل يجلب وجهة نظر فريدة لقرارات الزراعة',
    };
  }

  @Get('agents/:id')
  @ApiOperation({
    summary: 'Get details of specific council agent',
    description: 'الحصول على تفاصيل وكيل معين في المجلس',
  })
  @ApiParam({ name: 'id', example: 'fao_expert' })
  @ApiResponse({ status: 200, description: 'Agent details' })
  getAgent(@Param('id') id: string) {
    const agent = this.multiAgentService.getAgentById(id);

    if (!agent) {
      return {
        error: `Agent ${id} not found`,
        availableAgents: this.multiAgentService.getAgents().map(a => a.id),
      };
    }

    return { agent };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Demo Session - جلسة تجريبية
  // ─────────────────────────────────────────────────────────────────────────────

  @Get('demo')
  @ApiOperation({
    summary: 'Run a demo council session',
    description: 'تشغيل جلسة مجلس تجريبية',
  })
  @ApiQuery({ name: 'type', required: false, enum: ['irrigation', 'pest'], example: 'irrigation' })
  @ApiResponse({ status: 200, description: 'Demo session result' })
  runDemo(@Query('type') type?: string) {
    if (type === 'pest') {
      return this.multiAgentService.consultPestCouncil({
        cropType: 'TOMATO',
        symptoms: ['yellow leaves', 'brown spots'],
        location: 'Riyadh',
        season: 'summer',
        temperature: 35,
        humidity: 50,
      });
    }

    // Default: irrigation demo
    return this.multiAgentService.consultIrrigationCouncil({
      cropType: 'CORN',
      currentSoilMoisture: 0.20,
      weatherForecast: {
        temperature: 32,
        precipitation: 2,
        et0: 6.0,
      },
      growthStage: 'flowering',
    });
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Health Check
  // ─────────────────────────────────────────────────────────────────────────────

  @Get('health')
  @ApiOperation({
    summary: 'Multi-agent advisor service health check',
    description: 'فحص صحة خدمة المستشار متعدد الوكلاء',
  })
  @ApiResponse({ status: 200, description: 'Service is healthy' })
  healthCheck() {
    const agents = this.multiAgentService.getAgents();

    return {
      status: 'healthy',
      service: 'multi-agent-advisor',
      timestamp: new Date().toISOString(),
      version: '1.0.0',
      inspiration: 'Karpathy LLM-Council',
      councilAgents: agents.length,
      agentList: agents.map(a => ({ id: a.id, name: a.name, nameAr: a.nameAr })),
      capabilities: ['irrigation', 'pest/disease', 'fertilizer', 'general'],
      features: [
        'Multi-perspective analysis',
        'Consensus building',
        'Confidence scoring',
        'Bilingual output (EN/AR)',
      ],
    };
  }
}
