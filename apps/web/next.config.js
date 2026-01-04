const createNextIntlPlugin = require('next-intl/plugin');
const withBundleAnalyzer = require('@next/bundle-analyzer')({
  enabled: process.env.ANALYZE === 'true',
});

const withNextIntl = createNextIntlPlugin('./src/i18n.ts');

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,

  // Security: Remove X-Powered-By header
  poweredByHeader: false,

  // Ignore ESLint warnings during build - lint job checks separately
  eslint: {
    ignoreDuringBuilds: true,
  },

  // TypeScript checking during build
  typescript: {
    // Only ignore in development - fail on type errors in production
    ignoreBuildErrors: process.env.NODE_ENV === 'development',
  },

  // Note: i18n is handled via next-intl for App Router
  // Legacy Pages Router i18n config removed for Next.js 15 compatibility

  // Image optimization
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**.sahool.ye',
      },
      {
        protocol: 'https',
        hostname: '**.sahool.io',
      },
      {
        protocol: 'https',
        hostname: '**.sahool.app',
      },
      {
        protocol: 'https',
        hostname: 'sentinel-hub.com',
      },
    ],
    formats: ['image/avif', 'image/webp'],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
  },

  // Security headers
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
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block',
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin',
          },
          {
            key: 'Permissions-Policy',
            value: 'camera=(), microphone=(), geolocation=(self), payment=(), usb=(), interest-cohort=()',
          },
          // Note: CSP headers are set in middleware.ts with nonce support
          // CSP headers here are for static assets that bypass middleware
          {
            key: 'Cross-Origin-Embedder-Policy',
            value: 'credentialless',
          },
          {
            key: 'Cross-Origin-Opener-Policy',
            value: 'same-origin',
          },
          {
            key: 'Cross-Origin-Resource-Policy',
            value: 'same-origin',
          },
        ],
      },
    ];
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

  // Output configuration for Docker/standalone deployments
  output: process.env.DOCKER_BUILD === 'true' ? 'standalone' : undefined,

  // Performance optimizations
  compress: true,
  productionBrowserSourceMaps: false,

  // Experimental features
  experimental: {
    optimizePackageImports: ['lucide-react', '@tanstack/react-query', 'recharts'],
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

module.exports = withBundleAnalyzer(withNextIntl(nextConfig));
