// ═══════════════════════════════════════════════════════════════════════════════
// Biomass Service - خدمة الكتلة الحيوية
// Based on Source-Sink-Flow Assimilate Distribution Models (WOFOST/DSSAT)
// ═══════════════════════════════════════════════════════════════════════════════

import { Injectable } from "@nestjs/common";

// ─────────────────────────────────────────────────────────────────────────────
// Partitioning Parameters by Crop and Growth Stage
// معاملات توزيع المادة الجافة حسب المحصول ومرحلة النمو
// ─────────────────────────────────────────────────────────────────────────────

export interface PartitioningCoefficients {
  root: number;
  stem: number;
  leaf: number;
  storage: number; // grain/fruit/tuber
}

export interface CropBiomassParams {
  nameAr: string;
  nameEn: string;
  SLA: number; // Specific Leaf Area (m² kg⁻¹)
  RUE: number; // Radiation Use Efficiency (g MJ⁻¹)
  harvestIndex: number; // Harvest Index (0-1)
  maintenanceRespiration: number; // Maintenance respiration coefficient
  growthRespiration: number; // Growth respiration coefficient
  partitioning: {
    vegetative: PartitioningCoefficients;
    flowering: PartitioningCoefficients;
    grainFilling: PartitioningCoefficients;
    maturity: PartitioningCoefficients;
  };
}

const CROP_BIOMASS: Record<string, CropBiomassParams> = {
  WHEAT: {
    nameAr: "القمح",
    nameEn: "Wheat",
    SLA: 22,
    RUE: 2.8,
    harvestIndex: 0.45,
    maintenanceRespiration: 0.015,
    growthRespiration: 0.25,
    partitioning: {
      vegetative: { root: 0.3, stem: 0.35, leaf: 0.35, storage: 0.0 },
      flowering: { root: 0.1, stem: 0.4, leaf: 0.2, storage: 0.3 },
      grainFilling: { root: 0.05, stem: 0.15, leaf: 0.05, storage: 0.75 },
      maturity: { root: 0.02, stem: 0.08, leaf: 0.0, storage: 0.9 },
    },
  },
  RICE: {
    nameAr: "الأرز",
    nameEn: "Rice",
    SLA: 24,
    RUE: 2.5,
    harvestIndex: 0.5,
    maintenanceRespiration: 0.018,
    growthRespiration: 0.28,
    partitioning: {
      vegetative: { root: 0.25, stem: 0.35, leaf: 0.4, storage: 0.0 },
      flowering: { root: 0.08, stem: 0.35, leaf: 0.22, storage: 0.35 },
      grainFilling: { root: 0.03, stem: 0.12, leaf: 0.05, storage: 0.8 },
      maturity: { root: 0.01, stem: 0.05, leaf: 0.0, storage: 0.94 },
    },
  },
  CORN: {
    nameAr: "الذرة",
    nameEn: "Corn/Maize",
    SLA: 20,
    RUE: 3.8,
    harvestIndex: 0.5,
    maintenanceRespiration: 0.012,
    growthRespiration: 0.22,
    partitioning: {
      vegetative: { root: 0.28, stem: 0.4, leaf: 0.32, storage: 0.0 },
      flowering: { root: 0.12, stem: 0.38, leaf: 0.15, storage: 0.35 },
      grainFilling: { root: 0.04, stem: 0.1, leaf: 0.02, storage: 0.84 },
      maturity: { root: 0.01, stem: 0.05, leaf: 0.0, storage: 0.94 },
    },
  },
  SOYBEAN: {
    nameAr: "فول الصويا",
    nameEn: "Soybean",
    SLA: 26,
    RUE: 2.4,
    harvestIndex: 0.4,
    maintenanceRespiration: 0.02,
    growthRespiration: 0.3,
    partitioning: {
      vegetative: { root: 0.32, stem: 0.3, leaf: 0.38, storage: 0.0 },
      flowering: { root: 0.15, stem: 0.3, leaf: 0.2, storage: 0.35 },
      grainFilling: { root: 0.05, stem: 0.1, leaf: 0.05, storage: 0.8 },
      maturity: { root: 0.02, stem: 0.05, leaf: 0.0, storage: 0.93 },
    },
  },
  SUGARCANE: {
    nameAr: "قصب السكر",
    nameEn: "Sugarcane",
    SLA: 15,
    RUE: 4.2,
    harvestIndex: 0.75,
    maintenanceRespiration: 0.01,
    growthRespiration: 0.2,
    partitioning: {
      vegetative: { root: 0.2, stem: 0.5, leaf: 0.3, storage: 0.0 },
      flowering: { root: 0.08, stem: 0.6, leaf: 0.12, storage: 0.2 },
      grainFilling: { root: 0.03, stem: 0.72, leaf: 0.05, storage: 0.2 },
      maturity: { root: 0.02, stem: 0.83, leaf: 0.0, storage: 0.15 },
    },
  },
  COFFEE: {
    nameAr: "البن",
    nameEn: "Coffee",
    SLA: 18,
    RUE: 2.0,
    harvestIndex: 0.35,
    maintenanceRespiration: 0.016,
    growthRespiration: 0.25,
    partitioning: {
      vegetative: { root: 0.35, stem: 0.35, leaf: 0.3, storage: 0.0 },
      flowering: { root: 0.15, stem: 0.3, leaf: 0.2, storage: 0.35 },
      grainFilling: { root: 0.08, stem: 0.17, leaf: 0.1, storage: 0.65 },
      maturity: { root: 0.05, stem: 0.1, leaf: 0.05, storage: 0.8 },
    },
  },
};

@Injectable()
export class BiomassService {
  // ─────────────────────────────────────────────────────────────────────────────
  // Calculate Daily Biomass Production
  // حساب إنتاج الكتلة الحيوية اليومي
  // ─────────────────────────────────────────────────────────────────────────────

  calculateDailyBiomassProduction(
    par: number, // PAR intercepted (MJ m⁻² day⁻¹)
    fpar: number, // Fraction of PAR intercepted (0-1)
    cropType: string,
    temperature: number,
    existingBiomass?: {
      root: number;
      stem: number;
      leaf: number;
      storage: number;
    },
  ): {
    grossProduction: number;
    maintenanceRespiration: number;
    growthRespiration: number;
    netProduction: number;
    unit: string;
  } {
    const params = CROP_BIOMASS[cropType] || CROP_BIOMASS.WHEAT;

    // Gross production using RUE
    const interceptedPAR = par * fpar;
    const grossProduction = interceptedPAR * params.RUE;

    // Maintenance respiration (depends on existing biomass)
    let maintenanceResp = 0;
    if (existingBiomass) {
      const totalBiomass =
        existingBiomass.root +
        existingBiomass.stem +
        existingBiomass.leaf +
        existingBiomass.storage;
      // Temperature effect on respiration (Q10 = 2)
      const q10Factor = Math.pow(2, (temperature - 25) / 10);
      maintenanceResp =
        totalBiomass * params.maintenanceRespiration * q10Factor;
    }

    // Available for growth
    const availableForGrowth = grossProduction - maintenanceResp;

    // Growth respiration
    const growthResp = availableForGrowth * params.growthRespiration;

    // Net production
    const netProduction = Math.max(0, availableForGrowth - growthResp);

    return {
      grossProduction: Math.round(grossProduction * 100) / 100,
      maintenanceRespiration: Math.round(maintenanceResp * 100) / 100,
      growthRespiration: Math.round(growthResp * 100) / 100,
      netProduction: Math.round(netProduction * 100) / 100,
      unit: "g m⁻² day⁻¹",
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Distribute Assimilates to Organs
  // توزيع المواد المتمثلة على الأعضاء
  // ─────────────────────────────────────────────────────────────────────────────

  distributeAssimilates(
    netProduction: number,
    cropType: string,
    dvs: number, // Development stage (0-2)
  ): {
    toRoot: number;
    toStem: number;
    toLeaf: number;
    toStorage: number;
    growthPhase: string;
    growthPhaseAr: string;
  } {
    const params = CROP_BIOMASS[cropType] || CROP_BIOMASS.WHEAT;

    // Determine growth phase from DVS
    let coefficients: PartitioningCoefficients;
    let phase: string;
    let phaseAr: string;

    if (dvs < 0.7) {
      coefficients = params.partitioning.vegetative;
      phase = "vegetative";
      phaseAr = "النمو الخضري";
    } else if (dvs < 1.0) {
      coefficients = params.partitioning.flowering;
      phase = "flowering";
      phaseAr = "الإزهار";
    } else if (dvs < 1.5) {
      coefficients = params.partitioning.grainFilling;
      phase = "grain_filling";
      phaseAr = "امتلاء الحبوب";
    } else {
      coefficients = params.partitioning.maturity;
      phase = "maturity";
      phaseAr = "النضج";
    }

    return {
      toRoot: Math.round(netProduction * coefficients.root * 100) / 100,
      toStem: Math.round(netProduction * coefficients.stem * 100) / 100,
      toLeaf: Math.round(netProduction * coefficients.leaf * 100) / 100,
      toStorage: Math.round(netProduction * coefficients.storage * 100) / 100,
      growthPhase: phase,
      growthPhaseAr: phaseAr,
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Simulate Biomass Accumulation
  // محاكاة تراكم الكتلة الحيوية
  // ─────────────────────────────────────────────────────────────────────────────

  simulateBiomassAccumulation(
    cropType: string,
    dailyData: Array<{
      date: string;
      par: number;
      fpar: number;
      temperature: number;
      dvs: number;
    }>,
  ): Array<{
    date: string;
    day: number;
    dvs: number;
    grossProduction: number;
    netProduction: number;
    biomass: {
      root: number;
      stem: number;
      leaf: number;
      storage: number;
      total: number;
    };
    lai: number;
    growthPhase: string;
  }> {
    const params = CROP_BIOMASS[cropType] || CROP_BIOMASS.WHEAT;
    const results: Array<{
      date: string;
      day: number;
      dvs: number;
      grossProduction: number;
      netProduction: number;
      biomass: {
        root: number;
        stem: number;
        leaf: number;
        storage: number;
        total: number;
      };
      lai: number;
      growthPhase: string;
    }> = [];

    let biomass = { root: 10, stem: 5, leaf: 5, storage: 0 }; // Initial seedling biomass

    dailyData.forEach((day, index) => {
      // Calculate production
      const production = this.calculateDailyBiomassProduction(
        day.par,
        day.fpar,
        cropType,
        day.temperature,
        biomass,
      );

      // Distribute to organs
      const distribution = this.distributeAssimilates(
        production.netProduction,
        cropType,
        day.dvs,
      );

      // Update biomass pools
      biomass.root += distribution.toRoot;
      biomass.stem += distribution.toStem;
      biomass.leaf += distribution.toLeaf;
      biomass.storage += distribution.toStorage;

      // Calculate LAI from leaf biomass
      const lai = (biomass.leaf / 1000) * params.SLA;

      const total =
        biomass.root + biomass.stem + biomass.leaf + biomass.storage;

      results.push({
        date: day.date,
        day: index + 1,
        dvs: day.dvs,
        grossProduction: production.grossProduction,
        netProduction: production.netProduction,
        biomass: {
          root: Math.round(biomass.root),
          stem: Math.round(biomass.stem),
          leaf: Math.round(biomass.leaf),
          storage: Math.round(biomass.storage),
          total: Math.round(total),
        },
        lai: Math.round(lai * 100) / 100,
        growthPhase: distribution.growthPhase,
      });
    });

    return results;
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Calculate Yield
  // حساب الغلة
  // ─────────────────────────────────────────────────────────────────────────────

  calculateYield(
    totalAbovegroundBiomass: number,
    cropType: string,
    moistureContent: number = 0.14,
  ): {
    grainYield: number;
    harvestIndex: number;
    dryYield: number;
    freshYield: number;
    unit: string;
  } {
    const params = CROP_BIOMASS[cropType] || CROP_BIOMASS.WHEAT;

    // Grain/Storage yield using harvest index
    const dryYield = totalAbovegroundBiomass * params.harvestIndex;

    // Fresh yield (accounting for moisture)
    const freshYield = dryYield / (1 - moistureContent);

    // Convert from g/m² to kg/ha
    const yieldKgHa = freshYield * 10;

    return {
      grainYield: Math.round(yieldKgHa),
      harvestIndex: params.harvestIndex,
      dryYield: Math.round(dryYield * 10),
      freshYield: Math.round(yieldKgHa),
      unit: "kg ha⁻¹",
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Calculate LAI from Biomass
  // حساب مؤشر مساحة الأوراق من الكتلة الحيوية
  // ─────────────────────────────────────────────────────────────────────────────

  calculateLAI(
    leafBiomass: number, // g m⁻²
    cropType: string,
  ): {
    lai: number;
    sla: number;
    description: string;
  } {
    const params = CROP_BIOMASS[cropType] || CROP_BIOMASS.WHEAT;

    // LAI = (Leaf biomass / 1000) × SLA
    // Leaf biomass in g/m², need to convert to kg/m² for SLA (m²/kg)
    const lai = (leafBiomass / 1000) * params.SLA;

    return {
      lai: Math.round(lai * 100) / 100,
      sla: params.SLA,
      description: `LAI calculated using SLA = ${params.SLA} m² kg⁻¹`,
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Partitioning Coefficients
  // الحصول على معاملات التوزيع
  // ─────────────────────────────────────────────────────────────────────────────

  getPartitioningCoefficients(
    cropType: string,
    dvs?: number,
  ): {
    cropType: string;
    phases: Record<string, PartitioningCoefficients>;
    currentPhase?: {
      phase: string;
      coefficients: PartitioningCoefficients;
    };
  } {
    const params = CROP_BIOMASS[cropType] || CROP_BIOMASS.WHEAT;

    const result: {
      cropType: string;
      phases: Record<string, PartitioningCoefficients>;
      currentPhase?: {
        phase: string;
        coefficients: PartitioningCoefficients;
      };
    } = {
      cropType,
      phases: params.partitioning,
    };

    if (dvs !== undefined) {
      let phase: string;
      let coefficients: PartitioningCoefficients;

      if (dvs < 0.7) {
        phase = "vegetative";
        coefficients = params.partitioning.vegetative;
      } else if (dvs < 1.0) {
        phase = "flowering";
        coefficients = params.partitioning.flowering;
      } else if (dvs < 1.5) {
        phase = "grainFilling";
        coefficients = params.partitioning.grainFilling;
      } else {
        phase = "maturity";
        coefficients = params.partitioning.maturity;
      }

      result.currentPhase = { phase, coefficients };
    }

    return result;
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Crop Biomass Parameters
  // الحصول على معاملات الكتلة الحيوية للمحصول
  // ─────────────────────────────────────────────────────────────────────────────

  getCropParameters(
    cropType?: string,
  ): CropBiomassParams | Record<string, CropBiomassParams> | null {
    if (cropType) {
      return CROP_BIOMASS[cropType] || null;
    }
    return CROP_BIOMASS;
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Available Crops
  // الحصول على المحاصيل المتاحة
  // ─────────────────────────────────────────────────────────────────────────────

  getAvailableCrops(): Array<{
    id: string;
    nameEn: string;
    nameAr: string;
    harvestIndex: number;
  }> {
    return Object.entries(CROP_BIOMASS).map(([id, params]) => ({
      id,
      nameEn: params.nameEn,
      nameAr: params.nameAr,
      harvestIndex: params.harvestIndex,
    }));
  }
}
