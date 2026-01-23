/**
 * SAHOOL i18n Package
 * Internationalization utilities for the SAHOOL platform
 *
 * Features:
 * - Arabic (RTL) and English (LTR) support
 * - Type-safe translations
 * - Arabic pluralization with 6 plural forms
 * - Number and date formatting (Gregorian & Hijri)
 * - Currency formatting (SAR, YER, USD)
 * - RTL support utilities
 * - Regional settings for Middle East
 */

// Re-export locale files
import arMessages from "./locales/ar.json";
import enMessages from "./locales/en.json";

export const messages = {
  ar: arMessages,
  en: enMessages,
} as const;

export type Locale = keyof typeof messages;
export type Messages = typeof arMessages;

export const locales: Locale[] = ["ar", "en"];
export const defaultLocale: Locale = "ar";

// ═══════════════════════════════════════════════════════════════════════════
// Regional Configuration
// ═══════════════════════════════════════════════════════════════════════════

export interface RegionalConfig {
  timeZone: string;
  currency: string;
  currencySymbol: string;
  dateFormat: "gregorian" | "hijri" | "both";
  weekStartsOn: 0 | 1 | 6; // 0=Sunday, 1=Monday, 6=Saturday
  numberSystem: "latn" | "arab"; // Latin or Arabic-Indic numerals
}

export const regionalConfigs: Record<string, RegionalConfig> = {
  "sa": { // Saudi Arabia
    timeZone: "Asia/Riyadh",
    currency: "SAR",
    currencySymbol: "ر.س",
    dateFormat: "hijri",
    weekStartsOn: 0,
    numberSystem: "arab",
  },
  "ye": { // Yemen
    timeZone: "Asia/Aden",
    currency: "YER",
    currencySymbol: "ر.ي",
    dateFormat: "both",
    weekStartsOn: 0,
    numberSystem: "arab",
  },
  "ae": { // UAE
    timeZone: "Asia/Dubai",
    currency: "AED",
    currencySymbol: "د.إ",
    dateFormat: "gregorian",
    weekStartsOn: 0,
    numberSystem: "arab",
  },
  "default": {
    timeZone: "Asia/Aden",
    currency: "YER",
    currencySymbol: "ر.ي",
    dateFormat: "gregorian",
    weekStartsOn: 0,
    numberSystem: "latn",
  },
};

// Default regional config (Yemen as per SAHOOL)
export const defaultRegion = "ye";

/**
 * Get regional configuration
 */
export function getRegionalConfig(region: string = defaultRegion): RegionalConfig {
  return regionalConfigs[region] || regionalConfigs["default"];
}

// ═══════════════════════════════════════════════════════════════════════════
// Core i18n Functions
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Get messages for a specific locale
 */
export function getMessages(locale: Locale): Messages {
  return messages[locale] || messages[defaultLocale];
}

/**
 * Get locale display name
 */
export function getLocaleDisplayName(locale: Locale): string {
  const names: Record<Locale, string> = {
    ar: "العربية",
    en: "English",
  };
  return names[locale];
}

/**
 * Get locale native name for display
 */
export function getLocaleNativeName(locale: Locale): { name: string; nativeName: string } {
  const names: Record<Locale, { name: string; nativeName: string }> = {
    ar: { name: "Arabic", nativeName: "العربية" },
    en: { name: "English", nativeName: "English" },
  };
  return names[locale];
}

// ═══════════════════════════════════════════════════════════════════════════
// RTL Support
// ═══════════════════════════════════════════════════════════════════════════

const rtlLocales: Set<Locale> = new Set(["ar"]);

/**
 * Check if locale is RTL
 */
export function isRTL(locale: Locale): boolean {
  return rtlLocales.has(locale);
}

/**
 * Get text direction for locale
 */
export function getDirection(locale: Locale): "rtl" | "ltr" {
  return isRTL(locale) ? "rtl" : "ltr";
}

/**
 * Get CSS logical properties mapping for RTL support
 * Useful for consistent styling across RTL/LTR layouts
 */
export function getLogicalProperties(locale: Locale): {
  start: "left" | "right";
  end: "left" | "right";
  marginInlineStart: "marginLeft" | "marginRight";
  marginInlineEnd: "marginLeft" | "marginRight";
  paddingInlineStart: "paddingLeft" | "paddingRight";
  paddingInlineEnd: "paddingLeft" | "paddingRight";
  borderInlineStart: "borderLeft" | "borderRight";
  borderInlineEnd: "borderLeft" | "borderRight";
  textAlign: "left" | "right";
} {
  const rtl = isRTL(locale);
  return {
    start: rtl ? "right" : "left",
    end: rtl ? "left" : "right",
    marginInlineStart: rtl ? "marginRight" : "marginLeft",
    marginInlineEnd: rtl ? "marginLeft" : "marginRight",
    paddingInlineStart: rtl ? "paddingRight" : "paddingLeft",
    paddingInlineEnd: rtl ? "paddingLeft" : "paddingRight",
    borderInlineStart: rtl ? "borderRight" : "borderLeft",
    borderInlineEnd: rtl ? "borderLeft" : "borderRight",
    textAlign: rtl ? "right" : "left",
  };
}

/**
 * Get document/html attributes for locale
 */
export function getHtmlAttributes(locale: Locale): {
  lang: string;
  dir: "rtl" | "ltr";
} {
  return {
    lang: locale,
    dir: getDirection(locale),
  };
}

// ═══════════════════════════════════════════════════════════════════════════
// Number Formatting
// ═══════════════════════════════════════════════════════════════════════════

export interface NumberFormatOptions extends Intl.NumberFormatOptions {
  useArabicNumerals?: boolean;
}

/**
 * Format number according to locale
 */
export function formatNumber(
  value: number,
  locale: Locale,
  options?: NumberFormatOptions
): string {
  const { useArabicNumerals, ...intlOptions } = options || {};

  // Use Arabic-Indic numerals for Arabic locale if requested
  const numberingSystem = useArabicNumerals && locale === "ar" ? "arab" : undefined;
  const localeString = numberingSystem ? `${locale}-u-nu-${numberingSystem}` : locale;

  return new Intl.NumberFormat(localeString, intlOptions).format(value);
}

/**
 * Format currency
 */
export function formatCurrency(
  value: number,
  locale: Locale,
  currency: string = "YER",
  options?: Omit<NumberFormatOptions, "style" | "currency">
): string {
  return formatNumber(value, locale, {
    style: "currency",
    currency,
    ...options,
  });
}

/**
 * Format percentage
 */
export function formatPercent(
  value: number,
  locale: Locale,
  decimals: number = 1
): string {
  return formatNumber(value / 100, locale, {
    style: "percent",
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

/**
 * Format area (hectares)
 */
export function formatArea(
  value: number,
  locale: Locale,
  unit: "hectare" | "sqm" | "dunam" = "hectare"
): string {
  const formatted = formatNumber(value, locale, {
    maximumFractionDigits: 2,
  });

  const unitLabels: Record<string, Record<Locale, string>> = {
    hectare: { ar: "هكتار", en: "ha" },
    sqm: { ar: "م\u00b2", en: "m\u00b2" },
    dunam: { ar: "دونم", en: "dunam" },
  };

  return `${formatted} ${unitLabels[unit][locale]}`;
}

/**
 * Format weight (kg/ton)
 */
export function formatWeight(
  value: number,
  locale: Locale,
  unit: "kg" | "ton" | "gram" = "kg"
): string {
  const formatted = formatNumber(value, locale, {
    maximumFractionDigits: unit === "gram" ? 0 : 2,
  });

  const unitLabels: Record<string, Record<Locale, string>> = {
    kg: { ar: "كجم", en: "kg" },
    ton: { ar: "طن", en: "t" },
    gram: { ar: "جم", en: "g" },
  };

  return `${formatted} ${unitLabels[unit][locale]}`;
}

// ═══════════════════════════════════════════════════════════════════════════
// Date Formatting
// ═══════════════════════════════════════════════════════════════════════════

export interface DateFormatOptions extends Intl.DateTimeFormatOptions {
  calendar?: "gregory" | "islamic" | "islamic-umalqura";
}

/**
 * Format date according to locale
 */
export function formatDate(
  date: Date | string | number,
  locale: Locale,
  options?: DateFormatOptions
): string {
  const d = typeof date === "string" || typeof date === "number"
    ? new Date(date)
    : date;

  const { calendar, ...intlOptions } = options || {};

  // Build locale string with calendar if specified
  const localeString = calendar
    ? `${locale}-u-ca-${calendar}`
    : locale;

  return new Intl.DateTimeFormat(localeString, {
    dateStyle: "medium",
    ...intlOptions,
  }).format(d);
}

/**
 * Format date in Hijri calendar
 */
export function formatHijriDate(
  date: Date | string | number,
  locale: Locale,
  options?: Omit<DateFormatOptions, "calendar">
): string {
  return formatDate(date, locale, {
    calendar: "islamic-umalqura",
    ...options,
  });
}

/**
 * Format time according to locale
 */
export function formatTime(
  date: Date | string | number,
  locale: Locale,
  options?: Intl.DateTimeFormatOptions
): string {
  const d = typeof date === "string" || typeof date === "number"
    ? new Date(date)
    : date;

  return new Intl.DateTimeFormat(locale, {
    timeStyle: "short",
    ...options,
  }).format(d);
}

/**
 * Format datetime according to locale
 */
export function formatDateTime(
  date: Date | string | number,
  locale: Locale,
  options?: DateFormatOptions
): string {
  const d = typeof date === "string" || typeof date === "number"
    ? new Date(date)
    : date;

  const { calendar, ...intlOptions } = options || {};
  const localeString = calendar ? `${locale}-u-ca-${calendar}` : locale;

  return new Intl.DateTimeFormat(localeString, {
    dateStyle: "medium",
    timeStyle: "short",
    ...intlOptions,
  }).format(d);
}

/**
 * Format relative time (e.g., "2 hours ago", "in 3 days")
 */
export function formatRelativeTime(
  date: Date | string | number,
  locale: Locale,
  baseDate: Date = new Date()
): string {
  const d = typeof date === "string" || typeof date === "number"
    ? new Date(date)
    : date;

  const diffMs = d.getTime() - baseDate.getTime();
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHour = Math.floor(diffMin / 60);
  const diffDay = Math.floor(diffHour / 24);
  const diffMonth = Math.floor(diffDay / 30);
  const diffYear = Math.floor(diffDay / 365);

  const rtf = new Intl.RelativeTimeFormat(locale, { numeric: "auto" });

  if (Math.abs(diffYear) >= 1) return rtf.format(diffYear, "year");
  if (Math.abs(diffMonth) >= 1) return rtf.format(diffMonth, "month");
  if (Math.abs(diffDay) >= 1) return rtf.format(diffDay, "day");
  if (Math.abs(diffHour) >= 1) return rtf.format(diffHour, "hour");
  if (Math.abs(diffMin) >= 1) return rtf.format(diffMin, "minute");
  return rtf.format(diffSec, "second");
}

// ═══════════════════════════════════════════════════════════════════════════
// Pluralization
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Arabic plural categories based on CLDR rules
 * Arabic has 6 plural forms:
 * - zero: 0
 * - one: 1
 * - two: 2
 * - few: 3-10
 * - many: 11-99
 * - other: 100+
 */
export type ArabicPluralCategory = "zero" | "one" | "two" | "few" | "many" | "other";

/**
 * Get Arabic plural category for a number
 */
export function getArabicPluralCategory(n: number): ArabicPluralCategory {
  const absN = Math.abs(n);
  const i = Math.floor(absN); // Integer part

  if (n === 0) return "zero";
  if (n === 1) return "one";
  if (n === 2) return "two";

  // For numbers 3-10, category is "few"
  const mod100 = i % 100;
  if (mod100 >= 3 && mod100 <= 10) return "few";

  // For numbers 11-99 in the ones/tens place, category is "many"
  if (mod100 >= 11 && mod100 <= 99) return "many";

  return "other";
}

/**
 * Get plural category for a number and locale
 */
export function getPluralCategory(
  n: number,
  locale: Locale
): string {
  if (locale === "ar") {
    return getArabicPluralCategory(n);
  }

  // English plural rules (simplified)
  if (n === 0) return "zero";
  if (n === 1) return "one";
  return "other";
}

/**
 * Format a number with its plural form
 * Uses ICU MessageFormat syntax: {count, plural, =0 {...} =1 {...} other {...}}
 */
export function formatPlural(
  count: number,
  forms: {
    zero?: string;
    one?: string;
    two?: string;
    few?: string;
    many?: string;
    other: string;
  },
  locale: Locale
): string {
  const category = getPluralCategory(count, locale);
  const template = forms[category as keyof typeof forms] || forms.other;

  // Replace # with the count
  return template.replace(/#/g, formatNumber(count, locale));
}

// ═══════════════════════════════════════════════════════════════════════════
// Text Utilities
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Check if text contains Arabic characters
 */
export function containsArabic(text: string): boolean {
  return /[\u0600-\u06FF]/.test(text);
}

/**
 * Check if text is primarily Arabic
 */
export function isPrimarilyArabic(text: string): boolean {
  const arabicChars = (text.match(/[\u0600-\u06FF]/g) || []).length;
  const totalChars = text.replace(/\s/g, "").length;
  return arabicChars > totalChars / 2;
}

/**
 * Detect text direction based on content
 */
export function detectTextDirection(text: string): "rtl" | "ltr" {
  return isPrimarilyArabic(text) ? "rtl" : "ltr";
}

/**
 * Wrap text with directional markers for mixed content
 */
export function wrapWithDirection(text: string, dir: "rtl" | "ltr"): string {
  const LRM = "\u200E"; // Left-to-Right Mark
  const RLM = "\u200F"; // Right-to-Left Mark

  return dir === "rtl" ? `${RLM}${text}${RLM}` : `${LRM}${text}${LRM}`;
}

/**
 * Format bidirectional text for display
 * Useful for mixing Arabic and English text
 */
export function formatBidirectionalText(
  text: string,
  baseDirection: "rtl" | "ltr"
): string {
  // Use Unicode Bidirectional Algorithm markers
  const PDI = "\u2069"; // Pop Directional Isolate
  const LRI = "\u2066"; // Left-to-Right Isolate
  const RLI = "\u2067"; // Right-to-Left Isolate

  if (baseDirection === "rtl") {
    return `${RLI}${text}${PDI}`;
  }
  return `${LRI}${text}${PDI}`;
}

// ═══════════════════════════════════════════════════════════════════════════
// Agricultural Term Formatting
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Format yield value (kg/ha or ton/ha)
 */
export function formatYield(
  value: number,
  locale: Locale,
  unit: "kg/ha" | "ton/ha" = "kg/ha"
): string {
  const formatted = formatNumber(value, locale, {
    maximumFractionDigits: unit === "kg/ha" ? 0 : 2,
  });

  const unitLabels: Record<string, Record<Locale, string>> = {
    "kg/ha": { ar: "كجم/هـ", en: "kg/ha" },
    "ton/ha": { ar: "طن/هـ", en: "t/ha" },
  };

  return `${formatted} ${unitLabels[unit][locale]}`;
}

/**
 * Format water volume (liters or cubic meters)
 */
export function formatWaterVolume(
  value: number,
  locale: Locale,
  unit: "liter" | "m3" = "m3"
): string {
  const formatted = formatNumber(value, locale, {
    maximumFractionDigits: unit === "liter" ? 0 : 2,
  });

  const unitLabels: Record<string, Record<Locale, string>> = {
    liter: { ar: "لتر", en: "L" },
    m3: { ar: "م\u00b3", en: "m\u00b3" },
  };

  return `${formatted} ${unitLabels[unit][locale]}`;
}

/**
 * Format temperature
 */
export function formatTemperature(
  value: number,
  locale: Locale,
  unit: "celsius" | "fahrenheit" = "celsius"
): string {
  const formatted = formatNumber(value, locale, {
    maximumFractionDigits: 1,
  });

  const unitLabels: Record<string, Record<Locale, string>> = {
    celsius: { ar: "°م", en: "°C" },
    fahrenheit: { ar: "°ف", en: "°F" },
  };

  return `${formatted}${unitLabels[unit][locale]}`;
}

/**
 * Format soil moisture percentage
 */
export function formatSoilMoisture(value: number, locale: Locale): string {
  return formatPercent(value, locale, 0);
}

/**
 * Format NDVI value
 */
export function formatNDVI(value: number, locale: Locale): string {
  return formatNumber(value, locale, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// Exports for next-intl integration
// ═══════════════════════════════════════════════════════════════════════════

// Re-export next-intl utilities for convenience
export {
  useTranslations,
  useLocale,
  useMessages,
  useNow,
  useTimeZone,
  useFormatter,
  NextIntlClientProvider,
} from "next-intl";

export type { AbstractIntlMessages } from "next-intl";

// ═══════════════════════════════════════════════════════════════════════════
// Convenience object for importing all utilities
// ═══════════════════════════════════════════════════════════════════════════

export const i18n = {
  // Core
  messages,
  locales,
  defaultLocale,
  getMessages,
  getLocaleDisplayName,
  getLocaleNativeName,

  // Regional
  regionalConfigs,
  getRegionalConfig,

  // RTL
  isRTL,
  getDirection,
  getLogicalProperties,
  getHtmlAttributes,

  // Number formatting
  formatNumber,
  formatCurrency,
  formatPercent,
  formatArea,
  formatWeight,

  // Date formatting
  formatDate,
  formatHijriDate,
  formatTime,
  formatDateTime,
  formatRelativeTime,

  // Pluralization
  getPluralCategory,
  getArabicPluralCategory,
  formatPlural,

  // Text utilities
  containsArabic,
  isPrimarilyArabic,
  detectTextDirection,
  wrapWithDirection,
  formatBidirectionalText,

  // Agricultural formatting
  formatYield,
  formatWaterVolume,
  formatTemperature,
  formatSoilMoisture,
  formatNDVI,
};

export default i18n;
