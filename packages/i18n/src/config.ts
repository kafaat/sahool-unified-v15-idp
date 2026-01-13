/**
 * i18n Configuration for Next.js App Router
 */

import { getRequestConfig } from "next-intl/server";
import { locales, defaultLocale, type Locale } from "./index";

export default getRequestConfig(async ({ locale }) => {
  // Validate that the incoming `locale` parameter is valid
  const validLocale = locales.includes(locale as Locale)
    ? locale
    : defaultLocale;

  return {
    messages: (await import(`./locales/${validLocale}.json`)).default,
    timeZone: "Asia/Aden",
    now: new Date(),
  };
});

export { locales, defaultLocale };
export type { Locale };
