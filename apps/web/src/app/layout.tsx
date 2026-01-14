import type { Metadata } from "next";
import { NextIntlClientProvider } from "next-intl";
import { getMessages, getLocale } from "next-intl/server";
import "./globals.css";
import { Providers } from "./providers";
import { ErrorBoundary } from "@/components/common/ErrorBoundary";
import { getDirection, type Locale } from "@sahool/i18n";

export const metadata: Metadata = {
  title: "سهول | SAHOOL - Smart Agriculture Platform",
  description:
    "منصة سهول الزراعية الذكية - SAHOOL Smart Agricultural Platform for Yemen",
  keywords: [
    "سهول",
    "زراعة",
    "اليمن",
    "sahool",
    "agriculture",
    "yemen",
    "smart farming",
  ],
};

export default async function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  // Get locale from next-intl (configured in i18n.ts)
  const locale = (await getLocale()) as Locale;
  const messages = await getMessages();
  const direction = getDirection(locale);

  return (
    <html lang={locale} dir={direction}>
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap"
          rel="stylesheet"
        />
        <link
          rel="stylesheet"
          href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
          integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY="
          crossOrigin=""
        />
      </head>
      <body className="font-tajawal bg-gray-50 min-h-screen">
        <a
          href="#main-content"
          className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:start-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-blue-600 focus:text-white focus:rounded-lg focus:shadow-lg"
        >
          {direction === "rtl"
            ? "انتقل إلى المحتوى الرئيسي"
            : "Skip to main content"}
        </a>
        <ErrorBoundary>
          <NextIntlClientProvider messages={messages} locale={locale}>
            <Providers>{children}</Providers>
          </NextIntlClientProvider>
        </ErrorBoundary>
      </body>
    </html>
  );
}
