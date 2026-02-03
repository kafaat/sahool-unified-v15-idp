import type { Metadata } from "next";
import { headers } from "next/headers";
import "./globals.css";
import { Providers } from "./providers";

export const metadata: Metadata = {
  title: "لوحة تحكم سهول | Sahool Admin Dashboard",
  description: "لوحة تحكم المشرفين لمنصة سهول الزراعية الذكية",
  keywords: ["سهول", "زراعة", "اليمن", "sahool", "agriculture", "yemen"],
  icons: {
    icon: [
      { url: "/favicon.ico", sizes: "any" },
      { url: "/icon-192.png", sizes: "192x192", type: "image/png" },
      { url: "/icon-512.png", sizes: "512x512", type: "image/png" },
    ],
    apple: [{ url: "/icon-192.png", sizes: "192x192" }],
  },
};

// Force dynamic rendering to prevent static generation issues
export const dynamic = "force-dynamic";

export default async function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  // Get nonce from headers for CSP (set by middleware)
  const headersList = await headers();
  const nonce = headersList.get("X-Nonce") || "";

  return (
    // suppressHydrationWarning prevents errors from browser extensions (e.g., Dark Reader)
    // that modify DOM attributes during hydration
    <html lang="ar" dir="rtl" suppressHydrationWarning>
      <head suppressHydrationWarning>
        {/*
          Always render nonce attribute to prevent hydration mismatch.
          The nonce value may be empty string on client, but the attribute must be present.
        */}
        { }
        <link
          href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap"
          rel="stylesheet"
          nonce={nonce}
          suppressHydrationWarning
        />
        <link
          rel="stylesheet"
          href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
          integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY="
          crossOrigin=""
          nonce={nonce}
          suppressHydrationWarning
        />
      </head>
      <body className="font-tajawal bg-gray-50 min-h-screen" suppressHydrationWarning>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
