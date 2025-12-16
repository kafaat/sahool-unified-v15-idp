import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'لوحة تحكم سهول | Sahool Admin Dashboard',
  description: 'لوحة تحكم المشرفين لمنصة سهول الزراعية الذكية',
  keywords: ['سهول', 'زراعة', 'اليمن', 'sahool', 'agriculture', 'yemen'],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ar" dir="rtl">
      <head>
        <link
          rel="stylesheet"
          href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
          integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY="
          crossOrigin=""
        />
      </head>
      <body className="bg-gray-50 min-h-screen font-arabic">
        {children}
      </body>
    </html>
  );
}
