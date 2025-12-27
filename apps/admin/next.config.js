/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',

  // Security Headers
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'X-DNS-Prefetch-Control',
            value: 'on',
          },
          {
            key: 'Strict-Transport-Security',
            value: 'max-age=63072000; includeSubDomains; preload',
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block',
          },
          {
            key: 'X-Frame-Options',
            value: 'SAMEORIGIN',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin',
          },
          {
            key: 'Permissions-Policy',
            value: 'camera=(), microphone=(), geolocation=(self), interest-cohort=()',
          },
          {
            key: 'Content-Security-Policy',
            value: [
              "default-src 'self'",
              "script-src 'self' 'unsafe-inline' 'unsafe-eval'",
              "style-src 'self' 'unsafe-inline'",
              "img-src 'self' data: https: blob:",
              "font-src 'self' data:",
              "connect-src 'self' https://api.sahool.io https://api.sahool.app wss:",
              "frame-ancestors 'self'",
              "base-uri 'self'",
              "form-action 'self'",
            ].join('; '),
          },
        ],
      },
    ];
  },

  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'api.sahool.io',
      },
      {
        protocol: 'https',
        hostname: 'api.sahool.app',
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
