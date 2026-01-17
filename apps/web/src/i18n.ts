/**
 * i18n Configuration for SAHOOL Web Application
 * Using next-intl with App Router
 */

import { getRequestConfig } from "next-intl/server";
import { locales, defaultLocale, messages, type Locale } from "@sahool/i18n";

export default getRequestConfig(async ({ requestLocale }) => {
  // Await the requestLocale (new API in next-intl 3.22+)
  const locale = await requestLocale;

  // Validate that the incoming locale parameter is valid
  const validLocale = (
    locale && locales.includes(locale as Locale) ? locale : defaultLocale
  ) as Locale;

  return {
    locale: validLocale,
    messages: messages[validLocale],
    timeZone: "Asia/Aden",
    now: new Date(),
  };
});

export { locales, defaultLocale };
export type { Locale };
