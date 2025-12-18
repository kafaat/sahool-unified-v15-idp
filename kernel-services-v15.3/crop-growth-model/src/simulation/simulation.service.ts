// ═══════════════════════════════════════════════════════════════════════════════
// Growth Simulation Service - خدمة محاكاة النمو
// Integrated Crop Growth Model combining Phenology, Photosynthesis, and Biomass
// ═══════════════════════════════════════════════════════════════════════════════

import { Injectable } from '@nestjs/common';
import { PhenologyService } from '../phenology/phenology.service';
import { PhotosynthesisService } from '../photosynthesis/photosynthesis.service';
import { BiomassService } from '../biomass/biomass.service';

// ─────────────────────────────────────────────────────────────────────────────
// Simulation Input Types
// ─────────────────────────────────────────────────────────────────────────────

interface DailyWeather {
  date: string;
  tmin: number;
  tmax: number;
  radiation: number;  // MJ m⁻² day⁻¹
  precipitation?: number;
}

interface SimulationConfig {
  cropType: string;
  sowingDate: string;
  fieldLocation?: { latitude: number; longitude: number };
  soilType?: string;
  irrigated?: boolean;
}

interface SimulationResult {
  date: string;
  dayOfYear: number;
  daysAfterSowing: number;
  // Phenology
  gdd: number;
  accumulatedGDD: number;
  dvs: number;
  stage: string;
  stageAr: string;
  // Environment
  temperature: number;
  radiation: number;
  par: number;
  // Canopy
  fpar: number;
  lai: number;
  // Production
  grossPhotosynthesis: number;
  netProduction: number;
  // Biomass
  biomass: {
    root: number;
    stem: number;
    leaf: number;
    storage: number;
    total: number;
  };
  // Water (simplified)
  waterStress?: number;
}

@Injectable()
export class GrowthSimulationService {
  constructor(
    private readonly phenologyService: PhenologyService,
    private readonly photosynthesisService: PhotosynthesisService,
    private readonly biomassService: BiomassService,
  ) {}

  // ─────────────────────────────────────────────────────────────────────────────
  // Run Full Growth Simulation
  // تشغيل محاكاة النمو الكاملة
  // ─────────────────────────────────────────────────────────────────────────────

  runSimulation(
    config: SimulationConfig,
    weatherData: DailyWeather[],
  ): {
    config: SimulationConfig;
    summary: {
      cropType: string;
      sowingDate: string;
      harvestDate: string;
      seasonLength: number;
      maxLAI: number;
      totalBiomass: number;
      estimatedYield: number;
      yieldUnit: string;
    };
    keyDates: Array<{ event: string; eventAr: string; date: string; daysAfterSowing: number }>;
    dailyResults: SimulationResult[];
  } {
    const results: SimulationResult[] = [];
    const keyDates: Array<{ event: string; eventAr: string; date: string; daysAfterSowing: number }> = [];

    // Initialize state
    let accumulatedGDD = 0;
    let afterFlowering = false;
    let floweringGDD = 0;
    let biomass = { root: 5, stem: 3, leaf: 2, storage: 0 }; // Initial seedling
    let currentStage = '';
    let maxLAI = 0;

    // Get crop parameters
    const cropParams = this.phenologyService.getCropParameters(config.cropType);
    if (!cropParams || typeof cropParams !== 'object' || !('TSUM1' in cropParams)) {
      throw new Error(`Unknown crop type: ${config.cropType}`);
    }

    const tbase = cropParams.TBASEM;
    const tmax = cropParams.TEFFMX;

    weatherData.forEach((weather, index) => {
      const daysAfterSowing = index + 1;
      const dayOfYear = this.getDayOfYear(weather.date);
      const avgTemp = (weather.tmin + weather.tmax) / 2;

      // Calculate GDD
      const gdd = this.phenologyService.calculateGDD(
        weather.tmin,
        weather.tmax,
        tbase,
        tmax,
      );
      accumulatedGDD += gdd;

      // Check flowering transition
      if (!afterFlowering && accumulatedGDD >= cropParams.TSUM1) {
        afterFlowering = true;
        floweringGDD = accumulatedGDD;
        keyDates.push({
          event: 'Flowering',
          eventAr: 'الإزهار',
          date: weather.date,
          daysAfterSowing,
        });
      }

      // Calculate DVS
      const gddForDVS = afterFlowering ? accumulatedGDD - floweringGDD : accumulatedGDD;
      const { dvs, stage } = this.phenologyService.calculateDVS(
        gddForDVS,
        config.cropType,
        afterFlowering,
      );

      // Track stage transitions
      if (stage.name !== currentStage) {
        currentStage = stage.name;
        if (index > 0) {
          keyDates.push({
            event: stage.name,
            eventAr: stage.nameAr,
            date: weather.date,
            daysAfterSowing,
          });
        }
      }

      // Calculate PAR (approximately 50% of total radiation)
      const par = weather.radiation * 0.5;

      // Calculate LAI and fPAR
      const laiResult = this.biomassService.calculateLAI(biomass.leaf, config.cropType);
      const lai = laiResult.lai;
      maxLAI = Math.max(maxLAI, lai);

      // fPAR using Beer-Lambert law
      const k = 0.5; // Extinction coefficient
      const fpar = Math.min(0.95, 1 - Math.exp(-k * lai));

      // Calculate photosynthesis
      const gppResult = this.photosynthesisService.calculateGrossPrimaryProduction(
        par,
        fpar,
        config.cropType,
        avgTemp,
      );

      // Calculate biomass production
      const production = this.biomassService.calculateDailyBiomassProduction(
        par,
        fpar,
        config.cropType,
        avgTemp,
        biomass,
      );

      // Distribute assimilates
      const distribution = this.biomassService.distributeAssimilates(
        production.netProduction,
        config.cropType,
        dvs,
      );

      // Update biomass
      biomass.root += distribution.toRoot;
      biomass.stem += distribution.toStem;
      biomass.leaf += distribution.toLeaf;
      biomass.storage += distribution.toStorage;

      const totalBiomass = biomass.root + biomass.stem + biomass.leaf + biomass.storage;

      results.push({
        date: weather.date,
        dayOfYear,
        daysAfterSowing,
        gdd,
        accumulatedGDD: Math.round(accumulatedGDD),
        dvs,
        stage: stage.name,
        stageAr: stage.nameAr,
        temperature: avgTemp,
        radiation: weather.radiation,
        par,
        fpar: Math.round(fpar * 100) / 100,
        lai: Math.round(lai * 100) / 100,
        grossPhotosynthesis: gppResult.gpp,
        netProduction: production.netProduction,
        biomass: {
          root: Math.round(biomass.root),
          stem: Math.round(biomass.stem),
          leaf: Math.round(biomass.leaf),
          storage: Math.round(biomass.storage),
          total: Math.round(totalBiomass),
        },
      });
    });

    // Calculate final yield
    const finalResult = results[results.length - 1];
    const abovegroundBiomass = finalResult.biomass.stem +
      finalResult.biomass.leaf + finalResult.biomass.storage;
    const yieldResult = this.biomassService.calculateYield(
      abovegroundBiomass,
      config.cropType,
    );

    // Find harvest date (maturity or end of data)
    const harvestDate = results[results.length - 1].date;

    return {
      config,
      summary: {
        cropType: config.cropType,
        sowingDate: config.sowingDate,
        harvestDate,
        seasonLength: results.length,
        maxLAI: Math.round(maxLAI * 100) / 100,
        totalBiomass: finalResult.biomass.total,
        estimatedYield: yieldResult.grainYield,
        yieldUnit: yieldResult.unit,
      },
      keyDates,
      dailyResults: results,
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Generate Sample Weather Data
  // توليد بيانات طقس نموذجية
  // ─────────────────────────────────────────────────────────────────────────────

  generateSampleWeather(
    startDate: string,
    days: number,
    climate: 'temperate' | 'tropical' | 'arid' = 'temperate',
  ): DailyWeather[] {
    const weather: DailyWeather[] = [];
    const start = new Date(startDate);

    // Climate-specific base parameters
    const climateParams = {
      temperate: { baseTmin: 5, baseTmax: 20, radiation: 15, seasonalAmp: 10 },
      tropical: { baseTmin: 22, baseTmax: 32, radiation: 18, seasonalAmp: 3 },
      arid: { baseTmin: 15, baseTmax: 35, radiation: 22, seasonalAmp: 8 },
    };

    const params = climateParams[climate];

    for (let i = 0; i < days; i++) {
      const date = new Date(start);
      date.setDate(date.getDate() + i);

      // Seasonal variation
      const dayOfYear = this.getDayOfYear(date.toISOString().split('T')[0]);
      const seasonalFactor = Math.sin((dayOfYear - 80) * 2 * Math.PI / 365);

      // Add some random variation
      const randomVar = (Math.random() - 0.5) * 5;

      const tmin = params.baseTmin + seasonalFactor * params.seasonalAmp + randomVar;
      const tmax = params.baseTmax + seasonalFactor * params.seasonalAmp + randomVar;
      const radiation = params.radiation + seasonalFactor * 5 + (Math.random() - 0.5) * 4;

      weather.push({
        date: date.toISOString().split('T')[0],
        tmin: Math.round(tmin * 10) / 10,
        tmax: Math.round(tmax * 10) / 10,
        radiation: Math.round(Math.max(5, radiation) * 10) / 10,
      });
    }

    return weather;
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Quick Yield Estimation
  // تقدير سريع للغلة
  // ─────────────────────────────────────────────────────────────────────────────

  quickYieldEstimate(
    cropType: string,
    avgTemperature: number,
    avgRadiation: number,
    seasonLength: number,
  ): {
    estimatedYield: number;
    unit: string;
    assumptions: string[];
    confidence: string;
  } {
    // Simplified yield estimation
    // Based on radiation interception and conversion efficiency

    // Get crop parameters
    const biomassParams = this.biomassService.getCropParameters(cropType);
    if (!biomassParams || typeof biomassParams !== 'object' || !('RUE' in biomassParams)) {
      return {
        estimatedYield: 0,
        unit: 'kg ha⁻¹',
        assumptions: ['Unknown crop type'],
        confidence: 'very_low',
      };
    }

    // Average PAR
    const avgPAR = avgRadiation * 0.5;

    // Estimated average fPAR (assuming good canopy development)
    const avgFPAR = 0.7;

    // Temperature penalty
    const optTemp = 25; // Generic optimum
    const tempPenalty = Math.max(0.5, 1 - Math.abs(avgTemperature - optTemp) / 30);

    // Total intercepted PAR
    const totalPAR = avgPAR * avgFPAR * seasonLength;

    // Biomass production (g/m²)
    const totalBiomass = totalPAR * biomassParams.RUE * tempPenalty;

    // Yield from harvest index
    const yieldGM2 = totalBiomass * biomassParams.harvestIndex;
    const yieldKgHa = yieldGM2 * 10;

    return {
      estimatedYield: Math.round(yieldKgHa),
      unit: 'kg ha⁻¹',
      assumptions: [
        `Average fPAR = ${avgFPAR}`,
        `RUE = ${biomassParams.RUE} g MJ⁻¹`,
        `Harvest Index = ${biomassParams.harvestIndex}`,
        'No water or nutrient stress assumed',
      ],
      confidence: 'moderate',
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Model Information
  // الحصول على معلومات النموذج
  // ─────────────────────────────────────────────────────────────────────────────

  getModelInfo(): {
    name: string;
    nameAr: string;
    version: string;
    components: Array<{ name: string; nameAr: string; description: string }>;
    basedOn: string[];
    supportedCrops: Array<{ id: string; nameEn: string; nameAr: string }>;
  } {
    return {
      name: 'SAHOOL Crop Growth Model',
      nameAr: 'نموذج نمو المحاصيل - سهول',
      version: '1.0.0',
      components: [
        {
          name: 'Phenology',
          nameAr: 'مراحل النمو',
          description: 'WOFOST-style DVS with thermal time accumulation',
        },
        {
          name: 'Photosynthesis',
          nameAr: 'التمثيل الضوئي',
          description: 'LUE model and simplified Farquhar (FvCB) model',
        },
        {
          name: 'Biomass',
          nameAr: 'الكتلة الحيوية',
          description: 'Source-Sink-Flow partitioning with respiration',
        },
      ],
      basedOn: [
        'WOFOST (World Food Studies)',
        'DSSAT (Decision Support System for Agrotechnology Transfer)',
        'APSIM (Agricultural Production Systems sIMulator)',
        'Farquhar-von Caemmerer-Berry (FvCB) Model',
      ],
      supportedCrops: this.phenologyService.getAvailableCrops(),
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Helper: Get Day of Year
  // ─────────────────────────────────────────────────────────────────────────────

  private getDayOfYear(dateString: string): number {
    const date = new Date(dateString);
    const start = new Date(date.getFullYear(), 0, 0);
    const diff = date.getTime() - start.getTime();
    const oneDay = 1000 * 60 * 60 * 24;
    return Math.floor(diff / oneDay);
  }
}
