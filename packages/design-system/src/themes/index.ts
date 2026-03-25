/**
 * SAHOOL Design System - Theme Exports and Utilities
 * Central module for theme management
 *
 * Features:
 * - Theme configuration exports
 * - CSS variable generation
 * - RTL/LTR layout utilities
 * - Theme switching helpers
 * - Agricultural color utilities
 */

// Type exports
export type {
  Direction,
  ThemeMode,
  ColorShades,
  SemanticColor,
  BackgroundColors,
  TextColors,
  BorderColors,
  AgriculturalColors,
  Shadows,
  LayoutConfig,
  ThemeConfig,
  ThemeCSSVariables,
  ThemeContextValue,
  ThemeProviderProps,
  ColorCategory,
  ColorShade,
  AgriculturalCategory,
  CropHealthLevel,
  NDVILevel,
  MoistureLevel,
} from './types';

// Theme exports
export { lightTheme, lightThemeCSSVariables } from './light';
export { darkTheme, darkThemeCSSVariables } from './dark';

// Re-export defaults
import { lightTheme, lightThemeCSSVariables } from './light';
import { darkTheme, darkThemeCSSVariables } from './dark';
import type { ThemeConfig, ThemeMode, Direction, LayoutConfig, ColorCategory } from './types';

/**
 * Available themes registry
 */
export const themes = {
  light: lightTheme,
  dark: darkTheme,
} as const;

/**
 * CSS variables for each theme
 */
export const themeCSSVariables = {
  light: lightThemeCSSVariables,
  dark: darkThemeCSSVariables,
} as const;

/**
 * Default theme
 */
export const defaultTheme = lightTheme;

/**
 * Get theme by mode
 */
export function getTheme(mode: 'light' | 'dark'): ThemeConfig {
  return themes[mode];
}

/**
 * Get CSS variables for a theme
 */
export function getThemeCSSVariables(mode: 'light' | 'dark'): Record<string, string> {
  return themeCSSVariables[mode];
}

/**
 * Generate CSS variable string for injection into :root
 */
export function generateCSSVariableString(mode: 'light' | 'dark'): string {
  const variables = getThemeCSSVariables(mode);
  const keys = Object.keys(variables) as Array<keyof typeof variables>;
  return keys.map((key) => `${key}: ${variables[key]};`).join('\n  ');
}

/**
 * Generate CSS class rules for theme
 */
export function generateThemeCSS(mode: 'light' | 'dark'): string {
  const selector = mode === 'dark' ? ".dark, [data-theme='dark']" : ':root';
  const variables = generateCSSVariableString(mode);
  return `${selector} {\n  ${variables}\n}`;
}

/**
 * Generate complete CSS for both themes
 */
export function generateAllThemesCSS(): string {
  return `/* Light Theme (Default) */\n${generateThemeCSS('light')}\n\n/* Dark Theme */\n${generateThemeCSS('dark')}`;
}

/**
 * Layout configuration for LTR (English)
 */
export const ltrLayout: LayoutConfig = {
  direction: 'ltr',
  start: 'left',
  end: 'right',
  fontFamily: '"Tajawal", system-ui, sans-serif',
  baseFontSize: '16px',
  lineHeight: '1.5',
  letterSpacing: '0',
};

/**
 * Layout configuration for RTL (Arabic)
 */
export const rtlLayout: LayoutConfig = {
  direction: 'rtl',
  start: 'right',
  end: 'left',
  fontFamily: '"Tajawal", system-ui, sans-serif',
  baseFontSize: '16px',
  lineHeight: '1.7',
  letterSpacing: '0.02em',
};

/**
 * Get layout configuration by direction
 */
export function getLayout(direction: Direction): LayoutConfig {
  return direction === 'rtl' ? rtlLayout : ltrLayout;
}

/**
 * Generate layout CSS variables
 */
export function generateLayoutCSS(direction: Direction): string {
  const layout = getLayout(direction);
  return `
  --direction: ${layout.direction};
  --text-start: ${layout.start};
  --text-end: ${layout.end};
  --font-family: ${layout.fontFamily};
  --base-font-size: ${layout.baseFontSize};
  --line-height: ${layout.lineHeight};
  --letter-spacing: ${layout.letterSpacing};
`;
}

/**
 * Resolve system theme preference
 */
export function resolveThemeMode(mode: ThemeMode): 'light' | 'dark' {
  if (mode === 'system') {
    if (typeof window !== 'undefined' && window.matchMedia) {
      return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
    return 'light';
  }
  return mode;
}

/**
 * Get color from theme
 */
export function getThemeColor(
  theme: ThemeConfig,
  category: ColorCategory,
  shade: string | number
): string {
  const colorGroup = theme.colors[category];
  if ('light' in colorGroup && typeof shade === 'string') {
    const semanticColor = colorGroup as { light: string; main: string; dark: string };
    if (shade === 'light' || shade === 'main' || shade === 'dark') {
      return semanticColor[shade];
    }
  }
  // Access as indexed type for shade values
  const shadeKey = String(shade);
  if (shadeKey in colorGroup) {
    return (colorGroup as unknown as Record<string, string>)[shadeKey] || '';
  }
  return '';
}

/**
 * Get agricultural color from theme
 */
export function getAgriculturalColor(
  theme: ThemeConfig,
  category: keyof ThemeConfig['agricultural'],
  level: string
): string {
  const colorGroup = theme.agricultural[category];
  return (colorGroup as Record<string, string>)[level] || '';
}

/**
 * NDVI color mapping utility
 * Maps NDVI values (0-1) to appropriate colors
 */
export function getNDVIColor(theme: ThemeConfig, ndviValue: number): string {
  if (ndviValue < 0) return theme.agricultural.ndvi.water;
  if (ndviValue < 0.1) return theme.agricultural.ndvi.bare;
  if (ndviValue < 0.3) return theme.agricultural.ndvi.low;
  if (ndviValue < 0.5) return theme.agricultural.ndvi.medium;
  if (ndviValue < 0.7) return theme.agricultural.ndvi.mediumHigh;
  return theme.agricultural.ndvi.high;
}

/**
 * NDVI color gradient for map visualization
 */
export function getNDVIGradient(theme: ThemeConfig): string[] {
  return [
    theme.agricultural.ndvi.water,
    theme.agricultural.ndvi.bare,
    theme.agricultural.ndvi.low,
    theme.agricultural.ndvi.medium,
    theme.agricultural.ndvi.mediumHigh,
    theme.agricultural.ndvi.high,
  ];
}

/**
 * Moisture level color mapping
 * Maps moisture percentage (0-100) to colors
 */
export function getMoistureColor(theme: ThemeConfig, moisturePercent: number): string {
  if (moisturePercent < 20) return theme.agricultural.moisture.critical;
  if (moisturePercent < 40) return theme.agricultural.moisture.dry;
  if (moisturePercent < 60) return theme.agricultural.moisture.adequate;
  if (moisturePercent < 80) return theme.agricultural.moisture.optimal;
  return theme.agricultural.moisture.saturated;
}

/**
 * Moisture color gradient for visualization
 */
export function getMoistureGradient(theme: ThemeConfig): string[] {
  return [
    theme.agricultural.moisture.critical,
    theme.agricultural.moisture.dry,
    theme.agricultural.moisture.adequate,
    theme.agricultural.moisture.optimal,
    theme.agricultural.moisture.saturated,
  ];
}

/**
 * Crop health color mapping
 */
export function getCropHealthColor(theme: ThemeConfig, healthScore: number): string {
  if (healthScore < 20) return theme.agricultural.cropHealth.critical;
  if (healthScore < 40) return theme.agricultural.cropHealth.stressed;
  if (healthScore < 60) return theme.agricultural.cropHealth.moderate;
  if (healthScore < 80) return theme.agricultural.cropHealth.good;
  return theme.agricultural.cropHealth.excellent;
}

/**
 * Crop health gradient for visualization
 */
export function getCropHealthGradient(theme: ThemeConfig): string[] {
  return [
    theme.agricultural.cropHealth.critical,
    theme.agricultural.cropHealth.stressed,
    theme.agricultural.cropHealth.moderate,
    theme.agricultural.cropHealth.good,
    theme.agricultural.cropHealth.excellent,
  ];
}

/**
 * Theme-aware class generator
 * Returns appropriate Tailwind classes based on theme mode
 */
export function themeClass(lightClass: string, darkClass: string): string {
  return `${lightClass} dark:${darkClass}`;
}

/**
 * Direction-aware class generator
 * Returns appropriate Tailwind classes based on direction
 */
export function directionClass(ltrClass: string, rtlClass: string): string {
  return `ltr:${ltrClass} rtl:${rtlClass}`;
}

/**
 * Storage keys for theme persistence
 */
export const THEME_STORAGE_KEY = 'sahool-theme-mode';
export const DIRECTION_STORAGE_KEY = 'sahool-direction';

/**
 * Save theme preference to storage
 */
export function saveThemePreference(mode: ThemeMode): void {
  if (typeof localStorage !== 'undefined') {
    localStorage.setItem(THEME_STORAGE_KEY, mode);
  }
}

/**
 * Load theme preference from storage
 */
export function loadThemePreference(): ThemeMode {
  if (typeof localStorage !== 'undefined') {
    const stored = localStorage.getItem(THEME_STORAGE_KEY);
    if (stored === 'light' || stored === 'dark' || stored === 'system') {
      return stored;
    }
  }
  return 'system';
}

/**
 * Save direction preference to storage
 */
export function saveDirectionPreference(direction: Direction): void {
  if (typeof localStorage !== 'undefined') {
    localStorage.setItem(DIRECTION_STORAGE_KEY, direction);
  }
}

/**
 * Load direction preference from storage
 */
export function loadDirectionPreference(): Direction {
  if (typeof localStorage !== 'undefined') {
    const stored = localStorage.getItem(DIRECTION_STORAGE_KEY);
    if (stored === 'ltr' || stored === 'rtl') {
      return stored;
    }
  }
  return 'ltr';
}

/**
 * Apply theme to document
 */
export function applyTheme(mode: 'light' | 'dark'): void {
  if (typeof document !== 'undefined') {
    const root = document.documentElement;

    // Update class for Tailwind dark mode
    if (mode === 'dark') {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }

    // Update data attribute
    root.setAttribute('data-theme', mode);

    // Update color-scheme for native elements
    root.style.colorScheme = mode;

    // Inject CSS variables
    const cssVariables = getThemeCSSVariables(mode);
    const varKeys = Object.keys(cssVariables) as Array<keyof typeof cssVariables>;
    varKeys.forEach((key) => {
      root.style.setProperty(key, cssVariables[key] ?? null);
    });
  }
}

/**
 * Apply direction to document
 */
export function applyDirection(direction: Direction): void {
  if (typeof document !== 'undefined') {
    const root = document.documentElement;

    // Set dir attribute
    root.setAttribute('dir', direction);

    // Update layout CSS variables
    const layout = getLayout(direction);
    root.style.setProperty('--direction', layout.direction);
    root.style.setProperty('--text-start', layout.start);
    root.style.setProperty('--text-end', layout.end);
    root.style.setProperty('--font-family', layout.fontFamily);
    root.style.setProperty('--line-height', layout.lineHeight);
    root.style.setProperty('--letter-spacing', layout.letterSpacing);
  }
}

/**
 * Initialize theme system
 * Call this on app startup
 */
export function initializeTheme(): {
  mode: 'light' | 'dark';
  direction: Direction;
} {
  const storedMode = loadThemePreference();
  const resolvedMode = resolveThemeMode(storedMode);
  const direction = loadDirectionPreference();

  applyTheme(resolvedMode);
  applyDirection(direction);

  return { mode: resolvedMode, direction };
}

/**
 * Listen for system theme changes
 */
export function watchSystemTheme(callback: (mode: 'light' | 'dark') => void): () => void {
  if (typeof window !== 'undefined' && window.matchMedia) {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

    const handler = (e: MediaQueryListEvent) => {
      callback(e.matches ? 'dark' : 'light');
    };

    mediaQuery.addEventListener('change', handler);

    return () => {
      mediaQuery.removeEventListener('change', handler);
    };
  }

  return () => {};
}

/**
 * CSS custom properties base styles
 * Include in your global CSS
 */
export const baseThemeStyles = `
/* SAHOOL Design System - Base Theme Styles */

:root {
  color-scheme: light dark;
  ${generateCSSVariableString('light')}
  ${generateLayoutCSS('ltr')}
}

.dark,
[data-theme="dark"] {
  ${generateCSSVariableString('dark')}
}

[dir="rtl"] {
  ${generateLayoutCSS('rtl')}
}

/* Base element styles using CSS variables */
body {
  background-color: var(--bg-default);
  color: var(--text-primary);
  font-family: var(--font-family);
  font-size: var(--base-font-size);
  line-height: var(--line-height);
  letter-spacing: var(--letter-spacing);
  direction: var(--direction);
}

/* Focus ring using primary color */
:focus-visible {
  outline: 2px solid var(--border-focus);
  outline-offset: 2px;
}

/* Selection colors */
::selection {
  background-color: var(--color-primary-200);
  color: var(--text-primary);
}

.dark ::selection {
  background-color: var(--color-primary-700);
}
`;
