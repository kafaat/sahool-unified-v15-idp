/**
 * SAHOOL Design System - Accessibility Utilities
 * WCAG 2.1 AA compliant accessibility features
 *
 * Features:
 * - Focus management and visible focus rings
 * - Reduced motion support
 * - High contrast mode support
 * - Screen reader utilities
 * - Keyboard navigation helpers
 * - ARIA attribute helpers
 * - Color contrast validation
 *
 * @packageDocumentation
 */

// ═══════════════════════════════════════════════════════════════════════════════
// Types
// ═══════════════════════════════════════════════════════════════════════════════

export type FocusRingVariant = "default" | "inset" | "offset" | "none";
export type MotionPreference = "no-preference" | "reduce";
export type ContrastPreference = "no-preference" | "more" | "less" | "custom";

export interface A11yConfig {
  focusRingWidth: number;
  focusRingOffset: number;
  focusRingColor: string;
  reducedMotion: boolean;
  highContrast: boolean;
  minTouchTarget: number;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Default Configuration
// ═══════════════════════════════════════════════════════════════════════════════

export const defaultA11yConfig: A11yConfig = {
  focusRingWidth: 2,
  focusRingOffset: 2,
  focusRingColor: "var(--color-primary-500)",
  reducedMotion: false,
  highContrast: false,
  minTouchTarget: 44, // WCAG 2.1 AA minimum (44x44px)
};

// ═══════════════════════════════════════════════════════════════════════════════
// Focus Management Utilities
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Focus ring styles for interactive elements
 */
export const focusRing = {
  /** Default focus ring (visible only on keyboard focus) */
  default: [
    "focus:outline-none",
    "focus-visible:outline-none",
    "focus-visible:ring-2",
    "focus-visible:ring-primary-500",
    "focus-visible:ring-offset-2",
    "focus-visible:ring-offset-white",
    "dark:focus-visible:ring-offset-neutral-900",
  ].join(" "),

  /** Inset focus ring (inside the element) */
  inset: [
    "focus:outline-none",
    "focus-visible:outline-none",
    "focus-visible:ring-2",
    "focus-visible:ring-inset",
    "focus-visible:ring-primary-500",
  ].join(" "),

  /** Focus ring with larger offset */
  offset: [
    "focus:outline-none",
    "focus-visible:outline-none",
    "focus-visible:ring-2",
    "focus-visible:ring-primary-500",
    "focus-visible:ring-offset-4",
    "focus-visible:ring-offset-white",
    "dark:focus-visible:ring-offset-neutral-900",
  ].join(" "),

  /** No focus ring (use sparingly, ensure alternative indication) */
  none: "focus:outline-none focus-visible:outline-none",

  /** Error state focus ring */
  error: [
    "focus:outline-none",
    "focus-visible:outline-none",
    "focus-visible:ring-2",
    "focus-visible:ring-error-main",
    "focus-visible:ring-offset-2",
  ].join(" "),

  /** Success state focus ring */
  success: [
    "focus:outline-none",
    "focus-visible:outline-none",
    "focus-visible:ring-2",
    "focus-visible:ring-success-main",
    "focus-visible:ring-offset-2",
  ].join(" "),

  /** Within focus (for focus-within on containers) */
  within: [
    "focus-within:ring-2",
    "focus-within:ring-primary-500",
    "focus-within:ring-offset-2",
  ].join(" "),
} as const;

// ═══════════════════════════════════════════════════════════════════════════════
// Screen Reader Utilities
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Visually hidden but accessible to screen readers
 */
export const srOnly = [
  "absolute",
  "w-px h-px",
  "p-0 m-[-1px]",
  "overflow-hidden",
  "clip-[rect(0,0,0,0)]",
  "whitespace-nowrap",
  "border-0",
].join(" ");

/**
 * Visible only when focused (for skip links)
 */
export const srOnlyFocusable = [
  srOnly,
  "focus:relative",
  "focus:w-auto focus:h-auto",
  "focus:m-0",
  "focus:overflow-visible",
  "focus:clip-auto",
  "focus:whitespace-normal",
].join(" ");

/**
 * Screen reader announcement utilities
 */
export const srAnnouncement = {
  /** Polite announcement (wait for current speech to finish) */
  polite: 'aria-live="polite" aria-atomic="true"',
  /** Assertive announcement (interrupt current speech) */
  assertive: 'aria-live="assertive" aria-atomic="true"',
  /** Off (no announcements) */
  off: 'aria-live="off"',
} as const;

// ═══════════════════════════════════════════════════════════════════════════════
// Reduced Motion Utilities
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Motion-safe animations (respect user preferences)
 */
export const motionSafe = {
  /** Only animate if user hasn't requested reduced motion */
  animate: "motion-safe:animate-",

  /** Transition only if motion is allowed */
  transition: [
    "motion-safe:transition-all",
    "motion-safe:duration-200",
    "motion-safe:ease-in-out",
  ].join(" "),

  /** Fade animation */
  fade: "motion-safe:animate-fade-in",

  /** Slide animation */
  slide: "motion-safe:animate-slide-in",

  /** Scale animation */
  scale: "motion-safe:animate-scale-in",

  /** Spin animation (like loading spinners) */
  spin: "motion-safe:animate-spin",

  /** Pulse animation */
  pulse: "motion-safe:animate-pulse",

  /** Bounce animation */
  bounce: "motion-safe:animate-bounce",
} as const;

/**
 * Reduced motion alternatives
 */
export const motionReduce = {
  /** Remove all animations */
  none: "motion-reduce:animate-none motion-reduce:transition-none",

  /** Static state for loading indicators */
  staticLoader: "motion-reduce:animate-none motion-reduce:opacity-75",

  /** Instant transitions */
  instant: "motion-reduce:duration-0",
} as const;

// ═══════════════════════════════════════════════════════════════════════════════
// High Contrast Mode Utilities
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * High contrast mode styles
 * Supports forced-colors media query (Windows High Contrast Mode)
 */
export const highContrast = {
  /** Ensure visible borders in high contrast */
  border: "forced-colors:border-[ButtonText]",

  /** Text visibility in high contrast */
  text: "forced-colors:text-[ButtonText]",

  /** Background in high contrast */
  background: "forced-colors:bg-[Canvas]",

  /** Link visibility */
  link: "forced-colors:text-[LinkText]",

  /** Disabled state */
  disabled: "forced-colors:text-[GrayText]",

  /** Focus indicator */
  focus: "forced-colors:outline-[Highlight] forced-colors:outline-2",

  /** Highlight/selection */
  highlight: "forced-colors:bg-[Highlight] forced-colors:text-[HighlightText]",
} as const;

// ═══════════════════════════════════════════════════════════════════════════════
// Touch Target Utilities
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Minimum touch target sizes (WCAG 2.1 AA: 44x44px)
 */
export const touchTarget = {
  /** Minimum size (44x44px) */
  min: "min-h-[44px] min-w-[44px]",

  /** Comfortable size (48x48px) */
  comfortable: "min-h-[48px] min-w-[48px]",

  /** Large size (56x56px) */
  large: "min-h-[56px] min-w-[56px]",

  /** Extend touch area beyond visible bounds */
  extended: [
    "relative",
    "before:absolute",
    "before:inset-[-8px]",
    "before:content-['']",
  ].join(" "),

  /** Mobile-optimized touch target */
  mobile: [
    "min-h-[44px] min-w-[44px]",
    "sm:min-h-[40px] sm:min-w-[40px]",
  ].join(" "),
} as const;

// ═══════════════════════════════════════════════════════════════════════════════
// Keyboard Navigation Utilities
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Skip link for keyboard navigation
 */
export const skipLink = {
  wrapper: [
    "fixed top-0 start-0 z-[9999]",
    "transform -translate-y-full",
    "focus-within:translate-y-0",
    "transition-transform",
  ].join(" "),

  link: [
    "block px-4 py-2",
    "bg-primary-600 text-white",
    "font-medium",
    focusRing.offset,
  ].join(" "),
} as const;

/**
 * Keyboard-only visible elements
 */
export const keyboardOnly = {
  /** Show only on keyboard focus */
  visible: "opacity-0 focus-visible:opacity-100 transition-opacity",

  /** Hide from mouse/touch users */
  focusVisible: "invisible focus-visible:visible",
} as const;

// ═══════════════════════════════════════════════════════════════════════════════
// ARIA Attribute Helpers
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Common ARIA attributes as objects for spreading
 */
export const ariaAttributes = {
  /** Expandable/collapsible content */
  expanded: (isExpanded: boolean) => ({
    "aria-expanded": isExpanded,
  }),

  /** Selected state (tabs, menu items) */
  selected: (isSelected: boolean) => ({
    "aria-selected": isSelected,
  }),

  /** Checked state (checkboxes, toggles) */
  checked: (isChecked: boolean | "mixed") => ({
    "aria-checked": isChecked,
  }),

  /** Pressed state (toggle buttons) */
  pressed: (isPressed: boolean | "mixed") => ({
    "aria-pressed": isPressed,
  }),

  /** Disabled state */
  disabled: (isDisabled: boolean) => ({
    "aria-disabled": isDisabled,
  }),

  /** Hidden state */
  hidden: (isHidden: boolean) => ({
    "aria-hidden": isHidden,
  }),

  /** Invalid state (form validation) */
  invalid: (isInvalid: boolean) => ({
    "aria-invalid": isInvalid,
  }),

  /** Required field */
  required: (isRequired: boolean) => ({
    "aria-required": isRequired,
  }),

  /** Busy/loading state */
  busy: (isBusy: boolean) => ({
    "aria-busy": isBusy,
  }),

  /** Current page/step indicator */
  current: (type: "page" | "step" | "location" | "date" | "time" | true) => ({
    "aria-current": type,
  }),

  /** Description reference */
  describedBy: (id: string) => ({
    "aria-describedby": id,
  }),

  /** Label reference */
  labelledBy: (id: string) => ({
    "aria-labelledby": id,
  }),

  /** Controls reference */
  controls: (id: string) => ({
    "aria-controls": id,
  }),

  /** Popup information */
  hasPopup: (type: "menu" | "listbox" | "tree" | "grid" | "dialog" | true) => ({
    "aria-haspopup": type,
  }),

  /** Modal dialog */
  modal: (isModal: boolean) => ({
    "aria-modal": isModal,
  }),

  /** Value for progress bars, sliders */
  value: (current: number, min?: number, max?: number, text?: string) => ({
    "aria-valuenow": current,
    ...(min !== undefined && { "aria-valuemin": min }),
    ...(max !== undefined && { "aria-valuemax": max }),
    ...(text && { "aria-valuetext": text }),
  }),
} as const;

// ═══════════════════════════════════════════════════════════════════════════════
// Color Contrast Utilities
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Calculate relative luminance of a color
 */
export function getRelativeLuminance(r: number, g: number, b: number): number {
  const [rs, gs, bs] = [r, g, b].map((c) => {
    const s = c / 255;
    return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4);
  });
  return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
}

/**
 * Calculate contrast ratio between two colors
 */
export function getContrastRatio(
  color1: { r: number; g: number; b: number },
  color2: { r: number; g: number; b: number }
): number {
  const l1 = getRelativeLuminance(color1.r, color1.g, color1.b);
  const l2 = getRelativeLuminance(color2.r, color2.g, color2.b);
  const lighter = Math.max(l1, l2);
  const darker = Math.min(l1, l2);
  return (lighter + 0.05) / (darker + 0.05);
}

/**
 * Parse hex color to RGB
 */
export function hexToRgb(hex: string): { r: number; g: number; b: number } | null {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result
    ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16),
      }
    : null;
}

/**
 * Check if color combination meets WCAG contrast requirements
 */
export function meetsContrastRequirement(
  foreground: string,
  background: string,
  level: "AA" | "AAA" = "AA",
  isLargeText = false
): boolean {
  const fg = hexToRgb(foreground);
  const bg = hexToRgb(background);

  if (!fg || !bg) return false;

  const ratio = getContrastRatio(fg, bg);

  if (level === "AAA") {
    return isLargeText ? ratio >= 4.5 : ratio >= 7;
  }
  // AA level
  return isLargeText ? ratio >= 3 : ratio >= 4.5;
}

/**
 * Get recommended text color for a background
 */
export function getAccessibleTextColor(background: string): "white" | "black" {
  const bg = hexToRgb(background);
  if (!bg) return "black";

  const luminance = getRelativeLuminance(bg.r, bg.g, bg.b);
  return luminance > 0.179 ? "black" : "white";
}

// ═══════════════════════════════════════════════════════════════════════════════
// Focus Trap Utilities
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Focusable element selector
 */
export const focusableSelector = [
  'a[href]',
  'button:not([disabled])',
  'input:not([disabled])',
  'select:not([disabled])',
  'textarea:not([disabled])',
  '[tabindex]:not([tabindex="-1"])',
  '[contenteditable="true"]',
  'audio[controls]',
  'video[controls]',
  'details > summary',
].join(", ");

/**
 * Get all focusable elements within a container
 */
export function getFocusableElements(container: HTMLElement): HTMLElement[] {
  return Array.from(container.querySelectorAll<HTMLElement>(focusableSelector)).filter(
    (el) => !el.hasAttribute("disabled") && el.offsetParent !== null
  );
}

/**
 * Get first focusable element
 */
export function getFirstFocusableElement(container: HTMLElement): HTMLElement | null {
  const focusable = getFocusableElements(container);
  return focusable[0] || null;
}

/**
 * Get last focusable element
 */
export function getLastFocusableElement(container: HTMLElement): HTMLElement | null {
  const focusable = getFocusableElements(container);
  return focusable[focusable.length - 1] || null;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Media Query Utilities
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Check user's motion preference
 */
export function prefersReducedMotion(): boolean {
  if (typeof window === "undefined") return false;
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

/**
 * Check user's contrast preference
 */
export function prefersHighContrast(): boolean {
  if (typeof window === "undefined") return false;
  return window.matchMedia("(prefers-contrast: more)").matches;
}

/**
 * Check user's color scheme preference
 */
export function prefersDarkMode(): boolean {
  if (typeof window === "undefined") return false;
  return window.matchMedia("(prefers-color-scheme: dark)").matches;
}

/**
 * Watch for motion preference changes
 */
export function watchMotionPreference(
  callback: (prefersReduced: boolean) => void
): () => void {
  if (typeof window === "undefined") return () => {};

  const mediaQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
  const handler = (e: MediaQueryListEvent) => callback(e.matches);

  mediaQuery.addEventListener("change", handler);
  return () => mediaQuery.removeEventListener("change", handler);
}

// ═══════════════════════════════════════════════════════════════════════════════
// Accessible CSS Generation
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Generate base accessibility CSS
 */
export function generateAccessibilityCSS(): string {
  return `
/* ═══════════════════════════════════════════════════════════════════════════════ */
/* SAHOOL Design System - Accessibility Base Styles                                 */
/* WCAG 2.1 AA Compliant                                                           */
/* ═══════════════════════════════════════════════════════════════════════════════ */

/* Focus Visible Styles */
:focus-visible {
  outline: 2px solid var(--color-primary-500);
  outline-offset: 2px;
}

/* Remove default focus for mouse users */
:focus:not(:focus-visible) {
  outline: none;
}

/* Skip Link */
.skip-link {
  position: absolute;
  top: -100%;
  left: 0;
  z-index: 9999;
  padding: 0.5rem 1rem;
  background: var(--color-primary-600);
  color: white;
  text-decoration: none;
  font-weight: 500;
}

.skip-link:focus {
  top: 0;
}

/* Visually Hidden (Screen Reader Only) */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

.sr-only-focusable:focus {
  position: relative;
  width: auto;
  height: auto;
  margin: 0;
  overflow: visible;
  clip: auto;
  white-space: normal;
}

/* Reduced Motion */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}

/* High Contrast Mode */
@media (prefers-contrast: more) {
  :root {
    --border-default: currentColor;
    --border-strong: currentColor;
  }

  button,
  [role="button"] {
    border: 2px solid currentColor;
  }

  a {
    text-decoration: underline;
  }
}

/* Forced Colors (Windows High Contrast) */
@media (forced-colors: active) {
  button,
  [role="button"] {
    border: 2px solid ButtonText;
  }

  a {
    color: LinkText;
  }

  :focus {
    outline: 2px solid Highlight;
  }

  [aria-disabled="true"],
  [disabled] {
    color: GrayText;
  }
}

/* Touch Target Minimum Size */
@media (pointer: coarse) {
  button,
  [role="button"],
  a,
  input,
  select {
    min-height: 44px;
    min-width: 44px;
  }
}

/* Print Styles - Show focus indicators as underlines */
@media print {
  :focus {
    outline: none;
    text-decoration: underline;
  }
}

/* Ensure sufficient color contrast */
::selection {
  background-color: var(--color-primary-200);
  color: var(--color-primary-900);
}

.dark ::selection {
  background-color: var(--color-primary-700);
  color: var(--color-primary-100);
}
`;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Export all utilities
// ═══════════════════════════════════════════════════════════════════════════════

export const a11yUtils = {
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
} as const;
