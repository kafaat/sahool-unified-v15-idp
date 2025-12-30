// ═══════════════════════════════════════════════════════════════════════════════
// SAHOOL Animation Utilities
// Modern CSS-based animations with optional Framer Motion support
// أدوات الرسوم المتحركة الحديثة
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Animation presets with CSS classes and inline styles
 */
export type AnimationPreset = 'fadeIn' | 'fadeOut' | 'slideUp' | 'slideDown' | 'slideLeft' | 'slideRight' | 'scaleIn' | 'scaleOut' | 'bounceIn' | 'rotateIn';

/**
 * Animation duration presets
 */
export type AnimationDuration = 'fast' | 'normal' | 'slow' | 'slower';

/**
 * Animation easing functions
 */
export type AnimationEasing = 'linear' | 'ease' | 'ease-in' | 'ease-out' | 'ease-in-out' | 'spring' | 'bounce';

/**
 * Animation delay presets
 */
export type AnimationDelay = 'none' | 'short' | 'medium' | 'long';

/**
 * Animation configuration
 */
export interface AnimationConfig {
  preset: AnimationPreset;
  duration?: AnimationDuration;
  easing?: AnimationEasing;
  delay?: AnimationDelay;
  repeat?: boolean | number;
  direction?: 'normal' | 'reverse' | 'alternate' | 'alternate-reverse';
}

/**
 * Duration values in milliseconds
 */
export const DURATION_VALUES: Record<AnimationDuration, number> = {
  fast: 150,
  normal: 300,
  slow: 500,
  slower: 700,
};

/**
 * Delay values in milliseconds
 */
export const DELAY_VALUES: Record<AnimationDelay, number> = {
  none: 0,
  short: 100,
  medium: 200,
  long: 300,
};

/**
 * Easing function values for CSS
 */
export const EASING_VALUES: Record<AnimationEasing, string> = {
  linear: 'linear',
  ease: 'ease',
  'ease-in': 'ease-in',
  'ease-out': 'ease-out',
  'ease-in-out': 'ease-in-out',
  spring: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
  bounce: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
};

/**
 * Get CSS class name for animation preset
 */
export function getAnimationClass(preset: AnimationPreset): string {
  const classMap: Record<AnimationPreset, string> = {
    fadeIn: 'animate-fade-in',
    fadeOut: 'animate-fade-out',
    slideUp: 'animate-slide-up',
    slideDown: 'animate-slide-down',
    slideLeft: 'animate-slide-left',
    slideRight: 'animate-slide-right',
    scaleIn: 'animate-scale-in',
    scaleOut: 'animate-scale-out',
    bounceIn: 'animate-bounce-in',
    rotateIn: 'animate-rotate-in',
  };
  return classMap[preset];
}

/**
 * Get CSS class name for duration
 */
export function getDurationClass(duration: AnimationDuration): string {
  const durationMap: Record<AnimationDuration, string> = {
    fast: 'duration-150',
    normal: 'duration-300',
    slow: 'duration-500',
    slower: 'duration-700',
  };
  return durationMap[duration];
}

/**
 * Get CSS class name for easing
 */
export function getEasingClass(easing: AnimationEasing): string {
  const easingMap: Record<AnimationEasing, string> = {
    linear: 'ease-linear',
    ease: 'ease',
    'ease-in': 'ease-in',
    'ease-out': 'ease-out',
    'ease-in-out': 'ease-in-out',
    spring: 'ease-spring',
    bounce: 'ease-bounce',
  };
  return easingMap[easing];
}

/**
 * Generate complete animation classes based on configuration
 */
export function getAnimationClasses(config: AnimationConfig): string {
  const classes = [getAnimationClass(config.preset)];

  if (config.duration) {
    classes.push(getDurationClass(config.duration));
  }

  if (config.easing) {
    classes.push(getEasingClass(config.easing));
  }

  if (config.delay && config.delay !== 'none') {
    const delayMap: Record<Exclude<AnimationDelay, 'none'>, string> = {
      short: 'delay-100',
      medium: 'delay-200',
      long: 'delay-300',
    };
    classes.push(delayMap[config.delay]);
  }

  if (config.repeat === true) {
    classes.push('animate-infinite');
  }

  if (config.direction && config.direction !== 'normal') {
    const directionMap: Record<string, string> = {
      reverse: 'animate-reverse',
      alternate: 'animate-alternate',
      'alternate-reverse': 'animate-alternate-reverse',
    };
    classes.push(directionMap[config.direction]);
  }

  return classes.join(' ');
}

/**
 * Generate inline animation styles (fallback for non-Tailwind environments)
 */
export function getAnimationStyles(config: AnimationConfig): React.CSSProperties {
  const duration = config.duration ? DURATION_VALUES[config.duration] : DURATION_VALUES.normal;
  const delay = config.delay ? DELAY_VALUES[config.delay] : DELAY_VALUES.none;
  const easing = config.easing ? EASING_VALUES[config.easing] : EASING_VALUES.ease;

  const repeatValue = config.repeat === true ? 'infinite' : typeof config.repeat === 'number' ? config.repeat : 1;

  return {
    animationName: config.preset,
    animationDuration: `${duration}ms`,
    animationTimingFunction: easing,
    animationDelay: delay > 0 ? `${delay}ms` : undefined,
    animationIterationCount: repeatValue,
    animationDirection: config.direction || 'normal',
    animationFillMode: 'both',
  };
}

/**
 * Stagger animation utilities
 */
export interface StaggerConfig {
  delayPerChild: number;
  maxDelay?: number;
}

/**
 * Calculate stagger delay for a child element
 */
export function getStaggerDelay(index: number, config: StaggerConfig): number {
  const delay = index * config.delayPerChild;
  return config.maxDelay ? Math.min(delay, config.maxDelay) : delay;
}

/**
 * Generate stagger animation style
 */
export function getStaggerStyle(index: number, config: StaggerConfig): React.CSSProperties {
  return {
    animationDelay: `${getStaggerDelay(index, config)}ms`,
  };
}

/**
 * Hover and interaction animation utilities
 */
export const HOVER_ANIMATIONS = {
  scale: 'hover:scale-105 active:scale-95 transition-transform',
  lift: 'hover:-translate-y-1 hover:shadow-lg transition-all',
  glow: 'hover:shadow-xl hover:shadow-sahool-green-500/20 transition-shadow',
  rotate: 'hover:rotate-3 transition-transform',
  pulse: 'hover:animate-pulse',
  bounce: 'hover:animate-bounce',
};

/**
 * Focus animation utilities
 */
export const FOCUS_ANIMATIONS = {
  ring: 'focus:ring-2 focus:ring-sahool-green-500 focus:ring-offset-2 transition-shadow',
  scale: 'focus:scale-105 transition-transform',
  glow: 'focus:shadow-lg focus:shadow-sahool-green-500/30 transition-shadow',
};

/**
 * Transition presets for common use cases
 */
export const TRANSITION_PRESETS = {
  fast: 'transition-all duration-150 ease-in-out',
  normal: 'transition-all duration-300 ease-in-out',
  slow: 'transition-all duration-500 ease-in-out',
  spring: 'transition-all duration-300 ease-spring',
  bounce: 'transition-all duration-500 ease-bounce',
};

/**
 * Loading animation utilities
 */
export const LOADING_ANIMATIONS = {
  spin: 'animate-spin',
  pulse: 'animate-pulse',
  bounce: 'animate-bounce',
  ping: 'animate-ping',
};

/**
 * Intersection Observer hook helper for scroll-triggered animations
 */
export interface IntersectionConfig {
  threshold?: number;
  rootMargin?: string;
  triggerOnce?: boolean;
}

/**
 * Helper to create animation on scroll
 */
export function useScrollAnimation(config?: IntersectionConfig) {
  const [isVisible, setIsVisible] = React.useState(false);
  const elementRef = React.useRef<HTMLElement>(null);

  React.useEffect(() => {
    const element = elementRef.current;
    if (!element) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          if (config?.triggerOnce) {
            observer.unobserve(element);
          }
        } else if (!config?.triggerOnce) {
          setIsVisible(false);
        }
      },
      {
        threshold: config?.threshold || 0.1,
        rootMargin: config?.rootMargin || '0px',
      }
    );

    observer.observe(element);

    return () => {
      observer.disconnect();
    };
  }, [config?.threshold, config?.rootMargin, config?.triggerOnce]);

  return { isVisible, elementRef };
}

// React import for hook
import React from 'react';

/**
 * Animation preset definitions for use with inline styles or CSS-in-JS
 */
export const ANIMATION_KEYFRAMES = {
  fadeIn: {
    '0%': { opacity: 0 },
    '100%': { opacity: 1 },
  },
  fadeOut: {
    '0%': { opacity: 1 },
    '100%': { opacity: 0 },
  },
  slideUp: {
    '0%': { transform: 'translateY(20px)', opacity: 0 },
    '100%': { transform: 'translateY(0)', opacity: 1 },
  },
  slideDown: {
    '0%': { transform: 'translateY(-20px)', opacity: 0 },
    '100%': { transform: 'translateY(0)', opacity: 1 },
  },
  slideLeft: {
    '0%': { transform: 'translateX(20px)', opacity: 0 },
    '100%': { transform: 'translateX(0)', opacity: 1 },
  },
  slideRight: {
    '0%': { transform: 'translateX(-20px)', opacity: 0 },
    '100%': { transform: 'translateX(0)', opacity: 1 },
  },
  scaleIn: {
    '0%': { transform: 'scale(0.9)', opacity: 0 },
    '100%': { transform: 'scale(1)', opacity: 1 },
  },
  scaleOut: {
    '0%': { transform: 'scale(1)', opacity: 1 },
    '100%': { transform: 'scale(0.9)', opacity: 0 },
  },
  bounceIn: {
    '0%': { transform: 'scale(0.3)', opacity: 0 },
    '50%': { transform: 'scale(1.05)', opacity: 0.8 },
    '70%': { transform: 'scale(0.9)', opacity: 0.9 },
    '100%': { transform: 'scale(1)', opacity: 1 },
  },
  rotateIn: {
    '0%': { transform: 'rotate(-200deg) scale(0)', opacity: 0 },
    '100%': { transform: 'rotate(0) scale(1)', opacity: 1 },
  },
};
