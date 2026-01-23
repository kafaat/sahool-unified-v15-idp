/**
 * Internationalization (i18n) Tests for SAHOOL Platform
 *
 * Tests validate localization, translations, and bilingual support.
 */

import { describe, it, expect } from "vitest";
import {
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

  // Types
  type ArabicPluralCategory,
} from "../index";

// ═══════════════════════════════════════════════════════════════════════════
// Core i18n Tests
// ═══════════════════════════════════════════════════════════════════════════

describe("Core i18n", () => {
  describe("locales", () => {
    it("should have Arabic and English locales", () => {
      expect(locales).toContain("ar");
      expect(locales).toContain("en");
      expect(locales.length).toBe(2);
    });

    it("should have Arabic as default locale", () => {
      expect(defaultLocale).toBe("ar");
    });
  });

  describe("messages", () => {
    it("should have messages for both locales", () => {
      expect(messages.ar).toBeDefined();
      expect(messages.en).toBeDefined();
    });

    it("should have matching structure between locales", () => {
      const arKeys = Object.keys(messages.ar);
      const enKeys = Object.keys(messages.en);
      expect(arKeys).toEqual(enKeys);
    });
  });

  describe("getMessages", () => {
    it("should return messages for valid locale", () => {
      const arMessages = getMessages("ar");
      const enMessages = getMessages("en");
      expect(arMessages).toBe(messages.ar);
      expect(enMessages).toBe(messages.en);
    });
  });

  describe("getLocaleDisplayName", () => {
    it("should return Arabic name for ar locale", () => {
      expect(getLocaleDisplayName("ar")).toBe("العربية");
    });

    it("should return English name for en locale", () => {
      expect(getLocaleDisplayName("en")).toBe("English");
    });
  });

  describe("getLocaleNativeName", () => {
    it("should return both name and native name", () => {
      const ar = getLocaleNativeName("ar");
      expect(ar.name).toBe("Arabic");
      expect(ar.nativeName).toBe("العربية");

      const en = getLocaleNativeName("en");
      expect(en.name).toBe("English");
      expect(en.nativeName).toBe("English");
    });
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Regional Configuration Tests
// ═══════════════════════════════════════════════════════════════════════════

describe("Regional Configuration", () => {
  it("should have configuration for Yemen", () => {
    const config = regionalConfigs["ye"];
    expect(config.timeZone).toBe("Asia/Aden");
    expect(config.currency).toBe("YER");
    expect(config.currencySymbol).toBe("ر.ي");
  });

  it("should have configuration for Saudi Arabia", () => {
    const config = regionalConfigs["sa"];
    expect(config.timeZone).toBe("Asia/Riyadh");
    expect(config.currency).toBe("SAR");
    expect(config.dateFormat).toBe("hijri");
  });

  it("should have configuration for UAE", () => {
    const config = regionalConfigs["ae"];
    expect(config.timeZone).toBe("Asia/Dubai");
    expect(config.currency).toBe("AED");
  });

  describe("getRegionalConfig", () => {
    it("should return Yemen config by default", () => {
      const config = getRegionalConfig();
      expect(config.currency).toBe("YER");
    });

    it("should return correct config for specified region", () => {
      const saConfig = getRegionalConfig("sa");
      expect(saConfig.currency).toBe("SAR");
    });

    it("should return default config for unknown region", () => {
      const config = getRegionalConfig("unknown");
      expect(config.currency).toBe("YER");
    });
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// RTL Support Tests
// ═══════════════════════════════════════════════════════════════════════════

describe("RTL Support", () => {
  describe("isRTL", () => {
    it("should return true for Arabic", () => {
      expect(isRTL("ar")).toBe(true);
    });

    it("should return false for English", () => {
      expect(isRTL("en")).toBe(false);
    });
  });

  describe("getDirection", () => {
    it("should return rtl for Arabic", () => {
      expect(getDirection("ar")).toBe("rtl");
    });

    it("should return ltr for English", () => {
      expect(getDirection("en")).toBe("ltr");
    });
  });

  describe("getLogicalProperties", () => {
    it("should return RTL properties for Arabic", () => {
      const props = getLogicalProperties("ar");
      expect(props.start).toBe("right");
      expect(props.end).toBe("left");
      expect(props.textAlign).toBe("right");
      expect(props.marginInlineStart).toBe("marginRight");
      expect(props.paddingInlineEnd).toBe("paddingLeft");
    });

    it("should return LTR properties for English", () => {
      const props = getLogicalProperties("en");
      expect(props.start).toBe("left");
      expect(props.end).toBe("right");
      expect(props.textAlign).toBe("left");
      expect(props.marginInlineStart).toBe("marginLeft");
      expect(props.paddingInlineEnd).toBe("paddingRight");
    });
  });

  describe("getHtmlAttributes", () => {
    it("should return correct attributes for Arabic", () => {
      const attrs = getHtmlAttributes("ar");
      expect(attrs.lang).toBe("ar");
      expect(attrs.dir).toBe("rtl");
    });

    it("should return correct attributes for English", () => {
      const attrs = getHtmlAttributes("en");
      expect(attrs.lang).toBe("en");
      expect(attrs.dir).toBe("ltr");
    });
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Number Formatting Tests
// ═══════════════════════════════════════════════════════════════════════════

describe("Number Formatting", () => {
  describe("formatNumber", () => {
    it("should format numbers in English locale", () => {
      const result = formatNumber(1234567.89, "en");
      expect(result).toContain("1,234,567");
    });

    it("should format numbers in Arabic locale", () => {
      const result = formatNumber(1234567.89, "ar");
      expect(result).toBeDefined();
    });

    it("should support Arabic-Indic numerals", () => {
      const result = formatNumber(123, "ar", { useArabicNumerals: true });
      expect(result).toBeDefined();
    });

    it("should respect fraction digits options", () => {
      const result = formatNumber(123.456, "en", { maximumFractionDigits: 2 });
      expect(result).toBe("123.46");
    });
  });

  describe("formatCurrency", () => {
    it("should format YER currency", () => {
      const result = formatCurrency(1000, "ar", "YER");
      expect(result).toBeDefined();
    });

    it("should format SAR currency", () => {
      const result = formatCurrency(1500, "ar", "SAR");
      expect(result).toBeDefined();
    });

    it("should format USD currency in English", () => {
      const result = formatCurrency(1000, "en", "USD");
      expect(result).toContain("$");
    });
  });

  describe("formatPercent", () => {
    it("should format percentage in English", () => {
      const result = formatPercent(75, "en", 1);
      expect(result).toBe("75.0%");
    });

    it("should format percentage in Arabic", () => {
      const result = formatPercent(75, "ar", 0);
      expect(result).toBeDefined();
    });
  });

  describe("formatArea", () => {
    it("should format area in hectares", () => {
      const resultEn = formatArea(10.5, "en", "hectare");
      expect(resultEn).toBe("10.5 ha");

      const resultAr = formatArea(10.5, "ar", "hectare");
      expect(resultAr).toContain("هكتار");
    });

    it("should format area in square meters", () => {
      const result = formatArea(1000, "en", "sqm");
      expect(result).toContain("m\u00b2");
    });

    it("should format area in dunam", () => {
      const result = formatArea(5, "ar", "dunam");
      expect(result).toContain("دونم");
    });
  });

  describe("formatWeight", () => {
    it("should format weight in kg", () => {
      const resultEn = formatWeight(500, "en", "kg");
      expect(resultEn).toBe("500 kg");

      const resultAr = formatWeight(500, "ar", "kg");
      expect(resultAr).toContain("كجم");
    });

    it("should format weight in tons", () => {
      const result = formatWeight(2.5, "en", "ton");
      expect(result).toBe("2.5 t");
    });
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Date Formatting Tests
// ═══════════════════════════════════════════════════════════════════════════

describe("Date Formatting", () => {
  const testDate = new Date("2024-01-15T10:30:00Z");

  describe("formatDate", () => {
    it("should format date in English", () => {
      const result = formatDate(testDate, "en");
      expect(result).toBeDefined();
      expect(result).toContain("2024");
    });

    it("should format date in Arabic", () => {
      const result = formatDate(testDate, "ar");
      expect(result).toBeDefined();
    });

    it("should handle string dates", () => {
      const result = formatDate("2024-01-15", "en");
      expect(result).toBeDefined();
    });

    it("should handle timestamps", () => {
      const result = formatDate(testDate.getTime(), "en");
      expect(result).toBeDefined();
    });
  });

  describe("formatHijriDate", () => {
    it("should format date in Hijri calendar", () => {
      const result = formatHijriDate(testDate, "ar");
      expect(result).toBeDefined();
      // Hijri date should be different from Gregorian
    });
  });

  describe("formatTime", () => {
    it("should format time in English", () => {
      const result = formatTime(testDate, "en");
      expect(result).toBeDefined();
    });

    it("should format time in Arabic", () => {
      const result = formatTime(testDate, "ar");
      expect(result).toBeDefined();
    });
  });

  describe("formatDateTime", () => {
    it("should format datetime", () => {
      const result = formatDateTime(testDate, "en");
      expect(result).toBeDefined();
      expect(result).toContain("2024");
    });
  });

  describe("formatRelativeTime", () => {
    it("should format past time", () => {
      const pastDate = new Date(Date.now() - 3600000); // 1 hour ago
      const result = formatRelativeTime(pastDate, "en");
      expect(result).toBeDefined();
    });

    it("should format future time", () => {
      const futureDate = new Date(Date.now() + 86400000); // 1 day from now
      const result = formatRelativeTime(futureDate, "en");
      expect(result).toBeDefined();
    });

    it("should format in Arabic", () => {
      const pastDate = new Date(Date.now() - 7200000); // 2 hours ago
      const result = formatRelativeTime(pastDate, "ar");
      expect(result).toBeDefined();
    });
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Pluralization Tests
// ═══════════════════════════════════════════════════════════════════════════

describe("Pluralization", () => {
  describe("getArabicPluralCategory", () => {
    const testCases: [number, ArabicPluralCategory][] = [
      [0, "zero"],
      [1, "one"],
      [2, "two"],
      [3, "few"],
      [5, "few"],
      [10, "few"],
      [11, "many"],
      [25, "many"],
      [99, "many"],
      [100, "other"],
      [101, "other"],
      [103, "few"], // 103 % 100 = 3, which is "few"
      [111, "many"], // 111 % 100 = 11, which is "many"
    ];

    testCases.forEach(([num, expected]) => {
      it(`should return "${expected}" for ${num}`, () => {
        expect(getArabicPluralCategory(num)).toBe(expected);
      });
    });
  });

  describe("getPluralCategory", () => {
    it("should use Arabic rules for ar locale", () => {
      expect(getPluralCategory(5, "ar")).toBe("few");
      expect(getPluralCategory(25, "ar")).toBe("many");
    });

    it("should use English rules for en locale", () => {
      expect(getPluralCategory(0, "en")).toBe("zero");
      expect(getPluralCategory(1, "en")).toBe("one");
      expect(getPluralCategory(5, "en")).toBe("other");
    });
  });

  describe("formatPlural", () => {
    const fieldForms = {
      zero: "No fields",
      one: "1 field",
      two: "2 fields",
      few: "# fields",
      many: "# fields",
      other: "# fields",
    };

    const fieldFormsAr = {
      zero: "لا توجد حقول",
      one: "حقل واحد",
      two: "حقلان",
      few: "# حقول",
      many: "# حقلاً",
      other: "# حقل",
    };

    it("should format zero case", () => {
      expect(formatPlural(0, fieldForms, "en")).toBe("No fields");
      expect(formatPlural(0, fieldFormsAr, "ar")).toBe("لا توجد حقول");
    });

    it("should format one case", () => {
      expect(formatPlural(1, fieldForms, "en")).toBe("1 field");
      expect(formatPlural(1, fieldFormsAr, "ar")).toBe("حقل واحد");
    });

    it("should format two case (Arabic)", () => {
      expect(formatPlural(2, fieldFormsAr, "ar")).toBe("حقلان");
    });

    it("should format few case (Arabic)", () => {
      const result = formatPlural(5, fieldFormsAr, "ar");
      expect(result).toContain("حقول");
    });

    it("should format many case (Arabic)", () => {
      const result = formatPlural(25, fieldFormsAr, "ar");
      expect(result).toContain("حقلاً");
    });
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Text Utilities Tests
// ═══════════════════════════════════════════════════════════════════════════

describe("Text Utilities", () => {
  describe("containsArabic", () => {
    it("should return true for Arabic text", () => {
      expect(containsArabic("مرحبا")).toBe(true);
      expect(containsArabic("Hello مرحبا")).toBe(true);
    });

    it("should return false for English text", () => {
      expect(containsArabic("Hello World")).toBe(false);
      expect(containsArabic("123")).toBe(false);
    });
  });

  describe("isPrimarilyArabic", () => {
    it("should return true when majority is Arabic", () => {
      expect(isPrimarilyArabic("مرحبا بكم في سهول")).toBe(true);
    });

    it("should return false when majority is English", () => {
      expect(isPrimarilyArabic("Hello World مرحبا")).toBe(false);
    });
  });

  describe("detectTextDirection", () => {
    it("should detect RTL for Arabic text", () => {
      expect(detectTextDirection("مرحبا بكم")).toBe("rtl");
    });

    it("should detect LTR for English text", () => {
      expect(detectTextDirection("Hello World")).toBe("ltr");
    });
  });

  describe("wrapWithDirection", () => {
    it("should wrap RTL text with RLM markers", () => {
      const result = wrapWithDirection("مرحبا", "rtl");
      expect(result).toContain("\u200F"); // RLM
    });

    it("should wrap LTR text with LRM markers", () => {
      const result = wrapWithDirection("Hello", "ltr");
      expect(result).toContain("\u200E"); // LRM
    });
  });

  describe("formatBidirectionalText", () => {
    it("should wrap text with isolate markers", () => {
      const rtlResult = formatBidirectionalText("مرحبا", "rtl");
      expect(rtlResult).toContain("\u2067"); // RLI

      const ltrResult = formatBidirectionalText("Hello", "ltr");
      expect(ltrResult).toContain("\u2066"); // LRI
    });
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Agricultural Formatting Tests
// ═══════════════════════════════════════════════════════════════════════════

describe("Agricultural Formatting", () => {
  describe("formatYield", () => {
    it("should format yield in kg/ha", () => {
      const resultEn = formatYield(5000, "en", "kg/ha");
      expect(resultEn).toBe("5,000 kg/ha");

      const resultAr = formatYield(5000, "ar", "kg/ha");
      expect(resultAr).toContain("كجم/هـ");
    });

    it("should format yield in ton/ha", () => {
      const result = formatYield(4.5, "en", "ton/ha");
      expect(result).toBe("4.5 t/ha");
    });
  });

  describe("formatWaterVolume", () => {
    it("should format water volume in liters", () => {
      const result = formatWaterVolume(1000, "en", "liter");
      expect(result).toBe("1,000 L");
    });

    it("should format water volume in cubic meters", () => {
      const result = formatWaterVolume(250.5, "en", "m3");
      expect(result).toContain("m\u00b3");
    });

    it("should format in Arabic", () => {
      const result = formatWaterVolume(100, "ar", "liter");
      expect(result).toContain("لتر");
    });
  });

  describe("formatTemperature", () => {
    it("should format temperature in Celsius", () => {
      const resultEn = formatTemperature(25.5, "en", "celsius");
      expect(resultEn).toBe("25.5°C");

      const resultAr = formatTemperature(25.5, "ar", "celsius");
      expect(resultAr).toContain("°م");
    });

    it("should format temperature in Fahrenheit", () => {
      const result = formatTemperature(77, "en", "fahrenheit");
      expect(result).toBe("77°F");
    });
  });

  describe("formatSoilMoisture", () => {
    it("should format soil moisture as percentage", () => {
      const result = formatSoilMoisture(35, "en");
      expect(result).toBe("35%");
    });
  });

  describe("formatNDVI", () => {
    it("should format NDVI with 2 decimal places", () => {
      const result = formatNDVI(0.72, "en");
      expect(result).toBe("0.72");
    });

    it("should pad zeros for small values", () => {
      const result = formatNDVI(0.1, "en");
      expect(result).toBe("0.10");
    });
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Translation Completeness Tests
// ═══════════════════════════════════════════════════════════════════════════

describe("Translation Completeness", () => {
  function getNestedKeys(obj: object, prefix = ""): string[] {
    const keys: string[] = [];
    for (const [key, value] of Object.entries(obj)) {
      const fullKey = prefix ? `${prefix}.${key}` : key;
      if (typeof value === "object" && value !== null && !Array.isArray(value)) {
        keys.push(...getNestedKeys(value as object, fullKey));
      } else {
        keys.push(fullKey);
      }
    }
    return keys;
  }

  it("should have matching keys in both locales", () => {
    const arKeys = getNestedKeys(messages.ar).sort();
    const enKeys = getNestedKeys(messages.en).sort();
    expect(arKeys).toEqual(enKeys);
  });

  it("should have non-empty values for all Arabic translations", () => {
    const arKeys = getNestedKeys(messages.ar);
    const getValue = (obj: object, path: string): string => {
      return path.split(".").reduce((o: Record<string, unknown>, k) => o[k] as Record<string, unknown>, obj as Record<string, unknown>) as unknown as string;
    };

    const emptyKeys = arKeys.filter((key) => {
      const value = getValue(messages.ar, key);
      return typeof value === "string" && value.trim() === "";
    });

    expect(emptyKeys).toHaveLength(0);
  });

  it("should have Arabic characters in Arabic translations", () => {
    const arabicRegex = /[\u0600-\u06FF]/;

    // Check a sample of Arabic translations
    expect(arabicRegex.test(messages.ar.common.appName)).toBe(true);
    expect(arabicRegex.test(messages.ar.nav.dashboard)).toBe(true);
    expect(arabicRegex.test(messages.ar.crops.wheat)).toBe(true);
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Domain-Specific Translation Tests
// ═══════════════════════════════════════════════════════════════════════════

describe("Domain-Specific Translations", () => {
  describe("Crops", () => {
    it("should have translations for common crops", () => {
      const crops = ["wheat", "barley", "datePalm", "tomato", "cucumber"] as const;
      crops.forEach((crop) => {
        expect(messages.ar.crops[crop]).toBeDefined();
        expect(messages.en.crops[crop]).toBeDefined();
      });
    });
  });

  describe("Crop Stages", () => {
    it("should have translations for growth stages", () => {
      const stages = ["germination", "flowering", "harvest", "tillering"] as const;
      stages.forEach((stage) => {
        expect(messages.ar.cropStages[stage]).toBeDefined();
        expect(messages.en.cropStages[stage]).toBeDefined();
      });
    });
  });

  describe("Irrigation", () => {
    it("should have translations for irrigation methods", () => {
      expect(messages.ar.irrigation.drip).toBeDefined();
      expect(messages.ar.irrigation.sprinkler).toBeDefined();
      expect(messages.ar.irrigation.pivot).toBeDefined();
    });
  });

  describe("Weather", () => {
    it("should have translations for weather conditions", () => {
      const conditions = ["sunny", "cloudy", "rainy", "dusty"] as const;
      conditions.forEach((condition) => {
        expect(messages.ar.weather.conditions[condition]).toBeDefined();
        expect(messages.en.weather.conditions[condition]).toBeDefined();
      });
    });
  });

  describe("Sensors", () => {
    it("should have translations for sensor types", () => {
      const sensorTypes = ["temperature", "humidity", "soilMoisture", "ph"] as const;
      sensorTypes.forEach((type) => {
        expect(messages.ar.sensors.types[type]).toBeDefined();
        expect(messages.en.sensors.types[type]).toBeDefined();
      });
    });
  });

  describe("Islamic Calendar", () => {
    it("should have Hijri month names", () => {
      const months = ["muharram", "ramadan", "dhuAlHijjah"] as const;
      months.forEach((month) => {
        expect(messages.ar.time.hijriMonths[month]).toBeDefined();
        expect(messages.en.time.hijriMonths[month]).toBeDefined();
      });
    });
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Pluralization in Translations
// ═══════════════════════════════════════════════════════════════════════════

describe("Pluralization in Translations", () => {
  it("should have plural forms for Arabic", () => {
    const arPlurals = messages.ar.plurals;
    expect(arPlurals.field).toBeDefined();
    expect(arPlurals.farm).toBeDefined();
    expect(arPlurals.hectare).toBeDefined();

    // Arabic plurals should contain different forms
    expect(arPlurals.field).toContain("حقل");
    expect(arPlurals.field).toContain("حقلان"); // dual form
    expect(arPlurals.field).toContain("حقول"); // plural form
  });

  it("should have plural forms for English", () => {
    const enPlurals = messages.en.plurals;
    expect(enPlurals.field).toBeDefined();
    expect(enPlurals.farm).toBeDefined();
    expect(enPlurals.hectare).toBeDefined();
  });
});
