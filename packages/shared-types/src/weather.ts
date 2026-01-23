/**
 * SAHOOL Weather Types
 * Domain types for weather data, forecasts, and agricultural weather conditions
 *
 * Weather data is critical for irrigation scheduling, pest prediction,
 * and optimal farming operations timing.
 */

import type { Severity, ISODateString, ISODateTimeString } from "./common";
import type { Coordinates } from "./geo";

// ═══════════════════════════════════════════════════════════════════════════════
// Weather Condition Types
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Weather condition codes (following common weather APIs)
 */
export type WeatherCondition =
  | "clear"
  | "partly_cloudy"
  | "cloudy"
  | "overcast"
  | "fog"
  | "mist"
  | "haze"
  | "drizzle"
  | "light_rain"
  | "rain"
  | "heavy_rain"
  | "thunderstorm"
  | "snow"
  | "sleet"
  | "hail"
  | "dust"
  | "sandstorm"
  | "windy"
  | "hot"
  | "cold";

/**
 * Wind direction cardinal points
 */
export type WindDirection =
  | "N"
  | "NNE"
  | "NE"
  | "ENE"
  | "E"
  | "ESE"
  | "SE"
  | "SSE"
  | "S"
  | "SSW"
  | "SW"
  | "WSW"
  | "W"
  | "WNW"
  | "NW"
  | "NNW";

/**
 * UV index levels
 */
export type UVIndexLevel =
  | "low"      // 0-2
  | "moderate" // 3-5
  | "high"     // 6-7
  | "very_high" // 8-10
  | "extreme"; // 11+

// ═══════════════════════════════════════════════════════════════════════════════
// Current Weather Types
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Current weather data
 */
export interface WeatherData {
  /** Location identifier */
  locationId: string;
  /** Location name */
  locationName?: string;
  /** Location name in Arabic */
  locationNameAr?: string;
  /** Coordinates */
  coordinates?: Coordinates;
  /** Temperature in Celsius */
  temperatureC: number;
  /** Feels like temperature in Celsius */
  feelsLikeC?: number;
  /** Relative humidity percentage (0-100) */
  humidityPercent: number;
  /** Atmospheric pressure in hPa */
  pressureHpa?: number;
  /** Wind speed in km/h */
  windSpeedKmh: number;
  /** Wind gust speed in km/h */
  windGustKmh?: number;
  /** Wind direction in degrees (0-360) */
  windDirectionDeg?: number;
  /** Wind direction cardinal */
  windDirection?: WindDirection;
  /** Weather condition */
  condition: WeatherCondition;
  /** Condition description */
  conditionDescription?: string;
  /** Condition description in Arabic */
  conditionDescriptionAr?: string;
  /** Weather icon code */
  iconCode?: string;
  /** Cloud cover percentage (0-100) */
  cloudCoverPercent?: number;
  /** Visibility in kilometers */
  visibilityKm?: number;
  /** UV index (0-11+) */
  uvIndex?: number;
  /** UV level */
  uvLevel?: UVIndexLevel;
  /** Dew point in Celsius */
  dewPointC?: number;
  /** Precipitation in last hour (mm) */
  precipitationMm?: number;
  /** Observation timestamp */
  timestamp: ISODateTimeString;
  /** Data source */
  source?: string;
}

/**
 * Weather data with snake_case properties (API compatibility)
 */
export interface WeatherDataSnakeCase {
  location_id: string;
  temperature_c: number;
  humidity_percent: number;
  wind_speed_kmh: number;
  condition: string;
  condition_ar: string;
  timestamp?: string;
  // Aliases for component compatibility
  temperature?: number;
  humidity?: number;
  windSpeed?: number;
  conditionAr?: string;
  location?: string;
  windDirection?: string;
  pressure?: number;
  visibility?: number;
  uvIndex?: number;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Weather Forecast Types
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Hourly weather forecast
 */
export interface HourlyForecast {
  /** Forecast datetime */
  dateTime: ISODateTimeString;
  /** Temperature in Celsius */
  temperatureC: number;
  /** Feels like temperature */
  feelsLikeC?: number;
  /** Humidity percentage */
  humidityPercent: number;
  /** Wind speed km/h */
  windSpeedKmh: number;
  /** Wind direction */
  windDirection?: WindDirection;
  /** Weather condition */
  condition: WeatherCondition;
  /** Condition description */
  conditionDescription?: string;
  /** Condition in Arabic */
  conditionDescriptionAr?: string;
  /** Icon code */
  iconCode?: string;
  /** Precipitation probability (0-100) */
  precipitationProbabilityPercent?: number;
  /** Expected precipitation in mm */
  precipitationMm?: number;
  /** Cloud cover percentage */
  cloudCoverPercent?: number;
  /** UV index */
  uvIndex?: number;
}

/**
 * Daily weather forecast
 */
export interface DailyForecast {
  /** Forecast date */
  date: ISODateString;
  /** Maximum temperature in Celsius */
  tempMaxC: number;
  /** Minimum temperature in Celsius */
  tempMinC: number;
  /** Average temperature */
  tempAvgC?: number;
  /** Maximum feels like temperature */
  feelsLikeMaxC?: number;
  /** Minimum feels like temperature */
  feelsLikeMinC?: number;
  /** Average humidity percentage */
  humidityPercent?: number;
  /** Maximum wind speed */
  windMaxKmh?: number;
  /** Average wind speed */
  windAvgKmh?: number;
  /** Dominant wind direction */
  windDirection?: WindDirection;
  /** Day condition */
  conditionDay: WeatherCondition;
  /** Night condition */
  conditionNight?: WeatherCondition;
  /** Condition description */
  conditionDescription?: string;
  /** Condition in Arabic */
  conditionDescriptionAr?: string;
  /** Icon code for day */
  iconCodeDay?: string;
  /** Icon code for night */
  iconCodeNight?: string;
  /** Precipitation probability */
  precipitationProbabilityPercent?: number;
  /** Total precipitation in mm */
  precipitationMm?: number;
  /** Sunrise time (HH:mm) */
  sunrise?: string;
  /** Sunset time (HH:mm) */
  sunset?: string;
  /** UV index */
  uvIndex?: number;
  /** Moon phase */
  moonPhase?: string;
}

/**
 * Weather forecast response
 */
export interface WeatherForecast {
  /** Location identifier */
  locationId: string;
  /** Location name */
  locationName?: string;
  /** Location coordinates */
  coordinates?: Coordinates;
  /** Current conditions */
  current?: WeatherData;
  /** Hourly forecast (up to 48 hours) */
  hourly?: HourlyForecast[];
  /** Daily forecast (up to 14 days) */
  daily: DailyForecast[];
  /** Forecast generation timestamp */
  generatedAt: ISODateTimeString;
  /** Data source */
  source?: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Weather Alert Types
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Weather alert type
 */
export type WeatherAlertType =
  | "heat_wave"
  | "cold_wave"
  | "frost"
  | "heavy_rain"
  | "flood"
  | "thunderstorm"
  | "wind"
  | "dust_storm"
  | "sandstorm"
  | "hail"
  | "drought"
  | "fire_danger"
  | "uv_warning";

/**
 * Weather alert/warning
 */
export interface WeatherAlert {
  /** Alert ID */
  id: string;
  /** Alert type */
  type: WeatherAlertType;
  /** Severity level */
  severity: Severity;
  /** Alert title */
  title: string;
  /** Title in Arabic */
  titleAr?: string;
  /** Detailed description */
  description: string;
  /** Description in Arabic */
  descriptionAr?: string;
  /** Affected areas/regions */
  affectedAreas: string[];
  /** Alert start time */
  startTime: ISODateTimeString;
  /** Alert end time */
  endTime?: ISODateTimeString;
  /** Is currently active */
  isActive: boolean;
  /** Source/issuing authority */
  source?: string;
  /** Recommended actions */
  recommendations?: string[];
  /** Recommendations in Arabic */
  recommendationsAr?: string[];
  /** Alert issue timestamp */
  issuedAt: ISODateTimeString;
  /** Last update timestamp */
  updatedAt?: ISODateTimeString;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Agricultural Weather Types
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Evapotranspiration data (ET0)
 */
export interface EvapotranspirationData {
  /** Location ID */
  locationId: string;
  /** Date */
  date: ISODateString;
  /** Reference ET in mm/day (Penman-Monteith) */
  et0Mm: number;
  /** Crop coefficient (Kc) */
  cropCoefficient?: number;
  /** Crop ET in mm/day (ET0 * Kc) */
  etcMm?: number;
  /** Calculation method */
  method?: "penman_monteith" | "hargreaves" | "blaney_criddle";
  /** Data quality flag */
  qualityFlag?: "measured" | "estimated" | "interpolated";
}

/**
 * Growing Degree Days (GDD)
 */
export interface GrowingDegreeDays {
  /** Location ID */
  locationId: string;
  /** Date */
  date: ISODateString;
  /** Daily GDD */
  gddDaily: number;
  /** Cumulative GDD for season */
  gddCumulative: number;
  /** Base temperature used */
  baseTemperatureC: number;
  /** Upper threshold temperature */
  upperThresholdC?: number;
  /** Crop type */
  cropType?: string;
  /** Season start date */
  seasonStartDate?: ISODateString;
}

/**
 * Chill hours (for fruit trees)
 */
export interface ChillHours {
  /** Location ID */
  locationId: string;
  /** Date */
  date: ISODateString;
  /** Daily chill hours */
  chillHoursDaily: number;
  /** Cumulative chill hours */
  chillHoursCumulative: number;
  /** Calculation model */
  model?: "below_7" | "utah" | "dynamic";
  /** Season start date */
  seasonStartDate?: ISODateString;
}

/**
 * Agricultural weather summary
 */
export interface AgriculturalWeatherSummary {
  /** Location ID */
  locationId: string;
  /** Period start date */
  periodStart: ISODateString;
  /** Period end date */
  periodEnd: ISODateString;
  /** Average temperature */
  avgTemperatureC: number;
  /** Maximum temperature */
  maxTemperatureC: number;
  /** Minimum temperature */
  minTemperatureC: number;
  /** Total precipitation */
  totalPrecipitationMm: number;
  /** Rain days count */
  rainDaysCount: number;
  /** Average humidity */
  avgHumidityPercent: number;
  /** Total ET0 */
  totalEt0Mm?: number;
  /** Total GDD */
  totalGdd?: number;
  /** Total chill hours */
  totalChillHours?: number;
  /** Frost days count */
  frostDaysCount?: number;
  /** Hot days count (>35C) */
  hotDaysCount?: number;
  /** Spray window days (favorable for application) */
  sprayWindowDays?: number;
}

/**
 * Spray/application window
 */
export interface SprayWindow {
  /** Start time */
  startTime: ISODateTimeString;
  /** End time */
  endTime: ISODateTimeString;
  /** Window quality (how suitable conditions are) */
  quality: "excellent" | "good" | "fair" | "poor";
  /** Temperature during window */
  temperatureC: number;
  /** Wind speed during window */
  windSpeedKmh: number;
  /** Humidity during window */
  humidityPercent: number;
  /** Rain probability */
  rainProbabilityPercent: number;
  /** Hours until next rain */
  hoursUntilRain?: number;
  /** Limiting factors */
  limitingFactors?: string[];
}

// ═══════════════════════════════════════════════════════════════════════════════
// Weather Request Types
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Request for weather data
 */
export interface WeatherRequest {
  /** Location ID or coordinates */
  location: string | Coordinates;
  /** Include hourly forecast */
  includeHourly?: boolean;
  /** Number of forecast days (1-14) */
  forecastDays?: number;
  /** Include agricultural data */
  includeAgricultural?: boolean;
  /** Include alerts */
  includeAlerts?: boolean;
  /** Language preference */
  language?: "ar" | "en";
}

/**
 * Request for historical weather data
 */
export interface HistoricalWeatherRequest {
  /** Location ID or coordinates */
  location: string | Coordinates;
  /** Start date */
  startDate: ISODateString;
  /** End date */
  endDate: ISODateString;
  /** Data resolution */
  resolution?: "hourly" | "daily";
  /** Include agricultural metrics */
  includeAgricultural?: boolean;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Type Guards
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Type guard for WeatherData
 */
export function isWeatherData(obj: unknown): obj is WeatherData {
  return (
    typeof obj === "object" &&
    obj !== null &&
    "locationId" in obj &&
    "temperatureC" in obj &&
    "condition" in obj
  );
}

/**
 * Type guard for WeatherAlert
 */
export function isWeatherAlert(obj: unknown): obj is WeatherAlert {
  return (
    typeof obj === "object" &&
    obj !== null &&
    "id" in obj &&
    "type" in obj &&
    "severity" in obj &&
    "title" in obj
  );
}

/**
 * Check if weather is favorable for field work
 */
export function isFavorableForFieldWork(weather: WeatherData): boolean {
  return (
    weather.condition !== "rain" &&
    weather.condition !== "heavy_rain" &&
    weather.condition !== "thunderstorm" &&
    weather.windSpeedKmh < 30 &&
    weather.temperatureC >= 5 &&
    weather.temperatureC <= 35
  );
}

/**
 * Check if weather is favorable for spraying
 */
export function isFavorableForSpraying(weather: WeatherData): boolean {
  return (
    weather.condition !== "rain" &&
    weather.condition !== "heavy_rain" &&
    weather.condition !== "drizzle" &&
    weather.windSpeedKmh < 15 &&
    weather.temperatureC >= 10 &&
    weather.temperatureC <= 30 &&
    weather.humidityPercent >= 40 &&
    weather.humidityPercent <= 90
  );
}
