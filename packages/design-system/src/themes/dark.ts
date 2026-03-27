/**
 * SAHOOL Design System - Dark Theme
 * Dark theme color palette and configuration
 *
 * Designed for:
 * - Reduced eye strain in low-light conditions
 * - Night-time field operations
 * - Battery efficiency on OLED displays
 * - Arabic and English language support
 */

import type { ThemeConfig } from './types';

/**
 * Dark theme configuration
 */
export const darkTheme: ThemeConfig = {
  name: 'sahool-dark',
  displayName: 'Dark',
  displayNameAr: 'داكن',
  mode: 'dark',

  colors: {
    // Primary - Agricultural Green (adjusted for dark mode)
    primary: {
      50: '#1B3D1E',
      100: '#1E4A22',
      200: '#245729',
      300: '#2E7D32',
      400: '#388E3C',
      500: '#43A047',
      600: '#4CAF50',
      700: '#66BB6A',
      800: '#81C784',
      900: '#A5D6A7',
    },

    // Secondary - Water Blue (adjusted for dark mode)
    secondary: {
      50: '#0D2E4A',
      100: '#0F3A5C',
      200: '#124770',
      300: '#1565C0',
      400: '#1976D2',
      500: '#1E88E5',
      600: '#2196F3',
      700: '#42A5F5',
      800: '#64B5F6',
      900: '#90CAF9',
    },

    // Accent - Harvest Orange (adjusted for dark mode)
    accent: {
      50: '#3D2200',
      100: '#4A2B00',
      200: '#5C3700',
      300: '#EF6C00',
      400: '#F57C00',
      500: '#FB8C00',
      600: '#FF9800',
      700: '#FFA726',
      800: '#FFB74D',
      900: '#FFCC80',
    },

    // Neutral - Grays (inverted for dark mode)
    neutral: {
      0: '#000000',
      50: '#121212',
      100: '#1E1E1E',
      200: '#2D2D2D',
      300: '#3D3D3D',
      400: '#4D4D4D',
      500: '#6D6D6D',
      600: '#8D8D8D',
      700: '#ADADAD',
      800: '#CDCDCD',
      900: '#EDEDED',
      1000: '#FFFFFF',
    },

    // Semantic Colors (adjusted for dark backgrounds)
    success: {
      light: '#2E7D32',
      main: '#4CAF50',
      dark: '#81C784',
      contrastText: '#000000',
    },

    warning: {
      light: '#F57C00',
      main: '#FF9800',
      dark: '#FFB74D',
      contrastText: '#000000',
    },

    error: {
      light: '#C62828',
      main: '#EF5350',
      dark: '#E57373',
      contrastText: '#000000',
    },

    info: {
      light: '#1565C0',
      main: '#42A5F5',
      dark: '#64B5F6',
      contrastText: '#000000',
    },
  },

  background: {
    default: '#121212',
    paper: '#1E1E1E',
    elevated: '#2D2D2D',
    overlay: 'rgba(0, 0, 0, 0.7)',
    subtle: '#1A1A1A',
    input: '#2D2D2D',
  },

  text: {
    primary: '#EDEDED',
    secondary: '#ADADAD',
    disabled: '#6D6D6D',
    hint: '#5D5D5D',
    inverse: '#121212',
    link: '#64B5F6',
  },

  border: {
    default: '#3D3D3D',
    light: '#2D2D2D',
    strong: '#5D5D5D',
    focus: '#66BB6A',
    divider: '#3D3D3D',
  },

  agricultural: {
    soil: {
      healthy: '#A1887F',
      dry: '#8D6E63',
      wet: '#6D4C41',
      neutral: '#795548',
    },

    water: {
      optimal: '#4FC3F7',
      excess: '#0288D1',
      deficit: '#FF8A65',
      neutral: '#29B6F6',
    },

    cropHealth: {
      excellent: '#66BB6A',
      good: '#81C784',
      moderate: '#AED581',
      stressed: '#FFD54F',
      critical: '#EF5350',
    },

    ndvi: {
      high: '#66BB6A',
      mediumHigh: '#81C784',
      medium: '#A5D6A7',
      low: '#FFEE58',
      bare: '#8D6E63',
      water: '#42A5F5',
    },

    moisture: {
      saturated: '#0288D1',
      optimal: '#4FC3F7',
      adequate: '#81D4FA',
      dry: '#FFB74D',
      critical: '#EF5350',
    },

    weather: {
      sunny: '#FFF176',
      cloudy: '#78909C',
      rainy: '#64B5F6',
      stormy: '#7986CB',
      frost: '#4FC3F7',
      heat: '#FF8A65',
    },
  },

  shadows: {
    none: 'none',
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.3)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.4), 0 2px 4px -1px rgba(0, 0, 0, 0.3)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.4), 0 4px 6px -2px rgba(0, 0, 0, 0.3)',
    xl: '0 20px 25px -5px rgba(0, 0, 0, 0.4), 0 10px 10px -5px rgba(0, 0, 0, 0.3)',
    '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.5)',
    inner: 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.3)',
    card: '0 2px 8px rgba(0, 0, 0, 0.3)',
    dropdown: '0 4px 12px rgba(0, 0, 0, 0.4)',
    modal: '0 20px 40px rgba(0, 0, 0, 0.5)',
  },
};

/**
 * Dark theme CSS variables for CSS-in-JS integration
 */
export const darkThemeCSSVariables = {
  // Primary colors
  '--color-primary-50': darkTheme.colors.primary[50],
  '--color-primary-100': darkTheme.colors.primary[100],
  '--color-primary-200': darkTheme.colors.primary[200],
  '--color-primary-300': darkTheme.colors.primary[300],
  '--color-primary-400': darkTheme.colors.primary[400],
  '--color-primary-500': darkTheme.colors.primary[500],
  '--color-primary-600': darkTheme.colors.primary[600],
  '--color-primary-700': darkTheme.colors.primary[700],
  '--color-primary-800': darkTheme.colors.primary[800],
  '--color-primary-900': darkTheme.colors.primary[900],

  // Secondary colors
  '--color-secondary-50': darkTheme.colors.secondary[50],
  '--color-secondary-100': darkTheme.colors.secondary[100],
  '--color-secondary-200': darkTheme.colors.secondary[200],
  '--color-secondary-300': darkTheme.colors.secondary[300],
  '--color-secondary-400': darkTheme.colors.secondary[400],
  '--color-secondary-500': darkTheme.colors.secondary[500],
  '--color-secondary-600': darkTheme.colors.secondary[600],
  '--color-secondary-700': darkTheme.colors.secondary[700],
  '--color-secondary-800': darkTheme.colors.secondary[800],
  '--color-secondary-900': darkTheme.colors.secondary[900],

  // Accent colors
  '--color-accent-50': darkTheme.colors.accent[50],
  '--color-accent-100': darkTheme.colors.accent[100],
  '--color-accent-200': darkTheme.colors.accent[200],
  '--color-accent-300': darkTheme.colors.accent[300],
  '--color-accent-400': darkTheme.colors.accent[400],
  '--color-accent-500': darkTheme.colors.accent[500],
  '--color-accent-600': darkTheme.colors.accent[600],
  '--color-accent-700': darkTheme.colors.accent[700],
  '--color-accent-800': darkTheme.colors.accent[800],
  '--color-accent-900': darkTheme.colors.accent[900],

  // Semantic colors
  '--color-success-light': darkTheme.colors.success.light,
  '--color-success-main': darkTheme.colors.success.main,
  '--color-success-dark': darkTheme.colors.success.dark,
  '--color-warning-light': darkTheme.colors.warning.light,
  '--color-warning-main': darkTheme.colors.warning.main,
  '--color-warning-dark': darkTheme.colors.warning.dark,
  '--color-error-light': darkTheme.colors.error.light,
  '--color-error-main': darkTheme.colors.error.main,
  '--color-error-dark': darkTheme.colors.error.dark,
  '--color-info-light': darkTheme.colors.info.light,
  '--color-info-main': darkTheme.colors.info.main,
  '--color-info-dark': darkTheme.colors.info.dark,

  // Background colors
  '--bg-default': darkTheme.background.default,
  '--bg-paper': darkTheme.background.paper,
  '--bg-elevated': darkTheme.background.elevated,
  '--bg-overlay': darkTheme.background.overlay,
  '--bg-subtle': darkTheme.background.subtle,
  '--bg-input': darkTheme.background.input,

  // Text colors
  '--text-primary': darkTheme.text.primary,
  '--text-secondary': darkTheme.text.secondary,
  '--text-disabled': darkTheme.text.disabled,
  '--text-hint': darkTheme.text.hint,
  '--text-inverse': darkTheme.text.inverse,
  '--text-link': darkTheme.text.link,

  // Border colors
  '--border-default': darkTheme.border.default,
  '--border-light': darkTheme.border.light,
  '--border-strong': darkTheme.border.strong,
  '--border-focus': darkTheme.border.focus,
  '--border-divider': darkTheme.border.divider,

  // Agricultural - Crop Health
  '--agri-crop-excellent': darkTheme.agricultural.cropHealth.excellent,
  '--agri-crop-good': darkTheme.agricultural.cropHealth.good,
  '--agri-crop-moderate': darkTheme.agricultural.cropHealth.moderate,
  '--agri-crop-stressed': darkTheme.agricultural.cropHealth.stressed,
  '--agri-crop-critical': darkTheme.agricultural.cropHealth.critical,

  // Agricultural - NDVI
  '--agri-ndvi-high': darkTheme.agricultural.ndvi.high,
  '--agri-ndvi-medium-high': darkTheme.agricultural.ndvi.mediumHigh,
  '--agri-ndvi-medium': darkTheme.agricultural.ndvi.medium,
  '--agri-ndvi-low': darkTheme.agricultural.ndvi.low,
  '--agri-ndvi-bare': darkTheme.agricultural.ndvi.bare,
  '--agri-ndvi-water': darkTheme.agricultural.ndvi.water,

  // Agricultural - Moisture
  '--agri-moisture-saturated': darkTheme.agricultural.moisture.saturated,
  '--agri-moisture-optimal': darkTheme.agricultural.moisture.optimal,
  '--agri-moisture-adequate': darkTheme.agricultural.moisture.adequate,
  '--agri-moisture-dry': darkTheme.agricultural.moisture.dry,
  '--agri-moisture-critical': darkTheme.agricultural.moisture.critical,

  // Agricultural - Soil
  '--agri-soil-healthy': darkTheme.agricultural.soil.healthy,
  '--agri-soil-dry': darkTheme.agricultural.soil.dry,
  '--agri-soil-wet': darkTheme.agricultural.soil.wet,
  '--agri-soil-neutral': darkTheme.agricultural.soil.neutral,

  // Agricultural - Water
  '--agri-water-optimal': darkTheme.agricultural.water.optimal,
  '--agri-water-excess': darkTheme.agricultural.water.excess,
  '--agri-water-deficit': darkTheme.agricultural.water.deficit,
  '--agri-water-neutral': darkTheme.agricultural.water.neutral,

  // Agricultural - Weather
  '--agri-weather-sunny': darkTheme.agricultural.weather.sunny,
  '--agri-weather-cloudy': darkTheme.agricultural.weather.cloudy,
  '--agri-weather-rainy': darkTheme.agricultural.weather.rainy,
  '--agri-weather-stormy': darkTheme.agricultural.weather.stormy,
  '--agri-weather-frost': darkTheme.agricultural.weather.frost,
  '--agri-weather-heat': darkTheme.agricultural.weather.heat,

  // Shadows
  '--shadow-sm': darkTheme.shadows.sm,
  '--shadow-md': darkTheme.shadows.md,
  '--shadow-lg': darkTheme.shadows.lg,
  '--shadow-xl': darkTheme.shadows.xl,
  '--shadow-2xl': darkTheme.shadows['2xl'],
  '--shadow-inner': darkTheme.shadows.inner,
  '--shadow-card': darkTheme.shadows.card,
  '--shadow-dropdown': darkTheme.shadows.dropdown,
  '--shadow-modal': darkTheme.shadows.modal,
} as const;

export default darkTheme;
