/**
 * SAHOOL Action Windows Calculator
 * حاسبة نوافذ العمل
 *
 * Utility functions for calculating optimal windows for agricultural activities
 */

import type {
  WeatherCondition,
  WindowStatus,
  SprayWindowCriteria,
  WindowCalculationResult,
  SoilMoistureData,
  ETData,
  IrrigationNeed,
} from "../types/action-windows";

// ═══════════════════════════════════════════════════════════════════════════
// Default Criteria
// ═══════════════════════════════════════════════════════════════════════════

export const DEFAULT_SPRAY_CRITERIA: SprayWindowCriteria = {
  windSpeedMax: 15, // km/h
  windSpeedMin: 3, // km/h
  temperatureMin: 10, // °C
  temperatureMax: 30, // °C
  humidityMin: 50, // %
  humidityMax: 90, // %
  rainProbabilityMax: 20, // %
  minDuration: 2, // hours
};

// ═══════════════════════════════════════════════════════════════════════════
// Spray Window Calculator
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Calculate if weather conditions are suitable for spraying
 * حساب ما إذا كانت الظروف الجوية مناسبة للرش
 */
export function calculateSprayWindow(
  weather: WeatherCondition,
  criteria: Partial<SprayWindowCriteria> = {},
): WindowCalculationResult {
  const rules = { ...DEFAULT_SPRAY_CRITERIA, ...criteria };

  const checks = {
    windSpeed:
      weather.windSpeed >= rules.windSpeedMin &&
      weather.windSpeed <= rules.windSpeedMax,
    temperature:
      weather.temperature >= rules.temperatureMin &&
      weather.temperature <= rules.temperatureMax,
    humidity:
      weather.humidity >= rules.humidityMin &&
      weather.humidity <= rules.humidityMax,
    rain:
      weather.rainProbability <= rules.rainProbabilityMax &&
      weather.precipitation === 0,
  };

  const warnings: string[] = [];
  const warningsAr: string[] = [];
  const recommendations: string[] = [];
  const recommendationsAr: string[] = [];

  // Check wind speed
  if (!checks.windSpeed) {
    if (weather.windSpeed < rules.windSpeedMin) {
      warnings.push("Wind speed too low - spray drift may occur");
      warningsAr.push("سرعة الرياح منخفضة جداً - قد يحدث انجراف للرش");
    } else {
      warnings.push(
        `Wind speed too high (${weather.windSpeed} km/h) - avoid spraying`,
      );
      warningsAr.push(
        `سرعة الرياح عالية جداً (${weather.windSpeed} كم/ساعة) - تجنب الرش`,
      );
    }
  }

  // Check temperature
  if (!checks.temperature) {
    if (weather.temperature < rules.temperatureMin) {
      warnings.push(
        `Temperature too low (${weather.temperature}°C) - reduced effectiveness`,
      );
      warningsAr.push(
        `درجة الحرارة منخفضة جداً (${weather.temperature}°م) - فعالية منخفضة`,
      );
    } else {
      warnings.push(
        `Temperature too high (${weather.temperature}°C) - evaporation risk`,
      );
      warningsAr.push(
        `درجة الحرارة مرتفعة جداً (${weather.temperature}°م) - خطر التبخر`,
      );
    }
  }

  // Check humidity
  if (!checks.humidity) {
    if (weather.humidity < rules.humidityMin) {
      warnings.push(
        `Humidity too low (${weather.humidity}%) - rapid evaporation`,
      );
      warningsAr.push(`الرطوبة منخفضة جداً (${weather.humidity}%) - تبخر سريع`);
    } else {
      warnings.push(`Humidity too high (${weather.humidity}%) - slow drying`);
      warningsAr.push(`الرطوبة مرتفعة جداً (${weather.humidity}%) - جفاف بطيء`);
    }
  }

  // Check rain
  if (!checks.rain) {
    if (weather.precipitation > 0) {
      warnings.push("Rain detected - spraying not recommended");
      warningsAr.push("تم اكتشاف أمطار - الرش غير موصى به");
    } else {
      warnings.push(
        `High rain probability (${weather.rainProbability}%) - delay spraying`,
      );
      warningsAr.push(
        `احتمال أمطار عالٍ (${weather.rainProbability}%) - أجل الرش`,
      );
    }
  }

  // Add recommendations
  if (
    checks.windSpeed &&
    checks.temperature &&
    checks.humidity &&
    checks.rain
  ) {
    recommendations.push("Excellent conditions for spraying");
    recommendationsAr.push("ظروف ممتازة للرش");
    recommendations.push("Ensure equipment is calibrated correctly");
    recommendationsAr.push("تأكد من معايرة المعدات بشكل صحيح");
  } else if (checks.windSpeed && checks.temperature) {
    recommendations.push("Fair conditions - monitor weather closely");
    recommendationsAr.push("ظروف مقبولة - راقب الطقس عن كثب");
  } else {
    recommendations.push("Consider postponing until conditions improve");
    recommendationsAr.push("فكر في التأجيل حتى تتحسن الظروف");
  }

  // Calculate score (0-100)
  const scores = {
    windSpeed: checks.windSpeed ? 25 : 0,
    temperature: checks.temperature ? 25 : 0,
    humidity: checks.humidity ? 25 : 0,
    rain: checks.rain ? 25 : 0,
  };

  const totalScore = Object.values(scores).reduce(
    (sum, score) => sum + score,
    0,
  );

  // Determine status
  let status: WindowStatus;
  if (totalScore >= 75) {
    status = "optimal";
  } else if (totalScore >= 50) {
    status = "marginal";
  } else {
    status = "avoid";
  }

  return {
    status,
    score: totalScore,
    suitability: checks,
    warnings,
    warningsAr,
    recommendations,
    recommendationsAr,
  };
}

// ═══════════════════════════════════════════════════════════════════════════
// Irrigation Need Calculator
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Calculate irrigation needs based on soil moisture and ET
 * حساب احتياجات الري بناءً على رطوبة التربة والتبخر
 */
export function calculateIrrigationNeed(
  soilMoisture: SoilMoistureData,
  et: ETData,
  _fieldAreaHectares: number = 1,
): IrrigationNeed {
  const { current, target, fieldCapacity, wiltingPoint } = soilMoisture;
  const { et0, etc, kc } = et;

  // Calculate crop evapotranspiration if not provided
  const cropET = etc || et0 * (kc || 1.0);

  // Calculate soil moisture deficit
  const moistureDeficit = Math.max(0, target - current);

  // Convert moisture deficit to mm (assuming 1m soil depth)
  const soilDepthMm = 1000; // 1 meter
  const deficitMm = (moistureDeficit / 100) * soilDepthMm;

  // Add ET to deficit
  const totalDeficitMm = deficitMm + cropET;

  // Calculate recommended irrigation amount (mm)
  const recommendedAmount = Math.max(0, totalDeficitMm);

  // Calculate duration (assuming 5mm/hour irrigation rate)
  const irrigationRate = 5; // mm/hour
  const recommendedDuration = Math.ceil(recommendedAmount / irrigationRate);

  // Determine urgency
  let urgency: IrrigationNeed["urgency"];
  const stressLevel = (current - wiltingPoint) / (fieldCapacity - wiltingPoint);

  if (stressLevel < 0.3) {
    urgency = "critical";
  } else if (stressLevel < 0.5) {
    urgency = "high";
  } else if (stressLevel < 0.7) {
    urgency = "medium";
  } else if (current < target) {
    urgency = "low";
  } else {
    urgency = "none";
  }

  // Calculate next irrigation date
  const daysUntilNextIrrigation = Math.max(
    1,
    Math.floor((current - target) / cropET),
  );
  const nextIrrigationDate = new Date();
  nextIrrigationDate.setDate(
    nextIrrigationDate.getDate() + daysUntilNextIrrigation,
  );

  // Generate reasoning
  let reasoning = "";
  let reasoningAr = "";

  if (urgency === "critical") {
    reasoning = `Soil moisture critically low (${current.toFixed(1)}%). Immediate irrigation required to prevent crop stress.`;
    reasoningAr = `رطوبة التربة منخفضة بشكل حرج (${current.toFixed(1)}%). الري الفوري مطلوب لمنع إجهاد المحصول.`;
  } else if (urgency === "high") {
    reasoning = `Soil moisture low (${current.toFixed(1)}%). Irrigation needed within 24 hours.`;
    reasoningAr = `رطوبة التربة منخفضة (${current.toFixed(1)}%). الري مطلوب خلال 24 ساعة.`;
  } else if (urgency === "medium") {
    reasoning = `Soil moisture below target (${current.toFixed(1)}% vs ${target.toFixed(1)}%). Schedule irrigation soon.`;
    reasoningAr = `رطوبة التربة أقل من المستوى المستهدف (${current.toFixed(1)}% مقابل ${target.toFixed(1)}%). جدولة الري قريباً.`;
  } else if (urgency === "low") {
    reasoning = `Soil moisture adequate (${current.toFixed(1)}%). Monitor and prepare for next irrigation.`;
    reasoningAr = `رطوبة التربة كافية (${current.toFixed(1)}%). راقب واستعد للري القادم.`;
  } else {
    reasoning = `Soil moisture optimal (${current.toFixed(1)}%). No irrigation needed.`;
    reasoningAr = `رطوبة التربة مثالية (${current.toFixed(1)}%). لا حاجة للري.`;
  }

  return {
    fieldId: "", // Will be set by caller
    urgency,
    recommendedAmount,
    recommendedDuration,
    nextIrrigationDate: nextIrrigationDate.toISOString(),
    soilMoistureDeficit: totalDeficitMm,
    currentMoisture: current,
    targetMoisture: target,
    et0: cropET,
    reasoning,
    reasoningAr,
  };
}

// ═══════════════════════════════════════════════════════════════════════════
// Optimal Window Finder
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Find the optimal window from a list of weather conditions
 * إيجاد النافذة المثلى من قائمة ظروف الطقس
 */
export function getOptimalWindow(
  conditions: WeatherCondition[],
  actionType: "spray" | "irrigate" = "spray",
  criteria?: Partial<SprayWindowCriteria>,
): WeatherCondition | null {
  if (conditions.length === 0) return null;

  if (actionType === "spray") {
    const results = conditions.map((condition) => ({
      condition,
      result: calculateSprayWindow(condition, criteria),
    }));

    // Sort by score descending
    results.sort((a, b) => b.result.score - a.result.score);

    // Return best condition if it's at least marginal
    const best = results[0];
    if (best && best.result.status !== "avoid") {
      return best.condition;
    }
  } else {
    // For irrigation, prefer cooler temperatures and lower wind
    const scored = conditions.map((condition) => {
      let score = 100;

      // Prefer morning or evening (cooler)
      const hour = new Date(condition.timestamp).getHours();
      if (hour >= 6 && hour <= 9)
        score += 20; // Early morning
      else if (hour >= 17 && hour <= 20)
        score += 15; // Evening
      else if (hour >= 10 && hour <= 16) score -= 20; // Midday

      // Lower temperature is better
      if (condition.temperature < 25) score += 15;
      else if (condition.temperature > 30) score -= 15;

      // Lower wind is better
      if (condition.windSpeed < 10) score += 10;
      else if (condition.windSpeed > 20) score -= 10;

      // No rain
      if (condition.rainProbability < 10) score += 10;
      else if (condition.rainProbability > 50) score -= 20;

      return { condition, score };
    });

    scored.sort((a, b) => b.score - a.score);
    return scored[0]?.condition || null;
  }

  return null;
}

// ═══════════════════════════════════════════════════════════════════════════
// Helper Functions
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Calculate the Penman-Monteith ET0 (simplified version)
 * حساب التبخر المرجعي بطريقة بنمان-مونتيث (نسخة مبسطة)
 */
export function calculateET0(
  temperature: number,
  humidity: number,
  windSpeed: number,
  solarRadiation: number = 20, // MJ/m²/day (default)
): number {
  // Simplified Hargreaves equation for ET0
  // ET0 ≈ 0.0023 × (Tmean + 17.8) × (Tmax - Tmin)^0.5 × Ra
  // For hourly data, we use a simplified approach

  const vaporPressureDeficit = calculateVaporPressureDeficit(
    temperature,
    humidity,
  );
  const windFactor = 1 + windSpeed / 100;

  // Simplified ET0 calculation (mm/day)
  const et0 =
    (0.408 * solarRadiation * vaporPressureDeficit * windFactor) /
    (temperature + 273);

  return Math.max(0, et0);
}

/**
 * Calculate vapor pressure deficit
 */
function calculateVaporPressureDeficit(
  temperature: number,
  humidity: number,
): number {
  // Saturation vapor pressure (kPa)
  const es = 0.6108 * Math.exp((17.27 * temperature) / (temperature + 237.3));

  // Actual vapor pressure (kPa)
  const ea = (humidity / 100) * es;

  // Vapor pressure deficit (kPa)
  return Math.max(0, es - ea);
}

/**
 * Group consecutive hours into windows
 * تجميع الساعات المتتالية في نوافذ
 */
export function groupIntoWindows(
  conditions: Array<{ timestamp: string; status: WindowStatus }>,
  minDuration: number = 2,
): Array<{
  startTime: string;
  endTime: string;
  status: WindowStatus;
  duration: number;
}> {
  const windows: Array<{
    startTime: string;
    endTime: string;
    status: WindowStatus;
    duration: number;
  }> = [];

  if (conditions.length === 0) return windows;

  const firstCondition = conditions[0];
  if (!firstCondition) return windows;

  let currentWindow = {
    startTime: firstCondition.timestamp,
    endTime: firstCondition.timestamp,
    status: firstCondition.status,
    duration: 1,
  };

  for (let i = 1; i < conditions.length; i++) {
    const prev = conditions[i - 1];
    const curr = conditions[i];

    if (!prev || !curr) continue;

    const prevTime = new Date(prev.timestamp);
    const currTime = new Date(curr.timestamp);
    const hoursDiff =
      (currTime.getTime() - prevTime.getTime()) / (1000 * 60 * 60);

    // If same status and consecutive hours, extend window
    if (curr.status === currentWindow.status && hoursDiff <= 1) {
      currentWindow.endTime = curr.timestamp;
      currentWindow.duration++;
    } else {
      // Save current window if it meets minimum duration
      if (currentWindow.duration >= minDuration) {
        windows.push({ ...currentWindow });
      }

      // Start new window
      currentWindow = {
        startTime: curr.timestamp,
        endTime: curr.timestamp,
        status: curr.status,
        duration: 1,
      };
    }
  }

  // Add last window if it meets minimum duration
  if (currentWindow.duration >= minDuration) {
    windows.push(currentWindow);
  }

  return windows;
}
