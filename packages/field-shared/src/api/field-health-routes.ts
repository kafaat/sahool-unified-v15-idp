/**
 * Field Health API Routes
 * Comprehensive field health analysis based on NDVI, sensor data, and weather
 *
 * Migrated from field-ops Python service to TypeScript
 * Port: 3000 (field-management-service)
 */

import { Router, Request, Response } from "express";

const router = Router();

// ============================================================================
// Types and Interfaces
// ============================================================================

interface SensorData {
  soil_moisture: number; // 0-100%
  temperature: number; // -50 to 60°C
  humidity: number; // 0-100%
}

interface NDVIData {
  ndvi_value: number; // -1 to 1
  image_date?: string;
  cloud_coverage?: number; // 0-100%
}

interface WeatherData {
  precipitation: number; // mm
  wind_speed?: number; // km/h
  forecast_days?: number; // 1-14
}

interface FieldHealthRequest {
  field_id: string;
  crop_type: string;
  sensor_data: SensorData;
  ndvi_data: NDVIData;
  weather_data: WeatherData;
}

interface RiskFactor {
  type: string;
  severity: "low" | "medium" | "high" | "critical";
  description_ar: string;
  description_en: string;
  impact_score: number;
}

interface FieldHealthResponse {
  field_id: string;
  crop_type: string;
  overall_health_score: number;
  health_status: string;
  health_status_ar: string;

  // Component scores
  ndvi_score: number;
  soil_moisture_score: number;
  weather_score: number;
  sensor_anomaly_score: number;

  risk_factors: RiskFactor[];
  recommendations_ar: string[];
  recommendations_en: string[];

  analysis_timestamp: string;
  metadata: {
    ndvi_weight: number;
    soil_moisture_weight: number;
    weather_weight: number;
    sensor_anomaly_weight: number;
    total_risk_factors: number;
    critical_risks: number;
    high_risks: number;
  };
}

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Calculate NDVI score from NDVI data
 */
function calculateNdviScore(ndviData: NDVIData, cropType: string): number {
  const ndvi = ndviData.ndvi_value;

  let score: number;

  if (ndvi < 0) {
    score = 0;
  } else if (ndvi < 0.2) {
    score = (ndvi / 0.2) * 30; // 0-30 range
  } else if (ndvi < 0.4) {
    score = 30 + ((ndvi - 0.2) / 0.2) * 30; // 30-60 range
  } else if (ndvi < 0.6) {
    score = 60 + ((ndvi - 0.4) / 0.2) * 25; // 60-85 range
  } else {
    score = 85 + ((ndvi - 0.6) / 0.4) * 15; // 85-100 range
  }

  // Adjust for cloud coverage
  if (ndviData.cloud_coverage && ndviData.cloud_coverage > 30) {
    score = score * (1 - (ndviData.cloud_coverage - 30) / 100);
  }

  return Math.min(100, Math.max(0, score));
}

/**
 * Calculate soil moisture score based on crop type
 */
function calculateSoilMoistureScore(
  sensorData: SensorData,
  cropType: string,
): number {
  const moisture = sensorData.soil_moisture;

  // Optimal moisture ranges by crop type
  const optimalRanges: Record<string, [number, number]> = {
    wheat: [25, 35],
    corn: [30, 40],
    rice: [60, 80],
    tomato: [25, 35],
    potato: [30, 40],
    cotton: [20, 30],
    default: [25, 40],
  };

  const [optimalMin, optimalMax] =
    optimalRanges[cropType.toLowerCase()] || optimalRanges.default;

  let score: number;

  if (moisture >= optimalMin && moisture <= optimalMax) {
    score = 100; // Optimal
  } else if (moisture < optimalMin) {
    // Too dry
    if (moisture < optimalMin * 0.5) {
      score = 20; // Severe drought
    } else {
      score = 50 + ((moisture - optimalMin * 0.5) / (optimalMin * 0.5)) * 50;
    }
  } else {
    // Too wet
    if (moisture > optimalMax * 1.5) {
      score = 20; // Severe waterlogging
    } else {
      score = 100 - ((moisture - optimalMax) / (optimalMax * 0.5)) * 50;
    }
  }

  return Math.min(100, Math.max(0, score));
}

/**
 * Calculate weather suitability score
 */
function calculateWeatherScore(
  weatherData: WeatherData,
  cropType: string,
): number {
  let score = 100;

  const precipitation = weatherData.precipitation;

  if (precipitation === 0) {
    score -= 15; // No rain
  } else if (precipitation > 50) {
    score -= 25; // Very heavy rain
  } else if (precipitation > 30) {
    score -= 10; // Heavy rain
  }

  // Evaluate wind speed
  if (weatherData.wind_speed) {
    if (weatherData.wind_speed > 50) {
      score -= 30; // Storm winds
    } else if (weatherData.wind_speed > 30) {
      score -= 15; // Strong winds
    }
  }

  return Math.min(100, Math.max(0, score));
}

/**
 * Detect sensor anomalies
 */
function calculateSensorAnomalyScore(sensorData: SensorData): number {
  let score = 100;

  // Temperature out of reasonable range
  if (sensorData.temperature < -10 || sensorData.temperature > 50) {
    score -= 30;
  } else if (sensorData.temperature < 0 || sensorData.temperature > 45) {
    score -= 15;
  }

  // Inconsistent humidity
  if (sensorData.humidity < 10 || sensorData.humidity > 95) {
    score -= 20;
  }

  // Check consistency between humidity and soil moisture
  if (sensorData.humidity > 80 && sensorData.soil_moisture < 20) {
    score -= 15; // High air humidity but dry soil
  }

  return Math.min(100, Math.max(0, score));
}

/**
 * Identify risk factors based on analysis
 */
function identifyRiskFactors(
  request: FieldHealthRequest,
  ndviScore: number,
  soilScore: number,
  weatherScore: number,
  sensorScore: number,
): RiskFactor[] {
  const risks: RiskFactor[] = [];

  // Vegetation stress risk
  if (ndviScore < 40) {
    risks.push({
      type: "vegetation_stress",
      severity: ndviScore < 20 ? "critical" : "high",
      description_ar: "ضعف شديد في النمو النباتي يتطلب تدخل فوري",
      description_en:
        "Severe vegetation stress requiring immediate intervention",
      impact_score: 100 - ndviScore,
    });
  } else if (ndviScore < 60) {
    risks.push({
      type: "vegetation_stress",
      severity: "medium",
      description_ar: "إجهاد نباتي متوسط قد يؤثر على الإنتاجية",
      description_en: "Moderate vegetation stress may affect productivity",
      impact_score: 60 - ndviScore,
    });
  }

  // Drought or waterlogging risk
  if (soilScore < 40) {
    const moisture = request.sensor_data.soil_moisture;
    if (moisture < 20) {
      risks.push({
        type: "drought",
        severity: "high",
        description_ar: "جفاف شديد في التربة يتطلب ري فوري",
        description_en: "Severe soil drought requiring immediate irrigation",
        impact_score: 80,
      });
    } else {
      risks.push({
        type: "waterlogging",
        severity: "high",
        description_ar: "رطوبة زائدة في التربة قد تسبب تعفن الجذور",
        description_en: "Excessive soil moisture may cause root rot",
        impact_score: 70,
      });
    }
  }

  // Adverse weather risk
  if (weatherScore < 60) {
    if (request.weather_data.precipitation > 50) {
      risks.push({
        type: "heavy_rain",
        severity: "medium",
        description_ar: "أمطار غزيرة قد تؤثر على العمليات الزراعية",
        description_en: "Heavy rainfall may affect agricultural operations",
        impact_score: 50,
      });
    }

    if (
      request.weather_data.wind_speed &&
      request.weather_data.wind_speed > 40
    ) {
      risks.push({
        type: "strong_winds",
        severity: "high",
        description_ar: "رياح قوية قد تضر بالمحاصيل",
        description_en: "Strong winds may damage crops",
        impact_score: 60,
      });
    }
  }

  // Sensor malfunction risk
  if (sensorScore < 70) {
    risks.push({
      type: "sensor_anomaly",
      severity: "low",
      description_ar: "قراءات شاذة من الأجهزة تحتاج للمراجعة",
      description_en: "Anomalous sensor readings need review",
      impact_score: 30,
    });
  }

  return risks;
}

/**
 * Generate recommendations based on health analysis
 */
function generateRecommendations(
  request: FieldHealthRequest,
  overallScore: number,
  riskFactors: RiskFactor[],
  soilScore: number,
  ndviScore: number,
): { recommendations_ar: string[]; recommendations_en: string[] } {
  const recommendations_ar: string[] = [];
  const recommendations_en: string[] = [];

  // Overall health recommendations
  if (overallScore < 50) {
    recommendations_ar.push("⚠️ الحقل يحتاج لتدخل فوري لتحسين الصحة العامة");
    recommendations_en.push(
      "⚠️ Field requires immediate intervention to improve overall health",
    );
  }

  // Soil moisture recommendations
  const moisture = request.sensor_data.soil_moisture;
  if (moisture < 20) {
    recommendations_ar.push("💧 تنفيذ خطة ري عاجلة لمعالجة الجفاف الشديد");
    recommendations_en.push(
      "💧 Implement emergency irrigation plan to address severe drought",
    );
  } else if (moisture < 30) {
    recommendations_ar.push("💧 زيادة معدل الري للوصول للرطوبة المثلى");
    recommendations_en.push(
      "💧 Increase irrigation rate to reach optimal moisture",
    );
  } else if (moisture > 60) {
    recommendations_ar.push("💧 تقليل الري وتحسين الصرف لمنع تعفن الجذور");
    recommendations_en.push(
      "💧 Reduce irrigation and improve drainage to prevent root rot",
    );
  }

  // Vegetation growth recommendations
  if (ndviScore < 40) {
    recommendations_ar.push("🌱 فحص نظام التسميد وإجراء تحليل للتربة");
    recommendations_en.push(
      "🌱 Check fertilization system and conduct soil analysis",
    );
    recommendations_ar.push("🔍 فحص المحاصيل للكشف عن الآفات والأمراض");
    recommendations_en.push("🔍 Inspect crops for pests and diseases");
  }

  // Weather recommendations
  if (request.weather_data.precipitation > 40) {
    recommendations_ar.push("☔ تأجيل عمليات الرش والتسميد حتى تحسن الطقس");
    recommendations_en.push(
      "☔ Postpone spraying and fertilization until weather improves",
    );
  }

  if (request.weather_data.wind_speed && request.weather_data.wind_speed > 40) {
    recommendations_ar.push("💨 تركيب مصدات رياح لحماية المحاصيل");
    recommendations_en.push("💨 Install windbreaks to protect crops");
  }

  // Maintenance recommendations
  if (riskFactors.some((r) => r.type === "sensor_anomaly")) {
    recommendations_ar.push(
      "🔧 فحص وصيانة أجهزة الاستشعار للتأكد من دقة القراءات",
    );
    recommendations_en.push(
      "🔧 Check and maintain sensors to ensure accurate readings",
    );
  }

  // General improvement recommendations
  if (overallScore < 70) {
    recommendations_ar.push("📊 زيادة تكرار المراقبة لتتبع تحسن الصحة");
    recommendations_en.push(
      "📊 Increase monitoring frequency to track health improvement",
    );
  }

  return { recommendations_ar, recommendations_en };
}

/**
 * Get health status from score
 */
function getHealthStatus(score: number): { status: string; status_ar: string } {
  if (score >= 85) return { status: "excellent", status_ar: "ممتاز" };
  if (score >= 70) return { status: "good", status_ar: "جيد" };
  if (score >= 50) return { status: "fair", status_ar: "مقبول" };
  if (score >= 30) return { status: "poor", status_ar: "ضعيف" };
  return { status: "critical", status_ar: "حرج" };
}

// ============================================================================
// API Endpoint
// ============================================================================

/**
 * POST /api/v1/field-health
 * Analyze agricultural field health
 */
router.post("/field-health", async (req: Request, res: Response) => {
  try {
    const request = req.body as FieldHealthRequest;

    // Validate required fields
    if (
      !request.field_id ||
      !request.crop_type ||
      !request.sensor_data ||
      !request.ndvi_data ||
      !request.weather_data
    ) {
      return res.status(400).json({
        success: false,
        error:
          "Missing required fields: field_id, crop_type, sensor_data, ndvi_data, weather_data",
      });
    }

    // Validate sensor data ranges
    const { soil_moisture, temperature, humidity } = request.sensor_data;
    if (soil_moisture < 0 || soil_moisture > 100) {
      return res.status(400).json({
        success: false,
        error: "Invalid input data: soil_moisture must be between 0 and 100",
      });
    }
    if (temperature < -50 || temperature > 60) {
      return res.status(400).json({
        success: false,
        error: "Invalid input data: temperature must be between -50 and 60",
      });
    }
    if (humidity < 0 || humidity > 100) {
      return res.status(400).json({
        success: false,
        error: "Invalid input data: humidity must be between 0 and 100",
      });
    }

    // Validate NDVI value
    if (request.ndvi_data.ndvi_value < -1 || request.ndvi_data.ndvi_value > 1) {
      return res.status(400).json({
        success: false,
        error: "Invalid input data: ndvi_value must be between -1 and 1",
      });
    }

    // Calculate component scores
    const ndviScore = calculateNdviScore(request.ndvi_data, request.crop_type);
    const soilMoistureScore = calculateSoilMoistureScore(
      request.sensor_data,
      request.crop_type,
    );
    const weatherScore = calculateWeatherScore(
      request.weather_data,
      request.crop_type,
    );
    const sensorAnomalyScore = calculateSensorAnomalyScore(request.sensor_data);

    // Calculate weighted overall score
    const overallHealthScore =
      ndviScore * 0.4 +
      soilMoistureScore * 0.25 +
      weatherScore * 0.2 +
      sensorAnomalyScore * 0.15;

    // Determine health status
    const { status: healthStatus, status_ar: healthStatusAr } =
      getHealthStatus(overallHealthScore);

    // Identify risk factors
    const riskFactors = identifyRiskFactors(
      request,
      ndviScore,
      soilMoistureScore,
      weatherScore,
      sensorAnomalyScore,
    );

    // Generate recommendations
    const { recommendations_ar, recommendations_en } = generateRecommendations(
      request,
      overallHealthScore,
      riskFactors,
      soilMoistureScore,
      ndviScore,
    );

    // Build response
    const response: FieldHealthResponse = {
      field_id: request.field_id,
      crop_type: request.crop_type,
      overall_health_score: Math.round(overallHealthScore * 100) / 100,
      health_status: healthStatus,
      health_status_ar: healthStatusAr,
      ndvi_score: Math.round(ndviScore * 100) / 100,
      soil_moisture_score: Math.round(soilMoistureScore * 100) / 100,
      weather_score: Math.round(weatherScore * 100) / 100,
      sensor_anomaly_score: Math.round(sensorAnomalyScore * 100) / 100,
      risk_factors: riskFactors,
      recommendations_ar,
      recommendations_en,
      analysis_timestamp: new Date().toISOString(),
      metadata: {
        ndvi_weight: 0.4,
        soil_moisture_weight: 0.25,
        weather_weight: 0.2,
        sensor_anomaly_weight: 0.15,
        total_risk_factors: riskFactors.length,
        critical_risks: riskFactors.filter((r) => r.severity === "critical")
          .length,
        high_risks: riskFactors.filter((r) => r.severity === "high").length,
      },
    };

    res.json({
      success: true,
      data: response,
    });
  } catch (error) {
    console.error("Error in field health analysis:", error);
    res.status(500).json({
      success: false,
      error: "Internal server error during health analysis",
      detail: error instanceof Error ? error.message : "Unknown error",
    });
  }
});

export { router as fieldHealthRoutes };
