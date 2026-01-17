"use client";

/**
 * Input Component
 * مكون الإدخال
 *
 * A flexible form input component with label, error, and hint support
 */

import * as React from "react";
import { AlertCircle } from "lucide-react";
import { cn } from "@sahool/shared-utils";

// ═══════════════════════════════════════════════════════════════════════════
// Types
// ═══════════════════════════════════════════════════════════════════════════

export interface InputProps extends Omit<
  React.InputHTMLAttributes<HTMLInputElement>,
  "size"
> {
  /** Input label */
  label?: string;
  /** Error message */
  error?: string;
  /** Hint text */
  hint?: string;
  /** Input size */
  size?: "sm" | "md" | "lg";
  /** Left icon */
  leftIcon?: React.ReactNode;
  /** Right icon */
  rightIcon?: React.ReactNode;
  /** Full width */
  fullWidth?: boolean;
}

// ═══════════════════════════════════════════════════════════════════════════
// Component
// ═══════════════════════════════════════════════════════════════════════════

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  (
    {
      label,
      error,
      hint,
      size = "md",
      leftIcon,
      rightIcon,
      fullWidth = true,
      className,
      id,
      disabled,
      required,
      ...props
    },
    ref,
  ) => {
    const inputId = id || React.useId();
    const errorId = `${inputId}-error`;
    const hintId = `${inputId}-hint`;

    const sizeClasses = {
      sm: "px-2.5 py-1.5 text-sm",
      md: "px-3 py-2 text-base",
      lg: "px-4 py-3 text-lg",
    };

    const iconSizeClasses = {
      sm: "w-4 h-4",
      md: "w-5 h-5",
      lg: "w-6 h-6",
    };

    return (
      <div className={cn("flex flex-col gap-1.5", fullWidth && "w-full")}>
        {label && (
          <label
            htmlFor={inputId}
            className={cn(
              "text-sm font-medium text-gray-700",
              disabled && "text-gray-400",
            )}
          >
            {label}
            {required && <span className="text-red-500 ms-1">*</span>}
          </label>
        )}

        <div className="relative">
          {leftIcon && (
            <div
              className={cn(
                "absolute start-3 top-1/2 -translate-y-1/2 text-gray-400",
                iconSizeClasses[size],
              )}
            >
              {leftIcon}
            </div>
          )}

          <input
            ref={ref}
            id={inputId}
            disabled={disabled}
            required={required}
            aria-invalid={!!error}
            aria-describedby={error ? errorId : hint ? hintId : undefined}
            className={cn(
              "block rounded-lg border bg-white text-gray-900 transition-colors",
              "placeholder:text-gray-400",
              "focus:outline-none focus:ring-2 focus:ring-offset-0",
              sizeClasses[size],
              leftIcon && "ps-10",
              (rightIcon || error) && "pe-10",
              error
                ? "border-red-500 focus:border-red-500 focus:ring-red-200"
                : "border-gray-300 focus:border-sahool-500 focus:ring-sahool-200",
              disabled && "bg-gray-100 text-gray-500 cursor-not-allowed",
              fullWidth && "w-full",
              className,
            )}
            {...props}
          />

          {(rightIcon || error) && (
            <div
              className={cn(
                "absolute end-3 top-1/2 -translate-y-1/2",
                iconSizeClasses[size],
                error ? "text-red-500" : "text-gray-400",
              )}
            >
              {error ? <AlertCircle /> : rightIcon}
            </div>
          )}
        </div>

        {error && (
          <p id={errorId} role="alert" className="text-sm text-red-600">
            {error}
          </p>
        )}

        {hint && !error && (
          <p id={hintId} className="text-sm text-gray-500">
            {hint}
          </p>
        )}
      </div>
    );
  },
);

Input.displayName = "Input";

export default Input;
