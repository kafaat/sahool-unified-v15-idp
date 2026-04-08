import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Allow satellite imagery from Mapbox and Sentinel Hub tiles
  images: {
    remotePatterns: [
      { protocol: "https", hostname: "**.mapbox.com" },
      { protocol: "https", hostname: "services.sentinel-hub.com" },
      { protocol: "https", hostname: "api.openweathermap.org" },
    ],
  },
  // Proxy SH process API images through Next.js to keep credentials server-side
  async headers() {
    return [
      {
        source: "/api/sentinel/:path*",
        headers: [{ key: "Cache-Control", value: "public, max-age=3600, stale-while-revalidate=86400" }],
      },
    ];
  },
};

export default nextConfig;
