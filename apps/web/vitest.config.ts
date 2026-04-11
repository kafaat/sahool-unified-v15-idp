/// <reference types="vitest" />
import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: ["./src/__tests__/setup.ts"],
    include: ["src/**/*.{test,spec}.{js,ts,tsx}"],
    coverage: {
      provider: "v8",
      reporter: ["text", "json", "html"],
      // Exclude files that are not meaningfully unit-testable or that act
      // as thin re-export / type-only layers. Integration and E2E tests
      // cover the excluded surface (API wrappers, React hooks, etc.).
      exclude: [
        "node_modules/",
        "src/__tests__/setup.ts",
        // Type-only and re-export files
        "src/**/*.d.ts",
        "src/**/types.ts",
        "src/**/types/*.ts",
        "src/types/**",
        "src/**/index.ts",
        // API wrapper layers — covered by integration tests, not unit
        "src/features/**/api.ts",
        "src/features/**/api/**",
        "src/features/**/api.mock.ts",
        "src/lib/api/error-handler.ts",
        "src/lib/api/factory.ts",
        "src/lib/api/client.ts",
        "src/lib/api/hooks.ts",
        // React hooks — covered by component + integration tests
        "src/features/**/hooks/**",
        "src/hooks/**",
        // Feature clients / dashboards — thin view wrappers covered by E2E
        "src/features/**/components/*Client.tsx",
        "src/features/**/*Client.tsx",
        "src/features/ai-copilot/**",
        // Pages (Next.js app router) — covered by E2E
        "src/app/**/page.tsx",
        "src/app/**/layout.tsx",
        "src/app/**/loading.tsx",
        "src/app/**/error.tsx",
        "src/app/**/not-found.tsx",
        "src/app/**/*Client.tsx",
        "src/app/api/**",
        // Infrastructure shims and monitoring
        "src/lib/sentry-shim.ts",
        "src/lib/monitoring/**",
        "src/lib/performance/**",
        "src/lib/services/**",
        "src/lib/security/csp-example.tsx",
        "src/lib/security/index.ts",
        "src/lib/auth/route-guard.tsx",
        // Providers and global config
        "src/app/providers.tsx",
        "src/middleware.ts",
        "src/i18n.ts",
      ],
      thresholds: {
        statements: 40,
        branches: 30,
        functions: 40,
        lines: 40,
      },
    },
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
      "@sahool/shared-ui": path.resolve(__dirname, "../../packages/shared-ui/src"),
      "@sahool/ui": path.resolve(__dirname, "../../packages/shared-ui/src"),
      "@sahool/shared-hooks": path.resolve(__dirname, "../../packages/shared-hooks/src"),
      "@sahool/hooks": path.resolve(__dirname, "../../packages/shared-hooks/src"),
      "@sahool/shared-utils": path.resolve(__dirname, "../../packages/shared-utils/src"),
      "@sahool/utils": path.resolve(__dirname, "../../packages/shared-utils/src"),
      "@sahool/api-client": path.resolve(__dirname, "../../packages/api-client/src"),
      "@sahool/api": path.resolve(__dirname, "../../packages/api-client/src"),
      "@sahool/i18n": path.resolve(__dirname, "../../packages/i18n/src"),
      "@sahool/design-system": path.resolve(__dirname, "../../packages/design-system/src"),
      "@sahool/shared-types/contracts": path.resolve(__dirname, "../../packages/shared-types/src/contracts"),
      "@sahool/shared-types": path.resolve(__dirname, "../../packages/shared-types/src"),
    },
  },
});
