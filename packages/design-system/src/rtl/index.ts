/**
 * SAHOOL Design System - RTL (Right-to-Left) Utilities
 * Comprehensive support for Arabic language and bidirectional text
 *
 * Features:
 * - Logical CSS properties for automatic mirroring
 * - Arabic typography optimizations
 * - Bidirectional icon handling
 * - RTL-aware spacing utilities
 * - Mixed content support (Arabic + English)
 *
 * @packageDocumentation
 */

// ═══════════════════════════════════════════════════════════════════════════════
// Types
// ═══════════════════════════════════════════════════════════════════════════════

export type Direction = "ltr" | "rtl";
export type Language = "ar" | "en";

export interface RTLConfig {
  direction: Direction;
  language: Language;
  fontFamily: string;
  lineHeight: string;
  letterSpacing: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Constants
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Arabic-optimized configuration
 */
export const arabicConfig: RTLConfig = {
  direction: "rtl",
  language: "ar",
  fontFamily: '"IBM Plex Sans Arabic", "Noto Sans Arabic", "Tajawal", system-ui, sans-serif',
  lineHeight: "1.8",
  letterSpacing: "0.02em",
};

/**
 * English (LTR) configuration
 */
export const englishConfig: RTLConfig = {
  direction: "ltr",
  language: "en",
  fontFamily: '"Inter", "IBM Plex Sans", system-ui, sans-serif',
  lineHeight: "1.5",
  letterSpacing: "0",
};

// ═══════════════════════════════════════════════════════════════════════════════
// RTL-Aware Spacing Utilities
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Logical property utilities that automatically flip in RTL
 * Use these instead of physical properties (left/right)
 */
export const logicalSpacing = {
  // Margin-inline (horizontal margins)
  "ms-0": "ms-0",      // margin-inline-start: 0
  "ms-1": "ms-1",
  "ms-2": "ms-2",
  "ms-3": "ms-3",
  "ms-4": "ms-4",
  "ms-6": "ms-6",
  "ms-8": "ms-8",
  "ms-auto": "ms-auto",
  "me-0": "me-0",      // margin-inline-end: 0
  "me-1": "me-1",
  "me-2": "me-2",
  "me-3": "me-3",
  "me-4": "me-4",
  "me-6": "me-6",
  "me-8": "me-8",
  "me-auto": "me-auto",

  // Padding-inline (horizontal padding)
  "ps-0": "ps-0",      // padding-inline-start: 0
  "ps-1": "ps-1",
  "ps-2": "ps-2",
  "ps-3": "ps-3",
  "ps-4": "ps-4",
  "ps-6": "ps-6",
  "ps-8": "ps-8",
  "pe-0": "pe-0",      // padding-inline-end: 0
  "pe-1": "pe-1",
  "pe-2": "pe-2",
  "pe-3": "pe-3",
  "pe-4": "pe-4",
  "pe-6": "pe-6",
  "pe-8": "pe-8",

  // Positioning
  "start-0": "start-0",   // inset-inline-start: 0
  "start-1": "start-1",
  "start-2": "start-2",
  "start-4": "start-4",
  "start-auto": "start-auto",
  "end-0": "end-0",       // inset-inline-end: 0
  "end-1": "end-1",
  "end-2": "end-2",
  "end-4": "end-4",
  "end-auto": "end-auto",

  // Border
  "border-s": "border-s",      // border-inline-start
  "border-e": "border-e",      // border-inline-end
  "border-s-0": "border-s-0",
  "border-e-0": "border-e-0",
  "border-s-2": "border-s-2",
  "border-e-2": "border-e-2",
  "border-s-4": "border-s-4",
  "border-e-4": "border-e-4",

  // Rounded corners
  "rounded-s": "rounded-s",     // border-start-radius
  "rounded-e": "rounded-e",     // border-end-radius
  "rounded-ss": "rounded-ss",   // border-start-start-radius
  "rounded-se": "rounded-se",   // border-start-end-radius
  "rounded-es": "rounded-es",   // border-end-start-radius
  "rounded-ee": "rounded-ee",   // border-end-end-radius
} as const;

// ═══════════════════════════════════════════════════════════════════════════════
// RTL-Aware Text Utilities
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Text alignment utilities that respect RTL
 */
export const textAlignment = {
  /** Align to start (left in LTR, right in RTL) */
  start: "text-start",
  /** Align to end (right in LTR, left in RTL) */
  end: "text-end",
  /** Always center */
  center: "text-center",
  /** Justify text */
  justify: "text-justify",
} as const;

/**
 * Arabic typography enhancements
 */
export const arabicTypography = {
  /** Base Arabic text styling */
  base: [
    "font-arabic",
    "leading-relaxed",
    "tracking-wide",
  ].join(" "),

  /** Arabic heading styles */
  heading: [
    "font-arabic",
    "font-bold",
    "leading-normal",
    "tracking-normal",
  ].join(" "),

  /** Arabic body text */
  body: [
    "font-arabic",
    "text-base",
    "leading-loose",
    "tracking-wide",
  ].join(" "),

  /** Arabic small/caption text */
  caption: [
    "font-arabic",
    "text-sm",
    "leading-relaxed",
  ].join(" "),

  /** Numbers in Arabic text (use LTR for numbers) */
  number: [
    "font-sans",
    "tabular-nums",
    "ltr",
    "inline-block",
  ].join(" "),
} as const;

// ═══════════════════════════════════════════════════════════════════════════════
// Bidirectional Content Utilities
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * CSS classes for handling mixed direction content
 */
export const bidirectionalContent = {
  /** Force LTR for specific content (e.g., code, URLs, numbers) */
  forceLTR: "ltr inline-block",

  /** Force RTL for specific content */
  forceRTL: "rtl inline-block",

  /** Isolate bidirectional text */
  isolate: "[unicode-bidi:isolate]",

  /** Override bidirectional algorithm */
  override: "[unicode-bidi:bidi-override]",

  /** Embed LTR content in RTL context */
  embedLTR: "[unicode-bidi:embed] [direction:ltr]",

  /** Embed RTL content in LTR context */
  embedRTL: "[unicode-bidi:embed] [direction:rtl]",
} as const;

// ═══════════════════════════════════════════════════════════════════════════════
// RTL-Aware Flex Utilities
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Flex utilities that handle RTL correctly
 */
export const rtlFlex = {
  /** Row that reverses in RTL (default flex behavior) */
  row: "flex flex-row",

  /** Row that maintains direction in both LTR and RTL */
  rowFixed: "flex flex-row rtl:flex-row",

  /** Row that reverses in RTL */
  rowReverse: "flex flex-row rtl:flex-row-reverse",

  /** Row that reverses only in LTR (opposite behavior) */
  rowReverseLTR: "flex flex-row-reverse rtl:flex-row",

  /** Column (no change needed for RTL) */
  column: "flex flex-col",

  /** Justify items to start (respects RTL) */
  justifyStart: "justify-start",

  /** Justify items to end (respects RTL) */
  justifyEnd: "justify-end",

  /** Items alignment that respects RTL */
  itemsStart: "items-start",
  itemsEnd: "items-end",
} as const;

// ═══════════════════════════════════════════════════════════════════════════════
// RTL-Aware Icon Utilities
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Icons that should be mirrored in RTL
 * These are typically directional icons
 */
export const mirroredIcons = {
  /** Icons that should flip horizontally in RTL */
  mirror: "rtl:scale-x-[-1]",

  /** Icons that should NOT flip in RTL (e.g., checkmarks, social icons) */
  noMirror: "rtl:scale-x-100",

  /** Rotate icon for RTL (useful for arrows) */
  rotate180: "rtl:rotate-180",
} as const;

/**
 * Common directional icons that need mirroring
 */
export const directionalIcons = [
  "arrow-left",
  "arrow-right",
  "chevron-left",
  "chevron-right",
  "arrow-right-from-line",
  "arrow-left-from-line",
  "external-link",
  "reply",
  "forward",
  "undo",
  "redo",
  "indent",
  "outdent",
] as const;

// ═══════════════════════════════════════════════════════════════════════════════
// RTL-Aware Component Classes
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * RTL-aware navigation classes
 */
export const rtlNavigation = {
  /** Sidebar positioned at start */
  sidebarStart: "fixed start-0 top-0 h-full",

  /** Sidebar positioned at end */
  sidebarEnd: "fixed end-0 top-0 h-full",

  /** Breadcrumb separator */
  breadcrumbSeparator: "mx-2 rtl:rotate-180",

  /** Back button positioning */
  backButton: "absolute start-4 top-4",

  /** Forward/Next button positioning */
  nextButton: "absolute end-4 top-4",
} as const;

/**
 * RTL-aware form classes
 */
export const rtlForm = {
  /** Form field with label */
  fieldWrapper: "flex flex-col gap-1.5",

  /** Inline form field */
  inlineField: "flex items-center gap-2 rtl:flex-row-reverse",

  /** Checkbox/Radio with label */
  checkboxWrapper: "flex items-center gap-2",

  /** Input with icon */
  inputWithIconStart: "ps-10",
  inputWithIconEnd: "pe-10",

  /** Icon inside input (start) */
  inputIconStart: "absolute start-3 top-1/2 -translate-y-1/2",

  /** Icon inside input (end) */
  inputIconEnd: "absolute end-3 top-1/2 -translate-y-1/2",

  /** Error message */
  errorMessage: "text-sm text-error-main mt-1 text-start",

  /** Hint message */
  hintMessage: "text-sm text-neutral-500 mt-1 text-start",

  /** Required indicator */
  requiredIndicator: "text-error-main ms-1",
} as const;

/**
 * RTL-aware list classes
 */
export const rtlList = {
  /** List with start markers */
  markerStart: "[&>li]:ps-6 [&>li]:relative [&>li]:before:absolute [&>li]:before:start-0",

  /** Numbered list */
  orderedList: "list-decimal ps-6",

  /** Bulleted list */
  unorderedList: "list-disc ps-6",

  /** Description list */
  descriptionList: "[&>dt]:font-semibold [&>dd]:ps-4 [&>dd]:mb-2",
} as const;

// ═══════════════════════════════════════════════════════════════════════════════
// Utility Functions
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Get RTL configuration based on language
 */
export function getRTLConfig(language: Language): RTLConfig {
  return language === "ar" ? arabicConfig : englishConfig;
}

/**
 * Check if a language is RTL
 */
export function isRTLLanguage(language: string): boolean {
  const rtlLanguages = ["ar", "he", "fa", "ur", "ps", "sd", "yi"];
  return rtlLanguages.includes(language.toLowerCase().split("-")[0]);
}

/**
 * Get direction from language code
 */
export function getDirectionFromLanguage(language: string): Direction {
  return isRTLLanguage(language) ? "rtl" : "ltr";
}

/**
 * Create direction-aware class string
 * @param ltrClass - Class to apply in LTR mode
 * @param rtlClass - Class to apply in RTL mode
 */
export function directionClass(ltrClass: string, rtlClass: string): string {
  return `ltr:${ltrClass} rtl:${rtlClass}`;
}

/**
 * Create classes that apply only in RTL
 */
export function rtlOnly(className: string): string {
  return `rtl:${className}`;
}

/**
 * Create classes that apply only in LTR
 */
export function ltrOnly(className: string): string {
  return `ltr:${className}`;
}

/**
 * Swap left/right values for RTL
 * Useful for inline styles or CSS-in-JS
 */
export function swapForRTL<T>(ltrValue: T, rtlValue: T, isRTL: boolean): T {
  return isRTL ? rtlValue : ltrValue;
}

/**
 * Generate CSS for RTL layout
 */
export function generateRTLCSS(): string {
  return `
/* RTL Base Styles */
[dir="rtl"] {
  direction: rtl;
  text-align: right;
}

/* Arabic Font Stack */
[dir="rtl"],
[lang="ar"] {
  font-family: ${arabicConfig.fontFamily};
  line-height: ${arabicConfig.lineHeight};
  letter-spacing: ${arabicConfig.letterSpacing};
}

/* Preserve LTR for specific content */
[dir="rtl"] .ltr,
[dir="rtl"] code,
[dir="rtl"] pre,
[dir="rtl"] [dir="ltr"] {
  direction: ltr;
  text-align: left;
}

/* Numbers in RTL context */
[dir="rtl"] .tabular-nums {
  font-variant-numeric: tabular-nums;
  direction: ltr;
  display: inline-block;
}

/* Icon mirroring */
[dir="rtl"] .rtl-mirror {
  transform: scaleX(-1);
}

/* Scrollbar positioning */
[dir="rtl"] {
  scrollbar-gutter: stable both-edges;
}

/* Dialog/Modal positioning */
[dir="rtl"] [data-radix-dialog-content] {
  text-align: right;
}

/* Form alignment */
[dir="rtl"] input,
[dir="rtl"] textarea,
[dir="rtl"] select {
  text-align: inherit;
}

/* Table alignment */
[dir="rtl"] th,
[dir="rtl"] td {
  text-align: right;
}

/* Flexbox gap handling */
[dir="rtl"] .gap-x-2 {
  column-gap: 0.5rem;
}
`;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Arabic Number Formatting
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Arabic-Indic numerals mapping
 */
export const arabicIndic: Record<string, string> = {
  "0": "\u0660",
  "1": "\u0661",
  "2": "\u0662",
  "3": "\u0663",
  "4": "\u0664",
  "5": "\u0665",
  "6": "\u0666",
  "7": "\u0667",
  "8": "\u0668",
  "9": "\u0669",
};

/**
 * Convert Western numerals to Arabic-Indic numerals
 */
export function toArabicNumerals(num: number | string): string {
  return String(num).replace(/[0-9]/g, (d) => arabicIndic[d] || d);
}

/**
 * Format number for Arabic display
 * Keeps Western numerals but formats with Arabic conventions
 */
export function formatArabicNumber(
  num: number,
  options?: Intl.NumberFormatOptions
): string {
  return new Intl.NumberFormat("ar-SA", {
    useGrouping: true,
    ...options,
  }).format(num);
}

/**
 * Format currency for Arabic display
 */
export function formatArabicCurrency(
  amount: number,
  currency = "SAR"
): string {
  return new Intl.NumberFormat("ar-SA", {
    style: "currency",
    currency,
  }).format(amount);
}

/**
 * Format date for Arabic display
 */
export function formatArabicDate(
  date: Date,
  options?: Intl.DateTimeFormatOptions
): string {
  return new Intl.DateTimeFormat("ar-SA", {
    dateStyle: "long",
    ...options,
  }).format(date);
}

// ═══════════════════════════════════════════════════════════════════════════════
// Tailwind RTL Plugin Configuration
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Tailwind CSS configuration for RTL support
 * Include this in your tailwind.config.js
 */
export const tailwindRTLConfig = {
  theme: {
    extend: {
      fontFamily: {
        arabic: [
          "IBM Plex Sans Arabic",
          "Noto Sans Arabic",
          "Tajawal",
          "system-ui",
          "sans-serif",
        ],
      },
    },
  },
  plugins: [
    // RTL plugin for automatic logical properties
    // eslint-disable-next-line @typescript-eslint/no-require-imports
    // require('tailwindcss-rtl'),
  ],
} as const;

// ═══════════════════════════════════════════════════════════════════════════════
// Export all utilities
// ═══════════════════════════════════════════════════════════════════════════════

export const rtlUtils = {
  spacing: logicalSpacing,
  text: textAlignment,
  typography: arabicTypography,
  bidi: bidirectionalContent,
  flex: rtlFlex,
  icons: mirroredIcons,
  navigation: rtlNavigation,
  form: rtlForm,
  list: rtlList,
} as const;
