// ═══════════════════════════════════════════════════════════════════════════════
// Irrigation Decision Support Service - خدمة دعم قرارات الري الذكية
// Integrates FAO-56, Threshold Control, and Crop Growth Models
// Based on: IrriPro methodology and FAO Irrigation Guidelines
// ═══════════════════════════════════════════════════════════════════════════════

import { Injectable } from "@nestjs/common";

// ─────────────────────────────────────────────────────────────────────────────
// Interfaces - الواجهات
// ─────────────────────────────────────────────────────────────────────────────

export interface ScenarioInput {
  budget: "high" | "medium" | "low";
  terrain: "plain" | "mountain" | "greenhouse" | "terrace";
  cropType: string;
  cropValue: "high" | "medium" | "low";
  technicalCapability: "advanced" | "basic" | "minimal";
  waterAvailability: "abundant" | "limited" | "scarce";
}

export interface MethodRecommendation {
  primaryMethod: "fao56" | "threshold" | "crop_model" | "hybrid";
  methodNameAr: string;
  methodNameEn: string;
  reasoning: string;
  reasoningAr: string;
  estimatedWaterSaving: number; // percentage
  estimatedYieldIncrease: number; // percentage
  implementationCost: "high" | "medium" | "low";
  technicalRequirements: string[];
  technicalRequirementsAr: string[];
}

export interface ETcCalculationInput {
  cropType: string;
  daysAfterPlanting: number;
  et0: number; // mm/day
  soilType: "sandy" | "loam" | "clay" | "silt";
  stressCoefficient?: number; // Ks (0-1)
  growthStageAdjustment?: boolean;
}

export interface ThresholdControlInput {
  cropType: string;
  soilType: "sandy" | "loam" | "clay" | "silt";
  currentSoilMoisture: number; // volumetric water content (0-1)
  growthStage: "seedling" | "vegetative" | "flowering" | "maturity";
  rootDepth: number; // meters
}

export interface IrrigationRecommendation {
  shouldIrrigate: boolean;
  irrigationAmount: number; // mm
  urgency: "critical" | "recommended" | "optional" | "not_needed";
  reasoning: string;
  reasoningAr: string;
  nextCheckTime: string;
  waterEfficiencyTips: string[];
  waterEfficiencyTipsAr: string[];
}

export interface SmartScheduleInput {
  cropType: string;
  sowingDate: string;
  soilParams: {
    fieldCapacity: number;
    wiltingPoint: number;
    currentMoisture: number;
    soilType: "sandy" | "loam" | "clay" | "silt";
  };
  weatherForecast: Array<{
    date: string;
    et0: number;
    precipitation: number;
    temperature: number;
  }>;
  irrigationSystem: {
    type: "drip" | "sprinkler" | "furrow" | "flood";
    efficiency: number;
  };
  budget: "high" | "medium" | "low";
}

export interface SoilProperties {
  fieldCapacity: number;
  wiltingPoint: number;
  saturation: number;
  hydraulicConductivity: number;
  availableWater: number; // TAW per meter depth
}

export interface CropKcParams {
  Kc_ini: number;
  Kc_mid: number;
  Kc_end: number;
  stageLengths: {
    initial: number;
    development: number;
    mid: number;
    late: number;
  };
  depletionFraction: number; // p - allowable depletion
  rootDepth: { min: number; max: number };
  Ky: number; // yield response factor
}

@Injectable()
export class IrrigationDecisionService {
  // ─────────────────────────────────────────────────────────────────────────────
  // Soil Properties Database - خصائص التربة
  // ─────────────────────────────────────────────────────────────────────────────

  private readonly soilTypes: Map<string, SoilProperties> = new Map([
    [
      "sandy",
      {
        fieldCapacity: 0.12,
        wiltingPoint: 0.04,
        saturation: 0.4,
        hydraulicConductivity: 200, // mm/day
        availableWater: 80, // mm/m
      },
    ],
    [
      "loam",
      {
        fieldCapacity: 0.28,
        wiltingPoint: 0.12,
        saturation: 0.46,
        hydraulicConductivity: 50,
        availableWater: 160,
      },
    ],
    [
      "clay",
      {
        fieldCapacity: 0.38,
        wiltingPoint: 0.22,
        saturation: 0.5,
        hydraulicConductivity: 5,
        availableWater: 160,
      },
    ],
    [
      "silt",
      {
        fieldCapacity: 0.32,
        wiltingPoint: 0.14,
        saturation: 0.48,
        hydraulicConductivity: 30,
        availableWater: 180,
      },
    ],
  ]);

  // ─────────────────────────────────────────────────────────────────────────────
  // Crop Kc Parameters (FAO-56) - معاملات المحاصيل
  // ─────────────────────────────────────────────────────────────────────────────

  private readonly cropParams: Map<string, CropKcParams> = new Map([
    [
      "WHEAT",
      {
        Kc_ini: 0.3,
        Kc_mid: 1.15,
        Kc_end: 0.4,
        stageLengths: { initial: 30, development: 45, mid: 40, late: 30 },
        depletionFraction: 0.55,
        rootDepth: { min: 0.3, max: 1.5 },
        Ky: 1.0,
      },
    ],
    [
      "CORN",
      {
        Kc_ini: 0.3,
        Kc_mid: 1.2,
        Kc_end: 0.6,
        stageLengths: { initial: 25, development: 40, mid: 45, late: 30 },
        depletionFraction: 0.55,
        rootDepth: { min: 0.3, max: 1.7 },
        Ky: 1.25,
      },
    ],
    [
      "RICE",
      {
        Kc_ini: 1.05,
        Kc_mid: 1.2,
        Kc_end: 0.9,
        stageLengths: { initial: 30, development: 30, mid: 60, late: 30 },
        depletionFraction: 0.2,
        rootDepth: { min: 0.2, max: 0.6 },
        Ky: 1.1,
      },
    ],
    [
      "SOYBEAN",
      {
        Kc_ini: 0.4,
        Kc_mid: 1.15,
        Kc_end: 0.5,
        stageLengths: { initial: 20, development: 35, mid: 45, late: 20 },
        depletionFraction: 0.5,
        rootDepth: { min: 0.3, max: 1.3 },
        Ky: 0.85,
      },
    ],
    [
      "COTTON",
      {
        Kc_ini: 0.35,
        Kc_mid: 1.2,
        Kc_end: 0.7,
        stageLengths: { initial: 30, development: 50, mid: 55, late: 45 },
        depletionFraction: 0.65,
        rootDepth: { min: 0.3, max: 1.7 },
        Ky: 0.85,
      },
    ],
    [
      "TOMATO",
      {
        Kc_ini: 0.6,
        Kc_mid: 1.15,
        Kc_end: 0.8,
        stageLengths: { initial: 30, development: 40, mid: 45, late: 30 },
        depletionFraction: 0.4,
        rootDepth: { min: 0.3, max: 1.0 },
        Ky: 1.05,
      },
    ],
    [
      "GRAPE",
      {
        Kc_ini: 0.3,
        Kc_mid: 0.85,
        Kc_end: 0.45,
        stageLengths: { initial: 20, development: 50, mid: 75, late: 60 },
        depletionFraction: 0.45,
        rootDepth: { min: 0.5, max: 2.0 },
        Ky: 0.85,
      },
    ],
    [
      "STRAWBERRY",
      {
        Kc_ini: 0.4,
        Kc_mid: 0.85,
        Kc_end: 0.75,
        stageLengths: { initial: 20, development: 30, mid: 40, late: 20 },
        depletionFraction: 0.25,
        rootDepth: { min: 0.2, max: 0.5 },
        Ky: 1.1,
      },
    ],
    [
      "CUCUMBER",
      {
        Kc_ini: 0.6,
        Kc_mid: 1.0,
        Kc_end: 0.75,
        stageLengths: { initial: 20, development: 30, mid: 40, late: 15 },
        depletionFraction: 0.5,
        rootDepth: { min: 0.3, max: 0.7 },
        Ky: 1.0,
      },
    ],
    [
      "POTATO",
      {
        Kc_ini: 0.5,
        Kc_mid: 1.15,
        Kc_end: 0.75,
        stageLengths: { initial: 25, development: 30, mid: 45, late: 30 },
        depletionFraction: 0.35,
        rootDepth: { min: 0.3, max: 0.6 },
        Ky: 1.1,
      },
    ],
  ]);

  // ─────────────────────────────────────────────────────────────────────────────
  // Irrigation Thresholds by Crop and Growth Stage
  // عتبات الري حسب المحصول ومرحلة النمو
  // ─────────────────────────────────────────────────────────────────────────────

  private readonly irrigationThresholds: Map<
    string,
    { [stage: string]: { start: number; stop: number } }
  > = new Map([
    [
      "WHEAT",
      {
        seedling: { start: 0.5, stop: 0.85 },
        vegetative: { start: 0.55, stop: 0.9 },
        flowering: { start: 0.45, stop: 0.85 },
        maturity: { start: 0.6, stop: 0.85 },
      },
    ],
    [
      "CORN",
      {
        seedling: { start: 0.55, stop: 0.9 },
        vegetative: { start: 0.5, stop: 0.85 },
        flowering: { start: 0.4, stop: 0.8 }, // Critical stage - lower threshold
        maturity: { start: 0.6, stop: 0.85 },
      },
    ],
    [
      "RICE",
      {
        seedling: { start: 0.8, stop: 1.0 }, // Flooded
        vegetative: { start: 0.8, stop: 1.0 },
        flowering: { start: 0.85, stop: 1.0 },
        maturity: { start: 0.7, stop: 0.9 },
      },
    ],
    [
      "TOMATO",
      {
        seedling: { start: 0.5, stop: 0.85 },
        vegetative: { start: 0.45, stop: 0.8 },
        flowering: { start: 0.4, stop: 0.75 }, // Sensitive stage
        maturity: { start: 0.5, stop: 0.8 },
      },
    ],
    [
      "GRAPE",
      {
        seedling: { start: 0.55, stop: 0.85 },
        vegetative: { start: 0.5, stop: 0.8 },
        flowering: { start: 0.55, stop: 0.85 },
        maturity: { start: 0.6, stop: 0.8 }, // Slight stress improves sugar
      },
    ],
    [
      "STRAWBERRY",
      {
        seedling: { start: 0.6, stop: 0.9 },
        vegetative: { start: 0.55, stop: 0.85 },
        flowering: { start: 0.5, stop: 0.8 }, // Very sensitive
        maturity: { start: 0.55, stop: 0.85 },
      },
    ],
  ]);

  // ─────────────────────────────────────────────────────────────────────────────
  // Method Selection - اختيار الطريقة المثلى
  // ─────────────────────────────────────────────────────────────────────────────

  selectOptimalMethod(scenario: ScenarioInput): MethodRecommendation {
    // Decision matrix based on scenario
    let primaryMethod: "fao56" | "threshold" | "crop_model" | "hybrid";
    let estimatedWaterSaving = 0;
    let estimatedYieldIncrease = 0;
    let implementationCost: "high" | "medium" | "low";
    let reasoning = "";
    let reasoningAr = "";
    const technicalRequirements: string[] = [];
    const technicalRequirementsAr: string[] = [];

    // High budget + High value crops + Advanced capability → Crop Model
    if (
      scenario.budget === "high" &&
      scenario.cropValue === "high" &&
      scenario.technicalCapability === "advanced"
    ) {
      primaryMethod = "crop_model";
      estimatedWaterSaving = 35;
      estimatedYieldIncrease = 15;
      implementationCost = "high";
      reasoning =
        "High budget and technical capability support advanced crop model system for maximum precision and yield optimization";
      reasoningAr =
        "الميزانية العالية والقدرة التقنية تدعم نظام نماذج المحاصيل المتقدم لتحقيق أقصى دقة وتحسين الإنتاجية";
      technicalRequirements.push(
        "Weather station",
        "Soil moisture sensors (TDR/capacitance)",
        "Cloud platform",
        "DSSAT/APSIM model calibration",
      );
      technicalRequirementsAr.push(
        "محطة أرصاد جوية",
        "مستشعرات رطوبة التربة",
        "منصة سحابية",
        "معايرة نموذج DSSAT/APSIM",
      );
    }
    // Greenhouse → Crop Model (even with medium budget)
    else if (scenario.terrain === "greenhouse") {
      primaryMethod = "crop_model";
      estimatedWaterSaving = 40;
      estimatedYieldIncrease = 20;
      implementationCost = scenario.budget === "high" ? "high" : "medium";
      reasoning =
        "Greenhouse environment requires precise control; crop models prevent overwatering and disease";
      reasoningAr =
        "بيئة الدفيئة تتطلب تحكماً دقيقاً؛ نماذج المحاصيل تمنع الإفراط في الري والأمراض";
      technicalRequirements.push(
        "Temperature/humidity sensors",
        "Automated valve control",
        "Growth monitoring",
      );
      technicalRequirementsAr.push(
        "مستشعرات درجة الحرارة/الرطوبة",
        "تحكم آلي بالصمامات",
        "مراقبة النمو",
      );
    }
    // Mountain terrain → Threshold Control
    else if (
      scenario.terrain === "mountain" ||
      scenario.terrain === "terrace"
    ) {
      primaryMethod = "threshold";
      estimatedWaterSaving = 25;
      estimatedYieldIncrease = 10;
      implementationCost = "medium";
      reasoning =
        "Complex terrain requires real-time soil moisture response; threshold control handles pressure variations";
      reasoningAr =
        "التضاريس المعقدة تتطلب استجابة فورية لرطوبة التربة؛ التحكم بالعتبة يتعامل مع تقلبات الضغط";
      technicalRequirements.push(
        "Soil moisture sensors per zone",
        "Pressure-compensating emitters",
        "PLC/SCADA controller",
      );
      technicalRequirementsAr.push(
        "مستشعرات رطوبة لكل منطقة",
        "باعثات تعويض الضغط",
        "وحدة تحكم PLC",
      );
    }
    // Medium budget + Plain terrain → Hybrid (FAO-56 + Threshold)
    else if (scenario.budget === "medium" && scenario.terrain === "plain") {
      primaryMethod = "hybrid";
      estimatedWaterSaving = 28;
      estimatedYieldIncrease = 12;
      implementationCost = "medium";
      reasoning =
        "Hybrid approach: FAO-56 for baseline planning + threshold control for real-time execution";
      reasoningAr =
        "النهج المختلط: FAO-56 للتخطيط الأساسي + التحكم بالعتبة للتنفيذ الفوري";
      technicalRequirements.push(
        "Weather data access",
        "Basic soil sensors",
        "Timer-based controller",
      );
      technicalRequirementsAr.push(
        "الوصول لبيانات الطقس",
        "مستشعرات تربة أساسية",
        "وحدة تحكم بالوقت",
      );
    }
    // Low budget or basic capability → FAO-56 with manual threshold
    else if (
      scenario.budget === "low" ||
      scenario.technicalCapability === "minimal"
    ) {
      primaryMethod = "fao56";
      estimatedWaterSaving = 15;
      estimatedYieldIncrease = 5;
      implementationCost = "low";
      reasoning =
        "FAO-56 provides theoretical baseline with minimal infrastructure; manual monitoring sufficient";
      reasoningAr =
        "FAO-56 يوفر الأساس النظري مع الحد الأدنى من البنية التحتية؛ المراقبة اليدوية كافية";
      technicalRequirements.push(
        "Weather data (online/station)",
        "Kc tables",
        "Simple calculation spreadsheet",
      );
      technicalRequirementsAr.push(
        "بيانات الطقس (أونلاين/محطة)",
        "جداول Kc",
        "جدول حسابات بسيط",
      );
    }
    // Default: Threshold control
    else {
      primaryMethod = "threshold";
      estimatedWaterSaving = 30;
      estimatedYieldIncrease = 8;
      implementationCost = "medium";
      reasoning =
        "Threshold control provides good balance of cost and water savings for general scenarios";
      reasoningAr =
        "التحكم بالعتبة يوفر توازناً جيداً بين التكلفة وتوفير المياه للسيناريوهات العامة";
      technicalRequirements.push(
        "Soil moisture sensors",
        "Automatic valve controller",
        "Basic programming",
      );
      technicalRequirementsAr.push(
        "مستشعرات رطوبة التربة",
        "وحدة تحكم آلية بالصمامات",
        "برمجة أساسية",
      );
    }

    // Adjust for water scarcity
    if (scenario.waterAvailability === "scarce") {
      estimatedWaterSaving += 10;
      reasoning += " Water scarcity prioritizes deficit irrigation strategies.";
      reasoningAr += " ندرة المياه تعطي الأولوية لاستراتيجيات الري بالعجز.";
    }

    const methodNames: { [key: string]: { en: string; ar: string } } = {
      fao56: {
        en: "FAO-56 Reference Evapotranspiration",
        ar: "التبخر-نتح المرجعي FAO-56",
      },
      threshold: {
        en: "Soil Moisture Threshold Control",
        ar: "التحكم بعتبة رطوبة التربة",
      },
      crop_model: {
        en: "Crop Growth Model (DSSAT/APSIM)",
        ar: "نموذج نمو المحاصيل (DSSAT/APSIM)",
      },
      hybrid: {
        en: "Hybrid (FAO-56 + Threshold)",
        ar: "مختلط (FAO-56 + عتبة)",
      },
    };

    return {
      primaryMethod,
      methodNameEn: methodNames[primaryMethod].en,
      methodNameAr: methodNames[primaryMethod].ar,
      reasoning,
      reasoningAr,
      estimatedWaterSaving,
      estimatedYieldIncrease,
      implementationCost,
      technicalRequirements,
      technicalRequirementsAr,
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Calculate ETc - حساب التبخر-نتح للمحصول
  // ─────────────────────────────────────────────────────────────────────────────

  calculateETc(input: ETcCalculationInput): {
    etc: number;
    kc: number;
    ks: number;
    growthStage: string;
    adjustedEtc: number;
    dailyWaterNeed: number;
    formula: string;
  } {
    const cropParams = this.cropParams.get(input.cropType.toUpperCase());
    if (!cropParams) {
      throw new Error(`Crop type ${input.cropType} not found`);
    }

    // Determine growth stage and Kc
    const { stage, kc } = this.calculateKcForDay(
      input.daysAfterPlanting,
      cropParams,
    );

    // Soil type adjustment factor
    const soilProps = this.soilTypes.get(input.soilType);
    const soilFactor = soilProps ? soilProps.availableWater / 160 : 1.0; // Normalize to loam

    // Stress coefficient (default 1.0 = no stress)
    const ks = input.stressCoefficient ?? 1.0;

    // Calculate ETc
    const etc = kc * input.et0;
    const adjustedEtc =
      etc * ks * (input.growthStageAdjustment ? soilFactor : 1.0);

    // Convert to daily water need (mm → L/m²)
    const dailyWaterNeed = adjustedEtc; // 1 mm = 1 L/m²

    return {
      etc: Math.round(etc * 100) / 100,
      kc: Math.round(kc * 100) / 100,
      ks,
      growthStage: stage,
      adjustedEtc: Math.round(adjustedEtc * 100) / 100,
      dailyWaterNeed: Math.round(dailyWaterNeed * 100) / 100,
      formula: `ETc = Kc × ET0 = ${kc.toFixed(2)} × ${input.et0} = ${etc.toFixed(2)} mm/day`,
    };
  }

  private calculateKcForDay(
    daysAfterPlanting: number,
    params: CropKcParams,
  ): { stage: string; kc: number } {
    const { initial, development, mid, late } = params.stageLengths;
    const totalDays = initial + development + mid + late;

    if (daysAfterPlanting <= initial) {
      return { stage: "initial", kc: params.Kc_ini };
    } else if (daysAfterPlanting <= initial + development) {
      // Linear interpolation during development
      const progress = (daysAfterPlanting - initial) / development;
      const kc = params.Kc_ini + progress * (params.Kc_mid - params.Kc_ini);
      return { stage: "development", kc };
    } else if (daysAfterPlanting <= initial + development + mid) {
      return { stage: "mid-season", kc: params.Kc_mid };
    } else if (daysAfterPlanting <= totalDays) {
      // Linear interpolation during late season
      const progress = (daysAfterPlanting - initial - development - mid) / late;
      const kc = params.Kc_mid - progress * (params.Kc_mid - params.Kc_end);
      return { stage: "late", kc };
    } else {
      return { stage: "harvest", kc: params.Kc_end };
    }
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Threshold Control Decision - قرار التحكم بالعتبة
  // ─────────────────────────────────────────────────────────────────────────────

  evaluateThresholdControl(
    input: ThresholdControlInput,
  ): IrrigationRecommendation {
    const cropType = input.cropType.toUpperCase();
    const thresholds = this.irrigationThresholds.get(cropType);
    const cropParams = this.cropParams.get(cropType);
    const soilProps = this.soilTypes.get(input.soilType);

    if (!thresholds || !cropParams || !soilProps) {
      // Use default thresholds
      const defaultThreshold = { start: 0.5, stop: 0.85 };
      return this.makeDecision(
        input.currentSoilMoisture,
        defaultThreshold,
        soilProps || this.soilTypes.get("loam")!,
        input.rootDepth,
      );
    }

    const stageThreshold = thresholds[input.growthStage] || {
      start: 0.5,
      stop: 0.85,
    };
    return this.makeDecision(
      input.currentSoilMoisture,
      stageThreshold,
      soilProps,
      input.rootDepth,
    );
  }

  private makeDecision(
    currentMoisture: number,
    threshold: { start: number; stop: number },
    soilProps: SoilProperties,
    rootDepth: number,
  ): IrrigationRecommendation {
    // Calculate relative saturation
    const relativeSaturation =
      (currentMoisture - soilProps.wiltingPoint) /
      (soilProps.fieldCapacity - soilProps.wiltingPoint);

    // Calculate irrigation amount needed
    const targetMoisture =
      threshold.stop * (soilProps.fieldCapacity - soilProps.wiltingPoint) +
      soilProps.wiltingPoint;
    const deficit = Math.max(0, targetMoisture - currentMoisture);
    const irrigationAmount = deficit * rootDepth * 1000; // Convert to mm

    let shouldIrrigate = false;
    let urgency: "critical" | "recommended" | "optional" | "not_needed" =
      "not_needed";
    let reasoning = "";
    let reasoningAr = "";
    const waterEfficiencyTips: string[] = [];
    const waterEfficiencyTipsAr: string[] = [];

    if (relativeSaturation <= 0.3) {
      shouldIrrigate = true;
      urgency = "critical";
      reasoning =
        "Soil moisture critically low - immediate irrigation required to prevent crop damage";
      reasoningAr =
        "رطوبة التربة منخفضة بشكل حرج - الري الفوري مطلوب لمنع تلف المحصول";
    } else if (relativeSaturation <= threshold.start) {
      shouldIrrigate = true;
      urgency = "recommended";
      reasoning =
        "Soil moisture below threshold - irrigation recommended within 24 hours";
      reasoningAr = "رطوبة التربة أقل من العتبة - يُوصى بالري خلال 24 ساعة";
    } else if (relativeSaturation <= threshold.start + 0.1) {
      shouldIrrigate = false;
      urgency = "optional";
      reasoning = "Soil moisture approaching threshold - monitor closely";
      reasoningAr = "رطوبة التربة تقترب من العتبة - يجب المراقبة عن كثب";
    } else {
      shouldIrrigate = false;
      urgency = "not_needed";
      reasoning = "Soil moisture adequate - no irrigation needed";
      reasoningAr = "رطوبة التربة كافية - لا حاجة للري";
    }

    // Add tips
    if (shouldIrrigate) {
      waterEfficiencyTips.push(
        "Irrigate during early morning or late evening to reduce evaporation",
      );
      waterEfficiencyTipsAr.push(
        "الري في الصباح الباكر أو المساء المتأخر لتقليل التبخر",
      );

      if (irrigationAmount > 30) {
        waterEfficiencyTips.push(
          "Consider split irrigation to improve infiltration",
        );
        waterEfficiencyTipsAr.push("فكر في تقسيم الري لتحسين التسرب");
      }
    }

    // Calculate next check time
    const hoursUntilCheck =
      urgency === "critical"
        ? 6
        : urgency === "recommended"
          ? 12
          : urgency === "optional"
            ? 24
            : 48;

    return {
      shouldIrrigate,
      irrigationAmount: Math.round(irrigationAmount * 10) / 10,
      urgency,
      reasoning,
      reasoningAr,
      nextCheckTime: `${hoursUntilCheck} hours`,
      waterEfficiencyTips,
      waterEfficiencyTipsAr,
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Smart Irrigation Schedule - جدولة الري الذكي
  // ─────────────────────────────────────────────────────────────────────────────

  generateSmartSchedule(input: SmartScheduleInput): {
    schedule: Array<{
      date: string;
      dayOfSeason: number;
      growthStage: string;
      etc: number;
      precipitation: number;
      netWaterNeed: number;
      irrigationAmount: number;
      soilMoisture: number;
      recommendation: string;
    }>;
    summary: {
      totalIrrigation: number;
      totalPrecipitation: number;
      totalETc: number;
      waterSavings: number;
      irrigationEvents: number;
    };
    method: string;
    methodAr: string;
  } {
    const cropParams = this.cropParams.get(input.cropType.toUpperCase());
    if (!cropParams) {
      throw new Error(`Crop type ${input.cropType} not found`);
    }

    const soilProps = this.soilTypes.get(input.soilParams.soilType);
    if (!soilProps) {
      throw new Error(`Soil type ${input.soilParams.soilType} not found`);
    }

    // Determine method based on budget
    const method =
      input.budget === "high"
        ? "crop_model"
        : input.budget === "medium"
          ? "hybrid"
          : "threshold";

    const schedule: Array<{
      date: string;
      dayOfSeason: number;
      growthStage: string;
      etc: number;
      precipitation: number;
      netWaterNeed: number;
      irrigationAmount: number;
      soilMoisture: number;
      recommendation: string;
    }> = [];

    let currentMoisture = input.soilParams.currentMoisture;
    const sowingDate = new Date(input.sowingDate);
    let totalIrrigation = 0;
    let totalPrecipitation = 0;
    let totalETc = 0;
    let irrigationEvents = 0;

    // Calculate TAW (Total Available Water)
    const rootDepth = (cropParams.rootDepth.min + cropParams.rootDepth.max) / 2;
    const TAW =
      (soilProps.fieldCapacity - soilProps.wiltingPoint) * rootDepth * 1000; // mm
    const RAW = TAW * cropParams.depletionFraction; // Readily Available Water

    for (const forecast of input.weatherForecast) {
      const forecastDate = new Date(forecast.date);
      const dayOfSeason = Math.floor(
        (forecastDate.getTime() - sowingDate.getTime()) / (1000 * 60 * 60 * 24),
      );

      // Get Kc for this day
      const { stage, kc } = this.calculateKcForDay(dayOfSeason, cropParams);

      // Calculate ETc
      const etc = kc * forecast.et0;
      totalETc += etc;

      // Calculate water balance
      const precipitation = forecast.precipitation;
      totalPrecipitation += precipitation;

      // Effective precipitation (only a portion infiltrates)
      const effectivePrecipitation = precipitation * 0.8;

      // Update soil moisture
      currentMoisture =
        currentMoisture +
        effectivePrecipitation / (rootDepth * 1000) -
        etc / (rootDepth * 1000);
      currentMoisture = Math.max(
        soilProps.wiltingPoint,
        Math.min(soilProps.fieldCapacity, currentMoisture),
      );

      // Check if irrigation needed
      const depletion =
        (soilProps.fieldCapacity - currentMoisture) * rootDepth * 1000;
      let irrigationAmount = 0;
      let recommendation = "No irrigation needed";

      if (depletion >= RAW) {
        // Calculate irrigation to bring to field capacity
        irrigationAmount = depletion / input.irrigationSystem.efficiency;
        irrigationAmount = Math.round(irrigationAmount);

        // Update moisture after irrigation
        currentMoisture = soilProps.fieldCapacity;
        totalIrrigation += irrigationAmount;
        irrigationEvents++;
        recommendation = `Irrigate ${irrigationAmount} mm`;
      } else if (depletion >= RAW * 0.8) {
        recommendation = "Monitor - approaching threshold";
      }

      schedule.push({
        date: forecast.date,
        dayOfSeason,
        growthStage: stage,
        etc: Math.round(etc * 10) / 10,
        precipitation: Math.round(precipitation * 10) / 10,
        netWaterNeed: Math.round((etc - effectivePrecipitation) * 10) / 10,
        irrigationAmount,
        soilMoisture: Math.round(currentMoisture * 1000) / 1000,
        recommendation,
      });
    }

    // Calculate theoretical FAO-56 irrigation (no feedback)
    const faoIrrigation = totalETc - totalPrecipitation * 0.8;
    const waterSavings = Math.max(
      0,
      Math.round(((faoIrrigation - totalIrrigation) / faoIrrigation) * 100),
    );

    const methodNames: { [key: string]: { en: string; ar: string } } = {
      crop_model: {
        en: "Crop Growth Model Integration",
        ar: "تكامل نموذج نمو المحاصيل",
      },
      hybrid: { en: "Hybrid FAO-56 + Threshold", ar: "مختلط FAO-56 + عتبة" },
      threshold: { en: "Threshold Control", ar: "التحكم بالعتبة" },
    };

    return {
      schedule,
      summary: {
        totalIrrigation: Math.round(totalIrrigation),
        totalPrecipitation: Math.round(totalPrecipitation),
        totalETc: Math.round(totalETc),
        waterSavings,
        irrigationEvents,
      },
      method: methodNames[method].en,
      methodAr: methodNames[method].ar,
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Compare Methods - مقارنة الطرق
  // ─────────────────────────────────────────────────────────────────────────────

  compareMethods(): {
    comparison: Array<{
      method: string;
      methodAr: string;
      accuracy: number;
      waterSavings: string;
      yieldImpact: string;
      cost: string;
      complexity: string;
      bestFor: string;
      bestForAr: string;
    }>;
    recommendation: string;
    recommendationAr: string;
  } {
    return {
      comparison: [
        {
          method: "FAO-56 ET0",
          methodAr: "FAO-56 التبخر-نتح المرجعي",
          accuracy: 70,
          waterSavings: "15-20%",
          yieldImpact: "+5%",
          cost: "Low (800-2000 CNY)",
          complexity: "Basic",
          bestFor: "Budget-limited farms, initial planning",
          bestForAr: "المزارع محدودة الميزانية، التخطيط الأولي",
        },
        {
          method: "Threshold Control",
          methodAr: "التحكم بالعتبة",
          accuracy: 82,
          waterSavings: "25-30%",
          yieldImpact: "+8-10%",
          cost: "Medium (2000-5000 CNY)",
          complexity: "Moderate",
          bestFor: "General farms, mountain terrain, automation",
          bestForAr: "المزارع العامة، التضاريس الجبلية، الأتمتة",
        },
        {
          method: "Crop Growth Models",
          methodAr: "نماذج نمو المحاصيل",
          accuracy: 92,
          waterSavings: "35-40%",
          yieldImpact: "+15-20%",
          cost: "High (5000-15000 CNY)",
          complexity: "Advanced",
          bestFor: "High-value crops, greenhouses, precision agriculture",
          bestForAr: "المحاصيل عالية القيمة، الدفيئات، الزراعة الدقيقة",
        },
        {
          method: "Hybrid (FAO-56 + Threshold)",
          methodAr: "مختلط (FAO-56 + عتبة)",
          accuracy: 85,
          waterSavings: "28-32%",
          yieldImpact: "+10-12%",
          cost: "Medium (3000-6000 CNY)",
          complexity: "Moderate",
          bestFor: "Large plains, medium budget, balanced approach",
          bestForAr: "السهول الواسعة، الميزانية المتوسطة، النهج المتوازن",
        },
      ],
      recommendation:
        "Progressive adoption recommended: Start with FAO-56 for baseline, add threshold sensors, then integrate crop models as budget allows.",
      recommendationAr:
        "يُوصى بالتبني التدريجي: ابدأ بـ FAO-56 للأساس، أضف مستشعرات العتبة، ثم ادمج نماذج المحاصيل حسب الميزانية.",
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Available Crops - المحاصيل المتاحة
  // ─────────────────────────────────────────────────────────────────────────────

  getAvailableCrops(): string[] {
    return Array.from(this.cropParams.keys());
  }

  getCropParams(cropType: string): CropKcParams | undefined {
    return this.cropParams.get(cropType.toUpperCase());
  }

  getSoilTypes(): string[] {
    return Array.from(this.soilTypes.keys());
  }

  getSoilProperties(soilType: string): SoilProperties | undefined {
    return this.soilTypes.get(soilType);
  }
}
