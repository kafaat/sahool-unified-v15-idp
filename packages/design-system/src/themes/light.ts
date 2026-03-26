/**
 * SAHOOL Design System - Light Theme
 * Light theme color palette and configuration
 *
 * Designed for:
 * - Optimal readability in well-lit environments
 * - Agricultural field use (outdoor visibility)
 * - Arabic and English language support
 */

import type { ThemeConfig } from './types';

/**
 * Light theme configuration
 */
export const lightTheme: ThemeConfig = {
  name: 'sahool-light',
  displayName: 'Light',
  displayNameAr: 'فاتح',
  mode: 'light',

  colors: {
    // Primary - Agricultural Green (matching existing tokens)
    primary: {
      50: '#E8F5E9',
      100: '#C8E6C9',
      200: '#A5D6A7',
      300: '#81C784',
      400: '#66BB6A',
      500: '#4CAF50',
      600: '#43A047',
      700: '#388E3C',
      800: '#2E7D32',
      900: '#1B5E20',
    },

    // Secondary - Water Blue
    secondary: {
      50: '#E3F2FD',
      100: '#BBDEFB',
      200: '#90CAF9',
      300: '#64B5F6',
      400: '#42A5F5',
      500: '#2196F3',
      600: '#1E88E5',
      700: '#1976D2',
      800: '#1565C0',
      900: '#0D47A1',
    },

    // Accent - Harvest Orange
    accent: {
      50: '#FFF3E0',
      100: '#FFE0B2',
      200: '#FFCC80',
      300: '#FFB74D',
      400: '#FFA726',
      500: '#FF9800',
      600: '#FB8C00',
      700: '#F57C00',
      800: '#EF6C00',
      900: '#E65100',
    },

    // Neutral - Grays
    neutral: {
      0: '#FFFFFF',
      50: '#FAFAFA',
      100: '#F5F5F5',
      200: '#EEEEEE',
      300: '#E0E0E0',
      400: '#BDBDBD',
      500: '#9E9E9E',
      600: '#757575',
      700: '#616161',
      800: '#424242',
      900: '#212121',
      1000: '#000000',
    },

    // Semantic Colors
    success: {
      light: '#81C784',
      main: '#4CAF50',
      dark: '#388E3C',
      contrastText: '#FFFFFF',
    },

    warning: {
      light: '#FFB74D',
      main: '#FF9800',
      dark: '#F57C00',
      contrastText: '#000000',
    },

    error: {
      light: '#E57373',
      main: '#F44336',
      dark: '#D32F2F',
      contrastText: '#FFFFFF',
    },

    info: {
      light: '#64B5F6',
      main: '#2196F3',
      dark: '#1976D2',
      contrastText: '#FFFFFF',
    },
  },

  background: {
    default: '#FAFAFA',
    paper: '#FFFFFF',
    elevated: '#FFFFFF',
    overlay: 'rgba(0, 0, 0, 0.5)',
    subtle: '#F5F5F5',
    input: '#FFFFFF',
  },

  text: {
    primary: '#212121',
    secondary: '#616161',
    disabled: '#9E9E9E',
    hint: '#BDBDBD',
    inverse: '#FFFFFF',
    link: '#1976D2',
  },

  border: {
    default: '#E0E0E0',
    light: '#EEEEEE',
    strong: '#BDBDBD',
    focus: '#4CAF50',
    divider: '#EEEEEE',
  },

  agricultural: {
    soil: {
      healthy: '#8D6E63',
      dry: '#D7CCC8',
      wet: '#5D4037',
      neutral: '#A1887F',
    },

    water: {
      optimal: '#29B6F6',
      excess: '#0288D1',
      deficit: '#FF8A65',
      neutral: '#81D4FA',
    },

    cropHealth: {
      excellent: '#1B5E20',
      good: '#4CAF50',
      moderate: '#8BC34A',
      stressed: '#FFC107',
      critical: '#F44336',
    },

    ndvi: {
      high: '#1B5E20',
      mediumHigh: '#4CAF50',
      medium: '#81C784',
      low: '#FFF176',
      bare: '#D7CCC8',
      water: '#1565C0',
    },

    moisture: {
      saturated: '#0288D1',
      optimal: '#29B6F6',
      adequate: '#4FC3F7',
      dry: '#FFB74D',
      critical: '#F44336',
    },

    weather: {
      sunny: '#FFEB3B',
      cloudy: '#90A4AE',
      rainy: '#42A5F5',
      stormy: '#5C6BC0',
      frost: '#B3E5FC',
      heat: '#FF7043',
    },
  },

  shadows: {
    none: 'none',
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
    xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
    '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
    inner: 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)',
    card: '0 2px 8px rgba(0, 0, 0, 0.08)',
    dropdown: '0 4px 12px rgba(0, 0, 0, 0.15)',
    modal: '0 20px 40px rgba(0, 0, 0, 0.2)',
  },
};

/**
 * Light theme CSS variables for CSS-in-JS integration
 */
export const lightThemeCSSVariables = {
  // Primary colors
  '--color-primary-50': lightTheme.colors.primary[50],
  '--color-primary-100': lightTheme.colors.primary[100],
  '--color-primary-200': lightTheme.colors.primary[200],
  '--color-primary-300': lightTheme.colors.primary[300],
  '--color-primary-400': lightTheme.colors.primary[400],
  '--color-primary-500': lightTheme.colors.primary[500],
  '--color-primary-600': lightTheme.colors.primary[600],
  '--color-primary-700': lightTheme.colors.primary[700],
  '--color-primary-800': lightTheme.colors.primary[800],
  '--color-primary-900': lightTheme.colors.primary[900],

  // Secondary colors
  '--color-secondary-50': lightTheme.colors.secondary[50],
  '--color-secondary-100': lightTheme.colors.secondary[100],
  '--color-secondary-200': lightTheme.colors.secondary[200],
  '--color-secondary-300': lightTheme.colors.secondary[300],
  '--color-secondary-400': lightTheme.colors.secondary[400],
  '--color-secondary-500': lightTheme.colors.secondary[500],
  '--color-secondary-600': lightTheme.colors.secondary[600],
  '--color-secondary-700': lightTheme.colors.secondary[700],
  '--color-secondary-800': lightTheme.colors.secondary[800],
  '--color-secondary-900': lightTheme.colors.secondary[900],

  // Accent colors
  '--color-accent-50': lightTheme.colors.accent[50],
  '--color-accent-100': lightTheme.colors.accent[100],
  '--color-accent-200': lightTheme.colors.accent[200],
  '--color-accent-300': lightTheme.colors.accent[300],
  '--color-accent-400': lightTheme.colors.accent[400],
  '--color-accent-500': lightTheme.colors.accent[500],
  '--color-accent-600': lightTheme.colors.accent[600],
  '--color-accent-700': lightTheme.colors.accent[700],
  '--color-accent-800': lightTheme.colors.accent[800],
  '--color-accent-900': lightTheme.colors.accent[900],

  // Semantic colors
  '--color-success-light': lightTheme.colors.success.light,
  '--color-success-main': lightTheme.colors.success.main,
  '--color-success-dark': lightTheme.colors.success.dark,
  '--color-warning-light': lightTheme.colors.warning.light,
  '--color-warning-main': lightTheme.colors.warning.main,
  '--color-warning-dark': lightTheme.colors.warning.dark,
  '--color-error-light': lightTheme.colors.error.light,
  '--color-error-main': lightTheme.colors.error.main,
  '--color-error-dark': lightTheme.colors.error.dark,
  '--color-info-light': lightTheme.colors.info.light,
  '--color-info-main': lightTheme.colors.info.main,
  '--color-info-dark': lightTheme.colors.info.dark,

  // Background colors
  '--bg-default': lightTheme.background.default,
  '--bg-paper': lightTheme.background.paper,
  '--bg-elevated': lightTheme.background.elevated,
  '--bg-overlay': lightTheme.background.overlay,
  '--bg-subtle': lightTheme.background.subtle,
  '--bg-input': lightTheme.background.input,

  // Text colors
  '--text-primary': lightTheme.text.primary,
  '--text-secondary': lightTheme.text.secondary,
  '--text-disabled': lightTheme.text.disabled,
  '--text-hint': lightTheme.text.hint,
  '--text-inverse': lightTheme.text.inverse,
  '--text-link': lightTheme.text.link,

  // Border colors
  '--border-default': lightTheme.border.default,
  '--border-light': lightTheme.border.light,
  '--border-strong': lightTheme.border.strong,
  '--border-focus': lightTheme.border.focus,
  '--border-divider': lightTheme.border.divider,

  // Agricultural - Crop Health
  '--agri-crop-excellent': lightTheme.agricultural.cropHealth.excellent,
  '--agri-crop-good': lightTheme.agricultural.cropHealth.good,
  '--agri-crop-moderate': lightTheme.agricultural.cropHealth.moderate,
  '--agri-crop-stressed': lightTheme.agricultural.cropHealth.stressed,
  '--agri-crop-critical': lightTheme.agricultural.cropHealth.critical,

  // Agricultural - NDVI
  '--agri-ndvi-high': lightTheme.agricultural.ndvi.high,
  '--agri-ndvi-medium-high': lightTheme.agricultural.ndvi.mediumHigh,
  '--agri-ndvi-medium': lightTheme.agricultural.ndvi.medium,
  '--agri-ndvi-low': lightTheme.agricultural.ndvi.low,
  '--agri-ndvi-bare': lightTheme.agricultural.ndvi.bare,
  '--agri-ndvi-water': lightTheme.agricultural.ndvi.water,

  // Agricultural - Moisture
  '--agri-moisture-saturated': lightTheme.agricultural.moisture.saturated,
  '--agri-moisture-optimal': lightTheme.agricultural.moisture.optimal,
  '--agri-moisture-adequate': lightTheme.agricultural.moisture.adequate,
  '--agri-moisture-dry': lightTheme.agricultural.moisture.dry,
  '--agri-moisture-critical': lightTheme.agricultural.moisture.critical,

  // Agricultural - Soil
  '--agri-soil-healthy': lightTheme.agricultural.soil.healthy,
  '--agri-soil-dry': lightTheme.agricultural.soil.dry,
  '--agri-soil-wet': lightTheme.agricultural.soil.wet,
  '--agri-soil-neutral': lightTheme.agricultural.soil.neutral,

  // Agricultural - Water
  '--agri-water-optimal': lightTheme.agricultural.water.optimal,
  '--agri-water-excess': lightTheme.agricultural.water.excess,
  '--agri-water-deficit': lightTheme.agricultural.water.deficit,
  '--agri-water-neutral': lightTheme.agricultural.water.neutral,

  // Agricultural - Weather
  '--agri-weather-sunny': lightTheme.agricultural.weather.sunny,
  '--agri-weather-cloudy': lightTheme.agricultural.weather.cloudy,
  '--agri-weather-rainy': lightTheme.agricultural.weather.rainy,
  '--agri-weather-stormy': lightTheme.agricultural.weather.stormy,
  '--agri-weather-frost': lightTheme.agricultural.weather.frost,
  '--agri-weather-heat': lightTheme.agricultural.weather.heat,

  // Shadows
  '--shadow-sm': lightTheme.shadows.sm,
  '--shadow-md': lightTheme.shadows.md,
  '--shadow-lg': lightTheme.shadows.lg,
  '--shadow-xl': lightTheme.shadows.xl,
  '--shadow-2xl': lightTheme.shadows['2xl'],
  '--shadow-inner': lightTheme.shadows.inner,
  '--shadow-card': lightTheme.shadows.card,
  '--shadow-dropdown': lightTheme.shadows.dropdown,
  '--shadow-modal': lightTheme.shadows.modal,
} as const;

export default lightTheme;
