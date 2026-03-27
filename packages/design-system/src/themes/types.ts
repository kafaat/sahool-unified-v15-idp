/**
 * SAHOOL Design System - Theme Types
 * TypeScript definitions for theme configuration
 *
 * Supports:
 * - Light and dark themes
 * - RTL/LTR layouts (Arabic/English)
 * - Agricultural domain-specific colors
 * - CSS variables pattern for easy theming
 */

/**
 * Direction for RTL/LTR support
 */
export type Direction = 'ltr' | 'rtl';

/**
 * Theme mode
 */
export type ThemeMode = 'light' | 'dark' | 'system';

/**
 * Color shade values (50-900 scale)
 */
export interface ColorShades {
  50: string;
  100: string;
  200: string;
  300: string;
  400: string;
  500: string;
  600: string;
  700: string;
  800: string;
  900: string;
}

/**
 * Semantic color states (light, main, dark variants)
 */
export interface SemanticColor {
  light: string;
  main: string;
  dark: string;
  /** Contrast text color for this semantic color */
  contrastText: string;
}

/**
 * Background colors for surfaces
 */
export interface BackgroundColors {
  /** Default page background */
  default: string;
  /** Paper/card background */
  paper: string;
  /** Elevated surface background */
  elevated: string;
  /** Overlay background (modals, dropdowns) */
  overlay: string;
  /** Subtle background for highlighted areas */
  subtle: string;
  /** Input field background */
  input: string;
}

/**
 * Text colors with semantic hierarchy
 */
export interface TextColors {
  /** Primary text color */
  primary: string;
  /** Secondary text color (less emphasis) */
  secondary: string;
  /** Disabled text color */
  disabled: string;
  /** Hint/placeholder text color */
  hint: string;
  /** Inverted text (for dark backgrounds) */
  inverse: string;
  /** Link text color */
  link: string;
}

/**
 * Border colors
 */
export interface BorderColors {
  /** Default border color */
  default: string;
  /** Light/subtle border */
  light: string;
  /** Strong/emphasized border */
  strong: string;
  /** Focus ring color */
  focus: string;
  /** Divider color */
  divider: string;
}

/**
 * Agricultural domain-specific colors
 */
export interface AgriculturalColors {
  /** Soil-related colors */
  soil: {
    healthy: string;
    dry: string;
    wet: string;
    neutral: string;
  };
  /** Water/irrigation colors */
  water: {
    optimal: string;
    excess: string;
    deficit: string;
    neutral: string;
  };
  /** Crop health gradient colors */
  cropHealth: {
    excellent: string;
    good: string;
    moderate: string;
    stressed: string;
    critical: string;
  };
  /** NDVI vegetation index colors */
  ndvi: {
    /** High vegetation (0.7-1.0) */
    high: string;
    /** Medium-high (0.5-0.7) */
    mediumHigh: string;
    /** Medium (0.3-0.5) */
    medium: string;
    /** Low (0.1-0.3) */
    low: string;
    /** Bare soil/no vegetation (0-0.1) */
    bare: string;
    /** Water/negative values */
    water: string;
  };
  /** Moisture level colors */
  moisture: {
    saturated: string;
    optimal: string;
    adequate: string;
    dry: string;
    critical: string;
  };
  /** Weather condition indicators */
  weather: {
    sunny: string;
    cloudy: string;
    rainy: string;
    stormy: string;
    frost: string;
    heat: string;
  };
}

/**
 * Shadow definitions
 */
export interface Shadows {
  none: string;
  sm: string;
  md: string;
  lg: string;
  xl: string;
  '2xl': string;
  inner: string;
  /** Card shadow */
  card: string;
  /** Dropdown shadow */
  dropdown: string;
  /** Modal shadow */
  modal: string;
}

/**
 * RTL-compatible spacing and layout values
 */
export interface LayoutConfig {
  /** Text direction */
  direction: Direction;
  /** Start direction (left for LTR, right for RTL) */
  start: 'left' | 'right';
  /** End direction (right for LTR, left for RTL) */
  end: 'left' | 'right';
  /** Font family based on direction */
  fontFamily: string;
  /** Base font size */
  baseFontSize: string;
  /** Line height for body text */
  lineHeight: string;
  /** Letter spacing adjustment for Arabic */
  letterSpacing: string;
}

/**
 * Complete theme configuration
 */
export interface ThemeConfig {
  /** Theme name identifier */
  name: string;
  /** Display name in English */
  displayName: string;
  /** Display name in Arabic */
  displayNameAr: string;
  /** Theme mode */
  mode: 'light' | 'dark';
  /** Color palette */
  colors: {
    primary: ColorShades;
    secondary: ColorShades;
    accent: ColorShades;
    neutral: ColorShades & { 0: string; 1000: string };
    success: SemanticColor;
    warning: SemanticColor;
    error: SemanticColor;
    info: SemanticColor;
  };
  /** Background colors */
  background: BackgroundColors;
  /** Text colors */
  text: TextColors;
  /** Border colors */
  border: BorderColors;
  /** Agricultural domain colors */
  agricultural: AgriculturalColors;
  /** Shadow definitions */
  shadows: Shadows;
}

/**
 * CSS variable mapping for a theme
 */
export interface ThemeCSSVariables {
  /** CSS variable name to value mapping */
  [key: `--${string}`]: string;
}

/**
 * Theme context for React applications
 */
export interface ThemeContextValue {
  /** Current theme configuration */
  theme: ThemeConfig;
  /** Current theme mode */
  mode: ThemeMode;
  /** Text direction */
  direction: Direction;
  /** Layout configuration */
  layout: LayoutConfig;
  /** Toggle between light and dark */
  toggleMode: () => void;
  /** Set specific theme mode */
  setMode: (mode: ThemeMode) => void;
  /** Toggle between LTR and RTL */
  toggleDirection: () => void;
  /** Set specific direction */
  setDirection: (direction: Direction) => void;
  /** Check if dark mode */
  isDark: boolean;
  /** Check if RTL */
  isRTL: boolean;
}

/**
 * Theme provider props
 * Note: Uses generic ReactNode type for framework flexibility
 */
export interface ThemeProviderProps {
  /** Initial theme mode */
  defaultMode?: ThemeMode;
  /** Initial direction */
  defaultDirection?: Direction;
  /** Storage key for persisting theme preference */
  storageKey?: string;
  /** Children components (React.ReactNode compatible) */
  children: unknown;
}

/**
 * Color utility function types
 */
export type ColorCategory =
  | 'primary'
  | 'secondary'
  | 'accent'
  | 'neutral'
  | 'success'
  | 'warning'
  | 'error'
  | 'info';

export type ColorShade = keyof ColorShades | 'light' | 'main' | 'dark';

/**
 * Agricultural color category types
 */
export type AgriculturalCategory = keyof AgriculturalColors;
export type CropHealthLevel = keyof AgriculturalColors['cropHealth'];
export type NDVILevel = keyof AgriculturalColors['ndvi'];
export type MoistureLevel = keyof AgriculturalColors['moisture'];
