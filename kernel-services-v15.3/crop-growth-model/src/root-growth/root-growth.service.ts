// ═══════════════════════════════════════════════════════════════════════════════
// Root Growth Service - خدمة نمو الجذور
// Based on SimRoot 3D Root Architecture Model (Penn State)
// Reference: https://plantscience.psu.edu/research/labs/roots/methods/computer-analysis-tools/simroot
// ═══════════════════════════════════════════════════════════════════════════════

import { Injectable } from '@nestjs/common';

// ─────────────────────────────────────────────────────────────────────────────
// Root Parameters by Crop Type
// معاملات الجذور حسب نوع المحصول
// ─────────────────────────────────────────────────────────────────────────────

interface RootParams {
  nameAr: string;
  nameEn: string;
  maxRootDepth: number;          // Maximum root depth (cm)
  rootGrowthRate: number;        // Root elongation rate (cm day⁻¹)
  specificRootLength: number;    // Specific root length (m g⁻¹)
  rootDiameter: number;          // Average root diameter (mm)
  branchingAngle: number;        // Branching angle (degrees)
  lateralDensity: number;        // Lateral root density (roots cm⁻¹)
  rootShootRatio: number;        // Root:Shoot biomass ratio
  waterUptakeCoeff: number;      // Water uptake coefficient
  nutrientUptakeKm: {            // Michaelis-Menten Km values (μmol L⁻¹)
    nitrogen: number;
    phosphorus: number;
    potassium: number;
  };
}

const CROP_ROOT_PARAMS: Record<string, RootParams> = {
  WHEAT: {
    nameAr: 'القمح',
    nameEn: 'Wheat',
    maxRootDepth: 150,
    rootGrowthRate: 1.5,
    specificRootLength: 200,
    rootDiameter: 0.3,
    branchingAngle: 60,
    lateralDensity: 8,
    rootShootRatio: 0.25,
    waterUptakeCoeff: 0.04,
    nutrientUptakeKm: { nitrogen: 50, phosphorus: 5, potassium: 20 },
  },
  RICE: {
    nameAr: 'الأرز',
    nameEn: 'Rice',
    maxRootDepth: 60,
    rootGrowthRate: 1.2,
    specificRootLength: 180,
    rootDiameter: 0.35,
    branchingAngle: 45,
    lateralDensity: 10,
    rootShootRatio: 0.20,
    waterUptakeCoeff: 0.06,
    nutrientUptakeKm: { nitrogen: 40, phosphorus: 4, potassium: 15 },
  },
  CORN: {
    nameAr: 'الذرة',
    nameEn: 'Corn/Maize',
    maxRootDepth: 200,
    rootGrowthRate: 2.5,
    specificRootLength: 150,
    rootDiameter: 0.5,
    branchingAngle: 55,
    lateralDensity: 6,
    rootShootRatio: 0.18,
    waterUptakeCoeff: 0.035,
    nutrientUptakeKm: { nitrogen: 60, phosphorus: 6, potassium: 25 },
  },
  SOYBEAN: {
    nameAr: 'فول الصويا',
    nameEn: 'Soybean',
    maxRootDepth: 180,
    rootGrowthRate: 1.8,
    specificRootLength: 250,
    rootDiameter: 0.25,
    branchingAngle: 50,
    lateralDensity: 12,
    rootShootRatio: 0.22,
    waterUptakeCoeff: 0.038,
    nutrientUptakeKm: { nitrogen: 30, phosphorus: 3, potassium: 18 },
  },
  SUGARCANE: {
    nameAr: 'قصب السكر',
    nameEn: 'Sugarcane',
    maxRootDepth: 250,
    rootGrowthRate: 2.0,
    specificRootLength: 120,
    rootDiameter: 0.6,
    branchingAngle: 65,
    lateralDensity: 5,
    rootShootRatio: 0.15,
    waterUptakeCoeff: 0.05,
    nutrientUptakeKm: { nitrogen: 70, phosphorus: 7, potassium: 30 },
  },
  COFFEE: {
    nameAr: 'البن',
    nameEn: 'Coffee',
    maxRootDepth: 300,
    rootGrowthRate: 0.8,
    specificRootLength: 100,
    rootDiameter: 0.8,
    branchingAngle: 70,
    lateralDensity: 4,
    rootShootRatio: 0.30,
    waterUptakeCoeff: 0.03,
    nutrientUptakeKm: { nitrogen: 45, phosphorus: 5, potassium: 22 },
  },
};

// Soil layer structure
interface SoilLayer {
  depth: number;           // Depth from surface (cm)
  thickness: number;       // Layer thickness (cm)
  waterContent: number;    // Volumetric water content (m³ m⁻³)
  fieldCapacity: number;   // Field capacity (m³ m⁻³)
  wiltingPoint: number;    // Wilting point (m³ m⁻³)
  bulkDensity: number;     // Bulk density (g cm⁻³)
  nitrogen: number;        // Available N (kg ha⁻¹)
  phosphorus: number;      // Available P (kg ha⁻¹)
  potassium: number;       // Available K (kg ha⁻¹)
}

@Injectable()
export class RootGrowthService {
  // ─────────────────────────────────────────────────────────────────────────────
  // Calculate Root Depth Over Time
  // حساب عمق الجذور بمرور الوقت
  // ─────────────────────────────────────────────────────────────────────────────

  calculateRootDepth(
    cropType: string,
    daysAfterEmergence: number,
    soilTemperature: number = 20,
    waterStress: number = 1.0,
  ): {
    currentDepth: number;
    maxDepth: number;
    depthProgress: number;
    unit: string;
  } {
    const params = CROP_ROOT_PARAMS[cropType] || CROP_ROOT_PARAMS.WHEAT;

    // Temperature factor (optimal around 20-25°C)
    const tempFactor = this.temperatureResponseFunction(soilTemperature, 10, 25, 35);

    // Daily root growth adjusted for conditions
    const dailyGrowth = params.rootGrowthRate * tempFactor * waterStress;

    // Sigmoid growth pattern
    const k = 0.03; // Growth rate constant
    const midpoint = params.maxRootDepth / (2 * params.rootGrowthRate);
    const sigmoidFactor = 1 / (1 + Math.exp(-k * (daysAfterEmergence - midpoint)));

    // Current depth
    const linearDepth = dailyGrowth * daysAfterEmergence;
    const currentDepth = Math.min(
      params.maxRootDepth,
      linearDepth * sigmoidFactor * 2,
    );

    return {
      currentDepth: Math.round(currentDepth * 10) / 10,
      maxDepth: params.maxRootDepth,
      depthProgress: Math.round((currentDepth / params.maxRootDepth) * 100),
      unit: 'cm',
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Calculate Root Length Density Profile
  // حساب توزيع كثافة طول الجذور
  // ─────────────────────────────────────────────────────────────────────────────

  calculateRootLengthDensity(
    cropType: string,
    rootBiomass: number,      // Total root biomass (g m⁻²)
    currentDepth: number,     // Current root depth (cm)
  ): Array<{
    depth: number;
    rld: number;              // Root Length Density (cm cm⁻³)
    relativeRLD: number;
  }> {
    const params = CROP_ROOT_PARAMS[cropType] || CROP_ROOT_PARAMS.WHEAT;

    // Total root length (m m⁻²)
    const totalRootLength = (rootBiomass / 1000) * params.specificRootLength;

    // Root distribution using exponential decay
    const layers: Array<{ depth: number; rld: number; relativeRLD: number }> = [];
    const layerThickness = 10; // cm
    const decayCoeff = 0.03; // Exponential decay coefficient

    let cumulativeRLD = 0;
    for (let depth = 5; depth <= Math.min(currentDepth, params.maxRootDepth); depth += layerThickness) {
      // Exponential decay with depth
      const relativeRLD = Math.exp(-decayCoeff * depth);
      cumulativeRLD += relativeRLD;
    }

    for (let depth = 5; depth <= Math.min(currentDepth, params.maxRootDepth); depth += layerThickness) {
      const relativeRLD = Math.exp(-decayCoeff * depth);
      // RLD in cm cm⁻³ (convert from m m⁻²)
      const rld = (totalRootLength * 100 * (relativeRLD / cumulativeRLD)) /
        (layerThickness * 10000);

      layers.push({
        depth,
        rld: Math.round(rld * 1000) / 1000,
        relativeRLD: Math.round(relativeRLD * 100) / 100,
      });
    }

    return layers;
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Calculate Water Uptake by Roots
  // حساب امتصاص الماء بواسطة الجذور
  // Based on Feddes model
  // ─────────────────────────────────────────────────────────────────────────────

  calculateWaterUptake(
    cropType: string,
    potentialTranspiration: number,  // Potential transpiration (mm day⁻¹)
    soilLayers: SoilLayer[],
    rootDepth: number,
  ): {
    actualTranspiration: number;
    waterStress: number;
    uptakeByLayer: Array<{ depth: number; uptake: number }>;
    unit: string;
  } {
    const params = CROP_ROOT_PARAMS[cropType] || CROP_ROOT_PARAMS.WHEAT;

    const uptakeByLayer: Array<{ depth: number; uptake: number }> = [];
    let totalUptake = 0;

    // Calculate RLD profile
    const rldProfile = this.calculateRootLengthDensity(cropType, 100, rootDepth);

    soilLayers.forEach((layer) => {
      if (layer.depth > rootDepth) return;

      // Find matching RLD
      const rldLayer = rldProfile.find(r => Math.abs(r.depth - layer.depth) < 5);
      const relativeRLD = rldLayer ? rldLayer.relativeRLD : 0;

      // Water availability factor (0-1)
      const availableWater = (layer.waterContent - layer.wiltingPoint) /
        (layer.fieldCapacity - layer.wiltingPoint);
      const waterFactor = Math.max(0, Math.min(1, availableWater));

      // Layer uptake
      const layerUptake = potentialTranspiration * relativeRLD * waterFactor *
        params.waterUptakeCoeff;

      uptakeByLayer.push({
        depth: layer.depth,
        uptake: Math.round(layerUptake * 100) / 100,
      });

      totalUptake += layerUptake;
    });

    // Normalize to potential transpiration
    const actualTranspiration = Math.min(potentialTranspiration, totalUptake);
    const waterStress = potentialTranspiration > 0 ?
      actualTranspiration / potentialTranspiration : 1;

    return {
      actualTranspiration: Math.round(actualTranspiration * 100) / 100,
      waterStress: Math.round(waterStress * 100) / 100,
      uptakeByLayer,
      unit: 'mm day⁻¹',
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Calculate Nutrient Uptake
  // حساب امتصاص المغذيات
  // Based on Michaelis-Menten kinetics
  // ─────────────────────────────────────────────────────────────────────────────

  calculateNutrientUptake(
    cropType: string,
    rootBiomass: number,           // g m⁻²
    soilNutrientConc: {            // μmol L⁻¹
      nitrogen: number;
      phosphorus: number;
      potassium: number;
    },
    waterUptake: number,           // mm day⁻¹
  ): {
    nitrogen: { uptake: number; limitation: number };
    phosphorus: { uptake: number; limitation: number };
    potassium: { uptake: number; limitation: number };
    unit: string;
  } {
    const params = CROP_ROOT_PARAMS[cropType] || CROP_ROOT_PARAMS.WHEAT;

    // Maximum uptake rate (Vmax) scales with root biomass
    const Vmax = {
      nitrogen: 0.5 * rootBiomass / 100,     // μmol g⁻¹ root h⁻¹
      phosphorus: 0.1 * rootBiomass / 100,
      potassium: 0.3 * rootBiomass / 100,
    };

    // Michaelis-Menten uptake: V = Vmax * [S] / (Km + [S])
    const calculateMM = (
      conc: number,
      km: number,
      vmax: number,
    ): { uptake: number; limitation: number } => {
      const uptake = (vmax * conc) / (km + conc);
      const limitation = conc / (km + conc); // 0-1, 1 = no limitation
      return {
        uptake: Math.round(uptake * 1000) / 1000,
        limitation: Math.round(limitation * 100) / 100,
      };
    };

    return {
      nitrogen: calculateMM(
        soilNutrientConc.nitrogen,
        params.nutrientUptakeKm.nitrogen,
        Vmax.nitrogen,
      ),
      phosphorus: calculateMM(
        soilNutrientConc.phosphorus,
        params.nutrientUptakeKm.phosphorus,
        Vmax.phosphorus,
      ),
      potassium: calculateMM(
        soilNutrientConc.potassium,
        params.nutrientUptakeKm.potassium,
        Vmax.potassium,
      ),
      unit: 'μmol g⁻¹ root h⁻¹',
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Simulate Root Architecture Growth
  // محاكاة نمو بنية الجذور
  // ─────────────────────────────────────────────────────────────────────────────

  simulateRootArchitecture(
    cropType: string,
    daysAfterEmergence: number,
    soilConditions: {
      temperature: number;
      waterStress: number;
      nutrientStress: number;
    },
  ): {
    primaryRoots: number;
    lateralRoots: number;
    totalLength: number;
    rootVolume: number;
    rootSurfaceArea: number;
    architecture: {
      tapRootLength: number;
      lateralSpread: number;
      branchingDensity: number;
    };
  } {
    const params = CROP_ROOT_PARAMS[cropType] || CROP_ROOT_PARAMS.WHEAT;

    // Stress factor
    const stressFactor = Math.min(
      soilConditions.waterStress,
      soilConditions.nutrientStress,
    );

    // Primary root development
    const { currentDepth } = this.calculateRootDepth(
      cropType,
      daysAfterEmergence,
      soilConditions.temperature,
      stressFactor,
    );

    // Number of primary (seminal/nodal) roots
    const primaryRoots = Math.min(
      Math.floor(daysAfterEmergence / 5) + 3,
      cropType === 'CORN' ? 30 : 8,
    );

    // Lateral roots per primary root
    const lateralPerPrimary = params.lateralDensity * currentDepth;
    const lateralRoots = Math.floor(primaryRoots * lateralPerPrimary);

    // Total root length (cm)
    const primaryLength = primaryRoots * currentDepth;
    const avgLateralLength = currentDepth * 0.3;
    const lateralLength = lateralRoots * avgLateralLength;
    const totalLength = primaryLength + lateralLength;

    // Root volume (cm³)
    const radius = params.rootDiameter / 20; // cm
    const rootVolume = Math.PI * radius * radius * totalLength;

    // Root surface area (cm²)
    const rootSurfaceArea = 2 * Math.PI * radius * totalLength;

    // Lateral spread (horizontal extent)
    const lateralSpread = currentDepth * Math.tan(params.branchingAngle * Math.PI / 180);

    return {
      primaryRoots,
      lateralRoots,
      totalLength: Math.round(totalLength),
      rootVolume: Math.round(rootVolume * 10) / 10,
      rootSurfaceArea: Math.round(rootSurfaceArea),
      architecture: {
        tapRootLength: Math.round(currentDepth * 10) / 10,
        lateralSpread: Math.round(lateralSpread * 10) / 10,
        branchingDensity: params.lateralDensity,
      },
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Temperature Response Function
  // ─────────────────────────────────────────────────────────────────────────────

  private temperatureResponseFunction(
    temp: number,
    tmin: number,
    topt: number,
    tmax: number,
  ): number {
    if (temp <= tmin || temp >= tmax) return 0;

    const alpha = Math.log(2) / Math.log((tmax - tmin) / (topt - tmin));
    const response = (2 * Math.pow(temp - tmin, alpha) * Math.pow(topt - tmin, alpha) -
      Math.pow(temp - tmin, 2 * alpha)) / Math.pow(topt - tmin, 2 * alpha);

    return Math.max(0, Math.min(1, response));
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Crop Root Parameters
  // ─────────────────────────────────────────────────────────────────────────────

  getCropParameters(cropType?: string): RootParams | Record<string, RootParams> | null {
    if (cropType) {
      return CROP_ROOT_PARAMS[cropType] || null;
    }
    return CROP_ROOT_PARAMS;
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Available Crops
  // ─────────────────────────────────────────────────────────────────────────────

  getAvailableCrops(): Array<{ id: string; nameEn: string; nameAr: string; maxDepth: number }> {
    return Object.entries(CROP_ROOT_PARAMS).map(([id, params]) => ({
      id,
      nameEn: params.nameEn,
      nameAr: params.nameAr,
      maxDepth: params.maxRootDepth,
    }));
  }
}
