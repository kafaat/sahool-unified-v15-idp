/**
 * AI Context Compression Module
 * ==============================
 * وحدة ضغط السياق للذكاء الاصطناعي
 *
 * Provides context compression utilities for optimizing AI context windows.
 * Supports field data, weather data, and history compression with Arabic text support.
 *
 * المميزات:
 * - ضغط بيانات الحقول الزراعية
 * - ضغط بيانات الطقس والمناخ
 * - ضغط سجل العمليات
 * - دعم النص العربي
 * - تقدير عدد الرموز (Tokens)
 *
 * Author: SAHOOL Platform Team
 * Updated: January 2025
 */

// ─────────────────────────────────────────────────────────────────────────────
// Constants & Configuration
// ─────────────────────────────────────────────────────────────────────────────

// Average characters per token for different languages
// Arabic text typically has ~2.5 characters per token due to word structure
const CHARS_PER_TOKEN_ARABIC = 2.5;
const CHARS_PER_TOKEN_ENGLISH = 4.0;
const CHARS_PER_TOKEN_MIXED = 3.0;

// Default compression ratios
const DEFAULT_FIELD_COMPRESSION_RATIO = 0.3;
const DEFAULT_WEATHER_COMPRESSION_RATIO = 0.4;
const DEFAULT_HISTORY_COMPRESSION_RATIO = 0.25;

// ─────────────────────────────────────────────────────────────────────────────
// Enums & Models
// ─────────────────────────────────────────────────────────────────────────────

export enum CompressionStrategy {
  /** Extract key sentences / استخراج الجمل الرئيسية */
  EXTRACTIVE = "extractive",
  /** Generate summaries / إنشاء ملخصات */
  ABSTRACTIVE = "abstractive",
  /** Combine both approaches / دمج كلا النهجين */
  HYBRID = "hybrid",
  /** Select most relevant fields / اختيار أكثر الحقول صلة */
  SELECTIVE = "selective",
}

export interface CompressionResult {
  /** النص الأصلي - Original text before compression */
  originalText: string;
  /** النص المضغوط - Compressed text output */
  compressedText: string;
  /** عدد الرموز الأصلية - Estimated original token count */
  originalTokens: number;
  /** عدد الرموز المضغوطة - Estimated compressed token count */
  compressedTokens: number;
  /** نسبة الضغط - Compression ratio achieved */
  compressionRatio: number;
  /** الاستراتيجية - Strategy used for compression */
  strategy: CompressionStrategy;
  /** البيانات الوصفية - Additional metadata about compression */
  metadata: Record<string, unknown>;
}

// ─────────────────────────────────────────────────────────────────────────────
// Token Estimation
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Estimate the number of tokens in a text.
 * تقدير عدد الرموز في النص
 *
 * @param text - النص المراد تقدير رموزه - Text to estimate tokens for
 * @param language - لغة النص - Language hint ("ar", "en", "auto")
 * @returns عدد الرموز المقدر - Estimated token count
 *
 * Note: This is an approximation. For exact counts, use a tokenizer like tiktoken.
 * هذا تقدير تقريبي. للحصول على عدد دقيق، استخدم مُرمِّز مثل tiktoken.
 */
export function estimateTokens(text: string, language: string = "auto"): number {
  if (!text) {
    return 0;
  }

  const detectedLanguage = language === "auto" ? detectPrimaryLanguage(text) : language;

  const charsPerToken: Record<string, number> = {
    ar: CHARS_PER_TOKEN_ARABIC,
    en: CHARS_PER_TOKEN_ENGLISH,
    mixed: CHARS_PER_TOKEN_MIXED,
  };

  const tokenRatio = charsPerToken[detectedLanguage] || CHARS_PER_TOKEN_MIXED;

  // Account for whitespace and special characters
  const charCount = text.length;
  const whitespaceCount = (text.match(/\s/g) || []).length;
  const specialCount = (text.match(/[^\w\s]/g) || []).length;

  // Adjust for whitespace (doesn't add tokens in most tokenizers)
  const effectiveChars = charCount - whitespaceCount * 0.5;

  // Special characters often become individual tokens
  const specialTokenAdjustment = specialCount * 0.5;

  const estimatedTokens = effectiveChars / tokenRatio + specialTokenAdjustment;

  return Math.max(1, Math.floor(estimatedTokens));
}

/**
 * Detect the primary language of text.
 * تحديد اللغة الأساسية للنص
 *
 * @param text - النص - Text to analyze
 * @returns كود اللغة - Language code ("ar", "en", or "mixed")
 */
export function detectPrimaryLanguage(text: string): string {
  if (!text) {
    return "en";
  }

  // Count Arabic characters (Unicode range for Arabic)
  const arabicChars = (text.match(/[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]/g) || [])
    .length;
  // Count Latin characters
  const latinChars = (text.match(/[a-zA-Z]/g) || []).length;

  const totalChars = arabicChars + latinChars;
  if (totalChars === 0) {
    return "en";
  }

  const arabicRatio = arabicChars / totalChars;

  if (arabicRatio > 0.7) {
    return "ar";
  } else if (arabicRatio < 0.3) {
    return "en";
  } else {
    return "mixed";
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Context Compressor Class
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Context compression for AI interactions.
 * ضاغط السياق للتفاعلات مع الذكاء الاصطناعي
 *
 * Provides compression utilities for field data, weather data, and
 * operational history to optimize AI context window usage.
 *
 * يوفر أدوات ضغط لبيانات الحقول وبيانات الطقس وسجل العمليات
 * لتحسين استخدام نافذة سياق الذكاء الاصطناعي.
 */
export class ContextCompressor {
  private defaultStrategy: CompressionStrategy;
  private maxTokens: number;
  private preserveArabicDiacritics: boolean;
  private priorityFieldKeys: Set<string>;
  private priorityWeatherKeys: Set<string>;

  constructor(
    defaultStrategy: CompressionStrategy = CompressionStrategy.HYBRID,
    maxTokens: number = 4000,
    preserveArabicDiacritics: boolean = false,
  ) {
    /**
     * Initialize the context compressor.
     * تهيئة ضاغط السياق
     *
     * @param defaultStrategy - الاستراتيجية الافتراضية - Default compression strategy
     * @param maxTokens - الحد الأقصى للرموز - Maximum tokens target
     * @param preserveArabicDiacritics - الحفاظ على التشكيل - Keep Arabic diacritics
     */
    this.defaultStrategy = defaultStrategy;
    this.maxTokens = maxTokens;
    this.preserveArabicDiacritics = preserveArabicDiacritics;

    // Key field names for prioritization (English and Arabic)
    this.priorityFieldKeys = new Set([
      // English
      "field_id",
      "name",
      "area",
      "crop_type",
      "crop",
      "status",
      "health",
      "ndvi",
      "irrigation_status",
      "soil_type",
      "location",
      // Arabic
      "اسم_الحقل",
      "المساحة",
      "نوع_المحصول",
      "الحالة",
      "الصحة",
    ]);

    // Key weather fields
    this.priorityWeatherKeys = new Set([
      "temperature",
      "humidity",
      "precipitation",
      "wind_speed",
      "forecast",
      "alert",
      "درجة_الحرارة",
      "الرطوبة",
      "الأمطار",
    ]);
  }

  /**
   * Compress field data for AI context.
   * ضغط بيانات الحقل لسياق الذكاء الاصطناعي
   *
   * @param fieldData - بيانات الحقل - Field data dict or list of fields
   * @param strategy - الاستراتيجية - Compression strategy (optional)
   * @param targetRatio - نسبة الضغط المستهدفة - Target compression ratio
   * @returns نتيجة الضغط - Compression result
   */
  compressFieldData(
    fieldData: Record<string, unknown> | Array<Record<string, unknown>>,
    strategy?: CompressionStrategy,
    targetRatio: number = DEFAULT_FIELD_COMPRESSION_RATIO,
  ): CompressionResult {
    const selectedStrategy = strategy || this.defaultStrategy;

    // Convert to list if single dict
    const fields = Array.isArray(fieldData) ? fieldData : [fieldData];

    // Build original text representation
    const originalText = this._dictToText(fields);
    const originalTokens = estimateTokens(originalText);

    // Apply compression strategy
    let compressedFields: Array<Record<string, unknown>>;

    if (selectedStrategy === CompressionStrategy.SELECTIVE) {
      compressedFields = this._selectiveCompressFields(fields);
    } else if (selectedStrategy === CompressionStrategy.EXTRACTIVE) {
      compressedFields = this._extractiveCompressFields(fields, targetRatio);
    } else if (selectedStrategy === CompressionStrategy.ABSTRACTIVE) {
      compressedFields = this._abstractiveCompressFields(fields);
    } else {
      // HYBRID
      compressedFields = this._hybridCompressFields(fields, targetRatio);
    }

    const compressedText = this._dictToText(compressedFields);
    const compressedTokens = estimateTokens(compressedText);

    const actualRatio = compressedTokens / Math.max(originalTokens, 1);

    return {
      originalText,
      compressedText,
      originalTokens,
      compressedTokens,
      compressionRatio: actualRatio,
      strategy: selectedStrategy,
      metadata: {
        fieldCount: fields.length,
        keysPreserved: Array.from(this.priorityFieldKeys),
        targetRatio,
      },
    };
  }

  /**
   * Compress weather data for AI context.
   * ضغط بيانات الطقس لسياق الذكاء الاصطناعي
   *
   * @param weatherData - بيانات الطقس - Weather data dict or list
   * @param strategy - الاستراتيجية - Compression strategy (optional)
   * @param includeForecastDays - أيام التوقعات - Number of forecast days to include
   * @returns نتيجة الضغط - Compression result
   */
  compressWeatherData(
    weatherData: Record<string, unknown> | Array<Record<string, unknown>>,
    strategy?: CompressionStrategy,
    includeForecastDays: number = 3,
  ): CompressionResult {
    const selectedStrategy = strategy || this.defaultStrategy;

    // Handle single dict or list
    const weatherList = Array.isArray(weatherData) ? weatherData : [weatherData];

    const originalText = this._dictToText(weatherList);
    const originalTokens = estimateTokens(originalText);

    const compressedWeather = weatherList.map((weather) =>
      this._compressSingleWeather(weather, includeForecastDays),
    );

    const compressedText = this._dictToText(compressedWeather);
    const compressedTokens = estimateTokens(compressedText);

    const actualRatio = compressedTokens / Math.max(originalTokens, 1);

    return {
      originalText,
      compressedText,
      originalTokens,
      compressedTokens,
      compressionRatio: actualRatio,
      strategy: selectedStrategy,
      metadata: {
        forecastDaysIncluded: includeForecastDays,
        hasAlerts: weatherList.some((w) => "alert" in w || "alerts" in w),
      },
    };
  }

  /**
   * Compress operational history for AI context.
   * ضغط سجل العمليات لسياق الذكاء الاصطناعي
   *
   * Uses a sliding window approach to preserve recent entries while
   * summarizing older history.
   *
   * يستخدم نهج النافذة المنزلقة للحفاظ على الإدخالات الأخيرة
   * مع تلخيص السجل الأقدم.
   *
   * @param history - سجل العمليات - List of history entries
   * @param maxEntries - الحد الأقصى للإدخالات - Maximum entries to include
   * @param strategy - الاستراتيجية - Compression strategy (optional)
   * @param preserveRecent - عدد الإدخالات الحديثة - Recent entries to preserve fully
   * @returns نتيجة الضغط - Compression result
   */
  compressHistory(
    history: Array<Record<string, unknown>>,
    maxEntries: number = 10,
    strategy?: CompressionStrategy,
    preserveRecent: number = 3,
  ): CompressionResult {
    const selectedStrategy = strategy || this.defaultStrategy;

    if (!history || history.length === 0) {
      return {
        originalText: "",
        compressedText: "",
        originalTokens: 0,
        compressedTokens: 0,
        compressionRatio: 1.0,
        strategy: selectedStrategy,
        metadata: { entriesCount: 0 },
      };
    }

    const originalText = this._dictToText(history);
    const originalTokens = estimateTokens(originalText);

    // Sort by date if available (most recent first)
    const sortedHistory = this._sortByDate(history);

    // Preserve recent entries fully
    const recentEntries = sortedHistory.slice(0, preserveRecent);
    const olderEntries = sortedHistory.slice(preserveRecent);

    // Compress older entries
    const compressedOlder = this._compressOlderHistory(
      olderEntries,
      maxEntries - preserveRecent,
    );

    // Combine
    const compressedHistory = [...recentEntries, ...compressedOlder];

    const compressedText = this._dictToText(compressedHistory);
    const compressedTokens = estimateTokens(compressedText);

    const actualRatio = compressedTokens / Math.max(originalTokens, 1);

    return {
      originalText,
      compressedText,
      originalTokens,
      compressedTokens,
      compressionRatio: actualRatio,
      strategy: selectedStrategy,
      metadata: {
        originalEntries: history.length,
        compressedEntries: compressedHistory.length,
        recentPreserved: preserveRecent,
      },
    };
  }

  /**
   * Compress Arabic text specifically.
   * ضغط النص العربي بشكل خاص
   *
   * Handles Arabic-specific compression including:
   * - Removing diacritics (تشكيل) if allowed
   * - Condensing repeated phrases
   * - Removing redundant conjunctions
   *
   * @param text - النص العربي - Arabic text to compress
   * @param targetTokens - عدد الرموز المستهدف - Target token count
   * @param preserveMeaning - الحفاظ على المعنى - Preserve semantic meaning
   * @returns نتيجة الضغط - Compression result
   */
  compressArabicText(
    text: string,
    targetTokens?: number,
    preserveMeaning: boolean = true,
  ): CompressionResult {
    const originalTokens = estimateTokens(text, "ar");
    const target = targetTokens || Math.floor(originalTokens * 0.5);

    let compressedText = text;

    // Step 1: Remove diacritics if not preserving
    if (!this.preserveArabicDiacritics) {
      compressedText = this._removeArabicDiacritics(compressedText);
    }

    // Step 2: Normalize Arabic characters
    compressedText = this._normalizeArabic(compressedText);

    // Step 3: Remove redundant conjunctions and filler words
    if (!preserveMeaning) {
      compressedText = this._removeArabicFillers(compressedText);
    }

    // Step 4: Condense repeated information
    compressedText = this._condenseRepetitions(compressedText);

    // Step 5: Trim to target if still over
    let currentTokens = estimateTokens(compressedText, "ar");
    if (currentTokens > target) {
      compressedText = this._truncateToTokens(compressedText, target, "ar");
    }

    const compressedTokens = estimateTokens(compressedText, "ar");
    const actualRatio = compressedTokens / Math.max(originalTokens, 1);

    return {
      originalText: text,
      compressedText,
      originalTokens,
      compressedTokens,
      compressionRatio: actualRatio,
      strategy: CompressionStrategy.HYBRID,
      metadata: {
        language: "ar",
        diacriticsRemoved: !this.preserveArabicDiacritics,
        meaningPreserved: preserveMeaning,
      },
    };
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Private Helper Methods
  // ─────────────────────────────────────────────────────────────────────────

  private _dictToText(data: unknown): string {
    if (typeof data === "string") {
      return data;
    }
    return JSON.stringify(data, null, 2);
  }

  private _selectiveCompressFields(
    fields: Array<Record<string, unknown>>,
  ): Array<Record<string, unknown>> {
    const compressed: Array<Record<string, unknown>> = [];
    for (const fieldData of fields) {
      const compressedField: Record<string, unknown> = {};
      for (const [key, value] of Object.entries(fieldData)) {
        const keyLower = key.toLowerCase().replace(/ /g, "_");
        if (this.priorityFieldKeys.has(keyLower) || this.priorityFieldKeys.has(key)) {
          compressedField[key] = value;
        }
      }
      compressed.push(compressedField);
    }
    return compressed;
  }

  private _extractiveCompressFields(
    fields: Array<Record<string, unknown>>,
    targetRatio: number,
  ): Array<Record<string, unknown>> {
    // Start with selective compression
    const compressed = this._selectiveCompressFields(fields);

    // Add additional important fields based on target ratio
    for (let i = 0; i < fields.length; i++) {
      for (const [key, value] of Object.entries(fields[i])) {
        if (!(key in compressed[i]) && this._isImportantValue(value)) {
          compressed[i][key] = value;
        }
      }
    }

    return compressed;
  }

  private _abstractiveCompressFields(
    fields: Array<Record<string, unknown>>,
  ): Array<Record<string, unknown>> {
    const compressed: Array<Record<string, unknown>> = [];
    for (const fieldData of fields) {
      const summary: Record<string, unknown> = {
        summary: this._createFieldSummary(fieldData),
      };
      // Include critical identifiers
      for (const key of ["field_id", "id", "name"]) {
        if (key in fieldData) {
          summary[key] = fieldData[key];
        }
      }
      compressed.push(summary);
    }
    return compressed;
  }

  private _hybridCompressFields(
    fields: Array<Record<string, unknown>>,
    targetRatio: number,
  ): Array<Record<string, unknown>> {
    const compressed: Array<Record<string, unknown>> = [];
    for (const fieldData of fields) {
      const compressedField: Record<string, unknown> = {};

      // Keep priority fields
      for (const [key, value] of Object.entries(fieldData)) {
        const keyLower = key.toLowerCase().replace(/ /g, "_");
        if (this.priorityFieldKeys.has(keyLower) || this.priorityFieldKeys.has(key)) {
          compressedField[key] = value;
        }
      }

      // Add summary for complex nested data
      const nestedKeys = Object.entries(fieldData)
        .filter(([, v]) => typeof v === "object" && v !== null)
        .map(([k]) => k);
      if (nestedKeys.length > 0) {
        compressedField["_nested_summary"] = `Contains: ${nestedKeys.join(", ")}`;
      }

      compressed.push(compressedField);
    }
    return compressed;
  }

  private _compressSingleWeather(
    weather: Record<string, unknown>,
    forecastDays: number,
  ): Record<string, unknown> {
    const compressed: Record<string, unknown> = {};

    // Always include current conditions
    if ("current" in weather && typeof weather.current === "object") {
      compressed["current"] = this._extractKeyWeatherFields(
        weather.current as Record<string, unknown>,
      );
    }

    // Include limited forecast
    if ("forecast" in weather && Array.isArray(weather.forecast)) {
      compressed["forecast"] = weather.forecast
        .slice(0, forecastDays)
        .map((day) => this._extractKeyWeatherFields(day as Record<string, unknown>));
    }

    // Always include alerts
    if ("alerts" in weather) {
      compressed["alerts"] = weather.alerts;
    } else if ("alert" in weather) {
      compressed["alert"] = weather.alert;
    }

    // Include any other priority keys
    for (const [key, value] of Object.entries(weather)) {
      if (!(key in compressed) && this.priorityWeatherKeys.has(key.toLowerCase())) {
        compressed[key] = value;
      }
    }

    return compressed;
  }

  private _extractKeyWeatherFields(
    data: Record<string, unknown>,
  ): Record<string, unknown> {
    if (!data || typeof data !== "object") {
      return data;
    }

    const extracted: Record<string, unknown> = {};
    for (const [key, value] of Object.entries(data)) {
      const keyLower = key.toLowerCase();
      const hasPriority = Array.from(this.priorityWeatherKeys).some((pk) =>
        keyLower.includes(pk.toLowerCase()),
      );
      if (hasPriority) {
        extracted[key] = value;
      }
    }

    return Object.keys(extracted).length > 0 ? extracted : data;
  }

  private _sortByDate(history: Array<Record<string, unknown>>): Array<Record<string, unknown>> {
    const dateKeys = ["date", "timestamp", "created_at", "time", "التاريخ"];

    const getDate = (entry: Record<string, unknown>): Date => {
      for (const key of dateKeys) {
        if (key in entry) {
          const value = entry[key];
          if (value instanceof Date) {
            return value;
          }
          if (typeof value === "string") {
            try {
              return new Date(value.replace("Z", "+00:00"));
            } catch {
              // Continue to next key
            }
          }
        }
      }
      return new Date(0);
    };

    return [...history].sort((a, b) => getDate(b).getTime() - getDate(a).getTime());
  }

  private _compressOlderHistory(
    history: Array<Record<string, unknown>>,
    maxEntries: number,
  ): Array<Record<string, unknown>> {
    if (!history || history.length === 0 || maxEntries <= 0) {
      return [];
    }

    if (history.length <= maxEntries) {
      // Just remove non-essential fields
      return history.map((entry) => this._compressHistoryEntry(entry));
    }

    // Group by action type and summarize
    const actionGroups: Record<string, Array<Record<string, unknown>>> = {};
    for (const entry of history) {
      const action = (entry.action as string) || (entry.type as string) || "unknown";
      if (!(action in actionGroups)) {
        actionGroups[action] = [];
      }
      actionGroups[action].push(entry);
    }

    // Create summary entries
    const summaries: Array<Record<string, unknown>> = [];
    for (const [action, entries] of Object.entries(actionGroups)) {
      if (entries.length === 1) {
        summaries.push(this._compressHistoryEntry(entries[0]));
      } else {
        summaries.push({
          action,
          count: entries.length,
          summary: `${action}: ${entries.length} occurrences`,
          date_range: this._getDateRange(entries),
        });
      }
    }

    return summaries.slice(0, maxEntries);
  }

  private _compressHistoryEntry(entry: Record<string, unknown>): Record<string, unknown> {
    const importantKeys = new Set([
      "date",
      "timestamp",
      "action",
      "type",
      "status",
      "result",
      "field_id",
      "التاريخ",
      "الإجراء",
    ]);

    const result: Record<string, unknown> = {};
    for (const [k, v] of Object.entries(entry)) {
      if (importantKeys.has(k)) {
        result[k] = v;
      }
    }
    return result;
  }

  private _getDateRange(entries: Array<Record<string, unknown>>): string {
    const sortedEntries = this._sortByDate(entries);
    if (sortedEntries.length === 0) {
      return "unknown";
    }

    const first = sortedEntries[sortedEntries.length - 1].date ||
      sortedEntries[sortedEntries.length - 1].timestamp || "?";
    const last = sortedEntries[0].date || sortedEntries[0].timestamp || "?";

    return `${first} to ${last}`;
  }

  private _isImportantValue(value: unknown): boolean {
    if (value === null || value === undefined) {
      return false;
    }
    if (typeof value === "boolean") {
      return value; // True values are important
    }
    if (typeof value === "number") {
      return value !== 0;
    }
    if (typeof value === "string") {
      return value.length < 100 && value.length > 0;
    }
    return false;
  }

  private _createFieldSummary(field: Record<string, unknown>): string {
    const parts: string[] = [];

    const name = (field.name as string) || (field.اسم_الحقل as string) || "Unknown";
    parts.push(`Field: ${name}`);

    if ("area" in field || "المساحة" in field) {
      const area = field.area || field.المساحة;
      parts.push(`Area: ${area}`);
    }

    if ("crop" in field || "crop_type" in field || "نوع_المحصول" in field) {
      const crop = field.crop || field.crop_type || field.نوع_المحصول;
      parts.push(`Crop: ${crop}`);
    }

    if ("status" in field || "الحالة" in field) {
      const status = field.status || field.الحالة;
      parts.push(`Status: ${status}`);
    }

    return parts.join(" | ");
  }

  private _removeArabicDiacritics(text: string): string {
    // Arabic diacritics Unicode range
    return text.replace(/[\u064B-\u065F\u0670]/g, "");
  }

  private _normalizeArabic(text: string): string {
    // Normalize alef variations
    let result = text.replace(/[إأآا]/g, "ا");
    // Normalize yaa
    result = result.replace(/[ىي]/g, "ي");
    // Normalize taa marbouta
    result = result.replace(/ة/g, "ه");
    return result;
  }

  private _removeArabicFillers(text: string): string {
    // Common filler words in Arabic
    const fillers = [
      /\bو\s+/, // و (and) at word boundary
      /\bمن\s+/, // من (from)
      /\bإلى\s+/, // إلى (to)
      /\bفي\s+/, // في (in)
      /\bعلى\s+/, // على (on)
      /\bهذا\s+/, // هذا (this)
      /\bهذه\s+/, // هذه (this f)
      /\bالذي\s+/, // الذي (which)
      /\bالتي\s+/, // التي (which f)
    ];

    let result = text;
    for (const filler of fillers) {
      // Only remove if not changing meaning significantly
      const testRemoval = result.replace(filler, "");
      if (testRemoval.length > result.length * 0.5) {
        // Don't remove too much
        result = testRemoval;
      }
    }

    return result;
  }

  private _condenseRepetitions(text: string): string {
    // Remove duplicate consecutive words
    let result = text.replace(/\b(\w+)\s+\1\b/g, "$1");

    // Remove multiple spaces
    result = result.replace(/\s+/g, " ");

    // Remove repeated punctuation
    result = result.replace(/([.،,!?])\1+/g, "$1");

    return result.trim();
  }

  private _truncateToTokens(text: string, targetTokens: number, language: string): string {
    const currentTokens = estimateTokens(text, language);
    if (currentTokens <= targetTokens) {
      return text;
    }

    // Estimate characters needed
    const charsPerToken: Record<string, number> = {
      ar: CHARS_PER_TOKEN_ARABIC,
      en: CHARS_PER_TOKEN_ENGLISH,
      mixed: CHARS_PER_TOKEN_MIXED,
    };

    const tokenRatio = charsPerToken[language] || CHARS_PER_TOKEN_MIXED;
    const targetChars = Math.floor(targetTokens * tokenRatio);

    // Truncate at word boundary
    if (text.length > targetChars) {
      let truncated = text.substring(0, targetChars);
      const lastSpace = truncated.lastIndexOf(" ");
      if (lastSpace > targetChars * 0.8) {
        truncated = truncated.substring(0, lastSpace);
      }
      return truncated + "...";
    }

    return text;
  }
}
