"use client";

import { cn } from "@sahool/shared-utils";
import { AnchorHTMLAttributes, forwardRef, ReactNode } from "react";

export interface SkipLinkProps extends AnchorHTMLAttributes<HTMLAnchorElement> {
  /** Target element ID (with or without #) */
  href?: string;
  /** Link text content */
  children?: ReactNode;
  /** Additional CSS classes */
  className?: string;
}

/**
 * Skip Link Component for Accessibility
 * مكون تخطي الروابط لإمكانية الوصول
 *
 * Provides a way for keyboard users to skip navigation and jump to main content.
 * Invisible by default, appears on focus.
 *
 * @example
 * <SkipLink href="#main-content">Skip to main content</SkipLink>
 */
export const SkipLink = forwardRef<HTMLAnchorElement, SkipLinkProps>(
  (
    {
      href = "#main-content",
      children = "تخطي إلى المحتوى الرئيسي",
      className,
      ...props
    },
    ref,
  ) => {
    return (
      <a
        ref={ref}
        href={href}
        className={cn(
          "sr-only focus:not-sr-only",
          "focus:absolute focus:top-4 focus:start-4 focus:z-50",
          "focus:px-4 focus:py-2 focus:rounded-md",
          "focus:bg-sahool-600 focus:text-white",
          "focus:outline-none focus:ring-2 focus:ring-sahool-500 focus:ring-offset-2",
          className,
        )}
        {...props}
      >
        {children}
      </a>
    );
  },
);

SkipLink.displayName = "SkipLink";
