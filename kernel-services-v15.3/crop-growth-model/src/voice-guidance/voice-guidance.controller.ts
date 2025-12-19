// ═══════════════════════════════════════════════════════════════════════════════
// Voice Guidance Controller - مراقب التوجيه الصوتي
// REST API for AI-powered agricultural voice guidance (SoulX-Podcast inspired)
// ═══════════════════════════════════════════════════════════════════════════════

import { Controller, Get, Post, Body, Param, Query } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse, ApiQuery, ApiBody, ApiParam } from '@nestjs/swagger';
import { VoiceGuidanceService } from './voice-guidance.service';

class FieldBriefingInput {
  fieldName: string;
  weather: string;
  soilMoisture: number;
  cropStage: string;
  ndvi?: number;
  alerts?: string[];
  language?: 'ar' | 'en';
}

class PodcastRequest {
  topic: string;
  cropType?: string;
  language?: 'ar' | 'en';
  voiceStyle?: 'expert' | 'friendly' | 'formal' | 'storytelling';
  includeLocalWisdom?: boolean;
}

@ApiTags('voice-guidance')
@Controller('api/v1/voice-guidance')
export class VoiceGuidanceController {
  constructor(private readonly voiceGuidanceService: VoiceGuidanceService) {}

  // ─────────────────────────────────────────────────────────────────────────────
  // Voice Profiles - أصوات المرشدين
  // ─────────────────────────────────────────────────────────────────────────────

  @Get('voices')
  @ApiOperation({
    summary: 'List all available voice profiles',
    description: 'قائمة جميع أصوات المرشدين الزراعيين المتاحة',
  })
  @ApiResponse({ status: 200, description: 'List of voice profiles' })
  listVoices() {
    const voices = this.voiceGuidanceService.getVoiceProfiles();

    return {
      voices,
      total: voices.length,
      languages: ['ar', 'ar-sa', 'ar-eg', 'en'],
      styles: ['expert', 'friendly', 'formal', 'storytelling'],
      note: 'Each voice has unique personality and specialty',
      noteAr: 'كل صوت له شخصية وتخصص فريد',
    };
  }

  @Get('voices/:id')
  @ApiOperation({
    summary: 'Get voice profile details',
    description: 'الحصول على تفاصيل صوت مرشد معين',
  })
  @ApiParam({ name: 'id', example: 'abu_ahmad' })
  @ApiResponse({ status: 200, description: 'Voice profile details' })
  getVoice(@Param('id') id: string) {
    const voice = this.voiceGuidanceService.getVoiceProfileById(id);

    if (!voice) {
      return {
        error: `Voice profile ${id} not found`,
        availableVoices: this.voiceGuidanceService.getVoiceProfiles().map(v => ({
          id: v.id,
          name: v.nameEn,
        })),
      };
    }

    return { voice };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Guidance Scripts - النصوص الإرشادية
  // ─────────────────────────────────────────────────────────────────────────────

  @Get('scripts')
  @ApiOperation({
    summary: 'List all guidance scripts',
    description: 'قائمة جميع النصوص الإرشادية المتاحة',
  })
  @ApiQuery({ name: 'category', required: false, example: 'irrigation' })
  @ApiResponse({ status: 200, description: 'List of scripts' })
  listScripts(@Query('category') category?: string) {
    const scripts = category
      ? this.voiceGuidanceService.getScriptsByCategory(category)
      : this.voiceGuidanceService.getAllScripts();

    return {
      scripts: scripts.map(s => ({
        id: s.id,
        titleEn: s.titleEn,
        titleAr: s.titleAr,
        category: s.category,
        duration: s.duration,
        tags: s.tags,
      })),
      total: scripts.length,
      categories: this.voiceGuidanceService.getCategories(),
    };
  }

  @Get('scripts/:id')
  @ApiOperation({
    summary: 'Get full script content',
    description: 'الحصول على محتوى النص الإرشادي الكامل',
  })
  @ApiParam({ name: 'id', example: 'irrigation_basics' })
  @ApiResponse({ status: 200, description: 'Script content' })
  getScript(@Param('id') id: string) {
    const script = this.voiceGuidanceService.getScriptById(id);

    if (!script) {
      return {
        error: `Script ${id} not found`,
        availableScripts: this.voiceGuidanceService.getAllScripts().map(s => s.id),
      };
    }

    return {
      script,
      suggestedVoices: this.voiceGuidanceService.getVoiceProfiles().filter(v =>
        script.tags.includes('saudi') ? v.language.startsWith('ar') : true,
      ),
    };
  }

  @Get('categories')
  @ApiOperation({
    summary: 'List all guidance categories',
    description: 'قائمة جميع فئات التوجيه الإرشادي',
  })
  @ApiResponse({ status: 200, description: 'List of categories' })
  listCategories() {
    const categories = this.voiceGuidanceService.getCategories();

    return {
      categories,
      total: categories.length,
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Field Briefing - ملخص الحقل اليومي
  // ─────────────────────────────────────────────────────────────────────────────

  @Post('briefing')
  @ApiOperation({
    summary: 'Generate daily field briefing for farmer',
    description: 'توليد ملخص يومي للحقل للمزارع - صوت الصباح',
  })
  @ApiBody({
    description: 'Field conditions',
    schema: {
      type: 'object',
      properties: {
        fieldName: { type: 'string', example: 'North Field - Wheat' },
        weather: { type: 'string', example: 'sunny, 32°C, light wind' },
        soilMoisture: { type: 'number', example: 0.22, description: 'Volumetric (0-1)' },
        cropStage: { type: 'string', example: 'flowering' },
        ndvi: { type: 'number', example: 0.65, description: 'Vegetation index (optional)' },
        alerts: {
          type: 'array',
          items: { type: 'string' },
          example: ['Pest risk elevated due to humidity'],
        },
        language: { type: 'string', enum: ['ar', 'en'], example: 'ar' },
      },
      required: ['fieldName', 'weather', 'soilMoisture', 'cropStage'],
    },
  })
  @ApiResponse({ status: 200, description: 'Field briefing generated' })
  generateBriefing(@Body() input: FieldBriefingInput) {
    const briefing = this.voiceGuidanceService.generateFieldBriefing(input);

    return {
      ...briefing,
      apiNote: 'This briefing can be converted to audio using TTS integration',
      apiNoteAr: 'يمكن تحويل هذا الملخص إلى صوت باستخدام تكامل تحويل النص إلى كلام',
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Podcast Generation - توليد البودكاست
  // ─────────────────────────────────────────────────────────────────────────────

  @Post('podcast')
  @ApiOperation({
    summary: 'Generate podcast-style episode on agricultural topic',
    description: 'توليد حلقة بأسلوب البودكاست حول موضوع زراعي - مستوحى من SoulX-Podcast',
  })
  @ApiBody({
    description: 'Podcast request',
    schema: {
      type: 'object',
      properties: {
        topic: { type: 'string', example: 'irrigation', description: 'Topic to cover' },
        cropType: { type: 'string', example: 'wheat', description: 'Specific crop (optional)' },
        language: { type: 'string', enum: ['ar', 'en'], example: 'ar' },
        voiceStyle: {
          type: 'string',
          enum: ['expert', 'friendly', 'formal', 'storytelling'],
          example: 'storytelling',
        },
        includeLocalWisdom: { type: 'boolean', example: true, description: 'Include traditional sayings' },
      },
      required: ['topic'],
    },
  })
  @ApiResponse({ status: 200, description: 'Podcast episode generated' })
  generatePodcast(@Body() request: PodcastRequest) {
    const episode = this.voiceGuidanceService.generatePodcastEpisode(request);

    return {
      ...episode,
      inspiration: 'SoulX-Podcast AI Voice Generation',
      ttsIntegration: 'Ready for TTS conversion',
      ttsIntegrationAr: 'جاهز للتحويل لكلام منطوق',
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Quick Tips - نصائح سريعة
  // ─────────────────────────────────────────────────────────────────────────────

  @Get('quick-tip')
  @ApiOperation({
    summary: 'Get quick audio tip for current situation',
    description: 'الحصول على نصيحة صوتية سريعة للموقف الحالي',
  })
  @ApiQuery({
    name: 'situation',
    required: true,
    enum: ['morning', 'midday', 'evening', 'emergency'],
    example: 'morning',
  })
  @ApiQuery({ name: 'language', required: false, enum: ['ar', 'en'], example: 'ar' })
  @ApiResponse({ status: 200, description: 'Quick tip' })
  getQuickTip(
    @Query('situation') situation: 'morning' | 'midday' | 'evening' | 'emergency',
    @Query('language') language?: 'ar' | 'en',
  ) {
    const tip = this.voiceGuidanceService.getQuickTip(situation, language || 'ar');

    return {
      situation,
      ...tip,
      timestamp: new Date().toISOString(),
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Traditional Wisdom - الحكمة التقليدية
  // ─────────────────────────────────────────────────────────────────────────────

  @Get('wisdom')
  @ApiOperation({
    summary: 'Get traditional farming wisdom',
    description: 'الحصول على حكمة زراعية تقليدية',
  })
  @ApiQuery({ name: 'all', required: false, type: 'boolean', description: 'Get all wisdom quotes' })
  @ApiResponse({ status: 200, description: 'Traditional wisdom' })
  getWisdom(@Query('all') all?: string) {
    if (all === 'true') {
      const allWisdom = this.voiceGuidanceService.getAllTraditionalWisdom();
      return {
        wisdom: allWisdom,
        total: allWisdom.length,
        note: 'Wisdom passed down through generations of farmers',
        noteAr: 'حكمة توارثها أجيال من المزارعين',
      };
    }

    const wisdom = this.voiceGuidanceService.getTraditionalWisdom();
    return {
      wisdom,
      note: 'Random wisdom from our elders',
      noteAr: 'حكمة عشوائية من أجدادنا',
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Demo Endpoints - نقاط النهاية التجريبية
  // ─────────────────────────────────────────────────────────────────────────────

  @Get('demo/briefing')
  @ApiOperation({
    summary: 'Run a demo field briefing',
    description: 'تشغيل ملخص حقل تجريبي',
  })
  @ApiQuery({ name: 'language', required: false, enum: ['ar', 'en'], example: 'ar' })
  @ApiResponse({ status: 200, description: 'Demo briefing' })
  demoBriefing(@Query('language') language?: 'ar' | 'en') {
    return this.voiceGuidanceService.generateFieldBriefing({
      fieldName: 'Demo Farm - North Field',
      weather: 'Sunny, 34°C, Wind 15 km/h',
      soilMoisture: 0.18,
      cropStage: 'flowering',
      ndvi: 0.58,
      alerts: ['High ET expected today - monitor moisture closely'],
      language: language || 'ar',
    });
  }

  @Get('demo/podcast')
  @ApiOperation({
    summary: 'Run a demo podcast generation',
    description: 'تشغيل توليد بودكاست تجريبي',
  })
  @ApiQuery({ name: 'topic', required: false, example: 'irrigation' })
  @ApiResponse({ status: 200, description: 'Demo podcast' })
  demoPodcast(@Query('topic') topic?: string) {
    return this.voiceGuidanceService.generatePodcastEpisode({
      topic: topic || 'irrigation',
      language: 'ar',
      voiceStyle: 'storytelling',
      includeLocalWisdom: true,
    });
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Health Check
  // ─────────────────────────────────────────────────────────────────────────────

  @Get('health')
  @ApiOperation({
    summary: 'Voice guidance service health check',
    description: 'فحص صحة خدمة التوجيه الصوتي',
  })
  @ApiResponse({ status: 200, description: 'Service is healthy' })
  healthCheck() {
    const voices = this.voiceGuidanceService.getVoiceProfiles();
    const scripts = this.voiceGuidanceService.getAllScripts();
    const categories = this.voiceGuidanceService.getCategories();

    return {
      status: 'healthy',
      service: 'voice-guidance',
      timestamp: new Date().toISOString(),
      version: '1.0.0',
      inspiration: 'SoulX-Podcast AI Voice Generation',
      stats: {
        voiceProfiles: voices.length,
        guidanceScripts: scripts.length,
        categories: categories.length,
        languages: ['ar', 'ar-sa', 'en'],
      },
      features: [
        'Daily field briefings',
        'Podcast-style episodes',
        'Quick situational tips',
        'Traditional wisdom integration',
        'Bilingual content (AR/EN)',
        'Multiple voice personalities',
      ],
      featuresAr: [
        'ملخصات الحقل اليومية',
        'حلقات بأسلوب البودكاست',
        'نصائح موقفية سريعة',
        'دمج الحكمة التقليدية',
        'محتوى ثنائي اللغة',
        'شخصيات صوتية متعددة',
      ],
      ttsReady: true,
      ttsNote: 'All content ready for TTS conversion',
    };
  }
}
