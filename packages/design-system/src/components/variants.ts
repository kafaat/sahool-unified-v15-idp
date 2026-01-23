/**
 * SAHOOL Design System - Component Variants
 * Comprehensive styling variants for all UI components
 *
 * Features:
 * - Theme-consistent styling using design tokens
 * - RTL/LTR aware spacing
 * - Accessibility-compliant focus states
 * - Dark mode support
 * - Agricultural domain variants
 *
 * @packageDocumentation
 */

// ═══════════════════════════════════════════════════════════════════════════════
// Button Variants
// ═══════════════════════════════════════════════════════════════════════════════

export const buttonVariants = {
  base: [
    "inline-flex items-center justify-center gap-2",
    "rounded-lg font-medium transition-all duration-200",
    "focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2",
    "disabled:opacity-50 disabled:cursor-not-allowed disabled:pointer-events-none",
    // RTL support
    "rtl:flex-row-reverse",
  ].join(" "),

  variants: {
    primary: [
      "bg-primary-600 text-white",
      "hover:bg-primary-700 active:bg-primary-800",
      "focus-visible:ring-primary-500",
      // Dark mode
      "dark:bg-primary-500 dark:hover:bg-primary-600 dark:active:bg-primary-700",
    ].join(" "),

    secondary: [
      "bg-secondary-600 text-white",
      "hover:bg-secondary-700 active:bg-secondary-800",
      "focus-visible:ring-secondary-500",
      "dark:bg-secondary-500 dark:hover:bg-secondary-600",
    ].join(" "),

    accent: [
      "bg-accent-600 text-white",
      "hover:bg-accent-700 active:bg-accent-800",
      "focus-visible:ring-accent-500",
      "dark:bg-accent-500 dark:hover:bg-accent-600",
    ].join(" "),

    outline: [
      "border-2 border-primary-600 text-primary-700 bg-transparent",
      "hover:bg-primary-50 active:bg-primary-100",
      "focus-visible:ring-primary-500",
      "dark:border-primary-400 dark:text-primary-300",
      "dark:hover:bg-primary-900/30",
    ].join(" "),

    ghost: [
      "text-neutral-700 bg-transparent",
      "hover:bg-neutral-100 active:bg-neutral-200",
      "focus-visible:ring-neutral-500",
      "dark:text-neutral-300 dark:hover:bg-neutral-800",
    ].join(" "),

    danger: [
      "bg-error-main text-white",
      "hover:bg-error-dark active:brightness-90",
      "focus-visible:ring-error-light",
      "dark:bg-error-dark dark:hover:bg-error-main",
    ].join(" "),

    success: [
      "bg-success-main text-white",
      "hover:bg-success-dark active:brightness-90",
      "focus-visible:ring-success-light",
      "dark:bg-success-dark dark:hover:bg-success-main",
    ].join(" "),

    warning: [
      "bg-warning-main text-neutral-900",
      "hover:bg-warning-dark active:brightness-90",
      "focus-visible:ring-warning-light",
    ].join(" "),

    link: [
      "text-primary-600 bg-transparent underline-offset-4",
      "hover:underline hover:text-primary-700",
      "focus-visible:ring-primary-500",
      "dark:text-primary-400 dark:hover:text-primary-300",
    ].join(" "),
  },

  sizes: {
    xs: "h-7 px-2.5 text-xs",
    sm: "h-8 px-3 text-sm",
    md: "h-10 px-4 text-base",
    lg: "h-12 px-6 text-lg",
    xl: "h-14 px-8 text-xl",
  },

  iconOnly: {
    xs: "h-7 w-7 p-0",
    sm: "h-8 w-8 p-0",
    md: "h-10 w-10 p-0",
    lg: "h-12 w-12 p-0",
    xl: "h-14 w-14 p-0",
  },
} as const;

// ═══════════════════════════════════════════════════════════════════════════════
// Input Variants
// ═══════════════════════════════════════════════════════════════════════════════

export const inputVariants = {
  base: [
    "block w-full rounded-lg border transition-all duration-200",
    "bg-white text-neutral-900 placeholder:text-neutral-400",
    "focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-0",
    "disabled:bg-neutral-100 disabled:text-neutral-500 disabled:cursor-not-allowed",
    // Dark mode
    "dark:bg-neutral-800 dark:text-neutral-100 dark:placeholder:text-neutral-500",
    "dark:disabled:bg-neutral-900 dark:disabled:text-neutral-600",
  ].join(" "),

  states: {
    default: [
      "border-neutral-300",
      "focus-visible:border-primary-500 focus-visible:ring-primary-200",
      "dark:border-neutral-600 dark:focus-visible:ring-primary-800",
    ].join(" "),

    error: [
      "border-error-main",
      "focus-visible:border-error-main focus-visible:ring-error-light/30",
      "dark:border-error-dark",
    ].join(" "),

    success: [
      "border-success-main",
      "focus-visible:border-success-main focus-visible:ring-success-light/30",
      "dark:border-success-dark",
    ].join(" "),

    warning: [
      "border-warning-main",
      "focus-visible:border-warning-main focus-visible:ring-warning-light/30",
      "dark:border-warning-dark",
    ].join(" "),
  },

  sizes: {
    sm: "h-8 px-2.5 py-1.5 text-sm",
    md: "h-10 px-3 py-2 text-base",
    lg: "h-12 px-4 py-3 text-lg",
  },

  label: [
    "block text-sm font-medium text-neutral-700 mb-1.5",
    "dark:text-neutral-300",
  ].join(" "),

  hint: [
    "text-sm text-neutral-500 mt-1.5",
    "dark:text-neutral-400",
  ].join(" "),

  error: [
    "text-sm text-error-main mt-1.5",
    "dark:text-error-dark",
  ].join(" "),

  required: "text-error-main ms-1",
} as const;

// ═══════════════════════════════════════════════════════════════════════════════
// Card Variants
// ═══════════════════════════════════════════════════════════════════════════════

export const cardVariants = {
  base: [
    "rounded-xl border transition-shadow duration-200",
    "bg-white dark:bg-neutral-800",
    "border-neutral-200 dark:border-neutral-700",
  ].join(" "),

  variants: {
    default: "shadow-sm hover:shadow-md",
    elevated: "shadow-md hover:shadow-lg",
    outlined: "shadow-none",
    interactive: [
      "shadow-sm hover:shadow-lg cursor-pointer",
      "hover:border-primary-300 dark:hover:border-primary-600",
      "active:shadow-md",
    ].join(" "),
  },

  padding: {
    none: "p-0",
    sm: "p-3",
    md: "p-4",
    lg: "p-6",
    xl: "p-8",
  },

  header: [
    "px-4 py-3 border-b",
    "border-neutral-200 dark:border-neutral-700",
    "bg-neutral-50 dark:bg-neutral-900/50",
    "rounded-t-xl",
  ].join(" "),

  body: "px-4 py-4",

  footer: [
    "px-4 py-3 border-t",
    "border-neutral-200 dark:border-neutral-700",
    "bg-neutral-50 dark:bg-neutral-900/50",
    "rounded-b-xl",
  ].join(" "),
} as const;

// ═══════════════════════════════════════════════════════════════════════════════
// Alert Variants
// ═══════════════════════════════════════════════════════════════════════════════

export const alertVariants = {
  base: [
    "flex gap-3 p-4 rounded-lg border",
    "text-sm",
  ].join(" "),

  variants: {
    info: [
      "bg-info-light/10 border-info-main/30 text-info-dark",
      "dark:bg-info-dark/20 dark:border-info-main/50 dark:text-info-light",
    ].join(" "),

    success: [
      "bg-success-light/10 border-success-main/30 text-success-dark",
      "dark:bg-success-dark/20 dark:border-success-main/50 dark:text-success-light",
    ].join(" "),

    warning: [
      "bg-warning-light/10 border-warning-main/30 text-warning-dark",
      "dark:bg-warning-dark/20 dark:border-warning-main/50 dark:text-warning-light",
    ].join(" "),

    error: [
      "bg-error-light/10 border-error-main/30 text-error-dark",
      "dark:bg-error-dark/20 dark:border-error-main/50 dark:text-error-light",
    ].join(" "),
  },

  icon: {
    info: "text-info-main",
    success: "text-success-main",
    warning: "text-warning-main",
    error: "text-error-main",
  },

  title: "font-semibold mb-1",

  dismissButton: [
    "flex-shrink-0 p-1 rounded-md",
    "hover:bg-black/10 dark:hover:bg-white/10",
    "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2",
    "transition-colors",
  ].join(" "),
} as const;

// ═══════════════════════════════════════════════════════════════════════════════
// Badge Variants
// ═══════════════════════════════════════════════════════════════════════════════

export const badgeVariants = {
  base: [
    "inline-flex items-center justify-center",
    "rounded-full font-medium",
    "whitespace-nowrap",
  ].join(" "),

  variants: {
    default: "bg-neutral-100 text-neutral-700 dark:bg-neutral-700 dark:text-neutral-200",
    primary: "bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-200",
    secondary: "bg-secondary-100 text-secondary-700 dark:bg-secondary-900 dark:text-secondary-200",
    success: "bg-success-light/20 text-success-dark dark:bg-success-dark/30 dark:text-success-light",
    warning: "bg-warning-light/20 text-warning-dark dark:bg-warning-dark/30 dark:text-warning-light",
    error: "bg-error-light/20 text-error-dark dark:bg-error-dark/30 dark:text-error-light",
    info: "bg-info-light/20 text-info-dark dark:bg-info-dark/30 dark:text-info-light",
  },

  sizes: {
    sm: "h-5 px-2 text-xs",
    md: "h-6 px-2.5 text-sm",
    lg: "h-7 px-3 text-base",
  },

  /** Dot indicator for status badges */
  dot: {
    base: "w-2 h-2 rounded-full me-1.5",
    success: "bg-success-main",
    warning: "bg-warning-main",
    error: "bg-error-main",
    info: "bg-info-main",
    neutral: "bg-neutral-400",
  },
} as const;

// ═══════════════════════════════════════════════════════════════════════════════
// Modal/Dialog Variants
// ═══════════════════════════════════════════════════════════════════════════════

export const modalVariants = {
  overlay: [
    "fixed inset-0 z-50",
    "bg-black/50 dark:bg-black/70",
    "backdrop-blur-sm",
    "data-[state=open]:animate-in data-[state=closed]:animate-out",
    "data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0",
  ].join(" "),

  content: [
    "fixed left-1/2 top-1/2 z-50",
    "-translate-x-1/2 -translate-y-1/2",
    "w-full max-h-[90vh] overflow-auto",
    "rounded-xl border shadow-xl",
    "bg-white dark:bg-neutral-800",
    "border-neutral-200 dark:border-neutral-700",
    "data-[state=open]:animate-in data-[state=closed]:animate-out",
    "data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0",
    "data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95",
    "data-[state=closed]:slide-out-to-left-1/2 data-[state=closed]:slide-out-to-top-[48%]",
    "data-[state=open]:slide-in-from-left-1/2 data-[state=open]:slide-in-from-top-[48%]",
    "duration-200",
  ].join(" "),

  sizes: {
    sm: "max-w-sm",
    md: "max-w-md",
    lg: "max-w-lg",
    xl: "max-w-xl",
    "2xl": "max-w-2xl",
    full: "max-w-[calc(100vw-2rem)]",
  },

  header: [
    "flex items-center justify-between",
    "px-6 py-4 border-b",
    "border-neutral-200 dark:border-neutral-700",
  ].join(" "),

  body: "px-6 py-4",

  footer: [
    "flex items-center justify-end gap-3",
    "px-6 py-4 border-t",
    "border-neutral-200 dark:border-neutral-700",
    "rtl:flex-row-reverse",
  ].join(" "),

  closeButton: [
    "absolute top-4 end-4",
    "p-2 rounded-lg",
    "text-neutral-500 hover:text-neutral-700",
    "hover:bg-neutral-100 dark:hover:bg-neutral-700",
    "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500",
    "transition-colors",
  ].join(" "),
} as const;

// ═══════════════════════════════════════════════════════════════════════════════
// Select/Dropdown Variants
// ═══════════════════════════════════════════════════════════════════════════════

export const selectVariants = {
  trigger: [
    "flex items-center justify-between",
    "rounded-lg border transition-all duration-200",
    "bg-white text-neutral-900",
    "border-neutral-300",
    "hover:border-neutral-400",
    "focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-200 focus-visible:border-primary-500",
    "disabled:bg-neutral-100 disabled:cursor-not-allowed",
    "dark:bg-neutral-800 dark:text-neutral-100 dark:border-neutral-600",
    "dark:hover:border-neutral-500",
  ].join(" "),

  content: [
    "z-50 min-w-[8rem] overflow-hidden",
    "rounded-lg border shadow-lg",
    "bg-white dark:bg-neutral-800",
    "border-neutral-200 dark:border-neutral-700",
    "data-[state=open]:animate-in data-[state=closed]:animate-out",
    "data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0",
    "data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95",
    "data-[side=bottom]:slide-in-from-top-2",
    "data-[side=top]:slide-in-from-bottom-2",
  ].join(" "),

  item: [
    "relative flex items-center",
    "px-3 py-2 cursor-pointer",
    "text-neutral-900 dark:text-neutral-100",
    "hover:bg-neutral-100 dark:hover:bg-neutral-700",
    "focus:bg-neutral-100 dark:focus:bg-neutral-700",
    "focus:outline-none",
    "data-[disabled]:opacity-50 data-[disabled]:pointer-events-none",
    "data-[highlighted]:bg-primary-50 dark:data-[highlighted]:bg-primary-900/30",
  ].join(" "),

  sizes: {
    sm: "h-8 px-2.5 text-sm",
    md: "h-10 px-3 text-base",
    lg: "h-12 px-4 text-lg",
  },
} as const;

// ═══════════════════════════════════════════════════════════════════════════════
// Tabs Variants
// ═══════════════════════════════════════════════════════════════════════════════

export const tabsVariants = {
  list: [
    "flex",
    "border-b border-neutral-200 dark:border-neutral-700",
    "gap-1",
    "overflow-x-auto scrollbar-hide",
  ].join(" "),

  trigger: [
    "relative px-4 py-2.5",
    "text-sm font-medium",
    "text-neutral-600 dark:text-neutral-400",
    "hover:text-neutral-900 dark:hover:text-neutral-100",
    "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:ring-offset-2",
    "disabled:opacity-50 disabled:pointer-events-none",
    "transition-colors",
    "whitespace-nowrap",
    // Active state
    "data-[state=active]:text-primary-600 dark:data-[state=active]:text-primary-400",
    "data-[state=active]:after:absolute",
    "data-[state=active]:after:bottom-0 data-[state=active]:after:inset-x-0",
    "data-[state=active]:after:h-0.5 data-[state=active]:after:bg-primary-600",
    "dark:data-[state=active]:after:bg-primary-400",
  ].join(" "),

  content: [
    "mt-4",
    "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500",
  ].join(" "),

  /** Pills variant (alternative to underline) */
  pillsList: [
    "inline-flex p-1 rounded-lg",
    "bg-neutral-100 dark:bg-neutral-800",
  ].join(" "),

  pillsTrigger: [
    "px-4 py-2 rounded-md",
    "text-sm font-medium",
    "text-neutral-600 dark:text-neutral-400",
    "hover:text-neutral-900 dark:hover:text-neutral-100",
    "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500",
    "transition-all",
    "data-[state=active]:bg-white dark:data-[state=active]:bg-neutral-700",
    "data-[state=active]:text-neutral-900 dark:data-[state=active]:text-neutral-100",
    "data-[state=active]:shadow-sm",
  ].join(" "),
} as const;

// ═══════════════════════════════════════════════════════════════════════════════
// Table Variants
// ═══════════════════════════════════════════════════════════════════════════════

export const tableVariants = {
  wrapper: "overflow-x-auto rounded-lg border border-neutral-200 dark:border-neutral-700",

  table: "w-full text-sm",

  header: [
    "bg-neutral-50 dark:bg-neutral-800/50",
    "border-b border-neutral-200 dark:border-neutral-700",
  ].join(" "),

  headerCell: [
    "px-4 py-3 text-start font-semibold",
    "text-neutral-700 dark:text-neutral-300",
    "rtl:text-end",
  ].join(" "),

  body: "divide-y divide-neutral-200 dark:divide-neutral-700",

  row: [
    "hover:bg-neutral-50 dark:hover:bg-neutral-800/50",
    "transition-colors",
  ].join(" "),

  cell: [
    "px-4 py-3 text-start",
    "text-neutral-900 dark:text-neutral-100",
    "rtl:text-end",
  ].join(" "),

  /** Clickable row */
  clickableRow: [
    "hover:bg-neutral-100 dark:hover:bg-neutral-800",
    "cursor-pointer",
    "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-primary-500",
  ].join(" "),

  /** Empty state */
  empty: [
    "text-center py-12",
    "text-neutral-500 dark:text-neutral-400",
  ].join(" "),
} as const;

// ═══════════════════════════════════════════════════════════════════════════════
// Tooltip Variants
// ═══════════════════════════════════════════════════════════════════════════════

export const tooltipVariants = {
  content: [
    "z-50 px-3 py-1.5 rounded-md",
    "text-sm",
    "bg-neutral-900 text-white",
    "dark:bg-neutral-100 dark:text-neutral-900",
    "shadow-lg",
    "animate-in fade-in-0 zoom-in-95",
    "data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=closed]:zoom-out-95",
    "data-[side=bottom]:slide-in-from-top-2",
    "data-[side=top]:slide-in-from-bottom-2",
    "data-[side=left]:slide-in-from-right-2",
    "data-[side=right]:slide-in-from-left-2",
  ].join(" "),

  arrow: "fill-neutral-900 dark:fill-neutral-100",
} as const;

// ═══════════════════════════════════════════════════════════════════════════════
// Agricultural Domain Components
// ═══════════════════════════════════════════════════════════════════════════════

export const agriculturalVariants = {
  /** NDVI indicator badge */
  ndviBadge: {
    base: "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-sm font-medium",
    levels: {
      high: "bg-[var(--agri-ndvi-high)] text-white",
      mediumHigh: "bg-[var(--agri-ndvi-medium-high)] text-white",
      medium: "bg-[var(--agri-ndvi-medium)] text-neutral-900",
      low: "bg-[var(--agri-ndvi-low)] text-neutral-900",
      bare: "bg-[var(--agri-ndvi-bare)] text-neutral-900",
      water: "bg-[var(--agri-ndvi-water)] text-white",
    },
  },

  /** Moisture indicator */
  moistureBadge: {
    base: "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-sm font-medium",
    levels: {
      saturated: "bg-[var(--agri-moisture-saturated)] text-white",
      optimal: "bg-[var(--agri-moisture-optimal)] text-white",
      adequate: "bg-[var(--agri-moisture-adequate)] text-neutral-900",
      dry: "bg-[var(--agri-moisture-dry)] text-neutral-900",
      critical: "bg-[var(--agri-moisture-critical)] text-white",
    },
  },

  /** Crop health indicator */
  cropHealthBadge: {
    base: "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-sm font-medium",
    levels: {
      excellent: "bg-[var(--agri-crop-excellent)] text-white",
      good: "bg-[var(--agri-crop-good)] text-white",
      moderate: "bg-[var(--agri-crop-moderate)] text-neutral-900",
      stressed: "bg-[var(--agri-crop-stressed)] text-neutral-900",
      critical: "bg-[var(--agri-crop-critical)] text-white",
    },
  },

  /** Weather condition badge */
  weatherBadge: {
    base: "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-sm font-medium",
    conditions: {
      sunny: "bg-[var(--agri-weather-sunny)] text-neutral-900",
      cloudy: "bg-[var(--agri-weather-cloudy)] text-white",
      rainy: "bg-[var(--agri-weather-rainy)] text-white",
      stormy: "bg-[var(--agri-weather-stormy)] text-white",
      frost: "bg-[var(--agri-weather-frost)] text-neutral-900",
      heat: "bg-[var(--agri-weather-heat)] text-white",
    },
  },

  /** Field card */
  fieldCard: {
    base: [
      cardVariants.base,
      "relative overflow-hidden",
    ].join(" "),
    mapContainer: "h-32 bg-neutral-100 dark:bg-neutral-700",
    content: "p-4",
    stats: "grid grid-cols-2 gap-3 mt-3",
    statItem: "flex flex-col",
    statLabel: "text-xs text-neutral-500 dark:text-neutral-400",
    statValue: "text-lg font-semibold text-neutral-900 dark:text-neutral-100",
  },

  /** Sensor reading display */
  sensorReading: {
    base: [
      "flex items-center gap-3 p-3 rounded-lg",
      "bg-neutral-50 dark:bg-neutral-800",
      "border border-neutral-200 dark:border-neutral-700",
    ].join(" "),
    icon: "w-10 h-10 rounded-full flex items-center justify-center",
    value: "text-2xl font-bold text-neutral-900 dark:text-neutral-100",
    unit: "text-sm text-neutral-500 dark:text-neutral-400",
    label: "text-sm text-neutral-600 dark:text-neutral-300",
  },

  /** Advisory card */
  advisoryCard: {
    base: [
      cardVariants.base,
      "border-s-4",
    ].join(" "),
    priorities: {
      critical: "border-s-error-main",
      warning: "border-s-warning-main",
      advisory: "border-s-info-main",
      informational: "border-s-neutral-400",
    },
  },
} as const;

// ═══════════════════════════════════════════════════════════════════════════════
// Skeleton/Loading Variants
// ═══════════════════════════════════════════════════════════════════════════════

export const skeletonVariants = {
  base: [
    "animate-pulse rounded-md",
    "bg-neutral-200 dark:bg-neutral-700",
  ].join(" "),

  /** Text line skeleton */
  text: "h-4 w-full",

  /** Title skeleton */
  title: "h-6 w-3/4",

  /** Avatar skeleton */
  avatar: {
    sm: "h-8 w-8 rounded-full",
    md: "h-10 w-10 rounded-full",
    lg: "h-12 w-12 rounded-full",
  },

  /** Button skeleton */
  button: {
    sm: "h-8 w-20",
    md: "h-10 w-24",
    lg: "h-12 w-32",
  },

  /** Card skeleton */
  card: "h-48 w-full rounded-xl",

  /** Image skeleton */
  image: "aspect-video w-full rounded-lg",
} as const;

// ═══════════════════════════════════════════════════════════════════════════════
// Export Types
// ═══════════════════════════════════════════════════════════════════════════════

export type ButtonVariant = keyof typeof buttonVariants.variants;
export type ButtonSize = keyof typeof buttonVariants.sizes;
export type InputState = keyof typeof inputVariants.states;
export type InputSize = keyof typeof inputVariants.sizes;
export type CardVariant = keyof typeof cardVariants.variants;
export type CardPadding = keyof typeof cardVariants.padding;
export type AlertVariant = keyof typeof alertVariants.variants;
export type BadgeVariant = keyof typeof badgeVariants.variants;
export type BadgeSize = keyof typeof badgeVariants.sizes;
export type ModalSize = keyof typeof modalVariants.sizes;
export type NDVILevel = keyof typeof agriculturalVariants.ndviBadge.levels;
export type MoistureLevel = keyof typeof agriculturalVariants.moistureBadge.levels;
export type CropHealthLevel = keyof typeof agriculturalVariants.cropHealthBadge.levels;
export type WeatherCondition = keyof typeof agriculturalVariants.weatherBadge.conditions;
export type AdvisoryPriority = keyof typeof agriculturalVariants.advisoryCard.priorities;
