/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,

  // Internationalization
  i18n: {
    locales: ['ar', 'en'],
    defaultLocale: 'ar',
    localeDetection: true,
  },

  // Image optimization
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**.sahool.ye',
      },
      {
        protocol: 'https',
        hostname: 'sentinel-hub.com',
      },
    ],
  },

  // API rewrites for backend services
  async rewrites() {
    return [
      {
        source: '/api/v1/:path*',
        destination: `${process.env.API_URL || 'http://localhost:8000'}/api/v1/:path*`,
      },
    ];
  },

  // Environment variables exposed to browser
  env: {
    NEXT_PUBLIC_APP_NAME: 'SAHOOL',
    NEXT_PUBLIC_APP_VERSION: '16.0.0',
  },

  // Webpack configuration for Leaflet
  webpack: (config) => {
    config.resolve.fallback = {
      ...config.resolve.fallback,
      fs: false,
    };
    return config;
  },
};

module.exports = nextConfig;
