const path = require("path");

let withSentryConfig;
let sentryInstalled = false;
try {
  withSentryConfig = require("@sentry/nextjs").withSentryConfig;
  sentryInstalled = true;
} catch (/** @type {any} */ err) {
  // Swallow MODULE_NOT_FOUND for @sentry/nextjs or any of its transitive deps
  // (e.g. next/constants when next is not hoisted to root in monorepo)
  if (err?.code !== "MODULE_NOT_FOUND") throw err;
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

const createNextIntlPlugin = require("next-intl/plugin");
const withBundleAnalyzer = require("@next/bundle-analyzer")({
  enabled: process.env.ANALYZE === "true",
});

const withNextIntl = createNextIntlPlugin("./src/i18n.ts");

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,

  // Allow cross-origin requests from local network in development
  // (prevents "Cross origin request detected" warning)
  allowedDevOrigins: (process.env.ALLOWED_DEV_ORIGINS?.split(",").map(s => s.trim()).filter(Boolean)) || ["localhost", "127.0.0.1"],

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
    "@sahool/i18n",
    "@sahool/design-system",
  ],

  // ESLint errors must be fixed before build succeeds
  eslint: {
    ignoreDuringBuilds: false,
  },

  // TypeScript errors must be fixed before build succeeds
  typescript: {
    ignoreBuildErrors: false,
  },

  // Note: i18n is handled via next-intl for App Router
  // Legacy Pages Router i18n config removed for Next.js 15 compatibility

  // Image optimization
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
        protocol: "https",
        hostname: "sentinel-hub.com",
      },
      {
        protocol: "https",
        hostname: "maps.googleapis.com",
      },
      {
        protocol: "https",
        hostname: "maps.gstatic.com",
      },
    ],
    formats: ["image/avif", "image/webp"],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
  },

  // Security headers
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
          // Note: CSP headers are set in middleware.ts with nonce support
          // CSP headers here are for static assets that bypass middleware
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

  // Environment variables exposed to browser
  env: {
    NEXT_PUBLIC_APP_NAME: "SAHOOL",
    NEXT_PUBLIC_APP_VERSION: "16.0.0",
  },

  // Output configuration for Docker/standalone deployments
  // Always use standalone for optimal Docker image size (copies only needed files)
  output: "standalone",
  outputFileTracingRoot: path.resolve(__dirname, "../../"),

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

  // Experimental features
  experimental: {
    // Tree-shake barrel exports for these packages to reduce bundle size
    optimizePackageImports: [
      "lucide-react",
      "@tanstack/react-query",
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
      "@react-google-maps/api",
      "axios",
    ],
  },

  // Webpack configuration for Leaflet and warning suppression
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
      config.resolve.alias = {
        ...config.resolve.alias,
        "@sentry/nextjs": path.resolve(__dirname, "src/lib/sentry-shim.ts"),
      };
    }

    // Add parent node_modules to module resolution for workspace dependencies
    // This allows Next.js to find dependencies hoisted to the root in npm workspaces
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
            // Separate mapping libraries (leaflet, maplibre, google-maps) into their own chunk
            maps: {
              test: /[\\/]node_modules[\\/](leaflet|react-leaflet|maplibre-gl|@react-google-maps)[\\/]/,
              name: "maps",
              chunks: "all",
              priority: 30,
            },
            // NOTE: Do NOT add a "framework" cacheGroup here — Next.js has its own
            // built-in "framework" chunk for React/React-DOM/scheduler. Overriding it
            // breaks the chunk loading order and causes
            // "Cannot read properties of undefined (reading 'call')" at runtime.
          },
        },
      };
    }

    return config;
  },
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

  // Note: disableLogger was REMOVED — it uses an unscoped NormalModuleReplacementPlugin
  // regex (/logger/) that replaces ANY file named "logger" (including our src/lib/logger.ts)
  // with an empty module, causing "Cannot read properties of undefined (reading 'call')".
  // The same optimisation is already covered by bundleSizeOptimizations.excludeDebugStatements
  // below, which is properly scoped to @sentry/ internals only.

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

const baseConfig = withBundleAnalyzer(withNextIntl(nextConfig));
module.exports = withSentryConfig
  ? withSentryConfig(baseConfig, sentryOptions)
  : baseConfig;
