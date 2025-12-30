// ═══════════════════════════════════════════════════════════════════════════════
// SAHOOL Animated Container Component
// Wrapper component for applying animations to any content
// مكون حاوية متحركة
// ═══════════════════════════════════════════════════════════════════════════════

import React, { useEffect, useState, useRef } from 'react';
import {
  AnimationConfig,
  getAnimationClasses,
  getAnimationStyles,
  IntersectionConfig,
  useScrollAnimation,
} from '../animations';

export interface AnimatedContainerProps {
  children: React.ReactNode;
  animation: AnimationConfig;
  /** Apply animation on mount */
  animateOnMount?: boolean;
  /** Apply animation when element enters viewport */
  animateOnScroll?: boolean;
  /** Intersection observer configuration for scroll animations */
  scrollConfig?: IntersectionConfig;
  /** Additional CSS classes */
  className?: string;
  /** Container element type */
  as?: keyof JSX.IntrinsicElements;
  /** Additional inline styles */
  style?: React.CSSProperties;
  /** Callback when animation completes */
  onAnimationComplete?: () => void;
  /** Test ID for testing */
  testId?: string;
}

/**
 * AnimatedContainer - A flexible wrapper component for applying animations
 *
 * Features:
 * - CSS-based animations (no external dependencies)
 * - Animation on mount
 * - Scroll-triggered animations with Intersection Observer
 * - Customizable animation configurations
 * - TypeScript support
 *
 * @example
 * ```tsx
 * <AnimatedContainer
 *   animation={{ preset: 'fadeIn', duration: 'normal', easing: 'ease-out' }}
 *   animateOnMount
 * >
 *   <div>Content to animate</div>
 * </AnimatedContainer>
 * ```
 *
 * @example Scroll-triggered animation
 * ```tsx
 * <AnimatedContainer
 *   animation={{ preset: 'slideUp', duration: 'slow' }}
 *   animateOnScroll
 *   scrollConfig={{ threshold: 0.3, triggerOnce: true }}
 * >
 *   <div>Content appears when scrolled into view</div>
 * </AnimatedContainer>
 * ```
 */
export function AnimatedContainer({
  children,
  animation,
  animateOnMount = true,
  animateOnScroll = false,
  scrollConfig,
  className = '',
  as: Component = 'div',
  style,
  onAnimationComplete,
  testId,
}: AnimatedContainerProps) {
  const [shouldAnimate, setShouldAnimate] = useState(animateOnMount && !animateOnScroll);
  const elementRef = useRef<HTMLElement | null>(null);
  const { isVisible, elementRef: scrollRef } = animateOnScroll
    ? useScrollAnimation(scrollConfig)
    : { isVisible: false, elementRef: { current: null } };

  // Merge refs if using scroll animation
  const mergedRef = (node: HTMLElement | null) => {
    (elementRef as React.MutableRefObject<HTMLElement | null>).current = node;
    if (animateOnScroll && scrollRef) {
      (scrollRef as React.MutableRefObject<HTMLElement | null>).current = node;
    }
  };

  // Handle scroll-triggered animations
  useEffect(() => {
    if (animateOnScroll && isVisible) {
      setShouldAnimate(true);
    }
  }, [animateOnScroll, isVisible]);

  // Handle animation end
  useEffect(() => {
    const element = elementRef.current;
    if (!element || !onAnimationComplete) return;

    const handleAnimationEnd = () => {
      onAnimationComplete();
    };

    element.addEventListener('animationend', handleAnimationEnd);
    return () => {
      element.removeEventListener('animationend', handleAnimationEnd);
    };
  }, [onAnimationComplete]);

  // Get animation classes and styles
  const animationClasses = shouldAnimate ? getAnimationClasses(animation) : '';
  const animationStyles = shouldAnimate ? getAnimationStyles(animation) : {};

  const combinedClassName = `${animationClasses} ${className}`.trim();
  const combinedStyle = { ...animationStyles, ...style };

  return React.createElement(
    Component,
    {
      ref: mergedRef,
      className: combinedClassName,
      style: combinedStyle,
      'data-testid': testId,
    },
    children
  );
}

/**
 * Pre-configured animation variants for common use cases
 */

export interface FadeInProps extends Omit<AnimatedContainerProps, 'animation'> {
  duration?: AnimationConfig['duration'];
}

export function FadeIn({ duration = 'normal', ...props }: FadeInProps) {
  return (
    <AnimatedContainer
      animation={{ preset: 'fadeIn', duration, easing: 'ease-in-out' }}
      {...props}
    />
  );
}

export interface SlideUpProps extends Omit<AnimatedContainerProps, 'animation'> {
  duration?: AnimationConfig['duration'];
}

export function SlideUp({ duration = 'normal', ...props }: SlideUpProps) {
  return (
    <AnimatedContainer
      animation={{ preset: 'slideUp', duration, easing: 'ease-out' }}
      {...props}
    />
  );
}

export interface SlideDownProps extends Omit<AnimatedContainerProps, 'animation'> {
  duration?: AnimationConfig['duration'];
}

export function SlideDown({ duration = 'normal', ...props }: SlideDownProps) {
  return (
    <AnimatedContainer
      animation={{ preset: 'slideDown', duration, easing: 'ease-out' }}
      {...props}
    />
  );
}

export interface ScaleInProps extends Omit<AnimatedContainerProps, 'animation'> {
  duration?: AnimationConfig['duration'];
}

export function ScaleIn({ duration = 'normal', ...props }: ScaleInProps) {
  return (
    <AnimatedContainer
      animation={{ preset: 'scaleIn', duration, easing: 'spring' }}
      {...props}
    />
  );
}

export interface BounceInProps extends Omit<AnimatedContainerProps, 'animation'> {
  duration?: AnimationConfig['duration'];
}

export function BounceIn({ duration = 'slow', ...props }: BounceInProps) {
  return (
    <AnimatedContainer
      animation={{ preset: 'bounceIn', duration, easing: 'bounce' }}
      {...props}
    />
  );
}

/**
 * Example usage:
 *
 * ```tsx
 * // Basic usage
 * <FadeIn>
 *   <Card>Content</Card>
 * </FadeIn>
 *
 * // With scroll trigger
 * <SlideUp animateOnScroll scrollConfig={{ triggerOnce: true }}>
 *   <div>Animates when scrolled into view</div>
 * </SlideUp>
 *
 * // Custom configuration
 * <AnimatedContainer
 *   animation={{
 *     preset: 'scaleIn',
 *     duration: 'slow',
 *     easing: 'spring',
 *     delay: 'medium'
 *   }}
 *   animateOnMount
 *   onAnimationComplete={() => console.log('Animation done!')}
 * >
 *   <div>Custom animated content</div>
 * </AnimatedContainer>
 * ```
 */
