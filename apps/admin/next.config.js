let withSentryConfig;
let sentryInstalled = false;
try {
  withSentryConfig = require("@sentry/nextjs").withSentryConfig;
  sentryInstalled = true;
} catch (/** @type {any} */ err) {
  // Only swallow when @sentry/nextjs itself is missing; rethrow transitive failures
  const isSentryMissing =
    err?.code === "MODULE_NOT_FOUND" &&
    /['"]@sentry\/nextjs['"]/.test(err?.message ?? "");
  if (!isSentryMissing) throw err;
  // Fail fast when Sentry is expected (DSN configured) but the package is missing.
  // This prevents silently disabling source-map upload / instrumentation in CI/prod.
  if (process.env.NEXT_PUBLIC_SENTRY_DSN) {
    throw new Error(
      "@sentry/nextjs is not installed but NEXT_PUBLIC_SENTRY_DSN is set. " +
      "Install the package or remove the DSN to build without Sentry."
    );
  }
  withSentryConfig = null;
}

const withBundleAnalyzer = require("@next/bundle-analyzer")({
  enabled: process.env.ANALYZE === "true",
});

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: "standalone",

  // Security: Remove X-Powered-By header
  poweredByHeader: false,

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
            value: "DENY",
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
              "camera=(), microphone=(), geolocation=(self), payment=(), usb=(), interest-cohort=()",
          },
          // CSP is now handled by middleware with nonce-based security
          // See: src/middleware.ts and src/lib/security/csp-config.ts
          {
            key: "Cross-Origin-Embedder-Policy",
            value: "credentialless",
          },
          {
            key: "Cross-Origin-Opener-Policy",
            value: "same-origin",
          },
          {
            key: "Cross-Origin-Resource-Policy",
            value: "same-origin",
          },
        ],
      },
      // Static assets - long-term caching (content-hashed, immutable)
      {
        source: "/_next/static/:path*",
        headers: [
          {
            key: "Cache-Control",
            value: "public, max-age=31536000, immutable",
          },
        ],
      },
    ];
  },

  // API rewrites for backend services
  // Uses API_GATEWAY_URL (server-side, runtime) with NEXT_PUBLIC_API_URL as fallback.
  // In production (Docker/K8s), set API_GATEWAY_URL to the internal Kong URL.
  // NEXT_PUBLIC_API_URL is baked at build-time and should only be used for dev.
  async rewrites() {
    const apiOrigin =
      process.env.API_GATEWAY_URL ||
      process.env.NEXT_PUBLIC_API_URL ||
      "http://localhost:8000";
    return [
      {
        source: "/api/v1/:path*",
        destination: `${apiOrigin}/api/v1/:path*`,
      },
    ];
  },

  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "**.sahool.ye",
      },
      {
        protocol: "https",
        hostname: "**.sahool.io",
      },
      {
        protocol: "https",
        hostname: "**.sahool.app",
      },
      {
        protocol: "http",
        hostname: "localhost",
      },
    ],
    // Serve modern formats for smaller image payloads
    formats: ["image/avif", "image/webp"],
    // Breakpoints for srcset generation matching common device widths
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    // Sizes for images rendered smaller than the viewport (icons, thumbnails, avatars)
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
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

  // Compiler optimizations
  compiler: {
    // Strip console.log in production (keep error/warn for debugging)
    removeConsole:
      process.env.NODE_ENV === "production"
        ? { exclude: ["error", "warn"] }
        : false,
  },

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

    // When @sentry/nextjs is not installed, alias it to a real (empty) shim.
    // Using `false` causes webpack to generate a module reference without a
    // factory function, which crashes at runtime with
    // "Cannot read properties of undefined (reading 'call')".
    if (!sentryInstalled) {
      const path = require("path");
      config.resolve.alias = {
        ...config.resolve.alias,
        "@sentry/nextjs": path.resolve(__dirname, "src/lib/sentry-shim.ts"),
      };
    }

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

    // Optimize chunk splitting for better caching and smaller bundles
    if (!isServer) {
      config.optimization = {
        ...config.optimization,
        splitChunks: {
          ...config.optimization?.splitChunks,
          cacheGroups: {
            ...config.optimization?.splitChunks?.cacheGroups,
            // Separate heavy visualization libs into their own chunk
            charts: {
              test: /[\\/]node_modules[\\/](recharts|d3-.*|victory.*)[\\/]/,
              name: "charts",
              chunks: "all",
              priority: 30,
            },
            // Separate mapping libraries (leaflet) into their own chunk
            maps: {
              test: /[\\/]node_modules[\\/](leaflet|react-leaflet)[\\/]/,
              name: "maps",
              chunks: "all",
              priority: 30,
            },
            // Group framework-level dependencies that rarely change
            framework: {
              test: /[\\/]node_modules[\\/](react|react-dom|next|scheduler)[\\/]/,
              name: "framework",
              chunks: "all",
              priority: 40,
              enforce: true,
            },
          },
        },
      };
    }

    return config;
  },

  // Experimental features
  experimental: {
    // Tree-shake barrel exports for these packages to reduce bundle size
    optimizePackageImports: [
      "lucide-react",
      "recharts",
      "date-fns",
      "clsx",
      "tailwind-merge",
      "@sahool/shared-ui",
      "@sahool/shared-utils",
      "@sahool/shared-hooks",
      "@sahool/shared-types",
      "@sahool/api-client",
      "react-leaflet",
      "jose",
      "axios",
    ],
  },
  // Note: missingSuspenseWithCSRBailout was removed in Next.js 15
};

const sentryOptions = {
  // Sentry Build-Time Optimizations
  // https://docs.sentry.io/platforms/javascript/guides/nextjs/manual-setup/

  // Suppress source map upload logs during build
  silent: !process.env.CI,

  // Upload source maps to Sentry for production builds only
  sourcemaps: {
    disable: !process.env.SENTRY_AUTH_TOKEN,
  },

  // Tree-shake Sentry debug logger statements from the client bundle (~10KB savings)
  disableLogger: true,

  // Automatically tree-shake unused Sentry client code
  // Removes code for features not used (e.g., Profiling, Feedback widget)
  bundleSizeOptimizations: {
    excludeDebugStatements: true,
    excludeReplayIframe: true,
    excludeReplayShadowDom: true,
    excludeReplayWorker: true,
  },

  // Tunnel Sentry events through the Next.js server to avoid ad-blockers and CSP issues
  tunnelRoute: "/monitoring",

  // Hides Sentry source maps from client-side devtools
  hideSourceMaps: true,

  // Widen file upload scope so Sentry can match source maps across chunks
  widenClientFileUpload: true,
};

module.exports = withSentryConfig
  ? withSentryConfig(withBundleAnalyzer(nextConfig), sentryOptions)
  : withBundleAnalyzer(nextConfig);
