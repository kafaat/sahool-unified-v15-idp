/**
 * Yemen Crop Catalog
 * كتالوج المحاصيل اليمنية
 *
 * Ported 1:1 from archive/deprecated-services/yield-engine/src/main.py
 * (CROP_DATA + CropType + USD_TO_YER). The archived yield-engine exposed
 *   GET /v1/crops   — list supported crops
 *   GET /v1/price/:cropType — per-crop price lookup
 * Both are reference-data endpoints with no ML dependency, so they can
 * land in yield-prediction-service without porting the YieldPredictor.
 *
 * The archived POST /v1/predict (rich body form) is intentionally NOT
 * ported — it depends on the Python YieldPredictor (~220 lines of ML
 * logic). The successor already exposes GET /predict/:fieldId with the
 * DB-centric signature; a POST-body variant can be added later if the
 * product actually needs one.
 */

export type CropType =
  | "wheat"
  | "barley"
  | "corn"
  | "sorghum"
  | "millet"
  | "faba_bean"
  | "lentil"
  | "chickpea"
  | "tomato"
  | "potato"
  | "onion"
  | "garlic"
  | "pepper"
  | "eggplant"
  | "cucumber"
  | "okra"
  | "date_palm"
  | "mango"
  | "banana"
  | "grape"
  | "citrus_orange"
  | "citrus_lemon"
  | "pomegranate"
  | "fig"
  | "guava"
  | "coffee"
  | "sesame"
  | "cotton"
  | "alfalfa";

export interface CropInfo {
  /** Display name in Arabic (primary locale) */
  name_ar: string;
  /** Base expected yield, tonnes per hectare */
  base_yield_per_hectare: number;
  /** Target yield, kg per hectare (= base * 1200 historically) */
  target_yield: number;
  /** Reference price USD / tonne — used by the yield-prediction UI */
  price_usd_per_ton: number;
  /** Growing-season length, days */
  growing_season_days: number;
  /** Optimal rainfall, mm/season */
  optimal_rainfall: number;
  /** Optimal mean temperature, °C */
  optimal_temp: number;
  /** Qualitative water demand */
  water_requirement: "very_low" | "low" | "medium" | "high" | "very_high";
}

/** Approximate USD → YER exchange rate (kept as a constant to preserve
 *  behavioural parity with the archived service; the archived code did
 *  not fetch a live FX rate either). */
export const USD_TO_YER = 535;

export const CROP_CATALOG: Record<CropType, CropInfo> = {
  // Cereals
  wheat:   { name_ar: "قمح",        base_yield_per_hectare: 2.5,  target_yield: 3000,  price_usd_per_ton: 350,  growing_season_days: 120, optimal_rainfall: 450,  optimal_temp: 20, water_requirement: "medium" },
  barley:  { name_ar: "شعير",       base_yield_per_hectare: 2.0,  target_yield: 2400,  price_usd_per_ton: 280,  growing_season_days: 100, optimal_rainfall: 400,  optimal_temp: 17, water_requirement: "low" },
  corn:    { name_ar: "ذرة",        base_yield_per_hectare: 4.0,  target_yield: 4800,  price_usd_per_ton: 280,  growing_season_days: 100, optimal_rainfall: 500,  optimal_temp: 25, water_requirement: "high" },
  sorghum: { name_ar: "ذرة رفيعة",  base_yield_per_hectare: 2.0,  target_yield: 2400,  price_usd_per_ton: 250,  growing_season_days: 110, optimal_rainfall: 400,  optimal_temp: 27, water_requirement: "low" },
  millet:  { name_ar: "دخن",        base_yield_per_hectare: 1.5,  target_yield: 1800,  price_usd_per_ton: 300,  growing_season_days:  90, optimal_rainfall: 250,  optimal_temp: 30, water_requirement: "very_low" },
  // Legumes
  faba_bean: { name_ar: "فول",      base_yield_per_hectare: 2.5,  target_yield: 3000,  price_usd_per_ton: 600,  growing_season_days: 120, optimal_rainfall: 650,  optimal_temp: 18, water_requirement: "medium" },
  lentil:    { name_ar: "عدس",      base_yield_per_hectare: 1.0,  target_yield: 1200,  price_usd_per_ton: 800,  growing_season_days: 100, optimal_rainfall: 400,  optimal_temp: 15, water_requirement: "low" },
  chickpea:  { name_ar: "حمص",      base_yield_per_hectare: 1.2,  target_yield: 1440,  price_usd_per_ton: 900,  growing_season_days: 100, optimal_rainfall: 400,  optimal_temp: 20, water_requirement: "low" },
  // Vegetables
  tomato:   { name_ar: "طماطم",     base_yield_per_hectare: 35.0, target_yield: 42000, price_usd_per_ton: 400,  growing_season_days:  90, optimal_rainfall: 600,  optimal_temp: 24, water_requirement: "high" },
  potato:   { name_ar: "بطاطس",     base_yield_per_hectare: 20.0, target_yield: 24000, price_usd_per_ton: 320,  growing_season_days: 100, optimal_rainfall: 500,  optimal_temp: 18, water_requirement: "medium" },
  onion:    { name_ar: "بصل",       base_yield_per_hectare: 25.0, target_yield: 30000, price_usd_per_ton: 350,  growing_season_days: 120, optimal_rainfall: 650,  optimal_temp: 19, water_requirement: "medium" },
  garlic:   { name_ar: "ثوم",       base_yield_per_hectare: 8.0,  target_yield: 9600,  price_usd_per_ton: 1500, growing_season_days: 150, optimal_rainfall: 400,  optimal_temp: 15, water_requirement: "low" },
  pepper:   { name_ar: "فلفل حلو",  base_yield_per_hectare: 25.0, target_yield: 30000, price_usd_per_ton: 600,  growing_season_days:  90, optimal_rainfall: 900,  optimal_temp: 23, water_requirement: "high" },
  eggplant: { name_ar: "باذنجان",   base_yield_per_hectare: 30.0, target_yield: 36000, price_usd_per_ton: 350,  growing_season_days: 100, optimal_rainfall: 900,  optimal_temp: 26, water_requirement: "high" },
  cucumber: { name_ar: "خيار",      base_yield_per_hectare: 40.0, target_yield: 48000, price_usd_per_ton: 300,  growing_season_days:  60, optimal_rainfall: 900,  optimal_temp: 25, water_requirement: "high" },
  okra:     { name_ar: "بامية",     base_yield_per_hectare: 12.0, target_yield: 14400, price_usd_per_ton: 600,  growing_season_days:  90, optimal_rainfall: 650,  optimal_temp: 30, water_requirement: "medium" },
  // Fruits
  date_palm:     { name_ar: "نخيل (تمر)", base_yield_per_hectare: 8.0,  target_yield: 9600,  price_usd_per_ton: 1500, growing_season_days: 180, optimal_rainfall:  200, optimal_temp: 30, water_requirement: "low" },
  mango:         { name_ar: "مانجو",      base_yield_per_hectare: 10.0, target_yield: 12000, price_usd_per_ton: 800,  growing_season_days: 150, optimal_rainfall:  800, optimal_temp: 28, water_requirement: "medium" },
  banana:        { name_ar: "موز",        base_yield_per_hectare: 30.0, target_yield: 36000, price_usd_per_ton: 500,  growing_season_days: 300, optimal_rainfall: 1500, optimal_temp: 27, water_requirement: "very_high" },
  grape:         { name_ar: "عنب",        base_yield_per_hectare: 12.0, target_yield: 14400, price_usd_per_ton: 700,  growing_season_days: 170, optimal_rainfall:  600, optimal_temp: 22, water_requirement: "medium" },
  citrus_orange: { name_ar: "برتقال",     base_yield_per_hectare: 20.0, target_yield: 24000, price_usd_per_ton: 450,  growing_season_days: 300, optimal_rainfall:  650, optimal_temp: 24, water_requirement: "medium" },
  citrus_lemon:  { name_ar: "ليمون",      base_yield_per_hectare: 15.0, target_yield: 18000, price_usd_per_ton: 500,  growing_season_days: 300, optimal_rainfall:  650, optimal_temp: 24, water_requirement: "medium" },
  pomegranate:   { name_ar: "رمان",       base_yield_per_hectare: 12.0, target_yield: 14400, price_usd_per_ton: 700,  growing_season_days: 180, optimal_rainfall:  400, optimal_temp: 25, water_requirement: "low" },
  fig:           { name_ar: "تين",        base_yield_per_hectare: 8.0,  target_yield: 9600,  price_usd_per_ton: 800,  growing_season_days: 150, optimal_rainfall:  400, optimal_temp: 24, water_requirement: "low" },
  guava:         { name_ar: "جوافة",      base_yield_per_hectare: 25.0, target_yield: 30000, price_usd_per_ton: 500,  growing_season_days: 180, optimal_rainfall:  650, optimal_temp: 26, water_requirement: "medium" },
  // Cash crops
  coffee:  { name_ar: "بن يمني", base_yield_per_hectare: 0.8, target_yield: 1000, price_usd_per_ton: 8000, growing_season_days: 270, optimal_rainfall: 1200, optimal_temp: 20, water_requirement: "high" },
  sesame:  { name_ar: "سمسم",    base_yield_per_hectare: 0.8, target_yield: 1000, price_usd_per_ton: 2000, growing_season_days: 100, optimal_rainfall:  400, optimal_temp: 30, water_requirement: "low" },
  cotton:  { name_ar: "قطن",     base_yield_per_hectare: 2.5, target_yield: 3000, price_usd_per_ton: 1800, growing_season_days: 150, optimal_rainfall:  900, optimal_temp: 27, water_requirement: "high" },
  // Fodder
  alfalfa: { name_ar: "برسيم حجازي", base_yield_per_hectare: 15.0, target_yield: 18000, price_usd_per_ton: 200, growing_season_days: 365, optimal_rainfall: 900, optimal_temp: 22, water_requirement: "high" },
};

export const SUPPORTED_CROP_IDS: readonly CropType[] = Object.keys(
  CROP_CATALOG,
) as CropType[];

export function isSupportedCrop(crop: string): crop is CropType {
  return crop in CROP_CATALOG;
}
