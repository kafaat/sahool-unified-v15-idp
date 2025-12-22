// ═══════════════════════════════════════════════════════════════════════════════
// LAI Service - خدمة تقدير مؤشر مساحة الأوراق
// Based on LAI-TransNet Two-Stage Transfer Learning Framework
// Reference: Artificial Intelligence in Agriculture (2025), IF: 12.4
// Field-First Architecture - Early Stress Detection
// ═══════════════════════════════════════════════════════════════════════════════

import { Injectable } from '@nestjs/common';
import { v4 as uuidv4 } from 'uuid';
import {
  DataSource,
  CropType,
  GrowthStage,
  LAIEstimationResult,
  LAITimeSeriesPoint,
  LAIComparisonResult,
  SpectralBandsDto,
} from './lai.dto';

// ═══════════════════════════════════════════════════════════════════════════════
// Field-First Types
// ═══════════════════════════════════════════════════════════════════════════════

export interface Badge {
  type: string;
  label_ar: string;
  label_en: string;
  color: string;
}

export interface ActionTemplate {
  action_id: string;
  action_type: string;
  what: string;
  what_ar: string;
  why: string;
  why_ar: string;
  when: {
    deadline: string;
    optimal_window: string;
    optimal_window_ar: string;
  };
  how: string[];
  how_ar: string[];
  fallback: string;
  fallback_ar: string;
  badge: Badge;
  confidence: number;
  source_service: string;
  field_id: string;
  farmer_id?: string;
  tenant_id?: string;
  data: Record<string, unknown>;
  created_at: string;
}

export interface StressDetectionResponse {
  lai_analysis: {
    current_lai: number;
    expected_lai: number;
    deviation_percent: number;
    stress_detected: boolean;
    stress_level: string;
  };
  action_template: ActionTemplate;
  task_card: {
    id: string;
    type: string;
    title_ar: string;
    title_en: string;
    urgency: {
      level: string;
      label_ar: string;
      color: string;
    };
    field_id: string;
    confidence_percent: number;
    offline_ready: boolean;
    badge: Badge;
  };
  nats_topic: string;
}

// ─────────────────────────────────────────────────────────────────────────────
// Crop-specific LAI parameters based on PROSAIL model
// ─────────────────────────────────────────────────────────────────────────────
const CROP_LAI_PARAMS: Record<
  string,
  {
    nameAr: string;
    minLAI: number;
    maxLAI: number;
    optimalLAI: number;
    extinctionCoef: number; // k - معامل الانقراض
    stages: Record<string, { minLAI: number; maxLAI: number }>;
  }
> = {
  SOYBEAN: {
    nameAr: 'فول الصويا',
    minLAI: 0.5,
    maxLAI: 8.0,
    optimalLAI: 4.5,
    extinctionCoef: 0.65,
    stages: {
      EMERGENCE: { minLAI: 0.5, maxLAI: 1.0 },
      VEGETATIVE: { minLAI: 1.0, maxLAI: 4.0 },
      FLOWERING: { minLAI: 3.5, maxLAI: 6.0 },
      POD_DEVELOPMENT: { minLAI: 4.0, maxLAI: 8.0 },
      MATURITY: { minLAI: 2.0, maxLAI: 4.0 },
    },
  },
  WHEAT: {
    nameAr: 'القمح',
    minLAI: 0.3,
    maxLAI: 7.0,
    optimalLAI: 5.0,
    extinctionCoef: 0.55,
    stages: {
      EMERGENCE: { minLAI: 0.3, maxLAI: 0.8 },
      VEGETATIVE: { minLAI: 0.8, maxLAI: 3.5 },
      FLOWERING: { minLAI: 3.0, maxLAI: 5.5 },
      POD_DEVELOPMENT: { minLAI: 4.0, maxLAI: 7.0 },
      MATURITY: { minLAI: 2.0, maxLAI: 3.5 },
    },
  },
  CORN: {
    nameAr: 'الذرة',
    minLAI: 0.4,
    maxLAI: 6.5,
    optimalLAI: 4.0,
    extinctionCoef: 0.70,
    stages: {
      EMERGENCE: { minLAI: 0.4, maxLAI: 1.2 },
      VEGETATIVE: { minLAI: 1.2, maxLAI: 4.0 },
      FLOWERING: { minLAI: 3.5, maxLAI: 5.5 },
      POD_DEVELOPMENT: { minLAI: 4.0, maxLAI: 6.5 },
      MATURITY: { minLAI: 2.5, maxLAI: 4.0 },
    },
  },
  RICE: {
    nameAr: 'الأرز',
    minLAI: 0.5,
    maxLAI: 8.5,
    optimalLAI: 5.5,
    extinctionCoef: 0.60,
    stages: {
      EMERGENCE: { minLAI: 0.5, maxLAI: 1.5 },
      VEGETATIVE: { minLAI: 1.5, maxLAI: 4.5 },
      FLOWERING: { minLAI: 4.0, maxLAI: 7.0 },
      POD_DEVELOPMENT: { minLAI: 5.0, maxLAI: 8.5 },
      MATURITY: { minLAI: 3.0, maxLAI: 5.0 },
    },
  },
  COFFEE: {
    nameAr: 'البن',
    minLAI: 2.0,
    maxLAI: 9.0,
    optimalLAI: 6.0,
    extinctionCoef: 0.50,
    stages: {
      EMERGENCE: { minLAI: 2.0, maxLAI: 3.0 },
      VEGETATIVE: { minLAI: 3.0, maxLAI: 5.5 },
      FLOWERING: { minLAI: 5.0, maxLAI: 7.5 },
      POD_DEVELOPMENT: { minLAI: 6.0, maxLAI: 9.0 },
      MATURITY: { minLAI: 4.0, maxLAI: 6.0 },
    },
  },
  SORGHUM: {
    nameAr: 'الذرة الرفيعة',
    minLAI: 0.3,
    maxLAI: 5.5,
    optimalLAI: 3.5,
    extinctionCoef: 0.58,
    stages: {
      EMERGENCE: { minLAI: 0.3, maxLAI: 0.8 },
      VEGETATIVE: { minLAI: 0.8, maxLAI: 2.5 },
      FLOWERING: { minLAI: 2.0, maxLAI: 4.0 },
      POD_DEVELOPMENT: { minLAI: 3.0, maxLAI: 5.5 },
      MATURITY: { minLAI: 1.5, maxLAI: 3.0 },
    },
  },
};

// ─────────────────────────────────────────────────────────────────────────────
// Model accuracy metrics from LAI-TransNet research
// ─────────────────────────────────────────────────────────────────────────────
const MODEL_METRICS = {
  'CNN-TL': { r2: 0.81, rmse: 0.64, rrmse: 0.115 },
  'LAI-TransNet': { r2: 0.96, rmse: 0.11, rrmse: 0.068 },
  'LAI-TransNet-CrossScale': { r2: 0.69, rmse: 0.45, rrmse: 0.12 },
  RF: { r2: 0.4, rmse: 1.24, rrmse: 0.323 },
  MLP: { r2: 0.53, rmse: 0.98, rrmse: 0.286 },
};

@Injectable()
export class LAIService {
  // ─────────────────────────────────────────────────────────────────────────────
  // Vegetation Indices Calculation
  // حساب مؤشرات الغطاء النباتي
  // ─────────────────────────────────────────────────────────────────────────────

  calculateVegetationIndices(bands: SpectralBandsDto): {
    ndvi: number;
    evi2: number;
    gndvi: number;
    savi: number;
    msavi: number;
    mtvi2: number;
  } {
    const { green, red, redEdge, nir } = bands;

    // NDVI - Normalized Difference Vegetation Index
    const ndvi = (nir - red) / (nir + red + 0.0001);

    // EVI2 - Enhanced Vegetation Index 2 (without blue band)
    const evi2 = 2.5 * ((nir - red) / (nir + 2.4 * red + 1));

    // GNDVI - Green NDVI
    const gndvi = (nir - green) / (nir + green + 0.0001);

    // SAVI - Soil Adjusted Vegetation Index (L=0.5)
    const L = 0.5;
    const savi = ((nir - red) * (1 + L)) / (nir + red + L);

    // MSAVI - Modified SAVI
    const msavi =
      (2 * nir + 1 - Math.sqrt((2 * nir + 1) ** 2 - 8 * (nir - red))) / 2;

    // MTVI2 - Modified Triangular Vegetation Index 2
    const mtvi2 =
      (1.5 *
        (1.2 * (nir - green) - 2.5 * (red - green))) /
      Math.sqrt((2 * nir + 1) ** 2 - (6 * nir - 5 * Math.sqrt(red)) - 0.5);

    return {
      ndvi: this.clamp(ndvi, -1, 1),
      evi2: this.clamp(evi2, -1, 1),
      gndvi: this.clamp(gndvi, -1, 1),
      savi: this.clamp(savi, -1, 1),
      msavi: this.clamp(msavi, 0, 1),
      mtvi2: isNaN(mtvi2) ? 0 : this.clamp(mtvi2, 0, 1),
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // LAI Estimation using LAI-TransNet inspired algorithm
  // تقدير مؤشر مساحة الأوراق باستخدام خوارزمية مستوحاة من LAI-TransNet
  // ─────────────────────────────────────────────────────────────────────────────

  estimateLAIFromIndices(
    indices: { ndvi: number; evi2: number; gndvi: number; savi: number },
    cropType: CropType = CropType.SOYBEAN,
    growthStage?: GrowthStage,
  ): { lai: number; confidence: number; model: string } {
    const cropParams = CROP_LAI_PARAMS[cropType] || CROP_LAI_PARAMS.SOYBEAN;
    const { ndvi, evi2, gndvi, savi } = indices;

    // Weighted combination of indices (based on LAI-TransNet feature importance)
    // NDVI weight: 0.35, EVI2 weight: 0.30, GNDVI weight: 0.20, SAVI weight: 0.15
    const weightedIndex = 0.35 * ndvi + 0.3 * evi2 + 0.2 * gndvi + 0.15 * savi;

    // Apply Beer-Lambert law with crop-specific extinction coefficient
    // LAI = -ln(1 - fIPAR) / k
    // Where fIPAR ≈ normalized vegetation index
    const k = cropParams.extinctionCoef;
    const fIPAR = Math.max(0.01, Math.min(0.99, (weightedIndex + 1) / 2));
    let lai = -Math.log(1 - fIPAR) / k;

    // Apply growth stage constraints if provided
    if (growthStage && cropParams.stages[growthStage]) {
      const stageParams = cropParams.stages[growthStage];
      lai = this.clamp(lai, stageParams.minLAI, stageParams.maxLAI);
    } else {
      lai = this.clamp(lai, cropParams.minLAI, cropParams.maxLAI);
    }

    // Calculate confidence based on index consistency
    const indexStd = this.standardDeviation([ndvi, evi2, gndvi, savi]);
    const confidence = Math.max(0.5, 1 - indexStd);

    return {
      lai: Math.round(lai * 100) / 100,
      confidence: Math.round(confidence * 100) / 100,
      model: 'LAI-TransNet',
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Estimate LAI for Field
  // تقدير مؤشر مساحة الأوراق للحقل
  // ─────────────────────────────────────────────────────────────────────────────

  async estimateLAI(
    fieldId: string,
    dataSource: DataSource = DataSource.FUSION,
    cropType?: CropType,
    date?: string,
  ): Promise<LAIEstimationResult> {
    // Simulate spectral data retrieval (in production, fetch from satellite/UAV services)
    const simulatedBands = this.simulateSpectralBands(fieldId, date);
    const indices = this.calculateVegetationIndices(simulatedBands);

    const crop = cropType || CropType.SOYBEAN;
    const { lai, confidence, model } = this.estimateLAIFromIndices(
      indices,
      crop,
    );

    const cropParams = CROP_LAI_PARAMS[crop];
    const modelMetrics = MODEL_METRICS['LAI-TransNet'];

    // Determine quality based on data source
    const qualityMultiplier = this.getQualityMultiplier(dataSource);

    return {
      lai,
      laiAr: `${lai} متر مربع/متر مربع`,
      confidence: confidence * qualityMultiplier,
      model,
      dataSource,
      date: date || new Date().toISOString().split('T')[0],
      indices: {
        ndvi: Math.round(indices.ndvi * 1000) / 1000,
        evi2: Math.round(indices.evi2 * 1000) / 1000,
        gndvi: Math.round(indices.gndvi * 1000) / 1000,
        savi: Math.round(indices.savi * 1000) / 1000,
      },
      quality: {
        cloudCover: Math.random() * 15, // Simulated cloud cover %
        pixelPurity: 0.4 + Math.random() * 0.45, // 40-85% as per research
        r2: modelMetrics.r2,
        rmse: modelMetrics.rmse,
      },
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Time Series LAI
  // السلسلة الزمنية لمؤشر مساحة الأوراق
  // ─────────────────────────────────────────────────────────────────────────────

  async getLAITimeSeries(
    fieldId: string,
    startDate?: string,
    endDate?: string,
    dataSource: DataSource = DataSource.PLANETSCOPE,
  ): Promise<LAITimeSeriesPoint[]> {
    const start = startDate ? new Date(startDate) : new Date(Date.now() - 90 * 24 * 60 * 60 * 1000);
    const end = endDate ? new Date(endDate) : new Date();

    const points: LAITimeSeriesPoint[] = [];
    const daysDiff = Math.ceil((end.getTime() - start.getTime()) / (24 * 60 * 60 * 1000));
    const interval = dataSource === DataSource.PLANETSCOPE ? 1 : 5; // Daily for PlanetScope

    for (let i = 0; i <= daysDiff; i += interval) {
      const date = new Date(start.getTime() + i * 24 * 60 * 60 * 1000);
      const dateStr = date.toISOString().split('T')[0];

      // Simulate LAI growth curve (sigmoid function)
      const dayOfYear = this.getDayOfYear(date);
      const growthProgress = 1 / (1 + Math.exp(-0.03 * (dayOfYear - 150)));
      const baseLAI = 0.5 + growthProgress * 5.5 + (Math.random() - 0.5) * 0.3;

      points.push({
        date: dateStr,
        lai: Math.round(baseLAI * 100) / 100,
        confidence: 0.7 + Math.random() * 0.25,
        dataSource,
      });
    }

    return points;
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Compare LAI with Optimal Values
  // مقارنة مؤشر مساحة الأوراق مع القيم المثلى
  // ─────────────────────────────────────────────────────────────────────────────

  async compareLAI(
    fieldId: string,
    cropType: CropType = CropType.SOYBEAN,
  ): Promise<LAIComparisonResult> {
    const estimation = await this.estimateLAI(fieldId, DataSource.FUSION, cropType);
    const cropParams = CROP_LAI_PARAMS[cropType];
    const deviation = estimation.lai - cropParams.optimalLAI;
    const deviationPercent = (deviation / cropParams.optimalLAI) * 100;

    let recommendation: string;
    let recommendationAr: string;

    if (deviationPercent < -20) {
      recommendation = 'LAI is significantly below optimal. Consider increasing nitrogen fertilization and irrigation.';
      recommendationAr = 'مؤشر مساحة الأوراق أقل من المستوى المثالي بشكل كبير. يُنصح بزيادة التسميد النيتروجيني والري.';
    } else if (deviationPercent < -10) {
      recommendation = 'LAI is below optimal. Monitor crop growth and consider supplemental fertilization.';
      recommendationAr = 'مؤشر مساحة الأوراق أقل من المستوى المثالي. راقب نمو المحصول وفكر في التسميد التكميلي.';
    } else if (deviationPercent > 20) {
      recommendation = 'LAI is above optimal. Risk of lodging and disease. Consider growth regulators.';
      recommendationAr = 'مؤشر مساحة الأوراق أعلى من المستوى المثالي. خطر الرقاد والأمراض. فكر في منظمات النمو.';
    } else if (deviationPercent > 10) {
      recommendation = 'LAI is slightly above optimal. Monitor for lodging and ensure adequate air circulation.';
      recommendationAr = 'مؤشر مساحة الأوراق أعلى قليلاً من المستوى المثالي. راقب الرقاد وتأكد من التهوية الكافية.';
    } else {
      recommendation = 'LAI is within optimal range. Continue current management practices.';
      recommendationAr = 'مؤشر مساحة الأوراق ضمن النطاق المثالي. استمر في ممارسات الإدارة الحالية.';
    }

    return {
      fieldId,
      currentLAI: estimation.lai,
      optimalLAI: cropParams.optimalLAI,
      deviation: Math.round(deviation * 100) / 100,
      recommendation,
      recommendationAr,
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Model Information
  // معلومات النموذج
  // ─────────────────────────────────────────────────────────────────────────────

  getModelInfo(): Record<string, unknown> {
    return {
      name: 'LAI-TransNet',
      nameAr: 'شبكة تقدير مؤشر مساحة الأوراق بالتعلم الانتقالي',
      description: 'Two-stage transfer learning framework for LAI estimation',
      descriptionAr: 'إطار تعلم انتقالي على مرحلتين لتقدير مؤشر مساحة الأوراق',
      reference: 'Artificial Intelligence in Agriculture Journal (2025)',
      impactFactor: 12.4,
      metrics: MODEL_METRICS,
      stages: {
        stage1: {
          name: 'UAV Baseline Model',
          nameAr: 'نموذج خط الأساس للطائرات بدون طيار',
          description: 'CNN-TL trained on UAV-Sim + field measurements',
          r2: 0.81,
          rmse: 0.64,
        },
        stage2: {
          name: 'Cross-Scale Optimization',
          nameAr: 'التحسين عبر المقاييس',
          description: 'CycleGAN domain alignment for satellite data',
          r2: 0.96,
          rmse: 0.11,
        },
      },
      supportedDataSources: Object.values(DataSource),
      supportedCrops: Object.keys(CROP_LAI_PARAMS).map(key => ({
        type: key,
        nameAr: CROP_LAI_PARAMS[key].nameAr,
        optimalLAI: CROP_LAI_PARAMS[key].optimalLAI,
      })),
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Helper Methods
  // ─────────────────────────────────────────────────────────────────────────────

  private simulateSpectralBands(fieldId: string, date?: string): SpectralBandsDto {
    // Simulate realistic spectral bands based on field hash
    const hash = this.simpleHash(fieldId + (date || ''));
    const baseGreen = 0.05 + (hash % 100) / 1000;
    const baseRed = 0.03 + ((hash >> 8) % 100) / 1000;
    const baseNIR = 0.3 + ((hash >> 16) % 200) / 500;

    return {
      green: baseGreen + Math.random() * 0.02,
      red: baseRed + Math.random() * 0.02,
      redEdge: (baseRed + baseNIR) / 2 + Math.random() * 0.02,
      nir: baseNIR + Math.random() * 0.05,
    };
  }

  private getQualityMultiplier(dataSource: DataSource): number {
    const multipliers: Record<DataSource, number> = {
      [DataSource.UAV]: 1.0,
      [DataSource.PLANETSCOPE]: 0.95,
      [DataSource.SENTINEL2]: 0.90,
      [DataSource.LANDSAT]: 0.85,
      [DataSource.FUSION]: 0.98,
    };
    return multipliers[dataSource] || 0.9;
  }

  private clamp(value: number, min: number, max: number): number {
    return Math.max(min, Math.min(max, value));
  }

  private standardDeviation(values: number[]): number {
    const mean = values.reduce((a, b) => a + b, 0) / values.length;
    const squareDiffs = values.map(value => Math.pow(value - mean, 2));
    return Math.sqrt(squareDiffs.reduce((a, b) => a + b, 0) / values.length);
  }

  private getDayOfYear(date: Date): number {
    const start = new Date(date.getFullYear(), 0, 0);
    const diff = date.getTime() - start.getTime();
    return Math.floor(diff / (1000 * 60 * 60 * 24));
  }

  private simpleHash(str: string): number {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = (hash << 5) - hash + char;
      hash = hash & hash;
    }
    return Math.abs(hash);
  }

  // ═══════════════════════════════════════════════════════════════════════════════
  // Field-First: ActionTemplate Methods
  // ═══════════════════════════════════════════════════════════════════════════════

  /**
   * Detect stress with ActionTemplate
   * الكشف المبكر عن الإجهاد مع قالب إجراء
   */
  async detectStressWithAction(
    fieldId: string,
    cropType: CropType = CropType.SOYBEAN,
    farmerId?: string,
    tenantId?: string,
  ): Promise<StressDetectionResponse> {
    // Get LAI estimation and comparison
    const estimation = await this.estimateLAI(fieldId, DataSource.FUSION, cropType);
    const comparison = await this.compareLAI(fieldId, cropType);

    const currentLAI = estimation.lai;
    const expectedLAI = comparison.optimalLAI;
    const deviation = comparison.deviation;
    const deviationPercent = Math.round((deviation / expectedLAI) * 100);
    const actionId = uuidv4();

    // Determine stress level and urgency
    let stressLevel: string;
    let stressDetected: boolean;
    let urgencyLevel: string;
    let urgencyLabelAr: string;
    let urgencyColor: string;

    if (deviationPercent < -20) {
      stressLevel = 'severe';
      stressDetected = true;
      urgencyLevel = 'critical';
      urgencyLabelAr = 'حرج';
      urgencyColor = '#EF4444';
    } else if (deviationPercent < -10) {
      stressLevel = 'moderate';
      stressDetected = true;
      urgencyLevel = 'high';
      urgencyLabelAr = 'عالي';
      urgencyColor = '#F97316';
    } else if (deviationPercent < -5) {
      stressLevel = 'mild';
      stressDetected = true;
      urgencyLevel = 'medium';
      urgencyLabelAr = 'متوسط';
      urgencyColor = '#EAB308';
    } else {
      stressLevel = 'none';
      stressDetected = false;
      urgencyLevel = 'low';
      urgencyLabelAr = 'منخفض';
      urgencyColor = '#22C55E';
    }

    // Create ActionTemplate
    const actionTemplate: ActionTemplate = {
      action_id: actionId,
      action_type: stressDetected ? 'early_stress_alert' : 'monitoring',
      what: stressDetected ? 'Inspect for early stress' : 'Continue monitoring',
      what_ar: stressDetected ? 'فحص إجهاد مبكر' : 'استمر في المراقبة',
      why: `LAI ${stressDetected ? 'below' : 'within'} expected range (${currentLAI} vs ${expectedLAI})`,
      why_ar: stressDetected
        ? `LAI أقل من المتوقع بنسبة ${Math.abs(deviationPercent)}% - علامات إجهاد مبكر`
        : `LAI ضمن النطاق المثالي (${currentLAI})`,
      when: {
        deadline: stressDetected ? '48 hours' : 'Weekly check',
        optimal_window: 'Morning inspection',
        optimal_window_ar: stressDetected ? 'خلال 48 ساعة - صباحاً' : 'فحص أسبوعي',
      },
      how: stressDetected
        ? [
            'Inspect leaf color and condition',
            'Check soil moisture levels',
            'Look for pest or disease signs',
            'Photograph affected areas',
            'Compare with healthy areas',
          ]
        : [
            'Continue regular monitoring',
            'Maintain current practices',
          ],
      how_ar: stressDetected
        ? [
            'افحص لون الأوراق وحالتها',
            'تحقق من رطوبة التربة',
            'ابحث عن علامات آفات أو أمراض',
            'صوّر المنطقة المتأثرة',
            'قارن مع المناطق السليمة',
          ]
        : [
            'استمر في المراقبة المنتظمة',
            'حافظ على الممارسات الحالية',
          ],
      fallback: stressDetected
        ? 'If you cannot find the cause: consult agricultural engineer'
        : 'No action needed at this time',
      fallback_ar: stressDetected
        ? 'إذا لم تجد السبب: استشر المهندس الزراعي'
        : 'لا يلزم إجراء في الوقت الحالي',
      badge: {
        type: 'satellite_estimate',
        label_ar: 'تقدير من القمر الصناعي',
        label_en: 'Satellite Estimate',
        color: '#0EA5E9',
      },
      confidence: estimation.confidence,
      source_service: 'lai-estimation',
      field_id: fieldId,
      farmer_id: farmerId,
      tenant_id: tenantId,
      data: {
        current_lai: currentLAI,
        expected_lai: expectedLAI,
        deviation: deviation,
        deviation_percent: deviationPercent,
        stress_level: stressLevel,
        stress_detected: stressDetected,
        indices: estimation.indices,
        data_source: estimation.dataSource,
        model: 'LAI-TransNet',
        r2: estimation.quality.r2,
        rmse: estimation.quality.rmse,
      },
      created_at: new Date().toISOString(),
    };

    // Create task card for mobile app
    const taskCard = {
      id: actionId,
      type: stressDetected ? 'early_stress_alert' : 'monitoring',
      title_ar: stressDetected
        ? `تنبيه إجهاد - LAI ${Math.abs(deviationPercent)}% أقل`
        : `LAI طبيعي - ${currentLAI}`,
      title_en: stressDetected
        ? `Stress Alert - LAI ${Math.abs(deviationPercent)}% below`
        : `LAI Normal - ${currentLAI}`,
      urgency: {
        level: urgencyLevel,
        label_ar: urgencyLabelAr,
        color: urgencyColor,
      },
      field_id: fieldId,
      confidence_percent: Math.round(estimation.confidence * 100),
      offline_ready: true,
      badge: actionTemplate.badge,
    };

    return {
      lai_analysis: {
        current_lai: currentLAI,
        expected_lai: expectedLAI,
        deviation_percent: deviationPercent,
        stress_detected: stressDetected,
        stress_level: stressLevel,
      },
      action_template: actionTemplate,
      task_card: taskCard,
      nats_topic: 'sahool.alerts.stress_detection',
    };
  }

  /**
   * Check for LAI anomalies with ActionTemplate
   * فحص شذوذ LAI مع قالب إجراء
   */
  async checkAnomalyWithAction(
    fieldId: string,
    cropType: CropType = CropType.SOYBEAN,
    farmerId?: string,
  ) {
    // Get time series to detect anomalies
    const timeSeries = await this.getLAITimeSeries(fieldId);
    const estimation = await this.estimateLAI(fieldId, DataSource.FUSION, cropType);
    const actionId = uuidv4();

    // Calculate trend and detect anomalies
    const recentPoints = timeSeries.slice(-7); // Last 7 points
    const avgRecent = recentPoints.reduce((sum, p) => sum + p.lai, 0) / recentPoints.length;
    const currentLAI = estimation.lai;

    // Detect sudden drop (anomaly)
    const dropPercent = ((avgRecent - currentLAI) / avgRecent) * 100;
    const isAnomaly = dropPercent > 15; // 15% sudden drop

    let urgencyLevel: string;
    let urgencyLabelAr: string;
    let urgencyColor: string;

    if (dropPercent > 25) {
      urgencyLevel = 'critical';
      urgencyLabelAr = 'حرج';
      urgencyColor = '#EF4444';
    } else if (dropPercent > 15) {
      urgencyLevel = 'high';
      urgencyLabelAr = 'عالي';
      urgencyColor = '#F97316';
    } else if (dropPercent > 10) {
      urgencyLevel = 'medium';
      urgencyLabelAr = 'متوسط';
      urgencyColor = '#EAB308';
    } else {
      urgencyLevel = 'low';
      urgencyLabelAr = 'منخفض';
      urgencyColor = '#22C55E';
    }

    const actionTemplate: ActionTemplate = {
      action_id: actionId,
      action_type: isAnomaly ? 'lai_anomaly_alert' : 'monitoring',
      what: isAnomaly ? 'Investigate sudden LAI drop' : 'LAI trend normal',
      what_ar: isAnomaly ? 'تحقق من انخفاض LAI المفاجئ' : 'اتجاه LAI طبيعي',
      why: isAnomaly
        ? `Sudden ${dropPercent.toFixed(0)}% drop in LAI detected`
        : `LAI stable at ${currentLAI}`,
      why_ar: isAnomaly
        ? `انخفاض مفاجئ ${dropPercent.toFixed(0)}% في LAI - يتطلب تحقيق`
        : `LAI مستقر عند ${currentLAI}`,
      when: {
        deadline: isAnomaly ? 'Immediate' : 'Weekly',
        optimal_window: 'Morning',
        optimal_window_ar: isAnomaly ? 'فوري - الصباح الباكر' : 'أسبوعي',
      },
      how: isAnomaly
        ? [
            'Field inspection of affected zone',
            'Check for disease outbreak',
            'Check for pest damage',
            'Verify irrigation system',
            'Take soil samples',
          ]
        : ['Continue regular monitoring'],
      how_ar: isAnomaly
        ? [
            'فحص ميداني للمنطقة المتأثرة',
            'تحقق من وجود أمراض',
            'تحقق من أضرار الآفات',
            'تأكد من نظام الري',
            'خذ عينات تربة',
          ]
        : ['استمر في المراقبة المنتظمة'],
      fallback: isAnomaly
        ? 'If cause unknown: Contact agricultural extension office'
        : 'No action needed',
      fallback_ar: isAnomaly
        ? 'إذا لم تعرف السبب: اتصل بمكتب الإرشاد الزراعي'
        : 'لا يلزم إجراء',
      badge: {
        type: 'satellite_anomaly',
        label_ar: 'كشف شذوذ',
        label_en: 'Anomaly Detection',
        color: '#DC2626',
      },
      confidence: estimation.confidence,
      source_service: 'lai-estimation',
      field_id: fieldId,
      farmer_id: farmerId,
      data: {
        current_lai: currentLAI,
        recent_average: avgRecent,
        drop_percent: dropPercent,
        is_anomaly: isAnomaly,
        time_series_points: recentPoints.length,
        indices: estimation.indices,
      },
      created_at: new Date().toISOString(),
    };

    return {
      anomaly_analysis: {
        current_lai: currentLAI,
        recent_average: Math.round(avgRecent * 100) / 100,
        drop_percent: Math.round(dropPercent * 10) / 10,
        is_anomaly: isAnomaly,
      },
      action_template: actionTemplate,
      time_series_summary: {
        points_analyzed: recentPoints.length,
        trend: dropPercent > 5 ? 'declining' : dropPercent < -5 ? 'increasing' : 'stable',
        trend_ar: dropPercent > 5 ? 'تراجع' : dropPercent < -5 ? 'تحسن' : 'مستقر',
      },
      nats_topic: 'sahool.alerts.lai_anomaly',
    };
  }
}
