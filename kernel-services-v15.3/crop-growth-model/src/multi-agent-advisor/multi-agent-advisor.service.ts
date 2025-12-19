// ═══════════════════════════════════════════════════════════════════════════════
// Multi-Agent Agricultural Advisor Service - خدمة المستشار الزراعي متعدد الوكلاء
// Inspired by Karpathy's LLM-Council for multi-AI collaboration
// Multiple AI perspectives converge on agricultural recommendations
// ═══════════════════════════════════════════════════════════════════════════════

import { Injectable } from '@nestjs/common';

// ─────────────────────────────────────────────────────────────────────────────
// Interfaces - الواجهات
// ─────────────────────────────────────────────────────────────────────────────

interface AgentPerspective {
  agentId: string;
  agentName: string;
  agentNameAr: string;
  specialty: string;
  specialtyAr: string;
  response: string;
  responseAr: string;
  confidence: number;
  reasoning: string[];
  reasoningAr: string[];
  dataUsed: string[];
  recommendation: string;
  recommendationAr: string;
}

interface ConsensusResult {
  hasConsensus: boolean;
  consensusLevel: 'full' | 'majority' | 'partial' | 'none';
  finalRecommendation: string;
  finalRecommendationAr: string;
  dissenting: string[];
  dissentingAr: string[];
  confidence: number;
}

interface CouncilSession {
  sessionId: string;
  question: string;
  questionAr: string;
  category: string;
  timestamp: string;
  perspectives: AgentPerspective[];
  consensus: ConsensusResult;
  summary: string;
  summaryAr: string;
}

interface IrrigationQuestion {
  cropType: string;
  currentSoilMoisture: number;
  weatherForecast: { temperature: number; precipitation: number; et0: number };
  growthStage: string;
  lastIrrigation?: string;
}

interface PestQuestion {
  cropType: string;
  symptoms: string[];
  location: string;
  season: string;
  temperature: number;
  humidity: number;
}

interface FertilizerQuestion {
  cropType: string;
  soilNPK: { nitrogen: number; phosphorus: number; potassium: number };
  growthStage: string;
  targetYield: number;
  soilType: string;
}

interface AgentProfile {
  id: string;
  name: string;
  nameAr: string;
  specialty: string;
  specialtyAr: string;
  approach: string;
  approachAr: string;
  weight: number;
}

@Injectable()
export class MultiAgentAdvisorService {
  // ─────────────────────────────────────────────────────────────────────────────
  // Agent Profiles - ملفات الوكلاء
  // ─────────────────────────────────────────────────────────────────────────────

  private readonly agents: Map<string, AgentProfile> = new Map([
    ['fao_expert', {
      id: 'fao_expert',
      name: 'FAO Standards Expert',
      nameAr: 'خبير معايير الفاو',
      specialty: 'International agricultural standards and best practices',
      specialtyAr: 'المعايير الزراعية الدولية وأفضل الممارسات',
      approach: 'Evidence-based recommendations following FAO-56, FAO-33 guidelines',
      approachAr: 'توصيات مبنية على الأدلة وفق إرشادات FAO-56 و FAO-33',
      weight: 0.25,
    }],
    ['crop_model', {
      id: 'crop_model',
      name: 'Crop Model Specialist',
      nameAr: 'أخصائي نماذج المحاصيل',
      specialty: 'DSSAT, APSIM, WOFOST crop simulation models',
      specialtyAr: 'نماذج محاكاة المحاصيل DSSAT و APSIM و WOFOST',
      approach: 'Process-based simulation considering phenology, photosynthesis, and biomass',
      approachAr: 'محاكاة قائمة على العمليات تراعي الفينولوجيا والتمثيل الضوئي والكتلة الحيوية',
      weight: 0.25,
    }],
    ['local_wisdom', {
      id: 'local_wisdom',
      name: 'Regional Agriculture Expert',
      nameAr: 'خبير الزراعة الإقليمية',
      specialty: 'Traditional knowledge and local farming practices',
      specialtyAr: 'المعرفة التقليدية والممارسات الزراعية المحلية',
      approach: 'Considers local climate, soil conditions, and proven regional methods',
      approachAr: 'يراعي المناخ المحلي وظروف التربة والطرق الإقليمية المثبتة',
      weight: 0.20,
    }],
    ['precision_ag', {
      id: 'precision_ag',
      name: 'Precision Agriculture Analyst',
      nameAr: 'محلل الزراعة الدقيقة',
      specialty: 'IoT sensors, remote sensing, and data-driven farming',
      specialtyAr: 'مستشعرات إنترنت الأشياء والاستشعار عن بعد والزراعة المبنية على البيانات',
      approach: 'Real-time data analysis with satellite imagery and sensor networks',
      approachAr: 'تحليل البيانات الفوري مع صور الأقمار الصناعية وشبكات المستشعرات',
      weight: 0.15,
    }],
    ['economic_advisor', {
      id: 'economic_advisor',
      name: 'Agricultural Economist',
      nameAr: 'اقتصادي زراعي',
      specialty: 'Cost-benefit analysis and market considerations',
      specialtyAr: 'تحليل التكلفة والعائد واعتبارات السوق',
      approach: 'Optimizes for economic returns while considering resource constraints',
      approachAr: 'يحسّن العوائد الاقتصادية مع مراعاة قيود الموارد',
      weight: 0.15,
    }],
  ]);

  // ─────────────────────────────────────────────────────────────────────────────
  // Irrigation Council - مجلس الري
  // ─────────────────────────────────────────────────────────────────────────────

  consultIrrigationCouncil(input: IrrigationQuestion): CouncilSession {
    const sessionId = `IRR-${Date.now()}`;
    const perspectives: AgentPerspective[] = [];

    // FAO Expert perspective
    perspectives.push(this.getFAOIrrigationPerspective(input));

    // Crop Model perspective
    perspectives.push(this.getCropModelIrrigationPerspective(input));

    // Local Wisdom perspective
    perspectives.push(this.getLocalWisdomIrrigationPerspective(input));

    // Precision Ag perspective
    perspectives.push(this.getPrecisionAgIrrigationPerspective(input));

    // Economic perspective
    perspectives.push(this.getEconomicIrrigationPerspective(input));

    // Build consensus
    const consensus = this.buildConsensus(perspectives, 'irrigation');

    return {
      sessionId,
      question: `Should I irrigate ${input.cropType} now?`,
      questionAr: `هل يجب أن أروي ${input.cropType} الآن؟`,
      category: 'irrigation',
      timestamp: new Date().toISOString(),
      perspectives,
      consensus,
      summary: this.generateSummary(perspectives, consensus),
      summaryAr: this.generateSummaryAr(perspectives, consensus),
    };
  }

  private getFAOIrrigationPerspective(input: IrrigationQuestion): AgentPerspective {
    const agent = this.agents.get('fao_expert')!;

    // Calculate based on FAO-56 principles
    const depletionThreshold = 0.55; // Typical MAD for most crops
    const currentDepletion = 1 - input.currentSoilMoisture;
    const shouldIrrigate = currentDepletion > depletionThreshold;

    // Consider ET0 and weather
    const effectiveRain = input.weatherForecast.precipitation * 0.8;
    const netDemand = input.weatherForecast.et0 - effectiveRain;

    let recommendation = '';
    let recommendationAr = '';
    let confidence = 0.85;

    if (shouldIrrigate && netDemand > 3) {
      recommendation = `Irrigate now. Apply ${Math.round(netDemand * 1.2)} mm to restore field capacity.`;
      recommendationAr = `اروِ الآن. طبّق ${Math.round(netDemand * 1.2)} مم لاستعادة السعة الحقلية.`;
    } else if (shouldIrrigate && netDemand <= 3) {
      recommendation = `Light irrigation recommended. Apply ${Math.round(netDemand)} mm.`;
      recommendationAr = `يُوصى بري خفيف. طبّق ${Math.round(netDemand)} مم.`;
      confidence = 0.75;
    } else if (input.weatherForecast.precipitation > 5) {
      recommendation = `Wait for predicted rainfall (${input.weatherForecast.precipitation}mm expected).`;
      recommendationAr = `انتظر الأمطار المتوقعة (${input.weatherForecast.precipitation} مم متوقعة).`;
      confidence = 0.90;
    } else {
      recommendation = `No irrigation needed. Current soil moisture adequate.`;
      recommendationAr = `لا حاجة للري. رطوبة التربة الحالية كافية.`;
    }

    return {
      agentId: agent.id,
      agentName: agent.name,
      agentNameAr: agent.nameAr,
      specialty: agent.specialty,
      specialtyAr: agent.specialtyAr,
      response: `Based on FAO-56 guidelines, soil depletion is ${(currentDepletion * 100).toFixed(0)}% with ET0 of ${input.weatherForecast.et0}mm/day.`,
      responseAr: `بناءً على إرشادات FAO-56، استنزاف التربة ${(currentDepletion * 100).toFixed(0)}% مع ET0 بقيمة ${input.weatherForecast.et0} مم/يوم.`,
      confidence,
      reasoning: [
        `Soil depletion: ${(currentDepletion * 100).toFixed(0)}%`,
        `MAD threshold: ${depletionThreshold * 100}%`,
        `ET0: ${input.weatherForecast.et0} mm/day`,
        `Expected precipitation: ${input.weatherForecast.precipitation} mm`,
      ],
      reasoningAr: [
        `استنزاف التربة: ${(currentDepletion * 100).toFixed(0)}%`,
        `عتبة MAD: ${depletionThreshold * 100}%`,
        `ET0: ${input.weatherForecast.et0} مم/يوم`,
        `الأمطار المتوقعة: ${input.weatherForecast.precipitation} مم`,
      ],
      dataUsed: ['FAO-56 Penman-Monteith', 'Soil moisture sensor', 'Weather forecast'],
      recommendation,
      recommendationAr,
    };
  }

  private getCropModelIrrigationPerspective(input: IrrigationQuestion): AgentPerspective {
    const agent = this.agents.get('crop_model')!;

    // Crop model considers growth stage sensitivity
    const stageSensitivity: { [key: string]: number } = {
      seedling: 0.8,
      vegetative: 0.7,
      flowering: 0.95, // Critical stage
      maturity: 0.5,
    };

    const sensitivity = stageSensitivity[input.growthStage] || 0.7;
    const stressThreshold = 0.60 - (sensitivity * 0.15);
    const currentDepletion = 1 - input.currentSoilMoisture;
    const yieldImpact = currentDepletion > stressThreshold ? (currentDepletion - stressThreshold) * sensitivity * 100 : 0;

    let recommendation = '';
    let recommendationAr = '';
    let confidence = 0.88;

    if (input.growthStage === 'flowering' && currentDepletion > 0.35) {
      recommendation = `CRITICAL: Flowering stage - irrigate immediately to prevent ${yieldImpact.toFixed(0)}% yield loss.`;
      recommendationAr = `حرج: مرحلة الإزهار - اروِ فوراً لمنع خسارة ${yieldImpact.toFixed(0)}% من الإنتاج.`;
      confidence = 0.95;
    } else if (yieldImpact > 5) {
      recommendation = `Irrigate to prevent estimated ${yieldImpact.toFixed(0)}% yield reduction.`;
      recommendationAr = `اروِ لمنع انخفاض الإنتاج المقدر بـ ${yieldImpact.toFixed(0)}%.`;
    } else if (yieldImpact > 0) {
      recommendation = `Minor stress detected. Irrigation recommended within 24-48 hours.`;
      recommendationAr = `إجهاد طفيف مكتشف. يُوصى بالري خلال 24-48 ساعة.`;
      confidence = 0.75;
    } else {
      recommendation = `No significant yield impact expected. Monitor daily.`;
      recommendationAr = `لا يُتوقع تأثير كبير على الإنتاج. راقب يومياً.`;
    }

    return {
      agentId: agent.id,
      agentName: agent.name,
      agentNameAr: agent.nameAr,
      specialty: agent.specialty,
      specialtyAr: agent.specialtyAr,
      response: `Growth stage: ${input.growthStage} (sensitivity: ${(sensitivity * 100).toFixed(0)}%). Potential yield impact: ${yieldImpact.toFixed(1)}%.`,
      responseAr: `مرحلة النمو: ${input.growthStage} (حساسية: ${(sensitivity * 100).toFixed(0)}%). التأثير المحتمل على الإنتاج: ${yieldImpact.toFixed(1)}%.`,
      confidence,
      reasoning: [
        `Growth stage sensitivity: ${(sensitivity * 100).toFixed(0)}%`,
        `Stress threshold for stage: ${(stressThreshold * 100).toFixed(0)}%`,
        `Current depletion: ${(currentDepletion * 100).toFixed(0)}%`,
        `Estimated yield impact: ${yieldImpact.toFixed(1)}%`,
      ],
      reasoningAr: [
        `حساسية مرحلة النمو: ${(sensitivity * 100).toFixed(0)}%`,
        `عتبة الإجهاد للمرحلة: ${(stressThreshold * 100).toFixed(0)}%`,
        `الاستنزاف الحالي: ${(currentDepletion * 100).toFixed(0)}%`,
        `التأثير المقدر على الإنتاج: ${yieldImpact.toFixed(1)}%`,
      ],
      dataUsed: ['DSSAT crop model', 'Growth stage parameters', 'Yield response functions'],
      recommendation,
      recommendationAr,
    };
  }

  private getLocalWisdomIrrigationPerspective(input: IrrigationQuestion): AgentPerspective {
    const agent = this.agents.get('local_wisdom')!;

    // Regional wisdom based on temperature and season
    const isHotDay = input.weatherForecast.temperature > 35;
    const isCoolDay = input.weatherForecast.temperature < 20;

    let recommendation = '';
    let recommendationAr = '';
    let confidence = 0.70;

    if (isHotDay && input.currentSoilMoisture < 0.5) {
      recommendation = `Local practice: Irrigate early morning or late evening. Avoid midday irrigation.`;
      recommendationAr = `الممارسة المحلية: اروِ في الصباح الباكر أو المساء المتأخر. تجنب الري في منتصف النهار.`;
      confidence = 0.85;
    } else if (input.weatherForecast.precipitation > 10) {
      recommendation = `Traditional wisdom: Trust the rain. Save water and costs.`;
      recommendationAr = `الحكمة التقليدية: ثق بالمطر. وفّر الماء والتكاليف.`;
      confidence = 0.80;
    } else if (isCoolDay) {
      recommendation = `Cool weather reduces water demand. Light irrigation if soil is very dry.`;
      recommendationAr = `الطقس البارد يقلل الطلب على الماء. ري خفيف إذا كانت التربة جافة جداً.`;
    } else {
      recommendation = `Check soil by hand - if dry 10cm deep, time to irrigate.`;
      recommendationAr = `افحص التربة يدوياً - إذا كانت جافة على عمق 10 سم، حان وقت الري.`;
    }

    return {
      agentId: agent.id,
      agentName: agent.name,
      agentNameAr: agent.nameAr,
      specialty: agent.specialty,
      specialtyAr: agent.specialtyAr,
      response: `Temperature: ${input.weatherForecast.temperature}°C. Traditional practices consider local conditions.`,
      responseAr: `درجة الحرارة: ${input.weatherForecast.temperature}°م. الممارسات التقليدية تراعي الظروف المحلية.`,
      confidence,
      reasoning: [
        `Current temperature: ${input.weatherForecast.temperature}°C`,
        `Local irrigation timing practices`,
        `Traditional soil assessment methods`,
        `Seasonal patterns consideration`,
      ],
      reasoningAr: [
        `درجة الحرارة الحالية: ${input.weatherForecast.temperature}°م`,
        `ممارسات توقيت الري المحلية`,
        `طرق تقييم التربة التقليدية`,
        `مراعاة الأنماط الموسمية`,
      ],
      dataUsed: ['Local farming calendars', 'Traditional knowledge', 'Regional climate patterns'],
      recommendation,
      recommendationAr,
    };
  }

  private getPrecisionAgIrrigationPerspective(input: IrrigationQuestion): AgentPerspective {
    const agent = this.agents.get('precision_ag')!;

    // Data-driven analysis
    const moistureDeficit = (0.28 - input.currentSoilMoisture) * 100; // Assuming FC = 0.28
    const evaporativeDemand = input.weatherForecast.et0 * (input.weatherForecast.temperature / 25);

    let recommendation = '';
    let recommendationAr = '';
    let confidence = 0.82;

    if (moistureDeficit > 10 && evaporativeDemand > 5) {
      const precisAmount = Math.round(moistureDeficit * 0.4 * 10) / 10;
      recommendation = `Sensor data indicates: Apply exactly ${precisAmount}mm via drip irrigation. Zone-specific application recommended.`;
      recommendationAr = `بيانات المستشعرات تشير: طبّق بالضبط ${precisAmount} مم عبر الري بالتنقيط. يُوصى بالتطبيق حسب المنطقة.`;
      confidence = 0.90;
    } else if (moistureDeficit > 5) {
      recommendation = `Mild deficit detected. Schedule irrigation for tomorrow morning based on sensor trends.`;
      recommendationAr = `عجز طفيف مكتشف. جدول الري لصباح غد بناءً على اتجاهات المستشعرات.`;
    } else {
      recommendation = `Sensors show adequate moisture. Continue monitoring. NDVI indicates healthy crop.`;
      recommendationAr = `المستشعرات تُظهر رطوبة كافية. استمر في المراقبة. NDVI يشير إلى محصول صحي.`;
    }

    return {
      agentId: agent.id,
      agentName: agent.name,
      agentNameAr: agent.nameAr,
      specialty: agent.specialty,
      specialtyAr: agent.specialtyAr,
      response: `Real-time sensor analysis: Moisture deficit ${moistureDeficit.toFixed(1)}%, Evaporative demand ${evaporativeDemand.toFixed(1)} mm/day.`,
      responseAr: `تحليل المستشعرات الفوري: عجز الرطوبة ${moistureDeficit.toFixed(1)}%، الطلب التبخيري ${evaporativeDemand.toFixed(1)} مم/يوم.`,
      confidence,
      reasoning: [
        `Soil moisture deficit: ${moistureDeficit.toFixed(1)}%`,
        `Evaporative demand: ${evaporativeDemand.toFixed(1)} mm/day`,
        `Sensor network status: Active`,
        `NDVI health index: Normal`,
      ],
      reasoningAr: [
        `عجز رطوبة التربة: ${moistureDeficit.toFixed(1)}%`,
        `الطلب التبخيري: ${evaporativeDemand.toFixed(1)} مم/يوم`,
        `حالة شبكة المستشعرات: نشطة`,
        `مؤشر صحة NDVI: طبيعي`,
      ],
      dataUsed: ['IoT soil sensors', 'Weather station', 'Satellite NDVI', 'Historical trends'],
      recommendation,
      recommendationAr,
    };
  }

  private getEconomicIrrigationPerspective(input: IrrigationQuestion): AgentPerspective {
    const agent = this.agents.get('economic_advisor')!;

    // Economic analysis
    const waterCostPerMm = 0.15; // $/mm/ha
    const potentialYieldLoss = (1 - input.currentSoilMoisture) * 0.1; // 10% max loss
    const cropValue = 500; // $/ha estimated
    const lossValue = potentialYieldLoss * cropValue;
    const irrigationCost = input.weatherForecast.et0 * waterCostPerMm;

    let recommendation = '';
    let recommendationAr = '';
    let confidence = 0.75;

    if (lossValue > irrigationCost * 3) {
      recommendation = `Economically justified: Potential loss ($${lossValue.toFixed(0)}) exceeds irrigation cost ($${irrigationCost.toFixed(0)}). Irrigate now.`;
      recommendationAr = `مبرر اقتصادياً: الخسارة المحتملة (${lossValue.toFixed(0)}$) تتجاوز تكلفة الري (${irrigationCost.toFixed(0)}$). اروِ الآن.`;
      confidence = 0.85;
    } else if (input.weatherForecast.precipitation > 5) {
      recommendation = `Cost-effective: Wait for free rain. Save $${irrigationCost.toFixed(0)} in irrigation costs.`;
      recommendationAr = `فعّال من حيث التكلفة: انتظر المطر المجاني. وفّر ${irrigationCost.toFixed(0)}$ من تكاليف الري.`;
      confidence = 0.80;
    } else {
      recommendation = `Marginal benefit: Monitor closely. Delay irrigation if possible to optimize costs.`;
      recommendationAr = `فائدة هامشية: راقب عن كثب. أخّر الري إن أمكن لتحسين التكاليف.`;
    }

    return {
      agentId: agent.id,
      agentName: agent.name,
      agentNameAr: agent.nameAr,
      specialty: agent.specialty,
      specialtyAr: agent.specialtyAr,
      response: `Economic analysis: Potential yield loss $${lossValue.toFixed(0)}/ha vs irrigation cost $${irrigationCost.toFixed(0)}/ha.`,
      responseAr: `التحليل الاقتصادي: خسارة الإنتاج المحتملة ${lossValue.toFixed(0)}$/هكتار مقابل تكلفة الري ${irrigationCost.toFixed(0)}$/هكتار.`,
      confidence,
      reasoning: [
        `Estimated yield loss value: $${lossValue.toFixed(0)}/ha`,
        `Irrigation cost: $${irrigationCost.toFixed(0)}/ha`,
        `Cost-benefit ratio: ${(lossValue / irrigationCost).toFixed(1)}`,
        `Free rain probability considered`,
      ],
      reasoningAr: [
        `قيمة خسارة الإنتاج المقدرة: ${lossValue.toFixed(0)}$/هكتار`,
        `تكلفة الري: ${irrigationCost.toFixed(0)}$/هكتار`,
        `نسبة التكلفة/العائد: ${(lossValue / irrigationCost).toFixed(1)}`,
        `احتمالية المطر المجاني مُراعاة`,
      ],
      dataUsed: ['Water costs', 'Crop market prices', 'Yield response curves', 'Weather probability'],
      recommendation,
      recommendationAr,
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Pest/Disease Council - مجلس الآفات والأمراض
  // ─────────────────────────────────────────────────────────────────────────────

  consultPestCouncil(input: PestQuestion): CouncilSession {
    const sessionId = `PEST-${Date.now()}`;
    const perspectives: AgentPerspective[] = [];

    // Generate perspectives from each agent for pest/disease
    perspectives.push(this.getFAOPestPerspective(input));
    perspectives.push(this.getCropModelPestPerspective(input));
    perspectives.push(this.getLocalWisdomPestPerspective(input));
    perspectives.push(this.getPrecisionAgPestPerspective(input));
    perspectives.push(this.getEconomicPestPerspective(input));

    const consensus = this.buildConsensus(perspectives, 'pest');

    return {
      sessionId,
      question: `Pest/disease diagnosis for ${input.cropType} with symptoms: ${input.symptoms.join(', ')}`,
      questionAr: `تشخيص الآفة/المرض لـ ${input.cropType} مع أعراض: ${input.symptoms.join('، ')}`,
      category: 'pest',
      timestamp: new Date().toISOString(),
      perspectives,
      consensus,
      summary: this.generateSummary(perspectives, consensus),
      summaryAr: this.generateSummaryAr(perspectives, consensus),
    };
  }

  private getFAOPestPerspective(input: PestQuestion): AgentPerspective {
    const agent = this.agents.get('fao_expert')!;

    // Simple symptom matching (in production, this would use ML models)
    const hasYellowLeaves = input.symptoms.some(s => s.toLowerCase().includes('yellow'));
    const hasSpots = input.symptoms.some(s => s.toLowerCase().includes('spot'));
    const hasWilting = input.symptoms.some(s => s.toLowerCase().includes('wilt'));

    let diagnosis = 'General stress';
    let diagnosisAr = 'إجهاد عام';
    let treatment = 'Monitor and maintain proper irrigation';
    let treatmentAr = 'راقب وحافظ على الري المناسب';

    if (hasYellowLeaves && input.humidity > 70) {
      diagnosis = 'Possible fungal infection (early blight)';
      diagnosisAr = 'احتمال عدوى فطرية (لفحة مبكرة)';
      treatment = 'Apply copper-based fungicide. Follow IPM guidelines.';
      treatmentAr = 'طبّق مبيد فطري نحاسي. اتبع إرشادات الإدارة المتكاملة للآفات.';
    } else if (hasSpots) {
      diagnosis = 'Leaf spot disease - bacterial or fungal';
      diagnosisAr = 'مرض تبقع الأوراق - بكتيري أو فطري';
      treatment = 'Remove affected leaves. Apply appropriate fungicide/bactericide.';
      treatmentAr = 'أزل الأوراق المصابة. طبّق مبيد فطري/بكتيري مناسب.';
    } else if (hasWilting) {
      diagnosis = 'Possible root disease or water stress';
      diagnosisAr = 'احتمال مرض جذري أو إجهاد مائي';
      treatment = 'Check root health. Adjust irrigation. May need soil treatment.';
      treatmentAr = 'افحص صحة الجذور. اضبط الري. قد يحتاج معالجة التربة.';
    }

    return {
      agentId: agent.id,
      agentName: agent.name,
      agentNameAr: agent.nameAr,
      specialty: agent.specialty,
      specialtyAr: agent.specialtyAr,
      response: `FAO IPM diagnosis: ${diagnosis}`,
      responseAr: `تشخيص الإدارة المتكاملة للآفات (FAO): ${diagnosisAr}`,
      confidence: 0.75,
      reasoning: [
        `Symptoms: ${input.symptoms.join(', ')}`,
        `Temperature: ${input.temperature}°C`,
        `Humidity: ${input.humidity}%`,
        `IPM threshold assessment`,
      ],
      reasoningAr: [
        `الأعراض: ${input.symptoms.join('، ')}`,
        `درجة الحرارة: ${input.temperature}°م`,
        `الرطوبة: ${input.humidity}%`,
        `تقييم عتبة الإدارة المتكاملة للآفات`,
      ],
      dataUsed: ['FAO IPPC guidelines', 'Symptom database', 'Climate conditions'],
      recommendation: treatment,
      recommendationAr: treatmentAr,
    };
  }

  private getCropModelPestPerspective(input: PestQuestion): AgentPerspective {
    const agent = this.agents.get('crop_model')!;
    return {
      agentId: agent.id,
      agentName: agent.name,
      agentNameAr: agent.nameAr,
      specialty: agent.specialty,
      specialtyAr: agent.specialtyAr,
      response: `Disease pressure model indicates moderate risk based on temperature (${input.temperature}°C) and humidity (${input.humidity}%).`,
      responseAr: `نموذج ضغط الأمراض يشير إلى خطر متوسط بناءً على درجة الحرارة (${input.temperature}°م) والرطوبة (${input.humidity}%).`,
      confidence: 0.70,
      reasoning: ['Disease pressure index calculation', 'Environmental conditions', 'Crop susceptibility'],
      reasoningAr: ['حساب مؤشر ضغط الأمراض', 'الظروف البيئية', 'قابلية المحصول للإصابة'],
      dataUsed: ['DSSAT pest module', 'Weather data', 'Disease models'],
      recommendation: 'Monitor closely. Preventive treatment if conditions persist.',
      recommendationAr: 'راقب عن كثب. علاج وقائي إذا استمرت الظروف.',
    };
  }

  private getLocalWisdomPestPerspective(input: PestQuestion): AgentPerspective {
    const agent = this.agents.get('local_wisdom')!;
    return {
      agentId: agent.id,
      agentName: agent.name,
      agentNameAr: agent.nameAr,
      specialty: agent.specialty,
      specialtyAr: agent.specialtyAr,
      response: `Traditional observation: These symptoms are common in ${input.season}. Local farmers use neem-based solutions.`,
      responseAr: `الملاحظة التقليدية: هذه الأعراض شائعة في ${input.season}. المزارعون المحليون يستخدمون محاليل النيم.`,
      confidence: 0.65,
      reasoning: ['Seasonal patterns', 'Traditional treatments', 'Local crop varieties resilience'],
      reasoningAr: ['الأنماط الموسمية', 'العلاجات التقليدية', 'مقاومة الأصناف المحلية'],
      dataUsed: ['Traditional knowledge', 'Local pest calendars', 'Organic treatments'],
      recommendation: 'Try neem oil spray first. Consult local extension officer if persists.',
      recommendationAr: 'جرّب رش زيت النيم أولاً. استشر مسؤول الإرشاد المحلي إذا استمرت.',
    };
  }

  private getPrecisionAgPestPerspective(input: PestQuestion): AgentPerspective {
    const agent = this.agents.get('precision_ag')!;
    return {
      agentId: agent.id,
      agentName: agent.name,
      agentNameAr: agent.nameAr,
      specialty: agent.specialty,
      specialtyAr: agent.specialtyAr,
      response: `Multispectral analysis shows stress patterns. AI image analysis suggests 78% match with fungal infection.`,
      responseAr: `التحليل متعدد الطيف يُظهر أنماط إجهاد. تحليل الصور بالذكاء الاصطناعي يشير إلى تطابق 78% مع عدوى فطرية.`,
      confidence: 0.78,
      reasoning: ['NDVI anomaly detection', 'AI disease classification', 'Thermal imaging'],
      reasoningAr: ['كشف شذوذ NDVI', 'تصنيف الأمراض بالذكاء الاصطناعي', 'التصوير الحراري'],
      dataUsed: ['Drone imagery', 'AI disease models', 'Spectral analysis'],
      recommendation: 'Target affected zones only. Variable-rate application recommended.',
      recommendationAr: 'استهدف المناطق المصابة فقط. يُوصى بالتطبيق المتغير المعدل.',
    };
  }

  private getEconomicPestPerspective(input: PestQuestion): AgentPerspective {
    const agent = this.agents.get('economic_advisor')!;
    return {
      agentId: agent.id,
      agentName: agent.name,
      agentNameAr: agent.nameAr,
      specialty: agent.specialty,
      specialtyAr: agent.specialtyAr,
      response: `Treatment cost-benefit: Early intervention saves ~$200/ha vs late treatment. Action threshold reached.`,
      responseAr: `تكلفة/عائد العلاج: التدخل المبكر يوفر ~200$/هكتار مقارنة بالعلاج المتأخر. تم الوصول لعتبة العمل.`,
      confidence: 0.72,
      reasoning: ['Treatment costs', 'Yield loss estimation', 'Market value impact'],
      reasoningAr: ['تكاليف العلاج', 'تقدير خسارة الإنتاج', 'تأثير القيمة السوقية'],
      dataUsed: ['Treatment prices', 'Yield impact studies', 'Market forecasts'],
      recommendation: 'Treat now. Cost of inaction exceeds treatment cost by 3x.',
      recommendationAr: 'عالج الآن. تكلفة عدم التصرف تتجاوز تكلفة العلاج بـ 3 أضعاف.',
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Consensus Building - بناء التوافق
  // ─────────────────────────────────────────────────────────────────────────────

  private buildConsensus(perspectives: AgentPerspective[], category: string): ConsensusResult {
    // Analyze recommendations for agreement
    const recommendations = perspectives.map(p => p.recommendation.toLowerCase());

    // Simple consensus detection (in production, would use NLP)
    const irrigateVotes = recommendations.filter(r =>
      r.includes('irrigate') && !r.includes('no irrigation') && !r.includes('wait')
    ).length;
    const waitVotes = recommendations.filter(r =>
      r.includes('wait') || r.includes('no irrigation') || r.includes('monitor')
    ).length;

    const totalVotes = perspectives.length;
    const agreeingCount = Math.max(irrigateVotes, waitVotes);

    let consensusLevel: 'full' | 'majority' | 'partial' | 'none';
    let hasConsensus: boolean;

    if (agreeingCount === totalVotes) {
      consensusLevel = 'full';
      hasConsensus = true;
    } else if (agreeingCount >= totalVotes * 0.6) {
      consensusLevel = 'majority';
      hasConsensus = true;
    } else if (agreeingCount >= totalVotes * 0.4) {
      consensusLevel = 'partial';
      hasConsensus = false;
    } else {
      consensusLevel = 'none';
      hasConsensus = false;
    }

    // Weighted average confidence
    const agents = Array.from(this.agents.values());
    let weightedConfidence = 0;
    let totalWeight = 0;

    perspectives.forEach((p, i) => {
      const agent = agents.find(a => a.id === p.agentId);
      const weight = agent?.weight || 0.2;
      weightedConfidence += p.confidence * weight;
      totalWeight += weight;
    });

    // Find dissenting opinions
    const majorityAction = irrigateVotes > waitVotes ? 'irrigate' : 'wait';
    const dissenting = perspectives
      .filter(p => {
        const rec = p.recommendation.toLowerCase();
        if (majorityAction === 'irrigate') {
          return rec.includes('wait') || rec.includes('no irrigation');
        } else {
          return rec.includes('irrigate') && !rec.includes('no irrigation');
        }
      })
      .map(p => `${p.agentName}: ${p.recommendation}`);

    const dissentingAr = perspectives
      .filter(p => {
        const rec = p.recommendation.toLowerCase();
        if (majorityAction === 'irrigate') {
          return rec.includes('wait') || rec.includes('no irrigation');
        } else {
          return rec.includes('irrigate') && !rec.includes('no irrigation');
        }
      })
      .map(p => `${p.agentNameAr}: ${p.recommendationAr}`);

    // Generate final recommendation
    const highestConfidence = perspectives.reduce((max, p) => p.confidence > max.confidence ? p : max, perspectives[0]);

    return {
      hasConsensus,
      consensusLevel,
      finalRecommendation: hasConsensus
        ? highestConfidence.recommendation
        : `Mixed opinions. Primary recommendation: ${highestConfidence.recommendation}`,
      finalRecommendationAr: hasConsensus
        ? highestConfidence.recommendationAr
        : `آراء متباينة. التوصية الرئيسية: ${highestConfidence.recommendationAr}`,
      dissenting,
      dissentingAr,
      confidence: Math.round(weightedConfidence / totalWeight * 100) / 100,
    };
  }

  private generateSummary(perspectives: AgentPerspective[], consensus: ConsensusResult): string {
    const agreeCount = perspectives.length - consensus.dissenting.length;
    return `Council session complete. ${agreeCount}/${perspectives.length} agents agree. ` +
           `Consensus: ${consensus.consensusLevel} (${(consensus.confidence * 100).toFixed(0)}% confidence). ` +
           `Final recommendation: ${consensus.finalRecommendation}`;
  }

  private generateSummaryAr(perspectives: AgentPerspective[], consensus: ConsensusResult): string {
    const agreeCount = perspectives.length - consensus.dissentingAr.length;
    return `اكتملت جلسة المجلس. ${agreeCount}/${perspectives.length} وكلاء متفقون. ` +
           `التوافق: ${consensus.consensusLevel} (ثقة ${(consensus.confidence * 100).toFixed(0)}%). ` +
           `التوصية النهائية: ${consensus.finalRecommendationAr}`;
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Quick Consultation - استشارة سريعة
  // ─────────────────────────────────────────────────────────────────────────────

  quickConsult(question: string, category: 'irrigation' | 'pest' | 'fertilizer' | 'general'): {
    answer: string;
    answerAr: string;
    confidence: number;
    sources: string[];
  } {
    // Simplified quick response
    const responses: { [key: string]: { en: string; ar: string; confidence: number } } = {
      irrigation: {
        en: 'For quick irrigation decisions: Check soil moisture at 10cm depth. If dry, irrigate early morning. Consider weather forecast.',
        ar: 'لقرارات الري السريعة: افحص رطوبة التربة على عمق 10 سم. إذا كانت جافة، اروِ في الصباح الباكر. راعِ توقعات الطقس.',
        confidence: 0.75,
      },
      pest: {
        en: 'For pest identification: Take clear photos of symptoms. Check undersides of leaves. Monitor for 2-3 days if not severe.',
        ar: 'لتحديد الآفات: التقط صوراً واضحة للأعراض. افحص أسفل الأوراق. راقب لمدة 2-3 أيام إذا لم تكن شديدة.',
        confidence: 0.70,
      },
      fertilizer: {
        en: 'For fertilizer guidance: Test soil NPK levels first. Apply based on crop growth stage. Avoid over-fertilization.',
        ar: 'لإرشادات التسميد: اختبر مستويات NPK في التربة أولاً. طبّق حسب مرحلة نمو المحصول. تجنب الإفراط في التسميد.',
        confidence: 0.72,
      },
      general: {
        en: 'For detailed guidance, use the full council consultation with specific parameters for your situation.',
        ar: 'للإرشادات التفصيلية، استخدم الاستشارة الكاملة للمجلس مع معاملات محددة لحالتك.',
        confidence: 0.65,
      },
    };

    const response = responses[category] || responses.general;

    return {
      answer: response.en,
      answerAr: response.ar,
      confidence: response.confidence,
      sources: ['FAO Guidelines', 'Local Best Practices', 'Crop Models'],
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Agents Info - معلومات الوكلاء
  // ─────────────────────────────────────────────────────────────────────────────

  getAgents(): AgentProfile[] {
    return Array.from(this.agents.values());
  }

  getAgentById(id: string): AgentProfile | undefined {
    return this.agents.get(id);
  }
}
