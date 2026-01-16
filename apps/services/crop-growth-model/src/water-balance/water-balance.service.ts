// ═══════════════════════════════════════════════════════════════════════════════
// Water Balance Service - خدمة توازن المياه
// Integrated Soil-Crop-Atmosphere Water Balance Model
// Based on FAO-56 and SWAP model concepts
// ═══════════════════════════════════════════════════════════════════════════════

import { Injectable } from "@nestjs/common";

// ─────────────────────────────────────────────────────────────────────────────
// Crop Coefficients (Kc) - FAO-56
// معاملات المحصول - منظمة الفاو 56
// ─────────────────────────────────────────────────────────────────────────────

export interface CropWaterParams {
  nameAr: string;
  nameEn: string;
  Kc_ini: number; // Initial stage Kc
  Kc_mid: number; // Mid-season Kc
  Kc_end: number; // Late season Kc
  stageLengths: {
    // Days for each stage
    initial: number;
    development: number;
    mid: number;
    late: number;
  };
  rootingDepth: {
    // Rooting depth (m)
    min: number;
    max: number;
  };
  depletionFraction: number; // Allowable depletion fraction (p)
  yieldResponseFactor: number; // Ky - yield response to water
}

const CROP_WATER_PARAMS: Record<string, CropWaterParams> = {
  WHEAT: {
    nameAr: "القمح",
    nameEn: "Wheat",
    Kc_ini: 0.3,
    Kc_mid: 1.15,
    Kc_end: 0.25,
    stageLengths: { initial: 30, development: 40, mid: 50, late: 30 },
    rootingDepth: { min: 0.3, max: 1.5 },
    depletionFraction: 0.55,
    yieldResponseFactor: 1.0,
  },
  RICE: {
    nameAr: "الأرز",
    nameEn: "Rice",
    Kc_ini: 1.05,
    Kc_mid: 1.2,
    Kc_end: 0.9,
    stageLengths: { initial: 30, development: 30, mid: 60, late: 30 },
    rootingDepth: { min: 0.2, max: 0.6 },
    depletionFraction: 0.2,
    yieldResponseFactor: 1.1,
  },
  CORN: {
    nameAr: "الذرة",
    nameEn: "Corn/Maize",
    Kc_ini: 0.3,
    Kc_mid: 1.2,
    Kc_end: 0.35,
    stageLengths: { initial: 25, development: 40, mid: 45, late: 30 },
    rootingDepth: { min: 0.3, max: 2.0 },
    depletionFraction: 0.55,
    yieldResponseFactor: 1.25,
  },
  SOYBEAN: {
    nameAr: "فول الصويا",
    nameEn: "Soybean",
    Kc_ini: 0.4,
    Kc_mid: 1.15,
    Kc_end: 0.5,
    stageLengths: { initial: 20, development: 35, mid: 45, late: 25 },
    rootingDepth: { min: 0.3, max: 1.8 },
    depletionFraction: 0.5,
    yieldResponseFactor: 0.85,
  },
  SUGARCANE: {
    nameAr: "قصب السكر",
    nameEn: "Sugarcane",
    Kc_ini: 0.4,
    Kc_mid: 1.25,
    Kc_end: 0.75,
    stageLengths: { initial: 50, development: 70, mid: 180, late: 60 },
    rootingDepth: { min: 0.4, max: 2.5 },
    depletionFraction: 0.65,
    yieldResponseFactor: 1.2,
  },
  COFFEE: {
    nameAr: "البن",
    nameEn: "Coffee",
    Kc_ini: 0.9,
    Kc_mid: 0.95,
    Kc_end: 0.95,
    stageLengths: { initial: 60, development: 90, mid: 120, late: 95 },
    rootingDepth: { min: 0.5, max: 3.0 },
    depletionFraction: 0.4,
    yieldResponseFactor: 0.9,
  },
};

@Injectable()
export class WaterBalanceService {
  // ─────────────────────────────────────────────────────────────────────────────
  // Calculate Crop Coefficient (Kc)
  // حساب معامل المحصول
  // ─────────────────────────────────────────────────────────────────────────────

  calculateKc(
    cropType: string,
    daysAfterPlanting: number,
  ): {
    kc: number;
    stage: string;
    stageAr: string;
    stageProgress: number;
  } {
    const params = CROP_WATER_PARAMS[cropType] || CROP_WATER_PARAMS.WHEAT;
    const { initial, development, mid, late } = params.stageLengths;

    let kc: number;
    let stage: string;
    let stageAr: string;
    let stageProgress: number;

    if (daysAfterPlanting <= initial) {
      // Initial stage
      kc = params.Kc_ini;
      stage = "initial";
      stageAr = "المرحلة الأولية";
      stageProgress = daysAfterPlanting / initial;
    } else if (daysAfterPlanting <= initial + development) {
      // Development stage - linear interpolation
      const dayInStage = daysAfterPlanting - initial;
      const progress = dayInStage / development;
      kc = params.Kc_ini + (params.Kc_mid - params.Kc_ini) * progress;
      stage = "development";
      stageAr = "مرحلة التطور";
      stageProgress = progress;
    } else if (daysAfterPlanting <= initial + development + mid) {
      // Mid-season stage
      const dayInStage = daysAfterPlanting - initial - development;
      kc = params.Kc_mid;
      stage = "mid-season";
      stageAr = "منتصف الموسم";
      stageProgress = dayInStage / mid;
    } else {
      // Late stage - linear decline
      const dayInStage = daysAfterPlanting - initial - development - mid;
      const progress = Math.min(1, dayInStage / late);
      kc = params.Kc_mid - (params.Kc_mid - params.Kc_end) * progress;
      stage = "late";
      stageAr = "المرحلة المتأخرة";
      stageProgress = progress;
    }

    return {
      kc: Math.round(kc * 100) / 100,
      stage,
      stageAr,
      stageProgress: Math.round(stageProgress * 100),
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Calculate Crop Evapotranspiration (ETc)
  // حساب التبخر-نتح للمحصول
  // ─────────────────────────────────────────────────────────────────────────────

  calculateETc(
    cropType: string,
    et0: number, // Reference ET (mm day⁻¹)
    daysAfterPlanting: number,
    waterStress?: number, // Ks (0-1), optional stress coefficient
  ): {
    et0: number;
    kc: number;
    ks: number;
    etc: number;
    etc_adj: number;
    unit: string;
  } {
    const { kc } = this.calculateKc(cropType, daysAfterPlanting);
    const ks = waterStress ?? 1.0;

    // ETc = Kc × ET0
    const etc = kc * et0;

    // Adjusted ETc = Ks × Kc × ET0
    const etc_adj = ks * etc;

    return {
      et0,
      kc,
      ks,
      etc: Math.round(etc * 100) / 100,
      etc_adj: Math.round(etc_adj * 100) / 100,
      unit: "mm day⁻¹",
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Calculate Soil Water Balance
  // حساب توازن مياه التربة
  // ─────────────────────────────────────────────────────────────────────────────

  calculateWaterBalance(
    cropType: string,
    rootingDepth: number, // Current rooting depth (m)
    soilParams: {
      fieldCapacity: number; // FC (m³ m⁻³)
      wiltingPoint: number; // WP (m³ m⁻³)
      currentWaterContent: number; // θ (m³ m⁻³)
    },
    dailyInputs: {
      et0: number; // mm day⁻¹
      precipitation: number; // mm
      irrigation: number; // mm
      daysAfterPlanting: number;
    },
  ): {
    waterBalance: {
      initialStorage: number;
      etc: number;
      precipitation: number;
      irrigation: number;
      runoff: number;
      drainage: number;
      finalStorage: number;
    };
    soilMoisture: {
      depletion: number;
      relativeDepletion: number;
      stressCoefficient: number;
    };
    irrigationNeed: {
      needed: boolean;
      deficit: number;
      recommendation: string;
      recommendationAr: string;
    };
  } {
    const params = CROP_WATER_PARAMS[cropType] || CROP_WATER_PARAMS.WHEAT;

    // Total Available Water (TAW) in root zone
    const TAW =
      1000 *
      (soilParams.fieldCapacity - soilParams.wiltingPoint) *
      rootingDepth;

    // Readily Available Water (RAW)
    const RAW = params.depletionFraction * TAW;

    // Current soil water storage in root zone
    const initialStorage = 1000 * soilParams.currentWaterContent * rootingDepth;

    // Depletion
    const maxStorage = 1000 * soilParams.fieldCapacity * rootingDepth;
    const depletion = maxStorage - initialStorage;

    // Stress coefficient (Ks)
    let ks = 1.0;
    if (depletion > RAW) {
      ks = Math.max(0, (TAW - depletion) / (TAW - RAW));
    }

    // Calculate ETc with stress
    const { etc_adj } = this.calculateETc(
      cropType,
      dailyInputs.et0,
      dailyInputs.daysAfterPlanting,
      ks,
    );

    // Water balance components
    const precipitation = dailyInputs.precipitation;
    const irrigation = dailyInputs.irrigation;

    // Potential storage after additions
    const potentialStorage =
      initialStorage + precipitation + irrigation - etc_adj;

    // Runoff (if exceeds field capacity)
    const runoff = Math.max(0, potentialStorage - maxStorage);

    // Drainage (simplified - excess above FC)
    const drainage = runoff * 0.3; // Simplified drainage fraction

    // Final storage
    const finalStorage = Math.max(
      1000 * soilParams.wiltingPoint * rootingDepth,
      potentialStorage - runoff - drainage,
    );

    // Irrigation recommendation
    const irrigationDeficit = RAW - (maxStorage - finalStorage);
    const needsIrrigation = irrigationDeficit < 0;

    return {
      waterBalance: {
        initialStorage: Math.round(initialStorage * 10) / 10,
        etc: Math.round(etc_adj * 10) / 10,
        precipitation,
        irrigation,
        runoff: Math.round(runoff * 10) / 10,
        drainage: Math.round(drainage * 10) / 10,
        finalStorage: Math.round(finalStorage * 10) / 10,
      },
      soilMoisture: {
        depletion: Math.round(depletion * 10) / 10,
        relativeDepletion: Math.round((depletion / TAW) * 100),
        stressCoefficient: Math.round(ks * 100) / 100,
      },
      irrigationNeed: {
        needed: needsIrrigation,
        deficit: needsIrrigation ? Math.round(Math.abs(irrigationDeficit)) : 0,
        recommendation: needsIrrigation
          ? `Apply ${Math.round(Math.abs(irrigationDeficit))} mm irrigation`
          : "No irrigation needed",
        recommendationAr: needsIrrigation
          ? `قم بالري بكمية ${Math.round(Math.abs(irrigationDeficit))} ملم`
          : "لا حاجة للري",
      },
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Smart Irrigation Scheduling
  // جدولة الري الذكي
  // ─────────────────────────────────────────────────────────────────────────────

  generateIrrigationSchedule(
    cropType: string,
    sowingDate: string,
    weatherForecast: Array<{
      date: string;
      et0: number;
      precipitation: number;
    }>,
    soilParams: {
      fieldCapacity: number;
      wiltingPoint: number;
      initialWaterContent: number;
    },
    irrigationSystem: {
      type: "drip" | "sprinkler" | "furrow" | "flood";
      efficiency: number; // 0-1
      maxDailyApplication: number; // mm
    },
  ): {
    schedule: Array<{
      date: string;
      daysAfterPlanting: number;
      etc: number;
      soilMoisture: number;
      irrigationNeeded: boolean;
      irrigationAmount: number;
      accumulatedDeficit: number;
    }>;
    summary: {
      totalIrrigationEvents: number;
      totalWaterApplied: number;
      avgIntervalDays: number;
      waterUseEfficiency: number;
    };
  } {
    const params = CROP_WATER_PARAMS[cropType] || CROP_WATER_PARAMS.WHEAT;
    const schedule: Array<{
      date: string;
      daysAfterPlanting: number;
      etc: number;
      soilMoisture: number;
      irrigationNeeded: boolean;
      irrigationAmount: number;
      accumulatedDeficit: number;
    }> = [];

    const sowDate = new Date(sowingDate);
    let currentWaterContent = soilParams.initialWaterContent;
    let totalIrrigation = 0;
    let irrigationEvents = 0;
    let accumulatedDeficit = 0;

    // Dynamic rooting depth
    const totalSeasonLength =
      params.stageLengths.initial +
      params.stageLengths.development +
      params.stageLengths.mid +
      params.stageLengths.late;

    weatherForecast.forEach((day, index) => {
      const daysAfterPlanting = index + 1;
      const date = new Date(sowDate);
      date.setDate(date.getDate() + daysAfterPlanting);

      // Dynamic rooting depth
      const rootProgress = Math.min(
        1,
        daysAfterPlanting / (totalSeasonLength * 0.5),
      );
      const rootingDepth =
        params.rootingDepth.min +
        (params.rootingDepth.max - params.rootingDepth.min) * rootProgress;

      // Calculate ETc
      const { etc_adj, ks } = this.calculateETc(
        cropType,
        day.et0,
        daysAfterPlanting,
        1.0, // Will be adjusted below
      );

      // TAW and RAW
      const TAW =
        1000 *
        (soilParams.fieldCapacity - soilParams.wiltingPoint) *
        rootingDepth;
      const RAW = params.depletionFraction * TAW;

      // Update soil moisture
      const storage = 1000 * currentWaterContent * rootingDepth;
      const maxStorage = 1000 * soilParams.fieldCapacity * rootingDepth;
      const depletion = maxStorage - storage;

      // Check if irrigation needed
      const needsIrrigation = depletion > RAW * 0.8; // Irrigate at 80% of RAW
      let irrigationAmount = 0;

      if (needsIrrigation) {
        // Calculate net irrigation need
        const netNeed = depletion - RAW * 0.3; // Refill to 30% of RAW
        // Gross irrigation (accounting for efficiency)
        const grossNeed = netNeed / irrigationSystem.efficiency;
        irrigationAmount = Math.min(
          grossNeed,
          irrigationSystem.maxDailyApplication,
        );
        irrigationEvents++;
        totalIrrigation += irrigationAmount;
      }

      // Water balance
      const netInput = day.precipitation + irrigationAmount - etc_adj;
      currentWaterContent = Math.max(
        soilParams.wiltingPoint,
        Math.min(
          soilParams.fieldCapacity,
          currentWaterContent + netInput / (1000 * rootingDepth),
        ),
      );

      accumulatedDeficit = Math.max(0, accumulatedDeficit - netInput);

      schedule.push({
        date: day.date,
        daysAfterPlanting,
        etc: Math.round(etc_adj * 10) / 10,
        soilMoisture: Math.round(currentWaterContent * 100) / 100,
        irrigationNeeded: needsIrrigation,
        irrigationAmount: Math.round(irrigationAmount),
        accumulatedDeficit: Math.round(accumulatedDeficit),
      });
    });

    // Calculate average irrigation interval
    const irrigationDays = schedule
      .map((s, i) => (s.irrigationNeeded ? i : -1))
      .filter((i) => i >= 0);

    let avgInterval = 0;
    if (irrigationDays.length > 1) {
      const intervals = irrigationDays
        .slice(1)
        .map((day, i) => day - irrigationDays[i]);
      avgInterval = intervals.reduce((a, b) => a + b, 0) / intervals.length;
    }

    // Water use efficiency (kg yield per m³ water)
    // Simplified estimation
    const totalEtc = schedule.reduce((sum, s) => sum + s.etc, 0);
    const wue = totalEtc > 0 ? (totalIrrigation / totalEtc) * 10 : 0;

    return {
      schedule,
      summary: {
        totalIrrigationEvents: irrigationEvents,
        totalWaterApplied: Math.round(totalIrrigation),
        avgIntervalDays: Math.round(avgInterval),
        waterUseEfficiency: Math.round(wue * 100) / 100,
      },
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Calculate Yield Response to Water Stress
  // حساب استجابة الغلة لإجهاد المياه
  // Based on FAO-33 yield response factor (Ky)
  // ─────────────────────────────────────────────────────────────────────────────

  calculateYieldReduction(
    cropType: string,
    relativeETDeficit: number, // (1 - ETa/ETm)
  ): {
    yieldReduction: number;
    potentialYieldPercent: number;
    ky: number;
    description: string;
    descriptionAr: string;
  } {
    const params = CROP_WATER_PARAMS[cropType] || CROP_WATER_PARAMS.WHEAT;
    const ky = params.yieldResponseFactor;

    // Ya/Ym = 1 - Ky × (1 - ETa/ETm)
    const relativeYield = 1 - ky * relativeETDeficit;
    const yieldReduction = (1 - relativeYield) * 100;
    const potentialYieldPercent = relativeYield * 100;

    let description: string;
    let descriptionAr: string;

    if (yieldReduction < 10) {
      description = "Minimal yield impact";
      descriptionAr = "تأثير ضئيل على الغلة";
    } else if (yieldReduction < 25) {
      description = "Moderate yield reduction expected";
      descriptionAr = "انخفاض متوسط متوقع في الغلة";
    } else if (yieldReduction < 50) {
      description = "Significant yield loss likely";
      descriptionAr = "خسارة كبيرة متوقعة في الغلة";
    } else {
      description = "Severe yield reduction - critical water stress";
      descriptionAr = "انخفاض شديد في الغلة - إجهاد مائي حرج";
    }

    return {
      yieldReduction: Math.round(yieldReduction * 10) / 10,
      potentialYieldPercent: Math.round(potentialYieldPercent * 10) / 10,
      ky,
      description,
      descriptionAr,
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Crop Water Parameters
  // ─────────────────────────────────────────────────────────────────────────────

  getCropParameters(
    cropType?: string,
  ): CropWaterParams | Record<string, CropWaterParams> | null {
    if (cropType) {
      return CROP_WATER_PARAMS[cropType] || null;
    }
    return CROP_WATER_PARAMS;
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Available Crops
  // ─────────────────────────────────────────────────────────────────────────────

  getAvailableCrops(): Array<{
    id: string;
    nameEn: string;
    nameAr: string;
    kcMid: number;
  }> {
    return Object.entries(CROP_WATER_PARAMS).map(([id, params]) => ({
      id,
      nameEn: params.nameEn,
      nameAr: params.nameAr,
      kcMid: params.Kc_mid,
    }));
  }
}
