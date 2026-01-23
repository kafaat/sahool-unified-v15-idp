/**
 * i18n Configuration for Next.js App Router
 *
 * This configuration integrates with next-intl for server-side rendering
 * and provides locale-aware settings for the SAHOOL platform.
 */

import { getRequestConfig } from "next-intl/server";
import { locales, defaultLocale, getRegionalConfig, type Locale } from "./index";

export default getRequestConfig(async ({ locale }) => {
  // Validate that the incoming `locale` parameter is valid
  const validLocale = locales.includes(locale as Locale)
    ? (locale as Locale)
    : defaultLocale;

  // Get regional configuration for the default region (Yemen)
  const regionalConfig = getRegionalConfig();

  return {
    messages: (await import(`./locales/${validLocale}.json`)).default,
    timeZone: regionalConfig.timeZone,
    now: new Date(),
    // Additional formatting options
    formats: {
      dateTime: {
        short: {
          day: "numeric",
          month: "short",
          year: "numeric",
        },
        medium: {
          day: "numeric",
          month: "long",
          year: "numeric",
        },
        long: {
          day: "numeric",
          month: "long",
          year: "numeric",
          weekday: "long",
        },
        // Note: For Hijri calendar formatting, use the formatHijriDate utility
        // from @sahool/i18n instead of this format preset
      },
      number: {
        precise: {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2,
        },
        compact: {
          notation: "compact" as const,
        },
        percentage: {
          style: "percent" as const,
          minimumFractionDigits: 1,
          maximumFractionDigits: 1,
        },
        currency: {
          style: "currency" as const,
          currency: regionalConfig.currency,
        },
      },
    },
  };
});

export { locales, defaultLocale };
export type { Locale };
