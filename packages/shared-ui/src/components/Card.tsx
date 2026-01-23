"use client";

// ═══════════════════════════════════════════════════════════════════════════════
// Card Component - بطاقة
// Unified card component for content containers
// ═══════════════════════════════════════════════════════════════════════════════

import { cn } from "@sahool/shared-utils";
import { forwardRef, HTMLAttributes, ReactNode } from "react";

/** Card padding options */
export type CardPadding = "none" | "sm" | "md" | "lg";

export interface CardProps extends Omit<HTMLAttributes<HTMLDivElement>, "onClick"> {
  /** Card content */
  children: ReactNode;
  /** Additional CSS classes */
  className?: string;
  /** Padding size */
  padding?: CardPadding;
  /** Enable hover effect */
  hover?: boolean;
  /** Click handler - makes card interactive/focusable */
  onClick?: () => void;
  /** Accessible label for clickable cards */
  "aria-label"?: string;
}

const paddingClasses = {
  none: "",
  sm: "p-3",
  md: "p-4",
  lg: "p-6",
};

export const Card = forwardRef<HTMLDivElement, CardProps>(
  (
    {
      children,
      className = "",
      padding = "md",
      hover = false,
      onClick,
      "aria-label": ariaLabel,
      ...props
    },
    ref,
  ) => {
    const isClickable = !!onClick;

    const handleKeyDown = (e: React.KeyboardEvent<HTMLDivElement>) => {
      if (onClick && (e.key === "Enter" || e.key === " ")) {
        e.preventDefault();
        onClick();
      }
    };

    return (
      <div
        ref={ref}
        className={cn(
          "bg-white rounded-lg border border-gray-200 shadow-sm",
          paddingClasses[padding],
          hover && "hover:shadow-md transition-shadow cursor-pointer",
          isClickable && "focus:outline-none focus:ring-2 focus:ring-sahool-500 focus:ring-offset-2",
          className,
        )}
        onClick={onClick}
        onKeyDown={isClickable ? handleKeyDown : undefined}
        role={isClickable ? "button" : undefined}
        tabIndex={isClickable ? 0 : undefined}
        aria-label={isClickable ? ariaLabel : undefined}
        {...props}
      >
        {children}
      </div>
    );
  },
);

Card.displayName = "Card";

export interface CardHeaderProps {
  title: string;
  subtitle?: string;
  action?: ReactNode;
  className?: string;
}

export function CardHeader({
  title,
  subtitle,
  action,
  className = "",
}: CardHeaderProps) {
  return (
    <div className={cn("flex items-start justify-between mb-4", className)}>
      <div>
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        {subtitle && <p className="text-sm text-gray-500 mt-1">{subtitle}</p>}
      </div>
      {action && <div>{action}</div>}
    </div>
  );
}

export interface CardContentProps {
  children: ReactNode;
  className?: string;
}

export function CardContent({ children, className = "" }: CardContentProps) {
  return <div className={cn("", className)}>{children}</div>;
}

export interface CardFooterProps {
  children: ReactNode;
  className?: string;
}

export function CardFooter({ children, className = "" }: CardFooterProps) {
  return (
    <div className={cn("mt-4 pt-4 border-t border-gray-100", className)}>
      {children}
    </div>
  );
}
