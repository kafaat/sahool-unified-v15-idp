import type { Metadata } from 'next';
import { NextIntlClientProvider } from 'next-intl';
import { getMessages } from 'next-intl/server';
import { notFound } from 'next/navigation';
import './globals.css';
import { Providers } from './providers';
import { ErrorBoundary } from '@/components/common/ErrorBoundary';
import { locales, getDirection, type Locale } from '@sahool/i18n';

export const metadata: Metadata = {
  title: 'سهول | SAHOOL - Smart Agriculture Platform',
  description: 'منصة سهول الزراعية الذكية - SAHOOL Smart Agricultural Platform for Yemen',
  keywords: ['سهول', 'زراعة', 'اليمن', 'sahool', 'agriculture', 'yemen', 'smart farming'],
};

export function generateStaticParams() {
  return locales.map((locale) => ({ locale }));
}

export default async function RootLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: Promise<{ locale?: string }>;
}) {
  // In Next.js 15, params are Promises
  const resolvedParams = await params;
  // Default to 'ar' if no locale is provided
  const localeStr = resolvedParams.locale || 'ar';

  // Type guard to check if locale is valid
  const isValidLocale = (l: string): l is Locale => {
    return locales.includes(l as Locale);
  };

  // Validate locale
  if (!isValidLocale(localeStr)) {
    notFound();
  }

  const locale: Locale = localeStr;
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
        <ErrorBoundary>
          <NextIntlClientProvider messages={messages} locale={locale}>
            <Providers>{children}</Providers>
          </NextIntlClientProvider>
        </ErrorBoundary>
      </body>
    </html>
  );
}
