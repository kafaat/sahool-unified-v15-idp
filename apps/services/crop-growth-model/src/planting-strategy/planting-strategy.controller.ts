import {
  Controller,
  Get,
  Post,
  Body,
  Param,
  Query,
  HttpException,
  HttpStatus,
} from "@nestjs/common";
import { PlantingStrategyService } from "./planting-strategy.service";

// Request DTOs
interface OptimizeStrategyDto {
  cropType:
    | "wheat"
    | "barley"
    | "corn"
    | "rice"
    | "sorghum"
    | "date_palm"
    | "alfalfa";
  targetYield: number;
  fieldArea: number;
  soilType: "sandy" | "loamy" | "clay" | "silty" | "saline";
  climateZone:
    | "arid"
    | "semi_arid"
    | "mediterranean"
    | "continental"
    | "tropical";
  availableWater: number;
  soilMoisture?: number;
  organicMatter?: number;
  previousCrop?: string;
  plantingDate?: string;
}

interface GeneratePlanDto {
  fieldId: string;
  cropType:
    | "wheat"
    | "barley"
    | "corn"
    | "rice"
    | "sorghum"
    | "date_palm"
    | "alfalfa";
  targetYield: number;
  fieldArea: number;
  soilType: "sandy" | "loamy" | "clay" | "silty" | "saline";
  climateZone:
    | "arid"
    | "semi_arid"
    | "mediterranean"
    | "continental"
    | "tropical";
  availableWater: number;
  plantingDate: string;
  soilMoisture?: number;
  organicMatter?: number;
}

interface CalculateDensityDto {
  cropType:
    | "wheat"
    | "barley"
    | "corn"
    | "rice"
    | "sorghum"
    | "date_palm"
    | "alfalfa";
  method: "equal_row" | "wide_strip" | "space_broadcasting" | "small_basin";
  targetYield: number;
  soilType: "sandy" | "loamy" | "clay" | "silty" | "saline";
}

interface CalculateFertilizerDto {
  cropType:
    | "wheat"
    | "barley"
    | "corn"
    | "rice"
    | "sorghum"
    | "date_palm"
    | "alfalfa";
  targetYield: number;
  soilType: "sandy" | "loamy" | "clay" | "silty" | "saline";
  organicMatterContent: number;
}

interface CalculateIrrigationDto {
  cropType:
    | "wheat"
    | "barley"
    | "corn"
    | "rice"
    | "sorghum"
    | "date_palm"
    | "alfalfa";
  method: "equal_row" | "wide_strip" | "space_broadcasting" | "small_basin";
  climateZone:
    | "arid"
    | "semi_arid"
    | "mediterranean"
    | "continental"
    | "tropical";
  availableWater: number;
}

interface DigitalTwinIntegrationDto {
  fieldId: string;
  soilMoisture: number;
  temperature: number;
  growthStage: string;
  ndvi: number;
}

interface CompareMethodsDto {
  cropType:
    | "wheat"
    | "barley"
    | "corn"
    | "rice"
    | "sorghum"
    | "date_palm"
    | "alfalfa";
  targetYield: number;
  soilType: "sandy" | "loamy" | "clay" | "silty" | "saline";
  climateZone:
    | "arid"
    | "semi_arid"
    | "mediterranean"
    | "continental"
    | "tropical";
}

interface AnalyzeFieldDto {
  cropType:
    | "wheat"
    | "barley"
    | "corn"
    | "rice"
    | "sorghum"
    | "date_palm"
    | "alfalfa";
  targetYield: number;
  fieldArea: number;
  soilType: "sandy" | "loamy" | "clay" | "silty" | "saline";
  climateZone:
    | "arid"
    | "semi_arid"
    | "mediterranean"
    | "continental"
    | "tropical";
  availableWater: number;
  soilMoisture?: number;
  organicMatter?: number;
}

@Controller("planting-strategy")
export class PlantingStrategyController {
  constructor(
    private readonly plantingStrategyService: PlantingStrategyService,
  ) {}

  /**
   * GET /planting-strategy
   * Service information and capabilities
   */
  @Get()
  getServiceInfo() {
    return {
      service: "Planting Strategy Optimizer",
      serviceAr: "محسّن استراتيجية الزراعة",
      version: "1.0.0",
      description:
        "Optimizes planting strategies based on crop type, soil conditions, and climate zone",
      capabilities: [
        "Planting method optimization",
        "Density and spacing calculations",
        "Fertilizer recommendations",
        "Irrigation scheduling",
        "Yield prediction",
        "Complete planting plan generation",
        "Method comparison analysis",
        "Digital Twin integration",
      ],
      plantingMethods: [
        {
          id: "equal_row",
          nameEn: "Equal Row Broadcasting",
          nameAr: "البذر المتساوي الصفوف",
        },
        {
          id: "wide_strip",
          nameEn: "Wide Strip Broadcasting",
          nameAr: "البذر الشريطي العريض",
        },
        {
          id: "space_broadcasting",
          nameEn: "Space Broadcasting",
          nameAr: "البذر المتباعد",
        },
        {
          id: "small_basin",
          nameEn: "Small Basin Planting",
          nameAr: "الزراعة في الأحواض الصغيرة",
        },
      ],
      supportedCrops: [
        "wheat",
        "barley",
        "corn",
        "rice",
        "sorghum",
        "date_palm",
        "alfalfa",
      ],
      supportedSoilTypes: ["sandy", "loamy", "clay", "silty", "saline"],
      supportedClimateZones: [
        "arid",
        "semi_arid",
        "mediterranean",
        "continental",
        "tropical",
      ],
      endpoints: {
        methods: "GET /planting-strategy/methods - List all planting methods",
        methodDetail:
          "GET /planting-strategy/methods/:methodId - Get method details",
        methodGuidance:
          "GET /planting-strategy/methods/:methodId/guidance - Step-by-step guide",
        optimize:
          "POST /planting-strategy/optimize - Get optimal strategy recommendation",
        generatePlan:
          "POST /planting-strategy/plan - Generate complete planting plan",
        calculateDensity:
          "POST /planting-strategy/density - Calculate planting density",
        calculateFertilizer:
          "POST /planting-strategy/fertilizer - Get fertilizer recommendations",
        calculateIrrigation:
          "POST /planting-strategy/irrigation - Get irrigation schedule",
        compareMethods: "POST /planting-strategy/compare - Compare all methods",
        analyzeField:
          "POST /planting-strategy/analyze-field - Analyze field conditions",
        digitalTwin:
          "POST /planting-strategy/digital-twin - Real-time optimization with Digital Twin",
      },
    };
  }

  /**
   * GET /planting-strategy/methods
   * List all available planting methods
   */
  @Get("methods")
  getAllMethods() {
    const methods = this.plantingStrategyService.getAllMethods();
    return {
      success: true,
      count: methods.length,
      methods: methods.map((m) => ({
        id: m.id,
        nameEn: m.nameEn,
        nameAr: m.nameAr,
        nameCn: m.nameCn,
        description: m.description,
        suitableYieldRange: m.suitableYieldRange,
        rowSpacing: m.rowSpacing,
        advantages: m.advantages,
        suitableSoilTypes: m.suitableSoilTypes,
        suitableClimateZones: m.suitableClimateZones,
      })),
    };
  }

  /**
   * GET /planting-strategy/methods/:methodId
   * Get specific planting method details
   */
  @Get("methods/:methodId")
  getMethod(@Param("methodId") methodId: string) {
    type PlantingMethodType =
      | "equal_row"
      | "wide_strip"
      | "space_broadcasting"
      | "small_basin";
    const validMethods: PlantingMethodType[] = [
      "equal_row",
      "wide_strip",
      "space_broadcasting",
      "small_basin",
    ];

    const isValidMethod = (id: string): id is PlantingMethodType => {
      return validMethods.includes(id as PlantingMethodType);
    };

    if (!isValidMethod(methodId)) {
      throw new HttpException(
        `Invalid method ID. Valid options: ${validMethods.join(", ")}`,
        HttpStatus.BAD_REQUEST,
      );
    }

    const method = this.plantingStrategyService.getMethod(methodId);
    if (!method) {
      throw new HttpException("Method not found", HttpStatus.NOT_FOUND);
    }

    return {
      success: true,
      method,
    };
  }

  /**
   * GET /planting-strategy/methods/:methodId/guidance
   * Get step-by-step guidance for a specific method
   */
  @Get("methods/:methodId/guidance")
  getMethodGuidance(@Param("methodId") methodId: string) {
    type PlantingMethodType =
      | "equal_row"
      | "wide_strip"
      | "space_broadcasting"
      | "small_basin";
    const validMethods: PlantingMethodType[] = [
      "equal_row",
      "wide_strip",
      "space_broadcasting",
      "small_basin",
    ];

    const isValidMethod = (id: string): id is PlantingMethodType => {
      return validMethods.includes(id as PlantingMethodType);
    };

    if (!isValidMethod(methodId)) {
      throw new HttpException(
        `Invalid method ID. Valid options: ${validMethods.join(", ")}`,
        HttpStatus.BAD_REQUEST,
      );
    }

    try {
      const guidance = this.plantingStrategyService.getMethodGuidance(methodId);
      return {
        success: true,
        guidance,
      };
    } catch (error) {
      throw new HttpException(error.message, HttpStatus.BAD_REQUEST);
    }
  }

  /**
   * POST /planting-strategy/optimize
   * Get optimal planting strategy recommendation
   */
  @Post("optimize")
  optimizeStrategy(@Body() dto: OptimizeStrategyDto) {
    // Validate required fields
    if (
      !dto.cropType ||
      !dto.targetYield ||
      !dto.fieldArea ||
      !dto.soilType ||
      !dto.climateZone ||
      dto.availableWater === undefined
    ) {
      throw new HttpException(
        "Missing required fields: cropType, targetYield, fieldArea, soilType, climateZone, availableWater",
        HttpStatus.BAD_REQUEST,
      );
    }

    const request = {
      cropType: dto.cropType,
      targetYield: dto.targetYield,
      fieldArea: dto.fieldArea,
      soilType: dto.soilType,
      climateZone: dto.climateZone,
      availableWater: dto.availableWater,
      soilMoisture: dto.soilMoisture,
      organicMatter: dto.organicMatter,
      previousCrop: dto.previousCrop,
      plantingDate: dto.plantingDate ? new Date(dto.plantingDate) : undefined,
    };

    const result =
      this.plantingStrategyService.optimizePlantingStrategy(request);

    return {
      success: true,
      optimization: {
        recommendedMethod: {
          id: result.recommendedMethod.id,
          nameEn: result.recommendedMethod.nameEn,
          nameAr: result.recommendedMethod.nameAr,
          description: result.recommendedMethod.description,
        },
        alternativeMethods: result.alternativeMethods.map((m) => ({
          id: m.id,
          nameEn: m.nameEn,
          nameAr: m.nameAr,
        })),
        spacingConfiguration: result.spacingConfiguration,
        fertilizerRecommendations: result.fertilizerRecommendations,
        irrigationSchedule: result.irrigationSchedule,
        expectedYield: result.expectedYield,
        confidenceLevel: Math.round(result.confidenceLevel * 100) + "%",
        warnings: result.warnings,
        recommendations: result.recommendations,
      },
    };
  }

  /**
   * POST /planting-strategy/plan
   * Generate complete planting plan
   */
  @Post("plan")
  generatePlan(@Body() dto: GeneratePlanDto) {
    // Validate required fields
    if (
      !dto.fieldId ||
      !dto.cropType ||
      !dto.targetYield ||
      !dto.fieldArea ||
      !dto.soilType ||
      !dto.climateZone ||
      dto.availableWater === undefined ||
      !dto.plantingDate
    ) {
      throw new HttpException(
        "Missing required fields: fieldId, cropType, targetYield, fieldArea, soilType, climateZone, availableWater, plantingDate",
        HttpStatus.BAD_REQUEST,
      );
    }

    const request = {
      cropType: dto.cropType,
      targetYield: dto.targetYield,
      fieldArea: dto.fieldArea,
      soilType: dto.soilType,
      climateZone: dto.climateZone,
      availableWater: dto.availableWater,
      soilMoisture: dto.soilMoisture,
      organicMatter: dto.organicMatter,
    };

    const plantingDate = new Date(dto.plantingDate);
    const plan = this.plantingStrategyService.generatePlantingPlan(
      dto.fieldId,
      request,
      plantingDate,
    );

    return {
      success: true,
      plan: {
        fieldId: plan.fieldId,
        cropType: plan.cropType,
        method: plan.method,
        plannedDate: plan.plannedDate.toISOString().split("T")[0],
        tasks: plan.tasks.map((t) => ({
          id: t.id,
          name: t.name,
          nameAr: t.nameAr,
          description: t.description,
          scheduledDate: new Date(
            plantingDate.getTime() - t.daysBeforePlanting * 24 * 60 * 60 * 1000,
          )
            .toISOString()
            .split("T")[0],
          daysBeforePlanting: t.daysBeforePlanting,
          duration: t.duration + " hours",
          equipment: t.equipment,
          laborRequired: t.laborRequired + " person-hours",
        })),
        resourceRequirements: {
          seeds: `${plan.resourceRequirements.seeds.quantity.toFixed(1)} ${plan.resourceRequirements.seeds.unit}`,
          fertilizers: plan.resourceRequirements.fertilizer.map(
            (f) => `${f.type}: ${f.quantity.toFixed(1)} ${f.unit}`,
          ),
          water: `${plan.resourceRequirements.water.quantity.toFixed(1)} ${plan.resourceRequirements.water.unit}`,
          laborHours: plan.resourceRequirements.labor.hours,
          estimatedCost: "$" + plan.resourceRequirements.totalCost.toFixed(2),
        },
        timeline: plan.timeline.map((t) => ({
          event: t.event,
          date: t.date.toISOString().split("T")[0],
          description: t.description,
          critical: t.critical,
        })),
      },
    };
  }

  /**
   * POST /planting-strategy/density
   * Calculate planting density
   */
  @Post("density")
  calculateDensity(@Body() dto: CalculateDensityDto) {
    if (!dto.cropType || !dto.method || !dto.targetYield || !dto.soilType) {
      throw new HttpException(
        "Missing required fields: cropType, method, targetYield, soilType",
        HttpStatus.BAD_REQUEST,
      );
    }

    const result = this.plantingStrategyService.calculateDensity(
      dto.cropType,
      dto.method,
      dto.targetYield,
      dto.soilType,
    );

    return {
      success: true,
      densityCalculation: {
        method: result.method,
        rowSpacing: result.rowSpacing + " cm",
        plantSpacing: result.plantSpacing + " cm",
        seedsPerHole: result.seedsPerHole,
        rowsPerMu: result.rowsPerMu,
        plantsPerRow: result.plantsPerRow,
        totalPlantsPerMu: result.totalPlantsPerMu,
        seedingRate: result.seedingRateKgPerMu + " kg/mu",
        coveragePercentage: result.coveragePercentage + "%",
      },
    };
  }

  /**
   * POST /planting-strategy/fertilizer
   * Calculate fertilizer recommendations
   */
  @Post("fertilizer")
  calculateFertilizer(@Body() dto: CalculateFertilizerDto) {
    if (
      !dto.cropType ||
      !dto.targetYield ||
      !dto.soilType ||
      dto.organicMatterContent === undefined
    ) {
      throw new HttpException(
        "Missing required fields: cropType, targetYield, soilType, organicMatterContent",
        HttpStatus.BAD_REQUEST,
      );
    }

    const result =
      this.plantingStrategyService.calculateFertilizerRecommendations(
        dto.cropType,
        dto.targetYield,
        dto.soilType,
        dto.organicMatterContent,
      );

    return {
      success: true,
      fertilizerRecommendations: {
        baseApplication: {
          nitrogen: result.baseApplication.n + " kg/mu",
          phosphorus: result.baseApplication.p + " kg/mu",
          potassium: result.baseApplication.k + " kg/mu",
          timing: "7-10 days before planting",
        },
        topDressing: result.topDressing.map((td) => ({
          stage: td.stage,
          nitrogen: td.n + " kg/mu",
          timing: td.timing,
        })),
        organicMatter: result.organicMatter + " kg/mu",
        notes: [
          "Apply base fertilizer and incorporate into soil",
          "Split nitrogen applications to reduce losses",
          "Adjust rates based on soil test results",
        ],
      },
    };
  }

  /**
   * POST /planting-strategy/irrigation
   * Calculate irrigation schedule
   */
  @Post("irrigation")
  calculateIrrigation(@Body() dto: CalculateIrrigationDto) {
    if (
      !dto.cropType ||
      !dto.method ||
      !dto.climateZone ||
      dto.availableWater === undefined
    ) {
      throw new HttpException(
        "Missing required fields: cropType, method, climateZone, availableWater",
        HttpStatus.BAD_REQUEST,
      );
    }

    const result = this.plantingStrategyService.calculateIrrigationSchedule(
      dto.cropType,
      dto.method,
      dto.climateZone,
      dto.availableWater,
    );

    return {
      success: true,
      irrigationSchedule: {
        stages: [
          {
            stage: "Pre-planting",
            water: result.prePlanting + " m³/mu",
            timing: "2-3 days before planting",
          },
          {
            stage: "Emergence",
            water: result.emergence + " m³/mu",
            timing: "7-10 days after planting",
          },
          {
            stage: "Tillering",
            water: result.tillering + " m³/mu",
            timing: "25-35 days after planting",
          },
          {
            stage: "Jointing",
            water: result.jointing + " m³/mu",
            timing: "50-60 days after planting",
          },
          {
            stage: "Heading",
            water: result.heading + " m³/mu",
            timing: "75-85 days after planting",
          },
          {
            stage: "Grain Filling",
            water: result.grainfilling + " m³/mu",
            timing: "100-120 days after planting",
          },
        ],
        totalSeasonWater: result.totalWater + " m³/mu",
        waterSufficiency:
          dto.availableWater >= result.totalWater
            ? "Sufficient"
            : "Deficit - consider water-saving methods",
        recommendations: [
          "Irrigate in early morning to reduce evaporation",
          "Monitor soil moisture to avoid over-watering",
          "Consider drip irrigation for water conservation",
        ],
      },
    };
  }

  /**
   * POST /planting-strategy/compare
   * Compare all planting methods
   */
  @Post("compare")
  compareMethods(@Body() dto: CompareMethodsDto) {
    if (
      !dto.cropType ||
      !dto.targetYield ||
      !dto.soilType ||
      !dto.climateZone
    ) {
      throw new HttpException(
        "Missing required fields: cropType, targetYield, soilType, climateZone",
        HttpStatus.BAD_REQUEST,
      );
    }

    const result = this.plantingStrategyService.compareMethods(
      dto.cropType,
      dto.targetYield,
      dto.soilType,
      dto.climateZone,
    );

    return {
      success: true,
      comparison: {
        methods: result.comparisons.map((c) => ({
          method: {
            id: c.method.id,
            nameEn: c.method.nameEn,
            nameAr: c.method.nameAr,
          },
          suitabilityScore: Math.round(c.suitabilityScore * 100) + "%",
          expectedYield: c.yieldPrediction.adjustedYield + " kg/mu",
          yieldConfidence: `${c.yieldPrediction.confidenceInterval.lower} - ${c.yieldPrediction.confidenceInterval.upper} kg/mu`,
          seedingRate: c.density.seedingRateKgPerMu + " kg/mu",
          waterRequirement: c.waterRequirement.toFixed(2) + " m³/mu",
          advantages: c.method.advantages.slice(0, 3),
        })),
        recommendation: result.recommendation,
      },
    };
  }

  /**
   * POST /planting-strategy/analyze-field
   * Analyze field conditions
   */
  @Post("analyze-field")
  analyzeField(@Body() dto: AnalyzeFieldDto) {
    if (
      !dto.cropType ||
      !dto.targetYield ||
      !dto.fieldArea ||
      !dto.soilType ||
      !dto.climateZone ||
      dto.availableWater === undefined
    ) {
      throw new HttpException(
        "Missing required fields: cropType, targetYield, fieldArea, soilType, climateZone, availableWater",
        HttpStatus.BAD_REQUEST,
      );
    }

    const request = {
      cropType: dto.cropType,
      targetYield: dto.targetYield,
      fieldArea: dto.fieldArea,
      soilType: dto.soilType,
      climateZone: dto.climateZone,
      availableWater: dto.availableWater,
      soilMoisture: dto.soilMoisture,
      organicMatter: dto.organicMatter,
    };

    const result = this.plantingStrategyService.analyzeField(request);

    return {
      success: true,
      fieldAnalysis: {
        scores: {
          soilQuality: Math.round(result.soilQualityScore * 100) + "%",
          waterAvailability:
            Math.round(result.waterAvailabilityScore * 100) + "%",
          climateCompatibility:
            Math.round(result.climateCompatibilityScore * 100) + "%",
          overallSuitability:
            Math.round(result.overallSuitabilityScore * 100) + "%",
        },
        rating:
          result.overallSuitabilityScore >= 0.8
            ? "Excellent"
            : result.overallSuitabilityScore >= 0.6
              ? "Good"
              : result.overallSuitabilityScore >= 0.4
                ? "Fair"
                : "Poor",
        limitingFactors: result.limitingFactors,
        improvementSuggestions: result.improvementSuggestions,
      },
    };
  }

  /**
   * POST /planting-strategy/digital-twin
   * Real-time optimization with Digital Twin integration
   */
  @Post("digital-twin")
  integrateDigitalTwin(@Body() dto: DigitalTwinIntegrationDto) {
    if (
      !dto.fieldId ||
      dto.soilMoisture === undefined ||
      dto.temperature === undefined ||
      !dto.growthStage ||
      dto.ndvi === undefined
    ) {
      throw new HttpException(
        "Missing required fields: fieldId, soilMoisture, temperature, growthStage, ndvi",
        HttpStatus.BAD_REQUEST,
      );
    }

    const result = this.plantingStrategyService.integrateWithDigitalTwin(
      dto.fieldId,
      {
        soilMoisture: dto.soilMoisture,
        temperature: dto.temperature,
        growthStage: dto.growthStage,
        ndvi: dto.ndvi,
      },
    );

    return {
      success: true,
      digitalTwinIntegration: {
        fieldId: dto.fieldId,
        currentStatus: result.currentStatus,
        timestamp: new Date().toISOString(),
        currentConditions: {
          soilMoisture: dto.soilMoisture + "%",
          temperature: dto.temperature + "°C",
          growthStage: dto.growthStage,
          ndvi: dto.ndvi,
        },
        adjustments: result.adjustments,
        alerts: result.alerts,
        nextActions: result.nextActions,
      },
    };
  }

  /**
   * GET /planting-strategy/crops/:cropType
   * Get crop-specific planting information
   */
  @Get("crops/:cropType")
  getCropInfo(@Param("cropType") cropType: string) {
    const validCrops = [
      "wheat",
      "barley",
      "corn",
      "rice",
      "sorghum",
      "date_palm",
      "alfalfa",
    ];
    if (!validCrops.includes(cropType)) {
      throw new HttpException(
        `Invalid crop type. Valid options: ${validCrops.join(", ")}`,
        HttpStatus.BAD_REQUEST,
      );
    }

    const cropNames: Record<string, { en: string; ar: string }> = {
      wheat: { en: "Wheat", ar: "القمح" },
      barley: { en: "Barley", ar: "الشعير" },
      corn: { en: "Corn/Maize", ar: "الذرة" },
      rice: { en: "Rice", ar: "الأرز" },
      sorghum: { en: "Sorghum", ar: "الذرة الرفيعة" },
      date_palm: { en: "Date Palm", ar: "نخيل التمر" },
      alfalfa: { en: "Alfalfa", ar: "البرسيم الحجازي" },
    };

    const recommendedMethods: Record<string, string[]> = {
      wheat: ["equal_row", "wide_strip", "space_broadcasting"],
      barley: ["equal_row", "wide_strip"],
      corn: ["equal_row", "space_broadcasting"],
      rice: ["equal_row", "small_basin"],
      sorghum: ["equal_row", "space_broadcasting"],
      date_palm: ["small_basin"],
      alfalfa: ["equal_row", "wide_strip"],
    };

    const plantingSeasons: Record<
      string,
      { early: string; optimal: string; late: string }
    > = {
      wheat: {
        early: "October 15",
        optimal: "November 1-15",
        late: "December 1",
      },
      barley: {
        early: "October 10",
        optimal: "October 20 - November 10",
        late: "November 25",
      },
      corn: { early: "March 15", optimal: "April 1-15", late: "May 1" },
      rice: { early: "April 1", optimal: "April 15 - May 15", late: "June 1" },
      sorghum: { early: "March 20", optimal: "April 1-20", late: "May 10" },
      date_palm: {
        early: "February 1",
        optimal: "March 1 - April 15",
        late: "May 1",
      },
      alfalfa: {
        early: "September 15",
        optimal: "October 1-20",
        late: "November 1",
      },
    };

    return {
      success: true,
      cropInfo: {
        cropType,
        names: cropNames[cropType],
        recommendedMethods: recommendedMethods[cropType],
        plantingSeason: plantingSeasons[cropType],
        tips: this.getCropTips(cropType),
      },
    };
  }

  private getCropTips(cropType: string): string[] {
    const tips: Record<string, string[]> = {
      wheat: [
        "Plant when soil temperature is 12-15°C",
        "Avoid planting too deep in clay soils",
        "Wide strip method can increase yield by 15-20%",
        "First irrigation critical 21-25 days after emergence",
      ],
      barley: [
        "More drought-tolerant than wheat",
        "Can tolerate slightly saline soils",
        "Shorter growing season allows double cropping",
        "Requires less nitrogen than wheat",
      ],
      corn: [
        "Requires warm soil (>12°C) for germination",
        "Space broadcasting improves pollination",
        "Critical water needs at tasseling stage",
        "Heavy nitrogen feeder - split applications recommended",
      ],
      rice: [
        "Small basin method ideal for water management",
        "Requires standing water during vegetative stage",
        "Alternate wetting and drying saves water",
        "Level fields critical for uniform growth",
      ],
      sorghum: [
        "Excellent drought tolerance",
        "Good for marginal lands",
        "Deep rooting system accesses subsoil moisture",
        "Lower input requirements than corn",
      ],
      date_palm: [
        "Basin planting essential for irrigation efficiency",
        "Long-term investment (3-5 years to first harvest)",
        "Tolerant of high salinity and heat",
        "Regular irrigation critical in first 2 years",
      ],
      alfalfa: [
        "Nitrogen-fixing reduces fertilizer needs",
        "Deep rooting improves soil structure",
        "Multiple harvests per season possible",
        "Inoculate seeds before first planting",
      ],
    };

    return tips[cropType] || [];
  }
}
