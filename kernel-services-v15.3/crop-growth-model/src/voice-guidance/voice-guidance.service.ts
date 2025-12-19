// ═══════════════════════════════════════════════════════════════════════════════
// Voice Guidance Service - خدمة التوجيه الصوتي للمزارعين
// Inspired by SoulX-Podcast AI voice generation concept
// Agricultural audio guidance for farmers in their native language
// ═══════════════════════════════════════════════════════════════════════════════

import { Injectable } from '@nestjs/common';

// ─────────────────────────────────────────────────────────────────────────────
// Interfaces & Types
// ─────────────────────────────────────────────────────────────────────────────

interface VoiceProfile {
  id: string;
  nameEn: string;
  nameAr: string;
  language: 'ar' | 'en' | 'ar-sa' | 'ar-eg' | 'ar-ma';
  gender: 'male' | 'female';
  style: 'expert' | 'friendly' | 'formal' | 'storytelling';
  specialty?: string;
}

interface GuidanceScript {
  id: string;
  category: string;
  titleEn: string;
  titleAr: string;
  contentEn: string;
  contentAr: string;
  duration: number; // seconds
  tags: string[];
}

interface PodcastEpisode {
  id: string;
  titleEn: string;
  titleAr: string;
  descriptionEn: string;
  descriptionAr: string;
  duration: number;
  segments: PodcastSegment[];
  voice: VoiceProfile;
  generatedAt: string;
}

interface PodcastSegment {
  order: number;
  type: 'intro' | 'main' | 'tip' | 'warning' | 'summary' | 'outro';
  contentEn: string;
  contentAr: string;
  duration: number;
}

interface FieldBriefing {
  id: string;
  fieldName: string;
  date: string;
  conditions: {
    weather: string;
    soilMoisture: number;
    cropStage: string;
    ndvi?: number;
  };
  recommendations: string[];
  recommendationsAr: string[];
  urgentAlerts: string[];
  urgentAlertsAr: string[];
  voice: VoiceProfile;
  estimatedDuration: number;
}

interface GuidanceRequest {
  topic: string;
  cropType?: string;
  language?: 'ar' | 'en';
  voiceStyle?: 'expert' | 'friendly' | 'formal' | 'storytelling';
  includeLocalWisdom?: boolean;
}

@Injectable()
export class VoiceGuidanceService {
  // ─────────────────────────────────────────────────────────────────────────────
  // Voice Profiles Database - أصوات المرشدين الزراعيين
  // ─────────────────────────────────────────────────────────────────────────────

  private readonly voiceProfiles: Map<string, VoiceProfile> = new Map([
    ['abu_ahmad', {
      id: 'abu_ahmad',
      nameEn: 'Abu Ahmad - Saudi Farm Expert',
      nameAr: 'أبو أحمد - خبير المزارع السعودية',
      language: 'ar-sa',
      gender: 'male',
      style: 'storytelling',
      specialty: 'Date palms and local crops',
    }],
    ['dr_fatima', {
      id: 'dr_fatima',
      nameEn: 'Dr. Fatima - Agricultural Scientist',
      nameAr: 'د. فاطمة - عالمة زراعية',
      language: 'ar',
      gender: 'female',
      style: 'expert',
      specialty: 'Precision agriculture and irrigation',
    }],
    ['farmer_john', {
      id: 'farmer_john',
      nameEn: 'John - Practical Farming Tips',
      nameAr: 'جون - نصائح زراعية عملية',
      language: 'en',
      gender: 'male',
      style: 'friendly',
      specialty: 'General farming practices',
    }],
    ['hajja_khadija', {
      id: 'hajja_khadija',
      nameEn: 'Hajja Khadija - Traditional Wisdom',
      nameAr: 'الحاجة خديجة - الحكمة التقليدية',
      language: 'ar-sa',
      gender: 'female',
      style: 'storytelling',
      specialty: 'Traditional farming knowledge',
    }],
    ['eng_mohammed', {
      id: 'eng_mohammed',
      nameEn: 'Eng. Mohammed - AgTech Expert',
      nameAr: 'م. محمد - خبير التقنية الزراعية',
      language: 'ar',
      gender: 'male',
      style: 'formal',
      specialty: 'Smart farming technology',
    }],
  ]);

  // ─────────────────────────────────────────────────────────────────────────────
  // Guidance Scripts Library - مكتبة النصوص الإرشادية
  // ─────────────────────────────────────────────────────────────────────────────

  private readonly guidanceScripts: GuidanceScript[] = [
    // Irrigation Guidance
    {
      id: 'irrigation_basics',
      category: 'irrigation',
      titleEn: 'Smart Irrigation Fundamentals',
      titleAr: 'أساسيات الري الذكي',
      contentEn: `Welcome farmer! Today we discuss smart irrigation. The key is giving your crops
        the right amount of water at the right time. Too much water drowns roots and wastes resources.
        Too little stresses your plants. We use soil moisture sensors and ET calculations to find
        the perfect balance. The FAO-56 method helps us calculate exactly how much water your crops
        need based on weather conditions. Remember: healthy roots mean healthy yields!`,
      contentAr: `مرحباً بك يا مزارع! اليوم نتحدث عن الري الذكي. المفتاح هو إعطاء محاصيلك
        الكمية المناسبة من الماء في الوقت المناسب. الماء الزائد يغرق الجذور ويهدر الموارد.
        والماء القليل يجهد نباتاتك. نستخدم حساسات رطوبة التربة وحسابات التبخر-النتح لإيجاد
        التوازن المثالي. طريقة FAO-56 تساعدنا في حساب كمية الماء التي تحتاجها محاصيلك بناءً
        على الظروف الجوية. تذكر: الجذور الصحية تعني إنتاجية صحية!`,
      duration: 90,
      tags: ['irrigation', 'basics', 'fao56', 'soil-moisture'],
    },
    {
      id: 'irrigation_timing',
      category: 'irrigation',
      titleEn: 'Best Times to Irrigate',
      titleAr: 'أفضل أوقات الري',
      contentEn: `The timing of irrigation is crucial. Early morning irrigation, before 9 AM,
        is ideal because water loss to evaporation is minimal, leaves dry quickly reducing disease risk,
        and plants are ready to use water during peak photosynthesis hours. Avoid midday irrigation
        when evaporation is highest. Evening irrigation can work but wet leaves overnight may invite
        fungal diseases. In Saudi Arabia's hot summers, some farmers irrigate at night - this is
        acceptable for drip irrigation systems where leaves stay dry.`,
      contentAr: `توقيت الري أمر حاسم. الري في الصباح الباكر، قبل الساعة 9، مثالي لأن فقدان الماء
        بالتبخر يكون في أدنى مستوياته، وتجف الأوراق بسرعة مما يقلل خطر الأمراض، والنباتات جاهزة
        لاستخدام الماء خلال ساعات الذروة للتمثيل الضوئي. تجنب الري في منتصف النهار عندما يكون
        التبخر في أعلى مستوياته. الري المسائي ممكن لكن الأوراق الرطبة طوال الليل قد تجذب الأمراض
        الفطرية. في صيف السعودية الحار، بعض المزارعين يروون ليلاً - وهذا مقبول مع أنظمة الري
        بالتنقيط حيث تبقى الأوراق جافة.`,
      duration: 75,
      tags: ['irrigation', 'timing', 'best-practices'],
    },
    // Pest Management
    {
      id: 'pest_early_detection',
      category: 'pest',
      titleEn: 'Early Pest Detection Saves Crops',
      titleAr: 'الكشف المبكر عن الآفات ينقذ المحاصيل',
      contentEn: `Prevention is better than cure in pest management. Walk your fields regularly -
        at least twice a week during growing season. Look for yellowing leaves, unusual spots,
        wilting, and insect damage. Check the undersides of leaves where pests often hide.
        Our AI-powered Sahool Vision can help identify problems from photos. Early detection
        means you can use targeted treatments before pests spread. Remember: a healthy crop
        with good nutrition is naturally more resistant to pests.`,
      contentAr: `الوقاية خير من العلاج في إدارة الآفات. تفقد حقولك بانتظام - مرتين في الأسبوع
        على الأقل خلال موسم النمو. ابحث عن اصفرار الأوراق، والبقع غير العادية، والذبول،
        وأضرار الحشرات. افحص الجهة السفلية من الأوراق حيث تختبئ الآفات غالباً. رؤية سهول
        المدعومة بالذكاء الاصطناعي يمكنها المساعدة في تحديد المشاكل من الصور. الكشف المبكر
        يعني أنك تستطيع استخدام العلاجات الموجهة قبل انتشار الآفات. تذكر: المحصول الصحي
        ذو التغذية الجيدة أكثر مقاومة للآفات بشكل طبيعي.`,
      duration: 85,
      tags: ['pest', 'detection', 'prevention', 'ai'],
    },
    // Date Palm Care (Saudi-specific)
    {
      id: 'date_palm_care',
      category: 'dates',
      titleEn: 'Date Palm Care Through the Seasons',
      titleAr: 'رعاية النخيل عبر الفصول',
      contentEn: `The date palm is the jewel of Arabian agriculture. In winter, we clean and prune.
        In spring comes pollination - traditionally done by hand for best results. Summer is about
        protecting the fruit bunches from birds and reducing them for better fruit size.
        The harvest in late summer depends on whether you want fresh rutab or dried tamr dates.
        Each variety has its own timing. Water requirements change dramatically - more in summer,
        less in winter. The palms tell us when they're thirsty through their frond color.`,
      contentAr: `النخلة جوهرة الزراعة العربية. في الشتاء، ننظف ونقلم. في الربيع يأتي التلقيح -
        تقليدياً باليد للحصول على أفضل النتائج. الصيف مخصص لحماية عذوق التمر من الطيور
        وتخفيفها للحصول على حجم أفضل للثمار. الحصاد في أواخر الصيف يعتمد على ما إذا كنت
        تريد رطب طازج أو تمر مجفف. كل صنف له توقيته الخاص. احتياجات الماء تتغير بشكل كبير -
        أكثر في الصيف، أقل في الشتاء. النخيل تخبرنا عندما تكون عطشى من خلال لون سعفها.`,
      duration: 95,
      tags: ['dates', 'palm', 'saudi', 'traditional'],
    },
    // Soil Health
    {
      id: 'soil_health_basics',
      category: 'soil',
      titleEn: 'Understanding Your Soil',
      titleAr: 'فهم تربتك',
      contentEn: `Soil is not just dirt - it's a living ecosystem! Healthy soil contains billions
        of beneficial microorganisms. In sandy desert soils common in Saudi Arabia, we face challenges
        of low water retention and nutrient leaching. Adding organic matter is key - compost, manure,
        or cover crops. This improves water holding capacity and feeds soil life. Soil testing
        every season helps you know exactly what nutrients are needed. pH matters too - most crops
        prefer slightly acidic to neutral soil between 6.0 and 7.0.`,
      contentAr: `التربة ليست مجرد تراب - إنها نظام بيئي حي! التربة الصحية تحتوي على مليارات
        الكائنات الحية المفيدة. في التربة الرملية الصحراوية الشائعة في السعودية، نواجه تحديات
        انخفاض احتباس الماء وغسل المغذيات. إضافة المادة العضوية هو المفتاح - السماد العضوي،
        أو روث الحيوانات، أو محاصيل التغطية. هذا يحسن قدرة احتباس الماء ويغذي الحياة في التربة.
        اختبار التربة كل موسم يساعدك على معرفة المغذيات المطلوبة بالضبط. درجة الحموضة مهمة
        أيضاً - معظم المحاصيل تفضل تربة حمضية قليلاً إلى متعادلة بين 6.0 و 7.0.`,
      duration: 80,
      tags: ['soil', 'organic', 'nutrients', 'testing'],
    },
    // Weather & Planning
    {
      id: 'weather_planning',
      category: 'weather',
      titleEn: 'Using Weather Forecasts for Farm Planning',
      titleAr: 'استخدام التنبؤات الجوية للتخطيط الزراعي',
      contentEn: `Modern farmers are weather watchers! Sahool's weather service gives you forecasts
        tailored for agriculture. Before planting, check for frost risk. Before spraying, ensure
        no rain is expected for 24 hours. High winds mean skip the spraying - chemicals drift.
        Heat waves mean more irrigation. Cold snaps need frost protection. Use our agricultural
        calendar feature to plan tasks around weather windows. The best time to plant is not
        just about the season, but about the specific weather conditions.`,
      contentAr: `المزارعون المعاصرون مراقبون للطقس! خدمة الطقس في سهول تعطيك تنبؤات مخصصة
        للزراعة. قبل الزراعة، تحقق من خطر الصقيع. قبل الرش، تأكد من عدم توقع هطول أمطار
        لمدة 24 ساعة. الرياح القوية تعني تخطي الرش - المواد الكيميائية تنجرف. موجات الحر
        تعني مزيداً من الري. موجات البرد تحتاج حماية من الصقيع. استخدم ميزة التقويم الزراعي
        لتخطيط المهام حول نوافذ الطقس. أفضل وقت للزراعة لا يتعلق فقط بالموسم، بل بالظروف
        الجوية المحددة.`,
      duration: 70,
      tags: ['weather', 'planning', 'frost', 'calendar'],
    },
  ];

  // ─────────────────────────────────────────────────────────────────────────────
  // Traditional Wisdom Quotes - حكم تقليدية
  // ─────────────────────────────────────────────────────────────────────────────

  private readonly traditionalWisdom: { en: string; ar: string }[] = [
    {
      en: 'The farmer who watches the sky waters at the right time.',
      ar: 'المزارع الذي يراقب السماء يروي في الوقت المناسب.',
    },
    {
      en: 'A palm tree planted by your grandfather will feed your grandchildren.',
      ar: 'نخلة غرسها جدك ستطعم أحفادك.',
    },
    {
      en: 'The soil remembers every drop of sweat you give it.',
      ar: 'التربة تتذكر كل قطرة عرق تعطيها إياها.',
    },
    {
      en: 'Better a small harvest with peace than a large one with debt.',
      ar: 'حصاد صغير بسلام خير من حصاد كبير بديون.',
    },
    {
      en: 'The best fertilizer is the farmer\'s footsteps.',
      ar: 'أفضل سماد هو خطوات المزارع.',
    },
    {
      en: 'Plant in the morning, water in the evening, trust in Allah.',
      ar: 'ازرع في الصباح، واسقِ في المساء، وتوكل على الله.',
    },
    {
      en: 'A healthy seed in poor soil beats a poor seed in healthy soil.',
      ar: 'بذرة صحية في تربة فقيرة تتفوق على بذرة ضعيفة في تربة صحية.',
    },
  ];

  // ─────────────────────────────────────────────────────────────────────────────
  // Service Methods
  // ─────────────────────────────────────────────────────────────────────────────

  /**
   * Get all available voice profiles
   */
  getVoiceProfiles(): VoiceProfile[] {
    return Array.from(this.voiceProfiles.values());
  }

  /**
   * Get voice profile by ID
   */
  getVoiceProfileById(id: string): VoiceProfile | undefined {
    return this.voiceProfiles.get(id);
  }

  /**
   * Get all guidance scripts
   */
  getAllScripts(): GuidanceScript[] {
    return this.guidanceScripts;
  }

  /**
   * Get scripts by category
   */
  getScriptsByCategory(category: string): GuidanceScript[] {
    return this.guidanceScripts.filter(s => s.category === category);
  }

  /**
   * Get script by ID
   */
  getScriptById(id: string): GuidanceScript | undefined {
    return this.guidanceScripts.find(s => s.id === id);
  }

  /**
   * Generate a daily field briefing for farmer
   */
  generateFieldBriefing(params: {
    fieldName: string;
    weather: string;
    soilMoisture: number;
    cropStage: string;
    ndvi?: number;
    alerts?: string[];
    language?: 'ar' | 'en';
  }): FieldBriefing {
    const voice = params.language === 'en'
      ? this.voiceProfiles.get('farmer_john')!
      : this.voiceProfiles.get('abu_ahmad')!;

    const recommendations: string[] = [];
    const recommendationsAr: string[] = [];
    const urgentAlerts: string[] = [];
    const urgentAlertsAr: string[] = [];

    // Analyze soil moisture
    if (params.soilMoisture < 0.15) {
      recommendations.push('Critical: Irrigate immediately - soil moisture critically low');
      recommendationsAr.push('حرج: قم بالري فوراً - رطوبة التربة منخفضة بشكل حرج');
      urgentAlerts.push('Low soil moisture requires immediate attention');
      urgentAlertsAr.push('انخفاض رطوبة التربة يتطلب اهتماماً فورياً');
    } else if (params.soilMoisture < 0.25) {
      recommendations.push('Plan irrigation within the next 24-48 hours');
      recommendationsAr.push('خطط للري خلال 24-48 ساعة القادمة');
    } else if (params.soilMoisture > 0.40) {
      recommendations.push('Soil moisture is adequate - no irrigation needed today');
      recommendationsAr.push('رطوبة التربة كافية - لا حاجة للري اليوم');
    }

    // Analyze NDVI if provided
    if (params.ndvi !== undefined) {
      if (params.ndvi < 0.3) {
        recommendations.push('Low vegetation index detected - check for plant stress');
        recommendationsAr.push('مؤشر نباتي منخفض - تحقق من إجهاد النبات');
        urgentAlerts.push('Vegetation health concern - field inspection recommended');
        urgentAlertsAr.push('قلق بشأن صحة النباتات - يوصى بفحص الحقل');
      } else if (params.ndvi > 0.6) {
        recommendations.push('Excellent vegetation health - crops are thriving');
        recommendationsAr.push('صحة نباتية ممتازة - المحاصيل تزدهر');
      }
    }

    // Growth stage specific advice
    if (params.cropStage === 'flowering') {
      recommendations.push('Flowering stage is critical - maintain consistent moisture');
      recommendationsAr.push('مرحلة الإزهار حرجة - حافظ على رطوبة ثابتة');
    } else if (params.cropStage === 'maturity') {
      recommendations.push('Approaching harvest - reduce irrigation gradually');
      recommendationsAr.push('اقتراب الحصاد - قلل الري تدريجياً');
    }

    // Add any alerts from parameters
    if (params.alerts) {
      urgentAlerts.push(...params.alerts);
      urgentAlertsAr.push(...params.alerts.map(a => `تنبيه: ${a}`));
    }

    return {
      id: `briefing_${Date.now()}`,
      fieldName: params.fieldName,
      date: new Date().toISOString().split('T')[0],
      conditions: {
        weather: params.weather,
        soilMoisture: params.soilMoisture,
        cropStage: params.cropStage,
        ndvi: params.ndvi,
      },
      recommendations,
      recommendationsAr,
      urgentAlerts,
      urgentAlertsAr,
      voice,
      estimatedDuration: 60 + recommendations.length * 15 + urgentAlerts.length * 10,
    };
  }

  /**
   * Generate a podcast-style episode on agricultural topic
   */
  generatePodcastEpisode(request: GuidanceRequest): PodcastEpisode {
    const language = request.language || 'ar';
    const voiceId = request.voiceStyle === 'storytelling'
      ? (language === 'ar' ? 'hajja_khadija' : 'farmer_john')
      : request.voiceStyle === 'expert'
        ? 'dr_fatima'
        : request.voiceStyle === 'formal'
          ? 'eng_mohammed'
          : 'abu_ahmad';

    const voice = this.voiceProfiles.get(voiceId) || this.voiceProfiles.get('abu_ahmad')!;

    // Find relevant scripts
    const relevantScripts = this.guidanceScripts.filter(s =>
      s.tags.some(t => request.topic.toLowerCase().includes(t)) ||
      s.category === request.topic.toLowerCase(),
    );

    const mainScript = relevantScripts[0] || this.guidanceScripts[0];

    // Build segments
    const segments: PodcastSegment[] = [
      {
        order: 1,
        type: 'intro',
        contentEn: `Welcome to Sahool Farm Radio. I'm ${voice.nameEn.split(' - ')[0]}.
          Today we're discussing ${mainScript.titleEn}. Stay tuned for practical tips
          you can use on your farm today.`,
        contentAr: `مرحباً بكم في إذاعة سهول الزراعية. أنا ${voice.nameAr.split(' - ')[0]}.
          اليوم نتحدث عن ${mainScript.titleAr}. ابقوا معنا للحصول على نصائح عملية
          يمكنكم استخدامها في مزارعكم اليوم.`,
        duration: 20,
      },
      {
        order: 2,
        type: 'main',
        contentEn: mainScript.contentEn,
        contentAr: mainScript.contentAr,
        duration: mainScript.duration,
      },
    ];

    // Add crop-specific tip if crop type provided
    if (request.cropType) {
      segments.push({
        order: 3,
        type: 'tip',
        contentEn: `Special tip for ${request.cropType} growers: Monitor your crop closely
          during this season. Use Sahool's AI tools for early detection of any issues.`,
        contentAr: `نصيحة خاصة لمزارعي ${request.cropType}: راقبوا محصولكم عن كثب
          خلال هذا الموسم. استخدموا أدوات سهول الذكية للكشف المبكر عن أي مشاكل.`,
        duration: 25,
      });
    }

    // Add traditional wisdom if requested
    if (request.includeLocalWisdom) {
      const wisdom = this.traditionalWisdom[Math.floor(Math.random() * this.traditionalWisdom.length)];
      segments.push({
        order: segments.length + 1,
        type: 'tip',
        contentEn: `And our elders used to say: "${wisdom.en}"`,
        contentAr: `وكان أجدادنا يقولون: "${wisdom.ar}"`,
        duration: 15,
      });
    }

    // Add summary
    segments.push({
      order: segments.length + 1,
      type: 'summary',
      contentEn: `To summarize today's key points: focus on timing, observation, and using
        the right tools for the job. Small improvements in farming practices lead to big
        improvements in yield.`,
      contentAr: `لتلخيص النقاط الرئيسية اليوم: ركزوا على التوقيت، والملاحظة، واستخدام
        الأدوات المناسبة للمهمة. التحسينات الصغيرة في الممارسات الزراعية تؤدي إلى تحسينات
        كبيرة في الإنتاجية.`,
      duration: 25,
    });

    // Add outro
    segments.push({
      order: segments.length + 1,
      type: 'outro',
      contentEn: `Thank you for listening to Sahool Farm Radio. May your harvest be abundant.
        Until next time, happy farming!`,
      contentAr: `شكراً لاستماعكم لإذاعة سهول الزراعية. نتمنى لكم محصولاً وفيراً.
        إلى اللقاء، زراعة سعيدة!`,
      duration: 15,
    });

    const totalDuration = segments.reduce((sum, s) => sum + s.duration, 0);

    return {
      id: `podcast_${Date.now()}`,
      titleEn: `Farm Radio: ${mainScript.titleEn}`,
      titleAr: `إذاعة المزرعة: ${mainScript.titleAr}`,
      descriptionEn: `Expert guidance on ${request.topic} for farmers`,
      descriptionAr: `إرشاد خبير حول ${request.topic} للمزارعين`,
      duration: totalDuration,
      segments,
      voice,
      generatedAt: new Date().toISOString(),
    };
  }

  /**
   * Get quick audio tip for specific situation
   */
  getQuickTip(situation: 'morning' | 'midday' | 'evening' | 'emergency', language: 'ar' | 'en' = 'ar'): {
    tip: string;
    tipAr: string;
    voice: VoiceProfile;
    duration: number;
  } {
    const tips: { [key: string]: { en: string; ar: string } } = {
      morning: {
        en: 'Good morning farmer! Today is a great day to inspect your fields. Walk through and observe your crops - they will tell you what they need.',
        ar: 'صباح الخير يا مزارع! اليوم يوم رائع لتفقد حقولك. امش بينها ولاحظ محاصيلك - ستخبرك بما تحتاجه.',
      },
      midday: {
        en: 'Avoid irrigation now - midday evaporation wastes water. If you see wilting, don\'t panic - slight afternoon wilt is normal and plants recover by evening.',
        ar: 'تجنب الري الآن - التبخر في منتصف النهار يهدر الماء. إذا رأيت ذبولاً، لا تقلق - الذبول الطفيف بعد الظهر طبيعي والنباتات تتعافى بحلول المساء.',
      },
      evening: {
        en: 'Evening is perfect for planning tomorrow\'s tasks. Check weather forecasts, review sensor data, and prepare your equipment. Rest well - farming needs a rested mind.',
        ar: 'المساء مثالي للتخطيط لمهام الغد. تحقق من توقعات الطقس، راجع بيانات المستشعرات، وجهز معداتك. استرح جيداً - الزراعة تحتاج عقلاً مرتاحاً.',
      },
      emergency: {
        en: 'If you detect a pest outbreak or disease, act quickly but calmly. Document with photos, isolate affected plants if possible, and consult Sahool\'s AI advisor immediately.',
        ar: 'إذا اكتشفت تفشي آفة أو مرض، تصرف بسرعة ولكن بهدوء. وثق بالصور، اعزل النباتات المصابة إن أمكن، واستشر مستشار سهول الذكي فوراً.',
      },
    };

    const tip = tips[situation];
    const voice = language === 'en'
      ? this.voiceProfiles.get('farmer_john')!
      : this.voiceProfiles.get('abu_ahmad')!;

    return {
      tip: language === 'en' ? tip.en : tip.ar,
      tipAr: tip.ar,
      voice,
      duration: 30,
    };
  }

  /**
   * Get all categories available for guidance
   */
  getCategories(): { id: string; nameEn: string; nameAr: string; scriptCount: number }[] {
    const categories = new Map<string, number>();
    this.guidanceScripts.forEach(s => {
      categories.set(s.category, (categories.get(s.category) || 0) + 1);
    });

    const categoryNames: { [key: string]: { en: string; ar: string } } = {
      irrigation: { en: 'Irrigation', ar: 'الري' },
      pest: { en: 'Pest Management', ar: 'إدارة الآفات' },
      dates: { en: 'Date Palm Care', ar: 'رعاية النخيل' },
      soil: { en: 'Soil Health', ar: 'صحة التربة' },
      weather: { en: 'Weather & Planning', ar: 'الطقس والتخطيط' },
    };

    return Array.from(categories.entries()).map(([id, count]) => ({
      id,
      nameEn: categoryNames[id]?.en || id,
      nameAr: categoryNames[id]?.ar || id,
      scriptCount: count,
    }));
  }

  /**
   * Get random traditional wisdom
   */
  getTraditionalWisdom(): { en: string; ar: string } {
    return this.traditionalWisdom[Math.floor(Math.random() * this.traditionalWisdom.length)];
  }

  /**
   * Get all traditional wisdom
   */
  getAllTraditionalWisdom(): { en: string; ar: string }[] {
    return this.traditionalWisdom;
  }
}
