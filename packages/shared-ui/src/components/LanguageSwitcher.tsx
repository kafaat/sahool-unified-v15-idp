"use client";

import React from "react";

export interface LanguageSwitcherProps {
  currentLocale: "ar" | "en";
  onLocaleChange: (locale: "ar" | "en") => void;
  className?: string;
}

const localeNames = {
  ar: "العربية",
  en: "English",
};

/**
 * Language Switcher Component
 * مكون تبديل اللغة
 */
export function LanguageSwitcher({
  currentLocale,
  onLocaleChange,
  className = "",
}: LanguageSwitcherProps) {
  const otherLocale = currentLocale === "ar" ? "en" : "ar";

  return (
    <button
      type="button"
      onClick={() => onLocaleChange(otherLocale)}
      className={`
        inline-flex items-center gap-2 px-3 py-1.5
        text-sm font-medium rounded-md
        bg-gray-100 hover:bg-gray-200
        dark:bg-gray-800 dark:hover:bg-gray-700
        text-gray-700 dark:text-gray-300
        transition-colors duration-200
        ${className}
      `}
      aria-label={`Switch to ${localeNames[otherLocale]}`}
    >
      <span className="text-base">🌐</span>
      <span>{localeNames[otherLocale]}</span>
    </button>
  );
}

export default LanguageSwitcher;
