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

  // Note: telemetry is disabled via NEXT_TELEMETRY_DISABLED env var in Dockerfile

  // TypeScript - strict mode enabled for production safety
  typescript: {
    // Do NOT ignore build errors - ensures type safety
    ignoreBuildErrors: false,
  },
  eslint: {
    // Ignore ESLint warnings during build - lint job checks separately
    ignoreDuringBuilds: true,
  },

  // Note: swcMinify is enabled by default in Next.js 15

  // Configure webpack for better error handling
  webpack: (config, { isServer }) => {
    // Handle potential module resolution issues
    config.resolve.fallback = {
      ...config.resolve.fallback,
      fs: false,
      net: false,
      tls: false,
    };

    // Add parent node_modules to module resolution for workspace dependencies
    // This allows Next.js to find dependencies hoisted to the root in npm workspaces
    const path = require('path');
    const parentNodeModules = path.resolve(__dirname, '../../node_modules');
    config.resolve.modules = [
      ...(config.resolve.modules || ['node_modules']),
      parentNodeModules,
    ];

    return config;
  },

  // Experimental features
  // Note: missingSuspenseWithCSRBailout was removed in Next.js 15
};

module.exports = nextConfig;
