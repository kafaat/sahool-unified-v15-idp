import { Injectable } from '@nestjs/common';

// Planting method types
type PlantingMethodType = 'equal_row' | 'wide_strip' | 'space_broadcasting' | 'small_basin';

// Soil type classification
type SoilType = 'sandy' | 'loamy' | 'clay' | 'silty' | 'saline';

// Climate zone
type ClimateZone = 'arid' | 'semi_arid' | 'mediterranean' | 'continental' | 'tropical';

// Crop type
type CropType = 'wheat' | 'barley' | 'corn' | 'rice' | 'sorghum' | 'date_palm' | 'alfalfa';

// Planting method configuration
export interface PlantingMethod {
  id: PlantingMethodType;
  nameEn: string;
  nameAr: string;
  nameCn: string;
  description: string;
  suitableYieldRange: { min: number; max: number }; // kg/mu
  rowSpacing: { min: number; max: number }; // cm
  seedDepth: { min: number; max: number }; // cm
  seedingRate: { min: number; max: number }; // kg/mu
  advantages: string[];
  disadvantages: string[];
  suitableSoilTypes: SoilType[];
  suitableClimateZones: ClimateZone[];
}

// Optimization request
export interface OptimizationRequest {
  cropType: CropType;
  targetYield: number; // kg/mu
  fieldArea: number; // mu (1 mu = 666.67 m²)
  soilType: SoilType;
  climateZone: ClimateZone;
  availableWater: number; // m³/mu
  soilMoisture?: number; // percentage
  organicMatter?: number; // percentage
  previousCrop?: string;
  plantingDate?: Date;
}

// Optimization result
export interface OptimizationResult {
  recommendedMethod: PlantingMethod;
  alternativeMethods: PlantingMethod[];
  spacingConfiguration: {
    rowSpacing: number;
    plantSpacing: number;
    seedDepth: number;
    seedingRate: number;
    plantsPerMu: number;
  };
  fertilizerRecommendations: {
    baseApplication: { n: number; p: number; k: number }; // kg/mu
    topDressing: { stage: string; n: number; timing: string }[];
    organicMatter: number; // kg/mu
  };
  irrigationSchedule: {
    prePlanting: number; // m³/mu
    emergence: number;
    tillering: number;
    jointing: number;
    heading: number;
    grainfilling: number;
    totalWater: number;
  };
  expectedYield: number;
  confidenceLevel: number;
  warnings: string[];
  recommendations: string[];
}

// Field analysis result
export interface FieldAnalysis {
  soilQualityScore: number;
  waterAvailabilityScore: number;
  climateCompatibilityScore: number;
  overallSuitabilityScore: number;
  limitingFactors: string[];
  improvementSuggestions: string[];
}

// Planting plan
export interface PlantingPlan {
  fieldId: string;
  cropType: CropType;
  method: PlantingMethodType;
  plannedDate: Date;
  tasks: PlantingTask[];
  resourceRequirements: ResourceRequirements;
  timeline: TimelineEvent[];
}

export interface PlantingTask {
  id: string;
  name: string;
  nameAr: string;
  description: string;
  daysBeforePlanting: number;
  duration: number; // hours
  equipment: string[];
  laborRequired: number; // person-hours
}

export interface ResourceRequirements {
  seeds: { quantity: number; unit: string; cost: number };
  fertilizer: { type: string; quantity: number; unit: string; cost: number }[];
  water: { quantity: number; unit: string };
  labor: { hours: number; cost: number };
  machinery: { type: string; hours: number; cost: number }[];
  totalCost: number;
}

export interface TimelineEvent {
  event: string;
  date: Date;
  description: string;
  critical: boolean;
}

// Density calculation result
export interface DensityCalculation {
  method: PlantingMethodType;
  rowSpacing: number; // cm
  plantSpacing: number; // cm
  seedsPerHole: number;
  rowsPerMu: number;
  plantsPerRow: number;
  totalPlantsPerMu: number;
  seedingRateKgPerMu: number;
  coveragePercentage: number;
}

// Yield prediction
export interface YieldPrediction {
  method: PlantingMethodType;
  baseYield: number;
  adjustedYield: number;
  adjustmentFactors: {
    factor: string;
    impact: number; // percentage
    description: string;
  }[];
  confidenceInterval: { lower: number; upper: number };
  riskFactors: string[];
}

@Injectable()
export class PlantingStrategyService {
  // Planting methods database
  private readonly plantingMethods: Map<PlantingMethodType, PlantingMethod> = new Map([
    ['equal_row', {
      id: 'equal_row',
      nameEn: 'Equal Row Broadcasting',
      nameAr: 'البذر المتساوي الصفوف',
      nameCn: '等行条播',
      description: 'Traditional method with equal spacing between all rows, suitable for moderate yield targets',
      suitableYieldRange: { min: 250, max: 350 },
      rowSpacing: { min: 15, max: 20 },
      seedDepth: { min: 3, max: 5 },
      seedingRate: { min: 10, max: 15 },
      advantages: [
        'Simple and easy to implement',
        'Uniform light distribution',
        'Easy mechanical harvesting',
        'Good air circulation',
        'Suitable for most soil types',
      ],
      disadvantages: [
        'Limited yield potential',
        'May waste space in fertile soils',
        'Less efficient water use',
      ],
      suitableSoilTypes: ['loamy', 'clay', 'silty'],
      suitableClimateZones: ['semi_arid', 'mediterranean', 'continental'],
    }],
    ['wide_strip', {
      id: 'wide_strip',
      nameEn: 'Wide Strip Broadcasting',
      nameAr: 'البذر الشريطي العريض',
      nameCn: '宽幅条播',
      description: 'High-density method with wide seeding strips for maximum yield in fertile conditions',
      suitableYieldRange: { min: 350, max: 600 },
      rowSpacing: { min: 20, max: 30 },
      seedDepth: { min: 3, max: 5 },
      seedingRate: { min: 12, max: 18 },
      advantages: [
        'Higher yield potential (15-20% increase)',
        'Better space utilization',
        'Improved competition against weeds',
        'More uniform maturity',
        'Efficient use of fertile soil',
      ],
      disadvantages: [
        'Requires precise equipment',
        'Higher seed cost',
        'May cause lodging in over-fertile conditions',
        'Requires careful water management',
      ],
      suitableSoilTypes: ['loamy', 'silty'],
      suitableClimateZones: ['mediterranean', 'continental'],
    }],
    ['space_broadcasting', {
      id: 'space_broadcasting',
      nameEn: 'Space Broadcasting (Wide-Narrow Row)',
      nameAr: 'البذر المتباعد (صفوف عريضة وضيقة)',
      nameCn: '宽窄行条播',
      description: 'Alternating wide and narrow rows for optimal light capture and ventilation',
      suitableYieldRange: { min: 300, max: 500 },
      rowSpacing: { min: 10, max: 30 },
      seedDepth: { min: 3, max: 5 },
      seedingRate: { min: 11, max: 16 },
      advantages: [
        'Optimal light interception',
        'Excellent ventilation reduces disease',
        'Balanced population density',
        'Good for manual and mechanical operations',
        'Flexible for different conditions',
      ],
      disadvantages: [
        'More complex to implement',
        'Requires planning for row arrangement',
        'Variable results based on execution',
      ],
      suitableSoilTypes: ['loamy', 'clay', 'silty', 'sandy'],
      suitableClimateZones: ['arid', 'semi_arid', 'mediterranean'],
    }],
    ['small_basin', {
      id: 'small_basin',
      nameEn: 'Small Basin Planting',
      nameAr: 'الزراعة في الأحواض الصغيرة',
      nameCn: '畦播',
      description: 'Basin-based planting for water conservation in arid regions',
      suitableYieldRange: { min: 200, max: 400 },
      rowSpacing: { min: 20, max: 25 },
      seedDepth: { min: 10, max: 15 },
      seedingRate: { min: 10, max: 14 },
      advantages: [
        'Excellent water conservation',
        'Suitable for arid climates',
        'Reduces evaporation',
        'Good for saline soils',
        'Easy flood irrigation',
      ],
      disadvantages: [
        'Labor-intensive preparation',
        'Limited mechanization',
        'May cause waterlogging in heavy rain',
        'Requires level ground',
      ],
      suitableSoilTypes: ['sandy', 'loamy', 'saline'],
      suitableClimateZones: ['arid', 'semi_arid'],
    }],
  ]);

  // Crop-specific parameters
  private readonly cropParameters: Map<CropType, {
    thousandGrainWeight: number; // grams
    germinationRate: number; // percentage
    optimalDensity: number; // plants per m²
    waterRequirement: number; // mm per season
    growthDuration: number; // days
    baseTemperature: number; // °C
    optimalTemperature: { min: number; max: number };
  }> = new Map([
    ['wheat', {
      thousandGrainWeight: 42,
      germinationRate: 0.85,
      optimalDensity: 450,
      waterRequirement: 450,
      growthDuration: 180,
      baseTemperature: 4,
      optimalTemperature: { min: 15, max: 22 },
    }],
    ['barley', {
      thousandGrainWeight: 45,
      germinationRate: 0.88,
      optimalDensity: 350,
      waterRequirement: 350,
      growthDuration: 150,
      baseTemperature: 5,
      optimalTemperature: { min: 12, max: 20 },
    }],
    ['corn', {
      thousandGrainWeight: 280,
      germinationRate: 0.92,
      optimalDensity: 65,
      waterRequirement: 550,
      growthDuration: 120,
      baseTemperature: 10,
      optimalTemperature: { min: 20, max: 30 },
    }],
    ['rice', {
      thousandGrainWeight: 25,
      germinationRate: 0.90,
      optimalDensity: 300,
      waterRequirement: 1200,
      growthDuration: 140,
      baseTemperature: 12,
      optimalTemperature: { min: 25, max: 32 },
    }],
    ['sorghum', {
      thousandGrainWeight: 28,
      germinationRate: 0.85,
      optimalDensity: 120,
      waterRequirement: 400,
      growthDuration: 110,
      baseTemperature: 10,
      optimalTemperature: { min: 25, max: 35 },
    }],
    ['date_palm', {
      thousandGrainWeight: 950,
      germinationRate: 0.70,
      optimalDensity: 0.015, // 100-150 palms per hectare
      waterRequirement: 800,
      growthDuration: 365,
      baseTemperature: 18,
      optimalTemperature: { min: 30, max: 40 },
    }],
    ['alfalfa', {
      thousandGrainWeight: 2.2,
      germinationRate: 0.75,
      optimalDensity: 200,
      waterRequirement: 700,
      growthDuration: 365,
      baseTemperature: 5,
      optimalTemperature: { min: 18, max: 28 },
    }],
  ]);

  // Soil adjustment factors
  private readonly soilFactors: Map<SoilType, {
    waterRetention: number;
    fertilityFactor: number;
    workabilityFactor: number;
    densityAdjustment: number;
  }> = new Map([
    ['sandy', { waterRetention: 0.6, fertilityFactor: 0.7, workabilityFactor: 1.2, densityAdjustment: 0.9 }],
    ['loamy', { waterRetention: 1.0, fertilityFactor: 1.0, workabilityFactor: 1.0, densityAdjustment: 1.0 }],
    ['clay', { waterRetention: 1.3, fertilityFactor: 1.1, workabilityFactor: 0.7, densityAdjustment: 0.95 }],
    ['silty', { waterRetention: 1.1, fertilityFactor: 1.05, workabilityFactor: 0.9, densityAdjustment: 1.05 }],
    ['saline', { waterRetention: 0.8, fertilityFactor: 0.6, workabilityFactor: 0.8, densityAdjustment: 0.8 }],
  ]);

  // Climate adjustment factors
  private readonly climateFactors: Map<ClimateZone, {
    temperatureFactor: number;
    precipitationFactor: number;
    evaporationFactor: number;
    yieldAdjustment: number;
  }> = new Map([
    ['arid', { temperatureFactor: 1.3, precipitationFactor: 0.3, evaporationFactor: 1.5, yieldAdjustment: 0.75 }],
    ['semi_arid', { temperatureFactor: 1.1, precipitationFactor: 0.5, evaporationFactor: 1.2, yieldAdjustment: 0.85 }],
    ['mediterranean', { temperatureFactor: 1.0, precipitationFactor: 0.7, evaporationFactor: 1.0, yieldAdjustment: 1.0 }],
    ['continental', { temperatureFactor: 0.9, precipitationFactor: 0.8, evaporationFactor: 0.8, yieldAdjustment: 1.05 }],
    ['tropical', { temperatureFactor: 1.2, precipitationFactor: 1.2, evaporationFactor: 1.3, yieldAdjustment: 0.9 }],
  ]);

  /**
   * Get all available planting methods
   */
  getAllMethods(): PlantingMethod[] {
    return Array.from(this.plantingMethods.values());
  }

  /**
   * Get specific planting method details
   */
  getMethod(methodId: PlantingMethodType): PlantingMethod | undefined {
    return this.plantingMethods.get(methodId);
  }

  /**
   * Optimize planting strategy based on conditions
   */
  optimizePlantingStrategy(request: OptimizationRequest): OptimizationResult {
    // Analyze field conditions
    const fieldAnalysis = this.analyzeField(request);

    // Score each method for the given conditions
    const methodScores = this.scoreAllMethods(request, fieldAnalysis);

    // Select best method
    const sortedMethods = methodScores.sort((a, b) => b.score - a.score);
    const bestMethod = this.plantingMethods.get(sortedMethods[0].method)!;
    const alternativeMethods = sortedMethods.slice(1, 3)
      .map(m => this.plantingMethods.get(m.method)!)
      .filter(m => m !== undefined);

    // Calculate optimal spacing configuration
    const spacingConfig = this.calculateOptimalSpacing(
      request.cropType,
      bestMethod.id,
      request.targetYield,
      request.soilType
    );

    // Generate fertilizer recommendations
    const fertilizerRec = this.calculateFertilizerRecommendations(
      request.cropType,
      request.targetYield,
      request.soilType,
      request.organicMatter || 1.5
    );

    // Generate irrigation schedule
    const irrigationSchedule = this.calculateIrrigationSchedule(
      request.cropType,
      bestMethod.id,
      request.climateZone,
      request.availableWater
    );

    // Predict expected yield
    const yieldPrediction = this.predictYield(
      request.cropType,
      bestMethod.id,
      request.targetYield,
      fieldAnalysis
    );

    // Generate warnings and recommendations
    const warnings: string[] = [];
    const recommendations: string[] = [];

    if (fieldAnalysis.waterAvailabilityScore < 0.6) {
      warnings.push('Water availability is limited. Consider drought-tolerant varieties.');
    }
    if (fieldAnalysis.soilQualityScore < 0.5) {
      warnings.push('Soil quality is below optimal. Soil improvement recommended.');
    }
    if (request.targetYield > bestMethod.suitableYieldRange.max) {
      warnings.push(`Target yield exceeds typical range for ${bestMethod.nameEn}. Results may vary.`);
    }

    recommendations.push(`Optimal planting depth: ${spacingConfig.seedDepth} cm`);
    recommendations.push(`Apply base fertilizer 7-10 days before planting`);
    recommendations.push(`First irrigation immediately after planting`);

    if (bestMethod.id === 'wide_strip') {
      recommendations.push('Use precision seeder for optimal strip width (8-12cm)');
    }
    if (bestMethod.id === 'small_basin') {
      recommendations.push('Prepare basins 5-7 days before planting to allow settling');
    }

    return {
      recommendedMethod: bestMethod,
      alternativeMethods,
      spacingConfiguration: {
        rowSpacing: spacingConfig.rowSpacing,
        plantSpacing: spacingConfig.plantSpacing,
        seedDepth: (bestMethod.seedDepth.min + bestMethod.seedDepth.max) / 2,
        seedingRate: spacingConfig.seedingRateKgPerMu,
        plantsPerMu: spacingConfig.totalPlantsPerMu,
      },
      fertilizerRecommendations: fertilizerRec,
      irrigationSchedule,
      expectedYield: yieldPrediction.adjustedYield,
      confidenceLevel: sortedMethods[0].score,
      warnings,
      recommendations,
    };
  }

  /**
   * Analyze field conditions
   */
  analyzeField(request: OptimizationRequest): FieldAnalysis {
    const soilFactor = this.soilFactors.get(request.soilType)!;
    const climateFactor = this.climateFactors.get(request.climateZone)!;
    const cropParams = this.cropParameters.get(request.cropType)!;

    // Calculate soil quality score
    const soilQualityScore = (
      soilFactor.fertilityFactor * 0.4 +
      soilFactor.waterRetention * 0.3 +
      soilFactor.workabilityFactor * 0.3
    );

    // Calculate water availability score
    const requiredWater = cropParams.waterRequirement * 0.667 / 1000; // Convert to m³/mu
    const waterAvailabilityScore = Math.min(1, request.availableWater / requiredWater);

    // Calculate climate compatibility score
    const climateCompatibilityScore = climateFactor.yieldAdjustment;

    // Overall suitability
    const overallSuitabilityScore = (
      soilQualityScore * 0.35 +
      waterAvailabilityScore * 0.35 +
      climateCompatibilityScore * 0.30
    );

    // Identify limiting factors
    const limitingFactors: string[] = [];
    const improvementSuggestions: string[] = [];

    if (soilFactor.fertilityFactor < 0.8) {
      limitingFactors.push('Low soil fertility');
      improvementSuggestions.push('Apply organic matter and balanced NPK fertilizer');
    }
    if (waterAvailabilityScore < 0.7) {
      limitingFactors.push('Insufficient water supply');
      improvementSuggestions.push('Consider drip irrigation or water-conserving methods');
    }
    if (request.soilType === 'saline') {
      limitingFactors.push('Soil salinity');
      improvementSuggestions.push('Apply gypsum and ensure good drainage');
    }
    if (request.climateZone === 'arid') {
      limitingFactors.push('High evapotranspiration');
      improvementSuggestions.push('Use mulching and schedule irrigation for early morning');
    }

    return {
      soilQualityScore,
      waterAvailabilityScore,
      climateCompatibilityScore,
      overallSuitabilityScore,
      limitingFactors,
      improvementSuggestions,
    };
  }

  /**
   * Score all planting methods for given conditions
   */
  private scoreAllMethods(
    request: OptimizationRequest,
    fieldAnalysis: FieldAnalysis
  ): { method: PlantingMethodType; score: number }[] {
    const scores: { method: PlantingMethodType; score: number }[] = [];

    for (const [methodId, method] of this.plantingMethods) {
      let score = 0.5; // Base score

      // Yield range compatibility (0-0.25)
      const targetYield = request.targetYield;
      if (targetYield >= method.suitableYieldRange.min && targetYield <= method.suitableYieldRange.max) {
        score += 0.25;
      } else if (targetYield < method.suitableYieldRange.min) {
        score += 0.15; // Can achieve lower yield, just not optimal
      } else {
        score += 0.05; // May not achieve higher yield
      }

      // Soil compatibility (0-0.15)
      if (method.suitableSoilTypes.includes(request.soilType)) {
        score += 0.15;
      } else {
        score += 0.05;
      }

      // Climate compatibility (0-0.15)
      if (method.suitableClimateZones.includes(request.climateZone)) {
        score += 0.15;
      } else {
        score += 0.05;
      }

      // Water availability adjustment
      if (methodId === 'small_basin' && fieldAnalysis.waterAvailabilityScore < 0.6) {
        score += 0.1; // Bonus for water-conserving method in water-scarce conditions
      }
      if (methodId === 'wide_strip' && fieldAnalysis.waterAvailabilityScore > 0.8) {
        score += 0.1; // Bonus for high-yield method when water is available
      }

      // Field quality adjustment
      score += fieldAnalysis.overallSuitabilityScore * 0.1;

      scores.push({ method: methodId, score: Math.min(1, score) });
    }

    return scores;
  }

  /**
   * Calculate optimal spacing and density
   */
  calculateDensity(
    cropType: CropType,
    method: PlantingMethodType,
    targetYield: number,
    soilType: SoilType
  ): DensityCalculation {
    const methodConfig = this.plantingMethods.get(method)!;
    const cropParams = this.cropParameters.get(cropType)!;
    const soilFactor = this.soilFactors.get(soilType)!;

    // Calculate base row spacing
    const baseRowSpacing = (methodConfig.rowSpacing.min + methodConfig.rowSpacing.max) / 2;

    // Adjust for method-specific configurations
    let rowSpacing = baseRowSpacing;
    let plantSpacing = 3; // Default 3cm for grains
    let seedsPerHole = 1;

    switch (method) {
      case 'equal_row':
        rowSpacing = targetYield <= 300 ? 20 : 15;
        plantSpacing = 3;
        break;
      case 'wide_strip':
        rowSpacing = 25; // Wide rows
        plantSpacing = 2; // Denser within strip
        break;
      case 'space_broadcasting':
        // Alternating wide (25cm) and narrow (15cm) rows
        rowSpacing = 20; // Average
        plantSpacing = 3;
        break;
      case 'small_basin':
        rowSpacing = 22;
        plantSpacing = 4;
        seedsPerHole = 2;
        break;
    }

    // Apply soil adjustment
    rowSpacing *= soilFactor.densityAdjustment;

    // Calculate plants per mu (1 mu = 666.67 m²)
    const muArea = 666.67 * 10000; // cm²
    const rowsPerMu = Math.floor(Math.sqrt(muArea / rowSpacing) / 100 * rowSpacing);
    const rowLength = Math.sqrt(muArea); // cm
    const plantsPerRow = Math.floor(rowLength / plantSpacing);
    const totalPlantsPerMu = Math.floor(
      rowsPerMu * plantsPerRow * seedsPerHole * cropParams.germinationRate
    );

    // Calculate seeding rate
    const seedingRateKgPerMu = (
      totalPlantsPerMu * cropParams.thousandGrainWeight / 1000 / cropParams.germinationRate / 1000
    );

    // Coverage percentage
    const plantArea = Math.PI * 2 * 2; // Assuming 2cm effective plant radius
    const coveragePercentage = (totalPlantsPerMu * plantArea / muArea) * 100;

    return {
      method,
      rowSpacing: Math.round(rowSpacing * 10) / 10,
      plantSpacing,
      seedsPerHole,
      rowsPerMu,
      plantsPerRow,
      totalPlantsPerMu,
      seedingRateKgPerMu: Math.round(seedingRateKgPerMu * 10) / 10,
      coveragePercentage: Math.round(coveragePercentage * 10) / 10,
    };
  }

  /**
   * Calculate optimal spacing configuration
   */
  private calculateOptimalSpacing(
    cropType: CropType,
    method: PlantingMethodType,
    targetYield: number,
    soilType: SoilType
  ): DensityCalculation & { seedDepth: number } {
    const density = this.calculateDensity(cropType, method, targetYield, soilType);
    const methodConfig = this.plantingMethods.get(method)!;

    return {
      ...density,
      seedDepth: (methodConfig.seedDepth.min + methodConfig.seedDepth.max) / 2,
    };
  }

  /**
   * Calculate fertilizer recommendations
   */
  calculateFertilizerRecommendations(
    cropType: CropType,
    targetYield: number,
    soilType: SoilType,
    organicMatterContent: number
  ): {
    baseApplication: { n: number; p: number; k: number };
    topDressing: { stage: string; n: number; timing: string }[];
    organicMatter: number;
  } {
    const soilFactor = this.soilFactors.get(soilType)!;

    // Base NPK requirements per 100kg grain yield
    const baseNPK = {
      wheat: { n: 3.0, p: 1.2, k: 2.5 },
      barley: { n: 2.5, p: 1.0, k: 2.0 },
      corn: { n: 2.8, p: 1.0, k: 2.5 },
      rice: { n: 2.4, p: 1.0, k: 2.0 },
      sorghum: { n: 2.5, p: 0.8, k: 2.2 },
      date_palm: { n: 2.0, p: 0.8, k: 3.0 },
      alfalfa: { n: 0.5, p: 0.5, k: 2.5 }, // N-fixing
    };

    const cropNPK = baseNPK[cropType];
    const yieldFactor = targetYield / 100;
    const fertilityAdjustment = 2 - soilFactor.fertilityFactor; // Lower fertility = more fertilizer

    // Calculate base application (40% of total N, 100% P&K)
    const totalN = cropNPK.n * yieldFactor * fertilityAdjustment;
    const totalP = cropNPK.p * yieldFactor * fertilityAdjustment;
    const totalK = cropNPK.k * yieldFactor * fertilityAdjustment;

    const baseApplication = {
      n: Math.round(totalN * 0.4 * 10) / 10,
      p: Math.round(totalP * 10) / 10,
      k: Math.round(totalK * 10) / 10,
    };

    // Top dressing schedule (60% of N split)
    const topDressing = [
      {
        stage: 'Tillering',
        n: Math.round(totalN * 0.3 * 10) / 10,
        timing: '25-30 days after emergence',
      },
      {
        stage: 'Jointing',
        n: Math.round(totalN * 0.2 * 10) / 10,
        timing: '45-50 days after emergence',
      },
      {
        stage: 'Heading',
        n: Math.round(totalN * 0.1 * 10) / 10,
        timing: '70-75 days after emergence',
      },
    ];

    // Organic matter recommendation
    const organicMatterNeeded = organicMatterContent < 2.0
      ? Math.round((2.0 - organicMatterContent) * 1000)
      : 500; // Maintenance amount

    return {
      baseApplication,
      topDressing,
      organicMatter: organicMatterNeeded,
    };
  }

  /**
   * Calculate irrigation schedule
   */
  calculateIrrigationSchedule(
    cropType: CropType,
    method: PlantingMethodType,
    climateZone: ClimateZone,
    availableWater: number
  ): {
    prePlanting: number;
    emergence: number;
    tillering: number;
    jointing: number;
    heading: number;
    grainfilling: number;
    totalWater: number;
  } {
    const cropParams = this.cropParameters.get(cropType)!;
    const climateFactor = this.climateFactors.get(climateZone)!;
    const methodConfig = this.plantingMethods.get(method)!;

    // Base water requirement per mu (m³)
    const baseWater = cropParams.waterRequirement * 0.667 / 1000; // Convert mm to m³/mu

    // Climate adjustment
    const adjustedWater = baseWater * climateFactor.evaporationFactor;

    // Method adjustment (small basin saves water)
    const methodAdjustment = method === 'small_basin' ? 0.85 : 1.0;
    const totalRequired = adjustedWater * methodAdjustment;

    // Distribution across growth stages (typical for wheat)
    const schedule = {
      prePlanting: totalRequired * 0.15,
      emergence: totalRequired * 0.10,
      tillering: totalRequired * 0.20,
      jointing: totalRequired * 0.25,
      heading: totalRequired * 0.20,
      grainfilling: totalRequired * 0.10,
      totalWater: totalRequired,
    };

    // Round values
    return {
      prePlanting: Math.round(schedule.prePlanting * 100) / 100,
      emergence: Math.round(schedule.emergence * 100) / 100,
      tillering: Math.round(schedule.tillering * 100) / 100,
      jointing: Math.round(schedule.jointing * 100) / 100,
      heading: Math.round(schedule.heading * 100) / 100,
      grainfilling: Math.round(schedule.grainfilling * 100) / 100,
      totalWater: Math.round(schedule.totalWater * 100) / 100,
    };
  }

  /**
   * Predict yield based on conditions
   */
  predictYield(
    cropType: CropType,
    method: PlantingMethodType,
    targetYield: number,
    fieldAnalysis: FieldAnalysis
  ): YieldPrediction {
    const methodConfig = this.plantingMethods.get(method)!;

    const adjustmentFactors: YieldPrediction['adjustmentFactors'] = [];
    let totalAdjustment = 1.0;

    // Soil quality adjustment
    const soilImpact = (fieldAnalysis.soilQualityScore - 0.7) * 20;
    adjustmentFactors.push({
      factor: 'Soil Quality',
      impact: soilImpact,
      description: fieldAnalysis.soilQualityScore >= 0.7
        ? 'Good soil conditions'
        : 'Soil improvement needed',
    });
    totalAdjustment *= (1 + soilImpact / 100);

    // Water availability adjustment
    const waterImpact = (fieldAnalysis.waterAvailabilityScore - 0.7) * 25;
    adjustmentFactors.push({
      factor: 'Water Availability',
      impact: waterImpact,
      description: fieldAnalysis.waterAvailabilityScore >= 0.7
        ? 'Adequate water supply'
        : 'Water stress expected',
    });
    totalAdjustment *= (1 + waterImpact / 100);

    // Climate compatibility adjustment
    const climateImpact = (fieldAnalysis.climateCompatibilityScore - 1.0) * 15;
    adjustmentFactors.push({
      factor: 'Climate Compatibility',
      impact: climateImpact,
      description: fieldAnalysis.climateCompatibilityScore >= 0.9
        ? 'Favorable climate'
        : 'Climate challenges expected',
    });
    totalAdjustment *= (1 + climateImpact / 100);

    // Method efficiency bonus
    const methodBonus = method === 'wide_strip' ? 10 :
                       method === 'space_broadcasting' ? 5 : 0;
    if (methodBonus > 0) {
      adjustmentFactors.push({
        factor: 'Method Efficiency',
        impact: methodBonus,
        description: `${methodConfig.nameEn} provides yield bonus`,
      });
      totalAdjustment *= (1 + methodBonus / 100);
    }

    // Calculate predicted yield
    const baseYield = Math.min(targetYield, methodConfig.suitableYieldRange.max);
    const adjustedYield = Math.round(baseYield * totalAdjustment);

    // Confidence interval (±15%)
    const confidenceInterval = {
      lower: Math.round(adjustedYield * 0.85),
      upper: Math.round(adjustedYield * 1.15),
    };

    // Risk factors
    const riskFactors: string[] = [];
    if (fieldAnalysis.waterAvailabilityScore < 0.5) {
      riskFactors.push('High drought risk');
    }
    if (fieldAnalysis.soilQualityScore < 0.5) {
      riskFactors.push('Poor soil conditions may limit yield');
    }
    fieldAnalysis.limitingFactors.forEach(f => riskFactors.push(f));

    return {
      method,
      baseYield,
      adjustedYield,
      adjustmentFactors,
      confidenceInterval,
      riskFactors,
    };
  }

  /**
   * Generate complete planting plan
   */
  generatePlantingPlan(
    fieldId: string,
    request: OptimizationRequest,
    plantingDate: Date
  ): PlantingPlan {
    const optimization = this.optimizePlantingStrategy(request);
    const method = optimization.recommendedMethod.id;

    // Define tasks
    const tasks: PlantingTask[] = [
      {
        id: 'soil_test',
        name: 'Soil Testing',
        nameAr: 'فحص التربة',
        description: 'Conduct soil analysis for NPK, pH, and organic matter',
        daysBeforePlanting: 30,
        duration: 2,
        equipment: ['Soil auger', 'Sample containers'],
        laborRequired: 4,
      },
      {
        id: 'field_prep',
        name: 'Field Preparation',
        nameAr: 'تحضير الحقل',
        description: 'Plow and level the field',
        daysBeforePlanting: 14,
        duration: 8,
        equipment: ['Tractor', 'Plow', 'Leveler'],
        laborRequired: 16,
      },
      {
        id: 'base_fertilizer',
        name: 'Base Fertilizer Application',
        nameAr: 'تطبيق السماد الأساسي',
        description: 'Apply base NPK fertilizer and organic matter',
        daysBeforePlanting: 7,
        duration: 4,
        equipment: ['Fertilizer spreader'],
        laborRequired: 8,
      },
      {
        id: 'seed_prep',
        name: 'Seed Preparation',
        nameAr: 'تحضير البذور',
        description: 'Treat seeds with fungicide and measure quantities',
        daysBeforePlanting: 3,
        duration: 2,
        equipment: ['Seed treatment equipment', 'Scales'],
        laborRequired: 4,
      },
      {
        id: 'pre_irrigation',
        name: 'Pre-planting Irrigation',
        nameAr: 'الري قبل الزراعة',
        description: 'Apply pre-planting irrigation to moisten soil',
        daysBeforePlanting: 2,
        duration: 6,
        equipment: ['Irrigation system'],
        laborRequired: 4,
      },
      {
        id: 'planting',
        name: 'Planting',
        nameAr: 'الزراعة',
        description: `Plant using ${optimization.recommendedMethod.nameEn} method`,
        daysBeforePlanting: 0,
        duration: 8,
        equipment: ['Seeder', 'Tractor'],
        laborRequired: 16,
      },
      {
        id: 'post_irrigation',
        name: 'Post-planting Irrigation',
        nameAr: 'الري بعد الزراعة',
        description: 'Light irrigation to ensure seed-soil contact',
        daysBeforePlanting: -1,
        duration: 4,
        equipment: ['Irrigation system'],
        laborRequired: 4,
      },
    ];

    // Add method-specific tasks
    if (method === 'small_basin') {
      tasks.splice(2, 0, {
        id: 'basin_prep',
        name: 'Basin Preparation',
        nameAr: 'تحضير الأحواض',
        description: 'Form basins 20-25cm wide and 10-15cm deep',
        daysBeforePlanting: 10,
        duration: 12,
        equipment: ['Basin maker', 'Tractor'],
        laborRequired: 24,
      });
    }

    // Calculate resource requirements
    const cropParams = this.cropParameters.get(request.cropType)!;
    const seedCost = optimization.spacingConfiguration.seedingRate * 5 * request.fieldArea; // $5/kg estimate

    const resourceRequirements: ResourceRequirements = {
      seeds: {
        quantity: optimization.spacingConfiguration.seedingRate * request.fieldArea,
        unit: 'kg',
        cost: seedCost,
      },
      fertilizer: [
        {
          type: 'Urea (46% N)',
          quantity: optimization.fertilizerRecommendations.baseApplication.n * 2.17 * request.fieldArea,
          unit: 'kg',
          cost: optimization.fertilizerRecommendations.baseApplication.n * 2.17 * 0.5 * request.fieldArea,
        },
        {
          type: 'DAP (18-46-0)',
          quantity: optimization.fertilizerRecommendations.baseApplication.p * 2.17 * request.fieldArea,
          unit: 'kg',
          cost: optimization.fertilizerRecommendations.baseApplication.p * 2.17 * 0.6 * request.fieldArea,
        },
        {
          type: 'Potassium Sulfate',
          quantity: optimization.fertilizerRecommendations.baseApplication.k * 2 * request.fieldArea,
          unit: 'kg',
          cost: optimization.fertilizerRecommendations.baseApplication.k * 2 * 0.4 * request.fieldArea,
        },
      ],
      water: {
        quantity: optimization.irrigationSchedule.totalWater * request.fieldArea,
        unit: 'm³',
      },
      labor: {
        hours: tasks.reduce((sum, t) => sum + t.laborRequired, 0),
        cost: tasks.reduce((sum, t) => sum + t.laborRequired, 0) * 10, // $10/hour estimate
      },
      machinery: [
        { type: 'Tractor', hours: 20 * request.fieldArea / 10, cost: 20 * request.fieldArea / 10 * 30 },
        { type: 'Seeder', hours: 8 * request.fieldArea / 10, cost: 8 * request.fieldArea / 10 * 20 },
      ],
      totalCost: 0,
    };

    resourceRequirements.totalCost =
      resourceRequirements.seeds.cost +
      resourceRequirements.fertilizer.reduce((sum, f) => sum + f.cost, 0) +
      resourceRequirements.labor.cost +
      resourceRequirements.machinery.reduce((sum, m) => sum + m.cost, 0);

    // Generate timeline
    const timeline: TimelineEvent[] = tasks.map(task => ({
      event: task.name,
      date: new Date(plantingDate.getTime() - task.daysBeforePlanting * 24 * 60 * 60 * 1000),
      description: task.description,
      critical: ['planting', 'base_fertilizer', 'pre_irrigation'].includes(task.id),
    }));

    // Add growth stage milestones
    const growthMilestones = [
      { name: 'Emergence', days: 10 },
      { name: 'Tillering', days: 35 },
      { name: 'Jointing', days: 55 },
      { name: 'Heading', days: 80 },
      { name: 'Flowering', days: 90 },
      { name: 'Grain Filling', days: 110 },
      { name: 'Maturity', days: 140 },
      { name: 'Harvest', days: cropParams.growthDuration },
    ];

    growthMilestones.forEach(milestone => {
      timeline.push({
        event: milestone.name,
        date: new Date(plantingDate.getTime() + milestone.days * 24 * 60 * 60 * 1000),
        description: `Expected ${milestone.name.toLowerCase()} stage`,
        critical: ['Heading', 'Harvest'].includes(milestone.name),
      });
    });

    // Sort timeline by date
    timeline.sort((a, b) => a.date.getTime() - b.date.getTime());

    return {
      fieldId,
      cropType: request.cropType,
      method,
      plannedDate: plantingDate,
      tasks,
      resourceRequirements,
      timeline,
    };
  }

  /**
   * Compare multiple planting methods
   */
  compareMethods(
    cropType: CropType,
    targetYield: number,
    soilType: SoilType,
    climateZone: ClimateZone
  ): {
    comparisons: {
      method: PlantingMethod;
      density: DensityCalculation;
      yieldPrediction: YieldPrediction;
      waterRequirement: number;
      suitabilityScore: number;
    }[];
    recommendation: string;
  } {
    const request: OptimizationRequest = {
      cropType,
      targetYield,
      fieldArea: 1,
      soilType,
      climateZone,
      availableWater: 500,
    };

    const fieldAnalysis = this.analyzeField(request);
    const comparisons = [];

    for (const [methodId, method] of this.plantingMethods) {
      const density = this.calculateDensity(cropType, methodId, targetYield, soilType);
      const yieldPrediction = this.predictYield(cropType, methodId, targetYield, fieldAnalysis);
      const irrigation = this.calculateIrrigationSchedule(cropType, methodId, climateZone, 500);

      const scores = this.scoreAllMethods(request, fieldAnalysis);
      const suitabilityScore = scores.find(s => s.method === methodId)?.score || 0;

      comparisons.push({
        method,
        density,
        yieldPrediction,
        waterRequirement: irrigation.totalWater,
        suitabilityScore,
      });
    }

    // Sort by suitability score
    comparisons.sort((a, b) => b.suitabilityScore - a.suitabilityScore);

    // Generate recommendation
    const best = comparisons[0];
    const recommendation = `Based on your conditions (${soilType} soil, ${climateZone} climate, target ${targetYield} kg/mu), ` +
      `we recommend ${best.method.nameEn} (${best.method.nameAr}) with a suitability score of ${(best.suitabilityScore * 100).toFixed(0)}%. ` +
      `Expected yield: ${best.yieldPrediction.adjustedYield} kg/mu. ` +
      `Water requirement: ${best.waterRequirement.toFixed(2)} m³/mu.`;

    return { comparisons, recommendation };
  }

  /**
   * Get method-specific guidance
   */
  getMethodGuidance(method: PlantingMethodType): {
    method: PlantingMethod;
    stepByStepGuide: { step: number; title: string; titleAr: string; description: string; tips: string[] }[];
    commonMistakes: { mistake: string; solution: string }[];
    equipmentRequired: { name: string; purpose: string; alternatives: string[] }[];
  } {
    const methodConfig = this.plantingMethods.get(method);
    if (!methodConfig) {
      throw new Error(`Unknown planting method: ${method}`);
    }

    const guides: Record<PlantingMethodType, { step: number; title: string; titleAr: string; description: string; tips: string[] }[]> = {
      equal_row: [
        { step: 1, title: 'Field Preparation', titleAr: 'تحضير الحقل', description: 'Plow to 20-25cm depth and level the field', tips: ['Ensure good drainage', 'Remove crop residues'] },
        { step: 2, title: 'Mark Rows', titleAr: 'تحديد الصفوف', description: 'Mark rows at 15-20cm intervals', tips: ['Use string lines for straight rows', 'Maintain consistent spacing'] },
        { step: 3, title: 'Seeding', titleAr: 'البذر', description: 'Sow seeds at 3-5cm depth', tips: ['Check seeder calibration', 'Maintain uniform depth'] },
        { step: 4, title: 'Cover and Press', titleAr: 'التغطية والضغط', description: 'Cover seeds and lightly compress soil', tips: ['Ensure seed-soil contact', 'Avoid over-compaction'] },
        { step: 5, title: 'Initial Irrigation', titleAr: 'الري الأولي', description: 'Apply light irrigation immediately', tips: ['Avoid waterlogging', 'Irrigate early morning'] },
      ],
      wide_strip: [
        { step: 1, title: 'Field Preparation', titleAr: 'تحضير الحقل', description: 'Deep plow and fine tilth preparation', tips: ['Achieve fine soil structure', 'Level precisely'] },
        { step: 2, title: 'Calibrate Seeder', titleAr: 'معايرة البذارة', description: 'Set strip width to 8-12cm, row spacing 20-30cm', tips: ['Test on sample area first', 'Check seed rate'] },
        { step: 3, title: 'Create Strips', titleAr: 'إنشاء الأشرطة', description: 'Plant in wide strips with precision seeder', tips: ['Maintain consistent strip width', 'Overlap prevention'] },
        { step: 4, title: 'Firm Soil', titleAr: 'ضغط التربة', description: 'Roll to ensure seed-soil contact', tips: ['Use appropriate roller weight', 'Roll when soil is moist'] },
        { step: 5, title: 'Monitor Closely', titleAr: 'المراقبة عن كثب', description: 'Check emergence uniformity', tips: ['Reseed thin areas if needed', 'Watch for lodging signs later'] },
      ],
      space_broadcasting: [
        { step: 1, title: 'Field Preparation', titleAr: 'تحضير الحقل', description: 'Standard tillage with good leveling', tips: ['Ensure uniform soil moisture', 'Break clods thoroughly'] },
        { step: 2, title: 'Plan Row Pattern', titleAr: 'تخطيط نمط الصفوف', description: 'Alternate wide (20-30cm) and narrow (10-20cm) rows', tips: ['Mark pattern before planting', 'Consider machinery width'] },
        { step: 3, title: 'Adjust Seeder', titleAr: 'ضبط البذارة', description: 'Configure for alternating row spacing', tips: ['Use adjustable seeder', 'Test pattern accuracy'] },
        { step: 4, title: 'Plant Systematically', titleAr: 'الزراعة المنتظمة', description: 'Follow the marked pattern precisely', tips: ['Maintain consistent speed', 'Check alignment regularly'] },
        { step: 5, title: 'Post-plant Care', titleAr: 'العناية بعد الزراعة', description: 'Light irrigation and monitoring', tips: ['Wide rows allow cultivation', 'Good air circulation'] },
      ],
      small_basin: [
        { step: 1, title: 'Field Leveling', titleAr: 'تسوية الحقل', description: 'Precise leveling is critical for basin irrigation', tips: ['Use laser leveler if available', 'Slope <0.1%'] },
        { step: 2, title: 'Basin Formation', titleAr: 'تشكيل الأحواض', description: 'Create basins 20-25cm wide, 10-15cm deep', tips: ['Use basin-making equipment', 'Compact basin walls'] },
        { step: 3, title: 'Pre-irrigation', titleAr: 'الري المسبق', description: 'Fill basins to check level and moisten soil', tips: ['Identify low spots', 'Allow settling'] },
        { step: 4, title: 'Seeding in Basins', titleAr: 'البذر في الأحواض', description: 'Plant seeds in bottom of basins', tips: ['Deeper planting (10-15cm)', '2-3 seeds per spot'] },
        { step: 5, title: 'Basin Irrigation', titleAr: 'ري الأحواض', description: 'Flood irrigate to basin capacity', tips: ['Water conservation benefit', 'Avoid overflow'] },
      ],
    };

    const commonMistakes: Record<PlantingMethodType, { mistake: string; solution: string }[]> = {
      equal_row: [
        { mistake: 'Inconsistent row spacing', solution: 'Use mechanical markers or GPS guidance' },
        { mistake: 'Planting too deep', solution: 'Calibrate seeder depth regularly' },
        { mistake: 'Over-seeding', solution: 'Follow recommended rates for yield target' },
      ],
      wide_strip: [
        { mistake: 'Strips too wide causing competition', solution: 'Keep strips 8-12cm maximum' },
        { mistake: 'Seed bunching in strips', solution: 'Check seed metering mechanism' },
        { mistake: 'Lodging from over-density', solution: 'Reduce seeding rate on fertile soils' },
      ],
      space_broadcasting: [
        { mistake: 'Losing the wide-narrow pattern', solution: 'Mark edges clearly before planting' },
        { mistake: 'Uneven distribution', solution: 'Maintain consistent planting speed' },
        { mistake: 'Wrong row ratio', solution: 'Plan pattern mathematically before field work' },
      ],
      small_basin: [
        { mistake: 'Basins not level', solution: 'Invest time in precision leveling' },
        { mistake: 'Basin walls eroding', solution: 'Compact walls and avoid over-filling' },
        { mistake: 'Waterlogging', solution: 'Ensure drainage and don\'t over-irrigate' },
      ],
    };

    const equipment: Record<PlantingMethodType, { name: string; purpose: string; alternatives: string[] }[]> = {
      equal_row: [
        { name: 'Seed drill', purpose: 'Precision row seeding', alternatives: ['Manual seeder', 'Broadcast spreader with rake'] },
        { name: 'Row marker', purpose: 'Consistent spacing', alternatives: ['String lines', 'GPS guidance'] },
        { name: 'Roller', purpose: 'Seed-soil contact', alternatives: ['Cultipacker', 'Manual tamping'] },
      ],
      wide_strip: [
        { name: 'Wide-strip seeder', purpose: 'Create uniform strips', alternatives: ['Modified seed drill'] },
        { name: 'Precision depth control', purpose: 'Consistent seed depth', alternatives: ['Depth wheels'] },
        { name: 'Heavy roller', purpose: 'Firm seed bed', alternatives: ['Cambridge roller'] },
      ],
      space_broadcasting: [
        { name: 'Adjustable row seeder', purpose: 'Variable spacing', alternatives: ['Multiple pass with standard drill'] },
        { name: 'Pattern marker', purpose: 'Maintain alternating pattern', alternatives: ['GPS mapping'] },
        { name: 'Standard cultivator', purpose: 'Inter-row cultivation', alternatives: ['Manual hoe'] },
      ],
      small_basin: [
        { name: 'Basin maker', purpose: 'Form uniform basins', alternatives: ['Manual basin hoe', 'Furrow opener'] },
        { name: 'Laser leveler', purpose: 'Precision field leveling', alternatives: ['Traditional leveling board'] },
        { name: 'Basin irrigator', purpose: 'Controlled water delivery', alternatives: ['Flood gates', 'Siphon tubes'] },
      ],
    };

    return {
      method: methodConfig,
      stepByStepGuide: guides[method],
      commonMistakes: commonMistakes[method],
      equipmentRequired: equipment[method],
    };
  }

  /**
   * Integrate with Digital Twin for real-time optimization
   */
  integrateWithDigitalTwin(
    fieldId: string,
    currentConditions: {
      soilMoisture: number;
      temperature: number;
      growthStage: string;
      ndvi: number;
    }
  ): {
    currentStatus: string;
    adjustments: { parameter: string; currentValue: any; recommendedValue: any; reason: string }[];
    alerts: { level: 'info' | 'warning' | 'critical'; message: string }[];
    nextActions: { action: string; timing: string; priority: 'high' | 'medium' | 'low' }[];
  } {
    const adjustments: any[] = [];
    const alerts: any[] = [];
    const nextActions: any[] = [];

    // Analyze current conditions
    if (currentConditions.soilMoisture < 30) {
      adjustments.push({
        parameter: 'Irrigation',
        currentValue: 'Low moisture detected',
        recommendedValue: 'Increase irrigation frequency',
        reason: 'Soil moisture below optimal 40-60% range',
      });
      alerts.push({
        level: 'warning',
        message: 'Soil moisture critical - irrigation needed within 24 hours',
      });
      nextActions.push({
        action: 'Apply irrigation',
        timing: 'Immediately',
        priority: 'high',
      });
    }

    if (currentConditions.ndvi < 0.4) {
      adjustments.push({
        parameter: 'Nitrogen',
        currentValue: `NDVI: ${currentConditions.ndvi}`,
        recommendedValue: 'Apply nitrogen top-dressing',
        reason: 'Low NDVI indicates potential nitrogen deficiency',
      });
      nextActions.push({
        action: 'Apply nitrogen fertilizer',
        timing: 'Next 3-5 days',
        priority: 'medium',
      });
    }

    if (currentConditions.temperature > 35) {
      alerts.push({
        level: 'warning',
        message: 'High temperature stress - consider supplemental irrigation',
      });
    }

    // Growth stage specific recommendations
    const stageActions: Record<string, { action: string; timing: string; priority: 'high' | 'medium' | 'low' }> = {
      tillering: { action: 'First nitrogen top-dressing', timing: 'Now', priority: 'high' },
      jointing: { action: 'Second nitrogen application', timing: 'Now', priority: 'high' },
      heading: { action: 'Foliar micronutrient spray', timing: 'Next week', priority: 'medium' },
      grainfilling: { action: 'Maintain irrigation, reduce nitrogen', timing: 'Ongoing', priority: 'medium' },
    };

    if (stageActions[currentConditions.growthStage]) {
      nextActions.push(stageActions[currentConditions.growthStage]);
    }

    const currentStatus = alerts.some(a => a.level === 'critical') ? 'Critical attention needed' :
                         alerts.some(a => a.level === 'warning') ? 'Monitoring required' :
                         'Normal operations';

    return {
      currentStatus,
      adjustments,
      alerts,
      nextActions,
    };
  }
}
