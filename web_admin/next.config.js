/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'api.sahool.io',
      },
      {
        protocol: 'http',
        hostname: 'localhost',
      },
    ],
  },
  // Enable Arabic RTL support
  i18n: {
    locales: ['ar', 'en'],
    defaultLocale: 'ar',
    localeDetection: true,
  },
};

module.exports = nextConfig;
