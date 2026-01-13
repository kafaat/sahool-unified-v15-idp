/**
 * Locale Switcher Component
 * مكون تبديل اللغة
 *
 * Allows users to switch between Arabic and English
 */

"use client";

import React, { useTransition } from "react";
import { useRouter, usePathname } from "next/navigation";
import { useLocale } from "next-intl";
import { Globe } from "lucide-react";
import { clsx } from "clsx";
import { locales, getLocaleDisplayName } from "@sahool/i18n";

export function LocaleSwitcher() {
  const router = useRouter();
  const pathname = usePathname();
  const currentLocale = useLocale();
  const [isPending, startTransition] = useTransition();

  const handleLocaleChange = (newLocale: string) => {
    startTransition(() => {
      // Remove the current locale from pathname if it exists
      const pathnameWithoutLocale = pathname.replace(/^\/(ar|en)/, "") || "/";

      // Add new locale prefix only if not the default locale
      const newPath =
        newLocale === "ar"
          ? pathnameWithoutLocale
          : `/${newLocale}${pathnameWithoutLocale}`;

      router.replace(newPath);
    });
  };

  return (
    <div className="relative inline-block">
      <div className="flex items-center gap-2 px-3 py-2 bg-white border border-gray-200 rounded-lg">
        <Globe className="w-4 h-4 text-gray-600" />
        <div className="flex gap-1">
          {locales.map((locale) => {
            const isActive = locale === currentLocale;
            return (
              <button
                key={locale}
                onClick={() => handleLocaleChange(locale)}
                disabled={isPending || isActive}
                className={clsx(
                  "px-3 py-1 text-sm font-medium rounded transition-colors",
                  "focus:outline-none focus:ring-2 focus:ring-sahool-green-500",
                  isActive
                    ? "bg-sahool-green-100 text-sahool-green-700"
                    : "text-gray-600 hover:bg-gray-100",
                  isPending && "opacity-50 cursor-wait",
                )}
                aria-label={`Switch to ${getLocaleDisplayName(locale)}`}
                aria-current={isActive ? "true" : undefined}
              >
                {getLocaleDisplayName(locale)}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
