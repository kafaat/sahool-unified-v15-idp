const withBundleAnalyzer = require("@next/bundle-analyzer")({
  enabled: process.env.ANALYZE === "true",
});

/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "standalone",

  // Transpile workspace packages so Next.js compiles them from source
  // This avoids dependency on pre-built dist/ directories from build:packages
  transpilePackages: [
    "@sahool/shared-ui",
    "@sahool/shared-utils",
    "@sahool/shared-hooks",
    "@sahool/shared-types",
    "@sahool/api-client",
  ],

  // Security Headers
  async headers() {
    return [
      {
        source: "/:path*",
        headers: [
          {
            key: "X-DNS-Prefetch-Control",
            value: "on",
          },
          {
            key: "Strict-Transport-Security",
            value: "max-age=63072000; includeSubDomains; preload",
          },
          {
            key: "X-XSS-Protection",
            value: "1; mode=block",
          },
          {
            key: "X-Frame-Options",
            value: "SAMEORIGIN",
          },
          {
            key: "X-Content-Type-Options",
            value: "nosniff",
          },
          {
            key: "Referrer-Policy",
            value: "strict-origin-when-cross-origin",
          },
          {
            key: "Permissions-Policy",
            value:
              "camera=(), microphone=(), geolocation=(self), interest-cohort=()",
          },
          // CSP is now handled by middleware with nonce-based security
          // See: src/middleware.ts and src/lib/security/csp-config.ts
        ],
      },
    ];
  },

  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "api.sahool.io",
      },
      {
        protocol: "https",
        hostname: "api.sahool.app",
      },
      {
        protocol: "http",
        hostname: "localhost",
      },
    ],
  },
  // RTL support is handled in layout.tsx via lang="ar" dir="rtl"
  // For full i18n with App Router, use next-intl or similar library

  // Note: telemetry is disabled via NEXT_TELEMETRY_DISABLED env var in Dockerfile

  // TypeScript - ignore during build since type-check runs separately in CI
  typescript: {
    // Type checking is done by dedicated 'typecheck' job in CI pipeline
    ignoreBuildErrors: true,
  },

  // ESLint - ignore during build since lint runs separately in CI
  eslint: {
    ignoreDuringBuilds: true,
  },

  // Note: eslint configuration moved to .eslintrc.json or eslint.config.js
  // See: https://nextjs.org/docs/app/api-reference/cli/next#next-lint-options

  // Note: swcMinify is enabled by default in Next.js 15+

  // Security: Remove X-Powered-By header
  poweredByHeader: false,

  // Performance optimizations
  compress: true,
  productionBrowserSourceMaps: false,

  // Turbopack configuration (Next.js 16 default bundler)
  turbopack: {
    // Empty config to acknowledge Turbopack usage and silence warnings
    // Turbopack handles module resolution automatically for workspace dependencies
  },

  // Configure webpack for better error handling (fallback when using --webpack flag)
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
    const path = require("path");
    const parentNodeModules = path.resolve(__dirname, "../../node_modules");
    config.resolve.modules = [
      ...(config.resolve.modules || ["node_modules"]),
      parentNodeModules,
    ];

    // Suppress OpenTelemetry critical dependency warnings from @sentry/nextjs
    // These warnings occur due to dynamic requires in OpenTelemetry instrumentation
    // and don't affect functionality when Sentry DSN is not configured
    config.ignoreWarnings = [
      ...(config.ignoreWarnings || []),
      {
        module: /@opentelemetry\/instrumentation/,
        message: /Critical dependency/,
      },
      {
        module: /@sentry/,
        message: /Critical dependency/,
      },
    ];

    return config;
  },

  // Experimental features
  experimental: {
    optimizePackageImports: [
      "lucide-react",
      "recharts",
      "date-fns",
      "clsx",
      "tailwind-merge",
      "@sahool/shared-ui",
      "@sahool/shared-utils",
      "@sahool/shared-hooks",
    ],
  },
  // Note: missingSuspenseWithCSRBailout was removed in Next.js 15
};

module.exports = withBundleAnalyzer(nextConfig);
