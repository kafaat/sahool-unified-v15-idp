// ═══════════════════════════════════════════════════════════════════════════════
// SAHOOL Staggered List Component
// List component with staggered animations for children
// مكون قائمة بالرسوم المتحركة المتتالية
// ═══════════════════════════════════════════════════════════════════════════════

import React, { Children, cloneElement, isValidElement, useEffect, useState, useRef } from 'react';
import {
  AnimationPreset,
  AnimationDuration,
  AnimationEasing,
  StaggerConfig,
  getStaggerStyle,
  getAnimationClass,
  getDurationClass,
  getEasingClass,
  useScrollAnimation,
  IntersectionConfig,
} from '../animations';

export interface StaggeredListProps {
  children: React.ReactNode;
  /** Animation preset for each item */
  animation?: AnimationPreset;
  /** Animation duration */
  duration?: AnimationDuration;
  /** Animation easing */
  easing?: AnimationEasing;
  /** Delay between each item in milliseconds */
  staggerDelay?: number;
  /** Maximum delay for later items */
  maxDelay?: number;
  /** Animate on mount */
  animateOnMount?: boolean;
  /** Animate when scrolled into view */
  animateOnScroll?: boolean;
  /** Intersection observer configuration */
  scrollConfig?: IntersectionConfig;
  /** Container element type */
  as?: keyof JSX.IntrinsicElements;
  /** Additional CSS classes for container */
  className?: string;
  /** Additional CSS classes for each item */
  itemClassName?: string;
  /** Container styles */
  style?: React.CSSProperties;
  /** Reverse stagger direction (last to first) */
  reverse?: boolean;
  /** Test ID for testing */
  testId?: string;
}

/**
 * StaggeredList - Animates children with a staggered delay
 *
 * Features:
 * - CSS-based staggered animations
 * - Customizable delay between items
 * - Scroll-triggered animations
 * - Reverse stagger option
 * - TypeScript support
 *
 * @example
 * ```tsx
 * <StaggeredList
 *   animation="slideUp"
 *   staggerDelay={100}
 *   animateOnMount
 * >
 *   <div>Item 1</div>
 *   <div>Item 2</div>
 *   <div>Item 3</div>
 * </StaggeredList>
 * ```
 *
 * @example With scroll trigger
 * ```tsx
 * <StaggeredList
 *   animation="fadeIn"
 *   staggerDelay={75}
 *   animateOnScroll
 *   scrollConfig={{ threshold: 0.2, triggerOnce: true }}
 * >
 *   {items.map(item => (
 *     <Card key={item.id}>{item.content}</Card>
 *   ))}
 * </StaggeredList>
 * ```
 */
export function StaggeredList({
  children,
  animation = 'fadeIn',
  duration = 'normal',
  easing = 'ease-out',
  staggerDelay = 100,
  maxDelay,
  animateOnMount = true,
  animateOnScroll = false,
  scrollConfig,
  as: Component = 'div',
  className = '',
  itemClassName = '',
  style,
  reverse = false,
  testId,
}: StaggeredListProps) {
  const [shouldAnimate, setShouldAnimate] = useState(animateOnMount && !animateOnScroll);
  const containerRef = useRef<HTMLElement | null>(null);
  const { isVisible, elementRef: scrollRef } = animateOnScroll
    ? useScrollAnimation(scrollConfig)
    : { isVisible: false, elementRef: { current: null } };

  // Merge refs if using scroll animation
  const mergedRef = (node: HTMLElement | null) => {
    (containerRef as React.MutableRefObject<HTMLElement | null>).current = node;
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

  // Convert children to array
  const childArray = Children.toArray(children);
  const itemCount = childArray.length;

  // Stagger configuration
  const staggerConfig: StaggerConfig = {
    delayPerChild: staggerDelay,
    maxDelay,
  };

  // Get base animation classes
  const baseAnimationClass = getAnimationClass(animation);
  const durationClass = getDurationClass(duration);
  const easingClass = getEasingClass(easing);

  const mappedChildren = childArray.map((child, index) => {
    // Calculate stagger index (reverse if needed)
    const staggerIndex = reverse ? itemCount - 1 - index : index;

    // Get stagger style for this item
    const staggerStyle = shouldAnimate
      ? getStaggerStyle(staggerIndex, staggerConfig)
      : {};

    // Combine animation classes
    const animationClasses = shouldAnimate
      ? `${baseAnimationClass} ${durationClass} ${easingClass}`
      : '';

    // If child is a valid React element, clone it with animation props
    if (isValidElement(child)) {
      const childClassName = child.props.className || '';
      const childStyle = child.props.style || {};

      return cloneElement(child, {
        ...child.props,
        key: child.key || index,
        className: `${childClassName} ${animationClasses} ${itemClassName}`.trim(),
        style: {
          ...childStyle,
          ...staggerStyle,
        },
      } as any);
    }

    // If child is not a valid element, wrap it
    return (
      <div
        key={index}
        className={`${animationClasses} ${itemClassName}`.trim()}
        style={staggerStyle}
      >
        {child}
      </div>
    );
  });

  return React.createElement(
    Component,
    {
      ref: mergedRef,
      className,
      style,
      'data-testid': testId,
    },
    mappedChildren
  );
}

/**
 * Pre-configured staggered list variants
 */

export interface StaggerFadeInProps extends Omit<StaggeredListProps, 'animation'> {
  duration?: AnimationDuration;
}

export function StaggerFadeIn({ duration = 'normal', ...props }: StaggerFadeInProps) {
  return (
    <StaggeredList
      animation="fadeIn"
      duration={duration}
      easing="ease-in-out"
      {...props}
    />
  );
}

export interface StaggerSlideUpProps extends Omit<StaggeredListProps, 'animation'> {
  duration?: AnimationDuration;
}

export function StaggerSlideUp({ duration = 'normal', ...props }: StaggerSlideUpProps) {
  return (
    <StaggeredList
      animation="slideUp"
      duration={duration}
      easing="ease-out"
      {...props}
    />
  );
}

export interface StaggerScaleInProps extends Omit<StaggeredListProps, 'animation'> {
  duration?: AnimationDuration;
}

export function StaggerScaleIn({ duration = 'normal', ...props }: StaggerScaleInProps) {
  return (
    <StaggeredList
      animation="scaleIn"
      duration={duration}
      easing="spring"
      {...props}
    />
  );
}

/**
 * Grid variant with staggered animations
 */
export interface StaggeredGridProps extends StaggeredListProps {
  /** Number of columns */
  columns?: number | { sm?: number; md?: number; lg?: number; xl?: number };
  /** Gap between items */
  gap?: number | string;
}

export function StaggeredGrid({
  columns = 3,
  gap = '1rem',
  className = '',
  style,
  ...props
}: StaggeredGridProps) {
  // Build grid classes for responsive columns
  let gridClasses = 'grid';

  if (typeof columns === 'number') {
    gridClasses += ` grid-cols-${columns}`;
  } else {
    if (columns.sm) gridClasses += ` sm:grid-cols-${columns.sm}`;
    if (columns.md) gridClasses += ` md:grid-cols-${columns.md}`;
    if (columns.lg) gridClasses += ` lg:grid-cols-${columns.lg}`;
    if (columns.xl) gridClasses += ` xl:grid-cols-${columns.xl}`;
  }

  const gridStyle: React.CSSProperties = {
    gap: typeof gap === 'number' ? `${gap}px` : gap,
    ...style,
  };

  return (
    <StaggeredList
      className={`${gridClasses} ${className}`.trim()}
      style={gridStyle}
      {...props}
    />
  );
}

/**
 * Example usage:
 *
 * ```tsx
 * // Basic staggered list
 * <StaggeredList animation="slideUp" staggerDelay={100}>
 *   <Card>Item 1</Card>
 *   <Card>Item 2</Card>
 *   <Card>Item 3</Card>
 * </StaggeredList>
 *
 * // Staggered grid with scroll trigger
 * <StaggeredGrid
 *   columns={{ sm: 1, md: 2, lg: 3 }}
 *   animation="scaleIn"
 *   staggerDelay={75}
 *   animateOnScroll
 *   scrollConfig={{ triggerOnce: true }}
 * >
 *   {products.map(product => (
 *     <ProductCard key={product.id} product={product} />
 *   ))}
 * </StaggeredGrid>
 *
 * // Reverse stagger (bottom to top)
 * <StaggerSlideUp reverse staggerDelay={50}>
 *   <div>Last to animate</div>
 *   <div>Second to animate</div>
 *   <div>First to animate</div>
 * </StaggerSlideUp>
 * ```
 */
