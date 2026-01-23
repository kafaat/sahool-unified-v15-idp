"use client";

import { cn } from "@sahool/shared-utils";
import { ElementType, HTMLAttributes, ReactNode } from "react";

/** Allowed HTML elements for VisuallyHidden */
export type VisuallyHiddenElement = "span" | "div" | "p" | "h1" | "h2" | "h3" | "h4" | "h5" | "h6" | "label";

export interface VisuallyHiddenProps extends HTMLAttributes<HTMLElement> {
  /** Content to be visually hidden but accessible to screen readers */
  children: ReactNode;
  /** HTML element to render */
  as?: VisuallyHiddenElement;
  /** Additional CSS classes */
  className?: string;
  /** Whether to make visible on focus (for skip links, etc.) */
  focusable?: boolean;
}

/**
 * Visually Hidden Component for Screen Readers
 * مكون مخفي بصرياً لقارئات الشاشة
 *
 * Hides content visually while keeping it accessible to assistive technologies.
 *
 * @example
 * <VisuallyHidden>Additional context for screen readers</VisuallyHidden>
 * <VisuallyHidden as="h2">Section heading</VisuallyHidden>
 */
export function VisuallyHidden({
  children,
  as: Component = "span",
  className,
  focusable = false,
  ...props
}: VisuallyHiddenProps) {
  const Element = Component as ElementType;

  return (
    <Element
      className={cn(
        "sr-only",
        focusable && "focus:not-sr-only",
        className,
      )}
      {...props}
    >
      {children}
    </Element>
  );
}
