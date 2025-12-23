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
  // RTL support is handled in layout.tsx via lang="ar" dir="rtl"
  // For full i18n with App Router, use next-intl or similar library

  // Disable telemetry for Docker builds
  telemetry: {
    enabled: false,
  },

  // TypeScript - strict mode enabled for production safety
  typescript: {
    // Do NOT ignore build errors - ensures type safety
    ignoreBuildErrors: false,
  },
  eslint: {
    // Ignore ESLint warnings during build - lint job checks separately
    ignoreDuringBuilds: true,
  },

  // Optimize for production
  swcMinify: true,

  // Configure webpack for better error handling
  webpack: (config, { isServer }) => {
    // Handle potential module resolution issues
    config.resolve.fallback = {
      ...config.resolve.fallback,
      fs: false,
      net: false,
      tls: false,
    };

    return config;
  },

  // Experimental features
  experimental: {
    missingSuspenseWithCSRBailout: false,
  },
};

module.exports = nextConfig;
