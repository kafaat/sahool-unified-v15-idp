"use client";

import { cn } from "@sahool/shared-utils";
import { Globe } from "lucide-react";
import { ButtonHTMLAttributes, forwardRef } from "react";

/** Supported locale options */
export type SupportedLocale = "ar" | "en";

export interface LanguageSwitcherProps extends Omit<ButtonHTMLAttributes<HTMLButtonElement>, "onClick"> {
  /** Current active locale */
  currentLocale: SupportedLocale;
  /** Callback when locale changes */
  onLocaleChange: (locale: SupportedLocale) => void;
  /** Additional CSS classes */
  className?: string;
  /** Size variant */
  size?: "sm" | "md" | "lg";
  /** Show full language name or just code */
  showFullName?: boolean;
}

const localeNames: Record<SupportedLocale, string> = {
  ar: "العربية",
  en: "English",
};

const localeCodes: Record<SupportedLocale, string> = {
  ar: "AR",
  en: "EN",
};

const sizeClasses = {
  sm: "px-2 py-1 text-xs gap-1",
  md: "px-3 py-1.5 text-sm gap-2",
  lg: "px-4 py-2 text-base gap-2",
};

const iconSizes = {
  sm: 12,
  md: 16,
  lg: 20,
};

/**
 * Language Switcher Component
 * مكون تبديل اللغة
 *
 * Allows users to switch between Arabic and English locales.
 *
 * @example
 * <LanguageSwitcher
 *   currentLocale="ar"
 *   onLocaleChange={(locale) => setLocale(locale)}
 * />
 */
export const LanguageSwitcher = forwardRef<HTMLButtonElement, LanguageSwitcherProps>(
  (
    {
      currentLocale,
      onLocaleChange,
      className,
      size = "md",
      showFullName = true,
      ...props
    },
    ref,
  ) => {
    const otherLocale: SupportedLocale = currentLocale === "ar" ? "en" : "ar";
    const displayText = showFullName ? localeNames[otherLocale] : localeCodes[otherLocale];

    return (
      <button
        ref={ref}
        type="button"
        onClick={() => onLocaleChange(otherLocale)}
        className={cn(
          "inline-flex items-center font-medium rounded-md",
          "bg-gray-100 hover:bg-gray-200",
          "text-gray-700",
          "transition-colors duration-200",
          "focus:outline-none focus:ring-2 focus:ring-sahool-500 focus:ring-offset-2",
          sizeClasses[size],
          className,
        )}
        aria-label={`Switch language to ${localeNames[otherLocale]}`}
        lang={otherLocale}
        {...props}
      >
        <Globe size={iconSizes[size]} aria-hidden="true" />
        <span>{displayText}</span>
      </button>
    );
  },
);

LanguageSwitcher.displayName = "LanguageSwitcher";
