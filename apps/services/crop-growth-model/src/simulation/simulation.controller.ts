// ═══════════════════════════════════════════════════════════════════════════════
// Growth Simulation Controller - مراقب محاكاة النمو
// Integrated Crop Growth Model combining Phenology, Photosynthesis, and Biomass
// ═══════════════════════════════════════════════════════════════════════════════

import { Controller, Get, Post, Body, Query } from "@nestjs/common";
import {
  ApiTags,
  ApiOperation,
  ApiResponse,
  ApiQuery,
  ApiBody,
} from "@nestjs/swagger";
import { GrowthSimulationService } from "./simulation.service";

class SimulationInput {
  cropType: string;
  sowingDate: string;
  fieldLocation?: { latitude: number; longitude: number };
  soilType?: string;
  irrigated?: boolean;
  weatherData: Array<{
    date: string;
    tmin: number;
    tmax: number;
    radiation: number;
    precipitation?: number;
  }>;
}

class QuickEstimateInput {
  cropType: string;
  avgTemperature: number;
  avgRadiation: number;
  seasonLength: number;
}

@ApiTags("simulation")
@Controller("api/v1/simulation")
export class GrowthSimulationController {
  constructor(private readonly simulationService: GrowthSimulationService) {}

  // ─────────────────────────────────────────────────────────────────────────────
  // Run Full Growth Simulation
  // تشغيل محاكاة النمو الكاملة
  // ─────────────────────────────────────────────────────────────────────────────

  @Post("run")
  @ApiOperation({
    summary: "Run full crop growth simulation",
    description: "تشغيل محاكاة نمو المحصول الكاملة مع بيانات الطقس الفعلية",
  })
  @ApiBody({
    description: "Simulation configuration and weather data",
    schema: {
      type: "object",
      properties: {
        cropType: {
          type: "string",
          example: "WHEAT",
          description: "Crop type identifier",
        },
        sowingDate: {
          type: "string",
          example: "2024-11-15",
          description: "Sowing date (YYYY-MM-DD)",
        },
        fieldLocation: {
          type: "object",
          properties: {
            latitude: { type: "number", example: 24.7136 },
            longitude: { type: "number", example: 46.6753 },
          },
        },
        irrigated: { type: "boolean", example: true },
        weatherData: {
          type: "array",
          items: {
            type: "object",
            properties: {
              date: { type: "string", example: "2024-11-15" },
              tmin: { type: "number", example: 12 },
              tmax: { type: "number", example: 25 },
              radiation: { type: "number", example: 15 },
            },
          },
        },
      },
      required: ["cropType", "sowingDate", "weatherData"],
    },
  })
  @ApiResponse({ status: 200, description: "Complete simulation results" })
  runSimulation(@Body() input: SimulationInput) {
    const config = {
      cropType: input.cropType,
      sowingDate: input.sowingDate,
      fieldLocation: input.fieldLocation,
      soilType: input.soilType,
      irrigated: input.irrigated,
    };

    return this.simulationService.runSimulation(config, input.weatherData);
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Run Demo Simulation
  // تشغيل محاكاة تجريبية
  // ─────────────────────────────────────────────────────────────────────────────

  @Get("demo")
  @ApiOperation({
    summary: "Run demo simulation with sample weather data",
    description: "تشغيل محاكاة تجريبية باستخدام بيانات طقس نموذجية",
  })
  @ApiQuery({
    name: "cropType",
    required: false,
    example: "WHEAT",
    description: "Crop type",
  })
  @ApiQuery({
    name: "sowingDate",
    required: false,
    example: "2024-11-15",
    description: "Sowing date",
  })
  @ApiQuery({
    name: "days",
    required: false,
    example: 180,
    description: "Simulation days",
  })
  @ApiQuery({
    name: "climate",
    required: false,
    example: "temperate",
    description: "Climate type",
  })
  @ApiResponse({ status: 200, description: "Demo simulation results" })
  runDemoSimulation(
    @Query("cropType") cropType: string = "WHEAT",
    @Query("sowingDate") sowingDate: string = "2024-11-15",
    @Query("days") days: string = "180",
    @Query("climate") climate: string = "temperate",
  ) {
    const numDays = parseInt(days, 10) || 180;
    const climateType = climate as "temperate" | "tropical" | "arid";

    // Generate sample weather
    const weatherData = this.simulationService.generateSampleWeather(
      sowingDate,
      numDays,
      climateType,
    );

    const config = {
      cropType,
      sowingDate,
      irrigated: true,
    };

    const result = this.simulationService.runSimulation(config, weatherData);

    return {
      ...result,
      note: "This is a demo simulation using generated weather data",
      noteAr: "هذه محاكاة تجريبية باستخدام بيانات طقس مولدة",
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Quick Yield Estimate
  // تقدير سريع للغلة
  // ─────────────────────────────────────────────────────────────────────────────

  @Post("quick-estimate")
  @ApiOperation({
    summary: "Get quick yield estimate without full simulation",
    description: "تقدير سريع للغلة دون تشغيل محاكاة كاملة",
  })
  @ApiBody({
    description: "Quick estimate parameters",
    schema: {
      type: "object",
      properties: {
        cropType: { type: "string", example: "CORN", description: "Crop type" },
        avgTemperature: {
          type: "number",
          example: 25,
          description: "Average temperature (°C)",
        },
        avgRadiation: {
          type: "number",
          example: 18,
          description: "Average radiation (MJ m⁻² day⁻¹)",
        },
        seasonLength: {
          type: "number",
          example: 120,
          description: "Growing season length (days)",
        },
      },
      required: ["cropType", "avgTemperature", "avgRadiation", "seasonLength"],
    },
  })
  @ApiResponse({ status: 200, description: "Quick yield estimate" })
  getQuickEstimate(@Body() input: QuickEstimateInput) {
    return {
      input,
      result: this.simulationService.quickYieldEstimate(
        input.cropType,
        input.avgTemperature,
        input.avgRadiation,
        input.seasonLength,
      ),
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Generate Sample Weather
  // توليد بيانات طقس نموذجية
  // ─────────────────────────────────────────────────────────────────────────────

  @Get("weather/sample")
  @ApiOperation({
    summary: "Generate sample weather data",
    description: "توليد بيانات طقس نموذجية للمحاكاة",
  })
  @ApiQuery({
    name: "startDate",
    required: false,
    example: "2024-11-15",
    description: "Start date",
  })
  @ApiQuery({
    name: "days",
    required: false,
    example: 30,
    description: "Number of days",
  })
  @ApiQuery({
    name: "climate",
    required: false,
    example: "tropical",
    description: "Climate type",
  })
  @ApiResponse({ status: 200, description: "Sample weather data" })
  generateSampleWeather(
    @Query("startDate") startDate: string = "2024-11-15",
    @Query("days") days: string = "30",
    @Query("climate") climate: string = "temperate",
  ) {
    const numDays = parseInt(days, 10) || 30;
    const climateType = climate as "temperate" | "tropical" | "arid";

    const weatherData = this.simulationService.generateSampleWeather(
      startDate,
      numDays,
      climateType,
    );

    return {
      parameters: {
        startDate,
        days: numDays,
        climate: climateType,
      },
      weatherData,
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Model Information
  // الحصول على معلومات النموذج
  // ─────────────────────────────────────────────────────────────────────────────

  @Get("info")
  @ApiOperation({
    summary: "Get crop growth model information",
    description: "الحصول على معلومات حول نموذج نمو المحاصيل",
  })
  @ApiResponse({ status: 200, description: "Model information" })
  getModelInfo() {
    return this.simulationService.getModelInfo();
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Health Check
  // فحص صحة الخدمة
  // ─────────────────────────────────────────────────────────────────────────────

  @Get("health")
  @ApiOperation({
    summary: "Simulation service health check",
    description: "فحص صحة خدمة المحاكاة",
  })
  @ApiResponse({ status: 200, description: "Service is healthy" })
  healthCheck() {
    return {
      status: "healthy",
      service: "growth-simulation",
      timestamp: new Date().toISOString(),
      version: "1.0.0",
      components: ["phenology", "photosynthesis", "biomass"],
    };
  }
}
