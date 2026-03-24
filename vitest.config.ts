/**
 * Vitest Configuration
 * تكوين Vitest للمشروع
 */

import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: ["./packages/shared-ui/src/test/setup.ts"],
    include: [
      "packages/**/*.{test,spec}.{ts,tsx}",
      "apps/web/src/**/*.{test,spec}.{ts,tsx}",
      "shared/**/*.{test,spec}.{ts,tsx}",
      // API Integration Tests
      "tests/integration/api/**/*.{test,spec}.{ts,tsx}",
      // Contract Consistency Tests
      "tests/integration/contracts/**/*.{test,spec}.{ts,tsx}",
      // Resilience & Error Handling Tests
      "tests/integration/resilience/**/*.{test,spec}.{ts,tsx}",
      // Security Integration Tests
      "tests/integration/security/**/*.{test,spec}.{ts,tsx}",
      // Database Integration Tests
      "tests/integration/database/**/*.{test,spec}.{ts,tsx}",
      // Financial Precision & Wallet Tests
      "tests/integration/financial/**/*.{test,spec}.{ts,tsx}",
    ],
    exclude: [
      "**/node_modules/**",
      "**/dist/**",
      // Exclude NestJS tests - they use Jest, not Vitest
      "apps/services/marketplace-service/**",
      // Exclude Python tests
      "apps/services/**/*.py",
      // Exclude Node.js-only crypto tests (require node environment)
      "packages/shared-crypto/**",
    ],
  },
  resolve: {
    alias: {
      "@sahool/shared-types/contracts": path.resolve(__dirname, "./packages/shared-types/src/contracts"),
      "@sahool/shared-types": path.resolve(__dirname, "./packages/shared-types/src"),
      "@sahool/shared-ui": path.resolve(__dirname, "./packages/shared-ui/src"),
      "@sahool/ui": path.resolve(__dirname, "./packages/shared-ui/src"),
      "@sahool/shared-hooks": path.resolve(__dirname, "./packages/shared-hooks/src"),
      "@sahool/hooks": path.resolve(__dirname, "./packages/shared-hooks/src"),
      "@sahool/shared-utils": path.resolve(__dirname, "./packages/shared-utils/src"),
      "@sahool/utils": path.resolve(__dirname, "./packages/shared-utils/src"),
      "@sahool/api-client": path.resolve(__dirname, "./packages/api-client/src"),
      "@sahool/api": path.resolve(__dirname, "./packages/api-client/src"),
      "@sahool/i18n": path.resolve(__dirname, "./packages/i18n/src"),
      "@sahool/design-system": path.resolve(__dirname, "./packages/design-system/src"),
      "@": path.resolve(__dirname, "./apps/web/src"),
    },
  },
});
