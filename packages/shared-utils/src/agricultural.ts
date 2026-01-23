/**
 * Agricultural Utility Functions
 * دوال زراعية مساعدة
 *
 * Domain-specific utilities for the SAHOOL agricultural platform.
 * أدوات خاصة بالمجال لمنصة سهول الزراعية.
 */

// ─────────────────────────────────────────────────────────────────────────────
// Coordinate Utilities
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Geographic coordinate
 * إحداثية جغرافية
 */
export interface Coordinate {
  /** خط العرض - Latitude (-90 to 90) */
  latitude: number;
  /** خط الطول - Longitude (-180 to 180) */
  longitude: number;
}

/**
 * Validate geographic coordinates
 * التحقق من صحة الإحداثيات الجغرافية
 *
 * @param lat - خط العرض - Latitude
 * @param lng - خط الطول - Longitude
 * @returns هل الإحداثيات صالحة - True if valid
 */
export function isValidCoordinate(lat: number, lng: number): boolean {
  return (
    typeof lat === "number" &&
    typeof lng === "number" &&
    !Number.isNaN(lat) &&
    !Number.isNaN(lng) &&
    lat >= -90 &&
    lat <= 90 &&
    lng >= -180 &&
    lng <= 180
  );
}

/**
 * Check if coordinates are within Middle East region
 * التحقق مما إذا كانت الإحداثيات ضمن منطقة الشرق الأوسط
 *
 * Approximate bounds for Middle East agricultural zones:
 * Lat: 12°N to 42°N, Lng: 24°E to 63°E
 */
export function isMiddleEastCoordinate(lat: number, lng: number): boolean {
  return isValidCoordinate(lat, lng) && lat >= 12 && lat <= 42 && lng >= 24 && lng <= 63;
}

/**
 * Check if coordinates are within Yemen
 * التحقق مما إذا كانت الإحداثيات ضمن اليمن
 *
 * Approximate bounds for Yemen:
 * Lat: 12°N to 19°N, Lng: 42°E to 54°E
 */
export function isYemenCoordinate(lat: number, lng: number): boolean {
  return isValidCoordinate(lat, lng) && lat >= 12 && lat <= 19 && lng >= 42 && lng <= 54;
}

/**
 * Calculate distance between two coordinates (Haversine formula)
 * حساب المسافة بين إحداثيتين (صيغة هافرسين)
 *
 * @param coord1 - الإحداثية الأولى - First coordinate
 * @param coord2 - الإحداثية الثانية - Second coordinate
 * @returns المسافة بالكيلومترات - Distance in kilometers
 */
export function calculateDistance(coord1: Coordinate, coord2: Coordinate): number {
  const R = 6371; // Earth's radius in km
  const dLat = toRadians(coord2.latitude - coord1.latitude);
  const dLng = toRadians(coord2.longitude - coord1.longitude);

  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(toRadians(coord1.latitude)) *
      Math.cos(toRadians(coord2.latitude)) *
      Math.sin(dLng / 2) *
      Math.sin(dLng / 2);

  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}

/**
 * Convert degrees to radians
 * تحويل الدرجات إلى راديان
 */
function toRadians(degrees: number): number {
  return degrees * (Math.PI / 180);
}

// ─────────────────────────────────────────────────────────────────────────────
// Area Calculations
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Area unit type
 * نوع وحدة المساحة
 */
export type AreaUnit = "hectare" | "dunum" | "feddan" | "sqm" | "acre";

/**
 * Conversion factors to hectares
 * عوامل التحويل إلى هكتار
 */
const AREA_TO_HECTARE: Record<AreaUnit, number> = {
  hectare: 1,
  dunum: 0.1, // 1 dunum = 1000 sqm = 0.1 ha
  feddan: 0.42, // Egyptian feddan ≈ 0.42 ha
  sqm: 0.0001, // 1 sqm = 0.0001 ha
  acre: 0.4047, // 1 acre ≈ 0.4047 ha
};

/**
 * Convert area between units
 * تحويل المساحة بين الوحدات
 *
 * @param value - القيمة - Area value
 * @param from - من - Source unit
 * @param to - إلى - Target unit
 * @returns المساحة المحولة - Converted area
 */
export function convertArea(value: number, from: AreaUnit, to: AreaUnit): number {
  const hectares = value * AREA_TO_HECTARE[from];
  return hectares / AREA_TO_HECTARE[to];
}

/**
 * Calculate polygon area from coordinates (Shoelace formula)
 * حساب مساحة المضلع من الإحداثيات
 *
 * @param coordinates - الإحداثيات - Array of coordinates forming the polygon
 * @returns المساحة بالهكتار - Area in hectares
 */
export function calculatePolygonArea(coordinates: Coordinate[]): number {
  if (coordinates.length < 3) {
    return 0;
  }

  // Convert to projected coordinates for more accurate area
  // Using simplified equirectangular projection
  const centerLat = coordinates.reduce((sum, c) => sum + c.latitude, 0) / coordinates.length;
  const latFactor = 111320; // meters per degree latitude
  const lngFactor = 111320 * Math.cos(toRadians(centerLat)); // meters per degree longitude

  // Apply Shoelace formula
  let area = 0;
  for (let i = 0; i < coordinates.length; i++) {
    const j = (i + 1) % coordinates.length;
    const xi = coordinates[i].longitude * lngFactor;
    const yi = coordinates[i].latitude * latFactor;
    const xj = coordinates[j].longitude * lngFactor;
    const yj = coordinates[j].latitude * latFactor;
    area += xi * yj - xj * yi;
  }

  // Convert from square meters to hectares
  return Math.abs(area / 2) / 10000;
}

// ─────────────────────────────────────────────────────────────────────────────
// Agricultural Indices
// ─────────────────────────────────────────────────────────────────────────────

/**
 * NDVI health classification
 * تصنيف صحة NDVI
 */
export interface NDVIClassification {
  /** التصنيف - Classification label */
  label: string;
  /** التصنيف بالعربية - Arabic label */
  labelAr: string;
  /** لون التصنيف - Color code */
  color: string;
  /** الحد الأدنى - Minimum NDVI value */
  min: number;
  /** الحد الأقصى - Maximum NDVI value */
  max: number;
}

/**
 * NDVI classification ranges
 * نطاقات تصنيف NDVI
 */
export const NDVI_CLASSIFICATIONS: NDVIClassification[] = [
  { label: "Water/No Data", labelAr: "ماء/لا بيانات", color: "#0000FF", min: -1, max: 0 },
  { label: "Bare Soil", labelAr: "تربة عارية", color: "#A52A2A", min: 0, max: 0.1 },
  { label: "Sparse Vegetation", labelAr: "غطاء نباتي متناثر", color: "#FFD700", min: 0.1, max: 0.2 },
  { label: "Moderate Vegetation", labelAr: "غطاء نباتي متوسط", color: "#90EE90", min: 0.2, max: 0.4 },
  { label: "Dense Vegetation", labelAr: "غطاء نباتي كثيف", color: "#228B22", min: 0.4, max: 0.6 },
  { label: "Very Dense Vegetation", labelAr: "غطاء نباتي كثيف جداً", color: "#006400", min: 0.6, max: 1 },
];

/**
 * Classify NDVI value
 * تصنيف قيمة NDVI
 *
 * @param ndvi - قيمة NDVI - NDVI value (-1 to 1)
 * @returns التصنيف - Classification object
 */
export function classifyNDVI(ndvi: number): NDVIClassification {
  // Clamp to valid range
  const value = Math.max(-1, Math.min(1, ndvi));

  for (const classification of NDVI_CLASSIFICATIONS) {
    if (value >= classification.min && value < classification.max) {
      return classification;
    }
  }

  return NDVI_CLASSIFICATIONS[NDVI_CLASSIFICATIONS.length - 1];
}

/**
 * Calculate vegetation health score from NDVI (0-100)
 * حساب درجة صحة النبات من NDVI
 *
 * @param ndvi - قيمة NDVI - NDVI value
 * @returns درجة الصحة - Health score 0-100
 */
export function ndviToHealthScore(ndvi: number): number {
  // Only positive NDVI indicates vegetation
  if (ndvi <= 0) return 0;

  // Map 0-0.8 NDVI to 0-100 health score (0.8+ is very healthy)
  const score = (Math.min(ndvi, 0.8) / 0.8) * 100;
  return Math.round(score);
}

// ─────────────────────────────────────────────────────────────────────────────
// Soil Moisture Utilities
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Soil moisture status
 * حالة رطوبة التربة
 */
export interface SoilMoistureStatus {
  /** الحالة - Status label */
  status: "very_dry" | "dry" | "optimal" | "wet" | "very_wet";
  /** الحالة بالعربية - Arabic status */
  statusAr: string;
  /** يحتاج ري - Needs irrigation */
  needsIrrigation: boolean;
  /** لون الحالة - Status color */
  color: string;
}

/**
 * Classify soil moisture percentage
 * تصنيف نسبة رطوبة التربة
 *
 * @param moisturePercent - نسبة الرطوبة - Soil moisture percentage (0-100)
 * @param cropType - نوع المحصول - Optional crop type for adjusted thresholds
 * @returns حالة الرطوبة - Moisture status
 */
export function classifySoilMoisture(
  moisturePercent: number,
  cropType?: string,
): SoilMoistureStatus {
  // Default thresholds (can be adjusted by crop type)
  let veryDry = 20;
  let dry = 35;
  let optimalMin = 35;
  let optimalMax = 65;
  let wet = 75;

  // Adjust for specific crops
  if (cropType) {
    const crop = cropType.toLowerCase();
    if (crop.includes("rice") || crop.includes("أرز")) {
      // Rice needs more water
      veryDry = 40;
      dry = 50;
      optimalMin = 60;
      optimalMax = 90;
      wet = 95;
    } else if (crop.includes("date") || crop.includes("نخيل") || crop.includes("تمر")) {
      // Date palms are drought tolerant
      veryDry = 15;
      dry = 25;
      optimalMin = 25;
      optimalMax = 50;
      wet = 60;
    }
  }

  const moisture = Math.max(0, Math.min(100, moisturePercent));

  if (moisture < veryDry) {
    return {
      status: "very_dry",
      statusAr: "جاف جداً",
      needsIrrigation: true,
      color: "#DC2626",
    };
  }
  if (moisture < dry) {
    return {
      status: "dry",
      statusAr: "جاف",
      needsIrrigation: true,
      color: "#F59E0B",
    };
  }
  if (moisture <= optimalMax) {
    return {
      status: "optimal",
      statusAr: "مثالي",
      needsIrrigation: false,
      color: "#10B981",
    };
  }
  if (moisture <= wet) {
    return {
      status: "wet",
      statusAr: "رطب",
      needsIrrigation: false,
      color: "#3B82F6",
    };
  }

  return {
    status: "very_wet",
    statusAr: "رطب جداً",
    needsIrrigation: false,
    color: "#6366F1",
  };
}

// ─────────────────────────────────────────────────────────────────────────────
// Weather & Climate Utilities
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Calculate evapotranspiration (simplified Hargreaves method)
 * حساب التبخر-نتح (طريقة هارغريفز المبسطة)
 *
 * @param tempMin - الحرارة الصغرى - Minimum temperature in Celsius
 * @param tempMax - الحرارة الكبرى - Maximum temperature in Celsius
 * @param latitude - خط العرض - Latitude in degrees
 * @param dayOfYear - يوم السنة - Day of year (1-365)
 * @returns ET0 بالمم/يوم - Reference evapotranspiration in mm/day
 */
export function calculateET0(
  tempMin: number,
  tempMax: number,
  latitude: number,
  dayOfYear: number,
): number {
  const tempMean = (tempMin + tempMax) / 2;
  const tempRange = tempMax - tempMin;

  // Calculate extraterrestrial radiation (simplified)
  const latRad = toRadians(latitude);
  const solarDeclination = 0.409 * Math.sin((2 * Math.PI * dayOfYear) / 365 - 1.39);
  const sunsetHourAngle = Math.acos(-Math.tan(latRad) * Math.tan(solarDeclination));

  const dr = 1 + 0.033 * Math.cos((2 * Math.PI * dayOfYear) / 365);
  const Ra =
    (24 * 60 / Math.PI) *
    0.082 *
    dr *
    (sunsetHourAngle * Math.sin(latRad) * Math.sin(solarDeclination) +
      Math.cos(latRad) * Math.cos(solarDeclination) * Math.sin(sunsetHourAngle));

  // Hargreaves equation
  const ET0 = 0.0023 * (tempMean + 17.8) * Math.sqrt(Math.max(0, tempRange)) * Ra;

  return Math.max(0, ET0);
}

/**
 * Calculate Growing Degree Days (GDD)
 * حساب درجات النمو الحرارية
 *
 * @param tempMin - الحرارة الصغرى - Minimum temperature
 * @param tempMax - الحرارة الكبرى - Maximum temperature
 * @param baseTemp - درجة القاعدة - Base temperature (default: 10°C)
 * @returns GDD - Growing degree days
 */
export function calculateGDD(
  tempMin: number,
  tempMax: number,
  baseTemp: number = 10,
): number {
  const tempMean = (tempMin + tempMax) / 2;
  return Math.max(0, tempMean - baseTemp);
}

/**
 * Frost risk classification
 * تصنيف خطر الصقيع
 */
export type FrostRisk = "none" | "low" | "moderate" | "high" | "severe";

/**
 * Assess frost risk based on minimum temperature forecast
 * تقييم خطر الصقيع بناءً على توقعات الحرارة الصغرى
 *
 * @param forecastTempMin - الحرارة الصغرى المتوقعة - Forecasted minimum temperature
 * @returns خطر الصقيع - Frost risk level
 */
export function assessFrostRisk(forecastTempMin: number): {
  risk: FrostRisk;
  riskAr: string;
  recommendation: string;
  recommendationAr: string;
} {
  if (forecastTempMin > 5) {
    return {
      risk: "none",
      riskAr: "لا يوجد",
      recommendation: "No frost protection needed",
      recommendationAr: "لا حاجة للحماية من الصقيع",
    };
  }

  if (forecastTempMin > 2) {
    return {
      risk: "low",
      riskAr: "منخفض",
      recommendation: "Monitor temperatures; protect sensitive seedlings",
      recommendationAr: "راقب درجات الحرارة؛ احمِ الشتلات الحساسة",
    };
  }

  if (forecastTempMin > 0) {
    return {
      risk: "moderate",
      riskAr: "متوسط",
      recommendation: "Cover crops with cloth; avoid early morning irrigation",
      recommendationAr: "غطِّ المحاصيل بالقماش؛ تجنب الري في الصباح الباكر",
    };
  }

  if (forecastTempMin > -3) {
    return {
      risk: "high",
      riskAr: "مرتفع",
      recommendation: "Use frost protection methods; consider heating",
      recommendationAr: "استخدم طرق الحماية من الصقيع؛ فكر في التدفئة",
    };
  }

  return {
    risk: "severe",
    riskAr: "شديد",
    recommendation: "Maximum frost protection; harvest vulnerable crops",
    recommendationAr: "أقصى حماية من الصقيع؛ احصد المحاصيل المعرضة للخطر",
  };
}

// ─────────────────────────────────────────────────────────────────────────────
// Crop Stage Utilities
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Wheat growth stage (Zadoks scale simplified)
 * مرحلة نمو القمح (مقياس زادوكس المبسط)
 */
export type WheatGrowthStage =
  | "germination"
  | "seedling"
  | "tillering"
  | "stem_elongation"
  | "booting"
  | "heading"
  | "flowering"
  | "grain_filling"
  | "ripening";

/**
 * Get wheat growth stage from days after planting
 * الحصول على مرحلة نمو القمح من الأيام بعد الزراعة
 *
 * @param daysAfterPlanting - الأيام بعد الزراعة - Days since planting
 * @param variety - الصنف - Wheat variety (early/medium/late)
 * @returns مرحلة النمو - Growth stage information
 */
export function getWheatGrowthStage(
  daysAfterPlanting: number,
  variety: "early" | "medium" | "late" = "medium",
): { stage: WheatGrowthStage; stageAr: string; daysRemaining: number; nextStage: string } {
  // Adjustment factor based on variety
  const factor = variety === "early" ? 0.9 : variety === "late" ? 1.1 : 1.0;

  const stages: Array<{
    stage: WheatGrowthStage;
    stageAr: string;
    endDay: number;
    next: string;
  }> = [
    { stage: "germination", stageAr: "الإنبات", endDay: 10 * factor, next: "Seedling" },
    { stage: "seedling", stageAr: "البادرة", endDay: 20 * factor, next: "Tillering" },
    { stage: "tillering", stageAr: "التفريع", endDay: 50 * factor, next: "Stem Elongation" },
    { stage: "stem_elongation", stageAr: "استطالة الساق", endDay: 75 * factor, next: "Booting" },
    { stage: "booting", stageAr: "الانغماد", endDay: 90 * factor, next: "Heading" },
    { stage: "heading", stageAr: "طرد السنابل", endDay: 100 * factor, next: "Flowering" },
    { stage: "flowering", stageAr: "الإزهار", endDay: 110 * factor, next: "Grain Filling" },
    { stage: "grain_filling", stageAr: "امتلاء الحبوب", endDay: 135 * factor, next: "Ripening" },
    { stage: "ripening", stageAr: "النضج", endDay: 150 * factor, next: "Harvest" },
  ];

  for (const { stage, stageAr, endDay, next } of stages) {
    if (daysAfterPlanting <= endDay) {
      return {
        stage,
        stageAr,
        daysRemaining: Math.round(endDay - daysAfterPlanting),
        nextStage: next,
      };
    }
  }

  return {
    stage: "ripening",
    stageAr: "النضج",
    daysRemaining: 0,
    nextStage: "Harvest",
  };
}

// ─────────────────────────────────────────────────────────────────────────────
// Validation Utilities
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Validate phone number for Middle East countries
 * التحقق من رقم الهاتف لدول الشرق الأوسط
 *
 * @param phone - رقم الهاتف - Phone number
 * @param countryCode - رمز الدولة - Country code (optional)
 * @returns هل الرقم صالح - True if valid
 */
export function isValidMiddleEastPhone(phone: string, countryCode?: string): boolean {
  const cleaned = phone.replace(/[\s\-()]/g, "");

  const patterns: Record<string, RegExp> = {
    YE: /^(\+?967|00967)?[1-9]\d{8}$/, // Yemen
    SA: /^(\+?966|00966)?[1-9]\d{8}$/, // Saudi Arabia
    AE: /^(\+?971|00971)?[1-9]\d{8}$/, // UAE
    OM: /^(\+?968|00968)?[1-9]\d{7}$/, // Oman
    KW: /^(\+?965|00965)?[1-9]\d{7}$/, // Kuwait
    QA: /^(\+?974|00974)?[1-9]\d{7}$/, // Qatar
    BH: /^(\+?973|00973)?[1-9]\d{7}$/, // Bahrain
    JO: /^(\+?962|00962)?[1-9]\d{8}$/, // Jordan
    EG: /^(\+?20|0020)?[1-9]\d{9}$/, // Egypt
  };

  if (countryCode && patterns[countryCode.toUpperCase()]) {
    return patterns[countryCode.toUpperCase()].test(cleaned);
  }

  // Check against all patterns
  return Object.values(patterns).some((pattern) => pattern.test(cleaned));
}

/**
 * Validate field ID format
 * التحقق من تنسيق معرف الحقل
 *
 * Expected format: FIELD-XXX or FLD-XXXXX
 */
export function isValidFieldId(fieldId: string): boolean {
  const pattern = /^(FIELD|FLD)-[A-Z0-9]{3,10}$/i;
  return pattern.test(fieldId);
}

/**
 * Validate farm ID format
 * التحقق من تنسيق معرف المزرعة
 *
 * Expected format: FARM-XXX
 */
export function isValidFarmId(farmId: string): boolean {
  const pattern = /^FARM-[A-Z0-9]{3,10}$/i;
  return pattern.test(farmId);
}
