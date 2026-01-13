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
      "apps/admin/src/**/*.{test,spec}.{ts,tsx}",
    ],
    exclude: [
      "**/node_modules/**",
      "**/dist/**",
      // Exclude NestJS tests - they use Jest, not Vitest
      "apps/services/marketplace-service/**",
      // Exclude Python tests
      "apps/services/**/*.py",
    ],
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./apps/web/src"),
    },
  },
});
