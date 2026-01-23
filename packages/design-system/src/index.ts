/**
 * SAHOOL Design System
 * Unified design tokens, components, themes, and utilities
 *
 * A comprehensive design system for the SAHOOL Agricultural Intelligence Platform
 * supporting:
 * - Light and dark themes
 * - RTL/LTR layouts (Arabic/English)
 * - Agricultural domain-specific colors and components
 * - WCAG 2.1 AA accessibility compliance
 *
 * @packageDocumentation
 */

// ═══════════════════════════════════════════════════════════════════════════════
// Tokens
// ═══════════════════════════════════════════════════════════════════════════════

export { tokens } from "../tokens/tokens";
export type { TokenColors, TokenSpacing } from "../tokens/tokens";

// ═══════════════════════════════════════════════════════════════════════════════
// Themes
// ═══════════════════════════════════════════════════════════════════════════════

export * from "./themes";
export {
  lightTheme,
  darkTheme,
  themes,
  defaultTheme,
  getTheme,
  initializeTheme,
  applyTheme,
  applyDirection,
  getNDVIColor,
  getMoistureColor,
  getCropHealthColor,
  themeClass,
  directionClass,
  getThemeCSSVariables,
  generateCSSVariableString,
  generateThemeCSS,
  generateAllThemesCSS,
  ltrLayout,
  rtlLayout,
  getLayout,
  generateLayoutCSS,
  resolveThemeMode,
  getThemeColor,
  getAgriculturalColor,
  getNDVIGradient,
  getMoistureGradient,
  getCropHealthGradient,
  THEME_STORAGE_KEY,
  DIRECTION_STORAGE_KEY,
  saveThemePreference,
  loadThemePreference,
  saveDirectionPreference,
  loadDirectionPreference,
  watchSystemTheme,
  baseThemeStyles,
} from "./themes";

// ═══════════════════════════════════════════════════════════════════════════════
// Component Variants
// ═══════════════════════════════════════════════════════════════════════════════

export {
  buttonVariants,
  inputVariants,
  cardVariants,
  alertVariants,
  badgeVariants,
  modalVariants,
  selectVariants,
  tabsVariants,
  tableVariants,
  tooltipVariants,
  agriculturalVariants,
  skeletonVariants,
} from "./components/variants";

export type {
  ButtonVariant,
  ButtonSize,
  InputState,
  InputSize,
  CardVariant,
  CardPadding,
  AlertVariant,
  BadgeVariant,
  BadgeSize,
  ModalSize,
  NDVILevel,
  MoistureLevel,
  CropHealthLevel,
  WeatherCondition,
  AdvisoryPriority,
} from "./components/variants";

// ═══════════════════════════════════════════════════════════════════════════════
// RTL Utilities
// ═══════════════════════════════════════════════════════════════════════════════

export {
  arabicConfig,
  englishConfig,
  logicalSpacing,
  textAlignment,
  arabicTypography,
  bidirectionalContent,
  rtlFlex,
  mirroredIcons,
  directionalIcons,
  rtlNavigation,
  rtlForm,
  rtlList,
  getRTLConfig,
  isRTLLanguage,
  getDirectionFromLanguage,
  directionClass as rtlDirectionClass,
  rtlOnly,
  ltrOnly,
  swapForRTL,
  generateRTLCSS,
  arabicIndic,
  toArabicNumerals,
  formatArabicNumber,
  formatArabicCurrency,
  formatArabicDate,
  tailwindRTLConfig,
  rtlUtils,
} from "./rtl";

export type { Direction, Language, RTLConfig } from "./rtl";

// ═══════════════════════════════════════════════════════════════════════════════
// Accessibility Utilities
// ═══════════════════════════════════════════════════════════════════════════════

export {
  defaultA11yConfig,
  focusRing,
  srOnly,
  srOnlyFocusable,
  srAnnouncement,
  motionSafe,
  motionReduce,
  highContrast,
  touchTarget,
  skipLink,
  keyboardOnly,
  ariaAttributes,
  getRelativeLuminance,
  getContrastRatio,
  hexToRgb,
  meetsContrastRequirement,
  getAccessibleTextColor,
  focusableSelector,
  getFocusableElements,
  getFirstFocusableElement,
  getLastFocusableElement,
  prefersReducedMotion,
  prefersHighContrast,
  prefersDarkMode,
  watchMotionPreference,
  generateAccessibilityCSS,
  a11yUtils,
} from "./accessibility";

export type {
  FocusRingVariant,
  MotionPreference,
  ContrastPreference,
  A11yConfig,
} from "./accessibility";

// ═══════════════════════════════════════════════════════════════════════════════
// React Hooks
// ═══════════════════════════════════════════════════════════════════════════════

export {
  useTheme,
  useDirection,
  useMediaQuery,
  useReducedMotion,
  useHighContrast,
  usePrefersDark,
  useIsTouchDevice,
  useBreakpoints,
  useBreakpoint,
  useFocusTrap,
  useInView,
  useLocalStorage,
  useDebounce,
  breakpoints,
  designSystemHooks,
} from "./hooks";

export type {
  UseThemeReturn,
  UseDirectionReturn,
  UseFocusTrapOptions,
  UseInViewOptions,
  Breakpoint,
} from "./hooks";

// ═══════════════════════════════════════════════════════════════════════════════
// Utility Functions
// ═══════════════════════════════════════════════════════════════════════════════

import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";
import { tokens } from "../tokens/tokens";

/**
 * Merge Tailwind CSS classes with clsx
 * Handles class conflicts intelligently
 *
 * @example
 * ```tsx
 * cn('px-2 py-1', 'px-4'); // => 'py-1 px-4'
 * cn('text-red-500', condition && 'text-blue-500');
 * ```
 */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}

/**
 * Get color value from tokens
 */
export function getColor(
  category:
    | "primary"
    | "secondary"
    | "accent"
    | "success"
    | "warning"
    | "error"
    | "info"
    | "neutral"
    | "domain",
  shade: string
): string {
  return (tokens.colors[category] as Record<string, string>)?.[shade] || "";
}

/**
 * Get spacing value from tokens
 */
export function getSpacing(size: string): string {
  return (tokens.spacing as Record<string, string>)[size] || "0";
}

/**
 * Get typography value from tokens
 */
export function getFontSize(size: keyof typeof tokens.typography.sizes): string {
  return tokens.typography.sizes[size];
}

/**
 * Get font family from tokens
 */
export function getFontFamily(type: keyof typeof tokens.typography.fonts): string {
  return tokens.typography.fonts[type];
}

// ═══════════════════════════════════════════════════════════════════════════════
// Component Style Utilities (Legacy - for backward compatibility)
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * @deprecated Use buttonVariants from ./components/variants instead
 */
export const componentStyles = {
  button: {
    base: "inline-flex items-center justify-center rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
    variants: {
      primary:
        "bg-primary-600 text-white hover:bg-primary-700 focus-visible:ring-primary-500",
      secondary:
        "bg-secondary-600 text-white hover:bg-secondary-700 focus-visible:ring-secondary-500",
      outline:
        "border border-neutral-300 bg-transparent hover:bg-neutral-100 focus-visible:ring-neutral-500",
      ghost:
        "bg-transparent hover:bg-neutral-100 focus-visible:ring-neutral-500",
    },
    sizes: {
      sm: "h-8 px-3 text-sm",
      md: "h-10 px-4 text-base",
      lg: "h-12 px-6 text-lg",
    },
  },
  card: {
    base: "rounded-lg border border-neutral-200 bg-white shadow-sm",
    header: "flex flex-col space-y-1.5 p-6",
    content: "p-6 pt-0",
    footer: "flex items-center p-6 pt-0",
  },
  input: {
    base: "flex h-10 w-full rounded-md border border-neutral-300 bg-white px-3 py-2 text-sm placeholder:text-neutral-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent disabled:cursor-not-allowed disabled:opacity-50",
    label: "text-sm font-medium text-neutral-700",
    error: "text-sm text-error-main mt-1",
  },
} as const;

// ═══════════════════════════════════════════════════════════════════════════════
// CSS Generation Utilities
// ═══════════════════════════════════════════════════════════════════════════════

import { generateAllThemesCSS, baseThemeStyles } from "./themes";
import { generateRTLCSS } from "./rtl";
import { generateAccessibilityCSS } from "./accessibility";

/**
 * Generate complete design system CSS
 * Includes themes, RTL support, and accessibility styles
 */
export function generateDesignSystemCSS(): string {
  return `
/* ═══════════════════════════════════════════════════════════════════════════════ */
/* SAHOOL Design System - Complete CSS                                              */
/* Version: 16.0.0                                                                  */
/* Generated: ${new Date().toISOString()}                                           */
/* ═══════════════════════════════════════════════════════════════════════════════ */

${baseThemeStyles}

${generateRTLCSS()}

${generateAccessibilityCSS()}
`;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Version Information
// ═══════════════════════════════════════════════════════════════════════════════

export const VERSION = "16.0.0";
export const PACKAGE_NAME = "@sahool/design-system";
