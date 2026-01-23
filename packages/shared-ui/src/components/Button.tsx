"use client";

// ═══════════════════════════════════════════════════════════════════════════════
// Button Component - زر
// Unified button component with variants
// ═══════════════════════════════════════════════════════════════════════════════

import { cn } from "@sahool/shared-utils";
import { ButtonHTMLAttributes, forwardRef, ReactNode } from "react";
import { Loader2, LucideIcon } from "lucide-react";

/** Button visual variants */
export type ButtonVariant = "primary" | "secondary" | "outline" | "ghost" | "danger";

/** Button size options */
export type ButtonSize = "sm" | "md" | "lg";

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  /** Visual style variant of the button */
  variant?: ButtonVariant;
  /** Size of the button */
  size?: ButtonSize;
  /** Shows loading spinner and disables the button */
  loading?: boolean;
  /** Loading text announced to screen readers */
  loadingText?: string;
  /** Icon component from lucide-react */
  icon?: LucideIcon;
  /** Position of the icon relative to children */
  iconPosition?: "left" | "right";
  /** Button content */
  children: ReactNode;
}

const variantClasses = {
  primary: "bg-sahool-600 text-white hover:bg-sahool-700 focus:ring-sahool-500",
  secondary: "bg-gray-100 text-gray-900 hover:bg-gray-200 focus:ring-gray-500",
  outline:
    "border border-gray-300 text-gray-700 hover:bg-gray-50 focus:ring-gray-500",
  ghost: "text-gray-700 hover:bg-gray-100 focus:ring-gray-500",
  danger: "bg-red-600 text-white hover:bg-red-700 focus:ring-red-500",
};

const sizeClasses = {
  sm: "px-3 py-1.5 text-sm",
  md: "px-4 py-2 text-base",
  lg: "px-6 py-3 text-lg",
};

const iconSizes = {
  sm: 14,
  md: 16,
  lg: 20,
};

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant = "primary",
      size = "md",
      loading = false,
      loadingText = "جاري التحميل...",
      icon: Icon,
      iconPosition = "left",
      className = "",
      disabled,
      children,
      "aria-label": ariaLabel,
      ...props
    },
    ref,
  ) => {
    const isDisabled = disabled || loading;

    return (
      <button
        ref={ref}
        className={cn(
          "inline-flex items-center justify-center gap-2 rounded-lg font-medium transition-colors",
          "focus:outline-none focus:ring-2 focus:ring-offset-2",
          "disabled:opacity-50 disabled:cursor-not-allowed",
          variantClasses[variant],
          sizeClasses[size],
          className,
        )}
        disabled={isDisabled}
        aria-disabled={isDisabled}
        aria-busy={loading}
        aria-label={loading ? loadingText : ariaLabel}
        {...props}
      >
        {loading && (
          <Loader2
            className="animate-spin"
            size={iconSizes[size]}
            aria-hidden="true"
          />
        )}
        {!loading && Icon && iconPosition === "left" && (
          <Icon size={iconSizes[size]} aria-hidden="true" />
        )}
        <span>{children}</span>
        {!loading && Icon && iconPosition === "right" && (
          <Icon size={iconSizes[size]} aria-hidden="true" />
        )}
      </button>
    );
  },
);

Button.displayName = "Button";
